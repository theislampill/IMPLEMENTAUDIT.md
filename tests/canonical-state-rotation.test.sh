#!/usr/bin/env bash
# R0039 F1 is an immutable, nonmergeable semantic RED checkpoint.
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
checker="$repo_root/scripts/check-canonical-state-rotation.sh"
helper="$repo_root/skills/implementaudit/scripts/rotate-canonical-state.py"
claim_helper="$repo_root/skills/implementaudit/scripts/claim-run.sh"
f2_fixture="$repo_root/fixtures/canonical-state-rotation/f2-draft-archive.json"
f3_fixture="$repo_root/fixtures/canonical-state-rotation/f3-reader-matrix.json"
tmp="$(mktemp -d)"
trap 'rm -rf -- "$tmp"' EXIT

fail() { printf 'canonical-state-rotation.test: %s\n' "$*" >&2; exit 2; }

case "${1:-}" in
  '') f2_only=false; f3_only=false; clarifications_only=false ;;
  --clarifications-only) f2_only=false; f3_only=false; clarifications_only=true ;;
  --f2-only) f2_only=true; f3_only=false; clarifications_only=false ;;
  --f3-only) f2_only=false; f3_only=true; clarifications_only=false ;;
  *) fail "usage: canonical-state-rotation.test.sh [--clarifications-only|--f2-only|--f3-only]" ;;
esac

[ -f "$checker" ] || fail "missing root checker: $checker"
bash -n "$checker" || fail "checker syntax is invalid"
if $clarifications_only; then
  # Catches production that omits event-byte canonicalization, bound cursors,
  # or sequence-CAS isolation despite an apparently valid reader migration.
  bash "$checker" --clarification-fixtures-self-check >/dev/null
  printf '%s\n' \
    'CANONICAL_STATE_ROTATION_CLARIFICATIONS_RED=EVENT_BYTES_CURSOR_SEQUENCE_CAS_NOT_IMPLEMENTED' >&2
  exit 1
fi
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

[ -f "$f3_fixture" ] || fail "missing F3 fixture: $f3_fixture"
[ -f "$claim_helper" ] || fail "missing claim reader owner: $claim_helper"
bash "$checker" --f3-fixture-self-check

matrix_repo="$tmp/matrix-repo"
mkdir -p "$matrix_repo"
git -C "$matrix_repo" init -q
git -C "$matrix_repo" config user.name 'reader matrix fixture'
git -C "$matrix_repo" config user.email 'reader-matrix@example.invalid'
printf 'reader matrix\n' >"$matrix_repo/product.txt"
git -C "$matrix_repo" add product.txt
GIT_AUTHOR_DATE='2000-01-01T00:00:00Z' \
  GIT_COMMITTER_DATE='2000-01-01T00:00:00Z' \
  git -C "$matrix_repo" -c commit.gpgsign=false commit -qm preimage
matrix_rel="$(cd "$matrix_repo" && IMPLEMENTAUDIT_BASE=.IMPLEMENTAUDIT/runs \
  bash "$claim_helper" --controller reader-controller 'reader migration matrix')" \
  || fail 'F3 matrix controller claim failed'
matrix_root="$matrix_repo/$matrix_rel"
matrix_claim="$(sed -n 's/^claim_id=//p' "$matrix_root/.claimed")"
for file in STATE.md PROTOCOL.md ROADMAP.md THINKING.md sidecars.md tools.md context.md; do
  cp "$repo_root/skills/implementaudit/templates/$file" "$matrix_root/$file"
done
matrix_head="$(git -C "$matrix_repo" rev-parse HEAD)"
matrix_tree="$(git -C "$matrix_repo" rev-parse 'HEAD^{tree}')"
python - "$matrix_root/STATE.md" "$matrix_rel" "$matrix_head" "$matrix_tree" <<'PY'
import sys
from pathlib import Path
path=Path(sys.argv[1]); run,head,tree=sys.argv[2:]
text=path.read_text(encoding='utf-8')
text=text.replace('| Run root |  |',f'| Run root | `{run}` |')
text=text.replace('| Next action |  |','| Next action | exercise the complete reader migration matrix |')
anchor='| Epoch | Boundary provenance | Established at | Repo identity | Reconciled | Notes |\n|---|---|---|---|---|---|'
row=f'| G0001 | new-session | 2000-01-01T00:00:00Z | repo at `{head}` / `{tree}` | yes | exact legacy reader fixture |'
path.write_text(text.replace(anchor,anchor+'\n'+row),encoding='utf-8')
PY
legacy_token="$(cd "$matrix_repo" && bash "$claim_helper" --resume-controller \
  reader-controller --boundary new-session --epoch G0001)" \
  || fail 'F3 matrix could not mint its isolated exact-v2 control'
