#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

if command -v python >/dev/null 2>&1; then
  py_cmd=(python)
elif command -v python3 >/dev/null 2>&1; then
  py_cmd=(python3)
elif command -v py >/dev/null 2>&1; then
  py_cmd=(py -3)
else
  printf 'work-graph-compiler.test: python is required\n' >&2
  exit 1
fi

"${py_cmd[@]}" - \
  "$repo_root/skills/implementaudit/scripts/compile-work-graph.py" <<'PY'
import copy
import hashlib
import importlib.util
import json
import pathlib
import subprocess
import sys
import tempfile

module_path = pathlib.Path(sys.argv[1])
if not module_path.is_file():
    raise SystemExit("work-graph-compiler.test: compiler missing")
spec = importlib.util.spec_from_file_location("compile_work_graph", module_path)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)


def canonical(value):
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def signed_graph(value):
    result = copy.deepcopy(value)
    result["digest"] = hashlib.sha256(canonical(result)).hexdigest()
    return result


base = {
    "schema": "implementaudit.work-graph.v1",
    "population": {"total_cells": 4},
    "cells": [
        {"id": "A", "state": "ACTIVE", "deps": []},
        {"id": "D", "state": "DONE", "deps": []},
        {"id": "R", "state": "READY", "deps": ["D"]},
        {"id": "B", "state": "BLOCKED", "deps": ["A", "R"]},
    ],
    "serialization_groups": {
        "W_ROUTE": ["R", "A"],
        "R_BROWSER": ["B", "A"],
    },
}
graph = signed_graph(base)
projection = module.compile_frontier_projection(canonical(graph))
expected_without_digest = {
    "population": 4,
    "counts": {"DONE": 1, "ACTIVE": 1, "READY": 1, "BLOCKED": 1},
    "active": ["A"],
    "ready": ["R"],
    "blocked_summary": {"B": ["A", "R"]},
    "writer_holds": {"W_ROUTE": ["A", "R"]},
    "resource_holds": {"R_BROWSER": ["A", "B"]},
}
expected = dict(expected_without_digest)
expected["digest"] = hashlib.sha256(canonical(expected_without_digest)).hexdigest()
if projection != expected:
    raise SystemExit(
        "positive projection mismatch:\n"
        + json.dumps(projection, indent=2, sort_keys=True)
    )

def expect_reject(raw, label, message_fragment):
    try:
        module.compile_frontier_projection(raw)
    except module.WorkGraphError as exc:
        if message_fragment not in str(exc):
            raise SystemExit(f"{label}: wrong diagnostic: {exc}")
    else:
        raise SystemExit(f"{label}: invalid graph accepted")


expect_reject(b"\xef\xbb\xbf{}", "BOM", "BOM")
expect_reject(b'{"schema":"implementaudit.work-graph.v1","schema":"x"}',
              "duplicate key", "duplicate key")
expect_reject(b"\xff", "invalid UTF-8", "UTF-8")
expect_reject(canonical({"value": 1.5}), "float", "floats")
expect_reject(b'{"value":NaN}', "non-finite", "non-finite")
expect_reject(canonical({"value": 9223372036854775808}),
              "wide integer", "signed 64-bit")

unknown_state = copy.deepcopy(base)
unknown_state["cells"][0]["state"] = "RUNNING"
expect_reject(canonical(unknown_state), "unknown state", "unknown cell state")

count_mismatch = copy.deepcopy(base)
count_mismatch["population"]["total_cells"] = 5
expect_reject(canonical(count_mismatch), "count mismatch", "frontier count")

duplicate_id = copy.deepcopy(base)
duplicate_id["cells"][1]["id"] = "A"
expect_reject(canonical(duplicate_id), "duplicate cell", "duplicate cell id")

dangling = copy.deepcopy(base)
dangling["cells"][2]["deps"] = ["MISSING"]
expect_reject(canonical(dangling), "dependency closure", "unknown dependency")

