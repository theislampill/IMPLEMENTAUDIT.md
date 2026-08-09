#!/usr/bin/env bash
set -euo pipefail

# Action-selection contract gate (#48, IA-ACTION-DEPTH). Ordinary task-shaped
# invocations must derive the warranted ydqyq-audit-action set from the seven
# live factors — scope, uncertainty, risk, dependencies, evidence gaps,
# authorization state, intended executor — record selections AND omissions,
# and never gate depth on an activation keyword.
#
# Usage: check-action-selection-contract.sh [--repo-root <dir>]

fail() {
  printf 'check-action-selection-contract: %s\n' "$*" >&2
  exit 1
}

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [ "${1:-}" = "--repo-root" ]; then
  [ "$#" -ge 2 ] || fail "--repo-root requires a directory argument"
  repo_root="$2"
fi
cd "$repo_root"

require() {
  local file="$1"
  local text="$2"
  [ -f "$file" ] || fail "missing file: $file"
  grep -Fqi -e "$text" "$file" || fail "missing in $file: $text"
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

# --- runtime contract: planning-depth.md owns the contract ---
depth_ref="skills/implementaudit/references/planning-depth.md"
for text in \
  "## Action-selection contract" \
  "Depth never requires an activation keyword" \
  "- scope" \
  "- uncertainty" \
  "- risk" \
  "- dependencies" \
  "- evidence gaps" \
  "- authorization state" \
  "- intended executor" \
  "Selection is recorded, both ways" \
  "considered-but-omitted actions with the reason" \
  "why deeper planning was or was not warranted" \
  "Reference loading follows selection" \
  "request size alone never does" \
  "plan-quality defect"
do
  require "$depth_ref" "$text"
done

# --- engineering-value admission and retirement contract (#163 / R34) ---
for text in \
  "## Engineering-value admission and control lifecycle" \
  "Preserve the gate or engineering obligation where warranted" \
  "authoritative consumer" \
  "cheapest sufficient discriminator" \
  "stopping, retirement, or reclassification condition" \
  "No activation factor means no R34 diagnostic or artefact"
do
  require "$depth_ref" "$text"
done

lean_ref="skills/implementaudit/references/lean-operating-discipline.md"
for text in \
  "## Engineering-value admission, retention, and retirement" \
  "optional-by-whim" \
  "expected-risk" \
  "Retain" \
  "Merge" \
  "conditional" \
  "Retire" \
  "Reclassify" \
  "relevant bytes, state, consumer, and evidence scope" \
  "one shared owner does not serialise disjoint cells" \
  "mandatory control ledger" \
  "large worksheet"
do
  require "$lean_ref" "$text"
done

"${py_cmd[@]}" - "$repo_root/fixtures/audit-action-selection/engineering-value-cases.json" <<'PY'
import json
import sys
from pathlib import Path

path = Path(sys.argv[1])
try:
    payload = json.loads(path.read_text(encoding="utf-8"))
except (OSError, UnicodeError, json.JSONDecodeError) as exc:
    raise SystemExit(f"engineering-value fixture unreadable: {exc}")

if set(payload) != {"schema", "cases"} or payload["schema"] != 1:
    raise SystemExit("engineering-value fixture schema mismatch")
cases = payload["cases"]
if not isinstance(cases, list):
    raise SystemExit("engineering-value cases must be a list")

required_ids = {
    f"R34-C{number:02d}-{suffix}"
    for number, suffix in (
        (1, "tiny-cheap-path"), (2, "triggered-minimal-record"),
        (3, "deep-retrospective-bounded"), (4, "risky-smoke-retained"),
        (5, "habit-only-control"), (6, "optional-by-whim"),
        (7, "commit-count-proxy"), (8, "artefact-count-proxy"),
        (9, "report-count-proxy"), (10, "reviewer-count-proxy"),
        (11, "command-count-proxy"), (12, "recovery-handoff"),
        (13, "duplicate-status-artefact"), (14, "demonstrated-defect-control"),
        (15, "rare-catastrophic-risk"), (16, "exact-evidence-reuse"),
        (17, "changed-state-rerun"), (18, "repeat-review-no-residual"),
        (19, "review-new-mutation-family"), (20, "shared-and-disjoint-topology"),
        (21, "shared-cell-conflict"), (22, "duplicate-controls-merge"),
        (23, "trigger-dependent-control"), (24, "retire-obsolete-control"),
        (25, "reclassify-changed-risk"), (26, "live-consumer-retirement"),
        (27, "mandatory-large-worksheet"), (28, "filled-record-no-consequence"),
        (29, "complete-admission"),
    )
}
ids = [case.get("id") for case in cases if isinstance(case, dict)]
if len(ids) != len(set(ids)) or set(ids) != required_ids:
    raise SystemExit("engineering-value fixture population is incomplete or duplicated")

def exact(observations, names):
    if set(observations) != set(names.split()):
        raise ValueError("observation members")

def booleans(observations, names):
    if any(type(observations[name]) is not bool for name in names.split()):
        raise ValueError("boolean observation type")

def decide(case):
    kind = case["kind"]
    o = case["observations"]
    if kind == "depth":
        exact(o, "activation process_heavy_or_disputed")
        booleans(o, "activation process_heavy_or_disputed")
        if not o["activation"]:
            return "NO_R34_ARTEFACT"
        return "DEEP_RETROSPECTIVE" if o["process_heavy_or_disputed"] else "MINIMAL_TRIGGERED_RECORD"
    if kind == "admission":
        exact(o, "required_gate equivalent_protection live_driver consumer consequence discriminator exit_condition proxy_only optional_by_whim expected_risk_material")
        booleans(o, "required_gate equivalent_protection live_driver consumer consequence discriminator exit_condition proxy_only optional_by_whim expected_risk_material")
        if o["required_gate"] and not o["equivalent_protection"]:
            return "RETAIN"
        if o["expected_risk_material"]:
            return "RETAIN_OR_OWNER_DECISION"
        if o["proxy_only"] or o["optional_by_whim"] or not all((o["live_driver"], o["consumer"], o["consequence"])):
            return "REJECT"
        if not o["discriminator"] or not o["exit_condition"]:
            return "DEFER_OR_OWNER_DECISION"
        return "ADMIT"
    if kind == "anti_gaming":
        exact(o, "proxy large_mandatory_worksheet form_only")
        booleans(o, "large_mandatory_worksheet form_only")
        if type(o["proxy"]) is not str:
            raise ValueError("proxy type")
        if o["proxy"] not in {"none", "commit_count", "artefact_count", "report_count", "reviewer_count", "command_count"}:
            raise ValueError("unknown proxy")
        return "FAIL" if o["proxy"] != "none" or o["large_mandatory_worksheet"] or o["form_only"] else "PASS"
    if kind == "artefact":
        exact(o, "live_consumer recovery_or_authority_consequence duplicate_authority")
        booleans(o, "live_consumer recovery_or_authority_consequence duplicate_authority")
        if o["duplicate_authority"]:
            return "MERGE_OR_RETIRE"
        return "RETAIN" if o["live_consumer"] and o["recovery_or_authority_consequence"] else "RETIRE_OR_DEFER"
    if kind == "repeat":
        exact(o, "prior_exact_pass relevant_state_unchanged scope_identical consumer_identical new_residual new_mutation_family")
        booleans(o, "prior_exact_pass relevant_state_unchanged scope_identical consumer_identical new_residual new_mutation_family")
        if o["new_residual"] or o["new_mutation_family"] or not o["relevant_state_unchanged"]:
            return "RUN"
        if all((o["prior_exact_pass"], o["scope_identical"], o["consumer_identical"])):
            return "REUSE"
        return "STOP"
    if kind == "review":
        exact(o, "new_residual new_mutation_family")
        booleans(o, "new_residual new_mutation_family")
        return "RUN" if o["new_residual"] or o["new_mutation_family"] else "STOP"
    if kind == "topology":
        exact(o, "shared_owner shared_cell disjoint_cells closed_write_boundaries reconciliation_point parallel_shared_cell")
        booleans(o, "shared_owner shared_cell closed_write_boundaries reconciliation_point parallel_shared_cell")
        if type(o["disjoint_cells"]) is not int or o["disjoint_cells"] < 0:
            raise ValueError("disjoint_cells")
        if o["parallel_shared_cell"] or o["shared_cell"] and not o["closed_write_boundaries"]:
            return "FAIL"
        if o["shared_owner"] and o["shared_cell"] and o["disjoint_cells"] and o["reconciliation_point"]:
            return "PARALLEL_DISJOINT_SERIALISE_SHARED"
        return "SERIALISE_SHARED"
    if kind == "lifecycle":
        exact(o, "requested live_consumer failure_mode_live rollback_proved duplicate_authority activation_conditional risk_or_authority_changed")
        booleans(o, "live_consumer failure_mode_live rollback_proved duplicate_authority activation_conditional risk_or_authority_changed")
        if o["requested"] not in {"retain", "merge", "conditionalise", "retire"}:
            raise ValueError("requested lifecycle disposition")
        if o["risk_or_authority_changed"]:
            return "RECLASSIFY"
        if o["requested"] == "retire" and o["live_consumer"]:
            return "FAIL"
        if o["duplicate_authority"]:
            return "MERGE"
        if o["activation_conditional"]:
            return "CONDITIONAL"
        if o["requested"] == "retire" and not o["failure_mode_live"] and o["rollback_proved"]:
            return "RETIRE"
        return "RETAIN"
    raise ValueError("unknown case kind")

failures = []
for case in cases:
    try:
        if set(case) != {"id", "kind", "observations", "expected"}:
            raise ValueError("case members")
        if not isinstance(case["observations"], dict) or not all(type(value) in {bool, int, str} for value in case["observations"].values()):
            raise ValueError("observation types")
        actual = decide(case)
        if actual != case["expected"]:
            failures.append(f"{case['id']}: expected {case['expected']}, observed {actual}")
    except (KeyError, TypeError, ValueError) as exc:
        failures.append(f"{case.get('id', '<unknown>')}: invalid fixture: {exc}")
if failures:
    raise SystemExit("\n".join(failures))
print(f"engineering-value controls: {len(cases)}/{len(cases)}")
PY

# --- bootloader: Stage 1 derives and records the action set ---
skill="skills/implementaudit/SKILL.md"
for text in \
  "Derive the warranted \`ydqyq-audit-action\` set from scope, uncertainty, risk," \
  "record" \
  "action-selection contract" \
  "Depth never requires an activation keyword"
do
  require "$skill" "$text"
done

# --- templates: the record has a home in the audit object ---
thinking="skills/implementaudit/templates/THINKING.md"
for text in \
  "## Action selection" \
  "Selected ydqyq-audit-actions:" \
  "Considered-but-omitted actions (with reasons):" \
  "Why deeper planning was or was not warranted:"
do
  require "$thinking" "$text"
done

roadmap="skills/implementaudit/templates/ROADMAP.md"
for text in \
  "## Action selection" \
  "Depth rationale"
do
  require "$roadmap" "$text"
done

# --- positive fixtures ---
deepens="fixtures/audit-action-selection/ordinary-task-deepens.md"
for text in \
  "no activation keyword" \
  "action-selection record" \
  "phase decomposition" \
  "considered-but-omitted actions with reasons"
do
  require "$deepens" "$text"
done

shallow="fixtures/audit-action-selection/narrow-direct-stays-shallow.md"
for text in \
  "stays direct" \
  "why deeper planning was not warranted" \
  "omitted actions with reasons" \
  "Over-planning"
do
  require "$shallow" "$text"
done

# --- adapted route fixtures carry the contract linkage ---
require "fixtures/native-integration/single-plan-native-route.md" \
  "action-selection record notes why phase decomposition beyond the single"
require "fixtures/audit-object-routing/deep-pressure-disclosure.md" \
  "factor-driven action-selection rationale"

# --- negative fixtures exist and declare their failing disposition ---
for negative in \
  "fixtures/audit-action-selection/negative-keyword-gated-depth.md" \
  "fixtures/audit-action-selection/negative-size-only-deepening.md" \
  "fixtures/audit-action-selection/negative-missing-selection-record.md"
do
  require "$negative" "NEGATIVE FIXTURE"
  require "$negative" "must fail"
  require "$negative" "Expected disposition when reviewed: FAIL"
done

# --- no command-mode advertisement in the new surfaces ---
if grep -R -n -E '/implementaudit (quick|deep|security|next|features|roadmap)' \
  fixtures/audit-action-selection "$depth_ref" \
  | grep -v "Do not advertise" \
  | grep -v "Do not add" \
  >/tmp/implementaudit-action-selection-command-mode-hit.txt; then
  cat /tmp/implementaudit-action-selection-command-mode-hit.txt >&2
  rm -f /tmp/implementaudit-action-selection-command-mode-hit.txt
  fail "command-mode identity advertised in action-selection surfaces"
fi
rm -f /tmp/implementaudit-action-selection-command-mode-hit.txt

printf 'check-action-selection-contract: ok\n'
