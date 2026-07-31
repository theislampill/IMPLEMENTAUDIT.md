#!/usr/bin/env python3
"""Deterministic tests for the separate candidate-matrix freeze packet."""
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
MODULE = HERE / "validate_candidate_matrix_freeze.py"
FIXTURES = ["B0", "B1", "B2", "E1", "E2a", "E2b", "E3", "E4",
            "E5", "E6", "E7", "E8", "E9", "E10"]


def load_module():
    spec = importlib.util.spec_from_file_location("candidate_matrix_freeze", MODULE)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def attach_surface_contract(packet):
    sha = "a" * 64
    commit = packet["foundation"]["commit"]
    tree = packet["foundation"]["tree"]
    roles = {}
    for role in surfaces.required_roles(surfaces.MATRIX_CAMPAIGN):
        if role in surfaces.INLINE_ROLES:
            owner = {"kind": f"packet-projection-{role}"}
        elif role == "artifact-contract":
            owner = {"kind": "packet-artifact-contract"}
        elif role in ("scorer", "evaluator", "host-runner"):
            artifact = {"host-runner": "runner"}.get(role, role)
            owner = {
                "kind": f"packet-artifact-{role}", "artifact": artifact,
                "git_commit": commit, "git_tree": tree,
            }
        elif role.startswith("fixture-"):
            owner = {"kind": "packet-fixture",
                     "fixture_id": role[len("fixture-"):]}
        elif role == "independent-rederiver":
            owner = {
                "kind": "packet-independent-rederiver",
                "git_commit": commit, "git_tree": tree,
            }
        elif role == "native-executable":
            owner = {"kind": "packet-native-executable"}
        elif role == "product-candidate":
            owner = {
                "kind": "packet-product-candidate",
                "packet_owner": "candidate",
                "path": "surface/candidate/SKILL.md",
            }
        elif role == "host-attestation":
            owner = {"kind": "packet-host-attestation",
                     "path": "surface/host-attestation.json"}
        elif role in surfaces.FIXED_FILE_PATHS:
            owner = {"kind": f"frozen-{role}", "sha256": sha}
            if role in surfaces.GIT_IDENTITY_ROLES[
                    surfaces.MATRIX_CAMPAIGN]:
                owner.update({"git_commit": commit, "git_tree": tree})
        else:
            path = {
                "checkout-runtime-topology":
                    "surface/checkout-runtime-topology.json",
                "launcher": "surface/luna-launcher",
                "prompt-template": "surface/prompt-template.md",
            }.get(role, f"surface/{role}.bin")
            owner = {
                "kind": f"frozen-{role}",
                "path": path, "sha256": sha,
            }
        roles[role] = owner
    packet["evaluated_surface_owners"] = {
        "schema": surfaces.OWNER_SCHEMA,
        "campaign": surfaces.MATRIX_CAMPAIGN,
        "roles": roles,
    }
    entries = []
    for role in surfaces.required_roles(surfaces.MATRIX_CAMPAIGN):
        path, digest, git, raw = surfaces._packet_file_identity(
            packet, surfaces.MATRIX_CAMPAIGN, role, roles[role])
        entries.append({
            "role": role, "path": path,
            "byte_length": len(raw) if raw is not None else 1,
            "sha256": digest, **git,
        })
    packet["evaluated_surfaces"] = {
        "schema": surfaces.SCHEMA, "campaign": surfaces.MATRIX_CAMPAIGN,
        "entries": entries,
    }
    return packet


