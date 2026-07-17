# Fable review of PR #33 — Experimental bounded-convergence reference and adoption gate

## Provenance statement

This review was produced end to end by **Claude Fable 5** (model id
`claude-fable-5`) on 2026-07-17 (session 13/16). The harness reported Fable 5
at session start and no substitution was observed. Every conclusion below
was re-derived from live GitHub state, exact Git objects, current source,
and executed mutation probes against the production checker.

## Identity proof (exact objects)

| Object | SHA |
|---|---|
| PR #33 head (`feat/i11-convergence-mode`) | `b7ad3a271261491da34c429d4ebe7e061820f3fa` |
| Merge commit on `main` | `e6daee7c10393a88d0d86d04589b33904f7a3717` |
| Merge base (parent 1) | `2a5e20e23b1ab3d474b240bbdc43698cb23ec026` |
| `origin/main` at review time | `82297b0683e6b1379bfeee7568c965c143a358d4` |

- `git diff --exit-code b7ad3a2 e6daee7^2` — empty; merged tree
  byte-identical to reviewed head; `git diff --check` clean. Single
  commit; 9 files, +171/−0 (optional reference, SKILL pointer, two
  adoption-gate fixtures, structural test, registries, CHANGELOG). Zero
  post-merge drift on the reference, test, or fixtures.

## Issue #11 and closure review — the packet’s central concern

- Issue #11 (EXPERIMENTAL status header; milestone v0.3.2.0), closed
  2026-07-17T15:10:46Z by merge linkage.
- **The PR #33 body overclaimed:** it characterized the disposition as
  “evidence-backed non-adoption into core” while stating in the same
  paragraph that the model evaluation “has not been run”. Not-tested is
  neither adoption nor evidence-backed rejection.
- **Already remediated by the owner (documented, pre-dating this
  session):** a post-closure issue comment (2026-07-17T16:01:42Z,
  “Provenance + wording correction (genuine-Fable re-audit)”) explicitly
  **retracts** that phrasing and records the accurate disposition:
  delivered scope = optional reference + fixtures (what the issue defines
  as its deliverable); **core adoption DEFERRED, not decided** — the gate
  is a #9 model evaluation, blocked at the time by quota, verdict
  delegated to the #9 program. The issue stays closed because its own
  scope gates adoption elsewhere (“No core-protocol change until the
  adoption gate passes”).
- **Grep-verified:** the phrase “evidence-backed non-adoption” (and any
  “non-adoption” token) appears NOWHERE in the merged tree or current
  `main` product bytes — it lived only in the immutable PR description.
  The reference file itself says throughout: n=1, hypothesis, “has not
  yet been run, so this mode remains optional and non-core”.
- Packet invariants 5–6 are therefore satisfied: the close criteria read
  exactly (delivery scope vs core-adoption gate), and the overclaim is
  retracted where it can be (the PR body is immutable history; the
  correction is the durable record).

## Invariant adjudication (packet checks 1–6)

1. **Optional, near-zero burden** — the reference lives in `references/`
   (progressive-disclosure lane), the SKILL pointer says “load ONLY when
   its trigger fires… Not core protocol; not part of the ordinary run”,
   and the test asserts the mode body is NOT inlined into the bootloader
   (executed: leaking a body phrase into SKILL.md fails). CONFIRMED.
2. **Bounded trigger** — two-or-more same-family rejections OR a #7
   under-specified-state-space judgment; the reference explicitly forbids
   the mode for single faults (“an enumeration artifact there is
   over-process”). CONFIRMED.
3. **Single-fault negative control** — the control fixture declares
   `expected_trigger: no` / `expected_enumeration_dimensions: 0` and
   scores enumeration as over-process; flipping it to `yes` fails the
   checker (executed). CONFIRMED.
4. **No unmeasured benefit claims** — the reference states n=1,
   single-project, transcript-verified, gate not run, non-core;
   “must beat the serial-loop baseline” appears only as a gate
   criterion. Stripping the EXPERIMENTAL marking fails the checker
   (executed). CONFIRMED.
5. **Close criteria read exactly** — delivery scope closed; adoption
   gate open and delegated; owner comment is the authoritative record.
   CONFIRMED.
6. **No surviving “evidence-backed non-adoption” statement** — retracted
   by the owner; zero occurrences in product bytes. CONFIRMED
   (remediated upstream).

## What was executed (evidence)

- `bash tests/convergence-mode-contract.test.sh` — green at `main`.
- Mutation battery (scratch tree carrying the production checker,
  reference, SKILL.md, fixtures; each mutation must fail the checker):
  - Mode body leaked into bootloader SKILL.md → detected.
  - Negative-control fixture flipped to `expected_trigger: yes` →
    detected.
  - “must NOT trigger” rule stripped from the reference → detected.
  - EXPERIMENTAL marking stripped (mode presented as standard policy) →
    detected.
  - Enumeration-artifact step removed → detected — and this probe
    demonstrated the checker’s robustness: it flattens newlines before
    grepping, so line-wrapped occurrences my first line-based mutation
    missed were still caught; only a multiline-aware removal produced
    the expected failure. (Two earlier apparent misses were incomplete
    mutations on the review side, not checker gaps.)
  - Baseline scratch tree green (6/6 genuine mutations detected).
- All 53 repo suites green in the review worktree; `verify-package.sh`
  ok; `git diff --check` clean.

## Findings by severity

**Finding 1 — INFO (already remediated).** The PR-body overclaim
(“evidence-backed non-adoption”) was real and is exactly the packet’s
concern — and the owner’s post-closure correction retracted it with the
accurate deferred-not-decided disposition before this session ran. The
immutable PR body cannot be edited; the comment is the durable
correction; product bytes never carried the phrase.

**Finding 2 — INFO (design note).** The shipped test is explicitly
structural (“the model-in-the-loop adoption gate itself is a #9
evaluation and is NOT run here”) and says so in its own header — the
honest scope the packet’s keyword-vs-transition concern asks for. The
fixtures encode expected state transitions declaratively
(`expected_trigger`, `expected_enumeration_dimensions`) for the future
#9 scorer; behavioral verification is correctly deferred, not faked.

**Finding 3 — INFO.** All PR-body technical claims reproduce: on-trigger
loading, no bootloader leakage, fixture pair shape, registries, CI
execution at merge.

## Corrections made (this branch)

**None — report only.** The single genuine problem was already corrected
by the owner in the issue record; no product byte carries a defect
attributable to this PR. Per the review protocol, no change is
manufactured. This branch adds only this report.

## Residual risks and nonclaims

- The adoption gate remains unrun; nothing here claims the mode helps or
  harms — that verdict belongs to the #9 evaluation, as the issue and
  the owner’s correction both state.
- The structural checker pins text and fixture declarations; live
  trigger discipline (does a model actually refrain on single faults?)
  is #9-measured.
- The PR description remains immutable GitHub history containing the
  retracted phrase; readers must follow the issue comment — this report
  is a second pointer.

## Verdict

**CONFIRMED.**

The delivered bytes match the issue’s explicit experimental design
exactly: an optional, trigger-gated reference with zero ordinary-run
burden, honest n=1/not-run status throughout, a bounded trigger with an
explicit single-fault prohibition, both adoption-gate fixtures, and a
structural checker that detected every genuine mutation thrown at it.
The one overclaim lived only in the immutable PR description and was
retracted by the owner with a documented correction before this review.

Integrator notes: report-only branch; no product bytes changed; no file
overlap with any other review branch except the distinct report under
`docs/reviews/v0.3.2.0/`.
