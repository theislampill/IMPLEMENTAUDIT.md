#!/usr/bin/env bash
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
bash_exe="$(command -v bash)"
if command -v cygpath >/dev/null 2>&1; then bash_exe="$(cygpath -w "$bash_exe")"; fi
if command -v python3 >/dev/null 2>&1; then python_cmd=(python3)
elif command -v python >/dev/null 2>&1; then python_cmd=(python)
elif command -v py >/dev/null 2>&1; then python_cmd=(py -3)
else printf 'apply-observed-mutation: Python is required\n' >&2; exit 77
fi
MSYS2_ARG_CONV_EXCL='*' exec "${python_cmd[@]}" - "$script_dir" "$bash_exe" "$@" <<'PY'
import argparse
import ctypes
import hashlib
import json
import os
import re
import secrets
import stat
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

SCRIPT_DIR_RAW = sys.argv[1]
BASH_EXE_RAW = sys.argv[2]
ARGV = sys.argv[3:]
os.environ.pop("MSYS2_ARG_CONV_EXCL", None)
EXITS = {
    "COMMITTED": 0,
    "NO_CHANGE": 0,
    "REJECTED_NO_MUTATION": 64,
    "CONFLICT_REBASE": 65,
    "MUTATION_FAILED_NO_STATE_CHANGE": 70,
    "MUTATION_FAILED_ROLLED_BACK": 71,
    "POST_STATE_MISMATCH_ROLLED_BACK": 72,
    "RECOVERY_REQUIRED": 73,
    "ROLLBACK_CONFLICT": 74,
    "ROLLBACK_FAILED_WITH_RESIDUE": 75,
    "POST_COMMIT_DRIFT": 76,
    "UNSUPPORTED_OWNER_DECISION": 77,
}


def canonical(value):
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def digest(data):
    return hashlib.sha256(data).hexdigest()


def simple_identity(data):
    return {"sha256": digest(data), "byte_length": len(data)}


def utc_now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def is_reparse(st):
    return bool(getattr(st, "st_file_attributes", 0) & 0x400)


def path_identity(path):
    path = Path(path)
    try:
        st = os.lstat(path)
    except FileNotFoundError:
        return {"kind": "absent"}
    base = {
        "device": int(st.st_dev),
        "inode": int(st.st_ino),
        "link_count": int(st.st_nlink),
    }
    if stat.S_ISLNK(st.st_mode) or is_reparse(st):
        return {"kind": "symlink", **base}
    if stat.S_ISREG(st.st_mode):
        data = path.read_bytes()
        return {
            "kind": "regular",
            "sha256": digest(data),
            "byte_length": len(data),
            **base,
        }
    if stat.S_ISDIR(st.st_mode):
        return {"kind": "directory", **base}
    return {"kind": "other", **base}


def regular_bytes(path):
    identity = path_identity(path)
    if identity.get("kind") != "regular":
        return None
    return Path(path).read_bytes()


def contained_regular(path, root=None):
    path = Path(path)
    try:
        st = os.lstat(path)
    except OSError:
        return False
    if not stat.S_ISREG(st.st_mode) or is_reparse(st):
        return False
    cursor = path
    while True:
        try:
            st = os.lstat(cursor)
        except OSError:
            return False
        if stat.S_ISLNK(st.st_mode) or is_reparse(st):
            return False
        if root is not None and cursor == root:
            return True
        if cursor.parent == cursor:
            return root is None
        cursor = cursor.parent


def repo_relative(path):
    return Path(os.path.abspath(path)).relative_to(REPO).as_posix()


def repo_path(raw):
    if (
        not isinstance(raw, str)
        or not raw
        or raw.startswith("/")
        or "\\" in raw
        or any(part in ("", ".", "..") for part in raw.split("/"))
    ):
        return None
    path = REPO.joinpath(*raw.split("/"))
    try:
        path.relative_to(REPO)
    except ValueError:
        return None
    cursor = REPO
    for part in raw.split("/")[:-1]:
        cursor = cursor / part
        try:
            st = os.lstat(cursor)
        except OSError:
            return None
        if not stat.S_ISDIR(st.st_mode) or stat.S_ISLNK(st.st_mode) or is_reparse(st):
            return None
    try:
        st = os.lstat(path)
        if stat.S_ISLNK(st.st_mode) or is_reparse(st):
            return None
    except FileNotFoundError:
        pass
    return path


