#!/usr/bin/env bash
set -euo pipefail

# Action-selection contract test (#48, IA-ACTION-DEPTH): runs the checker on
# the live repo, then proves the checker actually fails on mutated copies
# (embedded negative controls, not whole-file grep optimism).

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

fail() {
  printf 'action-selection-contract.test: %s\n' "$*" >&2
  exit 1
}

if command -v python >/dev/null 2>&1; then
  py_cmd=(python)
elif command -v python3 >/dev/null 2>&1; then
  py_cmd=(python3)
elif command -v py >/dev/null 2>&1; then
  py_cmd=(py -3)
else
  fail "python, python3, or py -3 is required"
fi

# 1. Positive: live repo passes.
bash scripts/check-action-selection-contract.sh \
  || fail "checker fails on the live repo"

# Sandbox for negative controls.
tmp_root="$(mktemp -d)"
trap 'rm -rf "$tmp_root"' EXIT

reset_sandbox() {
  rm -rf "$tmp_root"
  mkdir -p \
    "$tmp_root/skills/implementaudit/references" \
    "$tmp_root/skills/implementaudit/scripts" \
    "$tmp_root/skills/implementaudit/templates" \
    "$tmp_root/fixtures/audit-action-selection" \
    "$tmp_root/fixtures/native-integration" \
    "$tmp_root/fixtures/audit-object-routing"
  cp skills/implementaudit/SKILL.md "$tmp_root/skills/implementaudit/"
  cp skills/implementaudit/references/planning-depth.md \
    "$tmp_root/skills/implementaudit/references/"
  cp skills/implementaudit/references/audit-playbook.md \
    "$tmp_root/skills/implementaudit/references/"
  cp skills/implementaudit/references/lean-operating-discipline.md \
    "$tmp_root/skills/implementaudit/references/"
  cp skills/implementaudit/references/child-agents.md \
    "$tmp_root/skills/implementaudit/references/"
  cp skills/implementaudit/references/plan-lifecycle.md \
    "$tmp_root/skills/implementaudit/references/"
  cp skills/implementaudit/scripts/compile-work-graph.py \
    "$tmp_root/skills/implementaudit/scripts/"
  cp skills/implementaudit/templates/THINKING.md \
    skills/implementaudit/templates/ROADMAP.md \
    "$tmp_root/skills/implementaudit/templates/"
  cp fixtures/audit-action-selection/*.md \
    "$tmp_root/fixtures/audit-action-selection/"
  cp fixtures/audit-action-selection/*.json \
    "$tmp_root/fixtures/audit-action-selection/"
  cp fixtures/native-integration/single-plan-native-route.md \
    "$tmp_root/fixtures/native-integration/"
  cp fixtures/audit-object-routing/deep-pressure-disclosure.md \
    "$tmp_root/fixtures/audit-object-routing/"
}

expect_fail() {
  local label="$1"
  if bash scripts/check-action-selection-contract.sh --repo-root "$tmp_root" \
    >/dev/null 2>&1; then
    fail "negative control not detected: $label"
  fi
}

# 2. Sanity: untouched sandbox passes.
reset_sandbox
bash scripts/check-action-selection-contract.sh --repo-root "$tmp_root" \
  >/dev/null 2>&1 || fail "checker fails on the untouched sandbox copy"

# HC-H4. Canonical graph projection is executable owner behavior, not prose-only
# scheduling advice. Each owner route and the helper itself are independently
# pinned before the older action-selection negative controls run.
reset_sandbox
grep -v "Compile the bounded frontier projection" \
  "$tmp_root/skills/implementaudit/references/child-agents.md" \
  >"$tmp_root/child-agents.tmp"
mv "$tmp_root/child-agents.tmp" \
  "$tmp_root/skills/implementaudit/references/child-agents.md"
expect_fail "canonical WORK_GRAPH compiler execution owner removed"

reset_sandbox
grep -v "derive the bounded ready-cell projection" \
  "$tmp_root/skills/implementaudit/references/planning-depth.md" \
  >"$tmp_root/planning-depth.tmp"
mv "$tmp_root/planning-depth.tmp" \
  "$tmp_root/skills/implementaudit/references/planning-depth.md"
expect_fail "factor-derived WORK_GRAPH compiler route removed"

reset_sandbox
rm "$tmp_root/skills/implementaudit/scripts/compile-work-graph.py"
expect_fail "canonical WORK_GRAPH compiler helper removed"

# 3. Keyword-freedom clause removed from the contract -> must fail.
reset_sandbox
grep -v "Depth never requires an activation keyword" \
  "$tmp_root/skills/implementaudit/references/planning-depth.md" \
  >"$tmp_root/planning-depth.tmp"
mv "$tmp_root/planning-depth.tmp" \
  "$tmp_root/skills/implementaudit/references/planning-depth.md"
expect_fail "planning-depth.md without the keyword-freedom clause"

# 4. Action-selection record loses its template home -> must fail.
reset_sandbox
sed 's/^## Action selection$/## Renamed section/' \
  "$tmp_root/skills/implementaudit/templates/THINKING.md" \
  >"$tmp_root/thinking.tmp"
mv "$tmp_root/thinking.tmp" \
  "$tmp_root/skills/implementaudit/templates/THINKING.md"
expect_fail "THINKING.md without the Action selection section"

# 5. A negative fixture disappears -> must fail.
reset_sandbox
rm "$tmp_root/fixtures/audit-action-selection/negative-keyword-gated-depth.md"
expect_fail "missing negative-keyword-gated-depth fixture"

# 6. Command-mode advertisement in the new surfaces -> must fail.
reset_sandbox
printf '\nAdvertised mode: /implementaudit deep\n' \
  >>"$tmp_root/fixtures/audit-action-selection/ordinary-task-deepens.md"
expect_fail "command-mode advertisement in an action-selection fixture"

# 7. The engineering-value owner clause disappears -> must fail.
reset_sandbox
sed '/^## Engineering-value admission and control lifecycle$/,/^## Unit independence and change class$/{
  /^## Unit independence and change class$/!d
}' "$tmp_root/skills/implementaudit/references/planning-depth.md" \
  >"$tmp_root/planning-depth.tmp"
mv "$tmp_root/planning-depth.tmp" \
  "$tmp_root/skills/implementaudit/references/planning-depth.md"
expect_fail "missing engineering-value admission owner"

# 8. A changed expected answer cannot make an invalid control green.
reset_sandbox
"${py_cmd[@]}" - \
  "$tmp_root/fixtures/audit-action-selection/engineering-value-cases.json" <<'PY'
import json
import pathlib
import sys

path = pathlib.Path(sys.argv[1])
payload = json.loads(path.read_text(encoding="utf-8"))
payload["cases"][0]["expected"] = "ADMIT"
path.write_text(json.dumps(payload), encoding="utf-8")
PY
expect_fail "changed expected answer for the tiny cheap path"

# 9. Truthy strings cannot impersonate observed boolean state.
reset_sandbox
"${py_cmd[@]}" - \
  "$tmp_root/fixtures/audit-action-selection/engineering-value-cases.json" <<'PY'
import json
import pathlib
import sys

path = pathlib.Path(sys.argv[1])
payload = json.loads(path.read_text(encoding="utf-8"))
payload["cases"][1]["observations"]["activation"] = "yes"
path.write_text(json.dumps(payload), encoding="utf-8")
PY
expect_fail "truthy string substituted for an observed boolean"

# 10. Process-heavy evidence derives activation even when the caller's flag is false.
reset_sandbox
"${py_cmd[@]}" - \
  "$tmp_root/fixtures/audit-action-selection/engineering-value-cases.json" <<'PY'
import json
import pathlib
import sys

path = pathlib.Path(sys.argv[1])
payload = json.loads(path.read_text(encoding="utf-8"))
case = next(item for item in payload["cases"] if item["id"] == "R34-C01-tiny-cheap-path")
case["observations"]["process_heavy_or_disputed"] = True
case["expected"] = "DEEP_RETROSPECTIVE"
path.write_text(json.dumps(payload), encoding="utf-8")
PY
bash scripts/check-action-selection-contract.sh --repo-root "$tmp_root" \
  >/dev/null 2>&1 || fail "held-out process-heavy activation derivation failed"

# 11. Closed disjoint cells still need an explicit reconciliation point.
reset_sandbox
"${py_cmd[@]}" - \
  "$tmp_root/fixtures/audit-action-selection/engineering-value-cases.json" <<'PY'
import json
import pathlib
import sys

path = pathlib.Path(sys.argv[1])
payload = json.loads(path.read_text(encoding="utf-8"))
case = next(item for item in payload["cases"] if item["id"] == "R34-C45-disjoint-cells-no-shared-cell")
case["observations"]["disjoint_cells"] = 1
case["observations"]["reconciliation_point"] = False
case["expected"] = "SERIALISE_SHARED"
path.write_text(json.dumps(payload), encoding="utf-8")
PY
bash scripts/check-action-selection-contract.sh --repo-root "$tmp_root" \
  >/dev/null 2>&1 || fail "held-out missing reconciliation point was called parallel-safe"

# 12. A protective buffer is not waste merely because it consumes capacity.
reset_sandbox
"${py_cmd[@]}" - \
  "$tmp_root/fixtures/audit-action-selection/engineering-value-cases.json" <<'PY'
import json
import pathlib
import sys

path = pathlib.Path(sys.argv[1])
payload = json.loads(path.read_text(encoding="utf-8"))
case = next(item for item in payload["cases"] if item["id"] == "R34-C73-protective-buffer")
case["expected"] = "REJECT"
path.write_text(json.dumps(payload), encoding="utf-8")
PY
expect_fail "protective buffer misclassified as waste"

# 13. Feedback frequency without actionable information is not value evidence.
reset_sandbox
"${py_cmd[@]}" - \
  "$tmp_root/fixtures/audit-action-selection/engineering-value-cases.json" <<'PY'
import json
import pathlib
import sys

path = pathlib.Path(sys.argv[1])
payload = json.loads(path.read_text(encoding="utf-8"))
case = next(item for item in payload["cases"] if item["id"] == "R34-C75-actionable-feedback")
case["observations"]["actionable_information"] = False
case["expected"] = "SELECT_PROPORTIONATE_CONTROL"
path.write_text(json.dumps(payload), encoding="utf-8")
PY
expect_fail "non-actionable feedback retained as proportionate"

# 14. Temporary option value ends when carrying cost dominates.
reset_sandbox
"${py_cmd[@]}" - \
  "$tmp_root/fixtures/audit-action-selection/engineering-value-cases.json" <<'PY'
import json
import pathlib
import sys

path = pathlib.Path(sys.argv[1])
payload = json.loads(path.read_text(encoding="utf-8"))
case = next(item for item in payload["cases"] if item["id"] == "R34-C79-bounded-option-value")
case["observations"]["benefit_exceeds_carrying_cost"] = False
case["expected"] = "RETIRE"
path.write_text(json.dumps(payload), encoding="utf-8")
PY
bash scripts/check-action-selection-contract.sh --repo-root "$tmp_root" \
  >/dev/null 2>&1 || fail "held-out option retirement was not derived from carrying cost"

# 15. Universal utilisation/WIP/cadence rules cannot self-authorise.
reset_sandbox
"${py_cmd[@]}" - \
  "$tmp_root/fixtures/audit-action-selection/engineering-value-cases.json" <<'PY'
import json
import pathlib
import sys

path = pathlib.Path(sys.argv[1])
payload = json.loads(path.read_text(encoding="utf-8"))
case = next(item for item in payload["cases"] if item["id"] == "R34-C77-sustainable-recovery-capacity")
case["observations"]["universal_rule"] = True
case["expected"] = "SELECT_PROPORTIONATE_CONTROL"
path.write_text(json.dumps(payload), encoding="utf-8")
PY
expect_fail "universal maximum-utilisation rule accepted"

# 16. The native rule must stay ceremony-free.
reset_sandbox
"${py_cmd[@]}" - \
  "$tmp_root/fixtures/audit-action-selection/engineering-value-cases.json" <<'PY'
import json
import pathlib
import sys

path = pathlib.Path(sys.argv[1])
payload = json.loads(path.read_text(encoding="utf-8"))
case = next(item for item in payload["cases"] if item["id"] == "R34-C75-actionable-feedback")
case["observations"]["methodology_ceremony"] = True
case["expected"] = "SELECT_PROPORTIONATE_CONTROL"
path.write_text(json.dumps(payload), encoding="utf-8")
PY
expect_fail "methodology ceremony accepted as a native control"

# 17. The executable population remains bound to its native owner prose.
reset_sandbox
grep -v "Feedback value depends on actionable" \
  "$tmp_root/skills/implementaudit/references/planning-depth.md" \
  >"$tmp_root/planning-depth.tmp"
mv "$tmp_root/planning-depth.tmp" \
  "$tmp_root/skills/implementaudit/references/planning-depth.md"
expect_fail "actionability rule removed from native owner prose"

# 18. A completed cell recomputes the frontier and activates newly ready work.
# This catches a scheduler that records static parallel safety but never uses
# freed capacity after a dependency transition.
reset_sandbox
"${py_cmd[@]}" - \
  "$tmp_root/fixtures/audit-action-selection/engineering-value-cases.json" <<'PY'
import json
import pathlib
import sys

path = pathlib.Path(sys.argv[1])
payload = json.loads(path.read_text(encoding="utf-8"))
case = next(item for item in payload["cases"] if item["id"] == "R34-C01-tiny-cheap-path")
case["kind"] = "scheduling"
case["observations"] = {
    "event": "cell_complete",
    "work_units": 4,
    "host_capacity": 2,
    "operator_ceiling": -1,
    "active_cells": 1,
    "ready_cells": 1,
    "parallelism_allowed": True,
    "cell_independence_known": True,
    "closed_write_boundaries": True,
    "closed_acceptance_boundaries": True,
    "closed_resource_boundaries": True,
    "closed_authority_boundaries": True,
    "authority_boundary_open": False,
    "irreversible_external": False,
    "authorization_current": True,
}
case["expected"] = "RECOMPUTE_AND_ACTIVATE"
path.write_text(json.dumps(payload), encoding="utf-8")
PY
bash scripts/check-action-selection-contract.sh --repo-root "$tmp_root" \
  >/dev/null 2>&1 || fail "completed cell did not activate newly ready independent work"

# 19. A shared resource claim cannot be relabelled as work-conserving activation.
reset_sandbox
"${py_cmd[@]}" - \
  "$tmp_root/fixtures/audit-action-selection/engineering-value-cases.json" <<'PY'
import json
import pathlib
import sys

path = pathlib.Path(sys.argv[1])
payload = json.loads(path.read_text(encoding="utf-8"))
case = next(item for item in payload["cases"] if item["id"] == "R34-C95-resource-claim-conflict-serialises")
case["expected"] = "ACTIVATE_READY_CELLS"
path.write_text(json.dumps(payload), encoding="utf-8")
PY
expect_fail "resource conflict relabelled as parallel activation"

# 20. Unknown independence cannot be treated as an activatable ready cell.
reset_sandbox
"${py_cmd[@]}" - \
  "$tmp_root/fixtures/audit-action-selection/engineering-value-cases.json" <<'PY'
import json
import pathlib
import sys

path = pathlib.Path(sys.argv[1])
payload = json.loads(path.read_text(encoding="utf-8"))
case = next(item for item in payload["cases"] if item["id"] == "R34-C92-unknown-independence-defers")
case["expected"] = "ACTIVATE_READY_CELLS"
path.write_text(json.dumps(payload), encoding="utf-8")
PY
expect_fail "unknown independence relabelled as parallel activation"

# 21. Host capacity one retains the ordinary cheap serial path.
reset_sandbox
"${py_cmd[@]}" - \
  "$tmp_root/fixtures/audit-action-selection/engineering-value-cases.json" <<'PY'
import json
import pathlib
import sys

path = pathlib.Path(sys.argv[1])
payload = json.loads(path.read_text(encoding="utf-8"))
case = next(item for item in payload["cases"] if item["id"] == "R34-C97-host-capacity-one-cheap-serial")
case["expected"] = "ACTIVATE_READY_CELLS"
path.write_text(json.dumps(payload), encoding="utf-8")
PY
expect_fail "host-capacity-one cheap path relabelled as parallel activation"

# 22. An unchanged reminder is not a frontier event or redispatch warrant.
reset_sandbox
"${py_cmd[@]}" - \
  "$tmp_root/fixtures/audit-action-selection/engineering-value-cases.json" <<'PY'
import json
import pathlib
import sys

path = pathlib.Path(sys.argv[1])
payload = json.loads(path.read_text(encoding="utf-8"))
case = next(item for item in payload["cases"] if item["id"] == "R34-C99-reminder-does-not-redispatch")
case["expected"] = "RECOMPUTE_AND_ACTIVATE"
path.write_text(json.dumps(payload), encoding="utf-8")
PY
expect_fail "unchanged reminder relabelled as a frontier event"

# 23. The executable scheduling population must remain bound to its native
# ready-frontier execution owner, not merely to fixture verdicts.
reset_sandbox
grep -v "Maintain a ready-cell frontier" \
  "$tmp_root/skills/implementaudit/references/child-agents.md" \
  >"$tmp_root/child-agents.tmp"
mv "$tmp_root/child-agents.tmp" \
  "$tmp_root/skills/implementaudit/references/child-agents.md"
expect_fail "ready-frontier execution owner removed"

# 24. The always-loaded runtime loop must progressively activate closed
# frontier accounting rather than merely permit it in a deep reference.
reset_sandbox
grep -v "reacquire a closed DONE/ACTIVE/READY/BLOCKED census" \
  "$tmp_root/skills/implementaudit/SKILL.md" \
  >"$tmp_root/SKILL.tmp"
mv "$tmp_root/SKILL.tmp" "$tmp_root/skills/implementaudit/SKILL.md"
expect_fail "closed frontier census runtime route removed"

# 25. Two currently authorised cells that overlap an authority boundary still
# serialize; current authorization is not proof of independent authority.
reset_sandbox
"${py_cmd[@]}" - \
  "$tmp_root/fixtures/audit-action-selection/engineering-value-cases.json" <<'PY'
import json
import pathlib
import sys

path = pathlib.Path(sys.argv[1])
payload = json.loads(path.read_text(encoding="utf-8"))
case = next(item for item in payload["cases"] if item["id"] == "R34-C102-authority-boundary-conflict-serialises")
case["expected"] = "ACTIVATE_READY_CELLS"
path.write_text(json.dumps(payload), encoding="utf-8")
PY
expect_fail "authority conflict relabelled as parallel activation"

# 26. The authority observation, not the fixture label, drives the conflict.
reset_sandbox
"${py_cmd[@]}" - \
  "$tmp_root/fixtures/audit-action-selection/engineering-value-cases.json" <<'PY'
import json
import pathlib
import sys

path = pathlib.Path(sys.argv[1])
payload = json.loads(path.read_text(encoding="utf-8"))
case = next(item for item in payload["cases"] if item["id"] == "R34-C102-authority-boundary-conflict-serialises")
case["observations"]["closed_authority_boundaries"] = True
path.write_text(json.dumps(payload), encoding="utf-8")
PY
expect_fail "authority-conflict observation did not change the derived verdict"

# 27. The serial cheap path must not grow a mandatory scheduler dashboard.
reset_sandbox
sed 's/, dashboard//' \
  "$tmp_root/skills/implementaudit/references/child-agents.md" \
  >"$tmp_root/child-agents.tmp"
mv "$tmp_root/child-agents.tmp" \
  "$tmp_root/skills/implementaudit/references/child-agents.md"
expect_fail "dashboard prohibition removed from cheap-path owner"

# 28. Completion must recompute and activate a newly ready cell.
reset_sandbox
"${py_cmd[@]}" - \
  "$tmp_root/fixtures/audit-action-selection/engineering-value-cases.json" <<'PY'
import json
import pathlib
import sys

path = pathlib.Path(sys.argv[1])
payload = json.loads(path.read_text(encoding="utf-8"))
case = next(item for item in payload["cases"] if item["id"] == "R34-C104-completion-recomputes-frontier")
case["expected"] = "HOLD_FRONTIER"
path.write_text(json.dumps(payload), encoding="utf-8")
PY
expect_fail "completion bypassed ready-frontier recomputation"

# 29. An operator ceiling must remain an upper bound, not disappear into host capacity.
reset_sandbox
"${py_cmd[@]}" - \
  "$tmp_root/fixtures/audit-action-selection/engineering-value-cases.json" <<'PY'
import json
import pathlib
import sys

path = pathlib.Path(sys.argv[1])
payload = json.loads(path.read_text(encoding="utf-8"))
case = next(item for item in payload["cases"] if item["id"] == "R34-C109-operator-ceiling-bounds-frontier")
case["observations"]["operator_ceiling"] = -1
path.write_text(json.dumps(payload), encoding="utf-8")
PY
expect_fail "operator ceiling ignored"

# 30. A live self-confirmation trigger cannot fall back to same-root execution.
reset_sandbox
"${py_cmd[@]}" - \
  "$tmp_root/fixtures/audit-action-selection/engineering-value-cases.json" <<'PY'
import json
import pathlib
import sys

path = pathlib.Path(sys.argv[1])
payload = json.loads(path.read_text(encoding="utf-8"))
case = next(item for item in payload["cases"] if item["id"] == "R34-C115-triggered-planner-executor-separation")
case["expected"] = "SAME_ROOT"
path.write_text(json.dumps(payload), encoding="utf-8")
PY
expect_fail "self-confirmation trigger collapsed to same-root execution"

# 31. Cost cannot select a route whose capability is insufficient.
reset_sandbox
"${py_cmd[@]}" - \
  "$tmp_root/fixtures/audit-action-selection/engineering-value-cases.json" <<'PY'
import json
import pathlib
import sys

path = pathlib.Path(sys.argv[1])
payload = json.loads(path.read_text(encoding="utf-8"))
case = next(item for item in payload["cases"] if item["id"] == "R34-C120-cheaper-incapable-route-rejected")
case["expected"] = "DELEGATE_LEAST_COST_SUFFICIENT"
path.write_text(json.dumps(payload), encoding="utf-8")
PY
expect_fail "incapable lower-cost route selected"

# 32. The cross-boundary context/revalidation owner clause is mandatory.
reset_sandbox
sed '/This prompt is an explicit context capsule/,/issuing any disposition\./d' \
  "$tmp_root/skills/implementaudit/references/plan-lifecycle.md" \
  >"$tmp_root/plan-lifecycle.tmp"
mv "$tmp_root/plan-lifecycle.tmp" \
  "$tmp_root/skills/implementaudit/references/plan-lifecycle.md"
expect_fail "missing context capsule and fresh-source revalidation"

# 33. Cross-repo behavior cannot be credited from a success-shaped receipt
# that hides activation-keyword leakage.
reset_sandbox
"${py_cmd[@]}" - \
  "$tmp_root/fixtures/audit-action-selection/dominance-dogfood-receipt.json" <<'PY'
import json
import pathlib
import sys

path = pathlib.Path(sys.argv[1])
payload = json.loads(path.read_text(encoding="utf-8"))
payload["activation_prompt_leakage"] = True
path.write_text(json.dumps(payload), encoding="utf-8")
PY
expect_fail "dogfood receipt with activation-keyword leakage"

# 34. The timed-out combined cell must remain rejected non-evidence.
reset_sandbox
"${py_cmd[@]}" - \
  "$tmp_root/fixtures/audit-action-selection/dominance-dogfood-receipt.json" <<'PY'
import json
import pathlib
import sys

path = pathlib.Path(sys.argv[1])
payload = json.loads(path.read_text(encoding="utf-8"))
payload["cells"][-1]["disposition"] = "PASS"
path.write_text(json.dumps(payload), encoding="utf-8")
PY
expect_fail "timed-out dogfood cell promoted to PASS"

# 35. Current authorization cannot impersonate an unresolved authority boundary.
reset_sandbox
"${py_cmd[@]}" - \
  "$tmp_root/fixtures/audit-action-selection/engineering-value-cases.json" <<'PY'
import json
import pathlib
import sys

path = pathlib.Path(sys.argv[1])
payload = json.loads(path.read_text(encoding="utf-8"))
case = next(item for item in payload["cases"] if item["id"] == "R34-C126-open-authority-boundary-defers")
case["expected"] = "ACTIVATE_READY_CELLS"
path.write_text(json.dumps(payload), encoding="utf-8")
PY
expect_fail "open authority boundary activated"

# 36. Drift is a reconciliation event even on the serial cheap path.
reset_sandbox
"${py_cmd[@]}" - \
  "$tmp_root/fixtures/audit-action-selection/engineering-value-cases.json" <<'PY'
import json
import pathlib
import sys

path = pathlib.Path(sys.argv[1])
payload = json.loads(path.read_text(encoding="utf-8"))
case = next(item for item in payload["cases"] if item["id"] == "R34-C127-small-drift-still-reconciles")
case["expected"] = "SERIAL_CHEAP_PATH"
path.write_text(json.dumps(payload), encoding="utf-8")
PY
expect_fail "serial cheap path hid drift reconciliation"

# 37. Recomputing under a zero ceiling cannot activate a ready cell.
reset_sandbox
"${py_cmd[@]}" - \
  "$tmp_root/fixtures/audit-action-selection/engineering-value-cases.json" <<'PY'
import json
import pathlib
import sys

path = pathlib.Path(sys.argv[1])
payload = json.loads(path.read_text(encoding="utf-8"))
case = next(item for item in payload["cases"] if item["id"] == "R34-C130-zero-ceiling-completion-recomputes-without-activation")
case["expected"] = "RECOMPUTE_AND_ACTIVATE"
path.write_text(json.dumps(payload), encoding="utf-8")
PY
expect_fail "zero-ceiling recomputation activated a ready cell"

# 38. A completion frees only the bounded slot left after the closed frontier
# census; it does not reset active work to zero or spend the whole ceiling.
reset_sandbox
"${py_cmd[@]}" - \
  "$tmp_root/fixtures/audit-action-selection/engineering-value-cases.json" <<'PY'
import json
import pathlib
import sys

path = pathlib.Path(sys.argv[1])
payload = json.loads(path.read_text(encoding="utf-8"))
case = next(item for item in payload["cases"] if item["id"] == "R34-C131-completion-frees-one-bounded-slot")
case["observations"]["done_cells"] = 2
case["observations"]["active_cells"] = 0
path.write_text(json.dumps(payload), encoding="utf-8")
PY
expect_fail "completed cell reset the active census and overspent the ceiling"

# 39. The executable discriminator remains bound to the native runtime owner.
reset_sandbox
grep -v "state prevents dispatch" \
  "$tmp_root/skills/implementaudit/references/child-agents.md" \
  >"$tmp_root/child-agents.tmp"
mv "$tmp_root/child-agents.tmp" \
  "$tmp_root/skills/implementaudit/references/child-agents.md"
expect_fail "closed frontier census runtime owner removed"

# 40. A larger population derives three free slots from current occupancy;
# changing DONE/ACTIVE labels without changing the total must change dispatch.
reset_sandbox
"${py_cmd[@]}" - \
  "$tmp_root/fixtures/audit-action-selection/engineering-value-cases.json" <<'PY'
import json
import pathlib
import sys

path = pathlib.Path(sys.argv[1])
payload = json.loads(path.read_text(encoding="utf-8"))
case = next(item for item in payload["cases"] if item["id"] == "R34-C132-closed-population-bounds-three-slots")
case["observations"]["done_cells"] = 4
case["observations"]["active_cells"] = 1
path.write_text(json.dumps(payload), encoding="utf-8")
PY
expect_fail "larger closed population ignored active occupancy"

# 41. READY cardinality, not spare ceiling alone, bounds dispatch.
reset_sandbox
"${py_cmd[@]}" - \
  "$tmp_root/fixtures/audit-action-selection/engineering-value-cases.json" <<'PY'
import json
import pathlib
import sys

path = pathlib.Path(sys.argv[1])
payload = json.loads(path.read_text(encoding="utf-8"))
case = next(item for item in payload["cases"] if item["id"] == "R34-C133-ready-population-bounds-one-dispatch")
case["expected"] = "DISPATCH_5_READY_CELLS"
path.write_text(json.dumps(payload), encoding="utf-8")
PY
expect_fail "spare ceiling overrode ready cardinality"

# 42. An unknown cell cannot be relabelled BLOCKED to manufacture free capacity.
reset_sandbox
"${py_cmd[@]}" - \
  "$tmp_root/fixtures/audit-action-selection/engineering-value-cases.json" <<'PY'
import json
import pathlib
import sys

path = pathlib.Path(sys.argv[1])
payload = json.loads(path.read_text(encoding="utf-8"))
case = next(item for item in payload["cases"] if item["id"] == "R34-C134-unknown-population-refuses-capacity-assumption")
case["observations"]["unknown_cells"] = 0
case["observations"]["blocked_cells"] = 1
path.write_text(json.dumps(payload), encoding="utf-8")
PY
expect_fail "unknown cell was laundered into free capacity"

# 43. A complete-looking but stale state partition is not dispatch authority.
reset_sandbox
"${py_cmd[@]}" - \
  "$tmp_root/fixtures/audit-action-selection/engineering-value-cases.json" <<'PY'
import json
import pathlib
import sys

path = pathlib.Path(sys.argv[1])
payload = json.loads(path.read_text(encoding="utf-8"))
case = next(item for item in payload["cases"] if item["id"] == "R34-C135-stale-population-refuses-dispatch")
case["observations"]["state_evidence_current"] = True
path.write_text(json.dumps(payload), encoding="utf-8")
PY
expect_fail "stale frontier state was treated as current dispatch authority"

# 44. An executor-ready handoff cannot claim READY before live source grounds
# its exact state, scope, edits, and verification route.
reset_sandbox
"${py_cmd[@]}" - \
  "$tmp_root/fixtures/audit-action-selection/engineering-value-cases.json" <<'PY'
import json
import pathlib
import sys

path = pathlib.Path(sys.argv[1])
payload = json.loads(path.read_text(encoding="utf-8"))
case = next(item for item in payload["cases"] if item["id"] == "R31-C137-uninspected-plan-held")
case["expected"] = "EXECUTOR_PLAN_READY"
path.write_text(json.dumps(payload), encoding="utf-8")
PY
expect_fail "uninspected speculative executor plan claimed READY"

# 45. The READY positive requires every reconstructibility field; schema shape
# plus generic STOP/rollback prose cannot replace exact current-state evidence.
reset_sandbox
"${py_cmd[@]}" - \
  "$tmp_root/fixtures/audit-action-selection/engineering-value-cases.json" <<'PY'
import json
import pathlib
import sys

path = pathlib.Path(sys.argv[1])
payload = json.loads(path.read_text(encoding="utf-8"))
case = next(item for item in payload["cases"] if item["id"] == "R31-C136-grounded-executor-plan-ready")
case["observations"]["current_state_exact"] = False
path.write_text(json.dumps(payload), encoding="utf-8")
PY
expect_fail "generic plan shape replaced exact current state"

# 46. The executable discriminator remains bound to the R001F lifecycle owner.
reset_sandbox
grep -v "cannot claim READY" \
  "$tmp_root/skills/implementaudit/references/plan-lifecycle.md" \
  >"$tmp_root/plan-lifecycle.tmp"
mv "$tmp_root/plan-lifecycle.tmp" \
  "$tmp_root/skills/implementaudit/references/plan-lifecycle.md"
expect_fail "executor-plan source-grounding owner removed"

# 47. Live grounding does not authorize optional ancillary tidy-up files.
reset_sandbox
"${py_cmd[@]}" - \
  "$tmp_root/fixtures/audit-action-selection/engineering-value-cases.json" <<'PY'
import json
import pathlib
import sys

path = pathlib.Path(sys.argv[1])
payload = json.loads(path.read_text(encoding="utf-8"))
case = next(item for item in payload["cases"] if item["id"] == "R31-C136-grounded-executor-plan-ready")
case["observations"]["scope_exact"] = False
path.write_text(json.dumps(payload), encoding="utf-8")
PY
expect_fail "optional ancillary file expanded executor authority"

# 48. Remove the closed-scope owner phrase while leaving source grounding.
reset_sandbox
grep -v "Optional ancillary files remain out of scope" \
  "$tmp_root/skills/implementaudit/references/plan-lifecycle.md" \
  >"$tmp_root/plan-lifecycle.tmp"
mv "$tmp_root/plan-lifecycle.tmp" \
  "$tmp_root/skills/implementaudit/references/plan-lifecycle.md"
expect_fail "closed executor mutation scope owner removed"

# 49. The catalogue trigger must route scheduling decisions to the executable
# owner instead of allowing a description-only claim of skill use.
reset_sandbox
grep -v "For scheduling/dispatch/resource ceilings, read" \
  "$tmp_root/skills/implementaudit/SKILL.md" \
  >"$tmp_root/SKILL.tmp"
mv "$tmp_root/SKILL.tmp" \
  "$tmp_root/skills/implementaudit/SKILL.md"
expect_fail "scheduling catalogue route removed"

# 50. Reconciliation must expose population conservation and occupied-capacity
# arithmetic before dispatch; merely asserting that reconciliation occurred is
# not an observable scheduling discriminator.
reset_sandbox
grep -v "Before dispatch, expose:" \
  "$tmp_root/skills/implementaudit/references/child-agents.md" \
  >"$tmp_root/child-agents.tmp"
mv "$tmp_root/child-agents.tmp" \
  "$tmp_root/skills/implementaudit/references/child-agents.md"
expect_fail "frontier conservation proof owner removed"

# 51. Occupancy arithmetic is deterministic plumbing. Removing its tool-use
# boundary must fail even when the equations remain as plausible prose.
reset_sandbox
grep -v "Use deterministic tooling, not model estimates" \
  "$tmp_root/skills/implementaudit/references/child-agents.md" \
  >"$tmp_root/child-agents.tmp"
mv "$tmp_root/child-agents.tmp" \
  "$tmp_root/skills/implementaudit/references/child-agents.md"
expect_fail "deterministic frontier arithmetic boundary removed"

# 52. A zero operator ceiling is an explicit no-dispatch bound, not an absent
# ceiling that silently falls back to host capacity.
reset_sandbox
grep -v "capacity = 0 at ceiling 0" \
  "$tmp_root/skills/implementaudit/references/child-agents.md" \
  >"$tmp_root/child-agents.tmp"
mv "$tmp_root/child-agents.tmp" \
  "$tmp_root/skills/implementaudit/references/child-agents.md"
expect_fail "zero-ceiling capacity branch removed"

# 53. Completion may leave ACTIVE at zero, but it cannot infer that other
# governed activity vanished merely because one cell completed.
reset_sandbox
grep -v "never infer other ACTIVE=0" \
  "$tmp_root/skills/implementaudit/references/child-agents.md" \
  >"$tmp_root/child-agents.tmp"
mv "$tmp_root/child-agents.tmp" \
  "$tmp_root/skills/implementaudit/references/child-agents.md"
expect_fail "completion inferred other active cells were zero"

# 54. A high-consequence control cannot pass without the complete target,
# feedback, containment, and recovery envelope.
reset_sandbox
"${py_cmd[@]}" - \
  "$tmp_root/fixtures/audit-action-selection/engineering-value-cases.json" <<'PY'
import json, pathlib, sys
path = pathlib.Path(sys.argv[1])
payload = json.loads(path.read_text(encoding="utf-8"))
case = next(x for x in payload["cases"] if x["id"] == "R44-C142-high-consequence-control-trigger")
case["observations"]["containment"] = False
path.write_text(json.dumps(payload), encoding="utf-8")
PY
expect_fail "high-consequence control accepted without containment"

# 55. Method labels never replace the consequence-control discriminator.
reset_sandbox
"${py_cmd[@]}" - \
  "$tmp_root/fixtures/audit-action-selection/engineering-value-cases.json" <<'PY'
import json, pathlib, sys
path = pathlib.Path(sys.argv[1])
payload = json.loads(path.read_text(encoding="utf-8"))
case = next(x for x in payload["cases"] if x["id"] == "R44-C145-risk-matrix-insufficient")
case["expected"] = "SELECT_CONSEQUENCE_CONTROL"
path.write_text(json.dumps(payload), encoding="utf-8")
PY
expect_fail "risk-matrix label accepted as sufficient control evidence"

# 56. A bounded control with an established safe stop and no material trigger
# is the cheap path; it must not inherit BLOCK from the rejected material case.
reset_sandbox
"${py_cmd[@]}" - \
  "$tmp_root/fixtures/audit-action-selection/engineering-value-cases.json" <<'PY'
import json, pathlib, sys
path = pathlib.Path(sys.argv[1])
payload = json.loads(path.read_text(encoding="utf-8"))
case = next(x for x in payload["cases"] if x["id"] == "R34-C146-safe-stop-control-cheap-path")
case["expected"] = "BLOCK"
path.write_text(json.dumps(payload), encoding="utf-8")
PY
expect_fail "safe-stop control inherited material BLOCK"

# 57. A nominal override remains insufficient even when every other field
# resembles the safe-stop control cheap path.
reset_sandbox
"${py_cmd[@]}" - \
  "$tmp_root/fixtures/audit-action-selection/engineering-value-cases.json" <<'PY'
import json, pathlib, sys
path = pathlib.Path(sys.argv[1])
payload = json.loads(path.read_text(encoding="utf-8"))
case = next(x for x in payload["cases"] if x["id"] == "R34-C146-safe-stop-control-cheap-path")
case["observations"]["nominal_override_only"] = True
path.write_text(json.dumps(payload), encoding="utf-8")
PY
expect_fail "nominal override accepted as safe-stop cheap path"

# 58. An omitted semantic owner cannot be relabelled as a serial cheap plan.
reset_sandbox
"${py_cmd[@]}" - \
  "$tmp_root/fixtures/audit-action-selection/verifier-plan-cases.json" <<'PY'
import json, pathlib, sys
path = pathlib.Path(sys.argv[1])
payload = json.loads(path.read_text(encoding="utf-8"))
case = next(x for x in payload["cases"] if x["id"] == "R0022-V01-owner-omitted-under-scoped")
case["expected"] = "SERIAL_CHEAP_PATH"
path.write_text(json.dumps(payload), encoding="utf-8")
PY
expect_fail "under-scoped verifier plan accepted with omitted semantic owner"

# 59. Consumer and effect omissions are equally unable to retain a cheap plan.
for case_id in R0022-V02-consumer-omitted-under-scoped R0022-V03-effect-omitted-under-scoped; do
  reset_sandbox
  "${py_cmd[@]}" - \
    "$tmp_root/fixtures/audit-action-selection/verifier-plan-cases.json" \
    "$case_id" <<'PY'
import json, pathlib, sys
path = pathlib.Path(sys.argv[1])
case_id = sys.argv[2]
payload = json.loads(path.read_text(encoding="utf-8"))
case = next(x for x in payload["cases"] if x["id"] == case_id)
case["expected"] = "SERIAL_CHEAP_PATH"
path.write_text(json.dumps(payload), encoding="utf-8")
PY
  expect_fail "under-scoped verifier plan accepted for $case_id"
done

# 60. Wider transitive, package, public, and external impacts have their own
# affected verifier and cannot collapse to the cheap local path.
for case_id in R0022-V07-transitive-consumer-verifier-plan R0022-V08-package-consumer-verifier-plan R0022-V09-public-consumer-verifier-plan R0022-V10-external-consumer-verifier-plan; do
  reset_sandbox
  "${py_cmd[@]}" - \
    "$tmp_root/fixtures/audit-action-selection/verifier-plan-cases.json" \
    "$case_id" <<'PY'
import json, pathlib, sys
path = pathlib.Path(sys.argv[1])
case_id = sys.argv[2]
payload = json.loads(path.read_text(encoding="utf-8"))
case = next(x for x in payload["cases"] if x["id"] == case_id)
case["expected"] = "SERIAL_CHEAP_PATH"
path.write_text(json.dumps(payload), encoding="utf-8")
PY
  expect_fail "under-scoped verifier plan accepted for $case_id"
done

# 61. Relation, registry, ambiguity, and projection uncertainty each has one
# live predicate; no second true predicate may mask its omission.
for case_id in R0022-V11-unknown-relation-only-escalates R0022-V12-registry-change-only-escalates R0022-V13-package-or-release-ambiguity-only-escalates R0022-V14-stale-projection-only-escalates; do
  reset_sandbox
  "${py_cmd[@]}" - \
    "$tmp_root/fixtures/audit-action-selection/verifier-plan-cases.json" \
    "$case_id" <<'PY'
import json, pathlib, sys
path = pathlib.Path(sys.argv[1])
case_id = sys.argv[2]
payload = json.loads(path.read_text(encoding="utf-8"))
case = next(x for x in payload["cases"] if x["id"] == case_id)
case["expected"] = "SERIAL_CHEAP_PATH"
path.write_text(json.dumps(payload), encoding="utf-8")
PY
  expect_fail "conservative verifier plan relabelled as cheap for $case_id"
done

# 62. Multiple independent affected consumers retain the composed outcome.
reset_sandbox
"${py_cmd[@]}" - \
  "$tmp_root/fixtures/audit-action-selection/verifier-plan-cases.json" <<'PY'
import json, pathlib, sys
path = pathlib.Path(sys.argv[1])
payload = json.loads(path.read_text(encoding="utf-8"))
case = next(x for x in payload["cases"] if x["id"] == "R0022-V15-generated-package-composed-verifier-plan")
case["expected"] = "VERIFY_PACKAGE_CONSUMER"
path.write_text(json.dumps(payload), encoding="utf-8")
PY
expect_fail "multi-impact verifier plan lost composed outcome"

# 63. The reviewed 31/18/4/6/1 proof-layer partition is exact and retains the
# external/domain rows as unverified rather than silently closing them.
reset_sandbox
"${py_cmd[@]}" - \
  "$tmp_root/fixtures/audit-action-selection/security-profile-cases.json" <<'PY'
import json, pathlib, sys
path = pathlib.Path(sys.argv[1])
payload = json.loads(path.read_text(encoding="utf-8"))
payload["proof_layer_partition"]["external_domain_unverified"] = 5
path.write_text(json.dumps(payload), encoding="utf-8")
PY
expect_fail "security profile accepted a changed proof-layer partition"

# 64. Each bounded security-profile control has a distinct observable outcome;
# relabelling one as its distractor must fail against the real checker.
while IFS='|' read -r case_id wrong_expected; do
  reset_sandbox
  "${py_cmd[@]}" - \
    "$tmp_root/fixtures/audit-action-selection/security-profile-cases.json" \
    "$case_id" "$wrong_expected" <<'PY'
import json, pathlib, sys
path = pathlib.Path(sys.argv[1])
case_id, wrong_expected = sys.argv[2:]
payload = json.loads(path.read_text(encoding="utf-8"))
case = next(x for x in payload["cases"] if x["id"] == case_id)
case["expected"] = wrong_expected
path.write_text(json.dumps(payload), encoding="utf-8")
PY
  expect_fail "security-profile control relabelled for $case_id"
done <<'EOF'
R002E-S01-material-profile-selected|NO_SECURITY_PROFILE
R002E-S02-low-exposure-cheap-path|SELECT_NATIVE_SECURITY_PROFILE
R002E-S03-stale-provenance-blocked|SELECT_NATIVE_SECURITY_PROFILE
R002E-S04-authentication-is-not-authorization|SELECT_NATIVE_SECURITY_PROFILE
R002E-S05-availability-is-not-trust-restoration|SELECT_NATIVE_SECURITY_PROFILE
R002E-S06-label-only-proof-rejected|SELECT_NATIVE_SECURITY_PROFILE
R002E-S07-no-trigger-no-profile|SELECT_NATIVE_SECURITY_PROFILE
R002E-S08-unbounded-adversary-held|SELECT_NATIVE_SECURITY_PROFILE
R002E-S09-missing-assurance-evidence-held|SELECT_NATIVE_SECURITY_PROFILE
EOF

# 65. Assurance evidence and the limits of that evidence are independent
# completeness dimensions; the fixture must hold when evidence itself is absent.
"${py_cmd[@]}" - \
  fixtures/audit-action-selection/security-profile-cases.json <<'PY'
import json, pathlib, sys
path = pathlib.Path(sys.argv[1])
payload = json.loads(path.read_text(encoding="utf-8"))
cases = payload["cases"]
missing = [case["id"] for case in cases
           if "assurance_evidence" not in case["observations"]]
if missing:
    raise SystemExit("security-profile cases missing assurance_evidence: " + ", ".join(missing))
case = next((item for item in cases
             if item["id"] == "R002E-S09-missing-assurance-evidence-held"), None)
if case is None:
    raise SystemExit("missing assurance-evidence negative control")
if case["observations"]["assurance_evidence"] is not False:
    raise SystemExit("missing assurance-evidence control is not false")
if case["observations"]["assurance_limits"] is not True:
    raise SystemExit("missing assurance-evidence control also removed assurance limits")
if case["expected"] != "HOLD_INCOMPLETE_PROFILE":
    raise SystemExit("missing assurance-evidence control has wrong outcome")
PY

# 66. Every accepted trigger-family clause is independently pinned. Removing
# any one from the sandbox owner must make the static checker fail.
while IFS= read -r trigger_clause; do
  reset_sandbox
  "${py_cmd[@]}" - \
    "$tmp_root/skills/implementaudit/references/planning-depth.md" \
    "$trigger_clause" <<'PY'
import pathlib, sys
path = pathlib.Path(sys.argv[1])
clause = sys.argv[2]
text = path.read_text(encoding="utf-8")
if text.count(clause) != 1:
    raise SystemExit(f"trigger clause occurrence mismatch for {clause!r}")
path.write_text(text.replace(clause, "[deleted trigger clause]"), encoding="utf-8")
PY
  expect_fail "security-profile trigger clause removed: $trigger_clause"
done <<'EOF'
material protected consequence
or untrusted capability
changed trust, privilege, or delegation boundary
consequential security authority
provenance-dependent claim
adaptive-adversary or common-mode risk
weak detection or recovery
consequential security, privacy, safety, availability, or usability decision
EOF

# 67. Each named non-proof proxy is independently pinned in the accepted prose.
# A generic whole-system sentence cannot mask deletion of a concrete proxy.
while IFS= read -r proxy_token; do
  reset_sandbox
  "${py_cmd[@]}" - \
    "$tmp_root/skills/implementaudit/references/audit-playbook.md" \
    "$proxy_token" <<'PY'
import pathlib, sys
path = pathlib.Path(sys.argv[1])
token = sys.argv[2]
text = path.read_text(encoding="utf-8")
if text.count(token) != 1:
    raise SystemExit(f"proxy token occurrence mismatch for {token!r}")
path.write_text(text.replace(token, "[deleted proxy token]"), encoding="utf-8")
PY
  expect_fail "security-profile non-proof proxy removed: $proxy_token"
done <<'EOF'
scanner
penetration-test result
SBOM
signature
CVSS score
certificate
encryption label
zero-trust slogan
EOF

# 68. Each trigger family is causally sufficient by itself: with every trigger
# false the complete control observes NO_SECURITY_PROFILE, then toggling only
# the named trigger selects the native profile.
while IFS= read -r trigger_field; do
  reset_sandbox
  "${py_cmd[@]}" - \
    "$tmp_root/fixtures/audit-action-selection/security-profile-cases.json" \
    "$trigger_field" false <<'PY'
import json, pathlib, sys
path = pathlib.Path(sys.argv[1])
trigger_field, enabled = sys.argv[2], sys.argv[3] == "true"
payload = json.loads(path.read_text(encoding="utf-8"))
case = next(x for x in payload["cases"] if x["id"] == "R002E-S01-material-profile-selected")
trigger_fields = (
    "material_protected_consequence", "exposed_or_untrusted_capability",
    "trust_or_privilege_boundary_change", "consequential_security_authority",
    "provenance_dependent_claim", "adaptive_or_common_mode_risk",
    "weak_detection_or_recovery",
    "consequential_security_privacy_safety_availability_usability_decision",
)
for field in trigger_fields:
    case["observations"][field] = False
case["observations"][trigger_field] = enabled
case["expected"] = "SELECT_NATIVE_SECURITY_PROFILE" if enabled else "NO_SECURITY_PROFILE"
path.write_text(json.dumps(payload), encoding="utf-8")
PY
  bash scripts/check-action-selection-contract.sh --repo-root "$tmp_root" \
    >/dev/null 2>&1 || fail "all-false trigger counterfactual failed for $trigger_field"
  "${py_cmd[@]}" - \
    "$tmp_root/fixtures/audit-action-selection/security-profile-cases.json" \
    "$trigger_field" <<'PY'
import json, pathlib, sys
path = pathlib.Path(sys.argv[1])
trigger_field = sys.argv[2]
payload = json.loads(path.read_text(encoding="utf-8"))
case = next(x for x in payload["cases"] if x["id"] == "R002E-S01-material-profile-selected")
case["observations"][trigger_field] = True
case["expected"] = "SELECT_NATIVE_SECURITY_PROFILE"
path.write_text(json.dumps(payload), encoding="utf-8")
PY
  bash scripts/check-action-selection-contract.sh --repo-root "$tmp_root" \
    >/dev/null 2>&1 || fail "sole-trigger counterfactual failed for $trigger_field"
done <<'EOF'
material_protected_consequence
exposed_or_untrusted_capability
trust_or_privilege_boundary_change
consequential_security_authority
provenance_dependent_claim
adaptive_or_common_mode_risk
weak_detection_or_recovery
consequential_security_privacy_safety_availability_usability_decision
EOF

# 69. Authentication, restored availability, and a named label/instrument are
# causal non-proof proxies even when the full profile is otherwise complete.
while IFS='|' read -r proxy_field rejected_outcome; do
  reset_sandbox
  "${py_cmd[@]}" - \
    "$tmp_root/fixtures/audit-action-selection/security-profile-cases.json" \
    "$proxy_field" false "SELECT_NATIVE_SECURITY_PROFILE" <<'PY'
import json, pathlib, sys
path = pathlib.Path(sys.argv[1])
proxy_field, enabled, expected = sys.argv[2], sys.argv[3] == "true", sys.argv[4]
payload = json.loads(path.read_text(encoding="utf-8"))
case = next(x for x in payload["cases"] if x["id"] == "R002E-S01-material-profile-selected")
case["observations"][proxy_field] = enabled
case["expected"] = expected
path.write_text(json.dumps(payload), encoding="utf-8")
PY
  bash scripts/check-action-selection-contract.sh --repo-root "$tmp_root" \
    >/dev/null 2>&1 || fail "false proxy counterfactual failed for $proxy_field"
  "${py_cmd[@]}" - \
    "$tmp_root/fixtures/audit-action-selection/security-profile-cases.json" \
    "$proxy_field" true "$rejected_outcome" <<'PY'
import json, pathlib, sys
path = pathlib.Path(sys.argv[1])
proxy_field, enabled, expected = sys.argv[2], sys.argv[3] == "true", sys.argv[4]
payload = json.loads(path.read_text(encoding="utf-8"))
case = next(x for x in payload["cases"] if x["id"] == "R002E-S01-material-profile-selected")
case["observations"][proxy_field] = enabled
case["expected"] = expected
path.write_text(json.dumps(payload), encoding="utf-8")
PY
  bash scripts/check-action-selection-contract.sh --repo-root "$tmp_root" \
    >/dev/null 2>&1 || fail "true proxy counterfactual failed for $proxy_field"
done <<'EOF'
authentication_as_authorization|REJECT_AUTHENTICATION_PROXY
availability_as_trust|REJECT_AVAILABILITY_PROXY
label_or_instrument_as_whole_system_proof|REJECT_WHOLE_SYSTEM_PROXY
EOF

printf 'action-selection-contract.test: ok\n'
