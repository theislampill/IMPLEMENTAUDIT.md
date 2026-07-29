#!/usr/bin/env python3
"""Independent, fail-closed rederivation of a frozen candidate matrix campaign.

This module intentionally has no dependency on the evaluator's host adapters,
runner, or scoring library. It consumes only retained campaign evidence.
"""
from __future__ import annotations

import argparse
import base64
import decimal
import fnmatch
import hashlib
import json
import math
import os
import pathlib
import re
import shlex
import stat
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


FIXTURE_ORDER = (
    "B0", "B1", "B2", "E1", "E2a", "E2b", "E3", "E4",
    "E5", "E6", "E7", "E8", "E9", "E10",
)
PLAN = tuple(
    {"index": index, "config": "L", "fixture": fixture}
    for index, fixture in enumerate(FIXTURE_ORDER)
)
FREEZE_FIELDS = {
    "schema", "campaign", "state", "artifact_contract", "foundation",
    "fixtures", "artifacts", "candidate", "configuration", "authorization",
    "seed", "cells", "luna_stage", "evidence_profiles",
    "result_composition", "attempt_policy", "acceptance_rule",
    "invalid_error_rule", "stop_conditions", "independent_rederiver",
    "evaluated_surfaces",
}
EVALUATED_SURFACE_ROLES = tuple(sorted((
    "acceptance-rules", "adapter", "artifact-contract",
    "authorization-acknowledgement", "checkout-runtime-topology",
    "evaluator", "evidence-contract", "fixture-inventory",
    "host-attestation", "host-read-contract", "host-runner",
    "independent-rederiver", "launcher", "lifecycle-contract",
    "model-reasoning-host-identity", "native-executable",
    "official-driver", "product-candidate", "prompt-construction-rules",
    "prompt-template", "scorer", "seed-order-repetition-rules",
    "verdict-contract",
) + tuple(f"fixture-{name}" for name in FIXTURE_ORDER)))
EVALUATED_SURFACE_GIT_ROLES = {
    "product-candidate", "official-driver", "host-runner", "scorer",
    "evaluator", "adapter", "independent-rederiver",
}
EVALUATED_SURFACE_EXTERNAL_ROLES = {
    "product-candidate", "authorization-acknowledgement",
    "host-attestation", "launcher", "native-executable",
    "checkout-runtime-topology",
}
CONTRACT_ARTIFACTS = {
    "campaign_freeze", "campaign_manifest", "attempt_status",
    "host_attestation", "official_verdict", "attempt_terminal",
    "host_custody", "official_luna_result", "luna_stage_terminal",
    "independent_rederivation",
}
CAMPAIGN_MANIFEST_FIELDS = {
    "schema", "campaign", "freeze_sha256", "contract_sha256", "created_at",
    "execution_stage",
}
CAMPAIGN_ANDON_FIELDS = {
    "schema", "campaign", "freeze_sha256", "contract_sha256",
    "mission_index", "attempt_name", "execution_mode", "terminal_path",
    "terminal_leaf", "stop_reason", "error_type", "created_at",
}
ATTEMPT_STATUS_FIELDS = {
    "schema", "campaign", "freeze_sha256", "contract_sha256", "mission",
    "state", "execution_mode", "created_at", "host_attestation_binding",
}
HOST_ATTESTATION_BINDING_FIELDS = {
    "path", "sha256", "config", "host", "model_resolved_required",
}
HOST_ATTESTATION_FIELDS = {"id", "shell_dialect", "executables"}
ATTEMPT_TERMINAL_FIELDS = {
    "schema", "campaign", "mission_index", "execution_mode",
    "overall_status", "resolved_model", "host_run_root",
    "official_overall_status", "official_verdict_sha256", "stop_reason",
    "error_type", "completed_at", "completed_attempt_seal",
}
COMPLETED_ATTEMPT_SEAL_FIELDS = {
    "schema", "campaign", "freeze_sha256", "contract_sha256", "mission",
    "execution_mode", "overall_status", "resolved_model", "host_run_root",
    "official_overall_status", "official_verdict_sha256", "stop_reason",
    "error_type", "completed_at", "attempt_name", "attempt_status_sha256",
    "host_attestation_sha256", "host_custody_manifest_sha256",
}
OFFICIAL_LUNA_RESULT_FIELDS = {
    "schema", "campaign", "freeze_sha256", "contract_sha256",
    "execution_mode", "disposition", "luna_stage_accepted",
    "accepted", "cell_count",
    "cells", "luna_identity", "independent_rederivation", "claims",
}
FINAL_CLAIMS = {
    "final_28_of_28": False, "cross_model_qualified": False,
    "release_authorized": False, "tag_authorized": False,
    "publication_authorized": False,
}
INDEPENDENT_PASS_ROW_FIELDS = {
    "index", "config", "fixture", "execution_mode",
    "product_status", "host_status",
    "overall_status", "properties", "reason", "bundle_manifest_sha256",
    "raw_stdout_sha256", "native_session_sha256",
    "official_overall_status", "independent_overall_status",
    "model_resolved", "official_verdict_sha256",
}
MAX_JSON_DEPTH = 512
LUNA_MODEL = "gpt-5.6-luna"
ACCEPTANCE_RULE = (
    "all fourteen canonical Luna candidate fixture cells terminal and PASS; "
    "every retained attempt and result execution mode is exactly production; "
    "independent rederivation agrees; zero INVALID, ERROR, or substitution; "
    "successful Luna stage is INCOMPLETE_PENDING_OPUS with "
    "luna_stage_accepted true and accepted false"
)
INVALID_ERROR_RULE = (
    "FAIL, INVALID, unexplained ERROR, substitution, disagreement, and "
    "custody or identity failure halt the Luna stage"
)
STOP_CONDITIONS = [
    "authentication or quota failure",
    "model substitution",
    "identity or custody mismatch",
    "any FAIL, INVALID, or unexplained ERROR",
    "official and independent disagreement",
    "frozen input drift",
]
REDERIVER_IMPORT_BOUNDARY = [
    "eval.candidate_matrix_campaign", "eval.hosts", "eval.runner",
    "eval.lib.scoring", "eval.adapters", "eval.campaign_lifecycle",
    "eval.b3v4_campaign", "eval.b3v4_rederive", "eval.b3v4_contract",
    "eval.evaluated_surfaces", "eval.provisional_integration",
]
CAPTURE_FILES = (
    "host-read-profile.json", "host-read-preimages.json",
    "host-read-fixture.raw", "host-read-replay-spec.json",
    "host-read-pre-spawn.json", "host-stdout.raw", "host-session.raw",
    "host-tool-trace.json", "host-read-matrix.json",
    "host-read-post-probe.json", "host-read-terminal.json",
)


def _exact_json_equal(left, right):
    """Independent exact comparison for strict retained JSON values."""
    active_observed = set()
    active_expected = set()
    pending = [("compare", left, right, 0)]
    while pending:
        action, observed, expected, depth = pending.pop()
        if action == "leave":
            active_observed.remove(id(observed))
            active_expected.remove(id(expected))
            continue
        if type(observed) is not type(expected):
            return False
        if type(observed) is dict:
            if depth >= MAX_JSON_DEPTH or set(observed) != set(expected):
                return False
            observed_id = id(observed)
            expected_id = id(expected)
            if (observed_id in active_observed or
                    expected_id in active_expected):
                return False
            active_observed.add(observed_id)
            active_expected.add(expected_id)
            pending.append(("leave", observed, expected, depth))
            pending.extend(
                ("compare", observed[key], expected[key], depth + 1)
                for key in reversed(list(observed)))
            continue
        if type(observed) is list:
            if depth >= MAX_JSON_DEPTH or len(observed) != len(expected):
                return False
            observed_id = id(observed)
            expected_id = id(expected)
            if (observed_id in active_observed or
                    expected_id in active_expected):
                return False
            active_observed.add(observed_id)
            active_expected.add(expected_id)
            pending.append(("leave", observed, expected, depth))
            pending.extend(
                ("compare", observed_item, expected_item, depth + 1)
                for observed_item, expected_item in reversed(
                    list(zip(observed, expected))))
            continue
        if type(observed) is float:
            if (not math.isfinite(observed) or not math.isfinite(expected) or
                    observed != expected or
                    (observed == 0.0 and
                     math.copysign(1.0, observed) !=
                     math.copysign(1.0, expected))):
                return False
            continue
        if type(observed) in (str, bool, int) or observed is None:
            if observed != expected:
                return False
            continue
        return False
    return True
HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")
CONTRACT_SHA256 = "5b84c8a05daa2050538a1e11596227e06fec07add852eb318ede3cd3b36a0a08"
OFFICIAL_STATES = frozenset({"PASS", "FAIL", "INVALID", "ERROR"})
CONTINUE_STATES = frozenset({"PASS"})
STOP_STATES = frozenset({"FAIL", "INVALID", "ERROR"})
SCORED_STATES = frozenset({"PASS", "FAIL"})
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
SIMPLE_HOST_CHECK_KINDS = {
    "file_regex", "run_root_exists", "validate_run_root",
}
REPLAY_HOST_CHECK_KINDS = {"json_fields_equal", "path_access_order"}
SUPPORTED_HOST_CHECK_KINDS = (
    SIMPLE_HOST_CHECK_KINDS | REPLAY_HOST_CHECK_KINDS)
AUXILIARY_BUNDLE_ARTIFACTS = {
    "host-stderr.raw", "raw-host-events.jsonl", "derived-transform.json",
}


class EvidenceInvalid(ValueError):
    """Retained evidence cannot support a campaign result."""


_CUSTODY_COMPONENT_CACHE = set()


def _sha(data):
    return hashlib.sha256(data).hexdigest()


def _reparse_point(path_stat):
    return bool(getattr(path_stat, "st_file_attributes", 0) &
                getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400))


def _read_bytes(path):
    """Independently enforce unique-path custody before trusting any bytes."""
    lexical = pathlib.Path(path).absolute()
    try:
        lexical_stat = os.lstat(lexical)
        if lexical.is_symlink() or _reparse_point(lexical_stat):
            raise EvidenceInvalid(
                f"retained evidence link or reparse alias: {lexical.name}")
        current = lexical.parent
        while current.parent != current:
            if current not in _CUSTODY_COMPONENT_CACHE:
                current_stat = os.lstat(current)
                if current.is_symlink() or _reparse_point(current_stat):
                    raise EvidenceInvalid(
                        "retained evidence path-component alias: "
                        f"{lexical.name}")
                _CUSTODY_COMPONENT_CACHE.add(current)
            current = current.parent
        with open(lexical, "rb") as stream:
            opened = os.fstat(stream.fileno())
            if not stat.S_ISREG(opened.st_mode) or opened.st_nlink != 1:
                raise EvidenceInvalid(
                    f"retained evidence hardlink or non-file alias: {lexical.name}")
            return stream.read()
    except EvidenceInvalid:
        raise
    except OSError as exc:
        raise EvidenceInvalid(f"missing evidence: {lexical.name}") from exc


