---
name: implementaudit
description: >
  Implement audit findings from an input report safely and verifiably using
  PDCA, Gemba, Smoke Before Claim, Andon, Hansei, 5 Whys, and Plan Closure.
  Activate when the user invokes /implementaudit, pipes an audit into it,
  or asks to implement findings from a handoff,
  review, checklist, audit report, or implementation plan. Also activate when
  the user says "implement these findings", "act on this audit", "close these
  items", or "work through this handoff". Repo-generic: inspect the actual repo
  first; never assume framework, language, CI, build system, or release
  convention. Does not commit, push, tag, publish, or release unless the input
  explicitly authorizes that action and repo instructions allow it.
---

# /implementaudit

Convert audit findings, handoffs, reviews, or checklists into safe, verified repo changes.

Every finding closes. No orphan items. No unsafe actions. No proof claim without evidence.

Do not stop at "partial," "safe but unchanged," or "next countermeasure needed" while an obvious in-scope next action remains. Continue until every audit item is terminally closed as `done`, `changed`, `blocked`, `deferred`, or `unverified`.

---

## 0. Non-negotiable safety defaults

Before touching files, inspect repo instructions when present:

- `AGENTS.md`
- `CONTRIBUTING.md`
- `README.md`
- `docs/**`
- CI/workflow files
- existing handoff/audit docs
- package/build/test/release docs

Never do any of the following unless the input explicitly authorizes the action and repo docs allow it:

- push
- tag
- publish
- create or update releases
- delete data
- alter credentials or secrets
- rewrite history
- commit raw diagnostic outputs
- hand-edit generated artifacts when a source generator exists
- claim proof without running the smallest meaningful check

**Explicit authorization** means a direct imperative such as `commit changes`, `push to main`, `push this branch`, `tag vX.Y.Z`, or `update the release assets`. References to CI, deployment, release plans, or implied workflows do not count.

If the repo contains domain notation, schema keys, DSL tokens, public API names, file paths, release asset names, or exact contract strings, preserve them exactly unless the audit explicitly asks to change them. Do not rename, simplify, transliterate, ASCII-normalize, or "clean up" symbolic tokens just to improve prose, layout, or style.

Stop and report if any requested action is unsafe, unsupported, unauthorized, or blocked by repo policy:

```text
STOP:
Denied action:
Reason:
Owner/source:
Smallest passing check or next action:
```

Default stance unless explicitly authorized:

```text
No commit. No push. No tag. No release. No publication.
```

---

## 1. Core operating method

### PDCA — Plan, Do, Check, Act

| Phase | Discipline |
|---|---|
| Plan | Identify finding, owner/source, risk, smallest safe change, and verification command. |
| Do | Patch the owner/source, not the nearest symptom. Keep changes atomic. Avoid broad rewrites. |
| Check | Run the smallest meaningful check, relevant tests/smokes, and inspect generated output where applicable. |
| Act | Standardize if successful. Revise or revert if failed. Update the closure ledger. |

**Broad rewrite threshold:** A patch is broad if it touches more than one logical unit not named in the audit, or if it restructures surrounding code unrelated to the finding. When in doubt, make the narrowest change that closes the finding and log the rest to the scope-creep register.

### Gemba — Real place of work

Inspect the actual artifact where the error or value occurs: source file, generated file, browser page, package, smoke output, checker error, workflow, logs, release asset, prompt file, or skill file. Do not diagnose from summaries when the live artifact exists.

For non-code artifacts (skills, prompts, config files, markdown docs, data files with no test runner): Gemba means reading the artifact directly and identifying structural, logical, or semantic issues. The bash orientation commands below may produce nothing useful; read the file instead.

### Smoke Before Claim

Run the smallest meaningful check before claiming behavior.

```text
Smoke Before Claim:
Command:
Result:
Evidence type: [live runtime | local generated-runtime | package-bound | unit test | integration test | static checker | manual inspection | visual/browser | unverified]
Remaining risk:
```

