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
    4: ("implementaudit.canonical-verifier-task.v4", "REGISTRY_ALL_NODES_AND_PRELUDE_OBLIGATIONS"),
}
PROPERTIES = (
    ("registry_nonempty", (38, 41), (ROSTER,)),
    ("fixed_python_runner_image", (53, 57), (WORKFLOW,)),
    ("registry_once", (58, 61), (REGISTRY, ROSTER)),
    ("canonical_route_exactly_once", (63, 67), (WORKFLOW,)),
    ("no_direct_ci_test_dispatch", (68, 73), (WORKFLOW, ROSTER)),
)
PRELUDE_REGISTRIES = {
    "65c7b6939c7bf9396f83cdad58c735cabbc7e28232ceff816e7a8909bf625878":
        ("702f64905d0c9ef8afbeb84ca494ec393f26b3ce3c7388374b95cc48dfdcd07e", 0),
    "ea132140d64d2714f5a54356c4b79cd05dd2b32017c38cd2307115adc7ec6978":
        ("aaf7a9e0992bb2e76733b149cba3cdb8b5c6297641a6617f1291b7c4fe1001f3", 2),
}
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
    if inputs[REGISTRY]["sha256"] not in PRELUDE_REGISTRIES:
        raise ValueError("version prelude requires the exact supported registry")
    return inputs


def canonical_prelude(mapping, observed):
    node = mapping["nodes"][0]
    basis = PRELUDE_REGISTRIES.get(mapping["registry_sha256"])
    if (basis is None or node["id"] != "PRELUDE"
            or node["kind"] != "COMPOSED_PRELUDE"
            or hashlib.sha256(node["source"].encode("utf-8")).hexdigest() != basis[0]):
        raise ValueError("version prelude does not match the exact canonical source span")
    terminal = observed["nodes"][0]
    if terminal["node"] != "PRELUDE":
        raise ValueError("version prelude observation is out of order")
    return node, terminal["status"] == "PASS", basis[1]


def version_prelude_rows(inputs, mapping, observed, issue):
    node, passed, line_offset = canonical_prelude(mapping, observed)
    outcome = "PASS" if passed else "UNVERIFIED"
    return [{
        "id": name, "outcome": outcome, "dispatch_id": issue["dispatch_id"], "node": "PRELUDE",
        "source_lines": [line + line_offset for line in lines],
        "inputs": {path: inputs[path] for path in (REGISTRY, *depends)},
        "requires": node["requires"], "environment_digest": node["environment_digest"],
        "writer_resource_constraint": node["writer_resource_constraint"],
        "observation": "RETAINED_CANONICAL_NODE_TERMINAL",
        "invalidators": ["task_input", "prelude_inputs", "node_source", "environment", "node_trace"],
        "normalization": "PASS_REQUIRES_OBSERVED_COMPOSED_PRELUDE_PASS;OTHER_OUTCOMES_UNVERIFIED",
    } for name, lines, depends in VERSION_PRELUDE_PROPERTIES]


def required_file_rows(source, mapping, observed, issue):
    node, passed, _ = canonical_prelude(mapping, observed)
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



