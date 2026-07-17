# Fable review of PR #36 — B3 supplementary context-epoch fixture

## Provenance statement

This review was produced end to end by **Claude Fable 5** (model id
`claude-fable-5`) on 2026-07-17 (session 16/16 — the final session of the
review program). The harness reported Fable 5 at session start and no
substitution was observed. Every conclusion below was re-derived from live
GitHub state, exact Git objects, current source, and executed probes
against the production scoring engine.

## Identity proof (exact objects)

| Object | SHA |
|---|---|
| PR #36 head (`feat/b3-context-epoch-fixture`) | `4f878a765322cd7453b47f51ceac41e3137d43a9` |
| Merge commit on `main` | `82297b0683e6b1379bfeee7568c965c143a358d4` |
| Merge base (parent 1) | `32fa651ffdd8f36245e918ecf3628e1f2046678b` |
| `origin/main` at review time | `82297b0683e6b1379bfeee7568c965c143a358d4` (the merge IS current main) |

- `git diff --exit-code 4f878a7 82297b0^2` — empty; merged tree
  byte-identical to reviewed head; `git diff --check` clean. Two commits;
  5 files, +106/−4 (fixture.json, pass/fail transcripts, README
  supplementary statement, CHANGELOG).

## Issue #35 and closure review

- Issue #35 is **OPEN** — correctly: PR #36 is fixture-only per the
  sequencing note and does NOT close the issue (no `Closes` keyword; the
  body says the product behavior comes in a later PR after the B3
  pre-change missions). Nothing was closed, on CI or otherwise.
- The issue’s design contract was reviewed in session 15
  (`issue-35-fable-design-review.md`, CONFIRMED_WITH_FIXES) with one
  issue-body amendment; this session adjudicates the fixture against
  that contract.

## Invariant adjudication (packet checks 1–6)

1. **Supplementary, never in the primary aggregate** — the fixture
   carries `supplementary: true` AND a self-describing
   `not_in_primary_campaign` sentinel; `eval/README.md` states B3 “is
   deliberately NOT part of the frozen 14-fixture primary campaign and
   must never be folded into the primary aggregate.” The primary
   campaign runner itself lives in the private evaluation custody
   (correctly outside this repo and this review’s reach); the
   product-side machinery (selftest/runner dry-run) validates B3 without
   any aggregate to pollute. CONFIRMED at the product boundary; the
   private campaign list is a recorded nonclaim.
2. **Pass/fail transcripts under independent rescoring** — executed
   directly against `scoring.score`/`scoring.overall`: PASS → True,
   FAIL → False (all five properties fail on the FAIL transcript, each
   for its own reason). CONFIRMED.
3. **Required behaviors encoded** — boundary provenance (the five honest
   tokens), live-state read before mutation, satisfied-one-shot
   classification, continuation from ANDON 251, and no duplicate
   mutation are the five required properties; capsule generation appears
   in `expected_correct_behavior` and the PASS transcript but is not a
   scored property — adjudicated below (Finding 2, carrying session
   15’s handoff). CONFIRMED with the documented scope note.
4. **Standing constraints survive** — issue #35 negative controls 4–5;
   B3 is the single stale-steer reproducer and does not seed a standing
   constraint, so this is contract-test territory per the issue’s
   acceptance criteria, not a B3 scoring gap. CONFIRMED as designed
   scope.
5. **Owner reopen not suppressed** — same: negative control 3 of the
   issue; B3’s seed contains no reopen event. The fixture’s absent-rule
   correctly allows *negated* and *quoted* references (see Finding 1
   fix) so a future reopen-fixture will not collide with this pattern.
   CONFIRMED as designed scope.
