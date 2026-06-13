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

## Current contract essentials (v0.3.0.0 line)

- Four invocation shapes: embedded governance, direct governance, goal
  synthesis, and governed casual-build intake (natural-language intent is
  synthesized into a bounded audit object before any mutation).
- Failure handling is Andon escalation, not retry counting:
  `ANDON_PROBE` → `ANDON_ESCALATE` → `ANDON_HANDOFF`, driven by same-class
  recurrence with new evidence; handoff fires only on a genuine blocking
  condition. There is no try or round cap anywhere.
- Sidecars are two-tier: Graphify/ActiveGraph are optional for every consumer
  repo, canonical for maintenance rounds on this repo (see `AGENTS.md`).
- Native route integration is behavioral, not command identity: repo-audit and
  planning requests use the default category matrix, deep/security pressure,
  DMADV-routed direction analysis, self-contained run-root plans, branch/diff
  scoping, review-plan checks, execute/review dispatch semantics, and
  reconciliation under the audit object.
- Issue publication remains deferred; do not create tracker issues without a
  future explicit publication gate.
- Deeper onboarding: the docs portal source (`docs/portal/site.json` plus
  `docs/portal/pages/**`, built for GitHub Pages; current public deployment
  requires successful deploy evidence and any owner gate) and, for the agent-eval pack,
  `fixtures/agent-eval/RUNBOOK.md`.

## Worked flow

```text
Finding:
- README describes behavior that no longer matches `skills/SKILL.md`.

Owner/source:
- `skills/SKILL.md` defines behavior.
- README.md is derived public documentation.

Smoke A:
- Read `skills/SKILL.md` and README.md.
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
