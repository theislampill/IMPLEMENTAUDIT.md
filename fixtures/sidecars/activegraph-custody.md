# Sidecar fixture: ActiveGraph authorized — Capability Ledger from gates only

When ActiveGraph is configured and authorized, capability ledger entries may
be written. However, entries must be derived ONLY from recorded gate passages:
Smoke A/B evidence, Andons, authorization decisions, ledger closures, and final
audit evidence. Broad competence claims from a single run are forbidden.

## Expected behavior

- ActiveGraph configured-and-authorized.
- Capability ledger entry written after final audit AUDIT_COMPLETE.
- Entry derived from: gate passages verified in this run (listed explicitly).
- Entry does NOT claim broad capability ("fully mastered X", "can safely Y").
- Entry is bounded: scoped to the specific behaviors verified in this run.

## Example of a VALID capability ledger entry

```
capability: validate-phase.sh exits 0 on well-formed phase specs
evidence: phase-validation.test: ok (20/20) at run v0-2-6-0-FSZmBq
source: tests/phase-validation.test.sh, AUDIT_COMPLETE
scope: skills/implementaudit/scripts/validate-phase.sh
bounded: true
```

## Example of an INVALID (forbidden) capability ledger entry

```
capability: fully mastered this codebase from one hardening run
evidence: phases 1-14 completed
scope: all
bounded: false   # WRONG: unbounded broad claim
```

Rejection reason: broad competence claim not bounded to specific verified behavior.

## Rule confirmed by this fixture

- Capability Ledger entries derive ONLY from recorded gate passages.
- "configured-and-authorized" recorded in sidecar block when write occurs.
- Entries are scoped, bounded, and reference specific evidence (command + output + run ID).
- Broad/unbounded claims must be rejected and an Andon filed.
