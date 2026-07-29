#!/usr/bin/env python3
"""Official-side strict decoding and custody helpers for candidate matrix."""
from __future__ import annotations

import hashlib
import os
import pathlib
import re
import stat

import campaign_lifecycle as lifecycle


HERE = pathlib.Path(__file__).resolve().parent
DECLARATION_PATH = HERE / "candidate_matrix_contract.json"
DECLARATION_SHA256 = "522f54fac32568369863485c1f03714eb0d7d77e796c01d3c0a8e72707decf10"
HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")
FREEZE_FIELDS = {
    "schema", "campaign", "state", "artifact_contract", "foundation",
    "fixtures", "artifacts", "candidate", "configuration",
    "authorization", "seed", "cells",
    "luna_stage", "evidence_profiles", "result_composition", "attempt_policy",
    "acceptance_rule", "invalid_error_rule", "stop_conditions",
    "independent_rederiver",
}
FIXTURE_ORDER = (
    "B0", "B1", "B2", "E1", "E2a", "E2b", "E3", "E4",
    "E5", "E6", "E7", "E8", "E9", "E10",
)
PLAN = tuple(
    {"index": index, "config": "L", "fixture": fixture}
    for index, fixture in enumerate(FIXTURE_ORDER)
)
OFFICIAL_CELL_FIELDS = {
    "index", "config", "fixture", "product_status", "host_status",
    "overall_status", "properties", "reason", "bundle_manifest_sha256",
    "raw_stdout_sha256", "native_session_sha256",
    "official_overall_status", "independent_overall_status",
    "model_resolved", "official_verdict_sha256",
}
LUNA_IDENTITY_FIELDS = {
    "config", "host", "model_resolved_required", "host_attestation_id",
    "host_attestation_sha256",
}
INDEPENDENT_REDERIVATION_FIELDS = {
    "path", "sha256", "schema", "contract_id", "implementation_sha256",
}
FINAL_CLAIM_FIELDS = {
    "final_28_of_28", "cross_model_qualified", "release_authorized",
    "tag_authorized", "publication_authorized",
}


def decode_json_bytes(data, owner, *, require_object=False):
    return lifecycle.decode_strict_json_bytes(
        data, owner, require_object=require_object)


def _reparse_point(path_stat):
    return bool(getattr(path_stat, "st_file_attributes", 0) &
                getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400))


def read_custodied_bytes(path, owner, *, root=None):
    """Read one retained regular file only through its unique lexical path."""
    return lifecycle.read_custodied_bytes(path, owner, root=root)


def read_custodied_directory_manifest(path, owner, *, root=None):
    return lifecycle.read_custodied_directory_manifest(
        path, owner, root=root)


def load_json_file(path, owner, *, require_object=True, root=None):
    return decode_json_bytes(read_custodied_bytes(path, owner, root=root), owner,
                             require_object=require_object)


def _exact(value, fields, owner):
    if type(value) is not dict:
        raise ValueError(f"{owner} must be an object")
    if set(value) != set(fields):
        missing = sorted(set(fields) - set(value))
        extra = sorted(set(value) - set(fields))
        raise ValueError(f"{owner} key set invalid; missing={missing}; extra={extra}")
    return value


def _string(value, owner, *, nonempty=True):
    if type(value) is not str or (nonempty and not value):
        raise ValueError(f"{owner} must be a non-empty string")


def _digest(value, owner):
    if type(value) is not str or not HEX64.fullmatch(value):
        raise ValueError(f"{owner} must be a lowercase SHA-256")


def _git_id(value, owner):
    if type(value) is not str or not HEX40.fullmatch(value):
        raise ValueError(f"{owner} must be a lowercase full Git object id")


def safe_relative_path(value, owner="artifact"):
    _string(value, owner)
    if ("\\" in value or "\x00" in value or value.startswith("/") or
            re.match(r"^[A-Za-z]:", value)):
        raise ValueError(f"{owner} path invalid")
    parts = value.split("/")
    if any(part in ("", ".", "..") for part in parts):
        raise ValueError(f"{owner} path invalid")
    return value


