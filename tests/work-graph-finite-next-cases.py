#!/usr/bin/env python3
"""Three explicit original-node profiles; no canonical-chain/native claim."""
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
HELPER = ROOT / "scripts/qualify-work-graph-finite-leaf.py"
spec = importlib.util.spec_from_file_location("finite_next_support", ROOT / "tests/work-graph-audit-spec-cases.py")
shared = importlib.util.module_from_spec(spec)
spec.loader.exec_module(shared)
Q, P = shared.Q, shared.P
COMMIT = "CONTROLLED_TASK_COMMIT_MESSAGE_V1"
AGENTS = "CONTROLLED_TASK_AGENTS_BOOTSTRAP_V1"
ESCALATION = "CONTROLLED_TASK_ANDON_ESCALATION_V1"
PROFILES = (COMMIT, AGENTS, ESCALATION)
MAPPING = {COMMIT: (56, "tests/commit-message-contract.test.sh", 31),
           AGENTS: (59, "tests/agents-bootstrap-budget.test.sh", 5),
           ESCALATION: (39, "tests/andon-escalation-judgment.test.sh", 8)}


class CatalogCases(unittest.TestCase):
    def setUp(self):
        self.A, _ = shared.load("finite_next_catalog", HELPER)

    def test_exact_original_indices_and_omitted_population(self):
        registry = (ROOT / "scripts/verify-package.sh").read_bytes()
        for profile, (index, program, count) in MAPPING.items():
            with self.subTest(profile=profile):
                graph, scope, node = self.A.select_node(Q.WG, registry, P.ENVIRONMENT, profile=profile)
                self.assertEqual(len(graph["nodes"]), 117)
                self.assertEqual(node, graph["nodes"][index])
                self.assertEqual(node["source"], "bash " + program + "\n")
                self.assertEqual(scope["nodes"], ["COMMAND:" + program + ":0"])
                self.assertEqual(len(scope["omitted_nodes"]), 116)
                self.assertEqual(len(self.A.source_paths(profile)), count)

    def test_unknown_profile_and_registry_bytes_refuse(self):
        for profile in ("future", "CONTROLLED_TASK_COMMIT_MESSAGE_V2", None, {}):
            with self.subTest(profile=profile), self.assertRaises(ValueError):
                self.A.contract_for(profile)
        registry = (ROOT / "scripts/verify-package.sh").read_bytes()
        for profile in PROFILES:
            with self.subTest(profile=profile), self.assertRaisesRegex(ValueError, "registry"):
                self.A.select_node(Q.WG, registry + b"\n", P.ENVIRONMENT, profile=profile)

    def test_commit_fixture_population_is_exactly_the_28_literal_operands(self):
        import re
        data = (ROOT / "tests/commit-message-contract.test.sh").read_text()
        actual = set(re.findall(r"fixtures/commit-message/[A-Za-z0-9-]+\.md", data))
        self.assertEqual(set(self.A.COMMIT_FIXTURES), actual)
        self.assertEqual(len(actual), 28)
        self.assertNotIn(".git", self.A.source_paths(COMMIT))

    def test_contract_copies_cannot_modify_admission_policy(self):
        for profile in PROFILES:
            first = self.A.contract_for(profile)
            first["programs"].clear()
            first["bounds"]["file_bytes"] = 2**40
            self.assertTrue(self.A.contract_for(profile)["programs"])
            self.assertLess(self.A.contract_for(profile)["bounds"]["file_bytes"], 2**40)


class NextFixture(shared.ProfileFixture):
    PROFILE = COMMIT

    def session(self, name="evidence", **options):
        # Use the existing public captured factory. CLI names are a separately
        # serialized receiving change; the profile API already owns validation.
        return self.source_admission_session(Q.create_finite_leaf_session(
            self.source, self.base / name, profile=self.profile, **options))

    def datum(self):
        if self.profile == COMMIT:
            return self.A.COMMIT_FIXTURES[0]
        if self.profile == AGENTS:
            return "AGENTS.md"
        return self.A.ESCALATION_FIXTURES[-1]

    def semantic_mutation(self):
        if self.profile == COMMIT:
            name = "fixtures/commit-message/behavior-change-empty-body-FAIL.md"
            (self.source / name).write_bytes((self.source / "fixtures/commit-message/docs-typo-slim-PASS.md").read_bytes())
            return b"expected exit 1, got 0"
        if self.profile == AGENTS:
            path = self.source / "AGENTS.md"
            path.write_bytes(path.read_bytes().replace(b"## Project Identity", b"## Removed Project Heading"))
            return b"missing required bootloader token: ## Project Identity"
        path = self.source / self.A.ESCALATION_FIXTURES[-1]
        path.write_bytes(path.read_bytes().replace(b"Rejection reason:", b"Removed reason:"))
        return b"reasoned-rejection fixture must record an explicit reason"


