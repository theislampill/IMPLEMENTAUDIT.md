"""Prove the exact-source V02 association boundary without running the verifier."""

import ast
import contextlib
import importlib.util
import inspect
import io
import json
from pathlib import Path
import re
import sys
from unittest.mock import patch


HERE = Path(__file__).parent
V01_SHA = "41bb6794af7a31656d193cfc95bc97c48c078b19a484d38491ab0e23eef3d913"
CHECKER = "scripts/check-validation-registry.sh"
WORKFLOW = ".github/workflows/validate.yml"
OWNER_NODE = "COMMAND:scripts/check-validation-registry.sh:0"
REQUIRED_RELATIONS = {"whole", "portal", "repro", "pending_durability", "pending_loader"}


def v01_module():
    location = HERE.parent / "original-v01" / "verify_v01.py"
    spec = importlib.util.spec_from_file_location("v01_exact_reads", location)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def source_row(v):
    data = json.loads(v.blob(v.WORK_ORDER, "recovery/contracts/original/DEFINITIONS_48_20_117_12.json"))
    control = json.loads(v.blob(v.RESULTS, v.ROW_MAP))
    expected = next(row for row in data["original48"] if row["id"] == "R35-V02")
    actual = next(row for row in control["rows"] if row["criterion_id"] == "R35-V02")
    v.require(len(data["original48"]) == len(control["rows"]) == 48 and
              expected["requirement_exact"] == actual["original_text"] and
              expected["original_scope_and_binding_exact"] == actual["original_scope_and_binding"],
              "V02 contract changed")
    v.require(actual["mandatory_operation_or_consumer_references"] == ["M2"]
              and actual["conditional_references"] == [], "V02 applicability changed")
    return {"id": "R35-V02", "literal": expected["requirement_exact"],
            "scope": expected["original_scope_and_binding_exact"], "mandatory": ["M2"],
            "conditional": [], "original_rows": 48}


def checker_result(source, registry, workflow, paths):
    reads = {"scripts/verify-package.sh": registry.decode(), WORKFLOW: workflow.decode()}
    output, errors = io.StringIO(), io.StringIO()

    def read_text(path, *, encoding):
        if encoding != "utf-8":
            raise ValueError("unexpected fixture encoding")
        return reads[path.as_posix()]

    def glob(path, pattern):
        if path.as_posix() != "tests" or pattern != "*.test.sh":
            raise ValueError("unexpected fixture lookup")
        return [Path(name) for name in paths]

    status = 0
    with patch.object(Path, "read_text", read_text), patch.object(Path, "glob", glob), \
            contextlib.redirect_stdout(output), contextlib.redirect_stderr(errors):
        try:
            exec(source, {})
        except SystemExit as exc:
            status = exc.code
    return status, output.getvalue(), errors.getvalue()


def discriminators(v, registry, paths, checker, workflow):
    # Only the exact inline read-only checker runs. Neither shell nor CI sees these data variants.
    parts = re.findall(rb"<<'PY'\r?\n(.*?)\r?\nPY(?:\r?\n|$)", checker, re.S)
    v.require(len(parts) == 1, "exact one inline read-only checker")
    source = compile(parts[0], "<exact registry checker on inert data>", "exec")
    ok = f"check-validation-registry: ok ({len(paths)} tests; one canonical CI route)\n"
    v.require(checker_result(source, registry, workflow, paths) == (0, ok, ""), "exact positive checker")

    invocation = b"        run: bash scripts/verify-package.sh\n"
    v.require(workflow.count(invocation) == 1, "single invocation selection")
    duplicate = workflow.replace(invocation, invocation
                                 + b"      - name: Constructed duplicate registry route\n"
                                 + invocation)
    direct = workflow.replace(invocation, invocation
                              + b"      - name: Constructed direct test\n"
                              + b"        run: bash tests/phase-validation.test.sh\n")
    runner = b"    runs-on: ubuntu-24.04\n"
    v.require(workflow.count(runner) == 1 and b"/usr/bin/python3.12" in workflow,
              "qualified runner variant precondition")
    foreign_image = workflow.replace(runner, b"    runs-on: ubuntu-latest\n")
    observed = {}
    for key, modified, diagnostic in (
        ("canonical_route_exactly_once", duplicate, "must invoke scripts/verify-package.sh exactly once"),
        ("no_direct_ci_test_dispatch", direct, "tests/phase-validation.test.sh is directly invoked"),
        ("fixed_python_runner_image", foreign_image, "fixed Python 3.12 CI prerequisites require"),
    ):
        status, out, err = checker_result(source, registry, modified, paths)
        v.require(status == 1 and not out and diagnostic in err and len(err.splitlines()) == 1,
                  f"individual actual checker predicate was not discriminated: {key}")
        observed[key] = {"exit": status, "diagnostic": err.strip(), "changed_workflow_data": v.pin(modified),
                         "registry_input_changed": False, "compiler_property_association_available": False}
    return observed


