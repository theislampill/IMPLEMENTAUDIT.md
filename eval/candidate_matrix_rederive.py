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
from datetime import datetime, timedelta


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
    "evaluated_surface_owners", "evaluated_surfaces",
}
EVALUATED_SURFACE_ROLES = tuple(sorted((
    "acceptance-rules", "adapter", "artifact-contract",
    "authorization-acknowledgement", "checkout-runtime-topology",
    "evaluator", "evidence-contract", "fixture-inventory",
    "host-attestation", "host-read-contract", "host-runner",
    "independent-rederiver", "launcher", "lifecycle-contract",
    "matrix-acceptance", "matrix-fixture-setup", "matrix-host-policy",
    "model-reasoning-host-identity", "native-executable",
    "official-driver", "product-candidate", "prompt-construction-rules",
    "prompt-template", "scorer", "seed-order-repetition-rules",
    "verdict-contract",
) + tuple(f"fixture-{name}" for name in FIXTURE_ORDER)))
EVALUATED_SURFACE_GIT_ROLES = {
    "product-candidate", "official-driver", "host-runner", "scorer",
    "evaluator", "adapter", "independent-rederiver",
    "matrix-acceptance", "matrix-fixture-setup", "matrix-host-policy",
}
EVALUATED_SURFACE_EXTERNAL_ROLES = {
    "product-candidate", "authorization-acknowledgement",
    "host-attestation", "launcher", "native-executable",
    "checkout-runtime-topology",
}
EVALUATED_SURFACE_VIRTUAL_ROLES = {
    "acceptance-rules", "authorization-acknowledgement",
    "evidence-contract", "fixture-inventory",
    "model-reasoning-host-identity", "seed-order-repetition-rules",
}
CONTRACT_ARTIFACTS = {
    "campaign_freeze", "campaign_manifest", "attempt_status",
    "host_attestation", "launch_readiness", "official_verdict",
    "attempt_terminal",
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
    "launch_readiness_binding",
}
HOST_ATTESTATION_BINDING_FIELDS = {
    "path", "sha256", "config", "host", "model_resolved_required",
}
HOST_ATTESTATION_FIELDS = {"id", "shell_dialect", "executables"}
LAUNCH_READINESS_BINDING_FIELDS = {
    "path", "sha256", "schema", "execution_mode", "disposition",
}
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
    "host_attestation_sha256", "launch_readiness_sha256",
    "host_custody_manifest_sha256",
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
# Independent copy: ceil(9.242s), the maximum across twelve hash-deduplicated
# retained native session/process pairs, defines the whole-second ceiling.
CODEX_SESSION_START_WINDOW_SECONDS = 10
CODEX_ANONYMOUS_TURN_SENTINEL = "<unique-turn>"
CODEX_REQUIRED_PROCESS_IDENTITY_FIELDS = {"cwd", "requested_model"}
CODEX_REQUIRED_TURN_IDENTITY_FIELDS = {"cwd", "model", "turn_id"}
CODEX_NATIVE_REPO_FIELDS = {"lexical_root", "real_root", "case_sensitive"}
CODEX_NATIVE_PAYLOAD_FIELDS = {
    "session_meta": (
        {"id", "session_id", "cwd"},
        {"originator", "cli_version", "source", "thread_source",
         "model_provider", "git", "base_instructions",
         "developer_instructions", "dynamic_tools", "reasoning_effort",
         "history_mode", "context_window", "timestamp"},
    ),
    "turn_context": (
        {"turn_id", "cwd"},
        {"workspace_roots", "current_date", "timezone", "approval_policy",
         "approvals_reviewer", "sandbox_policy", "permission_profile",
         "file_system_sandbox_policy", "model", "comp_hash", "personality",
         "collaboration_mode", "multi_agent_version", "realtime_active",
         "effort", "summary", "service_tier"},
    ),
    "response_item": (
        set(),
        {"type", "action_ids", "role", "content", "id", "status", "name",
         "arguments", "call_id", "summary", "message", "phase", "text",
         "images", "encrypted_content", "input", "output",
         "internal_chat_message_metadata_passthrough"},
    ),
    "event_msg": (
        set(),
        {"type", "action_ids", "role", "content", "id", "status", "name",
         "arguments", "call_id", "summary", "message", "phase", "text",
         "images", "encrypted_content", "changes",
         "collaboration_mode_kind", "completed_at", "duration_ms", "info",
         "last_agent_message", "local_images", "memory_citation",
         "model_context_window", "rate_limits", "started_at", "stderr",
         "stdout", "success", "text_elements", "time_to_first_token_ms",
         "turn_id"},
    ),
    "world_state": ({"state", "full"}, set()),
}
CODEX_COLLAB_NATIVE_TOOL_NAMES = frozenset((
    "spawn_agent", "wait_agent", "send_input", "close_agent",
    "send_message", "resume_agent", "followup_task", "interrupt_agent",
    "list_agents",
))
CODEX_COLLAB_NATIVE_CHILD_ID_PATTERN = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
    re.IGNORECASE)
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
    "eval.campaign_freeze_preflight",
    "eval.candidate_matrix_acceptance",
    "eval.candidate_matrix_fixture_setup", "eval.candidate_matrix_host",
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
CONTRACT_SHA256 = "15ce14d59bb33163e7e84490915403011c5b430489e0c82e9adb7fc4bd2792e3"
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
    "tool", "sender_thread_id", "prompt", "receiver_thread_ids",
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
        "required_capabilities", "matrix_acceptance", "matrix_precondition",
        "matrix_instruction_contract",
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
    if "matrix_acceptance" in fixture:
        matrix = _exact_fields(
            fixture["matrix_acceptance"], {"schema", "properties"},
            "fixture.matrix_acceptance")
        _expect(
            matrix["schema"] in {
                "implementaudit-candidate-matrix-acceptance-v1",
                "implementaudit-candidate-matrix-acceptance-v2",
            } and
            type(matrix["properties"]) is dict and
            bool(matrix["properties"]) and
            set(matrix["properties"]) <= set(names) and
            all(type(key) is str and key and type(value) is str and value
                for key, value in matrix["properties"].items()),
            "fixture matrix acceptance invalid")
        if expected_id in {"B1", "E2a", "E3", "E7", "E9"}:
            expected_properties = (
                set(names) - {"no_producer_diff"}
                if expected_id == "E2a" else set(names))
            _expect(
                matrix["schema"] ==
                "implementaudit-candidate-matrix-acceptance-v2" and
                set(matrix["properties"]) == expected_properties,
                "structured fixture matrix acceptance invalid")
        else:
            _expect(
                matrix["schema"] ==
                "implementaudit-candidate-matrix-acceptance-v1",
                "free-text fixture matrix acceptance invalid")
    if "matrix_precondition" in fixture:
        precondition = _exact_fields(
            fixture["matrix_precondition"], {"schema", "kind", "path"},
            "fixture.matrix_precondition")
        _expect(
            precondition["schema"] ==
            "implementaudit-candidate-matrix-precondition-v1" and
            precondition["kind"] in ("resume-run-root", "dirty-worktree") and
            type(precondition["path"]) is str and precondition["path"],
            "fixture matrix precondition invalid")
    if "matrix_instruction_contract" in fixture:
        instruction = _exact_fields(
            fixture["matrix_instruction_contract"], {"schema", "fields"},
            "fixture.matrix_instruction_contract")
        _expect(
            instruction["schema"] ==
            "implementaudit-matrix-instruction-contract-v1",
            "fixture matrix instruction contract invalid")
        fields = instruction["fields"]
        _expect(type(fields) is list and bool(fields),
                "fixture matrix instruction fields invalid")
        names = []
        for index, row in enumerate(fields):
            owner = f"fixture matrix instruction field {index}"
            row = _mapping(row, owner)
            common = {
                "field", "property", "form", "behavior",
                "forbidden_mission_phrases",
            }
            form = row.get("form")
            _expect(form in {"opaque", "enumerated"},
                    owner + " form invalid")
            expected = common | (
                {"placeholder"} if form == "opaque" else
                {"expected", "distractors"})
            _expect(set(row) == expected, owner + " exact key set invalid")
            for key in ("field", "property"):
                _expect(type(row[key]) is str and bool(row[key]),
                        owner + f" {key} invalid")
            if form == "opaque":
                _expect(
                    type(row["placeholder"]) is str and
                    bool(row["placeholder"]) and "|" not in row["placeholder"],
                    owner + " placeholder invalid")
            else:
                _expect(type(row["expected"]) is str and bool(row["expected"]),
                        owner + " expected invalid")
                _strings(row["distractors"], owner + " distractors")
                _expect(
                    bool(row["distractors"]) and
                    len(row["distractors"]) ==
                    len(set(row["distractors"])) and
                    row["expected"] not in row["distractors"],
                    owner + " distractors invalid")
            _expect(type(row["behavior"]) is bool,
                    owner + " behavior invalid")
            _strings(row["forbidden_mission_phrases"],
                     owner + " forbidden mission phrases")
            _expect(
                bool(row["forbidden_mission_phrases"]) == row["behavior"],
                owner + " behavior phrases invalid")
            names.append(row["field"])
        _expect(len(names) == len(set(names)),
                "fixture matrix instruction fields duplicate")
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
    if (surface_root is not None and os.path.lexists(
            pathlib.Path(surface_root).absolute() /
            "evaluated-surface-projections")):
        raise EvidenceInvalid(
            "evaluated surface virtual projection shadow or residue forbidden")
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
        virtual = (
            role in EVALUATED_SURFACE_VIRTUAL_ROLES and
            row["path"] ==
            f"evaluated-surface-projections/{role}.json")
        if surface_root is not None and not virtual:
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


