"""Import-safe positive Y04 constructor. Proposals only; never installs or runs."""
import hashlib,json,os,re,stat
from pathlib import Path
HERE=Path(__file__).resolve().parent
PINS=dict(binding_owner='2e784dbbe8470cd2de335e07c66ea0112d7c324b292a21f1f236309d5d0be1fa',
 handler='e180069d3810903a138e64751d71fe8952049967a0ef0deff1e6306c42f749e0',
 validator='7787569b4bceb541c33ee3287f0a8297882caff5478687e84fc534077e4c28ad',
 custody='d52369e56c9e06d0b10b43ddffbae8f353c37b53aac8f7642bbaea356c31a389',
 python='5f7b89a612c9b8af1d6456cdfcd1dbe5ca630849e79aebced9bee9a6694952ec')
PROJECTION=('host_id','host_session_id','binding_generation','controller_id','claim_id','explicit_run_root',
 'repository_identity','git_common_directory_identity','worktree_identity','applicable_continuity_generation','applicable_continuity_receipt')
FIELDS=('host_session_id','controller_id','claim_id','explicit_run_root','repository_identity','git_common_directory_identity',
 'worktree_identity','applicable_continuity_generation','applicable_continuity_receipt','activation_event_id','activation_receipt')
def digest(b):return hashlib.sha256(b).hexdigest()
def text(v):
 if not isinstance(v,str) or not v or any(ord(c)<32 for c in v):raise ValueError('Missing/control-bearing actual input')
 return v
def path(v):
 p=Path(text(str(v)))
 if not p.is_absolute() or any(c in str(p) for c in '$`"') or '..' in p.parts:raise ValueError('Unsafe/nonabsolute path')
 for x in (p,*p.parents):
  if x.exists():
   st=x.lstat()
   if stat.S_ISLNK(st.st_mode) or getattr(st,'st_file_attributes',0)&0x400:raise ValueError('Aliased/reparse path')
 return p
def pinned(v,pin,maximum):
 p=path(v);before=p.lstat()
 if not stat.S_ISREG(before.st_mode) or before.st_nlink!=1 or before.st_size>maximum:raise ValueError('Unsafe pinned member')
 ident=lambda s:(s.st_dev,s.st_ino,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns,getattr(s,'st_file_attributes',None),getattr(s,'st_reparse_tag',None))
 with p.open('rb') as f:
  opened=os.fstat(f.fileno())
  if not stat.S_ISREG(opened.st_mode) or opened.st_nlink!=1 or getattr(opened,'st_file_attributes',0)&0x400 or getattr(opened,'st_reparse_tag',0) or ident(opened)!=ident(before):raise ValueError('Opened pin type/link/reparse/identity differs before payload')
  b=f.read(maximum+1);closed=os.fstat(f.fileno())
 after=p.lstat()
 if ident(before)!=ident(opened) or ident(opened)!=ident(closed) or ident(after)!=ident(before):raise ValueError('Pin identity drift')
 if before.st_mode!=after.st_mode or opened.st_mode!=closed.st_mode:raise ValueError('Per-API mode drift')
 if len(b)!=before.st_size or digest(b)!=pin:raise ValueError('Wrong exact source bytes')
 return dict(path=str(p),bytes=len(b),sha256=pin)
def expected_binding(inputs):
 """Prospective initialB dictionary, not evidence B occurred. ActualA fields only."""
 actual={k:text(inputs[k]) for k in FIELDS}
 if not re.fullmatch(r'[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}',actual['host_session_id']):raise ValueError('Actual native thread UUID required')
 if not re.fullmatch(r'[0-9a-f]{32}',actual['claim_id']):raise ValueError('Actual claim ID required')
 if not re.fullmatch(r'[a-z0-9][a-z0-9-]{0,47}',actual['controller_id']):raise ValueError('Actual controller required')
 g=actual['applicable_continuity_generation']
 if not re.fullmatch(r'G[0-9A-F]{4}',g):raise ValueError('Actual continuity generation required')
 token=actual['applicable_continuity_receipt']
 if not re.fullmatch('refs/implementaudit/continuity-receipts/'+re.escape(actual['controller_id'])+'/'+g+r'@[0-9a-f]{40}',token):raise ValueError('Actual receipt/controller/generation disagree')
 for k in ('explicit_run_root','repository_identity','git_common_directory_identity','worktree_identity'):actual[k]=str(path(actual[k]))
 root=Path(actual['explicit_run_root']);repo=Path(actual['repository_identity']);worktree=Path(actual['worktree_identity'])
 if repo!=worktree or not root.is_relative_to(worktree):raise ValueError('Actual run/worktree custody mismatch')
 return dict(schema='implementaudit.host-session-binding.v1',host_id='codex',**actual,binding_generation='G0001',
  status='ACTIVE',predecessor_generation=None,supersession_or_tombstone_reason=None)
