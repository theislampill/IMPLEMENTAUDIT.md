#!/usr/bin/env python3
"""Finite source controls for exact original86; live controls require root allocation."""
import ast
import importlib.util
import json
import os
from pathlib import Path
import shutil
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("layout_profile_support", ROOT / "tests/work-graph-audit-spec-cases.py")
shared = importlib.util.module_from_spec(spec)
spec.loader.exec_module(shared)
Q, P = shared.Q, shared.P
PROFILE = "CONTROLLED_TASK_SKILL_LAYOUT_V1"


class CatalogCases(unittest.TestCase):
    def test_exact_original_profile_is_explicitly_available(self):
        helper, _ = shared.load("layout_catalog", ROOT / "scripts/qualify-work-graph-finite-leaf.py")
        try:
            contract = helper.contract_for(PROFILE)
        except ValueError:
            contract = None
        self.assertIsNotNone(contract, "missing exact original86 skill-layout profile")

    def test_exact_mapping_whole_programs_and_complete_scan_roots(self):
        helper, _ = shared.load("layout_catalog", ROOT / "scripts/qualify-work-graph-finite-leaf.py")
        graph, scope, node = helper.select_node(Q.WG, (ROOT / helper.REGISTRY).read_bytes(), P.ENVIRONMENT, profile=PROFILE)
        self.assertEqual((len(graph["nodes"]), node), (117, graph["nodes"][86]))
        self.assertEqual(node["source"], "bash tests/skill-layout-contract.test.sh\n")
        self.assertEqual((scope["nodes"], len(scope["omitted_nodes"])), ([node["id"]], 116))
        self.assertEqual(Q._FINITE_MODES["skill-layout"], PROFILE)
        contract = helper.contract_for(PROFILE)
        self.assertEqual(contract["programs"], {
            "tests/skill-layout-contract.test.sh": "1139d5406839aec5ebdfd82eb0ad63ec9f3c5404cabf3a6c377af0db4a546a7e",
            "scripts/check-skill-layout-contract.sh": "b73e014aa4727d064108515fd959f1d9efb799b2afa1d02f0e7677bd51d02988",
            "scripts/run-work-graph-verifier.sh": "345f51885abbeeda2e4ecd0de503febe50f30f853630a44c0c1277f414c1f9ae"})
        checker = (ROOT / "scripts/check-skill-layout-contract.sh").read_text()
        body = checker.split("<<'PY'\n", 1)[1].split("\nPY\n", 1)[0]
        syntax = ast.parse(body)
        active = next(ast.literal_eval(n.value) for n in syntax.body if isinstance(n, ast.Assign)
                      and any(isinstance(t, ast.Name) and t.id == "active_roots" for t in n.targets))
        self.assertEqual(set(active), {".claude-plugin", ".github", "scripts", "tests", "docs/portal", "README.md", "AGENTS.md", "CONTRIBUTING.md"})
        self.assertEqual(set(contract["recursive"]["roots"]), set(active) - {"README.md", "AGENTS.md", "CONTRIBUTING.md"} | {"skills"})
        self.assertEqual(set(contract["recursive"]["optional_files"]), {"CONTRIBUTING.md", ".git"})
        self.assertEqual(set(contract["data"]), {"README.md", "AGENTS.md", ".codex-plugin/plugin.json"})


class LayoutFixture(shared.ProfileFixture):
    PROFILE = PROFILE

    def setUp(self):
        super().setUp()
        # This is a complete physical no-Git source population. Do not relabel
        # a Git checkout or import a Git answer into this eligible branch.
        for name in ("skills", ".claude-plugin", ".github", "scripts", "tests", "docs/portal"):
            if (ROOT / name).exists():
                shutil.copytree(ROOT / name, self.source / name, dirs_exist_ok=True)
        if (ROOT / "CONTRIBUTING.md").exists():
            shutil.copyfile(ROOT / "CONTRIBUTING.md", self.source / "CONTRIBUTING.md")
        self.assertFalse((self.source / ".git").exists())

    def session(self, name="evidence", **options):
        return self.source_admission_session(Q.create_finite_leaf_session(
            self.source, self.base / name, profile=PROFILE, **options))

    def member(self, name, raw=b"new source input\n"):
        path = self.source / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
        path.chmod(0o644)
        return path

    def semantic_mutation(self):
        self.member("skills/audit-state/.unexpected-substrate.txt")
        return b"skills/audit-state must not duplicate shared substrate: skills/audit-state/.unexpected-substrate.txt"


