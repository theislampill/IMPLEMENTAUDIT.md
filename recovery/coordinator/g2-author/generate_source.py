"""Bounded local source generation/controls; no hosted/native/private operation."""
import argparse
import ast
import copy
import hashlib
import io
import json
import os
from pathlib import Path
import re
import stat
import sys
import types
import zipfile
from datetime import datetime,timezone

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'generated-source-01'
BASE=ROOT.parent
REPO=BASE.parent.parent
H=lambda b:hashlib.sha256(b).hexdigest()
D=lambda b:dict(bytes=len(b),sha256=H(b))
MARK=lambda s:(s.st_dev,s.st_ino,s.st_mode,s.st_size,s.st_mtime_ns,s.st_ctime_ns,s.st_nlink)

def read_owned(p,maximum=16*1024**2):
    s=p.lstat();assert stat.S_ISREG(s.st_mode) and not p.is_symlink() and s.st_size<=maximum
    raw=p.read_bytes();assert MARK(p.lstat())==MARK(s) and len(raw)==s.st_size;return raw

archive=Path('C:/Users/theis/Downloads/G2_CURRENT03_SOURCE_CANDIDATE_20261107.zip')
archive_raw=read_owned(archive)
assert D(archive_raw)==dict(bytes=2537258,sha256='2d494416aed0a77d60c28ea47dc9e1cc9411fed9271b4d844aae17c453be4fc0')
with zipfile.ZipFile(io.BytesIO(archive_raw)) as z:
    assert len(z.namelist())==len(set(z.namelist()))==255
    seal=json.loads(z.read('packet/SEAL.json'));packet={}
    assert len(seal['members'])==219
    for row in seal['members']:
        n=row['path'];assert not n.startswith('/') and '..' not in Path(n).parts and '\\' not in n
        info=z.getinfo('packet/'+n);assert not info.is_dir() and info.file_size==row['bytes'] and info.file_size<=4*1024**2
        raw=z.read(info);assert D(raw)=={k:row[k] for k in ('bytes','sha256')};packet[n]=raw
    assert len(packet)==219 and sum(map(len,packet.values()))==9200297
host_root=REPO/'plans/astra-successor-reconciliation-20261108/g2-direct-openssl/source'
host_names=('CAPTURE_DIAGNOSTIC_CATALOG.json','CODE_MANIFEST.json','HOST_COMPONENT_SEAL.json','bound_child.py',
 'capture_evidence.py','fs_carrier.py','fs_command.py','fs_io.py','fs_protocol.py','fs_runner.py','fs_transport.py',
 'full_g2_hooks.py','protected_bridge.py','protected_preflight.py')
host={n:read_owned(host_root/n) for n in host_names}
assert H(host['protected_preflight.py'])=='ae2b291462fc543b5ed0f25401ab50d6792c51c820ff1f40961fbf28a4e595d7'
assert H(host['protected_bridge.py'])=='1f3c8ee0e567ce16edb257019f0a717290706fa557c3752dd25d77b5249f59d0'
witness_root=REPO/'plans/astra-successor-reconciliation-20261108/direct-encrypt-qualification-01'
locations=dict(root=witness_root/'ASTRA_MAXIMUM_ROOT_RECEIVING.json',public=witness_root/'ACTUAL_PUBLIC_DELIVERY.json',
 provider=witness_root/'PROVIDER_RECEIVING.json',
 independent=BASE/'g1-current03-recovered/g2-public-receiving/FINAL.json',
 source_root=host_root.parent/'ASTRA_SOURCE_RECEIVING.json')
records={n:read_owned(p) for n,p in locations.items()}
extension=read_owned(ROOT/'source/direct_host_profile.py')
assert not OUT.exists()
events={}

def inside(path):
    try:return Path(os.path.abspath(path)).is_relative_to(OUT)
    except (TypeError,ValueError):return False

def fence(event,args):
    if event.startswith(('subprocess.','socket.','ctypes.')) or event in (
      'os.system','os.exec','os.posix_spawn','os.fork','os.kill','os.killpg','os.spawn','os.startfile','os.putenv','os.unsetenv'):
        raise PermissionError('SOURCE_ONLY_EFFECT_REFUSED')
    if event=='open' and not inside(args[0]):raise PermissionError('NON_OWNED_OPEN_REFUSED')
    if event in ('os.mkdir','os.chmod','os.remove','os.rmdir','os.rename','os.link','os.symlink'):
        if event in ('os.rename','os.link','os.symlink') or not inside(args[0]):raise PermissionError('NON_OWNED_MUTATION_REFUSED')
    events[event]=events.get(event,0)+1

