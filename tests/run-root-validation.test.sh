#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

tmp="$(mktemp -d)"
trajectory_review_dir=""
cleanup() {
  rm -rf "$tmp"
  if [ -n "$trajectory_review_dir" ]; then
    rm -rf "$trajectory_review_dir"
  fi
}
trap cleanup EXIT

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

# Digest-bound second-independent-review trajectory enforcement. This runs
# before the inherited DONE/tools-template RED so the two claims remain
# independently observable.
trajectory_review_dir="$(mktemp -d "$repo_root/.trajectory-reviews.XXXXXX")"
review_a="$trajectory_review_dir/review-a.md"
review_b="$trajectory_review_dir/review-b.md"
review_pass="$trajectory_review_dir/review-pass.md"
printf '# Independent candidate review A\n\nHC_H7A_TEST_REVIEW_A: NEEDS_REVISION\n' > "$review_a"
printf '# Independent candidate review B\n\nHC_H7A_TEST_REVIEW_B: NEEDS_REVISION\n' > "$review_b"
printf '# Independent candidate review control\n\nHC_H7A_TEST_REVIEW_CONTROL: PASS\n' > "$review_pass"
review_a_rel="${review_a#"$repo_root/"}"
review_b_rel="${review_b#"$repo_root/"}"
review_pass_rel="${review_pass#"$repo_root/"}"
review_a_sha="$(sha256sum "$review_a" | awk '{print $1}')"
review_b_sha="$(sha256sum "$review_b" | awk '{print $1}')"
review_pass_sha="$(sha256sum "$review_pass" | awk '{print $1}')"

make_review_trajectory_root() {
  local name="$1" second_class="$2" second_owner="$3" second_path="$4" second_sha="$5" decision="${6:-}"
  local root="$tmp/$name" state
  mkdir -p "$root"
  cp -r "$tmp/good/." "$root/"
  state="$root/STATE.md"
  "${py_cmd[@]}" - "$state" "$review_a_rel" "$review_a_sha" "$second_path" "$second_sha" "$second_class" "$second_owner" "$decision" <<'PY'
import sys
from pathlib import Path

state_path = Path(sys.argv[1])
review_a, sha_a, review_b, sha_b, second_class, second_owner, decision = sys.argv[2:]
payload = state_path.read_text(encoding="utf-8")
artifact_header = "| Artifact | Status | Notes |\n|---|---|---|"
artifact_rows = (
    f"{artifact_header}\n"
    f"| `{review_a}` | independent review | SHA-256 `{sha_a}`; NEEDS_REVISION |\n"
    f"| `{review_b}` | independent review | SHA-256 `{sha_b}`; NEEDS_REVISION |"
)
if payload.count(artifact_header) != 1:
    raise SystemExit("run-root-validation.test: expected one Runtime artifacts header")
payload = payload.replace(artifact_header, artifact_rows, 1)
occurrence = "## Occurrence resolution and residuals"
rows = (
    "| 901 | trajectory-a | direct | regression | candidate countermeasure failed | repair; owner/source=eval/shared-owner.py | "
    f"`{review_a}` | resolved |\n"
    f"| 902 | trajectory-b | direct | {second_class} | candidate countermeasure failed | repair; owner/source={second_owner} | "
    f"`{review_b}` | resolved |\n"
)
if decision:
    rows += f"\nMechanism-replacement decision: {decision}\n"
if payload.count(occurrence) != 1:
    raise SystemExit("run-root-validation.test: expected one occurrence-resolution heading")
state_path.write_text(payload.replace(occurrence, rows + "\n" + occurrence, 1), encoding="utf-8")
PY
}

make_review_trajectory_root trajectory-two-reviews-no-decision \
  regression eval/shared-owner.py "$review_b_rel" "$review_b_sha"
if bash "$helper" "$tmp/trajectory-two-reviews-no-decision" >/dev/null 2>&1; then
  printf 'run-root-validation.test: two digest-bound independent same-family/owner reviews must require a decision\n' >&2
  exit 1
fi

make_review_trajectory_root trajectory-one-review \
  regression eval/shared-owner.py "$review_a_rel" "$review_a_sha"
bash "$helper" "$tmp/trajectory-one-review" >/dev/null || {
  printf 'run-root-validation.test: duplicate review identity must not establish the trajectory trigger\n' >&2
  exit 1
}

make_review_trajectory_root trajectory-duplicate-occurrence \
  regression eval/shared-owner.py "$review_b_rel" "$review_b_sha"
sed -i 's/| 902 | trajectory-b |/| 902 | trajectory-a |/' \
  "$tmp/trajectory-duplicate-occurrence/STATE.md"
bash "$helper" "$tmp/trajectory-duplicate-occurrence" >/dev/null || {
  printf 'run-root-validation.test: duplicate Andon occurrence must not establish the trajectory trigger\n' >&2
  exit 1
}

make_review_trajectory_root trajectory-unrelated-family \
  failed-criterion eval/shared-owner.py "$review_b_rel" "$review_b_sha"
bash "$helper" "$tmp/trajectory-unrelated-family" >/dev/null || {
  printf 'run-root-validation.test: unrelated review families must not establish the trajectory trigger\n' >&2
  exit 1
}

make_review_trajectory_root trajectory-different-owner \
  regression eval/other-owner.py "$review_b_rel" "$review_b_sha"
bash "$helper" "$tmp/trajectory-different-owner" >/dev/null || {
  printf 'run-root-validation.test: different review owners must not establish the trajectory trigger\n' >&2
  exit 1
}

make_review_trajectory_root trajectory-digest-mismatch \
  regression eval/shared-owner.py "$review_b_rel" "f${review_b_sha:1}"
bash "$helper" "$tmp/trajectory-digest-mismatch" >/dev/null || {
  printf 'run-root-validation.test: digest mismatch must not establish the trajectory trigger\n' >&2
  exit 1
}

make_review_trajectory_root trajectory-missing-artifact \
  regression eval/shared-owner.py '.trajectory-reviews.missing/review.md' "$review_b_sha"
