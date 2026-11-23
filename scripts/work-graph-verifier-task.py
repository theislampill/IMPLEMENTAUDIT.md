#!/usr/bin/env python3
"""Run the canonical verifier under a live, task-owned completion contract."""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
TASK = "VERIFY"
JOIN = "SETTLE"
CHECKER = "scripts/check-validation-registry.sh"
CHECKER_SHA256 = "723d5c90ae7ec8e57d997e72735e2f17be71836923343bb7c1368622f6f03f63"
REGISTRY = "scripts/verify-package.sh"
WORKFLOW = ".github/workflows/validate.yml"
ROSTER = "tests/*.test.sh"
PROPERTIES = (
    ("registry_nonempty", (38, 41), (ROSTER,)),
    ("fixed_python_runner_image", (53, 57), (WORKFLOW,)),
    ("registry_once", (58, 61), (REGISTRY, ROSTER)),
    ("canonical_route_exactly_once", (63, 67), (WORKFLOW,)),
    ("no_direct_ci_test_dispatch", (68, 73), (WORKFLOW, ROSTER)),
)


def load_owner(name):
    spec = importlib.util.spec_from_file_location(name, HERE / (name + ".py"))
    owner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(owner)
    return owner


def node(name, *, parent="ROOT", kind="TASK", requires=(), reads=(), consumer=None):
    return {
        "id": name, "parent": parent, "kind": kind, "state": "OPEN",
        "requires": list(requires), "optional": [], "reads": list(reads), "writes": [],
        "acceptance": [], "resources": [], "authority": [], "effect": "READ_ONLY",
        "authorization": "PERMITTED", "independence": "KNOWN", "resource_demand": 1,
        "rank": 0, "route_scopes": [], "logical_delivery": None,
        "future_consumer": {"node": consumer, "condition": "exact verifier capture"} if consumer else None,
        "invalidators": [], "independent_results": False, "done_evidence": None,
        "context": {"locality": "GOVERNOR", "governor_cost": 1, "child_cost": 2,
                    "return_cost": 1, "useful_value": 5},
    }


def write_contract(root, observation, encode):
    graph = [
        node("ROOT", parent=None, kind="PLAN", requires=("NEXT",)),
        node(TASK, reads=("path:inputs/verification.json",), consumer=JOIN),
        node(JOIN, kind="JOIN", requires=(TASK,)),
        node("NEXT", requires=(JOIN,)),
    ]
    state = {
        "schema": "implementaudit.native-state.v1", "campaign": "canonical-verifier",
        "root": "ROOT", "original_scope": "canonical verifier task and completion",
        "nodes": [row["id"] for row in graph],
        "event": {"id": "intent", "kind": "RETURN", "subject": TASK},
        "context": {"host_capacity": 1, "operator_ceiling": None, "reserve": 0,
                    "route_facts": [], "outstanding_deliveries": []},
    }
    documents = {"STATE.md": state, "ROADMAP.md": {"schema": "implementaudit.native-roadmap.v1", "phases": []}}
    for row in graph:
        directory = "plans" if row["kind"] == "PLAN" else "tasks"
        documents[f"{directory}/{row['id']}.md"] = {"schema": "implementaudit.native-spec.v1", "nodes": [row]}
    for name, value in documents.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"```implementaudit-work-graph\n" + encode(value) + b"\n```\n")
    path = root / "inputs/verification.json"
    path.parent.mkdir()
    path.write_bytes(encode(observation))


def checker_inputs(qualifier):
    members = {}
    for path in (CHECKER, REGISTRY, WORKFLOW):
        member = qualifier.source_member(path, with_bytes=True, byte_limit=65536)
        if member["kind"] == "MISSING":
            return None
        if member["kind"] != "FILE":
            raise ValueError("nonregular checker input: " + path)
        members[path] = member
    if members[CHECKER]["sha256"] != CHECKER_SHA256:
        return None
    roster = qualifier.registry_membership_v1(qualifier.ROOT)
    return {
        "inputs": {path: {field: row[field] for field in ("bytes", "sha256", "mode")}
                   for path, row in members.items()},
        "registered_roster": roster,
        "fixed_image_rule_applies": b"/usr/bin/python3.12" in members[WORKFLOW]["_acquired_bytes"],
    }