class AdmissionMixin:
    def test_complete_literal_closure_and_current_data_identity(self):
        state, stamps, objects = self.snapshot()
        self.assertEqual(len(state["files"]), MAPPING[self.profile][2])
        self.assertEqual(set(state["files"]), set(self.A.source_paths(self.profile)))
        self.assertFalse((self.source / ".git").exists())
        self.assertNotIn("registry_membership", state)
        for name, value in state["files"].items():
            self.assertEqual(objects[value["sha256"]], (self.source / name).read_bytes())
            self.assertIn(name, stamps)
        path = self.source / self.datum()
        path.write_bytes(path.read_bytes() + b"\n")
        changed, _, _ = self.snapshot()
        self.assertNotEqual(changed, state)

    def test_each_missing_datum_refuses_without_semantic_negative_credit(self):
        for name in self.A.contract_for(self.profile)["data"]:
            path = self.source / name
            raw = path.read_bytes()
            path.unlink()
            with self.subTest(path=name), self.assertRaises((ValueError, OSError)):
                self.snapshot()
            path.write_bytes(raw)
            path.chmod(0o644)

    def test_unknown_program_or_registry_refuses_before_dispatch(self):
        contract = self.A.contract_for(self.profile)
        for number, name in enumerate((*contract["programs"], "scripts/verify-package.sh")):
            path = self.source / name
            raw = path.read_bytes()
            path.write_bytes(raw + b"\n")
            session = self.session("unknown-" + str(number))
            with self.subTest(path=name), self.assertRaisesRegex(ValueError, "executable|registry"):
                session.run()
            self.assertEqual(session.dispatch_count, 0)
            self.assertEqual(list(session.output.rglob("dispatch.json")), [])
            path.write_bytes(raw)

    def test_data_alias_and_special_file_refuse_before_dispatch(self):
        path = self.source / self.datum()
        raw = path.read_bytes()
        outside = self.base / "outside"
        outside.write_bytes(raw)
        for kind in ("link", "hardlink", "fifo", "directory"):
            path.unlink()
            if kind == "link": path.symlink_to(outside)
            elif kind == "hardlink": os.link(outside, path)
            elif kind == "fifo": os.mkfifo(path)
            else: path.mkdir()
            session = self.session("unsafe-" + kind)
            with self.subTest(kind=kind), self.assertRaises((ValueError, OSError)):
                session.run()
            self.assertEqual(session.dispatch_count, 0)
            if kind == "directory": path.rmdir()
            else: path.unlink()
            path.write_bytes(raw)
            path.chmod(0o644)

    def test_data_byte_bounds_refuse_before_dispatch(self):
        bound = self.A.contract_for(self.profile)["bounds"]["file_bytes"]
        path = self.source / self.datum()
        path.write_bytes(b"x" * (bound + 1))
        session = self.session()
        with self.assertRaisesRegex(ValueError, "bound"):
            session.run()
        self.assertEqual(session.dispatch_count, 0)
        self.assertFalse((session.output / "objects").exists())

    def test_fixed_private_write_set_and_capacity_gate(self):
        state, _, _ = self.snapshot()
        reservation = self.A.temporary_requirements(state, profile=self.profile)
        if self.profile == AGENTS:
            self.assertEqual((reservation["files"], reservation["directories"]), (13, 1))
            self.assertGreaterEqual(reservation["content_bytes"], 5412 + 788 + 1034 + 3 * 65536)
            self.assertLess(reservation["required_bytes"], 8 * 1024**2)
            session = self.session()
            session.LIMITS = dict(session.LIMITS, scratch_bytes=reservation["required_bytes"] - 1)
            with self.assertRaisesRegex(ValueError, "scratch|temporary"):
                session.run()
            self.assertEqual(session.dispatch_count, 0)
            self.assertFalse((session.output / "objects").exists())
        elif self.profile == COMMIT:
            self.assertEqual((reservation["files"], reservation["directories"]), (28, 0))
            self.assertGreater(reservation["content_bytes"], 0)
            self.assertLess(reservation["required_bytes"], 8 * 1024**2)
        else:
            self.assertEqual((reservation["files"], reservation["directories"], reservation["required_bytes"]), (0, 0, 0))

    def test_no_imported_receipt_command_or_environment(self):
        session = self.session()
        for kwargs in ({"receipt": {"exit": 0}}, {"command": "true"}, {"environment": {}}):
            with self.subTest(kwargs=kwargs), self.assertRaises(TypeError):
                session.run(**kwargs)
        self.assertEqual(session.dispatch_count, 0)

    def test_raw_parent_traversal_refuses_before_evidence_creation(self):
        output = self.base / "refused"
        with self.assertRaisesRegex(ValueError, "parent traversal"):
            Q.create_finite_leaf_session(self.source / ".." / "source", output, profile=self.profile)
        self.assertFalse(output.exists())


class CommitAdmission(AdmissionMixin, NextFixture, unittest.TestCase):
    PROFILE = COMMIT


class AgentsAdmission(AdmissionMixin, NextFixture, unittest.TestCase):
    PROFILE = AGENTS


