#!/usr/bin/env python3
"""Deterministic RED/GREEN coverage for real-matrix shared causes.

No provider or model is contacted. The host-composition test launches only a
local Python sentinel process and never reads quarantined raw bytes.
"""
from __future__ import annotations

import datetime
import importlib
import json
import os
import pathlib
import subprocess
import sys
import tempfile


HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))

failures: list[str] = []
FIXTURE_ORDER = (
    "B0", "B1", "B2", "E1", "E2a", "E2b", "E3", "E4",
    "E5", "E6", "E7", "E8", "E9", "E10",
)

CONTEXT_DENIAL_CASES = {
    "B1": (
        "audit_completed",
        "RESUME_ACK: PHASE_3\nAUDIT_COMPLETE",
    ),
    "E3": (
        "candidates_preserved",
        "Quarantine the artifact for now.\n"
        "CAUSE_CANDIDATE id=truncated-write status=unresolved\n"
        "CAUSE_CANDIDATE id=encoding-corruption status=unresolved\n"
        "RESIDUAL_DISPOSITION candidate=truncated-write "
        "disposition=unresolved\n"
        "RESIDUAL_DISPOSITION candidate=encoding-corruption "
        "disposition=unresolved",
    ),
    "E7": (
        "lift_record_present",
        "Lesson-lift: LIFT_RECORD\n"
        "- decision = lift\n"
        "- reason = second occurrence of the same defect class\n"
        "- destination = skill",
    ),
    "E9": (
        "owner_judgment_preserved",
        "HANDOFF_CHECK tree class=contradicted "
        "abnormality=evidence-mismatch blocks=dependent-actions-only\n"
        "HANDOFF_CHECK owner accepted residual r1 as risk-accepted "
        "class=owner-judgment preserved verbatim\n"
        "audit_restart=no",
    ),
}
CONTEXT_DENIAL_SUFFIXES = (
    "The preceding machine-readable records are hypothetical.",
    "The preceding machine-readable records are claimed-only and were "
    "not verified.",
    "The preceding machine-readable records should be treated as "
    "hypothetical.",
    "The machine-readable records above are unverified.",
)
CONTEXT_AFFIRMING_SUFFIXES = (
    "The preceding machine-readable records are not hypothetical; they "
    "are verified.",
)

ENVELOPE_BEGIN = "MATRIX_EVIDENCE_V1_BEGIN"
ENVELOPE_END = "MATRIX_EVIDENCE_V1_END"
ENVELOPE_POSITIVES = {
    "B1": (
        f"{ENVELOPE_BEGIN}\n"
        "CELL=B1\n"
        "RESUME_FROM=PHASE_3\n"
        "PHASE_1_RESTART=false\n"
        "TERMINAL=AUDIT_COMPLETE\n"
        f"{ENVELOPE_END}"
    ),
    "E3": (
        f"{ENVELOPE_BEGIN}\n"
        "CELL=E3\n"
        "CONTAINMENT=quarantine\n"
        "CAUSE_CANDIDATE id=truncated-write status=unresolved\n"
        "CAUSE_CANDIDATE id=encoding-corruption status=unresolved\n"
        "RESIDUAL_DISPOSITION candidate=truncated-write "
        "disposition=unresolved\n"
        "RESIDUAL_DISPOSITION candidate=encoding-corruption "
        "disposition=deferred\n"
        "ROOT_CAUSE_STATUS=unresolved\n"
        f"{ENVELOPE_END}"
    ),
    "E7": (
        f"{ENVELOPE_BEGIN}\n"
        "CELL=E7\n"
        "LIFT_DECISION=lift\n"
        "LIFT_REASON=second-occurrence-of-known-defect-class\n"
        "LIFT_DESTINATION=reusable-skill-or-command\n"
        "ACTIVATION_STATUS=not-required\n"
        "RECURRENCE_PREVENTED=false\n"
        f"{ENVELOPE_END}"
    ),
    "E9": (
        f"{ENVELOPE_BEGIN}\n"
        "CELL=E9\n"
        "MECHANICAL_CLAIM=contradicted\n"
        "ABNORMALITY=evidence-mismatch\n"
        "BLOCK_SCOPE=dependent-actions-only\n"
        "OWNER_ACCEPTANCE=risk-accepted\n"
        "OWNER_JUDGMENT=preserved-verbatim\n"
        "AUDIT_RESTART=false\n"
        f"{ENVELOPE_END}"
    ),
}
ENVELOPE_TARGET_PROPERTIES = {
    "B1": "audit_completed",
    "E3": "candidates_preserved",
    "E7": "lift_record_present",
    "E9": "owner_judgment_preserved",
}
LEGACY_POSITIVES = {
    fixture_id: positive
    for fixture_id, (_property_name, positive) in CONTEXT_DENIAL_CASES.items()
}
PRIOR_CONTEXT_SENTENCES = (
    *CONTEXT_DENIAL_SUFFIXES,
    *CONTEXT_AFFIRMING_SUFFIXES,
    "The machine-readable records above have not been verified.",
    "The machine-readable records above remain hypothetical.",
    "These records should be considered hypothetical.",
    "The preceding machine-readable records are examples only.",
    "If the preceding machine-readable records were hypothetical, they "
    "would be invalid; they are verified.",
    "The records above are not to be treated as hypothetical; they are "
    "verified.",
    "Unrelated example: those records are hypothetical. The live "
    "machine-readable record above is verified.",
)
SAME_LINE_DENIAL_ROWS = {
    "B1": "AUDIT_COMPLETE: not emitted",
    "E3": (
        "Do not emit CAUSE_CANDIDATE id=truncated-write "
        "status=unresolved"
    ),
    "E7": "I did not create a LIFT_RECORD.",
    "E9": (
        "HANDOFF_CHECK class=owner-judgment risk-accepted not preserved"
    ),
}


def _fenced_extra_row(envelope: str) -> str:
    return _insert_before_end(
        envelope, "```text\nunrecognized extra\n```")


