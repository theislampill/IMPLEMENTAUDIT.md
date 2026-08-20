#!/usr/bin/env bash
# R0039 F1 is an immutable, nonmergeable semantic RED checkpoint.
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
checker="$repo_root/scripts/check-canonical-state-rotation.sh"
helper="$repo_root/skills/implementaudit/scripts/rotate-canonical-state.py"
f2_fixture="$repo_root/fixtures/canonical-state-rotation/f2-draft-archive.json"
tmp="$(mktemp -d)"
trap 'rm -rf -- "$tmp"' EXIT

fail() { printf 'canonical-state-rotation.test: %s\n' "$*" >&2; exit 2; }

case "${1:-}" in
  '') f2_only=false ;;
  --f2-only) f2_only=true ;;
  *) fail "usage: canonical-state-rotation.test.sh [--f2-only]" ;;
esac

[ -f "$checker" ] || fail "missing root checker: $checker"
bash -n "$checker" || fail "checker syntax is invalid"
fixture_output="$(bash "$checker" --fixture-self-check)"
printf '%s\n' "$fixture_output"
grep -Fq 'denominator=110 omission=110 mutation=110 owner-mutation=110 root-semantic-red=56' <<<"$fixture_output" \
  || fail 'protected denominator is not the exact reviewed four-part population'
grep -Fq 'partitions={"ARCHIVED_ONLY_HISTORY":14,"DERIVED_BINDINGS":29,"MONOTONIC_TRANSITION":18,"PRESERVED_PAYLOAD":49}' <<<"$fixture_output" \
  || fail 'protected denominator is not exactly four-part'
if grep -Fq 'TRIGGER_CALIBRATION' <<<"$fixture_output"; then
  fail 'trigger/calibration leaked into the protected-state partitions'
fi
trigger_output="$(bash "$checker" --trigger-self-check)"
printf '%s\n' "$trigger_output"
grep -Fq 'CANONICAL_STATE_ROTATION_TRIGGER_SELF_CHECK=PASS' <<<"$trigger_output" \
  || fail 'trigger/calibration self-check did not pass'
grep -Fq 'large-root=TRIGGER below-threshold=NO_TRIGGER archive=0 model=0 extra-ceremony=0' <<<"$trigger_output" \
  || fail 'trigger self-check did not preserve the positive and cheap-path outcomes'
grep -Fq 'population-sha256=b3df1ff07d18f8f5de145cf6d10f48a15f0a0416b392d0ca84567dce6d23e497 digest-mutations=55/55' <<<"$trigger_output" \
  || fail 'trigger self-check did not prove canonical population digest mutation coverage'
bash "$checker" --assert-root-red

before_shared_refs="$(git -C "$repo_root" for-each-ref --format='%(refname) %(objectname)' \
  refs/implementaudit/current-generations/ \
  refs/implementaudit/current-generation-migrations/ \
  refs/implementaudit/continuity-invalidations/ \
  refs/implementaudit/continuity-receipts/ \
  refs/implementaudit/state-archives/)"

[ -f "$f2_fixture" ] || fail "missing F2 fixture: $f2_fixture"
if [ ! -f "$helper" ]; then
  printf '%s\n' \
    'CANONICAL_STATE_ROTATION_F2_RED=DRAFT_ARCHIVE_OWNER_ABSENT' >&2
  exit 1
fi
bash "$checker" --f2-fixture-self-check

