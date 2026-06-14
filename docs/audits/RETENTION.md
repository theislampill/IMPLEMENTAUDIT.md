# Audit Evidence Retention Policy

This directory keeps release and source-milestone evidence without turning the
repo root into a raw transcript dump.

Maintainer instruction history is retained separately at
`docs/maintenance/AGENTS-HISTORY.md` so root `AGENTS.md` can stay a concise
baseline-first bootloader. That history file is not an active audit ledger; it
preserves anti-repeat rationale moved out of the first-read instruction surface.

## Active Root

Keep these files directly under `docs/audits/`:

| File | Classification | Retention reason |
|---|---|---|
| `INDEX.md` | canonical release/proof ledger index | Starting map for current and historical proof. |
| `RETENTION.md` | canonical retention policy | Defines what stays active, what may be archived, and what must not enter tracked source. |

## Archive

Historical ledgers that still carry unique release claims, checksum decisions,
dogfood verdicts, regression rationale, adaptation evidence, or source
milestone proof may live under `docs/audits/archive/`.

`docs/audits/archive/` is optional history, not a required source-evidence or
package-validation input. When historical ledgers are intentionally removed or
summarized, current validation must continue to pass from `INDEX.md`,
`RETENTION.md`, source checkers, tests, and maintained fixtures.

Retain archive entries when they are one of these classes:

- release-critical historical ledger;
- superseded draft retained for false-pass or rerun rationale;
- historical but summarized ledger referenced by `INDEX.md` or `CHANGELOG.md`;
- source inventory or matrix fixture needed to explain a past source milestone;
- dogfood, package-boundary, checksum, owner-decision, or explicit-deferral proof.

`docs/audits/INDEX.md` owns the compact current proof map. Do not duplicate a
full per-file archive inventory here.

## Deletion Rule

Delete an audit file only when all are true:

- `INDEX.md` summarizes the retained claim, decision, and remaining boundary;
- no README, CHANGELOG, AGENTS, docs portal, checker, package evidence, or
  current proof map references the file as active proof;
- the file is not the only source of a release claim, checksum, dogfood
  verdict, regression rationale, adaptation matrix, owner decision, or explicit
  deferral;
- `scripts/check-audit-retention.sh` passes after deletion.

Historical proof may be archived or summarized to reduce active-root bulk.
Restoring archived ledgers solely to satisfy stale tests is not valid evidence;
the tests must instead target the current maintained invariant.

## Generated And Local Evidence Boundary

The following must not be tracked as source evidence:

- `.IMPLEMENTAUDIT/`
- `dist/`
- `graphify-out/`
- `.graphify/`
- `.activegraph/`
- `custody.db`
- raw local transcripts or diagnostics
- RC `.skill` files
- RC source evidence zip files
- `plans/` unless explicitly promoted by a future owner decision

Tracked transcript fixtures are allowed only under `fixtures/` when they are
small, synthetic or redacted, and checker-owned.

Root maintainer instructions must remain under the budget enforced by:

```bash
bash scripts/check-agents-bootstrap-budget.sh
bash tests/agents-bootstrap-budget.test.sh
```

## Validation

Run:

```bash
bash scripts/check-agents-bootstrap-budget.sh
bash tests/agents-bootstrap-budget.test.sh
bash scripts/check-audit-retention.sh
bash tests/audit-retention.test.sh
```

`scripts/verify-package.sh` and CI also run the retention checker.
