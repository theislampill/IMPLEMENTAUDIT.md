#!/usr/bin/env python3
"""Original node46 complete copies and conservative resource/runtime admission."""
import copy
import importlib.util
import os
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]

_historical_spec = importlib.util.spec_from_file_location("historical_fixture", ROOT / "tests/work-graph-historical-fixture.py")
H = importlib.util.module_from_spec(_historical_spec)
_historical_spec.loader.exec_module(H)
spec = importlib.util.spec_from_file_location("planner_copy_support", ROOT / "tests/work-graph-audit-spec-cases.py")
shared = importlib.util.module_from_spec(spec)
spec.loader.exec_module(shared)
Q, P = shared.Q, shared.P
PROFILE = "CONTROLLED_TASK_PLANNER_COPY_V1"
PROGRAM = "tests/planner-stages.test.sh"


class CatalogCases(unittest.TestCase):
    def test_exact_original46_has_a_separate_bounded_copy_contract(self):
        A, _ = shared.load("planner_copy_catalog", ROOT / "scripts/qualify-work-graph-finite-leaf.py")
        try:
            contract = A.contract_for(PROFILE)
        except ValueError as error:
            self.fail("missing original46 acquisition profile: " + str(error))
        graph, scope, node = A.select_node(Q.WG, H.original("scripts/verify-package.sh"), P.ENVIRONMENT, profile=PROFILE)
        self.assertEqual((len(graph["nodes"]), node), (117, graph["nodes"][46]))
        self.assertEqual(node["source"], "bash " + PROGRAM + "\n")
        self.assertEqual(len(scope["omitted_nodes"]), 116)
        self.assertEqual(scope["nodes"], ["COMMAND:" + PROGRAM + ":0"])
        self.assertEqual(Q._FINITE_MODES["planner-copy"], PROFILE)
        self.assertEqual(contract["recursive"]["roots"], ("skills", "fixtures"))
        self.assertEqual(contract["source_modes"], "PRESERVE_READ_ONLY_MOUNT")
        self.assertEqual(set(contract["programs"]), {PROGRAM, "scripts/check-planner-stages.sh"})
        self.assertEqual(contract["scratch_bytes"], 256 * 1024**2)

    def test_fixed_profile_scratch_limits_preserve_defaults_and_planner_image_key(self):
        A, raw = shared.load("planner_copy_limits", ROOT / "scripts/qualify-work-graph-finite-leaf.py")
        parent = P.bind_session(Q.VerifierTaskSession, Q.WG, Q.ROOT,
            (Q.ROOT / "scripts/qualify-work-graph-prefix.py").read_bytes())
        classes = {}
        for profile in Q._FINITE_MODES.values():
            cls = A.bind_session(Q.VerifierTaskSession, Q.WG, Q.ROOT, raw, profile=profile)
            classes[profile] = cls
            expected = dict(parent.LIMITS)
            if profile == PROFILE:
                expected["scratch_bytes"] = 256 * 1024**2
            elif profile == "CONTROLLED_TASK_NATIVE_INTEGRATION_V1":
                expected["scratch_bytes"] = 128 * 1024**2
            elif profile == "CONTROLLED_TASK_AUDIT_OBJECT_CONTRACT_V1":
                expected["scratch_bytes"] = 64 * 1024**2
            elif profile == "CONTROLLED_TASK_TERMINOLOGY_INTEGRATION_V1":
                expected["scratch_bytes"] = 512 * 1024**2
            elif profile == "CONTROLLED_TASK_LEAN_DISCIPLINE_V1":
                expected["scratch_bytes"] = 512 * 1024**2
            elif profile == "CONTROLLED_TASK_PACKAGE_SHAPE_CLAIMS_V1":
                expected["scratch_bytes"] = 64 * 1024**2
            with self.subTest(profile=profile):
                self.assertEqual(cls.LIMITS, expected)
        self.assertEqual(parent.LIMITS["scratch_bytes"], 32 * 1024**2)
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            prior = classes[A.PROFILE](ROOT, base / "old")
            planner = classes[PROFILE](ROOT, base / "planner")
            old_image, old_key = prior._image({"/work/test": (b"same bytes", 0o444)}, {})
            image, key = planner._image({"/work/test": (b"same bytes", 0o444)}, {})
            self.assertEqual(image["limits"]["scratch_bytes"], 256 * 1024**2)
            self.assertEqual(old_image["limits"]["scratch_bytes"], 32 * 1024**2)
            self.assertNotEqual(key, old_key)
            self.assertEqual(prior.dispatch_count + planner.dispatch_count, 0)


class CopyFixture(shared.ProfileFixture):
    PROFILE = PROFILE

    def setUp(self):
        super().setUp()
        for name in ("skills", "fixtures"):
            shutil.copytree(ROOT / name, self.source / name, dirs_exist_ok=True)
        self.restore_historical_inputs()

    def session(self, name="evidence", **options):
        return self.source_admission_session(Q.create_finite_leaf_session(
            self.source, self.base / name, profile=PROFILE, **options))