def resolve_contained(root, relative, *, require_exists=True):
    root = pathlib.Path(root).resolve(strict=True)
    safe_relative_path(relative)
    lexical = root.joinpath(*relative.split("/"))
    try:
        resolved = lexical.resolve(strict=require_exists)
    except OSError as exc:
        raise ValueError("artifact path cannot be resolved") from exc
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise ValueError("artifact path escapes owner root") from exc
    if require_exists:
        current = root
        for part in relative.split("/"):
            current = current / part
            if current.is_symlink() or _reparse_point(os.lstat(current)):
                raise ValueError("artifact link alias forbidden")
        stat = resolved.stat()
        if stat.st_nlink != 1:
            raise ValueError("artifact hardlink alias forbidden")
    return resolved


def resolve_external_file(path, owner):
    _string(path, owner)
    lexical = pathlib.Path(path).absolute()
    try:
        resolved = lexical.resolve(strict=True)
        if resolved != lexical:
            raise ValueError(f"{owner} link or reparse alias forbidden")
        current = pathlib.Path(lexical.anchor)
        for part in lexical.parts[1:]:
            current = current / part
            path_stat = os.lstat(current)
            if stat.S_ISLNK(path_stat.st_mode) or _reparse_point(path_stat):
                raise ValueError(f"{owner} link or reparse alias forbidden")
        with open(lexical, "rb") as stream:
            opened = os.fstat(stream.fileno())
            if not stat.S_ISREG(opened.st_mode) or opened.st_nlink != 1:
                raise ValueError(f"{owner} link or non-file identity forbidden")
    except OSError as exc:
        raise ValueError(f"{owner} cannot be resolved") from exc
    return resolved


def canonical_json_bytes(value):
    return lifecycle.canonical_json_bytes(value)


def exact_json_equal(left, right):
    return lifecycle._exact_json_equal(left, right)


_exact_json_equal = exact_json_equal


def write_new_json(path, value):
    return lifecycle.write_new_json(path, value)


def _declaration():
    return load_json_file(DECLARATION_PATH, "candidate matrix artifact contract")


def contract_sha256():
    observed = hashlib.sha256(read_custodied_bytes(
        DECLARATION_PATH, "candidate matrix artifact contract")).hexdigest()
    if observed != DECLARATION_SHA256:
        raise ValueError("candidate matrix artifact contract semantic identity drift")
    return observed


