# Fixture: Graphify present — first-contact terrain orientation before DMAIC

Route: DMAIC (brownfield — sidecar-present scenario)

## Scenario

Graphify is present and fresh on an unfamiliar, majority-code repo. Before
owner/source selection, it answers one terrain-shaped question about the broad
component neighborhood. DMAIC defect surface, dependency paths, and regression
risk are established later with ordinary live-file and checker evidence.

## Graphify query (orientation only, not proof)

Query type: components neighboring the named `skills/implementaudit` area
Graph: <authorized-outside-repo>/graph.json
Result summary: candidate component boundaries only
Evidence boundary: orientation only, not proof
Freshness evidence: `built_at_commit` equals `git rev-parse HEAD`; command exit 0
Recorded in: <run-root>/sidecars.md

## Analyze step

Graphify-derived component candidates are re-established with `git ls-tree`,
`rg`, and direct reads before owner/source selection. No dependency or
reference census is taken from the graph.

## Expected runtime behavior

1. Graphify terrain used for first-contact component orientation only.
2. Every candidate confirmed by deterministic search and live-file read before mutation.
3. `sidecars.md` records: trigger decision, query, result, two SHAs, executed comparison, evidence boundary, confirmation.
4. No criterion is closed on Graphify result alone — live-file Gemba required.
5. Smoke A run before mutation; Smoke B run after.

## What must NOT happen

- Do not patch a file because Graphify listed it as high-degree without reading the file.
- Do not ask Graphify for data-file consumers, constants, embedded languages, prose completeness, or Git topology.
- Do not record INFERRED graph relations as confirmed until live-file check passes.
- Do not commit graphify-out/ or graph.json to tracked source.

## PHASE_VERIFY stub

IMPLEMENTAUDIT_PHASE_VERIFY
- [pass] Graphify terrain used: yes — one terrain-shaped first-contact query
- [pass] Candidates confirmed against live files: yes — deterministic search and direct reads
- [pass] sidecars.md updated: yes — triggers, purpose, result, SHA comparison, boundary, follow-up recorded
- [pass] Graphify output treated as orientation only: yes — no criterion closed on Graphify alone
- [pass] Smoke A/B pass: yes
Sidecar: Graphify present-and-fresh (orientation only); ActiveGraph skipped; Markdown fallback yes
Remaining risk: none
