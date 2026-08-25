#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

fail() {
  printf 'operational-evidence-contract.test: %s\n' "$*" >&2
  exit 1
}

if command -v python >/dev/null 2>&1; then
  py_cmd=(python)
elif command -v python3 >/dev/null 2>&1; then
  py_cmd=(python3)
elif command -v py >/dev/null 2>&1; then
  py_cmd=(py -3)
else
  fail "python, python3, or py -3 is required"
fi

loader="skills/implementaudit/scripts/operational-evidence.py"
rotation_loader="skills/implementaudit/scripts/rotate-canonical-state.py"
fixtures="fixtures/operational-evidence"
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

run_query_contract() {
"${py_cmd[@]}" - "$loader" "$rotation_loader" \
  "$fixtures/query-cases.json" \
  "fixtures/canonical-state-rotation/query-cursor-cases.json" <<'PY'
import base64
import copy
import hashlib
import importlib.util
import json
import pathlib
import sys


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


evidence = load("operational_evidence_query", sys.argv[1])
rotation = load("rotation_query", sys.argv[2])
cases = json.loads(pathlib.Path(sys.argv[3]).read_text(encoding="utf-8"))
frozen = json.loads(pathlib.Path(sys.argv[4]).read_text(encoding="utf-8"))
families = ["CODE", "OWNERSHIP", "EXECUTION", "EVIDENCE", "FAILURE", "RELEASE"]

if cases != {
        "schema": "implementaudit.operational-evidence-query-cases.v1",
        "causal_cases": [f"C07-R{i:02d}" for i in range(1, 19)],
        "held_out_cases": [f"C07-H{i:02d}" for i in range(1, 5)],
        "families": families,
        "cursor_cases": frozen["cases"],
    }:
    raise SystemExit("C07 query fixture does not bind the frozen matrix")

required_functions = {
    "evaluate_currentness", "query_family", "normalize_history_filters_v1",
    "encode_query_cursor_v1", "decode_query_cursor_v1", "query_history_v1",
    "explain_history_why_v1", "build_cli_parser_v1",
}
missing = sorted(name for name in required_functions if not hasattr(evidence, name))
if missing:
    raise SystemExit(f"C07-R01 status/query/why interfaces are absent: {missing}")

schema = json.loads(pathlib.Path(
    "skills/implementaudit/references/operational-evidence-schema.json"
).read_text(encoding="utf-8"))
if schema.get("x-bounded-history-query") != {
        "schema": "implementaudit.operational-evidence-query.v1",
        "cursor_schema": "implementaudit.history-query-cursor.v1",
        "history_contract": "implementaudit.history-query.v1",
        "authority_ceiling": "READ_ONLY_OBSERVATION",
        "cursor_integrity": "sha256_checksum_not_authentication",
        "cursor_pages": "never_decision_usable",
        "decision_page": "untruncated_first_page_from_filter_start_only",
        "overflow": "OE_QUERY_REQUIRES_BOUNDED_REVIEW",
        "history_discovery": "verified_current_pointer_manifest_predecessor_chain_only",
        "activegraph_authority": False,
        "publication": False,
    }:
    raise SystemExit("C07 query schema contract is absent or widened")


def currentness(state="CURRENT", invalidators=None):
    return {"state": state, "invalidators": list(invalidators or [])}


def record(identifier, family, state="CURRENT", invalidators=None, **extra):
    return {
        "id": identifier,
        "family": family,
        "native_owner_identity": f"owner:{family.lower()}",
        "source_identity": {"id": f"source:{identifier}", "layer": "evidence"},
        "evidence_layer": "evidence",
        "currentness": currentness(state, invalidators),
        **extra,
    }


records = [
    record("code", "CODE", record_type="File", required=True,
           capability="tracked-file"),
    record("owner", "OWNERSHIP", record_type="Writer", required=True,
           capability="semantic-owner"),
    record("execution", "EXECUTION", record_type="Run", required=True,
           capability="bounded-run"),
    record("evidence", "EVIDENCE", record_type="Evidence", required=True,
           capability="claim-leg", contrary_evidence=["contrary-open"]),
    record("failure", "FAILURE", record_type="Andon", required=True,
           capability="supported-cause"),
    record("release", "RELEASE", record_type="Release", required=True,
           capability="public-readback"),
    record("stale-evidence", "EVIDENCE", "STALE", ["receipt-drift"],
           record_type="Evidence", required=False, capability="historical-only"),
]
relations = [
    record("rel-evidence-criterion", "EVIDENCE", relation_type="EVIDENCES",
           source_entity_id="evidence", target_entity_id="failure",
           confidence="mechanical", inference_rule=None),
    record("rel-failure-release", "FAILURE", relation_type="BLOCKS",
           source_entity_id="failure", target_entity_id="release",
           confidence="declared", inference_rule=None),
]
snapshot = {
    "schema_version": "implementaudit-operational-snapshot-payload.v1",
    "snapshot_id": "iasnap-v1-" + "a" * 64,
    "aggregate": "DEGRADED",
    "families": families,
    "missing_or_omitted_state": [{"kind": "OWNER_FACT_NON_CURRENT",
                                   "family": "EVIDENCE", "state": "STALE"}],
    "collections": {
        "fixture": {"owner": "R0038-test", "state": "CURRENT",
                    "value": {"records": records, "relations": relations}},
    },
    "input_manifest_sha256": "a" * 64,
}

status = evidence.evaluate_currentness(snapshot)
if (status["schema"] != "implementaudit.operational-evidence-status.v1" or
        status["aggregate"] != "DEGRADED" or
        status["family_state_census"]["EVIDENCE"] != {"CURRENT": 2, "STALE": 1} or
        status["authority_ceiling"] != "READ_ONLY_OBSERVATION" or
        status["establishes"]):
    raise SystemExit("C07-R02/R05 status lost six-family currentness or authority")

current_view = evidence.query_family(snapshot, "EVIDENCE", current_only=True)
if ([row["record"]["id"] for row in current_view["rows"]] != [
        "evidence", "rel-evidence-criterion"] or
        current_view["omitted_state_census"] != {"STALE": 1}):
    raise SystemExit("C07-R03 CURRENT-only view hid its omitted-state census")
all_view = evidence.query_family(snapshot, "EVIDENCE")
if len(all_view["rows"]) != 3 or not any(
        row["record"]["currentness"]["invalidators"] == ["receipt-drift"]
        for row in all_view["rows"]):
    raise SystemExit("C07-R05 query normalized a non-current fact to success")

permuted = copy.deepcopy(snapshot)
permuted["collections"]["fixture"]["value"]["records"].reverse()
permuted["collections"]["fixture"]["value"]["relations"].reverse()
if evidence.canonical_json_v1(evidence.query_family(snapshot, "EVIDENCE")) != \
        evidence.canonical_json_v1(evidence.query_family(permuted, "EVIDENCE")):
    raise SystemExit("C07-R04 query bytes depend on input ordering")

why = evidence.explain_history_why_v1(snapshot, "evidence")
if ([row["id"] for row in why["chain"]] != ["evidence", "failure", "release"] or
        why["contrary_evidence"] != ["contrary-open"]):
    raise SystemExit("C07-R06 why chain is not deterministic or lost contrary evidence")
missing_why = evidence.explain_history_why_v1(snapshot, "absent")
if missing_why["status"] != "UNKNOWN" or missing_why["chain"]:
    raise SystemExit("C07-R06 missing why edge invented a cause")
cyclic = copy.deepcopy(snapshot)
cyclic["collections"]["fixture"]["value"]["relations"].append(
    record("rel-release-evidence", "RELEASE", relation_type="DEPENDS_ON",
           source_entity_id="release", target_entity_id="evidence",
           confidence="declared", inference_rule=None))
try:
    evidence.explain_history_why_v1(cyclic, "evidence")
except evidence.OperationalEvidenceError as exc:
    if exc.code != "OE_WHY_CYCLE":
        raise SystemExit(f"C07-R06 wrong why-cycle discriminator: {exc.code}")
else:
    raise SystemExit("C07-R06 malformed why cycle was accepted")


def source_locator():
    return {
        "kind": "run-root-relative", "root_identity": "sha256:" + "b" * 64,
        "path": "operational-evidence/snapshots/iasnap-v1-" + "a" * 64 +
                "/snapshot.json", "host_identity": None,
    }


def event(sequence, generation, kind, subject, status="CLOSED"):
    value = {
        "schema_version": "implementaudit.history-event.v1",
        "run_id": "run-query", "controller_id": "controller-query",
        "generation_id": generation, "sequence": f"{sequence:020d}",
        "record_kind": kind, "subject_id": subject,
        "source_epoch": generation, "transition": "APPENDED", "status": status,
        "supersedes_event_id": None, "payload": {"subject": subject},
        "source_evidence_id": "iasrc-v1-r0038-snapshot-" + "a" * 64,
        "source_locator": source_locator(), "source_digest": "sha256:" + "c" * 64,
    }
    value["payload_digest"] = hashlib.sha256(
        rotation.canonical_json_v1(value["payload"])).hexdigest()
    value["event_id"] = "iaevt-v1-" + hashlib.sha256(
        rotation.canonical_json_v1(value)).hexdigest()
    rotation.validate_event_output_v1(value)
    return value


def manifest(generation, events, predecessor=None):
    before = predecessor["high_water"] if predecessor else "00000000000000000000"
    predecessor_digest = predecessor["manifest_digest"] if predecessor else None
    rows = [{
        "sequence": value["sequence"], "event_id": value["event_id"],
        "segment_digest": "sha256:" + hashlib.sha256(
            rotation.canonical_json_v1(value)).hexdigest(),
        "record_kind": value["record_kind"],
        "source_evidence_id": value["source_evidence_id"],
    } for value in events]
    counts = {}
    for row in rows:
        counts[row["record_kind"]] = counts.get(row["record_kind"], 0) + 1
    value = {
        "schema_version": "implementaudit.state-generation-manifest.v1",
        "query_contract_version": "implementaudit.history-query.v1",
        "controller_id": "controller-query", "claim_id": "d" * 32,
        "run_id": "run-query", "generation_id": generation,
        "source_epoch": generation,
        "predecessor_manifest_digest": predecessor_digest,
        "predecessor_high_water": before, "events": rows,
        "record_class_counts": dict(sorted(counts.items())),
        "population_digest": hashlib.sha256(rotation.canonical_json_v1([
            {key: row[key] for key in rotation.MANIFEST_EVENT_KEYS} for row in rows
        ])).hexdigest(),
        "high_water": rows[-1]["sequence"],
    }
    value["manifest_digest"] = hashlib.sha256(
        rotation.canonical_json_v1(value)).hexdigest()
    rotation.verify_generation_manifest_v1(value)
    return value


old_events = [
    event(1, "G0001", "finding.closed", "finding-old"),
    event(2, "G0001", "andon.closed", "andon-old"),
]
old_manifest = manifest("G0001", old_events)
new_events = [
    event(3, "G0002", "finding.closed", "finding-new"),
    event(4, "G0002", "transition.closed", "transition-new"),
]
new_manifest = manifest("G0002", new_events, old_manifest)
events_by_id = {row["event_id"]: row for row in old_events + new_events}
manifests = {old_manifest["manifest_digest"]: old_manifest}
loaded = []

rejected_by_r39 = {
    "schema_version": "implementaudit.state-generation-manifest.v1",
    "query_contract_version": "implementaudit.history-query.v1",
    "generation_id": "G0002", "events": [],
}
rejected_by_r39["manifest_digest"] = hashlib.sha256(
    rotation.canonical_json_v1(rejected_by_r39)).hexdigest()
try:
    rotation.verify_generation_manifest_v1(rejected_by_r39)
except rotation.RotationError:
    pass
else:
    raise SystemExit("C07-C01 discriminator is not rejected by canonical R39")
try:
    evidence.query_history_v1(
        {"schema": "implementaudit.operational-evidence-query.v1",
         "filters": {"event_ids": [new_events[0]["event_id"]]},
         "max_rows": 10, "max_bytes": 65536},
        rejected_by_r39,
        load_segment=lambda *_args: (_ for _ in ()).throw(
            AssertionError("invalid manifest traversed a segment")),
        load_predecessor=lambda *_args: (_ for _ in ()).throw(
            AssertionError("invalid manifest traversed a predecessor")))
except evidence.OperationalEvidenceError as exc:
    if exc.code != "OE_QUERY_MANIFEST_INVALID":
        raise SystemExit(f"C07-C01 wrong manifest refusal {exc.code}")
else:
    raise SystemExit(
        "C07-C01 unverified self-digested manifest produced an OK absence")

manifest_oid = "1" * 40
pointer_oid = "2" * 40
marker_oid = "3" * 40
pointer, _pointer_raw = rotation.build_generation_pointer_v1(
    controller_id=new_manifest["controller_id"],
    claim_id=new_manifest["claim_id"], run_id=new_manifest["run_id"],
    generation_id=new_manifest["generation_id"], source_epoch=new_manifest["source_epoch"],
    predecessor_pointer_oid=None, predecessor_pointer_digest=None,
    generation_manifest_oid=manifest_oid,
    generation_manifest_digest=new_manifest["manifest_digest"],
    cold_high_water=new_manifest["high_water"], hot_state_digest="4" * 64,
    hot_roadmap_digest="5" * 64, work_graph_path="WORK_GRAPH.json",
    work_graph_digest="6" * 64, degraded_state="NONE")
live_selection = {
    "repo_path": pathlib.Path("fixture-repository"),
    "pointer_oid": pointer_oid, "marker_oid": marker_oid,
    "receipt": {"fixture": "current-v3"},
}
selection_calls = []
original_selection_functions = {
    name: getattr(rotation, name) for name in (
        "load_governed_source_custody_v1",
        "load_canonical_generation_pointer_oid_v1",
        "load_canonical_generation_manifest_oid_v1",
        "verify_pointer_manifest_tuple_v1",
        "require_complete_pointer_receipt_marker_route_v1")
}
rotation.load_governed_source_custody_v1 = lambda: (
    selection_calls.append("CURRENT") or live_selection)
rotation.load_canonical_generation_pointer_oid_v1 = lambda repo, oid: (
    selection_calls.append(("POINTER", repo, oid)) or pointer)
rotation.load_canonical_generation_manifest_oid_v1 = lambda repo, oid: (
    selection_calls.append(("MANIFEST", repo, oid)) or new_manifest)


def verify_tuple_spy(**kwargs):
    selection_calls.append("TUPLE")
    return original_selection_functions["verify_pointer_manifest_tuple_v1"](
        **kwargs)


rotation.verify_pointer_manifest_tuple_v1 = verify_tuple_spy
rotation.require_complete_pointer_receipt_marker_route_v1 = lambda **kwargs: (
    selection_calls.append(("ROUTE", kwargs)) or None)
try:
    if evidence._require_r39_current_manifest_v1(
            rotation, new_manifest) != new_manifest:
        raise SystemExit("C07-C01 exact-current positive returned foreign manifest")
finally:
    for name, function in original_selection_functions.items():
        setattr(rotation, name, function)
if (selection_calls[:4] != [
        "CURRENT", ("POINTER", pathlib.Path("fixture-repository"), pointer_oid),
        ("MANIFEST", pathlib.Path("fixture-repository"), manifest_oid), "TUPLE"] or
        len(selection_calls) != 5 or selection_calls[4][0] != "ROUTE"):
    raise SystemExit("C07-C01 exact-current positive skipped a canonical R39 binding leg")

selected_current = [new_manifest]


def require_fixture_current(_r39, expected):
    if evidence.canonical_json_v1(expected) != evidence.canonical_json_v1(
            selected_current[0]):
        raise evidence.OperationalEvidenceError(
            "OE_QUERY_CURRENT_MANIFEST_INVALID", "$query.current_manifest",
            "fixture manifest is not selected current")
    return selected_current[0]


evidence._require_r39_current_manifest_v1 = require_fixture_current

selected_current[0] = old_manifest
try:
    evidence.query_history_v1(
        {"schema": "implementaudit.operational-evidence-query.v1",
         "filters": {"event_ids": [new_events[0]["event_id"]]},
         "max_rows": 10, "max_bytes": 65536},
        new_manifest,
        load_segment=lambda *_args: (_ for _ in ()).throw(
            AssertionError("stale current selection traversed a segment")),
        load_predecessor=lambda *_args: (_ for _ in ()).throw(
            AssertionError("stale current selection traversed a predecessor")))
except evidence.OperationalEvidenceError as exc:
    if exc.code != "OE_QUERY_CURRENT_MANIFEST_INVALID":
        raise SystemExit(f"C07-C01 wrong stale-current refusal {exc.code}")
else:
    raise SystemExit("C07-C01 structurally valid stale manifest became decision-usable")
finally:
    selected_current[0] = new_manifest


def load_predecessor(digest):
    return manifests[digest]


def load_segment(_manifest, row):
    loaded.append(row["event_id"])
    return rotation.canonical_json_v1(events_by_id[row["event_id"]])


def request(filters, rows=10, size=65536):
    return {"schema": "implementaudit.operational-evidence-query.v1",
            "filters": filters, "max_rows": rows, "max_bytes": size}


target = new_events[0]["event_id"]
exact_request = request({"event_ids": [target]})
result = evidence.query_history_v1(
    exact_request, new_manifest, load_segment=load_segment,
    load_predecessor=load_predecessor)
if ([row["event_id"] for row in result["rows"]] != [target] or
        loaded != [target] or not result["decision_usable"] or result["truncated"] or
        result["authority_ceiling"] != "READ_ONLY_OBSERVATION" or
        result["establishes"]):
    raise SystemExit("C07-R12/R15 exact query hydrated unrelated history or gained authority")

current_observations = []


def require_stable_current(_r39, expected):
    current_observations.append("CURRENT")
    if len(current_observations) == 2:
        raise evidence.OperationalEvidenceError(
            "OE_QUERY_CURRENT_MANIFEST_INVALID", "$query.current_manifest",
            "fixture selection changed during query")
    return expected


evidence._require_r39_current_manifest_v1 = require_stable_current
try:
    evidence.query_history_v1(
        exact_request, new_manifest, load_segment=load_segment,
        load_predecessor=load_predecessor)
except evidence.OperationalEvidenceError as exc:
    if exc.code != "OE_QUERY_CURRENT_MANIFEST_INVALID":
        raise SystemExit(f"C07-C01 wrong final-current fence refusal {exc.code}")
else:
    raise SystemExit("C07-C01 current selection drift escaped final fence")
finally:
    evidence._require_r39_current_manifest_v1 = require_fixture_current


def corrupt_referenced_segment(manifest_value, row):
    if row["event_id"] == target:
        return b"{}"
    raise SystemExit("C07-R13 exact query attempted to hydrate unrelated history")


try:
    evidence.query_history_v1(
        exact_request, new_manifest, load_segment=corrupt_referenced_segment,
        load_predecessor=load_predecessor)
except evidence.OperationalEvidenceError as exc:
    if exc.code != "OE_QUERY_SEGMENT_INVALID":
        raise SystemExit(f"C07-R13 referenced corruption returned {exc.code}")
else:
    raise SystemExit("C07-R13 referenced corrupt segment was accepted")

foreign_old = copy.deepcopy(old_manifest)
foreign_old["run_id"] = "foreign-run"
foreign_old["manifest_digest"] = hashlib.sha256(rotation.canonical_json_v1({
    key: value for key, value in foreign_old.items() if key != "manifest_digest"
})).hexdigest()
foreign_current = copy.deepcopy(new_manifest)
foreign_current["predecessor_manifest_digest"] = foreign_old["manifest_digest"]
foreign_current["manifest_digest"] = hashlib.sha256(rotation.canonical_json_v1({
    key: value for key, value in foreign_current.items()
    if key != "manifest_digest"
})).hexdigest()
selected_current[0] = foreign_current
try:
    evidence.query_history_v1(
        exact_request, foreign_current, load_segment=load_segment,
        load_predecessor=lambda _digest: foreign_old)
except evidence.OperationalEvidenceError as exc:
    if exc.code != "OE_QUERY_MANIFEST_INVALID":
        raise SystemExit(f"C07-R13 foreign predecessor returned {exc.code}")
else:
    raise SystemExit("C07-R13 foreign predecessor custody was accepted")
finally:
    selected_current[0] = new_manifest

for filters in ({}, {"event_ids": []}, {"event_ids": [True]},
                {"not_a_filter": [target]}):
    try:
        evidence.normalize_history_filters_v1(filters)
    except evidence.OperationalEvidenceError as exc:
        if exc.code != "OE_QUERY_FILTER_INVALID":
            raise SystemExit(f"C07-R07 wrong filter discriminator: {exc.code}")
    else:
        raise SystemExit("C07-R07 empty/malformed filter was accepted")
for bad in (0, -1, True, 1.5):
    try:
        evidence.query_history_v1(
            request({"event_ids": [target]}, rows=bad), new_manifest,
            load_segment=load_segment, load_predecessor=load_predecessor)
    except evidence.OperationalEvidenceError as exc:
        if exc.code != "OE_QUERY_BOUND_INVALID":
            raise SystemExit(f"C07-R07 wrong bound discriminator: {exc.code}")
    else:
        raise SystemExit("C07-R07 non-positive/non-integer bound was accepted")

position = {"sequence": old_events[1]["sequence"],
            "event_id": old_events[1]["event_id"]}
cursor = evidence.encode_query_cursor_v1(exact_request, new_manifest, position)
decoded = evidence.decode_query_cursor_v1(cursor, exact_request, new_manifest)
if decoded["requested_position"] != position:
    raise SystemExit("QC01 valid cursor did not round-trip")


def decode_cursor(token):
    encoded = token.split(".")[1]
    encoded += "=" * (-len(encoded) % 4)
    return json.loads(base64.urlsafe_b64decode(encoded).decode("utf-8"))


def encode_cursor(value):
    raw = evidence.canonical_json_v1(value)
    payload = base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")
    return "iaqcur-v1." + payload + "." + hashlib.sha256(raw).hexdigest()


def expect_cursor_failure(case_id, token, expected_code, req=exact_request,
                          current_manifest=new_manifest):
    try:
        evidence.decode_query_cursor_v1(token, req, current_manifest)
    except evidence.OperationalEvidenceError as exc:
        if exc.code != expected_code:
            raise SystemExit(f"{case_id} expected {expected_code}, got {exc.code}")
    else:
        raise SystemExit(f"{case_id} cursor was accepted")


mutated = decode_cursor(cursor)
mutated["schema"] = "implementaudit.history-query-cursor.v2"
expect_cursor_failure("QC02", encode_cursor(mutated), "OE_QUERY_CURSOR_VERSION_MISMATCH")
mutated = decode_cursor(cursor); mutated["generation_id"] = "G0001"
expect_cursor_failure("QC03", encode_cursor(mutated), "OE_QUERY_CURSOR_GENERATION_MISMATCH")
mutated = decode_cursor(cursor); mutated["manifest_digest"] = "e" * 64
expect_cursor_failure("QC04", encode_cursor(mutated), "OE_QUERY_CURSOR_MANIFEST_MISMATCH")
expect_cursor_failure(
    "QC05", cursor, "OE_QUERY_CURSOR_FILTER_MISMATCH",
    req=request({"event_ids": [old_events[0]["event_id"]]}))
stale = decode_cursor(cursor)
stale["requested_position"] = {"sequence": "99999999999999999999",
                                "event_id": "iaevt-v1-" + "f" * 64}
stale_cursor = encode_cursor(stale)
try:
    evidence.query_history_v1(
        exact_request, new_manifest, cursor=stale_cursor,
        load_segment=load_segment, load_predecessor=load_predecessor)
except evidence.OperationalEvidenceError as exc:
    if exc.code != "OE_QUERY_CURSOR_POSITION_STALE":
        raise SystemExit(f"QC06 wrong stale-position discriminator: {exc.code}")
else:
    raise SystemExit("QC06 stale cursor position was accepted")
expect_cursor_failure(
    "QC07", cursor[:-1] + ("0" if cursor[-1] != "0" else "1"),
    "OE_QUERY_CURSOR_DIGEST_INVALID")

recomputed = evidence.encode_query_cursor_v1(
    exact_request, new_manifest,
    {"sequence": new_events[0]["sequence"], "event_id": target})
page = evidence.query_history_v1(
    exact_request, new_manifest, cursor=recomputed, load_segment=load_segment,
    load_predecessor=load_predecessor)
if page["decision_usable"] or page["requested_position"] != {
        "sequence": new_events[0]["sequence"], "event_id": target}:
    raise SystemExit("QC08 recomputed skip became decision-usable or hid coverage")

overflow = evidence.query_history_v1(
    request({"record_kinds": ["finding.closed"]}, rows=1), new_manifest,
    load_segment=load_segment, load_predecessor=load_predecessor)
if (overflow["code"] != "OE_QUERY_REQUIRES_BOUNDED_REVIEW" or
        not overflow["truncated"] or overflow["decision_usable"] or
        overflow["next_cursor"] is None):
    raise SystemExit("C07-R08/R11 overflow made a negative or complete claim")

old_raw = rotation.canonical_json_v1(old_events[0])
byte_overflow = evidence.query_history_v1(
    request({"record_kinds": ["finding.closed"]}, rows=10,
            size=len(old_raw)), new_manifest,
    load_segment=load_segment, load_predecessor=load_predecessor)
if (len(byte_overflow["rows"]) != 1 or not byte_overflow["truncated"] or
        byte_overflow["next_cursor"] is None or
        byte_overflow["code"] != "OE_QUERY_REQUIRES_BOUNDED_REVIEW" or
        byte_overflow["coverage"]["start"] is None or
        byte_overflow["coverage"]["end"] is None):
    raise SystemExit("C07-R08 byte overflow lost bounded coverage or next cursor")

route_request = {
    "schema": "implementaudit.history-query-request.v1",
    "route": "QUERY_HISTORY_THEN_RESUME", "requirement": "REQUIRED",
    "evidence_ids": [target],
}
if evidence.normalize_history_filters_v1(route_request) != {"event_ids": [target]}:
    raise SystemExit("C07-R12 exact HC-H2B request did not normalize")
loaded.clear()
route_result = evidence.query_history_v1(
    request(route_request), new_manifest, load_segment=load_segment,
    load_predecessor=load_predecessor)
if ([row["event_id"] for row in route_result["rows"]] != [target] or
        loaded != [target] or not route_result["decision_usable"] or
        route_result["establishes"]):
    raise SystemExit("C07-R12 exact HC-H2B request was not selectively executed")
for key, value in (
        ("route", "OTHER"), ("requirement", "OPTIONAL"),
        ("evidence_ids", []), ("evidence_ids", [target, old_events[0]["event_id"]]),
        ("evidence_ids", ["foreign"])):
    bad = dict(route_request); bad[key] = value
    try:
        evidence.normalize_history_filters_v1(bad)
    except evidence.OperationalEvidenceError as exc:
        if exc.code != "OE_QUERY_FILTER_INVALID":
            raise SystemExit(f"C07-R12 malformed route request returned {exc.code}")
    else:
        raise SystemExit("C07-R12 malformed route request was accepted")

parser = evidence.build_cli_parser_v1()
if parser.parse_args(["status"]).command != "status":
    raise SystemExit("C07-R01 status grammar is absent")
query_args = parser.parse_args([
    "query", "--family", "CODE", "--max-rows", "1", "--max-bytes", "1024"])
if query_args.command != "query" or query_args.family != "CODE":
    raise SystemExit("C07-R01 query grammar is absent")
if parser.parse_args(["why", "evidence"]).record_id != "evidence":
    raise SystemExit("C07-R01 why grammar is absent")
effects = []
original_urlopen = evidence.urllib.request.urlopen
original_subprocess_run = evidence.subprocess.run


def forbidden_network(*_args, **_kwargs):
    effects.append("NETWORK")
    raise AssertionError("C07 reader attempted network")


def forbidden_process(*_args, **_kwargs):
    effects.append("PROCESS")
    raise AssertionError("C07 pure reader attempted a process effect")


evidence.urllib.request.urlopen = forbidden_network
evidence.subprocess.run = forbidden_process
try:
    evidence.evaluate_currentness(snapshot)
    evidence.query_family(snapshot, "CODE")
    evidence.explain_history_why_v1(snapshot, "evidence")
    evidence.query_history_v1(
        exact_request, new_manifest, load_segment=load_segment,
        load_predecessor=load_predecessor)
finally:
    evidence.urllib.request.urlopen = original_urlopen
    evidence.subprocess.run = original_subprocess_run
if effects:
    raise SystemExit(f"C07-R16 pure readers crossed an effect boundary: {effects}")
for required in ("diff_snapshots", "export_snapshot"):
    if not hasattr(evidence, required):
        raise SystemExit(f"C08-DE00 required diff/export interface is absent: {required}")
if any(action.dest in ("repository", "run_root", "snapshot_root", "manifest")
       for action in parser._actions):
    raise SystemExit("C07-R16 CLI accepted caller-supplied authority")
PY
}