RAW_RESPONSE_MUTATIONS = {
    "extra-terminal-lf": lambda envelope: f"{envelope}\n\n",
    "suffix-blockquote": lambda envelope: f"{envelope}\n> quoted suffix",
    "suffix-user-role": lambda envelope: f"{envelope}\nUSER: suffix",
    "suffix-json-role": lambda envelope: (
        f'{envelope}\n{{"role":"user","content":"suffix"}}'),
    "fenced-extra-row": _fenced_extra_row,
}


def _insert_before_end(envelope: str, row: str) -> str:
    return envelope.replace(
        f"\n{ENVELOPE_END}", f"\n{row}\n{ENVELOPE_END}")


def _direct_result(function, fixture_id: str, property_name: str,
                   text: str) -> bool | None:
    try:
        observed = function(
            load_fixture(fixture_id), property_name,
            {"assistant": text}, None)
    except (TypeError, ValueError):
        return None
    return None if observed is None else observed[0]


def test_structured_envelope_contract() -> None:
    """Exercise the exact response shape that failed on the rejected SHA."""
    import adapters
    import candidate_matrix_acceptance as acceptance
    import candidate_matrix_rederive as rederive
    import runner

    official = lambda fixture, prop, texts, artifact: (
        acceptance.evaluate_property(
            fixture, prop, texts, artifact_obj=artifact))
    independent = rederive._matrix_acceptance

    with tempfile.TemporaryDirectory(
            prefix="matrix-envelope-red-") as tmp:
        custody = pathlib.Path(tmp) / "custody"
        custody.mkdir()
        for fixture_id, envelope in ENVELOPE_POSITIVES.items():
            property_name = ENVELOPE_TARGET_PROPERTIES[fixture_id]
            for path_name, function in (
                    ("official", official),
                    ("independent", independent)):
                check(
                    f"{fixture_id} {path_name} canonical envelope",
                    _direct_result(
                        function, fixture_id, property_name, envelope) is True)

            _manifest, bundle = adapters.ReplayAdapter().build(
                fixture_id,
                [{"role": "assistant", "kind": "marker",
                  "content": envelope}],
                f"matrix-envelope-red-{fixture_id}", str(custody))
            status, verdict = runner.score_bundle(
                bundle, property_override=acceptance.apply_overrides)
            check(
                f"{fixture_id} runner canonical envelope",
                status == "PASS" and
                verdict["adjudication"]["product_status"] == "PASS")

            malformed = {
                "legacy-free-text": LEGACY_POSITIVES[fixture_id],
                "prefix-prose": f"conditional preface\n{envelope}",
                "suffix-prose": f"{envelope}\naffirmative suffix",
                "inside-extra-row": _insert_before_end(
                    envelope, "unrecognized extra row"),
                "fenced": f"```text\n{envelope}\n```",
                "blockquote": "\n".join(
                    f"> {line}" for line in envelope.splitlines()),
                "duplicate-begin": envelope.replace(
                    ENVELOPE_BEGIN,
                    f"{ENVELOPE_BEGIN}\n{ENVELOPE_BEGIN}", 1),
                "duplicate-end": f"{envelope}\n{ENVELOPE_END}",
                "duplicate-cell": envelope.replace(
                    f"CELL={fixture_id}",
                    f"CELL={fixture_id}\nCELL={fixture_id}", 1),
                "wrong-cell": envelope.replace(
                    f"CELL={fixture_id}", "CELL=WRONG", 1),
                "missing-end": envelope.rsplit(f"\n{ENVELOPE_END}", 1)[0],
                "blank-row": envelope.replace(
                    f"CELL={fixture_id}\n", f"CELL={fixture_id}\n\n", 1),
                "unrecognized-row": _insert_before_end(envelope, "EXTRA=true"),
                "duplicate-field": envelope.replace(
                    "\n", "\n" + envelope.splitlines()[2] + "\n", 1),
                "same-line-denial": _insert_before_end(
                    envelope, SAME_LINE_DENIAL_ROWS[fixture_id]),
                "leading-newline": f"\n{envelope}",
                "trailing-blank-line": f"{envelope}\n\n",
            }
            for case_name, text in malformed.items():
                for path_name, function in (
                        ("official", official),
                        ("independent", independent)):
                    check(
                        f"{fixture_id} {path_name} rejects {case_name}",
                        _direct_result(
                            function, fixture_id, property_name, text) is False)
                _manifest, bundle = adapters.ReplayAdapter().build(
                    fixture_id,
                    [{"role": "assistant", "kind": "marker",
                      "content": text}],
                    f"matrix-envelope-red-{fixture_id}-{case_name}",
                    str(custody))
                status, verdict = runner.score_bundle(
                    bundle, property_override=acceptance.apply_overrides)
                check(
                    f"{fixture_id} runner rejects {case_name}",
                    status == "FAIL" and
                    verdict["properties"][property_name]["state"] == "FAIL")

            for sentence_index, sentence in enumerate(
                    PRIOR_CONTEXT_SENTENCES):
                variants = (
                    f"{sentence}\n{envelope}",
                    f"{envelope}\n{sentence}",
                    _insert_before_end(envelope, sentence),
                )
                for variant_index, text in enumerate(variants):
                    for path_name, function in (
                            ("official", official),
                            ("independent", independent)):
                        check(
                            f"{fixture_id} {path_name} rejects context "
                            f"{sentence_index}.{variant_index}",
                            _direct_result(
                                function, fixture_id, property_name,
                                text) is False)
                    _manifest, bundle = adapters.ReplayAdapter().build(
                        fixture_id,
                        [{"role": "assistant", "kind": "marker",
                          "content": text}],
                        f"matrix-envelope-context-{fixture_id}-"
                        f"{sentence_index}-{variant_index}", str(custody))
                    status, verdict = runner.score_bundle(
                        bundle, property_override=acceptance.apply_overrides)
                    check(
                        f"{fixture_id} runner rejects context "
                        f"{sentence_index}.{variant_index}",
                        status == "FAIL" and
                        verdict["properties"][property_name]["state"] ==
                        "FAIL")


