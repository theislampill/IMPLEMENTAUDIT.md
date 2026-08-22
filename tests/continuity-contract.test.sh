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
mutation_helper="skills/implementaudit/scripts/apply-observed-mutation.sh"
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
contains_normalized "$state_t" "Partial or mixed migrated state is STOP" ||
  fail "STATE template missing mixed-generation stop rule"
contains_normalized "$state_t" "Only the current epoch stays hot; prior epochs remain immutable query records" ||
  fail "STATE template missing bounded-history rule"
grep -qi "Context epochs and instruction applicability" "$state_t" || fail "STATE template missing epoch section"
grep -qi "NO new marker" "$tc" || fail "transcript contract missing no-new-marker rule"
contains_normalized "$ref" "run-authored steer and advisory outputs" ||
  fail "reference missing run-authored steer/advisory lifecycle"
contains_normalized "$ref" "precision-critical owner vocabulary" ||
  fail "reference missing immediate vocabulary preservation rule"
grep -Fqi 'supersedes:' "$ref" || fail "reference missing steer precedence header"
for surface in "$ref" "$proto"; do
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
for literal in \
  'pointer -> receipt v3 -> permanent marker' \
  'pointer OID/digest' \
  'WORK_GRAPH path/digest' \
  'generation manifest OID/digest' \
  'cold high-water' \
  'historical event segments are not read'; do
  contains_normalized "$ref" "$literal" || fail "continuity reference missing Task 6 contract: $literal"
done
contains_normalized "$skill" 'pointer -> receipt v3 -> permanent marker' ||
  fail 'SKILL.md runtime loop omits the exact Task 6 publication order'
contains_normalized "$skill" 'without historical hydration' ||
  fail 'SKILL.md runtime loop omits bounded v3 recovery'

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
    "execute audit-governed work to closure or handoff",
    "activate for /implementaudit and audit closure",
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
description = description_value[1:-1].lower()
if not description.startswith("host-reported compaction stop"):
    raise SystemExit("compaction stop is not the first catalog-visible instruction")
if "use only the host-supplied skill path" not in description:
    raise SystemExit("description does not permit bounded skill loading")
if "do not search or inspect the target first" not in description:
    raise SystemExit("description does not forbid pre-custody target orientation")
if description.index("--current-controller") > description.index("execute audit-governed work"):
    raise SystemExit("ordinary activation precedes the compaction fence")
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

# Canonical rows are uppercase fixed-width HEX4; malformed or zero generations
# must not evade validation merely because their spelling is unrecognised.
epoch_case bad_generation \
"| g0002 | host-reported-compaction | 2026-07-18T02:00Z | repo@abc def | yes | - |" "" fail
epoch_case zero_generation \
"| G0000 | host-reported-compaction | 2026-07-18T02:00Z | repo@abc def | yes | - |" "" fail

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
    (*sys.argv[1:5], "G0001", "new-session", "continue implementation in the controller worktree"),
    (*sys.argv[5:9], "G0002", "host-reported-compaction", "qualify the authoritative successor before release"),
):
    p=Path(state); s=p.read_text(encoding="utf-8")
    s=s.replace("| Run root |  |", f"| Run root | `{run}` |")
    s=s.replace("| Next action |  |", f"| Next action | {action} |")
    s=s.replace("Current epoch: G0001", f"Current epoch: {epoch}")
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
    --boundary host-reported-compaction --epoch G0002) >/dev/null 2>&1; then
  fail "stale controller worktree emitted a successor continuity receipt"
fi

legacy_epoch_e2=e2
receipt="$(cd "$successor_repo" && bash "$claim_helper" --resume-controller release-v0333 \
  --boundary host-reported-compaction --epoch "$legacy_epoch_e2")" \
  || fail "current successor controller did not produce a continuity receipt"
case "$receipt" in refs/implementaudit/continuity-receipts/release-v0333/G0002@[0-9a-f][0-9a-f]*) :;; *) fail "continuity receipt did not canonicalise the legacy generation input";; esac
receipt_oid="${receipt##*@}"
receipt_record="$(git -C "$successor_repo" cat-file blob "$receipt_oid")"
"${py_cmd[@]}" - "$receipt_record" "$successor_claim" "$successor_head" "$successor_tree" <<'PY' \
  || fail "continuity receipt omitted receiver-required currentness state"
