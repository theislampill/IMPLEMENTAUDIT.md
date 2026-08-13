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
import errno
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

if os.name == "nt":
    import msvcrt
else:
    import fcntl

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
COORDINATION_SCOPE = "GOVERNED_HELPER_ROUTED_WRITERS_ONLY"


class WriterDomainBreach(RuntimeError):
    """Detected interference outside the cooperating helper-writer domain."""


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
        "coordination_scope": COORDINATION_SCOPE,
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
LOCK_GATE = LOCK_ROOT / "namespace.gate"
RELEASED_LOCK_ROOT = TX / "released-locks"

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
owner = secrets.token_hex(16)
released_locks = {lock: RELEASED_LOCK_ROOT / lock.name for lock in lock_paths}

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
plan(RELEASED_LOCK_ROOT, ["released-lock-root"], ["mkdir", "fsync"], "durable")
plan(LOCK_ROOT, ["lock-root"], ["mkdir", "fsync"], "durable")
plan(LOCK_GATE, ["lock-namespace-gate"], ["create", "write", "fsync"], "durable")
plan(LOCK_PARENT, ["lock-parent"], ["fsync"], "durable")
for lock in lock_paths:
    released = released_locks[lock]
    plan(lock, ["path-lock", "residue"], ["mkdir", "replace", "fsync"], "transient")
    plan(lock / "owner", ["lock-owner", "residue"], ["create", "write", "fsync"], "transient")
    plan(released, ["released-lock-record"], ["replace", "fsync"], "durable")
    plan(released / "owner", ["released-lock-owner"], [], "durable")

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
namespace_gate_fd = None


