# Fable review of PR #30 — Receiving-side handoff inspection against live state

## Provenance statement

This review was produced end to end by **Claude Fable 5** (model id
`claude-fable-5`) on 2026-07-17 (session 10/16). The harness reported Fable 5
at session start and no substitution was observed. Every conclusion below
was re-derived from live GitHub state, exact Git objects, current source,
and executed probes against the production checker.

## Identity proof (exact objects)

| Object | SHA |
|---|---|
| PR #30 head (`feat/i15-handoff-inspection`) | `ead5f126802d498f8782b958b0fd12a63ffdcbf9` |
| Merge commit on `main` | `b48c3c0e0c64d219670ddf881462e9faa70b677b` |
| Merge base (parent 1) | `60b26bf1622add6759b514e42db191777ea034a8` |
| `origin/main` at review time | `82297b0683e6b1379bfeee7568c965c143a358d4` |

- `git diff --exit-code ead5f12 b48c3c0^2` — empty; merged tree
  byte-identical to reviewed head; `git diff --check` clean. Single
  commit; 9 files, +220/−0 (PROTOCOL section, payload checker, two
  packet fixtures, test, registries, CHANGELOG).

## Issue #15 and closure review

- Issue #15 (milestone v0.3.2.0), zero comments, closed
  2026-07-17T14:40:10Z by merge linkage; `updatedAt == closedAt`. No
  close-comment overclaim.
- CI at merge ran the new test.
- Acceptance adjudication (executed): contradicted packet → named
  `evidence-mismatch` abnormality, blocking exit, owner acceptance still
  echoed verbatim through the mismatch; matching packet (generated from
  live repo state, exercising the real recompute path) proceeds;
  owner-acceptance carried unmodified; no-claims packet → “nothing
  mechanical to verify”, proceeds. All four acceptance behaviors
  reproduce. The PROTOCOL section carries the full contract: packet
  identity incl. receiver-run-id recording and the non-Git
  file-inventory fallback, the three claim classes with per-class
  reconciliation, and block-only-dependent-execution.
- **Supersession (documented):** PR #34 (`9ff0dfc`) fixed the checker’s
  `get()` early-death under `set -e` for absent optional fields and
  added the minimal-fields regression — a documented post-merge
  correction, verified in place.

## Invariant adjudication (packet checks 1–6)

1. **Identity/version/hash and run identities bound** — the four identity
   fields are required (fail-closed, executed); but the content hash was
   required *present* and never *recomputed* — a decorative field
   (Finding 3). Receiver-run-id recording is the receiver’s PROTOCOL
   duty (prose; the checker sees only the packet). CONFIRMED WITH FIX.
2. **Mechanical claims recomputed from live state** — repo, branch,
   HEAD/tree, and cleanliness are genuinely recomputed (wrong-clean and
   wrong-branch contradictions executed); receiver re-derivation wins.
   But tree comparison used PREFIX matching — a 4-character prefix was
   confirmed as tree identity (Finding 1). CONFIRMED WITH FIX.
3. **Evidence references rebound or unverifiable** — Class 2 composes
   with #4’s `check-evidence-anchor.sh` (session 03) per the PROTOCOL;
   the handoff checker itself carries no evidence-ref keys. Recorded as
   designed composition, not a gap.
4. **Authority preserved verbatim, amendable only by issuer** — the
   checker echoes `owner_acceptance` verbatim and never rewrites
   (executed through a mismatch). DETECTING a rewrite requires the
   content-hash binding — which did not exist (Finding 3); with the fix,
   a tampered Class-3 text breaks a sha256-bound packet. CONFIRMED WITH
   FIX.
5. **Mismatch blocks only dependent execution with a precise record** —
   nonzero exit + named abnormality + per-field claimed/live discrepancy
   note; the “audit NOT restarted” language is explicit. CONFIRMED.
6. **Non-Git fallback carries inventory + hashes** — normative in the
   PROTOCOL packet-identity paragraph; the checker skips git comparisons
   when the subject is not a git repo and fail-closes on unresolvable
   claims. Mechanical inventory verification is not implemented
   (recorded limitation; prose-governed). CONFIRMED at contract level.

## What was executed (evidence)

