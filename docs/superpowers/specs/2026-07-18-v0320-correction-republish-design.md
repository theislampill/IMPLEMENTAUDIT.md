# v0.3.2.0 corrected evaluator and stable 28/28 release design

**Status:** owner-approved design, execution in progress
**Author/provenance:** Sol
**Owner/source:** 2026-07-18 correction directive and later scope amendment
**Baseline:** `main` / `origin/main` at
`e7102711c0c514dc8478c807039c098335bb00cf`; original tag target
`dfa55020cd883e1c9b1b65f7e96921b383b72820`

## Problem and amended target

The first `v0.3.2.0` publication claimed an all-true B3 ceiling that its bound
verdicts did not contain and the tagged scorer did not reproduce. This is an
`evidence-mismatch` and `false-closure`, caused by fixture/authorization
confounding, host-safety short-circuiting, verdict composition, and report
adjudication. The release was withdrawn and its closure surfaces reopened.

The corrected release must now satisfy two layers before same-version
republication:

1. a corrected, independently rederived evaluation and reproducible-build
   foundation; and
2. genuinely stable product behavior: 28/28 once, 28/28 again without changing
   product/instrument/configuration, then the untouched holdout.

B3-v3 is a foundation checkpoint only. PR #73 may merge that foundation but
does not authorize tag movement, publication, or closure. No `v0.3.3.0`
milestone is created for this work.

## Corrected evidence architecture

The verdict keeps three independently inspectable layers:

1. **Product properties:** every declared property is persisted as PASS, FAIL,
   or INCOMPLETE with evidence.
2. **Host safety:** unauthorized mutation, identity/custody INVALID,
   infrastructure ERROR, terminal uncertainty, and substitution are recorded
   separately.
3. **Overall adjudication:** product and host statuses are composed explicitly;
   host failure cannot manufacture or erase product measurements.

Claims are eligible only when reconstructible from the stored verdict and an
independent replay/rederivation matches. Negative controls protect against
property manufacture, property erasure, incomplete-ceiling claims,
unreconstructible reports, and replay mismatch.

## B3 version history and selected contract

- **B3-v1:** immutable failed-publication evidence; authorization and
  host-short-circuit confound the experiment.
- **B3-v2:** immutable calibration; layered verdict succeeds, but phrase-family
  properties false-fail correct behavior.
- **B3-v3:** selected qualification instrument. It keeps the bounded
  decision-before-forbidden-mutation contract and derives properties from exact
  capsule JSON, successful structured read-before-write tool events, and bound
  repository snapshots containing only the required capsule.

Frozen B3-v3 completed 12/12 PASS, 72/72 property cells true, 12/12 host PASS,
and zero INVALID/ERROR/substitution. A separate implementation importing no
evaluator host/scorer/runner code reproduced the entire matrix. This proves the
evaluation path can honestly decide #35; it does not prove the 28-cell product
matrix.

## Behavioral diagnosis hierarchy

The historical 10/28 control and 11/28 candidate results remain immutable.
The two invariant-level improvements remain narrow observations, never a
general-superiority claim.

The 17 historical non-PASS candidate cells are individual Andon occurrences:

`17 cell Andons -> evidence-bound Gemba and 5-Whys reports -> synthesis and
adversarial review -> shared causal-cluster map -> cluster governing Andons ->
coherent countermeasure tranches -> 28/28 -> unchanged confirmation -> holdout`.

One read-only forensic subagent per cell inspects raw bundle, transcript, tool
events, before/after state, fixture, scorer, and verdict. Reports distinguish
product, scorer, fixture, host, and authorization origin and stop 5-Whys where
evidence ends. Cell agents cannot modify anything.

Only after all reports exist may separate synthesis/adversarial passes resolve
contradictions and approve causal clusters. Implementation agents are
authorized per approved cluster, not per cell. One coherent governing
countermeasure should close every related cell.

The adversarial pass found that historical PASS evidence is also contaminated
by scorer-manufactured positives. Corrected adjudication therefore covers all
56 historical candidate/control bundles append-only. It also left E3 and the
E4/E7/E8/E10 authority-boundary product causes unresolved. Activation,
governing-rule use, model-visible authority, host enforcement, and external
write observability must be installed before falsifying probes and before any
product countermeasure is approved.

The corrected causal order is: layered verdicts; fixture/world preflight;
separate semantic-classification, protocol-record, entity-counting, and hidden
oracle repairs; append-only 56-bundle re-adjudication; observability; causal
probes; proven cluster-level product countermeasures; full qualification.

## Product-countermeasure constraints

Countermeasures must strengthen ordinary task-shaped behavior. They may use
concise bootloader decisions, progressive references, executable templates,
mechanical checkers, explicit audit-object state, reconstructible handoffs,
and evidence/authorization boundaries.

They may not use fixture names, magic keywords, test-string branches,
model-specific transcript hacks, post-result scorer relaxation, cherry-picked
runs, silent retries, or giant always-loaded instructions. Each causal tranche
must pass deterministic RED/GREEN tests, adversarial controls, targeted L/O
comparison, independent cold review, and full no-regression qualification
before merge.

## Frozen final qualification

Before tuning, freeze the 28-cell matrix, instrument hashes, exact L/O
identities, attempt-retention and no-retry rules, INVALID/ERROR handling,
comparison/repetition rules, and untouched holdout/perturbation suite.

Stable qualification requires:

1. 28/28 on one fully preregistered matrix;
2. 28/28 on a second clean matrix with unchanged product, fixture, scorer,
   host/model configs, and rules;
3. the untouched holdout/perturbation suite passes;
4. zero INVALID, unexplained ERROR, or model substitution;
5. independent raw-ledger rederivation of both matrices and holdout.

A single lucky 28/28 is insufficient. If nondeterminism prevents confirmation,
report exact unstable cells rather than weaken the definition.

## Release reproducibility and publication transaction

The ZIP builder canonically fixes entry ordering, `/` paths, timestamps from a
fixed epoch, modes, creator/platform fields, compression, locale, and timezone.
Final qualification builds the exact release commit in independent clean
Windows and Linux checkouts and requires byte-identical archives plus identical
entry content/modes/manifest.

Only after behavioral, holdout, deterministic, package, reproducibility,
review, and exact-head CI gates are green may the old tag ref be replaced with
the disclosed owner-authorized corrected annotation. The release body must
explain the withdrawn first publication and publish old/new tag and asset
hashes. Public assets are downloaded cleanly, hash-verified, installed from the
public bytes, parity-checked, and smoked before #9/#10/#35 and the milestone
close.

If any gate fails, the release remains unpublished and the tag stays at its
archived old target. No success marker is printed.

## Provenance

- Fable: original review, implementation, and evaluation through the recorded
  boundary.
- Opus: first-publication finalization.
- Sol: independent defect discovery, evaluator correction, re-evaluation,
  behavioral causal program, and eventual corrected republication.
- Owner: withdrawal, same-version replacement/republication, and amended
  28/28-inside-v0.3.2.0 authority.

No Sol-authored material uses a Fable label or trailer.
