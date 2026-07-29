#!/usr/bin/env python3
"""Custody-derived certificate for the Luna-qualified merge disposition."""
from __future__ import annotations

import hashlib
import os
import pathlib
import stat

import b3v4_campaign
import b3v4_contract
import b3v4_rederive
import campaign_lifecycle as lifecycle
import candidate_matrix_campaign
import candidate_matrix_contract
import candidate_matrix_rederive
import evaluated_surfaces as surfaces


SCHEMA = "implementaudit-luna-qualified-integration-certificate-v3"
DISPOSITION = "LUNA_6_OF_6_AND_14_OF_14_GREEN_MERGED_TO_MAIN"
REQUIRED_GATES = (
    "deterministic", "package", "ci", "reproducibility",
    "independent-review",
)
GATE_FILENAMES = {
    name: f"{name}-terminal.json" for name in REQUIRED_GATES
}


def _exact(value, fields, owner):
    if type(value) is not dict or set(value) != set(fields):
        raise ValueError(f"{owner} terminal schema fields invalid")
    return value


def _digest(value, owner):
    if (type(value) is not str or len(value) != 64 or
            any(char not in "0123456789abcdef" for char in value)):
        raise ValueError(f"{owner} SHA-256 invalid")


def _reparse_point(path_stat):
    return bool(getattr(path_stat, "st_file_attributes", 0) &
                getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400))


def _strict_directory_identity(path, owner):
    lexical = pathlib.Path(path).absolute()
    try:
        resolved = lexical.resolve(strict=True)
        if resolved != lexical:
            raise ValueError(f"{owner} link or reparse alias forbidden")
        current = pathlib.Path(lexical.anchor)
        for part in lexical.parts[1:]:
            current = current / part
            observed = os.lstat(current)
            if stat.S_ISLNK(observed.st_mode) or _reparse_point(observed):
                raise ValueError(f"{owner} link or reparse alias forbidden")
        before = os.lstat(lexical)
        if (not stat.S_ISDIR(before.st_mode) or
                stat.S_ISLNK(before.st_mode) or _reparse_point(before)):
            raise ValueError(f"{owner} must be a retained directory")
        after = os.lstat(lexical)
        if ((before.st_dev, before.st_ino, before.st_mode) !=
                (after.st_dev, after.st_ino, after.st_mode)):
            raise ValueError(f"{owner} identity changed during custody read")
    except ValueError:
        raise
    except OSError as exc:
        raise ValueError(f"{owner} retained directory unavailable") from exc
    return lexical, {
        "path": str(lexical),
        "canonical_path": str(resolved),
        "lexical": os.path.normcase(os.path.normpath(str(lexical))),
        "canonical": os.path.normcase(os.path.normpath(str(resolved))),
        "physical": (before.st_dev, before.st_ino),
    }


def _strict_directory(path, owner):
    return _strict_directory_identity(path, owner)[0]


def _identity_tokens(identity):
    return {
        ("lexical", identity["lexical"]),
        ("canonical", identity["canonical"]),
        ("physical", identity["physical"]),
    }


def _require_distinct_post_roots(pre_roots, post_roots):
    prior = []
    for campaign, identity in pre_roots.items():
        prior.append((f"{campaign} frozen pre root", identity))
    for campaign, identity in post_roots.items():
        for owner, previous in prior:
            if _identity_tokens(identity) & _identity_tokens(previous):
                raise ValueError(
                    f"{campaign} post-integration root identity aliases "
                    f"{owner}")
        prior.append((f"{campaign} post-integration root", identity))


def _require_post_files_distinct_from_pre(
        post_campaign, post_identities, pre_identities):
    prior = {}
    for campaign, roles in pre_identities.items():
        for role, identity in roles.items():
            for token in _identity_tokens(identity):
                prior[token] = f"{campaign}:{role}"
    for role, identity in post_identities.items():
        aliases = {
            prior[token] for token in _identity_tokens(identity)
            if token in prior
        }
        if aliases:
            raise ValueError(
                f"{post_campaign} post-integration surface {role} aliases "
                f"pre-integration physical identity {sorted(aliases)[0]}")


def _canonical_sha(value):
    return hashlib.sha256(lifecycle.canonical_json_bytes(value)).hexdigest()


def _read_root_json(root, name, owner):
    path = pathlib.Path(root) / name
    raw = lifecycle.read_custodied_bytes(path, owner, root=root)
    value = lifecycle.decode_strict_json_bytes(
        raw, owner, require_object=True)
    return value, raw