def _custodied_directory_manifest(path, owner):
    """Independently reproduce the canonical recursive custody manifest."""
    directory = pathlib.Path(path).absolute()
    entries = []
    seen_directories = set()
    pending = [(directory, pathlib.PurePosixPath("."))]
    try:
        while pending:
            current, relative = pending.pop()
            current_stat = os.lstat(current)
            if (current.is_symlink() or _reparse_point(current_stat) or
                    not stat.S_ISDIR(current_stat.st_mode)):
                raise EvidenceInvalid(
                    f"{owner} directory identity invalid")
            identity = (current_stat.st_dev, current_stat.st_ino)
            if identity in seen_directories:
                raise EvidenceInvalid(
                    f"{owner} repeated directory identity forbidden")
            seen_directories.add(identity)
            entries.append({
                "path": relative.as_posix(), "kind": "directory"})
            with os.scandir(current) as scanned:
                children = list(scanned)
            for child in reversed(sorted(children, key=lambda row: row.name)):
                if child.name in ("", ".", "..") or "/" in child.name or \
                        "\\" in child.name:
                    raise EvidenceInvalid(f"{owner} entry name invalid")
                child_path = current / child.name
                child_relative = (
                    pathlib.PurePosixPath(child.name)
                    if relative == pathlib.PurePosixPath(".")
                    else relative / child.name)
                child_stat = os.lstat(child_path)
                if child_path.is_symlink() or _reparse_point(child_stat):
                    raise EvidenceInvalid(
                        f"{owner} link or reparse alias forbidden")
                if stat.S_ISDIR(child_stat.st_mode):
                    pending.append((child_path, child_relative))
                    continue
                if (not stat.S_ISREG(child_stat.st_mode) or
                        child_stat.st_nlink != 1):
                    raise EvidenceInvalid(
                        f"{owner} hardlink or special file forbidden")
                payload = _read_bytes(child_path)
                observed = os.lstat(child_path)
                if ((observed.st_dev, observed.st_ino, observed.st_size) !=
                        (child_stat.st_dev, child_stat.st_ino,
                         child_stat.st_size)):
                    raise EvidenceInvalid(f"{owner} file identity changed")
                entries.append({
                    "path": child_relative.as_posix(), "kind": "file",
                    "byte_length": len(payload), "sha256": _sha(payload),
                })
    except EvidenceInvalid:
        raise
    except OSError as exc:
        raise EvidenceInvalid(
            f"{owner} cannot be read as retained evidence") from exc
    entries.sort(key=lambda row: row["path"])
    return (json.dumps({
        "schema": "implementaudit-custodied-directory-manifest-v1",
        "entries": entries,
    }, indent=1, sort_keys=True, allow_nan=False) + "\n").encode("utf-8")


def _validate_strict_json_model(value, owner="JSON value"):
    """Independently enforce the frozen exact-model and depth contract."""
    active = set()
    pending = [("visit", value, owner, 0)]
    while pending:
        action, current, current_owner, depth = pending.pop()
        if action == "leave":
            active.remove(id(current))
            continue
        if type(current) is dict:
            if depth >= MAX_JSON_DEPTH:
                raise EvidenceInvalid(
                    f"{current_owner} exceeds JSON depth limit")
            identity = id(current)
            if identity in active:
                raise EvidenceInvalid(
                    f"{current_owner} contains a cyclic JSON container")
            active.add(identity)
            pending.append(("leave", current, current_owner, depth))
            children = []
            for key, child in current.items():
                if type(key) is not str:
                    raise EvidenceInvalid(
                        f"{current_owner} object key must be an exact string")
                children.append((
                    "visit", child, f"{current_owner}.{key}", depth + 1))
            pending.extend(reversed(children))
            continue
        if isinstance(current, dict):
            raise EvidenceInvalid(
                f"{current_owner} object type must be exact dict")
        if type(current) is list:
            if depth >= MAX_JSON_DEPTH:
                raise EvidenceInvalid(
                    f"{current_owner} exceeds JSON depth limit")
            identity = id(current)
            if identity in active:
                raise EvidenceInvalid(
                    f"{current_owner} contains a cyclic JSON container")
            active.add(identity)
            pending.append(("leave", current, current_owner, depth))
            pending.extend(
                ("visit", child, f"{current_owner}[{index}]", depth + 1)
                for index, child in reversed(list(enumerate(current))))
            continue
        if isinstance(current, (list, tuple)):
            raise EvidenceInvalid(
                f"{current_owner} array type must be exact list")
        if current is None or type(current) in (str, bool, int):
            continue
        if type(current) is float:
            if not math.isfinite(current):
                raise EvidenceInvalid(
                    f"{current_owner} contains a non-finite number")
            continue
        raise EvidenceInvalid(
            f"{current_owner} scalar type is not strict JSON")


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

        def lossless_float(token):
            try:
                source = decimal.Decimal(token)
                value = float(source)
                round_trip = (decimal.Decimal(repr(value))
                              if math.isfinite(value) else None)
                numerically_equal = (
                    round_trip == source if round_trip is not None else False)
            except (decimal.DecimalException, OverflowError, ValueError) as exc:
                raise EvidenceInvalid(
                    f"{owner} contains JSON number domain error: {token}") \
                    from exc
            if not math.isfinite(value):
                raise EvidenceInvalid(
                    f"{owner} contains non-finite number {token}")
            sign_changed = (
                source.is_zero() and
                source.is_signed() != (math.copysign(1.0, value) < 0.0))
            if not numerically_equal or sign_changed:
                raise EvidenceInvalid(
                    f"{owner} contains lossy JSON number {token}")
            return value

        value = json.loads(text, object_pairs_hook=unique,
                           parse_constant=nonfinite,
                           parse_float=lossless_float)
        _validate_strict_json_model(value, owner)
    except EvidenceInvalid:
        raise
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise EvidenceInvalid(malformed) from exc
    except ValueError as exc:
        raise EvidenceInvalid(f"{owner} contains invalid JSON number") from exc
    except (RecursionError, MemoryError) as exc:
        raise EvidenceInvalid(
            f"{owner} exceeds JSON resource limits") from exc
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
    declaration = _exact_fields(
        declaration,
        {"schema", "contract_id", "campaign", "encoding", "execution",
         "artifacts", "lifecycle_schemas"},
        "artifact contract")
    _expect(
        declaration["schema"] ==
        "implementaudit-candidate-matrix-artifact-contract-v1" and
        declaration["contract_id"] ==
        "implementaudit-candidate-matrix-artifact-contract-v1" and
        declaration["campaign"] == "candidate-matrix-sol-luna-r1",
        "artifact contract identity drift")
    encoding = _exact_fields(
        declaration["encoding"],
        {"charset", "duplicate_keys", "non_finite_numbers", "object_keys",
         "scalar_types", "paths", "writes"}, "artifact contract encoding")
    _expect(_exact_json_equal(encoding, {
        "charset": "UTF-8", "duplicate_keys": "REJECT_RECURSIVELY",
        "non_finite_numbers": "REJECT", "object_keys": "EXACT",
        "scalar_types": "EXACT_NO_COERCION",
        "paths": "CANONICAL_ROLE_CONTAINED_NO_LINK_ALIAS",
        "writes": "CREATE_ONCE"}), "artifact contract encoding drift")
    execution = _exact_fields(declaration["execution"], {
        "configuration", "fixture_order", "mission_count", "silent_retry",
        "preserve_every_attempt", "qualifying_execution_mode",
        "test_mode_disposition", "success_disposition",
        "luna_stage_accepted", "final_acceptance",
    }, "artifact contract execution")
    _expect(_exact_json_equal(execution, {
        "configuration": "L", "fixture_order": list(FIXTURE_ORDER),
        "mission_count": 14, "silent_retry": "FORBIDDEN",
        "preserve_every_attempt": True,
        "qualifying_execution_mode": "production",
        "test_mode_disposition": "TEST_ONLY_NON_QUALIFYING",
        "success_disposition": "INCOMPLETE_PENDING_OPUS",
        "luna_stage_accepted": True, "final_acceptance": False}),
        "artifact contract execution drift")
    _expect(
        type(declaration["artifacts"]) is dict and
        set(declaration["artifacts"]) == CONTRACT_ARTIFACTS,
        "artifact contract retained artifact set invalid")
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
        {"campaign_manifest", "campaign_andon", "attempt_status",
         "attempt_terminal", "official_luna_result"},
        "artifact contract lifecycle schemas")
    _expect(set(lifecycle) == {
                "campaign_manifest", "campaign_andon", "attempt_status",
                "attempt_terminal", "official_luna_result"} and
            set(lifecycle["campaign_manifest"]) == CAMPAIGN_MANIFEST_FIELDS and
            set(lifecycle["campaign_andon"]) == CAMPAIGN_ANDON_FIELDS and
            set(lifecycle["attempt_status"]) == ATTEMPT_STATUS_FIELDS and
            set(lifecycle["attempt_terminal"]) == ATTEMPT_TERMINAL_FIELDS and
            set(lifecycle["official_luna_result"]) ==
            OFFICIAL_LUNA_RESULT_FIELDS,
            "artifact contract lifecycle field sets drift")


