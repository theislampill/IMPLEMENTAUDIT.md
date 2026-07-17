#!/usr/bin/env bash
set -euo pipefail

# Long-running/background command contract (#2): the PROTOCOL section, the
# SKILL.md pointer, the state vocabulary, and the owner-amended
# state-transition fixtures (marker files -> resulting state token).

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

proto="skills/implementaudit/templates/PROTOCOL.md"
skill="skills/implementaudit/SKILL.md"

fail() { printf 'background-chain-contract: %s\n' "$*" >&2; exit 1; }

grep -q '^### Long-running and background commands' "$proto" \
  || fail "PROTOCOL section missing"
for tok in running succeeded failed aborted terminal-state-unverified \
    contaminated infrastructure-failed chain-status.txt chain.done \
    launch-intent.md transport-infrastructure; do
  grep -q -- "$tok" "$proto" || fail "PROTOCOL missing token: $tok"
done
# suspicion-not-proof amendment: producer countermeasures barred until
# origin classification
flat="$(tr '\n' ' ' < "$proto")"
printf '%s' "$flat" | grep -qi 'suspect infrastructure, not proof' \
  || fail "suspicion-not-proof rule missing"
printf '%s' "$flat" | grep -qi 'PROHIBITED until the run.s origin is classified' \
  || fail "producer-countermeasure prohibition missing"
printf '%s' "$flat" | grep -qi 'missing completion record is not a failure verdict' \
  || fail "missing-marker rule missing"

grep -q 'Long-running and background commands' "$skill" \
  || fail "SKILL.md pointer missing"

# --- state-transition fixtures (owner amendment): marker files on disk ----
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

# classify <chain-dir> [siblings-contaminated] -> the state token the
# contract assigns. This is the deterministic disposition rule from the
# PROTOCOL section, exercised as fixtures.
classify() {
  d="$1"
  last="$(tail -n 1 "$d/chain-status.txt" 2>/dev/null || true)"
  case "$last" in
    *infrastructure-failed*) printf 'infrastructure-failed'; return ;;
    *contaminated*)          printf 'contaminated'; return ;;
    *aborted*)               printf 'aborted'; return ;;
  esac
  if [ ! -f "$d/chain.done" ]; then
    printf 'terminal-state-unverified'; return
  fi
  case "$last" in
    *"exit=0"*) printf 'succeeded' ;;
    *"exit="*)  printf 'failed' ;;
    *)          printf 'terminal-state-unverified' ;;
  esac
}

mk() { mkdir -p "$tmp/$1"; printf 'cmd\n' > "$tmp/$1/launch-intent.md"; }

# running -> succeeded (marker present, exit 0 recorded)
mk ok; printf 'running\nexit=0\n' > "$tmp/ok/chain-status.txt"
: > "$tmp/ok/chain.done"
[ "$(classify "$tmp/ok")" = succeeded ] || fail "fixture ok != succeeded"

# running -> failed (nonzero exit recorded + marker present)
mk bad; printf 'running\nexit=3\n' > "$tmp/bad/chain-status.txt"
: > "$tmp/bad/chain.done"
[ "$(classify "$tmp/bad")" = failed ] || fail "fixture bad != failed"

# running -> aborted (owned-tree kill recorded)
mk ab; printf 'running\naborted owned-tree-kill pid=123\n' \
  > "$tmp/ab/chain-status.txt"
[ "$(classify "$tmp/ab")" = aborted ] || fail "fixture ab != aborted"

# running -> terminal-state-unverified (no completion marker)
mk tsu; printf 'running\n' > "$tmp/tsu/chain-status.txt"
[ "$(classify "$tmp/tsu")" = terminal-state-unverified ] \
  || fail "fixture tsu != terminal-state-unverified"

# aborted -> contaminated (sibling contamination recorded)
mk cont; printf 'running\naborted\ncontaminated siblings=lane-B\n' \
  > "$tmp/cont/chain-status.txt"
[ "$(classify "$tmp/cont")" = contaminated ] \
  || fail "fixture cont != contaminated"

# infrastructure-failed classification (recorded evidence, e.g. 0xC0000142)
mk infra
printf 'running\ninfrastructure-failed evidence=0xC0000142 cross-lane\n' \
  > "$tmp/infra/chain-status.txt"
[ "$(classify "$tmp/infra")" = infrastructure-failed ] \
  || fail "fixture infra != infrastructure-failed"

printf 'background-chain-contract: ok (section + vocabulary + 6 transition fixtures)\n'
