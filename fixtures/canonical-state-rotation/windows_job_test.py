#!/usr/bin/env python3
"""Portable recorder controls; native integration requires an entitled Windows run."""
from __future__ import annotations

import copy
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest


SOURCE = Path(__file__).resolve().parents[2] / "scripts/r0039-windows-job.py"
M = None
if SOURCE.is_file():
    spec = importlib.util.spec_from_file_location("r0039_windows_job", SOURCE)
    M = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(M)


def event(name, pid):
    return {"event": name, "pid": pid}


def complete_events():
    return [event("NEW_PROCESS", 10), event("NEW_PROCESS", 20),
            event("EXIT_PROCESS", 20), event("EXIT_PROCESS", 10),
            event("ACTIVE_PROCESS_ZERO", 0)]


class ReconcileProcessEvents(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(M, "The maintained Windows Job recorder is missing")

    def test_complete_lifetimes_match_kernel_total(self):
        summary = M.reconcile_process_events(complete_events(), 2, 10)
        self.assertEqual(summary["creation_event_count"], 2)
        self.assertEqual(summary["exit_event_count"], 2)
        self.assertEqual(summary["abnormal_exit_event_count"], 0)
        self.assertEqual(summary["active_process_zero_count"], 1)
        self.assertIs(summary["complete_memory_scope_valid"], True)

    def test_recycled_child_pid_is_two_distinct_completed_lifetimes(self):
        events = [event("NEW_PROCESS", 10), event("NEW_PROCESS", 20),
                  event("EXIT_PROCESS", 20), event("NEW_PROCESS", 20),
                  event("ABNORMAL_EXIT_PROCESS", 20), event("EXIT_PROCESS", 10),
                  event("ACTIVE_PROCESS_ZERO", 0)]
        summary = M.reconcile_process_events(events, 3, 10)
        self.assertEqual(summary["creation_event_count"], 3)
        self.assertEqual(summary["exit_event_count"], 3)
        self.assertEqual(summary["abnormal_exit_event_count"], 1)

    def test_missing_new_or_exit_event_refuses(self):
        for index in (0, 1, 2, 3):
            events = complete_events()
            del events[index]
            with self.subTest(index=index), self.assertRaises(M.MeasurementError):
                M.reconcile_process_events(events, 2, 10)

    def test_duplicate_live_pid_and_duplicate_exit_refuse(self):
        for insertion in (event("NEW_PROCESS", 20), event("EXIT_PROCESS", 20)):
            events = complete_events()
            events.insert(2 if insertion["event"] == "NEW_PROCESS" else 3, insertion)
            with self.subTest(insertion=insertion), self.assertRaises(M.MeasurementError):
                M.reconcile_process_events(events, 2, 10)

    def test_root_must_have_exactly_one_lifetime(self):
        for root_pid in (99, 20):
            events = complete_events()
            if root_pid == 20:
                events[3:3] = [event("NEW_PROCESS", 20), event("EXIT_PROCESS", 20)]
            with self.subTest(root=root_pid), self.assertRaises(M.MeasurementError):
                M.reconcile_process_events(events, 3 if root_pid == 20 else 2, root_pid)

    def test_kernel_total_mismatch_and_untyped_totals_refuse(self):
        for total in (0, 1, 3, -1, True, 2.0, "2", None):
            with self.subTest(total=total), self.assertRaises(M.MeasurementError):
                M.reconcile_process_events(complete_events(), total, 10)

    def test_missing_early_duplicate_or_nonterminal_zero_refuses(self):
        variants = [complete_events()[:-1],
                    [event("ACTIVE_PROCESS_ZERO", 0)] + complete_events(),
                    complete_events() + [event("ACTIVE_PROCESS_ZERO", 0)],
                    complete_events() + [event("NEW_PROCESS", 30), event("EXIT_PROCESS", 30)]]
        for events in variants:
            with self.subTest(events=events), self.assertRaises(M.MeasurementError):
                M.reconcile_process_events(events, 2, 10)

    def test_unknown_message_or_capture_loss_refuses(self):
        for name in ("UNKNOWN_42", "EVENTS_LOST", "ACTIVE_PROCESS_LIMIT"):
            events = complete_events()
            events.insert(2, event(name, 20))
            with self.subTest(name=name), self.assertRaises(M.MeasurementError):
                M.reconcile_process_events(events, 2, 10)

    def test_malformed_pid_or_event_schema_refuses(self):
        malformed = [event("NEW_PROCESS", pid) for pid in (True, 0, -1, 20.0, "20", None)]
        malformed += [{"event": "NEW_PROCESS"}, {"pid": 20},
                      {"event": "NEW_PROCESS", "pid": 20, "trusted": True},
                      event("ACTIVE_PROCESS_ZERO", 20), None, []]
        for row in malformed:
            events = complete_events()
            events[1] = row
            with self.subTest(row=row), self.assertRaises(M.MeasurementError):
                M.reconcile_process_events(events, 2, 10)

    def test_input_is_not_changed(self):
        events = complete_events()
        before = copy.deepcopy(events)
        M.reconcile_process_events(events, 2, 10)
        self.assertEqual(events, before)


class PlatformBoundary(unittest.TestCase):
    @unittest.skipIf(os.name == "nt", "This control proves actual non-Windows refusal")
    def test_non_windows_refuses_before_any_output_or_launch(self):
        self.assertIsNotNone(M, "The maintained Windows Job recorder is missing")
        with tempfile.TemporaryDirectory(prefix="r0039-windows-refusal-") as temporary:
            out = Path(temporary) / "never-created"
            with self.assertRaisesRegex(M.MeasurementError, "Windows"):
                M.measure([], Path(temporary), {}, out)
            self.assertEqual(list(Path(temporary).iterdir()), [])


NATIVE_AUTHORIZED = os.name == "nt" and os.environ.get("IMPLEMENTAUDIT_WINDOWS_JOB_CONTROLS") == "1"


@unittest.skipUnless(NATIVE_AUTHORIZED, "Requires entitled Windows host and explicit IMPLEMENTAUDIT_WINDOWS_JOB_CONTROLS=1")
class WindowsKernelIntegration(unittest.TestCase):
    def test_parent_child_allocation_and_actual_process_membership(self):
        with tempfile.TemporaryDirectory(prefix="r0039-windows-job-") as temporary:
            parent = Path(temporary)
            child = "import os,time; allocation=bytearray(24*1024*1024); print(os.getpid(),flush=True); time.sleep(0.3)"
            program = ("import subprocess,sys; allocation=bytearray(16*1024*1024); "
                       "subprocess.run([sys.executable,'-B','-c'," + repr(child) + "],check=True)")
            result = M.measure([sys.executable, "-B", "-c", program], parent, dict(os.environ), parent / "operation")
            self.assertEqual(result["exit_code"], 0)
            self.assertIs(result["complete_memory_scope_valid"], True)
            self.assertEqual(result["kernel_total_processes"], result["creation_event_count"])
            self.assertEqual(result["creation_event_count"], result["exit_event_count"])
            self.assertGreaterEqual(result["kernel_total_processes"], 2)
            self.assertEqual(result["terminal_active_processes"], 0)
            self.assertGreaterEqual(result["peak_job_committed_bytes"], 40 * 1024 * 1024)
            self.assertEqual(result["baseline_subtracted_bytes"], 0)
            self.assertFalse(result["sampled_pid_census_complete"])
            self.assertIs(result["started_suspended"], True)
            self.assertIs(result["assigned_before_resume"], True)
            self.assertIs(result["root_job_membership_confirmed"], True)
            self.assertEqual(result["root_prior_suspend_count"], 1)
            root = next(row for row in result["observed_processes"] if row["pid"] == result["root_pid"])
            self.assertIs(root["in_job"], True)
            self.assertEqual(len(root["image_sha256"]), 64)
            child_pid = int((parent / "operation/stdout.bin").read_bytes())
            actual_child = next(row for row in result["observed_processes"] if row["pid"] == child_pid)
            self.assertIs(actual_child["in_job"], True)
            self.assertTrue(Path(actual_child["image"]).samefile(sys.executable))
            self.assertEqual(json.loads((parent / "operation/measurement.json").read_bytes()), result)

    def test_actual_git_root_identity_is_observed_before_resume(self):
        selected = os.environ.get("IMPLEMENTAUDIT_WINDOWS_JOB_GIT", r"C:\Program Files\Git\mingw64\bin\git.exe")
        spec = importlib.util.spec_from_file_location("r0039_windows_git_policy", SOURCE.with_name("check-r0039-windows-resume.py"))
        policy = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(policy)
        policy.direct_git_layout(selected)
        git = Path(selected)
        if not git.is_file():
            self.skipTest("The fixed physical Git executable is unavailable")
        with tempfile.TemporaryDirectory(prefix="r0039-windows-git-") as temporary:
            parent = Path(temporary)
            result = M.measure([str(git), "--version"], parent, dict(os.environ), parent / "operation")
            self.assertEqual(result["exit_code"], 0)
            self.assertIs(result["complete_memory_scope_valid"], True)
            root = next(row for row in result["observed_processes"] if row["pid"] == result["root_pid"])
            self.assertTrue(Path(root["image"]).samefile(git))
            self.assertIs(root["in_job"], True)

    def test_timeout_retains_partial_record_and_does_not_retry(self):
        with tempfile.TemporaryDirectory(prefix="r0039-windows-timeout-") as temporary:
            parent = Path(temporary)
            out = parent / "operation"
            with self.assertRaises(M.MeasurementError):
                M.measure([sys.executable, "-B", "-c", "import time; time.sleep(10)"],
                          parent, dict(os.environ), out, diagnostic_timeout_seconds=0.2)
            partial = json.loads((out / "measurement.json").read_bytes())
            self.assertIs(partial["complete_memory_scope_valid"], False)
            self.assertEqual(partial["status"], "INCOMPLETE_UNADMITTED")
            self.assertEqual(partial["metric_admission"], "UNADMITTED_DIAGNOSTIC")
            original = (out / "measurement.json").read_bytes()
            with self.assertRaises((M.MeasurementError, FileExistsError)):
                M.measure([sys.executable, "-B", "-c", "raise SystemExit(0)"], parent, dict(os.environ), out)
            self.assertEqual((out / "measurement.json").read_bytes(), original)


if __name__ == "__main__":
    unittest.main()
