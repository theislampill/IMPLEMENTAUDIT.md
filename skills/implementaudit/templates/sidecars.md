# Sidecars

Runtime copy target: `.IMPLEMENTAUDIT/runs/<task-slug>-<id>/sidecars.md`

Read this file before any Graphify or ActiveGraph use in the run. Both
sidecars are optional: absence is not a failure and blocks nothing. Graphify
output is orientation evidence, not proof. ActiveGraph custody is not
correctness proof. Markdown ledger and final report remain first-class
fallback.

## Status

| Sidecar | Detected | Authorized this run | Mode |
|---|---|---|---|
| Graphify | absent / present (version) / stale terrain | none / query-only / re-extract | — |
| ActiveGraph | absent / present (version) | none / read-prior-only / write | — |
| Markdown fallback | always available | first-class | yes/no in use |

Authorization boundaries: install, indexing/extraction, store setup, event
writing, and export are each separately authorized. Detection alone
authorizes nothing.

## Graphify terrain

Terrain path: `graphify-out/graph.json` (agent-extracted; gitignored; never
packaged). Nodes need `id` + `label` (optional `type`); links need
`source`/`target`. Staleness: any tracked file newer than the terrain.

Query log — one row per query:

| Query purpose | Nodes/links at query time | Result summary | Freshness | Evidence boundary | Live-file follow-up |
|---|---|---|---|---|---|
|  |  |  | fresh / stale | orientation only, not proof |  |

## ActiveGraph custody

Store path: `<run-root>/custody.db` (SQLite) or `<run-root>/custody-trace.jsonl`
(append-only fallback). One store per run root; never a tracked path.

| Field | Value |
|---|---|
| Store |  |
| Run id |  |
| Custody mode | live mode for this run / historical_backfill for reconstructed events |
| Prior stores preloaded (read-only) | `.IMPLEMENTAUDIT/runs/*/custody.db`, `*/custody-trace.jsonl` — list any used |
| Events written |  |

Backfill labeling: reconstructed events must carry
`custody_mode: historical_backfill` plus `source`, `backfilled_at`,
`original_event_time`, and `evidence_boundary`.

## Evidence boundaries

- Live files beat terrain; Smoke A/B and the final audit beat custody.
- Record every Graphify/live-file contradiction here and resolve in favor of
  live files.
- Sidecar outputs never enter tracked source, commit messages, or the
  packaged `.skill`.
