#!/usr/bin/env python3
"""Real host adapters for #9 phase 2b — DISABLED BY DEFAULT.

Two host-model CONFIGURATIONS (model and host effects are confounded and
always reported as configurations, never as pure model comparisons):

  Configuration L — Codex CLI / gpt-5.6-luna / reasoning effort max
      ("Luna Max" is that TUPLE — model + effort — never a concatenated
      slug; `luna-max` and `gpt-5.6-luna-max` are REJECTED at construction).
      Requires CLI >= 0.144.0 (fail closed); auth mode recorded, API/metered
      auth blocked without an owner cap. Payload presentation: the adapter
      ITSELF stages immutable v0.3.1.0 into the fresh temporary CODEX_HOME
      at skills/implementaudit/ (Codex's native skill location), hashes the
      STAGED copy, and fails INVALID on absence or mismatch. Native Windows
      workspace-write is requested; the RESOLVED sandbox is read from the
      host-owned session `turn_context` and any downgrade is INVALID.

  Configuration O — Claude Code CLI / Opus High (`ClaudeAdapter`)
      `claude -p --model opus --effort high --output-format stream-json`.
      Scored events are the HOST-ASSIGNED per-message assistant events from
      the stream (intermediate turns retained); the project transcript,
      selected by the exact returned session id, corroborates them. Payload
      presentation DIFFERS from Codex and is labeled: staged into the
      fixture repository at `.claude/skills/implementaudit/` with a
      CLAUDE.md pointer. Cross-configuration comparisons must carry this
      packaging difference as a caveat.

Shared guarantees (mock-tested in eval/test_hosts.py; NO live mission in CI):
  - `require_owner_approval()` gates every spawn; unconditional refusal in
    CI; no hidden retry (exactly one spawn per mission);
  - run lifecycle is CRASH-RECONCILABLE: create-once `run-intent.json`
    before spawn, create-once `process-started.json` immediately after
    spawn, one canonical create-once `terminal.json` in a finally path, and
    `reconcile.reconcile_custody()` adjudicates stale intents before any
    new run id is claimed (see eval/reconcile.py);
  - host-session identity is BOUND (cwd + not-before time window; exactly
    one match) — zero or multiple matching sessions is INVALID; there is NO
    newest-file fallback anywhere;
  - requested vs resolved model, reasoning effort, and execution policy are
    recorded separately; substitution or missing provenance FAILS CLOSED;
    `models_observed[]` records every model the host reported and its role;
    adapter-attested capability notes are labeled as such, never presented
    as host-resolved fact;
  - clean constructed environment (no os.environ passthrough beyond an
    allowlist); credentials live only in the temp home's auth files; bundles
    are scanned with word-bounded credential patterns (no prose false
    positives) and a detected leak QUARANTINES the bundle create-once and
    terminalizes INVALID without ever printing the matched value;
  - canonical payload checkout is hashed before/after the mission; any
    write to it aborts the run; fixture repos are isolated with
    before/after snapshots; per-fixture `required_capabilities` are gated
    before spawn; host nonzero exit or timeout => ERROR; malformed
    structured output => INVALID; both preserved, never silently retried.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "lib"))
sys.path.insert(0, HERE)
import adapters as framework  # noqa: E402
import bundle as bundlelib  # noqa: E402
import hostread  # noqa: E402
import reconcile as reconcilelib  # noqa: E402
import reposnapshot  # noqa: E402

ENV_ALLOWLIST = ("SYSTEMROOT", "WINDIR", "PATH", "TEMP", "TMP", "HOME",
                 "USERPROFILE", "COMSPEC", "PATHEXT", "LANG", "LC_ALL",
                 "APPDATA", "LOCALAPPDATA", "PROGRAMDATA")


def _utc_now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


_SECRET_REDACT = None


def _redact_secrets(text):
    """Replace credential-shaped substrings with <redacted> so a host error
    message can never carry a secret into result.detail / terminal.json."""
    global _SECRET_REDACT
    import re as _re
    if _SECRET_REDACT is None:
        _SECRET_REDACT = [
            _re.compile(r"sk-ant-[A-Za-z0-9_-]{8,}"),
            _re.compile(r"sk-proj-[A-Za-z0-9_-]{8,}"),
            _re.compile(r"\bsk-[A-Za-z0-9]{24,}"),
            _re.compile(r"\bghp_[A-Za-z0-9]{20,}"),
            _re.compile(r"\bgho_[A-Za-z0-9]{20,}"),
            _re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}"),
            _re.compile(r"\bxox[abprs]-[A-Za-z0-9-]{10,}"),
            _re.compile(r"Bearer\s+[A-Za-z0-9._-]{20,}"),
            _re.compile(r"\beyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{10,}"
                        r"\.[A-Za-z0-9_-]{10,}"),
        ]
    for pat in _SECRET_REDACT:
        text = pat.sub("<redacted>", text)
    return text


def _parse_ts(s):
    """RFC3339 -> aware datetime; None when unparsable. Timestamp windows
    must NEVER be compared as strings: '...03.635Z' sorts lexicographically
    BEFORE '...03Z', which silently excluded a same-second session record
    (smoke-L-b0-r1 INVALID, v0.3.2.0 R1)."""
    if not isinstance(s, str) or not s:
        return None
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except ValueError:
        return None



def _read_custody_file(path, cap=4 * 1024 * 1024):
    """Bounded, special-file-safe read for exit-time custody verification:
    only a REGULAR, non-symlink file up to `cap` bytes is readable — a
    mission that swapped a custody record for a FIFO/symlink/device must
    yield a hash mismatch, never a blocked or unbounded read."""
    try:
        st = os.lstat(path)
    except OSError:
        return None
    import stat as _stat
    if not _stat.S_ISREG(st.st_mode) or st.st_size > cap:
        return None
    try:
        with open(path, "rb") as fh:
            return fh.read(cap + 1)
    except OSError:
        return None


class HostRunResult:
    def __init__(self, kind, detail, raw_events=None, resolved_model=None):
        self.kind = kind          # "ok" | "error" | "invalid"
        self.detail = detail
        self.raw_events = raw_events or []
        self.resolved_model = resolved_model


def _clean_env(extra=None):
    env = {k: os.environ[k] for k in ENV_ALLOWLIST if k in os.environ}
    env.update(extra or {})
    return env


class _Outcome:
    def __init__(self, stdout, stderr, returncode):
        self.stdout = stdout
        self.stderr = stderr
        self.returncode = returncode


class _WinJob:
    """Windows Job Object owning the spawned host's whole process tree.
    kill-on-close means an adapter crash (handle close) also reaps the
    tree; terminate() reaps it atomically on timeout and verify_empty()
    proves no descendant survived before the run terminalizes."""

    def __init__(self):
        import ctypes
        from ctypes import wintypes
        self._ct = ctypes
        self.k32 = ctypes.windll.kernel32

        class _BASIC(ctypes.Structure):
            _fields_ = [("PerProcessUserTimeLimit", ctypes.c_longlong),
                        ("PerJobUserTimeLimit", ctypes.c_longlong),
                        ("LimitFlags", wintypes.DWORD),
                        ("MinimumWorkingSetSize", ctypes.c_size_t),
                        ("MaximumWorkingSetSize", ctypes.c_size_t),
                        ("ActiveProcessLimit", wintypes.DWORD),
                        ("Affinity", ctypes.c_size_t),
                        ("PriorityClass", wintypes.DWORD),
                        ("SchedulingClass", wintypes.DWORD)]

        class _IOC(ctypes.Structure):
            _fields_ = [(n, ctypes.c_ulonglong) for n in (
                "ReadOperationCount", "WriteOperationCount",
                "OtherOperationCount", "ReadTransferCount",
                "WriteTransferCount", "OtherTransferCount")]

        class _EXT(ctypes.Structure):
            _fields_ = [("BasicLimitInformation", _BASIC),
                        ("IoInfo", _IOC),
                        ("ProcessMemoryLimit", ctypes.c_size_t),
                        ("JobMemoryLimit", ctypes.c_size_t),
                        ("PeakProcessMemoryUsed", ctypes.c_size_t),
                        ("PeakJobMemoryUsed", ctypes.c_size_t)]

        class _ACCT(ctypes.Structure):
            _fields_ = [("TotalUserTime", ctypes.c_longlong),
                        ("TotalKernelTime", ctypes.c_longlong),
                        ("ThisPeriodTotalUserTime", ctypes.c_longlong),
                        ("ThisPeriodTotalKernelTime", ctypes.c_longlong),
                        ("TotalPageFaultCount", wintypes.DWORD),
                        ("TotalProcesses", wintypes.DWORD),
                        ("ActiveProcesses", wintypes.DWORD),
                        ("TotalTerminatedProcesses", wintypes.DWORD)]

        self._ACCT = _ACCT
        self.handle = self.k32.CreateJobObjectW(None, None)
        if not self.handle:
            raise OSError("CreateJobObjectW failed")
        info = _EXT()
        info.BasicLimitInformation.LimitFlags = 0x2000  # KILL_ON_JOB_CLOSE
        JobObjectExtendedLimitInformation = 9
        if not self.k32.SetInformationJobObject(
                self.handle, JobObjectExtendedLimitInformation,
                ctypes.byref(info), ctypes.sizeof(info)):
            self.close()
            raise OSError("SetInformationJobObject failed")

    def assign(self, proc):
        if not self.k32.AssignProcessToJobObject(
                self.handle, int(proc._handle)):
            raise OSError("AssignProcessToJobObject failed")

    def terminate(self):
        self.k32.TerminateJobObject(self.handle, 1)

    def verify_empty(self, timeout_s=10.0):
        """True when zero processes remain in the job."""
        import time as _t
        JobObjectBasicAccountingInformation = 1
        deadline = _t.monotonic() + timeout_s
        while _t.monotonic() < deadline:
            acct = self._ACCT()
            ok = self.k32.QueryInformationJobObject(
                self.handle, JobObjectBasicAccountingInformation,
                self._ct.byref(acct), self._ct.sizeof(acct), None)
            if ok and acct.ActiveProcesses == 0:
                return True
            _t.sleep(0.1)
        return False

    def close(self):
        try:
            self.k32.CloseHandle(self.handle)
        except Exception:
            pass


def _kill_tree(proc, job=None):
    """Terminate the OWNED process tree, not only the direct child, and
    return a short verification note ('tree-verified-dead' when no
    descendant provably survives). Windows: TerminateJobObject on the job
    the child was assigned to at spawn (taskkill /T fallback). POSIX: the
    child was spawned in its own session/process group; SIGTERM then
    SIGKILL the group and verify with killpg(0)."""
    import time as _t
    if os.name == "nt":
        if job is not None:
            job.terminate()
            note = ("tree-verified-dead" if job.verify_empty()
                    else "job-terminate-descendants-unverified")
        else:
            try:
                subprocess.run(["taskkill", "/PID", str(proc.pid),
                                "/T", "/F"], capture_output=True, timeout=30)
                note = "taskkill-tree-unverified"
            except Exception as exc:
                note = f"taskkill-failed:{exc!r}"
        try:
            proc.kill()
        except OSError:
            pass
        return note
    import signal
    try:
        pgid = os.getpgid(proc.pid)
    except OSError:
        pgid = None
    if pgid is not None and pgid != os.getpgid(0):
        try:
            os.killpg(pgid, signal.SIGTERM)
        except OSError:
            pass
        deadline = _t.monotonic() + 5.0
        while _t.monotonic() < deadline and proc.poll() is None:
            _t.sleep(0.1)
        try:
            os.killpg(pgid, signal.SIGKILL)
        except OSError:
            pass
        try:
            os.killpg(pgid, 0)
            note = "killpg-descendants-unverified"
        except OSError:
            # HONEST LABEL: killpg(0) proves the process GROUP is empty; a
            # descendant that called setsid() left the group and is not
            # covered (platform-limited; cgroup containment is v0.3.3.0).
            note = "process-group-verified-dead"
    else:
        note = "no-own-process-group"
    try:
        proc.kill()
    except OSError:
        pass
    return note


def _spawn_once(argv, env, cwd, timeout_s, stdin_text=None, on_started=None):
    """Exactly one spawn — no hidden retry lives anywhere in this module.
    `on_started` runs immediately after the process exists (create-once
    process-started custody); if it fails the child is killed and the run
    terminalizes ERROR. The child owns a Job Object (Windows) or its own
    session (POSIX) so every termination path reaps the WHOLE tree."""
    popen_kw = {}
    if os.name != "nt":
        popen_kw["start_new_session"] = True
    try:
        proc = subprocess.Popen(argv, env=env, cwd=cwd,
                                stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                text=True, encoding="utf-8",
                                errors="replace", **popen_kw)
    except OSError as exc:
        return HostRunResult("error", f"host spawn failed: {exc}")
    job = None
    if os.name == "nt":
        try:
            job = _WinJob()
            job.assign(proc)
        except OSError as exc:
            # FAIL CLOSED (independent review): a Windows mission without
            # job-object tree ownership cannot be verifiably terminated —
            # do not run it. (The sub-ms window between CreateProcess and
            # assignment is a documented residual; assignment FAILURE is
            # not tolerated.)
            if job is not None:
                job.close()
            note = _kill_tree(proc, None)
            proc.communicate()
            return HostRunResult(
                "error", f"job-object ownership unavailable ({exc}); "
                         f"refusing to run without verifiable tree "
                         f"termination (kill: {note})")
    try:
        if on_started is not None:
            try:
                on_started(proc)
            except Exception as exc:
                note = _kill_tree(proc, job)
                proc.communicate()
                return HostRunResult(
                    "error", f"process-started custody write failed: "
                             f"{exc!r} (kill: {note})")
        try:
            out, err = proc.communicate(input=stdin_text, timeout=timeout_s)
        except subprocess.TimeoutExpired:
            note = _kill_tree(proc, job)
            out, err = proc.communicate()
            r = HostRunResult(
                "error", f"host timeout after {timeout_s}s (kill: {note})")
            r.stdout, r.stderr = out or "", err or ""
            return r
    finally:
        if job is not None:
            job.close()
    if proc.returncode != 0:
        # Carry the raw streams so the caller can preserve them at the run
        # root — an ERROR run must never leave custody without the host
        # output that explains it (v0.3.2.0 R1: an empty-stderr exit-1 was
        # undiagnosable from custody alone). The detail message is
        # secret-redacted; the full raw streams are scrubbed by the caller's
        # finally-path credential scan.
        r = HostRunResult(
            "error",
            f"host exit {proc.returncode}: "
            f"{_redact_secrets(err or '')[:300]}")
        r.stdout, r.stderr = out or "", err or ""
        return r
    return _Outcome(out or "", err or "", proc.returncode)


class _BaseAdapter:
    name = "base"
    version = "3"
    timeout_s = 1800
    capabilities = frozenset()

    def __init__(self, host_argv_template, requested_model,
                 product_checkout=None, host_cwd=None, formal=True,
                 lane_id=None, product_expected_rev="v0.3.1.0",
                 host_read_attestation=None):
        self.host_argv_template = list(host_argv_template)
        self.requested_model = requested_model
        self.product_checkout = product_checkout
        # The rev the product checkout MUST be at to attest (tag or full
        # SHA). Defaults to the immutable baseline tag; candidate-product
        # campaigns (post-change B3, cluster/final comparisons) pass the
        # campaign intent's candidate commit so the gate cross-checks the
        # checkout against the INTENDED identity — never self-attestation.
        self.product_expected_rev = product_expected_rev
        self.host_cwd = host_cwd
        # A FORMAL run produces evidence (smoke/baseline/comparison) and
        # must carry an attested product checkout — zero identities are
        # never a valid fallback for scored evidence. Only explicitly
        # declared mock/test adapters may run without one.
        self.formal = formal
        self.lane_id = lane_id
        self.models_observed = []
        self._events_source = None
        self._staged_payload_hash = None
        self._not_before = None
        self._tool_trace = []
        self._formal_host_read = None
        self._formal_host_read_results = {}
        self._host_read_attestation = self._validate_host_read_attestation(
            host_read_attestation)

    # --- provenance -------------------------------------------------------
    def resolve_model(self, host_output_text):
        raise NotImplementedError

    def check_provenance(self, host_output_text):
        resolved = self.resolve_model(host_output_text)
        if not resolved:
            raise framework.AdapterError(
                "missing model provenance: host output does not prove which "
                "model ran — fail closed")
        if resolved != self.requested_model_canonical():
            raise framework.AdapterError(
                f"model substitution: requested "
                f"{self.requested_model_canonical()!r} but host resolved "
                f"{resolved!r} — fail closed (recorded)")
        return resolved

    def requested_model_canonical(self):
        return self.requested_model

    def preflight(self):
        """Configuration-specific pre-spawn gates (version/auth)."""
        return None

    def post_checks(self, host_output_text):
        """Configuration-specific post-spawn provenance checks."""
        return None

    # --- mission ----------------------------------------------------------
    def stage_payload(self, repo):
        """Present the product payload to the host (configuration-specific;
        overridden by subclasses). Returns the STAGED-copy hash."""
        return None

    def reconcile_events(self, events, repo, outcome):
        """Cross-check parsed events against host-owned records
        (configuration-specific). Returns the events to score."""
        return events

    def run_mission(self, fixture_id, custody_root, run_id, work_root,
                    _test_gate=None, call_ordinal=1):
        """CRASH-RECONCILABLE PRE-SPAWN CUSTODY: stale intents are
        reconciled BEFORE a new run id is claimed; the create-once run root
        and run-intent.json exist BEFORE any process launches; a create-once
        process-started.json exists immediately AFTER launch; and one
        canonical terminal record is written in a finally path for EVERY
        launch. `_test_gate` is code-level test plumbing only."""
        self._reset_formal_host_read_state()
        (framework.require_owner_approval if _test_gate is None
         else _test_gate)()
        self.preflight()
        reconcilelib.reconcile_custody(custody_root)
        # ATOMIC CLAIM: the intent is written inside a create-once staging
        # dir which is then renamed to the final run root, so a hard crash
        # can never leave an intent-less orphan run root — a crash before
        # the rename leaves only a `<run_id>.claiming` staging dir, which
        # the reconciler sweeps and terminally classifies.
        claiming = framework.custody.resolve_and_create_output_dir(
            custody_root, run_id + ".claiming")
        run_root = os.path.join(os.path.dirname(claiming), run_id)
        framework.custody.resolve_output_dir(custody_root, run_id)
        if os.path.lexists(run_root):
            os.rmdir(claiming)
            raise framework.custody.CustodyError(
                f"destination already exists: {run_root!r}")
        started_ts = _utc_now()
        self._not_before = started_ts
        fixture_path = os.path.join(HERE, "fixtures", fixture_id,
                                    "fixture.json")
        fixture_bytes = open(fixture_path, "rb").read()
        fx = json.loads(fixture_bytes.decode("utf-8"))
        intent = {
            "schema": "implementaudit-run-intent-v1", "run_id": run_id,
            "fixture_id": fixture_id, "call_ordinal": call_ordinal,
            "fixture_sha256": bundlelib._sha256_bytes(fixture_bytes),
            "product_checkout": self.product_checkout,
            "adapter_name": self.name,
            "adapter_sha256": bundlelib.sha256_file(
                os.path.abspath(__file__)),
            "harness_commit": _harness_commit(),
            "model_requested": self.requested_model_canonical(),
            "reasoning_effort_requested": getattr(
                self, "reasoning_effort_requested", None),
            "policy_requested": self.requested_policy(),
            "required_capabilities": fx.get("required_capabilities", []),
            "temp_home": getattr(self, "codex_home", None) or getattr(
                self, "config_dir", None),
            "started_at": started_ts,
        }
        intent_bytes = json.dumps(intent, indent=1,
                                  sort_keys=True).encode("utf-8")
        with open(os.path.join(claiming, "run-intent.json"), "xb") as fh:
            fh.write(intent_bytes)
        # Atomic claim. Residual TOCTOU (POSIX rename replaces an EMPTY
        # dst dir created between the lexists check and here) is accepted:
        # custody is single-orchestrator with serialized lanes and no
        # mission process is alive during the claim; the create-once
        # .claiming dir already collides duplicate claims of the same id.
        os.rename(claiming, run_root)
        if not os.path.isfile(os.path.join(run_root, "run-intent.json")):
            raise framework.custody.CustodyError(
                f"claim postcondition failed: no intent at {run_root!r}")
        # Custody-record integrity: a Config-O mission process has no OS
        # filesystem jail (canary-proven), so it could rewrite its own
        # custody records mid-run. Hash them at write time and re-verify on
        # every exit path; a mismatch downgrades the run to INVALID.
        self._custody_hashes = {
            "run-intent.json": bundlelib._sha256_bytes(intent_bytes)}
        result = HostRunResult("error", "adapter did not terminalize")
        spawned = False
        payload_before = None
        try:
            if self.formal and not self.product_checkout:
                raise framework.AdapterError(
                    "formal run without an attested product checkout — "
                    "zero identities are not a valid fallback for scored "
                    "evidence; INVALID before spawn")
            if self.formal:
                # PRE-SPAWN ATTESTATION (independent review): presence of a
                # path is not attestation. Pin the checkout's payload hash
                # (raises → INVALID on a bogus/non-payload dir) and its git
                # commit into a create-once custody record BEFORE spawn.
                try:
                    att_payload = framework.payload_hash(
                        self.product_checkout)
                except Exception as exc:
                    raise framework.AdapterError(
                        f"product checkout unattestable "
                        f"({exc!r}) — INVALID before spawn")
                if att_payload == hashlib.sha256().hexdigest():
                    raise framework.AdapterError(
                        "product checkout unattestable (empty payload "
                        "tree) — INVALID before spawn")
                try:
                    att_commit = subprocess.run(
                        ["git", "-C", self.product_checkout, "rev-parse",
                         "HEAD"], capture_output=True, text=True,
                        timeout=30).stdout.strip() or None
                except Exception:
                    att_commit = None
                att_bytes = json.dumps(
                    {"schema": "implementaudit-product-attestation-v1",
                     "run_id": run_id, "path": self.product_checkout,
                     "payload_sha256": att_payload,
                     "git_commit": att_commit, "attested_at": _utc_now()},
                    indent=1, sort_keys=True).encode("utf-8")
                with open(os.path.join(run_root,
                                       "product-attestation.json"),
                          "xb") as fh:
                    fh.write(att_bytes)
                self._custody_hashes["product-attestation.json"] = \
                    bundlelib._sha256_bytes(att_bytes)
            need = set(fx.get("required_capabilities", []))
            missing = sorted(need - set(self.capabilities))
            if missing:
                raise framework.AdapterError(
                    f"fixture {fixture_id} requires host capabilities "
                    f"{missing} that this adapter configuration does not "
                    f"provide — INVALID")
            payload_before = (framework.payload_hash(self.product_checkout)
                              if self.product_checkout else None)
            self._payload_before = payload_before
            repo = framework.seed_fixture_repo(fixture_id, work_root)
            self._current_repo = repo
            staged_hash = None
            if self.product_checkout:
                staged_hash = self.stage_payload(repo)
            if self.formal and any(
                    spec.get("kind") == "path_access_order"
                    for spec in (fx.get("host_checks") or {}).get(
                        "specs", [])):
                self._prepare_formal_host_read(
                    fx, repo, run_root, intent["fixture_sha256"],
                    self._custody_hashes["run-intent.json"],
                    fixture_bytes)
            before = reposnapshot.snapshot(repo)
            mission = fx["mission"]
            argv = [a.replace("{model}", self.requested_model)
                    for a in self.host_argv_template]

            def _on_started(proc):
                rec = {"schema": "implementaudit-process-started-v2",
                       "run_id": run_id,
                       "cwd": self.host_cwd or repo,
                       "started_at": _utc_now(),
                       "argv_sha256": bundlelib._sha256_bytes(
                           "\x00".join(argv).encode("utf-8")),
                       "requested_model": self.requested_model_canonical(),
                       "temp_home": intent["temp_home"]}
                # Full process identity (lane, OS, boot, pid, creation
                # time): the reconciler refuses to treat a recycled or
                # foreign-lane pid as the original process, so every field
                # it compares must be captured at spawn.
                rec.update(reconcilelib.process_identity(
                    proc.pid, lane_id=getattr(self, "lane_id", None)))
                if self._formal_host_read is not None:
                    rec["host_read_pre_spawn_sha256"] = \
                        self._custody_hashes[
                            "host-read-pre-spawn.json"]
                rec_bytes = json.dumps(rec, indent=1,
                                       sort_keys=True).encode("utf-8")
                with open(os.path.join(run_root, "process-started.json"),
                          "xb") as fh:
                    fh.write(rec_bytes)
                self._custody_hashes["process-started.json"] = \
                    bundlelib._sha256_bytes(rec_bytes)

            spawned = True
            outcome = _spawn_once(argv, self._mission_env(repo),
                                  self.host_cwd or repo, self.timeout_s,
                                  stdin_text=mission,
                                  on_started=_on_started)
            # FORGED-CUSTODY SWEEP (independent review blocking): the
            # mission process is dead now; anything in the run root beyond
            # what THIS adapter wrote pre-spawn was planted by the mission
            # (jail-less Config-O can reach custody). A precreated
            # terminal.json or bundle/ would otherwise become authoritative
            # (terminal "x" would hit FileExistsError and the forged record
            # would survive; the scorer would read forged evidence).
            # Quarantine every unexpected entry and terminalize INVALID.
            allowed_now = {"run-intent.json", "process-started.json",
                           "product-attestation.json"}
            if self._formal_host_read is not None:
                allowed_now.update({"host-read-profile.json",
                                    "host-read-preimages.json",
                                    "host-read-fixture.raw",
                                    "host-read-replay-spec.json",
                                    "host-read-pre-spawn.json"})
            planted = sorted(set(os.listdir(run_root)) - allowed_now)
            if planted:
                qdir = os.path.join(run_root, "quarantine-planted")
                os.makedirs(qdir, exist_ok=True)
                for n in planted:
                    try:
                        os.replace(os.path.join(run_root, n),
                                   os.path.join(qdir, n))
                    except OSError:
                        pass
                # A process was launched, so the formal property layer must
                # still get a best-effort terminal seal.  The forged entries
                # have already been removed from the custody root and cannot
                # become inputs to this seal; the host layer remains INVALID.
                if self._formal_host_read is not None:
                    try:
                        self._attempt_finalize_formal_host_read(
                            fx, repo, outcome, run_root, "invalid")
                    except Exception as exc:  # preserve the custody verdict
                        self._formal_host_read_host_status = "INVALID"
                        self._formal_host_read_seal_error = type(exc).__name__
                raise framework.AdapterError(
                    f"mission planted {len(planted)} unexpected entr"
                    f"{'y' if len(planted) == 1 else 'ies'} in the run "
                    f"root ({', '.join(planted[:4])}) — quarantined; "
                    f"INVALID")
            # Preserve the raw host stdout/stderr at the RUN ROOT immediately
            # — for BOTH the nonzero-exit/timeout error path and the normal
            # path — so no INVALID/ERROR classification ever destroys the
            # diagnostic evidence (v0.3.2.0 R1 lessons).
            raw_records = [("host-stderr.raw",
                            getattr(outcome, "stderr", ""))]
            if self._formal_host_read is None:
                raw_records.insert(0, ("host-stdout.raw",
                                       getattr(outcome, "stdout", "")))
            for rel, data in raw_records:
                try:
                    with open(os.path.join(run_root, rel), "xb") as fh:
                        fh.write((data or "").encode("utf-8"))
                except FileExistsError:
                    pass
            if self._formal_host_read is not None:
                terminal_kind = (outcome.kind if isinstance(
                    outcome, HostRunResult) else
                    "ok" if getattr(outcome, "returncode", 0) == 0 else
                    "error")
                try:
                    self._attempt_finalize_formal_host_read(
                        fx, repo, outcome, run_root, terminal_kind)
                except Exception as exc:
                    # A sealing defect must never replace the original
                    # timeout/error result from the launched host process.
                    self._formal_host_read_host_status = "INVALID"
                    self._formal_host_read_seal_error = type(exc).__name__
            if isinstance(outcome, HostRunResult):
                result = outcome
                return result
            if (self._formal_host_read is not None and
                    self._formal_host_read_host_status != "PASS"):
                result = HostRunResult(
                    "invalid", "formal host-read evidence boundary INVALID; "
                    "separate product-property measurements were sealed")
                return result
            self._tool_trace = self._extract_tool_trace(outcome.stdout)
            try:
                events = self.parse_events(outcome.stdout)
            except ValueError as exc:
                result = HostRunResult(
                    "invalid", f"malformed structured output: {exc}")
                return result
            events = self.reconcile_events(events, repo, outcome)
            raw_stream = self.collect_raw_stream(repo, outcome)
            provenance_stream = chr(10).join(
                [outcome.stderr or "", outcome.stdout or ""])
            resolved = self.check_provenance(provenance_stream)
            self.post_checks(provenance_stream)
            self.check_policy(repo)
            if payload_before is not None:
                if framework.payload_hash(
                        self.product_checkout) != payload_before:
                    result = HostRunResult(
                        "invalid", "canonical payload checkout modified "
                        "during the mission")
                    return result
            host_checks = self._run_host_checks(fx, repo)
            after = reposnapshot.snapshot(repo)
            cmp_ = reposnapshot.compare_with_repo(repo, before, after)
            ended_ts = _utc_now()
            fields = self.identity_fields(run_id, fixture_id, resolved,
                                          started_ts, ended_ts, staged_hash)
            fields["policy_requested"] = self.requested_policy()
            fields["policy_resolved"] = getattr(self, "policy_resolved", {})
            fields["models_observed"] = self.models_observed
            fields["reasoning_effort_requested"] = getattr(
                self, "reasoning_effort_requested", None)
            fields["reasoning_effort_resolved"] = getattr(
                self, "reasoning_effort_resolved", None)
            bundle_root = os.path.join(run_root, "bundle")
            ev_objs = [bundlelib.make_event(
                run_id, fixture_id, i + 1, e["role"], e["content"],
                kind=e.get("kind", "message"),
                recorded_at=e.get("ts") or "1970-01-01T00:00:00Z")
                for i, e in enumerate(events)]
            derived_meta = {
                "schema": "implementaudit-derived-view-v1",
                "transform": self.name + "-host-event-extraction-v2",
                "source": self._events_source or self.name + "-stdout",
                "source_raw_sha256": (bundlelib._sha256_bytes(raw_stream)
                                      if raw_stream else None),
                "rules": "one scored event per HOST-ASSIGNED assistant "
                         "message; prompt echoes/user/system/tool events "
                         "are never scored as assistant content; complete "
                         "raw streams preserved; no deletion",
            }
            artifacts = dict(self.mission_artifacts or {})
            artifacts["host-stdout.raw"] = (outcome.stdout or "").encode(
                "utf-8")
            artifacts["host-stderr.raw"] = (outcome.stderr or "").encode(
                "utf-8")
            if raw_stream:
                artifacts["raw-host-events.jsonl"] = raw_stream
            if self._formal_host_read is not None:
                for name in hostread._CAPTURE_FILES + (
                        "host-read-manifest.json",):
                    path = os.path.join(run_root, name)
                    if os.path.isfile(path):
                        artifacts[name] = open(path, "rb").read()
            if host_checks is not None:
                artifacts[(fx.get("host_checks") or {}).get(
                    "artifact", "host-checks.json")] = json.dumps(
                    host_checks, indent=1, sort_keys=True).encode("utf-8")
            obs = self._emit_host_observation(fx)
            if obs is not None:
                artifacts[obs[0]] = obs[1]
            artifacts["derived-transform.json"] = json.dumps(
                derived_meta, indent=1).encode()
            bundlelib.write_bundle(
                bundle_root, fields, ev_objs, fixture_bytes,
                ("MISSION:" + chr(10) + mission).encode(),
                repo_before=before, repo_after=after, repo_comparison=cmp_,
                artifacts=artifacts)
            # Credential scan covers BOTH the bundle AND the run-root-level
            # raw host output (host-stdout.raw / host-stderr.raw): those are
            # shipped custody too, so a leak in either must quarantine and
            # fail closed (independent review MAJOR). BOTH locations are
            # quarantined before raising — a leak lives in both copies, and
            # quarantining only the bundle would leave cleartext at the run
            # root.
            hits = []
            h1 = self._quarantine_if_leak(bundle_root, "quarantine-bundle")
            if h1:
                hits.append(h1)
            h2 = self._quarantine_if_leak(
                run_root, "quarantine-raw",
                only=("host-stdout.raw", "host-stderr.raw",
                      "run-intent.json", "process-started.json",
                      "product-attestation.json"))
            if h2:
                hits.append(h2)
            if hits:
                raise framework.AdapterError(
                    f"credential pattern {hits[0][0]!r} found in file "
                    f"{hits[0][1]!r} — moved to quarantine; custody "
                    f"violation ({len(hits)} location(s) scrubbed)")
            for rel, want in (getattr(self, "_custody_hashes", None)
                              or {}).items():
                data = _read_custody_file(os.path.join(run_root, rel))
                got = (bundlelib._sha256_bytes(data)
                       if data is not None else None)
                if got != want:
                    raise framework.AdapterError(
                        f"custody record {rel} modified during the "
                        f"mission — INVALID")
            result = HostRunResult("ok", bundle_root,
                                   raw_events=events,
                                   resolved_model=resolved)
            return result
        except framework.AdapterError as exc:
            result = HostRunResult("invalid", str(exc))
            return result
        except framework.custody.CustodyError as exc:
            result = HostRunResult("invalid", f"custody: {exc}")
            return result
        except Exception as exc:  # adapter crash still terminalizes
            result = HostRunResult("error",
                                   f"adapter exception: {exc!r}")
            return result
        finally:
            # Canonical-checkout integrity on EVERY exit path (independent
            # review blocking): a model that tampers with the immutable
            # payload then exits nonzero / times out must still be caught —
            # not only on the ok path. A detected tamper downgrades the
            # terminal record to INVALID.
            pb = getattr(self, "_payload_before", None)
            if pb is not None and self.product_checkout and spawned:
                try:
                    if framework.payload_hash(self.product_checkout) != pb:
                        result = HostRunResult(
                            "invalid", "canonical payload checkout modified "
                            "during the mission (detected on exit)")
                except OSError:
                    pass
            # Custody-record integrity on EVERY exit path (Config-O canary
            # finding, v0.3.2.0): a jail-less mission process that rewrote
            # its own run-intent.json / process-started.json must be caught
            # before the run terminalizes.
            for rel, want in (getattr(self, "_custody_hashes", None)
                              or {}).items():
                data = _read_custody_file(os.path.join(run_root, rel))
                got = (bundlelib._sha256_bytes(data)
                       if data is not None else None)
                if got != want:
                    result = HostRunResult(
                        "invalid", f"custody record {rel} modified during "
                                   f"the mission (detected on exit)")
                    break
            # Credential nonretention on EVERY exit path (independent review
            # blocking): the run-root raw host output is scrubbed and the
            # terminal detail is redacted regardless of kind — a host that
            # printed a secret then exited nonzero/timed out must not leave
            # cleartext in host-stderr.raw or in terminal.json's detail.
            try:
                self._quarantine_if_leak(
                    run_root, "quarantine-raw",
                    only=("host-stdout.raw", "host-stderr.raw",
                      "run-intent.json", "process-started.json",
                      "product-attestation.json"))
            except Exception:
                pass
            term = {"schema": "implementaudit-run-terminal-v1",
                    "run_id": run_id, "spawned": spawned,
                    "kind": result.kind,
                    "detail": _redact_secrets(str(result.detail))[:500],
                    "resolved_model": result.resolved_model,
                    "reconciled": False,
                    "started_at": started_ts, "ended_at": _utc_now(),
                    "policy_resolved": getattr(self, "policy_resolved", {})}
            path = os.path.join(run_root, "terminal.json")
            try:
                with open(path, "x", encoding="utf-8") as fh:
                    json.dump(term, fh, indent=1, sort_keys=True)
            except FileExistsError:
                # ONE canonical terminal record per run: a second writer is
                # a custody anomaly, surfaced loudly — never a silent
                # terminal-2 fallback.
                with open(os.path.join(
                        run_root, "terminal-conflict.json"), "x",
                        encoding="utf-8") as fh:
                    json.dump({"anomaly": "terminal-already-present",
                               "attempted": term}, fh, indent=1,
                              sort_keys=True)

    def requested_policy(self):
        return {"sandbox": None, "approval": None, "tools": None,
                "network": "host-default", "writable_roots": ["<fixture>"]}

    def check_policy(self, repo):
        """Resolved-vs-requested execution policy; mismatch = INVALID."""
        return None

    def collect_raw_stream(self, repo, outcome):
        """Complete host-owned raw session/event stream (bytes) or None."""
        return None

    mission_artifacts = None

    def _mission_env(self, repo):
        return _clean_env()

    @staticmethod
    def _path_order_specs(fx):
        return [spec for spec in (fx.get("host_checks") or {}).get(
            "specs", []) if spec.get("kind") == "path_access_order"]

    def _reset_formal_host_read_state(self):
        self._formal_host_read = None
        self._formal_host_read_results = {}
        self._formal_host_read_host_status = None
        self._formal_host_read_seal_error = None

    def _prepare_formal_host_read(self, fx, repo, run_root,
                                  fixture_sha256, run_intent_sha256,
                                  fixture_bytes):
        """Mint immutable profile/preimages before the host process starts."""
        specs = self._path_order_specs(fx)
        targets = []
        for spec in specs:
            for target in spec.get("reads", []):
                if target not in targets:
                    targets.append(target)
        if not targets:
            raise framework.AdapterError(
                "formal path-order check has no read targets — INVALID")
        try:
            preimages = hostread.capture_preimages(repo, targets)
            if self.name == "codex-cli":
                env = self._mission_env(repo)
                shell = shutil.which("bash", path=env.get("PATH"))
                if not shell:
                    raise ValueError("no internally resolved POSIX bash")
                profile = hostread.mint_codex_profile(
                    repo, shell, env=env, writable_roots=(repo,))
                profile_runtime = {"shell": shell, "env": env}
            elif self.name == "claude-cli":
                requested = self.tools.split()
                profile = hostread.mint_claude_profile(repo, requested)
                profile_runtime = {"requested_tools": requested}
            else:
                raise ValueError(f"unsupported formal host {self.name!r}")
            replay_checks = [
                {"key": spec["key"], "reads": list(spec.get("reads") or []),
                 "write": spec.get("write")}
                for spec in specs]
            replay_spec = hostread.make_replay_spec(
                "codex" if self.name == "codex-cli" else "claude",
                replay_checks,
                requested_tools=(profile_runtime.get("requested_tools") or
                                 []),
                fixture_sha256=fixture_sha256,
                run_intent_sha256=run_intent_sha256)
            hostread.begin_capture(run_root, profile, preimages,
                                   replay_spec=replay_spec,
                                   fixture_bytes=fixture_bytes, formal=True)
        except (OSError, ValueError, FileExistsError) as exc:
            raise framework.AdapterError(
                f"formal host-read pre-spawn custody failed: {exc} — "
                "INVALID")
        self._formal_host_read = {
            "profile": profile, "preimages": preimages,
            "runtime": profile_runtime, "replay_spec": replay_spec,
            "run_root": run_root}
        for name in ("host-read-profile.json",
                     "host-read-preimages.json",
                     "host-read-fixture.raw",
                     "host-read-replay-spec.json",
                     "host-read-pre-spawn.json"):
            data = _read_custody_file(os.path.join(run_root, name))
            self._custody_hashes[name] = bundlelib._sha256_bytes(data)

    def _collect_formal_session_stream(self, repo, outcome, binding):
        """Collect the bound native stream without depending on scoring parse."""
        if self.name == "codex-cli":
            path, context = self._select_session(repo)
            if (not path or context.get("session_id") !=
                    (binding or {}).get("thread_id")):
                return None
            return open(path, "rb").read()
        session_id = (binding or {}).get("session_id")
        if not session_id or not self.config_dir:
            return None
        import glob as _glob
        matches = _glob.glob(os.path.join(
            self.config_dir, "projects", "*", session_id + ".jsonl"))
        return open(matches[0], "rb").read() if len(matches) == 1 else None

    def _attempt_finalize_formal_host_read(self, fx, repo, outcome, run_root,
                                           host_terminal_kind):
        """Seal reconstructible facts on every launched terminal path."""
        context = self._formal_host_read
        profile = context["profile"]
        preimages = context["preimages"]
        raw_stdout = getattr(outcome, "stdout", "") or ""
        if self.name == "codex-cli":
            binding = hostread.derive_codex_binding(raw_stdout)
            normalized = hostread.normalize_codex(
                raw_stdout, profile=profile, binding=binding or {},
                formal=True)
            runtime = context["runtime"]
            try:
                post = hostread.post_probe(profile, runtime["shell"],
                                           env=runtime["env"])
            except Exception as exc:
                post = {"probe_error": type(exc).__name__}
        else:
            binding = hostread.derive_claude_binding(raw_stdout)
            requested = context["runtime"]["requested_tools"]
            normalized = hostread.normalize_claude(
                raw_stdout, requested_tools=requested,
                binding=binding or {},
                profile=profile, formal=True)
            post = {"native_tools": profile["native_tools"]}
        post_status = hostread.validate_profile(
            profile, post_probe=post, formal=True)["host_status"]
        try:
            raw_session = self._collect_formal_session_stream(
                repo, outcome, binding)
        except Exception:
            raw_session = None
        if self.name == "codex-cli" and binding is not None:
            binding = hostread.augment_codex_binding(
                binding, raw_session or b"")
        try:
            process_started = json.load(open(os.path.join(
                run_root, "process-started.json"), encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            process_started = {}
        session_status = hostread.corroborate_session(
            raw_stdout, raw_session or b"",
            context["replay_spec"]["host"], binding or {}, normalized,
            profile=profile, process_started=process_started)
        if binding is None:
            hostread.add_host_finding(normalized,
                                      "lineage-binding-invalid")
        if post_status != "PASS":
            hostread.add_host_finding(normalized,
                                      "profile-post-probe-invalid")
        if session_status != "VALID":
            hostread.add_host_finding(normalized,
                                      "native-session-unbound")
        if host_terminal_kind == "error":
            hostread.add_host_finding(normalized, "host-terminal-error",
                                      host_status="ERROR")
        elif host_terminal_kind == "invalid":
            hostread.add_host_finding(normalized, "host-terminal-invalid")
        matrix = hostread.build_matrix(
            normalized, context["replay_spec"], preimages, profile,
            profile_post_status=post_status, formal=True)
        adjudications = matrix["specs"]
        try:
            hostread.finish_capture(
                run_root, raw_stdout=raw_stdout.encode("utf-8"),
                raw_session=raw_session or b"", trace=normalized,
                matrix=matrix, post_probe=post, binding=binding or {},
                host_terminal_kind=host_terminal_kind,
                session_status=session_status, formal=True,
                minted_profile=profile)
        except (OSError, ValueError, FileExistsError) as exc:
            self._formal_host_read_host_status = "INVALID"
            self._formal_host_read_seal_error = type(exc).__name__
            return False
        replay = hostread.replay_capture(run_root, formal=True)
        self._formal_host_read_results = adjudications
        for name in hostread._CAPTURE_FILES + ("host-read-manifest.json",):
            data = _read_custody_file(os.path.join(run_root, name))
            self._custody_hashes[name] = bundlelib._sha256_bytes(data)
        self._formal_host_read_host_status = (
            "PASS" if replay.get("status") == "PASS" and
            normalized.get("host_status") == "PASS" and
            post_status == "PASS" and session_status == "VALID" and
            binding is not None else "INVALID")
        return replay.get("status") == "PASS"

    # --- deterministic host checks (fixture-declared) ----------------------
    @staticmethod
    def _validate_host_read_attestation(attestation):
        """Validate optional host-owned shell/executable resolution facts."""
        if attestation is None:
            return None
        if not isinstance(attestation, dict):
            raise framework.AdapterError(
                "host_read_attestation must be an object")
        attestation_id = attestation.get("id")
        dialect = attestation.get("shell_dialect")
        executables = attestation.get("executables")
        if (not isinstance(attestation_id, str) or not attestation_id or
                dialect not in ("posix", "powershell", "cmd") or
                not isinstance(executables, dict) or not executables or
                any(not isinstance(name, str) or not name or
                    not isinstance(identity, str) or not identity
                    for name, identity in executables.items())):
            raise framework.AdapterError(
                "invalid host_read_attestation identity/dialect/executables")
        return {
            "id": attestation_id, "shell_dialect": dialect,
            "executables": dict(executables)}

    def _host_read_profile(self, repo=None):
        """Frozen evidence profile for the deliberately small shell subset."""
        host_kind = "claude" if self.name == "claude-cli" else "codex"
        attestation = self._host_read_attestation or {}
        return {
            "schema": "implementaudit-host-read-profile-v1",
            "host": host_kind,
            "repo_root": os.path.abspath(repo) if repo else None,
            "filesystem_identity": "exact-case-root-bound-no-symlink-alias",
            "attestation_id": attestation.get("id"),
            "shell_dialect": attestation.get("shell_dialect"),
            "executables": dict(attestation.get("executables") or {}),
        }

    def _bind_command_profile(self, record, host_owned_wrapper=False):
        """Attach only adapter-owned attestation facts to a command record."""
        bound = dict(record)
        profile = self._host_read_profile()
        if profile["attestation_id"]:
            bound["host_read_attestation_id"] = profile["attestation_id"]
            bound["shell_dialect"] = profile["shell_dialect"]
        bound["wrapper_host_owned"] = bool(host_owned_wrapper)
        return bound

    @staticmethod
    def _strict_json(line):
        """Decode one JSON object while rejecting duplicate object keys."""
        def unique_object(pairs):
            result = {}
            for key, value in pairs:
                if key in result:
                    raise ValueError(f"duplicate JSON key {key!r}")
                result[key] = value
            return result

        value = json.loads(line, object_pairs_hook=unique_object)
        if not isinstance(value, dict):
            raise ValueError("host event is not a JSON object")
        return value

    @staticmethod
    def _invalid_trace(records, ordinal, reason):
        records.append({
            "ordinal": ordinal, "invoked_ordinal": ordinal,
            "completed_ordinal": None, "action": "invalid",
            "reason": reason, "source": "host-stream-invalid"})

    @staticmethod
    def _codex_action_payload(item):
        """Normalized identity-bearing payload for start/completion binding."""
        item_type = item.get("type")
        if item_type == "command_execution":
            command = item.get("command")
            return (("command", command) if isinstance(command, str)
                    else None)
        if item_type == "file_change":
            changes = item.get("changes")
            if not isinstance(changes, list):
                return None
            normalized = []
            for change in changes:
                if (not isinstance(change, dict) or
                        not isinstance(change.get("path"), str) or
                        not change.get("path") or
                        ("kind" in change and
                         not isinstance(change.get("kind"), str))):
                    return None
                normalized.append((change["path"], change.get("kind")))
            return ("changes", tuple(normalized))
        return None

    def _extract_tool_trace(self, out):
        """Normalize one host's raw stream into typed action intervals.

        Codex and Claude schemas are intentionally disjoint. Malformed or
        cross-host data remains in the diagnostic trace as an ``invalid``
        record, which contaminates ordering proof without discarding later
        valid events. Invocation and completion ordinals stay separate so a
        read completing after a write starts cannot be credited.
        """
        host_kind = self._host_read_profile()["host"]
        records = []
        pending = {}
        completed_ids = set()
        ordinal = 0
        for raw_line in (out or "").splitlines():
            ordinal += 1
            try:
                event = self._strict_json(raw_line)
            except (TypeError, json.JSONDecodeError, ValueError) as exc:
                self._invalid_trace(records, ordinal, str(exc))
                continue
            event_type = event.get("type")
            if host_kind == "codex":
                if event_type in ("assistant", "user"):
                    self._invalid_trace(
                        records, ordinal, "Claude envelope in Codex stream")
                    continue
                if event_type not in ("item.started", "item.completed"):
                    continue
                item = event.get("item")
                if not isinstance(item, dict):
                    self._invalid_trace(
                        records, ordinal, "Codex item is not an object")
                    continue
                item_type = item.get("type")
                if item_type not in ("command_execution", "file_change"):
                    continue
                item_id = item.get("id")
                if item_id is not None and not isinstance(item_id, str):
                    self._invalid_trace(
                        records, ordinal, "Codex item id is not a string")
                    continue
                if event_type == "item.started":
                    if not item_id:
                        self._invalid_trace(
                            records, ordinal,
                            "Codex started item lacks correlation id")
                        continue
                    if item_id in pending or item_id in completed_ids:
                        self._invalid_trace(
                            records, ordinal, "duplicate Codex item id")
                        continue
                    payload = self._codex_action_payload(item)
                    if payload is None:
                        self._invalid_trace(
                            records, ordinal,
                            "Codex started item lacks normalized payload")
                        continue
                    pending[item_id] = {
                        "ordinal": ordinal, "item_type": item_type,
                        "payload": payload}
                    continue
                if item_id and item_id in completed_ids:
                    self._invalid_trace(
                        records, ordinal, "duplicate Codex completion")
                    continue
                if item_id:
                    completed_ids.add(item_id)
                started = pending.pop(item_id, None) if item_id else None
                if started and started["item_type"] != item_type:
                    self._invalid_trace(
                        records, ordinal, "Codex item type changed")
                    continue
                completed_payload = self._codex_action_payload(item)
                if completed_payload is None or (
                        started and
                        completed_payload != started.get("payload")):
                    self._invalid_trace(
                        records, ordinal,
                        "Codex start/completion payload conflict")
                    continue
                invoked = started["ordinal"] if started else ordinal
                if item_type == "command_execution":
                    exit_code = item.get("exit_code")
                    command = item.get("command")
                    output = item.get("aggregated_output", "")
                    if (type(exit_code) is not int or
                            not isinstance(command, str) or
                            not isinstance(output, str) or
                            item.get("status") in ("failed", "error") or
                            event.get("status") in ("failed", "error")):
                        self._invalid_trace(
                            records, ordinal,
                            "invalid Codex command completion")
                        continue
                    records.append(self._bind_command_profile({
                        "ordinal": ordinal, "invoked_ordinal": invoked,
                        "completed_ordinal": ordinal, "action": "command",
                        "command": command, "output": output,
                        "exit_code": exit_code,
                        "source": "codex-command-completed"}))
                else:
                    changes = item.get("changes")
                    if (item.get("status") not in (None, "completed") or
                            not isinstance(changes, list)):
                        self._invalid_trace(
                            records, ordinal,
                            "invalid Codex file-change completion")
                        continue
                    for change in changes:
                        if (not isinstance(change, dict) or
                                not isinstance(change.get("path"), str) or
                                not change.get("path")):
                            self._invalid_trace(
                                records, ordinal,
                                "invalid Codex file-change path")
                            continue
                        records.append({
                            "ordinal": ordinal, "invoked_ordinal": invoked,
                            "completed_ordinal": ordinal, "action": "write",
                            "path": change["path"],
                            "source": "codex-file-change-completed"})
                continue

            # Claude stream-json normalization. Codex envelopes are a hard
            # host-isolation failure, while unrelated system/result messages
            # contain no file action and are ignored here.
            if event_type in ("item.started", "item.completed"):
                self._invalid_trace(
                    records, ordinal, "Codex envelope in Claude stream")
                continue
            if event_type not in ("assistant", "user"):
                continue
            message = event.get("message")
            if not isinstance(message, dict):
                self._invalid_trace(
                    records, ordinal, "Claude message is not an object")
                continue
            blocks = message.get("content")
            if not isinstance(blocks, list):
                self._invalid_trace(
                    records, ordinal, "Claude content is not a list")
                continue
            for block in blocks:
                if not isinstance(block, dict):
                    self._invalid_trace(
                        records, ordinal, "Claude content block is not object")
                    continue
                if event_type == "assistant" and \
                        block.get("type") == "tool_use":
                    tool_id = block.get("id")
                    tool = block.get("name")
                    inputs = block.get("input")
                    if (not isinstance(tool_id, str) or not tool_id or
                            tool_id in pending or tool_id in completed_ids or
                            not isinstance(tool, str) or
                            not isinstance(inputs, dict)):
                        self._invalid_trace(
                            records, ordinal, "invalid Claude tool use")
                        continue
                    action = None
                    path = None
                    command = None
                    if tool == "Read":
                        action, path = "read", inputs.get("file_path")
                    elif tool in ("Write", "Edit"):
                        action, path = "write", inputs.get("file_path")
                    elif tool == "Bash":
                        action, command = "command", inputs.get("command")
                    else:
                        continue
                    if ((action in ("read", "write") and
                         (not isinstance(path, str) or not path)) or
                            (action == "command" and
                             (not isinstance(command, str) or not command))):
                        self._invalid_trace(
                            records, ordinal, "invalid Claude tool input")
                        continue
                    pending[tool_id] = {
                        "ordinal": ordinal, "action": action,
                        "path": path, "command": command,
                        "source": f"claude-{tool.lower()}-completed"}
                elif event_type == "user" and \
                        block.get("type") == "tool_result":
                    tool_id = block.get("tool_use_id")
                    if (not isinstance(tool_id, str) or not tool_id or
                            tool_id not in pending or tool_id in completed_ids):
                        self._invalid_trace(
                            records, ordinal, "unmatched Claude tool result")
                        continue
                    is_error = block.get("is_error", None)
                    status = block.get("status")
                    if (("is_error" in block and
                         not isinstance(is_error, bool)) or
                            status in ("failed", "error") or
                            is_error is True):
                        self._invalid_trace(
                            records, ordinal, "failed Claude tool result")
                        completed_ids.add(tool_id)
                        pending.pop(tool_id, None)
                        continue
                    record = pending.pop(tool_id)
                    completed_ids.add(tool_id)
                    result_path = (((event.get("tool_use_result") or {})
                                    .get("file") or {}).get("filePath")
                                   if isinstance(
                                       event.get("tool_use_result"), dict)
                                   else None)
                    if (result_path is not None and
                            (not isinstance(result_path, str) or
                             (record.get("path") and
                              result_path != record["path"]))):
                        self._invalid_trace(
                            records, ordinal,
                            "Claude result path contradicts tool use")
                        continue
                    content = block.get("content", "")
                    if not isinstance(content, str):
                        content = ""
                    normalized = {
                        "ordinal": ordinal,
                        "invoked_ordinal": record["ordinal"],
                        "completed_ordinal": ordinal,
                        "action": record["action"],
                        "path": record.get("path"),
                        "command": record.get("command"),
                        "output": content, "exit_code": 0,
                        "source": record["source"]}
                    if normalized["action"] == "command":
                        normalized = self._bind_command_profile(normalized)
                    records.append(normalized)
        if pending:
            self._invalid_trace(
                records, ordinal + 1, "host action lacks completion")
        return sorted(records, key=lambda record: record["ordinal"])

    @staticmethod
    def _canonical_trace_path(observed, repo):
        if not isinstance(observed, str) or not observed or "\x00" in observed:
            return None
        text = observed.replace("\\", "/")
        if any(part == ".." for part in text.split("/")):
            return None
        root_native = os.path.abspath(repo)
        root = root_native.replace("\\", "/").rstrip("/")
        if os.path.isabs(observed):
            candidate = os.path.abspath(observed).replace("\\", "/")
        else:
            candidate = os.path.abspath(os.path.join(
                repo, *text.split("/"))).replace("\\", "/")
        if candidate != root and not candidate.startswith(root + "/"):
            return None
        # Lexical aliases through a symlink/junction do not establish exact
        # fixture-file identity without host-retained accessed-path evidence.
        real_candidate = os.path.realpath(candidate).replace(
            "\\", "/").rstrip("/")
        real_root = os.path.realpath(root_native).replace(
            "\\", "/").rstrip("/")
        if ((real_candidate != candidate.rstrip("/")) or
                (real_candidate != real_root and
                 not real_candidate.startswith(real_root + "/"))):
            return None
        return candidate.rstrip("/")

    @classmethod
    def _trace_path_match(cls, observed, expected, repo):
        obs = cls._canonical_trace_path(observed, repo)
        exp = cls._canonical_trace_path(expected, repo)
        return bool(obs and exp and obs == exp)

    @staticmethod
    def _command_name(token):
        name = str(token or "").replace("\\", "/").rsplit("/", 1)[-1]
        name = name.lower()
        return name[:-4] if name.endswith(".exe") else name

    @classmethod
    def _resolved_command(cls, stage, profile):
        """Resolve a small, explicitly supported transparent-wrapper set."""
        tokens = list(stage)
        index = 0
        assignment = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=")
        while index < len(tokens):
            while index < len(tokens) and assignment.match(tokens[index]):
                if tokens[index].split("=", 1)[0] in (
                        "PATH", "CDPATH", "ENV", "BASH_ENV", "SHELL"):
                    return "<unsupported>", tokens[index:]
                index += 1
            if index >= len(tokens):
                return None, []
            executable = tokens[index]
            name = cls._command_name(executable)
            index += 1
            normalized = executable.replace("\\", "/")
            expected_identity = (profile.get("executables") or {}).get(name)
            if expected_identity is None:
                return "<unsupported>", tokens[index:]
            expected_normalized = expected_identity.replace("\\", "/")
            if "/" in normalized and normalized != expected_normalized:
                return "<unsupported>", tokens[index:]
            if "/" in normalized and expected_normalized.startswith("builtin:"):
                return "<unsupported>", tokens[index:]
            if name == "command":
                if index < len(tokens) and tokens[index] in ("-v", "-V"):
                    return None, []
                if index < len(tokens) and tokens[index] == "-p":
                    index += 1
                continue
            if name in ("env", "sudo", "xargs") and index < len(tokens) and \
                    tokens[index] in ("--help", "--version"):
                return None, []
            if name == "exec" and index < len(tokens) and \
                    tokens[index] == "-a":
                if index + 1 >= len(tokens):
                    return "<unsupported>", []
                index += 2
            if name == "env":
                while index < len(tokens):
                    option = tokens[index]
                    if option in ("-i", "--ignore-environment"):
                        index += 1
                    elif option in ("-u", "--unset"):
                        if index + 1 >= len(tokens):
                            return "<unsupported>", []
                        index += 2
                    elif option.startswith("--unset="):
                        index += 1
                    else:
                        break
                while index < len(tokens) and assignment.match(tokens[index]):
                    if tokens[index].split("=", 1)[0] in (
                            "PATH", "CDPATH", "ENV", "BASH_ENV", "SHELL"):
                        return "<unsupported>", tokens[index:]
                    index += 1
                continue
            if name == "sudo":
                while index < len(tokens):
                    option = tokens[index]
                    if option in ("-n", "--non-interactive"):
                        index += 1
                    elif option in ("-u", "--user"):
                        if index + 1 >= len(tokens):
                            return "<unsupported>", []
                        index += 2
                    elif option.startswith("--user="):
                        index += 1
                    else:
                        break
                continue
            if name == "exec":
                continue
            if name == "xargs":
                # Raw aggregate events do not retain expanded child argv or
                # per-child status. Never infer content reads through xargs.
                return "<xargs-unsupported>", tokens[index:]
            return name, tokens[index:]
        return None, []

    @staticmethod
    def _target_mentioned(command, expected):
        text = str(command or "").replace("\\", "/")
        target = str(expected).replace("\\", "/").strip("/")
        return bool(target and target in text)

    @staticmethod
    def _replace_process_substitutions(text):
        """Replace balanced POSIX process substitutions with /dev/null.

        Their generated streams are not reads of path-looking text inside the
        substitution. Unbalanced forms remain untouched and fail parsing.
        """
        result = []
        index = 0
        while index < len(text):
            if index + 1 < len(text) and text[index:index + 2] in ("<(", ">("):
                depth = 1
                quote = None
                escaped = False
                end = index + 2
                while end < len(text) and depth:
                    char = text[end]
                    if escaped:
                        escaped = False
                    elif quote:
                        if char == quote:
                            quote = None
                        elif quote == '"' and char == "\\":
                            escaped = True
                    elif char in ("'", '"'):
                        quote = char
                    elif char == "\\":
                        escaped = True
                    elif char == "(":
                        depth += 1
                    elif char == ")":
                        depth -= 1
                    end += 1
                if depth:
                    return None
                result.append("/dev/null")
                index = end
                continue
            result.append(text[index])
            index += 1
        return "".join(result)

    @staticmethod
    def _unsupported_unquoted_syntax(text):
        quote = None
        escaped = False
        index = 0
        while index < len(text):
            char = text[index]
            if char == "\x00" or char in "\r\n":
                return True
            if escaped:
                escaped = False
                index += 1
                continue
            if quote:
                if char == quote:
                    quote = None
                elif quote == '"' and char == "\\":
                    escaped = True
                elif quote == '"' and char in ("$", "`"):
                    return True
                index += 1
                continue
            if char == "\\":
                escaped = True
            elif char in ("'", '"'):
                quote = char
            elif char == "`" or char in "(){}*?[~":
                return True
            elif char == "$":
                following = text[index + 1:index + 2]
                if following == "(" or following == "{" or \
                        following == "_" or following.isalpha():
                    return True
            index += 1
        return quote is not None

    @staticmethod
    def _has_dynamic_expansion(text):
        """Detect shell expansion outside single-quoted literal data."""
        quote = None
        escaped = False
        for char in str(text or ""):
            if escaped:
                escaped = False
                continue
            if char == "\\" and quote != "'":
                escaped = True
                continue
            if char in ("'", '"'):
                if quote is None:
                    quote = char
                elif quote == char:
                    quote = None
                continue
            if char in ("$", "`", "*", "?", "[", "{", "~") and \
                    quote != "'":
                return True
        return False

    @classmethod
    def _unwrap_host_command(cls, command, source,
                             wrapper_host_owned=False):
        """Unwrap only the frozen, host-owned Codex bash login envelope."""
        text = str(command or "")
        try:
            tokens = shlex.split(text, posix=True)
        except ValueError:
            return text, False
        if (wrapper_host_owned and
                source == "codex-command-completed" and len(tokens) == 3 and
                tokens[0] in ("/bin/bash", "/usr/bin/bash") and
                tokens[1] == "-lc"):
            return tokens[2], True
        return text, False

    @staticmethod
    def _split_redirections(tokens):
        """Return argv, stdin paths, output paths, or an error marker."""
        argv = []
        inputs = []
        outputs = []
        index = 0
        redirs = {"<", ">", ">>", "<>", ">&", "<&", "<<<", "<<"}
        while index < len(tokens):
            token = tokens[index]
            fd = None
            if (index + 1 < len(tokens) and token.isdigit() and
                    tokens[index + 1] in redirs):
                fd = int(token)
                index += 1
                token = tokens[index]
            if token not in redirs:
                argv.append(token)
                index += 1
                continue
            if index + 1 >= len(tokens):
                return None, None, None
            operand = tokens[index + 1]
            index += 2
            if token in (">&", "<&"):
                if operand != "-" and not operand.isdigit():
                    return None, None, None
                continue
            if token in ("<<<", "<<"):
                # Here strings/documents carry literal data, not a file path.
                continue
            if token in ("<", "<>"):
                if fd in (None, 0):
                    inputs.append(operand)
                if token == "<>" and fd in (None, 0, 1):
                    outputs.append(operand)
            elif token in (">", ">>"):
                outputs.append(operand)
        return argv, inputs, outputs

    @classmethod
    def _token_path_state(cls, operand, expected, repo):
        if not isinstance(operand, str):
            return "ambiguous"
        if any(mark in operand for mark in ("$", "`", "*", "?", "[", "]")):
            return "ambiguous" if cls._target_mentioned(operand, expected) \
                else "other"
        observed = cls._canonical_trace_path(operand.rstrip(","), repo)
        wanted = cls._canonical_trace_path(expected, repo)
        if observed and wanted and observed == wanted:
            return "exact"
        return "other"

    @classmethod
    def _output_identifies_path(cls, output, expected, repo):
        """Recognize a search-result filename only at the line's source edge."""
        wanted = cls._canonical_trace_path(expected, repo)
        if not wanted:
            return False
        relative = os.path.relpath(wanted, os.path.abspath(repo)).replace(
            "\\", "/")
        absolute = wanted.replace("\\", "/")
        for raw_line in str(output or "").splitlines():
            line = raw_line.strip().replace("\\", "/")
            if (line == relative or line.startswith(relative + ":") or
                    line == absolute or line.startswith(absolute + ":")):
                return True
        return False

    @classmethod
    def _scope_contains_target(cls, scope, expected, repo):
        observed = cls._canonical_trace_path(scope, repo)
        wanted = cls._canonical_trace_path(expected, repo)
        return bool(observed and wanted and
                    (wanted == observed or wanted.startswith(observed + "/")))

    @classmethod
    def _reader_effect(cls, name, args, stdin_paths, expected, repo, output,
                       shell_dialect):
        """Return ``read``, ``not``, or ``ambiguous`` for one shell stage."""
        if name in ("<unsupported>", "<xargs-unsupported>"):
            return "ambiguous" if any(
                cls._target_mentioned(token, expected)
                for token in args) else "not"
        if name in (None, "true", "false", "exit", "printf", "echo",
                    "find", "ls", "stat", "git", "touch", "tee"):
            return "not"
        if name in ("sh", "bash", "cmd", "powershell", "pwsh"):
            return "ambiguous" if any(
                cls._target_mentioned(token, expected)
                for token in args) else "not"

        direct = list(stdin_paths)
        scopes = []
        terminal_no_read = False
        reader = name in ("cat", "sed", "head", "tail", "get-content",
                          "type", "rg", "grep")
        if not reader:
            return "ambiguous" if any(
                cls._target_mentioned(token, expected)
                for token in args) else "not"
        dialect_readers = {
            "posix": {"cat", "sed", "head", "tail", "rg", "grep"},
            "powershell": {"get-content", "rg", "grep"},
            "cmd": {"type", "rg", "grep"},
        }
        if name not in dialect_readers.get(shell_dialect, set()):
            return "ambiguous" if any(
                cls._target_mentioned(token, expected)
                for token in args + stdin_paths) else "not"
        if any(arg in ("--help", "--version") for arg in args):
            return "not"

        if name in ("cat", "type"):
            direct.extend(arg for arg in args if arg == "-" or
                          not arg.startswith("-"))
        elif name in ("head", "tail"):
            index = 0
            while index < len(args):
                arg = args[index]
                if arg in ("-n", "--lines"):
                    if index + 1 >= len(args):
                        return "ambiguous"
                    terminal_no_read = args[index + 1] == "0"
                    index += 2
                elif arg.startswith("--lines="):
                    terminal_no_read = arg.split("=", 1)[1] == "0"
                    index += 1
                elif arg.startswith("-") and arg[1:].isdigit():
                    terminal_no_read = int(arg[1:]) == 0
                    index += 1
                else:
                    direct.append(arg)
                    index += 1
        elif name == "get-content":
            index = 0
            while index < len(args):
                arg = args[index]
                lower = arg.lower()
                if lower in ("-delimiter", "-totalcount", "-tail",
                             "-readcount", "-encoding", "-filter",
                             "-include", "-exclude"):
                    if index + 1 >= len(args):
                        return "ambiguous"
                    index += 2
                elif lower in ("-literalpath", "-path"):
                    if index + 1 >= len(args):
                        return "ambiguous"
                    direct.extend(args[index + 1].split(","))
                    index += 2
                elif arg.startswith("-"):
                    index += 1
                else:
                    direct.extend(arg.split(","))
                    index += 1
        elif name == "sed":
            index = 0
            saw_program = False
            while index < len(args):
                arg = args[index]
                if arg == "--":
                    index += 1
                    break
                if arg in ("-e", "--expression"):
                    if index + 1 >= len(args):
                        return "ambiguous"
                    saw_program = True
                    index += 2
                elif arg.startswith("-e") and len(arg) > 2:
                    saw_program = True
                    index += 1
                elif arg in ("-f", "--file"):
                    if index + 1 >= len(args):
                        return "ambiguous"
                    direct.append(args[index + 1])
                    saw_program = True
                    index += 2
                elif arg.startswith("-f") and len(arg) > 2:
                    direct.append(arg[2:])
                    saw_program = True
                    index += 1
                elif arg.startswith("-"):
                    index += 1
                elif not saw_program:
                    saw_program = True
                    index += 1
                else:
                    break
            direct.extend(args[index:])
        else:  # grep / rg
            if name == "rg" and "--files" in args[:args.index("--")
                                                   if "--" in args
                                                   else len(args)]:
                return "not"
            index = 0
            pattern_supplied = False
            output_identity_safe = True
            unsafe_output_modes = {
                "--no-filename", "-I", "--replace", "-r", "--json",
                "--vimgrep", "--count", "--count-matches",
                "--files-with-matches", "-l", "--files-without-match",
                "--only-matching", "-o", "--passthru", "--heading",
                "-h", "--null", "-0", "--null-data", "--stats"}
            unsafe_output_options_with_value = {
                "--label", "--path-separator", "--field-match-separator",
                "--field-context-separator"}
            while index < len(args):
                arg = args[index]
                if arg == "--":
                    index += 1
                    break
                if arg in ("-e", "--regexp"):
                    if index + 1 >= len(args):
                        return "ambiguous"
                    pattern_supplied = True
                    index += 2
                elif arg.startswith("-e") and len(arg) > 2:
                    pattern_supplied = True
                    index += 1
                elif arg in ("-f", "--file"):
                    if index + 1 >= len(args):
                        return "ambiguous"
                    direct.append(args[index + 1])
                    pattern_supplied = True
                    index += 2
                elif arg.startswith("-f") and len(arg) > 2:
                    direct.append(arg[2:])
                    pattern_supplied = True
                    index += 1
                elif arg in ("-g", "--glob", "--type", "--type-add"):
                    if index + 1 >= len(args):
                        return "ambiguous"
                    index += 2
                elif arg in ("--replace", "-r"):
                    output_identity_safe = False
                    if index + 1 >= len(args):
                        return "ambiguous"
                    index += 2
                elif arg.startswith("--replace=") or (
                        arg.startswith("-r") and len(arg) > 2):
                    output_identity_safe = False
                    index += 1
                elif arg in unsafe_output_options_with_value:
                    output_identity_safe = False
                    if index + 1 >= len(args):
                        return "ambiguous"
                    index += 2
                elif any(arg.startswith(option + "=")
                         for option in unsafe_output_options_with_value):
                    output_identity_safe = False
                    index += 1
                elif arg in unsafe_output_modes or (
                        arg.startswith("-") and not arg.startswith("--") and
                        any(flag in arg[1:] for flag in ("I", "l", "o"))):
                    output_identity_safe = False
                    index += 1
                elif arg.startswith("-"):
                    index += 1
                else:
                    break
            remaining = args[index:]
            if not pattern_supplied:
                if not remaining:
                    return "not"
                remaining = remaining[1:]
            for operand in remaining:
                state = cls._token_path_state(operand, expected, repo)
                if state == "exact":
                    direct.append(operand)
                elif (state == "other" and
                      output_identity_safe and
                      cls._scope_contains_target(operand, expected, repo) and
                      cls._output_identifies_path(output, expected, repo)):
                    scopes.append(operand)

        if terminal_no_read:
            return "not"
        states = [cls._token_path_state(path, expected, repo)
                  for path in direct]
        if "exact" in states or scopes:
            return "read"
        if "ambiguous" in states:
            return "ambiguous"
        return "not"

    @classmethod
    def _parse_shell(cls, command, expected, repo, output, source, profile,
                     wrapper_host_owned=False):
        text, _unwrapped = cls._unwrap_host_command(
            command, source, wrapper_host_owned)
        if "\n" in text or "\r" in text:
            heredoc = re.fullmatch(
                r"(?s)(?P<head>.*)<<-?\s*(?P<tag>[A-Za-z_][A-Za-z0-9_]*)"
                r"\r?\n.*\r?\n(?P=tag)\s*", text)
            if heredoc:
                text = heredoc.group("head") + " << " + heredoc.group("tag")
        replaced = cls._replace_process_substitutions(text)
        if replaced is None or cls._unsupported_unquoted_syntax(replaced):
            return None
        try:
            lexer = shlex.shlex(
                replaced, posix=True, punctuation_chars=";&|<>")
            lexer.whitespace_split = True
            lexer.commenters = "#"
            tokens = list(lexer)
        except ValueError:
            return None
        if not tokens:
            return []
        separators = {"|", "|&", "&&", "||", ";"}
        unsupported = {"&", ";;", ";&", ";;&"}
        if profile.get("shell_dialect") != "posix" and any(
                token in separators | unsupported |
                {"<", ">", ">>", "<>", ">&", "<&", "<<<", "<<"}
                for token in tokens):
            return None
        if (tokens[0] in separators | unsupported or
                tokens[-1] in separators | unsupported):
            return None
        pipelines = []
        connectors = []
        stages = []
        stage = []
        for token in tokens + [";"]:
            if token in unsupported:
                return None
            if token in ("|", "|&"):
                if not stage:
                    return None
                stages.append(stage)
                stage = []
            elif token in ("&&", "||", ";"):
                if not stage:
                    return None
                stages.append(stage)
                pipelines.append(stages)
                stages = []
                stage = []
                if token != ";" or len(pipelines) > 0:
                    connectors.append(token)
            else:
                stage.append(token)
        # The synthetic trailing ';' adds one connector too many.
        connectors = connectors[:max(0, len(pipelines) - 1)]
        parsed = []
        for pipeline in pipelines:
            parsed_stages = []
            for raw_stage in pipeline:
                argv, stdin_paths, outputs = cls._split_redirections(raw_stage)
                if argv is None or not argv:
                    return None
                name, args = cls._resolved_command(argv, profile)
                effect = cls._reader_effect(
                    name, args, stdin_paths, expected, repo, output,
                    profile.get("shell_dialect"))
                constant = True if name == "true" else (
                    False if name == "false" else None)
                terminates = False
                if name == "exit":
                    if len(args) > 1 or (args and not args[0].isdigit()):
                        return None
                    constant = (not args or int(args[0]) == 0)
                    terminates = True
                parsed_stages.append({
                    "name": name, "effect": effect, "constant": constant,
                    "terminates": terminates, "outputs": outputs,
                    "args": args})
            parsed.append(parsed_stages)
        return parsed, connectors

    def _classify_command_target(self, record, expected, repo):
        """Classify one exact target as content-read/not-read/fail-closed."""
        cls = type(self)
        command = record.get("command")
        profile = self._host_read_profile(repo)
        source = str(record.get("source") or "")
        if not source.startswith(profile["host"] + "-"):
            return ("fail-closed" if cls._target_mentioned(command, expected)
                    else "not-content-read")
        if (not profile.get("attestation_id") or
                record.get("host_read_attestation_id") !=
                profile.get("attestation_id") or
                record.get("shell_dialect") !=
                profile.get("shell_dialect")):
            return "fail-closed"
        parsed = cls._parse_shell(
            command, expected, repo, record.get("output", ""),
            record.get("source"), profile,
            bool(record.get("wrapper_host_owned")))
        if parsed is None:
            return ("fail-closed" if (
                    cls._target_mentioned(command, expected) or
                    cls._has_dynamic_expansion(command))
                    else "not-content-read")
        pipelines, connectors = parsed
        if not pipelines:
            return "not-content-read"
        if cls._target_mentioned(command, expected):
            known = {
                None,
                "cat", "sed", "head", "tail", "get-content", "type",
                "rg", "grep", "true", "false", "exit", "printf", "echo",
                "find", "ls", "stat", "git", "touch", "tee"}
            for pipeline in pipelines:
                for stage in pipeline:
                    if stage["name"] in (
                            "<unsupported>", "<xargs-unsupported>"):
                        stage["effect"] = "ambiguous"
                    elif stage["name"] not in known:
                        stage["effect"] = "ambiguous"
        # A literal empty printf feeding xargs proves that no child argv was
        # executed. This narrow negative control does not infer any expansion.
        for pipeline in pipelines:
            if (len(pipeline) >= 2 and pipeline[0]["name"] == "printf" and
                    pipeline[0]["args"] == [""] and
                    pipeline[1]["name"] == "<xargs-unsupported>"):
                pipeline[1]["effect"] = "not"
        stage_count = sum(len(pipeline) for pipeline in pipelines)
        if stage_count > 12:
            return ("fail-closed" if cls._target_mentioned(command, expected)
                    else "not-content-read")
        variables = []
        for p_index, pipeline in enumerate(pipelines):
            for s_index, stage in enumerate(pipeline):
                if stage["constant"] is None:
                    variables.append((p_index, s_index))
        if len(variables) > 12:
            return ("fail-closed" if cls._target_mentioned(command, expected)
                    else "not-content-read")
        exit_code = record.get("exit_code")
        if type(exit_code) is not int:
            return "fail-closed"
        wanted_status = exit_code == 0
        worlds = []
        for mask in range(1 << len(variables)):
            statuses = {}
            for bit, key in enumerate(variables):
                statuses[key] = bool(mask & (1 << bit))
            executed = []
            current_status = None
            terminated = False
            for p_index, pipeline in enumerate(pipelines):
                if p_index:
                    connector = connectors[p_index - 1]
                    should_run = (connector == ";" or
                                  (connector == "&&" and current_status) or
                                  (connector == "||" and not current_status))
                    if terminated or not should_run:
                        executed.append([])
                        continue
                pipeline_exec = []
                for s_index, stage in enumerate(pipeline):
                    status = (stage["constant"] if
                              stage["constant"] is not None else
                              statuses[(p_index, s_index)])
                    pipeline_exec.append((stage, status, s_index))
                executed.append(pipeline_exec)
                current_status = pipeline_exec[-1][1]
                if len(pipeline) == 1 and pipeline[0]["terminates"]:
                    terminated = True
            if current_status is None or current_status != wanted_status:
                continue
            read = False
            ambiguous = False
            for p_index, pipeline_exec in enumerate(executed):
                for stage, status, s_index in pipeline_exec:
                    if stage["effect"] == "ambiguous":
                        ambiguous = True
                    elif stage["effect"] == "read":
                        no_match_read = (
                            exit_code == 1 and
                            stage["name"] in ("grep", "rg") and
                            p_index == len(executed) - 1 and
                            s_index == len(pipelines[p_index]) - 1)
                        if status or no_match_read:
                            read = True
            worlds.append((read, ambiguous))
        if not worlds:
            return "fail-closed"
        if all(read and not ambiguous for read, ambiguous in worlds):
            return "content-read"
        if any(read or ambiguous for read, ambiguous in worlds):
            return "fail-closed"
        return "not-content-read"

    @classmethod
    def _command_write_paths(cls, record):
        """Return lexically explicit shell output paths for ordering only."""
        command, _unwrapped = cls._unwrap_host_command(
            record.get("command"), record.get("source"),
            bool(record.get("wrapper_host_owned")))
        replaced = cls._replace_process_substitutions(command)
        if replaced is None or cls._unsupported_unquoted_syntax(replaced):
            return []
        try:
            lexer = shlex.shlex(
                replaced, posix=True, punctuation_chars=";&|<>")
            lexer.whitespace_split = True
            lexer.commenters = "#"
            tokens = list(lexer)
        except ValueError:
            return []
        paths = []
        stage = []
        for token in tokens + [";"]:
            if token in ("|", "|&", "&&", "||", ";"):
                if stage:
                    _argv, _inputs, outputs = cls._split_redirections(stage)
                    if outputs is not None:
                        paths.extend(outputs)
                stage = []
            else:
                stage.append(token)
        return paths

    def _run_host_checks(self, fx, repo):
        hc = fx.get("host_checks")
        if not hc:
            return None
        import re as _re
        out = {}
        detail = {}
        for spec in hc.get("specs", []):
            key = spec["key"]
            kind = spec["kind"]
            if kind == "file_regex":
                path = os.path.join(repo, spec["path"])
                try:
                    text = open(path, encoding="utf-8").read()
                except OSError:
                    out[key] = False
                    detail[key] = "file unreadable"
                    continue
                ok = True
                if spec.get("must_match") and not _re.search(
                        spec["must_match"], text):
                    ok = False
                if spec.get("must_not_match") and _re.search(
                        spec["must_not_match"], text):
                    ok = False
                out[key] = ok
            elif kind == "json_fields_equal":
                rel = str(spec.get("path", "")).replace("\\", "/")
                expected = spec.get("equals")
                if (not rel or os.path.isabs(rel) or rel.startswith("/") or
                        any(part in ("", ".", "..")
                            for part in rel.split("/"))):
                    raise framework.AdapterError(
                        f"unsafe JSON host-check path {rel!r}")
                if not isinstance(expected, dict) or not expected:
                    raise framework.AdapterError(
                        "json_fields_equal requires non-empty equals object")
                path = os.path.abspath(os.path.join(
                    repo, *rel.split("/")))
                root = os.path.abspath(repo)
                try:
                    escaped = os.path.commonpath((root, path)) != root
                except ValueError:
                    escaped = True
                if escaped:
                    raise framework.AdapterError(
                        f"unsafe JSON host-check path {rel!r}")
                try:
                    with open(path, encoding="utf-8") as fh:
                        observed = json.load(fh)
                except (OSError, UnicodeError, json.JSONDecodeError) as exc:
                    out[key] = False
                    detail[key] = f"JSON unreadable: {type(exc).__name__}"
                    continue
                if not isinstance(observed, dict):
                    out[key] = False
                    detail[key] = "JSON root is not an object"
                    continue
                mismatches = [
                    field for field, value in expected.items()
                    if observed.get(field) != value
                ]
                out[key] = not mismatches
                if mismatches:
                    detail[key] = "mismatched fields: " + ",".join(mismatches)
            elif kind == "path_access_order":
                reads = [str(path).replace("\\", "/")
                         for path in spec.get("reads", [])]
                write = str(spec.get("write", "")).replace("\\", "/")
                if (not reads or not write or
                        any(os.path.isabs(path) or ".." in path.split("/")
                            for path in reads + [write])):
                    raise framework.AdapterError(
                        "path_access_order requires safe relative paths")

                if self.formal:
                    adjudication = self._formal_host_read_results.get(key)
                    if not isinstance(adjudication, dict):
                        raise framework.AdapterError(
                            "formal path_access_order lacks a sealed "
                            "host-read adjudication — INVALID")
                    out[key] = adjudication.get("property_status") == "PASS"
                    detail[key] = json.dumps(
                        {name: adjudication.get(name) for name in
                         ("property_status", "host_status", "overall_status",
                          "ordered", "write_completed", "live_preimage",
                          "ordering_source")},
                        sort_keys=True, separators=(",", ":"))
                    continue

                contaminated = any(
                    record.get("action") == "invalid"
                    for record in self._tool_trace)

                def first_read_completion(expected):
                    hits = []
                    for record in self._tool_trace:
                        if record.get("action") == "read" and \
                                self._trace_path_match(
                                    record.get("path"), expected, repo):
                            completed = record.get(
                                "completed_ordinal", record.get("ordinal"))
                            if completed is not None:
                                hits.append(completed)
                        elif record.get("action") == "command" and \
                                self._classify_command_target(
                                    record, expected, repo) == "content-read":
                            completed = record.get(
                                "completed_ordinal", record.get("ordinal"))
                            if completed is not None:
                                hits.append(completed)
                    return min(hits) if hits else None

                write_invocations = []
                write_completions = []
                for record in self._tool_trace:
                    if record.get("action") == "write" and \
                            self._trace_path_match(
                                record.get("path"), write, repo):
                        invoked = record.get(
                            "invoked_ordinal", record.get("ordinal"))
                        completed = record.get(
                            "completed_ordinal", record.get("ordinal"))
                        if invoked is not None:
                            write_invocations.append(invoked)
                        if completed is not None:
                            write_completions.append(completed)
                    elif record.get("action") == "command":
                        for path in self._command_write_paths(record):
                            if self._trace_path_match(path, write, repo):
                                invoked = record.get(
                                    "invoked_ordinal", record.get("ordinal"))
                                if invoked is not None:
                                    write_invocations.append(invoked)

                read_ordinals = [first_read_completion(path)
                                 for path in reads]
                write_ordinal = (min(write_invocations)
                                 if write_invocations else None)
                ok = (not contaminated and write_ordinal is not None and
                      bool(write_completions) and
                      all(value is not None for value in read_ordinals) and
                      max(read_ordinals) < write_ordinal)
                out[key] = ok
                detail[key] = (
                    f"read_ordinals={read_ordinals}; "
                    f"write_ordinal={write_ordinal}; "
                    f"write_completed={bool(write_completions)}; "
                    f"stream_contaminated={contaminated}")
            elif kind == "validate_run_root":
                out[key], detail[key] = self._validate_run_root(repo)
            elif kind == "run_root_exists":
                base = os.path.join(repo, *spec.get(
                    "dir", ".IMPLEMENTAUDIT/runs").split("/"))
                dirs = ([d for d in os.listdir(base)
                         if os.path.isdir(os.path.join(base, d))]
                        if os.path.isdir(base) else [])
                out[key] = bool(dirs)
                detail[key] = (",".join(dirs[:3]) if dirs
                               else "no run root on disk")
            else:
                raise framework.AdapterError(
                    f"unknown host check kind {kind!r}")
        out["_detail"] = detail
        return out

    def _emit_host_observation(self, fx):
        """Execute a fixture-declared deterministic observation generator
        and return (artifact_relpath, bytes) or None. `token_validator`
        genuinely RUNS the fixture's planted weak rule (accept iff the token
        appears) over fixture-declared case texts — the recorded verdicts
        are host observations of the planted rule's behavior, never model
        claims (E5 live-capture; #9 phase 2b)."""
        spec = fx.get("host_observation_spec")
        if not spec:
            return None
        if spec.get("kind") != "token_validator":
            raise framework.AdapterError(
                f"unknown host observation kind {spec.get('kind')!r}")
        token = spec["token"]
        verdicts = {field: ("accept" if token in text else "reject")
                    for field, text in spec["cases"].items()}
        return spec["file"], json.dumps(
            verdicts, indent=1, sort_keys=True).encode("utf-8")

    def _staged_script(self, repo, rel):
        """Locate a product script in the STAGED payload (preferred) or the
        canonical checkout."""
        candidates = []
        staged = getattr(self, "_staged_payload_dir", None)
        if staged:
            candidates.append(os.path.join(staged, rel))
        if self.product_checkout:
            candidates.append(os.path.join(
                self.product_checkout, "skills", "implementaudit", rel))
        for c in candidates:
            if os.path.isfile(c):
                return c
        return None

    def _validate_run_root(self, repo):
        """Run the product-owned validate-run-root.sh against the run root
        the mission created. Deterministic host observation. EXACTLY ONE run
        root is expected; zero or multiple is a flagged non-pass (never a
        newest-file guess).

        bash is invoked with cwd=repo and REPO-RELATIVE POSIX paths: the
        `bash` on PATH may be git-bash (mounts at /c/…) OR WSL bash (mounts
        at /mnt/c/…), and an absolute host path only works for one of them.
        Relative paths from a set cwd are correct for both, and for a native
        Linux lane."""
        base = os.path.join(repo, ".IMPLEMENTAUDIT", "runs")
        if not os.path.isdir(base):
            return False, "no .IMPLEMENTAUDIT/runs directory"
        dirs = [d for d in os.listdir(base)
                if os.path.isdir(os.path.join(base, d))]
        if not dirs:
            return False, "no run root claimed"
        if len(dirs) > 1:
            return False, (f"ambiguous: {len(dirs)} run roots under "
                           f".IMPLEMENTAUDIT/runs (expected exactly one)")
        target_abs = os.path.join(base, dirs[0])
        script = self._staged_script(repo, os.path.join(
            "scripts", "validate-run-root.sh"))
        if not script:
            return False, "validate-run-root.sh not available"
        script_rel = os.path.relpath(script, repo).replace("\\", "/")
        target_rel = os.path.relpath(target_abs, repo).replace("\\", "/")
        try:
            proc = subprocess.run(
                ["bash", script_rel, target_rel], cwd=repo,
                capture_output=True, text=True, timeout=60)
        except (OSError, subprocess.TimeoutExpired) as exc:
            return False, f"validator did not run: {exc!r}"
        target = target_abs
        rel = os.path.relpath(target, repo).replace("\\", "/")
        return proc.returncode == 0, (
            f"{rel}: exit {proc.returncode}; "
            f"{(proc.stderr or proc.stdout or '').strip()[:200]}")

    def identity_fields(self, run_id, fixture_id, resolved,
                        started_at, ended_at, staged_hash=None):
        ident = {"product_tag": "unattested", "product_commit": "0" * 40,
                 "product_tree": "0" * 40,
                 "installed_payload_sha256": "0" * 64}
        if self.product_checkout:
            ident.update(framework.product_identity(
                self.product_checkout,
                expected_tag=self.product_expected_rev))
            canonical = framework.payload_hash(os.path.join(
                self.product_checkout, "skills", "implementaudit"))
            ident["payload_source_sha256"] = canonical
            ident["installed_payload_sha256"] = staged_hash or canonical
        ident.update({
            "run_id": run_id, "fixture_id": fixture_id,
            "harness_commit": _harness_commit(),
            "adapter_name": self.name, "adapter_version": self.version,
            "adapter_sha256": bundlelib.sha256_file(
                os.path.abspath(__file__)),
            "model_requested": self.requested_model_canonical(),
            "model_resolved": resolved, "host": self.name,
            "started_at": started_at,
            "ended_at": ended_at,
        })
        return ident

    # Precise, word-bounded credential patterns — real key/token SHAPES,
    # never substrings of ordinary prose ("risk-", "task-").
    _CRED_PATTERNS = None

    @classmethod
    def _cred_patterns(cls):
        import re as _re
        if _BaseAdapter._CRED_PATTERNS is None:
            _BaseAdapter._CRED_PATTERNS = [
                _re.compile(r"sk-ant-[A-Za-z0-9_-]{8,}"),
                _re.compile(r"sk-proj-[A-Za-z0-9_-]{8,}"),
                _re.compile(r"\bsk-[A-Za-z0-9]{24,}"),
                _re.compile(r"\bghp_[A-Za-z0-9]{20,}"),
                _re.compile(r"\bgho_[A-Za-z0-9]{20,}"),
                _re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}"),
                _re.compile(r"\bxox[abprs]-[A-Za-z0-9-]{10,}"),
                _re.compile(r'"(access_token|refresh_token|api_key|'
                            r'apiKey|Authorization)"\s*:\s*"[^"]{8,}"'),
                _re.compile(r"(OPENAI_API_KEY|ANTHROPIC_API_KEY)\s*="
                            r"\s*\S{8,}"),
                _re.compile(r"Bearer\s+[A-Za-z0-9._-]{20,}"),
                _re.compile(r"\beyJ[A-Za-z0-9_-]{20,}\."
                            r"[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}"),
            ]
        return _BaseAdapter._CRED_PATTERNS

    def _quarantine_if_leak(self, root, quarantine_name, only=None):
        """Scan `root` for credential shapes; on a hit, quarantine the
        cleartext (create-once, out of the ordinary result set) and return
        (pattern, filename) WITHOUT raising, so every custody location can
        be scrubbed before the run terminalizes. `only` restricts to named
        top-level files. Reports class + location, never the value."""
        hit = None
        if only is not None:
            candidates = [os.path.join(root, n) for n in only
                          if os.path.isfile(os.path.join(root, n))]
        else:
            candidates = [os.path.join(base, name)
                          for base, _d, files in os.walk(root)
                          for name in files]
        for path in candidates:
            try:
                text = open(path, encoding="utf-8").read()
            except (UnicodeDecodeError, OSError):
                continue
            for pat in self._cred_patterns():
                if pat.search(text):
                    hit = (pat.pattern, os.path.basename(path))
                    break
            if hit:
                break
        if not hit:
            return None
        if only is not None:
            qdir = os.path.join(root, quarantine_name)
            os.makedirs(qdir, exist_ok=True)
            for n in only:
                src = os.path.join(root, n)
                if os.path.isfile(src):
                    os.replace(src, os.path.join(qdir, n))
        else:
            quarantine = os.path.join(os.path.dirname(root), quarantine_name)
            try:
                os.replace(root, quarantine)
            except OSError:
                pass
        return hit

    def scan_for_leaks(self, root, quarantine_name="quarantine-bundle",
                       only=None):
        """Single-location credential scan that RAISES on a hit (used by the
        mock tests and any single-target caller); run_mission uses
        `_quarantine_if_leak` directly to scrub every location first."""
        hit = self._quarantine_if_leak(root, quarantine_name, only=only)
        if hit:
            raise framework.AdapterError(
                f"credential pattern {hit[0]!r} found in file "
                f"{hit[1]!r} — moved to {quarantine_name}; custody violation")


