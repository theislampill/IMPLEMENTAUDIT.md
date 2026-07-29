#!/usr/bin/env python3
"""Focused tests for controller-owned qualification evidence production."""
from __future__ import annotations

import json
import copy
import hashlib
import os
import pathlib
import subprocess
import tempfile

import provisional_integration as integration
import qualification_evidence_producer as producer


HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parent


def _mock_bash_binding():
    empty = hashlib.sha256(b"").hexdigest()
    return {
        "path": r"C:\Program Files\Git\bin\bash.exe",
        "canonical_path": r"C:\Program Files\Git\bin\bash.exe",
        "sha256": "f" * 64,
        "byte_length": 1,
        "file_identity": {
            "device": 1, "inode": 2, "mode": 32768,
            "size": 1, "mtime_ns": 3,
        },
        "version_argv": [
            r"C:\Program Files\Git\bin\bash.exe", "--version"],
        "version_exit_code": 0,
        "version_stdout": "mock bash\n",
        "version_stdout_sha256":
            hashlib.sha256(b"mock bash\n").hexdigest(),
        "version_stderr": "",
        "version_stderr_sha256": empty,
    }


def _assert_closed_failure_root(root, reason, *, expected_inventory):
    expected = {
        "package-start.json",
        "package-command.stdout.log",
        "package-command.stderr.log",
        "package-terminal.json",
        "package-report.json",
        "package.stdout.log",
        "package.stderr.log",
        "package-evidence-manifest.json",
    }
    assert {path.name for path in root.iterdir()} == expected
    start = json.loads(
        (root / "package-start.json").read_text(encoding="utf-8"))
    assert start["attempt"] == 1
    assert start["closed_stdin"] is True
    assert start["argv"][1:] == ["scripts/verify-package.sh"]
    terminal = json.loads(
        (root / "package-terminal.json").read_text(encoding="utf-8"))
    assert terminal["status"] in {"FAIL", "INVALID", "ERROR"}
    assert terminal["reason_code"] == reason
    assert terminal["attempt"] == 1
    assert terminal["child"]["pid"] > 0
    assert terminal["child"]["duration_seconds"] >= 0
    assert terminal["partial_artifact_inventory"] == expected_inventory
    report = json.loads(
        (root / "package-report.json").read_text(encoding="utf-8"))
    assert report["status"] == terminal["status"]
    assert report["reason_code"] == reason
    assert report["terminal_sha256"] == hashlib.sha256(
        (root / "package-terminal.json").read_bytes()).hexdigest()
    manifest = json.loads(
        (root / "package-evidence-manifest.json").read_text(
            encoding="utf-8"))
    observed = []
    for name in (
            "package-start.json",
            "package-command.stdout.log",
            "package-command.stderr.log",
            "package-terminal.json",
            "package-report.json",
            "package.stdout.log",
            "package.stderr.log"):
        raw = (root / name).read_bytes()
        observed.append({
            "path": name, "byte_length": len(raw),
            "sha256": hashlib.sha256(raw).hexdigest(),
        })
    assert manifest["files"] == observed
    independently = integration._validate_failed_gate_evidence(
        "package", root, allow_test_evidence=True)
    assert independently == {
        "name": "package",
        "semantic_status": terminal["status"],
        "reason_code": reason,
        "attempt": 1,
    }


def _rebind_failed_root(root):
    terminal_path = root / "package-terminal.json"
    report_path = root / "package-report.json"
    manifest_path = root / "package-evidence-manifest.json"
    terminal_raw = terminal_path.read_bytes()
    report = json.loads(report_path.read_text(encoding="utf-8"))
    report["terminal_sha256"] = hashlib.sha256(
        terminal_raw).hexdigest()
    report_path.write_bytes(producer._encoded(report))
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    for row in manifest["files"]:
        payload = (root / row["path"]).read_bytes()
        row["byte_length"] = len(payload)
        row["sha256"] = hashlib.sha256(payload).hexdigest()
    manifest_path.write_bytes(producer._encoded(manifest))


