#!/usr/bin/env bash
set -euo pipefail

# Lesson-lift routing-record scorer (#13). Read-only. Scores ONE closure
# transcript/record file for the lesson-lift contract.
#
#   check-lesson-lift.sh <record-file> [--repo-root <dir>]
#
# Rules enforced:
#  - A record carrying a qualifying trigger MUST contain a `Lesson-lift:`
#    routing record (qualifying closure without one FAILS).
#  - A no-lift decision whose reason is "easy/cheap to redo by hand" FAILS;
#    a reasoned no-lift (any other substantive reason) PASSES.
#  - A destination of `checker or deterministic test` claiming the encoding
#    is active MUST name a target file that EXISTS and is NON-EMPTY — a
#    missing/empty target is a claimed-vs-active mismatch and FAILS.
#    (Whether a pre-existing target actually CHANGED is not checked here:
#    the scorer sees one closure record, not the baseline tree. Change
#    verification is the closure author's PROTOCOL duty, item 6.)
#  - A closure claiming "recurrence prevented" FAILS (only encoding-written,
#    mechanically-active, and installed-current are closure-time claims).
#  - A one-off correction with no qualifying trigger and a single `No-lift:`
#    disposition line PASSES (negative control).

fail() { printf 'check-lesson-lift: %s\n' "$*" >&2; exit 1; }

file="${1:-}"
[ -f "$file" ] || fail "record file not found: ${file:-<none>}"
repo_root="."
if [ "${2:-}" = "--repo-root" ]; then repo_root="${3:-.}"; fi

content="$(cat "$file")"
flat="$(printf '%s' "$content" | tr '\n' ' ')"

# 1. Forbidden closure claim: prevention is future evidence. Worded
# variants count too — "the recurrence has been prevented" and "prevents
# recurrence" are the same claim in disguise (Fable review of PR #29);
# intent forms ("meant/intended to prevent", "without preventing") are
# not claims and stay legal.
if printf '%s' "$flat" | grep -qiE 'recurrence[ _-]?prevented|prevented recurrence|will not recur|cannot recur|recurrence[^.]{0,60}\b(prevented|averted)\b|\bprevents\b[^.]{0,40}\brecurrence'; then
  fail "closure claims recurrence prevented — prevention is future evidence, not a closure-time claim"
fi

# One canonical record: two Lesson-lift records in one closure are
# competing records, which the contract forbids (Fable review of PR #29).
record_count="$(printf '%s\n' "$content" | grep -ciE '^Lesson-lift:' || true)"
if [ "${record_count:-0}" -gt 1 ]; then
  fail "found $record_count Lesson-lift records — one qualifying lesson produces exactly ONE canonical record"
fi

# The qualifying scan ignores `No-lift:` disposition lines: the one-off
# disposition describing itself ("no recurrence expected") must not
# trigger the ceremony the disposition exists to avoid (Fable review of
# PR #29).
qual_scan="$(printf '%s\n' "$content" | grep -viE '^No-lift:' | tr '\n' ' ')"
qualifies=0
printf '%s' "$qual_scan" | grep -qiE 'qualifying trigger:|recurrence|governing rule|governing-rule|repeated (manual )?workaround|high consequence|cross-project reuse|owner request' \
  && qualifies=1

has_record=0
printf '%s' "$content" | grep -qiE '^Lesson-lift:' && has_record=1

if [ "$qualifies" -eq 1 ] && [ "$has_record" -eq 0 ]; then
  # A one-off no-lift disposition line is the ONLY exception, and it does
  # not qualify. A qualifying lesson with no routing record fails.
  fail "qualifying lesson closed without a Lesson-lift routing record"
fi

# 2. No-lift reason quality.
if printf '%s' "$flat" | grep -qiE '(no-lift|no lift)[^.]*\b(easy|cheap|trivial) to redo by hand'; then
  fail "no-lift reason 'easy/cheap to redo by hand' is insufficient — record a substantive reason"
fi
# A no-lift DECISION inside a Lesson-lift record requires a non-empty
# reason — an empty `reason =` field is a bare "no" (Fable review of
# PR #29). The one-off `No-lift:` disposition line is not a record and
# is exempt.
if printf '%s' "$flat" | grep -qiE 'Lesson-lift:.*decision: *no-lift'; then
  reason_val="$(printf '%s' "$flat" | { grep -ioE 'reason *= *[^;]*' || true; } | head -n1 | sed -E 's/^[Rr]eason *= *//; s/^ +//; s/ +$//')"
  if ! printf '%s' "$reason_val" | grep -q '[[:alnum:]]'; then
    fail "no-lift decision with an empty reason — rejecting a lift requires a recorded reason"
  fi
fi

# 3. checker/test destination claimed active => target must be non-empty.
if printf '%s' "$flat" | grep -qiE 'destination: *(checker or deterministic test|checker|deterministic test)'; then
  if printf '%s' "$flat" | grep -qiE 'mechanically active: *yes|active: *yes'; then
    target="$(printf '%s' "$content" | { grep -ioE 'target: *[^ ;,]+' || true; } | head -n1 | sed 's/[Tt]arget: *//')"
    [ -n "$target" ] || fail "checker destination claims active but names no target file"
    tpath="$repo_root/$target"
    if [ ! -s "$tpath" ]; then
      fail "claimed-vs-active mismatch: destination is a checker/test claimed active, but target '$target' is missing/empty"
    fi
  fi
fi

printf 'check-lesson-lift: ok\n'
