#!/usr/bin/env python3
"""Original44 source/admission controls; no original execution or authority."""
import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("respec_support", ROOT / "tests/work-graph-audit-spec-cases.py")
shared = importlib.util.module_from_spec(spec)
spec.loader.exec_module(shared)
Q, P = shared.Q, shared.P
PROFILE = "CONTROLLED_TASK_RESPEC_IMPACT_SET_V1"
MODE = "respec-impact-set"
PROGRAM = "tests/respec-impact-set-contract.test.sh"
CHECKER = "skills/implementaudit/scripts/check-respec-impact-set.sh"
CLOSURE = "skills/implementaudit/scripts/check-closure-surface.sh"
SCHEMA = "eval/check_fixture_schema.py"
DATA = (
    "skills/implementaudit/templates/respec-impact-set.md",
    "skills/implementaudit/references/phase-design.md",
    "skills/implementaudit/templates/phase-goal.txt",
    "fixtures/respec-impact-set/cases.json",
)


class CatalogCases(unittest.TestCase):
    def test_original44_profile_and_exact_consumers(self):
        # Removing this profile or either transitive checker must fail here.
        A, _ = shared.load("respec_catalog", ROOT / "scripts/qualify-work-graph-finite-leaf.py")
        try:
            contract = A.contract_for(PROFILE)
        except ValueError as error:
            self.fail("missing exact original44 profile/source consumer: " + str(error))
        registry = (ROOT / "scripts/verify-package.sh").read_bytes()
        graph, scope, node = A.select_node(Q.WG, registry, P.ENVIRONMENT, profile=PROFILE)
        self.assertEqual((len(graph["nodes"]), node), (117, graph["nodes"][44]))
        self.assertEqual(node["source"], "bash tests/respec-impact-set-contract.test.sh\n")
        self.assertEqual(scope["nodes"], ["COMMAND:tests/respec-impact-set-contract.test.sh:0"])
        self.assertEqual(len(scope["omitted_nodes"]), 116)
        self.assertEqual(set(contract["programs"]), {PROGRAM, CHECKER, CLOSURE})
        self.assertEqual(set(A.source_paths(PROFILE)), {"scripts/verify-package.sh", PROGRAM, CHECKER, CLOSURE, *DATA})
        self.assertEqual(contract["absent"], (SCHEMA,))
        self.assertEqual(contract["recursive"]["roots"], ())
        self.assertEqual(contract["recursive"]["optional_files"], (SCHEMA,))
        self.assertEqual(Q._FINITE_MODES[MODE], PROFILE)
        with self.assertRaisesRegex(ValueError, "registry"):
            A.select_node(Q.WG, registry + b"\n", P.ENVIRONMENT, profile=PROFILE)


class RespecFixture(shared.ProfileFixture):
    PROFILE = PROFILE

    def setUp(self):
        super().setUp()
        (self.source / "eval").mkdir(mode=0o755)

    def session(self, name="evidence"):
        return self.source_admission_session(Q.create_finite_leaf_session(
            self.source, self.base / name, profile=PROFILE))

    def no_execution(self, session):
        self.assertEqual(session.dispatch_count, 0)
        self.assertEqual(session._issued, {})
        self.assertFalse((session.output / "objects").exists())
        self.assertEqual(list(session.output.rglob("receipt.json")), [])


