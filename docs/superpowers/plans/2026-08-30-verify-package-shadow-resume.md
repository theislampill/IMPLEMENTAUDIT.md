# Verify-Package Shadow Keep-Going and Resume Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a non-authoritative shadow verifier that exposes the complete safe independent failure frontier and reuses only exactly applicable PASS checkpoints.

**Architecture:** A Python standard-library engine consumes a versioned JSON registry whose command population is mechanically bound to the canonical Bash verifier. The first milestone implements deterministic serial keep-going; the second adds exact-fingerprint PASS checkpoints and selective resume without changing the canonical oracle.

**Tech Stack:** Python 3 standard library, JSON, Git, POSIX shell commands executed by Git Bash, `unittest`.

**Spec:** `docs/superpowers/specs/2026-08-30-verify-package-shadow-resume-design.md`

## Global Constraints

- Base exactly `62507de00e16cc2ada0e7546273988c387a20390` in the approved isolated worktree and branch.
- `MAIN_CAMPAIGN_AUTHORITY=NONE`, `HBASE_AUTHORITY=NONE`, `RELEASE_AUTHORITY=NONE`.
- Canonical `scripts/verify-package.sh` remains the reference/oracle.
- Shadow mode always reports `AUTHORITY=NONE` and is non-authoritative.
- Do not merge, install, tag, release, publish, or modify active campaign surfaces.
- Use only Python's standard library; do not add dependencies.
- Keep initial scheduling serial and deterministic; do not add unsafe concurrency.
- Follow TDD: every production behaviour is preceded by a focused failing test.
- Do not commit; commit authority was not granted.
- Do not use subagents in this side conversation.

---

### Task 1: Registry extraction and drift guard

**Files:**
- Create: `tests/verify_package_shadow_test.py`
- Create: `tests/fixtures/verify-package-shadow/canonical-verifier.sh`
- Create: `scripts/verify-package-shadow.py`
- Create: `scripts/verify-package-shadow-registry.json`

**Interfaces:**
- Produces `load_registry(path: Path) -> Registry`.
- Produces `extract_canonical_commands(text: str, first_command: str) -> list[tuple[int, tuple[str, ...]]]`.
- Produces `validate_registry(registry: Registry, repo_root: Path) -> list[str]`.

- [ ] Write a unit test whose miniature canonical verifier contains a composite prefix and three Bash commands; assert exact order and argv extraction.
- [ ] Run `python -m unittest tests.verify_package_shadow_test.RegistryTests.test_extracts_exact_command_population -v` and confirm RED because the module is absent.
- [ ] Implement only registry dataclasses, JSON loading, and exact top-level `bash` command extraction.
- [ ] Run the focused test and confirm PASS.
- [ ] Add failing tests for changed canonical digest, missing command, reordered command, duplicate check ID, unknown dependency, and dependency cycle.
- [ ] Run the six tests and confirm their expected RED diagnostics.
- [ ] Implement fail-closed registry validation and deterministic topological validation.
- [ ] Populate the current registry with the approved composite node, all 104 exact command nodes, and the single generated-diagram result edge.
- [ ] Run the registry tests and `python scripts/verify-package-shadow.py validate-registry --repo-root .` and confirm PASS with 105 total nodes.

### Task 2: Keep-going scheduler and terminal report milestone

**Files:**
- Modify: `tests/verify_package_shadow_test.py`
- Modify: `scripts/verify-package-shadow.py`
- Create: `tests/fixtures/verify-package-shadow/check.py`

**Interfaces:**
- Produces `CheckStatus` with the five required status strings.
- Produces `run_shadow(registry: Registry, options: RunOptions) -> RunReport`.
- Produces `RunReport.to_json_dict() -> dict[str, object]`.

- [ ] Add a failing scheduler test with A PASS, B FAIL, C depending on B, D PASS, E FAIL, and F PASS; assert B/E are primary failures, C is blocked by B, and A/D/F run in logical order.
- [ ] Run the focused scheduler test and confirm RED because execution is absent.
- [ ] Implement serial deterministic execution, dependency blocking, per-check stdout/stderr evidence files, and ordered records.
- [ ] Run the focused scheduler test and confirm PASS.
- [ ] Add failing tests for missing executable, process-start error, timeout, explicit not-applicable result, and two independent failures after an earlier failure.
- [ ] Implement distinct infrastructure and applicability classification without stderr guesswork: preflight-declared tool absence, process exception, timeout, and exact registry-declared not-applicable exit/output contract.
- [ ] Add a failing JSON-schema projection test asserting ordered status arrays, blocked dependency map, earliest failure, complete frontier, work counters, and `authority == "NONE"`.
- [ ] Implement canonical JSON report writing through a temporary sibling followed by `os.replace`.
- [ ] Add an oracle test where canonical fail-fast reaches B and shadow reaches B plus independent E; assert the shadow includes every canonical demonstrated failure.
- [ ] Run `python -m unittest tests.verify_package_shadow_test -v` and confirm all milestone tests PASS.
- [ ] Freeze milestone evidence with `python scripts/verify-package-shadow.py validate-registry --repo-root .`, test count/output, `git diff --check`, and a milestone report under an untracked temporary directory.