def _assert_production_failure_transactions(
        base, checkout, sha, tree, archive):
    original_popen = producer.subprocess.Popen
    original_binding = producer._production_bash_binding
    original_manifest = producer._manifest_for_archive
    original_validate = integration.validate_package_archive
    original_write_new = producer._write_new
    calls = []
    behavior = {}

    class FakeProcess:
        def __init__(self, argv, **kwargs):
            calls.append(list(argv))
            self.pid = 70000 + len(calls)
            self.returncode = behavior["exit_code"]
            self.environment = kwargs["env"]

        def communicate(self):
            action = behavior.get("action")
            if action is not None:
                action(self.environment)
            if behavior.get("communicate_error"):
                raise OSError("mock communicate failure")
            return b"mock child stdout\n", b"mock child stderr\n"

    def popen(argv, **kwargs):
        if len(argv) >= 2 and argv[1] == "scripts/verify-package.sh":
            return FakeProcess(argv, **kwargs)
        return original_popen(argv, **kwargs)

    def invoke(label, *, exit_code=0, action=None, reason,
               manifest=None, validate=None, communicate_error=False):
        root = base / f"production-{label}"
        behavior.clear()
        behavior.update(
            exit_code=exit_code, action=action,
            communicate_error=communicate_error)
        if manifest is not None:
            producer._manifest_for_archive = manifest
        else:
            producer._manifest_for_archive = original_manifest
        if validate is not None:
            integration.validate_package_archive = validate
        else:
            integration.validate_package_archive = original_validate
        before = len(calls)
        expect_error(
            reason,
            lambda: producer.run_gate(
                "package", repo_root=checkout, evidence_root=root,
                target_sha=sha, target_tree=tree,
                qualification_scope="TOOLING_EXACT_SHA",
                prior_evidence_sha256="c" * 64))
        assert len(calls) == before + 1
        return root

    def write_pair(environment, left=archive, right=archive):
        pathlib.Path(
            environment["REPRO_RETAINED_ASSET_A"]).write_bytes(left)
        pathlib.Path(
            environment["REPRO_RETAINED_ASSET_B"]).write_bytes(right)

    def write_a(environment):
        pathlib.Path(
            environment["REPRO_RETAINED_ASSET_A"]).write_bytes(archive)

    def write_b(environment):
        pathlib.Path(
            environment["REPRO_RETAINED_ASSET_B"]).write_bytes(archive)

    producer.subprocess.Popen = popen
    producer._production_bash_binding = _mock_bash_binding
    try:
        root = invoke(
            "exit23", exit_code=23, reason="CHILD_NONZERO_EXIT")
        _assert_closed_failure_root(
            root, "CHILD_NONZERO_EXIT", expected_inventory=[
                producer._missing_export_row(
                    "A", root.parent /
                    f".{root.name}-package-export" / "asset-a.skill"),
                producer._missing_export_row(
                    "B", root.parent /
                    f".{root.name}-package-export" / "asset-b.skill"),
                producer._missing_export_row(
                    "A_MANIFEST", root.parent /
                    f".{root.name}-package-export" /
                    "asset-a-entry-manifest.json"),
                producer._missing_export_row(
                    "B_MANIFEST", root.parent /
                    f".{root.name}-package-export" /
                    "asset-b-entry-manifest.json"),
            ])
        before = len(calls)
        expect_error(
            "already",
            lambda: producer.run_gate(
                "package", repo_root=checkout, evidence_root=root,
                target_sha=sha, target_tree=tree,
                qualification_scope="TOOLING_EXACT_SHA",
                prior_evidence_sha256="c" * 64))
        assert len(calls) == before

        root = invoke(
            "only-a", action=write_a,
            reason="PACKAGE_EXPORT_PAIR_INCOMPLETE")
        export_a = root.parent / \
            f".{root.name}-package-export" / "asset-a.skill"
        retained_a = export_a.read_bytes()
        terminal = json.loads(
            (root / "package-terminal.json").read_text(encoding="utf-8"))
        _assert_closed_failure_root(
            root, "PACKAGE_EXPORT_PAIR_INCOMPLETE",
            expected_inventory=terminal["partial_artifact_inventory"])
        assert terminal["partial_artifact_inventory"][0]["sha256"] == \
            hashlib.sha256(archive).hexdigest()
        assert terminal["partial_artifact_inventory"][1]["state"] == \
            "MISSING"
        assert export_a.read_bytes() == retained_a == archive
        export_a.write_bytes(retained_a + b"tamper")
        expect_error(
            "inventory",
            lambda: integration._validate_failed_gate_evidence(
                "package", root, allow_test_evidence=True))

        root = invoke(
            "only-b", action=write_b,
            reason="PACKAGE_EXPORT_PAIR_INCOMPLETE")
        terminal = json.loads(
            (root / "package-terminal.json").read_text(encoding="utf-8"))
        _assert_closed_failure_root(
            root, "PACKAGE_EXPORT_PAIR_INCOMPLETE",
            expected_inventory=terminal["partial_artifact_inventory"])
        terminal["partial_artifact_inventory"].pop()
        (root / "package-terminal.json").write_bytes(
            producer._encoded(terminal))
        _rebind_failed_root(root)
        expect_error(
            "inventory coverage",
            lambda: integration._validate_failed_gate_evidence(
                "package", root, allow_test_evidence=True))

        root = invoke(
            "drift", action=lambda env: write_pair(
                env, archive, archive + b"x"),
            reason="PACKAGE_EXPORT_DRIFT")
        terminal = json.loads(
            (root / "package-terminal.json").read_text(encoding="utf-8"))
        _assert_closed_failure_root(
            root, "PACKAGE_EXPORT_DRIFT",
            expected_inventory=terminal["partial_artifact_inventory"])

        root = invoke(
            "invalid-archive",
            action=lambda env: write_pair(env, b"not zip", b"not zip"),
            reason="PACKAGE_ARCHIVE_INVALID")
        terminal = json.loads(
            (root / "package-terminal.json").read_text(encoding="utf-8"))
        _assert_closed_failure_root(
            root, "PACKAGE_ARCHIVE_INVALID",
            expected_inventory=terminal["partial_artifact_inventory"])

        def write_alias(environment):
            first = pathlib.Path(
                environment["REPRO_RETAINED_ASSET_A"])
            second = pathlib.Path(
                environment["REPRO_RETAINED_ASSET_B"])
            first.write_bytes(archive)
            os.link(first, second)
        try:
            root = invoke(
                "alias", action=write_alias,
                reason="PACKAGE_EXPORT_ALIAS")
        except OSError:
            root = None
        if root is not None:
            terminal = json.loads(
                (root / "package-terminal.json").read_text(
                    encoding="utf-8"))
            _assert_closed_failure_root(
                root, "PACKAGE_EXPORT_ALIAS",
                expected_inventory=
                    terminal["partial_artifact_inventory"])

        manifest_calls = 0
        def divergent_manifest(repo_root, target_sha, target_tree, raw):
            nonlocal manifest_calls
            manifest_calls += 1
            result = original_manifest(
                repo_root, target_sha, target_tree, raw)
            return result if manifest_calls == 1 else result + b" "
        root = invoke(
            "manifest-drift", action=write_pair,
            reason="PACKAGE_MANIFEST_DRIFT",
            manifest=divergent_manifest)
        terminal = json.loads(
            (root / "package-terminal.json").read_text(encoding="utf-8"))
        _assert_closed_failure_root(
            root, "PACKAGE_MANIFEST_DRIFT",
            expected_inventory=terminal["partial_artifact_inventory"])

        root = invoke(
            "manifest-invalid", action=write_pair,
            reason="PACKAGE_MANIFEST_INVALID",
            manifest=lambda *_args: b"{")
        terminal = json.loads(
            (root / "package-terminal.json").read_text(encoding="utf-8"))
        _assert_closed_failure_root(
            root, "PACKAGE_MANIFEST_INVALID",
            expected_inventory=terminal["partial_artifact_inventory"])

        def invalid_source(*_args, **_kwargs):
            raise ValueError("mock source mismatch")
        root = invoke(
            "source-invalid", action=write_pair,
            reason="PACKAGE_SOURCE_BINDING_INVALID",
            validate=invalid_source)
        terminal = json.loads(
            (root / "package-terminal.json").read_text(encoding="utf-8"))
        _assert_closed_failure_root(
            root, "PACKAGE_SOURCE_BINDING_INVALID",
            expected_inventory=terminal["partial_artifact_inventory"])

        root = invoke(
            "communicate-error", action=write_pair,
            reason="CHILD_COMMUNICATION_ERROR",
            communicate_error=True)
        terminal = json.loads(
            (root / "package-terminal.json").read_text(encoding="utf-8"))
        _assert_closed_failure_root(
            root, "CHILD_COMMUNICATION_ERROR",
            expected_inventory=terminal["partial_artifact_inventory"])

        start_root = base / "production-start-write-fault"
        before = len(calls)
        def fail_start(path, payload):
            if pathlib.Path(path).name == "package-start.json":
                raise OSError("mock start write fault")
            return original_write_new(path, payload)
        producer._write_new = fail_start
        expect_error(
            "start write fault",
            lambda: producer.run_gate(
                "package", repo_root=checkout,
                evidence_root=start_root,
                target_sha=sha, target_tree=tree,
                qualification_scope="TOOLING_EXACT_SHA",
                prior_evidence_sha256="c" * 64))
        assert len(calls) == before
        producer._write_new = original_write_new

        for label, failed_name in (
                ("raw-log-write-fault",
                 "package-command.stdout.log"),
                ("terminal-write-fault", "package-terminal.json")):
            root = base / f"production-{label}"
            behavior.clear()
            behavior.update(
                exit_code=0, action=write_pair,
                communicate_error=False)
            before = len(calls)
            def fail_selected(path, payload, *,
                              failed_name=failed_name):
                if pathlib.Path(path).name == failed_name:
                    raise OSError(f"mock {failed_name} write fault")
                return original_write_new(path, payload)
            producer._write_new = fail_selected
            expect_error(
                "publication",
                lambda root=root: producer.run_gate(
                    "package", repo_root=checkout,
                    evidence_root=root,
                    target_sha=sha, target_tree=tree,
                    qualification_scope="TOOLING_EXACT_SHA",
                    prior_evidence_sha256="c" * 64))
            assert len(calls) == before + 1
            journal = json.loads(
                (root / "package-failure-journal.json").read_text(
                    encoding="utf-8"))
            assert journal["status"] == "ERROR"
            assert journal["attempt"] == 1
            assert journal["child_consumed"] is True
            assert any(
                row["path"] == "package-start.json" and
                row["state"] == "REGULAR" and
                row["sha256"] == hashlib.sha256(
                    (root / "package-start.json").read_bytes()).hexdigest()
                for row in journal["observed_files"])
            assert journal["stage"] in {
                "RAW_LOG_PUBLICATION",
                "SUCCESS_EVIDENCE_PUBLICATION",
            }
            producer._write_new = original_write_new

        success_root = base / "production-success"
        behavior.clear()
        behavior.update(
            exit_code=0, action=write_pair,
            communicate_error=False)
        before = len(calls)
        manifest_sha = producer.run_gate(
            "package", repo_root=checkout,
            evidence_root=success_root,
            target_sha=sha, target_tree=tree,
            qualification_scope="TOOLING_EXACT_SHA",
            prior_evidence_sha256="c" * 64)
        assert len(calls) == before + 1
        success_terminal = json.loads(
            (success_root / "package-terminal.json").read_text(
                encoding="utf-8"))
        assert success_terminal["status"] == "PASS"
        assert success_terminal["attempt"] == 1
        assert success_terminal["child"]["exit_code"] == 0
        success_manifest = json.loads(
            (success_root / "package-evidence-manifest.json").read_text(
                encoding="utf-8"))
        assert manifest_sha == hashlib.sha256(
            producer._encoded(success_manifest)).hexdigest()
        assert {row["path"] for row in success_manifest["files"]} == {
            "package-start.json",
            "package-terminal.json",
            "package-report.json",
            "package.stdout.log",
            "package.stderr.log",
            "package-command.stdout.log",
            "package-command.stderr.log",
            "package-retained.skill",
            "package-entry-manifest.json",
            "package-repro-a.skill",
            "package-repro-b.skill",
            "package-repro-a-entry-manifest.json",
            "package-repro-b-entry-manifest.json",
        }
        before = len(calls)
        expect_error(
            "already",
            lambda: producer.run_gate(
                "package", repo_root=checkout,
                evidence_root=success_root,
                target_sha=sha, target_tree=tree,
                qualification_scope="TOOLING_EXACT_SHA",
                prior_evidence_sha256="c" * 64))
        assert len(calls) == before
    finally:
        producer._write_new = original_write_new
        producer.subprocess.Popen = original_popen
        producer._production_bash_binding = original_binding
        producer._manifest_for_archive = original_manifest
        integration.validate_package_archive = original_validate


