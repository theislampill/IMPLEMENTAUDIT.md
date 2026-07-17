# Fable review of PR #25 — Evidence property and scope declarations

## Provenance statement

This review was produced end to end by **Claude Fable 5** (model id
`claude-fable-5`) on 2026-07-17 (session 05/16). The harness reported Fable 5
at session start and no substitution was observed before or during any
mutation on this branch. The packet flags this PR as the work nearest the
owner-observed model substitution; it was reviewed with byte-level scrutiny
accordingly, and every conclusion below was re-derived from live GitHub
state, exact Git objects, current source, and executed validator probes.

## Identity proof (exact objects)

| Object | SHA |
|---|---|
| PR #25 head (`feat/i3-evidence-property`) | `4771059e60aa44b20ba7306fd4894a49428b0933` |
| Merge commit on `main` | `a2f289ca6ec57fcb892cf144006d90b9c22a0b6c` |
| Merge base (parent 1) | `6edf6b9b812b3863718b9eeadf3e15333f1aed95` |
| `origin/main` at review time | `82297b0683e6b1379bfeee7568c965c143a358d4` |

- `git diff --exit-code 4771059 a2f289c^2` — empty; merged tree
  byte-identical to reviewed head. Two commits (`a4ca18e` core,
  `4771059` fixture migration); 9 files, +310/−228.
- **`git diff --check` is NOT clean for this merge**: it flags every added
  line of three fixture files as trailing whitespace — the CRLF signature
  (Finding 1).

## Issue #3 and closure review

- Issue #3 (milestone v0.3.2.0), zero comments, closed 2026-07-17T13:55:52Z
  by merge linkage; `updatedAt == closedAt`. No close-comment overclaim.
- CI at merge ran the extended `tests/phase-validation.test.sh` (26/26).
- Acceptance adjudication (executed):
  - Validator fails a spec whose mandatory command lacks a property tag
    (mixed case) and passes a tagged one — **verified** (shipped fixtures
    + probes).
  - `property: authorization` fails with “authorization is a separate
    gate, not a property” — **verified by execution**.
  - Fully-untagged legacy spec passes with an explicit WARNING —
    **verified** (shipped fixture).
  - Escalation text updated — **verified**: ANDON_ESCALATE now asks “is
    the check testing the evidence property … the claim actually needs?”
    and marks a green-but-weaker-property validator as itself suspect
    (packet invariant 5 satisfied: representable as a validator-scope
    defect).
  - Template (`phase-goal.txt`) carries the full contract: property class
    definitions, plain-language scope, explicit non-claims where confusion
    is plausible, “final audit may not claim a property class no command
    exercised”, authorization-not-a-property. Budgets preserved.
