"""Reproduce the exact R35-V01 verifier membership and M2 command-stream join."""

import ast
from collections import Counter
import copy
import hashlib
import io
import json
import pathlib
import re
import shlex
import subprocess
import sys
import tarfile
import zipfile


PRODUCT = "51416b2f156b341c4a5f09029e2c6ceb5b30b1e7"
TREE = "9c3913ceaa95f3f36b0377fe2dba4a302afcba89"
RESULTS = "6431a1d1e067ab37e4f461caa4a61890d69e7c14"
WORK_ORDER = "585012cbc6b47cb332222c2784481567a482c8a5"
RESULTS_ROOT = "handoff/pro-executor-results-20261115"
ROW_MAP = f"{RESULTS_ROOT}/continuing-execution-20261118-04/DG16_ORIGINAL48_CURRENT.json"
M2 = f"{RESULTS_ROOT}/continuing-execution-20261120-19/dg16-m2"
REGISTRY = "scripts/verify-package.sh"
OWNER = "skills/implementaudit/scripts/compile-work-graph.py"
FIRST = b"bash scripts/generate-readme-diagrams.sh --check\n"
TERMINAL = b"printf 'verify-package: ok\\n'\n"
FINAL = b"git diff --check\n"
BOUNDARY = re.compile(r"tests/[^/]+\.test\.sh\Z")
CONSTRUCTED_ENV = {"scope": "ORDINARY_SOURCE_ONLY_R35_V01_REDERIVATION"}


def require(condition, text):
    if not condition:
        raise ValueError(text)


def git(*args):
    return subprocess.check_output(["git", *args])


def blob(ref, path):
    return git("cat-file", "blob", f"{ref}:{path}")


