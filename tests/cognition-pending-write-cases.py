"""Real pending-owner writes must remain reloadable; no native admission credit."""
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("pending_durability", ROOT / "tests/cognition-pending-durability.py")
controls = importlib.util.module_from_spec(spec)
spec.loader.exec_module(controls)


class PendingWriteCases(unittest.TestCase):
    def setUp(self):
        self.temporary = None
        location = os.environ.get("R0033_WRITE_EVIDENCE_ROOT")
        if location:
            self.evidence = Path(location) / self._testMethodName
            self.evidence.mkdir(parents=True, exist_ok=False)
        else:
            self.temporary = tempfile.TemporaryDirectory(prefix="pending-write-")
            self.evidence = Path(self.temporary.name)
            self.addCleanup(self.temporary.cleanup)
        self.h = controls.Harness(ROOT, self.evidence)
        repository, common, work = (self.h.fixture / name for name in ("repository", "git-common", "worktree"))
        run = work / ".IMPLEMENTAUDIT/runs/fixture"
        for path in (repository, common, run):
            path.mkdir(parents=True)
        initialized = self.h.call("init", script="host-session-binding.py",
            args=["--store", str(self.h.store), "init", "--owner-id", controls.OWNER])
        self.assertEqual(initialized["status"], "READY")
        fields = {"owner-id": controls.OWNER, "host-id": "codex", "host-session-id": controls.SESSION,
            "controller-id": "fixture-controller", "claim-id": "fixture-claim", "explicit-run-root": run,
            "repository-identity": repository, "git-common-directory-identity": common, "worktree-identity": work,
            "activation-event-id": "fixture-activation", "activation-receipt": "opaque-fixture-activation",
            "continuity-generation": "G0001", "continuity-receipt": "opaque-fixture-continuity"}
        bound = self.h.call("bind", script="host-session-binding.py", args=["--store", str(self.h.store),
            "bind", *[part for key, value in fields.items() for part in ("--" + key, str(value))]])
        self.assertFalse(bound["host_activation_proven"])
        self.limits = {"currentness": "UNRESOLVED", "measured_epoch": None}
        self.h.held(self.h.call("resume", self.limits))

    def test_nonfinite_request_refuses_without_losing_pending_state(self):
        original = self.h.pending.read_bytes()
        for token in ("NaN", "Infinity", "-Infinity", "1e400"):
            with self.subTest(token=token):
                try:
                    wire = '{"currentness":"UNRESOLVED","measured_epoch":' + token + '}'
                    result = self.h.call("resume", raw=wire, expected_exit=2)
                    self.assertEqual(result["status"], "PENDING_OPERATION_REFUSED")
                    self.assertNotIn("decision", result)
                    self.assertEqual(self.h.pending.read_bytes(), original)
                    self.h.held(self.h.call("status"))
                finally:
                    # Fixture reset only; all actual before/after writes and
                    # responses remain in the process records/preimages.
                    self.h.pending.write_bytes(original)

    @staticmethod
    def persisted(value):
        return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")

    def boundary_state(self, headroom):
        state = self.h.state()
        state["revision"] = 9
        next(iter(state["observations"].values()))["version"] = 9
        state["observations"]["retained-boundary"] = dict(id="retained-boundary", kind="UNRESOLVED_SIGNAL",
            version=1, consumed_version=0, proof=dict(logical_occurrence_count=None,
                delivery_count_is_not_occurrence_identity=True, retained_data=""))
        maximum = 8 * 1024 * 1024
        padding = maximum - headroom - len(self.persisted(state))
        self.assertGreater(padding, 0)
        state["observations"]["retained-boundary"]["proof"]["retained_data"] = "x" * padding
        raw = self.persisted(state)
        self.assertEqual(len(raw), maximum - headroom)
        self.h.pending.write_bytes(raw)
        return raw

    def test_exact_reader_bound_refuses_expanding_write_without_replacement(self):
        original = self.boundary_state(0)
        before = self.h.snapshot()
        self.h.held(self.h.call("status"))
        result = self.h.call("resume", self.limits, expected_exit=2)
        self.assertEqual(result["status"], "PENDING_OPERATION_REFUSED")
        self.assertEqual(result["reason"], "PENDING_STATE_BYTE_BOUND")
        self.assertEqual(self.h.pending.read_bytes(), original)
        self.assertEqual(self.h.snapshot(), before)
        self.h.held(self.h.call("status"))

    def test_boundary_successor_is_readable_with_exact_utf8_bytes(self):
        self.boundary_state(3)
        result = self.h.call("resume", self.limits)
        state = self.h.held(result)
        self.assertEqual(state["revision"], 10)
        self.assertEqual(self.h.pending.stat().st_size, 8 * 1024 * 1024 - 1)
        self.assertEqual(self.h.call("status"), result)

    def test_existing_strict_writer_limit_is_not_relaxed(self):
        original = self.boundary_state(2)
        result = self.h.call("resume", self.limits, expected_exit=2)
        self.assertEqual(result["reason"], "PENDING_STATE_BYTE_BOUND")
        self.assertEqual(self.h.pending.read_bytes(), original)

    def test_finite_request_and_unicode_remain_reloadable(self):
        result = self.h.call("resume", {"currentness": "UNRESOLVED", "measured_epoch": "G0002"})
        self.h.held(result)
        self.assertEqual(self.h.call("status"), result)
        state = self.h.state()
        next(iter(state["observations"].values()))["proof"]["retained_note"] = "\u0628\u064a\u0627\u0646"
        self.h.pending.write_bytes(self.persisted(state))
        self.assertEqual(self.h.call("status"), result)


if __name__ == "__main__":
    unittest.main()
