#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

tmp_parent="$(mktemp -d)"
stray_file="skills/implementaudit/zz-package-parity-stray-test.txt"
trap 'rm -rf "$tmp_parent"; rm -f "$stray_file"' EXIT

if [ "${1:-}" = "--identity-only" ]; then
  fail() { printf 'release-asset.test: %s\n' "$*" >&2; exit 1; }
  canonical_receipt='fixtures/release-identity/current-public-v0.3.3.3.json'
  [ -f "$canonical_receipt" ] \
    || fail 'canonical current-public receipt is absent from the real worktree'
  git show "HEAD^:$canonical_receipt" > "$tmp_parent/parent-current-public-receipt.json" \
    || fail 'canonical current-public receipt is absent from the real first parent'
  git show "HEAD:$canonical_receipt" > "$tmp_parent/head-current-public-receipt.json" \
    || fail 'canonical current-public receipt is absent from the real HEAD'
  cmp -s "$tmp_parent/parent-current-public-receipt.json" "$canonical_receipt" \
    || fail 'canonical current-public receipt differs between first parent and worktree'
  cmp -s "$tmp_parent/head-current-public-receipt.json" "$canonical_receipt" \
    || fail 'canonical current-public receipt differs between HEAD and worktree'
  grep -Fq -- '--check-release-identity' scripts/build-release-asset.sh \
    || fail 'release-identity checker mode is missing'
  grep -Fq -- '--check-stale-artifact' scripts/build-release-asset.sh \
    || fail 'stale-artifact checker mode is missing'
  a_digest='aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
  b_digest='bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb'

  write_public_receipt() {
    local path="$1" tag="$2" digest="$3" bytes="$4" release_id="$5" asset_id="$6"
    printf '%s\n' \
      '{' \
      '  "schema_version": 1,' \
      '  "kind": "implementaudit-public-release-asset-readback",' \
      "  \"release_tag\": \"$tag\"," \
      "  \"release_id\": $release_id," \
      '  "asset_name": "IMPLEMENTAUDIT.skill",' \
      "  \"asset_id\": $asset_id," \
      "  \"api_bytes\": $bytes," \
      "  \"api_digest\": \"sha256:$digest\"," \
      "  \"download_bytes\": $bytes," \
      "  \"download_sha256\": \"$digest\"" \
      '}' > "$path"
  }

  make_fixture() {
    local root="$1" version="$2" previous_tag="${3:-v0.3.2.0}"
    mkdir -p "$root/.claude-plugin" "$root/skills/implementaudit"
    printf '{"version":"%s"}\n' "$version" > "$root/.claude-plugin/plugin.json"
    printf '%s\n' '---' 'metadata:' "  version: \"$version\"" '---' > "$root/skills/implementaudit/SKILL.md"
    printf '# Changelog\n\n## [%s] - 2026-07-18\n' "$previous_tag" > "$root/CHANGELOG.md"
    printf 'original payload\n' > "$root/payload.txt"
    printf 'original package\n' > "$root/IMPLEMENTAUDIT.skill"
    git -C "$root" init -q
    git -C "$root" config user.email t@example.invalid
    git -C "$root" config user.name t
    git -C "$root" add .
    git -C "$root" -c user.email=t@example.invalid -c user.name=t commit -qm initial
  }

  make_family_forward_fixture() {
    local root="$1" runtime_version="$2" previous_tag="$3" candidate_tag="$4"
    local site_milestone="${5:-$candidate_tag}"
    local ledger_milestone="${6:-$site_milestone}"
    local ledger_name="${7:-${ledger_milestone}-release-report.md}"
    make_fixture "$root" "$runtime_version" "$previous_tag"
    mkdir -p "$root/docs/portal"
    printf '{"release":{"milestone":"%s","audit_ledger_url":"https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/main/docs/audits/archive/%s"}}\n' \
      "$site_milestone" "$ledger_name" > "$root/docs/portal/site.json"
    printf 'changed payload\n' > "$root/payload.txt"
    {
      printf '# Changelog\n\n## [%s] - 2026-08-10\n- Corrective and completion release.\n\n' "$candidate_tag"
      tail -n +3 "$root/CHANGELOG.md"
    } > "$root/CHANGELOG.md.next"
    mv "$root/CHANGELOG.md.next" "$root/CHANGELOG.md"
    git -C "$root" add payload.txt CHANGELOG.md docs/portal/site.json
    git -C "$root" -c user.email=t@example.invalid -c user.name=t commit -qm family-forward
  }

  make_same_tag_correction_fixture() {
    local root="$1"
    local runtime_version="${2:-0.3.3}"
    local public_tag="${3:-v0.3.3.3}"
    local site_milestone="${4:-$public_tag}"
    local ledger_name="${5:-${site_milestone}-release-report.md}"
    local pair_count="${6:-1}"
    local old_digest='bfe323853fcb814530c9f58e078ef09d4e930419d99005af26c9135f936e3536'
    make_fixture "$root" "$runtime_version" v0.3.3.0
    mkdir -p "$root/fixtures/release-identity"
    write_public_receipt "$root/fixtures/release-identity/current-public-v0.3.3.3.json" "$public_tag" \
      "$old_digest" 227995 368332810 509660798
    git -C "$root" add fixtures/release-identity/current-public-v0.3.3.3.json
    git -C "$root" -c user.email=t@example.invalid -c user.name=t \
      commit -qm retain-current-public-receipt
    mkdir -p "$root/docs/portal"
    printf '{"release":{"milestone":"%s","audit_ledger_url":"https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/main/docs/audits/archive/%s"}}\n' \
      "$site_milestone" "$ledger_name" > "$root/docs/portal/site.json"
    printf 'corrected package bytes\n' > "$root/IMPLEMENTAUDIT.skill"
    local candidate_digest candidate_bytes
    candidate_digest="$(sha256sum "$root/IMPLEMENTAUDIT.skill" | awk '{print $1}')"
    candidate_bytes="$(wc -c < "$root/IMPLEMENTAUDIT.skill" | tr -d '[:space:]')"
    {
      printf '# Changelog\n\n## [%s] - 2026-08-11\n' "$public_tag"
      for _ in $(seq 1 "$pair_count"); do
        printf '\n- same-tag correction for `%s` `IMPLEMENTAUDIT.skill`: prematurely published `%s` (227,995 bytes) -> final `%s` (%s bytes).\n' \
          "$public_tag" "$old_digest" "$candidate_digest" "$candidate_bytes"
      done
      printf '\n'
      tail -n +3 "$root/CHANGELOG.md"
    } > "$root/CHANGELOG.md.next"
    mv "$root/CHANGELOG.md.next" "$root/CHANGELOG.md"
    git -C "$root" add .
    git -C "$root" -c user.email=t@example.invalid -c user.name=t commit -qm same-tag-correction
  }

  make_same_tag_merge_fixture() {
    local root="$1"
    make_same_tag_correction_fixture "$root"
    local correction_commit base_commit
    correction_commit="$(git -C "$root" rev-parse HEAD)"
    base_commit="$(git -C "$root" rev-parse HEAD^)"
    git -C "$root" switch -q -c main-side "$base_commit"
    printf 'main-side merge marker\n' > "$root/main-side.txt"
    git -C "$root" add main-side.txt
    git -C "$root" commit -qm main-side
    git -C "$root" merge -q --no-ff -m merge-correction "$correction_commit"
  }

  make_repeated_same_tag_correction_fixture() {
    local root="$1" pair_count="${2:-1}"
    local current_digest="${3:-151cb5400d248e3e41a30750ba690d8c46bbe907294ba82a0a5a627536ad563e}"
    local current_bytes="${4:-227999}"
    local history_action="${5:-preserve}" grammar="${6:-current}"
    make_fixture "$root" 0.3.3 v0.3.3.0
    mkdir -p "$root/fixtures/release-identity" "$root/docs/portal"
    cp fixtures/release-identity/current-public-v0.3.3.3.json \
      "$root/fixtures/release-identity/current-public-v0.3.3.3.json"
    printf '%s\n' \
      '{"release":{"milestone":"v0.3.3.3","audit_ledger_url":"https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/main/docs/audits/archive/v0.3.3.3-release-report.md"}}' \
      > "$root/docs/portal/site.json"
    {
      printf '# Changelog\n\n## [v0.3.3.3] - 2026-08-11\n\n'
      printf -- '- same-tag correction for `v0.3.3.3` `IMPLEMENTAUDIT.skill`: prematurely published `%s` (227,995 bytes) -> final `%s` (%s bytes).\n\n' \
        'bfe323853fcb814530c9f58e078ef09d4e930419d99005af26c9135f936e3536' \
        "$current_digest" "$current_bytes"
      tail -n +3 "$root/CHANGELOG.md"
    } > "$root/CHANGELOG.md.next"
    mv "$root/CHANGELOG.md.next" "$root/CHANGELOG.md"
    git -C "$root" add .
    git -C "$root" commit -qm first-public-correction

    printf 'repeated corrected package bytes\n' > "$root/IMPLEMENTAUDIT.skill"
    local candidate_digest candidate_bytes
    candidate_digest="$(sha256sum "$root/IMPLEMENTAUDIT.skill" | awk '{print $1}')"
    candidate_bytes="$(wc -c < "$root/IMPLEMENTAUDIT.skill" | tr -d '[:space:]')"
    [ "$history_action" = preserve ] || sed -i '/prematurely published/d' "$root/CHANGELOG.md"
    for _ in $(seq 1 "$pair_count"); do
      if [ "$grammar" = historical ]; then
        printf '\n- same-tag correction for `v0.3.3.3` `IMPLEMENTAUDIT.skill`: prematurely published `%s` (%s bytes) -> final `%s` (%s bytes).\n' \
          "$current_digest" "$current_bytes" "$candidate_digest" "$candidate_bytes" >> "$root/CHANGELOG.md"
      else
        printf '\n- same-tag correction for `v0.3.3.3` `IMPLEMENTAUDIT.skill`: current public `%s` (%s bytes) -> candidate `%s` (%s bytes).\n' \
          "$current_digest" "$current_bytes" "$candidate_digest" "$candidate_bytes" >> "$root/CHANGELOG.md"
      fi
    done
    git -C "$root" add IMPLEMENTAUDIT.skill CHANGELOG.md
    git -C "$root" commit -qm repeated-same-tag-correction
  }

  same_tag_correction="$tmp_parent/same-tag-correction"
  make_same_tag_correction_fixture "$same_tag_correction"
  bash scripts/build-release-asset.sh --check-release-identity \
    same-tag-correction v0.3.3.3 "$same_tag_correction/fixtures/release-identity/current-public-v0.3.3.3.json" \
    HEAD "$same_tag_correction" >/dev/null \
    || fail 'valid v0.3.3.3 same-tag correction was rejected'

  same_tag_merge="$tmp_parent/same-tag-merge"
  make_same_tag_merge_fixture "$same_tag_merge"
  bash scripts/build-release-asset.sh --check-release-identity \
    same-tag-correction v0.3.3.3 "$same_tag_merge/fixtures/release-identity/current-public-v0.3.3.3.json" \
    HEAD "$same_tag_merge" >/dev/null \
    || fail 'valid same-tag correction merged through a pull request was rejected'

  repeated_same_tag="$tmp_parent/repeated-same-tag"
  make_repeated_same_tag_correction_fixture "$repeated_same_tag"
  bash scripts/build-release-asset.sh --check-release-identity \
    same-tag-correction v0.3.3.3 "$repeated_same_tag/fixtures/release-identity/current-public-v0.3.3.3.json" \
    HEAD "$repeated_same_tag" >/dev/null \
    || fail 'valid repeated v0.3.3.3 correction bound to current public receipt was rejected'
  [ "$(grep -c 'same-tag correction for `v0.3.3.3`' "$repeated_same_tag/CHANGELOG.md")" -eq 2 ] \
    || fail 'repeated correction did not preserve the earlier same-tag pair as chronology'

  repeated_deleted_history="$tmp_parent/repeated-deleted-history"
  make_repeated_same_tag_correction_fixture "$repeated_deleted_history" 1 \
    151cb5400d248e3e41a30750ba690d8c46bbe907294ba82a0a5a627536ad563e 227999 delete

  repeated_fake_receipt="$tmp_parent/repeated-fake-receipt"
  make_repeated_same_tag_correction_fixture "$repeated_fake_receipt" 1 "$a_digest" 123
  write_public_receipt "$repeated_fake_receipt/untracked-self-authored-receipt.json" \
    v0.3.3.3 "$a_digest" 123 1 1

  repeated_historical_grammar="$tmp_parent/repeated-historical-grammar"
  make_repeated_same_tag_correction_fixture "$repeated_historical_grammar" 1 \
    151cb5400d248e3e41a30750ba690d8c46bbe907294ba82a0a5a627536ad563e 227999 preserve historical

  accepted_heldouts=()
  if bash scripts/build-release-asset.sh --check-release-identity \
      same-tag-correction v0.3.3.3 "$repeated_deleted_history/fixtures/release-identity/current-public-v0.3.3.3.json" \
      HEAD "$repeated_deleted_history" >/dev/null 2>&1; then
    accepted_heldouts+=(deleted-history)
  fi
  if bash scripts/build-release-asset.sh --check-release-identity \
      same-tag-correction v0.3.3.3 "$repeated_fake_receipt/untracked-self-authored-receipt.json" \
      HEAD "$repeated_fake_receipt" >/dev/null 2>&1; then
    accepted_heldouts+=(untracked-self-authored-receipt)
  fi
  if bash scripts/build-release-asset.sh --check-release-identity \
      same-tag-correction v0.3.3.3 "$repeated_historical_grammar/fixtures/release-identity/current-public-v0.3.3.3.json" \
      HEAD "$repeated_historical_grammar" >/dev/null 2>&1; then
    accepted_heldouts+=(repeated-historical-grammar)
  fi
  [ "${#accepted_heldouts[@]}" -eq 0 ] \
    || fail "same-tag correction accepted held-outs: ${accepted_heldouts[*]}"

  repeated_stale_receipt="$tmp_parent/repeated-stale-receipt"
  make_repeated_same_tag_correction_fixture "$repeated_stale_receipt"
  sed -i \
    -e 's/151cb5400d248e3e41a30750ba690d8c46bbe907294ba82a0a5a627536ad563e/bfe323853fcb814530c9f58e078ef09d4e930419d99005af26c9135f936e3536/g' \
    -e 's/227999/227995/g' \
    "$repeated_stale_receipt/fixtures/release-identity/current-public-v0.3.3.3.json"
  if bash scripts/build-release-asset.sh --check-release-identity \
      same-tag-correction v0.3.3.3 "$repeated_stale_receipt/fixtures/release-identity/current-public-v0.3.3.3.json" \
      HEAD "$repeated_stale_receipt" >/dev/null 2>&1; then
    fail 'repeated correction accepted a stale first-publication receipt as the current preimage'
  fi

  repeated_disagreeing_receipt="$tmp_parent/repeated-disagreeing-receipt"
  make_repeated_same_tag_correction_fixture "$repeated_disagreeing_receipt"
  sed -i \
    's/"download_sha256": "[0-9a-f]*"/"download_sha256": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"/' \
    "$repeated_disagreeing_receipt/fixtures/release-identity/current-public-v0.3.3.3.json"
  if bash scripts/build-release-asset.sh --check-release-identity \
      same-tag-correction v0.3.3.3 "$repeated_disagreeing_receipt/fixtures/release-identity/current-public-v0.3.3.3.json" \
      HEAD "$repeated_disagreeing_receipt" >/dev/null 2>&1; then
    fail 'repeated correction accepted disagreeing API and download readbacks'
  fi

  repeated_wrong_tag_receipt="$tmp_parent/repeated-wrong-tag-receipt"
  make_repeated_same_tag_correction_fixture "$repeated_wrong_tag_receipt"
  sed -i 's/"release_tag": "v0.3.3.3"/"release_tag": "v0.3.3.2"/' \
    "$repeated_wrong_tag_receipt/fixtures/release-identity/current-public-v0.3.3.3.json"
  if bash scripts/build-release-asset.sh --check-release-identity \
      same-tag-correction v0.3.3.3 "$repeated_wrong_tag_receipt/fixtures/release-identity/current-public-v0.3.3.3.json" \
      HEAD "$repeated_wrong_tag_receipt" >/dev/null 2>&1; then
    fail 'repeated correction accepted a current-public receipt for another tag'
  fi

  repeated_missing_pair="$tmp_parent/repeated-missing-pair"
  make_repeated_same_tag_correction_fixture "$repeated_missing_pair"
  sed -i '/current public/d' "$repeated_missing_pair/CHANGELOG.md"
  git -C "$repeated_missing_pair" add CHANGELOG.md
  git -C "$repeated_missing_pair" commit -qm repeated-missing-pair
  if bash scripts/build-release-asset.sh --check-release-identity \
      same-tag-correction v0.3.3.3 "$repeated_missing_pair/fixtures/release-identity/current-public-v0.3.3.3.json" \
      HEAD "$repeated_missing_pair" >/dev/null 2>&1; then
    fail 'repeated correction accepted a release commit without a new current-to-candidate pair'
  fi

  repeated_duplicate_pair="$tmp_parent/repeated-duplicate-pair"
  make_repeated_same_tag_correction_fixture "$repeated_duplicate_pair" 2
  if bash scripts/build-release-asset.sh --check-release-identity \
      same-tag-correction v0.3.3.3 "$repeated_duplicate_pair/fixtures/release-identity/current-public-v0.3.3.3.json" \
      HEAD "$repeated_duplicate_pair" >/dev/null 2>&1; then
    fail 'repeated correction accepted duplicate current-to-candidate pairs'
  fi

  repeated_unchanged_digest="$tmp_parent/repeated-unchanged-digest"
  make_repeated_same_tag_correction_fixture "$repeated_unchanged_digest"
  sed -i -E \
    '/current public/s/(candidate `)[0-9a-f]{64}/\1151cb5400d248e3e41a30750ba690d8c46bbe907294ba82a0a5a627536ad563e/' \
    "$repeated_unchanged_digest/CHANGELOG.md"
  git -C "$repeated_unchanged_digest" add CHANGELOG.md
  git -C "$repeated_unchanged_digest" commit -qm repeated-unchanged-digest
  if bash scripts/build-release-asset.sh --check-release-identity \
      same-tag-correction v0.3.3.3 "$repeated_unchanged_digest/fixtures/release-identity/current-public-v0.3.3.3.json" \
      HEAD "$repeated_unchanged_digest" >/dev/null 2>&1; then
    fail 'repeated correction accepted an unchanged current-public digest'
  fi

  repeated_wrong_candidate="$tmp_parent/repeated-wrong-candidate"
  make_repeated_same_tag_correction_fixture "$repeated_wrong_candidate"
  sed -i -E \
    '/current public/s/(candidate `)[0-9a-f]{64}/\1bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb/' \
    "$repeated_wrong_candidate/CHANGELOG.md"
  git -C "$repeated_wrong_candidate" add CHANGELOG.md
  git -C "$repeated_wrong_candidate" commit -qm repeated-wrong-candidate
  if bash scripts/build-release-asset.sh --check-release-identity \
      same-tag-correction v0.3.3.3 "$repeated_wrong_candidate/fixtures/release-identity/current-public-v0.3.3.3.json" \
      HEAD "$repeated_wrong_candidate" >/dev/null 2>&1; then
    fail 'repeated correction accepted a candidate digest that does not match the asset'
  fi

  repeated_wrong_candidate_bytes="$tmp_parent/repeated-wrong-candidate-bytes"
  make_repeated_same_tag_correction_fixture "$repeated_wrong_candidate_bytes"
  sed -i -E '/current public/s/(candidate `[^`]+` \()[0-9,]+/\1999/' \
    "$repeated_wrong_candidate_bytes/CHANGELOG.md"
  git -C "$repeated_wrong_candidate_bytes" add CHANGELOG.md
  git -C "$repeated_wrong_candidate_bytes" commit -qm repeated-wrong-candidate-bytes
  if bash scripts/build-release-asset.sh --check-release-identity \
      same-tag-correction v0.3.3.3 "$repeated_wrong_candidate_bytes/fixtures/release-identity/current-public-v0.3.3.3.json" \
      HEAD "$repeated_wrong_candidate_bytes" >/dev/null 2>&1; then
    fail 'repeated correction accepted candidate bytes that do not match the asset'
  fi

  repeated_dirty_owner="$tmp_parent/repeated-dirty-owner"
  make_repeated_same_tag_correction_fixture "$repeated_dirty_owner"
  printf '\n' >> "$repeated_dirty_owner/docs/portal/site.json"
  if bash scripts/build-release-asset.sh --check-release-identity \
      same-tag-correction v0.3.3.3 "$repeated_dirty_owner/fixtures/release-identity/current-public-v0.3.3.3.json" \
      HEAD "$repeated_dirty_owner" >/dev/null 2>&1; then
    fail 'repeated correction accepted a dirty release identity owner'
  fi

  repeated_non_head="$tmp_parent/repeated-non-head"
  make_repeated_same_tag_correction_fixture "$repeated_non_head"
  repeated_release_commit="$(git -C "$repeated_non_head" rev-parse HEAD)"
  printf 'later repeated tree\n' >> "$repeated_non_head/payload.txt"
  git -C "$repeated_non_head" add payload.txt
  git -C "$repeated_non_head" commit -qm repeated-later-tree
  if bash scripts/build-release-asset.sh --check-release-identity \
      same-tag-correction v0.3.3.3 "$repeated_non_head/fixtures/release-identity/current-public-v0.3.3.3.json" \
      "$repeated_release_commit" "$repeated_non_head" >/dev/null 2>&1; then
    fail 'repeated correction accepted a non-HEAD release commit/tree'
  fi

  if bash scripts/build-release-asset.sh --check-release-identity \
      forward 0.3.3.3 HEAD "$repeated_same_tag" >/dev/null 2>&1; then
    fail 'forward substituted for a repeated same-tag correction'
  fi
  if bash scripts/build-release-asset.sh --check-release-identity \
      republish 0.3.3 HEAD "$repeated_same_tag" >/dev/null 2>&1; then
    fail 'republish substituted for a repeated same-tag correction'
  fi
  if bash scripts/build-release-asset.sh --check-release-identity \
      family-forward v0.3.3.0 v0.3.3.3 HEAD "$repeated_same_tag" >/dev/null 2>&1; then
    fail 'family-forward substituted for a repeated same-tag correction'
  fi

  if bash scripts/build-release-asset.sh --check-release-identity \
      same-tag-correction v0.3.3.2 "$same_tag_correction/fixtures/release-identity/current-public-v0.3.3.3.json" \
      HEAD "$same_tag_correction" >/dev/null 2>&1; then
    fail 'same-tag correction accepted a different public tag'
  fi

  same_tag_missing_pair="$tmp_parent/same-tag-missing-pair"
  make_same_tag_correction_fixture "$same_tag_missing_pair"
  sed -i '/same-tag correction for/d' "$same_tag_missing_pair/CHANGELOG.md"
  git -C "$same_tag_missing_pair" add CHANGELOG.md
  git -C "$same_tag_missing_pair" commit -qm remove-pair
  if bash scripts/build-release-asset.sh --check-release-identity \
      same-tag-correction v0.3.3.3 "$same_tag_missing_pair/fixtures/release-identity/current-public-v0.3.3.3.json" \
      HEAD "$same_tag_missing_pair" >/dev/null 2>&1; then
    fail 'same-tag correction accepted a commit without the replacement pair'
  fi

  same_tag_duplicate_pair="$tmp_parent/same-tag-duplicate-pair"
  make_same_tag_correction_fixture "$same_tag_duplicate_pair" \
    0.3.3 v0.3.3.3 v0.3.3.3 v0.3.3.3-release-report.md 2
  if bash scripts/build-release-asset.sh --check-release-identity \
      same-tag-correction v0.3.3.3 "$same_tag_duplicate_pair/fixtures/release-identity/current-public-v0.3.3.3.json" \
      HEAD "$same_tag_duplicate_pair" >/dev/null 2>&1; then
    fail 'same-tag correction accepted duplicate replacement pairs'
  fi

  same_tag_unchanged_digest="$tmp_parent/same-tag-unchanged-digest"
  make_same_tag_correction_fixture "$same_tag_unchanged_digest"
  sed -i -E \
    's/(-> final `)[0-9a-f]{64}(`)/\1bfe323853fcb814530c9f58e078ef09d4e930419d99005af26c9135f936e3536\2/' \
    "$same_tag_unchanged_digest/CHANGELOG.md"
  git -C "$same_tag_unchanged_digest" add CHANGELOG.md
  git -C "$same_tag_unchanged_digest" commit -qm unchanged-digest
  if bash scripts/build-release-asset.sh --check-release-identity \
      same-tag-correction v0.3.3.3 "$same_tag_unchanged_digest/fixtures/release-identity/current-public-v0.3.3.3.json" \
      HEAD "$same_tag_unchanged_digest" >/dev/null 2>&1; then
    fail 'same-tag correction accepted an unchanged package digest'
  fi

  same_tag_wrong_old_digest="$tmp_parent/same-tag-wrong-old-digest"
  make_same_tag_correction_fixture "$same_tag_wrong_old_digest"
  sed -i \
    's/bfe323853fcb814530c9f58e078ef09d4e930419d99005af26c9135f936e3536/aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa/' \
    "$same_tag_wrong_old_digest/CHANGELOG.md"
  git -C "$same_tag_wrong_old_digest" add CHANGELOG.md
  git -C "$same_tag_wrong_old_digest" commit -qm wrong-old-digest
  if bash scripts/build-release-asset.sh --check-release-identity \
      same-tag-correction v0.3.3.3 "$same_tag_wrong_old_digest/fixtures/release-identity/current-public-v0.3.3.3.json" \
      HEAD "$same_tag_wrong_old_digest" >/dev/null 2>&1; then
    fail 'same-tag correction accepted the wrong premature package digest'
  fi

  same_tag_wrong_old_bytes="$tmp_parent/same-tag-wrong-old-bytes"
  make_same_tag_correction_fixture "$same_tag_wrong_old_bytes"
  sed -i 's/(227,995 bytes)/(227,994 bytes)/' "$same_tag_wrong_old_bytes/CHANGELOG.md"
  git -C "$same_tag_wrong_old_bytes" add CHANGELOG.md
  git -C "$same_tag_wrong_old_bytes" commit -qm wrong-old-bytes
  if bash scripts/build-release-asset.sh --check-release-identity \
      same-tag-correction v0.3.3.3 "$same_tag_wrong_old_bytes/fixtures/release-identity/current-public-v0.3.3.3.json" \
      HEAD "$same_tag_wrong_old_bytes" >/dev/null 2>&1; then
    fail 'same-tag correction accepted the wrong premature package byte count'
  fi

  same_tag_wrong_new_digest="$tmp_parent/same-tag-wrong-new-digest"
  make_same_tag_correction_fixture "$same_tag_wrong_new_digest"
  sed -i -E \
    's/(-> final `)[0-9a-f]{64}(`)/\1bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb\2/' \
    "$same_tag_wrong_new_digest/CHANGELOG.md"
  git -C "$same_tag_wrong_new_digest" add CHANGELOG.md
  git -C "$same_tag_wrong_new_digest" commit -qm wrong-new-digest
  if bash scripts/build-release-asset.sh --check-release-identity \
      same-tag-correction v0.3.3.3 "$same_tag_wrong_new_digest/fixtures/release-identity/current-public-v0.3.3.3.json" \
      HEAD "$same_tag_wrong_new_digest" >/dev/null 2>&1; then
    fail 'same-tag correction accepted a replacement digest that does not match the candidate'
  fi

  same_tag_wrong_new_bytes="$tmp_parent/same-tag-wrong-new-bytes"
  make_same_tag_correction_fixture "$same_tag_wrong_new_bytes"
  sed -i -E 's/(-> final `[^`]+` \()[0-9,]+( bytes\))/\1999\2/' \
    "$same_tag_wrong_new_bytes/CHANGELOG.md"
  git -C "$same_tag_wrong_new_bytes" add CHANGELOG.md
  git -C "$same_tag_wrong_new_bytes" commit -qm wrong-new-bytes
  if bash scripts/build-release-asset.sh --check-release-identity \
      same-tag-correction v0.3.3.3 "$same_tag_wrong_new_bytes/fixtures/release-identity/current-public-v0.3.3.3.json" \
      HEAD "$same_tag_wrong_new_bytes" >/dev/null 2>&1; then
    fail 'same-tag correction accepted a replacement byte count that does not match the candidate'
  fi

  for dirty_owner in \
      .claude-plugin/plugin.json \
      skills/implementaudit/SKILL.md \
      CHANGELOG.md \
      docs/portal/site.json; do
    owner_slug="$(printf '%s' "$dirty_owner" | tr '/.' '--')"
    dirty_owner_root="$tmp_parent/same-tag-dirty-owner-$owner_slug"
    make_same_tag_correction_fixture "$dirty_owner_root"
    printf '\n' >> "$dirty_owner_root/$dirty_owner"
    if bash scripts/build-release-asset.sh --check-release-identity \
        same-tag-correction v0.3.3.3 "$dirty_owner_root/fixtures/release-identity/current-public-v0.3.3.3.json" \
        HEAD "$dirty_owner_root" >/dev/null 2>&1; then
      fail "same-tag correction accepted dirty release identity owner $dirty_owner"
    fi
  done

  same_tag_wrong_portal="$tmp_parent/same-tag-wrong-portal"
  make_same_tag_correction_fixture "$same_tag_wrong_portal" 0.3.3 v0.3.3.3 v0.3.3.2
  if bash scripts/build-release-asset.sh --check-release-identity \
      same-tag-correction v0.3.3.3 "$same_tag_wrong_portal/fixtures/release-identity/current-public-v0.3.3.3.json" \
      HEAD "$same_tag_wrong_portal" >/dev/null 2>&1; then
    fail 'same-tag correction accepted the wrong portal milestone'
  fi

  same_tag_wrong_ledger="$tmp_parent/same-tag-wrong-ledger"
  make_same_tag_correction_fixture "$same_tag_wrong_ledger" 0.3.3 v0.3.3.3 v0.3.3.3 v0.3.3.2-release-report.md
  if bash scripts/build-release-asset.sh --check-release-identity \
      same-tag-correction v0.3.3.3 "$same_tag_wrong_ledger/fixtures/release-identity/current-public-v0.3.3.3.json" \
      HEAD "$same_tag_wrong_ledger" >/dev/null 2>&1; then
    fail 'same-tag correction accepted the wrong release ledger'
  fi

  same_tag_wrong_runtime="$tmp_parent/same-tag-wrong-runtime"
  make_same_tag_correction_fixture "$same_tag_wrong_runtime" 0.3.2
  if bash scripts/build-release-asset.sh --check-release-identity \
      same-tag-correction v0.3.3.3 "$same_tag_wrong_runtime/fixtures/release-identity/current-public-v0.3.3.3.json" \
      HEAD "$same_tag_wrong_runtime" >/dev/null 2>&1; then
    fail 'same-tag correction accepted a runtime outside 0.3.3'
  fi

  same_tag_non_head="$tmp_parent/same-tag-non-head"
  make_same_tag_correction_fixture "$same_tag_non_head"
  same_tag_release_commit="$(git -C "$same_tag_non_head" rev-parse HEAD)"
  printf 'later tree\n' >> "$same_tag_non_head/payload.txt"
  git -C "$same_tag_non_head" add payload.txt
  git -C "$same_tag_non_head" commit -qm later-tree
  if bash scripts/build-release-asset.sh --check-release-identity \
      same-tag-correction v0.3.3.3 "$same_tag_non_head/fixtures/release-identity/current-public-v0.3.3.3.json" \
      "$same_tag_release_commit" "$same_tag_non_head" >/dev/null 2>&1; then
    fail 'same-tag correction accepted a non-HEAD release commit/tree'
  fi

  # Enumerate every accepted prospective mode against the correction fixture:
  # same-tag-correction passes above; every ordinary mode must reject it.
  if bash scripts/build-release-asset.sh --check-release-identity \
      forward 0.3.3.3 HEAD "$same_tag_correction" >/dev/null 2>&1; then
    fail 'forward accepted a four-component public tag as a prior runtime version and substituted for same-tag correction'
  fi
  if bash scripts/build-release-asset.sh --check-release-identity \
      republish 0.3.3 HEAD "$same_tag_correction" >/dev/null 2>&1; then
    fail 'ordinary republish substituted for same-tag correction'
  fi
  if bash scripts/build-release-asset.sh --check-release-identity \
      family-forward v0.3.3.0 v0.3.3.3 HEAD "$same_tag_correction" >/dev/null 2>&1; then
    fail 'real-shape family-forward substituted for same-tag correction without enforcing its asset pair'
  fi
  verify_same_tag_output="$(bash scripts/verify-package.sh \
    --release-identity same-tag-correction 2>&1 || true)"
  case "$verify_same_tag_output" in
    *"--release-identity same-tag-correction requires <public-tag> <current-public-receipt> <release-commit>"*) : ;;
    *) fail 'verify-package.sh did not expose same-tag-correction identity mode' ;;
  esac

  no_record="$tmp_parent/republish-no-record"
  make_fixture "$no_record" 0.3.2
  printf 'changed payload\n' > "$no_record/payload.txt"
  printf 'changed package\n' > "$no_record/IMPLEMENTAUDIT.skill"
  git -C "$no_record" add payload.txt IMPLEMENTAUDIT.skill
  git -C "$no_record" -c user.email=t@example.invalid -c user.name=t commit -qm republish
  if bash scripts/build-release-asset.sh --check-release-identity \
      republish 0.3.2 HEAD "$no_record" >/dev/null 2>&1; then
    fail 'same-version republication without a digest pair was accepted'
  fi

  fabricated="$tmp_parent/republish-fabricated-pair"
  make_fixture "$fabricated" 0.3.2
  printf 'changed payload\n' > "$fabricated/payload.txt"
  printf 'real package bytes\n' > "$fabricated/IMPLEMENTAUDIT.skill"
  printf '\n## [v0.3.2.0 corrected re-release] - 2026-08-04\n- `IMPLEMENTAUDIT.skill`: superseded `%s` (1 byte) -> superseding `%s` (888 bytes).\n' \
    "$a_digest" "$b_digest" >> "$fabricated/CHANGELOG.md"
  git -C "$fabricated" add .
  git -C "$fabricated" commit -qm republish
  if bash scripts/build-release-asset.sh --check-release-identity \
      republish 0.3.2 HEAD "$fabricated" >/dev/null 2>&1; then
    fail 'fabricated package digest and byte count were accepted'
  fi

  preexisting="$tmp_parent/republish-preexisting-pair"
  make_fixture "$preexisting" 0.3.2
  printf '\n- `IMPLEMENTAUDIT.skill`: superseded `%s` (1 byte) -> superseding `%s` (2 bytes).\n' \
    "$a_digest" "$b_digest" >> "$preexisting/CHANGELOG.md"
  git -C "$preexisting" add CHANGELOG.md
  git -C "$preexisting" -c user.email=t@example.invalid -c user.name=t commit -qm record
  printf 'changed payload\n' > "$preexisting/payload.txt"
  git -C "$preexisting" add payload.txt
  git -C "$preexisting" -c user.email=t@example.invalid -c user.name=t commit -qm republish
  if bash scripts/build-release-asset.sh --check-release-identity \
      republish 0.3.2 HEAD "$preexisting" >/dev/null 2>&1; then
    fail 'digest pair from an earlier commit was accepted for republication'
  fi

  with_pair="$tmp_parent/republish-with-pair"
  make_fixture "$with_pair" 0.3.2
  printf 'changed payload\n' > "$with_pair/payload.txt"
  printf 'changed package\n' > "$with_pair/IMPLEMENTAUDIT.skill"
  candidate_digest="$(sha256sum "$with_pair/IMPLEMENTAUDIT.skill" | awk '{print $1}')"
  candidate_bytes="$(wc -c < "$with_pair/IMPLEMENTAUDIT.skill" | tr -d '[:space:]')"
  printf '\n## [v0.3.2.0 corrected re-release] - 2026-08-04\n- `IMPLEMENTAUDIT.skill`: superseded `%s` (1 byte) -> superseding `%s` (%s bytes).\n' \
    "$a_digest" "$candidate_digest" "$candidate_bytes" >> "$with_pair/CHANGELOG.md"
  git -C "$with_pair" add payload.txt IMPLEMENTAUDIT.skill CHANGELOG.md
  git -C "$with_pair" -c user.email=t@example.invalid -c user.name=t commit -qm republish
  bash scripts/build-release-asset.sh --check-release-identity \
    republish 0.3.2 HEAD "$with_pair" >/dev/null \
    || fail 'same-version republication with a same-commit digest pair was rejected'

  cross_artifact="$tmp_parent/republish-cross-artifact"
  make_fixture "$cross_artifact" 0.3.2
  printf 'changed package\n' > "$cross_artifact/IMPLEMENTAUDIT.skill"
  cross_digest="$(sha256sum "$cross_artifact/IMPLEMENTAUDIT.skill" | awk '{print $1}')"
  cross_bytes="$(wc -c < "$cross_artifact/IMPLEMENTAUDIT.skill" | tr -d '[:space:]')"
  printf '\n## [v0.3.2.0 corrected re-release] - 2026-08-04\n- `CHECKSUMS.txt`: IMPLEMENTAUDIT.skill superseded `%s` (1 byte) -> superseding `%s` (%s bytes).\n' \
    "$a_digest" "$cross_digest" "$cross_bytes" >> "$cross_artifact/CHANGELOG.md"
  git -C "$cross_artifact" add .
  git -C "$cross_artifact" commit -qm republish
  if bash scripts/build-release-asset.sh --check-release-identity \
      republish 0.3.2 HEAD "$cross_artifact" >/dev/null 2>&1; then
    fail 'digest pair for another artifact was accepted as IMPLEMENTAUDIT.skill identity'
  fi

  same_tree="$(git -C "$with_pair" write-tree)"
  orphan="$(printf 'unrelated same-tree record\n' | git -C "$with_pair" commit-tree "$same_tree")"
  if bash scripts/build-release-asset.sh --check-release-identity \
      republish 0.3.2 "$orphan" "$with_pair" >/dev/null 2>&1; then
    fail 'unrelated same-tree commit was accepted as release authority'
  fi

  forward="$tmp_parent/normal-version-bump"
  make_fixture "$forward" 0.3.2
  printf '{"version":"0.3.3"}\n' > "$forward/.claude-plugin/plugin.json"
  sed -i 's/version: "0.3.2"/version: "0.3.3"/' "$forward/skills/implementaudit/SKILL.md"
  printf 'changed payload\n' > "$forward/payload.txt"
  git -C "$forward" add .
  git -C "$forward" -c user.email=t@example.invalid -c user.name=t commit -qm forward
  bash scripts/build-release-asset.sh --check-release-identity \
    forward 0.3.2 HEAD "$forward" >/dev/null \
    || fail 'normal forward version bump gained a digest-pair obligation'
  if bash scripts/build-release-asset.sh --check-release-identity \
      forward 0.2.0 HEAD "$forward" >/dev/null 2>&1; then
    fail 'caller-supplied non-current previous version bypassed CHANGELOG authority'
  fi

  family_forward="$tmp_parent/family-forward"
  make_family_forward_fixture "$family_forward" 0.3.3 v0.3.3.0 v0.3.3.3
  bash scripts/build-release-asset.sh --check-release-identity \
    family-forward v0.3.3.0 v0.3.3.3 HEAD "$family_forward" >/dev/null \
    || fail 'valid v0.3.3.3 public identity for runtime 0.3.3 was rejected'

  dirty_candidate_owners="$tmp_parent/family-forward-dirty-candidate-owners"
  make_fixture "$dirty_candidate_owners" 0.3.3 v0.3.3.0
  printf '\n' >> "$dirty_candidate_owners/.claude-plugin/plugin.json"
  printf '\n' >> "$dirty_candidate_owners/skills/implementaudit/SKILL.md"
  mkdir -p "$dirty_candidate_owners/docs/portal"
  printf '{"release":{"milestone":"v0.3.3.3","audit_ledger_url":"https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/main/docs/audits/archive/v0.3.3.3-release-report.md"}}\n' \
    > "$dirty_candidate_owners/docs/portal/site.json"
  {
    printf '# Changelog\n\n## [v0.3.3.3] - 2026-08-10\n- Corrective and completion release.\n\n'
    tail -n +3 "$dirty_candidate_owners/CHANGELOG.md"
  } > "$dirty_candidate_owners/CHANGELOG.md.next"
  mv "$dirty_candidate_owners/CHANGELOG.md.next" "$dirty_candidate_owners/CHANGELOG.md"
  if bash scripts/build-release-asset.sh --check-release-identity \
      family-forward v0.3.3.0 v0.3.3.3 HEAD "$dirty_candidate_owners" >/dev/null 2>&1; then
    fail 'family-forward accepted dirty candidate owners absent from the v0.3.3.0 release commit'
  fi

  for dirty_owner in \
      .claude-plugin/plugin.json \
      skills/implementaudit/SKILL.md \
      CHANGELOG.md \
      docs/portal/site.json; do
    owner_slug="$(printf '%s' "$dirty_owner" | tr '/.' '--')"
    dirty_owner_root="$tmp_parent/family-forward-dirty-owner-$owner_slug"
    make_family_forward_fixture "$dirty_owner_root" 0.3.3 v0.3.3.0 v0.3.3.3
    printf '\n' >> "$dirty_owner_root/$dirty_owner"
    if bash scripts/build-release-asset.sh --check-release-identity \
        family-forward v0.3.3.0 v0.3.3.3 HEAD "$dirty_owner_root" >/dev/null 2>&1; then
      fail "family-forward accepted dirty release identity owner $dirty_owner"
    fi
  done

  backward_9_to_3="$tmp_parent/family-forward-backward-9-to-3"
  make_family_forward_fixture "$backward_9_to_3" 0.3.3 v0.3.3.9 v0.3.3.3
  if bash scripts/build-release-asset.sh --check-release-identity \
      family-forward v0.3.3.9 v0.3.3.3 HEAD "$backward_9_to_3" >/dev/null 2>&1; then
    fail 'family-forward accepted v0.3.3.9 -> v0.3.3.3 rollback'
  fi

  backward_3_to_2="$tmp_parent/family-forward-backward-3-to-2"
  make_family_forward_fixture "$backward_3_to_2" 0.3.3 v0.3.3.3 v0.3.3.2
  if bash scripts/build-release-asset.sh --check-release-identity \
      family-forward v0.3.3.3 v0.3.3.2 HEAD "$backward_3_to_2" >/dev/null 2>&1; then
    fail 'family-forward accepted v0.3.3.3 -> v0.3.3.2 rollback'
  fi

  site_mismatch="$tmp_parent/family-forward-site-mismatch"
  make_family_forward_fixture "$site_mismatch" 0.3.3 v0.3.3.0 v0.3.3.3 v0.3.3.2
  if bash scripts/build-release-asset.sh --check-release-identity \
      family-forward v0.3.3.0 v0.3.3.3 HEAD "$site_mismatch" >/dev/null 2>&1; then
    fail 'family-forward accepted a candidate tag different from docs/portal/site.json milestone'
  fi

  stale_ledger="$tmp_parent/family-forward-stale-ledger"
  make_family_forward_fixture "$stale_ledger" 0.3.3 v0.3.3.0 v0.3.3.3 v0.3.3.3 v0.3.3.0
  if bash scripts/build-release-asset.sh --check-release-identity \
      family-forward v0.3.3.0 v0.3.3.3 HEAD "$stale_ledger" >/dev/null 2>&1; then
    fail 'family-forward accepted a v0.3.3.0 audit ledger for v0.3.3.3'
  fi

  prefix_collision_ledger="$tmp_parent/family-forward-prefix-collision-ledger"
  make_family_forward_fixture "$prefix_collision_ledger" 0.3.3 v0.3.3.0 v0.3.3.3 v0.3.3.3 v0.3.3.30
  if bash scripts/build-release-asset.sh --check-release-identity \
      family-forward v0.3.3.0 v0.3.3.3 HEAD "$prefix_collision_ledger" >/dev/null 2>&1; then
    fail 'family-forward accepted a v0.3.3.30 audit ledger for v0.3.3.3'
  fi

  exact_tag_placeholder_ledger="$tmp_parent/family-forward-exact-tag-placeholder-ledger"
  make_family_forward_fixture "$exact_tag_placeholder_ledger" 0.3.3 v0.3.3.0 v0.3.3.3 \
    v0.3.3.3 v0.3.3.3 placeholder-v0.3.3.3-TBD.md
  if bash scripts/build-release-asset.sh --check-release-identity \
      family-forward v0.3.3.0 v0.3.3.3 HEAD "$exact_tag_placeholder_ledger" >/dev/null 2>&1; then
    fail 'family-forward accepted placeholder-v0.3.3.3-TBD.md instead of the canonical ledger basename'
  fi

  wrong_family="$tmp_parent/family-forward-wrong-family"
  make_family_forward_fixture "$wrong_family" 0.3.3 v0.3.3.0 v0.3.4.3
  if bash scripts/build-release-asset.sh --check-release-identity \
      family-forward v0.3.3.0 v0.3.4.3 HEAD "$wrong_family" >/dev/null 2>&1; then
    fail 'family-forward accepted a candidate tag outside runtime 0.3.3'
  fi

  zero_suffix="$tmp_parent/family-forward-zero-suffix"
  make_family_forward_fixture "$zero_suffix" 0.3.3 v0.3.3.2 v0.3.3.0
  if bash scripts/build-release-asset.sh --check-release-identity \
      family-forward v0.3.3.2 v0.3.3.0 HEAD "$zero_suffix" >/dev/null 2>&1; then
    fail 'family-forward accepted a zero fourth-component candidate tag'
  fi

  equal_tag="$tmp_parent/family-forward-equal-tag"
  make_family_forward_fixture "$equal_tag" 0.3.3 v0.3.3.3 v0.3.3.3
  if bash scripts/build-release-asset.sh --check-release-identity \
      family-forward v0.3.3.3 v0.3.3.3 HEAD "$equal_tag" >/dev/null 2>&1; then
    fail 'family-forward accepted an unchanged public tag'
  fi

  missing_heading="$tmp_parent/family-forward-missing-heading"
  make_fixture "$missing_heading" 0.3.3 v0.3.3.0
  printf 'changed payload\n' > "$missing_heading/payload.txt"
  git -C "$missing_heading" add payload.txt
  git -C "$missing_heading" -c user.email=t@example.invalid -c user.name=t commit -qm family-forward
  if bash scripts/build-release-asset.sh --check-release-identity \
      family-forward v0.3.3.0 v0.3.3.3 HEAD "$missing_heading" >/dev/null 2>&1; then
    fail 'family-forward accepted a candidate without an exact CHANGELOG heading'
  fi

  four_component_runtime="$tmp_parent/family-forward-four-component-runtime"
  make_family_forward_fixture "$four_component_runtime" 0.3.3.3 v0.3.3.0 v0.3.3.3
  if bash scripts/build-release-asset.sh --check-release-identity \
      family-forward v0.3.3.0 v0.3.3.3 HEAD "$four_component_runtime" >/dev/null 2>&1; then
    fail 'family-forward accepted a four-component runtime version'
  fi

  if bash scripts/build-release-asset.sh --check-release-identity \
      republish 0.3.3 HEAD "$family_forward" >/dev/null 2>&1; then
    fail 'republish substituted for a family-forward release'
  fi

  family_forward_commit="$(git -C "$family_forward" rev-parse HEAD)"
  printf 'moved head\n' >> "$family_forward/payload.txt"
  git -C "$family_forward" add payload.txt
  git -C "$family_forward" -c user.email=t@example.invalid -c user.name=t commit -qm moved-head
  if bash scripts/build-release-asset.sh --check-release-identity \
      family-forward v0.3.3.0 v0.3.3.3 "$family_forward_commit" "$family_forward" >/dev/null 2>&1; then
    fail 'family-forward accepted a candidate commit after HEAD moved'
  fi

  verify_family_forward="$tmp_parent/verify-family-forward"
  mkdir -p "$verify_family_forward"
  git archive HEAD | tar -x -C "$verify_family_forward"
  git -C "$verify_family_forward" init -q
  git -C "$verify_family_forward" config user.email t@example.invalid
  git -C "$verify_family_forward" config user.name t
  printf '%s\n' \
    '{"release":{"milestone":"v0.3.3.0","audit_ledger_url":"https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/main/docs/audits/archive/v0.3.3.0-release-report.md"}}' \
    > "$verify_family_forward/docs/portal/site.json"
  git -C "$verify_family_forward" add .
  git -C "$verify_family_forward" -c user.email=t@example.invalid \
    -c user.name=t commit -qm verify-family-forward
  verify_output="$(cd "$verify_family_forward" && \
    bash scripts/verify-package.sh --release-identity \
      family-forward v0.3.3.0 v0.3.3.3 HEAD 2>&1 || true)"
  case "$verify_output" in
    *"family-forward candidate tag 'v0.3.3.3' != docs/portal/site.json milestone 'v0.3.3.0'"*) : ;;
    *) fail 'verify-package.sh did not expose family-forward identity mode' ;;
  esac

  real_record_commit="$(git log -1 --format=%H -S 'This entry is the one retroactive application' -- CHANGELOG.md)"
  [ -n "$real_record_commit" ] || fail 'real #96 retroactive digest-pair commit not found'
  if bash scripts/build-release-asset.sh --check-release-identity \
      retroactive 0.3.2 "$real_record_commit" "$repo_root" >/dev/null 2>&1; then
    fail 'historical retroactive record remained available for prospective qualification'
  fi
  bash scripts/build-release-asset.sh --check-historical-release-record "$repo_root" >/dev/null \
    || fail 'separate nonqualifying historical #96 record check was rejected'
  if grep -Fq 'retroactive' scripts/verify-package.sh; then
    fail 'package verifier still exposes retroactive mode as prospective qualification'
  fi

  stale_root="$tmp_parent/stale-artifact"
  mkdir -p "$stale_root/dist"
  printf 'withdrawn bytes\n' > "$stale_root/dist/pkg.skill"
  stale_digest="$(sha256sum "$stale_root/dist/pkg.skill" | awk '{print $1}')"
  printf '# Changelog\n- asset: superseded `%s` -> superseding `%s`.\n' \
    "$stale_digest" "$b_digest" > "$stale_root/CHANGELOG.md"
  if bash scripts/build-release-asset.sh --check-stale-artifact \
      package "$stale_root/dist/pkg.skill" "$stale_root/CHANGELOG.md" >/dev/null 2>&1; then
    fail 'withdrawn ignored package artifact was accepted'
  fi
  bash scripts/build-release-asset.sh --check-stale-artifact \
    source "$stale_root/dist/pkg.skill" "$stale_root/CHANGELOG.md" >/dev/null \
    || fail 'source-only run was subjected to package/release stale-artifact policy'
  printf 'current bytes\n' > "$stale_root/dist/pkg.skill"
  bash scripts/build-release-asset.sh --check-stale-artifact \
    package "$stale_root/dist/pkg.skill" "$stale_root/CHANGELOG.md" >/dev/null \
    || fail 'non-superseded package artifact was rejected'

  printf 'release-asset.test: identity-only ok\n'
  exit 0
