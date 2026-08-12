#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
checker="$repo_root/skills/implementaudit/scripts/check-evidence-anchor.sh"
repo_state="$repo_root/skills/implementaudit/scripts/repo-state.sh"
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
expected = [f"R2-F{i}" for i in range(1, 48)]
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
  local opening_receipt="$repo/.IMPLEMENTAUDIT/runs/window/background/chain-a/opening-identities.nul"
  local closing_receipt="$repo/.IMPLEMENTAUDIT/runs/window/background/chain-a/closing-identities.nul"
  if [ "$state" = closed ]; then
    closed_at="$(git -C "$repo" rev-parse HEAD)"
  fi
  mkdir -p "$repo/.IMPLEMENTAUDIT/runs/window/background/chain-a"
  if [ ! -f "$opening_receipt" ]; then
    (cd "$repo" && bash "$repo_state" window-identities --records --surface "$surface" > "$opening_receipt") \
      || fail 'unable to record opening identity receipt'
  fi
  if [ "$state" = closed ]; then
    (cd "$repo" && bash "$repo_state" window-identities --records --surface "$surface" > "$closing_receipt") \
      || fail 'unable to record closing identity receipt'
  fi
  local opening_digest
  opening_digest="$(sha256sum "$opening_receipt" | awk '{print $1}')"
  local closing_digest=none
  if [ "$state" = closed ]; then
    closing_digest="$(sha256sum "$closing_receipt" | awk '{print $1}')"
  fi
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
    '    opening_identity_receipt: opening-identities.nul' \
    "    opening_identity_sha256: $opening_digest" \
    "    closing_identity_receipt: $([ "$state" = closed ] && printf '%s' closing-identities.nul || printf none)" \
    "    closing_identity_sha256: $closing_digest" \
    > "$repo/.IMPLEMENTAUDIT/runs/window/background/chain-a/launch-intent.md"
  case_intent="$repo/.IMPLEMENTAUDIT/runs/window/background/chain-a/launch-intent.md"
}

