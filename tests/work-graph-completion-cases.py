"""Portable completion contracts; never authentic native acceptance receipts."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

REPO = Path(__file__).resolve().parents[1]

def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()

def node(name, parent="ROOT", kind="TASK", **kw):
    value = dict(id=name, parent=parent, kind=kind, state="OPEN", requires=[],
                 optional=[], reads=[], writes=[], acceptance=[], resources=[],
                 authority=[], effect="READ_ONLY", authorization="PERMITTED",
                 independence="KNOWN", resource_demand=1, rank=0, route_scopes=[],
                 logical_delivery=None, future_consumer=None, invalidators=[],
                 independent_results=False, done_evidence=None,
                 context=dict(locality="GOVERNOR", governor_cost=1, child_cost=2,
                              return_cost=1, useful_value=5))
    value.update(kw)
    return value

class CompletionCases(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location("completion", REPO / "scripts/work-graph-completion.py")
        cls.owner = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.owner)

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="r0035-completion-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.run = self.root / "run"
        self.run.mkdir()
        self.nodes = [node("ROOT", None, "PLAN", requires=["NEXT"]),
                      node("A", reads=["path:inputs/a"], rank=4,
                           future_consumer=dict(node="JOIN", condition="exact retained output")),
                      node("B", reads=["path:inputs/b"], rank=3,
                           future_consumer=dict(node="JOIN", condition="exact retained output")),
                      node("JOIN", kind="JOIN", requires=["A", "B"]),
                      node("NEXT", requires=["JOIN"], reads=["path:inputs/next"],
                           future_consumer=dict(node="FINAL", condition="successor output")),
                      node("FINAL", kind="JOIN", requires=["NEXT"]),
                      node("EXTERNAL", effect="EXTERNAL", authorization="MISSING")]
        self.state = dict(schema="implementaudit.native-state.v1", campaign="portable-contract",
                          root="ROOT", original_scope="process-backed consumer controls",
                          nodes=[n["id"] for n in self.nodes],
                          event=dict(id="event-1", kind="RETURN", subject="A"),
                          context=dict(host_capacity=1, operator_ceiling=None, reserve=0,
                                       route_facts=[], outstanding_deliveries=[]))
        self.write_source()
        (self.run / "inputs").mkdir()
        for name in ("a", "b", "next"):
            (self.run / "inputs" / name).write_text(name + "\n")
        self.consumer = self.owner.CompletionContract(self.run, self.root / "journal")
        self.addCleanup(self.consumer.close)

    def write_source(self):
        values = {"STATE.md": self.state,
                  "ROADMAP.md": dict(schema="implementaudit.native-roadmap.v1", phases=[])}
        for value in self.nodes:
            directory = "plans" if value["kind"] == "PLAN" else "tasks"
            values[directory + "/" + value["id"] + ".md"] = dict(
                schema="implementaudit.native-spec.v1", nodes=[value])
        for name, value in values.items():
            path = self.run / name
            path.parent.mkdir(exist_ok=True)
            path.write_bytes(b"```implementaudit-work-graph\n" + canonical(value) + b"\n```\n")

    def result(self, frontier, name, status="PASS", output=None):
        if output is None:
            source = self.run / "inputs" / name.lower()
            observed = subprocess.run([sys.executable, "-I", "-S", "-B", "-c",
                                       "import pathlib,sys;sys.stdout.buffer.write(pathlib.Path(sys.argv[1]).read_bytes())",
                                       str(source)], capture_output=True, check=True)
            output = observed.stdout
        return dict(schema="implementaudit.work-result.v1", node=name,
                    dispatch_id=frontier["dispatch_id"], graph_digest=frontier["graph_digest"],
                    input_digest=frontier["inputs"][name], status=status,
                    terminal=status != "PENDING", exit_code=0 if status == "PASS" else None,
                    evidence_digest=hashlib.sha256(output).hexdigest(),
                    independence_key="process-" + name, scope=[name])

    def accept(self, name, consumer="JOIN", status="PASS", output=None):
        frontier = self.consumer.frontier()
        self.assertIn(name, frontier["selected"])
        result = self.result(frontier, name, status, output)
        receipt = self.consumer.accept(frontier, [result], consumer,
                                       expected_old=self.consumer.history_digest)
        return frontier, result, receipt

    def test_capacity_one_two_batches_join_and_actual_successor(self):
        self.assertEqual(self.consumer.frontier()["selected"], ["A"])
        self.accept("A")
        partial = self.consumer.join("JOIN", expected_old=self.consumer.history_digest)
        self.assertEqual(partial["status"], "PENDING")
        self.assertEqual(partial["missing"], ["B"])
        self.assertEqual(self.consumer.frontier()["selected"], ["B"])
        self.accept("B")
        joined = self.consumer.join("JOIN", expected_old=self.consumer.history_digest)
        self.assertEqual(joined["status"], "SATISFIED_AT_DECLARED_RESULT_CONTRACT")
        self.assertEqual(self.consumer.frontier()["selected"], ["NEXT"])
        a, b = ((self.run / "inputs" / x).read_bytes() for x in ("a", "b"))
        consumed = subprocess.run([sys.executable, "-I", "-S", "-B", "-c",
                                  "import sys;sys.stdout.buffer.write(sys.stdin.buffer.read().upper())"],
                                 input=a + b, capture_output=True, check=True).stdout
        self.accept("NEXT", "FINAL", output=consumed)
        self.consumer.join("FINAL", expected_old=self.consumer.history_digest)
        view = self.consumer.frontier()
        self.assertEqual(view["selected"], [])
        self.assertNotEqual(view["states"]["ROOT"], "DONE")
        self.assertEqual(view["authority"], "NONE")
        self.assertFalse(view["native_dispatch_authorized"])

    def test_changed_input_preserves_other_result_and_invalidates_join(self):
        self.accept("A")
        self.accept("B")
        self.consumer.join("JOIN", expected_old=self.consumer.history_digest)
        self.assertEqual(self.consumer.frontier()["selected"], ["NEXT"])
        (self.run / "inputs/a").write_text("changed\n")
        view = self.consumer.frontier()
        self.assertEqual(view["selected"], ["A"])
        self.assertEqual(view["states"]["B"], "DONE")
        self.assertEqual(view["states"]["JOIN"], "BLOCKED")
        self.assertEqual(view["states"]["NEXT"], "BLOCKED")
        self.assertTrue({"A", "JOIN"}.issubset(view["invalidated"]))

    def test_stale_dispatch_refuses_old_graph_replay(self):
        view = self.consumer.frontier()
        result = self.result(view, "A")
        (self.run / "inputs/a").write_text("changed\n")
        for unused in range(2):
            with self.assertRaisesRegex(self.owner.CompletionError, "stale"):
                self.consumer.accept(view, [result], "JOIN", expected_old=self.consumer.history_digest)
        self.assertEqual(self.consumer.frontier()["states"]["A"], "READY")

    def test_imported_or_modified_frontier_refuses(self):
        view = self.consumer.frontier()
        with self.assertRaisesRegex(self.owner.CompletionError, "issued"):
            self.consumer.accept(copy.deepcopy(view), [self.result(view, "A")], "JOIN",
                                 expected_old=self.consumer.history_digest)
        result = self.result(view, "A")
        view["selected"].append("EXTERNAL")
        with self.assertRaisesRegex(self.owner.CompletionError, "modified"):
            self.consumer.accept(view, [result], "JOIN", expected_old=self.consumer.history_digest)

    def test_duplicate_foreign_and_contradictory_results_refuse(self):
        view = self.consumer.frontier()
        result = self.result(view, "A")
        for results in ([result, result], [dict(result, scope=["ROOT"])],
                        [dict(result, node="EXTERNAL")], [dict(result, terminal=False)],
                        [dict(result, exit_code=True)], [dict(result, status=["PASS"])]):
            with self.subTest(results=results):
                with self.assertRaises(self.owner.CompletionError):
                    self.consumer.accept(view, results, "JOIN", expected_old=self.consumer.history_digest)
        with self.assertRaisesRegex(self.owner.CompletionError, "consumer"):
            self.consumer.accept(view, [result], "FINAL", expected_old=self.consumer.history_digest)

    def test_failures_and_interruption_preserve_independent_preparation(self):
        for status in ("FAIL", "PARTIAL", "PENDING", "INTERRUPTED", "NONVERDICT", "TRANSPORT_FAILURE"):
            with self.subTest(status=status):
                with self.owner.CompletionContract(self.run, self.root / ("journal-" + status)) as consumer:
                    view = consumer.frontier()
                    consumer.accept(view, [self.result(view, "A", status)], "JOIN",
                                    expected_old=consumer.history_digest)
                    joined = consumer.join("JOIN", expected_old=consumer.history_digest)
                    self.assertNotEqual(joined["status"], "SATISFIED_AT_DECLARED_RESULT_CONTRACT")
                    view = consumer.frontier()
                    self.assertNotEqual(view["states"]["A"], "DONE")
                    self.assertEqual(view["selected"], ["B"])

    def test_unbound_source_done_is_held(self):
        self.nodes[1].update(state="DONE", done_evidence="d" * 64)
        self.write_source()
        view = self.consumer.frontier()
        self.assertEqual(view["states"]["A"], "BLOCKED")
        self.assertIn("UNBOUND_SOURCE_COMPLETION", view["blocked"]["A"])

    def test_active_occupancy_and_effect_holds_remain(self):
        self.nodes[2]["state"] = "ACTIVE"
        self.write_source()
        view = self.consumer.frontier()
        self.assertEqual(view["active_occupancy"], 1)
        self.assertEqual(view["selected"], [])
        self.assertIn("EFFECT_EXECUTOR_UNAVAILABLE", view["blocked"]["EXTERNAL"])
        self.assertIn("AUTHORIZATION", view["blocked"]["EXTERNAL"])

    def test_expected_old_and_single_writer(self):
        old = self.consumer.history_digest
        self.accept("A")
        with self.assertRaisesRegex(self.owner.CompletionError, "expected-old"):
            self.consumer.join("JOIN", expected_old=old)
        with self.assertRaisesRegex(self.owner.CompletionError, "writer"):
            self.owner.CompletionContract(self.run, self.root / "journal")

    def test_restart_never_restores_acceptance_from_json(self):
        self.accept("A")
        old = self.consumer.history_digest
        self.consumer.close()
        with self.owner.CompletionContract(self.run, self.root / "journal") as recovered:
            self.assertEqual(recovered.history_digest, old)
            view = recovered.frontier()
            self.assertEqual(view["recovery_status"], "PRODUCER_REOBSERVATION_REQUIRED")
            self.assertEqual(view["states"]["A"], "BLOCKED")
            self.assertIn("COMPLETION_RECOVERY_CUSTODY_UNVERIFIED", view["blocked"]["A"])
            self.assertEqual(view["selected"], ["B"])

    def test_failed_journal_commit_holds_same_process_and_restart(self):
        from unittest.mock import patch
        view = self.consumer.frontier()
        result = self.result(view, "A")
        with patch.object(self.owner.os, "replace", side_effect=OSError("injected precommit interruption")):
            with self.assertRaises(OSError):
                self.consumer.accept(view, [result], "JOIN", expected_old=self.consumer.history_digest)
        self.assertTrue(list((self.root / "journal").glob("pending-*.json")))
        with self.assertRaisesRegex(self.owner.CompletionError, "pending"):
            self.consumer.frontier()
        self.consumer.close()
        with self.assertRaisesRegex(self.owner.CompletionError, "pending"):
            self.owner.CompletionContract(self.run, self.root / "journal")

    def test_torn_or_tampered_history_is_never_repaired_or_imported(self):
        self.accept("A")
        self.consumer.close()
        path = self.root / "journal/history.json"
        original = path.read_bytes()
        for value in (original[:-3], original.replace(b'"status":"PASS"', b'"status":"FAIL"')):
            path.write_bytes(value)
            with self.assertRaises(ValueError):
                self.owner.CompletionContract(self.run, self.root / "journal")
            self.assertEqual(path.read_bytes(), value)

    def test_optional_omission_and_independence_use_original_join_rules(self):
        self.nodes.append(node("OPTIONAL", authorization="MISSING"))
        self.state["nodes"].append("OPTIONAL")
        self.nodes[3]["optional"] = ["OPTIONAL"]
        self.nodes[3]["independent_results"] = True
        self.write_source()
        self.accept("A")
        self.accept("B")
        joined = self.consumer.join("JOIN", expected_old=self.consumer.history_digest)
        self.assertEqual(joined["status"], "SATISFIED_AT_DECLARED_RESULT_CONTRACT")
        self.assertEqual(joined["omitted_optional"], ["OPTIONAL"])
        self.assertNotIn("OPTIONAL", joined["retained_scopes"])

    def test_common_cause_results_cannot_satisfy_independent_join(self):
        self.nodes[2]["reads"] = ["path:inputs/a"]
        self.nodes[3]["independent_results"] = True
        self.write_source()
        self.accept("A")
        self.accept("B")
        joined = self.consumer.join("JOIN", expected_old=self.consumer.history_digest)
        self.assertEqual(joined["status"], "NONVERDICT")
        self.assertNotEqual(self.consumer.frontier()["states"]["JOIN"], "DONE")

    def test_join_does_not_bypass_authorization(self):
        self.nodes[3]["authorization"] = "MISSING"
        self.write_source()
        self.accept("A")
        self.accept("B")
        with self.assertRaisesRegex(self.owner.CompletionError, "holds"):
            self.consumer.join("JOIN", expected_old=self.consumer.history_digest)
        self.assertEqual(self.consumer.frontier()["states"]["JOIN"], "BLOCKED")

    def test_unchanged_reminder_retains_results_and_changed_premise_invalidates(self):
        self.accept("A")
        self.state["event"] = dict(id="reminder-2", kind="REMINDER", subject="B")
        self.write_source()
        self.assertEqual(self.consumer.frontier()["selected"], ["B"])
        self.nodes[1]["acceptance"] = ["scope:new-acceptance-premise"]
        self.write_source()
        self.assertEqual(self.consumer.frontier()["selected"], ["A"])

    def test_join_obeys_capacity_resource_and_context_selection(self):
        for kind in ("capacity", "resource", "context"):
            with self.subTest(kind=kind):
                if kind == "capacity": self.nodes[3]["resource_demand"] = 2
                if kind == "resource":
                    self.nodes[3]["resource_demand"] = 1
                    self.state["context"]["host_capacity"] = 2
                    self.nodes[3]["resources"] = ["scope:join-lease"]
                    self.nodes.append(node("BUSY", state="ACTIVE", resources=["scope:join-lease"]))
                    self.state["nodes"].append("BUSY")
                if kind == "context":
                    self.nodes[3]["resources"] = []
                    self.nodes[3]["context"]["useful_value"] = 0
                self.write_source()
                with self.owner.CompletionContract(self.run, self.root / ("hold-" + kind)) as c:
                    for name in ("A", "B"):
                        view = c.frontier()
                        c.accept(view, [self.result(view, name)], "JOIN", expected_old=c.history_digest)
                    view = c.frontier()
                    self.assertEqual(view["states"]["JOIN"], "READY")
                    self.assertNotIn("JOIN", view["selected"])
                    old = c.history_digest
                    with self.assertRaisesRegex(self.owner.CompletionError, "select"):
                        c.join("JOIN", expected_old=old)
                    self.assertEqual(c.history_digest, old)

    def test_supplied_join_pass_cannot_override_nonverdict(self):
        self.nodes[2]["reads"] = ["path:inputs/a"]
        self.nodes[3]["independent_results"] = True
        self.nodes[3]["future_consumer"] = dict(node="UPPER", condition="required join")
        self.nodes.append(node("UPPER", kind="JOIN", requires=["JOIN"]))
        self.state["nodes"].append("UPPER")
        self.write_source()
        self.accept("A"); self.accept("B")
        view = self.consumer.frontier()
        self.assertEqual(self.consumer.join("JOIN", expected_old=self.consumer.history_digest)["status"], "NONVERDICT")
        with self.assertRaisesRegex(self.owner.CompletionError, "JOIN"):
            self.consumer.accept(view, [self.result(view, "JOIN", output=b"forged supplied JOIN")],
                                 "UPPER", expected_old=self.consumer.history_digest)

    def test_same_dispatch_partial_returns_retain_original_identities(self):
        self.state["context"]["host_capacity"] = 2
        self.write_source()
        view = self.consumer.frontier()
        results = {name:self.result(view, name) for name in ("A", "B")}
        self.consumer.accept(view, [results["A"]], "JOIN", expected_old=self.consumer.history_digest)
        self.consumer.accept(view, [results["B"]], "JOIN", expected_old=self.consumer.history_digest)
        recorded = [r["result"] for e in self.consumer.journal.value["events"] for r in e["body"]["records"]]
        self.assertEqual(recorded, [results["A"], results["B"]])
        self.assertEqual(self.consumer.join("JOIN", expected_old=self.consumer.history_digest)["status"],
                         "SATISFIED_AT_DECLARED_RESULT_CONTRACT")

    def test_late_result_cannot_rebind_new_optional_predecessor_evidence(self):
        self.state["context"]["host_capacity"] = 2
        self.nodes[2]["optional"] = ["A"]
        self.write_source()
        view = self.consumer.frontier()
        a, b = self.result(view, "A"), self.result(view, "B")
        self.consumer.accept(view, [a], "JOIN", expected_old=self.consumer.history_digest)
        with self.assertRaisesRegex(self.owner.CompletionError, "predecessor"):
            self.consumer.accept(view, [b], "JOIN", expected_old=self.consumer.history_digest)

    def test_same_instance_concurrency_preserves_every_returned_commit(self):
        from unittest.mock import patch
        import threading
        self.state["context"]["host_capacity"] = 2
        self.write_source()
        c = self.consumer
        view = c.frontier()
        results = {name:self.result(view, name) for name in ("A", "B")}
        expected = c.history_digest
        parked, proceed, first_done = threading.Event(), threading.Event(), threading.Event()
        old_open = self.owner.os.open
        returned, errors = [], []
        def guarded_open(path, *args, **kw):
            if threading.current_thread().name == "held-B" and Path(path).name.startswith("pending-"):
                parked.set()
                if not proceed.wait(10): raise TimeoutError("test coordination")
            return old_open(path, *args, **kw)
        def invoke(name):
            try:
                returned.append(c.accept(view, [results[name]], "JOIN", expected_old=expected))
            except BaseException as exc: errors.append(exc)
            finally:
                if name == "A":first_done.set()
        with patch.object(self.owner.os, "open", side_effect=guarded_open):
            second = threading.Thread(target=invoke, args=("B",), name="held-B")
            second.start()
            self.assertTrue(parked.wait(10))
            first = threading.Thread(target=invoke, args=("A",), name="concurrent-A")
            first.start()
            first_done.wait(1)
            proceed.set()
            first.join(10); second.join(10)
        self.assertFalse(first.is_alive() or second.is_alive())
        disk = json.loads((self.root / "journal/history.json").read_bytes())
        committed = [r["node"] for e in disk["events"] for r in e["body"]["records"]]
        for event in returned:
            for r in event["body"]["records"]:self.assertIn(r["node"], committed)
        self.assertEqual(len(returned), 1)
        self.assertEqual(len(errors), 1)
        self.assertIsInstance(errors[0], self.owner.CompletionError)

    def test_native_entry_has_no_supplied_evidence_parameters(self):
        import inspect
        self.assertEqual(list(inspect.signature(self.owner.observe_fixed_native_completion).parameters),
                         ["run_root", "repo_root", "input_root"])

if __name__ == "__main__":
    unittest.main()
