#!/usr/bin/env bash
set -euo pipefail

# Receiving-side handoff packet inspection (#15). Read-only. Verifies a
# packet's mechanically recomputable Class-1 claims against live state and
# enforces the three-class reconciliation contract.
#
#   check-handoff-packet.sh <packet-file> [--repo-root <dir>]
#
# The packet is a small key: value document. Recognized keys:
#   packet_id, packet_version, packet_content_hash, sender_run_id,
#   subject_repo, claimed_tree, claimed_branch, claimed_clean (yes|no),
#   owner_acceptance (free text; Class-3, preserved verbatim),
#   has_state_claims (yes|no)
#
# Exit 0 = accept/proceed (with a one-line verification note or a
# "nothing mechanical to verify" note). Exit 1 = contradicted Class-1
# claim: a named abnormality is emitted and dependent execution BLOCKS.
# Class-3 owner authorization is always echoed verbatim, never recomputed.

fail() { printf 'check-handoff-packet: %s\n' "$*" >&2; exit 1; }

pkt="${1:-}"
[ -f "$pkt" ] || fail "packet file not found: ${pkt:-<none>}"
repo_root="."
if [ "${2:-}" = "--repo-root" ]; then repo_root="${3:-.}"; fi

# Absent fields are normal (most packet fields are optional). grep's
# no-match must NOT abort the script under `set -euo pipefail` — otherwise
# the contradiction/verbatim logic below is silently skipped and the
# checker exits without doing its job. Swallow the no-match to empty.
get() { { grep -iE "^$1:" "$pkt" || true; } | head -n1 | sed "s/^[^:]*: *//" | tr -d '\r'; }

# Repeated keys are a malformed packet, never a silent first-wins: a
# second conflicting `claimed_branch:` (or any recognized key) could
# smuggle a contradiction past the comparison (Fable review of PR #30).
for k in packet_id packet_version packet_content_hash sender_run_id \
         subject_repo claimed_tree claimed_branch claimed_clean \
         owner_acceptance has_state_claims; do
  n="$({ grep -ciE "^$k:" "$pkt" || true; })"
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
if printf '%s' "$phash" | grep -qiE '^[0-9a-f]{64}$'; then
  if command -v sha256sum >/dev/null 2>&1; then hasher="sha256sum";
  elif command -v shasum >/dev/null 2>&1; then hasher="shasum -a 256";
  else hasher=""; fi
  if [ -n "$hasher" ]; then
    live_hash="$({ grep -viE '^packet_content_hash:' "$pkt" || true; } \
      | $hasher | cut -d' ' -f1)"
    if [ "${phash,,}" != "$live_hash" ]; then
      fail "packet content hash mismatch (claimed $phash, recomputed $live_hash) — packet identity or Class-3 content was altered after issue"
    fi
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

has_claims="$(get has_state_claims)"
if [ "${has_claims,,}" = "no" ]; then
  printf 'check-handoff-packet: nothing mechanical to verify (no Class-1 state claims)\n'
  exit 0
fi

# Class 1: recompute continuation-critical state and compare.
contradicted=0
note=""

claimed_repo="$(get subject_repo)"
if [ -n "$claimed_repo" ] && git -C "$repo_root" rev-parse --show-toplevel >/dev/null 2>&1; then
  live_repo="$(basename "$(git -C "$repo_root" rev-parse --show-toplevel)")"
  case "$claimed_repo" in
    */"$live_repo"|"$live_repo") : ;;
    *) contradicted=1; note="$note subject_repo(claimed=$claimed_repo live=$live_repo)";;
  esac
fi

claimed_branch="$(get claimed_branch)"
if [ -n "$claimed_branch" ]; then
  live_branch="$(git -C "$repo_root" rev-parse --abbrev-ref HEAD 2>/dev/null || echo unknown)"
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
    live_tree="$(git -C "$repo_root" rev-parse HEAD 2>/dev/null || echo none)"
    if [ "${claimed_tree,,}" != "$live_tree" ]; then
      contradicted=1; note="$note tree(claimed=$claimed_tree live=$live_tree)"
    fi
  fi
fi

claimed_clean="$(get claimed_clean)"
if [ -n "$claimed_clean" ]; then
  if [ -z "$(git -C "$repo_root" status --porcelain 2>/dev/null)" ]; then live_clean=yes; else live_clean=no; fi
  [ "${claimed_clean,,}" = "$live_clean" ] || { contradicted=1; note="$note clean(claimed=$claimed_clean live=$live_clean)"; }
fi

if [ "$contradicted" -eq 1 ]; then
  printf 'check-handoff-packet: CONTRADICTED Class-1 claim(s):%s\n' "$note" >&2
  printf 'check-handoff-packet: abnormality class evidence-mismatch — receiver re-derivation WINS; dependent execution BLOCKS until acknowledged (audit NOT restarted)\n' >&2
  exit 1
fi

printf 'check-handoff-packet: verified — Class-1 claims confirmed against live state; proceed\n'