class AdmissionCases(LayoutFixture, unittest.TestCase):
    def test_complete_actual_bytes_modes_population_and_image_subject(self):
        state, _, objects = self.snapshot()
        self.assertEqual(set(state["files"]), {str(p.relative_to(self.source)) for p in self.source.rglob("*") if p.is_file()})
        for name, row in state["files"].items():
            self.assertEqual(objects[row["sha256"]], (self.source / name).read_bytes())
            self.assertEqual(row["mode"], (self.source / name).stat().st_mode & 0o777)
        subject = self.A.image_subject(state, profile=PROFILE)
        self.assertEqual(subject, state["files"])
        self.assertIn(self.A.REGISTRY, subject)
        self.assertIn(self.A.RUNNER, subject)
        self.assertNotIn(self.A.REGISTRY, self.A.image_subject(state, profile=self.A.PROFILE))
        self.assertIn(self.A.REGISTRY, self.A.image_subject(state, profile=self.A.REGISTRY_PROFILE))

    def test_every_required_operand_refuses_if_missing(self):
        contract = self.A.contract_for(PROFILE)
        for name in (*contract["data"], *contract["recursive"]["required_members"]):
            path = self.source / name
            raw, mode = path.read_bytes(), path.stat().st_mode & 0o777
            path.unlink()
            with self.subTest(name=name), self.assertRaises((ValueError, OSError)):
                self.snapshot()
            path.write_bytes(raw)
            path.chmod(mode)

    def test_optional_absence_is_recorded_without_fabricated_members(self):
        for name in (".github", "docs/portal", "CONTRIBUTING.md"):
            path = self.source / name
            path.rename(self.base / ("absent-" + path.name))
        state, _, _ = self.snapshot()
        probes = state["recursive_inputs"]["projection"]["probes"]
        for name in (".github", "docs/portal", "CONTRIBUTING.md", ".git"):
            self.assertEqual(probes[name]["kind"], "MISSING")
            self.assertNotIn(name, state["directories"])
            self.assertNotIn(name, state["files"])
        with self.assertRaisesRegex(AssertionError, "runtime acquisition"):
            self.session().run()

    def test_present_git_directory_file_and_alias_refuse_before_runtime(self):
        path = self.source / ".git"
        for index, kind in enumerate(("file", "directory", "alias")):
            if kind == "file":
                path.write_bytes(b"gitdir: /outside/acquisition\n")
            elif kind == "directory":
                path.mkdir()
            else:
                path.symlink_to(self.base / "absent-git")
            session = self.session("present-git-" + str(index))
            with self.subTest(kind=kind), self.assertRaises((ValueError, OSError)):
                session.run()
            self.assertEqual((session.dispatch_count, session._issued), (0, {}))
            self.assertFalse((session.output / "objects").exists())
            path.rmdir() if kind == "directory" else path.unlink()

    def test_hidden_binary_nested_empty_directory_and_extra_skill_are_captured(self):
        members = {
            "scripts/.hidden.bin": b"\xff\x00\r\n",
            "tests/nested/new-source.txt": b"arbitrary source data\n",
            "skills/invented-child/SKILL.md": b"extra physical skill\n",
        }
        for name, raw in members.items():
            self.member(name, raw)
        (self.source / "skills/audit-state/empty").mkdir()
        state, _, objects = self.snapshot()
        for name, raw in members.items():
            self.assertEqual(objects[state["files"][name]["sha256"]], raw)
        self.assertIn("skills/audit-state/empty", state["directories"])

    def test_whole_program_registry_and_engine_runner_drift_refuse(self):
        for index, name in enumerate((*self.A.contract_for(PROFILE)["programs"], self.A.REGISTRY)):
            path = self.source / name; raw = path.read_bytes()
            path.write_bytes(raw + b"\n")
            session = self.session("changed-" + str(index))
            with self.subTest(name=name), self.assertRaisesRegex(ValueError, "executable|source|registry"):
                session.run()
            self.assertEqual(session.dispatch_count, 0)
            path.write_bytes(raw)

    def test_alias_special_file_mode_and_physical_root_alias_refuse(self):
        target = self.member("tests/new-member.txt")
        outside = self.base / "outside"; outside.write_bytes(b"outside\n")
        target.unlink(); target.symlink_to(outside)
        with self.assertRaises((ValueError, OSError)): self.snapshot()
        target.unlink(); os.link(outside, target)
        with self.assertRaises((ValueError, OSError)): self.snapshot()
        target.unlink(); os.mkfifo(target)
        with self.assertRaises((ValueError, OSError)): self.snapshot()
        target.unlink(); target.write_bytes(b"ordinary\n"); target.chmod(0o444)
        with self.assertRaisesRegex(ValueError, "mode"): self.snapshot()
        target.chmod(0o644)
        alias = self.base / "source-alias"; alias.symlink_to(self.source, target_is_directory=True)
        with self.assertRaises((ValueError, OSError)):
            self.A.snapshot_source(P, alias, {}, profile=PROFILE)

    def test_semantic_data_change_reaches_runtime_without_preacceptance(self):
        original, _, _ = self.snapshot()
        self.semantic_mutation()
        changed, _, _ = self.snapshot()
        self.assertNotEqual(original, changed)
        session = self.session()
        with self.assertRaisesRegex(AssertionError, "runtime acquisition"): session.run()
        self.assertEqual((session.dispatch_count, session._issued), (0, {}))

    def test_nine_retained_trees_private_writes_and_capacity_are_reserved(self):
        state, _, _ = self.snapshot()
        reservation = self.A.temporary_requirements(state, profile=PROFILE)
        self.assertEqual((reservation["copies"], reservation["files"], reservation["directories"]), (10, 120, 137))
        self.assertEqual(reservation["private_fixture_trees"], 9)
        self.assertEqual(reservation["generated_private_files"], 109)
        self.assertLess(reservation["required_bytes"], 32 * 1024**2)
        self.assertLess(reservation["max_stderr_bytes"], 16 * 1024**2)
        for label, limit in (("scratch", {"scratch_bytes": reservation["required_bytes"] - 1}),
                             ("stream", {"stream_bytes": reservation["max_stderr_bytes"] - 1}),
                             ("file", {"file_bytes": reservation["largest_file_bytes"] - 1})):
            session = self.session("capacity-" + label)
            session.LIMITS = dict(session.LIMITS, **limit)
            with self.subTest(label=label), self.assertRaisesRegex(ValueError, "capacity"): session.run()
            self.assertEqual(session.dispatch_count, 0)

    def test_decoded_line_breaks_quoted_unicode_and_dense_output_are_bounded(self):
        self.member("scripts/line-shapes.txt", "first\rsecond\u0085third\u2028fourth\n".encode())
        state, _, _ = self.snapshot()
        self.assertEqual(state["layout_resources"]["scan_line_counts"]["scripts/line-shapes.txt"], 4)
        name = "tests/" + "/".join(["n" * 180] * 3) + "/" + "d" * 180 + ".txt"
        self.member(name, b"\n" * 40000)
        session = self.session()
        with self.assertRaisesRegex(ValueError, "capacity"): session.run()
        self.assertEqual(session.dispatch_count, 0)

    def test_literal_recursive_bounds_and_imported_receipt_refuse(self):
        path = self.source / "README.md"; raw = path.read_bytes()
        path.write_bytes(b"x" * (128 * 1024 + 1))
        with self.assertRaisesRegex(ValueError, "bound"): self.snapshot()
        path.write_bytes(raw)
        self.member("tests/too-large.bin", b"x" * (1024 * 1024 + 1))
        session = self.session()
        with self.assertRaisesRegex(ValueError, "bound"): session.run()
        self.assertEqual(session.dispatch_count, 0)
        with self.assertRaises(TypeError): session.run(receipt={"exit": 0}, command="git ls-files")


