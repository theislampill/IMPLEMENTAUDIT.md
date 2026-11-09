"""Pure maintained-generator extension for a distinct hosted encrypt profile.

Inputs are immutable byte maps. This module opens no paths, runs no commands,
issues no authority and never binds or replaces the legacy private profile.
The full original final-input/runtime/review guards remain in the predecessor.
"""
import ast
import hashlib
import json
import re
import types
from pathlib import Path

SOURCE='7e2b00b3a2a16fc6033a5eabe4fc795f6249366f'
TREE='6d3f972a424583f9d3d56d8bfd9ae11cf36ecf6e'
HOST_SEAL='9401f5b38a105b459301105b1f9dccb4badb908f5f92c30a35f7a551a5ef0786'
HOST_INDEX='b4b27db6dfce501d68d77f3fce7765c7212a0677de77f93daafc696c101871be'
ROOT_RECEIPT='8dd6be2cef66d4632b2f58f8bc406d93504e1f155b839e5ca559f34d3ff57a99'
ISSUER='01a1953f-a15b-7811-aa72-3538ebb03562'
RECIPIENT=dict(bytes=1464,sha256='5adbbeaf63e38116dcba9eb58af76b0fa056808649f9aa144e3f14dee838f4b8')
PREFIX='qualification/dg16-r5-full-g2/'
WORKFLOW='.github/workflows/dg16-r5-full-g2.yml'
UNBOUND_BRANCH='pro/dg16-r5-full-g2-direct-host-source-unbound'
UNBOUND_CONTROL='pro/dg16-r5-full-g2-direct-host-control-unbound'
sha=lambda b:hashlib.sha256(b).hexdigest()
desc=lambda b:dict(bytes=len(b),sha256=sha(b))
encode=lambda v:(json.dumps(v,sort_keys=True,indent=2,ensure_ascii=True,allow_nan=False)+'\n').encode('ascii')

def need(ok,code):
    if not ok:raise ValueError(code)

def parse(raw):
    def pairs(rows):
        out={}
        for k,v in rows:
            need(k not in out,'DUPLICATE_JSON_KEY');out[k]=v
        return out
    return json.loads(raw,object_pairs_hook=pairs,parse_constant=lambda _:need(False,'NONFINITE'))

def assign(raw,values):
    lines=raw.decode().splitlines(keepends=True);tree=ast.parse(raw);edits=[]
    for name,value in values.items():
        hits=[n for n in tree.body if isinstance(n,ast.Assign) and len(n.targets)==1
              and isinstance(n.targets[0],ast.Name) and n.targets[0].id==name]
        need(len(hits)==1,'EXACT_ASSIGNMENT_'+name);n=hits[0]
        edits.append((n.lineno-1,n.end_lineno,name+' = '+repr(value)+'\n'))
    for a,b,text in sorted(edits,reverse=True):lines[a:b]=[text]
    result=''.join(lines).encode();ast.parse(result);return result

def replace_once(raw,before,after):
    need(raw.count(before)==1,'EXACT_HOST_SOURCE_ANCHOR');return raw.replace(before,after)

