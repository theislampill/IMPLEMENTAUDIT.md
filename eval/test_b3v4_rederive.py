#!/usr/bin/env python3
"""Deterministic tests for the independent B3-v4 evidence rederiver."""
from __future__ import annotations

import ast
import copy
import hashlib
import importlib.util
import json
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile

from test_b3v4_freeze import valid_packet
from test_campaign_freeze_preflight import (
    write_retained_production_readiness_fixture,
)
import b3v4_contract as official_contract
import evaluated_surfaces as surfaces
import runner as official_runner
from lib import hostread as official_hostread


HERE = pathlib.Path(__file__).resolve().parent
REDERIVER = HERE / "b3v4_rederive.py"
CAPTURE_FILES = (
    "host-read-profile.json", "host-read-preimages.json",
    "host-read-fixture.raw", "host-read-replay-spec.json",
    "host-read-pre-spawn.json", "host-stdout.raw", "host-session.raw",
    "host-tool-trace.json", "host-read-matrix.json",
    "host-read-post-probe.json", "host-read-terminal.json",
)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode() + b"\n"


def write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data if isinstance(data, bytes) else encoded(data))


def snapshot(files):
    value = {
        "schema": "implementaudit-repo-snapshot-v2",
        "head_commit": "d" * 40, "head_tree": "e" * 40,
        "index_tree": "e" * 40, "staged": [], "unstaged": [],
        "renames": {}, "untracked": {}, "worktree_files": files,
        "tracked_diff_sha256": sha(b""),
    }
    body = json.dumps(value, sort_keys=True).encode()
    value["snapshot_sha256"] = sha(body)
    return value


def custody_manifest_bytes(path):
    path = pathlib.Path(path)
    entries = [{"path": ".", "kind": "directory"}]
    for current, directories, files in os.walk(path):
        current = pathlib.Path(current)
        relative = current.relative_to(path)
        directories.sort()
        files.sort()
        for name in directories:
            rel = ((relative / name).as_posix()
                   if relative != pathlib.Path(".") else name)
            entries.append({"path": rel, "kind": "directory"})
        for name in files:
            child = current / name
            rel = ((relative / name).as_posix()
                   if relative != pathlib.Path(".") else name)
            payload = child.read_bytes()
            entries.append({
                "path": rel, "kind": "file",
                "byte_length": len(payload), "sha256": sha(payload),
            })
    entries.sort(key=lambda row: row["path"])
    return (json.dumps({
        "schema": "implementaudit-custodied-directory-manifest-v1",
        "entries": entries,
    }, indent=1, sort_keys=True) + "\n").encode()


def make_fixture():
    return json.loads((HERE / "fixtures" / "B3-v3" / "fixture.json").read_text(
        encoding="utf-8"))


def bundle_hash(bundle):
    digest = hashlib.sha256()
    for name in ("manifest.json", "fixture.json", "prompt.txt",
                 "events.jsonl", "repo-before.json", "repo-after.json",
                 "repo-comparison.json", "artifact-manifest.json"):
        path = bundle / name
        if path.is_file():
            digest.update(name.encode())
            digest.update(path.read_bytes())
    return digest.hexdigest()


def synthetic_official_pass(fixture, model, manifest, bundle_sha256):
    properties = {
        prop["name"]: {
            "state": "PASS", "pass": True,
            "evidence": "synthetic retained evidence",
            "describes": prop.get("describes", ""),
            "basis": "host-observation",
        }
        for prop in fixture["properties"]
    }
    return {
        "schema": "implementaudit-eval-verdict-v3", "status": "PASS",
        **{key: manifest[key] for key in (
            "run_id", "fixture_id", "fixture_sha256", "prompt_sha256",
            "events_sha256", "product_tag", "product_commit", "product_tree",
            "installed_payload_sha256", "harness_commit", "adapter_name",
            "adapter_version", "adapter_sha256", "model_requested",
            "model_resolved", "host", "started_at", "ended_at")},
        "model_resolved": model, "model_substitution": False,
        "identity_attestation": {
            "verified_in_replay": [
                "fixture_sha256 (bytes + canonical-library authenticity)",
                "prompt_sha256 (bytes + mission consistency)",
                "events_sha256", "repo_before/after snapshot integrity",
                "artifact hashes via artifact-manifest"],
            "adapter_attested_only": [
                "product_tag/commit/tree", "installed_payload_sha256",
                "adapter_name/version/sha256", "host",
                "harness_commit (cross-checked when the scoring checkout is available)"],
        },
        "bundle_sha256": bundle_sha256,
        "scorer_commit": manifest["harness_commit"],
        "properties": properties,
        "host_safety": {
            "schema": "implementaudit-host-safety-v1", "status": "PASS",
            "failed_invariant": None, "failed_status": None, "findings": [],
        },
        "adjudication": {
            "schema": "implementaudit-eval-adjudication-v1",
            "product_status": "PASS", "host_status": "PASS",
            "overall_status": "PASS", "property_evidence_complete": True,
            "all_required_properties_true": True,
            "product_failed_invariant": None, "host_failed_invariant": None,
            "host_failed_status": None, "failed_domain": None,
            "failed_invariant": None,
        },
        "failed_domain": None, "failed_invariant": None,
        "evidence": ["synthetic retained evidence"], "reason": None,
    }


