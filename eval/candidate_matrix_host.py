#!/usr/bin/env python3
"""Matrix-only host policy layered on the shared Codex adapter.

The shared lifecycle stays unchanged. Matrix-specific policy materializes
prompt-bound fixture state and quarantines only files that actually contain a
credential shape, preserving non-sensitive create-once identity records.
"""
from __future__ import annotations

import json
import os
import pathlib
import shutil

import candidate_matrix_fixture_setup as fixture_setup
import hosts


_CAPTURE_ANCHOR = ".git/implementaudit-matrix-capture-anchor"
_CAPTURE_ANCHOR_BYTES = b"matrix-formal-v2-native-session\n"


def _read_bytes(root, name):
    return pathlib.Path(root, name).read_bytes()


def _read_object(root, name):
    value = json.loads(_read_bytes(root, name))
    if not isinstance(value, dict):
        raise ValueError(f"{name} is not an object")
    return value


def validate_universal_capture(root, fixture_bytes, expected_run_id):
    """Replay the matrix universal formal-v2/native-session profile.

    The shared host-read path deliberately requires at least one product
    path-order property. Matrix cells instead require the same custody and
    native-session evidence for every cell, including cells with no path
    property. This matrix-only replay admits exactly an empty property list;
    it does not weaken host, session, identity, or hash validation.
    """
    try:
        required = set(hosts.hostread._CAPTURE_FILES) | {
            "host-read-manifest.json", "run-intent.json",
            "process-started.json"}
        if any(not pathlib.Path(root, name).is_file() for name in required):
            return False
        actual = {name: hosts.bundlelib._sha256_bytes(_read_bytes(root, name))
                  for name in hosts.hostread._CAPTURE_FILES}
        manifest = _read_object(root, "host-read-manifest.json")
        if manifest != {
                "schema": "implementaudit-host-read-manifest-v1",
                "files": actual}:
            return False
        terminal = _read_object(root, "host-read-terminal.json")
        if set(terminal) != {
                "schema", "hashes", "post_probe_sha256",
                "profile_post_status", "binding", "actual_tools",
                "normalized_host_status", "host_terminal_kind",
                "session_bound", "session_status"} or \
                terminal.get("hashes") != {
                name: actual[name]
                for name in hosts.hostread._CAPTURE_FILES[:-1]}:
            return False
        if (terminal.get("schema") !=
                "implementaudit-host-read-terminal-v1" or
                terminal.get("host_terminal_kind") != "ok" or
                terminal.get("normalized_host_status") != "PASS" or
                terminal.get("profile_post_status") != "PASS" or
                terminal.get("session_status") != "VALID" or
                terminal.get("session_bound") is not True):
            return False
        pre_spawn = _read_object(root, "host-read-pre-spawn.json")
        if pre_spawn != {
                "schema": "implementaudit-host-read-pre-spawn-v1",
                "created_before_spawn": True,
                "profile_sha256": actual["host-read-profile.json"],
                "preimages_sha256": actual["host-read-preimages.json"],
                "fixture_sha256": actual["host-read-fixture.raw"],
                "replay_spec_sha256":
                actual["host-read-replay-spec.json"]}:
            return False
        if _read_bytes(root, "host-read-fixture.raw") != fixture_bytes:
            return False
        intent = _read_object(root, "run-intent.json")
        process = _read_object(root, "process-started.json")
        replay = _read_object(root, "host-read-replay-spec.json")
        fixture = json.loads(fixture_bytes)
        if (not isinstance(fixture, dict) or
                intent.get("schema") != "implementaudit-run-intent-v1" or
                intent.get("run_id") != expected_run_id or
                intent.get("fixture_id") != fixture.get("id") or
                process.get("run_id") != expected_run_id or
                intent.get("fixture_sha256") !=
                hosts.bundlelib._sha256_bytes(fixture_bytes) or
                process.get("host_read_pre_spawn_sha256") !=
                actual["host-read-pre-spawn.json"] or
                replay != {
                    "schema": "implementaudit-host-read-replay-spec-v1",
                    "mode": "formal-v2", "host": "codex", "checks": [],
                    "requested_tools": [],
                    "fixture_sha256":
                    hosts.bundlelib._sha256_bytes(fixture_bytes),
                    "run_intent_sha256":
                    hosts.bundlelib._sha256_bytes(
                        _read_bytes(root, "run-intent.json")),
                    "parser_sha256": hosts.hostread._file_sha256(
                        os.path.abspath(hosts.hostread.__file__))}):
            return False
        preimages = _read_object(root, "host-read-preimages.json")
        target = (preimages.get("targets") or {}).get(_CAPTURE_ANCHOR)
        if (set((preimages.get("targets") or {})) != {_CAPTURE_ANCHOR} or
                not isinstance(target, dict) or
                target.get("sha256") != hosts.bundlelib._sha256_bytes(
                    _CAPTURE_ANCHOR_BYTES) or
                hosts.hostread.validate_preimages(preimages).get("status") !=
                "PASS"):
            return False
        profile = _read_object(root, "host-read-profile.json")
        post = _read_object(root, "host-read-post-probe.json")
        admitted = hosts.hostread._admit_persisted_profile(
            profile, expected_host="codex")
        if (hosts.hostread.validate_profile(
                admitted, post_probe=post, formal=True).get("host_status") !=
                "PASS" or terminal.get("post_probe_sha256") !=
                hosts.bundlelib._sha256_bytes(
                    hosts.hostread._canonical_bytes(post))):
            return False
        raw_stdout = _read_bytes(root, "host-stdout.raw").decode("utf-8")
        raw_session = _read_bytes(root, "host-session.raw")
        if not raw_stdout or not raw_session:
            return False
        binding = terminal.get("binding")
        derived = hosts.hostread.derive_codex_binding(raw_stdout)
        if (not isinstance(binding, dict) or not derived or
                any(binding.get(key) != value
                    for key, value in derived.items()) or
                not isinstance(binding.get("native_turn_id"), str)):
            return False
        normalized = hosts.hostread.normalize_codex(
            raw_stdout, profile=admitted, binding=binding, formal=True)
        retained_trace = _read_object(root, "host-tool-trace.json")
        if (normalized.get("host_status") != "PASS" or
                hosts.hostread.corroborate_session(
                    raw_stdout, raw_session, "codex", binding, normalized,
                    profile=admitted, process_started=process) != "VALID" or
                hosts.hostread._canonical_bytes(retained_trace) !=
                hosts.hostread._canonical_bytes(normalized) or
                _read_object(root, "host-read-matrix.json") != {
                    "schema": "implementaudit-host-read-matrix-v1",
                    "raw_transforms": {
                        "host-stdout.raw":
                        "codex-typed-action-normalizer-v2",
                        "host-session.raw":
                        "lineage-corroboration-only"},
                    "specs": {}}):
            return False
        return terminal.get("actual_tools") == \
            list(normalized.get("observed_tools") or [])
    except (OSError, UnicodeError, ValueError, TypeError,
            json.JSONDecodeError):
        return False


