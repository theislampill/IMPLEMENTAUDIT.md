#!/usr/bin/env python3
"""Read-only Luna freeze-input preflight over retained legacy inventories."""
from __future__ import annotations

import argparse
import hashlib
import os
import pathlib
import stat

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
LIVE_READY_SCHEMAS = {
    "b3v4": "implementaudit-b3v4-luna-live-launch-readiness-v1",
    "candidate-matrix":
        "implementaudit-candidate-matrix-luna-live-launch-readiness-v1",
}
LIVE_READY_FIELDS = {
    "schema", "campaign", "freeze_sha256", "contract_sha256",
    "execution_mode", "disposition", "ready", "mission_authorized",
    "test_mock_authorized", "created_at", "model_scope",
    "host_attestation_binding", "native_executable_binding",
    "launcher_binding", "checkout_bindings", "runtime_root_binding",
    "authorization_binding", "cross_host_validation", "producer",
}


def _exact(value, fields, owner):
    if type(value) is not dict or set(value) != set(fields):
        raise ValueError(f"{owner} fields invalid")
    return value


def _digest(value, owner):
    if (type(value) is not str or len(value) != 64 or
            any(char not in "0123456789abcdef" for char in value)):
        raise ValueError(f"{owner} SHA-256 invalid")


def _regular_path(path, owner, *, read_bytes=False):
    if type(path) is not str or not pathlib.Path(path).is_absolute():
        raise ValueError(f"{owner} path must be absolute")
    lexical = pathlib.Path(path).absolute()
    try:
        canonical = lexical.resolve(strict=True)
        observed = os.lstat(lexical)
    except OSError as exc:
        raise ValueError(f"{owner} unavailable") from exc
    if (canonical != lexical or stat.S_ISLNK(observed.st_mode) or
            bool(getattr(observed, "st_file_attributes", 0) &
                 getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)) or
            observed.st_nlink != 1):
        raise ValueError(f"{owner} link, reparse, or hardlink forbidden")
    if read_bytes and not stat.S_ISREG(observed.st_mode):
        raise ValueError(f"{owner} must be a regular file")
    return lexical


def _absolute_directory(path, owner):
    lexical = _regular_path(path, owner)
    if not lexical.is_dir():
        raise ValueError(f"{owner} must be a directory")
    return lexical


