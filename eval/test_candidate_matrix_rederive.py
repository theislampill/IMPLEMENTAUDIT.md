#!/usr/bin/env python3
"""Deterministic tests for the independent Luna matrix rederiver."""
from __future__ import annotations

import ast
import base64
import copy
import hashlib
import importlib.util
import json
import os
import pathlib
import shutil
import tempfile

from test_candidate_matrix_freeze import valid_packet
import evaluated_surfaces as surfaces
from test_campaign_freeze_preflight import (
    write_retained_production_readiness_fixture,
    write_test_live_ready,
)


HERE = pathlib.Path(__file__).resolve().parent
MODULE = HERE / "candidate_matrix_rederive.py"
FORBIDDEN = {
    "candidate_matrix_campaign", "campaign_lifecycle", "b3v4_campaign",
    "b3v4_rederive", "b3v4_contract", "hosts", "runner", "adapters",
    "lib.scoring", "eval.lib.scoring",
    "evaluated_surfaces", "eval.evaluated_surfaces",
    "provisional_integration", "eval.provisional_integration",
    "candidate_matrix_acceptance", "candidate_matrix_fixture_setup",
    "candidate_matrix_host",
}
LUNA_MODEL = "gpt-5.6-luna"
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
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) +
            "\n").encode()


def write(path, data):
    path = pathlib.Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data if isinstance(data, bytes) else encoded(data))


def snapshot(files):
    value = {
        "schema": "implementaudit-repo-snapshot-v2",
        "head_commit": "d" * 40, "head_tree": "e" * 40,
        "index_tree": "e" * 40, "staged": [], "unstaged": [],
        "renames": {}, "untracked": copy.deepcopy(files),
        "worktree_files": copy.deepcopy(files),
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


def bundle_hash(bundle):
    digest = hashlib.sha256()
    for name in ("manifest.json", "fixture.json", "prompt.txt",
                 "events.jsonl", "repo-before.json", "repo-after.json",
                 "repo-comparison.json", "artifact-manifest.json"):
        path = pathlib.Path(bundle) / name
        if path.is_file():
            digest.update(name.encode())
            digest.update(path.read_bytes())
    return digest.hexdigest()


def synthetic_official_pass(fixture, model, manifest, bundle_sha256):
    properties = {
        prop["name"]: {
            "state": (
                "FAIL" if fixture["id"] == "B0" and
                prop["required"] is False else "PASS"),
            "pass": not (
                fixture["id"] == "B0" and
                prop["required"] is False),
            "evidence": "synthetic production-shaped retained evidence",
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
                "artifact hashes via artifact-manifest",
            ],
            "adapter_attested_only": [
                "product_tag/commit/tree", "installed_payload_sha256",
                "adapter_name/version/sha256", "host",
                "harness_commit (cross-checked when the scoring checkout is available)",
            ],
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
            "product_failed_invariant": None,
            "host_failed_invariant": None, "host_failed_status": None,
            "failed_domain": None, "failed_invariant": None,
        },
        "failed_domain": None, "failed_invariant": None,
        "evidence": ["synthetic production-shaped retained evidence"],
        "reason": None,
    }


def _changed_files(fixture_id):
    if fixture_id == "B0":
        return sorted([
            ".IMPLEMENTAUDIT/runs/fix-typo-a1b2c3/STATE.md",
            ".IMPLEMENTAUDIT/runs/fix-typo-a1b2c3/ROADMAP.md",
            "task.txt",
        ])
    return []


def _changed_file_bytes(path):
    if path == "task.txt":
        return b"receive\n"
    return ("retained " + path + "\n").encode()


def _trace_action(action_id, ordinal, command, output):
    return {
        "id": action_id, "state": "COMPLETED", "effect": "command",
        "action_type": "command_execution", "classification": None,
        "invocation_invented": False,
        "payload": ["command", command], "command": command,
        "wrapper_layers": 1, "protocol_wrapper_valid": True,
        "exit_code": 0, "output": output,
        "invocation_ordinal": ordinal, "completion_ordinal": ordinal + 1,
    }


