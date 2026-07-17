# Fable review of PR #26 — Plural defect profiles linked to one occurrence

## Provenance statement

This review was produced end to end by **Claude Fable 5** (model id
`claude-fable-5`) on 2026-07-17 (session 06/16). The harness reported Fable 5
at session start and no substitution was observed before or during any
mutation on this branch. The original PR #26 is treated as mixed-provenance
work; every conclusion below was re-derived from live GitHub state, exact
Git objects, current source, and executed adversarial run roots against the
production validator.

## Identity proof (exact objects)

| Object | SHA |
|---|---|
| PR #26 head (`feat/i5-occurrence-linkage`) | `f41554eae906b912c89d96bee09d06ae99721f9d` |
| Merge commit on `main` | `1aec235b2cddcac20badedae97261631886bae2c` |
| Merge base (parent 1) | `a2f289ca6ec57fcb892cf144006d90b9c22a0b6c` |
| `origin/main` at review time | `82297b0683e6b1379bfeee7568c965c143a358d4` |

- `git diff --exit-code f41554e 1aec235^2` — empty; merged tree
  byte-identical to reviewed head; `git diff --check` clean. Single
  commit; 6 files, +99/−10 (transcript contract, validator, PROTOCOL,
  STATE template, test, CHANGELOG).

## Issue #5 and closure review

- Issue #5 (milestone v0.3.2.0), zero comments, closed 2026-07-17T13:58:18Z
  by merge linkage; `updatedAt == closedAt` (amendments predate merge).
  No close-comment overclaim.
- CI at merge ran the extended `tests/run-root-validation.test.sh`.
- The owner amendments are honored in the merged bytes: legacy tables are
  accepted and never described as malformed anywhere in the touched code,
  tests, or docs (grep-verified); generation is detected from the header
  (`Occ` column presence); the linkage requirement binds new-format
  tables only. The original issue text “rejects the old malformed table”
  was superseded by the amendment and correctly NOT implemented.
- All three amended acceptance fixtures exist and pass: legacy-accepted,
  linked-plural-accepted, missing-occ-rejected.
