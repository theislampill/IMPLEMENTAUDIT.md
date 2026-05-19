---
name: implementaudit
description: >
  Implement audit findings from an input report safely and verifiably using
  PDCA, Gemba, Smoke Before Claim, Andon, Hansei, 5 Whys, and Plan Closure.
  Activate when the user invokes /implementaudit, pipes an audit with
  `/implementaudit < input.md`, or asks to implement findings from a handoff,
  review, checklist, audit report, or implementation plan. Repo-generic: inspect
  the actual repo first; never assume framework, language, CI, build system, or
  release convention. Does not commit, push, tag, publish, or release unless the
  input explicitly authorizes that action and repo instructions allow it.
---

# /implementaudit

Convert audit findings, handoffs, reviews, or checklists into safe, verified repo changes.

Every finding closes. No orphan items. No unsafe actions. No proof claim without evidence.

Do not stop at “partial,” “safe but unchanged,” or “next countermeasure needed” while an obvious in-scope next action remains. Continue until every audit item is terminally closed as `done`, `changed`, `blocked`, `deferred`, or `unverified`.

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

Explicit authorization means a direct imperative such as `commit changes`, `push to main`, `push this branch`, `tag vX.Y.Z`, or `update the release assets`. References to CI, deployment, release plans, or implied workflows do not count.

If the repo contains domain notation, schema keys, DSL tokens, public API names, file paths, release asset names, or exact contract strings, preserve them exactly unless the audit explicitly asks to change them. Do not rename, simplify, transliterate, ASCII-normalize, or “clean up” symbolic tokens just to improve prose, layout, or style.

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

### Gemba — Real place of work

Inspect the actual artifact where the error or value occurs: source file, generated file, browser page, package, smoke output, checker error, workflow, logs, or release asset. Do not diagnose from summaries when the live artifact exists.

### Smoke Before Claim

Run the smallest meaningful check before claiming behavior.

```text
Smoke Before Claim:
Command:
Result:
Evidence type: [live runtime | local generated-runtime | package-bound | unit test | integration test | static checker | manual inspection | visual/browser | unverified]
Remaining risk:
```

Never upgrade static evidence into live proof. If a live check cannot run, label the evidence type and remaining risk.

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

Do not hide failure. Do not mark “mostly done.”

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
- user request to “implement these findings,” “act on this audit,” “close these items,” or “work through this handoff”

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

Initialize the implementation ledger. `open` is an initial state, not a terminal status.

| # | Finding | Priority | Owner/source | Risk | Verification | Status | Evidence |
|---|---|---:|---|---|---|---|---|
| 1 | ... | P0 | ... | ... | `<command>` | open | — |

Initialize the scope-creep register.

| # | Issue found | Location | Recommendation |
|---|---|---|---|

Adjacent issues not in the ledger go into the scope-creep register and are not implemented.

Exception: if the adjacent issue is required to safely close a current ledger item, promote it into the ledger as `changed`, name the owner/source, and explain why it is necessary. Do not silently expand scope.

---

## 4. Gemba inspection

Go to the real place of work. Inspect actual files, not summaries.

Platform note: examples below are bash/Unix. On Windows, adapt using PowerShell, `dir`, `findstr`, `type`, or repo-standard commands.

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

# Detect generated artifacts, heuristic only
grep -rl "DO NOT EDIT\|generated by\|auto-generated\|this file is generated" \
  --include="*.ts" --include="*.js" --include="*.py" --include="*.go" . 2>/dev/null | head -10
```

Generated artifact rule: a file is generated if repo policy says so, if it lives in common generated paths such as `dist/`, `build/`, or `generated/`, if it carries a generated header, or if it is a known codegen output such as `.pb.go`, `.g.dart`, or `*.pb.ts`. Identify its source generator and edit the source, not the artifact. If repo policy explicitly permits direct artifact editing, cite that policy in the plan.

Idempotency: if a prior run exists, review its closure state. Do not re-implement already-closed items unless a regression has occurred. Re-open only with explicit reason.

---

## 5. Pre-flight checklist

With targets known from Gemba, confirm all items before mutation. Any failed item triggers STOP unless the audit target itself is the failure.

- [ ] Write access confirmed on all target files.
- [ ] Source generator identified for generated artifacts in scope, or repo policy cited.
- [ ] Commit/push authorization status resolved: not authorized by default, or explicitly cited.
- [ ] Repo safety constraints read and not violated by the plan.
- [ ] Baseline smoke has not yet run; it comes next.

Write access check example:

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
Risk:
Verification commands:
Rollback:
  Before commit      -> git restore <file> | git checkout <file> | git stash
  After commit       -> git revert <hash>  (preserves history; preferred)
  Unpushed commit    -> git reset --hard HEAD  (destructive; use with care)
  Generated output   -> rerun source generator
```

