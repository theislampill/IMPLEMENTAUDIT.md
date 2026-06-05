# Child-Agent Hierarchy Fixture

This fixture demonstrates scoped `AGENTS.md` guidance. The root `AGENTS.md`
remains the repo-wide contract. The fixture-local `AGENTS.md` narrows behavior
only for files under this directory.

The report examples in this directory are review evidence only. They do not
authorize edits, commits, pushes, releases, optional tool setup, or provenance.

## Roles

- `read-only-contract-auditor.md` describes a read-only check for package and
  transcript contract drift.
- `adversarial-behavioral-auditor.md` describes a read-only challenge pass for
  false completion, proof overclaiming, and safety-boundary drift.
- `*-report.md` files are sample outputs from those roles.

Instruction precedence still follows the `AGENTS.md` hierarchy. Reference files
do not define canonical instruction filenames.
