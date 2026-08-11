#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
helper="$repo_root/skills/implementaudit/scripts/claim-run.sh"
claim_validator="$repo_root/skills/implementaudit/scripts/validate-run-root.sh"

[ -f "$helper" ] || {
  printf 'claim-run.test: missing helper: %s\n' "$helper" >&2
  exit 1
}

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
if command -v python >/dev/null 2>&1; then py_cmd=(python)
elif command -v python3 >/dev/null 2>&1; then py_cmd=(python3)
elif command -v py >/dev/null 2>&1; then py_cmd=(py -3)
else printf 'claim-run.test: Python is required\n' >&2; exit 1; fi

work="$tmp/work with spaces"
mkdir -p "$work"
cd "$work"
git init -q
git config user.email claim-run@example.invalid
git config user.name claim-run-test

first="$(bash "$helper" "Audit release asset boundary" 2>/dev/null)"
second="$(bash "$helper" "Audit release asset boundary" 2>/dev/null)"

[ -d "$first" ] || {
  printf 'claim-run.test: first run root not created\n' >&2
  exit 1
}
[ -d "$second" ] || {
  printf 'claim-run.test: second run root not created\n' >&2
  exit 1
}
[ "$first" != "$second" ] || {
  printf 'claim-run.test: duplicate run roots for same slug\n' >&2
  exit 1
}

grep -qx 'mode=full' "$first/.claimed" || {
  printf 'claim-run.test: full claim sentinel missing mode=full\n' >&2
  exit 1
}
grep -qx 'templates=STATE.md PROTOCOL.md ROADMAP.md THINKING.md sidecars.md tools.md context.md' "$first/.claimed" || {
  printf 'claim-run.test: full claim sentinel missing canonical template set\n' >&2
  exit 1
}
grep -Eq '^claimed_at_utc=[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$' "$first/.claimed" || {
  printf 'claim-run.test: full claim sentinel missing UTC timestamp\n' >&2
  exit 1
}
CLAIM_EXPECTED_RUN_ROOT="$first" "${py_cmd[@]}" - "$first/.claimed" "$work" <<'PY' || {
import os,re,sys
from pathlib import Path
claim,work=map(Path,sys.argv[1:]); expected_run=os.environ['CLAIM_EXPECTED_RUN_ROOT']; rows=claim.read_text(encoding='utf-8').splitlines()
keys=[x.split('=',1)[0] for x in rows]
want=['schema','claim_id','claimed_at_utc','mode','templates','repo_root','git_common_dir','run_base','run_root','run_name']
if keys != want: raise SystemExit(f'claim key order {keys!r}')
d=dict(x.split('=',1) for x in rows)
if d['schema']!='implementaudit.run-claim.v2' or not re.fullmatch(r'[0-9a-f]{32}',d['claim_id']): raise SystemExit('v2 schema/id')
if Path(d['repo_root']) != work.resolve() or not Path(d['git_common_dir']).is_dir(): raise SystemExit('git custody')
if d['run_base']!='.IMPLEMENTAUDIT/runs' or d['run_root'] != expected_run or d['run_name'] != Path(expected_run).name: raise SystemExit('run identity')
PY
  printf 'claim-run.test: v2 claim metadata is not canonical\n' >&2
  exit 1
}

# The producer's own strict v2 claim must be consumable without path-domain
# translation.  This is especially important under Git Bash, where `pwd -P`
# and Git-for-Windows may otherwise report the same worktree in different
# native path domains.
for promised in STATE.md PROTOCOL.md ROADMAP.md THINKING.md sidecars.md tools.md context.md; do
  printf 'claim-run fixture\n' > "$first/$promised"
done
bash "$claim_validator" --claim-only "$first" --repo-root "$work" >/dev/null || {
  printf 'claim-run.test: generated v2 claim failed its strict consumer\n' >&2
  exit 1
}
case "$(uname -s 2>/dev/null || true)" in
  MINGW*|MSYS*|CYGWIN*)
    "${py_cmd[@]}" - "$first/.claimed" <<'PY' || {
import re,sys
from pathlib import Path
d=dict(line.split('=',1) for line in Path(sys.argv[1]).read_text(encoding='utf-8').splitlines())
for key in ('repo_root','git_common_dir'):
    if not re.match(r'^[A-Za-z]:[/\\]',d[key]):
        raise SystemExit(f'{key} is not in the Windows native path domain: {d[key]!r}')
PY
      printf 'claim-run.test: Git Bash claim paths are not canonical native Windows paths\n' >&2
      exit 1
    }
    ;;
esac

case "$first" in
  .IMPLEMENTAUDIT/runs/audit-release-asset-boundary-*) ;;
  *)
    printf 'claim-run.test: unexpected default run root: %s\n' "$first" >&2
    exit 1
    ;;
esac

custom_base="$tmp/custom base"
custom="$(IMPLEMENTAUDIT_BASE="$custom_base" bash "$helper" '../../Unsafe Name !!' 2>/dev/null)"
[ -d "$custom" ] || {
  printf 'claim-run.test: custom-base run root not created\n' >&2
  exit 1
}
case "$(basename "$custom")" in
  unsafe-name-*) ;;
  *)
    printf 'claim-run.test: slug was not sanitized: %s\n' "$custom" >&2
    exit 1
    ;;
esac

micro_base="$tmp/micro base"
micro="$(IMPLEMENTAUDIT_BASE="$micro_base" bash "$helper" --micro 'Tiny repair' 2>/dev/null)"
grep -qx 'mode=micro' "$micro/.claimed" || {
  printf 'claim-run.test: micro claim sentinel missing mode=micro\n' >&2
  exit 1
}
grep -qx 'templates=STATE.md' "$micro/.claimed" || {
  printf 'claim-run.test: micro claim sentinel names the wrong template set\n' >&2
  exit 1
}

mkdir -p "$micro_base/unmarked-sibling"
printf '# state without disposition\n' > "$micro_base/unmarked-sibling/STATE.md"
warning="$(IMPLEMENTAUDIT_BASE="$micro_base" bash "$helper" --micro 'Sibling warning' 2>&1 >/dev/null)"
printf '%s\n' "$warning" | grep -Fq 'unmarked-sibling' || {
  printf 'claim-run.test: claim did not list undispositioned sibling root\n' >&2
  exit 1
}

parallel_dir="$tmp/parallel"
mkdir -p "$parallel_dir"
N=16
i=1
while [ "$i" -le "$N" ]; do
  (
    cd "$work"
    bash "$helper" "same concurrent task" >"$parallel_dir/$i" 2>/dev/null
  ) &
  i=$((i + 1))
done
wait

emitted="$(cat "$parallel_dir"/* | grep -c .)"
unique="$(cat "$parallel_dir"/* | sort -u | grep -c .)"
[ "$emitted" = "$N" ] && [ "$unique" = "$N" ] || {
  printf 'claim-run.test: parallel claims not unique emitted=%s unique=%s\n' "$emitted" "$unique" >&2
  exit 1
}

printf 'claim-run.test: ok\n'
