#!/usr/bin/env python3
"""Original registry-wrapper/marker-order controls on one finite owner."""
import importlib.util
import hashlib
import json
import os
from pathlib import Path
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]

_historical_spec = importlib.util.spec_from_file_location("historical_fixture", ROOT / "tests/work-graph-historical-fixture.py")
H = importlib.util.module_from_spec(_historical_spec)
_historical_spec.loader.exec_module(H)
HELPER = ROOT / "scripts/qualify-work-graph-finite-leaf.py"
REGISTRY_PROFILE = "CONTROLLED_TASK_REGISTRY_WRAPPER_V1"
MARKER_PROFILE = "CONTROLLED_TASK_MARKER_ORDER_V1"
CI = ".github/workflows/validate.yml"
REGISTRY_PROGRAM = "tests/validation-registry.test.sh"
MARKER_PROGRAM = "tests/marker-order.test.sh"


def load_support():
    import importlib.util
    path = ROOT / "tests/work-graph-audit-spec-cases.py"
    spec = importlib.util.spec_from_file_location("finite_batch_support", path)
    module = importlib.util.module_from_spec(spec)
    exec(compile(path.read_bytes(), str(path), "exec"), module.__dict__)
    return module


shared = load_support()
Q, P = shared.Q, shared.P


class SelectionCases(unittest.TestCase):
    def setUp(self):
        self.A, _ = shared.load("finite_batch_selection", HELPER)

    def select(self, profile, index, program):
        registry = H.original("scripts/verify-package.sh")
        graph, scope, node = self.A.select_node(Q.WG, registry, P.ENVIRONMENT, profile=profile)
        self.assertEqual(len(graph["nodes"]), 117)
        self.assertEqual(node, graph["nodes"][index])
        self.assertEqual(node["id"], "COMMAND:" + program + ":0")
        self.assertEqual(node["source"], "bash " + program + "\n")
        self.assertEqual(scope["profile"], profile)
        self.assertEqual(scope["nodes"], [node["id"]])
        self.assertEqual(len(scope["omitted_nodes"]), 116)

    def test_registry_profile_selects_exact_original_113(self):
        self.select(REGISTRY_PROFILE, 113, REGISTRY_PROGRAM)

    def test_marker_profile_selects_exact_original_45(self):
        self.select(MARKER_PROFILE, 45, MARKER_PROGRAM)


class RegistryFixture(shared.ProfileFixture):
    PROFILE = REGISTRY_PROFILE

    def setUp(self):
        super().setUp()
        # Acquire the actual current names through the established owner. Other
        # test contents are not inputs to the original checker and are not read.
        membership, _ = Q._registry_membership_snapshot_v1(ROOT)
        self.members = set(membership["entries"])
        for name in self.members:
            path = self.source / "tests" / name
            if not path.exists():
                path.write_bytes(b"")
                path.chmod(0o644)

    def snapshot(self):
        objects = {}
        state, stamps = self.A.snapshot_source(P, self.source, objects,
            profile=self.profile, registry_snapshot=Q._registry_membership_snapshot_v1)
        return state, stamps, objects


