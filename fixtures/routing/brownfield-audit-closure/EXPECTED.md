# Expected Brownfield Audit Closure

Classification: brownfield.

Inspection before mutation:

- governing files: read `AGENTS.md` first
- existing owner/source: README claim text, CHANGELOG release notes, package
  validator, and host-claim checker
- contracts/invariants: no proof claim without evidence; release, publication,
  install, marketplace, license, and provenance claims need separate evidence
- tests/smokes/checkers: `scripts/verify-package.sh`,
  `scripts/check-host-claims.sh`, JSON validation, and `git diff --check`
- generated artifacts: README Mermaid blocks are generated from
  `docs/diagrams/*.mmd`; edit diagram sources and regenerate if diagram blocks
  change
- Graphify / ActiveGraph sidecars: optional and noncanonical; neither proves
  README correctness
- regression surface: public README claims, changelog wording, package verifier,
  release asset validation, and host-claim scan
- rollback path: revert the wording/checker change or restore the previous
  commit before release

Implementation rule:

- Patch owner/source only after inspection.
- Regenerate derived surfaces if touched.
- Run Smoke A/B before claiming closure.
- Close every finding as `done`, `changed`, `blocked`, `deferred`, or
  `unverified`.
