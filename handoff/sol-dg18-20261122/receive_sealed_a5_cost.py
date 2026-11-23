"""Receive the two frozen G0033/G0034 archives without extracting their contents."""
import argparse
import hashlib
import importlib.util
import io
import json
from pathlib import Path, PurePosixPath
import subprocess
import sys
import tarfile
import zipfile

ROOT = Path(__file__).resolve().parents[2]
SOURCE = "51416b2f156b341c4a5f09029e2c6ceb5b30b1e7"
TREE = "9c3913ceaa95f3f36b0377fe2dba4a302afcba89"
RESULTS = "6431a1d1e067ab37e4f461caa4a61890d69e7c14"
PUBLISHED = "handoff/pro-executor-results-20261115/continuing-execution-20261121-28/A5_CURRENT_COLD_AND_N01_RESULT.json"
OWNER = "skills/implementaudit/scripts/rotate-canonical-state.py"
STAGE2_REPORT = "independent-receiving/stage2_report.json"
STAGE2_SEAL = "independent-receiving/STAGE2_SEAL.json"
DECISION = "root/DG18_A5_CURRENT_CONSUMER_ROOT_DECISION.json"
RECEIPT_FIELDS = (
    "schema", "controller", "claim_id", "run_root_identity", "continuity_epoch", "invalidation_oid",
    "pointer_ref", "pointer_oid", "state_sha256", "roadmap_sha256", "protected_manifest_sha256",
    "archive_manifest_sha256", "exact_next_action", "predecessor_receipt_ref_oid",
)
ENCODING_SHA = "223921b76ee99bde995b7ff738513eef100fb51d18c93597a113bcffe865b2a7"


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def pin(raw):
    return {"bytes": len(raw), "sha256": sha(raw)}


def oid(raw):
    return hashlib.sha1(f"blob {len(raw)}\0".encode("ascii") + raw).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode()


def strict(raw):
    def pairs(rows):
        values = dict(rows)
        need(len(values) == len(rows), "duplicate JSON key")
        return values
    return json.loads(raw, object_pairs_hook=pairs)


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT, timeout=15)


def read_pinned(path, expected):
    need(path.stat().st_size == expected["bytes"], "input byte bound")
    raw = path.read_bytes()
    need(pin(raw) == {k: expected[k] for k in ("bytes", "sha256")}, "input identity")
    return raw


def zip_members(raw, count):
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        infos = z.infolist()
        need(len(infos) == len(set(z.namelist())) == count
             and sum(i.file_size for i in infos) < 4_000_000, "closed ZIP population")
        rows, modes = {}, {}
        for info in infos:
            name = PurePosixPath(info.filename)
            need(not name.is_absolute() and name.as_posix() == info.filename and ".." not in name.parts
                 and not info.is_dir() and not info.flag_bits & 1
                 and ((info.external_attr >> 16) & 0o170000) in (0, 0o100000), "nonregular or unbounded ZIP member")
            rows[info.filename] = z.read(info)
            modes[info.filename] = f"{(info.external_attr >> 16) & 0o777:04o}"
    manifest = strict(rows["ARTIFACT_MANIFEST.json"])
    entries = manifest["files"]
    need(len(entries) == count - 1 and {item["path"] for item in entries} == set(rows) - {"ARTIFACT_MANIFEST.json"},
         "ZIP manifest membership differs")
    for item in entries:
        path = item["path"]
        need(pin(rows[path]) == {k: item[k] for k in ("bytes", "sha256")} and modes[path] == item["mode"],
             "ZIP manifest bytes, hash, or mode mismatch")
    return rows, manifest


def confirm_source(execution):
    material = strict(execution["CURRENT_SOURCE_MATERIALIZATION.json"])
    need((material["commit"], material["tree"], material["count"]) == (SOURCE, TREE, 84), "source materialization")
    tree = {}
    for line in git("ls-tree", "-rz", SOURCE).split(b"\0"):
        if not line:
            continue
        head, name = line.decode().split("\t", 1)
        tree[name] = head.split()
    for dep in material["dependencies"]:
        name = dep["path"]
        raw = execution["source-51416/" + name]
        actual = (str(len(raw)), sha(raw), oid(raw))
        expected = (str(dep["current_bytes"]), dep["current_sha256"], dep["current_git_blob"])
        need(actual == expected and dep["readback_sha256"] == actual[1]
             and tree[name] == [dep["current_git_mode"], "blob", actual[2]], "source materialization row differs")
    need(len({row["path"] for row in material["dependencies"]}) == 84
         and sum(n.startswith("source-51416/") for n in execution) == 84, "source denominator")


