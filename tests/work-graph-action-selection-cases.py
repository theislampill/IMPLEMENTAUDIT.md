#!/usr/bin/env python3
"""Twelve original90 source controls; no runtime or original-execution claim."""
import ast
import hashlib
import importlib.util
import os
from pathlib import Path
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]

_historical_spec = importlib.util.spec_from_file_location("historical_fixture", ROOT / "tests/work-graph-historical-fixture.py")
H = importlib.util.module_from_spec(_historical_spec)
_historical_spec.loader.exec_module(H)
PROFILE = "CONTROLLED_TASK_ACTION_SELECTION_CONTRACT_V1"
MODE = "action-selection-contract"
PROGRAM = "tests/action-selection-contract.test.sh"
CHECKER = "scripts/check-action-selection-contract.sh"
FIXTURE_ROOT = "fixtures/audit-action-selection"
DEPTH = "skills/implementaudit/references/planning-depth.md"
ENGINEERING = FIXTURE_ROOT + "/engineering-value-cases.json"
REQUIRED = FIXTURE_ROOT + "/verifier-plan-cases.json"
DATA = (
    "skills/implementaudit/SKILL.md",
    DEPTH,
    "skills/implementaudit/references/lean-operating-discipline.md",
    "skills/implementaudit/references/child-agents.md",
    "skills/implementaudit/references/plan-lifecycle.md",
    "skills/implementaudit/templates/THINKING.md",
    "skills/implementaudit/templates/ROADMAP.md",
    "fixtures/native-integration/single-plan-native-route.md",
    "fixtures/audit-object-routing/deep-pressure-disclosure.md",
)
INCOMING_CONTRACTS_AST_SHA256 = "1c5e0d03608bc9f5d3b320d4af2d8d15a8465deb5b29dad84be23333d2f05e0e"
INCOMING_CONTRACT_NAMES = ('RESPEC_PROFILE',
 'BOOTSTRAP_BUDGET_PROFILE',
 'INTERNAL_ROUTING_PROFILE',
 'LEAN_DISCIPLINE_PROFILE',
 'CLAIM_BOUNDARY_PROFILE',
 'AUDIT_OBJECT_CONTRACT_PROFILE',
 'TERMINOLOGY_PROFILE',
 'MINI_AUDIT_PROFILE',
 'PACKAGE_SHAPE_PROFILE',
 'NATIVE_INTEGRATION_PROFILE',
 'SKILL_LAYOUT_PROFILE',
 'RETENTION_PROFILE',
 'AUDIT_OBJECT_PROFILE',
 'PROFILE',
 'ANDON_PROFILE',
 'REGISTRY_PROFILE',
 'MARKER_PROFILE',
 'COMMIT_PROFILE',
 'AGENTS_PROFILE',
 'ESCALATION_PROFILE',
 'TOPOLOGY_PROFILE',
 'CAPABILITY_PROFILE',
 'ISSUES_PROFILE',
 'TERMINAL_PROFILE',
 'BACKGROUND_PROFILE',
 'LIFECYCLE_PROFILE',
 'PLAN_QUALITY_PROFILE',
 'AUTHORIZATION_PROFILE',
 'READ_ONLY_PROFILE',
 'SAFEGUARD_PROFILE',
 'ROUTING_PROFILE',
 'INSTALLED_PROFILE',
 'PLANNER_COPY_PROFILE',
 'FANOUT_PROFILE')
PROGRAMS = {
    PROGRAM: "f49fdde27d2e23558bd1e8cc74c66fb30520953426e4b5166ebcb93dffaec0b0",
    CHECKER: "38e7b277b8429b0d13fb7710f47e4f144dde693504c8640463c2ab074f8cc6bb",
}
FIXTURES = tuple(FIXTURE_ROOT + "/" + name for name in (
    "dominance-dogfood-receipt.json", "engineering-value-cases.json",
    "narrow-direct-stays-shallow.md", "negative-keyword-gated-depth.md",
    "negative-missing-selection-record.md", "negative-size-only-deepening.md",
    "ordinary-task-deepens.md", "verifier-plan-cases.json"))


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    exec(compile(path.read_bytes(), str(path), "exec"), module.__dict__)
    return module