def verify_bound_result(inputs,result):
 """Call after actualB init/bind/lookup. No store read, bind or authority grant."""
 if not isinstance(result,dict) or result.get('status')!='BOUND' or result.get('binding')!=expected_binding(inputs):
  raise ValueError('Actual B full dictionary differs from exact expected fresh binding')
 return {k:result['binding'][k] for k in PROJECTION}
def build(inputs,output_dir):
 """Build private policy/launcher/hook PROPOSALS after actualA; effectful B separate."""
 out=path(output_dir)
 if not out.is_relative_to(HERE) or out==HERE or out.exists():raise ValueError('Fresh constructor-private output required')
 expected=expected_binding(inputs);repo=path(expected['repository_identity']);root=path(expected['explicit_run_root'])
 if not repo.is_dir() or not root.is_dir():raise ValueError('Actual post-A repository/run must exist')
 store=path(inputs['binding_store']);events=path(inputs['evidence_directory'])
 if any(store.is_relative_to(path(expected[k])) for k in ('repository_identity','git_common_directory_identity','worktree_identity')):
  raise ValueError('Binding store must be external to actual repository/common/worktree')
 # Supported transport permits a separate CASE evidence directory. Actual
 # CASE/write-set authority is independently bound by the StageA/B operation;
 # this constructor validates its exact path but never creates or writes it.
 hook_target=repo/'.codex/hooks.json'
 if os.path.lexists(hook_target):raise ValueError('Existing project definition must not be overwritten')
 evidence=[]
 # These are actual records to inspect independently, never self-authenticating permissions.
 for key in ('actual_stage_a_receipt','owner_approval_receipt'):
  d=inputs[key];evidence.append(pinned(d['path'],d['sha256'],2*1024*1024))
 if evidence[1]['sha256']!='05a0767e4a4a72eb7ff13f11bf9341a270b46954bab0e8e57e3e6c7bfa411aff':raise ValueError('Wrong actual owner approval carrier')
 sources={k:pinned(inputs[k],pin,16*1024*1024 if k=='python' else 1024*1024) for k,pin in PINS.items()}
 if Path(sources['custody']['path'])!=Path(sources['handler']['path']).with_name('canonical_custody.py'):raise ValueError('Handler custody sibling differs')
 bash=pinned(inputs['bash'],text(inputs['bash_sha256']),32*1024*1024)
 python=Path(sources['python']['path'])
 if python!=Path(r'C:\Users\theis\AppData\Local\Programs\Python\Python311\python.exe'):raise ValueError('Fixed Python311 required')
 fixed_path=str(python.parent)+r';C:\Program Files\Git\cmd;C:\Program Files\Git\usr\bin;C:\Windows\System32;C:\Windows'
 if inputs['fixed_path']!=fixed_path:raise ValueError('PATH differs from fixed reviewed path')
 policy=dict(schema='implementaudit.codex-stop-policy.v2',session_id=expected['host_session_id'],cwd=str(repo),
  binding_store=str(store),binding_owner=sources['binding_owner']['path'],binding_owner_sha256=PINS['binding_owner'],
  binding={k:expected[k] for k in PROJECTION},validator=sources['validator']['path'],validator_sha256=PINS['validator'],
  bash=bash['path'],timeout_seconds=45,path=fixed_path,evidence_directory=str(events),disposition=dict(kind='NONTERMINAL_YIELD'),
  authority_scope='Exact newly approved Y04 positive only, conditional independent post-A gates and actual freshB match; parent/programme stay open.',
  native_acceptance='Prospective source proposal only; actual hook/principal/effective readOnly networkfalse/trust/currentness/observation require independent actual receiving.')
 policy_bytes=(json.dumps(policy,indent=2,ensure_ascii=False)+'\n').encode();policy_path=out/'Y04_NONTERMINAL_POLICY.json';policy_sha=digest(policy_bytes)
 source=sources['handler']['path']
 # Reuse the supported exact-buffer -I/-S/-B architecture. No external launcher
 # file is reloaded as code: the reviewed literal command compiles one pinned buffer.
 launcher=("import os,stat,hashlib; identity=lambda s:(s.st_dev,s.st_ino,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns); p="+repr(source)+"; n=os.lstat(p); "
  "assert stat.S_ISREG(n.st_mode) and n.st_nlink==1 and not n.st_file_attributes&1024; "
  "f=os.open(p,os.O_RDONLY|os.O_BINARY|os.O_NOINHERIT); h=os.fdopen(f,'rb'); s=os.fstat(h.fileno()); "
  "assert (s.st_dev,s.st_ino)==(n.st_dev,n.st_ino) and stat.S_ISREG(s.st_mode); b=h.read(131073); "
  "assert identity(os.fstat(h.fileno()))==identity(s) and identity(os.lstat(p))==identity(n); h.close(); "
  "assert len(b)<=131072 and hashlib.sha256(b).hexdigest()=="+repr(PINS['handler'])+"; "
  "exec(compile(b,p,'exec'),{'__name__':'__main__','__file__':p})")
 command=str(python)+' -I -S -B -c "'+launcher.replace('"','`"')+'" --codex-stop-policy "'+str(policy_path)+'" '+policy_sha
 hook=dict(description='DG17 exact fresh-session positive nonterminal Stop; parent remains open. Proposal only.',
  hooks={'Stop':[{'hooks':[dict(type='command',command=command,commandWindows=command,timeout=60,statusMessage='DG17 bounded positive nonterminal Stop')]}]})
 hook_bytes=(json.dumps(hook,indent=2,ensure_ascii=False)+'\n').encode()
 out.mkdir(parents=False,exist_ok=False)
 for name,b in (('Y04_NONTERMINAL_POLICY.json',policy_bytes),('hooks.json.PROPOSAL',hook_bytes),('VERIFIED_BUFFER_LAUNCHER.txt',launcher.encode()+b'\n')):
  with (out/name).open('xb') as f:f.write(b)
 manifest=dict(schema='ordinary.dg17.parameterized-positive-hook-proposal.v1',status='INERT_PROPOSAL_B_INIT_BIND_TRUST_AND_NATIVE_EFFECTS_NOT_PERFORMED',
  intended_project_hook_path=str(hook_target),hook_proposal_path=str(out/'hooks.json.PROPOSAL'),hook_sha256=digest(hook_bytes),
  policy_path=str(policy_path),policy_sha256=policy_sha,commandWindows=command,launcher_source_sha256=digest(launcher.encode()),
  expected_initial_B_full_binding=expected,expected_policy_binding_projection=policy['binding'],
  binding_status='EXPECTED_G0001_ONLY_AFTER_ACTUAL_B_INIT_BIND; verify_bound_result must pass full equality beforeenable',
  source_readset=sources,host_bash=bash,actual_input_receipts=evidence,
  required_actual_runtime=dict(model_sandbox='readOnly',model_network=False,hook_permission_mode='bypassPermissions ONLY for this exact fixed reviewedcommand',
    independent_post_A_review='Required; code proposal, field equality or hash alone is not actual permission/principal/nativeactivation proof',
    inner_guard_seconds=10,record_guard_seconds=45,hook_guard_seconds=60),
  runtime_definition_key=None,runtime_current_hash=None,trust_applied=False,source_or_CASE_config_written=False,
  effects='Only private proposal outputs under constructor directory. No subprocess, preflight validator, claim, bind, H0, hook installation/trust/config/native/model/public effect.')
 with (out/'MANIFEST.json').open('xb') as f:f.write((json.dumps(manifest,indent=2,ensure_ascii=False)+'\n').encode())
 return manifest