import sys
schema,controller,owner_oid,claim,head,tree,state,roadmap,invalidation,boundary,epoch,next_action=sys.argv[1].split("\t")
assert schema=="implementaudit.continuity-receipt.v2" and controller=="release-v0333"
assert claim==sys.argv[2] and head==sys.argv[3] and tree==sys.argv[4]
assert boundary=="host-reported-compaction" and epoch=="G0002"
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
s=s.replace("Current epoch: G0002", "Current epoch: G0003")
s=s.replace("| Next action | qualify the authoritative successor before release |",
            "| Next action | continue only after generic continuity recovery |")
anchor="| Epoch | Boundary provenance | Established at | Repo identity | Reconciled | Notes |\n|---|---|---|---|---|---|"
row=f"| G0003 | inferred-context-gap | 2026-08-12T13:05:00Z | repo at `{head}` / `{tree}` | yes | generic fallback reconciliation complete |"
p.write_text(s.replace(anchor, anchor+"\n"+row), encoding="utf-8")
PY

# The active invalidation boundary is part of deterministic currentness.  A
# caller may not relabel the same interrupted event as a different accepted
# provenance merely by writing a matching STATE row.
"${py_cmd[@]}" - "$successor_root/STATE.md" <<'PY'
import sys
from pathlib import Path
p = Path(sys.argv[1])
s = p.read_text(encoding="utf-8")
p.write_text(s.replace("| G0003 | inferred-context-gap |", "| G0003 | manual-resume |"), encoding="utf-8")
PY
if (cd "$successor_repo" && bash "$claim_helper" --resume-controller release-v0333 \
    --boundary manual-resume --epoch G0003) >/dev/null 2>&1; then
  fail "invalidation-boundary mismatch minted a continuity receipt"
fi
"${py_cmd[@]}" - "$successor_root/STATE.md" <<'PY'
import sys
from pathlib import Path
p = Path(sys.argv[1])
s = p.read_text(encoding="utf-8")
p.write_text(s.replace("| G0003 | manual-resume |", "| G0003 | inferred-context-gap |"), encoding="utf-8")
PY
if (cd "$successor_repo" && bash "$claim_helper" \
    --require-current-continuity release-v0333) >/dev/null 2>&1; then
  fail "partial continuity recovery without separate ROADMAP state became current"
fi
printf '\nGeneric continuity recovery reconciled live state.\n' >> "$successor_root/ROADMAP.md"
receipt_e3="$(cd "$successor_repo" && bash "$claim_helper" --resume-controller release-v0333 \
  --boundary inferred-context-gap --epoch G0003)" \
  || fail "generic no-native-hook recovery did not mint a fresh receipt"
(cd "$successor_repo" && bash "$claim_helper" --verify-resume-receipt "$receipt_e3") >/dev/null \
  || fail "generic no-native-hook continuity receipt did not verify"
receipt_e3_ref="${receipt_e3%@*}"
receipt_e3_oid="${receipt_e3##*@}"
receipt_e3_record="$(git -C "$successor_repo" cat-file blob "$receipt_e3_oid")"
forged_e3_record="${receipt_e3_record/$'\tinferred-context-gap\tG0003\t'/$'\tmanual-resume\tG0003\t'}"
[ "$forged_e3_record" != "$receipt_e3_record" ] \
  || fail "could not construct cross-boundary receipt negative"
forged_e3_oid="$(printf '%s' "$forged_e3_record" | git -C "$successor_repo" hash-object -w --stdin)"
git -C "$successor_repo" update-ref "$receipt_e3_ref" "$forged_e3_oid" "$receipt_e3_oid"
if (cd "$successor_repo" && bash "$claim_helper" \
    --verify-resume-receipt "$receipt_e3_ref@$forged_e3_oid") >/dev/null 2>&1; then
  fail "receipt verification accepted invalidation-boundary mismatch"
fi
git -C "$successor_repo" update-ref "$receipt_e3_ref" "$receipt_e3_oid" "$forged_e3_oid"
current_receipt="$(cd "$successor_repo" && bash "$claim_helper" \
  --require-current-continuity release-v0333)" \
  || fail "fresh generic continuity recovery did not reopen governed mutation"