bash "$helper" "$tmp/trajectory-missing-artifact" >/dev/null || {
  printf 'run-root-validation.test: missing review artifact must not establish the trajectory trigger\n' >&2
  exit 1
}

make_review_trajectory_root trajectory-terminal-disposition-mismatch \
  regression eval/shared-owner.py "$review_pass_rel" "$review_pass_sha"
bash "$helper" "$tmp/trajectory-terminal-disposition-mismatch" >/dev/null || {
  printf 'run-root-validation.test: terminal review disposition mismatch must not establish the trajectory trigger\n' >&2
  exit 1
}

mkdir -p "$tmp/trajectory-review-words-only"
cp -r "$tmp/good/." "$tmp/trajectory-review-words-only/"
printf '\nIndependent review NEEDS_REVISION words without a bound artifact are narrative only.\n' \
  >> "$tmp/trajectory-review-words-only/STATE.md"
bash "$helper" "$tmp/trajectory-review-words-only" >/dev/null || {
  printf 'run-root-validation.test: review-like narrative words must not establish the trajectory trigger\n' >&2
  exit 1
}

for decision in \
  'replace-mechanism (shared parser)' \
  'continue (complete admitted convergence model)' \
  'escalate-to-convergence-mode (shared invariant)'; do
  decision_name="${decision%% *}"
  make_review_trajectory_root "trajectory-with-$decision_name" \
    regression eval/shared-owner.py "$review_b_rel" "$review_b_sha" "$decision"
  bash "$helper" "$tmp/trajectory-with-$decision_name" >/dev/null || {
    printf 'run-root-validation.test: digest-bound trajectory with %s decision expected PASS\n' "$decision_name" >&2
    exit 1
  }
done

# 1b. #139 full-mode evidence resolution. Only a phase explicitly marked done
# resolves current mandatory-command capture grammar; open phases remain cheap.
write_capture_phase() {
  local path="$1" status="$2" capture="$3"
  cat > "$path" <<EOF
IMPLEMENTAUDIT_PHASE_START
## Mandatory commands
- true > $capture 2>&1 — property: structural; scope: fixture; coverage: full; capture: $capture; expected: exit 0
IMPLEMENTAUDIT_PHASE_VERIFY
IMPLEMENTAUDIT_PHASE_DONE
Status: $status
EOF
}

mkdir -p "$tmp/done-capture-missing"
cp -r "$tmp/good/." "$tmp/done-capture-missing/"
write_capture_phase "$tmp/done-capture-missing/phases/phase-1.md" done \
  '<run-root>/evidence/mandatory.log'
if bash "$helper" "$tmp/done-capture-missing" >/dev/null 2>&1; then
  printf 'run-root-validation.test: DONE phase with missing capture must fail\n' >&2
  exit 1
fi

mkdir -p "$tmp/legacy-roadmap-done-missing"
cp -r "$tmp/done-capture-missing/." "$tmp/legacy-roadmap-done-missing/"
sed -i '/^Status: done$/d' "$tmp/legacy-roadmap-done-missing/phases/phase-1.md"
sed -i 's/| 1 |  |  | - |  |  |  | open |/| 1 | legacy | owner | - | smoke | smoke | n\/a | focused PASS |/' \
  "$tmp/legacy-roadmap-done-missing/ROADMAP.md"
sed -i '1i| 1 | unrelated numbered row | open |' \
  "$tmp/legacy-roadmap-done-missing/ROADMAP.md"
if bash "$helper" "$tmp/legacy-roadmap-done-missing" >/dev/null 2>&1; then
  printf 'run-root-validation.test: legacy ROADMAP-terminal phase with missing capture must fail\n' >&2
  exit 1
fi

mkdir -p "$tmp/roadmap-complete-semicolon"
cp -r "$tmp/legacy-roadmap-done-missing/." "$tmp/roadmap-complete-semicolon/"
sed -i 's/focused PASS/complete; finalized/' \
  "$tmp/roadmap-complete-semicolon/ROADMAP.md"
if bash "$helper" "$tmp/roadmap-complete-semicolon" >/dev/null 2>&1; then
  printf 'run-root-validation.test: ROADMAP complete-semicolon phase with missing capture must fail\n' >&2
  exit 1
fi

mkdir -p "$tmp/historical-local-status"
cp -r "$tmp/legacy-roadmap-done-missing/." "$tmp/historical-local-status/"
printf 'Status: FINDINGS_CLOSED_PASS\n' \
  >> "$tmp/historical-local-status/phases/phase-1.md"
if bash "$helper" "$tmp/historical-local-status" >/dev/null 2>&1; then
  printf 'run-root-validation.test: unknown historical status must fall back to terminal ROADMAP\n' >&2
  exit 1
fi

mkdir -p "$tmp/explicit-nonterminal-status"
cp -r "$tmp/historical-local-status/." "$tmp/explicit-nonterminal-status/"
sed -i 's/Status: FINDINGS_CLOSED_PASS/Status: open/' \
  "$tmp/explicit-nonterminal-status/phases/phase-1.md"
bash "$helper" "$tmp/explicit-nonterminal-status" >/dev/null || {
  printf 'run-root-validation.test: explicit nonterminal status must suppress ROADMAP fallback\n' >&2
  exit 1
}

mkdir -p "$tmp/done-capture-blank/evidence"
cp -r "$tmp/good/." "$tmp/done-capture-blank/"
write_capture_phase "$tmp/done-capture-blank/phases/phase-1.md" done \
  '<run-root>/evidence/mandatory.log'
: > "$tmp/done-capture-blank/evidence/mandatory.log"
if bash "$helper" "$tmp/done-capture-blank" >/dev/null 2>&1; then
  printf 'run-root-validation.test: DONE phase with blank capture must fail\n' >&2
  exit 1
fi

mkdir -p "$tmp/done-capture-whitespace/evidence"
cp -r "$tmp/good/." "$tmp/done-capture-whitespace/"
write_capture_phase "$tmp/done-capture-whitespace/phases/phase-1.md" done \
  '<run-root>/evidence/mandatory.log'
