"""Same-host fixed-file observation, then separately received root adoption.

Observation performs ordinary file reads only. It cannot create a recipient or
run a command. The immutable declaration contains no executable tool pin and
is never accepted as a Commands authorization. Actual root adoption arrives
on its own fixed ref, distinct from the ciphertext protocol and workflow ref.
"""
import base64
import ast
import json
import types
import hashlib
import io
import math
import os
from pathlib import Path
import secrets
import stat
import sys
import time
import zipfile
import carrier_policy as P
import carrier_io as F
import provider_reader as V

PROFILE='DEFERRED_SAME_HOST_FIXED_TOOLS_V1'
PATHS={'env':'/usr/bin/env','openssl':'/usr/bin/openssl'}
MAX_FILE=32*1024**2
MAX_BODY=65536
MAX_ARCHIVE=131072
MAX_PRIVATE_BYTES=4*1024**2
MAX_PRIVATE_ENTRIES=32
MAX_OBSERVATION_SECONDS=60
MAX_ADOPTION_SECONDS=600
_ANCHOR=None  # Installed only by the exact external entry, which pins the manifest.
_ROOT_PROFILE_SOURCE=None  # Root data receiver may supply only this exact pinned public body; never host observations.
OPERATIONS=('recipient','decrypt','prepare')
PHASES=('OPEN','PRE','POST','CLOSE')
FILES={'RESERVED.json':MAX_BODY,'HOST_TOOL_OBSERVATION.json':MAX_BODY,'SESSION.json':MAX_BODY,
 'OBSERVATION_OUTCOME.json':MAX_BODY,'ADOPTION_RESERVED.json':MAX_BODY,'HOST_TOOL_ADOPTION.json':MAX_BODY,
 'ADOPTION_PROVIDER.json':P.MAX_METADATA,'READY.json':MAX_BODY,'ADOPTION_OUTCOME.json':MAX_BODY}
FILES.update({'CURRENT_'+o.upper()+'_'+p+'.json':MAX_BODY for o in OPERATIONS for p in PHASES})

def declaration(binding):
    v=binding['host_tools']
    P.exact(v,('profile','paths','control_branch','control_parent','observation_seconds','adoption_seconds'))
    P.need(v['profile']==PROFILE and v['paths']==PATHS,'HOST_TOOLS_DEFERRED_DECLARATION')
    P.need(type(v['control_branch']) is str and P.re.fullmatch(r'pro/[A-Za-z0-9][A-Za-z0-9/_-]{0,180}',v['control_branch'])
      and '..' not in v['control_branch'] and '//' not in v['control_branch']
      and v['control_branch'] not in (binding['branch'],binding['control_branch']),'HOST_TOOLS_SEPARATE_RESERVED_REF')
    P.need(type(v['control_parent']) is str and P.re.fullmatch('[0-9a-f]{40}',v['control_parent'])
      and v['control_parent']!=binding['control_parent'],'HOST_TOOLS_SEPARATE_CONTROL_ANCESTRY')
    P.integer(v['observation_seconds'],1,MAX_OBSERVATION_SECONDS)
    P.integer(v['adoption_seconds'],1,MAX_ADOPTION_SECONDS)
    return v

def host_identity():
    body=Path('/proc/sys/kernel/random/boot_id').read_text().strip()
    P.need(P.re.fullmatch('[0-9a-f-]{36}',body),'HOST_TOOL_BOOT_ID')
    P.need(os.getuid()==os.geteuid()==0,'HOST_TOOL_ACTUAL_ROOT_HOST_REQUIRED')
    return dict(uid=os.getuid(),euid=os.geteuid(),gid=os.getgid(),egid=os.getegid(),boot_id=body)

def anchor(binding,ctx):
    P.context(ctx);declaration(binding)
    P.need(callable(_ANCHOR),'HOST_TOOL_EXTERNAL_MANIFEST_ANCHOR_REQUIRED')
    value=_ANCHOR(binding,ctx)
    P.exact(value,('public_manifest_sha256','bootstrap_admission_sha256'))
    for pin in value.values():P.digest(pin)
    return value

def directory(binding,ctx):return binding['_packet'].parent/('dg16-host-tools-'+ctx['run_id']+'-a1')

