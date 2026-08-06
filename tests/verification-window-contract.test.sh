#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
checker="$repo_root/skills/implementaudit/scripts/check-evidence-anchor.sh"
cases="$repo_root/fixtures/verification-window/cases.json"
protocol="$repo_root/skills/implementaudit/templates/PROTOCOL.md"
phase_design="$repo_root/skills/implementaudit/references/phase-design.md"
lean="$repo_root/skills/implementaudit/references/lean-operating-discipline.md"
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
count=0

if command -v python >/dev/null 2>&1; then
  py_cmd=(python)
elif command -v python3 >/dev/null 2>&1; then
  py_cmd=(python3)
elif command -v py >/dev/null 2>&1; then
  py_cmd=(py -3)
else
  printf 'verification-window-contract.test: python is required\n' >&2
  exit 1
fi

ok() { count=$((count + 1)); }
fail() { printf 'verification-window-contract.test: %s\n' "$*" >&2; exit 1; }

"${py_cmd[@]}" - "$cases" <<'PY'
import json, sys
rows = json.load(open(sys.argv[1], encoding="utf-8"))
ids = [row.get("id") for row in rows]
expected = [f"R2-F{i}" for i in range(1, 8)]
if ids != expected:
    raise SystemExit(f"verification-window cases must be exactly {expected}, got {ids}")
PY
ok

new_repo() {
  case_repo="$tmp/$1"
  mkdir -p "$case_repo/curriculum" "$case_repo/docs" "$case_repo/scratch"
  git -C "$case_repo" init -q
  git -C "$case_repo" config user.name fixture
  git -C "$case_repo" config user.email fixture@example.invalid
  printf 'original\n' > "$case_repo/curriculum/x.json"
  printf 'docs\n' > "$case_repo/docs/readme.md"
  git -C "$case_repo" add .
  git -C "$case_repo" commit -qm base
  case_opened="$(git -C "$case_repo" rev-parse HEAD)"
}

write_intent() {
  local repo="$1" state="$2" surface="${3:-curriculum/**}"
  local closed_at=none
  if [ "$state" = closed ]; then
    closed_at="$(git -C "$repo" rev-parse HEAD)"
  fi
  mkdir -p "$repo/.IMPLEMENTAUDIT/runs/window/background/chain-a"
  printf '%s\n' \
    'command: verify-curriculum' \
    'owner/source: tests/verification-window-contract.test.sh' \
    'expected_completion_marker: chain.done' \
    'abort_containment_plan: fixture-only' \
    'poll_budget: 3' \
    'terminal_signal: chain.done' \
    'expected_duration: 20m' \
    'transport_timeout: 10m' \
    'launch_mode: detached' \
    'verification_window:' \
    "  - surfaces: [$surface]" \
    "    opened_at: $case_opened" \
    "    closed_at: $closed_at" \
    '    chain: chain-a' \
    "    state: $state" \
    > "$repo/.IMPLEMENTAUDIT/runs/window/background/chain-a/launch-intent.md"
  case_intent="$repo/.IMPLEMENTAUDIT/runs/window/background/chain-a/launch-intent.md"
}

# R2-F1 / R2-F3: an intersecting committed change during an open window fails
# and names both anchors, the declared surface, and the intersecting path.
new_repo f1
write_intent "$case_repo" open
printf 'mutated\n' > "$case_repo/curriculum/x.json"
git -C "$case_repo" add curriculum/x.json
git -C "$case_repo" commit -qm intersecting
case_now="$(git -C "$case_repo" rev-parse HEAD)"
if (cd "$case_repo" && bash "$checker" --window "$case_intent" --now "$case_now") >"$tmp/f1.out" 2>&1; then
  fail 'R2-F1 expected intersecting open-window change to fail'
fi
grep -Fq "$case_opened" "$tmp/f1.out" || fail 'R2-F3 output missing opened_at SHA'
grep -Fq "$case_now" "$tmp/f1.out" || fail 'R2-F3 output missing now SHA'
grep -Fq 'curriculum/**' "$tmp/f1.out" || fail 'R2-F3 output missing declared surfaces'
grep -Fq 'curriculum/x.json' "$tmp/f1.out" || fail 'R2-F1 output missing intersecting path'
ok; ok

# R2-F2: the staged patch is disjoint while open, then the target mutation is
# permitted only after the completion marker and window closure.
new_repo f2
write_intent "$case_repo" open
printf 'apply curriculum change after chain.done\n' > "$case_repo/scratch/window.patch"
git -C "$case_repo" add scratch/window.patch
git -C "$case_repo" commit -qm staged-patch
case_now="$(git -C "$case_repo" rev-parse HEAD)"
(cd "$case_repo" && bash "$checker" --window "$case_intent" --now "$case_now") >"$tmp/f2-open.out" 2>&1 \
  || fail 'R2-F2 staged patch outside declared surface must pass'
