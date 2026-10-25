#!/usr/bin/env bash
set -euo pipefail

# Receiving-side handoff packet inspection (#15). Read-only. Verifies a
# packet's mechanically recomputable Class-1 claims against live state and
# enforces the three-class reconciliation contract.
#
#   check-handoff-packet.sh <packet-file> [--repo-root <dir>]
#     [--receiver-requires-reproduction]
#
# The packet is a small key: value document. Recognized keys:
#   packet_id, packet_version, packet_content_hash, sender_run_id,
#   subject_repo, claimed_tree, claimed_branch, claimed_clean (yes|no),
#   owner_acceptance (free text; Class-3, preserved verbatim),
#   has_state_claims (yes|no), handoff_state,
#   implementation_identity_present, frozen_denominator_present,
#   acceptance_oracle_present, reproduction_inputs_present,
#   evaluator_schema_semantics_present, prior_evidence_present,
#   rejected_non_evidence_present, authority_stop_boundaries_present,
#   exact_handoff_receipt_present, current_state_ref, provenance_ref,
#   pending_effects_disposition, authority_capability_ref, discrepancy_state,
#   receiver_live_verification
#   (yes|no; prior/rejected may be not-applicable)
#
# Exit 0 = accept/proceed (with a one-line verification note or a
# "nothing mechanical to verify" note). Exit 1 = contradicted or unverifiable Class-1
# claim: a named abnormality is emitted and dependent execution BLOCKS.
# Class-3 owner authorization is always echoed verbatim, never recomputed.

fail() { printf 'check-handoff-packet: %s\n' "$*" >&2; exit 1; }

unverifiable() {
  printf 'check-handoff-packet: UNVERIFIABLE Class-1 claim: %s (Git observation failed)\n' "$1" >&2
  fail "abnormality class evidence-mismatch — receiver re-derivation unavailable; dependent execution BLOCKS until acknowledged (audit NOT restarted)"
}

pkt="${1:-}"
[ -f "$pkt" ] || fail "packet file not found: ${pkt:-<none>}"
shift
repo_root="."
receiver_requires_reproduction=no
while [ "$#" -gt 0 ]; do
  case "$1" in
    --repo-root)
      [ "$#" -ge 2 ] || fail "--repo-root requires a directory"
      repo_root="$2"
      shift 2
      ;;
    --receiver-requires-reproduction)
      receiver_requires_reproduction=yes
      shift
      ;;
    *) fail "unknown argument: $1" ;;
  esac
done

# Capture once before parsing: a later replacement of the supplied pathname
# must not substitute fields after their content hash has been verified. Bash
# read preserves trailing newlines; NUL is a delimiter and is refused rather
# than silently discarded. This small text format is bounded at 1 MiB.
packet_bytes=""
capture_packet() {
  local LC_ALL=C
  if IFS= read -r -d '' -n 1048577 packet_bytes < "$pkt"; then
    [ "${#packet_bytes}" -le 1048576 ] || fail "packet exceeds 1 MiB text limit"
    fail "malformed packet: NUL bytes are not permitted"
  fi
  [ -n "$packet_bytes" ] || fail "packet is empty or unreadable"
}
capture_packet

# Optional fields may be absent; keep grep's no-match from aborting under
# `set -euo pipefail` and skipping the checks below.
get() { { printf '%s' "$packet_bytes" | grep -iE "^$1:" || true; } | head -n1 | sed $'s/^[^:]*: *//;s/\r$//'; }

# Exclude the hash field's complete physical line without adding/removing any
# other LF/CRLF bytes or manufacturing a newline for an unterminated last line.
packet_hash_body() {
  local line ending
  while :; do
    line=""
    if IFS= read -r line; then ending=$'\n'; else ending=""; fi
    [ -n "$line$ending" ] || break
    case "${line,,}" in
      packet_content_hash:*) : ;;
      *) printf '%s%s' "$line" "$ending" ;;
    esac
    [ -n "$ending" ] || break
  done
}

