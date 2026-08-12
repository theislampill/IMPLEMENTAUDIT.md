#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

# 1. The live repo must pass.
bash scripts/check-validation-registry.sh

# 2. A test on disk missing from the canonical registry must fail.
mkdir -p "$tmp/drift/tests" "$tmp/drift/scripts" "$tmp/drift/.github/workflows"
printf '#!/usr/bin/env bash\ntrue\n' > "$tmp/drift/tests/covered.test.sh"
printf '#!/usr/bin/env bash\ntrue\n' > "$tmp/drift/tests/orphan.test.sh"
printf '#!/usr/bin/env bash\ntrue\n' > "$tmp/drift/tests/docs-portal.test.sh"
printf 'bash tests/covered.test.sh\nbash tests/docs-portal.test.sh\n' > "$tmp/drift/scripts/verify-package.sh"
printf 'run: bash scripts/verify-package.sh\n' > "$tmp/drift/.github/workflows/validate.yml"

if bash scripts/check-validation-registry.sh --repo-root "$tmp/drift" >/dev/null 2>&1; then
  printf 'validation-registry.test: expected orphan test to fail parity\n' >&2
  exit 1
fi

# 3. A require_file-only mention must not count as execution.
mkdir -p "$tmp/require-only/tests" "$tmp/require-only/scripts" "$tmp/require-only/.github/workflows"
printf '#!/usr/bin/env bash\ntrue\n' > "$tmp/require-only/tests/covered.test.sh"
printf '#!/usr/bin/env bash\ntrue\n' > "$tmp/require-only/tests/orphan.test.sh"
printf '#!/usr/bin/env bash\ntrue\n' > "$tmp/require-only/tests/docs-portal.test.sh"
printf 'bash tests/covered.test.sh\nbash tests/docs-portal.test.sh\nrequire_file tests/orphan.test.sh\n' > "$tmp/require-only/scripts/verify-package.sh"
printf 'run: bash scripts/verify-package.sh\n' > "$tmp/require-only/.github/workflows/validate.yml"

if bash scripts/check-validation-registry.sh --repo-root "$tmp/require-only" >/dev/null 2>&1; then
  printf 'validation-registry.test: expected require_file-only test mention to fail\n' >&2
  exit 1
fi

# 4. Complete package registry plus one canonical CI route must pass.
printf 'bash tests/covered.test.sh\nbash tests/orphan.test.sh\nbash tests/docs-portal.test.sh\n' > "$tmp/drift/scripts/verify-package.sh"
printf 'run: bash scripts/verify-package.sh\n' > "$tmp/drift/.github/workflows/validate.yml"
bash scripts/check-validation-registry.sh --repo-root "$tmp/drift"

# 5. CI-only direct coverage must not exempt a test from package-registry parity.
mkdir -p "$tmp/ci-only/tests" "$tmp/ci-only/scripts" "$tmp/ci-only/.github/workflows"
printf '#!/usr/bin/env bash\ntrue\n' > "$tmp/ci-only/tests/covered.test.sh"
printf '#!/usr/bin/env bash\ntrue\n' > "$tmp/ci-only/tests/docs-portal.test.sh"
printf 'bash tests/covered.test.sh\n' > "$tmp/ci-only/scripts/verify-package.sh"
printf 'run: bash tests/covered.test.sh\nrun: bash tests/docs-portal.test.sh\n' > "$tmp/ci-only/.github/workflows/validate.yml"

if bash scripts/check-validation-registry.sh --repo-root "$tmp/ci-only" >/dev/null 2>&1; then
  printf 'validation-registry.test: expected CI-only test to fail package parity\n' >&2
  exit 1
fi

# 6. CI must reach the canonical registry.
printf 'true\n' > "$tmp/drift/.github/workflows/validate.yml"
if bash scripts/check-validation-registry.sh --repo-root "$tmp/drift" >/dev/null 2>&1; then
  printf 'validation-registry.test: expected missing canonical CI route to fail\n' >&2
  exit 1
fi

# 7. A canonical route plus direct test duplication must fail.
printf 'run: bash scripts/verify-package.sh\nrun: bash tests/covered.test.sh\n' > "$tmp/drift/.github/workflows/validate.yml"
if bash scripts/check-validation-registry.sh --repo-root "$tmp/drift" >/dev/null 2>&1; then
  printf 'validation-registry.test: expected duplicate direct CI test route to fail\n' >&2
  exit 1
fi

printf 'validation-registry.test: ok\n'