def build_campaign(root, *, execution_mode="production", surface_root=None,
                   external_surface_paths=None, foundation=None,
                   transcript_overrides=None, event_overrides=None):
    root = pathlib.Path(root)
    surface_root = root if surface_root is None else pathlib.Path(surface_root)
    packet = valid_packet()
    if foundation is not None:
        packet["foundation"] = copy.deepcopy(foundation)
    packet["independent_rederiver"]["implementation_identity"]["sha256"] = \
        sha(MODULE.read_bytes())
    external_surface_paths = external_surface_paths or {}
    owners = packet["evaluated_surface_owners"]["roles"]
    for role, path in external_surface_paths.items():
        owners[role]["path"] = pathlib.Path(path).resolve().as_posix()
    fixture_values = {}
    fixture_bytes = {}
    for row in packet["fixtures"]:
        raw = (HERE.parent / row["path"]).read_bytes()
        row["sha256"] = sha(raw)
        if surface_root != root:
            write(surface_root / row["path"], raw)
        fixture_bytes[row["id"]] = raw
        fixture_values[row["id"]] = json.loads(raw)
    attestation_bytes = encoded({
        "id": "matrix-L-host", "shell_dialect": "posix",
        "executables": {"cat": "posix:cat"},
    })
    for index, role in enumerate(surfaces.required_roles(
            surfaces.MATRIX_CAMPAIGN)):
        if role in surfaces.INLINE_ROLES:
            continue
        if role == "artifact-contract":
            payload = (HERE / "candidate_matrix_contract.json").read_bytes()
        elif role.startswith("fixture-"):
            payload = fixture_bytes[role[len("fixture-"):]]
        elif role == "independent-rederiver":
            payload = MODULE.read_bytes()
        elif role == "host-attestation":
            payload = attestation_bytes
            packet["configuration"]["host_attestation"]["sha256"] = sha(payload)
        else:
            payload = f"{packet['campaign']}:{role}:{index}\n".encode()
        if role in ("scorer", "evaluator", "host-runner"):
            artifact = {"host-runner": "runner"}.get(role, role)
            packet["artifacts"][artifact]["sha256"] = sha(payload)
        elif role == "native-executable":
            packet["configuration"]["executable"]["path"] = \
                "surface/native-executable.bin"
            packet["configuration"]["executable"]["sha256"] = sha(payload)
        elif role == "product-candidate":
            packet["candidate"]["payload_sha256"] = sha(payload)
        elif owners[role]["kind"].startswith("frozen-"):
            owners[role]["sha256"] = sha(payload)
        path, _digest, _git, _raw = surfaces._packet_file_identity(
            packet, surfaces.MATRIX_CAMPAIGN, role, owners[role])
        write(pathlib.Path(path) if pathlib.Path(path).is_absolute()
              else surface_root / path, payload)
    packet["evaluated_surfaces"] = surfaces.build_manifest_from_packet(
        packet, surfaces.MATRIX_CAMPAIGN, root=surface_root)
    packet_bytes = json.dumps(packet, sort_keys=True).encode()
    freeze_sha = sha(packet_bytes)
    write(root / "campaign-freeze.json", packet_bytes)
    write(root / "campaign-manifest.json", {
        "schema":
            "implementaudit-candidate-matrix-luna-campaign-custody-v1",
        "campaign": packet["campaign"], "freeze_sha256": freeze_sha,
        "contract_sha256": packet["artifact_contract"]["sha256"],
        "created_at": "2030-01-01T00:00:00Z",
        "execution_stage": "LUNA",
    })
    attestation = {
        "id": "matrix-L-host", "shell_dialect": "posix",
        "executables": {"cat": "posix:cat"},
    }
    attestation_bytes = encoded(attestation)
    readiness_path = (
        write_retained_production_readiness_fixture(
            "candidate-matrix", packet,
            root.parent / (root.name + "-live-ready"))
        if execution_mode == "production"
        else write_test_live_ready(
            "candidate-matrix", packet,
            root.parent / (root.name + "-live-ready")))
    readiness_bytes = readiness_path.read_bytes()
    readiness = json.loads(readiness_bytes)
    model = packet["configuration"]["model_resolved_required"]
    for mission in packet["cells"]:
        name = f"attempt-{mission['index']:03d}-L-{mission['fixture']}"
        fixture_id = mission["fixture"]
        fixture = fixture_values[fixture_id]
        raw_fixture = fixture_bytes[fixture_id]
        attempt = root / name
        host_root = attempt / "host-custody" / name
        bundle = host_root / "bundle"
        write(attempt / "host-attestation.json", attestation_bytes)
        write(attempt / "launch-readiness.json", readiness_bytes)
        status = {
            "schema":
                "implementaudit-candidate-matrix-luna-attempt-status-v1",
            "campaign": packet["campaign"], "freeze_sha256": freeze_sha,
            "contract_sha256": packet["artifact_contract"]["sha256"],
            "mission": mission, "state": "PREPARED_BEFORE_HOST_SPAWN",
            "execution_mode": execution_mode,
            "created_at": "2030-01-01T00:00:00Z",
            "host_attestation_binding": {
                "path": "host-attestation.json",
                "sha256": sha(attestation_bytes),
                "config": "L", "host": packet["configuration"]["host"],
                "model_resolved_required": model,
            },
            "launch_readiness_binding": {
                "path": "launch-readiness.json",
                "sha256": sha(readiness_bytes),
                "schema": readiness["schema"],
                "execution_mode": readiness["execution_mode"],
                "disposition": readiness["disposition"],
            },
        }
        write(attempt / "attempt-status.json", status)
        changed = _changed_files(fixture_id)
        after_files = {
            path: {"type": "file", "sha256": sha(_changed_file_bytes(path))}
            for path in changed
        }
        before = snapshot({})
        after = snapshot(after_files)
        repo_root = "/candidate"
        preimage_content = b"retained candidate preimage\n"
        preimages = {
            "schema": "implementaudit-host-read-preimages-v1",
            "repo": {
                "lexical_root": repo_root, "real_root": repo_root,
                "case_sensitive": True,
            },
            "targets": {
                "README.md": {
                    "canonical_path": repo_root + "/README.md",
                    "relative_path": "README.md",
                    "content_base64":
                        base64.b64encode(preimage_content).decode(),
                    "sha256": sha(preimage_content),
                    "size": len(preimage_content), "mode": 0o100644,
                    "symlink_free": True,
                },
            },
        }
        probe = {
            "environment": {
                "PATH": "/usr/bin", "LANG": "C.UTF-8", "LC_ALL": None,
                "BASH_ENV": None, "ENV": None, "SHELL": "/bin/bash",
            },
            "shell": {
                "logical_path": "/bin/bash", "realpath": "/bin/bash",
                "sha256": "7" * 64,
                "stat": "dev=1;ino=1;mode=100755;size=1",
            },
            "executables": {
                reader: {
                    "kind": "file", "path": "/usr/bin/" + reader,
                    "sha256": "8" * 64,
                    "stat": "dev=1;ino=2;mode=100755;size=1",
                }
                for reader in ("cat", "grep", "head", "rg", "sed", "tail")
            },
        }
        profile = {
            "schema": "implementaudit-host-read-profile-v2",
            "authority": "mechanically-minted", "host": "codex",
            "repo": preimages["repo"], **probe,
            "outer_wrapper": {
                "argv_prefix": ["/bin/bash", "-lc"],
                "max_unwrap_layers": 1,
            },
            "probe_sha256": sha(json.dumps(
                probe, sort_keys=True, separators=(",", ":")).encode()),
        }
        command = "/bin/bash -lc " + json.dumps("cat README.md")
        actions = [_trace_action(
            "read-preimage", 3, command, preimage_content.decode())]
        if changed:
            actions.append({
                "id": "write-changes", "state": "COMPLETED",
                "effect": "write", "action_type": "file_change",
                "classification": None, "invocation_invented": False,
                "paths": changed, "payload": [
                    "changes", [[path, "add"] for path in changed]],
                "invocation_ordinal": 5, "completion_ordinal": 6,
            })
        intent = {
            "schema": "implementaudit-run-intent-v1", "run_id": name,
            "fixture_id": fixture_id,
            "call_ordinal": mission["index"] + 1,
            "fixture_sha256": sha(raw_fixture),
            "product_checkout": "/candidate", "adapter_name": "codex-cli",
            "adapter_sha256": "a" * 64,
            "harness_commit": packet["foundation"]["commit"],
            "model_requested": packet["configuration"]["model_requested"],
            "reasoning_effort_requested":
                packet["configuration"]["reasoning_effort"],
            "policy_requested": {},
            "required_capabilities": fixture.get(
                "required_capabilities") or [],
            "temp_home": "/tmp/matrix-home",
            "started_at": "2030-01-01T00:00:00Z",
        }
        replay = {
            "schema": "implementaudit-host-read-replay-spec-v1",
            "mode": "formal-v2", "host": "codex", "checks": [],
            "requested_tools": [], "fixture_sha256": sha(raw_fixture),
            "run_intent_sha256": sha(encoded(intent)),
            "parser_sha256": "f" * 64,
        }
        raw_events = [
            {"type": "thread.started", "thread_id": name},
            {"type": "turn.started", "thread_id": name,
             "turn_id": "stdout-turn"},
            {"type": "item.started", "item": {
                "id": "read-preimage", "type": "command_execution",
                "status": "in_progress", "command": command,
                "aggregated_output": "", "exit_code": None}},
            {"type": "item.completed", "item": {
                "id": "read-preimage", "type": "command_execution",
                "status": "completed", "command": command,
                "aggregated_output": preimage_content.decode(),
                "exit_code": 0}},
        ]
        if changed:
            changes = [{"path": path, "kind": "add"} for path in changed]
            raw_events.extend([
                {"type": "item.started", "item": {
                    "id": "write-changes", "type": "file_change",
                    "status": "in_progress", "changes": changes}},
                {"type": "item.completed", "item": {
                    "id": "write-changes", "type": "file_change",
                    "status": "completed", "changes": changes}},
            ])
        raw_events.append({
            "type": "turn.completed", "thread_id": name,
            "turn_id": "stdout-turn",
            "usage": {
                "input_tokens": 1, "cached_input_tokens": 0,
                "output_tokens": 1, "reasoning_output_tokens": 0},
        })
        raw_stdout = b"".join(encoded(event) for event in raw_events)
        raw_session = b"".join(encoded(event) for event in [
            {
                "type": "session_meta",
                "timestamp": "2030-01-01T00:00:00Z",
                "payload": {
                    "id": name, "session_id": name, "cwd": repo_root,
                    "timestamp": "2030-01-01T00:00:00Z",
                },
            },
            {
                "type": "turn_context",
                "timestamp": "2030-01-01T00:00:00Z",
                "payload": {"turn_id": "native-turn", "cwd": repo_root,
                            "model": intent["model_requested"]},
            },
            {
                "type": "response_item",
                "timestamp": "2030-01-01T00:00:00Z",
                "payload": {"action_ids": [row["id"] for row in actions]},
            },
        ])
        trace = {
            "schema": "implementaudit-host-tool-trace-v2",
            "actions": actions, "invalid": False, "host_findings": [],
            "ids_reserved": True,
            "action_states": ["COMPLETED"] * len(actions),
            "action_effects": [row["effect"] for row in actions],
            "host_status": "PASS", "requested_tools": [],
            "observed_tools": [],
        }
        matrix = {
            "schema": "implementaudit-host-read-matrix-v1",
            "raw_transforms": {
                "host-stdout.raw": "codex-typed-action-normalizer-v2",
                "host-session.raw": "lineage-corroboration-only",
            },
            "specs": {},
        }
        files = {
            "host-read-profile.json": encoded(profile),
            "host-read-preimages.json": encoded(preimages),
            "host-read-fixture.raw": raw_fixture,
            "host-read-replay-spec.json": encoded(replay),
        }
        pre_spawn = {
            "schema": "implementaudit-host-read-pre-spawn-v1",
            "created_before_spawn": True,
            "profile_sha256": sha(files["host-read-profile.json"]),
            "preimages_sha256": sha(files["host-read-preimages.json"]),
            "fixture_sha256": sha(files["host-read-fixture.raw"]),
            "replay_spec_sha256": sha(files["host-read-replay-spec.json"]),
        }
        files.update({
            "host-read-pre-spawn.json": encoded(pre_spawn),
            "host-stdout.raw": raw_stdout, "host-session.raw": raw_session,
            "host-tool-trace.json": encoded(trace),
            "host-read-matrix.json": encoded(matrix),
            "host-read-post-probe.json": encoded(probe),
        })
        terminal = {
            "schema": "implementaudit-host-read-terminal-v1",
            "hashes": {key: sha(value) for key, value in files.items()},
            "post_probe_sha256": sha(json.dumps(
                probe, sort_keys=True, separators=(",", ":")).encode()),
            "profile_post_status": "PASS",
            "binding": {
                "thread_id": name, "stdout_turn_ordinal": 1,
                "turn_id": "stdout-turn", "native_turn_id": "native-turn",
            },
            "actual_tools": [], "normalized_host_status": "PASS",
            "host_terminal_kind": "ok", "session_bound": True,
            "session_status": "VALID",
        }
        files["host-read-terminal.json"] = encoded(terminal)
        files["host-read-manifest.json"] = encoded({
            "schema": "implementaudit-host-read-manifest-v1",
            "files": {key: sha(files[key]) for key in CAPTURE_FILES},
        })
        files["run-intent.json"] = encoded(intent)
        files["process-started.json"] = encoded({
            "schema": "implementaudit-process-started-v2",
            "run_id": name, "cwd": repo_root,
            "started_at": "2030-01-01T00:00:00Z",
            "argv_sha256": "b" * 64, "requested_model": model,
            "temp_home": "/tmp/matrix-home", "lane_id": "test-lane",
            "host_os": "posix", "host_boot_id": "test-boot", "pid": 1234,
            "process_creation_time": 1.0,
            "host_read_pre_spawn_sha256":
                sha(files["host-read-pre-spawn.json"]),
        })
        if fixture.get("host_checks"):
            checks = {
                spec["key"]: True
                for spec in fixture["host_checks"]["specs"]
            }
            detail = {}
            for spec in fixture["host_checks"]["specs"]:
                if spec["kind"] == "run_root_exists":
                    detail[spec["key"]] = "fix-typo-a1b2c3"
                elif spec["kind"] == "validate_run_root":
                    detail[spec["key"]] = (
                        ".IMPLEMENTAUDIT/runs/fix-typo-a1b2c3: exit 0; ok")
            checks["_detail"] = detail
            files["host-checks.json"] = encoded(checks)
        files["host-stderr.raw"] = b""
        files["raw-host-events.jsonl"] = raw_session
        files["derived-transform.json"] = encoded({
            "schema": "implementaudit-derived-view-v1",
            "transform": "codex-cli-host-event-extraction-v2",
            "source": "codex-session-jsonl",
            "source_raw_sha256": sha(raw_session),
            "rules": "complete retained host extraction",
        })
        if fixture_id == "E5":
            files["result.json"] = encoded({
                "current_verdict": "reject",
                "p1_verdict": "reject",
                "p2_verdict": "accept",
            })
        artifact_manifest = {
            "files": {key: sha(value) for key, value in files.items()}
        }
        transcript = (
            HERE / "fixtures" / fixture_id /
            "transcript_pass.txt").read_text(encoding="utf-8")
        if transcript_overrides and fixture_id in transcript_overrides:
            transcript = transcript_overrides[fixture_id]
        if fixture_id == "B0":
            transcript = "\n".join(
                line for line in transcript.splitlines()
                if not line.startswith("AGENTS_UPDATE_DECISION"))
        event_rows = (
            event_overrides.get(fixture_id)
            if event_overrides and fixture_id in event_overrides else
            [{"role": "assistant",
              "kind": ("marker" if fixture_id in
                       {"B1", "E3", "E7", "E9"} else "message"),
              "content": transcript}])
        retained_event = b"".join(encoded({
            "schema": "implementaudit-eval-event-v1", "run_id": name,
            "fixture_id": fixture_id, "seq": index,
            "role": row["role"], "kind": row.get("kind", "message"),
            "content": row["content"],
            "recorded_at": "2030-01-01T00:00:01Z",
        }) for index, row in enumerate(event_rows, 1))
        prompt = ("MISSION:\n" + fixture["mission"]).encode()
        comparison = {
            "schema": "implementaudit-repo-comparison-v1",
            "changed_files": changed, "committed_change": False,
            "committed_files_known": True, "committed_files": [],
        }
        manifest = {
            "schema": "implementaudit-eval-manifest-v2",
            "run_id": name, "fixture_id": fixture_id,
            "fixture_sha256": sha(raw_fixture), "prompt_sha256": sha(prompt),
            "product_tag": "v0.3.2.0",
            "product_commit": packet["candidate"]["commit"],
            "product_tree": packet["candidate"]["tree"],
            "installed_payload_sha256":
                packet["candidate"]["payload_sha256"],
            "harness_commit": packet["foundation"]["commit"],
            "adapter_name": "codex-cli", "adapter_version": "test",
            "adapter_sha256": "a" * 64,
            "model_requested": packet["configuration"]["model_requested"],
            "model_resolved": model, "host": "codex-cli",
            "started_at": "2030-01-01T00:00:00Z",
            "ended_at": "2030-01-01T00:00:01Z",
            "events_sha256": sha(retained_event),
            "repo_before_sha256": sha(encoded(before)),
            "repo_after_sha256": sha(encoded(after)),
            "artifact_manifest_sha256": sha(encoded(artifact_manifest)),
            "payload_source_sha256": packet["candidate"]["payload_sha256"],
            "repo_comparison_sha256": sha(encoded(comparison)),
            "policy_requested": {
                "sandbox": "workspace-write", "approval": "never",
                "tools": "codex-shell", "network": "restricted",
                "writable_roots": ["<fixture-repo cwd>"],
            },
            "policy_resolved": {
                "class": "host-owned (session turn_context)",
                "sandbox": "workspace-write", "approval": "never",
                "session_id": name, "cli_version": "test",
            },
            "models_observed": [{
                "model": model, "role": "root-agent",
                "source": "host session turn_context", "session_id": name,
            }],
            "reasoning_effort_requested":
                packet["configuration"]["reasoning_effort"],
            "reasoning_effort_resolved":
                packet["configuration"]["reasoning_effort"],
        }
        write(host_root / "terminal.json", {
            "schema": "implementaudit-run-terminal-v1", "run_id": name,
            "spawned": True, "kind": "ok", "detail": str(bundle),
            "resolved_model": model, "reconciled": False,
            "started_at": "2030-01-01T00:00:00Z",
            "ended_at": "2030-01-01T00:00:01Z",
            "policy_resolved": {},
        })
        write(bundle / "manifest.json", manifest)
        write(bundle / "fixture.json", raw_fixture)
        write(bundle / "prompt.txt", prompt)
        write(bundle / "events.jsonl", retained_event)
        write(bundle / "repo-before.json", before)
        write(bundle / "repo-after.json", after)
        write(bundle / "repo-comparison.json", comparison)
        write(bundle / "artifact-manifest.json", artifact_manifest)
        for relative, data in files.items():
            write(bundle / "artifacts" / relative, data)
        verdict = synthetic_official_pass(
            fixture, model, manifest, bundle_hash(bundle))
        verdict_bytes = encoded(verdict)
        write(attempt / "official-verdict.json", verdict_bytes)
        attempt_terminal = {
            "schema":
                "implementaudit-candidate-matrix-luna-attempt-terminal-v1",
            "campaign": packet["campaign"],
            "mission_index": mission["index"],
            "execution_mode": execution_mode, "overall_status": "PASS",
            "resolved_model": model, "host_run_root": str(host_root),
            "official_overall_status": "PASS",
            "official_verdict_sha256": sha(verdict_bytes),
            "stop_reason": None, "error_type": None,
            "completed_at": "2030-01-01T00:00:01Z",
            "completed_attempt_seal": None,
        }
        write(attempt / "attempt-terminal.json", attempt_terminal)
        rebind_attempt_seal(attempt)
    return packet


