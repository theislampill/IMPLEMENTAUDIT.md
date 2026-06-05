#!/usr/bin/env bash
set -euo pipefail

printf 'implementaudit.detect-stack\n'
printf 'side_effects=none\n'

check() {
  if [ -e "$1" ]; then
    printf 'present: %s\n' "$1"
  fi
}

printf '\npackage-and-build:\n'
check package.json
check pnpm-lock.yaml
check package-lock.json
check yarn.lock
check pyproject.toml
check requirements.txt
check uv.lock
check Cargo.toml
check go.mod
check Makefile
check justfile
check Dockerfile
check docker-compose.yml

printf '\ncanonical-sources:\n'
check skills/SKILL.md
check AGENTS.md
check README.md
check CHANGELOG.md
check CONTRIBUTING.md

printf '\ngenerated-or-derived-surfaces:\n'
check docs/diagrams
check docs/audits
check dist
check .IMPLEMENTAUDIT

printf '\nvalidators-and-tests:\n'
find scripts skills/scripts tests -maxdepth 2 -type f 2>/dev/null | sort | sed -n '1,120p' || true

printf '\nfixtures:\n'
find fixtures -maxdepth 3 -type f 2>/dev/null | sort | sed -n '1,120p' || true

printf '\nrelease-and-provenance-surfaces:\n'
check scripts/build-release-asset.sh
check scripts/write-release-checksums.sh
check .claude-plugin/plugin.json
check .claude-plugin/marketplace.json

if [ -d .github/workflows ]; then
  printf '\nci-workflows:\n'
  find .github/workflows -maxdepth 1 -type f -print | sort
fi

printf '\noptional-sidecar-roots:\n'
check graphify-out
check .graphify
check .activegraph
