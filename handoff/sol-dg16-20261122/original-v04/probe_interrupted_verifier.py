"""Capture a self-terminating benign fixture through the exact current verifier owners."""

import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile


PRODUCT = "51416b2f156b341c4a5f09029e2c6ceb5b30b1e7"
TREE = "9c3913ceaa95f3f36b0377fe2dba4a302afcba89"
DRIVER = "scripts/qualify-work-graph-verifier.py"
RUNNER = "scripts/run-work-graph-verifier.sh"
COMPILER = "skills/implementaudit/scripts/compile-work-graph.py"
SOURCES = {
    DRIVER: "79e3250a654abff1c5c326908875da1fea575686bdfb0c1a291c73bc525ed33b",
    RUNNER: "45e569b491d90b84929623b1966b03c7abc0b2c57f739c6b8fe23a58baab3ea9",
    COMPILER: "ac4cc4180b1d4225b36252080245c5afd6824aaae5624b784b06e49a763bf772",
}
# The two capture routes each create their own dedicated verifier shell.
# The fixture sends TERM only to that shell's own PID. No process is located externally.
REGISTRY = b"""#!/usr/bin/env bash
set -euo pipefail
printf 'ordinary verifier interruption fixture started\\n'
printf 'ordinary verifier interruption fixture diagnostic\\n' >&2
kill -TERM "$$"

bash scripts/generate-readme-diagrams.sh --check
bash tests/sample.test.sh
git diff --check
printf 'verify-package: ok\\n'
"""
STDOUT = b"ordinary verifier interruption fixture started\n"
STDERR = b"ordinary verifier interruption fixture diagnostic\n"
MAX_PACKET = 1024 * 1024


def require(condition, label):
    if not condition:
        raise ValueError(label)


