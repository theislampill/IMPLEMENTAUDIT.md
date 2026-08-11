#!/usr/bin/env bash
# R36 black-box state-family acceptance.  No production implementation is
# present at this checkpoint; --fixture-self-check and --mutant-self-check keep
# this test honest before the canonical helper exists.
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
canonical_helper="$repo_root/skills/implementaudit/scripts/apply-observed-mutation.sh"
helper="$canonical_helper"
if [ -n "${PYTHON:-}" ]; then python_bin="$PYTHON"
elif command -v python >/dev/null 2>&1; then python_bin=python
elif command -v python3 >/dev/null 2>&1; then python_bin=python3
else printf 'observation-bound-mutation-integrity: Python is required\n' >&2; exit 1; fi
tmp="$(mktemp -d)"
trap 'rm -rf -- "$tmp"' EXIT
fixture_repo="$tmp/repository"
run_root="$fixture_repo/.IMPLEMENTAUDIT/r36"
outside="$tmp/existing-outside-target"

fail() { printf 'observation-bound-mutation-integrity: %s\n' "$*" >&2; exit 1; }
status_exit() { case "$1" in COMMITTED|NO_CHANGE) echo 0;; REJECTED_NO_MUTATION) echo 64;; CONFLICT_REBASE) echo 65;; MUTATION_FAILED_NO_STATE_CHANGE) echo 70;; MUTATION_FAILED_ROLLED_BACK) echo 71;; POST_STATE_MISMATCH_ROLLED_BACK) echo 72;; RECOVERY_REQUIRED) echo 73;; ROLLBACK_CONFLICT) echo 74;; ROLLBACK_FAILED_WITH_RESIDUE) echo 75;; POST_COMMIT_DRIFT) echo 76;; UNSUPPORTED_OWNER_DECISION) echo 77;; *) fail "unknown status $1";; esac; }
wait_bounded() { local pid="$1" label="$2" ticks=0; while kill -0 "$pid" 2>/dev/null && [ "$ticks" -lt 500 ]; do sleep .02; ticks=$((ticks+1)); done; if kill -0 "$pid" 2>/dev/null; then kill "$pid" 2>/dev/null || true; wait "$pid" 2>/dev/null || true; fail "$label timed out"; fi; wait "$pid" || true; }

write_hex() { "$python_bin" - "$1" "$2" <<'PY'
import sys
from pathlib import Path
p=Path(sys.argv[1]); p.parent.mkdir(parents=True,exist_ok=True); p.write_bytes(bytes.fromhex(sys.argv[2]))
PY
}
assert_hex() { "$python_bin" - "$1" "$2" "$3" <<'PY'
import os,stat,sys
from pathlib import Path
label,path,want=sys.argv[1:]
if want == '@DIRECTORY':
 if not Path(path).is_dir(): raise SystemExit(f'{label}: expected a retained directory')
 raise SystemExit(0)
if want == '@SYMLINK_PATH':
 p=Path(path)
 if not any(q.is_symlink() for q in (p,*p.parents)): raise SystemExit(f'{label}: expected final or ancestor symlink')
 raise SystemExit(0)
p=Path(path)
try: mode=p.lstat().st_mode
except FileNotFoundError: mode=None
got=p.read_bytes() if mode is not None and stat.S_ISREG(mode) else None
expected=bytes.fromhex(want) if want != '-' else None
if got != expected: raise SystemExit(f'{label}: got={got!r} want={expected!r}')
PY
}
artifact() { local name="$1" hex="$2"; local p="$fixture_repo/artifacts/$name"; write_hex "$p" "$hex"; printf '%s\n' "$p"; }

setup() {
  rm -rf -- "$fixture_repo"
  mkdir -p "$fixture_repo/artifacts"
  run_root="$(cd "$fixture_repo" && IMPLEMENTAUDIT_BASE=.IMPLEMENTAUDIT/runs bash "$repo_root/skills/implementaudit/scripts/claim-run.sh" 'r36-observation-bound-mutation')"
  run_root="$fixture_repo/$run_root"
  write_hex "$fixture_repo/target" 4142434445
  write_hex "$fixture_repo/a" 41; write_hex "$fixture_repo/b" 42
  write_hex "$fixture_repo/equal-one" 53414d45; write_hex "$fixture_repo/equal-two" 53414d45
  write_hex "$fixture_repo/sibling" 5349424c494e47; ln "$fixture_repo/sibling" "$fixture_repo/hardlink"
  write_hex "$fixture_repo/crlf" 6f6e650d0a74776f0d0a74687265650d0a
  write_hex "$fixture_repo/unicode" 7072656669782de282ac2de4b8ade696872d737566666978
  write_hex "$fixture_repo/binary" 0001ff7f42494e0d0a
  write_hex "$outside" 4f555453494445
  "$python_bin" - "$fixture_repo" <<'PY'
import os,sys
from pathlib import Path
r=Path(sys.argv[1])
try:
 os.symlink('target',r/'final-link'); (r/'real').mkdir(); (r/'real'/'child').write_bytes(b'child'); os.symlink('real',r/'parent-link',target_is_directory=True); (r/'symlink-capability').write_text('yes')
except OSError: (r/'symlink-capability').write_text('no')
PY
}
fixture_self_check() {
  setup
  "$python_bin" - "$fixture_repo" <<'PY'
import os,sys
from pathlib import Path
r=Path(sys.argv[1])
assert (r/'target').read_bytes()==b'ABCDE'
assert (r/'crlf').read_bytes()==b'one\r\ntwo\r\nthree\r\n'
assert (r/'unicode').read_bytes()=='prefix-€-中文-suffix'.encode()
assert (r/'binary').read_bytes()==b'\0\1\xff\x7fBIN\r\n'
assert os.stat(r/'sibling').st_ino==os.stat(r/'hardlink').st_ino
claim=(r/'.IMPLEMENTAUDIT'/'runs')
assert len(list(claim.glob('r36-observation-bound-mutation-*/.claimed')))==1
print('R36_FIXTURE_SELF_CHECK=PASS bytes=raw topology=hardlink,symlink-or-declared-unsupported')
PY
}

# The fault/rendezvous driver is mechanically derived from the authoritative
# helper.  Production contains only inert structural hook markers; this copy
# receives test-only code by insertion and is never installed or packaged.
instrumented_helper() {
  local derived="$tmp/instrumented-apply-observed-mutation.sh"
  "$python_bin" - "$canonical_helper" "$derived" <<'PY' || return 1
import sys
from pathlib import Path
source=Path(sys.argv[1]).read_text(encoding='utf-8')
needle='    # R36_INSTRUMENT_INSERT\n'
if source.count(needle) != 1: raise SystemExit('R36 instrument marker count is not exactly one')
insert="""    # test-only insertion: absent from authoritative helper after strip\n    global bar,fault\n    if phase == 'init':\n        import os\n        bar=os.getenv('IMPLEMENTAUDIT_R36_TEST_BARRIER_DIR')\n        fault=os.getenv('IMPLEMENTAUDIT_R36_TEST_FAULT_STAGE')\n"""
Path(sys.argv[2]).write_text(source.replace(needle,needle+insert),encoding='utf-8')
PY
  chmod +x "$derived" || return 1
  "$python_bin" - "$canonical_helper" "$derived" <<'PY' || return 1
import sys
from pathlib import Path
canonical,derived=map(Path,sys.argv[1:]); text=derived.read_text(encoding='utf-8')
insert="""    # test-only insertion: absent from authoritative helper after strip\n    global bar,fault\n    if phase == 'init':\n        import os\n        bar=os.getenv('IMPLEMENTAUDIT_R36_TEST_BARRIER_DIR')\n        fault=os.getenv('IMPLEMENTAUDIT_R36_TEST_FAULT_STAGE')\n"""
if text.replace(insert,'') != canonical.read_text(encoding='utf-8'): raise SystemExit('instrumented copy does not strip byte-equal')
PY
  printf '%s\n' "$derived"
}

