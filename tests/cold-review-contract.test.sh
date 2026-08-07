#!/usr/bin/env bash
set -euo pipefail

# Cold-review contract test (#51, IA-ACTION-COLD-REVIEW): runs the checker
# on the live repo, then proves it fails on mutated copies (embedded
# negative controls).

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

fail() {
  printf 'cold-review-contract.test: %s\n' "$*" >&2
  exit 1
}

# 1. Positive: live repo passes.
bash scripts/check-cold-review-contract.sh \
  || fail "checker fails on the live repo"

# #86: the source-repo checker classifies the seven review-integrity cases.
for positive in \
  issue-86-attested-pass.md \
  issue-86-altered-packet-respawn.md \
  issue-86-runtime-non-verdict-replacement.md \
  issue-86-reviewer-selfcorrected-probe.md \
  issue-86-transient-channel-respawn.md
do
  bash scripts/check-cold-review-contract.sh \
    --fixture "fixtures/cold-review/$positive" >/dev/null 2>&1 \
    || fail "#86 positive fixture rejected: $positive"
done
for negative in \
  issue-86-negative-self-review-labeled.md \
  issue-86-negative-deterministic-respawn.md
do
  if bash scripts/check-cold-review-contract.sh \
    --fixture "fixtures/cold-review/$negative" >/dev/null 2>&1; then
    fail "#86 negative fixture false-greened: $negative"
  fi
done

# The same classifier is callable over an actual run-root packet directory;
# it must not be limited to repository fixture filenames.
successor_root="$(mktemp -d)"
write_transport_state() {
  local root="$1"
  cat > "$root/STATE.md" <<'EOF'
# State

## Andon log

| # | Occ | Phase | Class | Abnormality |
|---|---|---|---|---|
| 1 | o1 | 6 | transport-infrastructure | reviewer transport failure |
EOF
}
cp fixtures/cold-review/independent-review-confirms-handoff.md \
  fixtures/cold-review/projection-index-derivative.md \
  "$successor_root/"
write_transport_state "$successor_root"
cp fixtures/cold-review/issue-86-negative-deterministic-respawn.md \
  "$successor_root/packet-a.md"
if bash scripts/check-cold-review-contract.sh --run-root "$successor_root" \
  >/dev/null 2>&1; then
  fail "#86 run-root mode false-greened deterministic unaltered respawn"
fi
rm "$successor_root/packet-a.md"
cp fixtures/cold-review/issue-86-altered-packet-respawn.md \
  "$successor_root/packet-b.md"
bash scripts/check-cold-review-contract.sh --run-root "$successor_root" \
  >/dev/null 2>&1 || fail "#86 run-root mode rejected recorded packet alteration"
sed -i 's/2f4c3d54a95c60e8ad90dbf84ce5cb009258a10eaeaf4c0aad9d228791962138/0f4c3d54a95c60e8ad90dbf84ce5cb009258a10eaeaf4c0aad9d228791962138/' \
  "$successor_root/packet-b.md"
if bash scripts/check-cold-review-contract.sh --run-root "$successor_root" \
  >/dev/null 2>&1; then
  fail "#86 run-root mode accepted caller-fabricated packet digest"
fi
rm "$successor_root/packet-b.md"
cp fixtures/cold-review/issue-86-runtime-non-verdict-replacement.md \
  "$successor_root/issue-86-runtime-non-verdict-replacement.md"
bash scripts/check-cold-review-contract.sh --run-root "$successor_root" \
  >/dev/null 2>&1 || fail "#86 run-root mode rejected carried provisional findings"
sed -i 's|provisional_findings_carried: issue-86-runtime-non-verdict-replacement.md#finding-a|provisional_findings_carried: none|' \
  "$successor_root/issue-86-runtime-non-verdict-replacement.md"
if bash scripts/check-cold-review-contract.sh --run-root "$successor_root" \
  >/dev/null 2>&1; then
  fail "#86 run-root mode accepted dropped provisional findings"
fi

expect_issue86_runroot_fail() {
  local root="$1" expected="$2" label="$3" output
  output="$(bash scripts/check-cold-review-contract.sh --run-root "$root" 2>&1)" && {
    printf '%s\n' "$output" >&2
    fail "$label unexpectedly passed"
  }
  grep -Fq "$expected" <<<"$output" || {
    printf '%s\n' "$output" >&2
    fail "$label failed for the wrong reason"
  }
}

