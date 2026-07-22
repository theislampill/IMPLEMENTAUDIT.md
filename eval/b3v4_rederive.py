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


PLAN = [
    ("L", "candidate", 1), ("L", "control", 1),
    ("O", "control", 1), ("O", "candidate", 1),
    ("O", "candidate", 2), ("O", "control", 2),
    ("L", "control", 2), ("L", "candidate", 2),
    ("L", "control", 3), ("L", "candidate", 3),
    ("O", "candidate", 3), ("O", "control", 3),
]
FREEZE_FIELDS = {
    "schema", "campaign", "state", "foundation", "fixture", "artifacts",
    "candidate", "control", "configurations", "authorization", "seed",
    "repetitions_per_configuration_and_arm", "missions", "evidence_profiles",
    "result_composition", "attempt_policy", "acceptance_rule",
    "invalid_error_rule", "stop_conditions", "independent_rederiver",
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


class EvidenceInvalid(ValueError):
    """Retained evidence cannot support a campaign result."""


def _sha(data):
    return hashlib.sha256(data).hexdigest()


def _read_bytes(path):
    try:
        return pathlib.Path(path).read_bytes()
    except OSError as exc:
        raise EvidenceInvalid(f"missing evidence: {pathlib.Path(path).name}") from exc


def _read_json(path, owner):
    raw = _read_bytes(path)

    def unique(pairs):
        value = {}
        for key, item in pairs:
            if key in value:
                raise EvidenceInvalid(f"{owner} has duplicate key {key!r}")
            value[key] = item
        return value

    try:
        value = json.loads(raw.decode("utf-8"), object_pairs_hook=unique)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise EvidenceInvalid(f"{owner} is malformed") from exc
    if not isinstance(value, dict):
        raise EvidenceInvalid(f"{owner} must be an object")
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

    _expect(packet["seed"] == 20260718, "seed drift")
    _expect(packet["repetitions_per_configuration_and_arm"] == 3,
            "repetition count drift")
    missions = packet["missions"]
    _expect(isinstance(missions, list) and len(missions) == len(PLAN),
            "fixed 12-mission order drift")
    for index, (mission, planned) in enumerate(zip(missions, PLAN)):
        mission = _exact_fields(mission, {"index", "config", "arm", "rep"},
                                f"mission {index}")
        _expect(type(mission["index"]) is int and mission["index"] == index and
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


def _canonical_snapshot_hash(value):
    body = {key: item for key, item in value.items()
            if key not in ("snapshot_sha256", "changed_files", "unauthorized")}
    return _sha(json.dumps(body, sort_keys=True).encode("utf-8"))


def _validate_snapshot(value, owner):
    required = {"schema", "head_commit", "head_tree", "index_tree", "staged",
                "unstaged", "untracked", "tracked_diff_sha256",
                "snapshot_sha256", "worktree_files"}
    _expect(required <= set(value), f"{owner} fields incomplete")
    _expect(value["schema"] == "implementaudit-repo-snapshot-v2",
            f"{owner} schema invalid")
    _expect(_canonical_snapshot_hash(value) == value["snapshot_sha256"],
            f"{owner} internal hash invalid")
    for key in ("head_commit", "head_tree", "index_tree"):
        _expect(bool(HEX40.fullmatch(str(value[key]))),
                f"{owner} {key} invalid")
    for key in ("staged", "unstaged"):
        _expect(isinstance(value[key], list) and
                all(isinstance(path, str) for path in value[key]),
                f"{owner} {key} invalid")
    for key in ("untracked", "worktree_files"):
        _expect(isinstance(value[key], dict), f"{owner} {key} invalid")
    for rel, entry in value["worktree_files"].items():
        rel = _safe_rel(rel, owner)
        _expect(rel.split("/")[0].lower() != ".git",
                f"{owner} Git administrative identity invalid")
        _expect(isinstance(entry, dict), f"{owner} file identity invalid")
        if entry.get("type") == "file":
            _expect(set(entry) == {"type", "sha256"} and
                    bool(HEX64.fullmatch(str(entry.get("sha256")))),
                    f"{owner} file digest invalid")
        elif entry.get("type") == "symlink":
            _expect(set(entry) == {"type", "target_sha256"} and
                    bool(HEX64.fullmatch(str(entry.get("target_sha256")))),
                    f"{owner} symlink digest invalid")
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
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise EvidenceInvalid(f"{owner} line {ordinal} malformed") from exc
        _expect(isinstance(value, dict), f"{owner} line {ordinal} is not an object")
        rows.append((ordinal, value))
    _expect(rows, f"{owner} is empty")
    return rows


def _parse_codex_actions(raw):
    pending = {}
    actions = []
    reserved = set()
    for ordinal, event in _raw_json_lines(raw, "Codex raw stdout"):
        event_type = event.get("type")
        if event_type not in ("item.started", "item.completed"):
            continue
        item = event.get("item")
        _expect(isinstance(item, dict), "Codex raw item malformed")
        action_id = item.get("id")
        item_type = item.get("type")
        if item_type not in ("command_execution", "file_change"):
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
                          "effect": "command", "command": item["command"],
                          "invocation_ordinal": ordinal,
                          "completion_ordinal": None}
            elif item_type == "file_change":
                changes = item.get("changes")
                _expect(isinstance(changes, list) and all(
                    isinstance(change, dict) and
                    isinstance(change.get("path"), str) for change in changes),
                    "Codex raw file change malformed")
                action = {"id": action_id, "state": "PENDING",
                          "effect": "write",
                          "paths": [change["path"] for change in changes],
                          "invocation_ordinal": ordinal,
                          "completion_ordinal": None}
            pending[action_id] = action
            actions.append(action)
            continue
        action = pending.pop(action_id, None)
        _expect(action is not None, "Codex raw completion without invocation")
        if action["effect"] == "command":
            exit_code = item.get("exit_code")
            output = item.get("aggregated_output")
            _expect(type(exit_code) is int and isinstance(output, str) and
                    item.get("status") == ("completed" if exit_code == 0 else "failed"),
                    "Codex raw command completion contradictory")
            action.update({"state": "COMPLETED", "exit_code": exit_code,
                           "output": output, "completion_ordinal": ordinal})
        else:
            _expect(item.get("status") == "completed",
                    "Codex raw write completion invalid")
            action.update({"state": "COMPLETED", "completion_ordinal": ordinal})
    _expect(not pending and actions, "Codex raw action stream incomplete")
    return actions


def _parse_claude_actions(raw):
    pending = {}
    actions = []
    reserved = set()
    inventory_seen = False
    for ordinal, event in _raw_json_lines(raw, "Claude raw stdout"):
        if event.get("type") == "system" and event.get("subtype") == "init":
            _expect(not inventory_seen and isinstance(event.get("tools"), list),
                    "Claude raw tool inventory invalid")
            inventory_seen = True
            continue
        role = event.get("type")
        if role not in ("assistant", "user"):
            continue
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
                          "path": path, "inputs": inputs,
                          "command": inputs.get("command"),
                          "invocation_ordinal": ordinal,
                          "completion_ordinal": None}
                pending[action_id] = action
                actions.append(action)
            elif role == "user" and block.get("type") == "tool_result":
                action_id = block.get("tool_use_id")
                action = pending.pop(action_id, None)
                _expect(action is not None and block.get("is_error") is not True,
                        "Claude raw tool completion invalid")
                content = block.get("content")
                _expect(isinstance(content, str), "Claude raw tool result malformed")
                action.update({"state": "COMPLETED", "output": content,
                               "completion_ordinal": ordinal})
                if action["effect"] == "command":
                    action["exit_code"] = 0
    _expect(inventory_seen and not pending and actions,
            "Claude raw action stream incomplete")
    return actions


