#!/usr/bin/env bash
set -euo pipefail

fail() {
  printf 'install-plugin-from-release: %s\n' "$*" >&2
  exit 1
}

usage() {
  cat <<'EOF'
Usage:
  install-plugin-from-release.sh \
    --asset IMPLEMENTAUDIT.plugin.zip \
    --checksum CHECKSUMS.txt \
    --host codex|claude \
    --host-root ISOLATED_ROOT \
    [--version 0.4.0] [--allow-downgrade]

The host root must be a disposable directory containing the regular sentinel
.implementaudit-isolated-host-root. This command proves staged package copy,
inventory, update and rollback behavior only; it is not native host discovery or
invocation proof and never targets a real user home implicitly.
EOF
}

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

asset=""
checksum=""
host=""
host_root=""
expected_version="0.4.0"
allow_downgrade=""

while [ "$#" -gt 0 ]; do
  case "$1" in
    --asset) asset="${2:-}"; shift 2 ;;
    --checksum) checksum="${2:-}"; shift 2 ;;
    --host) host="${2:-}"; shift 2 ;;
    --host-root) host_root="${2:-}"; shift 2 ;;
    --version) expected_version="${2:-}"; shift 2 ;;
    --allow-downgrade) allow_downgrade="--allow-downgrade"; shift ;;
    -h|--help) usage; exit 0 ;;
    *) fail "unknown argument: $1" ;;
  esac
done

[ -n "$asset" ] || fail "--asset is required"
[ -n "$checksum" ] || fail "--checksum is required"
[ -n "$host" ] || fail "--host is required"
[ -n "$host_root" ] || fail "--host-root is required"
[ "$expected_version" = "0.4.0" ] \
  || fail "--version must match canonical runtime 0.4.0"
[ -f "$asset" ] && [ ! -L "$asset" ] \
  || fail "asset must be a regular non-symlink file"
[ -f "$checksum" ] && [ ! -L "$checksum" ] \
  || fail "checksum must be a regular non-symlink file"
[ "$(basename "$asset")" = "IMPLEMENTAUDIT.plugin.zip" ] \
  || fail "canonical plugin asset must be named IMPLEMENTAUDIT.plugin.zip"

if command -v python >/dev/null 2>&1; then
  py_cmd=(python)
elif command -v python3 >/dev/null 2>&1; then
  py_cmd=(python3)
elif command -v py >/dev/null 2>&1; then
  py_cmd=(py -3)
else
  fail "python, python3, or py -3 is required"
fi

"${py_cmd[@]}" - "$asset" "$checksum" <<'PY'
import hashlib
import pathlib
import sys

asset = pathlib.Path(sys.argv[1])
manifest = pathlib.Path(sys.argv[2])
digest = hashlib.sha256(asset.read_bytes()).hexdigest()
matches = []
for line in manifest.read_text(encoding="utf-8").splitlines():
    parts = line.split()
    if len(parts) == 3 and parts[0].lower() == "sha256" and parts[2] == asset.name:
        matches.append(parts[1].lower())
if len(matches) != 1:
    raise SystemExit(f"checksum manifest must name {asset.name} exactly once")
if matches[0] != digest:
    raise SystemExit("checksum manifest is stale or mismatched")
PY

args=(--install-plugin "$host" "$host_root" "$asset")
if [ -n "$allow_downgrade" ]; then
  args+=("$allow_downgrade")
fi
"${py_cmd[@]}" scripts/package-contract.py "${args[@]}"

printf 'install-plugin-from-release: staged-copy proof complete; native host discovery not claimed\n'
