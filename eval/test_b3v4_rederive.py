#!/usr/bin/env python3
"""Deterministic tests for the independent B3-v4 evidence rederiver."""
from __future__ import annotations

import ast
import copy
import hashlib
import importlib.util
import json
import pathlib
import shutil
import tempfile

from test_b3v4_freeze import valid_packet
import runner as official_runner


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


def synthetic_official_pass(fixture, model):
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
        "model_resolved": model, "model_substitution": False,
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
    }


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
        "contract_sha256": packet["artifact_contract"]["sha256"],
        "created_at": "2030-01-01T00:00:00Z",
        "execution_stage": "LUNA_THEN_OPUS_UNCHANGED_PACKET",
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
            "contract_sha256": packet["artifact_contract"]["sha256"],
            "mission": mission, "state": "PREPARED_BEFORE_HOST_SPAWN",
            "execution_mode": "production", "created_at": "2030-01-01T00:00:00Z",
        })
        attempt_terminal = {
            "schema": "implementaudit-b3v4-attempt-terminal-v1",
            "campaign": "b3v4-sol-r1", "mission_index": mission["index"],
            "execution_mode": "production", "overall_status": "PASS",
            "resolved_model": model, "host_run_root": str(host_root),
            "official_overall_status": None,
            "official_verdict_sha256": None,
            "stop_reason": None, "error_type": None,
            "completed_at": "2030-01-01T00:00:01Z",
        }
        write(attempt / "attempt-terminal.json", attempt_terminal)
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
        write(bundle / "events.jsonl", retained_event)
        write(bundle / "repo-before.json", before)
        write(bundle / "repo-after.json", after)
        write(bundle / "artifact-manifest.json", artifact_manifest)
        for rel, data in files.items():
            write(bundle / "artifacts" / rel, data)
        official_status = "PASS"
        official_verdict = synthetic_official_pass(fixture, model)
        official_bytes = encoded(official_verdict)
        write(attempt / "official-verdict.json", official_bytes)
        attempt_terminal.update({
            "official_overall_status": official_status,
            "official_verdict_sha256": sha(official_bytes),
        })
        write(attempt / "attempt-terminal.json", attempt_terminal)
    return packet


def load_module():
    spec = importlib.util.spec_from_file_location("b3v4rederive", REDERIVER)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def assert_independent_import_boundary():
    tree = ast.parse(REDERIVER.read_text(encoding="utf-8"))
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.append(node.module)
    forbidden = {
        "eval.hosts", "eval.runner", "eval.lib.scoring",
        "eval.validate_b3v4_freeze", "validate_b3v4_freeze",
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


def main():
    assert_independent_import_boundary()
    module = load_module()
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
            (("configurations", "O", "auth_mode"), "metered-api",
             "configuration O"),
            (("authorization", "metered_api_spend"), "allowed",
             "metered_api_spend"),
            (("seed",), 0, "seed"),
            (("repetitions_per_configuration_and_arm",), 1,
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

    with tempfile.TemporaryDirectory(prefix="b3v4-rederive-prefix-") as tmp:
        root = pathlib.Path(tmp) / "campaign"
        packet = build_campaign(root)
        for mission in packet["missions"][2:]:
            name = (f"attempt-{mission['index']:03d}-{mission['config']}-"
                    f"{mission['arm']}-r{mission['rep']}")
            shutil.rmtree(root / name)
        prefix = module.rederive_campaign(root / "campaign-freeze.json", root)
        assert prefix["campaign_status"] == "INCOMPLETE", prefix
        assert prefix["accepted"] is False and prefix["mission_count"] == 2
        (root / "unexpected-summary.json").write_text("{}", encoding="utf-8")
        try:
            module.rederive_campaign(root / "campaign-freeze.json", root)
        except module.EvidenceInvalid as exc:
            assert "unexpected custody" in str(exc), str(exc)
        else:
            raise AssertionError("unexpected campaign artifact was accepted")

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
        counterexample = module.rederive_campaign(
            root / "campaign-freeze.json", root)
        assert counterexample["campaign_status"] == "INVALID", counterexample
        assert counterexample["accepted"] is False

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
        counterexample = module.rederive_campaign(
            root / "campaign-freeze.json", root)
        assert counterexample["campaign_status"] == "INVALID", counterexample
        assert counterexample["accepted"] is False
        assert "official property key set" in counterexample["missions"][0]["reason"]

    with tempfile.TemporaryDirectory(prefix="b3v4-rederive-") as tmp:
        root = pathlib.Path(tmp) / "campaign"
        packet = build_campaign(root)
        result = module.rederive_campaign(root / "campaign-freeze.json", root)
        assert result["campaign_status"] == "PASS", result

        first = root / "attempt-000-L-candidate-r1"
        terminal_path = first / "attempt-terminal.json"
        terminal = json.loads(terminal_path.read_text(encoding="utf-8"))
        terminal["overall_status"] = "FAIL"
        write(terminal_path, terminal)
        disagreement = module.rederive_campaign(root / "campaign-freeze.json", root)
        assert disagreement["campaign_status"] == "INVALID", disagreement
        assert disagreement["accepted"] is False
        first_row = disagreement["missions"][0]
        assert first_row["overall_status"] == "INVALID"
        assert "disagree" in first_row["reason"]
        terminal["overall_status"] = "PASS"
        write(terminal_path, terminal)

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
        ambiguous = module.rederive_campaign(
            root / "campaign-freeze.json", root)
        assert ambiguous["campaign_status"] == "INVALID", ambiguous["missions"][0]
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
        rebound = module.rederive_campaign(root / "campaign-freeze.json", root)
        assert rebound["campaign_status"] == "INVALID", rebound
        assert "artifact set" in rebound["missions"][0]["reason"]

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
        assert falsified["campaign_status"] == "INVALID", falsified["missions"][0]
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
