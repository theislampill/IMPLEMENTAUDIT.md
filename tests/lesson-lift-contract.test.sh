#!/usr/bin/env bash
set -euo pipefail

# Lesson-lift routing record (#13): the PROTOCOL contract text and the
# scorer's five acceptance fixtures + negative control.

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

proto="skills/implementaudit/templates/PROTOCOL.md"
scorer="skills/implementaudit/scripts/check-lesson-lift.sh"
fx="fixtures/lesson-lift"
fail() { printf 'lesson-lift-contract: %s\n' "$*" >&2; exit 1; }

flat="$(tr '\n' ' ' < "$proto")"
printf '%s' "$flat" | grep -qi 'Lesson-lift routing record' \
  || fail "PROTOCOL missing the Lesson-lift routing record subsection"
printf '%s' "$flat" | grep -qi 'produces exactly ONE canonical lift record' \
  || fail "unification (one canonical record) missing"
printf '%s' "$flat" | grep -qi 'closure must never claim .*recurrence' \
  || fail "closure-must-not-claim-prevention rule missing"
printf '%s' "$flat" | grep -qi 'cheap to redo by hand.*insufficient' \
  || fail "insufficient-reason rule missing"
printf '%s' "$flat" | grep -qi \
  'mechanical destination is unavailable.*observed-pass activation.*executed-check evidence' \
  || fail "mechanical destination evidence gate missing"
printf '%s' "$flat" | grep -qi \
  'never pair a mechanical destination with.*unverified' \
  || fail "mechanical/unverified prohibition missing"

pass_case() {
  bash "$scorer" "$fx/$1" --repo-root "$repo_root" >/dev/null 2>&1 \
    || fail "$1 expected PASS"
}
fail_case() {
  if bash "$scorer" "$fx/$1" --repo-root "$repo_root" >/dev/null 2>&1; then
    fail "$1 expected FAIL"
  fi
}

fail_case qualifying-no-record-FAIL.md
fail_case checker-active-mismatch-FAIL.md
fail_case easy-redo-noreason-FAIL.md
fail_case prevented-claim-FAIL.md
fail_case remediation-unenforced-FAIL.md
fail_case checker-active-no-red-FAIL.md
pass_case reasoned-nolift-PASS.md
pass_case oneoff-typo-PASS.md
pass_case checker-active-ok-PASS.md
pass_case adopted-unenforced-not-cited-PASS.md

# --- Fable review of PR #29: adversarial regressions -----------------------
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
adv_fail() {  # label, record-content
  printf '%s\n' "$2" > "$tmp/adv.md"
  if bash "$scorer" "$tmp/adv.md" --repo-root "$repo_root" >/dev/null 2>&1; then
    fail "$1 expected FAIL"
  fi
}
adv_pass() {
  printf '%s\n' "$2" > "$tmp/adv.md"
  bash "$scorer" "$tmp/adv.md" --repo-root "$repo_root" >/dev/null 2>&1 \
    || fail "$1 expected PASS"
}

lift_rec='IMPLEMENTAUDIT_PHASE_VERIFY
Hansei: governing-rule evidence (qualifying trigger).
Lesson-lift: lesson observed = x; decision: lift; reason = y; destination: checker or deterministic test; target: tests/andon-class-contract.test.sh; authority: repo; encoding written: yes; mechanically active: yes; installed current: n/a; recurrence class: regression.
AUDIT_COMPLETE'

# Hidden wordings of the forbidden prevention claim still fail.
adv_fail "hidden prevented-variant (worded)" \
  "$lift_rec
The recurrence has been prevented by this encoding."
adv_fail "hidden prevented-variant (prevents recurrence)" \
  "$lift_rec
This encoding prevents recurrence of the class."

# Two Lesson-lift records in one closure are competing records.
adv_fail "duplicate competing records" \
'IMPLEMENTAUDIT_PHASE_VERIFY
Hansei: qualifying trigger: recurrence.
Lesson-lift: lesson observed = a; decision: lift; reason = z; destination: project docs; authority: repo.
Lesson-lift: lesson observed = a; decision: no-lift; reason = w; destination: no lift; authority: n/a.
AUDIT_COMPLETE'

