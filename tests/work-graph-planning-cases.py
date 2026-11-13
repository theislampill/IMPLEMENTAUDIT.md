#!/usr/bin/env python3
"""Exact original node31/80/84 acquisition controls; no native authority."""
import ast
import importlib.util
import json
import os
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]

_historical_spec = importlib.util.spec_from_file_location("historical_fixture", ROOT / "tests/work-graph-historical-fixture.py")
H = importlib.util.module_from_spec(_historical_spec)
_historical_spec.loader.exec_module(H)
spec = importlib.util.spec_from_file_location("planning_profile_support", ROOT / "tests/work-graph-audit-spec-cases.py")
shared = importlib.util.module_from_spec(spec)
spec.loader.exec_module(shared)
Q, P = shared.Q, shared.P
PLAN = "CONTROLLED_TASK_PLAN_QUALITY_V1"
AUTH = "CONTROLLED_TASK_AUTHORIZATION_BINDING_V1"
READ_ONLY = "CONTROLLED_TASK_READ_ONLY_PLANS_V1"
MAPPING = {
    PLAN: (84, "tests/plan-quality-contract.test.sh", "plan-quality", 16),
    AUTH: (31, "tests/authorization-binding-contract.test.sh", "authorization-binding", 12),
    READ_ONLY: (80, "tests/read-only-plans-lane.test.sh", "read-only-plans", 41),
}
DEFAULTS = {"fixtures/read-only-plans/valid-handoff-plan.md", "fixtures/e2e-mini-audit-loop/phase-1.md"}


def literal_python_paths(program):
    """Read the original fixed Python body, not the profile's path catalog."""
    body = (ROOT / program).read_text().split("<<'PY'\n", 1)[1].rsplit("\nPY", 1)[0]
    return {node.value for node in ast.walk(ast.parse(body))
            if isinstance(node, ast.Constant) and isinstance(node.value, str)
            and node.value.startswith(("skills/", "fixtures/", "docs/", "scripts/", "tests/"))
            and not node.value.endswith("/")
            and not any(char in node.value for char in (" ", "\n", ":"))}


class CatalogCases(unittest.TestCase):
    def setUp(self):
        self.A, _ = shared.load("planning_catalog", ROOT / "scripts/qualify-work-graph-finite-leaf.py")

    def test_three_original_profiles_are_explicitly_available(self):
        missing = []
        for profile in MAPPING:
            try:
                self.A.contract_for(profile)
            except ValueError:
                missing.append(profile)
        self.assertEqual(missing, [], "missing exact original-node profiles")

    def test_original_117_node_mapping_and_public_modes(self):
        registry = H.original("scripts/verify-package.sh")
        for profile, (index, program, mode, count) in MAPPING.items():
            with self.subTest(profile=profile):
                graph, scope, node = self.A.select_node(Q.WG, registry, P.ENVIRONMENT, profile=profile)
                self.assertEqual((len(graph["nodes"]), node), (117, graph["nodes"][index]))
                self.assertEqual(node["source"], "bash " + program + "\n")
                self.assertEqual(scope["nodes"], ["COMMAND:" + program + ":0"])
                self.assertEqual(len(scope["omitted_nodes"]), 116)
                self.assertEqual(len(self.A.source_paths(profile)), count)
                self.assertEqual(Q._FINITE_MODES[mode], profile)

    def test_plan_defaults_transitive_reads_and_parity_data_are_complete(self):
        common = DEFAULTS | literal_python_paths("scripts/check-plan-quality-contract.sh")
        extra = {"fixtures/read-only-plans/" + name for name in (
            "read-only-zero-mutation.status", "read-only-audit-ledger.status",
            "negative-read-only-source-mutation.status")}
        extra |= {"fixtures/secret-hygiene/" + name for name in (
            "negative-plan-reproduces-fake-secret.md", "negative-child-prompt-missing-security-rules.md")}
        required = common | extra | {"scripts/verify-package.sh", "scripts/check-plan-quality-contract.sh",
                                     "tests/plan-quality-contract.test.sh"}
        self.assertEqual(set(self.A.source_paths(PLAN)), required)
        self.assertEqual(self.A.contract_for(PLAN)["source_modes"], "PRESERVE_READ_ONLY_MOUNT")
        parity = literal_python_paths("scripts/check-capability-parity-contract.sh")
        required = common | parity | {"scripts/verify-package.sh", "scripts/check-capability-parity-contract.sh"}
        directories = {name for name in required if not Path(name).suffix}
        self.assertEqual(directories, {"fixtures/read-only-plans", "fixtures/secret-hygiene", "fixtures/dogfood-bootstrap"})
        self.assertEqual(set(self.A.source_paths(READ_ONLY)), required - directories)
        self.assertEqual(set(self.A.contract_for(READ_ONLY)["programs"]), {
            "tests/read-only-plans-lane.test.sh", "scripts/check-plan-quality-contract.sh",
            "scripts/check-capability-parity-contract.sh"})

    def test_authorization_whole_helper_and_original_glob_sensitive_fixtures_are_pinned(self):
        contract = self.A.contract_for(AUTH)
        self.assertEqual(set(contract["programs"]), {
            "tests/authorization-binding-contract.test.sh",
            "skills/implementaudit/scripts/check-authorization-binding.sh"})
        self.assertEqual(set(contract["pinned_data"]), {"fixtures/authorization-binding/" + name for name in (
            "auth.txt", "authorization-record.txt", "authorization-record-missing-source.txt")})
        self.assertEqual({"bash", "dirname", "grep", "tr", "head", "sed", "awk", "wc", "rm", "mktemp", "cp", "cat"} - set(P.TOOLS), set())