def valid_packet():
    sha = "a" * 64
    commit = "b" * 40
    tree = "c" * 40
    attestation = {"id": "matrix-L-host", "shell_dialect": "posix",
                   "executables": {"cat": "posix:cat"}}
    attestation_sha = hashlib.sha256(
        (json.dumps(attestation, sort_keys=True, separators=(",", ":")) +
         "\n").encode()).hexdigest()
    fixtures = []
    for fixture in FIXTURES:
        fixtures.append({
            "id": fixture,
            "path": f"eval/fixtures/{fixture}/fixture.json",
            "sha256": sha,
            "complete_manifest_sha256": sha,
        })
    packet = {
        "schema": "implementaudit-candidate-matrix-luna-freeze-v1",
        "campaign": "candidate-matrix-sol-luna-r1",
        "state": "FROZEN_BEFORE_FIRST_CELL",
        "artifact_contract": {
            "schema": "implementaudit-candidate-matrix-artifact-contract-v1",
            "path": "eval/candidate_matrix_contract.json",
            "sha256": hashlib.sha256(
                (HERE / "candidate_matrix_contract.json").read_bytes()
            ).hexdigest(),
        },
        "foundation": {"commit": commit, "tree": tree},
        "fixtures": fixtures,
        "artifacts": {
            name: {"path": f"eval/{name}.py", "sha256": sha}
            for name in ("scorer", "evaluator", "bundle", "runner")
        },
        "candidate": {"commit": commit, "tree": tree,
                      "skill_tree": tree, "payload_sha256": sha},
        "configuration": {
            "id": "L", "host": "WSL Ubuntu Codex CLI",
            "model_requested": "gpt-5.6-luna",
            "model_resolved_required": "gpt-5.6-luna",
            "reasoning_effort": "max",
            "auth_mode": "chatgpt-subscription",
            "executable": {"path": "surface/native-executable.bin",
                           "version": "1.2.3",
                           "sha256": sha},
            "host_attestation": {"id": "matrix-L-host",
                                 "sha256": attestation_sha},
        },
        "authorization": {
            "acknowledgement_path": "private/MATRIX_APPROVAL.txt",
            "acknowledgement_sha256": sha,
            "metered_api_spend": "FORBIDDEN",
        },
        "seed": 20260718,
        "cells": [{"index": i, "config": "L", "fixture": fixture}
                  for i, fixture in enumerate(FIXTURES)],
        "luna_stage": {
            "schema": "implementaudit-candidate-matrix-luna-stage-v1",
            "name": "LUNA", "cell_count": 14,
            "terminal_name": "luna-stage-terminal.json",
            "official_result_name": "candidate-matrix-luna-result.json",
            "independent_result_name":
                "candidate-matrix-luna-independent-rederivation.json",
            "success_disposition": "INCOMPLETE_PENDING_OPUS",
        },
        "evidence_profiles": {
            "formal_host_read": "implementaudit-host-read-profile-v2",
            "raw_stdout": "required", "native_session": "required",
            "pre_spawn": "required", "post_cell_manifest": "required",
        },
        "result_composition": {
            "product_property_states": ["PASS", "FAIL", "INCOMPLETE"],
            "host_states": ["PASS", "INVALID", "ERROR", "SUBSTITUTION"],
            "overall_states": ["PASS", "FAIL", "INVALID", "ERROR"],
            "luna_stage_dispositions": [
                "INCOMPLETE_PENDING_OPUS", "TEST_ONLY_NON_QUALIFYING"],
        },
        "attempt_policy": {
            "silent_retry": "FORBIDDEN", "preserve_every_attempt": True,
            "maximum_attempts": 14,
        },
        "acceptance_rule": (
            "all fourteen canonical Luna candidate fixture cells terminal and "
            "PASS; every retained attempt and result execution mode is exactly "
            "production; independent rederivation agrees; zero INVALID, ERROR, or "
            "substitution; successful Luna stage is INCOMPLETE_PENDING_OPUS "
            "with luna_stage_accepted true and accepted false"),
        "invalid_error_rule": (
            "FAIL, INVALID, unexplained ERROR, substitution, disagreement, "
            "and custody or identity failure halt the Luna stage"),
        "stop_conditions": [
            "authentication or quota failure", "model substitution",
            "identity or custody mismatch",
            "any FAIL, INVALID, or unexplained ERROR",
            "official and independent disagreement", "frozen input drift",
        ],
        "independent_rederiver": {
            "contract_id":
                "implementaudit-candidate-matrix-luna-rederiver-v1",
            "implementation_identity": {
                "path": "eval/candidate_matrix_rederive.py", "sha256": sha},
            "must_not_import": [
                "eval.candidate_matrix_campaign", "eval.hosts", "eval.runner",
                "eval.lib.scoring", "eval.adapters",
                "eval.campaign_lifecycle", "eval.b3v4_campaign",
                "eval.b3v4_rederive", "eval.b3v4_contract",
                "eval.evaluated_surfaces", "eval.provisional_integration",
                "eval.campaign_freeze_preflight",
                "eval.candidate_matrix_acceptance",
                "eval.candidate_matrix_fixture_setup",
                "eval.candidate_matrix_host",
            ],
            "input": "retained raw evidence only",
            "output": "independent Luna matrix result",
        },
        "evaluated_surface_owners": {},
        "evaluated_surfaces": {},
    }
    return attach_surface_contract(packet)


def reject(module, packet):
    try:
        module.validate_structure(packet)
    except (TypeError, ValueError):
        return
    raise AssertionError("mutated packet unexpectedly valid")


