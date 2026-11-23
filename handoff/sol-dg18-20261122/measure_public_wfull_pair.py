"""Measure the exact public accepted W-FULL STATE/ROADMAP readbacks in memory."""
import argparse
import hashlib
import importlib.util
import io
import json
import platform
import subprocess
import sys
from pathlib import Path
import zipfile


ROOT = Path(__file__).resolve().parents[2]
CONSUMER = "51416b2f156b341c4a5f09029e2c6ceb5b30b1e7"
RESULTS = "6431a1d1e067ab37e4f461caa4a61890d69e7c14"
GIT_PREFIX = RESULTS + ":handoff/pro-executor-results-20261115/authorized-execution-20261116/dg18/wfull/"
OWNER = "skills/implementaudit/scripts/rotate-canonical-state.py"
ARCHIVE_PREFIX = "dg18-w-full-43785700341-1/operation/"
ENCODING_SHA = "223921b76ee99bde995b7ff738513eef100fb51d18c93597a113bcffe865b2a7"


def require(value, message):
    if not value:
        raise ValueError(message)


def git_bytes(object_name):
    return subprocess.check_output(["git", "cat-file", "blob", object_name], cwd=ROOT, timeout=15)


def sha256(raw):
    return hashlib.sha256(raw).hexdigest()


def blob(raw):
    return hashlib.sha1(f"blob {len(raw)}\0".encode("ascii") + raw).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")


def recorded_pair(archive, paths, pointer, check_paths=None):
    results = []
    for role, path in paths.items():
        raw = archive.read(ARCHIVE_PREFIX + path + ".stdout")
        record = json.loads(archive.read(ARCHIVE_PREFIX + path + ".json"))
        require(record["exit_code"] == 0 and record["stdout_sha256"] == sha256(raw)
                == pointer[role.lower() + "_sha256"], f"archived {role} command/pointer disagrees")
        if check_paths is not None:
            require(raw == archive.read(ARCHIVE_PREFIX + check_paths[role] + ".stdout"),
                    f"preflight and launch {role} bytes disagree")
        results.append((role, ARCHIVE_PREFIX + path + ".stdout", raw))
    return results


def read_operation():
    receipt = json.loads(git_bytes(GIT_PREFIX + "ROOT_SCOPED_RECEIVING.json"))
    require(receipt["root_decision"] == "ACCEPT_AT_EXACT_DECLARED_WINDOWS_OPERATION_SCOPE"
            and receipt["actual_run"] == "43795345593" and receipt["run_attempt"] == 1,
            "unexpected scoped receiving")
    raw = git_bytes(GIT_PREFIX + "ARTIFACT.zip")
    require((len(raw), sha256(raw)) == (receipt["actual_archive"]["bytes"], receipt["actual_archive"]["sha256"]),
            "public operation archive differs from accepted bytes")
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        names = archive.namelist()
        require(len(names) == len(set(names)) == receipt["actual_archive"]["member_count"],
                "archive member census differs")
        plan_raw = archive.read(ARCHIVE_PREFIX + "OPERATION.json")
        result = json.loads(archive.read(ARCHIVE_PREFIX + "execution/RESULT.json"))
        require(sha256(plan_raw) == result["plan_sha256"] == receipt["operation_sha256"],
                "actual accepted operation differs")
        plan = json.loads(plan_raw)["prepared"]
        require(plan["snapshot"]["source_head"] == receipt["runtime_commit"], "operation runtime source differs")
        before = plan["before"]
        after = json.loads(archive.read(ARCHIVE_PREFIX + "execution/CURRENT.json"))
        require(before["boundary"] == "manual-resume" and before["pointer"]["continuity_epoch"] == "G0002"
                and after["pointer"]["continuity_epoch"] == "G0003"
                and after["pointer"]["predecessor_receipt_ref_oid"] == before["receipt_token"]
                and after["pointer_token"] == receipt["pointer_token"] and after["receipt_token"] == receipt["receipt_token"],
                "archived scope or generation sequence differs")
        for item in (before, after):
            require(blob(canonical(item["pointer"])) == item["pointer_token"].split("@")[1],
                    "pointer object does not match its exact token")
        receipt_raw = archive.read(ARCHIVE_PREFIX + "execution/RECEIPT.raw")
        receipt_fields = receipt_raw.decode("utf-8").split("\t")
        require(len(receipt_fields) == 14 and blob(receipt_raw) == receipt["receipt_token"].split("@")[1]
                and receipt_fields[7] == after["pointer_token"].split("@")[1]
                and receipt_fields[8:10] == [after["pointer"]["state_sha256"], after["pointer"]["roadmap_sha256"]],
                "historical receipt does not bind the exact current pair")
        pre = recorded_pair(archive, {"STATE": "execution/preflight/03-STATE", "ROADMAP": "execution/preflight/04-ROADMAP"},
                            before["pointer"], {"STATE": "execution/launch-preflight/03-STATE", "ROADMAP": "execution/launch-preflight/04-ROADMAP"})
        post = recorded_pair(archive, {"STATE": "execution/current-STATE", "ROADMAP": "execution/current-ROADMAP"},
                             after["pointer"])
        kept = json.loads(archive.read(ARCHIVE_PREFIX + "execution/PRESERVED_AFTER.json"))
        for role, _, body in pre:
            require(kept["files"][role] == {"bytes": len(body), "sha256": sha256(body)},
                    "historical preimage retention differs")
        for metric in ("elapsed_ms", "peak_job_committed_bytes"):
            require(result["measurement"][metric] == receipt["measurement"][metric], "recorded cost receiving differs")
    return receipt, pre, post, before["pointer_token"], before["receipt_token"]


