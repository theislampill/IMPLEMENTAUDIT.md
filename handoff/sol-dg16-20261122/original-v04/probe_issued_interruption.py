"""Bind a fresh benign verifier interruption to the existing completion owner."""
import base64
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import sys
import unittest


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


probe = load("exact_interrupt_probe", HERE / "probe_interrupted_verifier.py")
fixture = load("exact_completion_fixture", ROOT / "tests/work-graph-completion-cases.py")
OWNER_PINS = {
    "scripts/work-graph-completion.py": "70137df6459caa3eecbf847580a34968d13aa1991eae6208e37ea84e60f556eb",
    "tests/work-graph-completion-cases.py": "729eb577d2231754015d42a12a4c76c587077696a7b4a0691c2df473fe00e984",
    **probe.SOURCES,
}
OBSERVATION = {}


class InterruptedDispatchCase(fixture.CompletionCases):
    def test_observe_after_issue_and_settle_without_join_acceptance(self):
        inputs = {path: (ROOT / path).read_bytes() for path in OWNER_PINS}
        self.assertEqual({p: probe.pin(b)["sha256"] for p, b in inputs.items()}, OWNER_PINS)
        packet = {path: base64.b64encode(inputs[path]).decode() for path in probe.SOURCES}
        manifest = probe.dump({"scope": "FRESH_PORTABLE_INTERRUPT_PAIR",
                               "owner_sources": probe.SOURCES, "registry": probe.pin(probe.REGISTRY)})
        path = self.run / "inputs/a"
        path.write_bytes(manifest)
        frontier = self.consumer.frontier()
        self.assertEqual(frontier["selected"], ["A"])
        self.assertEqual(frontier["states"]["JOIN"], "BLOCKED")
        first_journal = self.consumer.history_digest

        # A owns both observations, and its exact issued frontier stays live in
        # this process before the benign paired operation starts.
        observed = probe.run_posix(packet)
        self.assertEqual(self.consumer.history_digest, first_journal)
        self.assertEqual(path.read_bytes(), manifest)
        self.assertTrue(observed["owned_fixture_removed"])
        actual_exits = {mode: x["retained_exit"] for mode, x in observed["captures"].items()}
        self.assertEqual(actual_exits, {"legacy": -15, "dag": -15})
        retained = probe.dump(observed)
        outcome = self.result(frontier, "A", status="INTERRUPTED", output=retained)
        outcome["exit_code"] = actual_exits["dag"]
        self.assertTrue(outcome["terminal"])
        self.assertEqual(outcome["evidence_digest"], hashlib.sha256(retained).hexdigest())
        event = self.consumer.accept(frontier, [outcome], "JOIN", expected_old=first_journal)
        self.assertEqual(event["body"]["records"][0]["result"], outcome)

        self.accept("B")
        before_join = self.consumer.history_digest
        joined = self.consumer.join("JOIN", expected_old=before_join)
        self.assertEqual(joined["status"], "NONVERDICT")
        self.assertTrue(joined["all_required_settled"])
        self.assertEqual(joined["missing"], [])
        self.assertEqual(joined["authority"], "NONE")
        self.assertFalse(joined["native_dispatch_authorized"])
        self.assertEqual(self.consumer.history_digest, before_join)
        view = self.consumer.frontier()
        self.assertEqual(view["states"]["NEXT"], "BLOCKED")
        self.assertNotIn("NEXT", view["selected"])

        OBSERVATION.update({
            "issued_before_capture": {"task": "A", "dispatch_id": frontier["dispatch_id"],
                "frontier_graph_digest": frontier["graph_digest"], "input_digest": frontier["inputs"]["A"],
                "input_manifest": probe.pin(manifest)},
            "captured_pair": observed, "captured_pair_descriptor": probe.pin(retained),
            "same_dispatch_accepted_result": outcome, "join": joined, "no_join_append": True,
            "successor": {"state": view["states"]["NEXT"], "selected": view["selected"]},
        })


if __name__ == "__main__":
    log = io.StringIO()
    suite = unittest.TestSuite([InterruptedDispatchCase("test_observe_after_issue_and_settle_without_join_acceptance")])
    run = unittest.TextTestRunner(stream=log).run(suite)
    if not run.wasSuccessful():
        print(log.getvalue(), file=sys.stderr)
        raise SystemExit(1)
    sys.stdout.buffer.write(probe.dump({
        "schema": "dg16.v04.portable-issued-interruption.v1",
        "scope": "PORTABLE_CONSTRUCTED_COMPLETION_OWNER", "authority": "NONE",
        "owner_source_pins": OWNER_PINS, "observation": OBSERVATION,
    }))
