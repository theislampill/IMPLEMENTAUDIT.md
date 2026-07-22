#!/usr/bin/env python3
"""Report-claim reconstruction tests. No model or network calls."""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "lib"))
import reporting  # noqa: E402
import verdict as verdictlib  # noqa: E402


FIXTURE = {
    "id": "B3-v2-test",
    "properties": [
        {"name": "p1", "required": True},
        {"name": "p2", "required": True},
        {"name": "note", "required": False},
    ],
}


def verdict(p1=True, p2=True, complete=True):
    def prop(value):
        if value is None:
            return {"state": "INCOMPLETE", "pass": None,
                    "evidence": "missing"}
        return {"state": "PASS" if value else "FAIL", "pass": value,
                "evidence": "bound-event:1"}

    return {
        "properties": {"p1": prop(p1), "p2": prop(p2),
                       "note": prop(True)},
        "adjudication": {
            "property_evidence_complete": complete,
            "all_required_properties_true": (
                None if not complete else bool(p1 and p2)),
        },
    }


def must_refuse(name, fn, failures):
    try:
        fn()
    except reporting.ClaimNotReconstructible:
        print(f"  [OK] {name}")
        return
    print(f"  [XX] {name}")
    failures.append(name)


def main():
    failures = []
    good = verdict()
    matrix = reporting.reconstruct_required_matrix(good, FIXTURE)
    ok = matrix == {"p1": True, "p2": True}
    print(f"  [{'OK' if ok else 'XX'}] report-reconstructs-complete-matrix")
    if not ok:
        failures.append("report-reconstructs-complete-matrix")

    reporting.require_all_required_true([good], FIXTURE,
                                        claim="all properties at ceiling")

    must_refuse(
        "report-refuses-empty-properties",
        lambda: reporting.require_all_required_true(
            [{"properties": {}, "adjudication": {
                "property_evidence_complete": False,
                "all_required_properties_true": None}}],
            FIXTURE, claim="all properties at ceiling"), failures)
    must_refuse(
        "report-refuses-incomplete-properties",
        lambda: reporting.require_all_required_true(
            [verdict(p1=None, complete=False)], FIXTURE,
            claim="all properties at ceiling"), failures)
    must_refuse(
        "report-refuses-recorded-failure",
        lambda: reporting.require_all_required_true(
            [verdict(p2=False)], FIXTURE,
            claim="all properties at ceiling"), failures)
    no_required = {"id": "no-required-properties", "properties": [
        {"name": "note", "required": False},
    ]}
    vacuous = {
        "properties": {"note": {
            "state": "PASS", "pass": True, "evidence": "bound-event:1"}},
        "adjudication": {
            "property_evidence_complete": True,
            "all_required_properties_true": True,
        },
    }
    must_refuse(
        "report-refuses-vacuous-no-required-property-ceiling",
        lambda: reporting.require_all_required_true(
            [vacuous], no_required, claim="all properties at ceiling"),
        failures)

    status_empty, _props_empty, _host_empty, adj_empty = (
        verdictlib.compose_adjudication(
            no_required,
            scored={"note": {"pass": True, "evidence": "bound-event:1"}},
            host_findings=[]))
    empty_ok = (
        status_empty == "INVALID"
        and adj_empty.get("product_status") == "INCOMPLETE"
        and adj_empty.get("property_evidence_complete") is False
        and adj_empty.get("all_required_properties_true") is None)
    if not empty_ok:
        failures.append("no-required-properties-is-incomplete")

    rescored = {
        "p1": {"pass": True, "evidence": "replay:1"},
        "p2": {"pass": True, "evidence": "replay:2"},
        "note": {"pass": True, "evidence": "replay:3"},
    }
    reporting.assert_replay_matches(good, rescored, FIXTURE)
    rescored["p2"]["pass"] = False
    must_refuse(
        "report-refuses-replay-mismatch",
        lambda: reporting.assert_replay_matches(good, rescored, FIXTURE),
        failures)

    if failures:
        print("REPORTING TESTS FAIL:", ", ".join(failures))
        return 1
    print("REPORTING TESTS OK: claims require complete reconstructible data.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
