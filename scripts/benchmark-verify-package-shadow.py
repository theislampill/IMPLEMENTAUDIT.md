#!/usr/bin/env python3
"""Reproducible local benchmark for the non-authoritative shadow verifier."""

from __future__ import annotations

import argparse
import importlib.util
import json
import platform
import statistics
import sys
import tempfile
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ENGINE_PATH = ROOT / "scripts" / "verify-package-shadow.py"
FIXTURE = ROOT / "tests" / "fixtures" / "verify-package-shadow" / "check.py"


def load_engine():
    spec = importlib.util.spec_from_file_location("verify_package_shadow", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load engine from {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def make_check(
    *,
    order: int,
    check_id: str,
    status: str,
    input_path: Path,
    log_path: Path,
    delay_seconds: float,
    dependencies: list[str] | None = None,
) -> dict:
    argv = [
        sys.executable,
        str(FIXTURE),
        "--id",
        check_id,
        "--status",
        status,
        "--log",
        str(log_path),
    ]
    if status == "sleep":
        argv.extend(["--seconds", str(delay_seconds)])
    return {
        "applicability": {"mode": "always"},
        "argv": argv,
        "checkpoint_policy": {"mode": "exact_declared_inputs"},
        "dependencies": dependencies or [],
        "environment": [],
        "id": check_id,
        "implementation_sources": [str(FIXTURE)],
        "input_contract": {"mode": "explicit", "paths": [str(input_path)]},
        "kind": "command",
        "material_tools": [sys.executable],
        "order": order,
        "output_contract": {"mode": "explicit", "paths": []},
    }


def timed_run(engine, registry: dict, options) -> tuple[object, float]:
    started = time.perf_counter()
    report = engine.run_shadow(registry, options)
    return report, time.perf_counter() - started


def run_trial(engine, root: Path, delay_seconds: float) -> dict:
    inputs = root / "inputs"
    inputs.mkdir(parents=True)
    input_paths: list[Path] = []
    for index in range(8):
        path = inputs / f"check-{index}.txt"
        path.write_text("v1\n", encoding="utf-8")
        input_paths.append(path)

    checkpoint_dir = root / "checkpoints"
    all_pass_log = root / "all-pass.log"
    all_pass_checks = [
        make_check(
            order=index,
            check_id=f"check-{index}",
            status="sleep",
            input_path=input_paths[index],
            log_path=all_pass_log,
            delay_seconds=delay_seconds,
        )
        for index in range(8)
    ]
    all_pass_registry = {"authority": "NONE", "checks": all_pass_checks}
    fresh, fresh_time = timed_run(
        engine,
        all_pass_registry,
        engine.RunOptions(
            root,
            root / "fresh-evidence",
            30,
            "FRESH",
            checkpoint_dir=checkpoint_dir,
        ),
    )
    if fresh.primary_failures or fresh.infrastructure_errors:
        raise RuntimeError("fresh benchmark fixture did not PASS")

    input_paths[5].write_text("v2\n", encoding="utf-8")
    input_paths[7].write_text("v2\n", encoding="utf-8")
    resumed, resumed_time = timed_run(
        engine,
        all_pass_registry,
        engine.RunOptions(
            root,
            root / "resume-evidence",
            30,
            "RESUME",
            checkpoint_dir=checkpoint_dir,
        ),
    )
    if resumed.primary_failures or resumed.infrastructure_errors:
        raise RuntimeError("resume benchmark fixture did not PASS")

    frontier_log = root / "frontier.log"
    frontier_statuses = ["sleep", "fail", "sleep", "sleep", "fail", "sleep", "fail", "sleep"]
    frontier_checks = [
        make_check(
            order=index,
            check_id=f"frontier-{index}",
            status=status,
            input_path=input_paths[index],
            log_path=frontier_log,
            delay_seconds=delay_seconds,
            dependencies=["frontier-1"] if index == 2 else [],
        )
        for index, status in enumerate(frontier_statuses)
    ]
    frontier, frontier_time = timed_run(
        engine,
        {"authority": "NONE", "checks": frontier_checks},
        engine.RunOptions(root, root / "frontier-evidence", 30, "KEEP_GOING"),
    )
    if frontier.primary_failures != ["frontier-1", "frontier-4", "frontier-6"]:
        raise RuntimeError("keep-going benchmark did not expose expected failures")
    if frontier.blocked_checks != ["frontier-2"]:
        raise RuntimeError("keep-going benchmark did not block expected dependent")

    return {
        "blocked_checks_keep_going": len(frontier.blocked_checks),
        "checkpoint_validation_overhead_seconds": resumed.checkpoint_validation_seconds,
        "checkpoints_invalidated": len(resumed.checkpoints_invalidated),
        "checkpoints_reused": len(resumed.checkpoints_reused),
        "checks_executed_fresh": len(fresh.checks_executed),
        "checks_executed_keep_going": len(frontier.checks_executed),
        "checks_executed_resumed": len(resumed.checks_executed),
        "fresh_full_run_time_seconds": fresh_time,
        "keep_going_discovery_time_seconds": frontier_time,
        "primary_failures_discovered_keep_going": len(frontier.primary_failures),
        "resumed_run_time_seconds": resumed_time,
    }


def median_payload(trials: list[dict], delay_seconds: float) -> dict:
    timing_keys = (
        "checkpoint_validation_overhead_seconds",
        "fresh_full_run_time_seconds",
        "keep_going_discovery_time_seconds",
        "resumed_run_time_seconds",
    )
    payload = {
        "authority": "NONE",
        "delay_seconds_per_passing_check": delay_seconds,
        "host": {
            "platform": platform.platform(),
            "python": platform.python_version(),
        },
        "schema": "implementaudit.verify-package-shadow.benchmark.v1",
        "trial_records": trials,
        "trials": len(trials),
    }
    for key in timing_keys:
        payload[key] = statistics.median(item[key] for item in trials)
    for key in (
        "blocked_checks_keep_going",
        "checkpoints_invalidated",
        "checkpoints_reused",
        "checks_executed_fresh",
        "checks_executed_keep_going",
        "checks_executed_resumed",
        "primary_failures_discovered_keep_going",
    ):
        values = {item[key] for item in trials}
        if len(values) != 1:
            raise RuntimeError(f"non-deterministic benchmark work count: {key}")
        payload[key] = values.pop()
    resumed = payload["resumed_run_time_seconds"]
    payload["measured_speedup_fresh_over_resume"] = (
        payload["fresh_full_run_time_seconds"] / resumed if resumed else None
    )
    return payload


def run_representative_real_subset(engine) -> dict:
    checks = [
        {
            "applicability": {"mode": "always"},
            "argv": ["bash", "scripts/generate-readme-diagrams.sh", "--check"],
            "checkpoint_policy": {"mode": "exact_declared_inputs"},
            "dependencies": [],
            "environment": [],
            "id": "script.generate-readme-diagrams",
            "implementation_sources": ["scripts/generate-readme-diagrams.sh"],
            "input_contract": {
                "mode": "explicit",
                "paths": [
                    "README.md",
                    "docs/diagrams/tooling-architecture.mmd",
                    "docs/diagrams/invocation-modes.mmd",
                    "docs/diagrams/execution-spine.mmd",
                ],
            },
            "kind": "command",
            "material_tools": ["bash", "python"],
            "order": 0,
            "output_contract": {"mode": "explicit", "paths": []},
        },
        {
            "applicability": {"mode": "always"},
            "argv": ["bash", "scripts/check-readme-toc.sh"],
            "checkpoint_policy": {"mode": "exact_declared_inputs"},
            "dependencies": [],
            "environment": [],
            "id": "script.check-readme-toc",
            "implementation_sources": ["scripts/check-readme-toc.sh"],
            "input_contract": {"mode": "explicit", "paths": ["README.md"]},
            "kind": "command",
            "material_tools": ["bash", "python"],
            "order": 1,
            "output_contract": {"mode": "explicit", "paths": []},
        },
    ]
    registry = {"authority": "NONE", "checks": checks}
    with tempfile.TemporaryDirectory(prefix="verify-package-shadow-real-") as tmp:
        evidence_root = Path(tmp)
        checkpoint_dir = evidence_root / "checkpoints"
        fresh, fresh_time = timed_run(
            engine,
            registry,
            engine.RunOptions(
                ROOT,
                evidence_root / "fresh",
                30,
                "FRESH",
                checkpoint_dir=checkpoint_dir,
            ),
        )
        resumed, resumed_time = timed_run(
            engine,
            registry,
            engine.RunOptions(
                ROOT,
                evidence_root / "resumed",
                30,
                "RESUME",
                checkpoint_dir=checkpoint_dir,
            ),
        )
    if fresh.primary_failures or fresh.infrastructure_errors:
        raise RuntimeError("representative real fresh subset did not PASS")
    if resumed.primary_failures or resumed.infrastructure_errors:
        raise RuntimeError("representative real resume subset did not PASS")
    return {
        "authority": "NONE",
        "checkpoint_validation_overhead_seconds": resumed.checkpoint_validation_seconds,
        "checkpoints_reused": len(resumed.checkpoints_reused),
        "checks": [check["id"] for check in checks],
        "checks_executed_fresh": len(fresh.checks_executed),
        "checks_executed_resumed": len(resumed.checks_executed),
        "fresh_primary_failures": list(fresh.primary_failures),
        "fresh_time_seconds": fresh_time,
        "measured_speedup_fresh_over_resume": (
            fresh_time / resumed_time if resumed_time else None
        ),
        "resume_primary_failures": list(resumed.primary_failures),
        "resume_time_seconds": resumed_time,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--trials", type=int, default=3)
    parser.add_argument("--delay-seconds", type=float, default=0.08)
    args = parser.parse_args(argv)
    if args.trials < 1 or args.delay_seconds < 0:
        parser.error("trials must be positive and delay must be non-negative")

    engine = load_engine()
    trial_records: list[dict] = []
    for _ in range(args.trials):
        with tempfile.TemporaryDirectory(prefix="verify-package-shadow-benchmark-") as tmp:
            trial_records.append(run_trial(engine, Path(tmp), args.delay_seconds))
    payload = median_payload(trial_records, args.delay_seconds)
    payload["representative_real_subset"] = run_representative_real_subset(engine)
    engine._write_json_atomic(args.output, payload)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
