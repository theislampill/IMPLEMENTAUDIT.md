#!/usr/bin/env python3
"""Stale-intent reconciliation for the eval custody root (#9 phase 2b).

`hosts.py` creates `run-intent.json` BEFORE spawn, `process-started.json`
immediately AFTER spawn, and a create-once `terminal.json` in a finally
path. That covers every in-process failure, but a hard kill of the adapter
process (or host crash / power loss) can still leave an intent with no
terminal record. This module adjudicates those remains truthfully:

    intent exists + terminal absent
        no process-started            -> ERROR / launch-not-confirmed
        bound process still alive     -> RUNNING (no record written)
        host terminal evidence exists -> ERROR / forensic-import-candidate
                                         (labeled; never formal evidence)
        otherwise                     -> ERROR / terminal-state-unverified

It runs before any new run id is claimed, at adapter startup, and as an
explicit recovery command (`python reconcile.py <custody_root>`).
Reconciled terminal records carry `"reconciled": true` and are never
promoted to formal baseline evidence; a forensic import stays labeled.
"""
from __future__ import annotations

import json
import os
import sys


def _pid_alive(pid):
    """Best-effort liveness for a numeric pid; False on any doubt."""
    if not isinstance(pid, int) or pid <= 0:
        return False
    try:
        if os.name == "nt":
            import ctypes
            k32 = ctypes.windll.kernel32
            SYNCHRONIZE = 0x00100000
            h = k32.OpenProcess(SYNCHRONIZE, False, pid)
            if not h:
                return False
            # WAIT_TIMEOUT (0x102) => still running
            rc = k32.WaitForSingleObject(h, 0)
            k32.CloseHandle(h)
            return rc == 0x102
        os.kill(pid, 0)
        return True
    except OSError:
        return False
    except Exception:
        return False


def host_os_name():
    """Coarse host lane OS name recorded in / compared against
    process-started.json ('windows' | 'posix')."""
    return "windows" if os.name == "nt" else "posix"


def host_boot_id():
    """Stable-within-a-boot host identifier; None when unavailable.
    Linux: the kernel boot_id. Windows: the boot epoch derived from
    GetTickCount64, rounded to whole minutes (compared with +/-1 tolerance
    to absorb clock slew at a minute boundary)."""
    if os.name == "posix":
        try:
            return open("/proc/sys/kernel/random/boot_id",
                        encoding="ascii").read().strip()
        except OSError:
            return None
    try:
        import ctypes
        import time as _t
        ticks = int(ctypes.windll.kernel32.GetTickCount64())
        boot_ms = int(_t.time() * 1000) - ticks
        return "winboot-" + str(int(round(boot_ms / 60000.0)))
    except Exception:
        return None


def process_creation_time(pid):
    """Absolute UTC epoch seconds when `pid` was created; None if unknown.
    This is the identity field that distinguishes a RECYCLED pid from the
    original process: a recycled pid has a different creation time.
    Linux: /proc/stat btime + /proc/<pid>/stat field 22 / CLK_TCK
    (absolute, so stable across reads within one boot).
    Windows: GetProcessTimes creation FILETIME (absolute UTC)."""
    if not isinstance(pid, int) or pid <= 0:
        return None
    if os.name == "posix":
        try:
            stat = open("/proc/%d/stat" % pid, "rb").read().decode("latin-1")
            # comm may contain spaces/parens; fields resume after last ')'
            rest = stat[stat.rindex(")") + 2:].split()
            start_jiffies = int(rest[19])          # overall field 22
            hz = os.sysconf("SC_CLK_TCK") or 100
            btime = None
            for ln in open("/proc/stat", encoding="ascii", errors="replace"):
                if ln.startswith("btime "):
                    btime = int(ln.split()[1])
                    break
            if btime is None:
                return None
            return round(btime + start_jiffies / float(hz), 2)
        except Exception:
            return None
    try:
        import ctypes
        from ctypes import wintypes
        k32 = ctypes.windll.kernel32
        PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
        h = k32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
        if not h:
            return None
        try:
            times = [wintypes.FILETIME() for _ in range(4)]
            if not k32.GetProcessTimes(h, *[ctypes.byref(t) for t in times]):
                return None
            ft = (times[0].dwHighDateTime << 32) | times[0].dwLowDateTime
            # FILETIME epoch 1601-01-01 UTC in 100ns units
            return round(ft / 1e7 - 11644473600.0, 2)
        finally:
            k32.CloseHandle(h)
    except Exception:
        return None


