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
    "$tmp_root/skills/implementaudit/templates" \
    "$tmp_root/fixtures/audit-action-selection" \
    "$tmp_root/fixtures/native-integration" \
    "$tmp_root/fixtures/audit-object-routing"
  cp skills/implementaudit/SKILL.md "$tmp_root/skills/implementaudit/"
  cp skills/implementaudit/references/planning-depth.md \
    "$tmp_root/skills/implementaudit/references/"
  cp skills/implementaudit/references/lean-operating-discipline.md \
    "$tmp_root/skills/implementaudit/references/"
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

printf 'action-selection-contract.test: ok\n'
