#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
core="${ROUTE_CORE:-$repo_root/skills/implementaudit/scripts/route-transaction.py}"
case_filter="${ROUTE_HISTORY_CASE:-all}"

python "$core" --help >/dev/null

python - "$core" "$case_filter" <<'PY'
import contextlib
import importlib.util
import io
import json
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path

spec = importlib.util.spec_from_file_location("route_transaction", sys.argv[1])
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
case_filter = sys.argv[2]


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8") + b"\n"


def route_record(repo, index, predecessor, *, malformed_bytes=False):
    base = {
        "schema": module.RECORD_SCHEMA,
        "predicate_version": module.PREDICATE_VERSION,
        "controller_id": "controller-route-capacity",
        "claim_id": "0123456789abcdef0123456789abcdef",
        "explicit_run_root": str(repo / ".IMPLEMENTAUDIT" / "runs" / "capacity-test"),
        "continuity_generation": f"G{index + 1:04X}",
        "continuity_receipt": f"capacity-receipt-{index + 1}",
        "host_id": "codex",
        "host_session_id": "capacity-session",
        "host_binding_generation": f"G{index + 1:04X}",
        "host_correlation_id": "sha256:" + "1" * 64,
        "boundary": {
            "kind": "manual-resume",
            "event_id": f"capacity-{index + 1}",
            "digest": "sha256:" + "2" * 64,
        },
        "scope": {"identity": "capacity validation", "digest": "sha256:" + "3" * 64},
        "action": {
            "identity": "capacity action",
            "class": "PURE_BOUNDED_READ_OR_VALIDATION",
            "argv": ["route-trigger", "STALE_CONTEXT_RECONSTRUCTION"],
            "digest": "sha256:" + "4" * 64,
        },
        "evidence": {},
        "inputs": [],
        "package": {},
        "child_source": {},
        "decision": "NOT_REQUIRED",
        "classification": "MECHANICALLY_NOT_REQUIRED",
        "invalidators": [],
        "expiry_fingerprint": "sha256:" + "5" * 64,
        "expires_on": module.EXPIRES_ON,
        "predecessor_record_oid": predecessor,
        "route_transaction_id": None,
        "obligation_id": None,
        "route_state": None,
        "child_lifecycle_owned": False,
        "consumed_record_oid": None,
    }
    record = {**base, "record_identity": module.digest_json(base)}
    raw = canonical(record)
    if malformed_bytes:
        raw = (json.dumps(record, sort_keys=True, indent=2) + "\n").encode("utf-8")
    return record, raw


def write_blob(repo, raw):
    completed = subprocess.run(
        ["git", "hash-object", "-w", "--stdin"],
        cwd=repo,
        input=raw,
        capture_output=True,
        check=True,
    )
    return completed.stdout.decode("ascii").strip()


def build_real_chain(repo, count, *, malformed_tail=False):
    predecessor = None
    head = None
    head_record = None
    for index in range(count):
        record, raw = route_record(
            repo,
            index,
            predecessor,
            malformed_bytes=malformed_tail and index == 0,
        )
        predecessor = write_blob(repo, raw)
        head = predecessor
        head_record = record
    return head, head_record


def expect_unavailable(action, message):
    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        try:
            action()
        except SystemExit as exc:
            if exc.code != 2:
                raise AssertionError(f"unexpected fail-closed exit {exc.code}") from exc
        else:
            raise AssertionError(f"expected fail-closed result containing {message!r}")
    rows = [row for row in output.getvalue().splitlines() if row]
    if not rows:
        raise AssertionError("fail-closed result emitted no canonical payload")
    result = json.loads(rows[-1])
    if result.get("status") != "UNAVAILABLE" or message not in result.get("error", ""):
        raise AssertionError(f"wrong fail-closed result: {result}")


def is_git_call(command, *wanted):
    argv = [str(item) for item in command]
    return len(argv) >= len(wanted) + 1 and tuple(argv[1 : len(wanted) + 1]) == wanted


