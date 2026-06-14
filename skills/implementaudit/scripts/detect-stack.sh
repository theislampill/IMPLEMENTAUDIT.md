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
check SKILL.md
check AGENTS.md
check README.md
check CHANGELOG.md
check CONTRIBUTING.md

printf '\ngenerated-or-derived-surfaces:\n'
check docs/diagrams
check docs/audits
check dist
check .IMPLEMENTAUDIT
check .IMPLEMENTAUDIT/runs

printf '\nvalidators-and-tests:\n'
find scripts skills/scripts tests -maxdepth 2 -type f 2>/dev/null | sort | sed -n '1,120p' || true

printf '\nfixtures:\n'
find fixtures -maxdepth 3 -type f 2>/dev/null | sort | sed -n '1,120p' || true

printf '\npackage-scripts:\n'
if [ -f package.json ]; then
  node -pe "JSON.stringify(require('./package.json').scripts||{},null,2)" 2>/dev/null \
    | sed -n '1,30p' || true
  printf 'package-name: '
  node -pe "require('./package.json').name||'(unnamed)'" 2>/dev/null || true
  printf 'package-version: '
  node -pe "require('./package.json').version||'(none)'" 2>/dev/null || true
fi

printf '\npython-hints:\n'
if [ -f pyproject.toml ]; then
  grep -E '^\[project\]|^name\s*=|^version\s*=|^\[build-system\]|requires\s*=' pyproject.toml 2>/dev/null | head -10 || true
fi
if [ -f requirements.txt ]; then
  printf 'requirements.txt: '
  wc -l < requirements.txt 2>/dev/null || true
  head -5 requirements.txt 2>/dev/null || true
fi

printf '\nlanguage-and-framework-hints:\n'
# Detect primary languages by extension count in tracked files
for ext in ts tsx js jsx py rs go java kt rb cs; do
  cnt=$(git ls-files 2>/dev/null | grep -c "\.$ext$" || true)
  if [ "$cnt" -gt 0 ]; then printf '%s: %d files\n' "$ext" "$cnt"; fi
done
# Framework hints
check src/app.tsx
check src/main.ts
check src/index.ts
check app.py
check main.go
check src/lib.rs
check next.config.js
check next.config.ts
check vite.config.ts
check astro.config.mjs

printf '\nsource-and-test-layout:\n'
for dir in src lib app pages components api routes tests test spec __tests__; do
  if [ -d "$dir" ]; then printf 'dir: %s (%d files)\n' "$dir" "$(find "$dir" -type f 2>/dev/null | wc -l)"; fi
done

printf '\nconfig-and-infra:\n'
check .env.example
check .env.test
check tsconfig.json
check jest.config.ts
check jest.config.js
check vitest.config.ts
check .eslintrc.json
check .eslintrc.js
check biome.json
check lefthook.yml
check .pre-commit-config.yaml
check helm
check k8s
check terraform
check ansible

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

printf '\nruntime-run-artifacts:\n'
if [ -d .IMPLEMENTAUDIT/runs ]; then
  find .IMPLEMENTAUDIT/runs -maxdepth 2 -type f 2>/dev/null | sort | sed -n '1,120p'
else
  printf 'none\n'
fi
for path in .IMPLEMENTAUDIT/ROADMAP.md .IMPLEMENTAUDIT/STATE.md .IMPLEMENTAUDIT/THINKING.md .IMPLEMENTAUDIT/PROTOCOL.md; do
  if [ -e "$path" ]; then printf 'legacy-flat: %s\n' "$path"; fi
done
