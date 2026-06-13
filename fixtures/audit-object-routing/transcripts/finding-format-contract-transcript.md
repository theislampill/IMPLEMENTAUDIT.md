# Transcript Fixture: Finding Format Contract

AUDIT_START

Input:

```text
Using /implementaudit, audit this repo and produce audit-object finding rows.
```

Expected route:

- default runtime pressure
- finding format contract
- audit object finding ledger

Evidence row:

Positive finding row:

| Field | Value |
|---|---|
| Finding title | Tighten package path-integrity wording |
| Category | DX / tooling |
| Evidence | `scripts/verify-package.sh:252` checks shipped-payload path integrity |
| Impact | Prevents installed users from receiving dangling source-repo paths |
| Effort | S |
| Risk | LOW, wording/checker-only change |
| Confidence | HIGH |
| Fix sketch / implementation route | Patch owner/source wording and rerun package verifier |
| Owner/source | `skills/SKILL.md`, `skills/references/*`, `scripts/verify-package.sh` |
| Acceptance criteria | Shipped runtime uses native finding-row wording and package verification passes |
| Verification | `bash scripts/verify-package.sh` |
| Rollback / Plan Closure | Revert wording/checker patch if package verification fails; close as changed only after verifier passes |
| Rejected/deferred rationale | not applicable |
| Remaining risk | Static package proof only until host import is separately tested |
| Route: DMAIC / DMADV / mixed / default runtime pressure / reconcile / dispatch-review / deferred | DMAIC |

Deferred/rejected row:

| Field | Value |
|---|---|
| Finding title | Publish generated issue rows |
| Category | docs / handoff |
| Evidence | `skills/references/plan-lifecycle.md` marks issue publication deferred |
| Impact | Issue tracker remains unchanged until owner authorizes publication |
| Effort | M |
| Risk | MED, public tracker mutation and sensitive-content review |
| Confidence | HIGH |
| Fix sketch / implementation route | Defer to future explicit publication gate |
| Owner/source | issue publication gate, not current runtime |
| Acceptance criteria | Current run produces issue-ready rows only and proves no issue creation happened |
| Verification | grep/checker proves issue creation remains refused |
| Rollback / Plan Closure | No rollback needed because no publication occurs; close as deferred with future gate |
| Rejected/deferred rationale | Deferred because v0.3.0.0 forbids `--issues` publication |
| Remaining risk | Users must manually publish or wait for the future gate |
| Route: DMAIC / DMADV / mixed / default runtime pressure / reconcile / dispatch-review / deferred | deferred |

Forbidden behavior:

- Do not publish GitHub issues.
- Do not omit evidence, owner/source, verification, or remaining risk.

AUDIT_VERIFY

Expected close: one complete positive row and one deferred/rejected row both
carry the required native finding-row fields.
