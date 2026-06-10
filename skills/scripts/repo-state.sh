#!/usr/bin/env bash
# repo-state.sh - evaluate complete working-tree state relative to a baseline.
#
# This helper is read-only. It never mutates the working tree, index, config, or
# files. Use it when final audits, deliverable checks, or cleanliness scans need
# to see committed, staged, unstaged, deleted, and untracked work.

set -uo pipefail

in_git_repo() {
  git rev-parse --is-inside-work-tree >/dev/null 2>&1
}

baseline_ok() {
  local baseline="${1:-}"
  [ -n "$baseline" ] || return 1
  [ "$baseline" = "no-git" ] && return 1
  git rev-parse --verify --quiet "${baseline}^{commit}" >/dev/null 2>&1
}

cmd_deliverable() {
  local baseline="$1"
  local path="$2"

  if in_git_repo && baseline_ok "$baseline"; then
    local untracked
    untracked="$(git ls-files --others --exclude-standard -- "$path" 2>/dev/null | head -1 || true)"
    if [ -n "$untracked" ]; then
      printf 'present - untracked new file (%s)\n' "$untracked"
      return 0
    fi

    if [ -e "$path" ]; then
      local stat
      stat="$(git diff --stat "$baseline" -- "$path" 2>/dev/null || true)"
      if [ -n "$stat" ]; then
        printf 'present - changed vs baseline (%s)\n' \
          "$(printf '%s' "$stat" | tail -1 | sed 's/^[[:space:]]*//')"
      else
        printf 'present - exists, unchanged since baseline\n'
      fi
      return 0
    fi

    local deleted
    deleted="$(git ls-files --deleted -- "$path" 2>/dev/null | head -1 || true)"
    if [ -n "$deleted" ]; then
      printf 'missing - tracked file deleted since baseline (%s)\n' "$deleted"
      return 1
    fi

    local tracked
    tracked="$(git ls-files -- "$path" 2>/dev/null | head -1 || true)"
    if [ -n "$tracked" ]; then
      printf 'missing - tracked path not present on disk (%s)\n' "$tracked"
      return 1
    fi

    printf 'missing\n'
    return 1
  fi

  if [ -e "$path" ]; then
    printf 'present - exists on disk (baseline unavailable)\n'
    return 0
  fi
  if in_git_repo && [ -n "$(git ls-files -- "$path" 2>/dev/null | head -1 || true)" ]; then
    printf 'present - tracked (baseline unavailable)\n'
    return 0
  fi
  printf 'missing\n'
  return 1
}

# Run-root artifacts under .IMPLEMENTAUDIT/ are the audit substrate, not
# deliverables: in target repos that do not gitignore them they would
# contaminate cleanliness and deliverable evidence. They are excluded from the
# enumeration commands below, and the exclusion is reported (never silent).
# Explicit `deliverable <path>` queries are answered honestly for any path.
note_excluded() {
  if [ "$1" -gt 0 ]; then
    printf 'repo-state: excluded %d run-root path(s) under .IMPLEMENTAUDIT/ from evidence\n' "$1" >&2
  fi
}

cmd_changed_files() {
  local baseline="$1"
  if in_git_repo && baseline_ok "$baseline"; then
    local excluded=0 f
    while IFS= read -r f; do
      case "$f" in
        .IMPLEMENTAUDIT/*) excluded=$((excluded + 1)) ;;
        *) printf '%s\n' "$f" ;;
      esac
    done < <(
      {
        git diff --name-only "$baseline" 2>/dev/null || true
        git ls-files --others --exclude-standard 2>/dev/null || true
      } | LC_ALL=C sort -u | sed '/^$/d'
    )
    note_excluded "$excluded"
  fi
}

cmd_added_lines() {
  local baseline="$1"
  if in_git_repo && baseline_ok "$baseline"; then
    git diff "$baseline" -- . ':(exclude).IMPLEMENTAUDIT' 2>/dev/null | grep '^+' | grep -v '^+++' | sed 's/^+//' || true
    local excluded=0 file
    while IFS= read -r -d '' file; do
      case "$file" in
        .IMPLEMENTAUDIT/*)
          excluded=$((excluded + 1))
          continue
          ;;
      esac
      [ -f "$file" ] && LC_ALL=C grep -Iq . "$file" 2>/dev/null && cat -- "$file"
    done < <(git ls-files --others --exclude-standard -z 2>/dev/null)
    note_excluded "$excluded"
  fi
}

subcommand="${1:-}"
shift 2>/dev/null || true

case "$subcommand" in
  deliverable)
    [ "$#" -ge 2 ] || {
      printf 'usage: repo-state.sh deliverable <baseline> <path>\n' >&2
      exit 2
    }
    cmd_deliverable "$1" "$2"
    ;;
  changed-files)
    [ "$#" -ge 1 ] || {
      printf 'usage: repo-state.sh changed-files <baseline>\n' >&2
      exit 2
    }
    cmd_changed_files "$1"
    ;;
  added-lines)
    [ "$#" -ge 1 ] || {
      printf 'usage: repo-state.sh added-lines <baseline>\n' >&2
      exit 2
    }
    cmd_added_lines "$1"
    ;;
  ""|-h|--help|help)
    cat >&2 <<'EOF'
repo-state.sh - evaluate complete working-tree state vs a baseline commit.

  repo-state.sh deliverable   <baseline> <path>
  repo-state.sh changed-files <baseline>
  repo-state.sh added-lines   <baseline>

Use a single baseline revision. Do not use a two-dot commit range for final
audit or cleanliness checks, because ranges miss staged, unstaged, and
untracked work. Invalid baselines and non-git directories degrade to
existence-only deliverable checks.
EOF
    exit 2
    ;;
  *)
    printf "repo-state.sh: unknown subcommand '%s'\n" "$subcommand" >&2
    exit 2
    ;;
esac