printf ' \n\t\n' > "$tmp/done-capture-whitespace/evidence/mandatory.log"
if bash "$helper" "$tmp/done-capture-whitespace" >/dev/null 2>&1; then
  printf 'run-root-validation.test: DONE phase with whitespace-only capture must fail\n' >&2
  exit 1
fi

mkdir -p "$tmp/done-capture-present/evidence"
cp -r "$tmp/good/." "$tmp/done-capture-present/"
write_capture_phase "$tmp/done-capture-present/phases/phase-1.md" done \
  '<run-root>/evidence/mandatory.log'
printf 'producer exit 0\n' > "$tmp/done-capture-present/evidence/mandatory.log"
bash "$helper" "$tmp/done-capture-present" >/dev/null || {
  printf 'run-root-validation.test: DONE phase with nonblank capture must pass\n' >&2
  exit 1
}

mkdir -p "$tmp/repo-relative/.IMPLEMENTAUDIT/runs/example/evidence"
cp -r "$tmp/good/." "$tmp/repo-relative/.IMPLEMENTAUDIT/runs/example/"
write_capture_phase "$tmp/repo-relative/.IMPLEMENTAUDIT/runs/example/phases/phase-1.md" \
  'PASS - focused gates' \
  '../repo-relative/.IMPLEMENTAUDIT/runs/example/evidence/mandatory.log'
printf 'producer exit 0\n' \
  > "$tmp/repo-relative/.IMPLEMENTAUDIT/runs/example/evidence/mandatory.log"
bash "$helper" "$tmp/repo-relative/.IMPLEMENTAUDIT/runs/example" >/dev/null || {
  printf 'run-root-validation.test: repo-relative capture from absolute run root must pass\n' >&2
  exit 1
}
rm "$tmp/repo-relative/.IMPLEMENTAUDIT/runs/example/evidence/mandatory.log"
if bash "$helper" "$tmp/repo-relative/.IMPLEMENTAUDIT/runs/example" >/dev/null 2>&1; then
  printf 'run-root-validation.test: descriptive PASS status with missing capture must fail\n' >&2
  exit 1
fi

mkdir -p "$tmp/unresolved-variable"
cp -r "$tmp/good/." "$tmp/unresolved-variable/"
write_capture_phase "$tmp/unresolved-variable/phases/phase-1.md" done \
  '$EVIDENCE_ROOT/legacy.log'
bash "$helper" "$tmp/unresolved-variable" >/dev/null || {
  printf 'run-root-validation.test: unresolved legacy capture variable must remain compatible\n' >&2
  exit 1
}

mkdir -p "$tmp/open-capture-missing"
cp -r "$tmp/good/." "$tmp/open-capture-missing/"
write_capture_phase "$tmp/open-capture-missing/phases/phase-1.md" open \
  '<run-root>/evidence/mandatory.log'
bash "$helper" "$tmp/open-capture-missing" >/dev/null || {
  printf 'run-root-validation.test: open phase capture must not resolve early\n' >&2
  exit 1
}

mkdir -p "$tmp/blank-planning-artifact"
cp -r "$tmp/good/." "$tmp/blank-planning-artifact/"
: > "$tmp/blank-planning-artifact/tools.md"
if bash "$helper" "$tmp/blank-planning-artifact" >/dev/null 2>&1; then
  printf 'run-root-validation.test: blank required planning artifact must fail\n' >&2
  exit 1
fi

mkdir -p "$tmp/whitespace-planning-artifact"
cp -r "$tmp/good/." "$tmp/whitespace-planning-artifact/"
printf ' \n\t\n' > "$tmp/whitespace-planning-artifact/tools.md"
if bash "$helper" "$tmp/whitespace-planning-artifact" >/dev/null 2>&1; then
  printf 'run-root-validation.test: whitespace-only planning artifact must fail\n' >&2
  exit 1
fi

mkdir -p "$tmp/template-only-done"
cp -r "$tmp/good/." "$tmp/template-only-done/"
sed -i 's/| Status | open |/| Status | DONE |/' \
  "$tmp/template-only-done/STATE.md"
sed -i 's#| `<run-root>/tools.md` | open |#| `<run-root>/tools.md` | complete |#' \
  "$tmp/template-only-done/STATE.md"
for f in ROADMAP.md THINKING.md sidecars.md context.md; do
  printf '\nfixture populated\n' >> "$tmp/template-only-done/$f"
done
template_output="$(bash "$helper" "$tmp/template-only-done" 2>&1 || true)"
if ! grep -Fq 'planning artifact remains an unfilled template at DONE: tools.md' \
  <<<"$template_output"; then
  printf 'run-root-validation.test: DONE root must reject an unfilled tools template\n' >&2
  exit 1
fi

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

# #87: concurrent mutation is one owner-authorized residual disposition. An
# unknown near-miss stays red.
res_case res_concurrent "partially-resolved" \
"| finding moved under review | yes | SUPERSEDED_BY_CONCURRENT_MUTATION | phase re-anchor | closure receipt |" pass
res_case res_concurrent_bad "partially-resolved" \
"| finding moved under review | yes | SUPERSEDED_BY_OTHER_MUTATION | phase re-anchor | closure receipt |" fail

# #87 canonical identity row. Legacy roots need no row. A requested/actual
# mismatch requires both transport Andon evidence and unbound claims.
identity_case() { # name, row, add-andon, expectation
  local name="$1" row="$2" add_andon="$3" expect="$4"
  mkdir -p "$tmp/$name"
  cp -r "$tmp/good/." "$tmp/$name/"
  printf '%s\n' "$row" >> "$tmp/$name/STATE.md"
  if [ "$add_andon" != no ]; then
    ANDON_EVENT="$add_andon" "${py_cmd[@]}" - "$tmp/$name/STATE.md" <<'PY'
import os, sys
from pathlib import Path
p = Path(sys.argv[1])
s = p.read_text(encoding="utf-8")
s = s.replace("|---|---|---|---|---|---|---|---|",
              "|---|---|---|---|---|---|---|---|\n"
              "| 87 | o87 | 1 | transport-infrastructure | model substitution | bind claims | host-event:" + os.environ["ANDON_EVENT"] + " | resolved |", 1)
p.write_text(s, encoding="utf-8")
PY
  fi
  if [ "$expect" = pass ]; then
    bash "$helper" "$tmp/$name" >/dev/null \
      || { printf 'run-root-validation.test: %s expected PASS\n' "$name" >&2; exit 1; }
  elif bash "$helper" "$tmp/$name" >/dev/null 2>&1; then
    printf 'run-root-validation.test: %s expected FAIL\n' "$name" >&2; exit 1
  fi
}
identity_case identity_equal \
  'model-identity: requested_model: fable | actual_model: fable | evidence: self-report | claims: bound' no pass
