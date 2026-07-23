#!/usr/bin/env python3
"""Focused contract tests for data-neutral staged-campaign mechanics."""
from __future__ import annotations

import copy
import hashlib
import math
import os
import pathlib
import subprocess
import sys
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


def collect_stable_value_error(label, fragment, fn, failures):
    try:
        fn()
    except ValueError as exc:
        if fragment.lower() not in str(exc).lower():
            failures.append(f"{label} wrong ValueError: {exc}")
    except Exception as exc:
        failures.append(f"{label} leaked {type(exc).__name__}: {exc}")
    else:
        failures.append(f"{label} unexpectedly accepted")


def collect_success(label, fn, failures):
    try:
        fn()
    except Exception as exc:
        failures.append(f"{label} raised {type(exc).__name__}: {exc}")


def nested_model(depth, kind):
    value = 0
    for _ in range(depth):
        value = [value] if kind == "array" else {"child": value}
    return value


def nested_json(depth, kind):
    if kind == "array":
        return b"[" * depth + b"0" + b"]" * depth
    return b'{"child":' * depth + b"0" + b"}" * depth


def campaign_manifest_with_raw_probe(raw_value):
    return (b'{"campaign":"campaign-a","probe":' + raw_value +
            b',"schema":"campaign-a-manifest-v1"}')


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


def write_attempt_without_control(root, descriptor, missing):
    attempt = root / descriptor["attempt"]
    attempt.mkdir()
    lifecycle.write_new_json(
        attempt / "attempt-status.json", descriptor["status_identity"])
    terminal = dict(descriptor["terminal_identity"])
    controls = {"overall_status": "PASS", "stop_reason": None}
    controls.pop(missing)
    terminal.update(controls)
    lifecycle.write_new_json(attempt / "attempt-terminal.json", terminal)


def directory_mission(index=0):
    descriptor = mission(index)
    descriptor["allowed_attempt"]["host-custody"] = {
        "kind": "custodied_directory"}
    return descriptor


def write_directory_tree(attempt, *, reverse=False):
    host = attempt / "host-custody"
    host.mkdir()
    operations = [
        ("directory", "empty", None),
        ("directory", "nested", None),
        ("directory", "nested/deeper", None),
        ("file", "nested/alpha.bin", b"alpha"),
        ("file", "nested/deeper/beta.bin", b"beta"),
        ("file", "top.bin", b"top"),
    ]
    if reverse:
        operations = list(reversed(operations))
    pending = list(operations)
    while pending:
        progressed = False
        for operation in list(pending):
            kind, relative, payload = operation
            path = host / pathlib.PurePosixPath(relative)
            if not path.parent.exists():
                continue
            if kind == "directory":
                path.mkdir()
            else:
                lifecycle.write_new_bytes(path, payload)
            pending.remove(operation)
            progressed = True
        assert progressed, "directory fixture dependency cycle"
    return host


def expected_directory_manifest():
    def leaf(path, payload):
        return {
            "path": path, "kind": "file", "byte_length": len(payload),
            "sha256": hashlib.sha256(payload).hexdigest(),
        }
    return {
        "schema": "implementaudit-custodied-directory-manifest-v1",
        "entries": [
            {"path": ".", "kind": "directory"},
            {"path": "empty", "kind": "directory"},
            {"path": "nested", "kind": "directory"},
            leaf("nested/alpha.bin", b"alpha"),
            {"path": "nested/deeper", "kind": "directory"},
            leaf("nested/deeper/beta.bin", b"beta"),
            leaf("top.bin", b"top"),
        ],
    }


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


def raw_probe_json(value, raw_value):
    placeholder = "__RAW_JSON_NUMBER__"
    prepared = dict(value)
    prepared["probe"] = placeholder
    encoded = lifecycle.canonical_json_bytes(prepared)
    return encoded.replace(
        lifecycle.canonical_json_bytes(placeholder).strip(), raw_value)


def raw_number_json(value, token):
    return raw_probe_json(value, token)


