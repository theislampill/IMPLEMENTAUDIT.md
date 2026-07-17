# Fable review of PR #29 — Hansei lesson-lift decision and encoding activation

## Provenance statement

This review was produced end to end by **Claude Fable 5** (model id
`claude-fable-5`) on 2026-07-17 (session 09/16). The harness reported Fable 5
at session start and no substitution was observed. Every conclusion below
was re-derived from live GitHub state, exact Git objects, current source,
and executed probes against the production scorer.

## Identity proof (exact objects)

| Object | SHA |
|---|---|
| PR #29 head (`feat/i13-lesson-lift`) | `25faca789fc48c72de1e77ab28f60d7d79663dd3` |
| Merge commit on `main` | `60b26bf1622add6759b514e42db191777ea034a8` |
| Merge base (parent 1) | `55d0c44c69b9a0bec99e250e9c8212f31ed5f087` |
| `origin/main` at review time | `82297b0683e6b1379bfeee7568c965c143a358d4` |

- `git diff --exit-code 25faca7 60b26bf^2` — empty; merged tree
  byte-identical to reviewed head; `git diff --check` clean. Two commits;
  14 files, +201/−2 (PROTOCOL subsection, payload scorer
  `check-lesson-lift.sh`, seven fixtures, test, registries, CHANGELOG).

## Issue #13 and closure review

- Issue #13 (milestone v0.3.2.0), zero comments, closed
  2026-07-17T14:21:38Z by merge linkage; `updatedAt == closedAt`. No
  close-comment overclaim.
- CI at merge ran the new `tests/lesson-lift-contract.test.sh`.
- Acceptance adjudication (all executed): qualifying-closure-without-record
  fails; checker destination with missing target fails (claimed-vs-active);
  “easy to redo by hand” fails while a reasoned no-lift passes;
  “Recurrence prevented.” fails scoring; the one-off negative control
  passes with a single disposition line. The PROTOCOL subsection carries
  the bounded trigger, the nine-field record, the unification rule
  (record satisfies AGENTS_UPDATE_DECISION + CONTINUITY_DECISION duties),
  authority boundaries, and the closure-claims limitation (items 5–7
  only).
- **Supersession (documented):** PR #34 (`9ff0dfc`) hardened the scorer’s
  `grep|head|sed` field lookup against `set -e` early-death — a
  documented post-merge correction; no behavioral change for
  correctly-populated inputs. The scorer/test/fixtures are otherwise
  byte-unchanged since merge.

## Invariant adjudication (packet checks 1–6)

1. **One canonical record without competing records** — unification rule
   present; but nothing detected DUPLICATE `Lesson-lift:` records in one
   closure (Finding 2). CONFIRMED WITH FIX.
2. **Record distinguishes destination, authority, target, encoding type,
   activation, bounded no-lift reason** — the nine-field format is
   normative and fixtures exercise it; field distinctions verified in the
   scorer’s parsing. CONFIRMED.
3. **Claimed update verified in the active destination** — mechanized
   HALF-way: a checker/test destination claimed active must name an
   existing, non-empty target (missing target fails, executed). Whether a
   PRE-EXISTING target actually changed is NOT checked — and the
   scorer’s own comment overstated (“non-empty / changed”). Comment made
   honest; deeper change-detection recorded as residual (Finding 4).
4. **No-lift allowed for a one-off but requires a reason** — the
   insufficient-phrase rule worked, but an EMPTY reason passed
   (Finding 3), and an innocent one-off mentioning “no recurrence
   expected” was forced into ceremony by the loose qualifying scan
   (Finding 5). Both fixed. CONFIRMED WITH FIXES.
5. **Closure may claim encoding/activation, never prevention** — the
   canonical phrase failed, but worded variants (“the recurrence has
   been prevented”, “prevents recurrence”) PASSED (Finding 1) — the
   packet’s hidden-variants case. Fixed; intent forms (“meant to
   prevent”, “without preventing”) remain legal, verified against all
   shipped PASS fixtures. CONFIRMED WITH FIX.
6. **Legacy run roots remain valid** — the scorer is invoked per closure
   record, not per run root; legacy roots carry no `Lesson-lift:` records
   and are untouched by any validator change. CONFIRMED.

## What was executed (evidence)

- `bash tests/lesson-lift-contract.test.sh` — green at `main`
  (contract + 4 fail + 3 pass fixtures).
- Probe battery against the production scorer (disposable records):
  - “The recurrence has been prevented …” → **ACCEPTED** (defect).
  - “This encoding prevents recurrence …” → **ACCEPTED** (defect).
  - Duplicate competing `Lesson-lift:` records → **ACCEPTED** (defect).
  - `reason = ;` (empty) on a no-lift decision → **ACCEPTED** (defect).
  - One-off `No-lift:` line saying “no recurrence expected” →
    **REJECTED** (over-trigger; forced ceremony on a trivial fix).
  - CRLF variants of a PASS and a FAIL fixture → correct verdicts.
  - Missing final newline → correct verdict.
  - Pre-existing unchanged target claimed active → accepted (recorded
    limitation; fixture family only covers missing/empty targets).
