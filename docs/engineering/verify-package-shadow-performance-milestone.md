# Verify-Package Shadow Performance Benchmark Milestone

```text
MILESTONE=PERFORMANCE_BENCHMARK
STATUS=PASS
AUTHORITY=NONE
MEASUREMENTS_MACHINE_LOCAL=YES
```

Reproduction command:

```powershell
python scripts/benchmark-verify-package-shadow.py `
  --output <path> `
  --trials 3 `
  --delay-seconds 0.08
```

The durable raw result is
`docs/engineering/verify-package-shadow-benchmark.json`.

## Synthetic controlled workload

Median of three trials on Windows 10 build 26200 with Python 3.11.9:

```text
FRESH_FULL_RUN_TIME=1.155562200001441 seconds
KEEP_GOING_DISCOVERY_TIME=0.7930094000039389 seconds
RESUMED_RUN_TIME=0.3338852000015322 seconds
CHECKS_EXECUTED_FRESH=8
CHECKS_EXECUTED_RESUMED=2
CHECKPOINTS_REUSED=6
CHECKPOINTS_INVALIDATED=2
PRIMARY_FAILURES_DISCOVERED_PER_KEEP_GOING_RUN=3
BLOCKED_DEPENDENTS=1
CHECKPOINT_VALIDATION_OVERHEAD=0.01600000000325963 seconds
MEASURED_FRESH_OVER_RESUME_SPEEDUP=3.4609566401749405x
```

## Representative current-verifier subset

Two current canonical commands with reviewed explicit input/tool contracts were
run fresh and then resumed without input changes:

```text
CHECKS=script.generate-readme-diagrams,script.check-readme-toc
FRESH_TIME=0.39229530000011437 seconds
RESUME_TIME=0.05961719999322668 seconds
CHECKS_EXECUTED_FRESH=2
CHECKS_EXECUTED_RESUMED=0
CHECKPOINTS_REUSED=2
MEASURED_FRESH_OVER_RESUME_SPEEDUP=6.580236912244863x
FRESH_PRIMARY_FAILURES=0
RESUME_PRIMARY_FAILURES=0
```

These are local measurements, not a whole-package performance claim. The live
105-node registry still admits zero checkpoints by default; the real subset is
a bounded benchmark registry embedded in the harness, not a promotion of those
contracts into canonical authority.