class RecordingStdin:
    def __init__(self, *, flush_delay=0.0, flush_error=None):
        self.closed = False
        self.writes = []
        self.flush_delay = flush_delay
        self.flush_error = flush_error
        self.release_event = threading.Event()

    def write(self, raw):
        self.writes.append(raw)
        return len(raw)

    def flush(self):
        if self.flush_delay:
            self.release_event.wait(self.flush_delay)
        if self.flush_error is not None:
            raise self.flush_error
        return None

    def close(self):
        self.closed = True


class ScriptedStdout:
    def __init__(self, header, reads=(), *, header_delay=0.0, header_error=None):
        self.header = header
        self.reads = list(reads)
        self.header_delay = header_delay
        self.header_error = header_error
        self.closed = False
        self.release_event = threading.Event()

    def readline(self, _limit):
        if self.header_delay:
            self.release_event.wait(self.header_delay)
        if self.header_error is not None:
            raise self.header_error
        return self.header

    def read(self, _size):
        if not self.reads:
            return b""
        action = self.reads.pop(0)
        if isinstance(action, tuple):
            delay, action = action
            self.release_event.wait(delay)
        if isinstance(action, BaseException):
            raise action
        return action

    def close(self):
        self.closed = True


class FakeBatchProcess:
    def __init__(self, stdout, *, stdin=None):
        self.stdin = stdin or RecordingStdin()
        self.stdout = stdout
        self.killed = False
        self.wait_calls = 0

    def poll(self):
        return -9 if self.killed else None

    def wait(self, timeout=None):
        self.wait_calls += 1
        if not self.killed:
            raise subprocess.TimeoutExpired("fake git cat-file --batch", timeout)
        return -9

    def kill(self):
        self.killed = True
        self.stdin.release_event.set()
        self.stdout.release_event.set()


def reader_failure_control(stdout, message, *, elapsed_budget=None, stdin=None):
    oid = "a" * 40
    process = FakeBatchProcess(stdout, stdin=stdin)
    original_popen = subprocess.Popen
    original_elapsed = module.MAX_ROUTE_LINEAGE_ELAPSED_SECONDS
    subprocess.Popen = lambda *_args, **_kwargs: process
    if elapsed_budget is not None:
        module.MAX_ROUTE_LINEAGE_ELAPSED_SECONDS = elapsed_budget
    started = time.monotonic()
    try:
        with module.RouteObjectReader(Path("C:/route-capacity-transport-fixture")) as reader:
            expect_unavailable(lambda: reader.read(oid, "transport fixture"), message)
    finally:
        subprocess.Popen = original_popen
        module.MAX_ROUTE_LINEAGE_ELAPSED_SECONDS = original_elapsed
    elapsed = time.monotonic() - started
    if (
        not process.killed
        or not process.stdin.closed
        or not process.stdout.closed
        or process.wait_calls == 0
    ):
        raise AssertionError("route transport failure did not kill and close its batch process")
    return elapsed


def transport_deadline_controls():
    oid = b"a" * 40
    raw = b"{}\n"
    header = oid + b" blob " + str(len(raw)).encode("ascii") + b"\n"
    for label, stdout, stdin in (
        (
            "flush",
            ScriptedStdout(header, (raw, b"\n")),
            RecordingStdin(flush_delay=0.25),
        ),
        ("header", ScriptedStdout(header, (raw, b"\n"), header_delay=0.25), None),
        ("body", ScriptedStdout(header, ((0.25, raw), b"\n")), None),
    ):
        elapsed = reader_failure_control(
            stdout,
            "route history resource budget exceeded: elapsed-work",
            elapsed_budget=0.05,
            stdin=stdin,
        )
        if elapsed >= 0.18:
            raise AssertionError(f"stalled {label} read exceeded its enforceable deadline: {elapsed:.3f}s")


