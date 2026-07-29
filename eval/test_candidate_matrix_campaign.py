#!/usr/bin/env python3
"""Deterministic tests for the serialized Luna candidate-matrix driver."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import pathlib
import shutil
import tempfile

from test_candidate_matrix_freeze import valid_packet
from test_candidate_matrix_rederive import (
    build_campaign, load_module as load_rederive_module)
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
    rederiver_path = HERE / "candidate_matrix_rederive.py"
    packet["independent_rederiver"]["implementation_identity"]["sha256"] = (
        hashlib.sha256(rederiver_path.read_bytes()).hexdigest())
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


def assert_independent_andon_stopped(driver):
    independent = load_rederive_module().rederive_campaign(
        driver.campaign_root / "campaign-freeze.json",
        driver.campaign_root)
    assert independent["luna_stage_status"] in ("INVALID", "ERROR"), independent
    assert independent["disposition"] == "ANDON_STOPPED", independent
    assert independent["luna_stage_accepted"] is False, independent
    assert independent["accepted"] is False, independent


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
        "execution_mode": summaries[0]["execution_mode"],
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


def assert_real_rederive_finalize(module):
    with tempfile.TemporaryDirectory(
            prefix="candidate-matrix-real-finalize-") as tmp:
        campaign_root = pathlib.Path(tmp) / "campaign"
        build_campaign(campaign_root, execution_mode="test")
        rederiver = load_rederive_module()
        independent = rederiver.rederive_campaign(
            campaign_root / "campaign-freeze.json", campaign_root)
        assert independent["luna_stage_status"] == \
            "TEST_ONLY_NON_QUALIFYING", independent
        assert independent["disposition"] == "TEST_ONLY_NON_QUALIFYING"
        assert independent["luna_stage_accepted"] is False
        assert independent["accepted"] is False
        output = (
            campaign_root /
            "candidate-matrix-luna-independent-rederivation.json")
        rederiver.write_rederivation(
            output, independent, root=campaign_root)
        driver = module.CampaignDriver(
            packet_path=campaign_root / "campaign-freeze.json",
            repo_root=HERE.parent, campaign_root=campaign_root,
            candidate_checkout=pathlib.Path(tmp) / "candidate",
            runtime_root=pathlib.Path(tmp) / "runtime",
            attestation=None, mission_executor=lambda _context: None,
            execution_mode="test",
            live_validator=lambda packet, repo: packet,
            identity_validator=lambda packet, **paths: None,
        )
        expect_error("production", driver.finalize_luna_stage)
        assert not (
            campaign_root / "candidate-matrix-luna-result.json").exists()
        assert not (campaign_root / "luna-stage-terminal.json").exists()


def assert_production_shaped_rederive_finalize(module):
    with tempfile.TemporaryDirectory(
            prefix="candidate-matrix-production-finalize-") as tmp:
        campaign_root = pathlib.Path(tmp) / "campaign"
        build_campaign(campaign_root, execution_mode="production")
        rederiver = load_rederive_module()
        independent = rederiver.rederive_campaign(
            campaign_root / "campaign-freeze.json", campaign_root)
        assert independent["luna_stage_status"] == "PASS", independent
        assert independent["disposition"] == "INCOMPLETE_PENDING_OPUS"
        assert independent["luna_stage_accepted"] is True
        output = (
            campaign_root /
            "candidate-matrix-luna-independent-rederivation.json")
        rederiver.write_rederivation(
            output, independent, root=campaign_root)
        driver = module.CampaignDriver(
            packet_path=campaign_root / "campaign-freeze.json",
            repo_root=HERE.parent, campaign_root=campaign_root,
            candidate_checkout=pathlib.Path(tmp) / "candidate",
            runtime_root=pathlib.Path(tmp) / "runtime",
            execution_mode="production",
        )
        driver.live_validator = lambda packet, repo: packet
        driver.identity_validator = lambda packet, **paths: None
        official = driver.finalize_luna_stage()
        assert official["cells"] == independent["cells"]
        assert official["disposition"] == "INCOMPLETE_PENDING_OPUS"
        assert official["luna_stage_accepted"] is True
        assert official["accepted"] is False
        assert official["cell_count"] == 14
        assert driver.validate_luna_stage() == official


def assert_post_executor_custody_failure_terminal(module):
    with tempfile.TemporaryDirectory(
            prefix="candidate-matrix-terminal-transaction-") as tmp:
        calls = []

        def loses_custody(context):
            calls.append(context.mission["index"])
            outcome = executor(context)
            shutil.rmtree(context.attempt_root / "host-custody")
            return outcome

        driver = make_driver(module, tmp, loses_custody)
        terminal = driver.run_next()
        assert terminal["overall_status"] in ("INVALID", "ERROR")
        assert terminal["completed_attempt_seal"] is None
        assert terminal["stop_reason"]
        attempt = next(driver.campaign_root.glob("attempt-*"))
        terminal_path = attempt / "attempt-terminal.json"
        assert terminal_path.is_file()
        assert len(list(attempt.glob("attempt-terminal.json"))) == 1
        retained = json.loads(terminal_path.read_text(encoding="utf-8"))
        assert retained == terminal
        assert_independent_andon_stopped(driver)
        expect_error("stopped", driver.run_next)
        assert calls == [0]
        try:
            driver.finalize_luna_stage()
        except (OSError, TypeError, ValueError):
            pass
        else:
            raise AssertionError(
                "post-executor custody failure finalized a Luna stage")
        assert not (
            driver.campaign_root /
            "candidate-matrix-luna-result.json").exists()
        assert not (
            driver.campaign_root / "luna-stage-terminal.json").exists()


def assert_post_executor_terminal_step_failures(module):
    for label in ("official-verdict-retained-then-failed",
                  "completed-seal-failed",
                  "terminal-contract-failed"):
        with tempfile.TemporaryDirectory(
                prefix=f"candidate-matrix-{label}-") as tmp:
            calls = []

            def counted_executor(context):
                calls.append(context.mission["index"])
                return executor(context)

            driver = make_driver(module, tmp, counted_executor)
            restore = None
            if label == "official-verdict-retained-then-failed":
                original = module._write_official_verdict

                def retained_then_failed(*args, **kwargs):
                    original(*args, **kwargs)
                    raise ValueError("injected official verdict failure")

                module._write_official_verdict = retained_then_failed
                restore = lambda: setattr(
                    module, "_write_official_verdict", original)
            elif label == "completed-seal-failed":
                original = module._completed_attempt_seal

                def seal_failed(*_args, **_kwargs):
                    raise ValueError("injected completed seal failure")

                module._completed_attempt_seal = seal_failed
                restore = lambda: setattr(
                    module, "_completed_attempt_seal", original)
            else:
                original = module.contract.validate_artifact
                injected = {"done": False}

                def terminal_contract_failed(name, value, **kwargs):
                    if (name == "attempt_terminal" and
                            value.get("overall_status") == "PASS" and
                            not injected["done"]):
                        injected["done"] = True
                        raise ValueError("injected terminal contract failure")
                    return original(name, value, **kwargs)

                module.contract.validate_artifact = terminal_contract_failed
                restore = lambda: setattr(
                    module.contract, "validate_artifact", original)
            try:
                terminal = driver.run_next()
            finally:
                restore()
            assert terminal["overall_status"] in ("INVALID", "ERROR")
            assert terminal["completed_attempt_seal"] is None
            assert terminal["official_overall_status"] is None
            assert terminal["official_verdict_sha256"] is None
            assert terminal["stop_reason"]
            attempt = next(driver.campaign_root.glob("attempt-*"))
            assert len(list(attempt.glob("attempt-terminal.json"))) == 1
            retained = json.loads(
                (attempt / "attempt-terminal.json").read_text(
                    encoding="utf-8"))
            assert retained == terminal
            if label == "official-verdict-retained-then-failed":
                assert (attempt / "official-verdict.json").is_file()
            assert_independent_andon_stopped(driver)
            expect_error("stopped", driver.run_next)
            assert calls == [0]


def assert_terminal_publication_failures(module):
    original = module._write_new_json
    terminal_name = "attempt-terminal.json"
    marker_name = "campaign-andon.json"
    for label in (
            "one-time-pre-create", "valid-then-raise",
            "partial-then-raise", "persistent-failure",
            "conflicting-preexisting", "transient-marker-failure",
            "marker-valid-then-raise", "marker-partial",
            "marker-conflicting", "marker-persistent",
            "marker-retry-valid-then-raise"):
        with tempfile.TemporaryDirectory(
                prefix=f"candidate-matrix-terminal-publication-{label}-") as tmp:
            calls = []
            injected = {"count": 0}

            def counted_executor(context):
                calls.append(context.mission["index"])
                return executor(context)

            def publication_control(path, value):
                path = pathlib.Path(path)
                if path.name != terminal_name:
                    if path.name == marker_name:
                        marker_count = injected.setdefault("marker", 0)
                        injected["marker"] += 1
                        if (label == "transient-marker-failure" and
                                marker_count == 0):
                            raise OSError(
                                "injected pre-create campaign marker failure")
                        if (label == "marker-valid-then-raise" and
                                marker_count == 0):
                            original(path, value)
                            raise OSError(
                                "injected post-create campaign marker failure")
                        if (label in ("marker-partial",
                                      "marker-conflicting") and
                                marker_count == 0):
                            with open(path, "xb") as stream:
                                stream.write(
                                    b"{" if label == "marker-partial"
                                    else b"{}\n")
                            raise OSError(
                                "injected nonconforming campaign marker")
                        if label == "marker-persistent":
                            raise OSError(
                                "injected persistent campaign marker failure")
                        if label == "marker-retry-valid-then-raise":
                            if marker_count == 0:
                                raise OSError(
                                    "injected first campaign marker failure")
                            if marker_count == 1:
                                original(path, value)
                                raise OSError(
                                    "injected retry post-create marker failure")
                    return original(path, value)
                injected["count"] += 1
                if label == "one-time-pre-create" and injected["count"] == 1:
                    raise OSError("injected pre-create terminal failure")
                if label == "valid-then-raise" and injected["count"] == 1:
                    original(path, value)
                    raise OSError("injected post-create terminal failure")
                if label == "partial-then-raise" and injected["count"] == 1:
                    with open(path, "xb") as stream:
                        stream.write(b"{")
                    raise OSError("injected partial terminal failure")
                if label in ("persistent-failure",
                             "transient-marker-failure",
                             "marker-valid-then-raise", "marker-partial",
                             "marker-conflicting", "marker-persistent",
                             "marker-retry-valid-then-raise"):
                    raise OSError("injected persistent terminal failure")
                if label == "conflicting-preexisting" and injected["count"] == 1:
                    with open(path, "xb") as stream:
                        stream.write(b"{}\n")
                    raise FileExistsError("injected conflicting terminal")
                return original(path, value)

            driver = make_driver(module, tmp, counted_executor)
            module._write_new_json = publication_control
            result = None
            try:
                try:
                    result = driver.run_next()
                except OSError:
                    if label not in (
                            "marker-partial", "marker-conflicting",
                            "marker-persistent"):
                        raise
            finally:
                module._write_new_json = original
            attempt = next(driver.campaign_root.glob("attempt-*"))
            terminal_path = attempt / terminal_name
            marker_path = driver.campaign_root / marker_name
            assert calls == [0]
            assert len(list(attempt.glob(terminal_name))) <= 1
            if label == "valid-then-raise":
                assert result["overall_status"] == "PASS", result
                assert terminal_path.is_file()
                assert not marker_path.exists()
                independent = load_rederive_module().rederive_campaign(
                    driver.campaign_root / "campaign-freeze.json",
                    driver.campaign_root)
                assert independent["luna_stage_accepted"] is False, independent
                continue
            if label == "one-time-pre-create":
                assert result["overall_status"] in ("INVALID", "ERROR"), result
                assert result["completed_attempt_seal"] is None
                assert result["stop_reason"] == \
                    "attempt-terminal-publication-failure"
                assert terminal_path.is_file()
                assert not marker_path.exists()
            elif result is not None:
                assert result["schema"] == \
                    "implementaudit-candidate-matrix-campaign-andon-v1", result
                assert result["stop_reason"] == \
                    "attempt-terminal-publication-failure"
                assert marker_path.is_file()
            independent = load_rederive_module().rederive_campaign(
                driver.campaign_root / "campaign-freeze.json",
                driver.campaign_root)
            assert independent["disposition"] == "ANDON_STOPPED", independent
            assert independent["luna_stage_accepted"] is False, independent
            try:
                driver.run_next()
            except (OSError, TypeError, ValueError):
                pass
            else:
                raise AssertionError(
                    "terminal publication failure ran a next mission")
            assert calls == [0]
            try:
                driver.finalize_luna_stage()
            except (OSError, TypeError, ValueError):
                pass
            else:
                raise AssertionError(
                    "terminal publication failure finalized a Luna stage")
            assert not (
                driver.campaign_root /
                "candidate-matrix-luna-result.json").exists()
            assert not (
                driver.campaign_root / "luna-stage-terminal.json").exists()


def assert_malformed_marker_never_qualifies():
    with tempfile.TemporaryDirectory(
            prefix="candidate-matrix-malformed-marker-") as tmp:
        campaign_root = pathlib.Path(tmp) / "campaign"
        build_campaign(campaign_root, execution_mode="production")
        (campaign_root / "campaign-andon.json").write_bytes(b"{}\n")
        independent = load_rederive_module().rederive_campaign(
            campaign_root / "campaign-freeze.json", campaign_root)
        assert independent["disposition"] == "ANDON_STOPPED", independent
        assert independent["luna_stage_accepted"] is False, independent


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
        campaign_root = pathlib.Path(tmp) / "campaign"
        build_campaign(campaign_root, execution_mode="production")
        rederiver = load_rederive_module()
        independent = rederiver.rederive_campaign(
            campaign_root / "campaign-freeze.json", campaign_root)
        independent["cells"][7]["fixture"] = "B3"
        rederiver.write_rederivation(
            campaign_root /
            "candidate-matrix-luna-independent-rederivation.json",
            independent, root=campaign_root)
        driver = module.CampaignDriver(
            packet_path=campaign_root / "campaign-freeze.json",
            repo_root=HERE.parent, campaign_root=campaign_root,
            candidate_checkout=pathlib.Path(tmp) / "candidate",
            runtime_root=pathlib.Path(tmp) / "runtime",
            execution_mode="production",
        )
        driver.live_validator = lambda packet, repo: packet
        driver.identity_validator = lambda packet, **paths: None
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
    assert_real_rederive_finalize(module)
    assert_production_shaped_rederive_finalize(module)
    assert_post_executor_custody_failure_terminal(module)
    assert_post_executor_terminal_step_failures(module)
    assert_terminal_publication_failures(module)
    assert_malformed_marker_never_qualifies()
    print("candidate matrix campaign: PASS")


if __name__ == "__main__":
    main()
