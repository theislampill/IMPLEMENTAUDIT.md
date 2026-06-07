#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
helper="$repo_root/skills/scripts/claim-run.sh"

[ -f "$helper" ] || {
  printf 'claim-run.test: missing helper: %s\n' "$helper" >&2
  exit 1
}

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

work="$tmp/work with spaces"
mkdir -p "$work"
cd "$work"

first="$(bash "$helper" "Audit release asset boundary" 2>/dev/null)"
second="$(bash "$helper" "Audit release asset boundary" 2>/dev/null)"

[ -d "$first" ] || {
  printf 'claim-run.test: first run root not created\n' >&2
  exit 1
}
[ -d "$second" ] || {
  printf 'claim-run.test: second run root not created\n' >&2
  exit 1
}
[ "$first" != "$second" ] || {
  printf 'claim-run.test: duplicate run roots for same slug\n' >&2
  exit 1
}

case "$first" in
  .IMPLEMENTAUDIT/runs/audit-release-asset-boundary-*) ;;
  *)
    printf 'claim-run.test: unexpected default run root: %s\n' "$first" >&2
    exit 1
    ;;
esac

custom_base="$tmp/custom base"
custom="$(IMPLEMENTAUDIT_BASE="$custom_base" bash "$helper" '../../Unsafe Name !!' 2>/dev/null)"
[ -d "$custom" ] || {
  printf 'claim-run.test: custom-base run root not created\n' >&2
  exit 1
}
case "$(basename "$custom")" in
  unsafe-name-*) ;;
  *)
    printf 'claim-run.test: slug was not sanitized: %s\n' "$custom" >&2
    exit 1
    ;;
esac

parallel_dir="$tmp/parallel"
mkdir -p "$parallel_dir"
N=16
i=1
while [ "$i" -le "$N" ]; do
  (
    cd "$work"
    bash "$helper" "same concurrent task" >"$parallel_dir/$i" 2>/dev/null
  ) &
  i=$((i + 1))
done
wait

emitted="$(cat "$parallel_dir"/* | grep -c .)"
unique="$(cat "$parallel_dir"/* | sort -u | grep -c .)"
[ "$emitted" = "$N" ] && [ "$unique" = "$N" ] || {
  printf 'claim-run.test: parallel claims not unique emitted=%s unique=%s\n' "$emitted" "$unique" >&2
  exit 1
}

printf 'claim-run.test: ok\n'