make_clean_root() {
  local root="$1"
  local run="$root/.IMPLEMENTAUDIT/runs/run-f2"
  mkdir -p "$run"
  git -C "$root" init -q
  printf 'controller: v0333-release\nphase: R39-F2\nnext: implement draft and archive\n' >"$run/STATE.md"
  printf 'audit: R0039\nfrontier: R39-F2\nnext: implement draft and archive\n' >"$run/ROADMAP.md"
  printf '{"active":["R39-F2"],"blocked":["R39-F3"]}\n' >"$run/WORK_GRAPH.json"
  cp "$f2_fixture" "$run/archive-population.json"
  git -C "$root" add .
  GIT_AUTHOR_DATE='2000-01-01T00:00:00Z' \
    GIT_COMMITTER_DATE='2000-01-01T00:00:00Z' \
    git -C "$root" -c user.name=fixture -c user.email=fixture@example.invalid \
      -c commit.gpgsign=false commit -qm preimage
  [ -z "$(git -C "$root" status --porcelain)" ] \
    || fail "two-clean-root control did not start clean: $root"
}

root_a="$tmp/root-a"
root_b="$tmp/root-b"
mkdir -p "$root_a" "$root_b"
make_clean_root "$root_a"
make_clean_root "$root_b"
run_a="$root_a/.IMPLEMENTAUDIT/runs/run-f2"
run_b="$root_b/.IMPLEMENTAUDIT/runs/run-f2"

draft_a="$(python "$helper" draft \
  --repo-root "$root_a" --run-root "$run_a" \
  --controller v0333-release --generation g0008 \
  --manifest "$run_a/archive-population.json")"
draft_b="$(python "$helper" draft \
  --repo-root "$root_b" --run-root "$run_b" \
  --controller v0333-release --generation g0008 \
  --manifest "$run_b/archive-population.json")"

draft_dir_a="$run_a/state-generations/g0008/draft"
draft_dir_b="$run_b/state-generations/g0008/draft"
diff -ru "$draft_dir_a" "$draft_dir_b" >/dev/null \
  || fail 'two clean roots produced different projection-draft bytes'

archive_a="$(python "$helper" archive \
  --repo-root "$root_a" --run-root "$run_a" \
  --controller v0333-release --generation g0008 \
  --draft-dir "$draft_dir_a")"
archive_b="$(python "$helper" archive \
  --repo-root "$root_b" --run-root "$run_b" \
  --controller v0333-release --generation g0008 \
  --draft-dir "$draft_dir_b")"

archive_ref='refs/implementaudit/state-archives/v0333-release/g0008'
archive_oid_a="$(git -C "$root_a" rev-parse --verify "$archive_ref")"
archive_oid_b="$(git -C "$root_b" rev-parse --verify "$archive_ref")"
[ "$archive_oid_a" = "$archive_oid_b" ] \
  || fail 'two clean roots produced different archive-manifest OIDs'
[ "$(git -C "$root_a" cat-file -t "$archive_oid_a")" = blob ] \
  || fail 'archive ref does not resolve to a typed blob'
[ "$(git -C "$root_a" cat-file blob "$archive_oid_a")" = \
   "$(git -C "$root_b" cat-file blob "$archive_oid_b")" ] \
  || fail 'two clean roots produced different archive-manifest bytes'

verify_a="$(python "$helper" verify-archive \
  --repo-root "$root_a" --controller v0333-release --generation g0008)"
verify_b="$(python "$helper" verify-archive \
  --repo-root "$root_b" --controller v0333-release --generation g0008)"

foreign="$tmp/foreign"
mkdir -p "$foreign"
git -C "$foreign" init -q
if ! verify_sanitized="$(GIT_DIR="$foreign/.git" GIT_WORK_TREE="$foreign" \
    python "$helper" verify-archive \
      --repo-root "$root_a" --controller v0333-release --generation g0008)"; then
  fail 'ambient Git repository variables overrode the explicit repository root'
fi
[ "$verify_sanitized" = "$verify_a" ] \
  || fail 'ambient Git repository variables changed typed archive retrieval'

if python "$helper" archive \
    --repo-root "$root_a" --run-root "$run_a" \
    --controller v0333-release --generation g0008 \
    --draft-dir "$draft_dir_a" >"$tmp/reanchor.out" 2>&1; then
  fail 'archive ref accepted a non-zero predecessor'
