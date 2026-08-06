#!/usr/bin/env bash

set -uo pipefail

err_count=0
err() {
  printf 'validate-run-root: ERROR: %s\n' "$*" >&2
  err_count=$((err_count + 1))
}
warn() { printf 'validate-run-root: WARNING: %s\n' "$*" >&2; }

if [ "${1:-}" = "--graph-freshness" ]; then
  if [ "$#" -ne 3 ]; then
    printf 'usage: validate-run-root.sh --graph-freshness <graph.json> <repo-root>\n' >&2
    exit 2
  fi

  graph_path="$2"
  repo_path="$3"
  [ -f "$graph_path" ] || {
    printf 'validate-run-root: graph freshness input is not a file: %s\n' "$graph_path" >&2
    exit 2
  }

  py_cmd=()
  if command -v python >/dev/null 2>&1; then
    py_cmd=(python)
  elif command -v python3 >/dev/null 2>&1; then
    py_cmd=(python3)
  elif command -v py >/dev/null 2>&1; then
    py_cmd=(py -3)
  else
    printf 'validate-run-root: python, python3, or py -3 is required for graph freshness\n' >&2
    exit 2
  fi

  built_at_commit="$("${py_cmd[@]}" - "$graph_path" <<'PY'
import json
import sys

path = sys.argv[1]
try:
    with open(path, encoding="utf-8") as handle:
        payload = json.load(handle)
except (OSError, UnicodeError, json.JSONDecodeError) as exc:
    sys.stderr.write(f"validate-run-root: invalid graph freshness input: {exc}\n")
    raise SystemExit(1)

value = payload.get("built_at_commit")
if not isinstance(value, str) or not value:
    sys.stderr.write("validate-run-root: graph.json has no string built_at_commit\n")
    raise SystemExit(1)
sys.stdout.write(value + "\n")
PY
)"
  parse_status=$?
  [ "$parse_status" -eq 0 ] || exit 1

  if ! printf '%s\n' "$built_at_commit" | grep -Eq '^[0-9a-fA-F]{40}$'; then
    printf 'validate-run-root: graph.json built_at_commit must be one full 40-hex commit SHA\n' >&2
    exit 1
  fi

  live_head="$(git -C "$repo_path" rev-parse HEAD 2>/dev/null)" || {
    printf 'validate-run-root: cannot resolve git rev-parse HEAD for %s\n' "$repo_path" >&2
    exit 2
  }

  if [ "$(printf '%s' "$built_at_commit" | tr '[:upper:]' '[:lower:]')" != \
       "$(printf '%s' "$live_head" | tr '[:upper:]' '[:lower:]')" ]; then
    printf 'validate-run-root: stale-sidecar: built_at_commit %s != git rev-parse HEAD %s\n' \
      "$built_at_commit" "$live_head" >&2
    exit 1
  fi
  exit 0
fi