def rejected_repo_identity(raw):
    """Describe a rejected lexical path without following an unsafe ancestor."""
    if (
        not isinstance(raw, str)
        or not raw
        or raw.startswith("/")
        or "\\" in raw
        or any(part in ("", ".", "..") for part in raw.split("/"))
    ):
        return {"kind": "absent"}
    cursor = REPO
    for part in raw.split("/"):
        cursor = cursor / part
        try:
            st = os.lstat(cursor)
        except OSError:
            return {"kind": "absent"}
        base = {
            "device": int(st.st_dev),
            "inode": int(st.st_ino),
            "link_count": int(st.st_nlink),
        }
        if stat.S_ISLNK(st.st_mode) or is_reparse(st):
            return {"kind": "symlink", **base}
        if cursor != REPO.joinpath(*raw.split("/")) and not stat.S_ISDIR(st.st_mode):
            return {"kind": "other", **base}
    return path_identity(cursor)


def safe_directory_chain(path, base, final_may_be_absent=False):
    try:
        relative = path.relative_to(base)
    except ValueError:
        return False
    cursor = base
    try:
        base_stat = os.lstat(cursor)
    except OSError:
        return False
    if (
        not stat.S_ISDIR(base_stat.st_mode)
        or stat.S_ISLNK(base_stat.st_mode)
        or is_reparse(base_stat)
    ):
        return False
    for index, part in enumerate(relative.parts):
        cursor = cursor / part
        try:
            current = os.lstat(cursor)
        except FileNotFoundError:
            return final_may_be_absent and index == len(relative.parts) - 1
        except OSError:
            return False
        if (
            not stat.S_ISDIR(current.st_mode)
            or stat.S_ISLNK(current.st_mode)
            or is_reparse(current)
        ):
            return False
    return True


def phase_hook(phase):
    # R36_INSTRUMENT_INSERT
    return


bar = None
fault = None


def wait(name, release="release"):
    if not bar:
        return
    base = Path(bar)
    base.mkdir(parents=True, exist_ok=True)
    (base / name).touch()
    for _ in range(500):
        if (base / release).exists():
            return
        time.sleep(0.02)
    raise RuntimeError("timeout")


parser = argparse.ArgumentParser(add_help=False)
parser.add_argument("--repo-root", required=True)
parser.add_argument("--run-root", required=True)
parser.add_argument("--phase", required=True, type=int)
parser.add_argument("--step", required=True, type=int)
parser.add_argument("--preimage")
parser.add_argument("--candidate")
parser.add_argument("--offset")
parser.add_argument("--region")
parser.add_argument("--replacement")
try:
    args, unknown = parser.parse_known_args(ARGV)
except SystemExit:
    raise SystemExit(64)
if unknown or args.phase <= 0 or args.step <= 0:
    if unknown:
        sys.stderr.write(f"apply-observed-mutation: unknown arguments: {unknown!r}\n")
    raise SystemExit(64)

RAW_REPO = args.repo_root
RAW_RUN = args.run_root


def native_input(raw):
    if os.name != "nt":
        return raw
    match = re.match(r"^/mnt/([A-Za-z])/(.*)$", raw)
    if match:
        return f"{match.group(1)}:/{match.group(2)}"
    match = re.match(r"^/([A-Za-z])/(.*)$", raw)
    if match:
        return f"{match.group(1)}:/{match.group(2)}"
    if raw == "/tmp" or raw.startswith("/tmp/"):
        suffix = raw[5:] if raw.startswith("/tmp/") else ""
        return os.path.join(os.environ.get("TEMP", os.environ.get("TMP", "")), suffix)
    return raw


def bash_path(raw):
    return os.fspath(raw).replace("\\", "/") if os.name == "nt" else os.fspath(raw)


SCRIPT_DIR = Path(native_input(SCRIPT_DIR_RAW))
BASH_EXE = native_input(BASH_EXE_RAW)
REPO = Path(os.path.abspath(native_input(RAW_REPO)))
RUN = Path(native_input(RAW_RUN))
RUN = Path(os.path.abspath(REPO / RUN)) if not RUN.is_absolute() else Path(os.path.abspath(RUN))
PHASE_FILE = RUN / "phases" / f"phase-{args.phase}.md"


def validator(command):
    completed = subprocess.run(command, text=True, capture_output=True, check=False)
    if completed.returncode != 0:
        sys.stderr.write(f"apply-observed-mutation: validator failed ({completed.returncode}): {command[1]}\n")
        if completed.stdout:
            sys.stderr.write(completed.stdout)
        if completed.stderr:
            sys.stderr.write(completed.stderr)
        raise SystemExit(64)
    return completed.stdout.strip()


validator(
    [
        BASH_EXE,
        bash_path(SCRIPT_DIR / "validate-run-root.sh"),
        "--claim-only",
        bash_path(native_input(RAW_RUN)),
        "--repo-root",
        bash_path(native_input(RAW_REPO)),
    ]
)
authority_text = validator(
    [
        BASH_EXE,
        bash_path(SCRIPT_DIR / "validate-phase.sh"),
        "--mutation-authority",
        bash_path(PHASE_FILE),
        "--phase",
        str(args.phase),
        "--step",
        str(args.step),
        "--repo-root",
        bash_path(REPO),
        "--run-root",
        bash_path(RUN),
    ]
)
try:
    authority_projection = json.loads(authority_text)