class EscalationAdmission(AdmissionMixin, NextFixture, unittest.TestCase):
    PROFILE = ESCALATION


class NextLiveFixture(NextFixture, shared.RetainedFixture):
    LIVE_ENV = "R0035_FINITE_NEXT_LIVE"
    EVIDENCE_ENV = "R0035_FINITE_NEXT_EVIDENCE"
    OBJECTS_ENV = "R0035_FINITE_NEXT_OBJECTS"
    TEST_SOURCE = "tests/work-graph-finite-next-cases.py"

    def retain_completed_case(self):
        destination = os.environ.get(self.EVIDENCE_ENV)
        if destination:
            with mock.patch.dict(os.environ, {self.EVIDENCE_ENV: str(Path(destination) / self.profile)}):
                super().retain_completed_case()

    def actual(self, session):
        result = session.run()
        directory = Path(result["evidence_directory"])
        stdout, stderr = ((directory / name).read_bytes() for name in ("stdout.log", "stderr.log"))
        self.assertEqual((directory / "exit-code.txt").read_bytes(), (str(result["exit"]) + "\n").encode())
        receipt = json.loads((directory / "receipt.json").read_bytes())
        self.assertEqual(receipt["node"], "COMMAND:" + MAPPING[self.profile][1] + ":0")
        self.assertEqual(result["group"]["nodes"], [receipt["node"]])
        self.assertEqual(len(result["group"]["omitted_nodes"]), 116)
        self.assertEqual(receipt["scope"], self.profile)
        self.assertEqual(result["canonical_acceptance"], "UNQUALIFIED")
        self.assertEqual(result["authority"], "NONE")
        return result, stdout, stderr


class LiveMixin:
    def test_actual_original_positive_reuse_and_current_input_refusal(self):
        session = self.session()
        first, stdout, stderr = self.actual(session)
        self.assertEqual(first["exit"], 0, stderr)
        self.assertTrue(first["complete"])
        self.assertEqual(stderr, b"")
        expected = {COMMIT: b"commit-message-contract: ok (28 fixtures)\n",
                    ESCALATION: b"andon-escalation-judgment: ok (contract + 5 scored fixtures)\n"}
        if self.profile in expected:
            self.assertEqual(stdout, expected[self.profile])
        else:
            self.assertTrue(stdout.startswith(b"check-agents-bootstrap-budget: ok ("))
            self.assertTrue(stdout.endswith(b"agents-bootstrap-budget.test: ok\n"))
        second, second_out, second_err = self.actual(session)
        self.assertEqual((first["disposition"], second["disposition"]), ("EXECUTED", "REUSED"))
        self.assertEqual(first["receipt_digest"], second["receipt_digest"])
        self.assertEqual((stdout, stderr), (second_out, second_err))
        path = self.source / self.datum()
        path.write_bytes(path.read_bytes() + b"\n")
        with self.assertRaisesRegex(ValueError, "prior receipt refused"):
            session.run()
        self.assertEqual(session.dispatch_count, 1)

    def test_original_semantic_negative_is_retained_and_not_reused(self):
        expected = self.semantic_mutation()
        session = self.session()
        result, stdout, stderr = self.actual(session)
        self.assertEqual(result["exit"], 1, stderr)
        self.assertTrue(result["complete"])
        self.assertIn(expected, stderr)
        self.assertEqual(session._issued, {})
        with self.assertRaisesRegex(ValueError, "failed or interrupted"):
            session.run()
        self.assertEqual(session.dispatch_count, 1)

    def test_foreign_process_and_changed_retained_result_refuse(self):
        session = self.session()
        result, stdout, stderr = self.actual(session)
        self.assertEqual(result["exit"], 0, stderr)
        read, write = os.pipe()
        pid = os.fork()
        if pid == 0:
            os.close(read)
            try:
                session.run()
                data = b"WRONGLY_ACCEPTED"
            except (ValueError, OSError) as exc:
                data = str(exc).encode()
            os.write(write, data[:4096])
            os.close(write)
            os._exit(0)
        os.close(write)
        message = os.read(read, 4096)
        os.close(read)
        _, status = os.waitpid(pid, 0)
        self.assertEqual(status, 0)
        self.assertIn(b"producer process changed", message)
        path = Path(result["evidence_directory"]) / "stdout.log"
        path.chmod(0o600)
        path.write_bytes(stdout + b"foreign mutation\n")
        path.chmod(0o400)
        with self.assertRaisesRegex(ValueError, "evidence refused"):
            session.run()
        self.assertEqual(session.dispatch_count, 1)


class CommitLive(LiveMixin, NextLiveFixture, unittest.TestCase):
    PROFILE = COMMIT


class AgentsLive(LiveMixin, NextLiveFixture, unittest.TestCase):
    PROFILE = AGENTS


class EscalationLive(LiveMixin, NextLiveFixture, unittest.TestCase):
    PROFILE = ESCALATION


if __name__ == "__main__":
    unittest.main()
