"""Read-only Q02 ordering proof over retained actual CI and original M2 receiving."""

from datetime import datetime
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys


HERE = Path(__file__).parent
REPO = "repos/theislampill/IMPLEMENTAUDIT.md"
PRIOR_PRODUCT = "14ed4c7179d477d90882ebf5c5031692056e5491"
PRIOR_LOG = {"bytes": 229426, "sha256": "342e0572654dce775dd9f6899e39e26eb7498c36748cc8c54cd7bd198326a954"}
CURRENT_LOG = {"bytes": 569919, "sha256": "7d58c311832168a01e8dc12841d4b770bd16a1873e63a7063ecc0d64f962b893"}
FOCUSED = (
    "test_both_current_compilers_load_exact_transport_and_refuse_substitution",
    "test_combined_read_closure_is_selected_and_changed_member_refuses",
    "test_combined_route_producer_is_source_selected",
    "test_engineered_profiles_select_current_bytes_and_preserve_every_historical_domain",
    "test_prior_windows_capture_profile_has_exact_physical_members",
    "test_windows_capture_receiver_platform_shapes_and_refusals",
    "test_current_c5_changed_source_or_selection_refuses_before_output",
    "test_current_c5_unknown_selection_refuses",
    "test_registry_preimages_refuse_current_pins_and_changed_specimens",
)


