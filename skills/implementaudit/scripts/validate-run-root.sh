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
# Usage: validate-run-root.sh <run-root>
# Exit 0: conformant. Exit 1: violations listed on stderr. Exit 2: usage.

set -uo pipefail

err_count=0
err() {
  printf 'validate-run-root: ERROR: %s\n' "$*" >&2
  err_count=$((err_count + 1))
}

run_root="${1:-}"
if [ -z "$run_root" ]; then
  printf 'usage: validate-run-root.sh <run-root>\n' >&2
  exit 2
fi
[ -d "$run_root" ] || { printf 'validate-run-root: not a directory: %s\n' "$run_root" >&2; exit 2; }

# Required artifacts for a dispatched run root.
for f in STATE.md PROTOCOL.md; do
  [ -f "$run_root/$f" ] || err "missing required artifact: $f"
done
for f in ROADMAP.md THINKING.md sidecars.md tools.md context.md; do
  [ -f "$run_root/$f" ] || err "missing planning artifact: $f (required for dispatched phase runs)"
done

state="$run_root/STATE.md"
if [ -f "$state" ]; then
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
