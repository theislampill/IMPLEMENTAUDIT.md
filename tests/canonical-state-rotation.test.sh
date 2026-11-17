#!/usr/bin/env bash
set -euo pipefail
export PYTHONDONTWRITEBYTECODE=1
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$root"
if command -v python3 >/dev/null 2>&1; then py=(python3 -B)
elif command -v python >/dev/null 2>&1; then py=(python -B)
else printf 'canonical-state-rotation.test: Python is required\n' >&2; exit 1; fi
bash scripts/check-canonical-state-rotation.sh
"${py[@]}" tests/canonical_source_custody.py
"${py[@]}" tests/shell_companion_source_custody.py
"${py[@]}" fixtures/canonical-state-rotation/pending_state_loader_test.py
"${py[@]}" fixtures/canonical-state-rotation/protected_projection_v2_test.py
"${py[@]}" fixtures/canonical-state-rotation/archive_v2_test.py
"${py[@]}" fixtures/canonical-state-rotation/native_resume_v2_test.py
"${py[@]}" fixtures/canonical-state-rotation/claim_transaction_test.py
"${py[@]}" fixtures/canonical-state-rotation/canonical_reader_test.py
"${py[@]}" fixtures/canonical-state-rotation/windows_custody_test.py
"${py[@]}" fixtures/canonical-state-rotation/ref_group_test.py
"${py[@]}" fixtures/canonical-state-rotation/input_contract_test.py
"${py[@]}" fixtures/canonical-state-rotation/token_admission_test.py
"${py[@]}" fixtures/canonical-state-rotation/occurrence_preservation_test.py
"${py[@]}" fixtures/canonical-state-rotation/native_input_adapter_test.py
"${py[@]}" fixtures/canonical-state-rotation/native_preflight_test.py
"${py[@]}" fixtures/canonical-state-rotation/c02_native_source_test.py
"${py[@]}" fixtures/canonical-state-rotation/native_episode_projection_test.py
"${py[@]}" fixtures/canonical-state-rotation/native_preparation_test.py
"${py[@]}" fixtures/canonical-state-rotation/owned_stdio_source_boundaries_test.py
"${py[@]}" fixtures/canonical-state-rotation/native_or_rotation_test.py
"${py[@]}" fixtures/canonical-state-rotation/native_claim_test.py
"${py[@]}" fixtures/canonical-state-rotation/c02_projection_test.py
"${py[@]}" fixtures/canonical-state-rotation/c02_publication_test.py
"${py[@]}" fixtures/canonical-state-rotation/c02_cli_test.py
"${py[@]}" fixtures/canonical-state-rotation/c02_reader_test.py
"${py[@]}" fixtures/canonical-state-rotation/c02_owner_selection_test.py
printf 'canonical-state-rotation.test: deterministic source/archive controls ok; native transaction qualification is separately bound\n'