def build_campaign(root, fixture_override=None, *, surface_root=None,
                   external_surface_paths=None, foundation=None):
    root = pathlib.Path(root)
    surface_root = root if surface_root is None else pathlib.Path(surface_root)
    fixture = copy.deepcopy(fixture_override) if fixture_override is not None \
        else make_fixture()
    fixture_bytes = (encoded(fixture) if fixture_override is not None else
                     (HERE / "fixtures" / "B3-v3" / "fixture.json").read_bytes())
    packet = valid_packet()
    if foundation is not None:
        packet["foundation"] = copy.deepcopy(foundation)
    packet["independent_rederiver"]["implementation_identity"]["sha256"] = \
        sha(REDERIVER.read_bytes())
    packet["fixture"]["fixture_sha256"] = sha(fixture_bytes)
    external_surface_paths = external_surface_paths or {}
    owners = packet["evaluated_surface_owners"]["roles"]
    for role, path in external_surface_paths.items():
        owners[role]["path"] = pathlib.Path(path).resolve().as_posix()
    attestation_bytes = encoded({
        "id": "b3v4-L-host", "shell_dialect": "posix",
        "executables": {"cat": "posix:cat"},
    })
    for index, role in enumerate(surfaces.required_roles(
            surfaces.B3_CAMPAIGN)):
        if role in surfaces.INLINE_ROLES:
            continue
        if role == "artifact-contract":
            payload = (HERE / "b3v4_contract.json").read_bytes()
        elif role == "fixture-B3-v3":
            payload = fixture_bytes
        elif role == "independent-rederiver":
            payload = REDERIVER.read_bytes()
        elif role == "host-attestation":
            payload = attestation_bytes
            packet["configurations"]["L"]["host_attestation"]["sha256"] = \
                sha(payload)
        else:
            payload = f"{packet['campaign']}:{role}:{index}\n".encode()
        if role in ("scorer", "evaluator", "host-runner"):
            artifact = {"host-runner": "runner"}.get(role, role)
            packet["artifacts"][artifact]["sha256"] = sha(payload)
        elif role == "native-executable":
            packet["configurations"]["L"]["executable"]["path"] = \
                owners[role].get(
                    "path", "surface/native-executable.bin")
            packet["configurations"]["L"]["executable"]["sha256"] = sha(payload)
        elif role in ("product-candidate", "product-control"):
            packet[role[len("product-"):]]["payload_sha256"] = sha(payload)
        elif owners[role]["kind"].startswith("frozen-"):
            owners[role]["sha256"] = sha(payload)
        path, _digest, _git, _raw = surfaces._packet_file_identity(
            packet, surfaces.B3_CAMPAIGN, role, owners[role])
        write(pathlib.Path(path) if pathlib.Path(path).is_absolute()
              else surface_root / path, payload)
    packet["evaluated_surfaces"] = surfaces.build_manifest_from_packet(
        packet, surfaces.B3_CAMPAIGN, root=surface_root)
    packet_bytes = json.dumps(packet, sort_keys=True).encode()
    freeze_sha = sha(packet_bytes)
    write(root / "campaign-freeze.json", packet_bytes)
    write(root / "campaign-manifest.json", {
        "schema": "implementaudit-b3v4-luna-campaign-custody-v3",
        "campaign": "b3v4-sol-luna-r2", "freeze_sha256": freeze_sha,
        "contract_sha256": packet["artifact_contract"]["sha256"],
        "created_at": "2030-01-01T00:00:00Z",
        "execution_stage": "LUNA",
        "campaign_root_identity": {
            "device": os.lstat(root).st_dev,
            "inode": os.lstat(root).st_ino,
            "mode": os.lstat(root).st_mode,
        },
    })
    capsule_path = fixture["allowed_paths"][0]
    capsule = {
        "repository_identity": "context-epoch-fixture-repo",
        "run_root": ".IMPLEMENTAUDIT/runs/audit-closure-a7Kx2f",
        "boundary_provenance": "host-reported-compaction",
        "source_epoch": "epoch-7", "new_epoch": "epoch-8",
        "current_active_item": "ANDON 251",
        "next_authorized_action": "countermeasure rerun for ANDON 251",
        "stale_one_shot": "fix ANDON 150",
        "stale_one_shot_status": "satisfied", "decision": "audited-handoff",
        "authorization_reason": "execution not authorized; capsule only",
    }
    capsule_bytes = encoded(capsule)
    readiness_path = write_retained_production_readiness_fixture(
        "b3v4", packet, root.parent / (root.name + "-live-ready"),
        campaign_root=root)
    readiness_bytes = readiness_path.read_bytes()
    readiness = json.loads(readiness_bytes)
    for mission in packet["missions"]:
        name = (f"attempt-{mission['index']:03d}-{mission['config']}-"
                f"{mission['arm']}-r{mission['rep']}")
        attempt = root / name
        host_root = attempt / "host-custody" / name
        bundle = host_root / "bundle"
        model = packet["configurations"][mission["config"]][
            "model_resolved_required"]
        config = packet["configurations"][mission["config"]]
        dialect, reader = (("posix", "cat") if mission["config"] == "L"
                           else ("powershell", "get-content"))
        attestation = {
            "id": f"b3v4-{mission['config']}-host",
            "shell_dialect": dialect,
            "executables": {reader: f"{dialect}:{reader}"},
        }
        attestation_bytes = encoded(attestation)
        write(attempt / "host-attestation.json", attestation_bytes)
        write(attempt / "launch-readiness.json", readiness_bytes)
        adapter = "codex-cli" if mission["config"] == "L" else "claude-cli"
        write(attempt / "attempt-status.json", {
            "schema": "implementaudit-b3v4-luna-attempt-status-v2",
            "campaign": "b3v4-sol-luna-r2", "freeze_sha256": freeze_sha,
            "contract_sha256": packet["artifact_contract"]["sha256"],
            "mission": mission, "state": "PREPARED_BEFORE_HOST_SPAWN",
            "execution_mode": "production", "created_at": "2030-01-01T00:00:00Z",
            "host_attestation_binding": {
                "path": "host-attestation.json", "sha256": sha(attestation_bytes),
                "config": mission["config"], "host": config["host"],
                "model_resolved_required": config["model_resolved_required"],
            },
            "launch_readiness_binding": {
                "path": "launch-readiness.json",
                "sha256": sha(readiness_bytes),
                "schema": readiness["schema"],
                "execution_mode": readiness["execution_mode"],
                "disposition": readiness["disposition"],
            },
        })
        attempt_terminal = {
            "schema": "implementaudit-b3v4-luna-attempt-terminal-v3",
            "campaign": "b3v4-sol-luna-r2", "mission_index": mission["index"],
            "execution_mode": "production", "overall_status": "PASS",
            "resolved_model": model, "host_run_root": str(host_root),
            "official_overall_status": None,
            "official_verdict_sha256": None,
            "stop_reason": None, "error_type": None,
            "completed_at": "2030-01-01T00:00:01Z",
            "completed_attempt_seal": None,
        }
        write(attempt / "attempt-terminal.json", attempt_terminal)
        before = snapshot({})
        after = snapshot({capsule_path: {"type": "file", "sha256": sha(capsule_bytes)}})
        after["untracked"] = {capsule_path: {"type": "file", "sha256": sha(capsule_bytes)}}
        body = {k: v for k, v in after.items() if k != "snapshot_sha256"}
        after["snapshot_sha256"] = sha(json.dumps(body, sort_keys=True).encode())
        host = "codex" if mission["config"] == "L" else "claude"
        profile = {
            "schema": "implementaudit-host-read-profile-v2",
            "authority": "mechanically-minted", "host": host,
            "repo": {"lexical_root": "/repo", "real_root": "/repo",
                     "case_sensitive": True},
        }
        if host == "codex":
            probe = {
                "environment": {"PATH": "/usr/bin", "LANG": "C.UTF-8",
                                "LC_ALL": None, "BASH_ENV": None,
                                "ENV": None, "SHELL": "/bin/bash"},
                "shell": {"logical_path": "/bin/bash",
                          "realpath": "/bin/bash", "sha256": "7" * 64,
                          "stat": "dev=1;ino=1;mode=100755;size=1"},
                "executables": {name: {
                    "kind": "file", "path": "/usr/bin/" + name,
                    "sha256": "8" * 64,
                    "stat": "dev=1;ino=2;mode=100755;size=1"}
                    for name in ("cat", "grep", "head", "rg", "sed", "tail")},
            }
            profile.update(probe)
            profile["outer_wrapper"] = {
                "argv_prefix": ["/bin/bash", "-lc"], "max_unwrap_layers": 1}
            profile["probe_sha256"] = sha(json.dumps(
                probe, sort_keys=True, separators=(",", ":")).encode())
            post = copy.deepcopy(probe)
        else:
            native_tools = {"requested": ["Read", "Write"]}
            profile["native_tools"] = native_tools
            profile["probe_sha256"] = sha(json.dumps({
                "repo": "/repo", "native_tools": native_tools},
                sort_keys=True, separators=(",", ":")).encode())
            post = {"native_tools": copy.deepcopy(native_tools)}
        reads = fixture["host_checks"]["specs"][1].get("reads") or \
            make_fixture()["host_checks"]["specs"][1]["reads"]
        targets = {}
        actions = []
        ordinal = 3 if host == "codex" else 2
        for target in reads:
            content = ("STATE\n" if target.endswith("STATE.md") else "ROADMAP\n").encode()
            targets[target] = {"canonical_path": "/repo/" + target,
                               "relative_path": target,
                               "sha256": sha(content),
                               "content_base64": __import__("base64").b64encode(content).decode(),
                               "size": len(content), "mode": 0o100644,
                               "symlink_free": True}
            if host == "codex":
                command = "/bin/bash -lc " + json.dumps("cat " + target)
                actions.append({
                    "id": f"read-{ordinal}", "state": "COMPLETED",
                    "effect": "command", "action_type": "command_execution",
                    "classification": None, "invocation_invented": False,
                    "payload": ["command", command],
                    "command": command, "wrapper_layers": 1,
                    "protocol_wrapper_valid": True, "exit_code": 0,
                    "output": content.decode(), "invocation_ordinal": ordinal,
                    "completion_ordinal": ordinal + 1})
            else:
                inputs = {"file_path": target}
                actions.append({
                    "id": f"read-{ordinal}", "state": "COMPLETED",
                    "effect": "read", "action_type": "Read", "path": target,
                    "classification": "fail-closed",
                    "invocation_invented": False,
                    "payload": ["Read", json.dumps(
                        inputs, sort_keys=True, separators=(",", ":"))],
                    "command": None, "inputs": inputs,
                    "output": content.decode(), "metadata": None,
                    "read_transport": "full-exact",
                    "structured_content": content.decode(),
                    "invocation_ordinal": ordinal,
                    "completion_ordinal": ordinal + 1})
            ordinal += 2
        write_action = {"id": "write", "state": "COMPLETED",
                        "effect": "write", "invocation_ordinal": ordinal,
                        "completion_ordinal": ordinal + 1,
                        "classification": None,
                        "invocation_invented": False}
        if host == "codex":
            write_action.update({"action_type": "file_change",
                                 "paths": [capsule_path],
                                 "payload": ["changes", [[capsule_path, "add"]]]})
        else:
            inputs = {"file_path": capsule_path,
                      "content": capsule_bytes.decode()}
            write_action.update({"action_type": "Write", "path": capsule_path,
                                 "command": None, "inputs": inputs,
                                 "payload": ["Write", json.dumps(
                                     inputs, sort_keys=True,
                                     separators=(",", ":"))],
                                 "output": "created", "metadata": None})
        actions.append(write_action)
        preimages = {"schema": "implementaudit-host-read-preimages-v1",
                     "repo": profile["repo"], "targets": targets}
        checks = [{"key": "live_state_read_before_capsule_write",
                   "reads": reads, "write": capsule_path}]
        intent = {
            "schema": "implementaudit-run-intent-v1", "run_id": name,
            "fixture_id": "B3-v3", "call_ordinal": mission["index"] + 1,
            "fixture_sha256": sha(fixture_bytes),
            "product_checkout": "/product", "adapter_name": adapter,
            "adapter_sha256": "a" * 64,
            "harness_commit": packet["foundation"]["commit"],
            "model_requested": (packet["configurations"][mission["config"]][
                "model_requested"] if mission["config"] == "L" else model),
            "reasoning_effort_requested": packet["configurations"][
                mission["config"]]["reasoning_effort"],
            "policy_requested": {},
            "required_capabilities": fixture["required_capabilities"],
            "temp_home": "/tmp/b3v4-home",
            "started_at": "2030-01-01T00:00:00Z",
        }
        replay = {"schema": "implementaudit-host-read-replay-spec-v1",
                  "mode": "formal-v2", "host": profile["host"], "checks": checks,
                  "requested_tools": [] if mission["config"] == "L" else ["Read", "Write"],
                  "fixture_sha256": sha(fixture_bytes),
                  "run_intent_sha256": sha(encoded(intent)), "parser_sha256": "f" * 64}
        if mission["config"] == "L":
            raw_events = [
                {"type": "thread.started", "thread_id": name},
                {"type": "turn.started", "thread_id": name,
                 "turn_id": "stdout-turn"},
            ]
            for action in actions[:-1]:
                item = {"id": action["id"], "type": "command_execution",
                        "status": "in_progress", "command": action["command"]}
                raw_events.append({"type": "item.started", "item": item})
                item = dict(item, status="completed",
                            aggregated_output=action["output"], exit_code=0)
                raw_events.append({"type": "item.completed", "item": item})
            changes = [{"path": capsule_path, "kind": "add"}]
            raw_events.extend([
                {"type": "item.started", "item": {"id": "write",
                 "type": "file_change", "status": "in_progress", "changes": changes}},
                {"type": "item.completed", "item": {"id": "write",
                 "type": "file_change", "status": "completed", "changes": changes}},
                {"type": "turn.completed", "thread_id": name,
                 "turn_id": "stdout-turn"},
            ])
        else:
            raw_events = [{"type": "system", "subtype": "init",
                           "session_id": name, "tools": ["Read", "Write"]}]
            for action in actions[:-1]:
                raw_events.extend([
                    {"type": "assistant", "session_id": name,
                     "message": {"content": [{"type": "tool_use",
                      "id": action["id"], "name": "Read",
                      "input": {"file_path": action["path"]}}]}},
                    {"type": "user", "session_id": name,
                     "message": {"content": [{"type": "tool_result",
                      "tool_use_id": action["id"], "content": action["output"],
                      "is_error": False}]}},
                ])
            raw_events.extend([
                {"type": "assistant", "session_id": name,
                 "message": {"content": [{"type": "tool_use", "id": "write",
                  "name": "Write", "input": {"file_path": capsule_path,
                                                "content": capsule_bytes.decode()}}]}},
                {"type": "user", "session_id": name,
                 "message": {"content": [{"type": "tool_result",
                  "tool_use_id": "write", "content": "created", "is_error": False}]}},
            ])
        raw_stdout = b"".join(encoded(event) for event in raw_events)
        if host == "codex":
            raw_session = b"".join(encoded(event) for event in [
                {"type": "session_meta", "timestamp": "2030-01-01T00:00:00Z",
                 "payload": {"id": name, "session_id": name, "cwd": "/repo",
                             "timestamp": "2030-01-01T00:00:00Z"}},
                {"type": "turn_context", "timestamp": "2030-01-01T00:00:00Z",
                 "payload": {"turn_id": "native-turn", "cwd": "/repo",
                             "model": intent["model_requested"]}},
                {"type": "response_item", "timestamp": "2030-01-01T00:00:00Z",
                 "payload": {
                    "action_ids": [action["id"] for action in actions]}}])
            binding = {"thread_id": name, "stdout_turn_ordinal": 1,
                       "turn_id": "stdout-turn", "native_turn_id": "native-turn"}
        else:
            raw_session = encoded({"type": "system", "subtype": "transcript",
                                   "session_id": name,
                                   "action_ids": [a["id"] for a in actions]})
            binding = {"session_id": name}
        trace = {"schema": "implementaudit-host-tool-trace-v2", "actions": actions,
                 "invalid": False, "host_findings": [], "ids_reserved": True,
                 "action_states": ["COMPLETED"] * len(actions),
                 "action_effects": [a["effect"] for a in actions],
                 "host_status": "PASS",
                 "requested_tools": [] if host == "codex" else ["Read", "Write"],
                 "observed_tools": [] if host == "codex" else ["Read", "Write"]}
        if host == "claude":
            trace["crashed"] = False
        read_results = {
            target: {"classification": "content-read",
                     "completion_ordinal": action["completion_ordinal"]}
            for target, action in zip(reads, actions[:-1])}
        matrix_row = {
            "schema": "implementaudit-host-read-matrix-v1",
            "property_status": "PASS", "host_status": "PASS",
            "overall_status": "PASS", "ordered": True,
            "ordering_source": "persisted-ordinal", "write_completed": True,
            "write_invocation_ordinal": write_action["invocation_ordinal"],
            "borrowed_completion": False, "live_preimage": True,
            "reads": read_results, "host_findings": [],
            "shell_write_observations": 0}
        matrix = {"schema": "implementaudit-host-read-matrix-v1",
                  "raw_transforms": {
                      "host-stdout.raw": host + "-typed-action-normalizer-v2",
                      "host-session.raw": "lineage-corroboration-only"},
                  "specs": {"live_state_read_before_capsule_write": matrix_row}}
        files = {
            "host-read-profile.json": encoded(profile),
            "host-read-preimages.json": encoded(preimages),
            "host-read-fixture.raw": fixture_bytes,
            "host-read-replay-spec.json": encoded(replay),
        }
        pre_spawn = {"schema": "implementaudit-host-read-pre-spawn-v1",
                     "created_before_spawn": True,
                     "profile_sha256": sha(files["host-read-profile.json"]),
                     "preimages_sha256": sha(files["host-read-preimages.json"]),
                     "fixture_sha256": sha(files["host-read-fixture.raw"]),
                     "replay_spec_sha256": sha(files["host-read-replay-spec.json"])}
        files.update({"host-read-pre-spawn.json": encoded(pre_spawn),
                      "host-stdout.raw": raw_stdout, "host-session.raw": raw_session,
                      "host-tool-trace.json": encoded(trace),
                      "host-read-matrix.json": encoded(matrix),
                      "host-read-post-probe.json": encoded(post)})
        terminal = {"schema": "implementaudit-host-read-terminal-v1",
                    "hashes": {key: sha(value) for key, value in files.items()},
                    "post_probe_sha256": sha(json.dumps(post, sort_keys=True,
                                                        separators=(",", ":")).encode()),
                    "profile_post_status": "PASS", "binding": binding,
                    "actual_tools": trace["observed_tools"],
                    "normalized_host_status": "PASS",
                    "host_terminal_kind": "ok", "session_bound": True,
                    "session_status": "VALID"}
        files["host-read-terminal.json"] = encoded(terminal)
        capture_manifest = {"schema": "implementaudit-host-read-manifest-v1",
                            "files": {key: sha(value) for key, value in files.items()}}
        files["host-read-manifest.json"] = encoded(capture_manifest)
        files["run-intent.json"] = encoded(intent)
        files["process-started.json"] = encoded({
            "schema": "implementaudit-process-started-v3", "run_id": name,
            "cwd": "/repo", "started_at": "2030-01-01T00:00:00Z",
            "argv_sha256": "b" * 64, "requested_model": model,
            "temp_home": "/tmp/b3v4-home",
            "lane_id": "test-lane", "host_os": (
                "posix" if mission["config"] == "L" else "windows"),
            "host_boot_id": "test-boot", "pid": 1234,
            "process_creation_time": 1.0,
            "host_read_pre_spawn_sha256": sha(
                files["host-read-pre-spawn.json"]),
            "trusted_spawn_guard": {
                "schema": "implementaudit-b3v4-trusted-spawn-guard-v1",
                "campaign": "b3v4-sol-luna-r2",
                "freeze_sha256": freeze_sha,
                "contract_sha256":
                    packet["artifact_contract"]["sha256"],
                "run_id": name,
                "mission": mission,
                "campaign_root_identity": {
                    "device": os.lstat(root).st_dev,
                    "inode": os.lstat(root).st_ino,
                    "mode": os.lstat(root).st_mode,
                },
                "guard_ordinal": 1,
                "state":
                    "GUARD_PASSED_IMMEDIATELY_BEFORE_OS_SPAWN",
            },
        })
        files["host-checks.json"] = encoded({spec["key"]: True
                                              for spec in fixture["host_checks"]["specs"]})
        files["host-check-inputs/" + capsule_path] = capsule_bytes
        files["host-stderr.raw"] = b""
        files["raw-host-events.jsonl"] = raw_session
        files["derived-transform.json"] = encoded({
            "schema": "implementaudit-derived-view-v1",
            "transform": adapter + "-host-event-extraction-v2",
            "source": ("codex-session-jsonl" if host == "codex" else
                       "claude-stream-json"),
            "source_raw_sha256": sha(raw_session),
            "rules": "one scored event per HOST-ASSIGNED assistant message; "
                     "prompt echoes/user/system/tool events are never scored as "
                     "assistant content; complete raw streams preserved; no deletion",
        })
        artifact_manifest = {"files": {key: sha(value) for key, value in files.items()}}
        retained_event = encoded({
            "schema": "implementaudit-eval-event-v1", "run_id": name,
            "fixture_id": "B3-v3", "seq": 1, "role": "assistant",
            "kind": "message", "content": "retained synthetic response",
            "recorded_at": "2030-01-01T00:00:01Z",
        })
        manifest = {
            "schema": "implementaudit-eval-manifest-v2", "run_id": name,
            "fixture_id": "B3-v3", "fixture_sha256": sha(fixture_bytes),
            "prompt_sha256": sha(("MISSION:\n" + fixture["mission"]).encode()),
            "product_tag": "v0.3.2.0", "product_commit": packet[mission["arm"]]["commit"],
            "product_tree": packet[mission["arm"]]["tree"],
            "installed_payload_sha256": packet[mission["arm"]]["payload_sha256"],
            "harness_commit": packet["foundation"]["commit"],
            "adapter_name": adapter, "adapter_version": "test",
            "adapter_sha256": "a" * 64,
            "model_requested": (packet["configurations"][mission["config"]]["model_requested"]
                                if mission["config"] == "L" else model),
            "model_resolved": model, "host": adapter,
            "started_at": "2030-01-01T00:00:00Z", "ended_at": "2030-01-01T00:00:01Z",
            "events_sha256": sha(retained_event),
            "repo_before_sha256": sha(encoded(before)),
            "repo_after_sha256": sha(encoded(after)),
            "artifact_manifest_sha256": sha(encoded(artifact_manifest)),
            "payload_source_sha256": packet[mission["arm"]]["payload_sha256"],
            "repo_comparison_sha256": "",
            "policy_requested": ({
                "sandbox": "workspace-write", "approval": "never",
                "tools": "codex-shell", "network": "restricted",
                "writable_roots": ["<fixture-repo cwd>"]} if host == "codex" else {
                "sandbox": "claude-headless-tool-permissions",
                "approval": "auto-deny-outside-allowed",
                "tools": "Read Glob Grep Write Edit Bash",
                "network": "tool-mediated only",
                "writable_roots": ["<fixture-repo cwd>"]}),
            "policy_resolved": ({
                "class": "host-owned (session turn_context)",
                "sandbox": "workspace-write", "approval": "never",
                "session_id": name, "cli_version": "test"} if host == "codex" else {
                "class": "adapter-attested (NOT host-owned)",
                "tools": "Read Glob Grep Write Edit Bash (argv-requested)",
                "note": "test canary attestation"}),
            "models_observed": ([{
                "model": model, "role": "root-agent",
                "source": "host session turn_context", "session_id": name}]
                if host == "codex" else [{
                "model": model, "role": "root-assistant-events",
                "events": 1, "source": "host-assigned message.model"}]),
            "reasoning_effort_requested": packet["configurations"][
                mission["config"]]["reasoning_effort"],
            "reasoning_effort_resolved": packet["configurations"][
                mission["config"]]["reasoning_effort"],
        }
        comparison = {
            "schema": "implementaudit-repo-comparison-v1",
            "changed_files": [capsule_path], "committed_change": False,
            "committed_files_known": True, "committed_files": [],
        }
        manifest["repo_comparison_sha256"] = sha(encoded(comparison))
        write(host_root / "terminal.json", {
            "schema": "implementaudit-run-terminal-v1", "run_id": name,
            "spawned": True, "kind": "ok", "detail": str(bundle),
            "resolved_model": model, "reconciled": False,
            "started_at": "2030-01-01T00:00:00Z", "ended_at": "2030-01-01T00:00:01Z",
            "policy_resolved": {},
        })
        write(bundle / "manifest.json", manifest)
        write(bundle / "fixture.json", fixture_bytes)
        write(bundle / "prompt.txt", ("MISSION:\n" + fixture["mission"]).encode())
        write(bundle / "events.jsonl", retained_event)
        write(bundle / "repo-before.json", before)
        write(bundle / "repo-after.json", after)
        write(bundle / "repo-comparison.json", comparison)
        write(bundle / "artifact-manifest.json", artifact_manifest)
        for rel, data in files.items():
            write(bundle / "artifacts" / rel, data)
        official_status = "PASS"
        official_verdict = synthetic_official_pass(
            fixture, model, manifest, bundle_hash(bundle))
        official_bytes = encoded(official_verdict)
        write(attempt / "official-verdict.json", official_bytes)
        attempt_terminal.update({
            "official_overall_status": official_status,
            "official_verdict_sha256": sha(official_bytes),
        })
        status_raw = (attempt / "attempt-status.json").read_bytes()
        attempt_terminal["completed_attempt_seal"] = {
            "schema": "implementaudit-b3v4-completed-attempt-seal-v1",
            "campaign": packet["campaign"],
            "freeze_sha256": freeze_sha,
            "contract_sha256": packet["artifact_contract"]["sha256"],
            "mission": mission,
            "execution_mode": attempt_terminal["execution_mode"],
            "overall_status": attempt_terminal["overall_status"],
            "resolved_model": attempt_terminal["resolved_model"],
            "host_run_root": attempt_terminal["host_run_root"],
            "official_overall_status":
                attempt_terminal["official_overall_status"],
            "official_verdict_sha256":
                attempt_terminal["official_verdict_sha256"],
            "stop_reason": attempt_terminal["stop_reason"],
            "error_type": attempt_terminal["error_type"],
            "completed_at": attempt_terminal["completed_at"],
            "attempt_name": name,
            "attempt_status_sha256": sha(status_raw),
            "host_attestation_sha256": sha(attestation_bytes),
            "launch_readiness_sha256": sha(readiness_bytes),
            "host_custody_manifest_sha256": sha(
                custody_manifest_bytes(attempt / "host-custody")),
        }
        write(attempt / "attempt-terminal.json", attempt_terminal)
    return packet


