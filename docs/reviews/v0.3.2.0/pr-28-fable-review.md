# Fable review of PR #28 — Second-order review of rules, criteria, validators, and routes

## Provenance statement

This review was produced end to end by **Claude Fable 5** (model id
`claude-fable-5`) on 2026-07-17 (session 08/16). The harness reported Fable 5
at session start and no substitution was observed. Every conclusion below
was re-derived from live GitHub state, exact Git objects, current source,
and executed mutation probes against the production checker.

## Identity proof (exact objects)

| Object | SHA |
|---|---|
| PR #28 head (`feat/i7-second-order-recurrence`) | `f92f9fa97a57dbebe494f55676e0a4595eee5c8a` |
| Merge commit on `main` | `55d0c44c69b9a0bec99e250e9c8212f31ed5f087` |
| Merge base (parent 1) | `aeed2684490857ff87bfa5929a799357edaa8a0b` |
| `origin/main` at review time | `82297b0683e6b1379bfeee7568c965c143a358d4` |

- `git diff --exit-code f92f9fa 55d0c44^2` — empty; merged tree
  byte-identical to reviewed head; `git diff --check` clean. Single
  commit; 11 files, +141/−1 (PROTOCOL 2b step + Hansei field, five
  scored fixtures, new test, CI/package registration, CHANGELOG — plus
  one stray duplicate fixture, see below).

## Issue #7 and closure review

- Issue #7 (milestone v0.3.2.0), zero comments, closed 2026-07-17T14:09:46Z
  by merge linkage; `updatedAt == closedAt`. No close-comment overclaim.
- CI at merge ran the new `tests/andon-escalation-judgment.test.sh`.
- Acceptance adjudication: the escalation text contains the judgment step
  (2b) with all three triggers; all five required fixtures exist with the
  required grep-scored judgment tokens; each fixture is substantive
  (evidence + judgment, not token-stuffing) — verified by reading and by
  executing the checker.
- **Supersession (documented, not silent):** the PR accidentally shipped a
  sixth, duplicate fixture (`fixtures/governing-rule/same-class-recurrence.md`,
  vs the PR body’s “five scored fixtures”). PR #34 (`9ff0dfc`,
  “post-merge correction from the genuine-Fable re-audit”) dropped the
  stray. Current `main` carries exactly the five referenced fixtures; the
  test never referenced the stray. Classified as a corrected packaging
  slip, already remediated upstream of this review.
- No later commit altered the 2b step or the fixtures; the test passes on
  current `main`.

## Invariant adjudication (packet checks 1–6)

1. **Trigger set** — (a) same-class recurrence with cited rows,
   (b) first-occurrence direct evidence of a rule-produced/concealed
   defect, (c) cross-class recurrences sharing one invariant: all three
   present in 2b and each embodied by a fixture. CONFIRMED.
2. **Green validator as suspected component** — the
   first-occurrence-misscoped-validator fixture records a PASSING
   validator judged `governing-rule-defect (validator)` because its PASS
   is not truth-connected to the claimed property; composes with
   PR #25’s “is the check testing the evidence property the claim needs”.
   CONFIRMED.
3. **Record identifies the governed component** — judgment tokens
   `case-defect` / `governing-rule-defect (class | standard | validator |
   route)`, matching the issue’s enum exactly. Note: the *trigger* list
   includes `criterion`, but the judgment enum does not — a
   criterion-produced defect routes through the separate “reframe the
   criterion” escalation path (step 3); `authority assignment` is
   PR #32’s later domain (parameter-bound authorization). Recorded as an
   observation, not a defect: the merged bytes match the issue’s own
   vocabulary. CONFIRMED.
4. **Rejection requires a recorded reason** — normative sentence (“a bare
   ‘no’ fails the contract”), Hansei field
   (“suspected / rejected with recorded reason”), and the
   reasoned-rejection fixture’s `Rejection reason:` are all
   checker-asserted. CONFIRMED.
5. **No automatic governance rewrite** — rule repairs route through
   poka-yoke and AGENTS_UPDATE_DECISION (owner-gated); issue non-goal
   “no automatic taxonomy editing” respected; no marker changes.
   CONFIRMED.
6. **Correct-by-luck as first-occurrence trigger** — explicit in 2b,
   with neighboring-perturbation probes admissible even when the answer
   was correct, and answer-correctness vs pathway-adequacy kept as
   separate judgments; fixture records the exact verdict phrase.
   CONFIRMED.

## What was executed (evidence)

- `bash tests/andon-escalation-judgment.test.sh` — green on `main`.
- Mutation probes (scratch tree carrying the production checker,
  PROTOCOL, and fixtures; one mutation at a time; checker must fail):
  - Rejection reason removed from the reasoned-rejection fixture
    (bare-no) → detected.
  - `Governing-rule judgment:` token stripped from the same-class
    fixture → detected.
  - “REQUIRES a recorded reason” rule stripped from PROTOCOL → detected.
  - `correct-by-luck` stripped from PROTOCOL → detected.
  - `neighboring-perturbation` admissibility stripped → detected.
  - Baseline scratch tree green (6/6 mutations detected).
- Fixture content review: each of the five demonstrates its situation
  with evidence (cited prior row #4; shared invariant naming; probe-based
  rejection reason; perturbation flip; truth-connection failure).
- All 53 repo suites green in the review worktree; `verify-package.sh`
  ok; `git diff --check` clean.

## Findings by severity

**Finding 1 — INFO (already remediated upstream).** The stray duplicate
fixture shipped by this PR was removed by PR #34 with a documented
rationale; no action needed.

**Finding 2 — INFO (vocabulary observation; no fix).** The judgment-token
enum omits `criterion` (present in the trigger list) and `authority
assignment` (the packet’s broader component list). This matches the
issue’s own enum byte-for-byte; criterion repairs have a dedicated
escalation path, and authority assignment gained its own machinery in
PR #32. Widening the enum would change contract vocabulary beyond the
reviewed issue and ripple into the #13 lesson-routing consumers — left
to the owner.

**Finding 3 — INFO (recorded limitation).** “Model blames the rule
without evidence” is not mechanically detectable by grep-scored
fixtures; the contract text demands trigger evidence, and live judgment
quality is #9 evaluation territory. Behaviorally governed.

## Corrections made (this branch)

**None — report only.** No defect attributable to this PR survived
execution; per the review protocol, no product change is manufactured.
This branch adds only this report.

## Residual risks and nonclaims

- The checker pins contract text and fixture tokens; it cannot score a
  live model’s judgment quality or evidence discipline (the #9
  evaluation measures that).
- The judgment enum vs trigger-list asymmetry (Finding 2) is a
  vocabulary observation for the owner, not a validated defect.
- No claim about PR #32’s authority machinery or PR #29’s lesson
  routing beyond their non-interference with this invariant.

## Verdict

**CONFIRMED.**

The second-order review contract is faithfully and substantively
implemented: all three triggers, the green-validator suspicion path,
component-identifying judgment tokens, the reasoned-rejection
requirement, owner-gated repair routing, and correct-by-luck /
perturbation admissibility are present, fixture-embodied, and pinned by
a checker that detected all six adversarial mutations. The one packaging
slip (stray fixture) was already corrected by PR #34 with documented
provenance.

Integrator notes: report-only branch; no product bytes changed; no file
overlap with any other review branch except the distinct report under
`docs/reviews/v0.3.2.0/`.
