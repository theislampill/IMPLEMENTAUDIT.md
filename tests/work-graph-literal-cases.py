#!/usr/bin/env python3
"""Original node40/node71 literal closures; no native or whole-chain claim."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import select
import signal
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]

_historical_spec = importlib.util.spec_from_file_location("historical_fixture", ROOT / "tests/work-graph-historical-fixture.py")
H = importlib.util.module_from_spec(_historical_spec)
_historical_spec.loader.exec_module(H)
HELPER = ROOT / "scripts/qualify-work-graph-finite-leaf.py"
spec = importlib.util.spec_from_file_location("literal_profile_support", ROOT / "tests/work-graph-audit-spec-cases.py")
shared = importlib.util.module_from_spec(spec)
spec.loader.exec_module(shared)
Q, P = shared.Q, shared.P
BACKGROUND = "CONTROLLED_TASK_BACKGROUND_CHAIN_V1"
LIFECYCLE = "CONTROLLED_TASK_PLAN_LIFECYCLE_V1"
PROFILES = (BACKGROUND, LIFECYCLE)
MAPPING = {BACKGROUND: (40, "tests/background-chain-contract.test.sh", 5),
           LIFECYCLE: (71, "tests/audit-object-plan-lifecycle.test.sh", 20)}
DATA = {
    BACKGROUND: ("skills/implementaudit/templates/PROTOCOL.md", "skills/implementaudit/SKILL.md",
                 "eval/fixtures/B5-wait-contract/fixture.json"),
    LIFECYCLE: (
        "skills/implementaudit/SKILL.md", "skills/implementaudit/templates/THINKING.md",
        "skills/implementaudit/templates/ROADMAP.md", "skills/implementaudit/templates/STATE.md",
        "skills/implementaudit/templates/PROTOCOL.md", "skills/implementaudit/templates/phase-goal.txt",
        "skills/implementaudit/scripts/claim-run.sh", "skills/implementaudit/references/planning-depth.md",
        "skills/implementaudit/references/goal-format.md", "skills/implementaudit/references/phase-design.md",
        "skills/implementaudit/references/transcript-contract.md",
        "skills/implementaudit/references/audit-category-matrix.md",
        "skills/implementaudit/references/plan-lifecycle.md", "docs/diagrams/execution-spine.mmd",
        "docs/portal/pages/planning-and-phases.html", "fixtures/simple-audit/EXPECTED-TRANSCRIPT-SKELETON.md",
        "fixtures/audit-object-routing/plan-lifecycle.md"),
}


class CatalogCases(unittest.TestCase):
    def setUp(self):
        self.A, _ = shared.load("literal_catalog", HELPER)

    def select_original(self, profile):
        try:
            contract = self.A.contract_for(profile)
        except ValueError as error:
            self.fail("missing explicit original-node contract: " + profile + ": " + str(error))
        index, program, count = MAPPING[profile]
        registry = H.original("scripts/verify-package.sh")
        graph, scope, node = self.A.select_node(Q.WG, registry, P.ENVIRONMENT, profile=profile)
        self.assertEqual(len(graph["nodes"]), 117)
        self.assertEqual(node, graph["nodes"][index])
        self.assertEqual(node["source"], "bash " + program + "\n")
        self.assertEqual(scope["nodes"], ["COMMAND:" + program + ":0"])
        self.assertEqual(len(scope["omitted_nodes"]), 116)
        self.assertEqual(set(contract["data"]), set(DATA[profile]))
        self.assertEqual(len(self.A.source_paths(profile)), count)

    def test_background_selects_original_index40(self):
        self.select_original(BACKGROUND)

    def test_lifecycle_selects_original_index71_with_full_transitive_checker(self):
        self.select_original(LIFECYCLE)
        self.assertEqual(set(self.A.contract_for(LIFECYCLE)["programs"]), {
            "tests/audit-object-plan-lifecycle.test.sh", "scripts/check-planner-stages.sh"})

    def test_unknown_profile_and_registry_bytes_refuse(self):
        for profile in ("future", "CONTROLLED_TASK_BACKGROUND_CHAIN_V2", None, {}):
            with self.subTest(profile=profile), self.assertRaises(ValueError):
                self.A.contract_for(profile)
        registry = H.original("scripts/verify-package.sh")
        for profile in PROFILES:
            with self.subTest(profile=profile), self.assertRaisesRegex(ValueError, "registry"):
                self.A.select_node(Q.WG, registry + b"\n", P.ENVIRONMENT, profile=profile)


class LiteralFixture(shared.ProfileFixture):
    PROFILE = BACKGROUND

    def session(self, name="evidence", **options):
        # Existing public captured factory; CLI registration is a separate
        # serialized receiving change. Static admission has explicit tripwires.
        return self.source_admission_session(Q.create_finite_leaf_session(
            self.source, self.base / name, profile=self.profile, **options))

    def datum(self):
        return DATA[self.profile][-1]

    def semantic_mutation(self):
        path = self.source / self.datum()
        if self.profile == BACKGROUND:
            value = json.loads(path.read_bytes())
            value["matrix_instruction_contract"]["fields"][0]["behavior"] = False
            path.write_text(json.dumps(value) + "\n")
            return b"AssertionError"
        raw = path.read_bytes()
        old = b"APPROVE means criteria are met with evidence"
        self.assertIn(old, raw)
        path.write_bytes(raw.replace(old, b"APPROVE omits the required evidence rule"))
        return b"audit-object-plan-lifecycle.test: missing in fixtures/audit-object-routing/plan-lifecycle.md"


class AdmissionMixin:
    def test_literal_closure_captures_all_current_bytes_without_git_or_enumeration(self):
        state, stamps, objects = self.snapshot()
        self.assertEqual(len(state["files"]), MAPPING[self.profile][2])
        self.assertEqual(set(state["files"]), set(self.A.source_paths(self.profile)))
        self.assertFalse((self.source / ".git").exists())
        self.assertNotIn("registry_membership", state)
        self.assertNotIn("skill_namespace", state)
        for name, value in state["files"].items():
            self.assertEqual(objects[value["sha256"]], (self.source / name).read_bytes())
            self.assertIn(name, stamps)
        path = self.source / self.datum()
        path.write_bytes(path.read_bytes() + b"\n")
        changed, _, _ = self.snapshot()
        self.assertNotEqual(changed, state)

    def test_each_missing_datum_refuses_acquisition(self):
        for name in DATA[self.profile]:
            path = self.source / name
            raw, mode = path.read_bytes(), path.stat().st_mode & 0o777
            path.unlink()
            with self.subTest(path=name), self.assertRaises(FileNotFoundError):
                self.snapshot()
            path.write_bytes(raw)
            path.chmod(mode)

    def test_unknown_program_or_registry_refuses_before_runtime_or_dispatch(self):
        for number, name in enumerate((*self.A.contract_for(self.profile)["programs"], "scripts/verify-package.sh")):
            path = self.source / name
            raw = path.read_bytes()
            path.write_bytes(raw + b"\n")
            session = self.session("unknown-" + str(number))
            with self.subTest(path=name), self.assertRaisesRegex(ValueError, "executable|registry"):
                session.run()
            self.assertEqual(session.dispatch_count, 0)
            self.assertEqual(list(session.output.rglob("dispatch.json")), [])
            path.write_bytes(raw)

    def test_data_alias_and_special_file_refuse_before_runtime_or_dispatch(self):
        path = self.source / self.datum()
        raw = path.read_bytes()
        outside = self.base / "outside"
        outside.write_bytes(raw)
        for kind in ("symlink", "hardlink", "fifo", "directory"):
            path.unlink()
            if kind == "symlink": path.symlink_to(outside)
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

    def test_data_byte_bound_refuses_before_runtime_or_dispatch(self):
        bound = self.A.contract_for(self.profile)["bounds"]["file_bytes"]
        (self.source / self.datum()).write_bytes(b"x" * (bound + 1))
        session = self.session()
        with self.assertRaisesRegex(ValueError, "bound"):
            session.run()
        self.assertEqual(session.dispatch_count, 0)
        self.assertFalse((session.output / "objects").exists())

    def test_aggregate_byte_bound_refuses_even_when_each_file_fits(self):
        bound = self.A.contract_for(self.profile)["bounds"]["file_bytes"]
        for name in DATA[self.profile]:
            (self.source / name).write_bytes(b"x" * bound)
        session = self.session()
        with self.assertRaisesRegex(ValueError, "byte bound"):
            session.run()
        self.assertEqual(session.dispatch_count, 0)
        self.assertFalse((session.output / "objects").exists())

    def test_exact_private_write_bound_and_capacity_refusal(self):
        state, _, _ = self.snapshot()
        value = self.A.temporary_requirements(state, profile=self.profile)
        expected = (21, 9, 3211264) if self.profile == BACKGROUND else (0, 0, 0)
        self.assertEqual((value["files"], value["directories"], value["required_bytes"]), expected)
        self.assertLess(value["required_bytes"], 32 * 1024**2)
        if self.profile == BACKGROUND:
            self.assertEqual(value["content_bytes"], 1266)
            session = self.session()
            session.LIMITS = dict(session.LIMITS, scratch_bytes=value["required_bytes"] - 1)
            with self.assertRaisesRegex(ValueError, "scratch|temporary"):
                session.run()
            self.assertEqual(session.dispatch_count, 0)
            self.assertFalse((session.output / "objects").exists())

    def test_valid_inputs_reach_assertive_runtime_boundary_not_a_source_pass(self):
        session = self.session()
        with self.assertRaisesRegex(AssertionError, "source-admission fixture reached runtime acquisition"):
            session.run()
        self.assertEqual(session.dispatch_count, 0)
        self.assertFalse((session.output / "objects").exists())
        with self.assertRaisesRegex(AssertionError, "source-admission fixture reached dispatch"):
            session._execute()

    def test_missing_namespace_tool_remains_an_unqualified_zero_dispatch_refusal(self):
        self.SOURCE_ADMISSION_ONLY = False
        original = Path.resolve

        def absent_bwrap(path, *args, **kwargs):
            if str(path) == "/usr/bin/bwrap":
                raise FileNotFoundError("reviewed test scenario: /usr/bin/bwrap is absent")
            return original(path, *args, **kwargs)

        session = self.session()
        with mock.patch.object(Path, "resolve", new=absent_bwrap):
            with self.assertRaisesRegex(FileNotFoundError, "/usr/bin/bwrap is absent"):
                session.run()
        self.assertEqual(session.dispatch_count, 0)
        self.assertEqual(list(session.output.rglob("dispatch.json")), [])
        self.assertFalse((session.output / "objects").exists())

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


class BackgroundAdmission(AdmissionMixin, LiteralFixture, unittest.TestCase):
    PROFILE = BACKGROUND


class LifecycleAdmission(AdmissionMixin, LiteralFixture, unittest.TestCase):
    PROFILE = LIFECYCLE


class LiteralLiveFixture(LiteralFixture, shared.RetainedFixture):
    LIVE_ENV = "R0035_FINITE_LITERAL_LIVE"
    EVIDENCE_ENV = "R0035_FINITE_LITERAL_EVIDENCE"
    OBJECTS_ENV = "R0035_FINITE_LITERAL_OBJECTS"
    TEST_SOURCE = "tests/work-graph-literal-cases.py"

    def retain_completed_case(self):
        destination = os.environ.get(self.EVIDENCE_ENV)
        if destination:
            with mock.patch.dict(os.environ, {self.EVIDENCE_ENV: str(Path(destination) / self.profile)}):
                super().retain_completed_case()

    def actual(self, session):
        self.assertFalse(self.SOURCE_ADMISSION_ONLY)
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
        expected = {
            BACKGROUND: b"background-chain-contract: ok (section + vocabulary + 8 fixtures incl. retention ordering + B5 P4-13)\n",
            LIFECYCLE: b"check-planner-stages: ok\naudit-object-plan-lifecycle.test: ok\n"}
        self.assertEqual(stdout, expected[self.profile])
        second, second_out, second_err = self.actual(session)
        self.assertEqual((first["disposition"], second["disposition"]), ("EXECUTED", "REUSED"))
        self.assertEqual(first["receipt_digest"], second["receipt_digest"])
        self.assertEqual((stdout, stderr), (second_out, second_err))
        path = self.source / self.datum()
        path.write_bytes(path.read_bytes() + b"\n")
        with self.assertRaisesRegex(ValueError, "prior receipt refused"):
            session.run()
        self.assertEqual(session.dispatch_count, 1)

    def test_original_semantic_failure_retained_and_not_reused(self):
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
        child = os.fork()
        if child == 0:
            os.close(read)
            try:
                session.run()
                message = b"WRONGLY_ACCEPTED"
            except (ValueError, OSError) as error:
                message = str(error).encode()
            os.write(write, message[:4096])
            os.close(write)
            os._exit(0)
        os.close(write)
        try:
            ready, _, _ = select.select([read], [], [], 5)
            self.assertTrue(ready, "foreign producer refusal did not return")
            message = os.read(read, 4096)
            _, status = os.waitpid(child, 0)
            child = None
            self.assertEqual(os.waitstatus_to_exitcode(status), 0)
            self.assertIn(b"producer process changed", message)
            (self.base / "foreign-process-refusal.txt").write_bytes(message + b"\n")
        finally:
            os.close(read)
            if child is not None:
                os.kill(child, signal.SIGKILL)
                os.waitpid(child, 0)
        path = Path(result["evidence_directory"]) / "stdout.log"
        path.chmod(0o600)
        path.write_bytes(stdout + b"changed retained output\n")
        path.chmod(0o400)
        with self.assertRaisesRegex(ValueError, "evidence refused"):
            session.run()
        self.assertEqual(session.dispatch_count, 1)


class BackgroundLive(LiveMixin, LiteralLiveFixture, unittest.TestCase):
    PROFILE = BACKGROUND


class LifecycleLive(LiveMixin, LiteralLiveFixture, unittest.TestCase):
    PROFILE = LIFECYCLE


if __name__ == "__main__":
    unittest.main()