legacy_token_base="$legacy_token"
legacy_ref="${legacy_token%@*}"
legacy_oid="${legacy_token##*@}"
controller_oid="$(git -C "$matrix_repo" rev-parse refs/implementaudit/controllers/reader-controller)"
legacy_v1_oid="$(printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
  implementaudit.continuity-receipt.v1 reader-controller "$controller_oid" "$matrix_claim" \
  "$matrix_head" "$matrix_tree" \
  "$(sha256sum "$matrix_root/STATE.md" | cut -d' ' -f1)" \
  "$(sha256sum "$matrix_root/ROADMAP.md" | cut -d' ' -f1)" \
  | git -C "$matrix_repo" hash-object -w --stdin)"
run_identity="$matrix_rel"
pointer_ref='refs/implementaudit/current-generations/reader-controller'
marker_ref='refs/implementaudit/current-generation-migrations/reader-controller'
v3_ref='refs/implementaudit/continuity-receipts/reader-controller/G0002'
invalidation_ref='refs/implementaudit/continuity-invalidations/reader-controller'
state_pristine="$tmp/matrix-state-pristine.md"
cp "$matrix_root/STATE.md" "$state_pristine"
invalidation_oid='1111111111111111111111111111111111111111'
state_sha='2222222222222222222222222222222222222222222222222222222222222222'
roadmap_sha='3333333333333333333333333333333333333333333333333333333333333333'
protected_sha='4444444444444444444444444444444444444444444444444444444444444444'
archive_sha='5555555555555555555555555555555555555555555555555555555555555555'
next_action='exercise the complete reader migration matrix'

# A current pointer must be tied to the actual run, rather than merely to a
# self-consistent synthetic tuple. Legacy cases deliberately retain no live
# invalidation and their original G0001 STATE.md.
prepare_live_tuple() {
  local generation="$1"
  cp "$state_pristine" "$matrix_root/STATE.md"
  git -C "$matrix_repo" update-ref -d "$invalidation_ref" >/dev/null 2>&1 || true
  invalidation_oid='1111111111111111111111111111111111111111'
  legacy_token="$legacy_token_base"
  next_action='exercise the complete reader migration matrix'
  if [ "$generation" = yes ]; then
    python - "$matrix_root/STATE.md" "$matrix_head" "$matrix_tree" <<'PY'
import sys
from pathlib import Path
p=Path(sys.argv[1]); head,tree=sys.argv[2:]
s=p.read_text(encoding='utf-8')
s=s.replace('Current epoch: G0001', 'Current epoch: G0002')
anchor=f'| G0001 | new-session | 2000-01-01T00:00:00Z | repo at `{head}` / `{tree}` | yes | exact legacy reader fixture |'
row=f'| G0002 | inferred-context-gap | 2000-01-01T00:01:00Z | repo at `{head}` / `{tree}` | yes | current generation reader fixture |'
p.write_text(s.replace(anchor, anchor+'\n'+row), encoding='utf-8')
PY
    invalidation_token="$(cd "$matrix_repo" && bash "$claim_helper" --invalidate-continuity \
      reader-controller --boundary inferred-context-gap --event reader-matrix-g0002)" \
      || fail 'F3 matrix could not mint its isolated live invalidation'
    invalidation_oid="${invalidation_token##*@}"
  fi
  state_sha="$(sha256sum "$matrix_root/STATE.md" | cut -d' ' -f1)"
  roadmap_sha="$(sha256sum "$matrix_root/ROADMAP.md" | cut -d' ' -f1)"
}