except json.JSONDecodeError:
    sys.stderr.write("apply-observed-mutation: phase authority emitted invalid JSON\n")
    raise SystemExit(64)

claim_bytes = (RUN / ".claimed").read_bytes()
claim_rows = claim_bytes.decode("utf-8").splitlines()
claim = dict(row.split("=", 1) for row in claim_rows)
claim_id = claim["claim_id"]
operation = authority_projection["operation"]
source_name = authority_projection["source"]
destination_name = authority_projection["destination"]
SOURCE = repo_path(source_name)
DESTINATION = repo_path(destination_name) if destination_name is not None else None


def identity_rows(paths):
    return [
        {"path": name, "identity": path_identity(path)}
        for name, path in paths
    ]


source_initial = path_identity(SOURCE) if SOURCE is not None else {"kind": "absent"}
pre_rows = identity_rows([(source_name, SOURCE)]) if SOURCE is not None else []
candidate_rows = []
candidate_data = None
preimage_data = None
reason = "NONE"


def evidence_bytes(raw):
    if not raw:
        return None
    path = Path(native_input(raw))
    if not contained_regular(path):
        return None
    return path.read_bytes()


if SOURCE is None or source_initial.get("kind") != "regular":
    reason = "PATH_REDIRECTION_UNSUPPORTED"
elif operation == "move" and (
    DESTINATION is None or destination_name == source_name or not DESTINATION.parent.is_dir()
):
    reason = "SCOPE_NOT_AUTHORIZED"

if operation in {"replace", "delete", "move"}:
    preimage_data = evidence_bytes(args.preimage)
    if preimage_data is None:
        reason = reason if reason != "NONE" else "PREIMAGE_REQUIRED"
elif operation == "patch":
    current = regular_bytes(SOURCE) if SOURCE is not None else None
    region = evidence_bytes(args.region)
    replacement = evidence_bytes(args.replacement)
    try:
        offset = int(args.offset)
    except (TypeError, ValueError):
        offset = -1
    if (
        current is None
        or region is None
        or replacement is None
        or offset < 0
        or not region
        or current[offset : offset + len(region)] != region
    ):
        reason = reason if reason != "NONE" else "PATCH_REGION_MISMATCH"
    else:
        candidate_data = current[:offset] + replacement + current[offset + len(region) :]

if operation == "replace":
    candidate_data = evidence_bytes(args.candidate)
    if candidate_data is None:
        reason = reason if reason != "NONE" else "PREIMAGE_REQUIRED"
if operation == "move" and preimage_data is not None:
    candidate_data = preimage_data
if candidate_data is not None:
    candidate_rows = [
        {
            "path": source_name,
            "identity": {
                "kind": "regular",
                **simple_identity(candidate_data),
                "device": 0,
                "inode": 0,
                "link_count": 0,
            },
        }
    ]


def current_post_rows():
    rows = []
    paths = []
    if SOURCE is not None:
        paths.append((source_name, SOURCE))
    elif source_name is not None:
        rows.append({"path": source_name, "identity": rejected_repo_identity(source_name)})
    if DESTINATION is not None:
        paths.append((destination_name, DESTINATION))
    return rows + identity_rows(paths)


empty_effect_digest = digest(canonical([]))


def emit_no_effect(status, why, transaction=None):
    result = {
        "schema": "implementaudit.observation_bound_mutation.v2",
        "transaction_id": transaction,
        "claim_id": claim_id,
        "phase": args.phase,
        "step": args.step,
        "authority_binding_sha256": authority_projection["authority_binding_sha256"],
        "operation": operation,
        "status": status,
        "reason_code": why,
        "source_path": source_name,
        "destination_path": destination_name,
        "pre_identities": pre_rows,
        "candidate_identities": candidate_rows,
        "post_identities": current_post_rows(),
        "planned_effect_set": [],
        "planned_effect_set_sha256": empty_effect_digest,
        "actual_effect_set": [],
        "residue": [],
    }
    print(json.dumps(result, separators=(",", ":"), ensure_ascii=False))
    raise SystemExit(EXITS[status])


if reason != "NONE":
    emit_no_effect("REJECTED_NO_MUTATION", reason)
current_data = regular_bytes(SOURCE)
if operation in {"replace", "delete", "move"} and current_data != preimage_data:
    status = (
        "REJECTED_NO_MUTATION"
        if current_data is not None
        and preimage_data is not None
        and current_data.startswith(preimage_data)
        else "CONFLICT_REBASE"
    )
    emit_no_effect(status, "PREIMAGE_DRIFT")
if operation == "replace" and candidate_data == current_data:
    emit_no_effect("NO_CHANGE", "NONE")
