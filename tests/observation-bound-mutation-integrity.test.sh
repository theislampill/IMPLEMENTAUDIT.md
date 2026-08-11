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

write_hex() { "$python_bin" - "$1" "$2" <<'PY'
import sys
from pathlib import Path
p=Path(sys.argv[1]); p.parent.mkdir(parents=True,exist_ok=True); p.write_bytes(bytes.fromhex(sys.argv[2]))
PY
}
assert_hex() { "$python_bin" - "$1" "$2" "$3" <<'PY'
import sys
from pathlib import Path
label,path,want=sys.argv[1:]
got=Path(path).read_bytes() if Path(path).exists() else None
expected=bytes.fromhex(want) if want != '-' else None
if got != expected: raise SystemExit(f'{label}: got={got!r} want={expected!r}')
PY
}
artifact() { local name="$1" hex="$2"; local p="$fixture_repo/artifacts/$name"; write_hex "$p" "$hex"; printf '%s\n' "$p"; }

setup() {
  rm -rf -- "$fixture_repo"
  mkdir -p "$fixture_repo/artifacts" "$run_root"
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
print('R36_FIXTURE_SELF_CHECK=PASS bytes=raw topology=hardlink,symlink-or-declared-unsupported')
PY
}

identity_json() { "$python_bin" - "$1" <<'PY'
import hashlib,json,sys
from pathlib import Path
p=Path(sys.argv[1])
if not p.exists(): print('null')
else:
 b=p.read_bytes(); print(json.dumps({'sha256':hashlib.sha256(b).hexdigest(),'byte_length':len(b)},separators=(',',':')))
PY
}
assert_response() { "$python_bin" - "$@" <<'PY'
import json,sys
label,status,operation,source,dest,targets,pre,candidate,post,out=sys.argv[1:]
lines=[x for x in out.splitlines() if x.strip()]
if len(lines)!=1: raise SystemExit(f'{label}: expected one stdout JSON object, got {len(lines)}')
r=json.loads(lines[0]); required={'schema','operation','status','source_path','destination_path','targets','pre_identity','candidate_identity','post_identity','token','journal_path','residue_paths'}
if set(r)!=required: raise SystemExit(f'{label}: schema keys differ: got={sorted(r)}')
want={'schema':'implementaudit.observation_bound_mutation.v1','operation':operation,'status':status,'source_path':source,'destination_path':None if dest=='-' else dest,'targets':json.loads(targets),'pre_identity':json.loads(pre),'candidate_identity':json.loads(candidate),'post_identity':json.loads(post)}
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
  local source_path="$fixture_repo/$target" post_path="$fixture_repo/$target"; [ "$op" = move ] && post_path="$fixture_repo/$dest"; [ "$op" = delete ] && post_path="$fixture_repo/__absent_post"
  local pre candidate_id post targets expected_exit stdout stderr actual
  pre="$(identity_json "$source_path")"; candidate_id="$(identity_json "$candidate")"
  if [ "$dest" = - ]; then targets="[\"$target\"]"; else targets="[\"$target\",\"$dest\"]"; fi
  expected_exit="$(status_exit "$status")"; stdout="$tmp/$label.out"; stderr="$tmp/$label.err"
  set +e; bash "$helper" --repo-root "$fixture_repo" --run-root "$run_root" --operation "$op" --target "$target" "$@" >"$stdout" 2>"$stderr"; actual=$?; set -e
  [ "$actual" -eq "$expected_exit" ] || fail "$label: exit=$actual expected=$expected_exit stderr=$(<"$stderr")"
  post="$(identity_json "$post_path")"
  last_record="$(assert_response "$label" "$status" "$op" "$target" "$dest" "$targets" "$pre" "$candidate_id" "$post" "$(<"$stdout")")"
  assert_hex "$label visible state" "$post_path" "$expected"
}

residual_field() { "$python_bin" - "$last_record" "$1" <<'PY'
import json,sys
v=json.loads(sys.argv[1])[sys.argv[2]]
if not isinstance(v,str) or not v: raise SystemExit('missing residual field')
print(v)
PY
}