identity_case identity_unbound_missing_andon \
  'model-identity: requested_model: fable | actual_model: opus | evidence: host-event:G0001 | claims: IDENTITY_UNBOUND' no fail
identity_case identity_unbound \
  'model-identity: requested_model: fable | actual_model: opus | evidence: host-event:G0001 | claims: IDENTITY_UNBOUND' G0001 pass
identity_case identity_unbound_wrong_event \
  'model-identity: requested_model: fable | actual_model: opus | evidence: host-event:missing-G0001 | claims: IDENTITY_UNBOUND' G0001 fail
identity_case identity_mismatch_bound \
  'model-identity: requested_model: fable | actual_model: opus | evidence: host-event:G0001 | claims: bound' G0001 fail
identity_case identity_malformed \
  'model-identity: requested: fable | actual: fable | evidence: self-report | claims: bound' no fail

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
  printf 'run-root-validation.test: micro root with cold-review disposition must fail\n' >&2
  exit 1
fi
for stage_label in 'Stage 6.i' 'Stage 6.2'; do
  stage_root="$tmp/micro-${stage_label// /-}"
  cp -R "$fixture_root/micro-conformant/root" "$stage_root"
  sed -i "/^AUDIT_COMPLETE$/i $stage_label: PASS" "$stage_root/STATE.md"
  if bash "$helper" --micro "$stage_root" >/dev/null 2>&1; then
    printf 'run-root-validation.test: micro root accepted %s disposition\n' "$stage_label" >&2
    exit 1
  fi
done

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

# 8. Mechanical second-order recurrence trigger (#91).
if recurrence_output="$(bash "$helper" --micro "$fixture_root/recurrence-3-same-class-same-file/root" 2>&1)"; then
  printf 'run-root-validation.test: recurring class on one owner/source must require a decision\n' >&2
  exit 1
fi
printf '%s\n' "$recurrence_output" | grep -Fq 'Mechanism-replacement decision:' || {
  printf 'run-root-validation.test: recurrence failure did not name the required decision\n' >&2
  exit 1
}

for decision_fixture in \
  recurrence-3-with-replace-decision \
  recurrence-3-with-continue-decision \
  recurrence-3-with-convergence-escalation; do
  bash "$helper" --micro "$fixture_root/$decision_fixture/root" >/dev/null || {
    printf 'run-root-validation.test: %s expected PASS\n' "$decision_fixture" >&2
    exit 1
  }
done

bash "$helper" --micro "$fixture_root/recurrence-3-different-files/root" >/dev/null || {
  printf 'run-root-validation.test: different-files control expected PASS\n' >&2
  exit 1
}
bash "$helper" --micro "$fixture_root/recurrence-3-different-classes/root" >/dev/null || {
  printf 'run-root-validation.test: different-classes control expected PASS\n' >&2
  exit 1
}

# The convergence-mode single-fault control is reused, not duplicated.
bash "$helper" --ledger fixtures/convergence-mode/single-fault-control.md >/dev/null || {
  printf 'run-root-validation.test: shared single-fault control expected PASS\n' >&2
  exit 1
}
bash "$helper" --ledger "$fixture_root/legacy-andon-shape/ledger.md" >/dev/null || {
  printf 'run-root-validation.test: legacy Andon ledger expected PASS\n' >&2
  exit 1
}
bash "$helper" --ledger "$fixture_root/direct-ledger-substrate/below-threshold.md" >/dev/null || {
  printf 'run-root-validation.test: direct ledger below threshold expected PASS\n' >&2
  exit 1
}
bash "$helper" --ledger "$fixture_root/direct-ledger-substrate/duplicate-occ-below-threshold.md" >/dev/null || {
  printf 'run-root-validation.test: duplicate Occ rows must count once\n' >&2
  exit 1
}
if bash "$helper" --ledger "$fixture_root/direct-ledger-substrate/trigger-no-decision.md" >/dev/null 2>&1; then
  printf 'run-root-validation.test: direct ledger trigger without decision must fail\n' >&2
  exit 1
fi
if bash "$helper" --ledger "$fixture_root/direct-ledger-substrate/invalid-empty-continue.md" >/dev/null 2>&1; then
  printf 'run-root-validation.test: continue without justification must fail\n' >&2
  exit 1
fi
if bash "$helper" --ledger "$fixture_root/direct-ledger-substrate/decision-after-audit-complete.md" >/dev/null 2>&1; then
  printf 'run-root-validation.test: decision after AUDIT_COMPLETE must fail\n' >&2
  exit 1
fi

# 9. Background-supervision contract (#81). New declarations are enforced;
# roots with old launch-intent records remain valid with a warning.
bg_case() {  # name, intent, status, process-json, expectation(pass|fail)
  local name="$1" intent="$2" chain_status="$3" process_json="$4" expect="$5"
  mkdir -p "$tmp/$name/background/chain-a"
  cp -r "$tmp/good/." "$tmp/$name/"
  printf '%s\n' "$intent" > "$tmp/$name/background/chain-a/launch-intent.md"
  printf '%s\n' "$chain_status" > "$tmp/$name/background/chain-a/chain-status.txt"
  if [ -n "$process_json" ]; then
    printf '%s\n' "$process_json" > "$tmp/$name/background/chain-a/process-started.json"
  fi
  if [ "$expect" = pass ]; then
    bash "$helper" "$tmp/$name" >/dev/null || {
      printf 'run-root-validation.test: %s expected PASS\n' "$name" >&2
      exit 1
    }
  else
    if bash "$helper" "$tmp/$name" >/dev/null 2>&1; then
      printf 'run-root-validation.test: %s expected FAIL\n' "$name" >&2
      exit 1
    fi
  fi
}

