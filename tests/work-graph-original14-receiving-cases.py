#!/usr/bin/env python3
"""Source-bound receiving controls for one reviewed R0039 original14 closure.

This separately selected POSIX fixture does not run an R0039 owner, Git,
currentness command or native subject. It acquires the producer's exact reviewed
compiler as data, extracts its source-owned tuple without importing it, and
checks the real R0035 acquisition and fixed receiver profiles against the actual
eight producer buffers. All mutations stay in a fresh retained fixture.

Example (the caller owns admission and fresh evidence paths):
  python3 -B tests/work-graph-original14-receiving-cases.py \
      --r0039-source-root /absolute/reviewed-r0039 \
      --retain-fixture /absolute/fresh-fixture \
      --evidence /absolute/fresh-result.json

Expected non-Windows refusal proves only that the existing host gate remains.
It is never positive Windows custody, authentic execution or native acceptance.
"""
from __future__ import annotations

import sys
sys.dont_write_bytecode = True

import argparse
import ast
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import types
from unittest import mock


ROOT = Path(__file__).absolute().parents[1]
PRODUCER_COMPILER = "source-peers/route-graph/skills/implementaudit/scripts/compile-work-graph.py"
# The independently reviewed producer candidate, not this receiver's own tuple.
PRODUCER_COMPILER_BYTES = 244556
PRODUCER_COMPILER_SHA256 = "78e519e7839b72d7402e948671dd311904e18d701925ceae04364b1e6081622c"
NAMES = ("claim-run.sh", "validate-run-root.sh", "claim-run-rotation.py",
         "rotate-canonical-state.py", "canonical_hot_projection.py",
         "canonical_custody.py", "canonical_rotation_inputs.py", "read-canonical-pair.py")
RECEIVER_FILES = ("skills/implementaudit/scripts/compile-work-graph.py",
                  "scripts/operational-evidence.py", "scripts/work-graph-continuity-transport.py",
                  "scripts/operational_query_policy.py")


def check(condition, message):
    if not condition:
        raise AssertionError(message)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def load(raw, path, name):
    # Compile the retained buffer, not an import loader's later pathname read.
    module = types.ModuleType(name)
    module.__file__ = str(path)
    module.__package__ = ""
    sys.modules[name] = module
    exec(compile(raw, str(path), "exec"), module.__dict__)
    return module


def acquire(graph, owner, path, maximum):
    return graph._native_static_file_v1(owner, path, maximum, dict(remaining=maximum))


def expect_refusal(error_type, operation, phrase):
    try:
        operation()
    except error_type as exc:
        check(phrase in str(exc), "unexpected refusal: " + str(exc))
        return str(exc)
    raise AssertionError("changed or unsupported input was accepted")


