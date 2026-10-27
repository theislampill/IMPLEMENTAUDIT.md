#!/usr/bin/env python3
"""PORTABLE process-crash and path-custody qualification of the pending owner.

Uses real H0/pending CLIs and constructed attribution only. The worker seams
import the actual owner: status denies observation/writes and crash exits
immediately around its real
pending.json os.replace. No native selector, registration, acceptance, JOIN,
or consumed scope is fabricated. This is not a power-loss/fsync guarantee.

Run from an integrated tests/ directory, or pass --repo-root for a proposal.
--evidence-dir must name a new directory; it retains every process result and
pending preimage, including unexpected failures. Without it a temp directory
is retained and its path is printed in the final JSON report.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import tarfile
import tempfile
import time
import traceback

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
PEER = Path("source-peers/native-runtime/skills/implementaudit/scripts")
OWNER = "fixture-owner"
SESSION = "portable-pending-session"
CEILING = {
    "authority": "NONE", "canonical_currentness": False,
    "recovery_authority": False, "epoch_authority": False,
    "effect_authority": False, "independent_children": "UNCHANGED",
    "actual_child_result_consumer": "UNQUALIFIED",
    "same_failed_scope_retry": "CONDITIONAL_UNQUALIFIED",
}
LIMITATIONS = [
    "Constructed H0 attribution only; host_activation_proven=false.",
    "Unresolved explicit resume deliveries are not physical occurrence proof.",
    "Private native selection remains absent; no reservation or accepted native JOIN is proved.",
    "Only process interruption/reload is tested, not power loss or directory-fsync durability.",
]


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def ceiling(value, *, decision=False):
    for key, expected in CEILING.items():
        require(value.get(key) == expected and type(value.get(key)) is type(expected), key)
    if decision:
        require(value["native_lifecycle"] == "NOT_CLAIMED", "native lifecycle promoted")
        require(value["native_producer_runtime_equivalence"] == "UNVERIFIED", "native equivalence promoted")


class StatusReadAudit:
    """Fixture-only read census: pathname opens plus one identity-bound FD wrapper."""
    def __init__(self, allowed):
        self.allowed = set(allowed)
        self.opened = []
        self.descriptors = {}
        self.wrapped = set()

    @staticmethod
    def stamp(info):
        return (info.st_dev, info.st_ino, info.st_mode, info.st_nlink,
                info.st_size, info.st_mtime_ns, info.st_ctime_ns)

    @staticmethod
    def readonly(flags):
        require(not flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND),
                "status attempted a writable open")

    def record_open(self, descriptor, path, flags):
        self.readonly(flags)
        path = Path(os.fsdecode(path))
        require(type(descriptor) is int and path in self.allowed and str(path) in self.opened,
                "descriptor has no admitted pathname open")
        observed = os.fstat(descriptor)
        require(stat.S_ISREG(observed.st_mode) and observed.st_nlink == 1
                and self.stamp(observed) == self.stamp(path.lstat()),
                "admitted descriptor differs from exact path")
        self.descriptors[descriptor] = (path, self.stamp(observed))
        self.wrapped.discard(descriptor)

    def __call__(self, event, args):
        if event == "open":
            path, mode_text, flags = args
            self.readonly(flags)
            if type(path) is int:
                require(path in self.descriptors and path not in self.wrapped,
                        "status used an unknown or repeated descriptor wrapper")
                name, expected = self.descriptors[path]
                try:
                    observed = self.stamp(os.fstat(path))
                    current = self.stamp(name.lstat())
                except OSError as error:
                    raise AssertionError("status descriptor is no longer current") from error
                require(observed == expected == current, "status descriptor identity changed")
                self.wrapped.add(path)
                return
            require(isinstance(path, (str, bytes, os.PathLike)) and Path(os.fsdecode(path)) in self.allowed,
                    "status read outside exact owner/binding/index/pending files: " + str(path))
            self.opened.append(os.fsdecode(path))
        elif event in ("os.listdir", "os.scandir", "os.rename", "os.remove", "os.rmdir",
                       "os.mkdir", "subprocess.Popen", "os.system", "socket.connect"):
            raise AssertionError("status attempted forbidden event: " + event)

def worker(mode, source_text, store_text, session, owner, action):
    """Fault/guard scheduling only; all pending semantics remain in source."""
    source, store = Path(source_text), Path(store_text)
    spec = importlib.util.spec_from_file_location("_portable_actual_pending", source)
    pending = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(pending)
    target = pending.state_path(store, session)
    require(target.is_relative_to(store), "fault target escaped fixture store")
    sys.argv = [str(source), "--store", str(store), "--session", session,
                "--owner-id", owner, action]
    if mode in ("before-replace", "after-replace"):
        actual_replace = pending.CORE.os.replace

        def scheduled_replace(src, dst, *args, **kwargs):
            if Path(dst) != target:
                return actual_replace(src, dst, *args, **kwargs)
            # CORE.atomic_json has flushed/fsynced its actual temp file here.
            if mode == "after-replace":
                actual_replace(src, dst, *args, **kwargs)
            sys.stderr.write("FAULT_REACHED " + mode + " " + str(target) + "\n")
            sys.stderr.flush()
            os._exit(91 if mode == "before-replace" else 92)

        pending.CORE.os.replace = scheduled_replace
        return pending.main()
    if mode == "pending-open-nonregular":
        require(action == "status", "open-boundary worker requires status")
        actual_lstat, actual_open = Path.lstat, os.open
        retained = target.with_name("retained-stored-json-open.pending.json")
        reached, opened_flags = [], []

        def scheduled_lstat(path, *args, **kwargs):
            info = actual_lstat(path, *args, **kwargs)
            if path == target and not reached:
                target.rename(retained)
                if hasattr(os, "mkfifo"):
                    os.mkfifo(target)
                else:
                    target.mkdir()
                reached.append(True)
            return info

        def observed_open(path, flags, *args, **kwargs):
            if Path(path) == target:
                opened_flags.append(flags)
            return actual_open(path, flags, *args, **kwargs)

        Path.lstat, os.open = scheduled_lstat, observed_open
        result = pending.main()
        require(reached and result == 2, "scheduled unsafe open did not refuse")
        require(all(flags & getattr(os, "O_NONBLOCK", 0) for flags in opened_flags)
                if hasattr(os, "O_NONBLOCK") else True, "unsafe open could block")
        sys.stderr.write(json.dumps({"pending_open_boundary": "REFUSED",
                                     "scheduled_kind": "fifo" if hasattr(os, "mkfifo") else "directory",
                                     "opened_flags": opened_flags}, sort_keys=True) + "\n")
        return result
    require(mode == "status-guard" and action == "status", "unknown worker mode")

    def forbidden(*args, **kwargs):
        raise AssertionError("status attempted observation, locking, or mutation")

    for name in ("refresh", "scan_source", "_scan_source_unheld", "record_signal",
                 "save", "nonprotected_code_identity"):
        setattr(pending, name, forbidden)
    pending.CORE.writer_lock = forbidden
    pending.CORE.atomic_json = forbidden
    allowed = {
        pending.CORE.owner_path(store),
        pending.CORE.state_path(store, "codex", session),
        pending.CORE.session_index_path(store, session),
    }
    if target.exists():
        allowed.add(target)
    audit = StatusReadAudit(allowed)
    actual_open = os.open

    def admitted_open(path, flags, *args, **kwargs):
        descriptor = actual_open(path, flags, *args, **kwargs)
        try:
            audit.record_open(descriptor, path, flags)
        except BaseException:
            os.close(descriptor)
            raise
        return descriptor

    sys.addaudithook(audit)
    os.open = admitted_open
    try:
        result = pending.main()
    finally:
        os.open = actual_open
    opened = audit.opened
    require(result == 0, "guarded status refused")
    require(len(opened) == len(allowed) and set(opened) == {str(p) for p in allowed},
            "status did not use one bounded read per expected custody file")
    sys.stderr.write(json.dumps({"status_guard": "PASS", "read_count": len(opened),
                                 "observations": 0, "writes": 0, "descriptor_wrappers": len(audit.wrapped)}, sort_keys=True) + "\n")
    return result


class Harness:
    def __init__(self, repo, evidence):
        self.repo, self.evidence = repo, evidence
        self.scripts = repo / PEER
        self.fixture = evidence / "constructed"
        self.store = self.fixture / "store"
        self.pending = self.store / "compaction-audits-v1" / sha(SESSION.encode()) / "pending.json"
        self.preimages = evidence / "preimages"
        self.preimages.mkdir()
        self.records, self.controls = [], []

    def mark(self, name):
        self.controls.append(name)
        print("PASS " + name, flush=True)

    def snapshot(self):
        """Include names, file bytes, metadata and directory metadata; omit atime."""
        result = {}
        for path in [self.store, *sorted(self.store.rglob("*"))]:
            info = path.lstat()
            result[str(path.relative_to(self.store))] = {
                "mode": info.st_mode, "inode": info.st_ino,
                "mtime_ns": info.st_mtime_ns, "ctime_ns": info.st_ctime_ns,
                "bytes": info.st_size if stat.S_ISREG(info.st_mode) else None,
                "sha256": sha(path.read_bytes()) if stat.S_ISREG(info.st_mode) else None,
            }
        return result

    def preserve(self, number, stage):
        # Unsafe-path controls must never follow a link or read a FIFO while
        # preserving the actual process boundary.
        if self.pending.is_symlink() or not self.pending.is_file():
            return None
        raw = self.pending.read_bytes()
        path = self.preimages / (f"{number:03d}-{stage}.pending.json")
        path.write_bytes(raw)
        return {"path": str(path.relative_to(self.evidence)), "bytes": len(raw), "sha256": sha(raw)}

    def call(self, action, data=None, *, script="compaction-audit-pending.py", args=None,
             mode=None, owner=OWNER, raw=None, expected_exit=0):
        number = len(self.records) + 1
        if args is None:
            args = ["--store", str(self.store), "--session", SESSION,
                    "--owner-id", owner, action]
        command = [sys.executable, "-B", str(self.scripts / script), *args]
        if mode:
            command = [sys.executable, "-B", str(Path(__file__).resolve()), "--worker", mode,
                       str(self.scripts / script), str(self.store), SESSION, owner, action]
        wire = raw if raw is not None else "" if data is None else json.dumps(data)
        record = {"number": number, "command": command, "input": wire,
                  "pending_before": self.preserve(number, "before")}
        started = time.monotonic()
        try:
            process = subprocess.run(command, input=wire, text=True, capture_output=True, timeout=15)
            record.update(exit=process.returncode, stdout=process.stdout, stderr=process.stderr)
        except subprocess.TimeoutExpired as error:
            record.update(timeout_seconds=15, stdout=str(error.stdout), stderr=str(error.stderr))
            raise
        finally:
            record["elapsed_seconds"] = round(time.monotonic() - started, 6)
            record["pending_after"] = self.preserve(number, "after")
            self.records.append(record)
            with (self.evidence / "process-records.jsonl").open("a", encoding="utf-8") as stream:
                stream.write(json.dumps(record, sort_keys=True) + "\n")
        require(process.returncode == expected_exit, "unexpected process result: " + json.dumps(record))
        if expected_exit in (91, 92):
            require(process.stdout == "" and "FAULT_REACHED " + mode in process.stderr,
                    "crash did not reach the scheduled atomic replacement")
            return None
        value = json.loads(process.stdout)
        if script == "compaction-audit-pending.py":
            ceiling(value, decision="decision" in value)
        return value

    def state(self):
        return json.loads(self.pending.read_bytes())

    def held(self, value):
        ceiling(value, decision=True)
        require(value["audit_state_required"] and value["state_dependent_decisions_held"],
                "outstanding obligation was silently cleared")
        require(value["decision"] == "AUDIT_STATE_REQUIRED" and not value["assigned_scope"],
                "unreserved pending scope changed")
        state = self.state()
        require(state["source"] is None and state["assignments"] == {}, "native state fabricated")
        require(all(row["consumed_version"] == 0 for row in state["observations"].values()),
                "unqualified scope was consumed")
        require(all(row["kind"] in ("UNRESOLVED_RESUME_OBSERVATION", "UNRESOLVED_SIGNAL")
                    and row["proof"]["logical_occurrence_count"] is None
                    and row["proof"]["delivery_count_is_not_occurrence_identity"] is True
                    for row in state["observations"].values()), "physical occurrence identity invented")
        return state

    def refused(self, name, action, data, reason, **options):
        before = self.snapshot()
        value = self.call(action, data, expected_exit=2, **options)
        require(value["status"] == "PENDING_OPERATION_REFUSED" and value["reason"] == reason,
                name + ": unexpected refusal " + json.dumps(value))
        require(before == self.snapshot(), name + ": refusal wrote fixture state")
        self.held(self.call("status"))
        self.mark(name)


def successor(before, after):
    """A resumed delivery changes only its version and the atomic state revision."""
    require(after["revision"] == before["revision"] + 1, "successor revision is incoherent")
    key = "unresolved-resume-" + sha(SESSION.encode())
    require(after["observations"][key]["version"] == before["observations"][key]["version"] + 1,
            "successor unresolved delivery version is incoherent")
    normalized = json.loads(json.dumps(after))
    normalized["revision"] = before["revision"]
    normalized["observations"][key]["version"] = before["observations"][key]["version"]
    require(normalized == before, "atomic successor altered unrelated pending state")


def materialize_selected_source(h):
    """Documented full frozen core plus all selected peer bytes; no native state.

    Only the pre-selection refusal is invoked from this source tree. It is not
    an admitted Git/controller/native composition and creates no Git refs.
    """
    commands = []

    def git(*args):
        command = ["git", "-C", str(h.repo), *args]
        process = subprocess.run(command, capture_output=True, timeout=15)
        commands.append({"command": command, "exit": process.returncode,
                         "stdout_bytes": len(process.stdout), "stdout_sha256": sha(process.stdout),
                         "stderr": process.stderr.decode("utf-8", errors="replace")})
        require(process.returncode == 0, "frozen source archive unavailable")
        return process.stdout

    head = git("rev-parse", "HEAD").decode().strip()
    archived = git("archive", "--format=tar", head, "skills", "source-peers")
    root = h.evidence / "constructed-source-tree"
    root.mkdir()
    with tarfile.open(fileobj=io.BytesIO(archived)) as stream:
        for member in stream.getmembers():
            path = Path(member.name)
            require(not path.is_absolute() and ".." not in path.parts
                    and (member.isfile() or member.isdir()), "unexpected archived source member")
        stream.extractall(root, filter="data")
    selected = []
    for group in ("native-runtime", "route-graph"):
        relative = Path("source-peers") / group / "SOURCE_MANIFEST.json"
        require((root / relative).read_bytes() == (h.repo / relative).read_bytes(),
                "working peer manifest differs from frozen HEAD")
        manifest = json.loads((root / relative).read_bytes())
        for entry in manifest["files"]:
            source, target = root / entry["path"], root / entry["materialized_path"]
            raw = source.read_bytes()
            require(raw == (h.repo / entry["path"]).read_bytes()
                    and len(raw) == entry["bytes"] and sha(raw) == entry["sha256"],
                    "manifested source bytes differ: " + entry["path"])
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(raw)
            target.chmod(int(entry["mode"], 8) & 0o777)
            require(target.read_bytes() == raw
                    and stat.S_IMODE(target.stat().st_mode) == (int(entry["mode"], 8) & 0o777),
                    "materialized source bytes or mode differ")
            selected.append({key: entry[key] for key in ("path", "materialized_path", "bytes", "sha256", "mode")})
    record = {"frozen_commit": head, "scope": "SOURCE_ONLY_PRE_SELECTION_REFUSAL",
              "native_admission": "NOT_ESTABLISHED", "selected_file_count": len(selected),
              "selected_files": selected, "commands": commands}
    (h.evidence / "materialization-record.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    h.materialization = {key: record[key] for key in ("frozen_commit", "scope", "native_admission", "selected_file_count")}
    return root / "skills/implementaudit/scripts"


def exercise(h, reservation_refusal):
    repository, common, work = (h.fixture / name for name in ("repository", "git-common", "worktree"))
    run = work / ".IMPLEMENTAUDIT/runs/fixture"
    for path in (repository, common, run):
        path.mkdir(parents=True)
    initialized = h.call("init", script="host-session-binding.py",
                         args=["--store", str(h.store), "init", "--owner-id", OWNER])
    require(initialized["status"] == "READY", "fixture H0 store initialization failed")
    fields = {
        "owner-id": OWNER, "host-id": "codex", "host-session-id": SESSION,
        "controller-id": "fixture-controller", "claim-id": "fixture-claim",
        "explicit-run-root": run, "repository-identity": repository,
        "git-common-directory-identity": common, "worktree-identity": work,
        "activation-event-id": "fixture-activation", "activation-receipt": "opaque-fixture-activation",
        "continuity-generation": "G0001", "continuity-receipt": "opaque-fixture-continuity",
    }
    bound = h.call("bind", script="host-session-binding.py",
                   args=["--store", str(h.store), "bind",
                         *[part for key, value in fields.items() for part in ("--" + key, str(value))]])
    require(bound["status"] == "BOUND" and bound["host_activation_proven"] is False
            and bound["proof_layers"]["host_activation"] == "UNVERIFIED", "fixture attribution promoted")
    h.mark("constructed-attribution-remains-host-unproved")

    before = h.snapshot()
    empty = h.call("status", mode="status-guard")
    require(empty["decision"] == "NO_PENDING_AUDIT" and not h.pending.exists()
            and before == h.snapshot(), "empty status created pending state")
    h.mark("empty-status-three-reads-zero-observations-zero-writes")

    deliveries = [
        {"currentness": "UNRESOLVED", "measured_epoch": None},
        {"currentness": "UNRESOLVED", "measured_epoch": "G0002"},
        {"currentness": "VERIFIED", "measured_epoch": None},
    ]
    identifier = "unresolved-resume-" + sha(SESSION.encode())
    for version, limits in enumerate(deliveries, 1):
        result = h.call("resume", limits)
        state = h.held(result)
        require(list(state["observations"]) == [identifier]
                and state["observations"][identifier]["version"] == version
                and state["observations"][identifier]["proof"]["observed_limits"] == limits,
                "resume limits discarded or mistaken for occurrence proof")
        require(result == h.call("status"), "new process did not reload exact pending decision")
    h.mark("unresolved-currentness-or-absent-epoch-retains-durable-obligation")

    before = h.state()
    result = h.call("resume", deliveries[-1])
    successor(before, h.held(result))
    require(result == h.call("status"), "repeated resume did not survive restart")
    h.mark("repeated-resume-versions-one-unresolved-identity")

    before = h.snapshot()
    require(h.call("status", mode="status-guard") == result and before == h.snapshot(),
            "pending status observed or changed state")
    h.mark("pending-status-four-reads-zero-observations-zero-writes")

    original, before = h.pending.read_bytes(), h.state()
    h.call("resume", deliveries[-1], mode="before-replace", expected_exit=91)
    require(h.pending.read_bytes() == original, "pre-replacement crash lost original pending bytes")
    require(h.call("status") == result, "pre-replacement restart decision changed")
    h.held(result)
    # A fresh real writer must reacquire the exited process's lock and advance.
    result = h.call("resume", deliveries[-1])
    successor(before, h.held(result))
    require(h.call("status") == result, "post-crash real writer did not reload")
    h.mark("crash-before-replace-retains-original-and-releases-writer-lock")

    before = h.state()
    h.call("resume", deliveries[-1], mode="after-replace", expected_exit=92)
    result = h.call("status")
    successor(before, h.held(result))
    h.mark("crash-after-replace-reloads-coherent-unconsumed-successor")

    direct_scripts = h.scripts
    h.scripts = materialize_selected_source(h)
    fixture_source = h.fixture / "unregistered-fixture.jsonl"
    fixture_source.write_text('{"fixture":true}\n', encoding="utf-8")
    h.refused("source-registration-requires-unmodified-selected-native-profile", "register-source",
              {"task_id": SESSION, "transcript": str(fixture_source),
               "expected_bytes": fixture_source.stat().st_size, "expected_sha256": sha(fixture_source.read_bytes())},
              "NONPROTECTED_SELECTED_ROOT_REQUIRED")
    h.refused("native-profile-absence-refuses-reservation", "reserve",
              {"child_id": "fixture-child", "bounded_purpose": "portable refusal only",
               "observation_source": {key: {} for key in
                                      ("open", "spawn_call", "spawn_output", "child_activation", "parent_turn_start")}},
              reservation_refusal)
    # No assignment exists after the refused reservation. These exercise the
    # actual early FOREIGN_CHILD gate, not deeper native acceptance/JOIN logic.
    h.refused("unreserved-return-refuses-without-state-change", "return",
              {"child_id": "fixture-child", "observation_id": "absent", "result_evidence": {}}, "FOREIGN_CHILD")
    h.refused("unreserved-JOIN-refuses-without-state-change", "join",
              {"child_id": "fixture-child", "return_digest": "0" * 64, "acceptance": {}}, "FOREIGN_CHILD")
    h.scripts = direct_scripts
    h.refused("foreign-owner-cannot-modify-pending", "resume", deliveries[0],
              "HOST_CUSTODY_UNAVAILABLE: foreign store owner", owner="foreign-fixture-owner")
    h.refused("unknown-child-cannot-observe-pending", "observe-child", {"child_id": "unknown-child"}, "FOREIGN_CHILD")
    h.refused("status-rejects-observation-payload", "status", {}, "STATUS_IS_NONOBSERVING")
    h.refused("malformed-resume-retains-pending", "resume", {**deliveries[0], "unexpected": True},
              "RESUME_OBSERVATION_SHAPE")
    h.refused("nonobject-request-retains-pending", "reserve", [], "REQUEST_SHAPE")
    h.refused("duplicate-request-key-retains-pending", "resume", None, "DUPLICATE_JSON_KEY",
              raw='{"currentness":"UNRESOLVED","currentness":"VERIFIED","measured_epoch":null}')


def exercise_path_custody(h):
    """Absent state stays cheap; a present unsafe path cannot mean absence.

    Each mutation is confined to the constructed store. Existing pending bytes
    are retained separately and restored before the next control. No selector,
    observed native result, acceptance or JOIN is supplied.
    """
    original = h.pending.read_bytes()
    before = h.snapshot()
    regular = h.call("status")
    h.held(regular)
    require(before == h.snapshot(), "regular pending status wrote state")
    h.mark("path-custody-regular-pending-reloads-read-only")

    retained = h.pending.with_name("retained-path-custody.pending.json")
    h.pending.rename(retained)
    try:
        before = h.snapshot()
        absent = h.call("status")
        require(absent["decision"] == "NO_PENDING_AUDIT"
                and not absent["audit_state_required"]
                and not absent["state_dependent_decisions_held"]
                and before == h.snapshot(), "genuinely absent pending state changed")
        h.mark("path-custody-genuine-absence-remains-read-only")
    finally:
        retained.rename(h.pending)

    def refuses_without_write(name, action):
        before = h.snapshot()
        limits = {"currentness": "UNRESOLVED", "measured_epoch": None}
        value = h.call(action, limits if action == "resume" else None, expected_exit=2)
        require(value["status"] == "PENDING_OPERATION_REFUSED"
                and "decision" not in value,
                name + ": unsafe custody yielded a decision")
        require(before == h.snapshot(), name + ": refusal altered pending custody")
        h.mark(name)

    h.pending.rename(retained)
    try:
        h.pending.symlink_to(h.pending.with_name("absent-path-custody-target"))
        for action in ("status", "resume"):
            refuses_without_write("path-custody-dangling-file-refuses-" + action, action)
    finally:
        h.pending.unlink(missing_ok=True)
        retained.rename(h.pending)

    parent = h.pending.parent
    retained_parent = parent.with_name(parent.name + "-retained-path-custody")
    parent.rename(retained_parent)
    try:
        parent.symlink_to(parent.with_name("absent-path-custody-directory"), target_is_directory=True)
        for action in ("status", "resume"):
            refuses_without_write("path-custody-dangling-ancestor-refuses-" + action, action)
    finally:
        parent.unlink(missing_ok=True)
        retained_parent.rename(parent)

    h.pending.rename(retained)
    try:
        # A real FIFO detects an accidental blocking read where supported;
        # elsewhere an actual directory still exercises the nonregular fence.
        kind = "fifo" if hasattr(os, "mkfifo") else "directory"
        if kind == "fifo":
            os.mkfifo(h.pending)
        else:
            h.pending.mkdir()
        refuses_without_write("path-custody-" + kind + "-refuses-status", "status")
    finally:
        if h.pending.is_dir():
            h.pending.rmdir()
        else:
            h.pending.unlink(missing_ok=True)
        retained.rename(h.pending)

    require(h.pending.read_bytes() == original and h.call("status") == regular,
            "path custody controls changed the retained pending obligation")
    h.mark("path-custody-original-pending-restored-exactly")



def exercise_stored_json_custody(h, parser_refusal=None):
    """Ambiguous stored keys cannot discard a genuine unconsumed obligation.

    Restoring CORE.read_json's ordinary parser must fail these actual-CLI
    controls. The exact old bytes are restored after each isolated mutation;
    no source registration, selected child or native event is constructed.
    """
    original = h.pending.read_bytes()
    before = h.snapshot()
    regular = h.call("status", mode="status-guard")
    state = h.held(regular)
    require(before == h.snapshot(), "unique-key pending status wrote state")
    h.mark("stored-json-unique-keys-remain-held-and-nonobserving")
    require(len(state["observations"]) == 1 and original.count(b'"consumed_version": 0') == 1,
            "stored-key fixture requires one real unconsumed observation")
    observation = next(iter(state["observations"].values()))
    top = original.rstrip()[:-1] + b',\n  "observations": {}\n}\n'
    nested = original.replace(b'"consumed_version": 0',
                              b'"consumed_version": 0, "consumed_version": '
                              + str(observation["version"]).encode("ascii"), 1)
    cases = [("duplicate-observations", top, action, "DUPLICATE_JSON_KEY")
             for action in ("status", "resume")]
    cases += [("duplicate-consumed-version", nested, action, "DUPLICATE_JSON_KEY")
              for action in ("status", "resume")]
    cases += [("utf16", original.decode("utf-8").encode("utf-16"), "status", parser_refusal),
              ("utf8-bom", b"\xef\xbb\xbf" + original, "status", parser_refusal)]
    failures = []
    for name, wire, action, reason in cases:
        case = "stored-json-" + name + "-refuses-" + action
        h.pending.write_bytes(wire)
        (h.evidence / (case + ".input")).write_bytes(wire)
        before = h.snapshot()
        try:
            value = h.call(action, {"currentness": "UNRESOLVED", "measured_epoch": None}
                           if action == "resume" else None, expected_exit=2)
            require(value["status"] == "PENDING_OPERATION_REFUSED" and "decision" not in value,
                    case + ": ambiguous stored bytes yielded a decision")
            require(value["reason"] == reason if reason is not None else
                    value["reason"].startswith("HOST_CUSTODY_UNAVAILABLE: compaction audit pending state is unreadable or malformed:"),
                    case + ": unexpected parser refusal")
            require(before == h.snapshot(), case + ": refusal wrote pending state")
            h.mark(case)
        except AssertionError as error:
            failures.append({"case": case, "error": str(error)})
        finally:
            h.pending.write_bytes(original)
            require(h.call("status") == regular and h.pending.read_bytes() == original,
                    case + ": restored pending obligation differs")

    retained = h.pending.with_name("retained-stored-json-open.pending.json")
    try:
        value = h.call("status", mode="pending-open-nonregular", expected_exit=2)
        require(value["status"] == "PENDING_OPERATION_REFUSED" and "decision" not in value,
                "scheduled nonregular open yielded a decision")
        require(retained.read_bytes() == original,
                "scheduled open changed retained pending bytes")
        h.mark("stored-json-preopen-nonregular-replacement-refuses")
    finally:
        if retained.exists():
            if h.pending.is_dir():
                h.pending.rmdir()
            else:
                h.pending.unlink(missing_ok=True)
            retained.rename(h.pending)
        require(h.call("status") == regular and h.pending.read_bytes() == original,
                "open-boundary restoration changed pending obligation")
    require(not failures, "stored JSON refusals failed: " + json.dumps(failures, sort_keys=True))



def exercise_stored_counter_positives(h):
    """Real integer producers and nonobserving readers retain their contract.

    The 2/1 and 2/2 rows are value fixtures only. They do not establish an
    accepted native return, JOIN or consumed-scope event.
    """
    original = h.pending.read_bytes()
    before = h.snapshot()
    regular = h.call("status", mode="status-guard")
    state = h.held(regular)
    require(before == h.snapshot(), "integer counter status wrote state")
    require(len(state["observations"]) == 1, "counter fixture needs one real observation")
    identifier, observation = next(iter(state["observations"].items()))
    require(type(observation["version"]) is int and observation["version"] > 0
            and type(observation["consumed_version"]) is int
            and observation["consumed_version"] == 0, "fixture producer emitted invalid counters")
    h.mark("stored-counter-genuine-integers-held-four-reads-zero-observations-zero-writes")

    retained = h.pending.with_name("retained-counter-positive.pending.json")
    h.pending.rename(retained)
    try:
        before = h.snapshot()
        absent = h.call("status", mode="status-guard")
        require(absent["decision"] == "NO_PENDING_AUDIT"
                and not absent["state_dependent_decisions_held"]
                and before == h.snapshot(), "absent counter status created state")
        h.mark("stored-counter-absence-three-reads-zero-observations-zero-writes")
    finally:
        retained.rename(h.pending)

    for consumed, expected, held in [(1, "AUDIT_STATE_REQUIRED", True),
                                      (2, "NO_PENDING_AUDIT", False)]:
        changed = json.loads(original)
        changed["observations"][identifier].update(version=2, consumed_version=consumed)
        wire = (json.dumps(changed, indent=2, sort_keys=True) + "\n").encode()
        h.pending.write_bytes(wire)
        try:
            before = h.snapshot()
            value = h.call("status")
            require(value["decision"] == expected
                    and value["state_dependent_decisions_held"] is held
                    and value["audit_state_required"] is held
                    and value["pending"] == ([{"id": identifier, "version": 2,
                                             "kind": observation["kind"]}] if held else [])
                    and value["assigned_scope"] == [] and before == h.snapshot(),
                    "valid value-only counter interval was misread")
            h.mark("stored-counter-value-only-two-" + str(consumed))
        finally:
            h.pending.write_bytes(original)
    try:
        resumed = h.call("resume", observation["proof"]["observed_limits"])
        after = h.held(resumed)
        successor(state, after)
        updated = after["observations"][identifier]
        require(type(updated["version"]) is int and type(updated["consumed_version"]) is int
                and h.call("status") == resumed, "real successor lost its integer pending state")
        h.mark("stored-counter-genuine-resume-preserves-integer-successor")
    finally:
        h.pending.write_bytes(original)
    require(h.pending.read_bytes() == original, "positive controls did not restore original bytes")


def exercise_stored_counter_refusals(h, selected=None, *, nonfinite_reason="PENDING_OBSERVATION_COUNTERS"):
    """Malformed counters cannot hide work or be rewritten by a later resume.

    Removing the load-time domain check must fail these actual status/resume
    controls. Every mutation changes one counter in a genuinely produced row;
    all other original bytes/values are restored before the next case.
    """
    original = h.pending.read_bytes()
    state = json.loads(original)
    require(len(state["observations"]) == 1, "counter fixture needs one real observation")
    identifier, observation = next(iter(state["observations"].items()))
    mutations = [
        ("version-nan", "version", float("nan")),
        ("version-boolean", "version", True),
        ("version-float", "version", 1.0),
        ("version-zero", "version", 0),
        ("version-negative", "version", -1),
        ("consumed-nan", "consumed_version", float("nan")),
        ("consumed-boolean", "consumed_version", True),
        ("consumed-float", "consumed_version", 0.0),
        ("consumed-negative", "consumed_version", -1),
        ("consumed-future", "consumed_version", observation["version"] + 1),
    ]
    cases = [(name, key, value, action) for name, key, value in mutations
             for action in ("status", "resume")]
    if selected is not None:
        require(set(selected) <= {name for name, _, _ in mutations}, "unknown counter test selection")
        cases = [row for row in cases if row[0] in selected]
    require(cases, "empty counter refusal selection")
    failures = []
    for name, key, bad_value, action in cases:
        case = "stored-counter-" + name + "-refuses-" + action
        changed = json.loads(original)
        changed["observations"][identifier][key] = bad_value
        wire = (json.dumps(changed, indent=2, sort_keys=True) + "\n").encode()
        h.pending.write_bytes(wire)
        (h.evidence / (case + ".input")).write_bytes(wire)
        before = h.snapshot()
        try:
            value = h.call(action, {"currentness": "UNRESOLVED", "measured_epoch": None}
                           if action == "resume" else None, expected_exit=2)
            require(value["status"] == "PENDING_OPERATION_REFUSED" and "decision" not in value
                    and value["reason"] == (nonfinite_reason if name in ("version-nan", "consumed-nan")
                                            else "PENDING_OBSERVATION_COUNTERS"),
                    case + ": malformed counters yielded the wrong result")
            require(before == h.snapshot(), case + ": refusal changed the actual store")
            h.mark(case)
        except AssertionError as error:
            failures.append({"case": case, "error": str(error)})
        finally:
            h.pending.write_bytes(original)
            require(h.pending.read_bytes() == original, case + ": exact restoration failed")
    h.held(h.call("status", mode="status-guard"))
    require(h.pending.read_bytes() == original, "restored counter read changed pending bytes")
    require(not failures, "stored counter refusals failed: " + json.dumps(failures, sort_keys=True))


def source_pins(repo):
    # These are the owners executed/imported by this bounded CLI qualification.
    names = ("compaction-audit-pending.py", "host-session-binding.py", "compaction-result-observation.py",
             "compaction-source-owner-codex-app.py")
    return {str(PEER / name): sha((repo / PEER / name).read_bytes()) for name in names}


def reservation_refusal_profile(pins):
    # All qualified sources refuse before assignment. R0039 selects a profile
    # before acquiring the absent native selection, so its exact first guard
    # differs. Bind the same four source owners recorded by source_pins; do not
    # accept either reason interchangeably or infer it from the response.
    profiles = {
        # Current DG08 source-only tuple; native selection remains absent.
        ('e9e8b5f9246f288ceade888c44ad4f1445033f4d944eabf3d8e4da391891a682',
         '75eb9d4fce108a89847a78d972800482751ad5994c340eb73b30d82932097728',
         'dba5771d606e1669090703cf6094440344684fdafd2d67a40ae8eb95e3190985',
         'f024cd50b4e5cdd3b93f16fe1d0489952a534a0a5f880c842c14afc897ac2bc7'):
            ('source-sha256:dba5771d606e1669090703cf6094440344684fdafd2d67a40ae8eb95e3190985',
             "NONPROTECTED_PROJECTION_PROFILE_REQUIRED", "PENDING_STATE_JSON", "PENDING_STATE_JSON_CONSTANT"),
        # Current native H0 JSON ambiguity guard; all older exact tuples remain.
        ("8c16f7f142b67eb4504ae275bf53e8ea104bb75378748402e8a4c0a31efdbc43",
         "9ea603b9d923df5c155c7a5406ee2dac21cbc8fc87ec205f978e3130fbe43345",
         "799d468f8a98a6990c798488517ba27f273f4862d6066a9b228ab0d1c7c6a517",
         "f024cd50b4e5cdd3b93f16fe1d0489952a534a0a5f880c842c14afc897ac2bc7"):
            ("source-sha256:f024cd50b4e5cdd3b93f16fe1d0489952a534a0a5f880c842c14afc897ac2bc7",
             "NONPROTECTED_PROJECTION_PROFILE_REQUIRED", "PENDING_STATE_JSON", "PENDING_STATE_JSON_CONSTANT"),
        # Generic policy repair: new exact four-owner tuple, still no native selection.
        ("8c16f7f142b67eb4504ae275bf53e8ea104bb75378748402e8a4c0a31efdbc43",
         "9ea603b9d923df5c155c7a5406ee2dac21cbc8fc87ec205f978e3130fbe43345",
         "799d468f8a98a6990c798488517ba27f273f4862d6066a9b228ab0d1c7c6a517",
         "62558bb209129c66b55d2a97325d16db4aecfd2ecbeb71323dd44070a50f0890"):
            ("source-sha256:799d468f8a98a6990c798488517ba27f273f4862d6066a9b228ab0d1c7c6a517",
             "NONPROTECTED_PROJECTION_PROFILE_REQUIRED", "PENDING_STATE_JSON", "PENDING_STATE_JSON_CONSTANT"),
        # Combined top-level counter guard; original parser and reservation guards retained.
        ("8c16f7f142b67eb4504ae275bf53e8ea104bb75378748402e8a4c0a31efdbc43",
         "9ea603b9d923df5c155c7a5406ee2dac21cbc8fc87ec205f978e3130fbe43345",
         "2fcb390a3e4105adc1178000e736b1a09b3b5a59db03fdd744cda895a1352d04",
         "62558bb209129c66b55d2a97325d16db4aecfd2ecbeb71323dd44070a50f0890"):
            ("source-sha256:8c16f7f142b67eb4504ae275bf53e8ea104bb75378748402e8a4c0a31efdbc43",
             "NONPROTECTED_PROJECTION_PROFILE_REQUIRED", "PENDING_STATE_JSON", "PENDING_STATE_JSON_CONSTANT"),
        ("b12a6e385bb911e54c641c8a3c56ba0d0a40819083f4444f2659c6eecd55af8c",
         "9ea603b9d923df5c155c7a5406ee2dac21cbc8fc87ec205f978e3130fbe43345",
         "2fcb390a3e4105adc1178000e736b1a09b3b5a59db03fdd744cda895a1352d04",
         "62558bb209129c66b55d2a97325d16db4aecfd2ecbeb71323dd44070a50f0890"):
            ("f74a7c6675073af8c78f8a83ef5f3eb1476d2bfb", "NONPROTECTED_PROJECTION_PROFILE_REQUIRED",
             "PENDING_STATE_JSON", "PENDING_STATE_JSON_CONSTANT"),
        ("9b5faf290e08d3df77b15d5e5301a3760c4e599d16719cf8f72e1768522ea691",
         "9ea603b9d923df5c155c7a5406ee2dac21cbc8fc87ec205f978e3130fbe43345",
         "2fcb390a3e4105adc1178000e736b1a09b3b5a59db03fdd744cda895a1352d04",
         "62558bb209129c66b55d2a97325d16db4aecfd2ecbeb71323dd44070a50f0890"):
            ("5d90c706518cd08f13dfbb2024e806702cae85e9", "NONPROTECTED_PROJECTION_PROFILE_REQUIRED"),
        ("2361a0026d108b551158eb865075912386eddb4878b71316560e46cc3597024d",
         "5848edf46581f885521fb677377f4742b630ac8ff0ab0b906ec0e00520fcf896",
         "1d7b7acaa9d1a481608ebf62ca5be8f30f25af0f5dc56d2bf4e795dce9c67c91",
         "62558bb209129c66b55d2a97325d16db4aecfd2ecbeb71323dd44070a50f0890"):
            ("2dccd7cbc7fb7866caff46ced84b4338c51a5b85", "NONPROTECTED_FIXED_SELECTION_UNBOUND"),
        ("50a67ea76a0c261627ff1a488f3916d33567404ed2d6b4fd068c909730d173f1",
         "5848edf46581f885521fb677377f4742b630ac8ff0ab0b906ec0e00520fcf896",
         "1d7b7acaa9d1a481608ebf62ca5be8f30f25af0f5dc56d2bf4e795dce9c67c91",
         "62558bb209129c66b55d2a97325d16db4aecfd2ecbeb71323dd44070a50f0890"):
            ("c013467cee36425630fbb6209a111c7642772ce2", "NONPROTECTED_FIXED_SELECTION_UNBOUND"),
        ("caca3f0a512b7c4e020fa8e6093e375e9ad849712e660612f82d680f90ebc0f9",
         "5848edf46581f885521fb677377f4742b630ac8ff0ab0b906ec0e00520fcf896",
         "1d7b7acaa9d1a481608ebf62ca5be8f30f25af0f5dc56d2bf4e795dce9c67c91",
         "62558bb209129c66b55d2a97325d16db4aecfd2ecbeb71323dd44070a50f0890"):
            ("068cb188acbac913088954a45dc1594846b2c81e", "NONPROTECTED_FIXED_SELECTION_UNBOUND"),
        ("0c673a96c86a131d73cb8dbf4ec0dce124943fd2f2c72c7b26af9a024249a986",
         "5848edf46581f885521fb677377f4742b630ac8ff0ab0b906ec0e00520fcf896",
         "1d7b7acaa9d1a481608ebf62ca5be8f30f25af0f5dc56d2bf4e795dce9c67c91",
         "62558bb209129c66b55d2a97325d16db4aecfd2ecbeb71323dd44070a50f0890"):
            ("b9fb34dbde3f344027e18aa427592e4853001c69", "NONPROTECTED_FIXED_SELECTION_UNBOUND"),
        ("e6516032d8d93e00a530c0753ed23e1b51cdcf2b27e45611b3923f3922718c34",
         "38236d9247b66202807f55c36e8505335c73c5129778cd16b3180661690578e4",
         "439b4efaddbe7c3a19b625db0e8480d7a857ebc603be34cb9e9bbec575902581",
         "62558bb209129c66b55d2a97325d16db4aecfd2ecbeb71323dd44070a50f0890"):
            ("8fd58276a50ae069ed71d52be01c775047ce692a", "NONPROTECTED_PROJECTION_PROFILE_REQUIRED"),
        ("e6516032d8d93e00a530c0753ed23e1b51cdcf2b27e45611b3923f3922718c34",
         "9ea603b9d923df5c155c7a5406ee2dac21cbc8fc87ec205f978e3130fbe43345",
         "2fcb390a3e4105adc1178000e736b1a09b3b5a59db03fdd744cda895a1352d04",
         "62558bb209129c66b55d2a97325d16db4aecfd2ecbeb71323dd44070a50f0890"):
            ("7a89c484b6c0884c0fb7be46423600cf1fe53d0d", "NONPROTECTED_PROJECTION_PROFILE_REQUIRED"),
    }
    names = ("compaction-audit-pending.py", "compaction-result-observation.py",
             "compaction-source-owner-codex-app.py", "host-session-binding.py")
    identity = tuple(pins.get(str(PEER / name)) for name in names)
    require(identity in profiles, "unqualified portable reservation-refusal source profile")
    selected = profiles[identity]
    checkpoint, reason = selected[:2]
    profile = {"qualified_checkpoint": checkpoint, "expected_reason": reason}
    if len(selected) >= 3:
        profile["stored_json_refusal"] = selected[2]
    if len(selected) == 4:
        profile["nonfinite_counter_refusal"] = selected[3]
    return profile


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    parser.add_argument("--evidence-dir", type=Path)
    args = parser.parse_args()
    repo = args.repo_root.resolve(strict=True)
    evidence = args.evidence_dir.absolute() if args.evidence_dir else Path(tempfile.mkdtemp(prefix="cognition-pending-durability-"))
    if args.evidence_dir:
        evidence.mkdir(parents=True, exist_ok=False)
    evidence = evidence.resolve(strict=True)
    h = Harness(repo, evidence)
    pins = source_pins(repo)
    report = {"scope": "PORTABLE_ACTUAL_OWNER_CLI_PROCESS_CRASH_ONLY", "evidence_dir": str(evidence),
              "host_activation_proven": False, "native_activation": "UNPROVED",
              "authentic_physical_boundary": "UNPROVED", "native_JOIN_consumption": "UNPROVED",
              "native_lifecycle": "NOT_CLAIMED", "native_producer_runtime_equivalence": "UNVERIFIED",
              "source_file_count": len(pins), "source_sha256": pins, "limitations": LIMITATIONS, **CEILING}
    try:
        profile = reservation_refusal_profile(pins)
        report["reservation_refusal_profile"] = profile
        # Refuse to run this portable fixture against a privately selected
        # native runtime. This reads the unchanged source; it never clears pins.
        tree = ast.parse((repo / PEER / "compaction-source-owner-codex-app.py").read_bytes())
        selections = [ast.literal_eval(node.value) for node in tree.body
                      if isinstance(node, ast.Assign)
                      and any(isinstance(target, ast.Name) and target.id == "NONPROTECTED_SELECTION_PIN"
                              for target in node.targets)]
        require(selections == [None], "portable test requires the original absent native selection")
        exercise(h, profile["expected_reason"])
        exercise_path_custody(h)
        exercise_stored_json_custody(h, profile.get("stored_json_refusal"))
        exercise_stored_counter_positives(h)
        exercise_stored_counter_refusals(h, nonfinite_reason=profile.get(
            "nonfinite_counter_refusal", "PENDING_OBSERVATION_COUNTERS"))
        require(source_pins(repo) == pins, "actual source owners changed during qualification")
        report["result"] = "PASS"
    except Exception as error:
        report.update(result="FAIL", error=str(error), traceback=traceback.format_exc())
    finally:
        report.update(controls=len(h.controls), control_names=h.controls, process_count=len(h.records),
                      source_unchanged=source_pins(repo) == pins,
                      materialization=getattr(h, "materialization", None))
        (evidence / "report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, sort_keys=True))
    return 0 if report["result"] == "PASS" else 1


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--worker":
        raise SystemExit(worker(*sys.argv[2:]))
    raise SystemExit(main())
