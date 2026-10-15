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

python -I -B - "$repo_root" "$tmp" "$BASH" <<'PY'
import os
from pathlib import Path
import subprocess
import sys

repo, temporary, bash = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3]
scanner = repo / 'scripts/check-installed-payload-self-contained.sh'
def run(name, row, expected, member='scripts/check-fixture.sh', source='owner', directory=False):
    root = temporary / ('route-' + name)
    skill = root / 'skills/implementaudit'
    target = skill / member
    target.parent.mkdir(parents=True, exist_ok=True)
    if directory:
        target.mkdir()
    else:
        target.write_text('#!/usr/bin/env bash\ntrue\n', encoding='utf-8')
    if name == 'root-only':
        root_checker = root / 'scripts/check-installed-payload-self-contained.sh'
        root_checker.parent.mkdir()
        root_checker.write_bytes(scanner.read_bytes())
    owner = skill / ('references/repo-state-comparison.md' if source == 'owner' else 'SKILL.md')
    owner.parent.mkdir(parents=True, exist_ok=True)
    owner.write_text(row + '\n', encoding='utf-8')
    result = subprocess.run([bash, str(scanner), '--scan-root', str(root)], capture_output=True, text=True)
    assert (result.returncode == 0) == expected, (name, result.stdout, result.stderr)
    print('installed-payload-self-contained: ' + name + ' ok')

valid='helper-route: scripts/check-fixture.sh|S|diagnosis|R|-|none|not-auto'
run('packaged-first-field', valid, True)
run('nested-member', valid.replace('scripts/check-fixture.sh','scripts/nested/check-fixture.sh'), True, 'scripts/nested/check-fixture.sh')
run('wrong-owner', valid, False, source='other')
for name, member in [('missing','scripts/check-missing.sh'),('root-only','scripts/check-installed-payload-self-contained.sh'),('traversal','scripts/../check-fixture.sh'),('absolute','/scripts/check-fixture.sh'),('backslash','scripts\\check-fixture.sh'),('mixed','scripts/nested\\check-fixture.sh'),('normalized-alias','scripts/./check-fixture.sh'),('double-slash','scripts//check-fixture.sh')]:
    run(name, valid.replace('scripts/check-fixture.sh',member), False)
run('directory',valid,False,directory=True)
run('six-fields', valid.rsplit('|',1)[0], False)
run('eight-fields', valid+'|extra', False)
for name, value in [('test','tests/smoke.test.sh'),('fixture','fixtures/secret.json'),('root-checker','scripts/check-repo-only.sh'),('repeat-first','scripts/check-fixture.sh')]:
    run('remaining-field-'+name,valid.replace('|none|','|'+value+'|'),False)
run('ordinary-reference','Run scripts/check-fixture.sh during installed use.',False)
run('repo-side-reference','Source repo maintenance uses scripts/check-fixture.sh.',True)
run('installed-source-layout','Source repo installed payload uses skills/implementaudit/scripts/check-fixture.sh.',False)

# A hardlink cannot turn an outside physical member into declaration authority.
root=temporary/'route-hardlink';skill=root/'skills/implementaudit'
(skill/'scripts').mkdir(parents=True);(skill/'references').mkdir()
outside=root/'outside.sh';outside.write_text('true\n',encoding='utf-8')
os.link(outside,skill/'scripts/check-fixture.sh')
(skill/'references/repo-state-comparison.md').write_text(valid+'\n',encoding='utf-8')
result=subprocess.run([bash,str(scanner),'--scan-root',str(root)],capture_output=True,text=True)
assert result.returncode!=0 and 'invalid packaged helper declaration' in result.stderr
print('installed-payload-self-contained: hardlink refusal ok')
PY

printf 'installed-payload-self-contained.test: ok\n'
