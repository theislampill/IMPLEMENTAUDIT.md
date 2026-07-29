#!/usr/bin/env python3
"""Production-shaped tests for the custody-derived integration certificate."""
from __future__ import annotations

import copy
import hashlib
import json
import os
import pathlib
import shutil
import tempfile

import b3v4_campaign
import b3v4_rederive
import candidate_matrix_campaign
import candidate_matrix_rederive
import evaluated_surfaces as surfaces
import provisional_integration as integration
import test_b3v4_rederive as b3_fixture
import test_candidate_matrix_rederive as matrix_fixture


def encoded(value):
    return (json.dumps(
        value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def write(path, value):
    path = pathlib.Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(value if isinstance(value, bytes) else encoded(value))


def expect_error(fragment, action):
    try:
        action()
    except (OSError, TypeError, ValueError) as exc:
        if fragment is not None:
            assert fragment.lower() in str(exc).lower(), str(exc)
    else:
        raise AssertionError(f"expected failure containing {fragment!r}")


def _finalize_b3(base):
    campaign_root = base / "b3-campaign"
    surface_root = base / "b3-surfaces"
    b3_fixture.build_campaign(campaign_root, surface_root=surface_root)
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
        surfaces.revalidate_manifest(packet["evaluated_surfaces"], root=root)
    driver.identity_validator = lambda _packet, **_paths: None
    official = driver.finalize_luna_stage()
    assert official["luna_stage_accepted"] is True
    assert official["mission_count"] == 6
    return campaign_root, surface_root


def _finalize_matrix(base):
    campaign_root = base / "matrix-campaign"
    surface_root = base / "matrix-surfaces"
    matrix_fixture.build_campaign(
        campaign_root, execution_mode="production",
        surface_root=surface_root)
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
        surfaces.revalidate_manifest(packet["evaluated_surfaces"], root=root)
    driver.identity_validator = lambda _packet, **_paths: None
    official = driver.finalize_luna_stage()
    assert official["luna_stage_accepted"] is True
    assert official["cell_count"] == 14
    return campaign_root, surface_root


def _gate_values(qualified):
    artifact = "a" * 64
    return {
        "deterministic": {
            "schema": "implementaudit-deterministic-terminal-v1",
            "gate": "deterministic",
            "qualified_input_sha256": qualified,
            "exit_code": 0, "failed_checks": [],
        },
        "package": {
            "schema": "implementaudit-package-terminal-v1",
            "gate": "package", "qualified_input_sha256": qualified,
            "exit_code": 0, "verification_passed": True,
            "package_manifest_sha256": artifact,
        },
        "ci": {
            "schema": "implementaudit-ci-terminal-v1",
            "gate": "ci", "qualified_input_sha256": qualified,
            "exit_code": 0, "failed_jobs": [],
        },
        "reproducibility": {
            "schema": "implementaudit-reproducibility-terminal-v1",
            "gate": "reproducibility",
            "qualified_input_sha256": qualified,
            "exit_code": 0, "comparison_equal": True,
            "first_artifact_sha256": artifact,
            "second_artifact_sha256": artifact,
        },
        "independent-review": {
            "schema": "implementaudit-independent-review-terminal-v1",
            "gate": "independent-review",
            "reviewed_qualified_input_sha256": qualified,
            "verdict": "PASS", "findings": [],
        },
    }


def _gates(root, qualified):
    root.mkdir()
    for name, value in _gate_values(qualified).items():
        write(root / integration.GATE_FILENAMES[name], value)
    return root


def _roots(base):
    b3_campaign_root, b3_surface_root = _finalize_b3(base)
    matrix_campaign_root, matrix_surface_root = _finalize_matrix(base)
    b3_after = base / "b3-after"
    matrix_after = base / "matrix-after"
    shutil.copytree(b3_surface_root, b3_after)
    shutil.copytree(matrix_surface_root, matrix_after)
    qualified = integration.derive_qualified_input_sha256(
        b3_campaign_root=b3_campaign_root,
        matrix_campaign_root=matrix_campaign_root,
        b3_surface_root=b3_surface_root,
        matrix_surface_root=matrix_surface_root)
    gate_root = _gates(base / "gates", qualified)
    return {
        "b3_campaign_root": b3_campaign_root,
        "matrix_campaign_root": matrix_campaign_root,
        "b3_surface_root": b3_surface_root,
        "matrix_surface_root": matrix_surface_root,
        "b3_after_surface_root": b3_after,
        "matrix_after_surface_root": matrix_after,
        "gate_root": gate_root,
    }


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


def main():
    with tempfile.TemporaryDirectory(
            prefix="task4-external-after-") as tmp:
        _exercise_external_after_locator(pathlib.Path(tmp).resolve())

    # The accepted path uses real production-shaped retained roots: six B3
    # attempts and fourteen matrix attempts, both official and independently
    # rederived, plus their real lifecycle stage terminals.
    with tempfile.TemporaryDirectory(
            prefix="task4-production-roots-") as tmp:
        base = pathlib.Path(tmp).resolve()
        roots = _roots(base)
        output = base / "integration-certificate.json"
        certificate = integration.write_certificate(output, **roots)
        assert certificate["disposition"] == \
            "LUNA_6_OF_6_AND_14_OF_14_GREEN_MERGED_TO_MAIN"
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
                base / "replaced.json", **roots))

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
                base / "fabricated.json", **roots))

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
                    base / f"{label}.json", **roots))

    print("PROVISIONAL-INTEGRATION-PASS")


if __name__ == "__main__":
    main()