def acquire_window_gate():
    """Lock the persistent governed-writer inode before any run-root effect."""
    global namespace_gate_fd
    try:
        gate_stat = os.lstat(LOCK_GATE)
    except OSError as error:
        raise WriterDomainBreach("governed-writer namespace gate is unavailable") from error
    if (
        not stat.S_ISREG(gate_stat.st_mode)
        or stat.S_ISLNK(gate_stat.st_mode)
        or is_reparse(gate_stat)
        or gate_stat.st_nlink != 1
        or gate_stat.st_size != 1
    ):
        raise WriterDomainBreach("governed-writer namespace gate is unavailable")
    flags = os.O_RDWR | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0)
    fd = os.open(LOCK_GATE, flags)
    try:
        opened = os.fstat(fd)
        if not stat.S_ISREG(opened.st_mode) or opened.st_nlink != 1:
            raise WriterDomainBreach("lock namespace gate is not a unique regular file")
        os.lseek(fd, 0, os.SEEK_SET)
        if os.name == "nt":
            while True:
                try:
                    msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)
                    break
                except OSError as error:
                    if error.errno not in {errno.EACCES, errno.EAGAIN, errno.EDEADLK}:
                        raise
                    time.sleep(0.05)
        else:
            fcntl.flock(fd, fcntl.LOCK_EX)
        current = os.lstat(LOCK_GATE)
        if (
            not stat.S_ISREG(current.st_mode)
            or stat.S_ISLNK(current.st_mode)
            or is_reparse(current)
            or current.st_nlink != 1
            or (current.st_dev, current.st_ino) != (opened.st_dev, opened.st_ino)
        ):
            raise WriterDomainBreach("lock namespace gate identity changed")
        namespace_gate_fd = fd
    except BaseException:
        try:
            if os.name == "nt":
                os.lseek(fd, 0, os.SEEK_SET)
                msvcrt.locking(fd, msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(fd, fcntl.LOCK_UN)
        except OSError:
            pass
        os.close(fd)
        raise


def release_window_gate():
    global namespace_gate_fd
    if namespace_gate_fd is None:
        return []
    fd = namespace_gate_fd
    namespace_gate_fd = None
    errors = []
    try:
        if os.name == "nt":
            os.lseek(fd, 0, os.SEEK_SET)
            msvcrt.locking(fd, msvcrt.LK_UNLCK, 1)
        else:
            fcntl.flock(fd, fcntl.LOCK_UN)
    except BaseException as error:
        errors.append(error)
    try:
        os.close(fd)
    except BaseException as error:
        errors.append(error)
    return errors


def current_controller_failure():
    marker = RUN / ".controller"
    identity = path_identity(marker)
    same = lambda l, r: os.path.normcase(os.path.abspath(native_input(l))) == os.path.normcase(os.path.abspath(r))
    def record(controller):
        completed = subprocess.run(
            [BASH_EXE, bash_path(SCRIPT_DIR / "claim-run.sh"), "--current-controller", controller],
            cwd=os.fspath(REPO), text=True, capture_output=True,
        )
        return completed.returncode, completed.stdout.rstrip("\n").split("\t")
    if identity.get("kind") == "absent":
        refs = subprocess.run(
            ["git", "for-each-ref", "--format=%(refname:strip=3)", "refs/implementaudit/controllers/"],
            cwd=os.fspath(REPO), text=True, capture_output=True,
        )
        if refs.returncode != 0:
            return "STALE_CONTROLLER_CUSTODY"
        for controller in refs.stdout.splitlines():
            rc, fields = record(controller)
            if rc == 0 and len(fields) == 4 and same(fields[1], REPO) and same(fields[2], RUN) and fields[3] == claim_id:
                return "STALE_CONTROLLER_CUSTODY"
        return None
    if identity.get("kind") != "regular" or identity.get("link_count") != 1 or not contained_regular(marker, RUN):
        return "STALE_CONTROLLER_CUSTODY"
    match = re.fullmatch(rb"controller_id=([a-z0-9](?:[a-z0-9-]{0,47}))\n", marker.read_bytes())
    if match is None:
        return "STALE_CONTROLLER_CUSTODY"
    controller = match.group(1).decode("ascii")
    rc, fields = record(controller)
    if rc != 0 or len(fields) != 4:
        return "STALE_CONTROLLER_CUSTODY"
    if not (fields[0] == controller and same(fields[1], REPO) and same(fields[2], RUN) and fields[3] == claim_id):
        return "STALE_CONTROLLER_CUSTODY"
    current = subprocess.run(
        [BASH_EXE, bash_path(SCRIPT_DIR / "claim-run.sh"), "--require-current-continuity", controller],
        cwd=os.fspath(REPO), text=True, capture_output=True,
    )
    return None if current.returncode == 0 else "STALE_CONTINUITY_RECEIPT"


def window_intents():
    runs = REPO / ".IMPLEMENTAUDIT" / "runs"
    if path_identity(runs).get("kind") == "absent":
        return []
    if not safe_directory_chain(runs, REPO):
        raise WriterDomainBreach("verification-window run base custody is unsafe")
    found = []
    for run in sorted(runs.iterdir(), key=lambda path: path.name):
        run_kind = path_identity(run).get("kind")
        if run_kind in {"symlink", "other"}:
            raise WriterDomainBreach("verification-window run census contains unsafe custody")
        if run_kind != "directory":
            continue
        background = run / "background"
        if path_identity(background).get("kind") == "absent":
            continue
        if not safe_directory_chain(background, run):
            raise WriterDomainBreach("verification-window background custody is unsafe")
        for chain in sorted(background.iterdir(), key=lambda path: path.name):
            chain_kind = path_identity(chain).get("kind")
            if chain_kind in {"symlink", "other"}:
                raise WriterDomainBreach("verification-window chain census contains unsafe custody")
            if chain_kind != "directory":
                continue
            intent = chain / "launch-intent.md"
            identity = path_identity(intent)
            if identity.get("kind") == "absent":
                continue
            if identity.get("kind") != "regular" or identity.get("link_count") != 1:
                raise WriterDomainBreach("verification-window intent is not a unique regular file")
            found.append(intent)
    return found


def verification_window_failure():
    head = subprocess.run(
        ["git", "-C", os.fspath(REPO), "rev-parse", "HEAD"],
        text=True,
        capture_output=True,
        check=False,
    )
    if head.returncode != 0 or not re.fullmatch(r"[0-9a-f]{40}", head.stdout.strip()):
        return "verification-window repository identity unavailable"
    environment = os.environ.copy()
    environment["IMPLEMENTAUDIT_WINDOW_PLANNED_PATHS_JSON"] = json.dumps(
        [row["path"] for row in planned if row["scope"] == "repo"],
        separators=(",", ":"),
    )
    checker = SCRIPT_DIR / "check-evidence-anchor.sh"
    for intent in window_intents():
        completed = subprocess.run(
            [BASH_EXE, bash_path(checker), "--window", bash_path(intent), "--now", head.stdout.strip(), "--planned-paths-env"],
            cwd=os.fspath(REPO), env=environment, text=True, capture_output=True, check=False,
        )
        if completed.returncode != 0:
            return (completed.stderr or completed.stdout).strip() or "verification-window authority rejected planned effects"
    return None


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


def notify_mutated(callback, path, effect):
    if callback is not None:
        callback(path, effect)


def notify_durable(callback, path, effect):
    if callback is not None:
        callback(path, effect)


def record_applied(path, effect, before, after, effect_row=None):
    if effect_row is None:
        record(path, effect, before, after)
        return
    if effect_row.get("sequence") != len(actual) + 1:
        raise RuntimeError("EFFECT_SET_SEQUENCE_DRIFT")
    if effect_row.get("scope") != "repo" or effect_row.get("path") != repo_relative(path) or effect_row.get("effect") != effect:
        raise RuntimeError("EFFECT_SET_PRECOMPUTE_DRIFT")
    actual.append(dict(effect_row))


def mkdir(path, on_mutated=None, on_durable=None, effect_row=None, sync_parent=True):
    before = path_identity(path)
    authorise(path, "mkdir")
    try:
        os.mkdir(path)
    except FileExistsError:
        record(path, "mkdir", before, path_identity(path), "not-applied")
        raise
    notify_mutated(on_mutated, path, "mkdir")
    record_applied(path, "mkdir", before, path_identity(path), effect_row)
    if sync_parent:
        fsync_dir(path.parent)
        notify_durable(on_durable, path, "mkdir")


def write_new(path, data, on_mutated=None, on_durable=None, effect_rows=None, sync_parent=True):
    before = path_identity(path)
    authorise(path, "create")
    authorise(path, "write")
    authorise(path, "fsync")
    rows = list(effect_rows or (None, None, None))
    if len(rows) != 3:
        raise RuntimeError("EFFECT_SET_PRECOMPUTE_DRIFT")
    with path.open("xb", buffering=0) as handle:
        notify_mutated(on_mutated, path, "create")
        record_applied(path, "create", before, path_identity(path), rows[0])
        written = handle.write(data)
        notify_mutated(on_mutated, path, "write")
        record_applied(path, "write", before, path_identity(path), rows[1])
        if written != len(data):
            raise OSError("short write")
        os.fsync(handle.fileno())
        record_applied(path, "fsync", path_identity(path), path_identity(path), rows[2])
    if sync_parent:
        fsync_dir(path.parent)
        notify_durable(on_durable, path, "write")


def unlink(path, on_mutated=None, on_durable=None, effect_row=None, sync_parent=True):
    before = path_identity(path)
    authorise(path, "unlink")
    os.unlink(path)
    notify_mutated(on_mutated, path, "unlink")
    record_applied(path, "unlink", before, path_identity(path), effect_row)
    if sync_parent:
        fsync_dir(path.parent)
        notify_durable(on_durable, path, "unlink")


def link(source, destination, on_mutated=None, on_durable=None, effect_row=None, sync_parent=True):
    before = path_identity(destination)
    authorise(destination, "link")
    os.link(source, destination)
    notify_mutated(on_mutated, destination, "link")
    record_applied(destination, "link", before, path_identity(destination), effect_row)
    if sync_parent:
        fsync_dir(destination.parent)
        notify_durable(on_durable, destination, "link")


def replace(source, destination, on_mutated=None, on_durable=None, effect_rows=None, sync_parents=True):
    source_before = path_identity(source)
    destination_before = path_identity(destination)
    authorise(source, "replace")
    authorise(destination, "replace")
    rows = list(effect_rows or (None, None))
    if len(rows) != 2:
        raise RuntimeError("EFFECT_SET_PRECOMPUTE_DRIFT")
    os.replace(source, destination)
    notify_mutated(on_mutated, source, "replace")
    record_applied(source, "replace", source_before, path_identity(source), rows[0])
    record_applied(destination, "replace", destination_before, path_identity(destination), rows[1])
    if sync_parents:
        fsync_dir(source.parent)
        if destination.parent != source.parent:
            fsync_dir(destination.parent)
        notify_durable(on_durable, destination, "replace")


def rename_no_replace(source, destination, on_mutated=None, on_durable=None, effect_rows=None, sync_parents=True):
    """Atomically move a custody directory without replacing any destination."""
    source_before = path_identity(source)
    destination_before = path_identity(destination)
    authorise(source, "replace")
    authorise(destination, "replace")
    rows = list(effect_rows or (None, None))
    if len(rows) != 2:
        raise RuntimeError("EFFECT_SET_PRECOMPUTE_DRIFT")
    if os.name == "nt":
        os.rename(source, destination)
    elif sys.platform.startswith("linux"):
        libc = ctypes.CDLL(None, use_errno=True)
        try:
            renameat2 = libc.renameat2
        except AttributeError as error:
            raise OSError(errno.ENOTSUP, "atomic no-replace rename is unavailable") from error
        renameat2.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_uint]
        renameat2.restype = ctypes.c_int
        if renameat2(-100, os.fsencode(source), -100, os.fsencode(destination), 1) != 0:
            code = ctypes.get_errno()
            if code == errno.EEXIST:
                raise FileExistsError(code, os.strerror(code), str(destination))
            raise OSError(code, os.strerror(code), str(destination))
    elif sys.platform == "darwin":
        libc = ctypes.CDLL(None, use_errno=True)
        try:
            renamex_np = libc.renamex_np
        except AttributeError as error:
            raise OSError(errno.ENOTSUP, "atomic no-replace rename is unavailable") from error
        renamex_np.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_uint]
        renamex_np.restype = ctypes.c_int
        if renamex_np(os.fsencode(source), os.fsencode(destination), 4) != 0:
            code = ctypes.get_errno()
            if code == errno.EEXIST:
                raise FileExistsError(code, os.strerror(code), str(destination))
            raise OSError(code, os.strerror(code), str(destination))
    else:
        raise OSError(errno.ENOTSUP, "atomic no-replace rename is unavailable")
    notify_mutated(on_mutated, source, "replace")
    record_applied(source, "replace", source_before, path_identity(source), rows[0])
    record_applied(destination, "replace", destination_before, path_identity(destination), rows[1])
    if sync_parents:
        fsync_dir(source.parent)
        if destination.parent != source.parent:
            fsync_dir(destination.parent)
        notify_durable(on_durable, destination, "replace")


