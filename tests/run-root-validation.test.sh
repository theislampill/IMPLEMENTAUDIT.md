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

printf 'run-root-validation.test: ok\n'