class AdmissionCases(CopyFixture, unittest.TestCase):
    def test_complete_copy_population_includes_unread_dot_binary_and_empty_members(self):
        path = self.source / "fixtures/.copy-observed/.binary"
        path.parent.mkdir(parents=True)
        path.write_bytes(b"\x00\xff\xfe copied even when checker never reads this file")
        (path.parent / ".empty").mkdir()
        state, _, objects = self.snapshot()
        for tree in ("skills", "fixtures"):
            expected = {p.relative_to(self.source).as_posix(): p.read_bytes() for p in (self.source / tree).rglob("*") if p.is_file()}
            actual = {name: objects[value["sha256"]] for name, value in state["files"].items() if name.startswith(tree + "/")}
            self.assertEqual(actual, expected)
        self.assertIn("fixtures/.copy-observed/.empty", state["directories"])
        self.assertEqual(state["files"]["skills/implementaudit/references/plan-lifecycle.md"]["mode"], 0o644)

    def test_exact_peak_two_tree_pairs_and_inplace_file_are_reserved(self):
        state, _, _ = self.snapshot()
        reservation = self.A.temporary_requirements(state, profile=PROFILE)
        files = [value["bytes"] for name, value in state["files"].items() if name.startswith(("skills/", "fixtures/"))]
        directories = [name for name in state["directories"] if name in ("skills", "fixtures") or name.startswith(("skills/", "fixtures/"))]
        self.assertEqual(reservation["copies"], 2)
        self.assertEqual(reservation["original_copy_phases"], 3)
        self.assertEqual(reservation["files"], 2 * len(files) + 6)
        self.assertEqual(reservation["directories"], 2 * len(directories) + 6)
        self.assertEqual(reservation["copied_source_bytes"], sum(files))
        self.assertEqual(reservation["allocation_granule"], 65536)
        self.assertGreater(reservation["required_bytes"], 32 * 1024**2)

    def test_complete_source_refuses_old_capacity_and_admits_only_bounded_planner_profile(self):
        state, _, _ = self.snapshot()
        reservation = self.A.temporary_requirements(state, profile=PROFILE)
        session = self.session()
        self.assertEqual(session.LIMITS["scratch_bytes"], 256 * 1024**2)
        with self.assertRaisesRegex(ValueError, "temporary write set exceeds scratch capacity"):
            self.A.require_resource_capacity(reservation, dict(session.LIMITS, scratch_bytes=32 * 1024**2))
        self.A.require_resource_capacity(reservation, session.LIMITS)
        with self.assertRaisesRegex(AssertionError, "source-admission fixture reached runtime acquisition"):
            session.run()
        self.assertEqual(session.dispatch_count, 0)
        self.assertEqual(session._issued, {})
        self.assertFalse((session.output / "objects").exists())

    def test_larger_scratch_still_refuses_capacity_file_and_stream_excess(self):
        state, _, _ = self.snapshot()
        reservation = self.A.temporary_requirements(state, profile=PROFILE)
        session = self.session()
        for field, limit in (("largest_file_bytes", session.LIMITS["file_bytes"]),
                             ("max_stdout_bytes", session.LIMITS["stream_bytes"]),
                             ("max_stderr_bytes", session.LIMITS["stream_bytes"])):
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, "original file/stream capacity"):
                self.A.require_resource_capacity(dict(reservation, **{field: limit + 1}), session.LIMITS)
        # Empty files still consume the unchanged per-file metadata reserve.
        # The complete source stays inside the existing entry/byte bounds.
        for number in range(600):
            (self.source / "fixtures" / (".capacity-%04d" % number)).write_bytes(b"")
        state, _, _ = self.snapshot()
        over = self.A.temporary_requirements(state, profile=PROFILE)
        self.assertGreater(over["required_bytes"], session.LIMITS["scratch_bytes"])
        with self.assertRaisesRegex(ValueError, "temporary write set exceeds scratch capacity"):
            session.run()
        self.assertEqual(session.dispatch_count, 0)
        self.assertEqual(session._issued, {})
        self.assertFalse((session.output / "objects").exists())

    def test_missing_cp_operand_or_required_checker_input_refuses(self):
        for name in ("README.md", "docs/diagrams/execution-spine.mmd", "docs/portal/pages/planning-and-phases.html", "skills/implementaudit/references/planning-depth.md"):
            path = self.source / name
            raw, mode = path.read_bytes(), path.stat().st_mode & 0o777
            path.unlink()
            with self.subTest(path=name), self.assertRaises((ValueError, OSError)):
                self.snapshot()
            path.write_bytes(raw)
            path.chmod(mode)

    def test_program_drift_and_copy_alias_refuse_without_partial_population(self):
        path = self.source / PROGRAM
        raw = path.read_bytes()
        path.write_bytes(raw + b"\n")
        with self.assertRaisesRegex(ValueError, "executable"):
            self.snapshot()
        path.write_bytes(raw)
        alias = self.source / "fixtures/.unobserved-link"
        alias.symlink_to(self.source / "README.md")
        with self.assertRaises((ValueError, OSError)):
            self.snapshot()