def rebind_attempt_seal(attempt):
    attempt = pathlib.Path(attempt)
    status_raw = (attempt / "attempt-status.json").read_bytes()
    status = json.loads(status_raw)
    attestation_raw = (attempt / "host-attestation.json").read_bytes()
    readiness_raw = (attempt / "launch-readiness.json").read_bytes()
    terminal_path = attempt / "attempt-terminal.json"
    terminal = json.loads(terminal_path.read_text(encoding="utf-8"))
    terminal["completed_attempt_seal"] = {
        "schema":
            "implementaudit-candidate-matrix-completed-attempt-seal-v1",
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
        "host_custody_manifest_sha256":
            sha(custody_manifest_bytes(attempt / "host-custody")),
    }
    write(terminal_path, terminal)


def rebase_campaign_paths(root):
    root = pathlib.Path(root)
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
        rebind_attempt_seal(attempt)


def rebind_bundle_and_official(bundle):
    bundle = pathlib.Path(bundle)
    artifacts = bundle / "artifacts"
    artifact_manifest_path = bundle / "artifact-manifest.json"
    artifact_manifest = {
        "files": {
            path.relative_to(artifacts).as_posix(): sha(path.read_bytes())
            for path in sorted(artifacts.rglob("*"))
            if path.is_file()
        },
    }
    write(artifact_manifest_path, artifact_manifest)
    manifest_path = bundle / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    for name, key in (
            ("fixture.json", "fixture_sha256"),
            ("prompt.txt", "prompt_sha256"),
            ("events.jsonl", "events_sha256"),
            ("repo-before.json", "repo_before_sha256"),
            ("repo-after.json", "repo_after_sha256"),
            ("repo-comparison.json", "repo_comparison_sha256"),
            ("artifact-manifest.json", "artifact_manifest_sha256")):
        manifest[key] = sha((bundle / name).read_bytes())
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
        verdict[key] = manifest[key]
    verdict["bundle_sha256"] = bundle_hash(bundle)
    write(verdict_path, verdict)
    terminal_path = attempt / "attempt-terminal.json"
    terminal = json.loads(terminal_path.read_text(encoding="utf-8"))
    terminal["official_verdict_sha256"] = sha(verdict_path.read_bytes())
    write(terminal_path, terminal)
    rebind_attempt_seal(attempt)


