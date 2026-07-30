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


def _official_status(rows, process=None, profile=None, binding=None):
    return hostread.corroborate_session(
        RAW_STDOUT, _raw(rows), "codex", binding or BINDING, TRACE,
        profile=profile or PROFILE, process_started=process or PROCESS)


def _independent_status(module, rows, process=None, profile=None,
                        binding=None):
    effective_binding = binding or BINDING
    try:
        module._validate_native_session(
            RAW_STDOUT.encode("utf-8"), _raw(rows).encode("utf-8"),
            "codex", effective_binding, STDOUT_BINDING, [], profile or PROFILE,
            process or PROCESS)
    except module.EvidenceInvalid:
        return "INVALID"
    return "VALID"


def _statuses(rows, process=None, profile=None, binding=None):
    return (
        _official_status(rows, process, profile, binding),
        _independent_status(
            b3v4_rederive, rows, process, profile, binding),
        _independent_status(
            candidate_matrix_rederive, rows, process, profile, binding),
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


def _identity_case(name, expected, mutate):
    rows = _base_rows()
    process = copy.deepcopy(PROCESS)
    profile = copy.deepcopy(PROFILE)
    binding = copy.deepcopy(BINDING)
    mutate(rows, process, profile, binding)
    observed = _statuses(rows, process, profile, binding)
    if observed != (expected,) * 3:
        raise AssertionError(
            f"{name}: expected {(expected,) * 3!r}, got {observed!r}")
    print(f"  [OK] {name}: {observed}")


def _set_all_paths(rows, process, profile, value, root=None):
    profile["repo"]["lexical_root"] = root if root is not None else value
    process["cwd"] = value
    rows[0]["payload"]["cwd"] = value
    rows[1]["payload"]["cwd"] = value


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
        candidate_matrix_rederive.CODEX_SESSION_START_WINDOW_SECONDS == 10 and
        set(hostread.CODEX_REQUIRED_PROCESS_IDENTITY_FIELDS) ==
        b3v4_rederive.CODEX_REQUIRED_PROCESS_IDENTITY_FIELDS ==
        candidate_matrix_rederive.CODEX_REQUIRED_PROCESS_IDENTITY_FIELDS and
        set(hostread.CODEX_REQUIRED_TURN_IDENTITY_FIELDS) ==
        b3v4_rederive.CODEX_REQUIRED_TURN_IDENTITY_FIELDS ==
        candidate_matrix_rederive.CODEX_REQUIRED_TURN_IDENTITY_FIELDS
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
    identity_cases = [
        ("process-cwd-absent", "INVALID",
         lambda _r, p, _f, _b: p.pop("cwd")),
        ("process-cwd-null", "INVALID",
         lambda _r, p, _f, _b: p.update(cwd=None)),
        ("process-cwd-empty", "INVALID",
         lambda _r, p, _f, _b: p.update(cwd="")),
        ("process-cwd-wrong-type", "INVALID",
         lambda _r, p, _f, _b: p.update(cwd=1)),
        ("meta-cwd-absent", "INVALID",
         lambda r, _p, _f, _b: r[0]["payload"].pop("cwd")),
        ("meta-cwd-null", "INVALID",
         lambda r, _p, _f, _b: r[0]["payload"].update(cwd=None)),
        ("meta-cwd-empty", "INVALID",
         lambda r, _p, _f, _b: r[0]["payload"].update(cwd="")),
        ("meta-cwd-wrong-type", "INVALID",
         lambda r, _p, _f, _b: r[0]["payload"].update(cwd=[])),
        ("turn-cwd-absent", "INVALID",
         lambda r, _p, _f, _b: r[1]["payload"].pop("cwd")),
        ("turn-cwd-null", "INVALID",
         lambda r, _p, _f, _b: r[1]["payload"].update(cwd=None)),
        ("turn-cwd-empty", "INVALID",
         lambda r, _p, _f, _b: r[1]["payload"].update(cwd="")),
        ("turn-cwd-wrong-type", "INVALID",
         lambda r, _p, _f, _b: r[1]["payload"].update(cwd={})),
        ("requested-model-absent", "INVALID",
         lambda _r, p, _f, _b: p.pop("requested_model")),
        ("requested-model-null", "INVALID",
         lambda _r, p, _f, _b: p.update(requested_model=None)),
        ("requested-model-empty", "INVALID",
         lambda _r, p, _f, _b: p.update(requested_model="")),
        ("requested-model-wrong-type", "INVALID",
         lambda _r, p, _f, _b: p.update(requested_model=1)),
        ("observed-model-absent", "INVALID",
         lambda r, _p, _f, _b: r[1]["payload"].pop("model")),
        ("observed-model-null", "INVALID",
         lambda r, _p, _f, _b: r[1]["payload"].update(model=None)),
        ("observed-model-empty", "INVALID",
         lambda r, _p, _f, _b: r[1]["payload"].update(model="")),
        ("observed-model-wrong-type", "INVALID",
         lambda r, _p, _f, _b: r[1]["payload"].update(model=[])),
        ("both-models-absent", "INVALID",
         lambda r, p, _f, _b: (
             p.pop("requested_model"), r[1]["payload"].pop("model"))),
        ("models-equal", "VALID",
         lambda _r, _p, _f, _b: None),
        ("models-conflict", "INVALID",
         lambda r, _p, _f, _b: r[1]["payload"].update(
             model="gpt-5.6-terra")),
        ("models-case-variant-sensitive", "INVALID",
         lambda r, _p, _f, _b: r[1]["payload"].update(
             model="GPT-5.6-LUNA")),
        ("models-case-variant-insensitive-path-policy", "INVALID",
         lambda r, _p, f, _b: (
             f["repo"].update(case_sensitive=False),
             r[1]["payload"].update(model="GPT-5.6-LUNA"))),
        ("process-start-absent", "INVALID",
         lambda _r, p, _f, _b: p.pop("started_at")),
        ("process-start-null", "INVALID",
         lambda _r, p, _f, _b: p.update(started_at=None)),
        ("process-start-empty", "INVALID",
         lambda _r, p, _f, _b: p.update(started_at="")),
        ("process-start-wrong-type", "INVALID",
         lambda _r, p, _f, _b: p.update(started_at=1)),
        ("meta-thread-id-absent", "INVALID",
         lambda r, _p, _f, _b: r[0]["payload"].pop("id")),
        ("meta-thread-id-null", "INVALID",
         lambda r, _p, _f, _b: r[0]["payload"].update(id=None)),
        ("meta-thread-id-empty", "INVALID",
         lambda r, _p, _f, _b: r[0]["payload"].update(id="")),
        ("meta-thread-id-wrong-type", "INVALID",
         lambda r, _p, _f, _b: r[0]["payload"].update(id=1)),
        ("meta-session-id-conflict", "INVALID",
         lambda r, _p, _f, _b: r[0]["payload"].update(
             session_id="other")),
        ("binding-thread-absent", "INVALID",
         lambda _r, _p, _f, b: b.pop("thread_id")),
        ("binding-thread-null", "INVALID",
         lambda _r, _p, _f, b: b.update(thread_id=None)),
        ("binding-thread-empty", "INVALID",
         lambda _r, _p, _f, b: b.update(thread_id="")),
        ("binding-thread-wrong-type", "INVALID",
         lambda _r, _p, _f, b: b.update(thread_id=1)),
        ("native-turn-absent", "INVALID",
         lambda r, _p, _f, _b: r[1]["payload"].pop("turn_id")),
        ("native-turn-null", "INVALID",
         lambda r, _p, _f, _b: r[1]["payload"].update(turn_id=None)),
        ("native-turn-empty", "INVALID",
         lambda r, _p, _f, _b: r[1]["payload"].update(turn_id="")),
        ("native-turn-wrong-type", "INVALID",
         lambda r, _p, _f, _b: r[1]["payload"].update(turn_id=1)),
        ("binding-native-turn-conflict", "INVALID",
         lambda _r, _p, _f, b: b.update(native_turn_id="other")),
        ("binding-ordinal-zero", "INVALID",
         lambda _r, _p, _f, b: b.update(stdout_turn_ordinal=0)),
        ("binding-ordinal-string", "INVALID",
         lambda _r, _p, _f, b: b.update(stdout_turn_ordinal="1")),
        ("path-case-sensitive-conflict", "INVALID",
         lambda r, p, _f, _b: (
             p.update(cwd="/FIXTURE/REPO"),
             r[0]["payload"].update(cwd="/FIXTURE/REPO"),
             r[1]["payload"].update(cwd="/FIXTURE/REPO"))),
        ("path-case-insensitive-equivalent", "VALID",
         lambda r, p, f, _b: (
             f["repo"].update(case_sensitive=False),
             p.update(cwd="/FIXTURE/REPO"),
             r[0]["payload"].update(cwd="/FIXTURE/REPO"),
             r[1]["payload"].update(cwd="/FIXTURE/REPO"))),
        ("path-case-insensitive-one-side", "VALID",
         lambda _r, p, f, _b: (
             f["repo"].update(case_sensitive=False),
             p.update(cwd="/FIXTURE/REPO"))),
        ("path-backslash-equivalent", "VALID",
         lambda r, p, _f, _b: (
             p.update(cwd="\\fixture\\repo"),
             r[0]["payload"].update(cwd="\\fixture\\repo"),
             r[1]["payload"].update(cwd="\\fixture\\repo"))),
        ("path-trailing-separator-equivalent", "VALID",
         lambda r, p, _f, _b: (
             p.update(cwd="/fixture/repo/"),
             r[0]["payload"].update(cwd="/fixture/repo/"),
             r[1]["payload"].update(cwd="/fixture/repo/"))),
        ("path-dot-segment-not-normalized", "INVALID",
         lambda r, p, _f, _b: (
             p.update(cwd="/fixture/./repo"),
             r[0]["payload"].update(cwd="/fixture/./repo"),
             r[1]["payload"].update(cwd="/fixture/./repo"))),
        ("path-parent-segment-not-normalized", "INVALID",
         lambda r, p, _f, _b: (
             p.update(cwd="/fixture/x/../repo"),
             r[0]["payload"].update(cwd="/fixture/x/../repo"),
             r[1]["payload"].update(cwd="/fixture/x/../repo"))),
        ("unicode-lowercase-path-equivalent", "VALID",
         lambda r, p, f, _b: (
             f["repo"].update(
                 lexical_root="/fixture/Σ", real_root="/fixture/Σ",
                 case_sensitive=False),
             p.update(cwd="/FIXTURE/σ"),
             r[0]["payload"].update(cwd="/FIXTURE/σ"),
             r[1]["payload"].update(cwd="/FIXTURE/σ"))),
        ("unicode-casefold-expansion-not-equivalent", "INVALID",
         lambda r, p, f, _b: (
             f["repo"].update(
                 lexical_root="/fixture/Straße", real_root="/fixture/Straße",
                 case_sensitive=False),
             p.update(cwd="/FIXTURE/STRASSE"),
             r[0]["payload"].update(cwd="/FIXTURE/STRASSE"),
             r[1]["payload"].update(cwd="/FIXTURE/STRASSE"))),
        ("unicode-normalization-not-equivalent", "INVALID",
         lambda r, p, f, _b: (
             f["repo"].update(
                 lexical_root="/fixture/é", real_root="/fixture/é",
                 case_sensitive=False),
             p.update(cwd="/fixture/e\u0301"),
             r[0]["payload"].update(cwd="/fixture/e\u0301"),
             r[1]["payload"].update(cwd="/fixture/e\u0301"))),
    ]
    for name, expected, mutate in identity_cases:
        try:
            _identity_case(name, expected, mutate)
        except AssertionError as exc:
            failures.append(str(exc))
            print(f"  [RED] {exc}")
    if failures:
        total = len(cases) + len(identity_cases)
        print(f"NATIVE-SESSION-PARITY-RED: {len(failures)}/{total}")
        return 1
    total = len(cases) + len(identity_cases)
    print(f"NATIVE-SESSION-PARITY-GREEN: {total}/{total}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
