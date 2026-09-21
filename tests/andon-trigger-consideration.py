#!/usr/bin/env python3
"""Bounded source/fixture qualification, never host cognition or route execution."""

import argparse
import copy
import json
from pathlib import Path
import re
import runpy


CHILD = "skills/implementaudit/references/child-agents.md"
OBLIGATIONS = {
    "all-four-at-boundary": "At a material decision or boundary, including a returned new constraint, explicitly consider audit-state, audit-assess, audit-implement and audit-andon.",
    "need-admission-entry-evidence": "Keep cognition need, ordinary admission, explicit direct Andon entry and actual route evidence separate in the existing task or route record; currentness=false is not an all-child no-need result.",
    "cold-roles": "Independent cold source review is not admitted audit-assess; isolated source preparation is not maintainer audit-implement qualification.",
    "genuine-recovery": "Completed compaction/resumption independently requires POST_COMPACTION_RECONCILIATION; its execution does not establish admitted native recovery or currentness.",
    "substantive-versus-cheap": "A substantive abnormality, a defeated countermeasure or changed routing behaviour requires fresh governor consideration; an already-bound cheap known failure bypasses diagnostic rerouting.",
    "unknown-dispositions": "Use scoped NOT_TRIGGERED or UNKNOWN dispositions; unknown hidden use is not NO.",
    "historical-defects": "Missed consideration, a missed visible witness and unknown historical use remain distinct, with no retroactive credit.",
    "direct-entry-ceiling": "An explicit direct cord-pull permits bounded audit-andon cognition without ordinary currentness or OPEN; it creates no R0033 OPEN, canonical authority or normal route credit.",
    "one-child-and-existing-gates": "Select at most one exact child under its applicable currentness, native-proof, independence and host-receipt gates; return changed constraints to the governor, never child-to-child dispatch or ceremonial replay.",
    "distinct-evidence": "Announcement, load/use evidence, return, acceptance and JOIN are separate facts.",
}


def source_consumer(root):
    # Reuse the accepted active-prose reader without invoking its old suites.
    existing = runpy.run_path(str(root / "tests/pre-use-announcement-contract.py"))
    return existing["section"], existing["procedural_prose_parts"]


def check_source(text, readers):
    section, prose = readers
    active = prose(section(text, "Governor-routed internal cognition"))
    for obligation, phrase in OBLIGATIONS.items():
        assert any(phrase in part for part in active), f"missing active trigger obligation: {obligation}"


def check_fixture_header(data):
    family = data.get("four_child_consideration")
    assert isinstance(family, dict), "missing symmetric direct/cold qualification family"
    assert family["evidence_kind"] == "SYNTHETIC_DECISION_PROJECTION"
    assert family["canonical_credit_granted"] is False
    assert family["host_model_conformance"] == "UNQUALIFIED"
    return family


CHILDREN = ("audit-state", "audit-assess", "audit-implement", "audit-andon")


