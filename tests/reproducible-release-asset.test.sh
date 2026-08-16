#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source_commit="$(git -C "$repo_root" rev-parse "${REPRO_SOURCE_REF:-HEAD}^{commit}")"

retain_skill_a="${REPRO_RETAINED_ASSET_A:-}"
retain_skill_b="${REPRO_RETAINED_ASSET_B:-}"
retain_plugin_a="${REPRO_RETAINED_PLUGIN_A:-}"
retain_plugin_b="${REPRO_RETAINED_PLUGIN_B:-}"
retain_checksums_a="${REPRO_RETAINED_CHECKSUMS_A:-}"
retain_checksums_b="${REPRO_RETAINED_CHECKSUMS_B:-}"

fail() {
  printf 'reproducible-release-asset.test: %s\n' "$*" >&2
  exit 1
}

if { [ -n "$retain_skill_a" ] && [ -z "$retain_skill_b" ]; } ||
   { [ -z "$retain_skill_a" ] && [ -n "$retain_skill_b" ]; }; then
  fail "both retained compatibility A/B paths are required"
fi

extra_retention=(
  "$retain_plugin_a" "$retain_plugin_b"
  "$retain_checksums_a" "$retain_checksums_b"
)
extra_count=0
for value in "${extra_retention[@]}"; do
  [ -z "$value" ] || extra_count=$((extra_count + 1))
done
if [ "$extra_count" -ne 0 ] && {
     [ "$extra_count" -ne 4 ] || [ -z "$retain_skill_a" ];
   }; then
  fail "complete plugin, compatibility, and checksum A/B retention paths are required"
fi

if command -v python >/dev/null 2>&1; then
  python_cmd=python
elif command -v python3 >/dev/null 2>&1; then
  python_cmd=python3
else
  fail "python or python3 is required"
fi

retained_targets=()
if [ -n "$retain_skill_a" ]; then
  retained_targets=("$retain_skill_a" "$retain_skill_b")
  if [ "$extra_count" -eq 4 ]; then
    retained_targets+=(
      "$retain_plugin_a" "$retain_plugin_b"
      "$retain_checksums_a" "$retain_checksums_b"
    )
  fi
fi

if [ "${#retained_targets[@]}" -gt 0 ]; then
  "$python_cmd" - "$repo_root" "${retained_targets[@]}" <<'PY'
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
        raise SystemExit("retained asset parent link or reparse alias forbidden")
    candidate = parent / target.name
    try:
        candidate.relative_to(repo)
    except ValueError:
        pass
    else:
        raise SystemExit("retained asset path must be outside the product worktree")
    if candidate.exists() or candidate.is_symlink():
        raise SystemExit("retained asset destination already exists")
    parent_stat = os.lstat(parent)
    if (not stat.S_ISDIR(parent_stat.st_mode) or
            stat.S_ISLNK(parent_stat.st_mode) or
            bool(getattr(parent_stat, "st_file_attributes", 0) &
                 getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400))):
        raise SystemExit("retained asset parent must be a real directory")
    prepared.append(candidate)
normalized = {
    os.path.normcase(os.path.normpath(str(path))) for path in prepared
}
if len(normalized) != len(prepared):
    raise SystemExit("retained release-set paths must be distinct")
PY
fi

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

for lane in a b; do
  git clone --quiet --no-local --no-checkout "$repo_root" "$tmp/checkout-$lane"
  git -C "$tmp/checkout-$lane" checkout --quiet --detach "$source_commit"
  [ -z "$(git -C "$tmp/checkout-$lane" status --porcelain)" ] \
    || fail "checkout $lane is dirty"
done

SOURCE_DATE_EPOCH=315532800 TZ=UTC LC_ALL=C \
  bash "$tmp/checkout-a/scripts/build-release-asset.sh" "$tmp/out-a"
SOURCE_DATE_EPOCH=315532800 TZ=America/New_York LC_ALL=C \
  bash "$tmp/checkout-b/scripts/build-release-asset.sh" "$tmp/out-b"

release_members=(IMPLEMENTAUDIT.plugin.zip IMPLEMENTAUDIT.skill CHECKSUMS.txt)
for member in "${release_members[@]}"; do
  cmp -s "$tmp/out-a/$member" "$tmp/out-b/$member" \
    || fail "$member differs byte-for-byte across clean builds"
done

for lane in a b; do
  bash "$tmp/checkout-$lane/scripts/write-release-checksums.sh" \
    --check --all "$tmp/out-$lane" "$tmp/out-$lane/CHECKSUMS.txt"
done

for role in plugin skill; do
  case "$role" in
    plugin) artifact=IMPLEMENTAUDIT.plugin.zip ;;
    skill) artifact=IMPLEMENTAUDIT.skill ;;
  esac
  for lane in a b; do
    "$python_cmd" - "$tmp/out-$lane/$artifact" > "$tmp/$role-manifest-$lane.json" <<'PY'
import hashlib
import json
import sys
import zipfile
from pathlib import PurePosixPath

