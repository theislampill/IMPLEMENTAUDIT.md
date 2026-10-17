#!/usr/bin/env python3
"""Capture an optional legacy/DAG verifier run without changing its registry.

This transport imports the single graph compiler. It does not own a second
registry, choose parallel tests, supply release authority, or install anything.
"""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("work_graph", ROOT / "skills/implementaudit/scripts/compile-work-graph.py")
WG = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(WG)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def source_identity():
    def git(*args):
        return subprocess.check_output(["git", *args], cwd=ROOT)
    names = git("ls-files", "-z").split(b"\0")
    files = []
    for name in names:
        if not name:
            continue
        path = ROOT / os.fsdecode(name)
        data = os.fsencode(os.readlink(path)) if path.is_symlink() else path.read_bytes() if path.is_file() else b"MISSING"
        files.append([os.fsdecode(name), sha(data)])
    return dict(head=git("rev-parse", "HEAD").decode().strip(), tree=git("rev-parse", "HEAD^{tree}").decode().strip(),
                tracked_source_digest=sha(WG.canonical_json_v1(files)),
                status_digest=sha(git("status", "--porcelain=v1", "-z", "--untracked-files=all")))


def compare(left, right, out):
    a, b = (json.loads((p / "result.json").read_bytes()) for p in (left, right))
    checks = dict(same_source=a["before"] == b["before"] == a["after"] == b["after"],
                  same_registry=a["registry_sha256"] == b["registry_sha256"],
                  same_environment=a["environment"] == b["environment"],
                  same_exit=a["exit"] == b["exit"],
                  same_stdout=(left / "stdout.log").read_bytes() == (right / "stdout.log").read_bytes(),
                  same_stderr=(left / "stderr.log").read_bytes() == (right / "stderr.log").read_bytes(),
                  route_pair={a["mode"], b["mode"]} == {"legacy", "dag"})
    result = dict(schema="implementaudit.verifier-correspondence.v1", checks=checks,
                  raw_observables_equal=all(checks.values()), normalization="NONE_RAW_BYTES",
                  evidence_semantics="NODE_AND_WHOLE_PROCESS_ONLY; TRANSITIVE_OUTPUT_ARTIFACT_SEMANTICS_UNQUALIFIED",
                  canonical_conversion="NOT_PERFORMED", retirement="NOT_PERFORMED", authority="NONE")
    out.write_bytes(WG.canonical_json_v1(result) + b"\n")
    print(json.dumps(result, sort_keys=True))
    return 0 if all(checks.values()) else 1


def run(mode, output):
    output.mkdir(parents=True, exist_ok=False)
    before = source_identity()
    environment = dict(platform=platform.platform(), python=sys.version,
                       python_executable=sys.executable,
                       bash=subprocess.check_output(["bash", "--version"]).decode().splitlines()[0],
                       git=subprocess.check_output(["git", "--version"]).decode().strip(),
                       selected_environment={k: os.environ.get(k) for k in ("PATH", "LANG", "LC_ALL", "TZ", "PYTHONDONTWRITEBYTECODE")})
    registry = (ROOT / "scripts/verify-package.sh").read_bytes()
    tests = WG.verifier_registered_tests_v1(registry)
    graph = WG.compile_verifier_graph_v1(registry, tests, environment)
    actual_tests = sorted(p.relative_to(ROOT).as_posix() for p in (ROOT / "tests").glob("*.test.sh"))
    registration_complete = actual_tests == tests
    (output / "mapping.json").write_bytes(WG.canonical_json_v1(graph) + b"\n")
    with tempfile.TemporaryDirectory(prefix="r0035-verifier-stream-") as temporary:
        stream = Path(temporary) / "commands.bin"
        stream.write_bytes(WG.verifier_command_stream_v1(graph, registry))
        if mode == "legacy":
            command = ["bash", "scripts/verify-package.sh"]
        else:
            command = ["bash", "scripts/run-work-graph-verifier.sh", str(stream), str(output / "nodes.tsv"), str(len(graph["nodes"])), sha(stream.read_bytes())]
        started = time.monotonic()
        with (output / "stdout.log").open("wb") as stdout, (output / "stderr.log").open("wb") as stderr:
            process = subprocess.run(command, cwd=ROOT, stdout=stdout, stderr=stderr)
            # Retain the actual nested exit before any source/trace/JSON work.
            # A later wrapper error cannot silently erase a completed verdict.
            with (output / "exit-code.txt").open("w") as terminal:
                terminal.write(str(process.returncode) + "\n")
                terminal.flush()
                os.fsync(terminal.fileno())
    after = source_identity()
    observed = {}
    if mode == "dag":
        for line in (output / "nodes.tsv").read_text().splitlines():
            name, state = line.split("\t")
            observed[name] = state
    node_results = []
    for n in graph["nodes"]:
        state = observed.get(n["id"])
        status = "PASS" if state == "PASS" else ("INTERRUPTED" if process.returncode < 0 else "FAIL") if state == "START" else "UNSETTLED"
        node_results.append(dict(node=n["id"], status=status, terminal=state is not None))
    result = dict(schema="implementaudit.verifier-run.v1", mode=mode, command=command[:2],
                  before=before, after=after, environment=environment,
                  registry_sha256=sha(registry), graph_digest=graph["digest"],
                  mapped_nodes=len(graph["nodes"]), registered_tests=len(tests),
                  registration_complete=registration_complete,
                  exit=process.returncode, elapsed_ms=int((time.monotonic() - started) * 1000),
                  stdout_sha256=sha((output / "stdout.log").read_bytes()), stderr_sha256=sha((output / "stderr.log").read_bytes()),
                  nodes=node_results, authority="NONE")
    (output / "result.json").write_bytes(WG.canonical_json_v1(result) + b"\n")
    print(json.dumps({k: result[k] for k in ("mode", "exit", "elapsed_ms", "mapped_nodes", "registered_tests", "registration_complete", "stdout_sha256", "stderr_sha256")}, sort_keys=True))
    return process.returncode if process.returncode >= 0 else 128 - process.returncode


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=["legacy", "dag", "compare"])
    parser.add_argument("paths", nargs="+", type=Path)
    args = parser.parse_args()
    try:
        if args.mode == "compare" and len(args.paths) == 3:
            return compare(*args.paths)
        if args.mode != "compare" and len(args.paths) == 1:
            return run(args.mode, args.paths[0].resolve())
        parser.error("run takes one fresh output directory; compare takes two run directories and a fresh result path")
    except (OSError, WG.WorkGraphError, subprocess.CalledProcessError) as exc:
        print("work-graph-verifier: " + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