def load_module(source=REDERIVER, name="b3v4rederive"):
    spec = importlib.util.spec_from_file_location(name, source)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def minimal_codex_rows(turn_started=None, turn_completed=None):
    return [
        {"type": "thread.started", "thread_id": "thread-a"},
        turn_started or {"type": "turn.started"},
        {
            "type": "item.started",
            "item": {
                "id": "cmd-1",
                "type": "command_execution",
                "status": "in_progress",
                "command": "true",
            },
        },
        {
            "type": "item.completed",
            "item": {
                "id": "cmd-1",
                "type": "command_execution",
                "status": "completed",
                "command": "true",
                "aggregated_output": "",
                "exit_code": 0,
            },
        },
        turn_completed or {"type": "turn.completed"},
    ]


def assert_codex_current_lifecycle_parity(module):
    def raw_text(rows):
        return "".join(
            json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n"
            for row in rows)

    def classify(raw):
        binding = official_hostread.derive_codex_binding(raw)
        official = official_hostread.normalize_codex(
            raw, formal=False, binding=binding)
        try:
            actions, independent_binding = module._parse_codex_actions(
                raw.encode("utf-8"))
        except module.EvidenceInvalid as exc:
            return official["host_status"], "INVALID", binding, str(exc)
        return official["host_status"], "PASS", independent_binding, actions

    rows = minimal_codex_rows()
    current_raw = raw_text(rows)
    current = classify(current_raw)
    assert current[:2] == ("PASS", "PASS"), current
    assert current[2] == {
        "thread_id": "thread-a",
        "stdout_turn_ordinal": 1,
    }, current
    assert len(current[3]) == 1 and current[3][0]["id"] == "cmd-1", current

    explicit_rows = minimal_codex_rows(
        {"type": "turn.started", "thread_id": "thread-a",
         "turn_id": "turn-a"},
        {"type": "turn.completed", "thread_id": "thread-a",
         "turn_id": "turn-a"})
    explicit = classify(raw_text(explicit_rows))
    assert explicit[:2] == ("PASS", "PASS"), explicit
    assert explicit[2] == {
        "thread_id": "thread-a",
        "stdout_turn_ordinal": 1,
        "turn_id": "turn-a",
    }, explicit
    explicit_item_identity_rows = copy.deepcopy(explicit_rows)
    for event in explicit_item_identity_rows[2:4]:
        event.update({"thread_id": "thread-a", "turn_id": "turn-a"})

    rooted_status_rows = copy.deepcopy(rows)
    rooted_status_rows[2]["status"] = "in_progress"
    rooted_status_rows[3]["status"] = "completed"
    rooted_status = classify(raw_text(rooted_status_rows))
    assert rooted_status[:2] == ("PASS", "PASS"), rooted_status

    retained_rows = copy.deepcopy(rows)
    retained_rows[2]["item"].update({
        "aggregated_output": "", "exit_code": None})
    retained_rows[-1]["usage"] = {
        "input_tokens": 100,
        "cached_input_tokens": 50,
        "output_tokens": 20,
        "reasoning_output_tokens": 10,
    }
    retained = classify(raw_text(retained_rows))
    assert retained[:2] == ("PASS", "PASS"), retained

    def command_start_rows(**updates):
        malformed = copy.deepcopy(rows[2])
        malformed["item"].update(updates)
        return [rows[0], rows[1], malformed, *rows[3:]]

    file_rows = [
        copy.deepcopy(rows[0]), copy.deepcopy(rows[1]),
        {"type": "item.started", "item": {
            "id": "file-1", "type": "file_change",
            "status": "in_progress",
            "changes": [{"path": "capsule.json", "kind": "add"}]}},
        {"type": "item.completed", "item": {
            "id": "file-1", "type": "file_change",
            "status": "completed",
            "changes": [{"path": "capsule.json", "kind": "add"}]}},
        copy.deepcopy(rows[4]),
    ]
    todo_rows = [
        copy.deepcopy(rows[0]), copy.deepcopy(rows[1]),
        {"type": "item.started", "item": {
            "id": "todo-1", "type": "todo_list",
            "status": "in_progress",
            "items": [{"text": "inspect", "completed": False}]}},
        {"type": "item.completed", "item": {
            "id": "todo-1", "type": "todo_list",
            "status": "completed",
            "items": [{"text": "inspect", "completed": True}]}},
        copy.deepcopy(rows[4]),
    ]
    message_rows = [
        copy.deepcopy(rows[0]), copy.deepcopy(rows[1]),
        {"type": "item.completed", "item": {
            "id": "message-1", "type": "agent_message",
            "status": "completed", "text": "done"}},
        copy.deepcopy(rows[4]),
    ]
    two_command_rows = [
        copy.deepcopy(rows[0]), copy.deepcopy(rows[1]),
        copy.deepcopy(rows[2]),
        {"type": "item.started", "item": {
            **copy.deepcopy(rows[2]["item"]), "id": "cmd-2"}},
        copy.deepcopy(rows[3]),
        {"type": "item.completed", "item": {
            **copy.deepcopy(rows[3]["item"]), "id": "cmd-2"}},
        copy.deepcopy(rows[4]),
    ]
    for label, valid_rows in (
            ("file change", file_rows),
            ("todo", todo_rows),
            ("agent message", message_rows),
            ("interleaved commands", two_command_rows)):
        valid = classify(raw_text(valid_rows))
        assert valid[:2] == ("PASS", "PASS"), (label, valid)

    adversarial = {
        "missing command completion":
            [rows[0], rows[1], rows[2], rows[4]],
        "orphan command completion":
            [rows[0], rows[1], rows[3], rows[4]],
        "duplicate command completion":
            rows[:4] + [copy.deepcopy(rows[3])] + rows[4:],
        "duplicate command start":
            rows[:3] + [copy.deepcopy(rows[2])] + rows[3:],
        "explicit start missing terminal id": minimal_codex_rows(
            {"type": "turn.started", "turn_id": "turn-a"},
            {"type": "turn.completed"}),
        "implicit start invented terminal id": minimal_codex_rows(
            turn_completed={
                "type": "turn.completed", "turn_id": "turn-a"}),
        "wrong completion thread": minimal_codex_rows(
            turn_completed={
                "type": "turn.completed", "thread_id": "thread-b"}),
        "extra start field": minimal_codex_rows(
            {"type": "turn.started", "unexpected": "value"}),
        "empty terminal turn": minimal_codex_rows(
            turn_completed={"type": "turn.completed", "turn_id": ""}),
        "zero active thread": rows[1:],
        "multiple active threads":
            rows[:1] + [dict(rows[0])] + rows[1:],
        "turn before thread":
            rows[1:2] + rows[:1] + rows[2:],
        "action before turn":
            rows[:1] + rows[2:3] + rows[1:2] + rows[3:],
        "duplicate turn start":
            rows[:2] + [{"type": "turn.started"}] + rows[2:],
        "wrong start thread": minimal_codex_rows(
            {"type": "turn.started", "thread_id": "thread-b"}),
        "mismatched explicit turn": minimal_codex_rows(
            {"type": "turn.started", "thread_id": "thread-a",
             "turn_id": "turn-a"},
            {"type": "turn.completed", "thread_id": "thread-a",
             "turn_id": "turn-b"}),
        "missing terminal": rows[:-1],
        "duplicate terminal": rows + [{"type": "turn.completed"}],
        "action after terminal":
            rows + [copy.deepcopy(rows[2])],
        "non-string start thread": minimal_codex_rows(
            {"type": "turn.started", "thread_id": 1}),
        "non-string start turn": minimal_codex_rows(
            {"type": "turn.started", "turn_id": True}),
        "non-string completion turn": minimal_codex_rows(
            turn_completed={"type": "turn.completed", "turn_id": 1}),
        "null completion thread": minimal_codex_rows(
            turn_completed={"type": "turn.completed", "thread_id": None}),
        "partial command start metadata":
            command_start_rows(aggregated_output=""),
        "nonempty command start output":
            command_start_rows(
                aggregated_output="invented", exit_code=None),
        "premature command start exit":
            command_start_rows(aggregated_output="", exit_code=0),
    }
    mismatched_id = copy.deepcopy(rows)
    mismatched_id[3]["item"]["id"] = "cmd-foreign"
    adversarial["command completion id mismatch"] = mismatched_id
    mismatched_kind = copy.deepcopy(rows)
    mismatched_kind[3]["item"] = copy.deepcopy(file_rows[3]["item"])
    mismatched_kind[3]["item"]["id"] = "cmd-1"
    adversarial["command completion kind mismatch"] = mismatched_kind
    mismatched_status = copy.deepcopy(rows)
    mismatched_status[3]["item"]["status"] = "in_progress"
    adversarial["command completion status mismatch"] = mismatched_status
    mismatched_exit = copy.deepcopy(rows)
    mismatched_exit[3]["item"]["exit_code"] = 1
    adversarial["command exit-status contradiction"] = mismatched_exit
    failed_zero = copy.deepcopy(rows)
    failed_zero[3]["item"]["status"] = "failed"
    adversarial["command failed-zero contradiction"] = failed_zero
    malformed_output = copy.deepcopy(rows)
    malformed_output[3]["item"]["aggregated_output"] = ["not", "text"]
    adversarial["command output coercion"] = malformed_output

    adversarial["missing file completion"] = (
        file_rows[:3] + file_rows[4:])
    adversarial["orphan file completion"] = (
        file_rows[:2] + file_rows[3:])
    file_path_mismatch = copy.deepcopy(file_rows)
    file_path_mismatch[3]["item"]["changes"][0]["path"] = "other.json"
    adversarial["file completion path mismatch"] = file_path_mismatch
    file_status_mismatch = copy.deepcopy(file_rows)
    file_status_mismatch[3]["item"]["status"] = "failed"
    adversarial["file completion status mismatch"] = file_status_mismatch

    agent_start = copy.deepcopy(message_rows)
    agent_start[2]["type"] = "item.started"
    agent_start[2]["item"]["status"] = "in_progress"
    adversarial["agent message cannot start"] = agent_start
    duplicate_message = copy.deepcopy(message_rows)
    duplicate_message.insert(3, copy.deepcopy(message_rows[2]))
    adversarial["duplicate agent terminal"] = duplicate_message

    adversarial["missing todo completion"] = (
        todo_rows[:3] + todo_rows[4:])
    todo_status_mismatch = copy.deepcopy(todo_rows)
    todo_status_mismatch[3]["item"]["status"] = "failed"
    adversarial["todo completion status mismatch"] = todo_status_mismatch

    turn_before_completion = copy.deepcopy(rows)
    turn_before_completion[3], turn_before_completion[4] = (
        turn_before_completion[4], turn_before_completion[3])
    adversarial["turn completes before command"] = turn_before_completion
    completion_before_start = copy.deepcopy(rows)
    completion_before_start[2], completion_before_start[3] = (
        completion_before_start[3], completion_before_start[2])
    adversarial["command completion before start"] = completion_before_start
    malformed_usage = copy.deepcopy(retained_rows)
    malformed_usage[-1]["usage"]["input_tokens"] = True
    adversarial["boolean terminal usage"] = malformed_usage
    extra_usage = copy.deepcopy(retained_rows)
    extra_usage[-1]["usage"]["unexpected"] = 1
    adversarial["extra terminal usage"] = extra_usage
    negative_usage = copy.deepcopy(retained_rows)
    negative_usage[-1]["usage"]["output_tokens"] = -1
    adversarial["negative terminal usage"] = negative_usage

    unknown_before = copy.deepcopy(rows)
    unknown_before.insert(0, {"type": "unrecognized.before"})
    adversarial["unknown event before thread"] = unknown_before
    unknown_inside = copy.deepcopy(rows)
    unknown_inside.insert(2, {"type": "unrecognized.lifecycle"})
    adversarial["unknown event inside turn"] = unknown_inside
    unknown_after = copy.deepcopy(rows)
    unknown_after.append({"type": "unrecognized.after"})
    adversarial["unknown event after terminal"] = unknown_after
    error_event = copy.deepcopy(rows)
    error_event.insert(2, {"type": "error", "message": "failed"})
    adversarial["unsupported error event"] = error_event
    terminal_event = copy.deepcopy(rows)
    terminal_event.append({"type": "terminal", "status": "completed"})
    adversarial["unsupported terminal event"] = terminal_event

    extra_started = copy.deepcopy(rows)
    extra_started[2]["unexpected"] = "value"
    adversarial["extra item-start root field"] = extra_started
    extra_completed = copy.deepcopy(rows)
    extra_completed[3]["unexpected"] = "value"
    adversarial["extra item-complete root field"] = extra_completed
    missing_started_item = copy.deepcopy(rows)
    missing_started_item[2].pop("item")
    adversarial["missing item-start payload"] = missing_started_item
    missing_completed_item = copy.deepcopy(rows)
    missing_completed_item[3].pop("item")
    adversarial["missing item-complete payload"] = missing_completed_item

    cross_thread_started = copy.deepcopy(rows)
    cross_thread_started[2]["thread_id"] = "foreign-thread"
    adversarial["cross-thread item start"] = cross_thread_started
    cross_thread_completed = copy.deepcopy(rows)
    cross_thread_completed[3]["thread_id"] = "foreign-thread"
    adversarial["cross-thread item completion"] = cross_thread_completed
    implicit_turn_started = copy.deepcopy(rows)
    implicit_turn_started[2]["turn_id"] = "invented-turn"
    adversarial["invented item-start turn"] = implicit_turn_started
    implicit_turn_completed = copy.deepcopy(rows)
    implicit_turn_completed[3]["turn_id"] = "invented-turn"
    adversarial["invented item-complete turn"] = implicit_turn_completed
    wrong_explicit_item_turn = copy.deepcopy(explicit_item_identity_rows)
    wrong_explicit_item_turn[3]["turn_id"] = "turn-b"
    adversarial["wrong explicit item turn"] = wrong_explicit_item_turn

    for label, index, value in (
            ("boolean item-start status", 2, True),
            ("null item-start status", 2, None),
            ("empty item-start status", 2, ""),
            ("completed item-start status", 2, "completed"),
            ("numeric item-complete status", 3, 1),
            ("in-progress item-complete status", 3, "in_progress"),
            ("failed item-complete root status", 3, "failed"),
            ("error item-complete root status", 3, "error")):
        malformed = copy.deepcopy(rows)
        malformed[index]["status"] = value
        adversarial[label] = malformed
    for label, invalid_rows in adversarial.items():
        observed = classify(raw_text(invalid_rows))
        assert observed[:2] == ("INVALID", "INVALID"), (
            label, observed)

    explicit_item_identity = classify(raw_text(explicit_item_identity_rows))
    assert explicit_item_identity[:2] == ("PASS", "PASS"), (
        explicit_item_identity)

    duplicate_key_raw = current_raw.replace(
        '{"type":"turn.started"}',
        '{"type":"turn.started","type":"turn.started"}', 1)
    duplicate_key = classify(duplicate_key_raw)
    assert duplicate_key[:2] == ("INVALID", "INVALID"), duplicate_key

    duplicate_item_key_raw = current_raw.replace(
        '{"item":{', '{"item":{},"item":{', 1)
    duplicate_item_key = classify(duplicate_item_key_raw)
    assert duplicate_item_key[:2] == ("INVALID", "INVALID"), (
        duplicate_item_key)

    nested = "null"
    for _ in range(module.MAX_JSON_DEPTH + 1):
        nested = "[" + nested + "]"
    depth_raw = current_raw.replace(
        '{"type":"turn.started"}',
        '{"type":"turn.started","unexpected":' + nested + "}", 1)
    depth = classify(depth_raw)
    assert depth[:2] == ("INVALID", "INVALID"), depth