if operation == "move" and path_identity(DESTINATION).get("kind") != "absent":
    emit_no_effect("REJECTED_NO_MUTATION", "DESTINATION_EXISTS")


def source_observation_unchanged():
    return path_identity(SOURCE) == source_initial

transaction_id = f"{claim_id}-p{args.phase}-s{args.step}"
TX_PARENT = RUN / "mutation-transactions"
TX = TX_PARENT / transaction_id
AUTHORITY = TX / "authority.json"
JOURNAL = TX / "journal.json"
JOURNAL_TMP = TX / "journal.tmp"
RESULT = TX / "result.json"
DISPOSITION = TX / "disposition.json"
BACKUP = TX / "backup.bin"
STAGE = TX / "stage.bin"
LOCK_ROOT = REPO / ".IMPLEMENTAUDIT" / ".r36-locks"
LOCK_PARENT = LOCK_ROOT.parent

if not safe_directory_chain(TX_PARENT, RUN, True):
    emit_no_effect("REJECTED_NO_MUTATION", "INTERNAL_CUSTODY_UNSAFE", transaction_id)
if not safe_directory_chain(LOCK_PARENT, REPO):
    emit_no_effect("REJECTED_NO_MUTATION", "INTERNAL_CUSTODY_UNSAFE", transaction_id)
if not safe_directory_chain(LOCK_ROOT, LOCK_PARENT, True):
    emit_no_effect("REJECTED_NO_MUTATION", "INTERNAL_CUSTODY_UNSAFE", transaction_id)

try:
    object_stat = os.lstat(SOURCE)
except OSError:
    emit_no_effect("REJECTED_NO_MUTATION", "PATH_NOT_REGULAR")
lock_keys = [source_name, f"object:{object_stat.st_dev}:{object_stat.st_ino}"]
if destination_name is not None:
    lock_keys.append(destination_name)
lock_paths = [LOCK_ROOT / (digest(key.encode("utf-8")) + ".lock") for key in sorted(lock_keys)]

planned_map = {}


def plan(path, roles, effects, retention):
    key = ("repo", repo_relative(path))
    row = planned_map.setdefault(
        key,
        {"roles": set(), "allowed_effects": set(), "retention": retention},
    )
    row["roles"].update(roles)
    row["allowed_effects"].update(effects)
    priorities = {"input": 0, "transient": 1, "durable": 2, "conditional-residue": 3}
    if priorities[retention] > priorities[row["retention"]]:
        row["retention"] = retention


plan(SOURCE, ["source"], ["link", "replace", "unlink", "fsync"], "input")
plan(SOURCE.parent, ["source-parent"], ["fsync"], "durable")
if DESTINATION is not None:
    plan(DESTINATION, ["destination", "residue"], ["link", "unlink", "fsync"], "conditional-residue")
    plan(DESTINATION.parent, ["destination-parent"], ["fsync"], "durable")
plan(RUN, ["transaction-parent"], ["fsync"], "durable")
plan(TX_PARENT, ["transaction-dir"], ["mkdir", "rmdir", "fsync"], "durable")
plan(TX, ["transaction-dir"], ["mkdir", "rmdir", "fsync"], "durable")
plan(AUTHORITY, ["authority"], ["create", "write", "unlink", "fsync"], "durable")
plan(JOURNAL, ["journal", "residue"], ["create", "write", "replace", "unlink", "fsync"], "conditional-residue")
plan(JOURNAL_TMP, ["journal-temp"], ["create", "write", "replace", "unlink", "fsync"], "transient")
plan(RESULT, ["result"], ["create", "write", "fsync"], "durable")
plan(DISPOSITION, ["disposition"], [], "durable")
plan(BACKUP, ["backup", "residue"], ["link", "replace", "unlink", "fsync"], "conditional-residue")
plan(STAGE, ["stage", "residue"], ["create", "write", "link", "unlink", "fsync"], "conditional-residue")
plan(LOCK_ROOT, ["lock-root"], ["mkdir", "fsync"], "durable")
plan(LOCK_PARENT, ["lock-parent"], ["fsync"], "durable")
for lock in lock_paths:
    plan(lock, ["path-lock", "residue"], ["mkdir", "rmdir", "fsync"], "conditional-residue")
    plan(lock / "owner", ["lock-owner", "residue"], ["create", "write", "unlink", "fsync"], "conditional-residue")

planned = [
    {
        "scope": scope,
        "path": path,
        "roles": sorted(row["roles"]),
        "allowed_effects": sorted(row["allowed_effects"]),
        "retention": row["retention"],
    }
    for (scope, path), row in sorted(planned_map.items())
]
planned_digest = digest(canonical(planned))
allowed = {
    (row["scope"], row["path"]): set(row["allowed_effects"]) for row in planned
}
actual = []


def authorise(path, effect):
    key = ("repo", repo_relative(path))
    if effect not in allowed.get(key, set()):
        raise RuntimeError(f"EFFECT_SET_INCOMPLETE:{key[1]}:{effect}")


