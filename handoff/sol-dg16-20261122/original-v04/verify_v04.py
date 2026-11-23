"""Read-only V04 receipt census plus pure interrupted-prefix shape proof."""

import ast
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import types


HERE = Path(__file__).parent
CI_JOB = 136022135798
CI_RUN = 44655969487
CI_LOG = {"bytes": 569919, "sha256": "7d58c311832168a01e8dc12841d4b770bd16a1873e63a7063ecc0d64f962b893"}
MARKERS = (
    "work-graph-verifier: explicit v3 partial artifacts, child environment and retained stdin consumed",
    "work-graph-verifier: complete registry byte partition; positive/fail-fast raw streams and exit match",
    "work-graph-verifier.test: ok",
)


def imported_v01():
    spec = importlib.util.spec_from_file_location("v01_retained", HERE.parent / "original-v01" / "verify_v01.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def literal_row(v):
    old = json.loads(v.blob(v.WORK_ORDER, "recovery/contracts/original/DEFINITIONS_48_20_117_12.json"))
    mapping = json.loads(v.blob(v.RESULTS, v.ROW_MAP))
    spec = next(r for r in old["original48"] if r["id"] == "R35-V04")
    retained = next(r for r in mapping["rows"] if r["criterion_id"] == "R35-V04")
    v.require(spec["requirement_exact"] == retained["original_text"]
              and spec["original_scope_and_binding_exact"] == retained["original_scope_and_binding"]
              and retained["mandatory_operation_or_consumer_references"] == ["M2"]
              and retained["conditional_references"] == [] and len(old["original48"]) == 48,
              "exact original V04 contract and applicability")
    return {"id": "R35-V04", "literal": spec["requirement_exact"],
            "scope": spec["original_scope_and_binding_exact"], "original_rows": 48}


def retained_markers(v):
    root = "repos/theislampill/IMPLEMENTAUDIT.md"
    job = json.loads(subprocess.check_output(["gh", "api", f"{root}/actions/jobs/{CI_JOB}"]))
    v.require((job["head_sha"], job["run_id"], job["run_attempt"]) == (v.PRODUCT, CI_RUN, 1),
              "exact provider verifier job")
    step = next(s for s in job["steps"] if s["number"] == 10)
    v.require(step["name"] == "Verify package contract" and step["conclusion"] == "success", "actual CI step")
    raw = subprocess.check_output(["gh", "api", f"{root}/actions/jobs/{CI_JOB}/logs"])
    v.require(v.pin(raw) == CI_LOG, "raw exact CI log")
    rows = raw.decode().splitlines()
    positions = {}
    for marker in MARKERS:
        coordinate, = [nr for nr, line in enumerate(rows, 1) if line.endswith(" " + marker)]
        positions[marker] = coordinate
    v.require(list(positions.values()) == sorted(positions.values()), "marker order")
    names = (
        "scripts/verify-package.sh", "tests/work-graph-verifier.test.sh",
        "tests/work-graph-verifier-cases.py", "tests/work-graph-prefix-cases.py",
        "tests/work-graph-completion-cases.py", "scripts/qualify-work-graph-verifier.py",
    )
    files = {n: v.blob(v.PRODUCT, n) for n in names}
    registry, entry, tests = (files[name] for name in names[:3])
    v.require(registry.count(b"\nbash tests/work-graph-verifier.test.sh\n") == 1
              and b"set -euo pipefail\n" in entry
              and b'"${py_cmd[@]}" tests/work-graph-verifier-cases.py' in entry
              and all(marker.encode() in tests for marker in MARKERS), "exact canonical source-to-test linkage")
    adj = {
        "test_timeout_and_interruption_keep_actual_owned_child_exit": "tests/work-graph-prefix-cases.py",
        "test_supplied_join_pass_cannot_override_nonverdict": "tests/work-graph-completion-cases.py",
    }
    adjacent = {}
    for name, path in adj.items():
        v.require(name.encode() in files[path], "adjacent retained source case")
        adjacent[name] = {"source": path, "individual_log_marker_lines":
                          [i for i, line in enumerate(rows, 1) if name in line],
                          "same_as_complete_current_verifier_capture": False}
    return {"run": CI_RUN, "job": CI_JOB, "exact_step": step, "log": v.pin(raw), "markers": positions,
            "source_pins": {name: v.pin(value) for name, value in files.items()},
            "adjacent_source_controls": adjacent}, files[names[-1]]


def pure_trace(v, raw, nodes):
    tree = ast.parse(raw)
    bodies = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in {"trace_nodes", "valid_nodes"}]
    v.require(len(bodies) == 2, "exact pure received-status reducers")
    owner, _ = v.compiler()
    ns = {"WG": types.SimpleNamespace(WorkGraphError=owner["WorkGraphError"])}
    exec(compile(ast.Module(body=bodies, type_ignores=[]), "<exact data-only trace reducers>", "exec"), ns)
    graph = {"nodes": [{"id": n["id"]} for n in nodes]}
    names = [n["id"] for n in nodes]
    prefix = b"".join(key.encode() + b"\t" + state for key, state in
                      ((names[0], b"START\n"), (names[0], b"PASS\n"), (names[1], b"START\n")))
    outcomes = {}
    for code, wanted in ((9, "FAIL"), (-15, "INTERRUPTED")):
        record = ns["trace_nodes"](graph, "dag", code, prefix)
        v.require(ns["valid_nodes"](record, names, "dag", code)
                  and [(r["status"], r["terminal"]) for r in record] ==
                  [("PASS", True), (wanted, True), ("UNSETTLED", False)], "outcome separation")
        outcomes[str(code)] = [r["status"] for r in record]
    try:
        ns["trace_nodes"](graph, "dag", 0, prefix)
    except owner["WorkGraphError"] as error:
        v.require(str(error) == "successful verifier has incomplete node trace", "same prefix success refusal")
        refused = str(error)
    else:
        raise ValueError("incomplete prefix promoted to success")
    legacy = ns["trace_nodes"](graph, "legacy", 0, None)
    v.require(all(r["status"] == "UNSETTLED" and not r["terminal"] for r in legacy),
              "legacy whole process success does not synthesize per-node status")
    return {"ordinary_status_inputs_only": True, "results_by_exit": outcomes,
            "same_incomplete_prefix_with_zero_exit_refused": refused,
            "legacy_without_node_trace_all_unsettled": True,
            "actual_interrupted_subject_capture_received_here": False}