def previous_checker():
    spec = importlib.util.spec_from_file_location("v01_read_only", HERE.parent / "original-v01" / "verify_v01.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def github(path):
    return subprocess.check_output(["gh", "api", f"{REPO}/{path}"])


def timestamp(line):
    return datetime.fromisoformat(line.split(" ", 1)[0].replace("Z", "+00:00"))


def direct_ci(v, job_id, run_id, subject, expected_log, conclusion):
    job = json.loads(github(f"actions/jobs/{job_id}"))
    v.require((job["id"], job["run_id"], job["run_attempt"], job["head_sha"], job["conclusion"])
              == (job_id, run_id, 1, subject, conclusion), "exact CI job")
    raw = github(f"actions/jobs/{job_id}/logs")
    v.require(v.pin(raw) == expected_log, "exact raw CI log")
    workflow = v.blob(subject, ".github/workflows/validate.yml")
    v.require(re.search(rb"(?m)^      - name: Verify package contract\n        run: bash scripts/verify-package\.sh$", workflow),
              "actual workflow canonical command")
    steps = {item["number"]: item for item in job["steps"]}
    step = steps[10]
    v.require(step["name"] == "Verify package contract" and step["conclusion"] == conclusion,
              "actual canonical step conclusion")
    lines = raw.decode("utf-8").splitlines()
    started, = [i for i, line in enumerate(lines) if line.endswith("##[group]Run bash scripts/verify-package.sh")]
    marker = [i for i, line in enumerate(lines) if line.endswith(" verify-package: ok")]
    v.require(len(marker) == (1 if conclusion == "success" else 0)
              and timestamp(lines[started]).replace(microsecond=0) == timestamp(step["started_at"]),
              "canonical step trace")
    if marker:
        v.require(timestamp(lines[marker[0]]).replace(microsecond=0) == timestamp(step["completed_at"]),
                  "canonical terminal trace")
    return {"id": job_id, "run": run_id, "attempt": 1, "source": subject,
            "workflow": v.pin(workflow), "log": expected_log, "canonical_step": step,
            "canonical_start_line": started + 1, "canonical_terminal_line": marker[0] + 1 if marker else None}, steps, lines


def focused_current(v, lines):
    states = {}
    for name in FOCUSED:
        line, = [i for i, item in enumerate(lines) if re.search(r"Z " + re.escape(name) + r" \(", item)]
        end = line if lines[line].endswith("... ok") else line + 1
        v.require(lines[end].endswith("... ok") or re.search(r"Z ok$", lines[end]), "expected focused regression record")
        states[name] = {"start_log_line": line + 1, "completion_log_line": end + 1,
                        "completed_at": timestamp(lines[end]).isoformat(), "recorded_ok": True}
    summary = next(i for i, item in enumerate(lines) if re.search(r"Z Ran 83 tests in ", item))
    v.require(lines[summary + 2].endswith("OK (skipped=2)"), "focused composite skipped controls")
    return {"selected_checks": states, "composite_suite": {"tests": 83, "skips": 2,
                                                          "summary_log_line": summary + 3}}


def failure_evidence(v, lines):
    previous = {}
    for n in FOCUSED:
        matched = [i + 1 for i, line in enumerate(lines) if re.search(r"Z (?:FAIL|ERROR): " + re.escape(n) + r" \(", line)]
        if matched:
            previous[n] = matched
    v.require(len(previous) >= 5 and any(line.endswith("FAILED (failures=9, errors=4, skipped=2)") for line in lines),
              "actual predecessor red")
    history, retained = "recovery/contracts/evidence", f"{v.RESULTS_ROOT}/original-acceptance/dg16-g2/receiving-retention-correction"
    early = json.loads(v.blob(v.WORK_ORDER, f"{history}/G2_ROOT_TERMINAL_DECISION.json"))
    v.require(early["run"] == 42579780645 and early["scoped_receiving"]["legacy_verifier_exit"] == 1
              and early["scoped_receiving"]["dag_verifier_executed"] is False,
              "actual historical original verifier failure")
    rejected = json.loads(v.blob(v.WORK_ORDER, f"{history}/RETAINED_PR255_CI_FAILURE.json"))
    v.require(rejected["outcome_flags"]["CONTINUITY_TRANSPORT_NAMESPACE_REFUSED"] is True
              and any(step["conclusion"] == "skipped" and step["name"] == "Verify package contract" for step in rejected["steps"]),
              "actual historical policy refusal and skipped verifier")
    red = json.loads(v.blob(v.RESULTS, f"{retained}/RED.json"))
    green = json.loads(v.blob(v.RESULTS, f"{retained}/GREEN.json"))
    correction = json.loads(v.blob(v.RESULTS, f"{retained}/ROOT_SOURCE_RECEIVING.json"))
    v.require((red["exit"], green["exit"]) == (1, 0)
              and correction["underlying_relation_and_witness"] == "UNKNOWN_NOT_RECOVERED",
              "retention red/green boundary")
    return {
        "prior_exact_composite_check_failure_log_lines": previous,
        "prior_exact_composite_summary": {"failures": 9, "errors": 4, "skips": 2},
        "actual_legacy_nonzero_DAG_not_started": {"run": early["run"], "source": early["source"], "cause": "UNPROVED"},
        "CI_continuity_policy_refusal_verifier_skipped": {"run": rejected["run"]["id"]},
        "acceptance_artifact_retention_control": {"RED": red["exit"], "GREEN": green["exit"],
                                                 "underlying_original_witness": correction["underlying_relation_and_witness"]},
    }


def read_m2(v, preceding):
    decision, probes, decision_pin, archive_pin = v.m2_records()
    job = json.loads(github(f"actions/jobs/{decision['job_id']}"))
    v.require((job["head_sha"], job["run_id"], job["run_attempt"]) ==
              (decision["workflow_commit"], decision["run_id"], 1), "actual original M2 workflow identity")
    source = {item["number"]: item for item in job["steps"]}
    order = [source[n] for n in (12, 13, 14, 15, 16, 17)]
    v.require(all(step["conclusion"] == "success" for step in order)
              and all(timestamp(x["completed_at"]) <= timestamp(y["started_at"]) for x, y in zip(order, order[1:]))
              and preceding < timestamp(source[14]["started_at"])
              and source[14]["name"] == "Qualify the fresh nine-case current-source native bank"
              and source[15]["name"] == "Receive all nine native cases and the unchanged two-case port"
              and source[16]["name"] == "Execute the complete current registry legacy then DAG once",
              "ordered focused/currentness/receiving steps before canonical operation")
    for probe in probes:
        receiver = probe["result"]
        v.require((receiver["source_commit"], receiver["source_tree"]) == (v.PRODUCT, v.TREE)
                  and receiver["subject_verifier_attempts"] == 2 and receiver["same_live_source_current"]
                  and [(r["mode"], r["exit"]) for r in receiver["records"]] == [("legacy", 0), ("dag", 0)],
                  "exact retained canonical legacy operation and source")
        phases = [p["name"] for p in probe["phases"] if p["status"] == "COMPLETED"]
        v.require(phases.index("native-bank") < phases.index("native-receive") < phases.index("pair"),
                  "independent M2 phase order")
    return {"run": decision["run_id"], "job": decision["job_id"], "workflow": decision["workflow_commit"],
            "qualifying_steps": order, "published_decision": decision_pin, "public_archive": archive_pin,
            "legacy_and_DAG_exit": [0, 0], "source": v.PRODUCT, "tree": v.TREE}


def main():
    v = previous_checker()
    row_map = json.loads(v.blob(v.RESULTS, v.ROW_MAP))
    contract = json.loads(v.blob(v.WORK_ORDER, "recovery/contracts/original/DEFINITIONS_48_20_117_12.json"))
    row = next(r for r in row_map["rows"] if r["criterion_id"] == "R35-Q02")
    literal = next(r for r in contract["original48"] if r["id"] == "R35-Q02")
    v.require(row["original_text"] == literal["requirement_exact"]
              and row["original_scope_and_binding"] == literal["original_scope_and_binding_exact"]
              and row["mandatory_operation_or_consumer_references"] == ["M2"] and row["conditional_references"] == [],
              "Q02 exact original requirement")
    prior, _, failed = direct_ci(v, 135972383182, 44641197003, PRIOR_PRODUCT, PRIOR_LOG, "failure")
    current, steps, passed = direct_ci(v, 136022135798, 44655969487, v.PRODUCT, CURRENT_LOG, "success")
    v.require([steps[n]["name"] for n in (8, 9)] == ["Validate whitespace", "Validate package-owner JSON"]
              and all(steps[n]["conclusion"] == "success" for n in (8, 9))
              and timestamp(steps[9]["completed_at"]) <= timestamp(steps[10]["started_at"]), "actual preparatory checks")
    focused = focused_current(v, passed)
    last = max(timestamp(record["completed_at"]) for record in focused["selected_checks"].values())
    v.require(timestamp(prior["canonical_step"]["completed_at"]) < timestamp(current["canonical_step"]["started_at"])
              <= last < timestamp(current["canonical_step"]["completed_at"]), "prior red / focused exact-source result order")
    result = {
        "schema": "dg16.original-q02.retained-ordering-receiving.v1",
        "row": {"id": "R35-Q02", "literal": literal["requirement_exact"],
                "scope": literal["original_scope_and_binding_exact"], "original_rows": len(contract["original48"])},
        "prior_ci": prior, "current_exact_ci": current, "current_ci_preparatory_steps": [steps[n] for n in (8, 9)],
        "focused_exact_source_regressions_in_earlier_ci": focused,
        "later_original_m2_order_and_receiving": read_m2(v, last),
        "historical_distinctions": failure_evidence(v, failed),
        "recommendation": "ACCEPT_ORIGINAL_R35_Q02_AT_EXACT_51416_WITNESSED_SCOPE",
        "original_awards": [], "independent_root_receiving_pending": True, "m6_credit": False,
        "full_verifier_rerun": False, "native_or_protected_operation_here": False,
    }
    sys.stdout.buffer.write((json.dumps(result, sort_keys=True, indent=2) + "\n").encode())


if __name__ == "__main__":
    main()
