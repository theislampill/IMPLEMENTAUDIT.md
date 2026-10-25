#!/usr/bin/env python3
"""Physical pending-state regression; no native or transaction qualification.

Each case catches an unsafe absence classification, ambiguous JSON acceptance,
or counter validation regression in the actual native-runtime pending owner.
Only synthetic private files are created. No production write API is called.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import types
from unittest import mock

sys.dont_write_bytecode = True
SESSION = "pending-state-loader-physical-regression"
OWNER_DIR = Path("source-peers/native-runtime/skills/implementaudit/scripts")
OWNER_NAMES = ("compaction-audit-pending.py", "host-session-binding.py",
               "compaction-result-observation.py")
COUNTER_MUTATIONS = (
    ("counter_row_list", None, []),
    ("counter_version_zero", "version", 0),
    ("counter_version_negative", "version", -1),
    ("counter_version_boolean", "version", True),
    ("counter_version_float", "version", 1.0),
    ("counter_version_string", "version", "1"),
    ("counter_version_null", "version", None),
    ("counter_version_missing", "version", ...),
    ("counter_consumed_negative", "consumed_version", -1),
    ("counter_consumed_boolean", "consumed_version", True),
    ("counter_consumed_float", "consumed_version", 0.0),
    ("counter_consumed_string", "consumed_version", "0"),
    ("counter_consumed_null", "consumed_version", None),
    ("counter_consumed_missing", "consumed_version", ...),
)
POSITIVE_CASES = {"absent_store", "absent_leaf", "valid_pending", "valid_empty",
                  "valid_consumed", "valid_unconsumed", "finite_proof_number"}
NUMBER_CASES = {"finite_proof_number": b"1.25", "overflow_proof_number": b"1e400",
                "negative_overflow_proof_number": b"-1e400"}


def require(ok, reason):
    if not ok:
        raise AssertionError(reason)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def identity(info):
    return [info.st_dev, info.st_ino, info.st_mode, info.st_nlink,
            info.st_size, info.st_mtime_ns, info.st_ctime_ns]


def source_bindings(root):
    manifest_path = root / "source-peers/native-runtime/SOURCE_MANIFEST.json"
    manifest_raw = manifest_path.read_bytes()
    manifest = json.loads(manifest_raw)
    entries = {row["path"]: row for row in manifest["files"]}
    bindings = {"manifest": {"sha256": sha(manifest_raw), "bytes": len(manifest_raw)}}
    buffers = {}
    for name in OWNER_NAMES:
        relative = OWNER_DIR / name
        path = root / relative
        before = path.lstat()
        require(path.resolve(strict=True) == path and stat.S_ISREG(before.st_mode)
                and before.st_nlink == 1, "owner source is aliased or unsafe")
        raw = path.read_bytes()
        require(identity(before) == identity(path.lstat()), "owner source changed during read")
        declared = entries[relative.as_posix()]
        mode = "100755" if before.st_mode & 0o111 else "100644"
        require(len(raw) == declared["bytes"] and sha(raw) == declared["sha256"]
                and mode == declared["mode"], "owner source does not match its native manifest")
        bindings[name] = {"path": str(path), "bytes": len(raw), "sha256": sha(raw),
                          "mode": mode, "identity": identity(before)}
        buffers[name] = raw
    return bindings, buffers


def snapshot(root):
    result = []
    for directory, names, files in os.walk(root, followlinks=False):
        for name in sorted(names + files):
            path = Path(directory) / name
            info = path.lstat()
            row = {"path": str(path.relative_to(root)), "identity": identity(info)}
            if stat.S_ISLNK(info.st_mode):
                row["target"] = os.readlink(path)
            elif stat.S_ISREG(info.st_mode):
                raw = path.read_bytes()
                require(len(raw) <= 8192, "fixture exceeded the finite byte bound")
                row["sha256"] = sha(raw)
            result.append(row)
    return sorted(result, key=lambda row: row["path"])


def base_state():
    return {"schema": "implementaudit.compaction-audit-pending.v1", "session_id": SESSION,
            "revision": 9, "source": None, "source_problem": None, "signals": 0,
            "unresolved_signal_version": 0, "observations": {}, "assignments": {},
            "active_child": None, "native_producer_runtime_equivalence": "UNVERIFIED"}


def wire(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode()


def prepare_case(owner, fixture, case):
    case_root = fixture / case
    case_root.mkdir(mode=0o700)
    store = case_root / "store"
    path = owner.state_path(store, SESSION)
    require(path.is_relative_to(case_root), "pending fixture escaped its private case")
    state = base_state()
    if case == "absent_store":
        return case_root, store, None
    path.parent.mkdir(mode=0o700, parents=True)
    if case == "absent_leaf":
        return case_root, store, None
    if case == "dangling_leaf":
        path.symlink_to(case_root / "never-created")
        return case_root, store, None
    if case in ("dangling_ancestor", "aliased_absent_leaf", "nondirectory_ancestor"):
        path.parent.rmdir()
        if case == "nondirectory_ancestor":
            path.parent.write_bytes(b"regular ancestor, not a directory\n")
        else:
            target = case_root / "separate-directory"
            if case == "aliased_absent_leaf":
                target.mkdir()
            path.parent.symlink_to(target, target_is_directory=True)
        return case_root, store, None
    if case == "directory_leaf":
        path.mkdir()
        return case_root, store, None
    if case == "fifo_leaf":
        os.mkfifo(path, 0o600)
        return case_root, store, None
    row = {"id": "observation-1", "kind": "compaction", "version": 3,
           "consumed_version": 1, "proof": {"retained_history": ["observed", "partly-consumed"]}}
    if case in ("valid_pending", "valid_consumed", "valid_unconsumed", "duplicate_observation", "duplicate_counter", "invalid_counter") or case in NUMBER_CASES:
        state["observations"] = {"observation-1": row}
    if case in NUMBER_CASES:
        row["proof"]["number"] = 1.25
    if case == "invalid_counter":
        row["consumed_version"] = 4
    elif case == "valid_consumed":
        row["consumed_version"] = 3
    elif case == "valid_unconsumed":
        row.update(version=1, consumed_version=0)
    mutations = {name: (field, value) for name, field, value in COUNTER_MUTATIONS}
    if case in mutations:
        row.update(version=1, consumed_version=0)
        field, value = mutations[case]
        if field is None:
            row = value
        elif value is ...:
            del row[field]
        else:
            row[field] = value
        state["observations"] = {"observation-1": row}
    raw = wire(state)
    if case in NUMBER_CASES:
        raw = raw.replace(b'"number":1.25', b'"number":' + NUMBER_CASES[case])
    if case == "duplicate_top_level":
        raw = raw.replace(b'"observations":{}', b'"observations":' + wire({"observation-1": row}).strip() + b',"observations":{}')
    elif case == "duplicate_observation":
        consumed = dict(row, consumed_version=3)
        raw = raw.replace(wire({"observation-1": row}).strip(),
                          b'{"observation-1":' + wire(row).strip() + b',"observation-1":' + wire(consumed).strip() + b'}')
    elif case == "duplicate_counter":
        raw = raw.replace(b'"consumed_version":1', b'"consumed_version":1,"consumed_version":3')
    elif case == "nonstandard_constant":
        raw = raw.replace(b'"signals":0', b'"signals":NaN')
    elif case == "malformed_json":
        raw = raw[:-2]
    elif case == "nonobject_json":
        raw = b"[]\n"
    require(len(raw) <= 8192, "fixture exceeds finite byte bound")
    path.write_bytes(raw)
    if case == "hardlinked_leaf":
        os.link(path, case_root / "same-file-link")
    return case_root, store, state


def read_race_controls(owner, fixture):
    """Schedule real read-boundary drift; the schedule alone mutates private input."""
    outcomes = []
    for case in ("after-open-same-inode", "after-fstat-same-inode", "after-fstat-path-replacement"):
        base = fixture / case
        base.mkdir()
        _, store, _ = prepare_case(owner, base, "valid_pending")
        path = owner.state_path(store, SESSION)
        raw, initial = path.read_bytes(), path.stat()
        reached = []
        real_open, real_fstat = os.open, os.fstat

        def mutate():
            if case == "after-fstat-path-replacement":
                path.rename(path.with_name("retained-before-replacement.json"))
                path.write_bytes(raw)
            else:
                changed = raw.replace(b'"revision":9', b'"revision":8')
                require(changed != raw and len(changed) == len(raw), "read-race mutation preimage changed")
                path.write_bytes(changed)
                os.utime(path, ns=(initial.st_atime_ns, initial.st_mtime_ns + 10_000_000_000))
            reached.append(case)

        def scheduled_open(name, flags, *args, **kwargs):
            descriptor = real_open(name, flags, *args, **kwargs)
            if case == "after-open-same-inode" and Path(name) == path and not reached:
                mutate()
            return descriptor

        def scheduled_fstat(descriptor):
            info = real_fstat(descriptor)
            if case != "after-open-same-inode" and not reached and (info.st_dev, info.st_ino) == (initial.st_dev, initial.st_ino):
                mutate()  # Return the real observation immediately preceding this scheduled mutation.
            return info

        with mock.patch.object(os, "open", scheduled_open), mock.patch.object(os, "fstat", scheduled_fstat):
            try:
                owner.load(store, SESSION)
            except owner.Refusal as error:
                reason = str(error)
                status = "PASS" if reason == "PENDING_STATE_CHANGED_DURING_READ" else "FAIL_WRONG_READ_REFUSAL"
            else:
                reason, status = None, "FAIL_CUSTODY_DRIFT_ACCEPTED"
        require(reached == [case], "read-race schedule was not reached exactly once")
        outcomes.append({"id": case, "status": status, "refusal": reason,
                         "scheduled_private_input_mutation": True,
                         "proof_scope": "ACTUAL_FILE_READ_BOUNDARY_NOT_NATIVE_OCCURRENCE"})
    return outcomes

def run(root, fixture, cases=None):
    include_read_races = cases is None and os.name == 'posix'
    before, buffers = source_bindings(root)
    module = types.ModuleType("_pending_state_loader_regression")
    module.__file__ = str(root / OWNER_DIR / OWNER_NAMES[0])
    attempts = []
    original_popen = subprocess.Popen

    def deny_launch(*_args, **_kwargs):
        attempts.append("subprocess.Popen")
        raise AssertionError("this control does not admit process launches")

    subprocess.Popen = deny_launch
    outcomes = []
    try:
        exec(compile(buffers[OWNER_NAMES[0]], module.__file__, "exec"), module.__dict__)
        require(Path(module.CORE.__file__) == root / OWNER_DIR / OWNER_NAMES[1]
                and Path(module.OBSERVATION.__file__) == root / OWNER_DIR / OWNER_NAMES[2],
                "pending owner selected an unexpected real sibling")
        if cases is None:
            cases = ("absent_store", "absent_leaf", "valid_pending", "invalid_counter",
                 "duplicate_top_level", "duplicate_observation", "duplicate_counter",
                 "nonstandard_constant", "malformed_json", "nonobject_json",
                 "dangling_leaf", "dangling_ancestor", "aliased_absent_leaf",
                 "nondirectory_ancestor", "directory_leaf", "hardlinked_leaf", "fifo_leaf",
                 "valid_empty", "valid_consumed", "valid_unconsumed",
                 *(name for name, _, _ in COUNTER_MUTATIONS), *NUMBER_CASES)
        physical_cases = {"dangling_leaf", "dangling_ancestor", "aliased_absent_leaf",
                          "nondirectory_ancestor", "directory_leaf", "hardlinked_leaf", "fifo_leaf"}
        for case in cases:
            if os.name != "posix" and case in physical_cases:
                outcomes.append({"id": case, "status": "SKIP_HOST_CAPABILITY",
                                 "reason": "physical representation control is qualified only on actual POSIX"})
                continue
            case_root, store, expected_state = prepare_case(module, fixture, case)
            physical_before = snapshot(case_root)
            row = {"id": case, "expected": "ACCEPT" if case in POSITIVE_CASES else "REFUSE"}
            try:
                loaded = module.load(store, SESSION)
                if row["expected"] == "REFUSE":
                    row.update(status="FAIL_UNSAFE_REPRESENTATION_ACCEPTED",
                               actual_decision=module.decision(loaded)["decision"])
                else:
                    decision = module.decision(loaded)
                    pending = case in ("valid_pending", "valid_unconsumed", "finite_proof_number")
                    require(decision["decision"] == ("AUDIT_STATE_REQUIRED" if pending else "NO_PENDING_AUDIT")
                            and decision["audit_state_required"] is pending, "legitimate state decision changed")
                    if expected_state is not None:
                        require(loaded == expected_state, "valid state or retained history changed")
                    else:
                        require(loaded["observations"] == {} and loaded["revision"] == 0,
                                "legitimate absence no longer returns an empty state")
                    if pending:
                        expected_version = 1 if case == "valid_unconsumed" else 3
                        require(decision["pending"] == [{"id": "observation-1", "kind": "compaction", "version": expected_version}],
                                "unconsumed observation was cleared")
                    row.update(status="PASS", actual_decision=decision["decision"])
            except module.Refusal as exc:
                row.update(status="PASS" if row["expected"] == "REFUSE" else "FAIL_UNEXPECTED_REFUSAL",
                           refusal=str(exc))
            except BaseException as exc:
                row.update(status="FAIL_UNTYPED_EXCEPTION", error=type(exc).__name__, message=str(exc))
            physical_after = snapshot(case_root)
            require(physical_before == physical_after, "data-only load changed fixture contents or identities")
            row["physical_before"] = physical_before
            row["physical_after"] = physical_after
            outcomes.append(row)
        if include_read_races:
            outcomes.extend(read_race_controls(module, fixture))
        after, _ = source_bindings(root)
        require(before == after, "owner code or source manifest changed")
        require(subprocess.Popen is deny_launch and not attempts, "process launch guard changed or was used")
    finally:
        subprocess.Popen = original_popen
    return {"schema": "r0039.pending-state-loader.regression.v1",
            "status": "PASS" if all(row["status"] in ("PASS", "SKIP_HOST_CAPABILITY") for row in outcomes) else "FAIL",
            "source_before": before, "source_after": after, "controls": outcomes, "actual_host": os.name,
            "child_launch_attempts": len(attempts), "native_operations": 0,
            "authority": "NONE", "proof_scope": "PHYSICAL_DATA_SOURCE_ONLY"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--retain-fixtures", type=Path)
    parser.add_argument("--evidence", type=Path)
    args = parser.parse_args()
    root = args.source_root.resolve(strict=True)
    if args.retain_fixtures:
        require(not os.path.lexists(args.retain_fixtures), "fixture already exists; no overwrite or retry")
        args.retain_fixtures.mkdir(mode=0o700, parents=True)
        result = run(root, args.retain_fixtures.resolve(strict=True))
    else:
        with tempfile.TemporaryDirectory(prefix="pending-state-loader-") as temporary:
            result = run(root, Path(temporary).resolve(strict=True))
    result["driver_sha256"] = sha(Path(__file__).read_bytes())
    if args.evidence:
        with args.evidence.open("x", encoding="utf-8") as output:
            json.dump(result, output, indent=2, sort_keys=True, allow_nan=False)
            output.write("\n")
    print(json.dumps({"status": result["status"], "cases": len(result["controls"]),
                      "skipped": [row["id"] for row in result["controls"] if row["status"] == "SKIP_HOST_CAPABILITY"],
                      "failures": [{"id": row["id"], "status": row["status"]} for row in result["controls"] if row["status"] not in ("PASS", "SKIP_HOST_CAPABILITY")],
                      "child_launch_attempts": result["child_launch_attempts"]}, sort_keys=True))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