def census(path):
    info=path.lstat()
    P.need(stat.S_ISDIR(info.st_mode) and not path.is_symlink() and info.st_uid==os.geteuid()
      and stat.S_IMODE(info.st_mode)==0o700 and not os.listxattr(path),'HOST_TOOL_DIRECTORY_CUSTODY')
    rows={}
    for entry in sorted(path.iterdir()):
        P.need(entry.name in FILES,'HOST_TOOL_UNKNOWN_MEMBER')
        _,rows[entry.name]=F.read_file(entry,FILES[entry.name],private=True)
    P.need(len(rows)+1<=MAX_PRIVATE_ENTRIES and sum(r['bytes'] for r in rows.values())<=MAX_PRIVATE_BYTES,
      'HOST_TOOL_ACTUAL_ALLOCATION_BOUND')
    return rows

def save(path,name,raw,*,terminal=False):
    P.need(name in FILES and type(raw) is bytes and len(raw)<=FILES[name],'HOST_TOOL_RECORD_SCOPE')
    rows=census(path)
    P.need(name not in rows and len(rows)+2+(0 if terminal else 2)<=MAX_PRIVATE_ENTRIES
      and sum(r['bytes'] for r in rows.values())+len(raw)+(0 if terminal else 2*MAX_BODY)<=MAX_PRIVATE_BYTES,
      'HOST_TOOL_PROSPECTIVE_ALLOCATION')
    return F.write_once(path/name,raw,FILES[name])

def tools_now():
    result={}
    for name,file in PATHS.items():
        raw,row=F.read_file(Path(file),MAX_FILE)
        info=Path(file).lstat()
        P.need(info.st_uid==0 and stat.S_IMODE(info.st_mode)&0o022==0 and os.access(file,os.X_OK)
          and all(x[4]==0 and x[3]&0o022==0 for x in row['ancestors']),'HOST_TOOL_ROOT_FILE_CUSTODY')
        result[name]=dict(path=file,descriptor=P.descriptor(raw),physical=row)
    return result

def _terminal(status,ctx,observation_sha256,adoption_sha256=None):
    return dict(schema='dg16.host-tool-phase-outcome.v1',authority='NONE',status=status,context=ctx,
      observation_sha256=observation_sha256,adoption_sha256=adoption_sha256,
      command_executed=False,crypto_capability_claim=False,original_awards=[])

def _profile_policy(binding,*,observe=False):
    """Only pinned policy/read-data definitions; no Commands or executable owner."""
    pin=binding['core_bodies']['host_utility.py']
    if _ROOT_PROFILE_SOURCE is not None:
        P.need(not observe and type(_ROOT_PROFILE_SOURCE) is bytes,'HOST_PROFILE_CHANGED')
        raw=_ROOT_PROFILE_SOURCE
    else:
        raw,row=F.read_file(Path(__file__).absolute().parent.parent/'host_utility.py',MAX_BODY)
        if '_opening_core' in binding:P.need(row==binding['_opening_core']['host_utility.py'],'HOST_PROFILE_CHANGED')
    P.need(0<len(raw)<=MAX_BODY and P.descriptor(raw)==pin,'HOST_PROFILE_CHANGED')
    names={'_g1_profile_need','g1_host_policy_sha256','select_g1_host_profile','validate_g1_host_profile'}
    if observe:names|={'g1_profile_from_inventory','observe_g1_host_profile'}
    nodes=[];seen=[]
    for n in ast.parse(raw).body:
        if isinstance(n,ast.FunctionDef) and n.name in names:nodes.append(n);seen.append(n.name)
        elif isinstance(n,ast.Assign) and len(n.targets)==1 and isinstance(n.targets[0],ast.Name) and n.targets[0].id=='G1_HOST_PROFILES':nodes.append(n);seen.append('G1_HOST_PROFILES')
    expected=names|{'G1_HOST_PROFILES'}
    P.need(set(seen)==expected and len(seen)==len(expected),'HOST_PROFILE_CHANGED')
    m=types.ModuleType('exact_g1_profile_data');m.__dict__.update(require=P.need,sha=P.sha,json=json,hashlib=hashlib)
    if observe:m.__dict__.update(os=os,sys=sys,Path=Path,checked_file=lambda path,maximum=MAX_BODY:F.read_file(path,maximum)[0])
    exec(compile(ast.fix_missing_locations(ast.Module(body=nodes,type_ignores=[])),'<pinned-G1-policy-data>','exec'),m.__dict__)
    return m

def require_selected_image(binding):
    return _profile_policy(binding,observe=True).observe_g1_host_profile()