def record(path, effect, before=None, after=None, outcome="applied"):
    key = ("repo", repo_relative(path))
    authorise(path, effect)
    actual.append(
        {
            "sequence": len(actual) + 1,
            "scope": "repo",
            "path": key[1],
            "effect": effect,
            "before": before,
            "after": after,
            "outcome": outcome,
        }
    )


def future_effect_rows(entries):
    rows = []
    for path, effect, before, after in entries:
        authorise(path, effect)
        rows.append(
            {
                "sequence": len(actual) + len(rows) + 1,
                "scope": "repo",
                "path": repo_relative(path),
                "effect": effect,
                "before": before,
                "after": after,
                "outcome": "applied",
            }
        )
    return rows


def mkdir(path, after_mutation=None):
    before = path_identity(path)
    authorise(path, "mkdir")
    try:
        os.mkdir(path)
    except FileExistsError:
        record(path, "mkdir", before, path_identity(path), "not-applied")
        raise
    if after_mutation is not None:
        after_mutation()
    record(path, "mkdir", before, path_identity(path))
    fsync_dir(path.parent)


def write_new(path, data, after_mutation=None):
    before = path_identity(path)
    authorise(path, "create")
    authorise(path, "write")
    authorise(path, "fsync")
    with path.open("xb") as handle:
        handle.write(data)
        handle.flush()
        os.fsync(handle.fileno())
    if after_mutation is not None:
        after_mutation()
    record(path, "create", before, path_identity(path))
    record(path, "write", before, path_identity(path))
    record(path, "fsync", path_identity(path), path_identity(path))
    fsync_dir(path.parent)


def unlink(path):
    before = path_identity(path)
    authorise(path, "unlink")
    os.unlink(path)
    record(path, "unlink", before, path_identity(path))
    fsync_dir(path.parent)


def link(source, destination, after_mutation=None):
    before = path_identity(destination)
    authorise(destination, "link")
    os.link(source, destination)
    if after_mutation is not None:
        after_mutation()
    record(destination, "link", before, path_identity(destination))
    fsync_dir(destination.parent)


def replace(source, destination, after_mutation=None):
    source_before = path_identity(source)
    destination_before = path_identity(destination)
    authorise(source, "replace")
    authorise(destination, "replace")
    os.replace(source, destination)
    if after_mutation is not None:
        after_mutation()
    record(source, "replace", source_before, path_identity(source))
    record(destination, "replace", destination_before, path_identity(destination))
    fsync_dir(source.parent)
    if destination.parent != source.parent:
        fsync_dir(destination.parent)


def rmdir(path):
    before = path_identity(path)
    authorise(path, "rmdir")
    os.rmdir(path)
    record(path, "rmdir", before, path_identity(path))
    fsync_dir(path.parent)


def fsync_dir(path):
    authorise(path, "fsync")
    sync_directory_raw(path)
    record(path, "fsync", path_identity(path), path_identity(path))


def sync_directory_raw(path):
    if os.name == "nt":
        kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        create = kernel.CreateFileW
        create.argtypes = [ctypes.c_wchar_p, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_void_p, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_void_p]
        create.restype = ctypes.c_void_p
        handle = create(str(path), 0x40000000, 0x1 | 0x2 | 0x4, None, 3, 0x02000000, None)
        if handle == ctypes.c_void_p(-1).value:
            raise OSError(ctypes.get_last_error(), "CreateFileW directory durability failed", str(path))
        try:
            if not kernel.FlushFileBuffers(ctypes.c_void_p(handle)):
                raise OSError(ctypes.get_last_error(), "FlushFileBuffers directory durability failed", str(path))
        finally:
            kernel.CloseHandle(ctypes.c_void_p(handle))
        return
    try:
        descriptor = os.open(path, os.O_RDONLY)
    except OSError:
        raise
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def observations():
    if operation == "patch":
        return {
            "current": simple_identity(current_data),
            "region": simple_identity(evidence_bytes(args.region)),
            "replacement": simple_identity(evidence_bytes(args.replacement)),
            "offset": int(args.offset),
            "candidate": simple_identity(candidate_data),
        }
    result = {"preimage": simple_identity(preimage_data)}
    if candidate_data is not None:
        result["candidate"] = simple_identity(candidate_data)
    return result


authority_record = {
    "schema": "implementaudit.observation-bound-mutation.authority.v2",
    "transaction_id": transaction_id,
    "created_at_utc": utc_now(),
    "claim": {
        "claim_id": claim_id,
        "claim_sha256": digest(claim_bytes),
        "repo_root": claim["repo_root"],
        "git_common_dir": claim["git_common_dir"],
        "run_root": claim["run_root"],
    },
    "phase": {
        "phase": args.phase,
        "step": args.step,
        "authority_binding_sha256": authority_projection["authority_binding_sha256"],
    },
    "operation": operation,
    "source": source_name,
    "destination": destination_name,
    "observations": observations(),
    "planned_effect_set": planned,
    "planned_effect_set_sha256": planned_digest,
}