Never upgrade static evidence into live proof. If a live check cannot run, label the evidence type and remaining risk explicitly.

For prompt/skill/non-executable artifacts: Smoke = trace the artifact against a known representative input, mentally or via a test invocation, and record what it produces.

### Andon — Visible problem signal

When work cannot honestly pass, surface it immediately:

```text
Andon:
Status:
Blocker:
Failing check:
Owner/source:
Next concrete action:
```

Do not hide failure. Do not mark "mostly done."

### Hansei — Structured reflection

After any failure or regression:

```text
Hansei:
Gap:
Cause:
Countermeasure:
Follow-up evidence:
```

### 5 Whys — Root-cause drill

Use 5 Whys carefully: symptom → systemic cause → countermeasure at the cause.

```text
5 Whys:
1. Why did the symptom occur?
2. Why did that condition exist?
3. Why did the system allow it?
4. Why was it not caught earlier?
5. What countermeasure prevents recurrence?
```

**Loop-exit protocol:** If 5 Whys identifies a root cause that is out of scope, requires an architectural change, or requires an OWNER DECISION, do not loop. Log it to the scope-creep register, close the current item as `deferred` with reason, and continue to the next item.

### Plan Closure

At the end, every plan item must be mapped to exactly one terminal status:

- `done`
- `changed`
- `blocked`
- `deferred`
- `unverified`

No item may remain `open`.

---

## 2. Validate input

Confirm the input is a recognizable audit artifact, such as:

- findings report
- handoff
- review checklist
- implementation plan
- explicit `/implementaudit` invocation
- user request to "implement these findings," "act on this audit," "close these items," or "work through this handoff"

If input is empty, malformed, or not an audit artifact:

```text
STOP:
Input is not a valid audit artifact.
Expected: findings report, handoff, checklist, implementation plan, or /implementaudit invocation.
Received:
Next action: request valid input from user.
```

Do not proceed until valid input is confirmed.

---

## 3. Read and normalize input

Extract:

- findings
- blockers
- recommended patches
- verification commands
- release/safety constraints
- deferred items
- owner decisions
- required output format

Classify each finding:

| Class | Criterion |
|---|---|
| `P0` | Blocks the stated goal, breaks an existing passing check, or is a safety violation. |
| `P1` | Directly named in the audit, reduces risk, improves correctness, and is safely achievable now. |
| `P2` | Defensive hardening or nice-to-have not required for the current goal. |
| `OWNER DECISION` | Requires a human call before safe proceeding. |
| `DEFERRED` | Explicitly pushed out by input or owner. |
| `OUT OF SCOPE` | Outside the stated mandate. |

**Dependency note:** If item B cannot safely proceed without item A being closed first, record this in the ledger. If A is blocked, mark B as `deferred` with reason "depends on #A" rather than attempting B independently.

Initialize the implementation ledger. `open` is an initial state, not a terminal status.

| # | Finding | Priority | Owner/source | Risk | Verification | Status | Evidence | Depends on |
|---|---|---:|---|---|---|---|---|---|
| 1 | ... | P0 | ... | ... | `<command>` | open | — | — |

Initialize the scope-creep register.

| # | Issue found | Location | Recommendation |
|---|---|---|---|

Adjacent issues not in the ledger go into the scope-creep register and are not implemented.

**Exception:** If an adjacent issue is required to safely close a current ledger item, promote it into the ledger as a new row with status `changed`, name the owner/source, cite which ledger item requires it, and explain why it is necessary. Do not silently expand scope. If the promoted item itself surfaces a further adjacent issue, log that to the scope-creep register and stop — do not chain promotions.

---

## 4. Gemba inspection

Go to the real place of work. Inspect actual files, not summaries.

**Platform note:** Examples below are bash/Unix. On Windows, adapt using PowerShell, `dir`, `findstr`, `type`, or repo-standard commands.