class PlanningFixture(shared.ProfileFixture):
    PROFILE = PLAN

    def session(self, name="evidence", **options):
        return self.source_admission_session(Q.create_finite_leaf_session(
            self.source, self.base / name, profile=self.profile, **options))

    def semantic_mutation(self):
        if self.profile == AUTH:
            name, before, after = "skills/implementaudit/templates/PROTOCOL.md", b"defaults are NEVER\nimplicitly adopted", b"implicit defaults are now allowed"
            diagnostic = b"authorization-binding-contract: no-implicit-defaults rule missing"
        else:
            name, before, after = "fixtures/read-only-plans/valid-handoff-plan.md", b"## Current state", b"## Removed current state"
            diagnostic = b"missing required token: ## Current state"
        path = self.source / name
        raw = path.read_bytes()
        self.assertTrue(before in raw, "exact semantic-mutation anchor is absent: " + name)
        path.write_bytes(raw.replace(before, after))
        return diagnostic


class AdmissionMixin:
    def test_complete_literal_source_identity_and_all_missing_operands_refuse(self):
        state, stamps, objects = self.snapshot()
        self.assertEqual(len(state["files"]), MAPPING[self.profile][3])
        self.assertNotIn("recursive_inputs", state)
        self.assertFalse((self.source / ".git").exists())
        for name, record in state["files"].items():
            self.assertEqual(objects[record["sha256"]], (self.source / name).read_bytes())
            self.assertIn(name, stamps)
        for name in self.A.contract_for(self.profile)["data"]:
            path = self.source / name
            raw = path.read_bytes()
            path.unlink()
            with self.subTest(missing=name), self.assertRaises((ValueError, OSError)):
                self.snapshot()
            path.write_bytes(raw)
            path.chmod(0o644)

    def test_changed_program_registry_and_glob_sensitive_data_refuse_before_runtime(self):
        contract = self.A.contract_for(self.profile)
        for number, name in enumerate((*contract["programs"], *contract.get("pinned_data", {}), "scripts/verify-package.sh")):
            path = self.source / name
            raw = path.read_bytes()
            path.write_bytes(raw + b"\n")
            session = self.session("changed-" + str(number))
            with self.subTest(path=name), self.assertRaisesRegex(ValueError, "source|registry|executable|pinned"):
                session.run()
            self.assertEqual(session.dispatch_count, 0)
            self.assertFalse((session.output / "objects").exists())
            path.write_bytes(raw)

    def test_data_and_directory_aliases_refuse(self):
        name = self.A.contract_for(self.profile)["data"][0]
        path = self.source / name
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
        alias = self.base / "aliased-source"
        alias.symlink_to(self.source, target_is_directory=True)
        with self.assertRaises((ValueError, OSError)):
            self.A.snapshot_source(P, alias, {}, profile=self.profile)

    def test_semantic_data_change_is_captured_and_not_preaccepted(self):
        before, _, _ = self.snapshot()
        self.semantic_mutation()
        after, _, _ = self.snapshot()
        self.assertNotEqual(before, after)
        session = self.session()
        with self.assertRaisesRegex(AssertionError, "runtime acquisition"):
            session.run()
        self.assertEqual(session.dispatch_count, 0)
        self.assertEqual(session._issued, {})

    def test_generated_files_spools_diagnostics_and_capacity_are_reserved(self):
        state, _, _ = self.snapshot()
        reservation = self.A.temporary_requirements(state, profile=self.profile)
        counts = {PLAN: (45, 1), AUTH: (7, 1), READ_ONLY: (5, 0)}
        self.assertEqual((reservation["files"], reservation["directories"]), counts[self.profile])
        self.assertEqual(reservation["copies"], 9 if self.profile == PLAN else 0)
        self.assertGreater(reservation["largest_file_bytes"], 0)
        self.assertLess(reservation["required_bytes"], 32 * 1024**2)
        for label, limit in (("scratch", {"scratch_bytes": reservation["required_bytes"] - 1}),
                             ("stream", {"stream_bytes": reservation["max_stderr_bytes"] - 1}),
                             ("file", {"file_bytes": reservation["largest_file_bytes"] - 1})):
            session = self.session("capacity-" + label)
            session.LIMITS = dict(session.LIMITS, **limit)
            with self.subTest(limit=label), self.assertRaisesRegex(ValueError, "capacity"):
                session.run()
            self.assertEqual(session.dispatch_count, 0)
        if self.profile == PLAN:
            path = self.source / "fixtures/read-only-plans/valid-handoff-plan.md"
            path.write_bytes(path.read_bytes() + b"x" * 65536)
            larger, _, _ = self.snapshot()
            changed = self.A.temporary_requirements(larger, profile=self.profile)
            self.assertGreaterEqual(changed["content_bytes"] - reservation["content_bytes"], 9 * 65536)

    def test_oversized_input_and_optional_native_branch_are_not_admitted(self):
        name = self.A.contract_for(self.profile)["data"][0]
        bound = self.A.contract_for(self.profile)["bounds"]["file_bytes"]
        (self.source / name).write_bytes(b"x" * (bound + 1))
        session = self.session()
        with self.assertRaisesRegex(ValueError, "bound"):
            session.run()
        self.assertEqual(session.dispatch_count, 0)
        with self.assertRaises(TypeError):
            session.run(command="--phase", receipt={"exit": 0})


