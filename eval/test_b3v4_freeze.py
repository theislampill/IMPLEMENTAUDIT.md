#!/usr/bin/env python3
"""Deterministic contract tests for the create-once B3-v4 freeze packet."""
from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import os
import pathlib
import subprocess
import tempfile

import evaluated_surfaces as surfaces

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
    host_attestations = {
        "L": {"id": "b3v4-L-host", "shell_dialect": "posix",
              "executables": {"cat": "posix:cat"}},
    }
    host_attestation_hashes = {
        name: hashlib.sha256((json.dumps(value, sort_keys=True,
              separators=(",", ":")) + "\n").encode()).hexdigest()
        for name, value in host_attestations.items()
    }
    missions = [
        {"index": i, "config": config, "arm": arm, "rep": rep}
        for i, (config, arm, rep) in enumerate([
            ("L", "candidate", 1), ("L", "control", 1),
            ("L", "control", 2), ("L", "candidate", 2),
            ("L", "control", 3), ("L", "candidate", 3),
        ])
    ]
    evaluated = {
        "schema": surfaces.SCHEMA, "campaign": surfaces.B3_CAMPAIGN,
        "entries": [],
    }
    for index, role in enumerate(surfaces.required_roles(
            surfaces.B3_CAMPAIGN)):
        row = {
            "role": role, "path": f"surface/{index:02d}.bin",
            "byte_length": 1, "sha256": sha,
        }
        if role in surfaces.GIT_IDENTITY_ROLES[surfaces.B3_CAMPAIGN]:
            row.update({"git_commit": commit, "git_tree": tree})
        evaluated["entries"].append(row)
    return {
        "schema": "implementaudit-b3v4-luna-campaign-freeze-v2",
        "campaign": "b3v4-sol-luna-r2",
        "state": "FROZEN_BEFORE_FIRST_MISSION",
        "artifact_contract": {
            "schema": "implementaudit-b3v4-luna-artifact-contract-v2",
            "path": "eval/b3v4_contract.json",
            "sha256": hashlib.sha256(
                (HERE / "b3v4_contract.json").read_bytes()).hexdigest(),
        },
        "foundation": {"commit": commit, "tree": tree},
        "fixture": {"id": "B3-v3", "fixture_sha256": sha,
                    "complete_manifest_sha256": sha},
        "artifacts": {
            name: {"path": f"eval/{name}.py", "sha256": sha}
            for name in ("scorer", "evaluator", "bundle", "runner")
        },
        "candidate": {"commit": commit, "tree": tree,
                      "skill_tree": tree, "payload_sha256": sha},
        "control": {"commit": "d" * 40, "tree": "e" * 40,
                    "skill_tree": "f" * 40, "payload_sha256": "b" * 64},
        "configurations": {
            "L": {"host": "WSL Ubuntu Codex CLI",
                  "model_requested": "gpt-5.6-luna",
                  "model_resolved_required": "gpt-5.6-luna",
                  "reasoning_effort": "max",
                  "auth_mode": "chatgpt-subscription",
                  "executable": {"path": "/bin/codex", "version": "1.2.3",
                                 "sha256": sha},
                  "host_attestation": {"id": host_attestations["L"]["id"],
                                       "sha256": host_attestation_hashes["L"]}},
        },
        "authorization": {"acknowledgement_path": "private/APPROVAL.txt",
                          "acknowledgement_sha256": sha,
                          "metered_api_spend": "FORBIDDEN"},
        "seed": 20260718,
        "repetitions_per_arm": 3,
        "missions": missions,
        "luna_stage": {
            "schema": "implementaudit-b3v4-luna-stage-v2",
            "name": "LUNA", "mission_count": 6,
            "terminal_name": "luna-stage-terminal.json",
            "official_result_name": "b3v4-luna-result.json",
            "independent_result_name":
                "b3v4-luna-independent-rederivation.json",
            "success_disposition": "INCOMPLETE_PENDING_OPUS",
        },
        "evidence_profiles": {
            "formal_host_read": "implementaudit-host-read-profile-v2",
            "raw_stdout": "required", "native_session": "required",
            "pre_spawn": "required", "post_mission_manifest": "required",
        },
        "result_composition": {
            "product_property_states": ["PASS", "FAIL", "INCOMPLETE"],
            "host_states": ["PASS", "INVALID", "ERROR", "SUBSTITUTION"],
            "overall_states": ["PASS", "FAIL", "INVALID", "ERROR"],
            "luna_stage_dispositions": ["INCOMPLETE_PENDING_OPUS"],
        },
        "attempt_policy": {"silent_retry": "FORBIDDEN",
                           "preserve_every_attempt": True,
                           "maximum_attempts": 6},
        "acceptance_rule": (
            "all six Luna missions terminal and PASS; independent Luna "
            "rederivation agrees with "
            "every stored property, host, and overall result; property "
            "evidence complete in every verdict; host status PASS in every "
            "mission; zero INVALID/ERROR; zero model substitution; exact "
            "candidate, control, model, host, fixture, scorer, evaluator, "
            "bundle, runner, and rederiver identities; successful Luna stage "
            "is INCOMPLETE_PENDING_OPUS with luna_stage_accepted true and "
            "accepted false"),
        "invalid_error_rule": (
            "FAIL, INVALID, unexplained ERROR, substitution, disagreement, "
            "and custody or identity failure halt the Luna stage and preserve "
            "every attempt"),
        "stop_conditions": ["authentication or quota failure", "model substitution",
                            "identity or custody mismatch",
                            "any FAIL, INVALID, or unexplained ERROR",
                            "official and independent disagreement",
                            "frozen input drift"],
        "independent_rederiver": {
            "contract_id":
                "implementaudit-b3v4-luna-independent-rederiver-v2",
            "implementation_identity": {
                "path": "eval/b3v4_rederive.py", "sha256": sha},
            "must_not_import": [
                "eval.b3v4_campaign", "eval.hosts", "eval.runner",
                "eval.lib.scoring", "eval.adapters",
                "eval.campaign_lifecycle", "eval.evaluated_surfaces",
                "eval.provisional_integration"],
            "input": "retained raw evidence only",
            "output": "independent Luna stage result",
        },
        "evaluated_surfaces": evaluated,
    }