### Task 3: Fail-closed checkpoint and selective resume

**Files:**
- Modify: `tests/verify_package_shadow_test.py`
- Modify: `scripts/verify-package-shadow.py`
- Modify: `scripts/verify-package-shadow-registry.json`

**Interfaces:**
- Produces `fingerprint_check(check: CheckSpec, context: FingerprintContext) -> FingerprintRecord`.
- Produces `load_checkpoint(path: Path) -> CheckpointDecision`.
- Produces `checkpoint_decision(check: CheckSpec, current: FingerprintRecord, stored: object) -> CheckpointDecision`.

- [ ] Add a failing test that reuses an unchanged PASS and executes zero commands on resume.
- [ ] Implement canonical JSON hashing and complete atomic PASS checkpoint storage.
- [ ] Add failing tests for relevant-input change, unrelated-input preservation under explicit scope, dependency fingerprint change, implementation-source change, corrupt JSON, incomplete record, material tool change, unknown applicability, and FAIL non-reuse.
- [ ] Implement path manifests for explicit files/globs and conservative tracked-tree fallback; include missing paths, symlinks, mode, size, and digest in canonical order.
- [ ] Implement dependency, tool, environment, applicability, engine, registry, command, and implementation fingerprints.
- [ ] Ensure every uncertain or invalid checkpoint reports a reason and reruns rather than reuses.
- [ ] Run the full unit suite and confirm all checkpoint controls PASS.

### Task 4: Fresh/resume and canonical-oracle integration evidence

**Files:**
- Modify: `tests/verify_package_shadow_test.py`
- Create: `tests/fixtures/verify-package-shadow/representative-registry.json`

**Interfaces:**
- Consumes the real engine CLI.
- Produces semantic comparison records for fresh, keep-going, resume, and canonical fail-fast modes.

- [ ] Add a failing resume-equivalence test: fresh and resumed runs over the same candidate must have identical semantic status/failure/block maps after removing execution-source and timing fields.
- [ ] Implement semantic normalisation for comparison output.
- [ ] Add clean and failing canonical-oracle scenarios using controlled fixture commands and assert no canonical demonstrated failure is suppressed.
- [ ] Add a corrupted-checkpoint CLI scenario and assert rerun plus fail-closed invalidation reason.
- [ ] Run `python -m unittest tests.verify_package_shadow_test -v` and confirm all equivalence tests PASS.
- [ ] Run the current registry drift guard against the exact real canonical verifier and record its digest and 105-node population.

### Task 5: Reproducible performance evidence

**Files:**
- Create: `scripts/benchmark-verify-package-shadow.py`
- Modify: `tests/verify_package_shadow_test.py`

**Interfaces:**
- Produces one JSON record containing fresh, keep-going, and resumed timings and work counters.

- [ ] Add a failing benchmark-schema test using short deterministic fixture delays.
- [ ] Implement a benchmark that runs one fresh all-pass fixture, one keep-going multi-failure fixture, and one resume fixture with a relevant and unrelated change.
- [ ] Record `fresh_full_run_time`, `keep_going_discovery_time`, `resumed_run_time`, executed/reused/invalidated counts, validation overhead, and primary failures per run.
- [ ] Run the benchmark three times and report median timings without claiming machine-independent performance.
- [ ] Run a representative real-check subset with exact registry/input identities when its runtime is bounded; otherwise record the exact blocker rather than substitute a claim.

### Task 6: Serial fresh-context review and final handoff

**Files:**
- Create: `docs/reviews/verify-package-shadow-resume-review.md`
- Create: `docs/engineering/verify-package-shadow-resume-handoff.md`

**Interfaces:**
- Produces a review disposition and the exact requested engineering handoff fields.

- [ ] Re-read the spec and plan from a fresh review pass, then inspect `git diff --no-ext-diff 62507de...HEAD` plus uncommitted changes for correctness, security, fail-closed behaviour, process cleanup, Windows/Git-Bash compatibility, and authority boundaries.
- [ ] Record Critical/Important/Minor findings and fix all Critical/Important findings through new RED/GREEN cycles.
- [ ] State that the review is serial self-review, not independent-agent review, because side-chat policy forbids subagents.
- [ ] Run fresh verification: `python -m unittest tests.verify_package_shadow_test -v`, registry validation, benchmark, focused real scenarios, `git diff --check`, `git status --short`, and residue checks.
- [ ] Write the compact handoff with exact worktree, branch, base/final HEAD, architecture, graph/edge justifications, validity contract, files/tests/results, equivalence, performance, limitations, risks, and recommended admission path.
- [ ] Stop with the worktree unmerged, uninstalled, uncommitted, and non-authoritative.