Use the smallest patch that satisfies the audit.

---

## 7. Baseline smoke: Smoke A before mutation

Run all audit-named verification commands before touching files. This is Smoke A. Subsequent smokes are compared against it.

If baseline checks are failing, classify them:

- If the failure is the audit target, proceed and treat Smoke A as failing baseline evidence.
- If the failure is unrelated, stop unless explicitly authorized.
- If unclear, report Andon and ask for owner decision.

Do not silently mix unrelated pre-existing failures with implementation regressions.

```text
Smoke A (baseline, pre-patch):
Commands run:
Results:
Pre-existing failures:
```

---

## 8. Implement item by item

Process items in P0 → P1 → P2 order.

For each item:

1. Confirm source owner.
2. Patch owner/source, not nearest symptom.
3. Rebuild generated outputs if needed.
4. Run the smallest local check.
5. Update ledger status and evidence.
6. Continue to the next item.

Mid-item blocker protocol:

If a blocker is hit mid-patch, restore clean state before reporting.

```bash
git restore <affected_file>
# or: git checkout <affected_file>
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
| Regression | Any Smoke A check that passed now fails | Andon → Hansei → 5 Whys → revert or revise → re-smoke. |

Regression signals include fewer tests passing, new lint/type/build errors, unexpected schema/output changes, new runtime errors, or expanded security surface.

---

## 10. Validate

Run audit-named checks first. Then run repo-standard checks if discoverable.

At minimum, run:

```bash
git diff --check
```

Project checks may include unit tests, integration tests, lint, typecheck, build, docs build, package-shape check, smoke artifact check, schema validation, provenance checks, or visual/browser inspection.

Report exact commands and results.

---

## 11. Update handoff or audit doc

Create or update a tracked doc when appropriate. Do not rely on chat context alone.

Include:

```text
Goal:
Implemented:
Changed:
Blocked:
Deferred:
Unverified:
Found — not in scope:
Smoke A:
Smoke B:
Checks run:
Next action:
```

If a root handoff file is ignored, mirror important status into a tracked audit/handoff doc.

---

## 12. Commit or push only if explicitly authorized

If commit/push is not explicitly authorized, do not stage, commit, or push.

If commit/push is explicitly authorized:

1. Run final checks first.
2. Stage explicit paths only; do not use `git add .`.
3. Verify raw diagnostics, build artifacts, local smoke outputs, secrets, and unrelated files are not staged.
4. Commit only after Smoke B and final validation pass.
5. Push only after commit succeeds and the working tree is reviewable.

If release/tag/publication is explicitly authorized, perform a separate release gate check according to repo policy. Do not infer release authorization from commit/push authorization.

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
BLOCKED                         cannot safely proceed due to unsafe/unauthorized entry condition or all P0s blocked
-->

## Goal

## Input basis

## Findings ledger
| # | Finding | Priority | Action | Status | Evidence | Follow-up |
|---|---|---:|---|---|---|---|

## Scope-creep register (found — not in scope)
| # | Issue | Location | Recommendation |
|---|---|---|---|
<!-- State “None found” explicitly if empty. -->

## Changes made

## Smoke A (baseline — pre-patch)
| Check | Command | Result | Evidence type | Pre-existing failure? |
|---|---|---|---|---|

## Smoke B (post-implementation)
| Check | Command | Result | Evidence type | Δ vs Smoke A | Remaining risk |
|---|---|---|---|---|---|

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
```

---

## Quality bar self-check

Run this internally before the final response. Any failing item must be fixed or marked `unverified` with reason.

- [ ] Every patch connects to a ledger item by number.
- [ ] Owner/source was patched, not nearest symptom.
- [ ] No broad rewrites outside audit scope.
- [ ] Meaningful check/evidence recorded for every changed item.
- [ ] Every ledger item has terminal status; zero `open` items remain.
- [ ] Deferred items have explicit reasons.
- [ ] Scope-creep register is populated or says `None found`.
- [ ] Smoke A recorded before mutation.
- [ ] Smoke B recorded after implementation.
- [ ] Broken baseline, if any, classified as target/unrelated/unclear.
- [ ] Exact notation/API/schema/contract strings preserved unless explicitly changed by audit.
- [ ] Verdict chosen by rubric, not intuition.
- [ ] Commit/push stance stated explicitly.
- [ ] Repo is left reviewable and non-broken.
```