# Reviewer finding F3: origin-detail relabeling cannot split one resolved
# predecessor occurrence, and the cited occurrence must be a real transport
# Andon row.
rm -f "$successor_root"/*.md
cp fixtures/cold-review/independent-review-confirms-handoff.md \
  fixtures/cold-review/issue-86-negative-deterministic-respawn.md \
  "$successor_root/"
write_transport_state "$successor_root"
expect_issue86_runroot_fail "$successor_root" \
  "content-deterministic refusal cannot respawn a materially unaltered packet" \
  "single unaltered deterministic successor"
sed -i '/| 1 | o1 | 6 | transport-infrastructure |/d' \
  "$successor_root/STATE.md"
cat > "$successor_root/unrelated-not-andon-log.md" <<'EOF'
| Occ | Class |
|---|---|
| o1 | transport-infrastructure |
EOF
expect_issue86_runroot_fail "$successor_root" \
  "predecessor_occurrence must resolve to a transport-infrastructure Andon row" \
  "missing Andon occurrence"
rm "$successor_root/issue-86-negative-deterministic-respawn.md"
cp fixtures/cold-review/issue-86-transient-channel-respawn.md \
  "$successor_root/issue-86-transient-channel-respawn.md"
write_transport_state "$successor_root"
sed -i '0,/failure_determinism: transient/! s/failure_determinism: transient/failure_determinism: content-deterministic/' \
  "$successor_root/issue-86-transient-channel-respawn.md"
expect_issue86_runroot_fail "$successor_root" \
  "one predecessor occurrence cannot change failure_determinism" \
  "determinism relabeling"
cp fixtures/cold-review/issue-86-transient-channel-respawn.md \
  "$successor_root/issue-86-transient-channel-respawn.md"
sed -i 's/successor-review: attempt: 2 /successor-review: attempt: 3 /' \
  "$successor_root/issue-86-transient-channel-respawn.md"
expect_issue86_runroot_fail "$successor_root" \
  "successor attempts must be contiguous from 1" \
  "successor attempt gap"

# Reviewer finding F4: raw byte churn outside the exact review-packet-scope row
# is not a material retry. The existing positive fixture proves a strict scope
# narrowing plus inline-to-reference transition remains accepted.
for noise_case in whitespace-only metadata-only unrelated-section; do
  rm -f "$successor_root"/*.md
  write_transport_state "$successor_root"
  printf '%s\n' \
    'review-packet-scope: scope: phase-spec,owner-authority | technique: cold-read | evidence_mode: inline' \
    > "$successor_root/packet-a.md"
  cp "$successor_root/packet-a.md" "$successor_root/packet-b.md"
  case "$noise_case" in
    whitespace-only) printf '\n\n' >> "$successor_root/packet-b.md" ;;
    metadata-only) printf '\nMetadata: changed\n' >> "$successor_root/packet-b.md" ;;
    unrelated-section) printf '\n## Unrelated section\nnot reviewer scope\n' >> "$successor_root/packet-b.md" ;;
  esac
  hash_a="$(sha256sum "$successor_root/packet-a.md" | awk '{print $1}')"
  hash_b="$(sha256sum "$successor_root/packet-b.md" | awk '{print $1}')"
  cat > "$successor_root/retry.md" <<EOF
| # | Occ | Phase | Class | Abnormality |
|---|---|---|---|---|
| 1 | o1 | 6 | transport-infrastructure | deterministic refusal |
successor-review: attempt: 1 | predecessor_failure_origin: transport-infrastructure | failure_determinism: content-deterministic | origin_detail: provider-policy | predecessor_occurrence: o1 | predecessor_packet_scope_file: packet-a.md | predecessor_packet_scope_sha256: $hash_a | packet_scope_file: packet-b.md | packet_scope_sha256: $hash_b | packet_alteration: technique-reworded | andon_class: transport-infrastructure | provisional_findings_carried: none
EOF
  expect_issue86_runroot_fail "$successor_root" \
    "content-deterministic refusal cannot respawn a materially unaltered packet" \
    "$noise_case packet alteration"
done

# Reviewer finding F5: non-verdict enums, occurrence identity, and contained
# provisional-finding anchors are all machine-bound.
rm -f "$successor_root"/*.md
cp fixtures/cold-review/independent-review-confirms-handoff.md \
  fixtures/cold-review/issue-86-runtime-non-verdict-replacement.md \
  "$successor_root/"
write_transport_state "$successor_root"
sed -i '0,/predecessor_failure_origin: transport-infrastructure/s//predecessor_failure_origin: invented-class/' \
  "$successor_root/issue-86-runtime-non-verdict-replacement.md"
expect_issue86_runroot_fail "$successor_root" \
  "runtime non-verdict must reuse transport-infrastructure" \
  "invented non-verdict origin"
cp fixtures/cold-review/issue-86-runtime-non-verdict-replacement.md \
  "$successor_root/issue-86-runtime-non-verdict-replacement.md"
sed -i '0,/failure_determinism: transient/s//failure_determinism: invented/' \
  "$successor_root/issue-86-runtime-non-verdict-replacement.md"
expect_issue86_runroot_fail "$successor_root" \
  "runtime non-verdict failure_determinism is invalid" \
  "invented non-verdict determinism"
cp fixtures/cold-review/issue-86-runtime-non-verdict-replacement.md \
  "$successor_root/issue-86-runtime-non-verdict-replacement.md"
sed -i 's/#finding-a/#missing-finding/g' \
  "$successor_root/issue-86-runtime-non-verdict-replacement.md"
expect_issue86_runroot_fail "$successor_root" \
  "provisional finding reference does not resolve to a contained heading" \
  "dangling provisional finding"
cp fixtures/cold-review/issue-86-runtime-non-verdict-replacement.md \
  "$successor_root/issue-86-runtime-non-verdict-replacement.md"
sed -i '/finding-record: id: finding-a | status: provisional/d' \
  "$successor_root/issue-86-runtime-non-verdict-replacement.md"
expect_issue86_runroot_fail "$successor_root" \
  "provisional finding reference does not resolve to an exact finding-record" \
  "ordinary heading presented as a finding"
cp fixtures/cold-review/issue-86-runtime-non-verdict-replacement.md \
  "$successor_root/issue-86-runtime-non-verdict-replacement.md"
sed -i '/| 1 | o1 | 6 | transport-infrastructure |/a\| 2 | o2 | 6 | transport-infrastructure | replacement incident |' \
  "$successor_root/STATE.md"
sed -i '0,/predecessor_occurrence: o1/! s/predecessor_occurrence: o1/predecessor_occurrence: o2/' \
  "$successor_root/issue-86-runtime-non-verdict-replacement.md"
expect_issue86_runroot_fail "$successor_root" \
  "replacement packet did not carry the provisional findings" \
  "cross-predecessor finding carry"
rm -rf "$successor_root"

tmp_root="$(mktemp -d)"
trap 'rm -rf "$tmp_root"' EXIT

reset_sandbox() {
  rm -rf "$tmp_root"
  mkdir -p \
    "$tmp_root/skills/implementaudit/references" \
    "$tmp_root/skills/implementaudit/templates" \
    "$tmp_root/fixtures/cold-review" \
    "$tmp_root/fixtures/audit-object-routing"
  cp skills/implementaudit/SKILL.md "$tmp_root/skills/implementaudit/"
  cp skills/implementaudit/references/planning-depth.md \
    skills/implementaudit/references/plan-lifecycle.md \
    skills/implementaudit/references/child-agents.md \
    skills/implementaudit/references/transcript-contract.md \
    "$tmp_root/skills/implementaudit/references/"
  cp skills/implementaudit/templates/ROADMAP.md \
    skills/implementaudit/templates/THINKING.md \
    skills/implementaudit/templates/child-agent-report.md \
    "$tmp_root/skills/implementaudit/templates/"
  cp fixtures/cold-review/*.md "$tmp_root/fixtures/cold-review/"
  cp fixtures/audit-object-routing/plan-lifecycle.md \
    "$tmp_root/fixtures/audit-object-routing/"
}

expect_fail() {
  local label="$1"
  if bash scripts/check-cold-review-contract.sh --repo-root "$tmp_root" \
    >/dev/null 2>&1; then
    fail "negative control not detected: $label"
  fi
}

# 2. Sanity: untouched sandbox passes.
reset_sandbox
bash scripts/check-cold-review-contract.sh --repo-root "$tmp_root" \
  >/dev/null 2>&1 || fail "checker fails on the untouched sandbox copy"

# 3. Stage 6.2 removed from the stage map -> must fail.
reset_sandbox
sed 's/^### Stage 6.2 - Independent cold review$/### Stage 6.2 - Removed/' \
  "$tmp_root/skills/implementaudit/SKILL.md" >"$tmp_root/skill.tmp"
mv "$tmp_root/skill.tmp" "$tmp_root/skills/implementaudit/SKILL.md"
expect_fail "SKILL.md without Stage 6.2"

# 4. Readiness gate clause removed from plan-lifecycle -> must fail.
reset_sandbox
grep -v "without a recorded disposition" \
  "$tmp_root/skills/implementaudit/references/plan-lifecycle.md" \
  >"$tmp_root/plan-lifecycle.tmp"
mv "$tmp_root/plan-lifecycle.tmp" \
  "$tmp_root/skills/implementaudit/references/plan-lifecycle.md"
expect_fail "plan-lifecycle.md without the readiness gate"

# 5. Projection loses its derivative statement -> must fail.
reset_sandbox
sed 's/derivative, never canonical/authoritative/' \
  "$tmp_root/skills/implementaudit/templates/ROADMAP.md" \
  >"$tmp_root/roadmap.tmp"
mv "$tmp_root/roadmap.tmp" "$tmp_root/skills/implementaudit/templates/ROADMAP.md"
expect_fail "ROADMAP.md without the derivative-projection statement"

# 6. A negative fixture disappears -> must fail.
reset_sandbox
rm "$tmp_root/fixtures/cold-review/negative-same-context-review.md"
expect_fail "missing negative-same-context-review fixture"

# 7. Command-mode advertisement in a cold-review fixture -> must fail.
reset_sandbox
printf '\nAdvertised mode: /implementaudit review-plan\n' \
  >>"$tmp_root/fixtures/cold-review/independent-review-confirms-handoff.md"
expect_fail "command-mode advertisement in a cold-review fixture"

printf 'cold-review-contract.test: ok\n'
