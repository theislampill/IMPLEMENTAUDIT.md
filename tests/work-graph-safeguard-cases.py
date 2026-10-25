#!/usr/bin/env python3
"""Complete original node83 input acquisition; no native or chain claim."""
import importlib.util
import json
import os
from pathlib import Path
import shutil
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]

_historical_spec = importlib.util.spec_from_file_location("historical_fixture", ROOT / "tests/work-graph-historical-fixture.py")
H = importlib.util.module_from_spec(_historical_spec)
_historical_spec.loader.exec_module(H)
spec = importlib.util.spec_from_file_location("safeguard_support", ROOT / "tests/work-graph-audit-spec-cases.py")
shared = importlib.util.module_from_spec(spec)
spec.loader.exec_module(shared)
Q, P = shared.Q, shared.P
PROFILE = "CONTROLLED_TASK_SAFEGUARD_RESTORATION_V1"
PROGRAM = "tests/safeguard-restoration.test.sh"


class CatalogCases(unittest.TestCase):
    def test_complete_original83_has_explicit_profile_and_public_mode(self):
        A, _ = shared.load("safeguard_catalog", ROOT / "scripts/qualify-work-graph-finite-leaf.py")
        try:
            contract = A.contract_for(PROFILE)
        except ValueError as error:
            self.fail("missing exact original83 profile: " + str(error))
        graph, scope, node = A.select_node(Q.WG, H.original("scripts/verify-package.sh"), P.ENVIRONMENT, profile=PROFILE)
        self.assertEqual((len(graph["nodes"]), node), (117, graph["nodes"][83]))
        self.assertEqual(node["source"], "bash " + PROGRAM + "\n")
        self.assertEqual(scope["nodes"], ["COMMAND:" + PROGRAM + ":0"])
        self.assertEqual(len(scope["omitted_nodes"]), 116)
        self.assertEqual(Q._FINITE_MODES["safeguard-restoration"], PROFILE)
        self.assertEqual(set(contract["programs"]), {PROGRAM, "scripts/check-safeguard-restoration.sh", "scripts/check-installed-payload-self-contained.sh"})
        self.assertEqual(contract["recursive"]["roots"], ("skills",))
        self.assertFalse(contract["recursive"]["optional"])


class SafeguardFixture(shared.ProfileFixture):
    PROFILE = PROFILE

    def setUp(self):
        super().setUp()
        shutil.copytree(ROOT / "skills", self.source / "skills", dirs_exist_ok=True)
        self.restore_historical_inputs()

    def session(self, name="evidence", **options):
        return self.source_admission_session(Q.create_finite_leaf_session(
            self.source, self.base / name, profile=self.profile, **options))

    def new_member(self, raw=b"ordinary added input\n", name=".added/.member"):
        path = self.source / "skills" / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
        return path