fi

# Hosted validation must exercise the candidate diff and must delegate the
# registered validation population to the canonical verifier exactly once.
workflow=.github/workflows/validate.yml
if ! grep -Fq 'run: git diff --check HEAD^ HEAD' "$workflow"; then
  printf 'release-asset.test: hosted whitespace check does not inspect the candidate diff\n' >&2
  exit 1
fi
if ! grep -Fq 'run: bash scripts/verify-package.sh' "$workflow"; then
  printf 'release-asset.test: hosted workflow does not invoke the canonical verifier\n' >&2
  exit 1
fi
direct_registered_tests="$(grep -Ec '^[[:space:]]+bash tests/.*\.sh' "$workflow" || :)"
if [ "$direct_registered_tests" -ne 0 ]; then
  printf 'release-asset.test: hosted workflow duplicates %s registered test invocation(s)\n' "$direct_registered_tests" >&2
  exit 1
fi
direct_verifier_scripts="$(grep -Ec '^[[:space:]]+(run:[[:space:]]+)?bash scripts/.*\.sh' "$workflow" || :)"
if [ "$direct_verifier_scripts" -ne 1 ]; then
  printf 'release-asset.test: hosted workflow has %s verifier script invocation(s), expected one canonical entrypoint\n' "$direct_verifier_scripts" >&2
  exit 1