identity_json() { "$python_bin" - "$1" <<'PY'
import hashlib,json,stat,sys
from pathlib import Path
p=Path(sys.argv[1])
try:
 unsafe=any(q.is_symlink() for q in (p,*p.parents))
 mode=p.lstat().st_mode
except FileNotFoundError: unsafe=True; mode=0
if unsafe or not stat.S_ISREG(mode): print('null')
else:
 b=p.read_bytes(); print(json.dumps({'sha256':hashlib.sha256(b).hexdigest(),'byte_length':len(b)},separators=(',',':')))
PY
}
post_identities_json() { "$python_bin" - "$fixture_repo" "$1" "$2" <<'PY'
import json,stat,sys
from pathlib import Path
import hashlib
r,target,dest=map(str,sys.argv[1:])
def ident(path):
 p=Path(path)
 try:
  unsafe=any(q.is_symlink() for q in (p,*p.parents)); mode=p.lstat().st_mode
 except FileNotFoundError: return None
 if unsafe or not stat.S_ISREG(mode): return None
 b=p.read_bytes(); return {'sha256':hashlib.sha256(b).hexdigest(),'byte_length':len(b)}
d={target:ident(Path(r)/target)}
if dest != '-': d[dest]=ident(Path(r)/dest)
print(json.dumps(d,separators=(',',':')))
PY
}
assert_response() { "$python_bin" - "$@" <<'PY'
import json,sys
label,status,operation,source,dest,targets,pre,candidate,post,post_identities,out=sys.argv[1:]
lines=[x for x in out.splitlines() if x.strip()]
if len(lines)!=1: raise SystemExit(f'{label}: expected one stdout JSON object, got {len(lines)}')
r=json.loads(lines[0]); required={'schema','operation','status','source_path','destination_path','targets','pre_identity','candidate_identity','post_identity','post_identities','token','journal_path','residue_paths'}
if set(r)!=required: raise SystemExit(f'{label}: schema keys differ: got={sorted(r)}')
want={'schema':'implementaudit.observation_bound_mutation.v1','operation':operation,'status':status,'source_path':source,'destination_path':None if dest=='-' else dest,'targets':json.loads(targets),'pre_identity':json.loads(pre),'candidate_identity':json.loads(candidate),'post_identity':json.loads(post),'post_identities':json.loads(post_identities)}
for k,v in want.items():
 if r[k]!=v: raise SystemExit(f'{label}: {k} got={r[k]!r} want={v!r}')
residual={'RECOVERY_REQUIRED','ROLLBACK_CONFLICT','ROLLBACK_FAILED_WITH_RESIDUE','POST_COMMIT_DRIFT'}
if status in residual:
 if not isinstance(r['token'],str) or not r['token'] or not isinstance(r['journal_path'],str) or not r['journal_path'] or not isinstance(r['residue_paths'],list) or not r['residue_paths'] or not all(isinstance(x,str) and x for x in r['residue_paths']): raise SystemExit(f'{label}: residual status lacks token/journal/residue')
else:
 if r['token'] is not None or r['journal_path'] is not None or r['residue_paths'] != []: raise SystemExit(f'{label}: non-residual status leaked recovery state')
print(json.dumps({'token':r['token'],'journal_path':r['journal_path'],'residue_paths':r['residue_paths']}))
PY
}

