#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source_commit="$(git -C "$repo_root" rev-parse "${REPRO_SOURCE_REF:-HEAD}^{commit}")"
retain_a="${REPRO_RETAINED_ASSET_A:-}"
retain_b="${REPRO_RETAINED_ASSET_B:-}"
if { [ -n "$retain_a" ] && [ -z "$retain_b" ]; } ||
   { [ -z "$retain_a" ] && [ -n "$retain_b" ]; }; then
  printf 'reproducible-release-asset.test: both retained A/B paths are required\n' >&2
  exit 1
fi
python_cmd=python
command -v "$python_cmd" >/dev/null 2>&1 || python_cmd=python3
if [ -n "$retain_a" ]; then
  "$python_cmd" - "$repo_root" "$retain_a" "$retain_b" <<'PY'
import os
import pathlib
import stat
import sys

repo = pathlib.Path(sys.argv[1]).resolve(strict=True)
prepared = []
for raw in sys.argv[2:]:
    target = pathlib.Path(raw)
    if not target.is_absolute():
        raise SystemExit("retained asset path must be absolute")
    requested_parent = target.parent.absolute()
    parent = requested_parent.resolve(strict=True)
    if os.path.normcase(os.path.normpath(requested_parent)) != \
            os.path.normcase(os.path.normpath(parent)):
        raise SystemExit(
            "retained asset parent link or reparse alias forbidden")
    candidate = parent / target.name
    try:
        candidate.relative_to(repo)
    except ValueError:
        pass
    else:
        raise SystemExit(
            "retained asset path must be outside the product worktree")
    if candidate.exists() or candidate.is_symlink():
        raise SystemExit("retained asset destination already exists")
    parent_stat = os.lstat(parent)
    if (not stat.S_ISDIR(parent_stat.st_mode) or
            stat.S_ISLNK(parent_stat.st_mode) or
            bool(getattr(parent_stat, "st_file_attributes", 0) &
                 getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400))):
        raise SystemExit("retained asset parent must be a real directory")
    prepared.append(candidate)
if len({
        os.path.normcase(os.path.normpath(str(path)))
        for path in prepared
}) != 2:
    raise SystemExit("retained A/B asset paths must be distinct")
PY
fi
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

if [ -n "$retain_a" ]; then
  "$python_cmd" - "$repo_root" \
    "$asset_a" "$retain_a" "$hash_a" \
    "$asset_b" "$retain_b" "$hash_b" <<'PY'
import hashlib
import os
import pathlib
import shutil
import stat
import sys

repo = pathlib.Path(sys.argv[1]).resolve(strict=True)
specs = [
    (pathlib.Path(sys.argv[2]).resolve(strict=True),
     pathlib.Path(sys.argv[3]), sys.argv[4], "A"),
    (pathlib.Path(sys.argv[5]).resolve(strict=True),
     pathlib.Path(sys.argv[6]), sys.argv[7], "B"),
]
prepared = []
for source, target, expected, label in specs:
    if not target.is_absolute():
        raise SystemExit("retained asset path must be absolute")
    requested_parent = target.parent.absolute()
    parent = requested_parent.resolve(strict=True)
    if os.path.normcase(os.path.normpath(requested_parent)) != \
            os.path.normcase(os.path.normpath(parent)):
        raise SystemExit(
            "retained asset parent link or reparse alias forbidden")
    candidate = parent / target.name
    try:
        candidate.relative_to(repo)
    except ValueError:
        pass
    else:
        raise SystemExit(
            "retained asset path must be outside the product worktree")
    if candidate.exists() or candidate.is_symlink():
        raise SystemExit("retained asset destination already exists")
    parent_stat = os.lstat(parent)
    if (not stat.S_ISDIR(parent_stat.st_mode) or
            stat.S_ISLNK(parent_stat.st_mode) or
            bool(getattr(parent_stat, "st_file_attributes", 0) &
                 getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400))):
        raise SystemExit("retained asset parent must be a real directory")
    prepared.append((source, candidate, expected, label, parent, parent_stat))
normalized = {
    os.path.normcase(os.path.normpath(str(row[1]))) for row in prepared
}
if len(normalized) != 2:
    raise SystemExit("retained A/B asset paths must be distinct")

created = []
try:
    for source, candidate, expected, label, parent, parent_stat in prepared:
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
        if hasattr(os, "O_NOFOLLOW"):
            flags |= os.O_NOFOLLOW
        descriptor = os.open(candidate, flags, 0o600)
        try:
            with os.fdopen(descriptor, "wb", closefd=False) as output:
                with source.open("rb") as input_file:
                    shutil.copyfileobj(input_file, output)
                output.flush()
                os.fsync(output.fileno())
        finally:
            os.close(descriptor)
        created.append(candidate)
        observed = os.lstat(candidate)
        parent_after = os.lstat(parent)
        if ((parent_stat.st_dev, parent_stat.st_ino, parent_stat.st_mode) !=
                (parent_after.st_dev, parent_after.st_ino,
                 parent_after.st_mode)):
            raise SystemExit("retained asset parent identity changed")
        if (not stat.S_ISREG(observed.st_mode) or observed.st_nlink != 1 or
                stat.S_ISLNK(observed.st_mode) or
                bool(getattr(observed, "st_file_attributes", 0) &
                     getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400))):
            raise SystemExit("retained asset custody invalid")
        actual = hashlib.sha256(candidate.read_bytes()).hexdigest()
        if actual != expected:
            raise SystemExit("retained asset rehash mismatch")
        print(
            f"REPRODUCIBLE_ASSET_{label}_RETAINED "
            f"path={candidate} sha256={actual}")
except BaseException:
    for candidate in created:
        candidate.unlink(missing_ok=True)
    raise
PY
fi

printf 'reproducible-release-asset.test: ok commit=%s sha256=%s\n' \
  "$source_commit" "$hash_a"
