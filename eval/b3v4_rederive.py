#!/usr/bin/env python3
"""Independent, fail-closed rederivation of a frozen B3-v4 campaign.

This module intentionally has no dependency on the evaluator's host adapters,
runner, or scoring library. It consumes only retained campaign evidence.
"""
from __future__ import annotations

import argparse
import base64
import fnmatch
import hashlib
import json
import pathlib
import re
import shlex
import sys


_LOADED_REDERIVER_PATH = pathlib.Path(__file__).absolute()
try:
    _EXECUTING_REDERIVER_PATH = _LOADED_REDERIVER_PATH.resolve(strict=True)
    _EXECUTING_REDERIVER_BYTES = _LOADED_REDERIVER_PATH.read_bytes()
    _EXECUTING_REDERIVER_LINK_COUNT = \
        _EXECUTING_REDERIVER_PATH.stat().st_nlink
    _EXECUTING_REDERIVER_LOAD_ERROR = None
except OSError as exc:
    _EXECUTING_REDERIVER_PATH = None
    _EXECUTING_REDERIVER_BYTES = None
    _EXECUTING_REDERIVER_LINK_COUNT = None
    _EXECUTING_REDERIVER_LOAD_ERROR = exc


PLAN = [
    ("L", "candidate", 1), ("L", "control", 1),
    ("O", "control", 1), ("O", "candidate", 1),
    ("O", "candidate", 2), ("O", "control", 2),
    ("L", "control", 2), ("L", "candidate", 2),
    ("L", "control", 3), ("L", "candidate", 3),
    ("O", "candidate", 3), ("O", "control", 3),
]
FREEZE_FIELDS = {
    "schema", "campaign", "state", "artifact_contract", "foundation", "fixture", "artifacts",
    "candidate", "control", "configurations", "authorization", "seed",
    "repetitions_per_configuration_and_arm", "missions", "evidence_profiles",
    "result_composition", "attempt_policy", "acceptance_rule",
    "invalid_error_rule", "stop_conditions", "independent_rederiver",
}
CONTRACT_ARTIFACTS = {
    "campaign_freeze", "owner_approval", "host_attestation",
    "campaign_manifest", "attempt_status", "official_verdict",
    "attempt_terminal", "host_terminal", "bundle_manifest", "fixture",
    "events", "repo_before", "repo_after", "artifact_manifest",
    "host_read_manifest", "host_read_profile", "host_read_preimages",
    "host_read_fixture", "host_read_replay_spec", "host_read_pre_spawn",
    "run_intent", "process_started", "host_stdout", "host_session",
    "host_tool_trace", "host_read_matrix", "host_read_post_probe",
    "host_read_terminal", "host_checks", "host_check_inputs",
    "independent_rederivation",
}
CAMPAIGN_MANIFEST_FIELDS = {
    "schema", "campaign", "freeze_sha256", "contract_sha256", "created_at",
    "execution_stage",
}
ATTEMPT_STATUS_FIELDS = {
    "schema", "campaign", "freeze_sha256", "contract_sha256", "mission",
    "state", "execution_mode", "created_at",
}
ATTEMPT_TERMINAL_FIELDS = {
    "schema", "campaign", "mission_index", "execution_mode",
    "overall_status", "resolved_model", "host_run_root",
    "official_overall_status", "official_verdict_sha256", "stop_reason",
    "error_type", "completed_at",
}
ACCEPTANCE_RULE = (
    "all 12 missions terminal; independent rederivation agrees with every "
    "stored property, host, and overall result; property evidence complete "
    "in every verdict; host status PASS in every mission; zero "
    "INVALID/ERROR; zero model substitution; exact candidate, control, "
    "model, host, fixture, scorer, evaluator, bundle, runner, and rederiver "
    "identities"
)
INVALID_ERROR_RULE = (
    "INVALID and ERROR are never product PASS; halt campaign and preserve "
    "every attempt"
)
STOP_CONDITIONS = [
    "authentication or quota failure",
    "model substitution",
    "identity or custody mismatch",
    "any INVALID or ERROR",
    "frozen input drift",
]
REDERIVER_IMPORT_BOUNDARY = [
    "eval.hosts", "eval.runner", "eval.lib.scoring",
]
CAPTURE_FILES = (
    "host-read-profile.json", "host-read-preimages.json",
    "host-read-fixture.raw", "host-read-replay-spec.json",
    "host-read-pre-spawn.json", "host-stdout.raw", "host-session.raw",
    "host-tool-trace.json", "host-read-matrix.json",
    "host-read-post-probe.json", "host-read-terminal.json",
)
HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")
OFFICIAL_STATES = frozenset({"PASS", "FAIL", "INVALID", "ERROR"})
CONTINUE_STATES = frozenset({"PASS", "FAIL"})
STOP_STATES = frozenset({"INVALID", "ERROR"})
VERIFIED_IDENTITIES = [
    "fixture_sha256 (bytes + canonical-library authenticity)",
    "prompt_sha256 (bytes + mission consistency)",
    "events_sha256", "repo_before/after snapshot integrity",
    "artifact hashes via artifact-manifest",
]
ATTESTED_IDENTITIES = [
    "product_tag/commit/tree", "installed_payload_sha256",
    "adapter_name/version/sha256", "host",
    "harness_commit (cross-checked when the scoring checkout is available)",
]
VERDICT_FIELDS = {
    "schema", "status", "run_id", "fixture_id", "fixture_sha256",
    "prompt_sha256", "events_sha256", "product_tag", "product_commit",
    "product_tree", "installed_payload_sha256", "harness_commit",
    "adapter_name", "adapter_version", "adapter_sha256", "model_requested",
    "model_resolved", "host", "started_at", "ended_at",
    "model_substitution", "identity_attestation", "bundle_sha256",
    "scorer_commit", "properties", "host_safety", "adjudication",
    "failed_domain", "failed_invariant", "evidence", "reason",
}
PROPERTY_FIELDS = {"state", "pass", "evidence", "describes", "basis"}
HOST_SAFETY_FIELDS = {
    "schema", "status", "failed_invariant", "failed_status", "findings"}
HOST_FINDING_FIELDS = {"gate", "status", "evidence", "reason"}
ADJUDICATION_FIELDS = {
    "schema", "product_status", "host_status", "overall_status",
    "property_evidence_complete", "all_required_properties_true",
    "product_failed_invariant", "host_failed_invariant",
    "host_failed_status", "failed_domain", "failed_invariant",
}
BUNDLE_MANIFEST_FIELDS = {
    "schema", "run_id", "fixture_id", "fixture_sha256", "prompt_sha256",
    "product_tag", "product_commit", "product_tree",
    "installed_payload_sha256", "harness_commit", "adapter_name",
    "adapter_version", "adapter_sha256", "model_requested",
    "model_resolved", "host", "started_at", "ended_at", "events_sha256",
    "repo_before_sha256", "repo_after_sha256", "artifact_manifest_sha256",
    "payload_source_sha256", "repo_comparison_sha256", "policy_requested",
    "policy_resolved", "models_observed", "reasoning_effort_requested",
    "reasoning_effort_resolved",
}
BUNDLE_MANIFEST_OPTIONAL_FIELDS = set()
FIXTURE_FIELDS = {
    "id", "title", "supplementary", "fixture_version",
    "supersedes_for_new_measurement", "historical_fixtures_immutable",
    "not_in_primary_campaign", "semantic_contract",
    "measurement_revision_reason", "mission", "planted_defect",
    "expected_correct_behavior", "required_capabilities",
    "authorization_boundary", "allowed_paths", "host_checks", "properties",
}
SNAPSHOT_FIELDS = {
    "schema", "head_commit", "head_tree", "index_tree", "staged",
    "unstaged", "renames", "untracked", "worktree_files",
    "tracked_diff_sha256", "snapshot_sha256",
}
HOST_TERMINAL_FIELDS = {
    "schema", "run_id", "spawned", "kind", "detail", "resolved_model",
    "reconciled", "started_at", "ended_at", "policy_resolved",
}
RUN_INTENT_FIELDS = {
    "schema", "run_id", "fixture_id", "call_ordinal", "fixture_sha256",
    "product_checkout", "adapter_name", "adapter_sha256", "harness_commit",
    "model_requested", "reasoning_effort_requested", "policy_requested",
    "required_capabilities", "temp_home", "started_at",
}
PROCESS_STARTED_FIELDS = {
    "schema", "run_id", "cwd", "started_at", "argv_sha256",
    "requested_model", "temp_home", "lane_id", "host_os", "host_boot_id",
    "pid", "process_creation_time", "host_read_pre_spawn_sha256",
}
FIXTURE_AUTH_FIELDS = {"allowed_repository_writes", "forbidden_actions"}
FIXTURE_HOST_CHECK_FIELDS = {"artifact", "specs"}
FIXTURE_PROPERTY_FIELDS = {"name", "required", "describes", "rule"}
REPO_IDENTITY_FIELDS = {"lexical_root", "real_root", "case_sensitive"}
PREIMAGE_TARGET_FIELDS = {
    "canonical_path", "relative_path", "content_base64", "sha256", "size",
    "mode", "symlink_free",
}
TRACE_ACTION_ALLOWED = {
    "id", "state", "effect", "classification", "invocation_invented",
    "invocation_ordinal", "completion_ordinal", "payload", "action_type",
    "command", "path", "paths", "inputs", "output", "exit_code",
    "metadata", "read_transport", "structured_content", "wrapper_layers",
    "protocol_wrapper_valid", "updates", "descendant_complete", "reason",
}
SUPPORTED_READERS = {"cat", "grep", "head", "rg", "sed", "tail"}
AUXILIARY_BUNDLE_ARTIFACTS = {
    "host-stderr.raw", "raw-host-events.jsonl", "derived-transform.json",
}


class EvidenceInvalid(ValueError):
    """Retained evidence cannot support a campaign result."""


def _sha(data):
    return hashlib.sha256(data).hexdigest()


def _read_bytes(path):
    try:
        return pathlib.Path(path).read_bytes()
    except OSError as exc:
        raise EvidenceInvalid(f"missing evidence: {pathlib.Path(path).name}") from exc


def _decode_json(data, owner, malformed, require_object=False):
    def unique(pairs):
        value = {}
        for key, item in pairs:
            if key in value:
                raise EvidenceInvalid(f"{owner} has duplicate key {key!r}")
            value[key] = item
        return value

    try:
        text = data.decode("utf-8") if isinstance(data, bytes) else data
        def nonfinite(value):
            raise EvidenceInvalid(f"{owner} contains non-finite number {value}")
        value = json.loads(text, object_pairs_hook=unique,
                           parse_constant=nonfinite)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise EvidenceInvalid(malformed) from exc
    if require_object and not isinstance(value, dict):
        raise EvidenceInvalid(f"{owner} must be an object")
    return value


def _read_json(path, owner):
    raw = _read_bytes(path)
    value = _decode_json(raw, owner, f"{owner} is malformed", True)
    return value, raw


def _expect(condition, reason):
    if not condition:
        raise EvidenceInvalid(reason)


def _mapping(value, owner):
    _expect(isinstance(value, dict), f"{owner} must be an object")
    return value


def _exact_fields(value, fields, owner):
    value = _mapping(value, owner)
    _expect(set(value) == set(fields), f"{owner} identity shape invalid")
    return value


def _closed_fields(value, required, optional, owner):
    value = _mapping(value, owner)
    keys = set(value)
    required = set(required)
    optional = set(optional)
    _expect(required <= keys and keys <= required | optional,
            f"{owner} exact key set invalid")
    return value


def _strings(value, owner, nonempty=True):
    _expect(isinstance(value, list) and all(
        type(item) is str and (bool(item) or not nonempty) for item in value),
        f"{owner} must be a string list")
    return value


def _validate_contract_declaration(declaration):
    encoding = _exact_fields(
        declaration["encoding"],
        {"charset", "duplicate_keys", "non_finite_numbers", "object_keys",
         "scalar_types", "paths", "writes"}, "artifact contract encoding")
    _expect(encoding == {
        "charset": "UTF-8", "duplicate_keys": "REJECT_RECURSIVELY",
        "non_finite_numbers": "REJECT", "object_keys": "EXACT",
        "scalar_types": "EXACT_NO_COERCION",
        "paths": "CANONICAL_ROLE_CONTAINED_NO_LINK_ALIAS",
        "writes": "CREATE_ONCE"}, "artifact contract encoding drift")
    execution = _exact_fields(
        declaration["execution"],
        {"campaign", "stage_order", "completion_requires", "silent_retry",
         "unexpected_attempt"}, "artifact contract execution")
    _expect(execution == {
        "campaign": "b3v4-sol-r1", "stage_order": ["LUNA", "OPUS"],
        "completion_requires": ["LUNA", "OPUS", "INDEPENDENT_REDERIVATION"],
        "silent_retry": "FORBIDDEN", "unexpected_attempt": "INVALID"},
        "artifact contract execution drift")
    for name, descriptor in declaration["artifacts"].items():
        descriptor = _exact_fields(
            descriptor,
            {"producer", "readers", "role", "format", "schema",
             "create_once"}, f"artifact contract descriptor {name}")
        _expect(type(descriptor["producer"]) is str and descriptor["producer"] and
                isinstance(descriptor["readers"], list) and
                descriptor["readers"] and all(
                    type(reader) is str and reader for reader in
                    descriptor["readers"]) and
                type(descriptor["role"]) is str and descriptor["role"] and
                descriptor["format"] in ("JSON", "JSONL", "BYTES") and
                (descriptor["schema"] is None or
                 (type(descriptor["schema"]) is str and descriptor["schema"])) and
                descriptor["create_once"] is True,
                f"artifact contract descriptor {name} invalid")
    lifecycle = _exact_fields(
        declaration["lifecycle_schemas"],
        {"campaign_manifest", "attempt_status", "attempt_terminal"},
        "artifact contract lifecycle schemas")
    _expect(set(lifecycle["campaign_manifest"]) == CAMPAIGN_MANIFEST_FIELDS and
            set(lifecycle["attempt_status"]) == ATTEMPT_STATUS_FIELDS and
            set(lifecycle["attempt_terminal"]) == ATTEMPT_TERMINAL_FIELDS,
            "artifact contract lifecycle field sets drift")