# invoke asserts independently expected bytes; it does not derive pass criteria
# from helper output.  Arguments: label status op target destination candidate-file expected-post-hex, then helper args.
invoke() {
  local label="$1" status="$2" op="$3" target="$4" dest="$5" candidate="$6" expected="$7"; shift 7
  local source_path="$fixture_repo/$target" post_path="$fixture_repo/$target"
  # A committed move publishes at destination. Every rejected/conflict move
  # must instead prove the original source survived unchanged; deletion proves
  # absence at its actual source path, never at a detached sentinel.
  [ "$op" = move ] && [ "$status" = "COMMITTED" ] && post_path="$fixture_repo/$dest"
  local pre candidate_id post post_identities targets expected_exit stdout stderr actual offset region replacement constructed fault_stage
  pre="$(identity_json "$source_path")"; candidate_id="$(identity_json "$candidate")"
  if [ "$op" = patch ]; then
    offset= region= replacement=
    local argv=("$@") i
    for ((i=0; i<${#argv[@]}; i++)); do case "${argv[$i]}" in --offset) offset="${argv[$((i+1))]}";; --region) region="${argv[$((i+1))]}";; --replacement) replacement="${argv[$((i+1))]}";; esac; done
    constructed="$tmp/$label.constructed"
    if "$python_bin" - "$source_path" "$offset" "$region" "$replacement" "$constructed" <<'PY'
import sys
from pathlib import Path
source,offset_text,region,replacement,out=sys.argv[1:]
try: offset=int(offset_text)
except ValueError: raise SystemExit(1)
current=Path(source).read_bytes(); observed=Path(region).read_bytes(); new=Path(replacement).read_bytes()
if offset < 0 or not observed or current[offset:offset+len(observed)] != observed: raise SystemExit(1)
Path(out).write_bytes(current[:offset]+new+current[offset+len(observed):])
PY
    then candidate_id="$(identity_json "$constructed")"; else candidate_id=null; fi
  fi
  if [ "$dest" = - ]; then targets="[\"$target\"]"; else targets="[\"$target\",\"$dest\"]"; fi
  expected_exit="$(status_exit "$status")"; stdout="$tmp/$label.out"; stderr="$tmp/$label.err"
  fault_stage="${IMPLEMENTAUDIT_R36_TEST_FAULT_STAGE:-}"
  set +e
  if [ -n "$fault_stage" ]; then IMPLEMENTAUDIT_R36_TEST_FAULT_STAGE="$fault_stage" bash "$helper" --repo-root "$fixture_repo" --run-root "$run_root" --operation "$op" --target "$target" "$@" >"$stdout" 2>"$stderr"; actual=$?
  else bash "$helper" --repo-root "$fixture_repo" --run-root "$run_root" --operation "$op" --target "$target" "$@" >"$stdout" 2>"$stderr"; actual=$?; fi
  set -e
  [ "$actual" -eq "$expected_exit" ] || fail "$label: exit=$actual expected=$expected_exit stderr=$(<"$stderr")"
  post="$(identity_json "$post_path")"; post_identities="$(post_identities_json "$target" "$dest")"
  last_record="$(assert_response "$label" "$status" "$op" "$target" "$dest" "$targets" "$pre" "$candidate_id" "$post" "$post_identities" "$(<"$stdout")")"
  assert_hex "$label visible state" "$post_path" "$expected"
}

# Test-only deterministic fault boundary.  The requested fault selects the
# injected failure, but it does not prove where it occurred: an independent
# observer reads the target while the call is paused.  The helper's only test
# synchronisation surface is a content-free `paused` file; it cannot satisfy
# the stage assertion by writing a claimed JSON outcome.
invoke_fault() {
  local stage="$1"; shift; local barrier="$tmp/fault-$stage" stdout="$tmp/fault-$stage.out" stderr="$tmp/fault-$stage.err" pid ticks=0 actual
  local label="$1" status="$2" op="$3" target="$4" dest="$5" candidate="$6" expected="$7" pre candidate_id post post_ids targets
  local canonical_saved="$helper" instrumented
  shift 7
  instrumented="$(instrumented_helper)"; helper="$instrumented"
  pre="$(identity_json "$fixture_repo/$target")"; candidate_id="$(identity_json "$candidate")"
  [ "$dest" = - ] && targets="[\"$target\"]" || targets="[\"$target\",\"$dest\"]"
  [ "$op" = patch ] && fail 'fault fixture only supports whole-file operations'
  rm -rf -- "$barrier"; mkdir "$barrier"
  # This actor is deliberately outside the helper process.  Its observations
  # (and, for mismatch/unsupported, its short owned write/restore transition)
  # are task evidence rather than helper-supplied fault claims.
  (set +e; IMPLEMENTAUDIT_R36_TEST_BARRIER_DIR="$barrier" IMPLEMENTAUDIT_R36_TEST_FAULT_STAGE="$stage" bash "$helper" --repo-root "$fixture_repo" --run-root "$run_root" --operation "$op" --target "$target" "$@" >"$stdout" 2>"$stderr"; echo $? >"$barrier/exit") & pid=$!
  while [ ! -f "$barrier/paused" ] && [ "$ticks" -lt 500 ]; do sleep .02; ticks=$((ticks+1)); done
  [ "$ticks" -lt 500 ] || { wait_bounded "$pid" "R36-$stage fault helper"; fail "R36-$stage did not pause for external stage observation"; }
  if [ "$stage" = after-publication ]; then
    "$python_bin" - "$fixture_repo/target" "$barrier/publication.snapshot" <<'PY'
import hashlib,json,sys
from pathlib import Path
b=Path(sys.argv[1]).read_bytes(); Path(sys.argv[2]).write_text(json.dumps({'published_sha256':hashlib.sha256(b).hexdigest(),'published_bytes':len(b)}),encoding='utf-8')
PY
  fi
  "$python_bin" - "$fixture_repo/target" "$barrier/observed.json" "$stage" <<'PY'
import hashlib,json,stat,sys
from pathlib import Path
p=Path(sys.argv[1]); out=Path(sys.argv[2]); stage=sys.argv[3]
try:
 mode=p.lstat().st_mode
 exists=stat.S_ISREG(mode)
 data=p.read_bytes() if exists else None
except FileNotFoundError:
 exists=False; data=None
record={'exists':exists,'sha256':None if data is None else hashlib.sha256(data).hexdigest(),'byte_length':None if data is None else len(data)}
out.write_text(json.dumps(record,sort_keys=True),encoding='utf-8')
PY
  # The post-mismatch and unsupported actors now retain their bytes throughout
  # release.  A helper which merely reads a caller label cannot pass: it must
  # observe the task-owned state before `continue-after-external` is granted.
  if [ "$stage" = post-state-mismatch ] || [ "$stage" = unsupported-external-writer ]; then
    "$python_bin" - "$fixture_repo/target" "$barrier/$stage.transition" "$barrier/$stage.before" "$stage" <<'PY'
import hashlib,json,sys
from pathlib import Path
t=Path(sys.argv[1]); out=Path(sys.argv[2]); saved=Path(sys.argv[3]); stage=sys.argv[4]
before=t.read_bytes(); injected=b'MISMATCH-ACTOR' if stage=='post-state-mismatch' else b'UNSUPPORTED-WRITER'
saved.write_bytes(before); t.write_bytes(injected); during=t.read_bytes()
out.write_text(json.dumps({'before_sha256':hashlib.sha256(before).hexdigest(),'during_sha256':hashlib.sha256(during).hexdigest(),'actor':stage},sort_keys=True),encoding='utf-8')
PY
    [ "$stage" != unsupported-external-writer ] || : >"$barrier/external-writer-created"
  fi
  : >"$barrier/release"
  if [ "$stage" = post-state-mismatch ] || [ "$stage" = unsupported-external-writer ]; then
    ticks=0; while [ ! -f "$barrier/observed-after-external" ] && kill -0 "$pid" 2>/dev/null && [ "$ticks" -lt 500 ]; do sleep .02; ticks=$((ticks+1)); done
    [ "$ticks" -lt 500 ] || { wait_bounded "$pid" "R36-$stage external observation"; fail "R36-$stage did not observe externally held state"; }
    "$python_bin" - "$fixture_repo/target" "$barrier/continuation.snapshot" <<'PY'
import hashlib,json,sys
from pathlib import Path
b=Path(sys.argv[1]).read_bytes(); Path(sys.argv[2]).write_text(json.dumps({'sha256':hashlib.sha256(b).hexdigest(),'byte_length':len(b)}),encoding='utf-8')
PY
    : >"$barrier/continue-after-external"
  fi
  wait_bounded "$pid" "R36-$stage fault helper"; actual="$(<"$barrier/exit")"
  [ "$actual" -eq "$(status_exit "$status")" ] || fail "R36-$stage exit=$actual expected $(status_exit "$status") stderr=$(<"$stderr")"
  post="$(identity_json "$fixture_repo/$target")"; post_ids="$(post_identities_json "$target" "$dest")"
  last_record="$(assert_response "$label" "$status" "$op" "$target" "$dest" "$targets" "$pre" "$candidate_id" "$post" "$post_ids" "$(<"$stdout")")"
  assert_hex "$label visible state" "$fixture_repo/$target" "$expected"
  "$python_bin" - "$barrier/observed.json" "$stage" <<'PY'
import json,sys
from pathlib import Path
record=json.loads(Path(sys.argv[1]).read_text(encoding='utf-8')); stage=sys.argv[2]
expected={
 'pre-displacement': {'exists': True, 'sha256': 'f0393febe8baaa55e32f7be2a7cc180bf34e52137d99e056c817a9c07b8f239a','byte_length':5},
 'after-displacement': {'exists': False, 'sha256': None,'byte_length':None},
 'after-publication': {'exists': True, 'sha256': 'a253ff09c5a8678e1fd1962b2c329245e139e45f9cc6ced4e5d7ad42c4108fc0','byte_length':3},
 'post-state-mismatch': {'exists': True, 'sha256': 'a253ff09c5a8678e1fd1962b2c329245e139e45f9cc6ced4e5d7ad42c4108fc0','byte_length':3},
 'unsupported-external-writer': {'exists': True, 'sha256': 'f0393febe8baaa55e32f7be2a7cc180bf34e52137d99e056c817a9c07b8f239a','byte_length':5},
}[stage]
if record != expected: raise SystemExit(f'fault stage observation mismatch: {record!r}')
PY
  if [ "$stage" = after-publication ]; then
    "$python_bin" - "$barrier/publication.snapshot" <<'PY'
import json,sys
r=json.loads(open(sys.argv[1],encoding='utf-8').read())
if r != {'published_sha256':'a253ff09c5a8678e1fd1962b2c329245e139e45f9cc6ced4e5d7ad42c4108fc0','published_bytes':3}: raise SystemExit(f'bad publication snapshot: {r!r}')
PY
  elif [ "$stage" = post-state-mismatch ] || [ "$stage" = unsupported-external-writer ]; then
    "$python_bin" - "$barrier/$stage.transition" "$stage" <<'PY'
import json,sys
r=json.loads(open(sys.argv[1],encoding='utf-8').read()); stage=sys.argv[2]
want_before='a253ff09c5a8678e1fd1962b2c329245e139e45f9cc6ced4e5d7ad42c4108fc0' if stage=='post-state-mismatch' else 'f0393febe8baaa55e32f7be2a7cc180bf34e52137d99e056c817a9c07b8f239a'
if r['actor'] != stage or r['before_sha256'] != want_before or r['during_sha256'] == want_before: raise SystemExit(f'bad externally-held transition: {r!r}')
PY
    # The continuation snapshot is made before the task grants the second
    # release gate.  If the helper exits instead, its terminal state above is
    # still checked exactly; either route proves the actor was not restored
    # before continuation became possible.
    if [ -f "$barrier/observed-after-external" ]; then
      "$python_bin" - "$barrier/continuation.snapshot" "$stage" <<'PY'
import hashlib,json,sys
r=json.loads(open(sys.argv[1],encoding='utf-8').read()); stage=sys.argv[2]
b=b'MISMATCH-ACTOR' if stage=='post-state-mismatch' else b'UNSUPPORTED-WRITER'
want={'sha256':hashlib.sha256(b).hexdigest(),'byte_length':len(b)}
if r != want: raise SystemExit(f'helper observation did not overlap injected state: {r!r}')
PY
    else
      [ -f "$barrier/exit" ] || fail "R36-$stage neither observed external state nor exited"
    fi
    "$python_bin" - "$fixture_repo/target" "$barrier/$stage.before" "$barrier/$stage.transition" "$stage" <<'PY'
import hashlib,json,sys
from pathlib import Path
t=Path(sys.argv[1]); saved=Path(sys.argv[2]); out=Path(sys.argv[3]); stage=sys.argv[4]
injected=b'MISMATCH-ACTOR' if stage=='post-state-mismatch' else b'UNSUPPORTED-WRITER'
current=t.read_bytes(); restored=current==injected
if restored: t.write_bytes(saved.read_bytes())
r=json.loads(out.read_text(encoding='utf-8')); r.update({'terminal_sha256':hashlib.sha256(current).hexdigest(),'actor_restored_after_exit':restored})
out.write_text(json.dumps(r,sort_keys=True),encoding='utf-8')
PY
    # Post-mismatch has already rolled back; unsupported deliberately leaves
    # the external writer's bytes alone until this task-owned cleanup.
    assert_hex "$label task-owned-actor-cleanup" "$fixture_repo/target" 4142434445
  fi
  [ "$stage" != unsupported-external-writer ] || [ -f "$barrier/external-writer-created" ] || fail 'R36 unsupported cell did not use external writer'
  helper="$canonical_saved"
}

residual_field() { "$python_bin" - "$last_record" "$1" <<'PY'
import json,sys
v=json.loads(sys.argv[1])[sys.argv[2]]
if not isinstance(v,str) or not v: raise SystemExit('missing residual field')
print(v)
PY
}
assert_retained_recovery_paths() { "$python_bin" - "$last_record" "$fixture_repo" <<'PY'
import json,sys
from pathlib import Path
record=json.loads(sys.argv[1]); root=Path(sys.argv[2]).resolve()
for field in ('journal_path',):
 p=Path(record[field]).resolve()
 if root not in p.parents or not p.exists(): raise SystemExit(f'missing retained {field}: {p}')
for raw in record['residue_paths']:
 p=Path(raw).resolve()
 if root not in p.parents or not p.exists(): raise SystemExit(f'missing retained residue: {p}')
PY
}

mutant_self_check() {
  setup
  local fake="$tmp/golden-helper.sh" pre candidate
  pre="$(artifact mutant-pre 4142434445)"; candidate="$(artifact mutant-candidate 4e4557)"
  cat >"$fake" <<'SH'
#!/usr/bin/env bash
set -euo pipefail
root=; target=; operation=; candidate=; arbitrary=0; status="${R36_SELF_STATUS:-COMMITTED}"; while [ "$#" -gt 0 ]; do case "$1" in --repo-root)root="$2";shift 2;;--target) target="$2";shift 2;;--operation)operation="$2";shift 2;;--candidate|--replacement)candidate="$2";shift 2;;--arbitrary-mutator)arbitrary=1;shift 2;;*)shift;;esac;done
[ "$arbitrary" = 0 ] || printf PWNED > "$root/sentinel"
python3 - "$root/$target" "$target" "$operation" "$candidate" "$status" <<'PY'
import hashlib,json,sys
t,p,o,c,s=sys.argv[1:]; b=open(t,'rb').read(); ident={'sha256':hashlib.sha256(b).hexdigest(),'byte_length':len(b)}; ci=None if not c else {'sha256':hashlib.sha256(open(c,'rb').read()).hexdigest(),'byte_length':len(open(c,'rb').read())}
print(json.dumps({'schema':'implementaudit.observation_bound_mutation.v1','operation':o,'status':s,'source_path':p,'destination_path':None,'targets':[p],'pre_identity':ident,'candidate_identity':ci,'post_identity':ident,'post_identities':{p:ident},'token':None,'journal_path':None,'residue_paths':[]}))
PY
case "$status" in COMMITTED|NO_CHANGE) exit 0;; REJECTED_NO_MUTATION) exit 64;; MUTATION_FAILED_NO_STATE_CHANGE) exit 70;; MUTATION_FAILED_ROLLED_BACK) exit 71;; POST_STATE_MISMATCH_ROLLED_BACK) exit 72;; UNSUPPORTED_OWNER_DECISION) exit 77;; *) exit 1;; esac
SH
  chmod +x "$fake"; helper="$fake"
  if (invoke R36-MUTANT COMMITTED replace target - "$candidate" 4e4557 --preimage "$pre" --candidate "$candidate") 2>"$tmp/mutant.err"; then fail 'R36 mutant golden-status helper escaped byte assertion'; fi
  grep -Fq 'visible state' "$tmp/mutant.err" || fail 'R36 mutant was not killed by the independent byte assertion'
  # Status 70/71/72/77 have executable, exit-specific schema discriminators;
  # they are test self-coherence probes, not a substitute for the real helper.
  for status in MUTATION_FAILED_NO_STATE_CHANGE MUTATION_FAILED_ROLLED_BACK POST_STATE_MISMATCH_ROLLED_BACK UNSUPPORTED_OWNER_DECISION; do
    R36_SELF_STATUS="$status" invoke "R36-MUTANT-$status" "$status" replace target - "$candidate" 4142434445 --preimage "$pre" --candidate "$candidate"
  done
  write_hex "$fixture_repo/sentinel" 53414645
  set +e; R36_SELF_STATUS=REJECTED_NO_MUTATION bash "$fake" --repo-root "$fixture_repo" --run-root "$run_root" --operation replace --target target --preimage "$pre" --candidate "$candidate" --arbitrary-mutator 'ignored' >/dev/null; local arbitrary_exit=$?; set -e
  [ "$arbitrary_exit" -eq 64 ] || fail 'R36 mutant arbitrary-command status did not use refusal exit'
  assert_hex R36-MUTANT-C4-sentinel "$fixture_repo/sentinel" 50574e4544
  # Held-out bank.  These are six different executable bad helpers, not names
  # looped over one no-op.  Each first proves that it performed its named bad
  # behaviour, then runs the focused acceptance discriminator that kills it.
  setup; candidate="$(artifact mutant-copy-candidate 4e4557)"; fake="$tmp/mutant-copy-vs-move.sh"
  cat >"$fake" <<'SH'