def emit_transaction_conflict(reason_code):
    result = {
        "schema": "implementaudit.observation_bound_mutation.v2",
        "transaction_id": transaction_id,
        "claim_id": claim_id,
        "phase": args.phase,
        "step": args.step,
        "authority_binding_sha256": authority_projection["authority_binding_sha256"],
        "operation": operation,
        "status": "CONFLICT_REBASE",
        "reason_code": reason_code,
        "source_path": source_name,
        "destination_path": destination_name,
        "pre_identities": pre_rows,
        "candidate_identities": candidate_rows,
        "post_identities": current_post_rows(),
        "planned_effect_set": planned,
        "planned_effect_set_sha256": planned_digest,
        "actual_effect_set": actual,
        "residue": [],
    }
    print(json.dumps(result, separators=(",", ":"), ensure_ascii=False))
    raise SystemExit(EXITS["CONFLICT_REBASE"])


phase_hook("pre-transaction")
if path_identity(TX).get("kind") != "absent":
    emit_transaction_conflict("PHASE_AUTHORITY_IN_PROGRESS_OR_REPLAY")
init_created_parent = False
init_created_tx = False
init_created_authority = False


def mark_init_parent():
    global init_created_parent
    init_created_parent = True


def mark_init_tx():
    global init_created_tx
    init_created_tx = True


def mark_init_authority():
    global init_created_authority
    init_created_authority = True


def emit_initialisation_failure():
    residue_paths = []
    try:
        if init_created_authority and path_identity(AUTHORITY).get("kind") == "regular":
            unlink(AUTHORITY)
        if init_created_tx and path_identity(TX).get("kind") == "directory":
            rmdir(TX)
        if init_created_parent and path_identity(TX_PARENT).get("kind") == "directory":
            rmdir(TX_PARENT)
    except (OSError, RuntimeError):
        owned_paths = (
            (AUTHORITY, init_created_authority),
            (TX, init_created_tx),
            (TX_PARENT, init_created_parent),
        )
        residue_paths = [path for path, owned in owned_paths if owned and path_identity(path).get("kind") != "absent"]
    status = "MUTATION_FAILED_NO_STATE_CHANGE" if not residue_paths else "ROLLBACK_FAILED_WITH_RESIDUE"
    result = {
        "schema": "implementaudit.observation_bound_mutation.v2",
        "transaction_id": transaction_id,
        "claim_id": claim_id,
        "phase": args.phase,
        "step": args.step,
        "authority_binding_sha256": authority_projection["authority_binding_sha256"],
        "operation": operation,
        "status": status,
        "reason_code": "INITIALISATION_IO_FAILURE",
        "source_path": source_name,
        "destination_path": destination_name,
        "pre_identities": pre_rows,
        "candidate_identities": candidate_rows,
        "post_identities": current_post_rows(),
        "planned_effect_set": planned,
        "planned_effect_set_sha256": planned_digest,
        "actual_effect_set": actual,
        "residue": [{"scope":"repo","path":repo_relative(path),"identity":path_identity(path),"custody":"run-owner-required"} for path in residue_paths],
    }
    print(json.dumps(result, separators=(",", ":"), ensure_ascii=False))
    raise SystemExit(EXITS[status])


try:
    if path_identity(TX_PARENT).get("kind") == "absent":
        try:
            mkdir(TX_PARENT, mark_init_parent)
        except FileExistsError:
            if not safe_directory_chain(TX_PARENT, RUN):
                emit_transaction_conflict("INTERNAL_CUSTODY_UNSAFE")
    mkdir(TX, mark_init_tx)
except FileExistsError:
    emit_transaction_conflict("PHASE_AUTHORITY_IN_PROGRESS_OR_REPLAY")
except OSError:
    emit_initialisation_failure()
try:
    write_new(AUTHORITY, canonical(authority_record), mark_init_authority)
    fsync_dir(TX)
except OSError:
    emit_initialisation_failure()

owner = secrets.token_hex(16)
held = []
residue = []


def residue_row(path):
    return {
        "scope": "repo",
        "path": repo_relative(path),
        "identity": path_identity(path),
        "custody": "run-owner-required",
    }


def journal_record(status, residue_paths=(), effect_rows=None):
    return {
        "schema": "implementaudit.observation-bound-mutation.journal.v2",
        "transaction_id": transaction_id,
        "authority_sha256": digest(AUTHORITY.read_bytes()),
        "status": status,
        "pre_identities": pre_rows,
        "candidate_identities": candidate_rows,
        "current_identities": current_post_rows(),
        "planned_effect_set_sha256": planned_digest,
        "actual_effect_set": list(actual if effect_rows is None else effect_rows),
        "residue": [residue_row(path) for path in residue_paths if path.exists()],
        "updated_at_utc": utc_now(),
    }


