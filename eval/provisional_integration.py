#!/usr/bin/env python3
"""Fail-closed evidence builder for the Luna-qualified merge disposition."""
from __future__ import annotations

import hashlib
import json
import pathlib
import re

import campaign_lifecycle as lifecycle
import evaluated_surfaces as surfaces


SCHEMA = "implementaudit-luna-qualified-integration-certificate-v1"
DISPOSITION = "LUNA_6_OF_6_AND_14_OF_14_GREEN_MERGED_TO_MAIN"
REQUIRED_GATES = (
    "deterministic", "package", "ci", "reproducibility",
    "independent-review",
)
B3_PLAN = (
    ("L", "candidate", 1), ("L", "control", 1),
    ("L", "control", 2), ("L", "candidate", 2),
    ("L", "control", 3), ("L", "candidate", 3),
)
MATRIX_FIXTURES = (
    "B0", "B1", "B2", "E1", "E2a", "E2b", "E3", "E4",
    "E5", "E6", "E7", "E8", "E9", "E10",
)
HEX64 = re.compile(r"^[0-9a-f]{64}$")
B3_CLAIMS = {
    "final_12_of_12": False, "cross_model_qualified": False,
    "release_authorized": False, "tag_authorized": False,
    "publication_authorized": False,
}
MATRIX_CLAIMS = {
    "final_28_of_28": False, "cross_model_qualified": False,
    "release_authorized": False, "tag_authorized": False,
    "publication_authorized": False,
}
PASS_ROW_COMMON = {
    "index", "config", "product_status", "host_status", "overall_status",
    "properties", "reason", "bundle_manifest_sha256", "raw_stdout_sha256",
    "native_session_sha256", "official_overall_status",
    "independent_overall_status", "model_resolved",
    "official_verdict_sha256",
}


def _exact(value, fields, owner):
    if type(value) is not dict or set(value) != set(fields):
        raise ValueError(f"{owner} fields invalid")
    return value


def _digest(value, owner):
    if type(value) is not str or not HEX64.fullmatch(value):
        raise ValueError(f"{owner} SHA-256 invalid")


def _canonical_sha(value):
    lifecycle.canonical_json_bytes(value)
    raw = (json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False) +
        "\n").encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _read_bound_json(binding, *, root, owner):
    surfaces.revalidate_file_binding(binding, root=root, owner=owner)
    path = pathlib.Path(root).absolute() / pathlib.PurePosixPath(
        binding["path"])
    raw = lifecycle.read_custodied_bytes(path, owner, root=root)
    if (len(raw) != binding["byte_length"] or
            hashlib.sha256(raw).hexdigest() != binding["sha256"]):
        raise ValueError(f"{owner} evidence byte drift")
    return lifecycle.decode_strict_json_bytes(
        raw, owner, require_object=True), raw


def _validate_claims(value, expected, owner):
    if type(value) is not dict or value != expected or any(
            type(item) is not bool for item in value.values()):
        raise ValueError(f"{owner} final claim boundary invalid")


def _validate_properties(value, owner):
    if type(value) is not dict or not value:
        raise ValueError(f"{owner} property evidence incomplete")
    for name, row in value.items():
        if type(name) is not str or not name:
            raise ValueError(f"{owner} property name invalid")
        _exact(row, {"state", "pass"}, f"{owner} property {name}")
        if row != {"state": "PASS", "pass": True}:
            raise ValueError(f"{owner} property {name} not PASS")


