#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

helper="skills/implementaudit/scripts/validate-run-root.sh"

if command -v python >/dev/null 2>&1; then
  py_cmd=(python)
elif command -v python3 >/dev/null 2>&1; then
  py_cmd=(python3)
elif command -v py >/dev/null 2>&1; then
  py_cmd=(py -3)
else
  printf 'run-root-validation.test: python, python3, or py -3 is required\n' >&2
  exit 1
fi

# 0. The tracked exemplars must pass their validators.
bash "$helper" fixtures/run-root-example
bash skills/implementaudit/scripts/validate-phase.sh fixtures/run-root-example/phases/phase-1.md >/dev/null
bash skills/implementaudit/scripts/validate-phase.sh fixtures/phase-design/dmadv-greenfield-phase.md >/dev/null
bash skills/implementaudit/scripts/validate-phase.sh --explain >/dev/null

# 1. A run root built from the shipped templates must pass.
mkdir -p "$tmp/good/phases"
cp skills/implementaudit/templates/STATE.md "$tmp/good/STATE.md"
cp skills/implementaudit/templates/PROTOCOL.md "$tmp/good/PROTOCOL.md"
cp skills/implementaudit/templates/ROADMAP.md "$tmp/good/ROADMAP.md"
cp skills/implementaudit/templates/THINKING.md "$tmp/good/THINKING.md"
cp skills/implementaudit/templates/sidecars.md "$tmp/good/sidecars.md"
cp skills/implementaudit/templates/tools.md "$tmp/good/tools.md"
cp skills/implementaudit/templates/context.md "$tmp/good/context.md"
# Model a dispatched root: every phase row in ROADMAP has a spec file
# (dispatch-prep step 5 guarantees this before any run executes).
grep -oE '^\| *[0-9]+ *\|' "$tmp/good/ROADMAP.md" | grep -oE '[0-9]+' | sort -un | while read -r n; do
  printf 'stub\n' > "$tmp/good/phases/phase-$n.md"
done
bash "$helper" "$tmp/good"

# 2. An invented Status token must fail.
mkdir -p "$tmp/badstatus"
cp -r "$tmp/good/." "$tmp/badstatus/"
"${py_cmd[@]}" - "$tmp/badstatus/STATE.md" <<'PY'
import sys
from pathlib import Path
p = Path(sys.argv[1])
p.write_text(p.read_text(encoding="utf-8").replace("| Status | open |", "| Status | mostly-done |"), encoding="utf-8")
PY
if bash "$helper" "$tmp/badstatus" >/dev/null 2>&1; then
  printf 'run-root-validation.test: expected invented status token to fail\n' >&2
  exit 1
fi

# 3. A missing Andon log section must fail.
mkdir -p "$tmp/noandon"
cp -r "$tmp/good/." "$tmp/noandon/"
"${py_cmd[@]}" - "$tmp/noandon/STATE.md" <<'PY'
import sys
from pathlib import Path
p = Path(sys.argv[1])
p.write_text(p.read_text(encoding="utf-8").replace("## Andon log", "## Renamed log"), encoding="utf-8")
PY
if bash "$helper" "$tmp/noandon" >/dev/null 2>&1; then
  printf 'run-root-validation.test: expected missing Andon log to fail\n' >&2
  exit 1
fi

# 4. Missing STATE.md must fail.
mkdir -p "$tmp/empty"
if bash "$helper" "$tmp/empty" >/dev/null 2>&1; then
  printf 'run-root-validation.test: expected empty run root to fail\n' >&2
  exit 1
fi

# 5. Occurrence linkage (#5).
# 5a. A LEGACY Andon table (no Occ column) remains valid and resumable.
mkdir -p "$tmp/legacy"
cp -r "$tmp/good/." "$tmp/legacy/"
"${py_cmd[@]}" - "$tmp/legacy/STATE.md" <<'PY'
import sys
from pathlib import Path
p = Path(sys.argv[1])
s = p.read_text(encoding="utf-8")
s = s.replace(
    "| # | Occ | Phase | Class | Abnormality | Countermeasure | Rerun evidence | Outcome |",
    "| # | Phase | Class | Abnormality | Countermeasure | Rerun evidence | Outcome |")
s = s.replace("|---|---|---|---|---|---|---|---|",
              "|---|---|---|---|---|---|---|")
p.write_text(s, encoding="utf-8")
PY
bash "$helper" "$tmp/legacy" >/dev/null \
  || { printf 'run-root-validation.test: legacy Andon table must stay valid\n' >&2; exit 1; }