# V02: every registry obligation maps exactly once to one node or the SETTLE JOIN.
# The classification is bound to one exact registry; any other registry is refused
# rather than emitted with partial coverage. Loop expansions are read from the
# canonical prelude source text; only line spans are tabulated here.
ALL_OBLIGATION_REGISTRY = "ea132140d64d2714f5a54356c4b79cd05dd2b32017c38cd2307115adc7ec6978"
NO_ARGUMENTS = "INAPPLICABLE_NO_ARGUMENTS_SUPPLIED"
CANONICAL_COMMANDS = (["bash", REGISTRY], ["bash", "scripts/run-work-graph-verifier.sh"])
CHILD_AGENTS = "skills/implementaudit/references/child-agents.md"
PRELUDE_STRUCTURE = {
    "shebang": (1,), "shell-options": (2,), "environment": (4,), "fail-definition": (6, 7, 8, 9),
    "repo-root": (11, 12), "state": (14, 15, 16), "exit-trap": (17, 18),
    "require-file-definition": (44, 45, 46), "comment": (568,),
    "child-report-loop": tuple(range(439, 446)) + (455, 457, 458),
    "marker-loop": tuple(range(571, 589)) + (590,),
    "require-absent-matches-definition": tuple(range(621, 634)),
    "absence-pattern-assembly": tuple(range(648, 654)),
}
HEREDOC_SCAFFOLD = tuple(range(494, 515)) + tuple(range(516, 567))
PRELUDE_OBLIGATIONS = (
    # id, registry lines, obligation kind, outcome rule, input members beyond the registry
    ("release-identity-arguments", range(19, 42), "ARGUMENT_MODE", NO_ARGUMENTS, ()),
    ("no-unknown-arguments", (42,), "ARGUMENT_GUARD", "NODE", ()),
    ("root-implementaudit-md-absent", range(48, 51), "INLINE_GUARD", "NODE", ("IMPLEMENTAUDIT.md",)),
    ("release-identity-build-and-check", range(66, 72), "CONDITIONAL_COMMANDS", NO_ARGUMENTS,
     ("scripts/build-release-asset.sh",)),
    ("child-agents-andon-registration-invariant", (460,), "INLINE_GUARD", "NODE", (CHILD_AGENTS,)),
    ("child-agents-false-green-rerun-rule", (461,), "INLINE_GUARD", "NODE", (CHILD_AGENTS,)),
    ("python-interpreter-available", range(463, 472), "INTERPRETER_SELECTION", "NODE", ()),
    ("plugin-json-valid", (473,), "SET_E_COMMAND", "NODE", (PLUGIN,)),
    ("marketplace-json-valid", (474,), "SET_E_COMMAND", "NODE", (MARKETPLACE,)),
    ("tracked-shell-lf-line-endings", range(476, 493), "INLINE_PYTHON_GUARD", "NODE", ()),
    ("installed-payload-self-contained", (569,), "SET_E_COMMAND", "NODE",
     ("scripts/check-installed-payload-self-contained.sh",)),
    ("scan-output-directory", (635,), "INLINE_GUARD", "NODE", ()),
    ("absent-root-behavior-source-direction", range(636, 645), "ABSENCE_SCAN", "NODE", ()),
    ("canonical-skill-source-documented", (646,), "INLINE_GUARD", "NODE", ()),
    ("absent-nonstandard-child-agent-filename", range(654, 658), "ABSENCE_SCAN", "NODE", ()),
    ("scan-output-cleanup", (658, 659), "SET_E_COMMAND", "NODE", ()),
)
DOCUMENTED_CLAIM_LINES = tuple(range(592, 620)) + tuple(range(661, 669))
CHILD_REPORT_LOOP = (439, 445, range(446, 455), 455, 456)  # header, do, section guards, field loop, field guard
MARKER_LOOP = (571, 588, 589)  # header, do, guard
CHECKER_AUXILIARY = (
    ("checker-auxiliary:repo-root-argument", (18,), "ARGUMENT_MODE", NO_ARGUMENTS),
    ("checker-auxiliary:python-available", (30,), "INTERPRETER_SELECTION", "NODE"),
)
NODE_EXIT_KINDS = {"TEST": "TEST_NODE_EXIT", "CHECK": "CHECK_NODE_EXIT",
                   "FINAL_CHECK": "FINAL_CHECK_EXIT", "TERMINAL": "TERMINAL_REPORT"}
COMPONENT_NORMALIZATION = ("PASS_REQUIRES_OBSERVED_NODE_PASS;OBSERVED_NODE_FAIL_UNATTRIBUTED_WITHIN_NODE_UNVERIFIED;"
                           "UNSETTLED_OR_INTERRUPTED_UNVERIFIED")
