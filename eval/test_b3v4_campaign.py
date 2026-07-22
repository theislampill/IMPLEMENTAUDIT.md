#!/usr/bin/env python3
"""Deterministic tests for the serialized B3-v4 campaign driver."""
from __future__ import annotations

import importlib.util
import hashlib
import json
import pathlib
import tempfile

from test_b3v4_freeze import valid_packet


HERE = pathlib.Path(__file__).resolve().parent
DRIVER = HERE / "b3v4_campaign.py"


def load_driver():
    spec = importlib.util.spec_from_file_location("b3v4campaign", DRIVER)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def write_packet(root):
    path = pathlib.Path(root) / "intent.json"
    path.write_text(json.dumps(valid_packet(), sort_keys=True), encoding="utf-8")
    return path


def make_driver(module, root, executor):
    packet = write_packet(root)
    return module.CampaignDriver(
        packet_path=packet,
        repo_root=HERE.parent,
        campaign_root=pathlib.Path(root) / "campaign",
        candidate_checkout=pathlib.Path(root) / "candidate",
        control_checkout=pathlib.Path(root) / "control",
        runtime_root=pathlib.Path(root) / "runtime",
        mission_executor=executor,
        execution_mode="test",
        live_validator=lambda packet, repo: packet,
        identity_validator=lambda packet, **paths: None,
    )


def expect_error(fragment, fn):
    try:
        fn()
    except ValueError as exc:
        assert fragment in str(exc), str(exc)
    else:
        raise AssertionError(f"expected ValueError containing {fragment!r}")


def official_verdict(context, status="PASS", *, product="PASS", host="PASS",
                     resolved_model=None, substituted=False):
    properties = {
        f"property-{index}": {"state": "PASS", "pass": True,
                               "evidence": "synthetic retained evidence"}
        for index in range(6)
    }
    return {
        "schema": "implementaudit-eval-verdict-v3", "status": status,
        "model_resolved": resolved_model or context.expected_model,
        "model_substitution": substituted,
        "properties": properties,
        "host_safety": {"schema": "implementaudit-host-safety-v1",
                        "status": host, "findings": []},
        "adjudication": {
            "schema": "implementaudit-eval-adjudication-v1",
            "product_status": product, "host_status": host,
            "overall_status": status, "property_evidence_complete": True,
            "all_required_properties_true": product == "PASS",
        },
    }


def scored_outcome(context, status="PASS", *, resolved_model=None,
                   product="PASS", host="PASS", substituted=False):
    resolved = resolved_model or context.expected_model
    return {"overall_status": status, "resolved_model": resolved,
            "host_run_root": "mock-host-run",
            "official_verdict": official_verdict(
                context, status, product=product, host=host,
                resolved_model=resolved, substituted=substituted)}