def validate_declaration(value):
    value = _exact(value, {"schema", "contract_id", "campaign", "encoding",
                           "execution", "artifacts", "lifecycle_schemas"},
                   "artifact contract")
    if (value["schema"] !=
            "implementaudit-candidate-matrix-artifact-contract-v1" or
            value["contract_id"] !=
            "implementaudit-candidate-matrix-artifact-contract-v1" or
            value["campaign"] != "candidate-matrix-sol-luna-r1"):
        raise ValueError("artifact contract schema invalid")
    encoding = _exact(value["encoding"], {"charset", "duplicate_keys",
                      "non_finite_numbers", "object_keys", "scalar_types",
                      "paths", "writes"}, "artifact contract encoding")
    if not exact_json_equal(encoding, {
            "charset": "UTF-8", "duplicate_keys": "REJECT_RECURSIVELY",
            "non_finite_numbers": "REJECT", "object_keys": "EXACT",
            "scalar_types": "EXACT_NO_COERCION",
            "paths": "CANONICAL_ROLE_CONTAINED_NO_LINK_ALIAS",
            "writes": "CREATE_ONCE"}):
        raise ValueError("artifact contract encoding drift")
    execution = _exact(value["execution"], {
        "configuration", "fixture_order", "mission_count", "silent_retry",
        "preserve_every_attempt", "success_disposition",
        "luna_stage_accepted", "final_acceptance",
    }, "artifact contract execution")
    if not exact_json_equal(execution, {
            "configuration": "L", "fixture_order": list(FIXTURE_ORDER),
            "mission_count": 14, "silent_retry": "FORBIDDEN",
            "preserve_every_attempt": True,
            "success_disposition": "INCOMPLETE_PENDING_OPUS",
            "luna_stage_accepted": True, "final_acceptance": False}):
        raise ValueError("artifact contract execution drift")
    artifacts = value["artifacts"]
    if type(artifacts) is not dict or not artifacts:
        raise ValueError("artifact contract artifacts invalid")
    fields = {"producer", "readers", "role", "format", "schema", "create_once"}
    for name, row in artifacts.items():
        safe_relative_path(name, "artifact name")
        row = _exact(row, fields, f"artifact {name}")
        _string(row["producer"], f"artifact {name} producer")
        if (type(row["readers"]) is not list or not row["readers"] or
                any(type(item) is not str or not item for item in row["readers"])):
            raise ValueError(f"artifact {name} readers invalid")
        if row["format"] not in ("JSON", "JSONL", "BYTES"):
            raise ValueError(f"artifact {name} format invalid")
        if type(row["create_once"]) is not bool or not row["create_once"]:
            raise ValueError(f"artifact {name} create-once policy invalid")
    if not exact_json_equal(value, _declaration()):
        raise ValueError("artifact contract semantic declaration drift")
    return value


