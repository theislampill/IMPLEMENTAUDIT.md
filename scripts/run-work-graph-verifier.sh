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
if [ -L "$r0035_verifier_stream" ] || [ ! -f "$r0035_verifier_stream" ]; then exit 2; fi
r0035_verifier_ids=()
r0035_verifier_sources=()
exec {r0035_verifier_frame_fd}<"$r0035_verifier_stream"
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
