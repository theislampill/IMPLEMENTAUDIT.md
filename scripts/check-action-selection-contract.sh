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
  "plan-quality defect" \
  "### Verifier-plan selection" \
  "authoritative changed semantic owners and effects" \
  "equivalent-protection evidence and current owner authority" \
  "generated, transitive runtime, package, or public/external" \
  "Unknown owner or relation, a changed registry, package or release ambiguity" \
  "Do not select full" \
  "verification from diff size, a fixed command count, or a generic review mandate"
do
  require "$depth_ref" "$text"
done

plan_lifecycle="skills/implementaudit/references/plan-lifecycle.md"
for text in \
  "keep the planning and" \
  "adjudication role non-mutating" \
  "Select among valid executor routes by sufficient capability first, then by" \
  "explicit context capsule across agent and worktree" \
  "reviewer rereads fresh live source" \
  "Handoff completeness is determined by the receiving continuation" \
  "cannot claim READY" \
  "Optional ancillary files remain out of scope"
do
  require "$plan_lifecycle" "$text"
done

child_ref="skills/implementaudit/references/child-agents.md"
for text in \
  "Independence is evidential" \
  "resist the same common cause" \
  "current access, competence, time, control" \
  "Maintain a ready-cell frontier" \
  "### Work-conserving ready-cell frontier" \
  "operator-supplied ceiling" \
  "shared write/acceptance/resource authority" \
  "Before dispatch, expose" \
  "DONE + ACTIVE + READY + BLOCKED = population" \
  "capacity = 0 at ceiling 0, host if absent, else min(host, ceiling)" \
  "free = max(0, capacity - ACTIVE)" \
  "dispatch = min(READY, free)" \
  "Use deterministic tooling, not model estimates" \
  "An unchanged reminder or status" \
  "Missing context stops the lane"
do
  require "$child_ref" "$text"
done

# --- engineering-value admission and retirement contract (#163 / R0022) ---
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
  "conditional planner/executor separation" \
  "least-cost" \
  "sufficiently capable route" \
  "work-conserving ready-cell" \
  "operator-supplied ceiling" \
  "stopping, retirement, or reclassification condition" \
  "coordination/peak-attention burden" \
  "nominal override or" \
  "degraded envelope is bounded and observable" \
  "authorised safe stop and no material trigger" \
  'bounded control `CHEAP_PATH`' \
  'material proposal is `BLOCK`' \
  "serial cheap path" \
  "No activation factor means no R0022 diagnostic or artefact" \
  "actual dependency, write," \
  "acceptance, resource, authority, and composed-only boundaries" \
  'ready-cell frontier in `child-agents.md`'
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
  "Known independence is not activation" \
  "Reconsider the ready frontier after a" \
  "not a concurrency or utilisation" \
  "mandatory control ledger" \
  "large worksheet"
do
  require "$lean_ref" "$text"
done

child_ref="skills/implementaudit/references/child-agents.md"
for text in \
  "### Work-conserving ready-cell frontier" \
  "Maintain a ready-cell frontier" \
  "Classify cells as ready, waiting on a named" \
  "At initial dispatch, execute worthwhile ready cells" \
  "Recompute after a material scheduling transition" \
  "An unchanged reminder or status" \
  "Partition each governed cell once" \
  "Unknown," \
  "state prevents dispatch" \
  "Completion" \
  "never infer other ACTIVE=0" \
  "Use the serial cheap path" \
  "ready-queue artefact" \
  "minimum agent count" \
  "dashboard"
do
  require "$child_ref" "$text"
done

skill_ref="skills/implementaudit/SKILL.md"
for text in \
  "For scheduling/dispatch/resource ceilings, read" \
  "reacquire a closed DONE/ACTIVE/READY/BLOCKED census" \
  "dispatch min(READY,capacity-ACTIVE)" \
  "serialise" \
  "references/child-agents.md"
do
  require "$skill_ref" "$text"
