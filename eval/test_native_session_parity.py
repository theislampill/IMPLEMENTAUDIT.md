#!/usr/bin/env python3
"""Cross-path contract for one retained Codex native-session byte stream."""
from __future__ import annotations

import copy
import hashlib
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
_DEFAULT = object()


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


def _official_status(rows, process=_DEFAULT, profile=_DEFAULT,
                     binding=_DEFAULT):
    process = PROCESS if process is _DEFAULT else process
    profile = PROFILE if profile is _DEFAULT else profile
    binding = BINDING if binding is _DEFAULT else binding
    try:
        return hostread.corroborate_session(
            RAW_STDOUT, _raw(rows), "codex", binding, TRACE,
            profile=profile, process_started=process)
    except Exception as exc:
        return f"CRASH({type(exc).__name__})"


def _independent_status(module, rows, process=_DEFAULT, profile=_DEFAULT,
                        binding=_DEFAULT):
    process = PROCESS if process is _DEFAULT else process
    profile = PROFILE if profile is _DEFAULT else profile
    binding = BINDING if binding is _DEFAULT else binding
    try:
        module._validate_native_session(
            RAW_STDOUT.encode("utf-8"), _raw(rows).encode("utf-8"),
            "codex", binding, STDOUT_BINDING, [], profile, process)
    except module.EvidenceInvalid:
        return "INVALID"
    except Exception as exc:
        return f"CRASH({type(exc).__name__})"
    return "VALID"


def _statuses(rows, process=_DEFAULT, profile=_DEFAULT, binding=_DEFAULT):
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


def _formal_codex_profile():
    shell = {
        "logical_path": "/bin/bash",
        "realpath": "/usr/bin/bash",
        "sha256": "a" * 64,
        "stat": "dev=1;ino=1;mode=100755;size=1",
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
        for index, name in enumerate(sorted(hostread.SUPPORTED_READERS))
    }
    post = {
        "environment": environment, "shell": shell,
        "executables": executables,
    }
    probe = json.dumps(
        post, sort_keys=True, separators=(",", ":")).encode("utf-8")
    profile = {
        "schema": "implementaudit-host-read-profile-v2",
        "authority": "mechanically-minted",
        "host": "codex",
        "repo": copy.deepcopy(PROFILE["repo"]),
        "shell": shell,
        "outer_wrapper": {
            "argv_prefix": ["/bin/bash", "-lc"],
            "max_unwrap_layers": 1,
        },
        "environment": environment,
        "executables": executables,
        "probe_sha256": hashlib.sha256(probe).hexdigest(),
    }
    return profile, post


def _profile_validator_statuses(profile, post):
    official = hostread.validate_profile(
        profile, post_probe=post, formal=False, expected_host="codex")
    statuses = [official["host_status"]]
    for module in (b3v4_rederive, candidate_matrix_rederive):
        try:
            module._validate_profile_and_post(profile, post, "codex")
        except module.EvidenceInvalid:
            statuses.append("INVALID")
        except Exception as exc:
            statuses.append(f"CRASH({type(exc).__name__})")
        else:
            statuses.append("VALID")
    return tuple(statuses)