class RegistryAdmissionCases(RegistryFixture, unittest.TestCase):
    def test_raw_parent_traversal_refuses_before_evidence_creation(self):
        cls = self.A.bind_session(Q.VerifierTaskSession, Q.WG, Q.ROOT, self.helper, profile=self.profile)
        cases = ((self.source / ".." / "source", self.base / "refused-source", self.base / "refused-source"),
                 (self.source, self.base / "unused" / ".." / "refused-output", self.base / "refused-output"))
        for source, output, actual in cases:
            with self.subTest(source=str(source), output=str(output)):
                with self.assertRaisesRegex(ValueError, "parent traversal"):
                    cls(source, output)
                self.assertFalse(actual.exists())

    def test_registry_literal_reads_and_complete_names_do_not_read_other_contents(self):
        other = next(name for name in sorted(self.members) if "tests/" + name != REGISTRY_PROGRAM)
        sentinel = b"not read as an executable or source dependency\n" * 4096
        (self.source / "tests" / other).write_bytes(sentinel)
        with mock.patch.object(P, "read_regular", wraps=P.read_regular) as reads:
            state, stamps, objects = self.snapshot()
        expected = {"scripts/verify-package.sh", REGISTRY_PROGRAM,
                    "scripts/check-validation-registry.sh", CI}
        self.assertEqual(set(state["files"]), expected)
        self.assertEqual({str(call.args[0].relative_to(self.source)) for call in reads.call_args_list}, expected)
        membership = state["registry_membership"]
        self.assertEqual(set(membership["projection"]["entries"]), self.members)
        self.assertEqual(set(membership["currentness"]["members"]), self.members)
        self.assertIn("registry_membership", stamps)
        self.assertNotIn(hashlib.sha256(sentinel).hexdigest(), objects)
        wrapper = state["files"][REGISTRY_PROGRAM]
        self.assertEqual(objects[wrapper["sha256"]], (ROOT / REGISTRY_PROGRAM).read_bytes())

    def test_registry_addition_deletion_and_dot_names_are_observed(self):
        before, _, _ = self.snapshot()
        extra = self.source / "tests/.r0035-unregistered.test.sh"
        extra.write_bytes(b"contents are not read\n")
        after, _, _ = self.snapshot()
        self.assertIn(extra.name, after["registry_membership"]["projection"]["entries"])
        self.assertNotEqual(before, after)
        removable = next(name for name in sorted(self.members) if "tests/" + name != REGISTRY_PROGRAM)
        (self.source / "tests" / removable).unlink()
        removed, _, _ = self.snapshot()
        self.assertNotIn(removable, removed["registry_membership"]["projection"]["entries"])
        self.assertNotEqual(after, removed)

    def test_registry_matching_link_directory_and_fifo_refuse_before_dispatch(self):
        path = self.source / "tests/.r0035-unregistered.test.sh"
        for kind in ("symlink", "directory", "fifo"):
            if kind == "symlink":
                path.symlink_to(self.source / REGISTRY_PROGRAM)
            elif kind == "directory":
                path.mkdir()
            else:
                os.mkfifo(path)
            session = self.session("evidence-" + kind)
            with self.subTest(kind=kind), self.assertRaisesRegex(ValueError, "ordinary file"):
                session.run()
            self.assertEqual(session.dispatch_count, 0)
            self.assertEqual(list(session.output.rglob("dispatch.json")), [])
            if kind == "directory":
                path.rmdir()
            else:
                path.unlink()

    def test_registry_missing_ci_and_unknown_program_refuse(self):
        path = self.source / CI
        data = path.read_bytes()
        path.unlink()
        with self.assertRaises((ValueError, OSError)):
            self.snapshot()
        path.write_bytes(data)
        path.chmod(0o644)
        program = self.source / "scripts/check-validation-registry.sh"
        program.write_bytes(program.read_bytes() + b"\n")
        session = self.session()
        with self.assertRaisesRegex(ValueError, "executable"):
            session.run()
        self.assertEqual(session.dispatch_count, 0)

    def test_registry_ci_byte_bound_and_private_write_bound_refuse(self):
        path = self.source / CI
        original = path.read_bytes()
        path.write_bytes(b"x" * (64 * 1024 + 1))
        with self.assertRaisesRegex(ValueError, "bound"):
            self.snapshot()
        path.write_bytes(original)
        state, _, _ = self.snapshot()
        reservation = self.A.temporary_requirements(state, profile=self.profile)
        self.assertEqual((reservation["files"], reservation["directories"]), (14, 16))
        self.assertGreaterEqual(reservation["content_bytes"], 575)
        session = self.session()
        session.LIMITS = dict(session.LIMITS, scratch_bytes=reservation["required_bytes"] - 1)
        with self.assertRaisesRegex(ValueError, "scratch|temporary"):
            session.run()
        self.assertEqual(session.dispatch_count, 0)
        self.assertFalse((session.output / "objects").exists())


class MarkerAdmissionCases(shared.ProfileFixture, unittest.TestCase):
    PROFILE = MARKER_PROFILE

    def test_marker_closure_has_no_unreachable_default_fixtures(self):
        state, _, _ = self.snapshot()
        self.assertEqual(set(state["files"]), {"scripts/verify-package.sh", MARKER_PROGRAM,
                                               "scripts/check-marker-order.sh"})
        self.assertFalse((self.source / "fixtures").exists())
        self.assertNotIn("registry_membership", state)

    def test_marker_unknown_wrapper_and_checker_refuse_before_dispatch(self):
        for index, name in enumerate((MARKER_PROGRAM, "scripts/check-marker-order.sh")):
            path = self.source / name
            original = path.read_bytes()
            path.write_bytes(original + b"\n")
            session = self.session("evidence-" + str(index))
            with self.subTest(path=name), self.assertRaisesRegex(ValueError, "executable"):
                session.run()
            self.assertEqual(session.dispatch_count, 0)
            path.write_bytes(original)

    def test_marker_generated_temporary_files_have_a_prelaunch_capacity_gate(self):
        state, _, _ = self.snapshot()
        reservation = self.A.temporary_requirements(state, profile=self.profile)
        self.assertEqual((reservation["files"], reservation["directories"]), (13, 1))
        self.assertGreaterEqual(reservation["content_bytes"], 1247)
        session = self.session()
        session.LIMITS = dict(session.LIMITS, scratch_bytes=reservation["required_bytes"] - 1)
        with self.assertRaisesRegex(ValueError, "scratch|temporary"):
            session.run()
        self.assertEqual(session.dispatch_count, 0)
        self.assertFalse((session.output / "objects").exists())