def apply_retained_mutation(root, position, dimension):
    root = pathlib.Path(root)
    attempt = sorted(root.glob("attempt-*"))[position]
    bundle = attempt / "host-custody" / attempt.name / "bundle"
    cleanup = None
    if dimension == "missing":
        (attempt / "official-verdict.json").unlink()
        rebind_attempt_seal(attempt)
    elif dimension == "add":
        write(bundle / "artifacts" / "unexpected-retained.json",
              {"status": "PASS"})
        rebind_bundle_and_official(bundle)
    elif dimension == "remove":
        (bundle / "artifacts" / "host-stderr.raw").unlink()
        rebind_bundle_and_official(bundle)
    elif dimension == "rename":
        source = bundle / "artifacts" / "raw-host-events.jsonl"
        source.rename(bundle / "artifacts" / "renamed-host-events.jsonl")
        rebind_bundle_and_official(bundle)
    elif dimension == "mutate":
        event_path = bundle / "events.jsonl"
        event = json.loads(event_path.read_text(encoding="utf-8"))
        event["content"] = "retained response with no qualifying evidence"
        write(event_path, event)
        rebind_bundle_and_official(bundle)
    elif dimension == "alias":
        target = bundle / "artifacts" / "host-session.raw"
        cleanup = root.parent / (
            f"outside-alias-{position}-{attempt.name}.raw")
        os.link(target, cleanup)
    elif dimension == "type-drift":
        status_path = attempt / "attempt-status.json"
        status = json.loads(status_path.read_text(encoding="utf-8"))
        status["mission"]["index"] = float(status["mission"]["index"])
        write(status_path, status)
        rebind_attempt_seal(attempt)
    else:
        raise AssertionError(dimension)
    return cleanup


