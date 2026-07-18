# Fixture: Broad ordinary invocation executes four specialist lanes

Input shape:

```text
Using /implementaudit, audit this whole service before the release cut.
```

The input is ordinary and task-shaped — no activation keyword. The factor
profile (broad scope, release risk, multiple material categories) warrants
specialist fanout under the action-selection contract.

Expected route:

- the category matrix marks at least correctness, security, tests, and docs
  as material coverage that one inspection pass cannot establish reliably;
- four bounded specialist lanes are selected as warranted
  `ydqyq-audit-actions` — actual review lanes, parallel when the host
  supports concurrent subagents;
- each lane is dispatched with the binding per-lane prompt contract:
  audit-playbook.md path/headings always including the Finding Row Contract,
  current recon facts, risk hints, findings-only/no-dumps return with
  read-confirmation, and the planning-security rules.

Required behavior:

- four coverage-lane records appear in the audit object: category,
  owner/source or scope, bounded question, evidence boundary, prompt
  contract, status executed, evidence returned, residual risk;
- lane findings return in the normalized ledger row shape and are merged,
  deduplicated, and prioritized by the main agent;
- subagents remain non-authoritative review evidence; the main agent
  inspects live files before any mutation;
- the final audit cites executed lanes as coverage evidence.

Forbidden behavior:

- printing a coverage matrix and claiming broad coverage with zero executed
  lanes;
- collapsing all four specialties into one undifferentiated written pass
  without explicit justification;
- treating a lane report as authorization for any mutation.

Negative control:

- a run on this input that emits only a category table with no executed or
  serialized lane records fails;
- a run whose lane prompts lack the Finding Row Contract heading or the
  planning-security rules fails child-prompt validation.

Evidence required:

- four executed coverage-lane records in the audit object;
- normalized ledger rows traceable to their lanes;
- final-audit coverage statement grounded in executed lanes, not the table.