done

# --- conditional native security profile (R002E) ---
security_ref="skills/implementaudit/references/audit-playbook.md"
for text in \
  "### Conditional systems-security profile" \
  "protected consequence and unacceptable state" \
  "bounded adversary and explicit exclusions" \
  "trust/identity boundary and authority/privilege boundary" \
  "configuration, dependency, build, artifact, and deployment" \
  "provenance; stale or missing identity" \
  "assurance evidence and its limits" \
  "detection, containment, revocation, recovery, and trust re-establishment" \
  "Authentication is not authorization" \
  "restored availability is not restored trust" \
  "whole-system security proof" \
  "domain and effectiveness claims remain" \
  "unverified until their required representative context exists"
do
  require "$security_ref" "$text"
done

for text in \
  "### Conditional systems-security selection" \
  "material protected consequence" \
  "or untrusted capability" \
  "changed trust, privilege, or delegation boundary" \
  "Low-exposure reversible work inside a current proven envelope" \
  "separate security mode, workflow, or planning artifact"
do
  require "$depth_ref" "$text"
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
        (102, "authority-boundary-conflict-serialises"),
        (103, "ready-frontier-activates"),
        (104, "completion-recomputes-frontier"),
        (105, "block-recomputes-frontier"),
        (106, "resource-conflict-serialises"),
        (107, "unknown-independence-defers"),
        (108, "trivial-serial-cheap-path"),
        (109, "operator-ceiling-bounds-frontier"),
        (110, "no-ceiling-uses-safe-capacity"),
        (111, "zero-ceiling-serial-cheap-path"),
        (112, "reminder-does-not-redispatch"),
        (113, "authorization-change-reconciles"),
        (114, "full-capacity-still-recomputes"),
        (115, "triggered-planner-executor-separation"),
        (116, "ordinary-same-root-cheap-path"),
        (117, "trigger-without-independent-route"),
        (118, "hidden-context-stops-delegation"),
        (119, "least-cost-sufficient-executor"),
        (120, "cheaper-incapable-route-rejected"),
        (121, "single-valid-executor"),
        (122, "privacy-excludes-cheaper-route"),
        (123, "insufficient-delegated-capability-escalates"),
        (124, "high-consequence-separates"),
        (125, "same-root-does-not-require-transfer-capsule"),
        (126, "open-authority-boundary-defers"),
        (127, "small-drift-still-reconciles"),
        (128, "zero-ceiling-authorization-change-reconciles"),
        (129, "serial-capacity-change-recomputes"),
        (130, "zero-ceiling-completion-recomputes-without-activation"),
        (131, "completion-frees-one-bounded-slot"),
        (132, "closed-population-bounds-three-slots"),
        (133, "ready-population-bounds-one-dispatch"),
        (134, "unknown-population-refuses-capacity-assumption"),
        (135, "stale-population-refuses-dispatch"),
    )
}
required_ids.update({
    "R31-C136-grounded-executor-plan-ready",
    "R31-C137-uninspected-plan-held",
    "R34-C138-joint-cognitive-burden-trigger",
    "R34-C139-immediate-effect-cheap-path",
    "R34-C140-capable-intervention-chain",
    "R34-C141-nominal-override-rejected",
    "R44-C142-high-consequence-control-trigger",
    "R44-C143-low-consequence-cheap-path",
    "R44-C144-bounded-degraded-operation",
    "R44-C145-risk-matrix-insufficient",
    "R34-C146-safe-stop-control-cheap-path",
})
ids = [case.get("id") for case in cases if isinstance(case, dict)]
if len(ids) != len(set(ids)) or set(ids) != required_ids:
    raise SystemExit("engineering-value fixture population is incomplete or duplicated")

dogfood_path = path.with_name("dominance-dogfood-receipt.json")
try:
    dogfood = json.loads(dogfood_path.read_text(encoding="utf-8"))
