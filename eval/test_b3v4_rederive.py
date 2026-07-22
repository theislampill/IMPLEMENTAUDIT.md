#!/usr/bin/env python3
"""Deterministic tests for the independent B3-v4 evidence rederiver."""
from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import pathlib
import tempfile

from test_b3v4_freeze import valid_packet


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
        "renames": [], "untracked": {}, "worktree_files": files,
        "tracked_diff_sha256": sha(b""),
    }
    body = json.dumps(value, sort_keys=True).encode()
    value["snapshot_sha256"] = sha(body)
    return value


def make_fixture():
    return json.loads((HERE / "fixtures" / "B3-v3" / "fixture.json").read_text(
        encoding="utf-8"))


def build_campaign(root):
    root = pathlib.Path(root)
    fixture = make_fixture()
    fixture_bytes = (HERE / "fixtures" / "B3-v3" / "fixture.json").read_bytes()
    packet = valid_packet()
    packet["fixture"]["fixture_sha256"] = sha(fixture_bytes)
    packet_bytes = json.dumps(packet, sort_keys=True).encode()
    freeze_sha = sha(packet_bytes)
    write(root / "campaign-freeze.json", packet_bytes)
    write(root / "campaign-manifest.json", {
        "schema": "implementaudit-b3v4-campaign-custody-v1",
        "campaign": "b3v4-sol-r1", "freeze_sha256": freeze_sha,
        "created_at": "2030-01-01T00:00:00Z",
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
    for mission in packet["missions"]:
        name = (f"attempt-{mission['index']:03d}-{mission['config']}-"
                f"{mission['arm']}-r{mission['rep']}")
        attempt = root / name
        host_root = attempt / "host-custody" / name
        bundle = host_root / "bundle"
        model = packet["configurations"][mission["config"]][
            "model_resolved_required"]
        adapter = "codex-cli" if mission["config"] == "L" else "claude-cli"
        write(attempt / "attempt-status.json", {
            "schema": "implementaudit-b3v4-attempt-status-v1",
            "campaign": "b3v4-sol-r1", "freeze_sha256": freeze_sha,
            "mission": mission, "state": "PREPARED_BEFORE_HOST_SPAWN",
            "execution_mode": "production", "created_at": "2030-01-01T00:00:00Z",
        })
        write(attempt / "attempt-terminal.json", {
            "schema": "implementaudit-b3v4-attempt-terminal-v1",
            "campaign": "b3v4-sol-r1", "mission_index": mission["index"],
            "execution_mode": "production", "overall_status": "PASS",
            "resolved_model": model, "host_run_root": str(host_root),
            "completed_at": "2030-01-01T00:00:01Z",
        })
        before = snapshot({})
        after = snapshot({capsule_path: {"type": "file", "sha256": sha(capsule_bytes)}})
        after["untracked"] = {capsule_path: {"type": "file", "sha256": sha(capsule_bytes)}}
        body = {k: v for k, v in after.items() if k != "snapshot_sha256"}
        after["snapshot_sha256"] = sha(json.dumps(body, sort_keys=True).encode())
        profile = {
            "schema": "implementaudit-host-read-profile-v2",
            "authority": "mechanically-minted",
            "host": "codex" if mission["config"] == "L" else "claude",
            "repo": {"lexical_root": "/repo", "real_root": "/repo",
                     "case_sensitive": True},
        }
        reads = fixture["host_checks"]["specs"][1]["reads"]
        targets = {}
        actions = []
        ordinal = 1
        for target in reads:
            content = ("STATE\n" if target.endswith("STATE.md") else "ROADMAP\n").encode()
            targets[target] = {"canonical_path": "/repo/" + target,
                               "sha256": sha(content),
                               "content_base64": __import__("base64").b64encode(content).decode()}
            actions.append({"id": f"read-{ordinal}", "state": "COMPLETED",
                            "effect": "read", "path": target, "inputs": {},
                            "output": content.decode(), "invocation_ordinal": ordinal,
                            "completion_ordinal": ordinal + 1})
            ordinal += 2
        actions.append({"id": "write", "state": "COMPLETED", "effect": "write",
                        "path": capsule_path, "inputs": {},
                        "invocation_ordinal": ordinal, "completion_ordinal": ordinal + 1})
        preimages = {"schema": "implementaudit-host-read-preimages-v1",
                     "repo": profile["repo"], "targets": targets}
        checks = [{"key": "live_state_read_before_capsule_write",
                   "reads": reads, "write": capsule_path}]
        intent = {"fixture_sha256": sha(fixture_bytes), "run_id": name}
        replay = {"schema": "implementaudit-host-read-replay-spec-v1",
                  "mode": "formal-v2", "host": profile["host"], "checks": checks,
                  "requested_tools": [] if mission["config"] == "L" else ["Read", "Write"],
                  "fixture_sha256": sha(fixture_bytes),
                  "run_intent_sha256": sha(encoded(intent)), "parser_sha256": "f" * 64}
        if mission["config"] == "L":
            raw_events = []
            for action in actions[:-1]:
                item = {"id": action["id"], "type": "command_execution",
                        "status": "in_progress", "command": "cat " + action["path"]}
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
        raw_session = encoded({"synthetic": "native-session", "run_id": name})
        trace = {"schema": "implementaudit-host-tool-trace-v2", "actions": actions,
                 "invalid": False, "host_findings": [], "ids_reserved": True,
                 "action_states": ["COMPLETED"] * len(actions),
                 "action_effects": [a["effect"] for a in actions],
                 "host_status": "PASS", "observed_tools": []}
        matrix = {"schema": "implementaudit-host-read-matrix-v1",
                  "raw_transforms": {}, "specs": {}}
        post = copy.deepcopy(profile)
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
                    "profile_post_status": "PASS", "binding": {},
                    "actual_tools": [], "normalized_host_status": "PASS",
                    "host_terminal_kind": "ok", "session_bound": True,
                    "session_status": "VALID"}
        files["host-read-terminal.json"] = encoded(terminal)
        capture_manifest = {"schema": "implementaudit-host-read-manifest-v1",
                            "files": {key: sha(value) for key, value in files.items()}}
        files["host-read-manifest.json"] = encoded(capture_manifest)
        files["run-intent.json"] = encoded(intent)
        files["process-started.json"] = encoded({
            "host_read_pre_spawn_sha256": sha(files["host-read-pre-spawn.json"]),
            "run_id": name})
        files["host-checks.json"] = encoded({spec["key"]: True
                                              for spec in fixture["host_checks"]["specs"]})
        files["host-check-inputs/" + capsule_path] = capsule_bytes
        artifact_manifest = {"files": {key: sha(value) for key, value in files.items()}}
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
            "events_sha256": sha(encoded({"event": "retained"})),
            "repo_before_sha256": sha(encoded(before)),
            "repo_after_sha256": sha(encoded(after)),
            "artifact_manifest_sha256": sha(encoded(artifact_manifest)),
        }
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
        write(bundle / "events.jsonl", encoded({"event": "retained"}))
        write(bundle / "repo-before.json", before)
        write(bundle / "repo-after.json", after)
        write(bundle / "artifact-manifest.json", artifact_manifest)
        for rel, data in files.items():
            write(bundle / "artifacts" / rel, data)
    return packet


