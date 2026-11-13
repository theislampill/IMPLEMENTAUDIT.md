#!/usr/bin/env python3
"""Finite original audit-spec node controls; no canonical-chain claim."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import select
import shutil
import signal
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
HELPER = ROOT / "scripts/qualify-work-graph-finite-leaf.py"


def load(name, path):
    data = path.read_bytes()
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    exec(compile(data, str(path), "exec"), module.__dict__)
    return module, data


H, _ = load("historical_fixture", ROOT / "tests/work-graph-historical-fixture.py")
Q, P = H.Q, H.P


class ProfileFixture:
    PROFILE = None
    SOURCE_ADMISSION_ONLY = True

    def setUp(self):
        self.assertTrue(HELPER.is_file(), "finite original audit-spec profile is absent")
        self.A, self.helper = load("audit_spec_profile", HELPER)
        self.profile = self.PROFILE or self.A.PROFILE
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name)
        self.source = self.base / "source"
        for name in self.A.source_paths(self.profile):
            path = self.source / name
            path.parent.mkdir(parents=True, exist_ok=True)
            if self.SOURCE_ADMISSION_ONLY:
                H.copy_input(name, path)
            else:
                path.write_bytes((ROOT / name).read_bytes())
                path.chmod((ROOT / name).stat().st_mode & 0o777)

    def restore_historical_inputs(self):
        # Construction only, after recursive copies and before any mutation.
        if self.SOURCE_ADMISSION_ONLY:
            H.populate_pins(self.source, self.A.contract_for(self.profile))

    def snapshot(self):
        objects = {}
        state, stamps = self.A.snapshot_source(P, self.source, objects, profile=self.profile)
        return state, stamps, objects

    def source_admission_session(self, session):
        """Test source/resource refusals without claiming a runtime observer.

        The live fixtures retain the unmodified session. Admission fixtures
        replace only the observer prerequisite with an unencodable sentinel;
        reaching runtime acquisition or dispatch is always a test failure.
        """
        if not self.SOURCE_ADMISSION_ONLY:
            return session

        def forbidden_runtime(*_args, **_kwargs):
            raise AssertionError("source-admission fixture reached runtime acquisition")

        scope = session._acquire.__func__.__globals__
        self.assertIn("finite_runtime", scope)
        guards = (
            mock.patch.object(session, "_observer", return_value=mock.sentinel.source_admission_only),
            mock.patch.dict(scope, {"finite_runtime": forbidden_runtime}),
            mock.patch.object(session, "_execute", side_effect=AssertionError(
                "source-admission fixture reached dispatch")),
        )
        for guard in guards:
            guard.start()
            self.addCleanup(guard.stop)
        return session

    def session(self, name="evidence", **options):
        cls = self.A.bind_session(Q.VerifierTaskSession, Q.WG, Q.ROOT, self.helper, profile=self.profile)
        return self.source_admission_session(cls(self.source, self.base / name, **options))


class AdmissionCases(ProfileFixture, unittest.TestCase):
    def test_profile_selects_exact_original_node_without_prefix(self):
        registry = H.original("scripts/verify-package.sh")
        graph, scope, node = self.A.select_node(Q.WG, registry, P.ENVIRONMENT)
        self.assertEqual(len(graph["nodes"]), 117)
        self.assertEqual(node, graph["nodes"][57])
        self.assertEqual(node["id"], "COMMAND:tests/audit-spec.test.sh:0")
        self.assertEqual(node["source"], "bash tests/audit-spec.test.sh\n")
        self.assertEqual(scope["nodes"], [node["id"]])
        self.assertEqual(len(scope["omitted_nodes"]), 116)
        self.assertEqual(scope["profile"], "CONTROLLED_TASK_AUDIT_SPEC_V1")
        with self.assertRaisesRegex(ValueError, "registry"):
            self.A.select_node(Q.WG, registry + b"\n", P.ENVIRONMENT)

    def test_all_nine_literal_inputs_are_acquired_without_git(self):
        state, stamps, objects = self.snapshot()
        self.assertEqual(len(state["files"]), 9)
        self.assertEqual(set(state["files"]), set(self.A.SOURCE_PATHS))
        self.assertFalse((self.source / ".git").exists())
        for name, record in state["files"].items():
            self.assertEqual(objects[record["sha256"]], (self.source / name).read_bytes())
            self.assertIn(name, stamps)
        self.assertIn(".", stamps)

    def test_changed_program_and_registry_refuse_admission(self):
        for name in (*self.A.PROGRAM_PINS, "scripts/verify-package.sh"):
            path = self.source / name
            original = path.read_bytes()
            path.write_bytes(original + b"\n")
            with self.subTest(path=name), self.assertRaisesRegex(ValueError, "source|registry|executable"):
                self.snapshot()
            path.write_bytes(original)

    def test_missing_fixture_refuses_instead_of_passing_expected_negative(self):
        for name in self.A.FIXTURES:
            path = self.source / name
            original = path.read_bytes()
            path.unlink()
            with self.subTest(path=name), self.assertRaises((ValueError, OSError)):
                self.snapshot()
            path.write_bytes(original)

    def test_fixture_link_and_ancestor_alias_refuse(self):
        path = self.source / self.A.FIXTURES[0]
        original = path.read_bytes()
        outside = self.base / "outside"
        outside.write_bytes(original)
        path.unlink()
        path.symlink_to(outside)
        with self.assertRaises((ValueError, OSError)):
            self.snapshot()
        path.unlink()
        os.link(outside, path)
        with self.assertRaises((ValueError, OSError)):
            self.snapshot()
        path.unlink()
        path.write_bytes(original)
        alias = self.base / "alias"
        alias.symlink_to(self.source, target_is_directory=True)
        with self.assertRaises((ValueError, OSError)):
            self.A.snapshot_source(P, alias, {})

    def test_fixture_data_changes_identity_and_remains_subject_input(self):
        first, _, _ = self.snapshot()
        path = self.source / self.A.FIXTURES[0]
        path.write_bytes(path.read_bytes().replace(b"Owner/source:", b"Removed owner:"))
        changed, _, objects = self.snapshot()
        self.assertNotEqual(first, changed)
        self.assertEqual(objects[changed["files"][self.A.FIXTURES[0]]["sha256"]], path.read_bytes())

    def test_no_imported_receipt_and_explicit_session_scope(self):
        session = self.session()
        self.assertEqual(session.SCOPE, self.A.PROFILE)
        self.assertEqual(json.loads((session.output / "session.json").read_bytes())["scope"], self.A.PROFILE)
        with self.assertRaises(TypeError):
            session.run(receipt={"exit": 0})
        self.assertEqual(session.dispatch_count, 0)

    def test_unknown_captured_helper_refuses_before_execution(self):
        engine = self.base / "foreign-engine"
        path = engine / self.A.PREFIX_HELPER
        path.parent.mkdir(parents=True)
        path.write_bytes(b"raise AssertionError('unknown helper must never execute')\n")
        with self.assertRaisesRegex(ValueError, "captured prefix helper"):
            self.A.bind_session(Q.VerifierTaskSession, Q.WG, engine, self.helper)

    def test_changed_program_refuses_before_any_dispatch(self):
        session = self.session()
        path = self.source / "tests/audit-spec.test.sh"
        path.write_bytes(path.read_bytes() + b"\n")
        with self.assertRaisesRegex(ValueError, "executable"):
            session.run()
        self.assertEqual(session.dispatch_count, 0)
        self.assertEqual(list(session.output.rglob("dispatch.json")), [])

    def test_source_admission_cannot_accept_valid_inputs(self):
        session = self.session()
        with self.assertRaisesRegex(AssertionError, "runtime acquisition"):
            session.run()
        self.assertEqual(session.dispatch_count, 0)
        self.assertEqual(session._issued, {})
        self.assertFalse((session.output / "objects").exists())
        self.assertEqual(list(session.output.rglob("result.json")), [])

    def test_missing_observer_tool_refuses_without_dispatch_or_receipt(self):
        session = self.session()
        resolve = Path.resolve
        absent = self.base / "missing-observer-bwrap"

        def missing_tool(path, *args, **kwargs):
            if str(path) == "/usr/bin/bwrap":
                return resolve(absent, *args, **kwargs)
            return resolve(path, *args, **kwargs)

        # Restore the real observer for this capability-refusal control, while
        # retaining the no-runtime/no-dispatch tripwires. No host file changes.
        observer = type(session)._observer.__get__(session, type(session))
        with mock.patch.object(session, "_observer", observer), mock.patch.object(Path, "resolve", missing_tool):
            with self.assertRaises(FileNotFoundError) as error:
                session.run()
        self.assertEqual(error.exception.filename, str(absent))
        self.assertEqual(session.dispatch_count, 0)
        self.assertEqual(session._issued, {})
        self.assertFalse((session.output / "objects").exists())
        self.assertEqual(list(session.output.rglob("dispatch.json")), [])
        self.assertEqual(list(session.output.rglob("result.json")), [])


class RetainedFixture(ProfileFixture):
    SOURCE_ADMISSION_ONLY = False
    LIVE_ENV = "R0035_AUDIT_SPEC_LIVE"
    EVIDENCE_ENV = "R0035_AUDIT_SPEC_EVIDENCE"
    OBJECTS_ENV = "R0035_AUDIT_SPEC_OBJECTS"
    TEST_SOURCE = "tests/work-graph-audit-spec-cases.py"

    @classmethod
    def setUpClass(cls):
        if os.environ.get(cls.LIVE_ENV) != "1":
            raise unittest.SkipTest("set " + cls.LIVE_ENV + "=1 for actual original node controls")

    def setUp(self):
        super().setUp()
        self.addCleanup(self.retain_completed_case)

    def retain_completed_case(self):
        if not os.environ.get(self.EVIDENCE_ENV):
            return
        destination = Path(os.environ[self.EVIDENCE_ENV])
        case = destination / "cases" / self._testMethodName
        case.parent.mkdir(parents=True, exist_ok=True)
        object_store = Path(os.environ.get(self.OBJECTS_ENV, str(destination / "objects")))
        # Retention occurs only after this live test has ended. Objects are
        # deduplicated for storage, never substituted into a live session.
        keys = []
        for path in sorted(self.base.glob("*/objects/*")):
            data = path.read_bytes()
            self.assertEqual(hashlib.sha256(data).hexdigest(), path.name)
            stored = object_store / path.name
            stored.parent.mkdir(parents=True, exist_ok=True)
            if stored.exists():
                self.assertEqual(stored.read_bytes(), data)
            else:
                path.rename(stored)
            keys.append(path.name)
        shutil.copytree(self.base, case, ignore=lambda _directory, names: ["objects"] if "objects" in names else [])
        (case / "retention.json").write_text(json.dumps(dict(
            scope="ACTUAL_INDEPENDENT_ORIGINAL_NODE_NOT_CANONICAL_COMPOSITION",
            profile=self.profile,
            original_fixture_root=str(self.source), retained_input_objects=sorted(set(keys)),
            object_store=os.path.relpath(object_store, case), retention="AFTER_TEST_NO_IMPORTED_LIVE_CUSTODY",
            source_sha256={name:hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in
                ("scripts/qualify-work-graph-finite-leaf.py", "scripts/qualify-work-graph-prefix.py",
                 "scripts/qualify-work-graph-verifier.py", "tests/work-graph-audit-spec-cases.py", self.TEST_SOURCE)},
            authority="NONE"), sort_keys=True) + "\n")


class LiveCases(RetainedFixture, unittest.TestCase):
    """Actual original command via the existing no-proc acquired launcher."""

    def run_original(self, session):
        result = session.run()
        directory = Path(result["evidence_directory"])
        stdout, stderr = ((directory / name).read_bytes() for name in ("stdout.log", "stderr.log"))
        self.assertEqual((directory / "exit-code.txt").read_bytes(), (str(result["exit"]) + "\n").encode())
        receipt = json.loads((directory / "receipt.json").read_bytes())
        self.assertEqual(receipt["node"], self.A.NODE)
        self.assertEqual(receipt["scope"], self.A.PROFILE)
        self.assertEqual(result["group"]["nodes"], [self.A.NODE])
        self.assertEqual(len(result["group"]["omitted_nodes"]), 116)
        return result, stdout, stderr

    def test_original_positive_reuse_then_stale_input_and_foreign_process_refuse(self):
        session = self.session()
        first, stdout, stderr = self.run_original(session)
        self.assertEqual(first["exit"], 0, stderr)
        self.assertTrue(first["complete"])
        self.assertEqual(stdout, b"validate-audit-spec: ok fixtures/audit-spec/valid-mixed.md\naudit-spec.test: ok\n")
        self.assertEqual(stderr, b"")
        second, _, _ = self.run_original(session)
        self.assertEqual((first["disposition"], second["disposition"]), ("EXECUTED", "REUSED"))
        self.assertEqual(first["receipt_digest"], second["receipt_digest"])
        self.assertEqual(session.dispatch_count, 1)
        path = self.source / self.A.FIXTURES[0]
        path.write_bytes(path.read_bytes().replace(b"Owner/source:", b"Removed owner:"))
        with self.assertRaisesRegex(ValueError, "prior receipt refused"):
            session.run()
        self.assertEqual(session.dispatch_count, 1)
        readfd, writefd = os.pipe()
        child = os.fork()
        if child == 0:
            os.close(readfd)
            try:
                session.run()
            except ValueError as exc:
                os.write(writefd, str(exc).encode())
                os._exit(0)
            os._exit(1)
        os.close(writefd)
        try:
            ready, _, _ = select.select([readfd], [], [], 5)
            self.assertTrue(ready, "foreign producer refusal did not return")
            message = os.read(readfd, 4096)
            _, status = os.waitpid(child, 0)
            child = None
            self.assertEqual(os.waitstatus_to_exitcode(status), 0)
            self.assertIn(b"producer process changed", message)
            (self.base / "foreign-process-refusal.txt").write_bytes(message + b"\n")
        finally:
            os.close(readfd)
            if child is not None:
                os.kill(child, signal.SIGKILL)
                os.waitpid(child, 0)

    def test_original_missing_owner_failure_is_actual_and_not_reusable(self):
        path = self.source / self.A.FIXTURES[0]
        mutated = path.read_bytes().replace(b"Owner/source", b"Removed-owner").replace(b"owner/source", b"removed-owner")
        self.assertNotIn(b"owner/source", mutated.lower())
        self.assertNotIn(b"owner source", mutated.lower())
        path.write_bytes(mutated)
        session = self.session()
        result, stdout, stderr = self.run_original(session)
        self.assertEqual(result["exit"], 1, stderr)
        self.assertTrue(result["complete"])
        self.assertEqual(stdout, b"")
        self.assertEqual(stderr, b"validate-audit-spec: fixtures/audit-spec/valid-mixed.md: missing owner/source\n")
        self.assertEqual(session._issued, {})
        with self.assertRaisesRegex(ValueError, "failed or interrupted"):
            session.run()
        self.assertEqual(session.dispatch_count, 1)

    def test_original_valid_data_in_negative_fixture_fails(self):
        (self.source / self.A.FIXTURES[1]).write_bytes((self.source / self.A.FIXTURES[0]).read_bytes())
        session = self.session()
        result, stdout, stderr = self.run_original(session)
        self.assertEqual(result["exit"], 1, stderr)
        self.assertTrue(result["complete"])
        self.assertEqual(stdout, b"validate-audit-spec: ok fixtures/audit-spec/valid-mixed.md\n")
        self.assertEqual(stderr, b"audit-spec.test: expected invalid fixture to fail: fixtures/audit-spec/invalid-missing-owner.md\n")
        self.assertEqual(session._issued, {})

    def test_actual_result_output_drift_and_missing_input_object_refuse(self):
        session = self.session()
        result, _, stderr = self.run_original(session)
        self.assertEqual(result["exit"], 0, stderr)
        retained = session._issued[self.A.PROFILE]
        output = retained["directory"] / "stdout.log"
        original = output.read_bytes()
        output.chmod(0o600)
        output.write_bytes(b"changed retained result\n")
        output.chmod(0o400)
        (self.base / "mutated-stdout.log").write_bytes(output.read_bytes())
        with self.assertRaisesRegex(ValueError, "evidence refused"):
            session.run()
        output.chmod(0o600)
        output.write_bytes(original)
        output.chmod(0o400)
        key = hashlib.sha256((self.source / self.A.FIXTURES[0]).read_bytes()).hexdigest()
        target = session.output / "objects" / key
        data = target.read_bytes()
        target.unlink()
        with self.assertRaisesRegex(ValueError, "evidence refused"):
            session.run()
        self.assertEqual(session.dispatch_count, 1)
        # Restore only after the refusal was observed, retaining both refusal
        # records and the tamper witness; no result is subsequently consumed.
        target.write_bytes(data)
        target.chmod(0o400)


if __name__ == "__main__":
    unittest.main()
