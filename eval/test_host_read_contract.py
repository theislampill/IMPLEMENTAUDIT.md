#!/usr/bin/env python3
"""Generated RED/GREEN corpus for the accepted host-read trust-state contract.

This is deterministic evaluator testing only.  It never launches a model and
never mutates campaign evidence.  Each accepted state ID reports separately so
missing implementation cannot hide unexecuted cases behind one import error.
"""
from __future__ import annotations

import json
import os
import re
import sys

import host_read_fixture_adapter


HERE = os.path.dirname(os.path.abspath(__file__))
LIB = os.path.join(HERE, "lib")
DATA = os.path.join(HERE, "testdata", "host-read-trust")
if LIB not in sys.path:
    sys.path.insert(0, LIB)


def _emit(value):
    sys.stdout.write(str(value) + "\n")


def _load_cases(selected=None):
    cases = []
    for name in sorted(os.listdir(DATA)):
        if not name.endswith(".json"):
            continue
        if selected and os.path.splitext(name)[0] not in selected:
            continue
        path = os.path.join(DATA, name)
        with open(path, encoding="utf-8") as fh:
            batch = json.load(fh)
        if not isinstance(batch, list):
            raise AssertionError(f"{name}: root must be a list")
        cases.extend(batch)
    return cases


def _get_path(value, path):
    if isinstance(value, dict) and path in value:
        return value[path]
    current = value
    parts = path.split(".")
    index = 0
    while index < len(parts):
        if isinstance(current, list):
            current = current[int(parts[index])]
            index += 1
            continue
        if not isinstance(current, dict):
            raise KeyError(path)
        matched = None
        for end in range(len(parts), index, -1):
            candidate = ".".join(parts[index:end])
            if candidate in current:
                matched = (candidate, end)
                break
        if matched is None:
            raise KeyError(path)
        current = current[matched[0]]
        index = matched[1]
    return current


def _project(result, select):
    return {name: _get_path(result, path) for name, path in select.items()}


def _execute(case):
    try:
        import hostread
    except ImportError as exc:
        raise AssertionError(f"hostread implementation absent: {exc}")
    operation = case.get("operation")
    select = case.get("select") or {}
    if "inputs" in case:
        return [_project(host_read_fixture_adapter.execute(
                    operation, value, hostread, DATA), select)
                for value in case["inputs"]]
    return _project(host_read_fixture_adapter.execute(
        operation, case["input"], hostread, DATA), select)


def _guard_no_case_coupling(cases):
    labels = {case["id"] for case in cases}
    for case in cases:
        if "scenario" in case or "kind" in case:
            raise AssertionError(
                f"{case['id']}: abstract scenario/kind fixture forbidden")
    for relative in ("lib/hostread.py", "hosts.py"):
        path = os.path.join(HERE, relative)
        if not os.path.isfile(path):
            continue
        text = open(path, encoding="utf-8").read()
        leaked = sorted(label for label in labels
                        if re.search(rf"(?<![A-Z0-9]){re.escape(label)}"
                                     rf"(?![A-Z0-9])", text))
        if leaked:
            raise AssertionError(
                f"production {relative} references fixture IDs: {leaked}")


def main(argv=None):
    selected = set((argv or sys.argv[1:])) or None
    cases = _load_cases(selected)
    ids = [case.get("id") for case in cases]
    if len(ids) != len(set(ids)):
        raise AssertionError("duplicate trust-state fixture id")
    _guard_no_case_coupling(cases)
    failures = []
    for case in cases:
        case_id = case.get("id", "<missing-id>")
        try:
            result = _execute(case)
            if result != case["expected"]:
                raise AssertionError(
                    f"expected {case['expected']!r}, got {result!r}")
        except Exception as exc:
            failures.append((case_id, f"{type(exc).__name__}: {exc}"))
            _emit(f"  [RED] T-{case_id}: {type(exc).__name__}: {exc}")
        else:
            _emit(f"  [OK] T-{case_id}")
    if failures:
        _emit(f"HOST-READ TRUST CONTRACT RED: {len(failures)}/{len(cases)} "
              "states failing")
        return 1
    _emit(f"HOST-READ TRUST CONTRACT GREEN: {len(cases)}/{len(cases)} states")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
