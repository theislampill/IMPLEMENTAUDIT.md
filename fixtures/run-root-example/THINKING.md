# Thinking — exemplar run root

Top objective: close the greeting-casing finding with bounded evidence.
Route: brownfield (existing file mutation). Owner/source: app.txt.
Top closure risks: none material; single-line change.
Rollback or removal path: git checkout -- app.txt.
Evidence strategy: Smoke A grep baseline; Smoke B grep after patch.
Sidecars: absent in the exemplar; Markdown fallback (see sidecars.md).