run_diff_export_contract() {
"${py_cmd[@]}" - "$loader" "$fixtures/diff-export-cases.json" \
  "skills/implementaudit/references/operational-evidence-schema.json" \
  "$tmp/diff-export" <<'PY'
import copy
import hashlib
import importlib.util
import inspect
import json
import os
import pathlib
import sys


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


evidence = load("operational_evidence_diff_export", sys.argv[1])
fixture = json.loads(pathlib.Path(sys.argv[2]).read_text(encoding="utf-8"))
schema = json.loads(pathlib.Path(sys.argv[3]).read_text(encoding="utf-8"))
tmp = pathlib.Path(sys.argv[4]).resolve()
tmp.mkdir(parents=True)
expected_ids = [f"DE{i:02d}" for i in range(1, 19)]
if (fixture.get("schema") !=
        "implementaudit.operational-evidence-diff-export-cases.v1" or
        [row.get("id") for row in fixture.get("cases", [])] != expected_ids or
        len({row.get("operation") for row in fixture["cases"]}) != 18 or
        fixture.get("states") != list(evidence.STATES) or
        fixture.get("formats") != ["json", "table", "graph"]):
    raise SystemExit("C08 DE fixture does not bind the complete ordered matrix")
missing = [name for name in fixture["required_interfaces"]
           if not hasattr(evidence, name)]
if missing:
    raise SystemExit(f"C08-DE00 required diff/export interface is absent: {missing}")
if schema.get("x-bounded-snapshot-diff-export") != {
        "diff_schema": "implementaudit-operational-snapshot-diff.v1",
        "export_schema": "implementaudit-operational-snapshot-export.v1",
        "projection_schema": "implementaudit-operational-snapshot-projection.v1",
        "payload_schema": "implementaudit-operational-snapshot-payload.v1",
        "semantic_identity": "record_id_plus_explicit_snapshot_fields",
        "canonical_json_export": "canonical_json_v1(snapshot)",
        "projection_formats": ["table", "graph"],
        "projection_encoding": "canonical_json_v1_inert_data",
        "bounds": "finite_positive_rows_and_record_bytes",
        "overflow": "OE_EXPORT_REQUIRES_BOUNDED_REVIEW",
        "destination": "explicit_absolute_new_file_under_isolated_owned_root",
        "authority_ceiling": "READ_ONLY_OBSERVATION_OR_EXPLICIT_TASK_OWNED_DESTINATION_ONLY",
        "activegraph_authority": False, "publication": False,
    }:
    raise SystemExit("C08 diff/export schema contract is absent or widened")


def currentness(state="CURRENT", invalidators=None):
    if invalidators is None:
        invalidators = [] if state == "CURRENT" else [f"FIXTURE_{state}"]
    return {"state": state, "invalidators": list(invalidators)}


def record(identifier, family="EVIDENCE", state="CURRENT", **extra):
    value = {
        "id": identifier, "sequence": 0, "record_type": "Evidence",
        "claim_id": f"claim:{identifier}", "criterion_id": f"criterion:{identifier}",
        "leg": "EFFECT", "result_class": "GREEN", "proxy": False,
        "source_identity": f"source:{identifier}",
        "native_owner_identity": f"owner:{family.lower()}",
        "currentness": currentness(state), "controls": [],
        "contrary_evidence": [], "family": family,
        "authority_ceiling": "READ_ONLY_NATIVE_ARTIFACT_FACT",
        "artifact_sha256": "1" * 64,
    }
    value.update(extra)
    return value


def snapshot(identifier, records=None, *, aggregate=None, omitted=None,
             manifest_digest=None):
    records = copy.deepcopy(list(records or []))
    release_types = sorted({
        "Commit", "Tree", "Worktree", "GeneratedArtifact", "Package",
        "Install", "Host", "PullRequest", "Check", "Merge", "Tag",
        "Release", "Asset", "PublicSurface"})
    release_invalidators = [
        f"MISSING_RELEASE_LAYER:{record_type}" for record_type in release_types]
    release_invalidators.append("PUBLIC_IDENTITY_NOT_EXACTLY_ONE")
    for sequence, row in enumerate(records):
        row["sequence"] = sequence
    if omitted is None:
        omitted = [{
            "kind": "OWNER_FACT_NON_CURRENT", "collector": "evidence_failure",
            "owner": "R0038-C04", "family": row["family"],
            "fact_path": f"evidence_records/{row['id']}", "record_id": row["id"],
            "record_type": row["record_type"],
            "native_owner_identity": row["native_owner_identity"],
            "state": row["currentness"]["state"],
            "invalidators": list(row["currentness"]["invalidators"]),
        } for row in records if row["currentness"]["state"] != "CURRENT"]
    omitted = list(omitted)
    omitted.extend({
        "kind": "RELEASE_INVALIDATOR", "collector": "release",
        "owner": "R0038-C05", "state": "UNVERIFIED", "code": code}
        for code in release_invalidators)
    omitted.sort(key=evidence.canonical_json_v1)
    aggregate = aggregate or ("DEGRADED" if omitted else "COMPLETE")

    def semantic(value):
        result = copy.deepcopy(value)
        result["semantic_sha256"] = hashlib.sha256(
            evidence.canonical_json_v1(result)).hexdigest()
        return result

    frontier = {"population": 1,
                "counts": {"DONE": 1, "ACTIVE": 0, "READY": 0, "BLOCKED": 0},
                "active": [], "ready": [], "blocked_summary": {},
                "writer_holds": {}, "resource_holds": {}}
    frontier["digest"] = hashlib.sha256(
        evidence.canonical_json_v1(frontier)).hexdigest()
    native_value = semantic({
        "schema": evidence.NATIVE_CURRENT_SCHEMA,
        "authority_ceiling": "READ_ONLY_NATIVE_CURRENT_FACT", "establishes": [],
        "repository": {"root": "$REPOSITORY_ROOT", "git_common_dir": "$GIT_COMMON_DIR"},
        "controller": {"id": "fixture-controller", "ref": "refs/controller",
                       "record_oid": "1" * 40},
        "claim": {"id": "fixture-claim", "run_id": "fixture-run",
                  "run_root": ".IMPLEMENTAUDIT/runs/fixture-run"},
        "continuity": {
            "generation": "G0001", "source_epoch": "G0001",
            "invalidation_ref": "refs/invalidation", "invalidation_oid": "2" * 40,
            "boundary_kind": "manual-resume", "boundary_event_id": "fixture-event",
            "pointer_ref": "refs/pointer", "pointer_oid": "3" * 40,
            "pointer_digest": "2" * 64,
            "receipt_schema": "implementaudit.continuity-receipt.v3",
            "receipt_ref": "refs/receipt", "receipt_oid": "4" * 40,
            "receipt": "refs/receipt@" + "4" * 40,
            "marker_ref": "refs/marker", "marker_oid": "5" * 40,
            "generation_manifest_oid": "6" * 40,
            "generation_manifest_digest": "3" * 64,
            "cold_high_water": "fixture-high-water", "degraded_state": "NONE"},
        "hot": {"state_path": "STATE.md", "state_sha256": "2" * 64,
                "roadmap_path": "ROADMAP.md", "roadmap_sha256": "3" * 64,
                "work_graph_path": "WORK_GRAPH.json", "work_graph_sha256": "4" * 64,
                "work_graph_compiler_sha256": "5" * 64},
        "frontier": frontier,
        "andon_state": "FIXTURE=ACTIVE",
        "open_andons": ["FIXTURE"], "active_instructions": [{
            "id": "I001", "reference": "fixture", "kind": "test",
            "authority": "fixture", "subject": "fixture", "issued_epoch": "G0001",
            "status": "active", "status_evidence": "fixture",
            "supersedes_by": "-", "scope_end": "fixture"}],
        "next_action": "bounded fixture observation", "route": {
            "controller_id": "fixture-controller", "controller_record_oid": "1" * 40,
            "ref": "refs/route", "record_oid": "7" * 40,
            "record_identity": "fixture-route", "decision": "NOT_REQUIRED",
            "classification": "none", "route_transaction_id": "fixture-transaction",
            "obligation_id": None, "route_state": None},
    })
    repository_value = {
        "schema": evidence.REPOSITORY_COLLECTION_SCHEMA,
        "repository": {"commit": "3" * 40, "tree": "4" * 40,
                       "worktree_state": "CLEAN", "input_file_set_sha256": "5" * 64},
        "capabilities": [
            {"capability": "file_facts", "state": "SUPPORTED",
             "reason_code": "fixture"},
            {"capability": "package_manifest", "state": "NOT_APPLICABLE",
             "reason_code": "fixture"},
            {"capability": "python_ast", "state": "NOT_APPLICABLE",
             "reason_code": "fixture"},
            {"capability": "validation_registry_entries",
             "state": "NOT_APPLICABLE", "reason_code": "fixture"}],
        "diagnostics": {"warnings": [], "errors": [], "skipped": [], "unknown": []},
        "facts": [], "static_collector_invocations": [],
    }
    evidence_value = semantic({
        "schema": evidence.EVIDENCE_FAILURE_COLLECTION_SCHEMA,
        "families": ["EVIDENCE", "FAILURE"],
        "source": {"path": "operational-evidence.json", "sha256": "6" * 64,
                   "run_identity": "fixture-run", "artifact_identity": "fixture-artifact"},
        "first_red_id": None, "first_red_state": "NOT_APPLICABLE",
        "weakest_leg_id": records[0]["id"] if records else None,
        "residual_ids": [],
        "layer_census": {"ATTEMPT": 0, "RECEIPT": 0, "EFFECT": len(records),
                         "RECOVERY": 0, "CLOSURE": 0},
        "evidence_records": records, "failure_records": [], "establishes": [],
    })
    release_value = semantic({
        "schema": evidence.RELEASE_COLLECTION_SCHEMA, "families": ["RELEASE"],
        "repository": {"commit": "3" * 40, "tree": "4" * 40,
                       "worktree_state": "CLEAN"},
        "local_manifest_sha256": "7" * 64, "external_capture_sha256": "8" * 64,
        "external_boundary": {
            "capture_identity": "fixture-capture", "source_identity": "fixture-source",
            "auth_state": "PRESENT", "rate_state": "AVAILABLE", "rate_remaining": 1,
            "pagination_state": "COMPLETE", "pagination_pages": 1,
            "object_drift": False, "captured_at": "2026-01-01T00:00:00Z",
            "expires_at": "2027-01-01T00:00:00Z",
            "evaluated_at": "2026-01-01T00:00:01Z"},
        "omissions": [{
            "record_type": record_type, "state": "UNKNOWN",
            "invalidator": f"MISSING_RELEASE_LAYER:{record_type}"}
            for record_type in release_types], "node_type_census": {
            "Commit": 0, "Tree": 0, "Worktree": 0, "GeneratedArtifact": 0,
            "Package": 0, "Install": 0, "Host": 0, "PullRequest": 0,
            "Check": 0, "Merge": 0, "Tag": 0, "Release": 0,
            "Asset": 0, "PublicSurface": 0}, "nodes": [],
        "candidate": {"state": "UNVERIFIED",
                      "invalidators": release_invalidators,
                      "local_commit": "3" * 40, "public_commit": None},
        "establishes": [],
    })

    def collection(owner, value):
        return {"owner": owner, "state": "CURRENT", "value": value,
                "sha256": hashlib.sha256(
                    evidence.canonical_json_v1(value)).hexdigest()}

    return {
        "schema_version": "implementaudit-operational-snapshot-payload.v1",
        "snapshot_id": "iasnap-v1-" + identifier * 64,
        "aggregate": aggregate,
        "families": list(evidence.FAMILIES),
        "missing_or_omitted_state": list(omitted),
        "collections": {
            "native_current": collection("R0038-C03", native_value),
            "repository": collection("R0038-C02", repository_value),
            "evidence_failure": collection("R0038-C04", evidence_value),
            "release": collection("R0038-C05", release_value),
        },
        "input_manifest_sha256": manifest_digest or identifier * 64,
    }


def canonical(value):
    return evidence.canonical_json_v1(value)


def refresh_collection(value, name):
    collection = value["collections"][name]
    semantic_value = collection["value"]
    if "semantic_sha256" in semantic_value:
        semantic_value.pop("semantic_sha256")
        semantic_value["semantic_sha256"] = hashlib.sha256(
            canonical(semantic_value)).hexdigest()
    collection["sha256"] = hashlib.sha256(canonical(semantic_value)).hexdigest()


def expect_error(code, action):
    try:
        action()
    except evidence.OperationalEvidenceError as exc:
        if exc.code != code:
            raise SystemExit(f"expected {code}, observed {exc.code}")
    else:
        raise SystemExit(f"expected {code}, operation passed")


observed = []
base = snapshot("a", [record("one"), record("two")])

# R4 causal controls are intentionally independent of the R3 generated model.
# C1 records the genuine C04 producer's unique-list calls and then duplicates a
# real retained failure reference with every dependent digest refreshed.  C2
# attacks the native operation itself on both sides of the terminal rename;
# neither cell is derived from the production phase-hook population.
r4_causal_red = []
producer_unique_paths = []
original_string_list = evidence._string_list


def observe_producer_unique(value, path, *, allowed=None, unique=True):
    if unique:
        producer_unique_paths.append(path)
    return original_string_list(value, path, allowed=allowed, unique=unique)


evidence._string_list = observe_producer_unique
try:
    producer_evidence = evidence.collect_evidence_failure(pathlib.Path(
        "fixtures/operational-evidence/run-artifacts/positive"))
finally:
    evidence._string_list = original_string_list
producer_operators = {
    ("currentness.invalidators"
     if path.endswith(".currentness.invalidators")
     else path.rsplit(".", 1)[-1])
    for path in producer_unique_paths}
expected_producer_operators = {
    "currentness.invalidators", "controls", "contrary_evidence",
    "evidence_ids", "residual_ids"}
if producer_operators != expected_producer_operators:
    r4_causal_red.append(
        "C08-R4-C1 producer unique-list census mismatch "
        f"{sorted(producer_operators)}")

producer_snapshot = copy.deepcopy(base)
producer_collection = producer_snapshot["collections"]["evidence_failure"]
producer_collection["value"] = producer_evidence
producer_collection["sha256"] = hashlib.sha256(
    canonical(producer_evidence)).hexdigest()
duplicate_lineage = copy.deepcopy(producer_snapshot)
failure = duplicate_lineage["collections"]["evidence_failure"]["value"][
    "failure_records"][0]
failure["evidence_ids"].append(failure["evidence_ids"][0])
refresh_collection(duplicate_lineage, "evidence_failure")
try:
    evidence.diff_snapshots(producer_snapshot, duplicate_lineage)
except evidence.OperationalEvidenceError as exc:
    if exc.code != "OE_DIFF_SNAPSHOT_INVALID":
        r4_causal_red.append(
            f"C08-R4-C1 duplicate evidence_ids returned {exc.code}")
else:
    r4_causal_red.append(
        "C08-R4-C1 duplicate evidence_ids returned success-shaped diff")

if os.name == "nt":
    original_publish = evidence._snapshot_atomic_no_replace_v1

    late_root = tmp / "r4-late-edge"
    late_root.mkdir()
    late_destination = late_root / "snapshot.json"
    late_alias = late_root / "late-alias"
    late_edge_reached = False
    late_link_created = False

    def attack_late_edge(handle, target):
        global late_edge_reached, late_link_created
        late_edge_reached = True
        stage = next(
            path for path in late_root.iterdir()
            if path != late_destination and
            path.name.endswith(".implementaudit-stage"))
        try:
            os.link(stage, late_alias)
            late_link_created = True
        except OSError:
            pass
        return original_publish(handle, target)

    evidence._snapshot_atomic_no_replace_v1 = attack_late_edge
    late_receipt = None
    late_error = None
    try:
        try:
            late_receipt = evidence.export_snapshot(
                producer_snapshot, late_destination, owned_root=late_root,
                output_format="json")
        except evidence.OperationalEvidenceError as exc:
            late_error = exc
    finally:
        evidence._snapshot_atomic_no_replace_v1 = original_publish
    if (late_link_created and
            (late_error is None or
             late_error.code != "OE_EXPORT_WRITE_FAILED" or late_receipt)):
        r4_causal_red.append(
            "C08-R4-C2 late hard link crossed final-check/native-rename edge")
    if (not late_edge_reached and
            (late_error is None or
             late_error.code != "OE_EXPORT_WRITE_FAILED" or late_receipt)):
        r4_causal_red.append(
            "C08-R4-C2 unavailable hard-link custody did not fail typed")
    if not late_edge_reached and any(late_root.iterdir()):
        r4_causal_red.append(
            "C08-R4-C2 capability refusal left a stage or destination")

    post_root = tmp / "r4-post-edge"
    post_root.mkdir()
    post_destination = post_root / "snapshot.json"
    post_alias = post_root / "post-alias"
    post_edge_reached = False
    post_link_created = False

    def attack_post_edge(handle, target):
        global post_edge_reached, post_link_created
        post_edge_reached = True
        result = original_publish(handle, target)
        try:
            os.link(target, post_alias)
            post_link_created = True
        except OSError:
            pass
        return result

    evidence._snapshot_atomic_no_replace_v1 = attack_post_edge
    post_receipt = None
    post_error = None
    try:
        try:
            post_receipt = evidence.export_snapshot(
                producer_snapshot, post_destination, owned_root=post_root,
                output_format="json")
        except evidence.OperationalEvidenceError as exc:
            post_error = exc
    finally:
        evidence._snapshot_atomic_no_replace_v1 = original_publish
    if (post_link_created and
            (post_error is None or
             post_error.code != "OE_EXPORT_WRITE_FAILED" or post_receipt)):
        r4_causal_red.append(
            "C08-R4-C2 post-publication live-handle hard link returned success")
    if (not post_edge_reached and
            (post_error is None or
             post_error.code != "OE_EXPORT_WRITE_FAILED" or post_receipt)):
        r4_causal_red.append(
            "C08-R4-C2 unavailable post-publication custody did not fail typed")
    if not post_edge_reached and any(post_root.iterdir()):
        r4_causal_red.append(
            "C08-R4-C2 post-publication capability refusal left an object")

if r4_causal_red:
    raise SystemExit("; ".join(r4_causal_red))

# The real current-volume capability cell above remains unmocked.  The
# remaining positive transaction controls exercise exact bytes, collision and
# cleanup on the explicit no-hard-link-capability branch.
if hasattr(evidence, "_snapshot_hardlink_publication_capable_v1"):
    evidence._snapshot_hardlink_publication_capable_v1 = (
        lambda _kernel, _handle: True)

permuted = copy.deepcopy(base)
permuted["collections"]["evidence_failure"]["value"]["evidence_records"].reverse()
refresh_collection(permuted, "evidence_failure")
first = evidence.diff_snapshots(base, permuted)
second = evidence.diff_snapshots(permuted, base)
if first["added"] or first["removed"] or first["changed"] or canonical(first) != canonical(second):
    raise SystemExit("DE01 permutation did not yield one empty canonical diff")
observed.append("DE01")

added_snapshot = snapshot("b", [record("one"), record("two"),
                                record("three")])
added = evidence.diff_snapshots(base, added_snapshot)
if ([row["identity"] for row in added["added"]] != ["record:three"] or
        added["removed"] or added["changed"] or
        added["before_snapshot_id"] != base["snapshot_id"] or
        added["after_snapshot_id"] != added_snapshot["snapshot_id"]):
    raise SystemExit("DE02 added record was not represented exactly once")
observed.append("DE02")

removed_snapshot = snapshot("c", [record("one")])
removed = evidence.diff_snapshots(base, removed_snapshot)
if [row["identity"] for row in removed["removed"]] != ["record:two"]:
    raise SystemExit("DE03 removed record was normalized away")
observed.append("DE03")

changed_snapshot = snapshot("d", [record("one", claim_id="changed"),
                                  record("two")])
changed = evidence.diff_snapshots(base, changed_snapshot)
if ([row["identity"] for row in changed["changed"]] != ["record:one"] or
        changed["added"] or changed["removed"]):
    raise SystemExit("DE04 semantic change became remove/add")
observed.append("DE04")

state_base = snapshot("a", [record("one"), record("two")])
for state in fixture["states"][1:]:
    state_snapshot = snapshot("e", [record("one"), record("two", state=state)])
    try:
        state_diff = evidence.diff_snapshots(state_base, state_snapshot)
    except evidence.OperationalEvidenceError as exc:
        raise SystemExit(
            f"DE05 {state} snapshot failed {exc.code} at {exc.path}: "
            f"{state_snapshot['missing_or_omitted_state']}") from exc
    if ([row["identity"] for row in state_diff["changed"]] != [
            "record:two", "snapshot:missing_or_omitted_state"] or
            state_diff["changed"][0]["after"]["currentness"]["state"] != state):
        raise SystemExit(f"DE05 lost explicit currentness transition to {state}")
observed.append("DE05")

identity_snapshot = snapshot(
    "f", [record("one"), record("two", state="STALE")], aggregate="DEGRADED",
    omitted=[{"family": "EVIDENCE", "kind": "OWNER_FACT_NON_CURRENT",
              "collector": "evidence_failure", "owner": "R0038-C04",
              "fact_path": "evidence_records/two", "record_id": "two",
              "record_type": "Evidence", "native_owner_identity": "owner:evidence",
              "state": "STALE", "invalidators": ["FIXTURE_STALE"]}],
    manifest_digest="f" * 64)
identity = evidence.diff_snapshots(base, identity_snapshot)
if ([row["identity"] for row in identity["changed"]] != [
        "record:two", "snapshot:missing_or_omitted_state"] or
        identity["before_input_manifest_sha256"] ==
        identity["after_input_manifest_sha256"]):
    raise SystemExit("DE06 snapshot identity/currentness changes were hidden")
observed.append("DE06")

json_destination = tmp / "snapshot.json"
json_receipt = evidence.export_snapshot(
    base, json_destination, owned_root=tmp, output_format="json")
if (json_destination.read_bytes() != canonical(base) or
        json_receipt["output_sha256"] != hashlib.sha256(canonical(base)).hexdigest() or
        json.loads(json_destination.read_text(encoding="utf-8")) != base):
    raise SystemExit("DE07 JSON export diverged from canonical snapshot bytes")
observed.append("DE07")

ambient_before = canonical(evidence.diff_snapshots(base, changed_snapshot))
old_cwd = pathlib.Path.cwd()
old_locale = os.environ.get("LC_ALL")
try:
    os.chdir(tmp)
    os.environ["LC_ALL"] = "C.invalid-hostile"
    os.environ["IMPLEMENTAUDIT_DIFF_NOISE"] = "ignored"
    ambient_after = canonical(evidence.diff_snapshots(base, changed_snapshot))
finally:
    os.chdir(old_cwd)
    os.environ.pop("IMPLEMENTAUDIT_DIFF_NOISE", None)
    if old_locale is None:
        os.environ.pop("LC_ALL", None)
    else:
        os.environ["LC_ALL"] = old_locale
if ambient_before != ambient_after:
    raise SystemExit("DE08 diff bytes depend on ambient cwd/locale/environment")
observed.append("DE08")

mixed = snapshot("8", [record("one"), record("two", state="STALE")])
for output_format in ("table", "graph"):
    projection = json.loads(evidence.render_snapshot_projection_v1(
        mixed, output_format=output_format, max_rows=100, max_bytes=100000))
    if (projection["format"] != output_format or projection["truncated"] or
            projection["included_count"] != 2 or projection["omitted_count"] != 0 or
            projection["state_census"] != {"CURRENT": 1, "STALE": 1}):
        raise SystemExit(f"DE09 {output_format} projection lost state coverage")
observed.append("DE09")

bounded = json.loads(evidence.render_snapshot_projection_v1(
    mixed, output_format="table", max_rows=1, max_bytes=100000))
if (not bounded["truncated"] or bounded["decision_usable"] or
        bounded["included_count"] != 1 or bounded["omitted_count"] != 1 or
        bounded["state_census"] != {"CURRENT": 1, "STALE": 1}):
    raise SystemExit("DE10 bounded projection did not remain explicit nondecision")
observed.append("DE10")

hostile_text = "|\n\t\u001b[31m`<script>javascript:()</script> $(touch pwn) =1+1"
hostile = snapshot("9", [record("hostile", claim_id=hostile_text)])
hostile_projection = json.loads(evidence.render_snapshot_projection_v1(
    hostile, output_format="graph", max_rows=10, max_bytes=100000))
if hostile_projection["rows"][0]["record"]["claim_id"] != hostile_text:
    raise SystemExit("DE11 hostile content was executed, removed, or normalized")
observed.append("DE11")

duplicate = snapshot("7", [record("dup"), record("dup")])
expect_error("OE_DIFF_SNAPSHOT_INVALID", lambda: evidence.diff_snapshots(base, duplicate))
invalid_schema = copy.deepcopy(base)
invalid_schema["schema_version"] = "wrong"
expect_error("OE_DIFF_SNAPSHOT_INVALID", lambda: evidence.diff_snapshots(invalid_schema, base))
invalid_digest = copy.deepcopy(base)
invalid_digest["input_manifest_sha256"] = "0" * 64
expect_error("OE_DIFF_SNAPSHOT_INVALID", lambda: evidence.diff_snapshots(base, invalid_digest))

foreign_record_type = copy.deepcopy(base)
foreign_record_type["collections"]["evidence_failure"]["value"][
    "evidence_records"][0]["record_type"] = "Foreign"
refresh_collection(foreign_record_type, "evidence_failure")
expect_error("OE_DIFF_SNAPSHOT_INVALID", lambda: evidence.diff_snapshots(
    base, foreign_record_type))

current_with_invalidator = copy.deepcopy(base)
current_with_invalidator["collections"]["evidence_failure"]["value"][
    "evidence_records"][0]["currentness"]["invalidators"] = ["FOREIGN"]
refresh_collection(current_with_invalidator, "evidence_failure")
expect_error("OE_DIFF_SNAPSHOT_INVALID", lambda: evidence.diff_snapshots(
    base, current_with_invalidator))

empty_collections = copy.deepcopy(base)
empty_collections["collections"] = {}
expect_error("OE_DIFF_SNAPSHOT_INVALID", lambda: evidence.diff_snapshots(
    base, empty_collections))

foreign_currentness = copy.deepcopy(base)
foreign_currentness["collections"]["evidence_failure"]["value"][
    "evidence_records"][0]["currentness"]["state"] = "FOREIGN"
refresh_collection(foreign_currentness, "evidence_failure")
expect_error("OE_DIFF_SNAPSHOT_INVALID", lambda: evidence.diff_snapshots(
    base, foreign_currentness))

foreign_omitted = copy.deepcopy(base)
foreign_omitted["missing_or_omitted_state"] = [{"foreign": "value"}]
expect_error("OE_DIFF_SNAPSHOT_INVALID", lambda: evidence.diff_snapshots(
    base, foreign_omitted))

unknown_nested_member = copy.deepcopy(base)
unknown_nested_member["collections"]["evidence_failure"]["value"][
    "evidence_records"][0]["unknown"] = "foreign"
refresh_collection(unknown_nested_member, "evidence_failure")
expect_error("OE_DIFF_SNAPSHOT_INVALID", lambda: evidence.diff_snapshots(
    base, unknown_nested_member))

mixed_release_variant = copy.deepcopy(base)
mixed_release_variant["collections"]["release"]["value"]["nodes"] = [{
    "id": "git-commit", "record_type": "Commit", "family": "RELEASE",
    "source_identity": "git:HEAD", "native_owner_identity": "git:repository",
    "currentness": currentness(),
    "authority_ceiling": "READ_ONLY_NATIVE_OBSERVATION", "layer": "LOCAL",
    "object_identity": "3" * 40, "path": "foreign-mixed-variant",
}]
refresh_collection(mixed_release_variant, "release")
expect_error("OE_DIFF_SNAPSHOT_INVALID", lambda: evidence.diff_snapshots(
    base, mixed_release_variant))
observed.append("DE12")

expect_error("OE_EXPORT_DESTINATION_INVALID", lambda: evidence.export_snapshot(
    base, None, owned_root=tmp, output_format="json"))
expect_error("OE_EXPORT_DESTINATION_INVALID", lambda: evidence.export_snapshot(
    base, pathlib.Path("relative.json"), owned_root=tmp, output_format="json"))
expect_error("OE_EXPORT_DESTINATION_INVALID", lambda: evidence.export_snapshot(
    base, tmp.parent / "outside.json", owned_root=tmp, output_format="json"))
if (tmp.parent / "outside.json").exists():
    raise SystemExit("DE13 export wrote outside the explicit owned root")
observed.append("DE13")

occupied = tmp / "occupied.json"
occupied.write_text("non-task-owned", encoding="utf-8")
expect_error("OE_EXPORT_DESTINATION_EXISTS", lambda: evidence.export_snapshot(
    base, occupied, owned_root=tmp, output_format="json"))
if occupied.read_text(encoding="utf-8") != "non-task-owned":
    raise SystemExit("DE14 export mutated an existing destination")

alias_parent = tmp / "alias-parent"
alias_parent.mkdir()
alias_destination = alias_parent / ".." / "alias-destination.json"
expect_error("OE_EXPORT_DESTINATION_INVALID", lambda: evidence.export_snapshot(
    base, alias_destination, owned_root=tmp, output_format="json"))
if (tmp / "alias-destination.json").exists():
    raise SystemExit("DE14 export accepted a non-canonical destination spelling")

alias_root = alias_parent / ".."
alias_root_destination = tmp / "alias-root-destination.json"
expect_error("OE_EXPORT_DESTINATION_INVALID", lambda: evidence.export_snapshot(
    base, alias_root_destination, owned_root=alias_root, output_format="json"))
if alias_root_destination.exists():
    raise SystemExit("DE14 export accepted a non-canonical owned-root spelling")

replacement_destination = tmp / "replacement.json"
replacement_alias = tmp / "replacement-stage-alias"
original_stage_hook = evidence._snapshot_stage_v1


def replace_at_final_check(phase):
    if phase == "before-publish":
        stage = next(path for path in tmp.iterdir()
                     if path.name.endswith(".implementaudit-stage"))
        os.link(stage, replacement_alias)


evidence._snapshot_stage_v1 = replace_at_final_check
try:
    expect_error("OE_EXPORT_WRITE_FAILED", lambda: evidence.export_snapshot(
        base, replacement_destination, owned_root=tmp, output_format="json"))
finally:
    evidence._snapshot_stage_v1 = original_stage_hook
observed.append("DE14")

noncurrent_first = json.loads(evidence.render_snapshot_projection_v1(
    mixed, output_format="table", max_rows=1, max_bytes=100000))
if (noncurrent_first["rows"][0]["record"]["currentness"]["state"] == "CURRENT" or
        noncurrent_first["omitted_state_census"] != {"CURRENT": 1}):
    raise SystemExit("DE15 bound preferentially hid non-current rows")
observed.append("DE15")

effects = []
original_process = evidence.subprocess.run
original_network = evidence.urllib.request.urlopen
evidence.subprocess.run = lambda *_a, **_k: effects.append("PROCESS")
evidence.urllib.request.urlopen = lambda *_a, **_k: effects.append("NETWORK")
try:
    evidence.diff_snapshots(hostile, base)
    evidence.render_snapshot_projection_v1(
        hostile, output_format="graph", max_rows=10, max_bytes=100000)
finally:
    evidence.subprocess.run = original_process
    evidence.urllib.request.urlopen = original_network
if effects:
    raise SystemExit(f"DE16 command-looking data triggered effects: {effects}")
observed.append("DE16")

before_bytes = canonical(base)
evidence.diff_snapshots(base, changed_snapshot)
if canonical(base) != before_bytes:
    raise SystemExit("DE17 diff mutated the immutable input snapshot")
observed.append("DE17")

source = inspect.getsource(evidence.diff_snapshots) + inspect.getsource(
    evidence.export_snapshot) + inspect.getsource(evidence.render_snapshot_projection_v1)
if any(name in source for name in ("ActiveGraph", "madge", "knip", "sqlite",
                                    "urlopen(", "subprocess.", "pip install")):
    raise SystemExit("DE18 core diff/export depends on optional or external tooling")
observed.append("DE18")

if observed != expected_ids:
    raise SystemExit(f"C08 DE matrix skipped or reordered cases: {observed}")

parser = evidence.build_cli_parser_v1()
if parser.parse_args(["diff", "before.json", "after.json"]).command != "diff":
    raise SystemExit("C08 diff CLI route is absent")
export_args = parser.parse_args([
    "export", "--destination", os.fspath(tmp / "cli.json"),
    "--owned-root", os.fspath(tmp), "--format", "json"])
if export_args.command != "export" or export_args.destination != (tmp / "cli.json"):
    raise SystemExit("C08 export CLI route is absent or derived authority")
PY
}