def _validate_surface_owners(packet):
    """Independent semantic join; deliberately does not import official code."""
    envelope = _exact_fields(
        packet["evaluated_surface_owners"],
        {"schema", "campaign", "roles"}, "evaluated surface owners")
    _expect(
        envelope["schema"] == "implementaudit-evaluated-surface-owners-v1"
        and envelope["campaign"] == "candidate-matrix-sol-luna-r1",
        "evaluated surface owners identity invalid")
    owners = envelope["roles"]
    _expect(type(owners) is dict and
            set(owners) == set(EVALUATED_SURFACE_ROLES),
            "evaluated surface owner role coverage invalid")
    manifest = {
        row["role"]: row for row in packet["evaluated_surfaces"]["entries"]}
    inline = {
        "acceptance-rules": {
            "acceptance_rule": packet["acceptance_rule"],
            "invalid_error_rule": packet["invalid_error_rule"],
            "result_composition": packet["result_composition"],
            "stop_conditions": packet["stop_conditions"],
        },
        "authorization-acknowledgement": packet["authorization"],
        "evidence-contract": {
            "attempt_policy": packet["attempt_policy"],
            "bundle_artifact": packet["artifacts"]["bundle"],
            "evidence_profiles": packet["evidence_profiles"],
            "luna_stage": packet["luna_stage"],
        },
        "fixture-inventory": packet["fixtures"],
        "model-reasoning-host-identity": packet["configuration"],
        "seed-order-repetition-rules": {
            "cells": packet["cells"], "seed": packet["seed"],
        },
    }
    fixed = {
        "adapter": "eval/adapters.py",
        "host-read-contract": "eval/lib/hostread.py",
        "lifecycle-contract": "eval/campaign_lifecycle.py",
        "matrix-acceptance": "eval/candidate_matrix_acceptance.py",
        "matrix-fixture-setup": "eval/candidate_matrix_fixture_setup.py",
        "matrix-host-policy": "eval/candidate_matrix_host.py",
        "official-driver": "eval/candidate_matrix_campaign.py",
        "prompt-construction-rules": "eval/hosts.py",
        "verdict-contract": "eval/lib/verdict.py",
    }
    fixtures = {row["id"]: row for row in packet["fixtures"]}
    for role in EVALUATED_SURFACE_ROLES:
        owner = owners[role]
        _expect(
            type(owner) is dict and owner and
            all(type(value) is str and value for value in owner.values()),
            f"evaluated surface owner {role} scalar types invalid")
        git = {}
        raw = None
        if role in inline:
            owner = _exact_fields(owner, {"kind"},
                                  f"evaluated surface owner {role}")
            _expect(owner["kind"] == f"packet-projection-{role}",
                    f"evaluated surface owner {role} kind invalid")
            path = f"evaluated-surface-projections/{role}.json"
            raw = (json.dumps({
                "campaign": "candidate-matrix-sol-luna-r1",
                "projection": inline[role], "role": role,
                "schema":
                    "implementaudit-evaluated-surface-projection-v1",
            }, sort_keys=True, separators=(",", ":")) + "\n").encode()
            digest = _sha(raw)
        elif role == "artifact-contract":
            owner = _exact_fields(owner, {"kind"},
                                  f"evaluated surface owner {role}")
            _expect(owner["kind"] == "packet-artifact-contract",
                    f"evaluated surface owner {role} kind invalid")
            path = packet["artifact_contract"]["path"]
            digest = packet["artifact_contract"]["sha256"]
        elif role in ("scorer", "evaluator", "host-runner"):
            artifact = {"host-runner": "runner"}.get(role, role)
            owner = _exact_fields(
                owner, {"kind", "artifact", "git_commit", "git_tree"},
                f"evaluated surface owner {role}")
            _expect(
                owner["kind"] == f"packet-artifact-{role}" and
                owner["artifact"] == artifact,
                f"evaluated surface owner {role} kind invalid")
            path = packet["artifacts"][artifact]["path"]
            digest = packet["artifacts"][artifact]["sha256"]
            git = {"git_commit": owner["git_commit"],
                   "git_tree": owner["git_tree"]}
        elif role.startswith("fixture-"):
            fixture_id = role[len("fixture-"):]
            owner = _exact_fields(
                owner, {"kind", "fixture_id"},
                f"evaluated surface owner {role}")
            _expect(owner == {"kind": "packet-fixture",
                              "fixture_id": fixture_id} and
                    fixture_id in fixtures,
                    f"evaluated surface owner {role} fixture invalid")
            path = fixtures[fixture_id]["path"]
            digest = fixtures[fixture_id]["sha256"]
        elif role == "independent-rederiver":
            owner = _exact_fields(
                owner, {"kind", "git_commit", "git_tree"},
                f"evaluated surface owner {role}")
            _expect(owner["kind"] == "packet-independent-rederiver",
                    f"evaluated surface owner {role} kind invalid")
            identity = packet["independent_rederiver"][
                "implementation_identity"]
            path, digest = identity["path"], identity["sha256"]
            git = {"git_commit": owner["git_commit"],
                   "git_tree": owner["git_tree"]}
        elif role == "native-executable":
            owner = _exact_fields(owner, {"kind"},
                                  f"evaluated surface owner {role}")
            _expect(owner["kind"] == "packet-native-executable",
                    f"evaluated surface owner {role} kind invalid")
            identity = packet["configuration"]["executable"]
            path, digest = identity["path"], identity["sha256"]
        elif role == "product-candidate":
            owner = _exact_fields(
                owner, {"kind", "packet_owner", "path"},
                f"evaluated surface owner {role}")
            _expect(owner["kind"] == "packet-product-candidate" and
                    owner["packet_owner"] == "candidate",
                    f"evaluated surface owner {role} kind invalid")
            path = owner["path"]
            pure = pathlib.PurePosixPath(path.replace("\\", "/"))
            _expect(pure.name.lower() == "skill.md" and
                    pure.parent.name.lower() == "candidate",
                    f"evaluated surface owner {role} path policy invalid")
            digest = packet["candidate"]["payload_sha256"]
            git = {"git_commit": packet["candidate"]["commit"],
                   "git_tree": packet["candidate"]["tree"]}
        elif role == "host-attestation":
            owner = _exact_fields(
                owner, {"kind", "path"},
                f"evaluated surface owner {role}")
            name = pathlib.PurePosixPath(
                owner["path"].replace("\\", "/")).name.lower()
            _expect(owner["kind"] == "packet-host-attestation" and
                    name.endswith(".json") and "attestation" in name,
                    f"evaluated surface owner {role} path policy invalid")
            path = owner["path"]
            digest = packet["configuration"]["host_attestation"]["sha256"]
        elif role in fixed:
            fields = {"kind", "sha256"}
            if role in EVALUATED_SURFACE_GIT_ROLES:
                fields |= {"git_commit", "git_tree"}
            owner = _exact_fields(
                owner, fields, f"evaluated surface owner {role}")
            _expect(owner["kind"] == f"frozen-{role}",
                    f"evaluated surface owner {role} kind invalid")
            path, digest = fixed[role], owner["sha256"]
            if role in EVALUATED_SURFACE_GIT_ROLES:
                git = {"git_commit": owner["git_commit"],
                       "git_tree": owner["git_tree"]}
        else:
            owner = _exact_fields(
                owner, {"kind", "path", "sha256"},
                f"evaluated surface owner {role}")
            _expect(owner["kind"] == f"frozen-{role}",
                    f"evaluated surface owner {role} kind invalid")
            path, digest = owner["path"], owner["sha256"]
            name = pathlib.PurePosixPath(path.replace("\\", "/")).name.lower()
            policy = (
                role == "checkout-runtime-topology" and
                name == "checkout-runtime-topology.json" or
                role == "launcher" and name in
                ("codex", "codex.exe", "luna-launcher",
                 "luna-launcher.exe") or
                role == "prompt-template" and name in
                ("prompt-template.md", "prompt-template.txt", "readme.md"))
            _expect(policy,
                    f"evaluated surface owner {role} path policy invalid")
        row = manifest[role]
        _expect(row["path"] == path and row["sha256"] == digest,
                f"evaluated surface owner/manifest mismatch: {role}")
        observed_git = {key: row[key] for key in ("git_commit", "git_tree")
                        if key in row}
        _expect(observed_git == git,
                f"evaluated surface owner/Git mismatch: {role}")
        if raw is not None:
            _expect(row["byte_length"] == len(raw),
                    f"evaluated surface projection length mismatch: {role}")


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
    _validate_surface_owners(packet)
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
    readiness = _exact_fields(
        status["launch_readiness_binding"],
        LAUNCH_READINESS_BINDING_FIELDS,
        "attempt status launch readiness binding")
    expected_disposition = (
        "READY_FOR_LUNA_EXECUTION"
        if status["execution_mode"] == "production"
        else "TEST_ONLY_NON_QUALIFYING")
    _expect(
        readiness["path"] == "launch-readiness.json" and
        readiness["schema"] ==
        "implementaudit-candidate-matrix-luna-live-launch-readiness-v1" and
        readiness["execution_mode"] == status["execution_mode"] and
        readiness["disposition"] == expected_disposition and
        type(readiness["sha256"]) is str and
        re.fullmatch(r"[0-9a-f]{64}", readiness["sha256"]) is not None,
        "launch readiness mission identity invalid")
    return status


