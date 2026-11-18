#!/usr/bin/env python3
"""Read and independently check retained DG17 evidence; never replay a host task."""
import hashlib
import io
import json
from pathlib import Path
import subprocess
import tarfile

ROOT = Path(__file__).resolve().parent
EP = ROOT / "receiving/episode1"
REPO = Path("/workspace/scratch/095d3235c921/implementaudit")
SOURCE = "a297957be11feb494c0ec467235794a1e0c54751"


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def read(path):
    return json.loads(path.read_bytes())


def identity(path):
    raw = path.read_bytes()
    return {"path": str(path.relative_to(ROOT)), "bytes": len(raw), "sha256": digest(raw)}


def bound(path, count, sha):
    raw = path.read_bytes()
    assert (len(raw), digest(raw)) == (count, sha), path
    return raw


def main():
    outer = read(ROOT / "receiving/INPUT_MANIFEST.json")
    for row in outer["members"]:
        bound(EP / Path(row["path"]).name, row["bytes"], row["sha256"])

    host = EP / "final"
    governor = EP / "governor"
    hosted = []
    for path in sorted((host / "commands").glob("*.json")):
        value = read(path)
        bound(path.parent / value["output_file"], value["output_bytes"], value["output_sha256"])
        stderr = value["stderr"]
        bound(path.parent / stderr["file"], stderr["bytes"], stderr["sha256"])
        assert value["exit_code"] == value["expected_exit"], path
        assert value["ended_at_unix"] >= value["started_at_unix"], path
        assert value["output_capture"] == "separate-stdout-stderr", path
        assert value["owned_pgid"] > 0 and value["process_cleanup"] == "owned-process-group-absent", path
        assert value["timed_out"] is False, path
        hosted.append({"command": path.name, "exit_code": value["exit_code"], "sha256": digest(path.read_bytes())})
    assert len(hosted) == 108

    snapshots = []
    for stage, count in (("admitted", 61), ("returned", 84), ("final", 108)):
        directory = host / stage
        packet = read(directory / "PACKET.json")
        assert digest((directory / "STATE.md").read_bytes()) == packet["binding"]["state_sha256"]
        assert digest((directory / "ROADMAP.md").read_bytes()) == packet["binding"]["roadmap_sha256"]
        records = list((directory / "commands").glob("*.json"))
        assert len(records) == count
        for record in records:
            assert record.read_bytes() == (host / "commands" / record.name).read_bytes()
            value = read(record)
            for name in (value["output_file"], value["stderr"]["file"]):
                assert (record.parent / name).read_bytes() == (host / "commands" / name).read_bytes()
        snapshots.append({"stage": stage, "captures": count, "packet": identity(directory / "PACKET.json"), "binding": packet["binding"]})

    local = []
    for path in sorted((governor / "commands").glob("*.json")):
        value = read(path)
        for stream in ("stdout", "stderr", "stdin"):
            if stream in value:
                spec = value[stream]
                bound(path.parent / Path(spec["file"]).name, spec["bytes"], spec["sha256"])
        assert value["coverage"] == "full"
        assert value["finished"] >= value["started"]
        local.append({"command": path.name, "exit_code": value["exit_code"], "sha256": digest(path.read_bytes())})
    assert len(local) == 32

    returns = read(governor / "returns.json")
    assert [e["entry"] for e in returns["entries"]] == ["governed", "direct"]
    assert (governor / "returns.json").read_bytes() == (host / "actual-child-returns.json").read_bytes()
    assert (host / "actual-child-returns.json").read_bytes() == (host / "mail-1.raw").read_bytes()
    assert (host / "mail-1.raw").read_bytes() == (EP / "source/published_returns.json").read_bytes()
    assert (governor / "decision.json").read_bytes() == (host / "actual-Root-decision.json").read_bytes()
    assert (host / "actual-Root-decision.json").read_bytes() == (host / "mail-2.raw").read_bytes()
    assert (host / "mail-2.raw").read_bytes() == (EP / "source/published_decision.json").read_bytes()
    return_records = []
    for entry in returns["entries"]:
        name = entry["entry"]
        output = governor / (name + "-result.txt")
        prompt = governor / (name + "-prompt.txt")
        dispatch = read(governor / (name + "-dispatch.json"))
        received = read(governor / (name + "-return-evidence.json"))
        assert output.read_text() == entry["result_text"]
        assert digest(output.read_bytes()) == entry["result_sha256"] == received["result_sha256"]
        assert len(output.read_bytes()) == received["result_bytes"]
        assert digest(prompt.read_bytes()) == entry["provenance"]["prompt_sha256"] == dispatch["prompt_sha256"]
        assert prompt.read_text() == dispatch["args"]["message"]
        assert entry["caller"] == entry["return_owner"]
        assert received["sender"] == dispatch["actor_id"] == entry["provenance"]["actor_id"]
        assert received["recipient"] == "/root/dg17_governor"
        return_records.append({"entry": name, "actor": received["sender"], "actual_recorded_recipient": received["recipient"],
                               "result": identity(output), "prompt": identity(prompt), "return_evidence": identity(governor / (name + "-return-evidence.json"))})

    final_packet = read(host / "final/PACKET.json")
    admitted = read(host / "admitted/PACKET.json")
    returned = read(host / "returned/PACKET.json")
    decision = read(host / "actual-Root-decision.json")
    assert returns["binding"] == admitted["binding"]
    assert decision["binding"] == returned["binding"]
    assert returned["return_sha256"] == digest((governor / "returns.json").read_bytes())
    assert final_packet["Root_decision_sha256"] == digest((governor / "decision.json").read_bytes())
    assert decision["decision"] == final_packet["decision"] == "repair-separately"
    assert final_packet["original_audit_object"] == "OPEN" and final_packet["subject_repaired"] is False
    assert final_packet["child_has_authority"] is False and final_packet["native_Stop_claim"] is False

    package = final_packet["package_members"]
    assert package == admitted["package_members"] == returned["package_members"]
    assert len(package) == 78
    package_checks = []
    for row in package:
        tree_row = subprocess.run(["git", "ls-tree", SOURCE, "--", row["path"]], cwd=REPO,
                                  capture_output=True, check=True).stdout.decode().split()
        assert tree_row[2] == row["git_blob"]
        raw = subprocess.run(["git", "cat-file", "blob", row["git_blob"]], cwd=REPO,
                             capture_output=True, check=True).stdout
        assert (len(raw), digest(raw)) == (row["bytes"], row["sha256"])
        assert int(tree_row[0], 8) & 0o777 == int(row["mode"], 8)
        package_checks.append({"path": row["path"], "sha256": digest(raw), "git_blob": row["git_blob"]})

    subject = final_packet["subject_members"]
    assert subject == admitted["subject_members"] == returned["subject_members"]
    assert len(subject) == 16
    for row in subject:
        assert row["path"].startswith("subject/")
        bound(EP / "contracts/episode_06" / row["path"], row["bytes"], row["sha256"])

    cleanup = read(host / "CLEANUP.json")
    custody_raw = (host / "actual-task-custody.tar.gz").read_bytes()
    assert digest(custody_raw) == cleanup["archive_sha256"]
    archive_comparisons = []
    with tarfile.open(fileobj=io.BytesIO(custody_raw), mode="r:gz") as archive:
        members = archive.getmembers()
        assert not any(m.issym() or m.islnk() for m in members)
        prefix = "actual-task/.IMPLEMENTAUDIT/runs/" + Path(final_packet["run_root"]).name + "/"
        for name in ("STATE.md", "ROADMAP.md", "PROTOCOL.md", "THINKING.md", "context.md", "sidecars.md", "tools.md"):
            raw = archive.extractfile(prefix + name).read()
            assert raw == (host / "final" / name).read_bytes()
            archive_comparisons.append(name)
        for row in subject:
            raw = archive.extractfile("actual-task/" + row["path"]).read()
            assert (len(raw), digest(raw)) == (row["bytes"], row["sha256"])
            archive_comparisons.append(row["path"])
    assert cleanup["task_removed"] and cleanup["host_custody_terminated"] and cleanup["unresolved_processes"] == []
    assert cleanup["audit_closure"] is False and cleanup["native_Stop_claim"] is False

    repair = read(governor / "LOCAL_REPAIR_VERIFIED.json")
    for row in repair["changed_original_members"]:
        bound(governor / "subject" / row["path"], row["bytes"], row["after_sha256"])
        assert digest((EP / "contracts/episode_06/subject" / row["path"]).read_bytes()) == row["before_sha256"]
    for row in repair["new_members"]:
        bound(governor / "subject" / row["path"], row["bytes"], row["sha256"])
    changed = {"subject/" + x["path"] for x in repair["changed_original_members"]}
    for row in subject:
        if row["path"] not in changed:
            assert (governor / row["path"]).read_bytes() == (EP / "contracts/episode_06" / row["path"]).read_bytes()
    assert (governor / "subject/output/report.txt").read_bytes() == (governor / "subject/expected_report.txt").read_bytes()

    contracts = {}
    for name, expected in (("issue211-body.md", "ca62f4899a45544549f623a0312c16121bb99f432ccb87a87b7361974ceb94c4"),
                           ("issue211-host-amendment.md", "7f39828c5f76683d74531bd49c2ec9a6a2c84bc4d59e52ba8d7a07c251c8c38e")):
        path = EP / "contracts/original-contract" / name
        assert digest(path.read_bytes()) == expected
        contracts[name] = identity(path)

    result = {"schema": "dg17.retained-P07-independent-byte-receiving.v1", "status": "PASS_AT_RETAINED_OPERATIONAL_SCOPE",
              "authority": "NONE", "replay": False, "source_commit": SOURCE,
              "hosted_commands": hosted, "hosted_nonzero": [x for x in hosted if x["exit_code"]],
              "local_governor_commands": local, "local_nonzero": [x for x in local if x["exit_code"]],
              "snapshots": snapshots, "returns": return_records, "package": package_checks,
              "subject_members": len(subject), "custody_comparisons": archive_comparisons,
              "contracts": contracts, "cleanup": cleanup,
              "new_receivable_scope": "Literal P07 registered L4 -> bounded audit-andon return -> appointed governor independent rederivation, followed by separate decision. Root decides acceptance.",
              "H07_limit": "Earlier episode uses the same actual caller actor in two roles; later distinct-caller summary is retained but raw returned results and first-return decision were not found in the inspected published archives.",
              "not_awarded": ["whole_P07", "whole_H07", "complete_model_control_family", "native_Stop", "DG17", "R0037_closure"],
              "files": [identity(governor / "returns.json"), identity(governor / "decision.json"),
                        identity(governor / "GOVERNOR_DECISION.md"), identity(EP / "final.zip"),
                        identity(EP / "source/hosted_governed.py")]}
    target = ROOT / "receiving/RECEIVING_CHECKS.json"
    target.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"result": identity(target), "hosted_commands": len(hosted), "local_commands": len(local),
                      "hosted_nonzero": result["hosted_nonzero"], "local_nonzero": result["local_nonzero"],
                      "package_members": len(package), "subject_members": len(subject), "status": result["status"]}, indent=2))


if __name__ == "__main__":
    main()