# A no-lift decision with an EMPTY reason is a bare no.
adv_fail "empty no-lift reason" \
'IMPLEMENTAUDIT_PHASE_VERIFY
Hansei: qualifying trigger: recurrence.
Lesson-lift: lesson observed = a; decision: no-lift; reason = ; destination: no lift; authority: n/a.
AUDIT_COMPLETE'

# A one-off disposition mentioning "recurrence" in its own line must NOT
# be forced into lift ceremony (bounded trigger).
adv_pass "one-off disposition mentioning recurrence" \
'IMPLEMENTAUDIT_PHASE_VERIFY
No-lift: one-off typo; no recurrence expected.
AUDIT_COMPLETE'

# --- #80 host-error memoization controls -----------------------------------
quirk_root="$tmp/quirk-repo"
mkdir -p "$quirk_root/.IMPLEMENTAUDIT"

quirk_pass() {
  local label="$1" fixture="$2"
  bash "$scorer" "$fx/$fixture" --repo-root "$quirk_root" >/dev/null 2>&1 \
    || fail "$label expected PASS"
}
quirk_fail() {
  local label="$1" fixture="$2" expected="$3" out
  if out="$(bash "$scorer" "$fx/$fixture" --repo-root "$quirk_root" 2>&1)"; then
    fail "$label expected FAIL"
  fi
  printf '%s\n' "$out" | grep -Fq "$expected" \
    || fail "$label missing diagnostic: $expected"
}

quirk_pass "first occurrence" quirk-first-occurrence-PASS.md
quirk_pass "distinct signatures" quirk-two-distinct-classes-PASS.md
quirk_pass "duplicate occurrence id" quirk-duplicate-occurrence-PASS.md
quirk_pass "documented refusal" quirk-documented-refusal-PASS.md
quirk_pass "outside Andon log" quirk-outside-andon-PASS.md
quirk_fail "wrong class" quirk-wrong-class-FAIL.md \
  "environment-quirk discriminator must use Class transport-infrastructure"
quirk_fail "missing discriminator" quirk-missing-discriminator-FAIL.md \
  "second distinct occurrence must use Blocker: environment-quirk"
quirk_fail "third unrecorded" quirk-third-unrecorded-FAIL.md \
  "reached 2 distinct occurrences without Workaround: or Not memoized:"
quirk_fail "empty refusal" quirk-empty-refusal-FAIL.md \
  "Not memoized: requires a nonempty reason"
quirk_fail "empty workaround" quirk-empty-workaround-FAIL.md \
  "Workaround: requires nonempty text"

printf '%s\n' \
  '# IMPLEMENTAUDIT Host Notes' \
  '2026-08-07T02:00:00Z | parsererror empty pipe element is not allowed | use a temporary script file | first-seen-run: test' \
  > "$quirk_root/.IMPLEMENTAUDIT/host-notes.md"
quirk_pass "second occurrence" quirk-second-occurrence-PASS.md
quirk_pass "path containing spaces" quirk-path-spaces-PASS.md
quirk_pass "drive forward-slash path" quirk-drive-forward-slash-PASS.md

printf '%s\n' \
  '# IMPLEMENTAUDIT Host Notes' \
  '2026-08-07T02:00:00Z | unicodeencodeerror charmap codec cant encode characters | set process encoding | first-seen-run: test' \
  > "$quirk_root/.IMPLEMENTAUDIT/host-notes.md"
quirk_pass "workaround spelling variance" quirk-spelling-variance-PASS.md

printf '%s\n' \
  '# IMPLEMENTAUDIT Host Notes' \
  '2026-08-07T02:00:00Z | parsererror empty pipe element is not allowed | first | first-seen-run: test' \
  '2026-08-07T02:01:00Z | parsererror empty pipe element is not allowed | duplicate | first-seen-run: test' \
  > "$quirk_root/.IMPLEMENTAUDIT/host-notes.md"
quirk_fail "duplicate host-note row" quirk-second-occurrence-PASS.md \
  "must have exactly one host-note row"

