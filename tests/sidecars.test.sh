#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

bash scripts/check-sidecar-boundaries.sh

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

cp -R skills README.md AGENTS.md scripts tests "$tmp/"
mkdir -p "$tmp/scripts"
cp scripts/check-sidecar-boundaries.sh "$tmp/scripts/check-sidecar-boundaries.sh"

perl -0pi -e 's/Graphify output is orientation evidence, not proof/Graphify output proves correctness/g' "$tmp/skills/SKILL.md"
if (cd "$tmp" && bash scripts/check-sidecar-boundaries.sh >/dev/null 2>&1); then
  printf 'sidecars.test: expected missing Graphify boundary to fail\n' >&2
  exit 1
fi

printf 'sidecars.test: ok\n'