class AdmissionCases(RespecFixture, unittest.TestCase):
    def test_all_inputs_and_typed_absence_are_acquired(self):
        # Dropping a literal read, losing bytes, or omitting the absence fails.
        state, stamps, objects = self.snapshot()
        self.assertEqual(set(state["files"]), {"scripts/verify-package.sh", PROGRAM, CHECKER, CLOSURE, *DATA})
        for name, record in state["files"].items():
            self.assertEqual(objects[record["sha256"]], (self.source / name).read_bytes())
            self.assertIn(name, stamps)
        self.assertEqual(state["recursive_inputs"]["projection"]["probes"], {
            SCHEMA: {"kind": "MISSING", "missing_at": SCHEMA}})
        self.assertIn("eval", state["directories"])
        self.assertNotIn(SCHEMA, self.A.image_subject(state, profile=PROFILE))
        self.assertNotIn("scripts/verify-package.sh", self.A.image_subject(state, profile=PROFILE))
        (self.source / "eval").rmdir()
        absent_parent, _, _ = self.snapshot()
        self.assertEqual(absent_parent["recursive_inputs"]["projection"]["probes"][SCHEMA],
                         {"kind": "MISSING", "missing_at": "eval"})
        self.assertNotEqual(state, absent_parent)

    def test_present_schema_and_unsupported_presence_refuse_before_runtime(self):
        # A swallowed execution must not admit an unpinned new program.
        path = self.source / SCHEMA
        outside = self.base / "outside-schema"
        outside.write_bytes(b"raise SystemExit(0)\n")
        for index, kind in enumerate(("file", "symlink", "hardlink", "directory", "fifo")):
            if kind == "file":
                path.write_bytes(b"raise SystemExit(0)\n")
            elif kind == "symlink":
                path.symlink_to(outside)
            elif kind == "hardlink":
                os.link(outside, path)
            elif kind == "directory":
                path.mkdir()
            else:
                os.mkfifo(path, 0o644)
            session = self.session("schema-" + str(index))
            with self.subTest(kind=kind), self.assertRaises((ValueError, OSError)):
                session.run()
            self.no_execution(session)
            if kind == "directory":
                path.rmdir()
            else:
                path.unlink()

    def test_schema_absence_is_rechecked_during_acquisition(self):
        # Publishing the absent name between the probe and closing census fails.
        real_stat = os.stat
        created = False
        def replace_after_absence(path, *args, **kwargs):
            nonlocal created
            try:
                return real_stat(path, *args, **kwargs)
            except FileNotFoundError:
                if path == "check_fixture_schema.py" and kwargs.get("dir_fd") is not None and not created:
                    created = True
                    (self.source / SCHEMA).write_bytes(b"raise SystemExit(0)\n")
                raise
        with mock.patch.object(self.A.os, "stat", side_effect=replace_after_absence), \
             self.assertRaisesRegex(ValueError, "presence|ancestor|source"):
            self.snapshot()
        self.assertTrue(created)

    def test_changed_programs_registry_and_missing_data_refuse_before_runtime(self):
        # Relaxed program pins or silently skipped required data fail this bank.
        for index, name in enumerate((PROGRAM, CHECKER, CLOSURE, "scripts/verify-package.sh")):
            path = self.source / name
            raw = path.read_bytes()
            path.write_bytes(raw + b"\n")
            session = self.session("program-" + str(index))
            with self.subTest(changed=name), self.assertRaisesRegex(ValueError, "source|registry|executable"):
                session.run()
            self.no_execution(session)
            path.write_bytes(raw)
        for index, name in enumerate(DATA):
            path = self.source / name
            raw = path.read_bytes()
            path.unlink()
            session = self.session("missing-" + str(index))
            with self.subTest(missing=name), self.assertRaises((OSError, ValueError)):
                session.run()
            self.no_execution(session)
            path.write_bytes(raw)
            path.chmod(0o644)

    def test_data_aliases_and_eval_ancestor_alias_refuse(self):
        # Following aliases would change which source bytes or absence was bound.
        path = self.source / DATA[-1]
        raw = path.read_bytes()
        outside = self.base / "outside-data"
        outside.write_bytes(raw)
        path.unlink()
        path.symlink_to(outside)
        with self.assertRaises((ValueError, OSError)):
            self.snapshot()
        path.unlink()
        os.link(outside, path)
        with self.assertRaises((ValueError, OSError)):
            self.snapshot()
        path.unlink()
        path.write_bytes(raw)
        external_eval = self.base / "external-eval"
        external_eval.mkdir()
        (self.source / "eval").rmdir()
        (self.source / "eval").symlink_to(external_eval, target_is_directory=True)
        with self.assertRaises((ValueError, OSError)):
            self.snapshot()
        (self.source / "eval").unlink()
        (self.source / "eval").mkdir()
        alias = self.base / "aliased-source"
        alias.symlink_to(self.source, target_is_directory=True)
        with self.assertRaises((ValueError, OSError)):
            self.A.snapshot_source(P, alias, {}, profile=PROFILE)

    def test_semantic_fixture_and_doc_changes_are_not_preaccepted(self):
        # Semantic data remains acquired input, never an admission-time verdict.
        before, _, _ = self.snapshot()
        path = self.source / DATA[-1]
        path.write_bytes(path.read_bytes().replace(b'"R4-F9"', b'"R4-NOT-F9"'))
        template = self.source / DATA[0]
        template.write_bytes(template.read_bytes().replace(b"IMPLEMENTAUDIT_RESPEC_IMPACT_SET", b"REMOVED_MARKER"))
        after, _, objects = self.snapshot()
        self.assertNotEqual(before, after)
        for name in (DATA[-1], DATA[0]):
            self.assertNotEqual(before["files"][name], after["files"][name])
            self.assertEqual(objects[after["files"][name]["sha256"]], (self.source / name).read_bytes())
        session = self.session()
        with self.assertRaisesRegex(AssertionError, "runtime acquisition"):
            session.run()
        self.no_execution(session)

    def test_private_outputs_spools_and_resource_boundaries(self):
        # Undercharging fixed writes or accepting insufficient capacity fails.
        state, _, _ = self.snapshot()
        reservation = self.A.temporary_requirements(state, profile=PROFILE)
        self.assertEqual((reservation["copies"], reservation["files"], reservation["directories"]), (0, 34, 1))
        self.assertEqual((reservation["generated_files"], reservation["sed_temporary_files"],
                          reservation["checker_spools"], reservation["wrapper_spools"]), (17, 2, 14, 1))
        self.assertGreaterEqual(reservation["checker_spool_bytes"], 14 * (ROOT / CHECKER).stat().st_size)
        self.assertGreaterEqual(reservation["largest_file_bytes"], 65536)
        self.assertLess(reservation["required_bytes"], 32 * 1024**2)
        limits = dict(scratch_bytes=32 * 1024**2, file_bytes=16 * 1024**2,
                      stream_bytes=16 * 1024**2, address_bytes=1024**3)
        self.A.require_resource_capacity(reservation, limits)
        for field, value in (("scratch_bytes", reservation["required_bytes"] - 1),
                             ("file_bytes", reservation["largest_file_bytes"] - 1),
                             ("stream_bytes", reservation["max_stderr_bytes"] - 1),
                             ("address_bytes", reservation["original_data_memory_reservation"])):
            with self.subTest(limit=field), self.assertRaisesRegex(ValueError, "capacity"):
                self.A.require_resource_capacity(reservation, dict(limits, **{field: value}))
        original = self.source / DATA[-1]
        original.write_bytes(original.read_bytes() + b" " * 4096)
        larger, _, _ = self.snapshot()
        increased = self.A.temporary_requirements(larger, profile=PROFILE)
        self.assertGreater(increased["max_stderr_bytes"], reservation["max_stderr_bytes"])
        self.assertGreater(increased["original_data_memory_reservation"], reservation["original_data_memory_reservation"])
        original.write_bytes(b" " * (128 * 1024 + 1))
        with self.assertRaises((ValueError, OSError)):
            self.snapshot()


