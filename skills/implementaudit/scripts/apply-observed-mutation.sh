#!/usr/bin/env bash
exec python3 - "$@" <<'PY'
import argparse,hashlib,json,os,secrets,stat,sys,time
from pathlib import Path
X={'COMMITTED':0,'NO_CHANGE':0,'REJECTED_NO_MUTATION':64,'CONFLICT_REBASE':65,'MUTATION_FAILED_NO_STATE_CHANGE':70,'MUTATION_FAILED_ROLLED_BACK':71,'POST_STATE_MISMATCH_ROLLED_BACK':72,'RECOVERY_REQUIRED':73,'ROLLBACK_CONFLICT':74,'ROLLBACK_FAILED_WITH_RESIDUE':75,'POST_COMMIT_DRIFT':76,'UNSUPPORTED_OWNER_DECISION':77}
def I(b): return {'sha256':hashlib.sha256(b).hexdigest(),'byte_length':len(b)}
def reg(p):
 try:return stat.S_ISREG(os.lstat(p).st_mode)
 except FileNotFoundError:return False
def links(p,stop=None):
 p=Path(p)
 try:
  while 1:
   if p.is_symlink():return False
   if stop and p==stop:return True
   if p.parent==p:return not stop
   p=p.parent
 except OSError:return False
def ident(p): return I(Path(p).read_bytes()) if reg(p) and links(p,R) else None
def raw(p): return Path(p).read_bytes() if reg(p) and links(p,R) else None
def rel(s):return bool(s) and not os.path.isabs(s) and '..' not in Path(s).parts
def phase_hook(phase):
    # R36_INSTRUMENT_INSERT
    return
p=argparse.ArgumentParser(add_help=False);p.add_argument('--repo-root',required=True);p.add_argument('--run-root',required=True);p.add_argument('--operation',required=True);p.add_argument('--target',required=True);p.add_argument('--preimage');p.add_argument('--candidate');p.add_argument('--destination');p.add_argument('--offset');p.add_argument('--region');p.add_argument('--replacement');p.add_argument('--journal');p.add_argument('--token');p.add_argument('--arbitrary-mutator',nargs=2)
try:a,u=p.parse_known_args()
except SystemExit:sys.exit(64)
R=Path(a.repo_root).resolve();T=R/a.target;D=R/a.destination if a.destination else None;op=a.operation
pre0=I(Path(T).read_bytes()) if reg(T) and links(T) else None
def out(s,pre=pre0,cand=None,post=None,j=None,tok=None,res=()):
 q=T if post is None else post; ps={a.target:ident(T)}
 if D:ps[a.destination]=ident(D)
 print(json.dumps({'schema':'implementaudit.observation_bound_mutation.v1','operation':op,'status':s,'source_path':a.target,'destination_path':a.destination,'targets':[a.target]+([a.destination] if D else []),'pre_identity':pre,'candidate_identity':cand,'post_identity':ident(q),'post_identities':ps,'token':tok,'journal_path':str(j) if j else None,'residue_paths':[str(x) for x in res]},separators=(',',':')));sys.exit(X[s])
def early():
 q=Path(a.candidate or a.preimage) if (a.candidate or a.preimage) else None;b=raw(q) if q else None;return I(b) if b is not None else None
if u or op not in ('patch','replace','delete','move','recover'):out('REJECTED_NO_MUTATION')
run=Path(a.run_root);run=run if run.is_absolute() else R/run
if not (R.is_dir() and R in run.parents and (run/'.claimed').is_file()):out('REJECTED_NO_MUTATION')
if not rel(a.target) or not links(T,R) or not T.parent.exists() or not links(T.parent,R):out('REJECTED_NO_MUTATION',cand=early())
if op=='recover':
 # Portable same-principal files cannot prove that a caller-created journal is
 # helper authority. Recovery is therefore owner-gated/manual custody, never
 # an automatic caller-driven mutation path.
 out('REJECTED_NO_MUTATION')
if op=='move' and (not rel(a.destination) or a.destination==a.target or not links(D.parent,R)):out('REJECTED_NO_MUTATION',cand=early())
pre=raw(a.preimage) if a.preimage else None
if op in ('replace','delete','move') and pre is None:out('REJECTED_NO_MUTATION',cand=early())
c=None
if op=='replace':
 c=raw(a.candidate)
 if c is None:out('REJECTED_NO_MUTATION')
elif op=='patch':
 g=raw(a.region);z=raw(a.replacement);now=raw(T)
 try:o=int(a.offset)
 except:out('REJECTED_NO_MUTATION')
 if now is None or g is None or z is None or o<0 or not g or now[o:o+len(g)]!=g:out('REJECTED_NO_MUTATION')
 c=now[:o]+z+now[o+len(g):]
if a.arbitrary_mutator:out('REJECTED_NO_MUTATION',cand=I(c) if c is not None else None)
now=raw(T)
if now is None:out('REJECTED_NO_MUTATION',cand=I(pre if op=='move' else c) if (op=='move' or c is not None) else None)
if op in ('replace','delete','move') and now!=pre:out('REJECTED_NO_MUTATION' if now.startswith(pre) else 'CONFLICT_REBASE',cand=I(pre if op=='move' else c) if (op=='move' or c is not None) else None)
if op=='replace' and c==now:out('NO_CHANGE',cand=I(c))
if op=='move' and D.exists():out('REJECTED_NO_MUTATION',cand=I(pre))
bar=None;fault=None;phase_hook('init')
def wait(name,release='release'):
 if not bar:return
 b=Path(bar);b.mkdir(parents=True,exist_ok=True);(b/name).touch()
 for _ in range(500):
  if (b/release).exists():return
  time.sleep(.02)
 raise RuntimeError('timeout')
