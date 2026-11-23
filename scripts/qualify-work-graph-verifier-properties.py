#!/usr/bin/env python3
"""Inactive, repo-only candidate for three canonical verifier properties."""

import argparse
import hashlib
import importlib.util
import os
from pathlib import Path
import re
import selectors
import subprocess
import sys
import tempfile
import time


HERE = Path(__file__).resolve()
ROOT = HERE.parents[1]
QUALIFIER = "scripts/qualify-work-graph-verifier.py"
COMPILER = "skills/implementaudit/scripts/compile-work-graph.py"
CHECKER = "scripts/check-validation-registry.sh"
REGISTRY = "scripts/verify-package.sh"
WORKFLOW = ".github/workflows/validate.yml"
ROSTER = "tests/*.test.sh"
NODE = f"COMMAND:{CHECKER}:0"
SCHEMA = "implementaudit.verifier-property-evidence.v5-candidate"
POPULATION = "INCOMPLETE_REST_UNQUALIFIED"

SOURCE_PINS = {
    QUALIFIER: "05840b610fc4490aed9f825eca2f5ccb1caf1169137c4820c3c9f0e2a68d1046",
    COMPILER: "ac4cc4180b1d4225b36252080245c5afd6824aaae5624b784b06e49a763bf772",
    CHECKER: "723d5c90ae7ec8e57d997e72735e2f17be71836923343bb7c1368622f6f03f63",
    REGISTRY: "ea132140d64d2714f5a54356c4b79cd05dd2b32017c38cd2307115adc7ec6978",
}
SOURCE_LIMIT = 64 * 1024
OWNER_LIMIT = 512 * 1024
OBSERVATION_LIMIT = 64 * 1024
RECORD_LIMIT = 256 * 1024
CHECK_SECONDS = 10
PYTHON_ARGS = ("-I", "-S", "-B", "-X", "utf8", "-")
CHILD_ENV = {"LC_ALL": "C"}

# Declarations for the exact source owner's existing branches. Order follows
# that owner's checks. Neither membership nor other nodes are in this slice.
PROPERTY_CONTRACTS = {
    "fixed_python_runner_image": ((53, 57), (WORKFLOW,)),
    "canonical_route_exactly_once": ((63, 67), (WORKFLOW,)),
    "no_direct_ci_test_dispatch": ((68, 73), (WORKFLOW, ROSTER)),
}
IMAGE_DIAGNOSTIC = "fixed Python 3.12 CI prerequisites require the qualified ubuntu-24.04 image"
ROUTE_DIAGNOSTIC = ".github/workflows/validate.yml must invoke scripts/verify-package.sh exactly once"


def descriptor(data):
    return {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}


def check_pin(name, data):
    if descriptor(data)["sha256"] != SOURCE_PINS[name]:
        raise ValueError(f"unsupported source pin: {name}")
    return data


def qualifier():
    """Load only the exact reviewed qualifier and its existing compiler."""
    path = ROOT / QUALIFIER
    with path.open("rb") as stream:
        driver = check_pin(QUALIFIER, stream.read(OWNER_LIMIT + 1))
    with (ROOT / COMPILER).open("rb") as stream:
        compiler = check_pin(COMPILER, stream.read(OWNER_LIMIT + 1))
    spec = importlib.util.spec_from_file_location("property_candidate_qualifier", path)
    module = importlib.util.module_from_spec(spec)
    # The existing loader-bound code path accepts source buffers only. This
    # consumes those exact bytes without importing an input-root program.
    module._R0035_EFFECT_SOURCE_CAPTURE = {
        "driver": driver, "compiler": compiler, "expected_compiler_sha256": SOURCE_PINS[COMPILER],
    }
    exec(compile(driver, str(path), "exec"), module.__dict__)
    return module


def read_member(owner, root, name, byte_limit):
    member = owner.source_member(name, root=root, with_bytes=True, byte_limit=byte_limit)
    if member["kind"] != "FILE":
        raise ValueError(f"ordinary file required: {name}")
    return member["_acquired_bytes"]


def acquire(owner, root):
    files = {name: read_member(owner, root, name, SOURCE_LIMIT) for name in (CHECKER, REGISTRY, WORKFLOW)}
    for name in (CHECKER, REGISTRY):
        check_pin(name, files[name])
    roster = owner.registry_membership_v1(root)["entries"]
    return files, roster