def _packet_and_manifest(campaign_root, surface_root, campaign):
    campaign_root = _strict_directory(campaign_root, f"{campaign} campaign root")
    surface_root = _strict_directory(surface_root, f"{campaign} surface root")
    packet, raw = _read_root_json(
        campaign_root, "campaign-freeze.json", f"{campaign} frozen packet")
    if campaign == surfaces.B3_CAMPAIGN:
        b3v4_contract.validate_freeze_envelope(packet)
    else:
        candidate_matrix_contract.validate_freeze_envelope(packet)
    manifest = packet["evaluated_surfaces"]
    surfaces.revalidate_manifest(manifest, root=surface_root)
    return packet, raw, manifest


def _result_fields(campaign):
    if campaign == surfaces.B3_CAMPAIGN:
        return (
            "b3v4-luna-result.json",
            "b3v4-luna-independent-rederivation.json",
            "missions", "mission_count", 6)
    return (
        "candidate-matrix-luna-result.json",
        "candidate-matrix-luna-independent-rederivation.json",
        "cells", "cell_count", 14)


def _validate_stage(campaign_root, surface_root, campaign):
    packet, packet_raw, manifest = _packet_and_manifest(
        campaign_root, surface_root, campaign)
    packet_path = pathlib.Path(campaign_root) / "campaign-freeze.json"
    if campaign == surfaces.B3_CAMPAIGN:
        official = b3v4_campaign.validate_retained_luna_stage(
            packet_path, campaign_root, surface_root)
        rederived = b3v4_rederive.rederive_campaign(
            packet_path, campaign_root, surface_root)
    else:
        official = candidate_matrix_campaign.validate_retained_luna_stage(
            packet_path, campaign_root, surface_root)
        rederived = candidate_matrix_rederive.rederive_campaign(
            packet_path, campaign_root, surface_root)
    official_name, independent_name, rows_name, count_name, target = \
        _result_fields(campaign)
    retained_official, official_raw = _read_root_json(
        campaign_root, official_name, f"{campaign} official retained result")
    retained_independent, independent_raw = _read_root_json(
        campaign_root, independent_name,
        f"{campaign} independent retained result")
    terminal, terminal_raw = _read_root_json(
        campaign_root, "luna-stage-terminal.json",
        f"{campaign} retained stage terminal")
    if (lifecycle.canonical_json_bytes(retained_official) !=
            lifecycle.canonical_json_bytes(official)):
        raise ValueError(f"{campaign} official retained result drift")
    if (lifecycle.canonical_json_bytes(retained_independent) !=
            lifecycle.canonical_json_bytes(rederived)):
        raise ValueError(f"{campaign} independent retained result drift")
    if (type(official.get(count_name)) is not int or
            official[count_name] != target or
            type(rederived.get(count_name)) is not int or
            rederived[count_name] != target or
            official.get("luna_stage_accepted") is not True or
            rederived.get("luna_stage_accepted") is not True or
            official.get("accepted") is not False or
            rederived.get("accepted") is not False or
            official.get("disposition") != "INCOMPLETE_PENDING_OPUS" or
            rederived.get("disposition") != "INCOMPLETE_PENDING_OPUS"):
        raise ValueError(f"{campaign} retained Luna stage is not accepted")
    if (lifecycle.canonical_json_bytes(official.get(rows_name)) !=
            lifecycle.canonical_json_bytes(rederived.get(rows_name))):
        raise ValueError(f"{campaign} official/independent row disagreement")
    return {
        "campaign": campaign,
        "freeze_sha256": hashlib.sha256(packet_raw).hexdigest(),
        "contract_sha256": packet["artifact_contract"]["sha256"],
        "official_result_sha256": hashlib.sha256(official_raw).hexdigest(),
        "independent_rederivation_sha256":
            hashlib.sha256(independent_raw).hexdigest(),
        "stage_terminal_sha256": hashlib.sha256(terminal_raw).hexdigest(),
        "stage_snapshot_sha256": terminal["stage_snapshot_sha256"],
        "accepted_count": target,
        "execution_mode": "production",
    }, manifest


def _gate_identity(b3, matrix, manifests):
    return _canonical_sha({
        "b3_freeze_sha256": b3["freeze_sha256"],
        "matrix_freeze_sha256": matrix["freeze_sha256"],
        "b3_evaluated_surfaces_sha256":
            _canonical_sha(manifests[surfaces.B3_CAMPAIGN]),
        "matrix_evaluated_surfaces_sha256":
            _canonical_sha(manifests[surfaces.MATRIX_CAMPAIGN]),
    })


