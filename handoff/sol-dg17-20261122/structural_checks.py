"""Source-only R0037 JOIN, input-radius and cheap-path observations."""
import ast
import json
from pathlib import Path
import runpy
import subprocess
import sys
import tempfile

CANDIDATE = "51416b2f156b341c4a5f09029e2c6ceb5b30b1e7"
ROOT = Path(__file__).resolve().parents[2]
OWNER = "skills/implementaudit/scripts/compile-work-graph.py"
FIXTURES = "tests/native-work-graph-cases.py"


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT).decode().strip()


def observe(name, expected, call, seed=None, error=None):
    try:
        actual = call()
    except Exception as exc:
        actual = {"exception": type(exc).__name__, "detail": str(exc)}
    if error is not None:
        matched = (
            isinstance(actual, dict)
            and actual.get("exception") == "WorkGraphError"
            and error in actual.get("detail", "")
        )
    else:
        matched = actual == expected
    print(json.dumps({
        "case": name,
        "status": "MATCH" if matched else "MISMATCH",
        "input": seed,
        "expected": expected if error is None else {"WorkGraphError": error},
        "observed": actual,
    }, sort_keys=True))
    return matched


def constructed_run(node, include_join):
    nodes = [
        node("STOCKTAKE", None, "PLAN", requires=["READOUT"] if include_join else []),
        node("PRECHECK", "STOCKTAKE", "PHASE", requires=["SHELF", "INVENTORY"]),
        node("SHELF", "PRECHECK", state="DONE", reads=["path:inputs/a.txt"], done_evidence="a" * 64),
        node("INVENTORY", "PRECHECK", state="DONE", reads=["path:inputs/b.txt"], done_evidence="b" * 64),
        node("LAYOUT", "PRECHECK", requires=["SHELF"]),
        node("TALLY", "STOCKTAKE", requires=["INVENTORY"]),
    ]
    if include_join:
        nodes.append(node("READOUT", "STOCKTAKE", "JOIN", requires=["LAYOUT", "TALLY"], independent_results=True))
    state = {
        "schema": "implementaudit.native-state.v1",
        "campaign": "inventory-discrepancy",
        "root": "STOCKTAKE",
        "original_scope": "bounded stocktake comparison",
        "nodes": [entry["id"] for entry in nodes],
        "event": {"id": "initial-return", "kind": "RETURN", "subject": "INVENTORY"},
        "context": {"host_capacity": 4, "operator_ceiling": None, "reserve": 1,
                    "route_facts": [], "outstanding_deliveries": []},
    }
    return state, nodes


def join_controls(root, fixture):
    owner, build, node, packet = (fixture[key] for key in ("wg", "graph", "node", "packet"))
    state, nodes = constructed_run(node, True)
    graph = build(root, state, nodes)
    plan = owner.select_native_frontier_v1(graph)
    results = [packet(graph, plan, name) for name in plan["selected"]]
    baseline = observe("JOIN:selected-pair", ["LAYOUT", "TALLY"],
                       lambda: sorted(plan["selected"]))
    if not baseline:
        return [baseline]

    def join(rows, current=graph, target="READOUT"):
        return owner.reconcile_native_results_v1(graph, current, plan, rows, target)

    def result_scope(rows):
        joined = join(rows)
        return {key: joined[key] for key in
                ("status", "consumer", "authority", "lifecycle_credit", "retained_scopes", "missing")}

    before = fixture["sha"](graph)
    observations = [
        baseline,
        observe("N11:valid-contributors", {
            "status": "SATISFIED_AT_DECLARED_RESULT_CONTRACT", "consumer": "READOUT",
            "authority": "NONE", "lifecycle_credit": "NONE", "missing": [],
            "retained_scopes": {"LAYOUT": ["LAYOUT"], "TALLY": ["TALLY"]},
        }, lambda: result_scope(results), seed=plan["selected"]),
        observe("N11:parent-credit-refused", None,
                lambda: join([dict(results[0], scope=["STOCKTAKE"]), results[1]]),
                seed={"scope": ["STOCKTAKE"]}, error="scope cannot grant whole-parent credit"),
        observe("JOIN:required-contributor-pending", {
            "status": "PENDING", "consumer": "READOUT", "authority": "NONE",
            "lifecycle_credit": "NONE", "retained_scopes": {"LAYOUT": ["LAYOUT"]}, "missing": ["TALLY"],
        }, lambda: result_scope([next(row for row in results if row["node"] == "LAYOUT")]), seed=["LAYOUT"]),
        observe("JOIN:duplicate", None, lambda: join([*results, results[0]]),
                seed="repeat first admitted packet", error="duplicate contributor"),
        observe("JOIN:stale-graph", None,
                lambda: join([dict(results[0], graph_digest="0" * 64), results[1]]),
                seed="prior graph identity", error="stale graph/dispatch/source identity"),
        observe("JOIN:undispatched", None,
                lambda: join([packet(graph, plan, "SHELF"), *results]),
                seed="SHELF", error="unknown or undispatched contributor"),
        observe("JOIN:graph-remains-immutable", before, lambda: fixture["sha"](graph)),
    ]
    other_state, other_nodes = constructed_run(node, False)
    omitted = build(root / "omitted-join", other_state, other_nodes)
    omitted_plan = owner.select_native_frontier_v1(omitted)
    omitted_results = [packet(omitted, omitted_plan, name) for name in omitted_plan["selected"]]
    observations.extend([
        observe("H04:valid-contributors-without-join", ["LAYOUT", "TALLY"],
                lambda: sorted(omitted_plan["selected"])),
        observe("H04:omitted-join-refused", None,
                lambda: owner.reconcile_native_results_v1(
                    omitted, omitted, omitted_plan, omitted_results, "READOUT"),
                seed={"join": "READOUT", "contributors": omitted_plan["selected"]}, error="unknown JOIN consumer"),
    ])
    (root / "inputs" / "a.txt").write_bytes(b"revised shelf measurements\n")
    current = build(root, state, nodes)
    current_nodes = fixture["by_id"](current)
    original_nodes = fixture["by_id"](graph)
    observations.extend([
        observe("B04/H05:disjoint-input-evidence-current", ["INVENTORY", "TALLY"],
                lambda: [name for name in ("INVENTORY", "TALLY")
                         if current_nodes[name]["input_digest"] == original_nodes[name]["input_digest"]
                         and current_nodes[name]["done_evidence"] == original_nodes[name]["done_evidence"]],
                seed="inputs/a.txt only"),
        observe("B04/H05:recompute-scoped-result", {
            "status": "RECOMPUTE_REQUIRED", "preserved": ["INVENTORY", "TALLY"],
            "invalidated": ["LAYOUT", "PRECHECK", "READOUT", "SHELF", "STOCKTAKE"], "authority": "NONE",
        }, lambda: {key: value for key, value in join(results, current=current).items()
                    if key in ("status", "preserved", "invalidated", "authority")},
                seed="reconsume prior scoped results against current graph"),
    ])
    return observations


