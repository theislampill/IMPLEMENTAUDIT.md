"""G221 public semantic composition, newly implemented after source loss.

Authentic host admission, source selection and distinct-agent provenance belong
to the controlling capability in the pinned V8 drivers. JSON checks below do
not authenticate a caller. Original public validators remain unchanged. This
module does not issue review, Root consumption, adoption, acceptance or effects.
"""
import ast
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import sys
import time
import types

ROOT = Path(__file__).resolve().parents[3]
CUSTODY = ROOT / 'handoff/dg16-g221-root-execution-inputs/g220-custody'
ORIGINAL_RECEIVER = CUSTODY / 'candidate-e76-source-01/receiver/public_receiver.py'
ORIGINAL_RECEIVER_SHA256 = '5bb8d71aa40e2a4d842ddd178b31257eef496ca3c0073461e8328d2e64560f5e'
ORIGINAL_BINDER = CUSTODY / 'author/bind_public_successor.py'
ORIGINAL_BINDER_SHA256 = 'a6545228f277408d361996b9c7a5d4aecde0e25ea5efe7443f482d535da2e5c3'
CONTROL_OWNER = CUSTODY / 'operator-static-source/core/prepare_live_control.py'
CONTROL_OWNER_SHA256 = '93ae48d79b76c6775179a500107c90d24173a2fbc189182c6543a07e87a31b4f'
PUBLIC_OPERATOR = CUSTODY / 'operator-static-source/public_operator_v2.py'
PUBLIC_OPERATOR_SHA256 = 'bcae77f8cc0b82668b966396d39ac9d36ca0f110c2413e3eeeb84506cd2283fb'
PLATFORM_OWNER = ROOT / 'handoff/dg16-pro-executor-20261115/platform_artifact.py'
PLATFORM_OWNER_SHA256 = '35ea21a75c8f7da3614454a384ebf53d30c132ac597cbdd86d39017161393389'
BINDING_ADAPTER_SHA256 = '9e2988fa416aaa828c6ef4b77f7da4ab8a62eb1cb9d64e9b791949a794dcaeed'
CHANNEL_SHA256 = 'b7c087ce21761b01fa8b5d2e0fd8409f73a402469371511a4df4e92215018e7c'
CHANNEL_JOURNAL_SHA256 = '9cbac140ff23f1df36867a0eca5fe65c94fd3cea27f52292e094f59d9a4e36db'
CURRENT_SOURCE_AUTHORS = ('/root', '/root/dg16_contract_check')
RECEIVER_NAMES = {'public_receiver.py','admission_gate.py','native_public.py','BINDING.json',
    'SUCCESSOR_RUNTIME_BINDING.json','FINAL_REVIEW_SELECTION.json','PUBLIC_BINDING_REQUIREMENTS.json'}
TOOL_MAX = 4 * 1024 ** 2
TERMINAL_LOG_MAX = 16 * 1024 ** 2


def need(value, code):
    if not value:
        raise ValueError(code)