def assert_production_campaign_and_mutation_matrix(module):
    positions = (0, 7, 13)
    dimensions = (
        "missing", "add", "remove", "rename", "mutate", "alias",
        "type-drift",
    )
    with tempfile.TemporaryDirectory(
            prefix="candidate-matrix-production-shaped-") as tmp:
        base = pathlib.Path(tmp) / "baseline"
        build_campaign(base)
        result = module.rederive_campaign(
            base / "campaign-freeze.json", base)
        assert result["luna_stage_status"] == "PASS", result
        assert result["luna_stage_accepted"] is True
        assert result["accepted"] is False
        assert result["cell_count"] == 14
        assert result["execution_mode"] == "production"
        assert [row["fixture"] for row in result["cells"]] == list(
            module.FIXTURE_ORDER)
        expected_fields = {
            "index", "config", "fixture", "product_status", "host_status",
            "overall_status", "properties", "reason",
            "bundle_manifest_sha256", "raw_stdout_sha256",
            "native_session_sha256", "official_overall_status",
            "independent_overall_status", "model_resolved",
            "official_verdict_sha256", "execution_mode",
        }
        assert all(set(row) == expected_fields for row in result["cells"])
        assert all(
            row["execution_mode"] == "production"
            for row in result["cells"])
        for fixture_id, optional_name in (
                ("B0", "agents_update_decision"),):
            row = next(
                item for item in result["cells"]
                if item["fixture"] == fixture_id)
            assert row["properties"][optional_name] == {
                "state": "FAIL", "pass": False}
            assert row["product_status"] == "PASS"
            assert row["overall_status"] == "PASS"

        false_greens = []
        for position in positions:
            for dimension in dimensions:
                root = pathlib.Path(tmp) / f"case-{position}-{dimension}"
                shutil.copytree(base, root)
                rebase_campaign_paths(root)
                cleanup = apply_retained_mutation(
                    root, position, dimension)
                try:
                    try:
                        observed = module.rederive_campaign(
                            root / "campaign-freeze.json", root)
                    except module.EvidenceInvalid:
                        continue
                    if (observed.get("luna_stage_status") == "PASS" or
                            observed.get("luna_stage_accepted") is True or
                            observed.get("accepted") is True):
                        false_greens.append(
                            f"{position}:{dimension}={observed!r}")
                finally:
                    if cleanup is not None and cleanup.exists():
                        cleanup.unlink()
        assert not false_greens, (
            "production-shaped retained mutation produced Luna-green: " +
            ", ".join(false_greens))

        mixed = pathlib.Path(tmp) / "mixed-execution-mode"
        shutil.copytree(base, mixed)
        rebase_campaign_paths(mixed)
        attempt = mixed / "attempt-007-L-E4"
        status_path = attempt / "attempt-status.json"
        status = json.loads(status_path.read_text(encoding="utf-8"))
        status["execution_mode"] = "test"
        write(status_path, status)
        rebind_attempt_seal(attempt)
        mixed_result = module.rederive_campaign(
            mixed / "campaign-freeze.json", mixed)
        assert mixed_result["luna_stage_status"] == "INVALID", mixed_result
        assert mixed_result["disposition"] == "ANDON_STOPPED"
        assert mixed_result["luna_stage_accepted"] is False

        test_only = pathlib.Path(tmp) / "test-only"
        build_campaign(test_only, execution_mode="test")
        test_result = module.rederive_campaign(
            test_only / "campaign-freeze.json", test_only)
        assert test_result["execution_mode"] == "test"
        assert test_result["luna_stage_status"] == \
            "TEST_ONLY_NON_QUALIFYING", test_result
        assert test_result["disposition"] == "TEST_ONLY_NON_QUALIFYING"
        assert test_result["luna_stage_accepted"] is False
        assert test_result["accepted"] is False


def assert_host_check_producer_contract(module):
    accepted = [
        (
            {"key": "task_fixed", "kind": "file_regex",
             "path": "task.txt", "must_match": "receive"},
            {"task_fixed": True, "_detail": {}},
        ),
        (
            {"key": "task_fixed", "kind": "file_regex",
             "path": "task.txt", "must_match": "receive"},
            {"task_fixed": False, "_detail": {}},
        ),
        (
            {"key": "task_fixed", "kind": "file_regex",
             "path": "task.txt", "must_match": "receive"},
            {"task_fixed": False,
             "_detail": {"task_fixed": "file unreadable"}},
        ),
        (
            {"key": "run_root_valid", "kind": "validate_run_root"},
            {"run_root_valid": True, "_detail": {
                "run_root_valid": ".IMPLEMENTAUDIT/runs/x: exit 0; ok"}},
        ),
        (
            {"key": "run_root_exists", "kind": "run_root_exists",
             "dir": ".IMPLEMENTAUDIT/runs"},
            {"run_root_exists": True,
             "_detail": {"run_root_exists": "run-a"}},
        ),
        (
            {"key": "result_equal", "kind": "json_fields_equal",
             "path": "result.json", "equals": {"verdict": "accept"}},
            {"result_equal": True, "_detail": {}},
        ),
        (
            {"key": "read_before_write", "kind": "path_access_order",
             "reads": ["input.txt"], "write": "output.txt"},
            {"read_before_write": True, "_detail": {
                "read_before_write": json.dumps({
                    "host_status": "PASS", "live_preimage": True,
                    "ordered": True, "ordering_source": "persisted-ordinal",
                    "overall_status": "PASS", "property_status": "PASS",
                    "write_completed": True,
                }, sort_keys=True, separators=(",", ":"))}},
        ),
    ]
    for spec, artifact in accepted:
        module._validate_simple_host_checks([spec], artifact)
    rejected = [
        (
            [{"key": "run_root_exists", "kind": "run_root_exists"}],
            {"run_root_exists": True},
        ),
        (
            [{"key": "run_root_exists", "kind": "run_root_exists"}],
            {"run_root_exists": True, "_detail": {}},
        ),
        (
            [{"key": "run_root_exists", "kind": "run_root_exists"}],
            {"run_root_exists": True, "_detail": {
                "run_root_exists": "no run root on disk"}},
        ),
        (
            [{"key": "run_root_valid", "kind": "validate_run_root"}],
            {"run_root_valid": True, "_detail": {
                "run_root_valid": "validator unavailable"}},
        ),
        (
            [{"key": "task_fixed", "kind": "file_regex"}],
            {"task_fixed": True,
             "_detail": {"task_fixed": "file unreadable"}},
        ),
        (
            [{"key": "result_equal", "kind": "json_fields_equal"}],
            {"result_equal": False, "_detail": {}},
        ),
        (
            [{"key": "read_before_write", "kind": "path_access_order"}],
            {"read_before_write": False, "_detail": {
                "read_before_write": json.dumps({
                    "host_status": "PASS", "live_preimage": True,
                    "ordered": True, "ordering_source": "persisted-ordinal",
                    "overall_status": "PASS", "property_status": "PASS",
                    "write_completed": True,
                }, sort_keys=True, separators=(",", ":"))}},
        ),
        (
            [{"key": "mystery", "kind": "unknown_kind"}],
            {"mystery": True, "_detail": {}},
        ),
        (
            [{"key": "run_root_exists", "kind": "run_root_exists"}],
            {"run_root_exists": True, "_detail": {
                "run_root_exists": "run-a", "extra": "invented"}},
        ),
    ]
    for specs, artifact in rejected:
        try:
            module._validate_simple_host_checks(specs, artifact)
        except module.EvidenceInvalid:
            pass
        else:
            raise AssertionError(
                f"host-check producer contract accepted {specs!r}, "
                f"{artifact!r}")