cycle = copy.deepcopy(base)
cycle["cells"][0]["deps"] = ["B"]
cycle["cells"][3]["deps"] = ["A"]
expect_reject(canonical(cycle), "dependency cycle", "cycle")

missing_holds = copy.deepcopy(base)
del missing_holds["serialization_groups"]
expect_reject(canonical(missing_holds), "missing holds", "serialization_groups")

no_holds = copy.deepcopy(base)
no_holds["serialization_groups"] = {}
no_hold_projection = module.compile_frontier_projection(canonical(no_holds))
if no_hold_projection["writer_holds"] != {} or no_hold_projection["resource_holds"] != {}:
    raise SystemExit("honest no-hold graph did not project empty hold maps")

empty_group = copy.deepcopy(base)
empty_group["serialization_groups"]["W_EMPTY"] = []
expect_reject(canonical(empty_group), "empty declared hold", "non-empty array")

duplicate_holder = copy.deepcopy(base)
duplicate_holder["serialization_groups"]["W_ROUTE"].append("A")
expect_reject(canonical(duplicate_holder), "duplicate declared hold", "duplicate cell")

unknown_holder = copy.deepcopy(base)
unknown_holder["serialization_groups"]["W_ROUTE"].append("MISSING")
expect_reject(canonical(unknown_holder), "unknown hold", "unknown cell")

unknown_hold_kind = copy.deepcopy(base)
unknown_hold_kind["serialization_groups"]["X_OTHER"] = ["A"]
expect_reject(canonical(unknown_hold_kind), "unknown hold kind", "unknown hold kind")

stale = copy.deepcopy(graph)
stale["digest"] = "0" * 64
expect_reject(canonical(stale), "stale digest", "stale digest")

stale_signed_omission = copy.deepcopy(graph)
del stale_signed_omission["serialization_groups"]["R_BROWSER"]
expect_reject(
    canonical(stale_signed_omission),
    "stale signed hold omission",
    "stale digest",
)

if projection["writer_holds"] != {"W_ROUTE": ["A", "R"]}:
    raise SystemExit("declared writer holds were not projected losslessly")
if projection["resource_holds"] != {"R_BROWSER": ["A", "B"]}:
    raise SystemExit("declared resource holds were not projected losslessly")

shuffled = copy.deepcopy(base)
shuffled["cells"] = list(reversed(shuffled["cells"]))
shuffled["serialization_groups"] = {
    "R_BROWSER": ["A", "B"],
    "W_ROUTE": ["A", "R"],
}
if module.compile_frontier_projection(canonical(signed_graph(shuffled))) != projection:
    raise SystemExit("projection changed with equivalent input ordering")

# R0035/HC-H4 activation-time causal REDs. These are complete positive inputs
# for the new preparation surface plus exact source-product failures; the
# pre-amendment compiler must expose all three false-pass families at once.
prep_red = copy.deepcopy(base)
prep_red["graph_id"] = "r0035-preparation-causal-red"
prep_red["cells"][3]["preparation"] = {
    "kinds": ["BRIEF", "RED_DESIGN"],
    "effect_class": "READ_ONLY_EFFECT_FREE",
    "final_composed_only": False,
    "execution_unavailable": {
        "kind": "UNMET_DEPENDENCIES",
        "dependencies": ["A", "R"],
    },
    "rank": {
        "terminal_unlock_value": 3,
        "expected_reuse": 2,
        "cost": 1,
        "invalidation_risk": 1,
    },
    "record": {
        "graph_path": "WORK_GRAPH.json",
        "receipt": "refs/implementaudit/continuity-receipts/v0333-release/G0130@"
        + "a" * 40,
        "predecessors": [
            {"cell_id": "A", "state": "ACTIVE"},
            {"cell_id": "R", "state": "READY"},
        ],
        "interface_assumptions": {"route_contract": "b" * 64},
        "inspected_paths": ["skills/implementaudit/references/child-agents.md"],
        "proposed_paths": ["tests/work-graph-compiler.test.sh"],
        "allowed_work": ["BRIEF", "RED_DESIGN"],
        "forbidden_work": [
            "SOURCE_MUTATION",
            "GRAPH_MUTATION",
            "LIFECYCLE_CREDIT",
            "REF_MUTATION",
            "PACKAGE_INSTALL_PUBLICATION",
            "EXTERNAL_EFFECT",
        ],
        "cost_boundary": "bounded",
        "invalidators": [
            "TARGET_STATE",
            "DEPENDENCY_RESULT",
            "INTERFACE_ASSUMPTION",
        ],
        "activation_revalidation": [
            "CURRENTNESS",
            "DEPENDENCY_RESULTS",
            "INTERFACE_ASSUMPTIONS",
            "CAUSAL_RED",
        ],
    },
}
causal_failures = []
prep_projection = module.compile_frontier_projection(
    canonical(signed_graph(prep_red))
)
if [item["cell_id"] for item in prep_projection.get("preparation_frontier", [])] != ["B"]:
    causal_failures.append("PF-01/PF-03: opt-in BLOCKED preparation omitted")