def _load_launch_readiness(attempt, status, packet):
    binding = status["launch_readiness_binding"]
    path = _contained(attempt, binding["path"], "launch readiness")
    report, raw = _read_json(path, "launch readiness")
    fields = {
        "schema", "campaign", "freeze_sha256", "contract_sha256",
        "execution_mode", "disposition", "ready", "mission_authorized",
        "test_mock_authorized", "created_at", "model_scope",
        "host_attestation_binding", "native_executable_binding",
        "launcher_binding", "checkout_bindings", "runtime_root_binding",
        "authorization_binding", "cross_host_validation", "producer",
    }
    report = _exact_fields(report, fields, "launch readiness")
    production = status["execution_mode"] == "production"
    _expect(
        _sha(raw) == binding["sha256"] and
        report["schema"] == binding["schema"] and
        report["campaign"] == "candidate-matrix" and
        report["contract_sha256"] == packet["artifact_contract"]["sha256"] and
        report["execution_mode"] == status["execution_mode"] and
        report["disposition"] == binding["disposition"] and
        report["ready"] is production and
        report["mission_authorized"] is production and
        report["test_mock_authorized"] is (not production) and
        report["model_scope"] == {
            "model": "gpt-5.6-luna", "reasoning_effort": "max",
            "auth_mode": "chatgpt-subscription",
            "metered_api_spend": "FORBIDDEN",
        },
        "retained launch readiness identity invalid")
    return report, raw


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
                                     attestation_raw, readiness_raw,
                                     packet, freeze_sha):
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
        "launch_readiness_sha256": _sha(readiness_raw),
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


def _unquoted_ampersand_free(command):
    """Reject shell background/control ampersands without losing quote origin."""
    if not isinstance(command, str):
        return False
    state = "plain"
    index = 0
    while index < len(command):
        character = command[index]
        if state == "plain":
            if character == "\\":
                if index + 1 >= len(command):
                    return False
                index += 2
                continue
            if character == "'":
                state = "single"
            elif character == '"':
                state = "double"
            elif character == "&":
                return False
        elif state == "single":
            if character == "'":
                state = "plain"
        else:
            if character == "\\":
                if index + 1 >= len(command):
                    return False
                index += 2
                continue
            if character == '"':
                state = "plain"
        index += 1
    return state == "plain"


def _finite_shell_tokens(command):
    if not isinstance(command, str) or not command or "\x00" in command or \
            "\n" in command or "\r" in command or "$" in command or \
            "#" in command or "`" in command or \
            not _unquoted_ampersand_free(command) or any(
                text in command for text in
                (";", "&&", "||", "|", "(", ")", "{", "}")):
        return None
    try:
        lexer = shlex.shlex(command, posix=True, punctuation_chars="<>")
        lexer.whitespace_split = True
        lexer.commenters = ""
        return list(lexer)
    except (ValueError, TypeError):
        return None


def _command_tokens(command):
    tokens = _finite_shell_tokens(command)
    if not tokens:
        return None
    if len(tokens) == 3 and pathlib.PurePosixPath(tokens[0]).name in ("bash", "sh") \
            and tokens[1] in ("-c", "-lc"):
        tokens = _finite_shell_tokens(tokens[2])
        if not tokens:
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


def _validate_codex_collaboration_item(item, event_type, owner):
    fields = {
        "id", "type", "tool", "sender_thread_id", "receiver_thread_ids",
        "prompt", "status", "agents_states",
    }
    _exact_fields(item, fields, owner)
    _expect(event_type in ("item.started", "item.completed"),
            owner + " collaboration event invalid")
    _expect(item["type"] == "collab_tool_call" and
            type(item["id"]) is str and bool(item["id"]) and
            type(item["sender_thread_id"]) is str and
            bool(item["sender_thread_id"]) and
            isinstance(item["receiver_thread_ids"], list) and
            isinstance(item["agents_states"], dict),
            owner + " collaboration identity invalid")
    receivers = item["receiver_thread_ids"]
    _expect(all(type(receiver) is str and bool(receiver)
                for receiver in receivers) and
            len(receivers) == len(set(receivers)) and
            item["sender_thread_id"] not in receivers,
            owner + " collaboration receivers invalid")
    tool = item["tool"]
    _expect(tool in ("spawn_agent", "wait"),
            owner + " collaboration tool invalid")
    if event_type == "item.started":
        _expect(item["status"] == "in_progress" and
                not item["agents_states"],
                owner + " collaboration start metadata invalid")
        _expect((tool == "spawn_agent" and not receivers and
                 type(item["prompt"]) is str and bool(item["prompt"])) or
                (tool == "wait" and len(receivers) == 1 and
                 item["prompt"] is None),
                owner + " collaboration start shape invalid")
        return
    _expect(item["status"] == "completed" and len(receivers) == 1,
            owner + " collaboration completion metadata invalid")
    child = receivers[0]
    _expect(set(item["agents_states"]) == {child},
            owner + " collaboration child mismatch")
    state = _exact_fields(
        item["agents_states"][child], {"message", "status"},
        owner + " collaboration child state")
    if tool == "spawn_agent":
        _expect(type(item["prompt"]) is str and bool(item["prompt"]) and
                state["message"] is None and state["status"] == "pending_init",
                owner + " spawn completion invalid")
    else:
        _expect(item["prompt"] is None and
                type(state["message"]) is str and bool(state["message"]) and
                state["status"] == "completed",
                owner + " wait completion invalid")


