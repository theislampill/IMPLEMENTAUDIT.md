# Fable review of PR #27 — Occurrence resolution, audit completion, and residual disposition

## Provenance statement

This review was produced end to end by **Claude Fable 5** (model id
`claude-fable-5`) on 2026-07-17 (session 07/16). The harness reported Fable 5
at session start and no substitution was observed before or during any
mutation on this branch. Every conclusion below was re-derived from live
GitHub state, exact Git objects, current source, and executed adversarial
run roots against the production validator.

## Identity proof (exact objects)

| Object | SHA |
|---|---|
| PR #27 head (`feat/i6-route-sufficient`) | `f624d0250a1994a97b71da9fd6f0f937d85a9736` |
| Merge commit on `main` | `aeed2684490857ff87bfa5929a799357edaa8a0b` |
| Merge base (parent 1) | `1aec235b2cddcac20badedae97261631886bae2c` |
| `origin/main` at review time | `82297b0683e6b1379bfeee7568c965c143a358d4` |

- `git diff --exit-code f624d02 aeed268^2` — empty; merged tree
  byte-identical to reviewed head; `git diff --check` clean. Single
  commit; 5 files, +125/−0 (validator, PROTOCOL, STATE, test, CHANGELOG).

## Issue #6 and closure review

- Issue #6 (milestone v0.3.2.0), zero comments, closed 2026-07-17T14:01:02Z
  by merge linkage; `updatedAt == closedAt`. No close-comment overclaim.
