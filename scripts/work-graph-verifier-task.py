#!/usr/bin/env python3
"""Run the canonical verifier under a live, task-owned completion contract."""
import argparse
import fnmatch
import hashlib
import importlib.util
import json
import os
from pathlib import Path, PurePosixPath
import re
import shlex
import stat
import subprocess
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
# rather than emitted with partial coverage. Loop expansions and the inputs read by
# grep guards are parsed from the canonical prelude source text; only line spans
# are tabulated here.
ALL_OBLIGATION_REGISTRY = "ea132140d64d2714f5a54356c4b79cd05dd2b32017c38cd2307115adc7ec6978"
NO_ARGUMENTS = "INAPPLICABLE_NO_ARGUMENTS_SUPPLIED"
CANONICAL_COMMANDS = (["bash", REGISTRY], ["bash", "scripts/run-work-graph-verifier.sh"])
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
# Input rules: "GREP" parses the files/directories the guard actually reads from its
# source line; "ABSENCE_SCAN" is a recursive scan of the whole candidate tree; "EXISTENCE"
# is a `[ -e ]` test; "GIT_INDEX" is a `git ls-files` query whose files are then read;
# "INTERPRETER" is the `command -v` selection; a path list binds members read directly.
# Recursive, existence and index scopes are bound by digest-bound read populations
# observed in the isolated checkout before and after the verifier occurrence.
PRELUDE_OBLIGATIONS = (
    # id, registry lines, obligation kind, outcome rule, input rule
    ("release-identity-arguments", range(19, 42), "ARGUMENT_MODE", NO_ARGUMENTS, ()),
    ("no-unknown-arguments", (42,), "ARGUMENT_GUARD", "NODE", ()),
    ("root-implementaudit-md-absent", range(48, 51), "INLINE_GUARD", "NODE", "EXISTENCE"),
    ("release-identity-build-and-check", range(66, 72), "CONDITIONAL_COMMANDS", NO_ARGUMENTS,
     ("scripts/build-release-asset.sh",)),
    ("child-agents-andon-registration-invariant", (460,), "INLINE_GUARD", "NODE", "GREP"),
    ("child-agents-false-green-rerun-rule", (461,), "INLINE_GUARD", "NODE", "GREP"),
    ("python-interpreter-available", range(463, 472), "INTERPRETER_SELECTION", "NODE", "INTERPRETER"),
    ("plugin-json-valid", (473,), "SET_E_COMMAND", "NODE", (PLUGIN,)),
    ("marketplace-json-valid", (474,), "SET_E_COMMAND", "NODE", (MARKETPLACE,)),
    ("tracked-shell-lf-line-endings", range(476, 493), "INLINE_PYTHON_GUARD", "NODE", "GIT_INDEX"),
    ("installed-payload-self-contained", (569,), "SET_E_COMMAND", "NODE",
     ("scripts/check-installed-payload-self-contained.sh",)),
    ("scan-output-directory", (635,), "INLINE_GUARD", "NODE", ()),
    ("absent-root-behavior-source-direction", range(636, 645), "ABSENCE_SCAN", "NODE", "ABSENCE_SCAN"),
    ("canonical-skill-source-documented", (646,), "INLINE_GUARD", "NODE", "GREP"),
    ("absent-nonstandard-child-agent-filename", range(654, 658), "ABSENCE_SCAN", "NODE", "ABSENCE_SCAN"),
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
EXIT_OUTCOMES = {"PASS": "PASS", "FAIL": "FAIL", "INTERRUPTED": "INTERRUPTED"}
COMPONENT_NORMALIZATION = ("PASS_REQUIRES_OBSERVED_COMPOSITE_PASS_AND_EVERY_READ_FILE_IDENTIFIED;"
                           "COMPOSITE_FAIL_OR_INTERRUPTION_UNATTRIBUTED_WITHIN_COMPOSITE_UNVERIFIED;"
                           "UNSETTLED_UNVERIFIED")
EXIT_NORMALIZATION = ("PASS_IFF_OBSERVED_NODE_PASS;FAIL_IFF_OBSERVED_NODE_FAIL;"
                      "INTERRUPTED_IFF_OBSERVED_NODE_INTERRUPTED;UNSETTLED_UNVERIFIED")
ARGUMENT_NORMALIZATION = "INAPPLICABLE_REQUIRES_CANONICAL_ROUTE_WITHOUT_REGISTRY_ARGUMENTS"
JOIN_NORMALIZATION = ("PASS_REQUIRES_VERIFY_PASS_ALL_REQUIRED_SETTLED_SUCCESSOR_READY_AND_EVERY_OBSERVED_NODE_PASS;"
                      "FAIL_IFF_VERIFY_FAIL;INTERRUPTED_IFF_VERIFY_INTERRUPTED;OTHER_OUTCOMES_UNVERIFIED")
UNBOUND_READ_REASON = ("no read population established before and after the occurrence; the Git-declared "
                       "member list alone leaves ignored entries unacquired, so the files read are not identified")
POPULATION_SCHEMA = "implementaudit.read-populations.v1"
POPULATION_SIDECAR = "read-populations.json"
POPULATION_MAX_ENTRIES = 50000
POPULATION_MAX_BYTES = 512 * 1024 * 1024
FIELD_GUARD = ('    grep -q "$field" "$child_report" || fail '
               '"child-agent report missing finding-format field \'$field\': $child_report"')
MARKER_GUARD = '  grep -R "$marker" -n skills >/dev/null || fail "missing transcript marker: $marker"'
COMPLETENESS_ACCEPTED = {"PASS", "INAPPLICABLE", NO_ARGUMENTS}


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


def _digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                     ensure_ascii=False).encode("utf-8")).hexdigest()