def rmdir(path, on_mutated=None, on_durable=None, effect_row=None, sync_parent=True):
    before = path_identity(path)
    authorise(path, "rmdir")
    os.rmdir(path)
    notify_mutated(on_mutated, path, "rmdir")
    record_applied(path, "rmdir", before, path_identity(path), effect_row)
    if sync_parent:
        fsync_dir(path.parent)
        notify_durable(on_durable, path, "rmdir")


def fsync_dir(path, effect_row=None):
    authorise(path, "fsync")
    before = path_identity(path)
    sync_directory_raw(path)
    record_applied(path, "fsync", before, path_identity(path), effect_row)


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
        "coordination_scope": COORDINATION_SCOPE,
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


def mark_init_parent(_path, _effect):
    global init_created_parent
    init_created_parent = True


def mark_init_tx(_path, _effect):
    global init_created_tx
    init_created_tx = True


def mark_init_authority(_path, _effect):
    global init_created_authority
    init_created_authority = True


def residue_row(path):
    return {
        "scope": "repo",
        "path": repo_relative(path),
        "identity": path_identity(path),
        "custody": "run-owner-required",
    }


def result_record(status, reason_code, residue_paths, effect_rows):
    return {
        "schema": "implementaudit.observation_bound_mutation.v2",
        "transaction_id": transaction_id,
        "claim_id": claim_id,
        "phase": args.phase,
        "step": args.step,
        "authority_binding_sha256": authority_projection["authority_binding_sha256"],
        "coordination_scope": COORDINATION_SCOPE,
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
        "residue": [residue_row(path) for path in residue_paths if path_identity(path).get("kind") != "absent"],
    }