make_matrix_objects() {
  local mutation="$1" object_controller=reader-controller object_claim="$matrix_claim"
  local object_run="$run_identity" pointer_schema=implementaudit.current-generation.v1
  local marker_schema=implementaudit.current-generation-migration.v1
  local receipt_schema=implementaudit.continuity-receipt.v3
  case "$mutation" in
    none) ;;
    controller) object_controller=other-controller ;;
    claim) object_claim=other-claim ;;
    run) object_run=.IMPLEMENTAUDIT/runs/other-run ;;
    pointer-schema) pointer_schema=implementaudit.current-generation.v0 ;;
    marker-schema) marker_schema=implementaudit.current-generation-migration.v0 ;;
    receipt-schema) receipt_schema=implementaudit.continuity-receipt.v2 ;;
    live-invalidation) invalidation_oid=9999999999999999999999999999999999999999 ;;
    live-state-hash) state_sha=aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa ;;
    live-roadmap-hash) roadmap_sha=bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb ;;
    live-next-action) next_action='stale reader action' ;;
    predecessor-ref) legacy_token="refs/implementaudit/continuity-receipts/reader-controller/G00FF@$legacy_oid" ;;
    predecessor-oid) legacy_token="$legacy_ref@0000000000000000000000000000000000000000" ;;
    *) fail "unknown F3 owner mutation: $mutation" ;;
  esac
  pointer_oid="$(printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
    "$pointer_schema" "$object_controller" "$object_claim" "$object_run" g0008 G0002 \
    "$invalidation_oid" "$legacy_token" "$v3_ref" implementaudit.canonical-state-projection.v1 \
    "$state_sha" "$roadmap_sha" "$protected_sha" "$archive_sha" "$next_action" \
    | git -C "$matrix_repo" hash-object -w --stdin)"
  v3_oid="$(printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
    "$receipt_schema" "$object_controller" "$object_claim" "$object_run" G0002 \
    "$invalidation_oid" "$pointer_ref" "$pointer_oid" "$state_sha" "$roadmap_sha" \
    "$protected_sha" "$archive_sha" "$next_action" "$legacy_token" \
    | git -C "$matrix_repo" hash-object -w --stdin)"
  marker_oid="$(printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
    "$marker_schema" "$object_controller" "$object_claim" "$object_run" G0002 \
    "$pointer_ref" implementaudit.current-generation.v1 "$v3_ref" "$v3_oid" true \
    | git -C "$matrix_repo" hash-object -w --stdin)"
  malformed_oid="$(printf 'malformed\n' | git -C "$matrix_repo" hash-object -w --stdin)"
  stale_v3_oid="$(printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
    implementaudit.continuity-receipt.v3 reader-controller "$matrix_claim" "$run_identity" G0002 \
    "$invalidation_oid" "$pointer_ref" 9999999999999999999999999999999999999999 \
    "$state_sha" "$roadmap_sha" "$protected_sha" "$archive_sha" "$next_action" "$legacy_token" \
    | git -C "$matrix_repo" hash-object -w --stdin)"
  mismatch_v3_oid="$(printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
    implementaudit.continuity-receipt.v3 reader-controller other-claim "$run_identity" G0002 \
    "$invalidation_oid" "$pointer_ref" "$pointer_oid" "$state_sha" "$roadmap_sha" \
    "$protected_sha" "$archive_sha" "$next_action" "$legacy_token" \
    | git -C "$matrix_repo" hash-object -w --stdin)"
  invalidated_v2_oid="$(git -C "$matrix_repo" cat-file blob "$legacy_oid" \
    | sed $'s/\tnone\tnew-session\t/\t8888888888888888888888888888888888888888\tnew-session\t/' \
    | git -C "$matrix_repo" hash-object -w --stdin)"
  mismatched_v2_oid="$(git -C "$matrix_repo" cat-file blob "$legacy_oid" \
    | sed $'s/\t'$matrix_claim$'\t/\tother-claim\t/' \
    | git -C "$matrix_repo" hash-object -w --stdin)"
}

matrix_cases="$(python - "$f3_fixture" <<'PY'
import json,sys
for row in json.load(open(sys.argv[1],encoding='utf-8'))['cases']:
    print('\t'.join(str(row[key]) for key in ('id','marker','pointer','receipt','owner_mutation','expected')))