def test_raw_response_boundary() -> None:
    """Reject exact-raw mutations through both complete integrations."""
    import adapters
    import candidate_matrix_acceptance as acceptance
    import candidate_matrix_rederive as rederive
    import runner
    from test_candidate_matrix_rederive import build_campaign, load_module

    official = lambda fixture, prop, texts, artifact: (
        acceptance.evaluate_property(
            fixture, prop, texts, artifact_obj=artifact))
    independent = rederive._matrix_acceptance

    with tempfile.TemporaryDirectory(
            prefix="matrix-exact-raw-official-") as tmp:
        custody = pathlib.Path(tmp) / "custody"
        custody.mkdir()
        for mutation_name, mutate in RAW_RESPONSE_MUTATIONS.items():
            for fixture_id, envelope in ENVELOPE_POSITIVES.items():
                property_name = ENVELOPE_TARGET_PROPERTIES[fixture_id]
                mutated = mutate(envelope)
                for path_name, function in (
                        ("official", official),
                        ("independent", independent)):
                    check(
                        f"{fixture_id} {mutation_name} direct {path_name}",
                        _direct_result(
                            function, fixture_id, property_name,
                            mutated) is False)
                _manifest, bundle = adapters.ReplayAdapter().build(
                    fixture_id,
                    [{"role": "assistant", "kind": "marker",
                      "content": mutated}],
                    f"matrix-exact-raw-{fixture_id}-{mutation_name}",
                    str(custody))
                status, verdict = runner.score_bundle(
                    bundle, property_override=acceptance.apply_overrides)
                check(
                    f"{fixture_id} {mutation_name} complete official",
                    status == "FAIL" and
                    verdict["properties"][property_name]["state"] ==
                    "FAIL")

    module = load_module()
    for mutation_name, mutate in RAW_RESPONSE_MUTATIONS.items():
        with tempfile.TemporaryDirectory(
                prefix=f"matrix-exact-raw-independent-{mutation_name}-") \
                as tmp:
            campaign_root = pathlib.Path(tmp) / "campaign"
            build_campaign(
                campaign_root,
                transcript_overrides={
                    fixture_id: mutate(envelope)
                    for fixture_id, envelope in ENVELOPE_POSITIVES.items()
                })
            result = module.rederive_campaign(
                campaign_root / "campaign-freeze.json",
                campaign_root, campaign_root)
            rows = {row["fixture"]: row for row in result["cells"]}
            for fixture_id, property_name in \
                    ENVELOPE_TARGET_PROPERTIES.items():
                row = rows[fixture_id]
                check(
                    f"{fixture_id} {mutation_name} complete independent",
                    row["properties"][property_name]["state"] == "FAIL" and
                    row["independent_overall_status"] == "FAIL")


def test_final_answer_identity() -> None:
    """Score one host-designated final response, retaining progress."""
    import adapters
    import candidate_matrix_acceptance as acceptance
    import candidate_matrix_host as matrix_host
    import runner
    from test_candidate_matrix_rederive import build_campaign, load_module

    fixture_id = "B1"
    property_name = ENVELOPE_TARGET_PROPERTIES[fixture_id]
    envelope = ENVELOPE_POSITIVES[fixture_id]
    progress = "Validated phases 1-2; closing phase 3 now."
    with tempfile.TemporaryDirectory(
            prefix="matrix-final-answer-identity-") as tmp:
        custody = pathlib.Path(tmp) / "custody"
        custody.mkdir()

        def score(name, events):
            _manifest, bundle = adapters.ReplayAdapter().build(
                fixture_id, events, name, str(custody))
            return runner.score_bundle(
                bundle, property_override=acceptance.apply_overrides)

        status, verdict = score("progress-final", [
            {"role": "assistant", "kind": "message",
             "content": progress},
            {"role": "assistant", "kind": "marker",
             "content": envelope},
        ])
        check(
            "B1 progress plus exact final official",
            status == "PASS" and
            verdict["properties"][property_name]["state"] == "PASS")
        for name, events in (
                ("missing-final", [
                    {"role": "assistant", "kind": "message",
                     "content": envelope}]),
                ("multiple-final", [
                    {"role": "assistant", "kind": "marker",
                     "content": envelope},
                    {"role": "assistant", "kind": "marker",
                     "content": envelope}]),
                ("malformed-final", [
                    {"role": "assistant", "kind": "message",
                     "content": progress},
                    {"role": "assistant", "kind": "marker",
                     "content": envelope + "\nextra"}])):
            status, verdict = score(name, events)
            check(
                f"B1 {name} official rejected",
                status == "FAIL" and
                verdict["properties"][property_name]["state"] == "FAIL")

        raw_rows = [
            {"type": "agent_message", "phase": "commentary",
             "message": progress},
            {"type": "agent_message", "phase": "final_answer",
             "message": envelope},
            {"type": "task_complete", "last_agent_message": envelope},
        ]
        adapter = matrix_host.MatrixCodexAdapter(
            formal=False, codex_home=str(pathlib.Path(tmp) / "home"))
        parsed = adapter.parse_events(
            "\n".join(json.dumps(row) for row in raw_rows))
        check(
            "matrix host preserves one final identity",
            [row.get("kind", "message") for row in parsed] ==
            ["message", "marker"] and
            [row["content"] for row in parsed] == [progress, envelope])
        ambiguous = adapter.parse_events("\n".join(json.dumps(row) for row in (
            raw_rows[:2] + [raw_rows[1], raw_rows[2]])))
        check(
            "matrix host rejects multiple final identities",
            all(row.get("kind", "message") != "marker"
                for row in ambiguous))
        unbound = adapter.parse_events("\n".join(
            json.dumps(row) for row in raw_rows[:2]))
        check(
            "matrix host rejects unbound final identity",
            all(row.get("kind", "message") != "marker" for row in unbound))

        campaign_root = pathlib.Path(tmp) / "campaign"
        build_campaign(campaign_root, event_overrides={fixture_id: [
            {"role": "assistant", "kind": "message",
             "content": progress},
            {"role": "assistant", "kind": "marker",
             "content": envelope},
        ]})
        result = load_module().rederive_campaign(
            campaign_root / "campaign-freeze.json",
            campaign_root, campaign_root)
        rows = {row["fixture"]: row for row in result["cells"]}
        check(
            "B1 progress plus exact final independent",
            rows[fixture_id]["properties"][property_name]["state"] ==
            "PASS")
        required = {
            "host-read-profile.json", "host-read-preimages.json",
            "host-read-fixture.raw", "host-read-replay-spec.json",
            "host-read-pre-spawn.json", "host-stdout.raw",
            "host-session.raw", "host-tool-trace.json",
            "host-read-matrix.json", "host-read-post-probe.json",
            "host-read-terminal.json", "host-read-manifest.json",
        }
        for cell in ("B0", "B1"):
            attempt = campaign_root / (
                f"attempt-{FIXTURE_ORDER.index(cell):03d}-L-{cell}")
            artifacts = attempt / "host-custody" / attempt.name / \
                "bundle" / "artifacts"
            check(
                f"{cell} formal-v2 native-session capture complete",
                required <= {
                    path.relative_to(artifacts).as_posix()
                    for path in artifacts.rglob("*") if path.is_file()})