# Repeated keys are a malformed packet, never a silent first-wins: a
# second conflicting `claimed_branch:` (or any recognized key) could
# smuggle a contradiction past the comparison (Fable review of PR #30).
for k in packet_id packet_version packet_content_hash sender_run_id \
         subject_repo claimed_tree claimed_branch claimed_clean \
         owner_acceptance has_state_claims handoff_state \
         implementation_identity_present frozen_denominator_present \
         acceptance_oracle_present reproduction_inputs_present \
         evaluator_schema_semantics_present prior_evidence_present \
         rejected_non_evidence_present authority_stop_boundaries_present \
         exact_handoff_receipt_present current_state_ref provenance_ref \
         pending_effects_disposition authority_capability_ref \
         discrepancy_state receiver_live_verification; do
  n="$({ printf '%s' "$packet_bytes" | grep -ciE "^$k:" || true; })"
  if [ "${n:-0}" -gt 1 ]; then
    fail "malformed packet: key '$k' appears $n times — one value per key"
  fi
done

# Packet identity is required.
for k in packet_id packet_version packet_content_hash sender_run_id; do
  [ -n "$(get "$k")" ] || fail "packet missing required identity field: $k"
done

# Content-hash binding: when packet_content_hash is a sha256 (64 hex), it
# is RECOMPUTED over the packet bytes minus the packet_content_hash line
# — this is what makes identity and the verbatim Class-3 text tamper-
# evident (a rewritten authorization breaks the hash). A non-sha256 token
# cannot be verified and is said so out loud, never silently trusted
# (Fable review of PR #30).
phash="$(get packet_content_hash)"
packet_hash_verified=no
if printf '%s' "$phash" | grep -qiE '^[0-9a-f]{64}$'; then
  if command -v sha256sum >/dev/null 2>&1; then hasher="sha256sum";
  elif command -v shasum >/dev/null 2>&1; then hasher="shasum -a 256";
  else hasher=""; fi
  if [ -n "$hasher" ]; then
    live_hash="$(printf '%s' "$packet_bytes" | packet_hash_body | $hasher | cut -d' ' -f1)"
    if [ "${phash,,}" != "$live_hash" ]; then
      fail "packet content hash mismatch (claimed $phash, recomputed $live_hash) — packet identity or Class-3 content was altered after issue"
    fi
    packet_hash_verified=yes
  else
    printf 'check-handoff-packet: content hash not verifiable (no sha256 tool on host)\n'
  fi
else
  printf 'check-handoff-packet: content hash not verifiable (non-sha256 token) — identity binding rests on the issuer\n'
fi

# Class 3 (owner/authorization) is preserved verbatim, regardless of any
# Class-1 mismatch below.
owner="$(get owner_acceptance)"
[ -n "$owner" ] && printf 'check-handoff-packet: Class-3 preserved verbatim: %s\n' "$owner"

# Receiver-relative READY boundary (R001F). The receiving continuation, not the
# sender, decides whether independent reproduction is required. In that mode a
# terminal handoff is incomplete unless its immutable implementation and
# acceptance-state bundle is explicitly carried. Ordinary implementation-only
# handoffs preserve the no-bundle cheap path.
if [ "$receiver_requires_reproduction" = yes ]; then
  handoff_state="$(get handoff_state)"
  [ "${handoff_state^^}" = READY ] || \
    fail "RECEIVER_INCOMPLETE: reproduction-required handoff is not terminal READY"
  missing=""
  for k in implementation_identity_present frozen_denominator_present \
           acceptance_oracle_present reproduction_inputs_present \
           evaluator_schema_semantics_present authority_stop_boundaries_present \
           exact_handoff_receipt_present; do
    value="$(get "$k")"
    [ "${value,,}" = yes ] || missing="$missing $k"
  done
  for k in current_state_ref provenance_ref pending_effects_disposition \
           authority_capability_ref discrepancy_state \
           receiver_live_verification; do
    value="$(get "$k" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')"
    case "${value,,}" in
      ''|yes|no|true|false|present|absent|unknown) missing="$missing $k" ;;
    esac
  done
  for k in prior_evidence_present rejected_non_evidence_present; do
    value="$(get "$k")"
    case "${value,,}" in
      yes|not-applicable) : ;;
      *) missing="$missing $k" ;;
    esac
  done
  [ -z "$missing" ] || \
    fail "RECEIVER_INCOMPLETE: READY handoff lacks receiver-required acceptance state:$missing"
fi

