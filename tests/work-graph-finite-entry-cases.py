#!/usr/bin/env python3
"""Receiving entry/custody controls; actual commands are qualified separately."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
DRIVER = "scripts/qualify-work-graph-verifier.py"
HELPER = "scripts/qualify-work-graph-finite-leaf.py"
PROFILES = {
    "audit-spec": "CONTROLLED_TASK_AUDIT_SPEC_V1",
    "andon-class": "CONTROLLED_TASK_ANDON_CLASS_V1",
    "registry-wrapper": "CONTROLLED_TASK_REGISTRY_WRAPPER_V1",
    "marker-order": "CONTROLLED_TASK_MARKER_ORDER_V1",
    "commit-message": "CONTROLLED_TASK_COMMIT_MESSAGE_V1",
    "agents-bootstrap": "CONTROLLED_TASK_AGENTS_BOOTSTRAP_V1",
    "andon-escalation": "CONTROLLED_TASK_ANDON_ESCALATION_V1",
    "internal-skill-topology": "CONTROLLED_TASK_INTERNAL_SKILL_TOPOLOGY_V1",
    "capability-ledger": "CONTROLLED_TASK_CAPABILITY_LEDGER_V1",
    "issues-deferred": "CONTROLLED_TASK_ISSUES_DEFERRED_V1",
    "no-terminal-cap": "CONTROLLED_TASK_NO_TERMINAL_CAP_V1",
    "background-chain": "CONTROLLED_TASK_BACKGROUND_CHAIN_V1",
    "plan-lifecycle": "CONTROLLED_TASK_PLAN_LIFECYCLE_V1",
    "plan-quality": "CONTROLLED_TASK_PLAN_QUALITY_V1",
    "authorization-binding": "CONTROLLED_TASK_AUTHORIZATION_BINDING_V1",
    "read-only-plans": "CONTROLLED_TASK_READ_ONLY_PLANS_V1",
    "safeguard-restoration": "CONTROLLED_TASK_SAFEGUARD_RESTORATION_V1",
    "routing": "CONTROLLED_TASK_ROUTING_V1",
    "audit-object-routing": "CONTROLLED_TASK_AUDIT_OBJECT_ROUTING_V1",
    "installed-payload": "CONTROLLED_TASK_INSTALLED_PAYLOAD_V1",
    "planner-copy": "CONTROLLED_TASK_PLANNER_COPY_V1",
    "fanout-coverage": "CONTROLLED_TASK_FANOUT_COVERAGE_V1",
    "skill-layout": "CONTROLLED_TASK_SKILL_LAYOUT_V1",
    "native-integration": "CONTROLLED_TASK_NATIVE_INTEGRATION_V1",
    "audit-retention": "CONTROLLED_TASK_AUDIT_RETENTION_V1",
    "audit-object-contract": "CONTROLLED_TASK_AUDIT_OBJECT_CONTRACT_V1",
    "claim-boundary": "CONTROLLED_TASK_CLAIM_BOUNDARY_V1",
    "terminology-integration": "CONTROLLED_TASK_TERMINOLOGY_INTEGRATION_V1",
    "lean-discipline": "CONTROLLED_TASK_LEAN_DISCIPLINE_V1",
    "internal-skill-routing": "CONTROLLED_TASK_INTERNAL_SKILL_ROUTING_V1",
    "bootstrap-load-budget": "CONTROLLED_TASK_BOOTSTRAP_LOAD_BUDGET_V1",
    "respec-impact-set": "CONTROLLED_TASK_RESPEC_IMPACT_SET_V1",
    "package-shape-claims": "CONTROLLED_TASK_PACKAGE_SHAPE_CLAIMS_V1",
    "mini-audit-loop": "CONTROLLED_TASK_MINI_AUDIT_LOOP_V1",
}


def load(root=ROOT):
    path = root / DRIVER
    spec = importlib.util.spec_from_file_location("finite_entry_qualifier", path)
    module = importlib.util.module_from_spec(spec)
    exec(compile(path.read_bytes(), str(path), "exec"), module.__dict__)
    return module


class FactoryCases(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name)
        self.q = load()

    def test_all_explicit_profiles_have_separate_live_session_custody(self):
        self.assertEqual(self.q._FINITE_MODES, PROFILES)
        sessions = [self.q.create_finite_leaf_session(ROOT, self.base / mode, profile=profile)
                    for mode, profile in PROFILES.items()]
        self.assertEqual([s.SCOPE for s in sessions], list(PROFILES.values()))
        self.assertEqual(len({type(s) for s in sessions}), len(PROFILES))
        self.assertEqual(len({s.producer for s in sessions}), len(PROFILES))
        for s in sessions:
            record = json.loads((s.output / "session.json").read_bytes())
            self.assertEqual(record["receipt_custody"], "LIVE_PRODUCER_ONLY_NO_IMPORT")
            self.assertEqual(s.dispatch_count, 0)
            self.assertEqual(record["engine"][HELPER], self.q.sha((ROOT / HELPER).read_bytes()))
            with self.assertRaises(TypeError):
                s.run(receipt={"exit": 0})

    def test_default_and_repeated_profile_keep_unique_evidence_and_producer(self):
        first = self.q.create_finite_leaf_session(ROOT, self.base / "one")
        second = self.q.create_finite_leaf_session(ROOT, self.base / "two")
        self.assertEqual(first.SCOPE, PROFILES["audit-spec"])
        self.assertIs(type(first), type(second))
        self.assertNotEqual(first.producer, second.producer)
        self.assertIsNot(first._issued, second._issued)
        with self.assertRaises(FileExistsError):
            self.q.create_finite_leaf_session(ROOT, first.output)

    def test_unknown_profiles_refuse_before_evidence_creation(self):
        for index, profile in enumerate(("UNKNOWN", "CONTROLLED_TASK_REGISTRY_V1", None, [], True)):
            output = self.base / str(index)
            with self.subTest(profile=profile), self.assertRaises(ValueError):
                self.q.create_finite_leaf_session(ROOT, output, profile=profile)
            self.assertFalse(output.exists())

    def test_changed_cached_helper_and_same_bytes_foreign_engine_refuse_custody(self):
        engine = self.base / "engine"
        for name in (DRIVER, HELPER, "scripts/qualify-work-graph-prefix.py",
                     "scripts/run-work-graph-verifier.sh", "skills/implementaudit/scripts/compile-work-graph.py"):
            path = engine / name
            path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, path)
        q = load(engine)
        session = q.create_finite_leaf_session(ROOT, self.base / "first")
        path = engine / HELPER
        path.write_bytes(path.read_bytes() + b"\n")
        with self.assertRaisesRegex(ValueError, "loaded finite-leaf helper differs"):
            session._custody()
        self.assertEqual(session.dispatch_count, 0)
        self.assertEqual(list(session.output.rglob("receipt.json")), [])
        with self.assertRaisesRegex(ValueError, "loaded finite-leaf helper differs"):
            q.create_finite_leaf_session(ROOT, self.base / "second")
        # An alias is refused even when its bytes would match the captured source.
        path.unlink()
        path.symlink_to(ROOT / HELPER)
        with self.assertRaises(ValueError):
            session._custody()


class ProtocolCases(unittest.TestCase):
    """Protocol routing only: fakes below never count as executed node evidence."""
    def setUp(self):
        self.q = load()
        self.calls = []

    def main(self, mode, request, *, result=None, extra=()):
        self.calls = []
        result = dict(exit=0, complete=True, scope="PROTOCOL_TEST_ONLY") if result is None else result
        session = mock.Mock()
        session.run.return_value = result
        def factory(*paths, **options):
            self.calls.append((paths, options))
            return session
        output, errors = io.StringIO(), io.StringIO()
        stdin = io.TextIOWrapper(io.BytesIO(request), encoding="utf-8")
        with mock.patch.object(self.q, "create_finite_leaf_session", side_effect=factory), \
             mock.patch.object(sys, "argv", [DRIVER, mode, "/source", "/evidence", *extra]), \
             mock.patch.object(sys, "stdin", stdin), \
             contextlib.redirect_stdout(output), contextlib.redirect_stderr(errors):
            code = self.q.main()
        return code, session.run.call_count, output.getvalue(), errors.getvalue()

    def test_exact_modes_route_two_run_requests_without_receipt_input(self):
        for mode, profile in PROFILES.items():
            with self.subTest(mode=mode):
                code, calls, out, err = self.main(mode, b'{"operation":"run"}\n' * 2)
                self.assertEqual((code, calls, err), (0, 2, ""))
                self.assertEqual(len(out.splitlines()), 2)
                self.assertEqual(self.calls, [((Path("/source"), Path("/evidence")), {"profile": profile})])

    def test_injection_duplicate_keys_and_oversized_requests_never_reach_run(self):
        bad = [b'{"operation":"run","receipt":{"exit":0}}\n',
               b'{"operation":"run","command":"true"}\n',
               b'{"operation":"run","operation":"run"}\n',
               b'{"operation":"reuse"}\n', b' ' * 4097 + b'\n']
        for mode in PROFILES:
            for request in bad:
                with self.subTest(mode=mode, request=request[:70]):
                    code, calls, out, err = self.main(mode, request)
                    self.assertEqual((code, calls, out), (2, 0, ""))
                    self.assertTrue(err)

    def test_actual_result_status_mapping_refuses_signal_and_incomplete_success(self):
        for mode in PROFILES:
            for result, expected in [(dict(exit=-9, complete=False), 1),
                                     (dict(exit=0, complete=False), 1),
                                     (dict(exit=7, complete=True), 7)]:
                with self.subTest(mode=mode, result=result):
                    code, calls, out, err = self.main(mode, b'{"operation":"run"}\n', result=result)
                    self.assertEqual((code, calls, err), (expected, 1, ""))
                    self.assertEqual(json.loads(out), result)

    def test_capture_options_refuse_before_factory(self):
        for mode in PROFILES:
            with self.subTest(mode=mode):
                code, calls, out, err = self.main(mode, b'{"operation":"run"}\n', extra=("--empty-stdin",))
                self.assertEqual((code, calls, out, self.calls), (2, 0, "", []))
                self.assertIn("require a legacy or dag capture", err)


if __name__ == "__main__":
    unittest.main()