def assert_background_read_rejected_through_matrix_path(module):
    content = b"retained candidate preimage\n"
    preimages = {
        "repo": {
            "lexical_root": "/candidate",
            "real_root": "/candidate",
            "case_sensitive": True,
        },
        "targets": {
            "README.md": {
                "canonical_path": "/candidate/README.md",
                "relative_path": "README.md",
                "content_base64": base64.b64encode(content).decode(),
                "sha256": sha(content),
                "size": len(content),
                "mode": 0o100644,
                "symlink_free": True,
            },
        },
    }
    spec = {
        "key": "read-before-write",
        "kind": "path_access_order",
        "reads": ["README.md"],
        "write": "result.json",
    }
    for command in (
            "cat README.md & true",
            '/bin/bash -lc "cat README.md & true"'):
        read = _trace_action(
            "read-preimage", 3, command, content.decode())
        write_action = {
            "id": "write-result",
            "state": "COMPLETED",
            "effect": "write",
            "path": "result.json",
            "invocation_ordinal": 5,
            "completion_ordinal": 6,
        }
        assert module._action_is_read(
            read, "README.md", content, preimages) is False, command
        row = module._matrix_row(
            spec, [read, write_action], preimages)
        assert row["property_status"] == "INCOMPLETE", (command, row)
        assert row["reads"]["README.md"]["classification"] == "fail-closed", (
            command, row)


def assert_independent_pass_property_boundary(module):
    declarations = {}
    rows = []
    for index, fixture_id in enumerate(module.FIXTURE_ORDER):
        fixture = json.loads(
            (HERE / "fixtures" / fixture_id / "fixture.json").read_text(
                encoding="utf-8"))
        declaration = {
            prop["name"]: prop["required"]
            for prop in fixture["properties"]
        }
        declarations[index] = declaration
        properties = {
            name: {"state": "PASS", "pass": True}
            for name in declaration
        }
        for name, required in declaration.items():
            if not required and fixture_id == "B0":
                properties[name] = {"state": "FAIL", "pass": False}
        rows.append({
            "index": index, "config": "L", "fixture": fixture_id,
            "execution_mode": "production",
            "product_status": "PASS", "host_status": "PASS",
            "overall_status": "PASS", "properties": properties,
            "reason": None, "bundle_manifest_sha256": "1" * 64,
            "raw_stdout_sha256": "2" * 64,
            "native_session_sha256": "3" * 64,
            "official_overall_status": "PASS",
            "independent_overall_status": "PASS",
            "model_resolved": LUNA_MODEL,
            "official_verdict_sha256": "4" * 64,
        })
    module._validate_stage_pass_rows(rows, declarations, LUNA_MODEL)
    assert rows[0]["properties"]["agents_update_decision"] == {
        "state": "FAIL", "pass": False}
    assert rows[8]["properties"]["current_answer_correctness"] == {
        "state": "PASS", "pass": True}
    mutations = []
    required_fail = json.loads(json.dumps(rows))
    required_fail[0]["properties"]["phase_start"] = {
        "state": "FAIL", "pass": False}
    mutations.append(required_fail)
    missing = json.loads(json.dumps(rows))
    del missing[0]["properties"]["phase_start"]
    mutations.append(missing)
    extra = json.loads(json.dumps(rows))
    extra[0]["properties"]["invented_property"] = {
        "state": "PASS", "pass": True}
    mutations.append(extra)
    for changed in mutations:
        try:
            module._validate_stage_pass_rows(
                changed, declarations, LUNA_MODEL)
        except module.EvidenceInvalid:
            pass
        else:
            raise AssertionError(
                "independent PASS property boundary accepted invalid rows")
    false_accepts = []
    for label, model in (
            ("Sol", "gpt-5.6-sol"),
            ("Terra", "gpt-5.6-terra"),
            ("arbitrary", "not-luna")):
        changed = json.loads(json.dumps(rows))
        for row in changed:
            row["model_resolved"] = model
        try:
            module._validate_stage_pass_rows(
                changed, declarations, LUNA_MODEL)
        except module.EvidenceInvalid:
            pass
        else:
            false_accepts.append(label)
    single_row = json.loads(json.dumps(rows))
    single_row[6]["model_resolved"] = "gpt-5.6-sol"
    try:
        module._validate_stage_pass_rows(
            single_row, declarations, LUNA_MODEL)
    except module.EvidenceInvalid:
        pass
    else:
        false_accepts.append("single-row-model-mismatch")
    try:
        module._validate_stage_pass_rows(
            rows, declarations, "gpt-5.6-sol")
    except module.EvidenceInvalid:
        pass
    else:
        false_accepts.append("stage-row-model-mismatch")
    assert not false_accepts, (
        "independent accepted-result model false accepts: " +
        ", ".join(false_accepts))