def main():
    v = imported_v01()
    prior = (HERE.parent / "original-v01" / "V01_EVIDENCE.json").read_bytes()
    v.require(v.pin(prior)["sha256"] == "41bb6794af7a31656d193cfc95bc97c48c078b19a484d38491ab0e23eef3d913",
              "exact previously received census")
    current = json.loads(prior)["current_source_census"]
    evidence, reducer = retained_markers(v)
    decision, probes, decision_pin, archive_pin = v.m2_records()
    v.require(all(p["result_disposition"] == "RECEIVED_COMPLETE_RAW_PAIR" for p in probes)
              and all([(r["mode"], r["exit"], r["legacy_node_trace"]) for r in p["result"]["records"]] ==
                      [("legacy", 0, "UNAVAILABLE_WHOLE_PROCESS_ONLY"), ("dag", 0, "NOT_APPLICABLE")]
                      for p in probes), "M2 evidence ceiling")
    result = {
        "schema": "dg16.original-v04.retained-control-disposition.v1",
        "row": literal_row(v), "product": {"commit": v.PRODUCT, "tree": v.TREE},
        "actual_CI_controls": evidence,
        "pure_trace_control": pure_trace(v, reducer, current[:3]),
        "retained_M2_scope": {"run": decision["run_id"], "archive": archive_pin, "decision": decision_pin,
                              "reported_verifier_exits": [0, 0],
                              "actual_interrupted_receipt_supplied": False},
        "original_conjunction": {
            "missing_duplicate_unknown_reordered_stale_falsely_settled":
                "ACCEPT_BOUNDED_EXACT_SOURCE_CONTROL_SCOPE",
            "nonzero_and_legacy_fail_fast": "ACCEPT_BOUNDED_ACTUALLY_EXECUTED_CONTROL_SCOPE",
            "partial_capture": "ACCEPT_BOUNDED_ACTUALLY_EXECUTED_PARTIAL_UNQUALIFIED_SCOPE",
            "nonverdict_all_settled_consumption": "ADJACENT_SCOPE_ONLY_NOT_CURRENT_ORIGINAL_VERIFIER_JOIN",
            "interrupted_capture_and_actual_receiving": "PURE_SOURCE_STATUS_COVERED_ACTUAL_CAPTURE_UNRECEIVED",
        },
        "recommendation": "HOLD_FULL_ORIGINAL_R35_V04",
        "new_original_awards": [], "m6_credit": False, "full_verifier_replay": False,
        "registry_commands_executed": 0, "native_or_protected_operation_here": False,
    }
    sys.stdout.buffer.write((json.dumps(result, sort_keys=True, indent=2) + "\n").encode())


if __name__ == "__main__":
    main()
