#!/usr/bin/env python3
"""Repo-only Windows whole-owner Job diagnostic; never native authority.

Adapted from the retained 9,496-byte windows_job_measure.py, SHA-256
6dc21e695a1a8ab5feee620d13a2ce9539736adc2632e07327396f0ff8391bda.
The historical file remains unchanged. Completion notifications are not
guaranteed: missing/unknown messages or unreconciled kernel counts refuse.
This Job census cannot prove that an external broker did no work outside it.
The separate operation qualifier owns exact source/command/required-executable
binding and native accepting readbacks. No calibration or effect is granted.

Win32 contracts:
https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-jobobject_associate_completion_port
https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-jobobject_basic_accounting_information
"""
from __future__ import annotations

import ctypes as C
from ctypes import wintypes as W
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import time


SCHEMA = "implementaudit.windows-job-measurement.v1"
MAX_PROCESS_EVENTS = 65536
MAX_OBSERVED_PROCESSES = 8192
JOB_FLAGS = 0x2000  # KILL_ON_JOB_CLOSE only; neither breakaway flag is admitted.
JOB_MESSAGES = {4: "ACTIVE_PROCESS_ZERO", 6: "NEW_PROCESS", 7: "EXIT_PROCESS",
                8: "ABNORMAL_EXIT_PROCESS"}


class MeasurementError(RuntimeError):
    """A complete native Job diagnostic could not be established."""


def reconcile_process_events(events, total, root_pid):
    """Validate complete ordered lifetimes against independent kernel accounting.

    A recycled child PID is admitted only after its earlier lifetime exited.
    The retained root handle forbids root PID recycling during this operation.
    ACTIVE_PROCESS_ZERO is required once, last, with no unmatched lifetimes.
    A complete stream is a census of this Job only, not external broker work.
    """
    if (type(total) is not int or not 0 < total <= 0xffffffff
            or type(root_pid) is not int or not 0 < root_pid <= 0xffffffff
            or type(events) is not list or not 1 <= len(events) <= MAX_PROCESS_EVENTS):
        raise MeasurementError("invalid or unbounded process-event accounting input")
    active = set()
    created = exited = abnormal = root_creations = zero = 0
    for index, row in enumerate(events):
        if type(row) is not dict or set(row) != {"event", "pid"}:
            raise MeasurementError("process event has an unknown schema")
        name, pid = row["event"], row["pid"]
        if type(name) is not str or name not in JOB_MESSAGES.values() or type(pid) is not int:
            raise MeasurementError("unknown, lost or untyped process event")
        if name == "ACTIVE_PROCESS_ZERO":
            if pid != 0 or active or zero or index != len(events) - 1:
                raise MeasurementError("terminal zero event is early, repeated or inconsistent")
            zero += 1
            continue
        if not 0 < pid <= 0xffffffff or zero:
            raise MeasurementError("process event has an invalid PID or follows terminal zero")
        if name == "NEW_PROCESS":
            if pid in active:
                raise MeasurementError("duplicate creation for a live process PID")
            active.add(pid)
            created += 1
            if pid == root_pid:
                root_creations += 1
                if root_creations != 1:
                    raise MeasurementError("retained root PID was recreated")
        else:
            if pid not in active:
                raise MeasurementError("process exit has no unique preceding creation")
            active.remove(pid)
            exited += 1
            abnormal += name == "ABNORMAL_EXIT_PROCESS"
    if active or root_creations != 1 or zero != 1 or created != total or exited != total:
        raise MeasurementError("process events are incomplete or differ from the kernel total")
    return {"creation_event_count": created, "exit_event_count": exited,
            "abnormal_exit_event_count": abnormal, "active_process_zero_count": zero,
            "complete_memory_scope_valid": True}


SIZE = C.c_size_t
U64 = C.c_ulonglong


class Limits(C.Structure):
    _fields_ = [("process_time", C.c_longlong), ("job_time", C.c_longlong),
                ("flags", W.DWORD), ("min_ws", SIZE), ("max_ws", SIZE),
                ("active_limit", W.DWORD), ("affinity", SIZE),
                ("priority", W.DWORD), ("scheduling", W.DWORD)]


