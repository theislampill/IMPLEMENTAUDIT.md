#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
sensor="$repo_root/skills/implementaudit/scripts/subagent-provenance-sensor.py"
fixture="$repo_root/fixtures/child-agents/bounded-continuation/current-fresh-resume.json"
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

py=()
if command -v python >/dev/null 2>&1; then
  py=(python)
elif command -v py >/dev/null 2>&1; then
  py=(py -3)
elif command -v python3 >/dev/null 2>&1; then
  py=(python3)
else
  printf 'subagent-provenance-sensor.test: Python 3 is required\n' >&2
  exit 1
fi

if [ ! -f "$sensor" ]; then
  printf 'subagent-provenance-sensor.test: causal RED: bounded continuation sensor is absent\n' >&2
  exit 1
fi

"${py[@]}" - "$fixture" "$tmp/source.json" "$tmp/observation.json" <<'PY'
import json
import pathlib
import sys

case = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
for key, output in (("source", sys.argv[2]), ("observation", sys.argv[3])):
    pathlib.Path(output).write_text(
        json.dumps(case[key], sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
PY

build_output="$("${py[@]}" "$sensor" build --input "$tmp/source.json")"
"${py[@]}" - "$build_output" "$tmp/packet.json" <<'PY'
import json
import pathlib
import sys

value = json.loads(sys.argv[1])
if value["schema"] != "implementaudit.bounded-continuation-build.v1":
    raise SystemExit("build schema is not exact")
if value["measurement"]["token_estimator"] != "characters/4-ceiling":
    raise SystemExit("packet estimator is not declared")
if value["measurement"]["bytes"] <= 0 or value["measurement"]["estimated_tokens"] <= 0:
    raise SystemExit("packet measurement is absent")
pathlib.Path(sys.argv[2]).write_text(
    json.dumps(value["packet"], sort_keys=True, separators=(",", ":")) + "\n",
    encoding="utf-8",
)
PY

classification="$("${py[@]}" "$sensor" classify \
  --packet "$tmp/packet.json" --observation "$tmp/observation.json")"
"${py[@]}" - "$classification" "$fixture" <<'PY'
import json
import sys

value = json.loads(sys.argv[1])
case = json.loads(open(sys.argv[2], encoding="utf-8").read())
source = case["source"]
if value["classifier"] != case["expected_classifier"]:
    raise SystemExit(f"fresh worker classified as {value['classifier']!r}")
if value["recovered"]["controller"] != source["controller"]:
    raise SystemExit("controller/claim/receipt were not recovered exactly")
if value["recovered"]["target"] != source["target"]:
    raise SystemExit("repo/cell/base/head/tree were not recovered exactly")
if value["recovered"]["graph"] != source["graph"]:
    raise SystemExit("graph state/dependencies/holds were not recovered exactly")
if value["recovered"]["next_action"] != source["continuation"]["next_action"]:
    raise SystemExit("next action was not recovered")
if value["history_query"] is not None or value["contradictions"]:
    raise SystemExit("current fresh resume invented a query or contradiction")
if value["authority_ceiling"] != "PARENT_GOVERNOR_ADJUDICATION_REQUIRED":
    raise SystemExit("sensor claimed authority")
if value["establishes"]:
    raise SystemExit("sensor established a lifecycle or result fact")
PY

"${py[@]}" - "$sensor" "$repo_root/fixtures/child-agents/bounded-continuation" "$tmp" <<'PY'
import copy
import hashlib
import json
import os
import pathlib
import subprocess
import sys

SENSOR = pathlib.Path(sys.argv[1])
FIXTURES = pathlib.Path(sys.argv[2])
TMP = pathlib.Path(sys.argv[3])
PYTHON = sys.executable
BASE = json.loads((FIXTURES / "current-fresh-resume.json").read_text(encoding="utf-8"))


def load(name):
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def merge(target, patch):
    for key, value in patch.items():
        if isinstance(value, dict) and isinstance(target.get(key), dict):
            merge(target[key], value)
        else:
            target[key] = copy.deepcopy(value)


def set_path(target, dotted, value):
    parts = dotted.split(".")
    for part in parts[:-1]:
        target = target[int(part)] if isinstance(target, list) else target[part]
    final = int(parts[-1]) if isinstance(target, list) else parts[-1]
    target[final] = copy.deepcopy(value)


def canonical_bytes(value):
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def refresh_history_identity(row):
    row["payload_digest"] = hashlib.sha256(canonical_bytes(row["payload"])).hexdigest()
    unsigned = dict(row)
    unsigned.pop("event_id", None)
    row["event_id"] = "iaevt-v1-" + hashlib.sha256(canonical_bytes(unsigned)).hexdigest()


def write(name, value):
    path = TMP / name
    path.write_text(json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    return path


def invoke(*args, env=None, ok=True):
    result = subprocess.run(
        [PYTHON, os.fspath(SENSOR), *map(os.fspath, args)],
        text=True,
        capture_output=True,
        env=env,
        check=False,
    )
    if ok and result.returncode != 0:
        raise SystemExit(f"unexpected CLI failure {result.returncode}: {result.stderr}")
    if not ok and result.returncode == 0:
        raise SystemExit(f"unexpected CLI success: {result.stdout}")
    raw = result.stdout if ok else result.stderr
    return json.loads(raw)


def build(source=None, tag="case", env=None):
    output = invoke("build", "--input", write(f"{tag}-source.json", source or BASE["source"]), env=env)
    packet = output["packet"]
    measurement = output["measurement"]
    raw = json.dumps(packet, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    if measurement["bytes"] != len(raw.encode("utf-8")):
        raise SystemExit("packet byte measurement is not exact")
    if measurement["characters"] != len(raw):
        raise SystemExit("packet character measurement is not exact")
    if measurement["estimated_tokens"] != (len(raw) + 3) // 4:
        raise SystemExit("four-character estimator is not ceiling-rounded")
    allowed = {
        "schema", "controller", "target", "graph", "authority", "process",
        "evidence", "continuation", "packet_digest",
    }
    if set(packet) != allowed:
        raise SystemExit("packet retained unrelated or undeclared fields")
    return packet


def classify(packet, observation=None, tag="case", ok=True):
    return invoke(
        "classify", "--packet", write(f"{tag}-packet.json", packet),
        "--observation", write(f"{tag}-observation.json", observation or BASE["observation"]),
        ok=ok,
    )


def assert_classification(value, classifier, contradiction=None):
    if value["classifier"] != classifier:
        raise SystemExit(f"expected {classifier}, got {value['classifier']}")
    if contradiction is not None and contradiction not in value["contradictions"]:
        raise SystemExit(f"missing contradiction {contradiction}: {value}")
    if value["authority_ceiling"] != "PARENT_GOVERNOR_ADJUDICATION_REQUIRED" or value["establishes"]:
        raise SystemExit("classifier crossed its authority ceiling")


# H6-R0002: packet tampering fails before a classifier is returned.
packet = build(tag="tamper")
packet["continuation"]["next_action"] = "tampered"
error = classify(packet, tag="tamper", ok=False)
if error["code"] != "CONTINUATION_PACKET_DIGEST_MISMATCH":
    raise SystemExit(f"tamper returned {error}")

# H6-R0003/R000A: stale continuity and pending effects wait for the governor.
for name in ("stale-receipt.json", "report-and-wait-active-effect.json"):
    case = load(name)
    observation = copy.deepcopy(BASE["observation"])
    merge(observation, case["observation_patch"])
    value = classify(build(tag=name), observation, tag=name)
    assert_classification(value, case["expected_classifier"], case["expected_contradiction"])

# H6-R0004/R000F: every foreign target and graph/writer change is rejected independently.
for name in ("foreign-controller-claim-run.json", "worktree-head-tree-mismatch.json"):
    case = load(name)
    for index, mutation in enumerate(case["cases"]):
        observation = copy.deepcopy(BASE["observation"])
        set_path(observation, mutation["path"], mutation["value"])
        value = classify(build(tag=f"{name}-{index}"), observation, tag=f"{name}-{index}")
        assert_classification(value, case["expected_classifier"], case["expected_contradiction"])
case = load("graph-digest-mismatch.json")
observation = copy.deepcopy(BASE["observation"]); merge(observation, case["observation_patch"])
assert_classification(
    classify(build(tag="graph-digest"), observation, tag="graph-digest"),
    case["expected_classifier"], case["expected_contradiction"],
)
observation = copy.deepcopy(BASE["observation"])
observation["graph"]["writer_holds"] = ["W_FOREIGN"]
assert_classification(
    classify(build(tag="writer-drift"), observation, tag="writer-drift"),
    "REPORT_AND_WAIT", "GRAPH_PROJECTION_MISMATCH",
)

# H6-R0005/R0006: exactly one evidence ID yields one normalized bounded query.
case = load("query-history-then-resume.json")
source = copy.deepcopy(BASE["source"])
source["evidence"]["unresolved_evidence_id"] = case["evidence_id"]
packet = build(source, "query")
value = classify(packet, tag="query-missing")
assert_classification(value, case["expected_classifier_without_result"])
if value["history_query"] != {
    "schema": "implementaudit.history-query-request.v1",
    "route": "QUERY_HISTORY_THEN_RESUME",
    "requirement": "REQUIRED",
    "evidence_ids": [case["evidence_id"]],
}:
    raise SystemExit("history query is not the exact one-ID R0038 contract")
observation = copy.deepcopy(BASE["observation"])
observation["query_result"] = case["usable_query_result"]
value = classify(packet, observation, "query-good")
assert_classification(value, case["expected_classifier_with_result"])
for index, mutation in enumerate(case["invalid_result_mutations"]):
    observation = copy.deepcopy(BASE["observation"])
    observation["query_result"] = copy.deepcopy(case["usable_query_result"])
    set_path(observation["query_result"], mutation["path"], mutation["value"])
    value = classify(packet, observation, f"query-bad-{index}")
    assert_classification(value, "REPORT_AND_WAIT", "HISTORY_QUERY_RESULT_NOT_DECISION_USABLE")

# H6-R06A: row length is not history-event integrity. Decision-bearing
# substitution must fail with stale payload/event identity even after row_bytes
# is recomputed.
observation = copy.deepcopy(BASE["observation"])
observation["query_result"] = copy.deepcopy(case["usable_query_result"])
row = observation["query_result"]["rows"][0]
row["payload"]["resolution"] = "substituted decision"
observation["query_result"]["row_bytes"] = len(canonical_bytes(row))
value = classify(packet, observation, "query-substituted-row")
assert_classification(
    value, "REPORT_AND_WAIT", "HISTORY_QUERY_RESULT_NOT_DECISION_USABLE",
)

# Recomputing independently supplied payload/event digests changes the event
# identity and still cannot satisfy the one-ID request/coverage fence.
observation = copy.deepcopy(BASE["observation"])
observation["query_result"] = copy.deepcopy(case["usable_query_result"])
row = observation["query_result"]["rows"][0]
row["payload"]["resolution"] = "substituted decision"
refresh_history_identity(row)
observation["query_result"]["row_bytes"] = len(canonical_bytes(row))
value = classify(packet, observation, "query-redigested-substitution")
assert_classification(
    value, "REPORT_AND_WAIT", "HISTORY_QUERY_RESULT_NOT_DECISION_USABLE",
)

# H6-R0007/R000E: unrelated growth is not input, and narrative/frontier keys fail closed.
case = load("unrelated-history.json")
history = TMP / "unrelated-history.json"
digests = []
for count in case["unrelated_history_counts"]:
    history.write_text(json.dumps([{"id": index} for index in range(count)]), encoding="utf-8")
    env = dict(os.environ); env["IMPLEMENTAUDIT_UNRELATED_HISTORY"] = os.fspath(history)
    digests.append(build(tag=f"history-{count}", env=env)["packet_digest"])
if len(set(digests)) != 1:
    raise SystemExit("packet changed with unrelated history growth")
for key in case["forbidden_observation_keys"]:
    observation = copy.deepcopy(BASE["observation"]); observation[key] = {"untrusted": True}
    error = classify(build(tag=f"forbidden-{key}"), observation, f"forbidden-{key}", ok=False)
    if error["code"] != "CONTINUATION_SCHEMA_INVALID":
        raise SystemExit(f"forbidden narrative key {key} returned {error}")
oversized = copy.deepcopy(BASE["source"])
oversized["continuation"]["next_action"] = "x" * case["max_packet_bytes"]
error = invoke("build", "--input", write("oversized-source.json", oversized), ok=False)
if error["code"] != "CONTINUATION_BOUND_EXCEEDED":
    raise SystemExit(f"oversized packet returned {error}")

# H6-R07A: classify applies the same canonical bound to a correctly
# re-digested packet that bypasses build.
oversized_packet = build(tag="oversized-classify")
oversized_packet["continuation"]["next_action"] = "x" * (case["max_packet_bytes"] + 8192)
unsigned = dict(oversized_packet)
unsigned.pop("packet_digest")
oversized_packet["packet_digest"] = hashlib.sha256(canonical_bytes(unsigned)).hexdigest()
if len(canonical_bytes(oversized_packet)) <= case["max_packet_bytes"]:
    raise SystemExit("oversized classify control did not cross the packet bound")
error = classify(oversized_packet, tag="oversized-classify", ok=False)
if error["code"] != "CONTINUATION_BOUND_EXCEEDED":
    raise SystemExit(f"oversized classify packet returned {error}")

# H6-R0008/R0009: consumed steers remain consumed; a distinct admitted event is new once.
case = load("reconstructed-consumed-owner-event.json")
value = classify(build(tag="consumed"), tag="consumed")
assert_classification(value, case["expected_classifier"])
if value["instruction_events"] != {
    "consumed": case["expected_consumed"], "admitted": case["expected_admitted"]}:
    raise SystemExit("consumed owner steer was reissued")
case = load("distinct-new-owner-event.json")
observation = copy.deepcopy(BASE["observation"])
observation["instruction_events"].append(case["new_event"])
value = classify(build(tag="new-event"), observation, "new-event")
assert_classification(value, case["expected_classifier"])
if value["instruction_events"]["admitted"] != case["expected_admitted"]:
    raise SystemExit("distinct new owner event was discarded")

# H6-R000B: same context is allowed only for verified interrupted cognition with headroom.
case = load("same-context-resume.json")
observation = copy.deepcopy(BASE["observation"]); merge(observation, case["observation_patch"])
assert_classification(classify(build(tag="same"), observation, "same"), case["expected_classifier"])
observation["receiver"]["headroom_sufficient"] = False
assert_classification(
    classify(build(tag="same-no-headroom"), observation, "same-no-headroom"),
    "REPORT_AND_WAIT", "SAME_CONTEXT_NOT_RESUMABLE",
)

# H6-R000C: host start/stop observations retain distinct states and establish nothing.
case = load("subagent-terminal-states.json")
observation = copy.deepcopy(BASE["observation"])
observation["subagent_observations"] = case["subagent_observations"]
value = classify(build(tag="subagents"), observation, "subagents")
assert_classification(value, case["expected_classifier"])
if value["subagent_observations"] != case["subagent_observations"]:
    raise SystemExit("subagent terminal observations were collapsed")

# H6-R000D: ActiveGraph is optional and cannot override WORK_GRAPH.
case = load("activegraph-contradiction.json")
observation = copy.deepcopy(BASE["observation"]); observation["activegraph"] = case["activegraph"]
value = classify(build(tag="activegraph"), observation, "activegraph")
assert_classification(value, case["expected_classifier"], case["expected_contradiction"])
if value["recovered"]["graph"]["state"] != "ACTIVE":
    raise SystemExit("ActiveGraph overrode authoritative WORK_GRAPH state")
observation = copy.deepcopy(BASE["observation"])
observation["activegraph"] = case["same_state_different_digest"]
value = classify(build(tag="activegraph-digest"), observation, "activegraph-digest")
assert_classification(value, case["expected_classifier"], case["expected_contradiction"])
PY

printf 'FRESH_WORKER_BOUNDED_RESUME_TEST=PASS\n'
