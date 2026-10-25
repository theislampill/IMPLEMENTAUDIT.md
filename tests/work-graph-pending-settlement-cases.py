"""Live portable pending settlement; never native acceptance or a task runner."""
from concurrent.futures import ThreadPoolExecutor
import copy
import errno
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import selectors
import shutil
import signal
import subprocess
import sys
import threading
import unittest

REPO = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "completion_support", REPO / "tests/work-graph-completion-cases.py")
support = importlib.util.module_from_spec(spec)
spec.loader.exec_module(support)

PRODUCER = """
import pathlib, sys
payload = pathlib.Path(sys.argv[1]).read_bytes()
sys.stderr.buffer.write(b'READY\\n')
sys.stderr.buffer.flush()
gate = sys.stdin.buffer.read(1)
if gate not in (b'G', b'F'):
    raise SystemExit(9)
sys.stdout.buffer.write(payload)
if gate == b'F':
    raise SystemExit(7)
"""


class GatedProducer:
    """Own a real read-only child until its bounded gate release or cleanup."""
    def __init__(self, source, observations):
        self.observations = observations
        self.process = subprocess.Popen(
            [sys.executable, "-I", "-S", "-B", "-c", PRODUCER, str(source)],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.output = None
        self.observation = dict(pid=self.process.pid, source=str(source),
                                input_sha256=hashlib.sha256(source.read_bytes()).hexdigest())
        observations.append(self.observation)
        try:
            with selectors.DefaultSelector() as selector:
                selector.register(self.process.stderr, selectors.EVENT_READ)
                if not selector.select(timeout=5):
                    raise AssertionError("producer did not reach its bounded gate")
                ready = os.read(self.process.stderr.fileno(), 64)
            self.observation.update(readiness=ready.decode("ascii"),
                                    poll_at_gate=self.process.poll())
            if ready != b"READY\n" or self.process.poll() is not None:
                raise AssertionError("producer was not live at its gate")
        except BaseException:
            self.close()
            raise

    def finish(self, exit_code=0):
        if self.output is not None:
            raise AssertionError("producer already released")
        if exit_code not in (0, 7):
            raise AssertionError("unsupported controlled producer exit")
        stdout, stderr = self.process.communicate(
            input=b"G" if exit_code == 0 else b"F", timeout=5)
        self.output = stdout
        self.observation.update(stdout=stdout.decode("utf-8"), stderr=stderr.decode("utf-8"),
                                output_sha256=hashlib.sha256(stdout).hexdigest(),
                                returncode=self.process.returncode)
        if self.process.returncode != exit_code:
            raise AssertionError("controlled producer did not reach its expected exit")
        return stdout

    def close(self):
        if self.process.poll() is None:
            self.process.kill()
            self.observation["cleanup_killed"] = True
        self.process.wait(timeout=5)
        for pipe in (self.process.stdin, self.process.stdout, self.process.stderr):
            if pipe is not None:
                pipe.close()
        try:
            os.waitpid(self.process.pid, os.WNOHANG)
        except ChildProcessError:
            self.observation["reaped"] = True
        else:
            raise AssertionError("producer custody was not reaped by its owner")
        self.observation["final_returncode"] = self.process.returncode


class PendingSettlementCases(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        support.CompletionCases.setUpClass()

    def setUp(self):
        # Compose the existing public fixture without inheriting its test bank.
        self.fixture = support.CompletionCases()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.owner = self.fixture.owner
        self.consumer = self.fixture.consumer
        self.root, self.run = self.fixture.root, self.fixture.run
        self.processes, self.observations, self.snapshots = [], [], {}

    def tearDown(self):
        for process in self.processes:
            process.close()
        location = os.environ.get("R0035_PENDING_EVIDENCE_ROOT")
        if location:
            destination = Path(location) / self._testMethodName
            destination.mkdir(parents=True, exist_ok=False)
            (destination / "observations.json").write_text(json.dumps(
                dict(authority="NONE", processes=self.observations, snapshots=self.snapshots),
                sort_keys=True, indent=2) + "\n")
            shutil.copytree(self.run, destination / "run")
            shutil.copytree(self.root / "journal", destination / "journal")

    def start(self, name="A"):
        process = GatedProducer(self.run / "inputs" / name.lower(), self.observations)
        self.processes.append(process)
        return process

    def result(self, frontier, status, output=b""):
        result = self.fixture.result(frontier, "A", status, output=output)
        if status == "PENDING":
            result.update(exit_code=None, evidence_digest=None)
        return result

    def history(self):
        return json.loads((self.root / "journal/history.json").read_bytes())

    def begin_pending(self, frontier=None):
        if frontier is None:
            frontier = self.consumer.frontier()
        self.assertIn("A", frontier["selected"])
        process = self.start()
        event = self.consumer.accept(frontier, [self.result(frontier, "PENDING")], "JOIN",
                                     expected_old=self.consumer.history_digest)
        self.assertIsNone(process.process.poll())
        self.snapshots.update(original_frontier=frontier, pending_event=event,
                              pending_history=self.history(), poll_after_pending=None)
        return frontier, process

    def assert_refused_without_append(self, frontier, results, consumer="JOIN", expected_old=None):
        before = (self.root / "journal/history.json").read_bytes()
        digest = self.consumer.history_digest
        with self.assertRaises(self.owner.CompletionError) as failure:
            self.consumer.accept(frontier, results, consumer,
                                 expected_old=digest if expected_old is None else expected_old)
        self.assertEqual((self.root / "journal/history.json").read_bytes(), before)
        self.assertEqual(self.consumer.history_digest, digest)
        self.snapshots.setdefault("refusals", []).append(str(failure.exception))

    def complete_b(self):
        frontier = self.consumer.frontier()
        self.assertIn("B", frontier["selected"])
        result = self.fixture.result(frontier, "B")
        return self.consumer.accept(frontier, [result], "JOIN",
                                    expected_old=self.consumer.history_digest)

    def assert_joined(self):
        joined = self.consumer.join("JOIN", expected_old=self.consumer.history_digest)
        self.snapshots["join"] = joined
        self.assertEqual(joined["status"], "SATISFIED_AT_DECLARED_RESULT_CONTRACT")
        self.assertTrue(joined["all_required_settled"])
        self.assertEqual(joined["authority"], "NONE")
        self.assertEqual(joined["lifecycle_credit"], "NONE")
        self.assertFalse(joined["native_dispatch_authorized"])
        next_frontier = self.consumer.frontier()
        self.assertEqual(next_frontier["selected"], ["NEXT"])
        self.assertNotEqual(next_frontier["states"]["ROOT"], "DONE")
        self.assertEqual(next_frontier["authority"], "NONE")
        self.assertFalse(next_frontier["native_dispatch_authorized"])

    def test_terminal_only_live_process_control(self):
        frontier = self.consumer.frontier()
        self.assertEqual(frontier["selected"], ["A"])
        process = self.start()
        output = process.finish()
        terminal = self.result(frontier, "PASS", output)
        self.snapshots["terminal_event"] = self.consumer.accept(
            frontier, [terminal], "JOIN", expected_old=self.consumer.history_digest)
        self.complete_b()
        self.assert_joined()

    def test_live_pending_then_terminal_same_frontier(self):
        frontier = self.consumer.frontier()
        self.assertEqual(frontier["selected"], ["A"])
        process = self.start()
        pending = self.result(frontier, "PENDING")
        pending_event = self.consumer.accept(
            frontier, [pending], "JOIN", expected_old=self.consumer.history_digest)
        pending_history = self.history()
        self.snapshots.update(original_frontier=frontier, pending_event=pending_event,
                              pending_history=pending_history,
                              poll_after_pending=process.process.poll())
        self.assertIsNone(process.process.poll())
        view = self.consumer.frontier()
        self.assertEqual(view["states"]["A"], "BLOCKED")
        self.assertIn("COMPLETION_PENDING", view["blocked"]["A"])
        self.assertEqual(view["selected"], ["B"])
        output = process.finish()
        terminal = self.result(frontier, "PASS", output)
        self.snapshots["actual_terminal_result"] = terminal
        error = None
        try:
            self.snapshots["terminal_event"] = self.consumer.accept(
                frontier, [terminal], "JOIN", expected_old=self.consumer.history_digest)
        except self.owner.CompletionError as exc:
            error = str(exc)
            self.snapshots["settlement_error"] = error
        self.complete_b()
        if error is not None:
            joined = self.consumer.join("JOIN", expected_old=self.consumer.history_digest)
            self.snapshots["join_after_refused_settlement"] = joined
            self.assertEqual(joined["status"], "PENDING")
            self.assertFalse(joined["all_required_settled"])
            self.assertEqual(joined["missing"], [])
            self.fail("actual live PENDING producer finished but settlement refused: " + error)
        self.assertEqual(self.history()["events"][:1], pending_history["events"])
        self.assertEqual(self.history()["events"][1]["previous"], pending_event["digest"])
        self.assertEqual(self.history()["events"][1]["body"]["records"][0]["status"], "PASS")
        self.assert_joined()

    def test_partial_frontier_remains_usable_and_terminal_replay_refuses(self):
        self.fixture.state["context"]["host_capacity"] = 2
        self.fixture.write_source()
        frontier, process = self.begin_pending()
        self.assertEqual(frontier["selected"], ["A", "B"])
        terminal = self.result(frontier, "PASS", process.finish())
        self.consumer.accept(frontier, [terminal], "JOIN", expected_old=self.consumer.history_digest)
        self.assert_refused_without_append(frontier, [terminal])
        b = self.fixture.result(frontier, "B")
        self.consumer.accept(frontier, [b], "JOIN", expected_old=self.consumer.history_digest)
        self.assertEqual(self.history()["events"][0], self.snapshots["pending_event"])
        self.assert_joined()

    def test_equal_or_copied_frontier_cannot_take_pending_custody(self):
        frontier = self.consumer.frontier()
        equal_frontier = self.consumer.frontier()
        self.assertEqual(frontier, equal_frontier)
        frontier, process = self.begin_pending(frontier)
        terminal = self.result(frontier, "PASS", process.finish())
        self.assert_refused_without_append(equal_frontier, [terminal])
        self.assert_refused_without_append(copy.deepcopy(frontier), [terminal])
        self.consumer.accept(frontier, [terminal], "JOIN", expected_old=self.consumer.history_digest)
        self.assertEqual(self.consumer.frontier()["states"]["A"], "DONE")

    def test_repeated_pending_and_nonterminal_replacement_refuse(self):
        frontier, process = self.begin_pending()
        for result in (self.result(frontier, "PENDING"),
                       dict(self.result(frontier, "FAIL"), terminal=False),
                       dict(self.result(frontier, "PASS"), terminal=False)):
            with self.subTest(status=result["status"]):
                self.assert_refused_without_append(frontier, [result])
        terminal = self.result(frontier, "PASS", process.finish())
        self.consumer.accept(frontier, [terminal], "JOIN", expected_old=self.consumer.history_digest)
        self.assertEqual(len(self.history()["events"]), 2)

    def test_actual_terminal_failure_settles_once_without_join_success(self):
        frontier, process = self.begin_pending()
        output = process.finish(exit_code=7)
        failure = dict(self.result(frontier, "FAIL", output), exit_code=7)
        self.consumer.accept(frontier, [failure], "JOIN", expected_old=self.consumer.history_digest)
        self.assert_refused_without_append(frontier, [self.result(frontier, "PASS", output)])
        self.complete_b()
        joined = self.consumer.join("JOIN", expected_old=self.consumer.history_digest)
        self.snapshots["join"] = joined
        self.assertEqual(joined["status"], "FAIL")
        self.assertTrue(joined["all_required_settled"])
        self.assertEqual(self.consumer.frontier()["states"]["A"], "BLOCKED")
        self.assertEqual(self.history()["events"][0], self.snapshots["pending_event"])

    def test_changed_input_refuses_settlement_and_retains_pending_history(self):
        frontier, process = self.begin_pending()
        terminal = self.result(frontier, "PASS", process.finish())
        (self.run / "inputs/a").write_text("new input\n")
        self.assert_refused_without_append(frontier, [terminal])
        view = self.consumer.frontier()
        self.assertIn("A", view["invalidated"])
        self.assertEqual(view["states"]["B"], "READY")
        self.assertEqual(len(self.history()["events"]), 1)

    def test_changed_authorization_cannot_be_removed_by_settlement(self):
        frontier, process = self.begin_pending()
        terminal = self.result(frontier, "PASS", process.finish())
        self.fixture.nodes[1]["authorization"] = "MISSING"
        self.fixture.write_source()
        self.assert_refused_without_append(frontier, [terminal])
        self.assertIn("AUTHORIZATION", self.consumer.frontier()["blocked"]["A"])

    def test_changed_context_premise_refuses_pending_settlement(self):
        frontier, process = self.begin_pending()
        terminal = self.result(frontier, "PASS", process.finish())
        self.fixture.nodes[1]["context"]["useful_value"] = 0
        self.fixture.write_source()
        self.assert_refused_without_append(frontier, [terminal])
        self.assertNotEqual(self.consumer.frontier()["states"]["A"], "DONE")

    def test_unrelated_active_occupancy_does_not_redispatch_finished_work(self):
        frontier, process = self.begin_pending()
        terminal = self.result(frontier, "PASS", process.finish())
        self.fixture.nodes[2]["state"] = "ACTIVE"
        self.fixture.write_source()
        self.consumer.accept(frontier, [terminal], "JOIN", expected_old=self.consumer.history_digest)
        current = self.consumer.frontier()
        self.assertEqual(current["states"]["A"], "DONE")
        self.assertEqual(current["states"]["B"], "ACTIVE")
        self.assertEqual(current["active_occupancy"], 1)
        self.assertEqual(current["selected"], [])

    def test_replaced_optional_predecessor_refuses_but_keeps_independent_result(self):
        self.fixture.nodes[1]["optional"] = ["B"]
        self.fixture.state["context"]["host_capacity"] = 2
        self.fixture.write_source()
        frontier, process = self.begin_pending()
        self.assertEqual(frontier["selected"], ["A", "B"])
        terminal = self.result(frontier, "PASS", process.finish())
        b = self.fixture.result(frontier, "B")
        self.consumer.accept(frontier, [b], "JOIN", expected_old=self.consumer.history_digest)
        self.assert_refused_without_append(frontier, [terminal])
        current = self.consumer.frontier()
        self.assertIn("A", current["invalidated"])
        self.assertEqual(current["states"]["B"], "DONE")

    def test_pending_consumer_and_independence_identity_cannot_change(self):
        self.fixture.nodes[1]["future_consumer"] = None
        self.fixture.nodes[5]["optional"] = ["A"]
        self.fixture.write_source()
        frontier, process = self.begin_pending()
        terminal = self.result(frontier, "PASS", process.finish())
        self.assert_refused_without_append(frontier, [terminal], consumer="FINAL")
        self.assert_refused_without_append(
            frontier, [dict(terminal, independence_key="a-different-producer")])
        self.consumer.accept(frontier, [terminal], "JOIN", expected_old=self.consumer.history_digest)
        self.assertEqual(self.consumer.frontier()["states"]["A"], "DONE")

    def test_stale_expected_old_refuses_without_losing_live_pending_custody(self):
        frontier, process = self.begin_pending()
        old = self.consumer.history_digest
        terminal = self.result(frontier, "PASS", process.finish())
        self.complete_b()
        self.assert_refused_without_append(frontier, [terminal], expected_old=old)
        self.consumer.accept(frontier, [terminal], "JOIN", expected_old=self.consumer.history_digest)
        self.assert_joined()

    def test_concurrent_terminal_arrivals_append_once(self):
        frontier, process = self.begin_pending()
        terminal = self.result(frontier, "PASS", process.finish())
        old = self.consumer.history_digest
        def arrive():
            try:
                return self.consumer.accept(frontier, [terminal], "JOIN", expected_old=old)
            except self.owner.CompletionError as exc:
                return str(exc)
        with ThreadPoolExecutor(max_workers=2) as pool:
            arrivals = list(pool.map(lambda unused: arrive(), range(2)))
        self.assertEqual(sum(isinstance(arrival, dict) for arrival in arrivals), 1)
        self.assertEqual(sum(isinstance(arrival, str) for arrival in arrivals), 1)
        self.assertEqual(len(self.history()["events"]), 2)
        self.snapshots["concurrent_arrivals"] = arrivals

    def test_reopened_journal_does_not_restore_pending_settlement_custody(self):
        frontier, process = self.begin_pending()
        terminal = self.result(frontier, "PASS", process.finish())
        before = (self.root / "journal/history.json").read_bytes()
        self.consumer.close()
        self.consumer = self.owner.CompletionContract(self.run, self.root / "journal")
        self.addCleanup(self.consumer.close)
        self.assert_refused_without_append(frontier, [terminal])
        reopened = self.consumer.transition()
        self.assertIn("COMPLETION_RECOVERY_CUSTODY_UNVERIFIED", reopened["blocked"]["A"])
        self.assertEqual(reopened["completion_events"], [])
        self.assert_refused_without_append(reopened, [terminal])
        self.assertEqual((self.root / "journal/history.json").read_bytes(), before)

    @unittest.skipUnless(hasattr(os, "fork"), "fork custody requires POSIX")
    def test_fork_refuses_inherited_custody_before_lock_and_parent_still_settles(self):
        frontier, producer = self.begin_pending()
        terminal = self.result(frontier, "PASS", producer.finish())
        producer.close()
        old = self.consumer.history_digest
        before = (self.root / "journal/history.json").read_bytes()
        parent_pid = os.getpid()
        locked, release = threading.Event(), threading.Event()
        hold_errors = []

        def hold_receiver_lock():
            # Reproduce a lock owned by a different thread at the fork boundary.
            # No result, graph or custody identity is modified by this control.
            with self.consumer._operation_lock:
                locked.set()
                if not release.wait(10):
                    hold_errors.append("parent lock coordination timed out")

        holder = threading.Thread(target=hold_receiver_lock, daemon=True)
        holder.start()
        if not locked.wait(5):
            release.set()
            holder.join(timeout=2)
            self.fail("parent thread did not hold receiver lock")
        read_fd, write_fd = os.pipe()
        child_pid = None
        payload, status, timed_out = b"", None, False
        try:
            child_pid = os.fork()
            if child_pid == 0:
                os.close(read_fd)
                signal.signal(signal.SIGALRM, signal.SIG_DFL)
                signal.alarm(5)
                report = dict(child_pid=os.getpid(), operations=[])
                try:
                    operations = [
                        ("accept", lambda: self.consumer.accept(
                            frontier, [terminal], "JOIN", expected_old=old)),
                        ("frontier", self.consumer.frontier),
                        ("transition", self.consumer.transition),
                        ("join", lambda: self.consumer.join("JOIN", expected_old=old)),
                        ("history_digest", lambda: self.consumer.history_digest),
                        ("enter", self.consumer.__enter__),
                        ("journal.check", self.consumer.journal.check),
                        ("journal.append", lambda: self.consumer.journal.append(
                            "BATCH", dict(records=[]), old)),
                    ]
                    for name, operation in operations:
                        try:
                            operation()
                            outcome = dict(operation=name, refused=False)
                        except BaseException as exc:
                            outcome = dict(operation=name, refused=True,
                                           error_type=type(exc).__name__, error=str(exc))
                        report["operations"].append(outcome)
                    self.consumer.close()
                    self.consumer.close()
                    try:
                        os.fstat(self.consumer.journal.fd)
                        report["inherited_descriptor_closed"] = False
                    except OSError as exc:
                        report["inherited_descriptor_closed"] = exc.errno == errno.EBADF
                    try:
                        reopened = self.owner.CompletionContract(self.run, self.root / "journal")
                    except self.owner.CompletionError as exc:
                        report["parent_writer_still_held"] = "already has a writer" in str(exc)
                    else:
                        reopened.close()
                        report["parent_writer_still_held"] = False
                except BaseException as exc:
                    report["unexpected_error"] = dict(type=type(exc).__name__, error=str(exc))
                encoded = json.dumps(report).encode()
                if len(encoded) <= 4096:
                    os.write(write_fd, encoded)
                os.close(write_fd)
                os._exit(0)
            os.close(write_fd)
            write_fd = None
            with selectors.DefaultSelector() as selector:
                selector.register(read_fd, selectors.EVENT_READ)
                if selector.select(timeout=8):
                    payload = os.read(read_fd, 4096)
                else:
                    timed_out = True
        finally:
            os.close(read_fd)
            if write_fd is not None:
                os.close(write_fd)
            if child_pid:
                if timed_out:
                    try:
                        os.kill(child_pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass
                waited, status = os.waitpid(child_pid, 0)
            release.set()
            holder.join(timeout=2)
        after = (self.root / "journal/history.json").read_bytes()
        report = json.loads(payload) if payload else {}
        self.snapshots["fork_process_owner"] = dict(
            parent_pid=parent_pid, child_pid=child_pid, child_wait_status=status,
            child_reaped=waited == child_pid, timed_out=timed_out, report=report,
            before_sha256=hashlib.sha256(before).hexdigest(),
            after_sha256=hashlib.sha256(after).hexdigest())
        self.assertFalse(holder.is_alive())
        self.assertEqual(hold_errors, [])
        self.assertEqual(status, 0, "inherited receiver did not refuse before the inherited-lock deadline")
        self.assertFalse(timed_out)
        self.assertNotEqual(parent_pid, report["child_pid"])
        self.assertNotIn("unexpected_error", report)
        self.assertEqual(len(report["operations"]), 8)
        for operation in report["operations"]:
            self.assertTrue(operation["refused"], operation)
            self.assertEqual(operation["error_type"], "CompletionError", operation)
            self.assertIn("another process", operation["error"], operation)
        self.assertTrue(report["inherited_descriptor_closed"])
        self.assertTrue(report["parent_writer_still_held"])
        self.assertEqual(before, after)
        self.assertEqual(self.consumer.history_digest, old)
        self.consumer.accept(frontier, [terminal], "JOIN", expected_old=old)
        self.assertEqual(self.history()["events"][0], self.snapshots["pending_event"])
        self.assertEqual(self.consumer.frontier()["states"]["A"], "DONE")
        self.complete_b()
        self.assert_joined()

    def test_pending_batch_settlement_is_atomic_and_transition_keeps_only_current_records(self):
        self.fixture.state["context"]["host_capacity"] = 2
        self.fixture.write_source()
        frontier = self.consumer.transition()
        self.assertEqual(frontier["selected"], ["A", "B"])
        a, b = self.start("A"), self.start("B")
        pending_a = self.result(frontier, "PENDING")
        pending_b = dict(self.fixture.result(frontier, "B", "PENDING", output=b""),
                         evidence_digest=None)
        event = self.consumer.accept(frontier, [pending_a, pending_b], "JOIN",
                                     expected_old=self.consumer.history_digest)
        self.assertIsNone(a.process.poll())
        self.assertIsNone(b.process.poll())
        self.snapshots["pending_event"] = event
        terminal_a = self.result(frontier, "PASS", a.finish())
        terminal_b = self.fixture.result(frontier, "B", output=b.finish())
        self.assert_refused_without_append(frontier, [terminal_a, dict(terminal_b, scope=["A"])])
        self.consumer.accept(frontier, [terminal_a, terminal_b], "JOIN",
                             expected_old=self.consumer.history_digest)
        history = self.history()
        self.assertEqual(len(history["events"]), 2)
        self.assertEqual(history["events"][0], event)
        projected = self.consumer.transition()
        self.assertEqual(len(projected["completion_events"]), 1)
        self.assertEqual(projected["completion_events"][0]["original_scope"], ["A", "B"])
        self.assertEqual(projected["completion_events"][0]["retained_scope"], ["A", "B"])
        self.assertEqual([record["status"] for record in
                          projected["completion_events"][0]["records"]], ["PASS", "PASS"])
        self.assert_joined()


if __name__ == "__main__":
    unittest.main()
