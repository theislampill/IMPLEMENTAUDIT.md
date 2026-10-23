#!/usr/bin/env bash
set -euo pipefail
export PYTHONDONTWRITEBYTECODE=1
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if command -v python3 >/dev/null 2>&1; then py=(python3 -B)
elif command -v python >/dev/null 2>&1; then py=(python -B)
else printf 'canonical-state-rotation: Python is required\n' >&2; exit 1; fi
"${py[@]}" - "$root" <<'PY'
import ast, hashlib, importlib.util, json, pathlib, sys
root = pathlib.Path(sys.argv[1])
path = root / 'skills/implementaudit/scripts/rotate-canonical-state.py'
ast.parse(path.read_text(encoding='utf-8'))
spec = importlib.util.spec_from_file_location('rotation_contract', path)
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)
assert module.POINTER_SCHEMA == 'implementaudit.current-generation.v1'
assert module.ARCHIVE_SCHEMA == 'implementaudit.state-archive.v1'
assert module.PROJECTION_SCHEMA == 'implementaudit.protected-projection.v2'
calibration = json.loads((root / 'fixtures/canonical-state-rotation/cases.json').read_text())['trigger_calibration']
bound = json.dumps(calibration['bound'], ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()
assert hashlib.sha256(bound).hexdigest() == calibration['population_sha256'] == module.CALIBRATION_SHA256
assert calibration['population_id'] == module.CALIBRATION_ID
assert module.calibration_contract_v1()['byte_threshold'] == calibration['bound']['thresholds']['bytes']['value']
for name in ('prepare_canonical_draft', 'finalize_canonical_projection', 'read_canonical_generation',
             'verify_canonical_archive', 'resolve_typed_archive_pointer_v2',
             'prepare_native_resume_draft', 'archive_retention_guards'):
    assert callable(getattr(module, name))
reference = root / 'skills/implementaudit/references/canonical-state-rotation.md'
assert reference.is_file()
print('canonical-state-rotation: paired source, original schemas and frozen calibration ok')
PY