def validate_freeze_envelope(packet):
    packet = _exact(packet, FREEZE_FIELDS, "freeze packet")
    if (packet["schema"] !=
            "implementaudit-candidate-matrix-luna-freeze-v1" or
            packet["campaign"] != "candidate-matrix-sol-luna-r1" or
            packet["state"] != "FROZEN_BEFORE_FIRST_CELL"):
        raise ValueError("freeze packet schema invalid")
    contract = _exact(packet["artifact_contract"], {"schema", "path", "sha256"},
                      "artifact_contract")
    if (contract["schema"] !=
            "implementaudit-candidate-matrix-artifact-contract-v1"):
        raise ValueError("artifact contract schema invalid")
    if contract["path"] != "eval/candidate_matrix_contract.json":
        raise ValueError("artifact contract path invalid")
    _digest(contract["sha256"], "artifact contract sha256")
    if contract["sha256"] != contract_sha256():
        raise ValueError("artifact contract hash mismatch")
    for owner in ("foundation",):
        row = _exact(packet[owner], {"commit", "tree"}, owner)
        _git_id(row["commit"], f"{owner}.commit")
        _git_id(row["tree"], f"{owner}.tree")
    fixtures = packet["fixtures"]
    if type(fixtures) is not list or len(fixtures) != len(FIXTURE_ORDER):
        raise ValueError("fixtures inventory invalid")
    for index, (fixture, expected_id) in enumerate(
            zip(fixtures, FIXTURE_ORDER)):
        fixture = _exact(
            fixture, {"id", "path", "sha256", "complete_manifest_sha256"},
            f"fixture {index}")
        if (fixture["id"] != expected_id or
                fixture["path"] !=
                f"eval/fixtures/{expected_id}/fixture.json"):
            raise ValueError("fixture identity or order invalid")
        _digest(fixture["sha256"], f"fixture {index} sha256")
        _digest(
            fixture["complete_manifest_sha256"],
            f"fixture {index} complete_manifest_sha256")
    if len({fixture["path"] for fixture in fixtures}) != len(fixtures):
        raise ValueError("fixture path aliases forbidden")
    artifacts = packet["artifacts"]
    if type(artifacts) is not dict or set(artifacts) != {"scorer", "evaluator", "bundle", "runner"}:
        raise ValueError("artifacts key set invalid")
    for name, row in artifacts.items():
        row = _exact(row, {"path", "sha256"}, f"artifact {name}")
        safe_relative_path(row["path"], f"artifact {name}")
        _digest(row["sha256"], f"artifact {name} sha256")
    if len({row["path"] for row in artifacts.values()}) != len(artifacts):
        raise ValueError("artifact role paths must be distinct")
    candidate = _exact(
        packet["candidate"],
        {"commit", "tree", "skill_tree", "payload_sha256"}, "candidate")
    for key in ("commit", "tree", "skill_tree"):
        _git_id(candidate[key], f"candidate.{key}")
    _digest(candidate["payload_sha256"], "candidate.payload_sha256")
    config_fields = {"id", "host", "model_requested", "model_resolved_required",
                     "reasoning_effort", "auth_mode", "executable",
                     "host_attestation"}
    configuration = _exact(
        packet["configuration"], config_fields, "configuration")
    if configuration["id"] != "L":
        raise ValueError("configuration id invalid")
    if (configuration["host"] != "WSL Ubuntu Codex CLI" or
            configuration["model_requested"] != "gpt-5.6-luna" or
            configuration["model_resolved_required"] != "gpt-5.6-luna" or
            configuration["reasoning_effort"] != "max" or
            configuration["auth_mode"] != "chatgpt-subscription"):
        raise ValueError("configuration identity/auth boundary drift")
    executable = _exact(
        configuration["executable"], {"path", "version", "sha256"},
        "configuration executable")
    for key in ("path", "version"):
        _string(executable[key], f"configuration executable {key}")
    _digest(executable["sha256"], "configuration executable sha256")
    host_attestation = _exact(
        configuration["host_attestation"], {"id", "sha256"},
        "configuration host attestation")
    _string(host_attestation["id"], "configuration host attestation id")
    _digest(
        host_attestation["sha256"], "configuration host attestation sha256")
    authorization = _exact(packet["authorization"], {"acknowledgement_path",
                           "acknowledgement_sha256", "metered_api_spend"}, "authorization")
    _string(authorization["acknowledgement_path"], "authorization acknowledgement_path")
    _digest(authorization["acknowledgement_sha256"], "authorization acknowledgement_sha256")
    if authorization["metered_api_spend"] != "FORBIDDEN":
        raise ValueError("authorization metered_api_spend invalid")
    if type(packet["seed"]) is not int or packet["seed"] != 20260718:
        raise ValueError("seed invalid")
    cells = packet["cells"]
    if type(cells) is not list or len(cells) != len(PLAN):
        raise ValueError("cell plan invalid")
    for index, (cell, expected) in enumerate(zip(cells, PLAN)):
        validate_mission(cell)
        if not exact_json_equal(cell, expected):
            raise ValueError("cell identity or order invalid")
    stage = _exact(packet["luna_stage"], {
        "schema", "name", "cell_count", "terminal_name",
        "official_result_name", "independent_result_name",
        "success_disposition"}, "luna_stage")
    if not exact_json_equal(stage, {
            "schema": "implementaudit-candidate-matrix-luna-stage-v1",
            "name": "LUNA", "cell_count": 14,
            "terminal_name": "luna-stage-terminal.json",
            "official_result_name": "candidate-matrix-luna-result.json",
            "independent_result_name":
                "candidate-matrix-luna-independent-rederivation.json",
            "success_disposition": "INCOMPLETE_PENDING_OPUS"}):
        raise ValueError("luna_stage boundary drift")
    _exact(packet["evidence_profiles"], {
        "formal_host_read", "raw_stdout", "native_session", "pre_spawn",
        "post_cell_manifest"}, "evidence_profiles")
    _exact(packet["result_composition"], {
        "product_property_states", "host_states", "overall_states",
        "luna_stage_dispositions"}, "result_composition")
    _exact(packet["attempt_policy"], {
        "silent_retry", "preserve_every_attempt", "maximum_attempts"},
        "attempt_policy")
    rederiver = _exact(packet["independent_rederiver"], {
        "contract_id", "implementation_identity", "must_not_import", "input",
        "output"}, "independent_rederiver")
    _exact(rederiver["implementation_identity"], {"path", "sha256"},
           "independent_rederiver.implementation_identity")
    if (rederiver["contract_id"] !=
            "implementaudit-candidate-matrix-luna-rederiver-v1" or
            rederiver["implementation_identity"]["path"] !=
            "eval/candidate_matrix_rederive.py" or
            rederiver["input"] != "retained raw evidence only" or
            rederiver["output"] != "independent Luna matrix result" or
            type(rederiver["must_not_import"]) is not list or
            not rederiver["must_not_import"]):
        raise ValueError("independent rederiver boundary drift")
    _digest(
        rederiver["implementation_identity"]["sha256"],
        "independent rederiver implementation sha256")
    return packet


