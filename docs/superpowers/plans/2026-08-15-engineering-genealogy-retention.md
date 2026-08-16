# Engineering Genealogy Retention Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Preserve the exact twelve-lineage/658-property Engineering Genealogy corpus and produce deterministic neutral indexes plus a frozen historical IMPLEMENTAUDIT absorption baseline on an isolated review branch.

**Architecture:** Exact packet ZIPs are immutable committed inputs; exact extracted members and all indexes are deterministic projections. Repository-neutral research lives under `docs/research/genealogy/`, while the read-only historical IMPLEMENTAUDIT baseline lives under `docs/research/implementaudit/historical-absorption-baseline/` and defers every current-v0.4 change claim.

**Tech Stack:** Python 3 standard library, POSIX shell tests executed with Git Bash, JSON, Markdown, Git.

## Global Constraints

- Preserve exact packet ZIPs and exact extracted corpus members.
- Preserve all four trifectas, twelve lineages, and 658 properties.
- Do not perform current-v0.4 reabsorption or make runtime, package, child-skill, RXX, PR, merge, or release decisions.
- Use British English for new prose.
- Keep local absolute paths out of committed public artifacts.
- Record all exact-v0.4.0-dependent work as `DEFER_TO_V0410_BASELINE`.
- Keep the genealogy tree outside all distributable package payloads.
- Do not use subagents in this side-conversation execution.

---

### Task 1: Freeze source inputs and establish a failing corpus contract

**Files:**
- Create packet ZIPs under: `docs/research/genealogy/law/{evolved-lean,evolved-agile,evolved-waterfall}/packet/`
- Create packet ZIPs under: `docs/research/genealogy/css/{evolved-cognitive-systems-engineering,evolved-statistical-engineering,evolved-systems-safety}/packet/`
- Create packet ZIPs under: `docs/research/genealogy/ssd/{evolved-systems-engineering,evolved-systems-security-engineering,evolved-decision-and-operations-engineering}/packet/`
- Create packet ZIPs under: `docs/research/genealogy/drf/{evolved-distributed-systems-engineering,evolved-reliability-and-maintainability-engineering,evolved-formal-methods-and-verification-engineering}/packet/`
- Create: `docs/research/genealogy/method/source-prompts/EVOLVED_DISTRIBUTED_SYSTEMS_ENGINEERING_PRO_RESEARCH_PROMPT.md`
- Create: `docs/research/genealogy/method/source-prompts/EVOLVED_RELIABILITY_AND_MAINTAINABILITY_ENGINEERING_PRO_RESEARCH_PROMPT.md`
- Create: `docs/research/genealogy/method/source-prompts/EVOLVED_FORMAL_METHODS_AND_VERIFICATION_ENGINEERING_PRO_RESEARCH_PROMPT.md`
- Create: `docs/research/genealogy/method/source-prompts/EVOLVED_DRF_PRO_RESEARCH_PROMPTS_MANIFEST.json`
- Create: `docs/research/genealogy/CORPUS_SOURCE_LOCK.json`
- Create: `tests/genealogy-corpus.test.sh`

**Interfaces:**
- Consumes: the twelve supplied frozen ZIP occurrences, their exact raw SHA-256 values, and the four supplied DRF prompt occurrences.
- Produces: immutable repository-local source inputs and a shell test that invokes `python scripts/check-genealogy-corpus.py --root .`.

- [ ] **Step 1: Copy exact immutable inputs**

Use `Copy-Item -LiteralPath` for each source occurrence into its declared repository-relative packet/prompt destination. Verify source-to-destination byte length and SHA-256 immediately; do not unpack with PowerShell.

- [ ] **Step 2: Write the source lock**

Write sorted UTF-8 JSON declaring four trifectas, twelve lineages, slugs, expected property counts, repository-relative packet paths, raw packet bytes/SHA-256, property-ledger member names and schema roots, and the prompt files/manifest. Embedded normalized packet digests are metadata, not substitutes for raw delivered ZIP identities.

- [ ] **Step 3: Write the failing positive contract**

Create `tests/genealogy-corpus.test.sh` with:

```bash
#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
python "$ROOT/scripts/check-genealogy-corpus.py" --root "$ROOT"
```

- [ ] **Step 4: Run the test and verify RED**

Run:

```bash
bash tests/genealogy-corpus.test.sh
```

Expected: non-zero because `scripts/check-genealogy-corpus.py` does not yet exist.

- [ ] **Step 5: Commit the source lock and failing contract only after recording RED**

```bash
git add docs/research/genealogy tests/genealogy-corpus.test.sh
git commit -m "test: freeze genealogy corpus contract"
```

### Task 2: Implement deterministic corpus generation and neutral documentation

