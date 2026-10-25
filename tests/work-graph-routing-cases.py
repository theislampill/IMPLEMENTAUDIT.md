#!/usr/bin/env python3
"""Exact repaired original54 acquisition controls; no native authority."""
import ast
import importlib.util
import json
import os
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("routing_profile_support", ROOT / "tests/work-graph-audit-spec-cases.py")
shared = importlib.util.module_from_spec(spec)
spec.loader.exec_module(shared)
Q, P = shared.Q, shared.P
PROFILE = "CONTROLLED_TASK_ROUTING_V1"


class CatalogCases(unittest.TestCase):
    def setUp(self):
        self.A, _ = shared.load("routing_catalog", ROOT / "scripts/qualify-work-graph-finite-leaf.py")

    def test_exact_repaired_original_profile_is_explicitly_available(self):
        try:
            contract = self.A.contract_for(PROFILE)
        except ValueError:
            contract = None
        self.assertIsNotNone(contract, "missing exact original54 routing profile")

    def test_original_mapping_and_literal_read_copy_closure(self):
        graph, scope, node = self.A.select_node(Q.WG, (ROOT / self.A.REGISTRY).read_bytes(), P.ENVIRONMENT, profile=PROFILE)
        self.assertEqual((len(graph["nodes"]), node), (117, graph["nodes"][54]))
        self.assertEqual(node["source"], "bash tests/routing.test.sh\n")
        self.assertEqual((scope["nodes"], len(scope["omitted_nodes"])), (["COMMAND:tests/routing.test.sh:0"], 116))
        self.assertEqual(Q._FINITE_MODES["routing"], PROFILE)
        wrapper = (ROOT / "tests/routing.test.sh").read_text()
        copied = set(re.findall(r"^cp ([^\s$]+) ", wrapper, re.M))
        self.assertEqual(len(copied), 20)
        self.assertEqual(set(self.A.source_paths(PROFILE)), copied | {self.A.REGISTRY, "tests/routing.test.sh"})
        checker = (ROOT / "scripts/check-routing.sh").read_text().split("<<'PY'\n", 1)[1].rsplit("\nPY", 1)[0]
        syntax = ast.parse(checker)
        paths = {part.value for part in ast.walk(syntax) if isinstance(part, ast.Constant)
                 and isinstance(part.value, str) and part.value.endswith(".md")}
        self.assertEqual(paths, copied - {"scripts/check-routing.sh"})
        scan = next(part.value for part in syntax.body if isinstance(part, ast.Assign)
                    and any(isinstance(target, ast.Name) and target.id == "scan_paths" for target in part.targets))
        self.assertEqual(set(ast.literal_eval(scan)), set(self.A.ROUTING_SCAN_INPUTS))

    def test_repaired_wrapper_whole_program_pin_and_copy_mode_are_preserved(self):
        contract = self.A.contract_for(PROFILE)
        self.assertEqual(contract["programs"]["tests/routing.test.sh"],
                         "77fdce7b44d893f4aa820c9ee913b1ffed37c976dc04a16a7a4c667eaf2ff2af")
        self.assertEqual(contract["programs"]["scripts/check-routing.sh"],
                         "6bddc813e29f13e63ac0f88474fd32418c38bef4110360a2ae6a451a69e36974")
        self.assertEqual(contract["source_modes"], "PRESERVE_READ_ONLY_MOUNT")
        self.assertEqual({"bash", "dirname", "mktemp", "rm", "mkdir", "cp", "cat", "wc", "python3.12"} - set(P.TOOLS), set())


class RoutingFixture(shared.ProfileFixture):
    PROFILE = PROFILE

    def session(self, name="evidence", **options):
        return self.source_admission_session(Q.create_finite_leaf_session(
            self.source, self.base / name, profile=self.profile, **options))

    def semantic_mutation(self):
        path = self.source / "skills/implementaudit/references/routing.md"
        raw = path.read_bytes()
        self.assertIn(b"Greenfield audit-governed work", raw)
        path.write_bytes(raw.replace(b"Greenfield audit-governed work", b"Removed greenfield definition"))
        return b"skills/implementaudit/references/routing.md: missing routing definition: greenfield audit-governed work"


