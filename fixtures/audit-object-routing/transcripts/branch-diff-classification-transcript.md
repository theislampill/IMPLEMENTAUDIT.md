# Transcript Fixture: Branch / Diff Classification

AUDIT_START

Input:

```text
Using /implementaudit, audit this branch against main.
```

Expected route:

- branch/diff scope
- DMAIC for introduced defects
- scope-creep register for unrelated pre-existing findings

Evidence row:

| Field | Value |
|---|---|
| Base ref | merge-base or owner-supplied baseline |
| Default/zero-ahead guard | default branch or zero commits ahead routes to standard/full audit offer |
| Diff files | changed, staged, unstaged, deleted, untracked |
| Finding classes | introduced by diff / pre-existing / unclear / out of scope / independently fixed |
| Verification | direct owner/source and dependent surface readback |

Forbidden behavior:

- Do not treat every repo finding as branch-introduced.
- Do not approve without diff-scope evidence.
- Do not fake branch scope on default branch or zero commits ahead.

AUDIT_VERIFY

Expected close: classification table maps findings to owner/source,
verification, terminal status, and remaining risk.