fi
grep -Fq 'archive ref already exists; expected-zero CAS refused' "$tmp/reanchor.out" \
  || fail 'archive ref collision did not fail with the expected-zero diagnostic'

for root in "$root_a" "$root_b"; do
  [ -z "$(git -C "$root" for-each-ref --format='%(refname)' \
      refs/implementaudit/current-generations/ \
      refs/implementaudit/current-generation-migrations/ \
      refs/implementaudit/continuity-invalidations/ \
      refs/implementaudit/continuity-receipts/)" ] \
    || fail 'F2 wrote a current-generation, marker, invalidation, or receipt ref'
done

python - "$draft_a" "$draft_b" "$archive_a" "$archive_b" \
  "$verify_a" "$verify_b" <<'PY' || fail 'F2 receipts are malformed or nondeterministic'
import json,sys
draft_a,draft_b,archive_a,archive_b,verify_a,verify_b = map(json.loads,sys.argv[1:])
if draft_a != draft_b:
    raise SystemExit("draft receipts differ")
if archive_a != archive_b:
    raise SystemExit("archive receipts differ")
if verify_a != verify_b or verify_a != archive_a:
    raise SystemExit("archive readback receipt differs")
if draft_a.get("schema") != "implementaudit.canonical-state-projection-draft-receipt.v1":
    raise SystemExit("draft receipt schema")
if archive_a.get("schema") != "implementaudit.canonical-state-archive-receipt.v1":
    raise SystemExit("archive receipt schema")
PY

python - "$root_a" "$draft_dir_a" "$archive_oid_a" <<'PY' \
  || fail 'archive typed retrieval, discovery exclusion, or permission readback failed'
import hashlib,json,os,stat,subprocess,sys
from pathlib import Path
root,draft_dir,manifest_oid=Path(sys.argv[1]),Path(sys.argv[2]),sys.argv[3]
draft=json.loads((draft_dir/'draft-manifest.json').read_text(encoding='utf-8'))
for forbidden in ('current_generation','epoch','invalidation_oid','migration_marker','pointer_oid','predecessor_receipt','receipt_oid'):
    if forbidden in draft:
        raise SystemExit(f"transition envelope leaked: {forbidden}")
archive=json.loads(subprocess.check_output(['git','-C',str(root),'cat-file','blob',manifest_oid],text=True))
if archive['entries'] != draft['entries']:
    raise SystemExit('archive and draft entries differ')
for entry in archive['entries']:
    if any(part in {'state-generations','state-archives','quarantine'} for part in Path(entry['source_path']).parts):
        raise SystemExit('recursive population leak')
    data=subprocess.check_output(['git','-C',str(root),'cat-file','blob',entry['blob_oid']])
    if hashlib.sha256(data).hexdigest()!=entry['sha256'] or len(data)!=entry['byte_length']:
        raise SystemExit('typed object identity mismatch')
    if subprocess.check_output(['git','-C',str(root),'cat-file','-t',entry['blob_oid']],text=True).strip()!='blob':
        raise SystemExit('archive entry is not a blob')
    draft_path=draft_dir/entry['draft_path']
    if f"{stat.S_IMODE(os.lstat(draft_path).st_mode):04o}" != entry['mode']:
        raise SystemExit('draft permission readback mismatch')
PY

negative="$tmp/negative"
mkdir -p "$negative"
make_clean_root "$negative"
negative_run="$negative/.IMPLEMENTAUDIT/runs/run-f2"
python - "$negative_run/archive-population.json" <<'PY'
import json,sys
from pathlib import Path
path=Path(sys.argv[1]); data=json.loads(path.read_text(encoding='utf-8'))
data['protected_files'][0]['path']='../STATE.md'
path.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
PY
if python "$helper" draft --repo-root "$negative" --run-root "$negative_run" \
    --controller v0333-release --generation g0008 \
    --manifest "$negative_run/archive-population.json" >"$tmp/traversal.out" 2>&1; then
  fail 'path traversal reached the draft writer'
