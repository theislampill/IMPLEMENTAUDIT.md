# Fable review of PR #32 — Parameter-bound authorization for consequential actions

## Provenance statement

This review was produced end to end by **Claude Fable 5** (model id
`claude-fable-5`) on 2026-07-17 (session 12/16). The harness reported Fable 5
at session start and no substitution was observed. Every conclusion below
was re-derived from live GitHub state, exact Git objects, current source,
and executed probes against the production checker.

## Identity proof (exact objects)

| Object | SHA |
|---|---|
| PR #32 head (`feat/i12-param-auth`) | `ac1662b5331dd22414e93e1cfaac3f7a2303c5b5` |
| Merge commit on `main` | `2a5e20e23b1ab3d474b240bbdc43698cb23ec026` |
| Merge base (parent 1) | `49c14b600992781e9d505e17e3cc3d297d2202e7` |
| `origin/main` at review time | `82297b0683e6b1379bfeee7568c965c143a358d4` |

- `git diff --exit-code ac1662b 2a5e20e^2` — empty; merged tree
  byte-identical to reviewed head; `git diff --check` clean. Single
  commit; 10 files, +147/−0 (PROTOCOL/Nemawashi rule, payload checker,
  auth + match/drift fixture trio, test, registries, CHANGELOG).

## Issue #12 and closure review

- Issue #12 (milestone v0.3.2.0), zero comments, closed
  2026-07-17T15:02:59Z by merge linkage; `updatedAt == closedAt`. No
  close-comment overclaim.
- CI at merge ran the new test.
- Acceptance adjudication (executed): the drift fixture (unbound
  `escape_hatch` + out-of-range `timeout_s`) classifies AUTHORITY DRIFT
  with the owner-unclear/authority class, the STOP instruction, and a
  nonzero exit; the matching fixture proceeds with zero added ceremony;
  the PROTOCOL text carries the binding rule, drift classification, and
  “defaults are NEVER implicitly adopted” (test-asserted).
- **Supersession (documented):** PR #34 (`9ff0dfc`) hardened `val()`
  against `set -e` early-death on the absent-`binds:` lookup and added
  the no-binds regression — verified in place, satisfying packet
  invariant 5 upstream of this review.

## Invariant adjudication (packet checks 1–6)

1. **Binding of subject/action/parameters/scope/window/nonclaims** — the
   record format binds action + enumerated consequential parameters with
   values/ranges/sets; scope and validity window are record fields per
   the PROTOCOL prose (mechanized for parameters; window is prose).
   CONFIRMED at the issue’s scope.
2. **Missing consequential parameter never silently defaults** — the
   direction “runtime param absent from record” was enforced, but the
   converse was not: an authorization binding `timeout_s` with an
   invocation that never supplies it returned a vacuous “all
   consequential parameters bound and in range” — the governed action
   would run on a source/tool default the owner never saw, precisely the
   behavior the issue’s owner-ruling evidence forbids (Finding 1).
   CONFIRMED WITH FIX.
3. **No ceremony on trivial parameters** — only `param.`-prefixed
   invocation lines are consequential; ordinary metadata lines are free
   (executed); one-line authorizations stay one line. CONFIRMED.
4. **Post-authorization parameter change = drift** — out-of-range and
   exact-value conflicts both drift with claimed-vs-bound detail
   (executed). CONFIRMED.
5. **Absent optional `binds` reaches drift logic** — PR #34’s hardening,
   re-verified by execution (no-binds + consequential param → drift, not
   early death). CONFIRMED (upstream fix).
6. **Class-3 authority text verbatim** — this checker compares
   parameters; verbatim carriage of authority text is #15’s contract
   (session 10) and the PROTOCOL prose. No rewriting surface exists
   here. CONFIRMED by composition.

## What was executed (evidence)

- `bash tests/authorization-binding-contract.test.sh` — green at `main`
  (contract + match/drift + no-binds regression).
