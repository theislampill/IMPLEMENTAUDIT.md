#!/usr/bin/env python3
"""Additive Q14 binding/guard controls, owned by issue-ready-work-orders.test.sh.

This consumes hand-authored synthetic projections, not actual semantic evidence.
It never evaluates prose, runs a model, or establishes native/currentness proof.
"""
import ast
import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
Q14_IDS = [
    "E-MATERIAL-NOPUB", "P-EMBEDDED-PUB", "P-TRIVIAL-NOPUB",
    "N-NONMATERIAL-EXCEPTION", "N-INHERITED-IDENTITY", "N-EXTRA-OBJECT",
    "N-NESTED-GOAL", "N-SECOND-ROOT", "N-SEPARATE-MODE", "N-NATIVE-SPINE",
    "N-UNAUTH-PUBLIC",
]
# Literal family expectations for every row and variant. Listed families must
# reject; every unlisted family must return NO_REJECTION. A wrong but well-formed
# singleton identity and unauthorized effects belong to the common output
# contract. The no-publication nested/root/mode clause rejects True, not null.
Q14_FAMILY_REJECTIONS = {
    ("E-MATERIAL-NOPUB", None): (),
    ("P-EMBEDDED-PUB", None): (),
    ("P-TRIVIAL-NOPUB", None): (),
    ("N-NONMATERIAL-EXCEPTION", None): ("embedded", "no_publication"),
    ("N-NONMATERIAL-EXCEPTION", "Use the compact-sufficient input instead of the no-residual input"): ("embedded", "no_publication"),
    ("N-INHERITED-IDENTITY", None): (),
    ("N-INHERITED-IDENTITY", "missing list"): ("native_object_spine",),
    ("N-INHERITED-IDENTITY", "empty list"): ("native_object_spine",),
    ("N-INHERITED-IDENTITY", "multiple distinct identities"): ("native_object_spine",),
    ("N-INHERITED-IDENTITY", "duplicate identity"): ("native_object_spine",),
    ("N-INHERITED-IDENTITY", "missing inherited_from"): (),
    ("N-INHERITED-IDENTITY", "wrong inherited_from"): (),
    ("N-INHERITED-IDENTITY", "self-consistent false identity"): (),
    ("N-EXTRA-OBJECT", None): ("native_object_spine", "no_publication"),
    ("N-EXTRA-OBJECT", "required false state absent"): ("native_object_spine", "no_publication"),
    ("N-NESTED-GOAL", None): ("embedded", "no_publication"),
    ("N-NESTED-GOAL", "required false state absent"): ("embedded",),
    ("N-SECOND-ROOT", None): ("embedded", "no_publication"),
    ("N-SECOND-ROOT", "required false state absent"): ("embedded",),
    ("N-SEPARATE-MODE", None): ("native_object_spine", "no_publication"),
    ("N-SEPARATE-MODE", "required false state absent"): ("native_object_spine",),
    ("N-NATIVE-SPINE", None): ("native_object_spine",),
    ("N-NATIVE-SPINE", "native spine absent"): ("native_object_spine",),
    ("N-UNAUTH-PUBLIC", None): (),
    ("N-UNAUTH-PUBLIC", "allocate durable identity"): (),
    ("N-UNAUTH-PUBLIC", "claim implementation authority"): (),
}
FACT_KEYS = {
    "accessible_corpus", "accepted_scope", "residual_scope",
    "required_distinctions", "surviving_distinctions", "sample_access",
    "first_missing_input", "sample_storage_locator", "consumer", "next_action",
    "horizon", "receiver_readback", "acceptance_basis",
}


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def strings(value):
    return isinstance(value, list) and all(isinstance(item, str) and item.strip() for item in value) and len(value) == len(set(value))


def read_bound(root, record):
    if not isinstance(record, dict) or not isinstance(record.get("path"), str):
        raise ValueError("missing path")
    path = (root / record["path"]).resolve()
    path.relative_to(root.resolve())
    data = path.read_bytes()
    if hashlib.sha256(data).hexdigest() != record.get("sha256"):
        raise ValueError("content digest mismatch")
    if "bytes" in record and len(data) != record["bytes"]:
        raise ValueError("content length mismatch")
    return data.decode("utf-8")