def verify_wire(algebra, post):
    pointer, receipt, marker = (algebra[key] for key in ("pointer", "receipt_fields", "marker_fields"))
    ptr_ref, ptr_oid = algebra["pointer_token"].split("@", 1)
    rec_ref, rec_oid = algebra["receipt_token"].split("@", 1)
    need(len(receipt) == 14 and set(receipt) == set(RECEIPT_FIELDS) and len(marker) == 10, "receipt/marker shape")
    refs = {x["ref"]: x for x in algebra["object_bindings"]}
    objects = {x["oid"]: x for x in algebra["object_bindings"]}
    need(len(refs) == 95 and len(algebra["archive_entries"]) == 83
         and ptr_oid == refs[ptr_ref]["oid"] and rec_oid == refs[rec_ref]["oid"], "object map disagreement")
    wires = (
        (ptr_oid, canonical(pointer)),
        (rec_oid, ("\t".join(receipt[k] for k in RECEIPT_FIELDS) + "\n").encode()),
        (algebra["marker_oid"], "\t".join(marker).encode()),
    )
    for expected, body in wires:
        need(oid(body) == expected and pin(body) == {k: objects[expected][k] for k in ("bytes", "sha256")},
             "sealed field wire algebra differs")
    for k in set(RECEIPT_FIELDS) & set(pointer) - {"schema"}:
        need(receipt[k] == pointer[k], "receipt pointer binding differs")
    need(receipt["pointer_ref"] == ptr_ref and receipt["pointer_oid"] == ptr_oid
         and pointer["expected_receipt_ref_schema"] == {"ref": rec_ref, "schema": receipt["schema"]}, "receipt route differs")
    need(marker[1:10] == [pointer["controller"], pointer["claim_id"], pointer["run_root_identity"], "G0002",
                         ptr_ref, pointer["schema"], rec_ref, rec_oid, "true"], "historical marker join differs")
    for role, data in post.items():
        need(sha(data) == pointer[role.lower() + "_sha256"], "postimage not the pointer-bound body")
    return {"receipt_fields": 14, "marker_fields": 10, "archive_entries": 83, "object_bindings": 95,
            "pointer_receipt_marker_wire_pins": [pin(data) for _, data in wires],
            "meaning": "exact historical field serialization and ref identifiers, no live currentness"}