def original14_controls(producer_root, fixture, report):
    compiler_raw = (ROOT / RECEIVER_FILES[0]).read_bytes()
    graph = load(compiler_raw, ROOT / RECEIVER_FILES[0], "original14_source_receiver")
    owner, _, _ = graph._native_static_owner_module_v1()
    producer_raw, producer_mode = acquire(graph, owner, producer_root / PRODUCER_COMPILER,
                                         PRODUCER_COMPILER_BYTES)
    check(len(producer_raw) == PRODUCER_COMPILER_BYTES and
          digest(producer_raw) == PRODUCER_COMPILER_SHA256,
          "producer compiler is outside the independently reviewed candidate")
    syntax = ast.parse(producer_raw)
    declarations = [node.value for node in syntax.body if isinstance(node, ast.Assign)
                    and any(isinstance(target, ast.Name) and
                            target.id == "_NATIVE_ORIGINAL14_CLOSURE_V1" for target in node.targets)]
    check(len(declarations) == 1, "producer must own exactly one original14 closure")
    producer_profile = ast.literal_eval(declarations[0])
    check(type(producer_profile) is tuple and tuple(row[0] for row in producer_profile) == NAMES,
          "reviewed producer closure population differs")
    expected = tuple((*row, None) for row in producer_profile)
    check(sum(row[1] for row in expected) <= 1024 * 1024, "closure exceeds unchanged acquisition budget")
    report["producer_compiler"] = dict(path=str(producer_root / PRODUCER_COMPILER),
        bytes=len(producer_raw), sha256=digest(producer_raw), mode=producer_mode)

    captures, source_records = {}, []
    for name, size, sha256 in producer_profile:
        relative = (("source-peers/native-runtime/skills/implementaudit/scripts/"
                     if name in NAMES[:2] else "skills/implementaudit/scripts/") + name)
        path = producer_root / relative
        raw, mode = acquire(graph, owner, path, size)
        check((len(raw), digest(raw)) == (size, sha256), "producer dependency differs: " + name)
        captures[name] = (raw, mode)
        source_records.append(dict(name=name, path=str(path), bytes=len(raw), sha256=digest(raw), mode=mode))
    report["producer_sources"] = source_records

    # This is an explicitly constructed receiving fixture, not production R35
    # materialization or a native install. Producer buffers are never imported.
    fixture.mkdir(parents=True, exist_ok=False)
    target = fixture / "receiver"
    target.mkdir()
    receiver_records, receiver_buffers = [], {}
    for relative in RECEIVER_FILES:
        raw, mode = acquire(graph, owner, ROOT / relative, 1024 * 1024)
        if relative == RECEIVER_FILES[0]:
            check(raw == compiler_raw, "actual executing compiler buffer changed before fixture capture")
        if relative == "scripts/operational_query_policy.py":
            check((len(raw), digest(raw)) ==
                  (owner._QUERY_POLICY_MODULE_BYTES, owner._QUERY_POLICY_MODULE_SHA256),
                  "receiving query-policy dependency differs from fixed owner pins")
        receiver_buffers[relative] = raw
        path = target / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("xb") as stream:
            stream.write(raw)
        path.chmod(mode)
        receiver_records.append(dict(path=relative, bytes=len(raw), sha256=digest(raw), mode=mode))
    scripts = target / "skills/implementaudit/scripts"
    for name, (raw, mode) in captures.items():
        path = scripts / name
        with path.open("xb") as stream:
            stream.write(raw)
        path.chmod(mode)
    report["receiver_sources"] = receiver_records
    report["fixture"] = str(target)

    receiver = load(receiver_buffers[RECEIVER_FILES[0]], scripts / "compile-work-graph.py",
                    "original14_constructed_receiver")
    receiving_owner, owner_path, owner_raw = receiver._native_static_owner_module_v1()
    claim, validate = (captures[name][0] for name in NAMES[:2])

    def acquire_closure():
        return receiver._native_six_source_transport_v1(receiving_owner, claim, validate)

    adapter, sources, adapter_source = acquire_closure()
    profile = adapter._source_profile(sources)
    check(profile == expected, "transport did not select the exact reviewed producer tuple")
    check(tuple(Path(path).name for path, raw in sources) == NAMES, "acquired source order differs")
    check(all(Path(path) == scripts / name and raw == captures[name][0]
              for (path, raw), name in zip(sources, NAMES)), "acquisition crossed a physical source path")
    check(sum(row == expected for row in receiving_owner._NATIVE_CONTINUITY_SOURCE_PROFILES_V1) == 1,
          "independent receiver must select exactly the same full tuple")
    check(profile in adapter.ORIGINAL14_SOURCE_PROFILES_V1,
          "original14 was classified as a POSIX or legacy shortcut profile")
    pair = tuple(row[2] for row in expected[:2])
    check(pair not in (receiver._NATIVE_REQUIRE_VERIFICATION_EQUIVALENCE,
                       receiver._NATIVE_COMBINED_CURRENT_PAIR_V1),
          "original14 entered an 18-field equivalence shortcut")
    report["controls"].append(dict(id="R01", status="PASS_SOURCE_ONLY",
        observation="Real compiler acquisition and independent receiver agree with all eight actual producer buffers",
        acquired_bytes=sum(len(raw) for _, raw in sources)))

    physical = []
    for name in NAMES:
        path = scripts / name
        raw = captures[name][0]
        changed = bytes((raw[0] ^ 1,)) + raw[1:]
        check(len(changed) == len(raw), "same-size negative control is malformed")
        try:
            path.write_bytes(changed)
            reason = expect_refusal(receiver.WorkGraphError, acquire_closure,
                                    "native continuity closure source identity changed")
            physical.append(dict(name=name, sha256=digest(changed), refusal=reason))
        finally:
            path.write_bytes(raw)
    check(acquire_closure()[1] == sources, "fixture source bytes were not restored")
    report["controls"].append(dict(id="R02", status="PASS_SOURCE_ONLY", variants=physical,
        observation="Every same-size physical dependency mutation refuses through the real compiler reader"))

    populations = []
    malformed = (
        ("omitted", sources[:-1]),
        ("extra", sources + sources[:1]),
        ("reordered", sources[1:] + sources[:1]),
        ("mutable-population", list(sources)),
        ("mutable-buffer", ((sources[0][0], bytearray(sources[0][1])),) + sources[1:]),
        ("changed-buffer", ((sources[0][0], sources[0][1] + b"\n"),) + sources[1:]),
    )
    for label, value in malformed:
        reason = expect_refusal(adapter.ContinuityTransportError,
            lambda value=value: adapter._source_profile(value), "CONTINUITY_TRANSPORT_SOURCE_REFUSED")
        populations.append(dict(variant=label, refusal=reason))
    report["controls"].append(dict(id="R03", status="PASS_SOURCE_ONLY", variants=populations,
        observation="Incomplete, reordered, mutable and changed source populations cannot select the profile"))

    pins = []
    for path, raw, operation, phrase in (
        (adapter_source[0], adapter_source[1], acquire_closure,
         "native continuity transport source identity changed"),
        (owner_path, owner_raw, receiver._native_static_owner_module_v1,
         "native static source owner is unavailable or changed"),
        (target / "scripts/operational_query_policy.py",
         receiver_buffers["scripts/operational_query_policy.py"],
         receiver._native_static_owner_module_v1,
         "native static source owner is unavailable or changed"),
    ):
        try:
            path.write_bytes(raw + b"\n# changed pinned source\n")
            reason = expect_refusal(receiver.WorkGraphError, operation, phrase)
            pins.append(dict(name=path.name, refusal=reason))
        finally:
            path.write_bytes(raw)
    report["controls"].append(dict(id="R04", status="PASS_SOURCE_ONLY", variants=pins,
        observation="Physical transport, receiving-owner and query-policy drift refuse before their altered bytes execute"))

    transport_refusal = expect_refusal(adapter.ContinuityTransportError,
        lambda: adapter.call_readonly_v1(receiving_owner, repository=str(target), sources=sources,
                                        arguments=("--current-controller",)),
        "CONTINUITY_TRANSPORT_UNSUPPORTED_HOST")
    receiver_refusal = expect_refusal(receiving_owner.OperationalEvidenceError,
        lambda: receiving_owner._native_check_continuity_closure_v1(
            dict(schema="implementaudit.native-continuity-closure.v1", authority="NONE"), target,
            scripts / "compile-work-graph.py",
            dict(claim_sha256=pair[0], validate_sha256=pair[1])),
        "original14 requires qualified Windows custody")
    report["controls"].append(dict(id="R05", status="PASS_EXPECTED_HOST_REFUSAL_ONLY",
        transport_refusal=transport_refusal, receiver_refusal=receiver_refusal,
        observation="Actual POSIX host cannot promote original14 source recognition into Windows custody"))
    check(acquire_closure()[1] == sources, "source closure changed after the controls")
    for record in receiver_records:
        path = target / record["path"]
        check((len(path.read_bytes()), digest(path.read_bytes()), stat.S_IMODE(path.stat().st_mode)) ==
              (record["bytes"], record["sha256"], record["mode"]), "receiver fixture not restored")
    report["transport"] = dict(path=str(adapter_source[0]), bytes=len(adapter_source[1]),
                               sha256=digest(adapter_source[1]), mode=adapter_source[2])
    report["selected_profile"] = profile


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--r0039-source-root", required=True, type=Path)
    parser.add_argument("--retain-fixture", required=True, type=Path)
    parser.add_argument("--evidence", required=True, type=Path)
    args = parser.parse_args()
    if os.name != "posix":
        parser.error("this source-only control requires an actual POSIX host; no Windows owner is launched")
    producer, fixture, evidence = (value.absolute() for value in
        (args.r0039_source_root, args.retain_fixture, args.evidence))
    for output in (fixture, evidence):
        if any(output == source or source in output.parents for source in (ROOT, producer)):
            parser.error("fixture and evidence must be outside both source roots")
    if os.path.lexists(fixture) or os.path.lexists(evidence):
        parser.error("fixture and evidence paths must be fresh")
    report = dict(schema="implementaudit.original14-source-receiving-controls.v1",
        status="STARTED", scope="PL5_CONSTRUCTED_SOURCE_RECEIVING_ONLY", controls=[],
        native_acceptance="NOT_ESTABLISHED", windows_custody="UNPROVED",
        receipt_execution="NOT_PERFORMED", originals=0, authority="NONE")
    attempts = [0]

    def no_children(*arguments, **keywords):
        attempts[0] += 1
        raise AssertionError("source-only receiving control attempted a child launch")

    code = 1
    try:
        with mock.patch.object(subprocess, "Popen", side_effect=no_children):
            original14_controls(producer, fixture, report)
        check(attempts[0] == 0, "a source control attempted native or child execution")
        report["status"] = "PASS_SOURCE_CONTROLS_ONLY"
        code = 0
    except Exception as exc:
        report["status"] = "FAIL_SOURCE_CONTROL"
        report["failure"] = dict(type=type(exc).__name__, message=str(exc))
    finally:
        report["child_launch_attempts"] = attempts[0]
        evidence.parent.mkdir(parents=True, exist_ok=True)
        with evidence.open("x", encoding="utf-8") as stream:
            stream.write(json.dumps(report, sort_keys=True, indent=2) + "\n")
    print(json.dumps(report, sort_keys=True))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
