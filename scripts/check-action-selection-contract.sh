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
  "consumer existence and authoritative consumer" \
  "cheapest sufficient discriminator" \
  "No retain, admit, or owner-decision disposition" \
  "Protective slack or a buffer is not waste" \
  "Feedback value depends on actionable" \
  "Temporary option value is retained" \
  "No universal rule makes shorter feedback" \
  "higher utilisation, more slack, or less slack correct" \
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
  "Protective slack, sustainable capacity, feedback cadence, temporary options" \
  "carrying cost and its exit condition remains current" \
  "Retain" \
  "Cheapen" \
  "Merge" \
  "conditional" \
  "Retire" \
  "Reclassify" \
  "Defer" \
  "Unresolved" \
  "Disposition labels never self-authorise" \
  "expected-risk and permanent-cost trade-off" \
  "exact bytes, other relevant state" \
  "Without a prior exact PASS, run qualification" \
  "changed scope or consumer requires a fresh run" \
  "no shared owner or shared write remains parallel-safe" \
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
        (30, "missing-authoritative-owner"), (31, "missing-consumer"),
        (32, "missing-consequence"), (33, "missing-discriminator"),
        (34, "missing-expected-evidence"), (35, "missing-marginal-cost"),
        (36, "missing-exit-condition"), (37, "changed-scope-rerun"),
        (38, "changed-consumer-rerun"), (39, "invalid-retain"),
        (40, "invalid-merge"), (41, "invalid-conditionalise"),
        (42, "cheapen-equivalent-control"), (43, "explicit-defer"),
        (44, "unresolved-tradeoff"), (45, "disjoint-cells-no-shared-cell"),
        (46, "owner-decision"), (47, "valid-retain"),
        (48, "invalid-cheapen"),
        (49, "defer-with-complete-mutation"),
        (50, "defer-without-controlling-gate"),
        (51, "unresolved-single-alternative"),
        (52, "unresolved-distinguishable-alternatives"),
        (53, "owner-decision-mechanically-resolvable"),
        (54, "owner-decision-without-risk-tradeoff"),
        (55, "held-out-defer-adjacent"),
        (56, "held-out-unresolved-adjacent"),
        (57, "held-out-owner-decision-adjacent"),
        (58, "non-authoritative-consumer"),
        (59, "changed-authoritative-consumer-rerun"),
        (60, "changed-bytes-rerun"),
        (61, "required-gate-without-live-driver"),
        (62, "retain-with-cheaper-equivalent"),
        (63, "reuse-without-prior-exact-pass"),
        (64, "required-gate-missing-authoritative-consumer"),
        (65, "nonrequired-without-live-driver"),
        (66, "required-complete-live-driver"),
        (67, "retain-equivalent-without-lower-cost"),
        (68, "retain-lower-cost-without-equivalence"),
        (69, "unqualified-changed-bytes"),
        (70, "process-heavy-derives-activation"),
        (71, "parallel-safe-without-reconciliation"),
        (72, "proportionality-cheap-path"),
        (73, "protective-buffer"),
        (74, "buffer-without-variability"),
        (75, "actionable-feedback"),
        (76, "feedback-without-actionability"),
        (77, "sustainable-recovery-capacity"),
        (78, "maximum-utilisation"),
        (79, "bounded-option-value"),
        (80, "option-carrying-cost-dominates"),
        (81, "indefinite-option"),
        (82, "hard-to-reverse-control-depth"),
        (83, "fixed-wip-rule"),
        (84, "methodology-ceremony"),
        (85, "missing-proportional-consumer"),
        (86, "ready-capacity-activates"),
        (87, "completion-recomputes-frontier"),
        (88, "blocked-cell-recomputes-frontier"),
        (89, "full-capacity-still-recomputes"),
        (90, "drift-reconciles-frontier"),
        (91, "authorization-change-reconciles-frontier"),
        (92, "unknown-independence-defers"),
        (93, "write-conflict-serialises"),
        (94, "acceptance-conflict-serialises"),
        (95, "resource-claim-conflict-serialises"),
        (96, "irreversible-external-serialises"),
        (97, "host-capacity-one-cheap-serial"),
        (98, "two-unit-cheap-serial"),
        (99, "reminder-does-not-redispatch"),
        (100, "capacity-change-recomputes-frontier"),
        (101, "parallelism-unavailable-cheap-serial"),
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
        derived_activation = o["activation"] or o["process_heavy_or_disputed"]
        if not derived_activation:
            return "NO_R34_ARTEFACT"
        return "DEEP_RETROSPECTIVE" if o["process_heavy_or_disputed"] else "MINIMAL_TRIGGERED_RECORD"
    if kind == "admission":
        fields = "required_gate equivalent_protection live_driver authoritative_owner consumer authoritative_consumer consequence discriminator expected_evidence marginal_cost_recorded exit_condition proxy_only optional_by_whim expected_risk_material"
        exact(o, fields)
        booleans(o, fields)
        complete = all((
            o["authoritative_owner"], o["consumer"],
            o["authoritative_consumer"], o["consequence"],
            o["discriminator"], o["expected_evidence"],
            o["marginal_cost_recorded"], o["exit_condition"],
        ))
        if o["required_gate"] and not o["equivalent_protection"]:
            return "RETAIN" if o["live_driver"] and complete else "DEFER"
        if o["proxy_only"] or o["optional_by_whim"] or not o["live_driver"]:
            return "REJECT"
        if not complete:
            return "DEFER"
        if o["expected_risk_material"]:
            return "RETAIN"
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
        fields = "prior_exact_pass exact_bytes_unchanged other_relevant_state_unchanged scope_identical consumer_identical authoritative_consumer_identical new_residual new_mutation_family"
        exact(o, fields)
        booleans(o, fields)
        if not o["prior_exact_pass"]:
            return "RUN"
        if (o["new_residual"] or o["new_mutation_family"]
                or not o["exact_bytes_unchanged"]
                or not o["other_relevant_state_unchanged"]
                or not o["scope_identical"]
                or not o["consumer_identical"]
                or not o["authoritative_consumer_identical"]):
            return "RUN"
        if all((o["prior_exact_pass"], o["scope_identical"],
                o["consumer_identical"], o["authoritative_consumer_identical"])):
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
        if o["shared_cell"] and not o["shared_owner"]:
            return "FAIL"
        if o["parallel_shared_cell"] or o["shared_cell"] and not o["closed_write_boundaries"]:
            return "FAIL"
        if o["shared_owner"] and o["shared_cell"] and o["disjoint_cells"] and o["reconciliation_point"]:
            return "PARALLEL_DISJOINT_SERIALISE_SHARED"
        if (not o["shared_cell"] and o["disjoint_cells"]
                and o["closed_write_boundaries"] and o["reconciliation_point"]):
            return "PARALLEL_SAFE"
        return "SERIALISE_SHARED"
    if kind == "scheduling":
        fields = "event work_units host_capacity active_cells ready_cells parallelism_allowed cell_independence_known closed_write_boundaries closed_acceptance_boundaries closed_resource_boundaries irreversible_external authorization_current"
        exact(o, fields)
        booleans(o, "parallelism_allowed cell_independence_known closed_write_boundaries closed_acceptance_boundaries closed_resource_boundaries irreversible_external authorization_current")
        if type(o["event"]) is not str or o["event"] not in {
                "initial", "cell_complete", "cell_blocked", "drift",
                "authorization_change", "capacity_change", "unchanged_reminder"}:
            raise ValueError("scheduling event")
        for name in ("work_units", "host_capacity", "active_cells", "ready_cells"):
            if type(o[name]) is not int or o[name] < 0:
                raise ValueError(f"scheduling {name}")
        if o["work_units"] < 1 or o["host_capacity"] < 1:
            raise ValueError("scheduling population or capacity")
        if (o["active_cells"] > o["host_capacity"]
                or o["active_cells"] + o["ready_cells"] > o["work_units"]):
            raise ValueError("scheduling frontier counts")
        if (o["work_units"] < 3 or o["host_capacity"] < 2
                or not o["parallelism_allowed"]):
            return "SERIAL_CHEAP_PATH"
        if o["event"] == "unchanged_reminder":
            return "NO_REDISPATCH"
        if (o["event"] in {"drift", "authorization_change"}
                or not o["authorization_current"]):
            return "RECONCILE_FRONTIER"
        if not o["cell_independence_known"]:
            return "DEFER_INDEPENDENCE_UNKNOWN"
        if (not all((o["closed_write_boundaries"],
                     o["closed_acceptance_boundaries"],
                     o["closed_resource_boundaries"]))
                or o["irreversible_external"]):
            return "SERIALISE_CONFLICT"
        capacity_available = o["active_cells"] < o["host_capacity"]
        activatable = capacity_available and o["ready_cells"] > 0
        if o["event"] in {"cell_complete", "cell_blocked", "capacity_change"}:
            return "RECOMPUTE_AND_ACTIVATE" if activatable else "RECOMPUTE_FRONTIER"
        return "ACTIVATE_READY_CELLS" if activatable else "HOLD_FRONTIER"
    if kind == "proportionality":
        fields = "candidate live_pressure variability_or_uncertainty high_consequence_or_hard_to_reverse actionable_information authoritative_consumer protected_consequence benefit_exceeds_carrying_cost bounded exit_condition recovery_capacity_required universal_rule methodology_ceremony"
        exact(o, fields)
        booleans(o, "live_pressure variability_or_uncertainty high_consequence_or_hard_to_reverse actionable_information authoritative_consumer protected_consequence benefit_exceeds_carrying_cost bounded exit_condition recovery_capacity_required universal_rule methodology_ceremony")
        if type(o["candidate"]) is not str or o["candidate"] not in {
                "none", "buffer", "feedback", "capacity", "option", "control_depth"}:
            raise ValueError("proportional candidate")
        if o["universal_rule"] or o["methodology_ceremony"]:
            return "REJECT"
        if o["candidate"] == "none":
            pressures = (
                o["live_pressure"], o["variability_or_uncertainty"],
                o["high_consequence_or_hard_to_reverse"],
                o["recovery_capacity_required"],
            )
            return "DEFER" if any(pressures) else "NO_R34_ARTEFACT"
        if not o["live_pressure"]:
            return "REJECT"
        if not o["bounded"]:
            return "REJECT"
        if not all((o["authoritative_consumer"], o["protected_consequence"], o["exit_condition"])):
            return "DEFER"
        if o["candidate"] == "option" and not o["benefit_exceeds_carrying_cost"]:
            return "RETIRE"
        if not o["benefit_exceeds_carrying_cost"]:
            return "REJECT"
        if o["candidate"] == "buffer":
            valid = o["variability_or_uncertainty"]
        elif o["candidate"] == "feedback":
            valid = o["actionable_information"]
        elif o["candidate"] == "capacity":
            valid = o["recovery_capacity_required"]
        elif o["candidate"] == "option":
            valid = o["variability_or_uncertainty"] and o["actionable_information"]
        else:
            valid = o["high_consequence_or_hard_to_reverse"]
        return "SELECT_PROPORTIONATE_CONTROL" if valid else "REJECT"
    if kind == "escalation":
        fields = "requested mutation_incomplete controlling_gate_intact supported_alternatives alternatives_indistinguishable expected_risk_material permanent_cost_material mechanically_resolvable"
        exact(o, fields)
        booleans(o, "mutation_incomplete controlling_gate_intact alternatives_indistinguishable expected_risk_material permanent_cost_material mechanically_resolvable")
        if type(o["supported_alternatives"]) is not int or o["supported_alternatives"] < 0:
            raise ValueError("supported alternatives")
        if o["requested"] == "defer":
            valid = o["mutation_incomplete"] and o["controlling_gate_intact"]
            return "DEFER" if valid else "FAIL"
        if o["requested"] == "unresolved":
            valid = (o["controlling_gate_intact"]
                     and o["supported_alternatives"] >= 2
                     and o["alternatives_indistinguishable"]
                     and not o["mechanically_resolvable"])
            return "UNRESOLVED" if valid else "FAIL"
        if o["requested"] == "owner_decision":
            valid = (o["controlling_gate_intact"]
                     and o["expected_risk_material"]
                     and o["permanent_cost_material"]
                     and not o["mechanically_resolvable"])
            return "OWNER_DECISION" if valid else "FAIL"
        raise ValueError("requested escalation disposition")
    if kind == "lifecycle":
        exact(o, "requested live_consumer protected_consequence failure_mode_live rollback_proved duplicate_authority activation_conditional risk_or_authority_changed equivalent_protection_proved marginal_cost_reduced record_complete")
        booleans(o, "live_consumer protected_consequence failure_mode_live rollback_proved duplicate_authority activation_conditional risk_or_authority_changed equivalent_protection_proved marginal_cost_reduced record_complete")
        if o["requested"] not in {"retain", "cheapen", "merge", "conditionalise", "retire", "reclassify"}:
            raise ValueError("requested lifecycle disposition")
        if not o["record_complete"]:
            return "DEFER"
        if o["risk_or_authority_changed"]:
            return "RECLASSIFY"
        if o["requested"] == "reclassify":
            return "DEFER"
        if o["requested"] == "retain":
            valid = o["live_consumer"] and o["protected_consequence"] and o["failure_mode_live"]
            if not valid:
                return "DEFER"
            if o["equivalent_protection_proved"] and o["marginal_cost_reduced"]:
                return "CHEAPEN"
            return "RETAIN"
        if o["requested"] == "merge":
            valid = all((o["live_consumer"], o["protected_consequence"], o["duplicate_authority"], o["equivalent_protection_proved"]))
            return "MERGE" if valid else "DEFER"
        if o["requested"] == "conditionalise":
            valid = all((o["live_consumer"], o["protected_consequence"], o["failure_mode_live"], o["activation_conditional"], o["equivalent_protection_proved"]))
            return "CONDITIONAL" if valid else "DEFER"
        if o["requested"] == "cheapen":
            valid = all((o["live_consumer"], o["protected_consequence"], o["equivalent_protection_proved"], o["marginal_cost_reduced"]))
            return "CHEAPEN" if valid else "DEFER"
        if o["requested"] == "retire":
            if o["live_consumer"] or o["protected_consequence"]:
                return "FAIL"
            return "RETIRE" if not o["failure_mode_live"] and o["rollback_proved"] else "DEFER"
        raise ValueError("unhandled lifecycle disposition")
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
sys.stdout.write(f"engineering-value controls: {len(cases)}/{len(cases)}\n")
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