def persist_journal(status, residue_paths=()):
    if path_identity(JOURNAL_TMP).get("kind") != "absent":
        unlink(JOURNAL_TMP)
    temporary_before = path_identity(JOURNAL_TMP)
    journal_before = path_identity(JOURNAL)
    directory_identity = path_identity(TX)
    future = future_effect_rows(
        [
            (JOURNAL_TMP, "create", temporary_before, None),
            (JOURNAL_TMP, "write", temporary_before, None),
            (JOURNAL_TMP, "fsync", None, None),
            (JOURNAL_TMP, "replace", None, {"kind": "absent"}),
            (JOURNAL, "replace", journal_before, None),
            (TX, "fsync", directory_identity, directory_identity),
        ]
    )
    data = canonical(journal_record(status, residue_paths, actual + future))
    with JOURNAL_TMP.open("xb") as handle:
        handle.write(data)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(JOURNAL_TMP, JOURNAL)
    sync_directory_raw(TX)
    actual.extend(future)


retain_owned_locks = False


def release_locks():
    while held:
        lock = held[-1]
        owner_path = lock / "owner"
        try:
            if owner_path.read_text(encoding="ascii") != owner:
                break
            unlink(owner_path)
            rmdir(lock)
            held.pop()
        except OSError:
            break


def final_result(status, reason_code="NONE", residue_paths=(), post_path=None):
    global retain_owned_locks
    uncertain_paths = list(residue_paths)
    if uncertain_paths:
        retain_owned_locks = True
        for lock in held:
            uncertain_paths.extend([lock, lock / "owner"])
    result_residue = [residue_row(path) for path in uncertain_paths if path_identity(path).get("kind") != "absent"]
    if not result_residue:
        if path_identity(JOURNAL).get("kind") != "absent":
            unlink(JOURNAL)
        release_locks()
    result_before = path_identity(RESULT)
    transaction_identity = path_identity(TX)
    future = future_effect_rows(
        [
            (RESULT, "create", result_before, None),
            (RESULT, "write", result_before, None),
            (RESULT, "fsync", None, None),
            (TX, "fsync", transaction_identity, transaction_identity),
        ]
    )
    def build_result(effect_rows):
        return {
        "schema": "implementaudit.observation_bound_mutation.v2",
        "transaction_id": transaction_id,
        "claim_id": claim_id,
        "phase": args.phase,
        "step": args.step,
        "authority_binding_sha256": authority_projection["authority_binding_sha256"],
        "operation": operation,
        "status": status,
        "reason_code": reason_code,
        "source_path": source_name,
        "destination_path": destination_name,
        "pre_identities": pre_rows,
        "candidate_identities": candidate_rows,
        "post_identities": current_post_rows(),
        "planned_effect_set": planned,
        "planned_effect_set_sha256": planned_digest,
        "actual_effect_set": list(effect_rows),
        "residue": result_residue,
        }
    with RESULT.open("xb") as handle:
        handle.write(canonical(build_result(actual + future)))
        handle.flush()
        os.fsync(handle.fileno())
    sync_directory_raw(TX)
    actual.extend(future)
    result = build_result(actual)
    print(json.dumps(result, separators=(",", ":"), ensure_ascii=False))
    raise SystemExit(EXITS[status])


phase_hook("init")
if fault == "pre-displacement":
    wait("paused")
    final_result("MUTATION_FAILED_NO_STATE_CHANGE", "NONE")
if fault == "unsupported-external-writer":
    wait("paused")
    wait("observed-after-external", "continue-after-external")
    final_result("UNSUPPORTED_OWNER_DECISION", "POST_STATE_MISMATCH")
if bar and not fault:
    wait("observed")
    if not source_observation_unchanged() or (
        operation == "move" and path_identity(DESTINATION).get("kind") != "absent"
    ):
        final_result("CONFLICT_REBASE", "PREIMAGE_DRIFT")

if path_identity(LOCK_ROOT).get("kind") == "absent":
    try:
        mkdir(LOCK_ROOT)
    except FileExistsError:
        if path_identity(LOCK_ROOT).get("kind") != "directory":
            final_result("UNSUPPORTED_OWNER_DECISION", "PATH_NOT_REGULAR")
displaced = False
move_destination_published = False


def mark_displaced():
    global displaced
    displaced = True


def mark_move_destination_published():
    global move_destination_published
    move_destination_published = True


