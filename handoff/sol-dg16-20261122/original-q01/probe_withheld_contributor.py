"""Observe a completed required producer whose result has yet to arrive."""
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
OBSERVATION = {}


class WithheldContributorCase(fixture.PendingSettlementCases):
    def test_finished_required_result_cannot_be_inferred(self):
        self.fixture.state["context"]["host_capacity"] = 2
        self.fixture.write_source()
        frontier = self.consumer.frontier()
        self.assertEqual(frontier["selected"], ["A", "B"])
        a, b = self.start("A"), self.start("B")
        self.assertIsNone(a.process.poll())
        self.assertIsNone(b.process.poll())
        a_body, b_body = a.finish(), b.finish()
        a.close()
        b.close()
        self.assertEqual([a.process.returncode, b.process.returncode], [0, 0])
        self.assertTrue(all(o["reaped"] for o in self.observations))
        a_result = self.fixture.result(frontier, "A", output=a_body)
        b_result = self.fixture.result(frontier, "B", output=b_body)
        self.consumer.accept(frontier, [a_result], "JOIN", expected_old=self.consumer.history_digest)

        journal_path = self.root / "journal/history.json"
        before = journal_path.read_bytes()
        pending = self.consumer.join("JOIN", expected_old=self.consumer.history_digest)
        self.assertEqual(pending["status"], "PENDING")
        self.assertEqual(pending["missing"], ["B"])
        self.assertFalse(pending["all_required_settled"])
        self.assertEqual(journal_path.read_bytes(), before)
        blocked = self.consumer.frontier()
        self.assertEqual(blocked["states"]["NEXT"], "BLOCKED")
        self.assertNotIn("NEXT", blocked["selected"])

        self.consumer.accept(frontier, [b_result], "JOIN", expected_old=self.consumer.history_digest)
        self.assert_joined()
        OBSERVATION.update({
            "dispatch_id": frontier["dispatch_id"], "selected": frontier["selected"],
            "producer_exits_before_first_join": {"A": a.process.returncode, "B": b.process.returncode},
            "producer_outputs": {"A": a_result["evidence_digest"], "B": b_result["evidence_digest"]},
            "both_reaped_before_first_join": True,
            "first_join_status": pending["status"], "missing": pending["missing"],
            "successor_before_receiving_b": blocked["states"]["NEXT"],
            "journal_unchanged_on_pending": True,
            "after_receiving_b": self.snapshots["join"]["status"], "newly_selected": ["NEXT"],
        })


if __name__ == "__main__":
    os.environ.pop("R0035_PENDING_EVIDENCE_ROOT", None)
    log = io.StringIO()
    suite = unittest.TestSuite([WithheldContributorCase("test_finished_required_result_cannot_be_inferred")])
    result = unittest.TextTestRunner(stream=log).run(suite)
    if not result.wasSuccessful():
        print(log.getvalue(), file=sys.stderr)
        raise SystemExit(1)
    paths = [FIXTURE, ROOT / "tests/work-graph-completion-cases.py", ROOT / "scripts/work-graph-completion.py",
             ROOT / "skills/implementaudit/scripts/compile-work-graph.py"]
    print(json.dumps({
        "schema": "dg16.q01.portable-withheld-contributor.v1",
        "case": "R53-DAG-N01-OMITTED-REQUIRED-JOIN",
        "authority": "NONE", "native_dispatch_authorized": False,
        "sources": {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest() for path in paths},
        "observation": OBSERVATION,
    }, sort_keys=True, indent=2))
