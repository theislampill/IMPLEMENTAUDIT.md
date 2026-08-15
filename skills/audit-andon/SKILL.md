---
name: audit-andon
description: bounded abnormality-response cognition used by /implementaudit L4 or an explicit cord-pull; returns diagnosis and countermeasure recommendations without control or mutation authority.
metadata:
  version: "0.4.0"
---

# audit-andon

Cross-cutting package cognition with two valid entry envelopes. It is a child of
the `/implementaudit` governor when L4 has established a non-trivial Andon, and
it is also directly invocable when a user or agent explicitly pulls the Andon
cord around an observed abnormality.

```text
ROUTING_OWNER=/implementaudit
GOVERNOR_ROUTE_ENVELOPE=REQUIRED_FOR_GOVERNED_ROUTE
TRIGGER=ESTABLISHED_NONTRIVIAL_ANDON_OR_EXPLICIT_CORD_PULL
GOVERNED_ROUTE=L4_TO_AUDIT_ANDON_TO_L4_OR_GOVERNOR
DIRECT_ENTRY=ALLOWED_BOUNDED_CORD_PULL
DIRECT_RETURN=ACTUAL_CALLER
DETERMINISTIC_ANDON_CHEAP_PATH=BYPASS
CHILD_ROUTING=FORBIDDEN
RETURN_TO_GOVERNOR=REQUIRED_FOR_GOVERNED_ROUTE
AUTHORITY_OWNERSHIP=NONE
CURRENTNESS_OWNERSHIP=NONE
LIFECYCLE_OWNERSHIP=NONE
STATE_MUTATION_OWNERSHIP=NONE
RELEASE_OWNERSHIP=NONE
CLOSURE_OWNERSHIP=NONE
RXX_OWNERSHIP=NONE
CAN_ESTABLISH_AUDIT_COMPLETE=NO
```

For a governed route, accept only an exact governor envelope that proves the
complete executing package and unambiguous precedence, binds the current Andon,
audit object, currentness and authority ceiling, and identifies what bounded
diagnostic judgement can change the response. Cheap mechanical Andons bypass
this skill. Return the result to L4/governor for every authoritative action.

For direct entry, require an actual observed abnormality, the caller and its
authority ceiling, available facts, requested containment/diagnosis scope, and
prohibited effects. Direct invocation requests the same bounded cognition; it
does not create an IMPLEMENTAUDIT run, register canonical L4 state, or acquire
authority that the caller lacks. Return to the actual caller.

Establish facts before causal claims. Perform proportional causal deepening and
5 Whys only while another question can change the decision. Distinguish a local
case defect from a systemic owner, rule, checker or mechanism defect; reason
about recurrence, blast radius, countermeasure scope, verification
proportionality, Hansei learning and durable poka-yoke/Kaizen where evidence
warrants them. Return a bounded abnormality classification, causal account,
local-vs-systemic disposition, countermeasure options, an `escalation recommendation`,
and a follow-up evidence obligation.

Do not detect or register canonical L4 state, stop a process by assertion,
execute a repair, mutate source/state, mint currentness, allocate or file an
RXX, activate convergence, route another child, grant PASS/AUDIT_COMPLETE, or
merge, publish, tag, release or close anything. The caller or L4/governor owns
all consequential action.
