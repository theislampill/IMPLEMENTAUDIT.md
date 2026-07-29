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