def project(value):
    """Evaluate synthetic inputs only; never infer real admissions or load children."""
    for key in ("genuine_recovery_boundary", "state_gate_satisfied", "immutable_packet",
                "independence_satisfied", "exact_realized_candidate", "release_currentness",
                "returned_new_constraint", "currentness", "normal_open", "explicit_cord_pull",
                "host_receipt_gate_satisfied", "announcement", "returned", "accepted", "joined"):
        assert type(value[key]) is bool, f"nonboolean {key}"
    for key in ("recovery_need", "assessment_need"):
        assert value[key] is None or type(value[key]) is bool, f"invalid unknown/boolean {key}"
    assert value["work_kind"] in {"SOURCE_PREPARATION", "MAINTAINER_QUALIFICATION", "NONE", "UNKNOWN"}
    assert value["abnormality"] in {"NONE", "KNOWN_CHEAP", "SUBSTANTIVE", "UNKNOWN"}
    assert value["entry_mode"] in {"NORMAL", "DIRECT_ANDON"}
    assert value["requester"] in {"GOVERNOR", "CHILD"}
    selection = value["selection"]
    assert isinstance(selection, list) and all(child in CHILDREN for child in selection)
    actual = value["actual_route_evidence"]
    assert set(actual) == set(CHILDREN), "actual route evidence must name all four, including UNKNOWN"
    assert all(status in {"UNKNOWN", "OBSERVED_DIRECT", "OBSERVED_GOVERNED", "OBSERVED_HIDDEN", "VERIFIED_NOT_OBSERVED"} for status in actual.values())

    recovery = value["recovery_need"]
    assessment = value["assessment_need"]
    kind = value["work_kind"]
    abnormality = value["abnormality"]
    cognition = {
        "audit-state": "UNKNOWN" if recovery is None else "WARRANTED" if recovery and value["genuine_recovery_boundary"] else "NOT_TRIGGERED",
        "audit-assess": "UNKNOWN" if assessment is None else "WARRANTED" if assessment else "NOT_TRIGGERED",
        "audit-implement": "UNKNOWN" if kind == "UNKNOWN" else "WARRANTED" if kind == "MAINTAINER_QUALIFICATION" else "NOT_TRIGGERED",
        "audit-andon": "WARRANTED" if value["returned_new_constraint"] or abnormality == "SUBSTANTIVE" else "UNKNOWN" if abnormality == "UNKNOWN" else "NOT_TRIGGERED",
    }
    ordinary = value["currentness"] and value["normal_open"] and value["host_receipt_gate_satisfied"]
    gates = {
        "audit-state": value["state_gate_satisfied"],
        "audit-assess": value["immutable_packet"] and value["independence_satisfied"],
        "audit-implement": value["exact_realized_candidate"] and value["release_currentness"],
        "audit-andon": True,
    }
    admission = {child: "SATISFIED_IN_FIXTURE" if ordinary and gates[child] and cognition[child] == "WARRANTED" else "UNADMITTED" for child in CHILDREN}
    direct = "NOT_REQUESTED" if not value["explicit_cord_pull"] else "WARRANTED" if cognition["audit-andon"] == "WARRANTED" else "NOT_WARRANTED"
    selected = None
    if len(selection) > 1:
        decision = "REJECT_MULTIPLE_CHILDREN"
    elif selection and value["requester"] == "CHILD":
        decision = "STOP_CHILD_TO_CHILD_DISPATCH"
    elif not selection:
        decision = "NO_SELECTION"
    elif value["entry_mode"] == "DIRECT_ANDON":
        decision = "DIRECT_BOUNDED_COGNITION" if selection == ["audit-andon"] and direct == "WARRANTED" else "REFUSE_DIRECT_ENTRY"
        if decision == "DIRECT_BOUNDED_COGNITION":
            selected = "audit-andon"
    elif cognition[selection[0]] != "WARRANTED":
        decision = "REFUSE_UNWARRANTED_SELECTION"
    elif admission[selection[0]] != "SATISFIED_IN_FIXTURE":
        decision = "REFUSE_GOVERNED_ENTRY"
    else:
        selected = selection[0]
        decision = "GOVERNED_PREREQUISITES_SATISFIED"
    return {
        "cognition": cognition, "ordinary_admission": admission, "direct_entry": direct,
        "selected_child": selected, "decision": decision,
        "governor_reconsideration": value["returned_new_constraint"],
        "actual_route_evidence": dict(actual),
        "evidence_facts": {key: value[key] for key in ("announcement", "returned", "accepted", "joined")},
        "normal_route_credit": False, "canonical_credit": False,
    }


def check_case(case):
    observed = project(case["input"])
    assert observed == case["expected"], f"{case['id']}: expected {case['expected']!r}, observed {observed!r}"
    return observed


def expect_rejected(label, operation):
    try:
        operation()
    except AssertionError:
        return
    raise AssertionError(f"control falsely accepted: {label}")