def assert_independent_import_boundary():
    tree = ast.parse(REDERIVER.read_text(encoding="utf-8"))
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.append(node.module)
    forbidden = {
        "eval.b3v4_campaign", "b3v4_campaign",
        "eval.hosts", "hosts", "eval.runner", "runner",
        "eval.lib.scoring", "lib.scoring",
        "eval.adapters", "adapters",
        "eval.campaign_lifecycle", "campaign_lifecycle",
        "eval.validate_b3v4_freeze", "validate_b3v4_freeze",
        "eval.b3v4_contract", "b3v4_contract",
        "eval.evaluated_surfaces", "evaluated_surfaces",
        "eval.provisional_integration", "provisional_integration",
    }
    assert not forbidden.intersection(imports), imports


def rebind_capture(bundle):
    artifacts = bundle / "artifacts"
    terminal_path = artifacts / "host-read-terminal.json"
    terminal = json.loads(terminal_path.read_text(encoding="utf-8"))
    terminal["hashes"] = {
        name: sha((artifacts / name).read_bytes())
        for name in CAPTURE_FILES[:-1]
    }
    write(terminal_path, terminal)
    capture_manifest_path = artifacts / "host-read-manifest.json"
    capture_manifest = json.loads(capture_manifest_path.read_text(encoding="utf-8"))
    capture_manifest["files"] = {
        name: sha((artifacts / name).read_bytes()) for name in CAPTURE_FILES
    }
    write(capture_manifest_path, capture_manifest)
    artifact_manifest_path = bundle / "artifact-manifest.json"
    artifact_manifest = json.loads(artifact_manifest_path.read_text(encoding="utf-8"))
    for rel in artifact_manifest["files"]:
        artifact_manifest["files"][rel] = sha((artifacts / rel).read_bytes())
    write(artifact_manifest_path, artifact_manifest)
    manifest_path = bundle / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["artifact_manifest_sha256"] = sha(artifact_manifest_path.read_bytes())
    write(manifest_path, manifest)


def rebind_attempt_seal(attempt):
    attempt = pathlib.Path(attempt)
    status_raw = (attempt / "attempt-status.json").read_bytes()
    status = json.loads(status_raw)
    attestation_raw = (attempt / "host-attestation.json").read_bytes()
    readiness_raw = (attempt / "launch-readiness.json").read_bytes()
    terminal_path = attempt / "attempt-terminal.json"
    terminal = json.loads(terminal_path.read_text(encoding="utf-8"))
    if terminal.get("overall_status") not in ("PASS", "FAIL"):
        return
    terminal["completed_attempt_seal"] = {
        "schema": "implementaudit-b3v4-completed-attempt-seal-v1",
        "campaign": status["campaign"],
        "freeze_sha256": status["freeze_sha256"],
        "contract_sha256": status["contract_sha256"],
        "mission": status["mission"],
        "execution_mode": terminal["execution_mode"],
        "overall_status": terminal["overall_status"],
        "resolved_model": terminal["resolved_model"],
        "host_run_root": terminal["host_run_root"],
        "official_overall_status": terminal["official_overall_status"],
        "official_verdict_sha256": terminal["official_verdict_sha256"],
        "stop_reason": terminal["stop_reason"],
        "error_type": terminal["error_type"],
        "completed_at": terminal["completed_at"],
        "attempt_name": attempt.name,
        "attempt_status_sha256": sha(status_raw),
        "host_attestation_sha256": sha(attestation_raw),
        "launch_readiness_sha256": sha(readiness_raw),
        "host_custody_manifest_sha256": sha(
            custody_manifest_bytes(attempt / "host-custody")),
    }
    write(terminal_path, terminal)


def rebind_bundle_and_official(root, bundle, capture=False):
    """Rebind every enclosing digest after a retained-evidence mutation."""
    root = pathlib.Path(root)
    bundle = pathlib.Path(bundle)
    if capture:
        rebind_capture(bundle)
    manifest_path = bundle / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    for name, key in (
            ("fixture.json", "fixture_sha256"),
            ("prompt.txt", "prompt_sha256"),
            ("events.jsonl", "events_sha256"),
            ("repo-before.json", "repo_before_sha256"),
            ("repo-after.json", "repo_after_sha256"),
            ("artifact-manifest.json", "artifact_manifest_sha256"),
            ("repo-comparison.json", "repo_comparison_sha256")):
        path = bundle / name
        if path.is_file() and key in manifest:
            manifest[key] = sha(path.read_bytes())
    write(manifest_path, manifest)
    attempt = bundle.parents[2]
    verdict_path = attempt / "official-verdict.json"
    verdict = json.loads(verdict_path.read_text(encoding="utf-8"))
    for key in (
            "run_id", "fixture_id", "fixture_sha256", "prompt_sha256",
            "events_sha256", "product_tag", "product_commit", "product_tree",
            "installed_payload_sha256", "harness_commit", "adapter_name",
            "adapter_version", "adapter_sha256", "model_requested",
            "model_resolved", "host", "started_at", "ended_at"):
        if key in manifest:
            verdict[key] = manifest[key]
    verdict["bundle_sha256"] = bundle_hash(bundle)
    write(verdict_path, verdict)
    terminal_path = attempt / "attempt-terminal.json"
    terminal = json.loads(terminal_path.read_text(encoding="utf-8"))
    terminal["official_verdict_sha256"] = sha(verdict_path.read_bytes())
    write(terminal_path, terminal)
    rebind_attempt_seal(attempt)


def mutate_mapping(path, object_path, mode, key):
    value = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
    owner = value
    for part in object_path:
        owner = owner[part]
    if mode == "extra":
        owner["mutable_summary"] = "PASS"
    else:
        del owner[key]
    write(path, value)


def mutate_jsonl(path, row_index, object_path, mode, key):
    rows = [json.loads(line) for line in pathlib.Path(path).read_text(
        encoding="utf-8").splitlines() if line]
    owner = rows[row_index]
    for part in object_path:
        owner = owner[part]
    if mode == "extra":
        owner["mutable_summary"] = "PASS"
    else:
        del owner[key]
    pathlib.Path(path).write_bytes(b"".join(encoded(row) for row in rows))


def rebase_campaign_paths(root):
    """Make a copied synthetic campaign's absolute custody paths truthful."""
    root = pathlib.Path(root)
    root_stat = os.lstat(root)
    manifest_path = root / "campaign-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["campaign_root_identity"] = {
        "device": root_stat.st_dev,
        "inode": root_stat.st_ino,
        "mode": root_stat.st_mode,
    }
    write(manifest_path, manifest)
    for attempt in root.glob("attempt-*"):
        host_root = attempt / "host-custody" / attempt.name
        terminal_path = attempt / "attempt-terminal.json"
        terminal = json.loads(terminal_path.read_text(encoding="utf-8"))
        terminal["host_run_root"] = str(host_root)
        write(terminal_path, terminal)
        parent_path = host_root / "terminal.json"
        parent = json.loads(parent_path.read_text(encoding="utf-8"))
        parent["detail"] = str(host_root / "bundle")
        write(parent_path, parent)
        bundle = host_root / "bundle"
        process_path = bundle / "artifacts" / "process-started.json"
        process = json.loads(process_path.read_text(encoding="utf-8"))
        process["trusted_spawn_guard"]["campaign_root_identity"] = \
            manifest["campaign_root_identity"]
        write(process_path, process)
        rebind_bundle_and_official(root, bundle, capture=True)


def first_bundle(root, index=0):
    attempt = sorted(pathlib.Path(root).glob("attempt-*"))[index]
    return attempt, attempt / "host-custody" / attempt.name / "bundle"


def mutate_official(root, mutate):
    attempt, _ = first_bundle(root)
    verdict_path = attempt / "official-verdict.json"
    verdict = json.loads(verdict_path.read_text(encoding="utf-8"))
    mutate(verdict)
    write(verdict_path, verdict)
    terminal_path = attempt / "attempt-terminal.json"
    terminal = json.loads(terminal_path.read_text(encoding="utf-8"))
    terminal["official_verdict_sha256"] = sha(verdict_path.read_bytes())
    write(terminal_path, terminal)
    rebind_attempt_seal(attempt)


def semantic_mutation(root, label):
    attempt, bundle = first_bundle(root)
    artifacts = bundle / "artifacts"
    if label == "empty-matrix":
        matrix_path = artifacts / "host-read-matrix.json"
        matrix = json.loads(matrix_path.read_text(encoding="utf-8"))
        matrix["specs"] = {}
        write(matrix_path, matrix)
    elif label == "contradictory-matrix":
        matrix_path = artifacts / "host-read-matrix.json"
        matrix = json.loads(matrix_path.read_text(encoding="utf-8"))
        row = next(iter(matrix["specs"].values()))
        row["property_status"] = "INCOMPLETE"
        row["overall_status"] = "INCOMPLETE"
        write(matrix_path, matrix)
    elif label == "partial-post-probe":
        write(artifacts / "host-read-post-probe.json", {})
    elif label == "arbitrary-native-session":
        write(artifacts / "host-session.raw", {"unbound": "arbitrary"})
    elif label == "trace-raw-disagreement":
        trace_path = artifacts / "host-tool-trace.json"
        trace = json.loads(trace_path.read_text(encoding="utf-8"))
        trace["actions"][0]["id"] = "not-in-raw-stream"
        write(trace_path, trace)
    elif label == "codex-action-type-contradiction":
        raw_path = artifacts / "host-stdout.raw"
        events = [json.loads(line) for line in raw_path.read_text(
            encoding="utf-8").splitlines()]
        completion = next(event for event in events
                          if event.get("type") == "item.completed" and
                          (event.get("item") or {}).get("type") == "file_change")
        completion["item"]["type"] = "command_execution"
        completion["item"]["command"] = "true"
        completion["item"]["aggregated_output"] = ""
        completion["item"]["exit_code"] = 0
        raw_path.write_bytes(b"".join(encoded(event) for event in events))
    elif label in ("claude-missing-error-state", "claude-cross-session",
                   "repeated-distinct-write"):
        second_attempt, bundle = first_bundle(root, 2)
        artifacts = bundle / "artifacts"
        raw_path = artifacts / "host-stdout.raw"
        events = [json.loads(line) for line in raw_path.read_text(
            encoding="utf-8").splitlines()]
        if label == "claude-missing-error-state":
            result = next(event for event in events
                          if any(block.get("type") == "tool_result"
                                 for block in event.get("message", {}).get(
                                     "content", [])))
            del result["message"]["content"][0]["is_error"]
        elif label == "claude-cross-session":
            events[1]["session_id"] = "cross-session"
        else:
            name = second_attempt.name
            capsule = make_fixture()["allowed_paths"][0]
            events.extend([
                {"type": "assistant", "session_id": name,
                 "message": {"content": [{"type": "tool_use",
                  "id": "write-again", "name": "Write",
                  "input": {"file_path": capsule, "content": "{}"}}]}},
                {"type": "user", "session_id": name,
                 "message": {"content": [{"type": "tool_result",
                  "tool_use_id": "write-again", "content": "overwritten",
                  "is_error": False}]}}])
        raw_path.write_bytes(b"".join(encoded(event) for event in events))
    else:
        raise AssertionError(label)
    rebind_capture(bundle)


def stop_after_first(root, status):
    root = pathlib.Path(root)
    first, _ = first_bundle(root)
    terminal_path = first / "attempt-terminal.json"
    terminal = json.loads(terminal_path.read_text(encoding="utf-8"))
    terminal.update({
        "overall_status": status, "official_overall_status": None,
        "official_verdict_sha256": None,
        "stop_reason": ("mission-execution-exception" if status == "ERROR"
                        else "invalid-or-error-halts-campaign"),
        "error_type": "RuntimeError" if status == "ERROR" else None,
        "completed_attempt_seal": None,
    })
    if status == "ERROR":
        terminal["resolved_model"] = None
        terminal["host_run_root"] = None
    write(terminal_path, terminal)
    (first / "official-verdict.json").unlink()
    for attempt in sorted(root.glob("attempt-*"))[1:]:
        shutil.rmtree(attempt)


def rebind_freeze(root, packet):
    packet_bytes = json.dumps(packet, sort_keys=True).encode()
    freeze_sha = sha(packet_bytes)
    write(root / "campaign-freeze.json", packet_bytes)
    custody_path = root / "campaign-manifest.json"
    custody = json.loads(custody_path.read_text(encoding="utf-8"))
    custody["freeze_sha256"] = freeze_sha
    write(custody_path, custody)
    for mission in packet["missions"]:
        name = (f"attempt-{mission['index']:03d}-{mission['config']}-"
                f"{mission['arm']}-r{mission['rep']}")
        status_path = root / name / "attempt-status.json"
        status = json.loads(status_path.read_text(encoding="utf-8"))
        status["freeze_sha256"] = freeze_sha
        write(status_path, status)


def expect_freeze_invalid(module, root, packet, fragment):
    rebind_freeze(root, packet)
    try:
        module.rederive_campaign(root / "campaign-freeze.json", root)
    except module.EvidenceInvalid as exc:
        assert fragment in str(exc), str(exc)
    else:
        raise AssertionError(
            f"rederiver accepted drifted freeze; wanted {fragment!r}")


