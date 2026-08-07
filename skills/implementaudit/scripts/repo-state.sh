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

cmd_ignored_artifact() {
  local surface="$1" artifact="$2" digest_record="$3" authority_baseline="$4"
  case "$surface" in
    source)
      printf 'ignored-artifact: not-applicable for source surface\n'
      return 0
      ;;
    package|release) : ;;
    *) printf 'repo-state: ignored-artifact surface must be source, package, or release\n' >&2; return 2;;
  esac
  case "$artifact" in
    /*|[A-Za-z]:*|../*|*/../*)
      printf 'repo-state: ignored artifact must be repository-relative: %s\n' "$artifact" >&2
      return 1
      ;;
  esac
  case "$digest_record" in
    ''|/*|[A-Za-z]:*|../*|*/../*|./*|*/./*|*//*|*:*)
      printf 'repo-state: published digest record must be repository-relative: %s\n' "$digest_record" >&2
      return 1
      ;;
  esac
  printf '%s' "$authority_baseline" | grep -qE '^[0-9a-f]{40}$' || {
    printf 'repo-state: authority baseline must be a full 40-hex commit SHA\n' >&2
    return 1
  }
  in_git_repo && baseline_ok "$authority_baseline" || {
    printf 'repo-state: authority baseline is not a local commit: %s\n' "$authority_baseline" >&2
    return 1
  }
  git merge-base --is-ancestor "$authority_baseline" HEAD 2>/dev/null || {
    printf 'repo-state: authority baseline is not an ancestor of HEAD: %s\n' "$authority_baseline" >&2
    return 1
  }
  [ -f "$artifact" ] && [ ! -L "$artifact" ] || {
    printf 'repo-state: ignored artifact must be a regular non-symlink file: %s\n' "$artifact" >&2
    return 1
  }
  [ -f "$digest_record" ] && [ ! -L "$digest_record" ] || {
    printf 'repo-state: published digest record must be a regular non-symlink file: %s\n' "$digest_record" >&2
    return 1
  }
  if in_git_repo && ! git check-ignore -q -- "$artifact"; then
    printf 'repo-state: %s is not ignored; use normal deliverable evidence\n' "$artifact" >&2
    return 1
  fi
  if git ls-files --error-unmatch -- "$artifact" >/dev/null 2>&1; then
    printf 'repo-state: ignored artifact must be untracked: %s\n' "$artifact" >&2
    return 1
  fi
  git cat-file -e "${authority_baseline}:${digest_record}" 2>/dev/null || {
    printf 'repo-state: published digest record is not tracked at authority baseline %s: %s\n' \
      "$authority_baseline" "$digest_record" >&2
    return 1
  }
  git ls-files --error-unmatch -- "$digest_record" >/dev/null 2>&1 || {
    printf 'repo-state: published digest record is not tracked now: %s\n' "$digest_record" >&2
    return 1
  }
  git diff --quiet "$authority_baseline" -- "$digest_record" 2>/dev/null || {
    printf 'repo-state: published digest record differs from authority baseline: %s\n' "$digest_record" >&2
    return 1
  }
  cmp -s -- "$digest_record" <(git cat-file blob "${authority_baseline}:${digest_record}") || {
    printf 'repo-state: published digest record bytes are not authority-baseline bytes: %s\n' "$digest_record" >&2
    return 1
  }
  if command -v python >/dev/null 2>&1; then py_cmd=(python)
  elif command -v python3 >/dev/null 2>&1; then py_cmd=(python3)
  elif command -v py >/dev/null 2>&1; then py_cmd=(py -3)
  else printf 'repo-state: python is required for ignored-artifact\n' >&2; return 2
  fi
  "${py_cmd[@]}" - "$artifact" "$digest_record" "$surface" "$authority_baseline" <<'PY'
import hashlib
import pathlib
import re
import sys

artifact = pathlib.Path(sys.argv[1])
record = pathlib.Path(sys.argv[2])
surface = sys.argv[3]
authority_baseline = sys.argv[4]
key = artifact.as_posix()
matches = []
seen_paths = set()
for number, line in enumerate(record.read_text(encoding="utf-8").splitlines(), 1):
    if not line:
        continue
    match = re.fullmatch(r"([0-9a-f]{64})  (.+)", line)
    if not match:
        print(f"repo-state: malformed published digest row {number}", file=sys.stderr)
        raise SystemExit(1)
    normalized = match.group(2).replace("\\", "/")
    if normalized in seen_paths:
        print(f"repo-state: duplicate published digest path {normalized}", file=sys.stderr)
        raise SystemExit(1)
    seen_paths.add(normalized)
    if normalized == key:
        matches.append(match.group(1))
if len(matches) != 1:
    print(f"repo-state: published digest record requires exactly one row for {key}", file=sys.stderr)
    raise SystemExit(1)
observed = hashlib.sha256(artifact.read_bytes()).hexdigest()
if observed != matches[0]:
    print(f"repo-state: stale ignored {surface} artifact {key}: observed={observed} published={matches[0]}", file=sys.stderr)
    raise SystemExit(1)
print(f"ignored-artifact: current | surface={surface} | path={key} | sha256={observed} | authority-baseline={authority_baseline}")
PY
}

cmd_commit_message() {
  local message_file="$1" ledger_linked="$2"
  [ -f "$message_file" ] && [ ! -L "$message_file" ] || {
    printf 'repo-state: commit-message input must be a regular non-symlink file: %s\n' "$message_file" >&2
    return 1
  }
  local py_cmd
  if command -v python >/dev/null 2>&1; then py_cmd=(python)
  elif command -v python3 >/dev/null 2>&1; then py_cmd=(python3)
  elif command -v py >/dev/null 2>&1; then py_cmd=(py -3)
  else printf 'repo-state: python is required for commit-message\n' >&2; return 2
  fi
  "${py_cmd[@]}" - "$message_file" "$ledger_linked" <<'PY'
import re
import sys
from pathlib import Path

message = Path(sys.argv[1]).read_text(encoding="utf-8")
ledger_linked = sys.argv[2] == "yes"
lines = message.splitlines()
subject = lines[0].strip() if lines else ""
body = "\n".join(lines[1:]).strip()

conventional = re.fullmatch(
    r"(?P<type>[a-z][a-z0-9-]*)(?:\([^)\r\n]+\))?(?P<bang>!)?:\s+\S.*",
    subject,
)
class_b = (
    ledger_linked
    or conventional is None
    or conventional.group("type") in {"feat", "fix", "perf", "revert"}
    or conventional.group("bang") == "!"
    or re.search(r"(?m)^BREAKING CHANGE:\s+\S", body) is not None
)

if class_b and not body:
    print("repo-state: commit-message Class B requires a non-empty body", file=sys.stderr)
    raise SystemExit(1)

sha_tokens = re.findall(r"(?<![0-9a-f])[0-9a-f]{7,40}(?![0-9a-f])", body)
has_sha = any(
    len(token) == 40
    or (any(ch.isdigit() for ch in token) and any(ch in "abcdef" for ch in token))
    for token in sha_tokens
)
has_path_line = re.search(
    r"(?<![A-Za-z0-9_./:-])(?:[A-Za-z0-9_.-]+/)*[A-Za-z0-9_.-]+\.[A-Za-z0-9_.-]+:[1-9][0-9]*\b",
    body,
) is not None
has_test_path = re.search(
    r"(?<![A-Za-z0-9_./:-])(?:fixtures|tests)/(?:[A-Za-z0-9_.-]+/)*[A-Za-z0-9_-]+\.[A-Za-z0-9_.-]+",
    body,
) is not None
has_command_exit = re.search(
    r"(?im)\b(?:[A-Za-z0-9_.-]+\.(?:sh|test)|[A-Za-z0-9_.-]*check[A-Za-z0-9_.-]*)\b[^\n]*\bexit(?:\s+|:\s*)[0-9]+\b",
    body,
) is not None
has_occurrences = re.search(
    r"(?im)\boccurrences:\s*[1-9][0-9]*(?=\s|$|[),.;])",
    body,
) is not None
sentinels = {"tbd", "todo", "none", "n/a", "na", "not-applicable", "unknown", "pending"}
landed_values = re.findall(
    r"(?im)\b(?:anchor|hunk):\s*([^\s<]+)(?=\s|$)",
    body,
)
has_landed = any(value.lower().rstrip(".,;") not in sentinels for value in landed_values)
has_anchor = has_sha or has_path_line or has_test_path or has_command_exit or has_occurrences or has_landed
if class_b and not has_anchor:
    print("repo-state: commit-message Class B requires an evidence anchor", file=sys.stderr)
    raise SystemExit(1)

has_issue = re.search(r"(?<![A-Za-z0-9])#[1-9][0-9]*\b", body) is not None
direct_row_values = re.findall(
    r"(?im)^\s*(?:finding|ledger-row|andon-row|andon):\s*([A-Za-z0-9][A-Za-z0-9._-]*)",
    body,
)
linkage_row_values = re.findall(
    r"(?im)^\s*linkage:\s*(?:ledger-row|andon):\s*([A-Za-z0-9][A-Za-z0-9._-]*)",
    body,
)
row_values = direct_row_values + linkage_row_values
has_row = any(
    value.lower() not in sentinels
    and (any(ch.isdigit() for ch in value) or "-" in value)
    for value in row_values
)
if ledger_linked and not (has_issue or has_row):
    print(
        "repo-state: commit-message --ledger-linked requires finding, issue, ledger-row, or Andon linkage",
        file=sys.stderr,
    )
    raise SystemExit(1)

print(
    "commit-message: class={} | body={} | anchor={} | ledger-linked={}".format(
        "B" if class_b else "M",
        "present" if body else "absent",
        "present" if has_anchor else "not-required",
        "yes" if ledger_linked else "no",
    )
)
PY
}

subcommand="${1:-}"
shift 2>/dev/null || true

case "$subcommand" in
  commit-message)
    [ "$#" -ge 1 ] && [ "$#" -le 2 ] || {
      printf 'usage: repo-state.sh commit-message <message-file> [--ledger-linked]\n' >&2
      exit 2
    }
    ledger_linked=no
    if [ "$#" -eq 2 ]; then
      [ "$2" = "--ledger-linked" ] || {
        printf 'usage: repo-state.sh commit-message <message-file> [--ledger-linked]\n' >&2
        exit 2
      }
      ledger_linked=yes
    fi
    cmd_commit_message "$1" "$ledger_linked"
    ;;
  ignored-artifact)
    [ "$#" -eq 4 ] || {
      printf 'usage: repo-state.sh ignored-artifact <source|package|release> <artifact> <published-digest-record> <authority-baseline>\n' >&2
      exit 2
    }
    cmd_ignored_artifact "$1" "$2" "$3" "$4"
    ;;
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
  repo-state.sh commit-message <message-file> [--ledger-linked]
  repo-state.sh ignored-artifact <source|package|release> <artifact> <published-digest-record> <authority-baseline>

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