def process_identity(pid, lane_id=None):
    """The identity record written into process-started.json at spawn."""
    return {"lane_id": lane_id or host_os_name(),
            "host_os": host_os_name(),
            "host_boot_id": host_boot_id(),
            "pid": pid,
            "process_creation_time": process_creation_time(pid)}


def _boot_ids_match(recorded, current):
    if recorded == current:
        return True
    try:
        if (str(recorded).startswith("winboot-")
                and str(current).startswith("winboot-")):
            return abs(int(str(recorded)[8:]) - int(str(current)[8:])) <= 1
    except ValueError:
        pass
    return False


def original_process_alive(started):
    """(alive, reason) — True ONLY when the recorded process identity
    provably matches a currently live process. A recycled pid, a
    foreign-OS-lane pid, a reboot, or any missing/unreadable identity
    field is NEVER 'alive': the reconciler must not keep a run open on a
    pid number alone (release campaign crash lesson, v0.3.2.0)."""
    rec_os = started.get("host_os")
    if rec_os is not None and rec_os != host_os_name():
        # A KNOWN different lane OS: the pid namespace differs, so local
        # liveness checks are meaningless. (A legacy record with no
        # host_os falls through to the identity checks below instead.)
        return False, "foreign-lane: recorded host_os %r, reconciling on %r" \
            % (rec_os, host_os_name())
    pid = started.get("pid")
    if not _pid_alive(pid):
        return False, "process dead"
    rec_ct = started.get("process_creation_time")
    if not isinstance(rec_ct, (int, float)):
        return False, "no recorded process_creation_time — identity " \
                      "unverifiable, not treated as the original process"
    cur_ct = process_creation_time(pid)
    if cur_ct is None:
        return False, "live pid identity unreadable — not treated as the " \
                      "original process"
    # 1.0s absorbs representation jitter (POSIX btime can slew under NTP)
    # while keeping the recycled-pid coincidence window minimal — both
    # reads come from the same kernel source for the same live pid.
    if abs(cur_ct - rec_ct) > 1.0:
        return False, "pid recycled: creation time %r != recorded %r" \
            % (cur_ct, rec_ct)
    rec_boot = started.get("host_boot_id")
    cur_boot = host_boot_id()
    if rec_boot and cur_boot and not _boot_ids_match(rec_boot, cur_boot):
        return False, "boot id mismatch: %r != recorded %r" \
            % (cur_boot, rec_boot)
    return True, "alive"


def _write_terminal(run_root, record):
    """Create-once terminal write; a conflict is surfaced, never silent."""
    path = os.path.join(run_root, "terminal.json")
    try:
        with open(path, "x", encoding="utf-8") as fh:
            json.dump(record, fh, indent=1, sort_keys=True)
        return "written"
    except FileExistsError:
        return "terminal-already-present"


def reconcile_custody(custody_root):
    """Adjudicate every intent-without-terminal under custody_root.

    Returns a list of {run_id, disposition} dicts. Never raises for an
    individual run dir; unreadable state is itself a truthful ERROR.
    """
    results = []
    if not os.path.isdir(custody_root):
        return results
    for name in sorted(os.listdir(custody_root)):
        run_root = os.path.join(custody_root, name)
        if not os.path.isdir(run_root):
            continue
        try:
            results.extend(_reconcile_one(name, run_root))
        except Exception as exc:  # per-dir contract: never raises
            results.append({"run_id": name, "disposition": "reconcile-error",
                            "write": "none", "detail": repr(exc)[:200]})
    return results


