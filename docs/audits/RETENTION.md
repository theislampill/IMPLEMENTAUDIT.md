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

## Proof-Level Taxonomy (PL1-PL7)

Capability, parity, and surpass claims carry an explicit proof level and
evidence basis (#53, `IA-PROOF-LEVELS`). The levels, weakest to strongest:

| Level | Name | Evidence basis |
|---|---|---|
| PL1 | prose presence | the capability is described in prose |
| PL2 | authoritative runtime instruction | required by SKILL.md/reference runtime text |
| PL3 | template requirement | required by a shipped template |
| PL4 | structural validation | a checker/test mechanically pins the contract |
| PL5 | fixture/example/transcript demonstration | synthetic fixtures or examples demonstrate accept/reject |
| PL6 | observed live behavior | an owner-approved live run exhibited the behavior |
| PL7 | fresh-executor proof | a fresh, weaker-context executor succeeded from the artifact alone |

Rules:

- Active/current surfaces (README, AGENTS, CHANGELOG, portal, eval docs,
  `INDEX.md`, this file) using verdict-class wording — the proof-level rule
  covers `PROVEN`, `PROVEN_WITH_WEAKNESSES`, `SURPASSED`, and variants (proof-level scope) —
  must carry a same-line proof-level qualification naming the attained
  level(s) and, when below PL6/PL7, stating what the claim is NOT (not
  behaviorally observed, not fresh-executor proven).
  `scripts/check-public-claim-boundaries.sh` enforces this on active
  surfaces.
- `docs/audits/archive/**` is exempt history: archived verdict bodies are
  never rewritten. Qualification happens where a verdict is SURFACED on an
  active/current page, not in the archive.
- The taxonomy composes with the per-command evidence properties in
  `skills/implementaudit/templates/phase-goal.txt`
  (`structural` / `behavioral` / `provenance`): command properties classify
  individual evidence commands; proof levels classify CLAIMS aggregating
  that evidence. PL4 rests on structural-property commands; PL6/PL7 require
  behavioral-property evidence from live runs. Authorization remains a
  separate gate, never an evidence property or proof level.
- Upgrade/downgrade: when behavioral or fresh-executor evidence later
  lands (e.g., owner-approved A-series runs, `eval/README.md`), the claim's
  proof level is upgraded in place; if evidence is invalidated, it is
  downgraded — silently neither. Claims genuinely at PL6/PL7 are not
  artificially downgraded.

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