class RuntimeCases(unittest.TestCase):
    def setUp(self):
        self.A, _ = shared.load("planner_copy_runtime", ROOT / "scripts/qualify-work-graph-finite-leaf.py")
        self.objects = {}
        self.dependencies = set(self.A._PLANNER_RUNTIME_PINS) - {"/usr/bin/perl"}
        # Presence-only inputs for early refusal controls, never a qualified
        # runtime. Successful capture below uses actual physical bytes.
        self.runtime = dict(files={name: {} for name in self.dependencies},
                            observations={name: {} for name in self.dependencies})

    def assert_refused(self, message, error_type=ValueError):
        before = copy.deepcopy((self.runtime, self.objects))
        with self.assertRaises(error_type) as caught:
            self.A._capture_planner_runtime(P, self.runtime, self.objects)
        self.assertEqual(str(caught.exception), message)
        self.assertEqual((self.runtime, self.objects), before)

    def test_actual_runtime_is_captured_or_explicitly_refused(self):
        self.runtime = dict(files={}, observations={})
        for name in self.dependencies:
            try:
                resolved = Path(name).resolve(strict=True)
                metadata, raw = P.read_regular(resolved, P.RUNTIME_BOUNDS["file_bytes"], single_link=False)
            except (OSError, ValueError):
                # An unavailable or inadmissible physical dependency cannot
                # supply a captured entry; the helper must refuse the closure.
                continue
            key = self.A.digest(raw)
            self.objects[key] = raw
            self.runtime["files"][name] = dict(mode=0o555 if metadata["mode"] & 0o111 else 0o444, bytes=len(raw), sha256=key)
            self.runtime["observations"][name] = dict(resolved=str(resolved), identity=metadata["identity"], sha256=key)
        if set(self.runtime["files"]) != self.dependencies:
            self.assert_refused("unsupported Perl loader/library closure")
            return
        try:
            metadata, raw = P.read_regular(Path("/usr/bin/perl"), P.RUNTIME_BOUNDS["file_bytes"], single_link=False)
        except (OSError, ValueError) as error:
            self.assert_refused(str(error), type(error))
            return
        if self.A.digest(raw) != self.A._PLANNER_RUNTIME_PINS["/usr/bin/perl"] or metadata["mode"] != 0o755:
            self.assert_refused("unsupported captured Perl executable")
            return
        if any(self.runtime["files"][name]["sha256"] != self.A._PLANNER_RUNTIME_PINS[name] for name in self.dependencies):
            self.assert_refused("unsupported Perl loader/library closure")
            return

        # Only a real supported baseline can discriminate changed-object
        # refusal from an unrelated unsupported-host refusal.
        key = self.A._PLANNER_RUNTIME_PINS["/lib/x86_64-linux-gnu/libcrypt.so.1"]
        saved = self.objects[key]
        self.objects[key] = b"changed captured library"
        self.assert_refused("unsupported Perl loader/library closure")
        self.objects[key] = saved
        self.A._capture_planner_runtime(P, self.runtime, self.objects)
        value = self.runtime["files"]["/usr/bin/perl"]
        self.assertEqual(value["sha256"], self.A._PLANNER_RUNTIME_PINS["/usr/bin/perl"])
        self.assertEqual(self.objects[value["sha256"]], raw)
        self.assertEqual(self.runtime["planner_perl_closure"], self.A._PLANNER_RUNTIME_PINS)
        self.assertEqual(self.runtime["planner_perl_inputs"]["/dev/urandom"], "ABSENT_IN_FINITE_IMAGE_RUNTIME_BEHAVIOR_UNQUALIFIED")
        self.assertEqual(self.runtime["planner_perl_inputs"]["/proc/self/exe"], "ABSENT_IN_FINITE_IMAGE_RUNTIME_BEHAVIOR_UNQUALIFIED")
        self.assertNotIn("/dev/urandom", self.runtime["files"])
        self.assertNotIn("/proc/self/exe", self.runtime["files"])

    def test_missing_dependency_refuses_before_runtime_acquisition(self):
        self.runtime["files"].pop("/lib/x86_64-linux-gnu/libcrypt.so.1")
        with mock.patch.object(P, "read_regular", side_effect=AssertionError("missing dependency reached runtime acquisition")):
            self.assert_refused("unsupported Perl loader/library closure")

    def test_unknown_perl_bytes_refuse(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "unknown-perl"
            path.write_bytes(b"unknown Perl executable")
            path.chmod(0o755)
            observed = P.read_regular(path, P.RUNTIME_BOUNDS["file_bytes"], single_link=False)
            def replaced(requested, *args, **kwargs):
                self.assertEqual(requested, Path("/usr/bin/perl"))
                return observed
            with mock.patch.object(P, "read_regular", side_effect=replaced):
                self.assert_refused("unsupported captured Perl executable")

    def test_claimed_absence_cannot_hide_a_runtime_member(self):
        self.runtime["files"]["/dev/urandom"] = dict(mode=0o444, bytes=1, sha256="unqualified")
        with mock.patch.object(P, "read_regular", side_effect=AssertionError("optional input reached runtime acquisition")):
            self.assert_refused("unsupported Perl optional input in finite runtime")


if __name__ == "__main__":
    unittest.main()