def validate_artifact(name, value):
    declaration = _declaration()
    fields = declaration["lifecycle_schemas"].get(name)
    if fields is None:
        raise ValueError(f"unknown lifecycle schema: {name}")
    value = _exact(value, fields, name)
    schema = value.get("schema")
    expected = {
        "campaign_manifest":
            "implementaudit-candidate-matrix-luna-campaign-custody-v1",
        "attempt_status":
            "implementaudit-candidate-matrix-luna-attempt-status-v1",
        "attempt_terminal":
            "implementaudit-candidate-matrix-luna-attempt-terminal-v1",
        "official_luna_result":
            "implementaudit-candidate-matrix-luna-result-v1",
    }[name]
    if schema != expected:
        raise ValueError(f"{name} schema invalid")
    if name in ("campaign_manifest", "attempt_status", "official_luna_result"):
        if value["campaign"] != "candidate-matrix-sol-luna-r1":
            raise ValueError(f"{name} campaign invalid")
        for key in ("freeze_sha256", "contract_sha256"):
            _digest(value[key], f"{name}.{key}")
    if name == "campaign_manifest":
        if value["execution_stage"] != "LUNA":
            raise ValueError("campaign manifest execution stage invalid")
    if name == "attempt_status":
        validate_mission(value["mission"])
        if value["state"] != "PREPARED_BEFORE_HOST_SPAWN":
            raise ValueError("attempt status state invalid")
        if value["execution_mode"] not in ("production", "test"):
            raise ValueError("attempt status execution mode invalid")
        binding = _exact(value["host_attestation_binding"],
                         {"path", "sha256", "config", "host",
                          "model_resolved_required"},
                         "attempt status host attestation binding")
        if binding["path"] != "host-attestation.json":
            raise ValueError("attempt status host attestation path invalid")
        _digest(binding["sha256"], "attempt status host attestation sha256")
        if binding["config"] != "L":
            raise ValueError("attempt status host attestation config invalid")
        _string(binding["host"], "attempt status host attestation host")
        _string(binding["model_resolved_required"],
                "attempt status host attestation model")
    if name == "attempt_terminal":
        if (type(value["mission_index"]) is not int or
                not 0 <= value["mission_index"] < 14):
            raise ValueError("attempt terminal mission index invalid")
        if value["overall_status"] not in ("PASS", "FAIL", "INVALID", "ERROR"):
            raise ValueError("attempt terminal overall status invalid")
        if value["official_overall_status"] is not None and value["official_overall_status"] not in ("PASS", "FAIL", "INVALID", "ERROR"):
            raise ValueError("attempt terminal official status invalid")
        if value["official_verdict_sha256"] is not None:
            _digest(value["official_verdict_sha256"], "attempt terminal verdict sha256")
        seal = value["completed_attempt_seal"]
        if value["overall_status"] in ("PASS", "FAIL"):
            seal = _exact(
                seal, {
                    "schema", "campaign", "freeze_sha256", "contract_sha256",
                    "mission", "execution_mode", "overall_status",
                    "resolved_model", "host_run_root",
                    "official_overall_status", "official_verdict_sha256",
                    "stop_reason", "error_type", "completed_at",
                    "attempt_name", "attempt_status_sha256",
                    "host_attestation_sha256",
                    "host_custody_manifest_sha256",
                }, "completed attempt seal")
            if seal["schema"] != \
                    "implementaudit-candidate-matrix-completed-attempt-seal-v1":
                raise ValueError("completed attempt seal schema invalid")
            validate_mission(seal["mission"])
            for key in (
                    "freeze_sha256", "contract_sha256",
                    "official_verdict_sha256", "attempt_status_sha256",
                    "host_attestation_sha256",
                    "host_custody_manifest_sha256"):
                _digest(seal[key], f"completed attempt seal {key}")
            for key in (
                    "campaign", "execution_mode", "overall_status",
                    "resolved_model", "host_run_root", "official_overall_status",
                    "completed_at", "attempt_name"):
                _string(seal[key], f"completed attempt seal {key}")
            if (seal["campaign"] != value["campaign"] or
                    seal["mission"]["index"] != value["mission_index"] or
                    seal["execution_mode"] != value["execution_mode"] or
                    seal["overall_status"] != value["overall_status"] or
                    seal["resolved_model"] != value["resolved_model"] or
                    seal["host_run_root"] != value["host_run_root"] or
                    seal["official_overall_status"] !=
                    value["official_overall_status"] or
                    seal["official_verdict_sha256"] !=
                    value["official_verdict_sha256"] or
                    not exact_json_equal(
                        seal["stop_reason"], value["stop_reason"]) or
                    not exact_json_equal(
                        seal["error_type"], value["error_type"]) or
                    seal["completed_at"] != value["completed_at"]):
                raise ValueError("completed attempt seal terminal identity drift")
        elif seal is not None:
            raise ValueError(
                "non-scored attempt terminal cannot claim a completion seal")
    if name == "official_luna_result":
        if (value["disposition"] != "INCOMPLETE_PENDING_OPUS" or
                value["luna_stage_accepted"] is not True or
                value["accepted"] is not False or
                type(value["cell_count"]) is not int or
                value["cell_count"] != 14 or
                type(value["cells"]) is not list or
                len(value["cells"]) != 14 or
                type(value["luna_identity"]) is not dict or
                type(value["independent_rederivation"]) is not dict or
                type(value["claims"]) is not dict):
            raise ValueError("official Luna result boundary invalid")
        if value["campaign"] != "candidate-matrix-sol-luna-r1":
            raise ValueError("official Luna result campaign invalid")
        for index, (cell, expected) in enumerate(
                zip(value["cells"], PLAN)):
            cell = _exact(
                cell, OFFICIAL_CELL_FIELDS,
                f"official Luna result cell {index}")
            if (type(cell["index"]) is not int or
                    cell["index"] != index):
                raise ValueError(
                    f"official Luna result cell {index} index invalid")
            if (cell["config"] != expected["config"] or
                    cell["fixture"] != expected["fixture"]):
                raise ValueError(
                    f"official Luna result cell {index} identity invalid")
            for key in ("overall_status", "official_overall_status",
                        "independent_overall_status"):
                if cell[key] != "PASS":
                    raise ValueError(
                        f"official Luna result cell {index} {key} invalid")
            for key in ("product_status", "host_status"):
                if cell[key] != "PASS":
                    raise ValueError(
                        f"official Luna result cell {index} {key} invalid")
            properties = cell["properties"]
            if type(properties) is not dict or not properties:
                raise ValueError(
                    f"official Luna result cell {index} properties invalid")
            for property_name, property_row in properties.items():
                _string(
                    property_name,
                    f"official Luna result cell {index} property name")
                property_row = _exact(
                    property_row, {"state", "pass"},
                    f"official Luna result cell {index} property")
                if not (
                        (property_row["state"] == "PASS" and
                         property_row["pass"] is True) or
                        (property_row["state"] == "FAIL" and
                         property_row["pass"] is False) or
                        (property_row["state"] == "INCOMPLETE" and
                         property_row["pass"] is None)):
                    raise ValueError(
                        f"official Luna result cell {index} property invalid")
            if cell["reason"] is not None:
                raise ValueError(
                    f"official Luna result cell {index} reason invalid")
            for key in ("bundle_manifest_sha256", "raw_stdout_sha256",
                        "native_session_sha256"):
                _digest(
                    cell[key],
                    f"official Luna result cell {index} {key}")
            _string(
                cell["model_resolved"],
                f"official Luna result cell {index} model")
            _digest(
                cell["official_verdict_sha256"],
                f"official Luna result cell {index} verdict sha256")
        identity = _exact(
            value["luna_identity"], LUNA_IDENTITY_FIELDS,
            "official Luna result Luna identity")
        if identity["config"] != "L":
            raise ValueError("official Luna result Luna identity config invalid")
        for key in ("host", "model_resolved_required",
                    "host_attestation_id"):
            _string(identity[key],
                    f"official Luna result Luna identity {key}")
        _digest(
            identity["host_attestation_sha256"],
            "official Luna result Luna identity attestation sha256")
        independent = _exact(
            value["independent_rederivation"],
            INDEPENDENT_REDERIVATION_FIELDS,
            "official Luna result independent rederivation")
        if (independent["path"] !=
                "candidate-matrix-luna-independent-rederivation.json"):
            raise ValueError(
                "official Luna result independent rederivation path invalid")
        _digest(
            independent["sha256"],
            "official Luna result independent rederivation sha256")
        if (independent["schema"] !=
                "implementaudit-candidate-matrix-luna-independent-rederivation-v1"):
            raise ValueError(
                "official Luna result independent rederivation schema invalid")
        if (independent["contract_id"] !=
                "implementaudit-candidate-matrix-luna-rederiver-v1"):
            raise ValueError(
                "official Luna result independent rederivation contract invalid")
        _digest(
            independent["implementation_sha256"],
            "official Luna result independent implementation sha256")
        claims = _exact(
            value["claims"], FINAL_CLAIM_FIELDS,
            "official Luna result claims")
        for key, claim in claims.items():
            if claim is not False:
                raise ValueError(
                    f"official Luna result claim {key} must be false")
    else:
        _string(value["created_at"] if name != "attempt_terminal" else value["completed_at"],
                f"{name} timestamp")
    return value


