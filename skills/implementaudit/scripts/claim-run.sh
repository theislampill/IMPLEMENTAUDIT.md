#!/usr/bin/env bash
# claim-run.sh - atomically claim a native IMPLEMENTAUDIT run root.
#
# The helper is intentionally small and side-effect bounded: it creates the
# run-root directory and its claim metadata under IMPLEMENTAUDIT_BASE, then
# prints that path. It does not write roadmap/state/protocol files, inspect
# source files, install tools, index sidecars, or start execution.

set -u

base="${IMPLEMENTAUDIT_BASE:-.IMPLEMENTAUDIT/runs}"

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

mkdir -p "$base" || {
  printf "claim-run.sh: cannot create base dir '%s'\n" "$base" >&2
  exit 1
}

run_root="$(mktemp -d "$base/${slug}-XXXXXX" 2>/dev/null)" || {
  printf "claim-run.sh: mktemp failed to claim a run dir under '%s'\n" "$base" >&2
  exit 1
}

claimed_at_utc="$(date -u '+%Y-%m-%dT%H:%M:%SZ')"
if ! printf 'claimed_at_utc=%s\nmode=%s\ntemplates=%s\n' \
  "$claimed_at_utc" "$mode" "$template_set" > "$run_root/.claimed"; then
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