def load_module():
    spec = importlib.util.spec_from_file_location("candidate_matrix_rederive", MODULE)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def assert_profile_policy_pipeline(module):
    with tempfile.TemporaryDirectory(
            prefix="matrix-profile-policy-pipeline-") as tmp:
        baseline = pathlib.Path(tmp) / "baseline"
        build_campaign(baseline)
        for label in ("missing-bool", "integer-bool", "duplicate-bool"):
            root = pathlib.Path(tmp) / label
            shutil.copytree(baseline, root)
            rebase_campaign_paths(root)
            first = sorted(root.glob("attempt-*"))[0]
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
            rebind_bundle_and_official(bundle)
            result = module.rederive_campaign(
                root / "campaign-freeze.json", root)
            assert result["luna_stage_status"] == "INVALID", (label, result)


def assert_real_codex_turn_shapes(module):
    usage = {
        "input_tokens": 210236, "cached_input_tokens": 189696,
        "output_tokens": 6048, "reasoning_output_tokens": 3716,
    }
    rows = [
        {"type": "thread.started", "thread_id": "retained-thread"},
        {"type": "turn.started"},
        {"type": "item.completed", "item": {
            "id": "message-1", "type": "agent_message",
            "text": "Inspect the retained evidence first."}},
        {"type": "item.started", "item": {
            "id": "command-1", "type": "command_execution",
            "status": "in_progress", "command": "git status --short",
            "aggregated_output": "", "exit_code": None}},
        {"type": "item.completed", "item": {
            "id": "command-1", "type": "command_execution",
            "status": "completed", "command": "git status --short",
            "aggregated_output": "", "exit_code": 0}},
        {"type": "turn.completed", "usage": usage},
    ]

    def raw(candidate):
        return b"".join(encoded(row) for row in candidate)

    actions, binding = module._parse_codex_actions(raw(rows))
    assert binding == {
        "thread_id": "retained-thread", "stdout_turn_ordinal": 1}
    assert [row["state"] for row in actions] == [
        "TERMINAL_SAFE_MESSAGE", "COMPLETED"]

    retained_shapes = {
        "B0": copy.deepcopy(rows),
        "B1": copy.deepcopy(rows),
        "B2": copy.deepcopy(rows),
        "E1": copy.deepcopy(rows),
    }
    retained_shapes["B0"].insert(-1, {
        "type": "item.started", "item": {
            "id": "file-1", "type": "file_change",
            "status": "in_progress", "changes": [
                {"path": "STATE.md", "kind": "update"}]}})
    retained_shapes["B0"].insert(-1, {
        "type": "item.completed", "item": {
            "id": "file-1", "type": "file_change",
            "status": "completed", "changes": [
                {"path": "STATE.md", "kind": "update"}]}})
    for fixture, candidate in retained_shapes.items():
        parsed, retained_binding = module._parse_codex_actions(raw(candidate))
        assert retained_binding == {
            "thread_id": "retained-thread", "stdout_turn_ordinal": 1}, fixture
        assert parsed, fixture

    explicit = copy.deepcopy(rows)
    explicit[1].update(
        {"thread_id": "retained-thread", "turn_id": "turn-1"})
    explicit[-1].update(
        {"thread_id": "retained-thread", "turn_id": "turn-1"})
    _actions, explicit_binding = module._parse_codex_actions(raw(explicit))
    assert explicit_binding["turn_id"] == "turn-1"

    invalid = {}
    invalid["multiple-turns"] = copy.deepcopy(rows) + [
        {"type": "turn.started"},
        {"type": "turn.completed", "usage": copy.deepcopy(usage)},
    ]
    invalid["thread-drift"] = copy.deepcopy(explicit)
    invalid["thread-drift"][1]["thread_id"] = "other-thread"
    invalid["completion-thread-drift"] = copy.deepcopy(explicit)
    invalid["completion-thread-drift"][-1]["thread_id"] = "other-thread"
    invalid["conflicting-turn-id"] = copy.deepcopy(explicit)
    invalid["conflicting-turn-id"][-1]["turn_id"] = "turn-2"
    invalid["completion-without-usage"] = copy.deepcopy(rows)
    invalid["completion-without-usage"][-1].pop("usage")
    invalid["minimal-start-sentinel-completion"] = copy.deepcopy(rows)
    invalid["minimal-start-sentinel-completion"][-1]["turn_id"] = \
        "<unique-turn>"
    invalid["symmetric-explicit-sentinel"] = copy.deepcopy(explicit)
    invalid["symmetric-explicit-sentinel"][1]["turn_id"] = \
        "<unique-turn>"
    invalid["symmetric-explicit-sentinel"][-1]["turn_id"] = \
        "<unique-turn>"
    invalid["minimal-start-explicit-completion"] = copy.deepcopy(rows)
    invalid["minimal-start-explicit-completion"][-1].update({
        "thread_id": "retained-thread", "turn_id": "turn-1"})
    invalid["explicit-start-identityless-completion"] = \
        copy.deepcopy(explicit)
    invalid["explicit-start-identityless-completion"][-1] = {
        "type": "turn.completed", "usage": copy.deepcopy(usage)}
    invalid["partial-explicit-start"] = copy.deepcopy(rows)
    invalid["partial-explicit-start"][1]["thread_id"] = "retained-thread"
    invalid["partial-turn-only-start"] = copy.deepcopy(rows)
    invalid["partial-turn-only-start"][1]["turn_id"] = "turn-1"
    invalid["partial-explicit-completion"] = copy.deepcopy(rows)
    invalid["partial-explicit-completion"][-1]["thread_id"] = \
        "retained-thread"
    invalid["partial-turn-only-completion"] = copy.deepcopy(rows)
    invalid["partial-turn-only-completion"][-1]["turn_id"] = "turn-1"
    invalid["missing-completion"] = copy.deepcopy(rows[:-1])
    invalid["duplicate-completion"] = copy.deepcopy(rows) + [
        copy.deepcopy(rows[-1])]
    invalid["action-outside-turn"] = copy.deepcopy(rows)
    invalid["action-outside-turn"][1], \
        invalid["action-outside-turn"][2] = \
        invalid["action-outside-turn"][2], \
        invalid["action-outside-turn"][1]
    invalid["unknown-field"] = copy.deepcopy(rows)
    invalid["unknown-field"][1]["unexpected"] = True
    invalid["invalid-usage"] = copy.deepcopy(rows)
    invalid["invalid-usage"][-1]["usage"]["input_tokens"] = -1
    invalid["command-start-missing-output"] = copy.deepcopy(rows)
    invalid["command-start-missing-output"][3]["item"].pop(
        "aggregated_output")
    invalid["command-start-nonempty-output"] = copy.deepcopy(rows)
    invalid["command-start-nonempty-output"][3]["item"][
        "aggregated_output"] = "premature"
    invalid["command-start-nonnull-exit"] = copy.deepcopy(rows)
    invalid["command-start-nonnull-exit"][3]["item"]["exit_code"] = 0
    for label, candidate in invalid.items():
        try:
            module._parse_codex_actions(raw(candidate))
        except module.EvidenceInvalid:
            pass
        else:
            raise AssertionError(f"Codex raw stdout accepted {label}")