null_product = copy.deepcopy(base)
null_product["cells"][1]["id"] = "R38-C06"
null_product["cells"][1]["owner"] = "R0038"
null_product["cells"][2]["deps"] = ["R38-C06"]
null_product["cells"][1]["source_bearing"] = True
null_product["cells"][1]["result"] = None
try:
    module.compile_frontier_projection(canonical(signed_graph(null_product)))
except module.WorkGraphError:
    pass
else:
    causal_failures.append("QP-01: source-bearing DONE/null result accepted")

stale_product = copy.deepcopy(base)
stale_product["cells"][1]["id"] = "HC-H7A"
stale_product["cells"][1]["owner"] = "R0037"
stale_product["cells"][2]["deps"] = ["HC-H7A"]
stale_product["cells"][1]["source_bearing"] = True
stale_product["cells"][1]["result"] = (
    "final convergence descendant d75631b148c4fafe663357a82c5f38b1b4b255b9 "
    "/ tree 9377533dee410aacf8bdd789c1fe4cdbaf705d03 preserves rejected "
    "trajectory through 23b61db0; stale free-form product pointer"
)
try:
    module.compile_frontier_projection(canonical(signed_graph(stale_product)))
except module.WorkGraphError:
    pass
else:
    causal_failures.append("QP-02: source-bearing DONE/free-form result accepted")

if causal_failures:
    raise SystemExit("R0035 causal RED:\n" + "\n".join(causal_failures))

# P01/P08/P09: preparation is advisory, leaves lifecycle/execution bytes alone
# on legacy input, and carries the exact no-credit record fields.
prep_item = prep_projection["preparation_frontier"][0]
if prep_item["observed_state"] != "BLOCKED":
    raise SystemExit("P01: blocked preparation changed observed state")
if prep_projection["counts"] != projection["counts"] or prep_projection["ready"] != projection["ready"]:
    raise SystemExit("P08: preparation changed lifecycle or executable dispatch")
for field in ("lifecycle_credit", "implementation_evidence", "authority_minted"):
    if prep_item[field] != "NONE":
        raise SystemExit(f"P08: preparation minted {field}")
legacy_again = module.compile_frontier_projection(canonical(graph))
if legacy_again != expected:
    raise SystemExit("P09: legacy execution projection bytes changed")

# P02: an otherwise READY target is preparation-eligible only while an exact
# named hold has a current ACTIVE holder.
ready_prep = copy.deepcopy(base)
ready_prep["graph_id"] = "r0035-ready-hold-preparation"
ready_decl = copy.deepcopy(prep_red["cells"][3]["preparation"])
ready_decl["execution_unavailable"] = {
    "kind": "LIVE_HOLD",
    "group": "W_ROUTE",
    "holders": ["A"],
}
ready_decl["record"]["predecessors"] = [
    {"cell_id": "A", "state": "ACTIVE"},
    {"cell_id": "D", "state": "DONE"},
]
ready_prep["cells"][2]["preparation"] = ready_decl
ready_projection = module.compile_frontier_projection(canonical(signed_graph(ready_prep)))
if [item["cell_id"] for item in ready_projection["preparation_frontier"]] != ["R"]:
    raise SystemExit("P02: READY live-hold preparation missing")