class EntryCases(RespecFixture, unittest.TestCase):
    def test_fixed_environment_disallows_respec_checker_override(self):
        # A caller-selected checker may never enter the fixed execution branch.
        session = self.session()
        self.assertNotIn("RESPEC_CHECKER", session.environment)
        session.environment["RESPEC_CHECKER"] = "/unqualified/checker"
        with self.assertRaisesRegex(ValueError, "environment"):
            session.run()
        self.no_execution(session)

    def test_public_mode_refuses_receipts_and_capture_options(self):
        # Actual parser/factory paths reject injected results before acquisition.
        requests = (b'{"operation":"run","receipt":{"exit":0}}\n',
                    b'{"operation":"run","command":"true"}\n',
                    b'{"operation":"run","operation":"run"}\n',
                    b' ' * 4097 + b'\n')
        for index, request in enumerate(requests):
            output = self.base / ("request-" + str(index))
            stdout, stderr = io.StringIO(), io.StringIO()
            stdin = io.TextIOWrapper(io.BytesIO(request), encoding="utf-8")
            with mock.patch.object(sys, "argv", ["qualifier", MODE, str(self.source), str(output)]), \
                 mock.patch.object(sys, "stdin", stdin), \
                 contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                status = Q.main()
            self.assertEqual((status, stdout.getvalue()), (2, ""))
            self.assertTrue(stderr.getvalue())
            self.assertEqual(json.loads((output / "session.json").read_bytes())["scope"], PROFILE)
            self.assertEqual(list(output.glob("generation-*")), [])
            self.assertEqual(list(output.rglob("receipt.json")), [])
        output = self.base / "capture-option"
        with mock.patch.object(sys, "argv", ["qualifier", MODE, str(self.source), str(output), "--empty-stdin"]), \
             contextlib.redirect_stderr(io.StringIO()):
            status = Q.main()
        self.assertEqual(status, 2)
        self.assertFalse(output.exists())

    def test_cached_helper_custody_change_refuses(self):
        # Cached code cannot outlive the exact source engine that issued it.
        engine = self.base / "engine"
        for name in ("scripts/qualify-work-graph-verifier.py", "scripts/qualify-work-graph-finite-leaf.py",
                     "scripts/qualify-work-graph-prefix.py", "scripts/run-work-graph-verifier.sh",
                     "skills/implementaudit/scripts/compile-work-graph.py"):
            path = engine / name
            path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, path)
        qualifier, _ = shared.load("respec_changed_engine", engine / "scripts/qualify-work-graph-verifier.py")
        session = qualifier.create_finite_leaf_session(self.source, self.base / "held", profile=PROFILE)
        helper = engine / "scripts/qualify-work-graph-finite-leaf.py"
        helper.write_bytes(helper.read_bytes() + b"\n")
        with self.assertRaisesRegex(ValueError, "loaded finite-leaf helper differs"):
            session._custody()
        self.no_execution(session)


class IntegrationCases(unittest.TestCase):
    def test_new_bank_reaches_capture_environment_boundary(self):
        # This changed wrapper population is observed through its existing probe.
        # The probe intercepts Python banks; it grants no original execution credit.
        verifier, _ = shared.load("respec_capture_boundary", ROOT / "tests/work-graph-verifier-cases.py")
        with tempfile.TemporaryDirectory() as temporary:
            verifier.fixture_capture_environment_cases(Path(temporary) / "capture")


if __name__ == "__main__":
    unittest.main()