[ "$current_receipt" = "$receipt_e3" ] \
  || fail "generic continuity recovery returned the wrong receipt"
if (cd "$successor_repo" && bash "$claim_helper" --resume-controller release-v0333 \
    --boundary host-reported-compaction --epoch G0002) >/dev/null 2>&1; then
  fail "a second writer claimed the same continuity epoch"
fi

# Task 6: once the canonical JSON pointer is current, R0011 alone mints and
# verifies the exact receipt v3.  Pointer-without-receipt and
# receipt-without-marker never become current; a marker cannot select the old
# root route.  Routine currentness remains bounded even when a cold segment is
# corrupt, while an explicit history read observes that corruption.
invalidation_e4="$(cd "$successor_repo" && bash "$claim_helper" \
  --invalidate-continuity release-v0333 --boundary manual-resume \
  --event task6-bounded-generation-e4 2>/dev/null)" \
  || fail 'Task 6 fixture could not mint its fresh invalidation'
invalidation_e4_oid="${invalidation_e4##*@}"
"${py_cmd[@]}" - "$successor_root/STATE.md" "$successor_head" "$successor_tree" <<'PY'
import sys
from pathlib import Path
p=Path(sys.argv[1]); head,tree=sys.argv[2:]
s=p.read_text(encoding="utf-8")
s=s.replace("Current epoch: G0003", "Current epoch: G0004")
s=s.replace("| Next action | continue only after generic continuity recovery |",
            "| Next action | resume through bounded generation currentness |")
anchor=(f"| G0003 | inferred-context-gap | 2026-08-12T13:05:00Z | "
        f"repo at `{head}` / `{tree}` | yes | generic fallback reconciliation complete |")
row=(f"| G0004 | manual-resume | 2026-08-12T13:10:00Z | "
     f"repo at `{head}` / `{tree}` | yes | bounded generation fixture complete |")
if s.count(anchor) != 1:
    raise SystemExit("Task 6 fixture lost the G0003 anchor")
p.write_text(s.replace(anchor,anchor+"\n"+row),encoding="utf-8")
PY
printf '\nTask 6 bounded generation recovery reconciled.\n' >>"$successor_root/ROADMAP.md"
printf '%s' '{"schema":"implementaudit.work-graph.fixture.v1"}' >"$successor_root/WORK_GRAPH.json"
task6_run_rel="${successor_root#$successor_repo/}"
mkdir -p "$successor_root/phases" "$successor_root/mutation-fences" \
  "$successor_repo/artifacts"
"${py_cmd[@]}" - "$repo_root/fixtures/phase-validation/valid-full-spec.md" \
  "$successor_root" "$task6_run_rel" "$successor_repo" <<'PY'
import json,sys
from pathlib import Path
template,run_root,run_rel,repo=map(Path,sys.argv[1:])
for phase,source in ((1,"protected-current"),(2,"protected-pointer-drift")):
    text=template.read_text(encoding="utf-8")
    text=text.replace("Phase: 1 of 3",f"Phase: {phase} of 2")
    text=text.replace("Run root: .IMPLEMENTAUDIT/runs/add-settings-Xy9Zq1",f"Run root: {run_rel.as_posix()}")
    text=text.replace("Baseline ref: abc123def456","Baseline ref: HEAD")
    text=text.replace("Owner/source: src/routes/settings.ts","Owner/source: issue:#200 D48-C02")
    needle="- Step 1: Create the settings route — target: src/routes/settings.ts (registerSettingsRoutes); change: add GET /api/settings handler behind requireAuth from src/middleware/auth.ts; verify: npm run build; expected: exit 0 with no errors"
    authority=json.dumps({"operation":"replace","source":source,"destination":None},separators=(",",":"))
    text=text.replace(needle,needle+"\n  mutation-authority: "+authority)
    scope=json.dumps({"in":[source],"out":["README.md"]},separators=(",",":"))
    text=text.replace("In scope: src/routes/settings.ts, tests/settings.test.ts, src/app.ts","In scope: D48-C02 pointer-aware protected mutation fixture\nMutation scope: "+scope)
    (run_root/"phases"/f"phase-{phase}.md").write_text(text,encoding="utf-8",newline="\n")
