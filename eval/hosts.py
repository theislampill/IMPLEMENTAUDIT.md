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
                    _test_gate=None):
        """Everything around exactly one model call. PRODUCTION PATH requires
        the owner approval token (fail-closed; unconditional CI refusal).
        `_test_gate` exists ONLY so the mock-driven CI tests can exercise the
        surrounding machinery with a fake host process — it is a code-level
        parameter (not an environment switch), so no environment state can
        disable the production gate."""
        (framework.require_owner_approval if _test_gate is None
         else _test_gate)()
        self.preflight()
        payload_before = (framework.payload_hash(self.product_checkout)
                          if self.product_checkout else None)
        repo = framework.seed_fixture_repo(fixture_id, work_root)
        if self.product_checkout:
            self.stage_payload(repo)
        before = reposnapshot.snapshot(repo)
        fixture_path = os.path.join(HERE, "fixtures", fixture_id,
                                    "fixture.json")
        mission = json.load(open(fixture_path, encoding="utf-8"))["mission"]
        argv = [a.replace("{model}", self.requested_model)
                for a in self.host_argv_template]
        outcome = _spawn_once(argv, self._mission_env(repo),
                              self.host_cwd or repo, self.timeout_s,
                              stdin_text=mission)
        if isinstance(outcome, HostRunResult):
            return outcome  # ERROR class, preserved, no retry
        try:
            events = self.parse_events(outcome.stdout)
        except ValueError as exc:
            return HostRunResult("invalid",
                                 f"malformed structured output: {exc}")
        resolved = self.check_provenance(outcome.stdout)
        self.post_checks(outcome.stdout)
        if payload_before is not None:
            payload_after = framework.payload_hash(self.product_checkout)
            if payload_after != payload_before:
                raise framework.AdapterError(
                    "canonical payload checkout was modified during the "
                    "mission — aborting; evidence preserved")
        after = reposnapshot.snapshot(repo)
        cmp_ = reposnapshot.compare_with_repo(repo, before, after)
        fields = self.identity_fields(run_id, fixture_id, resolved)
        run_root = framework.custody.resolve_and_create_output_dir(
            custody_root, run_id)
        bundle_root = os.path.join(run_root, "bundle")
        ev_objs = [bundlelib.make_event(run_id, fixture_id, i + 1,
                                        e["role"], e["content"],
                                        kind=e.get("kind", "message"))
                   for i, e in enumerate(events)]
        fixture_bytes = open(fixture_path, "rb").read()
        manifest = bundlelib.write_bundle(
            bundle_root, fields, ev_objs, fixture_bytes,
            ("MISSION:\n" + mission).encode(),
            repo_before=before, repo_after=after, repo_comparison=cmp_)
        self.scan_for_leaks(bundle_root)
        return HostRunResult("ok", bundle_root, raw_events=events,
                             resolved_model=resolved)

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

    def scan_for_leaks(self, bundle_root):
        """Credential nonretention: bundles must not contain auth material."""
        sentinels = ("sk-", "OPENAI_API_KEY", "ANTHROPIC_API_KEY",
                     "access_token", "refresh_token")
        for base, _dirs, files in os.walk(bundle_root):
            for name in files:
                try:
                    text = open(os.path.join(base, name),
                                encoding="utf-8").read()
                except (UnicodeDecodeError, OSError):
                    continue
                for s in sentinels:
                    if s in text:
                        raise framework.AdapterError(
                            f"credential sentinel {s!r} found in bundle "
                            f"file {name!r} — custody violation; aborting")


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

    def resolve_model(self, out):
        # Codex session headers print "model: <name>"; absence = no proof.
        for line in out.splitlines():
            if line.strip().lower().startswith("model:"):
                return line.split(":", 1)[1].strip()
        return None

    def preflight(self):
        self.check_cli_version()
        self.check_auth_mode()

    def post_checks(self, out):
        self.check_effort(out)

    def resolve_effort(self, out):
        # Session headers print "reasoning effort: <level>" when exposed.
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
        # codex exec plain output: treat the final assistant text as one
        # assistant event. Structured event capture is a follow-up once a
        # working selector exists to test against.
        text = out.strip()
        if not text:
            raise ValueError("empty host output")
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

    def resolve_model(self, out):
        try:
            data = json.loads(out)
        except json.JSONDecodeError:
            return None
        usage = data.get("modelUsage") or {}
        models = [m for m in usage.keys()]
        return models[0] if len(models) == 1 else None

    def parse_events(self, out):
        try:
            data = json.loads(out)
        except json.JSONDecodeError as exc:
            raise ValueError(f"not JSON: {exc}")
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