mutant_self_check() {
  setup
  local fake="$tmp/golden-helper.sh" pre candidate
  pre="$(artifact mutant-pre 4142434445)"; candidate="$(artifact mutant-candidate 4e4557)"
  cat >"$fake" <<'SH'
#!/usr/bin/env bash
set -euo pipefail
root=; target=; operation=; candidate=; while [ "$#" -gt 0 ]; do case "$1" in --repo-root)root="$2";shift 2;;--target) target="$2";shift 2;;--operation)operation="$2";shift 2;;--candidate|--replacement)candidate="$2";shift 2;;*)shift;;esac;done
python3 - "$root/$target" "$target" "$operation" "$candidate" <<'PY'
import hashlib,json,sys
t,p,o,c=sys.argv[1:]; b=open(t,'rb').read(); ident={'sha256':hashlib.sha256(b).hexdigest(),'byte_length':len(b)}; ci=None if not c else {'sha256':hashlib.sha256(open(c,'rb').read()).hexdigest(),'byte_length':len(open(c,'rb').read())}
print(json.dumps({'schema':'implementaudit.observation_bound_mutation.v1','operation':o,'status':'COMMITTED','source_path':p,'destination_path':None,'targets':[p],'pre_identity':ident,'candidate_identity':ci,'post_identity':ident,'token':None,'journal_path':None,'residue_paths':[]}))
PY
SH
  chmod +x "$fake"; helper="$fake"
  if (invoke R36-MUTANT COMMITTED replace target - "$candidate" 4e4557 --preimage "$pre" --candidate "$candidate") 2>"$tmp/mutant.err"; then fail 'R36 mutant golden-status helper escaped byte assertion'; fi
  grep -Fq 'visible state' "$tmp/mutant.err" || fail 'R36 mutant was not killed by the independent byte assertion'
  helper="$canonical_helper"
  printf 'R36_MUTANT_SELF_CHECK=PASS golden-json-without-mutation=killed\n'
}

concurrent_destination() {
  setup
  local pa pb barrier="$tmp/barrier-destination"; pa="$(artifact a-pre 41)"; pb="$(artifact b-pre 42)"; rm -rf "$barrier"; mkdir "$barrier"
  for source in a b; do (
    : >"$barrier/$source.ready"; while [ ! -f "$barrier/release" ]; do sleep .02; done
    set +e; bash "$helper" --repo-root "$fixture_repo" --run-root "$run_root" --operation move --target "$source" --preimage "$( [ "$source" = a ] && echo "$pa" || echo "$pb" )" --destination destination >"$barrier/$source.out" 2>"$barrier/$source.err"; echo $? >"$barrier/$source.exit"
  ) & done
  local ticks=0; while { [ ! -f "$barrier/a.ready" ] || [ ! -f "$barrier/b.ready" ]; } && [ "$ticks" -lt 250 ]; do sleep .02; ticks=$((ticks+1)); done
  [ "$ticks" -lt 250 ] || fail 'R36-CONCURRENCY destination barrier timeout'; : >"$barrier/release"; wait
  "$python_bin" - "$barrier" "$fixture_repo" <<'PY'
import json,sys
from pathlib import Path
b,r=map(Path,sys.argv[1:]); rows=[]
for n in ('a','b'):
 code=int((b/f'{n}.exit').read_text()); rec=json.loads((b/f'{n}.out').read_text()); rows.append((n,code,rec['status']))
if sorted((x[1],x[2]) for x in rows)!=[(0,'COMMITTED'),(65,'CONFLICT_REBASE')]: raise SystemExit(f'R36-CONCURRENCY statuses {rows!r}')
winner=next(n for n,c,s in rows if s=='COMMITTED'); loser='b' if winner=='a' else 'a'
if (r/'destination').read_bytes()!=winner.encode() or (r/loser).read_bytes()!=loser.upper().encode() or (r/winner).exists(): raise SystemExit('R36-CONCURRENCY filesystem postcondition failed')
PY
  # lock cleanup: a fresh, disjoint operation must not remain blocked by loser residue.
  local pt pc; pt="$(artifact follow-pre 4142434445)"; pc="$(artifact follow-candidate 4e4557)"; invoke R36-CONCURRENCY-follow COMMITTED replace target - "$pc" 4e4557 --preimage "$pt" --candidate "$pc"
}