if ready_projection["ready"] != ["R"]:
    raise SystemExit("P02: preparation consumed executable READY state")

# P03/P04/P07: absence is the cheap path; incomplete, ineligible, stale,
# effectful, fabricated, or activation-incomplete declarations fail closed.
incomplete_prep = copy.deepcopy(base)
incomplete_prep["cells"][3]["preparation"] = {}
expect_reject(canonical(incomplete_prep), "P03 incomplete preparation", "incomplete")

done_prep = copy.deepcopy(prep_red)
done_prep["cells"][3]["state"] = "DONE"
expect_reject(canonical(done_prep), "P03 DONE preparation", "not preparation-eligible")

active_prep = copy.deepcopy(prep_red)
active_prep["cells"][3]["state"] = "ACTIVE"
expect_reject(canonical(active_prep), "P03 ACTIVE preparation", "not preparation-eligible")

final_only_prep = copy.deepcopy(prep_red)
final_only_prep["cells"][3]["preparation"]["final_composed_only"] = True
expect_reject(canonical(final_only_prep), "P03 final-composed-only preparation", "forbidden")

effectful_prep = copy.deepcopy(prep_red)
effectful_prep["cells"][3]["preparation"]["effect_class"] = "SOURCE_MUTATION"
expect_reject(canonical(effectful_prep), "P03 effectful preparation", "effect-free")

dependency_mismatch = copy.deepcopy(prep_red)
dependency_mismatch["cells"][3]["preparation"]["execution_unavailable"]["dependencies"] = ["A"]
expect_reject(canonical(dependency_mismatch), "P04 dependency mismatch", "binding mismatch")

forbidden_gap = copy.deepcopy(prep_red)
forbidden_gap["cells"][3]["preparation"]["record"]["forbidden_work"].remove("EXTERNAL_EFFECT")
expect_reject(canonical(forbidden_gap), "P04 forbidden boundary gap", "forbidden-work")

authority_gap = copy.deepcopy(prep_red)
authority_gap["cells"][3]["preparation"]["record"]["receipt"] = "self-attested"
expect_reject(canonical(authority_gap), "P04 unresolved authority", "continuity receipt")

fabricated_prep = copy.deepcopy(prep_red)
fabricated_prep["cells"][3]["preparation"]["record"]["predecessors"][0]["cell_id"] = "MISSING"
expect_reject(canonical(fabricated_prep), "P04 fabricated predecessor", "fabricated")

stale_prep = copy.deepcopy(prep_red)
stale_prep["cells"][3]["preparation"]["record"]["predecessors"][0]["state"] = "DONE"
expect_reject(canonical(stale_prep), "P04 stale predecessor", "stale predecessor")

unresolved_assumption = copy.deepcopy(prep_red)
unresolved_assumption["cells"][3]["preparation"]["record"]["interface_assumptions"] = {}
expect_reject(canonical(unresolved_assumption), "P04 unresolved assumption", "assumptions required")

activation_gap = copy.deepcopy(prep_red)
activation_gap["cells"][3]["preparation"]["record"]["activation_revalidation"].remove("CAUSAL_RED")
expect_reject(canonical(activation_gap), "P07 activation without causal RED", "activation revalidation")

if not module.validate_preparation_activation_v1(
    prep_item,
    current_receipt=prep_item["receipt"],
    current_target_binding_sha256=prep_item["target_binding_sha256"],
    current_predecessors=prep_item["predecessors"],
    current_interface_assumptions=prep_item["interface_assumptions"],
    causal_red_passed=True,
):
    raise SystemExit("P07: exact activation revalidation rejected")
