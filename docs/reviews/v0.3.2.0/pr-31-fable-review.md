# Fable review of PR #31 — Claim-indexed success surfaces and closure evidence

## Provenance statement

This review was produced end to end by **Claude Fable 5** (model id
`claude-fable-5`) on 2026-07-17 (session 11/16). The harness reported Fable 5
at session start and no substitution was observed. Every conclusion below
was re-derived from live GitHub state, exact Git objects, current source,
and executed probes against the production scorer.

## Identity proof (exact objects)

| Object | SHA |
|---|---|
| PR #31 head (`feat/i14-closure-surface`) | `5dbe36274beba56472e6a207c07824fab349a809` |
| Merge commit on `main` | `49c14b600992781e9d505e17e3cc3d297d2202e7` |
| Merge base (parent 1) | `b48c3c0e0c64d219670ddf881462e9faa70b677b` |
| `origin/main` at review time | `82297b0683e6b1379bfeee7568c965c143a358d4` |

- `git diff --exit-code 5dbe362 49c14b6^2` — empty; merged tree
  byte-identical to reviewed head; `git diff --check` clean. Single
  commit; 12 files, +160/−0 (PROTOCOL clause, payload scorer, five
  fixtures, test, registries, CHANGELOG). Zero post-merge drift on the
  scorer, test, or fixtures.

## Issue #14 and closure review

- Issue #14 (milestone v0.3.2.0), zero comments, closed
  2026-07-17T14:48:17Z by merge linkage; `updatedAt == closedAt`. No
  close-comment overclaim.
- CI at merge ran the new test.
- Acceptance adjudication (executed): repo-green-but-deployed-broken →
  the source claim passes and the deployed claim fails as layer
  promotion; uninspectable surface → truthful `unverified` + residual
  reference passes; source-only work → single row, zero added steps;
  `verified` with no evidence-surface fails. The PROTOCOL clause carries
  the full contract including the unauthorized-inspection prohibition
  (“NEVER trigger an unauthorized network or deployment check”) and the
  honest framing (closure gate, not defect prevention) — both
  test-asserted.

## Invariant adjudication (packet checks 1–6)

1. **Claim-ID, surface, evidence, status per row** — enforced; unknown
   surface and invalid status fail-closed (executed). But duplicate
   Claim-IDs were not detected (Finding 1). CONFIRMED WITH FIX.
2. **No automatic promotion of lower-layer evidence** — the nine-surface
   total order is real; generated-artifact evidence for a user-visible
   claim fails; equal-surface passes; higher-layer evidence for a lower
   claim is allowed by design (a stronger surface establishes a weaker
   claim). CONFIRMED by execution.
3. **Verification status distinct from residual disposition** —
   `status: deferred` (a disposition token) is rejected as an invalid
   status; residuals are referenced via `residual:` per #6. CONFIRMED.
4. **Mixed tables evaluate rows independently** — a valid first row never
   rescues an invalid second (executed); fail-fast reports the first
   offending claim by ID. CONFIRMED.
5. **Exact-key parsing** — `field()` splits on pipes and matches the
   whole key, so `surface` never matches `evidence-surface` (executed:
   a row with only `evidence-surface:` fails for a missing surface).
   CONFIRMED.
6. **Uninspectable surfaces route truthfully** — `verified` without
   evidence-surface fails with the exact uninspectable-must-be-unverified
   message; the unverified+residual fixture passes. CONFIRMED.

## What was executed (evidence)

- `bash tests/closure-surface-contract.test.sh` — green at `main`
  (contract + 2 fail + 3 pass fixtures).
- Probe battery against the production scorer:
  - Generated-artifact evidence for a user-visible claim → fail.
  - Row with `evidence-surface:` but no `surface:` → fail (exact keys).
  - `status: deferred` → fail (enum separation).
  - **Duplicate Claim-ID with conflicting surfaces → ACCEPTED**
    (defect; fixed).
  - Prose-only tokens, no canonical rows → fail (“no closure claim
    rows”).
  - **Capitalized `Claim:` row carrying a layer promotion → silently
    skipped; file PASSED with the bad claim invisible** (defect; fixed).
  - Higher-layer evidence for a lower claim → pass (by design).
  - Mixed valid+invalid table → fail.
- Post-fix: extended test RED against the unfixed scorer (first failure:
  duplicate Claim-ID accepted), GREEN after; all 53 repo suites green;
  `verify-package.sh` ok; `git diff --check` clean.

## Findings by severity

**Finding 1 — MEDIUM (duplicate Claim-ID undetected; fixed).**
Two rows sharing one Claim-ID with conflicting surfaces — each valid in
isolation — passed, making the claim’s identity ambiguous (which surface
does “X” require?). The packet’s duplicate-ID robustness case. Fixed:
Claim-IDs are unique per table, failure names the ID.

**Finding 2 — MEDIUM (near-miss rows silently skipped; fixed).**
Row detection was exact-case (`claim:*`): a `Claim:`-capitalized row was
not scored at all — demonstrated with a capitalized layer-promotion row
(deployed-service “verified” by source evidence) that passed invisibly.
Casing a key must never hide a claim from every rule. Fixed: any line
whose key is case-insensitively `claim:` but not exactly lowercase fails
as malformed; nothing near-canonical is silently skipped.

**Finding 3 — INFO.** All remaining behaviors reproduce exactly as the
PR body claims, including the two prohibitions the test asserts
(unauthorized-inspection; honest closure-gate framing). The scorer’s
surface order matches the issue’s nine surfaces byte-for-byte.

## Corrections made (this branch)

Product payload bytes changed: **yes**
(`skills/implementaudit/scripts/check-closure-surface.sh`), plus its
test:

1. Duplicate Claim-IDs fail, naming the ID.
2. Near-miss (wrong-case key) claim rows fail as malformed instead of
   being silently skipped.
3. `tests/closure-surface-contract.test.sh` — three adversarial
   regressions (duplicate ID; capitalized hidden layer-promotion row;
   two-distinct-claims control). RED pre-fix, GREEN post-fix.

## Residual risks and nonclaims

- Claim IDs are free-text tokens; uniqueness is enforced per table, not
  across tables or runs (cross-run claim identity is #15/#4 territory).
- Evidence IDs are recorded fields; the scorer does not resolve them to
  artifacts (that composition lives with #4 anchors and the final-audit
  prose).
- The scorer checks the table, not the world: whether deployed-service
  evidence really came from the deployed service is the run’s PROTOCOL
  duty and #9-measured.

## Verdict

**CONFIRMED_WITH_FIXES.**

The claim-indexed surface model is faithfully implemented — total
surface order, no lower-layer promotion, status/disposition separation,
exact-key parsing, truthful uninspectable routing, per-row independence
— and every acceptance behavior reproduces under execution. Two scorer
defects (ambiguous duplicate Claim-IDs; silently skipped near-miss rows
that could hide a layer promotion) are fixed minimally and
regression-locked.

Integrator notes: changes shipped payload bytes
(`check-closure-surface.sh`) — release-asset hash changes at
integration; re-run verify-package. No post-merge drift existed on this
file; no overlap with other review branches except the distinct report
under `docs/reviews/v0.3.2.0/`.

Live-inventory note (2026-07-17, this session): issues #47–#53 (owner-
authored `IA-*` native-audit-action remediation program, created
21:44–21:45Z) appeared during the review program. They are issues, not
PRs, and not part of the mixed-provenance work under review — recorded
here per the common protocol’s inventory rule; no scope expansion.