def projection_decision(root, fixture, scenario_name, independent_id):
    """Validate synthetic binding and derive its limited symbolic disposition.

    Expected labels and response output are not arguments. The fact projection
    is an explicit fixture premise, never independently evaluated semantics.
    """
    rejected = {"valid": False, "disposition": "REJECT_BINDING", "proof_scope": "STRUCTURAL_SYNTHETIC_FIXTURE_ONLY"}
    try:
        context = fixture["receiver_context"]
        projection = fixture["synthetic_projections"][scenario_name]
        scenario = fixture["scenarios"][scenario_name]
        if not isinstance(projection, dict) or set(projection) != {"provenance", "semantic_evidence", "scenario_sha256", "context_sha256", "source_procedure_sha256", "source_procedure_lines", "quoted_anchors", "facts"}:
            return rejected
        if projection["provenance"] != "HAND_AUTHORED_SYNTHETIC_FIXTURE_PROJECTION" or projection["semantic_evidence"] != "NOT_OBSERVED":
            return rejected
        if context.get("audit_object_id") != independent_id or not isinstance(independent_id, str) or not independent_id.strip():
            return rejected
        if context.get("entitled_actions") != ["investigate", "reacquire"] or context.get("live_custody") != "NOT_ESTABLISHED":
            return rejected
        if projection["context_sha256"] != digest(context) or projection["scenario_sha256"] != scenario["sha256"]:
            return rejected
        procedure = fixture["source_procedure"]
        if projection["source_procedure_sha256"] != procedure["sha256"] or projection["source_procedure_lines"] != [74, 135]:
            return rejected
        read_bound(root, procedure)
        mission = read_bound(root, scenario)
        anchors = projection["quoted_anchors"]
        if not strings(anchors) or len(anchors) < 2 or any(anchor not in mission for anchor in anchors):
            return rejected
        facts = projection["facts"]
        if not isinstance(facts, dict) or set(facts) != FACT_KEYS:
            return rejected
        if facts["horizon"] != "unknown" or facts["receiver_readback"] != "absent" or facts["sample_storage_locator"] != "unknown":
            return rejected
        if facts["accessible_corpus"] == "hash-only-missing-bodies":
            if any(facts[key] is not None for key in ("accepted_scope", "residual_scope", "required_distinctions", "surviving_distinctions")) or facts["sample_access"] != "unknown" or facts["consumer"] != "unknown" or facts["next_action"] != "reacquire" or facts["acceptance_basis"] != "unknown":
                return rejected
            disposition = "REACQUIRE_UNKNOWN"
        elif facts["accessible_corpus"] == "scenario-body":
            if not all(strings(facts[key]) for key in ("accepted_scope", "residual_scope", "required_distinctions", "surviving_distinctions")):
                return rejected
            accepted, residual = set(facts["accepted_scope"]), set(facts["residual_scope"])
            required, surviving = set(facts["required_distinctions"]), set(facts["surviving_distinctions"])
            if accepted & residual or not surviving <= required:
                return rejected
            if residual:
                if not required or facts["sample_access"] != "unavailable" or facts["first_missing_input"] != "E-C sample content" or facts["next_action"] not in context["entitled_actions"] or facts["consumer"] != "scripts/migrate-store.py owner" or facts["acceptance_basis"] != "partial-identification-only":
                    return rejected
                disposition = "EXTEND_INHERITED" if required - surviving else "KEEP_COMPACT"
            else:
                if required or surviving or facts["first_missing_input"] is not None:
                    return rejected
                if facts["acceptance_basis"] == "synthetic-counterfactual-only" and facts["sample_access"] == "counterfactual-certificate" and facts["next_action"] == "none":
                    disposition = "KEEP_CLOSED_COUNTERFACTUAL"
                elif facts["acceptance_basis"] == "no-edit-or-check-result" and facts["sample_access"] == "not-applicable" and facts["next_action"] == "describe-one-line-step":
                    disposition = "KEEP_COMPACT"
                else:
                    return rejected
        else:
            return rejected
        return {"valid": True, "disposition": disposition, "inherited_object_id": independent_id, "proof_scope": "STRUCTURAL_SYNTHETIC_FIXTURE_ONLY", "semantic_evidence": "NOT_OBSERVED", "retirement": "WITHHELD_NO_READBACK", "implementation_readiness": "NOT_ESTABLISHED"}
    except (OSError, UnicodeError, KeyError, TypeError, ValueError):
        return rejected