def main():
    module = load_module()
    packet = valid_packet()
    module.validate_structure(packet)
    for mutation in ("missing", "duplicate"):
        changed = copy.deepcopy(packet)
        if mutation == "missing":
            changed["evaluated_surfaces"]["entries"].pop()
        else:
            changed["evaluated_surfaces"]["entries"][-1]["path"] = \
                changed["evaluated_surfaces"]["entries"][0]["path"]
        reject(module, changed)
    assert [row["fixture"] for row in packet["cells"]] == FIXTURES
    mutations = []
    for cells in (packet["cells"][:-1],
                  packet["cells"] + [{"index": 14, "config": "L",
                                      "fixture": "B3"}],
                  list(reversed(packet["cells"]))):
        changed = copy.deepcopy(packet)
        changed["cells"] = cells
        mutations.append(changed)
    for key, value in (("config", "O"), ("fixture", "B3"),
                       ("arm", "candidate"), ("rep", 1)):
        changed = copy.deepcopy(packet)
        changed["cells"][0][key] = value
        mutations.append(changed)
    for changed in mutations:
        reject(module, changed)
    for path, alias in (
            (("cells", 0, "index"), False),
            (("cells", 0, "index"), 0.0),
            (("seed",), 20260718.0),
            (("attempt_policy", "maximum_attempts"), 14.0),
            (("luna_stage", "cell_count"), True)):
        changed = copy.deepcopy(packet)
        owner = changed
        for key in path[:-1]:
            owner = owner[key]
        owner[path[-1]] = alias
        reject(module, changed)
    changed = copy.deepcopy(packet)
    changed["control"] = copy.deepcopy(changed["candidate"])
    reject(module, changed)
    changed = copy.deepcopy(packet)
    changed["fixtures"][7]["path"] = changed["fixtures"][0]["path"]
    reject(module, changed)
    changed = copy.deepcopy(packet)
    changed["independent_rederiver"]["must_not_import"] = []
    reject(module, changed)

    with tempfile.TemporaryDirectory(
            prefix="candidate-matrix-fixture-custody-") as tmp:
        root = pathlib.Path(tmp)
        tree = root / "fixture"
        tree.mkdir()
        external = root / "outside.bin"
        external.write_bytes(b"support\n")
        alias = tree / "support-hardlink.bin"
        os.link(external, alias)
        try:
            module._tree_manifest(tree)
        except ValueError as exc:
            assert "hardlink" in str(exc).lower(), str(exc)
        else:
            raise AssertionError("fixture tree hardlink alias accepted")

    with tempfile.TemporaryDirectory(
            prefix="candidate-matrix-fixture-junction-") as tmp:
        root = pathlib.Path(tmp)
        tree = root / "fixture"
        outside = root / "outside"
        tree.mkdir()
        outside.mkdir()
        junction = tree / "support-junction"
        if os.name == "nt":
            created = subprocess.run(
                ["cmd.exe", "/c", "mklink", "/J",
                 str(junction), str(outside)],
                capture_output=True, text=True, timeout=30)
            supported = created.returncode == 0
        else:
            try:
                os.symlink(outside, junction, target_is_directory=True)
            except OSError:
                supported = False
            else:
                supported = True
        if supported:
            try:
                try:
                    module._tree_manifest(tree)
                except ValueError as exc:
                    assert (
                        "link" in str(exc).lower() or
                        "reparse" in str(exc).lower()), str(exc)
                else:
                    raise AssertionError(
                        "fixture tree junction/reparse alias accepted")
            finally:
                if junction.exists():
                    os.rmdir(junction)
            print("CANDIDATE_MATRIX_FIXTURE_JUNCTION=PASS")
        else:
            print("CANDIDATE_MATRIX_FIXTURE_JUNCTION=SKIP:unsupported")

    with tempfile.TemporaryDirectory(
            prefix="candidate-matrix-fixture-mutation-") as tmp:
        tree = pathlib.Path(tmp) / "fixture"
        tree.mkdir()
        support = tree / "support.txt"
        support.write_bytes(b"before\n")
        expected = module._tree_manifest(tree)
        support.write_bytes(b"after\n")
        observed = module._tree_manifest(tree)
        assert observed != expected, (
            "fixture tree mutation retained the validated manifest")

    with tempfile.TemporaryDirectory() as tmp:
        path = pathlib.Path(tmp) / "duplicate.json"
        raw = json.dumps(packet, separators=(",", ":"))
        raw = raw[:-1] + ',"campaign":"duplicate"}'
        path.write_text(raw, encoding="utf-8")
        proc = subprocess.run(
            ["python", str(MODULE), str(path)],
            capture_output=True, text=True, timeout=30)
        assert proc.returncode == 1
        assert "INVALID" in proc.stderr
        duplicate_owner = raw.replace(
            '"roles":{',
            '"roles":{"scorer":' + json.dumps(
                packet["evaluated_surface_owners"]["roles"]["scorer"],
                sort_keys=True, separators=(",", ":")) + ",", 1)
        path.write_text(duplicate_owner, encoding="utf-8")
        proc = subprocess.run(
            ["python", str(MODULE), str(path)],
            capture_output=True, text=True, timeout=30)
        assert proc.returncode == 1
        assert "duplicate JSON key" in proc.stderr
        for label, scalar in (
                ("bool", True), ("integer", 7), ("null", None),
                ("list", []), ("object", {})):
            wrong_owner_type = copy.deepcopy(packet)
            wrong_owner_type["evaluated_surface_owners"]["roles"][
                "prompt-template"]["path"] = scalar
            path.write_text(
                json.dumps(wrong_owner_type, sort_keys=True),
                encoding="utf-8")
            proc = subprocess.run(
                ["python", str(MODULE), str(path)],
                capture_output=True, text=True, timeout=30)
            assert proc.returncode == 1, (label, proc)
            assert "INVALID" in proc.stderr, (label, proc.stderr)
            assert "Traceback" not in proc.stderr, (label, proc.stderr)
    print("candidate matrix freeze: PASS")


if __name__ == "__main__":
    main()