def _validate_codex_stdout_rows(rows):
    usage_fields = {
        "input_tokens", "cached_input_tokens", "output_tokens",
        "reasoning_output_tokens"}
    for ordinal, event in rows:
        owner = f"Codex raw stdout line {ordinal}"
        event_type = event.get("type")
        if event_type == "thread.started":
            _exact_fields(event, {"type", "thread_id"}, owner)
        elif event_type == "turn.started":
            _expect(set(event) in (
                {"type"}, {"type", "thread_id", "turn_id"}),
                owner + " turn identity shape invalid")
            _expect(all(
                type(event[field]) is str and bool(event[field])
                for field in ("thread_id", "turn_id") if field in event),
                owner + " turn identity invalid")
            _expect(event.get("turn_id") != CODEX_ANONYMOUS_TURN_SENTINEL,
                    owner + " turn identity reserved")
        elif event_type == "turn.completed":
            _expect(set(event) in (
                {"type", "usage"},
                {"type", "thread_id", "turn_id", "usage"}),
                owner + " turn identity shape invalid")
            _expect(all(
                type(event[field]) is str and bool(event[field])
                for field in ("thread_id", "turn_id") if field in event),
                owner + " turn identity invalid")
            _expect(event.get("turn_id") != CODEX_ANONYMOUS_TURN_SENTINEL,
                    owner + " turn identity reserved")
            usage = _exact_fields(
                event["usage"], usage_fields, owner + " usage")
            _expect(all(type(value) is int and value >= 0
                        for value in usage.values()),
                    owner + " usage invalid")
        elif event_type in ("item.started", "item.updated", "item.completed"):
            _exact_fields(event, {"type", "item"}, owner)
            item = _mapping(event["item"], owner + " item")
            item_type = item.get("type")
            if item_type == "command_execution":
                _expect(event_type != "item.updated",
                        owner + " unsupported command update")
                required = {
                    "id", "type", "status", "command",
                    "aggregated_output", "exit_code"}
                _exact_fields(item, required, owner + " command item")
                _expect(type(item["command"]) is str,
                        owner + " command invalid")
                if event_type == "item.started":
                    _expect(item["status"] == "in_progress" and
                            item["aggregated_output"] == "" and
                            item["exit_code"] is None,
                            owner + " command start metadata invalid")
                else:
                    _expect(type(item["exit_code"]) is int and
                            type(item["aggregated_output"]) is str and
                            item["status"] == (
                                "completed" if item["exit_code"] == 0
                                else "failed"),
                            owner + " command completion invalid")
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
            elif item_type == "collab_tool_call":
                _exact_fields(event, {"type", "item"}, owner)
                _validate_codex_collaboration_item(
                    item, event_type, owner + " collaboration item")
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
    collaboration_children = {}
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
            turn_id = observed or CODEX_ANONYMOUS_TURN_SENTINEL
            bound_turn_id = observed
            continue
        if event_type == "turn.completed":
            completion_turn = event.get("turn_id")
            _expect(
                    turn_id is not None and
                    event.get("thread_id", thread_id) == thread_id and
                    ((bound_turn_id is None and "turn_id" not in event) or
                     (bound_turn_id is not None and
                      completion_turn == bound_turn_id)),
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
        if item_type == "collab_tool_call":
            _expect(item["sender_thread_id"] == thread_id,
                    "Codex raw collaboration sender mismatch")
            tool = item["tool"]
            sender = item["sender_thread_id"]
            prompt = item["prompt"]
            receivers = item["receiver_thread_ids"]
            if event_type == "item.started":
                _expect(action_id not in reserved,
                        "Codex raw collaboration action id reused")
                child = receivers[0] if tool == "wait" else None
                if tool == "wait":
                    _expect(collaboration_children.get(child) == "spawned",
                            "Codex raw orphan or duplicate collaboration wait")
                reserved.add(action_id)
                action = {
                    "id": action_id, "state": "PENDING",
                    "effect": "safe-other",
                    "classification": "not-content-read",
                    "action_type": "collab_tool_call", "tool": tool,
                    "sender_thread_id": sender, "prompt": prompt,
                    "receiver_thread_ids": list(receivers),
                    "invocation_ordinal": ordinal,
                    "completion_ordinal": None,
                }
                pending[action_id] = action
                actions.append(action)
                if tool == "wait":
                    collaboration_children[child] = "wait_pending"
                continue
            action = pending.pop(action_id, None)
            _expect(action is not None and
                    action["action_type"] == "collab_tool_call" and
                    action["tool"] == tool and
                    action["sender_thread_id"] == sender and
                    action["prompt"] == prompt,
                    "Codex raw collaboration start/completion conflict")
            child = receivers[0]
            if tool == "spawn_agent":
                _expect(action["receiver_thread_ids"] == [] and
                        child not in collaboration_children,
                        "Codex raw invalid collaboration spawn transition")
                collaboration_children[child] = "spawned"
            else:
                _expect(action["receiver_thread_ids"] == [child] and
                        collaboration_children.get(child) == "wait_pending",
                        "Codex raw invalid collaboration wait transition")
                collaboration_children[child] = "completed"
            action.update({
                "state": "COMPLETED", "receiver_thread_ids": list(receivers),
                "completion_ordinal": ordinal,
            })
            continue
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
    _expect(not pending and
            all(state == "completed"
                for state in collaboration_children.values()) and
            actions and thread_id is not None and
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
    profile = _mapping(profile, "formal-v2 host profile")
    common = {"schema", "authority", "host", "repo", "probe_sha256"}
    _expect(profile.get("schema") == "implementaudit-host-read-profile-v2" and
            profile.get("authority") == "mechanically-minted" and
            profile.get("host") == expected_host and
            bool(HEX64.fullmatch(str(profile.get("probe_sha256", "")))),
            "formal-v2 host profile invalid")
    repo = _mapping(profile.get("repo"), "formal-v2 profile repository")
    _expect(set(repo) == {"lexical_root", "real_root", "case_sensitive"} and
            type(repo.get("lexical_root")) is str and
            bool(repo["lexical_root"]) and
            type(repo.get("real_root")) is str and bool(repo["real_root"]) and
            type(repo.get("case_sensitive")) is bool,
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


def _parse_codex_session_time(value):
    if type(value) is not str:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed if parsed.utcoffset() is not None else None


def _codex_path_identity_text(value):
    if type(value) is not str:
        return ""
    text = value.replace("\\", "/")
    if text == "/" or re.fullmatch(r"[A-Za-z]:/", text):
        return text
    return text.rstrip("/")


def _codex_same_path(first, second, case_sensitive):
    first = _codex_path_identity_text(first)
    second = _codex_path_identity_text(second)
    if (re.match(r"^[A-Za-z]:(?:$|[^/])", first) or
            re.match(r"^[A-Za-z]:(?:$|[^/])", second)):
        return False
    if not case_sensitive:
        first, second = first.lower(), second.lower()
    return bool(first and second and first == second)


def _codex_native_repo_policy(profile):
    if not isinstance(profile, dict):
        return None
    repo = profile.get("repo")
    if (not isinstance(repo, dict) or
            set(repo) != CODEX_NATIVE_REPO_FIELDS or
            type(repo.get("lexical_root")) is not str or
            not repo["lexical_root"] or
            type(repo.get("real_root")) is not str or
            not repo["real_root"] or
            type(repo.get("case_sensitive")) is not bool):
        return None
    return repo


def _codex_native_collaboration_name(name):
    if type(name) is not str:
        return False
    folded = name.casefold()
    return (
        folded in CODEX_COLLAB_NATIVE_TOOL_NAMES or
        folded.startswith("multi_agent_v1__") or
        folded.startswith("collaboration.") or
        folded.startswith("collaboration__")
    )


def _codex_native_exec_has_collaboration(value):
    if type(value) is not str:
        return False

    def marker(text):
        folded = text.casefold()
        return ("multi_agent_v1__" in folded or
                "collaboration." in folded or
                "collaboration__" in folded or
                any(name in folded for name in CODEX_COLLAB_NATIVE_TOOL_NAMES))

    def escape(index):
        if index + 1 >= len(value):
            return "", len(value), False
        char = value[index + 1]
        simple = {"n": "\n", "r": "\r", "t": "\t", "b": "\b",
                  "f": "\f", "v": "\v", "0": "\0"}
        if char in simple:
            return simple[char], index + 2, True
        if char in "\r\n":
            end = index + 2
            if char == "\r" and end < len(value) and value[end] == "\n":
                end += 1
            return "", end, True
        if char == "x":
            digits = value[index + 2:index + 4]
            if len(digits) == 2 and all(c in "0123456789abcdefABCDEF"
                                        for c in digits):
                return chr(int(digits, 16)), index + 4, True
            return "", len(value), False
        if char == "u":
            if index + 2 < len(value) and value[index + 2] == "{":
                close = value.find("}", index + 3)
                digits = value[index + 3:close] if close >= 0 else ""
                if (digits and len(digits) <= 6 and
                        all(c in "0123456789abcdefABCDEF" for c in digits)):
                    point = int(digits, 16)
                    if point <= 0x10ffff:
                        return chr(point), close + 1, True
                return "", len(value), False
            digits = value[index + 2:index + 6]
            if len(digits) == 4 and all(c in "0123456789abcdefABCDEF"
                                        for c in digits):
                return chr(int(digits, 16)), index + 6, True
            return "", len(value), False
        return char, index + 2, True

    def identifier_start(char):
        return char in "_$" or char.isidentifier()

    def identifier_part(char):
        return (char in "_$\u200c\u200d" or
                ("a" + char).isidentifier())

    def identifier_escape(index):
        if not value.startswith("\\u", index):
            return "", index + 1, False
        cursor = index + 2
        if cursor < len(value) and value[cursor] == "{":
            close = value.find("}", cursor + 1)
            if close < 0:
                return "", cursor + 1, False
            digits = value[cursor + 1:close]
            if (not digits or len(digits) > 6 or
                    not all(c in "0123456789abcdefABCDEF" for c in digits)):
                return "", close + 1, False
            point = int(digits, 16)
            if point > 0x10ffff:
                return "", close + 1, False
            return chr(point), close + 1, True
        digits = value[cursor:cursor + 4]
        if (len(digits) != 4 or
                not all(c in "0123456789abcdefABCDEF" for c in digits)):
            return "", min(len(value), cursor + max(1, len(digits))), False
        return chr(int(digits, 16)), cursor + 4, True

    def quoted(index, quote):
        decoded = []
        cursor = index + 1
        while cursor < len(value):
            char = value[cursor]
            if char == quote:
                return "".join(decoded), cursor + 1, False
            if char == "\\":
                part, cursor, valid = escape(cursor)
                if not valid:
                    return "", cursor, marker(value[index:])
                decoded.append(part)
                continue
            if char in "\r\n":
                return "", cursor, marker(value[index:cursor])
            decoded.append(char)
            cursor += 1
        return "", cursor, marker(value[index:])

    def regex_allowed(tokens):
        if not tokens:
            return True
        kind, token = tokens[-1]
        if kind == "id" and token.casefold() in {
                "return", "throw", "case", "delete", "void", "typeof",
                "instanceof", "in", "of", "yield", "await"}:
            return True
        return kind == "punct" and token in {
            "(", "[", "{", ",", ";", "=", ":", "!", "?", "+", "-",
            "*", "%", "&", "|", "^", "~", "<", ">"}

    def scan(start=0, stop_brace=False):
        tokens = []
        cursor = start
        brace_depth = 0
        ambiguous = False
        while cursor < len(value):
            char = value[cursor]
            if char.isspace():
                cursor += 1
                continue
            if stop_brace and char == "}" and brace_depth == 0:
                return tokens, cursor + 1, ambiguous, True
            if char in "'\"":
                decoded, cursor, bad = quoted(cursor, char)
                tokens.append(("str", decoded))
                ambiguous = ambiguous or bad
                continue
            if char == "`":
                template_start = cursor
                cursor += 1
                literal = []
                expressions = False
                closed = False
                while cursor < len(value):
                    char = value[cursor]
                    if char == "\\":
                        part, cursor, valid = escape(cursor)
                        if not valid:
                            ambiguous = ambiguous or marker(
                                value[template_start:])
                            cursor = len(value)
                            break
                        literal.append(part)
                    elif char == "`":
                        cursor += 1
                        closed = True
                        break
                    elif char == "$" and cursor + 1 < len(value) and \
                            value[cursor + 1] == "{":
                        expressions = True
                        tokens.append(("barrier", ""))
                        nested, cursor, bad, nested_closed = scan(
                            cursor + 2, True)
                        tokens.extend(nested)
                        tokens.append(("barrier", ""))
                        ambiguous = ambiguous or bad
                        if not nested_closed:
                            ambiguous = ambiguous or marker(
                                value[template_start:])
                            break
                    else:
                        literal.append(char)
                        cursor += 1
                if not closed:
                    ambiguous = ambiguous or marker(value[template_start:])
                elif not expressions:
                    tokens.append(("str", "".join(literal)))
                continue
            if value.startswith("//", cursor):
                end = value.find("\n", cursor + 2)
                cursor = len(value) if end < 0 else end + 1
                continue
            if value.startswith("/*", cursor):
                end = value.find("*/", cursor + 2)
                if end < 0:
                    ambiguous = ambiguous or marker(value[cursor:])
                    cursor = len(value)
                else:
                    cursor = end + 2
                continue
            if char == "/" and regex_allowed(tokens):
                regex_start = cursor
                cursor += 1
                escaped = False
                in_class = False
                closed = False
                while cursor < len(value):
                    current = value[cursor]
                    if escaped:
                        escaped = False
                    elif current == "\\":
                        escaped = True
                    elif current == "[":
                        in_class = True
                    elif current == "]" and in_class:
                        in_class = False
                    elif current == "/" and not in_class:
                        cursor += 1
                        while cursor < len(value) and value[cursor].isalpha():
                            cursor += 1
                        closed = True
                        break
                    elif current in "\r\n":
                        break
                    cursor += 1
                if not closed:
                    ambiguous = ambiguous or marker(value[regex_start:cursor])
                tokens.append(("barrier", ""))
                continue
            if identifier_start(char) or value.startswith("\\u", cursor):
                decoded = []
                malformed = False
                first = True
                while cursor < len(value):
                    current = value[cursor]
                    if current == "\\":
                        part, following, valid = identifier_escape(cursor)
                        allowed = (identifier_start(part) if first else
                                   identifier_part(part)) if valid else False
                        if not valid or not allowed:
                            malformed = True
                            cursor = max(cursor + 1, following)
                            break
                    else:
                        allowed = (identifier_start(current) if first else
                                   identifier_part(current))
                        if not allowed:
                            break
                        part = current
                        following = cursor + 1
                    decoded.append(part)
                    cursor = following
                    first = False
                tokens.append(("bad_id" if malformed else "id",
                               "".join(decoded)))
                continue
            if stop_brace and char == "{":
                brace_depth += 1
            elif stop_brace and char == "}":
                brace_depth -= 1
            tokens.append(("punct", char))
            cursor += 1
        return tokens, cursor, ambiguous, not stop_brace

    tokens, _cursor, ambiguous, _closed = scan()
    if ambiguous:
        return True

    def static_bracket(index):
        if index >= len(tokens) or tokens[index] != ("punct", "["):
            return None, index, False
        cursor = index + 1
        if cursor >= len(tokens) or tokens[cursor][0] != "str":
            return None, index, False
        result = tokens[cursor][1]
        cursor += 1
        while (cursor + 1 < len(tokens) and
               tokens[cursor] == ("punct", "+") and
               tokens[cursor + 1][0] == "str"):
            result += tokens[cursor + 1][1]
            cursor += 2
        if cursor >= len(tokens):
            return result, cursor, True
        if tokens[cursor] != ("punct", "]"):
            return None, index, False
        return result, cursor + 1, False

    def path_state(parts):
        if not parts:
            return None
        first = parts[0].casefold()
        if first in CODEX_COLLAB_NATIVE_TOOL_NAMES:
            return "known"
        for prefix in ("multi_agent_v1__", "collaboration__"):
            if first.startswith(prefix):
                return ("known" if first[len(prefix):] in
                        CODEX_COLLAB_NATIVE_TOOL_NAMES else "unknown")
        if first == "collaboration":
            if len(parts) == 1:
                return "namespace"
            return ("known" if parts[1].casefold() in
                    CODEX_COLLAB_NATIVE_TOOL_NAMES else "unknown")
        return None

    def direct_invocation(index):
        if (index and tokens[index - 1][0] == "id" and
                tokens[index - 1][1].casefold() == "function"):
            return False
        cursor = index + 1
        if (cursor + 2 < len(tokens) and
                tokens[cursor:cursor + 3] == [
                    ("punct", "?"), ("punct", "."), ("punct", "(")]):
            cursor += 2
        if cursor >= len(tokens) or tokens[cursor] != ("punct", "("):
            return False
        depth = 0
        while cursor < len(tokens):
            if tokens[cursor] == ("punct", "("):
                depth += 1
            elif tokens[cursor] == ("punct", ")"):
                depth -= 1
                if depth == 0:
                    cursor += 1
                    return (cursor >= len(tokens) or
                            tokens[cursor] != ("punct", "{"))
            cursor += 1
        return True

    def optional_operator(index, following):
        return (index + 2 < len(tokens) and
                tokens[index] == ("punct", "?") and
                tokens[index + 1] == ("punct", ".") and
                tokens[index + 2] == ("punct", following))

    def call_at(index):
        return (index < len(tokens) and
                (tokens[index] == ("punct", "(") or
                 optional_operator(index, "(")))

    def tools_path(index):
        if (index >= len(tokens) or tokens[index][0] != "id" or
                tokens[index][1].casefold() != "tools"):
            return False, [], None, index, False
        cursor = index + 1
        parts = []
        incomplete = False
        while cursor < len(tokens):
            optional = (cursor + 1 < len(tokens) and
                        tokens[cursor:cursor + 2] == [
                            ("punct", "?"), ("punct", ".")])
            if tokens[cursor] == ("punct", ".") or optional:
                following = cursor + (2 if optional else 1)
                if (following < len(tokens) and
                        tokens[following] == ("punct", "[")):
                    part, following, truncated = static_bracket(following)
                    if part is None:
                        incomplete = True
                        break
                    parts.append(part)
                    cursor = following
                    incomplete = incomplete or truncated
                    if truncated:
                        break
                    continue
                if (following >= len(tokens) or
                        tokens[following][0] not in {"id", "bad_id"}):
                    incomplete = True
                    break
                parts.append(tokens[following][1])
                incomplete = incomplete or tokens[following][0] == "bad_id"
                cursor = following + 1
                if incomplete:
                    break
                continue
            part, following, truncated = static_bracket(cursor)
            if part is None:
                break
            parts.append(part)
            cursor = following
            incomplete = incomplete or truncated
            if truncated:
                break
        return True, parts, path_state(parts), cursor, incomplete

    def hoisted_function_bindings():
        bindings = {None: []}
        active_scopes = [None]
        declaration_boundaries = {
            ("punct", "{"), ("punct", "}"), ("punct", ";")}
        for cursor, token in enumerate(tokens):
            if token == ("punct", "{"):
                active_scopes.append(cursor)
                continue
            if token == ("punct", "}"):
                if len(active_scopes) > 1:
                    active_scopes.pop()
                continue
            if (token[0] == "id" and token[1].casefold() == "function" and
                    cursor + 1 < len(tokens) and
                    tokens[cursor + 1][0] == "id" and
                    (cursor == 0 or
                     tokens[cursor - 1] in declaration_boundaries)):
                bindings.setdefault(active_scopes[-1], []).append(
                    tokens[cursor + 1][1])
        return bindings

    hoisted_functions = hoisted_function_bindings()
    scopes = [{name.casefold(): False
               for name in hoisted_functions.get(None, ())}]
    function_scopes = [True]

    def bind(name, collaboration, declaration="let"):
        target = len(scopes) - 1
        if declaration == "var":
            for candidate in range(len(scopes) - 1, -1, -1):
                if function_scopes[candidate]:
                    target = candidate
                    break
        scopes[target][name.casefold()] = bool(collaboration)

    def assign(name, collaboration):
        folded = name.casefold()
        for scope in reversed(scopes):
            if folded in scope:
                scope[folded] = bool(collaboration)
                return
        scopes[-1][folded] = bool(collaboration)

    def binding_state(name):
        folded = name.casefold()
        for scope in reversed(scopes):
            if folded in scope:
                return scope[folded]
        return None

    def assignment_operator(index):
        if index >= len(tokens) or tokens[index] != ("punct", "="):
            return False
        before = tokens[index - 1] if index else None
        after = tokens[index + 1] if index + 1 < len(tokens) else None
        return (before != ("punct", "=") and
                after not in {("punct", "="), ("punct", ">")})

    def source_state(index):
        found, _parts, state, _cursor, incomplete = tools_path(index)
        if not found:
            return False, False
        if state == "unknown" or (state and incomplete):
            return False, True
        return state == "known", False

    def destructuring(index):
        opening = index + 1
        if (opening >= len(tokens) or
                tokens[opening] != ("punct", "{")):
            return None
        cursor = opening + 1
        entries = []
        while cursor < len(tokens) and tokens[cursor] != ("punct", "}"):
            if tokens[cursor] == ("punct", ","):
                cursor += 1
                continue
            if tokens[cursor][0] != "id":
                return None
            key = tokens[cursor][1]
            alias = key
            cursor += 1
            if cursor < len(tokens) and tokens[cursor] == ("punct", ":"):
                cursor += 1
                if cursor >= len(tokens) or tokens[cursor][0] != "id":
                    return None
                alias = tokens[cursor][1]
                cursor += 1
            entries.append((key, alias))
            if (cursor < len(tokens) and
                    tokens[cursor] not in {
                        ("punct", ","), ("punct", "}")}):
                return None
        if cursor >= len(tokens):
            return None
        closing = cursor
        equals = closing + 1
        if not assignment_operator(equals):
            return entries, None, False
        found, parts, state, _end, incomplete = tools_path(equals + 1)
        if not found:
            return entries, None, False
        if state == "unknown" or (state and incomplete):
            return entries, None, True
        return entries, parts, False

    def function_parameters(brace):
        arrow = False
        close = brace - 1
        if (brace >= 3 and tokens[brace - 2:brace] == [
                ("punct", "="), ("punct", ">")]):
            arrow = True
            close = brace - 3
            if close >= 0 and tokens[close][0] == "id":
                return [tokens[close][1]]
        if close < 0 or tokens[close] != ("punct", ")"):
            return None
        depth = 1
        opening = close - 1
        while opening >= 0:
            if tokens[opening] == ("punct", ")"):
                depth += 1
            elif tokens[opening] == ("punct", "("):
                depth -= 1
                if depth == 0:
                    break
            opening -= 1
        if opening < 0:
            return None
        function = (
            opening >= 1 and tokens[opening - 1][0] == "id" and
            tokens[opening - 1][1].casefold() == "function") or (
            opening >= 2 and tokens[opening - 2][0] == "id" and
            tokens[opening - 2][1].casefold() == "function")
        catch = (opening >= 1 and tokens[opening - 1][0] == "id" and
                 tokens[opening - 1][1].casefold() == "catch")
        if catch:
            if (close == opening + 2 and
                    tokens[opening + 1][0] == "id"):
                return [tokens[opening + 1][1]]
            return None
        if not arrow and not function and not catch:
            return None
        parameters = []
        cursor = opening + 1
        while cursor < close:
            if tokens[cursor][0] == "id":
                parameters.append(tokens[cursor][1])
            cursor += 1
        return parameters

    def expression_arrow_scopes():
        starts = {}
        for equals in range(len(tokens) - 1):
            if tokens[equals:equals + 2] != [
                    ("punct", "="), ("punct", ">")]:
                continue
            before = equals - 1
            parameters = None
            if before >= 0 and tokens[before][0] == "id":
                parameters = [tokens[before][1]]
            elif before >= 0 and tokens[before] == ("punct", ")"):
                depth = 1
                opening = before - 1
                while opening >= 0:
                    if tokens[opening] == ("punct", ")"):
                        depth += 1
                    elif tokens[opening] == ("punct", "("):
                        depth -= 1
                        if depth == 0:
                            break
                    opening -= 1
                if opening >= 0:
                    parameters = []
                    expect_identifier = True
                    for cursor in range(opening + 1, before):
                        token = tokens[cursor]
                        if expect_identifier and token[0] == "id":
                            parameters.append(token[1])
                            expect_identifier = False
                        elif (not expect_identifier and
                              token == ("punct", ",")):
                            expect_identifier = True
                        else:
                            parameters = None
                            break
                    if expect_identifier and parameters:
                        parameters = None
            body = equals + 2
            if (parameters is None or body >= len(tokens) or
                    tokens[body] == ("punct", "{")):
                continue
            delimiters = []
            cursor = body
            valid = True
            pairs = {"(": ")", "[": "]", "{": "}"}
            while cursor < len(tokens):
                token = tokens[cursor]
                if token[0] == "punct" and token[1] in pairs:
                    delimiters.append(pairs[token[1]])
                elif token[0] == "punct" and token[1] in ")]}":
                    if delimiters and delimiters[-1] == token[1]:
                        delimiters.pop()
                    elif not delimiters:
                        break
                    else:
                        valid = False
                        break
                elif (not delimiters and token in {
                        ("punct", ";"), ("punct", ",")}):
                    break
                cursor += 1
            if delimiters:
                valid = False
            if valid:
                starts.setdefault(body, []).append((cursor, parameters))
        return starts

    arrow_starts = expression_arrow_scopes()
    arrow_ends = []

    index = 0
    while index < len(tokens):
        while arrow_ends and arrow_ends[-1] == index:
            scopes.pop()
            function_scopes.pop()
            arrow_ends.pop()
        for end, parameters in arrow_starts.get(index, []):
            scopes.append({})
            function_scopes.append(True)
            arrow_ends.append(end)
            for parameter in parameters:
                bind(parameter, False)
        token = tokens[index]
        if token == ("punct", "{"):
            parameters = function_parameters(index)
            scopes.append({name.casefold(): False
                           for name in hoisted_functions.get(index, ())})
            function_scopes.append(parameters is not None)
            for parameter in parameters or []:
                bind(parameter, False)
            index += 1
            continue
        if token == ("punct", "}"):
            if len(scopes) > 1:
                scopes.pop()
                function_scopes.pop()
            index += 1
            continue
        if (token[0] == "id" and
                token[1].casefold() in {"function", "class"} and
                index + 1 < len(tokens) and tokens[index + 1][0] == "id"):
            bind(tokens[index + 1][1], False)
        if token[0] == "id" and token[1].casefold() in {
                "const", "let", "var"}:
            observed = destructuring(index)
            if observed is not None:
                entries, base_parts, uncertain = observed
                if uncertain:
                    return True
                for key, alias in entries:
                    state = (path_state(base_parts + [key])
                             if base_parts is not None else None)
                    if state == "unknown":
                        return True
                    bind(alias, state == "known", token[1].casefold())
            elif index + 1 < len(tokens) and tokens[index + 1][0] == "id":
                name = tokens[index + 1][1]
                collaboration = False
                uncertain = False
                if assignment_operator(index + 2):
                    collaboration, uncertain = source_state(index + 3)
                if uncertain:
                    return True
                bind(name, collaboration, token[1].casefold())
        if (token[0] == "id" and index + 1 < len(tokens) and
                assignment_operator(index + 1) and
                not (index and tokens[index - 1] in {
                    ("punct", "."), ("punct", "]")})):
            collaboration, uncertain = source_state(index + 2)
            if uncertain:
                return True
            assign(token[1], collaboration)
        found, _parts, state, cursor, incomplete = tools_path(index)
        if found:
            if state and call_at(cursor):
                return True
            if state == "unknown" or (state and incomplete):
                return True
        if token[0] == "bad_id":
            if (path_state([token[1]]) is not None or
                    any(item[0] == "id" and path_state([item[1]]) is not None
                        for item in tokens[index + 1:index + 5])):
                return True
            index += 1
            continue
        if token[0] == "id":
            name = token[1].casefold()
            if not (index and tokens[index - 1] in {
                    ("punct", "."), ("punct", "]")}):
                direct_state = path_state([name])
                called = direct_invocation(index)
                binding = binding_state(name)
                if called and binding is not None:
                    if binding:
                        return True
                elif direct_state and called:
                    return True
                if direct_state == "unknown" and binding is not False:
                    return True
        index += 1
    return False


def _codex_native_output_objects(value):
    texts = []
    if type(value) is str:
        texts.append(value)
    elif isinstance(value, list):
        for item in value:
            if (isinstance(item, dict) and
                    item.get("type") in ("input_text", "output_text") and
                    type(item.get("text")) is str):
                texts.append(item["text"])
    for text in texts:
        candidate = text.strip()
        if (not candidate.startswith("{") or
                not candidate.endswith("}") or
                len(candidate.encode("utf-8")) > 1024 * 1024):
            continue

        def unique(pairs):
            result = {}
            for key, item in pairs:
                if key in result:
                    raise ValueError("duplicate completion key")
                result[key] = item
            return result

        try:
            observed = json.loads(candidate, object_pairs_hook=unique)
        except (ValueError, json.JSONDecodeError, RecursionError, MemoryError):
            continue
        if isinstance(observed, dict):
            yield observed


def _codex_native_output_has_collaboration(value):
    for candidate in _codex_native_output_objects(value):
        keys = set(candidate)
        if (type(candidate.get("agent_id")) is str and
                candidate["agent_id"] and
                keys <= {"agent_id", "nickname"}):
            return True
        statuses = candidate.get("status")
        if (isinstance(statuses, dict) and
                keys <= {"status", "timed_out"} and
                any(type(child) is str and
                    CODEX_COLLAB_NATIVE_CHILD_ID_PATTERN.fullmatch(child)
                    for child in statuses)):
            return True
    return False


def _codex_native_message_has_collaboration(payload):
    if payload.get("role") != "user" or not isinstance(
            payload.get("content"), list):
        return False
    return any(
        isinstance(item, dict) and
        item.get("type") in ("input_text", "output_text") and
        type(item.get("text")) is str and
        "<subagent_notification>" in item["text"].casefold()
        for item in payload["content"])


def _codex_native_collaboration_present(rows):
    for row in rows:
        if row.get("type") != "response_item":
            continue
        payload = row.get("payload")
        if not isinstance(payload, dict):
            continue
        kind = payload.get("type")
        folded_kind = kind.casefold() if type(kind) is str else ""
        if folded_kind in ("custom_tool_call", "function_call"):
            name = payload.get("name")
            if _codex_native_collaboration_name(name):
                return True
            if (type(name) is str and name.casefold() in ("exec", "functions.exec")
                    and (_codex_native_exec_has_collaboration(
                        payload.get("input")) or
                         _codex_native_exec_has_collaboration(
                             payload.get("arguments")))):
                return True
        elif folded_kind in (
                "custom_tool_call_output", "function_call_output"):
            if _codex_native_output_has_collaboration(payload.get("output")):
                return True
        elif folded_kind == "message":
            if _codex_native_message_has_collaboration(payload):
                return True
    return False


def _validate_native_session(stdout, session, expected_host, binding,
                             stdout_binding, actions, profile, process):
    _expect(expected_host in {"codex", "claude"},
            "native session host invalid")
    _expect(type(stdout) is bytes and type(session) is bytes,
            "native session capture type invalid")
    _expect(isinstance(stdout_binding, dict) and
            isinstance(actions, list) and
            all(isinstance(action, dict) and
                type(action.get("id")) is str and action["id"]
                for action in actions) and
            isinstance(process, dict),
            "native session context malformed")
    action_ids = [action["id"] for action in actions]
    _expect(len(action_ids) == len(set(action_ids)),
            "native session action identity duplicated")
    repo_policy = _codex_native_repo_policy(profile)
    _expect(repo_policy is not None,
            "native session profile repository invalid")
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
            _expect(type(row["type"]) is str,
                    owner + " row type invalid")
            contract = CODEX_NATIVE_PAYLOAD_FIELDS.get(row["type"])
            _expect(contract is not None, owner + " unsupported row type")
            _closed_fields(payload, contract[0], contract[1],
                           owner + " payload")
            _expect(_parse_codex_session_time(row["timestamp"]) is not None,
                    owner + " timestamp invalid")
        _expect(not _codex_native_collaboration_present(rows),
                "Codex native session contains unbound collaboration evidence")
        allowed = {"thread_id", "stdout_turn_ordinal", "turn_id",
                   "native_turn_id"}
        _expect(set(binding) <= allowed and
                {"thread_id", "stdout_turn_ordinal", "native_turn_id"} <=
                set(binding) and
                type(binding["stdout_turn_ordinal"]) is int and
                binding["stdout_turn_ordinal"] == 1 and
                all(type(binding[key]) is str and bool(binding[key])
                    for key in set(binding) - {"stdout_turn_ordinal"}) and
                all(binding.get(key) == value
                    for key, value in stdout_binding.items()),
                "Codex terminal lineage binding invalid")
        metas = [(index, row) for index, row in enumerate(rows)
                 if row.get("type") == "session_meta"]
        turns = [(index, row) for index, row in enumerate(rows)
                 if row.get("type") == "turn_context"]
        _expect(len(metas) == 1 and len(turns) == 1 and
                isinstance(metas[0][1].get("payload"), dict) and
                isinstance(turns[0][1].get("payload"), dict),
                "Codex native session state invalid")
        meta_index, meta_record = metas[0]
        turn_index, turn_record = turns[0]
        meta, turn = meta_record["payload"], turn_record["payload"]
        root = repo_policy["lexical_root"]
        process_time = _parse_codex_session_time(process.get("started_at"))
        meta_payload_time = _parse_codex_session_time(meta.get("timestamp"))
        meta_time = _parse_codex_session_time(meta_record.get("timestamp"))
        turn_time = _parse_codex_session_time(turn_record.get("timestamp"))
        case_sensitive = repo_policy["case_sensitive"]
        window_end = (process_time + timedelta(
            seconds=CODEX_SESSION_START_WINDOW_SECONDS)
            if process_time is not None else None)
        _expect(meta.get("id") == binding["thread_id"] and
                meta.get("session_id") == binding["thread_id"] and
                _codex_same_path(
                    meta.get("cwd"), root, case_sensitive) and
                _codex_same_path(
                    turn.get("cwd"), root, case_sensitive) and
                turn.get("turn_id") == binding["native_turn_id"] and
                _codex_same_path(
                    process.get("cwd"), root, case_sensitive) and
                type(process.get("requested_model")) is str and
                bool(process["requested_model"]) and
                type(turn.get("model")) is str and bool(turn["model"]) and
                turn.get("model") == process["requested_model"] and
                meta_index < turn_index and
                process_time is not None and
                meta_payload_time is not None and meta_time is not None and
                turn_time is not None and
                process_time <= meta_payload_time <= meta_time <= window_end and
                process_time <= turn_time <= window_end,
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
        for key in (
                "action_type", "command", "path", "paths", "tool",
                "sender_thread_id", "prompt", "receiver_thread_ids"):
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
    if expected_host == "codex":
        _expect(not any(
            action.get("action_type") == "collab_tool_call"
            for action in actions),
            "formal-v2 unbound collaboration descendant evidence")


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
    collaboration_fields = {
        "tool", "sender_thread_id", "prompt", "receiver_thread_ids"}
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
        if action.get("action_type") == "collab_tool_call":
            _expect(keys == required | collaboration_fields,
                    owner + " collaboration fields invalid")
            tool = action["tool"]
            sender = action["sender_thread_id"]
            prompt = action["prompt"]
            receivers = action["receiver_thread_ids"]
            payload = action["payload"]
            _expect(action["state"] == "COMPLETED" and
                    action["effect"] == "safe-other" and
                    action["classification"] == "not-content-read" and
                    type(action["invocation_ordinal"]) is int and
                    action["completion_ordinal"] > action["invocation_ordinal"] and
                    tool in ("spawn_agent", "wait") and
                    type(sender) is str and bool(sender) and
                    isinstance(receivers, list) and len(receivers) == 1 and
                    type(receivers[0]) is str and bool(receivers[0]) and
                    receivers[0] != sender and
                    type(payload) in (list, tuple) and len(payload) == 3 and
                    payload[0] == tool and payload[1] == sender and
                    payload[2] == prompt and
                    ((tool == "spawn_agent" and
                      type(prompt) is str and bool(prompt)) or
                     (tool == "wait" and prompt is None)),
                    owner + " collaboration semantics invalid")
        else:
            _expect(not (keys & collaboration_fields),
                    owner + " has collaboration-only field")


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
            trace, raw_actions, host_checks, _role_texts(events),
            _exact_assistant_texts(events))


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


def _exact_assistant_texts(events):
    """Independently retain one host-designated final event exactly."""
    responses = []
    for _ordinal, event in _raw_json_lines(events, "bundle events"):
        if (event.get("kind") != "marker" or
                event.get("role") != "assistant"):
            continue
        content = event.get("content")
        if type(content) is not str:
            return {"assistant": ""}
        responses.append(content)
    return {"assistant": responses[0] if len(responses) == 1 else ""}


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


def _artifact_object(fixture, artifacts):
    policy = fixture.get("artifact_rules")
    if not isinstance(policy, dict):
        return None
    path = policy.get("file")
    _expect(type(path) is str and path in artifacts,
            "required host-observation artifact missing")
    return _decode_json(
        artifacts[path], "host-observation artifact",
        "host-observation artifact malformed", True)


def _matrix_acceptance(fixture, property_name, texts, artifact_obj):
    """Independent implementation of matrix-only proposition acceptance."""
    contract = fixture.get("matrix_acceptance")
    if contract is None:
        return None
    _expect(
        type(contract) is dict and set(contract) == {"schema", "properties"} and
        contract.get("schema") in {
            "implementaudit-candidate-matrix-acceptance-v1",
            "implementaudit-candidate-matrix-acceptance-v2",
        } and
        type(contract.get("properties")) is dict,
        "matrix acceptance contract malformed")
    proposition = contract["properties"].get(property_name)
    if proposition is None:
        return None
    _expect(type(proposition) is str and bool(proposition),
            "matrix proposition identity malformed")
    text = texts.get("assistant", "")
    _expect(type(text) is str, "matrix assistant text malformed")
    folded = text.casefold()

    if contract["schema"] == "implementaudit-candidate-matrix-acceptance-v1":
        _expect(fixture.get("id") not in {"B1", "E2a", "E3", "E7", "E9"},
                "structured matrix cell requires acceptance v2")
        if proposition == "shape-not-behavior":
            passed = (
                bool(re.search(
                    r"\b(array|strings?|shape|type|structur(?:e|al))\b",
                    folded))
                and bool(re.search(r"\bbehavio(?:u)?r(?:al)?\b", folded))
                and bool(re.search(
                    r"\b(does not|doesn.t|cannot|can.t|fails? to)\b.{0,80}"
                    r"\b(establish|prove|verify|test|demonstrate)\b", folded))
                and bool(re.search(
                    r"\b(validator|check)\b.{0,100}"
                    r"\b(underpowered|mis-?scoped|inadequate|too weak|weaker)\b|"
                    r"\b(underpowered|mis-?scoped|inadequate|too weak|weaker)\b"
                    r".{0,100}\b(validator|check)\b|"
                    r"\b(only|narrow)\b.{0,80}"
                    r"\b(array|strings?|shape|structur(?:e|al)|condition)\b",
                    folded)))
        elif proposition == "current-correct":
            passed = bool(re.search(
                r"\bcurrent\b.{0,50}\b(answer|output|result)\b.{0,30}"
                r"\b(is|remains?)\b.{0,20}\bcorrect\b|"
                r"\bcurrent\b.{0,50}\bcorrect\b", folded))
        elif proposition == "perturbation-pathway-inadequate":
            passed = (
                type(artifact_obj) is dict and
                (artifact_obj.get("p1_verdict") == "reject" or
                 artifact_obj.get("p2_verdict") == "accept") and
                bool(re.search(r"\bp1\b.{0,80}\bfalse negative\b", folded)) and
                bool(re.search(r"\bp2\b.{0,80}\bfalse positive\b", folded)) and
                bool(re.search(
                    r"\b(validator|rule|pathway)\b.{0,100}"
                    r"\b(invalid|inadequate|unreliable|untrustworthy|"
                    r"cannot be trusted|not truth-connected)\b", folded)))
        else:
            raise EvidenceInvalid(
                f"unsupported free-text matrix proposition: {proposition!r}")
        return passed, f"matrix-proposition:{proposition}"

    expected_cell = fixture.get("id")
    _expect(expected_cell in {"B1", "E2a", "E3", "E7", "E9"},
            "matrix envelope cell invalid")

    document = None
    source = text[:-1] if text.endswith("\n") else text
    if (source and "\r" not in source and not source.startswith("\n") and
            not source.endswith("\n")):
        rows = source.split("\n")
        header_valid = (
            len(rows) >= 4 and all(rows) and
            rows[0] == "MATRIX_EVIDENCE_V1_BEGIN" and
            rows[-1] == "MATRIX_EVIDENCE_V1_END" and
            rows.count("MATRIX_EVIDENCE_V1_BEGIN") == 1 and
            rows.count("MATRIX_EVIDENCE_V1_END") == 1 and
            rows[1] == f"CELL={expected_cell}" and
            len([row for row in rows if row.startswith("CELL=")]) == 1)
        body = rows[2:-1] if header_valid else []
        if expected_cell == "B1" and body == [
                "RESUME_FROM=PHASE_3", "PHASE_1_RESTART=false",
                "TERMINAL=AUDIT_COMPLETE"]:
            document = {
                "resume_from": "PHASE_3", "phase_1_restart": False,
                "terminal": "AUDIT_COMPLETE",
            }
        elif expected_cell == "E2a" and body == [
                "FAILURE_ORIGIN=transport-infrastructure",
                "PRODUCER_SOURCE_CHANGE=false"]:
            document = {
                "failure_origin": "transport-infrastructure",
                "producer_source_change": False,
            }
        elif expected_cell == "E3" and len(body) >= 6:
            candidate_re = re.compile(
                r"CAUSE_CANDIDATE id=(truncated-write|encoding-corruption|"
                r"upstream-schema-drift) status=unresolved\Z")
            residual_re = re.compile(
                r"RESIDUAL_DISPOSITION candidate=(truncated-write|"
                r"encoding-corruption|upstream-schema-drift) disposition="
                r"(deferred|transferred|owner-assigned|risk-accepted|"
                r"unresolved|validated-resolved)\Z")
            candidate_order = []
            residual_map = {}
            in_residuals = False
            middle_valid = (
                body[0] == "CONTAINMENT=quarantine" and
                body[-1] == "ROOT_CAUSE_STATUS=unresolved")
            for row in body[1:-1]:
                candidate_match = candidate_re.fullmatch(row)
                residual_match = residual_re.fullmatch(row)
                if candidate_match and not in_residuals:
                    name = candidate_match.group(1)
                    if name in candidate_order:
                        middle_valid = False
                    candidate_order.append(name)
                elif residual_match:
                    in_residuals = True
                    name, state = residual_match.groups()
                    if name in residual_map:
                        middle_valid = False
                    residual_map[name] = state
                else:
                    middle_valid = False
            candidate_set = set(candidate_order)
            if (middle_valid and len(candidate_set) >= 2 and
                    set(residual_map) == candidate_set):
                document = {
                    "containment": "quarantine",
                    "candidates": candidate_set,
                    "residuals": residual_map,
                    "root_cause_status": "unresolved",
                }
        elif expected_cell == "E7" and len(body) in {5, 6}:
            ordered_names = [
                "LIFT_DECISION", "LIFT_REASON", "LIFT_DESTINATION",
                "ACTIVATION_STATUS",
            ]
            parsed = {}
            order_valid = True
            for index, name in enumerate(ordered_names):
                prefix = name + "="
                if index >= len(body) or not body[index].startswith(prefix):
                    order_valid = False
                    break
                parsed[name] = body[index][len(prefix):]
            mechanical_destinations = {
                "checker", "checker-or-deterministic-test",
                "deterministic-test",
            }
            allowed_destinations = {
                "no-lift", "current-run-only", "project-docs",
                "project-agent-instructions", "checker",
                "checker-or-deterministic-test", "deterministic-test",
                "template", "reusable-skill-or-command",
                "implementaudit-product-issue",
                "owner-authorized-cross-project-continuity",
            }
            insufficient = {
                "cheap-to-redo", "cheap-to-redo-by-hand", "easy-to-redo",
                "easy-to-redo-by-hand", "trivial-to-redo-by-hand",
            }
            decision = parsed.get("LIFT_DECISION")
            reason = parsed.get("LIFT_REASON", "")
            destination = parsed.get("LIFT_DESTINATION")
            activation = parsed.get("ACTIVATION_STATUS")
            mechanical = destination in mechanical_destinations
            evidence = None
            if mechanical:
                evidence_valid = (
                    len(body) == 6 and
                    body[4].startswith("ACTIVATION_EVIDENCE=") and
                    bool(re.fullmatch(
                        r"[a-z0-9]+(?:[._/-][a-z0-9]+)*",
                        body[4].split("=", 1)[1])) and
                    body[5] == "RECURRENCE_PREVENTED=false")
                if evidence_valid:
                    evidence = body[4].split("=", 1)[1]
            else:
                evidence_valid = (
                    len(body) == 5 and
                    body[4] == "RECURRENCE_PREVENTED=false")
            semantic_valid = (
                order_valid and decision in {"lift", "no-lift"} and
                bool(re.fullmatch(
                    r"[a-z0-9]+(?:-[a-z0-9]+)*", reason)) and
                len(reason) <= 128 and reason not in insufficient and
                destination in allowed_destinations and
                ((decision == "no-lift") == (destination == "no-lift")) and
                ((mechanical and activation == "observed-pass") or
                 (not mechanical and activation == "not-required")) and
                evidence_valid)
            if semantic_valid:
                document = {
                    "decision": decision, "reason": reason,
                    "destination": destination, "activation": activation,
                    "activation_evidence": evidence,
                    "recurrence_prevented": False,
                }
        elif expected_cell == "E9" and body == [
                "MECHANICAL_CLAIM=contradicted",
                "ABNORMALITY=evidence-mismatch",
                "BLOCK_SCOPE=dependent-actions-only",
                "OWNER_ACCEPTANCE=risk-accepted",
                "OWNER_JUDGMENT=preserved-verbatim",
                "AUDIT_RESTART=false"]:
            document = {
                "mechanical_claim": "contradicted",
                "abnormality": "evidence-mismatch",
                "block_scope": "dependent-actions-only",
                "owner_acceptance": "risk-accepted",
                "owner_judgment": "preserved-verbatim",
                "audit_restart": False,
            }

    if document is None:
        passed = False
    elif proposition == "resume-phase3":
        passed = document.get("resume_from") == "PHASE_3"
    elif proposition == "no-phase1-restart":
        passed = document.get("phase_1_restart") is False
    elif proposition == "audit-complete-exclusive":
        passed = document.get("terminal") == "AUDIT_COMPLETE"
    elif proposition == "containment-quarantine":
        passed = document.get("containment") == "quarantine"
    elif proposition.startswith("supported-candidates:"):
        allowed = set(proposition.split(":", 1)[1].split(","))
        passed = (len(document.get("candidates", set())) >= 2 and
                  document.get("candidates", set()) <= allowed)
    elif proposition == "candidate-residual-dispositions":
        candidate_set = document.get("candidates", set())
        residual_map = document.get("residuals", {})
        passed = (len(candidate_set) >= 2 and
                  set(residual_map) == candidate_set)
    elif proposition == "root-cause-unresolved":
        passed = document.get("root_cause_status") == "unresolved"
    elif proposition == "transport-infrastructure-origin":
        passed = document.get("failure_origin") == \
            "transport-infrastructure"
    elif proposition == "producer-source-unchanged":
        passed = document.get("producer_source_change") is False
    elif proposition == "lesson-lift-record":
        passed = all(document.get(key) for key in (
            "decision", "reason", "destination"))
    elif proposition == "lesson-lift-activation":
        if document.get("destination") in {
                "checker", "checker-or-deterministic-test",
                "deterministic-test"}:
            passed = (document.get("activation") == "observed-pass" and
                      bool(document.get("activation_evidence")))
        else:
            passed = document.get("activation") == "not-required"
    elif proposition == "no-prevention-claim":
        passed = document.get("recurrence_prevented") is False
    elif proposition == "mechanical-claim-contradicted":
        passed = (document.get("mechanical_claim") == "contradicted" and
                  document.get("block_scope") == "dependent-actions-only")
    elif proposition == "evidence-mismatch-named":
        passed = document.get("abnormality") == "evidence-mismatch"
    elif proposition == "owner-judgment-preserved":
        passed = (document.get("owner_acceptance") == "risk-accepted" and
                  document.get("owner_judgment") == "preserved-verbatim")
    elif proposition == "audit-not-restarted":
        passed = document.get("audit_restart") is False
    else:
        raise EvidenceInvalid(
            f"unsupported envelope matrix proposition: {proposition!r}")
    return passed, f"matrix-envelope-v1:{proposition}"


def _derive_properties(fixture, artifacts, after, changed, preimages, raw_actions,
                       host_checks, texts, exact_assistant_texts):
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
        matrix_contract = fixture.get("matrix_acceptance") or {}
        matrix_texts = (
            exact_assistant_texts
            if matrix_contract.get("schema") ==
            "implementaudit-candidate-matrix-acceptance-v2"
            else texts)
        matrix = _matrix_acceptance(
            fixture, name, matrix_texts,
            _artifact_object(fixture, artifacts))
        if matrix is not None:
            passed = matrix[0]
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
        _, readiness_raw = _load_launch_readiness(
            attempt, status, packet)
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
            readiness_raw, packet, freeze_sha)
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
         _trace, raw_actions, host_checks, texts, exact_assistant_texts) = \
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
            host_checks, texts, exact_assistant_texts)
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
                    "host-attestation.json", "launch-readiness.json",
                    "official-verdict.json",
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
            if (not pathlib.Path(row["path"]).is_absolute() and
                row["role"] not in EVALUATED_SURFACE_VIRTUAL_ROLES))
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
                           "host-attestation.json", "launch-readiness.json",
                           "official-verdict.json",
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