**Files:**
- Create: `scripts/genealogy_corpus.py`
- Create: `scripts/build-genealogy-corpus.py`
- Create: `scripts/check-genealogy-corpus.py`
- Create: `docs/research/genealogy/README.md`
- Create: `docs/research/genealogy/RESEARCH_METHOD.md`
- Create: `docs/research/genealogy/REPLICATION_GUIDE.md`
- Create: `docs/research/genealogy/{law,css,ssd,drf}/README.md`
- Create: lineage README files under the twelve exact lineage directories declared in Task 1
- Generate: twelve `LINEAGE_MANIFEST.json` files
- Generate: twelve exact `corpus/` trees
- Generate: `docs/research/genealogy/CORPUS_MANIFEST.json`
- Generate: `docs/research/genealogy/PROPERTY_MASTER_INDEX.json`
- Generate: `docs/research/genealogy/method/SOURCE_PROMPT_MANIFEST.json`

**Interfaces:**
- Consumes: `CORPUS_SOURCE_LOCK.json` plus repository-local packet/prompt bytes.
- Produces: `load_source_lock(root)`, `build_corpus(root)`, `check_corpus(root) -> list[str]`, exact extraction, source-row locators, and deterministic JSON projections.

- [ ] **Step 1: Add focused Python unit cases to the shell test**

Extend the shell test to create a temporary miniature ZIP/source lock and verify that the checker reports a changed packet hash, missing extracted member, duplicate property key, and dangling property locator. Invoke actual production functions through the command-line scripts; do not mock file access.

- [ ] **Step 2: Verify the new cases remain RED**

Run the focused test and confirm failure is due to absent production scripts/functions.

- [ ] **Step 3: Implement exact extraction and parsers**

Implement:

```python
def sha256_bytes(data: bytes) -> str: ...
def load_source_lock(root: Path) -> dict: ...
def parse_json_property_ledger(data: bytes, root_key: str) -> list[dict]: ...
def parse_yaml_property_ledger(data: bytes, root_key: str) -> list[dict]: ...
def build_corpus(root: Path) -> None: ...
def check_corpus(root: Path) -> list[str]: ...
```

The YAML parser is deliberately bounded to the frozen ledgers: it identifies each `PROPERTY_ID` record by indentation, collects `PROPERTY_NAME`, `CURRENT_STATUS`, `MATURE_OR_EVOLVED_FORM`, and `EVIDENCE_STRENGTH`, and records exact one-based line spans. Wrapped scalars are folded only for index display; preserved member bytes remain authoritative.

- [ ] **Step 4: Generate exact members and indexes**

Run:

```bash
python scripts/build-genealogy-corpus.py --root .
python scripts/check-genealogy-corpus.py --root .
```

Expected summary: `TRIFECTAS=4/4`, `LINEAGES=12/12`, `PROPERTIES=658/658`, and zero errors.

- [ ] **Step 5: Author neutral documentation**

Document source authority, denominator, schema heterogeneity, research method, replication, and the distinction between exact inputs and navigational projections. Do not assert current IMPLEMENTAUDIT/RXX ownership or implementation status.

- [ ] **Step 6: Prove deterministic regeneration**

Hash all generated manifests/indexes, rerun the builder, and compare hashes byte-for-byte. Expected: no changed hashes and an empty `git diff` for generated files.

- [ ] **Step 7: Commit the neutral corpus**

```bash
git add scripts docs/research/genealogy tests/genealogy-corpus.test.sh
git commit -m "docs: preserve engineering genealogy corpus"
```

### Task 3: Generate the read-only historical absorption baseline

**Files:**
- Create: `docs/research/implementaudit/historical-absorption-baseline/SOURCE_IDENTITY.json`
- Create: `docs/research/implementaudit/historical-absorption-baseline/HISTORICAL_ABSORPTION_BASELINE.json`
- Create: `docs/research/implementaudit/historical-absorption-baseline/README.md`
- Create: `scripts/build-historical-absorption-baseline.py`
- Modify: `tests/genealogy-corpus.test.sh`

**Interfaces:**
- Consumes: one exact copied/frozen input occurrence of `V0400_CANONICAL_RESEARCH_PROPERTY_RXX_CROSSWALK.pre-post-implementation.json`, identified by bytes/SHA-256 in `SOURCE_IDENTITY.json`; the source occurrence is analysis input and is not duplicated into the neutral genealogy corpus.
- Produces: an exhaustive 658-row historical classification, source locators, evidence-tagged constraint indicators, and aggregate counts.

- [ ] **Step 1: Add failing historical-classification tests**

Add fixtures covering every source disposition and LAW code. Assert the exhaustive expected counts:

