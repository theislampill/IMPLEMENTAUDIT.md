# Fixture: Independent cold review confirms an executor-ready phase spec

Input shape:

```text
Using /implementaudit, plan and hand off the config-parser extraction for a
fresh executor.
```

Ordinary task-shaped invocation — no "review" keyword anywhere. The run
produces an executor-facing handoff artifact, so the independent cold-review
gate binds.

Expected route:

- Stage 6 self-critique runs first: the author reviews its own phase spec
  and fixes what it can see;
- Stage 6.2 then dispatches an independent cold review: a separate
  fresh-context child agent receives the artifact and the baseline ref —
  and none of the authoring session's working notes;
- the reviewer reads as cold reader and weak executor, confirms exact
  targets, per-step verification, scope boundaries, and STOP conditions are
  reconstructible from disk alone;
- the reviewer returns findings plus the overall disposition PASS.

Required behavior:

- the disposition is recorded in the audit object before preflight;
- the roadmap projection shows the phase's Review cell as PASS alongside
  order, dependencies, and status;
- only after the recorded disposition does Stage 6.5 preflight run and the
  handoff proceed;
- self-critique and cold review both appear in the record as distinct gates.

Forbidden behavior:

- treating Stage 6 self-critique as satisfying the independent gate;
- dispatching the reviewer with the authoring session's working context;
- proceeding to preflight or handoff before the disposition is recorded.

Negative control:

- a run that reaches preflight with self-critique only fails;
- a run whose reviewer shares the authoring context fails.

Evidence required:

- distinct self-critique and cold-review records in the audit object;
- reviewer independence stated (separate child agent, or bounded serial
  fresh-context pass on hosts without subagents);
- recorded disposition PASS preceding preflight in the transcript order.