touch "$case_repo/.IMPLEMENTAUDIT/runs/window/background/chain-a/chain.done"
write_intent "$case_repo" closed
printf 'mutated after close\n' > "$case_repo/curriculum/x.json"
git -C "$case_repo" add curriculum/x.json
git -C "$case_repo" commit -qm after-close
case_now="$(git -C "$case_repo" rev-parse HEAD)"
(cd "$case_repo" && bash "$checker" --window "$case_intent" --now "$case_now") >"$tmp/f2-closed.out" 2>&1 \
  || fail 'R2-F2 target mutation after completion and closure must pass'
ok

# R2-F4: a closed window does not freeze later ordinary work.
new_repo f4
write_intent "$case_repo" closed
touch "$case_repo/.IMPLEMENTAUDIT/runs/window/background/chain-a/chain.done"
printf 'later\n' > "$case_repo/curriculum/x.json"
git -C "$case_repo" add curriculum/x.json
git -C "$case_repo" commit -qm later
case_now="$(git -C "$case_repo" rev-parse HEAD)"
(cd "$case_repo" && bash "$checker" --window "$case_intent" --now "$case_now") >"$tmp/f4.out" 2>&1 \
  || fail 'R2-F4 closed-window mutation must pass'
ok

# Poka-Yoke controls: "closed" is not self-authenticating. Closure without the
# declared terminal marker fails, as does a closing anchor whose window diff
# intersects the declared surface.
new_repo premature-close
write_intent "$case_repo" closed
case_now="$(git -C "$case_repo" rev-parse HEAD)"
if (cd "$case_repo" && bash "$checker" --window "$case_intent" --now "$case_now") >/dev/null 2>&1; then
  fail 'premature closed declaration without chain.done must fail'
fi
ok

new_repo intersecting-close
write_intent "$case_repo" open
printf 'mutated before close\n' > "$case_repo/curriculum/x.json"
git -C "$case_repo" add curriculum/x.json
git -C "$case_repo" commit -qm intersecting-before-close
touch "$case_repo/.IMPLEMENTAUDIT/runs/window/background/chain-a/chain.done"
write_intent "$case_repo" closed
case_now="$(git -C "$case_repo" rev-parse HEAD)"
if (cd "$case_repo" && bash "$checker" --window "$case_intent" --now "$case_now") >"$tmp/intersecting-close.out" 2>&1; then
  fail 'intersecting mutation before the closing anchor must fail'
fi
grep -Fq 'curriculum/x.json' "$tmp/intersecting-close.out" \
  || fail 'intersecting close failure must name the changed path'
ok

# R2-F5: a complete anchor-to-now diff that is disjoint from the declared
# surface passes even while the window remains open.
new_repo f5
write_intent "$case_repo" open
printf 'changed docs\n' > "$case_repo/docs/readme.md"
git -C "$case_repo" add docs/readme.md
git -C "$case_repo" commit -qm disjoint
case_now="$(git -C "$case_repo" rev-parse HEAD)"
(cd "$case_repo" && bash "$checker" --window "$case_intent" --now "$case_now") >"$tmp/f5.out" 2>&1 \
  || fail 'R2-F5 disjoint open-window change must pass'
grep -qi 'disjoint' "$tmp/f5.out" || fail 'R2-F5 output must state the disjoint basis'
ok

# R2-F6: compound stash/check/restore loses the restore when the check exits
# 124, leaving the mutation hidden in a stash. The contract must prohibit it.
new_repo f6
printf 'dirty\n' > "$case_repo/curriculum/x.json"
set +e
(cd "$case_repo" && bash -c 'set -e; git stash push -q; bash -c "exit 124"; git stash pop -q')
compound_exit=$?
set -e
[ "$compound_exit" -eq 124 ] || fail "R2-F6 expected producer exit 124, got $compound_exit"
[ -z "$(git -C "$case_repo" status --short)" ] || fail 'R2-F6 expected mutation to be hidden after aborted compound restore'
[ -n "$(git -C "$case_repo" stash list)" ] || fail 'R2-F6 expected retained stash proving hidden mutation'
grep -Fq 'Compound shell verification' "$protocol" || fail 'R2-F6 compound verification prohibition missing'
ok

# Legacy anchor modes remain compatible.
bash "$checker" --row 'legacy evidence without an anchor' >/dev/null
artifact="$tmp/artifact.md"
printf 'Anchor: 0123456789abcdef0123456789abcdef01234567\n' > "$artifact"
bash "$checker" --artifact "$artifact" --tree 0123456789abcdef0123456789abcdef01234567 >/dev/null
ok

# Contract placement and cross-reference controls.
grep -Fq '7. Verification-window freeze.' "$protocol" || fail 'PROTOCOL item 7 was not filled'
grep -Fq '8. Wait contract.' "$protocol" || fail '#81 item 8 moved'
grep -Fq '12. Checkpoint before block.' "$protocol" || fail '#81 item 12 moved'
grep -Fq 'verification is reading the same tree' "$phase_design" || fail 'phase-design verification boundary missing'
grep -Fq 'post-state was compared' "$lean" || fail 'Lean post-state evidence boundary missing'
ok; ok; ok; ok; ok

printf 'verification-window-contract.test: ok (%d/15)\n' "$count"