opposing_moves() {
  setup
  local pa pb barrier="$tmp/barrier-opposing"; pa="$(artifact opposing-a 41)"; pb="$(artifact opposing-b 42)"; rm -rf "$barrier"; mkdir "$barrier"
  for source in a b; do (
    : >"$barrier/$source.ready"; while [ ! -f "$barrier/release" ]; do sleep .02; done
    destination=b; [ "$source" = b ] && destination=a
    pre="$pb"; [ "$source" = a ] && pre="$pa"
    set +e; bash "$helper" --repo-root "$fixture_repo" --run-root "$run_root" --operation move --target "$source" --preimage "$pre" --destination "$destination" >"$barrier/$source.out" 2>"$barrier/$source.err"; echo $? >"$barrier/$source.exit"
  ) & done
  local ticks=0; while { [ ! -f "$barrier/a.ready" ] || [ ! -f "$barrier/b.ready" ]; } && [ "$ticks" -lt 250 ]; do sleep .02; ticks=$((ticks+1)); done
  [ "$ticks" -lt 250 ] || fail 'R36-OPPOSING barrier timeout'; : >"$barrier/release"; wait
  "$python_bin" - "$barrier" "$fixture_repo" <<'PY'
import json,sys
from pathlib import Path
b,r=map(Path,sys.argv[1:])
for n in ('a','b'):
 if int((b/f'{n}.exit').read_text()) != 64 or json.loads((b/f'{n}.out').read_text())['status'] != 'REJECTED_NO_MUTATION': raise SystemExit('R36-OPPOSING did not fail closed')
if (r/'a').read_bytes()!=b'A' or (r/'b').read_bytes()!=b'B': raise SystemExit('R36-OPPOSING changed either source')
PY
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
  local actor=$! ticks=0 actual status post record journal token
  while [ ! -f "$barrier/actor-ready" ] && [ "$ticks" -lt 250 ]; do sleep .02; ticks=$((ticks+1)); done
  [ "$ticks" -lt 250 ] || fail 'R36-DRIFT actor barrier timeout'
  : >"$barrier/release"
  set +e; bash "$helper" --repo-root "$fixture_repo" --run-root "$run_root" --operation replace --target target --preimage "$pre" --candidate "$candidate" >"$stdout" 2>"$stderr"; actual=$?; set -e
  wait "$actor" || fail "R36-DRIFT actor did not observe candidate publication"
  [ -f "$barrier/actor-fired" ] || fail 'R36-DRIFT actor did not fire'
  status="$($python_bin - "$stdout" <<'PY'
import json,sys
print(json.loads(open(sys.argv[1],encoding='utf-8').read())['status'])
PY
)"
  case "$status" in POST_COMMIT_DRIFT|ROLLBACK_CONFLICT|ROLLBACK_FAILED_WITH_RESIDUE) ;; *) fail "R36-DRIFT non-residual status $status";; esac
  [ "$actual" -eq "$(status_exit "$status")" ] || fail "R36-DRIFT exit/status mismatch"
  post="$(identity_json "$fixture_repo/target")"
  last_record="$(assert_response R36-DRIFT "$status" replace target - '["target"]' "$pre_id" "$(identity_json "$candidate")" "$post" "$(<"$stdout")")"
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
  # Correct token is exercised against the recreated winner; it must retain a
  # residual conflict rather than overwrite the external winner.
  set +e; bash "$helper" --repo-root "$fixture_repo" --run-root "$run_root" --operation recover --target target --journal "$journal" --token "$token" >"$tmp/recover.out" 2>"$tmp/recover.err"; actual=$?; set -e
  status="$($python_bin - "$tmp/recover.out" <<'PY'
import json,sys
print(json.loads(open(sys.argv[1],encoding='utf-8').read())['status'])
PY
)"
  case "$status" in ROLLBACK_CONFLICT|ROLLBACK_FAILED_WITH_RESIDUE|RECOVERY_REQUIRED) ;; *) fail "R36-DRIFT correct-token status $status";; esac
  [ "$actual" -eq "$(status_exit "$status")" ] || fail 'R36-DRIFT correct-token exit mismatch'
  assert_hex R36-DRIFT-correct-token-winner "$fixture_repo/target" 45585445524e414c2d57494e4e4552
}

