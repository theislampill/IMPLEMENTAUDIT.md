# Child-Agent Review Loops

Use this reference when `/implementaudit` needs bounded review evidence from
child agents, subagents, specialists, or simulated written audit passes.

## Instruction precedence

Repo-wide child/subagent rules live in root `AGENTS.md`. Subtree-specific
guidance belongs in the nearest scoped `AGENTS.md`, or `AGENTS.override.md` when
that host/repo convention is available and appropriate.

This file is packaged explanatory reference material. It is not an
instruction-precedence file.

## Non-authority rule

Child agents are review loops, not independent authorization authorities.

They do not authorize:

- edits
- commits
- pushes
- tool installs
- Graphify indexing
- ActiveGraph setup or export
- tags
- releases
- publication
- provenance
- AGENTS.md changes

Their reports are review evidence only. The main `/implementaudit` agent must
inspect live files, normalize findings into the ledger, classify priority, and
run Smoke A/B before claiming closure.

## Recommended pair

| Role | Scope | Output |
|---|---|---|
| Read-only contract auditor | Package claims, layout, manifests, templates, scripts, fixtures, README/CHANGELOG truthfulness, and optional-tool evidence boundaries. | PASS / GAP / OWNER DECISION rows. |
| Adversarial behavioral auditor | False completion paths, marker drift, weak boundaries, stale layout assumptions, authorization drift, and AGENTS_UPDATE_DECISION ambiguity. | exploit / risk / countermeasure / OWNER DECISION rows. |

## Specialist loops

Specialist loops may be useful for:

- Graphify terrain review
- ActiveGraph custody verification
- docs audit
- release/provenance review
- generated-artifact checking
- adversarial or red-team review

Each loop needs a bounded question, owner/source, evidence boundary, and explicit
statement that it does not authorize mutation or closure by itself.

## Ledger normalization

After child-agent reports:

1. Merge duplicate findings.
2. Assign each finding a priority and owner/source.
3. Separate `PASS`, `GAP`, `OWNER DECISION`, and out-of-scope observations.
4. Convert actionable gaps into `/implementaudit` ledger rows.
5. Patch only after the main agent has inspected the live owner/source.
6. Record why any durable lesson did or did not update `AGENTS.md`.
