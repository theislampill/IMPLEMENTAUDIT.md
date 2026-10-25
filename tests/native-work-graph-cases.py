"""Constructed POSIX source/consumer controls; never a native campaign receipt."""
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import types

REPO = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "work_graph", REPO / "skills/implementaudit/scripts/compile-work-graph.py")
wg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wg)
coverage_spec = importlib.util.spec_from_file_location("source_coverage", REPO / "scripts/check-auto-loom-coverage.py")
coverage = importlib.util.module_from_spec(coverage_spec)
coverage_spec.loader.exec_module(coverage)


def raw(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()


def sha(obj):
    return hashlib.sha256(raw(obj)).hexdigest()


def reject(call, text):
    try:
        call()
    except wg.WorkGraphError as exc:
        assert text in str(exc), (text, str(exc))
    else:
        raise AssertionError("accepted negative control: " + text)


def node(name, parent, kind="TASK", state="OPEN", **kw):
    result = dict(id=name, parent=parent, kind=kind, state=state,
                  requires=[], optional=[], reads=[], writes=[], acceptance=[],
                  resources=[], authority=[], effect="READ_ONLY", authorization="PERMITTED",
                  independence="KNOWN", resource_demand=1, rank=0,
                  route_scopes=[], logical_delivery=None, future_consumer=None,
                  invalidators=[], independent_results=False,
                  context=dict(locality="EITHER", governor_cost=1, child_cost=2,
                               return_cost=1, useful_value=5),
                  done_evidence="d" * 64 if state == "DONE" else None)
    result.update(kw)
    return result


def fixture():
    nodes = [
        node("ROOT", None, "PLAN", requires=["QUALIFY"]),
        node("PH", "ROOT", "PHASE", requires=["C1", "C2"]),
        node("C1", "PH", state="DONE", reads=["path:inputs/a.txt"]),
        node("C2", "PH", state="DONE", reads=["path:inputs/b.txt"]),
        node("ADMIT", "PH", requires=["C1", "C2"], effect="MUTATION",
             authorization="MISSING", authority=["scope:admission"],
             route_scopes=["admission"]),
        node("PREP", "PH", requires=["C1", "C2"], effect="PREPARATION",
             reads=["path:inputs/a.txt", "path:inputs/b.txt"],
             writes=["semantic:prepared-comparison"], rank=5,
             future_consumer=dict(node="QUALIFY", condition="exact input digest manifest")),
        node("SIB", "ROOT", reads=["path:inputs/c.txt"]),
        node("QUALIFY", "ROOT", "JOIN", requires=["PREP", "SIB", "ADMIT"],
             optional=["OPTIONAL"], independent_results=True),
        node("OPTIONAL", "ROOT", authorization="MISSING"),
    ]
    state = dict(schema="implementaudit.native-state.v1", campaign="portable-fixture",
                 root="ROOT", original_scope="bounded comparison qualification",
                 nodes=[n["id"] for n in nodes],
                 event=dict(id="return-2", kind="RETURN", subject="C2"),
                 context=dict(host_capacity=4, operator_ceiling=None, reserve=1,
                              route_facts=[], outstanding_deliveries=[]))
    return state, nodes


def write_run(root, state, nodes):
    def doc(rel, value):
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(b"# Constructed native-format fixture\n\n```implementaudit-work-graph\n" + raw(value) + b"\n```\n")
    doc("STATE.md", state)
    doc("ROADMAP.md", dict(schema="implementaudit.native-roadmap.v1",
                           phases=[n["id"] for n in nodes if n["kind"] == "PHASE"]))
    for n in nodes:
        directory = {"PLAN": "plans", "PHASE": "phases"}.get(n["kind"], "tasks")
        doc(directory + "/" + n["id"] + ".md",
            dict(schema="implementaudit.native-spec.v1", nodes=[n]))
    (root / "inputs").mkdir(exist_ok=True)
    for name in ("a", "b", "c"):
        path = root / "inputs" / (name + ".txt")
        if not path.exists():
            path.write_text("constructed input " + name + "\n")


def graph(root, state=None, nodes=None):
    if state is None:
        state, nodes = fixture()
    write_run(root, state, nodes)
    return wg.read_native_run_v1(root)


def by_id(g):
    return {n["id"]: n for n in g["nodes"]}


def slot_capacity_controls(root):
    """Zero declared resource units never erase a selected or ACTIVE slot."""
    cases = [
        ("zero-ready", 1, None, 0, 0, 0, None, ["PREP"], 0),
        ("zero-host", 0, None, 0, 0, 0, None, [], 0),
        ("zero-ceiling", 3, 0, 0, 0, 0, None, [], 0),
        ("one-ceiling", 3, 1, 0, 0, 0, None, ["PREP"], 0),
        ("reserve-held", 2, None, 1, 0, 0, None, ["PREP"], 0),
        ("two-free", 2, None, 0, 0, 0, None, ["PREP", "SIB"], 0),
        ("active-zero-full", 1, None, 0, 0, 0, "SIB", [], 1),
        ("active-zero-free", 2, None, 0, 0, 0, "SIB", ["PREP"], 1),
        ("active-over-capacity", 1, None, 0, 0, 2, "SIB", [], 2),
        ("positive-demand", 2, None, 0, 2, 1, None, ["PREP"], 0),
        ("mixed-demand", 2, None, 0, 0, 2, None, ["PREP"], 0),
        ("structural-active-zero", 1, None, 0, 0, 0, "ROOT", [], 1),
    ]
    for name, host, ceiling, reserve, prep, sibling, active, expected, occupied in cases:
        state, nodes = fixture()
        state["context"].update(host_capacity=host, operator_ceiling=ceiling, reserve=reserve)
        indexed = {n["id"]: n for n in nodes}
        indexed["PREP"]["resource_demand"] = prep
        indexed["SIB"]["resource_demand"] = sibling
        if active:
            indexed[active]["state"] = "ACTIVE"
            if active == "ROOT":
                indexed[active]["resource_demand"] = 0
        current = graph(root / name, state, nodes)
        dispatch = wg.select_native_frontier_v1(current)
        (root / name / "observed.json").write_bytes(raw(dict(
            scope="CONSTRUCTED_SOURCE_DERIVED_SELECTION_ONLY", authority="NONE",
            graph=current, dispatch=dispatch, expected_selected=expected,
            expected_active_occupancy=occupied)) + b"\n")
        assert dispatch["selected"] == expected, (name, dispatch)
        assert dispatch["active_occupancy"] == occupied, (name, dispatch)
        assert dispatch["free_capacity"] == max(0, dispatch["capacity"] - occupied)
        assert len(dispatch["selected"]) <= dispatch["free_capacity"], (name, dispatch)
        # The accepted source field remains zero; occupancy is derived separately.
        assert by_id(current)["PREP"]["resource_demand"] == prep


def completed_input_controls(root):
    """Current missing inputs cannot discharge required edges via old DONE."""
    state, nodes = fixture()
    nodes.append(node("C3", "PH", state="DONE", requires=["C1"]))
    state["nodes"].append("C3")
    nodes[5]["requires"] = ["C3", "C2"]
    before = graph(root, state, nodes)
    missing = root / "inputs/a.txt"
    original = missing.read_bytes()
    missing.unlink()
    after = wg.read_native_run_v1(root)
    current = by_id(after)
    assert current["C1"]["state"] == "BLOCKED", current["C1"]
    assert current["C1"]["declared_state"] == "DONE"
    assert current["C1"]["done_evidence"] == by_id(before)["C1"]["done_evidence"]
    assert current["C1"]["blocked_reasons"] == ["MISSING_INPUT"]
    assert current["C3"]["state"] == "BLOCKED"
    assert current["C3"]["blocked_reasons"] == ["DEPENDENCY"]
    assert current["PREP"]["state"] == "BLOCKED"
    assert current["C2"]["state"] == "DONE"
    assert wg.select_native_frontier_v1(after)["selected"] == ["SIB"]
    delta = wg.diff_native_graphs_v1(before, after)
    assert {"C1", "C3", "PREP"} <= set(delta["invalidated"])
    assert {"C2", "SIB"} <= set(delta["preserved"])
    missing.write_bytes(original)
    assert wg.read_native_run_v1(root) == before

    # ACTIVE custody is retained even if its current read becomes missing.
    active = copy.deepcopy(nodes)
    active[6].update(state="ACTIVE", done_evidence=None)
    graph(root, state, active)
    (root / "inputs/c.txt").unlink()
    active_missing = wg.read_native_run_v1(root)
    assert by_id(active_missing)["SIB"]["state"] == "ACTIVE"
    assert by_id(active_missing)["SIB"]["blocked_reasons"] == ["MISSING_INPUT"]
    assert wg.select_native_frontier_v1(active_missing)["active_occupancy"] == 1

    # A source DONE assertion over a source OPEN dependency remains invalid.
    contradiction = copy.deepcopy(nodes)
    contradiction[2].update(state="OPEN", done_evidence=None)
    write_run(root, state, contradiction)
    reject(lambda: wg.read_native_run_v1(root), "DONE contradicts open required")


def packet(g, plan, name, status="PASS", terminal=True, **kw):
    n = by_id(g)[name]
    result = dict(schema="implementaudit.work-result.v1", node=name,
                  dispatch_id=plan["dispatch_id"], graph_digest=g["digest"],
                  input_digest=n["input_digest"], status=status, terminal=terminal,
                  exit_code=0 if status == "PASS" else None,
                  evidence_digest=sha(name) if status == "PASS" else None,
                  independence_key="independent-" + name, scope=[name])
    result.update(kw)
    return result


def execute_manifest(input_root, g, transition, name, output):
    """Actual bounded fixture work over this node's declared file inputs."""
    n = by_id(g)[name]
    request = dict(node=name, dispatch_id=transition["dispatch_id"], graph_digest=g["digest"],
                   input_digest=n["input_digest"],
                   paths=sorted({p for p in n["reads"] + n["invalidators"] if p.startswith("path:")}))
    program = '''import hashlib,json,os,pathlib,sys
root=pathlib.Path(sys.argv[1]).resolve()
request=json.loads(sys.argv[2])
manifest={}
read_set={}
for identity in request.pop("paths"):
    path=root / identity[5:]
    if path.is_symlink() or not path.is_file():
        raise SystemExit(3)
    mode=path.stat().st_mode & 0o7777
    digest=hashlib.sha256(path.read_bytes()).hexdigest()
    manifest[identity]={"mode":mode,"content_sha256":digest}
    fact=json.dumps([mode,digest],sort_keys=True,separators=(",",":")).encode()
    read_set[identity]={"status":"PRESENT_FILE","sha256":hashlib.sha256(fact).hexdigest()}
request.update(input_root_identity=hashlib.sha256(os.fsencode(str(root))).hexdigest(),read_set=read_set,manifest=manifest)
pathlib.Path(sys.argv[3]).write_text(json.dumps(request,sort_keys=True,separators=(",",":")))
'''
    command = [sys.executable, "-B", "-c", program, str(input_root), raw(request).decode(), str(output)]
    result = subprocess.run(command, capture_output=True)
    output.with_suffix(".command.json").write_bytes(raw(dict(command=command, cwd=os.getcwd(),
                                                          scope="CONSTRUCTED_MANIFEST_SUBPROCESS")))
    output.with_suffix(".stdout").write_bytes(result.stdout)
    output.with_suffix(".stderr").write_bytes(result.stderr)
    output.with_suffix(".exit").write_text(str(result.returncode) + "\n")
    assert result.returncode == 0, result.stderr
    return result.returncode


def consume_manifest(input_root, g, transition, name, output, exit_code):
    """Named portable consumers independently read actual output and inputs.

    PREP's manifest is usable only for its exact comparison inputs. SIB's
    enclosing scope records its own c.txt check. Neither decision admits ADMIT.
    """
    actual = output.read_bytes()
    value = wg.decode_strict_json_bytes(actual, "constructed manifest output")
    n = by_id(g)[name]
    expected_paths = sorted({p for p in n["reads"] + n["invalidators"] if p.startswith("path:")})
    manifest = {}
    for identity in expected_paths:
        path = input_root / identity[5:]
        manifest[identity] = dict(mode=path.stat().st_mode & 0o7777, content_sha256=hashlib.sha256(path.read_bytes()).hexdigest())
    expected_reads = {p: g["binding"]["read_set"][p] for p in expected_paths}
    expected = dict(node=name, dispatch_id=transition["dispatch_id"], graph_digest=g["digest"],
                    input_digest=n["input_digest"], input_root_identity=g["binding"]["input_root_identity"],
                    read_set=expected_reads, manifest=manifest)
    # Output facts must match the source-bound graph AND the consumer's actual
    # files. Changing labels or pointing at another root cannot satisfy this.
    computed_reads = {p: dict(status="PRESENT_FILE", sha256=wg._graph_hash([m["mode"], m["content_sha256"]])) for p, m in manifest.items()}
    if (value != expected or computed_reads != expected_reads or
            hashlib.sha256(os.fsencode(str(input_root.resolve()))).hexdigest() != g["binding"]["input_root_identity"]):
        raise wg.WorkGraphError("portable consumer input/output binding mismatch")
    consumer = transition["consumers"][name]
    if name == "PREP":
        assert consumer == dict(node="QUALIFY", condition="exact input digest manifest")
        assert expected_paths == ["path:inputs/a.txt", "path:inputs/b.txt"]
        before, after = "MISSING_PREPARATION", "EXACT_COMPARISON_MANIFEST_USABLE"
    else:
        assert name == "SIB" and consumer["node"] == "ROOT"
        assert expected_paths == ["path:inputs/c.txt"]
        before, after = "SIBLING_INPUT_UNCHECKED", "SIBLING_INPUT_VERIFIED"
    execution = {k: value[k] for k in ("node", "dispatch_id", "graph_digest", "input_digest", "input_root_identity", "read_set")}
    execution.update(output_digest=hashlib.sha256(actual).hexdigest(), exit_code=exit_code)
    consumption = dict(node=name, consumer=consumer["node"], condition=consumer["condition"],
                       input_digest=value["input_digest"], input_root_identity=value["input_root_identity"],
                       read_set_digest=wg._graph_hash(value["read_set"]), output_digest=execution["output_digest"],
                       decision_before=before, decision_after=after)
    return execution, consumption


def reminder_controls(root, state, nodes, original, report, evidence):
    """Use the receipt of the actual PREP/SIB work and its real consumer."""
    history = [report["event_receipt"]]
    reminder_state = copy.deepcopy(state)
    reminder_state["event"].update(id="reminder-new-id", kind="REMINDER")
    reminder = graph(root, reminder_state, nodes)
    assert wg.diff_native_graphs_v1(original, reminder)["invalidated"] == []
    transition = wg.compile_recursive_transition_v1(reminder, history)
    evidence.mkdir()
    for name, value in (("original", original), ("consumed", report), ("reminder", reminder),
                        ("transition", transition)):
        (evidence / (name + ".json")).write_bytes(raw(value))
    assert transition["selected"] == [] and transition["mode"] == "NO_REDISPATCH", transition
    no_op = wg.check_recursive_execution_v1(reminder, history, transition, [], [])
    assert no_op["status"] == "NO_REDISPATCH_AT_SUPPLIED_HISTORY"
    assert no_op["event_receipt"] is None  # No new result or accepted-history token.
    assert report["event_receipt"]["source_graph"] == original
    (evidence / "no-op-consumption.json").write_bytes(raw(no_op))

    legacy = {k: v for k, v in history[0].items() if k != "source_graph"}
    assert wg.compile_recursive_transition_v1(original, [legacy])["selected"] == []
    reject(lambda: wg.compile_recursive_transition_v1(reminder, [legacy]), "unbound")
    reject(lambda: wg.compile_recursive_transition_v1(reminder, history * 2), "duplicate event")
    for key, value in (("graph_digest", "0" * 64), ("dispatch_id", "0" * 64),
                       ("event_id", "another-event"), ("consumed", ["PREP"])):
        wrong = copy.deepcopy(history[0])
        wrong[key] = value
        reject(lambda: wg.compile_recursive_transition_v1(reminder, [wrong]), "event")
    forged = copy.deepcopy(history[0])
    forged["source_graph"]["nodes"][0]["input_digest"] = "0" * 64
    forged["source_graph"].pop("digest")
    forged["source_graph"] = wg._seal_graph(forged["source_graph"])
    reject(lambda: wg.compile_recursive_transition_v1(reminder, [forged]), "source-derived")
    missing = copy.deepcopy(history[0])
    missing["source_graph"] = None
    reject(lambda: wg.compile_recursive_transition_v1(reminder, [missing]), "object")

    # A history entry cannot suppress a changed input, context or currentness.
    path = root / "inputs/a.txt"
    initial_bytes = path.read_bytes()
    path.write_bytes(initial_bytes + b"material change\n")
    changed = wg.read_native_run_v1(root)
    assert "PREP" in wg.diff_native_graphs_v1(original, changed)["invalidated"]
    assert wg.compile_recursive_transition_v1(changed, history)["selected"] == ["PREP", "SIB"]
    path.write_bytes(initial_bytes)
    altered_context = copy.deepcopy(reminder_state)
    altered_context["context"]["host_capacity"] += 1
    changed = graph(root, altered_context, nodes)
    assert wg.compile_recursive_transition_v1(changed, history)["selected"] == ["PREP", "SIB"]
    # Another material event type is not automatically an unchanged reminder.
    altered_context = copy.deepcopy(reminder_state)
    altered_context["event"].update(id="return-new-id", kind="RETURN")
    changed = graph(root, altered_context, nodes)
    assert wg.compile_recursive_transition_v1(changed, history)["selected"] == ["PREP", "SIB"]
    assert graph(root, state, nodes) == original
    print("native-work-graph: new-id unchanged reminder preserves consumed work; changed inputs/context reconsider")


def source_composition_controls(root, expected, scratch):
    """Keep constructed diagnostics separate from acquired repository evidence."""
    compiler = REPO / "skills/implementaudit/scripts/compile-work-graph.py"
    peer = REPO / "source-peers/route-graph/skills/implementaudit/scripts/compile-work-graph.py"
    compiler_raw, peer_raw = compiler.read_bytes(), peer.read_bytes()
    if compiler_raw != peer_raw:
        # The combined owners retain their distinct original route identities.
        # Admit only this exact literal difference; all other bytes must agree.
        canonical_pin = b"_NATIVE_ROUTE_PRODUCER_SHA256 = '8ed51e393f4f8a3be631e48255e9aeca59dcf120a803f1601a034e5ab9e02389'"
        peer_pin = b"_NATIVE_ROUTE_PRODUCER_SHA256 = 'cde0db3f9bbb7203572835dd8311c1f1cd3758baf6ec9aac117b98bb715e5525'"
        assert compiler_raw.count(canonical_pin) == peer_raw.count(peer_pin) == 1
        assert compiler_raw.replace(canonical_pin, peer_pin, 1) == peer_raw, "unqualified compiler source difference"
    manifest = json.loads((REPO / "source-peers/route-graph/SOURCE_MANIFEST.json").read_bytes())
    entry = next(row for row in manifest["files"] if row["semantic_owner"] == "R0035")
    assert entry["bytes"] == len(peer_raw)
    assert entry["sha256"] == hashlib.sha256(peer_raw).hexdigest()

    # The distribution contains the compiler, not the repository-only reader.
    # Execute exactly that layout, then compare the complete derived projection.
    installed = scratch / "installed/skills/implementaudit/scripts/compile-work-graph.py"
    installed.parent.mkdir(parents=True)
    shutil.copy2(compiler, installed)
    isolated = types.ModuleType("isolated_constructed_compiler")
    isolated.__file__ = str(installed)
    exec(compile(compiler_raw, str(installed), "exec"), isolated.__dict__)
    assert not (scratch / "installed/scripts/operational-evidence.py").exists()
    assert isolated.read_native_run_v1(root) == expected
    with isolated.observe_native_run_v1(root) as projection_raw:
        assert type(projection_raw) is bytes
        assert json.loads(projection_raw) == expected

    # The constructed route never calls the secure repository owner. An actual
    # native refusal must propagate, with no fallback or empty projection.
    original_owner = wg._native_static_owner_module_v1
    original_continuity = wg._native_continuity
    original_constructed = wg._constructed_source_snapshot_v1
    def forbidden_owner():
        raise AssertionError("constructed intake loaded the repository-only owner")
    try:
        wg._native_static_owner_module_v1 = forbidden_owner
        assert wg.read_native_run_v1(root) == expected
    finally:
        wg._native_static_owner_module_v1 = original_owner
    def refused_continuity(*args, **kwargs):
        raise wg.WorkGraphError("constructed test native-owner refusal")
    def forbidden_fallback(*args, **kwargs):
        raise AssertionError("native refusal fell back to constructed intake")
    try:
        wg._native_continuity = refused_continuity
        wg._constructed_source_snapshot_v1 = forbidden_fallback
        reject(lambda: wg.read_native_run_v1(root, REPO), "native-owner refusal")
    finally:
        wg._native_continuity = original_continuity
        wg._constructed_source_snapshot_v1 = original_constructed

    # A provisional result is not accepted until its context's final read.
    input_path = root / "inputs/a.txt"
    source_path = root / "STATE.md"
    for path, diagnostic in ((input_path, "native inputs changed during intake"),
                             (source_path, "native source changed during intake")):
        before = path.read_bytes()
        def mutate_during_use():
            with wg.observe_native_run_v1(root) as provisional:
                assert json.loads(provisional) == expected
                path.write_bytes(before + b"\n")
        try:
            reject(mutate_during_use, diagnostic)
        finally:
            path.write_bytes(before)
    assert wg.read_native_run_v1(root) == expected
    print("native-work-graph: exact canonical/peer source pair; installed constructed intake and closing fences; no native fallback")


def main():
    # Historical preimage is valid v1 projection, not native enumeration. This
    # assertion preserves its deliberate limit instead of changing the oracle.
    old = dict(schema="implementaudit.work-graph.v1", population=dict(total_cells=1),
               cells=[dict(id="C1", state="READY", deps=[])], serialization_groups={})
    assert wg.compile_frontier_projection(raw(old))["population"] == 1
    with tempfile.TemporaryDirectory(prefix="r0035-native-") as td:
        if len(sys.argv) > 1:
            td = str(Path(sys.argv[1]).resolve())
            Path(td).mkdir(parents=True, exist_ok=False)
        slot_capacity_controls(Path(td) / "slot-capacity")
        completed_input_controls(Path(td) / "completed-inputs")
        root = Path(td) / "run"
        state, nodes = fixture()
        g = graph(root, state, nodes)
        assert g["binding"]["acquisition"] == "CONSTRUCTED_FILESYSTEM"
        assert len(g["nodes"]) == len(nodes) == sum(g["population"].values())
        assert by_id(g)["ADMIT"]["state"] == "BLOCKED"
        assert by_id(g)["PREP"]["state"] == "READY"
        assert by_id(g)["QUALIFY"]["state"] == "BLOCKED"
        assert wg.read_native_run_v1(root) == g
        source_composition_controls(root, g, Path(td) / "source-composition")
        input_path = root / "inputs/a.txt"
        original_input = input_path.read_bytes()
        input_path.write_bytes(b"changed actual input\n")
        changed_input = wg.read_native_run_v1(root)
        input_delta = wg.diff_native_graphs_v1(g, changed_input)
        assert "PREP" in input_delta["invalidated"] and "SIB" in input_delta["preserved"], input_delta
        input_path.write_bytes(original_input)
        # A serialized final graph cannot silently drop acquisition evidence.
        snapshot = {path: data.encode() for path, data in g["source_documents"].items()}
        bound = {k: copy.deepcopy(v) for k, v in g["binding"].items() if k != "source_digest"}
        for mutate in (
            lambda b: b["read_set"].pop("path:inputs/c.txt"),
            lambda b: b["read_set"].update({"path:extra": dict(status="MISSING", sha256=None)}),
            lambda b: b["read_set"]["path:inputs/c.txt"].update(status="UNKNOWN"),
            lambda b: b["read_set"]["path:inputs/c.txt"].update(sha256=None),
            lambda b: b["read_set"]["path:inputs/c.txt"].update(status="MISSING"),
            lambda b: b.update(acquisition="CALLER_SATISFIED"),
            lambda b: b.update(receipt="caller-receipt"),
        ):
            mutant_binding = copy.deepcopy(bound)
            mutate(mutant_binding)
            reject(lambda: wg._compile_native_documents_v1(snapshot, mutant_binding), "binding")
        missing_nodes = copy.deepcopy(nodes)
        missing_nodes[6]["reads"] = ["path:missing-required-input"]
        missing_graph = graph(root, state, missing_nodes)
        assert "MISSING_INPUT" in by_id(missing_graph)["SIB"]["blocked_reasons"]
        mutant = copy.deepcopy(missing_graph)
        mutant["binding"]["read_set"].pop("path:missing-required-input")
        mutant.pop("digest")
        mutant = wg._seal_graph(mutant)
        reject(lambda: wg.select_native_frontier_v1(wg.decode_strict_json_bytes(raw(mutant), "constructed mutant")), "binding")
        directory_nodes = copy.deepcopy(nodes)
        directory_nodes[6]["reads"] = ["path:inputs"]
        directory = root / "inputs"
        directory.chmod(0o755)
        mode_before = graph(root, state, directory_nodes)
        directory.chmod(0o700)
        mode_after = wg.read_native_run_v1(root)
        assert mode_after != mode_before
        assert "SIB" in wg.diff_native_graphs_v1(mode_before, mode_after)["invalidated"]
        assert wg.read_native_run_v1(root) == mode_after
        directory.chmod(0o755)
        g = graph(root, state, nodes)
        tampered = copy.deepcopy(g)
        by_id(tampered)["ADMIT"]["state"] = "READY"
        tampered.pop("digest")
        tampered["digest"] = sha(tampered)
        reject(lambda: wg.select_native_frontier_v1(tampered), "source-derived")

        # A new obligation omitted from unchanged scalar summaries must now be
        # visible, or refuse the conflicting census. Source bytes decide.
        extra = node("OMITTED", "ROOT", writes=["semantic:prepared-comparison"])
        write_run(root, state, nodes + [extra])
        reject(lambda: wg.read_native_run_v1(root), "population")
        state["nodes"].append("OMITTED")
        write_run(root, state, nodes + [extra])
        enlarged = wg.read_native_run_v1(root)
        assert len(enlarged["nodes"]) == len(nodes) + 1
        assert enlarged["digest"] != g["digest"]
        (root / "tasks/OMITTED.md").unlink()
        state, nodes = fixture()
        g = graph(root, state, nodes)
        (root / "tasks/unknown.md").write_text("# Unspecified task\n")
        reject(lambda: wg.read_native_run_v1(root), "metadata")
        (root / "tasks/unknown.md").unlink()
        (root / "tasks/symlink.md").symlink_to(root / "tasks/PREP.md")
        reject(lambda: wg.read_native_run_v1(root), "symlink")
        (root / "tasks/symlink.md").unlink()

        for field, bad, diagnostic in [("root", "", "non-empty"),
                                       ("original_scope", "", "non-empty")]:
            mutant = copy.deepcopy(state)
            mutant[field] = bad
            write_run(root, mutant, nodes)
            reject(lambda: wg.read_native_run_v1(root), diagnostic)
        bad_nodes = copy.deepcopy(nodes)
        bad_nodes[1]["parent"] = "C1"
        write_run(root, state, bad_nodes)
        reject(lambda: wg.read_native_run_v1(root), "ancestry")
        bad_nodes = copy.deepcopy(nodes)
        bad_nodes[2]["requires"] = ["PREP"]
        write_run(root, state, bad_nodes)
        reject(lambda: wg.read_native_run_v1(root), "cycle")
        bad_nodes = copy.deepcopy(nodes)
        bad_nodes[4]["unknown_owner"] = "NONE"
        write_run(root, state, bad_nodes)
        reject(lambda: wg.read_native_run_v1(root), "member")
        g = graph(root, state, nodes)

        plan = wg.select_native_frontier_v1(g)
        assert plan["selected"] == ["PREP", "SIB"], plan
        assert plan["free_capacity"] == 3 and plan["authority"] == "NONE"
        assert plan["placements"]["PREP"] == "GOVERNOR"
        assert "ADMIT" in plan["blocked"]
        for ceiling, count in [(0, 0), (1, 1), (None, 2)]:
            s = copy.deepcopy(state)
            s["context"]["operator_ceiling"] = ceiling
            gg = graph(root, s, nodes)
            selected = wg.select_native_frontier_v1(gg)
            # reserve is subtracted from the host, then the operator ceiling.
            assert len(selected["selected"]) == count, selected
        s = copy.deepcopy(state)
        s["context"]["host_capacity"] = 1
        gg = graph(root, s, nodes)
        assert not wg.select_native_frontier_v1(gg)["selected"]

        # Semantic ownership, including read/write overlap, survives different
        # file names. Read/read alone is not a conflict.
        ns = copy.deepcopy(nodes)
        ns[6]["writes"] = ["semantic:prepared-comparison"]
        gg = graph(root, state, ns)
        pp = wg.select_native_frontier_v1(gg)
        assert pp["selected"] == ["PREP"] and pp["deferred"]["SIB"] == "CONFLICT"
        ns[6]["writes"] = []
        ns[6]["reads"] = ["semantic:prepared-comparison"]
        assert wg.select_native_frontier_v1(graph(root, state, ns))["selected"] == ["PREP"]
        ns[6]["reads"] = ["path:inputs/a.txt"]
        assert wg.select_native_frontier_v1(graph(root, state, ns))["selected"] == ["PREP", "SIB"]
        ns[6]["writes"] = ["path:inputs"]
        assert wg.select_native_frontier_v1(graph(root, state, ns))["selected"] == ["PREP"]
        ns = copy.deepcopy(nodes)
        ns[6]["state"] = "ACTIVE"
        ns[6]["writes"] = ["semantic:prepared-comparison"]
        gg = graph(root, state, ns)
        pp = wg.select_native_frontier_v1(gg)
        assert not pp["selected"] and pp["active_occupancy"] == 1
        assert by_id(gg)["SIB"]["state"] == "ACTIVE"

        # Missing effect capability is explicit; prompt permission alone cannot
        # turn an external action into executable portable work.
        ns = copy.deepcopy(nodes)
        ns[6]["effect"] = "EXTERNAL"
        ns[6]["logical_delivery"] = "same-logical-delivery"
        gg = graph(root, state, ns)
        assert "EFFECT_EXECUTOR_UNAVAILABLE" in by_id(gg)["SIB"]["blocked_reasons"]
        ss = copy.deepcopy(state)
        ss["context"]["outstanding_deliveries"] = [dict(id="same-logical-delivery", state="UNKNOWN", source_digest="e" * 64)]
        gg = graph(root, ss, ns)
        assert "LOGICAL_DELIVERY_HELD" in by_id(gg)["SIB"]["blocked_reasons"]
        assert "PREP" in wg.select_native_frontier_v1(gg)["selected"]

        # Current R0033 output currently lacks a scoped fact. This is a proposed
        # typed consumer, not an authenticated/adopted producer interface.
        ns = copy.deepcopy(nodes)
        ns[6]["route_scopes"] = ["admission"]
        ss = copy.deepcopy(state)
        fact = dict(schema="implementaudit.work-graph-route-fact.v1", scope="admission",
                    obligation="obligation-1", generation="route-1", binding="binding-1",
                    continuity="continuity-1", status="BLOCKED", satisfaction=None,
                    expected_satisfaction=None, source_digest="f" * 64)
        ss["context"]["route_facts"] = [fact]
        blocked = graph(root, ss, ns)
        assert wg.select_native_frontier_v1(blocked)["selected"] == ["PREP"]
        ss["context"]["route_facts"][0].update(status="SATISFIED", satisfaction="old", expected_satisfaction="new")
        stale = graph(root, ss, ns)
        assert "ROUTE_UNSATISFIED" in by_id(stale)["SIB"]["blocked_reasons"]
        ss["context"]["route_facts"][0]["satisfaction"] = "new"
        unblocked = graph(root, ss, ns)
        assert wg.select_native_frontier_v1(unblocked)["selected"] == ["PREP", "SIB"]
        invalidated = wg.diff_native_graphs_v1(blocked, unblocked)
        assert "SIB" in invalidated["invalidated"] and "PREP" in invalidated["preserved"]
        # Pure reducer controls cannot mint or verify a native receipt. Even a
        # matching scalar is insufficient when native acquisition is requested.
        assert wg._native_route_block(fact, "NATIVE_CONTINUITY_VERIFIED") == "ROUTE_PRODUCER_UNAVAILABLE"
        ss["context"]["route_facts"][0].update(status="NOT_REQUIRED", obligation=None, satisfaction=None, expected_satisfaction=None)
        not_required = graph(root, ss, ns)
        assert wg.select_native_frontier_v1(not_required)["selected"] == ["PREP", "SIB"]
        assert wg._native_route_block(ss["context"]["route_facts"][0], "NATIVE_CONTINUITY_VERIFIED") == "ROUTE_PRODUCER_UNAVAILABLE"

        # Required/optional result contracts, never parent lifecycle authority.
        ns = copy.deepcopy(nodes)
        ns[7]["requires"] = ["PREP", "SIB"]
        g = graph(root, state, ns)
        plan = wg.select_native_frontier_v1(g)
        results = [packet(g, plan, name) for name in plan["selected"]]
        join = lambda rr, current=g: wg.reconcile_native_results_v1(g, current, plan, rr, "QUALIFY")
        assert join(results)["status"] == "SATISFIED_AT_DECLARED_RESULT_CONTRACT"
        assert join(results)["authority"] == "NONE"
        assert join(results[:1])["status"] == "PENDING"
        reject(lambda: join(results + results[:1]), "duplicate")
        unknown = copy.deepcopy(results)
        unknown[0]["node"] = "UNKNOWN"
        reject(lambda: join(unknown), "unknown")
        old_result = copy.deepcopy(results)
        old_result[0]["graph_digest"] = "0" * 64
        reject(lambda: join(old_result), "stale")
        for status, terminal in [("PARTIAL", True), ("NONVERDICT", True), ("UNKNOWN", True),
                                 ("PENDING", False), ("INTERRUPTED", True)]:
            rr = [packet(g, plan, "PREP", status, terminal), results[1]]
            assert join(rr)["status"] != "SATISFIED_AT_DECLARED_RESULT_CONTRACT", status
        contradictory = copy.deepcopy(results)
        contradictory[0]["exit_code"] = 1
        reject(lambda: join(contradictory), "contradictory")
        correlated = copy.deepcopy(results)
        correlated[1]["independence_key"] = correlated[0]["independence_key"]
        assert join(correlated)["status"] == "NONVERDICT"
        common_nodes = copy.deepcopy(ns)
        common_nodes[6]["reads"] = ["path:inputs/a.txt"]
        common_graph = graph(root, state, common_nodes)
        common_plan = wg.select_native_frontier_v1(common_graph)
        common_results = [packet(common_graph, common_plan, name) for name in common_plan["selected"]]
        assert wg.reconcile_native_results_v1(common_graph, common_graph, common_plan, common_results, "QUALIFY")["status"] == "NONVERDICT"
        # Distinct immediate dependencies still share C1 transitively.
        transitive = copy.deepcopy(ns)
        transitive[3]["requires"] = ["C1"]
        transitive[5]["requires"] = ["C1"]
        transitive[6]["requires"] = ["C2"]
        transitive_graph = graph(root, state, transitive)
        transitive_plan = wg.select_native_frontier_v1(transitive_graph)
        transitive_results = [packet(transitive_graph, transitive_plan, n) for n in transitive_plan["selected"]]
        assert wg.reconcile_native_results_v1(transitive_graph, transitive_graph, transitive_plan, transitive_results, "QUALIFY")["status"] == "NONVERDICT"
        # Common transitive reads and optional sources also defeat independence.
        transitive[3]["requires"] = []
        transitive[3]["reads"] = ["path:inputs/a.txt"]
        transitive[3]["done_evidence"] = sha("C2 separate result")
        for optional in (False, True):
            if optional:
                transitive[6]["optional"], transitive[6]["requires"] = ["C2"], []
            tg = graph(root, state, transitive)
            tp = wg.select_native_frontier_v1(tg)
            tr = [packet(tg, tp, n) for n in tp["selected"]]
            assert wg.reconcile_native_results_v1(tg, tg, tp, tr, "QUALIFY")["status"] == "NONVERDICT"
        # A genuinely disjoint source closure remains eligible for scoped JOIN.
        transitive[3]["reads"] = ["path:inputs/c.txt"]
        dg = graph(root, state, transitive)
        dp = wg.select_native_frontier_v1(dg)
        dr = [packet(dg, dp, n) for n in dp["selected"]]
        assert wg.reconcile_native_results_v1(dg, dg, dp, dr, "QUALIFY")["status"] == "SATISFIED_AT_DECLARED_RESULT_CONTRACT"
        partial = copy.deepcopy(results)
        partial[0]["scope"] = ["ROOT"]
        reject(lambda: join(partial), "scope")
        fail = packet(g, plan, "PREP", "FAIL", True, exit_code=7)
        assert join([fail])["status"] == "PENDING"
        assert join([fail, results[1]])["status"] == "FAIL"
        changed_nodes = copy.deepcopy(ns)
        changed_nodes[5]["reads"].append("path:new-input")
        newer = graph(root, state, changed_nodes)
        rejoin = join(results, newer)
        assert rejoin["status"] == "RECOMPUTE_REQUIRED"
        assert "PREP" in rejoin["invalidated"] and "SIB" in rejoin["preserved"]

        # Held-out concrete portable transition. Outputs come from real bounded
        # subprocess work; the identified consumer checks exact bytes and changes
        # a qualification decision while admission stays blocked.
        g = graph(root, state, nodes)
        transition = wg.compile_recursive_transition_v1(g, [])
        assert transition["ancestors"] == ["C2", "PH", "ROOT"]
        assert transition["selected"] == ["PREP", "SIB"]
        binding = dict(campaign=g["campaign"], event=g["event"]["id"], state=g["digest"])
        facts = dict(binding=binding, currentness=None, evidence_scope=g["original_scope"],
                     parents={n["id"]: n["parent"] for n in g["nodes"]},
                     subject=g["event"]["subject"], root=g["root"], edges=[], views=["portable"], history=[])
        proposal = dict(binding=binding, authority="NONE", evidence_scope=g["original_scope"],
                        invariants=coverage.INVARIANTS, directions=sorted(coverage.DIRECTIONS),
                        ancestors=transition["ancestors"], edges=[],
                        new_actions=transition["selected"], backward_joins=[],
                        views=[dict(name="portable", binding=binding, status="CURRENT",
                                    evidence_scope=g["original_scope"], authority="NONE")])
        for name in ("C1", "C2", "ADMIT", "PREP", "SIB"):
            n = by_id(g)[name]
            gates = {key: "SATISFIED" for key in coverage.GATES}
            if name == "ADMIT":
                gates["authority"] = "MISSING"
            direction = "FORWARD" if name == "PREP" else "OUTWARD"
            source_state = "DONE" if n["state"] == "DONE" else "PENDING"
            consumer = (n["future_consumer"] or dict(node=n["parent"]))["node"]
            edge = dict(id=name, at=n["parent"], direction=direction, state=source_state,
                        gates=gates, accepted=False, joined_into=None, owner=n["source_path"],
                        consumer=consumer, reconsider="material event", next_action="bounded scoped work",
                        evidence_scope=g["original_scope"])
            facts["edges"].append(edge)
            pending = {k: v for k, v in gates.items() if v != "SATISFIED"}
            row = {k: edge[k] for k in ("id", "direction", "owner", "consumer", "reconsider", "next_action", "evidence_scope")}
            row.update(binding=binding, eligibility="RETAINED" if source_state == "DONE" else "BLOCKED" if pending else "ELIGIBLE",
                       pending=pending, authority="NONE")
            proposal["edges"].append(row)
        assert coverage.violations(facts, proposal) == []
        no_dispatch = copy.deepcopy(proposal)
        no_dispatch["new_actions"] = []
        exact_facts = raw(facts)
        assert coverage.violations(facts, no_dispatch) == []
        assert raw(facts) == exact_facts
        # Both are honestly source-consistent. Runtime conformance has a
        # different accepting operation and must reject omitted execution.
        reject(lambda: wg.check_recursive_execution_v1(g, [], transition, [], []), "missing execution")
        executions, consumptions = [], []
        for name in transition["selected"]:
            out = Path(td) / (name + ".json")
            code = execute_manifest(root, g, transition, name, out)
            execution, consumption = consume_manifest(root, g, transition, name, out, code)
            executions.append(execution)
            consumptions.append(consumption)
        assert len({e["output_digest"] for e in executions}) == 2
        report = wg.check_recursive_execution_v1(g, [], transition, executions, consumptions)
        assert report["status"] == "PORTABLE_RECORDS_CONSUMED"
        assert by_id(g)["ADMIT"]["state"] == "BLOCKED"
        # The same real program succeeds against unrelated input bytes, but
        # the fixed consumer refuses them against the original selected graph.
        wrong_root = Path(td) / "wrong-root"
        (wrong_root / "inputs").mkdir(parents=True)
        for name in ("a", "b", "c"):
            (wrong_root / "inputs" / (name + ".txt")).write_text("unrelated input " + name + "\n")
        wrong_output = Path(td) / "wrong-output.json"
        wrong_exit = execute_manifest(wrong_root, g, transition, "PREP", wrong_output)
        reject(lambda: consume_manifest(root, g, transition, "PREP", wrong_output, wrong_exit), "binding mismatch")
        original = (root / "inputs/a.txt").read_bytes()
        (root / "inputs/a.txt").write_bytes(b"changed after execution\n")
        reject(lambda: consume_manifest(root, g, transition, "PREP", Path(td) / "PREP.json", 0), "binding mismatch")
        (root / "inputs/a.txt").write_bytes(original)
        reject(lambda: wg.check_recursive_execution_v1(g, [], transition, executions[:1], consumptions[:1]), "missing execution")
        for key, value in (("input_digest", "0" * 64), ("input_root_identity", "0" * 64), ("read_set", {})):
            foreign_input = copy.deepcopy(executions)
            foreign_input[0][key] = value
            reject(lambda: wg.check_recursive_execution_v1(g, [], transition, foreign_input, consumptions), "input binding")
        foreign = copy.deepcopy(consumptions)
        foreign[0]["consumer"] = "ROOT"
        reject(lambda: wg.check_recursive_execution_v1(g, [], transition, executions, foreign), "consumer")
        foreign = copy.deepcopy(consumptions)
        foreign[0]["input_digest"] = "0" * 64
        reject(lambda: wg.check_recursive_execution_v1(g, [], transition, executions, foreign), "consumer input")
        replay = wg.compile_recursive_transition_v1(g, [report["event_receipt"]])
        assert replay["selected"] == [] and replay["mode"] == "NO_REDISPATCH"
        assert wg.check_recursive_execution_v1(g, [report["event_receipt"]], replay, [], [])["status"] == "NO_REDISPATCH_AT_SUPPLIED_HISTORY"
        reminder_controls(root, state, nodes, g, report, Path(td) / "reminder-controls")
        changed = copy.deepcopy(report["event_receipt"])
        changed["graph_digest"] = "0" * 64
        reject(lambda: wg.compile_recursive_transition_v1(g, [changed]), "event")
        omitted = copy.deepcopy(transition)
        omitted["ancestors"].pop()
        reject(lambda: wg.check_recursive_execution_v1(g, [], omitted, executions, consumptions), "digest")
        # Resealing cannot repair missing ancestry, siblings or selected work.
        for mutate in (lambda t: t["ancestors"].pop(),
                       lambda t: t["directions"].update(OUTWARD=[]),
                       lambda t: t.update(selected=[], consumers={})):
            omitted = copy.deepcopy(transition)
            mutate(omitted)
            omitted.pop("digest")
            omitted = wg._seal_graph(omitted)
            reject(lambda: wg.check_recursive_execution_v1(g, [], omitted, [], []), "source-derived")
        print("native-work-graph: held-out selected PREP/SIB; real subprocess outputs consumed; ADMIT remains BLOCKED")
        print("native-work-graph: matched no-dispatch control rejected; no native campaign or host prevention claim")
        print("native-work-graph: unchanged donor coverage checker accepts both identical-facts projections at consistency scope only")

        # Native acquisition must use the existing genuine continuity owner.
        # This checkout has no native controller; do not manufacture a receipt.
        completed = subprocess.run([sys.executable, str(REPO / "skills/implementaudit/scripts/compile-work-graph.py"),
                                    "--native-run", str(root), str(REPO)], capture_output=True)
        assert completed.returncode == 2
        assert b"continuity" in completed.stderr, completed.stderr
        for count in (0, 1, 2):
            assert wg.cheap_path_v1(count, count, 8)["graph_required"] is False
        assert wg.cheap_path_v1(7, 1, 8)["graph_required"] is False
        assert wg.cheap_path_v1(7, 4, 8)["graph_required"] is True
    print("native-work-graph.test: ok")


if __name__ == "__main__":
    main()