def _validate_rows(rows, campaign):
    matrix = campaign == surfaces.MATRIX_CAMPAIGN
    plan = MATRIX_FIXTURES if matrix else B3_PLAN
    if type(rows) is not list or len(rows) != len(plan):
        target = "fourteen" if matrix else "six"
        raise ValueError(f"{campaign} requires exact {target}-row Luna stage")
    expected_fields = PASS_ROW_COMMON | (
        {"fixture", "execution_mode"} if matrix else {"arm", "rep"})
    for index, (row, planned) in enumerate(zip(rows, plan)):
        _exact(row, expected_fields, f"{campaign} row {index}")
        if type(row["index"]) is not int or row["index"] != index:
            raise ValueError(f"{campaign} row order invalid")
        if row["config"] != "L":
            raise ValueError(f"{campaign} configuration/model invalid")
        if matrix:
            if (row["fixture"] != planned or
                    row["execution_mode"] != "production"):
                raise ValueError(f"{campaign} fixture/order/production invalid")
        else:
            config, arm, rep = planned
            if (row["config"], row["arm"], row["rep"]) != (
                    config, arm, rep):
                raise ValueError(f"{campaign} mission order invalid")
        if (row["product_status"], row["host_status"],
                row["overall_status"], row["official_overall_status"],
                row["independent_overall_status"]) != (
                    "PASS", "PASS", "PASS", "PASS", "PASS"):
            raise ValueError(f"{campaign} row is not complete PASS agreement")
        if row["model_resolved"] != "gpt-5.6-luna":
            raise ValueError(f"{campaign} model substitution detected")
        if row["reason"] is not None:
            raise ValueError(f"{campaign} unexplained row reason/error")
        _validate_properties(row["properties"], f"{campaign} row {index}")
        for field in (
                "bundle_manifest_sha256", "raw_stdout_sha256",
                "native_session_sha256", "official_verdict_sha256"):
            _digest(row[field], f"{campaign} row {index} {field}")
    return rows