def expect_invalid(module, packet, fragment):
    try:
        module.validate_structure(packet)
    except ValueError as exc:
        assert fragment in str(exc), str(exc)
    else:
        raise AssertionError(f"packet unexpectedly valid; wanted {fragment!r}")


def expect_live_invalid(module, packet, repo, fragment):
    try:
        module.validate_live(packet, repo)
    except ValueError as exc:
        assert fragment in str(exc), str(exc)
    else:
        raise AssertionError(f"live packet unexpectedly valid; wanted {fragment!r}")


def append_duplicate_member(raw, name, value):
    end = raw.rfind("}")
    assert end >= 0
    return raw[:end] + f',"{name}":{json.dumps(value)}' + raw[end:]


def main():
    module = load_validator()
    packet = valid_packet()
    module.validate_structure(packet)
    missing_surface = copy.deepcopy(packet)
    missing_surface["evaluated_surfaces"]["entries"].pop()
    expect_invalid(module, missing_surface, "role coverage")
    duplicate_surface = copy.deepcopy(packet)
    duplicate_surface["evaluated_surfaces"]["entries"][-1]["path"] = \
        duplicate_surface["evaluated_surfaces"]["entries"][0]["path"]
    expect_invalid(module, duplicate_surface, "duplicate path")
    for alias in (6.0, True):
        changed = copy.deepcopy(packet)
        changed["luna_stage"]["mission_count"] = alias
        expect_invalid(module, changed, "luna_stage")

    expected_plan = [
        ("L", "candidate", 1), ("L", "control", 1),
        ("L", "control", 2), ("L", "candidate", 2),
        ("L", "control", 3), ("L", "candidate", 3),
    ]
    assert [(row["config"], row["arm"], row["rep"])
            for row in packet["missions"]] == expected_plan
    assert set(packet["configurations"]) == {"L"}

    old_interleaved = copy.deepcopy(packet)
    old_interleaved["schema"] = "implementaudit-b3v4-campaign-freeze-v1"
    old_interleaved["missions"].extend([
        {"index": 6 + index, "config": "O", "arm": arm, "rep": rep}
        for index, (arm, rep) in enumerate([
            ("control", 1), ("candidate", 1), ("candidate", 2),
            ("control", 2), ("candidate", 3), ("control", 3)])])
    expect_invalid(module, old_interleaved, "schema")

    mission_mutations = []
    missing_mission = copy.deepcopy(packet); missing_mission["missions"].pop()
    mission_mutations.append(missing_mission)
    duplicate_mission = copy.deepcopy(packet)
    duplicate_mission["missions"][1] = copy.deepcopy(
        duplicate_mission["missions"][0])
    mission_mutations.append(duplicate_mission)
    reordered_mission = copy.deepcopy(packet)
    reordered_mission["missions"][0], reordered_mission["missions"][1] = (
        reordered_mission["missions"][1], reordered_mission["missions"][0])
    mission_mutations.append(reordered_mission)
    extra_mission = copy.deepcopy(packet)
    extra_mission["missions"].append(
        {"index": 6, "config": "L", "arm": "candidate", "rep": 4})
    mission_mutations.append(extra_mission)
    for key, value in (("config", "O"), ("arm", "other"), ("rep", 9)):
        changed = copy.deepcopy(packet)
        changed["missions"][0][key] = value
        mission_mutations.append(changed)
    for changed in mission_mutations:
        expect_invalid(module, changed, "mission")

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

    reviewer_counterexample = copy.deepcopy(packet)
    reviewer_counterexample["evidence_profiles"]["formal_host_read"] = "optional"
    reviewer_counterexample["acceptance_rule"] = "one official PASS is enough"
    reviewer_counterexample["invalid_error_rule"] = \
        "INVALID and ERROR count as product PASS; continue"
    reviewer_counterexample["stop_conditions"] = ["continue"] * 5
    reviewer_counterexample["independent_rederiver"].update({
        "implementation_identity": "",
        "input": "copy official result",
        "output": "copy official result",
    })
    expect_invalid(module, reviewer_counterexample, "implementation_identity")

    weak_formal_profile = copy.deepcopy(packet)
    weak_formal_profile["evidence_profiles"]["formal_host_read"] = "optional"
    expect_invalid(module, weak_formal_profile, "formal_host_read")

    weak_acceptance = copy.deepcopy(packet)
    weak_acceptance["acceptance_rule"] = "one official PASS is enough"
    expect_invalid(module, weak_acceptance, "acceptance_rule")

    weak_invalid_error = copy.deepcopy(packet)
    weak_invalid_error["invalid_error_rule"] = \
        "INVALID and ERROR count as product PASS; continue"
    expect_invalid(module, weak_invalid_error, "invalid_error_rule")

    weak_stops = copy.deepcopy(packet)
    weak_stops["stop_conditions"] = ["continue"] * 5
    expect_invalid(module, weak_stops, "stop_conditions")

    empty_identity = copy.deepcopy(packet)
    empty_identity["independent_rederiver"]["implementation_identity"] = ""
    expect_invalid(module, empty_identity, "implementation_identity")

    empty_identity_path = copy.deepcopy(packet)
    empty_identity_path["independent_rederiver"]["implementation_identity"][
        "path"] = ""
    expect_invalid(module, empty_identity_path, "implementation_identity.path")

    escaping_identity_path = copy.deepcopy(packet)
    escaping_identity_path["independent_rederiver"]["implementation_identity"][
        "path"] = "../eval/b3v4_rederive.py"
    expect_invalid(module, escaping_identity_path,
                   "implementation_identity.path")

    bad_identity_hash = copy.deepcopy(packet)
    bad_identity_hash["independent_rederiver"]["implementation_identity"][
        "sha256"] = "not-a-digest"
    expect_invalid(module, bad_identity_hash, "implementation_identity.sha256")

    copy_only_input = copy.deepcopy(packet)
    copy_only_input["independent_rederiver"]["input"] = "copy official result"
    expect_invalid(module, copy_only_input, "independent_rederiver.input")

    copy_only_output = copy.deepcopy(packet)
    copy_only_output["independent_rederiver"]["output"] = "copy official result"
    expect_invalid(module, copy_only_output, "independent_rederiver.output")

    with tempfile.TemporaryDirectory(prefix="b3v4-freeze-") as tmp:
        repo = HERE.parent
        approval = pathlib.Path(tmp) / "APPROVAL.txt"
        approval.write_text("owner-approved subscription boundary\n",
                            encoding="utf-8")
        live = valid_packet()
        live["foundation"] = {
            "commit": subprocess.check_output(
                ["git", "-C", str(repo), "rev-parse", "HEAD"],
                text=True).strip(),
            "tree": subprocess.check_output(
                ["git", "-C", str(repo), "rev-parse", "HEAD^{tree}"],
                text=True).strip(),
        }
        fixture_dir = repo / "eval" / "fixtures" / live["fixture"]["id"]
        live["fixture"]["fixture_sha256"] = module._sha256(
            fixture_dir / "fixture.json")
        live["fixture"]["complete_manifest_sha256"] = module._tree_manifest(
            fixture_dir)
        artifact_paths = {
            "scorer": "eval/lib/scoring.py",
            "evaluator": "eval/validate_b3v4_freeze.py",
            "bundle": "eval/lib/bundle.py", "runner": "eval/runner.py"}
        live["artifacts"] = {name: {"path": path,
            "sha256": module._sha256(repo / path)}
            for name, path in artifact_paths.items()}
        live["authorization"]["acknowledgement_path"] = str(approval)
        live["authorization"]["acknowledgement_sha256"] = module._sha256(
            approval)
        rederiver = repo / "eval" / "b3v4_rederive.py"
        live["independent_rederiver"]["implementation_identity"][
            "sha256"] = module._sha256(rederiver)
        tracked = subprocess.check_output(
            ["git", "-C", str(repo), "ls-files"], text=True).splitlines()
        retained = [
            path for path in tracked
            if (repo / pathlib.PurePosixPath(path)).is_file() and
            os.stat(repo / pathlib.PurePosixPath(path)).st_nlink == 1
        ]
        roles = surfaces.required_roles(surfaces.B3_CAMPAIGN)
        assert len(retained) >= len(roles)
        surface_sources = []
        for role, path in zip(roles, retained):
            row = {"role": role, "path": path}
            if role in surfaces.GIT_IDENTITY_ROLES[surfaces.B3_CAMPAIGN]:
                row.update({
                    "git_commit": live["foundation"]["commit"],
                    "git_tree": live["foundation"]["tree"],
                })
            surface_sources.append(row)
        live["evaluated_surfaces"] = surfaces.build_manifest(
            surfaces.B3_CAMPAIGN, surface_sources, root=repo)
        module.validate_structure(live)
        module.validate_live(live, repo)

        if os.name == "nt":
            approval_target = pathlib.Path(tmp) / "approval-target"
            approval_target.mkdir()
            junction_approval = approval_target / "APPROVAL.txt"
            junction_approval.write_text(
                "owner-approved subscription boundary\n", encoding="utf-8")
            approval_junction = pathlib.Path(tmp) / "approval-junction"
            made = subprocess.run(
                ["cmd", "/c", "mklink", "/J", str(approval_junction),
                 str(approval_target)], capture_output=True, text=True)
            if made.returncode:
                print("LIVE_APPROVAL_PARENT_JUNCTION=SKIP:mklink")
            else:
                junction_live = copy.deepcopy(live)
                alias = approval_junction / "APPROVAL.txt"
                junction_live["authorization"]["acknowledgement_path"] = str(alias)
                junction_live["authorization"]["acknowledgement_sha256"] = \
                    hashlib.sha256(junction_approval.read_bytes()).hexdigest()
                expect_live_invalid(module, junction_live, repo, "link")
                os.rmdir(approval_junction)
                print("LIVE_APPROVAL_PARENT_JUNCTION=PASS")

        tree_as_commit = copy.deepcopy(live)
        tree_as_commit["foundation"]["commit"] = live["foundation"]["tree"]
        expect_live_invalid(module, tree_as_commit, repo, "not a commit object")

        drifted_rederiver = copy.deepcopy(live)
        drifted_rederiver["independent_rederiver"][
            "implementation_identity"]["sha256"] = "0" * 64
        expect_live_invalid(module, drifted_rederiver, repo,
                            "rederiver implementation hash mismatch")

    encoded = json.dumps(packet, sort_keys=True, separators=(",", ":"))
    assert "FROZEN_BEFORE_FIRST_MISSION" in encoded
    with tempfile.TemporaryDirectory(prefix="b3v4-freeze-duplicate-") as tmp:
        intent = pathlib.Path(tmp) / "intent.json"
        intent.write_text(
            append_duplicate_member(encoded, "seed", 20260718),
            encoding="utf-8")
        rejected = subprocess.run(
            ["python", str(VALIDATOR), str(intent), "--schema-only"],
            capture_output=True, text=True)
        assert rejected.returncode == 2, rejected
        assert "duplicate JSON key" in rejected.stderr, rejected.stderr
        nested = encoded.replace(
            f'"fixture_sha256":"{"a" * 64}"',
            f'"fixture_sha256":"{"a" * 64}",'
            f'"fixture_sha256":"{"a" * 64}"', 1)
        intent.write_text(nested, encoding="utf-8")
        nested_rejected = subprocess.run(
            ["python", str(VALIDATOR), str(intent), "--schema-only"],
            capture_output=True, text=True)
        assert nested_rejected.returncode == 2, nested_rejected
        assert "duplicate JSON key" in nested_rejected.stderr, \
            nested_rejected.stderr
    print("test_b3v4_freeze: ok")


if __name__ == "__main__":
    main()