class AdmissionCases(SafeguardFixture, unittest.TestCase):
    def test_all_recursive_bytes_names_types_and_empty_directories_are_captured(self):
        path = self.new_member(b"\x00\xff\xfeopaque\n")
        (path.parent / ".empty").mkdir()
        state, stamps, objects = self.snapshot()
        expected = {p.relative_to(self.source).as_posix(): p.read_bytes() for p in (self.source / "skills").rglob("*") if p.is_file()}
        actual = {name: objects[row["sha256"]] for name, row in state["files"].items() if name.startswith("skills/")}
        self.assertEqual(actual, expected)
        self.assertIn("skills/.added/.empty", state["directories"])
        self.assertIn("recursive_inputs", stamps)
        self.assertFalse((self.source / ".git").exists())

    def test_unknown_called_program_or_registry_refuses_before_runtime(self):
        for number, name in enumerate((*self.A.contract_for(PROFILE)["programs"], "scripts/verify-package.sh")):
            path = self.source / name
            raw = path.read_bytes()
            path.write_bytes(raw + b"\n")
            session = self.session("changed-" + str(number))
            with self.subTest(path=name), self.assertRaisesRegex(ValueError, "executable|registry"):
                session.run()
            self.assertEqual(session.dispatch_count, 0)
            self.assertFalse((session.output / "objects").exists())
            path.write_bytes(raw)

    def test_each_literal_or_required_default_operand_absence_refuses(self):
        contract = self.A.contract_for(PROFILE)
        for name in (*contract["data"], *contract["recursive"]["required_members"]):
            path = self.source / name
            raw, mode = path.read_bytes(), path.stat().st_mode & 0o777
            path.unlink()
            with self.subTest(path=name), self.assertRaises((ValueError, OSError)):
                self.snapshot()
            path.write_bytes(raw)
            path.chmod(mode)

    def test_added_member_and_declared_missing_helper_remain_complete_source_inputs(self):
        before, _, _ = self.snapshot()
        path = self.new_member(b"bash scripts/check-added-source.sh\n", "added.md")
        added, _, _ = self.snapshot()
        self.assertNotEqual(before, added)
        path.unlink()
        owner = self.source / "skills/implementaudit/references/repo-state-comparison.md"
        owner.write_bytes(owner.read_bytes() + b"\nhelper-route: scripts/absent-owned-helper.sh|A|fixture|owner|boundary|evidence|scope\n")
        changed, _, _ = self.snapshot()
        self.assertNotEqual(changed, before)
        self.assertNotIn("skills/implementaudit/scripts/absent-owned-helper.sh", changed["files"])
        session = self.session()
        with self.assertRaisesRegex(AssertionError, "runtime acquisition"):
            session.run()
        self.assertEqual(session._issued, {})

    def test_alias_special_file_and_same_byte_member_replacement_are_not_hidden(self):
        path = self.new_member()
        outside = self.base / "outside"
        outside.write_bytes(b"outside")
        for kind in ("symlink", "hardlink", "fifo"):
            path.unlink()
            if kind == "symlink": path.symlink_to(outside)
            elif kind == "hardlink": os.link(outside, path)
            else: os.mkfifo(path)
            with self.subTest(kind=kind), self.assertRaises((ValueError, OSError)):
                self.snapshot()
            path.unlink()
            path.write_bytes(b"ordinary")
        before, _, _ = self.snapshot()
        raw = path.read_bytes()
        path.unlink()
        path.write_bytes(raw)
        after, _, _ = self.snapshot()
        self.assertNotEqual(before["recursive_inputs"], after["recursive_inputs"])

    def test_new_member_during_capture_refuses_closed_population(self):
        original, changed = P.snapshot_tree, False
        def raced(root, objects, bounds, **kwargs):
            nonlocal changed
            result = original(root, objects, bounds, **kwargs)
            if Path(root) == self.source / "skills" and not changed:
                changed = True
                self.new_member(b"late input\n")
            return result
        with mock.patch.object(P, "snapshot_tree", side_effect=raced), self.assertRaisesRegex(ValueError, "changed"):
            self.snapshot()

    def test_all_diagnostic_lines_including_non_lf_separators_are_reserved(self):
        before, _, _ = self.snapshot()
        value = before["recursive_inputs"]["resources"]["safeguard_possible_messages"]
        self.new_member(b"source repo only scripts/check-one.sh\rsource repo only scripts/check-two.sh\vsource repo only scripts/check-three.sh\n")
        after, _, _ = self.snapshot()
        self.assertEqual(after["recursive_inputs"]["resources"]["safeguard_possible_messages"] - value, 9)
        reservation = self.A.temporary_requirements(after, profile=PROFILE)
        self.assertEqual((reservation["files"], reservation["directories"]), (11, 1))
        self.assertLess(reservation["required_bytes"], 32 * 1024**2)
        self.A.require_resource_capacity(reservation, self.session().LIMITS)

    def test_large_diagnostics_refuse_original_scratch_or_stream_capacity(self):
        self.new_member(b"scripts/check-large.sh\n" * 30000, "x" * 180 + "/" + "y" * 180)
        state, _, _ = self.snapshot()
        reservation = self.A.temporary_requirements(state, profile=PROFILE)
        session = self.session()
        self.assertGreater(reservation["largest_file_bytes"], session.LIMITS["file_bytes"])
        with self.assertRaisesRegex(ValueError, "capacity"):
            session.run()
        self.assertEqual(session.dispatch_count, 0)
        self.assertFalse((session.output / "objects").exists())

    def test_valid_source_reaches_assertive_runtime_boundary_without_result(self):
        session = self.session()
        with self.assertRaisesRegex(AssertionError, "runtime acquisition"):
            session.run()
        self.assertEqual(session.dispatch_count, 0)
        self.assertEqual(session._issued, {})


class LiveCases(SafeguardFixture, shared.RetainedFixture, unittest.TestCase):
    LIVE_ENV = "R0035_FINITE_SAFEGUARD_LIVE"
    EVIDENCE_ENV = "R0035_FINITE_SAFEGUARD_EVIDENCE"
    OBJECTS_ENV = "R0035_FINITE_SAFEGUARD_OBJECTS"
    TEST_SOURCE = "tests/work-graph-safeguard-cases.py"

    def actual(self, session):
        self.assertFalse(self.SOURCE_ADMISSION_ONLY)
        result = session.run()
        directory = Path(result["evidence_directory"])
        stdout, stderr = ((directory / name).read_bytes() for name in ("stdout.log", "stderr.log"))
        receipt = json.loads((directory / "receipt.json").read_bytes())
        self.assertEqual(receipt["node"], "COMMAND:" + PROGRAM + ":0")
        self.assertEqual(result["group"]["nodes"], [receipt["node"]])
        self.assertEqual(len(result["group"]["omitted_nodes"]), 116)
        self.assertEqual((result["canonical_acceptance"], result["authority"]), ("UNQUALIFIED", "NONE"))
        return result, stdout, stderr

    def test_actual_original_positive_reuse_and_added_member_refusal(self):
        session = self.session()
        first, stdout, stderr = self.actual(session)
        expected = b"check-installed-payload-self-contained: ok\ncheck-safeguard-restoration: ok\nsafeguard-restoration.test: ok\n"
        self.assertEqual((first["exit"], first["complete"], stdout, stderr), (0, True, expected, b""))
        second, _, _ = self.actual(session)
        self.assertEqual((first["disposition"], second["disposition"], session.dispatch_count), ("EXECUTED", "REUSED", 1))
        self.assertEqual(first["receipt_digest"], second["receipt_digest"])
        self.new_member()
        with self.assertRaisesRegex(ValueError, "prior receipt refused"):
            session.run()
        self.assertEqual(session.dispatch_count, 1)

    def test_added_semantic_violation_fails_original_and_is_not_reused(self):
        self.new_member(b"bash scripts/check-unqualified-new-member.sh\n", "unqualified-added.md")
        session = self.session()
        result, _, stderr = self.actual(session)
        self.assertEqual((result["exit"], result["complete"]), (1, True))
        self.assertIn(b"unqualified-added.md:1: repo-only path reference without 'source repo' label", stderr)
        self.assertEqual(session._issued, {})
        with self.assertRaisesRegex(ValueError, "failed or interrupted"):
            session.run()
        self.assertEqual(session.dispatch_count, 1)


if __name__ == "__main__":
    unittest.main()
