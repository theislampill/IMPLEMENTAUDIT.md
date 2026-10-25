# Fixture: Narrow bounded repair stays direct with recorded restraint

Input shape:

```text
Using /implementaudit, fix the failing expected-output assertion in
tests/routing.test.sh so it matches the current checker banner.
```

The factor profile is light: single clear owner/source, low uncertainty, low
dependency density, no material evidence gap, authorization boundaries
unchanged, and the executor is the current session.

Expected route:

- direct governance: one ledger row against the bound `tdqyq-audit-object`;
- the action-selection contract still runs, and it selects restraint: deeper
  synthesis and decomposition are considered but omitted.

Required behavior:

- the run stays direct: no phase plan, no goal synthesis, no specialist
  fanout;
- the action-selection record is still written, and it records why deeper
  planning was not warranted (no safety, evidence, sequencing, or executor
  reconstructibility gained);
- omitted actions are named with reasons, not silently skipped;
- Smoke A/B and the final audit still run.

Forbidden behavior:

- over-planning: adding a phase plan or synthesis layer that adds no safety,
  evidence, sequencing, or executor-reconstructibility value;
- skipping the action-selection record because the work is small;
- treating restraint as an excuse to skip Smoke A/B or the final audit.

Negative control:

- a run that produces a multi-phase roadmap for this single bounded repair
  without factor-based justification fails;
- a run with no recorded reason for staying shallow fails.

Evidence required:

- one direct ledger row with owner/source and acceptance evidence;
- action-selection record including omitted actions with reasons;
- explicit statement of why deeper planning was not warranted.