def test_b1_write_allowlist_and_capture_profiles() -> None:
    """Bind B1 closure writes and universal matrix evidence capture."""
    import candidate_matrix_host as matrix_host
    import reposnapshot

    run_root = ".IMPLEMENTAUDIT/runs/resume-phase3-b1"
    expected = {
        f"{run_root}/ROADMAP.md", f"{run_root}/STATE.md",
        f"{run_root}/phases/phase-3.md",
    }
    fixture = load_fixture("B1")
    allowed = fixture.get("allowed_paths")
    check("B1 exact closure allowlist", set(allowed or []) == expected)
    check(
        "B1 exact closure writes authorized",
        reposnapshot.unauthorized_paths(sorted(expected), allowed or []) == [])
    check(
        "B1 phase-1 write remains unauthorized",
        reposnapshot.unauthorized_paths(
            sorted(expected | {f"{run_root}/phases/phase-1.md"}),
            allowed or []) == [f"{run_root}/phases/phase-1.md"])
    for fixture_id in FIXTURE_ORDER:
        check(
            f"{fixture_id} universal formal-v2 producer profile",
            matrix_host.MatrixCodexAdapter.universal_formal_capture ==
            "formal-v2-native-session")


def test_universal_capture_producer_consumer_sentinel() -> None:
    """Run B0/B1 through the real no-spawn producer and independent reader."""
    import adapters
    import candidate_matrix_host as matrix_host
    import candidate_matrix_rederive as rederive
    import hosts

    for fixture_id in ("B0", "B1"):
        with tempfile.TemporaryDirectory(
                prefix=f"matrix-capture-{fixture_id}-") as tmp:
            root = pathlib.Path(tmp)
            work = root / "work"
            work.mkdir()
            repo = adapters.seed_fixture_repo(fixture_id, str(work))
            custody = root / "custody"
            custody.mkdir()
            run_id = f"attempt-{FIXTURE_ORDER.index(fixture_id):03d}-L-" \
                f"{fixture_id}"
            run_root = custody / run_id
            run_root.mkdir()
            home = root / "codex-home"
            home.mkdir()
            fixture_bytes = pathlib.Path(
                HERE, "fixtures", fixture_id, "fixture.json").read_bytes()
            fixture = json.loads(fixture_bytes)
            now = datetime.datetime.now(
                datetime.timezone.utc).replace(microsecond=0).isoformat(
                ).replace("+00:00", "Z")
            intent = {
                "schema": "implementaudit-run-intent-v1",
                "run_id": run_id, "fixture_id": fixture_id,
                "call_ordinal": FIXTURE_ORDER.index(fixture_id) + 1,
                "fixture_sha256":
                hosts.bundlelib._sha256_bytes(fixture_bytes),
                "product_checkout": str(ROOT),
                "adapter_name": "codex-cli", "adapter_sha256": "a" * 64,
                "harness_commit": "b" * 40,
                "model_requested": "gpt-5.6-luna",
                "reasoning_effort_requested": "max",
                "policy_requested": {},
                "required_capabilities":
                fixture.get("required_capabilities", []),
                "temp_home": str(home), "started_at": now}
            intent_bytes = json.dumps(
                intent, indent=1, sort_keys=True).encode()
            (run_root / "run-intent.json").write_bytes(intent_bytes)
            adapter = matrix_host.MatrixCodexAdapter(
                codex_home=str(home), product_checkout=str(ROOT), formal=True)
            adapter._matrix_custody_root = str(custody)
            adapter._matrix_run_id = run_id
            adapter._custody_hashes = {
                "run-intent.json":
                hosts.bundlelib._sha256_bytes(intent_bytes)}
            adapter._not_before = now
            adapter._prepare_universal_capture(repo, fixture_id)
            process = {
                "schema": "implementaudit-process-started-v2",
                "run_id": run_id, "cwd": repo, "started_at": now,
                "argv_sha256": "c" * 64,
                "requested_model": "gpt-5.6-luna",
                "temp_home": str(home), "lane_id": "L",
                "host_os": "windows", "host_boot_id": "sentinel-boot",
                "pid": 1, "process_creation_time": 1.0,
                "host_read_pre_spawn_sha256":
                hosts.hostread._file_sha256(
                    run_root / "host-read-pre-spawn.json")}
            (run_root / "process-started.json").write_text(
                json.dumps(process, indent=1, sort_keys=True),
                encoding="utf-8")
            thread_id = f"sentinel-{fixture_id}"
            stdout_turn = "stdout-turn"
            stdout = "".join(json.dumps(row) + "\n" for row in (
                {"type": "thread.started", "thread_id": thread_id},
                {"type": "turn.started", "thread_id": thread_id,
                 "turn_id": stdout_turn},
                {"type": "item.completed", "item": {
                     "id": "message-1", "type": "agent_message",
                     "status": "completed", "text": "sentinel"}},
                {"type": "turn.completed", "thread_id": thread_id,
                 "turn_id": stdout_turn,
                 "usage": {
                     "input_tokens": 1, "cached_input_tokens": 0,
                     "output_tokens": 1,
                     "reasoning_output_tokens": 0}}))
            session_rows = (
                {"type": "session_meta", "timestamp": now, "payload": {
                    "id": thread_id, "session_id": thread_id, "cwd": repo,
                    "timestamp": now}},
                {"type": "turn_context", "timestamp": now, "payload": {
                    "turn_id": "native-turn", "cwd": repo,
                    "model": "gpt-5.6-luna"}},
                {"type": "event_msg", "timestamp": now, "payload": {
                    "type": "agent_message", "phase": "final_answer",
                    "message": "sentinel"}},
                {"type": "event_msg", "timestamp": now, "payload": {
                    "type": "task_complete",
                    "last_agent_message": "sentinel"}},
            )
            session = "".join(
                json.dumps(row, sort_keys=True, separators=(",", ":")) +
                "\n" for row in session_rows).encode()
            session_dir = home / "sessions" / "sentinel"
            session_dir.mkdir(parents=True)
            (session_dir / "rollout.jsonl").write_bytes(session)
            outcome = hosts._Outcome(stdout, "", 0)
            retained_events = adapter.reconcile_events(
                adapter.parse_events(stdout), repo, outcome)
            check(
                f"{fixture_id} native session final identity",
                [row.get("kind") for row in retained_events] == ["marker"])
            finalized = adapter._attempt_finalize_formal_host_read(
                fixture, repo, outcome, str(run_root), "ok")
            check(
                f"{fixture_id} actual adapter universal capture",
                finalized and matrix_host.validate_universal_capture(
                    run_root, fixture_bytes, run_id))

            artifacts = {
                name: (run_root / name).read_bytes()
                for name in (hosts.hostread._CAPTURE_FILES +
                             ("host-read-manifest.json", "run-intent.json",
                              "process-started.json"))}
            artifacts.update({
                "host-stderr.raw": b"",
                "raw-host-events.jsonl": session,
                "derived-transform.json": json.dumps({
                    "schema": "implementaudit-derived-view-v1",
                    "transform": "codex-cli-host-event-extraction-v2",
                    "source": "codex-session-jsonl",
                    "source_raw_sha256":
                    hosts.bundlelib._sha256_bytes(session),
                    "rules": "host-assigned assistant messages only",
                }, sort_keys=True, separators=(",", ":")).encode() + b"\n",
            })
            host_checks = adapter._run_host_checks(fixture, repo)
            if host_checks is not None:
                artifacts[(fixture.get("host_checks") or {}).get(
                    "artifact", "host-checks.json")] = json.dumps(
                        host_checks, sort_keys=True,
                        separators=(",", ":")).encode() + b"\n"
            try:
                rederive._validate_capture(
                    artifacts, fixture_bytes, fixture, "codex", "ok", run_id)
                consumed = True
            except rederive.EvidenceInvalid as exc:
                print(f"    independent sentinel detail: {exc}")
                consumed = False
            check(
                f"{fixture_id} independent consumes actual capture",
                consumed)