class IO(C.Structure):
    _fields_ = [(name, U64) for name in ("read_ops", "write_ops", "other_ops",
                                       "read_bytes", "write_bytes", "other_bytes")]


class Extended(C.Structure):
    _fields_ = [("basic", Limits), ("io", IO), ("process_limit", SIZE),
                ("job_limit", SIZE), ("peak_process_commit", SIZE), ("peak_job_commit", SIZE)]


class Accounting(C.Structure):
    _fields_ = [(name, C.c_longlong) for name in ("user", "kernel", "period_user", "period_kernel")] + [
        ("faults", W.DWORD), ("total", W.DWORD), ("active", W.DWORD), ("terminated", W.DWORD)]


class CompletionAssociation(C.Structure):
    _fields_ = [("key", C.c_void_p), ("port", W.HANDLE)]


class Startup(C.Structure):
    _fields_ = [("cb", W.DWORD), ("reserved", W.LPWSTR), ("desktop", W.LPWSTR),
                ("title", W.LPWSTR), ("x", W.DWORD), ("y", W.DWORD),
                ("xsize", W.DWORD), ("ysize", W.DWORD), ("xchars", W.DWORD),
                ("ychars", W.DWORD), ("fill", W.DWORD), ("flags", W.DWORD),
                ("show", W.WORD), ("reserved2_size", W.WORD),
                ("reserved2", C.c_void_p), ("stdin", W.HANDLE),
                ("stdout", W.HANDLE), ("stderr", W.HANDLE)]


class StartupEx(C.Structure):
    _fields_ = [("startup", Startup), ("attributes", C.c_void_p)]


class ProcessInfo(C.Structure):
    _fields_ = [("process", W.HANDLE), ("thread", W.HANDLE), ("pid", W.DWORD), ("tid", W.DWORD)]


class _WindowsAPI:
    def __init__(self):
        self.kernel32 = C.WinDLL("kernel32", use_last_error=True)

        def bind(name, result, *arguments):
            function = getattr(self.kernel32, name)
            function.restype, function.argtypes = result, arguments
            return function

        self.create_job = bind("CreateJobObjectW", W.HANDLE, C.c_void_p, W.LPCWSTR)
        self.set_job = bind("SetInformationJobObject", W.BOOL, W.HANDLE, C.c_int, C.c_void_p, W.DWORD)
        self.query_job = bind("QueryInformationJobObject", W.BOOL, W.HANDLE, C.c_int, C.c_void_p, W.DWORD, C.c_void_p)
        self.assign_job = bind("AssignProcessToJobObject", W.BOOL, W.HANDLE, W.HANDLE)
        self.in_job = bind("IsProcessInJob", W.BOOL, W.HANDLE, W.HANDLE, C.POINTER(W.BOOL))
        self.close = bind("CloseHandle", W.BOOL, W.HANDLE)
        self.terminate_job = bind("TerminateJobObject", W.BOOL, W.HANDLE, W.UINT)
        self.terminate_process = bind("TerminateProcess", W.BOOL, W.HANDLE, W.UINT)
        self.init_attrs = bind("InitializeProcThreadAttributeList", W.BOOL, C.c_void_p, W.DWORD, W.DWORD, C.POINTER(SIZE))
        self.update_attrs = bind("UpdateProcThreadAttribute", W.BOOL, C.c_void_p, W.DWORD, SIZE, C.c_void_p, SIZE, C.c_void_p, C.c_void_p)
        self.delete_attrs = bind("DeleteProcThreadAttributeList", None, C.c_void_p)
        self.create_process = bind("CreateProcessW", W.BOOL, W.LPCWSTR, W.LPWSTR, C.c_void_p, C.c_void_p,
                                   W.BOOL, W.DWORD, C.c_void_p, W.LPCWSTR, C.POINTER(Startup), C.POINTER(ProcessInfo))
        self.resume = bind("ResumeThread", W.DWORD, W.HANDLE)
        self.wait = bind("WaitForSingleObject", W.DWORD, W.HANDLE, W.DWORD)
        self.exit_code = bind("GetExitCodeProcess", W.BOOL, W.HANDLE, C.POINTER(W.DWORD))
        self.open_process = bind("OpenProcess", W.HANDLE, W.DWORD, W.BOOL, W.DWORD)
        self.process_image = bind("QueryFullProcessImageNameW", W.BOOL, W.HANDLE, W.DWORD, W.LPWSTR, C.POINTER(W.DWORD))
        self.create_port = bind("CreateIoCompletionPort", W.HANDLE, W.HANDLE, W.HANDLE, SIZE, W.DWORD)
        self.get_completion = bind("GetQueuedCompletionStatus", W.BOOL, W.HANDLE, C.POINTER(W.DWORD),
                                   C.POINTER(SIZE), C.POINTER(C.c_void_p), W.DWORD)

    @staticmethod
    def checked(value, operation):
        if not value:
            raise MeasurementError(operation + " failed; Win32 error " + str(C.get_last_error()))
        return value