def observe(binding,ctx):
    """Closed read-only phase; no Commands import, process or tool execution."""
    declared=declaration(binding);opening_anchor=anchor(binding,ctx);host=host_identity()
    selected_profile=require_selected_image(binding)
    path=directory(binding,ctx);fd,identity=F.private_directory(path);os.close(fd)
    started=time.monotonic();issued=int(time.time()*1000);nonce=secrets.token_hex(32)
    reservation=dict(context=ctx,nonce=nonce,carrier_binding_sha256=P.sha(binding['_binding_raw']),
      issued_unix_ms=issued,operation='READ_ONLY_FIXED_ENV_AND_OPENSSL_BODIES')
    save(path,'RESERVED.json',P.encode(reservation))
    try:
        observed=tools_now()
        P.need(time.monotonic()<started+declared['observation_seconds'] and tools_now()==observed
          and host_identity()==host and anchor(binding,ctx)==opening_anchor
          and require_selected_image(binding)==selected_profile,'HOST_TOOL_OBSERVATION_CLOSING')
        ancestry=F.parents(path/'marker');observed_at=time.monotonic()
        P.need(observed_at<started+declared['observation_seconds'],'HOST_TOOL_OBSERVATION_DEADLINE')
        value=dict(schema='dg16.same-host-fixed-tool-observation.v2',authority='NONE',phase='READ_ONLY_FIXED_TOOL_BODIES',
          context=ctx,source_commit=binding['source_commit'],source_tree=binding['source_tree'],
          carrier_binding_sha256=P.sha(binding['_binding_raw']),input_index_sha256=P.C.check_index(binding['_index']),
          **opening_anchor,host_identity=host,directory_identity=identity,nonce=nonce,issued_unix_ms=issued,
          tools=observed,host_profile=selected_profile,observation_elapsed_ns=max(0,int((observed_at-started)*10**9)),
          command_executed=False,crypto_capability_claim=False,original_awards=[])
        raw=P.encode(value);observation=save(path,'HOST_TOOL_OBSERVATION.json',raw)
        session=dict(schema='dg16.same-host-tool-bootstrap-session.v2',context=ctx,host_identity=host,
          directory_identity=identity,directory_ancestry=ancestry,nonce=nonce,observation=observation,host_profile=selected_profile,
          started_monotonic=started,adoption_deadline_monotonic=started+declared['observation_seconds']+declared['adoption_seconds'],
          latest_command_unix_ms=issued+(declared['observation_seconds']+declared['adoption_seconds']+binding['limits']['acquisition_seconds'])*1000)
        save(path,'SESSION.json',P.encode(session))
        P.need(time.monotonic()<started+declared['observation_seconds'],'HOST_TOOL_OBSERVATION_DEADLINE')
        outcome=_terminal('OBSERVED',ctx,P.sha(raw))
        save(path,'OBSERVATION_OUTCOME.json',P.encode(outcome),terminal=True)
        return dict(files={'HOST_TOOL_OBSERVATION.json':raw},result=outcome)
    except BaseException:
        outcome=_terminal('REFUSED',ctx,None)
        if not (path/'OBSERVATION_OUTCOME.json').exists():save(path,'OBSERVATION_OUTCOME.json',P.encode(outcome),terminal=True)
        raise

