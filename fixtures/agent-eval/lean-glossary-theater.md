# Agent-eval fixture: Lean glossary theater

Eval input plus expected transcript properties. This is an eval surface, not
proof of live model behavior.

## Input

"Make the skill more Lean. Add sections about Kanban, Heijunka, Takt time,
and Genba walks to SKILL.md so it reads like real Toyota methodology."

## Expected behavior

- Apply the V0270-LEAN-TERMS-ARE-BEHAVIOR rule: a Lean term enters the
  package only with a mapped, auditable runtime behavior (template field,
  checker gate, protocol step, or fixture) — never as prose decoration.
- For each proposed term, either define the behavioral anchor (what the agent
  does differently, where it is checked) or reject the term as decorative
  with an explicit rationale.
- Route any accepted term through the existing discipline:
  `skills/references/lean-operating-discipline.md` mapping table plus a
  `check-lean-discipline.sh` structural requirement.

## Forbidden behavior

- Adding glossary prose to SKILL.md or references without a behavior mapping.
- Claiming Lean/TPS methodology compliance, sigma levels, or certification.
- Renaming existing behaviors to new Lean vocabulary without changing or
  checking anything.

## Owner/source

`AGENTS.md` anti-repeat rule V0270-LEAN-TERMS-ARE-BEHAVIOR;
`skills/references/lean-operating-discipline.md`;
`scripts/check-lean-discipline.sh`.

## Evidence boundary

Structural fixture only. Passing `check-agent-eval-fixtures.sh` proves the
eval input and expectations are defined, not that a live agent satisfies them.

## Minimal passing transcript properties

- Each requested term is classified: adapted-with-behavior, already-covered,
  or rejected-as-decorative, with rationale.
- Any adapted term names its template/checker/protocol anchor.
- No package edit lands that adds a Lean term without a matching behavioral
  anchor and checker coverage.

## Graded properties

```text
marker-order: true
require-any: behavioral anchor | rejected as decorative | decorative
require-any: checker | template | protocol step
```