def _assert_deterministic_failure_transaction(
        base, checkout, sha, tree):
    original_popen = producer.subprocess.Popen
    original_binding = producer._production_bash_binding
    calls = []

    class FakeProcess:
        def __init__(self, argv, **_kwargs):
            calls.append(list(argv))
            self.pid = 81000 + len(calls)
            self.returncode = 23

        def communicate(self):
            return b"focused failure\n", b""

    def popen(argv, **kwargs):
        if argv[0] == "git":
            return original_popen(argv, **kwargs)
        return FakeProcess(argv, **kwargs)

    root = base / "production-deterministic-exit23"
    producer.subprocess.Popen = popen
    producer._production_bash_binding = _mock_bash_binding
    try:
        expect_error(
            "CHILD_NONZERO_EXIT",
            lambda: producer.run_gate(
                "deterministic", repo_root=checkout,
                evidence_root=root, target_sha=sha, target_tree=tree,
                qualification_scope="FROZEN_CAMPAIGNS",
                qualified_input_sha256="a" * 64,
                surfaces_sha256="b" * 64,
                prior_evidence_sha256="c" * 64))
        assert len(calls) == 1
        terminal = json.loads(
            (root / "deterministic-terminal.json").read_text(
                encoding="utf-8"))
        assert terminal["status"] == "FAIL"
        assert terminal["reason_code"] == "CHILD_NONZERO_EXIT"
        assert terminal["checks"][0] == terminal["child"]
        assert {
            path.name for path in root.iterdir()
        } == {
            "deterministic-start.json",
            "deterministic-00-compile.stdout.log",
            "deterministic-00-compile.stderr.log",
            "deterministic-terminal.json",
            "deterministic-report.json",
            "deterministic.stdout.log",
            "deterministic.stderr.log",
            "deterministic-evidence-manifest.json",
        }
        assert integration._validate_failed_gate_evidence(
            "deterministic", root,
            allow_test_evidence=True)["semantic_status"] == "FAIL"
        before = len(calls)
        expect_error(
            "already",
            lambda: producer.run_gate(
                "deterministic", repo_root=checkout,
                evidence_root=root, target_sha=sha, target_tree=tree,
                qualification_scope="FROZEN_CAMPAIGNS",
                qualified_input_sha256="a" * 64,
                surfaces_sha256="b" * 64,
                prior_evidence_sha256="c" * 64))
        assert len(calls) == before
    finally:
        producer.subprocess.Popen = original_popen
        producer._production_bash_binding = original_binding