check_recurrence_decision() {
  local ledger="$1" findings invalid_lines missing_classes
  findings="$(awk -F'|' '
    function trim(v) { gsub(/^[ \t]+|[ \t]+$/, "", v); return v }
    function owner_source(v) {
      if (v !~ /owner\/source[ \t]*=/) return ""
      sub(/^.*owner\/source[ \t]*=[ \t]*/, "", v)
      sub(/[ \t;,)]+.*$/, "", v)
      gsub(/\\/, "/", v)
      while (v ~ /^\.\//) sub(/^\.\//, "", v)
      return v
    }
    /^Mechanism-replacement decision:/ {
      if ($0 ~ /^Mechanism-replacement decision:[ \t]*(replace-mechanism|continue|escalate-to-convergence-mode)[ \t]*\([^()]*[[:alnum:]][^()]*\)[ \t]*$/) {
        valid_decision[NR]=1
      } else {
        print "invalid\t" NR
      }
    }
    /^[ \t]*AUDIT_COMPLETE[ \t]*$/ {
      if (audit_complete_line == 0) audit_complete_line=NR
    }
    /^## Andon log/ { in_andon=1; new_format=0; next }
    in_andon && /^## / { in_andon=0; new_format=0 }
    in_andon && tolower($0) ~ /\|[ \t]*occ[ \t]*\|[ \t]*phase[ \t]*\|[ \t]*class[ \t]*\|/ {
      new_format=1; next
    }
    in_andon && new_format && /^\|[[:space:]]*[0-9]+[[:space:]]*\|/ {
      occ=trim($3); cls=trim($5)
      if (occ == "" || cls == "") next
      key=cls SUBSEP occ
      if (!(key in seen)) {
        seen[key]=1
        count[cls]++
        previous_owner[cls]=last_owner[cls]
        last_owner[cls]=owner_source($7)
        last_line[cls]=NR
      }
    }
    END {
      for (cls in count) {
        if (count[cls] < 3 || last_owner[cls] == "" || previous_owner[cls] != last_owner[cls]) continue
        found=0
        for (line in valid_decision) {
          if ((line + 0) > last_line[cls] &&
              (audit_complete_line == 0 || (line + 0) < audit_complete_line)) found=1
        }
        if (!found) print "missing\t" cls
      }
    }' "$ledger")"

  invalid_lines="$(printf '%s\n' "$findings" | awk -F'\t' '$1 == "invalid" { print $2 }' | tr '\n' ' ')"
  if [ -n "$invalid_lines" ]; then
    err "invalid Mechanism-replacement decision: line(s) $invalid_lines (allowed: replace-mechanism (<what>) / continue (<justification>) / escalate-to-convergence-mode (<shared invariant>))"
  fi
  missing_classes="$(printf '%s\n' "$findings" | awk -F'\t' '$1 == "missing" { print $2 }' | tr '\n' ' ')"
  if [ -n "$missing_classes" ]; then
    err "Andon class(es) $missing_classes reached 3 distinct linked occurrences with the last 2 repairs on one owner/source; add a following Mechanism-replacement decision:"
  fi
}