for name in ("protected-current","protected-pointer-drift"):
    (repo/name).write_bytes(b"ORIGINAL\n")
(repo/"artifacts"/"candidate-current.bin").write_bytes(b"CURRENT\n")
(repo/"artifacts"/"candidate-drift.bin").write_bytes(b"DRIFT\n")
PY
printf '%s\n' \
  '| 1 | D48-C02 pointer-aware current protected mutation |' \
  '| 2 | D48-C02 pointer/receipt drift refusal |' \
  >>"$successor_root/ROADMAP.md"
sed -i '/^| 1 |  |  | - |  |  |  | open |$/d' "$successor_root/ROADMAP.md"
task6_state_sha="$(sha256sum "$successor_root/STATE.md" | cut -d' ' -f1)"
task6_road_sha="$(sha256sum "$successor_root/ROADMAP.md" | cut -d' ' -f1)"
task6_graph_sha="$(sha256sum "$successor_root/WORK_GRAPH.json" | cut -d' ' -f1)"
task6_manifest_raw='{"schema_version":"implementaudit.generation-manifest.fixture.v1"}'
task6_manifest_oid="$(printf '%s' "$task6_manifest_raw" | git -C "$successor_repo" hash-object -w --stdin)"
task6_manifest_sha="$(printf '%s' "$task6_manifest_raw" | sha256sum | cut -d' ' -f1)"
task6_run_id="$(basename "$successor_root")"
task6_pointer_ref='refs/implementaudit/current-generations/release-v0333'
task6_marker_ref='refs/implementaudit/current-generation-migrations/release-v0333'
task6_v3_ref='refs/implementaudit/continuity-receipts/release-v0333/G0004'
task6_pointer_oid="$("${py_cmd[@]}" - "$successor_claim" "$task6_run_id" \
  "$task6_manifest_oid" "$task6_manifest_sha" "$task6_state_sha" "$task6_road_sha" \
  "$task6_graph_sha" <<'PY' | git -C "$successor_repo" hash-object -w --stdin
import hashlib,json,sys
claim,run,manifest_oid,manifest_digest,state,road,graph=sys.argv[1:]
body={
 "schema_version":"implementaudit.state-generation-pointer.v1",
 "controller_id":"release-v0333","claim_id":claim,"run_id":run,
 "generation_id":"G0004","source_epoch":"G0004",
 "predecessor_pointer_oid":None,"predecessor_pointer_digest":None,
 "generation_manifest_oid":manifest_oid,"generation_manifest_digest":manifest_digest,
 "cold_high_water":"00000000000000000001",
 "hot_state_digest":state,"hot_roadmap_digest":road,
 "work_graph_path":"WORK_GRAPH.json","work_graph_digest":graph,
 "query_contract_version":"implementaudit.history-query.v1",
 "degraded_state":"NONE",
}
canonical=lambda value: json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=False)
body["pointer_digest"]=hashlib.sha256(canonical(body).encode()).hexdigest()
print(canonical(body),end="")
PY
)"
git -C "$successor_repo" update-ref "$task6_pointer_ref" "$task6_pointer_oid" \
  0000000000000000000000000000000000000000

set +e
pointer_only="$(cd "$successor_repo" && bash "$claim_helper" \
  --require-current-continuity release-v0333 2>&1)"
pointer_only_rc=$?
set -e
[ "$pointer_only_rc" -ne 0 ] || fail 'Task 6 pointer without receipt became current'
grep -Fq FIRST_MIGRATION_INCOMPLETE <<<"$pointer_only" &&
  fail 'Task 6 pointer without receipt was misclassified as receipt without marker'

premature_marker_oid="$(printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s' \
  implementaudit.current-generation-migration.v1 release-v0333 "$successor_claim" \
  "$task6_run_id" G0004 "$task6_pointer_ref" implementaudit.state-generation-pointer.v1 \
  "$task6_v3_ref" 7777777777777777777777777777777777777777 true \
  | git -C "$successor_repo" hash-object -w --stdin)"