class BatchLiveFixture(shared.RetainedFixture):
    LIVE_ENV = "R0035_FINITE_BATCH_LIVE"
    EVIDENCE_ENV = "R0035_FINITE_BATCH_EVIDENCE"
    OBJECTS_ENV = "R0035_FINITE_BATCH_OBJECTS"
    TEST_SOURCE = "tests/work-graph-finite-batch-cases.py"

    def run_original(self, session, program):
        result = session.run()
        directory = Path(result["evidence_directory"])
        stdout, stderr = ((directory / name).read_bytes() for name in ("stdout.log", "stderr.log"))
        self.assertEqual((directory / "exit-code.txt").read_bytes(), (str(result["exit"]) + "\n").encode())
        receipt = json.loads((directory / "receipt.json").read_bytes())
        self.assertEqual(receipt["node"], "COMMAND:" + program + ":0")
        self.assertEqual(receipt["scope"], self.profile)
        self.assertEqual(result["group"]["nodes"], [receipt["node"]])
        self.assertEqual(len(result["group"]["omitted_nodes"]), 116)
        return result, stdout, stderr


class RegistryLiveCases(RegistryFixture, BatchLiveFixture, unittest.TestCase):
    def test_registry_actual_positive_internal_cases_reuse_and_stale_membership(self):
        session = self.session()
        first, stdout, stderr = self.run_original(session, REGISTRY_PROGRAM)
        self.assertEqual(first["exit"], 0, stderr)
        self.assertEqual(stderr, b"")
        self.assertEqual(stdout, ("check-validation-registry: ok (%d tests; one canonical CI route)\n" % len(self.members)).encode() +
                         b"check-validation-registry: ok (3 tests; one canonical CI route)\nvalidation-registry.test: ok\n")
        image = json.loads((Path(first["evidence_directory"]) / "image.json").read_bytes())
        members = {item["path"]: item for item in image["files"]}
        wrapper = members["/work/" + REGISTRY_PROGRAM]
        self.assertEqual(wrapper["sha256"], hashlib.sha256((ROOT / REGISTRY_PROGRAM).read_bytes()).hexdigest())
        self.assertGreater(wrapper["bytes"], 0)
        for name in self.members:
            if "tests/" + name != REGISTRY_PROGRAM:
                self.assertEqual(members["/work/tests/" + name]["bytes"], 0)
        self.assertEqual(set(image["directory_membership"]["entries"]), self.members)
        self.assertIn("/work/scripts/verify-package.sh", members)
        second, _, _ = self.run_original(session, REGISTRY_PROGRAM)
        self.assertEqual((first["disposition"], second["disposition"]), ("EXECUTED", "REUSED"))
        self.assertEqual(first["receipt_digest"], second["receipt_digest"])
        (self.source / "tests/.r0035-stale.test.sh").write_bytes(b"")
        with self.assertRaisesRegex(ValueError, "prior receipt refused"):
            session.run()
        self.assertEqual(session.dispatch_count, 1)

    def test_registry_actual_hidden_unregistered_member_failure_is_not_reusable(self):
        name = ".r0035-unregistered.test.sh"
        (self.source / "tests" / name).write_bytes(b"candidate contents never read\n")
        session = self.session()
        result, stdout, stderr = self.run_original(session, REGISTRY_PROGRAM)
        self.assertEqual(result["exit"], 1, stderr)
        self.assertEqual(stdout, b"")
        self.assertEqual(stderr, ("tests/" + name + " is not invoked by scripts/verify-package.sh\n").encode())
        self.assertEqual(session._issued, {})
        with self.assertRaisesRegex(ValueError, "failed or interrupted"):
            session.run()
        self.assertEqual(session.dispatch_count, 1)

    def test_registry_actual_missing_ci_route_failure(self):
        (self.source / CI).write_bytes(b"true\n")
        session = self.session()
        result, stdout, stderr = self.run_original(session, REGISTRY_PROGRAM)
        self.assertEqual(result["exit"], 1, stderr)
        self.assertEqual(stdout, b"")
        self.assertEqual(stderr, b".github/workflows/validate.yml must invoke scripts/verify-package.sh exactly once\n")
        self.assertEqual(session._issued, {})


class MarkerLiveCases(BatchLiveFixture, unittest.TestCase):
    PROFILE = MARKER_PROFILE

    def test_marker_actual_original_three_positive_ten_negative_cases_and_reuse(self):
        self.assertFalse((self.source / "fixtures").exists())
        session = self.session()
        first, stdout, stderr = self.run_original(session, MARKER_PROGRAM)
        self.assertEqual(first["exit"], 0, stderr)
        self.assertEqual(stderr, b"")
        self.assertEqual(stdout, b"check-marker-order: ok\n" * 3 + b"marker-order.test: ok\n")
        image = json.loads((Path(first["evidence_directory"]) / "image.json").read_bytes())
        self.assertEqual({item["path"] for item in image["files"] if item["path"].startswith("/work/")},
                         {"/work/" + MARKER_PROGRAM, "/work/scripts/check-marker-order.sh",
                          "/work/scripts/run-work-graph-verifier.sh"})
        second, _, _ = self.run_original(session, MARKER_PROGRAM)
        self.assertEqual((first["disposition"], second["disposition"]), ("EXECUTED", "REUSED"))
        self.assertEqual(first["receipt_digest"], second["receipt_digest"])
        path = self.source / "scripts/check-marker-order.sh"
        path.write_bytes(path.read_bytes() + b"\n")
        with self.assertRaisesRegex(ValueError, "executable"):
            session.run()
        self.assertEqual(session.dispatch_count, 1)


if __name__ == "__main__":
    unittest.main()
