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
| Graphify | absent / present (version) / stale terrain | none / query-only / re-extract | first-contact terrain / not applicable |
| ActiveGraph | absent / present (version) | none / fork-diff / mirror-write | checkpoint assistance / non-authoritative mirror / not applicable |
| Markdown fallback | always available | first-class | yes/no in use |

Authorization boundaries: install, indexing/extraction, store setup, event
writing, and export are each separately authorized. Detection alone
authorizes nothing.

Scope qualification: dogfood-only, as tested on two repos, one Windows host,
Python 3.11.9, graphifyy 0.9.33, ActiveGraph 1.10.0, 2026-08-05. Broadening
requires the recorded unfamiliar-third-party-repo trial.

## Graphify terrain

Applicability: all triggers hold / anti-trigger matched (record which one).
Terrain path: `<authorized-outside-repo>/graph.json` (agent-extracted; never
packaged). In-repo output or ignore-file edits require separate mutation
authorization. Known limitations: data-file consumers, module-level constants,
embedded languages, prose censuses, and Git topology use ordinary tools.

Freshness evidence — execute once per extraction, before any query:

| Field | Value |
|---|---|
| `graph.json` `built_at_commit` | full SHA |
| `git rev-parse HEAD` | full SHA |
| Command | `bash "${IMPLEMENTAUDIT_SKILL_DIR:-skills/implementaudit}"/scripts/validate-run-root.sh --graph-freshness <graph.json> <repo-root>` |
| Exit / decision | `0` and silent = usable orientation / nonzero `stale-sidecar` = unusable; fall back to live files |

Query log — one row per query:

| Terrain-shaped query purpose | Nodes/links at query time | Result summary | Evidence boundary | Live-file follow-up |
|---|---|---|---|---|
|  |  |  | orientation only, not proof |  |

Privacy and spend decision:

| Field | Value |
|---|---|
| Model pass | none (`--code-only --no-cluster`) / proposed |
| Owner-named backend | none / exact owner choice; auto-detection refused; Ollama unauthorized |
| Content boundary | filename heuristic only; innocuously named secrets are not protected |
| Spend boundary | out-of-band bound / unmeasurable backend refused |

## ActiveGraph checkpoint assistance

The run root remains the sole authority for lifecycle facts. ActiveGraph may
assist only through authorized `fork / diff` resume-from-checkpoint. A store or
custody helper output is an optional non-authoritative mirror, never a tracked
path. `replay` does not reconstruct the tested custody use case from custom
event names.

| Field | Value |
|---|---|
| Run-root checkpoint |  |
| Run id |  |
| Operation | fork / diff / optional mirror / none |
| Store or trace, if separately authorized | `<run-root>/custody.db` / `<run-root>/custody-trace.jsonl` / other authorized path |
| Evidence boundary | checkpoint orientation / non-authoritative mirror |

If reconstructed events are mirrored, label them `historical_backfill` with
`source`, `backfilled_at`, `original_event_time`, and `evidence_boundary`.

## Evidence boundaries

- Live files beat terrain; the run root, Smoke A/B, and final audit beat any mirror.
- Record every Graphify/live-file contradiction here and resolve in favor of
  live files.
- Sidecar outputs never enter tracked source, commit messages, or the
  packaged `.skill`.