def _harness_commit():
    try:
        out = subprocess.run(["git", "-C", HERE, "rev-parse", "HEAD"],
                             capture_output=True, text=True)
        v = out.stdout.strip()
        return v if out.returncode == 0 and len(v) == 40 else "0" * 40
    except OSError:
        return "0" * 40


class CodexAdapter(_BaseAdapter):
    """Configuration L: Codex CLI / gpt-5.6-luna / reasoning effort max
    ("Luna Max" = that TUPLE, never a concatenated slug). Fails closed
    below the minimum CLI version and on any identity, effort, or policy
    substitution. Payload staged by the adapter into the temp CODEX_HOME."""

    name = "codex-cli"
    MIN_CLI = (0, 144, 0)
    REJECTED_SLUGS = ("luna-max", "gpt-5.6-luna-max")
    capabilities = frozenset({"read", "write", "shell", "script-execution",
                              "git-read"})

    def __init__(self, requested_model="gpt-5.6-luna",
                 reasoning_effort="max", codex_binary="codex",
                 codex_home=None, **kw):
        if requested_model in self.REJECTED_SLUGS:
            raise framework.AdapterError(
                f"{requested_model!r} is a concatenated slug, not a model: "
                "'Luna Max' means model gpt-5.6-luna + reasoning effort max")
        super().__init__(
            [codex_binary, "exec", "--model", "{model}",
             "-c", f'model_reasoning_effort="{reasoning_effort}"',
             "--sandbox", "workspace-write", "--json",
             "--skip-git-repo-check", "-"],
            requested_model, **kw)
        self.codex_binary = codex_binary
        self.reasoning_effort_requested = reasoning_effort
        self.codex_home = codex_home
        self.auth_mode = None  # recorded (chatgpt-subscription/api); no secrets

    def check_cli_version(self):
        """Fail closed below 0.144.0 (GPT-5.6 access requirement)."""
        try:
            proc = subprocess.run([self.codex_binary, "--version"],
                                  capture_output=True, text=True,
                                  timeout=60)
        except subprocess.TimeoutExpired:
            raise framework.AdapterError(
                "codex --version timed out — fail closed")
        out = (proc.stdout or "") + (proc.stderr or "")
        import re as _re
        m = _re.search(r"(\d+)\.(\d+)\.(\d+)", out)
        if proc.returncode != 0 or not m:
            raise framework.AdapterError(
                f"cannot determine codex CLI version: {out.strip()[:120]}")
        ver = tuple(int(x) for x in m.groups())
        if ver < self.MIN_CLI:
            raise framework.AdapterError(
                f"codex CLI {'.'.join(map(str, ver))} is below the required "
                f"0.144.0 for gpt-5.6 access — fail closed")
        return ver

    def check_auth_mode(self):
        """Record auth mode; refuse metered/API auth without owner cap."""
        env = _clean_env({"CODEX_HOME": self.codex_home or ""})
        try:
            proc = subprocess.run([self.codex_binary, "login", "status"],
                                  capture_output=True, text=True, env=env,
                                  timeout=60)
        except subprocess.TimeoutExpired:
            raise framework.AdapterError(
                "codex login status timed out — fail closed")
        out = (proc.stdout or "") + (proc.stderr or "")
        if "ChatGPT" in out:
            self.auth_mode = "chatgpt-subscription"
        elif "API" in out.upper():
            raise framework.AdapterError(
                "codex is using API-key (metered) auth — blocked without an "
                "explicit owner-approved spend cap")
        else:
            raise framework.AdapterError(
                f"unknown codex auth mode — fail closed: {out.strip()[:120]}")
        return self.auth_mode

    def _mission_env(self, repo):
        if not self.codex_home:
            raise framework.AdapterError(
                "CodexAdapter requires a fresh temporary CODEX_HOME "
                "(never the real user home)")
        real_home = os.path.realpath(os.path.expanduser("~/.codex"))
        if os.path.realpath(self.codex_home) == real_home:
            raise framework.AdapterError(
                "refusing to run against the REAL codex home")
        return _clean_env({"CODEX_HOME": self.codex_home})

    def stage_payload(self, repo):
        """Install immutable v0.3.1.0 into the temp CODEX_HOME's native
        skill location; hash the STAGED copy; fail closed on mismatch."""
        if not self.product_checkout:
            raise framework.AdapterError("no product checkout to stage")
        if not self.codex_home:
            raise framework.AdapterError(
                "cannot stage payload without a temp CODEX_HOME")
        src = os.path.join(self.product_checkout, "skills", "implementaudit")
        dst = os.path.join(self.codex_home, "skills", "implementaudit")
        if os.path.exists(dst):
            raise framework.AdapterError(
                "payload already present in CODEX_HOME — the temp home must "
                "be fresh (create-once staging)")
        shutil.copytree(src, dst)
        staged = framework.payload_hash(dst)
        source = framework.payload_hash(src)
        if staged != source:
            raise framework.AdapterError(
                "staged payload hash does not match the canonical source — "
                "fail closed")
        self._staged_payload_dir = dst
        self._staged_payload_hash = staged
        return staged

    def _select_session(self, repo, not_before=None):
        """Select the session record by BOUND identity: session_meta cwd
        match + not-before time window. EXACTLY ONE match is required when
        any session exists; zero matches returns (None, {}); multiple
        matches raise (INVALID). Never 'the newest file'."""
        import glob as _glob
        if not self.codex_home:
            return None, {}
        matches = []
        for f in sorted(_glob.glob(os.path.join(
                self.codex_home, "sessions", "**", "*.jsonl"),
                recursive=True)):
            try:
                first = json.loads(open(f, encoding="utf-8").readline())
            except (OSError, json.JSONDecodeError):
                continue
            p = first.get("payload", {})
            if first.get("type") != "session_meta":
                continue
            if os.path.normcase(p.get("cwd", "")) != os.path.normcase(repo):
                continue
            nb = not_before or self._not_before
            if nb:
                st = _parse_ts(p.get("timestamp", ""))
                nbt = _parse_ts(nb)
                if st is None or nbt is None or st < nbt:
                    continue
            matches.append((f, p))
        if not matches:
            return None, {}
        # Subagent lineage (candidate-product fanout, #49): a codex thread
        # spawned by the bound session writes its OWN session file into the
        # SAME isolated home with an explicit parent_thread_id. Children
        # whose parent chain terminates in a matched session are the same
        # mission identity, not ambiguity. Identity stays fail-closed:
        # anything except exactly one ROOT session — or a child whose
        # parent is not among the matched ids — still refuses.
        own_ids = {(p.get("id") or p.get("session_id")) for _f, p in matches}
        roots = [(f, p) for f, p in matches
                 if not p.get("parent_thread_id")]
        children = [(f, p) for f, p in matches if p.get("parent_thread_id")]
        foreign = [f for f, p in children
                   if p.get("parent_thread_id") not in own_ids]
        if len(roots) != 1 or foreign:
            raise framework.AdapterError(
                f"session identity ambiguous: {len(matches)} session files "
                f"({len(roots)} root, {len(foreign)} foreign-parent) match "
                f"this run's cwd+time binding — INVALID")
        best = roots[0][0]
        subagent_ids = sorted(
            str(p.get("id") or p.get("session_id")) for _f, p in children)
        ctx = {}
        try:
            for line in open(best, encoding="utf-8"):
                d = json.loads(line)
                pl = d.get("payload", {})
                if d.get("type") == "session_meta":
                    ctx["cli_version"] = pl.get("cli_version")
                    ctx["session_id"] = pl.get("session_id")
                elif d.get("type") == "turn_context":
                    ctx["model"] = pl.get("model")
                    ctx["effort"] = pl.get("effort")
                    ctx["approval_policy"] = pl.get("approval_policy")
                    sp = pl.get("sandbox_policy") or {}
                    ctx["sandbox_resolved"] = sp.get("type")
        except (OSError, json.JSONDecodeError):
            return best, {}
        if subagent_ids:
            ctx["subagent_sessions"] = subagent_ids
        return best, ctx

    def _session_agent_events(self, repo):
        """Host-owned agent_message events from the bound session file."""
        f, _ctx = self._select_session(repo)
        if not f:
            return None, []
        events = []
        try:
            for line in open(f, encoding="utf-8"):
                d = json.loads(line)
                pl = d.get("payload", {})
                if d.get("type") == "event_msg" and \
                        pl.get("type") == "agent_message" and \
                        isinstance(pl.get("message"), str):
                    events.append({"role": "assistant",
                                   "content": pl["message"],
                                   "ts": d.get("timestamp")})
        except (OSError, json.JSONDecodeError):
            return f, []
        return f, events

    def resolve_model(self, out):
        _f, ctx = self._select_session(
            getattr(self, "_current_repo", None) or "")
        model = ctx.get("model")
        if model:
            self.models_observed = [{
                "model": model, "role": "root-agent",
                "source": "host session turn_context",
                "session_id": ctx.get("session_id")}]
        return model

    def preflight(self):
        self.check_cli_version()
        self.check_auth_mode()

    def requested_policy(self):
        return {"sandbox": "workspace-write", "approval": "never",
                "tools": "codex-shell", "network": "restricted",
                "writable_roots": ["<fixture-repo cwd>"]}

    def check_policy(self, repo):
        f, ctx = self._select_session(repo)
        self.policy_resolved = {
            "class": "host-owned (session turn_context)",
            "sandbox": ctx.get("sandbox_resolved"),
            "approval": ctx.get("approval_policy"),
            "session_id": ctx.get("session_id"),
            "cli_version": ctx.get("cli_version")}
        if ctx.get("sandbox_resolved") != "workspace-write":
            raise framework.AdapterError(
                f"policy mismatch: requested sandbox workspace-write but "
                f"host resolved {ctx.get('sandbox_resolved')!r} - INVALID")
        if ctx.get("approval_policy") not in ("never", None):
            # requested approval 'never'; a host that resolved a different
            # approval policy changes the execution contract (independent
            # review) — recorded, not silently accepted.
            raise framework.AdapterError(
                f"policy mismatch: requested approval 'never' but host "
                f"resolved {ctx.get('approval_policy')!r} - INVALID")

    def collect_raw_stream(self, repo, outcome):
        f, _ctx = self._select_session(repo)
        if f:
            return open(f, "rb").read()
        return None

    def post_checks(self, out):
        self.check_effort(out)

    def resolve_effort(self, out):
        _f, ctx = self._select_session(
            getattr(self, "_current_repo", None) or "")
        return ctx.get("effort")

    def check_effort(self, out):
        resolved = self.resolve_effort(out)
        self.reasoning_effort_resolved = resolved
        if resolved is None:
            raise framework.AdapterError(
                "missing resolved reasoning effort: the host session "
                "turn_context does not record effort — fail closed")
        if resolved != self.reasoning_effort_requested:
            raise framework.AdapterError(
                f"reasoning-effort substitution: requested "
                f"{self.reasoning_effort_requested!r}, resolved "
                f"{resolved!r} — fail closed")
        return resolved

    def parse_events(self, out):
        """HOST-ASSIGNED events. Primary: `codex exec --json` JSONL
        agent_message events (every intermediate agent message, in order).
        The exec transcript echoes the user mission (which names fixture
        markers), so nothing outside host-typed agent messages is ever
        scored as assistant content. Legacy fallback for mock hosts: plain
        'codex' reply sections, else full text."""
        text = (out or "").strip()
        if not text:
            raise ValueError("empty host output")
        events = []
        for line in text.splitlines():
            line = line.strip()
            if not line.startswith("{"):
                continue
            try:
                d = json.loads(line)
            except json.JSONDecodeError:
                continue
            for obj in (d, d.get("msg") or {}, d.get("payload") or {}):
                if isinstance(obj, dict) and \
                        obj.get("type") == "agent_message" and \
                        isinstance(obj.get("message"), str):
                    events.append({"role": "assistant",
                                   "content": obj["message"],
                                   "ts": d.get("timestamp")})
                    break
        if events:
            self._events_source = "codex-exec-json"
            return events
        lines = text.splitlines()
        starts = [i for i, ln in enumerate(lines) if ln.strip() == "codex"]
        if starts:
            sections = []
            for s in starts:
                end = len(lines)
                for j in range(s + 1, len(lines)):
                    if lines[j].strip() in ("tokens used", "--------",
                                            "codex"):
                        end = j
                        break
                sec = chr(10).join(lines[s + 1:end]).strip()
                if sec:
                    sections.append(sec)
            if not sections:
                raise ValueError("empty codex reply sections")
            self._events_source = "codex-exec-transcript"
            return [{"role": "assistant", "content": s} for s in sections]
        self._events_source = "codex-stdout-fallback"
        return [{"role": "assistant", "content": text}]

    def reconcile_events(self, events, repo, outcome):
        """Cross-check stdout-parsed events against the host-owned session
        record. When the session records agent messages, every scored event
        must appear there; when stdout parsing fell back to legacy text and
        the session HAS agent messages, the session events are scored."""
        f, sess_events = self._session_agent_events(repo)
        if not sess_events:
            # A REAL codex lane (temp CODEX_HOME set) must yield host-owned
            # session agent messages; scoring raw stdout as assistant content
            # when the host recorded none would let the echoed mission forge
            # markers. Only the pure-mock path (no codex_home) may fall back.
            if self.codex_home and self._events_source in (
                    "codex-stdout-fallback", "codex-exec-transcript"):
                raise framework.AdapterError(
                    "no host-owned agent messages in the bound session for a "
                    "real codex run — refusing to score raw stdout (INVALID)")
            return events
        sess_texts = {e["content"] for e in sess_events}
        if self._events_source == "codex-exec-json":
            missing = [e for e in events if e["content"] not in sess_texts]
            if missing:
                raise framework.AdapterError(
                    f"event mismatch: {len(missing)} stdout agent message(s)"
                    f" absent from the host session record — INVALID")
            return events
        self._events_source = "codex-session-jsonl"
        return sess_events


