# Normalized Child-Agent Findings Ledger

| # | Source report | Finding | Priority | Owner/source | Action | Status | Evidence | Follow-up |
|---|---|---:|---|---|---|---|---|---|
| 1 | Contract auditor | Planner markers missing from packaged references. | P1 | `skills/references/` and `scripts/verify-package.sh` | Add packaged reference coverage and validator checks. | changed | Smoke B package validation | - |
| 2 | Adversarial auditor | `AUDIT_HANDOFF` can appear on success path. | P1 | `skills/templates/PROTOCOL.md`, `IMPLEMENTAUDIT.md`, `AGENTS.md` | Make handoff conditional and mutually exclusive with run completion. | changed | Marker readback and manual inspection | - |
| 3 | Contract auditor | License not selected. | OWNER DECISION | repo root | Do not add license or claim license status. | deferred | README/CHANGELOG caveat | Owner selects license |

## Closure expectations

- Every actionable child-agent finding maps to a ledger row before patching.
- Child-agent reports are review evidence only.
- Final audit prints `AUDIT_COMPLETE` before `IMPLEMENTAUDIT_RUN_COMPLETE`.
- `AUDIT_HANDOFF` is printed only when gaps, blockers, or handoff-required
  caveats remain.