def persist_result_record(status, reason_code, residue_paths):
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
    payload = result_record(status, reason_code, residue_paths, actual + future)
    write_new(RESULT, canonical(payload), effect_rows=future[:3], sync_parent=False)
    fsync_dir(TX, future[3])
    return result_record(status, reason_code, residue_paths, actual)


def persist_terminal_or_fallback(status, reason_code, residue_paths):
    try:
        return status, persist_result_record(status, reason_code, residue_paths)
    except (OSError, RuntimeError):
        fallback_paths = list(residue_paths)
        if path_identity(TX).get("kind") == "directory" and TX not in fallback_paths:
            fallback_paths.append(TX)
        if path_identity(RESULT).get("kind") != "absent":
            fallback_paths.append(RESULT)
        status = "ROLLBACK_FAILED_WITH_RESIDUE"
        return status, result_record(status, "RESULT_PERSISTENCE_FAILURE", fallback_paths, actual)


def initialisation_residue_paths():
    owned_paths = (
        (AUTHORITY, init_created_authority),
        (TX, init_created_tx),
        (TX_PARENT, init_created_parent),
    )
    return [path for path, owned in owned_paths if owned and path_identity(path).get("kind") != "absent"]


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
        residue_paths = initialisation_residue_paths()
    gate_release_errors = release_window_gate()
    if gate_release_errors:
        residue_paths.append(LOCK_GATE)
    status = "MUTATION_FAILED_NO_STATE_CHANGE" if not residue_paths else "ROLLBACK_FAILED_WITH_RESIDUE"
    result = result_record(status, "INITIALISATION_IO_FAILURE", residue_paths, actual)
    if status == "ROLLBACK_FAILED_WITH_RESIDUE" and path_identity(TX).get("kind") == "directory":
        status, result = persist_terminal_or_fallback(status, "INITIALISATION_IO_FAILURE", residue_paths)
    print(json.dumps(result, separators=(",", ":"), ensure_ascii=False))
    raise SystemExit(EXITS[status])