#!/usr/bin/env bash
set -euo pipefail
root= target= destination=; while [ "$#" -gt 0 ]; do case "$1" in --repo-root) root="$2"; shift 2;; --target) target="$2"; shift 2;; --destination) destination="$2"; shift 2;; *) shift;; esac; done
cp -- "$root/$target" "$root/$destination"
SH
  chmod +x "$fake"; bash "$fake" --repo-root "$fixture_repo" --operation move --target target --destination destination
  assert_hex R36-MUTANT-copy-destination "$fixture_repo/destination" 4142434445
  if (assert_hex R36-MUTANT-copy-vs-move-killed "$fixture_repo/target" -) 2>"$tmp/mutant-copy.err"; then fail 'copy-vs-move mutant escaped source-absence discriminator'; fi

  setup; candidate="$(artifact mutant-lock-candidate 4e4557)"; fake="$tmp/mutant-incomplete-target-set-lock.sh"
  cat >"$fake" <<'SH'
#!/usr/bin/env bash
set -euo pipefail
root= target= destination= candidate=; while [ "$#" -gt 0 ]; do case "$1" in --repo-root) root="$2"; shift 2;; --target) target="$2"; shift 2;; --destination) destination="$2"; shift 2;; --candidate) candidate="$2"; shift 2;; *) shift;; esac; done
mkdir -p "$root/.IMPLEMENTAUDIT/only-source.lock"; mv -- "$root/$target" "$root/$destination"
python3 - "$root" "$target" "$destination" "$candidate" <<'PY'
import hashlib,json,sys
from pathlib import Path
r,t,d,c=map(str,sys.argv[1:]); ident=lambda b:{'sha256':hashlib.sha256(b).hexdigest(),'byte_length':len(b)}
old=ident(b'ABCDE'); new=ident(Path(c).read_bytes())
print(json.dumps({'schema':'implementaudit.observation_bound_mutation.v1','operation':'move','status':'COMMITTED','source_path':t,'destination_path':d,'targets':[t],'pre_identity':old,'candidate_identity':new,'post_identity':new,'post_identities':{t:None,d:new},'token':None,'journal_path':None,'residue_paths':[]},separators=(',',':')))
PY
SH
  chmod +x "$fake"; pre="$(artifact mutant-lock-pre 4142434445)"; mutant_pre_id="$(identity_json "$fixture_repo/target")"; response="$(bash "$fake" --repo-root "$fixture_repo" --operation move --target target --destination destination --candidate "$candidate")"
  [ -d "$fixture_repo/.IMPLEMENTAUDIT/only-source.lock" ] && [ ! -e "$fixture_repo/.IMPLEMENTAUDIT/destination.lock" ] || fail 'incomplete-lock mutant did not exhibit one-slot locking'
  if (assert_response R36-MUTANT-incomplete-target-set-lock COMMITTED move target destination '["target","destination"]' "$mutant_pre_id" "$(identity_json "$candidate")" "$(identity_json "$fixture_repo/destination")" "$(post_identities_json target destination)" "$response") 2>"$tmp/mutant-lock.err"; then fail 'incomplete target-set mutant escaped schema discriminator'; fi

  setup; candidate="$(artifact mutant-race-candidate 4e4557)"; fake="$tmp/mutant-check-use-race.sh"; barrier="$tmp/mutant-check-use-race"; mkdir "$barrier"
  cat >"$fake" <<'SH'
#!/usr/bin/env bash
set -euo pipefail
root= target= candidate=; while [ "$#" -gt 0 ]; do case "$1" in --repo-root) root="$2"; shift 2;; --target) target="$2"; shift 2;; --candidate) candidate="$2"; shift 2;; *) shift;; esac; done
cmp -s "$root/$target" "$root/$target"; : >"$R36_MUTANT_BARRIER/checked"; while [ ! -f "$R36_MUTANT_BARRIER/release" ]; do sleep .02; done
cp -- "$candidate" "$root/$target"
SH
  chmod +x "$fake"; R36_MUTANT_BARRIER="$barrier" bash "$fake" --repo-root "$fixture_repo" --operation replace --target target --candidate "$candidate" & pid=$!
  ticks=0; while [ ! -f "$barrier/checked" ] && [ "$ticks" -lt 250 ]; do sleep .02; ticks=$((ticks+1)); done; [ "$ticks" -lt 250 ] || fail 'check-use mutant did not reach check barrier'
  write_hex "$fixture_repo/target" 4452494654; : >"$barrier/release"; wait_bounded "$pid" 'check-use mutant'
  assert_hex R36-MUTANT-check-use-observed-write "$fixture_repo/target" 4e4557
  if (assert_hex R36-MUTANT-check-use-killed "$fixture_repo/target" 4452494654) 2>"$tmp/mutant-race.err"; then fail 'check-use mutant escaped currentness discriminator'; fi

  setup; if [ "$(cat "$fixture_repo/symlink-capability")" = yes ]; then candidate="$(artifact mutant-link-candidate 4e4557)"; fake="$tmp/mutant-symlink-dereference.sh"
    cat >"$fake" <<'SH'