if [ "${1:-}" = "--diff-export-only" ]; then
  run_diff_export_contract
  printf 'operational-evidence-contract.test: diff/export ok\n'
  exit 0
fi

if [ "${1:-}" = "--query-only" ]; then
  run_query_contract
  printf 'operational-evidence-contract.test: query ok\n'
  exit 0
fi

"${py_cmd[@]}" - "$loader" \
  "skills/implementaudit/scripts/compile-work-graph.py" \
  "skills/implementaudit/scripts/route-transaction.py" \
  "skills/implementaudit/scripts/claim-run.sh" \
  "skills/implementaudit/scripts/validate-run-root.sh" \
  "skills/implementaudit/references/route-obligations.md" \
  "skills/implementaudit/SKILL.md" \
  "skills/audit-state/SKILL.md" \
  "$fixtures/native-current.json" "$tmp/native-current" \
  "$rotation_loader" <<'PY'
import copy
import hashlib
import importlib.util
import inspect
import json
import os
import pathlib
import shutil
import subprocess
import sys
import threading
import types


LOADER = pathlib.Path(sys.argv[1]).resolve()
COMPILER = pathlib.Path(sys.argv[2]).resolve()
ROUTE = pathlib.Path(sys.argv[3]).resolve()
CLAIM = pathlib.Path(sys.argv[4]).resolve()
VALIDATE_RUN_ROOT = pathlib.Path(sys.argv[5]).resolve()
ROUTE_REFERENCE = pathlib.Path(sys.argv[6]).resolve()
GOVERNOR = pathlib.Path(sys.argv[7]).resolve()
AUDIT_STATE = pathlib.Path(sys.argv[8]).resolve()
FIXTURE = json.loads(pathlib.Path(sys.argv[9]).read_text(encoding="utf-8"))
CASE_ROOT = pathlib.Path(sys.argv[10]).resolve()
ROTATION = pathlib.Path(sys.argv[11]).resolve()
CASE_ROOT.mkdir(parents=True)
ZERO64 = "0" * 64
ONE64 = "1" * 64
RUN_ARTIFACT_FIXTURE = pathlib.Path(
    "fixtures/operational-evidence/run-artifacts/positive/operational-evidence.json"
).resolve()
RELEASE_FIXTURE = pathlib.Path(
    "fixtures/operational-evidence/release/positive").resolve()
schema_definition = json.loads(
    (LOADER.parent.parent / "references/operational-evidence-schema.json")
    .read_text(encoding="utf-8"))
if schema_definition.get("x-native-current-facts") != {
        "schema": "implementaudit-native-current-facts-v1",
        "authority_ceiling": "READ_ONLY_NATIVE_CURRENT_FACT",
        "fixed_hot_paths": ["STATE.md", "ROADMAP.md", "WORK_GRAPH.json"],
        "currentness_chain": [
            "controller", "claim", "generation_pointer", "receipt_v3",
            "immediate_predecessor", "migration_marker", "route_record"],
        "predecessor_predicate":
            "canonical_R0011_read_only_currentness_and_exact_immediate_v2_v3",
        "predecessor_validator_execution": {
            "mode": "child_loaded_byte_bound_private_materialization",
            "closure": ["claim-run.sh", "validate-run-root.sh"],
            "child_binding": "completed_child_reports_exact_sha256_pair",
            "environment":
                "exact_allowlist_without_inherited_python_loader_or_module_overrides",
            "cleanup":
                "exact_members_or_typed_residue_with_manual_reconciliation",
        },
        "route_predicate": "canonical_R0033_pure_read_only_currentness",
        "route_semantic_fence":
            "canonical_R0033_recheck_with_fresh_controller_and_final_route_controller_ref_pair",
        "graph_projection": "implementaudit.work-graph.v1",
        "graph_compiler_execution": "byte_bound_and_finally_fenced",
        "publication": False,
        "activegraph_authority": False,
    }:
    raise SystemExit("NCR20 RED: schema does not freeze native-current facts")
snapshot_schema = schema_definition.get("x-immutable-snapshot-publication", {})
if (snapshot_schema.get("schema") != "IA-OPERATIONAL-SNAPSHOT-v1" or
        snapshot_schema.get("current_schema") !=
        "implementaudit.operational-snapshot-current.v1" or
        snapshot_schema.get("authority_ceiling") != "R0038_OUTPUT_ROOT_ONLY"):
    raise SystemExit("C06 schema does not freeze immutable snapshot publication")
fixture_manifest = json.loads(
    pathlib.Path("fixtures/operational-evidence/snapshots/fixture-manifest.json")
    .read_text(encoding="utf-8"))
if (fixture_manifest.get("causal_cases") != [f"C06-R{i:02d}" for i in range(1, 16)] or
        fixture_manifest.get("held_out_cases") != [f"C06-H{i:02d}" for i in range(1, 5)]):
    raise SystemExit("C06 fixture manifest does not enumerate the complete matrix")


def canonical(value):
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
        allow_nan=False).encode("utf-8")