def _parse_raw_actions(raw, host):
    if host == "codex":
        return _parse_codex_actions(raw)
    if host == "claude":
        return _parse_claude_actions(raw)
    raise EvidenceInvalid("unsupported formal-v2 host")


def _validate_capture(artifacts, fixture_bytes, fixture, expected_host,
                      parent_kind):
    required = set(CAPTURE_FILES) | {"host-read-manifest.json",
                                     "run-intent.json", "process-started.json"}
    _expect(required <= set(artifacts), "formal-v2 capture incomplete")
    objects = {}
    json_names = [name for name in required if not name.endswith(".raw")]
    for name in json_names:
        try:
            value = json.loads(artifacts[name].decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise EvidenceInvalid(f"{name} malformed") from exc
        _expect(isinstance(value, dict), f"{name} must be an object")
        objects[name] = value
    manifest = objects["host-read-manifest.json"]
    _expect(manifest.get("schema") == "implementaudit-host-read-manifest-v1" and
            set(manifest.get("files", {})) == set(CAPTURE_FILES),
            "formal-v2 manifest invalid")
    actual = {name: _sha(artifacts[name]) for name in CAPTURE_FILES}
    _expect(manifest["files"] == actual, "formal-v2 manifest hash mismatch")
    terminal = objects["host-read-terminal.json"]
    _expect(terminal.get("schema") == "implementaudit-host-read-terminal-v1" and
            terminal.get("hashes") == {name: actual[name]
                                        for name in CAPTURE_FILES[:-1]},
            "formal-v2 terminal hash mismatch")
    _expect(terminal.get("host_terminal_kind") == parent_kind,
            "formal-v2 parent terminal mismatch")
    profile = objects["host-read-profile.json"]
    _expect(profile.get("schema") == "implementaudit-host-read-profile-v2" and
            profile.get("authority") == "mechanically-minted" and
            profile.get("host") == expected_host,
            "formal-v2 host profile invalid")
    _expect(terminal.get("profile_post_status") == "PASS" and
            terminal.get("normalized_host_status") == "PASS" and
            terminal.get("session_bound") is True and
            terminal.get("session_status") == "VALID",
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
    _expect(pre_spawn.get("schema") == "implementaudit-host-read-pre-spawn-v1" and
            pre_spawn.get("created_before_spawn") is True and
            all(pre_spawn.get(key) == value for key, value in expected_pre.items()),
            "formal-v2 pre-spawn custody invalid")
    _expect(artifacts["host-read-fixture.raw"] == fixture_bytes,
            "formal-v2 fixture bytes drift")
    intent = objects["run-intent.json"]
    replay = objects["host-read-replay-spec.json"]
    process = objects["process-started.json"]
    expected_checks = [{"key": spec["key"],
                        "reads": list(spec.get("reads") or []),
                        "write": spec.get("write")}
                       for spec in (fixture.get("host_checks") or {}).get("specs", [])
                       if spec.get("kind") == "path_access_order"]
    _expect(replay.get("schema") == "implementaudit-host-read-replay-spec-v1" and
            replay.get("mode") == "formal-v2" and
            replay.get("host") == expected_host and
            replay.get("checks") == expected_checks and
            replay.get("fixture_sha256") == _sha(fixture_bytes) and
            replay.get("run_intent_sha256") == _sha(artifacts["run-intent.json"]),
            "formal-v2 replay recipe invalid")
    _expect(intent.get("fixture_sha256") == _sha(fixture_bytes) and
            process.get("host_read_pre_spawn_sha256") ==
            actual["host-read-pre-spawn.json"],
            "formal-v2 parent custody chain invalid")
    trace = objects["host-tool-trace.json"]
    _expect(trace.get("schema") == "implementaudit-host-tool-trace-v2" and
            trace.get("invalid") is False and trace.get("host_status") == "PASS" and
            isinstance(trace.get("host_findings"), list) and
            not trace["host_findings"], "formal-v2 trace host state invalid")
    post = objects["host-read-post-probe.json"]
    for key in ("environment", "shell", "executables", "native_tools"):
        if key in profile and key in post:
            _expect(profile[key] == post[key], "formal-v2 post-probe drift")
    raw_actions = _parse_raw_actions(artifacts["host-stdout.raw"], expected_host)
    return objects["host-read-preimages.json"], trace, raw_actions


def _load_bundle(bundle, packet, mission, parent_terminal):
    manifest, _ = _read_json(bundle / "manifest.json", "bundle manifest")
    fixture_bytes = _read_bytes(bundle / "fixture.json")
    prompt = _read_bytes(bundle / "prompt.txt")
    events = _read_bytes(bundle / "events.jsonl")
    before, before_bytes = _read_json(bundle / "repo-before.json", "repo-before")
    after, after_bytes = _read_json(bundle / "repo-after.json", "repo-after")
    artifact_manifest, artifact_manifest_bytes = _read_json(
        bundle / "artifact-manifest.json", "artifact manifest")
    _expect(manifest.get("schema") == "implementaudit-eval-manifest-v2",
            "bundle manifest schema invalid")
    for name, data, key in (("fixture", fixture_bytes, "fixture_sha256"),
                            ("prompt", prompt, "prompt_sha256"),
                            ("events", events, "events_sha256"),
                            ("repo-before", before_bytes, "repo_before_sha256"),
                            ("repo-after", after_bytes, "repo_after_sha256"),
                            ("artifact-manifest", artifact_manifest_bytes,
                             "artifact_manifest_sha256")):
        _expect(manifest.get(key) == _sha(data), f"{name} hash mismatch")
    _expect(bool(events.strip()), "events evidence empty")
    try:
        fixture = json.loads(fixture_bytes.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise EvidenceInvalid("fixture malformed") from exc
    _expect(isinstance(fixture, dict) and fixture.get("id") == "B3-v3" and
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
    files = artifact_manifest.get("files")
    _expect(isinstance(files, dict) and files, "artifact manifest invalid")
    artifacts = {}
    for rel, digest in files.items():
        rel = _safe_rel(rel, "artifact")
        _expect(bool(HEX64.fullmatch(str(digest))), "artifact digest invalid")
        data = _read_bytes(bundle / "artifacts" / pathlib.PurePosixPath(rel))
        _expect(_sha(data) == digest, f"artifact hash mismatch: {rel}")
        artifacts[rel] = data
    expected_host = "codex" if mission["config"] == "L" else "claude"
    preimages, trace, raw_actions = _validate_capture(
        artifacts, fixture_bytes, fixture, expected_host,
        parent_terminal.get("kind"))
    changed = _changed_paths(before, after)
    return (manifest, fixture, artifacts, before, after, changed, preimages,
            trace, raw_actions)


def _attempt_name(mission):
    return (f"attempt-{mission['index']:03d}-{mission['config']}-"
            f"{mission['arm']}-r{mission['rep']}")


def _derive_properties(fixture, artifacts, after, changed, preimages, raw_actions):
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
            try:
                value = json.loads(artifacts[artifact].decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                raise EvidenceInvalid(f"JSON host-check input malformed: {rel}") from exc
            observations[key] = isinstance(value, dict) and all(
                value.get(field) == expected
                for field, expected in (spec.get("equals") or {}).items())
        else:
            raise EvidenceInvalid(f"unsupported frozen host check: {kind!r}")
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


def _rederive_attempt(packet, campaign_root, mission, freeze_sha):
    name = _attempt_name(mission)
    attempt = campaign_root / name
    try:
        status, _ = _read_json(attempt / "attempt-status.json", "attempt status")
        terminal, _ = _read_json(attempt / "attempt-terminal.json", "attempt terminal")
        _expect(status.get("schema") == "implementaudit-b3v4-attempt-status-v1" and
                status.get("campaign") == "b3v4-sol-r1" and
                status.get("freeze_sha256") == freeze_sha and
                status.get("mission") == mission and
                status.get("state") == "PREPARED_BEFORE_HOST_SPAWN",
                "attempt status identity invalid")
        _expect(terminal.get("schema") == "implementaudit-b3v4-attempt-terminal-v1" and
                terminal.get("campaign") == "b3v4-sol-r1" and
                terminal.get("mission_index") == mission["index"],
                "attempt terminal identity invalid")
        expected_model = packet["configurations"][mission["config"]][
            "model_resolved_required"]
        if terminal.get("resolved_model") != expected_model:
            return _invalid_row(mission, "SUBSTITUTION", "model substitution")
        if terminal.get("overall_status") in ("INVALID", "ERROR"):
            return _invalid_row(mission, terminal["overall_status"],
                                "campaign driver recorded terminal stop state")
        _expect(terminal.get("overall_status") in ("PASS", "FAIL"),
                "attempt terminal state unsupported")
        host_root = (attempt / "host-custody" / name).resolve()
        recorded_root = pathlib.Path(str(terminal.get("host_run_root", ""))).resolve()
        _expect(recorded_root == host_root, "attempt host run root identity mismatch")
        parent, _ = _read_json(host_root / "terminal.json", "host terminal")
        _expect(parent.get("schema") == "implementaudit-run-terminal-v1" and
                parent.get("run_id") == name and parent.get("kind") == "ok" and
                parent.get("reconciled") is False and
                parent.get("resolved_model") == expected_model,
                "host terminal is non-authoritative")
        (manifest, fixture, artifacts, _before, after, changed, preimages,
         _trace, raw_actions) = \
            _load_bundle(host_root / "bundle", packet, mission, parent)
        properties = _derive_properties(
            fixture, artifacts, after, changed, preimages, raw_actions)
        required = [prop["name"] for prop in fixture["properties"]
                    if prop.get("required", True)]
        _expect(required and all(name in properties for name in required),
                "required property matrix incomplete")
        product_status = "PASS" if all(properties[name]["pass"]
                                       for name in required) else "FAIL"
        independent_overall = product_status
        official_overall = terminal["overall_status"]
        statuses_agree = official_overall == independent_overall
        overall = independent_overall if statuses_agree else "FAIL"
        return {"index": mission["index"], "config": mission["config"],
                "arm": mission["arm"], "rep": mission["rep"],
                "product_status": product_status, "host_status": "PASS",
                "overall_status": overall, "properties": properties,
                "reason": (None if statuses_agree else
                           "official and independently rederived overall statuses disagree"),
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
    _expect(custody.get("schema") == "implementaudit-b3v4-campaign-custody-v1" and
            custody.get("campaign") == "b3v4-sol-r1" and
            custody.get("freeze_sha256") == freeze_sha,
            "campaign custody invalid")
    expected_names = {_attempt_name(mission) for mission in packet["missions"]}
    actual_names = {path.name for path in campaign_root.glob("attempt-*")
                    if not path.name.endswith(".claiming")}
    _expect(not list(campaign_root.glob("attempt-*.claiming")),
            "campaign contains nonterminal claim")
    _expect(actual_names == expected_names, "campaign attempt set incomplete or unexpected")
    rows = [_rederive_attempt(packet, campaign_root, mission, freeze_sha)
            for mission in packet["missions"]]
    if any(row["overall_status"] == "ERROR" for row in rows):
        status = "ERROR"
    elif any(row["overall_status"] == "INVALID" for row in rows):
        status = "INVALID"
    elif any(row["overall_status"] == "FAIL" for row in rows):
        status = "FAIL"
    else:
        status = "PASS"
    return {"schema": "implementaudit-b3v4-independent-rederivation-v1",
            "campaign": "b3v4-sol-r1", "freeze_sha256": freeze_sha,
            "campaign_status": status, "accepted": status == "PASS",
            "mission_count": len(rows), "missions": rows}


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