def main():
    module = load_driver()

    with tempfile.TemporaryDirectory(prefix="b3v4-campaign-custody-") as tmp:
        def contradictory_executor(context):
            verdict = official_verdict(
                context, "INVALID", product="INCOMPLETE", host="INVALID")
            return {"overall_status": "PASS",
                    "resolved_model": context.expected_model,
                    "host_run_root": "mock-host-run",
                    "official_verdict": verdict}

        driver = make_driver(module, tmp, contradictory_executor)
        result = driver.run_next()
        attempt = pathlib.Path(tmp) / "campaign" / \
            "attempt-000-L-candidate-r1"
        verdict_path = attempt / "official-verdict.json"
        assert result["official_overall_status"] == "INVALID", result
        assert result["overall_status"] == "INVALID", result
        assert verdict_path.is_file(), "official verdict custody missing"
        assert result["official_verdict_sha256"] == hashlib.sha256(
            verdict_path.read_bytes()).hexdigest()

    with tempfile.TemporaryDirectory(prefix="b3v4-campaign-") as tmp:
        expect_error("cannot replace", lambda: module.CampaignDriver(
            packet_path=write_packet(tmp), repo_root=HERE.parent,
            campaign_root=pathlib.Path(tmp) / "campaign",
            candidate_checkout=pathlib.Path(tmp) / "candidate",
            control_checkout=pathlib.Path(tmp) / "control",
            runtime_root=pathlib.Path(tmp) / "runtime",
            mission_executor=lambda context: {}))

    with tempfile.TemporaryDirectory(prefix="b3v4-campaign-") as tmp:
        observed = []

        def pass_once(context):
            status = context.attempt_root / "attempt-status.json"
            assert status.is_file(), "pre-spawn attempt status missing"
            observed.append((context.mission["index"], context.mission["config"],
                             context.mission["arm"], context.mission["rep"]))
            return scored_outcome(context)

        driver = make_driver(module, tmp, pass_once)
        first = driver.run_next()
        second = driver.run_next()
        assert first["mission_index"] == 0 and second["mission_index"] == 1
        assert observed == [(0, "L", "candidate", 1),
                            (1, "L", "control", 1)]
        first_root = pathlib.Path(tmp) / "campaign" / \
            "attempt-000-L-candidate-r1"
        assert json.loads((first_root / "attempt-terminal.json").read_text(
            encoding="utf-8"))["overall_status"] == "PASS"

        # A prior nonterminal attempt is preserved and blocks all progression.
        (pathlib.Path(tmp) / "campaign" /
         "attempt-001-L-control-r1" / "attempt-terminal.json").unlink()
        expect_error("prior attempt is nonterminal", driver.run_next)
        assert len(observed) == 2

    with tempfile.TemporaryDirectory(prefix="b3v4-campaign-") as tmp:
        def invalid_once(context):
            return {"overall_status": "INVALID",
                    "resolved_model": context.expected_model,
                    "host_run_root": "mock-host-run"}

        driver = make_driver(module, tmp, invalid_once)
        result = driver.run_next()
        assert result["overall_status"] == "INVALID"
        expect_error("prior attempt stopped campaign", driver.run_next)

    with tempfile.TemporaryDirectory(prefix="b3v4-campaign-drift-") as tmp:
        driver = make_driver(module, tmp, scored_outcome)
        driver.run_next()
        first = pathlib.Path(tmp) / "campaign" / \
            "attempt-000-L-candidate-r1"
        verdict_path = first / "official-verdict.json"
        verdict = json.loads(verdict_path.read_text(encoding="utf-8"))
        verdict["reason"] = "post-terminal drift"
        verdict_path.write_text(json.dumps(verdict), encoding="utf-8")
        expect_error("official verdict custody drift", driver.run_next)

    with tempfile.TemporaryDirectory(prefix="b3v4-campaign-") as tmp:
        order = []

        def collect_order(context):
            order.append((context.mission["config"], context.mission["arm"],
                          context.mission["rep"]))
            return scored_outcome(context)

        driver = make_driver(module, tmp, collect_order)
        for _ in range(12):
            driver.run_next()
        assert order == [tuple(row) for row in module.freeze.PLAN]
        expect_error("all 12 attempts", driver.run_next)

    with tempfile.TemporaryDirectory(prefix="b3v4-campaign-") as tmp:
        def substitute(context):
            return scored_outcome(
                context, "INVALID", resolved_model="substituted-model",
                product="PASS", host="INVALID", substituted=True)

        driver = make_driver(module, tmp, substitute)
        result = driver.run_next()
        assert result["overall_status"] == "INVALID"
        assert result["stop_reason"] == "model-substitution"

    with tempfile.TemporaryDirectory(prefix="b3v4-campaign-") as tmp:
        driver = make_driver(module, tmp, lambda context: {
            "overall_status": "ERROR", "resolved_model": None,
            "host_run_root": "mock-host-run"})
        result = driver.run_next()
        assert result["overall_status"] == "ERROR"
        assert result["stop_reason"] == "invalid-or-error-halts-campaign"

    with tempfile.TemporaryDirectory(prefix="b3v4-campaign-") as tmp:
        driver = make_driver(
            module, tmp, scored_outcome)
        driver.run_next()
        packet = pathlib.Path(tmp) / "intent.json"
        changed = json.loads(packet.read_text(encoding="utf-8"))
        changed["acceptance_rule"] += " (drift)"
        packet.write_text(json.dumps(changed), encoding="utf-8")
        expect_error("frozen packet drift", driver.run_next)

    print("test_b3v4_campaign: ok")


if __name__ == "__main__":
    main()