def read_historical_pair(path, execution, execution_manifest, prelaunch, algebra, pins):
    """Stream the exact historical TAR and retain only the two preimage bodies and seals."""
    receiving = strict(execution["FULL_PACKET_RECEIVING.json"])
    carrier_pin = {
        "bytes": 4177344,
        "sha256": "cd1288b2d6d6f8172bf0e2a265aee8aa9d2b4648fe3ef8bb43d09d838968eae2",
    }
    need(carrier_pin == {key: receiving["archive"][key] for key in carrier_pin}
         == {key: execution_manifest["historical_carrier_not_duplicated"][key] for key in carrier_pin},
         "historical carrier reference changed")
    carrier = read_pinned(path, carrier_pin)
    prefix = "authentic-inputs/composed-packet/"
    base = "historical/h002/operation/receiver-packet/operation-evidence/preimage/"
    expected = {"CANDIDATE_MANIFEST.json": receiving["exact_manifest"],
                "CANDIDATE_SEAL.json": receiving["exact_seal"]}
    selected = {}
    for role, ordinal, archive_ordinal in (("STATE", 657, 0), ("ROADMAP", 656, 1)):
        name = base + role + ".md"
        row = prelaunch["files"][ordinal]
        archive_row = algebra["archive_entries"][archive_ordinal]
        need(row["path"] == prefix + name and archive_row["artifact_id"] == role
             and archive_row["role"] == role + "_PREIMAGE" and archive_row["source_path"] == role + ".md"
             and row["mode"] == archive_row["mode"] and row["bytes"] == pins[role]["bytes"]
             and row["sha256"] == pins[role]["sha256"], "sealed historical preimage role/path/ordinal differs")
        expected[name] = {key: pins[role][key] for key in ("bytes", "sha256")}
        selected[role] = name
    members, received = {}, {}
    expanded = 0
    limit = receiving["payload_bytes"] + receiving["exact_manifest"]["bytes"] + receiving["exact_seal"]["bytes"]
    with tarfile.open(fileobj=io.BytesIO(carrier), mode="r|gz") as archive:
        for item in archive:
            name = PurePosixPath(item.name)
            expanded += item.size
            need(len(members) < receiving["archive_members"] and 0 <= item.size <= limit and expanded <= limit
                 and item.isfile() and not name.is_absolute() and name.as_posix() == item.name
                 and "\\" not in item.name and ":" not in item.name and ".." not in name.parts
                 and item.name not in members, "unsafe or duplicate historical archive member")
            members[item.name] = (item.size, f"{item.mode:04o}")
            if item.name in expected:
                pin_expected = expected[item.name]
                need(item.size == pin_expected["bytes"], "historical selected member size differs")
                with archive.extractfile(item) as stream:
                    body = stream.read(item.size + 1)
                need(pin(body) == pin_expected, "historical selected member digest differs")
                received[item.name] = body
    need(len(members) == receiving["archive_members"] == 784 and expanded == limit
         and set(received) == set(expected), "incomplete historical archive population")
    manifest = strict(received["CANDIDATE_MANIFEST.json"])
    listed = {r["path"]: r for r in manifest["files"]}
    need(len(listed) == len(manifest["files"]) == manifest["file_count"] == 782
         and set(listed) | {"CANDIDATE_MANIFEST.json", "CANDIDATE_SEAL.json"} == set(members)
         and sum(r["bytes"] for r in listed.values()) == manifest["total_bytes"] == receiving["payload_bytes"],
         "historical input manifest population differs")
    for name, row in listed.items():
        need(members[name] == (row["bytes"], row["mode"]), "historical archive member shape differs")
    pre = {role: received[name] for role, name in selected.items()}
    for role, name in selected.items():
        need(listed[name]["sha256"] == pins[role]["sha256"] and oid(pre[role]) == pins[role]["git_blob"],
             "historical preimage manifest or Git blob differs")
    need(read_pinned(path, carrier_pin) == carrier, "historical carrier drift during receipt")
    return pre