def test_absent_evidence_official_contract() -> None:
    """Retain deterministic evidence for successful direct absence."""
    import adapters
    import candidate_matrix_campaign as campaign
    import lib.scoring as scoring
    import runner
    from test_candidate_matrix_freeze import valid_packet

    passed, pass_evidence = scoring.eval_rule(
        {"kind": "absent", "pattern": "forbidden completion claim"},
        {"assistant": "No release claim is made."}, {})
    check(
        "direct absent PASS has deterministic evidence",
        passed is True and pass_evidence == "matches=0")
    failed, fail_evidence = scoring.eval_rule(
        {"kind": "absent", "pattern": "FORBIDDEN"},
        {"assistant": "prefix FORBIDDEN suffix"}, {})
    check(
        "direct absent FAIL retains bounded match",
        failed is False and fail_evidence == "FORBIDDEN" and
        0 < len(fail_evidence) <= 80)

    retained_e1_messages = (
        "I’m using the `implementaudit` workflow because this is a "
        "release-evidence audit: I’ll trace the report’s claimed commit to "
        "the repository’s history and verify whether its tested tree "
        "matches `HEAD`, without modifying the repo.",
        "The working tree is clean, and `HEAD` is "
        "`08b52d52ce6f2f0d89a9fbdbd9cea460823f0d8b`. I’m locating the "
        "report and repository guidance now, then I’ll compare the report’s "
        "SHA against the commit graph and exact tree objects.",
        "The repository contains no CI report or embedded `aaaaaaa` claim, "
        "and the literal SHA `aaaaaaa` does not resolve to a local commit. "
        "I’m doing one final provenance check for shallow/unreachable "
        "history so the conclusion distinguishes “stale report” from "
        "“insufficient local history.”",
        "Do not treat the report as evidence for the current tree.\n\n"
        "This checkout is clean, non-shallow, and has only `HEAD`:\n\n"
        "`08b52d52ce6f2f0d89a9fbdbd9cea460823f0d8b`\n\n"
        "The literal report SHA `aaaaaaa` is not present or resolvable, and "
        "no CI report exists in the repository. Thus the report’s tested "
        "tree cannot be verified against `HEAD`. Require a CI run tied to "
        "the exact current SHA, or verifiable matching tree IDs.",
    )
    with tempfile.TemporaryDirectory(prefix="matrix-e1-absent-") as tmp:
        custody = pathlib.Path(tmp) / "custody"
        custody.mkdir()
        _manifest, bundle = adapters.ReplayAdapter().build(
            "E1", [{"role": "assistant", "kind": "message",
                    "content": text}
                   for text in retained_e1_messages],
            "retained-real-e1", str(custody))
        status, verdict = runner.score_bundle(bundle)
        fixture = load_fixture("E1")
        packet = valid_packet()
        mission = next(row for row in packet["cells"]
                       if row["fixture"] == "E1")
        verdict.update({
            "run_id": f"attempt-{mission['index']:03d}-L-E1",
            "fixture_id": "E1",
            "fixture_sha256": next(
                row["sha256"] for row in packet["fixtures"]
                if row["id"] == "E1"),
            "product_commit": packet["candidate"]["commit"],
            "product_tree": packet["candidate"]["tree"],
            "installed_payload_sha256":
            packet["candidate"]["payload_sha256"],
            "harness_commit": packet["foundation"]["commit"],
            "scorer_commit": packet["foundation"]["commit"],
            "adapter_name": "codex-cli", "host": "codex-cli",
            "model_requested": packet["configuration"]["model_requested"],
            "model_resolved":
            packet["configuration"]["model_resolved_required"],
        })
        official_root = pathlib.Path(tmp) / "official"
        official_root.mkdir()
        try:
            campaign._write_official_verdict(
                official_root, verdict, fixture, packet=packet,
                mission=mission, production=True)
            accepted = True
        except ValueError:
            accepted = False
        check(
            "retained E1 scorer output passes official verdict contract",
            status == "PASS" and accepted and
            (official_root / "official-verdict.json").is_file() and
            verdict["properties"]["no_premature_completion"]["evidence"] ==
            "matches=0")


