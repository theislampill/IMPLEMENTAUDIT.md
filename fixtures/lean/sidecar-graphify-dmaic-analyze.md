# Fixture: Graphify present — used in DMAIC Analyze, owner/source confirmed by live files

Route: DMAIC (brownfield — sidecar-present scenario)

## Scenario

Graphify is present and fresh. The DMAIC Analyze step uses Graphify terrain to identify
defect surface, owner/source candidates, and regression risk, then confirms each against
live files before patching.

## Graphify query (orientation only, not proof)

Query type: node degree by file (owner/source ranking)
Graph: graphify-out/graph.json
Result summary: skills/implementaudit/SKILL.md (49 links), skills/implementaudit/templates/PROTOCOL.md (25 links),
                skills/implementaudit/templates/THINKING.md (12 links)
Evidence boundary: orientation only, not proof
Freshness: extracted this session, no-cluster mode
Recorded in: <run-root>/sidecars.md

## Analyze step

Graphify-derived candidates:
1. skills/implementaudit/SKILL.md (49 links) — confirmed as canonical behavior owner by reading file header
   and cross-referencing verify-package.sh require_file check. CONFIRMED.
2. skills/implementaudit/templates/PROTOCOL.md (25 links) — confirmed as phase execution loop owner by
   reading PROTOCOL.md and checking check-planner-stages.sh references. CONFIRMED.
3. skills/implementaudit/templates/THINKING.md (12 links) — confirmed as planning template by reading
   file and AGENTS.md documentation. CONFIRMED.

## Expected runtime behavior

1. Graphify terrain used for candidate identification only.
2. Every candidate confirmed by reading the live file before mutation.
3. `sidecars.md` records: query, purpose, result, freshness, evidence boundary, confirmation.
4. No criterion is closed on Graphify result alone — live-file Gemba required.
5. Smoke A run before mutation; Smoke B run after.

## What must NOT happen

- Do not patch a file because Graphify listed it as high-degree without reading the file.
- Do not claim a dependency path exists without confirming in live source.
- Do not record INFERRED graph relations as confirmed until live-file check passes.
- Do not commit graphify-out/ or graph.json to tracked source.

## PHASE_VERIFY stub

IMPLEMENTAUDIT_PHASE_VERIFY
- [pass] Graphify terrain used: yes — 794 nodes, 724 links, 5 queries
- [pass] Candidates confirmed against live files: yes — all 3 candidates read and cross-referenced
- [pass] sidecars.md updated: yes — query purpose, result, freshness, boundary, follow-up recorded
- [pass] Graphify output treated as orientation only: yes — no criterion closed on Graphify alone
- [pass] Smoke A/B pass: yes
Sidecar: Graphify present-and-fresh (orientation only); ActiveGraph skipped; Markdown fallback yes
Remaining risk: none