```bash
# Repo type and root
ls -la && head -40 README.md 2>/dev/null

# Package/build config
find . -maxdepth 2 \( -name "package.json" -o -name "Makefile" \
  -o -name "pyproject.toml" -o -name "Cargo.toml" -o -name "go.mod" \) | head -10

# CI/workflow files
find . -maxdepth 4 \( -path "./.github/workflows/*.yml" \
  -o -name ".gitlab-ci.yml" -o -name "Jenkinsfile" \) | head -10

# Repo instructions and prior audits
find . -maxdepth 2 \( -name "AGENTS.md" -o -name "CONTRIBUTING.md" \
  -o -name "HANDOFF*" -o -name "AUDIT*" \) | head -10

# Current dirty state
git status && git diff --stat HEAD 2>/dev/null

# Detect generated artifacts (heuristic only)
grep -rl "DO NOT EDIT\|generated by\|auto-generated\|this file is generated" \
  --include="*.ts" --include="*.js" --include="*.py" --include="*.go" . 2>/dev/null | head -10
```

**Generated artifact rule:** A file is generated if repo policy says so; if it lives in `dist/`, `build/`, or `generated/`; if it carries a "do not edit" / "generated by" header; or if it is a known codegen output such as `.pb.go`, `.g.dart`, or `*.pb.ts`. Identify its source generator and edit the source, not the artifact.

**Generator-first protocol:** If the source generator encodes the same incorrect value as the generated artifact, fix the generator first, verify the generator, then regenerate the artifact. Do not regenerate before fixing the generator.

If repo policy explicitly permits direct artifact editing, cite that policy in the plan.

**Non-git VCS or no VCS:** If the repo uses a different VCS (SVN, Mercurial, Perforce) or none, adapt all git commands to the appropriate VCS equivalents. For non-VCS targets (zip archives, FTP deployments, CMS content), "rollback" means restoring from a saved backup or cached baseline taken before Step 7.

**Idempotency:** If a prior run exists (check for `HANDOFF.md`, `AUDIT.md`, or a prior ledger), review its closure state. Do not re-implement already-closed items unless a regression has since occurred. Re-open only with explicit reason.

---

## 5. Pre-flight checklist

With targets known from Gemba, confirm all items before mutation. Any failed item triggers STOP unless the audit target itself is the failure.

- [ ] Write access confirmed on all target files.
- [ ] Source generator identified for generated artifacts in scope, or repo policy cited.
- [ ] Generator-first order confirmed: generators that embed the finding are fixed before regeneration.
- [ ] Commit/push authorization status resolved: not authorized by default, or explicitly cited from input.
- [ ] Repo safety constraints read and not violated by the plan.
- [ ] Baseline smoke has not yet run; it comes next.

Write access check:

```bash
test -w <target_file> && echo "WRITABLE" || echo "NOT WRITABLE — stop"
```

---

## 6. Create working plan

Before mutation, write the working plan:

```text
Goal:
Top objective:
Owner/source of truth:
Audit items in scope, by ledger #:
Audit items out of scope, by ledger #:
Item dependencies (if any):
Risk:
Verification commands:
Rollback:
  Before commit (git)      -> git restore <file> | git checkout <file> | git stash
  After commit (git)       -> git revert <hash>  (preserves history; preferred)
  Unpushed commit (git)    -> git reset --hard HEAD  (destructive; use with care)
  Generated output         -> rerun source generator (after confirming generator is correct)
  Non-git / no VCS         -> restore from backup or cached baseline taken before Smoke A
```

Use the smallest patch that satisfies the audit.

---

## 7. Baseline smoke: Smoke A before mutation

Run all audit-named verification commands before touching files. This is Smoke A. Subsequent smokes are compared against it.

If baseline checks are failing, classify each failure before proceeding:

| Classification | Condition | Action |
|---|---|---|
| `target` | The failure is the audit finding itself | Proceed. Record as failing baseline evidence. |
| `unrelated` | The failure predates the audit and is not in scope | Stop unless explicitly authorized to proceed on a broken baseline. |
| `unclear` | Cannot determine | Andon → request owner decision before proceeding. |

