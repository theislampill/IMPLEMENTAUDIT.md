#!/usr/bin/env python3
"""Closed-contract tests for retained Codex collaboration lifecycle rows."""
from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import pathlib
import tempfile

import hosts
from lib import hostread as official_hostread
import test_native_session_parity as native_fixture


HERE = pathlib.Path(__file__).resolve().parent
def load(name, filename):
    spec = importlib.util.spec_from_file_location(name, HERE / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def collaboration_rows():
    sender = "thread-parent-redacted"
    child = "thread-child-redacted"
    prompt = "Independently review the bounded artifact and report PASS or BLOCK."
    return [
        {"type": "thread.started", "thread_id": sender},
        {"type": "turn.started"},
        {"type": "item.started", "item": {
            "type": "collab_tool_call", "id": "spawn-1", "tool": "spawn_agent",
            "sender_thread_id": sender, "receiver_thread_ids": [],
            "prompt": prompt, "status": "in_progress", "agents_states": {}}},
        {"type": "item.completed", "item": {
            "type": "collab_tool_call", "id": "spawn-1", "tool": "spawn_agent",
            "sender_thread_id": sender, "receiver_thread_ids": [child],
            "prompt": prompt, "status": "completed",
            "agents_states": {child: {"message": None, "status": "pending_init"}}}},
        {"type": "item.started", "item": {
            "type": "collab_tool_call", "id": "wait-1", "tool": "wait",
            "sender_thread_id": sender, "receiver_thread_ids": [child],
            "prompt": None, "status": "in_progress", "agents_states": {}}},
        {"type": "item.completed", "item": {
            "type": "collab_tool_call", "id": "wait-1", "tool": "wait",
            "sender_thread_id": sender, "receiver_thread_ids": [child],
            "prompt": None, "status": "completed",
            "agents_states": {child: {"message": "PASS", "status": "completed"}}}},
        {"type": "item.completed", "item": {
            "type": "agent_message", "id": "message-1", "text": "done"}},
        {"type": "turn.completed", "usage": {
            "input_tokens": 1, "cached_input_tokens": 0,
            "output_tokens": 1, "reasoning_output_tokens": 0}},
    ]


def encoded(rows):
    return "".join(
        json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n"
        for row in rows)


def official_parse(rows):
    raw = encoded(rows)
    binding = official_hostread.derive_codex_binding(raw)
    result = official_hostread.normalize_codex(
        raw, formal=False, binding=binding)
    if result["host_status"] != "PASS":
        raise ValueError(result["host_findings"])
    return result["actions"]


def independent_parse(module, rows):
    actions, _binding = module._parse_codex_actions(encoded(rows).encode("utf-8"))
    return actions


def official_trace(rows=None):
    raw = encoded(rows or collaboration_rows())
    binding = official_hostread.derive_codex_binding(raw)
    trace = official_hostread.normalize_codex(
        raw, formal=False, binding=binding)
    assert trace["host_status"] == "PASS", trace["host_findings"]
    return raw, trace


def formal_codex_profile():
    shell = {
        "logical_path": "/bin/bash", "realpath": "/usr/bin/bash",
        "sha256": "a" * 64, "stat": "dev=1;ino=1;mode=100755;size=1",
    }
    environment = {
        "PATH": "/usr/bin", "LANG": "C.UTF-8", "LC_ALL": "C.UTF-8",
        "BASH_ENV": None, "ENV": None, "SHELL": "/bin/bash",
    }
    executables = {
        name: {
            "kind": "file", "path": f"/usr/bin/{name}",
            "sha256": f"{index + 1:x}" * 64,
            "stat": f"dev=1;ino={index + 2};mode=100755;size=1",
        }
        for index, name in enumerate(sorted(official_hostread.SUPPORTED_READERS))
    }
    probe = {"environment": environment, "shell": shell,
             "executables": executables}
    profile = {
        "schema": "implementaudit-host-read-profile-v2",
        "authority": "mechanically-minted", "host": "codex",
        "repo": {"lexical_root": "/fixture/repo",
                 "real_root": "/fixture/repo", "case_sensitive": True},
        "shell": shell,
        "outer_wrapper": {"argv_prefix": ["/bin/bash", "-lc"],
                          "max_unwrap_layers": 1},
        "environment": environment, "executables": executables,
        "probe_sha256": hashlib.sha256(
            official_hostread._canonical_bytes(probe)).hexdigest(),
    }
    return official_hostread._admit_persisted_profile(profile)


def invalid_cases():
    cases = {}

    def add(label, mutate):
        rows = copy.deepcopy(collaboration_rows())
        mutate(rows)
        cases[label] = rows

    add("unknown-tool", lambda rows: rows[2]["item"].__setitem__("tool", "send_message"))
    add("extra-field", lambda rows: rows[2]["item"].__setitem__("extra", True))
    add("missing-field", lambda rows: rows[2]["item"].pop("agents_states"))
    add("missing-id", lambda rows: rows[2]["item"].__setitem__("id", ""))
    add("bad-start-status", lambda rows: rows[2]["item"].__setitem__("status", "completed"))
    add("bad-completion-status", lambda rows: rows[3]["item"].__setitem__("status", "in_progress"))
    add("orphan-completion", lambda rows: rows.pop(2))
    add("duplicate-action-id", lambda rows: rows[4]["item"].__setitem__("id", "spawn-1"))
    add("incomplete-spawn", lambda rows: rows.__delitem__(slice(3, 6)))
    add("incomplete-wait", lambda rows: rows.pop(5))
    add("completion-tool-change", lambda rows: rows[3]["item"].__setitem__("tool", "wait"))
    add("completion-sender-change", lambda rows: rows[3]["item"].__setitem__("sender_thread_id", "other"))
    add("completion-prompt-change", lambda rows: rows[3]["item"].__setitem__("prompt", "different"))
    add("spawn-start-has-receiver", lambda rows: rows[2]["item"].__setitem__("receiver_thread_ids", ["thread-child-redacted"]))
    add("receiver-mismatch", lambda rows: rows[5]["item"].__setitem__("receiver_thread_ids", ["other-child"]))
    add("wait-orphan-child", lambda rows: rows[4]["item"].__setitem__("receiver_thread_ids", ["other-child"]))
    add("failed-child", lambda rows: rows[5]["item"]["agents_states"]["thread-child-redacted"].__setitem__("status", "failed"))
    add("error-child", lambda rows: rows[5]["item"]["agents_states"]["thread-child-redacted"].__setitem__("status", "error"))
    add("child-message-wrong-type", lambda rows: rows[5]["item"]["agents_states"]["thread-child-redacted"].__setitem__("message", 7))
    add("spawn-child-wrong-state", lambda rows: rows[3]["item"]["agents_states"]["thread-child-redacted"].__setitem__("status", "completed"))
    add("spawn-child-message", lambda rows: rows[3]["item"]["agents_states"]["thread-child-redacted"].__setitem__("message", "premature"))
    add("duplicate-receiver", lambda rows: rows[5]["item"].__setitem__("receiver_thread_ids", ["thread-child-redacted", "thread-child-redacted"]))
    add("sender-as-receiver", lambda rows: rows[5]["item"].__setitem__("receiver_thread_ids", ["thread-parent-redacted"]))
    add("wait-prompt", lambda rows: rows[4]["item"].__setitem__("prompt", "wait now"))
    add("wait-before-spawn", lambda rows: rows.__setitem__(slice(2, 6), rows[4:6] + rows[2:4]))
    add("duplicate-child-spawn", lambda rows: rows.__setitem__(
        slice(4, 4), [
            {**copy.deepcopy(rows[2]), "item": {
                **copy.deepcopy(rows[2]["item"]), "id": "spawn-2"}},
            {**copy.deepcopy(rows[3]), "item": {
                **copy.deepcopy(rows[3]["item"]), "id": "spawn-2"}},
        ]))
    add("second-wait", lambda rows: rows.__setitem__(
        slice(6, 6), [
            {**copy.deepcopy(rows[4]), "item": {
                **copy.deepcopy(rows[4]["item"]), "id": "wait-2"}},
            {**copy.deepcopy(rows[5]), "item": {
                **copy.deepcopy(rows[5]["item"]), "id": "wait-2"}},
        ]))
    return cases


def assert_trace_parity(modules):
    raw, trace = official_trace()
    persisted_trace = json.loads(json.dumps(trace))
    for name, module in modules.items():
        actions, _binding = module._parse_codex_actions(raw.encode("utf-8"))
        for accepted in (trace, persisted_trace):
            module._validate_trace_action_rows(accepted)
            try:
                module._validate_trace_agreement(
                    accepted, actions, [], "codex")
            except module.EvidenceInvalid as exc:
                assert "unbound collaboration descendant evidence" in str(exc)
            else:
                raise AssertionError(
                    f"{name} accepted unbound collaboration evidence")

        def rejected(candidate, agreement=False):
            try:
                module._validate_trace_action_rows(candidate)
                if agreement:
                    module._validate_trace_agreement(
                        candidate, actions, [], "codex")
            except module.EvidenceInvalid:
                return
            raise AssertionError(f"{name} accepted malformed official trace")

        collaboration = [
            index for index, action in enumerate(trace["actions"])
            if action.get("action_type") == "collab_tool_call"]
        assert len(collaboration) == 2
        spawn_index, wait_index = collaboration

        for field in (
                "tool", "sender_thread_id", "prompt", "receiver_thread_ids"):
            malformed = copy.deepcopy(trace)
            malformed["actions"][spawn_index].pop(field)
            rejected(malformed)

        malformed = copy.deepcopy(trace)
        malformed["actions"][spawn_index]["unknown"] = True
        rejected(malformed)
        malformed = copy.deepcopy(trace)
        malformed["actions"][spawn_index]["command"] = "true"
        rejected(malformed)
        malformed = copy.deepcopy(trace)
        malformed["actions"][spawn_index]["effect"] = "read"
        malformed["action_effects"][spawn_index] = "read"
        rejected(malformed)
        malformed = copy.deepcopy(trace)
        malformed["actions"][spawn_index]["classification"] = "content-read"
        rejected(malformed)
        malformed = copy.deepcopy(trace)
        malformed["actions"][spawn_index]["tool"] = "send_message"
        rejected(malformed)
        malformed = copy.deepcopy(trace)
        malformed["actions"][spawn_index]["payload"] = (
            "spawn_agent", "different-sender", "different-prompt")
        rejected(malformed)
        malformed = copy.deepcopy(trace)
        malformed["actions"][wait_index]["prompt"] = "wait now"
        rejected(malformed)
        malformed = copy.deepcopy(trace)
        malformed["actions"][wait_index]["receiver_thread_ids"] = []
        rejected(malformed)
        malformed = copy.deepcopy(trace)
        malformed["actions"][spawn_index]["completion_ordinal"] = \
            malformed["actions"][spawn_index]["invocation_ordinal"]
        rejected(malformed)

        message_index = next(
            index for index, action in enumerate(trace["actions"])
            if action.get("state") == "TERMINAL_SAFE_MESSAGE")
        malformed = copy.deepcopy(trace)
        malformed["actions"][message_index].update({
            "tool": "wait", "sender_thread_id": "smuggled",
            "prompt": None, "receiver_thread_ids": ["smuggled-child"],
        })
        rejected(malformed)

        for field, value in (
                ("tool", "wait"),
                ("sender_thread_id", "different-sender"),
                ("prompt", "different prompt"),
                ("receiver_thread_ids", ["different-child"])):
            altered = copy.deepcopy(trace)
            action = altered["actions"][spawn_index]
            action[field] = value
            action["payload"] = (
                action["tool"], action["sender_thread_id"], action["prompt"])
            if field == "tool":
                action["prompt"] = None
                action["payload"] = (
                    action["tool"], action["sender_thread_id"], None)
            rejected(altered, agreement=True)


def assert_formal_collaboration_fail_closed():
    raw, _trace = official_trace()
    binding = official_hostread.derive_codex_binding(raw)
    formal = official_hostread.normalize_codex(
        raw, profile=formal_codex_profile(), binding=binding, formal=True)
    assert formal["host_status"] == "INVALID", formal
    assert any(
        finding.get("reason") == "unbound collaboration descendant evidence"
        for finding in formal["host_findings"]), formal


def assert_formal_session_custody_fail_closed():
    timestamp = "2026-08-03T00:00:00Z"
    parent_id = "thread-parent-redacted"

    def session(identity, cwd, parent=None, extra=None):
        payload = {"id": identity, "session_id": identity,
                   "cwd": str(cwd), "timestamp": timestamp}
        if parent is not None:
            payload["parent_thread_id"] = parent
        rows = [{"type": "session_meta", "timestamp": timestamp,
                 "payload": payload}]
        rows.extend(extra or [])
        return "".join(json.dumps(row) + "\n" for row in rows)

    cases = {
        "direct-child": [("child", parent_id, [])],
        "recursive-fanout": [
            ("child", parent_id, []), ("grandchild", "child", [])],
        "extra-root": [("other-root", None, [])],
        "orphan": [("child", "missing-parent", [])],
        "cycle": [("child", "grandchild", []),
                  ("grandchild", "child", [])],
        "duplicate-child": [("child", parent_id, []),
                            ("child", parent_id, [])],
        "identity-policy-drift": [("child", parent_id, [{
            "type": "turn_context", "timestamp": timestamp,
            "payload": {"model": "different-model", "effort": "low",
                        "approval_policy": "on-request",
                        "sandbox_policy": {"type": "danger-full-access"}}}])],
        "incomplete-hidden-write": [("child", parent_id, [{
            "type": "response_item", "timestamp": timestamp,
            "payload": {"type": "custom_tool_call", "name": "exec",
                        "status": "in_progress", "call_id": "hidden-write",
                        "input": {"command": "write then restore"}}}])],
    }
    with tempfile.TemporaryDirectory(
            prefix="formal-collab-custody-") as tmp:
        root = pathlib.Path(tmp)
        for label, descendants in cases.items():
            home = root / label / "codex-home"
            repo = root / label / "repo"
            sessions = home / "sessions" / "2026" / "08" / "03"
            repo.mkdir(parents=True)
            sessions.mkdir(parents=True)
            (sessions / "root.jsonl").write_text(
                session(parent_id, repo), encoding="utf-8")
            for index, (identity, parent, extra) in enumerate(descendants):
                (sessions / f"child-{index}.jsonl").write_text(
                    session(identity, repo, parent, extra), encoding="utf-8")
            if label in {"orphan", "extra-root"}:
                expected_error = True
            else:
                expected_error = False
            adapter = hosts.CodexAdapter(codex_home=str(home))
            try:
                retained = adapter._collect_formal_session_stream(
                    str(repo), None, {"thread_id": parent_id})
            except hosts.framework.AdapterError:
                assert expected_error or label in {"cycle"}
            else:
                assert retained is None, (label, retained)


def native_response(payload):
    return {
        "timestamp": "2026-07-30T05:26:12.000Z",
        "type": "response_item",
        "payload": payload,
    }


def assert_native_collaboration_fail_closed(modules):
    positive = {
        "real-exec-spawn-completed": native_response({
            "type": "custom_tool_call", "name": "exec",
            "status": "completed", "call_id": "call-spawn",
            "input": "await tools.multi_agent_v1__spawn_agent({task: 'review'});",
        }),
        "real-exec-wait-in-progress": native_response({
            "type": "custom_tool_call", "name": "exec",
            "status": "in_progress", "call_id": "call-wait",
            "input": "await tools.multi_agent_v1__wait_agent({ids: ['child']})",
        }),
        "direct-modern-alias": native_response({
            "type": "custom_tool_call", "name": "spawn_agent",
            "status": "completed", "call_id": "call-direct", "input": "{}",
        }),
        "direct-modern-send-message": native_response({
            "type": "custom_tool_call", "name": "send_message",
            "status": "completed", "call_id": "call-send", "input": "{}",
        }),
        "direct-unknown-v1-alias": native_response({
            "type": "custom_tool_call", "name": "MULTI_AGENT_V1__FUTURE_TOOL",
            "status": "completed", "call_id": "call-future", "input": "{}",
        }),
        "direct-collaboration-namespace": native_response({
            "type": "function_call", "name": "Collaboration.Send_Input",
            "status": "completed", "call_id": "call-collab", "arguments": "{}",
        }),
        "completion-agent-id": native_response({
            "type": "custom_tool_call_output", "call_id": "call-output",
            "output": [
                {"type": "input_text", "text": "Script completed\n"},
                {"type": "input_text", "text":
                 '{"agent_id":"019fc490-d9e1-7f22-8961-537433aadaf5",'
                 '"nickname":"Dirac"}'},
            ],
        }),
        "completion-status-map": native_response({
            "type": "function_call_output", "call_id": "call-status",
            "output": [
                {"type": "input_text", "text": "Script completed\n"},
                {"type": "input_text", "text":
                 '{"status":{"019fc490-d9e1-7f22-8961-537433aadaf5":'
                 '{"completed":"PASS"}},"timed_out":false}'},
            ],
        }),
        "subagent-notification": native_response({
            "type": "message", "role": "user", "content": [{
                "type": "input_text",
                "text": "<subagent_notification>{}</subagent_notification>",
            }],
        }),
        "casefolded-exec-alias": native_response({
            "type": "custom_tool_call", "name": "EXEC",
            "status": "completed", "call_id": "call-case",
            "input": "TOOLS.MULTI_AGENT_V1__SPAWN_AGENT({})",
        }),
        "truncated-near-collab": native_response({
            "type": "custom_tool_call", "name": "exec",
            "status": "in_progress", "call_id": "call-truncated",
            "input": "await tools.multi_agent_v1__spawn_ag",
        }),
        "whitespace-comment-call": native_response({
            "type": "custom_tool_call", "name": "exec",
            "status": "completed", "call_id": "call-whitespace",
            "input": (
                "await TOOLS /* dispatch */ . "
                "MULTI_AGENT_V1__SPAWN_AGENT /* args */ ({})"),
        }),
        "collaboration-namespace-call": native_response({
            "type": "custom_tool_call", "name": "exec",
            "status": "completed", "call_id": "call-namespace",
            "input": "await tools.collaboration.send_message({})",
        }),
        "collaboration-flat-namespace-call": native_response({
            "type": "custom_tool_call", "name": "exec",
            "status": "completed", "call_id": "call-flat-namespace",
            "input": "await tools.collaboration__send_message({})",
        }),
        "direct-modern-call": native_response({
            "type": "custom_tool_call", "name": "exec",
            "status": "completed", "call_id": "call-modern",
            "input": "await spawn_agent({})",
        }),
        "template-expression-call": native_response({
            "type": "custom_tool_call", "name": "exec",
            "status": "completed", "call_id": "call-template-expression",
            "input": (
                "const result = `prefix ${await "
                "tools.multi_agent_v1__spawn_agent({})} suffix`;"),
        }),
        "static-bracket-call": native_response({
            "type": "custom_tool_call", "name": "exec",
            "status": "completed", "call_id": "call-bracket",
            "input": "await tools['multi_agent_v1__spawn_agent']({})",
        }),
        "escaped-static-bracket-call": native_response({
            "type": "custom_tool_call", "name": "exec",
            "status": "completed", "call_id": "call-bracket-escape",
            "input": r"await tools['multi_agent_v1__spawn_\x61gent']({})",
        }),
        "concatenated-static-bracket-call": native_response({
            "type": "custom_tool_call", "name": "exec",
            "status": "completed", "call_id": "call-bracket-concat",
            "input": (
                "await tools['multi_agent_v1__' + 'spawn_agent']({})"),
        }),
        "nested-static-bracket-call": native_response({
            "type": "custom_tool_call", "name": "exec",
            "status": "completed", "call_id": "call-bracket-nested",
            "input": "await tools['collaboration']['send_message']({})",
        }),
        "truncated-known-call": native_response({
            "type": "custom_tool_call", "name": "exec",
            "status": "in_progress", "call_id": "call-truncated-call",
            "input": "await tools.multi_agent_v1__spawn_agent(",
        }),
    }
    negative = {
        "ordinary-exec": native_response({
            "type": "custom_tool_call", "name": "exec",
            "status": "completed", "call_id": "call-shell",
            "input": "await tools.shell_command({command: 'git status'})",
        }),
        "inert-tool-description-output": native_response({
            "type": "custom_tool_call_output", "call_id": "call-list",
            "output": "Available: tools.multi_agent_v1__spawn_agent and spawn_agent",
        }),
        "ordinary-agent-word": native_response({
            "type": "message", "role": "assistant", "content": [{
                "type": "output_text",
                "text": "The agent-oriented design uses Unicode: Luna Λ.",
            }],
        }),
        "exact-reviewer-source-search": native_response({
            "type": "custom_tool_call", "name": "exec",
            "status": "completed", "call_id": "call-reviewer-red",
            "input": (
                "const r = await tools.shell_command({command: "
                "\"rg -n 'tools.multi_agent_v1__spawn_agent' eval\"}); "
                "text(r);"),
        }),
        "single-quoted-literal": native_response({
            "type": "custom_tool_call", "name": "exec",
            "status": "completed", "call_id": "call-single-literal",
            "input": "const value = 'tools.multi_agent_v1__spawn_agent({})';",
        }),
        "double-quoted-escaped-literal": native_response({
            "type": "custom_tool_call", "name": "exec",
            "status": "completed", "call_id": "call-double-literal",
            "input": (
                'const value = "quoted \\\"tools.multi_agent_v1__spawn_agent'
                '({})\\\" text";'),
        }),
        "template-raw-literal": native_response({
            "type": "custom_tool_call", "name": "exec",
            "status": "completed", "call_id": "call-template-raw",
            "input": (
                "const value = `docs: tools.multi_agent_v1__spawn_agent({})`;"),
        }),
        "line-comment": native_response({
            "type": "custom_tool_call", "name": "exec",
            "status": "completed", "call_id": "call-line-comment",
            "input": (
                "// tools.multi_agent_v1__spawn_agent({})\n"
                "await tools.shell_command({command: 'git status'});"),
        }),
        "block-comment": native_response({
            "type": "custom_tool_call", "name": "exec",
            "status": "completed", "call_id": "call-block-comment",
            "input": (
                "/* tools.collaboration.send_message({}) */ "
                "await tools.shell_command({command: 'git status'});"),
        }),
        "regex-literal": native_response({
            "type": "custom_tool_call", "name": "exec",
            "status": "completed", "call_id": "call-regex",
            "input": (
                r"const pattern = /tools\.multi_agent_v1__spawn_agent\(/gi; "
                "text(pattern);"),
        }),
        "regexp-string": native_response({
            "type": "custom_tool_call", "name": "exec",
            "status": "completed", "call_id": "call-regexp-string",
            "input": (
                "const pattern = new RegExp("
                "'tools\\.multi_agent_v1__spawn_agent');"),
        }),
        "object-string-value": native_response({
            "type": "custom_tool_call", "name": "exec",
            "status": "completed", "call_id": "call-object-value",
            "input": (
                "const fixture = {source: "
                "'tools.multi_agent_v1__spawn_agent({})'}; text(fixture);"),
        }),
        "known-property-reference-only": native_response({
            "type": "custom_tool_call", "name": "exec",
            "status": "completed", "call_id": "call-property-reference",
            "input": "const reference = tools.multi_agent_v1__spawn_agent;",
        }),
        "known-bracket-reference-only": native_response({
            "type": "custom_tool_call", "name": "exec",
            "status": "completed", "call_id": "call-bracket-reference",
            "input": "const reference = tools['multi_agent_v1__spawn_agent'];",
        }),
    }

    for label, response in negative.items():
        rows = native_fixture._base_rows() + [response]
        raw = native_fixture._raw(rows)
        assert official_hostread.codex_native_collaboration_status(raw) == \
            "ABSENT", label
        observed = native_fixture._statuses(rows)
        assert observed == ("VALID", "VALID", "VALID"), (label, observed)
        for module in modules.values():
            assert not module._codex_native_collaboration_present(rows), label

    for label, response in positive.items():
        rows = native_fixture._base_rows() + [response]
        raw = native_fixture._raw(rows)
        assert official_hostread.codex_native_collaboration_status(raw) == \
            "PRESENT", label
        observed = native_fixture._statuses(rows)
        assert observed == ("INVALID", "INVALID", "INVALID"), (label, observed)
        for module in modules.values():
            assert module._codex_native_collaboration_present(rows), label

    configured_only = native_fixture._base_rows()
    configured_only[1]["payload"]["collaboration_mode"] = "default"
    configured_only[1]["payload"]["multi_agent_version"] = "v1"
    assert official_hostread.codex_native_collaboration_status(
        native_fixture._raw(configured_only)) == "ABSENT"
    assert native_fixture._statuses(configured_only) == \
        ("VALID", "VALID", "VALID")

    truncated = native_fixture._raw(native_fixture._base_rows())[:-2]
    assert official_hostread.codex_native_collaboration_status(truncated) == \
        "INVALID"

    rows = native_fixture._base_rows() + [positive["real-exec-spawn-completed"]]
    session = native_fixture._raw(rows)
    for label, add_out_of_window_child in (
            ("vanished-child", False), ("out-of-window-child", True)):
        with tempfile.TemporaryDirectory(
                prefix=f"native-collab-{label}-") as tmp:
            home = pathlib.Path(tmp)
            session_dir = home / "sessions" / "2026" / "07" / "30"
            session_dir.mkdir(parents=True)
            (session_dir / "root.jsonl").write_text(
                session, encoding="utf-8")
            if add_out_of_window_child:
                child = {
                    "timestamp": "2026-07-30T05:26:09.000Z",
                    "type": "session_meta",
                    "payload": {
                        "id": "child-out-of-window",
                        "session_id": "child-out-of-window",
                        "parent_thread_id": native_fixture.THREAD,
                        "timestamp": "2026-07-30T05:26:09.000Z",
                        "cwd": native_fixture.ROOT,
                    },
                }
                (session_dir / "child.jsonl").write_text(
                    json.dumps(child) + "\n", encoding="utf-8")
            adapter = hosts.CodexAdapter(codex_home=str(home))
            adapter._not_before = native_fixture.START
            retained = adapter._collect_formal_session_stream(
                native_fixture.ROOT, None,
                {"thread_id": native_fixture.THREAD})
            assert retained is None, label


def main():
    modules = {
        "candidate": load(
            "candidate_matrix_rederive", "candidate_matrix_rederive.py"),
        "b3v4": load("b3v4_rederive", "b3v4_rederive.py"),
    }
    consumers = {
        "official": official_parse,
        "candidate": lambda rows: independent_parse(modules["candidate"], rows),
        "b3v4": lambda rows: independent_parse(modules["b3v4"], rows),
    }
    for name, parse in consumers.items():
        actions = parse(collaboration_rows())
        collaboration = [
            action for action in actions
            if action.get("action_type") == "collab_tool_call"]
        assert len(collaboration) == 2, (name, actions)
        assert all(action["state"] == "COMPLETED" for action in collaboration)
        assert all(action["effect"] == "safe-other" for action in collaboration)
        assert all(action["classification"] == "not-content-read"
                   for action in collaboration)
        for label, rows in invalid_cases().items():
            try:
                parse(rows)
            except Exception:
                pass
            else:
                raise AssertionError(f"{name} accepted malformed {label}")
    assert_trace_parity(modules)
    assert_formal_collaboration_fail_closed()
    assert_formal_session_custody_fail_closed()
    assert_native_collaboration_fail_closed(modules)
    print("CODEX_COLLAB_LIFECYCLE=PASS")


if __name__ == "__main__":
    main()