git -C "$successor_repo" update-ref "$task6_marker_ref" "$premature_marker_oid" \
  0000000000000000000000000000000000000000
set +e
premature_marker="$(cd "$successor_repo" && bash "$claim_helper" \
  --require-current-continuity release-v0333 2>&1)"
premature_marker_rc=$?
set -e
[ "$premature_marker_rc" -ne 0 ] || fail 'Task 6 marker before receipt became current'
grep -Fq STOP_NO_ROOT_FALLBACK <<<"$premature_marker" ||
  fail 'Task 6 marker before receipt did not forbid root fallback'
git -C "$successor_repo" update-ref -d "$task6_marker_ref" "$premature_marker_oid"

task6_v3="$(cd "$successor_repo" && bash "$claim_helper" --resume-controller \
  release-v0333 --boundary manual-resume --epoch G0004)" \
  || fail 'Task 6 R0011 path did not mint receipt v3'
(cd "$successor_repo" && bash "$claim_helper" --verify-resume-receipt "$task6_v3") >/dev/null \
  || fail 'Task 6 R0011 path did not reread and verify receipt v3'
set +e
pre_marker="$(cd "$successor_repo" && bash "$claim_helper" \
  --require-current-continuity release-v0333 2>&1)"
pre_marker_rc=$?
set -e
[ "$pre_marker_rc" -ne 0 ] || fail 'Task 6 receipt v3 without marker became current'
grep -Fq FIRST_MIGRATION_INCOMPLETE <<<"$pre_marker" ||
  fail 'Task 6 receipt v3 without marker lost its exact stop outcome'
task6_v3_oid="${task6_v3##*@}"
task6_marker_oid="$(printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s' \
  implementaudit.current-generation-migration.v1 release-v0333 "$successor_claim" \
  "$task6_run_id" G0004 "$task6_pointer_ref" implementaudit.state-generation-pointer.v1 \
  "$task6_v3_ref" "$task6_v3_oid" true \
  | git -C "$successor_repo" hash-object -w --stdin)"
git -C "$successor_repo" update-ref "$task6_marker_ref" "$task6_marker_oid" \
  0000000000000000000000000000000000000000
task6_current="$(cd "$successor_repo" && bash "$claim_helper" \
  --require-current-continuity release-v0333)" \
  || fail 'Task 6 complete pointer/v3/marker route was not current'
[ "$task6_current" = "$task6_v3" ] || fail 'Task 6 complete route returned the wrong receipt'

"${py_cmd[@]}" - "$successor_root" "$task6_current" "$receipt_e3" <<'PY'
import hashlib,json,sys
from pathlib import Path
root,current,stale=sys.argv[1:]
root=Path(root)
for phase,source,receipt in (
    (1,"protected-current",current),
    (2,"protected-pointer-drift",stale),
):
    target=root.parents[2]/source
    payload={
      "schema":"implementaudit.protected-mutation-fence.v1",
      "phase":phase,"step":1,"source_path":source,
      "protected_target":{"sha256":hashlib.sha256(target.read_bytes()).hexdigest(),"byte_length":len(target.read_bytes())},
      "controller_generation":"G0004","authority_generation":"G0004",
      "protected_generation":"G0004","verified_resume_receipt":receipt,
      "sink_capability":"REJECT_AND_REPORT","controller_id":"release-v0333",
    }
    (root/"mutation-fences"/f"phase-{phase}-step-1.json").write_text(
        json.dumps(payload,sort_keys=True,separators=(",",":"))+"\n",encoding="utf-8",newline="\n")
PY
task6_mutation_out="$tmp/task6-protected-current.out"
bash "$mutation_helper" --repo-root "$successor_repo" --run-root "$successor_root" \
  --phase 1 --step 1 --preimage "$successor_repo/protected-current" \
  --candidate "$successor_repo/artifacts/candidate-current.bin" >"$task6_mutation_out" \
  || fail 'Task 6 pointer/v3 current generation did not reach the cooperating sink'
"${py_cmd[@]}" - "$task6_mutation_out" "$successor_root" "$task6_pointer_ref" \
  "$task6_pointer_oid" "$task6_v3_ref" "$task6_v3_oid" <<'PY' \
  || fail 'Task 6 protected mutation did not bind the pointer/v3 generation'