def _scope_id(descriptor):
    return descriptor["kind"].lower().replace("_", "-") + ":" + _digest(descriptor)[:16]


def _grep_descriptor(tokens):
    """Read population of one grep argv: operands, recursion, link behavior and exclusions."""
    descriptor = {"kind": "GREP_TREE", "recursive": False, "dereference": False,
                  "exclude_dir": [], "exclude": [], "include": [], "paths": []}
    operands, explicit_pattern, index = [], False, 0
    while index < len(tokens):
        token = tokens[index]
        if token == "-e":
            if index + 1 >= len(tokens):
                raise ValueError("unsupported grep guard in canonical prelude")
            explicit_pattern, index = True, index + 2
            continue
        option = re.fullmatch(r"--(exclude-dir|exclude|include)=(.+)", token)
        if option is not None:
            descriptor[option[1].replace("-", "_")].append(option[2])
        elif token.startswith("--"):
            raise ValueError("unsupported grep option in canonical prelude: " + token)
        elif token.startswith("-") and len(token) > 1:
            if set(token[1:]) - set("RrnIiq"):
                raise ValueError("unsupported grep option in canonical prelude: " + token)
            if "R" in token:
                descriptor.update(recursive=True, dereference=True)
            elif "r" in token:
                descriptor["recursive"] = True
        else:
            operands.append(token)
        index += 1
    paths = operands if explicit_pattern else operands[1:]
    if not paths or any("$" in path or path.startswith("/") or ".." in path.split("/") for path in paths):
        raise ValueError("unsupported grep guard operands in canonical prelude")
    descriptor["paths"] = paths
    return descriptor


def _grep_reads(command):
    """Return the read descriptor of the first grep of one guard line (a later pipe reads stdin)."""
    if " || fail " not in command:
        raise ValueError("unsupported grep guard in canonical prelude")
    first = command.strip().split(" || fail ", 1)[0].split(" | ", 1)[0]
    tokens = [token for token in shlex.split(first) if not token.startswith(">")]
    if not tokens or tokens[0] != "grep":
        raise ValueError("unsupported grep guard in canonical prelude")
    return _grep_descriptor(tokens[1:])


def _absence_reads(text, lines):
    if text[lines[-1] - 1].endswith("\\"):
        raise ValueError("unsupported absence scan in canonical prelude")
    tokens = shlex.split(" ".join(text[line - 1].rstrip("\\").strip() for line in lines))
    if tokens[:1] != ["require_absent_matches"] or len(tokens) < 3:
        raise ValueError("unsupported absence scan in canonical prelude")
    descriptor = _grep_descriptor(tokens[2:])
    if not descriptor["recursive"] or descriptor["paths"] != ["."]:
        raise ValueError("unsupported absence scan in canonical prelude")
    return descriptor


def _file_reads(paths):
    return {"kind": "GREP_TREE", "recursive": False, "dereference": False,
            "exclude_dir": [], "exclude": [], "include": [], "paths": list(paths)}


def _existence_reads(line):
    test = re.fullmatch(r"if \[ (-[ef]) ([A-Za-z0-9._/-]+) \]; then", line)
    if test is None:
        raise ValueError("unsupported existence test in canonical prelude")
    return {"kind": "EXISTENCE", "test": test[1], "path": test[2], "follows_symlinks": True}


