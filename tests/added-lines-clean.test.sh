#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

mkdir -p "$tmp/repo/scripts" "$tmp/repo/skills/scripts"
cp scripts/check-added-lines-clean.sh "$tmp/repo/scripts/check-added-lines-clean.sh"
cp scripts/check-forbidden-terms.sh "$tmp/repo/scripts/check-forbidden-terms.sh"
cp skills/scripts/repo-state.sh "$tmp/repo/skills/scripts/repo-state.sh"

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

printf 'FORBIDDEN_EXTERNAL_SENTINEL\n' >identity.txt
if IMPLEMENTAUDIT_FORBIDDEN_TERMS="FORBIDDEN_EXTERNAL_SENTINEL" bash scripts/check-added-lines-clean.sh "$baseline" >/dev/null 2>&1; then
  printf 'added-lines-clean.test: expected externally supplied forbidden term to fail\n' >&2
  exit 1
fi
rm identity.txt

printf 'clean line\n' >clean.txt
bash scripts/check-added-lines-clean.sh "$baseline"

printf 'added-lines-clean.test: ok\n'