asset = sys.argv[1]
expected_timestamp = (1980, 1, 1, 0, 0, 0)
manifest = []
with zipfile.ZipFile(asset) as archive:
    names = archive.namelist()
    if names != sorted(names) or len(names) != len(set(names)):
        raise SystemExit("archive entries are not uniquely sorted")
    for info in archive.infolist():
        member = PurePosixPath(info.filename)
        if "\\" in info.filename or member.is_absolute() or ".." in member.parts:
            raise SystemExit(f"non-portable archive path: {info.filename}")
        if info.date_time != expected_timestamp:
            raise SystemExit(f"unfixed timestamp: {info.filename}")
        if info.create_system != 3 or info.compress_type != zipfile.ZIP_DEFLATED:
            raise SystemExit(f"unfixed ZIP metadata: {info.filename}")
        if info.extra or info.comment:
            raise SystemExit(f"unexpected ZIP metadata: {info.filename}")
        observed_mode = (info.external_attr >> 16) & 0o777
        executable = (
            info.filename.startswith("scripts/")
            or "/scripts/" in info.filename
        )
        expected_mode = 0o755 if executable else 0o644
        if observed_mode != expected_mode:
            raise SystemExit(f"mode mismatch: {info.filename}")
        data = archive.read(info.filename)
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
  cmp -s "$tmp/$role-manifest-a.json" "$tmp/$role-manifest-b.json" \
    || fail "$role entry manifests differ"
done

sha256_file() {
  "$python_cmd" -c \
    'import hashlib,sys; print(hashlib.sha256(open(sys.argv[1],"rb").read()).hexdigest())' \
    "$1"
}

skill_hash_a="$(sha256_file "$tmp/out-a/IMPLEMENTAUDIT.skill")"
skill_hash_b="$(sha256_file "$tmp/out-b/IMPLEMENTAUDIT.skill")"
plugin_hash_a="$(sha256_file "$tmp/out-a/IMPLEMENTAUDIT.plugin.zip")"
plugin_hash_b="$(sha256_file "$tmp/out-b/IMPLEMENTAUDIT.plugin.zip")"
checksums_hash_a="$(sha256_file "$tmp/out-a/CHECKSUMS.txt")"
checksums_hash_b="$(sha256_file "$tmp/out-b/CHECKSUMS.txt")"
[ "$skill_hash_a" = "$skill_hash_b" ] || fail "compatibility SHA-256 mismatch"
[ "$plugin_hash_a" = "$plugin_hash_b" ] || fail "plugin SHA-256 mismatch"
[ "$checksums_hash_a" = "$checksums_hash_b" ] || fail "checksum-manifest SHA-256 mismatch"

if [ -n "$retain_skill_a" ]; then
  retention_specs=(
    "$tmp/out-a/IMPLEMENTAUDIT.skill" "$retain_skill_a" "$skill_hash_a" A
    "$tmp/out-b/IMPLEMENTAUDIT.skill" "$retain_skill_b" "$skill_hash_b" B
  )
  if [ "$extra_count" -eq 4 ]; then
    retention_specs+=(
      "$tmp/out-a/IMPLEMENTAUDIT.plugin.zip" "$retain_plugin_a" "$plugin_hash_a" PLUGIN_A
      "$tmp/out-b/IMPLEMENTAUDIT.plugin.zip" "$retain_plugin_b" "$plugin_hash_b" PLUGIN_B
      "$tmp/out-a/CHECKSUMS.txt" "$retain_checksums_a" "$checksums_hash_a" CHECKSUMS_A
      "$tmp/out-b/CHECKSUMS.txt" "$retain_checksums_b" "$checksums_hash_b" CHECKSUMS_B
    )
  fi
  "$python_cmd" - "$repo_root" "${retention_specs[@]}" <<'PY'
import hashlib
import os
import pathlib
import shutil
import stat
import sys

repo = pathlib.Path(sys.argv[1]).resolve(strict=True)
values = sys.argv[2:]
if len(values) % 4:
    raise SystemExit("retention specification is malformed")
prepared = []
for offset in range(0, len(values), 4):
    source = pathlib.Path(values[offset]).resolve(strict=True)
    target = pathlib.Path(values[offset + 1])
    expected = values[offset + 2]
    label = values[offset + 3]
    if not target.is_absolute():
        raise SystemExit("retained asset path must be absolute")
    requested_parent = target.parent.absolute()
    parent = requested_parent.resolve(strict=True)
    if os.path.normcase(os.path.normpath(requested_parent)) != \
            os.path.normcase(os.path.normpath(parent)):
        raise SystemExit("retained asset parent link or reparse alias forbidden")
    candidate = parent / target.name
    try:
        candidate.relative_to(repo)
    except ValueError:
        pass
    else:
        raise SystemExit("retained asset path must be outside the product worktree")
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
if len(normalized) != len(prepared):
    raise SystemExit("retained release-set paths must be distinct")

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
                (parent_after.st_dev, parent_after.st_ino, parent_after.st_mode)):
            raise SystemExit("retained asset parent identity changed")
        if (not stat.S_ISREG(observed.st_mode) or observed.st_nlink != 1 or
                stat.S_ISLNK(observed.st_mode) or
                bool(getattr(observed, "st_file_attributes", 0) &
                     getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400))):
            raise SystemExit("retained asset custody invalid")
        actual = hashlib.sha256(candidate.read_bytes()).hexdigest()
        if actual != expected:
            raise SystemExit("retained asset rehash mismatch")
        print(f"REPRODUCIBLE_ASSET_{label}_RETAINED path={candidate} sha256={actual}")
except BaseException:
    for candidate in created:
        candidate.unlink(missing_ok=True)
    raise
PY
fi

printf 'reproducible-release-asset.test: ok commit=%s plugin_sha256=%s skill_sha256=%s checksums_sha256=%s\n' \
  "$source_commit" "$plugin_hash_a" "$skill_hash_a" "$checksums_hash_a"