new_intent='command: run-long-job
owner/source: tests/background-chain-contract.test.sh
expected_completion_marker: chain.done
abort_containment_plan: process-started.json identity ledger
poll_budget: 3
terminal_signal: chain.done
expected_duration: 90m
transport_timeout: 10m
launch_mode: detached'

bg_case poll-budget-red "$new_intent" 'probe: 1 | command: check-chain | result: running
probe: 2 | command: check-chain | result: running
probe: 3 | command: check-chain | result: running
probe: 4 | command: check-chain | result: running
probe: 5 | command: check-chain | result: running
probe: 6 | command: check-chain | result: running
probe: 7 | command: check-chain | result: running
probe: 8 | command: check-chain | result: running
probe: 9 | command: check-chain | result: running
probe: 10 | command: check-chain | result: running' '' fail

bg_case poll-budget-green "$new_intent" 'probe: 1 | command: check-chain | result: running
probe: 2 | command: check-chain | result: running
probe: 3 | command: check-chain | result: running
report: terminal | outcome=succeeded' '' pass

inline_intent="$(printf '%s\n' "$new_intent" | sed 's/launch_mode: detached/launch_mode: inline/')"
bg_case transport-ceiling-inline "$inline_intent" 'running' '' fail
bg_case transport-ceiling-detached "$new_intent" 'running' '' pass

bg_case kill-authority-image-name "$new_intent" \
  "kill-command: Get-CimInstance Win32_Process -Filter \"Name='claude.exe'\" | Stop-Process" '' fail

owned_process='{"lane_id":"chain-a","host_os":"windows","host_boot_id":"boot-1","pid":123,"process_creation_time":"2026-08-06T01:02:03Z"}'
bg_case kill-authority-owned "$new_intent" \
  'kill: pid=123 | host_boot_id=boot-1 | process_creation_time=2026-08-06T01:02:03Z' \
  "$owned_process" pass

bg_case cadence-default-red "$new_intent" 'report: item=item-1 | outcome=success
report: item=item-2 | outcome=success
report: item=item-3 | outcome=success
report: item=item-4 | outcome=success
report: item=item-5 | outcome=success
report: item=item-6 | outcome=success
report: item=item-7 | outcome=success
report: item=item-8 | outcome=success
report: item=item-9 | outcome=success
report: item=item-10 | outcome=success
report: item=item-11 | outcome=success
report: item=item-12 | outcome=success
report: item=item-13 | outcome=success
report: item=item-14 | outcome=success
report: terminal | outcome=succeeded' '' fail

per_item_intent="$new_intent
report_cadence: per-item
report_cadence_justification: each item changes the next dispatch decision"
bg_case cadence-justified "$per_item_intent" 'report: item=item-1 | outcome=success
report: item=item-2 | outcome=success
report: terminal | outcome=succeeded' '' pass

bg_case checkpoint-before-block-red "$new_intent" 'wait: blocking | signal=chain.done' '' fail
bg_case checkpoint-before-block-green "$new_intent" 'checkpoint: STATE.md
wait: blocking | signal=chain.done' '' pass

mkdir -p "$tmp/background-legacy/background/chain-a"
cp -r "$tmp/good/." "$tmp/background-legacy/"
printf 'command: old-run\n' > "$tmp/background-legacy/background/chain-a/launch-intent.md"
printf 'running\n' > "$tmp/background-legacy/background/chain-a/chain-status.txt"
legacy_output="$(bash "$helper" "$tmp/background-legacy" 2>&1)" || {
  printf 'run-root-validation.test: legacy background root must stay valid\n' >&2
  exit 1
}
printf '%s\n' "$legacy_output" | grep -qi 'legacy' || {
  printf 'run-root-validation.test: legacy background root must warn\n' >&2
  exit 1
}

# 10. Verification-window closure contract (#75). A terminal run root cannot
# retain an open window; the identical declaration passes once closed.
window_root="$tmp/verification-window-open"
mkdir -p "$window_root/background/chain-a"
cp -r "$tmp/good/." "$window_root/"
"${py_cmd[@]}" - "$window_root/STATE.md" <<'PY'
import sys
from pathlib import Path
p = Path(sys.argv[1])
p.write_text(
    p.read_text(encoding="utf-8").replace("| Status | open |", "| Status | DONE |", 1),
    encoding="utf-8",
)
PY
printf '%s\n' "$new_intent" \
  'verification_window:' \
  '  - surfaces: [curriculum/**]' \
  '    opened_at: 0123456789abcdef0123456789abcdef01234567' \
  '    chain: chain-a' \
  '    state: open' \
  > "$window_root/background/chain-a/launch-intent.md"
printf 'running\n' > "$window_root/background/chain-a/chain-status.txt"
if bash "$helper" "$window_root" >/dev/null 2>&1; then
  printf 'run-root-validation.test: terminal root with open verification window must fail\n' >&2
  exit 1
fi

sed -i 's/state: open/state: closed/' "$window_root/background/chain-a/launch-intent.md"
if bash "$helper" "$window_root" >/dev/null 2>&1; then
  printf 'run-root-validation.test: closed declaration without receipt must fail\n' >&2
  exit 1
fi
sed -i '/state: closed/i\    closed_at: 0123456789abcdef0123456789abcdef01234567' "$window_root/background/chain-a/launch-intent.md"
touch "$window_root/background/chain-a/chain.done"
bash "$helper" "$window_root" >/dev/null || {
  printf 'run-root-validation.test: terminal root with closed verification window must pass\n' >&2
  exit 1
}