import json,sys
from pathlib import Path
out,root,pref,poid,rref,roid=sys.argv[1:]
result=json.loads(Path(out).read_text(encoding="utf-8"))
generation=result.get("identity_bindings",{}).get("generation",{})
if result.get("status")!="COMMITTED" or generation!={
 "generation_id":"G0004","receipt_schema":"implementaudit.continuity-receipt.v3",
 "receipt_ref":rref,"receipt_oid":roid,"pointer_ref":pref,"pointer_oid":poid,
 "pointer_digest":generation.get("pointer_digest"),
}: raise SystemExit(result)
if not isinstance(generation["pointer_digest"],str) or len(generation["pointer_digest"])!=64: raise SystemExit(generation)
transaction=result["transaction_id"]
authority=json.loads((Path(root)/"mutation-transactions"/transaction/"authority.json").read_text(encoding="utf-8"))
durable=json.loads((Path(root)/"mutation-transactions"/transaction/"result.json").read_text(encoding="utf-8"))
if authority.get("identity_bindings")!=result["identity_bindings"] or durable!=result: raise SystemExit("durable binding drift")
PY
[ "$(od -An -tx1 -v "$successor_repo/protected-current" | tr -d ' \n')" = 43555252454e540a ] \
  || fail 'Task 6 current protected mutation did not publish exact candidate bytes'
task6_drift_out="$tmp/task6-protected-pointer-drift.out"
set +e
bash "$mutation_helper" --repo-root "$successor_repo" --run-root "$successor_root" \
  --phase 2 --step 1 --preimage "$successor_repo/protected-pointer-drift" \
  --candidate "$successor_repo/artifacts/candidate-drift.bin" >"$task6_drift_out" 2>"$tmp/task6-protected-pointer-drift.err"
task6_drift_rc=$?
set -e
[ "$task6_drift_rc" -eq 64 ] || fail "Task 6 pointer/receipt drift exit=$task6_drift_rc expected=64"
"${py_cmd[@]}" - "$task6_drift_out" "$successor_root" <<'PY' \
  || fail 'Task 6 pointer/receipt drift did not reject before effect'
import json,sys
from pathlib import Path
r=json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
if r.get("status")!="REJECTED_NO_MUTATION" or r.get("reason_code")!="POINTER_RECEIPT_DRIFT": raise SystemExit(r)
if r.get("transaction_id") is not None or r.get("actual_effect_set")!=[]: raise SystemExit(r)
claim=r["claim_id"]
if (Path(sys.argv[2])/"mutation-transactions"/f"{claim}-p2-s1").exists(): raise SystemExit("transaction created")
PY
[ "$(od -An -tx1 -v "$successor_repo/protected-pointer-drift" | tr -d ' \n')" = 4f524947494e414c0a ] \
  || fail 'Task 6 pointer/receipt drift changed the protected target'
printf '%s\n' 'D48_C02_POINTER_V3_FENCE=PASS current=COMMITTED drift=REJECTED_NO_MUTATION'

task6_event_id="iaevt-v1-$(printf 'a%.0s' {1..64})"
task6_event_ref="refs/implementaudit/state-event-segments/$task6_run_id/G0004/00000000000000000001/$task6_event_id"
task6_corrupt_oid="$(printf 'not-json' | git -C "$successor_repo" hash-object -w --stdin)"
git -C "$successor_repo" update-ref "$task6_event_ref" "$task6_corrupt_oid"
bounded_current="$(cd "$successor_repo" && bash "$claim_helper" \
  --require-current-continuity release-v0333)" \
  || fail 'routine v3 currentness hydrated a corrupt historical segment'
[ "$bounded_current" = "$task6_v3" ] || fail 'bounded v3 recovery returned the wrong receipt'
if ! "${py_cmd[@]}" - "$repo_root/skills/implementaudit/scripts/rotate-canonical-state.py" \
    "$successor_repo" "$task6_run_id" "$task6_event_id" <<'PY'
