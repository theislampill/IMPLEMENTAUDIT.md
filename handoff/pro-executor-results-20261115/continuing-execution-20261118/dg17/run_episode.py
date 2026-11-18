#!/usr/bin/env python3
"""Original N11/H04 structural consumer episode; no native or model acceptance."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def node(name, parent="OWNED_OBJECT", kind="TASK", **changes):
    value = dict(id=name, parent=parent, kind=kind, state="OPEN", requires=[],
                 optional=[], reads=[], writes=[], acceptance=[], resources=[],
                 authority=[], effect="READ_ONLY", authorization="PERMITTED",
                 independence="KNOWN", resource_demand=1, rank=0, route_scopes=[],
                 logical_delivery=None, future_consumer=None, invalidators=[],
                 independent_results=False, done_evidence=None,
                 context=dict(locality="GOVERNOR", governor_cost=1, child_cost=2,
                              return_cost=1, useful_value=5))
    value.update(changes)
    return value


PRODUCER = '''import hashlib,json,pathlib,sys
manifest=json.loads(pathlib.Path(sys.argv[2]).read_bytes())
root=pathlib.Path(sys.argv[3])
rows=[]
for member in manifest['members']:
 raw=(root/member['path']).read_bytes()
 observed=hashlib.sha256(raw).hexdigest()
 if len(raw)!=member['bytes'] or observed!=member['sha256']:
  raise SystemExit('source identity differs')
 rows.append(member['path']+'\\t'+str(len(raw))+'\\t'+observed)
inventory=('\\n'.join(rows)+'\\n').encode()
if sys.argv[1]=='inventory':
 sys.stdout.buffer.write(inventory)
elif sys.argv[1]=='consume':
 supplied=sys.stdin.buffer.read()
 if supplied!=inventory:
  raise SystemExit('received inventory differs from actual source')
 sys.stdout.write(json.dumps({'consumed_members':len(rows),'inventory_sha256':hashlib.sha256(supplied).hexdigest(),'source_commit':manifest['commit']},sort_keys=True)+'\\n')
else:
 raise SystemExit('unsupported operation')
'''


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--work", type=Path, required=True)
    args = parser.parse_args()
    work, source = args.work.resolve(), args.source.resolve()
    manifest = json.loads((work / "SOURCE_MANIFEST.json").read_bytes())
    assert manifest["commit"] == "a297957be11feb494c0ec467235794a1e0c54751"

    def check_source():
        for member in manifest["members"]:
            path = source / member["path"]
            raw = path.read_bytes()
            assert (len(raw), sha(raw), path.stat().st_mode & 0o777) == (
                member["bytes"], member["sha256"], int(member["mode"], 8))

    check_source()
    run, journal = work / "run", work / "journal"
    run.mkdir(exist_ok=False)
    (run / "inputs").mkdir()
    (run / "inputs/manifest.json").write_bytes(canonical(manifest) + b"\n")
    (work / "producer.py").write_text(PRODUCER)
    observations = work / "observations"
    observations.mkdir(exist_ok=False)
    nodes = [
        node("OWNED_OBJECT", None, "PLAN", requires=["FINAL_REDUCER"]),
        node("ORCHID_INDEX", reads=["path:inputs/manifest.json"], rank=3,
             future_consumer=dict(node="RETURN_REDUCER", condition="exact three-source inventory")),
        node("RETURN_REDUCER", kind="JOIN", requires=["ORCHID_INDEX"],
             future_consumer=dict(node="FINAL_REDUCER", condition="governor-owned reduction")),
        node("ACTUAL_READER", requires=["RETURN_REDUCER"], reads=["path:inputs/manifest.json"], rank=1,
             future_consumer=dict(node="FINAL_REDUCER", condition="consume actual inventory bytes")),
        node("FINAL_REDUCER", kind="JOIN", requires=["ACTUAL_READER"]),
    ]
    state = dict(schema="implementaudit.native-state.v1", campaign="dg17-owned-join-source-20261118",
                 root="OWNED_OBJECT", original_scope="Original N11 H04 structural authority facts only",
                 nodes=[n["id"] for n in nodes],
                 event=dict(id="constructed-document-input", kind="RETURN", subject="ORCHID_INDEX"),
                 context=dict(host_capacity=1, operator_ceiling=None, reserve=0,
                              route_facts=[], outstanding_deliveries=[]))
    values = {"STATE.md": state, "ROADMAP.md": dict(schema="implementaudit.native-roadmap.v1", phases=[])}
    for value in nodes:
        folder = "plans" if value["kind"] == "PLAN" else "tasks"
        values[folder + "/" + value["id"] + ".md"] = dict(schema="implementaudit.native-spec.v1", nodes=[value])
    for name, value in values.items():
        path = run / name
        path.parent.mkdir(exist_ok=True)
        path.write_bytes(b"```implementaudit-work-graph\n" + canonical(value) + b"\n```\n")
    graph_preimage = {str(p.relative_to(run)): sha(p.read_bytes()) for p in run.rglob("*") if p.is_file()}
    captures = []

    def execute(mode, stdin=b""):
        command = [sys.executable, "-I", "-B", str(work / "producer.py"), mode,
                   str(run / "inputs/manifest.json"), str(source)]
        started = time.time_ns()
        process = subprocess.Popen(command, cwd=work, env={"PATH": "/usr/bin:/bin", "LANG": "C.UTF-8",
                                   "PYTHONDONTWRITEBYTECODE": "1"}, stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True)
        pgid = os.getpgid(process.pid)
        timed_out = False
        try:
            stdout, stderr = process.communicate(stdin, timeout=10)
        except subprocess.TimeoutExpired:
            timed_out = True
            os.killpg(pgid, signal.SIGKILL)
            stdout, stderr = process.communicate(timeout=5)
        ended = time.time_ns()
        try:
            os.killpg(pgid, 0)
        except ProcessLookupError:
            absent = True
        else:
            absent = False
        row = dict(operation=mode, argv=command, cwd=str(work), pid=process.pid, owned_pgid=pgid,
                   started_ns=started, ended_ns=ended, exit_code=process.returncode, timed_out=timed_out,
                   owned_process_group_absent=absent,
                   stdin=dict(bytes=len(stdin), sha256=sha(stdin)),
                   stdout=dict(bytes=len(stdout), sha256=sha(stdout), file=mode + ".stdout"),
                   stderr=dict(bytes=len(stderr), sha256=sha(stderr), file=mode + ".stderr"))
        (observations / row["stdout"]["file"]).write_bytes(stdout)
        (observations / row["stderr"]["file"]).write_bytes(stderr)
        (observations / (mode + ".stdin")).write_bytes(stdin)
        (observations / (mode + ".json")).write_bytes(canonical(row) + b"\n")
        captures.append(row)
        assert not timed_out and absent and process.returncode == 0 and not stderr, row
        return stdout

    spec = importlib.util.spec_from_file_location("dg17_exact_a297_completion", source / "scripts/work-graph-completion.py")
    owner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(owner)
    compiler_sha = next(m["sha256"] for m in manifest["members"] if m["path"].endswith("compile-work-graph.py"))
    snapshots = {}

    def returned(frontier, name, output):
        return dict(schema="implementaudit.work-result.v1", node=name, dispatch_id=frontier["dispatch_id"],
                    graph_digest=frontier["graph_digest"], input_digest=frontier["inputs"][name],
                    status="PASS", terminal=True, exit_code=0, evidence_digest=sha(output),
                    independence_key="actual-process-" + name, scope=[name])

    with owner.CompletionContract(run, journal, compiler_sha256=compiler_sha) as consumer:
        initial = consumer.frontier()
        assert initial["selected"] == ["ORCHID_INDEX"]
        snapshots["before_lane"] = initial
        inventory = execute("inventory")
        result = returned(initial, "ORCHID_INDEX", inventory)
        lane_event = consumer.accept(initial, [result], "RETURN_REDUCER", expected_old=consumer.history_digest)
        omitted = consumer.frontier()
        snapshots["lane_received_join_omitted"] = omitted
        assert omitted["states"]["ORCHID_INDEX"] == "DONE"
        assert omitted["states"]["ACTUAL_READER"] == "BLOCKED"
        assert omitted["selected"] == ["RETURN_REDUCER"]
        assert not any(r["operation"] == "consume" for r in captures)
        before = (journal / "history.json").read_bytes()
        before_digest = consumer.history_digest
        forged = returned(omitted, "RETURN_REDUCER", inventory)
        try:
            consumer.accept(omitted, [forged], "FINAL_REDUCER", expected_old=before_digest)
        except owner.CompletionError as failure:
            refusal = str(failure)
        else:
            raise AssertionError("supplied child/lane JOIN was accepted")
        assert refusal == "JOIN completion requires the shared JOIN reducer"
        assert before == (journal / "history.json").read_bytes() and before_digest == consumer.history_digest
        after_refusal = consumer.frontier()
        snapshots["after_supplied_join_refusal"] = after_refusal
        assert after_refusal["states"]["ACTUAL_READER"] == "BLOCKED"
        joined = consumer.join("RETURN_REDUCER", expected_old=consumer.history_digest)
        assert joined["status"] == "SATISFIED_AT_DECLARED_RESULT_CONTRACT"
        ready = consumer.frontier()
        snapshots["governor_reduced_join"] = ready
        assert ready["selected"] == ["ACTUAL_READER"]
        consumed = execute("consume", inventory)
        consumer.accept(ready, [returned(ready, "ACTUAL_READER", consumed)], "FINAL_REDUCER",
                        expected_old=consumer.history_digest)
        final_join = consumer.join("FINAL_REDUCER", expected_old=consumer.history_digest)
        assert final_join["status"] == "SATISFIED_AT_DECLARED_RESULT_CONTRACT"
        final = consumer.transition()
        snapshots["after_actual_consumer"] = final
        assert final["states"]["OWNED_OBJECT"] != "DONE"
        assert final["authority"] == "NONE" and final["native_dispatch_authorized"] is False
        final_digest = consumer.history_digest
    check_source()
    assert graph_preimage == {str(p.relative_to(run)): sha(p.read_bytes()) for p in run.rglob("*") if p.is_file()}
    evidence = dict(schema="dg17.N11-H04-source-consumer-episode.v1", authority="NONE",
                    source=manifest, source_after_identical=True, graph_after_identical=True,
                    construction="Graph documents and adversarial result envelope are explicitly constructed; two process executions and consumer refusals are actual.",
                    original_N11=dict(scenario="DAG JOIN attributed to child/lane result", expected="JOIN remains governor/DAG-owned"),
                    original_H04=dict(scenario="Unfamiliar DAG lane valid but JOIN omitted", expected="L2/L5 cannot consume; cognition cannot fill JOIN"),
                    observed_scope="Portable declared-result structural authority facts and actual read-only process/consumer behavior only",
                    mutation=dict(origin="RECEIVER_CONSTRUCTED_ENVELOPE_OF_ACTUAL_LANE_OUTPUT", supplied=forged,
                                  refusal=refusal, journal_before_sha256=sha(before), journal_after_refusal_sha256=sha(before),
                                  history_digest_unchanged=before_digest),
                    lane_event=lane_event, governor_join=joined, final_join=final_join,
                    final_history_digest=final_digest, captures=captures, snapshots=snapshots,
                    whole_case_award=False, native_session=False, native_Stop=False, model_control=False,
                    audit_closure=False, unresolved_processes=[])
    target = work / "evidence.json"
    target.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n")
    print(json.dumps(dict(status="OBSERVED_SOURCE_STRUCTURAL_SCOPE", evidence_bytes=target.stat().st_size,
                          evidence_sha256=sha(target.read_bytes()), source_commit=manifest["commit"],
                          actual_readonly_processes=len(captures), missing_join_successor="BLOCKED",
                          supplied_join_refusal=refusal, governor_join=joined["status"],
                          actual_consumer_exit=captures[-1]["exit_code"], root_state=final["states"]["OWNED_OBJECT"],
                          authority="NONE", whole_case_award=False, native_claim=False), indent=2))


if __name__ == "__main__":
    main()
