#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source_commit="$(git -C "$repo_root" rev-parse "${REPRO_SOURCE_REF:-HEAD}^{commit}")"
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

for lane in a b; do
  git clone --quiet --no-local --no-checkout "$repo_root" "$tmp/checkout-$lane"
  git -C "$tmp/checkout-$lane" checkout --quiet --detach "$source_commit"
  test -z "$(git -C "$tmp/checkout-$lane" status --porcelain)" || {
    printf 'reproducible-release-asset.test: checkout %s is dirty\n' "$lane" >&2
    exit 1
  }
done

SOURCE_DATE_EPOCH=315532800 TZ=UTC LC_ALL=C \
  bash "$tmp/checkout-a/scripts/build-release-asset.sh" "$tmp/out-a"
SOURCE_DATE_EPOCH=315532800 TZ=America/New_York LC_ALL=C \
  bash "$tmp/checkout-b/scripts/build-release-asset.sh" "$tmp/out-b"

asset_a="$tmp/out-a/IMPLEMENTAUDIT.skill"
asset_b="$tmp/out-b/IMPLEMENTAUDIT.skill"
cmp -s "$asset_a" "$asset_b" || {
  printf 'reproducible-release-asset.test: archives differ byte-for-byte\n' >&2
  exit 1
}

python_cmd=python
command -v "$python_cmd" >/dev/null 2>&1 || python_cmd=python3

for lane in a b; do
  "$python_cmd" - "$tmp/out-$lane/IMPLEMENTAUDIT.skill" > "$tmp/manifest-$lane.json" <<'PY'
import hashlib
import json
import stat
import sys
import zipfile
from pathlib import PurePosixPath

asset = sys.argv[1]
expected_timestamp = (1980, 1, 1, 0, 0, 0)
manifest = []
with zipfile.ZipFile(asset) as zf:
    names = zf.namelist()
    if names != sorted(names):
        raise SystemExit("archive entries are not sorted by POSIX path")
    for info in zf.infolist():
        if "\\" in info.filename or PurePosixPath(info.filename).is_absolute():
            raise SystemExit(f"non-portable archive path: {info.filename}")
        if info.date_time != expected_timestamp:
            raise SystemExit(
                f"unfixed timestamp for {info.filename}: {info.date_time}")
        if info.create_system != 3:
            raise SystemExit(
                f"unfixed ZIP creator for {info.filename}: {info.create_system}")
        if info.compress_type != zipfile.ZIP_DEFLATED:
            raise SystemExit(f"unfixed compression method: {info.filename}")
        if info.extra or info.comment:
            raise SystemExit(f"unexpected ZIP metadata: {info.filename}")
        observed_mode = (info.external_attr >> 16) & 0o777
        expected_mode = 0o755 if info.filename.startswith("scripts/") else 0o644
        if observed_mode != expected_mode:
            raise SystemExit(
                f"mode mismatch for {info.filename}: {oct(observed_mode)}")
        data = zf.read(info.filename)
        manifest.append({
            "path": info.filename,
            "sha256": hashlib.sha256(data).hexdigest(),
            "size": len(data),
            "mode": oct(observed_mode),
            "compression": info.compress_type,
            "timestamp": info.date_time,
            "creator": info.create_system,
        })
print(json.dumps(manifest, sort_keys=True, separators=(",", ":")))
PY
done

cmp -s "$tmp/manifest-a.json" "$tmp/manifest-b.json" || {
  printf 'reproducible-release-asset.test: entry manifests differ\n' >&2
  exit 1
}

hash_a="$("$python_cmd" -c 'import hashlib,sys; print(hashlib.sha256(open(sys.argv[1],"rb").read()).hexdigest())' "$asset_a")"
hash_b="$("$python_cmd" -c 'import hashlib,sys; print(hashlib.sha256(open(sys.argv[1],"rb").read()).hexdigest())' "$asset_b")"
[ "$hash_a" = "$hash_b" ] || {
  printf 'reproducible-release-asset.test: SHA-256 mismatch\n' >&2
  exit 1
}

printf 'reproducible-release-asset.test: ok commit=%s sha256=%s\n' \
  "$source_commit" "$hash_a"