6. **No pass by keyword parroting** — executed: scoring the mission text
   itself fails overall (provenance and live-read properties cannot be
   satisfied by mission echo); a summary-only transcript fails on the
   live-read property. Full keyword-stuffing beyond mission text remains
   theoretically possible — an inherent property of transcript-regex
   scoring shared by every fixture in the library, bounded in real
   missions by the host-event authority chain (#21/H37) and the
   host-checks machinery. CONFIRMED with the recorded inherent
   limitation.

## What was executed (evidence)

- Independent rescoring of both transcripts via the production scoring
  engine (P1: pass=True, fail=False with per-property detail).
- **Negation-blindness probe (packet-named case):** appending
  “I will not re-execute ANDON 150; it stays closed.” to the PASS
  transcript **flipped it to FAIL** — `execut(e|ing)` matched inside
  the negated “re-execute” (defect; fixed).
- Mission-echo-only transcript → overall FAIL (correct).
- Summary-only transcript (no live read) → FAIL on
  `live_state_read_before_mutation` (correct).
- Unknown-keys inertness: stripping `supplementary` and
  `not_in_primary_campaign` leaves both verdicts unchanged (correct).
- Replacement-pattern validation matrix: seven forbidden action forms
  still match (apply/execute/executed/re-execute/reopen/re-fix/perform);
  seven legal forms stay legal (quoted steers, `not`/`never`/`won't`
  negations, terminal statements).
- Red→green: with the OLD pattern and the negated sentence added to the
  PASS transcript, `eval/selftest.py` FAILS exactly on B3
  (evidence extract: `execute ANDON 150`); with the NEW pattern,
  selftest is green (16 fixtures) and `tests/eval-harness.test.sh`
  passes. All 53 repo suites green; `verify-package.sh` ok;
  `git diff --check` clean.

## Findings by severity

**Finding 1 — MEDIUM (negation blindness in the absent-rule; fixed).**
The `no_duplicate_mutation_of_satisfied` pattern matched the verb
substring inside negated forms: “I will not re-execute ANDON 150” — a
correct, even exemplary, statement — false-failed the transcript. Fixed
with negation lookbehinds (`not `/`never `/`n't `), a hyphen guard so
bare verbs no longer match inside `re-` compounds, and an explicit
`re-?execut` alternative so affirmative re-execution stays forbidden.
Quoted historical steers remain legal (the describes-text now says so
explicitly). Regression-locked structurally: the PASS transcript now
contains the negated sentence, so `eval/selftest.py` fails forever if
negation blindness returns.

**Finding 2 — LOW (session-15 handoff adjudicated; documented, no
schema change).** The issue’s B3 PASS text names capsule generation and
ambiguity-handoff; the fixture scores neither. Adjudication: for the
PRE-change baseline this is correct — immutable v0.3.1.0 has no capsule
to generate, and a required-but-unsatisfiable property would poison the
pre/post comparison. The capsule and ambiguity behaviors are covered by
the issue’s deterministic acceptance-criteria contract tests at
implementation time. Rather than adding scored-separately properties
(which would alter the fixture surface mid-review-set), this is
recorded here and in the describes-scope; the owner may add
`required: false` observation properties before the pre-change campaign
if post-change observability of the capsule via B3 missions is wanted.

**Finding 3 — INFO.** Baseline integrity is real: `supplementary: true`,
the self-describing sentinel key, the README prohibition, and the
14-fixture primary campaign left untouched (its definition lives with
the private campaign custody). The fixture-hash binding (#17/#21 chain)
means the B3 missions will bind whatever fixture bytes exist at run
time — **this branch must integrate before the B3 pre-change campaign
starts**, so the campaign binds the negation-robust fixture.

## Corrections made (this branch)

Product bytes changed: **yes** (eval fixture + transcript; not skill
payload — release-asset hash unaffected, eval tree is repo-side):

1. `eval/fixtures/B3/fixture.json` — negation-safe, quote-safe,
   re-compound-safe absent-rule pattern; describes-text states the
   negation legality explicitly.
2. `eval/fixtures/B3/transcript_pass.txt` — the negated sentence added,
   converting the shipped selftest into a standing regression against
   negation blindness. RED (old pattern) → GREEN (new pattern) proven.

## Residual risks and nonclaims

- The private campaign runner and the 84-mission primary aggregate are
  outside this repository and this review; the product-side exclusion
  evidence is the fixture keys + README + selftest scope.
- Transcript-regex scoring can in principle be keyword-stuffed by an
  adversarial model; real missions are additionally bound by host-event
  authority (#21) — B3 shares this boundary with the entire fixture
  library.
- The B3 pre-change missions have not run; nothing here claims any
  model behavior — this review hardened the measuring instrument only.

## Verdict

**CONFIRMED_WITH_FIXES.**

PR #36 delivers exactly what the sequencing note ordered: the B3
reproducer as a supplementary, primary-campaign-safe fixture with
faithful transcripts, inert extension keys, and honest README
treatment — and its scoring survived every probe except the
packet-named negation case, which is fixed and structurally
regression-locked. Issue #35 correctly remains open for the
pre-change → implement → post-change sequence.

Integrator notes: **integrate this branch before the B3 pre-change
campaign runs** (fixture-hash binding). Changes are eval-side only (no
skill payload; release-asset hash unchanged). No file overlap with any
other review branch except the distinct report under
`docs/reviews/v0.3.2.0/`. This completes the sixteen-session review
program: sixteen reports, sixteen draft review PRs (#37–#46, #54 and
following), verdicts: 3 × CONFIRMED (report-only: PRs #28, #33, #34),
13 × CONFIRMED_WITH_FIXES, 0 × REJECTED_PENDING_FIX.
