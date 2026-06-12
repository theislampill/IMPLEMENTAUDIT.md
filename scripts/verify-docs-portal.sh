#!/usr/bin/env bash
set -euo pipefail

fail() {
  printf 'verify-docs-portal: %s\n' "$*" >&2
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

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

out="$tmp/docs-portal"
"${py_cmd[@]}" scripts/build-docs-portal.py --out "$out" >/dev/null
"${py_cmd[@]}" scripts/check-docs-portal.py "$out"

printf 'verify-docs-portal: ok\n'