def environment(owner):
    executable = owner.executable_identity(sys.executable)
    tool = {name: executable[name] for name in ("mode", "bytes", "sha256")}
    return executable["resolved_path"], {
        "platform": sys.platform, "python_implementation": sys.implementation.name,
        "python_version": list(sys.version_info[:3]), "interpreter": tool,
        "python_args": list(PYTHON_ARGS), "child_environment": CHILD_ENV,
        "coverage": "FIXED_LOCAL_INTERPRETER_AND_ENVIRONMENT; OTHER_TOOLCHAIN_UNQUALIFIED",
    }


def collect_checker(command, program, root):
    stdout = bytearray()
    stderr = bytearray()
    deadline = time.monotonic() + CHECK_SECONDS

    def remaining():
        seconds = deadline - time.monotonic()
        if seconds <= 0:
            raise subprocess.TimeoutExpired(command, CHECK_SECONDS)
        return seconds

    # A file feeds the fixed program without blocking while either output pipe
    # fills. Read both pipes under one deadline and one byte budget.
    with tempfile.TemporaryFile() as source, selectors.DefaultSelector() as streams:
        source.write(program)
        source.seek(0)
        with subprocess.Popen(command, stdin=source, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              cwd=root, env=CHILD_ENV, bufsize=0) as child:
            try:
                streams.register(child.stdout, selectors.EVENT_READ, stdout)
                streams.register(child.stderr, selectors.EVENT_READ, stderr)
                while streams.get_map():
                    for key, _ in streams.select(remaining()):
                        available = OBSERVATION_LIMIT - len(stdout) - len(stderr)
                        chunk = os.read(key.fd, min(8192, available + 1))
                        if not chunk:
                            streams.unregister(key.fileobj)
                        elif len(chunk) > available:
                            raise ValueError("checker observation exceeds byte limit")
                        else:
                            key.data.extend(chunk)
                exit_code = child.wait(timeout=remaining())
            finally:
                if child.poll() is None:
                    child.kill()
    return bytes(stdout), bytes(stderr), exit_code


def run_checker(executable, files, roster):
    program, = re.findall(rb"<<'PY'\n(.*?)\nPY(?:\n|$)", files[CHECKER], re.S)
    with tempfile.TemporaryDirectory(prefix="verifier-properties-") as directory:
        root = Path(directory)
        for name in (REGISTRY, WORKFLOW):
            target = root / name
            target.parent.mkdir(parents=True)
            target.write_bytes(files[name])
        (root / "tests").mkdir()
        for name in roster:
            (root / "tests" / name).touch()
        stdout, stderr, exit_code = collect_checker([executable, *PYTHON_ARGS], program, root)
    return {
        "stdout": stdout.decode("utf-8"), "stderr": stderr.decode("utf-8"), "exit": exit_code,
        "stdout_descriptor": descriptor(stdout), "stderr_descriptor": descriptor(stderr),
    }


def associate(workflow, roster, observation):
    image_applies = b"/usr/bin/python3.12" in workflow
    groups = {
        "fixed_python_runner_image": {IMAGE_DIAGNOSTIC} if image_applies else set(),
        "canonical_route_exactly_once": {ROUTE_DIAGNOSTIC},
        "no_direct_ci_test_dispatch": {
            f"tests/{name} is directly invoked by .github/workflows/validate.yml; use the canonical registry"
            for name in roster
        },
    }
    unqualified = {f"tests/{name} is not invoked by scripts/verify-package.sh" for name in roster}
    raw_stderr = observation["stderr"]
    diagnostics = raw_stderr.splitlines()
    if observation["exit"] == 0:
        expected = f"check-validation-registry: ok ({len(roster)} tests; one canonical CI route)\n"
        if observation["stdout"] != expected or raw_stderr:
            raise ValueError("unexpected successful checker frame")
    elif observation["exit"] == 1:
        allowed = unqualified.union(*groups.values())
        if (observation["stdout"] or not diagnostics or "\n".join(diagnostics) + "\n" != raw_stderr
                or len(set(diagnostics)) != len(diagnostics) or not set(diagnostics) <= allowed):
            raise ValueError("unexpected negative checker frame")
    else:
        raise ValueError("checker invocation did not produce a recognized exit")

    properties = []
    for prop, (lines_in_source, inputs) in PROPERTY_CONTRACTS.items():
        lines = [index for index, text in enumerate(diagnostics, 1) if text in groups[prop]]
        outcome = "OWNER_DIAGNOSTIC_OBSERVED" if lines else "NO_OWNER_DIAGNOSTIC"
        if prop == "fixed_python_runner_image" and not image_applies:
            outcome = "CONDITION_NOT_APPLICABLE"
        properties.append({
            "id": prop, "owner": CHECKER, "source_lines_inclusive": list(lines_in_source),
            "node": NODE, "inputs": [CHECKER, REGISTRY, *inputs],
            "invalidated_by": [
                "canonical_node_binding", "local_execution_environment", "property_declaration",
                "owner_stdout_stderr_exit", CHECKER, REGISTRY, *inputs,
            ],
            "evidence_layer": "LOCAL_FIXED_CHECKER_PROCESS",
            "output": {"record_field": "observation", "stderr_lines_1_based": lines},
            "observation": outcome,
        })
    return properties