for label, overrides, diagnostic in (
    ("P07 stale currentness", {"current_receipt":
        "refs/implementaudit/continuity-receipts/v0333-release/G0131@" + "a" * 40},
     "currentness"),
    ("P07 target drift", {"current_target_binding_sha256": "0" * 64},
     "target binding"),
    ("P07 dependency-result drift", {"current_predecessors": []},
     "dependency results"),
    ("P07 assumption drift", {"current_interface_assumptions": {"route_contract": "0" * 64}},
     "interface assumptions"),
    ("P07 causal RED missing", {"causal_red_passed": False},
     "causal RED"),
):
    arguments = {
        "current_receipt": prep_item["receipt"],
        "current_target_binding_sha256": prep_item["target_binding_sha256"],
        "current_predecessors": prep_item["predecessors"],
        "current_interface_assumptions": prep_item["interface_assumptions"],
        "causal_red_passed": True,
    }
    arguments.update(overrides)
    try:
        module.validate_preparation_activation_v1(prep_item, **arguments)
    except module.WorkGraphError as exc:
        if diagnostic not in str(exc):
            raise SystemExit(f"{label}: wrong diagnostic: {exc}")
    else:
        raise SystemExit(f"{label}: invalid activation accepted")

# P05: rank is lexicographic and stable-ID deterministic, never a score that
# can admit an ineligible cell.
rank_graph = copy.deepcopy(prep_red)
rank_graph["population"]["total_cells"] = 6
for cell_id, value, reuse, cost, risk in (
    ("B2", 4, 1, 1, 1),
    ("B1", 3, 9, 0, 0),
):
    declaration = copy.deepcopy(prep_red["cells"][3]["preparation"])
    declaration["rank"] = {
        "terminal_unlock_value": value,
        "expected_reuse": reuse,
        "cost": cost,
        "invalidation_risk": risk,
    }
    rank_graph["cells"].append(
        {"id": cell_id, "state": "BLOCKED", "deps": ["A"], "preparation": declaration}
    )
    declaration["execution_unavailable"]["dependencies"] = ["A"]
    declaration["record"]["predecessors"] = [{"cell_id": "A", "state": "ACTIVE"}]
rank_projection = module.compile_frontier_projection(canonical(signed_graph(rank_graph)))
if [item["cell_id"] for item in rank_projection["preparation_frontier"]] != ["B2", "B1", "B"]:
    raise SystemExit("P05: preparation rank or stable tie-break is not deterministic")

# P06: unrelated graph drift changes whole-graph identity but preserves the
# target slice; target/interface drift changes the target binding.
unrelated = copy.deepcopy(prep_red)
unrelated["cells"][1]["note"] = "unrelated compared drift"
unrelated_item = module.compile_frontier_projection(canonical(signed_graph(unrelated)))["preparation_frontier"][0]
if unrelated_item["graph"]["sha256"] == prep_item["graph"]["sha256"]:
    raise SystemExit("P06: unrelated graph drift was not observable")
if unrelated_item["target_binding_sha256"] != prep_item["target_binding_sha256"]:
    raise SystemExit("P06: unrelated drift invalidated the target slice")
target_drift = copy.deepcopy(prep_red)
target_drift["cells"][3]["preparation"]["record"]["interface_assumptions"]["route_contract"] = "c" * 64
target_item = module.compile_frontier_projection(canonical(signed_graph(target_drift)))["preparation_frontier"][0]
if target_item["target_binding_sha256"] == prep_item["target_binding_sha256"]:
    raise SystemExit("P06: interface drift did not invalidate the target slice")


def product_result(seed, kind, target):
    return {
        "product": {
            "commit": seed * 40,
            "tree": chr(ord(seed) + 1) * 40,
            "review_sha256": chr(ord(seed) + 2) * 64,
        },
        "disposition": {"kind": kind, "target": target},
    }