def validate_live_ready(campaign, packet, report_path,
                        *, execution_mode="production"):
    """Validate the separate packet-bound live launch boundary.

    This function never reads authentication contents.  Test-only evidence is
    intentionally incapable of authorizing a production driver.
    """
    if campaign not in LIVE_READY_SCHEMAS:
        raise ValueError("live READY campaign invalid")
    if execution_mode not in ("production", "test"):
        raise ValueError("live READY execution mode invalid")
    if type(packet) is not dict:
        raise ValueError("live READY packet invalid")
    report_path = pathlib.Path(report_path).absolute()
    try:
        raw = lifecycle.read_custodied_bytes(
            report_path, "live READY report", root=report_path.parent)
        report = lifecycle.decode_strict_json_bytes(
            raw, "live READY report", require_object=True)
    except OSError as exc:
        raise ValueError("live READY report unavailable") from exc
    _exact(report, LIVE_READY_FIELDS, "live READY report")
    if (report["schema"] != LIVE_READY_SCHEMAS[campaign] or
            report["campaign"] != campaign or
            report["execution_mode"] != execution_mode):
        raise ValueError("live READY report campaign/mode invalid")
    expected_freeze = hashlib.sha256(
        lifecycle.canonical_json_bytes(packet)).hexdigest()
    contract = packet.get("artifact_contract")
    if (report["freeze_sha256"] != expected_freeze or
            type(contract) is not dict or
            report["contract_sha256"] != contract.get("sha256")):
        raise ValueError("live READY frozen identity mismatch")
    _digest(report["freeze_sha256"], "live READY freeze")
    _digest(report["contract_sha256"], "live READY contract")
    if execution_mode == "production":
        expected_state = (
            "READY_FOR_LUNA_EXECUTION", True, True, False)
    else:
        expected_state = (
            "TEST_ONLY_NON_QUALIFYING", False, False, True)
    if tuple(report[key] for key in (
            "disposition", "ready", "mission_authorized",
            "test_mock_authorized")) != expected_state:
        raise ValueError("live READY authorization disposition invalid")
    if report["model_scope"] != MODEL_SCOPE:
        raise ValueError("live READY Luna-only model scope invalid")

    host = _exact(report["host_attestation_binding"], {
        "id", "sha256", "producer_command_sha256", "producer_status",
    }, "live READY host attestation")
    _digest(host["sha256"], "live READY host attestation")
    _digest(host["producer_command_sha256"],
            "live READY host attestation producer")
    configs = packet.get("configurations")
    luna = (configs.get("L") if type(configs) is dict
            else packet.get("configuration"))
    frozen_host = luna.get("host_attestation") if type(luna) is dict else None
    if (type(frozen_host) is not dict or host["id"] != frozen_host.get("id") or
            host["sha256"] != frozen_host.get("sha256") or
            host["producer_status"] != "PASS"):
        raise ValueError("live READY host attestation binding invalid")

    native = _exact(report["native_executable_binding"], {
        "path", "version", "sha256",
    }, "live READY native executable")
    launcher = _exact(report["launcher_binding"], {
        "path", "sha256", "evaluated_surface_role",
        "evaluated_surface_manifest_sha256",
    }, "live READY launcher")
    native_path = _regular_path(
        native["path"], "live READY native executable", read_bytes=True)
    launcher_path = _regular_path(
        launcher["path"], "live READY launcher", read_bytes=True)
    for row, owner, path in (
            (native, "native executable", native_path),
            (launcher, "launcher", launcher_path)):
        _digest(row["sha256"], f"live READY {owner}")
        if hashlib.sha256(path.read_bytes()).hexdigest() != row["sha256"]:
            raise ValueError(f"live READY {owner} hash drift")
    if native_path == launcher_path or not native["version"]:
        raise ValueError("live READY launcher/native distinction invalid")

    checkouts = report["checkout_bindings"]
    expected_checkout_names = (
        {"candidate", "control"} if campaign == "b3v4"
        else {"candidate"})
    if type(checkouts) is not dict or set(checkouts) != expected_checkout_names:
        raise ValueError("live READY checkout coverage invalid")
    for name, row in checkouts.items():
        _exact(row, {
            "path", "commit", "tree", "skill_tree", "payload_sha256",
            "clean", "disposable", "native",
        }, f"live READY {name} checkout")
        _absolute_directory(row["path"], f"live READY {name} checkout")
        if (row["clean"] is not True or row["disposable"] is not True or
                row["native"] is not True):
            raise ValueError("live READY checkout state invalid")
        for key in ("commit", "tree", "skill_tree"):
            value = row[key]
            if (type(value) is not str or len(value) != 40 or
                    any(char not in "0123456789abcdef" for char in value)):
                raise ValueError(f"live READY checkout {key} invalid")
        _digest(row["payload_sha256"], "live READY checkout payload")

    runtime = _exact(report["runtime_root_binding"], {
        "path", "disposable", "initial_empty",
    }, "live READY runtime root")
    runtime_path = _absolute_directory(
        runtime["path"], "live READY runtime root")
    if (runtime["disposable"] is not True or
            runtime["initial_empty"] is not True):
        raise ValueError("live READY runtime root declaration invalid")

    authorization = _exact(report["authorization_binding"], {
        "acknowledgement_sha256", "metered_api_spend",
        "launch_authorized", "codex_auth_source_path",
        "auth_contents_read",
    }, "live READY authorization")
    _digest(authorization["acknowledgement_sha256"],
            "live READY acknowledgement")
    _regular_path(
        authorization["codex_auth_source_path"],
        "live READY authentication source")
    if (authorization["metered_api_spend"] != "FORBIDDEN" or
            authorization["auth_contents_read"] is not False or
            authorization["launch_authorized"] is not
            (execution_mode == "production")):
        raise ValueError("live READY authorization invalid")

    cross = _exact(report["cross_host_validation"], {
        "status", "launcher_path", "native_executable_path",
        "native_executable_version", "checkout_paths", "runtime_root_path",
        "executable_resolution",
    }, "live READY cross-host validation")
    if (cross["status"] != "PASS" or
            cross["launcher_path"] != str(launcher_path) or
            cross["native_executable_path"] != str(native_path) or
            cross["native_executable_version"] != native["version"] or
            cross["checkout_paths"] != {
                name: row["path"] for name, row in checkouts.items()} or
            cross["runtime_root_path"] != str(runtime_path) or
            cross["executable_resolution"] != "PASS"):
        raise ValueError("live READY cross-host validation invalid")
    producer = _exact(report["producer"], {
        "command", "command_sha256", "argv_sha256", "status",
    }, "live READY producer")
    for key in ("command_sha256", "argv_sha256"):
        _digest(producer[key], f"live READY producer {key}")
    if (type(producer["command"]) is not str or not producer["command"] or
            producer["status"] != "PASS"):
        raise ValueError("live READY producer invalid")
    return report, raw


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
