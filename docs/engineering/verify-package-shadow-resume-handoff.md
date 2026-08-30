# Verify-Package Shadow Keep-Going/Resume Engineering Handoff

```text
WORKTREE=C:\workspace\ai\improveimplementaudit\IMPLEMENTAUDIT-verify-package-shadow-resume
BRANCH=experiment/verify-package-shadow-resume
BASE_HEAD=62507de00e16cc2ada0e7546273988c387a20390
FINAL_HEAD=RESOLVE_FROM_ORIGIN_EXPERIMENT_BRANCH_CONTAINING_THIS_HANDOFF
MAIN_CAMPAIGN_AUTHORITY=NONE
HBASE_AUTHORITY=NONE
RELEASE_AUTHORITY=NONE
SHADOW_MODE_AUTHORITY=NONE
CANONICAL_VERIFY_PACKAGE_REMAINS_ORACLE=YES
```

## Current verifier architecture

The base canonical verifier is a 780-line fail-fast Bash program with one large
inline preflight and 104 top-level Bash invocations: 24 checker scripts, 78
registered shell tests, the validation-registry meta-gate, and release-asset
check mode. The shadow Strangler-Fig keeps that file unchanged and adds a
digest-bound 105-node registry (one approved composite plus 104 discrete
commands), a deterministic keep-going scheduler, a fail-closed checkpoint
store, and a machine-readable authority-NONE report.

```text
CURRENT_VERIFIER_ARCHITECTURE=CANONICAL_FAIL_FAST_BASH_PLUS_NONAUTHORITATIVE_SHADOW_ORCHESTRATOR
CHECK_REGISTRY=105_EXACT_NODES_1_COMPOSITE_104_COMMANDS
DEPENDENCY_GRAPH=ZERO_LIVE_HARD_RESULT_EDGES
DEPENDENCY_EDGE_JUSTIFICATIONS=NO_DOWNSTREAM_CURRENTLY_REQUIRES_ANOTHER_SCHEDULED_RESULT_TO_PRODUCE_TRUSTWORTHY_EVIDENCE
REJECTED_EDGE=generate-readme-diagrams_TO_verify-readme-diagrams-rendered_BECAUSE_DOWNSTREAM_SELF_EXECUTES_PARITY_CHECK
SYNTHETIC_BLOCKING_CONTROL=B_FAIL_TO_C_BLOCKED
```

## Implemented product

```text
KEEP_GOING_IMPLEMENTED=YES
CHECKPOINT_RESUME_IMPLEMENTED=YES
SHADOW_MODE_IMPLEMENTED=YES
ENGINE=scripts/verify-package-shadow.py
ENGINE_BYTES=53318
ENGINE_SHA256=b57f2ce6441bf31ecd7913064d76d1f6815968b6bb9acc6d07a7c726cdee648f
REGISTRY=scripts/verify-package-shadow-registry.json
REGISTRY_BYTES=901
REGISTRY_SHA256=2e5b9b45589684b089dc67f45ed3c4f2e2025b226bcd8f255687f9f60430723b
BENCHMARK_HARNESS=scripts/benchmark-verify-package-shadow.py
BENCHMARK_HARNESS_BYTES=11349
BENCHMARK_HARNESS_SHA256=3d5049bd37681599c383b3d8165b48d8aa0258af3a3a75aed92dd809528c454f
```

## Checkpoint validity and invalidation

```text
CHECKPOINT_VALIDITY_CONTRACT=EXACT_ADMITTED_PASS_ONLY
INVALIDATION_ALGORITHM=RECOMPUTE_CHECK_LOCAL_CANONICAL_IDENTITY_AND_COMPARE_EVERY_MATERIAL_FIELD
FAILURE_FRONTIER_SCHEMA=implementaudit.verify-package-shadow.report.v1
CHECKPOINT_SCHEMA=implementaudit.verify-package-shadow.checkpoint.v2
ENGINE_SEMANTICS=implementaudit.verify-package-shadow.keep-going.v2
```

A reusable PASS binds the exact check definition, implementation manifest,
declared input/read surface, declared generated artifacts, dependency PASS
fingerprints, canonical static environment, check-specific environment,
material tool path/version, applicability, engine semantics, exit status, and
digest-bound stdout/stderr sidecars. Any missing, unreadable, corrupt,
incomplete, changed, unknown, unadmitted, or tampered field reruns. Only checks
with `{"mode":"exact_declared_inputs"}` are eligible; the live registry has
`CHECKPOINT_ENABLED_COUNT=0`.

## Files changed

