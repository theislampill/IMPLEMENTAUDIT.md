"""Exercise the existing portable completion owner across a valid JOIN."""
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[3]
FIXTURE = ROOT / "tests/work-graph-completion-cases.py"
spec = importlib.util.spec_from_file_location("exact_completion_fixture", FIXTURE)
fixture = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fixture)
OBSERVATION = {}


class OldFrontierCase(fixture.CompletionCases):
    def test_completed_join_requires_fresh_successor_dispatch(self):
        self.accept("A")
        self.accept("B")
        old = self.consumer.frontier()
        self.assertEqual(old["selected"], ["JOIN"])
        self.assertEqual(old["states"]["NEXT"], "BLOCKED")
        prior = self.consumer.history_digest

        joined = self.consumer.join("JOIN", expected_old=prior)
        self.assertEqual(joined["status"], "SATISFIED_AT_DECLARED_RESULT_CONTRACT")
        current = self.consumer.history_digest
        self.assertNotEqual(current, prior)

        # Bind expected-old to the current journal so the old-frontier check,
        # rather than an older journal token, has to refuse the submission.
        self.assertNotIn("NEXT", old["inputs"])
        old_result = self.result(old, "JOIN", output=b"unexecuted old-frontier submission")
        old_result.update(node="NEXT", scope=["NEXT"])
        with self.assertRaisesRegex(self.owner.CompletionError,
                                    "^foreign, duplicate or undispatched contributor$") as refusal:
            self.consumer.accept(old, [old_result], "FINAL", expected_old=current)
        self.assertEqual(self.consumer.history_digest, current)

        fresh, result, _ = self.accept("NEXT", "FINAL")
        self.assertEqual(fresh["selected"], ["NEXT"])
        self.assertNotEqual(fresh["dispatch_id"], old["dispatch_id"])
        self.assertEqual(result["dispatch_id"], fresh["dispatch_id"])
        self.assertNotEqual(self.consumer.history_digest, current)
        final = self.consumer.join("FINAL", expected_old=self.consumer.history_digest)
        self.assertEqual(final["status"], "SATISFIED_AT_DECLARED_RESULT_CONTRACT")
        self.assertFalse(final["native_dispatch_authorized"])
        OBSERVATION.update({
            "old": {"selected": old["selected"], "dispatch_id": old["dispatch_id"],
                    "graph_digest": old["graph_digest"], "successor_state": old["states"]["NEXT"]},
            "join_status": joined["status"],
            "join_updated_journal": True,
            "old_result_dispatched": False,
            "refusal": str(refusal.exception),
            "journal_preserved_on_refusal": True,
            "new": {"selected": fresh["selected"], "dispatch_id": fresh["dispatch_id"],
                    "graph_digest": fresh["graph_digest"],
                    "observed_successor_output_sha256": result["evidence_digest"]},
            "final_join_status": final["status"],
        })


if __name__ == "__main__":
    suite = unittest.TestSuite([OldFrontierCase("test_completed_join_requires_fresh_successor_dispatch")])
    log = io.StringIO()
    run = unittest.TextTestRunner(stream=log).run(suite)
    if not run.wasSuccessful():
        print(log.getvalue(), file=sys.stderr)
        raise SystemExit(1)
    record = {
        "schema": "dg16.q01.portable-post-join-frontier.v1",
        "case": "R53-DAG-N04-NO-POST-JOIN-RECOMPUTE",
        "scope": "PORTABLE_DECLARED_RESULT_CONTRACT",
        "fixture_sha256": hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),
        "owner_sha256": hashlib.sha256((ROOT / "scripts/work-graph-completion.py").read_bytes()).hexdigest(),
        "native_dispatch_authorized": False,
        "authority": "NONE",
        "observation": OBSERVATION,
    }
    print(json.dumps(record, sort_keys=True, indent=2))