def _validate_fixture_schema(fixture, expected_id):
    required = {
        "id", "title", "mission", "expected_correct_behavior",
        "planted_defect", "properties",
    }
    optional = {
        "allowed_paths", "artifact_rules", "contract_source", "host_checks",
        "host_observation_spec", "issue_map", "negative_control",
        "required_capabilities",
    }
    fixture = _closed_fields(fixture, required, optional, "fixture")
    _expect(
        fixture["id"] == expected_id and expected_id in FIXTURE_ORDER,
        "fixture identity schema invalid")
    for key in (
            "title", "mission", "expected_correct_behavior",
            "planted_defect"):
        _expect(type(fixture[key]) is str and fixture[key],
                f"fixture.{key} invalid")
    properties = fixture["properties"]
    _expect(type(properties) is list and properties,
            "fixture properties invalid")
    names = []
    for index, prop in enumerate(properties):
        prop = _closed_fields(
            prop, {"name", "required", "rule"}, {"describes"},
            f"fixture property {index}")
        _expect(
            type(prop["name"]) is str and prop["name"] and
            type(prop["required"]) is bool and
            type(prop.get("describes", "")) is str and
            type(prop["rule"]) is dict and prop["rule"] and
            type(prop["rule"].get("kind")) is str and
            prop["rule"]["kind"],
            f"fixture property {index} invalid")
        names.append(prop["name"])
    _expect(len(names) == len(set(names)),
            "fixture property names are not unique")
    for key in ("allowed_paths", "required_capabilities"):
        if key in fixture:
            _strings(fixture[key], f"fixture.{key}")
    if "host_checks" in fixture:
        host_checks = _exact_fields(
            fixture["host_checks"], {"artifact", "specs"},
            "fixture.host_checks")
        _expect(host_checks["artifact"] == "host-checks.json" and
                type(host_checks["specs"]) is list and host_checks["specs"],
                "fixture host checks invalid")
        keys = []
        for index, spec in enumerate(host_checks["specs"]):
            owner = f"fixture host check {index}"
            spec = _mapping(spec, owner)
            kind = spec.get("kind")
            _expect(kind in SUPPORTED_HOST_CHECK_KINDS,
                    owner + " kind unsupported")
            required, optional = {
                "file_regex": (
                    {"key", "kind", "path"},
                    {"must_match", "must_not_match"}),
                "run_root_exists": (
                    {"key", "kind"}, {"dir"}),
                "validate_run_root": (
                    {"key", "kind"}, set()),
                "json_fields_equal": (
                    {"key", "kind", "path", "equals"}, set()),
                "path_access_order": (
                    {"key", "kind", "reads", "write"}, set()),
            }[kind]
            _closed_fields(spec, required, optional, owner)
            _expect(type(spec["key"]) is str and spec["key"],
                    owner + " key invalid")
            keys.append(spec["key"])
        _expect(len(keys) == len(set(keys)),
                "fixture host check keys are not unique")
    return fixture

