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
contains_normalized() {
  tr '\n' ' ' < "$1" | tr -s '[:space:]' ' ' | grep -Fqi "$2"
}

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
contains_normalized "$ref" "run-authored steer and advisory outputs" ||
  fail "reference missing run-authored steer/advisory lifecycle"
contains_normalized "$ref" "precision-critical owner vocabulary" ||
  fail "reference missing immediate vocabulary preservation rule"
grep -Fqi 'supersedes:' "$ref" || fail "reference missing steer precedence header"
for surface in "$ref" "$proto" "$state_t"; do
  grep -q 'requested_model' "$surface" || fail "$surface missing canonical requested_model field"
  grep -q 'actual_model' "$surface" || fail "$surface missing canonical actual_model field"
  grep -q 'IDENTITY_UNBOUND' "$surface" || fail "$surface missing identity-unbound consequence"
done
grep -q "references/continuity.md" skills/implementaudit/SKILL.md || fail "SKILL.md load map missing continuity reference"
# The bootloader itself must carry the load-bearing runtime instruction —
# the B3 post-change r1 wave proved reference-only placement does not
# reach a resuming executor (all four candidate missions failed).
skill="skills/implementaudit/SKILL.md"
for tok in host-reported-compaction new-session handoff-resume \
           manual-resume inferred-context-gap; do
  grep -q "$tok" "$skill" || fail "SKILL.md runtime loop missing provenance token: $tok"
done
grep -qi "live state wins" "$skill" || fail "SKILL.md runtime loop missing live-state-wins rule"
grep -qi "Target already satisfied at" "$skill" || fail "SKILL.md runtime loop missing refusal sentence"
grep -qi "epoch row" "$skill" || fail "SKILL.md runtime loop missing epoch-row recording"
route_ok() {
  grep -q -- '--current-controller' "$1" && grep -q -- '--resume-controller' "$1" &&
    grep -q -- '--current-controller' "$2" && grep -q -- '--resume-controller' "$2" &&
    grep -q -- '--supersede-claim' "$2" && grep -q -- '--verify-resume-receipt' "$2"
}
route_ok "$skill" "$ref" || fail "runtime route omits controller discovery, transfer, or receipt verification"

# e61 ecological RED: after an automatic compaction the model retained a true
# standing README constraint but promoted it into the active work cell, then
# launched checks and committed before a fresh host-compaction invalidation and
# receipt. The bootloader must carry the complete ordered entry fence; a deep
# reference or cooperating mutation helper is not enough for first-turn routing.
"${py_cmd[@]}" - "$skill" <<'PY' || fail "SKILL.md discovery description missing pre-load continuity fence"
import sys
from pathlib import Path

text = Path(sys.argv[1]).read_text(encoding="utf-8")
frontmatter = text.split("---", 2)[1]
description_lines = [
    line for line in frontmatter.splitlines() if line.startswith("description:")
]
if len(description_lines) != 1:
    raise SystemExit(1)
description_value = description_lines[0].split(":", 1)[1].strip()
if not (description_value.startswith('"') and description_value.endswith('"')):
    raise SystemExit(1)
required = (
    "host-reported compaction",
    "before any response or repo inspection",
    "through bash",
    "--current-controller",
    "separate command",
    "--invalidate-continuity <controller>",
    "--boundary host-reported-compaction",
    "--event <opaque-event>",
    "state.md then roadmap.md",
    "--resume-controller <controller> --boundary host-reported-compaction --epoch <next-epoch>",
    "--verify-resume-receipt <receipt>",
    "--require-current-continuity <controller>",
    "no response until the verified receipt",
    "only then emit the first message",
    "verified receipt",
)
if any(item.lower() not in frontmatter.lower() for item in required):
    raise SystemExit(1)
