#!/usr/bin/env bash
set -euo pipefail
repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if command -v python >/dev/null 2>&1; then
  py_cmd=(python)
else
  py_cmd=(python3)
fi
"${py_cmd[@]}" -B "$repo_root/fixtures/operational-evidence/portable-regressions.py" "$repo_root"
