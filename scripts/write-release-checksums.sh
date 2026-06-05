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

asset="${1:-dist/IMPLEMENTAUDIT.skill}"
manifest="${2:-dist/CHECKSUMS.txt}"

"${py_cmd[@]}" - "$mode" "$asset" "$manifest" <<'PY'
import hashlib
import sys
from pathlib import Path

mode, asset_arg, manifest_arg = sys.argv[1:4]
asset = Path(asset_arg)
manifest = Path(manifest_arg)

if not asset.is_file():
    raise SystemExit(f"missing asset: {asset}")

digest = hashlib.sha256(asset.read_bytes()).hexdigest()
line = f"sha256  {digest}  {asset.name}\n"

if mode == "--check":
    if not manifest.is_file():
        raise SystemExit(f"missing checksum manifest: {manifest}")
    if manifest.read_text() != line:
        raise SystemExit(f"checksum manifest is stale: {manifest}")
    print(f"write-release-checksums: check ok {asset.name}")
else:
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text(line)
    print(f"write-release-checksums: wrote {manifest}")
PY