def property_rows(checker, mapping, observed, issue):
    if checker is None:
        return []
    node_id = f"COMMAND:{CHECKER}:0"
    result = next((row for row in observed["nodes"] if row["node"] == node_id), None)
    if result is None:
        return []
    canonical = next(row for row in mapping["nodes"] if row["id"] == node_id)
    if canonical["command"] != CHECKER or canonical["source"].strip() != f"bash {CHECKER}":
        raise ValueError("unsupported canonical checker command")
    inputs = dict(checker["inputs"], **{ROSTER: checker["registered_roster"]})
    properties = []
    for name, lines, depends in PROPERTIES:
        outcome = "UNVERIFIED"
        if result["status"] == "PASS":
            outcome = "PASS"
            if name == "fixed_python_runner_image" and not checker["fixed_image_rule_applies"]:
                outcome = "INAPPLICABLE"
        properties.append({
            "id": name, "outcome": outcome, "dispatch_id": issue["dispatch_id"], "node": node_id,
            "source_lines": list(lines), "inputs": {p: inputs[p] for p in (CHECKER, *depends)},
            "requires": canonical["requires"], "environment_digest": canonical["environment_digest"],
            "writer_resource_constraint": canonical["writer_resource_constraint"],
            "observation": "RETAINED_CANONICAL_NODE_TERMINAL",
            "invalidators": ["task_input", "checker_inputs", "node_source", "environment", "node_trace"],
            "normalization": "PASS_REQUIRES_OBSERVED_NODE_PASS;OTHER_OUTCOMES_UNVERIFIED",
        })
    return properties


def task_status(exit_code):
    if exit_code < 0:
        return "INTERRUPTED"
    return "FAIL" if exit_code else "PASS"


def run_task(mode, output):
    qualifier = load_owner("qualify-work-graph-verifier")
    completion = load_owner("work-graph-completion")
    encode = qualifier.WG.canonical_json_v1
    output = output.resolve()
    if output == qualifier.ROOT or qualifier.ROOT in output.parents:
        raise ValueError("task evidence must be outside the candidate source")
    source = qualifier.source_identity()
    environment = qualifier.environment_identity(dict(os.environ), child_resolution=True)
    owner = qualifier.full_engine_binding()
    checker = checker_inputs(qualifier)
    output.mkdir(mode=0o700, parents=True, exist_ok=False)
    run_root = output / "contract"
    write_contract(run_root, {"mode": mode, "source": source, "environment": environment,
                              "engine_binding": owner, "checker": checker}, encode)
    capture = output / "capture"
    with completion.CompletionContract(run_root, output / "journal") as receiver:
        frontier = receiver.frontier()
        if frontier["selected"] != [TASK]:
            raise ValueError("canonical verifier task is not selected")
        issue = {"dispatch_id": frontier["dispatch_id"], "graph_digest": frontier["graph_digest"],
                 "input_digest": frontier["inputs"][TASK], "expected_old": receiver.history_digest}
        (output / "issue.json").write_bytes(encode(issue) + b"\n")
        wrapper_exit = qualifier.run(mode, capture, empty_stdin=True)
        observed = qualifier.verified_record(capture)
        if (observed["before"] != source or observed["after"] != source
                or observed["environment"] != environment or observed["environment_after"] != environment
                or observed["engine_binding"] != owner or not observed["registration_complete"]
                or qualifier.source_identity() != source or qualifier.full_engine_binding() != owner
                or checker_inputs(qualifier) != checker):
            raise ValueError("verifier source, environment or registry changed")
        code = observed["exit"]
        expected_exit = code if code >= 0 else 128 - code
        if wrapper_exit != expected_exit:
            raise ValueError("wrapper exit differs from observed process exit")
        status = task_status(code)
        result = {
            "schema": "implementaudit.work-result.v1", "node": TASK, "scope": [TASK],
            "dispatch_id": issue["dispatch_id"], "graph_digest": issue["graph_digest"],
            "input_digest": issue["input_digest"], "status": status, "terminal": True,
            "exit_code": code, "evidence_digest": qualifier.sha((capture / "result.json").read_bytes()),
            "independence_key": issue["dispatch_id"] + "-" + TASK,
        }
        mapping = qualifier.WG.decode_strict_json_bytes((capture / "mapping.json").read_bytes(), "mapping")
        properties = property_rows(checker, mapping, observed, issue)
        receiver.accept(frontier, [result], JOIN, expected_old=issue["expected_old"])
        joined = receiver.join(JOIN, expected_old=receiver.history_digest)
        record = {
            "schema": "implementaudit.canonical-verifier-task.v1", "authority": "NONE",
            "issue": issue, "result": result, "join": joined, "nodes": observed["nodes"],
            "properties": properties, "property_population": "REGISTRY_CHECKER_ONLY",
            "successor": receiver.frontier()["states"]["NEXT"],
        }
        (output / "task-result.json").write_bytes(encode(record) + b"\n")
        return record