def transport_error_controls():
    oid = b"a" * 40
    raw = b"{}\n"
    header = oid + b" blob " + str(len(raw)).encode("ascii") + b"\n"
    cases = (
        (
            "flush",
            ScriptedStdout(header, (raw, b"\n")),
            RecordingStdin(flush_error=OSError("flush transport failed")),
        ),
        ("header", ScriptedStdout(header, header_error=OSError("header transport failed")), None),
        ("body", ScriptedStdout(header, (raw[:1], OSError("body transport failed"))), None),
        ("trailer", ScriptedStdout(header, (raw, OSError("trailer transport failed"))), None),
    )
    for label, stdout, stdin in cases:
        reader_failure_control(
            stdout,
            "transport fixture blob is unreadable",
            stdin=stdin,
        )


def transport_protocol_controls():
    oid = b"a" * 40
    cases = (
        ("missing", ScriptedStdout(oid + b" missing\n")),
        ("nonblob", ScriptedStdout(oid + b" tree 3\n", (b"abc", b"\n"))),
        ("bad-trailer", ScriptedStdout(oid + b" blob 3\n", (b"{}\n", b"x"))),
    )
    for label, stdout in cases:
        reader_failure_control(stdout, "transport fixture blob is unreadable")


def valid_capacity_and_process_control():
    with tempfile.TemporaryDirectory() as raw_dir:
        repo = Path(raw_dir)
        subprocess.run(["git", "init", "-q", str(repo)], check=True)
        head, head_record = build_real_chain(repo, 120)

        original_run = subprocess.run
        original_popen = subprocess.Popen
        calls = {"legacy_blob": 0, "batch": 0}

        def observed_run(command, *args, **kwargs):
            if is_git_call(command, "cat-file", "blob"):
                calls["legacy_blob"] += 1
            return original_run(command, *args, **kwargs)

        def observed_popen(command, *args, **kwargs):
            if is_git_call(command, "cat-file", "--batch"):
                calls["batch"] += 1
            return original_popen(command, *args, **kwargs)

        subprocess.run = observed_run
        subprocess.Popen = observed_popen
        try:
            module.validate_route_record_semantics(
                repo,
                "controller-route-capacity",
                head,
                head_record,
            )
        finally:
            subprocess.run = original_run
            subprocess.Popen = original_popen

        if calls != {"legacy_blob": 0, "batch": 1}:
            raise AssertionError(f"route history did not use one bounded batch reader: {calls}")


def exactly_once_history_decode_control():
    with tempfile.TemporaryDirectory() as raw_dir:
        repo = Path(raw_dir)
        subprocess.run(["git", "init", "-q", str(repo)], check=True)
        head, head_record = build_real_chain(repo, 120)
        original_decode = module.decoded_artifact
        decoded = {}

        def observed_decode(raw, label):
            if label == "route record predecessor":
                identity = module.hashlib.sha256(raw).hexdigest()
                decoded[identity] = decoded.get(identity, 0) + 1
            return original_decode(raw, label)

        module.decoded_artifact = observed_decode
        try:
            module.validate_route_record_semantics(
                repo,
                "controller-route-capacity",
                head,
                head_record,
            )
        finally:
            module.decoded_artifact = original_decode
        if len(decoded) != 119 or any(count != 1 for count in decoded.values()):
            raise AssertionError(
                f"route history did not decode each predecessor exactly once: {decoded}"
            )


def malformed_deep_tail_control():
    with tempfile.TemporaryDirectory() as raw_dir:
        repo = Path(raw_dir)
        subprocess.run(["git", "init", "-q", str(repo)], check=True)
        head, head_record = build_real_chain(repo, 120, malformed_tail=True)
        expect_unavailable(
            lambda: module.validate_route_record_semantics(
                repo,
                "controller-route-capacity",
                head,
                head_record,
            ),
            "route record bytes are not exact canonical JSON",
        )


class MappingReader:
    def __init__(self, records):
        self.records = records

    def read(self, oid, label):
        try:
            return self.records[oid]
        except KeyError as exc:
            raise AssertionError(f"unexpected mapping read {label}: {oid}") from exc