def _validate_fixture_schema(fixture):
    fixture = _exact_fields(fixture, FIXTURE_FIELDS, "fixture")
    _expect(fixture["id"] == "B3-v3" and
            fixture["fixture_version"] == "B3-v3" and
            fixture["supplementary"] is True,
            "fixture identity schema invalid")
    for key in FIXTURE_FIELDS - {
            "supplementary", "required_capabilities", "authorization_boundary",
            "allowed_paths", "host_checks", "properties"}:
        _expect(type(fixture[key]) is str and bool(fixture[key]),
                f"fixture.{key} invalid")
    _strings(fixture["required_capabilities"], "fixture.required_capabilities")
    _strings(fixture["allowed_paths"], "fixture.allowed_paths")
    authorization = _exact_fields(
        fixture["authorization_boundary"], FIXTURE_AUTH_FIELDS,
        "fixture.authorization_boundary")
    _strings(authorization["allowed_repository_writes"],
             "fixture allowed writes")
    _strings(authorization["forbidden_actions"], "fixture forbidden actions")
    host_checks = _exact_fields(
        fixture["host_checks"], FIXTURE_HOST_CHECK_FIELDS,
        "fixture.host_checks")
    _expect(host_checks["artifact"] == "host-checks.json" and
            isinstance(host_checks["specs"], list) and host_checks["specs"],
            "fixture host checks invalid")
    check_keys = []
    for index, spec in enumerate(host_checks["specs"]):
        owner = f"fixture host check {index}"
        spec = _mapping(spec, owner)
        kind = spec.get("kind")
        if kind == "json_fields_equal":
            spec = _exact_fields(spec, {"key", "kind", "path", "equals"}, owner)
            _repo_relative(spec["path"], owner + ".path")
            _expect(isinstance(spec["equals"], dict) and spec["equals"],
                    owner + " equals invalid")
        elif kind == "path_access_order":
            spec = _exact_fields(spec, {"key", "kind", "reads", "write"}, owner)
            _strings(spec["reads"], owner + ".reads")
            for path in spec["reads"]:
                _repo_relative(path, owner + ".reads path")
            _repo_relative(spec["write"], owner + ".write")
        else:
            raise EvidenceInvalid(f"{owner} kind invalid")
        _expect(type(spec["key"]) is str and spec["key"], owner + " key invalid")
        check_keys.append(spec["key"])
    _expect(len(check_keys) == len(set(check_keys)),
            "fixture host check keys duplicated")
    _expect(isinstance(fixture["properties"], list) and fixture["properties"],
            "fixture properties invalid")
    names = []
    for index, prop in enumerate(fixture["properties"]):
        owner = f"fixture property {index}"
        prop = _exact_fields(prop, FIXTURE_PROPERTY_FIELDS, owner)
        _expect(type(prop["name"]) is str and prop["name"] and
                prop["required"] is True and type(prop["describes"]) is str and
                bool(prop["describes"]), owner + " invalid")
        rule = _mapping(prop["rule"], owner + ".rule")
        if rule.get("kind") == "summary_flag":
            rule = _exact_fields(rule, {"kind", "key"}, owner + ".rule")
            _expect(rule["key"] in check_keys, owner + " rule key invalid")
        elif rule.get("kind") == "changed_paths_within":
            rule = _exact_fields(
                rule, {"kind", "allowed", "required"}, owner + ".rule")
            _strings(rule["allowed"], owner + ".rule.allowed")
            _strings(rule["required"], owner + ".rule.required")
        else:
            raise EvidenceInvalid(owner + " rule kind invalid")
        names.append(prop["name"])
    _expect(len(names) == len(set(names)), "fixture property names duplicated")
    return fixture


def _validate_event_rows(data, expected_run_id):
    rows = _raw_json_lines(data, "bundle events")
    expected_seq = 1
    for _ordinal, row in rows:
        row = _exact_fields(
            row, {"schema", "run_id", "fixture_id", "seq", "role", "kind",
                  "content", "recorded_at"}, "bundle event")
        _expect(row["schema"] == "implementaudit-eval-event-v1" and
                row["run_id"] == expected_run_id and
                row["fixture_id"] == "B3-v3" and
                type(row["seq"]) is int and row["seq"] == expected_seq and
                row["role"] in ("assistant", "user", "system", "tool") and
                type(row["kind"]) is str and row["kind"] and
                type(row["content"]) is str and
                type(row["recorded_at"]) is str and row["recorded_at"],
                "bundle event row invalid")
        expected_seq += 1


def _validate_bundle_manifest_metadata(manifest, packet, mission):
    for key in ("fixture_sha256", "prompt_sha256", "installed_payload_sha256",
                "adapter_sha256", "events_sha256", "repo_before_sha256",
                "repo_after_sha256", "artifact_manifest_sha256",
                "payload_source_sha256", "repo_comparison_sha256"):
        _digest(manifest[key], "bundle manifest " + key)
    for key in ("product_commit", "product_tree", "harness_commit"):
        _git_id(manifest[key], "bundle manifest " + key)
    for key in ("schema", "run_id", "fixture_id", "product_tag",
                "adapter_name", "adapter_version", "model_requested",
                "model_resolved", "host", "started_at", "ended_at",
                "reasoning_effort_requested", "reasoning_effort_resolved"):
        _expect(type(manifest[key]) is str and manifest[key],
                "bundle manifest " + key + " invalid")
    arm = packet[mission["arm"]]
    config_name = mission["config"]
    config = packet["configurations"][config_name]
    _expect(manifest["payload_source_sha256"] == arm["payload_sha256"] and
            manifest["reasoning_effort_requested"] ==
            config["reasoning_effort"] and
            manifest["reasoning_effort_resolved"] ==
            config["reasoning_effort"],
            "bundle manifest payload or effort identity invalid")
    if config_name == "L":
        expected_requested = {
            "sandbox": "workspace-write", "approval": "never",
            "tools": "codex-shell", "network": "restricted",
            "writable_roots": ["<fixture-repo cwd>"]}
        resolved = _exact_fields(
            manifest["policy_resolved"],
            {"class", "sandbox", "approval", "session_id", "cli_version"},
            "bundle resolved Codex policy")
        _expect(resolved["class"] == "host-owned (session turn_context)" and
                resolved["sandbox"] == "workspace-write" and
                resolved["approval"] in ("never", None) and
                type(resolved["session_id"]) is str and resolved["session_id"] and
                type(resolved["cli_version"]) is str and resolved["cli_version"],
                "bundle resolved Codex policy invalid")
    else:
        expected_requested = {
            "sandbox": "claude-headless-tool-permissions",
            "approval": "auto-deny-outside-allowed",
            "tools": "Read Glob Grep Write Edit Bash",
            "network": "tool-mediated only",
            "writable_roots": ["<fixture-repo cwd>"]}
        resolved = _exact_fields(
            manifest["policy_resolved"], {"class", "tools", "note"},
            "bundle resolved Claude policy")
        _expect(resolved["class"] == "adapter-attested (NOT host-owned)" and
                resolved["tools"] ==
                "Read Glob Grep Write Edit Bash (argv-requested)" and
                type(resolved["note"]) is str and resolved["note"],
                "bundle resolved Claude policy invalid")
    _expect(manifest["policy_requested"] == expected_requested,
            "bundle requested policy invalid")
    observed = manifest["models_observed"]
    _expect(isinstance(observed, list) and observed,
            "bundle model observations missing")
    root_models = []
    for index, row in enumerate(observed):
        owner = f"bundle model observation {index}"
        row = _mapping(row, owner)
        role = row.get("role")
        if role == "root-agent":
            row = _exact_fields(
                row, {"model", "role", "source", "session_id"}, owner)
            _expect(row["source"] == "host session turn_context" and
                    type(row["session_id"]) is str and row["session_id"],
                    owner + " invalid")
            root_models.append(row["model"])
        elif role == "root-assistant-events":
            row = _exact_fields(
                row, {"model", "role", "events", "source"}, owner)
            _expect(type(row["events"]) is int and row["events"] > 0 and
                    row["source"] == "host-assigned message.model", owner + " invalid")
            root_models.append(row["model"])
        elif role == "modelUsage-accounting":
            row = _exact_fields(
                row, {"model", "role", "output_tokens",
                      "host_internal_auxiliary", "source"}, owner)
            _expect((row["output_tokens"] is None or
                     type(row["output_tokens"]) is int) and
                    type(row["host_internal_auxiliary"]) is bool and
                    row["source"] == "result.modelUsage", owner + " invalid")
        else:
            raise EvidenceInvalid(owner + " role invalid")
        _expect(type(row["model"]) is str and row["model"], owner + " model invalid")
    _expect(root_models == [manifest["model_resolved"]],
            "bundle root model observation invalid")


def _digest(value, owner):
    _expect(isinstance(value, str) and bool(HEX64.fullmatch(value)),
            f"{owner} must be a lowercase SHA-256")


def _git_id(value, owner):
    _expect(isinstance(value, str) and bool(HEX40.fullmatch(value)),
            f"{owner} must be a lowercase full Git object id")


def _repo_relative(value, owner):
    normalized = _safe_rel(value, owner)
    _expect(value == normalized, f"{owner} must use repository-relative POSIX form")
    return normalized


