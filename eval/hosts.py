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

import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "lib"))
sys.path.insert(0, HERE)
import adapters as framework  # noqa: E402
import bundle as bundlelib  # noqa: E402
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


def _spawn_once(argv, env, cwd, timeout_s, stdin_text=None, on_started=None):
    """Exactly one spawn — no hidden retry lives anywhere in this module.
    `on_started` runs immediately after the process exists (create-once
    process-started custody); if it fails the child is killed and the run
    terminalizes ERROR."""
    try:
        proc = subprocess.Popen(argv, env=env, cwd=cwd,
                                stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                text=True, encoding="utf-8",
                                errors="replace")
    except OSError as exc:
        return HostRunResult("error", f"host spawn failed: {exc}")
    if on_started is not None:
        try:
            on_started(proc)
        except Exception as exc:
            proc.kill()
            proc.communicate()
            return HostRunResult(
                "error", f"process-started custody write failed: {exc!r}")
    try:
        out, err = proc.communicate(input=stdin_text, timeout=timeout_s)
    except subprocess.TimeoutExpired:
        proc.kill()
        out, err = proc.communicate()
        r = HostRunResult("error", f"host timeout after {timeout_s}s")
        r.stdout, r.stderr = out or "", err or ""
        return r
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
    version = "2"
    timeout_s = 1800
    capabilities = frozenset()

    def __init__(self, host_argv_template, requested_model,
                 product_checkout=None, host_cwd=None):
        self.host_argv_template = list(host_argv_template)
        self.requested_model = requested_model
        self.product_checkout = product_checkout
        self.host_cwd = host_cwd
        self.models_observed = []
        self._events_source = None
        self._staged_payload_hash = None
        self._not_before = None

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
        (framework.require_owner_approval if _test_gate is None
         else _test_gate)()
        self.preflight()
        reconcilelib.reconcile_custody(custody_root)
        run_root = framework.custody.resolve_and_create_output_dir(
            custody_root, run_id)
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
        with open(os.path.join(run_root, "run-intent.json"), "x",
                  encoding="utf-8") as fh:
            json.dump(intent, fh, indent=1, sort_keys=True)
        result = HostRunResult("error", "adapter did not terminalize")
        spawned = False
        payload_before = None
        try:
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
            before = reposnapshot.snapshot(repo)
            mission = fx["mission"]
            argv = [a.replace("{model}", self.requested_model)
                    for a in self.host_argv_template]

            def _on_started(proc):
                rec = {"schema": "implementaudit-process-started-v1",
                       "run_id": run_id, "pid": proc.pid,
                       "cwd": self.host_cwd or repo,
                       "started_at": _utc_now(),
                       "argv_sha256": bundlelib._sha256_bytes(
                           "\x00".join(argv).encode("utf-8")),
                       "requested_model": self.requested_model_canonical(),
                       "temp_home": intent["temp_home"]}
                with open(os.path.join(run_root, "process-started.json"),
                          "x", encoding="utf-8") as fh:
                    json.dump(rec, fh, indent=1, sort_keys=True)

            spawned = True
            outcome = _spawn_once(argv, self._mission_env(repo),
                                  self.host_cwd or repo, self.timeout_s,
                                  stdin_text=mission,
                                  on_started=_on_started)
            # Preserve the raw host stdout/stderr at the RUN ROOT immediately
            # — for BOTH the nonzero-exit/timeout error path and the normal
            # path — so no INVALID/ERROR classification ever destroys the
            # diagnostic evidence (v0.3.2.0 R1 lessons).
            for rel, data in (("host-stdout.raw",
                               getattr(outcome, "stdout", "")),
                              ("host-stderr.raw",
                               getattr(outcome, "stderr", ""))):
                try:
                    with open(os.path.join(run_root, rel), "xb") as fh:
                        fh.write((data or "").encode("utf-8"))
                except FileExistsError:
                    pass
            if isinstance(outcome, HostRunResult):
                result = outcome
                return result
            raw_stream = self.collect_raw_stream(repo, outcome)
            try:
                events = self.parse_events(outcome.stdout)
            except ValueError as exc:
                result = HostRunResult(
                    "invalid", f"malformed structured output: {exc}")
                return result
            events = self.reconcile_events(events, repo, outcome)
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
                only=("host-stdout.raw", "host-stderr.raw"))
            if h2:
                hits.append(h2)
            if hits:
                raise framework.AdapterError(
                    f"credential pattern {hits[0][0]!r} found in file "
                    f"{hits[0][1]!r} — moved to quarantine; custody "
                    f"violation ({len(hits)} location(s) scrubbed)")
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
            # Credential nonretention on EVERY exit path (independent review
            # blocking): the run-root raw host output is scrubbed and the
            # terminal detail is redacted regardless of kind — a host that
            # printed a secret then exited nonzero/timed out must not leave
            # cleartext in host-stderr.raw or in terminal.json's detail.
            try:
                self._quarantine_if_leak(
                    run_root, "quarantine-raw",
                    only=("host-stdout.raw", "host-stderr.raw"))
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

    # --- deterministic host checks (fixture-declared) ----------------------
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

    @staticmethod
    def _bash_path(p):
        """Translate a Windows path to a bash/MSYS POSIX path so `bash`
        receives 'C:\\x\\y' as '/c/x/y' (backslashes were being eaten,
        giving exit 127 on the Windows Claude lane). No-op on POSIX."""
        if os.name != "nt":
            return p
        p = os.path.abspath(p)
        drive, rest = os.path.splitdrive(p)
        return "/" + drive[0].lower() + rest.replace("\\", "/")

    def _validate_run_root(self, repo):
        """Run the product-owned validate-run-root.sh against the run root
        the mission created. Deterministic host observation. EXACTLY ONE run
        root is expected; zero or multiple is a flagged non-pass (never a
        newest-file guess)."""
        base = os.path.join(repo, ".IMPLEMENTAUDIT", "runs")
        if not os.path.isdir(base):
            return False, "no .IMPLEMENTAUDIT/runs directory"
        dirs = [os.path.join(base, d) for d in os.listdir(base)
                if os.path.isdir(os.path.join(base, d))]
        if not dirs:
            return False, "no run root claimed"
        if len(dirs) > 1:
            return False, (f"ambiguous: {len(dirs)} run roots under "
                           f".IMPLEMENTAUDIT/runs (expected exactly one)")
        target = dirs[0]
        script = self._staged_script(repo, os.path.join(
            "scripts", "validate-run-root.sh"))
        if not script:
            return False, "validate-run-root.sh not available"
        try:
            proc = subprocess.run(
                ["bash", self._bash_path(script), self._bash_path(target)],
                capture_output=True, text=True, timeout=60)
        except (OSError, subprocess.TimeoutExpired) as exc:
            return False, f"validator did not run: {exc!r}"
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
            ident.update(framework.product_identity(self.product_checkout))
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
            matches.append(f)
        if not matches:
            return None, {}
        if len(matches) > 1:
            raise framework.AdapterError(
                f"session identity ambiguous: {len(matches)} session files "
                f"match this run's cwd+time binding — INVALID")
        best = matches[0]
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