class AdmissionCases(RoutingFixture, unittest.TestCase):
    def test_all_source_bytes_modes_and_missing_operands_are_closed(self):
        state, stamps, objects = self.snapshot()
        self.assertEqual(len(state["files"]), 22)
        self.assertNotIn("recursive_inputs", state)
        self.assertFalse((self.source / ".git").exists())
        for name, record in state["files"].items():
            path = self.source / name
            self.assertEqual(objects[record["sha256"]], path.read_bytes())
            self.assertEqual(record["mode"], path.stat().st_mode & 0o777)
            self.assertIn(name, stamps)
        for name in self.A.contract_for(PROFILE)["data"]:
            path = self.source / name
            raw, mode = path.read_bytes(), path.stat().st_mode & 0o777
            path.unlink()
            with self.subTest(missing=name), self.assertRaises((ValueError, OSError)):
                self.snapshot()
            path.write_bytes(raw)
            path.chmod(mode)

    def test_changed_program_registry_and_unknown_source_modes_refuse_before_runtime(self):
        for number, name in enumerate((*self.A.contract_for(PROFILE)["programs"], self.A.REGISTRY)):
            path = self.source / name
            raw = path.read_bytes()
            path.write_bytes(raw + b"\n")
            session = self.session("changed-" + str(number))
            with self.subTest(path=name), self.assertRaisesRegex(ValueError, "source|registry|executable"):
                session.run()
            self.assertEqual(session.dispatch_count, 0)
            self.assertFalse((session.output / "objects").exists())
            path.write_bytes(raw)
        path = self.source / "README.md"
        path.chmod(0o444)
        with self.assertRaisesRegex(ValueError, "mode"):
            self.snapshot()

    def test_file_and_physical_ancestor_aliases_refuse(self):
        path = self.source / "README.md"
        raw = path.read_bytes()
        outside = self.base / "outside"
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
        alias = self.base / "alias"
        alias.symlink_to(self.source, target_is_directory=True)
        with self.assertRaises((ValueError, OSError)):
            self.A.snapshot_source(P, alias, {}, profile=PROFILE)

    def test_semantic_data_is_captured_without_an_acceptance_shortcut(self):
        before, _, _ = self.snapshot()
        self.semantic_mutation()
        after, _, _ = self.snapshot()
        self.assertNotEqual(before, after)
        session = self.session()
        with self.assertRaisesRegex(AssertionError, "runtime acquisition"):
            session.run()
        self.assertEqual((session.dispatch_count, session._issued), (0, {}))

    def test_copy_diagnostics_spools_and_capacity_are_reserved(self):
        state, _, _ = self.snapshot()
        reservation = self.A.temporary_requirements(state, profile=PROFILE)
        self.assertEqual((reservation["copies"], reservation["files"], reservation["directories"]), (20, 29, 15))
        self.assertGreater(reservation["diagnostic_file_bound"], 4 * 1024**2)
        self.assertLess(reservation["required_bytes"], 32 * 1024**2)
        for label, limit in (("scratch", {"scratch_bytes": reservation["required_bytes"] - 1}),
                             ("stream", {"stream_bytes": reservation["max_stderr_bytes"] - 1}),
                             ("file", {"file_bytes": reservation["largest_file_bytes"] - 1})):
            session = self.session("capacity-" + label)
            session.LIMITS = dict(session.LIMITS, **limit)
            with self.subTest(limit=label), self.assertRaisesRegex(ValueError, "capacity"):
                session.run()
            self.assertEqual(session.dispatch_count, 0)

    def test_line_amplification_and_decoder_inputs_are_accounted_without_semantic_filtering(self):
        before, _, _ = self.snapshot()
        path = self.source / "README.md"
        raw = path.read_bytes()
        path.write_bytes(raw + b"\n" * 10000)
        after, _, _ = self.snapshot()
        growth = after["routing_resources"]["diagnostic_file_bound"] - before["routing_resources"]["diagnostic_file_bound"]
        self.assertGreaterEqual(growth, 10000 * 8 * (len("README.md") + 32 + 128))
        session = self.session("amplified")
        with self.assertRaisesRegex(ValueError, "capacity"):
            session.run()
        self.assertEqual(session.dispatch_count, 0)
        path.write_bytes(b"\xff invalid utf8\n")
        state, _, objects = self.snapshot()
        self.assertEqual(objects[state["files"]["README.md"]["sha256"]], path.read_bytes())
        self.assertGreaterEqual(state["routing_resources"]["diagnostic_file_bound"], 65536)

    def test_oversized_source_and_imported_result_refuse(self):
        (self.source / "README.md").write_bytes(b"x" * (128 * 1024 + 1))
        session = self.session()
        with self.assertRaisesRegex(ValueError, "bound"):
            session.run()
        self.assertEqual(session.dispatch_count, 0)
        with self.assertRaises(TypeError):
            session.run(receipt={"exit": 0}, command="bash other.sh")


