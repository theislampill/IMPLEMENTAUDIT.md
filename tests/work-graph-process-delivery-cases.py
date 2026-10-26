"""Owned process and no-effect ledger controls; constructed evidence only."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest

REPO = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "pending_case_support", REPO / "tests/work-graph-pending-settlement-cases.py")
pending = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pending)
support = pending.support
DELIVERY = "fixed-no-effect-delivery"
LEDGER = "inputs/no-effect-ledger.json"


class ProcessDeliveryCases(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pending.PendingSettlementCases.setUpClass()

    def setUp(self):
        self.case = pending.PendingSettlementCases()
        self.case._testMethodName = self._testMethodName
        self.case.setUp()
        self.addCleanup(self.case.doCleanups)
        self.fixture = self.case.fixture
        self.c, self.run = self.case.consumer, self.case.run
        self.snapshots = self.case.snapshots
        self.outputs = {}
        self.snapshots["evidence_boundary"] = dict(
            acquisition="CONSTRUCTED_FILESYSTEM", authority="NONE",
            native_process_roster=False, actual_external_effect=False)

    def tearDown(self):
        self.case.tearDown()

    def node(self, name):
        return next(node for node in self.fixture.nodes if node["id"] == name)

    def add_preparation(self, name="PREP", rank=2):
        self.fixture.nodes.append(support.node(
            name, effect="PREPARATION", reads=["path:inputs/" + name.lower()], rank=rank,
            future_consumer=dict(node="FINAL", condition="observed independent preparation")))
        self.node("FINAL")["requires"].append(name)
        self.fixture.state["nodes"] = [node["id"] for node in self.fixture.nodes]
        (self.run / "inputs" / name.lower()).write_text(name.lower() + " output\n")

    def configure_processes(self, *, semantic_conflict=False):
        self.add_preparation()
        self.node("JOIN")["independent_results"] = True
        self.node("EXTERNAL")["authorization"] = "PERMITTED"
        self.fixture.state["context"]["host_capacity"] = 2
        if semantic_conflict:
            self.node("B")["resources"] = ["semantic:comparison-slot"]
            self.node("PREP")["resources"] = ["semantic:comparison-slot"]
            self.add_preparation("SIDE", rank=1)
        self.fixture.write_source()

    def fresh(self, label):
        graph = self.c.wg.read_native_run_v1(self.run)
        self.assertEqual(graph["binding"]["acquisition"], "CONSTRUCTED_FILESYSTEM")
        frontier = self.c.transition()
        self.assertEqual(frontier["source_graph_digest"], graph["digest"])
        self.assertEqual(frontier["authority"], "NONE")
        self.assertFalse(frontier["native_dispatch_authorized"])
        self.assertFalse(frontier["native_campaign_proven"])
        self.snapshots[label] = dict(
            frontier=frontier, acquisition=graph["binding"]["acquisition"],
            input_root_identity=graph["binding"]["input_root_identity"],
            read_set=graph["binding"]["read_set"], source_inventory=graph["source_inventory"],
            source_event=graph["event"], outstanding_deliveries=graph["context"]["outstanding_deliveries"])
        return frontier, graph

    def observe_alive(self, label, producers):
        observation = dict(monotonic_ns=time.monotonic_ns(), processes={})
        for name, producer in producers.items():
            status = producer.process.poll()
            self.assertIsNone(status, name + " must remain observably alive")
            observation["processes"][name] = dict(pid=producer.process.pid, poll=status)
        self.assertEqual(len({p.process.pid for p in producers.values()}), len(producers))
        self.snapshots[label] = observation

    def begin_pair(self):
        frontier, unused = self.fresh("initial_dispatch")
        self.assertEqual(frontier["selected"], ["A", "B"])
        producers = {name: self.case.start(name) for name in ("A", "B")}
        self.observe_alive("actual_overlap", producers)
        results = [dict(self.fixture.result(frontier, name, "PENDING", output=b""),
                        evidence_digest=None) for name in producers]
        self.snapshots["original_pending_event"] = self.c.accept(
            frontier, results, "JOIN", expected_old=self.c.history_digest)
        for name in producers:
            self.node(name)["state"] = "ACTIVE"
        # These are explicit test-owned source declarations, not a native roster.
        self.fixture.write_source()
        active, unused = self.fresh("both_active")
        self.assertEqual(active["active_occupancy"], 2)
        self.assertEqual([active["states"][name] for name in producers], ["ACTIVE", "ACTIVE"])
        return frontier, producers

    def return_process(self, frontier, name, producer, *, other_alive=None):
        output = producer.finish()
        producer.close()
        self.outputs[name] = output
        if other_alive:
            self.observe_alive(name + "_finished_while_other_alive", other_alive)
        self.assertEqual(producer.process.returncode, 0)
        self.node(name)["state"] = "OPEN"
        self.fixture.write_source()
        # Restore the finished producer's original declaration before using its
        # original pending dispatch. ACTIVE source drift is never ignored.
        result = self.fixture.result(frontier, name, output=output)
        event = self.c.accept(frontier, [result], "JOIN", expected_old=self.c.history_digest)
        self.snapshots[name + "_terminal_event"] = event
        return output

    def prepare(self, name="PREP", frontier=None):
        if frontier is None:
            frontier, unused = self.fresh(name + "_dispatch")
        self.assertIn(name, frontier["selected"])
        producer = self.case.start(name)
        output = producer.finish()
        producer.close()
        event = self.c.accept(frontier, [self.fixture.result(frontier, name, output=output)],
                              "FINAL", expected_old=self.c.history_digest)
        self.snapshots[name + "_preparation_event"] = event
        return output

    def join_pair(self):
        joined = self.c.join("JOIN", expected_old=self.c.history_digest)
        self.assertEqual(joined["status"], "SATISFIED_AT_DECLARED_RESULT_CONTRACT")
        self.assertEqual(joined["required"], ["A", "B"])
        self.assertEqual(joined["retained_scopes"], {"A": ["A"], "B": ["B"]})
        self.assertEqual(joined["authority"], "NONE")
        self.assertEqual(joined["lifecycle_credit"], "NONE")
        self.assertFalse(joined["native_dispatch_authorized"])
        history = self.case.history()
        self.assertEqual(history["events"][0], self.snapshots["original_pending_event"])
        latest = {record["node"]: record for event in history["events"]
                  for record in event["body"]["records"]}
        for name in ("A", "B"):
            self.assertEqual(latest[name]["result"]["evidence_digest"],
                             hashlib.sha256(self.outputs[name]).hexdigest())
            self.assertEqual(latest["JOIN"]["predecessors"][name], latest[name]["digest"])
        self.snapshots["required_join"] = joined
        self.assertNotEqual(self.c.frontier()["states"]["ROOT"], "DONE")

    def test_actual_overlap_partial_return_preparation_and_required_join(self):
        self.configure_processes()
        frontier, producers = self.begin_pair()
        self.return_process(frontier, "A", producers["A"], other_alive={"B": producers["B"]})
        partial, unused = self.fresh("one_finished_one_active")
        self.assertEqual(partial["states"]["A"], "DONE")
        self.assertEqual(partial["states"]["B"], "ACTIVE")
        self.assertEqual(partial["active_occupancy"], 1)
        self.assertEqual(partial["free_capacity"], 1)
        self.assertEqual(partial["selected"], ["PREP"])
        self.assertEqual(self.c.join("JOIN", expected_old=self.c.history_digest)["status"], "PENDING")
        self.prepare(frontier=partial)
        self.observe_alive("preparation_completed_while_b_alive", {"B": producers["B"]})
        self.return_process(frontier, "B", producers["B"])
        self.join_pair()
        # An actual successor reads the retained A/B bytes through its declared input.
        combined = self.outputs["A"] + self.outputs["B"]
        (self.run / "inputs/next").write_bytes(combined)
        next_frontier, unused = self.fresh("actual_output_consumer_dispatch")
        self.assertEqual(next_frontier["selected"], ["NEXT"])
        consumer = self.case.start("NEXT")
        consumed = consumer.finish()
        consumer.close()
        self.assertEqual(consumed, combined)
        self.c.accept(next_frontier, [self.fixture.result(next_frontier, "NEXT", output=consumed)],
                      "FINAL", expected_old=self.c.history_digest)
        final = self.c.join("FINAL", expected_old=self.c.history_digest)
        self.assertEqual(final["status"], "SATISFIED_AT_DECLARED_RESULT_CONTRACT")
        self.snapshots["actual_output_consumer"] = dict(output=consumed.decode(), final=final)

    def test_live_active_occupancy_capacity_contrast_preserves_preparation(self):
        self.configure_processes()
        frontier, producers = self.begin_pair()
        occupied, unused = self.fresh("capacity_two_fully_occupied")
        self.assertEqual(occupied["capacity"], 2)
        self.assertEqual(occupied["free_capacity"], 0)
        self.assertEqual(occupied["selected"], [])
        self.assertEqual(occupied["deferred"]["PREP"], "CAPACITY")
        self.fixture.state["context"]["host_capacity"] = 3
        self.fixture.write_source()
        available, unused = self.fresh("capacity_three_one_slot_available")
        self.assertEqual(available["active_occupancy"], 2)
        self.assertEqual(available["free_capacity"], 1)
        self.assertEqual(available["selected"], ["PREP"])
        self.prepare(frontier=available)
        self.observe_alive("preparation_completed_while_both_alive", producers)
        self.return_process(frontier, "A", producers["A"], other_alive={"B": producers["B"]})
        self.return_process(frontier, "B", producers["B"])
        self.join_pair()

    def test_live_semantic_conflict_and_disjoint_preparation_contrast(self):
        self.configure_processes(semantic_conflict=True)
        frontier, producers = self.begin_pair()
        self.fixture.state["context"]["host_capacity"] = 3
        self.fixture.write_source()
        conflicting, unused = self.fresh("semantic_conflict_with_free_capacity")
        self.assertEqual(conflicting["free_capacity"], 1)
        self.assertEqual(conflicting["deferred"]["PREP"], "CONFLICT")
        self.assertEqual(conflicting["selected"], ["SIDE"])
        self.prepare("SIDE", frontier=conflicting)
        self.observe_alive("disjoint_side_completed_while_both_alive", producers)
        self.node("PREP")["resources"] = []
        self.fixture.write_source()
        disjoint, unused = self.fresh("same_capacity_without_semantic_overlap")
        self.assertEqual(disjoint["active_occupancy"], 2)
        self.assertEqual(disjoint["free_capacity"], 1)
        self.assertEqual(disjoint["selected"], ["PREP"])
        self.assertNotIn("PREP", disjoint["deferred"])
        self.prepare(frontier=disjoint)
        self.observe_alive("formerly_conflicting_preparation_completed", producers)
        self.return_process(frontier, "A", producers["A"], other_alive={"B": producers["B"]})
        self.return_process(frontier, "B", producers["B"])
        self.join_pair()

    def configure_delivery_probes(self):
        self.add_preparation()
        self.fixture.state["context"]["host_capacity"] = 3
        for name in ("A", "B"):
            self.node(name)["logical_delivery"] = DELIVERY
            self.node(name)["reads"].append("path:" + LEDGER)
            self.assertEqual(self.node(name)["effect"], "READ_ONLY")
        self.node("EXTERNAL")["authorization"] = "PERMITTED"
        self.fixture.write_source()
        self.write_ledger([])
        self.publish_ledger_source()
        baseline, graph = self.fresh("delivery_probe_baseline_without_hold")
        self.assertEqual(baseline["selected"], ["A", "B", "PREP"])
        for name in ("A", "B"):
            self.assertEqual(baseline["states"][name], "READY")
            self.assertNotIn(name, baseline["blocked"])
        self.assertEqual(baseline["blocked"]["EXTERNAL"], ["EFFECT_EXECUTOR_UNAVAILABLE"])
        self.assert_ledger_read(graph)
        return baseline

    def write_ledger(self, transactions):
        # Fixed test-owned NO-EFFECT data; this is not an operational adapter.
        value = dict(schema="r0035.no-effect-delivery-ledger.v1", effect="NONE",
                     logical_delivery=DELIVERY, transactions=transactions)
        raw = support.canonical(value) + b"\n"
        path = self.run / LEDGER
        path.write_bytes(raw)
        path.chmod(0o600)
        acquired = path.read_bytes()
        self.assertEqual(acquired, raw)
        self.snapshots.setdefault("physical_ledger_versions", []).append(dict(
            raw=acquired.decode(), sha256=hashlib.sha256(acquired).hexdigest(),
            mode=path.stat().st_mode & 0o777, bytes=len(acquired)))

    def publish_ledger_source(self):
        raw = (self.run / LEDGER).read_bytes()
        value = json.loads(raw)
        self.assertEqual(value["effect"], "NONE")
        self.assertEqual(value["logical_delivery"], DELIVERY)
        transactions = value["transactions"]
        self.assertEqual(len({entry["transaction_id"] for entry in transactions}), len(transactions))
        self.assertEqual(len({entry["event_id"] for entry in transactions}), len(transactions))
        latest = transactions[-1] if transactions else None
        self.fixture.state["context"]["outstanding_deliveries"] = [] if latest is None else [dict(
            id=value["logical_delivery"], state=latest["state"],
            source_digest=hashlib.sha256(raw).hexdigest())]
        self.fixture.state["event"] = dict(id="ledger-empty" if latest is None else latest["event_id"],
                                           kind="REDERIVE", subject="A")
        self.fixture.write_source()

    def assert_ledger_read(self, graph):
        path = self.run / LEDGER
        raw = path.read_bytes()
        expected = hashlib.sha256(support.canonical(
            [path.stat().st_mode & 4095, hashlib.sha256(raw).hexdigest()])).hexdigest()
        self.assertEqual(graph["binding"]["read_set"]["path:" + LEDGER],
                         dict(status="PRESENT_FILE", sha256=expected))

    def assert_logical_hold_only(self, frontier, graph, state):
        for name in ("A", "B"):
            self.assertEqual(frontier["blocked"][name], ["LOGICAL_DELIVERY_HELD"])
        self.assertEqual(frontier["blocked"]["EXTERNAL"], ["EFFECT_EXECUTOR_UNAVAILABLE"])
        self.assertEqual(graph["context"]["outstanding_deliveries"], [dict(
            id=DELIVERY, state=state, source_digest=hashlib.sha256((self.run / LEDGER).read_bytes()).hexdigest())])
        self.assert_ledger_read(graph)

    def test_logical_hold_across_transaction_ids_preserves_independent_preparation(self):
        self.configure_delivery_probes()
        first = dict(transaction_id="transaction-one", event_id="delivery-event-one", state="PENDING")
        second = dict(transaction_id="transaction-two", event_id="delivery-event-two", state="UNKNOWN")
        self.write_ledger([first])
        self.publish_ledger_source()
        held, graph = self.fresh("pending_first_transaction")
        self.assert_logical_hold_only(held, graph, "PENDING")
        self.assertEqual(held["selected"], ["PREP"])
        self.prepare(frontier=held)
        self.write_ledger([first, second])
        self.publish_ledger_source()
        unknown, graph = self.fresh("unknown_second_transaction_same_logical_delivery")
        self.assert_logical_hold_only(unknown, graph, "UNKNOWN")
        self.assertNotEqual(held["event"]["id"], unknown["event"]["id"])
        self.assertNotEqual(held["source_graph_digest"], unknown["source_graph_digest"])
        self.assertEqual(unknown["states"]["PREP"], "DONE")
        self.assertEqual(unknown["selected"], [])
        self.assertEqual(self.c.join("JOIN", expected_old=self.c.history_digest)["status"], "PENDING")

    def test_physical_ledger_drift_refuses_stale_result_before_hold_projection(self):
        baseline = self.configure_delivery_probes()
        probe = self.case.start("A")
        terminal = self.fixture.result(baseline, "A", output=probe.finish())
        probe.close()
        self.prepare(frontier=baseline)
        changed = dict(transaction_id="transaction-current", event_id="delivery-event-current", state="PENDING")
        with self.assertRaisesRegex(self.c.wg.WorkGraphError, "inputs changed during intake") as closing:
            with self.c.wg.observe_native_run_v1(self.run) as provisional:
                self.snapshots["provisional_before_ledger_drift"] = dict(
                    sha256=hashlib.sha256(provisional).hexdigest(), accepted=False)
                self.write_ledger([changed])
        self.snapshots["ledger_closing_guard_refusal"] = str(closing.exception)
        changed_frontier, graph = self.fresh("new_bytes_before_source_hold_projection")
        self.assert_ledger_read(graph)
        self.assertEqual(graph["context"]["outstanding_deliveries"], [])
        self.assertEqual(changed_frontier["states"]["A"], "READY")
        self.assertNotEqual(changed_frontier["inputs"]["A"], baseline["inputs"]["A"])
        self.case.assert_refused_without_append(baseline, [terminal])
        self.assertEqual(changed_frontier["states"]["PREP"], "DONE")
        self.publish_ledger_source()
        held, graph = self.fresh("fresh_hold_from_current_ledger_bytes")
        self.assert_logical_hold_only(held, graph, "PENDING")
        self.assertEqual(held["states"]["PREP"], "DONE")
        self.assertEqual(len(self.case.history()["events"]), 1)


class ActualEffectReceivingCases(unittest.TestCase):
    """Actual disposable R0030 effects into the existing portable graph owner.

    The fixture governor publishes the existing logical-delivery hold. It is
    not an operational adapter, retry mechanism or native acceptance issuer.
    """
    @classmethod
    def setUpClass(cls):
        support.CompletionCases.setUpClass()

    def setUp(self):
        retained = os.environ.get("R0035_ACTUAL_EFFECT_RECEIVING_EVIDENCE")
        if retained:
            parent = Path(retained)
            parent.mkdir(parents=True, exist_ok=True)
            self.base = Path(tempfile.mkdtemp(prefix=self._testMethodName + "-", dir=parent))
        else:
            temporary = tempfile.TemporaryDirectory(prefix="actual-effect-receiving-")
            self.addCleanup(temporary.cleanup)
            self.base = Path(temporary.name)

    def producer(self, command):
        result = subprocess.run(command, cwd=REPO, capture_output=True, timeout=90)
        (self.base / "producer.stdout").write_bytes(result.stdout)
        (self.base / "producer.stderr").write_bytes(result.stderr)
        (self.base / "command.json").write_text(json.dumps(command) + "\n")
        self.assertEqual(result.returncode, 0, result.stdout.decode() + result.stderr.decode())
        return result

    def receive(self, raw, subject):
        before = {str(path.relative_to(subject)): hashlib.sha256(path.read_bytes()).hexdigest()
                  for path in subject.rglob("*") if path.is_file()}
        fixture = support.CompletionCases()
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        run, consumer = fixture.run, fixture.consumer
        delivery = "one-disposable-operation-across-new-transaction-ids"
        report_name = "inputs/actual-mutation-return.json"
        (run / report_name).write_bytes(raw)
        for name in ("A", "B"):
            node = next(row for row in fixture.nodes if row["id"] == name)
            node["logical_delivery"] = delivery
            node["reads"].append("path:" + report_name)
            # Distinct prospective transaction inputs do not erase the hold.
            (run / "inputs" / name.lower()).write_text("new-transaction-" + name + "\n")
        fixture.nodes.extend([
            support.node("PREP", effect="PREPARATION", rank=2, reads=["path:inputs/prep"],
                         future_consumer=dict(node="JOIN", condition="independent preparation")),
            support.node("OTHER_ACTIVE", state="ACTIVE"),
        ])
        fixture.state["nodes"].extend(["PREP", "OTHER_ACTIVE"])
        fixture.state["context"]["host_capacity"] = 4
        next(row for row in fixture.nodes if row["id"] == "JOIN")["optional"] = ["PREP"]
        (run / "inputs/prep").write_text("independent preparation\n")
        fixture.write_source()
        unprojected = consumer.transition()
        self.assertEqual(unprojected["selected"], ["A", "B", "PREP"])
        self.assertNotEqual(unprojected["inputs"]["A"], unprojected["inputs"]["B"])
        # This is an explicit fixture-governor receiving action over the actual
        # live return. A saved COMMITTED record cannot authorize a new delivery.
        fixture.state["context"]["outstanding_deliveries"] = [dict(
            id=delivery, state="UNKNOWN", source_digest=hashlib.sha256(raw).hexdigest())]
        fixture.state["event"] = dict(id="actual-effect-return-received", kind="REDERIVE", subject="A")
        fixture.write_source()
        held = consumer.transition()
        self.assertEqual(held["selected"], ["PREP"])
        self.assertEqual(held["active_occupancy"], 1)
        for name in ("A", "B"):
            self.assertEqual(held["blocked"][name], ["LOGICAL_DELIVERY_HELD"])
        self.assertNotIn("A", held["inputs"])
        self.assertNotIn("B", held["inputs"])
        self.assertFalse(held["native_dispatch_authorized"])
        self.assertEqual(held["authority"], "NONE")
        result = fixture.result(held, "PREP")
        consumer.accept(held, [result], "JOIN", expected_old=consumer.history_digest)
        joined = consumer.join("JOIN", expected_old=consumer.history_digest)
        self.assertEqual(joined["status"], "PENDING")
        self.assertEqual(joined["missing"], ["A", "B"])
        successor = consumer.transition()
        self.assertEqual(successor["states"]["PREP"], "DONE")
        self.assertEqual(successor["active_occupancy"], 1)
        self.assertNotEqual(successor["states"]["ROOT"], "DONE")
        self.assertNotIn("NEXT", successor["selected"])
        self.assertEqual({str(path.relative_to(subject)): hashlib.sha256(path.read_bytes()).hexdigest()
                          for path in subject.rglob("*") if path.is_file()}, before)
        receipt = dict(scope="ACTUAL_DISPOSABLE_EFFECT_TO_PORTABLE_GRAPH_RECEIVING",
            actual_return_sha256=hashlib.sha256(raw).hexdigest(),
            helper_sha256=hashlib.sha256((REPO / "skills/implementaudit/scripts/apply-observed-mutation.sh").read_bytes()).hexdigest(),
            compiler_sha256=hashlib.sha256((REPO / "skills/implementaudit/scripts/compile-work-graph.py").read_bytes()).hexdigest(),
            unprojected=unprojected, held=held, required_join=joined, successor=successor,
            effect_subject_unchanged_by_graph=True, native_authority=False,
            automatic_effect_to_hold_adapter=False, original_issue_acceptance=False)
        (self.base / "RECEIVING.json").write_text(json.dumps(receipt, indent=2) + "\n")

    def test_lost_batch_return_preserves_prefix_and_holds_both_new_deliveries(self):
        evidence = self.base / "batch"
        self.producer(["bash", str(REPO / "tests/observation-bound-mutation-integrity.test.sh"),
            "--replacement-batch-apply-heldouts", str(evidence), "DISPATCH_EXCEPTION_AFTER_RETURN"])
        commands = json.loads((evidence / "commands.json").read_bytes())
        selected = [row for row in commands if "--batch-apply" in row["argv"]]
        self.assertEqual(len(selected), 1)
        self.assertEqual(selected[0]["returncode"], 78)
        raw = (evidence / selected[0]["stdout"]["path"]).read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(), selected[0]["stdout"]["sha256"])
        report = json.loads(raw)
        self.assertEqual((report["status"], report["completed_rows"], report["attempted_rows"]),
                         ("UNKNOWN", 1, 2))
        self.assertEqual(report["rows"][1]["disposition"], "UNKNOWN")
        self.assertIsNone(report["rows"][1]["dispatch_started"])
        self.assertIsNone(report["rows"][1]["decoded_result"])
        self.assertEqual(report["rows"][2]["disposition"], "NEVER_STARTED")
        self.assertIs(report["rows"][2]["dispatch_started"], False)
        self.assertFalse(report["aggregate_durable_receipt"])
        case = evidence / "DISPATCH_EXCEPTION_AFTER_RETURN"
        self.assertEqual(json.loads((case / "PREFIX-BEFORE-SECOND.json").read_bytes()),
                         json.loads((case / "PREFIX-AFTER-SECOND.json").read_bytes()))
        self.assertEqual((case / "repository/row-a").read_bytes(), b"row-a REPLACED\n")
        self.assertEqual((case / "repository/row-b").read_bytes(), b"row-b REPLACED\n")
        self.assertEqual((case / "repository/row-c").read_bytes(), b"row-c ORIGINAL\n")
        self.receive(raw, case / "repository")

    def test_later_result_fsync_failure_does_not_erase_effect_or_release_delivery(self):
        evidence = self.base / "persistence"
        self.producer([sys.executable, "-B", str(REPO / "tests/distributed_generation_fence.py"),
            "--case", "ordinary-final-result-dir-sync", "--evidence-dir", str(evidence)])
        cases = list(evidence.glob("d48-fence-*/ordinary-final-result-dir-sync"))
        self.assertEqual(len(cases), 1)
        case = cases[0]
        raw = (case / "sink.out").read_bytes()
        live = json.loads(raw)
        self.assertEqual((live["status"], live["reason_code"]),
                         ("ROLLBACK_FAILED_WITH_RESIDUE", "RESULT_PERSISTENCE_FAILURE"))
        self.assertEqual((case / "repo/target").read_bytes(), b"CURRENT\n")
        saved = list((case / "repo/.IMPLEMENTAUDIT/runs").glob("*/mutation-transactions/*/result.json"))
        self.assertEqual(len(saved), 1)
        retained = json.loads(saved[0].read_bytes())
        self.assertEqual(retained["status"], "COMMITTED")
        self.assertEqual(live["actual_effect_set"][:len(retained["actual_effect_set"])],
                         retained["actual_effect_set"])
        self.assertTrue(live["residue"])
        self.receive(raw, case / "repo")


if __name__ == "__main__":
    unittest.main()
