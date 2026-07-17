#!/usr/bin/env python3
"""Real host adapters for #9 phase 2b — DISABLED BY DEFAULT.

Two host-model CONFIGURATIONS (model and host effects are confounded and
always reported as configurations, never as pure model comparisons):

  Configuration L — Codex CLI / gpt-5.6-luna / reasoning effort max
      ("Luna Max" is that TUPLE — model + effort — never a concatenated
      slug; `luna-max` and `gpt-5.6-luna-max` are REJECTED at construction).
      Phase-E verified: works under ChatGPT-subscription auth on Codex CLI
      0.144.5 (the Phase-D metered-auth conclusion is retracted as an
      invalid test on an outdated CLI). Requires CLI >= 0.144.0 (fail
      closed); auth mode recorded, API/metered auth blocked without an
      owner cap; requested and resolved reasoning effort recorded
      separately when the host exposes them. Payload presentation:
      immutable v0.3.1.0 installed into a fresh temporary CODEX_HOME at
      skills/implementaudit/ (Codex's native skill location).

  Configuration O — Claude Code CLI / Opus High (`ClaudeAdapter`)
      Verified working selector: `claude -p --model opus --effort high
      --output-format json`; resolved identity is read from the CLI's JSON
      `modelUsage` keys (e.g. claude-opus-4-8). Payload presentation
      DIFFERS from Codex and is labeled: Claude Code has no CODEX_HOME-style
      skill install here, so the payload is staged into the fixture
      repository at `.claude/skills/implementaudit/` (project-scoped) with a
      CLAUDE.md pointer. Cross-configuration comparisons must carry this
      packaging difference as a caveat.

Shared guarantees (mock-tested in eval/test_hosts.py; NO live mission in CI):
  - `require_owner_approval()` gates every spawn; unconditional refusal in
    CI; no hidden retry (exactly one spawn per mission);
  - clean constructed environment (no os.environ passthrough beyond an
    allowlist) — host processes never see unrelated session variables;
  - credentials live only in the temp home's auth files; never in argv,
    prompts, bundles, or logs; bundles are scanned for leak sentinels;
  - requested vs resolved model identity: mismatch or missing provenance
    FAILS CLOSED (AdapterError) and is recorded;
  - canonical payload checkout is hashed before/after the mission; any
    write to it aborts the run;
  - fixture repo isolation + before/after snapshots per the merged
    foundation; create-once bundles under custody roots;
  - host nonzero exit or timeout => ERROR-class result; malformed
    structured output => INVALID-class result; both preserved, never
    silently retried.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "lib"))
sys.path.insert(0, HERE)
import adapters as framework  # noqa: E402
import bundle as bundlelib  # noqa: E402
import reposnapshot  # noqa: E402

ENV_ALLOWLIST = ("SYSTEMROOT", "WINDIR", "PATH", "TEMP", "TMP", "HOME",
                 "USERPROFILE", "COMSPEC", "PATHEXT", "LANG", "LC_ALL",
                 "APPDATA", "LOCALAPPDATA", "PROGRAMDATA")


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


def _spawn_once(argv, env, cwd, timeout_s, stdin_text=None):
    """Exactly one spawn — no hidden retry lives anywhere in this module."""
    try:
        proc = subprocess.run(argv, env=env, cwd=cwd, capture_output=True,
                              text=True, timeout=timeout_s,
                              input=stdin_text)
    except subprocess.TimeoutExpired:
        return HostRunResult("error", f"host timeout after {timeout_s}s")
    except OSError as exc:
        return HostRunResult("error", f"host spawn failed: {exc}")
    if proc.returncode != 0:
        return HostRunResult(
            "error", f"host exit {proc.returncode}: {proc.stderr[:300]}")
    return proc


class _BaseAdapter:
    name = "base"
    version = "1"
    timeout_s = 1800

    def __init__(self, host_argv_template, requested_model,
                 product_checkout=None, host_cwd=None):
        self.host_argv_template = list(host_argv_template)
        self.requested_model = requested_model
        self.product_checkout = product_checkout
        self.host_cwd = host_cwd

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
        overridden by subclasses). Returns the staged-payload hash."""
        return None

    def run_mission(self, fixture_id, custody_root, run_id, work_root,
                    _test_gate=None, call_ordinal=1):
        """PRE-SPAWN CUSTODY + TOTAL TERMINALIZATION: the create-once run
        root and run-intent.json exist BEFORE any process launches, and a
        terminal record (PASS-side bundle / FAIL / INVALID / ERROR) is
        written in a finally path for EVERY launch — a launched call with no
        record is impossible. `_test_gate` is code-level test plumbing only.
        """
        (framework.require_owner_approval if _test_gate is None
         else _test_gate)()
        self.preflight()
        run_root = framework.custody.resolve_and_create_output_dir(
            custody_root, run_id)
        intent = {
            "schema": "implementaudit-run-intent-v1", "run_id": run_id,
            "fixture_id": fixture_id, "call_ordinal": call_ordinal,
            "fixture_sha256": bundlelib.sha256_file(os.path.join(
                HERE, "fixtures", fixture_id, "fixture.json")),
            "product_checkout": self.product_checkout,
            "adapter_name": self.name,
            "adapter_sha256": bundlelib.sha256_file(
                os.path.abspath(__file__)),
            "harness_commit": _harness_commit(),
            "model_requested": self.requested_model_canonical(),
            "reasoning_effort_requested": getattr(
                self, "reasoning_effort_requested", None),
            "policy_requested": self.requested_policy(),
            "temp_home": getattr(self, "codex_home", None) or getattr(
                self, "config_dir", None),
            "started_at": "pre-spawn",
        }
        with open(os.path.join(run_root, "run-intent.json"), "x",
                  encoding="utf-8") as fh:
            json.dump(intent, fh, indent=1, sort_keys=True)
        result = HostRunResult("error", "adapter did not terminalize")
        spawned = False
        try:
            payload_before = (framework.payload_hash(self.product_checkout)
                              if self.product_checkout else None)
            repo = framework.seed_fixture_repo(fixture_id, work_root)
            self._current_repo = repo
            if self.product_checkout:
                self.stage_payload(repo)
            before = reposnapshot.snapshot(repo)
            fixture_path = os.path.join(HERE, "fixtures", fixture_id,
                                        "fixture.json")
            fixture_bytes = open(fixture_path, "rb").read()
            mission = json.loads(fixture_bytes.decode())["mission"]
            argv = [a.replace("{model}", self.requested_model)
                    for a in self.host_argv_template]
            spawned = True
            outcome = _spawn_once(argv, self._mission_env(repo),
                                  self.host_cwd or repo, self.timeout_s,
                                  stdin_text=mission)
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
            after = reposnapshot.snapshot(repo)
            cmp_ = reposnapshot.compare_with_repo(repo, before, after)
            fields = self.identity_fields(run_id, fixture_id, resolved)
            fields["policy_requested"] = self.requested_policy()
            fields["policy_resolved"] = getattr(self, "policy_resolved", {})
            bundle_root = os.path.join(run_root, "bundle")
            ev_objs = [bundlelib.make_event(run_id, fixture_id, i + 1,
                                            e["role"], e["content"],
                                            kind=e.get("kind", "message"))
                       for i, e in enumerate(events)]
            derived_meta = {
                "schema": "implementaudit-derived-view-v1",
                "transform": self.name + "-reply-extraction-v1",
                "source_raw_sha256": (bundlelib._sha256_bytes(raw_stream)
                                      if raw_stream else None),
                "rules": "assistant-reply extraction; tool/system events "
                         "preserved in raw stream; no deletion",
            }
            artifacts = dict(self.mission_artifacts or {})
            if raw_stream:
                artifacts["raw-host-events.jsonl"] = raw_stream
            artifacts["derived-transform.json"] = json.dumps(
                derived_meta, indent=1).encode()
            bundlelib.write_bundle(
                bundle_root, fields, ev_objs, fixture_bytes,
                ("MISSION:" + chr(10) + mission).encode(),
                repo_before=before, repo_after=after, repo_comparison=cmp_,
                artifacts=artifacts)
            self.scan_for_leaks(bundle_root)
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
            term = {"schema": "implementaudit-run-terminal-v1",
                    "run_id": run_id, "spawned": spawned,
                    "kind": result.kind, "detail": str(result.detail)[:500],
                    "resolved_model": result.resolved_model,
                    "policy_resolved": getattr(self, "policy_resolved", {})}
            path = os.path.join(run_root, "terminal.json")
            try:
                with open(path, "x", encoding="utf-8") as fh:
                    json.dump(term, fh, indent=1, sort_keys=True)
            except FileExistsError:
                with open(os.path.join(run_root, "terminal-2.json"), "x",
                          encoding="utf-8") as fh:
                    json.dump(term, fh, indent=1, sort_keys=True)

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

    def identity_fields(self, run_id, fixture_id, resolved):
        ident = {"product_tag": "unattested", "product_commit": "0" * 40,
                 "product_tree": "0" * 40,
                 "installed_payload_sha256": "0" * 64}
        if self.product_checkout:
            ident.update(framework.product_identity(self.product_checkout))
            ident["installed_payload_sha256"] = framework.payload_hash(
                self.product_checkout)
        ident.update({
            "run_id": run_id, "fixture_id": fixture_id,
            "harness_commit": _harness_commit(),
            "adapter_name": self.name, "adapter_version": self.version,
            "adapter_sha256": bundlelib.sha256_file(
                os.path.abspath(__file__)),
            "model_requested": self.requested_model_canonical(),
            "model_resolved": resolved, "host": self.name,
            "started_at": "1970-01-01T00:00:00Z",
            "ended_at": "1970-01-01T00:00:01Z",
        })
        return ident

    # Precise credential patterns — real API keys / token FIELDS, not
    # substrings that appear in ordinary prose ("risk-", "task").
    _CRED_PATTERNS = None

    def scan_for_leaks(self, bundle_root):
        """Credential nonretention: bundles must not contain auth material.
        Uses precise key/token patterns to avoid false positives on prose."""
        import re as _re
        if _BaseAdapter._CRED_PATTERNS is None:
            _BaseAdapter._CRED_PATTERNS = [
                _re.compile(r"sk-ant-[A-Za-z0-9_-]{8,}"),
                _re.compile(r"sk-proj-[A-Za-z0-9_-]{8,}"),
                _re.compile(r"sk-[A-Za-z0-9]{24,}"),
                _re.compile(r'"(access_token|refresh_token|api_key|'
                            r'apiKey|Authorization)"\s*:\s*"[^"]{8,}"'),
                _re.compile(r"(OPENAI_API_KEY|ANTHROPIC_API_KEY)\s*="
                            r"\s*\S{8,}"),
                _re.compile(r"Bearer\s+[A-Za-z0-9._-]{20,}"),
            ]
        for base, _dirs, files in os.walk(bundle_root):
            for name in files:
                try:
                    text = open(os.path.join(base, name),
                                encoding="utf-8").read()
                except (UnicodeDecodeError, OSError):
                    continue
                for pat in _BaseAdapter._CRED_PATTERNS:
                    m = pat.search(text)
                    if m:
                        raise framework.AdapterError(
                            f"credential pattern {pat.pattern!r} found in "
                            f"bundle file {name!r} — custody violation")


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
    ("Luna Max" = that TUPLE, never a concatenated slug). Verified working
    under ChatGPT-subscription auth on Codex CLI 0.144.5 (Phase E). Temp
    CODEX_HOME; skill installed at $CODEX_HOME/skills/implementaudit.
    Fails closed below the minimum CLI version and on any identity or
    effort substitution."""

    name = "codex-cli"
    MIN_CLI = (0, 144, 0)
    REJECTED_SLUGS = ("luna-max", "gpt-5.6-luna-max")

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
             "--sandbox", "workspace-write", "--skip-git-repo-check", "-"],
            requested_model, **kw)
        self.codex_binary = codex_binary
        self.reasoning_effort_requested = reasoning_effort
        self.codex_home = codex_home
        self.auth_mode = None  # recorded (chatgpt-subscription/api); no secrets

    def check_cli_version(self):
        """Fail closed below 0.144.0 (GPT-5.6 access requirement)."""
        proc = subprocess.run([self.codex_binary, "--version"],
                              capture_output=True, text=True)
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
        proc = subprocess.run([self.codex_binary, "login", "status"],
                              capture_output=True, text=True, env=env)
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

    def _select_session(self, repo, not_before=None):
        """Select the session record by BOUND identity: cwd match and
        (optionally) start time — never merely the newest file."""
        import glob as _glob
        if not self.codex_home:
            return None, {}
        best = None
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
            if not_before and p.get("timestamp", "") < not_before:
                continue
            best = f
        if not best:
            return None, {}
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

    def _latest_session_context(self):
        """HOST-OWNED provenance: codex writes session jsonl files under
        CODEX_HOME/sessions with session_meta (cli_version) and turn_context
        (model, effort). These are written by the host process, not the
        model, and are the preferred identity mechanism on 0.144.x."""
        import glob as _glob
        if not self.codex_home:
            return {}
        files = sorted(_glob.glob(os.path.join(
            self.codex_home, "sessions", "**", "*.jsonl"), recursive=True))
        if not files:
            return {}
        ctx = {}
        try:
            for line in open(files[-1], encoding="utf-8"):
                d = json.loads(line)
                p = d.get("payload", {})
                if d.get("type") == "session_meta":
                    ctx["cli_version"] = p.get("cli_version")
                elif d.get("type") == "turn_context":
                    ctx["model"] = p.get("model")
                    ctx["effort"] = p.get("effort")
        except (OSError, json.JSONDecodeError):
            return {}
        return ctx

    def resolve_model(self, out):
        ctx = {}
        if getattr(self, "_current_repo", None):
            _f, ctx = self._select_session(self._current_repo)
        if not ctx:
            ctx = self._latest_session_context()
        if ctx.get("model"):
            return ctx["model"]
        # fallback (mock hosts): "model: <name>" line in either stream
        for line in out.splitlines():
            if line.strip().lower().startswith("model:"):
                return line.split(":", 1)[1].strip()
        return None

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
            "sandbox": ctx.get("sandbox_resolved"),
            "approval": ctx.get("approval_policy"),
            "session_id": ctx.get("session_id"),
            "cli_version": ctx.get("cli_version")}
        if ctx.get("sandbox_resolved") != "workspace-write":
            raise framework.AdapterError(
                f"policy mismatch: requested sandbox workspace-write but "
                f"host resolved {ctx.get('sandbox_resolved')!r} - INVALID")

    def collect_raw_stream(self, repo, outcome):
        f, _ctx = self._select_session(repo)
        if f:
            return open(f, "rb").read()
        return None

    def post_checks(self, out):
        self.check_effort(out)

    def resolve_effort(self, out):
        ctx = {}
        if getattr(self, "_current_repo", None):
            _f, ctx = self._select_session(self._current_repo)
        if not ctx:
            ctx = self._latest_session_context()
        if ctx.get("effort"):
            return ctx["effort"]
        for line in out.splitlines():
            if line.strip().lower().startswith("reasoning effort:"):
                return line.split(":", 1)[1].strip()
        return None

    def check_effort(self, out):
        resolved = self.resolve_effort(out)
        self.reasoning_effort_resolved = resolved
        if resolved is not None and                 resolved != self.reasoning_effort_requested:
            raise framework.AdapterError(
                f"reasoning-effort substitution: requested "
                f"{self.reasoning_effort_requested!r}, resolved "
                f"{resolved!r} — fail closed")
        return resolved

    def parse_events(self, out):
        """Extract ONLY the model's reply section. codex exec transcripts
        echo the user mission (which names the fixture's markers), so
        treating the whole stdout as assistant content would let the echo
        forge marker evidence. The reply lies between the standalone
        'codex' section header and the trailing 'tokens used' line; when
        those headers are absent (mock hosts), fall back to full text."""
        text = (out or "").strip()
        if not text:
            raise ValueError("empty host output")
        lines = text.splitlines()
        starts = [i for i, ln in enumerate(lines) if ln.strip() == "codex"]
        if starts:
            start = starts[-1] + 1
            end = len(lines)
            for j in range(start, len(lines)):
                if lines[j].strip() in ("tokens used", "--------"):
                    end = j
                    break
            reply = chr(10).join(lines[start:end]).strip()
            if not reply:
                raise ValueError("empty codex reply section")
            return [{"role": "assistant", "content": reply}]
        return [{"role": "assistant", "content": text}]


class ClaudeAdapter(_BaseAdapter):
    """Configuration O: Claude Code CLI / Opus High. Temp CLAUDE_CONFIG_DIR;
    payload staged into the fixture repo at .claude/skills/implementaudit
    (project-scoped) with a CLAUDE.md pointer — a LABELED packaging
    difference from Configuration L."""

    name = "claude-cli"

    def __init__(self, requested_model="opus", effort="high",
                 config_dir=None, resolved_expect="claude-opus-4-8", **kw):
        super().__init__(
            ["claude", "-p", "--model", "{model}", "--effort", effort,
             "--output-format", "json"],
            requested_model, **kw)
        self.config_dir = config_dir
        self.resolved_expect = resolved_expect

    def requested_model_canonical(self):
        # "opus" is an alias; the canonical requested identity for the
        # provenance check is the expected resolved name.
        return self.resolved_expect

    def _mission_env(self, repo):
        if not self.config_dir:
            raise framework.AdapterError(
                "ClaudeAdapter requires a fresh temporary CLAUDE_CONFIG_DIR")
        return _clean_env({"CLAUDE_CONFIG_DIR": self.config_dir})

    def stage_payload(self, repo):
        """Project-scoped payload presentation (labeled difference)."""
        if not self.product_checkout:
            raise framework.AdapterError("no product checkout to stage")
        src = os.path.join(self.product_checkout, "skills", "implementaudit")
        dst = os.path.join(repo, ".claude", "skills", "implementaudit")
        shutil.copytree(src, dst)
        with open(os.path.join(repo, "CLAUDE.md"), "x",
                  encoding="utf-8") as fh:
            fh.write("Use the implementaudit skill at "
                     ".claude/skills/implementaudit/SKILL.md for this "
                     "task.\n")
        return framework.payload_hash(dst)

    @staticmethod
    def _extract_json(out):
        """The provenance stream may carry stderr noise before the CLI's
        JSON result; locate the last line that parses as a JSON object."""
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
                "tools": "Read Glob Grep Write Edit",
                "network": "tool-mediated only",
                "writable_roots": ["<fixture-repo cwd>"]}

    def check_policy(self, repo):
        self.policy_resolved = {
            "tools": "Read Glob Grep Write Edit (argv-requested)",
            "note": "claude -p auto-denies permission prompts; writes "
                    "outside cwd require permission and are auto-denied; "
                    "verified empirically by the pre-smoke canary"}

    def collect_raw_stream(self, repo, outcome):
        import glob as _glob
        if not self.config_dir:
            return None
        key = os.path.normcase(repo).replace(os.sep, "-").replace(
            ":", "-").lstrip("-")
        for f in sorted(_glob.glob(os.path.join(
                self.config_dir, "projects", "*", "*.jsonl"))):
            if os.path.normcase(os.path.basename(
                    os.path.dirname(f))).endswith(key[-40:]):
                return open(f, "rb").read()
        files = sorted(_glob.glob(os.path.join(
            self.config_dir, "projects", "*", "*.jsonl")))
        return open(files[-1], "rb").read() if files else None

    def resolve_model(self, out):
        # Claude Code may use an auxiliary model (e.g. haiku) alongside the
        # requested primary. Resolve to the PRIMARY = the modelUsage entry
        # with the most output tokens; the provenance check then confirms it
        # equals the expected model.
        data = self._extract_json(out)
        if not isinstance(data, dict):
            return None
        usage = data.get("modelUsage") or {}
        if not usage:
            return None
        def out_tokens(v):
            return (v or {}).get("outputTokens", 0) if isinstance(v, dict) else 0
        primary = max(usage.items(), key=lambda kv: out_tokens(kv[1]))
        # if tokens are absent, fall back to the expected model when present
        if all(out_tokens(v) == 0 for v in usage.values()):
            return self.resolved_expect if self.resolved_expect in usage else None
        return primary[0]

    def parse_events(self, out):
        data = self._extract_json(out)
        if data is None:
            raise ValueError("no JSON object found in host output")
        result = data.get("result")
        if not isinstance(result, str) or not result.strip():
            raise ValueError("JSON output lacks a result field")
        return [{"role": "assistant", "content": result}]


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
