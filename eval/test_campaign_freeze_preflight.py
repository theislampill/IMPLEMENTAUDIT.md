#!/usr/bin/env python3
"""Deterministic tests for Luna-only campaign freeze preflight."""
from __future__ import annotations

import copy
import hashlib
import json
import pathlib
import tempfile

import campaign_freeze_preflight as preflight


def write(path, value):
    pathlib.Path(path).write_text(
        json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8")


def write_test_live_ready(campaign, packet, base, execution_mode="test"):
    """Build a closed TEST_ONLY readiness boundary for driver unit tests."""
    base = pathlib.Path(base).absolute()
    base.mkdir(parents=True, exist_ok=True)
    native = base / "native-test-executable.bin"
    launcher = base / "launcher-test.py"
    auth = base / "auth-source-path.json"
    for path, payload in (
            (native, b"native test executable\n"),
            (launcher, b"test launcher\n"),
            (auth, b"opaque test auth locator; contents never read\n")):
        if not path.exists():
            path.write_bytes(payload)
    checkout_names = (
        ("candidate", "control") if campaign == "b3v4"
        else ("candidate",))
    checkouts = {}
    for name in checkout_names:
        path = base / name
        path.mkdir(exist_ok=True)
        checkouts[name] = {
            "path": str(path), "commit": "1" * 40,
            "tree": "2" * 40, "skill_tree": "3" * 40,
            "payload_sha256": "4" * 64,
            "clean": True, "disposable": True, "native": True,
        }
    runtime = base / "runtime"
    runtime.mkdir(exist_ok=True)
    config = (packet["configurations"]["L"]
              if campaign == "b3v4" else packet["configuration"])
    report = {
        "schema": preflight.LIVE_READY_SCHEMAS[campaign],
        "campaign": campaign,
        "freeze_sha256": hashlib.sha256(
            preflight.lifecycle.canonical_json_bytes(packet)).hexdigest(),
        "contract_sha256": packet["artifact_contract"]["sha256"],
        "execution_mode": execution_mode,
        "disposition": ("READY_FOR_LUNA_EXECUTION"
                        if execution_mode == "production"
                        else "TEST_ONLY_NON_QUALIFYING"),
        "ready": execution_mode == "production",
        "mission_authorized": execution_mode == "production",
        "test_mock_authorized": execution_mode == "test",
        "created_at": "2026-07-29T00:00:00Z",
        "model_scope": preflight.MODEL_SCOPE,
        "host_attestation_binding": {
            "id": config["host_attestation"]["id"],
            "sha256": config["host_attestation"]["sha256"],
            "producer_command_sha256": "5" * 64,
            "producer_status": "PASS",
        },
        "native_executable_binding": {
            "path": str(native), "version": "test-native-1",
            "sha256": hashlib.sha256(native.read_bytes()).hexdigest(),
        },
        "launcher_binding": {
            "path": str(launcher),
            "sha256": hashlib.sha256(launcher.read_bytes()).hexdigest(),
            "evaluated_surface_role": "host-runner",
            "evaluated_surface_manifest_sha256": "6" * 64,
        },
        "checkout_bindings": checkouts,
        "runtime_root_binding": {
            "path": str(runtime), "disposable": True,
            "initial_empty": True,
        },
        "authorization_binding": {
            "acknowledgement_sha256": "7" * 64,
            "metered_api_spend": "FORBIDDEN",
            "launch_authorized": execution_mode == "production",
            "codex_auth_source_path": str(auth),
            "auth_contents_read": False,
        },
        "cross_host_validation": {
            "status": "PASS", "launcher_path": str(launcher),
            "native_executable_path": str(native),
            "native_executable_version": "test-native-1",
            "checkout_paths": {
                name: row["path"] for name, row in checkouts.items()},
            "runtime_root_path": str(runtime),
            "executable_resolution": "PASS",
        },
        "producer": {
            "command": "test-only-readiness-producer",
            "command_sha256": "8" * 64, "argv_sha256": "9" * 64,
            "status": "PASS",
        },
    }
    path = base / f"{campaign}-test-live-readiness.json"
    write(path, report)
    return path


def expect_error(fragment, action):
    try:
        action()
    except (OSError, TypeError, ValueError) as exc:
        assert fragment.lower() in str(exc).lower(), str(exc)
    else:
        raise AssertionError(f"expected error containing {fragment!r}")


def fixtures(base):
    freeze = {
        "schema": "implementaudit-b3v4-freeze-input-preflight-v1",
        "disposition": "NOT_READY_TO_AUTHOR_FREEZE",
        "candidate_examined": {
            "branch": "fix/v0320-b3v4-freeze-sol",
            "commit": "1" * 40,
            "tree": "2" * 40,
            "clean_at_intake": True,
        },
        "packet_values": {
            "configurations": {
                "L": {
                    "model_requested": "gpt-5.6-luna",
                    "model_resolved_required": "gpt-5.6-luna",
                    "reasoning_effort": "max",
                    "auth_mode": "chatgpt-subscription",
                },
            },
            "authorization": {"metered_api_spend": "FORBIDDEN"},
        },
        "missing_or_ambiguous_inputs": [
            {"id": "host-attestations", "severity": "blocker",
             "detail": "formal Luna attestation absent"},
            {"id": "fresh-product-checkouts", "severity": "blocker",
             "detail": "fresh exact-tree checkouts absent"},
        ],
    }
    execution = {
        "schema": "implementaudit-b3v4-luna-execution-preflight-v1",
        "disposition": "NOT_READY_FOR_LUNA_EXECUTION",
        "read_only": True,
        "mission_executed": False,
        "freeze_created": False,
        "luna": {
            "model_requested": "gpt-5.6-luna",
            "model_resolved_required": "gpt-5.6-luna",
            "reasoning_effort": "max",
            "auth_mode": "chatgpt-subscription",
            "metered_api_spend": "FORBIDDEN",
            "auth_file_path": "/secret/auth.json",
            "auth_contents_read": False,
        },
        "blockers": [
            {"id": "LUNA_HOST_ATTESTATION_MISSING",
             "detail": "formal attestation absent"},
            {"id": "TEMP_AUTH_CUSTODY_UNBOUND",
             "detail": "auth copy boundary absent"},
        ],
    }
    freeze_path = base / "freeze.json"
    execution_path = base / "execution.json"
    write(freeze_path, freeze)
    write(execution_path, execution)
    return freeze_path, execution_path, freeze, execution


def main():
    # Governing round-2 RED: the implementation must expose the separate live
    # packet-bound READY validator; legacy NOT_READY conversion is insufficient.
    expect_error(
        "live READY",
        lambda: preflight.validate_live_ready(
            "b3v4", {}, pathlib.Path("missing-live-boundary.json")))

    with tempfile.TemporaryDirectory(prefix="live-ready-mode-boundary-") as tmp:
        packet = {
            "artifact_contract": {"sha256": "a" * 64},
            "configurations": {"L": {
                "host_attestation": {
                    "id": "b3v4-L-host", "sha256": "b" * 64},
            }},
        }
        report_path = write_test_live_ready(
            "b3v4", packet, pathlib.Path(tmp) / "ready")
        report, _ = preflight.validate_live_ready(
            "b3v4", packet, report_path, execution_mode="test")
        assert report["disposition"] == "TEST_ONLY_NON_QUALIFYING"
        expect_error(
            "mode",
            lambda: preflight.validate_live_ready(
                "b3v4", packet, report_path,
                execution_mode="production"))

    with tempfile.TemporaryDirectory(prefix="campaign-preflight-") as tmp:
        base = pathlib.Path(tmp)
        freeze_path, execution_path, freeze, execution = fixtures(base)
        for campaign, schema in (
                ("b3v4", "implementaudit-b3v4-luna-freeze-preflight-v1"),
                ("candidate-matrix",
                 "implementaudit-candidate-matrix-luna-freeze-preflight-v1")):
            output = base / f"{campaign}.json"
            report = preflight.inspect_legacy_preflights(
                campaign, freeze_path, execution_path, output)
            assert report["schema"] == schema
            assert report["disposition"] == "NOT_READY"
            assert report["ready"] is False
            assert report["model_scope"] == {
                "model": "gpt-5.6-luna",
                "reasoning_effort": "max",
                "auth_mode": "chatgpt-subscription",
                "metered_api_spend": "FORBIDDEN",
            }
            raw = output.read_text(encoding="utf-8")
            assert "auth.json" not in raw
            assert "secret" not in raw
            expect_error(
                "create-once",
                lambda: preflight.inspect_legacy_preflights(
                    campaign, freeze_path, execution_path, output))

        for label, mutate, fragment in (
                ("ready", lambda f, e: f.update(
                    disposition="READY_TO_AUTHOR_FREEZE"), "not-ready"),
                ("terra", lambda f, e: f["packet_values"][
                    "configurations"]["L"].update(
                        model_requested="gpt-5.6-terra"), "luna"),
                ("unauthorized-config", lambda f, e: f["packet_values"][
                    "configurations"].update(T={}), "luna-only"),
                ("metered", lambda f, e: f["packet_values"][
                    "authorization"].update(
                        metered_api_spend="ALLOWED"), "metered"),
                ("contents", lambda f, e: e["luna"].update(
                    auth_contents_read=True), "credential")):
            changed_f = copy.deepcopy(freeze)
            changed_e = copy.deepcopy(execution)
            mutate(changed_f, changed_e)
            fp = base / f"{label}-freeze.json"
            ep = base / f"{label}-execution.json"
            write(fp, changed_f)
            write(ep, changed_e)
            expect_error(
                fragment,
                lambda fp=fp, ep=ep, label=label:
                preflight.inspect_legacy_preflights(
                    "b3v4", fp, ep, base / f"{label}-out.json"))

        expect_error(
            "campaign",
            lambda: preflight.inspect_legacy_preflights(
                "opus", freeze_path, execution_path, base / "bad.json"))
    print("CAMPAIGN-FREEZE-PREFLIGHT-PASS")


if __name__ == "__main__":
    main()