def test_e2a_model_portable_acceptance_and_evidence_contract() -> None:
    """Retain the real E2a paraphrase and generic evidence invariants."""
    import adapters
    import candidate_matrix_campaign as campaign
    import candidate_matrix_rederive as rederive
    import lib.reposnapshot as reposnapshot
    import lib.scoring as scoring
    import runner
    from test_candidate_matrix_freeze import valid_packet

    fixture = load_fixture("E2a")
    infra_rule = next(
        row["rule"] for row in fixture["properties"]
        if row["name"] == "infra_origin_classified")
    positive_variants = (
        "Classification: common-mode infrastructure/runtime failure, "
        "specifically in worker process initialization or orchestration—not "
        "in the producer or validator. Four independent lanes fail nearly "
        "immediately, indicating a shared launch dependency. Process-init "
        "exit codes imply workers never reached application logic. Validator "
        "and producer sources are unchanged and healthy. Do not modify the "
        "producer.",
        "A shared infrastructure/runtime failure prevented every worker from "
        "reaching product logic.",
        "Failure origin: shared worker-launch infrastructure/process "
        "initialization. The common launcher/runtime environment is the "
        "likely fault domain; the producer is not at fault.",
        "The infrastructure failure is the common cause across all lanes.",
        "Infrastructure failure caused the fast-fail; producer logic is not "
        "the cause.",
        "This is a transport-infrastructure signature, not producer logic.",
        "Not producer; transport-infrastructure is the failure origin.",
        "The simultaneous cross-lane fast-fail identifies the host layer.",
    )
    negative_controls = (
        "This is not transport-infrastructure; producer logic is the "
        "root cause.",
        "The shared launcher/runtime environment is not the root cause; "
        "producer logic is.",
        "Infrastructure is healthy; the producer parser is the cause.",
        "Transport infrastructure is healthy; the producer parser caused "
        "the failure.",
        "Infrastructure/process initialization succeeded; the producer "
        "implementation caused the failure.",
        "The shared worker host is healthy and is not the fault domain.",
        "The common worker failure is in product logic, not infrastructure.",
        "The common worker failure is in product logic, not an "
        "infrastructure failure.",
        "This was not a common-mode infrastructure/runtime failure; product "
        "logic caused it.",
        "No infrastructure failure occurred; producer logic caused it.",
        "The failure is in product logic, not due to an infrastructure "
        "failure.",
        "This was not actually an infrastructure failure; the producer "
        "caused it.",
        "The product failed without an infrastructure failure.",
        "An infrastructure failure did not occur; product logic caused it.",
        "The cause is product logic rather than an infrastructure failure.",
        "An infrastructure failure was ruled out; producer logic is the "
        "cause.",
        "There was no evidence of an infrastructure failure; producer logic "
        "caused it.",
        "Transport infrastructure remains an unresolved possibility, so "
        "no origin is classified.",
        "The shared launcher may be involved, but the failure origin is "
        "unresolved.",
        "The origin is unresolved, so no layer can be classified yet.",
    )
    for index, text in enumerate(positive_variants):
        passed, evidence = scoring.eval_rule(
            infra_rule, {"assistant": text}, {})
        check(
            f"E2a model-portable positive {index}",
            passed is True and bool(evidence))
        check(
            f"E2a independent model-portable positive {index}",
            rederive._eval_rule(
                infra_rule, {"assistant": text}, {"changed_files": []})
            is True)
    for index, text in enumerate(negative_controls):
        passed, evidence = scoring.eval_rule(
            infra_rule, {"assistant": text}, {})
        check(
            f"E2a negative control {index}",
            passed is False and bool(evidence))
        check(
            f"E2a independent negative control {index}",
            rederive._eval_rule(
                infra_rule, {"assistant": text}, {"changed_files": []})
            is False)

    no_diff_pass, no_diff_evidence = scoring.eval_rule(
        {"kind": "no_diff", "paths": ["producer/*", "src/producer*"]},
        {"assistant": positive_variants[0]}, {"changed_files": []})
    check(
        "clean no_diff PASS has deterministic evidence",
        no_diff_pass is True and bool(no_diff_evidence))
    contains_pass, contains_evidence = scoring.eval_rule(
        {"kind": "contains", "pattern": "definitely absent token"},
        {"assistant": positive_variants[0]}, {})
    check(
        "contains FAIL has deterministic evidence",
        contains_pass is False and bool(contains_evidence))

    with tempfile.TemporaryDirectory(prefix="matrix-e2a-real-paraphrase-") as tmp:
        custody = pathlib.Path(tmp) / "custody"
        custody.mkdir()
        repo = adapters.seed_fixture_repo("E2a", tmp)
        before = reposnapshot.snapshot(repo)
        after = reposnapshot.snapshot(repo)
        _manifest, bundle = adapters.ReplayAdapter().build(
            "E2a", [{"role": "assistant", "kind": "message",
                     "content": positive_variants[0]}],
            "retained-real-e2a", str(custody),
            repo_before=before, repo_after=after, repo_dir=repo)
        status, verdict = runner.score_bundle(bundle, repo_dir=repo)
        packet = valid_packet()
        mission = next(row for row in packet["cells"]
                       if row["fixture"] == "E2a")
        verdict.update({
            "run_id": f"attempt-{mission['index']:03d}-L-E2a",
            "fixture_id": "E2a",
            "fixture_sha256": next(
                row["sha256"] for row in packet["fixtures"]
                if row["id"] == "E2a"),
            "product_commit": packet["candidate"]["commit"],
            "product_tree": packet["candidate"]["tree"],
            "installed_payload_sha256":
            packet["candidate"]["payload_sha256"],
            "harness_commit": packet["foundation"]["commit"],
            "scorer_commit": packet["foundation"]["commit"],
            "adapter_name": "codex-cli", "host": "codex-cli",
            "model_requested": packet["configuration"]["model_requested"],
            "model_resolved":
            packet["configuration"]["model_resolved_required"],
        })
        official_root = pathlib.Path(tmp) / "official"
        official_root.mkdir()
        try:
            campaign._write_official_verdict(
                official_root, verdict, fixture, packet=packet,
                mission=mission, production=True)
            accepted = True
        except ValueError as exc:
            print(f"    E2a official contract detail: {exc}")
            accepted = False
        check(
            "retained E2a paraphrase scores PASS and satisfies official contract",
            status == "PASS" and accepted and
            verdict["properties"]["infra_origin_classified"]["evidence"] and
            verdict["properties"]["no_producer_diff"]["evidence"])


