#!/usr/bin/env bash
set -euo pipefail

fail() { printf 'check-lesson-lift: %s\n' "$*" >&2; exit 1; }

file="${1:-}"
[ -f "$file" ] || fail "record file not found: ${file:-<none>}"
repo_root="."
if [ "${2:-}" = "--repo-root" ]; then repo_root="${3:-.}"; fi

quirk_threshold="${IMPLEMENTAUDIT_QUIRK_THRESHOLD:-2}"
case "$quirk_threshold" in
  0|2) ;;
  *) fail "IMPLEMENTAUDIT_QUIRK_THRESHOLD must be 0 or 2" ;;
esac

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

# Repeated host/tool failures reuse the existing transport-infrastructure
# class. At the governed second distinct occurrence, record one machine-local
# workaround or explicitly decline memoization. Duplicate rows for one Occ id
# count once, matching the run-root recurrence walker's occurrence semantics.
if [ "$quirk_threshold" -eq 2 ]; then
  normalize_quirk_signature() {
    printf '%s\n' "$1" \
      | tr '[:upper:]' '[:lower:]' \
      | sed -E \
          -e 's@([[:space:]]+at[[:space:]]+)?[a-z]:\\[^ )|,;]+@ @g' \
          -e 's@([[:space:]]+at[[:space:]]+)?/([^ /|,;]+/)*[^ )|,;]+@ @g' \
          -e 's/[0-9]{4}-[0-9]{2}-[0-9]{2}[t ][0-9]{2}:[0-9]{2}:[0-9]{2}([.,][0-9]+)?(z|[+-][0-9]{2}:[0-9]{2})?/ /g' \
          -e 's/\b(pid|process)[[:space:]]*[:=#]?[[:space:]]*[0-9]+\b/ /g' \
          -e 's/\b(line|column|col)[[:space:]]*[:=#]?[[:space:]]*[0-9]+\b/ /g' \
          -e 's/:[0-9]+(:[0-9]+)?\b/ /g' \
          -e 's/\b[0-9a-f]{6,}\b/ /g' \
          -e "s/'//g" \
          -e "s/[^a-z0-9]+/ /g" \
      | awk '{
          for (i = 1; i <= NF; i++) {
            if ($i ~ /(error|exception)$/) {
              last = i + 6; if (last > NF) last = NF
              out = $i
              for (j = i + 1; j <= last; j++) out = out " " $j
              print out
              exit
            }
          }
        }'
  }

  declare -A quirk_occurrences=()
  declare -A quirk_counts=()
  declare -A quirk_workaround=()
  declare -A quirk_refusal=()

  while IFS='|' read -r _ row_num occ phase class abnormality countermeasure rerun outcome _rest; do
    trim() { local value="$1"; value="${value#"${value%%[![:space:]]*}"}"; value="${value%"${value##*[![:space:]]}"}"; printf '%s' "$value"; }
    occ="$(trim "$occ")"
    class="$(trim "$class")"
    abnormality="$(trim "$abnormality")"
    countermeasure="$(trim "$countermeasure")"
    printf '%s' "$abnormality" | grep -qiE 'Blocker:[[:space:]]*environment-quirk[[:space:]]*\(' || continue
    if [ "$class" != "transport-infrastructure" ]; then
      fail "environment-quirk discriminator must use Class transport-infrastructure"
    fi
    raw_signature="${abnormality#*(}"
    raw_signature="${raw_signature%)*}"
    signature="$(normalize_quirk_signature "$raw_signature")"
    [ -n "$signature" ] || fail "environment-quirk signature has no error or exception class token"
    occurrence_key="$signature|$occ"
    if [ -z "${quirk_occurrences[$occurrence_key]+x}" ]; then
      quirk_occurrences[$occurrence_key]=1
      quirk_counts[$signature]="$(( ${quirk_counts[$signature]:-0} + 1 ))"
    fi
    printf '%s' "$countermeasure" | grep -q 'Workaround:' && quirk_workaround[$signature]=1
    printf '%s' "$countermeasure" | grep -q 'Not memoized:' && quirk_refusal[$signature]=1
  done < "$file"

  for signature in "${!quirk_counts[@]}"; do
    [ "${quirk_counts[$signature]}" -ge "$quirk_threshold" ] || continue
    if [ -z "${quirk_workaround[$signature]+x}" ] && [ -z "${quirk_refusal[$signature]+x}" ]; then
      fail "environment-quirk signature '$signature' reached 2 distinct occurrences without Workaround: or Not memoized:"
    fi
    if [ -n "${quirk_workaround[$signature]+x}" ] && [ -z "${quirk_refusal[$signature]+x}" ]; then
      host_notes="$repo_root/.IMPLEMENTAUDIT/host-notes.md"
      note_count=0
      if [ -f "$host_notes" ]; then
        note_count="$(awk -F'|' -v wanted="$signature" '
          /^[[:space:]]*#/ || /^[[:space:]]*$/ { next }
          NF >= 4 {
            value = tolower($2)
            gsub(/^[[:space:]]+|[[:space:]]+$/, "", value)
            if (value == wanted) count++
          }
          END { print count + 0 }
        ' "$host_notes")"
      fi
      [ "$note_count" -eq 1 ] \
        || fail "environment-quirk signature '$signature' must have exactly one host-note row (found $note_count)"
    fi
  done
fi

# 3. checker/test destination claimed active => target must be non-empty and
# exercised red once. Until then the encoding is ADOPTED_UNENFORCED and cannot
# be cited as a countermeasure.
if printf '%s' "$flat" | grep -qiE 'destination: *(checker or deterministic test|checker|deterministic test)'; then
  cited=0
  printf '%s' "$flat" | grep -qiE 'cited as countermeasure: *yes' && cited=1
  if printf '%s' "$flat" | grep -qiE 'enforcement state: *ADOPTED_UNENFORCED|mechanically active: *no'; then
    [ "$cited" -eq 0 ] || fail "ADOPTED_UNENFORCED remediation cited as a countermeasure"
  fi
  if printf '%s' "$flat" | grep -qiE 'mechanically active: *yes|active: *yes'; then
    printf '%s' "$flat" | grep -qiE 'enforcement state: *ACTIVE' \
      || fail "checker destination claims active without enforcement state ACTIVE"
    target="$(printf '%s' "$content" | { grep -ioE 'target: *[^ ;,]+' || true; } | head -n1 | sed 's/[Tt]arget: *//')"
    [ -n "$target" ] || fail "checker destination claims active but names no target file"
    tpath="$repo_root/$target"
    if [ ! -s "$tpath" ]; then
      fail "claimed-vs-active mismatch: destination is a checker/test claimed active, but target '$target' is missing/empty"
    fi
    printf '%s' "$flat" | grep -qiE 'red exercise: *[^;]+exit[ =:]+[1-9][0-9]*' \
      || fail "checker destination claims ACTIVE without a recorded red exercise (violating check must exit nonzero)"
  fi
fi

printf 'check-lesson-lift: ok\n'
