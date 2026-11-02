#!/usr/bin/env python3
"""Finite original70 acquisition; no native or canonical-route credit."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]

_historical_spec = importlib.util.spec_from_file_location("historical_fixture", ROOT / "tests/work-graph-historical-fixture.py")
H = importlib.util.module_from_spec(_historical_spec)
_historical_spec.loader.exec_module(H)
spec = importlib.util.spec_from_file_location("audit_routing_recursive", ROOT / "tests/work-graph-recursive-cases.py")
R = importlib.util.module_from_spec(spec)
spec.loader.exec_module(R)
PROFILE = "CONTROLLED_TASK_AUDIT_OBJECT_ROUTING_V1"
PROGRAM = "tests/audit-object-routing.test.sh"
R.MAPPING[PROFILE] = (70, PROGRAM)


class CatalogCases(unittest.TestCase):
    def test_original70_mapping_is_explicit_and_registry_bound(self):
        catalog, _ = R.shared.load("audit_routing_catalog", R.HELPER)
        registry = H.original("scripts/verify-package.sh")
        graph, scope, node = catalog.select_node(R.Q.WG, registry, R.P.ENVIRONMENT, profile=PROFILE)
        self.assertEqual(len(graph["nodes"]), 117)
        self.assertEqual(node, graph["nodes"][70])
        self.assertEqual(node["source"], "bash " + PROGRAM + "\n")
        self.assertEqual(scope["nodes"], ["COMMAND:" + PROGRAM + ":0"])
        self.assertEqual(len(scope["omitted_nodes"]), 116)
        with self.assertRaisesRegex(ValueError, "registry"):
            catalog.select_node(R.Q.WG, registry + b"\n", R.P.ENVIRONMENT, profile=PROFILE)


class Fixture(R.RecursiveFixture):
    PROFILE = PROFILE

    def session(self, name="evidence", **options):
        return self.source_admission_session(super().session(name, **options))


class AdmissionCases(Fixture, unittest.TestCase):
    def test_complete_three_trees_literal_reads_and_presence_inputs(self):
        added = self.source / "docs/portal/.hidden/.binary"
        added.parent.mkdir(parents=True)
        added.write_bytes(b"\x00\xff\ncomplete input bytes\n")
        (added.parent / ".empty").mkdir()
        state, _, objects = self.snapshot()
        contract = self.A.contract_for(PROFILE)
        expected = set(self.A.source_paths(PROFILE))
        for tree in ("skills", "docs/portal", "fixtures/audit-object-routing"):
            expected.update(p.relative_to(self.source).as_posix() for p in (self.source / tree).rglob("*") if p.is_file())
        self.assertEqual(set(state["files"]), expected)
        self.assertIn("docs/portal/.hidden/.empty", state["directories"])
        for name, record in state["files"].items():
            self.assertEqual(objects[record["sha256"]], (self.source / name).read_bytes())
        for name in ("fixtures/lean/brownfield-dmaic-release-repair.md",
                     "fixtures/semantic-preservation/cases.json",
                     "fixtures/semantic-preservation/evaluate.py",
                     "fixtures/semantic-preservation/test-cases.sh"):
            self.assertIn(name, contract["data"])
            self.assertNotIn(name, contract["programs"])

    def test_every_required_literal_and_positive_operand_absence_refuses(self):
        contract = self.A.contract_for(PROFILE)
        for name in (*contract["data"], *contract["recursive"]["required_members"]):
            path = self.source / name
            raw, mode = path.read_bytes(), path.stat().st_mode & 0o777
            path.unlink()
            with self.subTest(path=name), self.assertRaises((ValueError, OSError)):
                self.snapshot()
            path.write_bytes(raw)
            path.chmod(mode)

    def test_changed_program_or_registry_refuses_before_runtime_or_dispatch(self):
        for index, name in enumerate((*self.A.contract_for(PROFILE)["programs"], self.A.REGISTRY)):
            session = self.session("program-" + str(index))
            path = self.source / name
            raw = path.read_bytes()
            path.write_bytes(raw + b"\n")
            with self.subTest(path=name), self.assertRaisesRegex(ValueError, "registry|executable|source"):
                session.run()
            self.assertEqual(session.dispatch_count, 0)
            self.assertEqual(list(session.output.rglob("dispatch.json")), [])
            path.write_bytes(raw)

    def test_added_recursive_semantic_input_changes_acquisition_without_prejudging_result(self):
        first, _, _ = self.snapshot()
        path = self.source / "docs/portal/.mode-probe"
        path.write_bytes(b"/implementaudit quick\n")
        changed, _, objects = self.snapshot()
        self.assertNotEqual(first, changed)
        self.assertEqual(objects[changed["files"]["docs/portal/.mode-probe"]["sha256"]], path.read_bytes())

    def test_original_report_and_two_checker_spools_are_reserved(self):
        state, reservation = self.requirements()
        bound = state["recursive_inputs"]["resources"]
        self.assertEqual((reservation["files"], reservation["directories"]), (3, 0))
        self.assertEqual(reservation["report_file_bound"], bound["all_lines_grep_report_bytes"])
        self.assertEqual(reservation["checker_spool_bytes"], sum(
            state["files"][name]["bytes"] for name in ("scripts/check-routing.sh", "scripts/check-lean-discipline.sh")))
        self.A.require_resource_capacity(reservation, self.session().LIMITS)
        path = self.source / "docs/portal/.more-lines"
        path.write_bytes(b"x\ny")
        changed, enlarged = self.requirements()
        self.assertGreater(enlarged["report_file_bound"], reservation["report_file_bound"])
        self.assertGreater(enlarged["max_stderr_bytes"], reservation["max_stderr_bytes"])

    def test_prefixed_output_overflow_refuses_before_original_dispatch(self):
        path = self.source / "docs/portal" / ("x" * 180) / ("y" * 180)
        path.parent.mkdir()
        path.write_bytes(b"/implementaudit quick\n" * 45000)
        state, reservation = self.requirements()
        session = self.session()
        self.assertGreater(reservation["largest_file_bytes"], session.LIMITS["file_bytes"])
        with self.assertRaisesRegex(ValueError, "file/stream capacity|scratch capacity"):
            session.run()
        self.assertEqual(session.dispatch_count, 0)
        self.assertEqual(list(session.output.rglob("dispatch.json")), [])


class LiveCases(Fixture, R.RecursiveLiveFixture, unittest.TestCase):
    SOURCE_ADMISSION_ONLY = False

    @classmethod
    def setUpClass(cls):
        if os.environ.get("R0035_AUDIT_ROUTING_LIVE") != "1":
            raise unittest.SkipTest("set R0035_AUDIT_ROUTING_LIVE=1 under a receiving namespace allocation")

    def test_original_success_consumes_actual_receipt_without_redispatch(self):
        session = self.session()
        first, stdout, stderr = self.actual(session)
        self.assertEqual((first["exit"], first["complete"]), (0, True), stderr)
        self.assertEqual(stdout, b"check-routing: ok\ncheck-lean-discipline: ok\naudit-object-routing.test: ok\n")
        self.assertEqual(stderr, b"")
        second, _, _ = self.actual(session)
        self.assertEqual((first["disposition"], second["disposition"]), ("EXECUTED", "REUSED"))
        for field in ("key", "receipt_digest", "producer"):
            self.assertEqual(first[field], second[field])
        self.assertEqual(session.dispatch_count, 1)

    def test_actual_recursive_mode_violation_refuses_success_and_reuse(self):
        (self.source / "docs/portal/.mode-probe").write_bytes(b"/implementaudit quick\n")
        session = self.session()
        result, stdout, stderr = self.actual(session)
        self.assertEqual((result["exit"], result["complete"]), (1, True), stderr)
        self.assertEqual(stdout, b"check-routing: ok\ncheck-lean-discipline: ok\n")
        self.assertIn(b"audit-object-routing.test: non-native command mode advertised", stderr)
        self.assertIn(b"docs/portal/.mode-probe", stderr)
        self.assertEqual(session._issued, {})
        with self.assertRaisesRegex(ValueError, "failed or interrupted"):
            session.run()
        self.assertEqual(session.dispatch_count, 1)


if __name__ == "__main__":
    unittest.main()