def cheap_path_controls(owner):
    cases = [
        (0, 0, 4, False), (1, 1, 4, False), (2, 2, 4, False),
        (3, 2, 2, True), (3, 2, 1, False), (3, 1, 4, False),
    ]
    observations = [
        observe("M14:source-threshold", {
            "graph_required": expected, "mode": "GRAPH_CANDIDATE" if expected else "CHEAP_SERIAL",
            "authority": "NONE",
        }, lambda: owner.cheap_path_v1(total, ready, capacity), seed=[total, ready, capacity])
        for total, ready, capacity, expected in cases
    ]
    observations.append(observe("M14:contradictory-census", None,
                                lambda: owner.cheap_path_v1(2, 3, 1),
                                seed=[2, 3, 1], error="cheap path census contradiction"))

    # Change only the local copy of the graph-vs-serial threshold. Leave the
    # packaged owner and all guard, effect and authority decisions alone.
    source = (ROOT / OWNER).read_text(encoding="utf-8")
    for force_graph in (False, True):
        function = next(item for item in ast.parse(source).body
                        if isinstance(item, ast.FunctionDef) and item.name == "cheap_path_v1")
        threshold = next(item for item in function.body if isinstance(item, ast.Assign)
                         and [target.id for target in item.targets] == ["graph_required"])
        threshold.value = ast.Constant(force_graph)
        module = ast.fix_missing_locations(ast.Module(body=[function], type_ignores=[]))
        namespace = {"WorkGraphError": owner.WorkGraphError, "_native_int": owner._native_int}
        exec(compile(module, "<cheap-path-threshold-control>", "exec"), namespace)
        changed = namespace["cheap_path_v1"]
        mismatch = [list((total, ready, capacity)) for total, ready, capacity, expected in cases
                    if changed(total, ready, capacity)["graph_required"] != expected]
        expected = [[total, ready, capacity] for total, ready, capacity, originally in cases
                    if originally != force_graph]
        observations.append(observe("M14:in-memory-threshold-mutation", expected,
                                    lambda: mismatch, seed={"force_graph": force_graph}))
    return observations


def main():
    if git("status", "--porcelain", "--", "skills", "tests", "fixtures", "scripts"):
        raise SystemExit("Candidate source or fixture paths must be clean")
    git("diff", "--exit-code", CANDIDATE, "--", "skills", "tests", "fixtures", "scripts")
    print(json.dumps({
        "schema": "sol-dg17-source-observations.v1",
        "candidate": CANDIDATE,
        "tree": git("rev-parse", CANDIDATE + "^{tree}"),
        "owner_blob": git("rev-parse", f"{CANDIDATE}:{OWNER}"),
        "fixture_blob": git("rev-parse", f"{CANDIDATE}:{FIXTURES}"),
        "python": sys.version.split()[0],
        "scope": "constructed-source-observation",
    }, sort_keys=True))
    fixture = runpy.run_path(str(ROOT / FIXTURES))
    with tempfile.TemporaryDirectory(prefix="sol-dg17-", dir=ROOT / ".IMPLEMENTAUDIT") as scratch:
        observations = join_controls(Path(scratch), fixture)
    observations.extend(cheap_path_controls(fixture["wg"]))
    print(json.dumps({"checks": len(observations), "matches": sum(observations)}, sort_keys=True))
    return 0 if all(observations) else 1


if __name__ == "__main__":
    sys.exit(main())