def assert_retained_schema_matrix(module):
    """Every retained object boundary rejects rebound extra/missing fields."""
    with tempfile.TemporaryDirectory(prefix="b3v4-schema-base-") as tmp:
        baseline = pathlib.Path(tmp) / "baseline"
        build_campaign(baseline)
        cases = [
            # label, attempt index, relative path, nested path, required key,
            # capture-chain, snapshot-internal-hash, JSONL row
            ("bundle-manifest", 0, "manifest.json", (), "product_tag",
             False, False, None),
            ("bundle-policy", 0, "manifest.json", ("policy_requested",),
             "network", False, False, None),
            ("bundle-model-observation", 0, "manifest.json",
             ("models_observed", 0), "source", False, False, None),
            ("event-row", 0, "events.jsonl", (), "recorded_at",
             False, False, 0),
            ("repo-before", 0, "repo-before.json", (), "renames",
             False, True, None),
            ("repo-after", 0, "repo-after.json", (), "renames",
             False, True, None),
            ("snapshot-untracked-entry", 0, "repo-after.json",
             ("untracked", make_fixture()["allowed_paths"][0]), "sha256",
             False, True, None),
            ("snapshot-worktree-entry", 0, "repo-after.json",
             ("worktree_files", make_fixture()["allowed_paths"][0]), "sha256",
             False, True, None),
            ("artifact-manifest", 0, "artifact-manifest.json", (), "files",
             False, False, None),
            ("repo-comparison", 0, "repo-comparison.json", (),
             "committed_files", False, False, None),
            ("host-profile", 0, "artifacts/host-read-profile.json", (),
             "authority", True, False, None),
            ("host-profile-repo", 0, "artifacts/host-read-profile.json",
             ("repo",), "real_root", True, False, None),
            ("codex-profile-shell", 0, "artifacts/host-read-profile.json",
             ("shell",), "logical_path", True, False, None),
            ("codex-profile-wrapper", 0, "artifacts/host-read-profile.json",
             ("outer_wrapper",), "max_unwrap_layers", True, False, None),
            ("codex-profile-executable", 0,
             "artifacts/host-read-profile.json", ("executables", "cat"),
             "kind", True, False, None),
            ("host-preimages", 0, "artifacts/host-read-preimages.json", (),
             "schema", True, False, None),
            ("host-preimages-repo", 0,
             "artifacts/host-read-preimages.json", ("repo",), "real_root",
             True, False, None),
            ("host-preimage-target", 0,
             "artifacts/host-read-preimages.json",
             ("targets", ".IMPLEMENTAUDIT/runs/audit-closure-a7Kx2f/STATE.md"),
             "relative_path", True, False, None),
            ("replay-check-row", 0,
             "artifacts/host-read-replay-spec.json", ("checks", 0), "key",
             True, False, None),
            ("run-intent", 0, "artifacts/run-intent.json", (), "schema",
             True, False, None),
            ("process-started", 0, "artifacts/process-started.json", (),
             "started_at", True, False, None),
            ("trace-action", 0, "artifacts/host-tool-trace.json",
             ("actions", 0), "action_type", True, False, None),
            ("derived-transform", 0, "artifacts/derived-transform.json", (),
             "rules", True, False, None),
            ("codex-stdout-row", 0, "artifacts/host-stdout.raw", (),
             "thread_id", True, False, 0),
            ("codex-stdout-item", 0, "artifacts/host-stdout.raw", ("item",),
             "command", True, False, 2),
            ("codex-stdout-change", 0, "artifacts/host-stdout.raw",
             ("item", "changes", 0), "kind", True, False, 6),
            ("codex-session-row", 0, "artifacts/host-session.raw", (),
             "timestamp", True, False, 0),
            ("codex-session-payload", 0, "artifacts/host-session.raw",
             ("payload",), "cwd", True, False, 0),
        ]
        accepted = []
        for label, attempt_index, relative, object_path, required_key, \
                capture, snapshot_hash, row in cases:
            for mode in ("extra", "missing"):
                root = pathlib.Path(tmp) / f"case-{label}-{mode}"
                shutil.copytree(baseline, root)
                rebase_campaign_paths(root)
                attempt, bundle = first_bundle(root, attempt_index)
                target = bundle / relative
                if row is None:
                    mutate_mapping(target, object_path, mode, required_key)
                else:
                    mutate_jsonl(target, row, object_path, mode, required_key)
                if relative == "artifacts/host-session.raw":
                    (bundle / "artifacts/raw-host-events.jsonl").write_bytes(
                        target.read_bytes())
                if snapshot_hash:
                    snap = json.loads(target.read_text(encoding="utf-8"))
                    body = {key: value for key, value in snap.items()
                            if key not in ("snapshot_sha256", "changed_files",
                                           "unauthorized")}
                    snap["snapshot_sha256"] = sha(json.dumps(
                        body, sort_keys=True).encode())
                    write(target, snap)
                rebind_bundle_and_official(root, bundle, capture=capture)
                result = module.rederive_campaign(
                    root / "campaign-freeze.json", root)
                if result["luna_stage_status"] != "INVALID":
                    accepted.append(
                        f"{label}:{mode}={result['luna_stage_status']}")

        fixture_cases = [
            ("fixture-root", (), "title"),
            ("fixture-authorization", ("authorization_boundary",),
             "forbidden_actions"),
            ("fixture-host-checks", ("host_checks",), "artifact"),
            ("fixture-json-check", ("host_checks", "specs", 0), "equals"),
            ("fixture-path-check", ("host_checks", "specs", 1), "reads"),
            ("fixture-property", ("properties", 0), "describes"),
            ("fixture-summary-rule", ("properties", 0, "rule"), "key"),
            ("fixture-change-rule", ("properties", 3, "rule"), "required"),
        ]
        canonical = make_fixture()
        for label, object_path, required_key in fixture_cases:
            for mode in ("extra", "missing"):
                fixture = copy.deepcopy(canonical)
                owner = fixture
                for part in object_path:
                    owner = owner[part]
                if mode == "extra":
                    owner["mutable_summary"] = "PASS"
                else:
                    del owner[required_key]
                root = pathlib.Path(tmp) / f"case-{label}-{mode}"
                build_campaign(root, fixture_override=fixture)
                result = module.rederive_campaign(
                    root / "campaign-freeze.json", root)
                if result["luna_stage_status"] != "INVALID":
                    accepted.append(
                        f"{label}:{mode}={result['luna_stage_status']}")

        for mode in ("extra", "missing"):
            root = pathlib.Path(tmp) / f"case-host-terminal-{mode}"
            shutil.copytree(baseline, root)
            rebase_campaign_paths(root)
            attempt, bundle = first_bundle(root)
            parent_path = bundle.parent / "terminal.json"
            mutate_mapping(parent_path, (), mode, "policy_resolved")
            result = module.rederive_campaign(
                root / "campaign-freeze.json", root)
            if result["luna_stage_status"] != "INVALID":
                accepted.append(
                    f"host-terminal:{mode}={result['luna_stage_status']}")

        contract = json.loads((HERE / "b3v4_contract.json").read_text(
            encoding="utf-8"))
        contract_cases = [
            ("contract-encoding", ("encoding",), "writes"),
            ("contract-execution", ("execution",), "unexpected_attempt"),
            ("contract-artifact-descriptor",
             ("artifacts", "bundle_manifest"), "role"),
            ("contract-lifecycle", ("lifecycle_schemas",),
             "attempt_terminal"),
        ]
        for label, object_path, required_key in contract_cases:
            for mode in ("extra", "missing"):
                changed = copy.deepcopy(contract)
                owner = changed
                for part in object_path:
                    owner = owner[part]
                if mode == "extra":
                    owner["mutable_summary"] = "PASS"
                else:
                    del owner[required_key]
                try:
                    module._validate_contract_declaration(changed)
                except module.EvidenceInvalid:
                    pass
                else:
                    accepted.append(f"{label}:{mode}=ACCEPTED")
        assert not accepted, (
            "rederiver accepted exact-schema mutations: " +
            ", ".join(accepted))


def assert_host_attestation_custody_matrix(module):
    """Retained attestations stay frozen even after enclosing hash rebound."""
    accepted = []
    cases = ("missing", "extra-rebound", "malformed-rebound", "substituted",
             "hash-mismatch", "wrong-path", "wrong-config", "wrong-host",
             "wrong-model")
    for label in cases:
        with tempfile.TemporaryDirectory(prefix=f"b3v4-attestation-{label}-") as tmp:
            root = pathlib.Path(tmp) / "campaign"
            packet = build_campaign(root)
            first = root / "attempt-000-L-candidate-r1"
            attestation_path = first / "host-attestation.json"
            status_path = first / "attempt-status.json"
            status = json.loads(status_path.read_text(encoding="utf-8"))
            if label == "missing":
                attestation_path.unlink()
            elif label in ("extra-rebound", "malformed-rebound"):
                if label == "extra-rebound":
                    value = json.loads(attestation_path.read_text(encoding="utf-8"))
                    value["mutable_summary"] = "PASS"
                    raw = encoded(value)
                else:
                    raw = (b'{"executables":{"cat":"posix:cat"},'
                           b'"id":"b3v4-L-host","id":"b3v4-L-host",'
                           b'"shell_dialect":"posix"}\n')
                digest = sha(raw)
                packet["configurations"]["L"]["host_attestation"]["sha256"] = digest
                for mission in packet["missions"]:
                    if mission["config"] != "L":
                        continue
                    name = (f"attempt-{mission['index']:03d}-{mission['config']}-"
                            f"{mission['arm']}-r{mission['rep']}")
                    attempt = root / name
                    write(attempt / "host-attestation.json", raw)
                    bound_path = attempt / "attempt-status.json"
                    bound = json.loads(bound_path.read_text(encoding="utf-8"))
                    bound["host_attestation_binding"]["sha256"] = digest
                    write(bound_path, bound)
                rebind_freeze(root, packet)
            elif label == "substituted":
                raw = encoded({
                    "id": "substituted-host", "shell_dialect": "posix",
                    "executables": {"cat": "posix:cat"}})
                write(attestation_path, raw)
                status["host_attestation_binding"]["sha256"] = sha(raw)
                write(status_path, status)
            elif label == "hash-mismatch":
                attestation_path.write_bytes(attestation_path.read_bytes() + b" ")
            elif label == "wrong-path":
                alternate = first / "alternate-attestation.json"
                attestation_path.rename(alternate)
                status["host_attestation_binding"]["path"] = alternate.name
                write(status_path, status)
            else:
                key, value = {
                    "wrong-config": ("config", "O"),
                    "wrong-host": ("host", "Windows Claude CLI"),
                    "wrong-model": ("model_resolved_required", "claude-opus-4-8"),
                }[label]
                status["host_attestation_binding"][key] = value
                write(status_path, status)
            try:
                result = module.rederive_campaign(
                    root / "campaign-freeze.json", root)
            except module.EvidenceInvalid:
                continue
            if result["luna_stage_status"] != "INVALID" or result["accepted"]:
                accepted.append(f"{label}={result['luna_stage_status']}")
    assert not accepted, (
        "rederiver accepted host attestation custody mutations: " +
        ", ".join(accepted))


def assert_attempt_status_numeric_aliases_rejected(module):
    """Retained mission identities use JSON types, not Python equality."""
    assert module._exact_json_equal({"value": [0.0]}, {"value": [0.0]})
    assert not module._exact_json_equal(0.0, -0.0)
    assert not module._exact_json_equal(False, 0)
    left = []
    right = []
    left_cursor = left
    right_cursor = right
    for _ in range(400):
        left_cursor.append([])
        right_cursor.append([])
        left_cursor = left_cursor[0]
        right_cursor = right_cursor[0]
    assert module._exact_json_equal(left, right)
    left_cursor.append(left)
    right_cursor.append(right)
    assert not module._exact_json_equal(left, right)
    with tempfile.TemporaryDirectory(prefix="b3v4-status-alias-") as tmp:
        root = pathlib.Path(tmp) / "campaign"
        build_campaign(root)
        first = root / "attempt-000-L-candidate-r1"
        status_path = first / "attempt-status.json"
        original = json.loads(status_path.read_text(encoding="utf-8"))
        cases = (
            ("index", False), ("index", 0.0), ("index", -0.0),
            ("rep", True), ("rep", 1.0),
        )
        accepted = []
        for key, alias in cases:
            changed = copy.deepcopy(original)
            changed["mission"][key] = alias
            write(status_path, changed)
            result = module.rederive_campaign(
                root / "campaign-freeze.json", root)
            if result["luna_stage_status"] != "INVALID":
                accepted.append(f"{key}={alias!r}:{result['luna_stage_status']}")
        write(status_path, original)
        assert not accepted, (
            "rederiver accepted numeric mission aliases: " +
            ", ".join(accepted))


def assert_remaining_exact_scalar_aliases_rejected(module):
    declaration = json.loads(
        (HERE / "b3v4_contract.json").read_text(encoding="utf-8"))
    for alias in (0, 0.0, -0.0, True):
        changed = copy.deepcopy(declaration)
        changed["execution"]["final_acceptance"] = alias
        try:
            module._validate_contract_declaration(changed)
        except module.EvidenceInvalid:
            pass
        else:
            raise AssertionError(
                f"independent contract accepted final_acceptance={alias!r}")

    for alias in (6.0, True):
        with tempfile.TemporaryDirectory(prefix="b3v4-stage-alias-") as tmp:
            root = pathlib.Path(tmp) / "campaign"
            packet = build_campaign(root)
            packet["luna_stage"]["mission_count"] = alias
            expect_freeze_invalid(module, root, packet, "luna_stage")

    with tempfile.TemporaryDirectory(prefix="b3v4-matrix-alias-") as tmp:
        root = pathlib.Path(tmp) / "campaign"
        build_campaign(root)
        _attempt, bundle = first_bundle(root, 0)
        matrix_path = bundle / "artifacts" / "host-read-matrix.json"
        matrix = json.loads(matrix_path.read_text(encoding="utf-8"))
        for row in matrix["specs"].values():
            row["borrowed_completion"] = 0
        write(matrix_path, matrix)
        rebind_bundle_and_official(root, bundle, capture=True)
        result = module.rederive_campaign(
            root / "campaign-freeze.json", root)
        assert result["luna_stage_status"] == "INVALID", result


def assert_independent_output_custody(module):
    result = {
        "schema": "implementaudit-b3v4-luna-independent-rederivation-v2",
        "campaign": "b3v4-sol-luna-r2", "freeze_sha256": "a" * 64,
        "contract_sha256": module.CONTRACT_SHA256,
        "luna_stage_status": "INVALID", "disposition": "ANDON_STOPPED",
        "luna_stage_accepted": False, "accepted": False,
        "mission_count": 0, "missions": [],
        "claims": copy.deepcopy(module.FINAL_CLAIMS), "reason": "fixture",
    }
    with tempfile.TemporaryDirectory(prefix="b3v4-output-custody-") as tmp:
        base = pathlib.Path(tmp)
        root = base / "campaign"
        root.mkdir()
        outside = base / "outside-result.json"
        outside.write_text("outside\n", encoding="utf-8")
        output = root / "b3v4-luna-independent-rederivation.json"
        try:
            os.symlink(outside, output)
        except (NotImplementedError, OSError):
            print("REDERIVER_OUTPUT_LEAF_SYMLINK=SKIP")
        else:
            try:
                module.write_rederivation(output, result, root=root)
            except module.EvidenceInvalid:
                pass
            else:
                raise AssertionError("output leaf symlink accepted")
            output.unlink()
        os.link(outside, output)
        try:
            module.write_rederivation(output, result, root=root)
        except module.EvidenceInvalid:
            pass
        else:
            raise AssertionError("output leaf hardlink accepted")
        output.unlink()

    if os.name == "nt":
        with tempfile.TemporaryDirectory(
                prefix="b3v4-output-parent-junction-") as tmp:
            base = pathlib.Path(tmp)
            target = base / "target"
            target.mkdir()
            junction = base / "junction"
            made = subprocess.run(
                ["cmd", "/c", "mklink", "/J", str(junction), str(target)],
                capture_output=True, text=True)
            if made.returncode:
                print("REDERIVER_OUTPUT_PARENT_JUNCTION=SKIP:mklink")
            else:
                try:
                    root = junction / "campaign"
                    root.mkdir()
                    output = (
                        root /
                        "b3v4-luna-independent-rederivation.json")
                    try:
                        module.write_rederivation(output, result, root=root)
                    except module.EvidenceInvalid:
                        pass
                    else:
                        raise AssertionError(
                            "output ancestor junction accepted")
                finally:
                    if (target / "campaign" /
                            "b3v4-luna-independent-rederivation.json").exists():
                        (target / "campaign" /
                         "b3v4-luna-independent-rederivation.json").unlink()
                    if (target / "campaign").exists():
                        (target / "campaign").rmdir()
                    os.rmdir(junction)