def _image_hash(path):
    """Hash one held image file and reject changes during its readback."""
    with Path(path).open("rb") as stream:
        before = os.fstat(stream.fileno())
        digest = hashlib.sha256()
        while chunk := stream.read(1024 * 1024):
            digest.update(chunk)
        after = os.fstat(stream.fileno())
        current = os.stat(path)
    identity = lambda row: (row.st_dev, row.st_ino, row.st_size, row.st_mtime_ns)
    if identity(before) != identity(after) or identity(after) != identity(current):
        raise MeasurementError("observed process image changed during hashing")
    return digest.hexdigest()


def measure(command: list[str], cwd: Path, environment: dict[str, str], out: Path,
            *, diagnostic_timeout_seconds=180) -> dict:
    """Measure once; errors retain unadmitted evidence before Job containment.

    The harness is outside the Job. The caller must separately bind this
    command and actual interpreter/Git observations to one intended operation.
    No numeric qualification, baseline subtraction, retry or native grant is
    performed here. Completion-event accounting is this Job's census only.
    """
    if os.name != "nt" or sys.platform != "win32":
        raise MeasurementError("Actual Windows kernel is required before output or process creation")
    if (type(command) is not list or not command
            or any(type(value) is not str or "\0" in value for value in command)
            or not Path(command[0]).is_absolute() or not Path(command[0]).is_file()
            or not isinstance(cwd, Path) or not cwd.is_absolute() or not cwd.is_dir()
            or not isinstance(out, Path) or type(environment) is not dict
            or any(type(key) is not str or not key or "=" in key or "\0" in key
                   or type(value) is not str or "\0" in value for key, value in environment.items())
            or type(diagnostic_timeout_seconds) not in (int, float)
            or not math.isfinite(diagnostic_timeout_seconds) or diagnostic_timeout_seconds <= 0):
        raise MeasurementError("invalid Windows measurement command, paths, environment or timeout")
    import msvcrt

    api = _WindowsAPI()
    out.mkdir(mode=0o700, exist_ok=False)
    record = {"schema": SCHEMA, "platform": "win32", "command": list(command), "cwd": str(cwd),
              "status": "INCOMPLETE_UNADMITTED", "metric_admission": "UNADMITTED_DIAGNOSTIC",
              "root_pid": None, "started_suspended": False, "assigned_before_resume": False,
              "root_job_membership_confirmed": False, "complete_memory_scope_valid": False,
              "process_events": [], "observed_processes": [], "process_observation_failures": [],
              "creation_event_count": 0, "exit_event_count": 0,
              "sampled_pids": [], "sampled_process_images": {}, "sampled_pid_census_complete": False,
              "initial_job_flags": JOB_FLAGS, "terminal_job_flags": None,
              "terminal_breakaway_allowed": None, "baseline_subtracted_bytes": 0,
              "harness_included": False, "diagnostic_timeout_seconds": diagnostic_timeout_seconds,
              "containment": "private unnamed job; owner and descendants; KILL_ON_JOB_CLOSE",
              "containment_status": "NOT_STARTED", "cleanup_complete": False,
              "root_exit_observed_ms": None, "completion_port_associated_before_assignment": False}
    info = ProcessInfo()
    job = port = None
    attr_buf = None
    attrs_initialized = assigned = terminal = False
    began = None
    files, inherited_handles, process_handles = [], [], []
    observed_pids = set()
    error = None
    cleanup_errors = []
    evidence = (out / "measurement.json").open("x+", encoding="utf-8", newline="\n")

    def save():
        evidence.seek(0)
        json.dump(record, evidence, indent=2, sort_keys=True, allow_nan=False)
        evidence.write("\n")
        evidence.truncate()
        evidence.flush()
        os.fsync(evidence.fileno())

    def snapshot_job():
        accounting = Accounting()
        api.checked(api.query_job(job, 1, C.byref(accounting), C.sizeof(accounting), None), "query accounting")
        extended = Extended()
        api.checked(api.query_job(job, 9, C.byref(extended), C.sizeof(extended), None), "query Job peak")
        record.update(kernel_total_processes=accounting.total, terminal_active_processes=accounting.active,
                      kernel_terminated_processes=accounting.terminated,
                      peak_job_committed_bytes=extended.peak_job_commit,
                      peak_single_process_committed_bytes=extended.peak_process_commit,
                      terminal_job_flags=extended.basic.flags,
                      terminal_breakaway_allowed=bool(extended.basic.flags & 0x1800))
        if extended.basic.flags != JOB_FLAGS:
            raise MeasurementError("private Job flags changed or breakaway became admissible")
        return accounting

    def observe_process(pid, held=None):
        if pid in observed_pids:
            return
        if len(process_handles) >= MAX_OBSERVED_PROCESSES:
            raise MeasurementError("process image custody exceeds the recorder's physical bound")
        handle = held or api.open_process(0x1000, False, pid)
        if not handle:
            record["process_observation_failures"].append({"pid": pid, "reason": "PROCESS_ALREADY_GONE_OR_UNOPENABLE"})
            return
        # Retain every successfully opened handle until terminal accounting;
        # otherwise a later observation could silently refer to a recycled PID.
        if held is None:
            process_handles.append(handle)
        member = W.BOOL()
        api.checked(api.in_job(handle, job, C.byref(member)), "observe process Job membership")
        if not member.value:
            raise MeasurementError("observed process is outside the exact Job or PID identity was recycled")
        image = C.create_unicode_buffer(32768)
        length = W.DWORD(len(image))
        if not api.process_image(handle, 0, image, C.byref(length)):
            record["process_observation_failures"].append({"pid": pid, "reason": "IMAGE_UNAVAILABLE"})
            return
        row = {"pid": pid, "image": image.value, "image_sha256": _image_hash(image.value), "in_job": True}
        record["observed_processes"].append(row)
        observed_pids.add(pid)
        record["sampled_pids"] = sorted(observed_pids)
        record["sampled_process_images"][str(pid)] = image.value

    def receive(timeout_ms):
        if began is not None and not terminal and (time.perf_counter_ns() - began) / 1e9 > diagnostic_timeout_seconds:
            raise MeasurementError("private Job exceeded diagnostic containment timeout")
        number, key, payload = W.DWORD(), SIZE(), C.c_void_p()
        ok = api.get_completion(port, C.byref(number), C.byref(key), C.byref(payload), timeout_ms)
        if not ok:
            code = C.get_last_error()
            if code == 258 and payload.value is None:
                return False
            raise MeasurementError("completion dequeue failed; Win32 error " + str(code))
        if len(record["process_events"]) >= MAX_PROCESS_EVENTS:
            raise MeasurementError("process event capture exceeds the recorder's physical bound")
        name = JOB_MESSAGES.get(number.value, "UNKNOWN_" + str(number.value))
        if key.value != 1:
            name = "UNKNOWN_COMPLETION_KEY_" + str(key.value)
        event = {"event": name, "pid": payload.value or 0}
        record["process_events"].append(event)
        record["creation_event_count"] += name == "NEW_PROCESS"
        record["exit_event_count"] += name in {"EXIT_PROCESS", "ABNORMAL_EXIT_PROCESS"}
        if name not in JOB_MESSAGES.values():
            raise MeasurementError("unknown Job completion notification")
        if name == "NEW_PROCESS":
            observe_process(event["pid"])
        return True

    try:
        save()
        job = api.checked(api.create_job(None, None), "create Job")
        limits = Extended()
        limits.basic.flags = JOB_FLAGS
        api.checked(api.set_job(job, 9, C.byref(limits), C.sizeof(limits)), "set Job containment")
        port = api.checked(api.create_port(W.HANDLE(-1), None, 0, 1), "create completion port")
        association = CompletionAssociation(1, port)
        api.checked(api.set_job(job, 7, C.byref(association), C.sizeof(association)), "associate inactive Job completion port")
        record["completion_port_associated_before_assignment"] = True
        files.append(open(os.devnull, "rb"))
        files.append((out / "stdout.bin").open("xb"))
        files.append((out / "stderr.bin").open("xb"))
        inherited_handles = [msvcrt.get_osfhandle(stream.fileno()) for stream in files]
        for handle in inherited_handles:
            os.set_handle_inheritable(handle, True)
        size = SIZE()
        api.init_attrs(None, 1, 0, C.byref(size))
        if not size.value:
            raise MeasurementError("process attribute-list sizing failed")
        attr_buf = C.create_string_buffer(size.value)
        api.checked(api.init_attrs(attr_buf, 1, 0, C.byref(size)), "initialize process attributes")
        attrs_initialized = True
        allowed = (W.HANDLE * len(inherited_handles))(*inherited_handles)
        api.checked(api.update_attrs(attr_buf, 0, 0x20002, allowed, C.sizeof(allowed), None, None), "limit inherited handles")
        startup = StartupEx()
        startup.startup.cb = C.sizeof(startup)
        startup.startup.flags = 0x100
        startup.startup.stdin, startup.startup.stdout, startup.startup.stderr = inherited_handles
        startup.attributes = C.cast(attr_buf, C.c_void_p)
        environment_block = C.create_unicode_buffer("\0".join(key + "=" + value for key, value in
            sorted(environment.items(), key=lambda pair: pair[0].upper())) + "\0\0")
        command_line = C.create_unicode_buffer(subprocess.list2cmdline(command))
        began = time.perf_counter_ns()
        api.checked(api.create_process(command[0], command_line, None, None, True,
            0x4 | 0x400 | 0x80000 | 0x08000000, environment_block, str(cwd),
            C.byref(startup.startup), C.byref(info)), "create suspended root")
        record.update(root_pid=info.pid, started_suspended=True, containment_status="SUSPENDED_UNASSIGNED")
        api.checked(api.assign_job(job, info.process), "assign suspended root to Job")
        assigned = True
        member = W.BOOL()
        api.checked(api.in_job(info.process, job, C.byref(member)), "confirm root Job membership")
        if not member.value:
            raise MeasurementError("root is not in its private Job before resume")
        record.update(assigned_before_resume=True, root_job_membership_confirmed=True, containment_status="SUSPENDED_IN_JOB")
        observe_process(info.pid, held=info.process)
        save()
        if (time.perf_counter_ns() - began) / 1e9 > diagnostic_timeout_seconds:
            raise MeasurementError("suspended root preparation exceeded diagnostic containment timeout")
        prior_suspend_count = api.resume(info.thread)
        record["root_prior_suspend_count"] = prior_suspend_count
        if prior_suspend_count == 0xffffffff:
            raise MeasurementError("root resume failed; Win32 error " + str(C.get_last_error()))
        if prior_suspend_count != 1:
            raise MeasurementError("root suspension changed before the sole resume")
        api.checked(api.close(info.thread), "close resumed thread handle")
        info.thread = None
        record["containment_status"] = "RUNNING_IN_JOB"
        for handle in inherited_handles:
            os.set_handle_inheritable(handle, False)
        while True:
            receive(10)
            while receive(0):
                pass
            state = api.wait(info.process, 0)
            if state not in (0, 258):
                raise MeasurementError("root exit observation failed")
            now = time.perf_counter_ns()
            if state == 0 and record["root_exit_observed_ms"] is None:
                record["root_exit_observed_ms"] = (now - began) / 1e6
            accounting = snapshot_job()
            if state == 0 and accounting.active == 0:
                terminal = True
                record["elapsed_ms"] = (time.perf_counter_ns() - began) / 1e6
                break
            if (now - began) / 1e9 > diagnostic_timeout_seconds:
                raise MeasurementError("private Job exceeded diagnostic containment timeout")
        # The operation timer already ended at root exit + kernel active zero.
        # Allow only a bounded tail for already-terminal notification delivery.
        # Missing delivery is refusal, never inferred from the empty Job alone.
        drain_deadline = time.perf_counter_ns() + 1000000000
        while (not any(row["event"] == "ACTIVE_PROCESS_ZERO" for row in record["process_events"])
               and time.perf_counter_ns() < drain_deadline):
            receive(10)
        while receive(0):
            pass
        accounting = snapshot_job()
        if accounting.active != 0:
            raise MeasurementError("Job ceased to be terminal during final accounting")
        code = W.DWORD()
        api.checked(api.exit_code(info.process, C.byref(code)), "read root exit code")
        record["exit_code"] = code.value
        record.update(reconcile_process_events(record["process_events"], accounting.total, info.pid))
        record["containment_status"] = "ROOT_EXITED_AND_JOB_EMPTY"
    except BaseException as exc:
        error = exc
        record["complete_memory_scope_valid"] = False
        record["error"] = {"type": type(exc).__name__, "message": str(exc)}
        if terminal:
            record["containment_status"] = "ROOT_EXITED_AND_JOB_EMPTY"
        if began is not None and "elapsed_ms" not in record:
            record["elapsed_ms"] = (time.perf_counter_ns() - began) / 1e6
        if job:
            try:
                snapshot_job()
            except BaseException as snapshot_error:
                record["partial_accounting_error"] = type(snapshot_error).__name__ + ": " + str(snapshot_error)
        # Retain observed effects and incomplete accounting BEFORE containment.
        try:
            save()
        except BaseException as save_error:
            cleanup_errors.append("pre-containment evidence save: " + type(save_error).__name__)
    finally:
        if info.process and not terminal:
            record["containment_status"] = "TERMINATION_REQUESTED"
            try:
                if assigned:
                    api.checked(api.terminate_job(job, 125), "terminate incomplete Job")
                else:
                    api.checked(api.terminate_process(info.process, 125), "terminate unassigned suspended root")
                if api.wait(info.process, 30000) != 0:
                    raise MeasurementError("incomplete root termination did not become observable")
                if assigned:
                    containment_deadline = time.perf_counter_ns() + 5000000000
                    while snapshot_job().active:
                        if time.perf_counter_ns() >= containment_deadline:
                            raise MeasurementError("terminated Job did not become observably empty")
                        time.sleep(0.01)
                record["containment_status"] = "TERMINATED_AND_JOB_EMPTY" if assigned else "TERMINATED_UNASSIGNED_ROOT"
            except BaseException as containment_error:
                cleanup_errors.append("containment: " + str(containment_error))
        if attrs_initialized:
            try:
                api.delete_attrs(attr_buf)
            except BaseException as attribute_error:
                cleanup_errors.append("attribute cleanup: " + str(attribute_error))
        for handle in inherited_handles:
            try:
                os.set_handle_inheritable(handle, False)
            except OSError as reset_error:
                cleanup_errors.append("inheritance reset: " + str(reset_error))
        for handle in [*process_handles, info.thread, info.process, job, port]:
            if handle and not api.close(handle):
                cleanup_errors.append("close native handle; Win32 error " + str(C.get_last_error()))
        for stream in files:
            try:
                stream.close()
            except OSError as close_error:
                cleanup_errors.append("stdio close: " + str(close_error))
        record["cleanup_complete"] = not cleanup_errors
        if cleanup_errors:
            record["cleanup_errors"] = cleanup_errors
            record["complete_memory_scope_valid"] = False
        if error is None and not cleanup_errors:
            record["status"] = "COMPLETE_UNADMITTED"
        try:
            save()
        finally:
            evidence.close()
    if error is not None:
        if isinstance(error, (KeyboardInterrupt, SystemExit, MeasurementError)):
            raise error
        raise MeasurementError("Windows Job measurement failed: " + str(error)) from error
    if cleanup_errors:
        raise MeasurementError("Windows Job measurement cleanup was incomplete")
    return record