PY
for surface in "$skill" "$ref" "$proto"; do
  for literal in \
    'POST_BOUNDARY_FIRST_SUBSTANTIVE_MESSAGE=VERIFIED_CONTINUITY_RECEIPT' \
    'POST_BOUNDARY_NEW_EXECUTION=REFUSE_UNTIL_CURRENT' \
    'PREBOUNDARY_PROCESS=WAIT_OR_TERMINATE_ONLY' \
    'STANDING_CONSTRAINT_ROLE=DO_NOT_PROMOTE_WITHOUT_LIVE_STATE'; do
    grep -Fq "$literal" "$surface" ||
      fail "$surface missing post-compaction frontier fence: $literal"
  done
done
for tok in --invalidate-continuity --verify-resume-receipt --require-current-continuity; do
  grep -q -- "$tok" "$skill" || fail "SKILL.md bootloader missing ordered continuity command: $tok"
done
"${py_cmd[@]}" - "$skill" <<'PY' || fail "SKILL.md post-boundary command order is not reconstructible"
import sys
from pathlib import Path

text = Path(sys.argv[1]).read_text(encoding="utf-8")
start = text.index("0. Continuity boundary (when resuming):")
end = text.index("\n1. Safety read:", start)
section = text[start:end]
ordered = (
    "--current-controller",
    "--invalidate-continuity",
    "STATE.md",
    "ROADMAP.md",
    "--resume-controller",
    "--verify-resume-receipt",
    "--require-current-continuity",
    "POST_BOUNDARY_FIRST_SUBSTANTIVE_MESSAGE=VERIFIED_CONTINUITY_RECEIPT",
)
positions = [section.index(item) for item in ordered]
if positions != sorted(positions) or len(set(positions)) != len(positions):
    raise SystemExit(1)
PY
for tok in --invalidate-continuity --require-current-continuity; do
  grep -q -- "$tok" "$ref" || fail "reference missing host-neutral currentness route: $tok"
  grep -q -- "$tok" skills/implementaudit/scripts/claim-run.sh || fail "claim helper missing host-neutral currentness route: $tok"
done
contains_normalized "$ref" "generic no-native-hook fallback" ||
  fail "reference missing generic no-native-hook fallback"
contains_normalized "$ref" "native host signal is a trigger, never continuity authority" ||
  fail "reference promotes or omits the optional host-signal boundary"
cp "$skill" "$tmp/mutant-skill.md"; cp "$ref" "$tmp/mutant-continuity.md"
sed -i 's/--current-controller/--lost-controller/' "$tmp/mutant-skill.md"
route_ok "$tmp/mutant-skill.md" "$tmp/mutant-continuity.md" && fail "source-removal mutant retained a green continuity route"
cp "$skill" "$tmp/mutant-skill.md"; sed -i 's/--supersede-claim/--lost-predecessor/' "$tmp/mutant-continuity.md"
route_ok "$tmp/mutant-skill.md" "$tmp/mutant-continuity.md" && fail "transfer-removal mutant retained a green continuity route"
for surface in "$skill" "$ref" "$proto"; do
  contains_normalized "$surface" "own completed host action" ||
    fail "$surface missing separately attributable durable-state read rule"
  contains_normalized "$surface" "must not use ';', '&&', pipelines, multi-stage shell composition, or batching" ||
    fail "$surface missing no-composition evidence rule"
done

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

# 7. Long evolving-run continuity is keyed to a stable controller, not the
# last plausible worktree-local root.  The active controller migrates by an
# atomic expected-claim transition.  After compaction, a stale summary/root
# must resolve to the successor and cannot emit the successor's receipt.
claim_helper="${IMPLEMENTAUDIT_CLAIM_HELPER:-$repo_root/skills/implementaudit/scripts/claim-run.sh}"
resume_repo="$tmp/resume-repo"; successor_repo="$tmp/resume-successor"
mkdir -p "$resume_repo"
git -C "$resume_repo" init -q
git -C "$resume_repo" config user.name 'continuity fixture'
git -C "$resume_repo" config user.email 'continuity@example.invalid'
printf 'pre-merge\n' > "$resume_repo/product.txt"
git -C "$resume_repo" add product.txt
git -C "$resume_repo" commit -qm 'pre-merge state'
git -C "$resume_repo" worktree add -q -b successor "$successor_repo"

