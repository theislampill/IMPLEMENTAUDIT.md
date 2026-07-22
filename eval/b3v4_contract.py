#!/usr/bin/env python3
"""Official-side strict decoding and custody helpers for B3-v4."""
from __future__ import annotations

import hashlib
import os
import pathlib
import re
import stat

import campaign_lifecycle as lifecycle


HERE = pathlib.Path(__file__).resolve().parent
DECLARATION_PATH = HERE / "b3v4_contract.json"
DECLARATION_SHA256 = "4909f2e3b5ec9ba2188594f8e9669b8ea717ed1ecacff2dfa927395689b68495"
HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")
FREEZE_FIELDS = {
    "schema", "campaign", "state", "artifact_contract", "foundation",
    "fixture", "artifacts", "candidate", "control", "configurations",
    "authorization", "seed", "repetitions_per_configuration_and_arm",
    "missions", "evidence_profiles", "result_composition", "attempt_policy",
    "acceptance_rule", "invalid_error_rule", "stop_conditions",
    "independent_rederiver",
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


def write_new_json(path, value):
    return lifecycle.write_new_json(path, value)


def _declaration():
    return load_json_file(DECLARATION_PATH, "B3-v4 artifact contract")


def contract_sha256():
    observed = hashlib.sha256(read_custodied_bytes(
        DECLARATION_PATH, "B3-v4 artifact contract")).hexdigest()
    if observed != DECLARATION_SHA256:
        raise ValueError("B3-v4 artifact contract semantic identity drift")
    return observed


def validate_declaration(value):
    value = _exact(value, {"schema", "contract_id", "encoding", "execution",
                           "artifacts", "lifecycle_schemas"},
                   "artifact contract")
    if value["schema"] != "implementaudit-b3v4-artifact-contract-v1":
        raise ValueError("artifact contract schema invalid")
    encoding = _exact(value["encoding"], {"charset", "duplicate_keys",
                      "non_finite_numbers", "object_keys", "scalar_types",
                      "paths", "writes"}, "artifact contract encoding")
    if encoding != {
            "charset": "UTF-8", "duplicate_keys": "REJECT_RECURSIVELY",
            "non_finite_numbers": "REJECT", "object_keys": "EXACT",
            "scalar_types": "EXACT_NO_COERCION",
            "paths": "CANONICAL_ROLE_CONTAINED_NO_LINK_ALIAS",
            "writes": "CREATE_ONCE"}:
        raise ValueError("artifact contract encoding drift")
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
    if value != _declaration():
        raise ValueError("artifact contract semantic declaration drift")
    return value


def validate_freeze_envelope(packet):
    packet = _exact(packet, FREEZE_FIELDS, "freeze packet")
    if packet["schema"] != "implementaudit-b3v4-campaign-freeze-v1":
        raise ValueError("freeze packet schema invalid")
    contract = _exact(packet["artifact_contract"], {"schema", "path", "sha256"},
                      "artifact_contract")
    if contract["schema"] != "implementaudit-b3v4-artifact-contract-v1":
        raise ValueError("artifact contract schema invalid")
    if contract["path"] != "eval/b3v4_contract.json":
        raise ValueError("artifact contract path invalid")
    _digest(contract["sha256"], "artifact contract sha256")
    if contract["sha256"] != contract_sha256():
        raise ValueError("artifact contract hash mismatch")
    for owner in ("foundation",):
        row = _exact(packet[owner], {"commit", "tree"}, owner)
        _git_id(row["commit"], f"{owner}.commit")
        _git_id(row["tree"], f"{owner}.tree")
    fixture = _exact(packet["fixture"], {"id", "fixture_sha256",
                     "complete_manifest_sha256"}, "fixture")
    if fixture["id"] != "B3-v3":
        raise ValueError("fixture id invalid")
    _digest(fixture["fixture_sha256"], "fixture.fixture_sha256")
    _digest(fixture["complete_manifest_sha256"], "fixture.complete_manifest_sha256")
    artifacts = packet["artifacts"]
    if type(artifacts) is not dict or set(artifacts) != {"scorer", "evaluator", "bundle", "runner"}:
        raise ValueError("artifacts key set invalid")
    for name, row in artifacts.items():
        row = _exact(row, {"path", "sha256"}, f"artifact {name}")
        safe_relative_path(row["path"], f"artifact {name}")
        _digest(row["sha256"], f"artifact {name} sha256")
    if len({row["path"] for row in artifacts.values()}) != len(artifacts):
        raise ValueError("artifact role paths must be distinct")
    for owner in ("candidate", "control"):
        row = _exact(packet[owner], {"commit", "tree", "skill_tree", "payload_sha256"}, owner)
        for key in ("commit", "tree", "skill_tree"):
            _git_id(row[key], f"{owner}.{key}")
        _digest(row["payload_sha256"], f"{owner}.payload_sha256")
    if packet["candidate"] == packet["control"]:
        raise ValueError("candidate and control identities must be distinct")
    configurations = packet["configurations"]
    if type(configurations) is not dict or set(configurations) != {"L", "O"}:
        raise ValueError("configurations key set invalid")
    expected_hosts = {"L": "WSL Ubuntu Codex CLI", "O": "Windows Claude CLI"}
    config_fields = {"host", "model_requested", "model_resolved_required",
                     "reasoning_effort", "auth_mode", "executable",
                     "host_attestation"}
    for name, row in configurations.items():
        row = _exact(row, config_fields, f"configuration {name}")
        if row["host"] != expected_hosts[name]:
            raise ValueError(f"configuration {name} host invalid")
        executable = _exact(row["executable"], {"path", "version", "sha256"},
                            f"configuration {name} executable")
        for key in ("path", "version"):
            _string(executable[key], f"configuration {name} executable {key}")
        _digest(executable["sha256"], f"configuration {name} executable sha256")
        host_attestation = _exact(
            row["host_attestation"], {"id", "sha256"},
            f"configuration {name} host attestation")
        _string(host_attestation["id"],
                f"configuration {name} host attestation id")
        _digest(host_attestation["sha256"],
                f"configuration {name} host attestation sha256")
    authorization = _exact(packet["authorization"], {"acknowledgement_path",
                           "acknowledgement_sha256", "metered_api_spend"}, "authorization")
    _string(authorization["acknowledgement_path"], "authorization acknowledgement_path")
    _digest(authorization["acknowledgement_sha256"], "authorization acknowledgement_sha256")
    if authorization["metered_api_spend"] != "FORBIDDEN":
        raise ValueError("authorization metered_api_spend invalid")
    if type(packet["seed"]) is not int or packet["seed"] != 20260718:
        raise ValueError("seed invalid")
    if (type(packet["repetitions_per_configuration_and_arm"]) is not int or
            packet["repetitions_per_configuration_and_arm"] != 3):
        raise ValueError("repetition count invalid")
    missions = packet["missions"]
    if type(missions) is not list or len(missions) != 12:
        raise ValueError("mission plan invalid")
    for index, mission in enumerate(missions):
        mission = _exact(mission, {"index", "config", "arm", "rep"}, f"mission {index}")
        if type(mission["index"]) is not int or mission["index"] != index:
            raise ValueError("mission order index invalid")
        if mission["config"] not in ("L", "O") or mission["arm"] not in ("candidate", "control"):
            raise ValueError("mission enum invalid")
        if type(mission["rep"]) is not int or mission["rep"] not in (1, 2, 3):
            raise ValueError("mission rep invalid")
    _exact(packet["evidence_profiles"], {
        "formal_host_read", "raw_stdout", "native_session", "pre_spawn",
        "post_mission_manifest"}, "evidence_profiles")
    _exact(packet["result_composition"], {
        "product_property_states", "host_states", "overall_states"},
        "result_composition")
    _exact(packet["attempt_policy"], {
        "silent_retry", "preserve_every_attempt"}, "attempt_policy")
    rederiver = _exact(packet["independent_rederiver"], {
        "contract_id", "implementation_identity", "must_not_import", "input",
        "output"}, "independent_rederiver")
    _exact(rederiver["implementation_identity"], {"path", "sha256"},
           "independent_rederiver.implementation_identity")
    return packet


def validate_artifact(name, value):
    declaration = _declaration()
    fields = declaration["lifecycle_schemas"].get(name)
    if fields is None:
        raise ValueError(f"unknown lifecycle schema: {name}")
    value = _exact(value, fields, name)
    schema = value.get("schema")
    expected = {
        "campaign_manifest": "implementaudit-b3v4-campaign-custody-v1",
        "attempt_status": "implementaudit-b3v4-attempt-status-v1",
        "attempt_terminal": "implementaudit-b3v4-attempt-terminal-v1",
    }[name]
    if schema != expected:
        raise ValueError(f"{name} schema invalid")
    if name in ("campaign_manifest", "attempt_status"):
        for key in ("freeze_sha256", "contract_sha256"):
            _digest(value[key], f"{name}.{key}")
    if name == "campaign_manifest":
        if value["execution_stage"] != "LUNA_THEN_OPUS_UNCHANGED_PACKET":
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
        if binding["config"] not in ("L", "O"):
            raise ValueError("attempt status host attestation config invalid")
        _string(binding["host"], "attempt status host attestation host")
        _string(binding["model_resolved_required"],
                "attempt status host attestation model")
    if name == "attempt_terminal":
        if type(value["mission_index"]) is not int or not 0 <= value["mission_index"] < 12:
            raise ValueError("attempt terminal mission index invalid")
        if value["overall_status"] not in ("PASS", "FAIL", "INVALID", "ERROR"):
            raise ValueError("attempt terminal overall status invalid")
        if value["official_overall_status"] is not None and value["official_overall_status"] not in ("PASS", "FAIL", "INVALID", "ERROR"):
            raise ValueError("attempt terminal official status invalid")
        if value["official_verdict_sha256"] is not None:
            _digest(value["official_verdict_sha256"], "attempt terminal verdict sha256")
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
    mission = _exact(mission, {"index", "config", "arm", "rep"}, "mission")
    if type(mission["index"]) is not int or not 0 <= mission["index"] < 12:
        raise ValueError("mission index invalid")
    if mission["config"] not in ("L", "O") or mission["arm"] not in ("candidate", "control"):
        raise ValueError("mission enum invalid")
    if type(mission["rep"]) is not int or mission["rep"] not in (1, 2, 3):
        raise ValueError("mission rep invalid")
    return mission


def next_mission(plan, completed):
    if completed != plan[:len(completed)]:
        raise ValueError("campaign attempt order invalid")
    return None if len(completed) == len(plan) else plan[len(completed)]


def campaign_complete(plan, completed):
    return completed == plan and {m["config"] for m in completed} == {"L", "O"}


validate_declaration(_declaration())
contract_sha256()