def _validate_event_rows(data, expected_run_id, expected_fixture):
    rows = _raw_json_lines(data, "bundle events")
    expected_seq = 1
    for _ordinal, row in rows:
        row = _exact_fields(
            row, {"schema", "run_id", "fixture_id", "seq", "role", "kind",
                  "content", "recorded_at"}, "bundle event")
        _expect(row["schema"] == "implementaudit-eval-event-v1" and
                row["run_id"] == expected_run_id and
                row["fixture_id"] == expected_fixture and
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
    candidate = packet["candidate"]
    config_name = "L"
    config = packet["configuration"]
    _expect(
            manifest["payload_source_sha256"] ==
            candidate["payload_sha256"] and
            manifest["reasoning_effort_requested"] ==
            config["reasoning_effort"] and
            manifest["reasoning_effort_resolved"] ==
            config["reasoning_effort"],
            "bundle manifest payload or effort identity invalid")
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
    _expect(_exact_json_equal(
                manifest["policy_requested"], expected_requested),
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
    _expect(_exact_json_equal(root_models, [manifest["model_resolved"]]),
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


def _surface_path(root, value, role):
    _expect(type(value) is str and bool(value) and "\\" not in value and
            "\x00" not in value,
            f"evaluated surface {role} path invalid")
    pure = pathlib.PurePosixPath(value)
    _expect(not any(part in ("", ".", "..") for part in pure.parts),
            f"evaluated surface {role} path invalid")
    path = pathlib.Path(value)
    if path.is_absolute():
        _expect(role in EVALUATED_SURFACE_EXTERNAL_ROLES,
                f"evaluated surface {role} cannot use an external path")
        return path.absolute()
    root = pathlib.Path(root).absolute()
    candidate = (root / pure).absolute()
    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise EvidenceInvalid(
            f"evaluated surface {role} escapes surface root") from exc
    return candidate


def _read_surface(path, owner, root, allow_external):
    path = pathlib.Path(path).absolute()
    root = pathlib.Path(root).absolute()
    try:
        resolved = path.resolve(strict=True)
        if not allow_external:
            resolved.relative_to(root.resolve(strict=True))
        _expect(resolved == path,
                f"{owner} link or reparse alias forbidden")
        current = pathlib.Path(path.anchor)
        for part in path.parts[1:]:
            current = current / part
            observed = os.lstat(current)
            _expect(not stat.S_ISLNK(observed.st_mode) and
                    not _reparse_point(observed),
                    f"{owner} link or reparse alias forbidden")
        before = os.lstat(path)
        _expect(stat.S_ISREG(before.st_mode) and before.st_nlink == 1,
                f"{owner} hardlink or non-file alias forbidden")
        descriptor = os.open(
            path, os.O_RDONLY | getattr(os, "O_BINARY", 0) |
            getattr(os, "O_NOFOLLOW", 0))
        try:
            opened = os.fstat(descriptor)
            _expect(stat.S_ISREG(opened.st_mode) and opened.st_nlink == 1 and
                    (opened.st_dev, opened.st_ino) ==
                    (before.st_dev, before.st_ino),
                    f"{owner} identity changed during custody read")
            digest = hashlib.sha256()
            length = 0
            while True:
                chunk = os.read(descriptor, 1024 * 1024)
                if not chunk:
                    break
                length += len(chunk)
                digest.update(chunk)
            after = os.fstat(descriptor)
            _expect(
                (after.st_dev, after.st_ino, after.st_size,
                 getattr(after, "st_mtime_ns", None)) ==
                (opened.st_dev, opened.st_ino, opened.st_size,
                 getattr(opened, "st_mtime_ns", None)) and
                length == after.st_size,
                f"{owner} identity changed during custody read")
            identities = (
                os.path.normcase(os.path.normpath(str(path))),
                os.path.normcase(os.path.normpath(str(resolved))),
                (opened.st_dev, opened.st_ino),
            )
            return length, digest.hexdigest(), identities
        finally:
            os.close(descriptor)
    except EvidenceInvalid:
        raise
    except (OSError, ValueError) as exc:
        raise EvidenceInvalid(f"{owner} custody read failed") from exc


def _validate_evaluated_surfaces(value, surface_root=None):
    value = _exact_fields(
        value, {"schema", "campaign", "entries"},
        "evaluated surface manifest")
    _expect(
        value["schema"] == "implementaudit-evaluated-surfaces-v1" and
        value["campaign"] == "candidate-matrix-sol-luna-r1" and
        type(value["entries"]) is list,
        "evaluated surface manifest identity invalid")
    roles = []
    paths = []
    identity_owners = {}
    for index, row in enumerate(value["entries"]):
        allowed = {"role", "path", "byte_length", "sha256"}
        if type(row) is dict and (
                "git_commit" in row or "git_tree" in row):
            allowed |= {"git_commit", "git_tree"}
        row = _exact_fields(row, allowed, f"evaluated surface {index}")
        role = row["role"]
        _expect(type(role) is str and role in EVALUATED_SURFACE_ROLES,
                f"evaluated surface {index} role invalid")
        if pathlib.Path(row["path"]).is_absolute():
            _expect(role in EVALUATED_SURFACE_EXTERNAL_ROLES,
                    f"evaluated surface {role} cannot use an external path")
        else:
            _repo_relative(row["path"], f"evaluated surface {role} path")
        _expect(type(row["byte_length"]) is int and
                row["byte_length"] >= 0,
                f"evaluated surface {role} length invalid")
        _digest(row["sha256"], f"evaluated surface {role}.sha256")
        git_fields = {"git_commit", "git_tree"} & set(row)
        _expect(not git_fields or (
            git_fields == {"git_commit", "git_tree"} and
            role in EVALUATED_SURFACE_GIT_ROLES),
            f"evaluated surface {role} Git identity fields invalid")
        if git_fields:
            _git_id(row["git_commit"],
                    f"evaluated surface {role}.git_commit")
            _git_id(row["git_tree"], f"evaluated surface {role}.git_tree")
        roles.append(role)
        paths.append(row["path"])
        if surface_root is not None:
            surface_path = _surface_path(surface_root, row["path"], role)
            length, digest, identities = _read_surface(
                surface_path, f"evaluated surface {role}", surface_root,
                role in EVALUATED_SURFACE_EXTERNAL_ROLES)
            _expect(length == row["byte_length"] and digest == row["sha256"],
                    f"evaluated surface {role} hash or length drift")
            for identity in set(identities):
                _expect(identity not in identity_owners,
                        "evaluated surface physical alias forbidden")
                identity_owners[identity] = role
    _expect(
        roles == list(EVALUATED_SURFACE_ROLES) and
        len(set(roles)) == len(roles),
        "evaluated surface role coverage/order invalid")
    normalized_paths = {
        os.path.normcase(os.path.normpath(path.replace("/", os.sep)))
        for path in paths
    }
    _expect(len(normalized_paths) == len(paths),
            "evaluated surface path alias forbidden")
    return value


def _validate_freeze_contract(packet, surface_root=None):
    """Independently validate every matrix qualification-critical semantic."""
    packet = _exact_fields(packet, FREEZE_FIELDS, "freeze packet")
    _expect(
        packet["schema"] == "implementaudit-candidate-matrix-luna-freeze-v1"
        and packet["campaign"] == "candidate-matrix-sol-luna-r1"
        and packet["state"] == "FROZEN_BEFORE_FIRST_CELL",
        "freeze packet identity invalid")
    _validate_evaluated_surfaces(packet["evaluated_surfaces"], surface_root)

    artifact_contract = _exact_fields(
        packet["artifact_contract"], {"schema", "path", "sha256"},
        "artifact contract identity")
    _expect(
        artifact_contract["schema"] ==
        "implementaudit-candidate-matrix-artifact-contract-v1"
        and artifact_contract["path"] == "eval/candidate_matrix_contract.json",
        "artifact contract identity invalid")
    _digest(artifact_contract["sha256"], "artifact contract sha256")
    _expect(artifact_contract["sha256"] == CONTRACT_SHA256,
            "artifact contract semantic identity drift")
    declaration_path = pathlib.Path(__file__).resolve().parent.parent / \
        pathlib.PurePosixPath(artifact_contract["path"])
    declaration_bytes = _read_bytes(declaration_path)
    _expect(_sha(declaration_bytes) == artifact_contract["sha256"],
            "artifact contract hash mismatch")
    declaration = _decode_json(
        declaration_bytes, "artifact contract",
        "artifact contract is malformed", True)
    _validate_contract_declaration(declaration)

    foundation = _exact_fields(
        packet["foundation"], {"commit", "tree"}, "foundation")
    _git_id(foundation["commit"], "foundation.commit")
    _git_id(foundation["tree"], "foundation.tree")

    fixtures = packet["fixtures"]
    _expect(type(fixtures) is list and len(fixtures) == 14,
            "fixture inventory invalid")
    for index, (identity, fixture_id) in enumerate(
            zip(fixtures, FIXTURE_ORDER)):
        identity = _exact_fields(
            identity, {"id", "path", "sha256", "complete_manifest_sha256"},
            f"fixture {index}")
        _expect(
            identity["id"] == fixture_id and
            identity["path"] ==
            f"eval/fixtures/{fixture_id}/fixture.json",
            "fixture identity or order invalid")
        _digest(identity["sha256"], f"fixture {index}.sha256")
        _digest(identity["complete_manifest_sha256"],
                f"fixture {index}.complete_manifest_sha256")
    _expect(len({row["path"] for row in fixtures}) == 14,
            "fixture path alias forbidden")

    artifacts = _mapping(packet["artifacts"], "artifacts")
    _expect(set(artifacts) == {"scorer", "evaluator", "bundle", "runner"},
            "artifacts identity shape invalid")
    for name, value in artifacts.items():
        value = _exact_fields(value, {"path", "sha256"},
                              f"artifacts.{name}")
        _repo_relative(value["path"], f"artifacts.{name}.path")
        _digest(value["sha256"], f"artifacts.{name}.sha256")
    _expect(len({value["path"] for value in artifacts.values()}) == 4,
            "artifact path alias forbidden")

    candidate = _exact_fields(
        packet["candidate"],
        {"commit", "tree", "skill_tree", "payload_sha256"}, "candidate")
    for key in ("commit", "tree", "skill_tree"):
        _git_id(candidate[key], f"candidate.{key}")
    _digest(candidate["payload_sha256"], "candidate.payload_sha256")

    config = _exact_fields(packet["configuration"], {
        "id", "host", "model_requested", "model_resolved_required",
        "reasoning_effort", "auth_mode", "executable", "host_attestation",
    }, "configuration")
    _expect(
        config["id"] == "L" and config["host"] == "WSL Ubuntu Codex CLI"
        and config["model_requested"] == "gpt-5.6-luna"
        and config["model_resolved_required"] == "gpt-5.6-luna"
        and config["reasoning_effort"] == "max"
        and config["auth_mode"] == "chatgpt-subscription",
        "configuration identity/auth boundary drift")
    executable = _exact_fields(
        config["executable"], {"path", "version", "sha256"},
        "configuration executable")
    _expect(all(type(executable[key]) is str and executable[key]
                for key in ("path", "version")),
            "configuration executable identity incomplete")
    _digest(executable["sha256"], "configuration executable.sha256")
    attestation = _exact_fields(
        config["host_attestation"], {"id", "sha256"},
        "configuration host attestation")
    _expect(type(attestation["id"]) is str and attestation["id"],
            "configuration host attestation id invalid")
    _digest(attestation["sha256"], "configuration host attestation.sha256")

    authorization = _exact_fields(packet["authorization"], {
        "acknowledgement_path", "acknowledgement_sha256",
        "metered_api_spend"}, "authorization")
    _expect(type(authorization["acknowledgement_path"]) is str and
            authorization["acknowledgement_path"],
            "authorization acknowledgement path invalid")
    _digest(authorization["acknowledgement_sha256"],
            "authorization acknowledgement sha256")
    _expect(authorization["metered_api_spend"] == "FORBIDDEN",
            "metered API spending must be forbidden")
    _expect(type(packet["seed"]) is int and packet["seed"] == 20260718,
            "seed drift")

    cells = packet["cells"]
    _expect(type(cells) is list and len(cells) == 14,
            "fixed fourteen-cell order drift")
    for index, (cell, planned) in enumerate(zip(cells, PLAN)):
        cell = _exact_fields(
            cell, {"index", "config", "fixture"}, f"cell {index}")
        _expect(_exact_json_equal(cell, planned),
                "fixed fourteen-cell order drift")

    stage = _exact_fields(packet["luna_stage"], {
        "schema", "name", "cell_count", "terminal_name",
        "official_result_name", "independent_result_name",
        "success_disposition"}, "luna_stage")
    _expect(_exact_json_equal(stage, {
        "schema": "implementaudit-candidate-matrix-luna-stage-v1",
        "name": "LUNA", "cell_count": 14,
        "terminal_name": "luna-stage-terminal.json",
        "official_result_name": "candidate-matrix-luna-result.json",
        "independent_result_name":
            "candidate-matrix-luna-independent-rederivation.json",
        "success_disposition": "INCOMPLETE_PENDING_OPUS",
    }), "luna stage boundary drift")

    _expect(_exact_json_equal(packet["evidence_profiles"], {
        "formal_host_read": "implementaudit-host-read-profile-v2",
        "raw_stdout": "required", "native_session": "required",
        "pre_spawn": "required", "post_cell_manifest": "required",
    }), "evidence profile drift")
    _expect(_exact_json_equal(packet["result_composition"], {
        "product_property_states": ["PASS", "FAIL", "INCOMPLETE"],
        "host_states": ["PASS", "INVALID", "ERROR", "SUBSTITUTION"],
        "overall_states": ["PASS", "FAIL", "INVALID", "ERROR"],
        "luna_stage_dispositions": [
            "INCOMPLETE_PENDING_OPUS", "TEST_ONLY_NON_QUALIFYING"],
    }), "result composition drift")
    _expect(_exact_json_equal(packet["attempt_policy"], {
        "silent_retry": "FORBIDDEN", "preserve_every_attempt": True,
        "maximum_attempts": 14,
    }), "attempt policy drift")
    _expect(packet["acceptance_rule"] == ACCEPTANCE_RULE,
            "acceptance rule drift")
    _expect(packet["invalid_error_rule"] == INVALID_ERROR_RULE,
            "invalid/error rule drift")
    _expect(packet["stop_conditions"] == STOP_CONDITIONS,
            "stop conditions drift")

    rederiver = _exact_fields(packet["independent_rederiver"], {
        "contract_id", "implementation_identity", "must_not_import",
        "input", "output"}, "independent_rederiver")
    _expect(
        rederiver["contract_id"] ==
        "implementaudit-candidate-matrix-luna-rederiver-v1",
        "independent rederiver contract drift")
    identity = _exact_fields(
        rederiver["implementation_identity"], {"path", "sha256"},
        "independent rederiver implementation identity")
    _expect(identity["path"] == "eval/candidate_matrix_rederive.py",
            "independent rederiver path drift")
    _digest(identity["sha256"], "independent rederiver sha256")
    _expect(_EXECUTING_REDERIVER_LOAD_ERROR is None,
            "executing independent rederiver identity unavailable")
    loaded_repo_root = _LOADED_REDERIVER_PATH.parent.parent
    expected_loaded_path = loaded_repo_root.joinpath(
        *identity["path"].split("/")).absolute()
    _expect(_LOADED_REDERIVER_PATH == expected_loaded_path,
            "independent rederiver executing path mismatch")
    _expect(expected_loaded_path.resolve(strict=True) ==
            _EXECUTING_REDERIVER_PATH,
            "independent rederiver canonical path mismatch")
    _expect(not _LOADED_REDERIVER_PATH.is_symlink() and
            _EXECUTING_REDERIVER_LINK_COUNT == 1,
            "independent rederiver path alias forbidden")
    _expect(_sha(_EXECUTING_REDERIVER_BYTES) == identity["sha256"],
            "independent rederiver implementation hash mismatch")
    _expect(rederiver["must_not_import"] == REDERIVER_IMPORT_BOUNDARY,
            "independent rederiver import boundary drift")
    _expect(rederiver["input"] == "retained raw evidence only" and
            rederiver["output"] == "independent Luna matrix result",
            "independent rederiver I/O boundary drift")
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
    root = pathlib.Path(root).absolute()
    lexical = root.joinpath(*relative.split("/"))
    try:
        resolved = lexical.resolve(strict=True)
        resolved.relative_to(root)
        current = root
        for part in relative.split("/"):
            current = current / part
            current_stat = os.lstat(current)
            _expect(not current.is_symlink() and
                    not _reparse_point(current_stat),
                    f"{owner} link alias forbidden")
        _expect(resolved.stat().st_nlink == 1,
                f"{owner} hardlink alias forbidden")
    except (OSError, ValueError) as exc:
        raise EvidenceInvalid(f"{owner} path containment invalid") from exc
    return resolved


def _validate_attempt_status(status, mission, freeze_sha, contract_sha, config):
    status = _exact_fields(status, ATTEMPT_STATUS_FIELDS, "attempt status")
    _expect(status["schema"] ==
            "implementaudit-candidate-matrix-luna-attempt-status-v1" and
            status["campaign"] == "candidate-matrix-sol-luna-r1" and
            status["freeze_sha256"] == freeze_sha and
            status["contract_sha256"] == contract_sha and
            _exact_json_equal(status["mission"], mission) and
            status["state"] == "PREPARED_BEFORE_HOST_SPAWN" and
            status["execution_mode"] in ("production", "test") and
            type(status["created_at"]) is str and bool(status["created_at"]),
            "attempt status identity invalid")
    binding = _exact_fields(status["host_attestation_binding"],
                            HOST_ATTESTATION_BINDING_FIELDS,
                            "attempt status host attestation binding")
    _expect(_exact_json_equal(binding, {
        "path": "host-attestation.json",
        "sha256": config["host_attestation"]["sha256"],
        "config": mission["config"], "host": config["host"],
        "model_resolved_required": config["model_resolved_required"],
    }), "host attestation mission identity invalid")
    return status


def _load_host_attestation(attempt, status, config):
    binding = status["host_attestation_binding"]
    path = _contained(attempt, binding["path"], "host attestation")
    attestation, raw = _read_json(path, "host attestation")
    attestation = _exact_fields(attestation, HOST_ATTESTATION_FIELDS,
                                "host attestation")
    _expect(attestation["id"] == config["host_attestation"]["id"] and
            _sha(raw) == binding["sha256"],
            "host attestation frozen identity or hash invalid")
    _expect(attestation["shell_dialect"] in ("posix", "powershell", "cmd"),
            "host attestation shell dialect invalid")
    executables = attestation["executables"]
    _expect(type(executables) is dict and bool(executables) and
            all(type(name) is str and bool(name) and
                type(identity) is str and bool(identity)
                for name, identity in executables.items()),
            "host attestation executable identities invalid")
    return attestation, raw


def _validate_attempt_terminal(terminal, mission):
    terminal = _exact_fields(
        terminal, ATTEMPT_TERMINAL_FIELDS, "attempt terminal")
    _expect(terminal["schema"] ==
            "implementaudit-candidate-matrix-luna-attempt-terminal-v1" and
            terminal["campaign"] == "candidate-matrix-sol-luna-r1" and
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
    if terminal["overall_status"] in SCORED_STATES:
        _expect(type(terminal["completed_attempt_seal"]) is dict,
                "scored attempt completion seal missing")
    else:
        _expect(terminal["completed_attempt_seal"] is None,
                "non-scored attempt cannot claim completion seal")
    return terminal


def _validate_completed_attempt_seal(attempt, status, status_raw, terminal,
                                     attestation_raw, packet, freeze_sha):
    seal = _exact_fields(
        terminal["completed_attempt_seal"], COMPLETED_ATTEMPT_SEAL_FIELDS,
        "completed attempt seal")
    host_root = (attempt / "host-custody" / attempt.name).absolute()
    expected = {
        "schema": "implementaudit-candidate-matrix-completed-attempt-seal-v1",
        "campaign": packet["campaign"],
        "freeze_sha256": freeze_sha,
        "contract_sha256": packet["artifact_contract"]["sha256"],
        "mission": status["mission"],
        "execution_mode": terminal["execution_mode"],
        "overall_status": terminal["overall_status"],
        "resolved_model": terminal["resolved_model"],
        "host_run_root": str(host_root),
        "official_overall_status": terminal["official_overall_status"],
        "official_verdict_sha256": terminal["official_verdict_sha256"],
        "stop_reason": terminal["stop_reason"],
        "error_type": terminal["error_type"],
        "completed_at": terminal["completed_at"],
        "attempt_name": attempt.name,
        "attempt_status_sha256": _sha(status_raw),
        "host_attestation_sha256": _sha(attestation_raw),
        "host_custody_manifest_sha256": _sha(
            _custodied_directory_manifest(
                attempt / "host-custody", "completed host custody")),
    }
    _expect(_exact_json_equal(seal, expected),
            "completed attempt seal drift")
    return seal


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
        _expect(_exact_json_equal(entry, {"type": "dir"}),
                f"{owner} dir type invalid")
    else:
        _expect(_exact_json_equal(entry, {"type": "special"}),
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


def _relative_candidate_path(observed, preimages):
    if not isinstance(observed, str) or not observed or "\x00" in observed:
        return None
    root = (preimages.get("repo") or {}).get("lexical_root")
    if not isinstance(root, str) or not root:
        return None
    root = str(pathlib.PurePosixPath(root.replace("\\", "/")))
    value = observed.replace("\\", "/")
    absolute = value.startswith("/") or bool(re.match(r"^[A-Za-z]:/", value))
    if absolute:
        value = str(pathlib.PurePosixPath(value))
        case_sensitive = (
            (preimages.get("repo") or {}).get("case_sensitive") is not False)
        left = value if case_sensitive else value.lower()
        prefix = root if case_sensitive else root.lower()
        if not left.startswith(prefix.rstrip("/") + "/"):
            return None
        value = value[len(root.rstrip("/")) + 1:]
    elif value.startswith("./"):
        value = value[2:]
    parts = pathlib.PurePosixPath(value).parts
    if not parts or any(part in ("", ".", "..") for part in parts):
        return None
    return "/".join(parts)


def _validate_write_boundary(raw_actions, fixture, preimages):
    writes = [action for action in raw_actions if action.get("effect") == "write"]
    _expect(all(_write_paths(action) for action in writes),
            "formal-v2 raw write action has no bound path")
    write_paths = [
        path for action in writes for path in _write_paths(action)]
    allowed = fixture.get("allowed_paths", [])
    _expect(type(allowed) is list and
            all(type(pattern) is str and pattern and
                not pattern.startswith(("/", "\\")) and
                not re.match(r"^[A-Za-z]:[/\\]", pattern) and
                ".." not in pathlib.PurePosixPath(
                    pattern.replace("\\", "/")).parts
                for pattern in allowed),
            "fixture allowed-write boundary malformed")
    case_sensitive = (
        (preimages.get("repo") or {}).get("case_sensitive") is not False)
    for observed in write_paths:
        relative = _relative_candidate_path(observed, preimages)
        _expect(relative is not None,
                "formal-v2 raw stream exceeds the fixture write boundary")
        candidate = relative if case_sensitive else relative.lower()
        patterns = [
            pattern.replace("\\", "/")
            if case_sensitive else pattern.replace("\\", "/").lower()
            for pattern in allowed]
        _expect(any(fnmatch.fnmatchcase(candidate, pattern)
                    for pattern in patterns),
                "formal-v2 raw stream exceeds the fixture write boundary")


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
                        "Claude raw unsupported tool in candidate matrix evidence")
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
                _exact_json_equal(
                    wrapper, {"argv_prefix": ["/bin/bash", "-lc"],
                              "max_unwrap_layers": 1}) and
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
        _expect(_exact_json_equal(post, probe) and profile["probe_sha256"] == _sha(
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
        _expect(_exact_json_equal(
                    post, {"native_tools": profile["native_tools"]}) and
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
                _exact_json_equal(binding, stdout_binding),
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
            trace["host_status"] == "PASS" and
            _exact_json_equal(trace["host_findings"], []) and
            (expected_host != "claude" or trace["crashed"] is False) and
            _exact_json_equal(trace["observed_tools"], observed_tools) and
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
            _expect(_exact_json_equal(item.get(key), action.get(key)),
                    "formal-v2 raw/trace action disagreement")
        for key in ("action_type", "command", "path", "paths"):
            if key in action:
                _expect(_exact_json_equal(item.get(key), action[key]),
                        "formal-v2 raw/trace payload disagreement")
    projected = [item for item in trace["actions"]
                 if not str(item.get("id", "")).startswith("invalid@")]
    _expect(_exact_json_equal(
                trace["action_states"],
                [item["state"] for item in projected]) and
            _exact_json_equal(
                trace["action_effects"],
                [item["effect"] for item in projected]),
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
    _expect(isinstance(replay["checks"], list),
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


def _validate_parent_custody_objects(
        intent, process, expected_run_id, expected_fixture_id):
    intent = _exact_fields(intent, RUN_INTENT_FIELDS, "run intent")
    _expect(intent["schema"] == "implementaudit-run-intent-v1" and
            intent["run_id"] == expected_run_id and
            intent["fixture_id"] == expected_fixture_id and
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


def _required_capture_files(fixture):
    required = set(CAPTURE_FILES) | {"host-read-manifest.json",
                                     "run-intent.json", "process-started.json",
                                     } | AUXILIARY_BUNDLE_ARTIFACTS
    if fixture.get("host_checks"):
        required.add("host-checks.json")
    for spec in (fixture.get("host_checks") or {}).get("specs", []):
        if spec.get("kind") == "json_fields_equal":
            path = _safe_rel(spec.get("path"), "host-check input")
            required.add("host-check-inputs/" + path)
    artifact_policy = fixture.get("artifact_rules")
    if artifact_policy is not None:
        artifact_path = _safe_rel(
            artifact_policy.get("file"), "required host-observation artifact")
        required.add(artifact_path)
    return required


def _validate_simple_host_checks(specs, artifact):
    _expect(isinstance(artifact, dict),
            "formal-v2 host check aggregate malformed")
    declared = {spec["key"]: spec for spec in specs}
    _expect(set(artifact) == set(declared) | {"_detail"},
            "formal-v2 host check aggregate malformed")
    detail = artifact["_detail"]
    _expect(isinstance(detail, dict) and set(detail) <= set(declared) and
            all(type(value) is str and bool(value) for value in detail.values()),
            "formal-v2 host check detail malformed")
    results = {}
    for key, spec in declared.items():
        value = artifact[key]
        _expect(type(value) is bool,
                "formal-v2 host check aggregate malformed")
        kind = spec["kind"]
        explanation = detail.get(key)
        if kind == "file_regex":
            _expect(explanation is None or
                    (value is False and explanation == "file unreadable"),
                    "formal-v2 file-regex detail contradicts aggregate")
        elif kind == "run_root_exists":
            _expect(explanation is not None and
                    ((value is False and
                      explanation == "no run root on disk") or
                     (value is True and
                      explanation != "no run root on disk")),
                    "formal-v2 run-root detail contradicts aggregate")
        elif kind == "validate_run_root":
            _expect(explanation is not None and
                    (("exit 0" in explanation) is value),
                    "formal-v2 validation detail contradicts aggregate")
        elif kind == "json_fields_equal":
            failure_detail = (
                explanation == "JSON root is not an object" or
                (type(explanation) is str and
                 ((explanation.startswith("JSON unreadable: ") and
                   bool(explanation.removeprefix("JSON unreadable: "))) or
                  (explanation.startswith("mismatched fields: ") and
                   bool(explanation.removeprefix("mismatched fields: "))))))
            _expect((value is True and explanation is None) or
                    (value is False and failure_detail),
                    "formal-v2 JSON-check detail contradicts aggregate")
        elif kind == "path_access_order":
            _expect(explanation is not None,
                    "formal-v2 path-order detail missing")
            row = _decode_json(
                explanation.encode("utf-8"), f"host check detail {key}",
                "formal-v2 path-order detail malformed", True)
            _expect(
                set(row) == {"property_status", "host_status",
                             "overall_status", "ordered", "write_completed",
                             "live_preimage", "ordering_source"} and
                row["property_status"] in ("PASS", "INCOMPLETE") and
                row["host_status"] == "PASS" and
                row["overall_status"] == row["property_status"] and
                type(row["ordered"]) is bool and
                type(row["write_completed"]) is bool and
                type(row["live_preimage"]) is bool and
                row["ordering_source"] == "persisted-ordinal" and
                value is (row["property_status"] == "PASS"),
                "formal-v2 path-order detail contradicts aggregate")
        else:
            raise EvidenceInvalid("unsupported host-check kind")
        results[key] = value
    return results


def _validate_capture(artifacts, fixture_bytes, fixture, expected_host,
                      parent_kind, expected_run_id):
    required = _required_capture_files(fixture)
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
    _expect(_exact_json_equal(manifest["files"], actual),
            "formal-v2 manifest hash mismatch")
    terminal = objects["host-read-terminal.json"]
    _expect(set(terminal) == {"schema", "hashes", "post_probe_sha256",
                              "profile_post_status", "binding", "actual_tools",
                              "normalized_host_status", "host_terminal_kind",
                              "session_bound", "session_status"} and
            terminal.get("schema") == "implementaudit-host-read-terminal-v1" and
            _exact_json_equal(
                terminal.get("hashes"),
                {name: actual[name] for name in CAPTURE_FILES[:-1]}),
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
            _exact_json_equal(
                {key: pre_spawn.get(key) for key in expected_pre},
                expected_pre),
            "formal-v2 pre-spawn custody invalid")
    _expect(artifacts["host-read-fixture.raw"] == fixture_bytes,
            "formal-v2 fixture bytes drift")
    intent = objects["run-intent.json"]
    replay = objects["host-read-replay-spec.json"]
    process = objects["process-started.json"]
    _validate_replay_schema(replay)
    _validate_parent_custody_objects(
        intent, process, expected_run_id, fixture["id"])
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
            _exact_json_equal(replay.get("checks"), expected_checks) and
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
    _validate_write_boundary(
        raw_actions, fixture, objects["host-read-preimages.json"])
    _validate_trace_agreement(trace, raw_actions, observed_tools, expected_host)
    _validate_native_session(
        artifacts["host-stdout.raw"], artifacts["host-session.raw"],
        expected_host, terminal["binding"], stdout_binding, raw_actions,
        profile, process)
    _expect(_exact_json_equal(terminal["actual_tools"], observed_tools),
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
    _expect(_exact_json_equal(matrix, expected_matrix),
            "formal-v2 matrix does not independently regenerate")
    check_specs = (fixture.get("host_checks") or {}).get("specs", [])
    host_checks = (_validate_simple_host_checks(
        check_specs, objects["host-checks.json"]) if check_specs else {})
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
    _validate_event_rows(events, _attempt_name(mission), mission["fixture"])
    fixture = _decode_json(
        fixture_bytes, "fixture", "fixture malformed", True)
    fixture = _validate_fixture_schema(fixture, mission["fixture"])
    fixture_identity = next(
        row for row in packet["fixtures"]
        if row["id"] == mission["fixture"])
    _expect(
            manifest.get("fixture_id") == mission["fixture"] and
            fixture_identity["sha256"] == _sha(fixture_bytes),
            "fixture identity mismatch")
    _expect(fixture.get("mission") and fixture["mission"].encode("utf-8") in prompt,
            "prompt mission mismatch")
    candidate = packet["candidate"]
    config = packet["configuration"]
    adapter = "codex-cli"
    canonical_requested = config["model_requested"]
    _expect(manifest.get("run_id") == _attempt_name(mission) and
            manifest.get("product_commit") == candidate["commit"] and
            manifest.get("product_tree") == candidate["tree"] and
            manifest.get("installed_payload_sha256") ==
            candidate["payload_sha256"] and
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
            _exact_json_equal(comparison["changed_files"], changed) and
            comparison["committed_change"] is False and
            comparison["committed_files_known"] is True and
            _exact_json_equal(comparison["committed_files"], []),
            "repo comparison contradicts independent snapshot delta")
    return (manifest, fixture, artifacts, before, after, changed, preimages,
            trace, raw_actions, host_checks, _role_texts(events))


def _attempt_name(mission):
    return (f"attempt-{mission['index']:03d}-L-"
            f"{mission['fixture']}")


_ROLE_LINE = re.compile(
    r"^\s*(user|assistant|tool|system)\s*:\s", re.IGNORECASE)
_QUOTED_SENTINEL = re.compile(
    r"-{3,}\s*BEGIN QUOTED TRANSCRIPT", re.IGNORECASE)


def _clean_event_content(content):
    output = []
    in_fence = False
    for line in content.splitlines():
        if _QUOTED_SENTINEL.search(line):
            break
        stripped = line.lstrip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence or stripped.startswith(">") or _ROLE_LINE.match(line):
            continue
        if stripped.startswith("{") and stripped.endswith("}"):
            try:
                value = json.loads(stripped)
            except json.JSONDecodeError:
                value = None
            if isinstance(value, dict) and "role" in value:
                continue
        output.append(line)
    return "\n".join(output)


def _role_texts(events):
    texts = {}
    for _ordinal, event in _raw_json_lines(events, "bundle events"):
        if event.get("kind") not in ("message", "marker"):
            continue
        texts.setdefault(event["role"], []).append(
            _clean_event_content(event["content"]))
    return {role: "\n".join(parts) for role, parts in texts.items()}


def _marker_hits(lines, name, payload):
    hits = []
    for index, line in enumerate(lines):
        stripped = line.strip(" \t")
        if not stripped.startswith(name):
            continue
        remainder = stripped[len(name):]
        if remainder == "":
            if payload != "required":
                hits.append(index)
        elif remainder[0] in (":", " ") and remainder.strip():
            if payload == "none":
                continue
            if any(ord(char) == 0xA0 or
                   (ord(char) < 32 and char != "\t")
                   for char in remainder):
                continue
            hits.append(index)
    return hits


def _eval_rule(rule, texts, summary):
    kind = rule.get("kind")
    if kind == "no_diff":
        changed = summary.get("changed_files", [])
        hits = [
            path for path in changed
            if any(fnmatch.fnmatch(path, glob) for glob in rule["paths"])]
        return not hits
    if kind == "changed_paths_within":
        changed = [str(path).replace("\\", "/")
                   for path in summary.get("changed_files", [])]
        allowed = [str(glob).replace("\\", "/")
                   for glob in rule.get("allowed", [])]
        required = [str(glob).replace("\\", "/")
                    for glob in rule.get("required", [])]
        return (
            all(any(fnmatch.fnmatch(path, glob) for glob in allowed)
                for path in changed) and
            all(any(fnmatch.fnmatch(path, glob) for path in changed)
                for glob in required))
    if kind == "summary_flag":
        observed = summary.get(rule["key"])
        return None if observed is None else observed is True
    if kind in ("all_of", "any_of"):
        states = [_eval_rule(child, texts, summary)
                  for child in rule["rules"]]
        if kind == "all_of":
            return False if False in states else None if None in states else True
        return True if True in states else None if None in states else False
    text = texts.get(rule.get("role", "assistant"), "")
    search = lambda pattern: re.search(
        pattern, text, re.IGNORECASE | re.MULTILINE)
    if kind == "contains":
        return bool(search(rule["pattern"]))
    if kind == "absent":
        return search(rule["pattern"]) is None
    if kind == "order":
        first, then = search(rule["first"]), search(rule["then"])
        return bool(first and then and first.start() < then.start())
    if kind == "before_marker":
        pattern, marker = search(rule["pattern"]), search(rule["marker"])
        return bool(pattern) and (
            marker is None or pattern.start() < marker.start())
    if kind in ("count_at_least", "count_exactly"):
        count = len(re.findall(
            rule["pattern"], text, re.IGNORECASE | re.MULTILINE))
        return count >= rule["n"] if kind == "count_at_least" \
            else count == rule["n"]
    if kind == "count_distinct_at_least":
        matches = re.findall(
            rule["pattern"], text, re.IGNORECASE | re.MULTILINE)
        distinct = {
            item.lower() if isinstance(item, str)
            else str(item).lower() for item in matches}
        return len(distinct) >= rule["n"]
    if kind == "path_changed":
        return any(re.search(
            rule["pattern"], path.replace("\\", "/"))
            for path in summary.get("changed_files", []))
    if kind == "marker":
        hits = _marker_hits(
            text.splitlines(), rule["name"], rule.get("payload", "optional"))
        maximum = rule.get("max_count", 1)
        valid = len(hits) == maximum if maximum else bool(hits)
        after = rule.get("order_after")
        if valid and after:
            earlier = _marker_hits(text.splitlines(), after, "optional")
            valid = bool(earlier) and min(earlier) < min(hits)
        return valid
    raise EvidenceInvalid(f"unsupported frozen property rule: {kind!r}")


def _artifact_derivation(fixture, artifacts, property_name):
    policy = fixture.get("artifact_rules")
    if not isinstance(policy, dict):
        return None
    path = policy.get("file")
    _expect(type(path) is str and path in artifacts,
            "required host-observation artifact missing")
    artifact = _decode_json(
        artifacts[path], "host-observation artifact",
        "host-observation artifact malformed", True)
    spec = (policy.get("derive") or {}).get(property_name)
    if spec is None:
        return None
    truth = policy.get("ground_truth") or {}

    def accepted(field):
        value = artifact.get(field)
        _expect(value in ("accept", "reject"),
                "host-observation verdict invalid")
        return value == "accept"

    if spec["kind"] == "verdict_matches_truth":
        observed = accepted(spec["verdict_field"])
        expected = bool(truth[spec["truth_field"]])
        return observed == expected and \
            expected == bool(spec.get("and_truth_is", expected))
    if spec["kind"] == "rule_misjudged_any":
        return any(
            accepted(verdict_field) != bool(truth[truth_field])
            for verdict_field, truth_field in spec["pairs"])
    raise EvidenceInvalid("unsupported host-observation derivation")


def _derive_properties(fixture, artifacts, after, changed, preimages, raw_actions,
                       host_checks, texts):
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
        elif kind in SIMPLE_HOST_CHECK_KINDS:
            observations[key] = host_checks.get(key)
        else:
            raise EvidenceInvalid("unsupported host-check kind")
        _expect(host_checks.get(key) is observations[key],
                f"host check {key!r} disagrees with independent replay")
    summary = {"changed_files": changed, **observations}
    results = {}
    for prop in fixture.get("properties", []):
        name = prop.get("name")
        passed = _eval_rule(prop.get("rule") or {}, texts, summary)
        derived = _artifact_derivation(fixture, artifacts, name)
        if derived is not None:
            passed = None if passed is None else passed and derived
        results[name] = {
            "state": "INCOMPLETE" if passed is None
            else "PASS" if passed else "FAIL",
            "pass": passed,
        }
    _expect(results and len(results) == len(fixture.get("properties", [])),
            "property matrix incomplete")
    return results


def _invalid_row(mission, host_status, reason, execution_mode=None):
    return {"index": mission["index"], "config": mission["config"],
            "fixture": mission["fixture"],
            "execution_mode": execution_mode,
            "product_status": "INCOMPLETE", "host_status": host_status,
            "overall_status": "ERROR" if host_status == "ERROR" else "INVALID",
            "properties": {}, "reason": str(reason)}


def _stopped_row(mission, status, reason, execution_mode):
    return {"index": mission["index"], "config": mission["config"],
            "fixture": mission["fixture"],
            "execution_mode": execution_mode,
            "product_status": "INCOMPLETE", "host_status": status,
            "overall_status": status, "properties": {},
            "reason": str(reason), "official_overall_status": None,
            "independent_overall_status": status}


def _terminal_leaf_observation(path):
    path = pathlib.Path(path)
    if not os.path.lexists(path):
        return {"state": "absent", "byte_length": None, "sha256": None}
    try:
        raw = _read_bytes(path)
    except (EvidenceInvalid, OSError, ValueError):
        return {"state": "unreadable", "byte_length": None, "sha256": None}
    return {
        "state": "nonconforming", "byte_length": len(raw),
        "sha256": _sha(raw),
    }


def _validate_campaign_andon(marker, packet, campaign_root, freeze_sha):
    marker = _exact_fields(
        marker, CAMPAIGN_ANDON_FIELDS, "campaign ANDON")
    _expect(
        marker["schema"] ==
        "implementaudit-candidate-matrix-campaign-andon-v1" and
        marker["campaign"] == packet["campaign"] and
        marker["freeze_sha256"] == freeze_sha and
        marker["contract_sha256"] ==
        packet["artifact_contract"]["sha256"] and
        type(marker["mission_index"]) is int and
        0 <= marker["mission_index"] < len(packet["cells"]) and
        marker["execution_mode"] in ("production", "test") and
        marker["stop_reason"] ==
        "attempt-terminal-publication-failure" and
        type(marker["error_type"]) is str and bool(marker["error_type"]) and
        type(marker["created_at"]) is str and bool(marker["created_at"]),
        "campaign ANDON identity invalid")
    mission = packet["cells"][marker["mission_index"]]
    attempt_name = _attempt_name(mission)
    _expect(
        marker["attempt_name"] == attempt_name and
        marker["terminal_path"] ==
        f"{attempt_name}/attempt-terminal.json",
        "campaign ANDON attempt identity invalid")
    leaf = _exact_fields(
        marker["terminal_leaf"], {"state", "byte_length", "sha256"},
        "campaign ANDON terminal leaf")
    _expect(
        leaf["state"] in ("absent", "nonconforming", "unreadable"),
        "campaign ANDON terminal leaf state invalid")
    if leaf["state"] == "nonconforming":
        _expect(
            type(leaf["byte_length"]) is int and
            leaf["byte_length"] >= 0 and
            type(leaf["sha256"]) is str and HEX64.fullmatch(leaf["sha256"]),
            "campaign ANDON terminal leaf binding invalid")
    else:
        _expect(
            leaf["byte_length"] is None and leaf["sha256"] is None,
            "campaign ANDON terminal leaf null binding invalid")
    _expect(
        _exact_json_equal(
            leaf, _terminal_leaf_observation(
                campaign_root / marker["terminal_path"])),
        "campaign ANDON terminal leaf drift")
    status, _ = _read_json(
        campaign_root / attempt_name / "attempt-status.json",
        "campaign ANDON attempt status")
    status = _validate_attempt_status(
        status, mission, freeze_sha,
        packet["artifact_contract"]["sha256"], packet["configuration"])
    _expect(
        status["execution_mode"] == marker["execution_mode"],
        "campaign ANDON execution mode drift")
    return marker, mission


def _andon_result(packet, freeze_sha, rows, reason):
    observed_modes = {row.get("execution_mode") for row in rows}
    exact_mode = next(iter(observed_modes)) \
        if len(observed_modes) == 1 and \
        observed_modes <= {"production", "test"} else None
    return {
        "schema":
            "implementaudit-candidate-matrix-luna-independent-rederivation-v1",
        "campaign": "candidate-matrix-sol-luna-r1",
        "freeze_sha256": freeze_sha,
        "contract_sha256": packet["artifact_contract"]["sha256"],
        "execution_mode": exact_mode,
        "luna_stage_status": "ERROR",
        "disposition": "ANDON_STOPPED",
        "luna_stage_accepted": False,
        "accepted": False,
        "cell_count": len(rows),
        "cells": rows,
        "claims": dict(FINAL_CLAIMS),
        "reason": reason,
    }


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
    declared = [item.get("name") for item in specs]
    required = [item.get("name") for item in specs
                if item.get("required", True)]
    _expect(all(type(name) is str and bool(name) for name in declared) and
            len(declared) == len(set(declared)) and required and
            set(properties) == set(declared),
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
        if name in required:
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
    candidate = packet["candidate"]
    config = packet["configuration"]
    adapter = "codex-cli"
    requested = config["model_requested"]
    fixture_identity = next(
        row for row in packet["fixtures"]
        if row["id"] == mission["fixture"])
    _expect(manifest["run_id"] == _attempt_name(mission) and
            manifest["fixture_id"] == mission["fixture"] and
            manifest["fixture_sha256"] == fixture_identity["sha256"] and
            manifest["product_commit"] == candidate["commit"] and
            manifest["product_tree"] == candidate["tree"] and
            manifest["installed_payload_sha256"] ==
            candidate["payload_sha256"] and
            manifest["harness_commit"] == packet["foundation"]["commit"] and
            manifest["adapter_name"] == adapter and manifest["host"] == adapter and
            manifest["model_requested"] == requested and
            manifest["model_resolved"] == expected_model,
            "official verdict frozen identity mismatch")
    return verdict, adjudication, properties


def _official_disagreement_row(mission, properties, independent_properties,
                               official_status, independent_status, reason,
                               execution_mode):
    return {
        "index": mission["index"], "config": mission["config"],
        "fixture": mission["fixture"],
        "execution_mode": execution_mode,
        "product_status": "INCOMPLETE", "host_status": "INVALID",
        "overall_status": "INVALID", "properties": independent_properties,
        "official_properties": properties, "reason": reason,
        "official_overall_status": official_status,
        "independent_overall_status": independent_status,
    }


def _rederive_attempt(packet, campaign_root, mission, freeze_sha,
                      property_declarations):
    name = _attempt_name(mission)
    attempt = campaign_root / name
    execution_mode = None
    try:
        status, status_raw = _read_json(
            attempt / "attempt-status.json", "attempt status")
        terminal, _ = _read_json(attempt / "attempt-terminal.json", "attempt terminal")
        config = packet["configuration"]
        status = _validate_attempt_status(
            status, mission, freeze_sha,
            packet["artifact_contract"]["sha256"], config)
        _, attestation_raw = _load_host_attestation(attempt, status, config)
        terminal = _validate_attempt_terminal(terminal, mission)
        execution_mode = status["execution_mode"]
        _expect(
            terminal["execution_mode"] == execution_mode,
            "attempt status and terminal execution modes disagree")
        expected_model = config["model_resolved_required"]
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
                mission, terminal["overall_status"], terminal["stop_reason"],
                execution_mode)
        if terminal.get("resolved_model") != expected_model:
            return _invalid_row(
                mission, "SUBSTITUTION", "model substitution",
                execution_mode=execution_mode)
        host_root = (attempt / "host-custody" / name).absolute()
        _expect(terminal.get("host_run_root") == str(host_root),
                "attempt host run root identity mismatch")
        _validate_completed_attempt_seal(
            attempt, status, status_raw, terminal, attestation_raw,
            packet, freeze_sha)
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
         _trace, raw_actions, host_checks, texts) = \
            _load_bundle(host_root / "bundle", packet, mission, parent)
        property_declarations[mission["index"]] = {
            prop["name"]: prop["required"]
            for prop in fixture["properties"]
        }
        official, official_adjudication, official_properties = \
            _load_official_verdict(
                attempt, terminal, expected_model, fixture, manifest,
                host_root / "bundle", packet, mission)
        properties = _derive_properties(
            fixture, artifacts, after, changed, preimages, raw_actions,
            host_checks, texts)
        declared = [prop["name"] for prop in fixture["properties"]]
        required = [prop["name"] for prop in fixture["properties"]
                    if prop.get("required", True)]
        _expect(required and all(name in properties for name in required),
                "required property matrix incomplete")
        _expect(set(official_properties) == set(declared),
                "official property key set does not equal frozen declared "
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
            for name in declared)
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
                "states disagree or official property evidence is incomplete",
                execution_mode)
        overall = independent_overall
        return {"index": mission["index"], "config": mission["config"],
                "fixture": mission["fixture"],
                "execution_mode": execution_mode,
                "product_status": product_status, "host_status": "PASS",
                "overall_status": overall, "properties": properties,
                "reason": None,
                "bundle_manifest_sha256": _sha(
                    _read_bytes(host_root / "bundle" / "manifest.json")),
                "raw_stdout_sha256": _sha(artifacts["host-stdout.raw"]),
                "native_session_sha256": _sha(artifacts["host-session.raw"]),
                "official_overall_status": official_overall,
                "independent_overall_status": independent_overall,
                "model_resolved": manifest["model_resolved"],
                "official_verdict_sha256":
                    terminal["official_verdict_sha256"]}
    except (EvidenceInvalid, OSError, KeyError, TypeError, ValueError) as exc:
        return _invalid_row(
            mission, "INVALID", exc, execution_mode=execution_mode)


def _validate_stage_pass_rows(rows, property_declarations, expected_model):
    _expect(type(rows) is list and len(rows) == len(PLAN) and
            type(property_declarations) is dict and
            set(property_declarations) == set(range(len(PLAN))),
            "independent PASS property declarations incomplete")
    _expect(expected_model == LUNA_MODEL,
            "independent PASS stage model identity invalid")
    for index, (row, expected) in enumerate(zip(rows, PLAN)):
        _exact_fields(
            row, INDEPENDENT_PASS_ROW_FIELDS,
            f"independent PASS cell row {index}")
        _expect(type(row["index"]) is int and row["index"] == index and
                row["config"] == expected["config"] and
                row["fixture"] == expected["fixture"] and
                row["execution_mode"] == "production" and
                row["product_status"] == "PASS" and
                row["host_status"] == "PASS" and
                row["overall_status"] == "PASS" and
                row["official_overall_status"] == "PASS" and
                row["independent_overall_status"] == "PASS" and
                row["model_resolved"] == expected_model and
                row["reason"] is None and
                type(row["properties"]) is dict and
                bool(row["properties"]),
                f"independent PASS cell row {index} invalid")
        declaration = property_declarations[index]
        _expect(type(declaration) is dict and declaration and
                all(type(name) is str and bool(name) and
                    type(required) is bool
                    for name, required in declaration.items()) and
                set(row["properties"]) == set(declaration),
                f"independent PASS cell row {index} property set invalid")
        for name, required in declaration.items():
            property_row = _exact_fields(
                row["properties"][name], {"state", "pass"},
                f"independent PASS cell row {index} property")
            consistent = (
                (property_row["state"] == "PASS" and
                 property_row["pass"] is True) or
                (property_row["state"] == "FAIL" and
                 property_row["pass"] is False) or
                (property_row["state"] == "INCOMPLETE" and
                 property_row["pass"] is None))
            _expect(consistent and
                    (not required or
                     (property_row["state"] == "PASS" and
                      property_row["pass"] is True)),
                    f"independent PASS cell row {index} property invalid")
        for key in ("bundle_manifest_sha256", "raw_stdout_sha256",
                    "native_session_sha256", "official_verdict_sha256"):
            _digest(row[key], f"independent PASS cell row {index} {key}")


def rederive_campaign(packet_path, campaign_root, surface_root=None):
    # Path-component custody is stable only for one create-once read pass.
    # A later invocation must not inherit trust after a directory replacement.
    _CUSTODY_COMPONENT_CACHE.clear()
    packet_path = pathlib.Path(packet_path).absolute()
    campaign_root = pathlib.Path(campaign_root).absolute()
    surface_root = (campaign_root if surface_root is None else
                    pathlib.Path(surface_root).absolute())
    packet, packet_bytes = _read_json(packet_path, "freeze packet")
    _validate_freeze_contract(packet, surface_root)
    frozen = _read_bytes(campaign_root / "campaign-freeze.json")
    _expect(frozen == packet_bytes, "campaign frozen packet drift")
    freeze_sha = _sha(frozen)
    custody, _ = _read_json(campaign_root / "campaign-manifest.json",
                            "campaign manifest")
    custody = _exact_fields(
        custody, CAMPAIGN_MANIFEST_FIELDS, "campaign manifest")
    _expect(custody["schema"] ==
            "implementaudit-candidate-matrix-luna-campaign-custody-v1" and
            custody["campaign"] == packet["campaign"] and
            custody["freeze_sha256"] == freeze_sha and
            custody["contract_sha256"] ==
            packet["artifact_contract"]["sha256"] and
            custody["execution_stage"] ==
            "LUNA" and
            type(custody["created_at"]) is str and bool(custody["created_at"]),
            "campaign custody invalid")
    expected_order = [_attempt_name(mission) for mission in packet["cells"]]
    expected_names = set(expected_order)
    andon_path = campaign_root / "campaign-andon.json"
    invalid_andon = None
    if os.path.lexists(andon_path):
        try:
            marker_value, _ = _read_json(andon_path, "campaign ANDON")
            marker, stopped_mission = _validate_campaign_andon(
                marker_value, packet, campaign_root, freeze_sha)
            allowed_andon_root = expected_names | {
                "campaign-freeze.json", "campaign-manifest.json",
                "campaign-andon.json"}
            unexpected_root = {
                path.name for path in campaign_root.iterdir()} - \
                allowed_andon_root
            _expect(
                not unexpected_root,
                "campaign ANDON contains unexpected custody entry")
            _expect(
                not list(campaign_root.glob("attempt-*.claiming")),
                "campaign ANDON contains nonterminal claim")
            actual_names = {
                path.name for path in campaign_root.glob("attempt-*")
                if not path.name.endswith(".claiming")}
            stopped_index = marker["mission_index"]
            _expect(
                actual_names == set(expected_order[:stopped_index + 1]),
                "campaign ANDON attempt prefix invalid")
            stopped_attempt = campaign_root / marker["attempt_name"]
            _expect(
                stopped_attempt.is_dir() and
                {path.name for path in stopped_attempt.iterdir()} <= {
                    "attempt-status.json", "attempt-terminal.json",
                    "host-attestation.json", "official-verdict.json",
                    "host-custody"},
                "campaign ANDON attempt custody invalid")
            property_declarations = {}
            rows = [
                _rederive_attempt(
                    packet, campaign_root, mission, freeze_sha,
                    property_declarations)
                for mission in packet["cells"][:stopped_index]
            ]
            rows.append(_stopped_row(
                stopped_mission, "ERROR", marker["stop_reason"],
                marker["execution_mode"]))
            return _andon_result(
                packet, freeze_sha, rows, marker["stop_reason"])
        except (EvidenceInvalid, OSError, KeyError, TypeError, ValueError) as exc:
            invalid_andon = str(exc)
    allowed_root = expected_names | {"campaign-freeze.json",
                                     "campaign-manifest.json",
                                     "candidate-matrix-luna-independent-rederivation.json",
                                     "candidate-matrix-luna-result.json",
                                     "luna-stage-terminal.json"}
    if surface_root == campaign_root:
        allowed_root.update(
            pathlib.PurePosixPath(row["path"]).parts[0]
            for row in packet["evaluated_surfaces"]["entries"]
            if not pathlib.Path(row["path"]).is_absolute())
    if os.path.lexists(andon_path):
        allowed_root.add("campaign-andon.json")
    unexpected_root = {path.name for path in campaign_root.iterdir()} - allowed_root
    _expect(not unexpected_root, "campaign contains unexpected custody entry")
    actual_names = {path.name for path in campaign_root.glob("attempt-*")
                    if not path.name.endswith(".claiming")}
    _expect(not list(campaign_root.glob("attempt-*.claiming")),
            "campaign contains nonterminal claim")
    completed_count = len(actual_names)
    _expect(actual_names == set(expected_order[:completed_count]),
            "campaign attempt set reordered or unexpected")
    nonterminal_index = None
    for index, name in enumerate(expected_order[:completed_count]):
        attempt = campaign_root / name
        allowed_attempt = {"attempt-status.json", "attempt-terminal.json",
                           "host-attestation.json", "official-verdict.json",
                           "host-custody"}
        _expect({path.name for path in attempt.iterdir()} <= allowed_attempt,
                "attempt contains unexpected custody entry")
        _expect(
            (attempt / "attempt-status.json").is_file(),
            "attempt status is missing")
        if not (attempt / "attempt-terminal.json").is_file():
            _expect(
                index == completed_count - 1,
                "attempt lifecycle gap precedes later attempt")
            nonterminal_index = index
    if nonterminal_index is not None:
        property_declarations = {}
        rows = [
            _rederive_attempt(
                packet, campaign_root, mission, freeze_sha,
                property_declarations)
            for mission in packet["cells"][:nonterminal_index]
        ]
        mission = packet["cells"][nonterminal_index]
        status, _ = _read_json(
            campaign_root / expected_order[nonterminal_index] /
            "attempt-status.json", "nonterminal attempt status")
        status = _validate_attempt_status(
            status, mission, freeze_sha,
            packet["artifact_contract"]["sha256"],
            packet["configuration"])
        reason = invalid_andon or "attempt lifecycle is nonterminal"
        rows.append(_stopped_row(
            mission, "ERROR", reason, status["execution_mode"]))
        return _andon_result(packet, freeze_sha, rows, reason)
    if invalid_andon is not None:
        property_declarations = {}
        rows = [
            _rederive_attempt(
                packet, campaign_root, mission, freeze_sha,
                property_declarations)
            for mission in packet["cells"][:completed_count]
        ]
        if rows:
            last = rows[-1]
            rows[-1] = _stopped_row(
                packet["cells"][len(rows) - 1], "ERROR",
                invalid_andon, last.get("execution_mode"))
        return _andon_result(
            packet, freeze_sha, rows, invalid_andon)
    property_declarations = {}
    rows = [
        _rederive_attempt(
            packet, campaign_root, mission, freeze_sha,
            property_declarations)
        for mission in packet["cells"][:completed_count]]
    observed_modes = [row.get("execution_mode") for row in rows]
    mode_set = set(observed_modes)
    exact_mode = next(iter(mode_set)) if len(mode_set) == 1 and \
        mode_set <= {"production", "test"} else None
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
    elif completed_count < len(packet["cells"]):
        status = "INCOMPLETE"
    else:
        status = "PASS"
    if status == "PASS" and exact_mode == "test":
        status = "TEST_ONLY_NON_QUALIFYING"
    elif status == "PASS" and exact_mode != "production":
        status = "INVALID"
    stage_accepted = status == "PASS" and \
        completed_count == len(packet["cells"]) and \
        exact_mode == "production"
    if stage_accepted:
        _validate_stage_pass_rows(
            rows, property_declarations,
            packet["configuration"]["model_resolved_required"])
    disposition = ("INCOMPLETE_PENDING_OPUS" if stage_accepted else
                   "TEST_ONLY_NON_QUALIFYING"
                   if status == "TEST_ONLY_NON_QUALIFYING" else
                   "INCOMPLETE" if status == "INCOMPLETE" else
                   "ANDON_STOPPED")
    result = {
        "schema":
            "implementaudit-candidate-matrix-luna-independent-rederivation-v1",
        "campaign": "candidate-matrix-sol-luna-r1",
        "freeze_sha256": freeze_sha,
        "contract_sha256": packet["artifact_contract"]["sha256"],
        "execution_mode": exact_mode,
        "luna_stage_status": status, "disposition": disposition,
        "luna_stage_accepted": stage_accepted, "accepted": False,
        "cell_count": len(rows), "cells": rows,
        "claims": dict(FINAL_CLAIMS)}
    if attempts_after_stop:
        result["reason"] = "campaign contains attempt after terminal stop"
    elif status == "INVALID" and exact_mode is None:
        result["reason"] = "campaign execution modes are mixed or invalid"
    return result


def _validate_output_parent(root, path):
    root = pathlib.Path(root).absolute()
    path = pathlib.Path(path).absolute()
    _expect(path.parent == root and
            path.name ==
            "candidate-matrix-luna-independent-rederivation.json",
            "independent result path must be the declared campaign-root path")
    current = pathlib.Path(root.anchor)
    try:
        for part in root.parts[1:]:
            current = current / part
            component_stat = os.lstat(current)
            _expect(not current.is_symlink() and
                    not _reparse_point(component_stat),
                    "independent result parent path-component alias invalid")
        root_stat = os.lstat(root)
        _expect(stat.S_ISDIR(root_stat.st_mode),
                "independent result parent custody invalid")
        _expect(path.parent.resolve(strict=True) == root.resolve(strict=True),
                "independent result parent containment invalid")
    except EvidenceInvalid:
        raise
    except (OSError, ValueError) as exc:
        raise EvidenceInvalid(
            "independent result parent custody invalid") from exc
    return root, path, (root_stat.st_dev, root_stat.st_ino)


def write_rederivation(path, result, *, root):
    root, path, parent_identity = _validate_output_parent(root, path)
    try:
        try:
            os.lstat(path)
        except FileNotFoundError:
            pass
        else:
            raise EvidenceInvalid(
                "create-once independent result already exists")
        payload = (json.dumps(result, sort_keys=True,
                              separators=(",", ":")) + "\n").encode("utf-8")
        with open(path, "xb") as stream:
            opened = os.fstat(stream.fileno())
            _expect(stat.S_ISREG(opened.st_mode) and opened.st_nlink == 1,
                    "independent result create-once identity invalid")
            _root, _path, observed_parent_identity = \
                _validate_output_parent(root, path)
            _expect(observed_parent_identity == parent_identity,
                    "independent result parent changed during create")
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
    except FileExistsError as exc:
        raise EvidenceInvalid(
            "create-once independent result already exists") from exc
    except EvidenceInvalid:
        raise
    except OSError as exc:
        raise EvidenceInvalid("independent result cannot be created") from exc
    return path


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("intent")
    parser.add_argument("--campaign-root", required=True)
    parser.add_argument("--surface-root")
    parser.add_argument("--output")
    args = parser.parse_args(argv)
    try:
        result = rederive_campaign(
            args.intent, args.campaign_root, args.surface_root)
    except (EvidenceInvalid, OSError, KeyError, TypeError, ValueError) as exc:
        result = {
            "schema":
                "implementaudit-candidate-matrix-luna-independent-rederivation-v1",
            "campaign": "candidate-matrix-sol-luna-r1",
            "freeze_sha256": None,
            "contract_sha256": CONTRACT_SHA256,
            "execution_mode": None,
            "luna_stage_status": "INVALID",
            "disposition": "ANDON_STOPPED",
            "luna_stage_accepted": False, "accepted": False,
            "cell_count": 0, "cells": [],
            "claims": dict(FINAL_CLAIMS), "reason": str(exc)}
    rendered = json.dumps(result, indent=1, sort_keys=True) + "\n"
    if args.output:
        write_rederivation(args.output, result, root=args.campaign_root)
    else:
        sys.stdout.write(rendered)
    return 0 if result.get("luna_stage_accepted") is True else 2


if __name__ == "__main__":
    raise SystemExit(main())