def _duplicate_profile_statuses(profile):
    raw = json.dumps(
        profile, sort_keys=True, separators=(",", ":"))
    raw = raw.replace(
        '"case_sensitive":true',
        '"case_sensitive":false,"case_sensitive":true')
    statuses = []
    try:
        hostread._strict_object(raw)
    except (TypeError, ValueError, json.JSONDecodeError):
        statuses.append("INVALID")
    else:
        statuses.append("VALID")
    for module in (b3v4_rederive, candidate_matrix_rederive):
        try:
            module._decode_json(
                raw, "profile", "profile malformed", True)
        except module.EvidenceInvalid:
            statuses.append("INVALID")
        except Exception as exc:
            statuses.append(f"CRASH({type(exc).__name__})")
        else:
            statuses.append("VALID")
    return tuple(statuses)


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
        candidate_matrix_rederive.CODEX_REQUIRED_TURN_IDENTITY_FIELDS and
        set(hostread.CODEX_NATIVE_REPO_FIELDS) ==
        b3v4_rederive.CODEX_NATIVE_REPO_FIELDS ==
        candidate_matrix_rederive.CODEX_NATIVE_REPO_FIELDS
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
        ("row-type-null", "INVALID",
         lambda rows, _process: rows[0].update(type=None)),
        ("row-type-bool", "INVALID",
         lambda rows, _process: rows[0].update(type=True)),
        ("row-type-int", "INVALID",
         lambda rows, _process: rows[0].update(type=1)),
        ("row-type-float", "INVALID",
         lambda rows, _process: rows[0].update(type=1.0)),
        ("row-type-list", "INVALID",
         lambda rows, _process: rows[0].update(type=[])),
        ("row-type-object", "INVALID",
         lambda rows, _process: rows[0].update(type={})),
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
        ("binding-ordinal-bool-true", "INVALID",
         lambda _r, _p, _f, b: b.update(stdout_turn_ordinal=True)),
        ("binding-ordinal-bool-false", "INVALID",
         lambda _r, _p, _f, b: b.update(stdout_turn_ordinal=False)),
        ("binding-ordinal-float", "INVALID",
         lambda _r, _p, _f, b: b.update(stdout_turn_ordinal=1.0)),
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
    profile_scalar_cases = [
        ("profile-null", None),
        ("profile-bool-false", False),
        ("profile-bool-true", True),
        ("profile-int-zero", 0),
        ("profile-int-one", 1),
        ("profile-float", 1.0),
        ("profile-string", "profile"),
        ("profile-list", []),
    ]
    profile_cases = [
        ("profile-empty-object", {}),
        ("repo-missing", {}),
        ("repo-null", {"repo": None}),
        ("repo-bool", {"repo": True}),
        ("repo-int", {"repo": 1}),
        ("repo-float", {"repo": 1.0}),
        ("repo-string", {"repo": "repo"}),
        ("repo-list", {"repo": []}),
        ("repo-extra-field", {"repo": {
            "lexical_root": ROOT, "real_root": ROOT,
            "case_sensitive": True, "extra": "forbidden"}}),
    ]
    field_bad_values = [
        ("missing", _DEFAULT),
        ("null", None),
        ("bool", True),
        ("int", 1),
        ("float", 1.0),
        ("empty-string", ""),
        ("list", []),
        ("object", {}),
    ]
    for field in ("lexical_root", "real_root"):
        for suffix, value in field_bad_values:
            repo = copy.deepcopy(PROFILE["repo"])
            if value is _DEFAULT:
                repo.pop(field)
            else:
                repo[field] = value
            profile_cases.append((f"repo-{field}-{suffix}", {"repo": repo}))
    for suffix, value in [
            ("missing", _DEFAULT), ("null", None), ("int-zero", 0),
            ("int-one", 1), ("int-negative", -1), ("float-zero", 0.0),
            ("float-one", 1.0), ("empty-string", ""),
            ("false-string", "false"), ("true-string", "true"),
            ("list", []), ("object", {})]:
        repo = copy.deepcopy(PROFILE["repo"])
        if value is _DEFAULT:
            repo.pop("case_sensitive")
        else:
            repo["case_sensitive"] = value
        profile_cases.append((
            f"repo-case-sensitive-{suffix}", {"repo": repo}))
    for name, profile in profile_cases:
        identity_cases.append((
            name, "INVALID",
            lambda _r, _p, f, _b, value=profile: (
                f.clear(), f.update(copy.deepcopy(value)))))
    for name, expected, mutate in identity_cases:
        try:
            _identity_case(name, expected, mutate)
        except AssertionError as exc:
            failures.append(str(exc))
            print(f"  [RED] {exc}")
    for name, profile in profile_scalar_cases:
        observed = _statuses(
            _base_rows(), copy.deepcopy(PROCESS), profile,
            copy.deepcopy(BINDING))
        if observed != ("INVALID",) * 3:
            failure = (
                f"{name}: expected {('INVALID',) * 3!r}, got {observed!r}")
            failures.append(failure)
            print(f"  [RED] {failure}")
        else:
            print(f"  [OK] {name}: {observed}")
    scalar_context_cases = []
    for label, value in profile_scalar_cases:
        scalar_context_cases.extend((
            (f"process-context-{label}", value, PROFILE, BINDING),
            (f"binding-context-{label}", PROCESS, PROFILE, value),
        ))
    for name, process, profile, binding in scalar_context_cases:
        observed = _statuses(
            _base_rows(), process, profile, binding)
        if observed != ("INVALID",) * 3:
            failure = (
                f"{name}: expected {('INVALID',) * 3!r}, got {observed!r}")
            failures.append(failure)
            print(f"  [RED] {failure}")
        else:
            print(f"  [OK] {name}: {observed}")
    valid_full_profile, valid_post = _formal_codex_profile()
    full_status = _profile_validator_statuses(
        valid_full_profile, valid_post)
    if full_status != ("PASS", "VALID", "VALID"):
        failure = (
            "full-profile-valid: expected ('PASS', 'VALID', 'VALID'), "
            f"got {full_status!r}")
        failures.append(failure)
        print(f"  [RED] {failure}")
    else:
        print(f"  [OK] full-profile-valid: {full_status}")
    for name, profile in profile_cases:
        full_profile = copy.deepcopy(valid_full_profile)
        if isinstance(profile, dict) and "repo" in profile:
            full_profile["repo"] = copy.deepcopy(profile["repo"])
        else:
            full_profile.pop("repo", None)
        observed = _profile_validator_statuses(full_profile, valid_post)
        if observed != ("INVALID",) * 3:
            failure = (
                f"full-{name}: expected {('INVALID',) * 3!r}, "
                f"got {observed!r}")
            failures.append(failure)
            print(f"  [RED] {failure}")
        else:
            print(f"  [OK] full-{name}: {observed}")
    duplicate_status = _duplicate_profile_statuses(valid_full_profile)
    if duplicate_status != ("INVALID",) * 3:
        failure = (
            "full-profile-duplicate-case-sensitive: expected "
            f"{('INVALID',) * 3!r}, got {duplicate_status!r}")
        failures.append(failure)
        print(f"  [RED] {failure}")
    else:
        print("  [OK] full-profile-duplicate-case-sensitive: "
              f"{duplicate_status}")
    if failures:
        total = (len(cases) + len(identity_cases) +
                 len(profile_scalar_cases) + len(scalar_context_cases) +
                 2 + len(profile_cases))
        print(f"NATIVE-SESSION-PARITY-RED: {len(failures)}/{total}")
        return 1
    total = (len(cases) + len(identity_cases) +
             len(profile_scalar_cases) + len(scalar_context_cases) +
             2 + len(profile_cases))
    print(f"NATIVE-SESSION-PARITY-GREEN: {total}/{total}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
