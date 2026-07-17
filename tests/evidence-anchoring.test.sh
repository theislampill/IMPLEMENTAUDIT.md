#!/usr/bin/env bash
set -euo pipefail

# Evidence-version anchoring (#4): detect-env anchor fields, full-SHA
# anchor format enforcement, and stale-artifact substitution refusal.

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

de="$repo_root/skills/implementaudit/scripts/detect-env.sh"
cea="$repo_root/skills/implementaudit/scripts/check-evidence-anchor.sh"
vrr="$repo_root/skills/implementaudit/scripts/validate-run-root.sh"

fail() { printf 'evidence-anchoring: %s\n' "$*" >&2; exit 1; }

# --- detect-env fixture pair: WITHOUT upstream ------------------------------
mkdir "$tmp/no-upstream" && cd "$tmp/no-upstream"
git init -q . && git -c user.email=t@t -c user.name=t commit -q --allow-empty -m x
out="$(bash "$de")"
printf '%s\n' "$out" | grep -qE '^head=[0-9a-f]+ \(' || fail "no head=<sha> (<date>) field"
printf '%s\n' "$out" | grep -q '^upstream=none$' || fail "expected upstream=none"
printf '%s\n' "$out" | grep -q '^remote_freshness=not_checked$' \
  || fail "missing remote_freshness=not_checked"

# --- detect-env fixture pair: WITH upstream (behind 0 / ahead 1) ------------
cd "$tmp"
git clone -q "$tmp/no-upstream" with-upstream
cd "$tmp/with-upstream"
git -c user.email=t@t -c user.name=t commit -q --allow-empty -m y
out2="$(bash "$de")"
printf '%s\n' "$out2" | grep -qE '^upstream=origin/[^ ]+ behind_ahead=0/1$' \
  || fail "expected upstream=origin/<branch> behind_ahead=0/1, got: $(printf '%s' "$out2" | grep '^upstream=')"
printf '%s\n' "$out2" | grep -q '^remote_freshness=not_checked$' \
  || fail "missing remote_freshness with upstream"

# read-only: detect-env must not have touched the work tree
[ -z "$(git status --short)" ] || fail "detect-env mutated the repo"

cd "$repo_root"

# --- anchor row format: full SHA passes, short SHA fails --------------------
full="0123456789abcdef0123456789abcdef01234567"
bash "$cea" --row "grep clean @$full" >/dev/null || fail "full-sha row rejected"
if bash "$cea" --row "grep clean @0123456f" >/dev/null 2>&1; then
  fail "short-sha anchor row was accepted"
fi
bash "$cea" --row "legacy row without anchor" >/dev/null \
  || fail "legacy unanchored row rejected (must stay valid)"

# --- artifact substitution refusal ------------------------------------------
other="fedcba9876543210fedcba9876543210fedcba98"
printf 'verdict: ok\nAnchor: %s\n' "$full" > "$tmp/verdict.md"
bash "$cea" --artifact "$tmp/verdict.md" --tree "$full" >/dev/null \
  || fail "matching-anchor artifact refused"
if bash "$cea" --artifact "$tmp/verdict.md" --tree "$other" >/dev/null 2>&1; then
  fail "artifact anchored to tree X was ACCEPTED for tree Y"
fi
printf 'verdict: ok, no anchor\n' > "$tmp/unanchored.md"
if bash "$cea" --artifact "$tmp/unanchored.md" --tree "$full" >/dev/null 2>&1; then
  fail "unanchored artifact was accepted as current-state evidence"
fi

# --- run-root validation: short-sha anchor in STATE.md fails ----------------
seed="$tmp/run-root"
mkdir -p "$seed/phases"
for f in ROADMAP.md THINKING.md PROTOCOL.md context.md tools.md sidecars.md; do
  printf 'x\n' > "$seed/$f"
done
cp "$repo_root/skills/implementaudit/templates/STATE.md" "$seed/STATE.md"
if bash "$vrr" "$seed" >/dev/null 2>&1; then
  base_ok=1
else
  base_ok=0  # template may fail other structural checks; we only need the delta
fi
printf '| 1 | f | 1 | a | open | grep @%s | - | - |\n' "$full" >> "$seed/STATE.md"
out3="$(bash "$vrr" "$seed" 2>&1 || true)"
printf '%s' "$out3" | grep -q 'anchor' && fail "full-sha anchor flagged by validator"
printf '| 2 | f | 1 | a | open | grep @0123456f | - | - |\n' >> "$seed/STATE.md"
out4="$(bash "$vrr" "$seed" 2>&1 || true)"
printf '%s' "$out4" | grep -q 'anchor' \
  || fail "short-sha anchor NOT flagged by validator"

printf 'evidence-anchoring: ok\n'
