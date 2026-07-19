# v0.3.2.0 corrected evaluator, 28/28 qualification, and republication roadmap

> **Owner amendment, 2026-07-18:** The previously separate 28/28 successor
> campaign is now part of `v0.3.2.0`. B3-v3 qualifies the evaluation
> foundation only. Do not move the tag, republish, or close the release issues
> or milestone until two unchanged 28/28 matrices and the untouched holdout
> pass.

**Goal:** Transparently republish `v0.3.2.0` only after corrected evidence
architecture, reproducible packaging, stable 28/28 behavior, holdout evidence,
and complete public/install readback are all green.

**Owner/source:** 2026-07-18 correction directive plus later same-day scope
amendment.
**Planned-at baseline:** `e7102711c0c514dc8478c807039c098335bb00cf`.
**Foundation branch/PR:**
`fix/v0.3.2.0-b3-evidence-correction-sol` / PR #73.
**Run root:**
`.IMPLEMENTAUDIT/runs/v0-3-2-0-corrected-republication-sol-5FIN9Y`.
**Provenance:** Sol.

## Fixed boundaries

- The original public release is withdrawn; `v0.3.1.0` remains Latest.
- The old annotated `v0.3.2.0` tag stays at its archived target until the final
  combined release gate passes.
- Issues #9, #10, and #35 and milestone `v0.3.2.0` stay open.
- No `v0.3.3.0` milestone or release is created for this campaign.
- Historical B3, B3-v2, 10/28, and 11/28 evidence is immutable.
- No metered API spend, silent retry, cherry-picking, model substitution, or
  fixture/scorer edit in place.
- L/O model and host identities remain comparable unless the owner explicitly
  changes them.
- Sol-authored work is labeled Sol, never Fable.

## Checkpoint 1 — failed-publication preservation and withdrawal: complete

The old release metadata, tag object/target, downloaded assets, hashes,
closure state, B3-v1 raw-event/verdict/bundle hashes, and contradiction are
archived in the correction report. Release ID `356138470` was withdrawn only
after remote durability; #9/#10/#35 and milestone 1 were reopened. The tag was
not moved.

## Checkpoint 2 — corrected evaluator and reproducible builder: complete

PR #73's foundation separates product properties, host safety, and overall
adjudication; rejects unreconstructible claims; adds negative controls; and
normalizes ZIP ordering, time, modes, creator metadata, compression, paths,
locale, and timezone. Intermediate two-clean-checkout archive bytes match.
Final-commit cross-platform proof remains a release gate.

## Checkpoint 3 — B3-v3 evaluator-foundation qualification: complete

The immutable B3-v2 calibration remains failed phrase-measurement evidence.
B3-v3 was frozen before execution with intent SHA-256 `0e99120d392eb2d5982590c693b9a53c346812f4e89f383d7160fa42f305b6f0`.
The 12-mission interleaved campaign produced:

- 12/12 terminal PASS;
- 72/72 required property cells true;
- 12/12 host-safety PASS;
- zero INVALID, ERROR, or model substitution;
- exact candidate/control and L/O identities;
- exactly one authorized capsule change per mission.

A separate implementation importing none of the evaluator host/scorer/runner
modules rederived the raw host tool order, capsule fields, repository snapshot
deltas, identities, and stored matrix. It matched all rows; result SHA-256 is
`0be6f31af047e10441b19c93295766eba93337f8f0e9208d525f94f66ced8f0a`.
This closes the evaluator-foundation checkpoint, not the release.

## Phase 4 — cold-review and merge PR #73 as foundation only

1. Record the B3-v3 campaign hashes and full matrix in the correction report.
2. Perform a bounded fresh-context cold review of PR #73 without reusing the
   authoring rationale as proof.
3. Run complete eval, adversarial, host, adapter, reporting, package,
   reproducibility, docs, and exact-head CI gates.
4. Resolve every review finding and merge PR #73 only when green.

**Publication boundary:** merging PR #73 does not authorize tag movement,
release publication, or closure.

## Phase 5 — freeze the v0.3.2.0 28-cell design and untouched holdout

Before new product tuning:

1. Preserve the historical contemporaneous control at 10/28 and original WIP
   candidate at 11/28, including all splits, INVALID/ERROR records, and the two
   invariant-level improvements. Never describe the one-cell delta as general
   superiority.
2. Freeze the original 14 fixtures × L/O = 28-cell matrix, fixture and scorer
   hashes, exact host/model identities, attempt retention, no-retry rule,
   comparison/repetition rule, and INVALID/ERROR treatment.
3. Create an untouched holdout or preregistered perturbation suite and keep it
   separate from development fixtures.
4. Define the final gate before tuning: one 28/28 matrix, a second unchanged
   28/28 confirmation, then the unchanged holdout.

**STOP:** any rule, scorer, fixture, or holdout content is selected after
seeing its qualification result. A necessary correction creates a new version
and applies symmetrically; failed evidence is never edited in place.

## Phase 6 — fresh foundation measurement and complete 17-cell causal ledger

Run the corrected evaluator against the current v0.3.2.0 foundation before
product changes. For each of the 17 historical non-PASS candidate cells,
record raw evidence, invariant, observed/expected behavior, primary and
secondary cause classes, falsifying probe, smallest coherent correction,
deterministic RED/GREEN test, targeted model check, shared-rule hypothesis,
and dependencies.

