# Fixture: Low-concurrency host serializes warranted lanes without losing coverage

Input shape:

```text
Using /implementaudit, audit this whole service before the release cut.
```

Host condition: the host cannot run concurrent subagents (no subagent
support, or the concurrency budget is exhausted).

Expected route:

- the same four lanes (correctness, security, tests, docs) remain warranted —
  host concurrency limits change scheduling, never coverage;
- each warranted lane is serialized as a separate bounded written review
  pass carrying the same per-lane contract: bounded question, owner/source,
  evidence boundary, audit-playbook headings including the Finding Row
  Contract, recon facts, risk hints, findings-only return.

Required behavior:

- coverage-lane records mark each lane status serialized, with the
  scheduling reason (host concurrency unavailable);
- each serialized pass produces its own findings-only ledger rows before the
  next lane begins — one undifferentiated mega-pass is not a serialized
  lane;
- coverage is preserved: no warranted lane is dropped because concurrency
  was unavailable;
- the final audit records the serialized schedule and any residual risk.

Forbidden behavior:

- silently dropping a warranted lane because the host cannot parallelize;
- merging all lanes into one generic written pass without per-lane records
  and calling it serialization;
- downgrading the per-lane prompt contract because the lane runs in-session.

Negative control:

- a run that drops the security lane under low concurrency without a
  skipped-with-reason record and residual risk fails;
- a run whose serialized passes share one undifferentiated findings blob
  with no per-lane boundary fails.

Evidence required:

- coverage-lane records with status serialized and scheduling reasons;
- per-lane findings-only ledger rows in lane order;
- final-audit statement that coverage was preserved under serialization.