def validate_witness(records):
    """Receive exact already accepted source/data identities, not a new award.

    Root receipt provenance was separately received over the native channel.
    Matching JSON labels are not authentication of a root or human actor.
    """
    pins={
      'root':'8dd6be2cef66d4632b2f58f8bc406d93504e1f155b839e5ca559f34d3ff57a99',
      'public':'d873155e9442619e21af069d480d7eeaf81919417cc4a7fd320b1928eca96b6a',
      'provider':'4661713440ee13c2e71ed8dbc57548000e98972d1771985a9c22c8a8af04efc8',
      'independent':'ca7cb3a1c5e2f3b56102379034897a9e0cbf9910dfc723f053066ce1ee801ed3',
      'source_root':'a47fcec73cc94fbc00c76407acffae1145b2b86d238eb0fc15d2db771dacd227'}
    need(set(records)==set(pins),'HOST_WITNESS_RECORD_POPULATION')
    for n,digest in pins.items():need(type(records[n]) is bytes and sha(records[n])==digest,'HOST_WITNESS_PIN_'+n)
    root,public,independent,source=(parse(records[n]) for n in ('root','public','independent','source_root'))
    need(root['decision']=='ACCEPT_ACTUAL_DIRECT_OPENSSL_MAXIMUM_ENCRYPT_CAPTURE_ON_THIS_STANDALONE_HOST'
      and root['actor']==ISSUER and root['independent_final']['sha256']==sha(records['independent'])
      and root['provider']['sha256']==sha(records['provider']),'ACTUAL_HOST_ROOT_JOIN')
    target=root['target'];delivery=public['delivery'];q=public['qualification'];facts=q['facts']
    need(target==independent['provider_identity'] and target['run_id']==42562408045
      and target['job_id']==128981492233 and type(target['attempt']) is int and target['attempt']==1
      and target['head']==delivery['head']==delivery['payload_commit']=='c2c4e92d00822647f8a4c345f09c4d0f636b8334'
      and target['ref']==delivery['ref'] and target['actor']==delivery['actor']=='theislampill'
      and delivery['human_approval_sha256']==independent['external_expected_tuple']['human_approval_sha256'],
      'ACTUAL_HOST_DELIVERY_IDENTITY')
    need(q['stage']=='COMPLETE' and facts['component_seal']==HOST_SEAL
      and facts['recipient']==RECIPIENT and facts['plain_before']==facts['plain_after']==root['plaintext']
      and root['plaintext']['bytes']==268501016 and facts['cipher']==root['ciphertext']
      and 0<root['ciphertext']['bytes']<=268517400 and facts['currentness_bookends'] is True
      and set(facts['files_removed'])=={'FAILED_STREAMS.cms','FRAME.bin','recipient.pem'}
      and all(v is True for v in facts['files_removed'].values()),'ACTUAL_HOST_MAXIMUM_SCOPE')
    need(q['production_gate_received'] is False and q['authenticated_private_receiving'] is False
      and facts['authenticated_private_receiving'] is False
      and q['last_capture']['cleanup']==dict(echild=True,restoration_complete=True)
      and independent['decision']=='PASS_BOUNDED_ACTUAL_COMPACT_DATA_RECEIVING'
      and independent['scope_flags']['private_authenticated_interoperability'] is False
      and independent['scope_flags']['production_same_host_gate_received'] is False
      and source['source_seal_sha256']==HOST_SEAL and source['native_effect_granted'] is False,
      'ISOLATED_WITNESS_NOT_PRODUCTION_OR_PRIVATE')
    return {n:desc(raw) for n,raw in records.items()}

def selection_expected(branch,control,witness):
    for value in (branch,control):
        need(type(value) is str and re.fullmatch(r'pro/[A-Za-z0-9][A-Za-z0-9/_-]{0,180}',value)
          and '..' not in value and '//' not in value,'HOST_BRANCH')
    need(branch!=control,'DISTINCT_HOST_BRANCHES')
    return dict(schema='dg16.protected-full-g2-direct-host-recipient-adoption.v2',actor='/root',
      issuer_thread=ISSUER,status='ACTUAL_RECIPIENT_AND_QUALIFIED_HOST_PROFILE_SELECTED',
      source_commit=SOURCE,source_tree=TREE,branch=branch,control_branch=control,
      component_seal_sha256=HOST_SEAL,component_code_manifest_sha256=HOST_INDEX,
      recipient=RECIPIENT,host_qualification=witness,root_receiving=witness['root'],
      isolated_maximum_encrypt_capture_received=True,
      private_authenticated_interoperability='NOT_ESTABLISHED_BY_THIS_ADOPTION',
      host_gate='MAXIMUM_OPAQUE_PLAINTEXT_ENCRYPTION_BEFORE_EITHER_MAINTAINED_LEG',
      private_key_on_host=False,effect_grant=False,automatic_retry=False,original_awards=[])

def bridge_source(raw,expected,selection_raw=None):
    """Repair host adoption only; retain all remaining nearest-owner code."""
    tree=ast.parse(raw);function=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='selection')
    lines=raw.decode().splitlines(keepends=True)
    replacement='''def selection(u):
    # Exact Root source adoption is separate from private-role authentication.
    # Byte equality supplies no provenance; Root receives issuer history later.
    need(BOUND is True and type(SELECTION_SHA) is str,'PROTECTED_FINAL_BINDING_REQUIRED')
    raw=u.checked_file(Path(__file__).with_name('PROTECTED_RECIPIENT.json'),16384)
    need(desc(raw)['sha256']==SELECTION_SHA,'PROTECTED_ROOT_SELECTION_CHANGED')
    value=u.parse_json(raw)
    need(type(value) is dict and set(value)==set(HOST_SELECTION_EXPECTED)
      and all(type(value[k]) is type(v) and value[k]==v for k,v in HOST_SELECTION_EXPECTED.items()),
      'PROTECTED_ACTUAL_HOST_ONLY_SELECTION_SCOPE')
    cert=u.checked_file(Path(__file__).with_name('PROTECTED_RECIPIENT.pem'),8192)
    need(desc(cert)==value['recipient'],'PROTECTED_PUBLIC_RECIPIENT_CHANGED')
    return value,raw,cert
'''
    lines[function.lineno-1:function.end_lineno]=[replacement]
    raw=''.join(lines).encode()
    raw=assign(raw,dict(BOUND=selection_raw is not None,
      SELECTION_SHA=sha(selection_raw) if selection_raw is not None else None,
      BRANCH=expected['branch'],CONTROL_BRANCH=expected['control_branch']))
    raw=raw.replace(b"LOAD_ORDER=",('HOST_SELECTION_EXPECTED = '+repr(expected)+'\nLOAD_ORDER=').encode(),1)
    ast.parse(raw);return raw

