#!/usr/bin/env bash
set -euo pipefail

printf 'implementaudit.detect-stack\n'

check() {
  if [ -e "$1" ]; then
    printf 'present: %s\n' "$1"
  fi
}

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

if [ -d .github/workflows ]; then
  find .github/workflows -maxdepth 1 -type f -print | sort
fi

if [ -f AGENTS.md ]; then
  printf 'present: AGENTS.md\n'
fi
