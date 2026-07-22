#!/usr/bin/env python3
"""Validate the immutable B3-v4 preregistration packet without running a model."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import pathlib
import re
import subprocess
import sys

import b3v4_contract as contract


SHA256 = re.compile(r"^[0-9a-f]{64}$")
GIT_ID = re.compile(r"^[0-9a-f]{40}$")
PLAN = [
    ("L", "candidate", 1), ("L", "control", 1),
    ("O", "control", 1), ("O", "candidate", 1),
    ("O", "candidate", 2), ("O", "control", 2),
    ("L", "control", 2), ("L", "candidate", 2),
    ("L", "control", 3), ("L", "candidate", 3),
    ("O", "candidate", 3), ("O", "control", 3),
]
FORMAL_HOST_READ_PROFILE = "implementaudit-host-read-profile-v2"
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
REDERIVER_CONTRACT = "implementaudit-b3v4-independent-rederiver-v1"
REDERIVER_IMPORT_BOUNDARY = [
    "eval.hosts", "eval.runner", "eval.lib.scoring",
]
REDERIVER_INPUT = "retained raw evidence only"
REDERIVER_OUTPUT = "per-mission property, host, and overall rederivation"
REQUIRED = {
    "schema", "campaign", "state", "artifact_contract", "foundation", "fixture", "artifacts",
    "candidate", "control", "configurations", "authorization", "seed",
    "repetitions_per_configuration_and_arm", "missions", "evidence_profiles",
    "result_composition", "attempt_policy", "acceptance_rule",
    "invalid_error_rule", "stop_conditions", "independent_rederiver",
}


def _reject_duplicate_keys(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise ValueError(f"duplicate JSON key: {key}")
        value[key] = item
    return value


def _strict_json_load(stream):
    return json.load(stream, object_pairs_hook=_reject_duplicate_keys,
                     parse_constant=lambda value: (_ for _ in ()).throw(
                         ValueError(f"non-finite JSON number: {value}")))


def _mapping(value, name):
    if not isinstance(value, dict):
        raise ValueError(f"{name} must be an object")
    return value


def _required(mapping, names, owner):
    missing = sorted(set(names) - set(mapping))
    if missing:
        raise ValueError(f"{owner} missing required fields: {missing}")


def _digest(value, name):
    if not isinstance(value, str) or not SHA256.fullmatch(value):
        raise ValueError(f"{name} must be a lowercase SHA-256")


def _git_id(value, name):
    if not isinstance(value, str) or not GIT_ID.fullmatch(value):
        raise ValueError(f"{name} must be a lowercase full Git object id")


def _repo_relative_path(value, name):
    if not isinstance(value, str) or not value or "\x00" in value:
        raise ValueError(f"{name} must be a non-empty repository-relative path")
    normalized = value.replace("\\", "/")
    parts = normalized.split("/")
    if (value != normalized or normalized.startswith("/") or
            re.match(r"^[A-Za-z]:", normalized) or
            any(part in ("", ".", "..") for part in parts)):
        raise ValueError(f"{name} must be a non-empty repository-relative path")
    return normalized


def validate_structure(packet):
    contract.validate_freeze_envelope(packet)
    packet = _mapping(packet, "packet")
    _required(packet, REQUIRED, "packet")
    if packet["schema"] != "implementaudit-b3v4-campaign-freeze-v1":
        raise ValueError("unsupported B3-v4 freeze schema")
    if packet["campaign"] != "b3v4-sol-r1":
        raise ValueError("campaign must be b3v4-sol-r1")
    if packet["state"] != "FROZEN_BEFORE_FIRST_MISSION":
        raise ValueError("state must freeze the packet before the first mission")

    foundation = _mapping(packet["foundation"], "foundation")
    _required(foundation, {"commit", "tree"}, "foundation")
    _git_id(foundation["commit"], "foundation.commit")
    _git_id(foundation["tree"], "foundation.tree")

    fixture = _mapping(packet["fixture"], "fixture")
    _required(fixture, {"id", "fixture_sha256", "complete_manifest_sha256"},
              "fixture")
    _digest(fixture["fixture_sha256"], "fixture.fixture_sha256")
    _digest(fixture["complete_manifest_sha256"],
            "fixture.complete_manifest_sha256")

    artifacts = _mapping(packet["artifacts"], "artifacts")
    if set(artifacts) != {"scorer", "evaluator", "bundle", "runner"}:
        raise ValueError("artifacts must bind exactly scorer/evaluator/bundle/runner")
    for name, item in artifacts.items():
        item = _mapping(item, f"artifacts.{name}")
        _required(item, {"path", "sha256"}, f"artifacts.{name}")
        if not isinstance(item["path"], str) or not item["path"]:
            raise ValueError(f"artifacts.{name}.path must be non-empty")
        _digest(item["sha256"], f"artifacts.{name}.sha256")

    for arm in ("candidate", "control"):
        item = _mapping(packet[arm], arm)
        _required(item, {"commit", "tree", "skill_tree", "payload_sha256"}, arm)
        for key in ("commit", "tree", "skill_tree"):
            _git_id(item[key], f"{arm}.{key}")
        _digest(item["payload_sha256"], f"{arm}.payload_sha256")

    configurations = _mapping(packet["configurations"], "configurations")
    if set(configurations) != {"L", "O"}:
        raise ValueError("configurations must contain exactly L and O")
    expected = {
        "L": ("gpt-5.6-luna", "gpt-5.6-luna", "max",
              "chatgpt-subscription"),
        "O": ("opus", "claude-opus-4-8", "high", "claude.ai-max"),
    }
    for name, values in expected.items():
        item = _mapping(configurations[name], f"configurations.{name}")
        _required(item, {"host", "model_requested", "model_resolved_required",
                         "reasoning_effort", "auth_mode", "executable",
                         "host_attestation"},
                  f"configurations.{name}")
        observed = (item["model_requested"], item["model_resolved_required"],
                    item["reasoning_effort"], item["auth_mode"])
        if observed != values:
            raise ValueError(f"configuration {name} identity/auth boundary drift")
        executable = _mapping(item["executable"],
                              f"configurations.{name}.executable")
        _required(executable, {"path", "version", "sha256"},
                  f"configurations.{name}.executable")
        if not all(isinstance(executable[k], str) and executable[k]
                   for k in ("path", "version")):
            raise ValueError(f"configuration {name} executable identity incomplete")
        _digest(executable["sha256"],
                f"configurations.{name}.executable.sha256")
        attestation = _mapping(item["host_attestation"],
                               f"configurations.{name}.host_attestation")
        _required(attestation, {"id", "sha256"},
                  f"configurations.{name}.host_attestation")
        if not isinstance(attestation["id"], str) or not attestation["id"]:
            raise ValueError(
                f"configuration {name} host attestation id invalid")
        _digest(attestation["sha256"],
                f"configurations.{name}.host_attestation.sha256")

    authorization = _mapping(packet["authorization"], "authorization")
    _required(authorization, {"acknowledgement_path",
                              "acknowledgement_sha256", "metered_api_spend"},
              "authorization")
    _digest(authorization["acknowledgement_sha256"],
            "authorization.acknowledgement_sha256")
    if authorization["metered_api_spend"] != "FORBIDDEN":
        raise ValueError("authorization.metered_api_spend must be FORBIDDEN")

    if packet["seed"] != 20260718:
        raise ValueError("seed drift")
    if packet["repetitions_per_configuration_and_arm"] != 3:
        raise ValueError("repetition count drift")
    missions = packet["missions"]
    observed_plan = [
        (row.get("config"), row.get("arm"), row.get("rep"))
        for row in missions if isinstance(row, dict)
    ] if isinstance(missions, list) else []
    indices = [row.get("index") for row in missions
               if isinstance(row, dict)] if isinstance(missions, list) else []
    if observed_plan != PLAN or indices != list(range(12)):
        raise ValueError("fixed 12-mission order drift")

    profiles = _mapping(packet["evidence_profiles"], "evidence_profiles")
    _required(profiles, {"formal_host_read", "raw_stdout", "native_session",
                         "pre_spawn", "post_mission_manifest"},
              "evidence_profiles")
    if any(profiles[key] != "required" for key in (
            "raw_stdout", "native_session", "pre_spawn",
            "post_mission_manifest")):
        raise ValueError("formal-v2 evidence profiles must be required")
    if profiles["formal_host_read"] != FORMAL_HOST_READ_PROFILE:
        raise ValueError("evidence_profiles.formal_host_read must bind formal-v2")

    composition = _mapping(packet["result_composition"], "result_composition")
    if composition.get("product_property_states") != ["PASS", "FAIL", "INCOMPLETE"]:
        raise ValueError("product property state composition drift")
    if composition.get("overall_states") != ["PASS", "FAIL", "INVALID", "ERROR"]:
        raise ValueError("overall state composition drift")
    if composition.get("host_states") != ["PASS", "INVALID", "ERROR", "SUBSTITUTION"]:
        raise ValueError("host state composition drift")

    attempts = _mapping(packet["attempt_policy"], "attempt_policy")
    if attempts.get("silent_retry") != "FORBIDDEN":
        raise ValueError("attempt_policy.silent_retry must be FORBIDDEN")
    if attempts.get("preserve_every_attempt") is not True:
        raise ValueError("attempt_policy must preserve every attempt")

    if packet["acceptance_rule"] != ACCEPTANCE_RULE:
        raise ValueError("frozen packet drift: acceptance_rule")
    if packet["invalid_error_rule"] != INVALID_ERROR_RULE:
        raise ValueError("invalid_error_rule drift")
    if packet["stop_conditions"] != STOP_CONDITIONS:
        raise ValueError("stop_conditions drift")
    rederiver = _mapping(packet["independent_rederiver"],
                         "independent_rederiver")
    _required(rederiver, {"contract_id", "implementation_identity",
                          "must_not_import", "input", "output"},
              "independent_rederiver")
    if rederiver["contract_id"] != REDERIVER_CONTRACT:
        raise ValueError("independent_rederiver.contract_id drift")
    identity = _mapping(rederiver["implementation_identity"],
                        "independent_rederiver.implementation_identity")
    if set(identity) != {"path", "sha256"}:
        raise ValueError(
            "independent_rederiver.implementation_identity must bind path/sha256")
    _repo_relative_path(
        identity["path"], "independent_rederiver.implementation_identity.path")
    _digest(identity["sha256"],
            "independent_rederiver.implementation_identity.sha256")
    if rederiver["must_not_import"] != REDERIVER_IMPORT_BOUNDARY:
        raise ValueError("independent_rederiver.must_not_import drift")
    if rederiver["input"] != REDERIVER_INPUT:
        raise ValueError("independent_rederiver.input drift")
    if rederiver["output"] != REDERIVER_OUTPUT:
        raise ValueError("independent_rederiver.output drift")
    return packet


def _sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _tree_manifest(root):
    rows = []
    for base, dirs, files in os.walk(root):
        dirs.sort()
        for name in sorted(files):
            path = os.path.join(base, name)
            rel = os.path.relpath(path, root).replace("\\", "/")
            rows.append(f"{rel}\0{_sha256(path)}\n")
    return hashlib.sha256("".join(rows).encode("utf-8")).hexdigest()


def _git(repo, *args):
    proc = subprocess.run(["git", "-C", str(repo), *args], capture_output=True,
                          text=True, encoding="utf-8", errors="strict")
    if proc.returncode:
        raise ValueError(f"git identity check failed: {proc.stderr.strip()}")
    return proc.stdout.strip()


def validate_live(packet, repo_root):
    repo_root = pathlib.Path(repo_root).resolve()
    contract_identity = packet["artifact_contract"]
    contract_path = contract.resolve_contained(repo_root, contract_identity["path"])
    if _sha256(contract_path) != contract_identity["sha256"]:
        raise ValueError("artifact contract hash mismatch")
    foundation = packet["foundation"]
    if _git(repo_root, "cat-file", "-t", foundation["commit"]) != "commit":
        raise ValueError("foundation commit identity is not a commit object")
    if _git(repo_root, "rev-parse", foundation["commit"] + "^{tree}") != foundation["tree"]:
        raise ValueError("foundation commit/tree mismatch")
    fixture_dir = repo_root / "eval" / "fixtures" / packet["fixture"]["id"]
    if _sha256(fixture_dir / "fixture.json") != packet["fixture"]["fixture_sha256"]:
        raise ValueError("fixture hash mismatch")
    if _tree_manifest(fixture_dir) != packet["fixture"]["complete_manifest_sha256"]:
        raise ValueError("complete fixture manifest hash mismatch")
    for name, item in packet["artifacts"].items():
        path = contract.resolve_contained(repo_root, item["path"])
        if _sha256(path) != item["sha256"]:
            raise ValueError(f"{name} artifact hash mismatch")
    approval = packet["authorization"]
    approval_path = contract.resolve_external_file(
        approval["acknowledgement_path"], "approval acknowledgement")
    if _sha256(approval_path) != approval["acknowledgement_sha256"]:
        raise ValueError("approval acknowledgement hash mismatch")
    identity = packet["independent_rederiver"]["implementation_identity"]
    rederiver_path = repo_root / pathlib.PurePosixPath(identity["path"])
    if _sha256(rederiver_path) != identity["sha256"]:
        raise ValueError("independent rederiver implementation hash mismatch")
    return packet


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("intent")
    parser.add_argument("--repo-root", default=os.path.dirname(os.path.dirname(__file__)))
    parser.add_argument("--schema-only", action="store_true")
    args = parser.parse_args(argv)
    with open(args.intent, encoding="utf-8") as stream:
        packet = _strict_json_load(stream)
    validate_structure(packet)
    if not args.schema_only:
        validate_live(packet, args.repo_root)
    print("B3V4-FREEZE-VALID")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"B3V4-FREEZE-INVALID: {exc}", file=sys.stderr)
        raise SystemExit(2)
