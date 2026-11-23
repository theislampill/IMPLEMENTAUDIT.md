"""Distinguish successful transport from verdict in the portable JOIN owner."""
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[3]
FIXTURE = ROOT / "tests/work-graph-pending-settlement-cases.py"
spec = importlib.util.spec_from_file_location("exact_pending_fixture", FIXTURE)
fixture = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fixture)
OBSERVATIONS = []


class TransportVerdictCase(fixture.PendingSettlementCases):
    def compare_verdict(self, status, terminal, join_status):
        self.fixture.state["context"]["host_capacity"] = 2
        self.fixture.write_source()
        raw = (json.dumps({"status": status, "terminal": terminal}, sort_keys=True) + "\n").encode()
        (self.run / "inputs/a").write_bytes(raw)
        frontier = self.consumer.frontier()
        self.assertEqual(frontier["selected"], ["A", "B"])
        a, b = self.start("A"), self.start("B")
        a_body, b_body = a.finish(), b.finish()
        a.close()
        b.close()
        self.assertEqual(a_body, raw)
        self.assertEqual([a.process.returncode, b.process.returncode], [0, 0])
        observed = json.loads(a_body)
        a_result = self.fixture.result(frontier, "A", output=a_body)
        a_result.update(observed, exit_code=a.process.returncode)
        b_result = self.fixture.result(frontier, "B", output=b_body)
        self.consumer.accept(frontier, [a_result, b_result], "JOIN", expected_old=self.consumer.history_digest)

        before = (self.root / "journal/history.json").read_bytes()
        joined = self.consumer.join("JOIN", expected_old=self.consumer.history_digest)
        self.assertEqual(joined["status"], join_status)
        self.assertEqual(joined["missing"], [])
        self.assertIs(joined["all_required_settled"], terminal)
        self.assertEqual(joined["authority"], "NONE")
        self.assertFalse(joined["native_dispatch_authorized"])
        preserved = (self.root / "journal/history.json").read_bytes() == before
        successor = self.consumer.frontier()
        passed = status == "PASS"
        self.assertIs(preserved, not passed)
        self.assertIs("NEXT" in successor["selected"], passed)
        if not passed:
            self.assertEqual(successor["states"]["NEXT"], "BLOCKED")
            self.assertNotEqual(successor["states"]["A"], "DONE")
        OBSERVATIONS.append({
            "actual_exits": {"A": a.process.returncode, "B": b.process.returncode},
            "a_stdout": raw.decode(), "b_stdout": b_body.decode(),
            "a_submitted_result": a_result, "b_submitted_result": b_result,
            "join": joined, "journal_unchanged_on_join": preserved,
            "successor_state": successor["states"]["NEXT"], "selected_after_join": successor["selected"],
        })

    def test_partial(self):
        self.compare_verdict("PARTIAL", False, "PENDING")

    def test_nonverdict(self):
        self.compare_verdict("NONVERDICT", True, "NONVERDICT")

    def test_pass(self):
        self.compare_verdict("PASS", True, "SATISFIED_AT_DECLARED_RESULT_CONTRACT")


if __name__ == "__main__":
    os.environ.pop("R0035_PENDING_EVIDENCE_ROOT", None)
    log = io.StringIO()
    suite = unittest.TestSuite(TransportVerdictCase(name) for name in ("test_partial", "test_nonverdict", "test_pass"))
    outcome = unittest.TextTestRunner(stream=log).run(suite)
    if not outcome.wasSuccessful():
        print(log.getvalue(), file=sys.stderr)
        raise SystemExit(1)
    paths = [FIXTURE, ROOT / "tests/work-graph-completion-cases.py", ROOT / "scripts/work-graph-completion.py",
             ROOT / "skills/implementaudit/scripts/compile-work-graph.py"]
    print(json.dumps({
        "schema": "dg16.q01.portable-transport-verdict.v1",
        "case": "R53-DAG-N05-SUCCESS-ENVELOPE-NONVERDICT", "authority": "NONE",
        "sources": {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest() for path in paths},
        "observations": OBSERVATIONS,
    }, sort_keys=True, indent=2))