def _reconcile_one(name, run_root):
    results = []
    for _ in (0,):  # single pass; body uses `continue` as early-exit
        intent_p = os.path.join(run_root, "run-intent.json")
        term_p = os.path.join(run_root, "terminal.json")
        if name.endswith(".claiming"):
            # Orphan claim staging dir: the adapter crashed between creating
            # the staging dir and atomically renaming it to the final run
            # root. It never became a claimed run — terminally classify it
            # (never silently ignore), keyed by the intended run id.
            if os.path.isfile(term_p):
                continue
            intended = name[:-len(".claiming")]
            rec = {"schema": "implementaudit-run-terminal-v1",
                   "run_id": intended, "reconciled": True,
                   "resolved_model": None, "policy_resolved": {},
                   "kind": "error", "spawned": False,
                   "detail": "orphan-claim-swept: staging dir never renamed "
                             "to a claimed run root (intent %s)"
                             % ("present" if os.path.isfile(intent_p)
                                else "absent")}
            results.append({"run_id": intended,
                            "disposition": "orphan-claim-swept",
                            "write": _write_terminal(run_root, rec)})
            continue
        if not os.path.isfile(intent_p) or os.path.isfile(term_p):
            continue
        base = {"schema": "implementaudit-run-terminal-v1", "run_id": name,
                "reconciled": True, "resolved_model": None,
                "policy_resolved": {}}
        started_p = os.path.join(run_root, "process-started.json")
        if not os.path.isfile(started_p):
            base.update({"kind": "error", "spawned": False,
                         "detail": "launch-not-confirmed: intent exists but "
                                   "no process-started record"})
            results.append({"run_id": name,
                            "disposition": "launch-not-confirmed",
                            "write": _write_terminal(run_root, base)})
            continue
        try:
            started = json.load(open(started_p, encoding="utf-8"))
        except (OSError, ValueError):
            # ValueError covers BOTH malformed JSON (JSONDecodeError) and
            # non-UTF-8 garbage (UnicodeDecodeError): a record tampered
            # into undecodable bytes must reach the truthful-terminal path
            # below, never loop as reconcile-error without a terminal.
            started = {}
        if not isinstance(started, dict):
            # a rewritten/garbage record must yield a truthful terminal
            # disposition, never crash the reconciler (contract: never
            # raises for an individual run dir)
            started = {}
        alive, why = original_process_alive(started)
        if alive:
            results.append({"run_id": name, "disposition": "running",
                            "write": "none"})
            continue
        if why.startswith("foreign-lane"):
            # A pid from another OS lane cannot be adjudicated here at all
            # (different pid namespace): classify truthfully rather than
            # guessing liveness from an unrelated same-numbered process.
            base.update({"kind": "error", "spawned": True,
                         "detail": "terminal-state-unverified: " + why})
            results.append({"run_id": name,
                            "disposition": "terminal-state-unverified",
                            "write": _write_terminal(run_root, base)})
            continue
        # dead process: is there host terminal evidence (a sealed bundle)?
        bundle_manifest = os.path.join(run_root, "bundle", "manifest.json")
        if os.path.isfile(bundle_manifest):
            base.update({"kind": "error", "spawned": True,
                         "detail": "forensic-import-candidate: process died "
                                   "after sealing a bundle; adjudicate the "
                                   "bundle separately — NEVER formal "
                                   "baseline evidence without a bound "
                                   "pre-spawn intent review"})
            results.append({"run_id": name,
                            "disposition": "forensic-import-candidate",
                            "write": _write_terminal(run_root, base)})
            continue
        base.update({"kind": "error", "spawned": True,
                     "detail": "terminal-state-unverified: bound process is "
                               "not verifiably the original (%s) and no "
                               "terminal or bundle evidence exists" % why})
        results.append({"run_id": name,
                        "disposition": "terminal-state-unverified",
                        "write": _write_terminal(run_root, base)})
    return results


def main(argv):
    if len(argv) != 2:
        print("usage: reconcile.py <custody_root>", file=sys.stderr)
        return 2
    for r in reconcile_custody(argv[1]):
        print(json.dumps(r, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
