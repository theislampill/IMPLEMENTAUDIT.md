"""One exact system-bwrap prerequisite observation inside the qualified capsule.

Import is inert. This program never invokes Codex, a shell, a model, package
scripts, a policy writer or a command selected by input. Private streams remain
private. All source tests are pure or use owned temporary files.
"""
import base64
import ctypes
import errno
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import sys
import time
import types

IDENTITY = "dg17-9077-codex20-namespace-prerequisite04"
SCHEMA = "dg17.codex20.namespace-prerequisite-worker.v1"
DIRECTORY = "qualification/dg17-codex-namespace-prerequisite04"
WORKER_PATH = DIRECTORY + "/worker.py"
PREPARER_PATH = "qualification/dg17-codex-host-preparation02/prepare.py"
B64_PATH = "qualification/dg17-codex-host-preparation02/BWRAP_INPUT.b64"
EPISODE_PATH = "qualification/dg17-codex-routing/episode.py"
UTILITY_PATH = "qualification/dg17-codex-routing/host_utility.py"
DEPENDENCY_PATHS = (B64_PATH, PREPARER_PATH, WORKER_PATH, EPISODE_PATH, UTILITY_PATH)
UPSTREAM_SHA256 = "ec31c6bc4b844183ae3c6e5fcea5e97db95e6f26cfaeb4c9bedb37cdf01534ee"
MEMBER_SHA256 = "e318903862396f96de3df57264e0158682b952fd3fb53ac23d876413e7b30f71"
MEMBER_BYTES = 72160
PROBE_MILLISECONDS, POLL_MILLISECONDS, STDERR_LIMIT = 500, 50, 65536
INPUT_LIMIT, RESULT_LIMIT = 1048576, 16384
MARKERS = {
    "LOOPBACK_NEWADDR": b"loopback: Failed RTM_NEWADDR",
    "LOOPBACK_NEWLINK": b"loopback: Failed RTM_NEWLINK",
    "UID_MAP_PERMISSION": b"setting up uid map: Permission denied",
    "NAMESPACE_PERMISSION": b"No permissions to create a new namespace",
}
INTEGER_PATHS = {
    "unprivileged_userns_clone": "/proc/sys/kernel/unprivileged_userns_clone",
    "max_user_namespaces": "/proc/sys/user/max_user_namespaces",
    "max_net_namespaces": "/proc/sys/user/max_net_namespaces",
    "apparmor_restrict_unprivileged_userns": "/proc/sys/kernel/apparmor_restrict_unprivileged_userns",
}
OBSERVATION_PATHS = {
    **INTEGER_PATHS,
    "apparmor_enabled": "/sys/module/apparmor/parameters/enabled",
    "current_lsm_label": "/proc/self/attr/current",
    "seccomp": "/proc/self/status",
}
ARGUMENTS = ("--source", "--output", "--helper", "--helper-sha256", "--capsule-admission",
             "--expected-uid", "--expected-gid", "--parent-netns", "--parent-mntns",
             "--source-pins-sha256", "--context-sha256", "--upstream-sha256")


class Refusal(ValueError):
    pass


def need(ok, code):
    if ok is not True:
        raise Refusal(code)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def encoded(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False) + "\n").encode("ascii")


def strict(raw, bound):
    need(type(raw) is bytes and 0 < len(raw) <= bound, "JSON_BOUND")
    def pairs(items):
        result = {}
        for key, value in items:
            need(key not in result, "JSON_DUPLICATE"); result[key] = value
        return result
    def reject(value): raise Refusal("JSON_NONFINITE")
    try: return json.loads(raw.decode("utf8"), object_pairs_hook=pairs, parse_constant=reject)
    except (UnicodeError, json.JSONDecodeError): raise Refusal("JSON_SYNTAX") from None


def identity(info):
    return tuple(getattr(info, "st_" + key) for key in ("dev", "ino", "mode", "uid", "gid", "nlink", "size", "mtime_ns", "ctime_ns"))


def read_regular(path, bound):
    path = Path(path)
    need(path.is_absolute() and path.resolve(strict=True) == path, "READ_PHYSICAL_PATH")
    descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK | os.O_CLOEXEC)
    try:
        before = os.fstat(descriptor)
        need(stat.S_ISREG(before.st_mode) and before.st_nlink == 1 and before.st_size <= bound, "READ_FILE_BOUND")
        raw = bytearray()
        while len(raw) <= bound:
            part = os.read(descriptor, min(65536, bound + 1 - len(raw)))
            if not part: break
            raw.extend(part)
        need(len(raw) == before.st_size and identity(before) == identity(os.fstat(descriptor)) == identity(path.lstat()), "READ_CHANGED")
        return bytes(raw)
    finally: os.close(descriptor)


