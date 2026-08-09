#!/usr/bin/env bash
set -euo pipefail

fixture_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
evaluator="$fixture_dir/evaluate.py"
cases="$fixture_dir/cases.json"
fail() { printf 'semantic-preservation-cases: %s\n' "$*" >&2; exit 1; }

[ -f "$cases" ] || fail "cases.json missing"
[ -f "$evaluator" ] || fail "evaluate.py missing"

if command -v python >/dev/null 2>&1; then
  python_cmd=(python)
elif command -v python3 >/dev/null 2>&1; then
  python_cmd=(python3)
else
  fail "python or python3 is required"
fi

"${python_cmd[@]}" "$evaluator" --cases "$cases" --check
