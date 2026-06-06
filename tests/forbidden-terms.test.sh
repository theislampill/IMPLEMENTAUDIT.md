#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

sentinel="FORBIDDEN_EXTERNAL_SENTINEL"

mkdir -p "$tmp/clean"
printf 'ordinary IMPLEMENTAUDIT fixture text\n' >"$tmp/clean/ok.txt"
bash scripts/check-forbidden-terms.sh --root "$tmp/clean" --term "$sentinel"

mkdir -p "$tmp/direct"
printf '%s\n' "$sentinel" >"$tmp/direct/hit.txt"
if bash scripts/check-forbidden-terms.sh --root "$tmp/direct" --term "$sentinel" >/dev/null 2>&1; then
  printf 'forbidden-terms.test: expected direct sentinel match to fail\n' >&2
  exit 1
fi

mkdir -p "$tmp/assembled"
printf 'token = "FORBIDDEN_EXTERNAL_" + "SENTINEL"\n' >"$tmp/assembled/hit.py"
if bash scripts/check-forbidden-terms.sh --root "$tmp/assembled" --term "$sentinel" >/dev/null 2>&1; then
  printf 'forbidden-terms.test: expected assembled sentinel match to fail\n' >&2
  exit 1
fi

mkdir -p "$tmp/encoded"
printf 'Rk9SQklEREVOX0VYVEVSTkFMX1NFTlRJTkVM\n' >"$tmp/encoded/hit.txt"
if bash scripts/check-forbidden-terms.sh --root "$tmp/encoded" --term "$sentinel" >/dev/null 2>&1; then
  printf 'forbidden-terms.test: expected encoded sentinel match to fail\n' >&2
  exit 1
fi

terms_file="$tmp/terms.txt"
printf '%s\n' "$sentinel" >"$terms_file"
if bash scripts/check-forbidden-terms.sh --root "$tmp/direct" --terms-file "$terms_file" >/dev/null 2>&1; then
  printf 'forbidden-terms.test: expected terms-file sentinel match to fail\n' >&2
  exit 1
fi

if IMPLEMENTAUDIT_FORBIDDEN_TERMS="$sentinel" bash scripts/check-forbidden-terms.sh --root "$tmp/direct" >/dev/null 2>&1; then
  printf 'forbidden-terms.test: expected env sentinel match to fail\n' >&2
  exit 1
fi

bash scripts/check-forbidden-terms.sh --root "$tmp/clean" --allow-empty

printf 'forbidden-terms.test: ok\n'
