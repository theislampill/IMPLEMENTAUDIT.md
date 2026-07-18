# Audit Evidence Index

This is a compact map to repo-local evidence. It is not a release log,
provenance manifest, marketplace claim, or raw transcript dump.

Active audit root:

- `docs/audits/INDEX.md` - this map.
- `docs/audits/RETENTION.md` - retention rules and generated/local artifact
  boundary.

Current maintained proof surface for generic active safeguards:

- `scripts/verify-package.sh` - full source/package validation gate.
- `scripts/check-audit-retention.sh` and `tests/audit-retention.test.sh` -
  lean audit-root and generated/local evidence boundary.
- `scripts/check-skill-bootstrap-budget.sh` and
  `tests/skill-bootstrap-budget.test.sh` - concise runtime bootloader.
- `scripts/check-plan-quality-contract.sh` and
  `tests/plan-quality-contract.test.sh` - read-only plans lane, no-secret
  planning, repo-content-as-data, and prompt-injection handling.
- `scripts/check-installed-payload-self-contained.sh` and
  `tests/installed-payload-self-contained.test.sh` - package boundary and
  installed-payload self-containment.
- `scripts/check-dogfood-bootstrap-contract.sh` and
  `tests/dogfood-bootstrap-contract.test.sh` - baseline-first dogfood transcript
  rules and stale real-home readback rejection.
- `scripts/check-validation-registry.sh` - test registry consistency between
  source validation and CI.
- `scripts/build-source-evidence-pack.sh` and
  `tests/source-evidence-pack.test.sh` - runnable, LF-clean source evidence pack.
- `scripts/check-capability-parity-contract.sh`,
  `tests/read-only-plans-lane.test.sh`, and
  `tests/source-evidence-pack-runnable.test.sh` - generic capability coverage:
  read-only plans and runnable source evidence.

Historical evidence may be retained under `docs/audits/archive/` when present,
but that directory is optional history. Current validation and source evidence
must not require archived ledgers to exist.

## Archived Proof Ledgers (qualified per RETENTION.md proof levels)

Archived verdict bodies are history and are never rewritten; when surfaced
here or on any active page they carry proof-level qualification:

- `archive/v0.3.0.0-improve-parity-proof-audit.md` — verdict
  `PROVEN_WITH_WEAKNESSES` [proof level: PL4 structural validation + PL5
  fixture demonstration; not PL6 behaviorally observed, not PL7
  fresh-executor proven].
- `archive/v0.3.0.0-improve-parity-proof-audit-rerun.md` — verdict `PROVEN` [proof level:
  PL2 runtime instruction + PL4 structural + PL5 fixture/checker/package
  evidence; not PL6 behaviorally observed, not PL7 fresh-executor proven].
- `archive/v0.3.1.0-competitor-surpass-proof-audit.md` — verdict
  `V0_3_1_0_PROVEN_WITH_WEAKNESSES`, a self-described source milestone
  proof ledger [proof level: PL1-PL5 source/structural/fixture; not PL6
  behaviorally observed, not PL7 fresh-executor proven].

## Native Audit-Action Remediation Program (tracker #47)

Program record for the native audit-action remediation: umbrella issue #47
(`IA-ACTION-TRACK`), six child issues implemented by PRs #60-#65 and merged
to `main` in session order (merge head `efc1ea8`):

- #48 `IA-ACTION-DEPTH` (PR #60) — action-selection contract: factor-derived
  depth, recorded selections and omissions, no activation keywords.
- #50 `IA-PHASE-RECONSTRUCTIBILITY` (PR #61) — ordered implementation steps
  with per-step verification, scope boundaries, plan-specific STOPs
  (Rule P4-10).
- #49 `IA-ACTION-FANOUT` (PR #62) — binding specialist lanes with serialized
  fallback and coverage-lane records.
- #51 `IA-ACTION-COLD-REVIEW` (PR #63) — Stage 6.2 independent cold review;
  roadmap execution index stays a derivative projection.
- #52 `IA-EVAL-ACTION-SELECTION` (PR #64) — supplementary A-series
  behavioral campaign [proof level: PL4 structural + PL5 fixture;
  owner-approved live runs pending per the #9 posture].
- #53 `IA-PROOF-LEVELS` (PR #65) — PL1-PL7 taxonomy and active-surface
  claim discipline (see `RETENTION.md`).

Dependency order: #48 precedes #49 and #50; #50 precedes #51; #48/#49/#50/#51
precede #52; #52 precedes #53. Implementation order: #48, #50, #49, #51,
#52, #53.

Architecture conformance (tracker-closure audit at merge `efc1ea8`): no new
command identities, no keyword-activated modes, no parallel planning
subsystem, no canonical root competing with the validated `.IMPLEMENTAUDIT/runs/` run root,
projections derivative-only, archives byte-untouched across the program;
per-child what-must-remain-unchanged conformance: PASS for all six.
Standing gate owners: `check-action-selection-contract.sh`,
`check-fanout-coverage-contract.sh`, `check-cold-review-contract.sh`,
`check-plan-quality-contract.sh`, `validate-phase.sh`,
`check-public-claim-boundaries.sh`.

## Boundary

The index points to current proof owners only. Detailed historical narratives,
old matrices, raw transcripts, release-candidate artifacts, and local diagnostic
outputs are not active source evidence and must not be required by current
package or source-evidence validation.