def _validate_freeze_contract(packet):
    """Independently validate every qualification-critical frozen semantic."""
    packet = _exact_fields(packet, FREEZE_FIELDS, "freeze packet")
    _expect(packet["schema"] == "implementaudit-b3v4-campaign-freeze-v1",
            "freeze packet schema invalid")
    _expect(packet["campaign"] == "b3v4-sol-r1",
            "freeze packet campaign invalid")
    _expect(packet["state"] == "FROZEN_BEFORE_FIRST_MISSION",
            "freeze packet state invalid")

    artifact_contract = _exact_fields(
        packet["artifact_contract"], {"schema", "path", "sha256"},
        "artifact contract identity")
    _expect(artifact_contract["schema"] ==
            "implementaudit-b3v4-artifact-contract-v1",
            "artifact contract schema invalid")
    _expect(artifact_contract["path"] == "eval/b3v4_contract.json",
            "artifact contract path invalid")
    _digest(artifact_contract["sha256"], "artifact contract sha256")
    declaration_path = pathlib.Path(__file__).resolve().parent.parent / \
        pathlib.PurePosixPath(artifact_contract["path"])
    declaration_bytes = _read_bytes(declaration_path)
    _expect(_sha(declaration_bytes) == artifact_contract["sha256"],
            "artifact contract hash mismatch")
    declaration = _decode_json(
        declaration_bytes, "artifact contract",
        "artifact contract is malformed", True)
    declaration = _exact_fields(
        declaration, {"schema", "contract_id", "encoding", "execution",
                      "artifacts", "lifecycle_schemas"}, "artifact contract")
    _expect(declaration["schema"] == artifact_contract["schema"],
            "artifact contract declaration schema invalid")
    _expect(type(declaration["artifacts"]) is dict and
            set(declaration["artifacts"]) == CONTRACT_ARTIFACTS,
            "artifact contract retained artifact set invalid")
    _validate_contract_declaration(declaration)

    foundation = _exact_fields(packet["foundation"], {"commit", "tree"},
                               "foundation")
    for key in ("commit", "tree"):
        _git_id(foundation[key], f"foundation.{key}")

    fixture = _exact_fields(
        packet["fixture"],
        {"id", "fixture_sha256", "complete_manifest_sha256"}, "fixture")
    _expect(fixture["id"] == "B3-v3", "fixture.id invalid")
    _digest(fixture["fixture_sha256"], "fixture.fixture_sha256")
    _digest(fixture["complete_manifest_sha256"],
            "fixture.complete_manifest_sha256")

    artifacts = _mapping(packet["artifacts"], "artifacts")
    _expect(set(artifacts) == {"scorer", "evaluator", "bundle", "runner"},
            "artifacts identity shape invalid")
    for name, value in artifacts.items():
        value = _exact_fields(value, {"path", "sha256"},
                              f"artifacts.{name}")
        _repo_relative(value["path"], f"artifacts.{name}.path")
        _digest(value["sha256"], f"artifacts.{name}.sha256")

    for arm in ("candidate", "control"):
        identity = _exact_fields(
            packet[arm], {"commit", "tree", "skill_tree", "payload_sha256"},
            arm)
        for key in ("commit", "tree", "skill_tree"):
            _git_id(identity[key], f"{arm}.{key}")
        _digest(identity["payload_sha256"], f"{arm}.payload_sha256")
    _expect(packet["candidate"] != packet["control"],
            "candidate and control identities must be distinct")

    configurations = _mapping(packet["configurations"], "configurations")
    _expect(set(configurations) == {"L", "O"},
            "configurations identity shape invalid")
    expected = {
        "L": ("WSL Ubuntu Codex CLI", "gpt-5.6-luna", "gpt-5.6-luna",
              "max", "chatgpt-subscription"),
        "O": ("Windows Claude CLI", "opus", "claude-opus-4-8", "high",
              "claude.ai-max"),
    }
    config_fields = {"host", "model_requested", "model_resolved_required",
                     "reasoning_effort", "auth_mode", "executable"}
    for name, boundary in expected.items():
        config = _exact_fields(configurations[name], config_fields,
                               f"configuration {name}")
        observed = (config["host"], config["model_requested"],
                    config["model_resolved_required"],
                    config["reasoning_effort"], config["auth_mode"])
        _expect(observed == boundary,
                f"configuration {name} identity/auth boundary drift")
        executable = _exact_fields(
            config["executable"], {"path", "version", "sha256"},
            f"configuration {name} executable")
        _expect(all(isinstance(executable[key], str) and executable[key]
                    for key in ("path", "version")),
                f"configuration {name} executable identity incomplete")
        _digest(executable["sha256"],
                f"configuration {name} executable.sha256")

    authorization = _exact_fields(
        packet["authorization"],
        {"acknowledgement_path", "acknowledgement_sha256",
         "metered_api_spend"}, "authorization")
    _expect(isinstance(authorization["acknowledgement_path"], str) and
            bool(authorization["acknowledgement_path"]),
            "authorization.acknowledgement_path invalid")
    _digest(authorization["acknowledgement_sha256"],
            "authorization.acknowledgement_sha256")
    _expect(authorization["metered_api_spend"] == "FORBIDDEN",
            "authorization.metered_api_spend must be FORBIDDEN")

    _expect(type(packet["seed"]) is int and packet["seed"] == 20260718,
            "seed drift")
    _expect(type(packet["repetitions_per_configuration_and_arm"]) is int and
            packet["repetitions_per_configuration_and_arm"] == 3,
            "repetition count drift")
    missions = packet["missions"]
    _expect(isinstance(missions, list) and len(missions) == len(PLAN),
            "fixed 12-mission order drift")
    for index, (mission, planned) in enumerate(zip(missions, PLAN)):
        mission = _exact_fields(mission, {"index", "config", "arm", "rep"},
                                f"mission {index}")
        _expect(type(mission["index"]) is int and mission["index"] == index and
                type(mission["config"]) is str and
                type(mission["arm"]) is str and
                type(mission["rep"]) is int and
                (mission["config"], mission["arm"], mission["rep"]) == planned,
                "fixed 12-mission order drift")

    profiles = _exact_fields(
        packet["evidence_profiles"],
        {"formal_host_read", "raw_stdout", "native_session", "pre_spawn",
         "post_mission_manifest"}, "evidence_profiles")
    _expect(profiles["formal_host_read"] ==
            "implementaudit-host-read-profile-v2",
            "evidence_profiles.formal_host_read must bind formal-v2")
    _expect(all(profiles[key] == "required" for key in
                ("raw_stdout", "native_session", "pre_spawn",
                 "post_mission_manifest")),
            "formal-v2 evidence profiles must be required")

    composition = _exact_fields(
        packet["result_composition"],
        {"product_property_states", "host_states", "overall_states"},
        "result_composition")
    _expect(composition["product_property_states"] ==
            ["PASS", "FAIL", "INCOMPLETE"],
            "product property state composition drift")
    _expect(composition["host_states"] ==
            ["PASS", "INVALID", "ERROR", "SUBSTITUTION"],
            "host state composition drift")
    _expect(composition["overall_states"] ==
            ["PASS", "FAIL", "INVALID", "ERROR"],
            "overall state composition drift")

    attempts = _exact_fields(packet["attempt_policy"],
                             {"silent_retry", "preserve_every_attempt"},
                             "attempt_policy")
    _expect(attempts["silent_retry"] == "FORBIDDEN",
            "attempt_policy.silent_retry must be FORBIDDEN")
    _expect(attempts["preserve_every_attempt"] is True,
            "attempt_policy must preserve every attempt")
    _expect(packet["acceptance_rule"] == ACCEPTANCE_RULE,
            "frozen packet drift: acceptance_rule")
    _expect(packet["invalid_error_rule"] == INVALID_ERROR_RULE,
            "invalid_error_rule drift")
    _expect(packet["stop_conditions"] == STOP_CONDITIONS,
            "stop_conditions drift")

    rederiver = _exact_fields(
        packet["independent_rederiver"],
        {"contract_id", "implementation_identity", "must_not_import",
         "input", "output"}, "independent_rederiver")
    _expect(rederiver["contract_id"] ==
            "implementaudit-b3v4-independent-rederiver-v1",
            "independent_rederiver.contract_id drift")
    identity = _exact_fields(
        rederiver["implementation_identity"], {"path", "sha256"},
        "independent_rederiver.implementation_identity")
    _expect(identity["path"] == "eval/b3v4_rederive.py",
            "independent_rederiver.implementation_identity.path drift")
    _digest(identity["sha256"],
            "independent_rederiver.implementation_identity.sha256")
    _expect(_EXECUTING_REDERIVER_LOAD_ERROR is None,
            "executing independent rederiver identity unavailable")
    loaded_repo_root = _LOADED_REDERIVER_PATH.parent.parent
    expected_loaded_path = loaded_repo_root.joinpath(
        *identity["path"].split("/")).absolute()
    _expect(_LOADED_REDERIVER_PATH == expected_loaded_path,
            "independent rederiver executing path mismatch")
    try:
        expected_canonical_path = expected_loaded_path.resolve(strict=True)
    except OSError as exc:
        raise EvidenceInvalid(
            "independent rederiver executing path unavailable") from exc
    _expect(expected_canonical_path == _EXECUTING_REDERIVER_PATH,
            "independent rederiver canonical path mismatch")
    _expect(not _LOADED_REDERIVER_PATH.is_symlink() and
            _EXECUTING_REDERIVER_LINK_COUNT == 1,
            "independent rederiver path alias forbidden")
    _expect(_sha(_EXECUTING_REDERIVER_BYTES) == identity["sha256"],
            "independent rederiver implementation hash mismatch")
    _expect(rederiver["must_not_import"] == REDERIVER_IMPORT_BOUNDARY,
            "independent_rederiver.must_not_import drift")
    _expect(rederiver["input"] == "retained raw evidence only",
            "independent_rederiver.input drift")
    _expect(rederiver["output"] ==
            "per-mission property, host, and overall rederivation",
            "independent_rederiver.output drift")
    return packet


def _safe_rel(value, owner):
    _expect(isinstance(value, str) and value and "\x00" not in value,
            f"{owner} path invalid")
    value = value.replace("\\", "/")
    parts = value.split("/")
    _expect(not value.startswith("/") and
            not re.match(r"^[A-Za-z]:", value) and
            all(part not in ("", ".", "..") for part in parts),
            f"{owner} path invalid")
    return value


def _contained(root, relative, owner):
    relative = _safe_rel(relative, owner)
    root = pathlib.Path(root).resolve()
    lexical = root.joinpath(*relative.split("/"))
    try:
        resolved = lexical.resolve(strict=True)
        resolved.relative_to(root)
        current = root
        for part in relative.split("/"):
            current = current / part
            _expect(not current.is_symlink(), f"{owner} link alias forbidden")
        _expect(resolved.stat().st_nlink == 1,
                f"{owner} hardlink alias forbidden")
    except (OSError, ValueError) as exc:
        raise EvidenceInvalid(f"{owner} path containment invalid") from exc
    return resolved


def _validate_attempt_status(status, mission, freeze_sha, contract_sha):
    status = _exact_fields(status, ATTEMPT_STATUS_FIELDS, "attempt status")
    _expect(status["schema"] == "implementaudit-b3v4-attempt-status-v1" and
            status["campaign"] == "b3v4-sol-r1" and
            status["freeze_sha256"] == freeze_sha and
            status["contract_sha256"] == contract_sha and
            status["mission"] == mission and
            status["state"] == "PREPARED_BEFORE_HOST_SPAWN" and
            status["execution_mode"] in ("production", "test") and
            type(status["created_at"]) is str and bool(status["created_at"]),
            "attempt status identity invalid")
    return status


def _validate_attempt_terminal(terminal, mission):
    terminal = _exact_fields(
        terminal, ATTEMPT_TERMINAL_FIELDS, "attempt terminal")
    _expect(terminal["schema"] == "implementaudit-b3v4-attempt-terminal-v1" and
            terminal["campaign"] == "b3v4-sol-r1" and
            type(terminal["mission_index"]) is int and
            terminal["mission_index"] == mission["index"] and
            terminal["execution_mode"] in ("production", "test") and
            terminal["overall_status"] in OFFICIAL_STATES and
            type(terminal["completed_at"]) is str and
            bool(terminal["completed_at"]),
            "attempt terminal identity invalid")
    _expect(terminal["official_overall_status"] is None or
            terminal["official_overall_status"] in OFFICIAL_STATES,
            "attempt terminal official status invalid")
    _expect(terminal["official_verdict_sha256"] is None or
            (type(terminal["official_verdict_sha256"]) is str and
             bool(HEX64.fullmatch(terminal["official_verdict_sha256"]))),
            "attempt terminal verdict hash invalid")
    _expect((terminal["official_overall_status"] is None) ==
            (terminal["official_verdict_sha256"] is None),
            "attempt terminal official custody pair invalid")
    if terminal["overall_status"] in CONTINUE_STATES:
        _expect(terminal["official_overall_status"] ==
                terminal["overall_status"],
                "attempt terminal and official status disagree")
        _expect(terminal["official_verdict_sha256"] is not None and
                terminal["stop_reason"] is None and
                terminal["error_type"] is None,
                "attempt terminal continuing state invalid")
    else:
        _expect(type(terminal["stop_reason"]) is str and
                bool(terminal["stop_reason"]),
                "attempt terminal stop reason missing")
    return terminal


def _canonical_snapshot_hash(value):
    body = {key: item for key, item in value.items()
            if key not in ("snapshot_sha256", "changed_files", "unauthorized")}
    return _sha(json.dumps(body, sort_keys=True).encode("utf-8"))


def _validate_snapshot(value, owner):
    value = _exact_fields(value, SNAPSHOT_FIELDS, owner)
    _expect(value["schema"] == "implementaudit-repo-snapshot-v2",
            f"{owner} schema invalid")
    _expect(_canonical_snapshot_hash(value) == value["snapshot_sha256"],
            f"{owner} internal hash invalid")
    for key in ("head_commit", "head_tree", "index_tree"):
        _expect(type(value[key]) is str and bool(HEX40.fullmatch(value[key])),
                f"{owner} {key} invalid")
    for key in ("staged", "unstaged"):
        _expect(isinstance(value[key], list) and
                all(isinstance(path, str) for path in value[key]),
                f"{owner} {key} invalid")
    for key in ("untracked", "worktree_files"):
        _expect(isinstance(value[key], dict), f"{owner} {key} invalid")
    _expect(isinstance(value["renames"], dict), f"{owner} renames invalid")
    for destination, source in value["renames"].items():
        _safe_rel(destination, owner + " rename destination")
        _safe_rel(source, owner + " rename source")
    _digest(value["tracked_diff_sha256"], owner + " tracked diff")
    _digest(value["snapshot_sha256"], owner + " snapshot")
    for mapping_name in ("untracked", "worktree_files"):
        for rel, entry in value[mapping_name].items():
            _validate_snapshot_entry(rel, entry, owner, mapping_name)


def _validate_snapshot_entry(rel, entry, owner, mapping_name):
    rel = _safe_rel(rel, owner)
    _expect(rel.split("/")[0].lower() != ".git",
            f"{owner} Git administrative identity invalid")
    _expect(isinstance(entry, dict), f"{owner} file identity invalid")
    if entry.get("type") == "file":
        _expect(set(entry) == {"type", "sha256"} and
                type(entry["sha256"]) is str and
                bool(HEX64.fullmatch(entry["sha256"])),
                f"{owner} file digest invalid")
    elif entry.get("type") == "symlink":
        _expect(set(entry) == {"type", "target_sha256"} and
                type(entry["target_sha256"]) is str and
                bool(HEX64.fullmatch(entry["target_sha256"])),
                f"{owner} symlink digest invalid")
    elif mapping_name == "untracked" and entry.get("type") == "dir":
        _expect(entry == {"type": "dir"}, f"{owner} dir type invalid")
    else:
        _expect(entry == {"type": "special"},
                f"{owner} file type invalid")


def _changed_paths(before, after):
    _validate_snapshot(before, "repo-before")
    _validate_snapshot(after, "repo-after")
    _expect(before["head_commit"] == after["head_commit"],
            "committed change cannot be independently enumerated")
    changed = set(after["staged"]) | set(after["unstaged"])
    for path, entry in after["untracked"].items():
        if before["untracked"].get(path) != entry:
            changed.add(path)
    provided = after.get("changed_files")
    if provided is not None:
        _expect(set(provided) == changed,
                "repo-after changed_files contradicts rederivation")
    return sorted(changed)


def _path_match(observed, target, preimages):
    if not isinstance(observed, str):
        return False
    observed = observed.replace("\\", "/")
    target_entry = (preimages.get("targets") or {}).get(target)
    if not isinstance(target_entry, dict):
        return False
    root = (preimages.get("repo") or {}).get("lexical_root")
    if not isinstance(root, str):
        return False
    if not observed.startswith("/") and not re.match(r"^[A-Za-z]:/", observed):
        if observed.startswith("./"):
            observed = observed[2:]
        observed = root.rstrip("/") + "/" + observed
    expected = str(target_entry.get("canonical_path", "")).replace("\\", "/")
    case_sensitive = (preimages.get("repo") or {}).get("case_sensitive") is not False
    return observed == expected if case_sensitive else observed.lower() == expected.lower()


def _path_equivalent(observed, expected, preimages):
    if not isinstance(observed, str) or not isinstance(expected, str):
        return False
    root = (preimages.get("repo") or {}).get("lexical_root")
    if not isinstance(root, str):
        return False

    def absolute(value):
        value = value.replace("\\", "/")
        if value.startswith("/") or re.match(r"^[A-Za-z]:/", value):
            return str(pathlib.PurePosixPath(value))
        if any(part == ".." for part in value.split("/")):
            return None
        return str(pathlib.PurePosixPath(root, value))

    left, right = absolute(observed), absolute(expected)
    case_sensitive = (preimages.get("repo") or {}).get("case_sensitive") is not False
    return bool(left and right and
                (left == right if case_sensitive else left.lower() == right.lower()))