# Q03/Q06/Q10/Q12: cell and non-cell products emit once; product-aware order
# only reorders already-READY work and never changes lifecycle population.
product_graph = copy.deepcopy(base)
product_graph["cells"][1]["source_bearing"] = True
product_graph["cells"][1]["result"] = product_result("1", "COMPOSED", "R")
product_graph["integration_topology"] = {
    "qualified_products": [
        {"owner": "R0033", "result": product_result("4", "COMPOSED", "R")}
    ]
}
product_projection = module.compile_frontier_projection(canonical(signed_graph(product_graph)))
products = product_projection["product_frontier"]
if products["qualified_products"] != 2 or products["counts"]["COMPOSED"] != 2:
    raise SystemExit("Q03/Q06: qualified product emitted zero or multiple times")
if products["current_products"] != 2 or products["integration_debt"] != 2:
    raise SystemExit("Q07/Q09: current product or integration debt count changed")
if products["ready_preference"] != ["R"] or product_projection["ready"] != ["R"]:
    raise SystemExit("Q10: product preference changed execution eligibility")
if product_projection["population"] != 4 or product_projection["counts"] != projection["counts"]:
    raise SystemExit("Q06/Q12: product projection changed lifecycle population")

# Q04/Q05: malformed, ambiguous, and unresolved product/disposition bindings
# fail closed.
multi_disposition = copy.deepcopy(product_graph)
multi_disposition["cells"][1]["result"]["second_disposition"] = {
    "kind": "INTEGRATED", "target": "R"
}
expect_reject(canonical(multi_disposition), "Q04 multiple dispositions", "one disposition")

zero_disposition = copy.deepcopy(product_graph)
del zero_disposition["cells"][1]["result"]["disposition"]
expect_reject(canonical(zero_disposition), "Q04 zero dispositions", "one disposition")

duplicate_product = copy.deepcopy(product_graph)
duplicate_product["integration_topology"]["qualified_products"][0]["result"]["product"] = copy.deepcopy(
    duplicate_product["cells"][1]["result"]["product"]
)
expect_reject(canonical(duplicate_product), "Q03 duplicate product", "more than once")

unknown_consumer = copy.deepcopy(product_graph)
unknown_consumer["cells"][1]["result"]["disposition"]["target"] = "MISSING"
expect_reject(canonical(unknown_consumer), "Q05 unknown consumer", "unknown target")

unknown_product = copy.deepcopy(product_graph)
unknown_product["cells"][1]["result"]["product"]["commit"] = "not-a-commit"
expect_reject(canonical(unknown_product), "Q05 malformed product", "40-hex")

unknown_integration_head = copy.deepcopy(product_graph)
unknown_integration_head["cells"][1]["result"] = product_result(
    "1", "INTEGRATED", "7" * 40
)
expect_reject(
    canonical(unknown_integration_head),
    "Q05 unknown integration head",
    "unknown integration head",
)

integrated_product = copy.deepcopy(unknown_integration_head)
integrated_product["integration_topology"]["integration_heads"] = ["7" * 40]
integrated_projection = module.compile_frontier_projection(
    canonical(signed_graph(integrated_product))
)
if integrated_projection["product_frontier"]["counts"]["INTEGRATED"] != 1:
    raise SystemExit("Q03/Q05: resolved integration head did not emit")

unknown_superseder = copy.deepcopy(product_graph)
unknown_superseder["cells"][1]["result"] = product_result(
    "1", "SUPERSEDED", "9" * 40
)
expect_reject(
    canonical(unknown_superseder),
    "Q05 unknown superseding product",
    "unknown product identity",
)