initial_rel="$(cd "$resume_repo" && IMPLEMENTAUDIT_BASE=.IMPLEMENTAUDIT/runs \
  bash "$claim_helper" --controller release-v0333 'long evolving run' 2>/dev/null)" \
  || fail "initial controller claim failed"
initial_root="$resume_repo/$initial_rel"
initial_claim="$(sed -n 's/^claim_id=//p' "$initial_root/.claimed")"
[ "$(cat "$initial_root/.controller" 2>/dev/null)" = 'controller_id=release-v0333' ] || fail 'S3E-W02 RED: controller root lacks value-bearing custody record'

printf 'post-merge\n' >> "$successor_repo/product.txt"
git -C "$successor_repo" add product.txt
git -C "$successor_repo" commit -qm 'authoritative successor state'
successor_head="$(git -C "$successor_repo" rev-parse HEAD)"
successor_tree="$(git -C "$successor_repo" rev-parse 'HEAD^{tree}')"
successor_rel="$(cd "$successor_repo" && IMPLEMENTAUDIT_BASE=.IMPLEMENTAUDIT/runs \
  bash "$claim_helper" --controller release-v0333 --supersede-claim "$initial_claim" \
  'continued controller' 2>/dev/null)" || fail "controller migration failed"
successor_root="$successor_repo/$successor_rel"
successor_claim="$(sed -n 's/^claim_id=//p' "$successor_root/.claimed")"
[ "$(cat "$successor_root/.controller" 2>/dev/null)" = 'controller_id=release-v0333' ] || fail 'successor controller custody record is missing or malformed'

for root in "$initial_root" "$successor_root"; do
  for f in STATE.md PROTOCOL.md ROADMAP.md THINKING.md sidecars.md tools.md context.md; do
    cp "$repo_root/skills/implementaudit/templates/$f" "$root/$f"
  done
done

"${py_cmd[@]}" - "$initial_root/STATE.md" "$initial_rel" \
  "$(git -C "$resume_repo" rev-parse HEAD)" "$(git -C "$resume_repo" rev-parse 'HEAD^{tree}')" \
  "$successor_root/STATE.md" "$successor_rel" "$successor_head" "$successor_tree" <<'PY'
import sys
from pathlib import Path
for state, run, head, tree, epoch, boundary, action in (
    (*sys.argv[1:5], "e1", "new-session", "continue implementation in the controller worktree"),
    (*sys.argv[5:9], "e2", "host-reported-compaction", "qualify the authoritative successor before release"),
):
    p=Path(state); s=p.read_text(encoding="utf-8")
    s=s.replace("| Run root |  |", f"| Run root | `{run}` |")
    s=s.replace("| Next action |  |", f"| Next action | {action} |")
    s=s.replace("Current epoch: e1", f"Current epoch: {epoch}")
    anchor="| Epoch | Boundary provenance | Established at | Repo identity | Reconciled | Notes |\n|---|---|---|---|---|---|"
    row=f"| {epoch} | {boundary} | 2026-08-12T13:00:00Z | repo at `{head}` / `{tree}` | yes | live readback complete |"
    p.write_text(s.replace(anchor, anchor+"\n"+row), encoding="utf-8")
PY

current="$(cd "$resume_repo" && bash "$claim_helper" --current-controller)" \
  || fail "current controller discovery failed"
"${py_cmd[@]}" - "$current" "$successor_repo" "$successor_root" "$successor_claim" <<'PY' \
  || fail "stale worktree did not discover the exact successor controller: $current"
import os,sys
from pathlib import Path
controller,repo,root,claim=sys.argv[1].split("\t")
expected_repo,expected_root,expected_claim=sys.argv[2:]
same=lambda a,b: os.path.normcase(str(Path(a).resolve()))==os.path.normcase(str(Path(b).resolve()))
assert controller=="release-v0333" and same(repo,expected_repo) and same(root,expected_root) and claim==expected_claim
PY

