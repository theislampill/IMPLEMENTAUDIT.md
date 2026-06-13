#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

bash scripts/check-native-integration.sh

copy_runtime() {
  local dest="$1"
  mkdir -p "$dest"
  cp -R skills "$dest/"
  mkdir -p "$dest/fixtures"
  cp -R fixtures/native-integration "$dest/fixtures/"
}

copy_runtime "$tmp/missing-category"
rm "$tmp/missing-category/fixtures/native-integration/p0-performance-native-route.md"
if bash scripts/check-native-integration.sh --scan-root "$tmp/missing-category" >/tmp/native-missing-category.out 2>&1; then
  printf 'native-integration.test: expected missing category fixture to fail\n' >&2
  exit 1
fi
grep -q "missing required file: fixtures/native-integration/p0-performance-native-route.md" /tmp/native-missing-category.out || {
  printf 'native-integration.test: missing category failure was not specific\n' >&2
  cat /tmp/native-missing-category.out >&2
  exit 1
}

copy_runtime "$tmp/external-comparator-heading"
printf '\n## Donor Finding Format Contract\n' >> "$tmp/external-comparator-heading/skills/templates/THINKING.md"
if bash scripts/check-native-integration.sh --scan-root "$tmp/external-comparator-heading" >/tmp/native-external-comparator-heading.out 2>&1; then
  printf 'native-integration.test: expected external comparator heading to fail\n' >&2
  exit 1
fi
grep -q "runtime still contains standalone comparator-lane wording" /tmp/native-external-comparator-heading.out || {
  printf 'native-integration.test: external comparator heading failure was not specific\n' >&2
  cat /tmp/native-external-comparator-heading.out >&2
  exit 1
}

copy_runtime "$tmp/weak-fixture"
sed -i 's/Native route:/Comparator lane:/' \
  "$tmp/weak-fixture/fixtures/native-integration/p0-correctness-native-route.md"
if bash scripts/check-native-integration.sh --scan-root "$tmp/weak-fixture" >/tmp/native-weak-fixture.out 2>&1; then
  printf 'native-integration.test: expected weak fixture to fail\n' >&2
  exit 1
fi
grep -q "missing in fixtures/native-integration/p0-correctness-native-route.md: Native route:" /tmp/native-weak-fixture.out || {
  printf 'native-integration.test: weak fixture failure was not specific\n' >&2
  cat /tmp/native-weak-fixture.out >&2
  exit 1
}

copy_runtime "$tmp/canary-missing-marker"
sed -i '/AUDIT_VERIFY/d' \
  "$tmp/canary-missing-marker/fixtures/native-integration/transcripts/audit-object-route-canary-transcript.md"
if bash scripts/check-native-integration.sh --scan-root "$tmp/canary-missing-marker" >/tmp/native-canary-marker.out 2>&1; then
  printf 'native-integration.test: expected missing canary marker to fail\n' >&2
  exit 1
fi
grep -q "missing in fixtures/native-integration/transcripts/audit-object-route-canary-transcript.md: AUDIT_VERIFY" /tmp/native-canary-marker.out || {
  printf 'native-integration.test: canary marker failure was not specific\n' >&2
  cat /tmp/native-canary-marker.out >&2
  exit 1
}

copy_runtime "$tmp/missing-single-plan"
rm "$tmp/missing-single-plan/fixtures/native-integration/single-plan-native-route.md"
if bash scripts/check-native-integration.sh --scan-root "$tmp/missing-single-plan" >/tmp/native-single-plan.out 2>&1; then
  printf 'native-integration.test: expected missing single-plan fixture to fail\n' >&2
  exit 1
fi
grep -q "missing required file: fixtures/native-integration/single-plan-native-route.md" /tmp/native-single-plan.out || {
  printf 'native-integration.test: single-plan failure was not specific\n' >&2
  cat /tmp/native-single-plan.out >&2
  exit 1
}

copy_runtime "$tmp/generic-roadmap-weak"
sed -i '\|DMADV direction/design|d' "$tmp/generic-roadmap-weak/fixtures/native-integration/negative-generic-roadmap.md"
if bash scripts/check-native-integration.sh --scan-root "$tmp/generic-roadmap-weak" >/tmp/native-roadmap.out 2>&1; then
  printf 'native-integration.test: expected weak generic-roadmap negative fixture to fail\n' >&2
  exit 1
fi
grep -q "missing in fixtures/native-integration/negative-generic-roadmap.md: DMADV direction/design" /tmp/native-roadmap.out || {
  printf 'native-integration.test: roadmap negative failure was not specific\n' >&2
  cat /tmp/native-roadmap.out >&2
  exit 1
}

copy_runtime "$tmp/secret-hygiene"
printf '\nThe prod DB password is hunter2.\n' >> "$tmp/secret-hygiene/fixtures/native-integration/p0-security-native-route.md"
if bash scripts/check-native-integration.sh --scan-root "$tmp/secret-hygiene" >/tmp/native-secret.out 2>&1; then
  printf 'native-integration.test: expected realistic fake credential to fail\n' >&2
  exit 1
fi
grep -q "toy password" /tmp/native-secret.out || {
  printf 'native-integration.test: secret hygiene failure was not specific\n' >&2
  cat /tmp/native-secret.out >&2
  exit 1
}

printf 'native-integration.test: ok\n'