def derive_qualified_input_sha256(*, b3_campaign_root,
                                  matrix_campaign_root,
                                  b3_surface_root,
                                  matrix_surface_root):
    b3_packet, b3_raw, b3_manifest = _packet_and_manifest(
        b3_campaign_root, b3_surface_root, surfaces.B3_CAMPAIGN)
    matrix_packet, matrix_raw, matrix_manifest = _packet_and_manifest(
        matrix_campaign_root, matrix_surface_root,
        surfaces.MATRIX_CAMPAIGN)
    return _gate_identity(
        {
            "freeze_sha256": hashlib.sha256(b3_raw).hexdigest(),
            "contract_sha256": b3_packet["artifact_contract"]["sha256"],
        },
        {
            "freeze_sha256": hashlib.sha256(matrix_raw).hexdigest(),
            "contract_sha256":
                matrix_packet["artifact_contract"]["sha256"],
        },
        {
            surfaces.B3_CAMPAIGN: b3_manifest,
            surfaces.MATRIX_CAMPAIGN: matrix_manifest,
        })


def _string_list(value, owner):
    if (type(value) is not list or
            any(type(item) is not str or not item for item in value)):
        raise ValueError(f"{owner} must be an exact string list")


def _validate_gate_terminal(name, value, qualified_input_sha256):
    common = {"schema", "gate", "qualified_input_sha256", "exit_code"}
    if name == "deterministic":
        _exact(value, common | {"failed_checks"}, name)
        _string_list(value["failed_checks"], "deterministic failed checks")
        passed = value["exit_code"] == 0 and value["failed_checks"] == []
    elif name == "package":
        _exact(
            value, common | {
                "verification_passed", "package_manifest_sha256"}, name)
        _digest(value["package_manifest_sha256"], "package manifest")
        passed = (value["exit_code"] == 0 and
                  value["verification_passed"] is True)
    elif name == "ci":
        _exact(value, common | {"failed_jobs"}, name)
        _string_list(value["failed_jobs"], "CI failed jobs")
        passed = value["exit_code"] == 0 and value["failed_jobs"] == []
    elif name == "reproducibility":
        _exact(
            value, common | {
                "comparison_equal", "first_artifact_sha256",
                "second_artifact_sha256"}, name)
        _digest(value["first_artifact_sha256"], "first artifact")
        _digest(value["second_artifact_sha256"], "second artifact")
        passed = (
            value["exit_code"] == 0 and
            value["comparison_equal"] is True and
            value["first_artifact_sha256"] ==
            value["second_artifact_sha256"])
    elif name == "independent-review":
        _exact(value, {
            "schema", "gate", "reviewed_qualified_input_sha256",
            "verdict", "findings"}, name)
        _string_list(value["findings"], "independent review findings")
        passed = value["verdict"] == "PASS" and value["findings"] == []
        if value["reviewed_qualified_input_sha256"] != qualified_input_sha256:
            raise ValueError("independent-review qualified input mismatch")
    else:
        raise ValueError("unsupported integration gate")
    expected_schema = f"implementaudit-{name}-terminal-v1"
    if value["schema"] != expected_schema or value["gate"] != name:
        raise ValueError(f"{name} terminal schema identity invalid")
    if name != "independent-review":
        if type(value["exit_code"]) is not int:
            raise ValueError(f"{name} exit code type invalid")
        if value["qualified_input_sha256"] != qualified_input_sha256:
            raise ValueError(f"{name} qualified input mismatch")
    if not passed:
        raise ValueError(f"{name} terminal does not derive semantic PASS")


def _validate_gates(gate_root, qualified_input_sha256):
    gate_root = _strict_directory(gate_root, "integration gate root")
    gates = []
    for name in REQUIRED_GATES:
        filename = GATE_FILENAMES[name]
        value, raw = _read_root_json(
            gate_root, filename, f"integration gate {name}")
        _validate_gate_terminal(name, value, qualified_input_sha256)
        gates.append({
            "name": name,
            "semantic_status": "PASS",
            "path": filename,
            "byte_length": len(raw),
            "sha256": hashlib.sha256(raw).hexdigest(),
            "schema": value["schema"],
        })
    return gates


def _after_manifest(before, after_root, external_paths):
    if type(external_paths) is not dict:
        raise ValueError("post-integration external locators must be an object")
    expected_external_roles = {
        row["role"] for row in before["entries"]
        if pathlib.Path(row["path"]).is_absolute()
    }
    if set(external_paths) != expected_external_roles:
        raise ValueError(
            "post-integration external locator role coverage invalid")
    prior_paths = {
        row["role"]: row["path"] for row in before["entries"]
        if row["role"] in expected_external_roles
    }
    sources = []
    for row in before["entries"]:
        role = row["role"]
        path = external_paths.get(role, row["path"])
        if role in expected_external_roles:
            if (type(path) is not str or not pathlib.Path(path).is_absolute() or
                    "\\" in path):
                raise ValueError(
                    f"post-integration external locator invalid: {role}")
            if os.path.normcase(os.path.normpath(path)) == os.path.normcase(
                    os.path.normpath(prior_paths[role])):
                raise ValueError(
                    f"post-integration external locator reuses prior path: "
                    f"{role}")
        sources.append({"role": role, "path": path})
    return surfaces.build_manifest(
        before["campaign"], sources, root=after_root)