import importlib.util,json,sys
from pathlib import Path
spec=importlib.util.spec_from_file_location("continuity_task6_rotation",sys.argv[1])
module=importlib.util.module_from_spec(spec); sys.modules[spec.name]=module
assert spec.loader is not None; spec.loader.exec_module(module)
raw=module.load_exact_segment_bytes_v1(
    Path(sys.argv[2]),sys.argv[3],"G0004","00000000000000000001",sys.argv[4])
try:
    json.loads(raw.decode("utf-8","strict"))
except json.JSONDecodeError:
    raise SystemExit(0)
raise SystemExit(1)
PY
then
  fail 'explicit history query did not isolate corrupt segment failure'
fi
printf '%s\n' \
  'CONTINUITY_TASK6_GREEN=PASS order=POINTER_RECEIPT_V3_MARKER bounded-current=NO_HISTORY_READ explicit-history=CORRUPT_STOP'

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
r=f"| G0001 | host-reported-compaction | 2026-08-12T12:00:00Z | repo at `{head}` / `{tree}` | yes | separate live reads complete |"
p.write_text(s.replace(a,a+"\n"+r),encoding="utf-8")
PY
(cd "$positive_repo" && bash "$claim_helper" --resume-controller positive-n06 \
  --boundary host-reported-compaction --epoch G0001) >/dev/null \
  || fail "positive same-controller continuity case failed"

# An unchanged historical state/receipt pair remains exactly verifiable. New
# receipt minting canonicalises aliases, but verification never rewrites legacy
# evidence in place.
positive_claim="$(sed -n 's/^claim_id=//p' "$positive_root/.claimed")"
positive_owner="$(git -C "$positive_repo" rev-parse refs/implementaudit/controllers/positive-n06)"
positive_head="$(git -C "$positive_repo" rev-parse HEAD)"
positive_tree="$(git -C "$positive_repo" rev-parse 'HEAD^{tree}')"
"${py_cmd[@]}" - "$positive_root/STATE.md" <<'PY'
import sys
from pathlib import Path
p=Path(sys.argv[1]); s=p.read_text(encoding="utf-8")
s=s.replace("Current epoch: G0001", "Current epoch: e1")  # legacy spelling compatibility fixture
s=s.replace("| G0001 | host-reported-compaction |", "| e1 | host-reported-compaction |")
p.write_text(s,encoding="utf-8")
PY
positive_state_sha="$(sha256sum "$positive_root/STATE.md" | cut -d' ' -f1)"
positive_road_sha="$(sha256sum "$positive_root/ROADMAP.md" | cut -d' ' -f1)"
legacy_record="$(printf 'implementaudit.continuity-receipt.v1\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s' \
  positive-n06 "$positive_owner" "$positive_claim" "$positive_head" "$positive_tree" \
  "$positive_state_sha" "$positive_road_sha" host-reported-compaction e1 legacy-currentness)"
legacy_oid="$(printf '%s' "$legacy_record" | git -C "$positive_repo" hash-object -w --stdin)"
legacy_ref=refs/implementaudit/continuity-receipts/positive-n06/e1 # legacy spelling compatibility fixture
git -C "$positive_repo" update-ref "$legacy_ref" "$legacy_oid"
(cd "$positive_repo" && bash "$claim_helper" --verify-resume-receipt "$legacy_ref@$legacy_oid") >/dev/null \
  || fail "unchanged legacy continuity receipt no longer verifies"
if (cd "$positive_repo" && bash "$claim_helper" \
    --require-current-continuity positive-n06) >/dev/null 2>&1; then
  fail "legacy v1 receipt became a current recovery route"
fi

# Ordinary bounded claims remain the no-registry cheap path.
cheap_rel="$(cd "$positive_repo" && IMPLEMENTAUDIT_BASE=.IMPLEMENTAUDIT/runs \
  bash "$claim_helper" 'small ordinary task' 2>/dev/null)"
[ -f "$positive_repo/$cheap_rel/.claimed" ] || fail "ordinary claim cheap path regressed"
[ ! -e "$positive_repo/$cheap_rel/.controller" ] || fail 'ordinary cheap path acquired controller ceremony'

printf 'continuity-contract.test: ok (surfaces + validator: legacy pass, honest-provenance, kind/status tokens, terminal-status evidence)\n'