def source_controls(text, readers):
    # Each deletion catches loss of that operative obligation. History-only
    # controls catch the previously witnessed quoted/commented false-green.
    without = text
    for label, phrase in OBLIGATIONS.items():
        pattern = r"\s+".join(re.escape(word) for word in phrase.split())
        changed, count = re.subn(pattern, "", text)
        assert count == 1, f"ineffective source deletion: {label}"
        expect_rejected(label, lambda: check_source(changed, readers))
        without, count = re.subn(pattern, "", without)
        assert count == 1
    historical = "\n\n".join(OBLIGATIONS.values())
    for label, history in (
        ("comment-only", "<!--\n" + historical + "\n-->\n"),
        ("fence-only", "```text\n" + historical + "\n```\n"),
        ("quote-only", "\n".join("> " + line for line in historical.splitlines()) + "\n\n"),
    ):
        changed = without.replace("A missing gate refuses child loading;", history + "A missing gate refuses child loading;")
        expect_rejected(label, lambda: check_source(changed, readers))
    return len(OBLIGATIONS) + 3


def fixture_controls(family):
    cases = family["cases"]
    assert len({case["id"] for case in cases}) == len(cases), "duplicate case identity"
    for case in cases:
        check_case(case)
    # Change the actual input while freezing the former expectation. Each
    # paired case independently supplies the corrected literal expectation.
    for before, after in family["paired_controls"]:
        left, right = cases[before - 1], cases[after - 1]
        changed_fields = [key for key in left["input"] if left["input"][key] != right["input"][key]]
        assert len(changed_fields) == 1, f"pair is not a single-input control: {before}/{after}"
        changed = copy.deepcopy(left)
        changed["input"] = copy.deepcopy(right["input"])
        expect_rejected(f"stale expectation {before}/{after}", lambda: check_case(changed))
    # Missing prerequisite must defeat a fixture admission independently.
    gate_controls = ((5, "currentness"), (5, "host_receipt_gate_satisfied"),
                     (7, "immutable_packet"), (9, "exact_realized_candidate"),
                     (9, "release_currentness"), (11, "state_gate_satisfied"))
    for number, gate in gate_controls:
        changed = copy.deepcopy(cases[number - 1])
        assert changed["input"][gate] is True
        changed["input"][gate] = False
        assert project(changed["input"])["decision"] == "REFUSE_GOVERNED_ENTRY", gate
        expect_rejected(f"missing {gate}", lambda: check_case(changed))
    changed = copy.deepcopy(cases[0]["input"])
    del changed["actual_route_evidence"]["audit-state"]
    expect_rejected("omitted unknown state evidence", lambda: project(changed))
    for field, child in (("work_kind", "audit-implement"), ("abnormality", "audit-andon")):
        changed = copy.deepcopy(cases[0]["input"])
        changed[field] = "UNKNOWN"
        assert project(changed)["cognition"][child] == "UNKNOWN", f"unknown collapsed to NO: {child}"
    return len(cases), len(family["paired_controls"]) + len(gate_controls) + 1, 2


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--source-only", action="store_true")
    parser.add_argument("--fixture-only", action="store_true")
    parser.add_argument("--fixture", type=Path)
    args = parser.parse_args()
    fixture = args.fixture or args.root / "fixtures/a-to-g/andon-trigger-routing.json"
    if args.fixture_only:
        check_fixture_header(json.loads(fixture.read_text(encoding="utf-8")))
        return
    readers = source_consumer(args.root)
    text = (args.root / CHILD).read_text(encoding="utf-8")
    check_source(text, readers)
    if args.source_only:
        print("andon-trigger-consideration: source obligations present (source structural only)")
        return
    family = check_fixture_header(json.loads(fixture.read_text(encoding="utf-8")))
    cases, negatives, unknowns = fixture_controls(family)
    source_negatives = source_controls(text, readers)
    print(f"andon-trigger-consideration: ok ({cases} input cases; {negatives} input negatives; {unknowns} unknown-boundary controls; {source_negatives} active-source negatives; source/fixture only; host/model UNQUALIFIED)")


if __name__ == "__main__":
    main()