class LiveCases(RoutingFixture, shared.RetainedFixture, unittest.TestCase):
    LIVE_ENV = "R0035_FINITE_ROUTING_LIVE"
    EVIDENCE_ENV = "R0035_FINITE_ROUTING_EVIDENCE"
    OBJECTS_ENV = "R0035_FINITE_ROUTING_OBJECTS"
    TEST_SOURCE = "tests/work-graph-routing-cases.py"

    def actual(self, session):
        self.assertFalse(self.SOURCE_ADMISSION_ONLY)
        result = session.run()
        directory = Path(result["evidence_directory"])
        stdout, stderr = ((directory / name).read_bytes() for name in ("stdout.log", "stderr.log"))
        receipt = json.loads((directory / "receipt.json").read_bytes())
        self.assertEqual(receipt["node"], "COMMAND:tests/routing.test.sh:0")
        self.assertEqual(result["group"]["nodes"], [receipt["node"]])
        self.assertEqual(len(result["group"]["omitted_nodes"]), 116)
        self.assertEqual((result["canonical_acceptance"], result["authority"]), ("UNQUALIFIED", "NONE"))
        return result, stdout, stderr

    def test_actual_original_positive_reuse_and_changed_input_refusal(self):
        session = self.session()
        first, stdout, stderr = self.actual(session)
        self.assertEqual((first["exit"], first["complete"], stdout, stderr),
                         (0, True, b"check-routing: ok\nrouting.test: ok\n", b""))
        second, out2, err2 = self.actual(session)
        self.assertEqual((first["disposition"], second["disposition"], session.dispatch_count), ("EXECUTED", "REUSED", 1))
        self.assertEqual((first["receipt_digest"], stdout, stderr), (second["receipt_digest"], out2, err2))
        self.semantic_mutation()
        with self.assertRaisesRegex(ValueError, "prior receipt refused"):
            session.run()
        self.assertEqual(session.dispatch_count, 1)

    def test_actual_original_semantic_failure_retained_and_not_reused(self):
        diagnostic = self.semantic_mutation()
        session = self.session()
        result, stdout, stderr = self.actual(session)
        self.assertEqual((result["exit"], result["complete"], stdout), (1, True, b""))
        self.assertEqual(stderr, diagnostic + b"\n")
        self.assertEqual(session._issued, {})
        with self.assertRaisesRegex(ValueError, "failed or interrupted"):
            session.run()
        self.assertEqual(session.dispatch_count, 1)


if __name__ == "__main__":
    unittest.main()