def observation_current(binding,ctx):
    path=directory(binding,ctx);rows=census(path)
    s=P.parse(F.read_file(path/'SESSION.json',MAX_BODY,private=True)[0],MAX_BODY)
    P.exact(s,('schema','context','host_identity','directory_identity','directory_ancestry','nonce','observation',
      'started_monotonic','adoption_deadline_monotonic','latest_command_unix_ms','host_profile'))
    raw,row=F.read_file(path/'HOST_TOOL_OBSERVATION.json',MAX_BODY,private=True);v=P.parse(raw,MAX_BODY)
    P.need(s['schema']=='dg16.same-host-tool-bootstrap-session.v2' and s['context']==ctx
      and s['host_identity']==host_identity() and s['directory_identity']==F.directory_id(path.lstat())
      and s['directory_ancestry']==F.parents(path/'marker') and s['observation']==row
      and s['nonce']==v['nonce'] and s['host_profile']==v.get('host_profile'),'HOST_TOOL_SAME_SESSION')
    expected=_terminal('OBSERVED',ctx,P.sha(raw))
    P.need(P.parse(F.read_file(path/'OBSERVATION_OUTCOME.json',MAX_BODY,private=True)[0],MAX_BODY)==expected,
      'HOST_TOOL_OBSERVATION_TERMINAL_JOIN')
    P.exact(v,('schema','authority','phase','context','source_commit','source_tree','carrier_binding_sha256',
      'input_index_sha256','public_manifest_sha256','bootstrap_admission_sha256','host_identity','directory_identity',
      'nonce','issued_unix_ms','tools','observation_elapsed_ns','command_executed','crypto_capability_claim','original_awards','host_profile'))
    expected_anchor=anchor(binding,ctx)
    P.need(v['schema']=='dg16.same-host-fixed-tool-observation.v2' and v['authority']=='NONE'
      and v['phase']=='READ_ONLY_FIXED_TOOL_BODIES' and v['context']==ctx
      and v['source_commit']==binding['source_commit'] and v['source_tree']==binding['source_tree']
      and v['carrier_binding_sha256']==P.sha(binding['_binding_raw'])
      and v['input_index_sha256']==P.C.check_index(binding['_index'])
      and all(v[k]==expected_anchor[k] for k in expected_anchor) and v['host_identity']==host_identity()
      and v['directory_identity']==s['directory_identity'] and v['command_executed'] is False
      and v['crypto_capability_claim'] is False and v['original_awards']==[] and tools_now()==v['tools']
      and _profile_policy(binding).validate_g1_host_profile(v['host_profile'])==require_selected_image(binding),
      'HOST_TOOL_OBSERVATION_CURRENT_BODY')
    declared=declaration(binding);P.digest(v['nonce']);P.integer(v['issued_unix_ms'],0,int(time.time()*1000))
    P.integer(v['observation_elapsed_ns'],0,declared['observation_seconds']*10**9)
    P.need(s['adoption_deadline_monotonic']==s['started_monotonic']+declared['observation_seconds']+declared['adoption_seconds']
      and s['latest_command_unix_ms']==v['issued_unix_ms']+(declared['observation_seconds']+declared['adoption_seconds']+
        binding['limits']['acquisition_seconds'])*1000,'HOST_TOOL_FIXED_TIME_SCOPE')
    return path,s,raw,v,rows

def validate_adoption(raw,observation_raw,binding,now_ms):
    observation=P.parse(observation_raw,MAX_BODY);v=P.parse(raw,MAX_BODY)
    P.need(observation.get('schema')=='dg16.same-host-fixed-tool-observation.v2' and 'host_profile' in observation,'HOST_PROFILE_CHANGED')
    _profile_policy(binding).validate_g1_host_profile(observation['host_profile'])
    keys=('schema','issuer','operation','context','source_commit','source_tree','carrier_binding_sha256','input_index_sha256',
      'public_manifest_sha256','bootstrap_admission_sha256','observation','nonce','host_identity','tools','issued_unix_ms',
      'expires_unix_ms','command_scope','automatic_retry','crypto_capability_claim','core_or_native_effect_grant','original_awards','host_profile')
    P.exact(v,keys)
    wanted=dict(schema='dg16.same-host-fixed-tool-root-adoption.v2',issuer='R5_ROOT_GOVERNOR',
      operation='ADOPT_FIXED_SAME_HOST_TOOL_BODIES',observation=P.descriptor(observation_raw),
      command_scope=['recipient','decrypt'],automatic_retry=False,crypto_capability_claim=False,
      core_or_native_effect_grant=False,original_awards=[])
    for key in ('context','source_commit','source_tree','carrier_binding_sha256','input_index_sha256',
      'public_manifest_sha256','bootstrap_admission_sha256','nonce','host_identity','tools','host_profile'):wanted[key]=observation[key]
    wanted.update(issued_unix_ms=v['issued_unix_ms'],expires_unix_ms=v['expires_unix_ms'])
    P.need(P.encode(v)==P.encode(wanted),'HOST_TOOL_ADOPTION_EXACT_JOIN')
    declared=declaration(binding)
    P.integer(v['issued_unix_ms'],observation['issued_unix_ms'],now_ms)
    P.integer(v['expires_unix_ms'],now_ms+1,observation['issued_unix_ms']+
      (declared['observation_seconds']+declared['adoption_seconds']+binding['limits']['acquisition_seconds'])*1000)
    return v

