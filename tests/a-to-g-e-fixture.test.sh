#!/usr/bin/env bash
set -euo pipefail

fixture="${1:-fixtures/a-to-g/post-compaction-isolation.json}"
mode="${2:-all}"
: "${PYTHON_BIN:?PYTHON_BIN must name the explicit Python 3.11 executable}"

"$PYTHON_BIN" - "$fixture" "$mode" <<'PY'
import copy
import json
import sys

with open(sys.argv[1], encoding="utf-8") as handle:
    data = json.load(handle)

assert sys.argv[2] in {"all", "--whole-episode-only"}, "unknown E fixture selector"


def check_whole_episode_fixture(value):
    # This checks a proposed fixture interface, never an actual episode verdict.
    assert isinstance(value, dict), "whole-episode fixture contract missing"
    assert value.get("evidence_kind") == "PROPOSED_MEASUREMENT", "fixture promoted to actual evidence"
    assert value.get("scope") == "WHOLE_GOVERNOR_EPISODE", "worker-only scope"
    assert value.get("start") == "BEFORE_ATTRIBUTABLE_BOOTSTRAP_DISCOVERY", "bootstrap prefix omitted"
    assert value.get("end") == "AFTER_RETURN_RECONCILIATION_AND_REQUIRED_OWNER_CURRENTNESS_READBACK", "reconciliation tail omitted"
    assert value.get("phases") == ["BOOTSTRAP", "DISCOVERY", "DISPATCH", "EXECUTION", "RETURN", "RECONCILIATION"], "episode phase omitted"
    assert value.get("dimensions") == ["RETAINED_GOVERNOR_CONTEXT", "CONTEXT_COST", "DISPATCH_COST", "EXECUTION_COST", "RECONCILIATION_COST", "REMAINING_CONTINUATION_HEADROOM"], "governor dimension omitted"
    assert value.get("conditional_costs") == {"INSTALLATION": "APPLICABILITY_BASIS_REQUIRED", "MAINTENANCE": "APPLICABILITY_BASIS_REQUIRED"}, "conditional cost applicability missing"
    assert value.get("continuation") == "REUSE_SUFFICIENT_UNCHANGED_MACHINERY_INVESTIGATE_CHANGED_EVIDENCE_OR_DEPENDENCIES", "continuation evidence basis missing"
    assert value.get("worker_pressure") == "NO_ROOT_COMPACTION_WITHOUT_GENUINE_ROOT_EVENT_INVALIDATE_ONLY_AFFECTED_DEPENDENCIES", "worker pressure promoted to root boundary"
    assert value.get("unchanged_sufficient_evidence") == "REUSE_WITHOUT_IDLE_OR_REPEATED_PROCESS_WORK", "unchanged evidence replay required"
    assert value.get("actual_observations", "MISSING") is None, "fixture manufactured actual observations"
    assert value.get("actual_qualification") == "UNQUALIFIED", "fixture granted actual qualification"


whole_episode = data.get("whole_episode_qualification")
check_whole_episode_fixture(whole_episode)
# Each mutation crosses a retained owner discriminator. These are structural
# anti-promotion controls, not telemetry, a host run or an episode evaluator.
negative_controls = [
    ("evidence_kind", "ACTUAL_MEASUREMENT", "fixture promoted to actual evidence"),
    ("scope", "WORKER_PACKET", "worker-only scope"),
    ("start", "AT_DISPATCH", "bootstrap prefix omitted"),
    ("end", "AT_RETURN", "reconciliation tail omitted"),
    ("phases", ["DISCOVERY", "DISPATCH", "EXECUTION", "RETURN", "RECONCILIATION"], "episode phase omitted"),
    ("dimensions", ["RETAINED_GOVERNOR_CONTEXT", "CONTEXT_COST", "DISPATCH_COST", "EXECUTION_COST", "RECONCILIATION_COST"], "governor dimension omitted"),
    ("conditional_costs", {"INSTALLATION": 0, "MAINTENANCE": 0}, "conditional cost applicability missing"),
    ("continuation", "NEVER_INVESTIGATE_CHANGED_EVIDENCE", "continuation evidence basis missing"),
    ("worker_pressure", "INVALIDATE_ROOT_ON_WORKER_PRESSURE", "worker pressure promoted to root boundary"),
    ("unchanged_sufficient_evidence", "REPEAT_FOR_IDLE_TIME", "unchanged evidence replay required"),
    ("actual_observations", {"headroom_sufficient": True}, "fixture manufactured actual observations"),
    ("actual_qualification", "PASS", "fixture granted actual qualification"),
]
for key, replacement, expected in negative_controls:
    changed = copy.deepcopy(whole_episode)
    changed[key] = replacement
    try:
        check_whole_episode_fixture(changed)
    except AssertionError as exc:
        assert str(exc) == expected, (key, str(exc), expected)
    else:
        raise AssertionError(f"whole-episode negative control accepted: {key}")
print("a-to-g-e-whole-episode: structural fixture only (1 positive, 12 negative); actual episode UNQUALIFIED")
if sys.argv[2] == "--whole-episode-only":
    raise SystemExit(0)