def _preimage(preimages, target):
    item = (preimages.get("targets") or {}).get(target)
    _expect(isinstance(item, dict), f"preimage missing for {target}")
    try:
        content = base64.b64decode(item["content_base64"], validate=True)
    except (KeyError, ValueError, TypeError) as exc:
        raise EvidenceInvalid(f"preimage malformed for {target}") from exc
    _expect(_sha(content) == item.get("sha256"),
            f"preimage digest invalid for {target}")
    return content


def _command_tokens(command):
    if not isinstance(command, str) or any(ch in command for ch in ("\n", "\r", "\x00")):
        return None
    try:
        tokens = shlex.split(command, posix=True)
    except ValueError:
        return None
    if len(tokens) >= 3 and pathlib.PurePosixPath(tokens[0]).name in ("bash", "sh") \
            and tokens[1] in ("-c", "-lc"):
        try:
            tokens = shlex.split(tokens[2], posix=True)
        except ValueError:
            return None
    if any(token in ("|", ">", ">>", "<", "&&", ";") or
           any(symbol in token for symbol in (">", "<", "|", ";"))
           for token in tokens):
        return None
    return tokens


def _action_is_read(action, target, content, preimages):
    if action.get("state") != "COMPLETED" or \
            type(action.get("completion_ordinal")) is not int:
        return False
    if action.get("effect") == "read":
        delivered = (action.get("structured_content")
                     if action.get("read_transport") in
                     ("full-line-renderer", "full-exact") else action.get("output"))
        return (_path_match(action.get("path"), target, preimages) and
                not any(key in (action.get("inputs") or {})
                        for key in ("offset", "limit")) and
                isinstance(delivered, str) and delivered.encode("utf-8") == content)
    if action.get("effect") != "command" or action.get("exit_code") != 0 or \
            not isinstance(action.get("output"), str) or \
            action["output"].encode("utf-8") != content:
        return False
    tokens = _command_tokens(action.get("command"))
    if not tokens or pathlib.PurePosixPath(tokens[0]).name not in \
            ("cat", "grep", "head", "rg", "sed", "tail"):
        return False
    return any(_path_match(token, target, preimages) for token in tokens[1:])


def _write_paths(action):
    if action.get("effect") != "write":
        return []
    paths = []
    if isinstance(action.get("path"), str):
        paths.append(action["path"])
    paths.extend(path for path in action.get("paths", []) if isinstance(path, str))
    return paths


def _derive_path_order(spec, trace, preimages):
    reads = spec.get("reads")
    write = spec.get("write")
    _expect(isinstance(reads, list) and reads and
            all(isinstance(path, str) for path in reads) and
            isinstance(write, str), "path-order specification invalid")
    actions = trace.get("actions")
    _expect(isinstance(actions, list) and all(isinstance(a, dict) for a in actions),
            "host action trace invalid")
    completions = {}
    for target in reads:
        content = _preimage(preimages, target)
        matches = [action["completion_ordinal"] for action in actions
                   if _action_is_read(action, target, content, preimages)]
        completions[target] = min(matches) if matches else None
    writes = [action for action in actions
              if action.get("state") == "COMPLETED" and
              type(action.get("invocation_ordinal")) is int and
              type(action.get("completion_ordinal")) is int and
              any(_path_equivalent(path, write, preimages)
                  for path in _write_paths(action))]
    write_invocation = min((action["invocation_ordinal"] for action in writes),
                           default=None)
    if write_invocation is None or any(value is None or value >= write_invocation
                                       for value in completions.values()):
        return False
    for target, completion in completions.items():
        for action in actions:
            invocation = action.get("invocation_ordinal")
            if type(invocation) is int and invocation < completion and any(
                    _path_equivalent(path, target, preimages)
                    for path in _write_paths(action)):
                return False
    return True


def _raw_json_lines(data, owner):
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise EvidenceInvalid(f"{owner} is not UTF-8") from exc
    rows = []
    for ordinal, line in enumerate(text.splitlines(), 1):
        if not line:
            continue
        line_owner = f"{owner} line {ordinal}"
        value = _decode_json(
            line, line_owner, f"{line_owner} malformed", True)
        rows.append((ordinal, value))
    _expect(rows, f"{owner} is empty")
    return rows


def _validate_codex_stdout_rows(rows):
    for ordinal, event in rows:
        owner = f"Codex raw stdout line {ordinal}"
        event_type = event.get("type")
        if event_type == "thread.started":
            _exact_fields(event, {"type", "thread_id"}, owner)
        elif event_type in ("turn.started", "turn.completed"):
            _exact_fields(event, {"type", "thread_id", "turn_id"}, owner)
        elif event_type in ("item.started", "item.updated", "item.completed"):
            _closed_fields(event, {"type", "item"}, {"status"}, owner)
            item = _mapping(event["item"], owner + " item")
            item_type = item.get("type")
            if item_type == "command_execution":
                required = {"id", "type", "status", "command"}
                if event_type == "item.completed":
                    required |= {"aggregated_output", "exit_code"}
                _exact_fields(item, required, owner + " command item")
            elif item_type == "file_change":
                _exact_fields(
                    item, {"id", "type", "status", "changes"},
                    owner + " file-change item")
                _expect(isinstance(item["changes"], list),
                        owner + " file-change list invalid")
                for index, change in enumerate(item["changes"]):
                    change = _exact_fields(
                        change, {"path", "kind"},
                        f"{owner} file-change {index}")
                    _expect(type(change["path"]) is str and change["path"] and
                            type(change["kind"]) is str and change["kind"],
                            f"{owner} file-change {index} invalid")
            elif item_type == "todo_list":
                _exact_fields(
                    item, {"id", "type", "status", "items"},
                    owner + " todo item")
                _expect(isinstance(item["items"], list),
                        owner + " todo list invalid")
                for index, entry in enumerate(item["items"]):
                    entry = _exact_fields(
                        entry, {"text", "completed"},
                        f"{owner} todo row {index}")
                    _expect(type(entry["text"]) is str and
                            type(entry["completed"]) is bool,
                            f"{owner} todo row {index} invalid")
            elif event_type == "item.completed" and item_type == "agent_message":
                _closed_fields(item, {"id", "type", "text"}, {"status"},
                               owner + " agent message")
            else:
                raise EvidenceInvalid(owner + " unsupported item type")
        else:
            raise EvidenceInvalid(owner + " unsupported event type")


def _validate_claude_block(block, owner):
    block = _mapping(block, owner)
    kind = block.get("type")
    if kind == "tool_use":
        block = _exact_fields(block, {"type", "id", "name", "input"}, owner)
        _expect(type(block["id"]) is str and block["id"] and
                type(block["name"]) is str and block["name"], owner + " invalid")
        inputs = _mapping(block["input"], owner + " input")
        if block["name"] == "Read":
            _closed_fields(inputs, {"file_path"}, {"offset", "limit", "pages"},
                           owner + " Read input")
        elif block["name"] == "Write":
            _exact_fields(inputs, {"file_path", "content"},
                          owner + " Write input")
        elif block["name"] == "Edit":
            _closed_fields(inputs, {"file_path", "old_string", "new_string"},
                           {"replace_all"}, owner + " Edit input")
        elif block["name"] == "Bash":
            _closed_fields(inputs, {"command"},
                           {"description", "timeout", "run_in_background",
                            "dangerouslyDisableSandbox"}, owner + " Bash input")
        else:
            _expect(set(inputs) <= {
                "path", "pattern", "glob", "output_mode", "head_limit",
                "offset", "multiline", "-i", "skill", "prompt",
                "description", "subagent_type", "resume", "model",
                "run_in_background", "team_name", "name"},
                owner + " tool input has unknown field")
    elif kind == "tool_result":
        _closed_fields(block, {"type", "tool_use_id", "content", "is_error"},
                       {"status", "interrupted"}, owner)
        _expect(type(block["tool_use_id"]) is str and block["tool_use_id"] and
                type(block["content"]) is str and type(block["is_error"]) is bool,
                owner + " invalid")
    elif kind == "text":
        _exact_fields(block, {"type", "text"}, owner)
        _expect(type(block["text"]) is str, owner + " text invalid")
    else:
        raise EvidenceInvalid(owner + " unsupported block type")


def _validate_claude_rows(rows, owner_prefix="Claude raw stdout"):
    root_optional = {
        "effort", "cwd", "model", "permissionMode", "apiKeySource",
        "mcp_servers", "slash_commands", "output_style", "agents", "skills",
        "plugins", "uuid", "parent_tool_use_id", "tool_use_result",
        "duration_ms", "duration_api_ms", "num_turns", "result",
        "total_cost_usd", "usage", "structured_output", "subtype",
        "tools", "is_error", "action_ids",
    }
    for ordinal, event in rows:
        owner = f"{owner_prefix} line {ordinal}"
        event_type = event.get("type")
        if event_type == "system" and event.get("subtype") in ("init", "transcript"):
            required = {"type", "subtype", "session_id"}
            required.add("tools" if event["subtype"] == "init" else "action_ids")
            _closed_fields(event, required, root_optional, owner)
        elif event_type in ("assistant", "user"):
            _closed_fields(event, {"type", "session_id", "message"},
                           root_optional, owner)
            message = _closed_fields(
                event["message"], {"content"},
                {"model", "id", "type", "role", "stop_reason",
                 "stop_sequence", "usage"}, owner + " message")
            _expect(isinstance(message["content"], list),
                    owner + " content invalid")
            for index, block in enumerate(message["content"]):
                _validate_claude_block(block, f"{owner} block {index}")
        elif event_type == "result":
            _closed_fields(event, {"type", "session_id", "is_error"},
                           root_optional, owner)
            _expect(type(event["is_error"]) is bool, owner + " result invalid")
        else:
            raise EvidenceInvalid(owner + " unsupported event type")


def _parse_codex_actions(raw):
    pending = {}
    actions = []
    reserved = set()
    thread_id = None
    turn_id = None
    bound_turn_id = None
    turn_count = 0
    rows = _raw_json_lines(raw, "Codex raw stdout")
    _validate_codex_stdout_rows(rows)
    for ordinal, event in rows:
        event_type = event.get("type")
        if event_type == "thread.started":
            observed = event.get("thread_id")
            _expect(thread_id is None and isinstance(observed, str) and observed,
                    "Codex raw thread binding invalid")
            thread_id = observed
            continue
        if event_type == "turn.started":
            observed = event.get("turn_id")
            observed_thread = event.get("thread_id", thread_id)
            turn_count += 1
            _expect(thread_id is not None and turn_id is None and
                    turn_count == 1 and observed_thread == thread_id and
                    (observed is None or
                     (isinstance(observed, str) and observed)),
                    "Codex raw turn binding invalid")
            turn_id = observed or "<unique-turn>"
            bound_turn_id = observed
            continue
        if event_type == "turn.completed":
            _expect(turn_id is not None and
                    event.get("thread_id", thread_id) == thread_id and
                    event.get("turn_id", turn_id) == turn_id,
                    "Codex raw turn completion invalid")
            turn_id = None
            continue
        if event_type not in ("item.started", "item.updated", "item.completed"):
            continue
        _expect(thread_id is not None and turn_id is not None,
                "Codex raw action outside bound turn")
        item = event.get("item")
        _expect(isinstance(item, dict), "Codex raw item malformed")
        action_id = item.get("id")
        item_type = item.get("type")
        if event_type == "item.completed" and item_type == "agent_message":
            _expect(isinstance(action_id, str) and action_id and
                    action_id not in reserved and
                    item.get("status") in (None, "completed") and
                    isinstance(item.get("text"), str),
                    "Codex raw terminal message malformed")
            reserved.add(action_id)
            actions.append({"id": action_id,
                            "state": "TERMINAL_SAFE_MESSAGE",
                            "effect": "safe-other",
                            "invocation_ordinal": None,
                            "completion_ordinal": ordinal})
            continue
        if item_type not in ("command_execution", "file_change", "todo_list"):
            continue
        _expect(isinstance(action_id, str) and action_id,
                "Codex raw action id invalid")
        if event_type == "item.started":
            _expect(action_id not in reserved, "Codex raw action id reused")
            reserved.add(action_id)
            if item_type == "command_execution":
                _expect(isinstance(item.get("command"), str),
                        "Codex raw command malformed")
                action = {"id": action_id, "state": "PENDING",
                          "effect": "command", "action_type": item_type,
                          "command": item["command"],
                          "invocation_ordinal": ordinal,
                          "completion_ordinal": None}
            elif item_type == "file_change":
                changes = item.get("changes")
                _expect(isinstance(changes, list) and all(
                    isinstance(change, dict) and
                    isinstance(change.get("path"), str) for change in changes),
                    "Codex raw file change malformed")
                action = {"id": action_id, "state": "PENDING",
                          "effect": "write", "action_type": item_type,
                          "paths": [change["path"] for change in changes],
                          "invocation_ordinal": ordinal,
                          "completion_ordinal": None}
            else:
                items = item.get("items")
                _expect(isinstance(items, list) and all(
                    isinstance(entry, dict) and
                    set(entry) == {"text", "completed"} and
                    isinstance(entry["text"], str) and
                    type(entry["completed"]) is bool for entry in items),
                    "Codex raw todo list malformed")
                action = {"id": action_id, "state": "PENDING",
                          "effect": "safe-other", "action_type": item_type,
                          "invocation_ordinal": ordinal,
                          "completion_ordinal": None}
            pending[action_id] = action
            actions.append(action)
            continue
        if event_type == "item.updated":
            action = pending.get(action_id)
            _expect(action is not None and action["action_type"] == "todo_list" and
                    item_type == "todo_list" and
                    item.get("status") in (None, "in_progress") and
                    isinstance(item.get("items"), list),
                    "Codex raw todo update invalid")
            continue
        action = pending.pop(action_id, None)
        _expect(action is not None, "Codex raw completion without invocation")
        _expect(item_type == action["action_type"],
                "Codex raw start/completion action type contradiction")
        if action["effect"] == "command":
            exit_code = item.get("exit_code")
            output = item.get("aggregated_output")
            _expect(type(exit_code) is int and isinstance(output, str) and
                    item.get("status") == ("completed" if exit_code == 0 else "failed"),
                    "Codex raw command completion contradictory")
            _expect(item.get("command") == action["command"],
                    "Codex raw command payload contradiction")
            action.update({"state": "COMPLETED", "exit_code": exit_code,
                           "output": output, "completion_ordinal": ordinal})
        elif action["effect"] == "write":
            changes = item.get("changes")
            _expect(item.get("status") == "completed" and
                    isinstance(changes, list) and
                    [change.get("path") for change in changes
                     if isinstance(change, dict)] == action["paths"],
                    "Codex raw write completion invalid")
            action.update({"state": "COMPLETED", "completion_ordinal": ordinal})
        else:
            _expect(item.get("status") in (None, "completed"),
                    "Codex raw todo completion invalid")
            action.update({"state": "COMPLETED", "completion_ordinal": ordinal})
    _expect(not pending and actions and thread_id is not None and
            turn_count == 1 and turn_id is None,
            "Codex raw action stream incomplete")
    binding = {"thread_id": thread_id, "stdout_turn_ordinal": 1}
    if bound_turn_id is not None:
        binding["turn_id"] = bound_turn_id
    return actions, binding


