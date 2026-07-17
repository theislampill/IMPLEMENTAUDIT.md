#!/usr/bin/env bash
set -euo pipefail

# Receiving-side handoff inspection (#15): PROTOCOL contract text + the
# four acceptance fixtures (contradicted-blocks, matching-proceeds,
# owner-acceptance-carried, no-claims negative control). The matching
# fixture is generated against the LIVE repo so the recompute path is
# exercised for real.

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

proto="skills/implementaudit/templates/PROTOCOL.md"
scorer="skills/implementaudit/scripts/check-handoff-packet.sh"
fx="fixtures/handoff-packet"
fail() { printf 'handoff-packet-contract: %s\n' "$*" >&2; exit 1; }

flat="$(tr '\n' ' ' < "$proto")"
printf '%s' "$flat" | grep -qi 'Receiving-side handoff inspection' \
  || fail "PROTOCOL missing receiving-side handoff inspection section"
printf '%s' "$flat" | grep -qi 'Three claim classes' \
  || fail "three claim classes missing"
printf '%s' "$flat" | grep -qi 'PRESERVED verbatim' \
  || fail "Class-3 verbatim preservation missing"
printf '%s' "$flat" | grep -qi 'BLOCKS ONLY.*DEPENDENT EXECUTION' \
  || fail "block-only-dependent-execution rule missing"

# A. contradicted claim blocks + names abnormality + carries owner verbatim
out="$(bash "$scorer" "$fx/contradicted.pkt" --repo-root "$repo_root" 2>&1 || true)"
printf '%s' "$out" | grep -q 'CONTRADICTED' || fail "contradicted packet did not block"
printf '%s' "$out" | grep -q 'evidence-mismatch' || fail "no named abnormality"
printf '%s' "$out" | grep -qi 'Class-3 preserved verbatim' \
  || fail "owner acceptance not carried verbatim through a mismatch"
if bash "$scorer" "$fx/contradicted.pkt" --repo-root "$repo_root" >/dev/null 2>&1; then
  fail "contradicted packet must exit nonzero (block)"
fi

# D. no state claims -> nothing to verify, proceed
bash "$scorer" "$fx/no-claims.pkt" --repo-root "$repo_root" >/dev/null 2>&1 \
  || fail "no-claims packet must proceed"

# B. matching claims -> proceed. Generate a packet from LIVE state.
tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT
live_repo="$(basename "$(git -C "$repo_root" rev-parse --show-toplevel)")"
live_branch="$(git -C "$repo_root" rev-parse --abbrev-ref HEAD)"
live_tree="$(git -C "$repo_root" rev-parse HEAD)"
if [ -z "$(git -C "$repo_root" status --porcelain)" ]; then live_clean=yes; else live_clean=no; fi
cat > "$tmp/match.pkt" <<EOF
packet_id: pkt-live
packet_version: 1
packet_content_hash: livehash
sender_run_id: run-sender-B
subject_repo: $live_repo
claimed_branch: $live_branch
claimed_tree: $live_tree
claimed_clean: $live_clean
has_state_claims: yes
owner_acceptance: none
EOF
bash "$scorer" "$tmp/match.pkt" --repo-root "$repo_root" >/dev/null 2>&1 \
  || fail "matching packet must proceed against live state"

printf 'handoff-packet-contract: ok (contract + contradicted/matching/owner/no-claims)\n'
