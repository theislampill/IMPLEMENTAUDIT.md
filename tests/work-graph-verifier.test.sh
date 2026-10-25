#!/usr/bin/env bash
set -euo pipefail
repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"
export PYTHONDONTWRITEBYTECODE=1
# This family creates independent qualifier fixtures. The outer canonical
# capture belongs to the original reproduction node, not these child fixtures;
# explicit ambient-variable refusal is exercised inside the fixture controls.
for retained_name in "${!REPRO_RETAINED_@}"; do
  unset "$retained_name"
done
unset REPRO_SOURCE_REF R0035_REPRO_EVENT_CAPTURE_DIR IMPLEMENTAUDIT_PORTAL_CAPTURE
if command -v python >/dev/null 2>&1; then py_cmd=(python)
elif command -v python3 >/dev/null 2>&1; then py_cmd=(python3)
else py_cmd=(py -3); fi
"${py_cmd[@]}" tests/work-graph-verifier-cases.py
"${py_cmd[@]}" tests/work-graph-stream-cases.py
"${py_cmd[@]}" tests/work-graph-prefix-cases.py
"${py_cmd[@]}" tests/work-graph-registry-cases.py
"${py_cmd[@]}" tests/work-graph-repro-events-cases.py ProfileCases FailureCases DurabilityCases QualifierCases
"${py_cmd[@]}" tests/work-graph-correspondence-preflight-cases.py
"${py_cmd[@]}" tests/work-graph-audit-spec-cases.py
"${py_cmd[@]}" tests/work-graph-andon-cases.py
"${py_cmd[@]}" tests/work-graph-finite-batch-cases.py
"${py_cmd[@]}" tests/work-graph-finite-entry-cases.py
"${py_cmd[@]}" tests/work-graph-finite-next-cases.py
"${py_cmd[@]}" tests/work-graph-topology-cases.py
"${py_cmd[@]}" tests/work-graph-recursive-cases.py
"${py_cmd[@]}" tests/work-graph-literal-cases.py
"${py_cmd[@]}" tests/work-graph-planning-cases.py
"${py_cmd[@]}" tests/work-graph-routing-cases.py
"${py_cmd[@]}" tests/work-graph-audit-routing-cases.py
"${py_cmd[@]}" tests/work-graph-safeguard-cases.py
"${py_cmd[@]}" tests/work-graph-installed-cases.py
"${py_cmd[@]}" tests/work-graph-planner-copy-cases.py
"${py_cmd[@]}" tests/work-graph-fanout-cases.py
"${py_cmd[@]}" tests/work-graph-skill-layout-cases.py
"${py_cmd[@]}" tests/work-graph-native-integration-cases.py
"${py_cmd[@]}" tests/work-graph-audit-retention-cases.py
"${py_cmd[@]}" tests/work-graph-audit-object-contract-cases.py
"${py_cmd[@]}" tests/work-graph-claim-boundary-cases.py
"${py_cmd[@]}" tests/work-graph-terminology-cases.py
"${py_cmd[@]}" tests/work-graph-lean-discipline-cases.py
"${py_cmd[@]}" tests/work-graph-internal-routing-cases.py
"${py_cmd[@]}" tests/work-graph-bootstrap-budget-cases.py
"${py_cmd[@]}" tests/work-graph-respec-impact-set-cases.py
"${py_cmd[@]}" tests/work-graph-package-shape-claims-cases.py
"${py_cmd[@]}" tests/work-graph-mini-audit-loop-cases.py
"${py_cmd[@]}" tests/work-graph-action-selection-cases.py
"${py_cmd[@]}" tests/work-graph-readme-effect-cases.py
