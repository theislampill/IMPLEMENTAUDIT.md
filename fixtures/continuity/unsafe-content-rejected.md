# Continuity fixture: unsafe content — must be rejected

This fixture documents examples of continuity writeback content that must be
rejected. An agent attempting to write any of these must stop and report an
Andon instead.

## Unsafe: contains secrets / credentials

```yaml
---
type: repo-note
scope: src/
source: run-Xy/phases/phase-1.md
secret: false   # WRONG: the content below IS secret material
---
The prod DB password value is REDACTED_FAKE_SECRET_DO_NOT_USE; record only
credential-type-only-at-file-line in findings.
```

Rejection reason: credential material in memory note. Must NOT write.

## Unsafe: raw diagnostic output

```yaml
---
type: repo-note
scope: scripts/
source: run-Xy/phases/phase-3.md
diagnostic: false   # WRONG: the content below IS a raw diagnostic dump
---
Error trace: RangeError: Maximum call stack size exceeded
    at Object.<anonymous> (/home/user/project/src/parser.ts:42:3)
    at Module._compile (node:internal/modules/cjs/loader:1364:14)
    [... 200 more lines ...]
```

Rejection reason: raw log dump in memory note. Must NOT write.

## Unsafe: broad competence claim

```yaml
---
type: repo-note
scope: all
source: run-Xy/phases/phase-1.md
session: bounded   # WRONG: claim is NOT bounded to one verified behavior
---
I have now fully mastered this codebase and can safely rewrite any module.
```

Rejection reason: unsupported broad competence claim from one run. Must NOT write.

## Unsafe: external memory marker leak

Any note write that would cause `MEMORY_SAVED` or `GOAL_ACHIEVED` markers
(external comparator identity markers) to appear in tracked repo files, AGENTS.md,
README.md, or skills/SKILL.md is rejected.

Rejection reason: external identity contamination. Must NOT write.

---

Rule: before any memory writeback, check each item:
- secret: false (no credentials, API keys, passwords, PII)
- diagnostic: false (no raw error logs, stack traces, debug dumps)
- session: bounded (claim scoped to verified evidence from this run only)
- No external memory marker names in the written content
If any check fails, replace the writeback with: CONTINUITY_DECISION Decision: none, and file an Andon.
