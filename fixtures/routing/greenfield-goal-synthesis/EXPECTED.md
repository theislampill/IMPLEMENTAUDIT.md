# Expected Greenfield Goal Synthesis

Classification: mixed, with an inner greenfield artifact.

Brownfield inspection before creation:

- existing owner/source: `scripts/verify-package.sh`, existing claim checks, and
  README/reference docs
- contracts/invariants: no unverified install, release, publication, license,
  marketplace, or provenance claims
- tests/smokes/checkers: package verifier and any focused checker tests
- generated artifacts: README Mermaid blocks are generated from
  `docs/diagrams/*.mmd`
- regression surface: package validation, host-claim scanning, release asset
  validation, README/reference wording
- rollback path: remove the new checker and verifier wiring if it is wrong

Greenfield intake:

- owner/source of truth: new checker plus package verifier wiring
- scope: detect unsupported host-install claims in public docs and references
- non-scope: prove host install behavior or change marketplace behavior
- constraints/invariants: no false release, publication, license, marketplace,
  install, or provenance claims
- acceptance criteria: valid negative-context statements pass; endorsed
  unsupported claims fail
- rollback/removal path: remove the checker, fixtures, and verifier wiring
- evidence plan: run checker directly, run package verifier, and inspect sample
  fixture behavior
- generated artifact plan: source-owned checker and fixtures; no generated
  artifact is edited directly
- Graphify / ActiveGraph sidecar status: not applicable for the checker;
  optional and noncanonical if present in a future run
- canonical-vs-sidecar statement: Markdown docs, checkers, fixtures, and live
  files remain canonical unless repo policy changes

Decision:

- Do not implement until the intake fields above are recorded.
- If owner/source, rollback, or evidence plan cannot be resolved, block or
  defer instead of silently creating files.