def main():
    rejected("duplicate", lambda: lifecycle.decode_strict_json_bytes(
        b'{"outer":{"x":1,"x":2}}', "duplicate row"))
    for raw in (b'{"x":NaN}', b'{"x":Infinity}', b'{"x":-Infinity}'):
        rejected("non-finite", lambda value=raw:
                 lifecycle.decode_strict_json_bytes(value, "nonfinite row"))
    rejected("utf-8", lambda: lifecycle.decode_strict_json_bytes(
        b"\xff", "invalid row"))
    overflow_failures = []
    for label, raw in (("positive exponent overflow", b"1e400"),
                       ("negative exponent overflow", b"-1e400")):
        collect_rejection(
            label, "non-finite",
            lambda value=raw: lifecycle.decode_strict_json_bytes(
                value, "overflow row"),
            overflow_failures)
    assert not overflow_failures, (
        "decoded exponent overflow unexpectedly accepted: " +
        ", ".join(overflow_failures))

    lossy_number_cases = [
        ("underflow", b"1e-400", 0.0),
        ("precision collapse", b"9007199254740993.0", 9007199254740992.0),
    ]
    lossy_number_failures = []
    for label, token, _ in lossy_number_cases:
        collect_rejection(
            f"direct {label}", "lossy JSON number",
            lambda raw=token: lifecycle.decode_strict_json_bytes(
                raw, "lossy number"),
            lossy_number_failures)

    for target in ("root", "status", "terminal"):
        for label, token, expected_probe in lossy_number_cases:
            with tempfile.TemporaryDirectory(
                    prefix=f"campaign-lossy-{target}-") as tmp:
                root = pathlib.Path(tmp).resolve()
                expected_root = {
                    "schema": "campaign-a-manifest-v1",
                    "campaign": "campaign-a",
                }
                descriptor = mission(0)
                if target == "root":
                    expected_root["probe"] = expected_probe
                    (root / "campaign-manifest.json").write_bytes(
                        raw_number_json(expected_root, token))
                else:
                    lifecycle.write_new_json(
                        root / "campaign-manifest.json", expected_root)
                if target == "status":
                    descriptor["status_identity"]["probe"] = expected_probe
                elif target == "terminal":
                    descriptor["terminal_identity"]["probe"] = expected_probe
                write_attempt(root, descriptor)
                attempt = root / descriptor["attempt"]
                if target == "status":
                    (attempt / "attempt-status.json").write_bytes(
                        raw_number_json(descriptor["status_identity"], token))
                elif target == "terminal":
                    retained = dict(descriptor["terminal_identity"])
                    retained.update({
                        "overall_status": "PASS", "stop_reason": None})
                    (attempt / "attempt-terminal.json").write_bytes(
                        raw_number_json(retained, token))
                expected_root_policy = {
                    "campaign-manifest.json": {
                        "kind": "json_identity", "identity": expected_root,
                    },
                }
                collect_rejection(
                    f"{target} {label}", "lossy JSON number",
                    lambda path=root, item=descriptor,
                           policy=expected_root_policy:
                        lifecycle.validate_terminal_prefix(
                            path, [item], stop_states={"INVALID", "ERROR"},
                            allowed_root=policy),
                    lossy_number_failures)
    assert not lossy_number_failures, (
        "lossy JSON numbers unexpectedly accepted: " +
        ", ".join(lossy_number_failures))

    number_domain_cases = [
        ("positive exponent domain", b"1e1000000000000000000",
         "JSON number domain"),
        ("negative exponent domain", b"1e-1000000000000000000",
         "lossy JSON number"),
    ]
    number_domain_failures = []
    for label, token, reason in number_domain_cases:
        collect_stable_value_error(
            f"direct {label}", reason,
            lambda raw=token: lifecycle.decode_strict_json_bytes(
                raw, "domain number"),
            number_domain_failures)

    for target in ("root", "status", "terminal"):
        for label, token, reason in number_domain_cases:
            with tempfile.TemporaryDirectory(
                    prefix=f"campaign-domain-{target}-") as tmp:
                root = pathlib.Path(tmp).resolve()
                expected_root = {
                    "schema": "campaign-a-manifest-v1",
                    "campaign": "campaign-a",
                }
                descriptor = mission(0)
                if target == "root":
                    expected_root["probe"] = 0.0
                    (root / "campaign-manifest.json").write_bytes(
                        raw_number_json(expected_root, token))
                else:
                    lifecycle.write_new_json(
                        root / "campaign-manifest.json", expected_root)
                if target == "status":
                    descriptor["status_identity"]["probe"] = 0.0
                elif target == "terminal":
                    descriptor["terminal_identity"]["probe"] = 0.0
                write_attempt(root, descriptor)
                attempt = root / descriptor["attempt"]
                if target == "status":
                    (attempt / "attempt-status.json").write_bytes(
                        raw_number_json(descriptor["status_identity"], token))
                elif target == "terminal":
                    retained = dict(descriptor["terminal_identity"])
                    retained.update({
                        "overall_status": "PASS", "stop_reason": None})
                    (attempt / "attempt-terminal.json").write_bytes(
                        raw_number_json(retained, token))
                expected_root_policy = {
                    "campaign-manifest.json": {
                        "kind": "json_identity", "identity": expected_root,
                    },
                }
                collect_stable_value_error(
                    f"{target} {label}", reason,
                    lambda path=root, item=descriptor,
                           policy=expected_root_policy:
                        lifecycle.validate_terminal_prefix(
                            path, [item], stop_states={"INVALID", "ERROR"},
                            allowed_root=policy),
                    number_domain_failures)
    assert not number_domain_failures, (
        "JSON number domain failures were not normalized: " +
        "; ".join(number_domain_failures))

    excessive_depth = sys.getrecursionlimit() + 200
    overlimit_json = (b"[" * excessive_depth + b"0" +
                      b"]" * excessive_depth)
    json_depth_failures = []
    collect_stable_value_error(
        "direct excessive depth", "JSON depth",
        lambda: lifecycle.decode_strict_json_bytes(
            overlimit_json, "deep JSON"),
        json_depth_failures)

    for target in ("root", "status", "terminal"):
        with tempfile.TemporaryDirectory(
                prefix=f"campaign-depth-{target}-") as tmp:
            root = pathlib.Path(tmp).resolve()
            expected_root = {
                "schema": "campaign-a-manifest-v1",
                "campaign": "campaign-a",
            }
            descriptor = mission(0)
            if target == "root":
                expected_root["probe"] = []
                (root / "campaign-manifest.json").write_bytes(
                    raw_probe_json(expected_root, overlimit_json))
            else:
                lifecycle.write_new_json(
                    root / "campaign-manifest.json", expected_root)
            if target == "status":
                descriptor["status_identity"]["probe"] = []
            elif target == "terminal":
                descriptor["terminal_identity"]["probe"] = []
            write_attempt(root, descriptor)
            attempt = root / descriptor["attempt"]
            if target == "status":
                (attempt / "attempt-status.json").write_bytes(
                    raw_probe_json(
                        descriptor["status_identity"], overlimit_json))
            elif target == "terminal":
                retained = dict(descriptor["terminal_identity"])
                retained.update({
                    "overall_status": "PASS", "stop_reason": None})
                (attempt / "attempt-terminal.json").write_bytes(
                    raw_probe_json(retained, overlimit_json))
            expected_root_policy = {
                "campaign-manifest.json": {
                    "kind": "json_identity", "identity": expected_root,
                },
            }
            collect_stable_value_error(
                f"{target} excessive depth", "JSON depth",
                lambda path=root, item=descriptor,
                       policy=expected_root_policy:
                    lifecycle.validate_terminal_prefix(
                        path, [item], stop_states={"INVALID", "ERROR"},
                        allowed_root=policy),
                json_depth_failures)

    overlimit_model = 0
    for _ in range(excessive_depth):
        overlimit_model = [overlimit_model]
    collect_stable_value_error(
        "canonical excessive depth", "JSON depth",
        lambda value=overlimit_model: lifecycle.canonical_json_bytes(value),
        json_depth_failures)
    assert not json_depth_failures, (
        "JSON depth failures were not normalized: " +
        "; ".join(json_depth_failures))

    supported_depth_failures = []
    for kind in ("array", "object"):
        collect_success(
            f"direct supported {kind} identity",
            lambda shape=kind: lifecycle._identity(
                {"probe": nested_model(400, shape)},
                {"probe": nested_model(400, shape)},
                "supported deep identity"),
            supported_depth_failures)
        for target in ("root", "status", "terminal"):
            with tempfile.TemporaryDirectory(
                    prefix=f"campaign-supported-{kind}-{target}-") as tmp:
                root = pathlib.Path(tmp).resolve()
                expected_root = {
                    "schema": "campaign-a-manifest-v1",
                    "campaign": "campaign-a",
                }
                descriptor = mission(0)
                probe = nested_model(400, kind)
                if target == "root":
                    expected_root["probe"] = probe
                elif target == "status":
                    descriptor["status_identity"]["probe"] = probe
                else:
                    descriptor["terminal_identity"]["probe"] = probe
                lifecycle.write_new_json(
                    root / "campaign-manifest.json", expected_root)
                write_attempt(root, descriptor)
                expected_root_policy = {
                    "campaign-manifest.json": {
                        "kind": "json_identity", "identity": expected_root,
                    },
                }
                collect_success(
                    f"{target} supported {kind} identity",
                    lambda path=root, item=descriptor,
                           policy=expected_root_policy:
                        lifecycle.validate_terminal_prefix(
                            path, [item], stop_states={"INVALID", "ERROR"},
                            allowed_root=policy),
                    supported_depth_failures)
    traversal_failures = list(supported_depth_failures)
    for kind in ("array", "object"):
        deep_model = nested_model(excessive_depth, kind)
        collect_stable_value_error(
            f"identity over-limit {kind}", "identity drift",
            lambda value=deep_model: lifecycle._identity(
                {"probe": value}, {"probe": value}, "deep identity"),
            traversal_failures)
        collect_stable_value_error(
            f"canonical over-limit {kind}", "JSON depth",
            lambda value=deep_model: lifecycle.canonical_json_bytes(value),
            traversal_failures)

        expected_root = {
            "schema": "campaign-a-manifest-v1",
            "campaign": "campaign-a",
            "probe": deep_model,
        }
        deep_stage = stage([])
        deep_stage["allowed_root"] = {
            "campaign-manifest.json": {
                "kind": "json_identity", "identity": expected_root,
            },
        }
        raw_manifest = campaign_manifest_with_raw_probe(
            nested_json(excessive_depth, kind))
        with tempfile.TemporaryDirectory(
                prefix=f"campaign-deep-stage-write-{kind}-") as tmp:
            root = pathlib.Path(tmp).resolve()
            (root / "campaign-manifest.json").write_bytes(raw_manifest)
            collect_stable_value_error(
                f"stage write over-limit {kind}", "JSON depth",
                lambda path=root, descriptor=deep_stage:
                    lifecycle.write_stage_terminal(
                        path, descriptor, binding(0)),
                traversal_failures)
        with tempfile.TemporaryDirectory(
                prefix=f"campaign-deep-stage-resume-{kind}-") as tmp:
            root = pathlib.Path(tmp).resolve()
            (root / "campaign-manifest.json").write_bytes(raw_manifest)
            lifecycle.write_new_json(root / "luna-stage-terminal.json", {})
            collect_stable_value_error(
                f"stage resume over-limit {kind}", "JSON depth",
                lambda path=root, descriptor=deep_stage:
                    lifecycle.validate_stage_resume(
                        path, descriptor, binding(0)),
                traversal_failures)

    cyclic_array = []
    cyclic_array.append(cyclic_array)
    cyclic_object = {}
    cyclic_object["self"] = cyclic_object
    for label, cyclic in (
            ("array", cyclic_array), ("object", cyclic_object)):
        collect_stable_value_error(
            f"strict-model cyclic {label}", "cyclic",
            lambda value=cyclic:
                lifecycle._validate_strict_json_model(value),
            traversal_failures)
        collect_stable_value_error(
            f"canonical cyclic {label}", "cyclic",
            lambda value=cyclic: lifecycle.canonical_json_bytes(value),
            traversal_failures)
        collect_stable_value_error(
            f"identity cyclic {label}", "identity drift",
            lambda value=cyclic: lifecycle._identity(
                {"probe": value}, {"probe": value}, "cyclic identity"),
            traversal_failures)
    shared_child = {"values": [1, 2, 3]}
    shared_model = {"first": shared_child, "second": shared_child}
    collect_success(
        "strict-model shared acyclic container",
        lambda: lifecycle._validate_strict_json_model(shared_model),
        traversal_failures)
    collect_success(
        "canonical shared acyclic container",
        lambda: lifecycle.canonical_json_bytes(shared_model),
        traversal_failures)
    collect_success(
        "identity shared acyclic container",
        lambda: lifecycle._identity(
            {"probe": shared_model}, {"probe": shared_model},
            "shared identity"),
        traversal_failures)
    assert not traversal_failures, (
        "JSON traversal was not total: " +
        "; ".join(traversal_failures))

    policy_identity_failures = []
    policy_identity_cases = [
        ("integer-to-boolean", 1, True),
        ("integer-to-float", 1, 1.0),
        ("signed zero", 0.0, -0.0),
        ("nested type", {"nested": [1]}, {"nested": [True]}),
    ]
    for artifact_name, identity_name in (
            ("attempt-status.json", "status_identity"),
            ("attempt-terminal.json", "terminal_identity")):
        for label, expected_value, policy_value in policy_identity_cases:
            with tempfile.TemporaryDirectory(
                    prefix="campaign-policy-identity-") as tmp:
                root = pathlib.Path(tmp).resolve()
                lifecycle.write_new_json(root / "campaign-manifest.json", {
                    "schema": "campaign-a-manifest-v1",
                    "campaign": "campaign-a",
                })
                descriptor = mission(0)
                descriptor[identity_name] = {"probe": expected_value}
                descriptor["allowed_attempt"][artifact_name]["identity"] = {
                    "probe": policy_value,
                }
                collect_stable_value_error(
                    f"{artifact_name} {label}", "identity policy drift",
                    lambda path=root, item=descriptor:
                        lifecycle.validate_terminal_prefix(
                            path, [item], stop_states=["INVALID", "ERROR"],
                            allowed_root=root_policy()),
                    policy_identity_failures)

    for depth in (511, 512):
        with tempfile.TemporaryDirectory(
                prefix=f"campaign-deep-policy-{depth}-") as tmp:
            root = pathlib.Path(tmp).resolve()
            lifecycle.write_new_json(root / "campaign-manifest.json", {
                "schema": "campaign-a-manifest-v1", "campaign": "campaign-a"})
            descriptor = mission(0)
            descriptor["status_identity"] = nested_model(depth, "object")
            descriptor["terminal_identity"] = nested_model(depth, "object")
            descriptor["allowed_attempt"]["attempt-status.json"][
                "identity"] = nested_model(depth, "object")
            descriptor["allowed_attempt"]["attempt-terminal.json"][
                "identity"] = nested_model(depth, "object")
            collect_success(
                f"valid distinct deep policy identities at depth {depth}",
                lambda path=root, item=descriptor:
                    lifecycle.validate_terminal_prefix(
                        path, [item], stop_states=["INVALID", "ERROR"],
                        allowed_root=root_policy()),
                policy_identity_failures)
    control_key_failures = list(policy_identity_failures)
    for missing in ("overall_status", "stop_reason"):
        for operation in ("prefix", "stage write", "stage resume"):
            with tempfile.TemporaryDirectory(
                    prefix="campaign-missing-control-") as tmp:
                root = pathlib.Path(tmp).resolve()
                lifecycle.write_new_json(root / "campaign-manifest.json", {
                    "schema": "campaign-a-manifest-v1",
                    "campaign": "campaign-a",
                })
                descriptor = mission(0)
                write_attempt_without_control(root, descriptor, missing)
                if operation == "stage resume":
                    lifecycle.write_new_json(
                        root / "luna-stage-terminal.json", {})
                if operation == "prefix":
                    fn = (lambda path=root, item=descriptor:
                        lifecycle.validate_terminal_prefix(
                            path, [item], stop_states=["INVALID", "ERROR"],
                            allowed_root=root_policy()))
                elif operation == "stage write":
                    fn = (lambda path=root, item=descriptor:
                        lifecycle.write_stage_terminal(
                            path, stage([item]), binding(1)))
                else:
                    fn = (lambda path=root, item=descriptor:
                        lifecycle.validate_stage_resume(
                            path, stage([item]), binding(1)))
                collect_stable_value_error(
                    f"{operation} missing {missing}",
                    "terminal control field missing", fn,
                    control_key_failures)
    stop_state_failures = list(control_key_failures)
    invalid_stop_states = [
        ("list", []), ("object", {}), ("boolean", True),
        ("null", None), ("number", 1),
    ]
    for label, invalid_state in invalid_stop_states:
        for operation in ("prefix", "stage write", "stage resume"):
            with tempfile.TemporaryDirectory(
                    prefix="campaign-invalid-stop-state-") as tmp:
                root = pathlib.Path(tmp).resolve()
                lifecycle.write_new_json(root / "campaign-manifest.json", {
                    "schema": "campaign-a-manifest-v1",
                    "campaign": "campaign-a",
                })
                invalid_states = [invalid_state]
                if operation == "stage resume":
                    lifecycle.write_new_json(
                        root / "luna-stage-terminal.json", {})
                if operation == "prefix":
                    fn = (lambda path=root, states=invalid_states:
                        lifecycle.validate_terminal_prefix(
                            path, [], stop_states=states,
                            allowed_root=root_policy()))
                else:
                    invalid_stage = stage([])
                    invalid_stage["stop_states"] = invalid_states
                    if operation == "stage write":
                        fn = (lambda path=root, value=invalid_stage:
                            lifecycle.write_stage_terminal(
                                path, value, binding(0)))
                    else:
                        fn = (lambda path=root, value=invalid_stage:
                            lifecycle.validate_stage_resume(
                                path, value, binding(0)))
                collect_stable_value_error(
                    f"{operation} invalid {label} stop state",
                    "stop states contain an invalid value", fn,
                    stop_state_failures)
    assert not stop_state_failures, (
        "invalid stop-state elements were not rejected stably: " +
        "; ".join(stop_state_failures))

    representative_floats = [0.0, -0.0, 1.5, 1e-7, 1e20]
    for expected_float in representative_floats:
        decoded = lifecycle.decode_strict_json_bytes(
            lifecycle.canonical_json_bytes({"value": expected_float}),
            "canonical finite float", require_object=True)
        assert type(decoded["value"]) is float
        assert decoded["value"] == expected_float
        if expected_float == 0.0:
            assert math.copysign(1.0, decoded["value"]) == math.copysign(
                1.0, expected_float)
    exact_integer = 9007199254740993
    decoded_integer = lifecycle.decode_strict_json_bytes(
        lifecycle.canonical_json_bytes({"value": exact_integer}),
        "exact integer", require_object=True)["value"]
    assert type(decoded_integer) is int and decoded_integer == exact_integer

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

    exact_identity_cases = [
        ("scalar boolean", 1, True),
        ("scalar float", 1, 1.0),
        ("nested boolean", {"nested": [1]}, {"nested": [True]}),
        ("nested float", {"nested": [1]}, {"nested": [1.0]}),
        ("positive-to-negative zero", 0.0, -0.0),
        ("negative-to-positive zero", -0.0, 0.0),
    ]
    exact_identity_failures = []
    for label, expected_probe, retained_probe in exact_identity_cases:
        collect_rejection(
            f"direct {label}", "identity drift",
            lambda expected=expected_probe, retained=retained_probe:
                lifecycle._identity(
                    {"probe": retained}, {"probe": expected},
                    "direct identity"),
            exact_identity_failures)

    for target in ("root", "status", "terminal"):
        for label, expected_probe, retained_probe in exact_identity_cases:
            with tempfile.TemporaryDirectory(
                    prefix=f"campaign-exact-{target}-") as tmp:
                root = pathlib.Path(tmp).resolve()
                expected_root = {
                    "schema": "campaign-a-manifest-v1",
                    "campaign": "campaign-a",
                }
                retained_root = dict(expected_root)
                descriptor = mission(0)
                if target == "root":
                    expected_root["probe"] = expected_probe
                    retained_root["probe"] = retained_probe
                elif target == "status":
                    descriptor["status_identity"]["probe"] = expected_probe
                else:
                    descriptor["terminal_identity"]["probe"] = expected_probe
                lifecycle.write_new_json(
                    root / "campaign-manifest.json", retained_root)
                write_attempt(root, descriptor)
                attempt = root / descriptor["attempt"]
                if target == "status":
                    retained = dict(descriptor["status_identity"])
                    retained["probe"] = retained_probe
                    (attempt / "attempt-status.json").write_bytes(
                        lifecycle.canonical_json_bytes(retained))
                elif target == "terminal":
                    retained = dict(descriptor["terminal_identity"])
                    retained["probe"] = retained_probe
                    retained.update({
                        "overall_status": "PASS", "stop_reason": None})
                    (attempt / "attempt-terminal.json").write_bytes(
                        lifecycle.canonical_json_bytes(retained))
                expected_root_policy = {
                    "campaign-manifest.json": {
                        "kind": "json_identity", "identity": expected_root,
                    },
                }
                collect_rejection(
                    f"{target} {label}", "identity drift",
                    lambda path=root, item=descriptor,
                           policy=expected_root_policy:
                        lifecycle.validate_terminal_prefix(
                            path, [item], stop_states={"INVALID", "ERROR"},
                            allowed_root=policy),
                    exact_identity_failures)
    assert not exact_identity_failures, (
        "exact JSON identity drift unexpectedly accepted: " +
        ", ".join(exact_identity_failures))

    with tempfile.TemporaryDirectory(prefix="campaign-stage-terminal-type-") as tmp:
        root = pathlib.Path(tmp).resolve()
        lifecycle.write_new_json(root / "campaign-manifest.json", {
            "schema": "campaign-a-manifest-v1", "campaign": "campaign-a"})
        missions = [mission(0)]
        write_attempt(root, missions[0])
        terminal_path = lifecycle.write_stage_terminal(
            root, stage(missions), binding(1))
        terminal_bytes = terminal_path.read_bytes()
        terminal_value = lifecycle.decode_strict_json_bytes(
            terminal_bytes, "typed stage terminal", require_object=True)
        stage_terminal_type_failures = []
        for label, retained_count in (
                ("boolean mission count", True),
                ("float mission count", 1.0)):
            drifted = dict(terminal_value)
            drifted["mission_count"] = retained_count
            terminal_path.write_bytes(lifecycle.canonical_json_bytes(drifted))
            collect_rejection(
                label, "stage terminal identity mismatch",
                lambda: lifecycle.validate_stage_resume(
                    root, stage(missions), binding(1)),
                stage_terminal_type_failures)
        terminal_path.write_bytes(terminal_bytes)
        assert not stage_terminal_type_failures, (
            "cross-type stage terminal identity drift unexpectedly accepted: " +
            ", ".join(stage_terminal_type_failures))

        for label, extra_value in (
                ("boolean extra field", True),
                ("float extra field", 1.0)):
            drifted = dict(terminal_value)
            drifted["unexpected"] = extra_value
            terminal_path.write_bytes(lifecycle.canonical_json_bytes(drifted))
            rejected("stage terminal key set invalid", lambda:
                     lifecycle.validate_stage_resume(
                         root, stage(missions), binding(1)))
        terminal_path.write_bytes(terminal_bytes)

    with tempfile.TemporaryDirectory(prefix="campaign-directory-red-") as tmp:
        root = pathlib.Path(tmp).resolve()
        lifecycle.write_new_json(root / "campaign-manifest.json", {
            "schema": "campaign-a-manifest-v1", "campaign": "campaign-a"})
        descriptor = directory_mission()
        write_attempt(root, descriptor)
        write_directory_tree(root / descriptor["attempt"])
        prefix = lifecycle.validate_terminal_prefix(
            root, [descriptor], stop_states=["INVALID", "ERROR"],
            allowed_root=root_policy())
        assert prefix[0]["artifact_bytes"]["host-custody"] == (
            lifecycle.canonical_json_bytes(expected_directory_manifest()))

    deterministic_manifests = []
    for reverse in (False, True):
        with tempfile.TemporaryDirectory(
                prefix="campaign-directory-order-") as tmp:
            root = pathlib.Path(tmp).resolve()
            lifecycle.write_new_json(root / "campaign-manifest.json", {
                "schema": "campaign-a-manifest-v1",
                "campaign": "campaign-a",
            })
            descriptor = directory_mission()
            write_attempt(root, descriptor)
            write_directory_tree(
                root / descriptor["attempt"], reverse=reverse)
            row = lifecycle.validate_terminal_prefix(
                root, [descriptor], stop_states=["INVALID", "ERROR"],
                allowed_root=root_policy())[0]
            deterministic_manifests.append(
                row["artifact_bytes"]["host-custody"])
    assert deterministic_manifests[0] == deterministic_manifests[1]

    with tempfile.TemporaryDirectory(
            prefix="campaign-directory-entry-boundary-") as tmp:
        common = pathlib.Path(tmp).resolve()
        owner = common / "owner"
        owner.mkdir()
        sub = owner / "sub"
        sub.mkdir()
        outside = common / "outside"
        outside.mkdir()
        lifecycle.write_new_bytes(outside / "nested.bin", b"outside")
        rejected("escapes owner root", lambda:
                 lifecycle.read_custodied_directory_manifest(
                     outside, "absolute outside directory", root=owner))
        lexical_escape = owner / "sub" / ".." / ".." / "outside"
        directory_bound_failures = []
        collect_stable_value_error(
            "lexical dot-dot escape", "canonical",
            lambda: lifecycle.read_custodied_directory_manifest(
                lexical_escape, "lexical escape directory", root=owner),
            directory_bound_failures)

        for label, final_path in (
                ("final", owner / "final-link"),
                ("parent", owner / "parent-link" / "nested")):
            link = (final_path if label == "final" else final_path.parent)
            target = outside if label == "final" else outside
            try:
                os.symlink(target, link, target_is_directory=True)
            except (NotImplementedError, OSError) as exc:
                print("LIFECYCLE_CUSTODIED_DIRECTORY_ENTRY_" +
                      label.upper() + "_SYMLINK=SKIP:" +
                      type(exc).__name__)
            else:
                rejected("link", lambda path=final_path:
                         lifecycle.read_custodied_directory_manifest(
                             path, f"{label} symlink directory", root=owner))
                link.unlink()
                print("LIFECYCLE_CUSTODIED_DIRECTORY_ENTRY_" +
                      label.upper() + "_SYMLINK=PASS")

        if os.name == "nt":
            junction = owner / "parent-junction"
            made = subprocess.run(
                ["cmd", "/c", "mklink", "/J", str(junction), str(outside)],
                capture_output=True, text=True)
            if made.returncode:
                print("LIFECYCLE_CUSTODIED_DIRECTORY_ENTRY_JUNCTION=SKIP:mklink")
            else:
                rejected("link", lambda:
                         lifecycle.read_custodied_directory_manifest(
                             junction / "nested", "parent junction directory",
                             root=owner))
                os.rmdir(junction)
                print("LIFECYCLE_CUSTODIED_DIRECTORY_ENTRY_JUNCTION=PASS")

    with tempfile.TemporaryDirectory(
            prefix="campaign-directory-bounded-leaf-") as tmp:
        owner = pathlib.Path(tmp).resolve()
        retained = owner / "retained"
        retained.mkdir()
        leaf = retained / "large-sparse.bin"
        chunk_size = 1024 * 1024
        leaf_size = 2 * chunk_size + 17
        with open(leaf, "wb") as stream:
            stream.seek(leaf_size - 1)
            stream.write(b"Z")

        real_fdopen = lifecycle.os.fdopen
        read_sizes = []

        class BoundedReadStream:
            def __init__(self, stream):
                self.stream = stream

            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, traceback):
                self.stream.close()

            def read(self, size=-1):
                read_sizes.append(size)
                return self.stream.read(size)

        def instrumented_fdopen(descriptor, mode):
            return BoundedReadStream(real_fdopen(descriptor, mode))

        lifecycle.os.fdopen = instrumented_fdopen
        try:
            manifest_bytes = lifecycle.read_custodied_directory_manifest(
                retained, "bounded retained directory", root=owner)
        finally:
            lifecycle.os.fdopen = real_fdopen
        if (not read_sizes or
                any(size <= 0 or size > chunk_size for size in read_sizes)):
            directory_bound_failures.append(
                "directory custody used a negative or unbounded read")
        manifest = lifecycle.decode_strict_json_bytes(
            manifest_bytes, "bounded directory manifest", require_object=True)
        leaf_row = next(
            row for row in manifest["entries"]
            if row["path"] == "large-sparse.bin")
        expected_hash = hashlib.sha256()
        remaining_zeros = leaf_size - 1
        zero_block = b"\0" * chunk_size
        while remaining_zeros:
            take = min(remaining_zeros, chunk_size)
            expected_hash.update(zero_block[:take])
            remaining_zeros -= take
        expected_hash.update(b"Z")
        assert leaf_row == {
            "path": "large-sparse.bin", "kind": "file",
            "byte_length": leaf_size,
            "sha256": expected_hash.hexdigest(),
        }
        assert not directory_bound_failures, (
            "recursive custody bounds failed: " +
            "; ".join(directory_bound_failures))

    with tempfile.TemporaryDirectory(prefix="campaign-directory-root-policy-") as tmp:
        root = pathlib.Path(tmp).resolve()
        lifecycle.write_new_json(root / "campaign-manifest.json", {
            "schema": "campaign-a-manifest-v1", "campaign": "campaign-a"})
        (root / "host-custody").mkdir()
        forbidden_root_policy = root_policy()
        forbidden_root_policy["host-custody"] = {
            "kind": "custodied_directory"}
        rejected("forbidden", lambda: lifecycle.validate_terminal_prefix(
            root, [], stop_states=["INVALID", "ERROR"],
            allowed_root=forbidden_root_policy))

    with tempfile.TemporaryDirectory(prefix="campaign-directory-hardlink-") as tmp:
        root = pathlib.Path(tmp).resolve()
        lifecycle.write_new_json(root / "campaign-manifest.json", {
            "schema": "campaign-a-manifest-v1", "campaign": "campaign-a"})
        descriptor = directory_mission()
        write_attempt(root, descriptor)
        host = root / descriptor["attempt"] / "host-custody"
        host.mkdir()
        nested = host / "nested"
        nested.mkdir()
        with tempfile.TemporaryDirectory(
                prefix="campaign-directory-hardlink-source-") as source_tmp:
            source = pathlib.Path(source_tmp).resolve() / "source.bin"
            lifecycle.write_new_bytes(source, b"linked")
            os.link(source, nested / "linked.bin")
            rejected("hardlink identity", lambda:
                     lifecycle.validate_terminal_prefix(
                         root, [descriptor], stop_states=["INVALID", "ERROR"],
                         allowed_root=root_policy()))
            print("LIFECYCLE_CUSTODIED_DIRECTORY_HARDLINK=PASS")

    for link_kind in ("file", "directory", "parent"):
        with tempfile.TemporaryDirectory(
                prefix=f"campaign-directory-{link_kind}-symlink-") as tmp:
            root = pathlib.Path(tmp).resolve()
            lifecycle.write_new_json(root / "campaign-manifest.json", {
                "schema": "campaign-a-manifest-v1",
                "campaign": "campaign-a",
            })
            descriptor = directory_mission()
            write_attempt(root, descriptor)
            host = root / descriptor["attempt"] / "host-custody"
            host.mkdir()
            with tempfile.TemporaryDirectory(
                    prefix="campaign-directory-link-target-") as target_tmp:
                target = pathlib.Path(target_tmp).resolve()
                if link_kind == "file":
                    target_path = target / "target.bin"
                    lifecycle.write_new_bytes(target_path, b"target")
                    link = host / "linked.bin"
                    directory_link = False
                else:
                    target_path = target / "target-directory"
                    target_path.mkdir()
                    if link_kind == "parent":
                        lifecycle.write_new_bytes(
                            target_path / "nested.bin", b"nested")
                    link = host / ("linked-directory" if link_kind == "directory"
                                   else "linked-parent")
                    directory_link = True
                try:
                    os.symlink(
                        target_path, link, target_is_directory=directory_link)
                except (NotImplementedError, OSError) as exc:
                    print("LIFECYCLE_CUSTODIED_DIRECTORY_" +
                          link_kind.upper() + "_SYMLINK=SKIP:" +
                          type(exc).__name__)
                else:
                    rejected("link", lambda: lifecycle.validate_terminal_prefix(
                        root, [descriptor], stop_states=["INVALID", "ERROR"],
                        allowed_root=root_policy()))
                    link.unlink()
                    print("LIFECYCLE_CUSTODIED_DIRECTORY_" +
                          link_kind.upper() + "_SYMLINK=PASS")

    if os.name == "nt":
        with tempfile.TemporaryDirectory(
                prefix="campaign-directory-junction-") as tmp:
            root = pathlib.Path(tmp).resolve()
            lifecycle.write_new_json(root / "campaign-manifest.json", {
                "schema": "campaign-a-manifest-v1",
                "campaign": "campaign-a",
            })
            descriptor = directory_mission()
            write_attempt(root, descriptor)
            host = root / descriptor["attempt"] / "host-custody"
            host.mkdir()
            with tempfile.TemporaryDirectory(
                    prefix="campaign-directory-junction-target-") as target_tmp:
                target = pathlib.Path(target_tmp).resolve()
                lifecycle.write_new_bytes(target / "nested.bin", b"nested")
                junction = host / "junction"
                made = subprocess.run(
                    ["cmd", "/c", "mklink", "/J", str(junction), str(target)],
                    capture_output=True, text=True)
                if made.returncode:
                    print("LIFECYCLE_CUSTODIED_DIRECTORY_JUNCTION=SKIP:mklink")
                else:
                    rejected("link", lambda:
                             lifecycle.validate_terminal_prefix(
                                 root, [descriptor],
                                 stop_states=["INVALID", "ERROR"],
                                 allowed_root=root_policy()))
                    os.rmdir(junction)
                    print("LIFECYCLE_CUSTODIED_DIRECTORY_JUNCTION=PASS")

    if hasattr(os, "mkfifo"):
        with tempfile.TemporaryDirectory(
                prefix="campaign-directory-special-") as tmp:
            root = pathlib.Path(tmp).resolve()
            lifecycle.write_new_json(root / "campaign-manifest.json", {
                "schema": "campaign-a-manifest-v1",
                "campaign": "campaign-a",
            })
            descriptor = directory_mission()
            write_attempt(root, descriptor)
            host = root / descriptor["attempt"] / "host-custody"
            host.mkdir()
            fifo = host / "retained.fifo"
            os.mkfifo(fifo)
            rejected("special", lambda: lifecycle.validate_terminal_prefix(
                root, [descriptor], stop_states=["INVALID", "ERROR"],
                allowed_root=root_policy()))
            fifo.unlink()
            print("LIFECYCLE_CUSTODIED_DIRECTORY_SPECIAL=PASS")
    else:
        print("LIFECYCLE_CUSTODIED_DIRECTORY_SPECIAL=SKIP:unsupported")

    with tempfile.TemporaryDirectory(prefix="campaign-directory-snapshot-") as tmp:
        root = pathlib.Path(tmp).resolve()
        lifecycle.write_new_json(root / "campaign-manifest.json", {
            "schema": "campaign-a-manifest-v1", "campaign": "campaign-a"})
        descriptor = directory_mission()
        write_attempt(root, descriptor)
        host = write_directory_tree(root / descriptor["attempt"])
        lifecycle.write_stage_terminal(
            root, stage([descriptor]), binding(1))

        alpha = host / "nested" / "alpha.bin"
        alpha.write_bytes(b"changed")
        rejected("stage snapshot", lambda: lifecycle.validate_stage_resume(
            root, stage([descriptor]), binding(1)))
        alpha.write_bytes(b"alpha")

        added = host / "added.bin"
        lifecycle.write_new_bytes(added, b"added")
        rejected("stage snapshot", lambda: lifecycle.validate_stage_resume(
            root, stage([descriptor]), binding(1)))
        added.unlink()

        beta = host / "nested" / "deeper" / "beta.bin"
        beta.unlink()
        rejected("stage snapshot", lambda: lifecycle.validate_stage_resume(
            root, stage([descriptor]), binding(1)))
        lifecycle.write_new_bytes(beta, b"beta")

        added_empty = host / "added-empty"
        added_empty.mkdir()
        rejected("stage snapshot", lambda: lifecycle.validate_stage_resume(
            root, stage([descriptor]), binding(1)))
        added_empty.rmdir()

        empty = host / "empty"
        empty.rmdir()
        rejected("stage snapshot", lambda: lifecycle.validate_stage_resume(
            root, stage([descriptor]), binding(1)))
        empty.mkdir()

        renamed = host / "nested" / "renamed.bin"
        alpha.rename(renamed)
        rejected("stage snapshot", lambda: lifecycle.validate_stage_resume(
            root, stage([descriptor]), binding(1)))
        renamed.rename(alpha)

        top = host / "top.bin"
        top.unlink()
        top.mkdir()
        rejected("stage snapshot", lambda: lifecycle.validate_stage_resume(
            root, stage([descriptor]), binding(1)))
        top.rmdir()
        lifecycle.write_new_bytes(top, b"top")

        with tempfile.TemporaryDirectory(
                prefix="campaign-directory-replacement-source-") as source_tmp:
            hardlink_source = pathlib.Path(source_tmp).resolve() / "source.bin"
            lifecycle.write_new_bytes(hardlink_source, b"top")
            top.unlink()
            os.link(hardlink_source, top)
            rejected("hardlink", lambda: lifecycle.validate_stage_resume(
                root, stage([descriptor]), binding(1)))
            top.unlink()
            lifecycle.write_new_bytes(top, b"top")

        with tempfile.TemporaryDirectory(
                prefix="campaign-directory-symlink-source-") as source_tmp:
            symlink_source = pathlib.Path(source_tmp).resolve() / "source.bin"
            lifecycle.write_new_bytes(symlink_source, b"top")
            top.unlink()
            try:
                os.symlink(symlink_source, top)
            except (NotImplementedError, OSError) as exc:
                lifecycle.write_new_bytes(top, b"top")
                print("LIFECYCLE_CUSTODIED_DIRECTORY_POST_PAUSE_SYMLINK=SKIP:" +
                      type(exc).__name__)
            else:
                rejected("link", lambda: lifecycle.validate_stage_resume(
                    root, stage([descriptor]), binding(1)))
                top.unlink()
                lifecycle.write_new_bytes(top, b"top")
                print("LIFECYCLE_CUSTODIED_DIRECTORY_POST_PAUSE_SYMLINK=PASS")
        lifecycle.validate_stage_resume(
            root, stage([descriptor]), binding(1))

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

    with tempfile.TemporaryDirectory(prefix="campaign-tuple-missions-") as tmp:
        root = pathlib.Path(tmp).resolve()
        lifecycle.write_new_json(root / "campaign-manifest.json", {
            "schema": "campaign-a-manifest-v1", "campaign": "campaign-a"})
        missions = [mission(0)]
        write_attempt(root, missions[0])
        tuple_stage = stage(tuple(missions))
        rejected("stage descriptor missions must be an exact list", lambda:
                 lifecycle.write_stage_terminal(root, tuple_stage, binding(1)))

    with tempfile.TemporaryDirectory(prefix="campaign-set-stop-states-") as tmp:
        root = pathlib.Path(tmp).resolve()
        lifecycle.write_new_json(root / "campaign-manifest.json", {
            "schema": "campaign-a-manifest-v1", "campaign": "campaign-a"})
        missions = [mission(0)]
        write_attempt(root, missions[0])
        set_stage = stage(missions)
        set_stage["stop_states"] = {"INVALID", "ERROR"}
        rejected("stage descriptor stop_states must be an exact list", lambda:
                 lifecycle.write_stage_terminal(root, set_stage, binding(1)))

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

    root_campaign_failures = []
    with tempfile.TemporaryDirectory(prefix="campaign-foreign-root-") as tmp:
        root = pathlib.Path(tmp).resolve()
        lifecycle.write_new_json(root / "campaign-manifest.json", {
            "schema": "campaign-b-manifest-v1", "campaign": "campaign-b"})
        local_missions = [mission(0, "campaign-a")]
        write_attempt(root, local_missions[0])
        foreign_root_stage = stage(local_missions, campaign="campaign-a")
        foreign_root_stage["allowed_root"] = root_policy("campaign-b")
        collect_rejection(
            "foreign-only root campaign", "root campaign identity",
            lambda: lifecycle.write_stage_terminal(
                root, foreign_root_stage, binding(1, campaign="campaign-a")),
            root_campaign_failures)

    with tempfile.TemporaryDirectory(prefix="campaign-conflicting-root-") as tmp:
        root = pathlib.Path(tmp).resolve()
        lifecycle.write_new_json(root / "campaign-manifest.json", {
            "schema": "campaign-a-manifest-v1", "campaign": "campaign-a"})
        lifecycle.write_new_json(root / "foreign-root.json", {
            "schema": "campaign-b-root-v1", "campaign": "campaign-b"})
        local_missions = [mission(0, "campaign-a")]
        write_attempt(root, local_missions[0])
        conflicting_stage = stage(local_missions, campaign="campaign-a")
        conflicting_stage["allowed_root"]["foreign-root.json"] = {
            "kind": "json_identity",
            "identity": {
                "schema": "campaign-b-root-v1", "campaign": "campaign-b"},
        }
        collect_rejection(
            "conflicting additional root campaign", "root campaign identity",
            lambda: lifecycle.write_stage_terminal(
                root, conflicting_stage, binding(1, campaign="campaign-a")),
            root_campaign_failures)
    assert not root_campaign_failures, (
        "root campaign conflict unexpectedly accepted: " +
        ", ".join(root_campaign_failures))

    with tempfile.TemporaryDirectory(prefix="campaign-generic-root-") as tmp:
        root = pathlib.Path(tmp).resolve()
        lifecycle.write_new_json(root / "campaign-manifest.json", {
            "schema": "campaign-a-manifest-v1", "campaign": "campaign-a"})
        lifecycle.write_new_json(root / "generic-root.json", {
            "schema": "generic-root-v1", "purpose": "non-campaign evidence"})
        local_missions = [mission(0, "campaign-a")]
        write_attempt(root, local_missions[0])
        generic_stage = stage(local_missions, campaign="campaign-a")
        generic_stage["allowed_root"]["generic-root.json"] = {
            "kind": "json_identity",
            "identity": {"schema": "generic-root-v1"},
        }
        lifecycle.write_stage_terminal(
            root, generic_stage, binding(1, campaign="campaign-a"))

    with tempfile.TemporaryDirectory(prefix="campaign-complete-attempt-") as tmp:
        root = pathlib.Path(tmp).resolve()
        lifecycle.write_new_json(root / "campaign-manifest.json", {
            "schema": "campaign-a-manifest-v1", "campaign": "campaign-a"})
        complete_missions = [mission(0)]
        complete_descriptor = complete_missions[0]
        complete_descriptor["allowed_attempt"].update({
            "optional-evidence.bin": {"kind": "custodied_file"},
            "retained-evidence.bin": {"kind": "custodied_file"},
        })
        write_attempt(root, complete_descriptor)
        attempt = root / complete_descriptor["attempt"]
        retained_path = attempt / "retained-evidence.bin"
        retained_bytes = b"retained-at-pause"
        lifecycle.write_new_bytes(retained_path, retained_bytes)
        lifecycle.write_stage_terminal(
            root, stage(complete_missions), binding(1))

        complete_set_failures = []
        retained_path.write_bytes(b"mutated-after-pause")
        collect_rejection(
            "mutated present attempt artifact", "stage snapshot",
            lambda: lifecycle.validate_stage_resume(
                root, stage(complete_missions), binding(1)),
            complete_set_failures)
        retained_path.write_bytes(retained_bytes)

        optional_path = attempt / "optional-evidence.bin"
        lifecycle.write_new_bytes(optional_path, b"added-after-pause")
        collect_rejection(
            "added declared attempt artifact", "stage snapshot",
            lambda: lifecycle.validate_stage_resume(
                root, stage(complete_missions), binding(1)),
            complete_set_failures)
        optional_path.unlink()

        retained_path.unlink()
        collect_rejection(
            "removed declared attempt artifact", "stage snapshot",
            lambda: lifecycle.validate_stage_resume(
                root, stage(complete_missions), binding(1)),
            complete_set_failures)
        lifecycle.write_new_bytes(retained_path, retained_bytes)
        assert not complete_set_failures, (
            "complete attempt evidence drift unexpectedly accepted: " +
            ", ".join(complete_set_failures))

    print("test_campaign_lifecycle: ok")


if __name__ == "__main__":
    main()