class ClaudeAdapter(_BaseAdapter):
    """Configuration O: Claude Code CLI / Opus High. Temp CLAUDE_CONFIG_DIR;
    payload staged into the fixture repo at .claude/skills/implementaudit
    (project-scoped) with a CLAUDE.md pointer — a LABELED packaging
    difference from Configuration L. Scored events are the host-assigned
    per-message assistant events from `--output-format stream-json`."""

    name = "claude-cli"

    def __init__(self, requested_model="opus", effort="high",
                 config_dir=None, resolved_expect="claude-opus-4-8",
                 tools="Read Glob Grep Write Edit Bash", **kw):
        super().__init__(
            ["claude", "-p", "--model", "{model}", "--effort", effort,
             "--output-format", "stream-json", "--verbose",
             "--allowedTools", tools],
            requested_model, **kw)
        self.config_dir = config_dir
        self.resolved_expect = resolved_expect
        self.reasoning_effort_requested = effort
        self.tools = tools
        caps = set()
        toolset = set(tools.split())
        if toolset & {"Read", "Glob", "Grep"}:
            caps.add("read")
        if toolset & {"Write", "Edit"}:
            caps.add("write")
        if "Bash" in toolset:
            caps.update({"shell", "script-execution", "git-read"})
        self.capabilities = frozenset(caps)
        self._session_id = None
        self._event_models = []
        self._result_json = None
        self._init_event = None

    def requested_model_canonical(self):
        # "opus" is an alias; the canonical requested identity for the
        # provenance check is the expected resolved name.
        return self.resolved_expect

    def _mission_env(self, repo):
        if not self.config_dir:
            raise framework.AdapterError(
                "ClaudeAdapter requires a fresh temporary CLAUDE_CONFIG_DIR")
        real = os.path.realpath(os.path.expanduser("~/.claude"))
        if os.path.realpath(self.config_dir) == real:
            raise framework.AdapterError(
                "refusing to run against the REAL claude config home")
        return _clean_env({"CLAUDE_CONFIG_DIR": self.config_dir})

    def stage_payload(self, repo):
        """Project-scoped payload presentation (labeled difference)."""
        if not self.product_checkout:
            raise framework.AdapterError("no product checkout to stage")
        src = os.path.join(self.product_checkout, "skills", "implementaudit")
        dst = os.path.join(repo, ".claude", "skills", "implementaudit")
        shutil.copytree(src, dst)
        staged = framework.payload_hash(dst)
        source = framework.payload_hash(src)
        if staged != source:
            raise framework.AdapterError(
                "staged payload hash does not match the canonical source — "
                "fail closed")
        with open(os.path.join(repo, "CLAUDE.md"), "x",
                  encoding="utf-8") as fh:
            fh.write("Use the implementaudit skill at "
                     ".claude/skills/implementaudit/SKILL.md for this "
                     "task.\n")
        self._staged_payload_dir = dst
        self._staged_payload_hash = staged
        return staged

    @staticmethod
    def _extract_json(out):
        """Legacy: locate the last line that parses as a JSON object (the
        `--output-format json` result; mock hosts)."""
        for line in reversed((out or "").splitlines()):
            line = line.strip()
            if line.startswith("{"):
                try:
                    return json.loads(line)
                except json.JSONDecodeError:
                    continue
        return None

    def requested_policy(self):
        return {"sandbox": "claude-headless-tool-permissions",
                "approval": "auto-deny-outside-allowed",
                "tools": self.tools,
                "network": "tool-mediated only",
                "writable_roots": ["<fixture-repo cwd>"]}

    def check_policy(self, repo):
        # Claude Code exposes no host-owned resolved-policy record in print
        # mode; this attestation is ADAPTER INFERENCE plus canary evidence
        # and is labeled as such — never presented as host-resolved fact.
        self.policy_resolved = {
            "class": "adapter-attested (NOT host-owned)",
            "tools": self.tools + " (argv-requested)",
            "note": "claude -p auto-denies permission prompts outside the "
                    "allowed tool set; write containment verified "
                    "empirically by pre-smoke canary, not by a host record"}

    def parse_events(self, out):
        """HOST-ASSIGNED per-message assistant events from stream-json.
        Every intermediate assistant turn is retained; user/system/tool
        events and prompt echoes are never scored as assistant content.
        Legacy fallback for mock hosts: single `result` JSON."""
        # Reset ALL per-mission state (independent review: a reused adapter
        # must never inherit the prior run's session id / result / models).
        self._event_models = []
        self._session_id = None
        self._result_json = None
        self._init_event = None
        self._saw_result = False
        events = []
        for line in (out or "").splitlines():
            line = line.strip()
            if not line.startswith("{"):
                continue
            try:
                d = json.loads(line)
            except json.JSONDecodeError:
                continue
            t = d.get("type")
            if d.get("session_id"):
                self._session_id = d["session_id"]
            if t == "assistant":
                m = d.get("message") or {}
                parts = [b.get("text", "") for b in (m.get("content") or [])
                         if isinstance(b, dict) and b.get("type") == "text"]
                text = "\n".join(p for p in parts if p)
                if text.strip():
                    events.append({"role": "assistant", "content": text,
                                   "ts": d.get("timestamp")})
                    if m.get("model"):
                        self._event_models.append(m["model"])
            elif t == "result":
                self._result_json = d
                self._saw_result = True
            elif t == "system":
                if self._init_event is None:
                    self._init_event = d
        if events:
            # A complete stream-json run ends with a `result` event; its
            # absence means the stream was truncated (network cut, kill)
            # mid-run and must not score off a partial transcript
            # (independent review blocking).
            if not self._saw_result:
                raise ValueError(
                    "stream-json ended without a result event — truncated "
                    "transcript, INVALID")
            self._events_source = "claude-stream-json"
            return events
        data = self._extract_json(out)
        if data is None:
            raise ValueError("no JSON object found in host output")
        self._result_json = data
        result = data.get("result")
        if not isinstance(result, str) or not result.strip():
            raise ValueError("JSON output lacks a result field")
        self._events_source = "claude-result-json"
        return [{"role": "assistant", "content": result}]

    def reconcile_events(self, events, repo, outcome):
        """Corroborate scored events against the project transcript bound
        by the EXACT returned session id. Zero or multiple transcript
        matches for a known session id is INVALID; without a session id
        (legacy mock path) the check is skipped."""
        if not self._session_id or not self.config_dir:
            return events
        import glob as _glob
        matches = _glob.glob(os.path.join(
            self.config_dir, "projects", "*",
            self._session_id + ".jsonl"))
        if len(matches) != 1:
            raise framework.AdapterError(
                f"transcript binding failed: {len(matches)} project "
                f"transcript(s) match session id — INVALID")
        transcript_texts = set()
        try:
            for line in open(matches[0], encoding="utf-8"):
                try:
                    d = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if d.get("type") != "assistant":
                    continue
                m = d.get("message") or {}
                for b in (m.get("content") or []):
                    if isinstance(b, dict) and b.get("type") == "text":
                        transcript_texts.add(b.get("text", ""))
        except OSError as exc:
            raise framework.AdapterError(
                f"transcript unreadable for bound session — INVALID: {exc}")
        self._transcript_path = matches[0]
        missing = [e for e in events
                   if e["content"] not in transcript_texts and
                   not any(e["content"] in t or t in e["content"]
                           for t in transcript_texts)]
        if missing:
            raise framework.AdapterError(
                f"event mismatch: {len(missing)} stream assistant "
                f"message(s) absent from the bound project transcript — "
                f"INVALID")
        return events

    def collect_raw_stream(self, repo, outcome):
        if self._session_id and self.config_dir:
            import glob as _glob
            matches = _glob.glob(os.path.join(
                self.config_dir, "projects", "*",
                self._session_id + ".jsonl"))
            if len(matches) == 1:
                return open(matches[0], "rb").read()
        return None

    def resolve_model(self, out):
        """Root model from HOST-ASSIGNED assistant events (exactly one
        distinct model must author them). Legacy mock fallback: a single-
        model `modelUsage` map. No token-count heuristics; no
        expectation-confirming fallback."""
        observed = []
        distinct = sorted(set(self._event_models))
        usage = (self._result_json or {}).get("modelUsage") or {}
        for m in distinct:
            observed.append({
                "model": m, "role": "root-assistant-events",
                "events": self._event_models.count(m),
                "source": "host-assigned message.model"})
        for k, v in sorted(usage.items()):
            observed.append({
                "model": k, "role": "modelUsage-accounting",
                "output_tokens": (v or {}).get("outputTokens")
                if isinstance(v, dict) else None,
                "host_internal_auxiliary": k not in distinct,
                "source": "result.modelUsage"})
        self.models_observed = observed
        if len(distinct) == 1:
            return distinct[0]
        if len(distinct) > 1:
            return None  # ambiguous root authorship — fail closed upstream
        if len(usage) == 1:
            return next(iter(usage))
        return None

    def post_checks(self, out):
        resolved = None
        init = self._init_event or {}
        for key in ("effort", "reasoning_effort", "effortLevel"):
            if isinstance(init.get(key), str):
                resolved = init[key]
                break
        if resolved is None:
            # The host does not expose resolved effort in print mode:
            # recorded honestly, never guessed to match.
            resolved = "unavailable-from-host"
        self.reasoning_effort_resolved = resolved
        if resolved not in ("unavailable-from-host",
                            self.reasoning_effort_requested):
            raise framework.AdapterError(
                f"reasoning-effort substitution: requested "
                f"{self.reasoning_effort_requested!r}, resolved "
                f"{resolved!r} — fail closed")