def git(repo, *args, input_bytes=None):
    completed = subprocess.run(
        ["git", "-C", str(repo), *args], input=input_bytes,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    if completed.returncode:
        raise SystemExit(
            f"native-current fixture git {' '.join(args)} failed: "
            f"{completed.stderr.decode('utf-8', 'replace')}")
    return completed.stdout


def write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def object_id(repo, data):
    return git(repo, "hash-object", "-w", "--stdin", input_bytes=data).decode().strip()


def update_ref(repo, ref, oid):
    git(repo, "update-ref", ref, oid)


def load_bytes_module(path, name):
    module = types.ModuleType(name)
    module.__file__ = str(path)
    module.__package__ = ""
    exec(compile(path.read_bytes(), str(path), "exec"), module.__dict__)
    return module


def load_module(repo, serial):
    path = repo / "skills/implementaudit/scripts/operational-evidence.py"
    return load_bytes_module(path, f"operational_evidence_native_current_{serial}")


def prepare(case, serial, *, include_c04=False, include_c05=False):
    repo = CASE_ROOT / f"case-{serial:02d}-{case}"
    repo.mkdir()
    git(repo, "init", "--quiet")
    git(repo, "config", "user.name", "Fixture")
    git(repo, "config", "user.email", "fixture@example.invalid")
    write(repo / "tracked.txt", b"native current fixture\n")
    request_input = FIXTURE["route_request_input"]
    request_input_path = request_input["path"]
    request_input_raw = request_input["content"].encode("utf-8")
    write(repo / request_input_path, request_input_raw)
    script = repo / "skills/implementaudit/scripts/operational-evidence.py"
    compiler = repo / "skills/implementaudit/scripts/compile-work-graph.py"
    route = repo / "skills/implementaudit/scripts/route-transaction.py"
    claim = repo / "skills/implementaudit/scripts/claim-run.sh"
    validate_run_root = repo / "skills/implementaudit/scripts/validate-run-root.sh"
    route_reference = repo / "skills/implementaudit/references/route-obligations.md"
    schema = repo / "skills/implementaudit/references/operational-evidence-schema.json"
    governor = repo / "skills/implementaudit/SKILL.md"
    audit_state = repo / "skills/audit-state/SKILL.md"
    script.parent.mkdir(parents=True)
    route_reference.parent.mkdir(parents=True, exist_ok=True)
    audit_state.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(LOADER, script)
    shutil.copyfile(COMPILER, compiler)
    shutil.copyfile(ROUTE, route)
    shutil.copyfile(CLAIM, claim)
    shutil.copyfile(VALIDATE_RUN_ROOT, validate_run_root)
    shutil.copyfile(ROUTE_REFERENCE, route_reference)
    shutil.copyfile(
        LOADER.parent.parent / "references/operational-evidence-schema.json", schema)
    shutil.copyfile(GOVERNOR, governor)
    shutil.copyfile(AUDIT_STATE, audit_state)
    if include_c05:
        for release_member in RELEASE_FIXTURE.rglob("*"):
            if release_member.is_file():
                destination = repo / release_member.relative_to(RELEASE_FIXTURE)
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(release_member, destination)
    git(repo, "add", "tracked.txt", request_input_path,
        str(script.relative_to(repo)),
        str(compiler.relative_to(repo)), str(route.relative_to(repo)),
        str(claim.relative_to(repo)), str(validate_run_root.relative_to(repo)),
        str(route_reference.relative_to(repo)),
        str(schema.relative_to(repo)),
        str(governor.relative_to(repo)), str(audit_state.relative_to(repo)))
    if include_c05:
        git(repo, "add", "release-local.json", "external-capture.json", "artifacts")
    git(repo, "commit", "--quiet", "-m", "fixture")
    info_exclude = repo / ".git/info/exclude"
    with info_exclude.open("a", encoding="utf-8") as stream:
        stream.write(".IMPLEMENTAUDIT/\n")
    head = git(repo, "rev-parse", "HEAD").decode().strip()
    tree = git(repo, "rev-parse", "HEAD^{tree}").decode().strip()

    fixture = copy.deepcopy(FIXTURE)
    controller = fixture["controller_id"]
    claim = fixture["claim_id"]
    run_id = fixture["run_id"]
    v3_predecessor_cases = {
        "positive-v3-predecessor", "predecessor-v3-invalidation",
        "predecessor-v3-pointer", "predecessor-v3-own-token",
    }
    post_marker_successor = case == "positive-v3-predecessor"
    generation = "G0003" if case in v3_predecessor_cases else fixture["generation"]
    run_relative = pathlib.PurePosixPath(
        ".IMPLEMENTAUDIT", "runs", run_id).as_posix()
    run_root = repo / pathlib.Path(*pathlib.PurePosixPath(run_relative).parts)
    run_root.mkdir(parents=True)
    for name in (
            "STATE.md", "PROTOCOL.md", "ROADMAP.md", "THINKING.md",
            "sidecars.md", "tools.md", "context.md"):
        write(run_root / name, f"# {name} fixture\n".encode())
    common = git(
        repo, "rev-parse", "--path-format=absolute", "--git-common-dir"
    ).decode().strip()
    repository = repo.as_posix()
    controller_run_absolute = run_root.as_posix()
    run_absolute = str(run_root.resolve())

    claim_lines = [
        "schema=implementaudit.run-claim.v2",
        f"claim_id={claim}",
        "claimed_at_utc=2026-08-20T00:00:00Z",
        "mode=full",
        "templates=STATE.md PROTOCOL.md ROADMAP.md THINKING.md sidecars.md tools.md context.md",
        f"repo_root={repository}",
        f"git_common_dir={common}",
        "run_base=.IMPLEMENTAUDIT/runs",
        f"run_root={run_relative}",
        f"run_name={run_id}",
    ]
    write(run_root / ".claimed", ("\n".join(claim_lines) + "\n").encode())
    write(run_root / ".controller", f"controller_id={controller}\n".encode())

    instruction = fixture["active_instruction"]
    instruction_status = "satisfied" if case == "no-active-instruction" else instruction["status"]
    current_rows = [
        ("Run root", f"`{run_relative}`"),
        ("Phase", "native-current fixture"),
        ("Status", "IN_PHASE"),
    ]
    if case != "no-open-andon":
        current_rows.append(("Andon state", fixture["andon_state"]))
    current_rows.append((
        "Audit object state",
        "adjacent narrative falsely says CELL-A DONE and CELL-B BLOCKED"))
    if case != "no-next-action":
        current_rows.append(("Next action", fixture["next_action"]))
    state_lines = [
        "# Native current fixture",
        "",
        f"Current epoch: {generation}",
        "",
        "## Current phase",
        "",
        "| Field | Value |",
        "|---|---|",
        *[f"| {key} | {value} |" for key, value in current_rows],
        "",
        "## Instruction lifecycle",
        "",
        "| Instr | Reference | Kind | Authority | Subject | Issued epoch | Status | Status evidence | Supersedes/by | Scope end |",
        "|---|---|---|---|---|---|---|---|---|---|",
        "| {id} | {reference} | {kind} | {authority} | {subject} | {issued_epoch} | {status} | {status_evidence} | {supersedes_by} | {scope_end} |".format(
            **{**instruction, "status": instruction_status}),
        "",
        "## Reconciliation",
        "",
        "| Epoch | Boundary provenance | Established at | Repo identity | Reconciled | Notes |",
        "|---|---|---|---|---|---|",
        f"| {generation} | manual-resume | 2026-08-20T00:00:00Z | {head} {tree} | yes | exact native-current boundary |",
        "",
    ]
    state_raw = "\n".join(state_lines).encode("utf-8")
    roadmap_raw = b"# Native current roadmap\n\nOnly bounded current work is retained.\n"
    write(run_root / "STATE.md", state_raw)
    write(run_root / "ROADMAP.md", roadmap_raw)
    if include_c04:
        shutil.copyfile(RUN_ARTIFACT_FIXTURE, run_root / "operational-evidence.json")

    graph = fixture["work_graph"]
    if case == "no-active":
        graph["cells"][0]["state"] = "DONE"
    elif case == "no-ready":
        graph["cells"][1]["state"] = "DONE"
    elif case == "no-holds":
        graph["serialization_groups"] = {}
    elif case == "unknown-graph":
        graph["schema"] = "implementaudit.work-graph.future"
    graph_raw = canonical(graph)
    write(run_root / "WORK_GRAPH.json", graph_raw)
    write(
        repo / ".activegraph/native-current.json",
        canonical({"active": ["MIRROR-ONLY"], "authority": "forbidden"}))

    controller_record = (
        "implementaudit.controller-current.v1\t"
        f"{controller}\t{claim}\t{controller_run_absolute}\n").encode()
    controller_oid = object_id(repo, controller_record)
    if case != "no-controller":
        update_ref(repo, f"refs/implementaudit/controllers/{controller}", controller_oid)
    if case == "duplicate-controller":
        duplicate = object_id(repo, (
            "implementaudit.controller-current.v1\tcontroller-other\t"
            f"{claim}\t{controller_run_absolute}\n").encode())
        update_ref(repo, "refs/implementaudit/controllers/controller-other", duplicate)

    invalidation_raw = (
        "implementaudit.continuity-invalidation.v1\t"
        f"{controller}\t{controller_oid}\t{claim}\tmanual-resume\tfixture-boundary\n"
    ).encode()
    invalidation_oid = object_id(repo, invalidation_raw)
    update_ref(
        repo, f"refs/implementaudit/continuity-invalidations/{controller}",
        invalidation_oid)

    state_digest = hashlib.sha256(state_raw).hexdigest()
    roadmap_digest = hashlib.sha256(roadmap_raw).hexdigest()
    graph_digest = hashlib.sha256(graph_raw).hexdigest()
    manifest_raw = canonical({"schema": "implementaudit.state-generation-manifest.v1"})
    manifest_oid = object_id(repo, manifest_raw)
    manifest_digest = hashlib.sha256(manifest_raw).hexdigest()

    genesis_pointer = None
    genesis_pointer_oid = None
    if post_marker_successor:
        genesis_pointer_body = {
            "schema_version": "implementaudit.state-generation-pointer.v1",
            "controller_id": controller,
            "claim_id": claim,
            "run_id": run_id,
            "generation_id": "G0002",
            "predecessor_pointer_oid": None,
            "predecessor_pointer_digest": None,
            "generation_manifest_oid": manifest_oid,
            "generation_manifest_digest": manifest_digest,
            "cold_high_water": "00000000000000000001",
            "hot_state_digest": state_digest,
            "hot_roadmap_digest": roadmap_digest,
            "work_graph_path": "WORK_GRAPH.json",
            "work_graph_digest": graph_digest,
            "query_contract_version": "implementaudit.history-query.v1",
            "source_epoch": "G0002",
            "degraded_state": "NONE",
        }
        genesis_pointer = {
            **genesis_pointer_body,
            "pointer_digest": hashlib.sha256(
                canonical(genesis_pointer_body)).hexdigest(),
        }
        genesis_pointer_oid = object_id(repo, canonical(genesis_pointer))

    if case in v3_predecessor_cases:
        predecessor_epoch = "G0002"
        predecessor_ref = (
            f"refs/implementaudit/continuity-receipts/{controller}/"
            f"{predecessor_epoch}")
        predecessor_invalidation = (
            "invalid" if case == "predecessor-v3-invalidation"
            else invalidation_oid)
        predecessor_pointer_ref = (
            "refs/WRONG/pointer" if case == "predecessor-v3-pointer"
            else f"refs/implementaudit/current-generations/{controller}")
        own_predecessor = (
            "not-a-predecessor-token" if case == "predecessor-v3-own-token"
            else f"refs/implementaudit/continuity-receipts/{controller}/G0001@{head}")
        predecessor_pointer_oid = (
            genesis_pointer_oid if post_marker_successor else head)
        predecessor_pointer_digest = (
            genesis_pointer["pointer_digest"] if post_marker_successor else ONE64)
        predecessor_raw = (
            "implementaudit.continuity-receipt.v3\t"
            f"{controller}\t{claim}\t{run_id}\t{predecessor_epoch}\t"
            f"{predecessor_invalidation}\t{predecessor_pointer_ref}\t"
            f"{predecessor_pointer_oid}\t{predecessor_pointer_digest}\t"
            f"{state_digest}\t{roadmap_digest}\tWORK_GRAPH.json\t"
            f"{graph_digest}\t{manifest_oid}\t{manifest_digest}\t"
            f"00000000000000000001\t{fixture['next_action']}\t"
            f"{own_predecessor}\n").encode()
    else:
        predecessor_epoch = "G0001"
        predecessor_ref = (
            f"refs/implementaudit/continuity-receipts/{controller}/"
            f"{predecessor_epoch}")
        predecessor_head = (
            "not-an-object" if case == "predecessor-v2-head" else head)
        predecessor_boundary = (
            "unknown-boundary" if case == "predecessor-v2-boundary"
            else "manual-resume")
        predecessor_raw = (
            "implementaudit.continuity-receipt.v2\t"
            f"{controller}\t{controller_oid}\t{claim}\t{predecessor_head}\t{tree}\t"
            f"{state_digest}\t{roadmap_digest}\t{invalidation_oid}\t"
            f"{predecessor_boundary}\t{predecessor_epoch}\tfixture predecessor\n").encode()
    predecessor_oid = object_id(repo, predecessor_raw)
    update_ref(repo, predecessor_ref, predecessor_oid)
    predecessor = f"{predecessor_ref}@{predecessor_oid}"

    pointer_claim = ONE64[:32] if case == "wrong-claim" else claim
    pointer_run = "foreign-run" if case == "wrong-run" else run_id
    pointer_epoch = "G0001" if case == "wrong-epoch" else generation
    pointer_graph_digest = ZERO64 if case == "stale-graph-digest" else graph_digest
    pointer_state_digest = ZERO64 if case == "stale-state-digest" else state_digest
    pointer_body = {
        "schema_version": "implementaudit.state-generation-pointer.v1",
        "controller_id": controller,
        "claim_id": pointer_claim,
        "run_id": pointer_run,
        "generation_id": generation,
        "predecessor_pointer_oid": (
            genesis_pointer_oid if post_marker_successor else None),
        "predecessor_pointer_digest": (
            genesis_pointer["pointer_digest"] if post_marker_successor else None),
        "generation_manifest_oid": manifest_oid,
        "generation_manifest_digest": manifest_digest,
        "cold_high_water": "00000000000000000001",
        "hot_state_digest": pointer_state_digest,
        "hot_roadmap_digest": roadmap_digest,
        "work_graph_path": "WORK_GRAPH.json",
        "work_graph_digest": pointer_graph_digest,
        "query_contract_version": "implementaudit.history-query.v1",
        "source_epoch": pointer_epoch,
        "degraded_state": "NONE",
    }
    pointer = {
        **pointer_body,
        "pointer_digest": hashlib.sha256(canonical(pointer_body)).hexdigest(),
    }
    pointer_raw = canonical(pointer)
    if case == "malformed-pointer":
        pointer_raw = pointer_raw.replace(
            b'{"claim_id"',
            b'{"controller_id":"duplicate","claim_id"', 1)
    pointer_oid = object_id(repo, pointer_raw)
    pointer_ref = f"refs/implementaudit/current-generations/{controller}"
    update_ref(repo, pointer_ref, pointer_oid)

    receipt_ref = f"refs/implementaudit/continuity-receipts/{controller}/{generation}"
    receipt_raw = (
        "implementaudit.continuity-receipt.v3\t"
        f"{controller}\t{claim}\t{run_id}\t{generation}\t{invalidation_oid}\t"
        f"{pointer_ref}\t{pointer_oid}\t{pointer['pointer_digest']}\t"
        f"{state_digest}\t{roadmap_digest}\tWORK_GRAPH.json\t{graph_digest}\t"
        f"{manifest_oid}\t{manifest_digest}\t00000000000000000001\t"
        f"{fixture['next_action']}\t{predecessor}\n").encode()
    if case == "receipt-v2":
        receipt_raw = (
            "implementaudit.continuity-receipt.v2\t"
            f"{controller}\t{controller_oid}\t{claim}\t{head}\t{tree}\t"
            f"{state_digest}\t{roadmap_digest}\t{invalidation_oid}\t"
            f"manual-resume\t{generation}\t{fixture['next_action']}\n").encode()
    receipt_oid = object_id(repo, receipt_raw)
    update_ref(repo, receipt_ref, receipt_oid)
    receipt = f"{receipt_ref}@{receipt_oid}"

    marker_generation = "G0002" if post_marker_successor else generation
    marker_receipt_ref = predecessor_ref if post_marker_successor else receipt_ref
    marker_receipt_oid = predecessor_oid if post_marker_successor else receipt_oid
    marker_raw = (
        "implementaudit.current-generation-migration.v1\t"
        f"{controller}\t{claim}\t{run_id}\t{marker_generation}\t{pointer_ref}\t"
        f"implementaudit.state-generation-pointer.v1\t{marker_receipt_ref}\t"
        f"{marker_receipt_oid}\ttrue").encode()
    marker_oid = object_id(repo, marker_raw)
    if case != "missing-marker":
        update_ref(
            repo, f"refs/implementaudit/current-generation-migrations/{controller}",
            marker_oid)

    route_module = load_bytes_module(
        route, f"route_transaction_native_current_fixture_{serial}")
    boundary = {
        "kind": "manual-resume", "event_id": "fixture-boundary"}
    boundary["digest"] = route_module.digest_json(boundary)
    scope = {"identity": fixture["next_action"]}
    scope["digest"] = route_module.digest_json(scope)
    action = {
        "identity": "bounded-read",
        "class": "PURE_BOUNDED_READ_OR_VALIDATION",
        "argv": ["route-read-snapshot"],
    }
    action["digest"] = route_module.digest_json(action)
    request = {
        "schema": "implementaudit.route-decision-request.v1",
        "predicate_version": "R0033.route-predicate.v1",
        "boundary": boundary,
        "scope": scope,
        "action": action,
        "inputs": [
            {
                "identity": "input:hot-state",
                "path": f"{run_relative}/STATE.md",
                "digest": "sha256:" + state_digest,
            },
            {
                "identity": "input:request",
                "path": request_input_path,
                "digest": "sha256:" + hashlib.sha256(request_input_raw).hexdigest(),
            },
        ],
    }
    current = {
        "controller_id": controller,
        "controller_record_oid": controller_oid,
        "claim_id": claim,
        "explicit_run_root": run_absolute,
        "continuity_generation": generation,
        "continuity_receipt": receipt,
        "boundary_kind": "manual-resume",
        "boundary_event_id": "fixture-boundary",
        "next_action": fixture["next_action"],
    }
    noncurrent, observed_inputs = route_module.request_observations(
        repo, current, request)
    decision, classification, invalidators = route_module.classify(
        request, noncurrent)
    package, child_source = route_module.executing_package_evidence(repo, request)
    host_binding_generation = (
        "not-a-generation" if case == "stale-route-host-binding" else generation)
    host_correlation_id = "sha256:" + "3" * 64
    identity_seed = {
        "request": request,
        "controller_record_oid": controller_oid,
        "claim_id": claim,
        "continuity_receipt": receipt,
        "host_binding_generation": host_binding_generation,
        "package": package,
        "child_source": child_source,
    }
    route_transaction_id = route_module.digest_json(
        {"kind": "transaction", "seed": identity_seed})
    obligation_id = (
        route_module.digest_json({"kind": "obligation", "seed": identity_seed})
        if decision == "REQUIRED" else None)
    evidence = {
        "owner": {
            "controller_record_oid": controller_oid,
            "claim_id": claim,
            "run_root": run_absolute,
        },
        "authority": {
            "continuity_generation": generation,
            "continuity_receipt": receipt,
        },
        "effect": {
            "action_identity": action["identity"],
            "action_digest": action["digest"],
            "derived_class": route_module.mechanical_action_class(action["argv"]),
        },
        "dependency": {
            "host_binding_generation": host_binding_generation,
            "host_correlation_id": host_correlation_id,
        },
        "inputs": observed_inputs,
        "package": package,
        "child_source": child_source,
    }
    expiry_fingerprint = route_module.digest_json(
        {"request": request, "mechanical_evidence": evidence})
    route_controller = (
        "controller-other" if case == "wrong-route-controller" else controller)
    route_base = {
        "schema": "implementaudit.route-decision.v1",
        "predicate_version": "R0033.route-predicate.v1",
        "controller_id": route_controller,
        "claim_id": claim,
        "explicit_run_root": run_absolute,
        "continuity_generation": generation,
        "continuity_receipt": receipt,
        "host_id": "codex",
        "host_session_id": "native-current-fixture",
        "host_binding_generation": host_binding_generation,
        "host_correlation_id": host_correlation_id,
        "boundary": boundary,
        "scope": scope,
        "action": action,
        "evidence": {
            key: evidence[key] for key in (
                "owner", "authority", "effect", "dependency")
        },
        "inputs": observed_inputs,
        "package": package,
        "child_source": child_source,
        "decision": decision,
        "classification": classification,
        "invalidators": invalidators,
        "expiry_fingerprint": expiry_fingerprint,
        "expires_on": route_module.EXPIRES_ON,
        "predecessor_record_oid": None,
        "route_transaction_id": route_transaction_id,
        "obligation_id": obligation_id,
        "route_state": None,
        "child_lifecycle_owned": False,
        "consumed_record_oid": None,
    }
    if case == "stale-route-scope":
        stale_scope = {"identity": "stale native-current scope"}
        stale_scope["digest"] = route_module.digest_json(stale_scope)
        route_base["scope"] = stale_scope
    elif case == "stale-route-action":
        stale_action = {
            "identity": "stale-action", "class": "PURE_BOUNDED_READ_OR_VALIDATION",
            "argv": ["route-read-snapshot"],
        }
        stale_action["digest"] = route_module.digest_json(stale_action)
        route_base["action"] = stale_action
    elif case == "malformed-route-expiry":
        route_base["expiry_fingerprint"] = "not-a-digest"
    elif case == "contradictory-route-classification":
        route_base["classification"] = "JUDGEMENT_REQUIRED"
    elif case == "contradictory-route-evidence":
        route_base["evidence"] = copy.deepcopy(evidence)
        route_base["evidence"]["owner"]["claim_id"] = ONE64[:32]
    elif case == "mismatched-route-inputs":
        route_base["inputs"] = copy.deepcopy(request["inputs"])
        route_base["inputs"][0]["digest"] = "sha256:" + ZERO64
    elif case == "malformed-route-history":
        route_base["history_query"] = {"schema": "unknown-history"}
    elif case == "malformed-route-lifecycle":
        route_base["child_lifecycle_owned"] = True
        route_base["lifecycle"] = {"state": None}
    route_identity = "sha256:" + hashlib.sha256(canonical(route_base)).hexdigest()
    if case == "stale-route-identity":
        route_identity = "sha256:" + ZERO64
    route_record = {**route_base, "record_identity": route_identity}
    route_raw = canonical(route_record) + b"\n"
    if case == "noncanonical-route-bytes":
        route_raw = json.dumps(
            route_record, sort_keys=True, indent=2).encode("utf-8") + b"\n"
    route_oid = object_id(repo, route_raw)
    update_ref(repo, f"refs/implementaudit/route-decisions/{controller}", route_oid)
    return repo


positive_repo = prepare("positive", 0)
positive_module = load_module(positive_repo, 0)
if not hasattr(positive_module, "collect_native_current"):
    raise SystemExit("NCR00 RED: collect_native_current is missing")

negative_cases = [
    ("no-open-andon", "NCR04 missing open Andon"),
    ("no-active-instruction", "NCR05 missing active instruction"),
    ("no-next-action", "NCR06 missing next action"),
    ("no-controller", "NCR07 missing controller"),
    ("wrong-claim", "NCR08 wrong claim"),
    ("stale-graph-digest", "NCR09 stale graph digest"),
    ("stale-route-identity", "NCR10 stale route identity"),
    ("wrong-epoch", "NCR11 wrong epoch"),
    ("receipt-v2", "NCR12 non-v3 receipt"),
    ("duplicate-controller", "NCR13 duplicate controller"),
    ("malformed-pointer", "NCR14 malformed duplicate-key pointer"),
    ("wrong-run", "NCR15 wrong run"),
    ("stale-state-digest", "NCR16 stale hot STATE digest"),
    ("missing-marker", "NCR17 missing permanent marker"),
    ("wrong-route-controller", "NCR18 wrong-controller route"),
    ("unknown-graph", "NCR19 unknown graph schema"),
    ("predecessor-v2-head", "NCR21 malformed v2 predecessor object field"),
    ("predecessor-v2-boundary", "NCR22 malformed v2 predecessor boundary"),
    ("predecessor-v3-invalidation", "NCR23 malformed v3 predecessor typed field"),
    ("predecessor-v3-pointer", "NCR24 wrong v3 predecessor pointer ref"),
    ("predecessor-v3-own-token", "NCR25 malformed v3 own-predecessor token"),
    ("stale-route-host-binding", "NCR26 malformed retained R0033 host dependency"),
    ("stale-route-scope", "NCR27 stale R0033 scope"),
    ("stale-route-action", "NCR28 stale R0033 action"),
    ("malformed-route-expiry", "NCR29 malformed R0033 expiry fingerprint"),
    ("contradictory-route-classification", "NCR30 contradictory R0033 decision/classification"),
    ("contradictory-route-evidence", "NCR31 contradictory R0033 evidence"),
    ("mismatched-route-inputs", "NCR32 mismatched R0033 inputs"),
    ("malformed-route-history", "NCR33 malformed R0033 history payload"),
    ("malformed-route-lifecycle", "NCR34 malformed R0033 lifecycle payload"),
    ("noncanonical-route-bytes", "NCR49 noncanonical R0033 route-record bytes"),
]
red_failures = []


def expect_frontier_projection_error(label, mutation, serial):
    """Exercise the real collector's frontier-shape boundary with a bad projection."""
    repo = prepare("positive", serial)
    module = load_module(repo, serial)
    graph_path = repo / ".IMPLEMENTAUDIT/runs/native-current-ABC123/WORK_GRAPH.json"
    graph_raw = graph_path.read_bytes()
    projection = copy.deepcopy(module._native_graph_projection(graph_raw)[0])
    mutation(projection)

    def fake_module(*args, **kwargs):
        return types.SimpleNamespace(
            compile_frontier_projection=lambda ignored: copy.deepcopy(projection))

    module._native_module_from_bytes = fake_module
    try:
        module._native_graph_projection(graph_raw)
    except module.OperationalEvidenceError as exc:
        if exc.code != "OE_NATIVE_CURRENT_MISSING":
            red_failures.append(f"{label}: returned {exc.code}")
    else:
        red_failures.append(f"{label}: malformed frontier projection was accepted")


frontier_projection_controls = [
    ("R0038-H03 missing frontier field", lambda projection: projection.pop("active")),
    ("R0038-H04 wrong frontier field type",
     lambda projection: projection.__setitem__("active", {})),
    ("R0038-H05 inconsistent frontier count",
     lambda projection: projection["counts"].__setitem__("ACTIVE", 0)),
]

zero_active_repo = prepare("no-active", 140)
zero_active_module = load_module(zero_active_repo, 140)
try:
    zero_active_record = zero_active_module.collect_native_current()
except zero_active_module.OperationalEvidenceError as exc:
    raise SystemExit(
        "R0038-H01 legitimate zero-ACTIVE fixture was rejected: "
        f"{exc.code} at {exc.path}: {exc.message}")
if (zero_active_record["frontier"]["counts"]["ACTIVE"] != 0 or
        zero_active_record["frontier"]["active"] != []):
    raise SystemExit("R0038-H01 zero-ACTIVE frontier facts are inconsistent")

zero_hold_repo = prepare("no-holds", 141)
zero_hold_module = load_module(zero_hold_repo, 141)
try:
    zero_hold_record = zero_hold_module.collect_native_current()
except zero_hold_module.OperationalEvidenceError as exc:
    raise SystemExit(
        "R0038-H02 legitimate zero-hold fixture was rejected: "
        f"{exc.code} at {exc.path}: {exc.message}")
if (zero_hold_record["frontier"]["writer_holds"] != {} or
        zero_hold_record["frontier"]["resource_holds"] != {}):
    raise SystemExit("R0038-H02 zero-hold frontier facts are inconsistent")

for serial, (label, mutation) in enumerate(frontier_projection_controls, 150):
    expect_frontier_projection_error(label, mutation, serial)

for serial, (case, label) in enumerate(negative_cases, 1):
    repo = prepare(case, serial)
    module = load_module(repo, serial)
    try:
        module.collect_native_current()
    except module.OperationalEvidenceError:
        pass
    else:
        red_failures.append(f"{label}: invalid native fact was accepted")
    if case in {
            "no-open-andon", "no-active-instruction", "no-next-action",
            "no-controller",
            "wrong-claim", "stale-graph-digest", "wrong-epoch"}:
        try:
            module.publish_current_snapshot()
        except module.OperationalEvidenceError:
            pass
        else:
            red_failures.append(f"{label}: publisher accepted invalid native fact")
        if (repo / ".IMPLEMENTAUDIT/runs/native-current-ABC123/operational-evidence").exists():
            red_failures.append(f"{label}: publisher created output before validation")

v3_positive_repo = prepare("positive-v3-predecessor", 100)
v3_positive_module = load_module(v3_positive_repo, 100)
v3_route_module = load_bytes_module(
    v3_positive_repo / "skills/implementaudit/scripts/route-transaction.py",
    "route_transaction_v3_predecessor_probe")
v3_claim = v3_positive_repo / "skills/implementaudit/scripts/claim-run.sh"
v3_canonical = subprocess.run(
    [str(v3_route_module.trusted_host_executable(v3_positive_repo, "bash")),
     v3_route_module.bash_script_path(v3_claim),
     "--require-current-continuity", "controller-current"],
    cwd=v3_positive_repo, env=v3_route_module.sanitized_action_environment(),
    stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False)
if v3_canonical.returncode:
    raise SystemExit(
        "canonical v3 predecessor fixture is invalid: " +
        (v3_canonical.stderr.strip() or "no validator diagnostic"))
try:
    v3_positive_record = v3_positive_module.collect_native_current()
except v3_positive_module.OperationalEvidenceError as exc:
    raise SystemExit(
        f"bounded canonical v3 predecessor/no-history control failed: {exc.receipt()}")
v3_marker_oid = git(
    v3_positive_repo, "rev-parse", "--verify",
    "refs/implementaudit/current-generation-migrations/controller-current"
).decode().strip()
v3_marker_fields = git(
    v3_positive_repo, "cat-file", "blob", v3_marker_oid
).decode("utf-8").split("\t")
if (v3_positive_record["continuity"]["generation"] != "G0003" or
        v3_marker_fields[4] != "G0002"):
    raise SystemExit(
        "R0038_POST_MARKER_SPLIT_RED="
        f"current={v3_positive_record['continuity']['generation']};"
        f"marker-genesis={v3_marker_fields[4]}")
v3_current_pointer = json.loads(git(
    v3_positive_repo, "cat-file", "blob",
    v3_positive_record["continuity"]["pointer_oid"]))
v3_genesis_receipt_fields = git(
    v3_positive_repo, "cat-file", "blob", v3_marker_fields[8]
).decode("utf-8").rstrip("\n").split("\t")
if (v3_marker_fields[7] !=
        "refs/implementaudit/continuity-receipts/controller-current/G0002" or
        v3_current_pointer["predecessor_pointer_oid"] !=
        v3_genesis_receipt_fields[7] or
        v3_current_pointer["predecessor_pointer_digest"] !=
        v3_genesis_receipt_fields[8]):
    raise SystemExit(
        "R0038 post-marker positive does not bind current G0003 to genesis G0002")
older_ref = subprocess.run(
    ["git", "-C", str(v3_positive_repo), "show-ref", "--verify", "--hash",
     "refs/implementaudit/continuity-receipts/controller-current/G0001"],
    stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
if older_ref.returncode == 0:
    raise SystemExit("v3 no-history control unexpectedly resolved G0001")


def replace_permanent_marker(repo, transform):
    marker_ref = (
        "refs/implementaudit/current-generation-migrations/controller-current")
    marker_oid = git(repo, "rev-parse", "--verify", marker_ref).decode().strip()
    marker_raw = git(repo, "cat-file", "blob", marker_oid)
    replacement_oid = object_id(repo, transform(marker_raw))
    update_ref(repo, marker_ref, replacement_oid)


def expect_post_marker_rejection(label, serial, mutation, expected_path):
    repo = prepare("positive-v3-predecessor", serial)
    mutation(repo)
    module = load_module(repo, serial)
    try:
        module.collect_native_current()
    except module.OperationalEvidenceError as exc:
        if exc.path != expected_path:
            red_failures.append(
                f"{label}: rejected at {exc.path}, expected {expected_path}")
    else:
        red_failures.append(f"{label}: malformed post-marker route was accepted")


def malformed_marker_transform(kind):
    def transform(raw):
        fields = raw.split(b"\t")
        if kind == "NUL":
            return fields[0] + b"\0\t" + b"\t".join(fields[1:])
        if kind == "C0":
            return fields[0] + b"\x01\t" + b"\t".join(fields[1:])
        if kind == "DEL":
            return fields[0] + b"\x7f\t" + b"\t".join(fields[1:])
        if kind == "LF":
            return raw + b"\n"
        if kind == "CRLF":
            return raw + b"\r\n"
        if kind == "ADJACENT_TAB":
            return b"\t".join(fields[:2]) + b"\t\t" + b"\t".join(fields[2:])
        if kind == "TRAILING_TAB":
            return raw + b"\t"
        if kind == "EXTRA_FIELD":
            return raw + b"\textra"
        if kind == "INVALID_UTF8":
            return fields[0] + b"\xff\t" + b"\t".join(fields[1:])
        raise AssertionError(kind)
    return transform


for serial, malformed_kind in enumerate((
        "NUL", "C0", "DEL", "LF", "CRLF", "ADJACENT_TAB",
        "TRAILING_TAB", "EXTRA_FIELD", "INVALID_UTF8"), 160):
    expect_post_marker_rejection(
        f"R0038-PM-{malformed_kind}", serial,
        lambda repo, kind=malformed_kind: replace_permanent_marker(
            repo, malformed_marker_transform(kind)),
        "$native.marker")


def stale_genesis_receipt(repo):
    current_receipt_oid = git(
        repo, "rev-parse", "--verify",
        "refs/implementaudit/continuity-receipts/controller-current/G0003"
    ).decode().strip()

    def transform(raw):
        fields = raw.decode("utf-8").split("\t")
        fields[8] = current_receipt_oid
        return "\t".join(fields).encode("utf-8")

    replace_permanent_marker(repo, transform)


def rebound_marker(repo):
    current_receipt_ref = (
        "refs/implementaudit/continuity-receipts/controller-current/G0003")
    current_receipt_oid = git(
        repo, "rev-parse", "--verify", current_receipt_ref).decode().strip()

    def transform(raw):
        fields = raw.decode("utf-8").split("\t")
        fields[4] = "G0003"
        fields[7] = current_receipt_ref
        fields[8] = current_receipt_oid
        return "\t".join(fields).encode("utf-8")

    replace_permanent_marker(repo, transform)


def mismatch_immediate_predecessor(repo):
    pointer_ref = "refs/implementaudit/current-generations/controller-current"
    pointer_oid = git(repo, "rev-parse", "--verify", pointer_ref).decode().strip()
    pointer = json.loads(git(repo, "cat-file", "blob", pointer_oid))
    pointer_body = dict(pointer)
    pointer_body.pop("pointer_digest")
    pointer_body["predecessor_pointer_oid"] = "f" * 40
    pointer_body["predecessor_pointer_digest"] = "e" * 64
    replacement_pointer = {
        **pointer_body,
        "pointer_digest": hashlib.sha256(canonical(pointer_body)).hexdigest(),
    }
    replacement_pointer_oid = object_id(repo, canonical(replacement_pointer))
    update_ref(repo, pointer_ref, replacement_pointer_oid)
    receipt_ref = (
        "refs/implementaudit/continuity-receipts/controller-current/G0003")
    receipt_oid = git(repo, "rev-parse", "--verify", receipt_ref).decode().strip()
    receipt_fields = git(
        repo, "cat-file", "blob", receipt_oid
    ).decode("utf-8").rstrip("\n").split("\t")
    receipt_fields[7] = replacement_pointer_oid
    receipt_fields[8] = replacement_pointer["pointer_digest"]
    replacement_receipt_oid = object_id(
        repo, ("\t".join(receipt_fields) + "\n").encode("utf-8"))
    update_ref(repo, receipt_ref, replacement_receipt_oid)


expect_post_marker_rejection(
    "R0038-PM-STALE-GENESIS-RECEIPT", 169,
    stale_genesis_receipt, "$native.marker")
expect_post_marker_rejection(
    "R0038-PM-MARKER-REBOUND", 170,
    rebound_marker, "$native.marker")
expect_post_marker_rejection(
    "R0038-PM-IMMEDIATE-PREDECESSOR-MISMATCH", 171,
    mismatch_immediate_predecessor, "$native.pointer.predecessor")

predecessor_race_repo = prepare("positive", 101)
predecessor_race_module = load_module(predecessor_race_repo, 101)
original_predecessor = predecessor_race_module._native_predecessor


def drift_predecessor(*args, **kwargs):
    result = original_predecessor(*args, **kwargs)
    replacement = object_id(predecessor_race_repo, b"predecessor ref drift\n")
    update_ref(
        predecessor_race_repo,
        "refs/implementaudit/continuity-receipts/controller-current/G0001",
        replacement)
    return result


predecessor_race_module._native_predecessor = drift_predecessor
try:
    predecessor_race_module.collect_native_current()
except predecessor_race_module.OperationalEvidenceError:
    pass
else:
    red_failures.append("NCR35 predecessor-ref drift was accepted")

route_race_repo = prepare("positive", 102)
route_race_module = load_module(route_race_repo, 102)
original_route = route_race_module._native_route


def drift_route(*args, **kwargs):
    result = original_route(*args, **kwargs)
    replacement = object_id(route_race_repo, b"route ref drift\n")
    update_ref(
        route_race_repo,
        "refs/implementaudit/route-decisions/controller-current",
        replacement)
    return result


route_race_module._native_route = drift_route
try:
    route_race_module.collect_native_current()
except route_race_module.OperationalEvidenceError:
    pass
else:
    red_failures.append("NCR36 route-ref drift was accepted")

fake_compiler = b'''def compile_frontier_projection(raw):
    return {"population":4,"counts":{"DONE":1,"ACTIVE":1,"READY":1,"BLOCKED":1},
            "active":["RACE-ACTIVE"],"ready":["CELL-B"],"blocked_summary":{},
            "writer_holds":{"W_NATIVE_CURRENT":["CELL-A"]},"resource_holds":{},
            "digest":"0"*64}
'''
compiler_race_repo = prepare("positive", 103)
compiler_race_module = load_module(compiler_race_repo, 103)
compiler_race_path = (
    compiler_race_repo / "skills/implementaudit/scripts/compile-work-graph.py")
original_native_file = compiler_race_module._native_file
compiler_replaced = False


def replace_compiler_after_read(path, label, maximum=256 * 1024):
    global compiler_replaced
    raw = original_native_file(path, label, maximum)
    if path == compiler_race_path and not compiler_replaced:
        compiler_replaced = True
        path.write_bytes(fake_compiler)
    return raw


compiler_race_module._native_file = replace_compiler_after_read
try:
    compiler_race_module._native_graph_projection(
        (compiler_race_repo / ".IMPLEMENTAUDIT/runs/native-current-ABC123/WORK_GRAPH.json")
        .read_bytes())
except compiler_race_module.OperationalEvidenceError as exc:
    if exc.code != "OE_NATIVE_CURRENT_CHANGED":
        red_failures.append(
            f"NCR37 compiler pre-execution mutation returned {exc.code}")
else:
    red_failures.append("NCR37 compiler pre-execution mutation was accepted")

compiler_final_repo = prepare("positive", 104)
compiler_final_module = load_module(compiler_final_repo, 104)
compiler_final_path = (
    compiler_final_repo / "skills/implementaudit/scripts/compile-work-graph.py")
original_final_route = compiler_final_module._native_route


def replace_compiler_after_execution(*args, **kwargs):
    result = original_final_route(*args, **kwargs)
    compiler_final_path.write_bytes(fake_compiler)
    return result


compiler_final_module._native_route = replace_compiler_after_execution
try:
    compiler_final_module.collect_native_current()
except compiler_final_module.OperationalEvidenceError as exc:
    if exc.code != "OE_NATIVE_CURRENT_CHANGED":
        red_failures.append(
            f"NCR38 compiler post-execution mutation returned {exc.code}")
else:
    red_failures.append("NCR38 compiler post-execution mutation was accepted")


def expect_late_route_read_set_refusal(serial, label, mutate):
    repo = prepare("positive", serial)
    module = load_module(repo, serial)
    original_route = module._native_route
    mutated = False

    def mutate_after_route(*args, **kwargs):
        nonlocal mutated
        result = original_route(*args, **kwargs)
        if not mutated:
            mutate(repo)
            mutated = True
        return result

    module._native_route = mutate_after_route
    try:
        module.collect_native_current()
    except module.OperationalEvidenceError:
        pass
    else:
        red_failures.append(f"{label} was accepted")
    if not mutated:
        red_failures.append(f"{label} injection did not reach the post-route boundary")


expect_late_route_read_set_refusal(
    105, "NCR39 late R0033 request-input mutation",
    lambda repo: write(repo / "request-input.txt", b"late request mutation\n"))
expect_late_route_read_set_refusal(
    106, "NCR40 late R0033 executing-package mutation",
    lambda repo: write(
        repo / "skills/implementaudit/SKILL.md", b"late package mutation\n"))
expect_late_route_read_set_refusal(
    107, "NCR41 late R0033 audit-state child mutation",
    lambda repo: write(
        repo / "skills/audit-state/SKILL.md", b"late child mutation\n"))
expect_late_route_read_set_refusal(
    108, "NCR42 late R0033 tracked-member mutation",
    lambda repo: write(repo / "tracked.txt", b"late tracked mutation\n"))
expect_late_route_read_set_refusal(
    109, "NCR43 late R0033 Git-metadata mutation",
    lambda repo: git(repo, "config", "fixture.late-route-read-set", "changed"))


def expect_private_validator_substitution_contained(serial, name):
    repo = prepare("positive", serial)
    module = load_module(repo, serial)
    sentinel = repo / f"{name}.executed-sentinel"
    receipt_oid = git(
        repo, "rev-parse", "--verify",
        "refs/implementaudit/continuity-receipts/controller-current/G0002"
    ).decode().strip()
    receipt = (
        "refs/implementaudit/continuity-receipts/controller-current/G0002@" +
        receipt_oid)
    if name == "claim-run.sh":
        replacement = (
            "#!/usr/bin/env bash\n"
            f"printf 'replacement executed\\n' > '{sentinel.as_posix()}'\n"
            f"printf '%s\\n' '{receipt}'\n"
        ).encode()
        label = "NCR44 private claim-run child substitution"
    else:
        replacement = (
            "#!/usr/bin/env bash\n"
            f"printf 'replacement executed\\n' > '{sentinel.as_posix()}'\n"
            "exit 0\n"
        ).encode()
        label = "NCR45 private validate-run-root child substitution"
    before_refs = git(
        repo, "for-each-ref", "--format=%(refname)%00%(objectname)",
        "refs/implementaudit/")
    before_objects = git(repo, "count-objects", "-v")
    real_run = module.subprocess.run
    real_mkdtemp = module.tempfile.mkdtemp
    substituted = False
    closure = None

    def observe_private_closure(*args, **kwargs):
        nonlocal closure
        value = real_mkdtemp(*args, **kwargs)
        closure = pathlib.Path(value)
        return value

    def substitute_before_execution(command, *args, **kwargs):
        nonlocal substituted
        if (not substituted and isinstance(command, (list, tuple)) and
                "--require-current-continuity" in command):
            if closure is None:
                red_failures.append(
                    f"{label} did not expose its exact private closure")
                return real_run(command, *args, **kwargs)
            target = closure / name
            target.write_bytes(replacement)
            substituted = True
        return real_run(command, *args, **kwargs)

    module.tempfile.mkdtemp = observe_private_closure
    module.subprocess.run = substitute_before_execution
    try:
        try:
            module.collect_native_current()
        except module.OperationalEvidenceError:
            pass
        else:
            red_failures.append(f"{label} returned native-current facts")
    finally:
        module.tempfile.mkdtemp = real_mkdtemp
        module.subprocess.run = real_run
        if closure is not None and closure.exists():
            shutil.rmtree(closure)
    after_refs = git(
        repo, "for-each-ref", "--format=%(refname)%00%(objectname)",
        "refs/implementaudit/")
    after_objects = git(repo, "count-objects", "-v")
    if not substituted:
        red_failures.append(f"{label} did not reach the execution boundary")
    if sentinel.exists():
        red_failures.append(f"{label} executed replacement bytes")
    if before_refs != after_refs or before_objects != after_objects:
        red_failures.append(f"{label} changed protected refs or Git objects")


expect_private_validator_substitution_contained(110, "claim-run.sh")
expect_private_validator_substitution_contained(111, "validate-run-root.sh")


python_loader_repo = prepare("positive", 112)
python_loader_module = load_module(python_loader_repo, 112)
python_loader_root = CASE_ROOT / "python-loader-override"
python_loader_root.mkdir()
python_loader_sentinel = CASE_ROOT / "python-loader.executed-sentinel"
write(
    python_loader_root / "sitecustomize.py",
    ("from pathlib import Path\n"
     f"Path({str(python_loader_sentinel)!r}).write_text("
     "'loader executed\\n', encoding='utf-8')\n").encode())
old_pythonpath = os.environ.get("PYTHONPATH")
os.environ["PYTHONPATH"] = str(python_loader_root)
try:
    try:
        python_loader_module.collect_native_current()
    except python_loader_module.OperationalEvidenceError as exc:
        red_failures.append(
            f"NCR46 isolated child environment rejected the positive route: "
            f"{exc.receipt()}")
finally:
    if old_pythonpath is None:
        os.environ.pop("PYTHONPATH", None)
    else:
        os.environ["PYTHONPATH"] = old_pythonpath
if python_loader_sentinel.exists():
    red_failures.append("NCR46 inherited Python loader executed outside the closure")


controller_race_repo = prepare("positive", 113)
controller_race_module = load_module(controller_race_repo, 113)
original_controller_route = controller_race_module._native_route
controller_route_calls = 0
controller_replaced = False
controller_ref = "refs/implementaudit/controllers/controller-current"
controller_old_oid = git(
    controller_race_repo, "rev-parse", "--verify", controller_ref).decode().strip()
controller_record = git(
    controller_race_repo, "cat-file", "blob", controller_old_oid)
controller_new_oid = object_id(
    controller_race_repo, controller_record.rstrip(b"\n") + b"\n")
if controller_new_oid == controller_old_oid:
    controller_new_oid = object_id(
        controller_race_repo,
        controller_record.rstrip(b"\n") + b"\textra-field\n")


def replace_controller_before_final_route(*args, **kwargs):
    global controller_route_calls, controller_replaced
    controller_route_calls += 1
    if controller_route_calls == 2:
        update_ref(controller_race_repo, controller_ref, controller_new_oid)
        controller_replaced = True
    return original_controller_route(*args, **kwargs)


controller_race_module._native_route = replace_controller_before_final_route
try:
    controller_record_result = controller_race_module.collect_native_current()
except controller_race_module.OperationalEvidenceError:
    pass
else:
    if controller_record_result["controller"]["record_oid"] == controller_old_oid:
        red_failures.append(
            "NCR47 late current-controller replacement returned stale native facts")
if not controller_replaced:
    red_failures.append(
        "NCR47 late current-controller replacement did not reach the final route boundary")


cleanup_repo = prepare("positive", 114)
cleanup_module = load_module(cleanup_repo, 114)
cleanup_route_module, _, _ = cleanup_module._native_route_module()
cleanup_receipt_oid = git(
    cleanup_repo, "rev-parse", "--verify",
    "refs/implementaudit/continuity-receipts/controller-current/G0002"
).decode().strip()
cleanup_receipt = (
    "refs/implementaudit/continuity-receipts/controller-current/G0002@" +
    cleanup_receipt_oid)
real_mkdtemp = cleanup_module.tempfile.mkdtemp
real_unlink = cleanup_module.os.unlink
real_cleanup_run = cleanup_module.subprocess.run
cleanup_closure = None
cleanup_armed = False
cleanup_refused = False


def observe_private_closure(*args, **kwargs):
    global cleanup_closure
    value = real_mkdtemp(*args, **kwargs)
    cleanup_closure = pathlib.Path(value)
    return value


def arm_cleanup_after_child(command, *args, **kwargs):
    global cleanup_armed
    completed = real_cleanup_run(command, *args, **kwargs)
    if (isinstance(command, (list, tuple)) and
            "--require-current-continuity" in command):
        cleanup_armed = True
    return completed


def refuse_exact_cleanup(path, *args, **kwargs):
    global cleanup_refused
    if (cleanup_armed and pathlib.Path(os.fspath(path)).name == "claim-run.sh"):
        cleanup_refused = True
        raise PermissionError("injected exact private cleanup refusal")
    return real_unlink(path, *args, **kwargs)


cleanup_module.tempfile.mkdtemp = observe_private_closure
cleanup_module.subprocess.run = arm_cleanup_after_child
cleanup_module.os.unlink = refuse_exact_cleanup
cleanup_error = None
try:
    try:
        cleanup_module._native_require_current_receipt(
            cleanup_repo, "controller-current", cleanup_receipt,
            cleanup_route_module)
    except cleanup_module.OperationalEvidenceError as exc:
        cleanup_error = exc
finally:
    cleanup_module.tempfile.mkdtemp = real_mkdtemp
    cleanup_module.subprocess.run = real_cleanup_run
    cleanup_module.os.unlink = real_unlink
if cleanup_closure is None:
    red_failures.append("NCR48 cleanup refusal did not observe the private closure")
else:
    expected_residue = sorted(str(path) for path in (
        cleanup_closure,
        cleanup_closure / "claim-run.sh",
        cleanup_closure / "validate-run-root.sh",
    ))
    expected_cleanup_message = (
        "private R0011 closure cleanup refused; residue=" +
        json.dumps(expected_residue, sort_keys=True, separators=(",", ":")) +
        "; manual reconciliation required")
    if (cleanup_error is None or cleanup_error.code != "OE_NATIVE_CURRENT_CLEANUP" or
            cleanup_error.path != "$native.private_continuity_closure" or
            cleanup_error.message != expected_cleanup_message):
        red_failures.append(
            "NCR48 cleanup refusal lacked exact residue/manual-reconciliation evidence")
    if not all(pathlib.Path(path).exists() for path in expected_residue):
        red_failures.append("NCR48 cleanup refusal did not preserve exact bounded residue")
    if cleanup_closure.exists():
        shutil.rmtree(cleanup_closure)
if not cleanup_refused:
    red_failures.append("NCR48 cleanup refusal did not reach the exact cleanup boundary")

if red_failures:
    for label in red_failures:
        print(f"{label} RED", file=sys.stderr)
    raise SystemExit(1)

before_refs = git(
    positive_repo, "for-each-ref", "--format=%(refname)%00%(objectname)",
    "refs/implementaudit/")
before_objects = git(positive_repo, "count-objects", "-v")
record = positive_module.collect_native_current()
repeat = positive_module.collect_native_current()
after_refs = git(
    positive_repo, "for-each-ref", "--format=%(refname)%00%(objectname)",
    "refs/implementaudit/")
after_objects = git(positive_repo, "count-objects", "-v")
if before_refs != after_refs or before_objects != after_objects:
    raise SystemExit("native-current read changed protected refs or Git objects")
if (positive_repo / ".IMPLEMENTAUDIT/runs/native-current-ABC123/operational-evidence").exists():
    raise SystemExit("C03 created a snapshot/publication root")
if record != repeat or positive_module.canonical_json_v1(record) != positive_module.canonical_json_v1(repeat):
    raise SystemExit("native-current facts are not deterministic")
if record.get("schema") != "implementaudit-native-current-facts-v1":
    raise SystemExit("native-current fact schema missing")
if record.get("authority_ceiling") != "READ_ONLY_NATIVE_CURRENT_FACT":
    raise SystemExit("native-current authority ceiling drift")
if record.get("frontier", {}).get("active") != ["CELL-A"]:
    raise SystemExit("WORK_GRAPH ACTIVE projection was overridden by adjacent narrative")
if record.get("frontier", {}).get("ready") != ["CELL-B"]:
    raise SystemExit("WORK_GRAPH READY projection was overridden by adjacent narrative")
if record.get("frontier", {}).get("writer_holds") != {
        "W_NATIVE_CURRENT": ["CELL-A", "CELL-B"]}:
    raise SystemExit("declared writer holds were not retained")
if record.get("open_andons") != ["V041_RELEASE_BLOCK"]:
    raise SystemExit("open Andon fact missing")
if [row.get("id") for row in record.get("active_instructions", [])] != ["i01"]:
    raise SystemExit("active instruction fact missing")
if record.get("continuity", {}).get("receipt_schema") != "implementaudit.continuity-receipt.v3":
    raise SystemExit("receipt-v3 fact missing")
if record.get("route", {}).get("record_identity") is None:
    raise SystemExit("R0033 route identity missing")
if b"activegraph" in positive_module.canonical_json_v1(record).lower():
    raise SystemExit("ActiveGraph mirror entered native-current input or authority")
semantic = record.get("semantic_sha256")
without_semantic = {key: value for key, value in record.items() if key != "semantic_sha256"}
if semantic != hashlib.sha256(positive_module.canonical_json_v1(without_semantic)).hexdigest():
    raise SystemExit("native-current semantic digest mismatch")

snapshot_repo = prepare("positive", 200)
snapshot_module = load_module(snapshot_repo, 200)
if list(inspect.signature(snapshot_module.publish_current_snapshot).parameters):
    raise SystemExit("C06-R09 publisher accepts caller-supplied authority")
snapshot_native = snapshot_module.collect_native_current()
snapshot_run = snapshot_repo / ".IMPLEMENTAUDIT/runs/native-current-ABC123"
snapshot_root = snapshot_run / "operational-evidence/snapshots"

rotation_spec = importlib.util.spec_from_file_location(
    "rotation_c06_consumer", ROTATION)
rotation = importlib.util.module_from_spec(rotation_spec)
sys.modules[rotation_spec.name] = rotation
rotation_spec.loader.exec_module(rotation)
consumer_args = {
    "run_root": snapshot_run,
    "pointer_oid": snapshot_native["continuity"]["pointer_oid"],
    "controller_id": snapshot_native["controller"]["id"],
    "claim_id": snapshot_native["claim"]["id"],
    "run_id": snapshot_native["claim"]["run_id"],
    "source_epoch": snapshot_native["continuity"]["source_epoch"],
}
try:
    rotation.load_exact_r0038_current_snapshot_manifest_v1(**consumer_args)
except rotation.RotationError as exc:
    if str(exc) != "OE_R0038_SNAPSHOT_NOT_PUBLISHED":
        raise SystemExit(f"C06-R10 pre-publication consumer returned {exc}")
else:
    raise SystemExit("C06-R10 consumer found a snapshot before publication")

original_external_get = snapshot_module._native_external_get
def forbidden_external_get(*args, **kwargs):
    raise SystemExit("C06-R15 snapshot publisher attempted network")
snapshot_module._native_external_get = forbidden_external_get
try:
    publication = snapshot_module.publish_current_snapshot()
finally:
    snapshot_module._native_external_get = original_external_get
if (publication.get("schema") !=
        "implementaudit-operational-snapshot-publication-v1" or
        publication.get("selection_state") != "ADVANCED" or
        publication.get("aggregate") != "DEGRADED" or
        publication.get("authority_ceiling") != "R0038_OUTPUT_ROOT_ONLY" or
        publication.get("establishes") != []):
    raise SystemExit("C06 publication receipt is malformed or over-authoritative")
snapshot_id = publication["snapshot_id"]
snapshot_dir = snapshot_root / snapshot_id
input_raw = (snapshot_dir / "input-manifest.json").read_bytes()
payload_raw = (snapshot_dir / "snapshot.json").read_bytes()
manifest_raw = (snapshot_dir / "manifest.json").read_bytes()
current_raw = (snapshot_root / "CURRENT").read_bytes()
if any(raw.endswith(b"\n") for raw in (input_raw, payload_raw, manifest_raw, current_raw)):
    raise SystemExit("C06 canonical snapshot bytes retained terminal LF")
input_manifest = json.loads(input_raw)
payload = json.loads(payload_raw)
manifest = json.loads(manifest_raw)
current = json.loads(current_raw)
if snapshot_id != "iasnap-v1-" + hashlib.sha256(input_raw).hexdigest():
    raise SystemExit("C06 snapshot identity is not the canonical input-manifest digest")
if set(manifest) != {
        "schema_version", "controller_id", "claim_id", "run_id", "source_epoch",
        "source_pointer_oid", "source_evidence_entries"}:
    raise SystemExit("C06 manifest key set drifted from the frozen R39 consumer")
if set(current) != {
        "schema_version", "snapshot_id", "manifest_sha256", "source_pointer_oid"}:
    raise SystemExit("C06 CURRENT key set drifted from the frozen R39 consumer")
if (current["manifest_sha256"] != hashlib.sha256(manifest_raw).hexdigest() or
        current["snapshot_id"] != snapshot_id or
        current["source_pointer_oid"] != snapshot_native["continuity"]["pointer_oid"]):
    raise SystemExit("C06 CURRENT does not bind the exact immutable manifest")
if (payload.get("aggregate") != "DEGRADED" or
        {row.get("collector") for row in payload.get("missing_or_omitted_state", [])}
        < {"evidence_failure", "release"}):
    raise SystemExit("C06-R05 DEGRADED snapshot lost its complete missing census")
if input_manifest.get("missing_or_omitted_state") != payload.get(
        "missing_or_omitted_state"):
    raise SystemExit("C06 input manifest and payload missing censuses disagree")

original_collections = snapshot_module._collect_snapshot_inputs_v1(snapshot_native)
variant_native = copy.deepcopy(snapshot_native)
original_repo_root = pathlib.Path(snapshot_native["repository"]["root"])
original_common = pathlib.Path(snapshot_native["repository"]["git_common_dir"])
original_run = original_repo_root / pathlib.PurePosixPath(
    snapshot_native["claim"]["run_root"])
variant_repo_root = CASE_ROOT / "different-absolute-envelope/repository"
variant_common = CASE_ROOT / "different-absolute-envelope/common.git"
variant_run = variant_repo_root / pathlib.PurePosixPath(
    snapshot_native["claim"]["run_root"])
replacements = {
    str(original_repo_root): str(variant_repo_root),
    original_repo_root.as_posix(): variant_repo_root.as_posix(),
    str(original_common): str(variant_common),
    original_common.as_posix(): variant_common.as_posix(),
    str(original_run): str(variant_run),
    original_run.as_posix(): variant_run.as_posix(),
}
def replace_envelope(value):
    if isinstance(value, dict):
        return {key: replace_envelope(item) for key, item in value.items()}
    if isinstance(value, list):
        return [replace_envelope(item) for item in value]
    if isinstance(value, str):
        return replacements.get(value, value)
    return value
variant_native = replace_envelope(variant_native)
variant_collections = copy.deepcopy(original_collections)
variant_collections["native_current"]["value"] = (
    snapshot_module._snapshot_portable_native_v1(variant_native))
variant_collections["native_current"]["sha256"] = hashlib.sha256(
    snapshot_module.canonical_json_v1(
        variant_collections["native_current"]["value"])).hexdigest()
compiler_raw = (snapshot_repo /
    "skills/implementaudit/scripts/operational-evidence.py").read_bytes()
schema_raw = (snapshot_repo /
    "skills/implementaudit/references/operational-evidence-schema.json").read_bytes()
original_material = snapshot_module._build_snapshot_material_v1(
    snapshot_native, original_collections, schema_raw, compiler_raw)
variant_material = snapshot_module._build_snapshot_material_v1(
    variant_native, variant_collections, schema_raw, compiler_raw)
materialized_payload = json.loads(original_material["payload_raw"].decode("utf-8"))
materialized_diff = snapshot_module.diff_snapshots(
    materialized_payload, copy.deepcopy(materialized_payload))
if (materialized_diff["added"] or materialized_diff["removed"] or
        materialized_diff["changed"]):
    raise SystemExit("C08-R2 exact producer payload did not yield an empty diff")
for key in ("snapshot_id", "input_raw", "payload_raw", "manifest_raw", "current_raw"):
    if original_material[key] != variant_material[key]:
        raise SystemExit(f"C06-R04 volatile absolute envelope changed {key}")

owner_manifest = rotation.load_exact_r0038_current_snapshot_manifest_v1(
    **consumer_args)
if owner_manifest != {"entries": manifest["source_evidence_entries"]}:
    raise SystemExit("C06-R10 unchanged R39 consumer did not resolve exact entries")
evidence_id = publication["source_evidence_ids"][0]
if rotation.load_immutable_r0038_snapshot_for_evidence_id_v1(
        run_root=snapshot_run,
        controller_id=snapshot_native["controller"]["id"],
        claim_id=snapshot_native["claim"]["id"],
        run_id=snapshot_native["claim"]["run_id"],
        source_epoch=snapshot_native["continuity"]["source_epoch"],
        source_evidence_id=evidence_id) != owner_manifest:
    raise SystemExit("C06-R10 stored snapshot did not re-resolve by immutable identity")

repeat_publication = snapshot_module.publish_current_snapshot()
if (repeat_publication["snapshot_id"] != snapshot_id or
        repeat_publication["selection_state"] != "UNCHANGED" or
        (snapshot_dir / "input-manifest.json").read_bytes() != input_raw or
        (snapshot_dir / "snapshot.json").read_bytes() != payload_raw or
        (snapshot_dir / "manifest.json").read_bytes() != manifest_raw):
    raise SystemExit("C06 identical publication was not deterministic and immutable")

lock_common = pathlib.Path(git(
    snapshot_repo, "rev-parse", "--path-format=absolute", "--git-common-dir"
).decode().strip())
writer_lock = lock_common / "implementaudit-r0038-snapshot-writer.lock"
writer_lock.mkdir()
try:
    try:
        snapshot_module.publish_current_snapshot()
    except snapshot_module.OperationalEvidenceError as exc:
        if exc.code != "OE_SNAPSHOT_WRITER_BUSY":
            raise SystemExit(f"C06-R08 writer loser returned {exc.code}")
    else:
        raise SystemExit("C06-R08 concurrent writer was admitted")
finally:
    writer_lock.rmdir()
if (snapshot_root / "CURRENT").read_bytes() != current_raw:
    raise SystemExit("C06-R08 writer loser changed the winner selection")

drift_repo = prepare("positive", 201)
drift_module = load_module(drift_repo, 201)
drift_state = drift_repo / ".IMPLEMENTAUDIT/runs/native-current-ABC123/STATE.md"
drift_original = drift_state.read_bytes()
def drift_after_observation(stage):
    if stage == "after-first-observation":
        drift_state.write_bytes(drift_original + b"\nlate drift\n")
drift_module._snapshot_stage_v1 = drift_after_observation
try:
    drift_module.publish_current_snapshot()
except drift_module.OperationalEvidenceError:
    pass
else:
    raise SystemExit("C06-H01 final input fence accepted late hot-state drift")
if (drift_repo / ".IMPLEMENTAUDIT/runs/native-current-ABC123/operational-evidence").exists():
    raise SystemExit("C06-H01 late drift created publication output")

correction_red_failures = []
late_stages = (
    "after-manifest-reread", "before-current-temp", "after-current-temp",
    "before-current-replace")
late_inputs = (
    "compiler", "schema", "native", "route", "graph", "repository",
    "evidence_failure", "release")


late_repo = prepare("positive", 500)
late_module = load_module(late_repo, 500)
late_native = late_module.collect_native_current()
late_collections = late_module._collect_snapshot_inputs_v1(late_native)
late_run = late_repo / ".IMPLEMENTAUDIT/runs/native-current-ABC123"
late_output = late_run / "operational-evidence"
late_current = late_output / "snapshots/CURRENT"
late_compiler_path = (
    late_repo / "skills/implementaudit/scripts/operational-evidence.py")
late_schema_path = (
    late_repo / "skills/implementaudit/references/operational-evidence-schema.json")
late_compiler_raw = late_compiler_path.read_bytes()
late_schema_raw = late_schema_path.read_bytes()


def late_observation_variant(input_name):
    native = copy.deepcopy(late_native)
    collections = copy.deepcopy(late_collections)
    if input_name == "native":
        native["hot"]["state_sha256"] = ZERO64
    elif input_name == "route":
        native["route"]["record_identity"] = "sha256:" + ZERO64
    elif input_name == "graph":
        native["hot"]["work_graph_sha256"] = ZERO64
    elif input_name in {"repository", "evidence_failure", "release"}:
        collections[input_name]["value"]["late_test_probe"] = input_name
        collections[input_name]["sha256"] = hashlib.sha256(
            late_module.canonical_json_v1(
                collections[input_name]["value"])).hexdigest()
    return native, collections


for late_stage, late_input in (
        (stage, input_name) for stage in late_stages for input_name in late_inputs):
    if late_output.exists():
        shutil.rmtree(late_output)
    mutation = {"done": False}
    final_native, final_collections = late_observation_variant(late_input)

    def observed_native(state=mutation, final=final_native):
        return copy.deepcopy(final if state["done"] else late_native)

    def observed_collections(native, state=mutation, final=final_collections):
        del native
        return copy.deepcopy(final if state["done"] else late_collections)

    def mutate_at_late_stage(stage, expected=late_stage, name=late_input,
                             state=mutation):
        if stage != expected or state["done"]:
            return
        if name == "compiler":
            late_compiler_path.write_bytes(
                late_compiler_raw + b"\n# late compiler drift\n")
        elif name == "schema":
            late_schema_path.write_bytes(late_schema_raw + b"\n")
        state["done"] = True

    late_module.collect_native_current = observed_native
    late_module._collect_snapshot_inputs_v1 = observed_collections
    late_module._snapshot_stage_v1 = mutate_at_late_stage
    try:
        try:
            late_receipt = late_module.publish_current_snapshot()
        except late_module.OperationalEvidenceError:
            late_receipt = None
        except Exception as exc:
            correction_red_failures.append(
                f"C06-C1 {late_stage}/{late_input} returned untyped "
                f"{type(exc).__name__}")
            late_receipt = None
    finally:
        late_compiler_path.write_bytes(late_compiler_raw)
        late_schema_path.write_bytes(late_schema_raw)
    if not mutation["done"]:
        correction_red_failures.append(
            f"C06-C1 {late_stage}/{late_input} did not reach its callback")
    if late_receipt is not None:
        correction_red_failures.append(
            f"C06-C1 {late_stage}/{late_input} returned success "
            f"{late_receipt.get('selection_state')}")
    if late_current.exists() or late_current.is_symlink():
        correction_red_failures.append(
            f"C06-C1 {late_stage}/{late_input} advanced CURRENT")

census_repo = prepare(
    "positive", 550, include_c04=True, include_c05=True)
census_module = load_module(census_repo, 550)
census_native = census_module.collect_native_current()
census_collections = census_module._collect_snapshot_inputs_v1(census_native)
census_compiler_raw = (
    census_repo / "skills/implementaudit/scripts/operational-evidence.py").read_bytes()
census_schema_raw = (
    census_repo / "skills/implementaudit/references/operational-evidence-schema.json"
).read_bytes()
c08_r3_material = census_module._build_snapshot_material_v1(
    census_native, census_collections, census_schema_raw, census_compiler_raw)
c08_r3_payload = json.loads(c08_r3_material["payload_raw"].decode("utf-8"))
c08_r3_positive = census_module.diff_snapshots(
    c08_r3_payload, copy.deepcopy(c08_r3_payload))
if (c08_r3_positive["added"] or c08_r3_positive["removed"] or
        c08_r3_positive["changed"]):
    correction_red_failures.append(
        "C08-R3-C1 genuine producer payload did not yield an empty diff")


def c08_r3_refresh_payload(payload, preserve_semantic=None):
    """Refresh every enclosing producer digest after one hostile mutation."""
    for name, collection in payload["collections"].items():
        value = collection["value"]
        if (collection["state"] == "CURRENT" and isinstance(value, dict) and
                "semantic_sha256" in value and
                preserve_semantic != (name, "semantic_sha256")):
            semantic = {
                key: item for key, item in value.items()
                if key != "semantic_sha256"}
            value["semantic_sha256"] = hashlib.sha256(
                census_module.canonical_json_v1(semantic)).hexdigest()
        collection["sha256"] = hashlib.sha256(
            census_module.canonical_json_v1(value)).hexdigest()


def c08_r3_value(payload, actual_path):
    collection = payload["collections"][actual_path[0]]["value"]
    value = collection
    for part in actual_path[1:]:
        value = value[part]
    return value


def c08_r3_parent(payload, actual_path):
    parent = c08_r3_value(payload, actual_path[:-1])
    return parent, actual_path[-1]


def c08_r3_discriminator(value, index):
    if isinstance(value, dict):
        for key in ("record_type", "kind", "capability", "id"):
            if isinstance(value.get(key), str) and value[key]:
                return value[key]
    return str(index)


def c08_r3_schema_nodes():
    """Select one genuine producer node for every named structural branch."""
    nodes = {}

    def visit(value, actual_path, display_path):
        kind = type(value).__name__
        nodes.setdefault((display_path, kind), (actual_path, value))
        if isinstance(value, dict):
            for key in sorted(value):
                visit(value[key], actual_path + (key,), f"{display_path}.{key}")
        elif isinstance(value, list):
            for index, item in enumerate(value):
                discriminator = c08_r3_discriminator(item, index)
                visit(item, actual_path + (index,),
                      f"{display_path}[{discriminator}]")

    for name in sorted(c08_r3_payload["collections"]):
        visit(c08_r3_payload["collections"][name]["value"], (name,), name)
    return list(nodes.values())


def c08_r3_expect_invalid(label, payload):
    try:
        census_module.diff_snapshots(c08_r3_payload, payload)
    except census_module.OperationalEvidenceError as exc:
        if exc.code != "OE_DIFF_SNAPSHOT_INVALID":
            correction_red_failures.append(
                f"C08-R3-C1 {label} returned {exc.code}")
    except Exception as exc:
        correction_red_failures.append(
            f"C08-R3-C1 {label} leaked {type(exc).__name__}")
    else:
        correction_red_failures.append(
            f"C08-R3-C1 {label} returned success-shaped diff")


# Generated closed-grammar matrix. Each operator is applied to one genuine
# instance of every named producer branch/variant. Enclosing semantic and
# collection digests are maliciously refreshed so an outer checksum cannot be
# the discriminator.
for actual_path, original in c08_r3_schema_nodes():
    label = ".".join(str(part) for part in actual_path)
    if isinstance(original, dict):
        dynamic_map = actual_path[-2:] in (
            ("frontier", "blocked_summary"),
            ("frontier", "writer_holds"),
            ("frontier", "resource_holds"))
        mutated = copy.deepcopy(c08_r3_payload)
        c08_r3_value(mutated, actual_path)["__foreign_branch__"] = {
            "foreign": "member"}
        c08_r3_refresh_payload(mutated)
        c08_r3_expect_invalid(f"{label}:extra-key", mutated)
        for key in (() if dynamic_map else sorted(original)):
            mutated = copy.deepcopy(c08_r3_payload)
            del c08_r3_value(mutated, actual_path)[key]
            if key == "semantic_sha256":
                c08_r3_refresh_payload(
                    mutated, preserve_semantic=(actual_path[0], key))
            else:
                c08_r3_refresh_payload(mutated)
            c08_r3_expect_invalid(f"{label}:missing-{key}", mutated)
    elif isinstance(original, list):
        mutated = copy.deepcopy(c08_r3_payload)
        parent, key = c08_r3_parent(mutated, actual_path)
        parent[key] = {"foreign": "array-type"}
        c08_r3_refresh_payload(mutated)
        c08_r3_expect_invalid(f"{label}:wrong-array-type", mutated)

        mutated = copy.deepcopy(c08_r3_payload)
        c08_r3_value(mutated, actual_path).append({"foreign": "array-member"})
        c08_r3_refresh_payload(mutated)
        c08_r3_expect_invalid(f"{label}:foreign-array-member", mutated)
    else:
        mutated = copy.deepcopy(c08_r3_payload)
        parent, key = c08_r3_parent(mutated, actual_path)
        if type(original) is bool:
            parent[key] = 0
        elif type(original) is int:
            parent[key] = True
        elif original is None:
            parent[key] = "foreign-null"
        elif type(original) is str:
            parent[key] = {"foreign": "scalar-type"}
        else:
            parent[key] = {"foreign": "scalar-type"}
        preserve = ((actual_path[0], "semantic_sha256")
                    if actual_path[-1] == "semantic_sha256" else None)
        c08_r3_refresh_payload(mutated, preserve_semantic=preserve)
        c08_r3_expect_invalid(f"{label}:wrong-scalar-type", mutated)
        if type(original) is str and original:
            mutated = copy.deepcopy(c08_r3_payload)
            parent, key = c08_r3_parent(mutated, actual_path)
            parent[key] = ""
            c08_r3_refresh_payload(mutated, preserve_semantic=preserve)
            c08_r3_expect_invalid(f"{label}:empty-text", mutated)
            if actual_path[-1] in {
                    "state", "record_type", "family", "layer", "leg",
                    "result_class", "cause_confidence", "recovery_state",
                    "worktree_state", "file_type", "language", "auth_state",
                    "rate_state", "pagination_state", "decision", "route_state"}:
                mutated = copy.deepcopy(c08_r3_payload)
                parent, key = c08_r3_parent(mutated, actual_path)
                parent[key] = "__FOREIGN_ENUM__"
                c08_r3_refresh_payload(mutated, preserve_semantic=preserve)
                c08_r3_expect_invalid(f"{label}:foreign-enum", mutated)


def c08_r3_named_mutation(label, action):
    mutated = copy.deepcopy(c08_r3_payload)
    action(mutated)
    c08_r3_refresh_payload(mutated)
    c08_r3_expect_invalid(label, mutated)


def c08_r3_repo_foreign_fact(payload):
    payload["collections"]["repository"]["value"]["facts"].append(
        {"foreign": "member"})


def c08_r3_native_foreign_repository_key(payload):
    payload["collections"]["native_current"]["value"]["repository"][
        "foreign"] = "member"


def c08_r3_release_ill_typed_object(payload):
    node = next(row for row in payload["collections"]["release"]["value"][
        "nodes"] if row["record_type"] == "Commit")
    node["object_identity"] = {"foreign": "object"}


def c08_r3_duplicate_identity(payload):
    records = payload["collections"]["evidence_failure"]["value"][
        "evidence_records"]
    records[1]["id"] = records[0]["id"]


def c08_r3_duplicate_sequence(payload):
    records = payload["collections"]["evidence_failure"]["value"][
        "evidence_records"]
    records[1]["sequence"] = records[0]["sequence"]


def c08_r3_bad_layer_census(payload):
    payload["collections"]["evidence_failure"]["value"]["layer_census"][
        "EFFECT"] += 1


def c08_r3_bad_release_census(payload):
    payload["collections"]["release"]["value"]["node_type_census"][
        "Commit"] += 1


def c08_r3_bad_currentness(payload):
    record = payload["collections"]["evidence_failure"]["value"][
        "evidence_records"][0]
    record["currentness"] = {"state": "CURRENT", "invalidators": ["FOREIGN"]}


for label, action in (
        ("repository-foreign-fact", c08_r3_repo_foreign_fact),
        ("native-foreign-repository-key", c08_r3_native_foreign_repository_key),
        ("release-ill-typed-object", c08_r3_release_ill_typed_object),
        ("duplicate-record-identity", c08_r3_duplicate_identity),
        ("duplicate-record-sequence", c08_r3_duplicate_sequence),
        ("evidence-layer-census", c08_r3_bad_layer_census),
        ("release-node-type-census", c08_r3_bad_release_census),
        ("CURRENT-with-invalidator", c08_r3_bad_currentness)):
    c08_r3_named_mutation(label, action)


# Derive the unique-list operator population from genuine producer validation,
# not from the C08 parser or its hand-selected field model.  Any new producer
# unique-list call changes this census before it can silently escape the diff
# grammar.
c08_r4_unique_paths = []
c08_r4_original_string_list = census_module._string_list


def c08_r4_observe_unique_list(value, path, *, allowed=None, unique=True):
    if unique and path.startswith("$run_artifact"):
        c08_r4_unique_paths.append(path)
    return c08_r4_original_string_list(
        value, path, allowed=allowed, unique=unique)


census_module._string_list = c08_r4_observe_unique_list
try:
    census_module._collect_snapshot_inputs_v1(census_native)
finally:
    census_module._string_list = c08_r4_original_string_list


def c08_r4_unique_operator(path):
    if path.endswith(".currentness.invalidators"):
        return "currentness.invalidators"
    return path.rsplit(".", 1)[-1]


c08_r4_unique_operators = {
    c08_r4_unique_operator(path) for path in c08_r4_unique_paths}
c08_r4_expected_unique_operators = {
    "currentness.invalidators", "controls", "contrary_evidence",
    "evidence_ids", "residual_ids"}
if c08_r4_unique_operators != c08_r4_expected_unique_operators:
    correction_red_failures.append(
        "C08-R4-C1 producer unique-list census differs: "
        f"observed={sorted(c08_r4_unique_operators)} "
        f"expected={sorted(c08_r4_expected_unique_operators)}")


def c08_r4_duplicate_unique_operator(payload, operator):
    evidence = payload["collections"]["evidence_failure"]["value"]
    records = evidence["evidence_records"]
    failures = evidence["failure_records"]
    if operator == "controls":
        records[0]["controls"] = ["PARITY_CONTROL", "PARITY_CONTROL"]
    elif operator == "contrary_evidence":
        records[0]["contrary_evidence"] = [records[0]["id"], records[0]["id"]]
    elif operator == "evidence_ids":
        reference = records[0]["id"]
        failures[0]["evidence_ids"] = [reference, reference]
    elif operator == "residual_ids":
        residual = next(
            row["id"] for row in failures if row["record_type"] == "Residual")
        evidence["residual_ids"] = [residual, residual]
    else:
        populations = (records, failures,
                       payload["collections"]["release"]["value"]["nodes"])
        currentness = next(
            row["currentness"] for population in populations for row in population)
        currentness["invalidators"] = [
            "PARITY_INVALIDATOR", "PARITY_INVALIDATOR"]


for operator in sorted(c08_r4_expected_unique_operators):
    c08_r3_named_mutation(
        f"producer-unique-list:{operator}",
        lambda payload, selected=operator:
        c08_r4_duplicate_unique_operator(payload, selected))


# The staged publication contract is finite and observable at named phases.
# On the rejected destination-direct mechanism none of these phases exists;
# the matrix must therefore RED before any production mechanism replacement.
c08_r4_capability_check = getattr(
    census_module, "_snapshot_hardlink_publication_capable_v1", None)
if c08_r4_capability_check is not None:
    census_module._snapshot_hardlink_publication_capable_v1 = (
        lambda _kernel, _handle: True)
c08_r3_export_root = CASE_ROOT / "c08-r3-export-matrix"
c08_r3_export_root.mkdir()
c08_r3_phases = (
    "stage-created", "write-complete", "fsync-complete",
    "readback-start", "readback-eof", "before-publish")
c08_r3_topologies = (
    "same-inode-same-size", "same-inode-size-change",
    "unlink-recreate", "link-swap", "destination-occupation")
for phase in c08_r3_phases:
    for topology in c08_r3_topologies:
        case_root = c08_r3_export_root / f"{phase}-{topology}"
        case_root.mkdir()
        destination = case_root / "snapshot.json"
        alias = case_root / "stage-alias"
        phase_seen = False
        mutation_succeeded = False
        mutation_excluded = False
        original_stage = census_module._snapshot_stage_v1

        def mutate_at_phase(observed_phase, *, expected=phase, kind=topology):
            global phase_seen, mutation_succeeded, mutation_excluded
            if observed_phase != expected:
                return
            phase_seen = True
            stage_paths = [
                path for path in case_root.iterdir()
                if path not in (destination, alias)]
            try:
                if kind == "destination-occupation":
                    destination.write_bytes(b"foreign-destination")
                elif not stage_paths:
                    return
                elif kind == "same-inode-same-size":
                    with stage_paths[0].open("r+b") as stream:
                        observed = stream.read()
                        stream.seek(0)
                        stream.write(b"X" * len(observed) if observed else b"X")
                        stream.flush()
                        os.fsync(stream.fileno())
                elif kind == "same-inode-size-change":
                    with stage_paths[0].open("ab") as stream:
                        stream.write(b"X")
                        stream.flush()
                        os.fsync(stream.fileno())
                elif kind == "unlink-recreate":
                    stage_paths[0].unlink()
                    stage_paths[0].write_bytes(b"foreign-stage")
                else:
                    os.link(stage_paths[0], alias)
                mutation_succeeded = True
            except OSError:
                mutation_excluded = True

        census_module._snapshot_stage_v1 = mutate_at_phase
        receipt = None
        error = None
        try:
            try:
                receipt = census_module.export_snapshot(
                    c08_r3_payload, destination, owned_root=case_root,
                    output_format="json")
            except census_module.OperationalEvidenceError as exc:
                error = exc
        finally:
            census_module._snapshot_stage_v1 = original_stage
        label = f"{phase}/{topology}"
        if not phase_seen:
            correction_red_failures.append(
                f"C08-R3-C2 {label} did not reach the staged transaction phase")
        elif topology == "destination-occupation":
            if (not mutation_succeeded or error is None or
                    error.code != "OE_EXPORT_DESTINATION_EXISTS" or
                    destination.read_bytes() != b"foreign-destination"):
                correction_red_failures.append(
                    f"C08-R3-C2 {label} overwrote or misclassified foreign occupancy")
        elif mutation_succeeded:
            if error is None or error.code != "OE_EXPORT_WRITE_FAILED" or receipt:
                correction_red_failures.append(
                    f"C08-R3-C2 {label} mutation returned success-shaped receipt")
        elif mutation_excluded:
            if (receipt is None or error is not None or
                    destination.read_bytes() !=
                    census_module.canonical_json_v1(c08_r3_payload)):
                correction_red_failures.append(
                    f"C08-R3-C2 {label} excluded mutation lost the positive export")

if os.name == "nt":
    if not hasattr(census_module, "_snapshot_atomic_no_replace_v1"):
        correction_red_failures.append(
            "C08-R3-C2 after-publication live-handle exclusion is absent")
    else:
        after_root = c08_r3_export_root / "after-publication"
        after_root.mkdir()
        after_destination = after_root / "snapshot.json"
        original_publish = census_module._snapshot_atomic_no_replace_v1
        after_attack_excluded = False

        def publish_then_attack(handle, target):
            global after_attack_excluded
            result = original_publish(handle, target)
            try:
                with pathlib.Path(target).open("r+b") as stream:
                    stream.write(b"X")
                    stream.flush()
                    os.fsync(stream.fileno())
            except OSError:
                after_attack_excluded = True
            return result

        census_module._snapshot_atomic_no_replace_v1 = publish_then_attack
        try:
            after_receipt = census_module.export_snapshot(
                c08_r3_payload, after_destination, owned_root=after_root,
                output_format="json")
        finally:
            census_module._snapshot_atomic_no_replace_v1 = original_publish
        if (not after_attack_excluded or
                after_destination.read_bytes() !=
                census_module.canonical_json_v1(c08_r3_payload) or
                after_receipt["output_sha256"] != hashlib.sha256(
                    after_destination.read_bytes()).hexdigest()):
            correction_red_failures.append(
                "C08-R3-C2 post-publication write was not excluded by live handle")

    if c08_r4_capability_check is not None:
        census_module._snapshot_hardlink_publication_capable_v1 = (
            c08_r4_capability_check)

    # These two cells are derived from native operation edges, not the
    # production hook population.  They reproduce hard-link creation between
    # the final handle observation and FileRenameInfo, and immediately after
    # the atomic rename while the transaction handle is still live.
    late_root = c08_r3_export_root / "native-late-hardlink"
    late_root.mkdir()
    late_destination = late_root / "snapshot.json"
    late_alias = late_root / "late-alias"
    original_publish = census_module._snapshot_atomic_no_replace_v1
    late_edge_reached = False
    late_link_created = False

    def attack_before_native_rename(handle, target):
        global late_edge_reached, late_link_created
        late_edge_reached = True
        stage = next(
            path for path in late_root.iterdir()
            if path != late_destination and
            path.name.endswith(".implementaudit-stage"))
        try:
            os.link(stage, late_alias)
            late_link_created = True
        except OSError:
            pass
        return original_publish(handle, target)

    census_module._snapshot_atomic_no_replace_v1 = attack_before_native_rename
    late_receipt = None
    late_error = None
    try:
        try:
            late_receipt = census_module.export_snapshot(
                c08_r3_payload, late_destination, owned_root=late_root,
                output_format="json")
        except census_module.OperationalEvidenceError as exc:
            late_error = exc
    finally:
        census_module._snapshot_atomic_no_replace_v1 = original_publish
    if (late_link_created and
            (late_error is None or
             late_error.code != "OE_EXPORT_WRITE_FAILED" or late_receipt)):
        correction_red_failures.append(
            "C08-R4-C2 after-final-check/before-native-rename hard link "
            "returned success-shaped receipt")
    if (not late_edge_reached and
            (late_error is None or
             late_error.code != "OE_EXPORT_WRITE_FAILED" or late_receipt)):
        correction_red_failures.append(
            "C08-R4-C2 unavailable hard-link custody did not fail typed")
    if not late_edge_reached and any(late_root.iterdir()):
        correction_red_failures.append(
            "C08-R4-C2 capability refusal left a stage or destination")

    post_root = c08_r3_export_root / "native-post-publication-hardlink"
    post_root.mkdir()
    post_destination = post_root / "snapshot.json"
    post_alias = post_root / "post-alias"
    post_edge_reached = False
    post_link_created = False

    def publish_then_hardlink(handle, target):
        global post_edge_reached, post_link_created
        post_edge_reached = True
        result = original_publish(handle, target)
        try:
            os.link(target, post_alias)
            post_link_created = True
        except OSError:
            pass
        return result

    census_module._snapshot_atomic_no_replace_v1 = publish_then_hardlink
    post_receipt = None
    post_error = None
    try:
        try:
            post_receipt = census_module.export_snapshot(
                c08_r3_payload, post_destination, owned_root=post_root,
                output_format="json")
        except census_module.OperationalEvidenceError as exc:
            post_error = exc
    finally:
        census_module._snapshot_atomic_no_replace_v1 = original_publish
    if (post_link_created and
            (post_error is None or
             post_error.code != "OE_EXPORT_WRITE_FAILED" or post_receipt)):
        correction_red_failures.append(
            "C08-R4-C2 post-publication live-handle hard link returned "
            "success-shaped receipt")
    if (not post_edge_reached and
            (post_error is None or
             post_error.code != "OE_EXPORT_WRITE_FAILED" or post_receipt)):
        correction_red_failures.append(
            "C08-R4-C2 unavailable post-publication custody did not fail typed")
    if not post_edge_reached and any(post_root.iterdir()):
        correction_red_failures.append(
            "C08-R4-C2 post-publication capability refusal left an object")
def refresh_release_candidate_invalidators(value):
    boundary = value["external_boundary"]
    boundary_currentness = census_module._external_boundary_currentness(
        boundary["auth_state"], boundary["rate_state"],
        boundary["pagination_state"], boundary["object_drift"],
        boundary["expires_at"], boundary["evaluated_at"])
    invalidators = list(boundary_currentness["invalidators"])
    for row in value["nodes"]:
        if row["layer"] != "EXTERNAL":
            continue
        for invalidator in row["currentness"]["invalidators"]:
            if invalidator not in invalidators:
                invalidators.append(invalidator)
    required_types = {
        "Commit", "Tree", "Worktree", "GeneratedArtifact", "Package",
        "Install", "Host", "PullRequest", "Check", "Merge", "Tag",
        "Release", "Asset", "PublicSurface"}
    observed_types = {row["record_type"] for row in value["nodes"]}
    invalidators.extend(
        f"MISSING_RELEASE_LAYER:{record_type}"
        for record_type in sorted(required_types - observed_types))
    public_nodes = [
        row for row in value["nodes"]
        if row["record_type"] == "PublicSurface"]
    if len(public_nodes) != 1:
        invalidators.append("PUBLIC_IDENTITY_NOT_EXACTLY_ONE")
    elif public_nodes[0]["commit_identity"] != value["repository"]["commit"]:
        invalidators.append("PUBLIC_PREDECESSOR_DIFFERS_FROM_LOCAL_COMMIT")
    if value["repository"]["worktree_state"] != "CLEAN":
        invalidators.append("LOCAL_WORKTREE_DIRTY")
    if not invalidators:
        invalidators.append("NATIVE_CANDIDATE_QUALIFICATION_REQUIRED")
    value["candidate"]["invalidators"] = invalidators


census_targets = (
    ("evidence_failure", "evidence_records", "claim-effectiveness",
     "R0038-C04", "EVIDENCE", None, "fixture-evidence-owner"),
    ("evidence_failure", "failure_records", "andon-first-red",
     "R0038-C04", "FAILURE", None, "fixture-failure-owner"),
    ("release", "nodes", "generated-plugin",
     "R0038-C05", "RELEASE", "LOCAL", "fixture-generated-owner"),
    ("release", "nodes", "external-pr",
     "R0038-C05", "RELEASE", "EXTERNAL", "github:fixture/repository"),
)
admitted_non_current_states = tuple(
    state for state in census_module.STATES if state != "CURRENT")
for (collector, bucket, record_id, owner, family, layer,
     native_owner_identity) in census_targets:
    for state in admitted_non_current_states:
        collections = copy.deepcopy(census_collections)
        value = collections[collector]["value"]
        target = next(row for row in value[bucket] if row["id"] == record_id)
        invalidators = [f"HELD_OUT_{state}"]
        target["currentness"] = {
            "state": state, "invalidators": invalidators}
        if collector == "release" and target.get("layer") == "EXTERNAL":
            target["native_currentness"] = {
                "state": state, "invalidators": invalidators}
            target["currentness"] = census_module._compose_currentness(
                target["native_currentness"], target["capture_currentness"])
            refresh_release_candidate_invalidators(value)
        census_module._currentness(
            target["currentness"], f"$held_out.{collector}.{record_id}")
        semantic_value = {
            key: item for key, item in value.items()
            if key != "semantic_sha256"}
        value["semantic_sha256"] = hashlib.sha256(
            census_module.canonical_json_v1(semantic_value)).hexdigest()
        collections[collector]["sha256"] = hashlib.sha256(
            census_module.canonical_json_v1(value)).hexdigest()
        material = census_module._build_snapshot_material_v1(
            census_native, collections, census_schema_raw, census_compiler_raw)
        held_out_payload = json.loads(material["payload_raw"].decode("utf-8"))
        held_out_diff = census_module.diff_snapshots(
            held_out_payload, copy.deepcopy(held_out_payload))
        if (held_out_diff["added"] or held_out_diff["removed"] or
                held_out_diff["changed"]):
            correction_red_failures.append(
                f"C08-R3-C1 valid {collector}/{record_id}/{state} "
                "did not yield an empty diff")
        input_census = json.loads(material["input_raw"])[
            "missing_or_omitted_state"]
        payload_census = json.loads(material["payload_raw"])[
            "missing_or_omitted_state"]
        fact_path = f"{bucket}/{record_id}"
        for surface, rows in (
                ("input-manifest", input_census), ("payload", payload_census)):
            matches = [
                row for row in rows
                if row.get("kind") == "OWNER_FACT_NON_CURRENT" and
                row.get("collector") == collector and
                row.get("fact_path") == fact_path]
            if len(matches) != 1:
                correction_red_failures.append(
                    f"C06-I1 {surface} retained {len(matches)} rows for "
                    f"{collector}/{fact_path}/{state}")
                continue
            observed = matches[0]
            expected = {
                "owner": owner, "family": family, "state": state,
                "invalidators": invalidators,
                "native_owner_identity": native_owner_identity}
            if any(observed.get(key) != item for key, item in expected.items()):
                correction_red_failures.append(
                    f"C06-I1 {surface} lost owner/state for "
                    f"{collector}/{fact_path}/{state}")
            if layer is not None and observed.get("layer") != layer:
                correction_red_failures.append(
                    f"C06-I1 {surface} lost layer for "
                    f"{collector}/{fact_path}/{state}")
        if input_census != payload_census:
            correction_red_failures.append(
                f"C06-I1 census surfaces disagree for "
                f"{collector}/{fact_path}/{state}")

publisher_census_repo = census_repo
publisher_census_run = (
    publisher_census_repo / ".IMPLEMENTAUDIT/runs/native-current-ABC123")
publisher_census_module = census_module
publisher_collections = copy.deepcopy(census_collections)
publisher_changes = (
    ("evidence_failure", "evidence_records", "claim-effectiveness",
     "UNKNOWN", ["PUBLISHER_C04_UNKNOWN"]),
    ("release", "nodes", "external-pr",
     "UNVERIFIED", ["PUBLISHER_C05_UNVERIFIED"]),
)
for collector, bucket, record_id, state, invalidators in publisher_changes:
    value = publisher_collections[collector]["value"]
    target = next(row for row in value[bucket] if row["id"] == record_id)
    target["currentness"] = {
        "state": state, "invalidators": invalidators}
    semantic_value = {
        key: item for key, item in value.items()
        if key != "semantic_sha256"}
    value["semantic_sha256"] = hashlib.sha256(
        publisher_census_module.canonical_json_v1(semantic_value)).hexdigest()
    publisher_collections[collector]["sha256"] = hashlib.sha256(
        publisher_census_module.canonical_json_v1(value)).hexdigest()
publisher_census_module.collect_native_current = lambda: copy.deepcopy(
    census_native)
publisher_census_module._collect_snapshot_inputs_v1 = lambda native: (
    copy.deepcopy(publisher_collections))
publisher_census_receipt = publisher_census_module.publish_current_snapshot()
publisher_census_dir = (
    publisher_census_run / "operational-evidence/snapshots" /
    publisher_census_receipt["snapshot_id"])
publisher_input_census = json.loads(
    (publisher_census_dir / "input-manifest.json").read_bytes()
)["missing_or_omitted_state"]
publisher_payload_census = json.loads(
    (publisher_census_dir / "snapshot.json").read_bytes()
)["missing_or_omitted_state"]
for collector, fact_path, owner, state in (
        ("evidence_failure", "evidence_records/claim-effectiveness",
         "R0038-C04", "UNKNOWN"),
        ("release", "nodes/external-pr", "R0038-C05", "UNVERIFIED")):
    for surface, rows in (
            ("input-manifest", publisher_input_census),
            ("payload", publisher_payload_census)):
        matches = [
            row for row in rows
            if row.get("kind") == "OWNER_FACT_NON_CURRENT" and
            row.get("collector") == collector and
            row.get("fact_path") == fact_path and
            row.get("owner") == owner and row.get("state") == state]
        if len(matches) != 1:
            correction_red_failures.append(
                f"C06-I1 no-argument {surface} retained {len(matches)} rows "
                f"for {collector}/{fact_path}/{state}")

if correction_red_failures:
    for label in correction_red_failures:
        print(f"{label} RED", file=sys.stderr)
    raise SystemExit(1)

invalid_repo = prepare("positive", 202)
invalid_module = load_module(invalid_repo, 202)
invalid_run = invalid_repo / ".IMPLEMENTAUDIT/runs/native-current-ABC123"
(invalid_run / "operational-evidence.json").write_bytes(b'{"malformed":')
try:
    invalid_module.publish_current_snapshot()
except invalid_module.OperationalEvidenceError as exc:
    if exc.code != "OE_JSON_MALFORMED":
        raise SystemExit(f"C06-R06 invalid owner input returned {exc.code}")
else:
    raise SystemExit("C06-R06 invalid owner input was published as DEGRADED")
if (invalid_run / "operational-evidence/snapshots/CURRENT").exists():
    raise SystemExit("C06-R06 invalid owner input advanced CURRENT")

fault_stages = fixture_manifest["fault_stages"]
for index, fault_stage in enumerate(fault_stages, 300):
    fault_repo = prepare("positive", index)
    fault_module = load_module(fault_repo, index)
    fault_run = fault_repo / ".IMPLEMENTAUDIT/runs/native-current-ABC123"
    fault_snapshots = fault_run / "operational-evidence/snapshots"
    def inject(stage, expected=fault_stage):
        if stage == expected:
            raise RuntimeError("fixture fault")
    fault_module._snapshot_stage_v1 = inject
    try:
        fault_module.publish_current_snapshot()
    except fault_module.OperationalEvidenceError as exc:
        expected_code = (
            "OE_SNAPSHOT_PUBLICATION_UNKNOWN_EFFECT"
            if fault_stage == "after-current-replace"
            else "OE_SNAPSHOT_PUBLICATION_FAILED")
        if exc.code != expected_code:
            raise SystemExit(
                f"C06-R07 {fault_stage} returned {exc.code}, expected {expected_code}")
    else:
        raise SystemExit(f"C06-R07 {fault_stage} did not interrupt publication")
    current_path = fault_snapshots / "CURRENT"
    if fault_stage == "after-current-replace":
        current_value = fault_module._snapshot_current_raw_v1(fault_snapshots)
        if current_value is None:
            raise SystemExit("C06-R07 post-replace fault lost the new complete selection")
    elif current_path.exists() or current_path.is_symlink():
        raise SystemExit(f"C06-R07 {fault_stage} advanced CURRENT")
    if fault_stage == "before-current-temp":
        fault_native = fault_module.collect_native_current()
        try:
            rotation.load_exact_r0038_current_snapshot_manifest_v1(
                run_root=fault_run,
                pointer_oid=fault_native["continuity"]["pointer_oid"],
                controller_id=fault_native["controller"]["id"],
                claim_id=fault_native["claim"]["id"],
                run_id=fault_native["claim"]["run_id"],
                source_epoch=fault_native["continuity"]["source_epoch"])
        except rotation.RotationError as exc:
            if str(exc) != "OE_R0038_SNAPSHOT_NOT_PUBLISHED":
                raise SystemExit(f"C06-H02 unselected snapshot returned {exc}")
        else:
            raise SystemExit("C06-H02 unselected immutable directory was discovered")
    if fault_snapshots.exists():
        residue = [
            path.name for path in fault_snapshots.iterdir()
            if path.name.startswith(".pending-") or path.name.startswith(".CURRENT-")]
        if residue:
            raise SystemExit(f"C06-R07 {fault_stage} left private temp residue: {residue}")
PY

if [ "${1:-}" = "--native-current-only" ]; then
  printf 'operational-evidence-contract.test: native-current ok\n'
  exit 0
fi

"${py_cmd[@]}" - "$loader" "$rotation_loader" <<'PY'
import importlib.util
import sys


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


evidence = load("operational_evidence_cross_owner", sys.argv[1])
rotation = load("rotation_cross_owner", sys.argv[2])
value = {"unicode": "\u00e9", "nested": [0, None, True]}
if evidence.canonical_json_v1(value) != rotation.canonical_json_v1(value):
    raise SystemExit("R0038/R0039 canonical event bytes diverged")
if rotation.canonical_json_v1(value).endswith(b"\n"):
    raise SystemExit("R0039 canonical event bytes retained terminal LF")
PY

expect_typed_failure() {
  local fixture="$1"
  local code="$2"
  local status
  set +e
  "${py_cmd[@]}" "$loader" validate "$fixtures/$fixture" \
    >"$tmp/stdout" 2>"$tmp/stderr"
  status=$?
  set -e
  [ "$status" -eq 2 ] \
    || fail "$fixture expected typed exit 2, got $status"
  "${py_cmd[@]}" - "$tmp/stderr" "$code" <<'PY'
import json
import sys

with open(sys.argv[1], encoding="utf-8") as stream:
    error = json.load(stream)
if error.get("schema") != "implementaudit-operational-evidence-error-v1":
    raise SystemExit("stable typed error schema missing")
if error.get("code") != sys.argv[2]:
    raise SystemExit(
        f"expected typed failure {sys.argv[2]}, got {error.get('code')!r}")
PY
}

"${py_cmd[@]}" "$loader" validate "$fixtures/valid-minimal.json" \
  >"$tmp/valid.json"
"${py_cmd[@]}" - "$tmp/valid.json" <<'PY'
import json
import sys

with open(sys.argv[1], encoding="utf-8") as stream:
    result = json.load(stream)
if result.get("schema") != "implementaudit-operational-evidence-validation-v1":
    raise SystemExit("validation receipt schema missing")
if result.get("aggregate") != "COMPLETE":
    raise SystemExit("valid COMPLETE fixture did not remain COMPLETE")
if result.get("families") != [
        "CODE", "OWNERSHIP", "EXECUTION", "EVIDENCE", "FAILURE", "RELEASE"]:
    raise SystemExit("six frozen families were not preserved in order")
PY

"${py_cmd[@]}" "$loader" validate "$fixtures/valid-unknown.json" \
  >"$tmp/unknown-receipt.json"
"${py_cmd[@]}" "$loader" canonicalize "$fixtures/valid-unknown.json" \
  >"$tmp/unknown-canonical.json"
"${py_cmd[@]}" - "$tmp/unknown-receipt.json" \
  "$tmp/unknown-canonical.json" <<'PY'
import json
import sys

with open(sys.argv[1], encoding="utf-8") as stream:
    receipt = json.load(stream)
with open(sys.argv[2], encoding="utf-8") as stream:
    canonical = json.load(stream)
if receipt.get("aggregate") != "DEGRADED":
    raise SystemExit("UNKNOWN receipt must preserve DEGRADED aggregate")
if receipt.get("fact_state_census") != {"UNKNOWN": 1}:
    raise SystemExit("UNKNOWN receipt state census drift")
if canonical["aggregate"] != "DEGRADED":
    raise SystemExit("UNKNOWN canonical aggregate drift")
if canonical["affected_families"] != ["CODE"]:
    raise SystemExit("UNKNOWN affected family drift")
if canonical["entities"][0]["currentness"] != {
        "state": "UNKNOWN", "invalidators": []}:
    raise SystemExit("UNKNOWN canonical state drift")
PY

expect_typed_failure duplicate-key.json OE_JSON_DUPLICATE_KEY
expect_typed_failure nonfinite.json OE_JSON_NONFINITE
expect_typed_failure malformed-record.json OE_SCHEMA_INVALID
expect_typed_failure record-type-array.json OE_SCHEMA_INVALID
expect_typed_failure integer-digit-limit.json OE_JSON_NUMBER_LIMIT
expect_typed_failure cross-layer.json OE_CROSS_LAYER
expect_typed_failure stale-current.json OE_STALE_RECORD
expect_typed_failure unsupported-schema.json OE_SCHEMA_UNSUPPORTED
expect_typed_failure duplicate-id.json OE_SCHEMA_INVALID
expect_typed_failure payload-digest-mismatch.json OE_PAYLOAD_DIGEST

"${py_cmd[@]}" "$loader" canonicalize "$fixtures/payload-lf.json" \
  >"$tmp/payload-lf.json"
"${py_cmd[@]}" "$loader" canonicalize "$fixtures/payload-crlf.json" \
  >"$tmp/payload-crlf.json"
cmp "$tmp/payload-lf.json" "$tmp/payload-crlf.json" \
  || fail "equivalent payload newline forms did not canonicalize byte-identically"
"${py_cmd[@]}" - "$tmp/payload-lf.json" <<'PY'
import json
import sys

with open(sys.argv[1], encoding="utf-8") as stream:
    value = json.load(stream)
payload = value["payload_records"][0]
if payload["payload"] != "line one\nline two":
    raise SystemExit("payload rule must normalize CRLF/CR to LF and strip trailing LF")
if payload["payload_sha256"] != (
        "b6858b03a6cae635deeaeab09a74e598979b72c917cbfff0bb3fe2cd05111dbc"):
    raise SystemExit("payload digest drift")
PY

"${py_cmd[@]}" - "$loader" "$fixtures/static-repository" "$tmp" <<'PY'
import ast
import copy
import hashlib
import importlib.util
import json
import os
import pathlib
import platform
import shutil
import subprocess
import sys
import threading


loader_path = pathlib.Path(sys.argv[1])
fixture_root = pathlib.Path(sys.argv[2])
tmp_root = pathlib.Path(sys.argv[3])
spec = importlib.util.spec_from_file_location("operational_evidence", loader_path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

for symbol in ("collect_repository", "normalize_static_receipt",
               "normalize_static_receipts"):
    if not hasattr(module, symbol):
        raise SystemExit(f"C02 RED: CODE collector/normalizer missing: {symbol}")

if not hasattr(module, "collect_evidence_failure"):
    raise SystemExit(
        "C04 RED: carrier cannot distinguish attempt, effect, recovery, closure")

for symbol in ("collect_release", "run_external_readonly"):
    if not hasattr(module, symbol):
        raise SystemExit(
            "C05 RED: RELEASE projection/explicit read-only refresh missing: "
            f"{symbol}")


def git(root, *args):
    result = subprocess.run(
        ["git", "-C", os.fspath(root), *args], check=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return result.stdout.strip()


def initialize_repo(root):
    git(root, "init", "-q")
    git(root, "config", "user.name", "Operational Evidence Fixture")
    git(root, "config", "user.email", "fixture@example.invalid")
    git(root, "add", "--all")
    env = dict(os.environ)
    env.update({
        "GIT_AUTHOR_DATE": "2026-08-20T00:00:00Z",
        "GIT_COMMITTER_DATE": "2026-08-20T00:00:00Z",
    })
    subprocess.run(
        ["git", "-C", os.fspath(root), "commit", "-q", "-m", "fixture"],
        check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)


def fingerprint(root):
    rows = []
    for path in sorted(root.rglob("*")):
        if ".git" in path.parts or not path.is_file():
            continue
        rows.append((path.relative_to(root).as_posix(),
                     hashlib.sha256(path.read_bytes()).hexdigest()))
    return rows, git(root, "status", "--porcelain=v1", "--untracked-files=all")


repo = tmp_root / "static-repository"
shutil.copytree(fixture_root, repo)
initialize_repo(repo)
before = fingerprint(repo)
collection = module.collect_repository(repo)
after = fingerprint(repo)
if before != after:
    raise SystemExit("repository collector mutated target bytes or Git state")
if collection.get("schema") != "implementaudit-repository-collection-v1":
    raise SystemExit("repository collection schema missing")
repository = collection.get("repository", {})
if repository.get("commit") != git(repo, "rev-parse", "HEAD"):
    raise SystemExit("repository commit provenance drift")
if repository.get("tree") != git(repo, "rev-parse", "HEAD^{tree}"):
    raise SystemExit("repository tree provenance drift")
if repository.get("worktree_state") != "CLEAN":
    raise SystemExit("clean fixture repository did not remain CLEAN")

facts = collection.get("facts", [])
file_facts = {row.get("path"): row for row in facts if row.get("kind") == "FILE"}
expected_paths = {
    "README.weird", "package/implementaudit-package.json", "scripts/check.sh",
    "scripts/verify-package.sh", "src/broken.py", "src/helper.py",
    "src/main.py", "tests/example.test.sh",
}
if set(file_facts) != expected_paths:
    raise SystemExit("tracked file fact census drift")
if file_facts["src/main.py"].get("sha256") != (
        "46f4e61c6e13ed54aebb3dec432b98d712703106ba7292ac8a8419f7149d2bff"):
    raise SystemExit("file byte provenance drift")

edges = [row for row in facts if row.get("kind") == "PYTHON_IMPORT"]
if [(row.get("source"), row.get("target")) for row in edges] != [
        ("src/main.py", "src/helper.py")]:
    raise SystemExit("bounded Python-AST positive edge drift")
edge_provenance = edges[0].get("provenance", {})
if (edge_provenance.get("parser") != "python-ast-static-imports-v1" or
        edge_provenance.get("input_path") != "src/main.py" or
        edge_provenance.get("input_sha256") != file_facts["src/main.py"]["sha256"]):
    raise SystemExit("Python-AST edge lost parser/input provenance")
expected_ast_digest = hashlib.sha256(
    pathlib.Path(ast.__file__).read_bytes()).hexdigest()
if ({
        "collector_identity": edge_provenance.get("collector_identity"),
        "collector_version": edge_provenance.get("collector_version"),
        "collector_package_sha256": edge_provenance.get(
            "collector_package_sha256"),
        "invocation_identity": edge_provenance.get("invocation_identity"),
        "output_schema_identity": edge_provenance.get("output_schema_identity"),
    } != {
        "collector_identity": "python-stdlib-ast",
        "collector_version": (
            f"{platform.python_implementation()}-{platform.python_version()}"),
        "collector_package_sha256": expected_ast_digest,
        "invocation_identity": "ast.parse(mode=exec,type_comments=false)",
        "output_schema_identity": "implementaudit-repository-collection-v1",
    }):
    raise SystemExit("Python-AST edge lost exact collector provenance")
reverse = [row for row in facts if row.get("kind") == "PYTHON_REVERSE_DEPENDENT"]
if [(row.get("source"), row.get("target")) for row in reverse] != [
        ("src/helper.py", "src/main.py")]:
    raise SystemExit("reverse-dependent positive fact drift")
external = [row for row in facts
            if row.get("kind") == "UNSUPPORTED_IMPORT_OBSERVATION"]
if [(row.get("source"), row.get("target"), row.get("state"))
        for row in external] != [("src/main.py", "importlib", "UNSUPPORTED")]:
    raise SystemExit("unsupported external import became a missing edge")
if not any(value.startswith("computed-import:src/main.py:")
           for value in collection["diagnostics"]["unknown"]):
    raise SystemExit("computed import did not remain explicitly unknown")
if any(row.get("kind") in {"WORK_DEPENDENCY", "READY", "JOIN"}
       for row in facts):
    raise SystemExit("source topology invented work authority")
parser_errors = [row for row in facts
                 if row.get("kind") == "PARSER_ERROR_OBSERVATION"]
if len(parser_errors) != 1 or parser_errors[0].get("path") != "src/broken.py":
    raise SystemExit("parser failure became empty or lost its file identity")
if not any(row.get("kind") == "PACKAGE_ROOT" and row.get("path") == "src"
           for row in facts):
    raise SystemExit("positive package-root relation missing")
registry = [row for row in facts if row.get("kind") == "REGISTRY_FILE"]
if len(registry) != 1 or registry[0].get("path") != "scripts/verify-package.sh":
    raise SystemExit("registry file identity missing")
if any(row.get("kind") == "REGISTRY_ENTRY" for row in facts):
    raise SystemExit("unsupported shell registry inferred entries")
capabilities = {row["capability"]: row for row in collection["capabilities"]}
if capabilities["python_ast"]["state"] != "PARTIAL":
    raise SystemExit("parser error did not degrade Python-AST capability")
if capabilities["python_ast"].get("provenance") != {
        "collector_identity": "python-stdlib-ast",
        "collector_version": (
            f"{platform.python_implementation()}-{platform.python_version()}"),
        "collector_package_sha256": expected_ast_digest,
        "invocation_identity": "ast.parse(mode=exec,type_comments=false)",
        "output_schema_identity": "implementaudit-repository-collection-v1",
        "parser": "python-ast-static-imports-v1",
        "input_file_set_sha256": repository["input_file_set_sha256"],
    }:
    raise SystemExit("Python-AST capability lost exact degraded provenance")
if capabilities["validation_registry_entries"]["state"] != "UNSUPPORTED":
    raise SystemExit("shell registry extraction was not marked unsupported")
if module.canonical_json_v1(collection) != module.canonical_json_v1(
        module.collect_repository(repo)):
    raise SystemExit("repository collection is not semantically repeatable")

(repo / "README.weird").unlink()
missing_file = module.collect_repository(repo)
missing_caps = {
    row["capability"]: row for row in missing_file["capabilities"]}
if missing_caps["file_facts"]["state"] != "PARTIAL":
    raise SystemExit("unreadable tracked file did not degrade file capability")
missing_facts = [
    row for row in missing_file["facts"]
    if row.get("kind") == "FILE_UNREADABLE_OBSERVATION"]
if (len(missing_facts) != 1 or
        missing_facts[0].get("path") != "README.weird" or
        missing_facts[0].get("state") != "STALE"):
    raise SystemExit("unreadable tracked file became an empty fact gap")

non_applicable = tmp_root / "non-applicable"
non_applicable.mkdir()
(non_applicable / "package.json").write_text(
    '{"scripts":{"collect":"node target-controlled.js"}}\n', encoding="utf-8")
(non_applicable / "target-controlled.js").write_text(
    "require('fs').writeFileSync('EXECUTED', 'bad')\n", encoding="utf-8")
(non_applicable / "webpack.config.js").write_text(
    "throw new Error('must not execute')\n", encoding="utf-8")
initialize_repo(non_applicable)
cheap = module.collect_repository(non_applicable)
if (non_applicable / "EXECUTED").exists():
    raise SystemExit("non-applicable collection executed target code")
if cheap.get("static_collector_invocations") != []:
    raise SystemExit("non-applicable repository paid mandatory collector cost")
cheap_caps = {row["capability"]: row for row in cheap["capabilities"]}
if cheap_caps["python_ast"]["state"] != "NOT_APPLICABLE":
    raise SystemExit("non-applicable repository state drift")
if not [row for row in cheap["facts"] if row.get("kind") == "FILE"]:
    raise SystemExit("non-applicable repository lost exact file fallback")

fsmonitor_repo = tmp_root / "fsmonitor-repository"
shutil.copytree(fixture_root, fsmonitor_repo)
initialize_repo(fsmonitor_repo)
fsmonitor_marker = fsmonitor_repo / "FSMONITOR_EXECUTED"
fsmonitor_hook = tmp_root / "fsmonitor-sentinel.sh"
fsmonitor_hook.write_text(
    '#!/bin/sh\nprintf invoked > FSMONITOR_EXECUTED\n',
    encoding="utf-8")
fsmonitor_hook.chmod(0o755)
git(fsmonitor_repo, "config", "core.fsmonitor", fsmonitor_hook.as_posix())
git(fsmonitor_repo, "update-index", "--fsmonitor")
if fsmonitor_marker.exists():
    fsmonitor_marker.unlink()
git(fsmonitor_repo, "status", "--porcelain=v1", "--untracked-files=all")
if not fsmonitor_marker.exists():
    raise SystemExit("fsmonitor sentinel control did not execute under ordinary Git")
fsmonitor_marker.unlink()
module.collect_repository(fsmonitor_repo)
if fsmonitor_marker.exists():
    raise SystemExit("repository collector executed target core.fsmonitor helper")

changing_repo = tmp_root / "changing-repository"
shutil.copytree(fixture_root, changing_repo)
initialize_repo(changing_repo)
changing_path = (changing_repo / "src" / "main.py").resolve()
original_read_bytes = pathlib.Path.read_bytes
first_hash_read = threading.Event()
mutation_finished = threading.Event()
read_state = {"intercepted": False}


def synchronized_read_bytes(path):
    data = original_read_bytes(path)
    if path.resolve() == changing_path and not read_state["intercepted"]:
        read_state["intercepted"] = True
        first_hash_read.set()
        if not mutation_finished.wait(timeout=5):
            raise RuntimeError("timed out waiting for synchronized mutation")
    return data


def mutate_after_first_hash():
    if not first_hash_read.wait(timeout=5):
        return
    changing_path.write_bytes(
        original_read_bytes(changing_path) + b"\n# synchronized change\n")
    mutation_finished.set()


mutator = threading.Thread(target=mutate_after_first_hash)
mutator.start()
pathlib.Path.read_bytes = synchronized_read_bytes
try:
    module.collect_repository(changing_repo)
except module.OperationalEvidenceError as exc:
    if exc.code != "OE_REPOSITORY_CHANGED_DURING_SCAN":
        raise SystemExit(
            "mid-scan mutation expected OE_REPOSITORY_CHANGED_DURING_SCAN, "
            f"got {exc.code}")
else:
    raise SystemExit("mid-scan mutation returned a mixed CURRENT snapshot")
finally:
    pathlib.Path.read_bytes = original_read_bytes
    mutator.join(timeout=5)
if mutator.is_alive() or not mutation_finished.is_set():
    raise SystemExit("synchronized mid-scan mutation control did not complete")

late_changing_repo = tmp_root / "late-changing-repository"
shutil.copytree(fixture_root, late_changing_repo)
initialize_repo(late_changing_repo)
late_changing_path = (late_changing_repo / "src" / "main.py").resolve()
original_ast_parse = module.ast.parse
ast_scan_started = threading.Event()
late_mutation_finished = threading.Event()


def synchronized_ast_parse(source, filename="<unknown>", mode="exec", **kwargs):
    if filename == "src/main.py":
        ast_scan_started.set()
        if not late_mutation_finished.wait(timeout=5):
            raise RuntimeError("timed out waiting for late synchronized mutation")
    return original_ast_parse(source, filename=filename, mode=mode, **kwargs)


def mutate_during_ast_scan():
    if not ast_scan_started.wait(timeout=5):
        return
    late_changing_path.write_bytes(
        late_changing_path.read_bytes() + b"\n# late synchronized change\n")
    late_mutation_finished.set()


late_mutator = threading.Thread(target=mutate_during_ast_scan)
late_mutator.start()
module.ast.parse = synchronized_ast_parse
try:
    module.collect_repository(late_changing_repo)
except module.OperationalEvidenceError as exc:
    if exc.code != "OE_REPOSITORY_CHANGED_DURING_SCAN":
        raise SystemExit(
            "during-AST mutation expected OE_REPOSITORY_CHANGED_DURING_SCAN, "
            f"got {exc.code}")
else:
    raise SystemExit("during-AST mutation returned a mixed CURRENT snapshot")
finally:
    module.ast.parse = original_ast_parse
    late_mutator.join(timeout=5)
if late_mutator.is_alive() or not late_mutation_finished.is_set():
    raise SystemExit("synchronized during-AST mutation control did not complete")

post_fence_repo = tmp_root / "post-fence-repository"
shutil.copytree(fixture_root, post_fence_repo)
initialize_repo(post_fence_repo)
post_fence_path = (post_fence_repo / "src" / "main.py").resolve()
original_stability_fence = module._require_repository_snapshot_stable
original_canonical_json = module.canonical_json_v1
post_fence_state = {"fences": 0, "armed": False, "mutated": False}


def observing_stability_fence(*args, **kwargs):
    result = original_stability_fence(*args, **kwargs)
    post_fence_state["fences"] += 1
    if post_fence_state["fences"] == 2:
        post_fence_state["armed"] = True
    return result


def mutate_from_post_fence_canonicalization(value):
    if post_fence_state["armed"] and not post_fence_state["mutated"]:
        post_fence_path.write_bytes(
            post_fence_path.read_bytes() + b"\n# post-fence callback change\n")
        post_fence_state["mutated"] = True
    return original_canonical_json(value)


module._require_repository_snapshot_stable = observing_stability_fence
module.canonical_json_v1 = mutate_from_post_fence_canonicalization
try:
    module.collect_repository(post_fence_repo)
except module.OperationalEvidenceError as exc:
    if exc.code != "OE_REPOSITORY_CHANGED_DURING_SCAN":
        raise SystemExit(
            "post-fence callback mutation expected "
            f"OE_REPOSITORY_CHANGED_DURING_SCAN, got {exc.code}")
else:
    raise SystemExit("post-final-fence canonicalization mutation escaped")
finally:
    module._require_repository_snapshot_stable = original_stability_fence
    module.canonical_json_v1 = original_canonical_json
if not post_fence_state["mutated"] or post_fence_state["fences"] != 2:
    raise SystemExit("post-final-fence mutation control did not reach its window")

terminal_repo = tmp_root / "terminal-fence-repository"
shutil.copytree(fixture_root, terminal_repo)
initialize_repo(terminal_repo)
original_read_repository_path = module._read_repository_path
original_run_git = module._run_git
original_decode_strict_json = module.decode_strict_json_bytes
terminal_original_ast_parse = module.ast.parse
terminal_state = {"fences": 0, "complete": False, "after": []}


def terminal_stability_fence(*args, **kwargs):
    result = original_stability_fence(*args, **kwargs)
    terminal_state["fences"] += 1
    if terminal_state["fences"] == 3:
        terminal_state["complete"] = True
    return result


def record_after_final(name, function):
    def wrapper(*args, **kwargs):
        if terminal_state["complete"]:
            terminal_state["after"].append(name)
        return function(*args, **kwargs)
    return wrapper


module._require_repository_snapshot_stable = terminal_stability_fence
module.canonical_json_v1 = record_after_final(
    "canonical_json_v1", original_canonical_json)
module._read_repository_path = record_after_final(
    "read_repository_path", original_read_repository_path)
module._run_git = record_after_final("run_git", original_run_git)
module.decode_strict_json_bytes = record_after_final(
    "decode_strict_json_bytes", original_decode_strict_json)
module.ast.parse = record_after_final("ast.parse", terminal_original_ast_parse)
try:
    terminal_collection = module.collect_repository(terminal_repo)
finally:
    module._require_repository_snapshot_stable = original_stability_fence
    module.canonical_json_v1 = original_canonical_json
    module._read_repository_path = original_read_repository_path
    module._run_git = original_run_git
    module.decode_strict_json_bytes = original_decode_strict_json
    module.ast.parse = terminal_original_ast_parse
if terminal_state["fences"] != 3:
    raise SystemExit("true final stability fence was not observed exactly once")
if terminal_state["after"]:
    raise SystemExit(
        "target-sensitive/callback work followed final fence: " +
        ",".join(terminal_state["after"]))
if terminal_collection.get("repository", {}).get("worktree_state") != "CLEAN":
    raise SystemExit("terminal-fence unchanged repository lost CURRENT path")

run_fixture_root = fixture_root.parent / "run-artifacts" / "positive"
run_root = tmp_root / "run-artifacts-positive"
shutil.copytree(run_fixture_root, run_root)


def artifact_fingerprint(root):
    return [
        (path.relative_to(root).as_posix(),
         hashlib.sha256(path.read_bytes()).hexdigest())
        for path in sorted(root.rglob("*")) if path.is_file()
    ]


before_run_artifacts = artifact_fingerprint(run_root)
run_collection = module.collect_evidence_failure(run_root)
if artifact_fingerprint(run_root) != before_run_artifacts:
    raise SystemExit("evidence/failure collector mutated canonical run artifacts")
if run_collection.get("schema") != (
        "implementaudit-evidence-failure-collection-v1"):
    raise SystemExit("C04 evidence/failure collection schema missing")
if run_collection.get("families") != ["EVIDENCE", "FAILURE"]:
    raise SystemExit("C04 collection crossed or lost its frozen families")
source = run_collection.get("source", {})
canonical_artifact = run_root / "operational-evidence.json"
if source != {
        "path": "operational-evidence.json",
        "sha256": hashlib.sha256(canonical_artifact.read_bytes()).hexdigest(),
        "run_identity": "fixture-run-c04",
        "artifact_identity": "fixture-run-c04-evidence-1"}:
    raise SystemExit("C04 canonical artifact provenance drift")
evidence = {
    row["id"]: row for row in run_collection.get("evidence_records", [])}
failures = {
    row["id"]: row for row in run_collection.get("failure_records", [])}
if set(evidence) != {
        "claim-effectiveness", "criterion-live-effect", "check-attempt-red",
        "effect-red", "proxy-green", "recovery-observed",
        "review-nonverdict"}:
    raise SystemExit("C04 evidence population was collapsed")
if run_collection.get("layer_census") != {
        "ATTEMPT": 4, "RECEIPT": 0, "EFFECT": 1, "RECOVERY": 1,
        "CLOSURE": 1}:
    raise SystemExit("attempt/effect/recovery/closure layers were conflated")
if (run_collection.get("first_red_id") != "check-attempt-red" or
        run_collection.get("first_red_state") != "PRESENT" or
        run_collection.get("weakest_leg_id") != "effect-red"):
    raise SystemExit("first RED or weakest evidence leg was promoted away")
if (evidence["effect-red"]["result_class"] != "RED" or
        evidence["proxy-green"]["proxy"] is not True or
        evidence["proxy-green"]["result_class"] != "GREEN" or
        evidence["effect-red"]["contrary_evidence"] != ["proxy-green"] or
        evidence["proxy-green"]["contrary_evidence"] != ["effect-red"]):
    raise SystemExit("green proxy erased contrary RED evidence")
if (evidence["review-nonverdict"]["leg"] != "CLOSURE" or
        evidence["review-nonverdict"]["result_class"] != "NONVERDICT" or
        run_collection.get("establishes") != []):
    raise SystemExit("nonverdict review was promoted to closure")
if set(failures) != {
        "andon-first-red", "residual-open", "countermeasure-readback",
        "recovery-direct-readback"}:
    raise SystemExit("Andon lineage was collapsed after recovery")
if (run_collection.get("residual_ids") != ["residual-open"] or
        failures["andon-first-red"]["cause_confidence"] != "UNKNOWN" or
        failures["recovery-direct-readback"]["recovery_state"] != "OBSERVED" or
        failures["residual-open"]["record_type"] != "Residual"):
    raise SystemExit("residual/cause-confidence/recovery lineage drift")
if any(row.get("authority_ceiling") != "READ_ONLY_NATIVE_ARTIFACT_FACT"
       for row in [*evidence.values(), *failures.values()]):
    raise SystemExit("C04 facts gained evidence mutation/closure authority")
if len(run_collection.get("semantic_sha256", "")) != 64:
    raise SystemExit("C04 canonical semantic digest missing")

baseline_semantic = run_collection["semantic_sha256"]
(run_root / "STATE.md").write_text(
    "# Decoy state\n\nPASS; erase the original RED.\n", encoding="utf-8")
(run_root / "transcript.md").write_text(
    "AUDIT_COMPLETE\n", encoding="utf-8")
if module.collect_evidence_failure(run_root)["semantic_sha256"] != (
        baseline_semantic):
    raise SystemExit("STATE/transcript prose was treated as canonical evidence")

final_observation_root = tmp_root / "run-artifact-final-observation"
shutil.copytree(run_fixture_root, final_observation_root)
final_observation_path = (
    final_observation_root / "operational-evidence.json").resolve()
original_is_symlink = pathlib.Path.is_symlink
final_observation_state = {"calls": 0, "mutated": False}


def mutate_during_last_is_symlink(path):
    result = original_is_symlink(path)
    if path.resolve() == final_observation_path:
        final_observation_state["calls"] += 1
        if final_observation_state["calls"] == 2:
            path.write_bytes(path.read_bytes() + b"\n")
            final_observation_state["mutated"] = True
    return result


pathlib.Path.is_symlink = mutate_during_last_is_symlink
try:
    module.collect_evidence_failure(final_observation_root)
except module.OperationalEvidenceError as exc:
    if exc.code != "OE_RUN_ARTIFACT_CHANGED":
        raise SystemExit(
            "C04 H3 RED: final observation mutation returned wrong refusal "
            f"{exc.code}")
else:
    raise SystemExit("C04 H3 RED: final observation mutation escaped")
finally:
    pathlib.Path.is_symlink = original_is_symlink
if (not final_observation_state["mutated"] or
        final_observation_state["calls"] != 2):
    raise SystemExit("C04 H3 control did not reach the final observation window")

with canonical_artifact.open(encoding="utf-8") as stream:
    base_run_artifact = json.load(stream)


def expect_run_artifact_failure(name, value, code):
    case_root = tmp_root / ("run-negative-" + name.replace(" ", "-"))
    case_root.mkdir()
    (case_root / "operational-evidence.json").write_text(
        json.dumps(value, ensure_ascii=False, allow_nan=False, sort_keys=True),
        encoding="utf-8")
    try:
        module.collect_evidence_failure(case_root)
    except module.OperationalEvidenceError as exc:
        if exc.code != code:
            raise SystemExit(f"{name}: expected {code}, got {exc.code}")
    else:
        raise SystemExit(f"{name}: invalid run artifact was accepted")


def collect_run_artifact_case(name, value):
    case_root = tmp_root / ("run-positive-" + name.replace(" ", "-"))
    case_root.mkdir()
    (case_root / "operational-evidence.json").write_text(
        json.dumps(value, ensure_ascii=False, allow_nan=False, sort_keys=True),
        encoding="utf-8")
    return module.collect_evidence_failure(case_root)


case = copy.deepcopy(base_run_artifact)
next(row for row in case["evidence_records"]
     if row["id"] == "proxy-green")["leg"] = "RECEIPT"
try:
    receipt_collection = collect_run_artifact_case("receipt-leg", case)
except module.OperationalEvidenceError:
    raise SystemExit("C04 H1 RED: typed RECEIPT evidence leg rejected")
if (next(row for row in receipt_collection["evidence_records"]
         if row["id"] == "proxy-green")["leg"] != "RECEIPT" or
        receipt_collection["layer_census"].get("RECEIPT") != 1):
    raise SystemExit("C04 H1 RED: typed RECEIPT evidence leg lost")

case = copy.deepcopy(base_run_artifact)
next(row for row in case["failure_records"]
     if row["id"] == "countermeasure-readback")["record_type"] = "Containment"
try:
    containment_collection = collect_run_artifact_case(
        "containment-record", case)
except module.OperationalEvidenceError:
    raise SystemExit("C04 H1 RED: typed Containment failure record rejected")
if next(row for row in containment_collection["failure_records"]
        if row["id"] == "countermeasure-readback")["record_type"] != (
            "Containment"):
    raise SystemExit("C04 H1 RED: typed Containment failure record lost")

case = copy.deepcopy(base_run_artifact)
next(row for row in case["failure_records"]
     if row["id"] == "countermeasure-readback")["record_type"] = "Rerun"
try:
    rerun_collection = collect_run_artifact_case("rerun-record", case)
except module.OperationalEvidenceError:
    raise SystemExit("C04 H1 RED: typed Rerun failure record rejected")
if next(row for row in rerun_collection["failure_records"]
        if row["id"] == "countermeasure-readback")["record_type"] != "Rerun":
    raise SystemExit("C04 H1 RED: typed Rerun failure record lost")

case = copy.deepcopy(base_run_artifact)
countermeasure = next(
    row for row in case["failure_records"]
    if row["id"] == "countermeasure-readback")
countermeasure["recovery_state"] = "OBSERVED"
countermeasure["evidence_ids"] = ["check-attempt-red"]
try:
    collect_run_artifact_case("non-recovery-observed", case)
except module.OperationalEvidenceError as exc:
    if exc.code != "OE_RUN_RECOVERY_EVIDENCE":
        raise SystemExit(
            "C04 H2 RED: non-Recovery OBSERVED returned wrong refusal "
            f"{exc.code}")
else:
    raise SystemExit(
        "C04 H2 RED: non-Recovery OBSERVED accepted ATTEMPT evidence")

case = copy.deepcopy(base_run_artifact)
for row in case["evidence_records"]:
    if row["result_class"] == "RED":
        row["result_class"] = "GREEN"
case["first_red_id"] = None
case["residual_ids"] = []
case["failure_records"] = []
try:
    green_only_collection = collect_run_artifact_case("green-only", case)
except module.OperationalEvidenceError:
    raise SystemExit(
        "C04 M1 RED: green-only population lacks typed no-first-RED state")
if (green_only_collection.get("first_red_id", "missing") is not None or
        green_only_collection.get("first_red_state") != "NOT_APPLICABLE" or
        green_only_collection.get("failure_records") != [] or
        any(row["result_class"] == "RED"
            for row in green_only_collection["evidence_records"])):
    raise SystemExit(
        "C04 M1 RED: green-only population fabricated or lost RED absence")


case = copy.deepcopy(base_run_artifact)
case["first_red_id"] = "proxy-green"
expect_run_artifact_failure(
    "green proxy replaced first RED", case, "OE_RUN_EVIDENCE_FIRST_RED")

case = copy.deepcopy(base_run_artifact)
case["weakest_leg_id"] = "proxy-green"
expect_run_artifact_failure(
    "green proxy replaced weakest leg", case, "OE_RUN_EVIDENCE_WEAKEST")

case = copy.deepcopy(base_run_artifact)
next(row for row in case["evidence_records"]
     if row["id"] == "proxy-green")["leg"] = "EFFECT"
expect_run_artifact_failure(
    "proxy promoted to effect", case, "OE_RUN_EVIDENCE_PROXY")

case = copy.deepcopy(base_run_artifact)
next(row for row in case["evidence_records"]
     if row["id"] == "effect-red")["contrary_evidence"] = ["missing"]
expect_run_artifact_failure(
    "contrary evidence reference missing", case,
    "OE_RUN_EVIDENCE_REFERENCE")

case = copy.deepcopy(base_run_artifact)
case["failure_records"] = [
    row for row in case["failure_records"] if row["id"] != "residual-open"]
expect_run_artifact_failure(
    "declared residual disappeared", case, "OE_RUN_FAILURE_REFERENCE")

case = copy.deepcopy(base_run_artifact)
next(row for row in case["failure_records"]
     if row["record_type"] == "Recovery")["evidence_ids"] = [
         "check-attempt-red"]
expect_run_artifact_failure(
    "attempt receipt promoted to recovery", case,
    "OE_RUN_RECOVERY_EVIDENCE")

case = copy.deepcopy(base_run_artifact)
next(row for row in case["failure_records"]
     if row["record_type"] == "Andon")["cause_confidence"] = "CERTAIN"
expect_run_artifact_failure(
    "unsupported cause confidence invented", case, "OE_RUN_FAILURE_INVALID")

missing_artifact_root = tmp_root / "run-artifact-missing"
missing_artifact_root.mkdir()
try:
    module.collect_evidence_failure(missing_artifact_root)
except module.OperationalEvidenceError as exc:
    if exc.code != "OE_RUN_ARTIFACT_MISSING":
        raise SystemExit(
            "missing canonical run artifact expected OE_RUN_ARTIFACT_MISSING, "
            f"got {exc.code}")
else:
    raise SystemExit("STATE/transcript-only root was accepted as evidence")

release_fixture_root = fixture_root.parent / "release" / "positive"
release_root = tmp_root / "release-positive"
shutil.copytree(release_fixture_root, release_root)
initialize_repo(release_root)
before_release = fingerprint(release_root)


def forbidden_frozen_refresh(*args, **kwargs):
    raise SystemExit("frozen RELEASE collection invoked external refresh")


original_external_runner = module.run_external_readonly
module.run_external_readonly = forbidden_frozen_refresh
try:
    release_collection = module.collect_release(release_root)
finally:
    module.run_external_readonly = original_external_runner
if fingerprint(release_root) != before_release:
    raise SystemExit("RELEASE collector mutated local/frozen owner artifacts")
if release_collection.get("schema") != "implementaudit-release-collection-v1":
    raise SystemExit("C05 RELEASE collection schema missing")
if (release_collection.get("families") != ["RELEASE"] or
        release_collection.get("establishes") != []):
    raise SystemExit("C05 RELEASE collection gained non-RELEASE authority")
release_repository = release_collection.get("repository", {})
if release_repository != {
        "commit": git(release_root, "rev-parse", "HEAD"),
        "tree": git(release_root, "rev-parse", "HEAD^{tree}"),
        "worktree_state": "CLEAN"}:
    raise SystemExit("local commit/tree/worktree RELEASE identities drift")
release_nodes = {
    row["id"]: row for row in release_collection.get("nodes", [])}
expected_release_types = {
    "Commit", "Tree", "Worktree", "GeneratedArtifact", "Package",
    "Install", "Host", "PullRequest", "Check", "Merge", "Tag",
    "Release", "Asset", "PublicSurface"}
if {row["record_type"] for row in release_nodes.values()} != (
        expected_release_types):
    raise SystemExit("C05 local/external RELEASE layers were collapsed")
if len(release_nodes) != 14:
    raise SystemExit("C05 RELEASE node population drift")
if any(row.get("family") != "RELEASE" or
       row.get("authority_ceiling") != "READ_ONLY_NATIVE_OBSERVATION"
       for row in release_nodes.values()):
    raise SystemExit("C05 RELEASE fact authority ceiling drift")
if release_collection.get("external_boundary") != {
        "capture_identity": "fixture-external-capture-1",
        "source_identity": "github:theislampill/IMPLEMENTAUDIT.md",
        "auth_state": "PRESENT",
        "rate_state": "AVAILABLE",
        "rate_remaining": 4999,
        "pagination_state": "COMPLETE",
        "pagination_pages": 1,
        "object_drift": False,
        "captured_at": "2026-08-20T02:30:00Z",
        "expires_at": "2026-08-20T03:30:00Z",
        "evaluated_at": "2026-08-20T02:31:00Z"}:
    raise SystemExit("C05 external boundary state was hidden or collapsed")
candidate = release_collection.get("candidate", {})
if (candidate.get("state") != "UNVERIFIED" or
        candidate.get("invalidators") != [
            "PUBLIC_PREDECESSOR_DIFFERS_FROM_LOCAL_COMMIT"] or
        candidate.get("local_commit") != release_repository["commit"] or
        candidate.get("public_commit") != "0" * 40):
    raise SystemExit("public predecessor was promoted to a local candidate")
if len(release_collection.get("semantic_sha256", "")) != 64:
    raise SystemExit("C05 RELEASE semantic digest missing")
if module.canonical_json_v1(release_collection) != module.canonical_json_v1(
        module.collect_release(release_root)):
    raise SystemExit("unchanged frozen RELEASE collection is not deterministic")


def release_case_root(name, mutate_capture=None, mutate_local=None):
    root = tmp_root / ("release-case-" + name.replace(" ", "-"))
    shutil.copytree(release_fixture_root, root)
    local_path = root / "release-local.json"
    with local_path.open(encoding="utf-8") as stream:
        local = json.load(stream)
    if mutate_local is not None:
        mutate_local(local)
    local_path.write_text(
        json.dumps(local, ensure_ascii=False, allow_nan=False, sort_keys=True),
        encoding="utf-8")
    capture_path = root / "external-capture.json"
    with capture_path.open(encoding="utf-8") as stream:
        capture = json.load(stream)
    if mutate_capture is not None:
        mutate_capture(capture)
    capture_path.write_text(
        json.dumps(capture, ensure_ascii=False, allow_nan=False, sort_keys=True),
        encoding="utf-8")
    initialize_repo(root)
    return root


def remove_release_type(value, record_type):
    value["records"] = [
        row for row in value["records"]
        if row["record_type"] != record_type]


missing_asset = module.collect_release(release_case_root(
    "missing asset", lambda value: remove_release_type(value, "Asset")))
missing_install = module.collect_release(release_case_root(
    "missing install", mutate_local=lambda value: remove_release_type(
        value, "Install")))
if ("MISSING_RELEASE_LAYER:Asset" not in
        missing_asset["candidate"]["invalidators"] or
        "MISSING_RELEASE_LAYER:Install" not in
        missing_install["candidate"]["invalidators"] or
        missing_asset.get("omissions") != [{
            "record_type": "Asset", "state": "UNKNOWN",
            "invalidator": "MISSING_RELEASE_LAYER:Asset"}] or
        missing_install.get("omissions") != [{
            "record_type": "Install", "state": "UNKNOWN",
            "invalidator": "MISSING_RELEASE_LAYER:Install"}] or
        missing_asset["node_type_census"].get("Asset") != 0 or
        missing_install["node_type_census"].get("Install") != 0):
    raise SystemExit(
        "C05 H2 RED: missing Asset/Install layer was silently omitted")


def assert_external_state(name, mutate_capture, state, invalidator):
    collection = module.collect_release(
        release_case_root(name, mutate_capture))
    external = [
        row for row in collection["nodes"] if row["layer"] == "EXTERNAL"]
    if not external or any(
            row["currentness"] != {
                "state": state, "invalidators": [invalidator]}
            for row in external):
        raise SystemExit(
            f"{name}: external state did not preserve {invalidator}")


assert_external_state(
    "auth absent", lambda value: value.update(auth_state="ABSENT"),
    "UNVERIFIED", "AUTH_ABSENT")
assert_external_state(
    "auth unknown", lambda value: value.update(auth_state="UNKNOWN"),
    "UNVERIFIED", "AUTH_UNKNOWN")
assert_external_state(
    "rate exhausted", lambda value: value["rate"].update(
        state="EXHAUSTED", remaining=0),
    "UNKNOWN", "RATE_LIMITED")
assert_external_state(
    "rate unknown", lambda value: value["rate"].update(state="UNKNOWN"),
    "UNKNOWN", "RATE_UNKNOWN")
assert_external_state(
    "pagination incomplete", lambda value: value["pagination"].update(
        state="INCOMPLETE"),
    "UNKNOWN", "PAGINATION_INCOMPLETE")
assert_external_state(
    "pagination unknown", lambda value: value["pagination"].update(
        state="UNKNOWN"),
    "UNKNOWN", "PAGINATION_UNKNOWN")
assert_external_state(
    "object drift", lambda value: value.update(object_drift=True),
    "STALE", "OBJECT_DRIFT")
assert_external_state(
    "capture expired", lambda value: value.update(
        evaluated_at="2026-08-20T04:00:00Z"),
    "STALE", "CAPTURE_EXPIRED")


def stale_native_with_absent_auth(value):
    value["auth_state"] = "ABSENT"
    pull_request = next(
        row for row in value["records"]
        if row["record_type"] == "PullRequest")
    pull_request["currentness"] = {
        "state": "STALE", "invalidators": ["PAYLOAD_CHANGED"]}


composed_collection = module.collect_release(release_case_root(
    "stale native absent auth", stale_native_with_absent_auth))
composed_pull_request = next(
    row for row in composed_collection["nodes"]
    if row["record_type"] == "PullRequest")
if (composed_pull_request.get("native_currentness") != {
        "state": "STALE", "invalidators": ["PAYLOAD_CHANGED"]} or
        composed_pull_request.get("capture_currentness") != {
        "state": "UNVERIFIED", "invalidators": ["AUTH_ABSENT"]} or
        composed_pull_request.get("currentness") != {
        "state": "STALE",
        "invalidators": ["PAYLOAD_CHANGED", "AUTH_ABSENT"]}):
    raise SystemExit(
        "C05 H3 RED: capture degradation weakened native currentness")

try:
    module.collect_release(release_case_root(
        "impossible timestamp",
        lambda value: value.update(expires_at="2026-99-99T99:99:99Z")))
except module.OperationalEvidenceError as exc:
    if exc.code != "OE_EXTERNAL_CAPTURE_INVALID":
        raise SystemExit(
            f"impossible timestamp returned wrong refusal {exc.code}")
else:
    raise SystemExit("C05 M1 RED: impossible calendar timestamp was fresh")

try:
    module.collect_release(release_case_root(
        "impossible chronology",
        lambda value: value.update(
            captured_at="2026-08-20T04:00:00Z",
            expires_at="2026-08-20T03:30:00Z",
            evaluated_at="2026-08-20T02:31:00Z")))
except module.OperationalEvidenceError as exc:
    if exc.code != "OE_EXTERNAL_CAPTURE_INVALID":
        raise SystemExit(
            f"impossible chronology returned wrong refusal {exc.code}")
else:
    raise SystemExit("C05 M1 RED: impossible capture chronology was fresh")

expiry_equality = module.collect_release(release_case_root(
    "expiry equality",
    lambda value: value.update(evaluated_at=value["expires_at"])))
if any(
        row["currentness"] != {
            "state": "STALE", "invalidators": ["CAPTURE_EXPIRED"]}
        for row in expiry_equality["nodes"] if row["layer"] == "EXTERNAL"):
    raise SystemExit("C05 M1 RED: expiry equality remained fresh")

digest_mismatch_root = release_case_root("local digest mismatch")
(digest_mismatch_root / "artifacts" / "generated.txt").write_text(
    "changed generated bytes\n", encoding="utf-8")
try:
    module.collect_release(digest_mismatch_root)
except module.OperationalEvidenceError as exc:
    if exc.code != "OE_RELEASE_LOCAL_DIGEST":
        raise SystemExit(
            "local digest mismatch expected OE_RELEASE_LOCAL_DIGEST, "
            f"got {exc.code}")
else:
    raise SystemExit("changed local generated artifact retained CURRENT")

transport_calls = []


def external_transport(url, headers):
    transport_calls.append((url, headers))
    return {
        "status": 200,
        "headers": {
            "etag": "fixture-pr-etag",
            "x-ratelimit-remaining": "4999",
            "link": ""},
        "body": b'{"id":1,"node_id":"PR_fixture"}',
    }


external_request = {
    "schema": "implementaudit-external-read-request-v1",
    "source": "GITHUB_API",
    "operation": "PULL_REQUEST",
    "path": "/repos/fixture/project/pulls/1",
    "auth_state": "PRESENT",
    "page": 1,
    "per_page": 100,
    "expected_etag": "fixture-pr-etag",
    "captured_at": "2026-08-20T02:30:00Z",
    "expires_at": "2026-08-20T03:30:00Z",
    "evaluated_at": "2026-08-20T02:31:00Z",
}
external_receipt = module.run_external_readonly(
    external_request, external_transport)
if external_receipt.get("schema") != "implementaudit-external-read-capture-v1":
    raise SystemExit("C05 external read capture schema missing")
if external_receipt.get("boundary") != {
        "method": "UNVERIFIED", "network_used": True,
        "write_verb_exposed": "UNKNOWN",
        "transport_trust": "UNTRUSTED_INJECTED"}:
    raise SystemExit("C05 injected transport gained a GET/no-write claim")
if (external_receipt.get("authority_ceiling") !=
        "READ_ONLY_EXTERNAL_CAPTURE" or
        external_receipt.get("establishes") != []):
    raise SystemExit("C05 external capture gained qualification authority")
if external_receipt.get("currentness") != {
        "state": "UNVERIFIED",
        "invalidators": ["UNTRUSTED_INJECTED_TRANSPORT"]}:
    raise SystemExit("untrusted injected transport retained CURRENT")
if len(transport_calls) != 1:
    raise SystemExit("external read boundary did not make exactly one GET")
url, headers = transport_calls[0]
if (url != "https://api.github.com/repos/fixture/project/pulls/1?page=1&per_page=100" or
        set(headers) != {"Accept", "X-GitHub-Api-Version"}):
    raise SystemExit("external runner request escaped its fixed allowlist")

injected_effects = []


def effectful_injected_transport(url, headers):
    injected_effects.append("WRITE_EFFECT")
    return external_transport(url, headers)


injected_receipt = module.run_external_readonly(
    external_request, effectful_injected_transport)
injected_boundary = injected_receipt.get("boundary", {})
if (injected_effects != ["WRITE_EFFECT"] or
        injected_receipt.get("currentness", {}).get("state") == "CURRENT" or
        injected_boundary.get("method") == "GET" or
        injected_boundary.get("write_verb_exposed") is False):
    raise SystemExit(
        "C05 H1 RED: injected transport substantiated GET/no-write CURRENT")


def expect_external_failure(name, request, code):
    try:
        module.run_external_readonly(request, external_transport)
    except module.OperationalEvidenceError as exc:
        if exc.code != code:
            raise SystemExit(f"{name}: expected {code}, got {exc.code}")
    else:
        raise SystemExit(f"{name}: unsafe external request was accepted")


case = copy.deepcopy(external_request)
case["method"] = "POST"
expect_external_failure("caller supplied write verb", case, "OE_EXTERNAL_REQUEST")

case = copy.deepcopy(external_request)
case["path"] = "/repos/fixture/project/issues/1"
expect_external_failure("non-allowlisted external path", case,
                        "OE_EXTERNAL_REQUEST")


def assert_external_capture_state(name, request_changes, response, expected):
    request = copy.deepcopy(external_request)
    request.update(request_changes)
    receipt = module.run_external_readonly(request, lambda _url, _headers: response)
    expected = copy.deepcopy(expected)
    expected["invalidators"].append("UNTRUSTED_INJECTED_TRANSPORT")
    if receipt.get("currentness") != expected:
        raise SystemExit(
            f"{name}: external capture state drift: "
            f"{receipt.get('currentness')!r}")


base_response = {
    "status": 200,
    "headers": {
        "etag": "fixture-pr-etag", "x-ratelimit-remaining": "4999",
        "link": ""},
    "body": b'{"id":1}',
}
case_colliding_response = {
    **base_response,
    "headers": {
        "ETag": "wrong-etag",
        "etag": "fixture-pr-etag",
        "x-ratelimit-remaining": "4999",
        "link": ""},
}
try:
    module.run_external_readonly(
        external_request,
        lambda _url, _headers: case_colliding_response)
except module.OperationalEvidenceError as exc:
    if exc.code != "OE_EXTERNAL_RESPONSE":
        raise SystemExit(
            f"case-colliding ETag returned wrong refusal {exc.code}")
else:
    raise SystemExit("C05 M2 RED: case-colliding ETag was accepted")

negative_rate_response = {
    **base_response,
    "headers": {
        **base_response["headers"], "x-ratelimit-remaining": "-1"},
}
try:
    module.run_external_readonly(
        external_request,
        lambda _url, _headers: negative_rate_response)
except module.OperationalEvidenceError as exc:
    if exc.code != "OE_EXTERNAL_RESPONSE":
        raise SystemExit(
            f"negative rate remaining returned wrong refusal {exc.code}")
else:
    raise SystemExit("C05 M2 RED: negative rate remaining was accepted")

assert_external_capture_state(
    "external auth absent", {"auth_state": "ABSENT"},
    {**base_response, "status": 401},
    {"state": "UNVERIFIED", "invalidators": ["AUTH_ABSENT"]})
assert_external_capture_state(
    "external rate exhausted", {},
    {**base_response, "status": 429,
     "headers": {**base_response["headers"], "x-ratelimit-remaining": "0"}},
    {"state": "UNKNOWN", "invalidators": ["RATE_LIMITED"]})
assert_external_capture_state(
    "external pagination incomplete", {},
    {**base_response,
     "headers": {**base_response["headers"],
                 "link": '<https://api.github.com/next>; rel="next"'}},
    {"state": "UNKNOWN", "invalidators": ["PAGINATION_INCOMPLETE"]})
assert_external_capture_state(
    "external object drift", {"expected_etag": "prior-etag"}, base_response,
    {"state": "STALE", "invalidators": ["OBJECT_DRIFT"]})
assert_external_capture_state(
    "external capture expired", {"evaluated_at": "2026-08-20T04:00:00Z"},
    base_response,
    {"state": "STALE", "invalidators": ["CAPTURE_EXPIRED"]})


ZERO64 = "0" * 64
ONE64 = "1" * 64
TWO64 = "2" * 64
ZERO40 = "0" * 40
ONE40 = "1" * 40


def qualification_for(receipt, currentness="CURRENT", invalidators=None):
    qualification = {
        "qualification_identity": "fixture-static-qualification-v1",
        "self_probe_identity": "fixture-bounded-self-probe-v1",
        "wrapper_identity": receipt["collector"]["invocation_identity"],
        "collector_identity": receipt["collector"]["identity"],
        "collector_version": receipt["collector"]["version"],
        "collector_package_sha256": receipt["collector"]["package_sha256"],
        "configuration_sha256": receipt["collector"]["configuration_sha256"],
        "invocation_identity": receipt["collector"]["invocation_identity"],
        "output_schema_identity": receipt["collector"][
            "output_schema_identity"],
        "parser_mode": receipt["collector"]["parser_mode"],
        "trust_mode": receipt["collector"]["trust_mode"],
        "scope_sha256": hashlib.sha256(json.dumps(
            receipt["scope"], ensure_ascii=False, allow_nan=False,
            sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest(),
        "probe_results": {
            "positive": "PASS", "negative": "PASS", "unsupported": "PASS",
            "parser_error": "PASS", "repeatability": "PASS",
        },
        "currentness": currentness,
        "invalidators": [] if invalidators is None else invalidators,
    }
    qualification["receipt_sha256"] = hashlib.sha256(json.dumps(
        qualification, ensure_ascii=False, allow_nan=False, sort_keys=True,
        separators=(",", ":")).encode("utf-8")).hexdigest()
    return qualification


def refresh_qualification(receipt, currentness="CURRENT", invalidators=None):
    receipt["qualification"] = qualification_for(
        receipt, currentness=currentness, invalidators=invalidators)


def reseal_qualification(qualification):
    payload = dict(qualification)
    payload.pop("receipt_sha256", None)
    qualification["receipt_sha256"] = hashlib.sha256(json.dumps(
        payload, ensure_ascii=False, allow_nan=False, sort_keys=True,
        separators=(",", ":")).encode("utf-8")).hexdigest()


def base_receipt():
    receipt = {
        "schema": "implementaudit-static-receipt-v1",
        "outcome": "CURRENT",
        "invalidators": [],
        "collector": {
            "identity": "fixture-python-ast",
            "version": "3.11",
            "package_sha256": ZERO64,
            "invocation_identity": "python-ast-static-imports-v1",
            "output_schema_identity": "fixture-static-output-v1",
            "parser_mode": "python-ast-static-imports-v1",
            "configuration_sha256": ONE64,
            "trust_mode": "UNTRUSTED_DATA_ONLY",
            "executes_target_code": False,
            "auto_installs": False,
            "network_access": False,
        },
        "target": {
            "repository_identity": "fixture/repository",
            "snapshot_identity": "fixture-snapshot",
            "commit": ZERO40,
            "tree": ONE40,
            "worktree_state": "CLEAN",
            "input_file_set_sha256": TWO64,
            "physical_change": False,
        },
        "scope": {
            "applicable": True,
            "supported": ["python:static-import"],
            "unsupported": ["python:computed-import"],
            "input_complete": True,
            "entrypoints_complete": True,
            "workspace_complete": True,
            "extension_resolution_complete": True,
            "dynamic_entrypoints_complete": False,
            "generated_policy_complete": True,
            "parser_complete": True,
        },
        "diagnostics": {
            "warnings": [], "errors": [], "skipped": [],
            "unknown": ["python:computed-import"],
        },
        "facts": [{
            "id": "edge-main-helper",
            "kind": "MODULE_EDGE",
            "polarity": "POSITIVE",
            "source": "src/main.py",
            "target": "src/helper.py",
            "resolution": "RESOLVED",
            "state": "CURRENT",
            "work_consequence": "NONE",
            "mapping": None,
        }, {
            "id": "reverse-helper-main",
            "kind": "REVERSE_DEPENDENT",
            "polarity": "POSITIVE",
            "source": "src/helper.py",
            "target": "src/main.py",
            "resolution": "RESOLVED",
            "state": "CURRENT",
            "work_consequence": "NONE",
            "mapping": None,
        }],
    }
    refresh_qualification(receipt)
    return receipt


def noncurrent_positive_receipt():
    receipt = base_receipt()
    receipt["outcome"] = "PARTIAL"
    del receipt["qualification"]
    for fact in receipt["facts"]:
        fact["state"] = "PARTIAL"
    return receipt


def expect_failure(name, value, code):
    try:
        module.normalize_static_receipt(value)
    except module.OperationalEvidenceError as exc:
        if exc.code != code:
            raise SystemExit(f"{name}: expected {code}, got {exc.code}")
    else:
        raise SystemExit(f"{name}: unsafe static receipt was accepted")


case = base_receipt()
expect_failure(
    "caller self-issued an all-PASS qualification", case,
    "OE_STATIC_QUALIFICATION_REQUIRED")

case = base_receipt()
case["qualification"]["wrapper_identity"] = "caller-changed-wrapper"
reseal_qualification(case["qualification"])
expect_failure(
    "same invocation caller changed and resealed wrapper identity", case,
    "OE_STATIC_QUALIFICATION_REQUIRED")

case = base_receipt()
case["facts"][1]["mapping"] = {
    "work_node_id": "FABRICATED-NODE",
    "relation_type": "EVIDENCE",
    "effect": "INVALIDATE_EVIDENCE",
}
expect_failure(
    "caller supplied a fabricated governed mapping", case,
    "OE_STATIC_MAPPING_FORBIDDEN")

case = base_receipt()
del case["qualification"]
expect_failure(
    "CURRENT external receipt omitted qualification", case,
    "OE_STATIC_QUALIFICATION_REQUIRED")

case = base_receipt()
case["collector"]["package_sha256"] = TWO64
expect_failure(
    "CURRENT qualification bound changed collector bytes", case,
    "OE_STATIC_QUALIFICATION_REQUIRED")

case = base_receipt()
refresh_qualification(
    case, currentness="EXPIRED", invalidators=["qualification expired"])
expect_failure(
    "CURRENT receipt reused expired qualification", case,
    "OE_STATIC_QUALIFICATION_REQUIRED")


normalized = module.normalize_static_receipt(noncurrent_positive_receipt())
if normalized.get("schema") != "implementaudit-static-normalized-v1":
    raise SystemExit("normalized static receipt schema missing")
if normalized.get("outcome") != "PARTIAL":
    raise SystemExit("unqualified external positive receipt escaped non-current")
if normalized.get("normalization_identity") != "canonical_json_v1":
    raise SystemExit("static output normalization identity missing")
if normalized.get("qualification", {}).get("self_probe") is not None:
    raise SystemExit("C02 retained caller-issued qualification authority")
if len(normalized.get("facts", [])) != 2:
    raise SystemExit("supported edge/reverse facts missing")
for fact in normalized["facts"]:
    if (fact.get("native_owner_identity") != "fixture/repository" or
            fact.get("authority_ceiling") != "READ_ONLY_STRUCTURAL_FACT"):
        raise SystemExit("static fact native owner/authority ceiling drift")
    provenance = fact.get("provenance", {})
    expected = {
        "collector_identity": "fixture-python-ast",
        "collector_version": "3.11",
        "collector_package_sha256": ZERO64,
        "invocation_identity": "python-ast-static-imports-v1",
        "output_schema_identity": "fixture-static-output-v1",
        "parser_mode": "python-ast-static-imports-v1",
        "configuration_sha256": ONE64,
        "target_snapshot_identity": "fixture-snapshot",
        "input_file_set_sha256": TWO64,
    }
    if provenance != expected:
        raise SystemExit("static fact provenance drift")
if any(fact.get("mapping") is not None for fact in normalized["facts"]):
    raise SystemExit("C02 static normalization invented a governed mapping")
if any(fact.get("work_consequence") != "NONE" for fact in normalized["facts"]):
    raise SystemExit("supported facts invented a work consequence")
if len(normalized.get("semantic_sha256", "")) != 64:
    raise SystemExit("normalized static receipt semantic digest missing")
if module.canonical_json_v1(normalized) != module.canonical_json_v1(
        module.normalize_static_receipt(noncurrent_positive_receipt())):
    raise SystemExit("static normalization is not semantically repeatable")

case = base_receipt()
case["facts"][0]["work_consequence"] = "WORK_DEPENDENCY"
expect_failure("module graph promoted to work DAG", case, "OE_STATIC_AUTHORITY")

case = base_receipt()
case["facts"] = [{
    "id": "missing-computed-edge", "kind": "NO_EDGE", "polarity": "NEGATIVE",
    "source": "src/main.py", "target": "src/dynamic.py",
    "resolution": "RESOLVED", "state": "CURRENT",
    "work_consequence": "NONE", "mapping": None,
}]
expect_failure(
    "unsupported computed edge treated absent", case,
    "OE_STATIC_NEGATIVE_UNQUALIFIED")

case = base_receipt()
case["facts"][0].update({"kind": "ORPHAN", "work_consequence": "DELETE"})
expect_failure(
    "orphan promoted to deletion", case, "OE_STATIC_AUTHORITY")

case = base_receipt()
case["target"]["physical_change"] = True
expect_failure("stale graph reused", case, "OE_STATIC_STALE")

case = base_receipt()
case["invalidators"] = ["collector configuration changed"]
expect_failure(
    "CURRENT receipt retained an invalidator", case, "OE_STATIC_CURRENTNESS")

case = base_receipt()
case["collector"]["executes_target_code"] = True
expect_failure(
    "untrusted target configuration executed", case, "OE_STATIC_TRUST")

case = base_receipt()
case["outcome"] = "PARSER_ERROR"
del case["qualification"]
case["scope"]["parser_complete"] = False
case["diagnostics"]["errors"] = ["src/broken.py: invalid syntax"]
case["facts"] = []
parser_error = module.normalize_static_receipt(case)
if parser_error["outcome"] != "PARSER_ERROR" or not parser_error["facts"]:
    raise SystemExit("parser error became an empty graph")
if parser_error["facts"][0].get("kind") != "PARSER_ERROR_OBSERVATION":
    raise SystemExit("parser-error non-empty control drift")

left = noncurrent_positive_receipt()
left["facts"] = [left["facts"][0]]
right = noncurrent_positive_receipt()
right["collector"]["identity"] = "fixture-second-collector"
right["scope"]["unsupported"] = []
right["scope"]["dynamic_entrypoints_complete"] = True
right["facts"] = [{
    "id": "no-edge-main-helper", "kind": "NO_EDGE", "polarity": "NEGATIVE",
    "source": "src/main.py", "target": "src/helper.py",
    "resolution": "RESOLVED", "state": "CURRENT",
    "work_consequence": "NONE", "mapping": None,
}]
contradictory = module.normalize_static_receipts([left, right])
if contradictory.get("outcome") != "CONTRADICTORY":
    raise SystemExit("contradictory collectors were silently merged")
if len(contradictory.get("facts", [])) != 2:
    raise SystemExit("contradictory provenance was collapsed")
if len({fact["provenance"]["collector_identity"]
        for fact in contradictory["facts"]}) != 2:
    raise SystemExit("overlapping collector provenance was lost")

mismatched = copy.deepcopy(right)
mismatched["target"]["snapshot_identity"] = "different-snapshot"
try:
    module.normalize_static_receipts([left, mismatched])
except module.OperationalEvidenceError as exc:
    if exc.code != "OE_STATIC_SET_MISMATCH":
        raise SystemExit(
            f"snapshot mismatch expected OE_STATIC_SET_MISMATCH, got {exc.code}")
else:
    raise SystemExit("collectors from different target snapshots were combined")

for forbidden in ("READY", "JOIN"):
    case = base_receipt()
    case["facts"][0]["work_consequence"] = forbidden
    expect_failure(
        f"R0038 output setting {forbidden}", case, "OE_STATIC_AUTHORITY")

case = base_receipt()
case["facts"][0].update({
    "kind": "SOURCE_CYCLE", "work_consequence": "WORK_DAG_CYCLE"})
expect_failure(
    "source cycle promoted to work-DAG cycle", case, "OE_STATIC_AUTHORITY")

case = base_receipt()
case["outcome"] = "UNSUPPORTED"
del case["qualification"]
case["scope"]["applicable"] = False
case["scope"]["supported"] = []
case["facts"] = []
unsupported = module.normalize_static_receipt(case)
if unsupported["outcome"] != "UNSUPPORTED" or not unsupported["facts"]:
    raise SystemExit("unsupported collector became an empty graph")
if unsupported["facts"][0].get("kind") != "UNSUPPORTED_OBSERVATION":
    raise SystemExit("unsupported non-empty control drift")

case = base_receipt()
case["outcome"] = "NOT_INSTALLED"
del case["qualification"]
case["facts"] = []
not_installed = module.normalize_static_receipt(case)
if (not_installed["outcome"] != "NOT_INSTALLED" or
        not_installed["facts"][0].get("kind") != "TOOL_UNAVAILABLE_OBSERVATION"):
    raise SystemExit("tool absence fallback drift")

case = base_receipt()
case["outcome"] = "PARTIAL"
case["diagnostics"]["skipped"] = ["src/generated.py"]
del case["qualification"]
partial = module.normalize_static_receipt(case)
if partial["outcome"] != "PARTIAL" or partial["diagnostics"]["skipped"] != [
        "src/generated.py"]:
    raise SystemExit("partial degradation was not preserved")
if any(fact.get("state") == "CURRENT" for fact in partial["facts"]):
    raise SystemExit("non-current external receipt retained CURRENT facts")
PY

run_query_contract
run_diff_export_contract

printf 'operational-evidence-contract.test: ok\n'