class PlanAdmission(AdmissionMixin, PlanningFixture, unittest.TestCase):
    PROFILE = PLAN


class AuthorizationAdmission(AdmissionMixin, PlanningFixture, unittest.TestCase):
    PROFILE = AUTH


class ReadOnlyAdmission(AdmissionMixin, PlanningFixture, unittest.TestCase):
    PROFILE = READ_ONLY


class PlanningLiveFixture(PlanningFixture, shared.RetainedFixture):
    LIVE_ENV = "R0035_FINITE_PLANNING_LIVE"
    EVIDENCE_ENV = "R0035_FINITE_PLANNING_EVIDENCE"
    OBJECTS_ENV = "R0035_FINITE_PLANNING_OBJECTS"
    TEST_SOURCE = "tests/work-graph-planning-cases.py"

    def retain_completed_case(self):
        destination = os.environ.get(self.EVIDENCE_ENV)
        if destination:
            from unittest import mock
            with mock.patch.dict(os.environ, {self.EVIDENCE_ENV: str(Path(destination) / self.profile)}):
                super().retain_completed_case()

    def actual(self, session):
        self.assertFalse(self.SOURCE_ADMISSION_ONLY)
        result = session.run()
        directory = Path(result["evidence_directory"])
        stdout, stderr = ((directory / name).read_bytes() for name in ("stdout.log", "stderr.log"))
        receipt = json.loads((directory / "receipt.json").read_bytes())
        self.assertEqual(receipt["node"], "COMMAND:" + MAPPING[self.profile][1] + ":0")
        self.assertEqual(result["group"]["nodes"], [receipt["node"]])
        self.assertEqual(len(result["group"]["omitted_nodes"]), 116)
        self.assertEqual((result["canonical_acceptance"], result["authority"]), ("UNQUALIFIED", "NONE"))
        return result, stdout, stderr


class LiveMixin:
    def test_actual_original_positive_reuse_and_changed_input_refusal(self):
        session = self.session()
        first, stdout, stderr = self.actual(session)
        expected = {
            PLAN: b"check-plan-quality-contract: ok\n" * 3 + b"plan-quality-contract.test: ok\n",
            AUTH: b"authorization-binding-contract: ok (intake 6 + match/drift + no-binds + 3 Fable adversarial)\n",
            READ_ONLY: b"check-capability-parity-contract: ok\ncheck-plan-quality-contract: ok\nread-only-plans-lane.test: ok\n"}
        self.assertEqual((first["exit"], first["complete"], stdout, stderr), (0, True, expected[self.profile], b""))
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
        result, _, stderr = self.actual(session)
        self.assertEqual((result["exit"], result["complete"]), (1, True))
        self.assertIn(diagnostic, stderr)
        self.assertEqual(session._issued, {})
        with self.assertRaisesRegex(ValueError, "failed or interrupted"):
            session.run()
        self.assertEqual(session.dispatch_count, 1)


class PlanLive(LiveMixin, PlanningLiveFixture, unittest.TestCase):
    PROFILE = PLAN


class AuthorizationLive(LiveMixin, PlanningLiveFixture, unittest.TestCase):
    PROFILE = AUTH


class ReadOnlyLive(LiveMixin, PlanningLiveFixture, unittest.TestCase):
    PROFILE = READ_ONLY


if __name__ == "__main__":
    unittest.main()