#!/usr/bin/env bash
set -euo pipefail
root= target= candidate=; while [ "$#" -gt 0 ]; do case "$1" in --repo-root) root="$2"; shift 2;; --target) target="$2"; shift 2;; --candidate) candidate="$2"; shift 2;; *) shift;; esac; done
cp -- "$candidate" "$root/$target"
SH
    chmod +x "$fake"; bash "$fake" --repo-root "$fixture_repo" --operation replace --target final-link --candidate "$candidate"
    assert_hex R36-MUTANT-symlink-referent "$fixture_repo/target" 4e4557
    if (assert_hex R36-MUTANT-symlink-killed "$fixture_repo/target" 4142434445) 2>"$tmp/mutant-symlink.err"; then fail 'symlink dereference mutant escaped referent discriminator'; fi
  fi

  setup; candidate="$(artifact mutant-residue-candidate 4e4557)"; fake="$tmp/mutant-fictitious-residue.sh"
  cat >"$fake" <<'SH'
#!/usr/bin/env bash
set -euo pipefail
root= target= candidate=; while [ "$#" -gt 0 ]; do case "$1" in --repo-root) root="$2"; shift 2;; --target) target="$2"; shift 2;; --candidate) candidate="$2"; shift 2;; *) shift;; esac; done
python3 - "$root" "$target" "$candidate" <<'PY'
import hashlib,json,sys
from pathlib import Path
r,t,c=map(str,sys.argv[1:]); ident=lambda b:{'sha256':hashlib.sha256(b).hexdigest(),'byte_length':len(b)}; old=ident(Path(r,t).read_bytes()); new=ident(Path(c).read_bytes())
print(json.dumps({'schema':'implementaudit.observation_bound_mutation.v1','operation':'replace','status':'ROLLBACK_CONFLICT','source_path':t,'destination_path':None,'targets':[t],'pre_identity':old,'candidate_identity':new,'post_identity':old,'post_identities':{t:old},'token':'fiction','journal_path':r+'/missing-journal','residue_paths':[r+'/missing-residue']},separators=(',',':')))
PY
exit 74
SH
  chmod +x "$fake"; pre="$(artifact mutant-residue-pre 4142434445)"; set +e; response="$(bash "$fake" --repo-root "$fixture_repo" --operation replace --target target --candidate "$candidate")"; actual=$?; set -e
  [ "$actual" -eq 74 ] || fail 'fictitious residue mutant did not emit rollback-conflict exit'
  last_record="$(assert_response R36-MUTANT-fictitious-residue ROLLBACK_CONFLICT replace target - '["target"]' "$(identity_json "$fixture_repo/target")" "$(identity_json "$candidate")" "$(identity_json "$fixture_repo/target")" "$(post_identities_json target -)" "$response")"
  if (assert_retained_recovery_paths) 2>"$tmp/mutant-residue.err"; then fail 'fictitious residue mutant escaped retained-path discriminator'; fi

  setup; candidate="$(artifact mutant-rollback-candidate 4e4557)"; fake="$tmp/mutant-fake-rollback.sh"
  cat >"$fake" <<'SH'
#!/usr/bin/env bash
set -euo pipefail
root= target= candidate=; while [ "$#" -gt 0 ]; do case "$1" in --repo-root) root="$2"; shift 2;; --target) target="$2"; shift 2;; --candidate) candidate="$2"; shift 2;; *) shift;; esac; done
cp -- "$candidate" "$root/$target"; exit 71
SH
  chmod +x "$fake"; set +e; bash "$fake" --repo-root "$fixture_repo" --operation replace --target target --candidate "$candidate"; actual=$?; set -e
  [ "$actual" -eq 71 ] || fail 'fake rollback mutant did not emit rollback exit'
  assert_hex R36-MUTANT-fake-rollback-visible "$fixture_repo/target" 4e4557
  if (assert_hex R36-MUTANT-fake-rollback-killed "$fixture_repo/target" 4142434445) 2>"$tmp/mutant-rollback.err"; then fail 'fake rollback mutant escaped restoration discriminator'; fi
  helper="$canonical_helper"
  printf 'R36_MUTANT_SELF_CHECK=PASS golden-json-without-mutation=killed\n'
}

concurrent_destination() {
  setup
  local pa pb barrier="$tmp/barrier-destination"; pa="$(artifact a-pre 41)"; pb="$(artifact b-pre 42)"; rm -rf "$barrier"; mkdir "$barrier"
  local pid_a pid_b
  for source in a b; do (
    : >"$barrier/$source.ready"; while [ ! -f "$barrier/release" ]; do sleep .02; done
    set +e; bash "$helper" --repo-root "$fixture_repo" --run-root "$run_root" --operation move --target "$source" --preimage "$( [ "$source" = a ] && echo "$pa" || echo "$pb" )" --destination destination >"$barrier/$source.out" 2>"$barrier/$source.err"; echo $? >"$barrier/$source.exit"
  ) &
  [ "$source" = a ] && pid_a=$! || pid_b=$!
  done
  local ticks=0; while { [ ! -f "$barrier/a.ready" ] || [ ! -f "$barrier/b.ready" ]; } && [ "$ticks" -lt 250 ]; do sleep .02; ticks=$((ticks+1)); done
  [ "$ticks" -lt 250 ] || fail 'R36-CONCURRENCY destination barrier timeout'; : >"$barrier/release"; wait_bounded "$pid_a" 'R36-CONCURRENCY writer a'; wait_bounded "$pid_b" 'R36-CONCURRENCY writer b'
  "$python_bin" - "$barrier" "$fixture_repo" <<'PY'
import json,sys
from pathlib import Path
b,r=map(Path,sys.argv[1:]); rows=[]
for n in ('a','b'):
 code=int((b/f'{n}.exit').read_text()); rec=json.loads((b/f'{n}.out').read_text()); rows.append((n,code,rec['status']))
if sorted((x[1],x[2]) for x in rows)!=[(0,'COMMITTED'),(65,'CONFLICT_REBASE')]: raise SystemExit(f'R36-CONCURRENCY statuses {rows!r}')
winner=next(n for n,c,s in rows if s=='COMMITTED'); loser='b' if winner=='a' else 'a'
if (r/'destination').read_bytes()!=winner.upper().encode() or (r/loser).read_bytes()!=loser.upper().encode() or (r/winner).exists(): raise SystemExit('R36-CONCURRENCY filesystem postcondition failed')
(b/'winner').write_text(winner,encoding='ascii'); (b/'loser').write_text(loser,encoding='ascii')
PY
  # Probe the actual target sets after the losing contender exits: its source
  # and the contested destination must both be reusable, not merely a disjoint file.
  local winner loser destination_pre destination_candidate loser_pre loser_candidate loser_hex
  winner="$(<"$barrier/winner")"; loser="$(<"$barrier/loser")"
  destination_pre="$(artifact destination-reuse-pre "$( [ "$winner" = "a" ] && printf 41 || printf 42 )")"
  destination_candidate="$(artifact destination-reuse-candidate 44)"
  invoke R36-CONCURRENCY-destination-reuse COMMITTED replace destination - "$destination_candidate" 44 --preimage "$destination_pre" --candidate "$destination_candidate"
  loser_hex=42; [ "$loser" = a ] && loser_hex=41
  loser_pre="$(artifact loser-reuse-pre "$loser_hex")"; loser_candidate="$(artifact loser-reuse-candidate 4c)"
  invoke R36-CONCURRENCY-loser-reuse COMMITTED replace "$loser" - "$loser_candidate" 4c --preimage "$loser_pre" --candidate "$loser_candidate"
}

opposing_moves() {
  setup
  local pa pb barrier="$tmp/barrier-opposing"; pa="$(artifact opposing-a 41)"; pb="$(artifact opposing-b 42)"; rm -rf "$barrier"; mkdir "$barrier"
  local pid_a pid_b
  for source in a b; do (
    : >"$barrier/$source.ready"; while [ ! -f "$barrier/release" ]; do sleep .02; done
    destination=b; [ "$source" = b ] && destination=a
    pre="$pb"; [ "$source" = a ] && pre="$pa"
    set +e; bash "$helper" --repo-root "$fixture_repo" --run-root "$run_root" --operation move --target "$source" --preimage "$pre" --destination "$destination" >"$barrier/$source.out" 2>"$barrier/$source.err"; echo $? >"$barrier/$source.exit"
  ) &
  [ "$source" = a ] && pid_a=$! || pid_b=$!
  done
  local ticks=0; while { [ ! -f "$barrier/a.ready" ] || [ ! -f "$barrier/b.ready" ]; } && [ "$ticks" -lt 250 ]; do sleep .02; ticks=$((ticks+1)); done
  [ "$ticks" -lt 250 ] || fail 'R36-OPPOSING barrier timeout'; : >"$barrier/release"; wait_bounded "$pid_a" 'R36-OPPOSING writer a'; wait_bounded "$pid_b" 'R36-OPPOSING writer b'
  "$python_bin" - "$barrier" "$fixture_repo" <<'PY'
import json,sys
from pathlib import Path
b,r=map(Path,sys.argv[1:])
for n in ('a','b'):
 if int((b/f'{n}.exit').read_text()) != 64 or json.loads((b/f'{n}.out').read_text())['status'] != 'REJECTED_NO_MUTATION': raise SystemExit('R36-OPPOSING did not fail closed')
if (r/'a').read_bytes()!=b'A' or (r/'b').read_bytes()!=b'B': raise SystemExit('R36-OPPOSING changed either source')
PY
}

