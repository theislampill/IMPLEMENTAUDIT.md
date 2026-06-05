# Expected Mixed Routing

Classification: mixed.

Brownfield shell:

- read `AGENTS.md`, package metadata, current skill/reference layout, fixtures,
  validators, generated README diagram sources, and CI workflow
- identify `skills/SKILL.md` as canonical skill source and `IMPLEMENTAUDIT.md`
  as synchronized compatibility root
- identify package verifier, host-claim checker, release asset builder, and
  generated README diagram checker as regression surface

Greenfield intake for new artifacts:

- owner/source of truth: routing reference, routing fixtures, routing checker,
  and package verifier wiring
- scope: classify greenfield, brownfield, and mixed audit-governed work
- non-scope: become a generalized autonomous builder or import external
  markers/artifact paths
- constraints/invariants: owner/source patching, Smoke A/B, no proof without
  evidence, optional Graphify/ActiveGraph boundaries, Markdown fallback
- acceptance criteria: routing reference exists; valid examples pass; invalid
  examples fail; README/reference identity scan passes
- rollback/removal path: remove routing artifacts and verifier wiring before
  release if checks fail
- evidence plan: run routing checker, package verifier, generated diagram check,
  host-claim scan, and release asset validation
- generated artifact plan: edit source docs/checkers; regenerate README only if
  diagram blocks change
- Graphify / ActiveGraph sidecar status: optional and noncanonical
- canonical-vs-sidecar statement: repo files, fixtures, checkers, smoke output,
  and final audit ledger remain canonical
