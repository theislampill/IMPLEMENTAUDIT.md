#!/usr/bin/env bash
set -euo pipefail
repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"
export PYTHONDONTWRITEBYTECODE=1
# This family creates independent qualifier fixtures. The outer canonical
# capture belongs to the original reproduction node, not these child fixtures;
# explicit ambient-variable refusal is exercised inside the fixture controls.
unset R0035_REPRO_EVENT_CAPTURE_DIR
if command -v python >/dev/null 2>&1; then py_cmd=(python)
elif command -v python3 >/dev/null 2>&1; then py_cmd=(python3)
else py_cmd=(py -3); fi
"${py_cmd[@]}" tests/work-graph-verifier-cases.py
"${py_cmd[@]}" tests/work-graph-stream-cases.py
"${py_cmd[@]}" tests/work-graph-repro-events-cases.py ProfileCases FailureCases DurabilityCases QualifierCases