def canonical_consumer(v):
    verifier = v.blob(v.PRODUCT, "scripts/qualify-work-graph-verifier.py")
    transport = v.blob(v.PRODUCT, "scripts/run-work-graph-verifier.sh")
    tree = ast.parse(verifier)
    receiver = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "verified_record")
    closure = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "valid_nodes")
    fields = set()
    for node in receiver.body:
        if isinstance(node, ast.Assign) and any(isinstance(x, ast.Name) and x.id == "fields" for x in node.targets):
            fields |= ast.literal_eval(node.value)
    for node in ast.walk(receiver):
        if isinstance(node, ast.AugAssign) and isinstance(node.target, ast.Name) and node.target.id == "fields":
            fields |= ast.literal_eval(node.value)
    node_fields = sorted(ast.literal_eval(node) for node in ast.walk(closure)
                         if isinstance(node, ast.Set) and ast.literal_eval(node) == {"node", "status", "terminal"})
    v.require(node_fields == [{"node", "status", "terminal"}] and "graph_digest" in fields
              and "environment" in fields and "stdout_sha256" in fields and "stderr_sha256" in fields
              and not fields.intersection({"property_rows", "property_map", "obligation_map", "join_rows"}),
              "canonical result shape drift")
    v.require(b'IFS= read -r -d \'\' -u "$r0035_verifier_frame_fd" r0035_verifier_id' in transport
              and b'IFS= read -r -d \'\' -u "$r0035_verifier_frame_fd" r0035_verifier_source' in transport,
              "canonical command frame shape changed")
    return {"receiver_source": v.pin(verifier), "transport_source": v.pin(transport),
            "receiver_result_fields_union": sorted(fields), "receiver_node_fields": sorted(node_fields[0]),
            "transport_fields": ["node_id", "source_bytes"]}

def main():
    v = v01_module()
    original = HERE.parent / "original-v01" / "V01_EVIDENCE.json"
    raw = original.read_bytes()
    v.require(v.pin(raw)["sha256"] == V01_SHA, "frozen V01 evidence differs")
    evidence = json.loads(raw)
    v.require(evidence["product"] == {"commit": v.PRODUCT, "tree": v.TREE}, "V01 exact subject differs")
    registry = v.blob(v.PRODUCT, v.REGISTRY)
    checker, workflow = v.blob(v.PRODUCT, CHECKER), v.blob(v.PRODUCT, WORKFLOW)
    paths = evidence["current_registered_tests"]
    ns, owner_pin = v.compiler()
    graph = ns["compile_verifier_graph_v1"](registry, paths, v.CONSTRUCTED_ENV)
    node = next(node for node in graph["nodes"] if node["id"] == OWNER_NODE)
    v.require(len([row for row in graph["nodes"] if row["command"] == CHECKER]) == 1
              and v.pin(registry) == evidence["registry"] and
              v.pin(ns["verifier_command_stream_v1"](graph, registry)) ==
              evidence["retained_m2"]["source_command_stream_descriptor"], "V01 graph identity reuse")
    controls = discriminators(v, registry, paths, checker, workflow)

    decision, probes, decision_pin, archive_pin = v.m2_records()
    m2 = probes[0]["result"]["full_correspondence"]
    v.require(set(m2["relations"]) == REQUIRED_RELATIONS and m2["all_declared_relations_equal"]
              and m2 == probes[1]["result"]["full_correspondence"], "retained M2 relation scope")
    captures = {}
    for record in probes[0]["result"]["records"]:
        v.require(all(set(row) == {"ordinal", "status", "terminal"} for row in record["nodes"]),
                  "M2 public per-node result shape")
        captures[record["mode"]] = {"public_node_fields": sorted(record["nodes"][0]),
                                    "legacy_trace": record["legacy_node_trace"],
                                    "ordinal_slots": len(record["nodes"])}
    result = {
        "schema": "dg16.original-v02.exact-source-association-boundary.v1",
        "row": source_row(v), "product": evidence["product"], "v01_census_receipt": v.pin(raw),
        "canonical_compiler": owner_pin,
        "canonical_workflow": v.pin(workflow), "selected_registry_checker": v.pin(checker),
        "node_witness": {"id": OWNER_NODE, "fields": sorted(node),
                         "environment_digest": node["environment_digest"],
                         "writer_resource_constraint": node["writer_resource_constraint"],
                         "independence": node["independence"], "evidence_tags": node["evidence"],
                         "invalidators": node["invalidators"], "result_contract": node["result_contract"]},
        "graph_inputs": list(inspect.signature(ns["compile_verifier_graph_v1"]).parameters),
        "canonical_consumer": canonical_consumer(v),
        "property_discriminators": controls,
        "m2": {"run": decision["run_id"], "archive": archive_pin, "decision": decision_pin,
               "named_whole_operation_relations": sorted(m2["relations"]), "public_captures": captures},
        "canonical_source_property_association": "UNREPRESENTED_BY_SELECTED_GRAPH_AND_RECEIVER",
        "retained_application_evidence": "NO_COMPLETE_PROPERTY_TO_NODE_OR_JOIN_ASSOCIATION_RECEIVED",
        "recommended_disposition": "HOLD_ORIGINAL_R35_V02",
        "independent_root_receiving_pending": True, "new_original_awards": [],
        "registry_commands_executed": 0, "hosted_dispatch": False, "m2_replay": False, "m6_credit": False,
    }
    sys.stdout.buffer.write((json.dumps(result, sort_keys=True, indent=2) + "\n").encode())


if __name__ == "__main__":
    main()
