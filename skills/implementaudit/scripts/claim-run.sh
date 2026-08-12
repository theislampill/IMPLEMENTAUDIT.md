#!/usr/bin/env bash
# claim-run.sh - atomically claim a native IMPLEMENTAUDIT run root.
#
# The helper is intentionally small and side-effect bounded: it creates the
# run-root directory and its claim metadata under IMPLEMENTAUDIT_BASE, then
# prints that path. It does not write roadmap/state/protocol files, inspect
# source files, install tools, index sidecars, or start execution.

set -u

base="${IMPLEMENTAUDIT_BASE:-.IMPLEMENTAUDIT/runs}"

reject_coordination_reparse() {
  local candidate="$1"
  [ ! -L "$candidate" ] || return 1
  if [ -e "$candidate" ] && command -v cmd.exe >/dev/null 2>&1 && command -v cygpath >/dev/null 2>&1; then
    local candidate_win
    candidate_win="$(cygpath -aw "$candidate")" || return 1
    if MSYS2_ARG_CONV_EXCL='*' cmd.exe /d /c fsutil reparsepoint query "$candidate_win" >/dev/null 2>&1; then
      return 1
    fi
  fi
  return 0
}

mode=full
if [ "${1:-}" = "--micro" ]; then
  mode=micro
  shift
fi

case "$mode" in
  full) template_set="STATE.md PROTOCOL.md ROADMAP.md THINKING.md sidecars.md tools.md context.md" ;;
  micro) template_set="STATE.md" ;;
esac

slug="$(printf '%s' "${1:-}" \
  | tr '[:upper:]' '[:lower:]' \
  | tr -c 'a-z0-9' '-' \
  | sed -E 's/-+/-/g; s/^-//; s/-$//' \
  | cut -c1-48 \
  | sed -E 's/-$//')"
[ -n "$slug" ] || slug="run"

if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  preflight_repo="$(git rev-parse --path-format=absolute --show-toplevel)" || exit 1
  reject_coordination_reparse "$preflight_repo/.IMPLEMENTAUDIT" || {
    printf "claim-run.sh: run and coordination custody contains a symlink or reparse point: '%s/.IMPLEMENTAUDIT'\n" "$preflight_repo" >&2
    exit 1
  }
  gate_dir="$preflight_repo/.IMPLEMENTAUDIT/.r36-locks"
  gate="$gate_dir/namespace.gate"
  reject_coordination_reparse "$gate_dir" || {
    printf "claim-run.sh: governed-writer namespace custody contains a symlink or reparse point: '%s'\n" "$gate_dir" >&2
    exit 1
  }
  mkdir -p "$gate_dir" || exit 1
  if [ ! -e "$gate" ]; then
    ( set -C; printf '\0' > "$gate" ) 2>/dev/null || true
  fi
  [ -f "$gate" ] && [ ! -L "$gate" ] && [ "$(wc -c < "$gate" | tr -d ' ')" = 1 ] \
    && [ "$(find "$gate" -maxdepth 0 -links 1 -print 2>/dev/null)" = "$gate" ] || {
    printf "claim-run.sh: governed-writer namespace gate is unsafe: '%s'\n" "$gate" >&2
    exit 1
  }
fi

mkdir -p "$base" || {
  printf "claim-run.sh: cannot create base dir '%s'\n" "$base" >&2
  exit 1
}

run_root="$(mktemp -d "$base/${slug}-XXXXXX" 2>/dev/null)" || {
  printf "claim-run.sh: mktemp failed to claim a run dir under '%s'\n" "$base" >&2
  exit 1
}

claimed_at_utc="$(date -u '+%Y-%m-%dT%H:%M:%SZ')"
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  # Keep producer and strict consumer in Git's native absolute path domain.
  # In Git Bash, `pwd -P` may spell the worktree as /c/... while Git and the
  # host Python runtime use C:/...; mixing those domains makes an own-generated
  # claim fail strict custody despite naming the same worktree.
  claim_repo="$(git rev-parse --path-format=absolute --show-toplevel)" || exit 1
  claim_common="$(git rev-parse --path-format=absolute --git-common-dir)" || exit 1
  claim_id="$(LC_ALL=C od -An -N16 -tx1 /dev/urandom | tr -d ' \n')"
  claim_name="$(basename "$run_root")"
  { printf 'schema=implementaudit.run-claim.v2\nclaim_id=%s\nclaimed_at_utc=%s\nmode=%s\ntemplates=%s\n' "$claim_id" "$claimed_at_utc" "$mode" "$template_set"; printf 'repo_root=%s\ngit_common_dir=%s\nrun_base=%s\nrun_root=%s\nrun_name=%s\n' "$claim_repo" "$claim_common" "$base" "$run_root" "$claim_name"; } > "$run_root/.claimed"
else
  printf 'claimed_at_utc=%s\nmode=%s\ntemplates=%s\n' "$claimed_at_utc" "$mode" "$template_set" > "$run_root/.claimed"
fi
if [ ! -f "$run_root/.claimed" ]; then
  printf "claim-run.sh: cannot write claim sentinel '%s/.claimed'\n" "$run_root" >&2
  rmdir "$run_root" 2>/dev/null || true
  exit 1
fi

# Claiming remains non-blocking so explicitly parallel work can declare itself.
# List siblings that need COMPLETE, HANDOFF, SUPERSEDED_BY, or PARALLEL state.
for sibling in "$base"/*; do
  [ -d "$sibling" ] || continue
  [ "$sibling" = "$run_root" ] && continue
  sibling_state="$sibling/STATE.md"
  if [ ! -f "$sibling_state" ] || ! grep -Eq \
    '^(AUDIT_COMPLETE|IMPLEMENTAUDIT_RUN_COMPLETE|AUDIT_HANDOFF|ANDON_HANDOFF|COMPLETE|HANDOFF|SUPERSEDED_BY:[[:space:]].+|PARALLEL:[[:space:]].+)$' \
    "$sibling_state"; then
    printf 'claim-run: undispositioned sibling root: %s\n' "$sibling" >&2
  fi
done

# Advisory only (this helper never mutates repo config): in target repos that
# do not ignore the run-root base, run artifacts would appear as untracked
# changes in commits and evidence scans.
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  if ! git check-ignore -q "$base" 2>/dev/null; then
    printf 'claim-run: note: %s is not gitignored here; consider adding ".IMPLEMENTAUDIT/" to .git/info/exclude (local-only) so run artifacts stay out of commits and evidence\n' "$base" >&2
  fi
fi

printf '%s\n' "$run_root"