PY
)"
matrix_pass=0
while IFS=$'\t' read -r case_id marker_state pointer_state receipt_state mutation expected; do
  [ -n "$case_id" ] || continue
  expected="${expected%$'\r'}"
  if [ "$pointer_state" = valid ]; then prepare_live_tuple yes; else prepare_live_tuple no; fi
  make_matrix_objects "$mutation"
  git -C "$matrix_repo" update-ref -d "$pointer_ref" >/dev/null 2>&1 || true
  git -C "$matrix_repo" update-ref -d "$marker_ref" >/dev/null 2>&1 || true
  git -C "$matrix_repo" update-ref -d "$legacy_ref" >/dev/null 2>&1 || true
  git -C "$matrix_repo" update-ref -d "$v3_ref" >/dev/null 2>&1 || true
  [ "$pointer_state" != valid ] || git -C "$matrix_repo" update-ref "$legacy_ref" "$legacy_oid"
  case "$pointer_state" in
    absent) ;;
    valid) git -C "$matrix_repo" update-ref "$pointer_ref" "$pointer_oid" ;;
    malformed) git -C "$matrix_repo" update-ref "$pointer_ref" "$malformed_oid" ;;
  esac
  case "$receipt_state" in
    absent) current_token='' ;;
    exact-v1) git -C "$matrix_repo" update-ref "$legacy_ref" "$legacy_v1_oid"; current_token="$legacy_ref@$legacy_v1_oid" ;;
    exact-v2) git -C "$matrix_repo" update-ref "$legacy_ref" "$legacy_oid"; current_token="$legacy_token" ;;
    invalidated-v2) git -C "$matrix_repo" update-ref "$legacy_ref" "$invalidated_v2_oid"; current_token="$legacy_ref@$invalidated_v2_oid" ;;
    mismatched-v2) git -C "$matrix_repo" update-ref "$legacy_ref" "$mismatched_v2_oid"; current_token="$legacy_ref@$mismatched_v2_oid" ;;
    exact-v3) git -C "$matrix_repo" update-ref "$v3_ref" "$v3_oid"; current_token="$v3_ref@$v3_oid" ;;
    stale-v3) git -C "$matrix_repo" update-ref "$v3_ref" "$stale_v3_oid"; current_token="$v3_ref@$stale_v3_oid" ;;
    mismatched-v3) git -C "$matrix_repo" update-ref "$v3_ref" "$mismatch_v3_oid"; current_token="$v3_ref@$mismatch_v3_oid" ;;
  esac
  case "$marker_state" in
    absent) ;;
    valid) git -C "$matrix_repo" update-ref "$marker_ref" "$marker_oid" ;;
    malformed) git -C "$matrix_repo" update-ref "$marker_ref" "$malformed_oid" ;;
  esac
  set +e
  matrix_output="$(cd "$matrix_repo" && bash "$claim_helper" \
    --require-current-continuity reader-controller 2>&1)"
  matrix_rc=$?
  set -e
  matrix_actual=STOP
  if [ "$matrix_rc" -eq 0 ] && [ "$matrix_output" = "$legacy_token" ]; then
    matrix_actual=LEGACY_COMPATIBILITY
  elif [ "$matrix_rc" -eq 0 ] && [ "$matrix_output" = "$current_token" ]; then
    matrix_actual=POINTER_CURRENT
  elif grep -Fq 'FIRST_MIGRATION_INCOMPLETE' <<<"$matrix_output"; then
    matrix_actual=FIRST_MIGRATION_INCOMPLETE
  elif grep -Fq 'STOP_NO_ROOT_FALLBACK' <<<"$matrix_output"; then
    matrix_actual=STOP_NO_ROOT_FALLBACK
  fi
  if [ "$matrix_actual" != "$expected" ]; then
    printf '%s\n' "CANONICAL_STATE_ROTATION_F3_RED=READER_MATRIX_NOT_ENFORCED case=$case_id expected=$expected actual=$matrix_actual" >&2
    exit 1
  fi
  matrix_pass=$((matrix_pass + 1))
done <<<"$matrix_cases"
[ "$matrix_pass" -eq 24 ] || fail "F3 matrix executed $matrix_pass cases instead of 24"

# Held-out live binding negatives. Each begins from a real current G0002
# tuple; a reader that validates only pointer/v3/marker self-consistency would
# incorrectly accept these mutations.
install_held_out_current() {
  prepare_live_tuple yes
  make_matrix_objects none
  git -C "$matrix_repo" update-ref "$legacy_ref" "$legacy_oid"
  git -C "$matrix_repo" update-ref "$pointer_ref" "$pointer_oid"
  git -C "$matrix_repo" update-ref "$v3_ref" "$v3_oid"
  git -C "$matrix_repo" update-ref "$marker_ref" "$marker_oid"
}