- Probe battery against the production checker:
  - **Bound-but-unsupplied parameter → vacuous OK** (defect; fixed).
  - Exact-value conflict → drift (correct).
  - `param.` tokens in comment lines → ignored; metadata lines free
    (correct).
  - **Duplicate `timeout_s:` specs, permissive first → strict spec
    silently shadowed, invocation passed** (defect; fixed). Duplicate
    `binds:` lines drifted only by accident of ordering — ambiguity now
    diagnosed as malformed.
  - **Drifting parameter on a final line without trailing newline →
    silently dropped, invocation passed** (defect; fixed).
  - CRLF drift line → detected (correct).
- Post-fix: extended test RED against the unfixed checker (first
  failure: bound-but-unsupplied did not drift), GREEN after; all 53 repo
  suites green; `verify-package.sh` ok; `git diff --check` clean.

## Findings by severity

**Finding 1 — MEDIUM (vacuous pass on bound-but-unsupplied; fixed).**
The checker verified only the invocation→record direction. A parameter
the authorization declares consequential (`binds: timeout_s`) that the
invocation never states produced a clean “all consequential parameters
bound and in range” — while the governed action would run on whatever
default the tool supplies, unseen by the owner. The issue’s own
longitudinal evidence (“source-code defaults are not implicitly
adoptable for governed parameters”) is precisely this case. Fixed:
every bound parameter must be supplied by the invocation; absence
drifts with “bound-but-unsupplied — runtime value unknown; defaults are
never implicitly adopted”.

**Finding 2 — MEDIUM (duplicate auth keys first-wins; fixed).**
`val()` takes the first match: an authorization carrying
`timeout_s: 1..1000000` before `timeout_s: 1..10` silently enforced the
permissive spec (executed: 500 passed). Ambiguous authority records are
now malformed per key, matching the same rule this program installed
for handoff packets (session 10). Duplicate `binds:` lines likewise.

**Finding 3 — LOW-MEDIUM (unterminated final line dropped; fixed).**
`while read` skips a final line without a newline: a drifting
`param.escape_hatch` as the last unterminated line was invisible
(executed) — the packet’s no-final-newline robustness case, and the
same escape-hatch shape as the issue’s May-2026 incident. Fixed with
the standard `|| [ -n "$line" ]` guard.

**Finding 4 — INFO.** PR #34’s hardening verified; all PR-body claims
reproduce; CRLF/comment/metadata handling correct.

## Corrections made (this branch)

Product payload bytes changed: **yes**
(`skills/implementaudit/scripts/check-authorization-binding.sh`), plus
its test:

1. Bound-but-unsupplied parameters drift (no silent default adoption).
2. Duplicate `binds:`/spec keys in the authorization fail as malformed.
3. Final unterminated invocation lines are evaluated.
4. `tests/authorization-binding-contract.test.sh` — three adversarial
   regressions. RED pre-fix, GREEN post-fix.

## Residual risks and nonclaims

- Validity windows and subject identity are PROTOCOL-prose fields, not
  mechanized here (the issue scoped mechanization to the parameter
  comparison).
- Keys are matched as word tokens; a key containing regex metacharacters
  would misbehave (same class as the original code; keys are tokens by
  format).
- The checker sees declared invocation parameters; a runtime that simply
  lies about its parameters is beyond any record comparison — #9
  territory.

## Verdict

**CONFIRMED_WITH_FIXES.**

The parameter-binding contract is faithfully implemented — enumerated
binds with values/ranges/sets, drift classification with stop-and-ask
semantics, zero ceremony for trivial parameters, and PR #34’s
absent-field hardening — and every acceptance behavior reproduces under
execution. Three checker defects (vacuous pass on bound-but-unsupplied
parameters, first-wins duplicate authority keys, dropped unterminated
final lines) are fixed minimally and regression-locked.

Integrator notes: changes shipped payload bytes
(`check-authorization-binding.sh`) — release-asset hash changes at
integration; re-run verify-package. File already touched post-merge by
PR #34; this branch builds on current `main`, no conflict. No overlap
with other review branches except the distinct report under
`docs/reviews/v0.3.2.0/`.
