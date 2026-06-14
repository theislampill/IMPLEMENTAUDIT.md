#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

# Detect python (same logic as checkers)
if command -v python >/dev/null 2>&1; then
  PY=python
elif command -v python3 >/dev/null 2>&1; then
  PY=python3
elif command -v py >/dev/null 2>&1; then
  PY="py -3"
else
  echo "lean-discipline.test: SKIP (no python)" >&2; exit 0
fi

pass=0
fail=0
errors=()

ok() { pass=$((pass + 1)); }
fail_case() { fail=$((fail + 1)); errors+=("$1"); }

# Replace text in a file using python (cross-platform)
py_replace() {
  local file="$1" old="$2" new="$3"
  $PY -c "
import pathlib, sys
p=pathlib.Path(sys.argv[1])
p.write_text(p.read_text().replace(sys.argv[2], sys.argv[3]))
" "$file" "$old" "$new"
}

# ── Positive: current repo should pass ───────────────────────────────────────
if bash scripts/check-lean-discipline.sh >/dev/null 2>&1; then
  ok
else
  fail_case "FAIL: check-lean-discipline.sh should pass on current repo"
fi

# ── Helper: make temp copy of repo ───────────────────────────────────────────
make_temp() {
  local t
  t="$(mktemp -d)"
  cp -r . "$t/" 2>/dev/null || true
  echo "$t"
}

# ── Negative: missing lean-operating-discipline.md ───────────────────────────
T=$(make_temp)
rm -f "$T/skills/implementaudit/references/lean-operating-discipline.md"
if ! bash "$T/scripts/check-lean-discipline.sh" >/dev/null 2>&1; then ok
else fail_case "FAIL: should fail when lean-operating-discipline.md absent"; fi
rm -rf "$T"

# ── Negative: 5S_CHECK missing from PROTOCOL.md ──────────────────────────────
T=$(make_temp)
py_replace "$T/skills/implementaudit/templates/PROTOCOL.md" "5S_CHECK" "FIVES_REMOVED"
if ! bash "$T/scripts/check-lean-discipline.sh" >/dev/null 2>&1; then ok
else fail_case "FAIL: should fail when 5S_CHECK missing from PROTOCOL.md"; fi
rm -rf "$T"

# ── Negative: Jidoka chain missing from PROTOCOL.md ──────────────────────────
T=$(make_temp)
# Replace all jidoka/Jidoka/JIDOKA occurrences with a neutral string that
# does not contain "jidoka" as a substring (so the checker can't find it)
$PY -c "
import pathlib, re, sys
p=pathlib.Path(sys.argv[1])
t=re.sub(r'[Jj][Ii][Dd][Oo][Kk][Aa]', 'STOP_SIGNAL', p.read_text())
p.write_text(t)
" "$T/skills/implementaudit/templates/PROTOCOL.md"
if ! bash "$T/scripts/check-lean-discipline.sh" >/dev/null 2>&1; then ok
else fail_case "FAIL: should fail when Jidoka chain missing from PROTOCOL.md"; fi
rm -rf "$T"

# ── Negative: Muda/Mura/Muri missing from THINKING.md ────────────────────────
T=$(make_temp)
py_replace "$T/skills/implementaudit/templates/THINKING.md" "Muda" "WASTE_REMOVED"
py_replace "$T/skills/implementaudit/templates/THINKING.md" "muda" "waste_removed"
if ! bash "$T/scripts/check-lean-discipline.sh" >/dev/null 2>&1; then ok
else fail_case "FAIL: should fail when Muda/Mura/Muri missing from THINKING.md"; fi
rm -rf "$T"

# ── Negative: DMAIC missing from routing.md ──────────────────────────────────
T=$(make_temp)
# Replace DMAIC/dmaic with a string that does NOT start with "dmaic"
$PY -c "
import pathlib, re, sys
p=pathlib.Path(sys.argv[1])
t=re.sub(r'[Dd][Mm][Aa][Ii][Cc]', 'REPAIR_ROUTE', p.read_text())
p.write_text(t)
" "$T/skills/implementaudit/references/routing.md"
if ! bash "$T/scripts/check-lean-discipline.sh" >/dev/null 2>&1; then ok
else fail_case "FAIL: should fail when DMAIC missing from routing.md"; fi
rm -rf "$T"

# ── Negative: certification overclaim in lean reference ──────────────────────
T=$(make_temp)
$PY -c "
import pathlib, sys
p=pathlib.Path(sys.argv[1])
p.write_text(p.read_text() + '\nThis run achieves six sigma certification.\n')
" "$T/skills/implementaudit/references/lean-operating-discipline.md"
if ! bash "$T/scripts/check-lean-discipline.sh" >/dev/null 2>&1; then ok
else fail_case "FAIL: should fail when certification overclaim in lean reference"; fi
rm -rf "$T"

