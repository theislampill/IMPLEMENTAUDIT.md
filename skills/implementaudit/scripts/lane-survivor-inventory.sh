#!/usr/bin/env bash
# Print-only interruption inventory for declared lane outputs.
# Deliberately unwired from closure gates: automatic retry can replay satisfied
# one-shots or bypass current authorization, so this script classifies and
# recommends a re-dispatch set but never acts on it.
set -euo pipefail

usage() {
  printf 'usage: lane-survivor-inventory.sh RUN_ROOT --expect RELATIVE_PATH [--contains LITERAL] ...\n' >&2
}

fail() {
  printf 'lane-survivor-inventory: %s\n' "$*" >&2
  exit 2
}

[ "$#" -ge 3 ] || {
  usage
  exit 2
}

run_root="$1"
shift
[ -d "$run_root" ] || fail "run root is not a directory: $run_root"

declare -a expected=()
declare -a contains=()
current=-1

while [ "$#" -gt 0 ]; do
  case "$1" in
    --expect)
      [ "$#" -ge 2 ] || fail "--expect requires a relative path"
      rel="$2"
      case "$rel" in
        ''|/*|[A-Za-z]:*|*\\*) fail "expected path must be a slash-separated relative path: $rel" ;;
      esac
      if [[ "$rel" == *$'\t'* || "$rel" == *$'\r'* || "$rel" == *$'\n'* ]]; then
        fail "expected path contains a control character"
      fi
      case "/$rel/" in
        */../*|*/./*) fail "expected path contains a traversal segment: $rel" ;;
      esac
      for prior in "${expected[@]}"; do
        [ "$prior" != "$rel" ] || fail "expected path is duplicated: $rel"
      done
      expected+=("$rel")
      contains+=("")
      current=$((${#expected[@]} - 1))
      shift 2
      ;;
    --contains)
      [ "$#" -ge 2 ] || fail "--contains requires a literal"
      [ "$current" -ge 0 ] || fail "--contains must follow --expect"
      [ -z "${contains[$current]}" ] || fail "only one --contains is allowed per expected path"
      contains[$current]="$2"
      shift 2
      ;;
    *)
      fail "unknown argument: $1"
      ;;
  esac
done

[ "${#expected[@]}" -gt 0 ] || fail "at least one --expect is required"

declare -a redispatch=()
for index in "${!expected[@]}"; do
  rel="${expected[$index]}"
  target="$run_root/$rel"
  required_literal="${contains[$index]}"
  classification=present

  if [ ! -e "$target" ]; then
    classification=absent
  elif [ ! -f "$target" ] || [ ! -s "$target" ]; then
    classification=partial
  elif [ -n "$required_literal" ] && ! grep -Fq -e "$required_literal" "$target"; then
    classification=partial
  fi

  printf '%s\t%s\n' "$classification" "$rel"
  if [ "$classification" != present ]; then
    redispatch+=("$rel")
  fi
done

for rel in "${redispatch[@]}"; do
  printf 're-dispatch\t%s\n' "$rel"
done

printf 'advisory\tThis inventory only prints classifications because automatic retry can replay satisfied one-shots or bypass authorization.\n'
