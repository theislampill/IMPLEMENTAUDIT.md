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
