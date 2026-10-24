#!/usr/bin/env python3
"""Exact original91 finite fanout source controls; no native dispatch authority."""
import ast
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("fanout_profile_support", ROOT / "tests/work-graph-audit-spec-cases.py")
shared = importlib.util.module_from_spec(spec)
spec.loader.exec_module(shared)
Q, P = shared.Q, shared.P
PROFILE = "CONTROLLED_TASK_FANOUT_COVERAGE_V1"


class CatalogCases(unittest.TestCase):
    def setUp(self):
        self.A, _ = shared.load("fanout_catalog", ROOT / "scripts/qualify-work-graph-finite-leaf.py")

    def test_exact_original_profile_is_explicitly_available(self):
        try:
            contract = self.A.contract_for(PROFILE)
        except ValueError:
            contract = None
        self.assertIsNotNone(contract, "missing exact original91 fanout-coverage profile")

    def test_original_mapping_and_complete_default_import_closure(self):
        graph, scope, node = self.A.select_node(Q.WG, (ROOT / self.A.REGISTRY).read_bytes(), P.ENVIRONMENT, profile=PROFILE)
        self.assertEqual((len(graph["nodes"]), node), (117, graph["nodes"][91]))
        self.assertEqual(node["source"], "bash tests/fanout-coverage-contract.test.sh\n")
        self.assertEqual((scope["nodes"], len(scope["omitted_nodes"])),
                         (["COMMAND:tests/fanout-coverage-contract.test.sh:0"], 116))
        self.assertEqual(Q._FINITE_MODES["fanout-coverage"], PROFILE)
        checker = (ROOT / "scripts/check-plan-quality-contract.sh").read_text()
        body = checker.split("<<'PY'\n", 1)[1].rsplit("\nPY", 1)[0]
        syntax = ast.parse(body)
        plan_paths = {node.value for node in ast.walk(syntax) if isinstance(node, ast.Constant)
                      and isinstance(node.value, str) and node.value.startswith(("skills/", "fixtures/"))
                      and node.value.endswith((".md", ".txt")) and " " not in node.value}
        defaults = set(re.findall(r'"(fixtures/[^"\n]+)"', checker.split('if [ "${#files[@]}" -eq 0 ]; then', 1)[1].split('\nfi', 1)[0]))
        self.assertEqual(defaults, {"fixtures/read-only-plans/valid-handoff-plan.md", "fixtures/e2e-mini-audit-loop/phase-1.md"})
        fanout = (ROOT / "scripts/check-fanout-coverage-contract.sh").read_text()
        original_paths = set(re.findall(r'"((?:skills|fixtures)/[^"\n]+\.md)"', fanout))
        recursive_paths = {name for name in original_paths if name.startswith("fixtures/child-agents/")}
        contract = self.A.contract_for(PROFILE)
        self.assertEqual(set(contract["recursive"]["required_members"]), recursive_paths)
        self.assertEqual(set(contract["data"]), (plan_paths | defaults | original_paths) - recursive_paths)
        self.assertEqual(len(self.A.source_paths(PROFILE)), 14)
        self.assertEqual(contract["recursive"]["roots"], ("fixtures/child-agents",))
        self.assertFalse(contract["recursive"]["optional"])
        self.assertEqual(contract["source_modes"], "PRESERVE_READ_ONLY_MOUNT")

    def test_whole_original_programs_glob_and_reset_sequence_are_retained(self):
        contract = self.A.contract_for(PROFILE)
        self.assertEqual(contract["programs"], {
            "tests/fanout-coverage-contract.test.sh": "1a3d5274e30d99d9f7e1f087086bf3c239228b2b890758736312253b7ca2c372",
            "scripts/check-fanout-coverage-contract.sh": "b3701a09bc7bdda184001e335f5762e5e57b1babc61ce733f91eb4fd3cd6c40b",
            "scripts/check-plan-quality-contract.sh": "f89b9ba3e6f7d9a003238b1efc398e3b78aba9a84a9e4fc19cab5dc81c70f8df"})
        wrapper = (ROOT / contract["program"]).read_text()
        self.assertIn('cp fixtures/child-agents/*.md "$tmp_root/fixtures/child-agents/"', wrapper)
        self.assertEqual(len(re.findall(r'^reset_sandbox$', wrapper, re.M)), 11)
        self.assertEqual({"bash", "dirname", "grep", "awk", "cat", "rm", "mktemp", "mkdir", "cp", "mv", "sed", "python3.12"} - set(P.TOOLS), set())


