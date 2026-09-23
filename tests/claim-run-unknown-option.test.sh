#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
helper="${IMPLEMENTAUDIT_CLAIM_HELPER:-$repo_root/skills/implementaudit/scripts/claim-run.sh}"

failures=0
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

init_repo() {
  local repo="$1"
  mkdir -p "$repo"
  git -C "$repo" init -q
  git -C "$repo" config user.email claim-run-unknown-option@example.invalid
  git -C "$repo" config user.name claim-run-unknown-option-test
  git -C "$repo" commit --allow-empty -qm fixture
}

snapshot_runs() {
  local repo="$1" runs="$1/.IMPLEMENTAUDIT/runs" path
  if [ ! -d "$runs" ]; then
    printf 'ABSENT\n'
    return
  fi
  (
    cd "$runs"
    while IFS= read -r -d '' path; do
      if [ -L "$path" ]; then
        printf 'L\t%s\t%s\n' "$path" "$(readlink "$path")"
      elif [ -d "$path" ]; then
        printf 'D\t%s\n' "$path"
      elif [ -f "$path" ]; then
        printf 'F\t%s\t%s\t%s\n' \
          "$path" "$(wc -c < "$path" | tr -d ' ')" \
          "$(sha256sum "$path" | cut -d' ' -f1)"
      else
        printf 'O\t%s\n' "$path"
      fi
    done < <(find . -mindepth 1 -print0 | LC_ALL=C sort -z)
  )
}

snapshot_refs() {
  git -C "$1" for-each-ref \
    --format='%(refname)%09%(objectname)' refs/implementaudit | LC_ALL=C sort
}

check_unknown_rejection() {
  local label="$1" option="$2" repo="$tmp/$1"
  local before_runs before_refs after_runs after_refs output rc
  init_repo "$repo"
  before_runs="$(snapshot_runs "$repo")"
  before_refs="$(snapshot_refs "$repo")"

  if output="$(cd "$repo" && bash "$helper" "$option" 2>&1)"; then
    rc=0
  else
    rc=$?
  fi

  after_runs="$(snapshot_runs "$repo")"
  after_refs="$(snapshot_refs "$repo")"
  if [ "$rc" -eq 0 ]; then
    printf 'claim-run-unknown-option.test: %s was accepted and reached effect-capable claim creation: %s\n' \
      "$option" "$output" >&2
    failures=$((failures + 1))
  fi
  if [ "$before_runs" != "$after_runs" ]; then
    printf 'claim-run-unknown-option.test: %s changed the exact run-root population/content\n' \
      "$option" >&2
    failures=$((failures + 1))
  fi
  if [ "$before_refs" != "$after_refs" ]; then
    printf 'claim-run-unknown-option.test: %s changed implementaudit refs\n' \
      "$option" >&2
    failures=$((failures + 1))
  fi
}

check_unknown_rejection help --help
check_unknown_rejection unrelated --unknown-claim-control

positive_repo="$tmp/positive"
init_repo "$positive_repo"
positional="$(
  cd "$positive_repo"
  IMPLEMENTAUDIT_BASE=.IMPLEMENTAUDIT/runs bash "$helper" 'Valid positional task slug' 2>/dev/null
)"
case "$positional" in
  .IMPLEMENTAUDIT/runs/valid-positional-task-slug-*) ;;
  *)
    printf 'claim-run-unknown-option.test: valid positional task slug was not preserved: %s\n' \
      "$positional" >&2
    exit 1
    ;;
esac
[ -f "$positive_repo/$positional/.claimed" ] || {
  printf 'claim-run-unknown-option.test: positional claim sentinel is missing\n' >&2
  exit 1
}

micro="$(
  cd "$positive_repo"
  IMPLEMENTAUDIT_BASE=.IMPLEMENTAUDIT/runs bash "$helper" --micro 'Supported micro claim' 2>/dev/null
)"
grep -qx 'mode=micro' "$positive_repo/$micro/.claimed" || {
  printf 'claim-run-unknown-option.test: --micro did not preserve the micro claim path\n' >&2
  exit 1
}

controller_repo="$tmp/current-controller"
init_repo "$controller_repo"
controller_run="$(
  cd "$controller_repo"
  IMPLEMENTAUDIT_BASE=.IMPLEMENTAUDIT/runs \
    bash "$helper" --controller focused-controller 'Controller fixture' 2>/dev/null
)"
for promised in STATE.md PROTOCOL.md ROADMAP.md THINKING.md sidecars.md tools.md context.md; do
  printf 'controller fixture\n' > "$controller_repo/$controller_run/$promised"
done
before_current_runs="$(snapshot_runs "$controller_repo")"
before_current_refs="$(snapshot_refs "$controller_repo")"
current="$(cd "$controller_repo" && bash "$helper" --current-controller focused-controller)"
after_current_runs="$(snapshot_runs "$controller_repo")"
after_current_refs="$(snapshot_refs "$controller_repo")"
[ "${current%%$'\t'*}" = focused-controller ] || {
  printf 'claim-run-unknown-option.test: --current-controller did not resolve the fixture\n' >&2
  exit 1
}
[ "$before_current_runs" = "$after_current_runs" ] || {
  printf 'claim-run-unknown-option.test: --current-controller changed run-root content\n' >&2
  exit 1
}
[ "$before_current_refs" = "$after_current_refs" ] || {
  printf 'claim-run-unknown-option.test: --current-controller changed refs\n' >&2
  exit 1
}
[ -f "$controller_repo/$controller_run/.claimed" ] || {
  printf 'claim-run-unknown-option.test: controller fixture claim is missing\n' >&2
  exit 1
}

if [ "$failures" -ne 0 ]; then
  printf 'claim-run-unknown-option.test: FAIL (%s discriminator failures)\n' "$failures" >&2
  exit 1
fi

printf 'claim-run-unknown-option.test: ok\n'
