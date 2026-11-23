#!/usr/bin/env python3
"""Run the canonical verifier under a live, task-owned completion contract."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import sys


HERE = Path(__file__).resolve().parent
TASK = "VERIFY"
JOIN = "SETTLE"
CHECKER = "scripts/check-validation-registry.sh"
CHECKER_SHA256 = "723d5c90ae7ec8e57d997e72735e2f17be71836923343bb7c1368622f6f03f63"
REGISTRY = "scripts/verify-package.sh"
WORKFLOW = ".github/workflows/validate.yml"
ROSTER = "tests/*.test.sh"
TASK_RECORD_SCOPES = {
    1: ("implementaudit.canonical-verifier-task.v1", "REGISTRY_CHECKER_ONLY"),
    2: ("implementaudit.canonical-verifier-task.v2", "REGISTRY_CHECKER_AND_VERSION_PRELUDE"),
    3: ("implementaudit.canonical-verifier-task.v3", "REGISTRY_CHECKER_AND_PRELUDE_VERSION_AND_FILES"),
}
PROPERTIES = (
    ("registry_nonempty", (38, 41), (ROSTER,)),
    ("fixed_python_runner_image", (53, 57), (WORKFLOW,)),
    ("registry_once", (58, 61), (REGISTRY, ROSTER)),
    ("canonical_route_exactly_once", (63, 67), (WORKFLOW,)),
    ("no_direct_ci_test_dispatch", (68, 73), (WORKFLOW, ROSTER)),
)
PRELUDE_SHA256 = "702f64905d0c9ef8afbeb84ca494ec393f26b3ce3c7388374b95cc48dfdcd07e"
PRELUDE_REGISTRY_SHA256 = "65c7b6939c7bf9396f83cdad58c735cabbc7e28232ceff816e7a8909bf625878"
PLUGIN = ".claude-plugin/plugin.json"
MARKETPLACE = ".claude-plugin/marketplace.json"
SKILL = "skills/implementaudit/SKILL.md"
README = "README.md"
PORTAL = "docs/portal/site.json"
VERSION_PRELUDE_PROPERTIES = (
    ("skill-frontmatter", (499, 501), (SKILL,)),
    ("skill-version-present", (502, 505), (SKILL,)),
    ("skill-plugin-version-equal", (506, 511), (SKILL, PLUGIN)),
    ("plugin-name", (520, 521), (PLUGIN,)),
    ("plugin-source-skills-path", (522, 526), (PLUGIN,)),
    ("plugin-version-present", (527, 528), (PLUGIN,)),
    ("plugin-family-version", (529, 530), (PLUGIN,)),
    ("marketplace-list-nonempty", (533, 535), (MARKETPLACE,)),
    ("marketplace-source-root", (536, 537), (MARKETPLACE,)),
    ("marketplace-path-absent", (538, 539), (MARKETPLACE,)),
    ("milestone-shape", (548, 551), (PORTAL,)),
    ("milestone-family", (552, 555), (PORTAL, PLUGIN)),
    ("readme-claim-present", (556, 558), (README,)),
    ("each-readme-claim-matches", (559, 563), (README, PORTAL, PLUGIN)),
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


def version_prelude_inputs(source):
    members = source["members"]
    inputs = {}
    for path in (REGISTRY, PLUGIN, MARKETPLACE, SKILL, README, PORTAL):
        member = members.get(path)
        if member is None or member["kind"] != "FILE":
            raise ValueError("version prelude requires a regular source member: " + path)
        inputs[path] = {key: member[key] for key in ("bytes", "sha256", "mode")}
    if inputs[REGISTRY]["sha256"] != PRELUDE_REGISTRY_SHA256:
        raise ValueError("version prelude requires the exact supported registry")
    return inputs


def canonical_prelude(mapping, observed):
    node = mapping["nodes"][0]
    if (mapping["registry_sha256"] != PRELUDE_REGISTRY_SHA256 or node["id"] != "PRELUDE"
            or node["kind"] != "COMPOSED_PRELUDE"
            or hashlib.sha256(node["source"].encode("utf-8")).hexdigest() != PRELUDE_SHA256):
        raise ValueError("version prelude does not match the exact canonical source span")
    terminal = observed["nodes"][0]
    if terminal["node"] != "PRELUDE":
        raise ValueError("version prelude observation is out of order")
    return node, terminal["status"] == "PASS"


def version_prelude_rows(inputs, mapping, observed, issue):
    node, passed = canonical_prelude(mapping, observed)
    outcome = "PASS" if passed else "UNVERIFIED"
    return [{
        "id": name, "outcome": outcome, "dispatch_id": issue["dispatch_id"], "node": "PRELUDE",
        "source_lines": list(lines), "inputs": {path: inputs[path] for path in (REGISTRY, *depends)},
        "requires": node["requires"], "environment_digest": node["environment_digest"],
        "writer_resource_constraint": node["writer_resource_constraint"],
        "observation": "RETAINED_CANONICAL_NODE_TERMINAL",
        "invalidators": ["task_input", "prelude_inputs", "node_source", "environment", "node_trace"],
        "normalization": "PASS_REQUIRES_OBSERVED_COMPOSED_PRELUDE_PASS;OTHER_OUTCOMES_UNVERIFIED",
    } for name, lines, depends in VERSION_PRELUDE_PROPERTIES]


def required_file_rows(source, mapping, observed, issue):
    node, passed = canonical_prelude(mapping, observed)
    locations = {}
    for line_number, line in enumerate(node["source"].splitlines(), 1):
        if line.startswith("require_file "):
            call = re.fullmatch(r"require_file ([A-Za-z0-9._/-]+)", line)
            if call is None:
                raise ValueError("unsupported required-file call in canonical prelude")
            locations.setdefault(call[1], []).append(line_number)
    members = source["members"]
    rows = []
    for path, lines in locations.items():
        member = members.get(path, {"kind": "UNACQUIRED"})
        outcome = "PASS" if passed and member["kind"] == "FILE" else "UNVERIFIED"
        rows.append({
            "id": "required-file:" + path, "outcome": outcome, "dispatch_id": issue["dispatch_id"],
            "node": "PRELUDE", "source_lines": lines, "inputs": {REGISTRY: members[REGISTRY], path: member},
            "requires": node["requires"], "environment_digest": node["environment_digest"],
            "writer_resource_constraint": node["writer_resource_constraint"],
            "observation": "RETAINED_CANONICAL_NODE_TERMINAL",
            "invalidators": ["task_input", "required_member", "node_source", "environment", "node_trace"],
            "normalization": "PASS_REQUIRES_OBSERVED_COMPOSED_PRELUDE_PASS_AND_REGULAR_INPUT",
        })
    return rows


def task_status(exit_code):
    if exit_code < 0:
        return "INTERRUPTED"
    return "FAIL" if exit_code else "PASS"


def run_task(mode, output, *, include_version_prelude=False, include_required_files=False):
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
    observation = {"mode": mode, "source": source, "environment": environment,
                   "engine_binding": owner, "checker": checker}
    version = 3 if include_required_files else 2 if include_version_prelude else 1
    if version >= 2:
        if checker is None:
            raise ValueError("version prelude evidence requires the supported registry checker")
        observation["version_prelude_inputs"] = version_prelude_inputs(source)
    if version == 3:
        observation["required_file_properties"] = True
    output.mkdir(mode=0o700, parents=True, exist_ok=False)
    run_root = output / "contract"
    write_contract(run_root, observation, encode)
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
        if version >= 2:
            properties = version_prelude_rows(observation["version_prelude_inputs"], mapping, observed, issue) + properties
        if version == 3:
            properties = required_file_rows(source, mapping, observed, issue) + properties
        receiver.accept(frontier, [result], JOIN, expected_old=issue["expected_old"])
        joined = receiver.join(JOIN, expected_old=receiver.history_digest)
        schema, population = TASK_RECORD_SCOPES[version]
        record = {
            "schema": schema, "authority": "NONE",
            "issue": issue, "result": result, "join": joined, "nodes": observed["nodes"],
            "properties": properties, "property_population": population,
            "successor": receiver.frontier()["states"]["NEXT"],
        }
        (output / "task-result.json").write_bytes(encode(record) + b"\n")
        return record


def verify_task_history(completion, qualifier, directory, observed, record, input_digest):
    """Compare the portable completion readback without opening a journal writer."""
    wg = qualifier.WG
    digest = completion._hash
    require = completion._require
    message = "retained capture does not match the declared task result"
    original_contract = str(Path(observed["execution_context"]["output"]).parent / "contract")
    run_identity = digest([original_contract, original_contract])
    history, _ = completion._read_history(directory / "journal" / "history.json",
                                          run_identity, wg.decode_strict_json_bytes)
    result = record["result"]
    kinds = ["BATCH", "JOIN"] if result["status"] == "PASS" else ["BATCH"]
    events = history["events"]
    require([event["kind"] for event in events] == kinds, message)
    received = []
    for event in events:
        body = event["body"]
        require(type(body) is dict and set(body) == {"records"} and type(body["records"]) is list
                and len(body["records"]) == 1, message)
        item = body["records"][0]
        require(type(item) is dict and set(item) ==
                {"digest", "node", "status", "consumer", "result", "predecessors", "source_graph"}
                and item["digest"] == digest({key: value for key, value in item.items() if key != "digest"}),
                message)
        received.append(item)
    task = received[0]
    graph = task["source_graph"]
    issued = wg.derive_completion_frontier_v1(graph, {})
    expected_old = digest(dict(history, events=[]))
    require(issued["selected"] == [TASK] and record["issue"] == {
        "dispatch_id": issued["dispatch_id"], "graph_digest": issued["graph_digest"],
        "input_digest": issued["inputs"][TASK], "expected_old": expected_old,
    }, message)
    require(task["node"] == TASK and task["consumer"] == JOIN and task["status"] == result["status"]
            and task["predecessors"] == {} and wg.canonical_json_v1(task["result"]) == wg.canonical_json_v1(result)
            and graph["binding"]["read_set"] == {
                "path:inputs/verification.json": {"status": "PRESENT_FILE", "sha256": input_digest},
            }, message)
    verdict = wg._join_native_results_v1(graph, {TASK: result}, JOIN)
    verdict.update(evidence_scope="PORTABLE_DECLARED_RESULT_CONTRACT", native_dispatch_authorized=False)
    outcomes = {TASK: {"status": task["status"], "digest": task["digest"]}}
    if len(received) == 2:
        joined = received[1]
        frontier = wg.derive_completion_frontier_v1(graph, outcomes)
        require(frontier["selected"] == [JOIN], message)
        join_result = {
            "schema": "implementaudit.work-result.v1", "node": JOIN, "scope": [JOIN],
            "dispatch_id": frontier["dispatch_id"], "graph_digest": frontier["graph_digest"],
            "input_digest": frontier["inputs"][JOIN], "status": "PASS", "terminal": True,
            "exit_code": 0, "evidence_digest": digest(verdict), "independence_key": "required-join-" + JOIN,
        }
        require(joined["node"] == JOIN and joined["status"] == "PASS" and joined["consumer"] is None
                and joined["source_graph"] == graph and joined["predecessors"] == {TASK: task["digest"]}
                and wg.canonical_json_v1(joined["result"]) == wg.canonical_json_v1(join_result), message)
        outcomes[JOIN] = {"status": joined["status"], "digest": joined["digest"]}
        verdict.update(completion_digest=joined["digest"], replay=False)
    require(wg.canonical_json_v1(record["join"]) == wg.canonical_json_v1(verdict)
            and record["successor"] == wg.derive_completion_frontier_v1(graph, outcomes)["states"]["NEXT"], message)


def compare_tasks(legacy, dag, output):
    """Compare retained raw evidence without taking live settlement custody."""
    qualifier = load_owner("qualify-work-graph-verifier")
    completion = load_owner("work-graph-completion")
    encode = qualifier.WG.canonical_json_v1
    captures = []
    property_inputs_by_route = []
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
        version = next((key for key, scope in TASK_RECORD_SCOPES.items() if scope[0] == record["schema"]), None)
        if (version is None or record["authority"] != "NONE"
                or observed["mode"] != mode or record["issue"] != issue
                or encode(record["nodes"]) != encode(observed["nodes"])
                or encode(record["result"]) != encode(expected)):
            raise ValueError(message)
        _, population = TASK_RECORD_SCOPES[version]

        input_bytes, input_identity = completion._read(directory / "contract" / "inputs" / "verification.json",
                                                       completion.MAX_JOURNAL_BYTES)
        input_digest = qualifier.WG._graph_hash([input_identity[2] & 0o7777, qualifier.sha(input_bytes)])
        verify_task_history(completion, qualifier, directory, observed, record, input_digest)
        observation = qualifier.WG.decode_strict_json_bytes(input_bytes, "issued verifier input")
        binding = {"mode": mode, "source": observed["before"], "environment": observed["environment"],
                   "engine_binding": observed["engine_binding"]}
        if version >= 2:
            binding["version_prelude_inputs"] = version_prelude_inputs(observed["before"])
        if version == 3:
            binding["required_file_properties"] = True
        if (type(observation) is not dict or set(observation) != {*binding, "checker"}
                or any(encode(observation[key]) != encode(value) for key, value in binding.items())):
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
        version_inputs = binding.get("version_prelude_inputs")
        if version >= 2:
            if checker is None:
                raise ValueError(message)
            expected_properties = version_prelude_rows(version_inputs, mapping, observed, issue) + expected_properties
        if version == 3:
            expected_properties = required_file_rows(observed["before"], mapping, observed, issue) + expected_properties
        if record["property_population"] != population or encode(record["properties"]) != encode(expected_properties):
            raise ValueError(message)
        property_inputs_by_route.append((version, checker, version_inputs))
        captures.append(capture)
    if property_inputs_by_route[0] != property_inputs_by_route[1]:
        raise ValueError(message)
    output.mkdir(mode=0o700, parents=True, exist_ok=False)
    return qualifier.compare(*captures, output / "raw-comparison.json")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("legacy", "dag", "compare"))
    parser.add_argument("paths", type=Path, nargs="+")
    parser.add_argument("--include-version-prelude", action="store_true")
    parser.add_argument("--include-required-files", action="store_true")
    args = parser.parse_args()
    if args.mode == "compare" and (args.include_version_prelude or args.include_required_files):
        parser.error("compare reads the property evidence version from each retained run")
    if args.mode == "compare" and len(args.paths) == 3:
        return compare_tasks(*args.paths)
    if args.mode == "compare" or len(args.paths) != 1:
        parser.error("run takes a new output directory; compare takes legacy, DAG and new output directories")
    record = run_task(args.mode, args.paths[0], include_version_prelude=args.include_version_prelude,
                      include_required_files=args.include_required_files)
    code = record["result"]["exit_code"]
    return code if code >= 0 else 128 - code


if __name__ == "__main__":
    sys.exit(main())