fi
grep -Fq 'unsafe protected path: ../STATE.md' "$tmp/traversal.out" \
  || fail 'path traversal did not fail with the bounded diagnostic'

mkdir -p "$negative_run/STATE-GENERATIONS"
printf 'recursive preimage\n' >"$negative_run/STATE-GENERATIONS/STATE.md"
python - "$negative_run/archive-population.json" "$f2_fixture" <<'PY'
import json,sys
from pathlib import Path
path,fixture=map(Path,sys.argv[1:])
data=json.loads(fixture.read_text(encoding='utf-8'))
data['protected_files'][0]['path']='STATE-GENERATIONS/STATE.md'
path.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
PY
if python "$helper" draft --repo-root "$negative" --run-root "$negative_run" \
    --controller v0333-release --generation g0008 \
    --manifest "$negative_run/archive-population.json" >"$tmp/recursive-case.out" 2>&1; then
  fail 'case-aliased recursive population reached the draft writer'
fi
grep -Fq 'unsafe protected path: STATE-GENERATIONS/STATE.md' "$tmp/recursive-case.out" \
  || fail 'case-aliased recursive population lacked the bounded diagnostic'

tampered="$tmp/tampered-draft"
mkdir -p "$tampered"
make_clean_root "$tampered"
tampered_run="$tampered/.IMPLEMENTAUDIT/runs/run-f2"
python "$helper" draft --repo-root "$tampered" --run-root "$tampered_run" \
  --controller v0333-release --generation g0008 \
  --manifest "$tampered_run/archive-population.json" >/dev/null
tampered_draft="$tampered_run/state-generations/g0008/draft"
python - "$tampered_draft/draft-manifest.json" <<'PY'
import json,sys
from pathlib import Path
path=Path(sys.argv[1]); data=json.loads(path.read_text(encoding='utf-8'))
data['entries'][0]['source_path']='state-archives/recursive/STATE.md'
path.write_bytes((json.dumps(data,sort_keys=True,separators=(',',':'))+'\n').encode('utf-8'))
PY
if python "$helper" archive --repo-root "$tampered" --run-root "$tampered_run" \
    --controller v0333-release --generation g0008 \
    --draft-dir "$tampered_draft" >"$tmp/tampered-draft.out" 2>&1; then
  fail 'recursive source-path mutation reached the archive writer'
fi
grep -Fq 'unsafe protected path: state-archives/recursive/STATE.md' "$tmp/tampered-draft.out" \
  || fail 'recursive source-path mutation lacked the bounded diagnostic'

cp "$f2_fixture" "$negative_run/archive-population.json"
python - "$negative_run/STATE.md" <<'PY'
import os,stat,sys
os.chmod(sys.argv[1],stat.S_IREAD)
PY
if python "$helper" draft --repo-root "$negative" --run-root "$negative_run" \
    --controller v0333-release --generation g0008 \
    --manifest "$negative_run/archive-population.json" >"$tmp/permission.out" 2>&1; then
  fail 'read-only protected input reached the draft writer'
fi
grep -Fq 'unsafe permissions for protected file: STATE.md' "$tmp/permission.out" \
  || fail 'permission mutation did not fail with the bounded diagnostic'

cp "$f2_fixture" "$negative_run/archive-population.json"
reparse_kind="$(python - "$negative_run" <<'PY'
import os,subprocess,sys
from pathlib import Path
root=Path(sys.argv[1]); outside=root.parent.parent.parent/'reparse-outside'; alias=root/'alias'
outside.mkdir(); (outside/'STATE.md').write_text('outside\n',encoding='utf-8')
try:
    os.symlink(outside,alias,target_is_directory=True)
    print('symlink')
except OSError:
    result=subprocess.run(
        ['cmd.exe','/d','/c','mklink','/J',str(alias),str(outside)],
        stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=False,
    )
    if result.returncode:
        raise SystemExit('could not create a symlink or reparse-point control')
    print('reparse-junction')
