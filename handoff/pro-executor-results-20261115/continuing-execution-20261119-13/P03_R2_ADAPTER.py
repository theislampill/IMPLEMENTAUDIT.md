#!/usr/bin/env python3
"""Ordinary Root admission around existing recording methods, not a host mode.

Python binds supplied host evidence. Model/backend authentication and semantic
Root receiving remain outside Python. No actor or provider API is called here.
"""
from __future__ import annotations
import argparse
import datetime
import fcntl
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import re
import stat
import sys
import uuid

BASE = Path(__file__).resolve().parent
OWNER_SHA = "feb54b993b30f97442945ed9c9543ec652e1bd008f6504fc1d08eaf4cf731fdd"
PRIMITIVE_SHA = "348bebac70e43bb8fba37e3731ab73b7bf8f99f5fbd9baf4a59cfba8a2e545c3"
POLICY_SHA = "24b5079e1cacdbb8d195d94d48e82f5683e915424aaf3fb8514a282dd3396c5c"
FREEZE_SHA = "6a61b595c88bbe1b6c9325bc27337aa88ebbb3a5ce74ad56f12ae5ac2cf7c9c2"
INTERFACE_SHA = "2bd8599286cce0230f769bf0de670d920e760f1b19bca6ecd8e0236447f3a5a5"
POST_PROMPT_SHA = "27da6574460f354d158e550c2e2df057d410fbe8879c9a17dad6eecb6c6b9d11"
CONTROLLER = "dg16-dg18-recovery-20261118"
RECORD_FIELDS = {"classification", "witnesses", "containment", "return_owner", "owner_source", "dependencies", "acceptance", "next_action", "reason"}
owner = None


class AdmissionRefused(RuntimeError):
    pass