fi

# Package parity: a stray file under skills/implementaudit/ must fail the build, because it
# would otherwise ship without a deliberate manifest update.
printf 'stray payload parity probe\n' > "$stray_file"
if bash scripts/build-release-asset.sh --check >/dev/null 2>&1; then
  printf 'release-asset.test: expected stray skills/implementaudit/ file to fail package parity\n' >&2
  exit 1
fi
rm -f "$stray_file"

out_dir="$tmp_parent/path with spaces"
mkdir -p "$out_dir"

bash scripts/build-release-asset.sh "$out_dir"

asset="$out_dir/IMPLEMENTAUDIT.skill"
[ -f "$asset" ] || {
  printf 'release-asset.test: missing asset\n' >&2
  exit 1
}

bash scripts/write-release-checksums.sh "$asset" "$out_dir/CHECKSUMS.txt"
bash scripts/write-release-checksums.sh --check "$asset" "$out_dir/CHECKSUMS.txt"

if command -v python >/dev/null 2>&1; then
  py_cmd=(python)
elif command -v python3 >/dev/null 2>&1; then
  py_cmd=(python3)
elif command -v py >/dev/null 2>&1; then
  py_cmd=(py -3)
else
  printf 'release-asset.test: python, python3, or py -3 is required\n' >&2
  exit 1
