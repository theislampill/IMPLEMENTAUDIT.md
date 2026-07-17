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

# E. ADVERSARIAL (post-merge robustness): a packet with only the required
# identity fields + a contradicted subject_repo, and NO optional fields
# (owner_acceptance, branch, tree, clean) must STILL reach the Class-1
# contradiction logic and NAME the abnormality — not die early on an
# absent-field lookup under `set -euo pipefail`.
cat > "$tmp/min-contradicted.pkt" <<EOF
packet_id: pmin
packet_version: 1
packet_content_hash: h
sender_run_id: r
subject_repo: DEFINITELY-NOT-THIS-REPO
has_state_claims: yes
EOF
out="$(bash "$scorer" "$tmp/min-contradicted.pkt" --repo-root "$repo_root" 2>&1 || true)"
printf '%s' "$out" | grep -q 'CONTRADICTED' \
  || fail "minimal contradicted packet did not reach the contradiction logic (early-death regression)"
printf '%s' "$out" | grep -q 'evidence-mismatch' \
  || fail "minimal contradicted packet did not name the abnormality"

# --- Fable review of PR #30: adversarial regressions -----------------------
# F. A claimed_tree PREFIX (even a long one) is never confirmed identity.
cat > "$tmp/prefix.pkt" <<EOF
packet_id: pfx
packet_version: 1
packet_content_hash: h
sender_run_id: r
claimed_tree: ${live_tree:0:7}
has_state_claims: yes
EOF
if bash "$scorer" "$tmp/prefix.pkt" --repo-root "$repo_root" >/dev/null 2>&1; then
  fail "short-prefix claimed_tree was confirmed as tree identity"
fi

# G. Duplicate conflicting keys are a malformed packet, not first-wins.
cat > "$tmp/dup.pkt" <<EOF
packet_id: pdup
packet_version: 1
packet_content_hash: h
sender_run_id: r
claimed_branch: $live_branch
claimed_branch: totally-other-branch
has_state_claims: yes
EOF
out="$(bash "$scorer" "$tmp/dup.pkt" --repo-root "$repo_root" 2>&1 || true)"
printf '%s' "$out" | grep -qi 'malformed packet' \
  || fail "duplicate conflicting keys were not rejected as malformed"

# H. sha256 content hash binds the packet: a correct hash passes; a
# packet altered after issue (tampered Class-3 text) fails the binding.
if command -v sha256sum >/dev/null 2>&1; then
  cat > "$tmp/bound.body" <<EOF
packet_id: pbind
packet_version: 1
sender_run_id: r
owner_acceptance: owner accepted residual risk R1 (verbatim)
has_state_claims: no
EOF
  bh="$(sha256sum "$tmp/bound.body" | cut -d' ' -f1)"
  { head -n1 "$tmp/bound.body"; printf 'packet_content_hash: %s\n' "$bh"; \
    tail -n +2 "$tmp/bound.body"; } > "$tmp/bound.pkt"
  bash "$scorer" "$tmp/bound.pkt" --repo-root "$repo_root" >/dev/null 2>&1 \
    || fail "correctly sha256-bound packet must pass"
  sed 's/residual risk R1/residual risk R1 AND R2/' "$tmp/bound.pkt" \
    > "$tmp/tampered.pkt"
  if bash "$scorer" "$tmp/tampered.pkt" --repo-root "$repo_root" >/dev/null 2>&1; then
    fail "tampered Class-3 text passed a sha256-bound packet"
  fi
fi

# I. Control: an opaque (non-sha256) hash token is still tolerated, with
# the unverifiability said out loud.
out="$(bash "$scorer" "$fx/no-claims.pkt" --repo-root "$repo_root" 2>&1)" \
  || fail "opaque-hash legacy packet must still proceed"
printf '%s' "$out" | grep -qi 'not verifiable' \
  || fail "opaque hash must be reported as not verifiable, not silently trusted"

printf 'handoff-packet-contract: ok (contract + contradicted/matching/owner/no-claims + minimal-fields + 4 Fable adversarial)\n'
