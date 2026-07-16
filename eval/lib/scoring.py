#!/usr/bin/env python3
"""Deterministic transcript scorer for the implementaudit eval harness (#9).

No model, no judgment: each fixture declares a scoring rule expressed as
grep/marker/order/diff predicates over a plain-text transcript plus a small
structured summary. Returns per-property PASS/FAIL with matched evidence.

A rule is a JSON object with a "kind" and parameters. Supported kinds:

  contains        {"pattern": <regex>}                          - regex present
  absent          {"pattern": <regex>}                          - regex absent
  order           {"first": <regex>, "then": <regex>}           - first precedes then
  before_marker   {"pattern": <regex>, "marker": <regex>}       - pattern appears before first marker
  no_diff         {"paths": [<glob>...]}                         - summary.changed_files disjoint from paths
  count_at_least  {"pattern": <regex>, "n": <int>}              - >= n non-overlapping matches
  all_of          {"rules": [<rule>...]}                        - conjunction
  any_of          {"rules": [<rule>...]}                        - disjunction

The transcript is the model/agent output text. `summary` is an optional dict a
runner may attach (e.g. {"changed_files": [...]}) derived mechanically from the
run's working tree; scoring never infers it from prose.
"""
from __future__ import annotations

import json
import re
import sys
from fnmatch import fnmatch


def _search(pattern, text):
    return re.search(pattern, text, re.IGNORECASE | re.MULTILINE)


def eval_rule(rule, transcript, summary):
    kind = rule.get("kind")
    if kind == "contains":
        m = _search(rule["pattern"], transcript)
        return (bool(m), m.group(0)[:80] if m else "")
    if kind == "absent":
        m = _search(rule["pattern"], transcript)
        return (m is None, "" if m is None else m.group(0)[:80])
    if kind == "order":
        a = _search(rule["first"], transcript)
        b = _search(rule["then"], transcript)
        ok = bool(a and b and a.start() < b.start())
        return (ok, f"first@{a.start() if a else '-'} then@{b.start() if b else '-'}")
    if kind == "before_marker":
        p = _search(rule["pattern"], transcript)
        mk = _search(rule["marker"], transcript)
        # PASS if pattern present and (no marker OR pattern precedes first marker)
        ok = bool(p) and (mk is None or p.start() < mk.start())
        return (ok, f"pattern@{p.start() if p else '-'} marker@{mk.start() if mk else '-'}")
    if kind == "no_diff":
        changed = (summary or {}).get("changed_files", [])
        globs = rule["paths"]
        hits = [f for f in changed if any(fnmatch(f, g) for g in globs)]
        return (len(hits) == 0, ",".join(hits[:5]))
    if kind == "count_at_least":
        matches = re.findall(rule["pattern"], transcript, re.IGNORECASE | re.MULTILINE)
        return (len(matches) >= rule["n"], f"{len(matches)}>={rule['n']}")
    if kind == "all_of":
        results = [eval_rule(r, transcript, summary) for r in rule["rules"]]
        ok = all(r[0] for r in results)
        return (ok, "; ".join(f"{'Y' if r[0] else 'N'}:{r[1]}" for r in results))
    if kind == "any_of":
        results = [eval_rule(r, transcript, summary) for r in rule["rules"]]
        ok = any(r[0] for r in results)
        return (ok, "; ".join(f"{'Y' if r[0] else 'N'}:{r[1]}" for r in results))
    raise ValueError(f"unknown rule kind: {kind!r}")


def score(fixture, transcript, summary=None):
    """Return {property_name: {"pass": bool, "evidence": str}} for each scored property."""
    out = {}
    for prop in fixture["properties"]:
        ok, ev = eval_rule(prop["rule"], transcript, summary or {})
        out[prop["name"]] = {"pass": ok, "evidence": ev, "describes": prop.get("describes", "")}
    return out


def overall(scored, fixture):
    """A fixture PASSES iff every property marked required=True passes."""
    required = {p["name"] for p in fixture["properties"] if p.get("required", True)}
    return all(scored[n]["pass"] for n in required)


def main(argv):
    if len(argv) < 3:
        print("usage: scoring.py <fixture.json> <transcript.txt> [summary.json]", file=sys.stderr)
        return 2
    fixture = json.load(open(argv[1], encoding="utf-8"))
    transcript = open(argv[2], encoding="utf-8").read()
    summary = json.load(open(argv[3], encoding="utf-8")) if len(argv) > 3 else {}
    scored = score(fixture, transcript, summary)
    result = {"fixture": fixture["id"], "properties": scored,
              "overall_pass": overall(scored, fixture)}
    print(json.dumps(result, indent=1))
    return 0 if result["overall_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
