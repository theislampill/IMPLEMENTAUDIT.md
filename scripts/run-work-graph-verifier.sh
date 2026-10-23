#!/usr/bin/env bash
# Optional R0035 qualification transport. Canonical verify-package is unchanged.
# Command bytes come only from the exact revalidated canonical registry mapping.
set -euo pipefail
if [ "${1:-}" = "--isolated-leaf" ]; then
  # The task acquirer supplies the closed filesystem/environment. This route
  # emits no canonical terminal marker and inherits no evidence descriptors.
  [ "$#" -eq 4 ] || exit 2
  exec python -c '
import hashlib, os, sys
source, digest = sys.argv[1:]
if hashlib.sha256(source.encode()).hexdigest() != digest:
    raise SystemExit(2)
os.closerange(3, 4096)
os.execv("/usr/bin/bash", ["bash", "--noprofile", "--norc", "-c", source])
' "$3" "$4"
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
