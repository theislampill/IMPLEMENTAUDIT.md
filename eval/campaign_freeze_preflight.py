#!/usr/bin/env python3
"""Read-only Luna freeze-input preflight over retained legacy inventories."""
from __future__ import annotations

import argparse
import hashlib
import pathlib

import campaign_lifecycle as lifecycle


CAMPAIGNS = {
    "b3v4": "implementaudit-b3v4-luna-freeze-preflight-v1",
    "candidate-matrix":
        "implementaudit-candidate-matrix-luna-freeze-preflight-v1",
}
MODEL_SCOPE = {
    "model": "gpt-5.6-luna",
    "reasoning_effort": "max",
    "auth_mode": "chatgpt-subscription",
    "metered_api_spend": "FORBIDDEN",
}
RESOLVED_BY_CURRENT_LUNA_CONTRACT = {
    "staged-order-pause-semantics",
    "LUNA_FIRST_ORDER_CONTRADICTION",
}


def _read(path, owner):
    path = pathlib.Path(path).absolute()
    raw = lifecycle.read_custodied_bytes(path, owner, root=path.parent)
    return lifecycle.decode_strict_json_bytes(
        raw, owner, require_object=True), raw


def _nonempty(value, owner):
    if type(value) is not str or not value:
        raise ValueError(f"{owner} must be a nonempty string")


def _blockers(value, owner):
    if type(value) is not list or not value:
        raise ValueError(f"{owner} blockers missing")
    rows = []
    for row in value:
        if type(row) is not dict:
            raise ValueError(f"{owner} blocker invalid")
        if not {"id", "detail"}.issubset(row):
            raise ValueError(f"{owner} blocker fields invalid")
        _nonempty(row["id"], f"{owner} blocker id")
        _nonempty(row["detail"], f"{owner} blocker detail")
        rows.append({"id": row["id"], "source": owner})
    return rows


def inspect_legacy_preflights(campaign, freeze_inventory,
                              execution_preflight, output):
    if campaign not in CAMPAIGNS:
        raise ValueError("campaign must be b3v4 or candidate-matrix")
    freeze, freeze_raw = _read(
        freeze_inventory, "retained freeze-input preflight")
    execution, execution_raw = _read(
        execution_preflight, "retained Luna execution preflight")
    if (freeze.get("schema") !=
            "implementaudit-b3v4-freeze-input-preflight-v1" or
            freeze.get("disposition") != "NOT_READY_TO_AUTHOR_FREEZE"):
        raise ValueError("retained freeze inventory is not-ready")
    if (execution.get("schema") !=
            "implementaudit-b3v4-luna-execution-preflight-v1" or
            execution.get("disposition") !=
            "NOT_READY_FOR_LUNA_EXECUTION" or
            execution.get("read_only") is not True or
            execution.get("mission_executed") is not False or
            execution.get("freeze_created") is not False):
        raise ValueError("retained execution preflight is not read-only NOT_READY")

    packet_values = freeze.get("packet_values")
    if type(packet_values) is not dict:
        raise ValueError("retained packet values missing")
    configs = packet_values.get("configurations")
    if (type(configs) is not dict or
            set(configs) not in ({"L"}, {"L", "O"})):
        raise ValueError("retained scope is not Luna-only")
    config = configs["L"]
    if type(config) is not dict:
        raise ValueError("retained Luna configuration invalid")
    observed_scope = {
        "model": config.get("model_requested"),
        "reasoning_effort": config.get("reasoning_effort"),
        "auth_mode": config.get("auth_mode"),
        "metered_api_spend":
            packet_values.get("authorization", {}).get(
                "metered_api_spend"),
    }
    if (config.get("model_resolved_required") != MODEL_SCOPE["model"] or
            observed_scope != MODEL_SCOPE):
        if observed_scope["metered_api_spend"] != "FORBIDDEN":
            raise ValueError("metered API use is forbidden")
        raise ValueError("only the exact approved Luna scope is admissible")

    luna = execution.get("luna")
    if type(luna) is not dict:
        raise ValueError("retained execution Luna observation missing")
    for key, expected in (
            ("model_requested", MODEL_SCOPE["model"]),
            ("model_resolved_required", MODEL_SCOPE["model"]),
            ("reasoning_effort", MODEL_SCOPE["reasoning_effort"]),
            ("auth_mode", MODEL_SCOPE["auth_mode"]),
            ("metered_api_spend", MODEL_SCOPE["metered_api_spend"])):
        if luna.get(key) != expected:
            raise ValueError(f"retained execution Luna {key} invalid")
    if luna.get("auth_contents_read") is not False:
        raise ValueError("credential contents must not be read or serialized")

    observed_blockers = _blockers(
        freeze.get("missing_or_ambiguous_inputs"), "freeze-inventory")
    observed_blockers.extend(
        _blockers(execution.get("blockers"), "execution-preflight"))
    resolved = sorted(
        [
            row for row in observed_blockers
            if row["id"] in RESOLVED_BY_CURRENT_LUNA_CONTRACT
        ],
        key=lambda row: (row["source"], row["id"]))
    blockers = [
        row for row in observed_blockers
        if row["id"] not in RESOLVED_BY_CURRENT_LUNA_CONTRACT
    ]
    if "O" in configs:
        blockers.append({
            "id": "LEGACY_OPUS_CONFIGURATION_OUT_OF_CURRENT_SCOPE",
            "source": "freeze-inventory",
        })
    blockers = sorted(
        {f"{row['source']}:{row['id']}": row for row in blockers}.values(),
        key=lambda row: (row["source"], row["id"]))
    report = {
        "schema": CAMPAIGNS[campaign],
        "campaign": campaign,
        "source_bindings": {
            "freeze_inventory_sha256":
                hashlib.sha256(freeze_raw).hexdigest(),
            "execution_preflight_sha256":
                hashlib.sha256(execution_raw).hexdigest(),
        },
        "model_scope": MODEL_SCOPE,
        "blockers": blockers,
        "resolved_legacy_gaps": resolved,
        "disposition": "NOT_READY",
        "ready": False,
        "mission_authorized": False,
    }
    output = pathlib.Path(output)
    try:
        lifecycle.write_new_json(output, report)
    except FileExistsError as exc:
        raise ValueError("create-once preflight report exists") from exc
    return report


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "campaign", choices=tuple(CAMPAIGNS))
    parser.add_argument("--freeze-inventory", required=True)
    parser.add_argument("--execution-preflight", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args(argv)
    try:
        report = inspect_legacy_preflights(
            args.campaign, args.freeze_inventory,
            args.execution_preflight, args.output)
    except (OSError, TypeError, ValueError) as exc:
        print(f"CAMPAIGN-FREEZE-PREFLIGHT-NOT-READY: {exc}")
        return 2
    print(
        "CAMPAIGN-FREEZE-PREFLIGHT-NOT-READY "
        f"campaign={report['campaign']} blockers={len(report['blockers'])}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