def check_control(provider,body,binding):
    P.exact(provider,('ref','commit','tree','blob','closing_ref'))
    d=declaration(binding);r=provider['ref'];c=provider['commit'];t=provider['tree']
    P.need(r==provider['closing_ref'] and r.get('ref')=='refs/heads/'+d['control_branch']
      and r.get('object',{}).get('type')=='commit' and r['object']['sha']==c.get('sha')
      and c['sha']!=d['control_parent'] and type(c.get('parents')) is list and len(c['parents'])==1
      and c['parents'][0].get('sha')==d['control_parent'],
      'HOST_TOOL_CONTROL_FRESH_PARENT')
    P.need(c.get('tree',{}).get('sha')==t.get('sha') and t.get('truncated') is False
      and type(t.get('tree')) is list and len(t['tree'])==1,'HOST_TOOL_CONTROL_TREE')
    row=t['tree'][0]
    P.need(row.get('path')=='HOST_TOOL_ADOPTION.json' and row.get('mode')=='100644' and row.get('type')=='blob'
      and row.get('size')==len(body) and row.get('sha')==provider['blob'].get('sha')
      and V.blob(provider['blob'],MAX_BODY)==body,'HOST_TOOL_CONTROL_BODY')
    return c['sha']

def api(binding,token,deadline):
    # A compile-bound separate ref; this cannot select the ciphertext reader.
    d=declaration(binding);copy=dict(binding,control_branch=d['control_branch'],control_parent=d['control_parent'])
    remaining=deadline-time.monotonic();P.need(remaining>0,'HOST_TOOL_PROVIDER_DEADLINE')
    copy['limits']=dict(binding['limits'],acquisition_seconds=max(1,math.ceil(remaining)))
    return V.GitHubReads(copy,token,deadline)

def receive_adoption(binding,ctx,token=None):
    path,s,observation_raw,observation,_=observation_current(binding,ctx)
    P.need(time.monotonic()<s['adoption_deadline_monotonic'],'HOST_TOOL_ADOPTION_DEADLINE')
    save(path,'ADOPTION_RESERVED.json',P.encode(dict(context=ctx,observation=P.descriptor(observation_raw),nonce=observation['nonce'])))
    reader=api(binding,token,s['adoption_deadline_monotonic']);d=declaration(binding)
    try:
        while True:
            observation_current(binding,ctx);ref=reader.get('ref',d['control_branch'])
            P.need(ref.get('ref')=='refs/heads/'+d['control_branch'] and ref.get('object',{}).get('type')=='commit','HOST_TOOL_REF_SCOPE')
            if ref['object']['sha']!=d['control_parent']:break
            remaining=s['adoption_deadline_monotonic']-time.monotonic();P.need(remaining>0,'HOST_TOOL_ADOPTION_DEADLINE')
            time.sleep(min(binding['limits']['poll_seconds'],remaining))
        commit=reader.get('commit',ref['object']['sha']);tree=reader.get('tree',commit.get('tree',{}).get('sha'))
        P.need(type(tree.get('tree')) is list and len(tree['tree'])==1,'HOST_TOOL_CONTROL_TREE')
        blob=reader.get('blob',tree['tree'][0].get('sha'));raw=V.blob(blob,MAX_BODY)
        provider=dict(ref=ref,commit=commit,tree=tree,blob=blob,closing_ref=reader.get('ref',d['control_branch']))
        selected=check_control(provider,raw,binding);adoption=validate_adoption(raw,observation_raw,binding,int(time.time()*1000))
        save(path,'HOST_TOOL_ADOPTION.json',raw);save(path,'ADOPTION_PROVIDER.json',P.encode(provider))
        observation_current(binding,ctx)
        P.need(time.monotonic()<s['adoption_deadline_monotonic'],'HOST_TOOL_ADOPTION_DEADLINE')
        ready=dict(schema='dg16.actual-same-host-tools-ready.v1',authority='NONE',context=ctx,observation=P.descriptor(observation_raw),
          adoption=P.descriptor(raw),control_commit=selected,nonce=observation['nonce'],retained=census(path),
          command_deadline_monotonic=min(s['adoption_deadline_monotonic']+binding['limits']['acquisition_seconds'],
            time.monotonic()+(adoption['expires_unix_ms']-int(time.time()*1000))/1000),
          original_awards=[])
        save(path,'READY.json',P.encode(ready));outcome=_terminal('ADOPTED',ctx,P.sha(observation_raw),P.sha(raw))
        save(path,'ADOPTION_OUTCOME.json',P.encode(outcome),terminal=True);return outcome
    except BaseException:
        outcome=_terminal('REFUSED',ctx,P.sha(observation_raw))
        if not (path/'ADOPTION_OUTCOME.json').exists():save(path,'ADOPTION_OUTCOME.json',P.encode(outcome),terminal=True)
        raise

