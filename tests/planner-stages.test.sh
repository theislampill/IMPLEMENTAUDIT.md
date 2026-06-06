#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

bash scripts/check-planner-stages.sh

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

cp -R skills "$tmp/skills"
cp scripts/check-planner-stages.sh "$tmp/check-planner-stages.sh"

if ! grep -Fq "Stage 6.5 - Pre-flight smoke" "$tmp/skills/SKILL.md"; then
  printf 'planner-stages.test: fixture setup failed\n' >&2
  exit 1
fi

perl -0pi -e 's/Stage 6\.5 - Pre-flight smoke/Stage 6.5 - missing/' "$tmp/skills/SKILL.md"

(
  cd "$tmp"
  mkdir scripts
  mv check-planner-stages.sh scripts/check-planner-stages.sh
  if bash scripts/check-planner-stages.sh >/dev/null 2>&1; then
    printf 'planner-stages.test: expected missing Stage 6.5 check to fail\n' >&2
    exit 1
  fi
)

printf 'planner-stages.test: ok\n'
