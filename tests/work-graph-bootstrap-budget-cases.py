#!/usr/bin/env python3
"""Finite original88 source/runtime controls; live original tests are gated."""
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
spec = importlib.util.spec_from_file_location("bootstrap_shared", ROOT / "tests/work-graph-audit-spec-cases.py")
shared = importlib.util.module_from_spec(spec)
spec.loader.exec_module(shared)
Q, P = shared.Q, shared.P
PROFILE = "CONTROLLED_TASK_BOOTSTRAP_LOAD_BUDGET_V1"
PROGRAM = "tests/skill-bootstrap-budget.test.sh"
CHECKER = "scripts/check-skill-bootstrap-budget.sh"
EVALUATOR = "fixtures/semantic-preservation/evaluate.py"


class CatalogCases(unittest.TestCase):
    def test_exact_original88_profile_and_public_entry(self):
        A, _ = shared.load("bootstrap_catalog", ROOT / "scripts/qualify-work-graph-finite-leaf.py")
        try:
            contract = A.contract_for(PROFILE)
        except ValueError as error:
            self.fail("missing exact original88 bootstrap-load-budget profile: " + str(error))
        graph, scope, node = A.select_node(Q.WG, H.original("scripts/verify-package.sh"),
                                          P.ENVIRONMENT, profile=PROFILE)
        self.assertEqual((len(graph["nodes"]), node), (117, graph["nodes"][88]))
        self.assertEqual(node["source"], "bash " + PROGRAM + "\n")
        self.assertEqual(scope["nodes"], ["COMMAND:" + PROGRAM + ":0"])
        self.assertEqual(len(scope["omitted_nodes"]), 116)
        self.assertEqual(Q._FINITE_MODES["bootstrap-load-budget"], PROFILE)
        self.assertEqual(set(contract["programs"]), {PROGRAM, CHECKER, EVALUATOR})
        self.assertEqual(set(contract["data"]), {
            "scripts/package-contract.py", "package/implementaudit-package.json",
            "fixtures/semantic-preservation/cases.json", "fixtures/semantic-preservation/test-cases.sh",
            "fixtures/skill-bootstrap-budget/negative-full-read-installed-payload.md"})
        self.assertEqual(contract["recursive"]["roots"], ("skills",))
        self.assertFalse(contract["recursive"]["optional"])
        self.assertEqual(contract["source_modes"], "PRESERVE_READ_ONLY_MOUNT")
        self.assertEqual(set(contract["pinned_data"]),
                         {"scripts/package-contract.py", "fixtures/semantic-preservation/cases.json"})


class BootstrapFixture(shared.ProfileFixture):
    PROFILE = PROFILE

    def setUp(self):
        super().setUp()
        shutil.copytree(ROOT / "skills", self.source / "skills", dirs_exist_ok=True)
        self.restore_historical_inputs()

    def session(self, name="evidence", **options):
        return self.source_admission_session(Q.create_finite_leaf_session(
            self.source, self.base / name, profile=self.profile, **options))

    def new_member(self, raw=b"ordinary additional data\n", name=".extra/opaque.bin"):
        path = self.source / "skills" / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
        return path