def _git_index_reads(text, lines):
    calls = [re.search(r'\["git", "ls-files", "([^"]+)"\]', text[line - 1]) for line in lines]
    calls = [call for call in calls if call is not None]
    if len(calls) != 1 or "Path(path).is_file()" not in "\n".join(text[line - 1] for line in lines):
        raise ValueError("unsupported Git index query in canonical prelude")
    return {"kind": "GIT_INDEX_QUERY", "argv": ["git", "ls-files", calls[0][1]],
            "worktree_read": "IS_FILE_THEN_READ_BYTES_FOLLOWING_SYMLINKS"}


def required_read_scopes(prelude_source):
    """Every read population the canonical prelude requires, keyed by scope id."""
    text = prelude_source.splitlines()
    descriptors = []
    for _, lines, _, _, rule in PRELUDE_OBLIGATIONS:
        lines = list(lines)
        if rule == "GREP":
            descriptors.append(_grep_reads(text[lines[0] - 1]))
        elif rule == "ABSENCE_SCAN":
            descriptors.append(_absence_reads(text, lines))
        elif rule == "EXISTENCE":
            descriptors.append(_existence_reads(text[lines[0] - 1]))
        elif rule == "GIT_INDEX":
            descriptors.append(_git_index_reads(text, lines))
    descriptors.append(_grep_reads(text[MARKER_LOOP[2] - 1]))
    descriptors += [_grep_reads(text[line - 1]) for line in DOCUMENTED_CLAIM_LINES]
    return {_scope_id(item): item for item in descriptors
            if item["kind"] != "GREP_TREE" or item["recursive"]}


def _inside(root, path):
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def _hash_file(path, budget):
    digest, size = hashlib.sha256(), 0
    with open(path, "rb") as stream:
        while True:
            chunk = stream.read(1 << 20)
            if not chunk:
                break
            size += len(chunk)
            if size > budget:
                return None, size
            digest.update(chunk)
    return digest.hexdigest(), size


def observe_read_population(root, descriptor, *, max_entries=POPULATION_MAX_ENTRIES,
                            max_bytes=POPULATION_MAX_BYTES):
    """Identities (never content) of everything one read scope can read inside the checkout."""
    root = Path(root).resolve()
    entries, state = [], {"bytes": 0}

    class Stop(Exception):
        pass

    def stop(status):
        state["status"] = status
        raise Stop()

    def entry(relative, kind, path=None, **extra):
        if len(entries) >= max_entries:
            stop("EXCEEDED_BOUND")
        item = {"path": relative, "kind": kind, **extra}
        if path is not None:
            sha, size = _hash_file(path, max_bytes - state["bytes"])
            if sha is None:
                stop("EXCEEDED_BOUND")
            state["bytes"] += size
            item.update(bytes=size, sha256=sha)
        entries.append(item)

    def grep_walk(relative, command_line, visited):
        path = root / relative
        name = PurePosixPath(relative).name
        try:
            info = path.lstat()
        except FileNotFoundError:
            entry(relative, "MISSING")
            return
        linked = stat.S_ISLNK(info.st_mode)
        if linked and not (command_line or descriptor["dereference"]):
            return  # grep -r skips symbolic links met during recursion
        target = path.resolve() if linked else path
        if not _inside(root, target):
            stop("OUTSIDE_CHECKOUT")
        try:
            info = target.stat()
        except FileNotFoundError:
            entry(relative, "DANGLING_SYMLINK")
            return
        if stat.S_ISDIR(info.st_mode):
            if any(fnmatch.fnmatchcase(name, glob) for glob in descriptor["exclude_dir"]) and relative != ".":
                return
            if not descriptor["recursive"]:
                entry(relative, "DIRECTORY_NOT_READ")
                return
            key = (info.st_dev, info.st_ino)
            if key in visited:
                entry(relative, "DIRECTORY_CYCLE_SKIPPED")
                return
            for child in sorted(os.listdir(target)):
                grep_walk(child if relative == "." else relative + "/" + child, False, visited | {key})
        elif stat.S_ISREG(info.st_mode):
            if any(fnmatch.fnmatchcase(name, glob) for glob in descriptor["exclude"]):
                return
            if descriptor["include"] and not any(fnmatch.fnmatchcase(name, glob) for glob in descriptor["include"]):
                return
            # -I still opens and reads a file to classify it as binary, so it stays in the population.
            entry(relative, "SYMLINK_FILE" if linked else "FILE", target,
                  **({"target": target.relative_to(root).as_posix()} if linked else {}))
        else:
            stop("UNSUPPORTED_ENTRY")

    try:
        if descriptor["kind"] == "GREP_TREE":
            for relative in descriptor["paths"]:
                grep_walk(relative, True, frozenset())
        elif descriptor["kind"] == "EXISTENCE":
            path = root / descriptor["path"]
            exists = os.path.exists(path)  # [ -e ] follows symbolic links
            if exists and not _inside(root, path.resolve()):
                stop("OUTSIDE_CHECKOUT")
            entry(descriptor["path"], "EXISTS" if exists else "ABSENT",
                  path if exists and path.is_file() else None)
        elif descriptor["kind"] == "GIT_INDEX_QUERY":
            listed = subprocess.run(["git", "ls-files", "-s", "-z", "--", descriptor["argv"][2]], cwd=root,
                                    check=True, capture_output=True).stdout
            for record in filter(None, listed.split(b"\0")):
                meta, name = record.split(b"\t", 1)
                mode, blob, _ = meta.decode().split(" ")
                relative = os.fsdecode(name)
                path = root / relative
                if path.is_file() and not _inside(root, path.resolve()):
                    stop("OUTSIDE_CHECKOUT")
                entry(relative, "INDEXED_FILE" if path.is_file() else "INDEXED_NOT_A_FILE",
                      path if path.is_file() else None, index_mode=mode, blob=blob)
        else:
            stop("UNRECOGNIZED_SCOPE")
    except Stop:
        return {"status": state["status"], "entries": [], "entry_count": None, "bytes": None, "digest": None}
    return {"status": "BOUNDED", "entries": entries, "entry_count": len(entries), "bytes": state["bytes"],
            "digest": _digest([descriptor, entries])}