class FanoutFixture(shared.ProfileFixture):
    PROFILE = PROFILE

    def setUp(self):
        super().setUp()
        shutil.copytree(ROOT / "fixtures/child-agents", self.source / "fixtures/child-agents")

    def session(self, name="evidence", **options):
        return self.source_admission_session(Q.create_finite_leaf_session(
            self.source, self.base / name, profile=self.profile, **options))

    def new_member(self, name, data=b"complete newly observed data\n"):
        path = self.source / "fixtures/child-agents" / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        path.chmod(0o644)
        return path

    def semantic_mutation(self):
        self.new_member(".unexpected-command-mode.txt", b"Advertised mode: /implementaudit deep\n")
        return b"command-mode identity advertised in fanout surfaces"


class AdmissionCases(FanoutFixture, unittest.TestCase):
    def test_literal_inputs_full_tree_modes_and_every_required_operand(self):
        state, stamps, objects = self.snapshot()
        disk = {str(path.relative_to(self.source)) for path in self.source.rglob("*") if path.is_file()}
        self.assertEqual(set(state["files"]), disk)
        self.assertEqual(len(state["files"]), 28)
        self.assertIn("recursive_inputs", stamps)
        self.assertFalse((self.source / ".git").exists())
        for name, record in state["files"].items():
            self.assertEqual(objects[record["sha256"]], (self.source / name).read_bytes())
            self.assertEqual(record["mode"], (self.source / name).stat().st_mode & 0o777)
        contract = self.A.contract_for(PROFILE)
        for name in (*contract["data"], *contract["recursive"]["required_members"]):
            path = self.source / name
            raw, mode = path.read_bytes(), path.stat().st_mode & 0o777
            path.unlink()
            with self.subTest(missing=name), self.assertRaises((ValueError, OSError)):
                self.snapshot()
            path.write_bytes(raw)
            path.chmod(mode)

    def test_hidden_binary_nested_empty_and_glob_names_are_captured(self):
        before, _, _ = self.snapshot()
        self.new_member(".hidden.md", b"\x00\xff\xfe complete binary bytes\n")
        self.new_member("nested/unlisted.txt")
        visible = self.new_member("new-visible.md")
        empty = self.source / "fixtures/child-agents/empty"
        empty.mkdir()
        matching_directory = self.source / "fixtures/child-agents/directory.md"
        matching_directory.mkdir()
        state, _, objects = self.snapshot()
        self.assertNotEqual(before, state)
        self.assertIn(str(empty.relative_to(self.source)), state["directories"])
        self.assertIn(str(matching_directory.relative_to(self.source)), state["directories"])
        self.assertEqual(objects[state["files"]["fixtures/child-agents/.hidden.md"]["sha256"]], b"\x00\xff\xfe complete binary bytes\n")
        self.assertIn("fixtures/child-agents/nested/unlisted.txt", state["files"])
        reservation = self.A.temporary_requirements(state, profile=PROFILE)
        expected = sorted(str(path.relative_to(self.source)) for path in (self.source / "fixtures/child-agents").glob("*.md")
                          if path.is_file() and not path.name.startswith("."))
        self.assertEqual(reservation["glob_files"], expected)
        self.assertIn(str(visible.relative_to(self.source)), reservation["glob_files"])
        self.assertNotIn("fixtures/child-agents/.hidden.md", reservation["glob_files"])
        self.assertNotIn("fixtures/child-agents/directory.md", reservation["glob_files"])

    def test_changed_executables_and_registry_refuse_before_runtime(self):
        contract = self.A.contract_for(PROFILE)
        for number, name in enumerate((*contract["programs"], self.A.REGISTRY)):
            path = self.source / name
            raw = path.read_bytes()
            path.write_bytes(raw + b"\n")
            session = self.session("changed-" + str(number))
            with self.subTest(path=name), self.assertRaisesRegex(ValueError, "source|registry|executable"):
                session.run()
            self.assertEqual(session.dispatch_count, 0)
            self.assertFalse((session.output / "objects").exists())
            path.write_bytes(raw)

    def test_recursive_alias_special_file_mode_and_physical_root_alias_refuse(self):
        path = self.new_member("unlisted.md")
        outside = self.base / "outside"
        outside.write_bytes(path.read_bytes())
        path.unlink()
        path.symlink_to(outside)
        with self.assertRaises((ValueError, OSError)):
            self.snapshot()
        path.unlink()
        os.link(outside, path)
        with self.assertRaises((ValueError, OSError)):
            self.snapshot()
        path.unlink()
        os.mkfifo(path)
        with self.assertRaises((ValueError, OSError)):
            self.snapshot()
        path.unlink()
        path.write_bytes(outside.read_bytes())
        path.chmod(0o444)
        with self.assertRaisesRegex(ValueError, "mode"):
            self.snapshot()
        path.chmod(0o644)
        alias = self.base / "alias"
        alias.symlink_to(self.source, target_is_directory=True)
        with self.assertRaises((ValueError, OSError)):
            self.A.snapshot_source(P, alias, {}, profile=PROFILE)

    def test_default_plan_data_change_reaches_only_runtime_tripwire(self):
        before, _, _ = self.snapshot()
        path = self.source / "fixtures/read-only-plans/valid-handoff-plan.md"
        raw = path.read_bytes()
        self.assertIn(b"## Current state", raw)
        path.write_bytes(raw.replace(b"## Current state", b"## Removed current state"))
        after, _, _ = self.snapshot()
        self.assertNotEqual(before, after)
        session = self.session()
        with self.assertRaisesRegex(AssertionError, "runtime acquisition"):
            session.run()
        self.assertEqual((session.dispatch_count, session._issued), (0, {}))

    def test_unlisted_semantic_input_is_captured_without_preacceptance(self):
        before, _, _ = self.snapshot()
        self.semantic_mutation()
        after, _, objects = self.snapshot()
        self.assertNotEqual(before, after)
        key = after["files"]["fixtures/child-agents/.unexpected-command-mode.txt"]["sha256"]
        self.assertEqual(objects[key], b"Advertised mode: /implementaudit deep\n")
        session = self.session()
        with self.assertRaisesRegex(AssertionError, "runtime acquisition"):
            session.run()
        self.assertEqual((session.dispatch_count, session._issued), (0, {}))

    def test_copy_transform_diagnostics_spools_and_capacity_are_reserved(self):
        state, _, _ = self.snapshot()
        reservation = self.A.temporary_requirements(state, profile=PROFILE)
        self.assertEqual((reservation["copies"], reservation["files"], reservation["directories"]), (17, 25, 7))
        self.assertEqual(reservation["private_tree_incarnations"], 11)
        self.assertLess(reservation["required_bytes"], 32 * 1024**2)
        self.assertGreater(reservation["recursive_report_bound"], state["recursive_inputs"]["resources"]["all_lines_grep_report_bytes"])
        for label, limit in (("scratch", {"scratch_bytes": reservation["required_bytes"] - 1}),
                             ("stream", {"stream_bytes": reservation["max_stderr_bytes"] - 1}),
                             ("file", {"file_bytes": reservation["largest_file_bytes"] - 1})):
            session = self.session("capacity-" + label)
            session.LIMITS = dict(session.LIMITS, **limit)
            with self.subTest(limit=label), self.assertRaisesRegex(ValueError, "capacity"):
                session.run()
            self.assertEqual(session.dispatch_count, 0)

    def test_sed_growth_and_recursive_prefixed_output_are_bounded(self):
        state, _, _ = self.snapshot()
        before = self.A.temporary_requirements(state, profile=PROFILE)
        path = self.source / "fixtures/child-agents/exploratory-discrimination-cases.md"
        extra = b"Expected disposition: ALLOW\n" * 1000
        path.write_bytes(path.read_bytes() + extra)
        state, _, _ = self.snapshot()
        after = self.A.temporary_requirements(state, profile=PROFILE)
        self.assertGreaterEqual(after["content_bytes"] - before["content_bytes"], 4 * len(extra))
        self.new_member("deep/" + "x" * 180 + "/unlisted.bin", b"\n" * 40000)
        session = self.session("prefixed-output")
        with self.assertRaisesRegex(ValueError, "capacity"):
            session.run()
        self.assertEqual(session.dispatch_count, 0)

    def test_many_glob_matches_reserve_every_private_copy(self):
        for number in range(260):
            self.new_member("new-" + str(number) + ".md", b"")
        state, _, _ = self.snapshot()
        reservation = self.A.temporary_requirements(state, profile=PROFILE)
        self.assertEqual(reservation["copies"], 17 + 260)
        session = self.session()
        with self.assertRaisesRegex(ValueError, "capacity"):
            session.run()
        self.assertEqual(session.dispatch_count, 0)

    def test_literal_and_recursive_byte_bounds_and_imported_result_refuse(self):
        path = self.source / "skills/implementaudit/references/child-agents.md"
        raw = path.read_bytes()
        path.write_bytes(b"x" * (128 * 1024 + 1))
        with self.assertRaisesRegex(ValueError, "bound"):
            self.snapshot()
        path.write_bytes(raw)
        self.new_member("over-bound.bin", b"x" * (1024 * 1024 + 1))
        session = self.session()
        with self.assertRaisesRegex(ValueError, "bound"):
            session.run()
        self.assertEqual(session.dispatch_count, 0)
        with self.assertRaises(TypeError):
            session.run(receipt={"exit": 0}, command="dispatch child")


