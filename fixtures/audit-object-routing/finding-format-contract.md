# Fixture: Finding Row Contract

Input shape:

```text
Using /implementaudit, produce audit-object finding rows for this repo.
```

Expected route:

- default runtime pressure
- DMAIC / DMADV / mixed / reconcile / dispatch-review / deferred as appropriate
- findings stored in the audit object

Required behavior:

Each material finding or deferred issue-ready row includes:

- Finding title
- Category
- Evidence
- Impact
- Effort
- Risk
- Confidence
- Fix sketch / implementation route
- Owner/source
- Acceptance criteria
- Verification
- Rollback / Plan Closure
- Rejected/deferred rationale when applicable
- Remaining risk
- Route: DMAIC / DMADV / mixed / default runtime pressure / reconcile / dispatch-review / deferred

Forbidden behavior:

- do not invent evidence to fill the template;
- do not omit owner/source or verification for actionable findings;
- do not treat issue-ready rows as published issues.

Evidence required:

- one complete positive finding row;
- one deferred/rejected row when applicable;
- checker or transcript proof that required fields are present.
