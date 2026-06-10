#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

helper="skills/scripts/validate-run-root.sh"

# 0. The tracked exemplars must pass their validators.
bash "$helper" fixtures/run-root-example
bash skills/scripts/validate-phase.sh fixtures/run-root-example/phases/phase-1.md >/dev/null
bash skills/scripts/validate-phase.sh fixtures/phase-design/dmadv-greenfield-phase.md >/dev/null
bash skills/scripts/validate-phase.sh --explain >/dev/null

# 1. A run root built from the shipped templates must pass.
mkdir -p "$tmp/good/phases"
cp skills/templates/STATE.md "$tmp/good/STATE.md"
cp skills/templates/PROTOCOL.md "$tmp/good/PROTOCOL.md"
cp skills/templates/ROADMAP.md "$tmp/good/ROADMAP.md"
cp skills/templates/THINKING.md "$tmp/good/THINKING.md"
cp skills/templates/sidecars.md "$tmp/good/sidecars.md"
cp skills/templates/tools.md "$tmp/good/tools.md"
cp skills/templates/context.md "$tmp/good/context.md"
# Model a dispatched root: every phase row in ROADMAP has a spec file
# (dispatch-prep step 5 guarantees this before any run executes).
grep -oE '^\| *[0-9]+ *\|' "$tmp/good/ROADMAP.md" | grep -oE '[0-9]+' | sort -un | while read -r n; do
  printf 'stub\n' > "$tmp/good/phases/phase-$n.md"
done
bash "$helper" "$tmp/good"

# 2. An invented Status token must fail.
mkdir -p "$tmp/badstatus"
cp -r "$tmp/good/." "$tmp/badstatus/"
python - "$tmp/badstatus/STATE.md" <<'PY'
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
python - "$tmp/noandon/STATE.md" <<'PY'
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

printf 'run-root-validation.test: ok\n'