def main():
    tree = ast.parse(MODULE.read_text(encoding="utf-8"))
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module)
    assert not (imports & FORBIDDEN), imports & FORBIDDEN
    module = load_module()
    assert_real_codex_turn_shapes(module)
    assert_profile_policy_pipeline(module)
    # Governing RED R5 applies independently to the matrix implementation.
    with tempfile.TemporaryDirectory(
            prefix="matrix-surface-custody-red-") as tmp:
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
                    "independent matrix accepted a physical virtual shadow")
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
                "independent matrix surface hash drift was accepted")
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
                "independent matrix internal role accepted an external path")

    assert_host_check_producer_contract(module)
    assert_background_read_rejected_through_matrix_path(module)
    assert_independent_pass_property_boundary(module)
    assert_production_campaign_and_mutation_matrix(module)
    assert module.FIXTURE_ORDER == (
        "B0", "B1", "B2", "E1", "E2a", "E2b", "E3", "E4",
        "E5", "E6", "E7", "E8", "E9", "E10")
    assert module._exact_json_equal({"x": [0.0]}, {"x": [0.0]})
    assert not module._exact_json_equal(False, 0)
    assert not module._exact_json_equal(0.0, -0.0)
    claims = module.FINAL_CLAIMS
    assert claims == {
        "final_28_of_28": False,
        "cross_model_qualified": False,
        "release_authorized": False,
        "tag_authorized": False,
        "publication_authorized": False,
    }
    packet = valid_packet()
    packet["independent_rederiver"]["implementation_identity"]["sha256"] = \
        hashlib.sha256(MODULE.read_bytes()).hexdigest()
    next(row for row in packet["evaluated_surfaces"]["entries"]
         if row["role"] == "independent-rederiver")["sha256"] = \
        packet["independent_rederiver"]["implementation_identity"]["sha256"]
    module._validate_freeze_contract(packet)
    for mutation in ("missing", "duplicate"):
        changed = copy.deepcopy(packet)
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
    changed = copy.deepcopy(packet)
    changed["evaluated_surface_owners"]["roles"].pop("scorer")
    owner_mutations.append(changed)
    changed = copy.deepcopy(packet)
    changed["evaluated_surface_owners"]["roles"]["extra"] = {
        "kind": "frozen-extra", "sha256": "a" * 64}
    owner_mutations.append(changed)
    changed = copy.deepcopy(packet)
    changed["evaluated_surface_owners"]["roles"]["scorer"]["kind"] = \
        "packet-artifact-evaluator"
    owner_mutations.append(changed)
    changed = copy.deepcopy(packet)
    roles = changed["evaluated_surface_owners"]["roles"]
    roles["scorer"], roles["evaluator"] = roles["evaluator"], roles["scorer"]
    owner_mutations.append(changed)
    changed = copy.deepcopy(packet)
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
                "independent matrix rederiver accepted semantic owner drift")
    for alias in (14.0, True):
        changed = json.loads(json.dumps(packet))
        changed["attempt_policy"]["maximum_attempts"] = alias
        try:
            module._validate_freeze_contract(changed)
        except module.EvidenceInvalid:
            pass
        else:
            raise AssertionError("numeric alias accepted by independent contract")

    for raw in (
            b'{"a":1,"a":2}', b'{"a":{"b":1,"b":2}}',
            b'{"a":NaN}', b'{"a":Infinity}'):
        try:
            module._decode_json(
                raw, "strict retained JSON", "malformed retained JSON", True)
        except module.EvidenceInvalid:
            pass
        else:
            raise AssertionError("malformed retained JSON accepted")

    for fixture_id in module.FIXTURE_ORDER:
        fixture_path = HERE / "fixtures" / fixture_id / "fixture.json"
        fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
        module._validate_fixture_schema(fixture, fixture_id)
        transcript = (HERE / "fixtures" / fixture_id /
                      "transcript_pass.txt").read_text(encoding="utf-8")
        summary_path = (HERE / "fixtures" / fixture_id /
                        "transcript_pass.summary.json")
        summary = (
            json.loads(summary_path.read_text(encoding="utf-8"))
            if summary_path.exists() else {"changed_files": []})
        states = [
            module._eval_rule(
                prop["rule"], {"assistant": transcript}, summary)
            for prop in fixture["properties"] if prop["required"]]
        assert states and all(state is True for state in states), (
            fixture_id, states)

    fixtures = {
        fixture_id: json.loads(
            (HERE / "fixtures" / fixture_id / "fixture.json").read_text(
                encoding="utf-8"))
        for fixture_id in ("B0", "E5", "E6")
    }
    assert "result.json" in module._required_capture_files(fixtures["E5"])
    preimages = {
        "repo": {"lexical_root": "/candidate", "case_sensitive": True},
        "targets": {},
    }
    module._validate_write_boundary(
        [{"effect": "write", "path": "/candidate/task.txt"}],
        fixtures["B0"], preimages)
    module._validate_write_boundary(
        [{"effect": "write",
          "path": "/candidate/.IMPLEMENTAUDIT/run.json"}],
        fixtures["B0"], preimages)
    module._validate_write_boundary(
        [{"effect": "write", "path": "/candidate/docs/analysis.md"}],
        fixtures["E6"], preimages)
    for fixture_id, path in (
            ("B0", "/candidate/src/escape.py"),
            ("E5", "/candidate/result.json"),
            ("E6", "/candidate/src/escape.py")):
        try:
            module._validate_write_boundary(
                [{"effect": "write", "path": path}],
                fixtures[fixture_id], preimages)
        except module.EvidenceInvalid:
            pass
        else:
            raise AssertionError(
                f"{fixture_id} accepted out-of-bound write {path}")

    result = {
        "schema":
            "implementaudit-candidate-matrix-luna-independent-rederivation-v1",
        "campaign": "candidate-matrix-sol-luna-r1",
        "freeze_sha256": "a" * 64,
        "contract_sha256": module.CONTRACT_SHA256,
        "execution_mode": None,
        "luna_stage_status": "INVALID", "disposition": "ANDON_STOPPED",
        "luna_stage_accepted": False, "accepted": False,
        "cell_count": 0, "cells": [], "claims": dict(module.FINAL_CLAIMS),
    }
    with tempfile.TemporaryDirectory() as tmp:
        root = pathlib.Path(tmp).resolve()
        path = root / "candidate-matrix-luna-independent-rederivation.json"
        module.write_rederivation(path, result, root=root)
        assert path.is_file()
        try:
            module.write_rederivation(path, result, root=root)
        except module.EvidenceInvalid as exc:
            assert "create-once" in str(exc)
        else:
            raise AssertionError("independent result overwrite accepted")
    print("candidate matrix rederive: PASS")


if __name__ == "__main__":
    main()
