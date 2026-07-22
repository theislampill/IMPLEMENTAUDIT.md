#!/usr/bin/env python3
"""Focused contract tests for data-neutral staged-campaign mechanics."""
from __future__ import annotations

import copy
import hashlib
import os
import pathlib
import subprocess
import tempfile

import campaign_lifecycle as lifecycle


def rejected(fragment, fn):
    try:
        fn()
    except (OSError, TypeError, ValueError) as exc:
        assert fragment.lower() in str(exc).lower(), str(exc)
    else:
        raise AssertionError(f"unexpectedly accepted; wanted {fragment!r}")


def collect_rejection(label, fragment, fn, accepted):
    try:
        fn()
    except (OSError, TypeError, ValueError) as exc:
        if fragment.lower() not in str(exc).lower():
            raise AssertionError(
                f"{label} rejected for wrong reason: {exc}") from exc
    else:
        accepted.append(label)


def mission(index, campaign="campaign-a"):
    status_identity = {
        "schema": f"{campaign}-attempt-status-v1",
        "campaign": campaign,
        "mission_index": index,
    }
    terminal_identity = {
        "schema": f"{campaign}-attempt-terminal-v1",
        "campaign": campaign,
        "mission_index": index,
    }
    return {
        "attempt": f"attempt-{index:03d}",
        "status_identity": status_identity,
        "terminal_identity": terminal_identity,
        "terminal_state_field": "overall_status",
        "terminal_stop_reason_field": "stop_reason",
        "allowed_attempt": {
            "attempt-status.json": {
                "kind": "json_identity", "identity": status_identity,
            },
            "attempt-terminal.json": {
                "kind": "json_identity", "identity": terminal_identity,
            },
        },
    }


def write_attempt(root, descriptor, state="PASS", stop_reason=None):
    attempt = root / descriptor["attempt"]
    attempt.mkdir()
    lifecycle.write_new_json(
        attempt / "attempt-status.json", descriptor["status_identity"])
    terminal = dict(descriptor["terminal_identity"])
    terminal.update({"overall_status": state, "stop_reason": stop_reason})
    lifecycle.write_new_json(attempt / "attempt-terminal.json", terminal)


def stage(missions, campaign="campaign-a"):
    return {
        "name": "luna",
        "campaign": campaign,
        "schema": f"{campaign}-luna-stage-v1",
        "terminal_name": "luna-stage-terminal.json",
        "missions": missions,
        "stop_states": ["INVALID", "ERROR"],
        "allowed_root": root_policy(campaign),
    }


def binding(mission_count, campaign="campaign-a"):
    return {
        "campaign": campaign,
        "stage": "luna",
        "stage_schema": f"{campaign}-luna-stage-v1",
        "mission_count": mission_count,
        "packet_sha256": "a" * 64,
    }


def root_policy(campaign="campaign-a", *, stage_terminal=None):
    policy = {
        "campaign-manifest.json": {
            "kind": "json_identity",
            "identity": {
                "schema": f"{campaign}-manifest-v1", "campaign": campaign,
            },
        },
    }
    if stage_terminal is not None:
        policy["luna-stage-terminal.json"] = {
            "kind": "exact_bytes", "byte_length": len(stage_terminal),
            "sha256": hashlib.sha256(stage_terminal).hexdigest(),
        }
    return policy