def _validate_stage(stage, campaign, *, evidence_root):
    _exact(stage, {"execution_mode", "official", "independent", "evidence"},
           f"{campaign} stage binding")
    if stage["execution_mode"] != "production":
        raise ValueError(f"{campaign} stage must be production")
    matrix = campaign == surfaces.MATRIX_CAMPAIGN
    evidence = _exact(
        stage["evidence"], {"official", "independent", "stage_terminal"},
        f"{campaign} retained stage evidence")
    evidence_paths = [
        binding.get("path") if type(binding) is dict else None
        for binding in evidence.values()]
    if len(set(evidence_paths)) != 3:
        raise ValueError(f"{campaign} retained stage evidence path alias")
    retained_official, official_raw = _read_bound_json(
        evidence["official"], root=evidence_root,
        owner=f"{campaign} official retained result")
    retained_independent, independent_raw = _read_bound_json(
        evidence["independent"], root=evidence_root,
        owner=f"{campaign} independent retained result")
    terminal, _terminal_raw = _read_bound_json(
        evidence["stage_terminal"], root=evidence_root,
        owner=f"{campaign} retained stage terminal")
    if (retained_official != stage["official"] or
            retained_independent != stage["independent"]):
        raise ValueError(f"{campaign} retained stage evidence disagreement")
    independent_fields = {
        "schema", "campaign", "freeze_sha256", "contract_sha256",
        "luna_stage_status", "disposition", "luna_stage_accepted",
        "accepted", ("cell_count" if matrix else "mission_count"),
        ("cells" if matrix else "missions"), "claims",
    }
    if matrix:
        independent_fields.add("execution_mode")
    independent = _exact(
        stage["independent"], independent_fields,
        f"{campaign} independent stage")
    expected_independent_schema = (
        "implementaudit-candidate-matrix-luna-independent-rederivation-v1"
        if matrix else
        "implementaudit-b3v4-luna-independent-rederivation-v2")
    if (independent["schema"] != expected_independent_schema or
            independent["campaign"] != campaign):
        raise ValueError(f"{campaign} independent campaign/schema substitution")
    if matrix and independent["execution_mode"] != "production":
        raise ValueError(f"{campaign} independent stage must be production")
    count_name = "cell_count" if matrix else "mission_count"
    rows_name = "cells" if matrix else "missions"
    target = 14 if matrix else 6
    if (type(independent[count_name]) is not int or
            independent[count_name] != target or
            independent["luna_stage_status"] != "PASS" or
            independent["disposition"] != "INCOMPLETE_PENDING_OPUS" or
            independent["luna_stage_accepted"] is not True or
            independent["accepted"] is not False):
        raise ValueError(f"{campaign} independent Luna stage not accepted")
    _digest(independent["freeze_sha256"], f"{campaign} freeze")
    _digest(independent["contract_sha256"], f"{campaign} contract")
    rows = _validate_rows(independent[rows_name], campaign)
    claims = MATRIX_CLAIMS if matrix else B3_CLAIMS
    _validate_claims(independent["claims"], claims, f"{campaign} independent")

    official_fields = {
        "schema", "campaign", "freeze_sha256", "contract_sha256",
        "disposition", "luna_stage_accepted", "accepted", count_name,
        rows_name, "luna_identity", "independent_rederivation", "claims",
    }
    if matrix:
        official_fields.add("execution_mode")
    official = _exact(
        stage["official"], official_fields, f"{campaign} official stage")
    expected_official_schema = (
        "implementaudit-candidate-matrix-luna-result-v1"
        if matrix else "implementaudit-b3v4-luna-result-v2")
    if (official["schema"] != expected_official_schema or
            official["campaign"] != campaign):
        raise ValueError(f"{campaign} official campaign/schema substitution")
    if matrix and official["execution_mode"] != "production":
        raise ValueError(f"{campaign} official stage must be production")
    if (type(official[count_name]) is not int or
            official[count_name] != target or
            official["disposition"] != "INCOMPLETE_PENDING_OPUS" or
            official["luna_stage_accepted"] is not True or
            official["accepted"] is not False or
            official["freeze_sha256"] != independent["freeze_sha256"] or
            official["contract_sha256"] != independent["contract_sha256"]):
        raise ValueError(f"{campaign} official Luna stage not accepted")
    _validate_claims(official["claims"], claims, f"{campaign} official")
    if official[rows_name] != rows:
        raise ValueError(f"{campaign} official/independent agreement invalid")
    identity = _exact(
        official["luna_identity"], {
            "config", "host", "model_resolved_required",
            "host_attestation_id", "host_attestation_sha256",
        }, f"{campaign} Luna identity")
    if (identity["config"] != "L" or
            identity["model_resolved_required"] != "gpt-5.6-luna" or
            type(identity["host"]) is not str or not identity["host"] or
            type(identity["host_attestation_id"]) is not str or
            not identity["host_attestation_id"]):
        raise ValueError(f"{campaign} Luna host/model identity invalid")
    _digest(identity["host_attestation_sha256"],
            f"{campaign} host attestation")
    rederivation = _exact(
        official["independent_rederivation"], {
            "path", "sha256", "schema", "contract_id",
            "implementation_sha256",
        }, f"{campaign} independent binding")
    independent_sha = hashlib.sha256(independent_raw).hexdigest()
    official_sha = hashlib.sha256(official_raw).hexdigest()
    if (rederivation["schema"] != independent["schema"] or
            rederivation["sha256"] != independent_sha):
        raise ValueError(
            f"{campaign} independent rederivation evidence binding invalid")
    _digest(rederivation["implementation_sha256"],
            f"{campaign} independent implementation")
    stage_binding = {
        "campaign": campaign, "stage": "LUNA",
        "stage_schema": (
            "implementaudit-candidate-matrix-luna-stage-v1"
            if matrix else "implementaudit-b3v4-luna-stage-v2"),
        "mission_count": target,
        "freeze_sha256": independent["freeze_sha256"],
        "contract_sha256": independent["contract_sha256"],
        "official_result_sha256": official_sha,
        "independent_rederivation_sha256": independent_sha,
        "independent_rederiver_contract": rederivation["contract_id"],
        "luna_identity": identity,
        "claims": claims,
    }
    if matrix:
        stage_binding.update({
            "execution_mode": "production",
            "disposition": "INCOMPLETE_PENDING_OPUS",
            "luna_stage_accepted": True,
        })
    terminal = _exact(terminal, {
        "schema", "campaign", "stage", "stage_schema", "mission_count",
        "binding_sha256", "stage_snapshot_sha256",
    }, f"{campaign} stage terminal")
    if (terminal["schema"] !=
            "implementaudit-staged-campaign-terminal-v1" or
            terminal["campaign"] != campaign or terminal["stage"] != "LUNA" or
            terminal["stage_schema"] != stage_binding["stage_schema"] or
            type(terminal["mission_count"]) is not int or
            terminal["mission_count"] != target or
            terminal["binding_sha256"] != hashlib.sha256(
                lifecycle.canonical_json_bytes(stage_binding)).hexdigest()):
        raise ValueError(f"{campaign} stage terminal binding invalid")
    _digest(terminal["stage_snapshot_sha256"],
            f"{campaign} stage snapshot")
    return {
        "campaign": campaign,
        "freeze_sha256": independent["freeze_sha256"],
        "contract_sha256": independent["contract_sha256"],
        "official_result_sha256": official_sha,
        "independent_rederivation_sha256": independent_sha,
        "stage_terminal_sha256":
            evidence["stage_terminal"]["sha256"],
        "accepted_count": target,
        "execution_mode": "production",
    }


