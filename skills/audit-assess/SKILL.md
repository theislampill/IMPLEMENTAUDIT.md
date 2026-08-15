---
name: audit-assess
description: Internal independent/adversarial assessment routed by the /implementaudit governor for an immutable digest-bound packet; returns findings without readiness or closure authority.
metadata:
  version: "0.4.0"
---

# audit-assess

Internal package-relative cognition only. It is not a public/default entrypoint.

```text
ROUTING_OWNER=/implementaudit
GOVERNOR_ROUTE_ENVELOPE=REQUIRED
TRIGGER=IMMUTABLE_PACKET_AND_GOVERNOR_PROVED_INDEPENDENCE
PACKET_DIGEST=REQUIRED
PROSE_ONLY_REVIEW=REJECTED
DIRECT_ENTRY=REFUSE_OR_RETURN_TO_GOVERNOR
CHILD_ROUTING=FORBIDDEN
RETURN_TO_GOVERNOR=REQUIRED
AUTHORITY_OWNERSHIP=NONE
CURRENTNESS_OWNERSHIP=NONE
LIFECYCLE_OWNERSHIP=NONE
STATE_MUTATION_OWNERSHIP=NONE
RELEASE_OWNERSHIP=NONE
CLOSURE_OWNERSHIP=NONE
CAN_ESTABLISH_AUDIT_COMPLETE=NO
```

Accept a route only when the governor envelope identifies this child, proves
the complete executing package and unambiguous precedence, binds the audit
object and authority ceiling, and supplies the immutable packet digest,
requested claims, evidence/read boundary, disposition vocabulary, and a proved
fresh-context independence contract. A prose summary or self-review context is
insufficient; refuse and return to `/implementaudit`.

Within the packet only, adversarially test each claim for missing semantic
owners, omitted counterexamples, correlated evidence, unsupported identity or
currentness, authority leakage, and false closure. Reconcile contrary evidence
without repairing the work or broadening the packet. Return claim-level
findings and a bounded `PASS / NEEDS_REVISION / NONVERDICT` disposition with
the exact evidence gaps and next governor-owned decision.

The shared review owner is
`../implementaudit/references/plan-lifecycle.md`, with category heuristics in
`../implementaudit/references/audit-playbook.md`. Do not edit, repair, establish
readiness or acceptance, authorize effects, transition lifecycle, or close the
audit. Return to the governor, which independently validates and reconciles the
result.