- Post-fix: extended test RED against the unfixed scorer (first failure:
  hidden prevented-variant), GREEN after (4 fail + 3 pass + 5
  adversarial); all 53 repo suites green; `verify-package.sh` ok;
  `git diff --check` clean.

## Findings by severity

**Finding 1 — MEDIUM (forbidden-claim regex too literal; fixed).**
The prevention-claim scan matched only adjacency forms
(`recurrence prevented`, `prevented recurrence`, `will/cannot recur`).
Ordinary wordings — “the recurrence has been prevented”, “prevents
recurrence” — passed scoring, defeating the issue’s bolded acceptance
criterion. Fixed with bounded within-sentence patterns; intent forms
stay legal (verified against every shipped PASS fixture, including
“without preventing any reachable recurrence”).

**Finding 2 — MEDIUM (competing records undetected; fixed).**
Two `Lesson-lift:` records in one closure — with conflicting decisions —
passed. The contract’s core sentence is “one qualifying lesson produces
exactly ONE canonical record”; now enforced by count.

**Finding 3 — LOW-MEDIUM (empty no-lift reason accepted; fixed).**
Only the specific phrase “easy/cheap/trivial to redo by hand” failed; an
empty `reason =` field — the barest possible “no” — passed. Now a
no-lift decision inside a record requires a non-empty reason (the
one-off `No-lift:` disposition line remains exempt, per the bounded
trigger).

**Finding 4 — LOW (overstating comment; honesty fix + residual).**
The scorer checked target existence/non-emptiness while its comment
claimed “non-empty / changed”. A pre-existing unchanged target claimed
active passes — undetectable from a single closure record without a
baseline tree. Comment corrected to what the code does; change
verification remains the closure author’s PROTOCOL item-6 duty; deeper
mechanization (baseline-aware diff) left to the owner as an option.

**Finding 5 — LOW-MEDIUM (over-trigger on the disposition line; fixed).**
The qualifying scan matched trigger words anywhere — including the
one-off `No-lift:` disposition line itself, so “No-lift: one-off typo;
no recurrence expected” FAILED, forcing lift ceremony on exactly the
trivial case the bounded trigger exempts. The scan now excludes
`No-lift:` disposition lines; trigger words elsewhere still qualify
(fail-closed preserved — the qualifying-no-record fixture still fails).

**Finding 6 — INFO.** PR #34’s `set -e` hardening of this scorer is a
documented, behavior-preserving supersession. PR body claims otherwise
verified exactly (nine fields, seven fixtures, registries, closure-claim
limits).

## Corrections made (this branch)

Product payload bytes changed: **yes**
(`skills/implementaudit/scripts/check-lesson-lift.sh`), plus its test:

1. Widened forbidden-claim patterns (worded prevented-variants;
   `prevents recurrence`), intent forms exempt.
2. Duplicate `Lesson-lift:` records fail (one canonical record).
3. Empty no-lift reason fails inside a record; `No-lift:` one-off line
   exempt.
4. Qualifying scan excludes `No-lift:` disposition lines (bounded
   trigger honored).
5. Comment honesty on the target check (existence/non-emptiness, not
   change detection).
6. `tests/lesson-lift-contract.test.sh` — five adversarial regressions
   (two hidden variants, duplicate records, empty reason, one-off with
   recurrence-word). RED pre-fix, GREEN post-fix.

## Residual risks and nonclaims

- Change-detection for pre-existing targets is not mechanized (needs a
  baseline tree the scorer does not have); PROTOCOL item 6 remains the
  authority, and the #9 evaluation measures live compliance.
- The qualifying scan is heuristic keyword matching: prose mentioning
  trigger words outside a `No-lift:` line still fail-closes into
  requiring a record — over-inclusion is retained deliberately in the
  safe direction.
- Natural language is unbounded: prevention claims phrased with entirely
  novel vocabulary (“this class is extinct”) can still evade a regex;
  the scorer narrows the gap, the contract text owns the rule, and #9
  E-scoring measures the behavior.
- No claim that lesson-lift improves recurrence rates — the issue’s own
  evidence limit (future recurrence windows / #9).

## Verdict

**CONFIRMED_WITH_FIXES.**

The lesson-lift contract — bounded trigger, nine-field canonical record,
unification of the two legacy markers, authority boundaries, activation
claims limited to closure-time facts — is faithfully implemented, and
the scorer’s core verdicts reproduce under execution including CRLF and
no-final-newline inputs. Five scorer gaps found by adversarial
execution (hidden prevention wordings, competing records, empty no-lift
reason, disposition-line over-trigger, overstating comment) are fixed
minimally and regression-locked.

Integrator notes: changes shipped payload bytes
(`check-lesson-lift.sh`) — release-asset hash changes at integration;
re-run verify-package. Note PR #34 already touched this file (the
`set -e` hardening) — this branch builds on the current `main` version,
so no conflict. No overlap with other review branches except the
distinct report under `docs/reviews/v0.3.2.0/`.