def deep_cycle_control():
    repo = Path("C:/route-capacity-cycle-fixture")
    oids = [f"{index + 1:040x}" for index in range(120)]
    records = {}
    parsed = {}
    predecessor = None
    for index, oid in enumerate(oids):
        record, raw = route_record(repo, index, predecessor)
        records[oid] = raw
        parsed[oid] = record
        predecessor = oid

    deep_tail_oid = oids[0]
    deep_tail = dict(parsed[deep_tail_oid])
    deep_tail["predecessor_record_oid"] = oids[10]
    deep_tail_base = {key: value for key, value in deep_tail.items() if key != "record_identity"}
    deep_tail["record_identity"] = module.digest_json(deep_tail_base)
    records[deep_tail_oid] = canonical(deep_tail)
    parsed[deep_tail_oid] = deep_tail

    expect_unavailable(
        lambda: module.validate_route_record_semantics(
            repo,
            "controller-route-capacity",
            oids[-1],
            parsed[oids[-1]],
            object_reader=MappingReader(records),
        ),
        "route record predecessor chain contains a cycle",
    )


def resource_budget_controls():
    with tempfile.TemporaryDirectory() as raw_dir:
        repo = Path(raw_dir)
        subprocess.run(["git", "init", "-q", str(repo)], check=True)
        head, _ = build_real_chain(repo, 120)
        route_ref = "refs/implementaudit/route-decisions/controller-route-capacity"
        subprocess.run(["git", "update-ref", route_ref, head], cwd=repo, check=True)

        original = {
            "record_count": module.MAX_ROUTE_LINEAGE_RECORDS,
            "per_record": module.MAX_ROUTE_RECORD_BYTES,
            "cumulative": module.MAX_ROUTE_LINEAGE_BYTES,
            "elapsed": module.MAX_ROUTE_LINEAGE_ELAPSED_SECONDS,
        }
        controls = (
            ("record-count", "MAX_ROUTE_LINEAGE_RECORDS", 119, "record_count"),
            ("per-record-bytes", "MAX_ROUTE_RECORD_BYTES", 1, "per_record"),
            ("cumulative-bytes", "MAX_ROUTE_LINEAGE_BYTES", 1, "cumulative"),
            ("elapsed-work", "MAX_ROUTE_LINEAGE_ELAPSED_SECONDS", -1.0, "elapsed"),
        )
        try:
            for label, name, value, original_key in controls:
                setattr(module, name, value)
                original_run = subprocess.run
                update_attempts = 0

                def observed_run(command, *args, **kwargs):
                    nonlocal update_attempts
                    if is_git_call(command, "update-ref"):
                        update_attempts += 1
                    return original_run(command, *args, **kwargs)

                subprocess.run = observed_run
                try:
                    expect_unavailable(
                        lambda: module.current_ref(repo, "controller-route-capacity"),
                        f"route history resource budget exceeded: {label}",
                    )
                finally:
                    subprocess.run = original_run
                    setattr(module, name, original[original_key])
                if update_attempts:
                    raise AssertionError(f"{label} budget failure attempted route CAS")
                current = subprocess.check_output(
                    ["git", "rev-parse", "--verify", route_ref], cwd=repo, text=True
                ).strip()
                if current != head:
                    raise AssertionError(f"{label} budget failure changed the canonical route ref")
        finally:
            module.MAX_ROUTE_LINEAGE_RECORDS = original["record_count"]
            module.MAX_ROUTE_RECORD_BYTES = original["per_record"]
            module.MAX_ROUTE_LINEAGE_BYTES = original["cumulative"]
            module.MAX_ROUTE_LINEAGE_ELAPSED_SECONDS = original["elapsed"]


cases = {
    "valid-process": valid_capacity_and_process_control,
    "decode-once": exactly_once_history_decode_control,
    "deep-cycle": deep_cycle_control,
    "malformed-tail": malformed_deep_tail_control,
    "resource-budgets": resource_budget_controls,
    "transport-deadline": transport_deadline_controls,
    "transport-errors": transport_error_controls,
    "transport-protocol": transport_protocol_controls,
}
if case_filter != "all" and case_filter not in cases:
    raise SystemExit(f"unknown ROUTE_HISTORY_CASE={case_filter}")
selected = cases.items() if case_filter == "all" else ((case_filter, cases[case_filter]),)
for name, test in selected:
    test()
    print(f"route-history-capacity.test: {name} GREEN")
PY
