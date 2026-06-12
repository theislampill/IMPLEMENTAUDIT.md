#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

# 1. The live repo must pass.
bash scripts/check-validation-registry.sh

# 2. A test on disk missing from either registry must fail.
mkdir -p "$tmp/drift/tests" "$tmp/drift/scripts" "$tmp/drift/.github/workflows"
printf '#!/usr/bin/env bash\ntrue\n' > "$tmp/drift/tests/covered.test.sh"
printf '#!/usr/bin/env bash\ntrue\n' > "$tmp/drift/tests/orphan.test.sh"
printf '#!/usr/bin/env bash\ntrue\n' > "$tmp/drift/tests/docs-portal.test.sh"
printf 'bash tests/covered.test.sh\nbash tests/docs-portal.test.sh\n' > "$tmp/drift/scripts/verify-package.sh"
printf 'run: bash tests/covered.test.sh\nrun: bash tests/docs-portal.test.sh\n' > "$tmp/drift/.github/workflows/validate.yml"

if bash scripts/check-validation-registry.sh --repo-root "$tmp/drift" >/dev/null 2>&1; then
  printf 'validation-registry.test: expected orphan test to fail parity\n' >&2
  exit 1
fi

# 3. Full parity in a synthetic tree must pass.
printf 'bash tests/covered.test.sh\nbash tests/orphan.test.sh\nbash tests/docs-portal.test.sh\n' > "$tmp/drift/scripts/verify-package.sh"
printf 'run: bash tests/covered.test.sh\nrun: bash tests/orphan.test.sh\nrun: bash tests/docs-portal.test.sh\n' > "$tmp/drift/.github/workflows/validate.yml"
bash scripts/check-validation-registry.sh --repo-root "$tmp/drift"

# 4. A test present in CI but missing from verify-package must fail.
mkdir -p "$tmp/stale/tests" "$tmp/stale/scripts" "$tmp/stale/.github/workflows"
printf '#!/usr/bin/env bash\ntrue\n' > "$tmp/stale/tests/covered.test.sh"
printf '#!/usr/bin/env bash\ntrue\n' > "$tmp/stale/tests/docs-portal.test.sh"
printf 'bash tests/covered.test.sh\n' > "$tmp/stale/scripts/verify-package.sh"
printf 'run: bash tests/covered.test.sh\nrun: bash tests/docs-portal.test.sh\n' > "$tmp/stale/.github/workflows/validate.yml"

if bash scripts/check-validation-registry.sh --repo-root "$tmp/stale" >/dev/null 2>&1; then
  printf 'validation-registry.test: expected verify-package omission to fail\n' >&2
  exit 1
fi

printf 'validation-registry.test: ok\n'