- Supersession: one later commit (`f624d02`, PR #27) extended the
  validator with the occurrence-resolution/residual-disposition section —
  layered on top of, and consistent with, this PR’s Occ semantics. The
  PR #26 logic is byte-unchanged; effective current behavior re-verified
  at `82297b0`.

## Invariant adjudication (packet checks 1–6)

1. **One class per row does not imply one class per occurrence** —
   contract text (“one class per row; one or more linked rows per
   occurrence”) in transcript contract, PROTOCOL, and STATE; executed
   plural fixture passes. CONFIRMED — WITH FIX: the “one class per row”
   half was prose-only; a comma-separated multi-class cell passed the
   validator (Finding 1).
2. **Every new-format defect row has an occurrence identity** — enforced
   by the validator’s awk over new-format data rows; two-row
   missing-Occ input rejected with BOTH row numbers named (“row(s) 1 2”).
   CONFIRMED.
3. **Several rows may link to one occurrence without collapsing into
   free text** — the structure is columns + shared short id; the plural
   fixture (two classes, one `o1`) passes; each row keeps its own class,
   countermeasure, rerun evidence, and outcome. CONFIRMED.
4. **Legacy roots valid and resumable; absence of linkage is legacy, not
   malformed** — legacy header accepted with data rows (executed);
   validator error message explicitly says “legacy shape without Occ also
   accepted”; no “malformed” description anywhere. CONFIRMED.
5. **Rows cannot silently link to a foreign run/version’s occurrence** —
   structurally, Occ ids live inside one run root’s STATE.md; no
   cross-file reference mechanism exists, so cross-run linkage is not
   representable. Same-file id reuse across genuinely distinct
   occurrences is semantic and not mechanically detectable (free-text
   ids) — recorded as a nonclaim. CONFIRMED structurally.
6. **Summary/rendering preserves every linked defect** — no rendering
   layer exists; STATE.md is the record, and each linked row carries its
   own Outcome tracked to closure (“each remedy is tracked to closure”).
   CONFIRMED at the substrate level; no claim about external renderers.

## What was executed (evidence)

- `bash tests/run-root-validation.test.sh` — green at `main` (incl. the
  three shipped #5 fixtures and PR #27’s residual cases).
- Adversarial run roots against the production validator (template-built
  scaffolds, disposable):
  - Two rows with no Occ → rejected, both row numbers reported.
  - Linked plural rows (two classes, shared `o1`) → accepted.
  - **Comma-separated classes in one row
    (`failed-criterion, regression`) → ACCEPTED** (defect; fixed).
  - Legacy table with data rows → accepted (never malformed).
  - Same Occ id on semantically unrelated rows → accepted (structural
    validator; recorded limitation).
  - Duplicate identical row (same `#`, same Occ) → accepted (row-id
    uniqueness unchecked; recorded limitation).
- Post-fix: new 5d regression RED against the unfixed validator, GREEN
  after; all 53 repo suites green; `verify-package.sh` ok;
  `git diff --check` clean.

## Findings by severity

**Finding 1 — MEDIUM (one-class-per-row unenforced; fixed).**
The invariant’s load-bearing half — exactly one class per row — existed
only as prose. A new-format row with `failed-criterion, regression` in
the Class cell passed `validate-run-root.sh`, smuggling plural defects
into one row and defeating the very linkage design this PR introduced
(fixing one defect silently leaves the sibling, the class the issue’s
motivating incident named). This is the packet’s comma-separated-bypass
robustness case, confirmed by execution. Fixed minimally: new-format
data rows require a single-token Class cell (`^[A-Za-z-]+$`); plural
defects must link rows via a shared Occ id. Legacy tables untouched.
Regression-locked (5d).

**Finding 2 — INFO (recorded limitations, no fix).** The validator is a
substrate checker: it cannot detect semantic Occ-id reuse across
genuinely distinct occurrences, duplicate row ids, or class-token
membership (the latter is the andon-class-contract test’s jurisdiction
at the source level; run-root STATE.md files are user artifacts).
Enforcing id-uniqueness or class membership would exceed the issue’s
scope (“no new schema files”) and risk rejecting legitimate resumed
roots.

**Finding 3 — INFO.** PR body claims verified exactly: fixture trio,
generation detection from the header, legacy wording ban, per-class
recurrence citation semantics unchanged (ANDON_ESCALATE still cites
prior same-class rows by `#`; STATE text says “per-class citation
semantics unchanged by linkage”).

## Corrections made (this branch)

Product payload bytes changed: **yes**
(`skills/implementaudit/scripts/validate-run-root.sh` is shipped
payload), plus its test:

1. `validate-run-root.sh` — new-format Andon rows with a non-single-token
   Class cell (commas/spaces) are rejected, naming the offending rows;
   error text restates the rule (one class per row; plural defects link
   rows via Occ). Legacy tables unaffected.
2. `tests/run-root-validation.test.sh` — regression 5d: comma-separated
   multi-class row rejected. RED pre-fix, GREEN post-fix.

## Residual risks and nonclaims

- Occ ids are free-text and file-scoped: semantic misuse (one id reused
  for unrelated occurrences; duplicated rows) is behaviorally governed,
  not mechanically checked.
- Class-token *membership* in the official 13 is enforced at the source
  level by `tests/andon-class-contract.test.sh` (session 02), not per
  run root; a new-format row with a single-token but non-official class
  passes this validator.
- No claim about external summarizers/renderers — none exist in the
  product.
- Frequency of plural-defect occurrences beyond the motivating incident
  remains unmeasured (issue’s own evidence limit).

## Verdict

**CONFIRMED_WITH_FIXES.**

The Occ linkage design is faithfully implemented per the amended issue —
legacy compatibility included and correctly worded — and survived all
hard robustness cases by execution. Its prose-only half (one class per
row) was mechanically bypassable by a comma-separated cell and is now
enforced for new-format rows, with a deterministic regression.

Integrator notes: changes shipped payload bytes (`validate-run-root.sh`)
— release-asset hash changes at integration. **Conflict alert:** the
session-03 branch (`review/fable-pr-23`, PR #39) does NOT touch this
file, but both this branch and any later session touching
`validate-run-root.sh` edit the same region family; this branch’s edit
is inside the #5 new-format block and is additive. No other overlap with
sessions 01–05 branches except distinct reports under
`docs/reviews/v0.3.2.0/`.
