#!/usr/bin/env bash
set -euo pipefail

fail() {
  printf 'check-added-lines-clean: %s\n' "$*" >&2
  exit 1
}

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

baseline="${1:-HEAD}"
helper="skills/scripts/repo-state.sh"
[ -f "$helper" ] || fail "missing helper: $helper"

added="$(mktemp)"
session_marker_added="$(mktemp)"
trap 'rm -f "$added" "$session_marker_added"' EXIT

is_skipped_path() {
  case "$1" in
    tests/*|fixtures/*|docs/audits/*|scripts/check-added-lines-clean.sh|*__pycache__*|*.pyc)
      return 0
      ;;
    *)
      return 1
      ;;
  esac
}

append_added_lines_for_file() {
  local file="$1"
  [ -n "$file" ] || return 0
  is_skipped_path "$file" && return 0

  if git rev-parse --is-inside-work-tree >/dev/null 2>&1 &&
    git rev-parse --verify --quiet "${baseline}^{commit}" >/dev/null 2>&1
  then
    if git ls-files --others --exclude-standard -- "$file" | grep -Fx "$file" >/dev/null 2>&1; then
      if [ -f "$file" ] && LC_ALL=C grep -Iq . "$file" 2>/dev/null; then
        cat -- "$file" >>"$added"
      fi
    else
      git diff "$baseline" -- "$file" 2>/dev/null |
        grep '^+' |
        grep -v '^+++' |
        sed 's/^+//' >>"$added" || true
    fi
  fi
}

while IFS= read -r changed_file; do
  append_added_lines_for_file "$changed_file"
done < <(bash "$helper" changed-files "$baseline")

failures=0

scan() {
  local label="$1"
  local pattern="$2"
  if grep -En "$pattern" "$added" >/tmp/implementaudit-added-lines-hit.txt; then
    printf 'check-added-lines-clean: %s\n' "$label" >&2
    cat /tmp/implementaudit-added-lines-hit.txt >&2
    failures=$((failures + 1))
  fi
  rm -f /tmp/implementaudit-added-lines-hit.txt
}

scan "debug print added" 'console\.log|console\.error|debugger;|(^|[^[:alnum:]_])print[[:space:]]*\(|pprint[[:space:]]*\(|fmt\.Println|log\.Println'

# TODO is also a deliberate reconciliation status in the v0.3.0.0 plan
# lifecycle contract. Remove only that exact status-list context before the
# generic session-marker scan, so ordinary TODO/FIXME/XXX debris still fails.
grep -Ev 'Reconciliation statuses|DONE / BLOCKED / IN PROGRESS / TODO / STALE / DRIFTED / FIXED INDEPENDENTLY|`TODO`' "$added" >"$session_marker_added" || true
if grep -En '\b(TODO|FIXME|XXX)\b' "$session_marker_added" >/tmp/implementaudit-added-lines-hit.txt; then
  printf 'check-added-lines-clean: session TODO/FIXME marker added\n' >&2
  cat /tmp/implementaudit-added-lines-hit.txt >&2
  failures=$((failures + 1))
fi
rm -f /tmp/implementaudit-added-lines-hit.txt

verified_word="verified"
install_word="install"
marketplace_word="marketplace"
published_word="published"
package_word="package"
attestation_word="attestation"
generated_word="generated"
signed_word="signed"
release_word="release"
sbom_word="sbom"
spdx_word="spdx"
mit_word="mit"
apache_word="apache"
license_word="license"
unsupported_claim_regex="${verified_word} ${install_word}|${install_word} ${verified_word}|${marketplace_word} ${verified_word}|${verified_word} ${marketplace_word}|${published_word} ${package_word}|${attestation_word} ${generated_word}|${signed_word} ${release_word}|${sbom_word} ${generated_word}|${spdx_word} ${generated_word}|${mit_word} ${license_word}|${apache_word} ${license_word}"
scan "unsupported host/release claim added" "$unsupported_claim_regex"

if [ "$failures" -ne 0 ]; then
  fail "$failures cleanliness/overclaim issue(s) found in added lines since $baseline"
fi

printf 'check-added-lines-clean: ok\n'