if (cd "$resume_repo" && bash "$claim_helper" --resume-controller release-v0333 \
    --boundary host-reported-compaction --epoch e2) >/dev/null 2>&1; then
  fail "stale controller worktree emitted a successor continuity receipt"
fi

receipt="$(cd "$successor_repo" && bash "$claim_helper" --resume-controller release-v0333 \
  --boundary host-reported-compaction --epoch e2)" \
  || fail "current successor controller did not produce a continuity receipt"
case "$receipt" in refs/implementaudit/continuity-receipts/release-v0333/e2@[0-9a-f][0-9a-f]*) :;; *) fail "continuity receipt is not a ref-bound token";; esac
receipt_oid="${receipt##*@}"
receipt_record="$(git -C "$successor_repo" cat-file blob "$receipt_oid")"
"${py_cmd[@]}" - "$receipt_record" "$successor_claim" "$successor_head" "$successor_tree" <<'PY' \
  || fail "continuity receipt omitted receiver-required currentness state"
import sys
schema,controller,owner_oid,claim,head,tree,state,roadmap,invalidation,boundary,epoch,next_action=sys.argv[1].split("\t")
assert schema=="implementaudit.continuity-receipt.v2" and controller=="release-v0333"
assert claim==sys.argv[2] and head==sys.argv[3] and tree==sys.argv[4]
assert boundary=="host-reported-compaction" and epoch=="e2"
assert next_action=="qualify the authoritative successor before release"
assert invalidation=="none"
assert len(owner_oid)==40 and len(state)==64 and len(roadmap)==64
PY
(cd "$successor_repo" && bash "$claim_helper" --verify-resume-receipt "$receipt") >/dev/null \
  || fail "fresh successor continuity receipt did not verify"

current_receipt="$(cd "$successor_repo" && bash "$claim_helper" \
  --require-current-continuity release-v0333 2>/dev/null)" \
  || fail "current continuity gate rejected the fresh baseline receipt"
[ "$current_receipt" = "$receipt" ] \
  || fail "current continuity gate did not return the active receipt"

invalidation="$(cd "$successor_repo" && bash "$claim_helper" \
  --invalidate-continuity release-v0333 --boundary inferred-context-gap \
  --event generic-no-native-hook-e3 2>/dev/null)" \
  || fail "host-neutral continuity invalidation command is absent"
case "$invalidation" in
  refs/implementaudit/continuity-invalidations/release-v0333@[0-9a-f][0-9a-f]*) :;;
  *) fail "continuity invalidation is not a ref-bound token: $invalidation";;
esac
same_invalidation="$(cd "$successor_repo" && bash "$claim_helper" \
  --invalidate-continuity release-v0333 --boundary inferred-context-gap \
  --event generic-no-native-hook-e3 2>/dev/null)" \
  || fail "idempotent continuity invalidation failed"
[ "$same_invalidation" = "$invalidation" ] \
  || fail "same continuity event minted a second invalidation"
if (cd "$successor_repo" && bash "$claim_helper" \
    --require-current-continuity release-v0333) >/dev/null 2>&1; then
  fail "POST_COMPACTION_WITHOUT_FRESH_CONTINUITY remained current"
fi

"${py_cmd[@]}" - "$successor_root/STATE.md" "$successor_rel" \
  "$successor_head" "$successor_tree" <<'PY'
import sys
from pathlib import Path
p=Path(sys.argv[1]); run,head,tree=sys.argv[2:]
s=p.read_text(encoding="utf-8")
s=s.replace("Current epoch: e2", "Current epoch: e3")
s=s.replace("| Next action | qualify the authoritative successor before release |",
            "| Next action | continue only after generic continuity recovery |")
anchor="| Epoch | Boundary provenance | Established at | Repo identity | Reconciled | Notes |\n|---|---|---|---|---|---|"
row=f"| e3 | inferred-context-gap | 2026-08-12T13:05:00Z | repo at `{head}` / `{tree}` | yes | generic fallback reconciliation complete |"
p.write_text(s.replace(anchor, anchor+"\n"+row), encoding="utf-8")
PY
if (cd "$successor_repo" && bash "$claim_helper" \
    --require-current-continuity release-v0333) >/dev/null 2>&1; then
  fail "partial continuity recovery without separate ROADMAP state became current"
