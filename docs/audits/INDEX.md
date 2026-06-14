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

## Boundary

The index points to current proof owners only. Detailed historical narratives,
old matrices, raw transcripts, release-candidate artifacts, and local diagnostic
outputs are not active source evidence and must not be required by current
package or source-evidence validation.