sys.addaudithook(fence)
M=types.ModuleType('direct_host_profile');M.__file__=str(ROOT/'source/direct_host_profile.py')
exec(compile(extension,M.__file__,'exec'),M.__dict__)
public,receiver,request,proof=M.compose(packet,host,records)
controls=[]

def expect_refusal(label,call,exception=ValueError):
    try:call()
    except exception as exc:controls.append(dict(case=label,result='PASS',refusal=str(exc)))
    else:raise AssertionError(label)

expect_refusal('outside_open',lambda:open(ROOT/'not-created','wb'),PermissionError)
expect_refusal('process_event',lambda:sys.audit('subprocess.Popen','/not-executed',[],None,None),PermissionError)
expect_refusal('socket_event',lambda:sys.audit('socket.__new__',None,2,1,0),PermissionError)
changed=dict(records);changed['root']=changed['root']+b' '
expect_refusal('changed_actual_root_witness',lambda:M.validate_witness(changed))
need=M.need
bridge=types.ModuleType('inert_bridge_selection_control');bridge.__file__='/source-only-fixture/protected_bridge.py'
exec(compile(public[M.PREFIX+'protected_bridge.py'],bridge.__file__,'exec'),bridge.__dict__)
actual_expected=request['host_selection_expected'];cert=packet['prepared/candidate/public/'+M.PREFIX+'PROTECTED_RECIPIENT.pem']
assert D(cert)==M.RECIPIENT

class Utility:
    body=M.encode(actual_expected)
    certificate=cert
    def checked_file(self,path,maximum):
        raw=self.body if Path(path).name=='PROTECTED_RECIPIENT.json' else self.certificate
        assert len(raw)<=maximum;return raw
    parse_json=staticmethod(M.parse)

utility=Utility()
expect_refusal('actual_generated_source_stays_unbound',lambda:bridge.selection(utility))
# Fixture-only binding for pure selection unit controls. No selected body is
# written into candidate/public or represented as an actual Root issuance.
bridge.BOUND=True;bridge.SELECTION_SHA=H(utility.body)
assert bridge.selection(utility)[0]==actual_expected
controls.append(dict(case='host_only_selection_fixture',result='PASS',actual_adoption=False))
for label,key,value in (
 ('legacy_authenticated_flag_rejected','small_authenticated_qualified',True),
 ('legacy_schema_rejected','schema','dg16.protected-full-g2-public-recipient-adoption.v1'),
 ('private_claim_rejected','private_authenticated_interoperability','QUALIFIED'),
 ('missing_isolated_witness_rejected','isolated_maximum_encrypt_capture_received',False),
 ('wrong_host_component','component_seal_sha256','e99a60d5790355ae39c0e4bbc4567add87e702775ade8f5655e2f3ef56bd9602'),
 ('unexpected_branch','branch','pro/foreign'),
 ('effect_grant_rejected','effect_grant',True),
 ('retry_rejected','automatic_retry',True),
 ('bool_source_attempt_scope','original_awards',[True])):
    fixture=copy.deepcopy(actual_expected);fixture[key]=value;utility.body=M.encode(fixture)
    bridge.SELECTION_SHA=H(utility.body)
    expect_refusal(label,lambda:bridge.selection(utility))
utility.body=M.encode(actual_expected);bridge.SELECTION_SHA=H(utility.body);utility.certificate=cert+b' '
expect_refusal('wrong_certificate',lambda:bridge.selection(utility))
utility.certificate=cert;bridge.SELECTION_SHA='0'*64
expect_refusal('wrong_actual_body_hash',lambda:bridge.selection(utility))