# 11. An optional re-spec impact set is routed through the shared validator.
cp -r "$tmp/good/." "$tmp/respec-invalid/"
printf '%s\n' \
  'IMPLEMENTAUDIT_RESPEC_IMPACT_SET' \
  'Change: old -> new' \
  'Declared by: fixture' \
  'Population size: 1' \
  'Enumeration method: literal + stem/dirname' \
  'Literal carriers: file.md' \
  'Literal count: 1' \
  'Stem/dirname additional carriers: none' \
  'Stem/dirname additional count: 0' \
  'Replacement: no' \
  '| # | Carrier | Kind | Status | Evidence |' \
  '|---|---|---|---|---|' \
  '| 1 | file.md | doc |  | diff:x |' \
  > "$tmp/respec-invalid/respec-impact-set.md"
if bash "$helper" "$tmp/respec-invalid" >/dev/null 2>&1; then
  printf 'run-root-validation.test: invalid re-spec impact set must fail\n' >&2
  exit 1
fi

# 12. #86 cold-review attestation is prospective: legacy roots above remain
# valid. A declared disposition binds a contained report's exact terminal
# result and canonical #87 identity fields to two real, ordered Git commits.
review_repo="$tmp/review-repo"
git init -q "$review_repo"
git -C "$review_repo" config user.name implementaudit-test
git -C "$review_repo" config user.email implementaudit-test@example.invalid
printf 'base\n' > "$review_repo/base.txt"
git -C "$review_repo" add base.txt
git -C "$review_repo" commit -q -m base
review_base="$(git -C "$review_repo" rev-parse HEAD)"
printf 'head\n' > "$review_repo/head.txt"
git -C "$review_repo" add head.txt
git -C "$review_repo" commit -q -m head
review_head="$(git -C "$review_repo" rev-parse HEAD)"
review_attested="$review_repo/.IMPLEMENTAUDIT/review-attested"
mkdir -p "$review_attested/reviews"
cp -r "$tmp/good/." "$review_attested/"
cat >> "$review_attested/STATE.md" <<EOF
model-identity: requested_model: GPT-5 | actual_model: GPT-5 | evidence: self-report | claims: bound
cold-review: disposition: PASS | attestation: reviews/cold.md | base_sha: $review_base | head_sha: $review_head
EOF
cat > "$review_attested/reviews/cold.md" <<EOF
Report state: FINAL
Verdict: PASS
Reviewer attestation:
- reviewer_identity: task-cold-1
- requested_model: GPT-5
- actual_model: GPT-5
- authoring_context_reuse: no
- other_reviewer_output_seen: no
- base_sha: $review_base
- head_sha: $review_head

PASS
EOF
bash "$helper" "$review_attested" >/dev/null || {
  printf 'run-root-validation.test: valid #86 cold-review attestation rejected\n' >&2
  exit 1
}

expect_cold_review_fail() {
  local root="$1" expected="$2" label="$3" output
  output="$(bash "$helper" "$root" 2>&1)" && {
    printf '%s\n' "$output" >&2
    printf 'run-root-validation.test: %s unexpectedly passed\n' "$label" >&2
    exit 1
  }
  grep -Fq "$expected" <<<"$output" || {
    printf '%s\n' "$output" >&2
    printf 'run-root-validation.test: %s failed for the wrong reason\n' "$label" >&2
    exit 1
  }
}

review_case() {
  local name="$1" destination
  destination="$review_repo/.IMPLEMENTAUDIT/$name"
  mkdir -p "$destination"
  cp -r "$review_attested/." "$destination/"
  printf '%s\n' "$destination"
}

review_self="$(review_case review-self)"
sed -i 's/authoring_context_reuse: no/authoring_context_reuse: yes/' \
  "$review_self/reviews/cold.md"
expect_cold_review_fail "$review_self" \
  "authoring-context reuse labels self-critique" \
  "authoring-context self-review"

review_dangling="$(review_case review-dangling)"
sed -i 's#reviews/cold.md#reviews/missing.md#' "$review_dangling/STATE.md"
expect_cold_review_fail "$review_dangling" \
  "cold-review attestation must resolve to a regular non-symlink file" \
  "dangling cold-review attestation"

# Reviewer finding F1: STATE and report must agree on one exact final token.
review_contradictory="$(review_case review-contradictory)"
sed -i 's/Verdict: PASS/Verdict: BLOCKED/' "$review_contradictory/reviews/cold.md"
expect_cold_review_fail "$review_contradictory" \
  "cold-review artifact contains a contradictory disposition" \
  "contradictory report verdict"

review_final_alias="$(review_case review-final-alias)"
sed -i 's/Verdict: PASS/Disposition: FINAL/' "$review_final_alias/reviews/cold.md"
expect_cold_review_fail "$review_final_alias" \
  "cold-review artifact contains a contradictory disposition" \
  "non-gate FINAL disposition"

review_state_partial="$(review_case review-state-partial)"
sed -i 's/Report state: FINAL/Report state: PARTIAL/' \
  "$review_state_partial/reviews/cold.md"
expect_cold_review_fail "$review_state_partial" \
  "cold-review artifact requires exactly one Report state: FINAL" \
  "explicit PARTIAL report state"

review_state_interrupted="$(review_case review-state-interrupted)"
sed -i 's/Report state: FINAL/Report state: interrupted-partial/' \
  "$review_state_interrupted/reviews/cold.md"
expect_cold_review_fail "$review_state_interrupted" \
  "cold-review artifact requires exactly one Report state: FINAL" \
  "explicit interrupted report state"

review_state_missing="$(review_case review-state-missing)"
sed -i '/Report state: FINAL/d' "$review_state_missing/reviews/cold.md"
expect_cold_review_fail "$review_state_missing" \
  "cold-review artifact requires exactly one Report state: FINAL" \
  "missing report state"

review_partial="$(review_case review-partial)"
sed -i '$s/PASS/PARTIAL/' "$review_partial/reviews/cold.md"
expect_cold_review_fail "$review_partial" \
  "cold-review artifact requires one exact final disposition matching STATE" \
  "partial report disposition"

review_interrupted="$(review_case review-interrupted)"
sed -i '$s/PASS/interrupted-partial/' "$review_interrupted/reviews/cold.md"
expect_cold_review_fail "$review_interrupted" \
  "cold-review artifact requires one exact final disposition matching STATE" \
  "interrupted-partial report disposition"