canonical_observation_races() {
  # The helper publishes an `observed` barrier only after it captured the
  # supplied preimage/current target, so these external writes are genuinely
  # after observation rather than setup-time stale fixtures.
  local label mode pre barrier pid actual stdout stderr source_pre source_post post_set canonical_saved="$helper" instrumented
  instrumented="$(instrumented_helper)"; helper="$instrumented"
  for mode in source destination; do
    setup; label="R36-RACE-$mode"; pre="$(artifact "$mode-pre" 4142434445)"; barrier="$tmp/barrier-race-$mode"; mkdir "$barrier"; stdout="$tmp/$label.out"; stderr="$tmp/$label.err"; source_pre="$(identity_json "$fixture_repo/target")"
    (set +e; IMPLEMENTAUDIT_R36_TEST_BARRIER_DIR="$barrier" bash "$helper" --repo-root "$fixture_repo" --run-root "$run_root" --operation move --target target --preimage "$pre" --destination destination >"$stdout" 2>"$stderr"; echo $? >"$barrier/exit") & pid=$!
    local ticks=0; while [ ! -f "$barrier/observed" ] && [ "$ticks" -lt 500 ]; do sleep .02; ticks=$((ticks+1)); done
    [ "$ticks" -lt 500 ] || fail "$label did not acknowledge post-observation barrier"
    if [ "$mode" = source ]; then write_hex "$fixture_repo/target" 4c41544552; else write_hex "$fixture_repo/destination" 45585445524e414c; fi
    : >"$barrier/release"; wait_bounded "$pid" "$label helper"; actual="$(<"$barrier/exit")"
    [ "$actual" -eq 65 ] || fail "$label exit $actual, expected stale conflict 65"
    source_post="$(identity_json "$fixture_repo/target")"; post_set="$(post_identities_json target destination)"
    last_record="$(assert_response "$label" CONFLICT_REBASE move target destination '["target","destination"]' "$source_pre" "$(identity_json "$pre")" "$source_post" "$post_set" "$(<"$stdout")")"
    if [ "$mode" = source ]; then assert_hex "$label-source" "$fixture_repo/target" 4c41544552; assert_hex "$label-destination" "$fixture_repo/destination" -
    else assert_hex "$label-source" "$fixture_repo/target" 4142434445; assert_hex "$label-destination" "$fixture_repo/destination" 45585445524e414c; fi
  done
  helper="$canonical_saved"
}

