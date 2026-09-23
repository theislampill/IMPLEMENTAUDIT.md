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

if bash scripts/check-installed-payload-self-contained.sh --scan-root "$tmp" >"$tmp/payload-self-contained.out" 2>&1; then
  printf 'installed-payload-self-contained.test: bad payload unexpectedly passed\n' >&2
  exit 1
fi
grep -F "repo-only path reference" "$tmp/payload-self-contained.out" >/dev/null || {
  printf 'installed-payload-self-contained.test: expected repo-only path diagnostic\n' >&2
  cat "$tmp/payload-self-contained.out" >&2
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

# Runtime-relative rows, prose slashes, and real source-path negatives.
python - "$repo_root" <<'PATH_SCANNER_PY'
import subprocess,tempfile,pathlib,json,sys
r=pathlib.Path(sys.argv[1]).resolve();rows=[]
cases=[('typed-runtime','helper-route: scripts/check-evidence-anchor.sh|R|scope|P|-|--artifact ...|disjoint\n',True),('prose-slashes','Existing authority/review/tests/qualification remains separate.\n',True),('root-test','Run tests/unshipped.test.sh after install.\n',False),('infix-not-root','The presence/tests/self-use/wildcards do not prove conformance.\n',True),('forged-registry','helper-route: scripts/check-absent.sh|R|scope|P|-|x|y\n',False),('runtime-plus-source','helper-route: scripts/check-evidence-anchor.sh|R|scope|P|-|x|y; run tests/absent.sh\n',False),('source-qualified','Use skills/implementaudit/scripts/repo-state.sh after install.\n',False)]
for name,text,expected in cases:
 with tempfile.TemporaryDirectory() as t:
  t=pathlib.Path(t);p=t/'skills/implementaudit';(p/'scripts').mkdir(parents=True)
  (p/'SKILL.md').write_text(text);(p/'scripts/check-evidence-anchor.sh').write_text('#!/bin/sh\nexit 0\n')
  q=subprocess.run(['bash',str(r/'scripts/check-installed-payload-self-contained.sh'),'--scan-root',str(t)],capture_output=True,text=True)
  rows.append({'case':name,'expected_accept':expected,'exit':q.returncode,'passed':(q.returncode==0)==expected,'stderr':q.stderr})
print(json.dumps(rows,indent=2));sys.exit(0 if all(x['passed'] for x in rows) else 1)

PATH_SCANNER_PY

# Both entry points must use the same namespace and separator contract.
python - "$repo_root" <<'ENTRY_PARITY_PY'
import pathlib,subprocess,sys,tempfile,json,shutil
r=pathlib.Path(sys.argv[1]);v=(r/'scripts/verify-package.sh').read_text()
start=v.index('# Shipped-payload path integrity:')
end=v.index('\nfor marker in \\',start)
block=v[start:end]
rows=[]
for name,text,accept in [
 ('typed','helper-route: scripts/check-evidence-anchor.sh|R|scope|P|-|x|y\n',True),
 ('prose','Keep authority/review/tests/qualification separate.\n',True),
 ('infix','Presence/tests/self-use/wildcards are not proof.\n',True),
 ('dangling','Run tests/not-shipped.sh now.\n',False),
 ('backslash','Use skills\\implementaudit\\scripts\\repo-state.sh after install.\n',False),
 ('mixed','Use skills/implementaudit\\scripts/repo-state.sh after install.\n',False),
 ('forged','helper-route: scripts/check-absent.sh|R|scope|P|-|x|y\n',False),
 ('qualified','Source repo: run tests/not-shipped.sh there.\n',True),
]:
 with tempfile.TemporaryDirectory() as td:
  t=pathlib.Path(td);(t/'skills/implementaudit/scripts').mkdir(parents=True);(t/'scripts').mkdir()
  (t/'skills/implementaudit/SKILL.md').write_text(text)
  (t/'skills/implementaudit/scripts/check-evidence-anchor.sh').write_text('#!/bin/sh\nexit 0\n')
  shutil.copy2(r/'scripts/check-installed-payload-self-contained.sh',t/'scripts')
  q=subprocess.run(['bash','-c','set -euo pipefail\npy_cmd=(python)\n'+block],cwd=t,capture_output=True,text=True)
  rows.append(dict(case=name,expected_accept=accept,exit=q.returncode,pass_=(q.returncode==0)==accept,stderr=q.stderr))
print(json.dumps(rows,indent=2));assert all(x['pass_'] for x in rows), 'canonical and maintained scanner differ'
ENTRY_PARITY_PY
