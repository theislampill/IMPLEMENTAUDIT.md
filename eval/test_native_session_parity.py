#!/usr/bin/env python3
"""Cross-path contract for one retained Codex native-session byte stream."""
from __future__ import annotations

import copy
import json
import os
import sys


HERE = os.path.dirname(os.path.abspath(__file__))
LIB = os.path.join(HERE, "lib")
if LIB not in sys.path:
    sys.path.insert(0, LIB)

import b3v4_rederive
import candidate_matrix_rederive
import hostread


THREAD = "019f77dc-c42c-7511-b77e-dea799279bc6"
TURN = "019f77dc-c4a6-75b3-ab18-130c2efdb677"
ROOT = "/fixture/repo"
MODEL = "gpt-5.6-luna"
START = "2026-07-30T05:26:10.000Z"
BINDING = {
    "thread_id": THREAD,
    "stdout_turn_ordinal": 1,
    "native_turn_id": TURN,
}
STDOUT_BINDING = {
    "thread_id": THREAD,
    "stdout_turn_ordinal": 1,
}
RAW_STDOUT = "\n".join((
    json.dumps({"type": "thread.started", "thread_id": THREAD}),
    json.dumps({"type": "turn.started"}),
    json.dumps({"type": "turn.completed"}),
)) + "\n"
PROFILE = {
    "repo": {
        "lexical_root": ROOT,
        "real_root": ROOT,
        "case_sensitive": True,
    },
}
TRACE = {"actions": []}
PROCESS = {
    "started_at": START,
    "cwd": ROOT,
    "requested_model": MODEL,
}


def _base_rows():
    return [
        {
            "timestamp": "2026-07-30T05:26:11.065Z",
            "type": "session_meta",
            "payload": {
                "session_id": THREAD,
                "id": THREAD,
                "timestamp": "2026-07-30T05:26:10.990Z",
                "cwd": ROOT,
            },
        },
        {
            "timestamp": "2026-07-30T05:26:10.568Z",
            "type": "turn_context",
            "payload": {
                "turn_id": TURN,
                "cwd": ROOT,
                "model": MODEL,
            },
        },
    ]


def _raw(rows):
    return "\n".join(
        json.dumps(row, sort_keys=True, separators=(",", ":"))
        for row in rows) + "\n"


def _official_status(rows, process=None):
    return hostread.corroborate_session(
        RAW_STDOUT, _raw(rows), "codex", BINDING, TRACE,
        profile=PROFILE, process_started=process or PROCESS)


def _independent_status(module, rows, process=None):
    try:
        module._validate_native_session(
            RAW_STDOUT.encode("utf-8"), _raw(rows).encode("utf-8"),
            "codex", BINDING, STDOUT_BINDING, [], PROFILE,
            process or PROCESS)
    except module.EvidenceInvalid:
        return "INVALID"
    return "VALID"


def _statuses(rows, process=None):
    return (
        _official_status(rows, process),
        _independent_status(b3v4_rederive, rows, process),
        _independent_status(candidate_matrix_rederive, rows, process),
    )


def _case(name, expected, mutate):
    rows = _base_rows()
    process = copy.deepcopy(PROCESS)
    mutate(rows, process)
    observed = _statuses(rows, process)
    if observed != (expected,) * 3:
        raise AssertionError(
            f"{name}: expected {(expected,) * 3!r}, got {observed!r}")
    print(f"  [OK] {name}: {observed}")


def _noop(_rows, _process):
    pass


