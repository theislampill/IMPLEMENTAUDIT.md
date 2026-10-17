#!/usr/bin/env bash
set -euo pipefail
repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"
export PYTHONDONTWRITEBYTECODE=1
if command -v python >/dev/null 2>&1; then py_cmd=(python)
elif command -v python3 >/dev/null 2>&1; then py_cmd=(python3)
else py_cmd=(py -3); fi
"${py_cmd[@]}" tests/work-graph-verifier-cases.py