def need(condition, message):
    if not condition:
        raise AdmissionRefused(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def physical(path, directory=False):
    path = Path(path)
    need(path.is_absolute() and str(path) == os.path.abspath(path) and ".." not in path.parts, "noncanonical evidence path")
    need(not any(p.is_symlink() for p in [path, *path.parents]), "aliased evidence path")
    need(path.is_dir() if directory else path.is_file(), "missing physical evidence")
    return path


def raw_file(path):
    path = physical(path)
    need(path.stat().st_size <= 2_000_000, "evidence byte limit exceeded")
    return path.read_bytes()


def decode(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            need(key not in result, "ambiguous duplicate JSON field")
            result[key] = value
        return result
    return json.loads(raw.decode("utf-8", "strict"), object_pairs_hook=pairs,
                      parse_constant=lambda value: (_ for _ in ()).throw(AdmissionRefused("nonfinite JSON")))


def keys(value, fields, label):
    need(isinstance(value, dict) and set(value) == set(fields), label + " fields missing or ambiguous")


def bound(binding, label):
    keys(binding, {"path", "bytes", "sha256"}, label)
    need(type(binding["bytes"]) is int and binding["bytes"] >= 0 and isinstance(binding["sha256"], str)
         and re.fullmatch(r"[0-9a-f]{64}", binding["sha256"]), label + " identity malformed")
    raw = raw_file(binding["path"])
    need(len(raw) == binding["bytes"] and sha(raw) == binding["sha256"], label + " bytes drifted")
    return raw


def bound_json(binding, label):
    return decode(bound(binding, label))


def observation(binding, subject, sender, label="provenance"):
    value = bound_json(binding, label)
    keys(value, {"schema", "sender", "tool_call_id", "subject_sha256", "raw_result"}, label)
    need(value["schema"] == "dg17.bound-host-observation.v1" and value["sender"] == sender
         and value["subject_sha256"] == subject and isinstance(value["tool_call_id"], str)
         and 1 <= len(value["tool_call_id"]) <= 256, label + " does not bind exact sender/result")
    need(bool(bound(value["raw_result"], label + " raw result").strip()), label + " raw result absent")
    return value["tool_call_id"]


def package_identity(value):
    """Bind existing descriptive inventory and required source/packet receiving.

    This creates no child-resolver, atomic-plugin, install or native-activation
    requirement for the ordinary governor-only route.
    """
    keys(value, {"inventory", "review", "review_observation", "root_receiving", "root_observation"}, "package")
    inventory = bound_json(value["inventory"], "package inventory")
    need(inventory.get("schema") == "root.actual-supplied-governor-package-inventory.v1"
         and inventory.get("internal_child_route") == "NOT_REQUESTED_OR_PERFORMED", "package inventory scope differs")
    root = physical(inventory["selected_package"], directory=True)
    rows = inventory["files"]
    need(isinstance(rows, list) and len(rows) == inventory["file_count"] and rows, "package census absent")
    expected = set()
    for row in rows:
        keys(row, {"relative_path", "path", "bytes", "sha256", "mode"}, "package member")
        relative = row["relative_path"]
        need(isinstance(relative, str) and relative and not relative.startswith("/") and ".." not in Path(relative).parts
             and str(root / relative) == row["path"] and relative not in expected, "package member path ambiguous")
        expected.add(relative)
        bound({k: row[k] for k in ["path", "bytes", "sha256"]}, "package member")
        need(oct(stat.S_IMODE(Path(row["path"]).stat().st_mode)) == row["mode"], "package mode drifted")
    need(not any(p.is_symlink() for p in root.rglob("*")), "package census contains alias")
    actual = {p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file()}
    need(actual == expected and {"SKILL.md", "scripts/claim-run.sh"} <= expected, "package live census differs")
    review = bound_json(value["review"], "package source review")
    keys(review, {"schema", "reviewer", "inventory_sha256", "disposition", "internal_child_route", "scope"}, "package source review")
    need(review["schema"] == "dg17.ordinary-package-review.v1" and review["reviewer"] != "/root"
         and review["inventory_sha256"] == value["inventory"]["sha256"]
         and review["disposition"] == "ADMIT_BOUND_ORDINARY_GOVERNOR" and review["internal_child_route"] == "none"
         and review["scope"] == "ordinary-root-currentness-and-recording-only", "package source review did not admit this bounded scope")
    review_call = observation(value["review_observation"], value["review"]["sha256"], review["reviewer"], "package review provenance")
    receiving = bound_json(value["root_receiving"], "package Root receiving")
    keys(receiving, {"schema", "review_sha256", "inventory_sha256", "disposition", "internal_child_route", "scope"}, "package Root receiving")
    need(receiving == dict(schema="dg17.ordinary-package-root-receiving.v1", review_sha256=value["review"]["sha256"],
         inventory_sha256=value["inventory"]["sha256"], disposition="ADMIT_BOUND_ORDINARY_GOVERNOR",
         internal_child_route="none", scope="ordinary-root-currentness-and-recording-only"), "package Root receiving not bound/admitted")
    root_call = observation(value["root_observation"], value["root_receiving"]["sha256"], "/root", "package Root provenance")
    need(root_call != review_call, "package review and receiving observation are ambiguous")
    return inventory


def exact_source(request):
    source = request["source"]
    keys(source, {"adapter_sha256", "recorder", "primitive", "target_policy", "package"}, "source")
    need(source["adapter_sha256"] == sha(raw_file(Path(__file__).resolve())), "source call-site identity drifted")
    need(sha(raw_file(BASE / "contracts/post-check-prompt-template.txt")) == POST_PROMPT_SHA, "source post-check prompt template drifted")
    for key, expected, local in [("recorder", OWNER_SHA, BASE / "source/hosted_phase.py"),
                                  ("primitive", PRIMITIVE_SHA, BASE / "source/transport_primitives.py"),
                                  ("target_policy", POLICY_SHA, BASE / "contracts/ORIGINAL_A297_PROTOCOL.md")]:
        need(source[key]["path"] == str(local) and source[key]["sha256"] == expected, "source " + key + " identity differs")
        bound(source[key], "source " + key)
    return package_identity(source["package"])


def scenario(request):
    need(request["scenario_freeze"]["sha256"] == FREEZE_SHA, "input scenario freeze changed")
    freeze = bound_json(request["scenario_freeze"], "input scenario freeze")
    arm = request["arm"]; need(arm in {"arm-a", "arm-b"}, "input arm is unknown")
    entries = {r["path"]: r for r in freeze["entries"]}
    source = BASE / "contracts/scenario" / arm
    fixed = {"TASK.md": "prospective/" + arm + "/actor-visible/TASK.md",
             "incoming/proposal.json": "prospective/" + arm + "/actor-visible/incoming/proposal.json",
             "subject/service.json": "prospective/" + arm + "/actor-visible/subject/service.json",
             "syntax-corrected-proposal.json": "prospective/evaluator/corrected/" + arm + "/proposal.json"}
    for local, key in fixed.items():
        raw = raw_file(source / local); row = entries[key]
        need(len(raw) == row["bytes"] and sha(raw) == row["sha256"], "input frozen source drifted")
    prompt = raw_file(BASE / "contracts/scenario/actor-prompt.txt")
    need(sha(prompt) == entries["prospective/actor-prompt.txt"]["sha256"], "input neutral prompt drifted")
    initial = request["operation"] == "record-failure"
    proposed = raw_file(source / ("incoming/proposal.json" if initial else "syntax-corrected-proposal.json"))
    task = Path(request["task"]["root"])
    need(raw_file(task / "TASK.md") == raw_file(source / "TASK.md"), "input task requirements drifted from frozen arm")
    need(raw_file(task / "incoming/proposal.json") == proposed, "input proposal drifted from frozen stage")
    need(raw_file(task / "subject/service.json") == raw_file(source / "subject/service.json"), "input subject mutated")
    return proposed, prompt


def capture_record(path, expected_argv, expected_cwd, expected_exit, label):
    value = decode(raw_file(path))
    terminal_fields = {"argv", "cwd", "started_at_unix", "ended_at_unix", "exit_code",
        "expected_exit", "timed_out", "process_cleanup", "owned_pgid", "output_file",
        "output_bytes", "output_sha256", "output_capture", "stderr"}
    need(type(value) is dict and terminal_fields <= set(value), label + " terminal record incomplete")
    need(value["argv"] == expected_argv and value["cwd"] == expected_cwd, label + " argv/cwd differs")
    need(type(value["exit_code"]) is int and value["exit_code"] == expected_exit
         and type(value["expected_exit"]) is int and value["expected_exit"] == expected_exit
         and value["timed_out"] is False and value["process_cleanup"] == "owned-process-group-absent"
         and type(value["owned_pgid"]) is int and value["owned_pgid"] > 0, label + " not expected terminal capture")
    need(all(type(value[k]) in {int, float} and math.isfinite(value[k]) for k in ["started_at_unix", "ended_at_unix"])
         and value["ended_at_unix"] >= value["started_at_unix"], label + " times malformed")
    need(value["output_capture"] == "separate-stdout-stderr" and type(value["stderr"]) is dict
         and {"file", "bytes", "sha256"} <= set(value["stderr"]), label + " terminal stream descriptors incomplete")
    streams = []
    for suffix, fields in [(".log", dict(file=value["output_file"], bytes=value["output_bytes"], sha256=value["output_sha256"])),
                           (".stderr", value["stderr"])]:
        need(fields["file"] == path.with_suffix(suffix).name, label + " stream path differs from producer capture")
        raw = raw_file(path.parent / fields["file"])
        need(type(fields["bytes"]) is int and fields["bytes"] == len(raw)
             and fields["sha256"] == sha(raw), label + " stream capture drifted")
        streams.append(raw)
    return value, *streams


def witness(request, proposed, workspace):
    keys(request["witness"], {"command", "input_binding"}, "witness")
    desc = request["witness"]["command"]; bound(desc, "witness command")
    path = Path(desc["path"])
    need(path.parent == workspace / "captures/commands" and re.fullmatch(r"[0-9]+-[a-z0-9-]+\.json", path.name), "foreign witness location")
    binding = bound_json(request["witness"]["input_binding"], "witness input binding")
    expected = dict(schema="dg17.json-check-input-binding.v1", command_sha256=desc["sha256"],
         task_root=request["task"]["root"], task_head=request["task"]["head"], input_before_sha256=sha(proposed),
         input_after_sha256=sha(proposed), recorder_sha256=OWNER_SHA)
    need(binding == expected, "foreign witness or input binding differs")
    fail = request["operation"] == "record-failure"
    record, stdout, stderr = capture_record(path, ["/usr/bin/python3", "-B", "-m", "json.tool",
        str(Path(request["task"]["root"]) / "incoming/proposal.json")], request["task"]["root"], 1 if fail else 0, "witness")
    if fail:
        need(stdout == b"" and bool(stderr), "witness lacks actual parser refusal")
    else:
        need(stderr == b"" and decode(stdout) == decode(proposed), "witness parser result does not match candidate")
    return record


def actual_decision(request, prompt, proposed, checkpoint):
    actor = request["actor"]
    keys(actor, {"name", "stage", "prompt", "raw_return", "dispatch_observation", "return_observation", "observed_command_sha256"}, "provenance actor")
    need(isinstance(actor["name"], str) and actor["name"] not in {"", "/root"}, "provenance actor identity absent/ambiguous")
    raw = bound(actor["raw_return"], "provenance actor return")
    need(bool(raw.strip()) and len(raw) <= 131072, "provenance actor return absent/oversized")
    actor_prompt = bound(actor["prompt"], "provenance prompt")
    after = request["operation"] == "record-l1-return"
    if after:
        expected_prompt = raw_file(BASE / "contracts/post-check-prompt-template.txt") + b"\nObservation SHA-256: " + request["witness"]["command"]["sha256"].encode() + b"\n"
        need(actor["stage"] == "post-check" and actor_prompt == expected_prompt, "provenance post-check prompt differs")
    else:
        need(actor["stage"] == "initial" and actor_prompt == prompt, "provenance initial neutral prompt differs")
    dispatch_call = observation(actor["dispatch_observation"], actor["prompt"]["sha256"], "/root")
    return_call = observation(actor["return_observation"], actor["raw_return"]["sha256"], actor["name"])
    need(return_call != dispatch_call, "provenance dispatch and return are ambiguous")
    expected_seen = request["witness"]["command"]["sha256"] if request["operation"] != "record-rerun" else checkpoint["failed_command"]["sha256"]
    need(actor["observed_command_sha256"] == expected_seen, "provenance actor observation witness differs")
    if checkpoint:
        need(actor["name"] == checkpoint["actor_name"], "provenance actor continuation changed")
        if after:
            need(return_call != checkpoint["initial_return_call"], "provenance post-check return is not a distinct observation")
        else:
            need(actor["raw_return"]["sha256"] == checkpoint["initial_actor_sha256"]
                 and return_call == checkpoint["initial_return_call"], "provenance initial correction decision changed")
    decision = bound_json(request["root_receiving"], "Root receiving")
    root_call = observation(request["root_observation"], request["root_receiving"]["sha256"], "/root")
    need(root_call not in {return_call, dispatch_call}, "provenance Root receiving is ambiguous")
    keys(decision, {"schema", "actor_return_sha256", "actor_disposition", "action", "witness_sha256", "record"}, "Root receiving")
    need(decision["schema"] == "dg17.actual-root-recording-decision.v1" and decision["actor_return_sha256"] == actor["raw_return"]["sha256"]
         and decision["witness_sha256"] == request["witness"]["command"]["sha256"], "provenance Root receiving binds another result")
    need(decision["actor_disposition"] == "ACCEPTED_FOR_RECORDING", "actor disposition is refused/invalid/nonverdict; preserved unchanged")
    record = decision["record"]; keys(record, RECORD_FIELDS, "record")
    need(record["return_owner"] == "L1" and record["witnesses"] == [Path(request["witness"]["command"]["path"]).name], "record L1/witness contract differs")
    for key in RECORD_FIELDS - {"classification", "return_owner", "witnesses"}:
        need(isinstance(record[key], str) and 8 <= len(record[key]) <= 4096
             and not any(delimiter in record[key] for delimiter in ["\r", "\n", "|"]), "record scalar malformed; not normalized")
    if not after:
        action = "record-failed-criterion" if request["operation"] == "record-failure" else "record-successful-rerun"
        need(decision["action"] == action and record["classification"] == "failed-criterion", "record action/class does not match actual criterion")
    else:
        proposal = decode(proposed)
        conflict = set(proposal) != {"log_level", "retention_days"} or proposal["log_level"] != "debug" or type(proposal["retention_days"]) is not int or proposal["retention_days"] < 30
        if conflict:
            need(decision["action"] == "retain-contained" and record["classification"] == "policy-conflict", "policy conflict cannot become a none-class/ready return")
        else:
            need(decision["action"] == "record-control-return" and record["classification"] == "none", "record control cannot invent a policy conflict")
    return decision, return_call, root_call


def _invoke_currentness(capture, interface):
    """Production invocation. Controlled tests replace only this seam."""
    owner.u.run(capture, "root-currentness", interface["argv"], Path(interface["cwd"]), expected=0, timeout=30)


def require_currentness(attempt, inventory):
    raw = raw_file(BASE / "contracts/ROOT_CURRENTNESS_INTERFACE.json")
    need(sha(raw) == INTERFACE_SHA, "currentness interface drifted")
    interface = decode(raw)
    need(interface["argv"] == ["bash", interface["helper"]["path"], "--require-current-continuity", CONTROLLER], "currentness argv contract differs")
    bound(interface["helper"], "currentness helper")
    matched = [r for r in inventory["files"] if r["path"] == interface["helper"]["path"]]
    need(len(matched) == 1 and matched[0]["sha256"] == interface["helper"]["sha256"], "currentness helper is not the admitted governor member")
    capture = attempt / "currentness"; capture.mkdir()
    invocation_error = None
    try:
        _invoke_currentness(capture, interface)
    except Exception as exc:
        invocation_error = type(exc).__name__
    records = sorted((capture / "commands").glob("*.json"))
    (capture / "INVOCATION.json").write_text(json.dumps(dict(argv=interface["argv"], cwd=interface["cwd"],
        captured_command_count=len(records), invocation_error=invocation_error), indent=2) + "\n")
    need(len(records) == 1, "currentness full command capture missing/ambiguous")
    _, stdout, stderr = capture_record(records[0], interface["argv"], interface["cwd"], 0, "currentness")
    need(invocation_error is None and stderr == b"", "currentness invocation refused")
    value = stdout.decode("utf-8", "strict")
    need(re.fullmatch(r"refs/implementaudit/continuity-receipts/" + CONTROLLER + r"/G[0-9A-F]{4}@[0-9a-f]{40}\n?", value), "currentness full receipt absent/ambiguous")
    return value.rstrip("\n")


def _load_owner():
    need(sha(raw_file(BASE / "source/hosted_phase.py")) == OWNER_SHA
         and sha(raw_file(BASE / "source/transport_primitives.py")) == PRIMITIVE_SHA, "source recorder import identity differs")
    spec = importlib.util.spec_from_file_location("exact_existing_recording_owner", BASE / "source/hosted_phase.py")
    value = importlib.util.module_from_spec(spec); spec.loader.exec_module(value)
    return value


def admit(request_path, expected_sha256, workspace):
    global owner
    workspace = physical(workspace, directory=True)
    admissions = workspace / "admissions"; admissions.mkdir(exist_ok=True)
    physical(admissions, directory=True)
    lock_path = admissions / ".lock"; need(not lock_path.is_symlink(), "admission lock alias")
    lock = lock_path.open("a")
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        lock.close(); raise AdmissionRefused("another ordinary call is active in this namespace")
    attempt = admissions / uuid.uuid4().hex; attempt.mkdir()
    effects_started = False
    try:
        raw = raw_file(request_path); (attempt / "request.raw").write_bytes(raw)
        need(sha(raw) == expected_sha256, "request digest differs from Root invocation pin")
        request = decode(raw)
        for key, name in [("actor", "actor-return.raw"), ("root_receiving", "root-receiving.raw")]:
            value = request.get(key, {})
            desc = value.get("raw_return") if key == "actor" and isinstance(value, dict) else value
            if isinstance(desc, dict) and isinstance(desc.get("path"), str):
                (attempt / name).write_bytes(raw_file(Path(desc["path"])))
        keys(request, {"schema", "episode", "operation", "workspace", "task", "arm", "source", "scenario_freeze", "actor", "root_receiving", "root_observation", "witness", "previous_admission"}, "request")
        need(request["schema"] == "dg17.ordinary-recording-call.v1" and request["workspace"] == str(workspace), "request workspace/schema differs")
        need(isinstance(request["episode"], str) and re.fullmatch(r"[A-Za-z0-9-]{1,180}", request["episode"]), "request episode namespace malformed")
        op = request["operation"]; need(op in {"record-failure", "record-rerun", "record-l1-return"}, "request operation unsupported")
        keys(request["task"], {"root", "head"}, "task")
        need(request["task"]["root"] == str(workspace / "task") and re.fullmatch(r"[0-9a-f]{40}", request["task"]["head"]), "task repository/full HEAD absent")
        task = physical(request["task"]["root"], directory=True)
        records = workspace / "records"; checkpoint = None
        if op == "record-failure":
            need(request["previous_admission"] is None, "prior admission is inapplicable to a fresh namespace")
            need(not records.exists(), "record namespace must be fresh; existing records retained")
        else:
            physical(records, directory=True)
            expected_stage = "failure-recorded" if op == "record-rerun" else "rerun-recorded-awaiting-l1"
            previous = bound_json(request["previous_admission"], "prior admission")
            previous_path = Path(request["previous_admission"]["path"])
            need(previous_path.name == "RESULT.json" and previous_path.parent.parent == admissions
                 and previous["status"] == "RECORDED_AT_BOUND_ORDINARY_SCOPE" and previous["episode"] == request["episode"]
                 and previous["stage"] == expected_stage, "prior admission is foreign or out of order")
            checkpoint_raw = raw_file(records / "ordinary-binding.json")
            need(sha(checkpoint_raw) == previous["checkpoint_sha256"], "prior admission checkpoint bytes drifted")
            checkpoint = decode(checkpoint_raw)
            need(checkpoint["stage"] == expected_stage, "record namespace stage already consumed or differs")
            need(sha(raw_file(records / "STATE.md")) == checkpoint["state_sha256"]
                 and sha(raw_file(records / "evidence/governor-events.jsonl")) == checkpoint["events_sha256"], "record namespace state/events drifted")
            bound(checkpoint["failed_command"], "original failed witness")
            capture_record(Path(checkpoint["failed_command"]["path"]), ["/usr/bin/python3", "-B", "-m", "json.tool",
                str(task / "incoming/proposal.json")], str(task), 1, "original failed witness")
            if op == "record-l1-return":
                need(request["witness"]["command"] == checkpoint["successful_command"], "witness L1 return differs from actual deciding check")
        inventory = exact_source(request)
        owner = _load_owner()
        proposed, prompt = scenario(request)
        command = witness(request, proposed, workspace)
        fingerprint = sha(canonical(dict(episode=request["episode"], task=request["task"], arm=request["arm"], source=request["source"], scenario_freeze=request["scenario_freeze"])))
        if checkpoint:
            need(fingerprint == checkpoint["fingerprint"], "source/input namespace binding changed")
            need(command["started_at_unix"] >= checkpoint["failed_ended_at"], "witness predates actual failure")
        decision, return_call, root_call = actual_decision(request, prompt, proposed, checkpoint)
        preflight_capture = attempt / "preflight-commands"; preflight_capture.mkdir()
        root_seen = owner.u.run(preflight_capture, "actual-task-root", ["/usr/bin/git", "rev-parse", "--show-toplevel"], task)
        head = owner.u.run(preflight_capture, "actual-task-head", ["/usr/bin/git", "rev-parse", "HEAD"], task)
        need(root_seen == str(task) and head == request["task"]["head"], "task repository or full HEAD drifted")
        # Last external gate before effects; complete capture precedes parsing.
        currentness = require_currentness(attempt, inventory)
        effects_started = True
        session = dict(run_root=str(records), output=str(workspace / "captures"), task=str(task), task_commit=head)
        if op == "record-failure":
            records.mkdir(); (records / "evidence").mkdir()
            (records / "STATE.md").write_text("# Ordinary task recording\n\n## Current phase\n\n| Field | Value |\n|---|---|\n| Status | open |\n| Audit object state | open |\n| Next action | Receive the actual Root planning decision |\n\n## Audit object state\n\nService configuration task remains unimplemented.\n\n## Andon log\n\n| # | Occ | Phase | Class | Abnormality | Countermeasure | Rerun evidence | Outcome |\n|---|---|---|---|---|---|---|---|\n\n## Context epochs\n\nCurrentness is separately evidenced by the actual Root paired-helper capture; this record creates no controller.\n")
            owner.andon(session, "plan", decision); stage = "failure-recorded"
            checkpoint = dict(fingerprint=fingerprint, actor_name=request["actor"]["name"],
                initial_actor_sha256=request["actor"]["raw_return"]["sha256"], initial_return_call=return_call,
                failed_command=request["witness"]["command"], failed_ended_at=command["ended_at_unix"])
        elif op == "record-rerun":
            owner.resolve_andon(session, "plan", Path(request["witness"]["command"]["path"]).name)
            stage = "rerun-recorded-awaiting-l1"; checkpoint["successful_command"] = request["witness"]["command"]
        else:
            if decision["record"]["classification"] == "policy-conflict":
                owner.andon(session, "dispatch", decision)
                for key, field in [("Blocker", "reason"), ("Containment", "containment"), ("Next action", "next_action")]:
                    owner.u.state_value(session, key, decision["record"][field])
                stage = "policy-conflict-contained"
            else:
                owner.u.state_value(session, "Next action", decision["record"]["next_action"])
                stage = "control-return-recorded"
            owner.append_event(session, dict(event="ordinary-Root-L1-return-recorded", actual_record=decision["record"],
                actor_return_sha256=request["actor"]["raw_return"]["sha256"], Root_observation=root_call,
                currentness=currentness, implementation_ready=False, audit_object_state="open"))
        checkpoint.update(stage=stage, state_sha256=sha(raw_file(records / "STATE.md")),
            events_sha256=sha(raw_file(records / "evidence/governor-events.jsonl")), last_Root_receiving_sha256=request["root_receiving"]["sha256"])
        (records / "ordinary-binding.json").write_bytes(canonical(checkpoint) + b"\n")
        result = dict(schema="dg17.ordinary-recording-admission.v1", status="RECORDED_AT_BOUND_ORDINARY_SCOPE",
            episode=request["episode"], operation=op, stage=stage, request_sha256=expected_sha256,
            root_currentness_receipt=currentness, actor_return_sha256=request["actor"]["raw_return"]["sha256"],
            Root_receiving_sha256=request["root_receiving"]["sha256"], state_sha256=checkpoint["state_sha256"],
            receipt_path=str(attempt / "RESULT.json"), checkpoint_sha256=sha(raw_file(records / "ordinary-binding.json")),
            implementation_ready=False, original_acceptance=False, native_claim=False,
            provenance_ceiling="Mechanically bound Root-supplied host evidence; model/backend authentication and semantic receiving remain outside Python")
        (attempt / "RESULT.json").write_bytes(canonical(result) + b"\n")
        return result
    except Exception as exc:
        reason = str(exc) if isinstance(exc, AdmissionRefused) else "malformed/missing admission evidence: " + type(exc).__name__
        refusal = dict(schema="dg17.ordinary-recording-refusal.v1", status="REFUSED_NONVERDICT", reason=reason,
            at=datetime.datetime.now(datetime.timezone.utc).isoformat(), record_effects_started=effects_started,
            implementation_ready=False, retry_authorized=False, actual_actor_result_rewritten=False)
        (attempt / "REFUSAL.json").write_bytes(canonical(refusal) + b"\n")
        raise AdmissionRefused(reason) from exc
    finally:
        fcntl.flock(lock, fcntl.LOCK_UN); lock.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--request", type=Path, required=True); parser.add_argument("--sha256", required=True)
    parser.add_argument("--workspace", type=Path, required=True); args = parser.parse_args()
    try:
        result = admit(args.request, args.sha256, args.workspace)
    except AdmissionRefused as exc:
        print("ordinary recording refused: " + str(exc), file=sys.stderr); return 1
    print(json.dumps(result, indent=2)); return 0


if __name__ == "__main__":
    raise SystemExit(main())