Do not silently mix unrelated pre-existing failures with implementation regressions.

```text
Smoke A (baseline, pre-patch):
Commands run:
Results:
Pre-existing failures (classified as target / unrelated / unclear):
```

---

## 8. Implement item by item

Process items in P0 → P1 → P2 order. Skip items whose dependencies are blocked.

For each item:

1. Confirm source owner.
2. Patch owner/source, not nearest symptom.
3. If the fix changes a data type, format, algorithm, or API contract: flag downstream artifacts that encode assumptions about the old value (test expectations, dependent configs, generated outputs, documentation). Check each one and add to the ledger if promotion is warranted per Step 3 rules, or to the scope-creep register if not.
4. Rebuild generated outputs if needed, following generator-first protocol.
5. Run the smallest local check.
6. Update ledger status and evidence.
7. Continue to the next item.

Mid-item blocker protocol: if a blocker is hit mid-patch, restore clean state before reporting.

```bash
git restore <affected_file>
# or: git checkout <affected_file>
# non-git: restore from backup
```

Then use Andon, update the ledger as `blocked`, and continue if other items remain. Never leave files in a broken intermediate state.

Scope-creep guard remains active throughout this step.

---

## 9. Post-implementation smoke: Smoke B

Run the full verification suite after changes are complete. For P0 or high-risk changes, run an interim smoke after each patch set.

```text
Smoke B (post-patch):
Commands run:
Results:
```

Decision criteria:

| Outcome | Condition | Action |
|---|---|---|
| Resolved + preserved | Finding closed and all Smoke A passing checks still pass | Accept as `done` or `changed`. |
| Preserved only | No regression, but finding not fully closed | Continue if in scope; otherwise close as `blocked`, `deferred`, or `unverified` with reason. |
| Regression | Any Smoke A check that passed now fails | See regression protocol below. |

**Regression protocol:**

1. Identify whether the regression is in the fix itself or in a downstream dependency of the fix (e.g., a test encoding a stale assumption about the old behavior).
2. If the regression is in a downstream dependency: revise the dependency, not the fix. Do not revert the correct fix to restore a wrong baseline.
3. If the regression is in the fix itself: Andon → Hansei → 5 Whys → revert fix → revise → re-smoke.
4. After revision, re-run Smoke B. Do not claim resolution without a clean re-smoke.

Regression signals: fewer tests passing, new lint/type/build errors, unexpected schema/output changes, new runtime errors, expanded security surface, contract or API shape change not authorized by audit.

---

## 10. Validate

Run audit-named checks first. Then run repo-standard checks if discoverable.

At minimum:

```bash
git diff --check
```

Project checks may include unit tests, integration tests, lint, typecheck, build, docs build, package-shape check, smoke artifact check, schema validation, provenance checks, or visual/browser inspection.

Report exact commands and results.

---

## 11. Update handoff or audit doc

Create or update a tracked doc when appropriate. Do not rely on chat context alone.

```text
Goal:
Implemented:
Changed:
Blocked:
Deferred:
Unverified:
Found — not in scope (scope-creep register):
Smoke A (pre-patch baseline, with pre-existing failure classifications):
Smoke B (post-implementation, with regression protocol notes if triggered):
Checks run:
Next action:
```

If a root handoff file is ignored by tooling, mirror important status into a tracked audit/handoff doc.

---

## 12. Commit or push only if explicitly authorized

If commit/push is not explicitly authorized, do not stage, commit, or push.

If commit/push is explicitly authorized:

1. Run final checks first.
2. Stage explicit paths only; do not use `git add .`.
3. Verify that raw diagnostics, build artifacts, local smoke outputs, secrets, and unrelated files are not staged.
4. Commit only after Smoke B and final validation pass.
5. Push only after commit succeeds and the working tree is reviewable.