def expect_error(fragment, action):
    try:
        action()
    except (OSError, TypeError, ValueError) as exc:
        assert fragment.lower() in str(exc).lower(), str(exc)
    else:
        raise AssertionError(f"expected error containing {fragment!r}")


def main():
    if os.name == "nt":
        expected = pathlib.Path(
            r"C:\Program Files\Git\bin\bash.exe").resolve(strict=True)
        original_which = producer.shutil.which
        producer.shutil.which = lambda _name: \
            r"C:\Windows\System32\bash.exe"
        try:
            resolved = producer._resolved_argv(["bash"])
        finally:
            producer.shutil.which = original_which
        assert pathlib.Path(resolved[0]) == expected, resolved
        binding = producer._production_bash_binding()
        assert binding["canonical_path"] == str(expected)
        assert binding["path"] == str(expected)
        assert binding["version_argv"] == [str(expected), "--version"]
        assert binding["version_exit_code"] == 0
        assert binding["sha256"] == hashlib.sha256(
            expected.read_bytes()).hexdigest()
        assert binding["byte_length"] == expected.stat().st_size

    with tempfile.TemporaryDirectory(
            prefix="qualification-producer-") as tmp:
        base = pathlib.Path(tmp)
        checkout = base / "checkout"
        subprocess.run(
            ["git", "clone", "--quiet", "--no-hardlinks",
             str(REPO), str(checkout)],
            stdin=subprocess.DEVNULL, check=True)
        sha = subprocess.check_output(
            ["git", "-C", str(checkout), "rev-parse", "HEAD"],
            text=True).strip()
        tree = subprocess.check_output(
            ["git", "-C", str(checkout), "show", "-s", "--format=%T",
             "HEAD"], text=True).strip()
        tooling_hash, tooling_identity = producer._qualification_identity(
            "package", checkout, sha, tree,
            qualification_scope="TOOLING_EXACT_SHA")
        assert len(tooling_hash) == 64
        assert tooling_identity["qualification_scope"] == \
            "TOOLING_EXACT_SHA"
        assert tooling_identity["target_sha"] == sha
        assert tooling_identity["target_tree"] == tree
        assert [row["path"] for row in
                tooling_identity["tooling_source_manifest"]["files"]] == \
            list(producer.TOOLING_SOURCE_PATHS)
        expect_error(
            "not permitted",
            lambda: producer._qualification_identity(
                "package", checkout, sha, tree,
                qualification_scope="TOOLING_EXACT_SHA",
                qualified_input_sha256="a" * 64,
                surfaces_sha256="b" * 64))
        expect_error(
            "scope",
            lambda: producer._qualification_identity(
                "package", checkout, sha, tree,
                qualification_scope="FROZEN_CAMPAIGNS",
                qualified_input_sha256="a" * 64,
                surfaces_sha256="b" * 64))
        expect_error(
            "required",
            lambda: producer._qualification_identity(
                "deterministic", checkout, sha, tree,
                qualification_scope="FROZEN_CAMPAIGNS",
                qualified_input_sha256="a" * 64))
        frozen_hash, frozen_identity = producer._qualification_identity(
            "deterministic", checkout, sha, tree,
            qualification_scope="FROZEN_CAMPAIGNS",
            qualified_input_sha256="a" * 64,
            surfaces_sha256="b" * 64)
        assert frozen_hash == "a" * 64
        assert frozen_identity == {
            "qualification_scope": "FROZEN_CAMPAIGNS",
            "target_sha": sha,
            "target_tree": tree,
            "campaign_qualified_input_sha256": "a" * 64,
            "evaluated_surfaces_sha256": "b" * 64,
        }
        export_root = base / "package-export"
        export_root.mkdir()
        export_a = export_root / "a.skill"
        export_b = export_root / "b.skill"
        expect_error(
            "both",
            lambda: producer._package_export_contract(
                checkout, None, None))
        expect_error(
            "both",
            lambda: producer._package_export_contract(
                checkout, export_a, None))
        expect_error(
            "distinct",
            lambda: producer._package_export_contract(
                checkout, export_a, export_a))
        export_a.write_bytes(b"existing")
        expect_error(
            "already exists",
            lambda: producer._package_export_contract(
                checkout, export_a, export_b))
        export_a.unlink()
        selected_a, selected_b = producer._package_export_contract(
            checkout, export_a, export_b)
        assert selected_a == export_a.resolve()
        assert selected_b == export_b.resolve()
        export_a.write_bytes(b"same")
        export_b.write_bytes(b"different")
        expect_error(
            "differ",
            lambda: producer._read_exported_package_pair(
                export_a, export_b))
        export_b.write_bytes(b"same")
        first, second = producer._read_exported_package_pair(
            export_a, export_b)
        assert first == second == b"same"
        shell_contract = base / "shell-export-contract"
        shell_contract.mkdir()
        shell_a = shell_contract / "a.skill"
        shell_b = shell_contract / "b.skill"
        bash = (r"C:\Program Files\Git\bin\bash.exe"
                if os.name == "nt" else "bash")

        def export_control(asset_a_value, asset_b_value):
            environment = os.environ.copy()
            if asset_a_value is not None:
                environment["REPRO_RETAINED_ASSET_A"] = str(asset_a_value)
            if asset_b_value is not None:
                environment["REPRO_RETAINED_ASSET_B"] = str(asset_b_value)
            return subprocess.run(
                [bash, str(
                    REPO / "tests" /
                    "reproducible-release-asset.test.sh")],
                cwd=REPO, stdin=subprocess.DEVNULL,
                capture_output=True, check=False, env=environment)

        assert export_control(shell_a, None).returncode != 0
        assert not shell_a.exists()
        assert export_control(shell_a, shell_a).returncode != 0
        assert not shell_a.exists()
        shell_a.write_bytes(b"existing")
        assert export_control(shell_a, shell_b).returncode != 0
        assert not shell_b.exists()
        archive_raw, manifest_raw = producer._package(
            checkout, sha, tree)
        archive = base / "source-bound.skill"
        manifest = base / "source-bound-manifest.json"
        archive.write_bytes(archive_raw)
        manifest.write_bytes(manifest_raw)
        rows = integration.validate_package_archive(
            archive, manifest, sha, tree, repo_root=checkout)
        assert len(rows) == 43
        decoded = json.loads(manifest_raw)
        assert decoded["builder_source_path"] == \
            "scripts/build-release-asset.sh"
        _assert_production_failure_transactions(
            base, checkout, sha, tree, archive_raw)
        _assert_deterministic_failure_transaction(
            base, checkout, sha, tree)

        test_evidence = base / "test-only-evidence"
        producer.run_gate(
            "deterministic", repo_root=checkout,
            evidence_root=test_evidence, target_sha=sha,
            qualification_scope="FROZEN_CAMPAIGNS",
            target_tree=tree, qualified_input_sha256="a" * 64,
            surfaces_sha256="b" * 64,
            prior_evidence_sha256="c" * 64, test_only=True)
        expect_error(
            "evidence_mode",
            lambda: integration._validate_gate_evidence(
                "deterministic", test_evidence, "a" * 64,
                sha, tree, "b" * 64, "c" * 64,
                allow_test_evidence=False))
        expect_error(
            "external job evidence",
            lambda: producer.run_gate(
                "ci", repo_root=checkout,
                evidence_root=base / "production-ci-evidence",
                target_sha=sha, target_tree=tree,
                qualification_scope="TOOLING_EXACT_SHA",
                prior_evidence_sha256="c" * 64))
        workflow = subprocess.check_output(
            ["git", "-C", str(checkout), "show",
             f"{sha}:.github/workflows/validate.yml"])
        hosted = {
            "schema": "implementaudit-hosted-ci-provider-export-v1",
            "evidence_mode": "PRODUCTION",
            "provider": "github-actions",
            "workflow_path": ".github/workflows/validate.yml",
            "workflow_sha256": hashlib.sha256(workflow).hexdigest(),
            "run_id": 123, "attempt": 1,
            "head_sha": sha, "head_tree": tree,
            "event": "push", "ref": "refs/heads/test",
            "started_at": "2026-07-29T00:00:00Z",
            "completed_at": "2026-07-29T00:01:00Z",
            "conclusion": "success",
            "jobs": [{
                "name": "package", "job_id": 456,
                "conclusion": "success",
                "producer_identity": "owner-supplied-provider-export",
            }],
        }

        def raw(value):
            return (json.dumps(
                value, sort_keys=True, separators=(",", ":")) +
                "\n").encode()

        for label, mutate in (
                ("head", lambda value: value.update(head_sha="0" * 40)),
                ("workflow", lambda value: value.update(
                    workflow_sha256="0" * 64)),
                ("job-missing", lambda value: value.update(jobs=[])),
                ("job-duplicate", lambda value: value["jobs"].append(
                    copy.deepcopy(value["jobs"][0]))),
                ("conclusion", lambda value: value.update(
                    conclusion="failure")),
                ("coercion", lambda value: value.update(attempt=True))):
            changed = copy.deepcopy(hosted)
            mutate(changed)
            expect_error(
                "CI",
                lambda changed=changed, label=label: producer.run_gate(
                    "ci", repo_root=checkout,
                    evidence_root=base / f"bad-ci-{label}",
                    target_sha=sha, target_tree=tree,
                    qualification_scope="TOOLING_EXACT_SHA",
                    prior_evidence_sha256="c" * 64,
                    external_ci=raw(changed)))
        expect_error(
            "JSON",
            lambda: producer.run_gate(
                "ci", repo_root=checkout,
                evidence_root=base / "malformed-ci",
                target_sha=sha, target_tree=tree,
                qualification_scope="TOOLING_EXACT_SHA",
                prior_evidence_sha256="c" * 64,
                external_ci=b"{"))
        producer.run_gate(
            "ci", repo_root=checkout,
            evidence_root=base / "valid-hosted-ci",
            target_sha=sha, target_tree=tree,
            qualification_scope="TOOLING_EXACT_SHA",
            prior_evidence_sha256="c" * 64,
            external_ci=raw(hosted))

        (checkout / "untracked-drift").write_text(
            "drift\n", encoding="utf-8")
        expect_error(
            "dirty",
            lambda: producer.run_gate(
                "deterministic", repo_root=checkout,
                evidence_root=base / "dirty-evidence",
                target_sha=sha, target_tree=tree,
                qualification_scope="FROZEN_CAMPAIGNS",
                qualified_input_sha256="a" * 64,
                surfaces_sha256="b" * 64,
                prior_evidence_sha256="c" * 64))
    print("QUALIFICATION-EVIDENCE-PRODUCER-PASS")


if __name__ == "__main__":
    main()