def write_private(path, raw, bound):
    path = Path(path); parent = path.parent; info = parent.lstat()
    need(parent.resolve(strict=True) == parent and stat.S_ISDIR(info.st_mode) and info.st_uid == os.getuid()
         and stat.S_IMODE(info.st_mode) == 0o700 and type(raw) is bytes and len(raw) <= bound, "PRIVATE_OUTPUT_ADMISSION")
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC, 0o600)
    with os.fdopen(descriptor, "wb") as stream:
        stream.write(raw); stream.flush(); os.fsync(stream.fileno())


def read_fixed(path, bound):
    """Only fixed proc/sys observations; proc's self aliases are intentional."""
    need(path in OBSERVATION_PATHS.values(), "OBSERVATION_PATH")
    descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK | os.O_CLOEXEC)
    try:
        before = os.fstat(descriptor)
        need(stat.S_ISREG(before.st_mode), "OBSERVATION_FILE")
        raw = bytearray()
        while len(raw) <= bound:
            part = os.read(descriptor, min(4096, bound + 1 - len(raw)))
            if not part: break
            raw.extend(part)
        need(len(raw) <= bound and (before.st_dev, before.st_ino, before.st_mode) ==
             (os.fstat(descriptor).st_dev, os.fstat(descriptor).st_ino, os.fstat(descriptor).st_mode), "OBSERVATION_BOUND")
        return bytes(raw)
    finally: os.close(descriptor)


def parse_integer(raw):
    need(type(raw) is bytes and len(raw) <= 256 and re.fullmatch(rb"[0-9]{1,16}\n?", raw) is not None, "INTEGER_FACT")
    return int(raw)


def parse_lsm_label(raw):
    need(type(raw) is bytes and 0 < len(raw) <= 256 and b"\x00" not in raw, "LSM_LABEL_FACT")
    return "UNCONFINED" if raw.rstrip(b"\n") == b"unconfined" else "CONFINED_OR_OTHER"


def parse_seccomp(raw):
    need(type(raw) is bytes and len(raw) <= 16384, "STATUS_BOUND")
    values = {}
    for line in raw.splitlines():
        if b":" not in line: continue
        name, value = line.split(b":", 1)
        if name not in (b"Seccomp", b"Seccomp_filters"): continue
        need(name not in values, "STATUS_DUPLICATE")
        values[name] = parse_integer(value.strip())
    need(set(values) == {b"Seccomp", b"Seccomp_filters"} and values[b"Seccomp"] in (0, 1, 2)
         and values[b"Seccomp_filters"] <= 65536, "SECCOMP_FACT")
    return {"mode": values[b"Seccomp"], "filters": values[b"Seccomp_filters"]}


def policy_snapshot(reader=read_fixed):
    public, private = {}, {}
    for name, path in OBSERVATION_PATHS.items():
        row = {"state": "UNREADABLE", "value": None, "bytes": 0, "sha256": None, "errno": None}
        raw = None
        try:
            raw = reader(path, 16384 if name == "seccomp" else 256)
            row.update(bytes=len(raw), sha256=sha(raw))
            if name in INTEGER_PATHS: value = parse_integer(raw)
            elif name == "current_lsm_label": value = parse_lsm_label(raw)
            elif name == "seccomp": value = parse_seccomp(raw)
            else:
                need(raw in (b"Y", b"Y\n", b"N", b"N\n"), "APPARMOR_ENABLED_FACT")
                value = raw[:1] == b"Y"
            row.update(state="VALUE", value=value)
        except OSError as exc:
            row.update(state="MISSING" if exc.errno == errno.ENOENT else "UNREADABLE",
                       errno=exc.errno if type(exc.errno) is int and 0 <= exc.errno <= 4096 else None)
        except (Refusal, UnicodeError): row["state"] = "INVALID"
        public[name] = row
        private[name] = {"path": path, "raw_base64": base64.b64encode(raw).decode("ascii") if raw is not None else None, "observation": row}
    return public, private


def policy_agrees(before, after):
    if type(before) is not dict or type(after) is not dict or set(before) != set(OBSERVATION_PATHS) or set(after) != set(OBSERVATION_PATHS):
        return False
    for name in OBSERVATION_PATHS:
        keys = ("state", "value", "errno", "sha256") if name == "current_lsm_label" else ("state", "value", "errno")
        if any(before[name].get(key) != after[name].get(key) for key in keys): return False
    return True