PY
)"
python - "$negative_run/archive-population.json" <<'PY'
import json,sys
from pathlib import Path
path=Path(sys.argv[1]); data=json.loads(path.read_text(encoding='utf-8'))
data['protected_files'][0]['path']='alias/STATE.md'
path.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
PY
set +e
python "$helper" draft --repo-root "$negative" --run-root "$negative_run" \
  --controller v0333-release --generation g0008 \
  --manifest "$negative_run/archive-population.json" >"$tmp/reparse.out" 2>&1
reparse_rc=$?
set -e
python - "$negative_run/alias" <<'PY'
import os,sys
from pathlib import Path
path=Path(sys.argv[1])
if path.is_symlink():
    path.unlink()
elif path.exists():
    os.rmdir(path)
PY
[ "$reparse_rc" -ne 0 ] || fail "$reparse_kind path reached the draft writer"
grep -Fq 'directory custody contains a symlink or reparse point' "$tmp/reparse.out" \
  || fail "$reparse_kind path did not fail with the bounded diagnostic"

python - "$helper" <<'PY' \
  || fail 'Windows reparse-point detector did not reject the held-out attribute'
import importlib.util,sys
from types import SimpleNamespace
spec=importlib.util.spec_from_file_location('rotation_helper',sys.argv[1])
module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
if not module.is_reparse(SimpleNamespace(st_file_attributes=0x400)):
    raise SystemExit('reparse bit accepted')
PY

printf '%s\n' \
  'CANONICAL_STATE_ROTATION_F2_GREEN=PASS draft=BYTE_IDENTICAL archive=BYTE_IDENTICAL typed-retrieval=PASS archive-ref=EXPECTED_ZERO_CAS discovery=EXCLUDED recursive-population=EXCLUDED path=REJECTED symlink-reparse=REJECTED permissions=EXACT_READBACK'

after_shared_refs="$(git -C "$repo_root" for-each-ref --format='%(refname) %(objectname)' \
  refs/implementaudit/current-generations/ \
  refs/implementaudit/current-generation-migrations/ \
  refs/implementaudit/continuity-invalidations/ \
  refs/implementaudit/continuity-receipts/ \
  refs/implementaudit/state-archives/)"
[ "$before_shared_refs" = "$after_shared_refs" ] \
  || fail 'F2 test mutated a shared protected Git-ref namespace'

if $f2_only; then
  exit 0
fi

set +e
bash "$checker" --assert-f2-residual-red >"$tmp/f2-red.out" 2>&1
f2_red_rc=$?
set -e
[ "$f2_red_rc" -eq 1 ] \
  || fail "F2 residual oracle exited $f2_red_rc instead of semantic RED 1"

grep -Fq 'CANONICAL_STATE_ROTATION_RED=F2_DRAFT_ARCHIVE_ONLY_NOT_EQUIVALENT semantic-failures=44 preserved-payload=49/49 missing-equivalence=transition,pointer+marker+v3,rehydration' "$tmp/f2-red.out" \
  || fail 'F2 residual did not preserve the exact later-cell semantic RED'
for anchor in \
  'M01-generation-successor:semantic-mutation' \
  'D05-pointer-ref:semantic-mutation' \
  'D23-rehydrate-identity:semantic-mutation'; do
  grep -Fq "$anchor" "$tmp/f2-red.out" || fail "F2 residual RED omitted anchor $anchor"
done
if grep -Fq 'A01-state-preimage:semantic-mutation' "$tmp/f2-red.out"; then
  fail 'F2 residual still reports the completed draft/archive slice RED'
fi

cat "$tmp/f2-red.out" >&2
printf '%s\n' \
  'canonical-state-rotation.test: INTENDED_RED later F3-F7 currentness transaction remains absent' >&2
exit 1
