#!/usr/bin/env python3
"""Append-only diagnostic replay of the immutable B3-v3 host streams.

This is not a campaign scorer.  It preserves the accepted rejected-policy
projection and separately asks whether the historical evidence is eligible
under the corrected formal-v2 custody contract.  It never writes inside an
input run root and refuses to reuse an output directory.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone


HERE = os.path.dirname(os.path.abspath(__file__))
LIB = os.path.join(HERE, "lib")
if LIB not in sys.path:
    sys.path.insert(0, LIB)
import hostread  # noqa: E402


RUN_RE = re.compile(
    r"^b3v3-sol-r1-(?P<ordinal>\d{3})-B3v3-(?P<config>[LO])-"
    r"(?P<arm>candidate|control)-r(?P<rep>[123])$")
READS = (
    ".IMPLEMENTAUDIT/runs/audit-closure-a7Kx2f/STATE.md",
    ".IMPLEMENTAUDIT/runs/audit-closure-a7Kx2f/ROADMAP.md",
)
WRITE = ".IMPLEMENTAUDIT/runs/audit-closure-a7Kx2f/continuity-capsule.json"
FORMAL_REQUIRED = (
    "host-read-profile.json",
    "host-read-preimages.json",
    "host-read-fixture.raw",
    "host-read-replay-spec.json",
    "host-read-pre-spawn.json",
    "host-stdout.raw",
    "host-session.raw",
    "host-tool-trace.json",
    "host-read-matrix.json",
    "host-read-post-probe.json",
    "host-read-terminal.json",
    "host-read-manifest.json",
)


def _emit(value):
    sys.stdout.write(str(value) + "\n")


def _sha(data):
    return hashlib.sha256(data).hexdigest()


def _read(path):
    with open(path, "rb") as fh:
        return fh.read()


def _json(path):
    return json.loads(_read(path).decode("utf-8"))


def _write_new_json(path, value):
    data = (json.dumps(value, indent=2, sort_keys=True,
                       ensure_ascii=False) + "\n").encode("utf-8")
    with open(path, "xb") as fh:
        fh.write(data)
    return _sha(data)


def _snapshot_inputs(private_root, runs, seed_root, policy_path):
    roots = [(run, os.path.join(private_root, run)) for run in runs]
    roots.append(("source-fixture", seed_root))
    roots.append(("rejected-policy", policy_path))
    records = []
    for label, root in roots:
        if os.path.isfile(root):
            data = _read(root)
            records.append({"path": label, "size": len(data),
                            "sha256": _sha(data)})
            continue
        for current, dirs, files in os.walk(root, followlinks=False):
            dirs.sort()
            files.sort()
            for name in files:
                path = os.path.join(current, name)
                data = _read(path)
                rel = os.path.relpath(path, root).replace("\\", "/")
                records.append({"path": f"{label}/{rel}",
                                "size": len(data), "sha256": _sha(data)})
    return records


def _load_rejected_projection(policy_path):
    batches = _json(policy_path)
    case = next((entry for entry in batches if entry.get("id") == "O01"),
                None)
    if case is None:
        raise ValueError("O01 rejected-policy fixture missing")
    rows = case.get("input", {}).get("rows", [])
    if len(rows) != 12:
        raise ValueError("O01 must preserve exactly 12 historical runs")
    return {row["run"]: row for row in rows}


def _repo_root(private_root, run, adapter_name):
    native = os.path.join(private_root, "work", run, "fixture-repo-B3-v3")
    text = native.replace("\\", "/")
    if adapter_name == "codex-cli":
        match = re.match(r"^([A-Za-z]):/(.*)$", text)
        if not match:
            raise ValueError("Codex replay expects a drive-rooted private path")
        return f"/mnt/{match.group(1).lower()}/{match.group(2)}"
    return text


def _posthoc_preimages(seed_root, repo_root):
    """Build an explicitly unbound diagnostic view from immutable seed bytes."""
    targets = {}
    for relative in READS:
        source = os.path.join(seed_root, *relative.split("/"))
        data = _read(source)
        targets[relative] = {
            "canonical_path": repo_root.rstrip("/") + "/" + relative,
            "relative_path": relative,
            "content_base64": base64.b64encode(data).decode("ascii"),
            "sha256": _sha(data), "size": len(data),
            "mode": 0o100644, "symlink_free": True,
        }
    return {"schema": hostread.PREIMAGE_SCHEMA,
            "repo": {"lexical_root": repo_root, "real_root": repo_root,
                     "case_sensitive": not re.match(r"^[A-Za-z]:/", repo_root)},
            "targets": targets}


def _output_fingerprint(action):
    output = action.get("output")
    if not isinstance(output, str):
        return None
    data = output.encode("utf-8")
    return {"size": len(data), "sha256": _sha(data)}


def _write_disposition(action, preimages):
    if action.get("effect") == "write":
        paths = ([action.get("path")] if isinstance(action.get("path"), str)
                 else list(action.get("paths") or []))
        matches = any(hostread._equivalent_path(path, WRITE, preimages)
                      for path in paths if isinstance(path, str))
        if not matches:
            return {"classification": "not-target-write",
                    "write_state": "NOT_APPLICABLE"}
        complete = action.get("state") == "COMPLETED"
        return {"classification": ("write-observed" if complete
                                    else "fail-closed"),
                "write_state": "COMPLETED" if complete else "INCOMPLETE"}
    if action.get("effect") == "command":
        return hostread.classify_shell_write(
            {"command": action.get("command"),
             "output": action.get("output"),
             "exit_code": action.get("exit_code")},
            WRITE, preimages, profile=None, formal=True)
    return {"classification": "not-target-write",
            "write_state": "NOT_APPLICABLE"}


def _action_record(action, preimages, profile=None, formal=True):
    keep = ("id", "state", "effect", "action_type",
            "invocation_ordinal", "completion_ordinal", "command",
            "path", "paths", "exit_code", "reason", "classification")
    result = {key: action[key] for key in keep if key in action}
    result["output"] = _output_fingerprint(action)
    result["read_dispositions"] = {
        target: hostread.classify_actions(
            [action], [target], preimages, profile=profile,
            formal=formal)[target]
        for target in READS
    }
    result["write_disposition"] = _write_disposition(action, preimages)
    return result


def _formal_missing(run_root, adapter_name, has_native_session):
    missing = [name for name in FORMAL_REQUIRED
               if not os.path.isfile(os.path.join(run_root, name))]
    reasons = ["missing-pre-spawn-formal-profile",
               "missing-bound-preimages",
               "missing-bound-fixture-bytes",
               "missing-replay-recipe",
               "missing-pre-spawn-parent-record",
               "process-started-does-not-bind-host-read-parent",
               "missing-post-mission-formal-custody-manifest"]
    if not has_native_session:
        reasons.append("distinct-native-session-stream-not-retained")
    elif adapter_name == "codex-cli":
        reasons.append("retained-native-session-not-prebound-by-formal-manifest")
    return missing, reasons


def _replay_one(private_root, run, rejected, seed_root):
    match = RUN_RE.fullmatch(run)
    if not match:
        raise ValueError(f"unexpected run identity {run!r}")
    root = os.path.join(private_root, run)
    intent = _json(os.path.join(root, "run-intent.json"))
    adapter = intent.get("adapter_name")
    if adapter not in ("codex-cli", "claude-cli"):
        raise ValueError(f"{run}: unsupported adapter {adapter!r}")
    root_stdout = _read(os.path.join(root, "host-stdout.raw"))
    bundle_stdout = _read(os.path.join(
        root, "bundle", "artifacts", "host-stdout.raw"))
    if root_stdout != bundle_stdout:
        raise ValueError(f"{run}: root/bundle stdout mismatch")
    if _sha(root_stdout) != rejected["raw_sha256"]:
        raise ValueError(f"{run}: stdout differs from frozen O01 identity")
    session_path = os.path.join(
        root, "bundle", "artifacts", "raw-host-events.jsonl")
    raw_session = _read(session_path) if os.path.isfile(session_path) else None
    text = root_stdout.decode("utf-8")
    requested = str(intent.get("policy_requested", {}).get("tools", "")).split()
    repo_root = _repo_root(private_root, run, adapter)
    preimages = _posthoc_preimages(seed_root, repo_root)
    if adapter == "codex-cli":
        binding = hostread.derive_codex_binding(text)
        if binding and raw_session is not None:
            binding = hostread.augment_codex_binding(binding, raw_session)
        normalized = hostread.normalize_codex(
            text, profile=None, binding=binding or {}, formal=True)
        host = "codex"
        profile_state = "missing formal profile"
        diagnostic_profile = None
        diagnostic_formal = True
    else:
        # Claude's native-tool profile contains no ambient executable facts.
        # Reconstruct its retained repository/tool shape for diagnostic-only
        # property extraction, while labeling it test-only and unbound so it
        # can never become formal qualification evidence.
        diagnostic_profile = hostread.mint_claude_profile(repo_root, requested)
        diagnostic_profile["authority"] = "test-fixture-only"
        diagnostic_profile["diagnostic_origin"] = "posthoc-unbound"
        binding = hostread.derive_claude_binding(text)
        normalized = hostread.normalize_claude(
            text, requested_tools=requested, binding=binding or {},
            profile=diagnostic_profile, formal=False)
        host = "claude"
        profile_state = ("post-hoc repository/tool reconstruction; "
                         "no frozen formal profile")
        diagnostic_formal = False
    property_projection = hostread.adjudicate_path_order(
        normalized, READS, WRITE, preimages, profile=diagnostic_profile,
        formal=diagnostic_formal)
    actions = [_action_record(action, preimages,
                              profile=diagnostic_profile,
                              formal=diagnostic_formal)
               for action in normalized.get("actions", [])]
    missing, reasons = _formal_missing(
        root, adapter, raw_session is not None)
    return {
        "schema": "implementaudit-b3v3-host-read-diagnostic-v1",
        "run": {"id": run, "ordinal": match.group("ordinal"),
                "host": host, "config": match.group("config"),
                "arm": match.group("arm"), "repetition":
                int(match.group("rep"))},
        "raw_evidence": {
            "root_stdout": {"sha256": _sha(root_stdout),
                            "size": len(root_stdout)},
            "bundle_stdout": {"sha256": _sha(bundle_stdout),
                              "size": len(bundle_stdout)},
            "native_session": ({"sha256": _sha(raw_session),
                                "size": len(raw_session)}
                               if raw_session is not None else None),
        },
        "rejected_policy_projection": {
            "source": "frozen O01 accepted omission-review fixture",
            "profile_state": profile_state,
            "disposition": rejected["disposition"],
            "is_campaign_score": False,
        },
        "corrected_normalization_diagnostic": {
            "binding": binding,
            "requested_tools": normalized.get("requested_tools", []),
            "actual_tools": normalized.get("observed_tools", []),
            "normalizer_host_status": normalized.get("host_status"),
            "host_findings": normalized.get("host_findings", []),
            "actions": actions,
            "posthoc_unbound_property_projection": property_projection,
            "preimage_source": "immutable fixture seed, post-hoc and unbound",
        },
        "formal_v2_eligibility": {
            "eligible": False, "host_status": "INVALID",
            "overall_disposition": "INVALID",
            "missing_capture_files": missing,
            "reasons": reasons,
            "property_facts_retained_but_not_qualification_evidence": True,
            "replacement_campaign_score": None,
        },
    }


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--private-root", required=True)
    parser.add_argument("--output-root", required=True)
    args = parser.parse_args(argv)
    private_root = os.path.abspath(args.private_root)
    output_root = os.path.abspath(args.output_root)
    if os.path.commonpath((private_root, output_root)) != private_root:
        raise SystemExit("output must be an append-only child of private root")
    runs = sorted(name for name in os.listdir(private_root)
                  if RUN_RE.fullmatch(name))
    if len(runs) != 12:
        raise SystemExit(f"expected 12 B3-v3 roots, found {len(runs)}")
    policy_path = os.path.join(HERE, "testdata", "host-read-trust", "O.json")
    seed_root = os.path.join(private_root, "harness-b3v3-sol", "eval",
                             "fixtures", "B3-v3", "seed")
    rejected = _load_rejected_projection(policy_path)
    if sorted(rejected) != [f"{index:03d}" for index in range(12)]:
        raise SystemExit("frozen O01 run identities are incomplete")
    before = _snapshot_inputs(private_root, runs, seed_root, policy_path)
    os.makedirs(os.path.dirname(output_root), exist_ok=True)
    os.mkdir(output_root)
    created_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    before_hash = _write_new_json(os.path.join(
        output_root, "input-manifest-before.json"), before)
    results = []
    output_hashes = {"input-manifest-before.json": before_hash}
    for run in runs:
        ordinal = RUN_RE.fullmatch(run).group("ordinal")
        result = _replay_one(private_root, run, rejected[ordinal], seed_root)
        name = f"{ordinal}-{run}.json"
        output_hashes[name] = _write_new_json(os.path.join(output_root, name),
                                              result)
        results.append(result)
    after = _snapshot_inputs(private_root, runs, seed_root, policy_path)
    after_hash = _write_new_json(os.path.join(
        output_root, "input-manifest-after.json"), after)
    output_hashes["input-manifest-after.json"] = after_hash
    if before != after:
        raise SystemExit("immutable B3-v3 inputs changed during replay")
    summary = {
        "schema": "implementaudit-b3v3-host-read-diagnostic-summary-v1",
        "created_at": created_at, "runtime_model_identity": "Sol",
        "input_runs": runs, "input_unchanged": True,
        "rejected_policy_projection": {
            "PASS": sum(row["rejected_policy_projection"]["disposition"] ==
                        "PASS" for row in results),
            "INVALID_OR_INCOMPLETE": sum(
                row["rejected_policy_projection"]["disposition"] != "PASS"
                for row in results),
            "is_campaign_score": False,
        },
        "formal_v2_eligibility": {
            "eligible": sum(row["formal_v2_eligibility"]["eligible"]
                            for row in results),
            "ineligible": sum(not row["formal_v2_eligibility"]["eligible"]
                              for row in results),
            "replacement_campaign_score": None,
        },
        "parser_sha256": _sha(_read(hostread.__file__)),
        "replay_script_sha256": _sha(_read(__file__)),
        "policy_fixture_sha256": _sha(_read(policy_path)),
        "per_run": [{"id": row["run"]["id"],
                     "raw_sha256": row["raw_evidence"]["root_stdout"]["sha256"],
                     "rejected": row["rejected_policy_projection"]["disposition"],
                     "formal_v2_eligible": False,
                     "diagnostic_property": row[
                         "corrected_normalization_diagnostic"][
                             "posthoc_unbound_property_projection"][
                                 "property_status"]}
                    for row in results],
    }
    output_hashes["summary.json"] = _write_new_json(
        os.path.join(output_root, "summary.json"), summary)
    output_manifest = {
        "schema": "implementaudit-append-only-diagnostic-manifest-v1",
        "created_at": created_at, "files": output_hashes,
        "input_manifest_equal": True,
    }
    _write_new_json(os.path.join(output_root, "output-manifest.json"),
                    output_manifest)
    _emit(json.dumps({
        "output_root": output_root,
        "rejected_policy": "3 PASS / 9 INVALID-or-incomplete",
        "formal_v2": "0 eligible / 12 ineligible",
        "input_unchanged": True}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