EXIT_NORMALIZATION = "PASS_IFF_OBSERVED_NODE_PASS;FAIL_IFF_OBSERVED_NODE_FAIL;UNSETTLED_OR_INTERRUPTED_UNVERIFIED"
ARGUMENT_NORMALIZATION = "INAPPLICABLE_REQUIRES_CANONICAL_ROUTE_WITHOUT_REGISTRY_ARGUMENTS"
JOIN_NORMALIZATION = ("PASS_REQUIRES_VERIFY_PASS_ALL_REQUIRED_SETTLED_SUCCESSOR_READY_AND_EVERY_OBSERVED_NODE_PASS;"
                      "FAIL_IFF_VERIFY_FAIL;OTHER_OUTCOMES_UNVERIFIED")
FIELD_GUARD = ('    grep -q "$field" "$child_report" || fail '
               '"child-agent report missing finding-format field \'$field\': $child_report"')
MARKER_GUARD = '  grep -R "$marker" -n skills >/dev/null || fail "missing transcript marker: $marker"'


def _classify(table, lines, tag):
    for line in lines:
        if line in table:
            raise ValueError(f"all-obligation prelude line {line} classified twice: {table[line]} and {tag}")
        table[line] = tag


def _section_pattern(line):
    call = re.fullmatch(r'  grep -q "([^"$]+)" "\$child_report" \|\| fail "[^"]*"', line)
    if call is None:
        raise ValueError("unsupported loop-expanded guard in canonical prelude")
    return call[1]


def _loop_values(text, header, do, name):
    if text[header - 1] != f"for {name} in \\" or text[do - 1] != "do":
        raise ValueError("unsupported loop header in canonical prelude")
    values = []
    for line in range(header + 1, do):
        value = re.fullmatch(r"  ([A-Za-z0-9._/:-]+)( \\)?", text[line - 1])
        if value is None or (value[2] is None) != (line == do - 1):
            raise ValueError("unsupported loop member in canonical prelude")
        values.append(value[1])
    return values


def _component_outcome(rule, status):
    if rule == NO_ARGUMENTS:
        return NO_ARGUMENTS, ARGUMENT_NORMALIZATION
    return ("PASS" if status == "PASS" else "UNVERIFIED"), COMPONENT_NORMALIZATION


