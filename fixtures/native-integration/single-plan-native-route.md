# Exact single-plan native route

Input:

```text
/implementaudit plan the package-shape checker repair
```

Native route:

- tdqyq-audit-object: one plan-synthesis audit object for a user-specified
  implementation target.
- ydqyq-audit-action: recon, classify ambiguity, produce exactly one phase/plan
  artifact, then review it against evidence boundaries.
- Owner/source: the checker and its tests, not a broad repo survey.
- Smoke A/B: baseline checker result before plan mutation; planned Smoke B
  command after execution.
- Andon: unresolved owner/source, stale baseline, unsafe package-boundary
  ambiguity, or missing rollback becomes OWNER DECISION or audited handoff.
- Final audit: confirms one self-contained plan exists and no extra plan lane
  was created.

Required behavior:

- user already knows the desired plan;
- skips broad category survey;
- recon investigates only enough to specify the plan safely;
- ambiguity is resolved from repo files first;
- remaining ambiguity becomes owner questions or assumptions;
- exactly one self-contained native IMPLEMENTAUDIT phase/plan artifact is
  produced;
- includes owner/source, drift check, scope/non-scope, STOP conditions,
  expected outputs, verification commands, rollback/removal path, and evidence
  boundary;
- does not use root plans/ as canonical;
- does not use external-lane phrasing.

Finding row contract:

- Finding title: Single requested plan needs bounded IMPLEMENTAUDIT phase spec
- Category: plan synthesis
- Evidence: source files inspected and ambiguity list
- Impact: prevents broad survey drift
- Effort: small
- Risk: stale baseline or over-scoped plan
- Confidence: HIGH when owner/source is found in repo files
- Fix sketch / implementation route: direct governance plan synthesis
- Owner/source: checker and test files named by recon
- Acceptance criteria: exactly one self-contained phase/plan artifact
- Verification: validate phase/run-root or direct plan checklist
- Rollback / Plan Closure: remove generated plan if owner rejects it
- Rejected/deferred rationale: broad category survey deferred as out of scope
- Remaining risk: plan execution still needs Smoke A/B
- Route: plan lifecycle

Forbidden behavior:

- broad category survey when the plan target is already known;
- root `plans/` as canonical;
- multiple competing plan artifacts;
- command-lane or external-source phrasing.

Negative control:

- a generic implementation roadmap, multiple root `plans/` files, or a
  detached advice note without drift/STOP/rollback/verification fails.

False parity to reject:

- a plan that is merely self-contained prose without audit-object lifecycle,
  owner/source, drift check, STOP conditions, verification commands, rollback,
  final audit, and Plan Closure.

Evidence required:

- one native IMPLEMENTAUDIT phase/plan artifact;
- source-owner readback;
- drift check;
- STOP conditions;
- expected outputs;
- verification commands;
- rollback/removal path;
- evidence boundary.