fi
printf '\nGeneric continuity recovery reconciled live state.\n' >> "$successor_root/ROADMAP.md"
receipt_e3="$(cd "$successor_repo" && bash "$claim_helper" --resume-controller release-v0333 \
  --boundary inferred-context-gap --epoch e3)" \
  || fail "generic no-native-hook recovery did not mint a fresh receipt"
(cd "$successor_repo" && bash "$claim_helper" --verify-resume-receipt "$receipt_e3") >/dev/null \
  || fail "generic no-native-hook continuity receipt did not verify"
current_receipt="$(cd "$successor_repo" && bash "$claim_helper" \
  --require-current-continuity release-v0333)" \
  || fail "fresh generic continuity recovery did not reopen governed mutation"
[ "$current_receipt" = "$receipt_e3" ] \
  || fail "generic continuity recovery returned the wrong receipt"
if (cd "$successor_repo" && bash "$claim_helper" --resume-controller release-v0333 \
    --boundary host-reported-compaction --epoch e2) >/dev/null 2>&1; then
  fail "a second writer claimed the same continuity epoch"
fi

# Multiple controller records are an audited ambiguity, never a guessed root.
(cd "$successor_repo" && IMPLEMENTAUDIT_BASE=.IMPLEMENTAUDIT/runs \
  bash "$claim_helper" --controller sibling-controller 'independent sibling' >/dev/null 2>&1) \
  || fail "independent controller claim failed"
if (cd "$successor_repo" && bash "$claim_helper" --current-controller) >/dev/null 2>&1; then
  fail "ambiguous controller discovery guessed one current root"
fi
(cd "$successor_repo" && bash "$claim_helper" --current-controller release-v0333) >/dev/null \
  || fail "explicit controller discovery failed under legitimate parallelism"

# A controller blob copied into an unrelated object store is not current
# authority there, even when its embedded run root and claim are internally
# valid. Discovery must bind the ref store and run custody to one Git common.
foreign_a="$tmp/foreign-a"; foreign_b="$tmp/foreign-b"
for foreign_repo in "$foreign_a" "$foreign_b"; do
  mkdir -p "$foreign_repo"; git -C "$foreign_repo" init -q
  git -C "$foreign_repo" config user.name 'continuity fixture'
  git -C "$foreign_repo" config user.email 'continuity@example.invalid'
  printf 'repo\n' > "$foreign_repo/product.txt"
  git -C "$foreign_repo" add product.txt; git -C "$foreign_repo" commit -qm initial
done
(cd "$foreign_b" && IMPLEMENTAUDIT_BASE=.IMPLEMENTAUDIT/runs \
  bash "$claim_helper" --controller foreign-custody 'foreign controller' >"$tmp/foreign-rel" 2>/dev/null) \
  || fail "foreign controller fixture claim failed"
foreign_root="$foreign_b/$(cat "$tmp/foreign-rel")"
for f in STATE.md PROTOCOL.md ROADMAP.md THINKING.md sidecars.md tools.md context.md; do
  cp "$repo_root/skills/implementaudit/templates/$f" "$foreign_root/$f"