class LiveCases(FanoutFixture, shared.RetainedFixture, unittest.TestCase):
    LIVE_ENV = "R0035_FINITE_FANOUT_LIVE"
    EVIDENCE_ENV = "R0035_FINITE_FANOUT_EVIDENCE"
    OBJECTS_ENV = "R0035_FINITE_FANOUT_OBJECTS"
    TEST_SOURCE = "tests/work-graph-fanout-cases.py"

    def actual(self, session):
        self.assertFalse(self.SOURCE_ADMISSION_ONLY)
        result = session.run()
        directory = Path(result["evidence_directory"])
        stdout, stderr = ((directory / name).read_bytes() for name in ("stdout.log", "stderr.log"))
        receipt = json.loads((directory / "receipt.json").read_bytes())
        self.assertEqual(receipt["node"], "COMMAND:tests/fanout-coverage-contract.test.sh:0")
        self.assertEqual(result["group"]["nodes"], [receipt["node"]])
        self.assertEqual(len(result["group"]["omitted_nodes"]), 116)
        self.assertEqual((result["canonical_acceptance"], result["authority"]), ("UNQUALIFIED", "NONE"))
        return result, stdout, stderr

    def test_actual_original_positive_reuse_and_changed_population_refusal(self):
        session = self.session()
        first, stdout, stderr = self.actual(session)
        self.assertEqual((first["exit"], first["complete"], stdout, stderr),
                         (0, True, b"check-fanout-coverage-contract: ok\nfanout-coverage-contract.test: ok\n", b""))
        second, out2, err2 = self.actual(session)
        self.assertEqual((first["disposition"], second["disposition"], session.dispatch_count), ("EXECUTED", "REUSED", 1))
        self.assertEqual((first["receipt_digest"], stdout, stderr), (second["receipt_digest"], out2, err2))
        self.new_member("new-source-population.txt")
        with self.assertRaisesRegex(ValueError, "prior receipt refused"):
            session.run()
        self.assertEqual(session.dispatch_count, 1)

    def test_actual_original_semantic_failure_retained_and_not_reused(self):
        diagnostic = self.semantic_mutation()
        session = self.session()
        result, stdout, stderr = self.actual(session)
        self.assertEqual((result["exit"], result["complete"], stdout), (1, True, b""))
        self.assertIn(b"fixtures/child-agents/.unexpected-command-mode.txt:1:Advertised mode: /implementaudit deep", stderr)
        self.assertIn(diagnostic, stderr)
        self.assertEqual(session._issued, {})
        with self.assertRaisesRegex(ValueError, "failed or interrupted"):
            session.run()
        self.assertEqual(session.dispatch_count, 1)


if __name__ == "__main__":
    unittest.main()