If release/tag/publication is explicitly authorized, perform a separate release gate check according to repo policy. Release authorization is not implied by commit/push authorization.

For non-git VCS: adapt staging and commit steps to the appropriate VCS commands. For no VCS: record the set of changed files and their checksums as the "commit" record.

---

## 13. Final response format

```md
# /implementaudit Result

## Verdict
<!-- Choose exactly one:
IMPLEMENTED AND VERIFIED        all P0+P1 done/changed; Smoke B checks pass; no unresolved blockers
IMPLEMENTED WITH DEFERRED       all P0 done; some P1/P2 deferred by design; Smoke B passes
PARTIAL; BLOCKERS REMAIN        at least one P0/P1 blocked/unverified; Smoke B partial or skipped
REGRESSION FOUND                any Smoke A passing check fails after patching
BLOCKED                         cannot safely proceed — all P0s blocked, or unsafe/unauthorized entry condition
-->

## Goal

## Input basis

## Findings ledger
| # | Finding | Priority | Action | Status | Evidence | Depends on | Follow-up |
|---|---|---:|---|---|---|---|---|

## Scope-creep register (found — not in scope)
| # | Issue | Location | Recommendation |
|---|---|---|---|
<!-- State "None found" explicitly if empty. -->

## Changes made

## Smoke A (baseline — pre-patch)
| Check | Command | Result | Evidence type | Classification (target/unrelated/unclear) |
|---|---|---|---|---|

## Smoke B (post-implementation)
| Check | Command | Result | Evidence type | Δ vs Smoke A | Remaining risk |
|---|---|---|---|---|---|

## Regression protocol triggered
<!-- Include only if a regression was detected during Smoke B.
State whether the regression was in the fix itself or a downstream dependency,
and which branch of the regression protocol was followed. -->

## Andon / Hansei / 5 Whys
<!-- Include only if failures or blockers occurred. -->

## Plan closure
| # | Item | Status | Evidence | Follow-up |
|---|---|---|---|---|

## Files changed

## Commands run

## Commit / push
<!-- State exactly one:
No commit performed. No push performed.
Commit performed: `<hash>`. No push performed.
Commit and push performed: `<hash>` to `<remote>/<branch>`.
-->

## Remaining caveats
<!-- Items the implementer could not verify, risks not eliminated,
owner decisions deferred, or conditions that could invalidate the verdict. -->
```

---

## Quality bar self-check

Run this internally before the final response. Any failing item must be fixed or marked `unverified` with reason.

- [ ] Every patch connects to a ledger item by number.
- [ ] Owner/source was patched, not nearest symptom.
- [ ] No broad rewrites outside audit scope (threshold: changes limited to the logical unit named in the finding).
- [ ] Meaningful check/evidence recorded for every changed item.
- [ ] Every ledger item has a terminal status; zero `open` items remain.
- [ ] Deferred items have explicit reasons.
- [ ] Items with dependencies: blocked dependencies caused dependents to be deferred, not attempted.
- [ ] Format/algorithm/contract-changing fixes: downstream assumptions (test expectations, dependent configs, generated outputs) were identified and handled.
- [ ] Generator-first protocol observed for generated artifacts.
- [ ] Scope-creep register is populated or says "None found."
- [ ] Promotion chains stopped at one level; no cascading scope expansions.
- [ ] Scope-creep loop-exit followed for 5 Whys cycles that hit out-of-scope root causes.
- [ ] Smoke A recorded before mutation, with pre-existing failure classifications.
- [ ] Smoke B recorded after implementation.
- [ ] Regression protocol branch identified and followed if triggered.
- [ ] Broken baseline failures classified as target / unrelated / unclear.
- [ ] Exact notation/API/schema/contract strings preserved unless explicitly changed by audit.
- [ ] Verdict chosen by rubric, not intuition.
- [ ] Commit/push stance stated explicitly.
- [ ] Repo left reviewable and non-broken.
