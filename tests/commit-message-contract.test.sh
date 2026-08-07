#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

checker="skills/implementaudit/scripts/repo-state.sh"

fail() {
  printf 'commit-message-contract: %s\n' "$*" >&2
  exit 1
}

expect_pass() {
  local fixture="$1"
  shift
  bash "$checker" commit-message "$fixture" "$@" >/dev/null \
    || fail "$fixture expected PASS"
}

expect_fail() {
  local fixture="$1" expected="$2"
  shift 2
  local output status
  set +e
  output="$(bash "$checker" commit-message "$fixture" "$@" 2>&1)"
  status=$?
  set -e
  [ "$status" -eq 1 ] || fail "$fixture expected exit 1, got $status: $output"
  [ "$output" = "$expected" ] \
    || fail "$fixture unexpected diagnostic: $output"
}

expect_fail fixtures/commit-message/behavior-change-empty-body-FAIL.md \
  'repo-state: commit-message Class B requires a non-empty body'
expect_pass fixtures/commit-message/mechanical-regen-slim-PASS.md
expect_pass fixtures/commit-message/real-window-best-body-PASS.md --ledger-linked
expect_fail fixtures/commit-message/finding-close-no-anchor-FAIL.md \
  'repo-state: commit-message Class B requires an evidence anchor' \
  --ledger-linked
expect_pass fixtures/commit-message/decision-record-PASS.md --ledger-linked
expect_fail fixtures/commit-message/decision-record-empty-body-FAIL.md \
  'repo-state: commit-message Class B requires a non-empty body' \
  --ledger-linked
expect_fail fixtures/commit-message/unparseable-subject-slim-FAIL.md \
  'repo-state: commit-message Class B requires a non-empty body'
expect_pass fixtures/commit-message/docs-typo-slim-PASS.md
expect_pass fixtures/commit-message/behavior-change-three-line-body-PASS.md
expect_pass fixtures/commit-message/codename-unexpanded-PASS.md
expect_pass fixtures/commit-message/reviewer-slots-unscored-PASS.md
expect_pass fixtures/commit-message/mechanical-with-long-body-PASS.md
expect_fail fixtures/commit-message/ledger-linked-no-linkage-FAIL.md \
  'repo-state: commit-message --ledger-linked requires finding, issue, ledger-row, or Andon linkage' \
  --ledger-linked
expect_fail fixtures/commit-message/breaking-subject-empty-body-FAIL.md \
  'repo-state: commit-message Class B requires a non-empty body'
expect_fail fixtures/commit-message/breaking-body-no-anchor-FAIL.md \
  'repo-state: commit-message Class B requires an evidence anchor'
expect_fail fixtures/commit-message/placeholder-anchor-FAIL.md \
  'repo-state: commit-message Class B requires an evidence anchor'
expect_fail fixtures/commit-message/external-url-not-anchor-FAIL.md \
  'repo-state: commit-message Class B requires an evidence anchor'
expect_fail fixtures/commit-message/ordinary-hex-word-not-anchor-FAIL.md \
  'repo-state: commit-message Class B requires an evidence anchor'
expect_fail fixtures/commit-message/bare-count-not-anchor-FAIL.md \
  'repo-state: commit-message Class B requires an evidence anchor'
expect_fail fixtures/commit-message/occurrences-ratio-not-anchor-FAIL.md \
  'repo-state: commit-message Class B requires an evidence anchor'
expect_fail fixtures/commit-message/landed-placeholder-not-anchor-FAIL.md \
  'repo-state: commit-message Class B requires an evidence anchor'
expect_fail fixtures/commit-message/test-placeholder-not-anchor-FAIL.md \
  'repo-state: commit-message Class B requires an evidence anchor'
expect_fail fixtures/commit-message/andon-not-applicable-linkage-FAIL.md \
  'repo-state: commit-message --ledger-linked requires finding, issue, ledger-row, or Andon linkage' \
  --ledger-linked
expect_pass fixtures/commit-message/linkage-ledger-row-PASS.md --ledger-linked
expect_pass fixtures/commit-message/linkage-andon-PASS.md --ledger-linked
expect_pass fixtures/commit-message/occurrences-anchor-PASS.md
expect_pass fixtures/commit-message/named-anchor-PASS.md
expect_pass fixtures/commit-message/hunk-anchor-PASS.md

printf 'commit-message-contract: ok (28 fixtures)\n'
