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


HERE = pathlib.Path(__file__).resolve().parent
MODULE = HERE / "candidate_matrix_rederive.py"
FORBIDDEN = {
    "candidate_matrix_campaign", "campaign_lifecycle", "b3v4_campaign",
    "b3v4_rederive", "b3v4_contract", "hosts", "runner", "adapters",
    "lib.scoring", "eval.lib.scoring",
}
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
            "state": "PASS", "pass": True,
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


def build_campaign(root, *, execution_mode="production"):
    root = pathlib.Path(root)
    packet = valid_packet()
    packet["independent_rederiver"]["implementation_identity"]["sha256"] = \
        sha(MODULE.read_bytes())
    fixture_values = {}
    fixture_bytes = {}
    for row in packet["fixtures"]:
        raw = (HERE.parent / row["path"]).read_bytes()
        row["sha256"] = sha(raw)
        fixture_bytes[row["id"]] = raw
        fixture_values[row["id"]] = json.loads(raw)
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
                "status": "in_progress", "command": command}},
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
        })
        raw_stdout = b"".join(encoded(event) for event in raw_events)
        raw_session = b"".join(encoded(event) for event in [
            {
                "type": "session_meta",
                "timestamp": "2030-01-01T00:00:00Z",
                "payload": {
                    "id": name, "session_id": name, "cwd": repo_root,
                },
            },
            {
                "type": "turn_context",
                "timestamp": "2030-01-01T00:00:00Z",
                "payload": {"turn_id": "native-turn", "cwd": repo_root},
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
        checks = {
            spec["key"]: True
            for spec in (fixture.get("host_checks") or {}).get("specs", [])
        }
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
                "current_verdict": "accept",
                "p1_verdict": "reject",
                "p2_verdict": "accept",
            })
        artifact_manifest = {
            "files": {key: sha(value) for key, value in files.items()}
        }
        transcript = (
            HERE / "fixtures" / fixture_id /
            "transcript_pass.txt").read_text(encoding="utf-8")
        retained_event = encoded({
            "schema": "implementaudit-eval-event-v1", "run_id": name,
            "fixture_id": fixture_id, "seq": 1, "role": "assistant",
            "kind": "message", "content": transcript,
            "recorded_at": "2030-01-01T00:00:01Z",
        })
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
        assert [row["fixture"] for row in result["cells"]] == list(
            module.FIXTURE_ORDER)
        expected_fields = {
            "index", "config", "fixture", "product_status", "host_status",
            "overall_status", "properties", "reason",
            "bundle_manifest_sha256", "raw_stdout_sha256",
            "native_session_sha256", "official_overall_status",
            "independent_overall_status", "model_resolved",
            "official_verdict_sha256",
        }
        assert all(set(row) == expected_fields for row in result["cells"])

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


def load_module():
    spec = importlib.util.spec_from_file_location("candidate_matrix_rederive", MODULE)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


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
    module._validate_freeze_contract(packet)
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