if fault=='pre-displacement':wait('paused');out('MUTATION_FAILED_NO_STATE_CHANGE',cand=I(c) if c is not None else None)
if fault=='unsupported-external-writer':
 wait('paused');wait('observed-after-external','continue-after-external');out('UNSUPPORTED_OWNER_DECISION',cand=I(c))
if bar and not fault:
 wait('observed')
 if raw(T)!=now or (op=='move' and D.exists()):out('CONFLICT_REBASE',cand=I(pre if op=='move' else c))
L=R/'.IMPLEMENTAUDIT'/'.r36-locks'
if L.is_symlink() or (L.exists() and not L.is_dir()):out('UNSUPPORTED_OWNER_DECISION',cand=I(pre if op=='move' else c) if (op=='move' or c is not None) else None)
L.mkdir(parents=True,exist_ok=True);owner=secrets.token_hex(16);held=[];initial=bool(op=='move' and D.exists())
try:
 obj=os.lstat(T); keys=[a.target]+([a.destination] if op=='move' else [])+[f'object:{obj.st_dev}:{obj.st_ino}']
 for k in sorted(keys):
  q=L/(hashlib.sha256(k.encode()).hexdigest()+'.lock')
  try:
   os.mkdir(q);(q/'owner').write_text(owner);held.append(q)
  except FileExistsError:out('CONFLICT_REBASE',cand=I(pre if op=='move' else c))
 if initial:out('REJECTED_NO_MUTATION',cand=I(pre))
 if raw(T)!=now or (op=='move' and D.exists()):out('CONFLICT_REBASE',cand=I(pre if op=='move' else c))
 if op=='move':
  time.sleep(.05)
  # Re-read immediately before the absent-only publish; a writer that changed
  # the source during lock acquisition cannot be moved under an old preimage.
  if raw(T)!=pre or D.exists():out('CONFLICT_REBASE',cand=I(pre))
  tok=secrets.token_hex(16);J=run/('.r36-journal-'+tok+'.json')
  # A move has a real intermediate state: destination published while the
  # source still names the same bytes.  Record it durably before publication;
  # after a crash this is manual-custody residue, never an implicit copy.
  with J.open('w',encoding='utf-8') as jf:
   json.dump({'token':tok,'operation':'move','target':a.target,'destination':a.destination,'pre_identity':I(pre),'candidate_identity':I(pre),'recovery_disposition':'RECOVERY_REQUIRED'},jf,separators=(',',':'));jf.flush();os.fsync(jf.fileno())
  try:os.link(T,D)
  except FileExistsError:
   J.unlink();out('CONFLICT_REBASE',cand=I(pre))
  except OSError:
   J.unlink();out('UNSUPPORTED_OWNER_DECISION',cand=I(pre))
  phase_hook('move-destination-published')
  # Do not remove a source that changed after link publication.  The exact
  # destination and journal remain for manual owner disposition.
  if raw(T)!=pre or raw(D)!=pre:out('RECOVERY_REQUIRED',cand=I(pre),j=J,tok=tok,res=[D])
  os.unlink(T)
  J.unlink()
  out('COMMITTED',cand=I(pre),post=D)
 tok=secrets.token_hex(16);B=run/('.r36-backup-'+tok);J=run/('.r36-journal-'+tok+'.json')
 # The journal is durable before the first destructive rename.
 with J.open('w',encoding='utf-8') as jf:
  json.dump({'token':tok,'target':a.target,'backup':str(B),'pre_identity':I(now),'candidate_identity':I(c) if c is not None else None,'recovery_disposition':'RECOVERY_REQUIRED'},jf,separators=(',',':'));jf.flush();os.fsync(jf.fileno())
 os.replace(T,B)
 if fault=='after-displacement':wait('paused');os.link(B,T);B.unlink();J.unlink();out('MUTATION_FAILED_ROLLED_BACK',cand=I(c) if c else None)
 if op=='delete':os.unlink(B);J.unlink();out('COMMITTED')
 S=run/('.r36-stage-'+secrets.token_hex(8));S.write_bytes(c);os.link(S,T);S.unlink()
 if fault=='after-publication':wait('paused');os.unlink(T);os.link(B,T);B.unlink();J.unlink();out('MUTATION_FAILED_ROLLED_BACK',cand=I(c))
 if fault=='post-state-mismatch':
  wait('paused');wait('observed-after-external','continue-after-external');
  if reg(T):os.unlink(T)
  os.link(B,T);B.unlink();J.unlink();out('POST_STATE_MISMATCH_ROLLED_BACK',cand=I(c))
 for _ in range(30):
  if raw(T)!=c:break
  time.sleep(.005)
 if raw(T)!=c:
  out('ROLLBACK_CONFLICT',cand=I(c),j=J,tok=tok,res=[B])
 B.unlink();J.unlink();out('COMMITTED',cand=I(c))
finally:
 for q in held:
  try:
   if (q/'owner').read_text()==owner: (q/'owner').unlink();os.rmdir(q)
  except OSError:pass
PY
