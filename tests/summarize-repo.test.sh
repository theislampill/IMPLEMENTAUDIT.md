#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

helper="$repo_root/skills/implementaudit/scripts/summarize-repo.sh"

# 1. In a minimal repo with no checkers, candidate discovery offers only the
#    universal baseline command — no hardcoded IMPLEMENTAUDIT paths.
mkdir -p "$tmp/bare"
(
  cd "$tmp/bare"
  git init -q
  printf '# bare\n' > README.md
  git add README.md
  git -c user.email=test@example.invalid -c user.name=test commit -qm init
  bash "$helper" > out.log 2>&1
)
grep -q "git diff --check" "$tmp/bare/out.log" || {
  printf 'summarize-repo.test: baseline candidate missing in bare repo\n' >&2
  exit 1
}
if grep -q "bash scripts/check-" "$tmp/bare/out.log"; then
  printf 'summarize-repo.test: hardcoded checker candidates leaked into bare repo\n' >&2
  exit 1
fi

# 2. In a repo that has checkers and focused tests, discovery offers them.
mkdir -p "$tmp/rich/scripts" "$tmp/rich/tests"
(
  cd "$tmp/rich"
  git init -q
  printf '#!/usr/bin/env bash\ntrue\n' > scripts/check-example.sh
  printf '#!/usr/bin/env bash\ntrue\n' > scripts/verify-package.sh
  printf '#!/usr/bin/env bash\ntrue\n' > tests/example.test.sh
  git add -A
  git -c user.email=test@example.invalid -c user.name=test commit -qm init
  bash "$helper" > out.log 2>&1
)
grep -q "bash scripts/check-example.sh" "$tmp/rich/out.log" || {
  printf 'summarize-repo.test: discovered checker candidate missing\n' >&2
  exit 1
}
grep -q "bash scripts/verify-package.sh" "$tmp/rich/out.log" || {
  printf 'summarize-repo.test: verify-package candidate missing\n' >&2
  exit 1
}
grep -q "bash tests/example.test.sh" "$tmp/rich/out.log" || {
  printf 'summarize-repo.test: discovered test candidate missing\n' >&2
  exit 1
}

printf 'summarize-repo.test: ok\n'