B = load("action_selection_shared_fixtures", ROOT / "tests/work-graph-audit-spec-cases.py")


class SourceCases(B.ProfileFixture, unittest.TestCase):
    PROFILE = PROFILE

    def setUp(self):
        super().setUp()
        for name in FIXTURES:
            path = self.source / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(H.input_bytes(name))
            path.chmod(H.input_mode(name))
        for guard in (
            mock.patch.object(B.P, "acquire_runtime", side_effect=AssertionError("runtime acquisition forbidden")),
            mock.patch.object(self.A, "finite_runtime", side_effect=AssertionError("runtime acquisition forbidden")),
            mock.patch.object(B.Q.VerifierTaskSession, "_execute", side_effect=AssertionError("original dispatch forbidden")),
            mock.patch.object(B.Q.VerifierTaskSession, "_mini_audit_entropy_device_v1",
                              side_effect=AssertionError("node90 entropy-device observation forbidden")),
            mock.patch("subprocess.Popen", side_effect=AssertionError("external execution forbidden")),
        ):
            guard.start()
            self.addCleanup(guard.stop)

    def assert_no_dispatch(self, session):
        self.assertEqual(session.dispatch_count, 0)
        self.assertEqual(session._issued, {})
        self.assertEqual(list(session.output.rglob("dispatch.json")), [])
        self.assertEqual(list(session.output.rglob("result.json")), [])

    def test_c01_fixed_catalog_and_historical_contracts(self):
        """C01: original90 wiring and historical34 after fixed runner-pin advances."""
        contract = self.A.contract_for(PROFILE)
        self.assertEqual((contract["label"], contract["index"], contract["program"]), (MODE, 90, PROGRAM))
        self.assertEqual(contract["programs"], PROGRAMS)
        self.assertEqual(contract["data"], DATA)
        self.assertEqual(contract["bounds"], dict(file_bytes=131072, total_bytes=8388608, files=12))
        self.assertEqual(contract["recursive"], dict(roots=(FIXTURE_ROOT,), optional=False,
            bounds=dict(file_bytes=1048576, total_bytes=8388608, entries=2048, depth=40, path_bytes=2048),
            required_members=FIXTURES))
        self.assertEqual(contract["source_modes"], "PRESERVE_READ_ONLY_MOUNT")
        self.assertNotIn("pinned_data", contract)
        self.assertNotIn("complete_git", contract)
        self.assertNotIn("scratch_bytes", contract)
        self.assertEqual(B.Q._FINITE_MODES[MODE], PROFILE)
        entry = ast.parse((ROOT / "tests/work-graph-finite-entry-cases.py").read_bytes())
        modes = next(node.value for node in entry.body if isinstance(node, ast.Assign)
            and any(isinstance(t, ast.Name) and t.id == "PROFILES" for t in node.targets))
        self.assertEqual(ast.literal_eval(modes)[MODE], PROFILE)
        graph, scope, node = self.A.select_node(B.Q.WG, H.original("scripts/verify-package.sh"), B.P.ENVIRONMENT, profile=PROFILE)
        self.assertEqual(len(graph["nodes"]), 117)
        self.assertEqual(node, graph["nodes"][90])
        self.assertEqual(node["source"], "bash " + PROGRAM + "\n")
        self.assertEqual(hashlib.sha256(node["source"].encode()).hexdigest(),
                         "a66331a3bac577619f223ab4dcf28447327668977677f1b9fdc7aaa2f6b18e1b")
        self.assertEqual(scope["nodes"], ["COMMAND:" + PROGRAM + ":0"])
        self.assertEqual(len(scope["omitted_nodes"]), 116)
        # Original105 advances six shared runner identities. Reverse only that
        # exact byte pin before comparing the complete historical34 contracts.
        runner_pin = "6f6d2bdbcf8350d6b370d37a5e15f4ddb73d336b5bc42d941540f3269613150f"
        self.assertEqual(hashlib.sha256((ROOT / self.A.RUNNER).read_bytes()).hexdigest(), runner_pin)
        normalized = self.helper.replace(runner_pin.encode("ascii"),
            b"532b06dbe91298bf71d44c88ecf20186adc93b4e3fb16ee2c4d12bc2edee45ff")
        contracts = next(node.value for node in ast.parse(normalized).body if isinstance(node, ast.Assign)
            and any(isinstance(t, ast.Name) and t.id == "_CONTRACTS" for t in node.targets))
        retained = [(key, value) for key, value in zip(contracts.keys, contracts.values)
            if isinstance(key, ast.Name) and key.id in INCOMING_CONTRACT_NAMES]
        self.assertEqual(tuple(key.id for key, _ in retained), INCOMING_CONTRACT_NAMES)
        self.assertEqual(len(retained), 34)
        payload = "\n".join(ast.dump(ast.Tuple(elts=[key, value], ctx=ast.Load()), include_attributes=False)
                            for key, value in retained)
        self.assertEqual(hashlib.sha256(payload.encode()).hexdigest(), INCOMING_CONTRACTS_AST_SHA256)
        loader = ast.parse((ROOT / "scripts/load-work-graph-readme-effect.py").read_bytes())
        pins = next(node.value for node in loader.body if isinstance(node, ast.Assign)
            and any(isinstance(t, ast.Name) and t.id == "PINS" for t in node.targets))
        self.assertEqual(ast.literal_eval(pins.args[0])["scripts/qualify-work-graph-verifier.py"],
                         hashlib.sha256(H.original("scripts/qualify-work-graph-verifier.py")).hexdigest())
        self.assertIn(b'"${py_cmd[@]}" tests/work-graph-action-selection-cases.py\n',
                      (ROOT / "tests/work-graph-verifier.test.sh").read_bytes())

    def test_c02_complete_baseline_modes_and_serial_reservation(self):
        """C02:20 actual inputs, preserved0644 copy modes and4,325,376 bytes."""
        state, _, objects = self.snapshot()
        self.assertEqual(len(state["files"]), 20)
        self.assertEqual(sum(row["bytes"] for row in state["files"].values()), 333310)
        self.assertEqual(len(state["directories"]), 11)
        self.assertEqual(set(state["files"]), {self.A.REGISTRY, *PROGRAMS, *DATA, *FIXTURES})
        self.assertNotIn("complete_git_inputs", state)
        subject = self.A.image_subject(state, profile=PROFILE)
        self.assertNotIn(self.A.REGISTRY, subject)
        files = {"/work/" + name: (objects[row["sha256"]], row["mode"]) for name, row in subject.items()}
        projected, permissions = self.A.finite_image_permissions(files, state, profile=PROFILE)
        self.assertEqual(projected, files)
        self.assertEqual(permissions, dict(source_modes="PRESERVE_READ_ONLY_MOUNT"))
        self.assertTrue(all(mode == 0o644 for _, mode in projected.values()))
        bound = self.A.temporary_requirements(state, profile=PROFILE)
        self.assertEqual((bound["copies"], bound["files"], bound["directories"]), (1, 21, 10))
        self.assertEqual(bound["copied_source_files"], 17)
        self.assertEqual(bound["copied_source_bytes"], 210236)
        self.assertEqual(bound["max_JSON_growth_bytes"], 332804)
        self.assertEqual(bound["max_single_copy_rounded_growth_bytes"], 327680)
        self.assertEqual(bound["report_initial_bound"], 468008)
        self.assertEqual(bound["report_file_bound"], 587885)
        self.assertEqual(bound["report_binary_diagnostic_bound"], 3384)
        self.assertEqual(bound["transform_bound_bytes"], 30905)
        self.assertEqual(bound["overhead_bytes"], 2031616)
        self.assertEqual(bound["required_bytes"], 4325376)
        self.assertEqual(bound["max_stderr_bytes"], 1338405)
        self.assertEqual(bound["original_data_memory_reservation"], 40002368)
        self.assertEqual((bound["original_checker_calls"], bound["private_tree_incarnations"], bound["live_copy_trees"]), (69, 68, 1))
        session = self.session()
        self.assertEqual(session.ENVIRONMENT, B.P.ENVIRONMENT)
        self.assertEqual(session.LIMITS, dict(cpu_seconds=90, address_bytes=1073741824, file_bytes=16777216,
            staging_file_bytes=285212672, descriptors=4096, work_bytes=536870912, scratch_bytes=33554432,
            wall_seconds=120, stream_bytes=16777216, retained_object_bytes=1073741824, evidence_bytes=2147483648))
        self.A.require_resource_capacity(bound, session.LIMITS)
        self.assert_no_dispatch(session)

    def test_c03_faithful_negative_is_data_not_admission_oracle(self):
        """C03: remove original case3's exact76-byte line; reach runtime boundary."""
        path = self.source / DEPTH
        lines = path.read_bytes().splitlines(keepends=True)
        removed = [line for line in lines if b"Depth never requires an activation keyword" in line]
        self.assertEqual(len(removed), 1)
        self.assertEqual(len(removed[0]), 76)
        raw = b"".join(line for line in lines if line not in removed)
        path.write_bytes(raw)
        self.assertEqual(hashlib.sha256(raw).hexdigest(), "678b90e0cc6580e2853aab429f0706d505bf075b6b6547a4eaf2fd50b4da352a")
        state, _, objects = self.snapshot()
        self.assertEqual(objects[state["files"][DEPTH]["sha256"]], raw)
        session = self.session()
        with self.assertRaisesRegex(AssertionError, "source-admission fixture reached runtime acquisition"):
            session.run()
        self.assert_no_dispatch(session)

    def test_c04_hidden_opaque_nested_and_empty_namespace_is_current(self):
        """C04: complete recursive membership includes noncopied and empty inputs."""
        first, stamps, _ = self.snapshot()
        hidden = FIXTURE_ROOT + "/.original90-currentness-witness.bin"
        witness = b"original90-currentness\0opaque\xff\n"
        self.assertEqual(hashlib.sha256(witness).hexdigest(), "8d1c0e9fd6dba84188511ad12c5bd4dc27952310861fcbc3b1b409646420231a")
        (self.source / hidden).write_bytes(witness)
        nested = FIXTURE_ROOT + "/nested/opaque.bin"
        (self.source / nested).parent.mkdir()
        (self.source / nested).write_bytes(b"opaque\0\xff\n")
        for name in (FIXTURE_ROOT + "/nested/.empty", FIXTURE_ROOT + "/looks-like-data.json"):
            (self.source / name).mkdir()
        changed, current, objects = self.snapshot()
        self.assertNotEqual(changed, first)
        self.assertNotEqual(current, stamps)
        self.assertEqual(objects[changed["files"][hidden]["sha256"]], witness)
        self.assertIn(nested, changed["files"])
        self.assertEqual(changed["directories"][FIXTURE_ROOT + "/nested/.empty"], 0o755)
        self.assertEqual(changed["directories"][FIXTURE_ROOT + "/looks-like-data.json"], 0o755)
        bound = changed["recursive_inputs"]["resources"]
        self.assertEqual(bound["copied_source_files"], 17)
        self.assertGreater(bound["report_file_bound"], first["recursive_inputs"]["resources"]["report_file_bound"])
        self.assertNotIn(hidden, bound["copied_paths"])

    def test_c05_required_operand_absence_refuses(self):
        """C05: an absent original positive fixture cannot become a clean scan."""
        (self.source / REQUIRED).unlink()
        with self.assertRaisesRegex(ValueError, "required original positive operand is absent"):
            self.snapshot()

    def test_c06_recursive_symlink_refuses(self):
        """C06: a selected fixture symlink never imports outside bytes."""
        path = self.source / REQUIRED
        outside = self.base / "outside"
        outside.write_bytes(path.read_bytes())
        path.unlink()
        path.symlink_to(outside)
        with self.assertRaises((ValueError, OSError)):
            self.snapshot()

    def test_c07_recursive_hardlink_refuses(self):
        """C07: the complete source owner rejects a shared-inode fixture."""
        path = self.source / REQUIRED
        os.link(path, self.base / "outside-alias")
        self.assertEqual(path.stat().st_nlink, 2)
        with self.assertRaises((ValueError, OSError)):
            self.snapshot()

    def test_c08_recursive_unsupported_mode_refuses(self):
        """C08: unsupported input modes are not normalized into accepted copies."""
        (self.source / REQUIRED).chmod(0o600)
        with self.assertRaisesRegex(ValueError, "mode"):
            self.snapshot()

    def test_c09_each_original_program_and_registry_pin_refuses(self):
        """C09: three fixed pin variants; none reaches runtime or original dispatch."""
        for index, name in enumerate((PROGRAM, CHECKER, self.A.REGISTRY)):
            with self.subTest(path=name):
                path = self.source / name
                original = path.read_bytes()
                path.write_bytes(original + b"\n")
                session = self.session("pin-%d" % index)
                with self.assertRaisesRegex(ValueError, "executable or registry"):
                    session.run()
                self.assert_no_dispatch(session)
                path.write_bytes(original)

    def test_c10_copy_glob_and_single_json_growth_recompute(self):
        """C10: actual extra copied bytes and one growing JSON rewrite affect bounds."""
        before, _, _ = self.snapshot()
        baseline = self.A.temporary_requirements(before, profile=PROFILE)
        extra = FIXTURE_ROOT + "/extra.md"
        (self.source / extra).write_bytes(b"x" * 65536 + b"\n")
        path = self.source / ENGINEERING
        old_size = path.stat().st_size
        path.write_bytes(path.read_bytes() + b" " * 65536)
        state, _, _ = self.snapshot()
        bound = self.A.temporary_requirements(state, profile=PROFILE)
        self.assertEqual(bound["copied_source_files"], 18)
        self.assertEqual(bound["copied_source_bytes"], 210236 + 65537 + 65536)
        self.assertIn(extra, bound["copied_paths"])
        self.assertEqual(bound["json_rewrite_bounds"][ENGINEERING], 6 * (old_size + 65536) + 1024)
        self.assertEqual(bound["files"], 22)
        self.assertEqual(bound["copies"], 1)
        self.assertEqual(bound["directories"], 10)
        self.assertGreater(bound["required_bytes"], baseline["required_bytes"])
        self.assertGreater(bound["original_data_memory_reservation"], baseline["original_data_memory_reservation"])
        self.assertGreater(bound["max_stderr_bytes"], baseline["max_stderr_bytes"])

    def test_c11_acquired_many_line_report_refuses_before_runtime(self):
        """C11: an ordinary bounded input can exceed fixed scratch; fail closed."""
        path = self.source / FIXTURE_ROOT / "over-cap.bin"
        path.write_bytes(b"\n" * 200000)
        state, _, _ = self.snapshot()
        self.assertLess(sum(row["bytes"] for row in state["files"].values()), 8388608)
        bound = self.A.temporary_requirements(state, profile=PROFILE)
        self.assertGreater(bound["required_bytes"], 33554432)
        session = self.session()
        with self.assertRaisesRegex(ValueError, "scratch capacity"):
            session.run()
        self.assert_no_dispatch(session)

    def test_c12_closing_recursive_namespace_drift_refuses(self):
        """C12: a new nested file after acquisition cannot evade the closing census."""
        nested = self.source / FIXTURE_ROOT / "closing"
        nested.mkdir()
        actual = B.P.snapshot_tree
        calls = []
        def drift(root, objects, bounds):
            result = actual(root, objects, bounds)
            if Path(root) == self.source / FIXTURE_ROOT:
                calls.append(str(root))
                if len(calls) == 1:
                    (nested / "late.bin").write_bytes(b"new recursive member\0")
            return result
        with mock.patch.object(B.P, "snapshot_tree", side_effect=drift):
            with self.assertRaisesRegex(ValueError, "recursive source changed during complete acquisition"):
                self.snapshot()
        self.assertEqual(len(calls), 2)


if __name__ == "__main__":
    unittest.main()
