#!/usr/bin/env bash
set -euo pipefail

# Closure-claim success-surface scorer (#14). Read-only. Scores a closure
# record whose claims are indexed to the surface that establishes them.
#
#   check-closure-surface.sh <record-file>
#
# Record lines of the form:
#   claim: <id> | surface: <surface> | property: <structural|behavioral|provenance> | status: <verified|failed|unverified|not-applicable> | evidence-surface: <surface> | [residual: <ref>]
#
# Rules:
#  - A `verified` claim MUST carry evidence from its OWN required surface;
#    evidence-surface at a LOWER layer than the claimed surface => layer
#    promotion => FAIL (e.g. deployed-service claim verified by source).
#  - A required surface that cannot be inspected must be `unverified` /
#    deferred (a residual ref), never `verified` — a `verified` claim with
#    no evidence-surface FAILS.
#  - Surfaces are ordered source < generated-artifact < package <
#    installed-payload < running-local-service < deployed-service < api <
#    user-visible < publication.

fail() { printf 'check-closure-surface: %s\n' "$*" >&2; exit 1; }

file="${1:-}"
[ -f "$file" ] || fail "record file not found: ${file:-<none>}"

rank() {
  case "$1" in
    source) echo 0;; generated-artifact) echo 1;; package) echo 2;;
    installed-payload) echo 3;; running-local-service) echo 4;;
    deployed-service) echo 5;; api) echo 6;; user-visible) echo 7;;
    publication) echo 8;; *) echo -1;;
  esac
}

# Exact-key field extraction over pipe-separated `key: value` segments, so
# `surface` never accidentally matches `evidence-surface`.
field() {
  printf '%s\n' "$1" | tr '|' '\n' | while IFS= read -r seg; do
    k="$(printf '%s' "$seg" | sed -n 's/^[[:space:]]*\([a-z-]*\):.*/\1/p')"
    if [ "$k" = "$2" ]; then
      printf '%s' "$seg" | sed "s/^[[:space:]]*$2:[[:space:]]*//; s/[[:space:]]*$//"
      return
    fi
  done
}

rows=0
while IFS= read -r line; do
  case "$line" in claim:*) : ;; *) continue;; esac
  rows=$((rows + 1))
  cid="$(field "$line" claim)"
  surface="$(field "$line" surface)"
  status="$(field "$line" status)"
  esurface="$(field "$line" 'evidence-surface')"
  [ "$(rank "$surface")" -ge 0 ] || fail "claim $cid: unknown required surface '$surface'"
  case "$status" in
    verified|failed|unverified|not-applicable) : ;;
    *) fail "claim $cid: invalid verification status '$status'";;
  esac
  if [ "$status" = verified ]; then
    [ -n "$esurface" ] || fail "claim $cid: verified with no evidence-surface — an uninspectable surface must be unverified/deferred"
    er="$(rank "$esurface")"
    sr="$(rank "$surface")"
    [ "$er" -ge 0 ] || fail "claim $cid: unknown evidence-surface '$esurface'"
    if [ "$er" -lt "$sr" ]; then
      fail "claim $cid: layer promotion — '$surface' claim verified only by lower-layer '$esurface' evidence"
    fi
  fi
done < "$file"

[ "$rows" -gt 0 ] || fail "no closure claim rows found"
printf 'check-closure-surface: ok (%d claim row(s))\n' "$rows"