IMPLEMENTAUDIT_QUIRK_THRESHOLD=0 bash "$scorer" \
  "$fx/quirk-third-unrecorded-FAIL.md" --repo-root "$quirk_root" >/dev/null \
  || fail "threshold 0 must disable host-error memoization"
if IMPLEMENTAUDIT_QUIRK_THRESHOLD=3 bash "$scorer" \
  "$fx/quirk-third-unrecorded-FAIL.md" --repo-root "$quirk_root" >/dev/null 2>&1; then
  fail "threshold 3 must be rejected; only 0 or 2 is governed"
fi

# detect-env names the repo-level path and counts data rows without mutation.
detect_repo="$tmp/detect-repo"
mkdir -p "$detect_repo/.IMPLEMENTAUDIT"
git -C "$detect_repo" init -q
detect_common_dir="$(git -C "$detect_repo" rev-parse --path-format=absolute --git-common-dir)"
detect_shared_root="$(cd "$(dirname "$detect_common_dir")" && pwd -P)"
printf '%s\n' \
  '# IMPLEMENTAUDIT Host Notes' \
  '2026-08-07T02:00:00Z | first signature | first workaround | first-seen-run: a' \
  '2026-08-07T02:01:00Z | second signature | second workaround | first-seen-run: b' \
  > "$detect_repo/.IMPLEMENTAUDIT/host-notes.md"
detect_out="$(cd "$detect_repo" && bash "$repo_root/skills/implementaudit/scripts/detect-env.sh")"
printf '%s\n' "$detect_out" | grep -Fq "host_notes_path=$detect_shared_root/.IMPLEMENTAUDIT/host-notes.md" \
  || fail "detect-env did not reveal the repo-level host-notes path"
printf '%s\n' "$detect_out" | grep -Fq 'host_notes_count=2' \
  || fail "detect-env did not count host-note rows"

# The host-note owner is shared across linked worktrees through Git's common
# directory, not derived from each worktree's distinct top-level path.
printf '%s\n' \
  '2026-08-07T02:02:00Z | parsererror empty pipe element is not allowed | use a temporary script file | first-seen-run: c' \
  >> "$detect_repo/.IMPLEMENTAUDIT/host-notes.md"
printf '%s\n' init > "$detect_repo/README.md"
git -C "$detect_repo" add README.md
git -C "$detect_repo" -c user.name=test -c user.email=test@example.invalid commit -qm init
detect_sibling="$tmp/detect-sibling"
git -C "$detect_repo" worktree add -q -b sibling "$detect_sibling"
sibling_out="$(cd "$detect_sibling" && bash "$repo_root/skills/implementaudit/scripts/detect-env.sh")"
printf '%s\n' "$sibling_out" | grep -Fq "host_notes_path=$detect_shared_root/.IMPLEMENTAUDIT/host-notes.md" \
  || fail "detect-env did not share the host-notes path across sibling worktrees"
if ! shared_check_out="$(bash "$scorer" "$fx/quirk-second-occurrence-PASS.md" --repo-root "$detect_sibling" 2>&1)"; then
  fail "checker did not resolve the shared host-note owner from a sibling worktree: $shared_check_out"
fi

# F5: preserve the one #101 Graphify limitation and admit no new host trivia.
payload="skills/implementaudit"
for forbidden in cp1252 PYTHONIOENCODING MAX_PATH; do
  if grep -RFiq -- "$forbidden" "$payload"; then
    fail "payload gained forbidden host trivia: $forbidden"
  fi
done
heredoc_hits="$(grep -RFi -- 'heredoc' "$payload" || true)"
[ "$(printf '%s\n' "$heredoc_hits" | grep -c .)" -eq 1 ] \
  || fail "payload must preserve exactly one pre-existing heredoc occurrence"
printf '%s\n' "$heredoc_hits" | grep -Fq \
  'skills/implementaudit/references/lean-operating-discipline.md:- embedded-language code (such as heredoc Python) is not extracted;' \
  || fail "the sole heredoc occurrence is not the exact #101 baseline"

printf 'lesson-lift-contract: ok (contract + enforcement-state + 5 adversarial + #80 F1-F6)\n'