def pin(raw):
    return {"bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}


def work_order():
    original = json.loads(blob(WORK_ORDER, "recovery/contracts/original/DEFINITIONS_48_20_117_12.json"))
    mapping = json.loads(blob(RESULTS, ROW_MAP))
    by_id = {x["id"]: (x["requirement_exact"], x["original_scope_and_binding_exact"])
             for x in original["original48"]}
    rows = {x["criterion_id"]: (x["original_text"], x["original_scope_and_binding"])
            for x in mapping["rows"]}
    require(len(mapping["rows"]) == len(by_id) == 48 and set(by_id) == set(rows), "original row universe")
    require(rows == by_id, "original source and scope literals differ")
    selected = next(row for row in mapping["rows"] if row["criterion_id"] == "R35-V01")
    require(selected["mandatory_operation_or_consumer_references"] == ["M2"]
            and selected["conditional_references"] == [] and selected["new_row_award"] is False,
            "R35-V01 original applicability")
    return {"id": "R35-V01", "literal": selected["original_text"],
            "scope": selected["original_scope_and_binding"], "mandatory": ["M2"],
            "conditional": [], "original_rows": len(rows)}


def compiler():
    raw = blob(PRODUCT, OWNER)
    tree = ast.parse(raw)
    names = {
        "WorkGraphError", "verifier_registered_tests_v1", "compile_verifier_graph_v1",
        "verifier_command_stream_v1", "_native_strings", "_require_string_array", "_require_string",
        "_require_object", "_validate_scalar_unicode", "validate_identity_json_v1",
        "canonical_json_v1", "_graph_hash", "_seal_graph", "_check_graph_seal",
    }
    constants = {"INT64_MIN", "INT64_MAX"}
    chosen = [node for node in tree.body if
              (isinstance(node, (ast.FunctionDef, ast.ClassDef)) and node.name in names)
              or (isinstance(node, ast.Assign) and len(node.targets) == 1
                  and isinstance(node.targets[0], ast.Name) and node.targets[0].id in constants)
              or (isinstance(node, ast.ImportFrom) and node.module == "__future__")]
    require(len(chosen) == len(names) + len(constants) + 1, "exact data-only compiler selection")
    ns = dict(re=re, shlex=shlex, hashlib=hashlib, copy=copy, json=json)
    exec(compile(ast.Module(body=chosen, type_ignores=[]), "<exact pure registry compiler>", "exec"), ns)
    return ns, pin(raw)


def physical_tests():
    tree_names = git("ls-tree", "-rz", "--name-only", PRODUCT, "--", "tests").decode().split("\0")
    paths = sorted(path for path in tree_names if BOUNDARY.fullmatch(path))
    physical = sorted(path.as_posix() for path in pathlib.Path("tests").glob("*.test.sh"))
    require(paths and paths == physical, "exact immutable/physical test population differs")
    for path in paths:
        actual = pathlib.Path(path)
        require(actual.is_file() and not actual.is_symlink() and actual.read_bytes() == blob(PRODUCT, path),
                f"actual test differs from exact product input: {path}")
    return paths


def lexical_census(registry):
    """Independent one-pass accounting of the actual registry's source spans."""
    require(registry.count(FIRST) == 1, "composed source boundary")
    at = registry.index(FIRST)
    spans = [("PRELUDE", "COMPOSED_PRELUDE", 0, at)]
    tail_pattern = re.compile(rb"bash ((?:scripts|tests)/[A-Za-z0-9_.-]+\.sh)(?:[ \t]|\n|$)")
    commands = Counter()
    length = at
    while length < len(registry):
        begin = length
        end = registry.index(b"\n", begin) + 1
        while registry[end - 2:end] == b"\\\n":
            end = registry.index(b"\n", end) + 1
        logical = registry[begin:end].replace(b"\\\n", b"")
        if not logical.strip():
            ident, kind, prior, _ = spans.pop()
            spans.append((ident, kind, prior, end))
        else:
            match = tail_pattern.match(logical)
            if match:
                command = match[1].decode()
                ident = f"COMMAND:{command}:{commands[command]}"
                commands[command] += 1
                kind = "TEST" if command.startswith("tests/") else "CHECK"
            elif logical == FINAL:
                ident, kind = "FINAL_DIFF", "FINAL_CHECK"
            elif logical == TERMINAL and end == len(registry):
                ident, kind = "TERMINAL", "TERMINAL"
            else:
                raise ValueError(f"independent census unaccounted tail at byte {begin}")
            spans.append((ident, kind, begin, end))
        length = end
    return spans


def compare_registry(source, graph, ns):
    spans = lexical_census(source)
    observed = [(node["id"], node["kind"], node["byte_start"], node["byte_end"])
                for node in graph["nodes"]]
    require(observed == spans, "independent ordered command/range census differs")
    stream = b""
    last = 0
    prior = None
    for row in graph["nodes"]:
        start, end = row["byte_start"], row["byte_end"]
        raw = source[start:end]
        require(start == last and end > start and raw == row["source"].encode()
                and pin(raw)["sha256"] == row["source_sha256"], "exact source coverage or pin")
        require(row["requires"] == ([prior] if prior else []), "legacy command order changed")
        stream += row["id"].encode() + b"\0" + raw + b"\0"
        last, prior = end, row["id"]
    require(last == graph["covered_bytes"] == len(source)
            and stream == ns["verifier_command_stream_v1"](graph, source), "exact command-stream reconstruction")
    return stream


def controls(ns, registry, graph, paths):
    compile_graph = ns["compile_verifier_graph_v1"]
    command_stream = ns["verifier_command_stream_v1"]
    observed = {}

    def expect_refusal(label, expected, call):
        try:
            call()
        except ns["WorkGraphError"] as error:
            require(expected in str(error), f"wrong refusal: {label}")
            observed[label] = str(error)
            return
        raise ValueError(f"false acceptance: {label}")

    def changed(source, population):
        revised = compile_graph(source, population, CONSTRUCTED_ENV)
        require(revised["digest"] != graph["digest"], "changed registry reused old identity")
        compare_registry(source, revised, ns)
        return revised

    added = "tests/v01-ordinary-census-probe.test.sh"
    require(added not in paths and b"\n" + FINAL in registry, "constructed addition precondition")
    source = registry.replace(b"\n" + FINAL, b"\nbash " + added.encode() + b"\n" + FINAL)
    revised = changed(source, sorted([*paths, added]))
    require(set(revised["test_nodes"]) == {*paths, added} and len(revised["nodes"]) == len(graph["nodes"]) + 1,
            "added obligation did not expand graph")
    observed["added_registered_and_derived"] = len(revised["nodes"])
    expect_refusal("added_but_physical_census_unchanged", "population mismatch",
                   lambda: compile_graph(source, paths, CONSTRUCTED_ENV))

    member = b"bash tests/phase-validation.test.sh\n"
    require(registry.count(member) == 1, "constructed deletion precondition")
    omitted = registry.replace(member, b"")
    revised = changed(omitted, [p for p in paths if p != "tests/phase-validation.test.sh"])
    require(len(revised["nodes"]) == len(graph["nodes"]) - 1, "deletion did not shrink graph")
    observed["removed_from_registry_and_census"] = len(revised["nodes"])
    expect_refusal("removed_registry_with_physical_member_remaining", "population mismatch",
                   lambda: compile_graph(omitted, paths, CONSTRUCTED_ENV))
    expect_refusal("same_count_foreign_registration", "population mismatch",
                   lambda: compile_graph(registry.replace(member, b"bash " + added.encode() + b"\n"),
                                         paths, CONSTRUCTED_ENV))
    expect_refusal("duplicate_registration", "duplicate test",
                   lambda: compile_graph(registry.replace(member, member * 2), paths, CONSTRUCTED_ENV))

    pair = re.search(rb"(?m)^(bash tests/[^\n]+\.test\.sh\n)(bash tests/[^\n]+\.test\.sh\n)", registry)
    require(pair is not None, "ordered test swap precondition")
    swapped = registry[:pair.start()] + pair[2] + pair[1] + registry[pair.end():]
    revised = changed(swapped, paths)
    require(revised["test_nodes"] == graph["test_nodes"] and len(revised["nodes"]) == len(graph["nodes"])
            and [n["id"] for n in revised["nodes"]] != [n["id"] for n in graph["nodes"]],
            "order-only change was lost")
    observed["same_membership_reorder_rederived"] = True
    expect_refusal("stale_graph_after_reorder", "stale registry", lambda: command_stream(graph, swapped))

    prelude = registry.replace(FIRST, b"# v01 in-memory byte-span control\n" + FIRST)
    revised = changed(prelude, paths)
    require(len(revised["nodes"]) == len(graph["nodes"])
            and revised["nodes"][0]["source_sha256"] != graph["nodes"][0]["source_sha256"],
            "prelude change was not bound")
    observed["opaque_prelude_change_rederived"] = True
    expect_refusal("registered_test_moved_to_prelude", "test hidden in composed prelude",
                   lambda: compile_graph(omitted.replace(FIRST, member + FIRST), paths, CONSTRUCTED_ENV))
    expect_refusal("unknown_tail", "unknown tail command",
                   lambda: compile_graph(registry.replace(FINAL, b":\n" + FINAL), paths, CONSTRUCTED_ENV))
    expect_refusal("missing_terminal_operation", "exact terminal operation required",
                   lambda: compile_graph(registry.removesuffix(TERMINAL), paths, CONSTRUCTED_ENV))
    return observed


def m2_records():
    index = json.loads(blob(RESULTS, f"{M2}/EVIDENCE_PARTS.json"))
    parts = []
    for row in index["parts"]:
        raw = blob(RESULTS, f"{M2}/{row['path']}")
        require(pin(raw) == {k: row[k] for k in ("bytes", "sha256")}, "exact M2 archive part")
        parts.append(raw)
    raw = b"".join(parts)
    require(pin(raw) == {k: index[k] for k in ("bytes", "sha256")}, "exact M2 archive")
    rows = json.loads(blob(RESULTS, f"{M2}/ARCHIVE_MEMBERS.json"))["members"]
    descriptors = {row["path"]: {k: row[k] for k in ("bytes", "sha256")} for row in rows}
    with tarfile.open(fileobj=io.BytesIO(raw), mode="r:gz") as archive:
        def read(name):
            members = [row for row in archive.getmembers() if row.name == name]
            require(len(members) == 1 and members[0].isfile(), f"ambiguous M2 archive member: {name}")
            value = archive.extractfile(members[0]).read()
            require(pin(value) == descriptors[name], f"exact M2 archive member: {name}")
            return value

        decision_raw = blob(RESULTS, f"{M2}/ROOT_ADJUDICATION.json")
        require(decision_raw == read("root/ROOT_ADJUDICATION.json"), "exact M2 decision duplicate")
        decision = json.loads(decision_raw)
        require(decision["disposition"] == "ACCEPTED_ORIGINAL_M2_FULL_CORRESPONDENCE_AT_EXACT_51416"
                and (decision["product_source"], decision["product_tree"]) == (PRODUCT, TREE)
                and decision["automatic_whole_row_awards"] == [], "M2 receiving scope")
        codec = read("closing/derivation/public_codec_exact.py")
        tree = ast.parse(codec)
        require(len(tree.body) == 1 and isinstance(tree.body[0], ast.FunctionDef)
                and tree.body[0].name == "public_codec", "bounded public decode source")
        public = {"json": json}
        exec(compile(tree, "<exact public M2 codec>", "exec"), public)
        probes = []
        for carrier, member_name, decoded_name, expected_rows, sha_key in (
            ("closing/received-final/ARTIFACT.zip", "PROBE.json", "closing/decoded-final/PROBE.json",
             7, "final_zip_sha256"),
            ("live/received/ARTIFACT.zip", "public/PROBE.json", "live/decoded/PROBE.json",
             9, "live_zip_sha256"),
        ):
            value = read(carrier)
            require(pin(value)["sha256"] == decision["public_evidence"][sha_key], "M2 provider ZIP identity")
            with zipfile.ZipFile(io.BytesIO(value)) as nz:
                require(len(nz.namelist()) == len(set(nz.namelist())) == expected_rows, "M2 ZIP census")
                encoded = nz.read(member_name)
                source_wire = nz.read(member_name.replace("PROBE.json", "SOURCE.json"))
            source_decoded = public["public_codec"]("SOURCE.json", source_wire, decode=True)
            require(source_decoded == json.loads(read(decoded_name.replace("PROBE.json", "SOURCE.json")))
                    and public["public_codec"]("SOURCE.json", source_decoded) == source_wire,
                    "exact M2 source body decode/round trip")
            decoded = public["public_codec"]("PROBE.json", encoded, decode=True)
            require(decoded == json.loads(read(decoded_name))
                    and public["public_codec"]("PROBE.json", decoded) == encoded, "M2 public body decode/round trip")
            probes.append(decoded)
        source = json.loads(read("closing/decoded-final/SOURCE.json"))
        require((source["commit"], source["tree"]) == (PRODUCT, TREE)
                and source["before"] == source["after"] and source["before"]["all_members_match"]
                and source["tracked_source_mutations"] is False, "M2 exact source bookends")
    return decision, probes, pin(decision_raw), pin(raw)


def join(physical, registry, graph, stream, probes):
    mapping = probes[0]["result"]["mapping"]
    physical_body = (json.dumps(physical, sort_keys=True, indent=2) + "\n").encode()
    records = []
    for probe in probes:
        require(all(probe[field] is True for field in ("currentness_before_pair", "currentness_after_pair",
                                                      "same_checkout_controller_discovered", "normal_receipt_verified")),
                "retained M2 currentness observations")
        result = probe["result"]
        require((result["source_commit"], result["source_tree"]) == (PRODUCT, TREE)
                and result["same_live_source_current"] is True and result["subject_verifier_attempts"] == 2,
                "M2 public actual input/source")
        require(result["mapping"] == mapping and mapping["exact_registry_reassembly"]
                and mapping["registered_tests"] == len(physical) and mapping["mapped_nodes"] == len(graph["nodes"])
                and mapping["physical_tests"] == pin(physical_body)
                and mapping["command_stream"] == pin(stream), "exact M2 observed input and command-stream join")
        relation = result["full_correspondence"]
        require(relation["registry_sha256"] == pin(registry)["sha256"]
                and relation["command_stream_sha256"] == pin(stream)["sha256"]
                and relation["registered_tests"] == len(physical)
                and relation["mapped_nodes"] == len(graph["nodes"]), "M2 required correspondence mapping")
        summary = [(r["mode"], r["registration_complete"], r["registry_sha256"], r["mapped_nodes"])
                   for r in result["records"]]
        require(summary == [(mode, True, pin(registry)["sha256"], len(graph["nodes"])) for mode in ("legacy", "dag")],
                "actual M2 paired census")
        for capture in result["records"]:
            legacy = capture["mode"] == "legacy"
            require(capture["exit"] == 0 and len(capture["nodes"]) == len(graph["nodes"])
                    and capture["legacy_node_trace"] == ("UNAVAILABLE_WHOLE_PROCESS_ONLY" if legacy else "NOT_APPLICABLE"),
                    "M2 capture scope")
            for ordinal, record in enumerate(capture["nodes"]):
                require(record == {"ordinal": ordinal, "status": "UNSETTLED" if legacy else "PASS",
                                   "terminal": not legacy}, "retained actual node-slot evidence changed")
        records.append(summary)
    return {"paired_mapping_consistent_in_live_and_final_public_artifacts": records[0] == records[1],
            "registered_physical_tests_descriptor": mapping["physical_tests"],
            "reported_full_mapping_descriptor": mapping["mapping"],
            "live_full_mapping_graph_independently_reconstructed": False,
            "source_command_stream_descriptor": mapping["command_stream"],
            "historical_before_and_after_currentness_observed": True,
            "retained_legacy_per_node_trace": "UNAVAILABLE_WHOLE_PROCESS_ONLY"}


def main():
    require(git("rev-parse", f"{PRODUCT}^{{tree}}").decode().strip() == TREE, "exact product tree")
    row = work_order()
    registry = blob(PRODUCT, REGISTRY)
    require(registry == pathlib.Path(REGISTRY).read_bytes(), "registry in tested worktree differs from Git subject")
    tests = physical_tests()
    ns, compiler_pin = compiler()
    graph = ns["compile_verifier_graph_v1"](registry, tests, CONSTRUCTED_ENV)
    require(set(graph["test_nodes"]) == set(tests), "exact complete registered test set")
    stream = compare_registry(registry, graph, ns)
    kinds = Counter(node["kind"] for node in graph["nodes"])
    require(graph["nodes"][0]["kind"] == "COMPOSED_PRELUDE"
            and registry[:graph["nodes"][0]["byte_end"]].count(b"<<'PY'") > 0
            and b"bash scripts/build-release-asset.sh --check-release-identity" in registry[:graph["nodes"][0]["byte_end"]]
            and graph["nodes"][-2]["id"] == "FINAL_DIFF" and graph["nodes"][-1]["id"] == "TERMINAL"
            and any(node["source"] == "bash scripts/build-release-asset.sh --check\n\n"
                    for node in graph["nodes"]), "prelude, final and build semantics protected")
    workflow = blob(PRODUCT, ".github/workflows/validate.yml")
    require(workflow == pathlib.Path(".github/workflows/validate.yml").read_bytes()
            and len(re.findall(rb"(?m)^\s*run: bash scripts/verify-package\.sh[ \t]*$", workflow)) == 1
            and not re.search(rb"(?m)^\s*(?:run: )?bash tests/[^\n]+\.test\.sh", workflow),
            "canonical CI registry source topology")
    checked = controls(ns, registry, graph, tests)
    historic = blob(PRODUCT, "test-support/work-graph-registry/original117/verify-package.sh")
    historic_paths = sorted(match[0].decode().split()[1] for match in
                            re.finditer(rb"(?m)^bash tests/[^\n]+?\.test\.sh(?=\s|$)", historic))
    historic_graph = ns["compile_verifier_graph_v1"](historic, historic_paths, CONSTRUCTED_ENV)
    compare_registry(historic, historic_graph, ns)
    decision, history, root_pin, archive_pin = m2_records()
    receiving = join(tests, registry, graph, stream, history)
    out = {
        "schema":"dg16.one-original-row.v01-source-m2-receiving.v1",
        "row":row, "product":{"commit":PRODUCT,"tree":TREE},
        "registry":pin(registry), "compiler":compiler_pin, "current_node_kinds":dict(kinds),
        "ci_registry_source_topology":{"workflow":pin(workflow),"direct_canonical_routes":1,
                                       "ci_outcome_claimed":False},
        "current_registered_tests":tests,
        "current_source_census":[{key:n[key] for key in ("id","kind","byte_start","byte_end","source_sha256")}
                                 for n in graph["nodes"]],
        "original_snapshot":{"registry":pin(historic),"nodes":len(historic_graph["nodes"]),
                             "registered_tests":len(historic_paths)},
        "source_model_controls":checked,
        "retained_m2":{"run":decision["run_id"],"job":decision["job_id"],"attempt":decision["attempt"],
                       "decision":root_pin,"published_archive":archive_pin,**receiving},
        "recommended_disposition":"ACCEPT_ORIGINAL_R35_V01_AT_EXACT_51416_POPULATION_SCOPE",
        "independent_root_receiving_pending":True,"new_original_awards":[],
        "registry_commands_executed":0,"m2_replay":False,"m6_credit":False,
    }
    sys.stdout.buffer.write((json.dumps(out, sort_keys=True, indent=2) + "\n").encode())


if __name__ == "__main__":
    main()