# ── Negative: missing fixture ─────────────────────────────────────────────────
T=$(make_temp)
rm -f "$T/fixtures/lean/brownfield-dmaic-release-repair.md"
if ! bash "$T/scripts/check-lean-discipline.sh" >/dev/null 2>&1; then ok
else fail_case "FAIL: should fail when a required lean fixture is absent"; fi
rm -rf "$T"

# ── Negative: quality route missing from phase-goal.txt ──────────────────────
T=$(make_temp)
py_replace "$T/skills/implementaudit/templates/phase-goal.txt" "Quality route:" "QUALITY_REMOVED:"
if ! bash "$T/scripts/check-lean-discipline.sh" >/dev/null 2>&1; then ok
else fail_case "FAIL: should fail when Quality route field missing from phase-goal.txt"; fi
rm -rf "$T"

# ── Negative: Graphify terrain leverage section missing from lean reference ──
T=$(make_temp)
$PY -c "
import pathlib, re, sys
p=pathlib.Path(sys.argv[1])
t=re.sub(r'[Gg]raphify terrain leverage', 'GRAPHIFY_LEVERAGE_REMOVED', p.read_text())
p.write_text(t)
" "$T/skills/implementaudit/references/lean-operating-discipline.md"
if ! bash "$T/scripts/check-lean-discipline.sh" >/dev/null 2>&1; then ok
else fail_case "FAIL: should fail when Graphify terrain leverage section missing from lean reference"; fi
rm -rf "$T"

# ── Negative: ActiveGraph custody events section missing from lean reference ─
T=$(make_temp)
$PY -c "
import pathlib, re, sys
p=pathlib.Path(sys.argv[1])
t=re.sub(r'[Aa]ctive[Gg]raph custody events', 'ACTIVEGRAPH_CUSTODY_REMOVED', p.read_text())
p.write_text(t)
" "$T/skills/implementaudit/references/lean-operating-discipline.md"
if ! bash "$T/scripts/check-lean-discipline.sh" >/dev/null 2>&1; then ok
else fail_case "FAIL: should fail when ActiveGraph custody events section missing from lean reference"; fi
rm -rf "$T"

# ── Negative: Jidoka/Andon reduced to a generic error label ─────────────────
T=$(make_temp)
$PY -c "
import pathlib, re, sys
p=pathlib.Path(sys.argv[1])
t=p.read_text()
t=re.sub(r'\| Jidoka \|[^\\n]+', '| Jidoka | Generic error label for failures. | skills/implementaudit/templates/PROTOCOL.md | check-planner-stages.sh |', t)
t=re.sub(r'\| Andon \|[^\\n]+', '| Andon | Generic error label for failures. | skills/implementaudit/SKILL.md | check-planner-stages.sh |', t)
p.write_text(t)
" "$T/skills/implementaudit/references/lean-operating-discipline.md"
if ! bash "$T/scripts/check-lean-discipline.sh" >/dev/null 2>&1; then ok
else fail_case "FAIL: should fail when Jidoka/Andon are generic error labels"; fi
rm -rf "$T"

# ── Negative: Poka-yoke without a concrete prevention mechanism ─────────────
T=$(make_temp)
$PY -c "
import pathlib, re, sys
p=pathlib.Path(sys.argv[1])
t=re.sub(r'\| Poka-yoke \|[^\\n]+', '| Poka-yoke | Quality improvement mindset for better work. | skills/implementaudit/references/lean-operating-discipline.md | verify-package.sh |', p.read_text())
p.write_text(t)
" "$T/skills/implementaudit/references/lean-operating-discipline.md"
if ! bash "$T/scripts/check-lean-discipline.sh" >/dev/null 2>&1; then ok
else fail_case "FAIL: should fail when Poka-yoke lacks concrete prevention mechanism"; fi
rm -rf "$T"

# ── Negative: Standard Work without stable repo-specific rule/template ──────
T=$(make_temp)
$PY -c "
import pathlib, re, sys
p=pathlib.Path(sys.argv[1])
t=re.sub(r'\| Standard Work \|[^\\n]+', '| Standard Work | Repeat good habits whenever possible. | skills/implementaudit/references/lean-operating-discipline.md | verify-package.sh |', p.read_text())
p.write_text(t)
" "$T/skills/implementaudit/references/lean-operating-discipline.md"
if ! bash "$T/scripts/check-lean-discipline.sh" >/dev/null 2>&1; then ok
else fail_case "FAIL: should fail when Standard Work lacks stable repo-specific rule/template"; fi
rm -rf "$T"

# ── Summary ───────────────────────────────────────────────────────────────────
total=$((pass + fail))
if [ "$fail" -eq 0 ]; then
  printf 'lean-discipline.test: ok (%d/%d)\n' "$pass" "$total"
else
  for e in "${errors[@]}"; do printf '%s\n' "$e" >&2; done
  printf 'lean-discipline.test: FAIL (%d/%d passed)\n' "$pass" "$total" >&2
  exit 1
fi