def probe_argv():
    return ["/usr/bin/bwrap", "--unshare-user", "--unshare-net", "--ro-bind", "/", "/", "/bin/true"]


def classify_probe(returncode, stderr, timed_out, capture_refused, start_errno, complete):
    need(type(stderr) is bytes and len(stderr) <= STDERR_LIMIT, "CLASSIFY_BOUND")
    markers = {key: value in stderr for key, value in MARKERS.items()}
    if start_errno is not None: outcome, branch = "START_REFUSED", False
    elif timed_out: outcome, branch = "TIMEOUT", False
    elif capture_refused or not complete or type(returncode) is not int: outcome, branch = "CAPTURE_REFUSED", None
    elif returncode == 0: outcome, branch = "EXIT_ZERO", False
    elif any(markers.values()): outcome, branch = "USER_NAMESPACE_REFUSAL", True
    else: outcome, branch = "NONZERO_OTHER", False
    return {"outcome": outcome, "markers": markers, "upstream_warning_branch": branch}


def input_sources(source, expected):
    source = Path(source)
    need(source.is_absolute() and source.resolve(strict=True) == source and re.fullmatch("[0-9a-f]{64}", expected) is not None, "SOURCE_ROOT")
    raw = read_regular(source / DIRECTORY / "INPUT_PINS.json", 16384)
    need(sha(raw) == expected, "INPUT_PINS_DIGEST")
    value = strict(raw, 16384)
    need(type(value) is dict and set(value) == {"schema", "files"} and value["schema"] == "dg17.namespace-prerequisite.inputs.v1", "INPUT_PINS_SCHEMA")
    rows = value["files"]
    need(type(rows) is list and len(rows) == len(DEPENDENCY_PATHS), "INPUT_POPULATION")
    need(all(type(row) is dict and set(row) == {"path", "bytes", "sha256"} for row in rows), "INPUT_ROW")
    need([row["path"] for row in rows] == sorted(DEPENDENCY_PATHS), "INPUT_PATHS")
    need(all(type(row["bytes"]) is int and 0 < row["bytes"] <= INPUT_LIMIT and type(row["sha256"]) is str
             and re.fullmatch("[0-9a-f]{64}", row["sha256"]) is not None for row in rows)
         and sum(row["bytes"] for row in rows) <= INPUT_LIMIT, "INPUT_AGGREGATE")
    bodies = {}
    for row in rows:
        body = read_regular(source / row["path"], row["bytes"])
        need(len(body) == row["bytes"] and sha(body) == row["sha256"], "INPUT_BODY")
        bodies[row["path"]] = body
    return rows, bodies


def loaded(raw, name):
    module = types.ModuleType(name)
    exec(compile(raw, name, "exec"), module.__dict__)
    return module


def quiescent(u):
    need(u.children() == [], "CHILD_CENSUS")
    try: os.waitpid(-1, os.WNOHANG | 0x40000000)
    except ChildProcessError: return True
    raise Refusal("ECHILD_UNCONFIRMED")