review_missing_result="$(review_case review-missing-result)"
sed -i '$d' "$review_missing_result/reviews/cold.md"
expect_cold_review_fail "$review_missing_result" \
  "cold-review artifact requires one exact final disposition matching STATE" \
  "missing terminal report disposition"

# Reviewer finding F2: lexical 40-hex is insufficient. The STATE declaration,
# report attestation, Git object type, and base-before-head ancestry all bind.
review_bogus="$(review_case review-bogus)"
bogus_base=ffffffffffffffffffffffffffffffffffffffff
sed -i "s/$review_base/$bogus_base/g" "$review_bogus/STATE.md" "$review_bogus/reviews/cold.md"
expect_cold_review_fail "$review_bogus" \
  "cold-review base_sha does not resolve to a commit" \
  "nonexistent review base"

review_wrong_base="$(review_case review-wrong-base)"
sed -i "s/- base_sha: $review_base/- base_sha: $review_head/" \
  "$review_wrong_base/reviews/cold.md"
expect_cold_review_fail "$review_wrong_base" \
  "cold-review attestation base/head must match the STATE review identity" \
  "wrong attested base"

review_wrong_head="$(review_case review-wrong-head)"
sed -i "s/- head_sha: $review_head/- head_sha: $review_base/" \
  "$review_wrong_head/reviews/cold.md"
expect_cold_review_fail "$review_wrong_head" \
  "cold-review attestation base/head must match the STATE review identity" \
  "wrong attested head"

review_model_substitution="$(review_case review-model-substitution)"
sed -i 's/model-identity: requested_model: GPT-5 | actual_model: GPT-5 | evidence: self-report | claims: bound/model-identity: requested_model: GPT-5 | actual_model: other-model | evidence: host-event:G0001 | claims: IDENTITY_UNBOUND/' \
  "$review_model_substitution/STATE.md"
"${py_cmd[@]}" - "$review_model_substitution/STATE.md" <<'PY'
import sys
from pathlib import Path
path = Path(sys.argv[1])
text = path.read_text(encoding="utf-8")
marker = "|---|---|---|---|---|---|---|---|"
row = "| 1 | o1 | 6 | transport-infrastructure | model substitution | preserve unbound claims | host-event:G0001 | resolved |"
path.write_text(text.replace(marker, marker + "\n" + row, 1), encoding="utf-8")
PY
sed -i 's/- actual_model: GPT-5/- actual_model: other-model/' \
  "$review_model_substitution/reviews/cold.md"
expect_cold_review_fail "$review_model_substitution" \
  "cold-review PASS requires bound requested_model and actual_model identity" \
  "unbound substituted-model PASS"

review_reversed="$(review_case review-reversed)"
"${py_cmd[@]}" - "$review_reversed/STATE.md" "$review_reversed/reviews/cold.md" "$review_base" "$review_head" <<'PY'
import sys
from pathlib import Path
for name in sys.argv[1:3]:
    path = Path(name)
    text = path.read_text(encoding="utf-8")
    text = text.replace(sys.argv[3], "REVIEW_BASE_PLACEHOLDER")
    text = text.replace(sys.argv[4], sys.argv[3])
    text = text.replace("REVIEW_BASE_PLACEHOLDER", sys.argv[4])
    path.write_text(text, encoding="utf-8")
PY
expect_cold_review_fail "$review_reversed" \
  "cold-review base_sha must be an ancestor of head_sha" \
  "reversed review ancestry"

review_equal="$(review_case review-equal)"
sed -i "s/$review_head/$review_base/g" \
  "$review_equal/STATE.md" "$review_equal/reviews/cold.md"
expect_cold_review_fail "$review_equal" \
  "cold-review base_sha must strictly precede head_sha" \
  "equal review anchors"

empty_tree="$(git -C "$review_repo" mktree </dev/null)"
unrelated_sha="$(printf 'unrelated\n' | git -C "$review_repo" commit-tree "$empty_tree")"
review_unrelated="$(review_case review-unrelated)"
sed -i "s/$review_base/$unrelated_sha/g" \
  "$review_unrelated/STATE.md" "$review_unrelated/reviews/cold.md"
expect_cold_review_fail "$review_unrelated" \
  "cold-review base_sha must be an ancestor of head_sha" \
  "unrelated review anchors"

# The shipped run-root validator must invoke the repo-side live parser from its
# own source tree when successor/non-verdict rows exist; a callable test-only
# mode or a same-named script in the run-root checkout is insufficient.

live_deterministic="$(review_case live-deterministic)"
"${py_cmd[@]}" - "$live_deterministic/STATE.md" <<'PY'
import sys
from pathlib import Path
path = Path(sys.argv[1])
text = path.read_text(encoding="utf-8")
marker = "|---|---|---|---|---|---|---|---|"
row = "| 1 | o1 | 6 | transport-infrastructure | deterministic refusal | alter packet | evidence/failure.md | open |"
path.write_text(text.replace(marker, marker + "\n" + row, 1), encoding="utf-8")
PY
cat > "$live_deterministic/packet.md" <<'EOF'
review-packet-scope: scope: phase-spec | technique: cold-read | evidence_mode: inline
EOF
live_packet_hash="$(sha256sum "$live_deterministic/packet.md" | awk '{print $1}')"
cat >> "$live_deterministic/STATE.md" <<EOF
successor-review: attempt: 1 | predecessor_failure_origin: transport-infrastructure | failure_determinism: content-deterministic | origin_detail: provider-policy | predecessor_occurrence: o1 | predecessor_packet_scope_file: packet.md | predecessor_packet_scope_sha256: $live_packet_hash | packet_scope_file: packet.md | packet_scope_sha256: $live_packet_hash | packet_alteration: none | andon_class: transport-infrastructure | provisional_findings_carried: none
EOF
expect_cold_review_fail "$live_deterministic" \
  "live successor/non-verdict contract failed" \
  "live unaltered deterministic successor"

