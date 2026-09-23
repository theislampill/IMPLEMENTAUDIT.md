#!/usr/bin/env python3
"""Finite cross-trifecta counterexamples; these do not test IMPLEMENTAUDIT runtime."""

from __future__ import annotations

import itertools
import json
import sys


def cases() -> list[dict]:
    results = []

    def record(identity, bad, control, observation):
        if not bad or not control:
            raise AssertionError(identity)
        results.append({"id": identity, "counterexample_observed": bad,
                        "positive_control_observed": control, "observation": observation})

    # A product choice, workflow constraint and actor constraint share variables.
    states = list(itertools.product((0, 1), repeat=3))
    rules = [lambda s: s[0] != s[1], lambda s: s[1] != s[2], lambda s: s[2] != s[0]]
    pairwise = [any(all(rules[i](s) for i in pair) for s in states)
                for pair in itertools.combinations(range(3), 2)]
    joint = [s for s in states if all(rule(s) for rule in rules)]
    record("TC01", all(pairwise) and not joint,
           any(rules[0](s) and rules[1](s) and s[2] == s[0] for s in states),
           {"pairwise_satisfiable": pairwise, "joint_solutions": len(joint)})

    # Equal artifact bytes do not imply equal decision meanings or authority.
    evidence = {"bytes": "h", "configuration": "v1", "definition": "w1", "grant": "observe"}
    current = {**evidence, "definition": "w2", "grant": "execute"}
    record("TC02", evidence["bytes"] == current["bytes"] and evidence != current,
           dict(evidence) == evidence,
           {"byte_identity_retained": True, "decision_tuple_retained": False})

    # Distinct route transactions can still attempt the same external delivery.
    attempts = [("route-a", "order-7", "send"), ("route-b", "order-7", "send")]
    routes = {row[0] for row in attempts}
    deliveries = {row[1:] for row in attempts}
    record("TC03", len(routes) == 2 and len(deliveries) == 1,
           len({("order-7", "send"), ("order-8", "send")}) == 2,
           {"route_count": len(routes), "logical_delivery_count": len(deliveries)})

    # A performed declaration is not a recipient's acceptance event.
    meanings = {"old": {"done": "performed"}, "new": {"done": "accepted"}}
    old_event = ("old", "done")
    wrongly_reinterpreted = meanings["new"][old_event[1]]
    original = meanings[old_event[0]][old_event[1]]
    record("TC04", wrongly_reinterpreted == "accepted" and original != "accepted",
           meanings["new"]["done"] == "accepted",
           {"old_event_meaning": original, "unqualified_reinterpretation": wrongly_reinterpreted})

    # Resetting local state cannot unsend a notification already received.
    initial = {"local": 0, "received_messages": 0}
    changed = {"local": 1, "received_messages": 1}
    compensated = {**changed, "local": 0}
    record("TC05", compensated["local"] == initial["local"] and compensated != initial,
           {**initial, "local": 0} == initial,
           {"local_restored": True, "external_residue": compensated["received_messages"]})

    # Ending new admission does not discharge an old deployed consumer.
    admitted_new = set()
    supported_consumers = {"old-product-case"}
    transferred = {"old-product-case": "successor-owner-accepted"}
    remaining_obligations = supported_consumers - transferred.keys()
    record("TC06", not admitted_new and bool(supported_consumers),
           not admitted_new and not remaining_obligations
           and all(transferred[consumer] == "successor-owner-accepted"
                   for consumer in supported_consumers),
           {"new_admissions": 0, "remaining_supported_consumers": 1,
            "control_transfer_receipts": transferred})

    # The selected local machines each can finish when their peer is assumed done.
    # Their composition starts with neither peer done and has no enabled action.
    def enabled(state):
        a, b = state
        return ((not a and b), (not b and a))
    record("TC07", not any(enabled((False, False))),
           any(enabled((False, True))),
           {"joint_start_enabled": list(enabled((False, False))), "missing_premise": "peer progress"})

    # Shared history is not a present executable prerequisite.
    historic_changes = {"a": {1, 2, 3}, "b": {1, 2, 3}}
    live_dependencies = {"a": set(), "b": set()}
    ready = lambda dependencies, done: {key for key, parents in dependencies.items()
                                       if key not in done and parents <= done}
    real_dependency = {"a": set(), "b": {"a"}}
    record("TC08", historic_changes["a"] == historic_changes["b"]
           and ready(live_dependencies, set()) == {"a", "b"},
           ready(real_dependency, set()) == {"a"} and ready(real_dependency, {"a"}) == {"b"},
           {"cochange_equal": True, "declared_live_dependency_edges": 0})

    # A common originating observation stays one observation through three reports.
    reports = [("architecture", "observation-1"), ("workflow", "observation-1"),
               ("agent", "observation-1")]
    record("TC09", len(reports) == 3 and len({r[1] for r in reports}) == 1,
           len({"observation-1", "observation-2"}) == 2,
           {"reports": 3, "originating_observations": 1})

    # Regime/case-mix change creates an aggregate improvement despite both strata worsening.
    old = {"hard": (45, 90), "easy": (9, 10)}
    new = {"hard": (4, 10), "easy": (72, 90)}
    rate = lambda d: sum(x[0] for x in d.values()) / sum(x[1] for x in d.values())
    worse = all(new[k][0] / new[k][1] < old[k][0] / old[k][1] for k in old)
    matched_old = sum(old[k][0] / old[k][1] for k in old) / 2
    matched_new = sum(new[k][0] / new[k][1] for k in new) / 2
    record("TC10", rate(new) > rate(old) and worse, matched_new < matched_old,
           {"old_aggregate": rate(old), "new_aggregate": rate(new),
            "matched_old": matched_old, "matched_new": matched_new})

    # A later boundary changes applicability without making an earlier verdict false.
    review = {"generation": 4, "valid_at_original_decision": True}
    record("TC11", review["valid_at_original_decision"] and review["generation"] != 5,
           review["generation"] == 4,
           {"historical_verdict_preserved": True, "current_generation_matches": False})

    # A permissive successor validator cannot establish its own predecessor-governed admission.
    predecessor = lambda action: action in {"read", "bounded-write"}
    successor = lambda action: True
    record("TC12", successor("unbounded-write") and not predecessor("unbounded-write"),
           predecessor("bounded-write") and successor("bounded-write"),
           {"successor_self_acceptance": True, "predecessor_admission": False})
    return results


if __name__ == "__main__":
    json.dump({"schema": "implementaudit.triad-analytical-cases.v1",
                      "evidence_ceiling": "FINITE_CONSTRUCTED_EXAMPLES_NOT_PRODUCT_OR_EMPIRICAL_PROOF",
               "cases": cases()}, sys.stdout, indent=2)
    sys.stdout.write("\n")