done
foreign_ref='refs/implementaudit/controllers/foreign-custody'
foreign_oid="$(git -C "$foreign_b" rev-parse "$foreign_ref")"
copied_oid="$(git -C "$foreign_b" cat-file blob "$foreign_oid" | git -C "$foreign_a" hash-object -w --stdin)"
[ "$copied_oid" = "$foreign_oid" ] || fail "foreign controller blob copy changed identity"
foreign_source=''; foreign_source_rc=0
foreign_source="$(cd "$foreign_b" && bash "$claim_helper" --current-controller foreign-custody 2>"$tmp/foreign-source.err")" || foreign_source_rc=$?
[ "$foreign_source_rc" -eq 0 ] || fail "source-store foreign controller was not independently valid: $(cat "$tmp/foreign-source.err")"
foreign_a_common="$(cd "$(git -C "$foreign_a" rev-parse --path-format=absolute --git-common-dir)" && pwd -P)"
foreign_b_common="$(cd "$(git -C "$foreign_b" rev-parse --path-format=absolute --git-common-dir)" && pwd -P)"
[ "$foreign_a_common" != "$foreign_b_common" ] || fail "foreign custody fixture did not create distinct Git commons"
git -C "$foreign_a" update-ref "$foreign_ref" "$copied_oid"
foreign_current=''; foreign_current_rc=0
foreign_current="$(cd "$foreign_a" && bash "$claim_helper" --current-controller foreign-custody 2>"$tmp/foreign.err")" || foreign_current_rc=$?
if [ "$foreign_current_rc" -eq 0 ]; then
  fail "controller discovery authenticated foreign Git-common custody"
fi

if (cd "$successor_repo" && IMPLEMENTAUDIT_BASE=.IMPLEMENTAUDIT/runs \
    bash "$claim_helper" --controller release-v0333 --supersede-claim "$initial_claim" \
    'stale competing migration') >/dev/null 2>&1; then
  fail "stale expected claim replaced the current controller"
fi

printf 'later drift\n' >> "$successor_repo/product.txt"
git -C "$successor_repo" add product.txt
git -C "$successor_repo" commit -qm 'later drift'
if (cd "$successor_repo" && bash "$claim_helper" --verify-resume-receipt "$receipt") >/dev/null 2>&1; then
  fail "continuity receipt remained valid after repository drift"
fi

# Two successor worktrees racing from one predecessor claim cannot create two
# current controllers.  The Git-common compare-and-swap selects exactly one;
# the loser remains non-authoritative.
race_repo="$tmp/race-repo"; race_a="$tmp/race-a"; race_b="$tmp/race-b"
mkdir -p "$race_repo"; git -C "$race_repo" init -q
git -C "$race_repo" config user.name 'continuity fixture'
git -C "$race_repo" config user.email 'continuity@example.invalid'
printf 'race\n' > "$race_repo/product.txt"; git -C "$race_repo" add product.txt
git -C "$race_repo" commit -qm race
git -C "$race_repo" worktree add -q -b race-a "$race_a"
git -C "$race_repo" worktree add -q -b race-b "$race_b"
race_initial_rel="$(cd "$race_repo" && IMPLEMENTAUDIT_BASE=.IMPLEMENTAUDIT/runs \
  bash "$claim_helper" --controller split-brain 'initial race controller' 2>/dev/null)"
race_claim="$(sed -n 's/^claim_id=//p' "$race_repo/$race_initial_rel/.claimed")"
(
  cd "$race_a" && IMPLEMENTAUDIT_BASE=.IMPLEMENTAUDIT/runs bash "$claim_helper" \
    --controller split-brain --supersede-claim "$race_claim" 'racing successor a' \
    >"$tmp/race-a.out" 2>"$tmp/race-a.err"
) & race_a_pid=$!
(
  cd "$race_b" && IMPLEMENTAUDIT_BASE=.IMPLEMENTAUDIT/runs bash "$claim_helper" \
    --controller split-brain --supersede-claim "$race_claim" 'racing successor b' \
    >"$tmp/race-b.out" 2>"$tmp/race-b.err"
) & race_b_pid=$!
race_a_rc=0; wait "$race_a_pid" || race_a_rc=$?
race_b_rc=0; wait "$race_b_pid" || race_b_rc=$?
[ $(( (race_a_rc == 0) + (race_b_rc == 0) )) -eq 1 ] ||
  fail "controller CAS did not select exactly one racing successor: $race_a_rc/$race_b_rc"
if [ "$race_a_rc" -eq 0 ]; then
  expected_winner="$race_a"; winner_rel="$(cat "$tmp/race-a.out")"; losing_repo="$race_b"