except (OSError, UnicodeError, json.JSONDecodeError) as exc:
    raise SystemExit(f"dominance dogfood receipt unreadable: {exc}")
if set(dogfood) != {
        "schema_version", "kind", "source_population", "candidate_package",
        "disposable_repository", "activation_prompt_leakage", "subagents_used",
        "cells", "evidence_boundary"}:
    raise SystemExit("dominance dogfood receipt schema")
if (dogfood["schema_version"] != 1
        or dogfood["kind"] != "implementaudit-improve-dominance-cross-repository-dogfood"
        or dogfood["activation_prompt_leakage"] is not False
        or dogfood["subagents_used"] is not False
        or dogfood["disposable_repository"].get("dirty_after") is not False):
    raise SystemExit("dominance dogfood receipt identity or hygiene")
dog_ids = [cell.get("id") for cell in dogfood["cells"]]
if dog_ids != [
        "DOG-C01-ready-frontier", "DOG-C02-conditional-separation",
        "DOG-C03-capability-fit", "DOG-C04-context-capsule-boundary",
        "DOG-C05-source-revalidation", "DOG-C06-cold-executor-reconstruction",
        "DOG-R01-combined-cell-timeout"]:
    raise SystemExit("dominance dogfood receipt population")
if [cell["disposition"] for cell in dogfood["cells"]] != [
        "PASS", "PASS", "PASS", "PASS", "PASS_WITH_TEST_EXECUTION_BLOCKED",
        "PASS", "REJECTED_NON_VERDICT"]:
    raise SystemExit("dominance dogfood receipt dispositions")

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
        fields = "event work_units host_capacity operator_ceiling active_cells ready_cells parallelism_allowed cell_independence_known closed_write_boundaries closed_acceptance_boundaries closed_resource_boundaries irreversible_external authorization_current closed_authority_boundaries authority_boundary_open"
        exact(o, fields)
        booleans(o, "parallelism_allowed cell_independence_known closed_write_boundaries closed_acceptance_boundaries closed_resource_boundaries irreversible_external authorization_current closed_authority_boundaries authority_boundary_open")
        if type(o["event"]) is not str or o["event"] not in {
                "initial", "cell_complete", "cell_blocked", "drift",
                "authorization_change", "capacity_change", "unchanged_reminder"}:
            raise ValueError("scheduling event")
        for name in ("work_units", "host_capacity", "operator_ceiling", "active_cells", "ready_cells"):
            if type(o[name]) is not int:
                raise ValueError(f"scheduling {name}")
        if (o["work_units"] < 1 or o["host_capacity"] < 1
                or o["operator_ceiling"] < -1 or o["active_cells"] < 0
                or o["ready_cells"] < 0
                or o["active_cells"] > o["host_capacity"]
                or o["active_cells"] + o["ready_cells"] > o["work_units"]):
            raise ValueError("scheduling population or capacity")
        if (o["event"] in {"drift", "authorization_change"}
                or not o["authorization_current"]):
            return "RECONCILE_FRONTIER"
        if o["event"] == "unchanged_reminder":
            return "NO_REDISPATCH"
        if o["authority_boundary_open"]:
            if o["closed_authority_boundaries"]:
                raise ValueError("authority boundary cannot be open and closed")
            return "DEFER_AUTHORITY_OPEN"
        if not o["cell_independence_known"]:
            return "DEFER_INDEPENDENCE_UNKNOWN"
        if (not all((o["closed_write_boundaries"],
                     o["closed_acceptance_boundaries"],
                     o["closed_resource_boundaries"],
                     o["closed_authority_boundaries"]))
                or o["irreversible_external"]):
            return "SERIALISE_CONFLICT"
        effective_capacity = (
            0 if o["operator_ceiling"] == 0
            else min(
                o["host_capacity"],
                o["operator_ceiling"] if o["operator_ceiling"] > 0
                else o["host_capacity"],
            )
        )
        capacity_available = o["active_cells"] < effective_capacity
        activatable = capacity_available and o["ready_cells"] > 0
        if o["event"] in {"cell_complete", "cell_blocked", "capacity_change"}:
            return "RECOMPUTE_AND_ACTIVATE" if activatable else "RECOMPUTE_FRONTIER"
        if (o["operator_ceiling"] == 0 or o["work_units"] < 3
                or effective_capacity < 2 or not o["parallelism_allowed"]):
            return "SERIAL_CHEAP_PATH"
        if activatable and o["operator_ceiling"] > 0:
            return "ACTIVATE_BOUNDED"
        return "ACTIVATE_READY_CELLS" if activatable else "HOLD_FRONTIER"
    if kind == "frontier_accounting":
        fields = "work_units done_cells active_cells ready_cells blocked_cells unknown_cells host_capacity operator_ceiling state_evidence_current dependencies_current"
        exact(o, fields)
        booleans(o, "state_evidence_current dependencies_current")
        for name in "work_units done_cells active_cells ready_cells blocked_cells unknown_cells host_capacity operator_ceiling".split():
            if type(o[name]) is not int:
                raise ValueError(f"frontier accounting {name}")
        if (o["work_units"] < 1 or o["host_capacity"] < 1
                or o["operator_ceiling"] < -1
                or any(o[name] < 0 for name in (
                    "done_cells", "active_cells", "ready_cells",
                    "blocked_cells", "unknown_cells"))
                or sum(o[name] for name in (
                    "done_cells", "active_cells", "ready_cells",
                    "blocked_cells", "unknown_cells"))
                    != o["work_units"]):
            raise ValueError("frontier accounting population")
        if o["unknown_cells"] or not o["state_evidence_current"]:
            return "REACQUIRE_OR_SERIALISE"
        if not o["dependencies_current"]:
            return "HOLD_DEPENDENCY"
        effective_capacity = (
            0 if o["operator_ceiling"] == 0
            else min(o["host_capacity"], o["operator_ceiling"])
            if o["operator_ceiling"] > 0 else o["host_capacity"]
        )
        dispatch = min(o["ready_cells"], max(0, effective_capacity - o["active_cells"]))
        suffix = "READY_CELL" if dispatch == 1 else "READY_CELLS"
        return f"DISPATCH_{dispatch}_{suffix}"
    if kind == "executor_plan_grounding":
        fields = "live_source_inspected current_state_exact scope_exact edits_exact verification_exact stop_conditions_present rollback_present non_scope_present"
        exact(o, fields)
        booleans(o, fields)
        if not o["live_source_inspected"]:
            return "HOLD_FOR_SOURCE_GROUNDING"
        if not all(o[name] for name in (
                "current_state_exact", "scope_exact", "edits_exact",
                "verification_exact", "stop_conditions_present",
                "rollback_present", "non_scope_present")):
            return "HOLD_INCOMPLETE_EXECUTOR_PLAN"
        return "EXECUTOR_PLAN_READY"
    if kind == "consequence_control":
        fields = "live_pressure low_consequence_reversible direct_readback coordination_or_attention_burden information_value_remaining capable_intervention_chain nominal_override_only high_consequence target_state feedback containment recovery stopping_hazardous bounded_degraded_operation method_only"
        exact(o, fields)
        booleans(o, fields)
        if o["method_only"]:
            return "REJECT"
        if o["nominal_override_only"] or not o["capable_intervention_chain"]:
            return "STOP_AND_ESCALATE"
        complete = all(o[name] for name in ("target_state", "feedback", "containment", "recovery"))
        no_material_trigger = not any(o[name] for name in (
            "live_pressure", "high_consequence", "coordination_or_attention_burden",
            "information_value_remaining", "bounded_degraded_operation"))
        if complete and o["capable_intervention_chain"] and not o["stopping_hazardous"] and no_material_trigger:
            return "CHEAP_PATH"
        if o["low_consequence_reversible"] and o["direct_readback"] and not o["high_consequence"]:
            return "SERIAL_CHEAP_PATH"
        if o["high_consequence"]:
            if not complete:
                return "DEFER"
            if o["stopping_hazardous"]:
                return "BOUNDED_DEGRADED_OPERATION" if o["bounded_degraded_operation"] else "DEFER"
            return "SELECT_CONSEQUENCE_CONTROL"
        if o["coordination_or_attention_burden"]:
            return "SELECT_PROPORTIONATE_CONTROL" if o["live_pressure"] and o["information_value_remaining"] else "NO_R34_ARTEFACT"
        return "CAPABLE_INTERVENTION" if o["live_pressure"] else "NO_R34_ARTEFACT"
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
    if kind == "delegation":
        fields = "ordinary_direct material_judgement self_confirmation_risk contested_interpretation high_consequence independent_executor_available independent_reviewer_available context_complete multiple_valid_executors lower_cost_executor_sufficient privacy_allows_lower_cost delegated_capability_insufficient"
        exact(o, fields)
        booleans(o, fields)
        separation_needed = o["material_judgement"] and any((
            o["self_confirmation_risk"],
            o["contested_interpretation"],
            o["high_consequence"],
        ))
        if separation_needed:
            if not o["context_complete"]:
                return "STOP_RECONSTRUCT_CONTEXT"
            if o["delegated_capability_insufficient"]:
                return "STOP_AND_ESCALATE"
            if not all((o["independent_executor_available"], o["independent_reviewer_available"])):
                return "BLOCK_OR_OWNER_DECISION"
            return "SEPARATE_EXECUTOR"
        if o["ordinary_direct"]:
            return "SAME_ROOT"
        if not o["context_complete"]:
            return "STOP_RECONSTRUCT_CONTEXT"
        if o["delegated_capability_insufficient"]:
            return "STOP_AND_ESCALATE"
        if o["multiple_valid_executors"]:
            if o["lower_cost_executor_sufficient"] and o["privacy_allows_lower_cost"]:
                return "DELEGATE_LEAST_COST_SUFFICIENT"
            return "RETAIN_CAPABLE_ROUTE"
        return "DIRECT_CAPABLE_ROUTE"
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

