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

printf 'run-root-validation.test: ok\n'