def read_ready(binding,ctx):
    path,s,oraw,observation,rows=observation_current(binding,ctx)
    ready=P.parse(F.read_file(path/'READY.json',MAX_BODY,private=True)[0],MAX_BODY)
    P.exact(ready,('schema','authority','context','observation','adoption','control_commit','nonce','retained',
      'command_deadline_monotonic','original_awards'))
    raw,_=F.read_file(path/'HOST_TOOL_ADOPTION.json',MAX_BODY,private=True)
    adopted=validate_adoption(raw,oraw,binding,int(time.time()*1000))
    provider=P.parse(F.read_file(path/'ADOPTION_PROVIDER.json',P.MAX_METADATA,private=True)[0],P.MAX_METADATA)
    commit=check_control(provider,raw,binding)
    P.need(ready['schema']=='dg16.actual-same-host-tools-ready.v1' and ready['authority']=='NONE'
      and ready['context']==ctx and ready['observation']==P.descriptor(oraw) and ready['adoption']==P.descriptor(raw)
      and ready['control_commit']==commit and ready['nonce']==observation['nonce'] and ready['original_awards']==[]
      and type(ready['command_deadline_monotonic']) in (int,float)
      and time.monotonic()<ready['command_deadline_monotonic']<=s['adoption_deadline_monotonic']+binding['limits']['acquisition_seconds'],
      'HOST_TOOL_READY_EXACT_JOIN')
    required={'RESERVED.json','HOST_TOOL_OBSERVATION.json','SESSION.json','OBSERVATION_OUTCOME.json',
      'ADOPTION_RESERVED.json','HOST_TOOL_ADOPTION.json','ADOPTION_PROVIDER.json'}
    P.need(type(ready['retained']) is dict and set(ready['retained'])==required
      and all(ready['retained'][n]==rows[n] for n in required),'HOST_TOOL_READY_ACTUAL_RETAINED_BODIES')
    outcome=P.parse(F.read_file(path/'ADOPTION_OUTCOME.json',MAX_BODY,private=True)[0],MAX_BODY)
    P.need(outcome==_terminal('ADOPTED',ctx,P.sha(oraw),P.sha(raw)),'HOST_TOOL_ADOPTION_TERMINAL_CONJUNCTION')
    return dict(path=path,ready=ready,adoption=adopted,observation=observation,
      pins={name:item['descriptor'] for name,item in observation['tools'].items()})

def core_profile_binding(binding,ctx,value):
    """Carry already received observation/adoption identity; no new grant."""
    observation=value['observation'];adopted=value['adoption']
    profile=_profile_policy(binding).validate_g1_host_profile(observation['host_profile'])
    P.need(adopted['host_profile']==profile and observation['context']==ctx,'HOST_TOOL_ADOPTION_EXACT_JOIN')
    return dict(schema='dg16.g1-finite-host-profile-adoption-binding.v1',context=ctx,
        source_commit=binding['source_commit'],source_tree=binding['source_tree'],host_profile=profile,
        host_identity=observation['host_identity'],observation=value['ready']['observation'],adoption=value['ready']['adoption'])

class ResolvedTools:
    def __init__(self,binding,ctx,operation,token=None):
        P.need(operation in OPERATIONS,'HOST_TOOL_FIXED_OPERATION');self.binding=binding;self.ctx=ctx
        self.operation=operation;self.token=token;self.performed={};self.value=read_ready(binding,ctx)
        self.recheck('OPEN')
    @property
    def pins(self):return self.value['pins']
    @property
    def deadline(self):return self.value['ready']['command_deadline_monotonic']
    def recheck(self,phase):
        P.need(phase in PHASES,'HOST_TOOL_FIXED_CURRENTNESS_PHASE')
        now=read_ready(self.binding,self.ctx);P.need(now==self.value,'HOST_TOOL_READY_CHANGED')
        path=self.value['path'];member='CURRENT_'+self.operation.upper()+'_'+phase+'.json'
        if phase in self.performed:
            _,row=F.read_file(path/member,MAX_BODY,private=True)
            P.need(row==self.performed[phase],'HOST_TOOL_RETAINED_CURRENTNESS_CHANGED');return True
        reader=api(self.binding,self.token,self.deadline);d=declaration(self.binding)
        ref=reader.get('ref',d['control_branch'])
        P.need(ref.get('ref')=='refs/heads/'+d['control_branch'] and ref.get('object',{}).get('type')=='commit'
          and ref['object']['sha']==self.value['ready']['control_commit'],'HOST_TOOL_CONTROL_CURRENTNESS')
        P.need(read_ready(self.binding,self.ctx)==self.value,'HOST_TOOL_CURRENT_READBACK_CHANGED')
        record=dict(schema='dg16.actual-host-tool-currentness.v1',operation=self.operation,phase=phase,
          observation=self.value['ready']['observation'],adoption=self.value['ready']['adoption'],
          control_commit=self.value['ready']['control_commit'],provider_ref=ref,actual_reads=reader.audit,
          host_identity=host_identity(),tools=self.value['observation']['tools'],authority='NONE')
        self.performed[phase]=save(path,member,P.encode(record));return True