def measure(args):
    published = strict(git("cat-file", "blob", RESULTS + ":" + PUBLISHED))
    record = published["dg18_a5"]
    e_pin, r_pin = published["durable_exact_evidence"]
    e_raw, r_raw = read_pinned(args.execution, e_pin), read_pinned(args.receiving, r_pin)
    e, em = zip_members(e_raw, 127)
    r, _ = zip_members(r_raw, 9)
    need(pin(r[DECISION]) == {"bytes": record["root_decision_bytes"], "sha256": record["root_decision_sha256"]},
         "Root decision differs from published exact digest")
    decision, review, seal = strict(r[DECISION]), strict(r[STAGE2_REPORT]), strict(r[STAGE2_SEAL])
    need(pin(r[STAGE2_REPORT]) == {k: seal["report"][k] for k in ("bytes", "sha256")}
         and sha(r[STAGE2_REPORT]) == record["independent_report_sha256"]
         and sha(r[STAGE2_SEAL]) == record["independent_seal_sha256"], "independent receipt hashes differ")
    need(pin(e_raw) == {k: seal["execution_zip"][k] for k in ("bytes", "sha256")}
         == {k: decision["execution_artifact"][k] for k in ("bytes", "sha256")}, "cross-archive execution identity differs")
    need(sha(canonical(review["observed_complete_census"])) == seal["complete_input_census_sha256"]
         and len(review["observed_complete_census"]) == seal["complete_input_census_count"] == 911, "independent census seal differs")
    frozen = strict(r["independent-receiving/FREEZE_SEAL.json"])
    release = strict(r["independent-receiving/ROOT_STAGE2_RELEASE.json"])
    need(frozen["frozen_at_utc"] < release["at_utc"] < seal["sealed_at_utc"]
         and frozen["stage2_read"] is False and seal["stage1_frozen_before_stage2"], "cold independence ordering")
    need(sha(r["independent-receiving/FREEZE_SEAL.json"]) == release["freeze_seal_sha256"]
         and sha(r["independent-receiving/five_fields.json"]) == release["frozen_stage1_sha256"]
         and sha(e["original/STAGE1_SEAL.json"]) == frozen["supplied_stage1_seal"]["sha256"], "cold freeze binds different bytes")
    for seal_name in ("original/STAGE1_SEAL.json", "original/OUTPUT_SEAL.json"):
        for item in strict(e[seal_name])["files"]:
            path = item["path"][item["path"].rfind("/original/") + 1:]
            need(pin(e[path]) == {k: item[k] for k in ("bytes", "sha256")}, "G0033 stage seal differs")
    admission, intent, ret = (strict(e[path]) for path in ("ROOT_ADMISSION.json", "actual-execution/INTENT.json",
                                                            "actual-execution/ACTUAL_RETURN.json"))
    need(len({x["operation"] for x in (admission, intent, ret, record, em, decision["consumer"])}) == 1
         and sha(e["ROOT_ADMISSION.json"]) == intent["admission_sha256"]
         and sha(e["actual-execution/stdout.txt"]) == ret["stdout_sha256"]
         and sha(e["actual-execution/stderr.txt"]) == ret["stderr_sha256"], "actual operation binding differs")
    need(admission["source"] == SOURCE and admission["source_tree"] == TREE
         and admission["native_operations_authorized"] is False
         and ret["exit_code"] == 0 and ret["elapsed_ns"] == decision["cost_scope"]["outer_process_elapsed_ns"],
         "actual execution scope differs")
    need(decision["decision"] == record["root_decision"] and decision["complete_original_A5_accepted"] is False
         and len(decision["nine_amended_contributions"]) == 9 and not decision["new_complete_original_criteria"],
         "Root award scope differs")
    initial = strict(e["PRELAUNCH_MANIFEST.json"])
    consumed = strict(e["ORIGINAL_LAUNCH_CONSUMED.json"])
    need(sha(e["PRELAUNCH_MANIFEST.json"]) == consumed["prelaunch_manifest_sha256"]
         == admission["prelaunch_manifest_sha256"] == decision["consumer"]["prelaunch_manifest_sha256"]
         and sha(e["current_a5_consumer.py"]) == consumed["entry_sha256"] == admission["entry_sha256"]
         and sha(e["ROOT_ADMISSION.json"]) == consumed["root_admission_sha256"]
         and consumed["operation"] == ret["operation"], "exact frozen entry or single-use binding differs")
    need(len(initial["files"]) == initial["file_count"] == record["complete_frozen_input_files"]
         and sum(row["bytes"] for row in initial["files"]) == initial["total_bytes"] == record["complete_frozen_input_bytes"],
         "frozen prelaunch descriptor denominator")
    product_return = strict(e["original/stage2/CURRENT_CONSUMER_RESULT.json"])
    read_only = decision["cost_scope"]
    need(read_only == review["actual_cost_scope"] and product_return["runtime"]["elapsed_ns"] == read_only["inner_consumer_elapsed_ns"]
         and product_return["runtime"]["process_cpu_ns"] == read_only["inner_consumer_cpu_ns"]
         and product_return["runtime"]["maxrss_linux_kib"] == read_only["linux_self_maxrss_kib_at_sample"]
         and product_return["native_owner_operations"] == product_return["actual_current_native_runtime_observations"] == 0,
         "accepted cost interval or native ceiling differs")
    confirm_source(e)
    algebra = strict(e["original/stage2/CANONICAL_ALGEBRA.json"])
    post = {role: e[f"original/stage1/{role}.md"] for role in ("STATE", "ROADMAP")}
    wire = verify_wire(algebra, post)
    pre_pins = {row["artifact_id"]: {"bytes": row["byte_length"], "sha256": row["sha256"], "git_blob": row["blob_oid"]}
                for row in algebra["archive_entries"] if row["role"] in ("STATE_PREIMAGE", "ROADMAP_PREIMAGE")}
    for row in review["independent_recomputation"]["derived_pairs"]:
        role = row["role"]
        need(pin(post[role]) == {"bytes": row["derived_bytes"], "sha256": row["derived_sha256"]}
             and pre_pins[role]["sha256"] == row["preimage_sha256"] and pre_pins[role]["bytes"] == row["preimage_bytes"],
             "cold pre/post pair descriptors differ")
    files_given = args.preimage_state is not None and args.preimage_roadmap is not None
    need(files_given or (args.preimage_state is None and args.preimage_roadmap is None), "provide both optional exact preimage bodies")
    need(not (files_given and args.historical_carrier is not None), "choose exact preimage files or the historical carrier")
    pre = {}
    if args.historical_carrier is not None:
        pre = read_historical_pair(args.historical_carrier, e, em, initial, algebra, pre_pins)
    elif files_given:
        for role, path in (("STATE", args.preimage_state), ("ROADMAP", args.preimage_roadmap)):
            pre[role] = read_pinned(path, pre_pins[role])
            need(oid(pre[role]) == pre_pins[role]["git_blob"], "wrong preimage Git blob")
    kept = bool(pre)
    encoding = read_pinned(args.encoding, {"bytes": 1681126, "sha256": ENCODING_SHA})
    owner = ROOT / OWNER
    need(owner.read_bytes() == git("cat-file", "blob", SOURCE + ":" + OWNER), "token counting owner differs")
    spec = importlib.util.spec_from_file_location("sealed_a5_token_owner", owner)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    counts = module.count_rotation_tokens_v1(encoding, tuple(pre.values()) + tuple(post.values()))
    pre_counts, post_counts = (dict(zip(pre, counts[:2], strict=True)), dict(zip(post, counts[2:], strict=True))) if kept else (None, dict(zip(post, counts, strict=True)))
    byte_reduction = sum(v["bytes"] for v in pre_pins.values()) - sum(map(len, post.values()))
    need(byte_reduction == decision["cost_scope"]["pair_byte_reduction"] == 193436, "exact byte reduction arithmetic differs")
    token_reduction = sum(pre_counts.values()) - sum(post_counts.values()) if kept else None
    need(read_pinned(args.execution, e_pin) == e_raw and read_pinned(args.receiving, r_pin) == r_raw,
         "original archive bytes drifted during receipt")
    return {
        "schema": "dg18.a5.sealed-cost-receiving.v1", "source": SOURCE, "tree": TREE, "operation": ret["operation"],
        "execution_zip": pin(e_raw), "receiving_zip": pin(r_raw), "exact_zip_members_verified": [127, 9],
        "exact_source_members_verified": 84, "sealed_census_descriptor_rows": 911, "raw_census_population_reverified": False,
        "existing_root_decision": pin(r[DECISION]), "existing_root_disposition": decision["decision"],
        "typed_historical_wire_consistency": wire, "exact_postimage": {k: pin(v) for k, v in post.items()},
        "exact_preimage_descriptors": pre_pins, "exact_preimage_received": kept, "byte_reduction": byte_reduction,
        "tokenizer": {"name": "cl100k_base", "version": "0.13.0", "encoding_sha256": ENCODING_SHA},
        "preimage_tokens": pre_counts, "postimage_tokens": post_counts, "token_reduction": token_reduction,
        "byte_arm_threshold_met_in_arithmetic": sum(v["bytes"] for v in pre_pins.values()) >= 131072,
        "payoff_at_current_frozen_predicate": module.rotation_payoff_v1(byte_reduction, token_reduction) if kept else None,
        "outer_read_only_elapsed_ns": ret["elapsed_ns"], "inner_read_only_elapsed_ns": read_only["inner_consumer_elapsed_ns"],
        "inner_read_only_cpu_ns": read_only["inner_consumer_cpu_ns"],
        "prelaunch_descriptor_files": initial["file_count"], "prelaunch_descriptor_bytes": initial["total_bytes"],
        "linux_process_peak_rss_kib": decision["cost_scope"]["linux_self_maxrss_kib_at_sample"],
        "native_whole_operation_cost_established": False, "host_metering_admitted": False, "original_full_a5_accepted": False,
        "historical_or_native_operation_replayed": False,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("execution", "receiving", "encoding"):
        parser.add_argument("--" + name, type=Path, required=True)
    for name in ("preimage-state", "preimage-roadmap", "historical-carrier"):
        parser.add_argument("--" + name, type=Path)
    print(json.dumps(measure(parser.parse_args()), indent=2))
