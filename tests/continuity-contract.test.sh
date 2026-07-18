#!/usr/bin/env bash
# continuity-contract.test.sh — context-epoch continuity contract (#35).
#
# Deterministic checks over the shipped contract surfaces plus validator
# behavior with negative controls. Behavioral (model-in-the-loop) coverage
# is the separately versioned B3 supplementary baseline; this test pins the
# product bytes and the mechanical state checks.
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

helper="skills/implementaudit/scripts/validate-run-root.sh"
ref="skills/implementaudit/references/continuity.md"
proto="skills/implementaudit/templates/PROTOCOL.md"
state_t="skills/implementaudit/templates/STATE.md"
tc="skills/implementaudit/references/transcript-contract.md"

if command -v python >/dev/null 2>&1; then
  py_cmd=(python)
elif command -v python3 >/dev/null 2>&1; then
  py_cmd=(python3)
elif command -v py >/dev/null 2>&1; then
  py_cmd=(py -3)
else
  printf 'continuity-contract.test: python, python3, or py -3 is required\n' >&2
  exit 1
fi

fail() { printf 'continuity-contract.test: %s\n' "$*" >&2; exit 1; }

# 1. Contract surfaces exist and carry the load-bearing vocabulary.
[ -f "$ref" ] || fail "missing $ref"
for tok in host-reported-compaction new-session handoff-resume manual-resume \
           inferred-context-gap one-shot-action standing-constraint \
           standing-authorization persistent-objective \
           query-or-information-request; do
  grep -q "$tok" "$ref" || fail "reference missing token: $tok"
  grep -q "$tok" "$proto" || fail "PROTOCOL template missing token: $tok"
done
for st in active satisfied superseded revoked expired ambiguous; do
  grep -qw "$st" "$ref" || fail "reference missing status: $st"
done
grep -qi "observation of history" "$ref" || fail "reference missing summary-is-observation rule"
grep -qi "Target already satisfied at" "$ref" || fail "reference missing refusal sentence"
grep -qi "Target already satisfied at" "$proto" || fail "PROTOCOL missing refusal sentence"
grep -qi "uninterrupted turn crosses no boundary" "$proto" || fail "PROTOCOL missing no-extra-ceremony rule"
grep -qi "never a fabricated compaction" "$state_t" || fail "STATE template missing honest-provenance rule"
grep -qi "Context epochs and instruction applicability" "$state_t" || fail "STATE template missing epoch section"
grep -qi "NO new marker" "$tc" || fail "transcript contract missing no-new-marker rule"
grep -q "references/continuity.md" skills/implementaudit/SKILL.md || fail "SKILL.md load map missing continuity reference"

# 2. Template-built root (empty epoch tables) passes; a stripped legacy
# root (no epoch section at all) also passes — old roots stay resumable.
mkdir -p "$tmp/good/phases"
for f in STATE.md PROTOCOL.md ROADMAP.md THINKING.md sidecars.md tools.md context.md; do
  cp "skills/implementaudit/templates/$f" "$tmp/good/$f"
done
grep -oE '^\| *[0-9]+ *\|' "$tmp/good/ROADMAP.md" | grep -oE '[0-9]+' | sort -un | while read -r n; do
  printf 'stub\n' > "$tmp/good/phases/phase-$n.md"
done
bash "$helper" "$tmp/good" >/dev/null

mkdir -p "$tmp/legacy"
cp -r "$tmp/good/." "$tmp/legacy/"
"${py_cmd[@]}" - "$tmp/legacy/STATE.md" <<'PY'
import re, sys
from pathlib import Path
p = Path(sys.argv[1])
s = p.read_text(encoding="utf-8")
s = re.sub(r"## Context epochs and instruction applicability.*?(?=## AGENTS_UPDATE_DECISION)", "", s, flags=re.S)
p.write_text(s, encoding="utf-8")
PY
grep -qi "Context epochs" "$tmp/legacy/STATE.md" && fail "legacy fixture still has the epoch section"
bash "$helper" "$tmp/legacy" >/dev/null || fail "legacy root without epoch section must remain valid"

# Helper: append rows under the epoch section and expect pass/fail.
epoch_case() {
  local name="$1" epoch_row="$2" instr_row="$3" want="$4"
  mkdir -p "$tmp/$name"
  cp -r "$tmp/good/." "$tmp/$name/"
  "${py_cmd[@]}" - "$tmp/$name/STATE.md" "$epoch_row" "$instr_row" <<'PY'
import sys
from pathlib import Path
p = Path(sys.argv[1])
erow, irow = sys.argv[2], sys.argv[3]
s = p.read_text(encoding="utf-8")
anchor = "| Epoch | Boundary provenance | Established at | Repo identity | Reconciled | Notes |\n|---|---|---|---|---|---|"
if erow:
    s = s.replace(anchor, anchor + "\n" + erow)
ianchor = "| Instr | Reference | Kind | Authority | Subject | Issued epoch | Status | Status evidence | Supersedes/by | Scope end |\n|---|---|---|---|---|---|---|---|---|---|"
if irow:
    s = s.replace(ianchor, ianchor + "\n" + irow)
p.write_text(s, encoding="utf-8")
PY
  if bash "$helper" "$tmp/$name" >/dev/null 2>&1; then got=pass; else got=fail; fi
  [ "$got" = "$want" ] || fail "case $name: wanted $want, got $got"
}

# 3. Valid epoch + applicability rows pass: honest compaction provenance,
# a satisfied one-shot WITH evidence, and a standing constraint that
# stays active across the boundary (controls 4/5: not consumed).
epoch_case ok_rows \
"| e2 | host-reported-compaction | 2026-07-18T02:00Z | repo@abc def | yes | - |" \
"| i1 | evt-4402508-hash | one-shot-action | owner | ANDON 150 | e1 | satisfied | rerun evidence ledger row 7 | - | - |" pass
epoch_case ok_standing \
"| e2 | new-session | 2026-07-18T02:10Z | repo@abc def | yes | - |" \
"| i2 | evt-11aa22-hash | standing-constraint | owner | do-not-push | e1 | active | n/a — standing | - | until revoked |" pass

# 4. A fabricated/invented provenance token fails (honest provenance only).
epoch_case bad_prov \
"| e2 | assumed-compaction | 2026-07-18T02:00Z | repo@abc def | yes | - |" "" fail

# 5. Invalid instruction kind or status tokens fail.
epoch_case bad_kind \
"| e2 | manual-resume | 2026-07-18T02:00Z | repo@abc def | yes | - |" \
"| i1 | evt-h | replayable-action | owner | ANDON 150 | e1 | active | - | - | - |" fail
epoch_case bad_status \
"| e2 | manual-resume | 2026-07-18T02:00Z | repo@abc def | yes | - |" \
"| i1 | evt-h | one-shot-action | owner | ANDON 150 | e1 | done | - | - | - |" fail

# 6. A terminal status with NO status evidence fails — the bare
# "satisfied" claim is precisely the replay hazard (#35).
epoch_case bare_satisfied \
"| e2 | handoff-resume | 2026-07-18T02:00Z | repo@abc def | yes | - |" \
"| i1 | evt-h | one-shot-action | owner | ANDON 150 | e1 | satisfied |  | - | - |" fail
epoch_case bare_revoked \
"| e2 | inferred-context-gap | 2026-07-18T02:00Z | repo@abc def | yes | - |" \
"| i1 | evt-h | standing-authorization | owner | commit-auth | e1 | revoked | - | - | - |" fail

printf 'continuity-contract.test: ok (surfaces + validator: legacy pass, honest-provenance, kind/status tokens, terminal-status evidence)\n'
