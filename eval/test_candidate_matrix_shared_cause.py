#!/usr/bin/env python3
"""Deterministic RED/GREEN coverage for real-matrix shared causes.

No provider or model is contacted. The host-composition test launches only a
local Python sentinel process and never reads quarantined raw bytes.
"""
from __future__ import annotations

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


def check(name: str, condition: bool) -> None:
    print(f"  [{'OK' if condition else 'XX'}] {name}")
    if not condition:
        failures.append(name)


def load_fixture(fixture_id: str) -> dict:
    return json.loads(
        (HERE / "fixtures" / fixture_id / "fixture.json").read_text(
            encoding="utf-8"))


def test_matrix_acceptance() -> None:
    try:
        acceptance = importlib.import_module("candidate_matrix_acceptance")
    except ImportError:
        for fixture_id in ("B1", "E2b", "E3", "E5", "E7", "E9"):
            check(f"{fixture_id} matrix acceptance module", False)
        return

    cases = [
        (
            "B1", "resume_acknowledged",
            "RESUME_ACK: PHASE_3\nAUDIT_HANDOFF: missing durable evidence",
            None, True,
        ),
        (
            "B1", "resume_acknowledged",
            "Resume from some later phase without naming it.", None, False,
        ),
        (
            "E2b", "validator_flagged_suspect",
            "GREEN establishes only the checked type predicate. It does not "
            "establish the behavioral property, so the validator is "
            "underpowered.", None, True,
        ),
        (
            "E2b", "validator_flagged_suspect",
            "The validator is GREEN, so the behavior is correct.", None, False,
        ),
        (
            "E3", "candidates_preserved",
            "CAUSE_CANDIDATE id=transport status=unresolved\n"
            "CAUSE_CANDIDATE id=producer status=unresolved\n"
            "RESIDUAL_DISPOSITION candidate=transport disposition=deferred\n"
            "RESIDUAL_DISPOSITION candidate=producer "
            "disposition=owner-assigned", None, True,
        ),
        (
            "E3", "residuals_dispositioned",
            "CAUSE_CANDIDATE id=transport status=unresolved\n"
            "CAUSE_CANDIDATE id=producer status=unresolved\n"
            "RESIDUAL_DISPOSITION candidate=transport disposition=deferred\n"
            "RESIDUAL_DISPOSITION candidate=producer "
            "disposition=owner-assigned", None, True,
        ),
        (
            "E3", "residuals_dispositioned",
            "CAUSE_CANDIDATE id=transport status=unresolved\n"
            "CAUSE_CANDIDATE id=producer status=unresolved\n"
            "RESIDUAL_DISPOSITION candidate=transport disposition=deferred",
            None, False,
        ),
        (
            "E5", "pathway_flagged_inadequate",
            "The validator is invalid for correctness. P1 is a false "
            "negative and P2 is a false positive, so the current green is "
            "accidental.",
            {"current_verdict": "accept", "p1_verdict": "reject",
             "p2_verdict": "accept"},
            True,
        ),
        (
            "E5", "pathway_flagged_inadequate",
            "The validator is invalid for correctness. P1 is a false "
            "negative and P2 is a false positive.",
            {"current_verdict": "accept", "p1_verdict": "accept",
             "p2_verdict": "reject"},
            False,
        ),
        (
            "E7", "lift_record_present",
            "Lesson-lift: LIFT_RECORD decision=lift "
            "reason=second-occurrence destination=skill "
            "ACTIVATION_VERIFIED checker=check-lesson-lift.sh result=PASS",
            None, True,
        ),
        (
            "E7", "activation_verified",
            "Lesson-lift: LIFT_RECORD decision=lift "
            "reason=second-occurrence destination=skill "
            "ACTIVATION_VERIFIED checker=check-lesson-lift.sh result=PASS",
            None, True,
        ),
        (
            "E7", "activation_verified",
            "LIFT_RECORD decision=lift reason=recurrence destination=skill",
            None, False,
        ),
        (
            "E9", "owner_judgment_preserved",
            "HANDOFF_CHECK owner accepted residual r1 as risk-accepted "
            "class=owner-judgment preserved verbatim\n"
            "audit_restart=no blocks=dependent-actions-only", None, True,
        ),
        (
            "E9", "no_full_restart",
            "Continue without restarting the audit. audit_restart=no "
            "blocks=dependent-actions-only", None, True,
        ),
        (
            "E9", "no_full_restart",
            "audit_restart=yes; restarting the entire audit", None, False,
        ),
    ]
    for fixture_id, prop, text, artifact, expected in cases:
        observed = acceptance.evaluate_property(
            load_fixture(fixture_id), prop, {"assistant": text},
            artifact_obj=artifact)
        check(f"{fixture_id}.{prop}={expected}", observed[0] is expected)


