#!/usr/bin/env python3
"""Production-shaped tests for the custody-derived integration certificate."""
from __future__ import annotations

import copy
import atexit
import hashlib
import json
import io
import os
import pathlib
import shutil
import stat
import subprocess
import sys
import tempfile
import zipfile

import b3v4_campaign
import b3v4_rederive
import candidate_matrix_campaign
import candidate_matrix_rederive
import evaluated_surfaces as surfaces
import provisional_integration as integration
import qualification_evidence_producer as evidence_producer
import test_b3v4_rederive as b3_fixture
import test_candidate_matrix_rederive as matrix_fixture


def encoded(value):
    return (json.dumps(
        value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def write(path, value):
    path = pathlib.Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(value if isinstance(value, bytes) else encoded(value))


def _git(*args, text=False):
    return subprocess.run(
        ["git", "-C", str(HERE.parent), *args],
        stdin=subprocess.DEVNULL, capture_output=True, check=True,
        text=text).stdout


HERE = pathlib.Path(__file__).resolve().parent
TARGET_SHA = _git("rev-parse", "HEAD", text=True).strip()
TARGET_TREE = _git("show", "-s", "--format=%T", "HEAD", text=True).strip()
TARGET_FOUNDATION = {"commit": TARGET_SHA, "tree": TARGET_TREE}
_PRODUCER_REPO = None


def _producer_repo():
    global _PRODUCER_REPO
    if _PRODUCER_REPO is None:
        _PRODUCER_REPO = pathlib.Path(tempfile.mkdtemp(
            prefix="qualification-producer-checkout-"))
        subprocess.run(
            ["git", "clone", "--quiet", "--no-hardlinks",
             str(HERE.parent), str(_PRODUCER_REPO)],
            stdin=subprocess.DEVNULL, check=True)
        subprocess.run(
            ["git", "-C", str(_PRODUCER_REPO), "checkout", "--quiet",
             "--detach", TARGET_SHA],
            stdin=subprocess.DEVNULL, check=True)
        atexit.register(
            shutil.rmtree, _PRODUCER_REPO, ignore_errors=True)
    return _PRODUCER_REPO


def _package_bytes(source_sha, source_tree):
    names = _git(
        "ls-tree", "-r", "--name-only", source_sha,
        "skills/implementaudit", text=True).splitlines()
    payloads = {}
    for source_path in names:
        archive_path = source_path.removeprefix("skills/implementaudit/")
        _source, payload, _transform = \
            integration._source_bound_archive_payload(
                HERE.parent, source_sha, archive_path)
        payloads[archive_path] = payload
    for archive_path in (
            ".claude-plugin/plugin.json",
            ".claude-plugin/marketplace.json"):
        _source, payload, _transform = \
            integration._source_bound_archive_payload(
                HERE.parent, source_sha, archive_path)
        payloads[archive_path] = payload
    stream = io.BytesIO()
    with zipfile.ZipFile(
            stream, "w", compression=zipfile.ZIP_DEFLATED,
            compresslevel=9) as archive:
        for name in sorted(payloads):
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.create_system = 3
            info.create_version = 20
            info.extract_version = 20
            mode = 0o755 if name.startswith("scripts/") else 0o644
            info.external_attr = (stat.S_IFREG | mode) << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            info.extra = b""
            info.comment = b""
            archive.writestr(info, payloads[name])
    raw = stream.getvalue()
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        entries = [
            integration._zip_entry_row(info, archive.read(info))
            for info in archive.infolist()
        ]
    return raw, {
        "schema": integration.PACKAGE_MANIFEST_SCHEMA,
        "source_sha": source_sha,
        "source_tree": source_tree,
        "builder_source_path": "scripts/build-release-asset.sh",
        "builder_source_sha256": hashlib.sha256(_git(
            "show", f"{source_sha}:scripts/build-release-asset.sh")).hexdigest(),
        "entries": entries,
    }


def expect_error(fragment, action):
    try:
        action()
    except (OSError, TypeError, ValueError) as exc:
        if fragment is not None:
            assert fragment.lower() in str(exc).lower(), str(exc)
    else:
        raise AssertionError(f"expected failure containing {fragment!r}")


def _assert_production_bash_binding_boundary():
    binding = evidence_producer._production_bash_binding()
    frozen_identity = {
        "qualification_scope": "FROZEN_CAMPAIGNS",
        "target_sha": TARGET_SHA,
        "target_tree": TARGET_TREE,
        "campaign_qualified_input_sha256": "a" * 64,
        "evaluated_surfaces_sha256": "b" * 64,
    }
    deterministic = {
        "schema": "implementaudit-deterministic-terminal-v2",
        "gate": "deterministic",
        "qualified_input_sha256": "a" * 64,
        "exit_code": 0,
        "failed_checks": [],
        "qualification_scope": "FROZEN_CAMPAIGNS",
        "qualification_identity": frozen_identity,
        "bash_executable": binding,
        "status": "PASS",
        "attempt": 1,
        "checks": [],
    }
    for index, name in enumerate(integration.DETERMINISTIC_CHECKS):
        expected = list(integration.DETERMINISTIC_COMMANDS[name])
        if expected[0] == "bash":
            expected[0] = binding["canonical_path"]
        deterministic["checks"].append({
            "name": name,
            "argv": expected,
            "exit_code": 0,
            "started_at": "2026-07-29T00:00:00Z",
            "completed_at": "2026-07-29T00:00:01Z",
            "duration_seconds": 1.0,
            "pid": index + 1,
            "stdout_path":
                f"deterministic-{index:02d}-{name}.stdout.log",
            "stdout_sha256": hashlib.sha256(b"").hexdigest(),
            "stderr_path":
                f"deterministic-{index:02d}-{name}.stderr.log",
            "stderr_sha256": hashlib.sha256(b"").hexdigest(),
        })
    integration._validate_gate_terminal(
        "deterministic", deterministic, "a" * 64, {},
        evidence_mode="PRODUCTION")

    package_hashes = {
        "package-entry-manifest.json": "b" * 64,
        "package-retained.skill": "c" * 64,
        "package-repro-a.skill": "c" * 64,
        "package-repro-b.skill": "c" * 64,
        "package-repro-a-entry-manifest.json": "d" * 64,
        "package-repro-b-entry-manifest.json": "d" * 64,
        "package-command.stdout.log": "e" * 64,
        "package-command.stderr.log": "f" * 64,
    }
    tooling_identity = {
        "qualification_scope": "TOOLING_EXACT_SHA",
        "target_sha": TARGET_SHA,
        "target_tree": TARGET_TREE,
        "tooling_source_manifest": {},
        "tooling_source_manifest_sha256": "e" * 64,
    }
    package_reproducibility = {
        "selected_archive_path": "package-retained.skill",
        "selected_archive_sha256": "c" * 64,
        "assets": [{
            "label": label,
            "path": f"package-repro-{label.lower()}.skill",
            "sha256": "c" * 64,
            "manifest_path":
                f"package-repro-{label.lower()}-entry-manifest.json",
            "manifest_sha256": "d" * 64,
        } for label in ("A", "B")],
    }
    package = {
        "schema": "implementaudit-package-terminal-v2",
        "gate": "package",
        "qualified_input_sha256": "a" * 64,
        "exit_code": 0,
        "verification_passed": True,
        "package_manifest_sha256": "b" * 64,
        "argv": [
            binding["canonical_path"], "scripts/verify-package.sh"],
        "started_at": "2026-07-29T00:00:00.000000Z",
        "completed_at": "2026-07-29T00:00:01.000000Z",
        "duration_seconds": 1.0,
        "pid": 1,
        "status": "PASS",
        "attempt": 1,
        "qualification_scope": "TOOLING_EXACT_SHA",
        "qualification_identity": tooling_identity,
        "package_reproducibility": package_reproducibility,
        "bash_executable": binding,
    }
    package["child"] = {
        "argv": package["argv"],
        "pid": package["pid"],
        "started_at": package["started_at"],
        "completed_at": package["completed_at"],
        "duration_seconds": package["duration_seconds"],
        "exit_code": package["exit_code"],
        "stdout_path": "package-command.stdout.log",
        "stdout_sha256": package_hashes[
            "package-command.stdout.log"],
        "stderr_path": "package-command.stderr.log",
        "stderr_sha256": package_hashes[
            "package-command.stderr.log"],
        "child_completed": True,
        "communication_error": None,
        "termination_action": "NONE",
        "termination_started_at": None,
        "termination_completed_at": None,
    }
    integration._validate_gate_terminal(
        "package", package, "a" * 64,
        package_hashes,
        evidence_mode="PRODUCTION")

    mutations = (
        ("wrong path", lambda row: row.update(
            path=r"C:\Windows\System32\bash.exe")),
        ("wrong hash", lambda row: row.update(sha256="0" * 64)),
        ("wrong identity", lambda row: row["file_identity"].update(
            inode=row["file_identity"]["inode"] + 1)),
        ("wrong version", lambda row: row.update(
            version_stdout=row["version_stdout"] + "forged\n")),
        ("WSL basename", lambda row: row.update(
            path="bash.exe", canonical_path="bash.exe",
            version_argv=["bash.exe", "--version"])),
    )
    for label, mutate in mutations:
        changed = copy.deepcopy(package)
        mutate(changed["bash_executable"])
        expect_error(
            "bash",
            lambda changed=changed: integration._validate_gate_terminal(
                "package", changed, "a" * 64,
                package_hashes,
                evidence_mode="PRODUCTION"))
    print("PROVISIONAL-PRODUCTION-BASH-BINDING=PASS")


def _assert_gate_qualification_scope_boundary():
    tooling_hash, tooling = evidence_producer._qualification_identity(
        "package", HERE.parent, TARGET_SHA, TARGET_TREE,
        qualification_scope="TOOLING_EXACT_SHA")
    assert integration._validate_qualification_identity(
        "package", tooling, tooling_hash, TARGET_SHA, TARGET_TREE,
        "a" * 64, "b" * 64) == tooling

    frozen_hash, frozen = evidence_producer._qualification_identity(
        "deterministic", HERE.parent, TARGET_SHA, TARGET_TREE,
        qualification_scope="FROZEN_CAMPAIGNS",
        qualified_input_sha256="a" * 64,
        surfaces_sha256="b" * 64)
    assert integration._validate_qualification_identity(
        "deterministic", frozen, frozen_hash, TARGET_SHA, TARGET_TREE,
        "a" * 64, "b" * 64) == frozen

    mutations = (
        ("scope confusion", lambda value: value.update(
            qualification_scope="FROZEN_CAMPAIGNS")),
        ("different SHA", lambda value: value.update(target_sha="0" * 40)),
        ("different tree", lambda value: value.update(target_tree="0" * 40)),
        ("missing field", lambda value: value.pop(
            "tooling_source_manifest")),
        ("extra field", lambda value: value.update(
            evaluated_surfaces_sha256="b" * 64)),
    )
    for label, mutate in mutations:
        changed = copy.deepcopy(tooling)
        mutate(changed)
        expect_error(
            None,
            lambda changed=changed: integration.
            _validate_qualification_identity(
                "package", changed, tooling_hash, TARGET_SHA, TARGET_TREE,
                "a" * 64, "b" * 64))
    print("PROVISIONAL-QUALIFICATION-SCOPE=PASS")


def _assert_package_reproducibility_asset_boundary():
    asset_hash = "c" * 64
    manifest_hash = "d" * 64
    binding = {
        "selected_archive_path": "package-retained.skill",
        "selected_archive_sha256": asset_hash,
        "assets": [
            {
                "label": "A",
                "path": "package-repro-a.skill",
                "sha256": asset_hash,
                "manifest_path": "package-repro-a-entry-manifest.json",
                "manifest_sha256": manifest_hash,
            },
            {
                "label": "B",
                "path": "package-repro-b.skill",
                "sha256": asset_hash,
                "manifest_path": "package-repro-b-entry-manifest.json",
                "manifest_sha256": manifest_hash,
            },
        ],
    }
    hashes = {
        "package-retained.skill": asset_hash,
        "package-repro-a.skill": asset_hash,
        "package-repro-b.skill": asset_hash,
        "package-repro-a-entry-manifest.json": manifest_hash,
        "package-repro-b-entry-manifest.json": manifest_hash,
    }
    assert integration._validate_package_asset_binding(
        binding, hashes) == binding
    mutations = (
        ("missing A/B", lambda value: value["assets"].pop()),
        ("drift", lambda value: value["assets"][1].update(
            sha256="e" * 64)),
        ("asset alias", lambda value: value["assets"][1].update(
            path="package-repro-a.skill")),
        ("manifest alias", lambda value: value["assets"][1].update(
            manifest_path="package-repro-a-entry-manifest.json")),
        ("extra asset", lambda value: value["assets"].append(
            copy.deepcopy(value["assets"][0]))),
    )
    for _label, mutate in mutations:
        changed = copy.deepcopy(binding)
        mutate(changed)
        expect_error(
            None,
            lambda changed=changed: integration.
            _validate_package_asset_binding(changed, hashes))
    print("PROVISIONAL-PACKAGE-REPRO-ASSETS=PASS")


def _finalize_b3(base, external_surface_paths=None):
    campaign_root = base / "b3-campaign"
    surface_root = base / "b3-surfaces"
    b3_fixture.build_campaign(
        campaign_root, surface_root=surface_root,
        external_surface_paths=external_surface_paths,
        foundation=TARGET_FOUNDATION)
    packet_path = campaign_root / "campaign-freeze.json"
    independent = b3v4_rederive.rederive_campaign(
        packet_path, campaign_root, surface_root)
    assert independent["luna_stage_status"] == "PASS", independent
    b3v4_rederive.write_rederivation(
        campaign_root / "b3v4-luna-independent-rederivation.json",
        independent, root=campaign_root)
    driver = b3v4_campaign.CampaignDriver(
        packet_path=packet_path, repo_root=surface_root,
        campaign_root=campaign_root, candidate_checkout=surface_root,
        control_checkout=surface_root, runtime_root=base / "b3-runtime",
        execution_mode="production")
    driver.live_validator = lambda packet, root: \
        surfaces.validate_packet_surfaces(
            packet, surfaces.B3_CAMPAIGN, root=root)
    driver.identity_validator = lambda _packet, **_paths: None
    retained_manifest = json.loads(
        (campaign_root / "campaign-manifest.json").read_text(
            encoding="utf-8"))

    class SyntheticFixtureCustody:
        root_fd = 1

        @staticmethod
        def verify():
            return retained_manifest["campaign_root_identity"]

    driver._custody_session = SyntheticFixtureCustody()
    official = driver.finalize_luna_stage()
    assert official["luna_stage_accepted"] is True
    assert official["mission_count"] == 6
    return campaign_root, surface_root


def _finalize_matrix(base, external_surface_paths=None):
    campaign_root = base / "matrix-campaign"
    surface_root = base / "matrix-surfaces"
    matrix_fixture.build_campaign(
        campaign_root, execution_mode="production",
        surface_root=surface_root,
        external_surface_paths=external_surface_paths,
        foundation=TARGET_FOUNDATION)
    packet_path = campaign_root / "campaign-freeze.json"
    independent = candidate_matrix_rederive.rederive_campaign(
        packet_path, campaign_root, surface_root)
    assert independent["luna_stage_status"] == "PASS", independent
    candidate_matrix_rederive.write_rederivation(
        campaign_root /
        "candidate-matrix-luna-independent-rederivation.json",
        independent, root=campaign_root)
    driver = candidate_matrix_campaign.CampaignDriver(
        packet_path=packet_path, repo_root=surface_root,
        campaign_root=campaign_root, candidate_checkout=surface_root,
        runtime_root=base / "matrix-runtime", execution_mode="production")
    driver.live_validator = lambda packet, root: \
        surfaces.validate_packet_surfaces(
            packet, surfaces.MATRIX_CAMPAIGN, root=root)
    driver.identity_validator = lambda _packet, **_paths: None
    official = driver.finalize_luna_stage()
    assert official["luna_stage_accepted"] is True
    assert official["cell_count"] == 14
    return campaign_root, surface_root


def _gate_values(qualified, package_manifest_hash, artifact_hash):
    workflow_sha = hashlib.sha256(
        (pathlib.Path(__file__).resolve().parent.parent /
         ".github" / "workflows" /
         "validate.yml").read_bytes()).hexdigest()
    frozen_identity = {
        "qualification_scope": "FROZEN_CAMPAIGNS",
        "target_sha": TARGET_SHA,
        "target_tree": TARGET_TREE,
        "campaign_qualified_input_sha256": qualified,
        "evaluated_surfaces_sha256": "f" * 64,
    }
    common = {
        "qualification_scope": "FROZEN_CAMPAIGNS",
        "qualification_identity": frozen_identity,
    }
    values = {
        "deterministic": {
            "schema": "implementaudit-deterministic-terminal-v1",
            "gate": "deterministic",
            "qualified_input_sha256": qualified,
            "exit_code": 0, "failed_checks": [],
            "checks": [{
                "name": name, "command": f"focused:{name}",
                "exit_code": 0,
                "marker": f"FOCUSED_CHECK_PASS name={name}",
            } for name in integration.DETERMINISTIC_CHECKS],
        },
        "package": {
            "schema": "implementaudit-package-terminal-v1",
            "gate": "package", "qualified_input_sha256": qualified,
            "exit_code": 0, "verification_passed": True,
            "package_manifest_sha256": package_manifest_hash,
        },
        "ci": {
            "schema": "implementaudit-ci-terminal-v1",
            "gate": "ci", "qualified_input_sha256": qualified,
            "exit_code": 0, "failed_jobs": [],
            "jobs": [{
                "name": "package",
                "workflow_path": ".github/workflows/validate.yml",
                "workflow_sha256": workflow_sha,
                "run_attempt": 1, "conclusion": "success",
                "log_marker": "CI_JOB_PASS name=package",
            }],
        },
        "reproducibility": {
            "schema": "implementaudit-reproducibility-terminal-v1",
            "gate": "reproducibility",
            "qualified_input_sha256": qualified,
            "exit_code": 0, "comparison_equal": True,
            "first_artifact_sha256": artifact_hash,
            "second_artifact_sha256": artifact_hash,
        },
        "independent-review": {
            "schema": "implementaudit-independent-review-terminal-v1",
            "gate": "independent-review",
            "reviewed_qualified_input_sha256": qualified,
            "verdict": "PASS", "findings": [],
        },
    }
    for value in values.values():
        value.update(common)
    return values


def _gates(root, qualified, target_sha, target_tree, surfaces_sha256):
    root.mkdir()
    producer_repo = _producer_repo()
    prior = hashlib.sha256(b"").hexdigest()
    for name in integration.REQUIRED_GATES:
        review = None
        qualification_scope = (
            "TOOLING_EXACT_SHA"
            if name in ("package", "ci", "reproducibility")
            else "FROZEN_CAMPAIGNS")
        if name == "independent-review":
            base_sha = subprocess.check_output(
                ["git", "-C", str(producer_repo), "rev-parse",
                 f"{target_sha}^"], text=True).strip()
            scope = subprocess.check_output(
                ["git", "-C", str(producer_repo), "diff", "--name-only",
                 base_sha, target_sha], text=True).splitlines()
            review = {
                "reviewer_identity": "fresh-reviewer-1",
                "reviewer_role": "independent-read-only-reviewer",
                "reviewed_evidence_sha256": prior,
                "base_sha": base_sha,
                "range": f"{base_sha}..{target_sha}",
                "scope": scope, "findings": [], "verdict": "PASS",
                "report":
                    b"# Complete-boundary review\n\nVERDICT: PASS\n",
            }
        manifest_sha = evidence_producer.run_gate(
            name, repo_root=producer_repo, evidence_root=root,
            target_sha=target_sha, target_tree=target_tree,
            qualification_scope=qualification_scope,
            qualified_input_sha256=(
                qualified if qualification_scope ==
                "FROZEN_CAMPAIGNS" else None),
            surfaces_sha256=(
                surfaces_sha256 if qualification_scope ==
                "FROZEN_CAMPAIGNS" else None),
            prior_evidence_sha256=prior, review=review,
            test_only=True)
        prior = integration._canonical_sha({
            "prior": prior, "name": name,
            "evidence_manifest_sha256": manifest_sha,
        })
    return root


def _rebind_gate_manifest(root, name):
    path = root / f"{name}-evidence-manifest.json"
    manifest = json.loads(path.read_text(encoding="utf-8"))
    for row in manifest["files"]:
        raw = (root / row["path"]).read_bytes()
        row["byte_length"] = len(raw)
        row["sha256"] = hashlib.sha256(raw).hexdigest()
    write(path, manifest)


def _certificate_root(base, label):
    root = pathlib.Path(base) / f"certificate-{label}"
    root.mkdir(parents=True)
    return root


def _roots(base, *, with_external=False):
    if with_external:
        b3_pre_external = {
            "host-attestation":
                base / "b3-pre-external" / "luna-host-attestation.json",
            "product-candidate":
                base / "b3-pre-external" / "candidate" / "SKILL.md",
        }
        matrix_pre_external = {
            "host-attestation":
                base / "matrix-pre-external" /
                "luna-host-attestation.json",
            "product-candidate":
                base / "matrix-pre-external" / "candidate" / "SKILL.md",
        }
    else:
        b3_pre_external = {}
        matrix_pre_external = {}
    b3_campaign_root, b3_surface_root = _finalize_b3(
        base, b3_pre_external)
    matrix_campaign_root, matrix_surface_root = _finalize_matrix(
        base, matrix_pre_external)
    b3_after = base / "b3-after"
    matrix_after = base / "matrix-after"
    shutil.copytree(b3_surface_root, b3_after)
    shutil.copytree(matrix_surface_root, matrix_after)
    qualified = integration.derive_qualified_input_sha256(
        b3_campaign_root=b3_campaign_root,
        matrix_campaign_root=matrix_campaign_root,
        b3_surface_root=b3_surface_root,
        matrix_surface_root=matrix_surface_root)
    b3_packet = json.loads(
        (b3_campaign_root / "campaign-freeze.json").read_text(
            encoding="utf-8"))
    b3_manifest = b3_packet["evaluated_surfaces"]
    matrix_packet = json.loads(
        (matrix_campaign_root / "campaign-freeze.json").read_text(
            encoding="utf-8"))
    surfaces_sha256 = integration._canonical_sha({
        surfaces.B3_CAMPAIGN: surfaces.manifest_sha256(b3_manifest),
        surfaces.MATRIX_CAMPAIGN: surfaces.manifest_sha256(
            matrix_packet["evaluated_surfaces"]),
    })
    gate_root = _gates(
        base / "gates", qualified,
        b3_packet["foundation"]["commit"], b3_packet["foundation"]["tree"],
        surfaces_sha256)
    roots = {
        "b3_campaign_root": b3_campaign_root,
        "matrix_campaign_root": matrix_campaign_root,
        "b3_surface_root": b3_surface_root,
        "matrix_surface_root": matrix_surface_root,
        "b3_after_surface_root": b3_after,
        "matrix_after_surface_root": matrix_after,
        "gate_root": gate_root,
        "allow_test_evidence": True,
    }
    if with_external:
        b3_after_external = {}
        matrix_after_external = {}
        for campaign, before, after in (
                ("b3", b3_pre_external, b3_after_external),
                ("matrix", matrix_pre_external, matrix_after_external)):
            for role, source in before.items():
                name = ("luna-host-attestation.json"
                        if role == "host-attestation" else "candidate/SKILL.md")
                target = base / f"{campaign}-after-external" / name
                write(target, pathlib.Path(source).read_bytes())
                after[role] = target.as_posix()
        roots["b3_after_external_paths"] = b3_after_external
        roots["matrix_after_external_paths"] = matrix_after_external
    return roots


def _replace_all(root):
    for path in sorted(root.rglob("*")):
        if path.is_file():
            path.write_bytes(b"replacement bytes\n")


def _exercise_external_after_locator(base):
    before_root = base / "external-before"
    after_root = base / "external-after"
    before_external = {
        "product-candidate": base / "before-product.bin",
        "host-attestation": base / "before-attestation.bin",
    }
    after_external = {
        "product-candidate": base / "after-product.bin",
        "host-attestation": base / "after-attestation.bin",
    }
    for role in before_external:
        payload = f"{role} exact bytes\n".encode()
        write(before_external[role], payload)
        write(after_external[role], payload)
    sources = []
    for index, role in enumerate(
            surfaces.required_roles(surfaces.MATRIX_CAMPAIGN)):
        if role in before_external:
            path = before_external[role].as_posix()
        else:
            path = f"surface/{index:02d}.bin"
            write(before_root / path, f"{role}\n".encode())
            write(after_root / path, f"{role}\n".encode())
        sources.append({"role": role, "path": path})
    before = surfaces.build_manifest(
        surfaces.MATRIX_CAMPAIGN, sources, root=before_root)
    locators = {
        role: path.as_posix() for role, path in after_external.items()
    }
    expect_error(
        "external locator",
        lambda: integration._after_manifest(before, after_root, {}))
    expect_error(
        "external locator",
        lambda: integration._after_manifest(
            before, after_root,
            {**locators, "launcher": (base / "extra.bin").as_posix()}))
    expect_error(
        "reuses prior path",
        lambda: integration._after_manifest(
            before, after_root, {
                **locators,
                "product-candidate":
                    before_external["product-candidate"].as_posix(),
            }))
    expect_error(
        "physical alias",
        lambda: integration._after_manifest(
            before, after_root, {
                role: after_external["product-candidate"].as_posix()
                for role in locators
            }))
    expect_error(
        "escapes owner root",
        lambda: integration._after_manifest(
            before, after_root, {
                **locators,
                "product-candidate": (
                    after_external["product-candidate"].parent / "alias" /
                    ".." / after_external["product-candidate"].name
                ).as_posix(),
            }))
    if os.name == "nt":
        expect_error(
            "physical alias",
            lambda: integration._after_manifest(
                before, after_root, {
                    "product-candidate":
                        after_external["product-candidate"].as_posix(),
                    "host-attestation":
                        after_external["product-candidate"].as_posix().upper(),
                }))
    swapped = integration._after_manifest(
        before, after_root, {
            "product-candidate":
                after_external["host-attestation"].as_posix(),
            "host-attestation":
                after_external["product-candidate"].as_posix(),
        })
    expect_error(
        "byte drift",
        lambda: integration._compare_after_bytes(
            before, swapped, surfaces.MATRIX_CAMPAIGN))
    after = integration._after_manifest(
        before, after_root, locators)
    integration._compare_after_bytes(
        before, after, surfaces.MATRIX_CAMPAIGN)
    write(after_external["product-candidate"], b"changed product bytes\n")
    changed = integration._after_manifest(
        before, after_root, locators)
    expect_error(
        "byte drift",
        lambda: integration._compare_after_bytes(
            before, changed, surfaces.MATRIX_CAMPAIGN))


def _mutate_stage_rows(campaign_root, official_name, independent_name,
                       rows_name):
    independent_path = campaign_root / independent_name
    independent = json.loads(independent_path.read_text(encoding="utf-8"))
    independent[rows_name][0]["bundle_manifest_sha256"] = "7" * 64
    write(independent_path, independent)
    official_path = campaign_root / official_name
    official = json.loads(official_path.read_text(encoding="utf-8"))
    official[rows_name][0]["bundle_manifest_sha256"] = "7" * 64
    official["independent_rederivation"]["sha256"] = hashlib.sha256(
        independent_path.read_bytes()).hexdigest()
    write(official_path, official)


ROOT_IDENTITY_CASES = (
    "b3-same-pre",
    "matrix-same-pre",
    "both-same-pre",
    "dot-alias",
    "dotdot-alias",
    "case-alias",
    "other-campaign-root",
    "junction-alias",
    "member-hardlink",
    "two-member-hardlinks",
    "external-pre-reuse",
    "two-external-pre-reuses",
)


def _relative_surface_path(campaign_root, role):
    packet = json.loads(
        (campaign_root / "campaign-freeze.json").read_text(encoding="utf-8"))
    for row in packet["evaluated_surfaces"]["entries"]:
        if row["role"] == role:
            assert not pathlib.Path(row["path"]).is_absolute()
            return pathlib.PurePosixPath(row["path"])
    raise AssertionError(f"missing role {role}")


def _exercise_root_identity_case(base, label):
    with_external = label in (
        "external-pre-reuse", "two-external-pre-reuses")
    roots = _roots(base, with_external=with_external)
    expected = "post-integration root identity"
    junction = None
    if label == "b3-same-pre":
        roots["b3_after_surface_root"] = roots["b3_surface_root"]
    elif label == "matrix-same-pre":
        roots["matrix_after_surface_root"] = roots["matrix_surface_root"]
    elif label == "both-same-pre":
        roots["b3_after_surface_root"] = roots["b3_surface_root"]
        roots["matrix_after_surface_root"] = roots["matrix_surface_root"]
    elif label == "dot-alias":
        root = roots["b3_surface_root"]
        roots["b3_after_surface_root"] = (
            str(root.parent) + os.sep + "." + os.sep + root.name)
    elif label == "dotdot-alias":
        root = roots["b3_surface_root"]
        alias_component = root.parent / "alias-component"
        alias_component.mkdir()
        roots["b3_after_surface_root"] = (
            str(alias_component) + os.sep + ".." + os.sep + root.name)
        expected = "link or reparse alias"
    elif label == "case-alias":
        if os.name != "nt":
            print("PROVISIONAL-ROOT-CASE-ALIAS=SKIP:not-windows")
            return
        roots["b3_after_surface_root"] = str(
            roots["b3_surface_root"]).swapcase()
    elif label == "other-campaign-root":
        roots["matrix_after_surface_root"] = roots["b3_after_surface_root"]
    elif label == "junction-alias":
        if os.name != "nt":
            print("PROVISIONAL-ROOT-JUNCTION=SKIP:not-windows")
            return
        junction = base / "b3-root-junction"
        result = subprocess.run(
            ["cmd", "/c", "mklink", "/J", str(junction),
             str(roots["b3_surface_root"])],
            capture_output=True, text=True)
        if result.returncode:
            print("PROVISIONAL-ROOT-JUNCTION=SKIP:mklink")
            return
        roots["b3_after_surface_root"] = junction
        expected = "link or reparse alias"
    elif label in ("member-hardlink", "two-member-hardlinks"):
        # Packet projections are virtual identities and have no physical leaf
        # to hardlink. Exercise the retained-file invariant on physical roles.
        roles = ["adapter"]
        if label == "two-member-hardlinks":
            roles.append("scorer")
        for role in roles:
            relative = _relative_surface_path(
                roots["b3_campaign_root"], role)
            before = roots["b3_surface_root"] / relative
            after = roots["b3_after_surface_root"] / relative
            after.unlink()
            os.link(before, after)
        expected = "hardlink"
    elif label in ("external-pre-reuse", "two-external-pre-reuses"):
        roles = ["product-candidate"]
        if label == "two-external-pre-reuses":
            roles.append("host-attestation")
        for role in roles:
            roots["b3_after_external_paths"][role] = (
                roots["b3_surface_root"].parent /
                "b3-pre-external" /
                ("luna-host-attestation.json"
                 if role == "host-attestation" else "candidate/SKILL.md")
            ).as_posix()
        expected = None
    else:
        raise AssertionError(f"unsupported root identity case {label}")
    try:
        expect_error(
            expected,
            lambda: integration.write_certificate(
                _certificate_root(base, label), **roots))
    finally:
        if junction is not None and junction.exists():
            os.rmdir(junction)


def _assert_output_custody_matrix(base):
    qualified = base / "qualified"
    qualified.mkdir()
    roots = _roots(qualified, with_external=True)
    root_keys = (
        "b3_campaign_root", "matrix_campaign_root",
        "b3_surface_root", "matrix_surface_root",
        "b3_after_surface_root", "matrix_after_surface_root", "gate_root",
    )
    # Equal and descendant roots cover campaign/packet, pre/post, every member
    # file under those roots, and all five gate evidence files.
    for key in root_keys:
        expect_error(
            "certificate",
            lambda key=key: integration._validate_certificate_root(
                roots[key], roots))
        child = pathlib.Path(roots[key]) / "certificate-output"
        child.mkdir()
        expect_error(
            "certificate",
            lambda child=child: integration._validate_certificate_root(
                child, roots))
    # A common ancestor is equally unsafe because certificate creation would
    # mutate the qualified custody namespace.
    expect_error(
        "certificate",
        lambda: integration._validate_certificate_root(qualified, roots))

    b3_root = pathlib.Path(roots["b3_campaign_root"])
    dot_alias = str(b3_root.parent) + os.sep + "." + os.sep + b3_root.name
    expect_error(
        "certificate",
        lambda: integration._validate_certificate_root(dot_alias, roots))
    alias_component = b3_root.parent / "certificate-alias-component"
    alias_component.mkdir()
    dotdot_alias = str(alias_component) + os.sep + ".." + os.sep + \
        b3_root.name
    expect_error(
        None,
        lambda: integration._validate_certificate_root(dotdot_alias, roots))
    if os.name == "nt":
        expect_error(
            "certificate",
            lambda: integration._validate_certificate_root(
                str(b3_root).swapcase(), roots))
        junction = qualified / "certificate-root-junction"
        made = subprocess.run(
            ["cmd", "/c", "mklink", "/J", str(junction), str(b3_root)],
            capture_output=True, text=True)
        if made.returncode:
            print("CERTIFICATE_ROOT_JUNCTION=SKIP:mklink")
        else:
            try:
                expect_error(
                    "link or reparse",
                    lambda: integration._validate_certificate_root(
                        junction, roots))
            finally:
                os.rmdir(junction)
            print("CERTIFICATE_ROOT_JUNCTION=PASS")

    preexisting = _certificate_root(base, "preexisting-leaf")
    write(preexisting / integration.CERTIFICATE_FILENAME, b"occupied\n")
    expect_error(
        "create-once",
        lambda: integration._validate_certificate_root(preexisting, roots))

    hardlinked = _certificate_root(base, "hardlinked-leaf")
    gate_file = pathlib.Path(roots["gate_root"]) / \
        integration.GATE_FILENAMES["deterministic"]
    os.link(gate_file, hardlinked / integration.CERTIFICATE_FILENAME)
    expect_error(
        "create-once",
        lambda: integration._validate_certificate_root(hardlinked, roots))

    # External before/after locators are outside the root set and therefore
    # receive a second explicit ancestor/equality check.
    for key in ("b3_after_external_paths", "matrix_after_external_paths"):
        for path in roots[key].values():
            parent = pathlib.Path(path).parent
            _root, identity = integration._validate_certificate_root(
                parent, roots)
            expect_error(
                "retained input file",
                lambda identity=identity:
                integration._validate_certificate_external_disjoint(
                    identity, roots))
    for campaign_key in ("b3_campaign_root", "matrix_campaign_root"):
        packet = json.loads((
            pathlib.Path(roots[campaign_key]) / "campaign-freeze.json"
        ).read_text(encoding="utf-8"))
        for row in packet["evaluated_surfaces"]["entries"]:
            if (pathlib.Path(row["path"]).is_absolute() and
                    row["role"] not in surfaces.INLINE_ROLES):
                parent = pathlib.Path(row["path"]).parent
                _root, identity = integration._validate_certificate_root(
                    parent, roots)
                expect_error(
                    "retained input file",
                    lambda identity=identity:
                    integration._validate_certificate_external_disjoint(
                        identity, roots))
    print("CERTIFICATE_OUTPUT_CUSTODY_MATRIX=PASS")


def _assert_virtual_projection_integration_boundary(base):
    roots = _roots(base)
    packet = json.loads((
        roots["b3_campaign_root"] / "campaign-freeze.json"
    ).read_text(encoding="utf-8"))
    before = copy.deepcopy(packet["evaluated_surfaces"])
    acceptance = next(
        row for row in before["entries"]
        if row["role"] == "acceptance-rules")
    acceptance["sha256"] = "0" * 64
    after = integration._after_manifest(
        before, roots["b3_after_surface_root"], {}, packet)
    canonical = next(
        row for row in after["entries"]
        if row["role"] == "acceptance-rules")
    assert canonical["sha256"] != acceptance["sha256"], (
        "post manifest trusted a caller-supplied virtual digest")

    forged = copy.deepcopy(packet["evaluated_surfaces"])
    adapter = next(
        row for row in forged["entries"] if row["role"] == "adapter")
    adapter["path"] = surfaces.projection_path("acceptance-rules")
    expect_error(
        "cannot be read",
        lambda: integration._after_manifest(
            forged, roots["b3_after_surface_root"], {}, packet))

    shadow = (roots["b3_after_surface_root"] /
              "evaluated-surface-projections")
    shadow.mkdir()
    try:
        expect_error(
            "shadow or residue",
            lambda: integration._after_manifest(
                packet["evaluated_surfaces"],
                roots["b3_after_surface_root"], {}, packet))
    finally:
        shadow.rmdir()
    print("PROVISIONAL-VIRTUAL-PROJECTION-BOUNDARY=PASS")


def main():
    # Round-3 governing RED: positive gate evidence comes only from the
    # controller-owned producer API, never direct test-authored terminals.
    assert callable(evidence_producer.run_gate)
    _assert_production_bash_binding_boundary()
    _assert_gate_qualification_scope_boundary()
    _assert_package_reproducibility_asset_boundary()

    # Governing round-2 RED: package authority must parse a real canonical
    # archive and derive its exact entry manifest, not merely compare digests.
    with tempfile.TemporaryDirectory(
            prefix="task5-r2-package-archive-red-") as tmp:
        base = pathlib.Path(tmp)
        archive = base / "package-retained.skill"
        archive.write_bytes(b"not a ZIP archive\n")
        manifest = base / "package-entry-manifest.json"
        write(manifest, {"entries": []})
        expect_error(
            "archive",
            lambda: integration.validate_package_archive(
                archive, manifest, "1" * 40, "2" * 40))

    gate_values = _gate_values("a" * 64, "b" * 64, "c" * 64)
    for label, name, mutate, fragment in (
            ("focused-order", "deterministic",
             lambda value: value["checks"].reverse(), "coverage"),
            ("focused-exit", "deterministic",
             lambda value: value["checks"][0].update(exit_code=1), "row"),
            ("ci-workflow-hash", "ci",
             lambda value: value["jobs"][0].update(
                 workflow_sha256="0" * 64), "row"),
            ("ci-duplicate", "ci",
             lambda value: value["jobs"].append(
                 copy.deepcopy(value["jobs"][0])), "coverage")):
        changed = copy.deepcopy(gate_values[name])
        mutate(changed)
        expect_error(
            fragment,
            lambda name=name, changed=changed:
            integration._validate_gate_terminal(
                name, changed, "a" * 64, {}))

    if len(sys.argv) == 3 and sys.argv[1] == "--root-identity-case":
        label = sys.argv[2]
        assert label in ROOT_IDENTITY_CASES
        with tempfile.TemporaryDirectory(
                prefix=f"task4-root-{label}-") as tmp:
            _exercise_root_identity_case(pathlib.Path(tmp).resolve(), label)
        print(f"PROVISIONAL-ROOT-IDENTITY-{label}=PASS")
        return

    with tempfile.TemporaryDirectory(
            prefix="task4-external-after-") as tmp:
        _exercise_external_after_locator(pathlib.Path(tmp).resolve())

    for label in ROOT_IDENTITY_CASES:
        with tempfile.TemporaryDirectory(
                prefix=f"task4-root-{label}-") as tmp:
            _exercise_root_identity_case(pathlib.Path(tmp).resolve(), label)

    with tempfile.TemporaryDirectory(
            prefix="task4-certificate-custody-matrix-") as tmp:
        _assert_output_custody_matrix(pathlib.Path(tmp).resolve())

    with tempfile.TemporaryDirectory(
            prefix="task4-virtual-projection-integration-") as tmp:
        _assert_virtual_projection_integration_boundary(
            pathlib.Path(tmp).resolve())

    # Certificate output is a new custody domain. It may not be placed inside
    # either retained campaign (nor, by extension, any other qualified input
    # domain).
    with tempfile.TemporaryDirectory(
            prefix="task4-output-custody-red-") as tmp:
        base = pathlib.Path(tmp).resolve()
        roots = _roots(base)
        expect_error(
            "certificate",
            lambda: integration.write_certificate(
                roots["b3_campaign_root"], **roots))

    # The structural path uses production-shaped retained roots: six B3
    # attempts and fourteen matrix attempts, both official and independently
    # rederived, plus their real lifecycle stage terminals.  Its gate evidence
    # is explicitly TEST_ONLY and therefore cannot authorize integration.
    with tempfile.TemporaryDirectory(
            prefix="task4-production-roots-") as tmp:
        base = pathlib.Path(tmp).resolve()
        roots = _roots(base)
        output = _certificate_root(base, "accepted")
        certificate = integration.write_certificate(output, **roots)
        assert (output / integration.CERTIFICATE_FILENAME).is_file()
        assert certificate["disposition"] == \
            "TEST_ONLY_NON_QUALIFYING"
        assert certificate["integration_authorized"] is False
        assert certificate["b3_luna"]["accepted_count"] == 6
        assert certificate["matrix_luna"]["accepted_count"] == 14
        assert all(
            row["semantic_status"] == "PASS"
            for row in certificate["gates"])
        assert certificate["release_authorized"] is False
        assert certificate["tag_authorized"] is False
        assert certificate["publication_authorized"] is False
        expect_error(
            "create-once",
            lambda: integration.write_certificate(output, **roots))
        write(roots["gate_root"] / "self-authored-extra.json", {})
        expect_error(
            "coverage",
            lambda: integration.write_certificate(
                _certificate_root(base, "extra-gate-evidence"), **roots))

    # External roles also use fresh post-integration locator files rather than
    # the packet's frozen absolute locations.
    with tempfile.TemporaryDirectory(
            prefix="task4-production-external-roots-") as tmp:
        base = pathlib.Path(tmp).resolve()
        roots = _roots(base, with_external=True)
        certificate = integration.write_certificate(
            _certificate_root(base, "external"), **roots)
        assert certificate["b3_luna"]["accepted_count"] == 6
        assert certificate["matrix_luna"]["accepted_count"] == 14
        assert all(
            row["post_files_distinct_from_all_pre_files"] is True
            for row in certificate["surface_comparisons"].values())

    # R1: packet-derived before bytes govern. Replacing every post-integration
    # surface cannot be legalized by rebuilding a caller manifest because no
    # caller manifest exists in the API.
    with tempfile.TemporaryDirectory(prefix="task4-r1-") as tmp:
        base = pathlib.Path(tmp).resolve()
        roots = _roots(base)
        _replace_all(roots["b3_after_surface_root"])
        _replace_all(roots["matrix_after_surface_root"])
        expect_error(
            "byte drift",
            lambda: integration.write_certificate(
                _certificate_root(base, "replaced"), **roots))

    # R2: result and stage summaries are reconstructed from the attempts.
    # Mutually rebinding fabricated row digests cannot replace campaign roots.
    with tempfile.TemporaryDirectory(prefix="task4-r2-") as tmp:
        base = pathlib.Path(tmp).resolve()
        roots = _roots(base)
        _mutate_stage_rows(
            roots["b3_campaign_root"], "b3v4-luna-result.json",
            "b3v4-luna-independent-rederivation.json", "missions")
        _mutate_stage_rows(
            roots["matrix_campaign_root"],
            "candidate-matrix-luna-result.json",
            "candidate-matrix-luna-independent-rederivation.json", "cells")
        expect_error(
            None,
            lambda: integration.write_certificate(
                _certificate_root(base, "fabricated"), **roots))

    # R3 and the neighboring closed terminal states: PASS is derived from each
    # gate's typed terminal bytes, never from caller status metadata.
    for label, mutate in (
            ("arbitrary", lambda value: {"status": "PASS"}),
            ("non-pass", lambda value: {
                **value, "exit_code": 1, "failed_checks": ["failed"]}),
            ("extra", lambda value: {**value, "status": "PASS"}),
            ("coercive", lambda value: {**value, "exit_code": False})):
        with tempfile.TemporaryDirectory(prefix=f"task4-r3-{label}-") as tmp:
            base = pathlib.Path(tmp).resolve()
            roots = _roots(base)
            path = roots["gate_root"] / \
                integration.GATE_FILENAMES["deterministic"]
            value = json.loads(path.read_text(encoding="utf-8"))
            write(path, mutate(copy.deepcopy(value)))
            expect_error(
                None,
                lambda: integration.write_certificate(
                    _certificate_root(base, label), **roots))

    # Governing complete-boundary RED: internally coherent caller-authored
    # summaries are not retained producer evidence.
    for label, gate_name, mutate in (
            ("zero-package-manifest", "package", lambda value: {
                **value, "package_manifest_sha256": "0" * 64}),
            ("one-filled-reproducibility", "reproducibility", lambda value: {
                **value,
                "first_artifact_sha256": "1" * 64,
                "second_artifact_sha256": "1" * 64,
            }),
            ("identity-free-review", "independent-review", lambda value: value)):
        with tempfile.TemporaryDirectory(
                prefix=f"task5-gate-authority-{label}-") as tmp:
            base = pathlib.Path(tmp).resolve()
            roots = _roots(base)
            path = roots["gate_root"] / integration.GATE_FILENAMES[gate_name]
            value = json.loads(path.read_text(encoding="utf-8"))
            write(path, mutate(copy.deepcopy(value)))
            if label == "identity-free-review":
                report_path = (
                    roots["gate_root"] /
                    "independent-review-report.json")
                report = json.loads(report_path.read_text(encoding="utf-8"))
                del report["reviewer_identity"]
                write(report_path, report)
            _rebind_gate_manifest(roots["gate_root"], gate_name)
            expect_error(
                None,
                lambda: integration.write_certificate(
                    _certificate_root(base, label), **roots))

    print("PROVISIONAL-INTEGRATION-PASS")


if __name__ == "__main__":
    main()
