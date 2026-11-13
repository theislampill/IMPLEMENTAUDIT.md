"""New original14 producer/receiver controls; no historical/native episode replay."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import shutil
import sys
import unittest
from unittest import mock

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "skills/implementaudit/scripts"

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@unittest.skipUnless(sys.platform == "linux", "disposable POSIX original14 source receiving")
class Original14HistoryReceiverCases(unittest.TestCase):
    def setUp(self):
        support = load("original14_history_fixture", ROOT / "fixtures/canonical-state-rotation/claim_transaction_test.py")
        self.subject = support.RealHelperIntegration()
        self.addCleanup(self.subject.doCleanups)
        self.subject.setUp()
        self.fixture = self.subject.fixture
        self.controller = support.CONTROLLER
        for name in ("canonical_rotation_inputs.py", "read-canonical-pair.py"):
            shutil.copyfile(CORE / name, self.fixture.scripts / name)
        for name in ("route-transaction.py", "route_request_policy.py"):
            shutil.copyfile(ROOT / "source-peers/route-graph/skills/implementaudit/scripts" / name,
                            self.fixture.scripts / name)
        self.route = load("original14_history_receiver", self.fixture.scripts / "route-transaction.py")

    def recover(self):
        subject = self.subject
        original = subject.helper.read_canonical_generation
        armed = True
        def interrupted(repo, run_root, pointer):
            nonlocal armed
            current = subject.owner.read_ref(repo, subject.context["pointer_ref"])
            oid = subject.owner.write_blob(subject.context, subject.owner.canonical(pointer))
            if current == oid and armed:
                armed = False
                raise RuntimeError("new original14 receiver control: post-CAS receipt not issued")
            return original(repo, run_root, pointer)
        with mock.patch.object(subject.helper, "read_canonical_generation", side_effect=interrupted):
            self.assertEqual(subject.rotate()["status"], "RECOVERED_PRIOR")
        joined = subject.owner.require_current_generation_join_v1(subject.context)
        self.assertEqual(joined["pointer"]["continuity_epoch"], "G0003")
        self.assertIsNone(subject.owner.read_ref(self.fixture.repo,
            subject.owner.receipt_ref(subject.context, "G0002")))
        self.current = joined["receipt_token"]
        self.current_generation = "G0003"
        return joined

    def chain(self, terminal=None):
        return self.route.validate_terminal_continuity_chain(self.fixture.repo,
            controller=self.controller, claim=self.subject.context["claim_id"],
            run_identity=self.fixture.run_root.name, terminal_generation="G0001",
            terminal_receipt=terminal or self.fixture.receipt, current_generation=self.current_generation,
            current_receipt=self.current, require_current_v3=True,
            explicit_run_root=str(self.fixture.run_root))

    def test_actual_recovery_link_is_received_without_a_synthetic_receipt_or_grant(self):
        self.recover()
        before = self.fixture.git("for-each-ref", "--format=%(refname) %(objectname)", "refs/implementaudit/")
        observed = self.fixture.claim("--resolve-retained-continuity-predecessor", self.controller,
            "--receipt", self.current, "--expected-current", self.current)
        self.assertEqual(observed.returncode, 0, observed.stderr.decode())
        producer = json.loads(observed.stdout)
        self.assertEqual(producer["predecessor_receipt_token"], self.fixture.receipt)
        self.assertEqual(producer["grants"], {"currentness": False, "effect": False, "native": False})
        self.assertEqual(self.chain(), [("G0001", self.fixture.receipt), ("G0003", self.current)])
        self.assertEqual(self.fixture.git("for-each-ref", "--format=%(refname) %(objectname)",
                                        "refs/implementaudit/"), before)

    def test_contiguous_original14_history_still_receives(self):
        rotated = self.subject.rotate()
        self.assertEqual(rotated["status"], "ROTATED")
        self.current, self.current_generation = rotated["receipt_token"], "G0002"
        self.assertEqual(self.chain(), [("G0001", self.fixture.receipt), ("G0002", self.current)])

    def test_changed_owner_source_refuses_before_dispatch(self):
        self.recover()
        shell = self.fixture.scripts / "claim-run.sh"
        raw = shell.read_bytes()
        shell.write_bytes(raw[:-1] + b" ")
        original = self.route.subprocess.run
        def no_shell(command, *args, **kwargs):
            if Path(command[0]).name in {"bash", "bash.exe"}:
                self.fail("unsupported historical owner was dispatched")
            return original(command, *args, **kwargs)
        output = io.StringIO()
        with contextlib.redirect_stdout(output), mock.patch.object(self.route.subprocess, "run", no_shell):
            with self.assertRaises(SystemExit) as refused:
                self.chain()
        self.assertEqual(refused.exception.code, 2)
        self.assertIn("source profile is unsupported", output.getvalue())
        self.assertEqual(shell.read_bytes(), raw[:-1] + b" ")

    def test_existing_generation_span_bound_still_refuses(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output), self.assertRaises(SystemExit) as refused:
            self.route.validate_terminal_continuity_chain(self.fixture.repo,
                controller=self.controller, claim=self.subject.context["claim_id"],
                run_identity=self.fixture.run_root.name, terminal_generation="G0001",
                terminal_receipt=self.fixture.receipt, current_generation="G0042",
                current_receipt="unissued", require_current_v3=True,
                explicit_run_root=str(self.fixture.run_root))
        self.assertEqual(refused.exception.code, 2)
        self.assertIn("continuity traversal exceeds its bound", output.getvalue())

    def test_recovered_history_refuses_wrong_endpoint_and_later_invalidation(self):
        self.recover()
        output = io.StringIO()
        with contextlib.redirect_stdout(output), self.assertRaises(SystemExit) as refused:
            self.chain(self.fixture.receipt.split("@", 1)[0] + "@" + "0" * 40)
        self.assertEqual(refused.exception.code, 2)
        self.assertIn("does not reach the terminal", output.getvalue())
        invalidated = self.fixture.claim("--invalidate-continuity", self.controller,
            "--boundary", "new-session", "--event", "new-receiver-uncovered-boundary")
        self.assertEqual(invalidated.returncode, 0, invalidated.stderr.decode())
        before = self.fixture.git("for-each-ref", "--format=%(refname) %(objectname)", "refs/implementaudit/")
        with contextlib.redirect_stdout(io.StringIO()), self.assertRaises(SystemExit) as refused:
            self.chain()
        self.assertEqual(refused.exception.code, 2)
        self.assertEqual(self.fixture.git("for-each-ref", "--format=%(refname) %(objectname)",
                                        "refs/implementaudit/"), before)

    def test_native18_skipped_predecessor_remains_refused(self):
        prefix = "refs/implementaudit/continuity-receipts/" + self.controller + "/"
        fields = ["implementaudit.continuity-receipt.v3", self.controller,
            self.subject.context["claim_id"], self.fixture.run_root.name, "G0003", "1" * 40,
            "refs/implementaudit/current-generations/" + self.controller, "2" * 40,
            "0" * 64, "0" * 64, "0" * 64, "WORK_GRAPH.json", "0" * 64,
            "3" * 40, "0" * 64, "00000000000000000001", "retained-next-action",
            prefix + "G0001@" + "4" * 40]
        oid = self.fixture.blob(("\t".join(fields) + "\n").encode())
        self.fixture.git("update-ref", prefix + "G0003", oid)
        output = io.StringIO()
        with contextlib.redirect_stdout(output), self.assertRaises(SystemExit) as refused:
            self.route.validated_v3_predecessor(self.fixture.repo, prefix + "G0003@" + oid,
                controller=self.controller, claim=self.subject.context["claim_id"],
                run_identity=self.fixture.run_root.name, generation="G0003")
        self.assertEqual(refused.exception.code, 2)
        self.assertIn("continuity predecessor token is foreign or noncanonical", output.getvalue())


if __name__ == "__main__":
    unittest.main(verbosity=2)