def desc(raw):
    return {'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}


def encode(value):
    return (json.dumps(value,sort_keys=True,indent=2,ensure_ascii=True,allow_nan=False)+'\n').encode('ascii')


def canonical(value):
    return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode('utf8')


def digest(value, length=64):
    return type(value) is str and re.fullmatch('[0-9a-f]{'+str(length)+'}',value) is not None and value!='0'*length


def strict(raw, maximum=TOOL_MAX):
    need(type(raw) is bytes and 0<len(raw)<=maximum,'JSON_BYTES_BOUND')
    def pairs(rows):
        out={}
        for key,value in rows:
            need(key not in out,'DUPLICATE_JSON_KEY')
            out[key]=value
        return out
    return json.loads(raw,object_pairs_hook=pairs,
        parse_constant=lambda _:need(False,'NONFINITE_JSON'))


def checked_path(value):
    need(type(value) in (str,Path) or isinstance(value,Path),'ABSOLUTE_PHYSICAL_PATH')
    path=Path(value)
    need(path.is_absolute() and str(path)==str(value) and len(str(path))<=4096 and
         not any(ord(c)<32 or ord(c)==127 for c in str(path)) and
         path.resolve(strict=True)==path,'ABSOLUTE_PHYSICAL_PATH')
    return path


def checked_file(value, maximum):
    path=checked_path(value)
    before=path.lstat()
    need(stat.S_ISREG(before.st_mode) and before.st_nlink==1 and 0<=before.st_size<=maximum,'INPUT_FILE_SHAPE')
    mark=lambda s:(s.st_dev,s.st_ino,s.st_mode,s.st_uid,s.st_gid,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
    fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC|os.O_NONBLOCK)
    try:
        need(mark(before)==mark(os.fstat(fd)),'INPUT_CHANGED')
        with os.fdopen(fd,'rb',closefd=False) as stream:
            raw=stream.read(maximum+1)
        need(mark(before)==mark(os.fstat(fd))==mark(path.lstat()) and len(raw)==before.st_size,'INPUT_CHANGED')
        return raw
    finally:
        os.close(fd)


def pinned(path, wanted, code):
    raw=checked_file(path,262144)
    need(desc(raw)['sha256']==wanted,code)
    return raw


def module(raw, path, name):
    result=types.ModuleType(name)
    result.__file__=str(path)
    exec(compile(raw,str(path),'exec',dont_inherit=True,optimize=0),result.__dict__)
    return result


def source_owners():
    owner=module(pinned(PLATFORM_OWNER,PLATFORM_OWNER_SHA256,'PLATFORM_SOURCE_PIN'),
        PLATFORM_OWNER,'exact_public_platform_owners')
    _,resolver,_,_,writer=owner.owners()
    return resolver,writer


def decode_log_wrapper(raw):
    value=strict(raw,TOOL_MAX)
    need(type(value) is dict and set(value)<={'content','structuredContent','isError','_meta'}
         and value.get('isError') is False and type(value.get('content')) is list,'COMPLETE_LOG_TOOL_RESULT')
    meta=value.get('_meta',{})
    need(type(meta) is dict and all(k in ('truncated','isTruncated','partial','hasMore') and v is False
         for k,v in meta.items()),'NO_PARTIAL_LOG_RESULT')
    body=value.get('structuredContent')
    need(type(body) is dict and set(body)=={'content'} and type(body['content']) is str,'EXACT_LOG_CONTENT')
    result=body['content'].encode('utf8')
    need(0<len(result)<=TERMINAL_LOG_MAX,'TERMINAL_LOG_BOUND')
    return result


def inspect_public(receiver, archive, kind, context, metadata, *, terminal_log=None):
    need(kind in ('live','terminal'),'PUBLIC_KIND')
    need(type(terminal_log) is bytes if kind=='terminal' else terminal_log is None,'EXACT_ROLE_LOG_REQUIREMENT')
    files=receiver.decode_zip(archive,kind)
    result=receiver.inspect(files,kind,run_id=context['run_id'],workflow_commit=context['workflow_commit'],
        metadata=metadata,archive=desc(archive))
    need(type(result) is dict and result.get('authority')=='NONE' and
         all(result.get(k) is False for k in ('original_acceptance','review_issued','root_consumption_issued')),
         'ORIGINAL_DATA_ONLY_OBSERVATION')
    if kind=='terminal':
        result['terminal_log_join']=receiver.match_terminal_log(files,terminal_log)
        need(result['terminal_log_join'].get('all_seven_exact') is True,'ORIGINAL_COMPLETE_TERMINAL_JOIN')
    return result


def bound_receiver_source(runtime_raw, binding_raw):
    binder=module(pinned(ORIGINAL_BINDER,ORIGINAL_BINDER_SHA256,'ORIGINAL_BINDER_PIN'),
        ORIGINAL_BINDER,'original_source_assignments')
    raw=pinned(ORIGINAL_RECEIVER,ORIGINAL_RECEIVER_SHA256,'ORIGINAL_RECEIVER_PIN')
    rt=strict(runtime_raw,16384)
    workspace=binder.path(rt['workspace_root'])
    binder.path(rt['receiver_output_root'])
    binder.path(rt['maintained_source_root'])
    node=next(n.value for n in ast.parse(raw).body if isinstance(n,ast.Assign) and
        isinstance(n.targets[0],ast.Name) and n.targets[0].id=='MAINTAINED_SOURCE_ROOTS')
    old=ast.literal_eval(node.args[0].generators[0].iter)
    excluded=tuple(dict.fromkeys(list(old)+[rt['maintained_source_root']]+[str(base/name)
        for base in (workspace,workspace.parent)
        for name in ('source','source-codex-home','source-3e','source-8ee4','source-ea61','source-current')]))
    return binder.assignments(raw,dict(ROOT='Path('+repr(rt['workspace_root'])+')',
        RECEIVER_OUT='Path('+repr(rt['receiver_output_root'])+')',
        RUNTIME_BINDING_SHA=repr(desc(runtime_raw)['sha256']),BINDING_SHA=repr(desc(binding_raw)['sha256']),
        MAINTAINED_SOURCE_ROOTS='tuple(Path(p) for p in '+repr(excluded)+')'))


def require_bound_source(raw, runtime_raw, binding_raw):
    need(raw==bound_receiver_source(runtime_raw,binding_raw),'BOUND_RECEIVER_SOURCE_CHANGED')


def load_receiver(selection, context):
    """Verify installation, reapply the original binder, then call verified().

    All bytes must already have genuine externally received selection/provenance.
    This does not replace the later actual Root require_final_review gate.
    """
    need(type(selection) is dict and set(selection)=={'directory','receiver_sha256','seal_sha256',
        'binding_sha256','runtime_sha256'} and all(digest(v) for k,v in selection.items() if k!='directory'),
        'EXACT_BOUND_RECEIVER_SELECTION')
    directory=checked_path(selection['directory'])
    need(directory.is_dir() and {p.name for p in directory.iterdir()}==RECEIVER_NAMES|{'SEAL.json'},
        'EXACT_SEVEN_MEMBER_RECEIVER')
    raw={}
    for name in RECEIVER_NAMES|{'SEAL.json'}:
        path=directory/name
        need(stat.S_IMODE(path.lstat().st_mode)==0o400,'IMMUTABLE_RECEIVER_MEMBER_MODE')
        raw[name]=checked_file(path,131072)
    for name,field in [('public_receiver.py','receiver_sha256'),('BINDING.json','binding_sha256'),
        ('SUCCESSOR_RUNTIME_BINDING.json','runtime_sha256'),('SEAL.json','seal_sha256')]:
        need(desc(raw[name])['sha256']==selection[field],'SELECTED_RECEIVER_MEMBER_CHANGED')
    seal=strict(raw['SEAL.json'],131072)
    rows=seal['members']
    need(type(rows) is list and len(rows)==seal['member_count']==7 and
         {r['path'] for r in rows}==RECEIVER_NAMES,'RECEIVER_SEAL_POPULATION')
    for row in rows:
        need(row['mode']=='0400' and desc(raw[row['path']])=={k:row[k] for k in ('bytes','sha256')},
            'RECEIVER_SEAL_MEMBER_CHANGED')
    runtime_raw,binding_raw=raw['SUCCESSOR_RUNTIME_BINDING.json'],raw['BINDING.json']
    runtime,binding=strict(runtime_raw,16384),strict(binding_raw,16384)
    need(runtime.get('issuer_thread')==runtime.get('session')==binding.get('session')=='PRO-EXECUTOR-01',
        'CURRENT_PUBLIC_ISSUER_SELECTION')
    need(all(binding.get(k)==context[k] for k in ('repository','branch','source_commit','source_tree')) and
         binding.get('final_tree')==context['workflow_tree'] and
         binding.get('control_branch')==context['branch'].replace('-host-','-control-'),'BOUND_RECEIVER_SUBJECT')
    require_bound_source(raw['public_receiver.py'],runtime_raw,binding_raw)
    # No supplied Python is executed before exact source reconstruction above.
    R=module(raw['public_receiver.py'],directory/'public_receiver.py','exact_bound_public_receiver')
    R.verify_seal(Path(binding['candidate_path']),binding['candidate_seal_sha256'])
    R.verify_seal(Path(binding['composition_path']),binding['composition_seal_sha256'])
    candidate=checked_path(binding['candidate_path'])/'candidate/public'
    compose=checked_path(binding['composition_path'])
    need(candidate.resolve(strict=True)==candidate,'PUBLIC_CANDIDATE_PATH')
    paths=[p for p in candidate.rglob('*') if p.is_file()]
    need(0<len(paths)<=128,'PUBLIC_CANDIDATE_POPULATION')
    public={p.relative_to(candidate).as_posix():checked_file(p,1024**2) for p in paths}
    prefix='qualification/dg16-r5-full-g2/'
    adoption=public[prefix+'PROTECTED_RECIPIENT.json']
    adapter_path=Path(__file__).with_name('binding_adapter.py')
    adapter=module(pinned(adapter_path,BINDING_ADAPTER_SHA256,'BINDING_ADAPTER_PIN'),
        adapter_path,'recovered_successor_binder_adapter')
    selected=adapter.prepare_binder(pinned(ORIGINAL_BINDER,ORIGINAL_BINDER_SHA256,'ORIGINAL_BINDER_PIN'),
        desc(adoption)['sha256'],strict(adoption,16384)['recipient'])
    structural={name:checked_file(ORIGINAL_RECEIVER.parent/name,131072)
        for name in ('public_receiver.py','admission_gate.py','native_public.py','BINDING_TEMPLATE.json')}
    review_selection=strict(raw['FINAL_REVIEW_SELECTION.json'],16384)
    need(review_selection['reviewer'] not in CURRENT_SOURCE_AUTHORS,'ACTUAL_DISTINCT_SOURCE_REVIEWER')
    decisions=('INDEPENDENT_COLD_REVIEW.json','ROOT_POLICY_ADOPTION.json',
        'NATIVE_INDEPENDENT_REVIEW.json','ROOT_NATIVE_APPLICABILITY_ADOPTION.json')
    inputs=dict(host_adoption=adoption,runtime=runtime_raw,binding=binding_raw,
        review_selection=raw['FINAL_REVIEW_SELECTION.json'],author=review_selection['author'],
        composition=checked_file(compose/'COMPOSITION.json',16384),
        policy_gate=checked_file(compose/'POLICY_GATE_READBACK.json',16384),
        native_gate=checked_file(compose/'NATIVE_GATE_READBACK.json',16384),
        decisions={name:checked_file(compose/'public/qualification/dg16-r5-full-g2-decisions'/name,65536)
            for name in decisions})
    rebound=selected.bind_public(structural,public,inputs)
    need(rebound=={name:raw[name] for name in RECEIVER_NAMES},'EXACT_ORIGINAL_PUBLIC_REBIND')
    R.verified()  # Unchanged original seals, composition, policy and native admission.
    return R


def validate_authors(value):
    need(type(value) in (list,tuple) and value and all(type(v) is str and
         re.fullmatch(r'/root(?:/[a-z0-9_]+)*',v) for v in value) and
         set(CURRENT_SOURCE_AUTHORS)<=set(value),'ACTUAL_SOURCE_AUTHORS_REQUIRED')
    return value


def control_preparer_source(runtime_raw, binding_raw, receiver_directory, author, live_directory):
    """Original control_source transformation with selected PRO issuer/paths."""
    core_raw=pinned(PUBLIC_OPERATOR,PUBLIC_OPERATOR_SHA256,'ORIGINAL_CONTROL_SOURCE_PIN')
    binder=module(pinned(ORIGINAL_BINDER,ORIGINAL_BINDER_SHA256,'ORIGINAL_BINDER_PIN'),
        ORIGINAL_BINDER,'control_source_assignments')
    control_raw=pinned(CONTROL_OWNER,CONTROL_OWNER_SHA256,'ORIGINAL_CONTROL_OWNER_PIN')
    core=module(binder.assignments(core_raw,{'ISSUER':repr('PRO-EXECUTOR-01')}),
        PUBLIC_OPERATOR,'original_public_control_source')
    subject=types.SimpleNamespace(runtime=strict(runtime_raw,16384),b=strict(binding_raw,16384),
        binding={'source_author':author},sources={'prepare_live_control.py':control_raw})
    prepared=core.PublicOperator.control_source(subject,receiver_directory,binding_raw)
    binder.path(live_directory)
    return binder.assignments(prepared,{'LIVE':'Path('+repr(live_directory)+')'})


def load_control_preparer(receiver, live_directory, author):
    directory=Path(receiver.__file__).parent
    raw=control_preparer_source(checked_file(directory/'SUCCESSOR_RUNTIME_BINDING.json',16384),
        checked_file(directory/'BINDING.json',16384),str(directory),author,live_directory)
    return module(raw,CONTROL_OWNER,'original_bound_control_verification'),raw


def verify_original_control_inputs(receiver, live_directory, root_input, payload, authors,
                                   review_seal_sha256, archive, metadata):
    """Run original statements only, stopping before Root body construction."""
    need(type(root_input) is dict and set(root_input)=={'path','bytes','sha256'},
        'ACTUAL_ROOT_DECISION_INPUT_REQUIRED')
    selected_raw=checked_file(root_input['path'],16384)
    need(desc(selected_raw)=={k:root_input[k] for k in ('bytes','sha256')},'ROOT_DECISION_INPUT_CHANGED')
    validate_authors(authors)
    P,source=load_control_preparer(receiver,live_directory,authors[0])
    main=next(n for n in ast.parse(source).body if isinstance(n,ast.FunctionDef) and n.name=='main')
    def positions(name):
        return [i for i,n in enumerate(main.body) if isinstance(n,ast.Assign) and
            isinstance(n.targets[0],ast.Name) and n.targets[0].id==name]
    starts,ends=positions('selected_raw'),positions('common')
    need(len(starts)==len(ends)==1 and starts[0]<ends[0],'EXACT_ORIGINAL_CONTROL_VERIFICATION_PREFIX')
    P.args=types.SimpleNamespace(root_input=Path(root_input['path']))
    exec(compile(ast.Module(body=main.body[starts[0]:ends[0]],type_ignores=[]),
        str(CONTROL_OWNER),'exec',dont_inherit=True,optimize=0),P.__dict__)
    need(P.selected_raw==selected_raw and P.archive==archive and P.metadata==metadata and
         P.review_raw==payload['INDEPENDENT_REVIEW.json'],'ORIGINAL_CONTROL_INPUT_JOIN')
    need(P.selected['independent_review_seal_sha256']==review_seal_sha256 and
         P.review['reviewer'] not in authors,'ACTUAL_DISTINCT_REVIEW_SEAL_JOIN')
    return dict(status='ORIGINAL_REVIEW_AND_ROOT_INPUT_CHECKS_PASSED_DATA_ONLY',authority='NONE',
        preparer_source=desc(source),root_decision_input=desc(selected_raw),review_seal_sha256=review_seal_sha256,
        review=desc(P.review_raw),final=desc(P.acquire(P.review_dir/'FINAL.json',16384)),
        receiver_binding_sha256=P.R.BINDING_SHA,request_sha256=desc(P.request_raw)['sha256'],
        proof_sha256=desc(P.files['PROOF.json'])['sha256'],root_consumption_issued=False,original_acceptance=False)


def original_tree_id(rows):
    raw=pinned(CONTROL_OWNER,CONTROL_OWNER_SHA256,'ORIGINAL_CONTROL_OWNER_PIN')
    node=next(n for n in ast.parse(raw).body if isinstance(n,ast.FunctionDef) and n.name=='tree_id')
    namespace={'hashlib':hashlib}
    exec(compile(ast.Module(body=[node],type_ignores=[]),
        str(CONTROL_OWNER),'exec',dont_inherit=True,optimize=0),namespace)
    return namespace['tree_id'](rows)


def prepare_control(receiver, archive, context, metadata, payload, leaves, *,
                    source_authors, review_seal_sha256):
    """Prepare original Git additions from already authored public decisions."""
    observation=inspect_public(receiver,archive,'live',context,metadata)
    binding,_,_,modules,_,_=receiver.verified()
    request_raw=receiver.decode_zip(archive,'live')['REQUEST.json']
    request=strict(request_raw,4096)
    need(type(payload) is dict and all(type(v) is bytes for v in payload.values()),'EXISTING_CONTROL_BYTES')
    validate_authors(source_authors)
    checked=modules['live_control.py'].validate(payload,request_raw,now=time.time())
    need(type(leaves) is list and len(leaves)<=10000 and all(type(r) is dict and
         type(r.get('path')) is str and not r['path'].startswith('/') and
         not any(p in ('','..','.') for p in r['path'].split('/')) and
         r.get('mode') in ('100644','100755') and digest(r.get('git_blob'),40) for r in leaves),
         'EXACT_COMPOSITION_LEAVES')
    need(original_tree_id(leaves)==binding['final_tree']==context['workflow_tree'],'COMPOSITION_BASE_TREE_CHANGED')
    if checked['decision']=='CONSUME':
        need(digest(review_seal_sha256) and checked['independent_reviewer'] not in source_authors,
            'ACTUAL_DISTINCT_LIVE_REVIEW_REQUIRED')
    else:
        need(checked['decision']=='STOP' and set(payload)=={'CONTROL.json'} and review_seal_sha256 is None,
            'STOP_DOES_NOT_ISSUE_CONSUMPTION')
    names={r['path'] for r in leaves}
    added,elements=[],[]
    for name,raw in sorted(payload.items()):
        path=request['control_path']+'/'+name
        need(path not in names and 0<len(raw)<=4096,'EXACT_ONLY_NEW_CONTROL_FILES')
        blob=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
        added.append(dict(path=path,mode='100644',git_blob=blob,**desc(raw)))
        elements.append(dict(path=path,mode='100644',type='blob',content=raw.decode('ascii')))
    tree=original_tree_id(leaves+added)
    need(time.time()<request['expires_utc_epoch'],'ORIGINAL_LIVE_CONTROL_EXPIRED')
    result=dict(payload)
    result['ROOT_LIVE_OBSERVATION.json']=encode(observation)
    result['CreateTree.json']=encode(dict(repository_full_name=binding['repository'],
        base_tree_sha=binding['final_tree'],tree_elements=elements))
    if checked['decision']=='CONSUME':
        result['PUBLICATION_REQUEST.json']=encode(dict(schema='dg16.current-g2.actual-live-control-publication-request.v1',
            actor='/root',branch=binding['control_branch'],sole_parent=request['workflow_commit'],
            expected_tree=tree,additions=added,run_id=request['run_id'],run_attempt=1,
            request_sha256=desc(request_raw)['sha256'],proof_sha256=request['proof']['sha256'],
            independent_review_seal_sha256=review_seal_sha256,expires_utc_epoch=request['expires_utc_epoch'],
            automatic_retry=False,original_awards=[],
            admission='ROOT_MUST_PERSIST_EXACT_ONE_SHOT_EFFECT_GRANT_BEFORE_PROVIDER_WRITE'))
    else:
        result['ADDITIONS.json']=encode(dict(expected_tree=tree,additions=added,authority='NONE',
            provider_effects=0,original_acceptance=False))
    return result


def validate_published_control(value):
    """Original validator for independently fetched immutable public bodies."""
    need(type(value) is dict and set(value)=={'receiver','context','request_raw','payload','source_authors','expires_ms'},
        'CONTROL_READBACK_FIELDS')
    need(type(value['expires_ms']) is int and time.time()*1000<value['expires_ms'],'CONTROL_READBACK_EXPIRED')
    R=load_receiver(value['receiver'],value['context'])
    binding,_,_,modules,_,_=R.verified()
    raw=value['request_raw'].encode('utf8')
    request=strict(raw,4096)
    need(all(request[k]==value['context'][k] for k in
         ('repository','branch','run_id','workflow_commit','source_commit','source_tree')) and
         request['control_branch']==binding['control_branch'],'CONTROL_READBACK_SUBJECT')
    payload={name:body.encode('utf8') for name,body in value['payload'].items()}
    result=modules['live_control.py'].validate(payload,raw,now=time.time())
    authors=validate_authors(value['source_authors'])
    need(result.get('independent_reviewer') not in authors,'CONTROL_READBACK_ACTUAL_DISTINCT_REVIEWER')
    need(time.time()*1000<min(value['expires_ms'],request['expires_utc_epoch']*1000),'CONTROL_READBACK_EXPIRED')
    return dict(schema='dg16.successor-public-control-readback.v1',authority='NONE',
        original_acceptance=False,review_issued=False,root_consumption_issued=False,
        request=desc(raw),files={name:desc(body) for name,body in sorted(payload.items())},**result)


def validate_selection(value):
    """Data consistency only; authentic admission is the V8 caller's duty."""
    need(type(value) is dict and set(value)=={'mode','actor','source_sha256','operator_receipt',
        'independent_receipt','body_outcome','receiver','journal_parent','authorization_sha256','expires_ms','control'},
        'EXACT_SEMANTIC_SELECTION')
    need(value['mode'] in ('receive','control') and digest(value['source_sha256']) and
         digest(value['authorization_sha256']),'SEMANTIC_SOURCE_AND_EXTERNAL_AUTHORITY_SELECTION')
    now=time.time()*1000
    operator,independent=value['operator_receipt'],value['independent_receipt']
    for receipt,is_independent in ((operator,False),(independent,True)):
        need(type(receipt) is dict,'RECEIPT_REQUIRED')
        unsigned={k:v for k,v in receipt.items() if k!='receipt_sha256'}
        need(digest(receipt.get('receipt_sha256')) and
             desc(canonical(unsigned))['sha256']==receipt['receipt_sha256'],'RECEIPT_CHANGED')
        need(receipt.get('schema')=='dg16.github-public-provider-observation.v1' and
             receipt.get('operator')=='PRO-EXECUTOR-01' and
             receipt.get('successor')=='PRO-EXECUTOR-01, designated by owner' and receipt.get('authority')=='NONE' and
             receipt.get('purpose') in ('SOURCE_QUALIFICATION','OWNER_APPROVED_ORIGINAL_ROUTE') and
             receipt.get('role') in ('live','terminal') and
             all(receipt.get(k) is False for k in ('original_acceptance','private_or_cipher','automatic_retry')),
             'PUBLIC_RECEIPT_SCOPE')
        source=receipt['source']
        need(type(source) is dict and set(source)=={'channel_sha256','journal_sha256','journal_path','python_path'} and
             source['channel_sha256']==CHANNEL_SHA256 and source['journal_sha256']==CHANNEL_JOURNAL_SHA256 and
             all(type(source[k]) is str and source[k].startswith('/') and len(source[k])<=4096 and
                 not any(ord(c)<32 or ord(c)==127 for c in source[k]) for k in ('journal_path','python_path')),
             'REVIEWED_CHANNEL_REQUIRED')
        need(receipt['public_metadata']==receipt['facts']['public_metadata'],'RECEIPT_FACTS_CHANGED')
        need(all(type(receipt.get(k)) is int for k in ('observed_start_ms','observed_end_ms','expires_ms')) and
             receipt['observed_start_ms']<=receipt['observed_end_ms']<=now<receipt['expires_ms']<=
             receipt['observed_start_ms']+300000,'CURRENT_PARENT_RECEIPT_REQUIRED')
        if is_independent:
            need(receipt.get('status')=='INDEPENDENT_PROVIDER_FACTS_MATCH_ONLY' and
                 type(receipt.get('actor')) is str and re.fullmatch(r'/root/[a-z0-9_]+',receipt['actor']),
                 'DISTINCT_RECEIVER_SELECTION')
        else:
            need(receipt.get('status')=='PUBLIC_PROVIDER_OBSERVATION_REQUIRES_INDEPENDENT_RECEIVING' and
                 receipt.get('actor')=='/root','ROOT_OPERATOR_SELECTION')
    need(independent.get('independent_operator_receipt_sha256')==operator['receipt_sha256'] and
         operator['observed_end_ms']<=independent['observed_start_ms'] and
         all(operator[k]==independent[k] for k in ('purpose','role','source','context','facts','public_metadata','control_selection')),
         'INDEPENDENT_RECEIVING_JOIN')
    need(value['actor']==('/root' if value['mode']=='control' else independent['actor']) and
         (value['mode']!='control' or operator['role']=='live'),'ACTUAL_SELECTED_ROLE')
    context=operator['context']
    need(context.get('repository')=='theislampill/IMPLEMENTAUDIT.md' and
         type(context.get('branch')) is str and re.fullmatch(r'pro/dg16-r5-full-g2-direct-host-[0-9]+-[0-9]{8}',context['branch']) and
         type(context.get('run_id')) is str and re.fullmatch('[1-9][0-9]{0,15}',context['run_id']) and
         type(context.get('run_attempt')) is int and context['run_attempt']==1 and
         all(digest(context.get(k),40) for k in ('workflow_commit','workflow_tree','source_commit','source_tree')),
         'EXACT_G221_CONTEXT')
    need(type(value['expires_ms']) is int and now<value['expires_ms']<=min(operator['expires_ms'],independent['expires_ms']),
         'SEMANTIC_PARENT_DEADLINE')
    body=value['body_outcome']
    artifact=operator['public_metadata']['artifact']
    need(type(body) is dict and body.get('status')=='EXACT_PUBLIC_BODY_RECEIVED' and
         body.get('authority')=='NONE' and body.get('operator')=='PRO-EXECUTOR-01' and
         body.get('purpose')==operator['purpose'] and body.get('provider_receipt_sha256')==operator['receipt_sha256'] and
         body.get('archive')=={'bytes':artifact['size_in_bytes'],'sha256':artifact['digest'].removeprefix('sha256:')} and
         type(body.get('body_get_attempts')) is int and body['body_get_attempts']==1 and
         all(body.get(k) is False for k in ('signed_url_retained','automatic_retry','original_acceptance')),
         'EXACT_ACQUIRED_PUBLIC_BODY')
    checked_path(body['journal_path'])
    receiver=value['receiver']
    need(type(receiver) is dict and set(receiver)=={'directory','receiver_sha256','seal_sha256','binding_sha256','runtime_sha256'} and
         all(digest(v) for k,v in receiver.items() if k!='directory'),'EXACT_RECEIVER_SELECTION')
    checked_path(receiver['directory'])
    journal=checked_path(value['journal_parent'])
    info=journal.lstat()
    need(stat.S_ISDIR(info.st_mode) and info.st_uid==os.geteuid() and stat.S_IMODE(info.st_mode)==0o700,
        'PRIVATE_JOURNAL_PARENT_REQUIRED')
    control=value['control']
    if value['mode']=='receive':
        need(control is None,'NO_CONTROL_FRAME_FOR_RECEIVING')
    else:
        need(type(control) is dict and set(control)=={'frame_sha256','leaves_path','leaves'} and
             digest(control['frame_sha256']) and type(control['leaves']) is dict and
             set(control['leaves'])=={'bytes','sha256'} and type(control['leaves']['bytes']) is int and
             0<control['leaves']['bytes']<=2*1024**2 and digest(control['leaves']['sha256']),
             'EXACT_CONTROL_SELECTION')
        checked_path(control['leaves_path'])
    return value


def run(input_selection):
    journal=None
    stage='selection'
    started=time.monotonic()
    try:
        selected=validate_selection(strict(canonical(input_selection),65536))
        operator,independent=selected['operator_receipt'],selected['independent_receipt']
        context=operator['context']
        expires=selected['expires_ms']
        def current():
            need(time.time()*1000<expires,'SEMANTIC_RECEIVING_EXPIRED')
            need(desc(checked_file(Path(__file__),262144))['sha256']==selected['source_sha256'],'SEMANTIC_SOURCE_CHANGED')
        current()
        resolver,writer=source_owners()
        stage='bound-receiver'
        receiver=load_receiver(selected['receiver'],context)
        current()
        archive_path=Path(selected['body_outcome']['journal_path'])/'ARTIFACT.zip'
        raw=checked_file(archive_path,400000)
        need(desc(raw)==selected['body_outcome']['archive'],'ACQUIRED_ARCHIVE_CHANGED')
        if operator['role']=='live':
            request=receiver.strict(receiver.decode_zip(raw,'live')['REQUEST.json'])
            need(type(request['expires_utc_epoch']) is int,'LIVE_REQUEST_DEADLINE_REQUIRED')
            expires=min(expires,request['expires_utc_epoch']*1000)
            current()
        key=desc(canonical({k:context[k] for k in ('repository','run_id','run_attempt','workflow_commit')} |
            {'actor':selected['actor'],'role':operator['role'],'mode':selected['mode']}))['sha256']
        stage='intent'
        journal=writer(Path(selected['journal_parent'])/key)
        job=independent['facts']['job']
        log_request=None
        if operator['role']=='terminal':
            need(type(job['id']) is int and job['id']>0 and job['run_id']==int(context['run_id']) and
                 job['run_attempt']==1 and job['head_sha']==context['workflow_commit'] and
                 job['name']=='full-registry-raw-pair' and job['status']=='completed','SELECTED_TERMINAL_JOB_REQUIRED')
            log_request={'repo_full_name':context['repository'],'job_id':job['id']}
        journal.write('INTENT.json',encode(dict(schema='dg16.successor-public-semantic-intent.v1',authority='NONE',
            actor=selected['actor'],mode=selected['mode'],source_sha256=selected['source_sha256'],receiver=selected['receiver'],
            operator_receipt_sha256=operator['receipt_sha256'],independent_receipt_sha256=independent['receipt_sha256'],
            archive=desc(raw),job_log_tool='mcp__codex_apps__github_fetch_workflow_job_logs' if log_request else None,
            job_log_request=log_request,control=selected['control'],authorization_sha256=selected['authorization_sha256'],
            expires_ms=expires,automatic_retry=False,original_acceptance=False)))
        current()
        stage='bounded-frame'
        frame=resolver.read_ephemeral_frame(TOOL_MAX,min(45,(expires-time.time()*1000)/1000))
        current()
        frame_descriptor=desc(frame)
        stage='semantic-receiving'
        if selected['mode']=='control':
            need(frame_descriptor['sha256']==selected['control']['frame_sha256'],'SELECTED_CONTROL_FRAME_CHANGED')
            request=strict(frame,65536)
            need(type(request) is dict and set(request)=={'payload','source_authors','review_seal_sha256','root_decision_input'},
                'CONTROL_FRAME_FIELDS')
            payload={n:body.encode('utf8') for n,body in request['payload'].items()}
            control_evidence=None
            if set(payload)!={'CONTROL.json'}:
                control_evidence=verify_original_control_inputs(receiver,str(archive_path.parent),request['root_decision_input'],
                    payload,request['source_authors'],request['review_seal_sha256'],raw,independent['public_metadata'])
            else:
                need(request['root_decision_input'] is None,'STOP_DOES_NOT_ISSUE_CONSUMPTION')
            leaves_raw=checked_file(selected['control']['leaves_path'],2*1024**2)
            need(desc(leaves_raw)==selected['control']['leaves'],'SELECTED_COMPOSITION_LEAVES_CHANGED')
            leaves=strict(leaves_raw,2*1024**2)['members']
            prepared=prepare_control(receiver,raw,context,independent['public_metadata'],payload,leaves,
                source_authors=request['source_authors'],review_seal_sha256=request['review_seal_sha256'])
            current()
            for name,body in prepared.items():
                journal.write(name,body)
                current()
            result=dict(status='LOCAL_CONTROL_PREPARATION_REQUIRES_SEPARATE_PUBLICATION_AUTHORITY',
                prepared={n:desc(b) for n,b in sorted(prepared.items())},provider_effects=0,original_control_checks=control_evidence)
            if 'PUBLICATION_REQUEST.json' in prepared:
                result['publication_inputs']=dict(request_raw=receiver.decode_zip(raw,'live')['REQUEST.json'].decode('utf8'),
                    files={n:body.decode('utf8') for n,body in payload.items()},
                    create_tree=strict(prepared['CreateTree.json'],65536),
                    publication_request=strict(prepared['PUBLICATION_REQUEST.json'],65536),
                    source_authors=request['source_authors'])
        else:
            if operator['role']=='terminal':
                log=decode_log_wrapper(frame)
            else:
                need(strict(frame,16)=={},'NO_LIVE_LOG_SUBSTITUTION')
                log=None
            observation=inspect_public(receiver,raw,operator['role'],context,independent['public_metadata'],terminal_log=log)
            current()
            result=dict(status='PUBLIC_SEMANTIC_RECEIVING_COMPLETE_DATA_ONLY',observation=observation)
        need(checked_file(archive_path,400000)==raw,'ACQUIRED_ARCHIVE_CLOSING_CHANGED')
        result.update(schema='dg16.successor-public-semantic-outcome.v1',authority='NONE',original_acceptance=False,
            automatic_retry=False,operator_receipt_sha256=operator['receipt_sha256'],independent_receipt_sha256=independent['receipt_sha256'],
            source_sha256=selected['source_sha256'],receiver=selected['receiver'],frame=frame_descriptor,
            journal_path=str(journal.path),elapsed_seconds=time.monotonic()-started,expires_ms=expires,
            external_authority_and_actual_distinct_agent_required=True)
        current()
        stage='final-durable-write'
        journal.write('FINAL.json',encode(result))
        current()
        return result
    except BaseException:
        result=dict(status='REFUSED_OR_UNCERTAIN_NO_RETRY',authority='NONE',stage=stage,
            automatic_retry=False,original_acceptance=False)
        if journal is not None:
            try:
                journal.write('UNKNOWN.json',encode(result))
            except BaseException:
                result['journal_completion']='UNKNOWN'
        return result
    finally:
        if journal is not None:
            journal.close()


if __name__=='__main__':
    try:
        need(len(sys.argv) in (2,3) and sys.flags.isolated and sys.dont_write_bytecode and
             sys.flags.optimize==0,'FIXED_ISOLATED_UNOPTIMIZED_ENTRY')
        if len(sys.argv)==3:
            need(sys.argv[1]=='--control-readback','FIXED_CONTROL_READBACK_ENTRY')
            result=validate_published_control(strict(sys.argv[2].encode('utf8'),65536))
        else:
            result=run(strict(sys.argv[1].encode('utf8'),65536))
        print(json.dumps(result,sort_keys=True),flush=True)
        raise SystemExit(0 if result.get('schema')=='dg16.successor-public-control-readback.v1' or result.get('status') in
            ('PUBLIC_SEMANTIC_RECEIVING_COMPLETE_DATA_ONLY','LOCAL_CONTROL_PREPARATION_REQUIRES_SEPARATE_PUBLICATION_AUTHORITY') else 1)
    except SystemExit:
        raise
    except BaseException:
        print('{"status":"REFUSED_OR_UNCERTAIN_NO_RETRY","authority":"NONE","automatic_retry":false,"original_acceptance":false}',flush=True)
        raise SystemExit(1)