class AdmissionCases(BootstrapFixture, unittest.TestCase):
    def test_full_copied_skills_and_literal_data_bytes_modes_and_empty_names(self):
        member = self.new_member(b"\x00\xff\xfeall bytes retained\n")
        (member.parent / "empty").mkdir()
        state, stamps, objects = self.snapshot()
        expected = {p.relative_to(self.source).as_posix(): p.read_bytes()
                    for p in (self.source / "skills").rglob("*") if p.is_file()}
        actual = {name: objects[row["sha256"]] for name, row in state["files"].items()
                  if name.startswith("skills/")}
        self.assertEqual(actual, expected)
        self.assertIn("skills/.extra/empty", state["directories"])
        self.assertIn("recursive_inputs", stamps)
        for name in self.A.source_paths(PROFILE):
            self.assertEqual(objects[state["files"][name]["sha256"]], (self.source / name).read_bytes())
        for name, row in state["files"].items():
            self.assertEqual(row["mode"], (self.source / name).stat().st_mode & 0o777)
        self.assertFalse((self.source / ".git").exists())

    def test_program_registry_and_dynamic_reader_data_changes_refuse_before_runtime(self):
        contract = self.A.contract_for(PROFILE)
        names = (*contract["programs"], self.A.REGISTRY, *contract["pinned_data"])
        for index, name in enumerate(names):
            path = self.source / name
            original = path.read_bytes()
            path.write_bytes(original + b"\n")
            session = self.session("changed-" + str(index))
            with self.subTest(path=name), self.assertRaisesRegex(ValueError, "executable|registry|pinned branch"):
                session.run()
            self.assertEqual((session.dispatch_count, session._issued), (0, {}))
            self.assertFalse((session.output / "objects").exists())
            path.write_bytes(original)

    def test_semantic_owner_changes_and_unlisted_references_remain_actual_data(self):
        before, _, _ = self.snapshot()
        owner = self.source / "skills/implementaudit/references/plan-lifecycle.md"
        owner.write_bytes(owner.read_bytes() + b"\nChanged owner data.\n")
        added = self.new_member(b"additional reference\n", "implementaudit/references/added-bootstrap.md")
        after, _, objects = self.snapshot()
        self.assertNotEqual(before, after)
        self.assertEqual(objects[after["files"][str(added.relative_to(self.source))]["sha256"]], added.read_bytes())
        session = self.session()
        with self.assertRaisesRegex(AssertionError, "runtime acquisition"):
            session.run()
        self.assertEqual((session.dispatch_count, session._issued), (0, {}))

    def test_one_complete_private_tree_mutation_logs_and_all_spools_fit_fixed_limits(self):
        state, _, _ = self.snapshot()
        reservation = self.A.temporary_requirements(state, profile=PROFILE)
        copied = [row for name, row in state["files"].items() if name.startswith("skills/")]
        directories = [name for name in state["directories"] if name == "skills" or name.startswith("skills/")]
        self.assertEqual(reservation["copied_source_files"], len(copied))
        self.assertEqual(reservation["copied_source_directories"], len(directories))
        self.assertEqual((reservation["private_copy_files"], reservation["files"], reservation["directories"]),
                         (len(copied) + 6, len(copied) + 26, len(directories) + 6))
        self.assertEqual((reservation["original_checker_calls"], reservation["possible_heredoc_spools"]), (16, 17))
        self.assertGreaterEqual(reservation["governor_private_max_bytes"], 21999)
        self.assertGreaterEqual(reservation["oversized_private_bytes"],
                                state["files"]["skills/implementaudit/SKILL.md"]["bytes"] + 17500)
        session = self.session()
        self.assertEqual(session.LIMITS["scratch_bytes"], 32 * 1024**2)
        self.A.require_resource_capacity(reservation, session.LIMITS)
        with self.assertRaisesRegex(AssertionError, "runtime acquisition"):
            session.run()
        self.assertEqual((session.dispatch_count, session._issued), (0, {}))

    def test_added_private_copy_population_refuses_unchanged_scratch_capacity(self):
        for index in range(260):
            self.new_member(b"copied member\n", ".many/member-" + str(index))
        state, _, _ = self.snapshot()
        session = self.session()
        reservation = self.A.temporary_requirements(state, profile=PROFILE)
        self.assertGreater(reservation["required_bytes"], session.LIMITS["scratch_bytes"])
        with self.assertRaisesRegex(ValueError, "scratch capacity"):
            session.run()
        self.assertEqual((session.dispatch_count, session._issued), (0, {}))
        self.assertFalse((session.output / "objects").exists())


class RuntimeCases(unittest.TestCase):
    def setUp(self):
        self.A, _ = shared.load("bootstrap_runtime", ROOT / "scripts/qualify-work-graph-finite-leaf.py")
        self.objects, self.runtime = {}, dict(files={}, observations={})
        for name in self.A._BOOTSTRAP_RUNTIME_PINS:
            if name == "/usr/bin/seq":
                continue
            path = Path(name).resolve(strict=True)
            metadata, raw = P.read_regular(path, single_link=False)
            key = self.A.digest(raw)
            self.objects[key] = raw
            self.runtime["files"][name] = dict(mode=0o555, bytes=len(raw), sha256=key)
            self.runtime["observations"][name] = dict(resolved=str(path), mode=metadata["mode"],
                bytes=len(raw), sha256=key, identity=metadata["identity"])

    def test_real_seq_bytes_and_captured_dependencies_or_actual_host_refusal(self):
        actual = dict((name, row["sha256"]) for name, row in self.runtime["files"].items())
        try:
            actual["/usr/bin/seq"] = self.A.digest(P.read_regular(Path("/usr/bin/seq"))[1])
        except (OSError, ValueError):
            with self.assertRaises((OSError, ValueError)):
                self.A._capture_bootstrap_runtime(P, self.runtime, self.objects)
            self.assertNotIn("/usr/bin/seq", self.runtime["files"])
            return
        if actual != self.A._BOOTSTRAP_RUNTIME_PINS:
            with self.assertRaisesRegex(ValueError, "unsupported.*seq"):
                self.A._capture_bootstrap_runtime(P, self.runtime, self.objects)
            self.assertNotIn("/usr/bin/seq", self.runtime["files"])
            return
        self.A._capture_bootstrap_runtime(P, self.runtime, self.objects)
        record = self.runtime["files"]["/usr/bin/seq"]
        self.assertEqual(self.objects[record["sha256"]], Path("/usr/bin/seq").read_bytes())
        self.assertEqual(record["mode"], 0o555)
        self.assertEqual(self.runtime["bootstrap_tool_closure"], self.A._BOOTSTRAP_RUNTIME_PINS)

    def test_missing_and_mismatched_captured_dependency_refuse(self):
        name = "/lib/x86_64-linux-gnu/libc.so.6"
        original = self.runtime["files"].pop(name)
        with self.assertRaisesRegex(ValueError, "seq.*closure"):
            self.A._capture_bootstrap_runtime(P, self.runtime, self.objects)
        self.runtime["files"][name] = dict(original, sha256="0" * 64)
        with self.assertRaisesRegex(ValueError, "seq.*closure"):
            self.A._capture_bootstrap_runtime(P, self.runtime, self.objects)
        self.assertNotIn("/usr/bin/seq", self.runtime["files"])

    def test_changed_seq_source_is_refused_without_qualifying_a_replacement(self):
        # On a genuinely unsupported host, retain the explicit refusal instead
        # of inventing a successful executable qualification to reach this guard.
        if (any(row["sha256"] != self.A._BOOTSTRAP_RUNTIME_PINS[name]
                for name, row in self.runtime["files"].items()) or not Path("/usr/bin/seq").is_file()):
            with self.assertRaises((OSError, ValueError)):
                self.A._capture_bootstrap_runtime(P, self.runtime, self.objects)
            self.assertNotIn("/usr/bin/seq", self.runtime["files"])
            return
        original = P.read_regular
        def unknown(path, *args, **kwargs):
            metadata, raw = original(path, *args, **kwargs)
            return (metadata, raw + b"changed executable") if str(path) == "/usr/bin/seq" else (metadata, raw)
        with mock.patch.object(P, "read_regular", side_effect=unknown), self.assertRaisesRegex(ValueError, "captured seq"):
            self.A._capture_bootstrap_runtime(P, self.runtime, self.objects)
        self.assertNotIn("/usr/bin/seq", self.runtime["files"])