write_prepared_intent() {
  local repo="$1" run="$2" surface="${3:-curriculum/**}"
  local promised
  for promised in STATE.md PROTOCOL.md ROADMAP.md THINKING.md sidecars.md tools.md context.md; do
    cp "$repo_root/skills/implementaudit/templates/$promised" "$run/$promised"
  done
  mkdir -p "$run/background/chain-a"
  printf '%s\n' \
    'command: verify-curriculum' \
    'owner/source: tests/verification-window-contract.test.sh' \
    'expected_completion_marker: chain.done' \
    'verification_window:' \
    "  - surfaces: [$surface]" \
    '    opened_at: none' \
    '    closed_at: none' \
    '    chain: chain-a' \
    '    state: prepared' \
    '    opening_identity_receipt: none' \
    '    opening_identity_sha256: none' \
    '    closing_identity_receipt: none' \
    '    closing_identity_sha256: none' \
    >"$run/background/chain-a/launch-intent.md"
  case_intent="$run/background/chain-a/launch-intent.md"
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

# R2-F8: an ignored, declared file remains a live verification surface. This
# starts with HEAD at opened_at, so an enumerator that only consults committed
# diffs or standard untracked files incorrectly returns the anchor-current PASS.
new_repo f8-ignored
printf 'ignored/**\n' > "$case_repo/.gitignore"
git -C "$case_repo" add .gitignore
git -C "$case_repo" commit -qm ignore-declared-surface
case_opened="$(git -C "$case_repo" rev-parse HEAD)"
write_intent "$case_repo" open 'ignored/declared.txt'
mkdir -p "$case_repo/ignored"
printf 'mutated while open\n' > "$case_repo/ignored/declared.txt"
case_now="$(git -C "$case_repo" rev-parse HEAD)"
if (cd "$case_repo" && bash "$checker" --window "$case_intent" --now "$case_now") >"$tmp/f8.out" 2>&1; then
  fail 'R2-F8 declared ignored surface mutation during an open window must fail'
fi
grep -Fq 'ignored/declared.txt' "$tmp/f8.out" || fail 'R2-F8 output missing ignored changed path'
ok

# R2-F9: a declared run-root file is a live verification surface even though
# the ordinary repo-state census deliberately excludes .IMPLEMENTAUDIT/.
new_repo f9-run-root
write_intent "$case_repo" open '.IMPLEMENTAUDIT/runs/window/live/**'
mkdir -p "$case_repo/.IMPLEMENTAUDIT/runs/window/live"
printf 'mutated while open\n' > "$case_repo/.IMPLEMENTAUDIT/runs/window/live/declared.txt"
case_now="$(git -C "$case_repo" rev-parse HEAD)"
if (cd "$case_repo" && bash "$checker" --window "$case_intent" --now "$case_now") >"$tmp/f9.out" 2>&1; then
  fail 'R2-F9 declared run-root surface mutation during an open window must fail'
fi
grep -Fq '.IMPLEMENTAUDIT/runs/window/live/declared.txt' "$tmp/f9.out" \
  || fail 'R2-F9 output missing run-root changed path'
ok

# R2-F10: a declared directory covers its descendants, rather than requiring
# every child to be repeated as a separate path/glob surface.
new_repo f10-directory
write_intent "$case_repo" open 'curriculum/'
printf 'mutated\n' > "$case_repo/curriculum/x.json"
git -C "$case_repo" add curriculum/x.json
git -C "$case_repo" commit -qm directory-intersection
case_now="$(git -C "$case_repo" rev-parse HEAD)"
if (cd "$case_repo" && bash "$checker" --window "$case_intent" --now "$case_now") >"$tmp/f10.out" 2>&1; then
  fail 'R2-F10 declared directory mutation during an open window must fail'
fi
grep -Fq 'curriculum/x.json' "$tmp/f10.out" || fail 'R2-F10 output missing directory child path'
ok

# R2-F11: deletion is a declared-surface mutation even when the path is absent
# when the window is checked.
new_repo f11-missing
mkdir -p "$case_repo/missing"
printf 'present at open\n' > "$case_repo/missing/declared.txt"
git -C "$case_repo" add missing/declared.txt
git -C "$case_repo" commit -qm missing-path-at-open
case_opened="$(git -C "$case_repo" rev-parse HEAD)"
write_intent "$case_repo" open 'missing/declared.txt'
rm "$case_repo/missing/declared.txt"
case_now="$(git -C "$case_repo" rev-parse HEAD)"
if (cd "$case_repo" && bash "$checker" --window "$case_intent" --now "$case_now") >"$tmp/f11.out" 2>&1; then
  fail 'R2-F11 deleted declared path during an open window must fail'
fi
grep -Fq 'missing/declared.txt' "$tmp/f11.out" || fail 'R2-F11 output missing deleted path'
ok

# R2-F12: the glob control remains enforced by the repaired enumeration.
new_repo f12-glob
write_intent "$case_repo" open 'curriculum/*.json'
printf 'mutated\n' > "$case_repo/curriculum/x.json"
git -C "$case_repo" add curriculum/x.json
git -C "$case_repo" commit -qm glob-intersection
case_now="$(git -C "$case_repo" rev-parse HEAD)"
if (cd "$case_repo" && bash "$checker" --window "$case_intent" --now "$case_now") >"$tmp/f12.out" 2>&1; then
  fail 'R2-F12 declared glob mutation during an open window must fail'
fi
ok

# R2-F13: complete enumeration remains surface-specific. An ignored held-out
# path does not stale a window whose declared ignored surface is disjoint.
new_repo f13-held-out
printf 'ignored/**\n' > "$case_repo/.gitignore"
git -C "$case_repo" add .gitignore
git -C "$case_repo" commit -qm ignore-held-out
case_opened="$(git -C "$case_repo" rev-parse HEAD)"
write_intent "$case_repo" open 'ignored/declared/**'
mkdir -p "$case_repo/ignored"
printf 'held out\n' > "$case_repo/ignored/not-declared.txt"
case_now="$(git -C "$case_repo" rev-parse HEAD)"
(cd "$case_repo" && bash "$checker" --window "$case_intent" --now "$case_now") >"$tmp/f13.out" 2>&1 \
  || fail 'R2-F13 ignored held-out path must remain disjoint'
ok

# R2-F14: a closed equal-SHA window still has to inspect its complete current
# identity population. The ignored mutation occurs before chain.done but does
# not move HEAD.
new_repo f14-closed-equal-ignored
printf 'ignored/**\n' > "$case_repo/.gitignore"
git -C "$case_repo" add .gitignore
git -C "$case_repo" commit -qm ignore-closed-equal
case_opened="$(git -C "$case_repo" rev-parse HEAD)"
write_intent "$case_repo" open 'ignored/declared.txt'
mkdir -p "$case_repo/ignored"
printf 'mutated before close\n' > "$case_repo/ignored/declared.txt"
touch "$case_repo/.IMPLEMENTAUDIT/runs/window/background/chain-a/chain.done"
write_intent "$case_repo" closed 'ignored/declared.txt'
case_now="$(git -C "$case_repo" rev-parse HEAD)"
if (cd "$case_repo" && bash "$checker" --window "$case_intent" --now "$case_now") >"$tmp/f14.out" 2>&1; then
  fail 'R2-F14 closed equal-SHA ignored mutation must fail'
fi
grep -Fq 'ignored/declared.txt' "$tmp/f14.out" || fail 'R2-F14 output missing ignored path'
ok

# R2-F15: an ignored mutation before a historical closing anchor must not be
# erased by the tracked-only opened-to-closed diff.
new_repo f15-closed-historical-ignored
printf 'ignored/**\n' > "$case_repo/.gitignore"
git -C "$case_repo" add .gitignore
git -C "$case_repo" commit -qm ignore-closed-historical
case_opened="$(git -C "$case_repo" rev-parse HEAD)"
write_intent "$case_repo" open 'ignored/declared.txt'
mkdir -p "$case_repo/ignored"
printf 'mutated before close\n' > "$case_repo/ignored/declared.txt"
printf 'closing anchor\n' > "$case_repo/docs/readme.md"
git -C "$case_repo" add docs/readme.md
git -C "$case_repo" commit -qm historical-close
touch "$case_repo/.IMPLEMENTAUDIT/runs/window/background/chain-a/chain.done"
write_intent "$case_repo" closed 'ignored/declared.txt'
printf 'later ordinary work\n' > "$case_repo/scratch/later.txt"
git -C "$case_repo" add scratch/later.txt
git -C "$case_repo" commit -qm post-close
case_now="$(git -C "$case_repo" rev-parse HEAD)"
if (cd "$case_repo" && bash "$checker" --window "$case_intent" --now "$case_now") >"$tmp/f15.out" 2>&1; then
  fail 'R2-F15 historical closed ignored mutation must fail'
fi
grep -Fq 'ignored/declared.txt' "$tmp/f15.out" || fail 'R2-F15 output missing ignored path'
ok

# R2-F16: the closed equal-SHA route also retains a declared run-root path.
new_repo f16-closed-equal-run-root
write_intent "$case_repo" open '.IMPLEMENTAUDIT/runs/window/live/declared.txt'
mkdir -p "$case_repo/.IMPLEMENTAUDIT/runs/window/live"
printf 'mutated before close\n' > "$case_repo/.IMPLEMENTAUDIT/runs/window/live/declared.txt"
touch "$case_repo/.IMPLEMENTAUDIT/runs/window/background/chain-a/chain.done"
write_intent "$case_repo" closed '.IMPLEMENTAUDIT/runs/window/live/declared.txt'
case_now="$(git -C "$case_repo" rev-parse HEAD)"
if (cd "$case_repo" && bash "$checker" --window "$case_intent" --now "$case_now") >"$tmp/f16.out" 2>&1; then
  fail 'R2-F16 closed equal-SHA run-root mutation must fail'
fi
grep -Fq '.IMPLEMENTAUDIT/runs/window/live/declared.txt' "$tmp/f16.out" \
  || fail 'R2-F16 output missing run-root path'
ok

# R2-F17: historical closure also retains declared run-root mutations.
new_repo f17-closed-historical-run-root
write_intent "$case_repo" open '.IMPLEMENTAUDIT/runs/window/live/declared.txt'
mkdir -p "$case_repo/.IMPLEMENTAUDIT/runs/window/live"
printf 'mutated before close\n' > "$case_repo/.IMPLEMENTAUDIT/runs/window/live/declared.txt"
printf 'closing anchor\n' > "$case_repo/docs/readme.md"
git -C "$case_repo" add docs/readme.md
git -C "$case_repo" commit -qm historical-close
touch "$case_repo/.IMPLEMENTAUDIT/runs/window/background/chain-a/chain.done"
write_intent "$case_repo" closed '.IMPLEMENTAUDIT/runs/window/live/declared.txt'
printf 'later ordinary work\n' > "$case_repo/scratch/later.txt"
git -C "$case_repo" add scratch/later.txt
git -C "$case_repo" commit -qm post-close
case_now="$(git -C "$case_repo" rev-parse HEAD)"
if (cd "$case_repo" && bash "$checker" --window "$case_intent" --now "$case_now") >"$tmp/f17.out" 2>&1; then
  fail 'R2-F17 historical closed run-root mutation must fail'
fi
grep -Fq '.IMPLEMENTAUDIT/runs/window/live/declared.txt' "$tmp/f17.out" \
  || fail 'R2-F17 output missing run-root path'
ok

# R2-F18: a declared ignored identity present at opening cannot disappear
# silently while the window is open.
new_repo f18-deleted-ignored
printf 'ignored/**\n' > "$case_repo/.gitignore"
git -C "$case_repo" add .gitignore
git -C "$case_repo" commit -qm ignore-deletion
mkdir -p "$case_repo/ignored"
printf 'present at open\n' > "$case_repo/ignored/declared.txt"
case_opened="$(git -C "$case_repo" rev-parse HEAD)"
write_intent "$case_repo" open 'ignored/declared.txt'
rm "$case_repo/ignored/declared.txt"
case_now="$(git -C "$case_repo" rev-parse HEAD)"
if (cd "$case_repo" && bash "$checker" --window "$case_intent" --now "$case_now") >"$tmp/f18.out" 2>&1; then
  fail 'R2-F18 deleted ignored surface during an open window must fail'
fi
grep -Fq 'ignored/declared.txt' "$tmp/f18.out" || fail 'R2-F18 output missing deleted ignored path'
ok

# R2-F19: the opening identity receipt also makes a deleted declared run-root
# path visible to the open-window check.
new_repo f19-deleted-run-root
mkdir -p "$case_repo/.IMPLEMENTAUDIT/runs/window/live"
printf 'present at open\n' > "$case_repo/.IMPLEMENTAUDIT/runs/window/live/declared.txt"
write_intent "$case_repo" open '.IMPLEMENTAUDIT/runs/window/live/declared.txt'
rm "$case_repo/.IMPLEMENTAUDIT/runs/window/live/declared.txt"
case_now="$(git -C "$case_repo" rev-parse HEAD)"
if (cd "$case_repo" && bash "$checker" --window "$case_intent" --now "$case_now") >"$tmp/f19.out" 2>&1; then
  fail 'R2-F19 deleted run-root surface during an open window must fail'
fi
grep -Fq '.IMPLEMENTAUDIT/runs/window/live/declared.txt' "$tmp/f19.out" \
  || fail 'R2-F19 output missing deleted run-root path'
ok

# R2-F20: a failed complete enumeration is a checker failure, never a quiet
# disjoint verdict. `/dev/null` is not a valid Git index, while rev-parse can
# still resolve the commit identity.
new_repo f20-enumerator-failure
write_intent "$case_repo" open
case_now="$(git -C "$case_repo" rev-parse HEAD)"
if (cd "$case_repo" && GIT_INDEX_FILE=/dev/null bash "$checker" --window "$case_intent" --now "$case_now") >"$tmp/f20.out" 2>&1; then
  fail 'R2-F20 failed window enumeration must fail the checker'
fi
grep -Fq 'complete window changed-files enumeration failed' "$tmp/f20.out" \
  || fail 'R2-F20 output missing enumeration failure'
ok

# R2-F21: even at the closing HEAD, a closing receipt cannot be altered after
# its digest was bound into the launch intent.
new_repo f21-altered-closing-receipt
write_intent "$case_repo" open
touch "$case_repo/.IMPLEMENTAUDIT/runs/window/background/chain-a/chain.done"
write_intent "$case_repo" closed
printf 'tampered\0' >> "$case_repo/.IMPLEMENTAUDIT/runs/window/background/chain-a/closing-identities.nul"
case_now="$(git -C "$case_repo" rev-parse HEAD)"
if (cd "$case_repo" && bash "$checker" --window "$case_intent" --now "$case_now") >"$tmp/f21.out" 2>&1; then
  fail 'R2-F21 altered closing identity receipt must fail'
fi
grep -Fq 'closing identity receipt digest does not match' "$tmp/f21.out" \
  || fail 'R2-F21 output missing closing receipt integrity failure'
ok

# R2-F22: an ignored identity that existed at opening and remains byte-for-byte
# unchanged through an equal-SHA close is not a mutation.
new_repo f22-equal-unchanged-ignored
printf 'ignored/**\n' > "$case_repo/.gitignore"
git -C "$case_repo" add .gitignore
git -C "$case_repo" commit -qm ignore-unchanged
mkdir -p "$case_repo/ignored"
printf 'unchanged\n' > "$case_repo/ignored/declared.txt"
case_opened="$(git -C "$case_repo" rev-parse HEAD)"
write_intent "$case_repo" open 'ignored/declared.txt'
touch "$case_repo/.IMPLEMENTAUDIT/runs/window/background/chain-a/chain.done"
write_intent "$case_repo" closed 'ignored/declared.txt'
case_now="$(git -C "$case_repo" rev-parse HEAD)"
(cd "$case_repo" && bash "$checker" --window "$case_intent" --now "$case_now") >"$tmp/f22.out" 2>&1 \
  || fail 'R2-F22 unchanged ignored identity at equal-SHA close must pass'
ok

# R2-F23/R2-F24: pre-existing ignored content must stale both equal-SHA and
# historical closing windows when its bytes change during the window.
new_repo f23-equal-mutated-ignored
printf 'ignored/**\n' > "$case_repo/.gitignore"
git -C "$case_repo" add .gitignore
git -C "$case_repo" commit -qm ignore-mutated-equal
mkdir -p "$case_repo/ignored"
printf 'before\n' > "$case_repo/ignored/declared.txt"
case_opened="$(git -C "$case_repo" rev-parse HEAD)"
write_intent "$case_repo" open 'ignored/declared.txt'
printf 'after\n' > "$case_repo/ignored/declared.txt"
touch "$case_repo/.IMPLEMENTAUDIT/runs/window/background/chain-a/chain.done"
write_intent "$case_repo" closed 'ignored/declared.txt'
case_now="$(git -C "$case_repo" rev-parse HEAD)"
if (cd "$case_repo" && bash "$checker" --window "$case_intent" --now "$case_now") >"$tmp/f23.out" 2>&1; then
  fail 'R2-F23 in-place ignored mutation at equal-SHA close must fail'
fi
ok

new_repo f24-historical-mutated-ignored
printf 'ignored/**\n' > "$case_repo/.gitignore"
git -C "$case_repo" add .gitignore
git -C "$case_repo" commit -qm ignore-mutated-historical
mkdir -p "$case_repo/ignored"
printf 'before\n' > "$case_repo/ignored/declared.txt"
case_opened="$(git -C "$case_repo" rev-parse HEAD)"
write_intent "$case_repo" open 'ignored/declared.txt'
printf 'after\n' > "$case_repo/ignored/declared.txt"
printf 'closing anchor\n' > "$case_repo/docs/readme.md"
git -C "$case_repo" add docs/readme.md
git -C "$case_repo" commit -qm historical-close
touch "$case_repo/.IMPLEMENTAUDIT/runs/window/background/chain-a/chain.done"
write_intent "$case_repo" closed 'ignored/declared.txt'
printf 'later ordinary work\n' > "$case_repo/scratch/later.txt"
git -C "$case_repo" add scratch/later.txt
git -C "$case_repo" commit -qm post-close
case_now="$(git -C "$case_repo" rev-parse HEAD)"
if (cd "$case_repo" && bash "$checker" --window "$case_intent" --now "$case_now") >"$tmp/f24.out" 2>&1; then
  fail 'R2-F24 in-place ignored mutation at historical close must fail'
fi
ok

# R2-F25/R2-F26/R2-F27 repeat the unchanged and in-place controls for a
# declared run-root identity.
new_repo f25-equal-unchanged-run-root
mkdir -p "$case_repo/.IMPLEMENTAUDIT/runs/window/live"
printf 'unchanged\n' > "$case_repo/.IMPLEMENTAUDIT/runs/window/live/declared.txt"
write_intent "$case_repo" open '.IMPLEMENTAUDIT/runs/window/live/declared.txt'
touch "$case_repo/.IMPLEMENTAUDIT/runs/window/background/chain-a/chain.done"
write_intent "$case_repo" closed '.IMPLEMENTAUDIT/runs/window/live/declared.txt'
case_now="$(git -C "$case_repo" rev-parse HEAD)"
(cd "$case_repo" && bash "$checker" --window "$case_intent" --now "$case_now") >"$tmp/f25.out" 2>&1 \
  || fail 'R2-F25 unchanged run-root identity at equal-SHA close must pass'
ok

new_repo f26-equal-mutated-run-root
mkdir -p "$case_repo/.IMPLEMENTAUDIT/runs/window/live"
printf 'before\n' > "$case_repo/.IMPLEMENTAUDIT/runs/window/live/declared.txt"
write_intent "$case_repo" open '.IMPLEMENTAUDIT/runs/window/live/declared.txt'
printf 'after\n' > "$case_repo/.IMPLEMENTAUDIT/runs/window/live/declared.txt"
touch "$case_repo/.IMPLEMENTAUDIT/runs/window/background/chain-a/chain.done"
write_intent "$case_repo" closed '.IMPLEMENTAUDIT/runs/window/live/declared.txt'
case_now="$(git -C "$case_repo" rev-parse HEAD)"
if (cd "$case_repo" && bash "$checker" --window "$case_intent" --now "$case_now") >"$tmp/f26.out" 2>&1; then
  fail 'R2-F26 in-place run-root mutation at equal-SHA close must fail'
fi
ok

new_repo f27-historical-mutated-run-root
mkdir -p "$case_repo/.IMPLEMENTAUDIT/runs/window/live"
printf 'before\n' > "$case_repo/.IMPLEMENTAUDIT/runs/window/live/declared.txt"
write_intent "$case_repo" open '.IMPLEMENTAUDIT/runs/window/live/declared.txt'
printf 'after\n' > "$case_repo/.IMPLEMENTAUDIT/runs/window/live/declared.txt"
printf 'closing anchor\n' > "$case_repo/docs/readme.md"
git -C "$case_repo" add docs/readme.md
git -C "$case_repo" commit -qm historical-close
touch "$case_repo/.IMPLEMENTAUDIT/runs/window/background/chain-a/chain.done"
write_intent "$case_repo" closed '.IMPLEMENTAUDIT/runs/window/live/declared.txt'
printf 'later ordinary work\n' > "$case_repo/scratch/later.txt"
git -C "$case_repo" add scratch/later.txt
git -C "$case_repo" commit -qm post-close
case_now="$(git -C "$case_repo" rev-parse HEAD)"
if (cd "$case_repo" && bash "$checker" --window "$case_intent" --now "$case_now") >"$tmp/f27.out" 2>&1; then
  fail 'R2-F27 in-place run-root mutation at historical close must fail'
fi
ok

# R2-F28/R2-F29/R2-F30: declared empty ignored directories retain their own
# identity. Existing empty directories pass, while creation and deletion fail.
new_repo f28-unchanged-empty-ignored-directory
printf 'ignored/**\n' > "$case_repo/.gitignore"
git -C "$case_repo" add .gitignore
git -C "$case_repo" commit -qm ignore-empty-directory
mkdir -p "$case_repo/ignored/empty"
case_opened="$(git -C "$case_repo" rev-parse HEAD)"
write_intent "$case_repo" open 'ignored/empty/'
touch "$case_repo/.IMPLEMENTAUDIT/runs/window/background/chain-a/chain.done"
write_intent "$case_repo" closed 'ignored/empty/'
case_now="$(git -C "$case_repo" rev-parse HEAD)"
(cd "$case_repo" && bash "$checker" --window "$case_intent" --now "$case_now") >"$tmp/f28.out" 2>&1 \
  || fail 'R2-F28 unchanged empty ignored directory must pass'
ok

new_repo f29-created-empty-ignored-directory
printf 'ignored/**\n' > "$case_repo/.gitignore"
git -C "$case_repo" add .gitignore
git -C "$case_repo" commit -qm ignore-empty-directory
case_opened="$(git -C "$case_repo" rev-parse HEAD)"
write_intent "$case_repo" open 'ignored/empty/'
mkdir -p "$case_repo/ignored/empty"
touch "$case_repo/.IMPLEMENTAUDIT/runs/window/background/chain-a/chain.done"
write_intent "$case_repo" closed 'ignored/empty/'
case_now="$(git -C "$case_repo" rev-parse HEAD)"
if (cd "$case_repo" && bash "$checker" --window "$case_intent" --now "$case_now") >"$tmp/f29.out" 2>&1; then
  fail 'R2-F29 created empty ignored directory must fail'
fi
ok

new_repo f30-deleted-empty-ignored-directory
printf 'ignored/**\n' > "$case_repo/.gitignore"
git -C "$case_repo" add .gitignore
git -C "$case_repo" commit -qm ignore-empty-directory
mkdir -p "$case_repo/ignored/empty"
case_opened="$(git -C "$case_repo" rev-parse HEAD)"
write_intent "$case_repo" open 'ignored/empty/'
rmdir "$case_repo/ignored/empty"
case_now="$(git -C "$case_repo" rev-parse HEAD)"
if (cd "$case_repo" && bash "$checker" --window "$case_intent" --now "$case_now") >"$tmp/f30.out" 2>&1; then
  fail 'R2-F30 deleted empty ignored directory must fail'
fi
ok

# R2-F31/R2-F32/R2-F33 repeat the empty-directory controls for an explicit
# run-root surface that Git does not otherwise enumerate.
new_repo f31-unchanged-empty-run-root-directory
mkdir -p "$case_repo/.IMPLEMENTAUDIT/runs/window/live/empty"
write_intent "$case_repo" open '.IMPLEMENTAUDIT/runs/window/live/empty/'
touch "$case_repo/.IMPLEMENTAUDIT/runs/window/background/chain-a/chain.done"
write_intent "$case_repo" closed '.IMPLEMENTAUDIT/runs/window/live/empty/'
case_now="$(git -C "$case_repo" rev-parse HEAD)"
(cd "$case_repo" && bash "$checker" --window "$case_intent" --now "$case_now") >"$tmp/f31.out" 2>&1 \
  || fail 'R2-F31 unchanged empty run-root directory must pass'
ok

new_repo f32-created-empty-run-root-directory
write_intent "$case_repo" open '.IMPLEMENTAUDIT/runs/window/live/empty/'
mkdir -p "$case_repo/.IMPLEMENTAUDIT/runs/window/live/empty"
touch "$case_repo/.IMPLEMENTAUDIT/runs/window/background/chain-a/chain.done"
write_intent "$case_repo" closed '.IMPLEMENTAUDIT/runs/window/live/empty/'
case_now="$(git -C "$case_repo" rev-parse HEAD)"
if (cd "$case_repo" && bash "$checker" --window "$case_intent" --now "$case_now") >"$tmp/f32.out" 2>&1; then
  fail 'R2-F32 created empty run-root directory must fail'
fi
ok

new_repo f33-deleted-empty-run-root-directory
mkdir -p "$case_repo/.IMPLEMENTAUDIT/runs/window/live/empty"
write_intent "$case_repo" open '.IMPLEMENTAUDIT/runs/window/live/empty/'
rmdir "$case_repo/.IMPLEMENTAUDIT/runs/window/live/empty"
case_now="$(git -C "$case_repo" rev-parse HEAD)"
if (cd "$case_repo" && bash "$checker" --window "$case_intent" --now "$case_now") >"$tmp/f33.out" 2>&1; then
  fail 'R2-F33 deleted empty run-root directory must fail'
fi
ok

# R2-F34: receipt creation requires the declared surface population, rather
# than allowing an unbound record set with zero --surface inputs.
new_repo f34-empty-surface-population
if (cd "$case_repo" && bash "$repo_state" window-identities --records) >"$tmp/f34.out" 2>&1; then
  fail 'R2-F34 window identity receipt without declared surfaces must fail'
fi
grep -Fq 'requires at least one declared surface' "$tmp/f34.out" \
  || fail 'R2-F34 output missing declared-surface requirement'
ok

# R2-F35: a digest-rebound opening receipt that omits an existing empty ignored
# directory declaration cannot buy an open-window pass.
new_repo f35-omitted-opening-empty-ignored-directory
printf 'ignored/**\n' > "$case_repo/.gitignore"
git -C "$case_repo" add .gitignore
git -C "$case_repo" commit -qm ignore-empty-directory
mkdir -p "$case_repo/ignored/empty"
case_opened="$(git -C "$case_repo" rev-parse HEAD)"
write_intent "$case_repo" open 'ignored/empty/'
opening_receipt="$case_repo/.IMPLEMENTAUDIT/runs/window/background/chain-a/opening-identities.nul"
(cd "$case_repo" && bash "$repo_state" window-identities --records --surface 'docs/' > "$opening_receipt")
opening_digest="$(sha256sum "$opening_receipt" | awk '{print $1}')"
sed -i "s/^    opening_identity_sha256: .*/    opening_identity_sha256: $opening_digest/" "$case_intent"
case_now="$(git -C "$case_repo" rev-parse HEAD)"
if (cd "$case_repo" && bash "$checker" --window "$case_intent" --now "$case_now") >"$tmp/f35.out" 2>&1; then
  fail 'R2-F35 omitted opening empty ignored declaration must fail'
fi
grep -Fq 'declared surfaces do not match' "$tmp/f35.out" \
  || fail 'R2-F35 output missing opening surface-binding failure'
ok

# R2-F36: the same declaration-binding check applies to the closing receipt of
# an unchanged empty run-root directory.
new_repo f36-omitted-closing-empty-run-root-directory
mkdir -p "$case_repo/.IMPLEMENTAUDIT/runs/window/live/empty"
write_intent "$case_repo" open '.IMPLEMENTAUDIT/runs/window/live/empty/'
touch "$case_repo/.IMPLEMENTAUDIT/runs/window/background/chain-a/chain.done"
write_intent "$case_repo" closed '.IMPLEMENTAUDIT/runs/window/live/empty/'
closing_receipt="$case_repo/.IMPLEMENTAUDIT/runs/window/background/chain-a/closing-identities.nul"
(cd "$case_repo" && bash "$repo_state" window-identities --records --surface 'docs/' > "$closing_receipt")
closing_digest="$(sha256sum "$closing_receipt" | awk '{print $1}')"
sed -i "s/^    closing_identity_sha256: .*/    closing_identity_sha256: $closing_digest/" "$case_intent"
case_now="$(git -C "$case_repo" rev-parse HEAD)"
if (cd "$case_repo" && bash "$checker" --window "$case_intent" --now "$case_now") >"$tmp/f36.out" 2>&1; then
  fail 'R2-F36 omitted closing empty run-root declaration must fail'
fi
grep -Fq 'declared surfaces do not match' "$tmp/f36.out" \
  || fail 'R2-F36 output missing closing surface-binding failure'
ok

# R2-F37: equivalent repo-relative spellings are normalized before receipt
# binding and intersection. A leading ./ must not hide an ignored mutation.
new_repo f37-normalized-relative-surface
printf 'ignored/**\n' > "$case_repo/.gitignore"
mkdir -p "$case_repo/ignored"
printf 'before\n' > "$case_repo/ignored/declared.txt"
git -C "$case_repo" add .gitignore
git -C "$case_repo" commit -qm normalize-declared-surface
write_intent "$case_repo" open './ignored/declared.txt'
printf 'after\n' > "$case_repo/ignored/declared.txt"
case_now="$(git -C "$case_repo" rev-parse HEAD)"
if (cd "$case_repo" && bash "$checker" --window "$case_intent" --now "$case_now") >"$tmp/f37.out" 2>&1; then
  fail 'R2-F37 leading-dot declared surface mutation must fail'
fi
grep -Fq 'ignored/declared.txt' "$tmp/f37.out" \
  || fail 'R2-F37 output missing normalized intersecting path'
ok

# R2-F38--F41: a governed mutation must present its complete planned repo-path
# population to the existing verification-window authority. Open intersections
# fail before mutation; disjoint and already-closed windows remain cheap.
new_repo f38-planned-intersection
write_intent "$case_repo" open 'curriculum/**'
case_now="$(git -C "$case_repo" rev-parse HEAD)"
if (cd "$case_repo" && IMPLEMENTAUDIT_WINDOW_PLANNED_PATHS_JSON='["curriculum/x.json"]' \
    bash "$checker" --window "$case_intent" --now "$case_now" --planned-paths-env) >"$tmp/f38.out" 2>&1; then
  fail 'R2-F38 planned intersection with an open window must fail'
fi
grep -Fq 'curriculum/x.json' "$tmp/f38.out" \
  || fail 'R2-F38 output missing planned intersecting path'
ok

new_repo f39-planned-disjoint
write_intent "$case_repo" open 'curriculum/**'
case_now="$(git -C "$case_repo" rev-parse HEAD)"
(cd "$case_repo" && IMPLEMENTAUDIT_WINDOW_PLANNED_PATHS_JSON='["docs/readme.md"]' \
  bash "$checker" --window "$case_intent" --now "$case_now" --planned-paths-env) >"$tmp/f39.out" 2>&1 \
  || fail 'R2-F39 planned path disjoint from an open window must pass'
ok

new_repo f40-planned-after-close
write_intent "$case_repo" open 'curriculum/**'
touch "$case_repo/.IMPLEMENTAUDIT/runs/window/background/chain-a/chain.done"
write_intent "$case_repo" closed 'curriculum/**'
case_now="$(git -C "$case_repo" rev-parse HEAD)"
(cd "$case_repo" && IMPLEMENTAUDIT_WINDOW_PLANNED_PATHS_JSON='["curriculum/x.json"]' \
  bash "$checker" --window "$case_intent" --now "$case_now" --planned-paths-env) >"$tmp/f40.out" 2>&1 \
  || fail 'R2-F40 planned path after verified closure must pass'
ok

new_repo f41-malformed-planned-population
write_intent "$case_repo" open 'curriculum/**'
case_now="$(git -C "$case_repo" rev-parse HEAD)"
if (cd "$case_repo" && IMPLEMENTAUDIT_WINDOW_PLANNED_PATHS_JSON='{"path":"curriculum/x.json"}' \
    bash "$checker" --window "$case_intent" --now "$case_now" --planned-paths-env) >"$tmp/f41.out" 2>&1; then
  fail 'R2-F41 malformed planned path population must fail closed'
fi
grep -Fq 'planned path population' "$tmp/f41.out" \
  || fail 'R2-F41 output missing malformed population diagnostic'
ok

# R2-F42--F46: only the governed transition route may publish open/closed
# state. It binds exact identities while holding the same persistent gate R36
# uses, and refuses premature closure, selector drift, and wrong custody.
new_repo f42-transition-open
transition_run_rel="$(cd "$case_repo" && IMPLEMENTAUDIT_BASE=.IMPLEMENTAUDIT/runs bash "$repo_root/skills/implementaudit/scripts/claim-run.sh" window 2>/dev/null)"
write_prepared_intent "$case_repo" "$case_repo/$transition_run_rel"
(cd "$case_repo" && bash "$checker" --window-transition open "$case_intent" --entry 1 --repo-root "$case_repo") >"$tmp/f42.out" 2>&1 \
  || { cat "$tmp/f42.out" >&2; fail 'R2-F42 governed open transition failed'; }
grep -Fq 'state: open' "$case_intent" || fail 'R2-F42 did not publish open state'
grep -Eq '^    opening_identity_sha256: [0-9a-f]{64}$' "$case_intent" \
  || fail 'R2-F42 did not bind opening identity digest'
case_now="$(git -C "$case_repo" rev-parse HEAD)"
(cd "$case_repo" && bash "$checker" --window "$case_intent" --now "$case_now") >/dev/null \
  || fail 'R2-F42 published window does not validate'
ok

new_repo f43-transition-premature-close
transition_run_rel="$(cd "$case_repo" && IMPLEMENTAUDIT_BASE=.IMPLEMENTAUDIT/runs bash "$repo_root/skills/implementaudit/scripts/claim-run.sh" window 2>/dev/null)"
write_prepared_intent "$case_repo" "$case_repo/$transition_run_rel"
(cd "$case_repo" && bash "$checker" --window-transition open "$case_intent" --entry 1 --repo-root "$case_repo") >/dev/null
if (cd "$case_repo" && bash "$checker" --window-transition close "$case_intent" --entry 1 --repo-root "$case_repo") >"$tmp/f43.out" 2>&1; then
  fail 'R2-F43 close transition without chain.done must fail'
fi
grep -Fq 'state: open' "$case_intent" || fail 'R2-F43 premature close altered open state'
ok

new_repo f44-transition-close
transition_run_rel="$(cd "$case_repo" && IMPLEMENTAUDIT_BASE=.IMPLEMENTAUDIT/runs bash "$repo_root/skills/implementaudit/scripts/claim-run.sh" window 2>/dev/null)"
write_prepared_intent "$case_repo" "$case_repo/$transition_run_rel"
(cd "$case_repo" && bash "$checker" --window-transition open "$case_intent" --entry 1 --repo-root "$case_repo") >/dev/null
touch "$(dirname "$case_intent")/chain.done"
(cd "$case_repo" && bash "$checker" --window-transition close "$case_intent" --entry 1 --repo-root "$case_repo") >"$tmp/f44.out" 2>&1 \
  || fail 'R2-F44 governed close transition failed'
grep -Fq 'state: closed' "$case_intent" || fail 'R2-F44 did not publish closed state'
grep -Eq '^    closing_identity_sha256: [0-9a-f]{64}$' "$case_intent" \
  || fail 'R2-F44 did not bind closing identity digest'
ok

new_repo f45-transition-entry
transition_run_rel="$(cd "$case_repo" && IMPLEMENTAUDIT_BASE=.IMPLEMENTAUDIT/runs bash "$repo_root/skills/implementaudit/scripts/claim-run.sh" window 2>/dev/null)"
write_prepared_intent "$case_repo" "$case_repo/$transition_run_rel"
if (cd "$case_repo" && bash "$checker" --window-transition open "$case_intent" --entry 2 --repo-root "$case_repo") >/dev/null 2>&1; then
  fail 'R2-F45 absent verification-window entry selector accepted'
fi
grep -Fq 'state: prepared' "$case_intent" || fail 'R2-F45 wrong selector altered intent'
ok

new_repo f46-transition-custody
transition_run_rel="$(cd "$case_repo" && IMPLEMENTAUDIT_BASE=.IMPLEMENTAUDIT/runs bash "$repo_root/skills/implementaudit/scripts/claim-run.sh" window 2>/dev/null)"
write_prepared_intent "$case_repo" "$case_repo/$transition_run_rel"
cp "$case_intent" "$case_repo/outside-intent.md"
if (cd "$case_repo" && bash "$checker" --window-transition open "$case_repo/outside-intent.md" --entry 1 --repo-root "$case_repo") >/dev/null 2>&1; then
  fail 'R2-F46 launch intent outside governed run topology accepted'
fi
grep -Fq 'state: prepared' "$case_repo/outside-intent.md" || fail 'R2-F46 wrong-custody intent altered'
ok

# R2-F47: identity receipts contain the complete declared-surface population,
# not unrelated tracked, ignored, or run-root paths. This is both the evidence
# ceiling and the condition that lets a governed transition capture identities
# while holding the namespace gate on Windows.
new_repo f47-declared-surface-only
mkdir -p "$case_repo/curriculum" "$case_repo/docs" "$case_repo/.IMPLEMENTAUDIT/private"
printf 'declared\n' > "$case_repo/curriculum/declared.txt"
printf 'unrelated tracked\n' > "$case_repo/docs/unrelated.txt"
printf 'unrelated ignored\n' > "$case_repo/.IMPLEMENTAUDIT/private/unrelated.txt"
git -C "$case_repo" add curriculum/declared.txt docs/unrelated.txt
git -C "$case_repo" commit -qm 'add receipt population'
(cd "$case_repo" && bash "$repo_state" window-identities --records --surface 'curriculum/**') > "$tmp/f47.receipt" \
  || fail 'R2-F47 declared-surface receipt failed'
python - "$tmp/f47.receipt" <<'PY' || fail 'R2-F47 receipt population was not bounded to declared surfaces'
import json
import pathlib
import sys

parts = [part for part in pathlib.Path(sys.argv[1]).read_bytes().split(b"\0") if part]
rows = [json.loads(part) for part in parts]
expected_header = {"schema": "verification-window-identity-receipt-v1", "surfaces": ["curriculum/**"]}
assert rows[0] == expected_header, f"header={rows[0]!r}"
paths = [row["path"] for row in rows[1:]]
assert paths == ["curriculum/declared.txt", "curriculum/x.json"], f"paths={paths!r}"
PY
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
grep -Fq 'Window intersection uses complete path identities, including ignored' "$protocol" \
  || fail 'verification-window complete identity route missing'
grep -Fq 'and .IMPLEMENTAUDIT/ run-root paths, when they are declared surfaces' "$protocol" \
  || fail 'verification-window complete identity route missing'
grep -Fq 'normalized complete declared-surface population, including explicitly absent paths and directories' "$protocol" \
  || fail 'verification-window receipt surface binding contract missing'
ok
grep -Fq 'opening_identity_receipt' "$protocol" \
  || fail 'verification-window opening identity receipt contract missing'
grep -Fq 'closing_identity_receipt' "$protocol" \
  || fail 'verification-window closing identity receipt contract missing'
ok
grep -Fq 'path, type, extent, and SHA-256 digest' "$protocol" \
  || fail 'verification-window content identity receipt contract missing'
ok
grep -Fq 'Declared trailing-slash directory surfaces are explicitly included' "$protocol" \
  || fail 'verification-window empty directory identity contract missing'
ok
grep -Fq 'verification is reading the same tree' "$phase_design" || fail 'phase-design verification boundary missing'
grep -Fq 'post-state was compared' "$lean" || fail 'Lean post-state evidence boundary missing'
ok; ok; ok; ok; ok

printf 'verification-window-contract.test: ok (%d/59)\n' "$count"