def load_owner(root):
    """Load only pure verdict dependencies, without old population/admission runs."""
    owner = root / "tests/issue-ready-work-orders.test.sh"
    script = owner.read_text(encoding="utf-8").split("<<'PY'\n", 1)[1].split("\nPY\n", 1)[0]
    tree = ast.parse(script)
    constants = {"material_fields", "trivial_fields", "material_effects", "pair_actions"}
    nodes = [node for node in tree.body if isinstance(node, (ast.Import, ast.ImportFrom, ast.FunctionDef)) or (isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and target.id in constants for target in node.targets))]
    namespace = {}
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(owner), "exec"), namespace)
    verdict = next(node for node in nodes if isinstance(node, ast.FunctionDef) and node.name == "verdict")
    families = {}
    for family, marker in (("native_object_spine", "audit_object_ids ="), ("embedded", 'if case.get("embedded") is True:'), ("no_publication", 'if case.get("publication_intent") is False:')):
        found = []
        for node in verdict.body:
            if not isinstance(node, ast.If):
                continue
            segment = ast.get_source_segment(script, node)
            if (family == "native_object_spine" and marker in segment) or segment.startswith(marker):
                found.append(node)
        if len(found) != 1:
            raise AssertionError(f"cannot independently locate {family} guard")
        function = ast.parse("def guard(case, inherited_continuation):\n    pass\n").body[0]
        function.body = [copy.deepcopy(found[0]), ast.Return(value=ast.Constant(value="NO_REJECTION"))]
        module = ast.fix_missing_locations(ast.Module(body=[function], type_ignores=[]))
        exec(compile(module, str(owner), "exec"), namespace)
        families[family] = namespace["guard"]
    return namespace, families


