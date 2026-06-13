# Fixture: Branch / Diff Classification

Input shape:

```text
Using /implementaudit, audit this branch against main.
```

Expected route:

- branch/diff scope inside plan lifecycle or reconciliation
- DMAIC for introduced defects
- scope-creep register for unrelated pre-existing findings

Required behavior:

- identify base ref or owner-supplied baseline;
- detect default branch or zero commits ahead / no material diff and offer a
  standard/full audit or owner decision instead of pretending a branch diff
  exists;
- list changed, staged, unstaged, deleted, and untracked files;
- classify each finding as introduced by the diff, pre-existing, unclear, out
  of scope, or independently fixed;
- inspect direct importers/callers or dependent docs/checkers when a contract
  changes;
- map introduced findings to owner/source and verification.

Forbidden behavior:

- do not treat every repo issue as introduced by the branch;
- do not ignore pre-existing findings;
- do not approve without diff-scope evidence.

Evidence required:

- base ref or fallback reason;
- default-branch / zero-ahead guard result;
- changed-file list;
- classification table;
- direct evidence for introduced and independently fixed rows.