def compare_tasks(legacy, dag, output):
    """Compare retained raw evidence without taking live settlement custody."""
    qualifier = load_owner("qualify-work-graph-verifier")
    captures = []
    checker_inputs_by_route = []
    for mode, directory in (("legacy", legacy), ("dag", dag)):
        capture = directory / "capture"
        observed = qualifier.verified_record(capture)
        record = qualifier.WG.decode_strict_json_bytes((directory / "task-result.json").read_bytes(), "task result")
        issue = qualifier.WG.decode_strict_json_bytes((directory / "issue.json").read_bytes(), "issued task")
        fields = {"schema", "authority", "issue", "result", "join", "nodes",
                  "properties", "property_population", "successor"}
        issue_fields = {"graph_digest", "dispatch_id", "input_digest", "expected_old"}
        message = "retained capture does not match the declared task result"
        if (type(record) is not dict or set(record) != fields or type(issue) is not dict
                or set(issue) != issue_fields or not all(type(value) is str for value in issue.values())):
            raise ValueError(message)
        status = task_status(observed["exit"])
        expected = {
            "schema": "implementaudit.work-result.v1", "node": TASK, "scope": [TASK],
            "dispatch_id": issue["dispatch_id"], "graph_digest": issue["graph_digest"],
            "input_digest": issue["input_digest"], "status": status, "terminal": True,
            "exit_code": observed["exit"], "evidence_digest": qualifier.sha((capture / "result.json").read_bytes()),
            "independence_key": issue["dispatch_id"] + "-" + TASK,
        }
        join_status = {
            "PASS": "SATISFIED_AT_DECLARED_RESULT_CONTRACT",
            "FAIL": "FAIL",
            "INTERRUPTED": "NONVERDICT",
        }[status]
        joined = record["join"]
        if (record["schema"] != "implementaudit.canonical-verifier-task.v1" or record["authority"] != "NONE"
                or observed["mode"] != mode or record["issue"] != issue or record["nodes"] != observed["nodes"]
                or qualifier.WG.canonical_json_v1(record["result"]) != qualifier.WG.canonical_json_v1(expected)
                or type(joined) is not dict or joined.get("schema") != "implementaudit.native-join.v1"
                or joined.get("consumer") != JOIN or joined.get("required") != [TASK]
                or joined.get("optional") != [] or joined.get("missing") != []
                or joined.get("retained_scopes") != {TASK: [TASK]}
                or joined.get("status") != join_status or joined.get("all_required_settled") is not True
                or joined.get("authority") != "NONE" or joined.get("lifecycle_credit") != "NONE"
                or joined.get("native_dispatch_authorized") is not False
                or record["successor"] != ("READY" if status == "PASS" else "BLOCKED")):
            raise ValueError(message)

        observation = qualifier.WG.decode_strict_json_bytes(
            (directory / "contract" / "inputs" / "verification.json").read_bytes(), "issued verifier input")
        binding = {"mode": mode, "source": observed["before"], "environment": observed["environment"],
                   "engine_binding": observed["engine_binding"]}
        if (type(observation) is not dict or set(observation) != {*binding, "checker"}
                or any(observation[key] != value for key, value in binding.items())):
            raise ValueError(message)
        checker = observation["checker"]
        if checker is not None and (type(checker) is not dict
                or set(checker) != {"inputs", "registered_roster", "fixed_image_rule_applies"}
                or type(checker["fixed_image_rule_applies"]) is not bool
                or type(checker["registered_roster"]) is not dict or type(checker["inputs"]) is not dict
                or set(checker["inputs"]) != {CHECKER, REGISTRY, WORKFLOW}):
            raise ValueError(message)
        mapping = qualifier.WG.decode_strict_json_bytes((capture / "mapping.json").read_bytes(), "mapping")
        expected_properties = property_rows(checker, mapping, observed, issue)
        if (record["property_population"] != "REGISTRY_CHECKER_ONLY"
                or qualifier.WG.canonical_json_v1(record["properties"])
                != qualifier.WG.canonical_json_v1(expected_properties)):
            raise ValueError(message)
        checker_inputs_by_route.append(checker)
        captures.append(capture)
    if checker_inputs_by_route[0] != checker_inputs_by_route[1]:
        raise ValueError(message)
    output.mkdir(mode=0o700, parents=True, exist_ok=False)
    return qualifier.compare(*captures, output / "raw-comparison.json")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("legacy", "dag", "compare"))
    parser.add_argument("paths", type=Path, nargs="+")
    args = parser.parse_args()
    if args.mode == "compare" and len(args.paths) == 3:
        return compare_tasks(*args.paths)
    if args.mode == "compare" or len(args.paths) != 1:
        parser.error("run takes a new output directory; compare takes legacy, DAG and new output directories")
    record = run_task(args.mode, args.paths[0])
    code = record["result"]["exit_code"]
    return code if code >= 0 else 128 - code


if __name__ == "__main__":
    sys.exit(main())
