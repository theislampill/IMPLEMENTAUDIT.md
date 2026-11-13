#!/usr/bin/env bash
# Optional R0035 qualification transport. Canonical verify-package is unchanged.
# Command bytes come only from the exact revalidated canonical registry mapping.
set -euo pipefail
if [ "${1:-}" = "--isolated-leaf" ]; then
  # The task acquirer supplies the closed filesystem/environment. This route
  # emits no canonical terminal marker. The default closes every evidence fd.
  if [ "$#" -eq 4 ]; then
    exec python -c '
import hashlib, os, sys
source, digest = sys.argv[1:]
if hashlib.sha256(source.encode()).hexdigest() != digest:
    raise SystemExit(2)
os.closerange(3, 4096)
os.execv("/usr/bin/bash", ["bash", "--noprofile", "--norc", "-c", source])
' "$3" "$4"
  fi
  [ "$#" -eq 6 ] && [ "$5" = "ORIGINAL96_PRIVATE_DOCS_V1" ] || exit 2
  # Only the fixed original96 image owns a writable docs parent. Its existing
  # bootstrap retains one bounded census fd; the actual original receives none.
  exec python -I -B -c '
import fcntl, hashlib, json, os, signal, stat, struct, subprocess, sys

def identity(info):
    return (info.st_dev, info.st_ino, info.st_mode, info.st_nlink,
            info.st_size, info.st_mtime_ns, info.st_ctime_ns)

def census(root, config):
    result = {"files": {}, "directories": {}}
    count = 0
    def visit(directory, relative):
        nonlocal count
        count += 1
        if count > config["entry_limit"]:
            raise ValueError("private census entry bound exceeded")
        before = os.fstat(directory)
        result["directories"][relative] = dict(mode=stat.S_IMODE(before.st_mode),
            read_only=bool(os.fstatvfs(directory).f_flag & os.ST_RDONLY), nlink=before.st_nlink)
        names = []
        with os.scandir(directory) as entries:
            for entry in entries:
                if len(names) + count >= config["entry_limit"]:
                    raise ValueError("private census directory population bound exceeded")
                names.append(entry.name)
        for name in sorted(names):
            path = name if relative == "." else relative + "/" + name
            if len(path.encode("utf-8")) > config["path_bytes"]:
                raise ValueError("private census path bound exceeded")
            info = os.stat(name, dir_fd=directory, follow_symlinks=False)
            flags = os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK
            if stat.S_ISDIR(info.st_mode):
                member = os.open(name, flags | os.O_DIRECTORY, dir_fd=directory)
                try:
                    if identity(info) != identity(os.fstat(member)):
                        raise ValueError("private census directory changed")
                    visit(member, path)
                finally:
                    os.close(member)
            elif stat.S_ISREG(info.st_mode):
                count += 1
                if count > config["entry_limit"] or info.st_size > config["file_bytes"]:
                    raise ValueError("private census file bound exceeded")
                member = os.open(name, flags, dir_fd=directory)
                try:
                    before_file = os.fstat(member)
                    if not stat.S_ISREG(before_file.st_mode) or identity(info) != identity(before_file):
                        raise ValueError("private census file changed")
                    digest, size = hashlib.sha256(), 0
                    while True:
                        data = os.read(member, min(1024**2, config["file_bytes"] + 1 - size))
                        if not data:
                            break
                        size += len(data)
                        if size > config["file_bytes"]:
                            raise ValueError("private census file grew beyond bound")
                        digest.update(data)
                    if size != before_file.st_size or identity(before_file) != identity(os.fstat(member)):
                        raise ValueError("private census bytes changed")
                    result["files"][path] = dict(mode=stat.S_IMODE(before_file.st_mode),
                        bytes=size, sha256=digest.hexdigest(), nlink=before_file.st_nlink,
                        read_only=bool(os.fstatvfs(member).f_flag & os.ST_RDONLY))
                finally:
                    os.close(member)
            else:
                raise ValueError("nonordinary member in private census")
        if identity(before) != identity(os.fstat(directory)):
            raise ValueError("private census directory changed during read")
    descriptor = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_NONBLOCK)
    try:
        visit(descriptor, ".")
    finally:
        os.close(descriptor)
    return result

def observe(config):
    mounts = {}
    for path in config["immutable_paths"]:
        descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
        try:
            mounts[path] = bool(os.fstatvfs(descriptor).f_flag & os.ST_RDONLY)
        finally:
            os.close(descriptor)
    return dict(docs=census(config["root"], config), tmp=census(config["tmp_root"], config),
                immutable_mounts=mounts)

def baseline_matches(observed, baseline):
    return (set(observed["files"]) == set(baseline["files"])
        and {name: entry["mode"] for name, entry in observed["directories"].items()} == baseline["directories"]
        and all({key: observed["files"][name][key] for key in ("mode", "bytes", "sha256")} == expected
                for name, expected in baseline["files"].items()))