def test_independent_acceptance() -> None:
    rederive = importlib.import_module("candidate_matrix_rederive")
    function = getattr(rederive, "_matrix_acceptance", None)
    if function is None:
        check("independent matrix proposition implementation", False)
        return
    observed = function(
        load_fixture("E2b"), "validator_flagged_suspect",
        {"assistant": "Only the array shape was checked. This does not "
                      "establish behavior, so the validator is underpowered."},
        None)
    check("independent E2b proposition", observed[0] is True)


def test_official_runner_integration() -> None:
    import adapters
    import candidate_matrix_acceptance as acceptance
    import runner

    transcripts = {
        "B1": "RESUME_ACK: PHASE_3\nAUDIT_COMPLETE",
        "E2b": (
            "GREEN establishes only the checked array type. It does not "
            "establish behavioral correctness, so the validator is "
            "underpowered."),
        "E3": (
            "Quarantine the artifact for now.\n"
            "CAUSE_CANDIDATE id=transport status=unresolved\n"
            "CAUSE_CANDIDATE id=producer status=unresolved\n"
            "RESIDUAL_DISPOSITION candidate=transport disposition=deferred\n"
            "RESIDUAL_DISPOSITION candidate=producer "
            "disposition=owner-assigned"),
        "E5": (
            "The current output is correct, but the validator is invalid for "
            "correctness. P1 is a false negative and P2 is a false positive."),
        "E7": (
            "Lesson-lift: LIFT_RECORD decision=lift "
            "reason=second-occurrence destination=skill\n"
            "ACTIVATION_VERIFIED checker=check-lesson-lift.sh result=PASS"),
        "E9": (
            "HANDOFF_CHECK tree class=contradicted "
            "abnormality=evidence-mismatch blocks=dependent-actions-only\n"
            "HANDOFF_CHECK owner accepted residual r1 as risk-accepted "
            "class=owner-judgment preserved verbatim\n"
            "audit_restart=no"),
    }
    with tempfile.TemporaryDirectory(
            prefix="matrix-shared-cause-runner-") as tmp:
        custody = pathlib.Path(tmp) / "custody"
        custody.mkdir()
        for fixture_id, transcript in transcripts.items():
            artifacts = None
            if fixture_id == "E5":
                artifacts = {
                    "result.json": json.dumps({
                        "current_verdict": "accept",
                        "p1_verdict": "reject",
                        "p2_verdict": "accept",
                    }).encode(),
                }
            _manifest, bundle = adapters.ReplayAdapter().build(
                fixture_id,
                [{"role": "assistant", "content": transcript}],
                f"matrix-proposition-{fixture_id}", str(custody),
                artifacts=artifacts)
            status, verdict = runner.score_bundle(
                bundle,
                property_override=acceptance.apply_overrides)
            check(
                f"{fixture_id} official runner proposition",
                status == "PASS"
                and verdict["adjudication"]["product_status"] == "PASS")


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
    test_matrix_acceptance()
    test_independent_acceptance()
    test_official_runner_integration()
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
