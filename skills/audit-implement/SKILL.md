---
name: audit-implement
description: Internal maintainer-side realised-implementation qualification cognition routed by the /implementaudit governor after verified release currentness; derives an evidence-bounded implement without mutation or release authority.
metadata:
  version: "0.4.0"
---

# audit-implement

Internal maintainer-only package-relative cognition. Here `implement` is a
project-domain deverbal noun: the implementation concretely realised for the
exact candidate and claim. The productive inversion is `IMPLEMENTAUDIT:
implement -> audit`; `audit-implement: audit -> implement`.

```text
ROUTING_OWNER=/implementaudit
GOVERNOR_ROUTE_ENVELOPE=REQUIRED
TRIGGER=MAINTAINER_EXACT_CANDIDATE_AFTER_VERIFIED_RELEASE_CURRENTNESS
RELEASE_CURRENTNESS=VERIFIED_REQUIRED
RELEASE_CURRENTNESS_NOT_APPLICABLE=REJECTED
PACKAGE_GATE_SUBJECT=EXECUTING_IMPLEMENTAUDIT_PACKAGE
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
the complete executing package and unambiguous precedence, proves maintainer
scope and mechanically verified release currentness, and binds exact source,
commit/tree, generated artifact, package, install and applicable host identity
to the claimed next boundary. `NOT_APPLICABLE`, stale, absent, mixed, or
ambiguous identity refuses and returns to `/implementaudit`.

Compare without collapsing source, generated, packaged, installed, hosted,
exact-main, released and public-readback states. Return the bounded
realised implementation supported at each applicable evidence surface:
established, contradicted, insufficient, stale, identity mismatch,
qualification gap, unresolved, or boundary not supportable. Its direction is
`observed evidence -> bounded realised implement`, never intent or diagnosis ->
mutation. State what progression the evidence supports as advice to the
governor, not permission.

The shared qualification and marker owner is
`../implementaudit/references/transcript-contract.md`; package and currentness
checks remain deterministic governor/substrate work. Do not establish formal
qualification, provenance, currentness, global PASS, release or closure; do not
commit, push, merge, tag, publish, release, mutate lifecycle, close a tracker,
or own a DAG JOIN. Return to the governor for the consequential decision.
