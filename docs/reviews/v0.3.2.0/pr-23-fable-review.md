# Fable review of PR #23 — Evidence identity, version anchors, and substitution refusal

## Provenance statement

This review was produced end to end by **Claude Fable 5** (model id
`claude-fable-5`) on 2026-07-17 (session 03/16). The harness reported Fable 5
at session start and no substitution was observed before or during any
mutation on this branch. The original PR #23 is treated as mixed-provenance
work; every conclusion below was re-derived from live GitHub state, exact Git
objects, current source, and executed adversarial cases against the
production scripts.

## Identity proof (exact objects)

| Object | SHA |
|---|---|
| PR #23 head (`feat/i4-evidence-anchoring`) | `c9e782979a1c584abb8e81bbc0fa6b9515babb31` |
| Merge commit on `main` | `da0ace0978d1b38a74c7100656efe5bc71387b72` |
| Merge base (parent 1) | `dae69015b0c1f065cbea8297588b7f93cc11eafd` |
| `origin/main` at review time | `82297b0683e6b1379bfeee7568c965c143a358d4` |

- `git diff --exit-code c9e7829 da0ace0^2` — empty; merged tree byte-identical
  to reviewed head; `git diff --check` clean. Single commit; 10 files,
  +199/−4 (checker, detect-env, run-root validator, PROTOCOL/STATE
  templates, new test, CI/package/manifest registration, CHANGELOG).

## Issue #4 and closure review

- Issue #4 (milestone v0.3.2.0), zero comments, closed 2026-07-17T13:40:06Z
  by merge linkage — no close-comment overclaim exists.
- CI at merge (`package`, SUCCESS) executed the new test: the PR registered
  `tests/evidence-anchoring.test.sh` in `validate.yml` and both
  verify-package registries.
- Acceptance criteria adjudication (all re-executed):
  1. detect-env fixture pair with/without upstream, incl.
     `remote_freshness=not_checked`, read-only, exit 0 — **verified** (plus
     harder variants below).
  2. Evidence row without full-SHA anchor fails the format check; anchored
     row passes — **verified** (`--row`, and `validate-run-root.sh` on a
     seeded run root).
  3. Verdict artifact bound to tree X offered for tree Y refused —
     **verified**, including a same-12-char-prefix / different-full-SHA
     collision pair.
- Supersession: 9 later commits touched `validate-run-root.sh` (+44),
  `STATE.md` (+31), and `PROTOCOL.md`, but the anchor logic, checker,
  detect-env fields, and test are byte-unchanged since merge; the anchor
  check is intact in the current validator (lines ~99–109). Effective
  current behavior re-verified on `82297b0`.

## Invariant adjudication (packet checks 1–6)

1. **Full identity as authority; short SHAs display-only** — anchors are
   full-40-hex everywhere authority is claimed; `head=<short-sha>` in
   detect-env is Stage-0 display per the issue’s own spec. CONFIRMED WITH
   FIX: `--artifact` mode accepted a malformed 41-hex anchor by silent
   truncation to its first 40 chars (Finding 1).
2. **Rows bind occurrence/version/surface, not just environment** — rows
   bind the capture commit; the generated-runtime *surface-file hash* is
   normative prose (PROTOCOL Step 10), not mechanically checked — recorded
   as a nonclaim, matching the issue’s scope (“prose + template field”).
3. **Wrong-tree report refused even if content correct** — CONFIRMED by
   execution (stale copy from an earlier tree refused; matching tree
   accepted).
4. **Offline divergence never implies remote freshness** — CONFIRMED:
   `remote_freshness=not_checked` printed unconditionally; no fetch;
   read-only verified after execution; `behind_ahead=2/1` exact on a
   two-way-diverged clone; detached HEAD yields `upstream=none` without
   error.
5. **Cohorts bound to exact trees, not filename/ordinal** — the artifact
   binding is by full-SHA `Anchor:` content, not path or ordinal;
   eval-side cohort binding (bundle fixture/product hashes) is PR #17/#21
   territory, reviewed in session 01. CONFIRMED for this PR’s surface.
6. **Legacy rows readable, no invented identity** — unanchored rows pass
   (valid legacy), never gain synthesized anchors; unanchored *artifacts*
   are refused as current-state evidence (asymmetry by design: the
   invariant binds newly recorded verdict artifacts). CONFIRMED.

## What was executed (evidence)