state_family() {
  local pre cand region repl
  setup; pre="$(artifact c1-pre 414243)"; cand="$(artifact c1-candidate 5a)"; invoke R36-C1 REJECTED_NO_MUTATION replace target - "$cand" 4142434445 --preimage "$pre" --candidate "$cand"
  setup; pre="$(artifact c2-pre 4142434445)"; cand="$(artifact c2-candidate 5a)"; write_hex "$fixture_repo/target" 494e54455256454e494e47; invoke R36-C2 CONFLICT_REBASE replace target - "$cand" 494e54455256454e494e47 --preimage "$pre" --candidate "$cand"
  # C3 is intentionally collapsed into the actual invariant: a byte-equal,
  # complete current preimage is the only qualifying observation.
  setup; pre="$(artifact c3-partial 414243)"; cand="$(artifact c3-candidate 5a)"; invoke R36-C3 REJECTED_NO_MUTATION replace target - "$cand" 4142434445 --preimage "$pre" --candidate "$cand"
  setup; pre="$(artifact c4-pre 4142434445)"; cand="$(artifact c4-candidate 5a)"; write_hex "$fixture_repo/sentinel" 53414645; invoke R36-C4 REJECTED_NO_MUTATION replace target - "$cand" 4142434445 --preimage "$pre" --candidate "$cand" --arbitrary-mutator 'sh -c touch-sentinel'; assert_hex R36-C4-sentinel "$fixture_repo/sentinel" 53414645
  setup; region="$(artifact crlf-region 74776f0d0a)"; repl="$(artifact crlf-repl 54574f0d0a)"; invoke R36-B1 COMMITTED patch crlf - "$repl" 6f6e650d0a54574f0d0a74687265650d0a --offset 5 --region "$region" --replacement "$repl"
  setup; region="$(artifact unicode-region e282ac2de4b8ade69687)"; repl="$(artifact unicode-repl f09f9880)"; invoke R36-B2 COMMITTED patch unicode - "$repl" 7072656669782df09f98802d737566666978 --offset 7 --region "$region" --replacement "$repl"
  setup; region="$(artifact split-region e2)"; repl="$(artifact split-repl 58)"; invoke R36-B2-split REJECTED_NO_MUTATION patch unicode - "$repl" 7072656669782de282ac2de4b8ade696872d737566666978 --offset 7 --region "$region" --replacement "$repl"
  setup; region="$(artifact empty-region '')"; repl="$(artifact empty-repl 58)"; invoke R36-B2-empty REJECTED_NO_MUTATION patch target - "$repl" 4142434445 --offset 0 --region "$region" --replacement "$repl"
  setup; pre="$(artifact binary-pre 0001ff7f42494e0d0a)"; cand="$(artifact binary-candidate ff0042494e2d)"; invoke R36-B3 COMMITTED replace binary - "$cand" ff0042494e2d --preimage "$pre" --candidate "$cand"; pre="$(artifact binary-delete-pre ff0042494e2d)"; invoke R36-B4 COMMITTED delete binary - - - --preimage "$pre"; setup; pre="$(artifact binary-move-pre 0001ff7f42494e0d0a)"; invoke R36-B5 COMMITTED move binary binary-destination "$pre" 0001ff7f42494e0d0a --preimage "$pre" --destination binary-destination
  setup; pre="$(artifact hard-pre 5349424c494e47)"; cand="$(artifact hard-candidate 4e4557)"; invoke R36-T1 COMMITTED replace hardlink - "$cand" 4e4557 --preimage "$pre" --candidate "$cand"; assert_hex R36-T1-sibling "$fixture_repo/sibling" 5349424c494e47
  setup; pre="$(artifact scope-pre 4142434445)"; cand="$(artifact scope-candidate 4e4557)"; invoke R36-T2 REJECTED_NO_MUTATION replace ../existing-outside-target - "$cand" 4f555453494445 --preimage "$pre" --candidate "$cand"; [ "$(cat "$fixture_repo/symlink-capability")" = yes ] && { pre="$(artifact link-pre 4142434445)"; invoke R36-T3 REJECTED_NO_MUTATION replace final-link - "$cand" 4142434445 --preimage "$pre" --candidate "$cand"; pre="$(artifact parent-pre 6368696c64)"; invoke R36-T4 REJECTED_NO_MUTATION replace parent-link/child - "$cand" 6368696c64 --preimage "$pre" --candidate "$cand"; }
  setup; pre="$(artifact stale-delete-pre 414243)"; invoke R36-D1 REJECTED_NO_MUTATION delete target - - 4142434445 --preimage "$pre"; pre="$(artifact stale-move-pre 414243)"; invoke R36-D2 REJECTED_NO_MUTATION move target absent-destination "$pre" 4142434445 --preimage "$pre" --destination absent-destination
  setup; pre="$(artifact stale-move-full-pre 4142434445)"; write_hex "$fixture_repo/target" 4c41544552; invoke R36-D2-currentness CONFLICT_REBASE move target absent-destination "$pre" 4c41544552 --preimage "$pre" --destination absent-destination
  setup; pre="$(artifact move-pre 4142434445)"; write_hex "$fixture_repo/existing-destination" 455849535453; invoke R36-D3 REJECTED_NO_MUTATION move target existing-destination "$pre" 4142434445 --preimage "$pre" --destination existing-destination; assert_hex R36-D3-destination "$fixture_repo/existing-destination" 455849535453
  setup; pre="$(artifact same-pre 4142434445)"; invoke R36-D4 REJECTED_NO_MUTATION move target target "$pre" 4142434445 --preimage "$pre" --destination target
  setup; mkdir "$fixture_repo/directory-target"; pre="$(artifact regular-pre 4142434445)"; cand="$(artifact regular-candidate 4e4557)"; invoke R36-D5 REJECTED_NO_MUTATION replace directory-target - "$cand" - --preimage "$pre" --candidate "$cand"
  concurrent_destination
  opposing_moves
  external_drift_and_recovery
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
state_family