live_dropped_findings="$(review_case live-dropped-findings)"
"${py_cmd[@]}" - "$live_dropped_findings/STATE.md" <<'PY'
import sys
from pathlib import Path
path = Path(sys.argv[1])
text = path.read_text(encoding="utf-8")
marker = "|---|---|---|---|---|---|---|---|"
row = "| 1 | o1 | 6 | transport-infrastructure | reviewer interruption | replace reviewer | evidence/failure.md | open |"
path.write_text(text.replace(marker, marker + "\n" + row, 1), encoding="utf-8")
PY
cp fixtures/cold-review/independent-review-confirms-handoff.md \
  "$live_dropped_findings/"
cp fixtures/cold-review/issue-86-runtime-non-verdict-replacement.md \
  "$live_dropped_findings/"
sed -i 's|provisional_findings_carried: issue-86-runtime-non-verdict-replacement.md#finding-a|provisional_findings_carried: none|' \
  "$live_dropped_findings/issue-86-runtime-non-verdict-replacement.md"
expect_cold_review_fail "$live_dropped_findings" \
  "live successor/non-verdict contract failed" \
  "live dropped provisional findings"

# Retained installed payloads and frozen repository fixtures are independent
# custody planes, not additional live rows in the current record root. A
# recursive scan would merge their intentionally positive and negative review
# fixtures into one synthetic record and false-red an otherwise valid root.
retained_review_fixtures="$(review_case retained-review-fixtures)"
mkdir -p "$retained_review_fixtures/archive/banquet/repository/fixtures/cold-review"
cp fixtures/cold-review/*.md \
  "$retained_review_fixtures/archive/banquet/repository/fixtures/cold-review/"
bash "$helper" "$retained_review_fixtures" >/dev/null || {
  printf 'run-root-validation.test: retained nested review fixtures must not be merged into the live record root\n' >&2
  exit 1
}
installed_validator_dir="$tmp/installed-validator/skills/implementaudit/scripts"
installed_template_dir="$tmp/installed-validator/skills/implementaudit/templates"
mkdir -p "$installed_validator_dir" "$installed_template_dir"
cp "$helper" "$installed_validator_dir/validate-run-root.sh"
cp skills/implementaudit/templates/* "$installed_template_dir/"
bash "$installed_validator_dir/validate-run-root.sh" \
  "$retained_review_fixtures" >/dev/null || {
  printf 'run-root-validation.test: installed validator must not require the source checker for retained nested review fixtures\n' >&2
  exit 1
}

# R0024 strict claim-only custody: ordinary legacy run-root validation remains
# compatible, while destructive callers require an exact v2 Git-bound claim.
claim_repo="$tmp/claim-only-repo"
mkdir -p "$claim_repo"
git -C "$claim_repo" init -q
git -C "$claim_repo" config user.email claim@example.invalid
git -C "$claim_repo" config user.name claim-only-test
claim_rel="$(cd "$claim_repo" && IMPLEMENTAUDIT_BASE=.IMPLEMENTAUDIT/runs bash "$repo_root/skills/implementaudit/scripts/claim-run.sh" 'strict custody' 2>/dev/null)"
claim_root="$claim_repo/$claim_rel"
for promised in STATE.md PROTOCOL.md ROADMAP.md THINKING.md sidecars.md tools.md context.md; do printf 'fixture\n' > "$claim_root/$promised"; done
bash "$helper" --claim-only "$claim_root" --repo-root "$claim_repo" >/dev/null || {
  printf 'run-root-validation.test: valid v2 Git claim must pass strict claim-only\n' >&2; exit 1;
}
claim_saved="$tmp/claim-only.saved"
cp "$claim_root/.claimed" "$claim_saved"
sed -i 's/^claimed_at_utc=.*/claimed_at_utc=2026-99-99T99:99:99Z/' "$claim_root/.claimed"
if bash "$helper" --claim-only "$claim_root" --repo-root "$claim_repo" >/dev/null 2>&1; then
  printf 'run-root-validation.test: impossible RFC3339 claim timestamp must fail\n' >&2; exit 1
fi
cp "$claim_saved" "$claim_root/.claimed"
alias_claim_root="$claim_root/."
alias_claim_repo="$claim_repo/."
case "$(uname -s 2>/dev/null || true)" in
  MINGW*|MSYS*|CYGWIN*)
    alias_claim_root="$(cygpath -w "$claim_root")\\."
    alias_claim_repo="$(cygpath -w "$claim_repo")\\."
    ;;
esac
if bash "$helper" --claim-only "$alias_claim_root" --repo-root "$claim_repo" >/dev/null 2>&1; then
  printf 'run-root-validation.test: lexical dot run-root alias must fail\n' >&2; exit 1
fi
if bash "$helper" --claim-only "$claim_root" --repo-root "$alias_claim_repo" >/dev/null 2>&1; then
  printf 'run-root-validation.test: lexical dot repo-root alias must fail\n' >&2; exit 1
fi
mkdir -p "$tmp/claim-alias-target"
if ln -s "$tmp/claim-alias-target" "$tmp/claim-alias-component" 2>/dev/null; then
  if bash "$helper" --claim-only "$tmp/claim-alias-component/../claim-only-repo/$claim_rel" --repo-root "$claim_repo" >/dev/null 2>&1; then
    printf 'run-root-validation.test: symlink-component dotdot alias must fail before normalisation\n' >&2; exit 1
  fi
fi
copied_repo="$tmp/claim-only-copied"
mkdir -p "$copied_repo"
git -C "$copied_repo" init -q
cp -a "$claim_root" "$copied_repo/copied-root"
if bash "$helper" --claim-only "$copied_repo/copied-root" --repo-root "$copied_repo" >/dev/null 2>&1; then
  printf 'run-root-validation.test: copied claim must fail strict custody\n' >&2; exit 1
fi
if ln -s "$claim_root" "$tmp/claim-only-link" 2>/dev/null; then
  if bash "$helper" --claim-only "$tmp/claim-only-link" --repo-root "$claim_repo" >/dev/null 2>&1; then
    printf 'run-root-validation.test: symlinked claim root must fail strict custody\n' >&2; exit 1
  fi
fi

printf 'run-root-validation.test: ok\n'