verifier_path = Path("fixtures/audit-action-selection/verifier-plan-cases.json")
try:
    verifier_payload = json.loads(verifier_path.read_text(encoding="utf-8"))
except (OSError, UnicodeError, json.JSONDecodeError) as exc:
    raise SystemExit(f"verifier-plan fixture unreadable: {exc}")
if set(verifier_payload) != {"schema_version", "kind", "cases"}:
    raise SystemExit("verifier-plan fixture schema")
if verifier_payload["schema_version"] != 1 or verifier_payload["kind"] != "r0022-verifier-plan-selection":
    raise SystemExit("verifier-plan fixture identity")
verifier_cases = verifier_payload["cases"]
required_verifier_ids = {
    "R0022-V01-owner-omitted-under-scoped",
    "R0022-V02-consumer-omitted-under-scoped",
    "R0022-V03-effect-omitted-under-scoped",
    "R0022-V04-trivial-local-cheap-path",
    "R0022-V05-docs-only-verifier-plan",
    "R0022-V06-generated-consumer-verifier-plan",
    "R0022-V07-transitive-consumer-verifier-plan",
    "R0022-V08-package-consumer-verifier-plan",
    "R0022-V09-public-consumer-verifier-plan",
    "R0022-V10-external-consumer-verifier-plan",
    "R0022-V11-unknown-relation-only-escalates",
    "R0022-V12-registry-change-only-escalates",
    "R0022-V13-package-or-release-ambiguity-only-escalates",
    "R0022-V14-stale-projection-only-escalates",
    "R0022-V15-generated-package-composed-verifier-plan",
}
verifier_ids = [case.get("id") for case in verifier_cases if isinstance(case, dict)]
if len(verifier_ids) != len(set(verifier_ids)) or set(verifier_ids) != required_verifier_ids:
    raise SystemExit("verifier-plan fixture population is incomplete or duplicated")

