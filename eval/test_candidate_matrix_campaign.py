#!/usr/bin/env python3
"""Deterministic tests for the serialized Luna candidate-matrix driver."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import pathlib
import tempfile

from test_candidate_matrix_freeze import valid_packet
import candidate_matrix_contract as matrix_contract


HERE = pathlib.Path(__file__).resolve().parent
MODULE = HERE / "candidate_matrix_campaign.py"
FIXTURES = ["B0", "B1", "B2", "E1", "E2a", "E2b", "E3", "E4",
            "E5", "E6", "E7", "E8", "E9", "E10"]


def load_module():
    spec = importlib.util.spec_from_file_location("candidate_matrix_campaign", MODULE)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def encoded(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) +
            "\n").encode()


FINAL_CLAIMS = {
    "final_28_of_28": False,
    "cross_model_qualified": False,
    "release_authorized": False,
    "tag_authorized": False,
    "publication_authorized": False,
}


def executor(context):
    mission = context.mission
    assert mission == {"index": mission["index"], "config": "L",
                       "fixture": FIXTURES[mission["index"]]}
    name = context.attempt_root.name
    bundle = context.attempt_root / "host-custody" / name / "bundle"
    artifacts = bundle / "artifacts"
    artifacts.mkdir(parents=True)
    (bundle / "manifest.json").write_bytes(b"synthetic manifest\n")
    (artifacts / "host-stdout.raw").write_bytes(b"synthetic stdout\n")
    (artifacts / "host-session.raw").write_bytes(b"synthetic session\n")
    fixture_path = HERE / "fixtures" / mission["fixture"] / "fixture.json"
    fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
    properties = {
        row["name"]: {
            "state": "PASS", "pass": True,
            "evidence": "synthetic retained evidence",
            "describes": row.get("describes", ""),
            "basis": "host-observation",
        }
        for row in fixture["properties"]
    }
    return {
        "overall_status": "PASS",
        "resolved_model": "gpt-5.6-luna",
        "host_run_root": str(
            (context.attempt_root / "host-custody" / name).absolute()),
        "official_verdict": {
            "schema": "implementaudit-eval-verdict-v3", "status": "PASS",
            "run_id": name, "fixture_id": mission["fixture"],
            "fixture_sha256": hashlib.sha256(fixture_path.read_bytes()).hexdigest(),
            "prompt_sha256": "a" * 64, "events_sha256": "b" * 64,
            "product_tag": "v0.3.2.0", "product_commit": "c" * 40,
            "product_tree": "d" * 40, "installed_payload_sha256": "e" * 64,
            "harness_commit": "f" * 40, "adapter_name": "synthetic",
            "adapter_version": "test", "adapter_sha256": "1" * 64,
            "model_requested": "gpt-5.6-luna",
            "model_resolved": "gpt-5.6-luna",
            "model_substitution": False, "host": "synthetic",
            "started_at": "2030-01-01T00:00:00Z",
            "ended_at": "2030-01-01T00:00:01Z",
            "identity_attestation": {
                "verified_in_replay": [
                    "fixture_sha256 (bytes + canonical-library authenticity)",
                    "prompt_sha256 (bytes + mission consistency)",
                    "events_sha256", "repo_before/after snapshot integrity",
                    "artifact hashes via artifact-manifest",
                ],
                "adapter_attested_only": [
                    "product_tag/commit/tree", "installed_payload_sha256",
                    "adapter_name/version/sha256", "host",
                    "harness_commit (cross-checked when the scoring checkout is available)",
                ],
            },
            "bundle_sha256": "2" * 64, "scorer_commit": "3" * 40,
            "properties": properties,
            "host_safety": {
                "schema": "implementaudit-host-safety-v1", "status": "PASS",
                "failed_invariant": None, "failed_status": None, "findings": [],
            },
            "adjudication": {
                "schema": "implementaudit-eval-adjudication-v1",
                "product_status": "PASS", "host_status": "PASS",
                "overall_status": "PASS",
                "property_evidence_complete": True,
                "all_required_properties_true": True,
                "product_failed_invariant": None,
                "host_failed_invariant": None,
                "host_failed_status": None, "failed_domain": None,
                "failed_invariant": None,
            },
            "failed_domain": None, "failed_invariant": None,
            "evidence": ["synthetic retained evidence"], "reason": None,
        },
    }


def make_driver(module, root, mission_executor=executor):
    root = pathlib.Path(root)
    packet = valid_packet()
    for row in packet["fixtures"]:
        fixture_path = HERE.parent / row["path"]
        row["sha256"] = hashlib.sha256(fixture_path.read_bytes()).hexdigest()
    packet_path = root / "intent.json"
    packet_path.write_bytes(encoded(packet))
    attestation = root / "L-host-attestation.json"
    attestation.write_bytes(encoded({
        "id": "matrix-L-host", "shell_dialect": "posix",
        "executables": {"cat": "posix:cat"},
    }))
    return module.CampaignDriver(
        packet_path=packet_path,
        repo_root=HERE.parent,
        campaign_root=root / "campaign",
        candidate_checkout=root / "candidate",
        runtime_root=root / "runtime",
        attestation=attestation,
        mission_executor=mission_executor,
        execution_mode="test",
        live_validator=lambda packet, repo: packet,
        identity_validator=lambda packet, **paths: None,
    )


def complete_summaries(driver):
    packet, packet_raw, freeze_sha = driver._load_packet()
    descriptor = driver._stage_descriptor(packet, packet_raw, freeze_sha)
    rows = matrix_contract.lifecycle.validate_terminal_prefix(
        driver.campaign_root, descriptor["missions"],
        stop_states=descriptor["stop_states"],
        allowed_root=descriptor["allowed_root"])
    return packet, freeze_sha, driver._luna_summaries(
        packet, freeze_sha, rows)


def write_independent_result(driver, summaries, *, mutate=None):
    packet, _, freeze_sha = driver._load_packet()
    rows = json.loads(json.dumps(summaries))
    if mutate is not None:
        mutate(rows)
    value = {
        "schema":
            "implementaudit-candidate-matrix-luna-independent-rederivation-v1",
        "campaign": packet["campaign"], "freeze_sha256": freeze_sha,
        "contract_sha256": packet["artifact_contract"]["sha256"],
        "luna_stage_status": "PASS",
        "disposition": "INCOMPLETE_PENDING_OPUS",
        "luna_stage_accepted": True, "accepted": False,
        "cell_count": 14, "cells": rows, "claims": dict(FINAL_CLAIMS),
    }
    path = (driver.campaign_root /
            "candidate-matrix-luna-independent-rederivation.json")
    path.write_bytes(encoded(value))
    return value


def expect_error(fragment, fn):
    try:
        fn()
    except (OSError, TypeError, ValueError) as exc:
        assert fragment.lower() in str(exc).lower(), str(exc)
    else:
        raise AssertionError(f"expected rejection containing {fragment!r}")


def main():
    module = load_module()
    assert module._exact_json_equal(False, False)
    assert not module._exact_json_equal(False, 0)
    with tempfile.TemporaryDirectory() as tmp:
        root = pathlib.Path(tmp)
        driver = make_driver(module, root)
        for expected in FIXTURES:
            result = driver.run_next()
            assert result["overall_status"] == "PASS"
            attempt = root / "campaign"
            status_paths = sorted(attempt.glob("attempt-*/attempt-status.json"))
            assert json.loads(status_paths[-1].read_text(
                encoding="utf-8"))["mission"]["fixture"] == expected
        try:
            driver.run_next()
        except ValueError as exc:
            assert "fourteen" in str(exc).lower() or "complete" in str(exc).lower()
        else:
            raise AssertionError("fifteenth attempt unexpectedly allowed")
        attempts = sorted((root / "campaign").glob("attempt-*"))
        assert len(attempts) == 14
        assert all((path / "attempt-terminal.json").is_file() for path in attempts)
        packet, freeze_sha, summaries = complete_summaries(driver)
        assert [row["fixture"] for row in summaries] == FIXTURES
        write_independent_result(driver, summaries)
        official = driver.finalize_luna_stage()
        assert official["disposition"] == "INCOMPLETE_PENDING_OPUS"
        assert official["luna_stage_accepted"] is True
        assert official["accepted"] is False
        assert official["cell_count"] == 14
        assert official["claims"] == FINAL_CLAIMS
        assert driver.validate_luna_stage() == official
        expect_error("create-once", driver.finalize_luna_stage)

    with tempfile.TemporaryDirectory() as tmp:
        calls = []

        def stopped(context):
            calls.append(context.mission["index"])
            return {
                "overall_status": "INVALID", "resolved_model": None,
                "host_run_root": None,
            }

        driver = make_driver(module, tmp, stopped)
        terminal = driver.run_next()
        assert terminal["overall_status"] == "INVALID"
        expect_error("stopped", driver.run_next)
        assert calls == [0]

    for position in (0, 7, 13):
        with tempfile.TemporaryDirectory() as tmp:
            driver = make_driver(module, tmp)
            for _ in range(position + 1):
                driver.run_next()
            packet, _, _ = driver._load_packet()
            attempt = driver.campaign_root / driver._attempt_name(
                packet["cells"][position])
            probe = (attempt / "host-custody" / attempt.name /
                     f"mutation-{position}.bin")
            probe.write_bytes(b"post-terminal mutation\n")
            expect_error("seal", driver.run_next)

    with tempfile.TemporaryDirectory() as tmp:
        driver = make_driver(module, tmp)
        for _ in range(14):
            driver.run_next()
        _packet, _freeze_sha, summaries = complete_summaries(driver)
        write_independent_result(
            driver, summaries,
            mutate=lambda rows: rows[7].__setitem__("fixture", "B3"))
        expect_error("disagree", driver.finalize_luna_stage)

    with tempfile.TemporaryDirectory() as tmp:
        driver = make_driver(module, tmp)
        driver.run_next()
        packet, _, _ = driver._load_packet()
        attempt = driver.campaign_root / driver._attempt_name(
            packet["cells"][0])
        alias = attempt / "attempt-status-alias.json"
        try:
            os.link(attempt / "attempt-status.json", alias)
        except OSError:
            pass
        else:
            expect_error("unexpected", driver.run_next)
            alias.unlink()
    print("candidate matrix campaign: PASS")


if __name__ == "__main__":
    main()