# Q08: a composition proposal is admitted only from existing topology
# authority when products are current, dependencies are DONE, independent
# qualification is exact, and no declared writer/resource hold is live.
composition_graph = copy.deepcopy(product_graph)
composition_graph["serialization_groups"]["W_ROUTE"] = ["R"]
composition_graph["integration_topology"]["composition_proposals"] = [
    {
        "owner": "R",
        "products": ["1" * 40, "4" * 40],
        "qualification_review_sha256": "8" * 64,
        "integration_authority":
            "refs/implementaudit/continuity-receipts/v0333-release/G0130@"
            + "9" * 40,
    }
]
composition_projection = module.compile_frontier_projection(
    canonical(signed_graph(composition_graph))
)
if [item["owner"] for item in composition_projection["product_frontier"]["composition_proposals"]] != ["R"]:
    raise SystemExit("Q08: admissible composition proposal was omitted")

hold_blocked_composition = copy.deepcopy(composition_graph)
hold_blocked_composition["serialization_groups"]["W_ROUTE"] = ["R", "A"]
expect_reject(
    canonical(hold_blocked_composition),
    "Q08 live-hold composition",
    "live hold conflict",
)

unqualified_composition = copy.deepcopy(composition_graph)
unqualified_composition["integration_topology"]["composition_proposals"][0][
    "qualification_review_sha256"
] = "not-a-review"
expect_reject(
    canonical(unqualified_composition),
    "Q08 unqualified composition",
    "64-hex",
)

unauthorized_composition = copy.deepcopy(composition_graph)
unauthorized_composition["integration_topology"]["composition_proposals"][0][
    "integration_authority"
] = "self-attested"
expect_reject(
    canonical(unauthorized_composition),
    "Q08 unauthorized composition",
    "unresolved integration authority",
)

proposal_without_product = copy.deepcopy(base)
proposal_without_product["integration_topology"] = {
    "composition_proposals": copy.deepcopy(
        composition_graph["integration_topology"]["composition_proposals"]
    )
}
expect_reject(
    canonical(proposal_without_product),
    "Q08 proposal without product",
    "no qualified products",
)

# Q07: terminal ancestors remain inspectable but are excluded from the exact
# current-product count rather than being double-counted as inventory.
terminal_products = copy.deepcopy(product_graph)
terminal_products["integration_topology"]["qualified_products"].extend(
    [
        {"owner": "OLD", "result": product_result("7", "SUPERSEDED", "4" * 40)},
        {"owner": "BAD", "result": product_result("a", "REJECTED", "a" * 40)},
    ]
)
terminal_products_projection = module.compile_frontier_projection(
    canonical(signed_graph(terminal_products))
)["product_frontier"]
if terminal_products_projection["qualified_products"] != 4:
    raise SystemExit("Q07: terminal product history disappeared")
if terminal_products_projection["current_products"] != 2:
    raise SystemExit("Q07: terminal products were double-counted as current")
if terminal_products_projection["counts"]["SUPERSEDED"] != 1 or terminal_products_projection["counts"]["REJECTED"] != 1:
    raise SystemExit("Q07: terminal product dispositions are not inspectable")

# Q10: inventory changes only the stable order among already-READY cells.
preference_graph = copy.deepcopy(product_graph)
preference_graph["population"]["total_cells"] = 5
preference_graph["cells"].append(
    {"id": "R2", "state": "READY", "deps": ["D"]}
)
preference_graph["integration_topology"]["qualified_products"].append(
    {"owner": "R0034", "result": product_result("7", "COMPOSED", "R2")}
)
preference_projection = module.compile_frontier_projection(
    canonical(signed_graph(preference_graph))
)
if preference_projection["ready"] != ["R", "R2"]:
    raise SystemExit("Q10: product projection changed READY membership")
if preference_projection["product_frontier"]["ready_preference"] != ["R", "R2"]:
    raise SystemExit("Q10: product-aware preference did not use current inventory")