def _compare_after_bytes(before, after, campaign):
    surfaces.validate_manifest(before, campaign)
    surfaces.validate_manifest(after, campaign)
    prior = {row["role"]: row for row in before["entries"]}
    current = {row["role"]: row for row in after["entries"]}
    for role in surfaces.required_roles(campaign):
        for field in ("byte_length", "sha256"):
            if prior[role][field] != current[role][field]:
                raise ValueError(
                    f"evaluated surface byte drift: {role} ({field})")
    return True


def validate_inputs(*, b3_campaign_root, matrix_campaign_root,
                    b3_surface_root, matrix_surface_root,
                    b3_after_surface_root, matrix_after_surface_root,
                    gate_root, b3_after_external_paths=None,
                    matrix_after_external_paths=None):
    b3_surface_root, b3_pre_root_identity = _strict_directory_identity(
        b3_surface_root, f"{surfaces.B3_CAMPAIGN} frozen pre surface root")
    matrix_surface_root, matrix_pre_root_identity = \
        _strict_directory_identity(
            matrix_surface_root,
            f"{surfaces.MATRIX_CAMPAIGN} frozen pre surface root")
    b3, b3_before = _validate_stage(
        b3_campaign_root, b3_surface_root, surfaces.B3_CAMPAIGN)
    matrix, matrix_before = _validate_stage(
        matrix_campaign_root, matrix_surface_root,
        surfaces.MATRIX_CAMPAIGN)
    manifests = {
        surfaces.B3_CAMPAIGN: b3_before,
        surfaces.MATRIX_CAMPAIGN: matrix_before,
    }
    pre_root_identities = {
        surfaces.B3_CAMPAIGN: b3_pre_root_identity,
        surfaces.MATRIX_CAMPAIGN: matrix_pre_root_identity,
    }
    pre_file_identities = {
        surfaces.B3_CAMPAIGN: surfaces.custody_identity_map(
            b3_before, root=b3_surface_root),
        surfaces.MATRIX_CAMPAIGN: surfaces.custody_identity_map(
            matrix_before, root=matrix_surface_root),
    }
    b3_after_surface_root, b3_post_root_identity = \
        _strict_directory_identity(
            b3_after_surface_root,
            f"{surfaces.B3_CAMPAIGN} post-integration surface root")
    matrix_after_surface_root, matrix_post_root_identity = \
        _strict_directory_identity(
            matrix_after_surface_root,
            f"{surfaces.MATRIX_CAMPAIGN} post-integration surface root")
    post_root_identities = {
        surfaces.B3_CAMPAIGN: b3_post_root_identity,
        surfaces.MATRIX_CAMPAIGN: matrix_post_root_identity,
    }
    _require_distinct_post_roots(
        pre_root_identities, post_root_identities)
    qualified_input_sha256 = _gate_identity(b3, matrix, manifests)
    gates = _validate_gates(gate_root, qualified_input_sha256)
    comparisons = {}
    for campaign, before, after_root, external_paths, pre_root, post_root in (
            (surfaces.B3_CAMPAIGN, b3_before, b3_after_surface_root,
             b3_after_external_paths, b3_pre_root_identity,
             b3_post_root_identity),
            (surfaces.MATRIX_CAMPAIGN, matrix_before,
             matrix_after_surface_root, matrix_after_external_paths,
             matrix_pre_root_identity, matrix_post_root_identity)):
        after = _after_manifest(before, after_root, external_paths or {})
        post_file_identities = surfaces.custody_identity_map(
            after, root=after_root)
        _require_post_files_distinct_from_pre(
            campaign, post_file_identities, pre_file_identities)
        _compare_after_bytes(before, after, campaign)
        comparisons[campaign] = {
            "equal_relevant_bytes": True,
            "post_root_distinct_from_all_pre_and_post_roots": True,
            "post_files_distinct_from_all_pre_files": True,
            "pre_root": {
                "path": pre_root["path"],
                "canonical_path": pre_root["canonical_path"],
                "device": pre_root["physical"][0],
                "inode": pre_root["physical"][1],
            },
            "post_root": {
                "path": post_root["path"],
                "canonical_path": post_root["canonical_path"],
                "device": post_root["physical"][0],
                "inode": post_root["physical"][1],
            },
            "before_manifest_sha256": _canonical_sha(before),
            "after_manifest_sha256": _canonical_sha(after),
        }
    return b3, matrix, gates, comparisons, qualified_input_sha256


def write_certificate(path, **roots):
    path = pathlib.Path(path).absolute()
    b3, matrix, gates, comparisons, qualified_input_sha256 = \
        validate_inputs(**roots)
    certificate = {
        "schema": SCHEMA,
        "disposition": DISPOSITION,
        "qualified_input_sha256": qualified_input_sha256,
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