def check_observation_artifact(archive,snapshot,context,binding,expected_anchor,now_ms,*,workflow_representation=V.RAW_API_WORKFLOW):
    """Body-backed mechanical receiving; root's actual tool history is separate.

    The return value is deliberately incapable of becoming a command pin or
    root adoption. The root must consume authentic provider responses and
    issue the separate exact adoption itself after this closed join succeeds.
    """
    P.need(type(archive) is bytes and 0<len(archive)<=MAX_ARCHIVE,'HOST_TOOL_ARTIFACT_BOUND')
    try:
        with zipfile.ZipFile(io.BytesIO(archive)) as z:
            rows=z.infolist();P.need(len(rows)==1 and rows[0].filename=='HOST_TOOL_OBSERVATION.json'
              and not rows[0].is_dir() and not rows[0].flag_bits&1 and rows[0].compress_type in (0,8)
              and 0<rows[0].file_size<=MAX_BODY and (rows[0].external_attr>>16)&0o170000 in (0,0o100000),
              'HOST_TOOL_ARTIFACT_POPULATION')
            raw=z.read(rows[0]);P.need(len(raw)==rows[0].file_size,'HOST_TOOL_ARTIFACT_BODY')
    except (zipfile.BadZipFile,RuntimeError,OSError) as exc:raise ValueError('HOST_TOOL_ARTIFACT_CRC') from exc
    v=P.parse(raw,MAX_BODY);P.context(context);P.exact(snapshot,('run','attempt','jobs','artifact','artifacts','workflow'))
    P.need(len(P.encode(snapshot))<=P.MAX_METADATA,'HOST_TOOL_ROOT_METADATA_AGGREGATE')
    P.exact(v,('schema','authority','phase','context','source_commit','source_tree','carrier_binding_sha256',
      'input_index_sha256','public_manifest_sha256','bootstrap_admission_sha256','host_identity','directory_identity',
      'nonce','issued_unix_ms','tools','observation_elapsed_ns','command_executed','crypto_capability_claim','original_awards','host_profile'))
    P.need(v['schema']=='dg16.same-host-fixed-tool-observation.v2' and v['authority']=='NONE' and v['original_awards']==[],
      'HOST_TOOL_ROOT_OBSERVATION_SCHEMA')
    profile=_profile_policy(binding).validate_g1_host_profile(v['host_profile'])
    P.need(all(type(v['host_identity'][k]) is int and v['host_identity'][k]==profile['facts'][k] for k in ('uid','euid','gid','egid')),'HOST_TOOL_ROOT_HOST_IDENTITY')
    P.digest(v['nonce']);P.integer(v['issued_unix_ms'],0,now_ms)
    P.integer(v['observation_elapsed_ns'],0,declaration(binding)['observation_seconds']*10**9)
    P.exact(v['host_identity'],('uid','euid','gid','egid','boot_id'))
    P.need(v['host_identity']['uid']==v['host_identity']['euid']==0
      and type(v['host_identity']['boot_id']) is str and P.re.fullmatch('[0-9a-f-]{36}',v['host_identity']['boot_id']),
      'HOST_TOOL_ROOT_HOST_IDENTITY')
    P.exact(v['tools'],('env','openssl'))
    for tool,file in PATHS.items():
        item=v['tools'][tool];P.exact(item,('path','descriptor','physical'));P.exact(item['descriptor'],('bytes','sha256'))
        P.integer(item['descriptor']['bytes'],1,MAX_FILE);P.digest(item['descriptor']['sha256'])
        physical=item['physical'];P.exact(physical,('bytes','sha256','identity','ancestors'))
        P.need(item['path']==file and {k:physical[k] for k in ('bytes','sha256')}==item['descriptor']
          and type(physical['identity']) is list and len(physical['identity'])==9
          and all(type(n) is int and n>=0 for n in physical['identity'])
          and stat.S_ISREG(physical['identity'][2]) and physical['identity'][3]==1
          and physical['identity'][4]==item['descriptor']['bytes'] and physical['identity'][7]==0
          and physical['identity'][2]&0o022==0,'HOST_TOOL_ROOT_PHYSICAL_BODY')
        ancestors=physical['ancestors']
        P.need(type(ancestors) is list and len(ancestors)==3
          and all(type(r) is list and len(r)==6 and all(type(n) is int and n>=0 for n in r[1:]) for r in ancestors)
          and [r[0] for r in ancestors]==['/','/usr','/usr/bin']
          and all(stat.S_ISDIR(r[3]) and r[3]&0o022==0 and r[4]==0 for r in ancestors),
          'HOST_TOOL_ROOT_PHYSICAL_ANCESTRY')
    P.need(v.get('context')==context and v.get('source_commit')==binding['source_commit']
      and v.get('source_tree')==binding['source_tree'] and v.get('carrier_binding_sha256')==P.sha(binding['_binding_raw'])
      and v.get('input_index_sha256')==P.C.check_index(binding['_index'])
      and all(v.get(k)==expected_anchor[k] for k in ('public_manifest_sha256','bootstrap_admission_sha256'))
      and v.get('phase')=='READ_ONLY_FIXED_TOOL_BODIES' and v.get('command_executed') is False
      and v.get('crypto_capability_claim') is False,'HOST_TOOL_ROOT_ARTIFACT_BINDING')
    for name in ('run','attempt'):
        r=snapshot[name]
        P.need(r.get('id')==int(context['run_id']) and r.get('run_attempt')==1 and r.get('event')=='push'
          and r.get('status')=='in_progress' and r.get('head_branch')==context['branch']
          and r.get('head_sha')==context['workflow_commit'] and r.get('path')==context['workflow_path']
          and r.get('repository',{}).get('full_name')==P.REPOSITORY
          and r.get('head_repository',{}).get('full_name')==P.REPOSITORY
          and V.unix_ms(r.get('run_started_at'))<=v['issued_unix_ms'],'HOST_TOOL_ROOT_LIVE_RUN')
    repo=snapshot['run']['repository']['id'];P.integer(repo,1,10**20)
    P.need(all(snapshot[n][k].get('id')==repo for n in ('run','attempt') for k in ('repository','head_repository')),
      'HOST_TOOL_ROOT_REPOSITORY_ID')
    jobs=snapshot['jobs'];P.need(jobs.get('total_count')==1 and type(jobs.get('jobs')) is list and len(jobs['jobs'])==1,
      'HOST_TOOL_ROOT_SINGLE_JOB');job=jobs['jobs'][0]
    P.need(job.get('run_id')==int(context['run_id']) and job.get('run_attempt')==1 and job.get('head_sha')==context['workflow_commit']
      and job.get('name')==context['job_name'] and job.get('status')=='in_progress'
      and V.unix_ms(job.get('started_at'))<=v['issued_unix_ms'],'HOST_TOOL_ROOT_LIVE_JOB')
    a=snapshot['artifact'];r=a.get('workflow_run',{})
    P.need(a.get('name')=='dg16-core-host-tools-'+context['run_id']+'-a1' and a.get('expired') is False
      and a.get('size_in_bytes')==len(archive) and a.get('digest')=='sha256:'+P.sha(archive)
      and r.get('id')==int(context['run_id']) and r.get('head_sha')==context['workflow_commit']
      and r.get('head_branch')==context['branch'] and r.get('repository_id')==r.get('head_repository_id')==repo
      and v['issued_unix_ms']<=V.unix_ms(a.get('created_at'))<=now_ms,'HOST_TOOL_ROOT_ACTUAL_ARTIFACT')
    listing=snapshot['artifacts'];P.need(type(listing.get('artifacts')) is list and type(listing.get('total_count')) is int
      and listing['total_count']==len(listing['artifacts'])<=100
      and [r for r in listing['artifacts'] if r.get('name')==a['name']]==[a],'HOST_TOOL_ROOT_ARTIFACT_JOIN')
    V.workflow_body(snapshot['workflow'],context,binding['workflow_sha256'],representation=workflow_representation)
    return dict(schema='dg16.host-tool-mechanical-artifact-receiving.v1',authority='NONE',observation=P.descriptor(raw),
      artifact=P.descriptor(archive),artifact_id=a['id'],job_id=job['id'],context=context,
      authentic_root_tool_history_required=True,tool_adoption_issued=False,command_authority=False,original_awards=[])