def capture_probe(u, environment, private):
    """Match upstream wait-then-bounded-read behavior; add owned cleanup/receipts.

    stderr is not drained while the probe is running, just as in the pinned
    upstream source. A full64KiB capture is explicitly incomplete because this
    observer will not read beyond the selected cap to establish EOF.
    """
    result = {"process_started": False, "pidfd_acquired": False, "returncode": None, "start_errno": None,
              "timeout": False, "stderr_bound_reached": False, "internal_failure": None,
              "stderr_bytes": 0, "stderr_sha256": sha(b""), "stderr_complete": False,
              "stdout_policy": "DISCARD_TO_DEVNULL", "stderr_read_phase": "NOT_STARTED", "elapsed_ms": 0,
              "private_stderr_retained": False, "cleanup": None}
    p, anchor, raw = None, None, bytearray()
    started = time.monotonic()
    def read_stderr(phase):
        result["stderr_read_phase"] = phase
        os.set_blocking(p.stderr.fileno(), False)
        while len(raw) < STDERR_LIMIT:
            try: part = os.read(p.stderr.fileno(), min(4096, STDERR_LIMIT - len(raw)))
            except BlockingIOError: break
            if not part:
                result["stderr_complete"] = True; break
            raw.extend(part)
        result["stderr_bound_reached"] = len(raw) == STDERR_LIMIT
    try:
        quiescent(u)
        try:
            p = subprocess.Popen(probe_argv(), stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                                 stderr=subprocess.PIPE, env=environment, close_fds=True)
        except OSError as exc:
            result["start_errno"] = exc.errno if type(exc.errno) is int and 0 <= exc.errno <= 4096 else 0
            result["stderr_complete"] = True
        if p is not None:
            result["process_started"] = True
            started = time.monotonic()
            anchor = os.pidfd_open(p.pid); result["pidfd_acquired"] = True
            deadline = started + PROBE_MILLISECONDS / 1000
            while True:
                rc = p.poll()
                if rc is not None:
                    result["returncode"] = rc; break
                if time.monotonic() >= deadline:
                    result["timeout"] = True; break
                time.sleep(POLL_MILLISECONDS / 1000)
            result["elapsed_ms"] = max(0, int((time.monotonic() - started) * 1000))
            if result["returncode"] is not None:
                # Preserve the upstream normal-path read timing. Later owned
                # descendant cleanup cannot add bytes to its marker evidence.
                read_stderr("AFTER_EXIT_BEFORE_CLEANUP")
    except BaseException:
        result["internal_failure"] = "PROBE_START_WAIT_OR_PIDFD_REFUSED"
    finally:
        # This dedicated subreaper owns only this one command and adopted
        # descendants. No PID-name or process-group signaling is available.
        try:
            cleanup = u.stop_owned_children()
        except BaseException as exc:
            cleanup = getattr(exc, "cleanup_partial", {"echild": False, "pidfd_signals": 0, "reaped_statuses": []})
            result["internal_failure"] = result["internal_failure"] or "PROBE_CLEANUP_REFUSED"
        result["cleanup"] = u.public_cleanup(cleanup)
        if p is not None:
            if result["returncode"] is None:
                # stop_owned_children may have reaped Popen's exact child.
                # Do not let Popen's ECHILD fallback replace its retained code.
                rc = next((row["returncode"] for row in cleanup["reaped_statuses"] if row["pid"] == p.pid), None)
                if rc is None: rc = p.returncode
                if rc is None and cleanup["echild"] is not True: rc = p.poll()
                result["returncode"] = rc; p.returncode = rc
            try:
                if result["stderr_read_phase"] == "NOT_STARTED":
                    read_stderr("AFTER_REFUSAL_CLEANUP")
            except BaseException:
                result["internal_failure"] = result["internal_failure"] or "PROBE_STDERR_READ_REFUSED"
            finally:
                try: p.stderr.close()
                except OSError: result["internal_failure"] = result["internal_failure"] or "PROBE_STDERR_READ_REFUSED"
        if anchor is not None:
            try: os.close(anchor)
            except OSError: result["internal_failure"] = result["internal_failure"] or "PROBE_CLEANUP_REFUSED"
        result.update(stderr_bytes=len(raw), stderr_sha256=sha(raw))
        try:
            write_private(Path(private) / "PROBE.stderr", bytes(raw), STDERR_LIMIT)
            result["private_stderr_retained"] = True
        except BaseException:
            result["internal_failure"] = result["internal_failure"] or "PROBE_PRIVATE_RETENTION_REFUSED"
    refused = result["internal_failure"] is not None or result["stderr_bound_reached"] or result["cleanup"]["echild"] is not True
    return result, classify_probe(result["returncode"], bytes(raw), result["timeout"], refused,
                                  result["start_errno"], result["stderr_complete"])


def arguments(argv):
    need(type(argv) is list and len(argv) == 24 and tuple(argv[::2]) == ARGUMENTS, "ARGUMENT_POPULATION")
    values = dict(zip(ARGUMENTS, argv[1::2]))
    need(all(type(value) is str and 0 < len(value) <= 4096 and "\x00" not in value for value in values.values()), "ARGUMENT_VALUE")
    need(values["--helper"] == "/usr/bin/bwrap" and values["--helper-sha256"] == MEMBER_SHA256
         and values["--upstream-sha256"] == UPSTREAM_SHA256, "HELPER_SOURCE_BINDING")
    for key in ("--expected-uid", "--expected-gid"):
        need(re.fullmatch("[1-9][0-9]{0,9}", values[key]) is not None, "OWNER_ARGUMENT")
    for key in ("--source-pins-sha256", "--context-sha256"):
        need(re.fullmatch("[0-9a-f]{64}", values[key]) is not None, "DIGEST_ARGUMENT")
    for key, family in (("--parent-netns", "net"), ("--parent-mntns", "mnt")):
        need(re.fullmatch(family + r":\[[0-9]+\]", values[key]) is not None, "NAMESPACE_ARGUMENT")
    return values


