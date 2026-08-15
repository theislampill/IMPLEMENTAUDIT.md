#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

bash scripts/check-installed-payload-self-contained.sh

mkdir -p "$tmp/skills/implementaudit"
cat >"$tmp/skills/implementaudit/SKILL.md" <<'BAD'
# Bad installed payload

Read fixtures/private-fixture.md before running this package.
Run tests/smoke.test.sh from the installed skill.
Use skills/implementaudit/scripts/repo-state.sh after install.
BAD

if bash scripts/check-installed-payload-self-contained.sh --scan-root "$tmp" >/tmp/payload-self-contained.out 2>&1; then
  printf 'installed-payload-self-contained.test: bad payload unexpectedly passed\n' >&2
  exit 1
fi
grep -F "repo-only path reference" /tmp/payload-self-contained.out >/dev/null || {
  printf 'installed-payload-self-contained.test: expected repo-only path diagnostic\n' >&2
  cat /tmp/payload-self-contained.out >&2
  exit 1
}

for variant in backslash mixed; do
  variant_root="$tmp/$variant"
  mkdir -p "$variant_root/skills/implementaudit"
  case "$variant" in
    backslash)
      printf '%s\n' 'Use skills\implementaudit\scripts\repo-state.sh after install.' \
        >"$variant_root/skills/implementaudit/SKILL.md"
      ;;
    mixed)
      printf '%s\n' 'Use skills/implementaudit\scripts/repo-state.sh after install.' \
        >"$variant_root/skills/implementaudit/SKILL.md"
      ;;
  esac
  if bash scripts/check-installed-payload-self-contained.sh \
      --scan-root "$variant_root" >"$tmp/$variant.out" 2>&1; then
    printf 'installed-payload-self-contained.test: %s path unexpectedly passed\n' \
      "$variant" >&2
    exit 1
  fi
  grep -F "repo-only path reference" "$tmp/$variant.out" >/dev/null || {
    printf 'installed-payload-self-contained.test: missing %s diagnostic\n' \
      "$variant" >&2
    cat "$tmp/$variant.out" >&2
    exit 1
  }
done

printf 'installed-payload-self-contained.test: ok\n'