- `bash tests/handoff-packet-contract.test.sh` — green at `main`
  (contract + 4 acceptance cases + PR #34’s minimal-fields regression).
- Probe battery against the production checker:
  - `claimed_tree` = 7-char and even 4-char prefix of live HEAD →
    **CONFIRMED as identity** (defect; fixed).
  - Duplicate conflicting `claimed_branch:` keys (first matches, second
    contradicts) → **ACCEPTED via silent first-wins** (defect; fixed).
  - Tampered `owner_acceptance` with an opaque content hash →
    undetectable (hash never recomputed; fixed for sha256 hashes,
    honestly labeled for opaque tokens).
  - Identity field present only in prose → fail-closed (correct).
  - CRLF packet, no-final-newline packet, wrong-clean claim → correct
    verdicts.
- Post-fix: extended test RED against the unfixed checker (first
  failure: short-prefix tree confirmed), GREEN after; all 53 repo suites
  green; `verify-package.sh` ok; `git diff --check` clean.

## Findings by severity

**Finding 1 — MEDIUM (prefix-matched tree identity; fixed).**
`claimed_tree` was compared with a shell prefix glob: any prefix of the
live HEAD — down to 4 characters — was “confirmed against live state”.
Under the program’s own evidence-identity law (#4: full commit identity
is authority; short hashes are display-only) a packet could claim an
ambiguous stub and receive a confirmed verdict. Fixed: `claimed_tree`
must be a full 40-hex SHA and exactly equal; anything shorter is a named
contradiction, never confirmation.

**Finding 2 — MEDIUM (silent first-wins on duplicate keys; fixed).**
`get()` takes the first match of each key; a packet carrying a matching
first value and a conflicting second smuggles the contradiction past the
comparison entirely — the packet-robustness case “repeated conflicting
keys”. Fixed: any recognized key appearing more than once is a malformed
packet, named per key.

**Finding 3 — MEDIUM (decorative content hash; fixed).**
`packet_content_hash` was required to exist and never recomputed —
so packet identity was unbound and a rewritten Class-3 authorization was
mechanically undetectable (executed: tampered owner text accepted). The
issue makes the hash part of required identity “before any claim
comparison”. Fixed: a sha256-shaped hash (64 hex) is recomputed over the
packet bytes minus the hash line — a correct hash passes, a
tampered-after-issue packet fails; a non-sha256 token is reported “not
verifiable — identity binding rests on the issuer” instead of being
silently trusted. Legacy fixtures (opaque tokens) keep their behavior,
now with the honest label.

**Finding 4 — INFO (recorded limitations).** Receiver-run-id recording,
Class-2 evidence rebinding (via #4’s anchor checker), and the non-Git
inventory verification are PROTOCOL duties of the receiving run, outside
this single-packet checker’s view. The continuation-critical Class-1 set
in prose (run root, phase, ledger, Andons, residuals, next action) is
mechanized only for the four repo-state keys; the rest is prose-governed
and #9-measured.

**Finding 5 — INFO.** PR #34’s `set -e` hardening verified in place;
PR body claims otherwise reproduce exactly.

## Corrections made (this branch)

Product payload bytes changed: **yes**
(`skills/implementaudit/scripts/check-handoff-packet.sh`), plus its test:

1. Full-40-hex exact-equality tree comparison (prefixes are named
   contradictions).
2. Duplicate recognized keys fail as malformed.
3. sha256 content-hash recomputation (packet minus hash line);
   non-sha256 tokens honestly labeled unverifiable.
4. `tests/handoff-packet-contract.test.sh` — four adversarial
   regressions: prefix-tree rejected; duplicate keys rejected;
   sha256-bound packet passes and its tampered variant fails; opaque
   hash tolerated with the unverifiability said out loud. RED pre-fix,
   GREEN post-fix.

## Residual risks and nonclaims

- The hash convention (sha256 over packet bytes excluding the
  `packet_content_hash:` line) is now defined by the checker; issuers
  using opaque tokens get tolerance plus an explicit unverifiability
  note, not silent trust. The owner may later require sha256 outright.
- Class-2/receiver-id/non-Git-inventory mechanization gaps are
  documented composition/limitation, per the issue’s own scope.
- No claim about live receiver behavior beyond what the checker
  mechanizes — the #9 fixture measures the gate’s behavioral half.

## Verdict

**CONFIRMED_WITH_FIXES.**

The receiving-side inspection contract is faithfully implemented — the
three-class model, verbatim Class-3 carriage through mismatches, live
recomputation with receiver-wins, named-abnormality blocking, negative
controls — and PR #34’s hardening is a documented, verified
supersession. Three checker defects found by execution (prefix-matched
tree identity, silent duplicate-key first-wins, decorative content hash
that left authority rewrites undetectable) are fixed minimally and
regression-locked.

Integrator notes: changes shipped payload bytes
(`check-handoff-packet.sh`) — release-asset hash changes at
integration; re-run verify-package. The file was already touched
post-merge by PR #34; this branch builds on current `main`, no conflict.
No overlap with other review branches except the distinct report under
`docs/reviews/v0.3.2.0/`.