# Resolve only the receiver-required current-state identity. Other acceptance
# semantics and Class-3 authority remain receiver obligations, never commands
# to evaluate. Keep the historical claimed_tree key's HEAD-commit meaning.
verify_receiver_reference() {
  [ "$receiver_requires_reproduction" = yes ] || return 0
  [ "$packet_hash_verified" = yes ] || \
    fail "RECEIVER_INCOMPLETE: reproduction requires a verified SHA-256 packet binding"
  local claimed_commit current_ref live_commit provenance
  claimed_commit="$(get claimed_tree)"
  printf '%s' "$claimed_commit" | grep -qiE '^[0-9a-f]{40}$' || \
    fail "RECEIVER_INCOMPLETE: current_state_ref requires a full claimed_tree commit identity"
  current_ref="$(get current_state_ref)"
  case "$current_ref" in
    git:HEAD) : ;;
    git:*)
      [ "${current_ref,,}" = "git:${claimed_commit,,}" ] || \
        fail "RECEIVER_INCOMPLETE: current_state_ref must name the exact claimed commit"
      ;;
    file:*)
      command -v python3 >/dev/null 2>&1 || \
        fail "RECEIVER_INCOMPLETE: safe file reference verification requires python3"
      python3 - "$repo_root" "$current_ref" <<'PY'
import hashlib
import os
import re
import stat
import sys

directories = []

def identity(info):
    return info.st_dev, info.st_ino, info.st_mode

def file_identity(info):
    return identity(info) + (info.st_size, info.st_mtime_ns, info.st_ctime_ns)

try:
    match = re.fullmatch(r"file:(.+)#sha256=([0-9a-fA-F]{64})", sys.argv[2])
    if match is None:
        raise ValueError("file reference needs a SHA-256 binding")
    parts = match[1].split("/")
    if any(part in ("", ".", "..") for part in parts):
        raise ValueError("file reference must stay beneath the receiver root")
    # Open each component relative to an already opened directory. No symlink
    # check/open race, path traversal, device/FIFO read, or command evaluation.
    if (os.open not in os.supports_dir_fd or
            os.stat not in os.supports_dir_fd or
            os.stat not in os.supports_follow_symlinks):
        raise NotImplementedError("host cannot safely open and re-stat relative paths")
    directory_flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
    directory = os.open(sys.argv[1], directory_flags)
    directories.append((None, sys.argv[1], directory))
    for part in parts[:-1]:
        child = os.open(part, directory_flags, dir_fd=directory)
        directories.append((directory, part, child))
        directory = child
    fd = os.open(parts[-1], os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK,
                 dir_fd=directory)
    with os.fdopen(fd, "rb") as state:
        before = os.fstat(state.fileno())
        if not stat.S_ISREG(before.st_mode):
            raise ValueError("current state must be a regular file")
        digest = hashlib.sha256()
        for chunk in iter(lambda: state.read(1024 * 1024), b""):
            digest.update(chunk)
        after = os.fstat(state.fileno())
        if file_identity(before) != file_identity(after):
            raise ValueError("current state changed during verification")
        if digest.hexdigest() != match[2].lower():
            raise ValueError("current state digest mismatch")
        # An open descriptor survives renaming. Recheck the live file and its
        # whole naming chain while retaining the captured descriptors, so a
        # replaced file, parent, or receiver root cannot validate old bytes.
        named = os.stat(parts[-1], dir_fd=directory, follow_symlinks=False)
        if file_identity(named) != file_identity(after):
            raise ValueError("current state path no longer names captured bytes")
        for parent, name, opened in reversed(directories):
            named = os.stat(name, dir_fd=parent, follow_symlinks=False)
            if identity(named) != identity(os.fstat(opened)):
                raise ValueError("current state naming chain changed")
        if file_identity(os.fstat(state.fileno())) != file_identity(after):
            raise ValueError("current state changed during final identity check")
except (AttributeError, NotImplementedError):
    print("check-handoff-packet: RECEIVER_INCOMPLETE: safe file reference "
          "verification is unavailable on this host", file=sys.stderr)
    sys.exit(1)
except (OSError, ValueError):
    print("check-handoff-packet: RECEIVER_INCOMPLETE: current_state_ref is "
          "missing, unsafe, changed, or digest-mismatched", file=sys.stderr)
    sys.exit(1)