# Native functions are compiled but never entered. Only public validators and
# budget arithmetic run; the captured standalone result is not a live gate.
pre=types.ModuleType('inert_preflight_public_control');pre.__file__='/source-only-fixture/protected_preflight.py'
exec(compile(host['protected_preflight.py'],pre.__file__,'exec'),pre.__dict__)
P=types.ModuleType('inert_protocol_public_control')
exec(compile(host['fs_protocol.py'],'<inert-protocol>','exec'),P.__dict__)
assert pre.deadline_stop(0,8400,30)==90
assert pre.deadline_stop(0,8400,410)==420
controls.append(dict(case='unchanged_60s_gate_and_7980s_pair_reserve',result='PASS'))
expect_refusal('no_pair_reserve',lambda:pre.deadline_stop(0,8400,420))
isolated=M.parse(records['public'])['qualification']['facts']
context=dict(repository='theislampill/IMPLEMENTAUDIT.md',branch=M.UNBOUND_BRANCH,run_id='1',run_attempt=1,
 workflow_commit='1'*40,source_commit=M.SOURCE,source_tree=M.TREE,
 workflow_path=M.WORKFLOW,job_name='full-registry-raw-pair')
expect_refusal('isolated_witness_is_not_production_gate',lambda:pre.validate_public(isolated,context,P,started=True))

source_raw=public[M.PREFIX+'run.py'];tree=ast.parse(source_raw)
literal=lambda name:ast.literal_eval(next(n.value for n in tree.body if isinstance(n,ast.Assign)
 and any(isinstance(x,ast.Name) and x.id==name for x in n.targets)))
assert literal('PROTECTED_BRIDGE_SHA')==H(public[M.PREFIX+'protected_bridge.py'])
assert public[M.WORKFLOW].count(H(source_raw).encode())==20
assert all(receiver['component/'+name]==packet['inputs/capacity_r1/'+name]
 for name in json.loads(packet['inputs/capacity_r1/CODE_MANIFEST.json'])['members'])
controls.append(dict(case='actual_public_pins_and_unchanged_private_components',result='PASS'))
# Recompose all source bytes independently of output and ensure deterministic
# byte maps. This is source generation, not a repeated native campaign.
second=M.compose(packet,host,records)
assert second==(public,receiver,request,proof)
controls.append(dict(case='deterministic_maintained_source_composition',result='PASS'))
assert len(controls)==22,len(controls)

OUT.mkdir()
files={**{'candidate/public/'+n:raw for n,raw in public.items()},
       **{'receiver/'+n:raw for n,raw in receiver.items()},
       'HOST_PROFILE_BINDING_REQUIREMENTS.json':M.encode(request)}
for name,raw in files.items():
    assert not name.startswith('/') and '..' not in Path(name).parts and not name.endswith(('.key','.p12','.pfx'))
    if name.endswith('.py'):ast.parse(raw)
    path=OUT/name;path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('xb') as stream:stream.write(raw)
    assert path.read_bytes()==raw
manifest={n:D(raw) for n,raw in files.items()}
report=dict(schema='dg16.direct-host-production-source-generation.v1',utc=datetime.now(timezone.utc).isoformat(),
 authority='NONE',state='SOURCE_COMPOSED_REQUIRES_DISTINCT_REVIEW_AND_FRESH_ROOT_BINDINGS',
 generator_extension=D(extension),input_archive=D(archive_raw),host_inputs={n:D(raw) for n,raw in host.items()},
 source_proof=proof,public_files=len(public),receiver_files=len(receiver),
 controls=controls,actual_native_crypto_hosted_or_key_effects=0,original_awards=[],
 complete_final_receiver=False,private_current_custody='UNKNOWN',
 original_private_interoperability='NOT_ESTABLISHED_BY_HOST_ENCRYPT_WITNESS',
 production_same_host_gate='REQUIRED_ON_ACTUAL_JOB',audit_events=events)
for name,value in (('GENERATION_RECEIPT.json',report),('MANIFEST.json',manifest)):
    raw=(json.dumps(value,indent=2)+'\n').encode()
    with (OUT/name).open('xb') as stream:stream.write(raw)
    assert (OUT/name).read_bytes()==raw
print(json.dumps(dict(state=report['state'],public_files=len(public),receiver_files=len(receiver),
 controls=len(controls),receipt=D((OUT/'GENERATION_RECEIPT.json').read_bytes()),
 manifest=D((OUT/'MANIFEST.json').read_bytes()),changed=list(proof['public_changed']))))
