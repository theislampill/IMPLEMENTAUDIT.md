#!/usr/bin/env python3
"""Thin test adapter from exact trust-state bytes to production hostread APIs.

This module may branch on the generic production operation being exercised.
It never branches on a state ID, description, expected value, or scenario.
"""
from __future__ import annotations

import base64
import copy
import json
import os
import tempfile


def _load_relative(data_root, relative):
    path = os.path.join(data_root, *relative.split("/"))
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _materialize(value, data_root):
    value = copy.deepcopy(value)
    if value.get("profile_file"):
        value["profile"] = _load_relative(data_root,
                                           value.pop("profile_file"))
    if value.get("preimages_file"):
        value["preimages"] = _load_relative(
            data_root, value.pop("preimages_file"))
    if "stdout_jsonl" in value:
        value["raw_stdout"] = "\n".join(
            json.dumps(row, sort_keys=True, separators=(",", ":"),
                       ensure_ascii=False)
            for row in value.pop("stdout_jsonl")) + "\n"
    elif "stdout_lines" in value:
        value["raw_stdout"] = "\n".join(value.pop("stdout_lines")) + "\n"
    return value


def _normalize(hostread, host, value):
    if host == "codex":
        return hostread.normalize_codex(
            value["raw_stdout"], profile=value.get("profile"),
            binding=value.get("binding") or {},
            formal=value.get("formal", True))
    if host == "claude":
        return hostread.normalize_claude(
            value["raw_stdout"],
            requested_tools=value.get("requested_tools") or [],
            binding=value.get("binding") or {},
            profile=value.get("profile"),
            formal=value.get("formal", True))
    raise AssertionError(f"unsupported host operation {host!r}")


def _classify_trace(hostread, normalized, value):
    target = value["target"]
    matrix = hostread.classify_actions(
        normalized["actions"], [target], value["preimages"],
        profile=value.get("profile"), formal=value.get("formal", True))
    return {**normalized, "matrix": matrix[target]}


def _adjudicate(hostread, normalized, value):
    result = hostread.adjudicate_path_order(
        normalized, value.get("reads") or [], value["write"],
        value["preimages"], profile=value.get("profile"),
        formal=value.get("formal", True))
    return {**normalized, **result}


def _seal_inputs(hostread, root):
    profile = {
        "schema": "implementaudit-host-read-profile-v2",
        "authority": "test-fixture-only", "host": "codex",
        "repo": {"lexical_root": "/fixture/repo",
                 "real_root": "/fixture/repo", "case_sensitive": True},
        "shell": {"logical_path": "/bin/bash", "realpath": "/usr/bin/bash",
                  "sha256": "a" * 64, "stat": "stable"},
        "outer_wrapper": {"argv_prefix": ["/bin/bash", "-lc"],
                          "max_unwrap_layers": 1},
        "environment": {"PATH": "/usr/bin", "LANG": "C",
                        "LC_ALL": "C", "BASH_ENV": None, "ENV": None,
                        "SHELL": "/bin/bash"},
        "executables": {"cat": {"kind": "file", "path": "/usr/bin/cat",
                                  "sha256": "b" * 64, "stat": "stable"}},
        "probe_sha256": "c" * 64}
    preimages = {
        "schema": "implementaudit-host-read-preimages-v1",
        "repo": profile["repo"],
        "targets": {"STATE.md": {"canonical_path": "/fixture/repo/STATE.md",
                                     "relative_path": "STATE.md",
                                     "content_base64": "U1RBVEUK",
                                     "sha256": "67a6dc4b86440c58cb95dabf079e13cd9758d3268c15ebfad42167af3cf400f5",
                                     "size": 6, "mode": 33188,
                                     "symlink_free": True}}}
    trace = {"schema": "implementaudit-host-tool-trace-v2", "actions": []}
    matrix = {"schema": "implementaudit-host-read-matrix-v1", "targets": {}}
    return hostread.seal_capture(
        root, profile=profile, preimages=preimages,
        raw_stdout=b"stdout\n", raw_session=b"session\n",
        trace=trace, matrix=matrix,
        post_probe={"environment": profile["environment"],
                    "shell": profile["shell"],
                    "executables": profile["executables"]},
        formal=False)