def validate_host_attestation(value):
    value = _exact(value, {"id", "shell_dialect", "executables"},
                   "host attestation")
    _string(value["id"], "host attestation id")
    if value["shell_dialect"] not in ("posix", "powershell", "cmd"):
        raise ValueError("host attestation shell dialect invalid")
    executables = value["executables"]
    if (type(executables) is not dict or not executables or
            any(type(name) is not str or not name or
                type(identity) is not str or not identity
                for name, identity in executables.items())):
        raise ValueError("host attestation executable identities invalid")
    return value


def validate_mission(mission):
    mission = _exact(mission, {"index", "config", "fixture"}, "mission")
    if type(mission["index"]) is not int or not 0 <= mission["index"] < 14:
        raise ValueError("mission index invalid")
    if (mission["config"] != "L" or
            type(mission["fixture"]) is not str or
            mission["fixture"] not in FIXTURE_ORDER or
            mission["fixture"] != FIXTURE_ORDER[mission["index"]]):
        raise ValueError("mission enum invalid")
    return mission


def next_mission(plan, completed):
    if not exact_json_equal(completed, plan[:len(completed)]):
        raise ValueError("campaign attempt order invalid")
    return None if len(completed) == len(plan) else plan[len(completed)]


def campaign_complete(plan, completed):
    return (exact_json_equal(completed, plan) and
            {m["config"] for m in completed} == {"L"})


validate_declaration(_declaration())
contract_sha256()