# 5b. A new-format table with linked plural rows (shared Occ id) passes.
mkdir -p "$tmp/plural"
cp -r "$tmp/good/." "$tmp/plural/"
"${py_cmd[@]}" - "$tmp/plural/STATE.md" <<'PY'
import sys
from pathlib import Path
p = Path(sys.argv[1])
s = p.read_text(encoding="utf-8")
s = s.replace("|---|---|---|---|---|---|---|---|",
              "|---|---|---|---|---|---|---|---|\n"
              "| 1 | o1 | 2 | failed-criterion | dup landing gate | dedupe | rerun gate | resolved |\n"
              "| 2 | o1 | 2 | evidence-mismatch | zero machine rows | regenerate | rerun extract | resolved |")
p.write_text(s, encoding="utf-8")
PY
bash "$helper" "$tmp/plural" >/dev/null \
  || { printf 'run-root-validation.test: linked plural rows must pass\n' >&2; exit 1; }

# 5c. A new-format row with an EMPTY Occ id fails (linkage required).
mkdir -p "$tmp/noocc"
cp -r "$tmp/good/." "$tmp/noocc/"
"${py_cmd[@]}" - "$tmp/noocc/STATE.md" <<'PY'
import sys
from pathlib import Path
p = Path(sys.argv[1])
s = p.read_text(encoding="utf-8")
s = s.replace("|---|---|---|---|---|---|---|---|",
              "|---|---|---|---|---|---|---|---|\n"
              "| 1 |  | 2 | failed-criterion | dup landing gate | dedupe | rerun gate | resolved |")
p.write_text(s, encoding="utf-8")
PY
if bash "$helper" "$tmp/noocc" >/dev/null 2>&1; then
  printf 'run-root-validation.test: new-format row without Occ id must fail\n' >&2
  exit 1
fi

# 6. Occurrence resolution + residual dispositions (#6).
res_case() {  # name, occurrence-line, residual-rows, expectation(pass|fail)
  local name="$1" occ="$2" rows="$3" expect="$4"
  mkdir -p "$tmp/$name"
  cp -r "$tmp/good/." "$tmp/$name/"
  RES_OCC="$occ" RES_ROWS="$rows" "${py_cmd[@]}" - "$tmp/$name/STATE.md" <<'PY'
import os, sys
from pathlib import Path
p = Path(sys.argv[1])
s = p.read_text(encoding="utf-8")
s = s.replace("Occurrence resolution: not-applicable",
              "Occurrence resolution: " + os.environ["RES_OCC"])
s = s.replace("| Residual | Consequential | Disposition | Owner / policy ref | Evidence |\n|---|---|---|---|---|",
              "| Residual | Consequential | Disposition | Owner / policy ref | Evidence |\n|---|---|---|---|---|\n" + os.environ["RES_ROWS"])
p.write_text(s, encoding="utf-8")
PY
  if [ "$expect" = pass ]; then
    bash "$helper" "$tmp/$name" >/dev/null \
      || { printf 'run-root-validation.test: %s expected PASS\n' "$name" >&2; exit 1; }
  else
    if bash "$helper" "$tmp/$name" >/dev/null 2>&1; then
      printf 'run-root-validation.test: %s expected FAIL\n' "$name" >&2; exit 1
    fi
  fi
}

# 6a. Quarantined artifact, cause unresolved: valid partial state — no
# failure classification (containment + residual rows with dispositions).
res_case res_partial "partially-resolved" \
"| broken artifact quarantined; cause open (2 candidates: race, stale cache) | yes | deferred | owner backlog | quarantine dir |" pass

# 6b. Owner-transferred residual permits closure bookkeeping.
res_case res_transfer "partially-resolved" \
"| flaky lane ownership | yes | transferred | ops-team (named) | handoff note |" pass

# 6c. Risk-accepted residual with policy reference is valid.
res_case res_risk "partially-resolved" \
"| legacy CRLF drift | no | risk-accepted | policy: repo-hygiene-v2 | ledger row 9 |" pass

# 6d. An invalid disposition token fails (e.g. 'resolved-ish').
res_case res_bad "partially-resolved" \
"| mystery crash | yes | resolved-ish | - | - |" fail

# 6e. An invented occurrence-resolution token fails.
res_case res_badocc "mostly-resolved" "" fail

# 5d. A new-format row with comma-separated classes fails: one class per
# row is what makes Occ linkage meaningful — plural defects record one
# row per class sharing an Occ id, never a multi-class cell (Fable
# review of PR #26).
mkdir -p "$tmp/multiclass"
cp -r "$tmp/good/." "$tmp/multiclass/"
"${py_cmd[@]}" - "$tmp/multiclass/STATE.md" <<'PY'
import sys
from pathlib import Path
p = Path(sys.argv[1])
s = p.read_text(encoding="utf-8")
s = s.replace("|---|---|---|---|---|---|---|---|",
              "|---|---|---|---|---|---|---|---|\n"
              "| 1 | o1 | 2 | failed-criterion, regression | two defects one row | c | r | resolved |")
