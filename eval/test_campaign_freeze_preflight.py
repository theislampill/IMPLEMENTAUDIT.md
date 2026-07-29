#!/usr/bin/env python3
"""Deterministic tests for Luna-only campaign freeze preflight."""
from __future__ import annotations

import copy
import json
import pathlib
import tempfile

import campaign_freeze_preflight as preflight


def write(path, value):
    pathlib.Path(path).write_text(
        json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8")


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