intent_value() { sed -n "s/^$2:[[:space:]]*//p" "$1" | head -n1; }
duration_seconds() {
  [[ "$1" =~ ^([0-9]+)([smhd]?)$ ]] || return
  case "${BASH_REMATCH[2]}" in '') m=1;; s) m=1;; m) m=60;; h) m=3600;; d) m=86400;; esac
  printf '%s\n' "$((BASH_REMATCH[1] * m))"
}
process_identity_matches() {
  local py
  if command -v python >/dev/null 2>&1; then py=(python)
  elif command -v python3 >/dev/null 2>&1; then py=(python3)
  elif command -v py >/dev/null 2>&1; then py=(py -3)
  else return 2; fi
  "${py[@]}" - "$@" <<'PY'
import json,sys
p,l,i,b,c=sys.argv[1:]
try:
 x=json.load(open(p,encoding="utf-8"))
except (OSError,UnicodeError,json.JSONDecodeError): raise SystemExit(1)
if isinstance(x,dict): x=[x]
keys={"lane_id","host_os","host_boot_id","pid","process_creation_time"}
ok=any(isinstance(r,dict) and keys<=r.keys() and r["lane_id"]==l and isinstance(r["host_os"],str) and r["host_os"] and str(r["pid"])==i and r["host_boot_id"]==b and r["process_creation_time"]==c for r in x)
raise SystemExit(not ok)
PY
}
intent_has_open_window() {
  awk '
    /^[^[:space:]]/ { in_window = ($0 ~ /^verification_window:/); next }
    in_window && /^[[:space:]]*state:[[:space:]]*open[[:space:]]*$/ { found = 1 }
    END { exit !found }
  ' "$1"
}
intent_has_closed_window() {
  grep -Eq '^[[:space:]]*state:[[:space:]]*closed[[:space:]]*$' "$1"
}
intent_has_invalid_closed_anchor() {
  awk '
    /^[^[:space:]]/ { in_window = ($0 ~ /^verification_window:/); next }
    in_window && /^[[:space:]]*-[[:space:]]*surfaces:/ { closed_at = ""; next }
    in_window && /^[[:space:]]*closed_at:/ {
      closed_at = $0
      sub(/^[[:space:]]*closed_at:[[:space:]]*/, "", closed_at)
      next
    }
    in_window && /^[[:space:]]*state:[[:space:]]*closed[[:space:]]*$/ {
      if (length(closed_at) != 40 || closed_at !~ /^[0-9a-f]+$/) bad = 1
    }
    END { exit !bad }
  ' "$1"
}
check_background_chains() {
  local root="$1" state="$2" chain id intent status budget signal expected timeout mode cadence why es ts polls line pid boot created rc
  [ -d "$root/background" ] || return
  for chain in "$root"/background/*; do
    [ -d "$chain" ] || continue; id="$(basename "$chain")"
    intent="$chain/launch-intent.md"; status="$chain/chain-status.txt"
    [ -f "$intent" ] || { err "background/$id missing launch-intent.md"; continue; }
    if intent_has_closed_window "$intent"; then
      [ -f "$chain/chain.done" ] \
        || err "background/$id closed verification window lacks chain.done"
      if intent_has_invalid_closed_anchor "$intent"; then
        err "background/$id closed verification window lacks a full-SHA closed_at"
      fi
    fi
    if [ -f "$state" ] &&
       grep -Eq '^\|[[:space:]]*Status[[:space:]]*\|[[:space:]]*DONE[[:space:]]*\|' "$state" &&
       intent_has_open_window "$intent"; then
      err "background/$id verification window remains open at run-root closure"
    fi
    if ! grep -Eq '^(poll_budget|terminal_signal|expected_duration|transport_timeout|launch_mode|report_cadence):' "$intent"; then
      warn "background/$id legacy launch intent; #81 checks skipped"; continue
    fi
    budget="$(intent_value "$intent" poll_budget)"; signal="$(intent_value "$intent" terminal_signal)"
    expected="$(intent_value "$intent" expected_duration)"; timeout="$(intent_value "$intent" transport_timeout)"
    mode="$(intent_value "$intent" launch_mode)"; cadence="$(intent_value "$intent" report_cadence)"
    why="$(intent_value "$intent" report_cadence_justification)"; [ -n "$cadence" ] || cadence=on-failure-and-terminal
    [[ "$budget" =~ ^[1-9][0-9]*$ ]] || err "background/$id invalid poll_budget"
    [[ "$signal" =~ ^[^[:space:]]+$ ]] || err "background/$id invalid terminal_signal"
    case "$mode" in inline|detached);; *) err "background/$id invalid launch_mode";; esac
    case "$cadence" in per-item|on-failure-and-terminal|terminal-only);; *) err "background/$id invalid report_cadence";; esac
    [ "$cadence" != per-item ] || [[ "$why" =~ [[:alnum:]] ]] || err "background/$id per-item cadence lacks justification"
    es="$(duration_seconds "$expected" 2>/dev/null || :)"; ts="$(duration_seconds "$timeout" 2>/dev/null || :)"
    [ -n "$es" ] || err "background/$id invalid expected_duration"; [ -n "$ts" ] || err "background/$id invalid transport_timeout"
    if [ -n "$es" ] && [ -n "$ts" ] && [ "$mode" = inline ] && [ "$es" -ge "$ts" ]; then err "background/$id inline launch meets/exceeds ceiling"; fi
    [ -f "$status" ] || continue
    polls="$(grep -c '^probe:' "$status" 2>/dev/null || :)"
    if [[ "$budget" =~ ^[1-9][0-9]*$ ]] && [ "$polls" -gt "$budget" ] &&
       { [ ! -f "$state" ] || ! awk -v n="$budget" 'index(tolower($0),"hung-command")&&index(tolower($0),"supervision-overrun")&&index(tolower($0),"poll_budget " n " exceeded"){f=1} END{exit !f}' "$state"; }; then
      err "background/$id poll_budget exceeded without matching hung-command Andon"
    fi
    if [ "$cadence" = on-failure-and-terminal ] && grep -E '^report: item=.*outcome=' "$status" | grep -Evq 'outcome=failure([ |]|$)'; then err "background/$id default cadence narrated success"
    elif [ "$cadence" = terminal-only ] && grep -q '^report: item=' "$status"; then err "background/$id terminal-only narrated item"; fi
    awk '/^checkpoint:/{c=NR}/^wait: blocking/{if(!c||c>=NR)b=1}END{exit b}' "$status" || err "background/$id wait lacks checkpoint"
    grep -R -E -q "Name[[:space:]]*=[[:space:]]*['\"][^'\"]*\\.exe|pkill[[:space:]]+-f|taskkill([.]exe)?[[:space:]].*/IM|Get-CimInstance[[:space:]]+Win32_Process" "$chain" 2>/dev/null && err "background/$id broad kill authority"
    if grep -R -E 'Get-Process([[:space:]]|$)' "$chain" 2>/dev/null | grep -Evq 'Get-Process[[:space:]]+-Id([[:space:]]|$)'; then err "background/$id broad Get-Process"; fi
    while IFS= read -r line; do
      pid="$(sed -n 's/.*pid=\([0-9][0-9]*\).*/\1/p' <<<"$line")"; boot="$(sed -n 's/.*host_boot_id=\([^ |]*\).*/\1/p' <<<"$line")"; created="$(sed -n 's/.*process_creation_time=\([^ |]*\).*/\1/p' <<<"$line")"
      if [ -z "$pid" ] || [ -z "$boot" ] || [ -z "$created" ] || [ ! -f "$chain/process-started.json" ]; then err "background/$id kill lacks process-started.json identity"; continue; fi
      if process_identity_matches "$chain/process-started.json" "$id" "$pid" "$boot" "$created"; then :; else rc=$?; [ "$rc" -eq 2 ] && err "background/$id python required for kill ledger" || err "background/$id kill identity not ledger-owned"; fi
    done < <(grep '^kill:' "$status" 2>/dev/null || :)
  done
}

