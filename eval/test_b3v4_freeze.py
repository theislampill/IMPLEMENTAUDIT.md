#!/usr/bin/env python3
"""Deterministic contract tests for the create-once B3-v4 freeze packet."""
from __future__ import annotations

import copy
import importlib.util
import json
import pathlib


HERE = pathlib.Path(__file__).resolve().parent
VALIDATOR = HERE / "validate_b3v4_freeze.py"


def load_validator():
    spec = importlib.util.spec_from_file_location("b3v4freeze", VALIDATOR)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def valid_packet():
    sha = "a" * 64
    commit = "b" * 40
    tree = "c" * 40
    missions = [
        {"index": i, "config": config, "arm": arm, "rep": rep}
        for i, (config, arm, rep) in enumerate([
            ("L", "candidate", 1), ("L", "control", 1),
            ("O", "control", 1), ("O", "candidate", 1),
            ("O", "candidate", 2), ("O", "control", 2),
            ("L", "control", 2), ("L", "candidate", 2),
            ("L", "control", 3), ("L", "candidate", 3),
            ("O", "candidate", 3), ("O", "control", 3),
        ])
    ]
    return {
        "schema": "implementaudit-b3v4-campaign-freeze-v1",
        "campaign": "b3v4-sol-r1",
        "state": "FROZEN_BEFORE_FIRST_MISSION",
        "foundation": {"commit": commit, "tree": tree},
        "fixture": {"id": "B3-v3", "fixture_sha256": sha,
                    "complete_manifest_sha256": sha},
        "artifacts": {
            name: {"path": f"eval/{name}.py", "sha256": sha}
            for name in ("scorer", "evaluator", "bundle", "runner")
        },
        "candidate": {"commit": commit, "tree": tree,
                      "skill_tree": tree, "payload_sha256": sha},
        "control": {"commit": commit, "tree": tree,
                    "skill_tree": tree, "payload_sha256": sha},
        "configurations": {
            "L": {"host": "WSL Ubuntu Codex CLI",
                  "model_requested": "gpt-5.6-luna",
                  "model_resolved_required": "gpt-5.6-luna",
                  "reasoning_effort": "max",
                  "auth_mode": "chatgpt-subscription",
                  "executable": {"path": "/bin/codex", "version": "1.2.3",
                                 "sha256": sha}},
            "O": {"host": "Windows Claude CLI",
                  "model_requested": "opus",
                  "model_resolved_required": "claude-opus-4-8",
                  "reasoning_effort": "high", "auth_mode": "claude.ai-max",
                  "executable": {"path": "C:/bin/claude.exe", "version": "2.3.4",
                                 "sha256": sha}},
        },
        "authorization": {"acknowledgement_path": "private/APPROVAL.txt",
                          "acknowledgement_sha256": sha,
                          "metered_api_spend": "FORBIDDEN"},
        "seed": 20260718,
        "repetitions_per_configuration_and_arm": 3,
        "missions": missions,
        "evidence_profiles": {
            "formal_host_read": "implementaudit-host-read-profile-v2",
            "raw_stdout": "required", "native_session": "required",
            "pre_spawn": "required", "post_mission_manifest": "required",
        },
        "result_composition": {
            "product_property_states": ["PASS", "FAIL", "INCOMPLETE"],
            "host_states": ["PASS", "INVALID", "ERROR", "SUBSTITUTION"],
            "overall_states": ["PASS", "FAIL", "INVALID", "ERROR"],
        },
        "attempt_policy": {"silent_retry": "FORBIDDEN",
                           "preserve_every_attempt": True},
        "acceptance_rule": "all 12 terminal and independently rederived",
        "invalid_error_rule": "never product data; halt and preserve",
        "stop_conditions": ["authentication or quota failure", "model substitution",
                            "identity or custody mismatch", "any INVALID or ERROR",
                            "frozen input drift"],
        "independent_rederiver": {
            "contract_id": "implementaudit-b3v4-independent-rederiver-v1",
            "implementation_identity": "separate-implementation-required-before-run",
            "must_not_import": ["eval.hosts", "eval.runner", "eval.lib.scoring"],
            "input": "retained raw evidence only",
            "output": "per-mission property, host, and overall rederivation",
        },
    }


def expect_invalid(module, packet, fragment):
    try:
        module.validate_structure(packet)
    except ValueError as exc:
        assert fragment in str(exc), str(exc)
    else:
        raise AssertionError(f"packet unexpectedly valid; wanted {fragment!r}")


def main():
    module = load_validator()
    packet = valid_packet()
    module.validate_structure(packet)

    missing = copy.deepcopy(packet)
    del missing["authorization"]
    expect_invalid(module, missing, "authorization")

    reordered = copy.deepcopy(packet)
    reordered["missions"][0], reordered["missions"][1] = (
        reordered["missions"][1], reordered["missions"][0])
    expect_invalid(module, reordered, "mission order")

    metered = copy.deepcopy(packet)
    metered["authorization"]["metered_api_spend"] = "allowed"
    expect_invalid(module, metered, "metered_api_spend")

    retry = copy.deepcopy(packet)
    retry["attempt_policy"]["silent_retry"] = "allowed"
    expect_invalid(module, retry, "silent_retry")

    weak_rederive = copy.deepcopy(packet)
    weak_rederive["independent_rederiver"]["must_not_import"] = []
    expect_invalid(module, weak_rederive, "must_not_import")

    encoded = json.dumps(packet, sort_keys=True, separators=(",", ":"))
    assert "FROZEN_BEFORE_FIRST_MISSION" in encoded
    print("test_b3v4_freeze: ok")


if __name__ == "__main__":
    main()