- Supersession: no later commit touched `validate-phase.sh`,
  `phase-goal.txt`, or the test. The later closure-surface fixtures
  (PR #31) reuse the `property:` vocabulary in a different row format
  outside this validator’s jurisdiction — no semantic conflict.

## Invariant adjudication (packet checks 1–7)

1. **Only structural/behavioral/provenance** — enforced; but see Finding 2
   (prefix aliases evaded the invalid-tag regex). CONFIRMED WITH FIX.
2. **Authorization not reintroduced** — rejected by execution with the
   correct message; template and prose repeat the separation. CONFIRMED.
3. **New-format specs require claim, property, scope, nonclaims** —
   property enforced; **scope was NOT enforced** (a tagged command without
   `scope:` passed silently — Finding 3); nonclaims are
   template/behavioral (“where confusion is plausible” is judgment).
   CONFIRMED WITH FIX for scope; nonclaims recorded as a nonclaim.
4. **Legacy warns, new cannot masquerade** — genuinely legacy specs warn
   and pass (verified). A brand-new fully-untagged spec is
   indistinguishable from legacy to a stateless validator; the
   countermeasure is the loud WARNING plus the PROTOCOL/template
   requirement. Adjudicated as an inherent limitation, correctly
   mitigated — the warning makes masquerade visible, not silent. (The
   worse masquerade — a prefix-aliased tag silently downgrading to
   legacy — was real and is fixed: Finding 2.)
5. **Green-but-wrong-property representable as validator-scope defect** —
   present in ANDON_ESCALATE text and the final-audit rule. CONFIRMED.
6. **No PR #26 plural-occurrence semantics leaked** — the
   whitespace-insensitive fixture delta is 7 insertions/7 deletions,
   all property/scope tags; nothing touches occurrence linkage. CONFIRMED.
7. **No CRLF/encoding churn hiding substance** — **VIOLATED by the
   original PR** (Finding 1); fixed.

## What was executed (evidence)

- `bash tests/phase-validation.test.sh` — 26/26 green at `main`.
- Validator probes (disposable mutated specs against the production
  `validate-phase.sh`):
  - `property: authorization` → FAIL, separate-gate message.
  - `property: structurally` on every item → **PASSED as
    legacy-with-warning** (defect; fixed → now invalid-tag FAIL).
  - Tagged items with `scope:` stripped → **PASSED** (defect; fixed →
    now FAIL naming the missing scope).
  - Byte forensics: `tr -dc '\r' | wc -c` = 62/107/52 (equal to the line
    counts) in the three churned fixtures; the fourth migrated fixture is
    CR-free; `git diff -w` isolates the substantive change to 7 lines.
- Post-fix: extended test RED against the original validator + CRLF
  fixtures (5/32 checks fail: alias accepted, scope accepted, 3 CRLF
  hits), GREEN after (32/32); all 53 repo suites green;
  `verify-package.sh` ok; worktree `git diff --check` clean.

## Findings by severity

**Finding 1 — MEDIUM (hygiene churn hiding substance; fixed).**
The fixture-migration commit rewrote three shipped fixtures
(`fixtures/phase-design/dmadv-greenfield-phase.md`,
`fixtures/phase-validation/valid-full-spec.md`,
`fixtures/run-root-example/phases/phase-1.md`) with CRLF line endings on
every line — 221 churned lines concealing a 7-line substantive change,
and permanent `git diff --check` noise for any future edit of those
files. This is exactly the packet’s check-7 hazard, in the repo whose own
CI validates whitespace. (CI’s `git diff --check` inspects the working
tree, which is clean after commit — so the churn passed CI unseen.)
Fixed by LF normalization (verified content-identical under
`git diff -w`) plus a CRLF guard over the four shipped phase-spec
fixtures.

**Finding 2 — MEDIUM (validator regex defect; fixed).**
`BAD_TAG`’s negative lookahead `(?!structural|behavioral|provenance)\w+`
cannot reject any token that merely *starts with* a valid class word:
`property: structurally` (or `behaviorally`, `provenanced`) matched
neither the valid-tag nor the invalid-tag pattern and silently downgraded
the whole spec to legacy-with-warning-pass — the packet’s “alias that
passes a loose membership grep” case. Fixed by `\b`-anchoring the
lookahead; a prefix alias is now a hard invalid-tag failure.
Regression-locked.

**Finding 3 — LOW-MEDIUM (unenforced half of the invariant; fixed).**
Issue #3’s required invariant reads “declares its evidence property
class … **plus a plain-language scope**”, and every migrated fixture and
template line carries `scope:` — but the validator never required it: a
tagged command with the scope stripped passed silently, reopening the
mis-scoped-validator hazard the issue exists to close (a tag alone says
what *kind* of evidence, not what the check actually tests). Fixed:
property-tagged commands must carry `scope:`; regression-locked. (The
issue’s literal acceptance criteria mentioned only the property tag —
this fix enforces the invariant text, not a new rule.)

**Finding 4 — INFO.** The PR body’s remaining claims verified exactly:
validator semantics, 26/26 suite, template/PROTOCOL text, budget
preservation, dual registration, CI execution at merge. The core
implementation commit (`a4ca18e`) migrated its fixture with correct LF —
only the follow-up migration commit (`4771059`) introduced CRLF, which is
consistent with the owner’s report of a mid-turn model substitution near
this work, though authorship cannot be proven from Git metadata.

## Corrections made (this branch)

Product payload bytes changed: **yes** (`validate-phase.sh` is shipped
payload), plus fixtures/test:

1. Three fixture files normalized CRLF→LF (content-identical;
   line-ending-only).
2. `skills/implementaudit/scripts/validate-phase.sh` — `BAD_TAG`
   lookahead `\b`-anchored; new rule: property-tagged mandatory commands
   must declare `scope:`.
3. `tests/phase-validation.test.sh` — three regressions: prefix-alias tag
   → invalid-tag FAIL; tag-without-scope → FAIL; CRLF guard over the four
   shipped phase-spec fixtures. RED 5/32 against original state, GREEN
   32/32 after.

## Residual risks and nonclaims

- “Explicit non-claims where confusion is plausible” is inherently a
  judgment call; it lives in the template and PROTOCOL as behavioral
  guidance and cannot be mechanically validated. No claim it is enforced.
- A newly written fully-untagged spec still passes as legacy **with a
  loud warning** — a stateless validator cannot date a file; the warning
  plus the template requirement is the designed countermeasure.
- Whether property/scope tags improve live model behavior is unmeasured
  until #9 E2b — the issue’s own evidence limit.
- The CRLF guard covers the four shipped phase-spec fixtures; it is not a
  repo-wide line-ending policy (out of this session’s scope).

## Verdict

**CONFIRMED_WITH_FIXES.**

The property/scope contract is faithfully implemented in template,
validator, PROTOCOL, and migrated fixtures, and its acceptance criteria
reproduce cleanly under execution. Three defects found by execution and
byte forensics — CRLF churn concealing the fixture migration’s substance,
a prefix-alias hole in the invalid-tag regex, and unenforced scope on
tagged commands — are fixed minimally and regression-locked on this
branch.

Integrator notes: changes shipped payload bytes (`validate-phase.sh`) —
release-asset hash changes at integration. The scope-enforcement rule is
stricter than merge-time behavior: any spec written after integration
must carry `scope:` on tagged commands (all shipped specs already do).
No overlap with sessions 01–04 branches except distinct reports under
`docs/reviews/v0.3.2.0/`.