def all_obligation_rows(source, mapping, observed, issue, existing, settlement):
    """Map every remaining registry obligation of the exact supported registry exactly once."""
    if mapping.get("registry_sha256") != ALL_OBLIGATION_REGISTRY:
        raise ValueError("all-obligation evidence requires the exact supported registry")
    if observed["command"] not in CANONICAL_COMMANDS:
        raise ValueError("all-obligation evidence requires the canonical route without registry arguments")
    nodes = mapping["nodes"]
    statuses = [(row["node"], row["status"]) for row in observed["nodes"]]
    if ([name for name, _ in statuses] != [row["id"] for row in nodes]
            or len({row["id"] for row in nodes}) != len(nodes)):
        raise ValueError("all-obligation observation does not cover the mapping nodes in order")
    status = dict(statuses)
    prelude, _, _ = canonical_prelude(mapping, observed)
    if prelude["byte_start"] != 0:
        raise ValueError("all-obligation prelude must start the registry")
    members = source["members"]
    registry_member = members.get(REGISTRY, {})
    if registry_member.get("sha256") != ALL_OBLIGATION_REGISTRY:
        raise ValueError("all-obligation source registry differs from the mapped registry")
    spans, line = [], 1
    for row in nodes:
        if row["byte_end"] <= row["byte_start"] or not row["source"].endswith("\n"):
            raise ValueError("all-obligation node span is not a whole-line registry span")
        last = line + row["source"].count("\n") - 1
        spans.append((row, list(range(line, last + 1))))
        line = last + 1
    text = prelude["source"].splitlines()
    rows = []

    def add(ident, node, lines, kind, outcome, normalization, paths=(), source_path=REGISTRY, **extra):
        rows.append({
            "id": ident, "outcome": outcome, "dispatch_id": issue["dispatch_id"], "node": node["id"],
            "obligation_kind": kind, "source_path": source_path, "source_lines": list(lines),
            "inputs": {REGISTRY: registry_member, "node_source_sha256": node["source_sha256"],
                       **{path: members.get(path, {"kind": "UNACQUIRED"}) for path in paths}},
            "requires": node["requires"], "environment_digest": node["environment_digest"],
            "writer_resource_constraint": node["writer_resource_constraint"],
            "evidence": node["evidence"], "observation": "RETAINED_CANONICAL_NODE_TERMINAL",
            "observed_node_status": status[node["id"]], "node_result_contract": node["result_contract"],
            "invalidators": ["task_input", *node["invalidators"], "node_trace"],
            "normalization": normalization, **extra,
        })

    # Classify every composed prelude line exactly once.
    table = {}
    existing_ids = [row["id"] for row in existing]
    if len(existing_ids) != len(set(existing_ids)):
        raise ValueError("all-obligation existing property rows are duplicated")
    for row in existing:
        if row["node"] == "PRELUDE":
            lines = row["source_lines"]
            if not row["id"].startswith("required-file:"):
                lines = range(lines[0], lines[1] + 1)
            _classify(table, lines, row["id"])
    for tag, lines in PRELUDE_STRUCTURE.items():
        _classify(table, lines, "structural:" + tag)
    _classify(table, [line for line in HEREDOC_SCAFFOLD if line not in table], "structural:heredoc-scaffold")
    prelude_status = status["PRELUDE"]
    for ident, lines, kind, rule, paths in PRELUDE_OBLIGATIONS:
        _classify(table, lines, ident)
        add(ident, prelude, lines, kind, *_component_outcome(rule, prelude_status), paths)
    outcome = _component_outcome("NODE", prelude_status)
    header, do, section_lines, field_loop, field_line = CHILD_REPORT_LOOP
    reports = _loop_values(text, header, do, "child_report")
    sections = [(line, _section_pattern(text[line - 1])) for line in section_lines]
    loop = re.fullmatch(r'  for field in ((?:"[^"$]+" ?)+); do', text[field_loop - 1])
    if loop is None or text[field_line - 1] != FIELD_GUARD:
        raise ValueError("unsupported field loop in canonical prelude")
    fields = re.findall(r'"([^"]+)"', loop[1])
    _classify(table, section_lines, "child-report-section-guards")
    _classify(table, (field_line,), "child-report-field-guards")
    for report in reports:
        for line, pattern in sections:
            add(f"child-report-section:{report}:{pattern}", prelude, (line,), "LOOP_EXPANDED_GUARD", *outcome,
                (report,), subject={"file": report, "pattern": pattern})
        for field in fields:
            add(f"child-report-field:{report}:{field}", prelude, (field_line,), "LOOP_EXPANDED_GUARD", *outcome,
                (report,), subject={"file": report, "pattern": field})
    header, do, guard = MARKER_LOOP
    markers = _loop_values(text, header, do, "marker")
    if text[guard - 1] != MARKER_GUARD:
        raise ValueError("unsupported transcript-marker guard in canonical prelude")
    _classify(table, (guard,), "transcript-marker-guards")
    for marker in markers:
        add("transcript-marker:" + marker, prelude, (guard,), "LOOP_EXPANDED_GUARD", *outcome,
            subject={"pattern": marker, "tree": "skills"})
    for line in DOCUMENTED_CLAIM_LINES:
        guard_text = text[line - 1]
        if not guard_text.startswith("grep ") or guard_text.count(" || fail ") != 1:
            raise ValueError("unsupported documented-claim guard in canonical prelude")
        _classify(table, (line,), f"documented-claim:L{line}")
        add(f"documented-claim:L{line}", prelude, (line,), "INLINE_GUARD", *outcome,
            subject={"guard": guard_text.split(" || fail ", 1)[1].strip()})
    for line, content in enumerate(text, 1):
        if line not in table and not content.strip():
            table[line] = "structural:blank"
    if sorted(table) != list(range(1, len(text) + 1)):
        raise ValueError("all-obligation classification does not cover every prelude line exactly once")

    # Every later node: auxiliary checker obligations, otherwise its own exit under its contract.
    checker_id = f"COMMAND:{CHECKER}:0"
    owned = {row["node"] for row in existing}
    for node, lines in spans[1:]:
        if node["id"] == checker_id:
            if checker_id not in owned:
                raise ValueError("all-obligation evidence requires the canonical checker property rows")
            for ident, checker_lines, kind, rule in CHECKER_AUXILIARY:
                add(ident, node, checker_lines, kind, *_component_outcome(rule, status[checker_id]),
                    (CHECKER,), source_path=CHECKER, registry_lines=lines)
            continue
        kind = NODE_EXIT_KINDS.get(node["kind"])
        if kind is None:
            raise ValueError("unsupported node kind for all-obligation evidence: " + str(node["kind"]))
        observed_status = status[node["id"]]
        exit_outcome = observed_status if observed_status in ("PASS", "FAIL") else "UNVERIFIED"
        command = node["command"]
        add("node-exit:" + node["id"], node, lines, kind, exit_outcome, EXIT_NORMALIZATION,
            (command,) if command in members else (), command=command)

    # Terminal semantics on the SETTLE JOIN.
    join, result = settlement["join"], settlement["result"]
    last = spans[-1][0]
    settled = (result["status"] == "PASS" and join["all_required_settled"] is True and not join["missing"]
               and settlement["successor"] == "READY" and all(value == "PASS" for value in status.values()))
    rows.append({
        "id": "terminal:settle-requires-all-registry-obligations",
        "outcome": "PASS" if settled else "FAIL" if result["status"] == "FAIL" else "UNVERIFIED",
        "dispatch_id": issue["dispatch_id"], "node": JOIN, "obligation_kind": "JOIN_SEMANTICS",
        "source_path": REGISTRY, "source_lines": [],
        "inputs": {REGISTRY: registry_member, "task_input_digest": issue["input_digest"],
                   "graph_digest": issue["graph_digest"]},
        "requires": join["required"], "settles_after": last["id"],
        "environment_digest": last["environment_digest"],
        "writer_resource_constraint": "SINGLE_COMPLETION_JOURNAL_WRITER",
        "evidence": ["completion_journal", "join_verdict", "successor_state"],
        "observation": "RETAINED_COMPLETION_JOIN", "observed_node_status": result["status"],
        "join_status": join["status"], "successor": settlement["successor"],
        "invalidators": ["task_input", "journal_history", "completion_digest", "node_trace"],
        "normalization": JOIN_NORMALIZATION,
    })

    ids = existing_ids + [row["id"] for row in rows]
    if len(ids) != len(set(ids)):
        raise ValueError("all-obligation rows duplicate an obligation")
    if {row["node"] for row in existing + rows} != {row["id"] for row in nodes} | {JOIN}:
        raise ValueError("all-obligation rows do not cover every mapping node")
    return rows


