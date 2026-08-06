#!/usr/bin/env bash
# validate-run-root.sh — structural conformance check for a live run root.
#
# Phase specs are validated at authoring time (validate-phase.sh); this helper
# validates the run root's live state, which matters most at resume: a
# PAUSED/INTERRUPTED run re-reads STATE.md from disk, and corrupted state
# propagates silently without a machine check. Structure-only by design — it
# never judges run content, only that the substrate is shaped like the
# contract.
#
# Usage:
#   validate-run-root.sh <run-root>
#   validate-run-root.sh --graph-freshness <graph.json> <repo-root>
# Usage: validate-run-root.sh [--micro] <run-root>
#        validate-run-root.sh --ledger <markdown-ledger>
# Exit 0: conformant. Exit 1: violations listed on stderr. Exit 2: usage.

set -uo pipefail

err_count=0
err() {
  printf 'validate-run-root: ERROR: %s\n' "$*" >&2
  err_count=$((err_count + 1))
}

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

# Count distinct Occ ids per Class in a new-format Andon table. The existing
# Countermeasure cell carries owner/source=<path>; normalize separators before
# comparing the last two distinct repair occurrences for a class. Keep this
# normalization shape aligned with #80's separate host-note signature counter;
# the substrates and scripts remain intentionally distinct.
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
  # Required artifacts for a dispatched run root. Absent .claimed preserves
  # the v0.3.2 legacy behavior exactly.
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
    # Status must be one of the exact contract tokens.
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

  # Andon log substrate must exist with the contract columns. Two valid
  # generations (#5): the current shape carries an `Occ` occurrence-linkage
  # column; the legacy shape (no Occ) remains VALID — it was the correct
  # contract of its time and legacy run roots resume unchanged.
  if ! grep -qi '^## Andon log' "$state"; then
    err "STATE.md is missing the '## Andon log' section"
  elif grep -qi '| Occ | Phase | Class | Abnormality | Countermeasure | Rerun evidence | Outcome |' "$state"; then
    # New-format table: every data row needs a non-empty Occ id so plural
    # defect rows born from one occurrence stay linked.
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
    # One class per row is LOAD-BEARING for the Occ design: a
    # comma/space-separated multi-class cell would smuggle plural defects
    # into one row instead of linking rows (Fable review of PR #26).
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


# A .claimed root is new-format. It cannot validate while an older sibling is
# undispositioned. SUPERSEDED_BY: is a root header; the distinct
# SUPERSEDED_BY_CONCURRENT_MUTATION token is a residual-table value, not a
# value of that header.
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

# Occurrence resolution + residual dispositions (#6): new-format roots
# (section present) need a valid occurrence-resolution token and a valid
# disposition per residual row; legacy roots without the section stay
# valid. Dispositions are owner/policy-assigned; this checks tokens only.
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
  # `transferred` names the receiving owner; `risk-accepted` cites the
  # policy — the contract says so in the same breath as the tokens, and a
  # transfer nobody receives (or an authority-less risk acceptance) is the
  # packet-of-record for a residual that silently evaporates (Fable review
  # of PR #27). Route-required rows need a non-empty, non-"-" ref cell.
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

# Context epochs + instruction applicability (#35): new-format roots
# (section present) need a valid boundary-provenance token per epoch row
# and valid kind/status tokens per instruction row; legacy roots without
# the section stay valid. Structure/tokens only — reconciliation substance
# is judged by the run, not this helper.
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
  # A terminal status is a claim about the world; without status evidence
  # it is exactly the bare assertion that lets a reconstructed summary
  # replay a "satisfied" one-shot. Terminal rows need a non-empty,
  # non-"-" Status evidence cell (#35).
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

# Evidence-version anchoring (#4): an ANCHORED evidence token must carry
# the FULL 40-hex commit SHA — a short-sha anchor is a stale-evidence
# hazard and fails. Tokens are `@<hex>` with 7+ hex chars (git-sha-like);
# legacy rows without anchors remain valid.
if [ -f "$state" ]; then
  short_anchors="$(grep -oE '@[0-9a-f]{7,}' "$state" 2>/dev/null \
    | grep -vE '^@[0-9a-f]{40}$' || true)"
  if [ -n "$short_anchors" ]; then
    err "STATE.md evidence anchor(s) not full 40-hex SHAs: $(printf '%s' "$short_anchors" | tr '\n' ' ')"
  fi
fi

# Every phase listed in ROADMAP.md must have a phase spec file.
if [ -f "$run_root/ROADMAP.md" ] && [ -d "$run_root/phases" ]; then
  while IFS= read -r n; do
    [ -f "$run_root/phases/phase-$n.md" ] || err "ROADMAP names phase $n but phases/phase-$n.md is missing"
  done < <(grep -oE '^\| *[0-9]+ *\|' "$run_root/ROADMAP.md" 2>/dev/null | grep -oE '[0-9]+' | sort -un)
fi

if [ "$err_count" -gt 0 ]; then
  printf 'validate-run-root: %d error(s)\n' "$err_count" >&2
  exit 1
fi
printf 'validate-run-root: ok\n'