mode=full
if [ "${1:-}" = "--micro" ]; then
  mode=micro
  shift
elif [ "${1:-}" = "--ledger" ]; then
  mode=ledger
  shift
fi
run_root="${1:-}"
if [ -z "$run_root" ]; then
  if [ "$mode" = micro ]; then
    printf 'usage: validate-run-root.sh --micro <run-root>\n' >&2
  elif [ "$mode" = ledger ]; then
    printf 'usage: validate-run-root.sh --ledger <markdown-ledger>\n' >&2
  else
    printf 'usage: validate-run-root.sh <run-root>\n' >&2
  fi
  exit 2
fi
[ "$mode" != ledger ] || {
  [ -f "$run_root" ] || { printf 'validate-run-root: not a file: %s\n' "$run_root" >&2; exit 2; }
  check_recurrence_decision "$run_root"
  if [ "$err_count" -gt 0 ]; then
    printf 'validate-run-root: %d error(s)\n' "$err_count" >&2
    exit 1
  fi
  printf 'validate-run-root: ok\n'
  exit 0
}
[ -d "$run_root" ] || { printf 'validate-run-root: not a directory: %s\n' "$run_root" >&2; exit 2; }

claim="$run_root/.claimed"
claim_mode=""
if [ "$mode" = micro ] && [ ! -f "$claim" ]; then
  err "micro root is missing .claimed metadata"
fi
if [ -f "$claim" ]; then
  claim_mode="$(awk -F= '$1 == "mode" { print substr($0, index($0, "=") + 1); exit }' "$claim")"
  case "$claim_mode" in
    full|micro) : ;;
    *) err ".claimed has invalid mode '$claim_mode' (expected full or micro)" ;;
  esac
  if [ "$claim_mode" = micro ] && [ "$mode" != micro ]; then
    err ".claimed records mode=micro; validate this declared narrowing with --micro"
  elif [ "$claim_mode" = full ] && [ "$mode" = micro ]; then
    err ".claimed records mode=full; --micro cannot narrow a full claim"
  fi

  claimed_templates="$(awk -F= '$1 == "templates" { print substr($0, index($0, "=") + 1); exit }' "$claim")"
  for f in $claimed_templates; do
    [ -f "$run_root/$f" ] || err "claimed $f is missing — sentinel/artifact drift"
  done
fi