```text
HISTORICALLY_ABSORBED_COMPLETE=221
HISTORICALLY_ABSORBED_PARTIAL=41
HISTORICALLY_EXISTING_OWNER_NEEDS_AMENDMENT=114
HISTORICALLY_LINEAGE_NATIVE_RESIDUAL=59
HISTORICALLY_IMPLEMENTATION_OR_REACHABILITY_GAP=2
HISTORICALLY_BEHAVIOURAL_PROOF_GAP=8
HISTORICALLY_ASSUMPTION_BOUND=40
HISTORICALLY_DOMAIN_BOUND=77
HISTORICALLY_REJECTED_OR_SUPERSEDED=79
HISTORICALLY_UNRESOLVED=17
```

Assert that all 658 rows contain `V0400_CHANGE_DISPOSITION=DEFER_TO_V0410_BASELINE` and no post-implementation verdict is copied.

- [ ] **Step 2: Verify RED**

Run the focused shell test. Expected: failure because the historical baseline builder/output is absent.

- [ ] **Step 3: Implement classification and evidence-tagged indicators**

Implement explicit maps for the ten historical classes. Constraint indicators scan only declared historical disposition/gap/implementation fields and retain the matched field path plus exact value. The algorithm must never infer a v0.4 disposition.

- [ ] **Step 4: Build and validate the baseline**

Run:

```bash
python scripts/build-historical-absorption-baseline.py --root . --source "$GENEALOGY_HISTORICAL_CROSSWALK"
bash tests/genealogy-corpus.test.sh
```

Expected: 658 unique rows, class-count sum 658, source SHA match, indicator evidence present for every tagged row, and all v0.4 changes deferred.

- [ ] **Step 5: Commit the baseline**

```bash
git add docs/research/implementaudit scripts/build-historical-absorption-baseline.py tests/genealogy-corpus.test.sh
git commit -m "docs: add historical absorption baseline"
```

### Task 4: Register package verification and prove fail-closed controls

**Files:**
- Modify: `scripts/verify-package.sh`
- Modify: `tests/genealogy-corpus.test.sh`

**Interfaces:**
- Consumes: the completed corpus and baseline checkers.
- Produces: one registry invocation and disposable negative controls without changing source inputs.

- [ ] **Step 1: Add registration and negative-control assertions**

Register `tests/genealogy-corpus.test.sh` exactly once in `scripts/verify-package.sh`. Extend the test to mutate temporary copies for: missing lineage, changed ZIP byte, missing property row, duplicate global key, dangling source locator, local absolute path in a public manifest, current IMPLEMENTAUDIT/RXX disposition in a neutral lineage README, and genealogy path in a package listing.

- [ ] **Step 2: Verify each control fails for its intended reason**

Run each mutation case independently and assert the checker emits its specific diagnostic. A generic non-zero result is insufficient.

- [ ] **Step 3: Verify positive and registry paths**

Run:

```bash
bash tests/genealogy-corpus.test.sh
bash tests/validation-registry.test.sh
```

Expected: all genealogy cases pass and the test registry is complete with one invocation per test.

- [ ] **Step 4: Commit verification integration**

```bash
git add scripts/verify-package.sh tests/genealogy-corpus.test.sh
git commit -m "test: enforce genealogy corpus integrity"
```

### Task 5: Final review, full verification, and branch publication

**Files:**
- Verify all changed files; create no PR metadata.

**Interfaces:**
- Consumes: all prior commits.
- Produces: a clean, pushed review branch with exact verification evidence.

- [ ] **Step 1: Review requirements and generated identities**

Re-read the design and plan. Recompute packet ZIP hashes, corpus manifest hash, property index hash, source prompt manifest hash, historical baseline hash, lineage/property counts, and committed byte total.

- [ ] **Step 2: Run focused verification fresh**

```bash
bash tests/genealogy-corpus.test.sh
bash tests/validation-registry.test.sh
git diff --check origin/main...HEAD
```

- [ ] **Step 3: Run full package verification with a sufficient timeout**

```bash
bash scripts/verify-package.sh
```

Record exit code and complete terminal summary. The earlier 120-second timeout is an incomplete attempt, not a pass or failure.

- [ ] **Step 4: Inspect bounded diff and status**

```bash
git status --short --branch
git diff --stat origin/main...HEAD
git log --oneline --decorate origin/main..HEAD
```

Confirm no active-v0.4 worktree paths or changes are present and no PR was opened.

- [ ] **Step 5: Push the dedicated branch**

```bash
git push -u origin docs/v0410-genealogy-retention
git ls-remote --heads origin refs/heads/docs/v0410-genealogy-retention
```

The remote SHA must equal local `HEAD`. Stop without opening or merging a pull request.
