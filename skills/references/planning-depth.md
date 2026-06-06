# Planning Depth

Use this reference when `/implementaudit` must decide whether to govern a
supplied target or synthesize a better bounded work target first.

## Invocation shapes

### Embedded governance

The user has already supplied a host goal, task, plan, or `/goal` runner target.
ImplementAudit applies its gates inside that run. Do not print a second `/goal`.

Use when the prompt already contains:

- the repo or worktree
- the target artifact or finding set
- the intended outcome
- safety boundaries
- enough verification shape to begin

### Direct governance

The user invokes `/implementaudit` with a concrete audit, handoff, checklist,
review, or bounded implementation plan. Normalize the artifact into a ledger and
execute with Smoke A/B, owner/source patching, and terminal closure.

### Goal synthesis

The user gives an idea, gap, incomplete target, or asks for the next best
implementation prompt. Do enough Gemba and Hoshin Kanri to return a bounded,
evidence-aware Kaizen handoff. If the host should continue under a goal runner,
print one ready-to-paste `/goal Using /implementaudit ...` line.

## Depth rule

Use the smallest planning layer that makes the work safe:

- single finding, clear owner/source: direct ledger row
- multiple dependent findings: phase plan
- unclear objective or missing evidence: synthesize a bounded goal first
- conflicting repo policy: OWNER DECISION

Do not add a planning layer merely because the work is large. Add it when the
extra structure improves evidence, sequencing, rollback, or owner decisions.

## Native planner stage rule

When goal synthesis or phased audit closure is selected, the stage contract in
`skills/SKILL.md` is load-bearing:

```text
Stage 0 - Context/tool/repo-state detection
Stage 1 - Audit-governed intake and routing
Stage 2 - Recon / Gemba
Stage 3 - Deep think / risk and dependency analysis
Stage 4 - Phase decomposition
Stage 5 - Write .IMPLEMENTAUDIT roadmap/state/thinking/protocol/phase specs
Stage 6 - Plan review and self-critique
Stage 6.5 - Pre-flight smoke
Stage 7 - One ready-to-paste /goal handoff when not already embedded
```

The stages are native IMPLEMENTAUDIT behavior. They do not import another
package's identity, artifact paths, or completion markers. The execution spine
still governs the actual work inside each phase.

## Planning artifacts

When phase planning is selected, do not leave the plan only in chat. Create or
update:

- `.IMPLEMENTAUDIT/ROADMAP.md`
- `.IMPLEMENTAUDIT/STATE.md`
- `.IMPLEMENTAUDIT/THINKING.md`
- `.IMPLEMENTAUDIT/PROTOCOL.md`
- `.IMPLEMENTAUDIT/phases/phase-N.md`

`THINKING.md` is reviewable planning evidence: objective, route, owner/source,
risks, dependencies, rollback, evidence strategy, generated-artifact plan,
sidecar boundaries, and owner decisions. It is not private chain-of-thought.