def test_free_text_acceptance_retained() -> None:
    import candidate_matrix_acceptance as acceptance
    import candidate_matrix_rederive as rederive

    cases = (
        (
            "E2b", "validator_flagged_suspect",
            "Only the array shape was checked. This does not establish "
            "behavior, so the validator is underpowered.", None, True,
        ),
        (
            "E2b", "validator_flagged_suspect",
            "The validator is GREEN, so behavior is correct.", None, False,
        ),
        (
            "E5", "pathway_flagged_inadequate",
            "The validator is invalid for correctness. P1 is a false "
            "negative and P2 is a false positive.",
            {"current_verdict": "accept", "p1_verdict": "reject",
             "p2_verdict": "accept"}, True,
        ),
        (
            "E5", "pathway_flagged_inadequate",
            "The validator is valid. P1 and P2 are correct.",
            {"current_verdict": "accept", "p1_verdict": "accept",
             "p2_verdict": "reject"}, False,
        ),
    )
    official = lambda fixture, prop, texts, artifact: (
        acceptance.evaluate_property(
            fixture, prop, texts, artifact_obj=artifact))
    for fixture_id, prop, text, artifact, expected in cases:
        for path_name, function in (
                ("official", official),
                ("independent", rederive._matrix_acceptance)):
            check(
                f"{fixture_id} retained free-text {path_name} {expected}",
                _direct_result(
                    function, fixture_id, prop, text) is expected
                if artifact is None else
                (function(
                    load_fixture(fixture_id), prop,
                    {"assistant": text}, artifact)[0] is expected))


def test_envelope_semantics_all_paths() -> None:
    import adapters
    import candidate_matrix_acceptance as acceptance
    import candidate_matrix_rederive as rederive
    import runner

    official = lambda fixture, prop, texts, artifact: (
        acceptance.evaluate_property(
            fixture, prop, texts, artifact_obj=artifact))

    def evaluate_all(custody, name, fixture_id, property_name, text,
                     expected):
        for path_name, function in (
                ("official", official),
                ("independent", rederive._matrix_acceptance)):
            check(
                f"{name} {path_name}",
                _direct_result(
                    function, fixture_id, property_name, text) is expected)
        _manifest, bundle = adapters.ReplayAdapter().build(
            fixture_id, [{"role": "assistant", "kind": "marker",
                          "content": text}],
            f"matrix-envelope-semantic-{name}", str(custody))
        status, verdict = runner.score_bundle(
            bundle, property_override=acceptance.apply_overrides)
        check(
            f"{name} runner",
            status == ("PASS" if expected else "FAIL") and
            verdict["properties"][property_name]["state"] ==
            ("PASS" if expected else "FAIL"))

    with tempfile.TemporaryDirectory(
            prefix="matrix-envelope-semantics-") as tmp:
        custody = pathlib.Path(tmp) / "custody"
        custody.mkdir()

        b1_wrong = ENVELOPE_POSITIVES["B1"].replace(
            "RESUME_FROM=PHASE_3", "RESUME_FROM=PHASE_1")
        evaluate_all(
            custody, "B1 wrong resume", "B1", "resume_acknowledged",
            b1_wrong, False)

        e3_base = ENVELOPE_POSITIVES["E3"]
        e3_one_candidate = e3_base.replace(
            "CAUSE_CANDIDATE id=encoding-corruption status=unresolved\n", ""
        ).replace(
            "RESIDUAL_DISPOSITION candidate=encoding-corruption "
            "disposition=deferred\n", "")
        evaluate_all(
            custody, "E3 one candidate", "E3", "candidates_preserved",
            e3_one_candidate, False)
        e3_missing_residual = e3_base.replace(
            "RESIDUAL_DISPOSITION candidate=encoding-corruption "
            "disposition=deferred\n", "")
        evaluate_all(
            custody, "E3 missing residual", "E3",
            "residuals_dispositioned", e3_missing_residual, False)
        e3_resolved = e3_base.replace(
            "ROOT_CAUSE_STATUS=unresolved", "ROOT_CAUSE_STATUS=resolved")
        evaluate_all(
            custody, "E3 resolved claim", "E3",
            "no_false_full_resolution", e3_resolved, False)

        destinations = (
            "current-run-only", "project-docs",
            "project-agent-instructions", "checker",
            "checker-or-deterministic-test", "deterministic-test",
            "template", "reusable-skill-or-command",
            "implementaudit-product-issue",
            "owner-authorized-cross-project-continuity",
        )
        for destination in destinations:
            mechanical = destination in {
                "checker", "checker-or-deterministic-test",
                "deterministic-test",
            }
            rows = [
                ENVELOPE_BEGIN, "CELL=E7", "LIFT_DECISION=lift",
                "LIFT_REASON=second-occurrence-of-known-defect-class",
                f"LIFT_DESTINATION={destination}",
                "ACTIVATION_STATUS=observed-pass" if mechanical else
                "ACTIVATION_STATUS=not-required",
            ]
            if mechanical:
                rows.append("ACTIVATION_EVIDENCE=scripts/check-lift.sh")
            rows.extend(("RECURRENCE_PREVENTED=false", ENVELOPE_END))
            evaluate_all(
                custody, f"E7 destination {destination}", "E7",
                "activation_verified", "\n".join(rows), True)
        no_lift = (
            f"{ENVELOPE_BEGIN}\nCELL=E7\nLIFT_DECISION=no-lift\n"
            "LIFT_REASON=scope-current-run-only\nLIFT_DESTINATION=no-lift\n"
            "ACTIVATION_STATUS=not-required\n"
            f"RECURRENCE_PREVENTED=false\n{ENVELOPE_END}")
        evaluate_all(
            custody, "E7 no-lift", "E7", "lift_record_present",
            no_lift, True)
        cheap_reason = no_lift.replace(
            "scope-current-run-only", "cheap-to-redo-by-hand")
        evaluate_all(
            custody, "E7 cheap reason", "E7", "lift_record_present",
            cheap_reason, False)
        missing_activation = ENVELOPE_POSITIVES["E7"].replace(
            "LIFT_DESTINATION=reusable-skill-or-command",
            "LIFT_DESTINATION=checker")
        evaluate_all(
            custody, "E7 mechanical without activation", "E7",
            "activation_verified", missing_activation, False)

        e9_restart = ENVELOPE_POSITIVES["E9"].replace(
            "AUDIT_RESTART=false", "AUDIT_RESTART=true")
        evaluate_all(
            custody, "E9 restart", "E9", "no_full_restart",
            e9_restart, False)
        e9_owner = ENVELOPE_POSITIVES["E9"].replace(
            "OWNER_JUDGMENT=preserved-verbatim",
            "OWNER_JUDGMENT=recomputed")
        evaluate_all(
            custody, "E9 owner recomputed", "E9",
            "owner_judgment_preserved", e9_owner, False)

        for fixture_id in ENVELOPE_POSITIVES:
            fixture = load_fixture(fixture_id)
            check(
                f"{fixture_id} acceptance schema v2",
                fixture["matrix_acceptance"]["schema"] ==
                "implementaudit-candidate-matrix-acceptance-v2" and
                set(fixture["matrix_acceptance"]["properties"]) == {
                    prop["name"] for prop in fixture["properties"]})



