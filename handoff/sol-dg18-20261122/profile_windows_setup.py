"""Observe the unmodified first A4 method in one ordinary Windows process."""
import builtins
import ctypes
import importlib
import json
import os
from pathlib import Path
import platform
import sys
import tempfile
import tracemalloc
import unittest


sys.path.insert(0, str(Path(__file__).resolve().parent))
from local_windows_control import BASE, DRAFT_GUARD, FIXTURES, ROOT, indexed_inputs, require, sha256, verify_source


class ProcessCounters(ctypes.Structure):
    _fields_ = [("size", ctypes.c_ulong), ("faults", ctypes.c_ulong)] + [
        (name, ctypes.c_size_t)
        for name in ("peak", "working", "peak_paged", "paged", "peak_nonpaged", "nonpaged", "pagefile", "peak_pagefile")
    ]


class SetupObserver:
    def __init__(self, setup_code, load_code):
        kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel.GetCurrentProcess.argtypes = []
        kernel.GetCurrentProcess.restype = ctypes.c_void_p
        self.handle = kernel.GetCurrentProcess()
        psapi = ctypes.WinDLL("psapi", use_last_error=True)
        self.read_counters = psapi.GetProcessMemoryInfo
        self.read_counters.argtypes = [ctypes.c_void_p, ctypes.POINTER(ProcessCounters), ctypes.c_ulong]
        self.read_counters.restype = ctypes.c_int
        self.counters = ProcessCounters()
        self.counters.size = ctypes.sizeof(self.counters)
        self.setup_code, self.load_code = setup_code, load_code
        self.owner = None
        self.compile_site = None
        self.compilations = 0
        self.events = []

    def record(self, kind, site=None):
        require(len(self.events) < 48, "setup observation exceeds closed record bound")
        live, interval_peak = tracemalloc.get_traced_memory()
        tracer_overhead = tracemalloc.get_tracemalloc_memory()
        counters = self.counters
        require(self.read_counters(self.handle, ctypes.byref(counters), counters.size) and counters.peak > 0,
                "native Win32 counters unavailable")
        self.events.append({
            "kind": kind, "owner": self.owner, "compile_site": site,
            "pid": os.getpid(),
            "lifetime_peak_working_set_bytes": counters.peak,
            "current_working_set_bytes": counters.working,
            "python_traced_live_bytes": live,
            "python_traced_interval_peak_bytes": interval_peak,
            "python_tracer_metadata_bytes": tracer_overhead,
        })

    def profile(self, frame, event, arg):
        code = frame.f_code
        if code is self.setup_code and event in ("call", "return"):
            self.record("setup_enter" if event == "call" else "setup_return")
        elif code is self.load_code and event == "call":
            require(self.owner is None, "recursive setup module loader")
            self.owner = frame.f_locals["name"]
            self.record("load_enter")
        elif code is self.load_code and event == "return":
            require(self.compile_site is None, "unclosed compile event")
            self.record("load_return")
            self.owner = None
        elif self.owner and arg is builtins.compile:
            if event == "c_call":
                require(self.compile_site is None, "recursive compile")
                self.compile_site = code.co_name
                self.compilations += 1
                self.record("compile_enter", self.compile_site)
                # Python tracer bookkeeping only. The Win32 lifetime peak is never reset.
                tracemalloc.reset_peak()
            elif event in ("c_return", "c_exception"):
                require(code.co_name == self.compile_site, "compile source changed before terminal sample")
                self.record("compile_return" if event == "c_return" else "compile_error", self.compile_site)
                self.compile_site = None


def run():
    require(os.name == "nt" and Path.cwd() == ROOT, "invoke on the owned Windows worktree")
    require(not sys.flags.optimize and sys.getprofile() is None and not tracemalloc.is_tracing(),
            "ordinary unoptimized Python with no pre-existing observer required")
    rows, original, input_pins = indexed_inputs()
    verify_source(rows)
    sys.path.insert(0, str(FIXTURES))
    modules = {}
    with tempfile.TemporaryDirectory(prefix=".d18-setup-", dir=ROOT) as temp:
        tf = tempfile.tempdir
        tempfile.tempdir = temp
        os.environ["R0039_CLAIM_EVIDENCE_DIR"] = str(Path(temp) / "claim")
        os.environ.pop("R0039_CLAIM_RETAIN_ARTIFACTS", None)
        try:
            for file in dict.fromkeys(item[0] for item in original):
                modules[file] = importlib.import_module(Path(file).stem)
            file, cls, method = original[0]
            module = modules[file]
            case_type = getattr(module, cls)
            case = case_type(method)
            observer = SetupObserver(case_type.setUp.__code__, module.load.__code__)
            result = unittest.TestResult()
            tracemalloc.start(1)
            try:
                observer.record("worker_probe_enter")
                sys.setprofile(observer.profile)
                try:
                    unittest.TestSuite([case]).run(result)
                finally:
                    sys.setprofile(None)
                observer.record("worker_probe_return")
            finally:
                tracemalloc.stop()
            cases_pass = result.wasSuccessful() and not result.skipped and result.testsRun == 1
            require((len(result.errors), len(result.failures), result.testsRun) == (0, 0, 1),
                    "original method did not complete its positive assertions")
            require(not case.root.exists(), "original method left its scratch root")
            guard_limit = case.rotate.calibration_contract_v1()["maximum_memory_bytes"]
            require(guard_limit == DRAFT_GUARD, "original guard limit changed")
            require({x.name for x in Path(temp).iterdir()} == {"claim"}, "unexpected observer fixture residue")
            require(not any((Path(temp) / "claim").iterdir()), "unexpected claim-fixture effects")
        finally:
            tempfile.tempdir = tf

    verify_source(rows)
    events = observer.events
    owners = ("claim-run-rotation", "rotate-canonical-state", "read-canonical-pair")
    require(tuple(e["owner"] for e in events if e["kind"] == "load_enter")
            == tuple(e["owner"] for e in events if e["kind"] == "load_return") == owners,
            "incomplete original module load population")
    require(sum(e["kind"] == "compile_return" for e in events) == observer.compilations,
            "compile observations were lost or refused")
    require(any(e["kind"] == "compile_return" and e["owner"] == owners[0]
                and e["compile_site"] == "_capture_claim_load_identity_v1" for e in events),
            "original self-source recompilation was not observed")
    peaks = [row["lifetime_peak_working_set_bytes"] for row in events]
    require(peaks == sorted(peaks) and not Path(temp).exists(), "native peak order or scratch cleanup failed")
    return {
        "schema": "dg18.a4.ordinary-setup-profile.v1",
        "base": BASE, "source_members_verified": len(rows), **input_pins,
        "pid": os.getpid(), "python": platform.python_version(), "platform": platform.platform(),
        "python_executable_sha256": sha256(Path(sys.executable).read_bytes()),
        "historical_method_ordinal": 1, "test": case.id(), "method_passed": cases_pass,
        "record_count": len(events), "windows_lifetime_peak_reset": False,
        "python_interval_peak_reset_only_before_traced_compile": True,
        "guard_limit_bytes_unchanged": guard_limit,
        "complete_a4_executed": False, "guard_acceptance_measured": False,
        "aggregate_job_measured": False, "source_or_native_effect": False,
        "scratch_clean": True, "observations": events,
    }


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