def load_module():
    spec = importlib.util.spec_from_file_location("b3v4rederive", REDERIVER)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


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


def main():
    module = load_module()
    with tempfile.TemporaryDirectory(prefix="b3v4-rederive-") as tmp:
        root = pathlib.Path(tmp) / "campaign"
        packet = build_campaign(root)
        result = module.rederive_campaign(root / "campaign-freeze.json", root)
        assert result["campaign_status"] == "PASS", result
        assert result["accepted"] is True
        assert len(result["missions"]) == 12
        assert all(row["product_status"] == "PASS" for row in result["missions"])
        assert all(len(row["properties"]) == 6 for row in result["missions"])

        first = root / "attempt-000-L-candidate-r1"
        terminal_path = first / "attempt-terminal.json"
        terminal = json.loads(terminal_path.read_text(encoding="utf-8"))
        terminal["resolved_model"] = "substituted-model"
        write(terminal_path, terminal)
        invalid = module.rederive_campaign(root / "campaign-freeze.json", root)
        assert invalid["campaign_status"] == "INVALID"
        assert invalid["accepted"] is False
        terminal["resolved_model"] = packet["configurations"]["L"]["model_resolved_required"]
        write(terminal_path, terminal)

        raw = (first / "host-custody" / first.name / "bundle" / "artifacts" /
               "host-session.raw")
        raw.write_bytes(b"tampered\n")
        invalid = module.rederive_campaign(root / "campaign-freeze.json", root)
        assert invalid["campaign_status"] == "INVALID"
        assert "hash" in invalid["missions"][0]["reason"]

    with tempfile.TemporaryDirectory(prefix="b3v4-rederive-") as tmp:
        root = pathlib.Path(tmp) / "campaign"
        build_campaign(root)
        first = root / "attempt-000-L-candidate-r1"
        bundle = first / "host-custody" / first.name / "bundle"
        raw = bundle / "artifacts" / "host-stdout.raw"
        events = [json.loads(line) for line in raw.read_text(encoding="utf-8").splitlines()]
        events[0]["item"]["command"] = "printf 'STATE\\n'"
        events[1]["item"]["command"] = "printf 'STATE\\n'"
        raw.write_bytes(b"".join(encoded(event) for event in events))
        rebind_capture(bundle)
        falsified = module.rederive_campaign(root / "campaign-freeze.json", root)
        assert falsified["campaign_status"] == "FAIL", falsified["missions"][0]
        assert falsified["missions"][0]["properties"][
            "live_state_read_before_mutation"]["state"] == "FAIL"

    print("test_b3v4_rederive: ok")


if __name__ == "__main__":
    main()