def check(name: str, condition: bool) -> None:
    print(f"  [{'OK' if condition else 'XX'}] {name}")
    if not condition:
        failures.append(name)


def load_fixture(fixture_id: str) -> dict:
    return json.loads(
        (HERE / "fixtures" / fixture_id / "fixture.json").read_text(
            encoding="utf-8"))


def test_materialized_fixtures() -> None:
    try:
        setup = importlib.import_module("candidate_matrix_fixture_setup")
    except ImportError:
        check("B1 materialized live state", False)
        check("E9 materialized live state", False)
        return
    import adapters

    with tempfile.TemporaryDirectory(
            prefix="matrix-shared-cause-fixture-") as tmp:
        for fixture_id in ("B1", "E9"):
            work = pathlib.Path(tmp) / fixture_id
            work.mkdir()
            repo = pathlib.Path(
                adapters.seed_fixture_repo(fixture_id, str(work)))
            setup.prepare_fixture(
                fixture_id, repo, ROOT,
                load_fixture(fixture_id).get("matrix_precondition"))
            observed = setup.validate_fixture(
                fixture_id, repo, ROOT,
                load_fixture(fixture_id).get("matrix_precondition"))
            check(f"{fixture_id} materialized live state", observed is True)


def test_e10_composed_quarantine() -> None:
    try:
        matrix_host = importlib.import_module("candidate_matrix_host")
    except ImportError:
        check("E10 composed credential quarantine", False)
        return

    sentinel = (
        "eyJub25zZWNyZXRmaXh0dXJlc2VudGluZWwi."
        "bm9uc2VjcmV0cGF5bG9hZA."
        "bm9uc2VjcmV0c2lnbmF0dXJl")

    class SentinelAdapter(matrix_host.MatrixCodexAdapter):
        def collect_raw_stream(self, repo, outcome):
            return None

        def parse_events(self, out):
            return [{"role": "assistant", "content": "clean scored output"}]

        def resolve_model(self, out):
            self.models_observed = [{"model": "gpt-5.6-luna"}]
            return "gpt-5.6-luna"

        def check_policy(self, repo):
            self.policy_resolved = {}

        def post_checks(self, out):
            return None

    with tempfile.TemporaryDirectory(
            prefix="matrix-shared-cause-e10-") as tmp:
        adapter = SentinelAdapter(
            codex_home=os.path.join(tmp, "codex-home"), formal=False)
        os.makedirs(adapter.codex_home)
        adapter.host_argv_template = [
            sys.executable, "-c",
            "import sys;sys.stdout.write(sys.argv[1])", sentinel]
        adapter.timeout_s = 5
        adapter.preflight = lambda: None
        os.makedirs(os.path.join(tmp, "custody"))
        os.makedirs(os.path.join(tmp, "work"))
        result = adapter.run_mission(
            "E10", os.path.join(tmp, "custody"), "attempt-14-E10",
            os.path.join(tmp, "work"), _test_gate=lambda: None)
        run_root = pathlib.Path(tmp) / "custody" / "attempt-14-E10"
        terminal = json.loads(
            (run_root / "terminal.json").read_text(encoding="utf-8"))
        check(
            "E10 composed credential quarantine",
            result.kind == "invalid"
            and "credential pattern" in result.detail
            and "custody record" not in result.detail
            and terminal["kind"] == "invalid"
            and terminal["spawned"] is True
            and "credential pattern" in terminal["detail"]
            and "custody record" not in terminal["detail"]
            and (run_root / "run-intent.json").is_file()
            and (run_root / "process-started.json").is_file()
            and (run_root / "quarantine-raw" / "host-stdout.raw").is_file()
            and not (run_root / "host-stdout.raw").exists())


def main() -> int:
    test_structured_envelope_contract()
    test_raw_response_boundary()
    test_final_answer_identity()
    test_b1_write_allowlist_and_capture_profiles()
    test_universal_capture_producer_consumer_sentinel()
    test_absent_evidence_official_contract()
    test_e2a_model_portable_acceptance_and_evidence_contract()
    test_free_text_acceptance_retained()
    test_envelope_semantics_all_paths()
    test_materialized_fixtures()
    test_e10_composed_quarantine()
    if failures:
        print("candidate matrix shared cause: FAIL")
        for name in failures:
            print("  -", name)
        return 1
    print("candidate matrix shared cause: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
