#!/usr/bin/env bash
# claim-run.sh - atomically claim a native IMPLEMENTAUDIT run root.
#
# The helper is intentionally small and side-effect bounded: it creates only the
# run-root directory under IMPLEMENTAUDIT_BASE, then prints that path. It does
# not write roadmap/state/protocol files, inspect source files, install tools,
# index sidecars, or start execution.

set -u

base="${IMPLEMENTAUDIT_BASE:-.IMPLEMENTAUDIT/runs}"

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

# Advisory only (this helper never mutates repo config): in target repos that
# do not ignore the run-root base, run artifacts would appear as untracked
# changes in commits and evidence scans.
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  if ! git check-ignore -q "$base" 2>/dev/null; then
    printf 'claim-run: note: %s is not gitignored here; consider adding ".IMPLEMENTAUDIT/" to .git/info/exclude (local-only) so run artifacts stay out of commits and evidence\n' "$base" >&2
  fi
fi

printf '%s\n' "$run_root"