def validate_inputs(inputs, *, evidence_root, surface_root=None):
    _exact(inputs, {
        "b3_stage", "matrix_stage", "gates", "before", "after"},
        "integration inputs")
    b3 = _validate_stage(
        inputs["b3_stage"], surfaces.B3_CAMPAIGN,
        evidence_root=evidence_root)
    matrix = _validate_stage(
        inputs["matrix_stage"], surfaces.MATRIX_CAMPAIGN,
        evidence_root=evidence_root)
    gates = inputs["gates"]
    if type(gates) is not list or [row.get("name") for row in gates
                                   if type(row) is dict] != list(REQUIRED_GATES):
        raise ValueError("integration gate evidence set/order invalid")
    for row in gates:
        surfaces.revalidate_file_binding(
            row, root=evidence_root,
            owner=f"integration gate {row.get('name')}")
    gate_paths = [row["path"] for row in gates]
    if len(set(gate_paths)) != len(gate_paths):
        raise ValueError("integration gate evidence path alias forbidden")
    for owner in ("before", "after"):
        _exact(inputs[owner], set(surfaces.CAMPAIGNS),
               f"integration {owner} manifests")
    comparisons = {}
    surface_root = evidence_root if surface_root is None else surface_root
    for campaign in surfaces.CAMPAIGNS:
        surfaces.revalidate_manifest(
            inputs["after"][campaign], root=surface_root)
        surfaces.compare_relevant_surfaces(
            inputs["before"][campaign], inputs["after"][campaign], campaign)
        comparisons[campaign] = {
            "equal_relevant_bytes": True,
            "before_manifest_sha256":
                _canonical_sha(inputs["before"][campaign]),
            "after_manifest_sha256":
                _canonical_sha(inputs["after"][campaign]),
        }
    return b3, matrix, gates, comparisons


def write_certificate(path, inputs, *, evidence_root, surface_root=None):
    path = pathlib.Path(path).absolute()
    b3, matrix, gates, comparisons = validate_inputs(
        inputs, evidence_root=evidence_root, surface_root=surface_root)
    certificate = {
        "schema": SCHEMA,
        "disposition": DISPOSITION,
        "b3_luna": b3,
        "matrix_luna": matrix,
        "gates": gates,
        "surface_comparisons": comparisons,
        "release_authorized": False,
        "tag_authorized": False,
        "publication_authorized": False,
        "final_cross_model_qualified": False,
    }
    try:
        lifecycle.write_new_json(path, certificate)
    except FileExistsError as exc:
        raise ValueError("create-once integration certificate exists") from exc
    return certificate
