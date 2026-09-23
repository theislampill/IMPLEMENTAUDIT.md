#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"

py=()
if command -v python >/dev/null 2>&1; then py=(python)
elif command -v python3 >/dev/null 2>&1; then py=(python3)
elif command -v py >/dev/null 2>&1; then py=(py -3)
else
  printf 'route-observation-gate.test: Python 3 is required\n' >&2
  exit 1
fi

tmp_parent="$(cd "${IMPLEMENTAUDIT_TEST_ROOT:-${TMPDIR:-/tmp}}" && pwd -P)"
tmp="$(mktemp -d "$tmp_parent/route-observation-gate.XXXXXX")"
case "$tmp" in "$tmp_parent"/route-observation-gate.*) ;; *) exit 1 ;; esac
trap 'case "$tmp" in "$tmp_parent"/route-observation-gate.*) rm -rf -- "$tmp" ;; *) exit 1 ;; esac' EXIT

PYTHONDONTWRITEBYTECODE=1 "${py[@]}" -I -S -B \
  "$repo_root/tests/route-observation-gate.test.py" \
  --source "$repo_root" --output-root "$tmp"
