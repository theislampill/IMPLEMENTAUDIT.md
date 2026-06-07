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

printf '\nhost-session:\n'
printf 'codex_home=%s\n' "${CODEX_HOME:-unset}"
printf 'claude_config_dir=%s\n' "${CLAUDE_CONFIG_DIR:-unset}"
printf 'implementaudit_base=%s\n' "${IMPLEMENTAUDIT_BASE:-.IMPLEMENTAUDIT/runs}"
printf 'implementaudit_run_root=%s\n' "${IMPLEMENTAUDIT_RUN_ROOT:-unset}"
printf 'implementaudit_baseline_ref=%s\n' "${IMPLEMENTAUDIT_BASELINE_REF:-unset}"

printf '\noptional-docs-and-web:\n'
for cmd in gh curl wget; do
  if command -v "$cmd" >/dev/null 2>&1; then
    printf '%s=%s\n' "$cmd" "$(command -v "$cmd")"
  else
    printf '%s=absent\n' "$cmd"
  fi
done
printf 'web_lookup_authorization=unknown_owner_decision\n'
printf 'current_docs_lookup_authorization=unknown_owner_decision\n'

printf '\nmemory-continuity:\n'
for cand in \
  "${CODEX_HOME:-$HOME/.codex}/memories" \
  "$HOME/.codex/memories" \
  "$HOME/.claude/memory" \
  "$PWD/.claude/memory" \
  "${IMPLEMENTAUDIT_RUN_ROOT:-.IMPLEMENTAUDIT/runs/unclaimed}/memory"
do
  if [ -d "$cand" ]; then
    printf 'present: %s\n' "$cand"
  else
    printf 'absent: %s\n' "$cand"
  fi
done

printf '\nrun-roots:\n'
if [ -d .IMPLEMENTAUDIT/runs ]; then
  find .IMPLEMENTAUDIT/runs -mindepth 1 -maxdepth 1 -type d 2>/dev/null | sort | sed -n '1,40p'
else
  printf 'none\n'
fi
if [ -f .IMPLEMENTAUDIT/STATE.md ] || [ -f .IMPLEMENTAUDIT/ROADMAP.md ]; then
  printf 'legacy_flat_state=present\n'
else
  printf 'legacy_flat_state=absent\n'
fi

for cmd in graphify activegraph; do
  if command -v "$cmd" >/dev/null 2>&1; then
    printf '%s=%s\n' "$cmd" "$(command -v "$cmd")"
  else
    printf '%s=absent_optional\n' "$cmd"
  fi
done

printf '\nsidecar-authorization:\n'
printf 'graphify_indexing=not_authorized_by_default\n'
printf 'activegraph_event_writing=not_authorized_by_default\n'