def task_status(exit_code):
    if exit_code < 0:
        return "INTERRUPTED"
    return "FAIL" if exit_code else "PASS"


def run_task(mode, output, *, include_version_prelude=False, include_required_files=False,
             include_all_obligations=False):
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
    if include_all_obligations and not (include_version_prelude and include_required_files):
        raise ValueError("all-obligation evidence requires version-prelude and required-file evidence")
    version = (4 if include_all_obligations else 3 if include_required_files
               else 2 if include_version_prelude else 1)
    if version >= 2:
        if checker is None:
            raise ValueError("version prelude evidence requires the supported registry checker")
        observation["version_prelude_inputs"] = version_prelude_inputs(source)
    if version >= 3:
        observation["required_file_properties"] = True
    if version == 4:
        if (observation["version_prelude_inputs"][REGISTRY]["sha256"] != ALL_OBLIGATION_REGISTRY
                or checker["inputs"][REGISTRY]["sha256"] != ALL_OBLIGATION_REGISTRY):
            raise ValueError("all-obligation evidence requires the exact supported registry")
        observation["all_obligation_properties"] = True
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
        if version >= 3:
            properties = required_file_rows(source, mapping, observed, issue) + properties
        receiver.accept(frontier, [result], JOIN, expected_old=issue["expected_old"])
        joined = receiver.join(JOIN, expected_old=receiver.history_digest)
        successor = receiver.frontier()["states"]["NEXT"]
        if version == 4:
            properties = properties + all_obligation_rows(
                source, mapping, observed, issue, properties,
                {"join": joined, "result": result, "successor": successor})
        schema, population = TASK_RECORD_SCOPES[version]
        record = {
            "schema": schema, "authority": "NONE",
            "issue": issue, "result": result, "join": joined, "nodes": observed["nodes"],
            "properties": properties, "property_population": population,
            "successor": successor,
        }
        (output / "task-result.json").write_bytes(encode(record) + b"\n")
        return record