fi

"${py_cmd[@]}" - "$asset" <<'PY'
import json
import struct
import sys
import tempfile
import zipfile
from importlib.metadata import version
from pathlib import Path

import zopfli.zlib

asset = Path(sys.argv[1])

# Skill content must be at archive root (no skills/ prefix) for Claude import.
required = {
    "SKILL.md",
    "references/planning-depth.md",
    "references/phase-design.md",
    "references/goal-format.md",
    "references/transcript-contract.md",
    "references/continuity.md",
    "references/routing.md",
    "references/repo-state-comparison.md",
    "references/sidecars.md",
    "references/child-agents.md",
    "references/lean-operating-discipline.md",
    "references/audit-category-matrix.md",
    "references/audit-playbook.md",
    "references/plan-lifecycle.md",
    "references/terminology-integration.md",
    "scripts/check-respec-impact-set.sh",
    "scripts/check-duplication-parity.sh",
    "scripts/claim-run.sh",
    "scripts/detect-env.sh",
    "scripts/detect-stack.sh",
    "scripts/map-pin-chain.sh",
    "scripts/repo-state.sh",
    "scripts/summarize-repo.sh",
    "scripts/validate-audit-spec.sh",
    "scripts/validate-phase.sh",
    "scripts/validate-run-root.sh",
    "scripts/custody-append.sh",
    "scripts/lane-survivor-inventory.sh",
    "templates/ROADMAP.md",
    "templates/STATE.md",
    "templates/THINKING.md",
    "templates/phase-goal.txt",
    "templates/child-agent-report.md",
    "templates/final-report.md",
    "templates/read-only-plan.md",
    "templates/PROTOCOL.md",
    "templates/host-notes.md",
    "templates/respec-impact-set.md",
    "templates/sidecars.md",
    "templates/tools.md",
    "templates/context.md",
    ".claude-plugin/plugin.json",
    ".claude-plugin/marketplace.json",
}
blocked_parts = {
    ".git",
    ".IMPLEMENTAUDIT",
    "graphify-out",
    ".graphify",
    ".activegraph",
    "tmp",
    "temp",
    "dist",
}
blocked_names = {
    "graph.json",
    "quickstart_demo_run.db",
}
# Positive whitelist: only these top-level names are allowed at archive root.
# Anything else (repo scripts/, docs/, fixtures/, tests/, README.md, etc.) is rejected.
allowed_top_level = {"SKILL.md", "references", "scripts", "templates", ".claude-plugin"}

