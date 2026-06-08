#!/usr/bin/env bash
# check-forbidden-terms.sh — generic forbidden-string checker for release gates
#
# Usage:
#   bash scripts/check-forbidden-terms.sh --term FORBIDDEN_STRING [--term ANOTHER]
#   bash scripts/check-forbidden-terms.sh --terms-file /path/to/terms.txt
#   bash scripts/check-forbidden-terms.sh --term FORBIDDEN_STRING --scan-path skills/
#
# The forbidden terms are NEVER embedded in this script source.
# They are supplied by the caller at runtime: --term, --terms-file, or stdin.
#
# Exit 0: no forbidden terms found in the scan scope.
# Exit 1: one or more forbidden terms found; report printed to stderr.
#
# Scan scope (default): all tracked git files, excluding:
#   .git, .IMPLEMENTAUDIT, dist, graphify-out, .graphify, .activegraph,
#   scripts/check-forbidden-terms.sh itself (to avoid self-referential match)
#
# --scan-path overrides the default scope to a specific file or directory.

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

# Parse arguments
terms=()
scan_path=""
terms_file=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --term)
      shift
      terms+=("$1")
      ;;
    --terms-file)
      shift
      terms_file="$1"
      ;;
    --scan-path)
      shift
      scan_path="$1"
      ;;
    *)
      printf 'check-forbidden-terms: unknown flag: %s\n' "$1" >&2
      exit 1
      ;;
  esac
  shift
done

# Load terms from file if provided
if [ -n "$terms_file" ]; then
  while IFS= read -r line || [ -n "$line" ]; do
    trimmed="${line#"${line%%[![:space:]]*}"}"
    trimmed="${trimmed%"${trimmed##*[![:space:]]}"}"
    [ -n "$trimmed" ] && [ "${trimmed:0:1}" != "#" ] && terms+=("$trimmed")
  done < "$terms_file"
fi

if [ "${#terms[@]}" -eq 0 ]; then
  printf 'check-forbidden-terms: no --term or --terms-file supplied; nothing to check\n' >&2
  exit 1
fi

# Build file list
blocked_dirs=(.git .IMPLEMENTAUDIT dist graphify-out .graphify .activegraph)

if [ -n "$scan_path" ]; then
  # Caller-supplied path
  if [ -d "$scan_path" ]; then
    mapfile -t files < <(find "$scan_path" -type f -not -path "*/.git/*" 2>/dev/null | sort)
  elif [ -f "$scan_path" ]; then
    files=("$scan_path")
  else
    printf 'check-forbidden-terms: scan-path not found: %s\n' "$scan_path" >&2
    exit 1
  fi
else
  # Default: tracked git files
  mapfile -t files < <(git ls-files 2>/dev/null | sort)
fi

# Filter out blocked dirs and this script itself
this_script="scripts/check-forbidden-terms.sh"
filtered=()
for f in "${files[@]}"; do
  skip=0
  for bd in "${blocked_dirs[@]}"; do
    case "$f" in
      "$bd"/* | "$bd") skip=1; break ;;
    esac
  done
  [ "$f" = "$this_script" ] && skip=1
  [ "$skip" -eq 0 ] && filtered+=("$f")
done

# Scan for each forbidden term
found=0
for term in "${terms[@]}"; do
  if [ "${#filtered[@]}" -gt 0 ]; then
    while IFS= read -r match; do
      printf 'check-forbidden-terms: FORBIDDEN TERM FOUND: %s\n' "$match" >&2
      found=$((found + 1))
    done < <(grep -rn --include='*' -F "$term" "${filtered[@]}" 2>/dev/null || true)
  fi
done

if [ "$found" -gt 0 ]; then
  printf 'check-forbidden-terms: %d occurrence(s) of forbidden term(s) found\n' "$found" >&2
  exit 1
fi

printf 'check-forbidden-terms: ok (0 forbidden term occurrences in %d files)\n' "${#filtered[@]}"