def compose(packet,host,records,selection_raw=None):
    """Run the maintained source algorithms and overlay the distinct host role.

    Output is a structural or actual-host-adoption-bound source candidate. Actual final receiver decisions,
    private custody, native admission and original awards remain absent.
    """
    witness=validate_witness(records)
    need(sha(packet['candidate/generator.py'])=='09b1398acda4bb670177ab6a15c22f6ac04c21e3c5b6670de96e3b25af6c218b','MAINTAINED_GENERATOR_PIN')
    need(sha(host['HOST_COMPONENT_SEAL.json'])==HOST_SEAL and sha(host['CODE_MANIFEST.json'])==HOST_INDEX,'HOST_COMPONENT_INPUT_PINS')
    pins=parse(host['CODE_MANIFEST.json'])['members']
    need(pins==parse(host['HOST_COMPONENT_SEAL.json'])['members'],'HOST_COMPONENT_INDEX_JOIN')
    for name,pin in pins.items():need(desc(host[name])==pin,'HOST_COMPONENT_MEMBER_'+name)
    expected=selection_expected(UNBOUND_BRANCH,UNBOUND_CONTROL,witness)
    if selection_raw is not None:
        selected=parse(selection_raw);expected=selection_expected(selected.get('branch'),selected.get('control_branch'),witness)
        need(selected==expected and selection_raw==encode(expected),'ACTUAL_HOST_SELECTION_REQUIRED')
        need(selected['branch']!=UNBOUND_BRANCH and selected['control_branch']!=UNBOUND_CONTROL,'UNBOUND_REF_NOT_ACTUAL_SELECTION')

    # A byte-only archive view qualifies source algorithms, not POSIX custody.
    class ArchivePath(type(Path())):
        def __str__(self):return super().__str__().replace('\\','/')
        def key(self):return self.relative_to('/g2_source_packet').as_posix()
        def is_file(self):return self.key() in packet
        def read_bytes(self):return packet[self.key()]
        def rglob(self,pattern):
            need(pattern=='*','ARCHIVE_PATTERN');prefix=self.key().rstrip('/')+'/'
            return iter(ArchivePath('/g2_source_packet')/n for n in sorted(packet) if n.startswith(prefix))
    G=types.ModuleType('maintained_g2_source_generator');G.__file__='/g2_source_packet/candidate/generator.py'
    exec(compile(packet['candidate/generator.py'],G.__file__,'exec'),G.__dict__)
    G.Path=ArchivePath;G.ROOT=ArchivePath('/g2_source_packet');G.INPUT=G.ROOT/'inputs'
    def read(path,maximum=1024**2):
        raw=packet[ArchivePath(path).key()];need(len(raw)<=maximum,'ARCHIVE_READ_BOUND');return raw
    G.read=read;G.BRANCH=expected['branch'];G.CONTROL=expected['control_branch']
    public=G.prepared_public(None);legacy_receiver=G.prepared_receiver(None)
    baseline_public=dict(public);receiver=dict(legacy_receiver)
    for name in pins:public[PREFIX+name]=host[name]
    public[PREFIX+'protected_preflight.py']=host['protected_preflight.py']
    bridge=bridge_source(host['protected_bridge.py'],expected,selection_raw)
    public[PREFIX+'protected_bridge.py']=bridge
    if selection_raw is not None:
        public[PREFIX+'PROTECTED_RECIPIENT.json']=selection_raw
        public[PREFIX+'PROTECTED_RECIPIENT.pem']=packet['prepared/candidate/public/'+PREFIX+'PROTECTED_RECIPIENT.pem']
        need(desc(public[PREFIX+'PROTECTED_RECIPIENT.pem'])==RECIPIENT,'ACTUAL_PUBLIC_CERTIFICATE')
    old_run=public[PREFIX+'run.py']
    public[PREFIX+'run.py']=assign(old_run,dict(PROTECTED_BRIDGE_SHA=sha(bridge),FINAL_COMPOSITION_READY=selection_raw is not None))
    # Nineteen maintained launch checks and one supplementary emit check.
    need(public[WORKFLOW].count(sha(old_run).encode())==20,'TWENTY_EXACT_WORKFLOW_RUN_PINS')
    public[WORKFLOW]=public[WORKFLOW].replace(sha(old_run).encode(),sha(public[PREFIX+'run.py']).encode())
    binding=parse(receiver['BINDING_TEMPLATE.json'])
    for name in tuple(binding['modules']):binding['modules'][name]=desc(public[PREFIX+name])
    if selection_raw is not None:
        for name in ('PROTECTED_RECIPIENT.json','PROTECTED_RECIPIENT.pem'):
            binding['modules'][name]=desc(public[PREFIX+name])
    receiver['BINDING_TEMPLATE.json']=G.encode(binding)
    root_binding=parse(receiver['ROOT_BINDING_TEMPLATE.json'])
    root_binding['workflow_sha256']=sha(public[WORKFLOW])
    receiver['ROOT_BINDING_TEMPLATE.json']=G.encode(root_binding)
    # Legacy private modules/helpers remain byte-identical; only public binding
    # module descriptors and the Root template's workflow descriptor may differ.
    for name,raw in legacy_receiver.items():
        if name not in ('BINDING_TEMPLATE.json','ROOT_BINDING_TEMPLATE.json'):
            need(receiver[name]==raw,'LEGACY_PRIVATE_SOURCE_CHANGED')
    need(root_binding['component_seal_sha256']==G.COMPONENT_SEAL
      and root_binding['component_index_sha256']==G.COMPONENT_INDEX
      and root_binding['actual_maximum_qualification_received'] is False
      and root_binding['actual_component_review_received'] is False
      and root_binding['session'] is None and root_binding['successor_runtime_binding'] is None,
      'PRIVATE_ROLE_STAYS_UNBOUND')
    # Verify the actual original injection survived the host-only extension.
    run=public[PREFIX+'run.py'].decode()
    need(run.count('        protected_preflight(state,source,output,u,tools,manifest)\n        require_native_for_pair(state,output,u)')==1,
      'PRODUCTION_SAME_HOST_GATE_MUST_PRECEDE_PAIR')
    need(('FINAL_COMPOSITION_READY = '+str(selection_raw is not None)) in run,'SOURCE_COMPOSITION_READINESS_MATCHES_ACTUAL_HOST_INPUT')
    manifest=parse(public[PREFIX+'SOURCE_MANIFEST.json'])
    need(manifest['commit']==SOURCE and manifest['tree']==TREE and manifest['file_count']==1759
      and manifest['total_bytes']==166407881,'MAINTAINED_SOURCE_CHANGED')
    request=dict(schema='dg16.direct-host-source-binding-requirements.v1',authority='NONE',actual_admission=False,
      host_selection_expected=expected,selection_status='ACTUAL_ROOT_BODY_STILL_REQUIRED' if selection_raw is None else 'SOURCE_ADOPTION_BODY_ONLY',
      host_component=HOST_SEAL,legacy_private_component=G.COMPONENT_SEAL,
      public_runtime='FRESH_ACTUAL_PUBLIC_PATHS_AND_ROOT_RECEIVING_REQUIRED; NO_HISTORICAL_SESSION_TRANSPLANT',
      final_binding='FRESH_CANDIDATE_COMPOSITION_TREE_NATIVE_POLICY_REVIEW_DECISIONS_AND_DISTINCT_REVIEW_SELECTION_REQUIRED',
      private_role='UNCHANGED_LEGACY_SOURCE_UNBOUND; ACTUAL_CUSTODY_AND_ORIGINAL_PRIVATE_INTEROPERABILITY_REQUIRED_IF_CLAIMED',
      production_gate='ACTUAL_SAME_HOST_MAXIMUM_BEFORE_EITHER_MAINTAINED_LEG',
      hosted_effect='SEPARATE_EXACT_ADMISSION_REQUIRED',original_awards=[])
    return public,receiver,request,dict(maintained_generator=desc(packet['candidate/generator.py']),
      public_changed={n:dict(before=desc(baseline_public[n]),after=desc(raw))
        for n,raw in public.items() if n in baseline_public and raw!=baseline_public[n]},
      legacy_private_members_retained=len(legacy_receiver)-2,host_witness=witness,
      host_source_bound=selection_raw is not None,final_public_receiver_bound=False,posix_reader_equivalence=False,source_members_changed=0)
