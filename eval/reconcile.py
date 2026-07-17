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
        intent_p = os.path.join(run_root, "run-intent.json")
        term_p = os.path.join(run_root, "terminal.json")
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
        except (OSError, json.JSONDecodeError):
            started = {}
        pid = started.get("pid")
        if _pid_alive(pid):
            results.append({"run_id": name, "disposition": "running",
                            "write": "none"})
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
                               "dead and no terminal or bundle evidence "
                               "exists"})
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