class LiveCases(LayoutFixture, shared.RetainedFixture, unittest.TestCase):
    LIVE_ENV = "R0035_FINITE_SKILL_LAYOUT_LIVE"
    EVIDENCE_ENV = "R0035_FINITE_SKILL_LAYOUT_EVIDENCE"
    OBJECTS_ENV = "R0035_FINITE_SKILL_LAYOUT_OBJECTS"
    TEST_SOURCE = "tests/work-graph-skill-layout-cases.py"

    def actual(self, session):
        self.assertFalse(self.SOURCE_ADMISSION_ONLY)
        result = session.run()
        directory = Path(result["evidence_directory"])
        stdout, stderr = ((directory / name).read_bytes() for name in ("stdout.log", "stderr.log"))
        receipt = json.loads((directory / "receipt.json").read_bytes())
        self.assertEqual(receipt["node"], "COMMAND:tests/skill-layout-contract.test.sh:0")
        self.assertEqual((result["group"]["nodes"], len(result["group"]["omitted_nodes"])), ([receipt["node"]], 116))
        self.assertEqual((result["canonical_acceptance"], result["authority"]), ("UNQUALIFIED", "NONE"))
        return result, stdout, stderr

    def test_actual_original_positive_reuse_and_changed_population_refusal(self):
        session = self.session()
        first, stdout, stderr = self.actual(session)
        self.assertEqual((first["exit"], first["complete"], stdout, stderr),
            (0, True, b"check-skill-layout-contract: ok\npayload path hygiene: ok\n" * 2 + b"skill-layout-contract.test: ok\n", b""))
        second, stdout2, stderr2 = self.actual(session)
        self.assertEqual((first["disposition"], second["disposition"], session.dispatch_count), ("EXECUTED", "REUSED", 1))
        self.assertEqual((first["receipt_digest"], first["key"], first["producer"], stdout, stderr),
                         (second["receipt_digest"], second["key"], second["producer"], stdout2, stderr2))
        self.member("tests/added-source-member.txt")
        with self.assertRaisesRegex(ValueError, "prior receipt refused"): session.run()
        self.assertEqual(session.dispatch_count, 1)

    def test_actual_original_semantic_failure_retained_and_not_reused(self):
        diagnostic = self.semantic_mutation()
        session = self.session()
        result, stdout, stderr = self.actual(session)
        self.assertEqual((result["exit"], result["complete"], stdout), (1, True, b""))
        self.assertIn(diagnostic, stderr)
        self.assertEqual(session._issued, {})
        with self.assertRaisesRegex(ValueError, "failed or interrupted"): session.run()
        self.assertEqual(session.dispatch_count, 1)


if __name__ == "__main__":
    unittest.main()