def fields(value, names, code):
    need(type(value) is dict and set(value) == set(names), code)


def integer(value, low=0, high=2**63-1):
    return type(value) is int and low <= value <= high


def digest_value(value):
    return type(value) is str and re.fullmatch("[0-9a-f]{64}", value) is not None


def validate_cleanup(value):
    fields(value, ("echild", "pidfd_signals", "retained_status_count", "retained_statuses_sha256", "reaped_statuses", "reaped_statuses_truncated"), "CLEANUP_FIELDS")
    need(type(value["echild"]) is bool and integer(value["pidfd_signals"], 0, 4096)
         and integer(value["retained_status_count"], 0, 4096) and digest_value(value["retained_statuses_sha256"])
         and type(value["reaped_statuses_truncated"]) is bool, "CLEANUP_VALUES")
    rows = value["reaped_statuses"]
    need(type(rows) is list and len(rows) == min(8, value["retained_status_count"])
         and value["reaped_statuses_truncated"] == (value["retained_status_count"] > 8), "CLEANUP_POPULATION")
    for row in rows:
        fields(row, ("pid", "returncode"), "CLEANUP_ROW")
        need(integer(row["pid"], 1, 2**31-1) and integer(row["returncode"], -128, 255), "CLEANUP_ROW_VALUE")


def validate_helper(value):
    if value.get("status") == "EXACT_ENOENT":
        fields(value, ("status", "errno"), "HELPER_ABSENT_FIELDS")
        need(type(value["errno"]) is int and value["errno"] == 2, "HELPER_ABSENT_VALUE")
        return
    fields(value, ("status", "identity", "bytes", "sha256", "elf", "file_capabilities", "bin_alias_same_file"), "HELPER_FIELDS")
    need(value["status"] == "PHYSICAL_HELPER_ADMITTED" and integer(value["bytes"], 64, 67108864)
         and digest_value(value["sha256"]) and value["elf"] == "ELF64_LSB_X86_64"
         and value["file_capabilities"] is False and value["bin_alias_same_file"] is True, "HELPER_VALUES")
    item = value["identity"]
    fields(item, ("dev", "ino", "mode", "uid", "gid", "nlink", "size", "mtime_ns", "ctime_ns"), "HELPER_IDENTITY_FIELDS")
    need(all(integer(number) for number in item.values()) and item["uid"] == 0 and item["size"] == value["bytes"]
         and item["nlink"] >= 1 and stat.S_ISREG(item["mode"]) and not item["mode"] & 0o6022 and bool(item["mode"] & 0o111), "HELPER_IDENTITY_VALUES")


def validate_policy(value):
    fields(value, OBSERVATION_PATHS, "POLICY_FIELDS")
    for name, row in value.items():
        fields(row, ("state", "value", "bytes", "sha256", "errno"), "POLICY_ROW_FIELDS")
        need(row["state"] in ("VALUE", "MISSING", "UNREADABLE", "INVALID")
             and integer(row["bytes"], 0, 16384 if name == "seccomp" else 256)
             and (row["sha256"] is None or digest_value(row["sha256"]))
             and (row["errno"] is None or integer(row["errno"], 0, 4096)), "POLICY_ROW_VALUES")
        if row["state"] == "VALUE":
            need(row["errno"] is None and row["bytes"] > 0 and digest_value(row["sha256"]), "POLICY_VALUE_CUSTODY")
            if name in INTEGER_PATHS: need(integer(row["value"], 0, 10**16-1), "POLICY_INTEGER")
            elif name == "current_lsm_label": need(row["value"] in ("UNCONFINED", "CONFINED_OR_OTHER"), "POLICY_LSM")
            elif name == "apparmor_enabled": need(type(row["value"]) is bool, "POLICY_APPARMOR")
            else:
                fields(row["value"], ("mode", "filters"), "POLICY_SECCOMP_FIELDS")
                need(integer(row["value"]["mode"], 0, 2) and integer(row["value"]["filters"], 0, 65536), "POLICY_SECCOMP_VALUES")
        else:
            need(row["value"] is None, "POLICY_UNOBSERVED_VALUE")
            if row["state"] == "MISSING": need(row["errno"] == 2 and row["bytes"] == 0 and row["sha256"] is None, "POLICY_MISSING")