def decide_verifier_plan(observations):
    fields = "change_identity semantic_owner effect consumer evidence_layer residual_risk rollback omission_equivalent_protection omission_owner_current generated_impact package_impact public_or_external_impact registry_changed package_or_release_ambiguous stale_projection unknown_owner_or_relation transitive_consumer local_reversible"
    exact(observations, fields)
    booleans(observations, fields)
    plan_complete = all((
        observations["change_identity"], observations["semantic_owner"],
        observations["effect"], observations["consumer"],
        observations["evidence_layer"], observations["residual_risk"],
        observations["rollback"], observations["omission_equivalent_protection"],
        observations["omission_owner_current"],
    ))
    if (not plan_complete or observations["unknown_owner_or_relation"]
            or observations["registry_changed"]
            or observations["package_or_release_ambiguous"]
            or observations["stale_projection"]):
        return "ESCALATE_CONSERVATIVELY"
    impact_count = sum((
        observations["generated_impact"], observations["transitive_consumer"],
        observations["package_impact"], observations["public_or_external_impact"],
    ))
    if impact_count > 1:
        return "VERIFY_COMPOSED_AFFECTED_CONSUMERS"
    if observations["generated_impact"]:
        return "VERIFY_SOURCE_AND_GENERATED_CONSUMER"
    if observations["transitive_consumer"]:
        return "VERIFY_TRANSITIVE_CONSUMER"
    if observations["package_impact"]:
        return "VERIFY_PACKAGE_CONSUMER"
    if observations["public_or_external_impact"]:
        return "VERIFY_PUBLIC_OR_EXTERNAL_CONSUMER"
    return "SERIAL_CHEAP_PATH" if observations["local_reversible"] else "VERIFY_AFFECTED_OWNER"

