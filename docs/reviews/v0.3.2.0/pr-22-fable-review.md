# Fable review of PR #22 — Andon taxonomy, origin boundaries, and source-list consistency

## Provenance statement

This review was produced end to end by **Claude Fable 5** (model id
`claude-fable-5`) on 2026-07-17 (session 02/16). The harness reported Fable 5
at session start and no substitution was observed before or during any
mutation on this branch. The original PR #22 is treated as mixed-provenance
work; every conclusion below was re-derived from live GitHub state, exact Git
objects, current source, and executed adversarial mutations of the production
checker.

## Identity proof (exact objects)

| Object | SHA |
|---|---|
| PR #22 head (`feat/i1-andon-taxonomy`) | `b7fee4fde96d09d289014bc6d4085c266a4d2e9b` |
| Merge commit on `main` | `dae69015b0c1f065cbea8297588b7f93cc11eafd` |
| Merge base (parent 1) | `6931e2b2187d09677921aeea004625df9350dece` |
| `origin/main` at review time | `82297b0683e6b1379bfeee7568c965c143a358d4` |

- `git diff --exit-code b7fee4f dae6901^2` — empty; `git diff --exit-code
  b7fee4f dae6901` — empty: merged tree byte-identical to reviewed head.
- `git diff --check` clean. Single commit; 7 files, +162/−3:
  `validate.yml`, `CHANGELOG.md`, `verify-package.sh`, `SKILL.md`,
  `references/transcript-contract.md`, `templates/PROTOCOL.md`, and new
  `tests/andon-class-contract.test.sh`. The CI/package wiring was present in
  the PR even though the review packet’s minimum file list did not name it.

## Issue #1 and closure review

- Issue #1 (milestone v0.3.2.0) with two owner amendment blocks
  (2026-07-16): normative class-boundary definitions, revised test
  semantics (set equality + required membership, **no fixed total**),
  boundary fixtures, and Amendment 2 (blocked review channel =
  `transport-infrastructure`, preserve + reissue to the same authorized
  reviewer identity, never accept/reject).
- Zero issue comments; closed 2026-07-17T13:20:23Z by merge linkage
  (`Closes #1`). No close-comment overclaim exists.
- CI at merge: the PR itself wired the new test into `validate.yml` and
  `scripts/verify-package.sh`, and its green `package` check executed it.
- Acceptance criteria adjudication:
  1. “The new test exists, passes” — **verified by execution** (merge state
     and current `main`).
     “…and fails when any one file’s list is edited alone” — **false for
     3 of 39 class×file omissions at merge** (Finding 1). The PR body’s
     “Negative control verified” claim did not hold universally.
  2. “All three files list 13 identical classes” — **verified** (the
     enumerations themselves are correct and consistent; the defect is in
     the checker’s discrimination power, not the lists).
  3. SKILL.md budget — **verified exactly**: 388 lines / 17,911 bytes at
     merge (claimed identically in the PR body), within 450 / 22,000.