class MatrixCodexAdapter(hosts.CodexAdapter):
    universal_formal_capture = "formal-v2-native-session"

    @staticmethod
    def _structured_rows(raw):
        rows = []
        for line in (raw or "").splitlines():
            try:
                value = json.loads(line)
            except (TypeError, json.JSONDecodeError):
                continue
            if not isinstance(value, dict):
                continue
            candidates = (value, value.get("msg"), value.get("payload"))
            rows.extend(item for item in candidates if isinstance(item, dict))
        return rows

    @classmethod
    def _mark_final_answer(cls, events, raw):
        """Retain progress but mark only one terminally bound final answer."""
        rows = cls._structured_rows(raw)
        finals = [
            row["message"] for row in rows
            if row.get("type") == "agent_message" and
            row.get("phase") == "final_answer" and
            isinstance(row.get("message"), str)]
        completions = [
            row["last_agent_message"] for row in rows
            if row.get("type") == "task_complete" and
            isinstance(row.get("last_agent_message"), str)]
        result = [dict(event, kind="message") for event in events]
        if (len(finals) != 1 or len(completions) != 1 or
                finals[0] != completions[0]):
            return result
        matches = [index for index, event in enumerate(result)
                   if event.get("role") == "assistant" and
                   event.get("content") == finals[0]]
        if len(matches) != 1:
            return result
        result[matches[0]]["kind"] = "marker"
        return result

    def run_mission(self, fixture_id, custody_root, run_id, work_root,
                    *args, **kwargs):
        self._matrix_fixture_id = fixture_id
        self._matrix_custody_root = custody_root
        self._matrix_run_id = run_id
        return super().run_mission(
            fixture_id, custody_root, run_id, work_root, *args, **kwargs)

    def parse_events(self, out):
        return self._mark_final_answer(super().parse_events(out), out)

    def reconcile_events(self, events, repo, outcome):
        reconciled = super().reconcile_events(events, repo, outcome)
        path, _context = self._select_session(repo)
        if not path:
            return reconciled
        try:
            raw = pathlib.Path(path).read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            return [dict(event, kind="message") for event in reconciled]
        return self._mark_final_answer(reconciled, raw)

    def stage_payload(self, repo):
        digest = super().stage_payload(repo)
        fixture_id = getattr(self, "_matrix_fixture_id", None)
        fixture = json.load(open(
            os.path.join(hosts.HERE, "fixtures", fixture_id, "fixture.json"),
            encoding="utf-8"))
        fixture_setup.prepare_fixture(
            fixture_id, pathlib.Path(repo), pathlib.Path(self.product_checkout),
            fixture.get("matrix_precondition"))
        if self.formal:
            self._prepare_universal_capture(repo, fixture_id)
        return digest

    def _prepare_universal_capture(self, repo, fixture_id):
        run_root = pathlib.Path(
            self._matrix_custody_root, self._matrix_run_id)
        fixture_path = pathlib.Path(
            hosts.HERE, "fixtures", fixture_id, "fixture.json")
        fixture_bytes = fixture_path.read_bytes()
        intent_path = run_root / "run-intent.json"
        anchor = pathlib.Path(repo, *_CAPTURE_ANCHOR.split("/"))
        anchor.parent.mkdir(parents=True, exist_ok=True)
        with open(anchor, "xb") as stream:
            stream.write(_CAPTURE_ANCHOR_BYTES)
        try:
            preimages = hosts.hostread.capture_preimages(
                repo, [_CAPTURE_ANCHOR])
            env = self._mission_env(repo)
            shell = shutil.which("bash", path=env.get("PATH"))
            if not shell:
                raise ValueError("no internally resolved POSIX bash")
            profile = hosts.hostread.mint_codex_profile(
                repo, shell, env=env, writable_roots=(repo,))
            replay = hosts.hostread.make_replay_spec(
                "codex", [], requested_tools=(),
                fixture_sha256=hosts.bundlelib._sha256_bytes(fixture_bytes),
                run_intent_sha256=hosts.bundlelib._sha256_bytes(
                    intent_path.read_bytes()))
            hosts.hostread._write_new_json(
                run_root / "host-read-profile.json", profile)
            hosts.hostread._write_new_json(
                run_root / "host-read-preimages.json", preimages)
            hosts.hostread._write_new(
                run_root / "host-read-fixture.raw", fixture_bytes)
            hosts.hostread._write_new_json(
                run_root / "host-read-replay-spec.json", replay)
            pre_spawn = {
                "schema": "implementaudit-host-read-pre-spawn-v1",
                "created_before_spawn": True,
                "profile_sha256": hosts.hostread._file_sha256(
                    run_root / "host-read-profile.json"),
                "preimages_sha256": hosts.hostread._file_sha256(
                    run_root / "host-read-preimages.json"),
                "fixture_sha256": hosts.hostread._file_sha256(
                    run_root / "host-read-fixture.raw"),
                "replay_spec_sha256": hosts.hostread._file_sha256(
                    run_root / "host-read-replay-spec.json")}
            hosts.hostread._write_new_json(
                run_root / "host-read-pre-spawn.json", pre_spawn)
        except (OSError, ValueError, FileExistsError) as exc:
            raise hosts.framework.AdapterError(
                f"matrix formal-v2 pre-spawn custody failed: {exc} — "
                "INVALID")
        self._formal_host_read = {
            "profile": profile, "preimages": preimages,
            "runtime": {"shell": shell, "env": env},
            "replay_spec": replay, "run_root": str(run_root)}
        for name in ("host-read-profile.json", "host-read-preimages.json",
                     "host-read-fixture.raw", "host-read-replay-spec.json",
                     "host-read-pre-spawn.json"):
            self._custody_hashes[name] = hosts.bundlelib._sha256_bytes(
                _read_bytes(run_root, name))

    def _attempt_finalize_formal_host_read(
            self, fx, repo, outcome, run_root, host_terminal_kind):
        shared_result = super()._attempt_finalize_formal_host_read(
            fx, repo, outcome, run_root, host_terminal_kind)
        if shared_result:
            return True
        fixture_bytes = pathlib.Path(
            hosts.HERE, "fixtures", fx["id"], "fixture.json").read_bytes()
        valid = validate_universal_capture(
            run_root, fixture_bytes, self._matrix_run_id)
        if valid:
            self._formal_host_read_results = {}
            self._formal_host_read_host_status = "PASS"
        return valid

    def _quarantine_if_leak(self, root, quarantine_name, only=None):
        if only is None:
            return super()._quarantine_if_leak(
                root, quarantine_name, only=only)
        hits = []
        for name in only:
            path = os.path.join(root, name)
            if not os.path.isfile(path):
                continue
            try:
                text = open(path, encoding="utf-8").read()
            except (UnicodeDecodeError, OSError):
                continue
            pattern = next(
                (item for item in self._cred_patterns()
                 if item.search(text)), None)
            if pattern is not None:
                hits.append((pattern.pattern, name))
        if not hits:
            return None
        qdir = os.path.join(root, quarantine_name)
        os.makedirs(qdir, exist_ok=True)
        for _pattern, name in hits:
            source = os.path.join(root, name)
            destination = os.path.join(qdir, name)
            if os.path.lexists(destination):
                raise hosts.framework.AdapterError(
                    "credential quarantine destination already exists")
            os.replace(source, destination)
        return hits[0]
