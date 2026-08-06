#!/usr/bin/env bash
set -euo pipefail


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

field() {
  printf '%s\n' "$1" | tr '|' '\n' | while IFS= read -r seg; do
    k="$(printf '%s' "$seg" | sed -n 's/^[[:space:]]*\([a-z_-]*\):.*/\1/p')"
    if [ "$k" = "$2" ]; then
      printf '%s' "$seg" | sed "s/^[[:space:]]*$2:[[:space:]]*//; s/[[:space:]]*$//"
      return
    fi
  done
}

rows=0
coverage_rows=0
seen_ids=""
while IFS= read -r line; do
  case "$line" in resource-exhausted:*)
    qid="$(field "$line" resource-exhausted)"
    qclass="$(field "$line" class)"
    blocker="$(field "$line" blocker)"
    reported="$(field "$line" reported_reset)"
    backoff="$(field "$line" backoff_probe_at)"
    next_probe="$(field "$line" next_probe_at)"
    capacity="$(field "$line" capacity_probe)"
    probe_evidence="$(field "$line" probe_evidence)"
    terminal="$(field "$line" terminal)"
    [ -n "$qid" ] || fail "resource-exhausted row has no identity"
    [ "$qclass" = transport-infrastructure ] \
      || fail "resource-exhausted $qid: class must be transport-infrastructure"
    [ "$blocker" = resource-exhausted ] \
      || fail "resource-exhausted $qid: blocker must be resource-exhausted"
    printf '%s' "$reported" | grep -Eq '^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z ADVISORY$' \
      || fail "resource-exhausted $qid: reported_reset must be canonical UTC and labelled ADVISORY"
    reported_ts="${reported%% *}"
    printf '%s' "$backoff" | grep -Eq '^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$' \
      || fail "resource-exhausted $qid: invalid backoff_probe_at"
    expected_next="$reported_ts"
    if [[ "$backoff" < "$expected_next" ]]; then expected_next="$backoff"; fi
    [ "$next_probe" = "$expected_next" ] \
      || fail "resource-exhausted $qid: next_probe_at must equal min(reported_reset, backoff_probe_at)"
    case "$capacity" in succeeded|failed) : ;;
      *) fail "resource-exhausted $qid: blocked/resume decision requires a completed cheap capacity probe";;
    esac
    [ -n "$probe_evidence" ] && [ "$probe_evidence" != none ] \
      || fail "resource-exhausted $qid: capacity probe has no checkable evidence"
    case "$capacity:$terminal" in
      succeeded:resumed|failed:blocked) : ;;
      succeeded:blocked) fail "resource-exhausted $qid: successful probe must resume before an advisory reset";;
      failed:resumed) fail "resource-exhausted $qid: failed probe cannot justify resumption";;
      *) fail "resource-exhausted $qid: invalid terminal '$terminal'";;
    esac
    continue
    ;;
  esac
  if printf '%s' "$line" | grep -qiE '^[[:space:]]*claim:'; then
    case "$line" in claim:*) : ;; *)
      fail "malformed claim row (key must be exactly lowercase 'claim:'): ${line%%|*}";;
    esac
  fi
  case "$line" in claim:*) : ;; *) continue;; esac
  rows=$((rows + 1))
  cid="$(field "$line" claim)"
  case " $seen_ids " in *" $cid "*)
    fail "duplicate Claim-ID '$cid' — each closure claim has one row";;
  esac
  seen_ids="$seen_ids $cid"
  surface="$(field "$line" surface)"
  status="$(field "$line" status)"
  esurface="$(field "$line" 'evidence-surface')"
  coverage="$(field "$line" coverage)"
  range_note="$(field "$line" range)"
  omission="$(field "$line" omission)"
  if [ -n "$coverage" ]; then
    coverage_rows=$((coverage_rows + 1))
    case "$coverage" in full|partial) : ;;
      *) fail "claim $cid: invalid coverage '$coverage' (expected full or partial)";;
    esac
  fi
  if [ "$coverage" = partial ]; then
    [ -n "$range_note" ] && [ -n "$omission" ] \
      || fail "claim $cid: partial coverage requires range and omission"
    [ "$status" != verified ] \
      || fail "claim $cid: partial coverage cannot support verified closure"
  fi
  if [ "$coverage" = full ] \
     && printf '%s' "$line" | grep -qi 'warning:[[:space:]]*truncated output'; then
    fail "claim $cid: truncation marker contradicts coverage full"
  fi
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
[ "$coverage_rows" -eq 0 ] || [ "$coverage_rows" -eq "$rows" ] \
  || fail "closure record mixes coverage-tagged and untagged claim rows"
if grep -E -q "Name[[:space:]]*=[[:space:]]*['\"][^'\"]*\\.exe|pkill[[:space:]]+-f|taskkill([.]exe)?[[:space:]].*/IM|Get-CimInstance[[:space:]]+Win32_Process" "$file"; then
  fail "kill authority uses executable name, image, pattern, or broad host-process enumeration instead of process-started.json identity"
fi
if grep -E 'Get-Process([[:space:]]|$)' "$file" |
   grep -Evq 'Get-Process[[:space:]]+-Id([[:space:]]|$)'; then
  fail "kill authority uses broad Get-Process enumeration without -Id"
fi
printf 'check-closure-surface: ok (%d claim row(s))\n' "$rows"