- `bash tests/evidence-anchoring.test.sh` — green at current `main`.
- Adversarial production-script cases (disposable inputs; no test-harness
  shims):
  - R1 same-12-char-prefix, different full commit → REFUSED.
  - R2 correct report copied from an earlier tree → REFUSED for the
    current tree; accepted for its own tree.
  - R3 `Anchor: <tree-sha><extra-hex-char>` (41 hex) → **ACCEPTED via
    truncation** (defect; fixed).
  - R4 valid header anchor + later full-SHA body token → accepted
    (first-anchor-wins; adjudicated intended, see Finding 2).
  - R5 39-hex flagged; full-40 passes; uppercase-hex token invisible to
    the scanner (Finding 3, no fix).
  - R6 detect-env on a both-ways-diverged clone: `behind_ahead=2/1`
    exact, `remote_freshness=not_checked`, work tree untouched.
  - R7 detached HEAD → `upstream=none`, no crash.
- Post-fix: extended test red against the unfixed script
  (“41-hex anchor was accepted via truncation”), green against the fixed
  one; all 53 `tests/*.test.sh` green; `verify-package.sh` ok;
  `git diff --check` clean.

## Findings by severity

**Finding 1 — LOW-MEDIUM (defect in PR #23’s checker; fixed).**
`check-evidence-anchor.sh --artifact` extracted the anchor with
`grep -oE '(Anchor: *|@)[0-9a-f]{40}'`, which matches the first 40 hex
chars of a longer token: `Anchor: <sha><extra-hex>` was accepted as
anchored to `<sha>` — while the identical token in `--row` mode is flagged
as malformed. One checker, one token, contradictory verdicts; a corrupted
anchor could pass as exact identity. Fixed by enforcing the same format
rule in artifact mode: every anchor-shaped token (`@…` or `Anchor: …`)
must be exactly 40 hex before extraction; regression cases added.

**Finding 2 — INFO (adjudicated intended; now pinned by test).**
With multiple valid full-SHA anchors, the FIRST names the attested tree
and later tokens are treated as ordinary commit references (e.g. “fixes
regression from @<sha>”). Failing on any non-matching body token would
false-positive on legitimate references; the header-first convention is
coherent. A regression case now pins this so it stays a decision, not an
accident.

**Finding 3 — INFO (no fix).** Uppercase-hex tokens are invisible to all
anchor scanners (row, artifact, validator). Git renders SHAs lowercase, so
such a token cannot arise from git output; widening the alphabet would
complicate the format rule for a non-git-shaped input. Recorded as a
boundary of the contract.

**Finding 4 — INFO.** Everything claimed in the PR body was reproduced
exactly: detect-env fields, row/artifact refusal semantics, dual-registry
registration, CI execution at merge, CHANGELOG accuracy.

## Corrections made (this branch)

Product payload bytes changed: **yes** (one payload script), plus its test:

1. `skills/implementaudit/scripts/check-evidence-anchor.sh` — `--artifact`
   now rejects any anchor-shaped token that is not exactly 40 hex
   (mirroring `--row`), before extracting the attestation anchor.
2. `tests/evidence-anchoring.test.sh` — three regression cases: 41-hex
   anchor refused (red against unfixed script, green after); short
   `@token` inside an artifact refused; header anchor + full-SHA body
   reference still accepted.

## Residual risks and nonclaims

- The generated-runtime **surface-file hash** half of invariant 2 is
  normative prose only; no mechanical checker exists (matches the issue’s
  declared scope; the retained-file manifest idea was explicitly deferred
  by the issue).
- Row-level anchoring cannot mechanically distinguish a *new* unanchored
  row from a *legacy* one — legacy validity is a documented contract
  decision, so a newly written unanchored row passes silently. Enforcement
  for new rows is behavioral (PROTOCOL Steps 5/10), measured only by the
  deferred #9 evaluation.
- Whether anchoring improves live model behavior is untested until #9 E1 —
  the issue’s own stated evidence limit.
- No claim is made about eval-harness cohort binding beyond session 01’s
  review.

## Verdict

**CONFIRMED_WITH_FIXES.**

The anchoring contract is faithfully implemented and its refusal semantics
held under adversarial execution, including prefix-collision and
stale-copy substitution. One real checker defect (41-hex truncation
acceptance, inconsistent with the row rule) was found by execution, fixed
minimally in the payload script, and regression-locked.

Integrator notes: touches `skills/implementaudit/scripts/check-evidence-anchor.sh`,
`tests/evidence-anchoring.test.sh`, and this report. No overlap with
sessions 01–02 branches except distinct files under `docs/reviews/v0.3.2.0/`.
Payload-hash-sensitive: this changes shipped payload bytes, so the release
asset hash changes when integrated (verify-package re-run required at
integration).
