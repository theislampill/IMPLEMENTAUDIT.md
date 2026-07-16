#!/usr/bin/env bash
# payload-path-hygiene.test.sh - the layout contract must reject user-home
# absolute paths planted in the payload (Windows, macOS, Linux forms) and
# accept the clean payload.
set -euo pipefail

fail() {
  printf 'payload-path-hygiene.test: %s\n' "$*" >&2
  exit 1
}

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT

copy="$work/repo"
mkdir -p "$copy"
(cd "$repo_root" && git ls-files -z | tar --null -T - -cf - ) | (cd "$copy" && tar -xf -)

bash "$copy/scripts/check-skill-layout-contract.sh" --repo-root "$copy" >/dev/null \
  || fail "clean payload unexpectedly rejected"

for planted in 'C:\Users\someone\.codex\skills\implementaudit\SKILL.md' \
               'C:\\Users\\someone\\.codex\\SKILL.md' \
               'C:/Users/someone/.codex/SKILL.md' \
               '/Users/someone/skills/implementaudit/' \
               '/home/someone/skills/implementaudit/'; do
  printf 'leaked path: %s\n' "$planted" > "$copy/skills/implementaudit/references/__planted__.md"
  if bash "$copy/scripts/check-skill-layout-contract.sh" --repo-root "$copy" >/dev/null 2>&1; then
    fail "planted path was not rejected: $planted"
  fi
  rm -f "$copy/skills/implementaudit/references/__planted__.md"
done

# False-positive guard: placeholder and env-var forms must NOT be rejected.
{
  printf 'placeholder: %s\n' 'C:\Users\<name>\.codex\skills\implementaudit'
  printf 'env form: %s\n' '$CODEX_HOME/skills/implementaudit'
  printf 'tilde form: %s\n' '~/.codex/skills/implementaudit'
  printf 'env posix: %s\n' '/home/$USER/skills/'
} > "$copy/skills/implementaudit/references/__placeholders__.md"
bash "$copy/scripts/check-skill-layout-contract.sh" --repo-root "$copy" >/dev/null \
  || fail "placeholder/env-var forms were wrongly rejected"
rm -f "$copy/skills/implementaudit/references/__placeholders__.md"

bash "$copy/scripts/check-skill-layout-contract.sh" --repo-root "$copy" >/dev/null \
  || fail "payload rejected after removing planted files"

printf 'payload-path-hygiene.test: ok\n'