verifier_failures = []
for case in verifier_cases:
    try:
        if set(case) != {"id", "observations", "expected"}:
            raise ValueError("case members")
        if not isinstance(case["observations"], dict) or not all(type(value) is bool for value in case["observations"].values()):
            raise ValueError("observation types")
        actual = decide_verifier_plan(case["observations"])
        if actual != case["expected"]:
            verifier_failures.append(f"{case['id']}: expected {case['expected']}, observed {actual}")
    except (KeyError, TypeError, ValueError) as exc:
        verifier_failures.append(f"{case.get('id', '<unknown>')}: invalid fixture: {exc}")
if verifier_failures:
    raise SystemExit("\n".join(verifier_failures))
sys.stdout.write(f"verifier-plan controls: {len(verifier_cases)}/{len(verifier_cases)}\n")

security_path = Path("fixtures/audit-action-selection/security-profile-cases.json")
try:
    security_payload = json.loads(security_path.read_text(encoding="utf-8"))
except (OSError, UnicodeError, json.JSONDecodeError) as exc:
    raise SystemExit(f"security-profile fixture unreadable: {exc}")
if set(security_payload) != {
        "schema_version", "kind", "proof_layer_partition",
        "domain_effectiveness_status", "cases"}:
    raise SystemExit("security-profile fixture schema")
if (security_payload["schema_version"] != 1
        or security_payload["kind"] != "conditional-native-security-profile"):
    raise SystemExit("security-profile fixture identity")
expected_partition = {
    "source_static": 31,
    "deterministic_fixture": 18,
    "package_provenance_reachability": 4,
    "external_domain_unverified": 6,
    "bounded_behavioural_deferred": 1,
}
if security_payload["proof_layer_partition"] != expected_partition:
    raise SystemExit("security-profile proof-layer partition")