def _parse_claude_actions(raw):
    pending = {}
    actions = []
    reserved = set()
    inventory_seen = False
    session_id = None
    observed_tools = None
    rows = _raw_json_lines(raw, "Claude raw stdout")
    _validate_claude_rows(rows)
    for ordinal, event in rows:
        if event.get("type") == "system" and event.get("subtype") == "init":
            observed_session = event.get("session_id")
            _expect(not inventory_seen and isinstance(event.get("tools"), list) and
                    all(isinstance(tool, str) and tool
                        for tool in event["tools"]) and
                    len(event["tools"]) == len(set(event["tools"])) and
                    isinstance(observed_session, str) and observed_session,
                    "Claude raw tool inventory invalid")
            inventory_seen = True
            session_id = observed_session
            observed_tools = list(event["tools"])
            continue
        role = event.get("type")
        if role not in ("assistant", "user"):
            continue
        _expect(session_id is not None and event.get("session_id") == session_id,
                "Claude raw session mismatch")
        message = event.get("message")
        _expect(isinstance(message, dict) and isinstance(message.get("content"), list),
                "Claude raw message malformed")
        for block in message["content"]:
            _expect(isinstance(block, dict), "Claude raw content block malformed")
            if role == "assistant" and block.get("type") == "tool_use":
                action_id = block.get("id")
                tool = block.get("name")
                inputs = block.get("input")
                _expect(isinstance(action_id, str) and action_id and
                        action_id not in reserved and isinstance(inputs, dict),
                        "Claude raw tool invocation invalid")
                reserved.add(action_id)
                _expect(tool in ("Read", "Write", "Edit", "Bash", "Grep",
                                 "Glob", "Skill", "Task", "Workflow"),
                        "Claude raw unsupported tool in B3-v4 evidence")
                effect = ("read" if tool == "Read" else
                          "write" if tool in ("Write", "Edit") else
                          "command" if tool == "Bash" else
                          "search" if tool == "Grep" else "safe-other")
                if tool in ("Task", "Workflow"):
                    effect = "descendant"
                path = (inputs.get("file_path") if effect in ("read", "write")
                        else inputs.get("path") if effect == "search" else None)
                if effect in ("read", "write", "search"):
                    _expect(isinstance(path, str) and path,
                            "Claude raw tool path invalid")
                if effect == "command":
                    _expect(isinstance(inputs.get("command"), str) and
                            inputs["command"], "Claude raw command invalid")
                action = {"id": action_id, "state": "PENDING",
                          "effect": effect,
                          "action_type": tool,
                          "path": path, "inputs": inputs,
                          "command": inputs.get("command"),
                          "invocation_ordinal": ordinal,
                          "completion_ordinal": None}
                pending[action_id] = action
                actions.append(action)
            elif role == "user" and block.get("type") == "tool_result":
                action_id = block.get("tool_use_id")
                action = pending.pop(action_id, None)
                _expect(action is not None and "is_error" in block and
                        type(block.get("is_error")) is bool and
                        block["is_error"] is False,
                        "Claude raw tool completion invalid")
                content = block.get("content")
                _expect(isinstance(content, str), "Claude raw tool result malformed")
                action.update({"state": "COMPLETED", "output": content,
                               "completion_ordinal": ordinal})
                if action["effect"] == "command":
                    action["exit_code"] = 0
    _expect(inventory_seen and not pending and actions and session_id,
            "Claude raw action stream incomplete")
    return actions, {"session_id": session_id}, observed_tools


def _parse_raw_actions(raw, host):
    if host == "codex":
        actions, binding = _parse_codex_actions(raw)
        return actions, binding, []
    if host == "claude":
        return _parse_claude_actions(raw)
    raise EvidenceInvalid("unsupported formal-v2 host")


