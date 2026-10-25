#!/usr/bin/env bash
set -euo pipefail
export PYTHONDONTWRITEBYTECODE=1
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$root"
if command -v python3 >/dev/null 2>&1; then py=(python3 -B)
elif command -v python >/dev/null 2>&1; then py=(python -B)
else printf 'canonical-state-rotation.test: Python is required\n' >&2; exit 1; fi
bash scripts/check-canonical-state-rotation.sh
"${py[@]}" tests/shell_companion_source_custody.py
"${py[@]}" fixtures/canonical-state-rotation/protected_projection_v2_test.py
"${py[@]}" fixtures/canonical-state-rotation/archive_v2_test.py
"${py[@]}" fixtures/canonical-state-rotation/native_resume_v2_test.py
"${py[@]}" fixtures/canonical-state-rotation/claim_transaction_test.py
"${py[@]}" fixtures/canonical-state-rotation/canonical_reader_test.py
"${py[@]}" fixtures/canonical-state-rotation/windows_custody_test.py
"${py[@]}" fixtures/canonical-state-rotation/input_contract_test.py
printf 'canonical-state-rotation.test: deterministic source/archive controls ok; native transaction qualification is separately bound\n'
