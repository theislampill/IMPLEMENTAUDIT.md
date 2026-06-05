# Contributing

IMPLEMENTAUDIT is an audit-closure governance skill. It is for turning findings,
handoffs, checklists, reviews, goals, tasks, gaps, and implementation plans into
bounded, verified repository changes.

It is not a release bot, provenance system, package publisher, or generic
autonomous build loop. Commit, push, tag, release, publication, provenance,
tool install, indexing, and custody export are separate explicit gates.

## Minimum method

1. Read `AGENTS.md`.
2. Read the live owner/source files before changing derived docs.
3. Classify findings into `P0`, `P1`, `P2`, `OWNER DECISION`, `DEFERRED`, or
   `OUT OF SCOPE`.
4. Run Smoke A before mutation.
5. Patch owner/source, not nearest symptom.
6. Run Smoke B after mutation and compare to Smoke A.
7. Close every item as `done`, `changed`, `blocked`, `deferred`, or
   `unverified`.
8. Update `AGENTS.md` only for durable repo-specific anti-repeat rules.
9. Use local commits only when explicitly authorized, and never push without
   separate authorization.

Validation scripts are POSIX shell scripts. On Windows, run them from Git Bash
or WSL.

## Worked flow

```text
Finding:
- README describes behavior that no longer matches IMPLEMENTAUDIT.md.

Owner/source:
- IMPLEMENTAUDIT.md defines behavior.
- README.md is derived public documentation.

Smoke A:
- Read IMPLEMENTAUDIT.md and README.md.
- Run git diff --check.

Countermeasure:
- Patch README.md to match the live source of truth.

Smoke B:
- Run git diff --check -- README.md.
- Manually inspect evidence and safety-boundary wording.

Closure:
- Status changed.
- Commit only if authorized; push only if separately authorized.
```
