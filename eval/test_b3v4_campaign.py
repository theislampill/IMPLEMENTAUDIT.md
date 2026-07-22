#!/usr/bin/env python3
"""Deterministic tests for the serialized B3-v4 campaign driver."""
from __future__ import annotations

import importlib.util
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


def main():
    module = load_driver()

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
            return {"overall_status": "PASS",
                    "resolved_model": context.expected_model,
                    "host_run_root": "mock-host-run"}

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

    with tempfile.TemporaryDirectory(prefix="b3v4-campaign-") as tmp:
        order = []

        def collect_order(context):
            order.append((context.mission["config"], context.mission["arm"],
                          context.mission["rep"]))
            return {"overall_status": "PASS",
                    "resolved_model": context.expected_model,
                    "host_run_root": "mock-host-run"}

        driver = make_driver(module, tmp, collect_order)
        for _ in range(12):
            driver.run_next()
        assert order == [tuple(row) for row in module.freeze.PLAN]
        expect_error("all 12 attempts", driver.run_next)

    with tempfile.TemporaryDirectory(prefix="b3v4-campaign-") as tmp:
        def substitute(context):
            return {"overall_status": "PASS",
                    "resolved_model": "substituted-model",
                    "host_run_root": "mock-host-run"}

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
            module, tmp, lambda context: {
                "overall_status": "PASS",
                "resolved_model": context.expected_model,
                "host_run_root": "mock-host-run"})
        driver.run_next()
        packet = pathlib.Path(tmp) / "intent.json"
        changed = json.loads(packet.read_text(encoding="utf-8"))
        changed["acceptance_rule"] += " (drift)"
        packet.write_text(json.dumps(changed), encoding="utf-8")
        expect_error("frozen packet drift", driver.run_next)

    print("test_b3v4_campaign: ok")


if __name__ == "__main__":
    main()