def pin(raw):
    return {"bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}


def dump(data):
    return (json.dumps(data, sort_keys=True, indent=2) + "\n").encode()


def git_run(root, *args):
    return subprocess.check_output(["git", "-c", "core.hooksPath=/dev/null", *args], cwd=root,
                                   stderr=subprocess.PIPE, timeout=10)


def collect(capture, process, mode):
    actual_exit = (capture / "exit-code.txt").read_bytes()
    stdout = (capture / "stdout.log").read_bytes()
    stderr = (capture / "stderr.log").read_bytes()
    require(actual_exit == b"-15\n" and process.returncode == 143
            and stdout == STDOUT and stderr == STDERR,
            f"{mode}: retained={actual_exit.strip()!r}, wrapper={process.returncode}, "
            f"stdout_same={stdout == STDOUT}({len(stdout)}), stderr_same={stderr == STDERR}({len(stderr)})")
    outcome_raw = (capture / "result.json").read_bytes()
    result = json.loads(outcome_raw)
    require(result["mode"] == mode and result["exit"] == -15 and result["authority"] == "NONE"
            and result["registration_complete"] and len(result["nodes"]) == 5, "actual typed capture")
    nodes = result["nodes"]
    expected = [{"node": node["node"], "status": "INTERRUPTED" if mode == "dag" and i == 0 else "UNSETTLED",
                 "terminal": mode == "dag" and i == 0} for i, node in enumerate(nodes)]
    require(nodes == expected and nodes[0]["node"] == "PRELUDE", "interrupted and unsettled nodes")
    trace = None if mode == "legacy" else (capture / "nodes.tsv").read_bytes()
    require(trace == (None if mode == "legacy" else b"PRELUDE\tSTART\n"), "actual incomplete trace shape")
    require(result["stdout_sha256"] == pin(stdout)["sha256"] and result["stderr_sha256"] == pin(stderr)["sha256"],
            "owner raw stream pins")
    return {
        "mode": mode, "driver_process_returncode": process.returncode, "retained_exit": -15,
        "stdout": {"text":stdout.decode(),**pin(stdout)}, "stderr": {"text":stderr.decode(),**pin(stderr)},
        "trace": None if trace is None else {"text":trace.decode(),**pin(trace)},
        "exit_code_file": pin(actual_exit), "result": pin(outcome_raw), "nodes": nodes,
        "owner_result_schema": result["schema"], "authority": result["authority"],
    }


def run_posix(packet):
    require(os.name == "posix" and os.geteuid() != 0 and set(packet) == set(SOURCES),
            "ordinary unprivileged POSIX fixture required")
    copies = {}
    for name, encoded in packet.items():
        raw = base64.b64decode(encoded, validate=True)
        require(pin(raw)["sha256"] == SOURCES[name], "exact owner input pin")
        copies[name] = raw
    result = None
    with tempfile.TemporaryDirectory(prefix="dg16-v04-benign-") as scratch:
        temp = Path(scratch)
        tools = temp / "bin"
        tools.mkdir(mode=0o700)
        interpreter = Path(sys.executable).resolve()
        require(interpreter.is_file(), "already installed fixture Python interpreter")
        (tools / "python").symlink_to(interpreter)
        environment = dict(os.environ, PATH=str(tools) + os.pathsep + os.environ.get("PATH", os.defpath))
        subject = temp / "subject"
        subject.mkdir()
        for name, raw in {**copies, "scripts/verify-package.sh": REGISTRY,
                          "scripts/generate-readme-diagrams.sh": b"#!/usr/bin/env bash\nprintf 'unreached generator\\n'\n",
                          "tests/sample.test.sh": b"#!/usr/bin/env bash\nprintf 'unreached sample\\n'\n"}.items():
            path = subject / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(raw)
        git_run(subject, "init", "-q")
        git_run(subject, "add", ".")
        git_run(subject, "-c", "user.name=DG16 Fixture", "-c", "user.email=fixture@example.test",
                "-c", "commit.gpgsign=false", "commit", "-qm", "one benign self-interrupting verifier fixture")
        before = git_run(subject, "rev-parse", "HEAD", "HEAD^{tree}").decode().splitlines()
        paths = {mode: temp / ("capture-" + mode) for mode in ("legacy", "dag")}
        observed = {}
        for mode, path in paths.items():
            proc = subprocess.run([sys.executable, "-B", DRIVER, mode, str(path)], cwd=subject,
                                  stdin=subprocess.DEVNULL, capture_output=True, timeout=25, env=environment)
            if not (path / "result.json").is_file():
                raise ValueError(f"{mode} actual capture incomplete: return {proc.returncode}; "
                                 + proc.stderr.decode("utf-8", "replace").splitlines()[-1][:140]
                                 if proc.stderr else f"{mode} actual capture incomplete: return {proc.returncode}")
            observed[mode] = collect(path, proc, mode)
        output = temp / "raw-comparison.json"
        receiver = subprocess.run([sys.executable, "-B", DRIVER, "compare", str(paths["legacy"]),
                                   str(paths["dag"]), str(output)], cwd=subject, stdin=subprocess.DEVNULL,
                                  capture_output=True, timeout=25)
        require(output.is_file(), "actual capture comparator did not issue a scoped record")
        record_raw = output.read_bytes()
        record = json.loads(record_raw)
        require(receiver.returncode == 0 and record["raw_observables_equal"]
                and all(record["checks"].values()) and record["normalization"] == "NONE_RAW_BYTES"
                and record["authority"] == "NONE" and record["canonical_conversion"] == "NOT_PERFORMED",
                "actual retained comparator scope")
        require(git_run(subject, "rev-parse", "HEAD", "HEAD^{tree}").decode().splitlines() == before
                and not git_run(subject, "status", "--porcelain"), "disposable fixture changed")
        result = {
            "schema": "dg16.v04.actual-benign-interrupted-receiving.v1",
            "exact_runtime_owners_from": {"commit": PRODUCT, "tree": TREE},
            "owner_source_pins": {name: pin(raw) for name, raw in copies.items()},
            "fixture_identity": {"commit": before[0], "tree": before[1], "registry": pin(REGISTRY)},
            "controlled_input_scope": "ONE_LOCAL_BENIGN_SELF_INTERRUPT_PER_ROUTE",
            "child_python_binding": "EXISTING_UBUNTU_PYTHON_UNDER_DISPOSABLE_PATH_ALIAS",
            "captures": observed,
            "actual_current_raw_comparator": {"process_exit": receiver.returncode, "result": pin(record_raw),
                                              "raw_observables_equal": True, "coverage": record["record_coverage"],
                                              "authority": record["authority"],
                                              "evidence_semantics": record["evidence_semantics"]},
            "full_original_M2_receiver_executed_here": False,
            "full_original_completion_admitted": False,
            "original_awards": [], "native_or_protected_operation": False,
        }
    require(not temp.exists(), "owned fixture cleanup")
    result["owned_fixture_removed"] = True
    return result


def main():
    if sys.argv[1:] == ["--ordinary-posix"]:
        raw = sys.stdin.buffer.read(MAX_PACKET + 1)
        require(len(raw) <= MAX_PACKET, "exact source input packet bound")
        sys.stdout.buffer.write(dump(run_posix(json.loads(raw))))
        return
    require(sys.argv[1:] == ["--wsl"], "use the selected ordinary Ubuntu runtime")
    packet = {}
    for path, digest in SOURCES.items():
        raw = subprocess.check_output(["git", "cat-file", "blob", f"{PRODUCT}:{path}"])
        require(pin(raw)["sha256"] == digest, "exact immutable product input")
        packet[path] = base64.b64encode(raw).decode()
    receiver = subprocess.run(["wsl.exe", "--distribution", "Ubuntu", "--exec", "python3",
                               "-I", "-B", "-c", Path(__file__).read_text(encoding="utf-8"), "--ordinary-posix"],
                              input=dump(packet), capture_output=True, timeout=80)
    if receiver.returncode:
        raise ValueError(receiver.stderr.decode("utf-8", "replace").splitlines()[-1][:240])
    result = json.loads(receiver.stdout)
    require(result["owned_fixture_removed"] and not result["native_or_protected_operation"],
            "actual benign fixture post-state")
    sys.stdout.buffer.write(dump(result))


if __name__ == "__main__":
    main()
