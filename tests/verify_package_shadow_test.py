#!/usr/bin/env python3
"""Behavioural tests for the non-authoritative package shadow verifier."""

from __future__ import annotations

import importlib.util
import hashlib
import json
import shutil
import subprocess
import tempfile
import sys
import unittest
from unittest import mock
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ENGINE_PATH = ROOT / "scripts" / "verify-package-shadow.py"
FIXTURES = ROOT / "tests" / "fixtures" / "verify-package-shadow"


def load_engine():
    spec = importlib.util.spec_from_file_location("verify_package_shadow", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load engine from {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class RegistryTests(unittest.TestCase):
    def valid_registry(self, root: Path) -> dict:
        canonical = root / "scripts" / "verify-package.sh"
        canonical.parent.mkdir(parents=True, exist_ok=True)
        canonical.write_bytes((FIXTURES / "canonical-verifier.sh").read_bytes())
        return {
            "schema": "implementaudit.verify-package-shadow.registry.v1",
            "authority": "NONE",
            "canonical": {
                "path": "scripts/verify-package.sh",
                "sha256": hashlib.sha256(canonical.read_bytes()).hexdigest(),
                "first_command": "scripts/alpha.sh",
            },
            "checks": [
                {
                    "id": "canonical.inline-preflight",
                    "kind": "canonical_prefix",
                    "order": 0,
                    "argv": [],
                    "dependencies": [],
                },
                {
                    "id": "script.alpha",
                    "kind": "command",
                    "order": 1,
                    "argv": ["bash", "scripts/alpha.sh"],
                    "dependencies": [],
                },
                {
                    "id": "script.bravo",
                    "kind": "command",
                    "order": 2,
                    "argv": ["bash", "scripts/bravo.sh", "--flag", "value"],
                    "dependencies": ["script.alpha"],
                },
                {
                    "id": "test.charlie",
                    "kind": "command",
                    "order": 3,
                    "argv": ["bash", "tests/charlie.test.sh"],
                    "dependencies": [],
                },
            ],
        }

    def valid_compact_registry(self, root: Path) -> dict:
        expanded = self.valid_registry(root)
        commands = [check["argv"] for check in expanded["checks"][1:]]
        population_digest = hashlib.sha256(
            json.dumps(commands, sort_keys=True, separators=(",", ":")).encode(
                "utf-8"
            )
        ).hexdigest()
        return {
            "schema": "implementaudit.verify-package-shadow.registry.v1",
            "authority": "NONE",
            "canonical": {
                **expanded["canonical"],
                "command_population_sha256": population_digest,
            },
            "composite": {
                "id": "canonical.inline-preflight",
                "input_contract": {"mode": "tracked_tree"},
            },
            "overrides": {
                "script.bravo": {"dependencies": ["script.alpha"]}
            },
        }

    def test_extracts_exact_command_population(self):
        """Dropping or splitting a continued canonical command must be caught."""
        engine = load_engine()
        text = (FIXTURES / "canonical-verifier.sh").read_text(encoding="utf-8")

        commands = engine.extract_canonical_commands(
            text, first_command="scripts/alpha.sh"
        )

        self.assertEqual(
            commands,
            [
                (9, ("bash", "scripts/alpha.sh")),
                (10, ("bash", "scripts/bravo.sh", "--flag", "value")),
                (12, ("bash", "tests/charlie.test.sh")),
            ],
        )

    def test_materializes_stable_checks_from_digest_bound_population(self):
        """Compact config must expand into stable check identities and edges."""
        engine = load_engine()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            compact = self.valid_compact_registry(root)
            registry = engine.materialize_registry(compact, root)
            self.assertEqual(
                [check["id"] for check in registry["checks"]],
                [
                    "canonical.inline-preflight",
                    "script.alpha",
                    "script.bravo",
                    "test.charlie",
                ],
            )
            self.assertEqual(
                registry["checks"][2]["dependencies"], ["script.alpha"]
            )
            self.assertEqual(engine.validate_registry(registry, root), [])

    def test_rejects_changed_canonical_digest(self):
        """A stale registry must not run against changed canonical bytes."""
        engine = load_engine()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            registry = self.valid_registry(root)
            (root / "scripts" / "verify-package.sh").write_text(
                "#!/usr/bin/env bash\nfalse\n", encoding="utf-8"
            )
            errors = engine.validate_registry(registry, root)
        self.assertIn("canonical verifier digest mismatch", errors)

    def test_rejects_missing_canonical_command(self):
        """Omitting a canonical command must invalidate the shadow registry."""
        engine = load_engine()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            registry = self.valid_registry(root)
            registry["checks"].pop()
            errors = engine.validate_registry(registry, root)
        self.assertIn("canonical command population mismatch", errors)

    def test_rejects_reordered_canonical_commands(self):
        """A registry may not reorder commands while claiming canonical parity."""
        engine = load_engine()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            registry = self.valid_registry(root)
            registry["checks"][1], registry["checks"][2] = (
                registry["checks"][2],
                registry["checks"][1],
            )
            errors = engine.validate_registry(registry, root)
        self.assertIn("check orders must be contiguous from zero", errors)
        self.assertIn("canonical command population mismatch", errors)

    def test_rejects_duplicate_check_identity(self):
        """Duplicate identities would make results and checkpoints ambiguous."""
        engine = load_engine()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            registry = self.valid_registry(root)
            registry["checks"][2]["id"] = "script.alpha"
            errors = engine.validate_registry(registry, root)
        self.assertIn("duplicate check id: script.alpha", errors)

    def test_rejects_unknown_dependency(self):
        """An unresolvable edge must fail before any command executes."""
        engine = load_engine()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            registry = self.valid_registry(root)
            registry["checks"][1]["dependencies"] = ["missing.check"]
            errors = engine.validate_registry(registry, root)
        self.assertIn("script.alpha has unknown dependency: missing.check", errors)

    def test_rejects_dependency_cycle(self):
        """A cycle cannot produce a complete deterministic frontier."""
        engine = load_engine()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            registry = self.valid_registry(root)
            registry["checks"][1]["dependencies"] = ["script.bravo"]
            errors = engine.validate_registry(registry, root)
        self.assertIn("dependency graph contains a cycle", errors)


class SchedulerTests(unittest.TestCase):
    def make_check(
        self,
        order: int,
        check_id: str,
        status: str,
        log: Path,
        dependencies: list[str] | None = None,
    ) -> dict:
        return {
            "id": check_id,
            "kind": "command",
            "order": order,
            "argv": [
                sys.executable,
                str(FIXTURES / "check.py"),
                "--id",
                check_id,
                "--status",
                status,
                "--log",
                str(log),
            ],
            "dependencies": dependencies or [],
            "implementation_sources": [],
            "input_contract": {"mode": "explicit", "paths": []},
            "material_tools": [sys.executable],
            "environment": [],
        }

    def test_continues_independent_checks_and_blocks_only_real_dependents(self):
        """A failed check must not terminate unrelated later evidence."""
        engine = load_engine()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            log = root / "execution.log"
            checks = [
                self.make_check(0, "A", "pass", log),
                self.make_check(1, "B", "fail", log),
                self.make_check(2, "C", "pass", log, ["B"]),
                self.make_check(3, "D", "pass", log),
                self.make_check(4, "E", "fail", log),
                self.make_check(5, "F", "pass", log),
            ]
            registry = {
                "schema": "implementaudit.verify-package-shadow.registry.v1",
                "authority": "NONE",
                "checks": checks,
            }
            report = engine.run_shadow(
                registry,
                engine.RunOptions(
                    repo_root=root,
                    output_dir=root / "evidence",
                    timeout_seconds=5,
                    mode="KEEP_GOING",
                ),
            )

            self.assertEqual(log.read_text(encoding="utf-8").splitlines(), ["A", "B", "D", "E", "F"])
            self.assertEqual(report.pass_checks, ["A", "D", "F"])
            self.assertEqual(report.primary_failures, ["B", "E"])
            self.assertEqual(report.blocked_checks, ["C"])
            self.assertEqual(report.blocked_dependency_map, {"C": ["B"]})
            self.assertEqual(report.infrastructure_errors, [])
            self.assertTrue(report.complete_safe_failure_frontier)
            self.assertEqual(report.authority, "NONE")

    def test_report_projection_is_deterministic_and_machine_readable(self):
        """Logical ordering must not depend on completion or mapping order."""
        engine = load_engine()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            log = root / "execution.log"
            registry = {
                "schema": "implementaudit.verify-package-shadow.registry.v1",
                "authority": "NONE",
                "checks": [
                    self.make_check(0, "first", "pass", log),
                    self.make_check(1, "second", "fail", log),
                ],
            }
            report = engine.run_shadow(
                registry,
                engine.RunOptions(root, root / "evidence", 5, "KEEP_GOING"),
            )
            payload = report.to_json_dict()

        self.assertEqual(payload["mode"], "KEEP_GOING")
        self.assertEqual(payload["pass_checks"], ["first"])
        self.assertEqual(payload["primary_failures"], ["second"])
        self.assertEqual(payload["earliest_failure"], "second")
        self.assertEqual(payload["authority"], "NONE")
        self.assertEqual([item["check_id"] for item in payload["checks"]], ["first", "second"])

    def test_missing_material_tool_is_infrastructure_error_and_work_continues(self):
        """A missing host prerequisite must not masquerade as product failure."""
        engine = load_engine()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            log = root / "execution.log"
            missing = self.make_check(0, "missing-tool", "pass", log)
            missing["material_tools"] = ["implementaudit-tool-that-does-not-exist"]
            good = self.make_check(1, "good", "pass", log)
            report = engine.run_shadow(
                {"checks": [missing, good]},
                engine.RunOptions(root, root / "evidence", 5, "KEEP_GOING"),
            )
        self.assertEqual(report.infrastructure_errors, ["missing-tool"])
        self.assertEqual(report.pass_checks, ["good"])
        self.assertFalse(report.complete_safe_failure_frontier)

    def test_process_start_failure_is_infrastructure_error(self):
        """An unlaunchable command is host evidence, not a package FAIL."""
        engine = load_engine()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            check = self.make_check(0, "unlaunchable", "pass", root / "log")
            check["argv"] = [str(root / "missing-executable")]
            check["material_tools"] = []
            report = engine.run_shadow(
                {"checks": [check]},
                engine.RunOptions(root, root / "evidence", 5, "KEEP_GOING"),
            )
        self.assertEqual(report.infrastructure_errors, ["unlaunchable"])
        self.assertIn("process start failed", report.checks[0].detail)

    def test_timeout_is_infrastructure_error(self):
        """An incomplete timed run must never become product failure evidence."""
        engine = load_engine()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            check = self.make_check(0, "slow", "sleep", root / "log")
            check["argv"].extend(["--seconds", "0.2"])
            report = engine.run_shadow(
                {"checks": [check]},
                engine.RunOptions(root, root / "evidence", 0.02, "KEEP_GOING"),
            )
        self.assertEqual(report.infrastructure_errors, ["slow"])
        self.assertIn("timeout after", report.checks[0].detail)

    def test_not_applicable_is_distinct_from_pass(self):
        """A progressive check that does not trigger must not claim PASS."""
        engine = load_engine()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            check = self.make_check(0, "conditional", "not-applicable", root / "log")
            check["not_applicable_output"] = "SHADOW_NOT_APPLICABLE"
            report = engine.run_shadow(
                {"checks": [check]},
                engine.RunOptions(root, root / "evidence", 5, "KEEP_GOING"),
            )
        self.assertEqual(report.skipped_not_applicable, ["conditional"])
        self.assertEqual(report.pass_checks, [])

    def test_composite_prefix_executes_exact_inline_region_only(self):
        """The approved legacy composite must stop before discrete commands."""
        engine = load_engine()
        if engine.resolve_tool("bash") is None:
            self.skipTest("Git Bash is unavailable")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            canonical = root / "scripts" / "verify-package.sh"
            canonical.parent.mkdir(parents=True)
            canonical.write_bytes((FIXTURES / "canonical-verifier.sh").read_bytes())
            registry = {
                "checks": [
                    {
                        "id": "canonical.inline-preflight",
                        "kind": "canonical_prefix",
                        "order": 0,
                        "argv": [],
                        "dependencies": [],
                        "material_tools": ["bash"],
                    }
                ],
                "canonical": {
                    "path": "scripts/verify-package.sh",
                    "first_command": "scripts/alpha.sh",
                },
            }
            report = engine.run_shadow(
                registry,
                engine.RunOptions(root, root / "evidence", 5, "KEEP_GOING"),
            )
            stdout = Path(report.checks[0].stdout_path).read_text(encoding="utf-8")
        self.assertEqual(report.pass_checks, ["canonical.inline-preflight"])
        self.assertIn("composite inline preflight", stdout)
        self.assertNotIn("alpha", stdout)

    def test_oracle_comparison_rejects_suppressed_canonical_failure(self):
        """Shadow evidence must include every failure the fail-fast oracle reached."""
        engine = load_engine()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            log = root / "execution.log"
            registry = {
                "checks": [
                    self.make_check(0, "A", "pass", log),
                    self.make_check(1, "B", "fail", log),
                    self.make_check(2, "E", "fail", log),
                ]
            }
            report = engine.run_shadow(
                registry,
                engine.RunOptions(root, root / "evidence", 5, "KEEP_GOING"),
            )
        comparison = engine.semantic_oracle_comparison(["B", "missing"], report)
        self.assertEqual(comparison["result"], "FAIL")
        self.assertEqual(comparison["suppressed_failures"], ["missing"])
        passing = engine.semantic_oracle_comparison(["B"], report)
        self.assertEqual(passing["result"], "PASS")
        self.assertEqual(passing["additional_shadow_failures"], ["E"])


class CheckpointTests(unittest.TestCase):
    def make_root(self, root: Path) -> tuple[Path, Path, Path]:
        implementation = root / "checks" / "check.py"
        implementation.parent.mkdir(parents=True)
        shutil.copyfile(FIXTURES / "check.py", implementation)
        relevant = root / "inputs" / "relevant.txt"
        relevant.parent.mkdir(parents=True)
        relevant.write_text("v1\n", encoding="utf-8")
        log = root / "execution.log"
        return implementation, relevant, log

    def make_check(
        self,
        order: int,
        check_id: str,
        implementation: Path,
        relevant: Path,
        log: Path,
        *,
        status: str = "pass",
        dependencies: list[str] | None = None,
        environment: list[str] | None = None,
        applicability: dict | None = None,
    ) -> dict:
        return {
            "id": check_id,
            "kind": "command",
            "order": order,
            "argv": [
                sys.executable,
                str(implementation),
                "--id",
                check_id,
                "--status",
                status,
                "--log",
                str(log),
            ],
            "dependencies": dependencies or [],
            "implementation_sources": [str(implementation)],
            "input_contract": {
                "mode": "explicit",
                "paths": [str(relevant)],
            },
            "material_tools": [sys.executable],
            "environment": environment or [],
            "applicability": applicability or {"mode": "always"},
            "checkpoint_policy": {"mode": "exact_declared_inputs"},
        }

    def run_engine(
        self,
        engine,
        root: Path,
        checks: list[dict],
        *,
        mode: str,
        output_name: str,
        environment: dict[str, str] | None = None,
    ):
        return engine.run_shadow(
            {
                "schema": "implementaudit.verify-package-shadow.registry.v1",
                "authority": "NONE",
                "checks": checks,
            },
            engine.RunOptions(
                root,
                root / output_name,
                5,
                mode,
                checkpoint_dir=root / "checkpoints",
                environment=environment,
            ),
        )

    def test_unchanged_exact_pass_is_reused_without_execution(self):
        engine = load_engine()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            implementation, relevant, log = self.make_root(root)
            checks = [self.make_check(0, "A", implementation, relevant, log)]
            fresh = self.run_engine(engine, root, checks, mode="FRESH", output_name="fresh")
            resumed = self.run_engine(engine, root, checks, mode="RESUME", output_name="resumed")

            self.assertEqual(log.read_text(encoding="utf-8").splitlines(), ["A"])
            self.assertEqual(fresh.checks_executed, ["A"])
            self.assertEqual(resumed.checkpoints_reused, ["A"])
            self.assertEqual(resumed.checks_executed, [])
            self.assertEqual(resumed.checks[0].execution_source, "CHECKPOINT_REUSED")

    def test_relevant_change_invalidates_but_unrelated_change_preserves(self):
        engine = load_engine()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            implementation, relevant, log = self.make_root(root)
            checks = [self.make_check(0, "A", implementation, relevant, log)]
            self.run_engine(engine, root, checks, mode="FRESH", output_name="fresh")
            (root / "unrelated.txt").write_text("unrelated\n", encoding="utf-8")
            preserved = self.run_engine(engine, root, checks, mode="RESUME", output_name="preserved")
            relevant.write_text("v2\n", encoding="utf-8")
            invalidated = self.run_engine(engine, root, checks, mode="RESUME", output_name="invalidated")

            self.assertEqual(preserved.checkpoints_reused, ["A"])
            self.assertEqual(invalidated.checks_executed, ["A"])
            self.assertIn("input_manifest_changed", invalidated.invalidation_reasons["A"])

    def test_changed_dependency_pass_fingerprint_invalidates_dependent(self):
        engine = load_engine()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            implementation, relevant_a, log = self.make_root(root)
            relevant_b = root / "inputs" / "dependent.txt"
            relevant_b.write_text("stable\n", encoding="utf-8")
            checks = [
                self.make_check(0, "A", implementation, relevant_a, log),
                self.make_check(1, "B", implementation, relevant_b, log, dependencies=["A"]),
            ]
            self.run_engine(engine, root, checks, mode="FRESH", output_name="fresh")
            relevant_a.write_text("v2\n", encoding="utf-8")
            resumed = self.run_engine(engine, root, checks, mode="RESUME", output_name="resumed")

            self.assertEqual(resumed.checks_executed, ["A", "B"])
            self.assertIn("dependency_fingerprints_changed", resumed.invalidation_reasons["B"])

    def test_implementation_change_invalidates_checkpoint(self):
        engine = load_engine()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            implementation, relevant, log = self.make_root(root)
            checks = [self.make_check(0, "A", implementation, relevant, log)]
            self.run_engine(engine, root, checks, mode="FRESH", output_name="fresh")
            implementation.write_text(
                implementation.read_text(encoding="utf-8") + "\n# implementation v2\n",
                encoding="utf-8",
            )
            resumed = self.run_engine(engine, root, checks, mode="RESUME", output_name="resumed")

            self.assertEqual(resumed.checks_executed, ["A"])
            self.assertIn("implementation_manifest_changed", resumed.invalidation_reasons["A"])

    def test_nested_file_change_in_declared_directory_invalidates_checkpoint(self):
        engine = load_engine()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            implementation, relevant, log = self.make_root(root)
            nested = root / "surface" / "nested" / "value.txt"
            nested.parent.mkdir(parents=True)
            nested.write_text("v1\n", encoding="utf-8")
            check = self.make_check(0, "A", implementation, relevant, log)
            check["input_contract"] = {
                "mode": "explicit",
                "paths": [str(root / "surface")],
            }
            self.run_engine(engine, root, [check], mode="FRESH", output_name="fresh")
            nested.write_text("v2\n", encoding="utf-8")
            resumed = self.run_engine(
                engine, root, [check], mode="RESUME", output_name="resumed"
            )

            self.assertEqual(resumed.checks_executed, ["A"])
            self.assertIn("input_manifest_changed", resumed.invalidation_reasons["A"])

    def test_unadmitted_checkpoint_policy_never_reuses(self):
        engine = load_engine()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            implementation, relevant, log = self.make_root(root)
            check = self.make_check(0, "A", implementation, relevant, log)
            check["checkpoint_policy"] = {"mode": "disabled"}
            self.run_engine(engine, root, [check], mode="FRESH", output_name="fresh")
            resumed = self.run_engine(
                engine, root, [check], mode="RESUME", output_name="resumed"
            )

            self.assertEqual(resumed.checks_executed, ["A"])
            self.assertIn("checkpoint_reuse_not_admitted", resumed.invalidation_reasons["A"])

    def test_corrupt_and_incomplete_checkpoints_fail_closed(self):
        engine = load_engine()
        for payload in ("not json\n", '{"schema":"wrong"}\n'):
            with self.subTest(payload=payload), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                implementation, relevant, log = self.make_root(root)
                checks = [self.make_check(0, "A", implementation, relevant, log)]
                checkpoint_dir = root / "checkpoints"
                checkpoint_dir.mkdir()
                (checkpoint_dir / "A.json").write_text(payload, encoding="utf-8")
                resumed = self.run_engine(engine, root, checks, mode="RESUME", output_name="resumed")

                self.assertEqual(resumed.checks_executed, ["A"])
                self.assertEqual(resumed.checkpoints_reused, [])
                self.assertTrue(resumed.invalidation_reasons["A"])

    def test_material_environment_change_invalidates_checkpoint(self):
        engine = load_engine()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            implementation, relevant, log = self.make_root(root)
            checks = [
                self.make_check(
                    0,
                    "A",
                    implementation,
                    relevant,
                    log,
                    environment=["SHADOW_MATERIAL_ENV"],
                )
            ]
            self.run_engine(
                engine,
                root,
                checks,
                mode="FRESH",
                output_name="fresh",
                environment={"SHADOW_MATERIAL_ENV": "one"},
            )
            resumed = self.run_engine(
                engine,
                root,
                checks,
                mode="RESUME",
                output_name="resumed",
                environment={"SHADOW_MATERIAL_ENV": "two"},
            )

            self.assertEqual(resumed.checks_executed, ["A"])
            self.assertIn("environment_changed", resumed.invalidation_reasons["A"])

    def test_material_tool_identity_change_invalidates_checkpoint(self):
        engine = load_engine()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            implementation, relevant, log = self.make_root(root)
            checks = [self.make_check(0, "A", implementation, relevant, log)]
            with mock.patch.object(
                engine,
                "_tool_identity",
                return_value={"path": "python", "reusable": True, "version": "v1"},
            ):
                self.run_engine(engine, root, checks, mode="FRESH", output_name="fresh")
            with mock.patch.object(
                engine,
                "_tool_identity",
                return_value={"path": "python", "reusable": True, "version": "v2"},
            ):
                resumed = self.run_engine(
                    engine, root, checks, mode="RESUME", output_name="resumed"
                )

            self.assertEqual(resumed.checks_executed, ["A"])
            self.assertIn("tool_identity_changed", resumed.invalidation_reasons["A"])

    def test_unknown_applicability_and_prior_fail_never_reuse(self):
        engine = load_engine()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            implementation, relevant, log = self.make_root(root)
            unknown = [
                self.make_check(
                    0,
                    "unknown",
                    implementation,
                    relevant,
                    log,
                    applicability={"mode": "unknown"},
                )
            ]
            first = self.run_engine(engine, root, unknown, mode="FRESH", output_name="unknown-fresh")
            second = self.run_engine(engine, root, unknown, mode="RESUME", output_name="unknown-resume")
            self.assertEqual(first.pass_checks, ["unknown"])
            self.assertEqual(second.checks_executed, ["unknown"])
            self.assertIn("applicability_not_proven", second.invalidation_reasons["unknown"])

            failing = [self.make_check(0, "failure", implementation, relevant, log, status="fail")]
            self.run_engine(engine, root, failing, mode="FRESH", output_name="fail-fresh")
            failed_resume = self.run_engine(engine, root, failing, mode="RESUME", output_name="fail-resume")
            self.assertEqual(failed_resume.checks_executed, ["failure"])
            self.assertIn("stored_result_not_pass", failed_resume.invalidation_reasons["failure"])

    def test_resumed_semantics_equal_fresh_semantics(self):
        engine = load_engine()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            implementation, relevant, log = self.make_root(root)
            second_input = root / "inputs" / "second.txt"
            second_input.write_text("stable\n", encoding="utf-8")
            checks = [
                self.make_check(0, "A", implementation, relevant, log),
                self.make_check(1, "B", implementation, second_input, log, status="fail"),
                self.make_check(2, "C", implementation, second_input, log, dependencies=["B"]),
                self.make_check(3, "D", implementation, second_input, log),
            ]
            fresh = self.run_engine(engine, root, checks, mode="FRESH", output_name="fresh")
            resumed = self.run_engine(engine, root, checks, mode="RESUME", output_name="resumed")

            semantic_fields = (
                "pass_checks",
                "primary_failures",
                "blocked_checks",
                "blocked_dependency_map",
                "infrastructure_errors",
                "complete_safe_failure_frontier",
            )
            for field in semantic_fields:
                self.assertEqual(getattr(resumed, field), getattr(fresh, field), field)
            self.assertEqual(resumed.checkpoints_reused, ["A", "D"])


class CliTests(unittest.TestCase):
    def test_validate_registry_cli_reports_exact_live_population(self):
        """The usable CLI must prove its live canonical population before running."""
        completed = subprocess.run(
            [
                sys.executable,
                str(ENGINE_PATH),
                "validate-registry",
                "--repo-root",
                str(ROOT),
                "--registry",
                str(ROOT / "scripts" / "verify-package-shadow-registry.json"),
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "PASS")
        self.assertEqual(payload["authority"], "NONE")
        self.assertEqual(payload["check_count"], 105)
        self.assertEqual(payload["command_check_count"], 104)

    def test_run_cli_writes_non_authoritative_failure_frontier(self):
        """The command-line product must persist typed frontier evidence."""
        engine = load_engine()
        registry_tests = RegistryTests()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            compact = registry_tests.valid_compact_registry(root)
            (root / "scripts" / "alpha.sh").write_text(
                "#!/usr/bin/env bash\nprintf 'alpha fail\\n'\nexit 1\n",
                encoding="utf-8",
            )
            (root / "scripts" / "bravo.sh").write_text(
                "#!/usr/bin/env bash\nprintf 'bravo pass\\n'\n",
                encoding="utf-8",
            )
            (root / "tests").mkdir()
            (root / "tests" / "charlie.test.sh").write_text(
                "#!/usr/bin/env bash\nprintf 'charlie fail\\n'\nexit 1\n",
                encoding="utf-8",
            )
            registry_path = root / "registry.json"
            registry_path.write_text(
                json.dumps(compact), encoding="utf-8", newline="\n"
            )
            output_dir = root / "evidence"
            completed = subprocess.run(
                [
                    sys.executable,
                    str(ENGINE_PATH),
                    "run",
                    "--repo-root",
                    str(root),
                    "--registry",
                    str(registry_path),
                    "--output-dir",
                    str(output_dir),
                    "--timeout-seconds",
                    "5",
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                check=False,
            )
            self.assertEqual(completed.returncode, 1, completed.stderr)
            report = json.loads((output_dir / "report.json").read_text(encoding="utf-8"))
        self.assertEqual(report["authority"], "NONE")
        self.assertEqual(report["primary_failures"], ["script.alpha", "test.charlie"])
        self.assertEqual(report["blocked_checks"], ["script.bravo"])
        self.assertEqual(report["blocked_dependency_map"], {"script.bravo": ["script.alpha"]})

    def test_run_cli_can_resume_only_exact_pass_checkpoints(self):
        """CLI resume must expose reuse while retaining authority NONE."""
        registry_tests = RegistryTests()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            compact = registry_tests.valid_compact_registry(root)
            compact["composite"]["checkpoint_policy"] = {
                "mode": "exact_declared_inputs"
            }
            compact["overrides"].update(
                {
                    "script.alpha": {
                        "checkpoint_policy": {"mode": "exact_declared_inputs"}
                    },
                    "script.bravo": {
                        "dependencies": ["script.alpha"],
                        "checkpoint_policy": {"mode": "exact_declared_inputs"},
                    },
                    "test.charlie": {
                        "checkpoint_policy": {"mode": "exact_declared_inputs"}
                    },
                }
            )
            (root / "scripts" / "alpha.sh").write_text(
                "#!/usr/bin/env bash\nprintf 'alpha pass\\n'\n", encoding="utf-8"
            )
            (root / "scripts" / "bravo.sh").write_text(
                "#!/usr/bin/env bash\nprintf 'bravo pass\\n'\n", encoding="utf-8"
            )
            (root / "tests").mkdir()
            (root / "tests" / "charlie.test.sh").write_text(
                "#!/usr/bin/env bash\nprintf 'charlie pass\\n'\n", encoding="utf-8"
            )
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            subprocess.run(["git", "add", "."], cwd=root, check=True)
            registry_path = root / "registry.json"
            registry_path.write_text(json.dumps(compact), encoding="utf-8", newline="\n")
            checkpoint_dir = root / "checkpoints"

            def invoke(output: str, resume: bool) -> subprocess.CompletedProcess[str]:
                command = [
                    sys.executable,
                    str(ENGINE_PATH),
                    "run",
                    "--repo-root",
                    str(root),
                    "--registry",
                    str(registry_path),
                    "--output-dir",
                    str(root / output),
                    "--checkpoint-dir",
                    str(checkpoint_dir),
                    "--timeout-seconds",
                    "5",
                ]
                if resume:
                    command.append("--resume")
                return subprocess.run(
                    command,
                    cwd=ROOT,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    check=False,
                )

            fresh = invoke("fresh", False)
            resumed = invoke("resumed", True)
            self.assertEqual(fresh.returncode, 0, fresh.stderr)
            self.assertEqual(resumed.returncode, 0, resumed.stderr)
            report = json.loads((root / "resumed" / "report.json").read_text(encoding="utf-8"))

        self.assertEqual(report["mode"], "RESUME")
        self.assertEqual(report["authority"], "NONE")
        self.assertEqual(
            report["checkpoints_reused"],
            ["canonical.inline-preflight", "script.alpha", "script.bravo", "test.charlie"],
        )
        self.assertEqual(report["checks_executed"], [])


if __name__ == "__main__":
    unittest.main()