else
  expected_winner="$race_b"; winner_rel="$(cat "$tmp/race-b.out")"; losing_repo="$race_a"
fi
find "$losing_repo/.IMPLEMENTAUDIT/runs" -mindepth 1 -maxdepth 1 -type d -print -quit 2>/dev/null | grep -q . &&
  fail "losing controller CAS retained a plausible stale run root"
for f in STATE.md PROTOCOL.md ROADMAP.md THINKING.md sidecars.md tools.md context.md; do
  cp "$repo_root/skills/implementaudit/templates/$f" "$expected_winner/$winner_rel/$f"
done
race_current="$(cd "$race_repo" && bash "$claim_helper" --current-controller split-brain)" ||
  fail "winning racing controller was not discoverable"
race_winner_repo="$(printf '%s' "$race_current" | cut -f2)"
"${py_cmd[@]}" - "$race_winner_repo" "$expected_winner" <<'PY' || fail "CAS current controller does not name the sole winner"
import os,sys
assert os.path.normcase(os.path.abspath(sys.argv[1]))==os.path.normcase(os.path.abspath(sys.argv[2]))
PY

# Positive N06-style control: one controller, one worktree, current root, live
# epoch and Next action.  It resumes without a migration or extra run.
positive_repo="$tmp/positive-repo"; mkdir -p "$positive_repo"
git -C "$positive_repo" init -q
git -C "$positive_repo" config user.name 'continuity fixture'
git -C "$positive_repo" config user.email 'continuity@example.invalid'
printf 'positive\n' > "$positive_repo/product.txt"
git -C "$positive_repo" add product.txt; git -C "$positive_repo" commit -qm positive
positive_rel="$(cd "$positive_repo" && IMPLEMENTAUDIT_BASE=.IMPLEMENTAUDIT/runs \
  bash "$claim_helper" --controller positive-n06 'positive continuity' 2>/dev/null)"
positive_root="$positive_repo/$positive_rel"
for f in STATE.md PROTOCOL.md ROADMAP.md THINKING.md sidecars.md tools.md context.md; do
  cp "$repo_root/skills/implementaudit/templates/$f" "$positive_root/$f"
done
"${py_cmd[@]}" - "$positive_root/STATE.md" "$positive_rel" \
  "$(git -C "$positive_repo" rev-parse HEAD)" "$(git -C "$positive_repo" rev-parse 'HEAD^{tree}')" <<'PY'
import sys
from pathlib import Path
p=Path(sys.argv[1]); run,head,tree=sys.argv[2:]
s=p.read_text(encoding="utf-8").replace("| Run root |  |",f"| Run root | `{run}` |")
s=s.replace("| Next action |  |","| Next action | resume the exact current checkpoint |")
a="| Epoch | Boundary provenance | Established at | Repo identity | Reconciled | Notes |\n|---|---|---|---|---|---|"
r=f"| e1 | host-reported-compaction | 2026-08-12T12:00:00Z | repo at `{head}` / `{tree}` | yes | separate live reads complete |"
p.write_text(s.replace(a,a+"\n"+r),encoding="utf-8")
PY
(cd "$positive_repo" && bash "$claim_helper" --resume-controller positive-n06 \
  --boundary host-reported-compaction --epoch e1) >/dev/null \
  || fail "positive same-controller continuity case failed"

# Ordinary bounded claims remain the no-registry cheap path.
cheap_rel="$(cd "$positive_repo" && IMPLEMENTAUDIT_BASE=.IMPLEMENTAUDIT/runs \
  bash "$claim_helper" 'small ordinary task' 2>/dev/null)"
[ -f "$positive_repo/$cheap_rel/.claimed" ] || fail "ordinary claim cheap path regressed"
[ ! -e "$positive_repo/$cheap_rel/.controller" ] || fail 'ordinary cheap path acquired controller ceremony'

printf 'continuity-contract.test: ok (surfaces + validator: legacy pass, honest-provenance, kind/status tokens, terminal-status evidence)\n'