def validate_capture(value):
    fields(value, ("process_started", "pidfd_acquired", "returncode", "start_errno", "timeout", "stderr_bound_reached", "internal_failure",
                   "stderr_bytes", "stderr_sha256", "stderr_complete", "stdout_policy", "stderr_read_phase", "elapsed_ms", "private_stderr_retained", "cleanup"), "PROBE_CAPTURE_FIELDS")
    for key in ("process_started", "pidfd_acquired", "timeout", "stderr_bound_reached", "stderr_complete", "private_stderr_retained"):
        need(type(value[key]) is bool, "PROBE_CAPTURE_BOOLEAN")
    need(value["returncode"] is None or integer(value["returncode"], -128, 255), "PROBE_RETURN")
    need(value["start_errno"] is None or integer(value["start_errno"], 0, 4096), "PROBE_START_ERRNO")
    need(value["internal_failure"] in (None, "PROBE_START_WAIT_OR_PIDFD_REFUSED", "PROBE_CLEANUP_REFUSED", "PROBE_STDERR_READ_REFUSED", "PROBE_PRIVATE_RETENTION_REFUSED"), "PROBE_FAILURE_ENUM")
    need(integer(value["stderr_bytes"], 0, STDERR_LIMIT) and digest_value(value["stderr_sha256"])
         and integer(value["elapsed_ms"], 0, 30000) and value["stdout_policy"] == "DISCARD_TO_DEVNULL"
         and value["stderr_bound_reached"] == (value["stderr_bytes"] == STDERR_LIMIT), "PROBE_CAPTURE_LIMIT")
    need(value["stderr_read_phase"] in ("NOT_STARTED", "AFTER_EXIT_BEFORE_CLEANUP", "AFTER_REFUSAL_CLEANUP"), "PROBE_READ_PHASE")
    need(not value["pidfd_acquired"] or value["process_started"], "PROBE_PIDFD_START_JOIN")
    need(not value["timeout"] or value["process_started"], "PROBE_TIMEOUT_START_JOIN")
    need(not value["stderr_bound_reached"] or value["stderr_complete"] is False, "PROBE_EOF_BOUND_JOIN")
    if value["stderr_bytes"] == 0: need(value["stderr_sha256"] == sha(b""), "PROBE_EMPTY_HASH")
    if value["start_errno"] is not None:
        need(not value["process_started"] and not value["pidfd_acquired"] and value["returncode"] is None
             and value["stderr_bytes"] == 0 and value["stderr_complete"] and value["stderr_read_phase"] == "NOT_STARTED", "PROBE_START_FAILURE_JOIN")
    if not value["process_started"] and value["internal_failure"] is None:
        need(value["start_errno"] is not None, "PROBE_UNSTARTED_ERRNO")
    validate_cleanup(value["cleanup"])