def main():
    rejected("duplicate", lambda: lifecycle.decode_strict_json_bytes(
        b'{"outer":{"x":1,"x":2}}', "duplicate row"))
    for raw in (b'{"x":NaN}', b'{"x":Infinity}', b'{"x":-Infinity}'):
        rejected("non-finite", lambda value=raw:
                 lifecycle.decode_strict_json_bytes(value, "nonfinite row"))
    rejected("utf-8", lambda: lifecycle.decode_strict_json_bytes(
        b"\xff", "invalid row"))

    class IntSubclass(int):
        pass

    class StringSubclass(str):
        pass

    class ListSubclass(list):
        pass

    class DictSubclass(dict):
        pass

    strict_model_failures = []
    strict_cases = [
        ("nested non-string object key", "object key",
         {"binding": {1: "x"}}),
        ("string-key coercion collision", "object key",
         {StringSubclass("1"): "x"}),
        ("tuple array coercion", "array type", ("x",)),
        ("list subclass coercion", "array type", ListSubclass(["x"])),
        ("dict subclass coercion", "object type", DictSubclass({"x": 1})),
        ("integer subclass coercion", "scalar type", IntSubclass(1)),
        ("string subclass coercion", "scalar type", StringSubclass("x")),
    ]
    for label, fragment, value in strict_cases:
        collect_rejection(
            label, fragment,
            lambda candidate=value: lifecycle.canonical_json_bytes(candidate),
            strict_model_failures)
    assert not strict_model_failures, (
        "non-strict JSON values unexpectedly accepted: " +
        ", ".join(strict_model_failures))
    rejected("non-finite", lambda: lifecycle.canonical_json_bytes(
        {"nested": [float("nan")]}))
    lifecycle.canonical_json_bytes({
        "array": [None, True, False, 0, -1, 1.5, "x", {}],
    })

    # RED 1: an identity-bearing root artifact may not be admitted through a
    # name-only policy that leaves its campaign and schema unchecked.
    with tempfile.TemporaryDirectory(prefix="campaign-root-policy-") as tmp:
        root = pathlib.Path(tmp).resolve()
        lifecycle.write_new_json(root / "campaign-manifest.json", {
            "schema": "campaign-b-manifest-v1", "campaign": "campaign-b"})
        rejected("policy", lambda: lifecycle.validate_terminal_prefix(
            root, [], stop_states={"INVALID", "ERROR"},
            allowed_root={"campaign-manifest.json"}))
        rejected("policy kind", lambda: lifecycle.validate_terminal_prefix(
            root, [], stop_states={"INVALID", "ERROR"},
            allowed_root={
                "campaign-manifest.json": {"kind": "deferred_exact_file"},
            }))
        rejected("root policy", lambda: lifecycle.validate_terminal_prefix(
            root, [], stop_states={"INVALID", "ERROR"},
            allowed_root={
                "campaign-manifest.json": {"kind": "custodied_file"},
            }))

    with tempfile.TemporaryDirectory(prefix="campaign-lifecycle-") as tmp:
        root = pathlib.Path(tmp).resolve()
        payload = root / "payload.bin"
        lifecycle.write_new_bytes(payload, b"first")
        assert lifecycle.read_custodied_bytes(
            payload, "payload", root=root) == b"first"
        rejected("exists", lambda: lifecycle.write_new_bytes(payload, b"second"))

        row_path = root / "row.json"
        lifecycle.write_new_json(row_path, {"b": 2, "a": 1})
        assert row_path.read_bytes() == b'{\n "a": 1,\n "b": 2\n}\n'
        assert lifecycle.read_strict_json_bytes(
            row_path, "row", root=root) == {"a": 1, "b": 2}
        rejected("exists", lambda: lifecycle.write_new_json(row_path, {}))

        outside = root.parent / (root.name + "-outside.json")
        outside.write_bytes(b"{}")
        try:
            rejected("escapes", lambda: lifecycle.read_custodied_bytes(
                outside, "outside", root=root))
        finally:
            outside.unlink()

        hardlink = root / "payload-hardlink.bin"
        os.link(payload, hardlink)
        rejected("hardlink", lambda: lifecycle.read_custodied_bytes(
            hardlink, "hardlink", root=root))
        hardlink.unlink()

        link = root / "payload-link.bin"
        try:
            os.symlink(payload, link)
        except (NotImplementedError, OSError) as exc:
            print("LIFECYCLE_FILE_SYMLINK=SKIP:" + type(exc).__name__)
        else:
            rejected("link", lambda: lifecycle.read_custodied_bytes(
                link, "symlink", root=root))
            link.unlink()
            print("LIFECYCLE_FILE_SYMLINK=PASS")

        safe = root / "safe"
        safe.mkdir()
        nested = safe / "nested.json"
        lifecycle.write_new_json(nested, {"ok": True})
        if os.name == "nt":
            junction = root / "safe-junction"
            made = subprocess.run(
                ["cmd", "/c", "mklink", "/J", str(junction), str(safe)],
                capture_output=True, text=True)
            if made.returncode:
                print("LIFECYCLE_DIRECTORY_JUNCTION=SKIP:mklink")
            else:
                rejected("link", lambda: lifecycle.read_custodied_bytes(
                    junction / "nested.json", "junction", root=root))
                os.rmdir(junction)
                print("LIFECYCLE_DIRECTORY_JUNCTION=PASS")

    with tempfile.TemporaryDirectory(prefix="campaign-prefix-") as tmp:
        root = pathlib.Path(tmp).resolve()
        lifecycle.write_new_json(root / "campaign-manifest.json", {
            "schema": "campaign-a-manifest-v1", "campaign": "campaign-a"})
        missions = [mission(0), mission(1)]
        assert lifecycle.validate_terminal_prefix(
            root, missions, stop_states={"INVALID", "ERROR"},
            allowed_root=root_policy()) == []
        write_attempt(root, missions[0])
        prefix = lifecycle.validate_terminal_prefix(
            root, missions, stop_states={"INVALID", "ERROR"},
            allowed_root=root_policy())
        assert [row["terminal"]["mission_index"] for row in prefix] == [0]

        claiming = root / "attempt-001.claiming"
        claiming.mkdir()
        rejected("claim", lambda: lifecycle.validate_terminal_prefix(
            root, missions, stop_states={"INVALID", "ERROR"},
            allowed_root=root_policy()))
        claiming.rmdir()

        write_attempt(root, missions[1])
        prefix = lifecycle.validate_terminal_prefix(
            root, missions, stop_states={"INVALID", "ERROR"},
            allowed_root=root_policy())
        assert len(prefix) == 2
        duplicate_missions = [missions[0], copy.deepcopy(missions[0])]
        rejected("duplicate", lambda: lifecycle.validate_terminal_prefix(
            root, duplicate_missions, stop_states={"INVALID", "ERROR"},
            allowed_root=root_policy()))
        rejected("campaign", lambda: lifecycle.validate_terminal_prefix(
            root, [mission(0, "campaign-b"), mission(1, "campaign-b")],
            stop_states={"INVALID", "ERROR"},
            allowed_root=root_policy("campaign-b")))

        with tempfile.TemporaryDirectory(prefix="campaign-early-") as early_tmp:
            early_root = pathlib.Path(early_tmp).resolve()
            lifecycle.write_new_json(early_root / "campaign-manifest.json", {
                "schema": "campaign-a-manifest-v1", "campaign": "campaign-a"})
            write_attempt(early_root, missions[0])
            rejected("prefix", lambda: lifecycle.write_stage_terminal(
                early_root, stage(missions), binding(2)))

        for supplied_digest in (None, "0" * 64):
            with tempfile.TemporaryDirectory(
                    prefix="campaign-caller-prefix-") as caller_tmp:
                caller_root = pathlib.Path(caller_tmp).resolve()
                lifecycle.write_new_json(
                    caller_root / "campaign-manifest.json", {
                        "schema": "campaign-a-manifest-v1",
                        "campaign": "campaign-a",
                    })
                caller_missions = [mission(0)]
                write_attempt(caller_root, caller_missions[0])
                caller_binding = binding(1)
                caller_binding["prefix_sha256"] = supplied_digest
                rejected("internal derivation", lambda:
                         lifecycle.write_stage_terminal(
                             caller_root, stage(caller_missions),
                             caller_binding))

        with tempfile.TemporaryDirectory(
                prefix="campaign-binding-json-model-") as binding_tmp:
            binding_root = pathlib.Path(binding_tmp).resolve()
            lifecycle.write_new_json(
                binding_root / "campaign-manifest.json", {
                    "schema": "campaign-a-manifest-v1",
                    "campaign": "campaign-a",
                })
            binding_missions = [mission(0)]
            write_attempt(binding_root, binding_missions[0])
            non_string_binding = binding(1)
            non_string_binding["nested"] = {1: "x"}
            rejected("object key", lambda: lifecycle.write_stage_terminal(
                binding_root, stage(binding_missions), non_string_binding))

        terminal_path = lifecycle.write_stage_terminal(
            root, stage(missions), binding(2))
        terminal_bytes = terminal_path.read_bytes()
        resumed = lifecycle.validate_stage_resume(
            root, stage(missions), binding(2))
        assert resumed["binding_sha256"] == hashlib.sha256(
            lifecycle.canonical_json_bytes(binding(2))).hexdigest()
        assert (len(resumed["stage_snapshot_sha256"]) == 64 and
                resumed["stage_snapshot_sha256"] != "0" * 64)
        rejected("exists", lambda: lifecycle.write_stage_terminal(
            root, stage(missions), binding(2)))
        assert terminal_path.read_bytes() == terminal_bytes

        stage_contract_failures = []
        changed_root_policy_stage = stage(missions)
        changed_root_policy_stage["allowed_root"][
            "campaign-manifest.json"]["identity"] = {
                "campaign": "campaign-a"}
        collect_rejection(
            "changed allowed_root policy", "stage snapshot",
            lambda: lifecycle.validate_stage_resume(
                root, changed_root_policy_stage, binding(2)),
            stage_contract_failures)

        changed_stop_stage = stage(missions)
        changed_stop_stage["stop_states"] = ["INVALID", "ERROR", "FAIL"]
        collect_rejection(
            "changed stop_states", "stage snapshot",
            lambda: lifecycle.validate_stage_resume(
                root, changed_stop_stage, binding(2)),
            stage_contract_failures)

        manifest_path = root / "campaign-manifest.json"
        manifest_bytes = manifest_path.read_bytes()
        changed_manifest = lifecycle.decode_strict_json_bytes(
            manifest_bytes, "changed manifest", require_object=True)
        changed_manifest["non_identity_note"] = "changed after pause"
        manifest_path.write_bytes(lifecycle.canonical_json_bytes(changed_manifest))
        collect_rejection(
            "changed root artifact bytes", "stage snapshot",
            lambda: lifecycle.validate_stage_resume(
                root, stage(missions), binding(2)),
            stage_contract_failures)
        manifest_path.write_bytes(manifest_bytes)
        assert not stage_contract_failures, (
            "stage contract drift unexpectedly accepted: " +
            ", ".join(stage_contract_failures))

        drift_failures = []
        second_terminal_path = (
            root / missions[1]["attempt"] / "attempt-terminal.json")
        second_terminal_bytes = second_terminal_path.read_bytes()
        drifted_terminal = lifecycle.decode_strict_json_bytes(
            second_terminal_bytes, "drifted terminal", require_object=True)
        drifted_terminal["post_pause_note"] = "changed bytes, same identity"
        second_terminal_path.write_bytes(
            lifecycle.canonical_json_bytes(drifted_terminal))
        collect_rejection(
            "post-pause terminal-byte drift", "stage snapshot",
            lambda: lifecycle.validate_stage_resume(
                root, stage(missions), binding(2)),
            drift_failures)
        second_terminal_path.write_bytes(second_terminal_bytes)

        changed_missions = copy.deepcopy(missions)
        changed_missions[0]["allowed_attempt"]["optional-evidence.bin"] = {
            "kind": "custodied_file"}
        collect_rejection(
            "changed descriptor at same mission count", "stage snapshot",
            lambda: lifecycle.validate_stage_resume(
                root, stage(changed_missions), binding(2)),
            drift_failures)
        assert not drift_failures, (
            "stage prefix drift unexpectedly accepted: " +
            ", ".join(drift_failures))

        wrong_binding = binding(2)
        wrong_binding["packet_sha256"] = "c" * 64
        rejected("hash", lambda: lifecycle.validate_stage_resume(
            root, stage(missions), wrong_binding))
        rejected("campaign", lambda: lifecycle.validate_stage_resume(
            root, stage(missions, campaign="campaign-b"),
            binding(2, campaign="campaign-b")))

        extra = mission(2)
        write_attempt(root, extra)
        rejected("unexpected", lambda: lifecycle.validate_terminal_prefix(
            root, missions, stop_states={"INVALID", "ERROR"},
            allowed_root=root_policy(stage_terminal=terminal_bytes)))

    # RED 2a: every declared attempt artifact needs custody validation, not
    # only membership in an allowed-name set.
    with tempfile.TemporaryDirectory(prefix="campaign-attempt-hardlink-") as tmp:
        root = pathlib.Path(tmp).resolve()
        lifecycle.write_new_json(root / "campaign-manifest.json", {
            "schema": "campaign-a-manifest-v1", "campaign": "campaign-a"})
        descriptor = mission(0)
        descriptor["allowed_attempt"]["retained-evidence.bin"] = {
            "kind": "custodied_file"}
        write_attempt(root, descriptor)
        with tempfile.TemporaryDirectory(
                prefix="campaign-attempt-hardlink-source-") as source_tmp:
            source = pathlib.Path(source_tmp).resolve() / "source.bin"
            source.write_bytes(b"retained")
            os.link(source, root / descriptor["attempt"] /
                    "retained-evidence.bin")
            rejected("hardlink", lambda: lifecycle.validate_terminal_prefix(
                root, [descriptor], stop_states={"INVALID", "ERROR"},
                allowed_root=root_policy()))

    with tempfile.TemporaryDirectory(prefix="campaign-attempt-file-link-") as tmp:
        root = pathlib.Path(tmp).resolve()
        lifecycle.write_new_json(root / "campaign-manifest.json", {
            "schema": "campaign-a-manifest-v1", "campaign": "campaign-a"})
        descriptor = mission(0)
        descriptor["allowed_attempt"]["retained-evidence.bin"] = {
            "kind": "custodied_file"}
        write_attempt(root, descriptor)
        attempt = root / descriptor["attempt"]
        with tempfile.TemporaryDirectory(
                prefix="campaign-attempt-file-link-source-") as source_tmp:
            source = pathlib.Path(source_tmp).resolve() / "source.bin"
            lifecycle.write_new_bytes(source, b"retained")
            link = attempt / "retained-evidence.bin"
            try:
                os.symlink(source, link)
            except (NotImplementedError, OSError) as exc:
                print("LIFECYCLE_ATTEMPT_FILE_SYMLINK=SKIP:" +
                      type(exc).__name__)
            else:
                rejected("link", lambda: lifecycle.validate_terminal_prefix(
                    root, [descriptor], stop_states={"INVALID", "ERROR"},
                    allowed_root=root_policy()))
                link.unlink()
                print("LIFECYCLE_ATTEMPT_FILE_SYMLINK=PASS")

    with tempfile.TemporaryDirectory(prefix="campaign-attempt-parent-link-") as tmp:
        root = pathlib.Path(tmp).resolve()
        lifecycle.write_new_json(root / "campaign-manifest.json", {
            "schema": "campaign-a-manifest-v1", "campaign": "campaign-a"})
        descriptor = mission(0)
        with tempfile.TemporaryDirectory(
                prefix="campaign-attempt-parent-target-") as target_tmp:
            target_root = pathlib.Path(target_tmp).resolve()
            write_attempt(target_root, descriptor)
            attempt_alias = root / descriptor["attempt"]
            try:
                os.symlink(target_root / descriptor["attempt"], attempt_alias,
                           target_is_directory=True)
            except (NotImplementedError, OSError) as exc:
                print("LIFECYCLE_ATTEMPT_PARENT_SYMLINK=SKIP:" +
                      type(exc).__name__)
            else:
                rejected("link", lambda: lifecycle.validate_terminal_prefix(
                    root, [descriptor], stop_states={"INVALID", "ERROR"},
                    allowed_root=root_policy()))
                attempt_alias.unlink()
                print("LIFECYCLE_ATTEMPT_PARENT_SYMLINK=PASS")

            if os.name == "nt":
                made = subprocess.run(
                    ["cmd", "/c", "mklink", "/J", str(attempt_alias),
                     str(target_root / descriptor["attempt"])],
                    capture_output=True, text=True)
                if made.returncode:
                    print("LIFECYCLE_ATTEMPT_PARENT_JUNCTION=SKIP:mklink")
                else:
                    rejected("link", lambda:
                             lifecycle.validate_terminal_prefix(
                                 root, [descriptor],
                                 stop_states={"INVALID", "ERROR"},
                                 allowed_root=root_policy()))
                    os.rmdir(attempt_alias)
                    print("LIFECYCLE_ATTEMPT_PARENT_JUNCTION=PASS")

    with tempfile.TemporaryDirectory(prefix="campaign-gap-") as tmp:
        root = pathlib.Path(tmp).resolve()
        lifecycle.write_new_json(root / "campaign-manifest.json", {
            "schema": "campaign-a-manifest-v1", "campaign": "campaign-a"})
        missions = [mission(0), mission(1)]
        write_attempt(root, missions[1])
        rejected("gap", lambda: lifecycle.validate_terminal_prefix(
            root, missions, stop_states={"INVALID", "ERROR"},
            allowed_root=root_policy()))

    # RED 3: distinct directory names cannot represent the same semantic
    # mission identity.
    with tempfile.TemporaryDirectory(prefix="campaign-semantic-duplicate-") as tmp:
        root = pathlib.Path(tmp).resolve()
        lifecycle.write_new_json(root / "campaign-manifest.json", {
            "schema": "campaign-a-manifest-v1", "campaign": "campaign-a"})
        first = mission(0)
        duplicate = copy.deepcopy(first)
        duplicate["attempt"] = "attempt-001"
        write_attempt(root, first)
        write_attempt(root, duplicate)
        rejected("semantic", lambda: lifecycle.validate_terminal_prefix(
            root, [first, duplicate], stop_states={"INVALID", "ERROR"},
            allowed_root=root_policy()))

    with tempfile.TemporaryDirectory(prefix="campaign-stop-") as tmp:
        root = pathlib.Path(tmp).resolve()
        lifecycle.write_new_json(root / "campaign-manifest.json", {
            "schema": "campaign-a-manifest-v1", "campaign": "campaign-a"})
        missions = [mission(0), mission(1)]
        write_attempt(root, missions[0], "INVALID", "identity-drift")
        write_attempt(root, missions[1])
        rejected("after terminal stop", lambda:
                 lifecycle.validate_terminal_prefix(
                     root, missions, stop_states={"INVALID", "ERROR"},
                     allowed_root=root_policy()))

    with tempfile.TemporaryDirectory(prefix="campaign-resume-") as tmp:
        root = pathlib.Path(tmp).resolve()
        lifecycle.write_new_json(root / "campaign-manifest.json", {
            "schema": "campaign-a-manifest-v1", "campaign": "campaign-a"})
        missions = [mission(0)]
        write_attempt(root, missions[0])
        rejected("missing", lambda: lifecycle.validate_stage_resume(
            root, stage(missions), binding(1)))

    with tempfile.TemporaryDirectory(prefix="campaign-stage-identity-") as tmp:
        root = pathlib.Path(tmp).resolve()
        lifecycle.write_new_json(root / "campaign-manifest.json", {
            "schema": "campaign-a-manifest-v1", "campaign": "campaign-a"})
        foreign_missions = [mission(0, "campaign-b")]
        write_attempt(root, foreign_missions[0])
        rejected("mission campaign identity", lambda:
                 lifecycle.write_stage_terminal(
                     root, stage(foreign_missions, campaign="campaign-a"),
                     binding(1, campaign="campaign-a")))

    print("test_campaign_lifecycle: ok")


if __name__ == "__main__":
    main()