if [ "$mode" = micro ]; then
  [ -f "$run_root/STATE.md" ] || err "missing required artifact: STATE.md"
else
  for f in STATE.md PROTOCOL.md; do
    [ -f "$run_root/$f" ] || err "missing required artifact: $f"
  done
  for f in ROADMAP.md THINKING.md sidecars.md tools.md context.md; do
    [ -f "$run_root/$f" ] || err "missing planning artifact: $f (required for dispatched phase runs)"
  done
fi

state="$run_root/STATE.md"
if [ -f "$state" ]; then
  if [ "$mode" = full ]; then
    status_line="$(grep -E '^\| Status \|' "$state" | head -1 || true)"
    if [ -z "$status_line" ]; then
      err "STATE.md has no '| Status |' row in the Current phase table"
    else
      status_value="$(printf '%s' "$status_line" | awk -F'|' '{gsub(/^[ \t]+|[ \t]+$/, "", $3); print $3}')"
      case "$status_value" in
        open|READY_TO_DISPATCH|IN_PHASE|PAUSED|BLOCKED|INTERRUPTED|DONE) : ;;
        *) err "STATE.md Status '$status_value' is not a contract token (open / READY_TO_DISPATCH / IN_PHASE / PAUSED / BLOCKED / INTERRUPTED / DONE)" ;;
      esac
    fi
  fi

  if ! grep -qi '^## Andon log' "$state"; then
    err "STATE.md is missing the '## Andon log' section"
  elif grep -qi '| Occ | Phase | Class | Abnormality | Countermeasure | Rerun evidence | Outcome |' "$state"; then
    missing_occ="$(awk -F'|' '
      /^## Andon log/ { in_andon=1; next }
      in_andon && /^## / { in_andon=0 }
      in_andon && /^\|[[:space:]]*[0-9]+[[:space:]]*\|/ {
        occ=$3; gsub(/^[ \t]+|[ \t]+$/, "", occ)
        if (occ == "") { n=$2; gsub(/^[ \t]+|[ \t]+$/, "", n); print n }
      }' "$state")"
    if [ -n "$missing_occ" ]; then
      err "STATE.md Andon log new-format rows missing an Occ occurrence id: row(s) $(printf '%s' "$missing_occ" | tr '\n' ' ')"
    fi
    multi_class="$(awk -F'|' '
      /^## Andon log/ { in_andon=1; next }
      in_andon && /^## / { in_andon=0 }
      in_andon && /^\|[[:space:]]*[0-9]+[[:space:]]*\|/ {
        cls=$5; gsub(/^[ \t]+|[ \t]+$/, "", cls)
        if (cls != "" && cls !~ /^[A-Za-z-]+$/) {
          n=$2; gsub(/^[ \t]+|[ \t]+$/, "", n); print n }
      }' "$state")"
    if [ -n "$multi_class" ]; then
      err "STATE.md Andon log row(s) with a non-single-token Class (exactly one class per row; plural defects record one row per class sharing an Occ id): row(s) $(printf '%s' "$multi_class" | tr '\n' ' ')"
    fi
  elif ! grep -qi '| Class | Abnormality | Countermeasure | Rerun evidence | Outcome |' "$state"; then
    err "STATE.md Andon log table is missing the contract columns (# | Occ | Phase | Class | Abnormality | Countermeasure | Rerun evidence | Outcome; legacy shape without Occ also accepted)"
  fi
  check_recurrence_decision "$state"

  if [ "$mode" = micro ]; then
    terminal_line="$(awk 'NF { last=$0 } END { print last }' "$state")"
    case "$terminal_line" in
      AUDIT_COMPLETE|AUDIT_HANDOFF|ANDON_HANDOFF) : ;;
      IMPLEMENTAUDIT_RUN_COMPLETE)
        grep -qx 'AUDIT_COMPLETE' "$state" || err "STATE.md ends with IMPLEMENTAUDIT_RUN_COMPLETE but has no preceding AUDIT_COMPLETE"
        ;;
      *) err "micro STATE.md final nonblank line is not a terminal marker (AUDIT_COMPLETE / IMPLEMENTAUDIT_RUN_COMPLETE / AUDIT_HANDOFF / ANDON_HANDOFF)" ;;
    esac

    if find "$run_root/phases" -type f -name 'phase-*.md' -print -quit 2>/dev/null | grep -q .; then
      err "micro root contains phase specs; phased dispatch requires a full run root"
    fi
    if [ -f "$run_root/ROADMAP.md" ] && grep -Eq '^\|[[:space:]]*[0-9]+[[:space:]]*\|' "$run_root/ROADMAP.md"; then
      err "micro root contains a ROADMAP phase table; phased dispatch requires a full run root"
    fi
    if grep -R -E -q '^(Stage 6\.2|Independent cold-review disposition|Review disposition):' "$run_root" \
      --exclude='.claimed' 2>/dev/null; then
      err "micro root contains a Stage 6.2 disposition; executor-facing review requires a full run root"
    fi
  fi