finally:
    for _, _, directory in reversed(directories):
        os.close(directory)
PY
      ;;
    *) fail "RECEIVER_INCOMPLETE: unsupported or unbound current_state_ref" ;;
  esac
  live_commit="$(git -C "$repo_root" rev-parse --verify HEAD 2>/dev/null)" || \
    fail "RECEIVER_INCOMPLETE: current repository commit is unavailable"
  [ "${claimed_commit,,}" = "$live_commit" ] || \
    fail "RECEIVER_INCOMPLETE: current_state_ref commit is stale"
  provenance="$(get provenance_ref)"
  case "$provenance" in
    packet:*)
      [ "$provenance" = "packet:$(get packet_id)" ] || \
        fail "RECEIVER_INCOMPLETE: provenance_ref names a different packet"
      ;;
  esac
  printf 'check-handoff-packet: RECEIVER_ACCEPTANCE_STATE=COMPLETE — current-state identity verified; semantic/authority acceptance remains receiver-owned\n'
}

has_claims="$(get has_state_claims)"
# A sender's denial cannot erase a populated Class-1 claim. Only a genuinely
# empty claim population may skip the existing live comparisons below.
if [ "${has_claims,,}" = "no" ] &&
   [ -z "$(get subject_repo)$(get claimed_branch)$(get claimed_tree)$(get claimed_clean)" ]; then
  verify_receiver_reference
  printf 'check-handoff-packet: nothing mechanical to verify (no Class-1 state claims)\n'
  exit 0
fi

# Class 1: recompute continuation-critical state and compare.
contradicted=0
note=""

claimed_repo="$(get subject_repo)"
if [ -n "$claimed_repo" ]; then
  live_repo="$(git -C "$repo_root" rev-parse --show-toplevel 2>/dev/null)" || unverifiable subject_repo
  live_repo="$(basename "$live_repo")"
  case "$claimed_repo" in
    */"$live_repo"|"$live_repo") : ;;
    *) contradicted=1; note="$note subject_repo(claimed=$claimed_repo live=$live_repo)";;
  esac
fi

claimed_branch="$(get claimed_branch)"
if [ -n "$claimed_branch" ]; then
  live_branch="$(git -C "$repo_root" rev-parse --abbrev-ref HEAD 2>/dev/null)" || unverifiable claimed_branch
  [ "$claimed_branch" = "$live_branch" ] || { contradicted=1; note="$note branch(claimed=$claimed_branch live=$live_branch)"; }
fi

claimed_tree="$(get claimed_tree)"
if [ -n "$claimed_tree" ]; then
  # Full-SHA equality only: a prefix (even 39 chars) is never confirmed
  # tree identity — short tokens are display, not authority (#4; Fable
  # review of PR #30 found a 4-char prefix was accepted).
  if ! printf '%s' "$claimed_tree" | grep -qiE '^[0-9a-f]{40}$'; then
    contradicted=1; note="$note tree(claimed=$claimed_tree — not a full 40-hex SHA; short identity is never confirmed)"
  else
    live_tree="$(git -C "$repo_root" rev-parse HEAD 2>/dev/null)" || unverifiable claimed_tree
    if [ "${claimed_tree,,}" != "$live_tree" ]; then
      contradicted=1; note="$note tree(claimed=$claimed_tree live=$live_tree)"
    fi
  fi
fi

claimed_clean="$(get claimed_clean)"
if [ -n "$claimed_clean" ]; then
  live_status="$(git -C "$repo_root" status --porcelain 2>/dev/null)" || unverifiable claimed_clean
  if [ -z "$live_status" ]; then live_clean=yes; else live_clean=no; fi
  [ "${claimed_clean,,}" = "$live_clean" ] || { contradicted=1; note="$note clean(claimed=$claimed_clean live=$live_clean)"; }
fi

if [ "$contradicted" -eq 1 ]; then
  printf 'check-handoff-packet: CONTRADICTED Class-1 claim(s):%s\n' "$note" >&2
  printf 'check-handoff-packet: abnormality class evidence-mismatch — receiver re-derivation WINS; dependent execution BLOCKS until acknowledged (audit NOT restarted)\n' >&2
  exit 1
fi

verify_receiver_reference
printf 'check-handoff-packet: verified — Class-1 claims confirmed against live state; proceed\n'