try:
    acquire_window_gate()
except WriterDomainBreach:
    emit_no_effect("UNSUPPORTED_OWNER_DECISION", "WRITER_DOMAIN_BREACH")
except OSError as error:
    sys.stderr.write(f"apply-observed-mutation: namespace gate acquisition failed: {error}\n")
    emit_no_effect("MUTATION_FAILED_NO_STATE_CHANGE", "IO_FAILURE")
controller_failure = current_controller_failure()
if controller_failure is not None:
    if release_window_gate():
        emit_no_effect("ROLLBACK_FAILED_WITH_RESIDUE", "GATE_RELEASE_FAILURE")
    emit_no_effect("UNSUPPORTED_OWNER_DECISION", controller_failure)
try:
    window_failure = verification_window_failure()
except (OSError, RuntimeError, WriterDomainBreach) as error:
    window_failure = str(error) or error.__class__.__name__
if window_failure is not None:
    sys.stderr.write(f"apply-observed-mutation: {window_failure}\n")
    if release_window_gate():
        emit_no_effect("ROLLBACK_FAILED_WITH_RESIDUE", "GATE_RELEASE_FAILURE")
    emit_no_effect("UNSUPPORTED_OWNER_DECISION", "OPEN_VERIFICATION_WINDOW")
phase_hook("window-scan-complete")

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

held = []
residue = []


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
    write_new(JOURNAL_TMP, data, effect_rows=future[:3], sync_parent=False)
    replace(JOURNAL_TMP, JOURNAL, effect_rows=future[3:5], sync_parents=False)
    fsync_dir(TX, future[5])


retain_owned_locks = False
lock_root_created = False


def mark_lock_root(_path, effect):
    global lock_root_created
    if effect == "mkdir":
        lock_root_created = True


def mark_lock_root_durable(_path, effect):
    global lock_root_created
    if effect == "mkdir":
        lock_root_created = False


def mark_lock_owned(lock):
    def mark(path, effect):
        entry = next((item for item in held if item["path"] == lock), None)
        if entry is None:
            entry = {
                "path": lock,
                "public_path": lock,
                "released_path": released_locks[lock],
                "lock_identity": path_identity(lock),
                "owner_created": False,
                "owner_identity": None,
                "owner_token_sha256": digest(owner.encode("ascii")),
                "conflict_paths": [],
            }
            held.append(entry)
        entry["lock_identity"] = path_identity(lock)
        if path == lock / "owner" and effect == "create":
            entry["owner_created"] = True
        if path == lock / "owner" and effect in {"create", "write"}:
            entry["owner_identity"] = path_identity(path)
    return mark


def mark_lock_released(entry):
    def mark(_path, effect):
        if effect == "replace":
            entry["path"] = entry["released_path"]
    return mark


def mark_lock_restored(entry):
    def mark(_path, effect):
        if effect == "replace":
            entry["path"] = entry["public_path"]
    return mark