# Contract declarations only. Actual pending-owner lifecycle runs in the
# separately registered compact-interlock/pending behavioral suite.
assert data["native_case_scope"] == "NATIVE_AUTHORITATIVE_RECOVERY"
reconciliation = data["post_compaction_reconciliation"]
assert reconciliation["entry"] == "POST_COMPACTION_RECONCILIATION"
assert reconciliation["evidence_kind"] == "PROPOSED_CONTRACT_CASES"
assert reconciliation["actual_host_qualification"] == "UNQUALIFIED"
pc = {case["id"]: case for case in reconciliation["cases"]}
assert len(pc) == len(reconciliation["cases"]) == 14
for key in ("PC_CURRENT", "PC_NOT_CURRENT", "PC_NO_EPOCH", "PC_ACTIVE_SIBLINGS", "PC_HOOK_FALLBACK"):
    assert pc[key]["expected"]["audit_state_required"] is True
assert pc["PC_NOT_CURRENT"]["expected"]["currentness_finding"] == "UNRESOLVED"
assert pc["PC_NO_EPOCH"]["expected"]["epoch_created"] is False
assert pc["PC_ACTIVE_SIBLINGS"]["expected"]["independent_children"] == "UNCHANGED"
assert pc["PC_ACTIVE_SIBLINGS"]["expected"]["new_governor_state_decisions"] == "HELD"
assert pc["PC_RETURN_ONLY"]["expected"]["pending"] is True
assert pc["PC_RETURN_ONLY"]["expected"]["canonical_currentness_granted"] is False
assert pc["PC_SECOND_BOUNDARY"]["expected"]["pending_boundaries"] == ["boundary-b"]
assert pc["PC_SECOND_BOUNDARY"]["expected"]["canonical_currentness_granted"] is False
assert pc["PC_HOOK_FALLBACK"]["expected"]["invented_host_id"] is False
assert pc["PC_DUPLICATE"]["expected"]["logical_pending_count"] == 1
assert pc["PC_DUPLICATE"]["expected"]["dispatch_consumes_pending"] is False
seam_expectations = {
    "PC_STATUS_QUERY": {"pending_mutated": False, "compaction_proved": False},
    "PC_UNPROVED_RESUME": {"audit_state_required": True, "observation": "UNRESOLVED_RESUME_OBSERVATION", "compaction_proved": False, "result_authority": "NONE"},
    "PC_FAILED_A_NEW_B": {"ready_scope": ["boundary-b"], "failed_a_assignment": "RETAINED", "a_dependent_governor_decisions": "HELD"},
    "PC_B_JOIN_PRESERVES_A": {"pending_scope": ["boundary-a"], "a_dependent_governor_decisions": "HELD", "result_authority": "NONE"},
    "PC_FAILED_SCOPE_RETRY": {"disposition": "CONDITIONAL_UNQUALIFIED", "automatic_release": False},
    "PC_CALLER_SUCCESS_ONLY": {"actual_lifecycle_proved": False, "lawful_join": False, "native_dispose_proved": False},
}
def check_seam_declarations(cases):
    for key, expected in seam_expectations.items():
        assert cases[key]["expected"] == expected, "post-compaction seam weakened: " + key

check_seam_declarations(pc)
for key in seam_expectations:
    weakened = copy.deepcopy(pc)
    weakened[key]["expected"] = {}
    try:
        check_seam_declarations(weakened)
    except AssertionError as exc:
        assert str(exc) == "post-compaction seam weakened: " + key
    else:
        raise AssertionError("post-compaction seam mutation accepted: " + key)
print("post-compaction E declarations: 14 independent cases, 6 seam-negative controls; no host qualification")

assert data["schema"] == "implementaudit.native-a-g.fixture.v1"
assert data["slice"] == "E_POST_COMPACTION_ISOLATION"
cases = {case["id"]: case for case in data["cases"]}
assert set(cases) == {
    "E01_GENUINE_COMPACTION_FENCES_BEFORE_SUBSTANTIVE_READ",
    "E02_RAW_STATE_READ_BEFORE_AUDIT_STATE_REJECTED",
    "E03_STALE_ROUTE_CREDIT_REJECTED",
    "E04_NON_BOUNDARY_STARTUP_DOES_NOT_TRIGGER_RECOVERY",
    "E05_SECOND_COMPACTION_REQUIRES_DISTINCT_TRANSACTION",
    "E06_AUDIT_STATE_RETURN_IS_COMPACT_NOT_RAW_CANONICAL_CONTENT",
}
assert cases["E01_GENUINE_COMPACTION_FENCES_BEFORE_SUBSTANTIVE_READ"]["expected"]["sequence"] == ["INVALIDATE", "MECHANICAL_CURRENTNESS", "OPEN_AUDIT_STATE", "RETURN", "RECONCILE", "RESUME_TYPED_EDGE"]
assert cases["E02_RAW_STATE_READ_BEFORE_AUDIT_STATE_REJECTED"]["expected"]["decision"] == "REJECT_GOVERNOR_SUBSTANTIVE_READ"
assert cases["E03_STALE_ROUTE_CREDIT_REJECTED"]["expected"]["credit"] is False
assert cases["E04_NON_BOUNDARY_STARTUP_DOES_NOT_TRIGGER_RECOVERY"]["expected"]["audit_state_required"] is False
assert cases["E05_SECOND_COMPACTION_REQUIRES_DISTINCT_TRANSACTION"]["expected"]["reuse_prior_transaction"] is False
assert cases["E06_AUDIT_STATE_RETURN_IS_COMPACT_NOT_RAW_CANONICAL_CONTENT"]["expected"]["raw_canonical_content_allowed"] is False
assert {case["coverage"] for case in cases.values()} == {"positive", "negative", "boundary"}
print("a-to-g-e-fixture: ok (6/6)")
PY