def observe_read_populations(root, scopes, **limits):
    return {scope: observe_read_population(root, descriptor, **limits) for scope, descriptor in scopes.items()}


def read_population_evidence(scopes, before, after):
    """Sidecar evidence: each scope's descriptor with its before/after populations."""
    return {"schema": POPULATION_SCHEMA, "authority": "NONE",
            "limits": {"max_entries": POPULATION_MAX_ENTRIES, "max_bytes": POPULATION_MAX_BYTES},
            "scopes": {scope: {"descriptor": descriptor, "before": before[scope], "after": after[scope]}
                       for scope, descriptor in scopes.items()}}


POPULATION_STOPS = {"EXCEEDED_BOUND", "OUTSIDE_CHECKOUT", "UNSUPPORTED_ENTRY", "UNRECOGNIZED_SCOPE"}
POPULATION_LIMITS = {"max_entries": POPULATION_MAX_ENTRIES, "max_bytes": POPULATION_MAX_BYTES}


def _bookend_consistent(descriptor, bookend):
    """A bookend counts only when its structure, digest, count and bytes rederive from its own entries."""
    if type(bookend) is not dict or set(bookend) != {"status", "entries", "entry_count", "bytes", "digest"}:
        return False
    entries = bookend["entries"]
    if bookend["status"] != "BOUNDED":
        return (bookend["status"] in POPULATION_STOPS and entries == []
                and bookend["entry_count"] is bookend["bytes"] is bookend["digest"] is None)
    if type(entries) is not list or len(entries) > POPULATION_MAX_ENTRIES:
        return False
    total = 0
    for item in entries:
        if (type(item) is not dict or type(item.get("path")) is not str or type(item.get("kind")) is not str
                or not set(item) - {"path", "kind"} <= {"bytes", "sha256", "target", "index_mode", "blob"}
                or ("bytes" in item) != ("sha256" in item)
                or any(type(item[key]) is not str for key in ("target", "index_mode", "blob") if key in item)):
            return False
        if "bytes" in item:
            if (type(item["bytes"]) is not int or item["bytes"] < 0 or type(item["sha256"]) is not str
                    or re.fullmatch(r"[0-9a-f]{64}", item["sha256"]) is None):
                return False
            total += item["bytes"]
    return (bookend["entry_count"] == len(entries) and type(bookend["entry_count"]) is int
            and bookend["bytes"] == total and type(bookend["bytes"]) is int and total <= POPULATION_MAX_BYTES
            and bookend["digest"] == _digest([descriptor, entries]))