def validate_result(value, context_sha, inputs_sha, uid, gid):
    names = ("schema", "candidate_identity", "status", "context_sha256", "input_pins_sha256", "uid", "gid", "helper_before", "helper_after",
             "helper_unchanged", "policy_before", "policy_after", "policy_unchanged", "capture", "classification", "source_bookends_equal",
             "capsule_admission_sha256", "global_echild_after", "failure", "native_execution", "security_policy_changed", "authority", "original_awards")
    fields(value, names, "WORKER_FIELDS")
    need(value["schema"] == SCHEMA and value["candidate_identity"] == IDENTITY
         and value["status"] in ("OBSERVED_NAMESPACE_PREREQUISITE", "FAILED_OR_UNRECEIVED")
         and value["context_sha256"] == context_sha and value["input_pins_sha256"] == inputs_sha
         and type(value["uid"]) is int and value["uid"] == uid and type(value["gid"]) is int and value["gid"] == gid, "WORKER_BINDING")
    for key in ("helper_unchanged", "policy_unchanged", "source_bookends_equal", "global_echild_after"):
        need(type(value[key]) is bool, "WORKER_BOOLEAN")
    need(value["native_execution"] is False and value["security_policy_changed"] is False and value["authority"] == "NONE" and value["original_awards"] == [], "WORKER_SCOPE")
    need(value["capsule_admission_sha256"] is None or digest_value(value["capsule_admission_sha256"]), "WORKER_ADMISSION_HASH")
    for key in ("helper_before", "helper_after"):
        if value[key] is not None:
            need(type(value[key]) is dict, "HELPER_TYPE"); validate_helper(value[key])
    for key in ("policy_before", "policy_after"):
        if value[key] is not None: validate_policy(value[key])
    if value["failure"] is not None:
        row = value["failure"]; fields(row, ("stage", "code", "errno"), "WORKER_FAILURE_FIELDS")
        need(row["stage"] in ("SOURCE", "CAPSULE", "HELPER", "POLICY", "PROBE", "BOOKEND", "CLEANUP")
             and row["code"] == row["stage"] + "_REFUSED" and (row["errno"] is None or integer(row["errno"], 0, 4096)), "WORKER_FAILURE_VALUES")
    if value["capture"] is not None:
        capture = value["capture"]; validate_capture(capture)
        classification = value["classification"]
        fields(classification, ("outcome", "markers", "upstream_warning_branch"), "CLASSIFICATION_FIELDS")
        fields(classification["markers"], MARKERS, "MARKER_FIELDS")
        need(all(type(flag) is bool for flag in classification["markers"].values()), "MARKER_VALUES")
        # Markers are claims over privately retained bytes. Validate their public
        # conjunction without pretending to receive or reconstruct those bytes.
        synthetic = b"\n".join(MARKERS[key] for key, flag in classification["markers"].items() if flag)
        refused = capture["internal_failure"] is not None or capture["stderr_bound_reached"] or capture["cleanup"]["echild"] is not True
        expected = classify_probe(capture["returncode"], synthetic, capture["timeout"], refused, capture["start_errno"], capture["stderr_complete"])
        need(classification == expected, "CLASSIFICATION_CONJUNCTION")
    else: need(value["classification"] is None, "CLASSIFICATION_WITHOUT_CAPTURE")
    if value["status"] == "OBSERVED_NAMESPACE_PREREQUISITE":
        need(value["failure"] is None and all(value[key] is True for key in ("helper_unchanged", "policy_unchanged", "source_bookends_equal", "global_echild_after")), "WORKER_OBSERVED_FLAGS")
        need(value["helper_before"] == value["helper_after"] and value["helper_before"] is not None
             and value["helper_before"].get("bytes") == MEMBER_BYTES and value["helper_before"].get("sha256") == MEMBER_SHA256
             and policy_agrees(value["policy_before"], value["policy_after"]), "WORKER_OBSERVED_BOOKENDS")
        capture = value["capture"]
        need(capture is not None and capture["internal_failure"] is None and capture["cleanup"]["echild"] is True
             and capture["private_stderr_retained"] is True and not capture["stderr_bound_reached"]
             and (capture["stderr_complete"] or capture["timeout"])
             and (not capture["process_started"] or capture["pidfd_acquired"] and integer(capture["returncode"], -128, 255)), "WORKER_OBSERVED_CAPTURE")
    return True


