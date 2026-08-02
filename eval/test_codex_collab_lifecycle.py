#!/usr/bin/env python3
"""Closed-contract tests for retained Codex collaboration lifecycle rows."""
from __future__ import annotations

import copy
import importlib.util
import json
import pathlib

from lib import hostread as official_hostread


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


def main():
    consumers = {
        "official": official_parse,
        "candidate": lambda rows: independent_parse(
            load("candidate_matrix_rederive", "candidate_matrix_rederive.py"), rows),
        "b3v4": lambda rows: independent_parse(
            load("b3v4_rederive", "b3v4_rederive.py"), rows),
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
    print("CODEX_COLLAB_LIFECYCLE=PASS")


if __name__ == "__main__":
    main()