- Supersession: 11 later commits (PRs #23–#33) touched the three owner
  files — heavily for PROTOCOL.md (+223 lines) — but none touched the test,
  and the enumerations remained consistent (test passes on `main`). However,
  the later prose additions silently **amplified** Finding 1 (see below).

## Invariant adjudication (packet checks 1–6)

1. **Set equality by normalized value; no frozen total** — the test asserts
   set equality + `REQUIRED` membership and no fixed total (verified by
   reading and by the coordinated-drop execution). But for the two prose
   files the “set” was computed by a whole-file token grep, which does not
   measure the enumeration — CONFIRMED WITH FIXES (Finding 1).
2. **Transport/infrastructure vs process-level hung-command** — normative
   discriminating evidence pinned (cross-lane simultaneity, OS init/exit
   signatures, outage window vs single stalled command on a responsive
   host); both directions pinned by fixture rows. CONFIRMED.
3. **Misplacement (right layer, wrong instance) vs
   generated-artifact-mismatch (wrong layer)** — distinct and pinned by
   paired fixtures. CONFIRMED.
4. **False-closure (accounting collapse) vs evidence-mismatch (one claim,
   unsupporting evidence)** — distinct, explicitly including the case where
   every individually cited piece of evidence is genuine. CONFIRMED.
5. **Blocked review channel is never a verdict** — normative disposition
   (preserve non-verdict + reissue to the SAME authorized reviewer
   identity; never accept/reject) present and asserted by the test.
   CONFIRMED.
6. **No overlap with owner-unclear / policy-conflict /
   impossible-criterion / evidence-mismatch** — the three new classes name
   environment failure, instance misattachment, and closure accounting;
   none of the four existing classes covers those meanings, and the
   boundary text distinguishes the nearest neighbor in each case.
   CONFIRMED by reading (semantic judgment, not executable).

## What was executed (evidence)

- Production test on current `main` and at merge state: green
  (13 classes, 3 files consistent, 7 fixtures).
- **Full omission matrix** against the production checker: for each of the
  13 classes × 3 files, the class token was removed from that file’s
  enumeration region only, and the test executed (78 runs across the two
  states):
  - **Merge state: 3/39 omissions undetected** — `evidence-mismatch`
    dropped from SKILL.md’s enumeration (masked by the dogfood-rule
    mention at SKILL.md line ~68); `regression` or `evidence-mismatch`
    dropped from PROTOCOL.md (masked by “regression test” and other prose).
  - **Current `main`: 7/39 undetected** — SKILL/`evidence-mismatch`,
    PROTOCOL/`regression`, `owner-unclear`, `evidence-mismatch`,
    `transport-infrastructure`, `misplacement`, `false-closure` — because
    later PRs (#24 background contract, #26/#28 Andon changes, etc.) added
    incidental prose mentions of these tokens in PROTOCOL.md.
  - **Alias variants**: en-dash and hyphen aliases detected in both
    states; the space alias `transport infrastructure` in PROTOCOL.md was
    **undetected on current `main`** (masked by the incidental mention at
    PROTOCOL.md line ~339).
  - Fixture-class flip (reclassifying the “no verdict” row) and a
    coordinated three-file drop: detected in both states.
- After the fix: **all 42 mutations detected** (39 omissions + 3 aliases),
  plus the fixed test’s own built-in negative controls pass.
- Full repo suite: all 53 `tests/*.test.sh` green in the review worktree;
  `bash scripts/verify-package.sh` ok (it executes the modified test,
  including its negative controls); `git diff --check` clean.

## Findings by severity

**Finding 1 — MEDIUM (defect in PR #22’s checker; fixed).**
`prose_set()` tested each class token against the **entire file text** of
SKILL.md and PROTOCOL.md rather than their enumeration regions. Any
incidental prose mention of a class token masks an enumeration omission —
so the invariant the test claims to pin (“three identical enumerations”)
was only partially enforced: 3/39 single-file omissions were invisible at
merge (making the PR body’s universal negative-control claim false), and
ordinary later prose growth silently degraded it to 7/39 plus an
undetected spelling alias on current `main`. This is precisely the packet’s
“alias/spelling variant that passes a loose membership grep” robustness
case. The enumerations themselves were and are consistent — no product
payload text was wrong.

**Finding 2 — INFO.** The degradation mechanism (unrelated PRs adding
legitimate prose mentions of class names) means the checker’s power was
trending monotonically toward zero for the prose files; by v0.3.3.0 most
single-file omissions would have been undetectable. Structural cause, not
a one-off.

**Finding 3 — INFO.** Class semantics, boundary definitions, fixtures, and
the blocked-review-channel disposition faithfully implement the issue body
including both amendments; SKILL.md budget claim exact; CHANGELOG entry
accurate.

## Corrections made (this branch)

Product payload bytes changed: **no** (`skills/` untouched). Repo test
hardened: `tests/andon-class-contract.test.sh`:

1. Class sets for SKILL.md and PROTOCOL.md are now extracted from each
   file’s **enumeration region** (SKILL: the `` `Class:` `` paragraph;
   PROTOCOL: the “exactly one official class from …)” parenthetical), with
   fail-closed behavior when a region cannot be located.
2. Built-in **negative controls**: the checker re-runs itself against
   mutated copies encoding the exact blind spots found (drop
   `evidence-mismatch` from SKILL’s enumeration; drop `regression` from
   PROTOCOL’s; space-alias `transport-infrastructure` in PROTOCOL’s) and
   fails if any mutation is accepted. The test now takes an optional
   target-root argument for these inner runs; no caller changes needed
   (`validate.yml` / `verify-package.sh` invoke it argument-less).
3. Verified: three controls red against the old logic (the original
   matrix run), green post-fix; full 42-mutation matrix detected; all 53
   repo suites + `verify-package.sh` green.

## Residual risks and nonclaims

- The checker pins **text**, not model behavior: whether the taxonomy
  improves live classification remains untested until the
  model-in-the-loop evaluation (issue #9) — the issue’s own stated
  evidence limit, unchanged by this review.
- Region extraction depends on the two prose anchors (“`Class:` is an
  abnormality class…”, “exactly one official class from…”). If a future
  rewrite rewords them, the test fails closed (loudly) rather than
  passing silently — that is the intended direction of failure.
- Invariant check 6 (semantic non-overlap) is a reading judgment, not an
  executable property.
- Cross-session note: this session’s CI Gemba exposed an
  evidence-mismatch in the session-01 report (it claimed CI does not run
  the eval suites; validate.yml’s `eval-harness.test.sh` does). Corrected
  in commit `4402508` on `review/fable-pr-21`. Recorded here because the
  discovery evidence belongs to this session.

## Verdict

**CONFIRMED_WITH_FIXES.**

The taxonomy, boundary definitions, fixtures, disposition rule, and
tri-file consistency are genuine and correctly implemented; the
enumerations are consistent in both the merged and current trees. The
consistency **checker** under-enforced its invariant (whole-file grep) —
demonstrated by execution at both states, worsened by later drift — and is
hardened on this branch with region-scoped extraction plus embedded
negative controls, with no change to product payload bytes.

Integrator notes: this branch touches only
`tests/andon-class-contract.test.sh` and adds this report. No overlap with
the session-01 branch (`review/fable-pr-21`) except both branches carry
`docs/reviews/v0.3.2.0/` files (distinct filenames; trivial merge). Later
sessions reviewing PRs #26/#28 (Andon-adjacent) should note the class
enumerations are already re-verified consistent here as of `82297b0`.