def run(argv):
    a = arguments(argv)
    source, output = Path(a["--source"]), Path(a["--output"])
    private = output / "private"; uid, gid = int(a["--expected-uid"]), int(a["--expected-gid"])
    need(os.getuid() == os.geteuid() == uid and os.getgid() == os.getegid() == gid, "ORDINARY_CAPSULE_OWNER")
    need(Path(__file__).absolute() == source / WORKER_PATH and Path(a["--capsule-admission"]) == private / "CAPSULE_ADMISSION.json", "WORKER_PATH")
    info = private.lstat()
    need(private.resolve(strict=True) == private and stat.S_ISDIR(info.st_mode) and info.st_uid == uid
         and info.st_gid == gid and stat.S_IMODE(info.st_mode) == 0o700, "PRIVATE_ROOT")
    result = {"schema": SCHEMA, "candidate_identity": IDENTITY, "status": "FAILED_OR_UNRECEIVED",
              "context_sha256": a["--context-sha256"], "input_pins_sha256": a["--source-pins-sha256"],
              "uid": uid, "gid": gid, "helper_before": None, "helper_after": None, "helper_unchanged": False,
              "policy_before": None, "policy_after": None, "policy_unchanged": False,
              "capture": None, "classification": None, "source_bookends_equal": False,
              "capsule_admission_sha256": None, "global_echild_after": False, "failure": None,
              "native_execution": False, "security_policy_changed": False, "authority": "NONE", "original_awards": []}
    stage, u = "SOURCE", None
    try:
        rows, bodies = input_sources(source, a["--source-pins-sha256"])
        u = loaded(bodies[UTILITY_PATH], "dg17_namespace_qualified_utility")
        p = loaded(bodies[PREPARER_PATH], "dg17_namespace_qualified_preparer")
        e = loaded(bodies[EPISODE_PATH], "dg17_namespace_qualified_capsule")
        context_raw = read_regular(private / "CONTEXT.json", 4096)
        need(sha(context_raw) == a["--context-sha256"], "CONTEXT_DIGEST")
        stage = "CAPSULE"
        admission_raw = read_regular(private / "CAPSULE_ADMISSION.json", 16384)
        admission = strict(admission_raw, 16384)
        expected_argv = ["/usr/bin/python3", "-I", "-S", "-B", str(source / WORKER_PATH), *argv]
        need(type(admission) is dict and set(admission) == {"schema", "child_argv_sha256", "snapshot"}
             and admission["schema"] == "dg17.private-view-admission.v3"
             and admission["child_argv_sha256"] == sha(e.encoded(expected_argv))
             and e.capsule_snapshot_valid(admission["snapshot"], uid, gid, a["--parent-mntns"], a["--parent-netns"]), "CAPSULE_ADMISSION")
        result["capsule_admission_sha256"] = sha(admission_raw)
        lib = ctypes.CDLL(None, use_errno=True)
        need(lib.prctl(36, 1, 0, 0, 0) == 0, "SUBREAPER")
        quiescent(u)
        stage = "HELPER"
        result["helper_before"] = p.physical_helper()
        need(result["helper_before"].get("status") == "PHYSICAL_HELPER_ADMITTED"
             and result["helper_before"].get("sha256") == MEMBER_SHA256
             and result["helper_before"].get("bytes") == MEMBER_BYTES, "EXACT_HELPER_REQUIRED")
        true_path, true_fact = u.trusted("true")
        need(true_path == "/usr/bin/true" and Path("/bin/true").resolve(strict=True) == Path(true_path), "TRUE_HELPER")
        stage = "POLICY"
        result["policy_before"], private_before = policy_snapshot()
        write_private(private / "POLICY_BEFORE.private.json", encoded(private_before), 32768)
        home, temp = private / "probe-home", private / "probe-tmp"
        home.mkdir(mode=0o700); temp.mkdir(mode=0o700)
        environment = u.safe_environment()
        environment.update(HOME=str(home), CODEX_HOME=str(home / ".codex"), TMPDIR=str(temp), TMP=str(temp), TEMP=str(temp),
                           XDG_CONFIG_HOME=str(home / ".config"), XDG_DATA_HOME=str(home / ".local/share"), XDG_CACHE_HOME=str(home / ".cache"))
        stage = "PROBE"
        result["capture"], result["classification"] = capture_probe(u, environment, private)
        stage = "BOOKEND"
        result["policy_after"], private_after = policy_snapshot()
        write_private(private / "POLICY_AFTER.private.json", encoded(private_after), 32768)
        result["policy_unchanged"] = policy_agrees(result["policy_before"], result["policy_after"])
        result["helper_after"] = p.physical_helper()
        result["helper_unchanged"] = result["helper_before"] == result["helper_after"]
        need(u.trusted("true") == (true_path, true_fact), "TRUE_HELPER_DRIFT")
        result["source_bookends_equal"] = input_sources(source, a["--source-pins-sha256"])[0] == rows
        result["global_echild_after"] = quiescent(u)
        capture = result["capture"]
        need(capture["internal_failure"] is None and capture["cleanup"]["echild"] is True
             and capture["private_stderr_retained"] is True and not capture["stderr_bound_reached"]
             and (capture["stderr_complete"] is True or capture["timeout"] is True), "PROBE_CAPTURE_INCOMPLETE")
        need(result["helper_unchanged"] and result["policy_unchanged"] and result["source_bookends_equal"], "BOOKEND_CHANGED")
        result["status"] = "OBSERVED_NAMESPACE_PREREQUISITE"
    except BaseException as exc:
        result["failure"] = {"stage": stage, "code": stage + "_REFUSED",
                             "errno": exc.errno if isinstance(exc, OSError) and type(exc.errno) is int and 0 <= exc.errno <= 4096 else None}
    finally:
        if u is not None:
            try: result["global_echild_after"] = quiescent(u)
            except BaseException:
                result["status"] = "FAILED_OR_UNRECEIVED"
                result["failure"] = result["failure"] or {"stage": "CLEANUP", "code": "CLEANUP_REFUSED", "errno": None}
    validate_result(result, a["--context-sha256"], a["--source-pins-sha256"], uid, gid)
    raw = encoded(result); need(len(raw) <= RESULT_LIMIT, "WORKER_RESULT_BOUND")
    write_private(private / "WORKER_RESULT.json", raw, RESULT_LIMIT)
    sys.stdout.buffer.write(raw); sys.stdout.buffer.flush()
    return 0 if result["status"] == "OBSERVED_NAMESPACE_PREREQUISITE" else 1


if __name__ == "__main__":
    try: raise SystemExit(run(sys.argv[1:]))
    except SystemExit: raise
    except BaseException:
        sys.stderr.write("DG17_NAMESPACE_WORKER_REFUSED\n")
        raise SystemExit(1)