def main():
    official_contract = {
        key: (set(value[0]), set(value[1]))
        for key, value in hostread.CODEX_NATIVE_PAYLOAD_FIELDS.items()
    }
    if not (
        official_contract == b3v4_rederive.CODEX_NATIVE_PAYLOAD_FIELDS ==
        candidate_matrix_rederive.CODEX_NATIVE_PAYLOAD_FIELDS and
        hostread.CODEX_SESSION_START_WINDOW_SECONDS ==
        b3v4_rederive.CODEX_SESSION_START_WINDOW_SECONDS ==
        candidate_matrix_rederive.CODEX_SESSION_START_WINDOW_SECONDS == 10
    ):
        raise AssertionError("three-path native-session contract drift")
    cases = [
        ("V18-identical-inversion", "VALID", _noop),
        ("exact-process-start", "VALID",
         lambda rows, _process: (
             rows[0].update(timestamp=START),
             rows[0]["payload"].update(timestamp=START),
             rows[1].update(timestamp=START))),
        ("observed-9.242-seconds", "VALID",
         lambda rows, _process: rows[1].update(
             timestamp="2026-07-30T05:26:19.242Z")),
        ("declared-10-second-ceiling", "VALID",
         lambda rows, _process: (
             rows[0].update(timestamp="2026-07-30T05:26:20.000Z"),
             rows[0]["payload"].update(
                 timestamp="2026-07-30T05:26:19.999Z"))),
        ("timezone-equivalent", "VALID",
         lambda rows, _process: (
             rows[0].update(timestamp="2026-07-30T01:26:11.065-04:00"),
             rows[0]["payload"].update(
                 timestamp="2026-07-30T01:26:10.990-04:00"),
             rows[1].update(timestamp="2026-07-30T01:26:10.568-04:00"))),
        ("world-state-current-producer-row", "VALID",
         lambda rows, _process: rows.insert(1, {
             "timestamp": "2026-07-30T05:26:10.500Z",
             "type": "world_state",
             "payload": {"state": {}, "full": True},
         })),
        ("unsupported-row", "INVALID",
         lambda rows, _process: rows.insert(1, {
             "timestamp": "2026-07-30T05:26:10.500Z",
             "type": "unsupported_native_row",
             "payload": {},
         })),
        ("turn-over-ceiling", "INVALID",
         lambda rows, _process: rows[1].update(
             timestamp="2026-07-30T05:26:20.001Z")),
        ("meta-over-ceiling", "INVALID",
         lambda rows, _process: rows[0].update(
             timestamp="2026-07-30T05:26:20.001Z")),
        ("payload-after-meta-top", "INVALID",
         lambda rows, _process: rows[0]["payload"].update(
             timestamp="2026-07-30T05:26:11.066Z")),
        ("turn-pre-spawn", "INVALID",
         lambda rows, _process: rows[1].update(
             timestamp="2026-07-30T05:26:09.999Z")),
        ("naive-timestamp", "INVALID",
         lambda rows, _process: rows[1].update(
             timestamp="2026-07-30T05:26:10.568")),
        ("malformed-timestamp", "INVALID",
         lambda rows, _process: rows[1].update(timestamp="not-a-time")),
        ("reordered-meta-turn", "INVALID",
         lambda rows, _process: rows.reverse()),
        ("duplicate-meta", "INVALID",
         lambda rows, _process: rows.insert(1, copy.deepcopy(rows[0]))),
        ("duplicate-turn", "INVALID",
         lambda rows, _process: rows.append(copy.deepcopy(rows[1]))),
        ("missing-meta", "INVALID",
         lambda rows, _process: rows.pop(0)),
        ("missing-turn", "INVALID",
         lambda rows, _process: rows.pop(1)),
        ("forged-thread-in-envelope", "INVALID",
         lambda rows, _process: (
             rows[0]["payload"].update(id="earlier-attempt",
                                       session_id="earlier-attempt"))),
        ("forged-turn-in-envelope", "INVALID",
         lambda rows, _process: rows[1]["payload"].update(
             turn_id="earlier-attempt")),
        ("forged-cwd-in-envelope", "INVALID",
         lambda rows, _process: rows[1]["payload"].update(cwd="/other")),
        ("forged-model-in-envelope", "INVALID",
         lambda rows, _process: rows[1]["payload"].update(
             model="gpt-5.6-terra")),
        ("forged-process-cwd-in-envelope", "INVALID",
         lambda _rows, process: process.update(cwd="/other")),
        ("forged-requested-model-in-envelope", "INVALID",
         lambda _rows, process: process.update(
             requested_model="gpt-5.6-terra")),
    ]
    failures = []
    for name, expected, mutate in cases:
        try:
            _case(name, expected, mutate)
        except AssertionError as exc:
            failures.append(str(exc))
            print(f"  [RED] {exc}")
    if failures:
        print(f"NATIVE-SESSION-PARITY-RED: {len(failures)}/{len(cases)}")
        return 1
    print(f"NATIVE-SESSION-PARITY-GREEN: {len(cases)}/{len(cases)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