def focused_controls(root=ROOT):
    fixture = json.loads((root / "fixtures/issue-ready-work-orders/q14/cases.json").read_text(encoding="utf-8"))
    if fixture.get("schema") != "implementaudit.q14-structural-synthetic-fixture.v1" or fixture.get("proof_scope") != "STRUCTURAL_SYNTHETIC_FIXTURE_ONLY":
        raise AssertionError("Q14 fixture scope/schema drift")
    rows = fixture["q14_cases"]
    assert [row.get("id") for row in rows] == Q14_IDS, "all original eleven Q14 IDs must remain"
    assert set(Q14_FAMILY_REJECTIONS) == {(row["id"], variant.get("name")) for row in rows for variant in [row] + row["variants"]}, "every Q14 row and variant needs explicit family expectations"
    old = json.loads((root / "fixtures/issue-ready-work-orders/cases.json").read_text(encoding="utf-8"))
    independent_id = old["cases"][24]["audit_object_ids"][0]
    assert old["cases"][24]["id"] == "R31-F25"
    namespace, families = load_owner(root)
    results, failures = [], []
    decisions = {name: projection_decision(root, fixture, name, independent_id) for name in fixture["scenarios"]}
    for name, expected in fixture["boundary_expectations"].items():
        if not decisions[name]["valid"] or decisions[name]["disposition"] != expected:
            failures.append(f"{name}: projection boundary mismatch")
    for row in rows:
        for variant in [row] + row["variants"]:
            scenario = variant["scenario"]
            decision = None if scenario is None else decisions[scenario]
            output = variant["output"]
            observed = namespace["verdict"](output, decision)
            active = decision is not None and decision.get("valid") is True and decision["disposition"] == "EXTEND_INHERITED"
            family_results = {name: guard(output, active) for name, guard in families.items()}
            expected_rejections = Q14_FAMILY_REJECTIONS[(row["id"], variant.get("name"))]
            assert set(expected_rejections) <= set(families), "unknown expected guard family"
            family_expectations = {name: "FAIL" if name in expected_rejections else "NO_REJECTION" for name in families}
            result = {"id": row["id"], "variant": variant.get("name"), "expected": variant["expected"], "observed": observed, "disposition": None if decision is None else decision["disposition"], "independent_guard_results": family_results}
            result["independent_guard_expectations"] = family_expectations
            results.append(result)
            if observed != variant["expected"]:
                failures.append(f"{row['id']} {variant.get('name')}: expected {variant['expected']}, observed {observed}")
            for family, expected in family_expectations.items():
                if family_results[family] != expected:
                    failures.append(f"{row['id']} {variant.get('name')} {family}: expected {expected}, observed {family_results[family]}")
            if variant is row and row["id"] in Q14_IDS[:3] and set(family_results.values()) != {"NO_REJECTION"}:
                failures.append(f"{row['id']}: independent positive guard applicability failed")
    # The same evidence-derived synthetic decision must reach both families.
    positive = rows[0]["output"]
    positive_decision = decisions["material"]
    for family in ("embedded", "no_publication"):
        assert families[family](positive, True) == "NO_REJECTION"
        assert families[family](positive, False) == "FAIL", f"{family}: omitted mapping must discriminate"
    # Strip evaluator labels: binding cannot read an oracle or the output row.
    unlabelled = copy.deepcopy(fixture)
    unlabelled.pop("q14_cases")
    unlabelled.pop("boundary_expectations")
    assert projection_decision(root, unlabelled, "material", independent_id) == positive_decision
    malformed = []
    def reject(name, mutate):
        changed = copy.deepcopy(fixture)
        mutate(changed)
        decision = projection_decision(root, changed, "material", independent_id)
        observed = namespace["verdict"](positive, decision)
        malformed.append({"id": name, "binding": decision["disposition"], "observed": observed})
        assert decision["valid"] is False and observed == "FAIL", name
    reject("absent-projection", lambda f: f["synthetic_projections"].pop("material"))
    reject("unbound-scenario", lambda f: f["synthetic_projections"]["material"].update(scenario_sha256="0" * 64))
    reject("unbound-context", lambda f: f["synthetic_projections"]["material"].update(context_sha256="0" * 64))
    reject("unbound-source-procedure", lambda f: f["synthetic_projections"]["material"].update(source_procedure_sha256="0" * 64))
    reject("missing-accessible-quote", lambda f: f["synthetic_projections"]["material"].update(quoted_anchors=["missing source body", "unavailable source body"]))
    reject("contradictory-absorption", lambda f: f["synthetic_projections"]["material"]["facts"]["accepted_scope"].append("migration"))
    reject("missing-sample-promoted-to-migration", lambda f: f["synthetic_projections"]["material"]["facts"].update(next_action="implement"))
    reject("invented-readback", lambda f: f["synthetic_projections"]["material"]["facts"].update(receiver_readback="accepted"))
    reject("invented-semantic-evidence", lambda f: f["synthetic_projections"]["material"].update(semantic_evidence="PASS"))
    reject("boolean-trigger-substitute", lambda f: f["synthetic_projections"].update(material={"material_trigger": True}))
    reject("expected-label-substitute", lambda f: f["synthetic_projections"].update(material={"expected": "EXTEND_INHERITED"}))
    def false_context(f):
        f["receiver_context"]["audit_object_id"] = "other-object"
        f["synthetic_projections"]["material"]["context_sha256"] = digest(f["receiver_context"])
    reject("self-consistent-false-context", false_context)
    # Deleted false states differ from present null and must also fail.
    for key in ("extra_audit_object", "nested_goal", "second_run_root", "separate_mode", "durable_id_allocation", "implementation_authority"):
        output = copy.deepcopy(positive)
        output.pop(key)
        assert namespace["verdict"](output, positive_decision) == "FAIL", key
    report = {"scope": "STRUCTURAL_SYNTHETIC_FIXTURE_ONLY", "q14_rows": len(rows), "q14_variants": len(results) - len(rows), "results": results, "decisions": decisions, "malformed_binding_controls": malformed, "omitted_family_mapping_controls": {"embedded": "FAIL", "no_publication": "FAIL"}, "deleted_false_state_controls": 6, "oracle_removed_control": "same synthetic binding result", "failures": failures, "old_26_46_admission_populations_executed": False, "semantic_receiver_execution": "NOT_RUN", "independent_semantic_evaluation": "NOT_RUN", "native_execution": "NOT_RUN"}
    if failures:
        raise AssertionError("\n".join(failures))
    return report


if __name__ == "__main__":
    report = focused_controls()
    print(json.dumps(report, indent=2))