def read_task_history(completion, directory, run_identity, decode):
    raw, _ = completion._read(directory / "journal" / "history.json", completion.MAX_JOURNAL_BYTES)
    history = decode(raw, "completion journal")
    require = completion._require
    require(type(history) is dict and set(history) == {"schema", "run_identity", "events"}
            and history["schema"] == "implementaudit.completion-history.v1"
            and history["run_identity"] == run_identity, "foreign or malformed completion journal")
    events = history["events"]
    require(type(events) is list and len(events) <= completion.MAX_EVENTS, "journal event bound")
    previous = None
    for event in events:
        require(type(event) is dict and set(event) == {"previous", "kind", "body", "digest"}
                and event["previous"] == previous
                and event["kind"] in {"BATCH", "JOIN"}, "journal chain or version mismatch")
        payload = {key: value for key, value in event.items() if key != "digest"}
        require(event["digest"] == completion._hash(payload), "journal digest mismatch")
        previous = event["digest"]
    return history


def verify_task_history(completion, qualifier, directory, observed, record, input_digest):
    """Compare the portable completion readback without opening a journal writer."""
    wg = qualifier.WG
    digest = completion._hash
    require = completion._require
    message = "retained capture does not match the declared task result"
    original_contract = str(Path(observed["execution_context"]["output"]).parent / "contract")
    run_identity = digest([original_contract, original_contract])
    history = read_task_history(completion, directory, run_identity, wg.decode_strict_json_bytes)
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
        if version >= 3:
            binding["required_file_properties"] = True
        if version == 4:
            binding["all_obligation_properties"] = True
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
        if version >= 3:
            expected_properties = required_file_rows(observed["before"], mapping, observed, issue) + expected_properties
        if version == 4:
            expected_properties = expected_properties + all_obligation_rows(
                observed["before"], mapping, observed, issue, expected_properties,
                {"join": record["join"], "result": record["result"], "successor": record["successor"]})
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
    parser.add_argument("--include-all-obligations", action="store_true")
    args = parser.parse_args()
    if args.include_all_obligations and not (args.include_version_prelude and args.include_required_files):
        parser.error("--include-all-obligations requires --include-version-prelude and --include-required-files")
    if args.mode == "compare" and (args.include_version_prelude or args.include_required_files
                                   or args.include_all_obligations):
        parser.error("compare reads the property evidence version from each retained run")
    if args.mode == "compare" and len(args.paths) == 3:
        return compare_tasks(*args.paths)
    if args.mode == "compare" or len(args.paths) != 1:
        parser.error("run takes a new output directory; compare takes legacy, DAG and new output directories")
    record = run_task(args.mode, args.paths[0], include_version_prelude=args.include_version_prelude,
                      include_required_files=args.include_required_files,
                      include_all_obligations=args.include_all_obligations)
    code = record["result"]["exit_code"]
    return code if code >= 0 else 128 - code


if __name__ == "__main__":
    sys.exit(main())
