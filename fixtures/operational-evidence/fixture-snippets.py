"""Constructed source-fixture data only; no host or native evidence.

Copied from pinned public tests/auto-loom-semantics-regression.py.
Only this pure fixture factory is included; no helper or test runner is imported.
"""
from copy import deepcopy

COVERAGE_INVARIANTS = {
    "AUTO_LOOM_SCOPE": "FULL_RECURSIVE_CAMPAIGN_HOLARCHY",
    "LOCAL_FORWARD_ONLY": "INSUFFICIENT",
    "OUTWARD_STARVATION": "CONFORMANCE_CONCERN",
    "FUTURE_JOIN_PRECOMPUTATION_REQUIRED": "YES",
    "BLOCK_EDGE_NOT_FUTURE_GRAPH": "YES",
}

def coverage_case():
    """Literal, hand-derived dispositions; no expectation calls the consumer."""
    binding = {"campaign": "fixture-v041", "event": "material-join-2", "state": "state-2"}
    old = {"campaign": "fixture-v041", "event": "material-join-1", "state": "state-1"}
    facts = {
        "binding": binding, "root": "campaign", "subject": "recovery",
        "parents": {"recovery": "integration", "integration": "campaign", "campaign": None},
        "views": ["auto_loom", "current_boundary", "runtime_directions_latest"],
        "history": [{"binding": old, "evidence_scope": "SOURCE_ONLY", "authority": "NONE"}],
        "currentness": False, "evidence_scope": "SOURCE_ONLY",
        "prior": None, "edges": [],
    }
    proposal = {
        "binding": deepcopy(binding), "invariants": deepcopy(COVERAGE_INVARIANTS),
        "directions": ["INWARD", "OUTWARD", "FORWARD", "BACKWARD"],
        "ancestors": ["recovery", "integration", "campaign"], "edges": [],
        "views": [
            {"name": "auto_loom", "status": "CURRENT", "binding": deepcopy(binding),
             "evidence_scope": "SOURCE_ONLY", "authority": "NONE"},
            {"name": "current_boundary", "status": "CURRENT", "binding": deepcopy(binding),
             "evidence_scope": "SOURCE_ONLY", "authority": "NONE"},
            {"name": "runtime_directions_latest", "status": "CURRENT", "binding": deepcopy(binding),
             "evidence_scope": "SOURCE_ONLY", "authority": "NONE"},
        ],
        "new_actions": ["rlgwo-prep", "future-source-join"],
        "backward_joins": ["accepted-source"],
        "evidence_scope": "SOURCE_ONLY", "authority": "NONE",
    }

    def add(identity, ancestor, direction, state, gates, want, pending, owner, consumer,
            reconsider, next_action, scope="SOURCE_ONLY", accepted=False, joined_into=None):
        common = {
            "id": identity, "direction": direction, "owner": owner, "consumer": consumer,
            "reconsider": reconsider, "next_action": next_action, "evidence_scope": scope,
        }
        facts["edges"].append({
            **common, "at": ancestor, "state": state, "gates": gates,
            "accepted": accepted, "joined_into": joined_into,
        })
        proposal["edges"].append({
            **common, "binding": deepcopy(binding), "eligibility": want,
            "pending": pending, "authority": "NONE",
        })

    clear = {"identity": "SATISFIED", "authority": "SATISFIED",
             "independence": "SATISFIED", "writer": "SATISFIED", "resource": "SATISFIED",
             "prerequisites": "SATISFIED"}
    add("native-recovery", "recovery", "INWARD", "PENDING",
        {**clear, "native_currentness": "MISSING"}, "BLOCKED", {"native_currentness": "MISSING"},
        "native-owner", "recovery-join", "native-currentness-receipt", "await-currentness",
        scope="NONE")
    add("rlgwo-prep", "integration", "OUTWARD", "PENDING", dict(clear), "ELIGIBLE", {},
        "rlgwo-owner", "crosswalk-join", "new-source-or-owner-disposition", "prepare-crosswalk")
    add("future-source-join", "campaign", "FORWARD", "PENDING", dict(clear), "ELIGIBLE", {},
        "source-owner", "future-b4-qualification-join", "integrated-identity-freeze", "prepare-gate-matrix")
    add("a-through-k-admission", "integration", "OUTWARD", "PENDING",
        {**clear, "independence": "UNKNOWN", "authority": "MISSING"}, "BLOCKED",
        {"independence": "UNKNOWN", "authority": "MISSING"},
        "admission-owner", "a-through-k-join", "per-lane-independence-and-authority", "await-lane-admission")
    add("material-census", "campaign", "FORWARD", "PENDING",
        {**clear, "writer": "MISSING"}, "BLOCKED", {"writer": "MISSING"},
        "census-owner", "material-census-join", "shared-writer-release", "await-writer")
    add("publication-done", "campaign", "FORWARD", "DONE", dict(clear), "RETAINED", {},
        "publication-owner", "public-consumer-readback", "applicability-change-only", "retain-completed-proof",
        scope="PUBLICATION_EVIDENCE")
    add("returned-source", "integration", "BACKWARD", "RETURNED", dict(clear), "PENDING_JOIN", {},
        "root", "source-join", "root-acceptance-join", "await-acceptance")
    add("accepted-source", "integration", "BACKWARD", "JOINED", dict(clear), "RETAINED", {},
        "root", "source-join", "changed-source-applicability", "retain-partial-join",
        accepted=True, joined_into="integration")
    add("four-child-active", "integration", "INWARD", "ACTIVE", dict(clear), "ACTIVE", {},
        "four-child-owner", "four-child-join", "material-return", "retain-active-owner")
    return facts, proposal