fi


if [ -f "$claim" ]; then
  run_base="$(dirname "$run_root")"
  for sibling in "$run_base"/*; do
    [ -d "$sibling" ] || continue
    [ "$sibling" = "$run_root" ] && continue
    sibling_state="$sibling/STATE.md"
    if [ ! -f "$sibling_state" ] || ! grep -Eq \
      '^(AUDIT_COMPLETE|IMPLEMENTAUDIT_RUN_COMPLETE|AUDIT_HANDOFF|ANDON_HANDOFF|COMPLETE|HANDOFF|SUPERSEDED_BY:[[:space:]].+|PARALLEL:[[:space:]].+)$' \
      "$sibling_state"; then
      err "newly claimed root has undispositioned sibling: $(basename "$sibling")"
    fi
  done
fi

if [ -f "$state" ] && grep -qi '^## Occurrence resolution and residuals' "$state"; then
  occ_res="$(awk '/^## Occurrence resolution and residuals/{f=1;next} f&&/^Occurrence resolution:/{sub(/^Occurrence resolution:[ \t]*/,"");print;exit}' "$state")"
  case "$occ_res" in
    not-applicable|unresolved|partially-resolved|resolved) : ;;
    *) err "STATE.md Occurrence resolution '$occ_res' is not a contract token (not-applicable / unresolved / partially-resolved / resolved)" ;;
  esac
  bad_disp="$(awk -F'|' '
    /^## Occurrence resolution and residuals/ { f=1; next }
    f && /^## / { f=0 }
    f && /^\|/ {
      d=$4; gsub(/^[ \t]+|[ \t]+$/, "", d)
      r=$2; gsub(/^[ \t]+|[ \t]+$/, "", r)
      if (r == "Residual" || r ~ /^-+$/ || r == "") next
      if (d !~ /^(unresolved|deferred|transferred|owner-assigned|risk-accepted|validated-resolved)$/) print r
    }' "$state")"
  if [ -n "$bad_disp" ]; then
    err "STATE.md residual row(s) with invalid disposition: $(printf '%s' "$bad_disp" | tr '\n' ' ') (allowed: unresolved / deferred / transferred / owner-assigned / risk-accepted / validated-resolved)"
  fi
  no_ref="$(awk -F'|' '
    /^## Occurrence resolution and residuals/ { f=1; next }
    f && /^## / { f=0 }
    f && /^\|/ {
      d=$4; gsub(/^[ \t]+|[ \t]+$/, "", d)
      o=$5; gsub(/^[ \t]+|[ \t]+$/, "", o)
      r=$2; gsub(/^[ \t]+|[ \t]+$/, "", r)
      if (r == "Residual" || r ~ /^-+$/ || r == "") next
      if ((d == "transferred" || d == "risk-accepted") &&
          (o == "" || o ~ /^-+$/)) print r
    }' "$state")"
  if [ -n "$no_ref" ]; then
    err "STATE.md residual row(s) with transferred/risk-accepted but no owner/policy ref: $(printf '%s' "$no_ref" | tr '\n' ' ') (transferred names the receiving owner; risk-accepted cites the policy)"
  fi
fi