Each cell is an individual Andon occurrence. Where host capacity permits, one
read-only forensic subagent owns one cell and must inspect the raw bundle,
transcript, tool events, repository before/after state, fixture, scorer, and
verdict rather than infer from the aggregate ledger. The subagent returns a
normalized evidence-bound Gemba/5-Whys report and cannot modify the product,
scorer, fixture, campaign, or repository. The main executor reviews and
materializes the durable report.

Historical cells entering the ledger:

| Preliminary group | Cells |
|---|---|
| Continuity/resume and receiving-side state | B1-O; E9-L; E9-O |
| Evidence skepticism, multi-cause reasoning, and residual closure | E2b-L/O; E3-L/O; E4-L/O; E5-L/O |
| Authorization, durable lift, public-claim boundaries, and recurrence | E6-O; E7-L/O; E8-O; E10-O |
| Infrastructure-origin separation | E2a-L |

The corrected fresh measurement may reclassify host-short-circuited cells,
but it never overwrites the historical 17-cell table. Because the forensic
review also found manufactured PASS evidence, append-only corrected
adjudication covers all 56 historical candidate/control bundles, not only the
17 candidate FAILs.

After all 17 reports exist, a separate synthesis pass clusters shared causes,
and a separate adversarial review challenges every cluster, contradiction, and
product-versus-measurement classification. Implementation cannot begin until
those dispositions are reconciled into cluster-level governing Andons.

## Phase 7 — measurement repair, re-adjudication, and causal probes

The adversarial synthesis accepted the shared measurement diagnosis but
rejected premature product attribution. Execute this order before any product
countermeasure:

1. generalize layered verdict persistence and report-claim reconstruction;
2. add fixture preflight for materialized state, authority/artifact coherence,
   oracle/doctrine consistency, and discriminating seeds;
3. repair four distinct scoring mechanisms: semantic classification,
   protocol-record parsing/negation, entity counting, and visible/grounded
   oracle identity;
4. append corrected adjudications for all 56 historical bundles without
   overwriting any original verdict;
5. add activation, governing-rule-use, model-visible authority, host
   enforcement, and external-write observability;
6. run preregistered falsifying diagnostics for E3, E4/E7/E8, and E10;
7. approve a cluster-level product governing Andon only when those probes
   establish product causality.

Only then may implementation subagents work at an approved causal-cluster
boundary, never one per cell. One coherent product countermeasure is expected
to close every related cell; the main executor reviews and integrates it.

Every evaluator, fixture, instrumentation, diagnostic, or proven product
tranche must pass, in order:

1. deterministic RED/GREEN regression tests;
2. adversarial/negative controls;
3. focused L/O model comparison under the frozen boundary;
4. independent cold review;
5. full no-regression qualification before merge.

No fixture names, magic evaluation keywords, test-string special cases,
model-specific transcript hacks, post-output scorer relaxation, or giant
always-loaded instruction expansion are permitted.

Required hierarchy:

`17 cell Andons -> evidence-bound Gemba and 5-Whys reports -> shared
causal-cluster map -> cluster-level governing Andons -> coherent countermeasure
tranches -> full 28/28 -> unchanged 28/28 confirmation -> holdout`.

## Phase 8 — final behavioral qualification

1. Freeze the final candidate commit and verify every development attempt is
   retained.
2. Run the full preregistered 28-cell matrix once. Require 28/28, zero INVALID,
   zero unexplained ERROR, zero substitution, and no release-critical
   regression.
3. Without changing product, fixture, scorer, config, or rules, run a second
   clean confirmation matrix and require 28/28 again.
4. Run the untouched holdout/perturbation suite unchanged.
5. Independently rederive both matrices and the holdout from raw ledgers.

A single 28/28 attempt is not stable qualification. If nondeterminism prevents
two confirmations, report exact unstable cells; do not weaken the definition.

## Phase 9 — final records, package, review, and CI

Update the evaluation/release/install/closure reports, CHANGELOG, README, audit
index, portal, release-body source, checksums, and public “What's New.” Keep
deterministic structural tests, independent implementation review, and observed
model behavior distinct. Correct the count to twelve core contracts
(`#1-#7` plus `#11-#15`) plus context continuity separately.

Run complete deterministic registries, evaluation suites, `verify-package.sh`,
two independent clean-checkout and cross-platform byte-reproducibility proof,
fresh install smoke, cold review, exact-head CI, and clean-scope checks.

## Phase 10 — transparent v0.3.2.0 tag replacement and republication

Only after Phases 4-9 are green:

1. archive/read back the old annotated tag again, delete the old ref, and
   create the disclosed owner-authorized corrected annotation at the final
   CI-green commit;
2. build twice and require byte-identical assets/checksums;
3. publish non-draft, non-prerelease, Latest with the visible correction note
   and old/new tag and asset hashes;
4. download public assets cleanly, verify hashes/metadata, install from the
   public asset, verify installed parity, and run smoke;
5. verify public tag/release/CI/readback, then and only then close #9/#10/#35
   and milestone `v0.3.2.0`.

Only after every public/install/closure readback passes may the terminal marker
`V0.3.2.0_CORRECTED_REPUBLISH_COMPLETE` be printed.

## Current next authorized action

Finish and reconcile the independent adversarial review of the complete
17-cell Andon register and causal-cluster synthesis. Only then approve the
first coherent evaluator/fixture countermeasure tranche. PR #73 still requires
its own cold review and complete foundation gates; a green merge does not
authorize publication.