try:
    for lock in lock_paths:
        try:
            mkdir(lock)
            write_new(lock / "owner", owner.encode("ascii"))
            held.append(lock)
        except FileExistsError:
            final_result("CONFLICT_REBASE", "TARGET_LOCK_BUSY")

    if not source_observation_unchanged() or (
        operation == "move" and path_identity(DESTINATION).get("kind") != "absent"
    ):
        final_result("CONFLICT_REBASE", "PREIMAGE_DRIFT")

    if operation == "move":
        time.sleep(0.05)
        if not source_observation_unchanged() or path_identity(DESTINATION).get("kind") != "absent":
            final_result("CONFLICT_REBASE", "PREIMAGE_DRIFT")
        persist_journal("PLANNED")
        try:
            link(SOURCE, DESTINATION, mark_move_destination_published)
        except FileExistsError:
            final_result("CONFLICT_REBASE", "DESTINATION_EXISTS")
        except OSError:
            if move_destination_published:
                raise
            final_result("UNSUPPORTED_OWNER_DECISION", "PATH_NOT_REGULAR")
        persist_journal("PUBLICATION_DURABLE", [DESTINATION])
        phase_hook("move-destination-published")
        if regular_bytes(SOURCE) != preimage_data or regular_bytes(DESTINATION) != preimage_data:
            persist_journal("RECOVERY_REQUIRED", [DESTINATION])
            final_result("RECOVERY_REQUIRED", "RESIDUE_RETAINED", [JOURNAL, DESTINATION])
        unlink(SOURCE)
        final_result("COMMITTED")

    persist_journal("PLANNED")
    replace(SOURCE, BACKUP, mark_displaced)
    persist_journal("DISPLACEMENT_DURABLE", [BACKUP])
    if fault == "after-displacement":
        wait("paused")
        link(BACKUP, SOURCE)
        unlink(BACKUP)
        final_result("MUTATION_FAILED_ROLLED_BACK")
    if operation == "delete":
        unlink(BACKUP)
        final_result("COMMITTED")

    write_new(STAGE, candidate_data)
    link(STAGE, SOURCE)
    unlink(STAGE)
    persist_journal("PUBLICATION_DURABLE", [BACKUP])
    if fault == "after-publication":
        wait("paused")
        unlink(SOURCE)
        link(BACKUP, SOURCE)
        unlink(BACKUP)
        final_result("MUTATION_FAILED_ROLLED_BACK")
    if fault == "post-state-mismatch":
        wait("paused")
        wait("observed-after-external", "continue-after-external")
        if path_identity(SOURCE).get("kind") == "regular":
            unlink(SOURCE)
        link(BACKUP, SOURCE)
        unlink(BACKUP)
        final_result("POST_STATE_MISMATCH_ROLLED_BACK")
    for _ in range(30):
        if regular_bytes(SOURCE) != candidate_data:
            break
        time.sleep(0.005)
    if regular_bytes(SOURCE) != candidate_data:
        persist_journal("ROLLBACK_CONFLICT", [BACKUP])
        final_result("ROLLBACK_CONFLICT", "ROLLBACK_TARGET_CHANGED", [JOURNAL, BACKUP])
    unlink(BACKUP)
    final_result("COMMITTED")
except RuntimeError as error:
    if str(error).startswith("EFFECT_SET_INCOMPLETE:"):
        final_result("UNSUPPORTED_OWNER_DECISION", "EFFECT_SET_INCOMPLETE", [JOURNAL] if JOURNAL.exists() else [])
    raise
except OSError:
    rollback_residue = [path for path in (JOURNAL, BACKUP, STAGE, DESTINATION) if path is not None and path_identity(path).get("kind") != "absent"]
    try:
        if operation == "move" and move_destination_published:
            if path_identity(SOURCE).get("kind") == "regular" and path_identity(DESTINATION).get("kind") == "regular":
                unlink(DESTINATION)
                final_result("MUTATION_FAILED_ROLLED_BACK", "IO_FAILURE")
        elif displaced and path_identity(BACKUP).get("kind") == "regular":
            if path_identity(SOURCE).get("kind") == "regular":
                unlink(SOURCE)
            link(BACKUP, SOURCE)
            unlink(BACKUP)
            if path_identity(STAGE).get("kind") != "absent":
                unlink(STAGE)
            final_result("MUTATION_FAILED_ROLLED_BACK", "IO_FAILURE")
        elif not displaced and not move_destination_published:
            final_result("MUTATION_FAILED_NO_STATE_CHANGE", "IO_FAILURE")
    except (OSError, RuntimeError):
        rollback_residue = [path for path in (JOURNAL, BACKUP, STAGE, DESTINATION) if path is not None and path_identity(path).get("kind") != "absent"]
    try:
        persist_journal("ROLLBACK_FAILED_WITH_RESIDUE", rollback_residue)
    except (OSError, RuntimeError):
        pass
    final_result("ROLLBACK_FAILED_WITH_RESIDUE", "IO_FAILURE", rollback_residue)
finally:
    if not retain_owned_locks:
        release_locks()
PY
