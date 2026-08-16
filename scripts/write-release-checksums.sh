#!/usr/bin/env bash
set -euo pipefail

fail() {
  printf 'write-release-checksums: %s\n' "$*" >&2
  exit 1
}

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

if command -v python >/dev/null 2>&1; then
  py_cmd=(python)
elif command -v python3 >/dev/null 2>&1; then
  py_cmd=(python3)
elif command -v py >/dev/null 2>&1; then
  py_cmd=(py -3)
else
  fail "python, python3, or py -3 is required"
fi

mode=""
if [ "${1:-}" = "--check" ]; then
  mode="--check"
  shift
fi

assets=()
manifest=""
if [ "$#" -eq 0 ]; then
  assets=(dist/IMPLEMENTAUDIT.plugin.zip dist/IMPLEMENTAUDIT.skill)
  manifest=dist/CHECKSUMS.txt
elif [ "${1:-}" = "--all" ]; then
  shift
  asset_dir="${1:-dist}"
  manifest="${2:-$asset_dir/CHECKSUMS.txt}"
  assets=("$asset_dir/IMPLEMENTAUDIT.plugin.zip" "$asset_dir/IMPLEMENTAUDIT.skill")
else
  [ "$#" -eq 2 ] || fail "expected <asset> <manifest> or --all [asset-dir] [manifest]"
  assets=("$1")
  manifest="$2"
fi

"${py_cmd[@]}" - "$mode" "$manifest" "${assets[@]}" <<'PY'
import hashlib
import sys
from pathlib import Path

mode, manifest_arg, *asset_args = sys.argv[1:]
manifest = Path(manifest_arg)
assets = [Path(value) for value in asset_args]

if not assets:
    raise SystemExit("at least one asset is required")
for asset in assets:
    if not asset.is_file():
        raise SystemExit(f"missing asset: {asset}")

names = [asset.name for asset in assets]
if len(names) != len(set(names)):
    raise SystemExit("asset basenames must be unique")
lines = [
    f"sha256  {hashlib.sha256(asset.read_bytes()).hexdigest()}  {asset.name}\n"
    for asset in sorted(assets, key=lambda value: value.name)
]
expected = "".join(lines)

if mode == "--check":
    if not manifest.is_file():
        raise SystemExit(f"missing checksum manifest: {manifest}")
    if manifest.read_text(encoding="utf-8") != expected:
        raise SystemExit(f"checksum manifest is stale: {manifest}")
    print(f"write-release-checksums: check ok {', '.join(sorted(names))}")
else:
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text(expected, encoding="utf-8")
    print(f"write-release-checksums: wrote {manifest}")
PY