def measure(encoding_path):
    encoding = encoding_path.read_bytes()
    require((len(encoding), sha256(encoding)) == (1681126, ENCODING_SHA), "exact pinned tokenizer encoding required")
    owner = ROOT / OWNER
    require(owner.read_bytes() == git_bytes(CONSUMER + ":" + OWNER), "counting owner changed")
    spec = importlib.util.spec_from_file_location("rotation_cost_source", owner)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    receipt, pre, post, pointer, receipt_token = read_operation()
    counts = module.count_rotation_tokens_v1(encoding, tuple(row[2] for row in pre + post))
    rows = {(role, path): {"role": role, "member": path, "bytes": len(raw), "sha256": sha256(raw), "tokens": tokens}
            for (role, path, raw), tokens in zip(pre + post, counts, strict=True)}
    pre_rows = [rows[(role, path)] for role, path, _ in pre]
    post_rows = [rows[(role, path)] for role, path, _ in post]
    before = {key: sum(row[key] for row in pre_rows) for key in ("bytes", "tokens")}
    after = {key: sum(row[key] for row in post_rows) for key in ("bytes", "tokens")}
    reduction = {key: before[key] - after[key] for key in ("bytes", "tokens")}
    payoff = module.rotation_payoff_v1(reduction["bytes"], reduction["tokens"])
    require(encoding_path.read_bytes() == encoding and owner.read_bytes() == git_bytes(CONSUMER + ":" + OWNER),
            "token measurement input/source changed")
    return {
        "schema": "dg18.a5.public-pair-cost.v1", "consumer_commit": CONSUMER, "historical_results_commit": RESULTS,
        "historical_run": receipt["actual_run"], "historical_runtime_commit": receipt["runtime_commit"],
        "archived_transition": "G0002 to G0003 manual resume", "historical_scope": receipt["root_decision"],
        "archive_sha256": receipt["actual_archive"]["sha256"], "operation_sha256": receipt["operation_sha256"],
        "historical_pointer_before": pointer, "historical_pointer_after": receipt["pointer_token"],
        "historical_receipt_before": receipt_token, "historical_receipt_after": receipt["receipt_token"],
        "pre": pre_rows, "post": post_rows, "pre_totals": before, "post_totals": after, "reduction": reduction,
        "applying_rotation_payoff_calculation_as_diagnostic": payoff,
        "rotator_trigger_checks_on_archived_input": {
            "byte_arm": before["bytes"] >= 131072, "token_arm": before["tokens"] >= 32768,
            "host_health": "UNAVAILABLE",
        },
        "historical_job_measurement": receipt["measurement"],
        "tokenizer": {"name": "cl100k_base", "version": "0.13.0", "encoding_sha256": ENCODING_SHA,
                      "local_python": platform.python_version()},
        "currentness": "historical receipt/pointer identity readback only",
        "original_a5_accepted": False, "host_metering_operation": False, "native_input_consumed": False,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--encoding", required=True, type=Path)
    args = parser.parse_args()
    print(json.dumps(measure(args.encoding), indent=2))
