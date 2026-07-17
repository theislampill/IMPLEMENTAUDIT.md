#!/usr/bin/env bash
set -euo pipefail

# Parameter-bound authorization drift check (#12). Read-only. Compares a
# runtime invocation's consequential parameters against the parameters an
# authorization record binds.
#
#   check-authorization-binding.sh --auth <auth-file> --invocation <inv-file>
#
# Both files are `key: value` lists. The auth file declares:
#   binds: <k1>,<k2>,...        (the consequential parameters governed)
#   <k>: <value-or-range>       (bound value; a range like 1..1000 or a set
#                                a|b|c is honored)
# The invocation file supplies actual runtime `<k>: <value>` lines.
#
# AUTHORITY DRIFT (exit 1) when a consequential parameter present in the
# invocation is NOT in `binds`, or its value conflicts with the bound
# value/range. A matching invocation exits 0 with no added ceremony. If the
# auth binds nothing (no `binds:` line), any consequential invocation
# parameter is unbound => drift.

fail() { printf 'check-authorization-binding: %s\n' "$*" >&2; exit 1; }
drift() {
  printf 'check-authorization-binding: AUTHORITY DRIFT (%s) — class owner-unclear/authority; STOP the governed action and request an owner decision\n' "$*" >&2
  exit 1
}

auth=""; inv=""
while [ "$#" -gt 0 ]; do
  case "$1" in
    --auth) auth="$2"; shift 2;;
    --invocation) inv="$2"; shift 2;;
    *) fail "unknown arg $1";;
  esac
done
[ -f "$auth" ] || fail "auth file not found: $auth"
[ -f "$inv" ] || fail "invocation file not found: $inv"

# An absent key (e.g. no `binds:` line) is a real case that must be
# EVALUATED (unbound => drift), not an early script death under
# `set -euo pipefail`. Swallow grep's no-match to empty output.
val() { { grep -iE "^$2:" "$1" || true; } | head -n1 | sed "s/^[^:]*: *//" | tr -d '\r' | sed 's/[[:space:]]*$//'; }

# Duplicate keys in the AUTHORIZATION record are ambiguous authority —
# a permissive spec listed first would silently shadow a stricter one
# (Fable review of PR #32). One value per key, malformed otherwise.
dup_check() {
  n="$({ grep -ciE "^$1:" "$auth" || true; })"
  [ "${n:-0}" -le 1 ] || fail "malformed authorization: key '$1' appears $n times — one value per key"
}
dup_check binds
binds="$(val "$auth" binds)"
for k in $(printf '%s' "$binds" | tr ',' ' '); do
  dup_check "$k"
done

in_range() {  # value, spec
  local v="$1" spec="$2"
  case "$spec" in
    *..*) local lo="${spec%%..*}" hi="${spec##*..}"
          [ "$v" -ge "$lo" ] 2>/dev/null && [ "$v" -le "$hi" ] 2>/dev/null ;;
    *"|"*) printf '%s' "|$spec|" | grep -qF "|$v|" ;;
    *) [ "$v" = "$spec" ] ;;
  esac
}

# Every consequential parameter the INVOCATION supplies must be bound and
# in-range. Consequential params are those the invocation marks with a
# leading `param.` prefix (so ordinary metadata lines are ignored).
drifted=""
# `|| [ -n "$line" ]` keeps a final line WITHOUT a trailing newline in
# scope — a drifting parameter on an unterminated last line was silently
# dropped by plain `while read` (Fable review of PR #32).
while IFS= read -r line || [ -n "$line" ]; do
  case "$line" in param.*) : ;; *) continue;; esac
  key="$(printf '%s' "$line" | sed -n 's/^\(param\.[a-zA-Z0-9_-]*\):.*/\1/p')"
  short="${key#param.}"
  v="$(printf '%s' "$line" | sed "s/^[^:]*: *//" | tr -d '\r' | sed 's/[[:space:]]*$//')"
  case ",$binds," in
    *",$short,"*) : ;;
    *) drifted="$drifted $short(unbound)"; continue;;
  esac
  spec="$(val "$auth" "$short")"
  if [ -n "$spec" ] && ! in_range "$v" "$spec"; then
    drifted="$drifted $short(=$v vs bound $spec)"
  fi
done < "$inv"

# Every parameter the authorization BINDS must actually be supplied by
# the invocation: a bound-but-unsupplied parameter means the governed
# action would run on a source/tool default the owner never saw —
# defaults are never implicitly adopted (Fable review of PR #32).
for k in $(printf '%s' "$binds" | tr ',' ' '); do
  grep -qiE "^param\.$k:" "$inv" \
    || drifted="$drifted $k(bound-but-unsupplied — runtime value unknown; defaults are never implicitly adopted)"
done

[ -z "$drifted" ] || drift "$drifted"
printf 'check-authorization-binding: ok — all consequential parameters bound and in range\n'
