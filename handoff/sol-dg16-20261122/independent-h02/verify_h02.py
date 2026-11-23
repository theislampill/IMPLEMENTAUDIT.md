"""Read-only independent receiving of the retained local H02 compound observation."""

import datetime
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys


CANDIDATE = "f585528d8d266a8bbd125cd00ef86ae59a1d6b2d"
ROOT = "handoff/sol-dg17-20261122"
RESULTS = "6431a1d1e067ab37e4f461caa4a61890d69e7c14"
PRIOR = ("handoff/pro-executor-results-20261115/continuing-execution-20261117/"
         "received-execution-evidence/DG17_H02_P06_ROOT_RECEIVING.json")


def require(condition, label):
    if not condition:
        raise ValueError(label)


def pin(raw):
    return {"bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}


def git(*args, directory=None):
    cmd = ["git", "--no-optional-locks"]
    if directory is not None:
        cmd += ["-C", str(directory)]
    return subprocess.check_output([*cmd, *args])


def observed_age(path):
    return datetime.datetime.fromtimestamp(path.stat().st_mtime, datetime.timezone.utc)


def byte_capture(path, expected, recorded):
    raw = path.read_bytes()
    if recorded is not None:
        require(raw == recorded["raw"].encode() and pin(raw)["sha256"] == recorded["sha256"],
                "captured echo bytes differ from submitted artifact")
    rows = {row["case"]: row for row in json.loads(raw)["rows"]}
    require(len(rows) == 7, "retained raw echo case population")
    for case in ("stock-codepage-437", "explicit-utf8-no-bom", "guarded-correction"):
        row = rows[case]
        require(bytes.fromhex(row["received_hex"]) == bytes.fromhex(row["accounted_hex"]) == expected
                and row["exact_match"] is True and row["received_bytes"] == len(expected),
                "raw echo differs from input")
    require(bytes.fromhex(rows["stock-codepage-65001"]["received_hex"]) == b"\xef\xbb\xbf" + expected
            and bytes.fromhex(rows["stock-codepage-65001-no-write"]["received_hex"]) == b"\xef\xbb\xbf",
            "original uncorrected transport negative")
    return pin(raw)


def main(base):
    published = git("cat-file", "blob", f"{CANDIDATE}:{ROOT}/H02_LATE_CURRENTNESS.json")
    candidate = json.loads(published)
    local_summary = (base / "h02-evidence.json").read_bytes()
    prior_summary = json.loads(local_summary)
    require(set(candidate) - set(prior_summary) == {"closure_boundary"}
            and prior_summary == {k: v for k, v in candidate.items() if k != "closure_boundary"},
            "published/retained summary differs outside declared receiving annotation")
    task = base / "task"
    run, = [p for p in (task / ".IMPLEMENTAUDIT" / "runs").iterdir() if p.is_dir()]
    observations = run / "evidence"
    before, revised = candidate["before"], candidate["late_revision"]
    first, last = before["head"], revised["head"]
    require(git("rev-parse", "HEAD", "HEAD^{tree}", "HEAD^", directory=task).decode().split()
            == [last, revised["tree"], first] and
            git("rev-parse", first + "^{tree}", directory=task).decode().strip() == before["tree"],
            "exact disposable candidate identity")
    require(git("diff-tree", "--no-commit-id", "--name-only", "-r", first, last,
                directory=task).decode().splitlines() == ["transport-frame.json"], "held-out tracked scope")
    windows = git("status", "--porcelain=v1", "--untracked-files=all", directory=task).decode().splitlines()
    mode_only = git("diff", "--summary", directory=task).decode().splitlines()
    require(sorted(windows) == sorted(" M " + name for name in candidate["disposable_subject_member_sha256"])
            and sorted(line.strip() for line in mode_only)
            == sorted("mode change 100755 => 100644 " + name
                      for name in candidate["disposable_subject_member_sha256"]),
            "unexpected Windows presentation beyond recorded mode-only differences")
    ubuntu = subprocess.check_output([
        "wsl.exe", "--distribution", "Ubuntu", "--exec", "bash", "-c",
        'p=$(wslpath -u "$1") && git --no-optional-locks -C "$p" status --porcelain=v1 --untracked-files=all',
        "read-only-source-receiving", str(task.resolve()),
    ])
    require(ubuntu == b"", "Ubuntu retained source is not clean")
    require(git("show", "-s", "--format=%an", last, directory=task).decode().strip() ==
            "Astra independent evaluator", "retained held-out author identity")
    old = git("cat-file", "blob", f"{first}:transport-frame.json", directory=task)
    new = git("cat-file", "blob", f"{last}:transport-frame.json", directory=task)
    delta = [[i, x, y] for i, (x, y) in enumerate(zip(old, new)) if x != y]
    require(len(old) == len(new) == 150 and len(delta) == 1
            and delta == revised["delta"] and (delta[0][1] ^ delta[0][2]).bit_count() == revised["changed_bits"],
            "exact one-byte held-out difference")
    require(pin(old)["sha256"] == revised["before_sha256"]
            and pin(new)["sha256"] == revised["after_sha256"], "exact file revisions")
    for name, sha in candidate["disposable_subject_member_sha256"].items():
        current = git("cat-file", "blob", f"{last}:{name}", directory=task)
        require((task / name).read_bytes() == current and pin(current)["sha256"] == sha,
                "retained exact disposable member")
        if name != "transport-frame.json":
            require(git("cat-file", "blob", f"{first}:{name}", directory=task) == current,
                    "unexpected collateral source drift")
    for name, sha in candidate["executed_product_owners"].items():
        path = "skills/implementaudit/scripts/" + name
        frozen = git("cat-file", "blob", f"{candidate['product_commit']}:{path}")
        require(pin(frozen)["sha256"] == sha and (base / "product" / path).read_bytes() == frozen,
                "installed-for-case owner bytes differ from exact source")

    for name, expected in (("audit-start.json", before["audit_start"]),
                           ("lower-audit-frozen.json", before["lower_audit"])):
        require(json.loads((observations / name).read_bytes()) == expected, "exact lower-audit markers")
    require(pin((observations / "lower-audit-frozen.json").read_bytes())["sha256"] == before["lower_audit_sha256"],
            "exact frozen lower audit")
    lower = before["lower_audit"]
    require(lower["coverage"] == "2/(2+0)" and lower["fresh_mandatory_checks"] == 2
            and lower["prior_phase_records"] == ["done", "done"] and lower["trust_prior"] == 0
            and lower["final_consumption"] == "PENDING_INDEPENDENT_RECEIVING"
            and lower["audit_object_closure_claim"] is False, "clean lower scope and pending final consumption")
    for item in lower["criteria"].values():
        for role in ("audit", "phase"):
            raw = (observations / item[role]).read_bytes()
            require(pin(raw)["sha256"] == item[role + "_sha256"] and json.loads(raw) == item["fresh_result"],
                    "retained phase/audit captures match exact lower audit")
    echoes = {name: byte_capture(observations / name, target, candidate["echoes"].get(name)) for name, target in
              (("echo.json", old), ("echo-audit.json", old), ("echo-reverify.json", new))}
    check = (observations / "reverify-transport.json").read_bytes()
    require(pin(check)["sha256"] == candidate["affected_scope"]["reverified_capture_sha256"]
            and json.loads(check) == candidate["affected_scope"]["reverified_input"]
            and json.loads(check)["echo_sha256"] == echoes["echo-reverify.json"]["sha256"],
            "fresh affected capture and raw echo join")
    policy = candidate["unaffected_scope"]
    require(pin((task / "independent-policy.json").read_bytes())["sha256"] == policy["input_sha256"]
            and pin((observations / "phase-2.json").read_bytes())["sha256"] == policy["phase_sha256"]
            and pin((observations / "audit-policy.json").read_bytes())["sha256"] == policy["audit_sha256"],
            "disjoint retained policy proof")

    revisions = {}
    for generation, row in candidate["receipts"].items():
        ref, oid = row["token"].split("@")
        require(git("rev-parse", ref, directory=task).decode().strip() == oid, "exact actual receipt ref")
        raw = git("cat-file", "blob", oid, directory=task)
        require(pin(raw)["sha256"] == row["sha256"] and raw.decode().splitlines() == [row["record"]]
                and (base / (generation + ".receipt")).read_text().strip() == row["token"],
                "exact retained receipt and token")
        revisions[generation] = row["record"].split("\t")
    g2, g3 = revisions["G0002"], revisions["G0003"]
    require(g2[0:4] == g3[0:4] and g2[4:6] == [first, before["tree"]]
            and g3[4:6] == [last, revised["tree"]] and g2[8] != g3[8]
            and g3[9:11] == ["manual-resume", "G0003"], "normal receipt comparison and fresh anchor")
    require(pin((run / "STATE.md").read_bytes())["sha256"] == g3[6]
            and pin((run / "ROADMAP.md").read_bytes())["sha256"] == g3[7],
            "retained G0003 currentness bookends")
    for name, row in candidate["negative_controls"].items():
        require(int((base / (name + ".exit")).read_text()) == row["exit"] == 1
                and pin((base / (name + ".stderr")).read_bytes())["sha256"] == row["stderr_sha256"]
                and len((base / (name + ".stdout")).read_bytes()) == row["stdout_bytes"],
                "retained refusal capture")
    late_time = datetime.datetime.fromisoformat(git("show", "-s", "--format=%cI", last,
                                                   directory=task).decode().strip())
    order = [observations / "echo.json", observations / "echo-audit.json",
             observations / "lower-audit-frozen.json", base / "old-receipt.exit", base / "old-current.exit",
             base / "G0003.receipt", base / "stale-proof.exit", observations / "echo-reverify.json",
             observations / "reverify-transport.json"]
    times = [observed_age(path) for path in order]
    require(times == sorted(times) and times[2] < late_time < times[3]
            and observed_age(observations / "audit-policy.json") < late_time, "retained chronology")
    markers = re.compile(r"(?m)^\s*(AUDIT_COMPLETE|IMPLEMENTAUDIT_RUN_COMPLETE)\s*$")
    require(all(not markers.search((run / name).read_text(encoding="utf-8"))
                for name in ("STATE.md", "ROADMAP.md")), "unexpected completion markers")
    prior_raw = git("cat-file", "blob", f"{RESULTS}:{PRIOR}")
    previous = json.loads(prior_raw)
    require(previous["resulting_binding"]["source_commit"].startswith("a297957b")
            and "whole_H02" in previous["not_awarded"], "prior original operational scope")

    result = {
        "schema": "dg17.h02.independent-readonly-local-receiving.v1",
        "candidate": CANDIDATE, "published_packet": pin(published), "local_collection_packet": pin(local_summary),
        "sole_public_summary_annotation": "closure_boundary",
        "ubuntu_retained_tree_clean": True, "windows_mode_only_readback_differences": len(windows),
        "product": {"commit": candidate["product_commit"], "tree": candidate["product_tree"]},
        "lower": {"head": first, "tree": before["tree"], "frozen_audit": pin((observations / "lower-audit-frozen.json").read_bytes()),
                  "fresh_mandatory_checks": 2, "scope": lower["scope"], "coverage": lower["coverage"]},
        "late": {"head": last, "tree": revised["tree"], "byte_delta": delta, "changed_paths": ["transport-frame.json"],
                 "unchanged_tracked_members": len(candidate["disposable_subject_member_sha256"]) - 1},
        "retained_refusal_captures": candidate["negative_controls"],
        "normal_receipt_refused_by_captured_result": True,
        "new_receipt_matches_retained_subject_state_readonly": True,
        "retained_echo_descriptors": echoes,
        "reverified_by_recorded_actor": candidate["closure_boundary"]["selection_and_reverify_actor"],
        "reverified_only": "transport-frame.json",
        "unaffected_preserved": "independent-policy.json and its two existing captures",
        "chronology": {**{p.name: t.isoformat() for p, t in zip(order, times)}, "late_candidate_commit": late_time.isoformat()},
        "historical_operational_h02_p06_decision": pin(prior_raw),
        "recommendation": "ACCEPT_ORIGINAL_H02_AT_EXACT_LOCAL_STRUCTURAL_SCOPE",
        "additive_original_scenario_award_at_declared_scope_recommended": True,
        "whole_H02_recommended": False, "terminal_consumer_executed_here": False,
        "model_or_automatic_selection_attributed": False, "original_awards": [],
        "commands_reexecuted": 0, "subject_mutated": False,
    }
    sys.stdout.buffer.write((json.dumps(result, sort_keys=True, indent=2) + "\n").encode())


if __name__ == "__main__":
    main(Path(sys.argv[1]))