def released_lock_matches(entry):
    released = entry["released_path"]
    current_lock = path_identity(released)
    current_owner = path_identity(released / "owner")
    return (
        current_lock == entry["lock_identity"]
        and entry["owner_created"]
        and current_owner == entry["owner_identity"]
        and current_owner.get("kind") == "regular"
        and current_owner.get("sha256") == entry["owner_token_sha256"]
    )


def release_locks():
    while held:
        entry = held[-1]
        public_lock = entry["public_path"]
        released = entry["released_path"]
        try:
            rename_no_replace(public_lock, released, mark_lock_released(entry))
            phase_hook("lock-release-published")
            if not released_lock_matches(entry):
                phase_hook("lock-release-mismatch")
                try:
                    rename_no_replace(released, public_lock, mark_lock_restored(entry))
                except (OSError, RuntimeError):
                    entry["conflict_paths"] = [public_lock, released]
                break
            held.pop()
        except (OSError, RuntimeError):
            break


def release_lock_root():
    return


def acquire_namespace_gate():
    if namespace_gate_fd is None:
        acquire_window_gate()


def release_namespace_gate():
    return release_window_gate()


def owned_lock_residue_paths():
    paths = []
    for entry in held:
        paths.extend([entry["path"], entry["path"] / "owner"])
        paths.extend(entry["conflict_paths"])
    if lock_root_created:
        paths.append(LOCK_ROOT)
    present = [path for path in paths if path_identity(path).get("kind") != "absent"]
    if held and not present and path_identity(TX).get("kind") == "directory":
        present.append(TX)
    return present


terminal_finalized = False


def final_result(status, reason_code="NONE", residue_paths=(), post_path=None):
    global retain_owned_locks, terminal_finalized
    uncertain_paths = list(residue_paths)
    if uncertain_paths:
        retain_owned_locks = True
        uncertain_paths.extend(owned_lock_residue_paths())
    else:
        if path_identity(JOURNAL).get("kind") != "absent":
            unlink(JOURNAL)
        release_locks()
        release_lock_root()
        cleanup_residue = owned_lock_residue_paths()
        if cleanup_residue:
            uncertain_paths.extend(cleanup_residue)
            retain_owned_locks = True
            status = "ROLLBACK_FAILED_WITH_RESIDUE"
            if reason_code == "NONE":
                reason_code = "IO_FAILURE"
    if status == "ROLLBACK_FAILED_WITH_RESIDUE":
        retain_owned_locks = True
    gate_release_errors = release_namespace_gate()
    if gate_release_errors:
        retain_owned_locks = True
        status = "ROLLBACK_FAILED_WITH_RESIDUE"
        reason_code = "GATE_RELEASE_FAILURE"
        uncertain_paths.append(LOCK_GATE)
        uncertain_paths.extend(owned_lock_residue_paths())
    status, result = persist_terminal_or_fallback(status, reason_code, uncertain_paths)
    if status == "ROLLBACK_FAILED_WITH_RESIDUE":
        retain_owned_locks = True
    terminal_finalized = True
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

displaced = False
move_destination_published = False


def mark_displaced(_path, _effect):
    global displaced
    displaced = True


def mark_move_destination_published(_path, _effect):
    global move_destination_published
    move_destination_published = True


try:
    mkdir(RELEASED_LOCK_ROOT)
    if path_identity(LOCK_ROOT).get("kind") == "absent":
        try:
            mkdir(LOCK_ROOT, on_mutated=mark_lock_root, on_durable=mark_lock_root_durable)
        except FileExistsError:
            if path_identity(LOCK_ROOT).get("kind") != "directory":
                final_result("UNSUPPORTED_OWNER_DECISION", "PATH_NOT_REGULAR")
    for lock in lock_paths:
        mark_owned = mark_lock_owned(lock)
        try:
            mkdir(lock, mark_owned)
            write_new(lock / "owner", owner.encode("ascii"), mark_owned)
        except FileExistsError:
            final_result("CONFLICT_REBASE", "TARGET_LOCK_BUSY")
    phase_hook("locks-acquired")

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
    if isinstance(error, WriterDomainBreach):
        final_result("UNSUPPORTED_OWNER_DECISION", "WRITER_DOMAIN_BREACH")
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
    if not terminal_finalized:
        if not retain_owned_locks:
            release_locks()
            release_lock_root()
        release_namespace_gate()
PY
