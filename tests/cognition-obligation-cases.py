#!/usr/bin/env python3
"""Qualify unchanged pending-owner value functions without native side effects.

The source peer remains unadmitted to the installed runtime. Execute only its
closed, side-effect-free value definitions and original constant values. This
does not replace the real observation/authentication/RETURN/acceptance/JOIN
chain or fabricate its proof. Native physical/custody controls keep their own
existing test owner.
"""
import ast
import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "source-peers/native-runtime/skills/implementaudit/scripts/compaction-audit-pending.py"
NAMES = {"Refusal", "require", "canonical", "digest", "blank", "add_observation",
         "outstanding", "scope_owners", "available_scope", "decision", "apply_covered_versions"}


def main():
    raw = SOURCE.read_bytes()
    tree = ast.parse(raw)
    nodes = [node for node in tree.body
             if isinstance(node, (ast.FunctionDef, ast.ClassDef)) and node.name in NAMES]
    assert {node.name for node in nodes} == NAMES, "original owner dependency closure changed"
    constants = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            if node.targets[0].id in {"CEILING", "SCHEMA"}:
                constants[node.targets[0].id] = ast.literal_eval(node.value)
    assert set(constants) == {"CEILING", "SCHEMA"}
    namespace = {"json": json, "hashlib": hashlib, **constants}
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(SOURCE), "exec"), namespace)
    blank, add, decide = (namespace[name] for name in ("blank", "add_observation", "decision"))
    count = 0

    def check(name, state, decision, pending):
        nonlocal count
        before = copy.deepcopy(state)
        result = decide(state)
        assert result["decision"] == decision, name
        assert [row["id"] for row in result["pending"]] == pending, name
        assert result["audit_state_required"] == bool(pending), name
        assert result["state_dependent_decisions_held"] == bool(pending), name
        assert result["authority"] == "NONE", name
        for flag in ("canonical_currentness", "recovery_authority", "epoch_authority", "effect_authority"):
            assert result[flag] is False, (name, flag)
        assert result["actual_child_result_consumer"] == "UNQUALIFIED", name
        assert result["native_lifecycle"] == "NOT_CLAIMED", name
        assert state == before, name + " decision mutated source state"
        count += 1

    check("ordinary-no-boundary", blank("same-session"), "NO_PENDING_AUDIT", [])
    for currentness in ("VERIFIED", "UNRESOLVED"):
        for epoch in ("G0002", None):
            state = blank("same-session")
            add(state, "physical-boundary-A", "COMPLETED_RESUMED_BOUNDARY",
                {"currentness": currentness, "measured_epoch": epoch, "source_offset": 20})
            check("required-currentness-epoch-matrix", state, "AUDIT_STATE_REQUIRED", ["physical-boundary-A"])
    state = blank("same-session")
    for name, offset in (("physical-boundary-A", 20), ("physical-boundary-B", 50)):
        add(state, name, "COMPLETED_RESUMED_BOUNDARY", {"H0": "same", "source_offset": offset})
    check("equal-H0-distinct-occurrences", state, "AUDIT_STATE_REQUIRED", ["physical-boundary-A", "physical-boundary-B"])
    # The first assignment covers only A. Observation/reservation/OPEN/LOAD or
    # a success-shaped return cannot consume either boundary's source version.
    scope = [{"id": "physical-boundary-A", "version": 1, "kind": "COMPLETED_RESUMED_BOUNDARY"}]
    for stage in ("OBSERVED", "RESERVED", "OPEN", "LOADED", "RETURNED", "ACCEPTED"):
        pending = copy.deepcopy(state)
        pending["assignments"]["child-A"] = {"scope": scope, "stage": stage, "return": {"status": "SUCCEEDED"}}
        check("no-consumption-at-" + stage, pending, "AUDIT_STATE_REQUIRED", ["physical-boundary-A", "physical-boundary-B"])
        assert decide(pending)["available_scope"] == [{"id": "physical-boundary-B", "version": 1, "kind": "COMPLETED_RESUMED_BOUNDARY"}]
    state["assignments"]["child-A"] = {"scope": scope}
    state["assignments"]["child-B"] = {"scope": [{"id": "physical-boundary-B", "version": 1, "kind": "COMPLETED_RESUMED_BOUNDARY"}]}
    check("all-reserved-remain-pending", state, "WAIT_EXISTING_AUDIT", ["physical-boundary-A", "physical-boundary-B"])
    # Exercise the actual pure application primitive only. It requires its
    # caller's validated exact cutoff; this call is NOT evidence of native JOIN.
    namespace["apply_covered_versions"](state, scope)
    check("exact-cutoff-leaves-successor", state, "WAIT_EXISTING_AUDIT", ["physical-boundary-B"])
    add(state, "physical-boundary-A", "COMPLETED_RESUMED_BOUNDARY", {"source_offset": 20}, version=2)
    check("new-version-survives-old-coverage", state, "AUDIT_STATE_REQUIRED", ["physical-boundary-A", "physical-boundary-B"])
    state["assignments"]["foreign-child"] = {"scope": [{"id": "physical-boundary-B", "version": 1, "kind": "COMPLETED_RESUMED_BOUNDARY"}]}
    try:
        decide(state)
    except namespace["Refusal"] as error:
        assert str(error) == "CONFLICTING_SCOPE_OWNERS"
        count += 1
    else:
        raise AssertionError("foreign competing scope ownership admitted")
    assert SOURCE.read_bytes() == raw, "selected owner changed during qualification"
    print(json.dumps({"controls": count, "scope": "SOURCE_VALUE_FUNCTIONS_ONLY_NO_NATIVE_ADMISSION",
                      "source_sha256": hashlib.sha256(raw).hexdigest(), "result": "PASS"}, sort_keys=True))


if __name__ == "__main__":
    main()