if [ -f "$state" ] && grep -qi '^## Context epochs and instruction applicability' "$state"; then
  bad_prov="$(awk -F'|' '
    /^## Context epochs and instruction applicability/ { f=1; next }
    f && /^## / { f=0 }
    f && /^\|[[:space:]]*e[0-9]+[[:space:]]*\|/ {
      p=$3; gsub(/^[ \t]+|[ \t]+$/, "", p)
      e=$2; gsub(/^[ \t]+|[ \t]+$/, "", e)
      if (p !~ /^(host-reported-compaction|new-session|handoff-resume|manual-resume|inferred-context-gap)$/) print e
    }' "$state")"
  if [ -n "$bad_prov" ]; then
    err "STATE.md epoch row(s) with invalid boundary provenance: $(printf '%s' "$bad_prov" | tr '\n' ' ') (allowed: host-reported-compaction / new-session / handoff-resume / manual-resume / inferred-context-gap; never fabricate a compaction)"
  fi
  bad_instr="$(awk -F'|' '
    /^## Context epochs and instruction applicability/ { f=1; next }
    f && /^## / { f=0 }
    f && /^\|[[:space:]]*i[0-9]+[[:space:]]*\|/ {
      k=$4; gsub(/^[ \t]+|[ \t]+$/, "", k)
      s=$8; gsub(/^[ \t]+|[ \t]+$/, "", s)
      n=$2; gsub(/^[ \t]+|[ \t]+$/, "", n)
      okk = (k ~ /^(one-shot-action|standing-constraint|standing-authorization|persistent-objective|query-or-information-request)$/)
      oks = (s ~ /^(active|satisfied|superseded|revoked|expired|ambiguous)$/)
      if (!okk || !oks) print n
    }' "$state")"
  if [ -n "$bad_instr" ]; then
    err "STATE.md instruction row(s) with invalid kind/status token: $(printf '%s' "$bad_instr" | tr '\n' ' ') (kind: one-shot-action / standing-constraint / standing-authorization / persistent-objective / query-or-information-request; status: active / satisfied / superseded / revoked / expired / ambiguous)"
  fi
  no_ev="$(awk -F'|' '
    /^## Context epochs and instruction applicability/ { f=1; next }
    f && /^## / { f=0 }
    f && /^\|[[:space:]]*i[0-9]+[[:space:]]*\|/ {
      s=$8; gsub(/^[ \t]+|[ \t]+$/, "", s)
      ev=$9; gsub(/^[ \t]+|[ \t]+$/, "", ev)
      n=$2; gsub(/^[ \t]+|[ \t]+$/, "", n)
      if (s ~ /^(satisfied|superseded|revoked|expired)$/ &&
          (ev == "" || ev ~ /^-+$/)) print n
    }' "$state")"
  if [ -n "$no_ev" ]; then
    err "STATE.md instruction row(s) with terminal status but no status evidence: $(printf '%s' "$no_ev" | tr '\n' ' ') (satisfied/superseded/revoked/expired require evidence — a bare terminal claim is the replay hazard #35 forbids)"
  fi
fi

if [ -f "$state" ]; then
  short_anchors="$(grep -oE '@[0-9a-f]{7,}' "$state" 2>/dev/null \
    | grep -vE '^@[0-9a-f]{40}$' || true)"
  if [ -n "$short_anchors" ]; then
    err "STATE.md evidence anchor(s) not full 40-hex SHAs: $(printf '%s' "$short_anchors" | tr '\n' ' ')"
  fi
fi

if [ -f "$run_root/ROADMAP.md" ] && [ -d "$run_root/phases" ]; then
  while IFS= read -r n; do
    [ -f "$run_root/phases/phase-$n.md" ] || err "ROADMAP names phase $n but phases/phase-$n.md is missing"
  done < <(grep -oE '^\| *[0-9]+ *\|' "$run_root/ROADMAP.md" 2>/dev/null | grep -oE '[0-9]+' | sort -un)
fi

check_background_chains "$run_root" "$state"

if [ "$err_count" -gt 0 ]; then
  printf 'validate-run-root: %d error(s)\n' "$err_count" >&2
  exit 1
fi
printf 'validate-run-root: ok\n'