def summarize_read_populations(evidence, evidence_sha256):
    scopes = {}
    limits = evidence.get("limits") == POPULATION_LIMITS
    for scope, item in evidence["scopes"].items():
        before, after = item["before"], item["after"]
        if scope != _scope_id(item["descriptor"]):
            status = "UNRECOGNIZED_SCOPE"
        elif not (limits and _bookend_consistent(item["descriptor"], before)
                  and _bookend_consistent(item["descriptor"], after)):
            status = "INCONSISTENT_BOOKEND"
        elif before["status"] != "BOUNDED":
            status = before["status"]
        elif after["status"] != "BOUNDED":
            status = after["status"]
        elif before["digest"] != after["digest"]:
            status = "DRIFT_DURING_OCCURRENCE"
        else:
            status = "ESTABLISHED"
        scopes[scope] = {"status": status, "digest": after["digest"] if status == "ESTABLISHED" else None,
                         "entry_count": after["entry_count"] if status == "ESTABLISHED" else None}
    return {"sidecar": POPULATION_SIDECAR, "sha256": evidence_sha256, "scopes": scopes}


def property_completeness(rows, read_populations=None):
    """Coverage verdict of the property rows; independent of the VERIFY/SETTLE decision."""
    outcomes = {}
    for row in rows:
        outcomes[row["outcome"]] = outcomes.get(row["outcome"], 0) + 1
    scoped = [row["read_scope"] for row in rows if "read_scope" in row]
    unbound = sum(scope["status"].startswith("UNVERIFIED") for scope in scoped)
    unestablished = sorted({scope["scope"] for scope in scoped
                            if scope["status"].startswith("UNVERIFIED") and "scope" in scope})
    referenced = {scope["scope"] for scope in scoped if "scope" in scope}
    unrecognized = sorted(set((read_populations or {}).get("scopes", {})) - referenced)
    rejected = {key: value for key, value in outcomes.items() if key not in COMPLETENESS_ACCEPTED}
    if any(key in ("FAIL", "INTERRUPTED") for key in rejected):
        verdict = "INCOMPLETE_FAILED_ROWS"
    elif rejected:
        verdict = "INCOMPLETE_UNVERIFIED_ROWS"
    elif unbound:
        verdict = "INCOMPLETE_UNVERIFIED_READ_SCOPE"
    elif unrecognized:
        verdict = "INCOMPLETE_UNRECOGNIZED_READ_SCOPE"
    else:
        verdict = "COMPLETE"
    return {"verdict": verdict, "rows": len(rows), "outcomes": dict(sorted(outcomes.items())),
            "inapplicable_rows": sum(value for key, value in outcomes.items() if key.startswith("INAPPLICABLE")),
            "not_accepted_rows": sum(rejected.values()), "unverified_read_scope_rows": unbound,
            "unestablished_scopes": unestablished, "unrecognized_scopes": unrecognized,
            "rule": "COMPLETE_REQUIRES_EVERY_ROW_PASS_OR_JUSTIFIED_INAPPLICABLE_AND_EVERY_REQUIRED_READ_SCOPE_"
                    "ESTABLISHED_BEFORE_AND_AFTER_THE_OCCURRENCE"}


