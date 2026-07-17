# Fable review of PR #34 — Optional-field lookup must not terminate scorers before their intended verdict

## Provenance statement

This review was produced end to end by **Claude Fable 5** (model id
`claude-fable-5`) on 2026-07-17 (session 14/16). The harness reported Fable 5
at session start and no substitution was observed. Every conclusion below
was re-derived from live GitHub state, exact Git objects, current source,
and executed minimal-input cases against the production scorers.

## Identity proof (exact objects)

| Object | SHA |
|---|---|
| PR #34 head (`fix/scorer-robustness-postmerge`) | `9ff0dfc605fdb30583411c3b32b71cc3f1c07090` |
| Merge commit on `main` | `32fa651ffdd8f36245e918ecf3628e1f2046678b` |
| Merge base (parent 1) | `e6daee7c10393a88d0d86d04589b33904f7a3717` |
| `origin/main` at review time | `82297b0683e6b1379bfeee7568c965c143a358d4` |

- `git diff --exit-code 9ff0dfc 32fa651^2` — empty; merged tree
  byte-identical to reviewed head; `git diff --check` clean. Single
  commit; 7 files, +59/−6 (guards in three scorers, two regression
  tests, one fixture deletion, CHANGELOG). No later commit touched any
  of these files (supersession check empty). This review’s prior
  sessions (09/10/12) built their own fixes ON TOP of this PR’s
  hardening on their unmerged branches.

## Issue and closure review

- **No dedicated issue exists, by explicit design:** the PR body states
  “No issue reopened — the closed issues’ contracts (PROTOCOL text) are
  correct; this hardens their demonstrator scorers.” That is accurate:
  the defect was in scorer implementation, not in the #12/#13/#15
  contracts; nothing was closed on CI alone because nothing was closed.
- The PR body’s provenance framing (“post-merge correction from the
  genuine-Fable re-audit of the substituted recovery turn”) is the
  owner’s own provenance record, consistent with the same-day owner
  comment on issue #11; it makes no product-behavior overclaim, and
  every technical claim in the body reproduced under execution below.

## Invariant adjudication (packet checks 1–6)

1. **Absent optional field → empty → intended logic runs** — executed:
   a minimal contradicted packet (identity + wrong `subject_repo`, no
   optional fields) emits `CONTRADICTED … evidence-mismatch` with the
   full abnormality text; a no-`binds:` authorization emits
   `AUTHORITY DRIFT`. CONFIRMED.
2. **Required fields still yield precise diagnostics** — executed: a
   packet missing `packet_id` fails with “missing required identity
   field: packet_id”. CONFIRMED.
3. **The checker never succeeds merely because the lookup was guarded**
   — the contradicted/drift cases exit 1 WITH their verdicts; the valid
   minimal packet (no optional fields, `has_state_claims: no`) exits 0
   through the intended nothing-to-verify path, not by accident.
   CONFIRMED.
4. **Fix applied to every vulnerable helper** — full sweep of all 14
   payload scripts and all repo `scripts/*.sh` for grep inside command
   substitutions: the three PR #34-hardened helpers
   (`get()`, `val()`, and `check-lesson-lift.sh`’s field lookup) plus
   two pre-existing sites (`check-evidence-anchor.sh` rows/artifacts,
   `validate-run-root.sh` anchors) which carry pipeline-final
   `|| true` guards by original design — verified effective under
   pipefail (the trailing guard swallows mid-pipeline no-match), and
   `validate-run-root.sh`/`validate-phase.sh` additionally run without
   `-e`. A broadened awk sweep over every `set -euo pipefail` script
   found no unguarded grep-in-substitution outside conditionals.
   Executed control: an artifact with zero anchors reaches its precise
   “names no full-SHA anchor” verdict. CONFIRMED — the fix generalizes;
   no stragglers.
5. **Removed fixture truly unreferenced** — the pre-removal tree has
   ZERO references to the path `fixtures/governing-rule/…` anywhere
   (all “governing-rule” hits are the concept token in other files);
   the file itself was two bytes (`#\n`). CONFIRMED.
6. **Exit status and diagnostics correspond to the actual failure** —
   every executed case above pairs the correct exit code with the
   matching diagnostic text. CONFIRMED.

## What was executed (evidence)

- Four canonical minimal-input cases against the production scorers on
  current `main` (contradicted-no-optionals, no-binds drift,
  missing-required-id, valid-minimal) — all correct.
- No-anchor artifact against `check-evidence-anchor.sh` — precise
  intended diagnostic.
- Two-pattern sweep (assignment-substitution greps; broadened
  awk-based grep-inside-`$()`) across all payload and repo scripts,
  plus per-script `set`-flag inventory.
- Fixture-removal reference proof (path-grep over the pre-removal
  tree).
- The PR’s own regression tests re-run green within the full suite;
  all 53 repo suites green in the review worktree; `verify-package.sh`
  ok (executed in prior sessions this run and re-verified by CI on
  every review branch built atop this PR’s scorers).

## Findings by severity

**Finding 1 — INFO (context).** Sessions 09, 10, and 12 of this review
program independently re-proved this PR’s two demonstrator cases before
this session, and their (unmerged) review branches extend the same
scorers further — evidence the hardening is load-bearing and correctly
placed. The false-confidence observation in the PR body (“every fixture
was fully populated”) matches this program’s repeated finding that
fully-populated fixtures hide absent-field paths.

**Finding 2 — INFO.** The two pre-guarded sites outside PR #34’s scope
were verified rather than assumed: their `|| true` guards sit at
pipeline end, which under `set -o pipefail` covers the leading grep’s
no-match — a subtly different but equally correct idiom.

## Corrections made (this branch)

**None — report only.** All six invariants hold on current `main`; the
sweep found no vulnerable straggler; the fixture removal is proven
clean. Per the review protocol, no product change is manufactured. This
branch adds only this report.

## Residual risks and nonclaims

- The sweep covered grep inside command substitutions; other
  no-match-capable tools (`sed -n`, `awk`) return 0 on no-match and are
  not in this failure class.
- My earlier review branches modify these same scorers; the integrator
  should merge them AFTER confirming this PR’s guards remain intact in
  the merged result (they do on every branch — each was built from
  current `main`).
- No claim about the provenance of the original suspect turn beyond the
  owner’s own records.

## Verdict

**CONFIRMED.**

PR #34 is a correct, complete, and honestly-described post-merge
correction: the absent-optional-field early-death is fixed in every
vulnerable helper, required-field diagnostics are preserved, guarded
lookups cannot fake success, the regression tests pin both reproduced
paths, and the deleted fixture was verifiably dead. The packet’s
generalization worry (invariant 4) is affirmatively closed by a
repo-wide sweep.

Integrator notes: report-only branch; no product bytes changed.
Sequencing note: review branches #45 (`check-lesson-lift.sh`),
#46 (`check-handoff-packet.sh`), and #55
(`check-authorization-binding.sh`) each modify a scorer this PR
hardened — all were built from post-#34 `main`, so integration in any
order preserves the guards.