def execute(operation, raw_input, hostread, data_root):
    value = _materialize(raw_input, data_root)
    if operation == "validate-profile":
        return hostread.validate_profile(
            value.get("profile"), post_probe=value.get("post_probe"),
            formal=value.get("formal", True),
            writable_roots=value.get("writable_roots") or [])
    if operation == "validate-preimages":
        return hostread.validate_preimages(value["preimages"])
    if operation == "normalize-codex":
        return _normalize(hostread, "codex", value)
    if operation == "normalize-claude":
        return _normalize(hostread, "claude", value)
    if operation == "normalize-host":
        return _normalize(hostread, value["host"], value)
    if operation == "normalize-classify-codex":
        return _classify_trace(hostread, _normalize(hostread, "codex", value),
                               value)
    if operation == "normalize-classify-claude":
        return _classify_trace(hostread, _normalize(hostread, "claude", value),
                               value)
    if operation == "classify-shell":
        return hostread.classify_shell(
            value["record"], value["target"], value["preimages"],
            profile=value.get("profile"), formal=value.get("formal", True),
            dialect_hint=value.get("dialect"))
    if operation == "classify-shell-multi":
        return {target: hostread.classify_shell(
                    value["record"], target, value["preimages"],
                    profile=value.get("profile"),
                    formal=value.get("formal", True),
                    dialect_hint=value.get("dialect"))
                for target in value["targets"]}
    if operation == "classify-shell-write":
        return hostread.classify_shell_write(
            value["record"], value["write"], value["preimages"],
            profile=value.get("profile"), formal=value.get("formal", True))
    if operation in ("adjudicate-codex", "adjudicate-claude"):
        host = operation.rsplit("-", 1)[1]
        return _adjudicate(hostread, _normalize(hostread, host, value), value)
    if operation == "adjudicate-host":
        return _adjudicate(
            hostread, _normalize(hostread, value["host"], value), value)
    if operation == "replay-capture":
        with tempfile.TemporaryDirectory() as root:
            for relative, text in value["files"].items():
                path = os.path.join(root, relative)
                os.makedirs(os.path.dirname(path), exist_ok=True)
                with open(path, "x", encoding="utf-8") as fh:
                    fh.write(text)
            return hostread.replay_capture(root, formal=False)
    if operation == "seal-and-tamper":
        with tempfile.TemporaryDirectory() as root:
            _seal_inputs(hostread, root)
            path = os.path.join(root, value["tamper"])
            with open(path, "ab") as fh:
                fh.write(b"tamper")
            return hostread.replay_capture(root, formal=False)
    if operation == "snapshot-replay-after-ambient-change":
        with tempfile.TemporaryDirectory() as repo:
            for relative, encoded in value["repo_files"].items():
                path = os.path.join(repo, *relative.split("/"))
                os.makedirs(os.path.dirname(path), exist_ok=True)
                with open(path, "xb") as fh:
                    fh.write(base64.b64decode(encoded))
            snap = hostread.capture_preimages(repo, value["targets"])
            before = hostread.snapshot_digest(snap)
            for relative, encoded in value["ambient_replacement"].items():
                path = os.path.join(repo, *relative.split("/"))
                with open(path, "wb") as fh:
                    fh.write(base64.b64decode(encoded))
            after = hostread.snapshot_digest(snap)
            return {"status": "UNCHANGED" if before == after else "INVALID",
                    "matrix_sha256": "same-as-before" if before == after
                    else "changed"}
    if operation == "verify-rejected-projection":
        return hostread.verify_projection(value)
    raise AssertionError(f"unknown generic operation {operation!r}")