```text
FILES_CHANGED=
docs/engineering/verify-package-shadow-benchmark.json
docs/engineering/verify-package-shadow-checkpoint-resume-milestone.md
docs/engineering/verify-package-shadow-keep-going-milestone.md
docs/engineering/verify-package-shadow-performance-milestone.md
docs/engineering/verify-package-shadow-resume-handoff.md
docs/reviews/verify-package-shadow-resume-review.md
docs/superpowers/plans/2026-08-30-verify-package-shadow-resume.md
docs/superpowers/specs/2026-08-30-verify-package-shadow-resume-design.md
scripts/benchmark-verify-package-shadow.py
scripts/verify-package-shadow-registry.json
scripts/verify-package-shadow.py
tests/fixtures/verify-package-shadow/canonical-verifier.sh
tests/fixtures/verify-package-shadow/check.py
tests/verify_package_shadow_test.py
```

## Evidence

```text
TESTS_ADDED=UNIT_INTEGRATION_NEGATIVE_ORACLE_RESUME_BENCHMARK
TEST_RESULTS=45_RUN_44_PASS_1_HOST_PRIVILEGE_SKIP
INDEPENDENT_REVIEW=NOT_PERFORMED_SIDECHAT_SUBAGENTS_FORBIDDEN
SERIAL_FRESH_CONTEXT_REVIEW=PASS_WITH_DOCUMENTED_ADMISSION_GAPS
ORACLE_EQUIVALENCE_RESULT=PASS_CONTROLLED_CLEAN_AND_FAILING_FIXTURES
LIVE_FULL_105_ORACLE_EQUIVALENCE_RESULT=NOT_CREDITED_SHARED_FIXED_RESOURCE_CONFLICT
RESUME_EQUIVALENCE_RESULT=PASS
FAIL_CLOSED_TEST_RESULT=PASS
```

The controlled failing oracle stopped at `script.alpha`; shadow execution
reported the same failure plus independent `test.charlie`, suppressing none.
The current progressive rendered-diagram check is typed NOT_APPLICABLE. A
representative real subset (`generate-readme-diagrams --check` and
`check-readme-toc`) passed fresh and resumed with two exact checkpoints reused.

## Performance

Machine-local median of three controlled trials:

```text
PERFORMANCE_BASELINE=FRESH_8_CHECKS_1.25197099999059_SECONDS
PERFORMANCE_ACCELERATED=RESUME_2_EXECUTED_6_REUSED_0.4008163000107743_SECONDS
MEASURED_SPEEDUP=3.123553108885382x
CHECKPOINT_VALIDATION_OVERHEAD=0.01600000000325963_SECONDS
KEEP_GOING_DISCOVERY=3_PRIMARY_FAILURES_1_BLOCKED_DEPENDENT_0.8441263000131585_SECONDS
```

Representative real two-check subset:

```text
REAL_SUBSET_FRESH=0.4998920000070939_SECONDS
REAL_SUBSET_RESUME=0.06329669999831822_SECONDS
REAL_SUBSET_REUSED=2_OF_2
REAL_SUBSET_SPEEDUP=7.8975997172107855x
```

These are local measurements, not a whole-package speed claim.

## Limitations and risk

```text
KNOWN_LIMITATIONS=SERIAL_SCHEDULER;ZERO_LIVE_CHECKPOINT_ADMISSIONS;DEFAULT_INVOCATION_ONLY;INCOMPLETE_NESTED_TOOL_DECLARATIONS;NO_FULL_LIVE_105_EQUIVALENCE_DURING_ACTIVE_HBASE
RESIDUAL_RISKS=FIXED_TMP_RESOURCE_COLLISION;LOCAL_UNSIGNED_CHECKPOINTS;SYMLINK_HOST_CONTROL_SKIPPED;NO_INDEPENDENT_REVIEW
SAFE_FOR_NONAUTHORITATIVE_SHADOW_USE=YES_WITH_EXCLUSIVE_FIXED_RESOURCE_WINDOW_AND_AUTHORITY_NONE
SAFE_FOR_AUTHORITATIVE_USE=NO_BY_DEFAULT
```

## Recommended future admission path

1. Wait for an exclusive fixed-resource window; do not overlap the live HBASE
   verifier or other canonical package runs.
2. Obtain an independent code review of the exact remote experiment commit.
3. Audit and admit per-check input/tool/environment/generated-output contracts
   incrementally; retain zero reuse for every unaudited check.
4. Run canonical and shadow once over the same immutable clean candidate,
   compare every reachable comparable result, and perform a residue census.
5. Use the shadow only as an authority-NONE preflight before one canonical
   verifier run.
6. Any authoritative migration remains a separate owner admission with new
   qualification evidence; do not infer it from this branch or handoff.

```text
CURRENT_V041_CAMPAIGN_DEPENDENCY=NO
HBASE_MAY_CONTINUE_IN_PARALLEL=YES
EXPERIMENT_PRODUCT_AUTHORITY=NONE
FUTURE_ADMISSION_REQUIRED_BEFORE_CANONICAL_USE=YES
DO_NOT_MERGE=YES
DO_NOT_INSTALL=YES
```