# Q07/Q09/Q11: terminal categories stay inspectable, current-product and debt
# counts are deterministic, and the frozen historical/current censuses remain
# separate zero-stranded controls.
summary_historical = module.summarize_product_dispositions_v1(
    ["CONSUMED"] + ["COMPOSED"] * 23 + ["INTEGRATED"] * 5
    + ["EXPLICITLY_DEFERRED_TO_NAMED_JOIN"]
)
if summary_historical != {
    "total": 30, "consumed": 1, "composed": 23, "integrated": 5,
    "superseded": 0, "rejected": 0, "deferred": 1,
    "potentially_stranded": 0, "p0": "NOT_TRIGGERED",
}:
    raise SystemExit("Q11: historical 30/1/23/5/0/1/0 census changed")
summary_current = module.summarize_product_dispositions_v1(
    ["COMPOSED"] * 25 + ["INTEGRATED"] * 5
    + ["EXPLICITLY_DEFERRED_TO_NAMED_JOIN"] * 3
)
if summary_current != {
    "total": 33, "consumed": 0, "composed": 25, "integrated": 5,
    "superseded": 0, "rejected": 0, "deferred": 3,
    "potentially_stranded": 0, "p0": "NOT_TRIGGERED",
}:
    raise SystemExit("Q11: current 33/0/25/5/0/3/0 census changed")

terminal_summary = module.summarize_product_dispositions_v1(
    ["COMPOSED", "SUPERSEDED", "REJECTED"]
)
if terminal_summary["total"] != 3 or terminal_summary["superseded"] != 1 or terminal_summary["rejected"] != 1:
    raise SystemExit("Q07/Q09: terminal product dispositions were collapsed")

stranded_summary = module.summarize_product_dispositions_v1(
    ["COMPOSED", None, "EXPLICITLY_DEFERRED_TO_NAMED_JOIN"]
)
if stranded_summary["potentially_stranded"] != 1 or stranded_summary["p0"] != "TRIGGERED":
    raise SystemExit("Q09: undisposed product did not produce deterministic debt/P0")

with tempfile.TemporaryDirectory() as temp_dir:
    graph_path = pathlib.Path(temp_dir, "WORK_GRAPH.json")
    graph_path.write_bytes(canonical(graph))
    state_path = pathlib.Path(temp_dir, "STATE.md")
    state_path.write_text("| A | DONE | duplicate narrative only |\n", encoding="utf-8")
    mutant_path = pathlib.Path(temp_dir, "adjacent-state-mutant.py")
    mutant_path.write_text(
        """import json
import pathlib
import subprocess
import sys

compiler, graph = sys.argv[1:]
completed = subprocess.run(
    [sys.executable, compiler, graph],
    check=True,
    stdout=subprocess.PIPE,
)
projection = json.loads(completed.stdout)
state = pathlib.Path(graph).with_name("STATE.md").read_text(encoding="utf-8")
if "| A | DONE |" in state:
    projection["active"] = []
    projection["counts"]["ACTIVE"] = 0
    projection["counts"]["DONE"] += 1
sys.stdout.write(json.dumps(projection, sort_keys=True, separators=(",", ":")))
""",
        encoding="utf-8",
    )

    def assert_cli_projection(command, label):
        completed = subprocess.run(
            command,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        if completed.returncode != 0:
            raise AssertionError(f"{label}: CLI rejected graph: " + completed.stderr.decode())
        if completed.stdout != canonical(expected):
            raise AssertionError(f"{label}: CLI output is not exact canonical projection bytes")
        if completed.stderr:
            raise AssertionError(f"{label}: CLI emitted stderr on success")

    assert_cli_projection(
        [sys.executable, str(module_path), str(graph_path)],
        "canonical compiler with adjacent narrative",
    )
    try:
        assert_cli_projection(
            [
                sys.executable,
                str(mutant_path),
                str(module_path),
                str(graph_path),
            ],
            "adjacent-state mutant",
        )
    except AssertionError:
        pass
    else:
        raise SystemExit("adjacent-state mutant was not rejected")
    print(
        "work-graph-compiler.test: contradiction retained: "
        "STATE A=DONE; WORK_GRAPH A=ACTIVE; adjacent-state mutant rejected"
    )

print("work-graph-compiler.test: ok")
PY