external_drift_and_recovery() {
  # The actor is external to the helper.  It waits for an actual publication of
  # candidate bytes, then recreates the target with winner bytes; no requested
  # outcome/fault-name is supplied to the helper.
  setup
  local pre candidate barrier="$tmp/barrier-drift" stdout="$tmp/drift.out" stderr="$tmp/drift.err" pre_id
  pre="$(artifact drift-pre 4142434445)"
  pre_id="$(identity_json "$fixture_repo/target")"
  candidate="$fixture_repo/artifacts/drift-candidate"
  "$python_bin" - "$candidate" <<'PY'
import sys
from pathlib import Path
Path(sys.argv[1]).write_bytes(b'N' * (8 * 1024 * 1024))
PY
  rm -rf "$barrier"; mkdir "$barrier"
  (
    : >"$barrier/actor-ready"; while [ ! -f "$barrier/release" ]; do sleep .02; done
    "$python_bin" - "$fixture_repo/target" "$candidate" "$barrier/actor-fired" <<'PY'
import hashlib,sys,time
from pathlib import Path
t,c,f=map(Path,sys.argv[1:]); wanted=hashlib.sha256(c.read_bytes()).digest()
for _ in range(1000):
    if t.exists() and hashlib.sha256(t.read_bytes()).digest()==wanted:
        t.write_bytes(b'EXTERNAL-WINNER')
        f.write_text('fired\n',encoding='ascii')
        raise SystemExit(0)
    time.sleep(.005)
raise SystemExit('candidate publication was not observed')
PY
  ) &
  local actor=$! helper_pid ticks=0 actual status post record journal token
  while [ ! -f "$barrier/actor-ready" ] && [ "$ticks" -lt 250 ]; do sleep .02; ticks=$((ticks+1)); done
  [ "$ticks" -lt 250 ] || fail 'R36-DRIFT actor barrier timeout'
  : >"$barrier/release"
  (set +e; bash "$helper" --repo-root "$fixture_repo" --run-root "$run_root" --operation replace --target target --preimage "$pre" --candidate "$candidate" >"$stdout" 2>"$stderr"; echo $? >"$barrier/helper.exit") & helper_pid=$!
  wait_bounded "$helper_pid" 'R36-DRIFT helper'
  actual="$(<"$barrier/helper.exit")"
  wait_bounded "$actor" 'R36-DRIFT actor'
  [ -f "$barrier/actor-fired" ] || fail 'R36-DRIFT actor did not fire'
  status="$($python_bin - "$stdout" <<'PY'
import json,sys
print(json.loads(open(sys.argv[1],encoding='utf-8').read())['status'])
PY
)"
  [ "$status" = ROLLBACK_CONFLICT ] || fail "R36-DRIFT status $status, expected ROLLBACK_CONFLICT"
  [ "$actual" -eq "$(status_exit ROLLBACK_CONFLICT)" ] || fail "R36-DRIFT exit/status mismatch"
  post="$(identity_json "$fixture_repo/target")"
  last_record="$(assert_response R36-DRIFT "$status" replace target - '["target"]' "$pre_id" "$(identity_json "$candidate")" "$post" "$(post_identities_json target -)" "$(<"$stdout")")"
  assert_hex R36-DRIFT-winner "$fixture_repo/target" 45585445524e414c2d57494e4e4552
  journal="$(residual_field journal_path)"; token="$(residual_field token)"
  case "$journal" in "$fixture_repo"/*) ;; *) fail "R36-DRIFT journal escapes fixture: $journal";; esac
  [ -e "$journal" ] || fail 'R36-DRIFT journal not retained'
  "$python_bin" - "$last_record" "$fixture_repo" <<'PY'
import json,sys
from pathlib import Path
r=Path(sys.argv[2]).resolve()
for p in json.loads(sys.argv[1])['residue_paths']:
 q=Path(p).resolve()
 if r not in q.parents or not q.exists(): raise SystemExit(f'bad residue {p}')
PY
  # Wrong token must not delete the journal, mutate winner bytes, or consume the lock/recovery authority.
  invoke R36-DRIFT-forged REJECTED_NO_MUTATION recover target - - 45585445524e414c2d57494e4e4552 --journal "$journal" --token "forged-$token"
  [ -e "$journal" ] || fail 'R36-DRIFT forged token removed journal'
  # A token-looking, externally crafted journal/backup cannot become recovery
  # authority or consume either external file.
  local crafted_backup="$tmp/crafted-backup" crafted_journal="$tmp/crafted-journal.json" crafted_token='crafted-token'
  write_hex "$crafted_backup" 41545441434b
  "$python_bin" - "$crafted_journal" "$crafted_backup" "$crafted_token" <<'PY'
import json,sys
from pathlib import Path
j,b,t=sys.argv[1:]; Path(j).write_text(json.dumps({'token':t,'target':'target','backup':b,'pre_identity':{'sha256':'x','byte_length':6},'candidate_identity':None}),encoding='utf-8')
PY
  invoke R36-DRIFT-crafted-journal REJECTED_NO_MUTATION recover target - - 45585445524e414c2d57494e4e4552 --journal "$crafted_journal" --token "$crafted_token"
  assert_hex R36-DRIFT-crafted-backup-intact "$crafted_backup" 41545441434b; [ -e "$crafted_journal" ] || fail 'crafted journal was consumed'
  # A caller can make a byte-consistent journal, backup, token-shaped names,
  # and even a linked would-be authority record in the claimed run.  Portable
  # same-principal storage does not establish who created those files, so none
  # of them may authorize automatic mutation.
  local internal_token='internal-token' internal_backup="$run_root/.r36-backup-internal-token" internal_journal="$run_root/.r36-journal-internal-token.json" internal_authority="$run_root/.r36-authority-internal-token"
  write_hex "$internal_backup" 41545441434b
  ln -s "$outside" "$internal_authority" 2>/dev/null || { printf 'authority-link-fallback\n' >"$internal_authority"; }
  "$python_bin" - "$internal_journal" "$internal_backup" "$internal_token" "$internal_authority" <<'PY'
import hashlib,json,sys
from pathlib import Path
j,b,t,a=sys.argv[1:]; raw=Path(b).read_bytes(); ident={'sha256':hashlib.sha256(raw).hexdigest(),'byte_length':len(raw)}
authority=Path(a).read_bytes(); ah=hashlib.sha256(authority).hexdigest()
Path(j).write_text(json.dumps({'token':t,'target':'target','backup':b,'pre_identity':ident,'candidate_identity':None,'authority_hash':ah}),encoding='utf-8')
PY
  invoke R36-DRIFT-internal-forgery REJECTED_NO_MUTATION recover target - - 45585445524e414c2d57494e4e4552 --journal "$internal_journal" --token "$internal_token"
  assert_hex R36-DRIFT-internal-backup-intact "$internal_backup" 41545441434b; [ -e "$internal_journal" ] || fail 'internal forged journal was consumed'
  [ -L "$internal_authority" ] && assert_hex R36-DRIFT-internal-linked-authority-referent "$outside" 4f555453494445
  # Even a correct token is manual/owner-gated custody on portable
  # same-principal filesystems: this helper never auto-recovers it.
  local recovery_pre recovery_post
  recovery_pre="$(identity_json "$fixture_repo/target")"
  set +e; bash "$helper" --repo-root "$fixture_repo" --run-root "$run_root" --operation recover --target target --journal "$journal" --token "$token" >"$tmp/recover.out" 2>"$tmp/recover.err"; actual=$?; set -e
  status="$($python_bin - "$tmp/recover.out" <<'PY'
import json,sys
print(json.loads(open(sys.argv[1],encoding='utf-8').read())['status'])
PY
)"
  [ "$status" = REJECTED_NO_MUTATION ] || fail "R36-DRIFT correct-token status $status"
  [ "$actual" -eq 64 ] || fail 'R36-DRIFT correct-token exit mismatch'
  recovery_post="$(identity_json "$fixture_repo/target")"
  last_record="$(assert_response R36-DRIFT-correct-token "$status" recover target - '["target"]' "$recovery_pre" null "$recovery_post" "$(post_identities_json target -)" "$(<"$tmp/recover.out")")"
  [ -e "$journal" ] || fail 'R36-DRIFT owner-gated recovery removed journal'
  assert_hex R36-DRIFT-correct-token-winner "$fixture_repo/target" 45585445524e414c2d57494e4e4552
}

true_kill_requires_manual_custody() {
  # A SIGKILL cannot emit a terminal JSON object.  The durable, pre-existing
  # journal is therefore the only truthful recovery-required report: it must
  # survive with the displaced preimage and owned lock set, while the public
  # recover CLI stays a non-mutating/manual-custody gate.
  setup
  local pre cand derived barrier="$tmp/true-kill" stdout="$tmp/true-kill.out" stderr="$tmp/true-kill.err" pid ticks=0 journal backup token record
  pre="$(artifact true-kill-pre 4142434445)"; cand="$(artifact true-kill-candidate 4e4557)"
  derived="$(instrumented_helper)" || fail 'R36 true-kill could not derive instrumented helper'
  rm -rf "$barrier"; mkdir "$barrier"
  (set +e; IMPLEMENTAUDIT_R36_TEST_BARRIER_DIR="$barrier" IMPLEMENTAUDIT_R36_TEST_FAULT_STAGE=after-displacement bash "$derived" --repo-root "$fixture_repo" --run-root "$run_root" --operation replace --target target --preimage "$pre" --candidate "$cand" >"$stdout" 2>"$stderr"; echo $? >"$barrier/exit") & pid=$!
  while [ ! -f "$barrier/paused" ] && kill -0 "$pid" 2>/dev/null && [ "$ticks" -lt 500 ]; do sleep .02; ticks=$((ticks+1)); done
  [ "$ticks" -lt 500 ] || { wait_bounded "$pid" 'R36 true-kill helper'; fail 'R36 true-kill never reached durable displacement'; }
  kill -9 "$pid" 2>/dev/null || true; wait "$pid" 2>/dev/null || true
  [ ! -e "$fixture_repo/target" ] || fail 'R36 true-kill retained target after displacement'
  journal="$(find "$run_root" -maxdepth 1 -type f -name '.r36-journal-*.json' -print -quit)"
  backup="$(find "$run_root" -maxdepth 1 -type f -name '.r36-backup-*' -print -quit)"
  [ -n "$journal" ] && [ -n "$backup" ] || fail 'R36 true-kill did not retain journal and backup'
  assert_hex R36-TRUE-KILL-backup "$backup" 4142434445
  record="$($python_bin - "$journal" <<'PY'
import json,sys
r=json.load(open(sys.argv[1],encoding='utf-8'))
if r.get('recovery_disposition') != 'RECOVERY_REQUIRED': raise SystemExit(f'journal disposition is not recovery-required: {r!r}')
if not isinstance(r.get('token'),str) or not r['token']: raise SystemExit('journal token missing')
print(r['token'])
PY
)" || fail 'R36 true-kill journal is not a durable recovery-required record'
  token="$record"
  find "$fixture_repo/.IMPLEMENTAUDIT/.r36-locks" -mindepth 1 -maxdepth 1 -type d -print -quit | grep -q . || fail 'R36 true-kill did not retain lock ownership'
  invoke R36-TRUE-KILL-manual-gate REJECTED_NO_MUTATION recover target - - - --journal "$journal" --token "$token"
  [ ! -e "$fixture_repo/target" ] || fail 'R36 true-kill recover mutated target'
  [ -e "$journal" ] && [ -e "$backup" ] || fail 'R36 true-kill recover consumed custody'
}

state_family() {
  local pre cand region repl
  setup; pre="$(artifact c1-pre 414243)"; cand="$(artifact c1-candidate 5a)"; invoke R36-C1 REJECTED_NO_MUTATION replace target - "$cand" 4142434445 --preimage "$pre" --candidate "$cand"
  setup; pre="$(artifact c2-pre 4142434445)"; cand="$(artifact c2-candidate 5a)"; write_hex "$fixture_repo/target" 494e54455256454e494e47; invoke R36-C2 CONFLICT_REBASE replace target - "$cand" 494e54455256454e494e47 --preimage "$pre" --candidate "$cand"
  # C3 is intentionally collapsed into the actual invariant: a byte-equal,
  # complete current preimage is the only qualifying observation.
  setup; pre="$(artifact c3-partial 414243)"; cand="$(artifact c3-candidate 5a)"; invoke R36-C3 REJECTED_NO_MUTATION replace target - "$cand" 4142434445 --preimage "$pre" --candidate "$cand"
  setup; pre="$(artifact c4-pre 4142434445)"; cand="$(artifact c4-candidate 5a)"; write_hex "$fixture_repo/sentinel" 53414645; mutator="$fixture_repo/artifacts/operative-mutator.sh"; "$python_bin" - "$mutator" "$fixture_repo/sentinel" <<'PY'
import os,sys
from pathlib import Path
p=Path(sys.argv[1]); p.write_text('#!/usr/bin/env bash\nprintf PWNED > "$1"\n',encoding='utf-8'); os.chmod(p,0o700)
PY
  invoke R36-C4 REJECTED_NO_MUTATION replace target - "$cand" 4142434445 --preimage "$pre" --candidate "$cand" --arbitrary-mutator "$mutator" "$fixture_repo/sentinel"; assert_hex R36-C4-sentinel "$fixture_repo/sentinel" 53414645
  # Ambient test labels are inert to the authoritative helper. Only the
  # mechanically derived, unshipped driver may consume them.
  setup; pre="$(artifact ambient-pre 4142434445)"; cand="$(artifact ambient-candidate 4e4557)"; IMPLEMENTAUDIT_R36_TEST_FAULT_STAGE=after-publication IMPLEMENTAUDIT_R36_TEST_BARRIER_DIR="$tmp/ambient-inert" invoke R36-AMBIENT-inert COMMITTED replace target - "$cand" 4e4557 --preimage "$pre" --candidate "$cand"
  setup; region="$(artifact crlf-region 74776f0d0a)"; repl="$(artifact crlf-repl 54574f0d0a)"; invoke R36-B1 COMMITTED patch crlf - "$repl" 6f6e650d0a54574f0d0a74687265650d0a --offset 5 --region "$region" --replacement "$repl"
  setup; region="$(artifact unicode-region e282ac2de4b8ade69687)"; repl="$(artifact unicode-repl f09f9880)"; invoke R36-B2 COMMITTED patch unicode - "$repl" 7072656669782df09f98802d737566666978 --offset 7 --region "$region" --replacement "$repl"
  setup; region="$(artifact split-region e2)"; repl="$(artifact split-repl 58)"; invoke R36-B2-split COMMITTED patch unicode - "$repl" 7072656669782d5882ac2de4b8ade696872d737566666978 --offset 7 --region "$region" --replacement "$repl"
  setup; region="$(artifact empty-region '')"; repl="$(artifact empty-repl 58)"; invoke R36-B2-empty REJECTED_NO_MUTATION patch target - "$repl" 4142434445 --offset 0 --region "$region" --replacement "$repl"
  # Canonical helper fault stages exercise concrete terminal families and
  # byte restoration at each transaction boundary.
  setup; pre="$(artifact fault-pre-displacement 4142434445)"; cand="$(artifact fault-candidate 4e4557)"; invoke_fault pre-displacement R36-F70 MUTATION_FAILED_NO_STATE_CHANGE replace target - "$cand" 4142434445 --preimage "$pre" --candidate "$cand"
  setup; pre="$(artifact fault-after-displacement 4142434445)"; cand="$(artifact fault-candidate 4e4557)"; invoke_fault after-displacement R36-F71a MUTATION_FAILED_ROLLED_BACK replace target - "$cand" 4142434445 --preimage "$pre" --candidate "$cand"
  setup; pre="$(artifact fault-after-publication 4142434445)"; cand="$(artifact fault-candidate 4e4557)"; invoke_fault after-publication R36-F71b MUTATION_FAILED_ROLLED_BACK replace target - "$cand" 4142434445 --preimage "$pre" --candidate "$cand"
  setup; pre="$(artifact fault-post-mismatch 4142434445)"; cand="$(artifact fault-candidate 4e4557)"; invoke_fault post-state-mismatch R36-F72 POST_STATE_MISMATCH_ROLLED_BACK replace target - "$cand" 4142434445 --preimage "$pre" --candidate "$cand"
  setup; pre="$(artifact fault-unsupported 4142434445)"; cand="$(artifact fault-candidate 4e4557)"; invoke_fault unsupported-external-writer R36-F77 UNSUPPORTED_OWNER_DECISION replace target - "$cand" 554e535550504f525445442d575249544552 --preimage "$pre" --candidate "$cand"
  setup; pre="$(artifact binary-pre 0001ff7f42494e0d0a)"; cand="$(artifact binary-candidate ff0042494e2d)"; invoke R36-B3 COMMITTED replace binary - "$cand" ff0042494e2d --preimage "$pre" --candidate "$cand"; pre="$(artifact binary-delete-pre ff0042494e2d)"; invoke R36-B4 COMMITTED delete binary - - - --preimage "$pre"; setup; pre="$(artifact binary-move-pre 0001ff7f42494e0d0a)"; invoke R36-B5 COMMITTED move binary binary-destination "$pre" 0001ff7f42494e0d0a --preimage "$pre" --destination binary-destination; assert_hex R36-B5-source-absent "$fixture_repo/binary" -; assert_hex R36-B5-destination "$fixture_repo/binary-destination" 0001ff7f42494e0d0a
  setup; pre="$(artifact hard-pre 5349424c494e47)"; cand="$(artifact hard-candidate 4e4557)"; invoke R36-T1 COMMITTED replace hardlink - "$cand" 4e4557 --preimage "$pre" --candidate "$cand"; assert_hex R36-T1-sibling "$fixture_repo/sibling" 5349424c494e47
  setup; pre="$(artifact equal-pre 53414d45)"; cand="$(artifact equal-candidate 4e4557)"; invoke R36-T1-equal COMMITTED replace equal-one - "$cand" 4e4557 --preimage "$pre" --candidate "$cand"; assert_hex R36-T1-equal-other "$fixture_repo/equal-two" 53414d45
  setup; pre="$(artifact scope-pre 4142434445)"; cand="$(artifact scope-candidate 4e4557)"; invoke R36-T2 REJECTED_NO_MUTATION replace ../existing-outside-target - "$cand" 4f555453494445 --preimage "$pre" --candidate "$cand"; [ "$(cat "$fixture_repo/symlink-capability")" = yes ] && { pre="$(artifact link-pre 4142434445)"; invoke R36-T3 REJECTED_NO_MUTATION replace final-link - "$cand" @SYMLINK_PATH --preimage "$pre" --candidate "$cand"; assert_hex R36-T3-outside-referent "$fixture_repo/target" 4142434445; pre="$(artifact parent-pre 6368696c64)"; invoke R36-T4 REJECTED_NO_MUTATION replace parent-link/child - "$cand" @SYMLINK_PATH --preimage "$pre" --candidate "$cand"; assert_hex R36-T4-ancestor-outside-referent "$fixture_repo/real/child" 6368696c64; }
  setup; pre="$(artifact reference-pre 4142434445)"; ln -s "$(basename "$pre")" "$fixture_repo/artifacts/reference-preimage" 2>/dev/null || true; if [ -L "$fixture_repo/artifacts/reference-preimage" ]; then cand="$(artifact reference-candidate 4e4557)"; invoke R36-T5 REJECTED_NO_MUTATION replace target - "$cand" 4142434445 --preimage "$fixture_repo/artifacts/reference-preimage" --candidate "$cand"; fi
  setup; pre="$(artifact stale-delete-pre 414243)"; invoke R36-D1 REJECTED_NO_MUTATION delete target - - 4142434445 --preimage "$pre"; pre="$(artifact stale-move-pre 414243)"; invoke R36-D2 REJECTED_NO_MUTATION move target absent-destination "$pre" 4142434445 --preimage "$pre" --destination absent-destination; assert_hex R36-D2-destination-absent "$fixture_repo/absent-destination" -
  setup; pre="$(artifact stale-move-full-pre 4142434445)"; write_hex "$fixture_repo/target" 4c41544552; invoke R36-D2-currentness CONFLICT_REBASE move target absent-destination "$pre" 4c41544552 --preimage "$pre" --destination absent-destination; assert_hex R36-D2-currentness-destination-absent "$fixture_repo/absent-destination" -
  setup; pre="$(artifact move-pre 4142434445)"; write_hex "$fixture_repo/existing-destination" 455849535453; invoke R36-D3 REJECTED_NO_MUTATION move target existing-destination "$pre" 4142434445 --preimage "$pre" --destination existing-destination; assert_hex R36-D3-destination "$fixture_repo/existing-destination" 455849535453
  setup; pre="$(artifact same-pre 4142434445)"; invoke R36-D4 REJECTED_NO_MUTATION move target target "$pre" 4142434445 --preimage "$pre" --destination target
  setup; mkdir "$fixture_repo/directory-target"; pre="$(artifact regular-pre 4142434445)"; cand="$(artifact regular-candidate 4e4557)"; invoke R36-D5 REJECTED_NO_MUTATION replace directory-target - "$cand" @DIRECTORY --preimage "$pre" --candidate "$cand"
  # Cheap controls are not helper triggers: read-only inspection, disposable
  # task-owned creation, and unrelated diagnostics leave the named bytes alone.
  setup; assert_hex R36-P1-read-only "$fixture_repo/target" 4142434445; : > "$run_root/disposable"; [ -f "$run_root/disposable" ] || fail 'R36-P1 disposable creation failed'
  setup; local run_relative="${run_root#$fixture_repo/}"; write_hex "$run_root/untracked" 554e545241434b4544; pre="$(artifact untracked-partial 554e54)"; cand="$(artifact untracked-candidate 4e4557)"; invoke R36-P2 REJECTED_NO_MUTATION replace "$run_relative/untracked" - "$cand" 554e545241434b4544 --preimage "$pre" --candidate "$cand"
  setup; printf 'diagnostic: truncated unrelated output\n' > "$fixture_repo/unrelated.log"; pre="$(artifact unrelated-pre 4142434445)"; cand="$(artifact unrelated-same 4142434445)"; invoke R36-P3 NO_CHANGE replace target - "$cand" 4142434445 --preimage "$pre" --candidate "$cand"
  concurrent_destination
  opposing_moves
  canonical_observation_races
  external_drift_and_recovery
  true_kill_requires_manual_custody
  printf 'observation-bound-mutation-integrity: PASS R36 state family\n'
}

case "${1:-}" in
  --fixture-self-check) fixture_self_check; exit 0;;
  --mutant-self-check) fixture_self_check; mutant_self_check; exit 0;;
esac
fixture_self_check
if [ -n "${R36_HELPER:-}" ] && [ "$R36_HELPER" != "$canonical_helper" ]; then fail "refusing non-canonical helper path: $R36_HELPER"; fi
if [ ! -f "$canonical_helper" ] || [ -L "$canonical_helper" ]; then printf 'observation-bound-mutation-integrity: RED missing authoritative helper: %s\n' "$canonical_helper" >&2; exit 1; fi
bash -n "$canonical_helper" || fail 'canonical helper has invalid Bash syntax'
instrumented_helper >/dev/null || fail 'R36 instrumented-copy derivation failed'
state_family