def capture(owner, source):
    candidate_pin = descriptor(HERE.read_bytes())
    files, roster = acquire(owner, source)
    executable, runtime = environment(owner)
    wg = owner.WG
    graph = wg.compile_verifier_graph_v1(files[REGISTRY], [f"tests/{name}" for name in roster], runtime)
    stream = wg.verifier_command_stream_v1(graph, files[REGISTRY])
    node, = (row for row in graph["nodes"] if row["id"] == NODE and row["command"] == CHECKER)
    evidence = run_checker(executable, files, roster)
    properties = associate(files[WORKFLOW], roster, evidence)
    if ((files, roster) != acquire(owner, source) or (executable, runtime) != environment(owner)
            or candidate_pin != descriptor(HERE.read_bytes())):
        raise ValueError("property inputs changed during capture")
    return {
        "schema": SCHEMA, "authority": "NONE",
        "scope": {
            "population": POPULATION, "canonical_node_execution": "UNQUALIFIED",
            "runtime_ci_image": "UNQUALIFIED", "selective_reuse": "UNQUALIFIED",
        },
        "candidate": candidate_pin,
        "owners": {name: SOURCE_PINS[name] for name in (QUALIFIER, COMPILER, CHECKER)},
        "inputs": {**{name: descriptor(data) for name, data in files.items()},
                   ROSTER: descriptor(wg.canonical_json_v1(roster))},
        "graph": {"digest": graph["digest"], "nodes": len(graph["nodes"]),
                  "command_stream": descriptor(stream), "ordering": graph["ordering"]},
        "node": {
            **{name: node[name] for name in ("id", "source_sha256", "byte_start", "byte_end",
                                           "requires", "environment_digest", "writer_resource_constraint",
                                           "invalidators", "evidence", "result_contract")},
            "ordinal": graph["nodes"].index(node),
        },
        "environment": runtime,
        "resource": {"snapshot": "PRIVATE_TEMPORARY_ORDINARY_FILES", "checker_timeout_seconds": CHECK_SECONDS,
                     "source_file_bytes_limit": SOURCE_LIMIT, "observation_bytes_limit": OBSERVATION_LIMIT},
        "properties": properties, "observation": evidence,
    }


def compare(owner, source, location):
    data = read_member(owner, location.parent, location.name, RECORD_LIMIT)
    wg = owner.WG
    record = wg.decode_strict_json_bytes(data, "candidate receipt")
    if type(record) is not dict or record.get("schema") != SCHEMA:
        raise ValueError("unsupported candidate receipt schema")
    rows = record.get("properties")
    if type(rows) is not list or any(type(row) is not dict or type(row.get("id")) is not str for row in rows):
        raise ValueError("missing or malformed property associations")
    ids = [row["id"] for row in rows]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate property association")
    if set(ids) != set(PROPERTY_CONTRACTS):
        raise ValueError("missing or extra property association")
    if ids != list(PROPERTY_CONTRACTS):
        raise ValueError("property association order differs")
    current = capture(owner, source)
    if data != wg.canonical_json_v1(current) + b"\n":
        raise ValueError("stale or altered candidate evidence")
    return {
        "schema": SCHEMA, "relation": "SAME_PROSPECTIVE_PROPERTY_EVIDENCE",
        "population": POPULATION, "authority": "NONE", "candidate_receipt": descriptor(data),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=("capture", "compare"))
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()
    if (args.operation == "compare") != (args.receipt is not None):
        parser.error("compare requires a receipt and capture takes no receipt")
    try:
        owner = qualifier()
        if args.operation == "capture":
            output = capture(owner, args.repo_root)
        else:
            output = compare(owner, args.repo_root, args.receipt)
        data = owner.WG.canonical_json_v1(output) + b"\n"
        if len(data) > RECORD_LIMIT:
            raise ValueError("candidate result exceeds byte limit")
        sys.stdout.buffer.write(data)
    except (OSError, ValueError, subprocess.TimeoutExpired) as exc:
        print(f"verifier property candidate: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