def _canonical_json(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode(
        "utf-8")


def _scalar_strings(value):
    if isinstance(value, dict):
        for item in value.values():
            yield from _scalar_strings(item)
    elif isinstance(value, list):
        for item in value:
            yield from _scalar_strings(item)
    elif isinstance(value, str):
        yield value


def _validate_profile_and_post(profile, post, expected_host):
    common = {"schema", "authority", "host", "repo", "probe_sha256"}
    _expect(profile.get("schema") == "implementaudit-host-read-profile-v2" and
            profile.get("authority") == "mechanically-minted" and
            profile.get("host") == expected_host and
            bool(HEX64.fullmatch(str(profile.get("probe_sha256", "")))),
            "formal-v2 host profile invalid")
    repo = profile.get("repo")
    _expect(isinstance(repo, dict) and
            set(repo) == {"lexical_root", "real_root", "case_sensitive"} and
            type(repo["lexical_root"]) is str and bool(repo["lexical_root"]) and
            type(repo["real_root"]) is str and bool(repo["real_root"]) and
            type(repo["case_sensitive"]) is bool,
            "formal-v2 profile repository invalid")
    if expected_host == "codex":
        _expect(set(profile) == common | {
            "shell", "outer_wrapper", "environment", "executables"},
            "formal-v2 Codex profile fields invalid")
        shell = profile["shell"]
        wrapper = profile["outer_wrapper"]
        _expect(isinstance(shell, dict) and
                set(shell) == {"logical_path", "realpath", "sha256", "stat"} and
                all(type(shell[key]) is str and bool(shell[key])
                    for key in ("logical_path", "realpath", "sha256", "stat")) and
                bool(HEX64.fullmatch(shell["sha256"])) and
                wrapper == {"argv_prefix": ["/bin/bash", "-lc"],
                            "max_unwrap_layers": 1} and
                isinstance(profile["environment"], dict) and
                set(profile["environment"]) == {
                    "PATH", "LANG", "LC_ALL", "BASH_ENV", "ENV", "SHELL"} and
                all(value is None or type(value) is str
                    for value in profile["environment"].values()) and
                isinstance(profile["executables"], dict) and
                set(profile["executables"]) == SUPPORTED_READERS,
                "formal-v2 Codex profile semantics invalid")
        for name, identity in profile["executables"].items():
            identity = _exact_fields(
                identity, {"kind", "path", "sha256", "stat"},
                f"formal-v2 Codex executable {name}")
            _expect(identity["kind"] == "file" and
                    all(type(identity[key]) is str and identity[key]
                        for key in ("path", "sha256", "stat")) and
                    bool(HEX64.fullmatch(identity["sha256"])),
                    f"formal-v2 Codex executable {name} invalid")
        probe = {"environment": profile["environment"], "shell": shell,
                 "executables": profile["executables"]}
        _expect(post == probe and profile["probe_sha256"] == _sha(
            _canonical_json(probe)), "formal-v2 Codex post-probe drift")
    else:
        _expect(set(profile) == common | {"native_tools"} and
                isinstance(profile["native_tools"], dict) and
                set(profile["native_tools"]) == {"requested"} and
                isinstance(profile["native_tools"]["requested"], list) and
                all(type(tool) is str and bool(tool)
                    for tool in profile["native_tools"]["requested"]),
                "formal-v2 Claude profile semantics invalid")
        probe = {"repo": repo["lexical_root"],
                 "native_tools": profile["native_tools"]}
        _expect(post == {"native_tools": profile["native_tools"]} and
                profile["probe_sha256"] == _sha(_canonical_json(probe)),
                "formal-v2 Claude post-probe drift")


def _validate_native_session(stdout, session, expected_host, binding,
                             stdout_binding, actions, profile, process):
    _expect(session and session != stdout, "native session evidence substituted")
    rows = [value for _, value in _raw_json_lines(
        session, expected_host.title() + " native session")]
    indexed_rows = list(enumerate(rows, 1))
    _expect(isinstance(binding, dict), "terminal lineage binding malformed")
    if expected_host == "codex":
        for ordinal, row in indexed_rows:
            owner = f"Codex native session line {ordinal}"
            _exact_fields(row, {"type", "timestamp", "payload"}, owner)
            payload = _mapping(row["payload"], owner + " payload")
            if row["type"] == "session_meta":
                _closed_fields(
                    payload, {"id", "session_id", "cwd"},
                    {"originator", "cli_version", "source", "model_provider",
                     "git", "base_instructions", "developer_instructions",
                     "dynamic_tools", "reasoning_effort", "timestamp"},
                    owner + " payload")
            elif row["type"] == "turn_context":
                _closed_fields(
                    payload, {"turn_id", "cwd"},
                    {"current_date", "timezone", "approval_policy",
                     "sandbox_policy", "model", "effort", "summary",
                     "service_tier"}, owner + " payload")
            elif row["type"] in ("response_item", "event_msg"):
                _expect(set(payload) <= {
                    "action_ids", "type", "role", "content", "id", "status",
                    "name", "arguments", "call_id", "summary", "message",
                    "phase", "text", "images", "encrypted_content"},
                    owner + " payload has unknown field")
            else:
                raise EvidenceInvalid(owner + " unsupported row type")
        allowed = {"thread_id", "stdout_turn_ordinal", "turn_id",
                   "native_turn_id"}
        _expect(set(binding) <= allowed and
                {"thread_id", "stdout_turn_ordinal", "native_turn_id"} <=
                set(binding) and binding["stdout_turn_ordinal"] == 1 and
                all(type(binding[key]) is str and bool(binding[key])
                    for key in set(binding) - {"stdout_turn_ordinal"}) and
                all(binding.get(key) == value
                    for key, value in stdout_binding.items()),
                "Codex terminal lineage binding invalid")
        metas = [row for row in rows if row.get("type") == "session_meta"]
        turns = [row for row in rows if row.get("type") == "turn_context"]
        _expect(len(metas) == 1 and len(turns) == 1 and
                isinstance(metas[0].get("payload"), dict) and
                isinstance(turns[0].get("payload"), dict),
                "Codex native session state invalid")
        meta, turn = metas[0]["payload"], turns[0]["payload"]
        root = profile["repo"]["lexical_root"]
        _expect(meta.get("id") == binding["thread_id"] and
                meta.get("session_id") == binding["thread_id"] and
                meta.get("cwd") == root and turn.get("cwd") == root and
                turn.get("turn_id") == binding["native_turn_id"] and
                type(process.get("started_at")) is str and
                type(metas[0].get("timestamp")) is str and
                type(turns[0].get("timestamp")) is str and
                process["started_at"] <= metas[0]["timestamp"] <=
                turns[0]["timestamp"],
                "Codex native session identity mismatch")
    else:
        _validate_claude_rows(indexed_rows, "Claude native session")
        _expect(set(binding) == {"session_id"} and
                type(binding["session_id"]) is str and bool(binding["session_id"]) and
                binding == stdout_binding,
                "Claude terminal lineage binding invalid")
        scalars = set(_scalar_strings(rows))
        _expect(binding["session_id"] in scalars and
                all(action["id"] in scalars for action in actions),
                "Claude native session identity mismatch")


def _validate_trace_agreement(trace, actions, observed_tools, expected_host):
    expected_fields = {"schema", "actions", "invalid", "host_findings",
                       "ids_reserved", "action_states", "action_effects",
                       "host_status", "requested_tools", "observed_tools"}
    if expected_host == "claude":
        expected_fields.add("crashed")
    _expect(set(trace) == expected_fields and
            trace["schema"] == "implementaudit-host-tool-trace-v2" and
            trace["invalid"] is False and trace["ids_reserved"] is True and
            trace["host_status"] == "PASS" and trace["host_findings"] == [] and
            (expected_host != "claude" or trace["crashed"] is False) and
            trace["observed_tools"] == observed_tools and
            isinstance(trace["actions"], list),
            "formal-v2 trace host state invalid")
    retained = {item.get("id"): item for item in trace["actions"]
                if isinstance(item, dict) and isinstance(item.get("id"), str)}
    raw_ids = {item["id"] for item in actions}
    extras = [item for item in trace["actions"]
              if isinstance(item, dict) and item.get("id") not in raw_ids]
    _expect(len(retained) == len(trace["actions"]) and
            raw_ids <= set(retained) and
            all(item.get("effect") == "safe-other" and
                item.get("state") == "TERMINAL_SAFE_MESSAGE"
                for item in extras),
            "formal-v2 raw/trace action identity disagreement")
    for action in actions:
        item = retained[action["id"]]
        for key in ("state", "effect", "invocation_ordinal",
                    "completion_ordinal"):
            _expect(item.get(key) == action.get(key),
                    "formal-v2 raw/trace action disagreement")
        for key in ("action_type", "command", "path", "paths"):
            if key in action:
                _expect(item.get(key) == action[key],
                        "formal-v2 raw/trace payload disagreement")
    projected = [item for item in trace["actions"]
                 if not str(item.get("id", "")).startswith("invalid@")]
    _expect(trace["action_states"] == [item["state"] for item in projected] and
            trace["action_effects"] == [item["effect"] for item in projected],
            "formal-v2 trace projections disagree")


def _validate_preimages_schema(preimages):
    preimages = _exact_fields(
        preimages, {"schema", "repo", "targets"}, "host preimages")
    _expect(preimages["schema"] == "implementaudit-host-read-preimages-v1",
            "host preimages schema invalid")
    repo = _exact_fields(preimages["repo"], REPO_IDENTITY_FIELDS,
                         "host preimages repository")
    _expect(type(repo["lexical_root"]) is str and repo["lexical_root"] and
            type(repo["real_root"]) is str and repo["real_root"] and
            type(repo["case_sensitive"]) is bool,
            "host preimages repository invalid")
    targets = _mapping(preimages["targets"], "host preimage targets")
    _expect(bool(targets), "host preimage targets empty")
    for relative, entry in targets.items():
        _repo_relative(relative, "host preimage target")
        entry = _exact_fields(
            entry, PREIMAGE_TARGET_FIELDS, f"host preimage {relative}")
        _expect(entry["relative_path"] == relative and
                type(entry["canonical_path"]) is str and
                bool(entry["canonical_path"]) and
                type(entry["content_base64"]) is str and
                type(entry["size"]) is int and entry["size"] >= 0 and
                type(entry["mode"]) is int and entry["mode"] >= 0 and
                entry["symlink_free"] is True,
                f"host preimage {relative} invalid")
        _digest(entry["sha256"], f"host preimage {relative} sha256")
        try:
            decoded = base64.b64decode(entry["content_base64"], validate=True)
        except (ValueError, TypeError) as exc:
            raise EvidenceInvalid(f"host preimage {relative} base64 invalid") from exc
        _expect(len(decoded) == entry["size"] and _sha(decoded) == entry["sha256"],
                f"host preimage {relative} content invalid")


def _validate_replay_schema(replay):
    replay = _exact_fields(
        replay, {"schema", "mode", "host", "checks", "requested_tools",
                 "fixture_sha256", "run_intent_sha256", "parser_sha256"},
        "host replay specification")
    _expect(replay["schema"] == "implementaudit-host-read-replay-spec-v1" and
            replay["mode"] == "formal-v2" and
            replay["host"] in ("codex", "claude"),
            "host replay specification identity invalid")
    for key in ("fixture_sha256", "run_intent_sha256", "parser_sha256"):
        _digest(replay[key], "host replay " + key)
    _strings(replay["requested_tools"], "host replay requested tools")
    _expect(isinstance(replay["checks"], list) and replay["checks"],
            "host replay checks invalid")
    for index, check in enumerate(replay["checks"]):
        check = _exact_fields(
            check, {"key", "reads", "write"}, f"host replay check {index}")
        _expect(type(check["key"]) is str and check["key"],
                f"host replay check {index} key invalid")
        _strings(check["reads"], f"host replay check {index} reads")
        for path in check["reads"]:
            _repo_relative(path, f"host replay check {index} read")
        _repo_relative(check["write"], f"host replay check {index} write")


def _validate_parent_custody_objects(intent, process, expected_run_id):
    intent = _exact_fields(intent, RUN_INTENT_FIELDS, "run intent")
    _expect(intent["schema"] == "implementaudit-run-intent-v1" and
            intent["run_id"] == expected_run_id and
            intent["fixture_id"] == "B3-v3" and
            type(intent["call_ordinal"]) is int and intent["call_ordinal"] > 0 and
            type(intent["product_checkout"]) is str and intent["product_checkout"] and
            type(intent["adapter_name"]) is str and intent["adapter_name"] and
            type(intent["harness_commit"]) is str and
            type(intent["model_requested"]) is str and intent["model_requested"] and
            type(intent["reasoning_effort_requested"]) is str and
            isinstance(intent["policy_requested"], dict) and
            isinstance(intent["required_capabilities"], list) and
            type(intent["temp_home"]) is str and intent["temp_home"] and
            type(intent["started_at"]) is str and intent["started_at"],
            "run intent fields invalid")
    for key in ("fixture_sha256", "adapter_sha256"):
        _digest(intent[key], "run intent " + key)
    _git_id(intent["harness_commit"], "run intent harness commit")
    _strings(intent["required_capabilities"], "run intent capabilities")
    process = _exact_fields(process, PROCESS_STARTED_FIELDS, "process started")
    _expect(process["schema"] == "implementaudit-process-started-v2" and
            process["run_id"] == expected_run_id and
            all(type(process[key]) is str and process[key]
                for key in ("cwd", "started_at", "requested_model", "temp_home",
                            "lane_id", "host_os", "host_boot_id")) and
            type(process["pid"]) is int and process["pid"] > 0 and
            type(process["process_creation_time"]) in (int, float) and
            not isinstance(process["process_creation_time"], bool),
            "process started fields invalid")
    for key in ("argv_sha256", "host_read_pre_spawn_sha256"):
        _digest(process[key], "process started " + key)


def _validate_trace_action_rows(trace):
    for index, action in enumerate(trace["actions"]):
        owner = f"host trace action {index}"
        action = _mapping(action, owner)
        keys = set(action)
        _expect(keys <= TRACE_ACTION_ALLOWED, owner + " has unknown field")
        if action.get("state") == "TERMINAL_SAFE_MESSAGE":
            required = {"id", "state", "effect", "classification", "payload",
                        "invocation_invented", "invocation_ordinal",
                        "completion_ordinal"}
        else:
            required = {"id", "state", "effect", "classification",
                        "invocation_invented", "invocation_ordinal",
                        "completion_ordinal", "payload", "action_type"}
        _expect(required <= keys, owner + " fields incomplete")
        _expect(type(action["id"]) is str and action["id"] and
                action["state"] in ("COMPLETED", "TERMINAL_SAFE_MESSAGE") and
                action["effect"] in (
                    "read", "write", "command", "search", "safe-other",
                    "descendant") and
                type(action["completion_ordinal"]) is int and
                (action["invocation_ordinal"] is None or
                 type(action["invocation_ordinal"]) is int) and
                action["invocation_invented"] is False,
                owner + " core fields invalid")


def _matrix_row(spec, actions, preimages):
    reads = spec["reads"]
    write = spec["write"]
    completions = {}
    for target in reads:
        content = _preimage(preimages, target)
        matches = [action["completion_ordinal"] for action in actions
                   if _action_is_read(action, target, content, preimages)]
        completions[target] = min(matches) if matches else None
    writes = [action for action in actions
              if action.get("state") == "COMPLETED" and
              any(_path_equivalent(path, write, preimages)
                  for path in _write_paths(action))]
    _expect(len(writes) == 1 and len(_write_paths(writes[0])) == 1,
            "formal-v2 repeated or ambiguous write")
    write_invocation = writes[0]["invocation_ordinal"]
    ordered = all(type(value) is int and value < write_invocation
                  for value in completions.values())
    live_preimage = True
    for target, completion in completions.items():
        for action in actions:
            invocation = action.get("invocation_ordinal")
            if (type(invocation) is int and type(completion) is int and
                    invocation < completion and any(
                        _path_equivalent(path, target, preimages)
                        for path in _write_paths(action))):
                live_preimage = False
    passed = all(value is not None for value in completions.values()) and \
        ordered and live_preimage
    return {
        "schema": "implementaudit-host-read-matrix-v1",
        "property_status": "PASS" if passed else "INCOMPLETE",
        "host_status": "PASS", "overall_status": (
            "PASS" if passed else "INCOMPLETE"), "ordered": ordered,
        "ordering_source": "persisted-ordinal", "write_completed": True,
        "write_invocation_ordinal": write_invocation,
        "borrowed_completion": False, "live_preimage": live_preimage,
        "reads": {target: {
            "classification": ("content-read" if completions[target] is not None
                               else "fail-closed"),
            "completion_ordinal": completions[target]} for target in reads},
        "host_findings": [], "shell_write_observations": 0,
    }


def _validate_capture(artifacts, fixture_bytes, fixture, expected_host,
                      parent_kind, expected_run_id):
    required = set(CAPTURE_FILES) | {"host-read-manifest.json",
                                     "run-intent.json", "process-started.json",
                                     "host-checks.json"} | \
        AUXILIARY_BUNDLE_ARTIFACTS
    for spec in (fixture.get("host_checks") or {}).get("specs", []):
        if spec.get("kind") == "json_fields_equal":
            path = _safe_rel(spec.get("path"), "host-check input")
            required.add("host-check-inputs/" + path)
    _expect(set(artifacts) == required,
            "formal-v2 capture artifact set incomplete or unexpected")
    objects = {}
    json_names = [name for name in required
                  if not name.endswith((".raw", ".jsonl"))]
    for name in json_names:
        value = _decode_json(
            artifacts[name], name, f"{name} malformed", True)
        objects[name] = value
    derived = _exact_fields(
        objects["derived-transform.json"],
        {"schema", "transform", "source", "source_raw_sha256", "rules"},
        "derived transform")
    adapter = "codex-cli" if expected_host == "codex" else "claude-cli"
    allowed_sources = ({"codex-exec-json", "codex-exec-transcript",
                        "codex-stdout-fallback", "codex-session-jsonl"}
                       if expected_host == "codex" else
                       {"claude-stream-json", "claude-result-json"})
    _expect(derived["schema"] == "implementaudit-derived-view-v1" and
            derived["transform"] == adapter + "-host-event-extraction-v2" and
            derived["source"] in allowed_sources and
            derived["source_raw_sha256"] ==
            _sha(artifacts["raw-host-events.jsonl"]) and
            type(derived["rules"]) is str and derived["rules"] and
            artifacts["raw-host-events.jsonl"] == artifacts["host-session.raw"],
            "derived host-event custody invalid")
    manifest = objects["host-read-manifest.json"]
    _expect(set(manifest) == {"schema", "files"} and
            manifest.get("schema") == "implementaudit-host-read-manifest-v1" and
            set(manifest.get("files", {})) == set(CAPTURE_FILES),
            "formal-v2 manifest invalid")
    actual = {name: _sha(artifacts[name]) for name in CAPTURE_FILES}
    _expect(manifest["files"] == actual, "formal-v2 manifest hash mismatch")
    terminal = objects["host-read-terminal.json"]
    _expect(set(terminal) == {"schema", "hashes", "post_probe_sha256",
                              "profile_post_status", "binding", "actual_tools",
                              "normalized_host_status", "host_terminal_kind",
                              "session_bound", "session_status"} and
            terminal.get("schema") == "implementaudit-host-read-terminal-v1" and
            terminal.get("hashes") == {name: actual[name]
                                        for name in CAPTURE_FILES[:-1]},
            "formal-v2 terminal hash mismatch")
    _expect(terminal.get("host_terminal_kind") == parent_kind,
            "formal-v2 parent terminal mismatch")
    profile = objects["host-read-profile.json"]
    post = objects["host-read-post-probe.json"]
    _validate_profile_and_post(profile, post, expected_host)
    _validate_preimages_schema(objects["host-read-preimages.json"])
    _expect(terminal.get("profile_post_status") == "PASS" and
            terminal.get("normalized_host_status") == "PASS" and
            terminal.get("session_bound") is True and
            terminal.get("session_status") == "VALID" and
            terminal.get("post_probe_sha256") == _sha(_canonical_json(post)),
            "formal-v2 terminal host state invalid")
    _expect(bool(artifacts["host-stdout.raw"]) and
            bool(artifacts["host-session.raw"]),
            "raw host evidence incomplete")
    pre_spawn = objects["host-read-pre-spawn.json"]
    expected_pre = {
        "profile_sha256": actual["host-read-profile.json"],
        "preimages_sha256": actual["host-read-preimages.json"],
        "fixture_sha256": actual["host-read-fixture.raw"],
        "replay_spec_sha256": actual["host-read-replay-spec.json"],
    }
    _expect(set(pre_spawn) == {"schema", "created_before_spawn",
                               "profile_sha256", "preimages_sha256",
                               "fixture_sha256", "replay_spec_sha256"} and
            pre_spawn.get("schema") == "implementaudit-host-read-pre-spawn-v1" and
            pre_spawn.get("created_before_spawn") is True and
            all(pre_spawn.get(key) == value for key, value in expected_pre.items()),
            "formal-v2 pre-spawn custody invalid")
    _expect(artifacts["host-read-fixture.raw"] == fixture_bytes,
            "formal-v2 fixture bytes drift")
    intent = objects["run-intent.json"]
    replay = objects["host-read-replay-spec.json"]
    process = objects["process-started.json"]
    _validate_replay_schema(replay)
    _validate_parent_custody_objects(intent, process, expected_run_id)
    expected_checks = [{"key": spec["key"],
                        "reads": list(spec.get("reads") or []),
                        "write": spec.get("write")}
                       for spec in (fixture.get("host_checks") or {}).get("specs", [])
                       if spec.get("kind") == "path_access_order"]
    _expect(set(replay) == {"schema", "mode", "host", "checks",
                            "requested_tools", "fixture_sha256",
                            "run_intent_sha256", "parser_sha256"} and
            replay.get("schema") == "implementaudit-host-read-replay-spec-v1" and
            replay.get("mode") == "formal-v2" and
            replay.get("host") == expected_host and
            replay.get("checks") == expected_checks and
            replay.get("fixture_sha256") == _sha(fixture_bytes) and
            replay.get("run_intent_sha256") == _sha(artifacts["run-intent.json"]),
            "formal-v2 replay recipe invalid")
    _expect(intent.get("fixture_sha256") == _sha(fixture_bytes) and
            intent.get("run_id") == expected_run_id and
            process.get("run_id") == expected_run_id and
            process.get("host_read_pre_spawn_sha256") ==
            actual["host-read-pre-spawn.json"],
            "formal-v2 parent custody chain invalid")
    trace = objects["host-tool-trace.json"]
    _validate_trace_action_rows(trace)
    raw_actions, stdout_binding, observed_tools = _parse_raw_actions(
        artifacts["host-stdout.raw"], expected_host)
    writes = [action for action in raw_actions if action.get("effect") == "write"]
    allowed_writes = fixture.get("allowed_paths")
    _expect(isinstance(allowed_writes, list) and len(allowed_writes) == 1 and
            len(writes) == 1 and len(_write_paths(writes[0])) == 1 and
            _path_equivalent(
                _write_paths(writes[0])[0], allowed_writes[0],
                objects["host-read-preimages.json"]),
            "formal-v2 raw stream violates the one-write boundary")
    _validate_trace_agreement(trace, raw_actions, observed_tools, expected_host)
    _validate_native_session(
        artifacts["host-stdout.raw"], artifacts["host-session.raw"],
        expected_host, terminal["binding"], stdout_binding, raw_actions,
        profile, process)
    _expect(terminal["actual_tools"] == observed_tools,
            "formal-v2 terminal tool inventory disagreement")
    matrix = objects["host-read-matrix.json"]
    expected_specs = {}
    for spec in (fixture.get("host_checks") or {}).get("specs", []):
        if spec.get("kind") == "path_access_order":
            expected_specs[spec["key"]] = _matrix_row(
                spec, raw_actions, objects["host-read-preimages.json"])
    expected_matrix = {
        "schema": "implementaudit-host-read-matrix-v1",
        "raw_transforms": {
            "host-stdout.raw": expected_host + "-typed-action-normalizer-v2",
            "host-session.raw": "lineage-corroboration-only"},
        "specs": expected_specs,
    }
    _expect(matrix == expected_matrix,
            "formal-v2 matrix does not independently regenerate")
    host_checks = objects["host-checks.json"]
    expected_check_keys = {
        spec["key"] for spec in (fixture.get("host_checks") or {}).get(
            "specs", [])}
    _expect(isinstance(host_checks, dict) and
            set(host_checks) == expected_check_keys and
            all(type(value) is bool for value in host_checks.values()),
            "formal-v2 host check aggregate malformed")
    return (objects["host-read-preimages.json"], trace, raw_actions,
            host_checks)


def _load_bundle(bundle, packet, mission, parent_terminal):
    manifest, _ = _read_json(bundle / "manifest.json", "bundle manifest")
    fixture_bytes = _read_bytes(bundle / "fixture.json")
    prompt = _read_bytes(bundle / "prompt.txt")
    events = _read_bytes(bundle / "events.jsonl")
    before, before_bytes = _read_json(bundle / "repo-before.json", "repo-before")
    after, after_bytes = _read_json(bundle / "repo-after.json", "repo-after")
    comparison, comparison_bytes = _read_json(
        bundle / "repo-comparison.json", "repo comparison")
    artifact_manifest, artifact_manifest_bytes = _read_json(
        bundle / "artifact-manifest.json", "artifact manifest")
    manifest = _closed_fields(
        manifest, BUNDLE_MANIFEST_FIELDS, BUNDLE_MANIFEST_OPTIONAL_FIELDS,
        "bundle manifest")
    _expect(manifest["schema"] == "implementaudit-eval-manifest-v2",
            "bundle manifest schema invalid")
    _validate_bundle_manifest_metadata(manifest, packet, mission)
    for name, data, key in (("fixture", fixture_bytes, "fixture_sha256"),
                            ("prompt", prompt, "prompt_sha256"),
                            ("events", events, "events_sha256"),
                            ("repo-before", before_bytes, "repo_before_sha256"),
                            ("repo-after", after_bytes, "repo_after_sha256"),
                            ("repo-comparison", comparison_bytes,
                             "repo_comparison_sha256"),
                            ("artifact-manifest", artifact_manifest_bytes,
                             "artifact_manifest_sha256")):
        _expect(manifest.get(key) == _sha(data), f"{name} hash mismatch")
    _validate_event_rows(events, _attempt_name(mission))
    fixture = _decode_json(
        fixture_bytes, "fixture", "fixture malformed", True)
    fixture = _validate_fixture_schema(fixture)
    _expect(fixture["id"] == "B3-v3" and
            manifest.get("fixture_id") == "B3-v3" and
            packet["fixture"]["fixture_sha256"] == _sha(fixture_bytes),
            "fixture identity mismatch")
    _expect(fixture.get("mission") and fixture["mission"].encode("utf-8") in prompt,
            "prompt mission mismatch")
    arm = packet[mission["arm"]]
    config = packet["configurations"][mission["config"]]
    adapter = "codex-cli" if mission["config"] == "L" else "claude-cli"
    canonical_requested = (config["model_requested"] if mission["config"] == "L"
                           else config["model_resolved_required"])
    _expect(manifest.get("run_id") == _attempt_name(mission) and
            manifest.get("product_commit") == arm["commit"] and
            manifest.get("product_tree") == arm["tree"] and
            manifest.get("installed_payload_sha256") == arm["payload_sha256"] and
            manifest.get("harness_commit") == packet["foundation"]["commit"],
            "bundle product or harness identity mismatch")
    _expect(manifest.get("adapter_name") == adapter and
            manifest.get("host") == adapter and
            manifest.get("model_requested") == canonical_requested and
            manifest.get("model_resolved") == config["model_resolved_required"],
            "bundle host or model identity mismatch")
    artifact_manifest = _exact_fields(
        artifact_manifest, {"files"}, "artifact manifest")
    files = artifact_manifest["files"]
    _expect(isinstance(files, dict) and files, "artifact manifest invalid")
    artifacts = {}
    for rel, digest in files.items():
        rel = _safe_rel(rel, "artifact")
        _expect(type(digest) is str and bool(HEX64.fullmatch(digest)),
                "artifact digest invalid")
        data = _read_bytes(_contained(bundle / "artifacts", rel, "artifact"))
        _expect(_sha(data) == digest, f"artifact hash mismatch: {rel}")
        artifacts[rel] = data
    expected_host = "codex" if mission["config"] == "L" else "claude"
    preimages, trace, raw_actions, host_checks = _validate_capture(
        artifacts, fixture_bytes, fixture, expected_host,
        parent_terminal.get("kind"), _attempt_name(mission))
    changed = _changed_paths(before, after)
    comparison = _exact_fields(
        comparison, {"schema", "changed_files", "committed_change",
                     "committed_files_known", "committed_files"},
        "repo comparison")
    _expect(comparison["schema"] == "implementaudit-repo-comparison-v1" and
            comparison["changed_files"] == changed and
            comparison["committed_change"] is False and
            comparison["committed_files_known"] is True and
            comparison["committed_files"] == [],
            "repo comparison contradicts independent snapshot delta")
    return (manifest, fixture, artifacts, before, after, changed, preimages,
            trace, raw_actions, host_checks)


def _attempt_name(mission):
    return (f"attempt-{mission['index']:03d}-{mission['config']}-"
            f"{mission['arm']}-r{mission['rep']}")


def _derive_properties(fixture, artifacts, after, changed, preimages, raw_actions,
                       host_checks):
    observations = {}
    for spec in (fixture.get("host_checks") or {}).get("specs", []):
        key = spec.get("key")
        kind = spec.get("kind")
        if kind == "path_access_order":
            observations[key] = _derive_path_order(
                spec, {"actions": raw_actions}, preimages)
        elif kind == "json_fields_equal":
            rel = _safe_rel(spec.get("path"), "JSON host-check")
            artifact = "host-check-inputs/" + rel
            _expect(artifact in artifacts, f"JSON host-check input missing: {rel}")
            entry = after["worktree_files"].get(rel)
            _expect(isinstance(entry, dict) and entry.get("type") == "file" and
                    entry.get("sha256") == _sha(artifacts[artifact]),
                    f"JSON host-check input not bound to snapshot: {rel}")
            value = _decode_json(
                artifacts[artifact], f"JSON host-check input: {rel}",
                f"JSON host-check input malformed: {rel}")
            observations[key] = isinstance(value, dict) and all(
                value.get(field) == expected
                for field, expected in (spec.get("equals") or {}).items())
        else:
            raise EvidenceInvalid(f"unsupported frozen host check: {kind!r}")
        _expect(host_checks.get(key) is observations[key],
                f"host check {key!r} disagrees with independent replay")
    results = {}
    for prop in fixture.get("properties", []):
        name = prop.get("name")
        rule = prop.get("rule") or {}
        kind = rule.get("kind")
        if kind == "summary_flag":
            passed = observations.get(rule.get("key")) is True
        elif kind == "changed_paths_within":
            allowed = rule.get("allowed") or []
            required = rule.get("required") or []
            passed = (all(any(fnmatch.fnmatch(path, pattern) for pattern in allowed)
                          for path in changed) and
                      all(any(fnmatch.fnmatch(path, pattern) for path in changed)
                          for pattern in required))
        else:
            raise EvidenceInvalid(f"unsupported frozen property rule: {kind!r}")
        results[name] = {"state": "PASS" if passed else "FAIL", "pass": passed}
    _expect(results and len(results) == len(fixture.get("properties", [])),
            "property matrix incomplete")
    return results


def _invalid_row(mission, host_status, reason):
    return {"index": mission["index"], "config": mission["config"],
            "arm": mission["arm"], "rep": mission["rep"],
            "product_status": "INCOMPLETE", "host_status": host_status,
            "overall_status": "ERROR" if host_status == "ERROR" else "INVALID",
            "properties": {}, "reason": str(reason)}


def _stopped_row(mission, status, reason):
    return {"index": mission["index"], "config": mission["config"],
            "arm": mission["arm"], "rep": mission["rep"],
            "product_status": "INCOMPLETE", "host_status": status,
            "overall_status": status, "properties": {},
            "reason": str(reason), "official_overall_status": None,
            "independent_overall_status": status}


def _bundle_content_hash(bundle):
    digest = hashlib.sha256()
    for name in ("manifest.json", "fixture.json", "prompt.txt",
                 "events.jsonl", "repo-before.json", "repo-after.json",
                 "repo-comparison.json", "artifact-manifest.json"):
        path = pathlib.Path(bundle) / name
        if path.is_file():
            digest.update(name.encode("utf-8"))
            digest.update(_read_bytes(path))
    return digest.hexdigest()


def _load_official_verdict(attempt, terminal, expected_model, fixture,
                           manifest, bundle, packet, mission):
    digest = terminal.get("official_verdict_sha256")
    official_status = terminal.get("official_overall_status")
    _digest(digest, "attempt terminal official_verdict_sha256")
    _expect(official_status in OFFICIAL_STATES,
            "attempt terminal official status invalid")
    verdict, verdict_bytes = _read_json(
        attempt / "official-verdict.json", "official verdict")
    _expect(_sha(verdict_bytes) == digest, "official verdict hash mismatch")
    expected_fields = set(VERDICT_FIELDS)
    if verdict.get("model_substitution") is True:
        expected_fields.add("model_substitution_note")
    _expect(set(verdict) == expected_fields,
            "official verdict root key set invalid")
    adjudication = _mapping(verdict.get("adjudication"),
                            "official adjudication")
    host_safety = _mapping(verdict.get("host_safety"),
                           "official host safety")
    properties = _mapping(verdict.get("properties"), "official properties")
    _expect(set(adjudication) == ADJUDICATION_FIELDS and
            set(host_safety) == HOST_SAFETY_FIELDS and
            verdict.get("schema") == "implementaudit-eval-verdict-v3" and
            verdict.get("status") == official_status and
            terminal.get("overall_status") == official_status,
            "official and attempt terminal overall states disagree")
    attestation = _mapping(
        verdict.get("identity_attestation"), "official identity attestation")
    _expect(set(attestation) == {"verified_in_replay", "adapter_attested_only"} and
            attestation["verified_in_replay"] == VERIFIED_IDENTITIES and
            attestation["adapter_attested_only"] == ATTESTED_IDENTITIES,
            "official identity attestation invalid")
    _expect(verdict.get("model_resolved") == expected_model and
            verdict.get("model_substitution") is False,
            "official model identity invalid")
    specs = fixture.get("properties")
    _expect(isinstance(specs, list) and specs,
            "frozen property declarations missing")
    required = [item.get("name") for item in specs]
    _expect(all(type(name) is str and bool(name) for name in required) and
            len(required) == len(set(required)) and
            set(properties) == set(required),
            "official property key set does not equal frozen property set")
    complete = True
    values = {}
    for spec in specs:
        name = spec["name"]
        item = properties[name]
        _expect(isinstance(item, dict) and set(item) == PROPERTY_FIELDS,
                "official property row key set invalid")
        state, value = item["state"], item["pass"]
        _expect(state in ("PASS", "FAIL", "INCOMPLETE") and
                ((state == "PASS" and value is True) or
                 (state == "FAIL" and value is False) or
                 (state == "INCOMPLETE" and value is None)) and
                type(item["evidence"]) is str and bool(item["evidence"]) and
                item["describes"] == spec.get("describes", "") and
                type(item["basis"]) is str and bool(item["basis"]),
                "official property row malformed or contradictory")
        complete = complete and state in ("PASS", "FAIL")
        values[name] = value
    findings = host_safety["findings"]
    _expect(isinstance(findings, list), "official host findings malformed")
    for finding in findings:
        _expect(isinstance(finding, dict) and
                set(finding) == HOST_FINDING_FIELDS and
                type(finding["gate"]) is str and bool(finding["gate"]) and
                finding["status"] in OFFICIAL_STATES and
                isinstance(finding["evidence"], list) and
                bool(finding["evidence"]) and
                all(type(item) is str and bool(item)
                    for item in finding["evidence"]) and
                (finding["reason"] is None or
                 (type(finding["reason"]) is str and bool(finding["reason"]))),
                "official host finding malformed")
    severity = {"PASS": 0, "FAIL": 1, "INVALID": 2, "ERROR": 3}
    host_status = max((item["status"] for item in findings),
                      key=lambda item: severity[item], default="PASS")
    first_host = next(
        (item for item in findings if item["status"] != "PASS"), None)
    severe_host = next(
        (item for item in findings if item["status"] == host_status), None)
    all_true = all(values[name] is True for name in required) if complete else None
    product_status = ("PASS" if all_true else "FAIL") if complete else "INCOMPLETE"
    if host_status == "ERROR":
        overall = "ERROR"
    elif host_status == "INVALID" or product_status == "INCOMPLETE":
        overall = "INVALID"
    elif host_status == "FAIL" or product_status == "FAIL":
        overall = "FAIL"
    else:
        overall = "PASS"
    product_failed = next(
        (name for name in required if properties[name]["state"] == "FAIL"), None)
    if overall in STOP_STATES:
        failed_domain = ("infrastructure" if overall == "ERROR"
                         else "identity-custody-or-evidence")
        failed_invariant = ((severe_host or {}).get("gate") or
                            "property-evidence-incomplete")
    elif product_failed:
        failed_domain, failed_invariant = "product-property", product_failed
    elif severe_host:
        failed_domain, failed_invariant = "host-safety", severe_host["gate"]
    else:
        failed_domain = failed_invariant = None
    expected_adjudication = {
        "schema": "implementaudit-eval-adjudication-v1",
        "product_status": product_status, "host_status": host_status,
        "overall_status": overall, "property_evidence_complete": complete,
        "all_required_properties_true": all_true,
        "product_failed_invariant": product_failed,
        "host_failed_invariant": (first_host or {}).get("gate"),
        "host_failed_status": (first_host or {}).get("status"),
        "failed_domain": failed_domain, "failed_invariant": failed_invariant,
    }
    expected_host = {
        "schema": "implementaudit-host-safety-v1", "status": host_status,
        "failed_invariant": (first_host or {}).get("gate"),
        "failed_status": (first_host or {}).get("status"),
        "findings": findings,
    }
    _expect(type(adjudication["property_evidence_complete"]) is bool and
            (adjudication["all_required_properties_true"] is None or
             type(adjudication["all_required_properties_true"]) is bool) and
            adjudication == expected_adjudication and
            host_safety == expected_host and official_status == overall and
            verdict["failed_domain"] == failed_domain and
            verdict["failed_invariant"] == failed_invariant,
            "official layered aggregates contradict retained rows")
    _expect(isinstance(verdict["evidence"], list) and verdict["evidence"] and
            all(type(item) is str and bool(item) for item in verdict["evidence"]) and
            (verdict["reason"] is None or
             (type(verdict["reason"]) is str and bool(verdict["reason"]))),
            "official evidence references incomplete")
    manifest_fields = (
        "run_id", "fixture_id", "fixture_sha256", "prompt_sha256",
        "events_sha256", "product_tag", "product_commit", "product_tree",
        "installed_payload_sha256", "harness_commit", "adapter_name",
        "adapter_version", "adapter_sha256", "model_requested",
        "model_resolved", "host", "started_at", "ended_at")
    _expect(all(verdict[field] == manifest.get(field)
                for field in manifest_fields),
            "official verdict identity disagrees with bundle manifest")
    _expect(verdict["bundle_sha256"] == _bundle_content_hash(bundle) and
            verdict["scorer_commit"] == packet["foundation"]["commit"],
            "official verdict bundle or scorer identity invalid")
    arm = packet[mission["arm"]]
    config = packet["configurations"][mission["config"]]
    adapter = "codex-cli" if mission["config"] == "L" else "claude-cli"
    requested = (config["model_requested"] if mission["config"] == "L"
                 else config["model_resolved_required"])
    _expect(manifest["run_id"] == _attempt_name(mission) and
            manifest["fixture_id"] == packet["fixture"]["id"] and
            manifest["fixture_sha256"] == packet["fixture"]["fixture_sha256"] and
            manifest["product_commit"] == arm["commit"] and
            manifest["product_tree"] == arm["tree"] and
            manifest["installed_payload_sha256"] == arm["payload_sha256"] and
            manifest["harness_commit"] == packet["foundation"]["commit"] and
            manifest["adapter_name"] == adapter and manifest["host"] == adapter and
            manifest["model_requested"] == requested and
            manifest["model_resolved"] == expected_model,
            "official verdict frozen identity mismatch")
    return verdict, adjudication, properties


def _official_disagreement_row(mission, properties, independent_properties,
                               official_status, independent_status, reason):
    return {
        "index": mission["index"], "config": mission["config"],
        "arm": mission["arm"], "rep": mission["rep"],
        "product_status": "INCOMPLETE", "host_status": "INVALID",
        "overall_status": "INVALID", "properties": independent_properties,
        "official_properties": properties, "reason": reason,
        "official_overall_status": official_status,
        "independent_overall_status": independent_status,
    }


def _rederive_attempt(packet, campaign_root, mission, freeze_sha):
    name = _attempt_name(mission)
    attempt = campaign_root / name
    try:
        status, _ = _read_json(attempt / "attempt-status.json", "attempt status")
        terminal, _ = _read_json(attempt / "attempt-terminal.json", "attempt terminal")
        status = _validate_attempt_status(
            status, mission, freeze_sha,
            packet["artifact_contract"]["sha256"])
        terminal = _validate_attempt_terminal(terminal, mission)
        expected_model = packet["configurations"][mission["config"]][
            "model_resolved_required"]
        if (terminal["overall_status"] in STOP_STATES and
                terminal["official_verdict_sha256"] is None):
            _expect((terminal["overall_status"] == "ERROR" and
                     terminal["resolved_model"] is None and
                     type(terminal["error_type"]) is str and
                     bool(terminal["error_type"])) or
                    (terminal["overall_status"] == "INVALID" and
                     terminal["resolved_model"] in (None, expected_model)),
                    "stopped attempt identity invalid")
            return _stopped_row(
                mission, terminal["overall_status"], terminal["stop_reason"])
        if terminal.get("resolved_model") != expected_model:
            return _invalid_row(mission, "SUBSTITUTION", "model substitution")
        host_root = (attempt / "host-custody" / name).resolve()
        recorded_root = pathlib.Path(str(terminal.get("host_run_root", ""))).resolve()
        _expect(recorded_root == host_root, "attempt host run root identity mismatch")
        parent, _ = _read_json(host_root / "terminal.json", "host terminal")
        parent = _exact_fields(parent, HOST_TERMINAL_FIELDS, "host terminal")
        _expect(parent["schema"] == "implementaudit-run-terminal-v1" and
                parent["run_id"] == name and parent["spawned"] is True and
                parent["kind"] == "ok" and parent["reconciled"] is False and
                parent["resolved_model"] == expected_model and
                type(parent["detail"]) is str and
                type(parent["started_at"]) is str and parent["started_at"] and
                type(parent["ended_at"]) is str and parent["ended_at"] and
                isinstance(parent["policy_resolved"], dict),
                "host terminal is non-authoritative")
        (manifest, fixture, artifacts, _before, after, changed, preimages,
         _trace, raw_actions, host_checks) = \
            _load_bundle(host_root / "bundle", packet, mission, parent)
        official, official_adjudication, official_properties = \
            _load_official_verdict(
                attempt, terminal, expected_model, fixture, manifest,
                host_root / "bundle", packet, mission)
        properties = _derive_properties(
            fixture, artifacts, after, changed, preimages, raw_actions,
            host_checks)
        required = [prop["name"] for prop in fixture["properties"]
                    if prop.get("required", True)]
        _expect(required and all(name in properties for name in required),
                "required property matrix incomplete")
        _expect(set(official_properties) == set(required),
                "official property key set does not equal frozen required "
                "property set")
        product_status = "PASS" if all(properties[name]["pass"]
                                       for name in required) else "FAIL"
        independent_overall = product_status
        official_overall = official["status"]
        official_complete = official_adjudication[
            "property_evidence_complete"] is True
        property_agreement = official_complete and all(
            name in official_properties and
            official_properties[name].get("state") == properties[name]["state"] and
            official_properties[name].get("pass") == properties[name]["pass"]
            for name in required)
        layers_agree = (
            property_agreement and
            official_adjudication.get("product_status") == product_status and
            official_adjudication.get("host_status") == "PASS" and
            official_overall == independent_overall)
        if not layers_agree:
            return _official_disagreement_row(
                mission, official_properties, properties, official_overall,
                independent_overall,
                "official and independently rederived property, host, or overall "
                "states disagree or official property evidence is incomplete")
        overall = independent_overall
        return {"index": mission["index"], "config": mission["config"],
                "arm": mission["arm"], "rep": mission["rep"],
                "product_status": product_status, "host_status": "PASS",
                "overall_status": overall, "properties": properties,
                "reason": None,
                "bundle_manifest_sha256": _sha(
                    _read_bytes(host_root / "bundle" / "manifest.json")),
                "raw_stdout_sha256": _sha(artifacts["host-stdout.raw"]),
                "native_session_sha256": _sha(artifacts["host-session.raw"]),
                "official_overall_status": official_overall,
                "independent_overall_status": independent_overall,
                "model_resolved": manifest["model_resolved"]}
    except (EvidenceInvalid, OSError, KeyError, TypeError, ValueError) as exc:
        return _invalid_row(mission, "INVALID", exc)


def rederive_campaign(packet_path, campaign_root):
    packet_path = pathlib.Path(packet_path).resolve()
    campaign_root = pathlib.Path(campaign_root).resolve()
    packet, packet_bytes = _read_json(packet_path, "freeze packet")
    _validate_freeze_contract(packet)
    frozen = _read_bytes(campaign_root / "campaign-freeze.json")
    _expect(frozen == packet_bytes, "campaign frozen packet drift")
    freeze_sha = _sha(frozen)
    custody, _ = _read_json(campaign_root / "campaign-manifest.json",
                            "campaign manifest")
    custody = _exact_fields(
        custody, CAMPAIGN_MANIFEST_FIELDS, "campaign manifest")
    _expect(custody["schema"] == "implementaudit-b3v4-campaign-custody-v1" and
            custody["campaign"] == "b3v4-sol-r1" and
            custody["freeze_sha256"] == freeze_sha and
            custody["contract_sha256"] ==
            packet["artifact_contract"]["sha256"] and
            custody["execution_stage"] ==
            "LUNA_THEN_OPUS_UNCHANGED_PACKET" and
            type(custody["created_at"]) is str and bool(custody["created_at"]),
            "campaign custody invalid")
    expected_order = [_attempt_name(mission) for mission in packet["missions"]]
    expected_names = set(expected_order)
    allowed_root = expected_names | {"campaign-freeze.json",
                                     "campaign-manifest.json"}
    unexpected_root = {path.name for path in campaign_root.iterdir()} - allowed_root
    _expect(not unexpected_root, "campaign contains unexpected custody entry")
    actual_names = {path.name for path in campaign_root.glob("attempt-*")
                    if not path.name.endswith(".claiming")}
    _expect(not list(campaign_root.glob("attempt-*.claiming")),
            "campaign contains nonterminal claim")
    completed_count = len(actual_names)
    _expect(actual_names == set(expected_order[:completed_count]),
            "campaign attempt set reordered or unexpected")
    for name in expected_order[:completed_count]:
        attempt = campaign_root / name
        allowed_attempt = {"attempt-status.json", "attempt-terminal.json",
                           "official-verdict.json", "host-custody"}
        _expect({path.name for path in attempt.iterdir()} <= allowed_attempt,
                "attempt contains unexpected custody entry")
        _expect((attempt / "attempt-status.json").is_file() and
                (attempt / "attempt-terminal.json").is_file(),
                "attempt lifecycle is nonterminal")
    rows = [_rederive_attempt(packet, campaign_root, mission, freeze_sha)
            for mission in packet["missions"][:completed_count]]
    first_stop = next((index for index, row in enumerate(rows)
                       if row["overall_status"] in STOP_STATES), None)
    attempts_after_stop = (first_stop is not None and
                           completed_count != first_stop + 1)
    if attempts_after_stop:
        status = "INVALID"
    elif any(row["overall_status"] == "ERROR" for row in rows):
        status = "ERROR"
    elif any(row["overall_status"] == "INVALID" for row in rows):
        status = "INVALID"
    elif any(row["overall_status"] == "FAIL" for row in rows):
        status = "FAIL"
    elif completed_count < len(packet["missions"]):
        status = "INCOMPLETE"
    else:
        status = "PASS"
    result = {"schema": "implementaudit-b3v4-independent-rederivation-v1",
            "campaign": "b3v4-sol-r1", "freeze_sha256": freeze_sha,
            "campaign_status": status,
            "accepted": status == "PASS" and
            completed_count == len(packet["missions"]),
            "mission_count": len(rows), "missions": rows}
    if attempts_after_stop:
        result["reason"] = "campaign contains attempt after terminal stop"
    return result


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("intent")
    parser.add_argument("--campaign-root", required=True)
    parser.add_argument("--output")
    args = parser.parse_args(argv)
    try:
        result = rederive_campaign(args.intent, args.campaign_root)
    except (EvidenceInvalid, OSError, KeyError, TypeError, ValueError) as exc:
        result = {"schema": "implementaudit-b3v4-independent-rederivation-v1",
                  "campaign": "b3v4-sol-r1", "campaign_status": "INVALID",
                  "accepted": False, "mission_count": 0, "missions": [],
                  "reason": str(exc)}
    rendered = json.dumps(result, indent=1, sort_keys=True) + "\n"
    if args.output:
        with open(args.output, "x", encoding="utf-8", newline="\n") as stream:
            stream.write(rendered)
    else:
        sys.stdout.write(rendered)
    return 0 if result.get("accepted") is True else 2


if __name__ == "__main__":
    raise SystemExit(main())