def assert_deep_cli_failure_normalized(module):
    with tempfile.TemporaryDirectory(prefix="b3v4-deep-cli-") as tmp:
        root = pathlib.Path(tmp) / "campaign"
        root.mkdir()
        intent = pathlib.Path(tmp) / "deep.json"
        intent.write_bytes(b"[" * 1100 + b"0" + b"]" * 1100)
        output = root / "b3v4-luna-independent-rederivation.json"
        try:
            module.main([
                str(intent), "--campaign-root", str(root),
                "--output", str(output)])
        except SystemExit as exc:
            assert "inherited campaign handle" in str(exc), str(exc)
        else:
            raise AssertionError("qualifying output accepted without custody")
        assert not output.exists()
        if os.name != "posix":
            return
        descriptor = os.open(
            root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        try:
            exit_code = module.main([
                str(intent), "--campaign-root", str(root),
                "--output", str(output),
                "--custody-fd", str(descriptor)])
        finally:
            os.close(descriptor)
        assert exit_code == 2
        value = json.loads(output.read_text(encoding="utf-8"))
        assert value["luna_stage_status"] == "INVALID"
    assert value["luna_stage_accepted"] is False


def assert_inherited_campaign_handle_contract(module):
    if os.name != "posix":
        print("REDERIVER_INHERITED_CUSTODY=SKIP:requires-posix")
        return
    with tempfile.TemporaryDirectory(
            prefix="b3v4-rederive-inherited-custody-") as tmp:
        root = pathlib.Path(tmp) / "campaign"
        build_campaign(root)
        descriptor = os.open(
            root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        output = root / "b3v4-luna-independent-rederivation.json"
        try:
            completed = subprocess.run([
                sys.executable, str(REDERIVER),
                str(root / "campaign-freeze.json"),
                "--campaign-root", str(root),
                "--output", str(output),
                "--custody-fd", str(descriptor),
            ], capture_output=True, text=True, pass_fds=(descriptor,))
            assert completed.returncode == 0, (
                completed.stdout, completed.stderr)
            value = json.loads(output.read_text(encoding="utf-8"))
            assert value["luna_stage_accepted"] is True, value
        finally:
            os.close(descriptor)

    with tempfile.TemporaryDirectory(
            prefix="b3v4-rederive-inherited-drift-") as tmp:
        root = pathlib.Path(tmp) / "campaign"
        build_campaign(root)
        descriptor = os.open(
            root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        original = root.with_name("campaign-original")
        os.rename(root, original)
        shutil.copytree(original, root)
        try:
            try:
                module.rederive_campaign(
                    root / "campaign-freeze.json", root,
                    custody_fd=descriptor)
            except module.EvidenceInvalid as exc:
                assert "handle/path drift" in str(exc), str(exc)
            else:
                raise AssertionError("rebound campaign root accepted")
        finally:
            os.close(descriptor)

    with tempfile.TemporaryDirectory(
            prefix="b3v4-rederive-inherited-loss-") as tmp:
        root = pathlib.Path(tmp) / "campaign"
        build_campaign(root)
        descriptor = os.open(
            root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        os.close(descriptor)
        try:
            module.rederive_campaign(
                root / "campaign-freeze.json", root,
                custody_fd=descriptor)
        except module.EvidenceInvalid as exc:
            assert "handle unavailable" in str(exc), str(exc)
        else:
            raise AssertionError("lost campaign handle accepted")


def nested_json_bytes(kind, depth):
    if kind == "array":
        opening, closing = [b"["] * depth, [b"]"] * depth
    elif kind == "object":
        opening, closing = [b'{"x":'] * depth, [b"}"] * depth
    else:
        opening = [b"[" if index % 2 == 0 else b'{"x":'
                   for index in range(depth)]
        closing = [b"]" if index % 2 == 0 else b"}"
                   for index in reversed(range(depth))]
    return b'{"value":' + b"".join(opening) + b"0" + \
        b"".join(closing) + b"}"


def nested_policy_value(total_depth):
    # The retained host-terminal object is depth zero and policy_resolved is
    # depth one.  Add total_depth - 1 descendants below that policy root.
    value = {"leaf": "valid"}
    for _ in range(total_depth - 1):
        value = {"nested": value}
    return value


def assert_exact_depth_parity(module):
    accepted_over_limit = []
    rejected_within_limit = []
    for kind in ("array", "object", "mixed"):
        for depth in (510, 511, 512, 513):
            raw = nested_json_bytes(kind, depth)
            official_accepted = True
            try:
                official_contract.decode_json_bytes(
                    raw, f"official {kind} depth {depth}",
                    require_object=True)
            except ValueError as exc:
                official_accepted = False
                assert "exceeds JSON depth limit" in str(exc), str(exc)
            assert official_accepted is (depth <= 511), (
                kind, depth, official_accepted)
            try:
                module._decode_json(
                    raw, f"independent {kind} depth {depth}",
                    "depth fixture malformed", require_object=True)
            except module.EvidenceInvalid as exc:
                if depth <= 511:
                    rejected_within_limit.append(
                        f"{kind}-{depth}:{str(exc)}")
                else:
                    assert "depth" in str(exc) or "resource" in str(exc), str(exc)
            else:
                if depth >= 512:
                    accepted_over_limit.append(f"{kind}-{depth}")
    assert not rejected_within_limit and not accepted_over_limit, (
        "independent depth parity drift: rejected-valid=" +
        ", ".join(rejected_within_limit) + "; accepted-invalid=" +
        ", ".join(accepted_over_limit))


def assert_post_decode_model_traversal(module):
    shared = {"finite": -0.0}
    module._validate_strict_json_model(
        {"left": shared, "right": shared}, "shared acyclic fixture")
    cycle = []
    cycle.append(cycle)
    invalid = [
        ("cycle", cycle),
        ("tuple", (1, 2)),
        ("non-string-key", {1: "invalid"}),
        ("non-finite", {"value": float("inf")}),
    ]
    for label, value in invalid:
        try:
            module._validate_strict_json_model(value, label)
        except module.EvidenceInvalid:
            pass
        else:
            raise AssertionError(
                f"independent strict-model traversal accepted {label}")


def assert_retained_depth_boundary(module):
    results = {}
    for depth in (511, 512):
        with tempfile.TemporaryDirectory(
                prefix=f"b3v4-retained-depth-{depth}-") as tmp:
            root = pathlib.Path(tmp) / "campaign"
            build_campaign(root)
            first = root / "attempt-000-L-candidate-r1"
            host_terminal_path = (
                first / "host-custody" / first.name / "terminal.json")
            host_terminal = json.loads(
                host_terminal_path.read_text(encoding="utf-8"))
            host_terminal["policy_resolved"] = nested_policy_value(depth)
            write(host_terminal_path, host_terminal)
            rebind_attempt_seal(first)
            result = module.rederive_campaign(
                root / "campaign-freeze.json", root)
            results[depth] = result
    assert results[511]["luna_stage_status"] == "PASS", results[511]
    assert results[511]["luna_stage_accepted"] is True, results[511]
    assert (results[512]["luna_stage_status"] != "PASS" and
            results[512]["luna_stage_accepted"] is False), (
        "retained depth-512 evidence produced Luna PASS: " +
        repr(results[512]))


def assert_lossless_numeric_domain_rejected(module):
    tokens = (
        "1e400",
        "-1e400",
        "1e-400",
        "0.100000000000000005",
        "4.9406564584124654e-324",
    )
    direct_accepts = []
    raw_exceptions = []
    for token in tokens:
        try:
            module._decode_json(
                f'{{"value":{token}}}'.encode(),
                "numeric-domain fixture",
                "numeric-domain fixture malformed",
                require_object=True)
        except module.EvidenceInvalid:
            pass
        except Exception as exc:
            raw_exceptions.append(f"{token}:{type(exc).__name__}")
        else:
            direct_accepts.append(token)
    end_to_end_passes = []
    for token in tokens:
        with tempfile.TemporaryDirectory(
                prefix="b3v4-numeric-domain-") as tmp:
            root = pathlib.Path(tmp) / "campaign"
            build_campaign(root)
            _, bundle = first_bundle(root)
            process_path = bundle / "artifacts" / "process-started.json"
            raw = process_path.read_bytes()
            replaced = raw.replace(
                b'"process_creation_time":1.0',
                f'"process_creation_time":{token}'.encode(), 1)
            assert replaced != raw, token
            process_path.write_bytes(replaced)
            rebind_bundle_and_official(root, bundle, capture=True)
            try:
                result = module.rederive_campaign(
                    root / "campaign-freeze.json", root)
            except module.EvidenceInvalid:
                continue
            except Exception as exc:
                raw_exceptions.append(f"e2e-{token}:{type(exc).__name__}")
                continue
            if (result.get("luna_stage_status") == "PASS" or
                    result.get("luna_stage_accepted") is True):
                end_to_end_passes.append(token)
    assert not raw_exceptions, (
        "numeric-domain retained evidence leaked raw exceptions: " +
        ", ".join(raw_exceptions))
    assert not direct_accepts and not end_to_end_passes, (
        "numeric-domain acceptance: direct=" + ", ".join(direct_accepts) +
        "; Luna-PASS=" + ", ".join(end_to_end_passes))


def assert_trusted_spawn_guard_receipt_closed(module):
    cases = (
        ("omitted", lambda value:
         value.pop("trusted_spawn_guard"), "process started identity"),
        ("stale-freeze", lambda value:
         value["trusted_spawn_guard"].update(
             {"freeze_sha256": "0" * 64}), "spawn guard"),
        ("root-identity-mismatch", lambda value:
         value["trusted_spawn_guard"]["campaign_root_identity"].update(
             {"inode":
              value["trusted_spawn_guard"]["campaign_root_identity"][
                  "inode"] + 1}), "spawn guard"),
        ("duplicate-ordinal", lambda value:
         value["trusted_spawn_guard"].update(
             {"guard_ordinal": 2}), "spawn guard"),
    )
    for label, mutate, expected_reason in cases:
        with tempfile.TemporaryDirectory(
                prefix=f"b3v4-spawn-guard-{label}-") as tmp:
            root = pathlib.Path(tmp) / "campaign"
            build_campaign(root)
            _, bundle = first_bundle(root)
            process_path = bundle / "artifacts" / "process-started.json"
            process = json.loads(process_path.read_text(encoding="utf-8"))
            mutate(process)
            write(process_path, process)
            rebind_bundle_and_official(root, bundle, capture=True)
            result = module.rederive_campaign(
                root / "campaign-freeze.json", root)
            assert result["luna_stage_status"] == "INVALID", (label, result)
            assert expected_reason in result["missions"][0]["reason"], (
                label, result["missions"][0])

    with tempfile.TemporaryDirectory(
            prefix="b3v4-spawn-guard-duplicate-key-") as tmp:
        root = pathlib.Path(tmp) / "campaign"
        build_campaign(root)
        _, bundle = first_bundle(root)
        process_path = bundle / "artifacts" / "process-started.json"
        process = json.loads(process_path.read_text(encoding="utf-8"))
        receipt = process.pop("trusted_spawn_guard")
        base = json.dumps(
            process, sort_keys=True, separators=(",", ":")).encode()
        receipt_raw = json.dumps(
            receipt, sort_keys=True, separators=(",", ":")).encode()
        process_path.write_bytes(
            base[:-1] + b',"trusted_spawn_guard":' + receipt_raw +
            b',"trusted_spawn_guard":' + receipt_raw + b"}\n")
        rebind_bundle_and_official(root, bundle, capture=True)
        result = module.rederive_campaign(
            root / "campaign-freeze.json", root)
        assert result["luna_stage_status"] == "INVALID", result
        assert "duplicate key 'trusted_spawn_guard'" in \
            result["missions"][0]["reason"], result["missions"][0]


def assert_complete_pass_row_schema(module):
    expected_fields = {
        "index", "config", "arm", "rep", "product_status", "host_status",
        "overall_status", "properties", "reason",
        "bundle_manifest_sha256", "raw_stdout_sha256",
        "native_session_sha256", "official_overall_status",
        "independent_overall_status", "model_resolved",
        "official_verdict_sha256",
    }
    with tempfile.TemporaryDirectory(prefix="b3v4-complete-row-") as tmp:
        root = pathlib.Path(tmp) / "campaign"
        build_campaign(root)
        result = module.rederive_campaign(
            root / "campaign-freeze.json", root)
        assert result["luna_stage_status"] == "PASS"
        assert len(result["missions"]) == 6
        for index, row in enumerate(result["missions"]):
            assert set(row) == expected_fields
            assert row["index"] == index
            assert row["product_status"] == "PASS"
            assert row["host_status"] == "PASS"
            assert row["overall_status"] == "PASS"
            assert all(set(value) == {"state", "pass"}
                       for value in row["properties"].values())


def assert_host_root_junction_rejected(module):
    if os.name != "nt":
        print("REDERIVER_HOST_ROOT_JUNCTION=SKIP:not-windows")
        return
    with tempfile.TemporaryDirectory(prefix="b3v4-rederive-junction-") as tmp:
        root = pathlib.Path(tmp) / "campaign"
        build_campaign(root)
        first = root / "attempt-000-L-candidate-r1"
        host_root = first / "host-custody" / first.name
        outside = pathlib.Path(tmp) / "outside-host-root"
        shutil.move(str(host_root), outside)
        made = subprocess.run(
            ["cmd", "/c", "mklink", "/J", str(host_root), str(outside)],
            capture_output=True, text=True)
        if made.returncode:
            shutil.move(str(outside), host_root)
            print("REDERIVER_HOST_ROOT_JUNCTION=SKIP:mklink")
            return
        try:
            result = module.rederive_campaign(root / "campaign-freeze.json", root)
            assert result["accepted"] is False, result
            assert result["luna_stage_status"] == "INVALID", result
        finally:
            os.rmdir(host_root)
            shutil.move(str(outside), host_root)
        print("REDERIVER_HOST_ROOT_JUNCTION=PASS")


def assert_profile_policy_pipeline(module):
    with tempfile.TemporaryDirectory(
            prefix="b3v4-profile-policy-pipeline-") as tmp:
        baseline = pathlib.Path(tmp) / "baseline"
        build_campaign(baseline)
        for label in ("missing-bool", "integer-bool", "duplicate-bool"):
            root = pathlib.Path(tmp) / label
            shutil.copytree(baseline, root)
            rebase_campaign_paths(root)
            first = root / "attempt-000-L-candidate-r1"
            bundle = first / "host-custody" / first.name / "bundle"
            profile_path = bundle / "artifacts" / "host-read-profile.json"
            profile = json.loads(profile_path.read_text(encoding="utf-8"))
            if label == "missing-bool":
                profile["repo"].pop("case_sensitive")
                write(profile_path, profile)
            elif label == "integer-bool":
                profile["repo"]["case_sensitive"] = 1
                write(profile_path, profile)
            else:
                raw = profile_path.read_bytes()
                needle = b'"case_sensitive":true'
                assert raw.count(needle) == 1
                profile_path.write_bytes(raw.replace(
                    needle,
                    b'"case_sensitive":false,"case_sensitive":true'))
            pre_spawn_path = (
                bundle / "artifacts" / "host-read-pre-spawn.json")
            pre_spawn = json.loads(pre_spawn_path.read_text(encoding="utf-8"))
            pre_spawn["profile_sha256"] = sha(profile_path.read_bytes())
            write(pre_spawn_path, pre_spawn)
            process_path = bundle / "artifacts" / "process-started.json"
            process = json.loads(process_path.read_text(encoding="utf-8"))
            process["host_read_pre_spawn_sha256"] = sha(
                pre_spawn_path.read_bytes())
            write(process_path, process)
            rebind_capture(bundle)
            rebind_attempt_seal(first)
            result = module.rederive_campaign(
                root / "campaign-freeze.json", root)
            assert result["luna_stage_status"] == "INVALID", (label, result)


def main():
    assert_independent_import_boundary()
    module = load_module()
    assert_profile_policy_pipeline(module)
    assert_codex_current_lifecycle_parity(module)
    assert_trusted_spawn_guard_receipt_closed(module)
    assert_inherited_campaign_handle_contract(module)
    with tempfile.TemporaryDirectory(
            prefix="b3v4-rederive-campaign-root-rebound-") as tmp:
        root = pathlib.Path(tmp) / "campaign"
        build_campaign(root)
        original = root.with_name("campaign-original")
        os.rename(root, original)
        shutil.copytree(original, root)
        try:
            module.rederive_campaign(root / "campaign-freeze.json", root)
        except module.EvidenceInvalid as exc:
            assert "campaign root physical identity" in str(exc), str(exc)
        else:
            raise AssertionError(
                "rederiver accepted copied campaign root identity")

    for label, mutate in (
            ("missing", lambda value:
             value["campaign_root_identity"].pop("inode")),
            ("extra", lambda value:
             value["campaign_root_identity"].update({"generation": 1})),
            ("bool", lambda value:
             value["campaign_root_identity"].update({"device": True})),
            ("string", lambda value:
             value["campaign_root_identity"].update({"inode": "2"})),
            ("drift", lambda value:
             value["campaign_root_identity"].update({
                 "inode": value["campaign_root_identity"]["inode"] + 1}))):
        with tempfile.TemporaryDirectory(
                prefix=f"b3v4-rederive-root-identity-{label}-") as tmp:
            root = pathlib.Path(tmp) / "campaign"
            build_campaign(root)
            manifest_path = root / "campaign-manifest.json"
            manifest = json.loads(
                manifest_path.read_text(encoding="utf-8"))
            mutate(manifest)
            write(manifest_path, manifest)
            try:
                module.rederive_campaign(
                    root / "campaign-freeze.json", root)
            except module.EvidenceInvalid:
                pass
            else:
                raise AssertionError(
                    f"rederiver accepted {label} campaign root identity")

    # Governing RED R5: syntax-valid rebound surface identities must be checked
    # against retained bytes by the independent implementation.
    with tempfile.TemporaryDirectory(prefix="b3v4-surface-custody-red-") as tmp:
        surface_root = pathlib.Path(tmp).resolve()
        packet = valid_packet()
        manifest = copy.deepcopy(packet["evaluated_surfaces"])
        for index, row in enumerate(manifest["entries"]):
            if row["role"] in module.EVALUATED_SURFACE_VIRTUAL_ROLES:
                continue
            path = surface_root / row["path"]
            payload = f"surface-{index}\n".encode()
            write(path, payload)
            row["byte_length"] = len(payload)
            row["sha256"] = sha(payload)
        module._validate_evaluated_surfaces(manifest, surface_root)
        shadow = surface_root / "evaluated-surface-projections"
        shadow.mkdir()
        try:
            try:
                module._validate_evaluated_surfaces(manifest, surface_root)
            except module.EvidenceInvalid as exc:
                assert "shadow or residue" in str(exc), str(exc)
            else:
                raise AssertionError(
                    "independent B3 accepted a physical virtual shadow")
        finally:
            shadow.rmdir()
        drifted = copy.deepcopy(manifest)
        next(row for row in drifted["entries"]
             if row["role"] not in
             module.EVALUATED_SURFACE_VIRTUAL_ROLES)["sha256"] = "0" * 64
        try:
            module._validate_evaluated_surfaces(drifted, surface_root)
        except (TypeError, module.EvidenceInvalid) as exc:
            assert "drift" in str(exc) or "hash" in str(exc), str(exc)
        else:
            raise AssertionError(
                "independent B3 surface hash drift was accepted")
        external = copy.deepcopy(manifest)
        internal = next(
            row for row in external["entries"]
            if row["role"] == "acceptance-rules")
        internal["path"] = str(
            surface_root / manifest["entries"][0]["path"]).replace("\\", "/")
        try:
            module._validate_evaluated_surfaces(external, surface_root)
        except module.EvidenceInvalid as exc:
            assert "external" in str(exc), str(exc)
        else:
            raise AssertionError(
                "independent B3 internal role accepted an external path")

    surface_packet = valid_packet()
    surface_packet["independent_rederiver"]["implementation_identity"][
        "sha256"] = hashlib.sha256(REDERIVER.read_bytes()).hexdigest()
    next(row for row in surface_packet["evaluated_surfaces"]["entries"]
         if row["role"] == "independent-rederiver")["sha256"] = \
        surface_packet["independent_rederiver"]["implementation_identity"][
            "sha256"]
    module._validate_freeze_contract(surface_packet)
    for mutation in ("missing", "duplicate"):
        changed = copy.deepcopy(surface_packet)
        if mutation == "missing":
            changed["evaluated_surfaces"]["entries"].pop()
        else:
            changed["evaluated_surfaces"]["entries"][-1]["role"] = \
                changed["evaluated_surfaces"]["entries"][0]["role"]
        try:
            module._validate_freeze_contract(changed)
        except module.EvidenceInvalid:
            pass
        else:
            raise AssertionError(
                f"independent rederiver accepted {mutation} surface role")
    owner_mutations = []
    changed = copy.deepcopy(surface_packet)
    changed["evaluated_surface_owners"]["roles"].pop("scorer")
    owner_mutations.append(changed)
    changed = copy.deepcopy(surface_packet)
    changed["evaluated_surface_owners"]["roles"]["extra"] = {
        "kind": "frozen-extra", "sha256": "a" * 64}
    owner_mutations.append(changed)
    changed = copy.deepcopy(surface_packet)
    changed["evaluated_surface_owners"]["roles"]["scorer"]["kind"] = \
        "packet-artifact-evaluator"
    owner_mutations.append(changed)
    changed = copy.deepcopy(surface_packet)
    roles = changed["evaluated_surface_owners"]["roles"]
    roles["scorer"], roles["evaluator"] = roles["evaluator"], roles["scorer"]
    owner_mutations.append(changed)
    changed = copy.deepcopy(surface_packet)
    owner = changed["evaluated_surface_owners"]["roles"]["prompt-template"]
    owner.update({"path": "surface/arbitrary.bin", "sha256": "d" * 64})
    row = next(row for row in changed["evaluated_surfaces"]["entries"]
               if row["role"] == "prompt-template")
    row.update({"path": owner["path"], "sha256": owner["sha256"]})
    owner_mutations.append(changed)
    for changed in owner_mutations:
        try:
            module._validate_freeze_contract(changed)
        except module.EvidenceInvalid:
            pass
        else:
            raise AssertionError(
                "independent B3 rederiver accepted semantic owner drift")
    assert_host_root_junction_rejected(module)
    assert_independent_output_custody(module)
    assert_deep_cli_failure_normalized(module)
    assert_exact_depth_parity(module)
    assert_post_decode_model_traversal(module)
    assert_retained_depth_boundary(module)
    assert_lossless_numeric_domain_rejected(module)
    assert_complete_pass_row_schema(module)

    # One campaign proves the universal retained-file check at every reader
    # family.  The outside hardlink remains byte-identical and all hashes stay
    # valid, so rejection can only come from custody identity enforcement.
    with tempfile.TemporaryDirectory(prefix="b3v4-rederive-hardlinks-") as tmp:
        root = pathlib.Path(tmp) / "campaign"
        build_campaign(root)
        first = root / "attempt-000-L-candidate-r1"
        bundle = first / "host-custody" / first.name / "bundle"
        hardlink_cases = {
            "campaign-freeze": root / "campaign-freeze.json",
            "campaign-manifest": root / "campaign-manifest.json",
            "attempt-status": first / "attempt-status.json",
            "attempt-terminal": first / "attempt-terminal.json",
            "host-attestation": first / "host-attestation.json",
            "official-verdict": first / "official-verdict.json",
            "host-terminal": first / "host-custody" / first.name / "terminal.json",
            "bundle-manifest": bundle / "manifest.json",
            "bundle-jsonl": bundle / "events.jsonl",
            "bundle-bytes": bundle / "prompt.txt",
            "bundle-snapshot-json": bundle / "repo-before.json",
            "artifact-json": bundle / "artifacts" / "host-read-profile.json",
            "artifact-bytes": bundle / "artifacts" / "host-session.raw",
        }
        accepted_aliases = []
        for label, target in hardlink_cases.items():
            alias = pathlib.Path(tmp) / f"{label}.outside-alias"
            os.link(target, alias)
            try:
                try:
                    if label == "campaign-manifest":
                        result = module.rederive_campaign(
                            root / "campaign-freeze.json", root)
                        if result.get("luna_stage_accepted") is True:
                            accepted_aliases.append(label)
                    else:
                        module._read_bytes(target)
                except module.EvidenceInvalid:
                    pass
                else:
                    if label != "campaign-manifest":
                        accepted_aliases.append(label)
            finally:
                alias.unlink()
        assert not accepted_aliases, (
            "rederiver accepted retained hardlink aliases: " +
            ", ".join(accepted_aliases))
    assert_retained_schema_matrix(module)
    assert_host_attestation_custody_matrix(module)
    assert_attempt_status_numeric_aliases_rejected(module)
    assert_remaining_exact_scalar_aliases_rejected(module)
    with tempfile.TemporaryDirectory(prefix="b3v4-rederive-freeze-") as tmp:
        root = pathlib.Path(tmp) / "campaign"
        packet = build_campaign(root)
        reviewer_counterexample = copy.deepcopy(packet)
        reviewer_counterexample["evidence_profiles"]["formal_host_read"] = \
            "optional"
        reviewer_counterexample["acceptance_rule"] = \
            "one official PASS is enough"
        expect_freeze_invalid(module, root, reviewer_counterexample,
                              "formal_host_read")
        mutations = [
            (("evidence_profiles", "formal_host_read"), "optional",
             "formal_host_read"),
            (("acceptance_rule",), "one official PASS is enough",
             "acceptance_rule"),
            (("schema",), "weakened-schema", "schema"),
            (("campaign",), "b3v4-substitute", "campaign"),
            (("state",), "RUNNING", "state"),
            (("foundation", "commit"), "short", "foundation.commit"),
            (("fixture", "id"), "B3-weakened", "fixture.id"),
            (("artifacts", "scorer", "sha256"), "short",
             "artifacts.scorer.sha256"),
            (("candidate", "payload_sha256"), "short",
             "candidate.payload_sha256"),
            (("control", "tree"), "short", "control.tree"),
            (("configurations", "L", "host"), "substitute",
             "configuration L"),
            (("configurations",), {"L": packet["configurations"]["L"],
                                    "O": {}}, "configuration"),
            (("authorization", "metered_api_spend"), "allowed",
             "metered_api_spend"),
            (("seed",), 0, "seed"),
            (("repetitions_per_arm",), 1,
             "repetition"),
            (("result_composition", "overall_states"), ["PASS"],
             "overall state"),
            (("attempt_policy", "silent_retry"), "allowed",
             "silent_retry"),
            (("attempt_policy", "preserve_every_attempt"), False,
             "preserve every attempt"),
            (("invalid_error_rule",), "continue", "invalid_error_rule"),
            (("stop_conditions",), ["continue"] * 5, "stop_conditions"),
            (("independent_rederiver", "contract_id"), "copy-results-v1",
             "contract_id"),
            (("independent_rederiver", "implementation_identity", "path"),
             "eval/copy_results.py", "implementation_identity.path"),
            (("independent_rederiver", "must_not_import"), [],
             "must_not_import"),
            (("independent_rederiver", "input"), "official result",
             "independent_rederiver.input"),
            (("independent_rederiver", "output"), "official result",
             "independent_rederiver.output"),
        ]
        for path, value, fragment in mutations:
            changed = copy.deepcopy(packet)
            owner = changed
            for key in path[:-1]:
                owner = owner[key]
            owner[path[-1]] = value
            expect_freeze_invalid(module, root, changed, fragment)

        accepted_numeric_aliases = []
        exact_integer_mutations = [
            ("seed-float", "seed", 20260718.0),
            ("seed-bool", "seed", True),
            ("seed-string", "seed", "20260718"),
            ("seed-null", "seed", None),
            ("repetitions-float", "repetitions_per_arm",
             3.0),
            ("repetitions-bool", "repetitions_per_arm",
             True),
            ("repetitions-string", "repetitions_per_arm",
             "3"),
            ("repetitions-null", "repetitions_per_arm",
             None),
        ]
        for label, key, value in exact_integer_mutations:
            changed = copy.deepcopy(packet)
            changed[key] = value
            rebind_freeze(root, changed)
            try:
                module.rederive_campaign(root / "campaign-freeze.json", root)
            except module.EvidenceInvalid:
                pass
            else:
                accepted_numeric_aliases.append(label)
        assert not accepted_numeric_aliases, (
            "rederiver accepted non-int frozen numeric fields: " +
            ", ".join(accepted_numeric_aliases))

        accepted_identity_substitutions = []
        for label, digest in (
                ("zero-digest", "0" * 64),
                ("other-bytes-digest", sha(b"not the executing rederiver"))):
            changed = copy.deepcopy(packet)
            changed["independent_rederiver"]["implementation_identity"][
                "sha256"] = digest
            rebind_freeze(root, changed)
            try:
                module.rederive_campaign(root / "campaign-freeze.json", root)
            except module.EvidenceInvalid:
                pass
            else:
                accepted_identity_substitutions.append(label)

        rebind_freeze(root, packet)
        with tempfile.NamedTemporaryFile(
                prefix=".b3v4-rederive-alias-", suffix=".py", dir=HERE,
                delete=False) as stream:
            stream.write(REDERIVER.read_bytes())
            alias_path = pathlib.Path(stream.name)
        try:
            alias_module = load_module(
                alias_path, "b3v4rederive_loaded_from_alias")
            try:
                alias_module.rederive_campaign(
                    root / "campaign-freeze.json", root)
            except alias_module.EvidenceInvalid:
                pass
            else:
                accepted_identity_substitutions.append(
                    "loaded-module-path-alias")
        finally:
            alias_path.unlink()

        assert not accepted_identity_substitutions, (
            "rederiver accepted frozen implementation identity substitutions: " +
            ", ".join(accepted_identity_substitutions))

    with tempfile.TemporaryDirectory(prefix="b3v4-rederive-prefix-") as tmp:
        root = pathlib.Path(tmp) / "campaign"
        packet = build_campaign(root)
        for mission in packet["missions"][2:]:
            name = (f"attempt-{mission['index']:03d}-{mission['config']}-"
                    f"{mission['arm']}-r{mission['rep']}")
            shutil.rmtree(root / name)
        prefix = module.rederive_campaign(root / "campaign-freeze.json", root)
        assert prefix["luna_stage_status"] == "INCOMPLETE", prefix
        assert prefix["accepted"] is False and prefix["mission_count"] == 2
        (root / "unexpected-summary.json").write_text("{}", encoding="utf-8")
        try:
            module.rederive_campaign(root / "campaign-freeze.json", root)
        except module.EvidenceInvalid as exc:
            assert "unexpected custody" in str(exc), str(exc)
        else:
            raise AssertionError("unexpected campaign artifact was accepted")

    for stopped_status in ("INVALID", "ERROR"):
        with tempfile.TemporaryDirectory(
                prefix="b3v4-rederive-stopped-prefix-") as tmp:
            root = pathlib.Path(tmp) / "campaign"
            build_campaign(root)
            stop_after_first(root, stopped_status)
            stopped = module.rederive_campaign(
                root / "campaign-freeze.json", root)
            assert stopped["luna_stage_status"] == stopped_status, stopped
            assert stopped["accepted"] is False
            assert stopped["mission_count"] == 1

    with tempfile.TemporaryDirectory(
            prefix="b3v4-rederive-after-stop-") as tmp:
        root = pathlib.Path(tmp) / "campaign"
        build_campaign(root)
        second = sorted(root.glob("attempt-*"))[1]
        held = pathlib.Path(tmp) / second.name
        shutil.move(str(second), held)
        stop_after_first(root, "INVALID")
        shutil.move(str(held), root / held.name)
        after_stop = module.rederive_campaign(
            root / "campaign-freeze.json", root)
        assert after_stop["luna_stage_status"] == "INVALID", after_stop
        assert after_stop["accepted"] is False
        assert "after terminal stop" in after_stop["reason"]

    semantic_mutations = [
        "empty-matrix", "contradictory-matrix", "partial-post-probe",
        "arbitrary-native-session", "trace-raw-disagreement",
        "codex-action-type-contradiction", "repeated-distinct-write",
    ]
    unexpected_passes = []
    for label in semantic_mutations:
        with tempfile.TemporaryDirectory(
                prefix="b3v4-rederive-semantic-red-") as tmp:
            root = pathlib.Path(tmp) / "campaign"
            build_campaign(root)
            semantic_mutation(root, label)
            try:
                result = module.rederive_campaign(
                    root / "campaign-freeze.json", root)
            except module.EvidenceInvalid:
                pass
            else:
                if (result["luna_stage_status"] == "PASS" or
                        result["accepted"] is True):
                    unexpected_passes.append(label)
    for label, mutate in (
            ("official-empty-evidence",
             lambda verdict: verdict["properties"][next(iter(
                 verdict["properties"]))].update(evidence="")),
            ("official-aggregate-contradiction",
             lambda verdict: verdict["adjudication"].update(
                 all_required_properties_true=False))):
        with tempfile.TemporaryDirectory(
                prefix="b3v4-rederive-official-red-") as tmp:
            root = pathlib.Path(tmp) / "campaign"
            build_campaign(root)
            mutate_official(root, mutate)
            try:
                result = module.rederive_campaign(
                    root / "campaign-freeze.json", root)
            except module.EvidenceInvalid:
                pass
            else:
                if (result["luna_stage_status"] == "PASS" or
                        result["accepted"] is True):
                    unexpected_passes.append(label)
    assert not unexpected_passes, (
        "rederiver accepted hash-rebound semantic mutations: " +
        ", ".join(unexpected_passes))

    with tempfile.TemporaryDirectory(prefix="b3v4-rederive-") as tmp:
        root = pathlib.Path(tmp) / "campaign"
        packet = build_campaign(root)
        result = module.rederive_campaign(root / "campaign-freeze.json", root)
        assert result["luna_stage_status"] == "PASS", result
        assert result["disposition"] == "INCOMPLETE_PENDING_OPUS", result
        assert result["luna_stage_accepted"] is True
        assert result["accepted"] is False
        repeated = module.rederive_campaign(root / "campaign-freeze.json", root)
        assert repeated == result
        first_render = json.dumps(result, indent=1, sort_keys=True) + "\n"
        second_render = json.dumps(repeated, indent=1, sort_keys=True) + "\n"
        assert sha(first_render.encode()) == sha(second_render.encode())
        assert set(result) == {
            "schema", "campaign", "freeze_sha256", "contract_sha256",
            "luna_stage_status", "disposition", "luna_stage_accepted",
            "accepted", "mission_count", "missions", "claims"}
        assert result["schema"] == \
            "implementaudit-b3v4-luna-independent-rederivation-v2"
        assert result["claims"] == {
            "final_12_of_12": False, "cross_model_qualified": False,
            "release_authorized": False, "tag_authorized": False,
            "publication_authorized": False}
        assert len(result["missions"]) == 6
        assert all(row["product_status"] == "PASS" for row in result["missions"])
        assert all(len(row["properties"]) == 6 for row in result["missions"])
        assert all(row["official_verdict_sha256"] for row in result["missions"])
        first = root / "attempt-000-L-candidate-r1"
        bundle = first / "host-custody" / first.name / "bundle"
        official_status, official_verdict = official_runner.score_bundle(
            str(bundle), repo_dir=None)
        assert official_status == "INVALID", official_verdict
        assert official_verdict["adjudication"]["property_evidence_complete"] is False
        assert official_verdict["adjudication"]["host_status"] == "INVALID"
        official_bytes = encoded(official_verdict)
        write(first / "official-verdict.json", official_bytes)
        terminal_path = first / "attempt-terminal.json"
        terminal = json.loads(terminal_path.read_text(encoding="utf-8"))
        terminal["official_overall_status"] = official_status
        terminal["official_verdict_sha256"] = sha(official_bytes)
        terminal["overall_status"] = "PASS"
        write(terminal_path, terminal)
        rebind_attempt_seal(first)
        counterexample = module.rederive_campaign(
            root / "campaign-freeze.json", root)
        assert counterexample["luna_stage_status"] == "INVALID", counterexample
        assert counterexample["accepted"] is False

    with tempfile.TemporaryDirectory(prefix="b3v4-rederive-output-") as tmp:
        root = pathlib.Path(tmp) / "campaign"
        build_campaign(root)
        result = module.rederive_campaign(root / "campaign-freeze.json", root)
        output = root / "b3v4-luna-independent-rederivation.json"
        module.write_rederivation(output, result, root=root)
        assert json.loads(output.read_text(encoding="utf-8")) == result
        try:
            module.write_rederivation(output, result, root=root)
        except module.EvidenceInvalid as exc:
            assert "already exists" in str(exc), str(exc)
        else:
            raise AssertionError("independent result overwrite was accepted")

    with tempfile.TemporaryDirectory(prefix="b3v4-rederive-") as tmp:
        root = pathlib.Path(tmp) / "campaign"
        build_campaign(root)
        first = root / "attempt-000-L-candidate-r1"
        verdict_path = first / "official-verdict.json"
        verdict = json.loads(verdict_path.read_text(encoding="utf-8"))
        verdict["properties"]["fabricated_hash_bound_property"] = {
            "state": "PASS", "pass": True,
            "evidence": "fabricated retained evidence",
            "describes": "not present in the frozen fixture",
            "basis": "host-observation",
        }
        write(verdict_path, verdict)
        terminal_path = first / "attempt-terminal.json"
        terminal = json.loads(terminal_path.read_text(encoding="utf-8"))
        terminal["official_verdict_sha256"] = sha(verdict_path.read_bytes())
        write(terminal_path, terminal)
        rebind_attempt_seal(first)
        rebind_attempt_seal(first)
        counterexample = module.rederive_campaign(
            root / "campaign-freeze.json", root)
        assert counterexample["luna_stage_status"] == "INVALID", counterexample
        assert counterexample["accepted"] is False
        assert "official property key set" in counterexample["missions"][0]["reason"]

    with tempfile.TemporaryDirectory(prefix="b3v4-rederive-") as tmp:
        root = pathlib.Path(tmp) / "campaign"
        packet = build_campaign(root)
        result = module.rederive_campaign(root / "campaign-freeze.json", root)
        assert result["luna_stage_status"] == "PASS", result

        first = root / "attempt-000-L-candidate-r1"
        terminal_path = first / "attempt-terminal.json"
        terminal = json.loads(terminal_path.read_text(encoding="utf-8"))
        terminal["overall_status"] = "FAIL"
        terminal["stop_reason"] = "failed-mission-halts-campaign"
        write(terminal_path, terminal)
        rebind_attempt_seal(first)
        disagreement = module.rederive_campaign(root / "campaign-freeze.json", root)
        assert disagreement["luna_stage_status"] == "INVALID", disagreement
        assert disagreement["accepted"] is False
        first_row = disagreement["missions"][0]
        assert first_row["overall_status"] == "INVALID"
        assert "disagree" in first_row["reason"]
        assert "after terminal stop" in disagreement["reason"]
        terminal["overall_status"] = "PASS"
        terminal["stop_reason"] = None
        write(terminal_path, terminal)
        rebind_attempt_seal(first)

        terminal["resolved_model"] = "substituted-model"
        write(terminal_path, terminal)
        rebind_attempt_seal(first)
        invalid = module.rederive_campaign(root / "campaign-freeze.json", root)
        assert invalid["luna_stage_status"] == "INVALID"
        assert invalid["accepted"] is False
        terminal["resolved_model"] = packet["configurations"]["L"]["model_resolved_required"]
        write(terminal_path, terminal)
        rebind_attempt_seal(first)

        raw = (first / "host-custody" / first.name / "bundle" / "artifacts" /
               "host-session.raw")
        raw.write_bytes(b"tampered\n")
        rebind_attempt_seal(first)
        invalid = module.rederive_campaign(root / "campaign-freeze.json", root)
        assert invalid["luna_stage_status"] == "INVALID"
        assert "hash" in invalid["missions"][0]["reason"]

    with tempfile.TemporaryDirectory(prefix="b3v4-rederive-") as tmp:
        root = pathlib.Path(tmp) / "campaign"
        build_campaign(root)
        first = root / "attempt-000-L-candidate-r1"
        bundle = first / "host-custody" / first.name / "bundle"
        profile_path = bundle / "artifacts" / "host-read-profile.json"
        profile_bytes = profile_path.read_bytes()
        authority = b'"authority":"mechanically-minted"'
        duplicate_authority = (
            b'"authority":"untrusted","authority":"mechanically-minted"')
        assert profile_bytes.count(authority) == 1
        profile_path.write_bytes(profile_bytes.replace(
            authority, duplicate_authority))
        pre_spawn_path = bundle / "artifacts" / "host-read-pre-spawn.json"
        pre_spawn = json.loads(pre_spawn_path.read_text(encoding="utf-8"))
        pre_spawn["profile_sha256"] = sha(profile_path.read_bytes())
        write(pre_spawn_path, pre_spawn)
        process_path = bundle / "artifacts" / "process-started.json"
        process = json.loads(process_path.read_text(encoding="utf-8"))
        process["host_read_pre_spawn_sha256"] = sha(pre_spawn_path.read_bytes())
        write(process_path, process)
        rebind_capture(bundle)
        rebind_attempt_seal(first)
        ambiguous = module.rederive_campaign(
            root / "campaign-freeze.json", root)
        assert ambiguous["luna_stage_status"] == "INVALID", ambiguous["missions"][0]
        assert ambiguous["accepted"] is False
        assert "duplicate key 'authority'" in ambiguous["missions"][0]["reason"]

    with tempfile.TemporaryDirectory(prefix="b3v4-rederive-extra-") as tmp:
        root = pathlib.Path(tmp) / "campaign"
        build_campaign(root)
        first = root / "attempt-000-L-candidate-r1"
        bundle = first / "host-custody" / first.name / "bundle"
        extra = bundle / "artifacts" / "unexpected-summary.json"
        write(extra, {"status": "PASS"})
        artifact_manifest_path = bundle / "artifact-manifest.json"
        artifact_manifest = json.loads(
            artifact_manifest_path.read_text(encoding="utf-8"))
        artifact_manifest["files"]["unexpected-summary.json"] = sha(
            extra.read_bytes())
        write(artifact_manifest_path, artifact_manifest)
        manifest_path = bundle / "manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["artifact_manifest_sha256"] = sha(
            artifact_manifest_path.read_bytes())
        write(manifest_path, manifest)
        rebind_attempt_seal(first)
        rebound = module.rederive_campaign(root / "campaign-freeze.json", root)
        assert rebound["luna_stage_status"] == "INVALID", rebound
        assert "artifact set" in rebound["missions"][0]["reason"]

    with tempfile.TemporaryDirectory(prefix="b3v4-rederive-") as tmp:
        root = pathlib.Path(tmp) / "campaign"
        build_campaign(root)
        first = root / "attempt-000-L-candidate-r1"
        bundle = first / "host-custody" / first.name / "bundle"
        raw = bundle / "artifacts" / "host-stdout.raw"
        events = [json.loads(line) for line in raw.read_text(encoding="utf-8").splitlines()]
        command_events = [event for event in events
                          if (event.get("item") or {}).get("type") ==
                          "command_execution"]
        command_events[0]["item"]["command"] = "printf 'STATE\\n'"
        command_events[1]["item"]["command"] = "printf 'STATE\\n'"
        raw.write_bytes(b"".join(encoded(event) for event in events))
        artifacts = bundle / "artifacts"
        trace_path = artifacts / "host-tool-trace.json"
        trace = json.loads(trace_path.read_text(encoding="utf-8"))
        trace["actions"][0]["command"] = "printf 'STATE\\n'"
        write(trace_path, trace)
        fixture = make_fixture()
        state_path = fixture["host_checks"]["specs"][1]["reads"][0]
        matrix_path = artifacts / "host-read-matrix.json"
        matrix = json.loads(matrix_path.read_text(encoding="utf-8"))
        matrix_row = matrix["specs"]["live_state_read_before_capsule_write"]
        matrix_row["property_status"] = "INCOMPLETE"
        matrix_row["overall_status"] = "INCOMPLETE"
        matrix_row["ordered"] = False
        matrix_row["reads"][state_path] = {
            "classification": "fail-closed", "completion_ordinal": None}
        write(matrix_path, matrix)
        checks_path = artifacts / "host-checks.json"
        checks = json.loads(checks_path.read_text(encoding="utf-8"))
        checks["live_state_read_before_capsule_write"] = False
        write(checks_path, checks)
        rebind_capture(bundle)
        verdict_path = first / "official-verdict.json"
        verdict = json.loads(verdict_path.read_text(encoding="utf-8"))
        verdict["bundle_sha256"] = bundle_hash(bundle)
        write(verdict_path, verdict)
        terminal_path = first / "attempt-terminal.json"
        terminal = json.loads(terminal_path.read_text(encoding="utf-8"))
        terminal["official_verdict_sha256"] = sha(verdict_path.read_bytes())
        write(terminal_path, terminal)
        rebind_attempt_seal(first)
        falsified = module.rederive_campaign(root / "campaign-freeze.json", root)
        assert falsified["luna_stage_status"] == "INVALID", falsified["missions"][0]
        first_row = falsified["missions"][0]
        assert first_row["official_overall_status"] == "PASS"
        assert first_row["independent_overall_status"] == "FAIL"
        assert first_row["overall_status"] == "INVALID"
        assert "disagree" in first_row["reason"]
        assert first_row["properties"][
            "live_state_read_before_mutation"]["state"] == "FAIL"

    print("test_b3v4_rederive: ok")


if __name__ == "__main__":
    main()