def sanitize_bundle(bundle_root):
    """RAW-FIRST custody: the sealed bundle is never touched. This creates a
    SEPARATE sanitized derivative directory next to it plus a redaction
    manifest binding derivative files to the raw originals by hash."""
    import re as _re
    home = os.path.expanduser("~").replace("\\", "/")
    pat = _re.compile(_re.escape(home) + "|" +
                      _re.escape(os.path.expanduser("~")).replace("\\", "\\\\"),
                      _re.IGNORECASE)
    out_root = bundle_root.rstrip("/\\") + "-sanitized"
    os.makedirs(out_root, exist_ok=False)
    manifest = {"schema": "implementaudit-redaction-manifest-v1",
                "raw_bundle": bundle_root, "files": {}}
    for base, _dirs, files in os.walk(bundle_root):
        for name in files:
            src = os.path.join(base, name)
            rel = os.path.relpath(src, bundle_root)
            data = open(src, "rb").read()
            raw_hash = bundlelib._sha256_bytes(data)
            try:
                text = data.decode("utf-8")
                red, n = pat.subn("<home>", text)
                out = red.encode("utf-8")
            except UnicodeDecodeError:
                out, n = data, 0
            dst = os.path.join(out_root, rel)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            with open(dst, "xb") as fh:
                fh.write(out)
            manifest["files"][rel] = {
                "raw_sha256": raw_hash,
                "sanitized_sha256": bundlelib._sha256_bytes(out),
                "redactions": n, "rule": "home-path -> <home>"}
    with open(os.path.join(out_root, "redaction-manifest.json"), "x",
              encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=1, sort_keys=True)
    return out_root


if __name__ == "__main__":
    print(__doc__)
    print("Adapters are DISABLED BY DEFAULT; every spawn requires "
          "require_owner_approval() and refuses in CI unconditionally.")