assert_held_out_stop() {
  local label="$1" marker_message="${2:-no}"
  local out rc
  set +e
  out="$(cd "$matrix_repo" && bash "$claim_helper" --require-current-continuity reader-controller 2>&1)"
  rc=$?
  set -e
  [ "$rc" -ne 0 ] || fail "held-out $label incorrectly accepted a stale generation tuple"
  if [ "$marker_message" = yes ]; then
    grep -Fq STOP_NO_ROOT_FALLBACK <<<"$out" || fail "held-out $label did not forbid root fallback"
  fi
}

held_out_pass=0
for mutation in live-invalidation live-state-hash live-roadmap-hash live-next-action predecessor-ref predecessor-oid; do
  install_held_out_current
  make_matrix_objects "$mutation"
  git -C "$matrix_repo" update-ref "$pointer_ref" "$pointer_oid"
  git -C "$matrix_repo" update-ref "$v3_ref" "$v3_oid"
  git -C "$matrix_repo" update-ref "$marker_ref" "$marker_oid"
  assert_held_out_stop "$mutation"
  held_out_pass=$((held_out_pass + 1))
done

install_held_out_current
pointer_path="$(git -C "$matrix_repo" rev-parse --path-format=absolute --git-path "$pointer_ref")"
rm -f -- "$pointer_path"
mkdir -p "$(dirname "$pointer_path")"
printf 'not-an-object-id\n' >"$pointer_path"
assert_held_out_stop broken-pointer-ref yes
rm -f -- "$pointer_path"
held_out_pass=$((held_out_pass + 1))

install_held_out_current
marker_path="$(git -C "$matrix_repo" rev-parse --path-format=absolute --git-path "$marker_ref")"
rm -f -- "$marker_path"
mkdir -p "$(dirname "$marker_path")"
printf 'not-an-object-id\n' >"$marker_path"
assert_held_out_stop broken-marker-ref yes
rm -f -- "$marker_path"
held_out_pass=$((held_out_pass + 1))

[ "$held_out_pass" -eq 8 ] || fail "F3 held-out reader negatives executed $held_out_pass cases instead of 8"
printf '%s\n' \
  'CANONICAL_STATE_ROTATION_F3_HELD_OUT_GREEN=PASS cases=8 live=invalidation,state,roadmap,next-action,predecessor-ref,predecessor-oid broken-refs=pointer,marker'

printf '%s\n' \
  'CANONICAL_STATE_ROTATION_F3_GREEN=PASS matrix=24/24 legacy=EXACT_V2_ONLY first-migration=STOP pointer-current=MARKER_POINTER_V3_JOIN marker-fallback=FORBIDDEN owner-schema-mismatch=REJECTED refs=READ_ONLY'

after_f3_shared_refs="$(git -C "$repo_root" for-each-ref --format='%(refname) %(objectname)' \
  refs/implementaudit/current-generations/ \
  refs/implementaudit/current-generation-migrations/ \
  refs/implementaudit/continuity-invalidations/ \
  refs/implementaudit/continuity-receipts/ \
  refs/implementaudit/state-archives/)"
[ "$before_shared_refs" = "$after_f3_shared_refs" ] \
  || fail 'F3 reader matrix mutated a shared protected Git-ref namespace'

if $f3_only; then
  exit 0
fi

set +e
bash "$checker" --assert-f3-residual-red >"$tmp/f3-red.out" 2>&1
f3_red_rc=$?
set -e
[ "$f3_red_rc" -eq 1 ] \
  || fail "F3 residual oracle exited $f3_red_rc instead of semantic RED 1"

grep -Fq 'CANONICAL_STATE_ROTATION_RED=F3_READERS_ONLY_NOT_EQUIVALENT semantic-failures=37 preserved-payload=49/49 missing-equivalence=transition,pointer+marker+v3-publication,rehydration' "$tmp/f3-red.out" \
  || fail 'F3 residual did not preserve the exact later-cell semantic RED'
for anchor in \
  'M01-generation-successor:semantic-mutation' \
  'D05-pointer-ref:semantic-mutation' \
  'D23-rehydrate-identity:semantic-mutation'; do
  grep -Fq "$anchor" "$tmp/f3-red.out" || fail "F3 residual RED omitted anchor $anchor"
done
if grep -Eq '(^|,)(A|D1[5-9]|D2[0-2])[0-9-]' "$tmp/f3-red.out"; then
  fail 'F3 residual still reports a completed archive or reader-matrix slice RED'
fi

cat "$tmp/f3-red.out" >&2
printf '%s\n' \
  'canonical-state-rotation.test: INTENDED_RED later F4-F7 currentness transaction remains absent' >&2
exit 1