class LiveCases(BootstrapFixture, shared.RetainedFixture, unittest.TestCase):
    LIVE_ENV = "R0035_BOOTSTRAP_BUDGET_LIVE"
    EVIDENCE_ENV = "R0035_BOOTSTRAP_BUDGET_EVIDENCE"
    OBJECTS_ENV = "R0035_BOOTSTRAP_BUDGET_OBJECTS"
    TEST_SOURCE = "tests/work-graph-bootstrap-budget-cases.py"

    def actual(self, session):
        self.assertFalse(self.SOURCE_ADMISSION_ONLY)
        result = session.run()
        directory = Path(result["evidence_directory"])
        stdout, stderr = ((directory / name).read_bytes() for name in ("stdout.log", "stderr.log"))
        receipt = json.loads((directory / "receipt.json").read_bytes())
        self.assertEqual(receipt["node"], "COMMAND:" + PROGRAM + ":0")
        self.assertEqual((result["canonical_acceptance"], result["authority"]), ("UNQUALIFIED", "NONE"))
        return result, stdout, stderr

    def test_actual_original_success_reuse_and_added_member_currentness_refusal(self):
        session = self.session()
        first, stdout, stderr = self.actual(session)
        self.assertEqual((first["exit"], first["complete"], stderr), (0, True, b""))
        self.assertIn(b"bootstrap-route: verified source owner; semantic reserve ", stdout)
        labels = [line for line in stdout.splitlines() if line.startswith(b"bootstrap-control: ")]
        self.assertEqual(labels, [b"bootstrap-control: " + name for name in (
            b"under-ceiling-one-byte-reserve", b"complete-progressive-route",
            b"missing-trigger-reference-still-present", b"commented-trigger", b"quoted-trigger",
            b"inert-trigger", b"wrong-owner-route", b"inert-run-root-edge-with-stage-owner-retained",
            b"equivalent-route-reflow", b"missing-owner", b"wrong-version-owner", b"mixed-owner",
            b"restored-complete-route")])
        self.assertTrue(stdout.endswith(b"skill-bootstrap-budget.test: ok\n"))
        second, _, _ = self.actual(session)
        self.assertEqual((first["disposition"], second["disposition"], session.dispatch_count), ("EXECUTED", "REUSED", 1))
        self.assertEqual(first["receipt_digest"], second["receipt_digest"])
        self.new_member()
        with self.assertRaisesRegex(ValueError, "prior receipt refused"):
            session.run()
        self.assertEqual(session.dispatch_count, 1)

    def test_actual_missing_load_map_reference_fails_and_is_not_reused(self):
        self.new_member(b"An ordinary new reference.\n", "implementaudit/references/added-bootstrap-live.md")
        session = self.session()
        result, _, stderr = self.actual(session)
        self.assertEqual((result["exit"], result["complete"]), (1, True))
        self.assertIn(b"Reference Load Map missing references/added-bootstrap-live.md", stderr)
        self.assertEqual(session._issued, {})
        with self.assertRaisesRegex(ValueError, "failed or interrupted"):
            session.run()
        self.assertEqual(session.dispatch_count, 1)


if __name__ == "__main__":
    unittest.main()
