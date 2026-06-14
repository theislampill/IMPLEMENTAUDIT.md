#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

mkdir -p "$tmp/repo/scripts" "$tmp/repo/skills/implementaudit/scripts"
cp scripts/check-added-lines-clean.sh "$tmp/repo/scripts/check-added-lines-clean.sh"
cp skills/implementaudit/scripts/repo-state.sh "$tmp/repo/skills/implementaudit/scripts/repo-state.sh"

cd "$tmp/repo"
git init -q
git config user.email test@example.invalid
git config user.name 'ImplementAudit Test'
printf 'base\n' >README.md
git add .
git commit -q -m baseline
baseline="$(git rev-parse HEAD)"

bash scripts/check-added-lines-clean.sh "$baseline"

printf 'console.log("debug")\n' >debug.js
if bash scripts/check-added-lines-clean.sh "$baseline" >/dev/null 2>&1; then
  printf 'added-lines-clean.test: expected debug print to fail\n' >&2
  exit 1
fi
rm debug.js

printf 'TODO: session marker\n' >todo.txt
if bash scripts/check-added-lines-clean.sh "$baseline" >/dev/null 2>&1; then
  printf 'added-lines-clean.test: expected TODO to fail\n' >&2
  exit 1
fi
rm todo.txt

cat >reconcile.md <<'OK'
Reconciliation statuses (DONE / BLOCKED / IN PROGRESS / TODO / STALE / DRIFTED / FIXED INDEPENDENTLY):
OK
bash scripts/check-added-lines-clean.sh "$baseline"
rm reconcile.md

printf 'clean line\n' >clean.txt
bash scripts/check-added-lines-clean.sh "$baseline"

printf 'added-lines-clean.test: ok\n'
