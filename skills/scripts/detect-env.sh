#!/usr/bin/env bash
set -euo pipefail

printf 'implementaudit.detect-env\n'
printf 'pwd=%s\n' "$(pwd)"
printf 'os=%s\n' "$(uname -s 2>/dev/null || printf unknown)"
printf 'shell=%s\n' "${SHELL:-unknown}"
printf 'side_effects=none\n'

if command -v git >/dev/null 2>&1; then
  printf 'git=%s\n' "$(git --version)"
  if git rev-parse --show-toplevel >/dev/null 2>&1; then
    printf 'git_root=%s\n' "$(git rev-parse --show-toplevel)"
    git status --short --branch
  else
    printf 'git_root=none\n'
  fi
else
  printf 'git=absent\n'
fi

for cmd in python python3 node npm pnpm yarn uv bash grep rg gh zip unzip; do
  if command -v "$cmd" >/dev/null 2>&1; then
    printf '%s=%s\n' "$cmd" "$(command -v "$cmd")"
  else
    printf '%s=absent\n' "$cmd"
  fi
done

for cmd in graphify activegraph; do
  if command -v "$cmd" >/dev/null 2>&1; then
    printf '%s=%s\n' "$cmd" "$(command -v "$cmd")"
  else
    printf '%s=absent_optional\n' "$cmd"
  fi
done