p.write_text(s, encoding="utf-8")
PY
if bash "$helper" "$tmp/multiclass" >/dev/null 2>&1; then
  printf 'run-root-validation.test: comma-separated multi-class row must fail\n' >&2
  exit 1
fi

# 6f. A transferred residual with NO receiving owner fails — a transfer
# nobody receives silently evaporates (Fable review of PR #27).
res_case res_noowner "partially-resolved" \
"| lane handoff | yes | transferred | - | note |" fail

# 6g. A risk-accepted residual with no policy/authority reference fails.
res_case res_nopolicy "partially-resolved" \
"| crlf drift | no | risk-accepted |  | row 9 |" fail

# 6h. Control: axes stay independent — an UNRESOLVED occurrence with a
# properly dispositioned consequential residual remains a valid state.
res_case res_axes "unresolved" \
"| open cause | yes | deferred | owner backlog | ledger |" pass

# 7. Run-root self-enforcement and micro-run mode (#90).
fixture_root="fixtures/run-root"

# 7a. A declared micro root passes only under --micro.
bash "$helper" --micro "$fixture_root/micro-conformant/root" >/dev/null || {
  printf 'run-root-validation.test: micro-conformant expected PASS under --micro\n' >&2
  exit 1
}
if bash "$helper" "$fixture_root/micro-conformant/root" >/dev/null 2>&1; then
  printf 'run-root-validation.test: micro-conformant must fail full validation\n' >&2
  exit 1
fi
if bash "$helper" --micro "$fixture_root/micro-no-sentinel/root" >/dev/null 2>&1; then
  printf 'run-root-validation.test: micro root without .claimed must fail\n' >&2
  exit 1
fi

# 7b. A micro root cannot carry phased-dispatch artifacts.
if bash "$helper" --micro "$fixture_root/micro-with-phase-specs/root" >/dev/null 2>&1; then
  printf 'run-root-validation.test: micro root with phase specs must fail\n' >&2
  exit 1
fi
if bash "$helper" --micro "$fixture_root/micro-with-roadmap-phase-table/root" >/dev/null 2>&1; then
  printf 'run-root-validation.test: micro root with ROADMAP phase table must fail\n' >&2
  exit 1
fi
if bash "$helper" --micro "$fixture_root/micro-with-stage62-disposition/root" >/dev/null 2>&1; then
  printf 'run-root-validation.test: micro root with Stage 6.2 disposition must fail\n' >&2
  exit 1
fi

# 7c. A sentinel-vs-artifact mismatch is diagnosed as drift.
if drift_output="$(bash "$helper" "$fixture_root/claimed-then-drifted/root" 2>&1)"; then
  printf 'run-root-validation.test: claimed-then-drifted must fail\n' >&2
  exit 1
fi
printf '%s\n' "$drift_output" | grep -qi 'drift' || {
  printf 'run-root-validation.test: drift failure did not name drift\n' >&2
  exit 1
}

# 7d. Legacy roots without .claimed preserve v0.3.2 behavior.
bash "$helper" "$fixture_root/no-sentinel-legacy/root" >/dev/null || {
  printf 'run-root-validation.test: no-sentinel legacy root must stay valid\n' >&2
  exit 1
}

# 7e. Newly claimed roots refuse undeclared sibling concurrency.
if sibling_output="$(bash "$helper" --micro "$fixture_root/sibling-unmarked/root" 2>&1)"; then
  printf 'run-root-validation.test: undispositioned sibling must fail\n' >&2
  exit 1
fi
printf '%s\n' "$sibling_output" | grep -Fq 'old-root' || {
  printf 'run-root-validation.test: sibling failure did not list old-root\n' >&2
  exit 1
}

# 7f. Superseded and explicitly parallel siblings are valid controls.
bash "$helper" --micro "$fixture_root/sibling-dispositioned/root" >/dev/null || {
  printf 'run-root-validation.test: dispositioned sibling expected PASS\n' >&2
  exit 1
}
bash "$helper" --micro "$fixture_root/sibling-declared-parallel/root" >/dev/null || {
  printf 'run-root-validation.test: declared-parallel sibling expected PASS\n' >&2
  exit 1
}

# 7g. Transcript-only closure is not on-disk terminal evidence.
if bash "$helper" --micro "$fixture_root/terminal-marker-transcript-only/root" >/dev/null 2>&1; then
  printf 'run-root-validation.test: micro root without terminal marker must fail\n' >&2
  exit 1
fi

printf 'run-root-validation.test: ok\n'