- CI at merge ran the extended run-root validation test.
- Acceptance adjudication (all four fixtures re-executed, plus the
  invalid-token controls): quarantined-partial, owner-transferred,
  risk-accepted, and invalid-disposition/invalid-occurrence-token all
  behave as specified. The fourth criterion’s scoring half (“full-
  resolution language with any consequential residual unresolved fails”)
  is encoded where the issue said it would be: the PROTOCOL
  AUDIT_COMPLETE gate names it false-closure, and eval fixture **E3**
  (“Route-sufficient action + closure semantics (per #6)”) carries the
  normative scoring — verified present with pass/fail transcripts.
- Supersession: later PRs (#28–#33) touched the same files; the #6
  validator block is byte-unchanged and PR #31 (issue #14) layers
  success-surface indexing on top without altering these semantics.
  Effective current behavior re-verified at `82297b0`.

## Invariant adjudication (packet checks 1–6)

1. **Three independent axes, never merged** — separate STATE.md
   representations (occurrence-resolution line; marker machinery;
   per-residual rows); executed control: an `unresolved` occurrence with
   a properly dispositioned consequential residual is a VALID state.
   CONFIRMED.
2. **Truthful AUDIT_COMPLETE with deferred/transferred/risk-accepted
   residuals** — extended gate: every consequential residual
   non-`unresolved` AND completion language claims audit-completion only;
   full-resolution claim over an unresolved consequential residual is
   named false-closure (linking to the session-02 taxonomy). CONFIRMED
   (prose gate; scoring lives in E3 as designed).
3. **Verification status not stored in the disposition enum** — the
   disposition enum matches the issue exactly; verified/unverified
   closure-surface status lives in PR #31’s separate index.
   `validated-resolved` is a terminal disposition (resolution + validation
   evidence), not a verification-status token; noted, not a defect.
   CONFIRMED.
4. **Every material residual has explicit disposition and owner/route
   where required** — disposition tokens were enforced, but the
   “where required” half was not: **a `transferred` residual with owner
   `-` and a `risk-accepted` residual with an empty policy cell both
   PASSED the validator** (Findings 1). Fixed. CONFIRMED WITH FIXES.
5. **Fully-resolved claim requires success-surface evidence** — the gate
   text requires it; mechanical surface indexing is PR #31’s layer
   (reviewed in a later session); E3 scores the language rule. CONFIRMED
   at this PR’s scope.
6. **No marker presence alone establishes closure** — the AUDIT_COMPLETE
   gate adds residual-disposition and language conditions beyond markers.
   CONFIRMED (behavioral; marker-order tests unchanged).

## What was executed (evidence)

- `bash tests/run-root-validation.test.sh` — green at `main` (6a–6e).
- Adversarial run roots against the production validator:
  - `transferred` with owner cell `-` → **ACCEPTED** (defect; fixed).
  - `risk-accepted` with empty policy cell → **ACCEPTED** (defect;
    fixed).
  - `unresolved` occurrence + dispositioned residual → accepted
    (truthful independent axes).
  - Invalid disposition (`resolved-ish`) and invalid occurrence token
    (`mostly-resolved`) → rejected (shipped controls).
- `eval/fixtures/E3/` presence and content verified (route-sufficient +
  closure-semantics scoring with pass/fail transcripts).
- Post-fix: regressions 6f/6g RED against the unfixed validator
  (`res_noowner expected FAIL`), GREEN after; control 6h green; all 53
  repo suites green; `verify-package.sh` ok; `git diff --check` clean.

## Findings by severity

**Finding 1 — MEDIUM (owner/route requirement unenforced; fixed).**
The contract text defines `transferred` as “name the receiving owner”
and `risk-accepted` as “cite the policy” in the same breath as the
tokens, and the issue’s acceptance fixtures pair the disposition with a
named owner/policy — but the validator checked tokens only. A transfer
nobody receives, or a risk acceptance with no authority, passed
silently: exactly the two packet robustness cases, and the mechanism by
which a residual evaporates while the bookkeeping looks closed. Fixed
minimally: rows with `transferred`/`risk-accepted` require a non-empty,
non-`-` Owner/policy-ref cell. Other dispositions unchanged
(`owner-assigned` semantics live in the cell by convention; enforcing it
was not contract text). Regression-locked (6f/6g), with an
axes-independence control (6h).

**Finding 2 — INFO (recorded limitations; no fix).**
A residual that is silently OMITTED from the table is mechanically
undetectable (the validator cannot know what was never recorded) — the
countermeasure is behavioral (gate text + E3 scoring + receiving-side
handoff inspection from PR #30). “Consequential” classification and
completion-language truthfulness are owner/model judgments scored by E3,
not validated per run root.

**Finding 3 — INFO.** PR body claims verified exactly: three
representations, route-sufficient rule (contain first, ≥2 candidate
causes or stated reason, named residual rows, partial-by-design), gate
extension, STATE fields, token checks scoped to new-format roots with
legacy roots unchanged, four fixtures + invalid-token control.

## Corrections made (this branch)

Product payload bytes changed: **yes**
(`skills/implementaudit/scripts/validate-run-root.sh`), plus its test:

1. `validate-run-root.sh` — `transferred`/`risk-accepted` residual rows
   require a non-empty, non-`-` Owner/policy-ref cell, naming offending
   rows.
2. `tests/run-root-validation.test.sh` — 6f (transferred, no owner →
   fail), 6g (risk-accepted, no policy → fail), 6h (unresolved
   occurrence + dispositioned residual → pass). RED pre-fix, GREEN after.

## Residual risks and nonclaims

- Omitted residuals, consequentiality judgments, and completion-language
  truthfulness are behaviorally governed (gate + E3 + #15 handoff
  inspection), not mechanically validated per run root.
- The owner/policy cell is checked for presence, not validity — a
  fabricated owner name passes; naming authenticity is an owner concern.
- No claim about PR #31’s success-surface layer beyond its consistency
  with these axes (reviewed separately in its own session).

## Verdict

**CONFIRMED_WITH_FIXES.**

The three-axis closure model, route-sufficient rule, extended
AUDIT_COMPLETE gate, and token validation are faithfully implemented and
survived execution, including the truthful-partial-states controls. The
“owner/route where required” half of the residual contract was
unenforced — demonstrated by execution for both `transferred` and
`risk-accepted` — and is now enforced minimally with deterministic
regressions.

Integrator notes: changes shipped payload bytes
(`validate-run-root.sh`) — **the same file is also modified by the
session-06 branch (`review/fable-pr-26`, PR #42) in a different block**
(Andon Class cell vs residual rows); both edits are additive and
textually non-overlapping, but integrate #42 and this branch in
dependency order and re-run `verify-package.sh` after each. Reports
under `docs/reviews/v0.3.2.0/` remain distinct files.