def all_obligation_rows(source, mapping, observed, issue, existing, settlement, read_populations=None):
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
    checker_id = f"COMMAND:{CHECKER}:0"
    rows = []

    summary = (read_populations or {}).get("summary", {}).get("scopes", {})
    evidence = (read_populations or {}).get("evidence", {}).get("scopes", {})
    environment = observed.get("environment")

    def population(descriptor):
        scope = _scope_id(descriptor)
        observed_scope = summary.get(scope)
        status = observed_scope["status"] if observed_scope else "MISSING_READ_POPULATION"
        if status != "ESTABLISHED":
            return scope, None, {"status": "UNVERIFIED_READ_POPULATION_" + status, "scope": scope,
                                 "reason": UNBOUND_READ_REASON}
        return scope, evidence[scope]["after"]["entries"], {
            "status": "ESTABLISHED_BOUNDED_POPULATION", "scope": scope,
            "population_digest": observed_scope["digest"], "entry_count": observed_scope["entry_count"],
            "sidecar": POPULATION_SIDECAR}

    def bind_reads(descriptor):
        """Bind each read operand; recursive scopes reference their digest-bound population."""
        bound, missing, entries, scope = {}, [], None, None
        if descriptor["kind"] == "GREP_TREE" and descriptor["recursive"]:
            _, entries, scope = population(descriptor)
        index = {item["path"]: item for item in entries or ()}
        for path in descriptor["paths"]:
            item = index.get(path)
            member = members.get(path)
            if item is not None and item["kind"] in ("FILE", "SYMLINK_FILE"):
                bound[path] = {"kind": item["kind"], "bytes": item["bytes"], "sha256": item["sha256"],
                               "acquired_by": "READ_POPULATION"}
            elif item is not None:
                bound[path] = {"kind": item["kind"], "acquired_by": "READ_POPULATION"}
                missing.append(path)
            elif entries is not None:
                pass  # a directory operand: its files are the population entries
            elif member is not None and member.get("kind") == "FILE":
                bound[path] = member
            elif descriptor["recursive"] and any(name.startswith("" if path == "." else path.rstrip("/") + "/")
                                                 for name in members):
                pass  # a directory operand without an established population: scope stays unverified
            else:
                bound[path] = member if member is not None else {"kind": "UNACQUIRED"}
                missing.append(path)
        if scope is None:
            scope = {"status": "BOUND_FILES", "paths": sorted(bound)}
        else:
            scope = dict(scope, paths=descriptor["paths"], bound_files=sorted(bound))
        return bound, scope, missing

    def interpreter_scope():
        resolution = (environment or {}).get("child_python_resolution")
        argv = (resolution or {}).get("external_fallback_argv")
        if not argv:
            return {"status": "UNVERIFIED_INTERPRETER_RESOLUTION",
                    "reason": "no observed child-environment python resolution"}, True
        executable = environment["executables"][argv[0]]
        return {"status": "ESTABLISHED_ENVIRONMENT_RESOLUTION", "selected_argv": argv,
                "executable": {key: executable[key] for key in ("resolved_path", "mode", "bytes", "sha256")},
                "order": ["python", "python3", "py"]}, False

    def composite_id(node):
        return "composite-observation:" + node["id"]

    def add(ident, node, lines, kind, outcome, normalization, paths=(), source_path=REGISTRY,
            reads=None, probe=None, composite=True, **extra):
        inputs = {REGISTRY: registry_member, "node_source_sha256": node["source_sha256"]}
        missing = []
        for path in paths:
            inputs[path] = members.get(path, {"kind": "UNACQUIRED"})
            if inputs[path].get("kind") != "FILE":
                missing.append(path)
        scope = None
        if reads is not None:
            bound, scope, unread = bind_reads(reads)
            inputs.update(bound)
            missing += unread
        contradiction = False
        if probe == "INTERPRETER":
            scope, contradiction = interpreter_scope()
        elif probe is not None:
            _, entries, scope = population(probe)
            if entries is not None and probe["kind"] == "EXISTENCE":
                contradiction = entries[0]["kind"] != "ABSENT"
                inputs[probe["path"]] = entries[0]
        if (missing or contradiction) and outcome == "PASS":
            outcome = "UNVERIFIED"
        row = {
            "id": ident, "outcome": outcome, "dispatch_id": issue["dispatch_id"], "node": node["id"],
            "obligation_kind": kind, "source_path": source_path, "source_lines": list(lines),
            "inputs": inputs, "requires": node["requires"], "environment_digest": node["environment_digest"],
            "writer_resource_constraint": node["writer_resource_constraint"],
            "evidence": node["evidence"], "observation": "RETAINED_CANONICAL_NODE_TERMINAL",
            "observed_node_status": status[node["id"]], "node_result_contract": node["result_contract"],
            "invalidators": ["task_input", *node["invalidators"], "node_trace"],
            "normalization": normalization, **extra,
        }
        if missing:
            row["missing_inputs"] = missing
        if scope is not None:
            row["read_scope"] = scope
        if contradiction:
            row["observed_contradiction"] = True
        if composite:
            row["composite"] = {"observation": composite_id(node), "observed_exit": status[node["id"]]}
        rows.append(row)

    def component(rule, node_status):
        if rule == NO_ARGUMENTS:
            return NO_ARGUMENTS, ARGUMENT_NORMALIZATION
        return ("PASS" if node_status == "PASS" else "UNVERIFIED"), COMPONENT_NORMALIZATION

    def composite(node, lines, members_before):
        observed_status = status[node["id"]]
        member_ids = members_before + [row["id"] for row in rows
                                       if row.get("composite", {}).get("observation") == composite_id(node)]
        rows.append({
            "id": composite_id(node), "outcome": EXIT_OUTCOMES.get(observed_status, "UNVERIFIED"),
            "dispatch_id": issue["dispatch_id"], "node": node["id"], "obligation_kind": "COMPOSITE_NODE_EXIT",
            "source_path": REGISTRY, "source_lines": lines,
            "inputs": {REGISTRY: registry_member, "node_source_sha256": node["source_sha256"]},
            "requires": node["requires"], "environment_digest": node["environment_digest"],
            "writer_resource_constraint": node["writer_resource_constraint"],
            "evidence": node["evidence"], "observation": "RETAINED_CANONICAL_NODE_TERMINAL",
            "observed_node_status": observed_status, "node_result_contract": node["result_contract"],
            "invalidators": ["task_input", *node["invalidators"], "node_trace"],
            "normalization": EXIT_NORMALIZATION, "members": member_ids,
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
    for ident, lines, kind, rule, inputs in PRELUDE_OBLIGATIONS:
        _classify(table, lines, ident)
        reads = (_grep_reads(text[lines[0] - 1]) if inputs == "GREP"
                 else _absence_reads(text, list(lines)) if inputs == "ABSENCE_SCAN" else None)
        probe = ("INTERPRETER" if inputs == "INTERPRETER"
                 else _existence_reads(text[lines[0] - 1]) if inputs == "EXISTENCE"
                 else _git_index_reads(text, list(lines)) if inputs == "GIT_INDEX" else None)
        add(ident, prelude, lines, kind, *component(rule, prelude_status),
            inputs if type(inputs) is tuple else (), reads=reads, probe=probe)
    outcome = component("NODE", prelude_status)
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
                reads=_file_reads([report]), subject={"file": report, "pattern": pattern})
        for field in fields:
            add(f"child-report-field:{report}:{field}", prelude, (field_line,), "LOOP_EXPANDED_GUARD", *outcome,
                reads=_file_reads([report]), subject={"file": report, "pattern": field})
    header, do, guard = MARKER_LOOP
    markers = _loop_values(text, header, do, "marker")
    if text[guard - 1] != MARKER_GUARD:
        raise ValueError("unsupported transcript-marker guard in canonical prelude")
    _classify(table, (guard,), "transcript-marker-guards")
    for marker in markers:
        add("transcript-marker:" + marker, prelude, (guard,), "LOOP_EXPANDED_GUARD", *outcome,
            reads=_grep_reads(text[guard - 1]), subject={"pattern": marker, "tree": "skills"})
    for line in DOCUMENTED_CLAIM_LINES:
        guard_text = text[line - 1]
        if not guard_text.startswith("grep ") or guard_text.count(" || fail ") != 1:
            raise ValueError("unsupported documented-claim guard in canonical prelude")
        _classify(table, (line,), f"documented-claim:L{line}")
        add(f"documented-claim:L{line}", prelude, (line,), "INLINE_GUARD", *outcome,
            reads=_grep_reads(guard_text), subject={"guard": guard_text.split(" || fail ", 1)[1].strip()})
    for line, content in enumerate(text, 1):
        if line not in table and not content.strip():
            table[line] = "structural:blank"
    if sorted(table) != list(range(1, len(text) + 1)):
        raise ValueError("all-obligation classification does not cover every prelude line exactly once")
    composite(prelude, spans[0][1], [row["id"] for row in existing if row["node"] == "PRELUDE"])

    # Every later node: the checker is a composite with auxiliary obligations; any other
    # node's registry obligation is its own exit under its contract.
    owned = {row["node"] for row in existing}
    for node, lines in spans[1:]:
        if node["id"] == checker_id:
            if checker_id not in owned:
                raise ValueError("all-obligation evidence requires the canonical checker property rows")
            for ident, checker_lines, kind, rule in CHECKER_AUXILIARY:
                add(ident, node, checker_lines, kind, *component(rule, status[checker_id]),
                    (CHECKER,), source_path=CHECKER, registry_lines=lines,
                    probe="INTERPRETER" if kind == "INTERPRETER_SELECTION" else None)
            composite(node, lines, [row["id"] for row in existing if row["node"] == checker_id])
            continue
        kind = NODE_EXIT_KINDS.get(node["kind"])
        if kind is None:
            raise ValueError("unsupported node kind for all-obligation evidence: " + str(node["kind"]))
        command = node["command"]
        add("node-exit:" + node["id"], node, lines, kind, EXIT_OUTCOMES.get(status[node["id"]], "UNVERIFIED"),
            EXIT_NORMALIZATION, (command,) if command in members else (), composite=False, command=command)

    # Terminal semantics on the SETTLE JOIN: exactly what VERIFY/SETTLE/READY decided.
    join, result = settlement["join"], settlement["result"]
    last = spans[-1][0]
    settled = (result["status"] == "PASS" and join["all_required_settled"] is True and not join["missing"]
               and settlement["successor"] == "READY" and all(value == "PASS" for value in status.values()))
    rows.append({
        "id": "terminal:settle-join",
        "outcome": "PASS" if settled else {"FAIL": "FAIL", "INTERRUPTED": "INTERRUPTED"}.get(
            result["status"], "UNVERIFIED"),
        "dispatch_id": issue["dispatch_id"], "node": JOIN, "obligation_kind": "JOIN_SEMANTICS",
        "source_path": REGISTRY, "source_lines": [],
        "inputs": {REGISTRY: registry_member, "task_input_digest": issue["input_digest"],
                   "graph_digest": issue["graph_digest"]},
        "requires": join["required"], "settles_after": last["id"],
        "environment_digest": last["environment_digest"],
        "writer_resource_constraint": "SINGLE_COMPLETION_JOURNAL_WRITER",
        "evidence": ["completion_journal", "join_verdict", "successor_state", "raw_capture_result"],
        "observation": "RETAINED_COMPLETION_JOIN", "observed_node_status": result["status"],
        "task_exit_code": result["exit_code"], "task_evidence_digest": result["evidence_digest"],
        "join_status": join["status"], "successor": settlement["successor"],
        "invalidators": ["task_input", "journal_history", "completion_digest", "node_trace"],
        "normalization": JOIN_NORMALIZATION,
    })

    referenced = {row["read_scope"]["scope"] for row in rows if "scope" in row.get("read_scope", {})}
    if referenced != set(required_read_scopes(prelude["source"])):
        raise ValueError("all-obligation rows do not reference exactly the required read scopes")
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
        registry_bytes = (qualifier.ROOT / REGISTRY).read_bytes()
        compiled = qualifier.WG.compile_verifier_graph_v1(
            registry_bytes, qualifier.WG.verifier_registered_tests_v1(registry_bytes), {})
        read_scopes = required_read_scopes(compiled["nodes"][0]["source"])
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
        if version == 4:
            populations_before = observe_read_populations(qualifier.ROOT, read_scopes)
        wrapper_exit = qualifier.run(mode, capture, empty_stdin=True)
        if version == 4:
            populations_after = observe_read_populations(qualifier.ROOT, read_scopes)
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
            if mapping["nodes"][0]["source"] != compiled["nodes"][0]["source"]:
                raise ValueError("read scopes were derived from a different canonical prelude")
            evidence_bytes = encode(read_population_evidence(read_scopes, populations_before,
                                                             populations_after)) + b"\n"
            (output / POPULATION_SIDECAR).write_bytes(evidence_bytes)
            evidence = qualifier.WG.decode_strict_json_bytes(evidence_bytes, "read populations")
            summary = summarize_read_populations(evidence, qualifier.sha(evidence_bytes))
            properties = properties + all_obligation_rows(
                source, mapping, observed, issue, properties,
                {"join": joined, "result": result, "successor": successor},
                {"summary": summary, "evidence": evidence})
        schema, population = TASK_RECORD_SCOPES[version]
        record = {
            "schema": schema, "authority": "NONE",
            "issue": issue, "result": result, "join": joined, "nodes": observed["nodes"],
            "properties": properties, "property_population": population,
            "successor": successor,
        }
        if version == 4:
            record["read_populations"] = summary
            record["property_completeness"] = property_completeness(properties, summary)
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
        v4_fields = {"property_completeness", "read_populations"}
        if (type(record) is not dict or set(record) - v4_fields != fields
                or (set(record) & v4_fields == v4_fields) != (record.get("schema") == TASK_RECORD_SCOPES[4][0])
                or (set(record) & v4_fields) not in (set(), v4_fields)
                or type(issue) is not dict
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
            evidence_bytes = (directory / POPULATION_SIDECAR).read_bytes()
            evidence = qualifier.WG.decode_strict_json_bytes(evidence_bytes, "read populations")
            summary = summarize_read_populations(evidence, qualifier.sha(evidence_bytes))
            if (type(evidence) is not dict or evidence.get("schema") != POPULATION_SCHEMA
                    or encode(record["read_populations"]) != encode(summary)):
                raise ValueError(message)
            expected_properties = expected_properties + all_obligation_rows(
                observed["before"], mapping, observed, issue, expected_properties,
                {"join": record["join"], "result": record["result"], "successor": record["successor"]},
                {"summary": summary, "evidence": evidence})
        if record["property_population"] != population or encode(record["properties"]) != encode(expected_properties):
            raise ValueError(message)
        if version == 4 and encode(record["property_completeness"]) != encode(
                property_completeness(expected_properties, record["read_populations"])):
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