if security_payload["domain_effectiveness_status"] != "UNVERIFIED":
    raise SystemExit("security-profile domain/effectiveness boundary")
security_cases = security_payload["cases"]
required_security_ids = {
    "R002E-S01-material-profile-selected",
    "R002E-S02-low-exposure-cheap-path",
    "R002E-S03-stale-provenance-blocked",
    "R002E-S04-authentication-is-not-authorization",
    "R002E-S05-availability-is-not-trust-restoration",
    "R002E-S06-label-only-proof-rejected",
    "R002E-S07-no-trigger-no-profile",
    "R002E-S08-unbounded-adversary-held",
}
security_ids = [case.get("id") for case in security_cases if isinstance(case, dict)]
if len(security_ids) != len(set(security_ids)) or set(security_ids) != required_security_ids:
    raise SystemExit("security-profile fixture population is incomplete or duplicated")

security_fields = """material_protected_consequence exposed_or_untrusted_capability
trust_or_privilege_boundary_change consequential_security_authority
provenance_dependent_claim adaptive_or_common_mode_risk weak_detection_or_recovery
consequential_security_privacy_safety_availability_usability_decision low_exposure
reversible inside_current_proven_envelope protected_consequence_named
unacceptable_state_named adversary_bounded exclusions_explicit trust_identity_boundary
authority_privilege_boundary provenance_current assurance_limits
detection_containment_revocation recovery trust_reestablishment
plausible_abuse_or_trust_check current_identity rollback authentication_as_authorization
availability_as_trust label_or_instrument_as_whole_system_proof""".split()
security_trigger_fields = security_fields[:8]
full_profile_fields = """protected_consequence_named unacceptable_state_named
adversary_bounded exclusions_explicit trust_identity_boundary authority_privilege_boundary
provenance_current assurance_limits detection_containment_revocation recovery
trust_reestablishment""".split()

def decide_security_profile(observations):
    exact(observations, " ".join(security_fields))
    booleans(observations, " ".join(security_fields))
    triggered = any(observations[name] for name in security_trigger_fields)
    if triggered:
        if not observations["provenance_current"]:
            return "BLOCK_STALE_PROVENANCE"
        if observations["authentication_as_authorization"]:
            return "REJECT_AUTHENTICATION_PROXY"
        if observations["availability_as_trust"]:
            return "REJECT_AVAILABILITY_PROXY"
        if observations["label_or_instrument_as_whole_system_proof"]:
            return "REJECT_WHOLE_SYSTEM_PROXY"
        if not all(observations[name] for name in full_profile_fields):
            return "HOLD_INCOMPLETE_PROFILE"
        return "SELECT_NATIVE_SECURITY_PROFILE"
    cheap_path = all(observations[name] for name in (
        "low_exposure", "reversible", "inside_current_proven_envelope"))
    if cheap_path:
        cheap_complete = all(observations[name] for name in (
            "protected_consequence_named", "plausible_abuse_or_trust_check",
            "current_identity", "rollback"))
        return "SECURITY_CHEAP_PATH" if cheap_complete else "HOLD_INCOMPLETE_CHEAP_PATH"
    return "NO_SECURITY_PROFILE"

security_failures = []
for case in security_cases:
    try:
        if set(case) != {"id", "observations", "expected"}:
            raise ValueError("case members")
        if (not isinstance(case["observations"], dict)
                or not all(type(value) is bool for value in case["observations"].values())):
            raise ValueError("observation types")
        actual = decide_security_profile(case["observations"])
        if actual != case["expected"]:
            security_failures.append(
                f"{case['id']}: expected {case['expected']}, observed {actual}")
    except (KeyError, TypeError, ValueError) as exc:
        security_failures.append(f"{case.get('id', '<unknown>')}: invalid fixture: {exc}")
if security_failures:
    raise SystemExit("\n".join(security_failures))
sys.stdout.write(f"security-profile controls: {len(security_cases)}/{len(security_cases)}\n")
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