def require_before(observed, config):
    if (not baseline_matches(observed["docs"], config["baseline"])
            or observed["tmp"]["files"] or set(observed["tmp"]["directories"]) != {"."}
            or observed["docs"]["directories"]["."]["read_only"] is not False
            or observed["tmp"]["directories"]["."]["read_only"] is not False
            or set(observed["immutable_mounts"]) != set(config["immutable_paths"])
            or not all(value is True for value in observed["immutable_mounts"].values())):
        raise ValueError("original96 before census differs from its protected image")

def store_record(descriptor, record, capacity):
    data = json.dumps(record, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")
    if len(data) > capacity - 8:
        raise ValueError("private census report bound exceeded")
    def write_all(data, offset):
        while data:
            written = os.pwrite(descriptor, data, offset)
            if written <= 0:
                raise OSError("private census short write")
            data, offset = data[written:], offset + written
    write_all(bytes(8), 0)
    write_all(data, 8)
    write_all(struct.pack("!Q", len(data)), 0)

node, source, digest, policy, fd_text = sys.argv[1:]
if (node != "COMMAND:tests/claim-boundary-proof-levels.test.sh:0"
        or source != "bash tests/claim-boundary-proof-levels.test.sh\n"
        or hashlib.sha256(source.encode()).hexdigest() != digest
        or policy != "ORIGINAL96_PRIVATE_DOCS_V1"):
    raise SystemExit(2)
descriptor = int(fd_text)
capacity = 4 * 1024**2
if not 3 <= descriptor < 4096 or os.fstat(descriptor).st_size != capacity:
    raise SystemExit(2)
seals = fcntl.fcntl(descriptor, fcntl.F_GET_SEALS)
if seals != fcntl.F_SEAL_GROW | fcntl.F_SEAL_SHRINK:
    raise SystemExit(2)
os.closerange(3, descriptor)
os.closerange(descriptor + 1, 4096)
os.set_inheritable(descriptor, False)
config_fd = os.open("/profile/original96-overlay.json", os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
try:
    if not stat.S_ISREG(os.fstat(config_fd).st_mode):
        raise ValueError("nonordinary fixed census configuration")
    raw = os.read(config_fd, 1024**2 + 1)
    if len(raw) > 1024**2:
        raise ValueError("fixed census configuration bound exceeded")
    config = json.loads(raw)
finally:
    os.close(config_fd)
if (config["policy"] != policy or config["root"] != "/work/docs" or config["tmp_root"] != "/tmp"
        or config["buffer_bytes"] != capacity):
    raise SystemExit(2)
record = dict(schema="implementaudit.original96-private-observation.v1", policy=policy,
              phase="INITIAL", original_started=False)
child, original_exit = None, None
try:
    record.update(phase="BEFORE", before=observe(config))
    store_record(descriptor, record, capacity)
    require_before(record["before"], config)
    child = subprocess.Popen(["/usr/bin/bash", "--noprofile", "--norc", "-c", source], close_fds=True)
    record.update(phase="RUNNING", original_started=True)
    store_record(descriptor, record, capacity)
    original_exit = child.wait()
    record.update(original_exit=original_exit, after=observe(config), phase="AFTER")
    store_record(descriptor, record, capacity)
except BaseException as error:
    if child is not None:
        if child.poll() is None:
            child.kill()
        original_exit = child.wait()
        record.update(original_started=True, original_exit=original_exit)
    record.update(phase="ERROR", error_type=type(error).__name__, detail=str(error)[:4096])
    try:
        store_record(descriptor, record, capacity)
    except (OSError, ValueError):
        pass
    print("original96 private census refused: " + type(error).__name__, file=sys.stderr)
finally:
    os.close(descriptor)
if original_exit is None:
    raise SystemExit(2)
if original_exit < 0:
    selected_signal = -original_exit
    if selected_signal not in (signal.SIGKILL, signal.SIGSTOP):
        signal.signal(selected_signal, signal.SIG_DFL)
    os.kill(os.getpid(), selected_signal)
    os._exit(128 + selected_signal)
raise SystemExit(original_exit)
' "$2" "$3" "$4" "$5" "$6"
fi
if [ "$#" -lt 4 ]; then
  printf 'work-graph-verifier: command stream, trace, node count and stream digest required\n' >&2
  exit 2
fi
r0035_verifier_stream="$1"
r0035_verifier_trace="$2"
r0035_verifier_expected="$3"
r0035_verifier_digest="$4"
shift 4
case "$r0035_verifier_expected" in ''|*[!0-9]*) exit 2;; esac
if ! [[ "$r0035_verifier_digest" =~ ^[0-9a-f]{64}$ ]]; then exit 2; fi
# Acquire one retained snapshot. Validation below hashes these exact arrays,
# never a path which could be replaced before a second open.
r0035_verifier_ids=()
r0035_verifier_sources=()
# A path check followed by a Bash open can follow a replacement symlink or
# block on a replacement FIFO. Acquire the final component once, through a
# nonblocking no-follow descriptor, before sending any bytes to this shell.
# The 16 MiB transport bound covers the complete current compiler stream;
# this is not acquisition of its ancestor namespace or executable runtime.
exec {r0035_verifier_frame_fd}< <(python -B -c '
import os, stat, sys

def identity(value):
    return (value.st_dev, value.st_ino, value.st_mode, value.st_size,
            value.st_mtime_ns, value.st_ctime_ns)

try:
    if not all(hasattr(os, name) for name in ("O_NOFOLLOW", "O_NONBLOCK")):
        raise ValueError("unsupported descriptor acquisition")
    descriptor = os.open(sys.argv[1], os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    try:
        before = os.fstat(descriptor)
        limit = 16 * 1024 * 1024
        if not stat.S_ISREG(before.st_mode) or before.st_size > limit:
            raise ValueError("nonregular or oversized stream")
        with os.fdopen(descriptor, "rb", closefd=False) as source:
            data = source.read(limit + 1)
        if (len(data) > limit or len(data) != before.st_size or
                identity(before) != identity(os.fstat(descriptor))):
            raise ValueError("stream changed during acquisition")
    finally:
        os.close(descriptor)
    sys.stdout.buffer.write(data)
    sys.stdout.buffer.flush()
except (OSError, ValueError):
    print("work-graph-verifier: command stream acquisition refused", file=sys.stderr)
    raise SystemExit(2)
' "$r0035_verifier_stream")
r0035_verifier_acquirer_pid=$!
while :; do
  r0035_verifier_id=''
  if ! IFS= read -r -d '' -u "$r0035_verifier_frame_fd" r0035_verifier_id; then
    if [ -n "$r0035_verifier_id" ]; then exit 2; fi
    break
  fi
  if ! IFS= read -r -d '' -u "$r0035_verifier_frame_fd" r0035_verifier_source; then exit 2; fi
  if [ -z "$r0035_verifier_id" ] || [ -z "$r0035_verifier_source" ]; then exit 2; fi
  r0035_verifier_ids+=("$r0035_verifier_id")
  r0035_verifier_sources+=("$r0035_verifier_source")
done
# No frame descriptor survives into a tested program; caller stdin is intact.
exec {r0035_verifier_frame_fd}<&-
# Process substitution does not propagate its producer status through exec.
# Even complete bytes from a failed producer must never authorize execution.
if ! wait "$r0035_verifier_acquirer_pid"; then exit 2; fi
if [ "${#r0035_verifier_ids[@]}" -ne "$r0035_verifier_expected" ]; then exit 2; fi
# This digest is supplied after exact compiler rederivation. The transport is
# not an untrusted-command sandbox or another canonical registry owner.
if ! {
  for r0035_verifier_index in "${!r0035_verifier_ids[@]}"; do
    printf '%s\0%s\0' "${r0035_verifier_ids[$r0035_verifier_index]}" "${r0035_verifier_sources[$r0035_verifier_index]}"
  done
} | python -B -c '
import hashlib, sys
data = sys.stdin.buffer.read()
frames = data.split(b"\0")
valid = (hashlib.sha256(data).hexdigest() == sys.argv[1] and
         len(frames) == 2 * int(sys.argv[2]) + 1 and frames[-1] == b"" and
         all(frames[:-1]) and len(set(frames[0:-1:2])) == int(sys.argv[2]) and
         frames[0] == b"PRELUDE" and frames[-3] == b"TERMINAL")
raise SystemExit(0 if valid else 2)
' "$r0035_verifier_digest" "$r0035_verifier_expected"; then
  printf 'work-graph-verifier: invalid command stream identity or framing\n' >&2
  exit 2
fi
r0035_verifier_seen=0
exec 3>"$r0035_verifier_trace"
for r0035_verifier_index in "${!r0035_verifier_ids[@]}"; do
  r0035_verifier_id="${r0035_verifier_ids[$r0035_verifier_index]}"
  r0035_verifier_source="${r0035_verifier_sources[$r0035_verifier_index]}"
  printf '%s\tSTART\n' "$r0035_verifier_id" >&3
  # One shell retains prelude locals/functions, traps, arguments and set -e.
  # BASH_SOURCE resolves this helper in the same scripts/ directory as the
  # legacy registry, preserving the canonical repo-root calculation.
  eval "$r0035_verifier_source"
  printf '%s\tPASS\n' "$r0035_verifier_id" >&3
  r0035_verifier_seen=$((r0035_verifier_seen + 1))
done
if [ "$r0035_verifier_seen" -ne "$r0035_verifier_expected" ]; then
  printf 'work-graph-verifier: incomplete node population\n' >&2
  exit 2
fi