with zipfile.ZipFile(asset) as zf:
    names = set(zf.namelist())

    if version("zopfli") != "0.2.3.post1":
        raise SystemExit("canonical release build requires zopfli 0.2.3.post1")

    archive_bytes = asset.read_bytes()
    for info in zf.infolist():
        if info.compress_type != zipfile.ZIP_DEFLATED:
            raise SystemExit(f"non-DEFLATE package member: {info.filename}")
        header = archive_bytes[info.header_offset:info.header_offset + 30]
        if len(header) != 30 or header[:4] != b"PK\x03\x04":
            raise SystemExit(f"invalid local ZIP header: {info.filename}")
        filename_len, extra_len = struct.unpack_from("<HH", header, 26)
        payload_offset = info.header_offset + 30 + filename_len + extra_len
        observed = archive_bytes[payload_offset:payload_offset + info.compress_size]
        expected = zopfli.zlib.compress(
            zf.read(info.filename),
            numiterations=15,
            blocksplitting=1,
            blocksplittinglast=0,
            blocksplittingmax=15,
        )[2:-4]
        if observed != expected:
            raise SystemExit(
                f"member is not canonical Zopfli DEFLATE: {info.filename}"
            )

    # Regression guard: skills/implementaudit/SKILL.md must NOT be in the archive.
    # Claude import requires SKILL.md at archive root.
    if "skills/implementaudit/SKILL.md" in names:
        raise SystemExit(
            "REGRESSION: archive has skills/implementaudit/SKILL.md at nested path; "
            "SKILL.md must be at archive root for Claude import"
        )

    missing = sorted(required - names)
    if missing:
        raise SystemExit("missing asset entries: " + ", ".join(missing))

    top_level = {Path(name).parts[0] for name in names if Path(name).parts}
    unexpected = sorted(top_level - allowed_top_level)
    if unexpected:
        raise SystemExit("unexpected top-level paths in archive: " + ", ".join(unexpected))

    for name in names:
        parts = set(Path(name).parts)
        if parts & blocked_parts:
            raise SystemExit(f"blocked path included: {name}")
        if Path(name).name in blocked_names:
            raise SystemExit(f"blocked sidecar artifact included: {name}")
        if name.endswith((".log", ".tmp", ".db", ".sqlite", ".sqlite3", ".jsonl")):
            raise SystemExit(f"blocked suffix included: {name}")
        if name.startswith(".env"):
            raise SystemExit(f"environment file included: {name}")

    # Compression regression guard: every non-empty entry must be ZIP_DEFLATED.
    # ZipInfo defaults to compress_type=ZIP_STORED (0), which silently overrides
    # the ZipFile-level ZIP_DEFLATED default when writestr() receives a ZipInfo
    # object.  If build-release-asset.sh ever loses the explicit
    # `info.compress_type = zipfile.ZIP_DEFLATED` assignment, all entries revert
    # to stored and the asset bloats from ~60 KB to ~155 KB with no error raised.
    stored_entries = [
        info.filename
        for info in zf.infolist()
        if info.compress_type == zipfile.ZIP_STORED and info.file_size > 0
    ]
    if stored_entries:
        sample = ", ".join(stored_entries[:5])
        tail = " ..." if len(stored_entries) > 5 else ""
        raise SystemExit(
            f"compression regression: {len(stored_entries)} non-empty entries are "
            "ZIP_STORED (uncompressed). build-release-asset.sh must set "
            "info.compress_type = zipfile.ZIP_DEFLATED on each ZipInfo before "
            f"calling writestr(). Stored: {sample}{tail}"
        )

    # Total asset size guard: catches accidental ZIP_STORED regressions and
    # unintentional payload bloat.  Update this threshold only after confirming
    # entries remain ZIP_DEFLATED (the check above) and the payload growth is
    # intentional.  History: 120_000 set at v0.2.6.0 (~60 KB deflated payload,
    # ~2x headroom); raised to 130_000 for #48 (IA-ACTION-DEPTH) after the
    # v0.3.2.0 review-set integration plus the action-selection contract grew
    # the deflated asset to ~121 KB — growth verified intentional and deflated.
    # Raised to 140_000 for #35 (context-epoch continuity): the new packaged
    # references/continuity.md plus PROTOCOL/STATE contract text grew the
    # deflated asset to ~131 KB — growth verified intentional and deflated.
    asset_bytes = asset.stat().st_size
    # Owner policy authority: the v0.3.3.3 composed-candidate disposition
    # (2026-08-12) binds a 260,000-byte outer guard. Calibrations at or below
    # that bound require either the owner or a dedicated calibration lane;
    # implementation lanes may not self-raise the hard ceiling.
    OWNER_OUTER_BOUND_BYTES = 260_000
    MIN_HEADROOM_BYTES = 2_000
    CALIBRATION_QUANTUM_BYTES = 1_000
    CURRENT_CALIBRATION_AUTHORITY = "owner"
    ALLOWED_CALIBRATION_AUTHORITIES = {
        "owner", "dedicated-calibration-lane",
    }
    if CURRENT_CALIBRATION_AUTHORITY != "owner":
        raise SystemExit(
            "current calibration authority must name the owner-authorised fold-in"
        )

    # The composed /improve dominance fold-in plus the S3E W01 and W02
    # state-synthesis and controller-fencing controls measure 257,981 bytes.
    # This
    # owner-authorised R33 calibration keeps the smallest whole-1,000-byte
    # ceiling preserving at least 2,000 bytes of measured headroom: 260,000
    # leaves 2,019 bytes. The 260,000-byte outer bound is a guard, not a target.
    MAX_ASSET_BYTES = 260_000
    CURRENT_CALIBRATION_ASSET_BYTES = 257_981
    N06_BASELINE_ASSET_BYTES = 206_584
    N06_FINAL_P7_ASSET_BYTES = 215_126
    FULL_W1_FORECAST_BYTES = 144_730
    N02_EVIDENCE_CENSUS_FORECAST_BYTES = 151_898
    ISSUE_75_77_84_TRAIN_FORECAST_BYTES = 161_007
    N04_IDENTITY_INTEGRITY_FORECAST_BYTES = 202_593
    N05_CALIBRATION_MAIN_ASSET_BYTES = 202_679
    N05_FINAL_MEASURED_FORECAST_BYTES = 206_159
    FIRST_REJECTED_BYTES = MAX_ASSET_BYTES + 1

    def enforce_asset_budget_policy(max_bytes, measured_bytes, authority):
        if max_bytes > OWNER_OUTER_BOUND_BYTES:
            raise SystemExit(
                f"hard ceiling {max_bytes:,} bytes exceeds owner outer bound "
                f"{OWNER_OUTER_BOUND_BYTES:,} bytes"
            )
        if max_bytes % CALIBRATION_QUANTUM_BYTES:
            raise SystemExit(
                f"hard ceiling must use {CALIBRATION_QUANTUM_BYTES:,}-byte quantum"
            )
        headroom_bytes = max_bytes - measured_bytes
        if headroom_bytes < MIN_HEADROOM_BYTES:
            raise SystemExit(
                f"minimum headroom {MIN_HEADROOM_BYTES:,} bytes not met: "
                f"{headroom_bytes:,} bytes"
            )
        if authority not in ALLOWED_CALIBRATION_AUTHORITIES:
            raise SystemExit(
                f"calibration authority rejected: {authority!r}"
            )

    def enforce_calibrated_asset_policy(
            max_bytes, configured_measured_bytes, actual_bytes, authority):
        if configured_measured_bytes != actual_bytes:
            raise SystemExit(
                "configured measurement does not match actual asset bytes: "
                f"configured {configured_measured_bytes:,}, "
                f"actual {actual_bytes:,}"
            )
        expected_calibration = (
            (actual_bytes + MIN_HEADROOM_BYTES
             + CALIBRATION_QUANTUM_BYTES - 1)
            // CALIBRATION_QUANTUM_BYTES
            * CALIBRATION_QUANTUM_BYTES
        )
        if max_bytes != expected_calibration:
            raise SystemExit(
                "hard ceiling is not the smallest calibrated quantum for the "
                f"actual asset: expected {expected_calibration:,}, "
                f"got {max_bytes:,}"
            )
        enforce_asset_budget_policy(max_bytes, actual_bytes, authority)

    def expect_policy_rejection(fragment, values):
        try:
            enforce_asset_budget_policy(*values)
        except SystemExit as exc:
            assert fragment in str(exc), exc
        else:
            raise SystemExit(f"budget policy accepted {fragment}")

    for fragment, values in (
        ("outer bound", (261_000, N06_BASELINE_ASSET_BYTES, "owner")),
        ("minimum headroom", (208_000, N06_BASELINE_ASSET_BYTES, "owner")),
        ("calibration authority", (
            MAX_ASSET_BYTES, N06_BASELINE_ASSET_BYTES, "implementation-lane")),
    ):
        expect_policy_rejection(fragment, values)

    def expect_calibration_proxy_rejection(fragment, values):
        try:
            enforce_calibrated_asset_policy(*values)
        except SystemExit as exc:
            assert fragment in str(exc), exc
        else:
            raise SystemExit(f"calibration proxy accepted {fragment}")

    for fragment, values in (
        ("configured measurement", (
            MAX_ASSET_BYTES, CURRENT_CALIBRATION_ASSET_BYTES, 224_000,
            "owner")),
        ("configured measurement", (
            MAX_ASSET_BYTES, 224_000, asset_bytes, "owner")),
        ("configured measurement", (
            230_000, 227_500, asset_bytes, "owner")),
        ("smallest calibrated quantum", (
            MAX_ASSET_BYTES - CALIBRATION_QUANTUM_BYTES,
            asset_bytes, asset_bytes, "owner")),
    ):
        expect_calibration_proxy_rejection(fragment, values)
    for authority in ALLOWED_CALIBRATION_AUTHORITIES:
        enforce_asset_budget_policy(
            MAX_ASSET_BYTES, N06_BASELINE_ASSET_BYTES, authority)

    def enforce_asset_budget(candidate_bytes):
        if candidate_bytes <= MAX_ASSET_BYTES:
            return
        raise SystemExit(
            f"asset size {candidate_bytes:,} bytes exceeds the {MAX_ASSET_BYTES:,}-byte "
            "threshold. Verify ZIP_DEFLATED compression is applied (the check above), "
            "then update MAX_ASSET_BYTES in tests/release-asset.test.sh if the payload "
            "growth is intentional."
        )

    # Historical probes, the N05 calibration main asset, the measured final N05
    # stack, and the ceiling itself must be admitted. The first byte above the
    # calibrated ceiling must remain rejected. The actual artifact must satisfy
    # both the durable policy and the unchanged hard-ceiling enforcement.
    enforce_asset_budget(FULL_W1_FORECAST_BYTES)
    enforce_asset_budget(N02_EVIDENCE_CENSUS_FORECAST_BYTES)
    enforce_asset_budget(ISSUE_75_77_84_TRAIN_FORECAST_BYTES)
    enforce_asset_budget(N04_IDENTITY_INTEGRITY_FORECAST_BYTES)
    enforce_asset_budget(N05_CALIBRATION_MAIN_ASSET_BYTES)
    enforce_asset_budget(N05_FINAL_MEASURED_FORECAST_BYTES)
    enforce_asset_budget(N06_FINAL_P7_ASSET_BYTES)
    enforce_asset_budget(MAX_ASSET_BYTES)
    try:
        enforce_asset_budget(FIRST_REJECTED_BYTES)
    except SystemExit:
        pass
    else:
        raise SystemExit("asset above MAX_ASSET_BYTES was accepted")

    enforce_calibrated_asset_policy(
        MAX_ASSET_BYTES, CURRENT_CALIBRATION_ASSET_BYTES, asset_bytes,
        CURRENT_CALIBRATION_AUTHORITY
    )
    enforce_asset_budget(asset_bytes)
    print(
        "RELEASE_ASSET_BUDGET_POLICY=PASS "
        f"outer={OWNER_OUTER_BOUND_BYTES} ceiling={MAX_ASSET_BYTES} "
        f"minimum_headroom={MIN_HEADROOM_BYTES} measured={asset_bytes} "
        f"headroom={MAX_ASSET_BYTES - asset_bytes}"
    )

    with tempfile.TemporaryDirectory() as temp_dir:
        zf.extractall(temp_dir)
        root = Path(temp_dir)

        # SKILL.md must be at archive root.
        if not (root / "SKILL.md").is_file():
            raise SystemExit("SKILL.md must be at archive root")

        # skills/ subdirectory must not exist at archive root.
        if (root / "skills").exists():
            raise SystemExit(
                "REGRESSION: skills/ subdirectory at archive root; "
                "skill content must be at archive root for Claude import"
            )

        plugin = json.loads((root / ".claude-plugin/plugin.json").read_text())
        if plugin.get("version") != "0.3.3":
            raise SystemExit("expected plugin version 0.3.3")
        if plugin.get("skills") != "./":
            raise SystemExit(
                "expected plugin skills path ./ "
                "(SKILL.md at archive root for Claude import)"
            )
        if (root / "IMPLEMENTAUDIT.md").exists():
            raise SystemExit("root IMPLEMENTAUDIT.md must not be included")

print("release-asset.test: ok")
PY
