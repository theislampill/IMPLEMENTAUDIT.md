"""Bounded full-G2 data receiver; never reviews, consumes, grants or awards.

Acquisition is outside this program. A live preview has no terminal log copy.
The exact bound packet is preparation only and carries no launch readiness.
"""
from pathlib import Path
import argparse,hashlib,io,json,os,re,stat,sys,time,types,zipfile

HERE=Path(__file__).resolve().parent
ROOT = Path('/home/agent/dg16-g2-current04-public-20261109')
RUNTIME_BINDING_SHA = '8f8b04026a9a29cbc84841c857ba1d07e717bdcf7e8283c5ee20eb433d9dd5e5'
MAINTAINED_SOURCE_ROOTS = tuple(Path(p) for p in ('/workspace/scratch/6746ee3422fa/source', '/workspace/scratch/6746ee3422fa/source-codex-home', '/workspace/scratch/6746ee3422fa/source-3e', '/workspace/scratch/6746ee3422fa/source-8ee4', '/workspace/scratch/6746ee3422fa/source-ea61', '/workspace/scratch/6746ee3422fa/source-current', '/home/agent/dg16-g2-current04-public-20261109/source', '/home/agent/dg16-g2-current04-public-20261109/source-codex-home', '/home/agent/dg16-g2-current04-public-20261109/source-3e', '/home/agent/dg16-g2-current04-public-20261109/source-8ee4', '/home/agent/dg16-g2-current04-public-20261109/source-ea61', '/home/agent/dg16-g2-current04-public-20261109/source-current', '/home/agent/source', '/home/agent/source-codex-home', '/home/agent/source-3e', '/home/agent/source-8ee4', '/home/agent/source-ea61', '/home/agent/source-current'))
RECEIVER_OUT = Path('/home/agent/dg16-g2-current04-public-20261109/public-receiving')
BINDING_SHA = 'a0750feb79bbbe00c20b852bb179989a8dce89669130effbb6a8433774f0b6e9'
NAMES=('RESULT.json','HOST.json','SOURCE.json','PROBE.json','CLEANUP.json','FAILURE.json','ARTIFACT_MANIFEST.json')
def need(value,code):
    if not value:raise ValueError(code)
def audit(event,args):
    if event in ('subprocess.Popen','os.system','os.fork','os.posix_spawn','socket.__new__'):raise ValueError('RECEIVER_PROCESS_OR_NETWORK_FORBIDDEN')
    if event=='exec' and args and type(args[0]) is types.CodeType:
        need(not any(args[0].co_filename.startswith(str(root)+'/') for root in MAINTAINED_SOURCE_ROOTS),'RECEIVER_MAINTAINED_EXECUTION_FORBIDDEN')
sys.addaudithook(audit)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def desc(raw):return {'bytes':len(raw),'sha256':sha(raw)}
def encode(value):return (json.dumps(value,sort_keys=True,indent=2,ensure_ascii=True,allow_nan=False)+'\n').encode('ascii')
def strict(raw):
    def pairs(items):
        result={}
        for key,value in items:
            need(key not in result,'DUPLICATE_JSON_KEY');result[key]=value
        return result
    return json.loads(raw,object_pairs_hook=pairs,parse_constant=lambda _:(_ for _ in ()).throw(ValueError('NONFINITE_JSON')))
def acquire(path,limit):
    before=path.lstat();need(stat.S_ISREG(before.st_mode) and before.st_nlink==1 and 0<=before.st_size<=limit,'INPUT_FILE_SHAPE')
    fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC)
    try:
        with os.fdopen(fd,'rb',closefd=False) as stream:raw=stream.read(limit+1)
        after=os.fstat(fd)
        stamp=lambda s:(s.st_dev,s.st_ino,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
        need(stamp(before)==stamp(after)==stamp(path.lstat()) and len(raw)==before.st_size,'INPUT_CHANGED')
        return raw
    finally:os.close(fd)
def verify_seal(path,wanted):
    raw=acquire(path/'SEAL.json',65536);need(sha(raw)==wanted,'DEPENDENCY_SEAL_CHANGED');value=strict(raw)
    rows=value['members'];need(type(rows) is list and len(rows)==value['member_count'] and len({r['path'] for r in rows})==len(rows),'DEPENDENCY_MEMBER_POPULATION')
    for row in rows:
        name=Path(row['path']);need(not name.is_absolute() and '..' not in name.parts,'DEPENDENCY_PATH')
        need(desc(acquire(path/name,8*1024**2))=={k:row[k] for k in ('bytes','sha256')},'DEPENDENCY_MEMBER_CHANGED')
    return value
def verified():
    need(type(RUNTIME_BINDING_SHA) is str,'SUCCESSOR_RUNTIME_BINDING_REQUIRED')
    runtime_raw=acquire(HERE/'SUCCESSOR_RUNTIME_BINDING.json',16384)
    need(sha(runtime_raw)==RUNTIME_BINDING_SHA,'SUCCESSOR_RUNTIME_BINDING_CHANGED')
    raw=acquire(HERE/'BINDING.json',16384);need(sha(raw)==BINDING_SHA,'RECEIVER_BINDING_CHANGED');b=strict(raw)
    lane=Path(b['candidate_path']);compose=Path(b['composition_path']);code=lane/'candidate/public/qualification/dg16-r5-full-g2'
    verify_seal(lane,b['candidate_seal_sha256']);verify_seal(compose,b['composition_seal_sha256'])
    c_raw=acquire(compose/'COMPOSITION.json',16384);g_raw=acquire(compose/'POLICY_GATE_READBACK.json',16384)
    need(sha(c_raw)==b['composition_sha256'] and sha(g_raw)==b['policy_gate_sha256'],'COMPOSITION_RECORD_CHANGED')
    composition,gate=strict(c_raw),strict(g_raw)
    for field in ('source_commit','source_tree','final_tree','branch','control_branch','candidate_seal_sha256'):
        need(composition[field]==b[field],'COMPOSITION_BINDING')
    need(composition['independent_review_seal_sha256']==b['code_review_seal_sha256'] and
         gate['review_sha256']==b['public_review_sha256'] and gate['adoption_sha256']==b['public_adoption_sha256'],'DECISION_BINDING')
    acquired={n:acquire(code/n,1024**2) for n in b['modules']}
    need(all(desc(raw)==b['modules'][n] for n,raw in acquired.items()),'VALIDATOR_PIN_CHANGED')
    modules={}
    for n in ('host_utility.py','full_relation.py','live_control.py','run.py','capture_evidence.py'):
        m=types.ModuleType('receiver_bound_'+n[:-3]);m.__file__=str(code/n)
        exec(compile(acquired[n],str(code/n),'exec',dont_inherit=True,optimize=0),m.__dict__);modules[n]=m
    native_raw=acquire(HERE/'native_public.py',65536)
    need(desc(native_raw)==b['native_public_validator'],'NATIVE_PUBLIC_VALIDATOR_PIN')
    native=types.ModuleType('receiver_current_native_public');native.__file__=str(HERE/'native_public.py')
    exec(compile(native_raw,native.__file__,'exec',dont_inherit=True,optimize=0),native.__dict__)
    modules['native_public.py']=native
    modules['native_integration.py']=modules['run.py'].load_native(modules['host_utility.py'])
    native_gate_raw=acquire(compose/'NATIVE_GATE_READBACK.json',16384)
    need(sha(native_gate_raw)==b['native_gate_sha256'],'NATIVE_GATE_RECORD_CHANGED')
    integration=modules['native_integration.py']
    decisions=compose/'public/qualification/dg16-r5-full-g2-decisions'
    payload={name:acquire(decisions/name,65536) for name in integration.A.FILES}
    native.validate_admission(payload,integration=integration,gate=strict(native_gate_raw),
        binding=b,composition=composition)
    return b,composition,gate,modules,strict(acquired['CAPTURE_DIAGNOSTIC_CATALOG.json']),strict(acquired['SOURCE_MANIFEST.json'])

def expected_names(kind):
    need(kind in ('live','terminal'),'ARTIFACT_KIND')
    return set(NAMES) if kind=='terminal' else {'REQUEST.json','PROOF.json'}|{'public/'+n for n in NAMES}
def decode_zip(raw,kind):
    need(type(raw) is bytes and 0<len(raw)<=400000,'ARCHIVE_COMPRESSED_BOUND');expected=expected_names(kind)
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        infos=archive.infolist();need(len(infos)==len(expected) and {i.filename for i in infos}==expected,'ARCHIVE_POPULATION')
        need(sum(i.file_size for i in infos)<=262144,'ARCHIVE_TOTAL_BOUND');files={}
        for entry in infos:
            limit=4096 if entry.filename=='REQUEST.json' else 16384 if entry.filename=='PROOF.json' else 65536
            need(entry.filename not in files and not entry.is_dir() and not entry.flag_bits&1 and
                 entry.compress_type in (zipfile.ZIP_STORED,zipfile.ZIP_DEFLATED) and
                 stat.S_IFMT(entry.external_attr>>16) in (0,stat.S_IFREG) and 0<entry.file_size<=limit,'ARCHIVE_ENTRY')
            with archive.open(entry) as stream:data=stream.read(limit+1)
            need(len(data)==entry.file_size and encode(strict(data))==data,'ARCHIVE_MEMBER_CANONICAL')
            files[entry.filename]=data
    return files

def metadata_bindings(metadata,kind,run_id,workflow_commit,archive,b):
    need(type(metadata) is dict and set(metadata)=={'run','commit','artifact'},'METADATA_POPULATION')
    run,commit,artifact=(metadata[n] for n in ('run','commit','artifact'))
    need(type(run_id) is str and re.fullmatch('[1-9][0-9]{0,19}',run_id) and re.fullmatch('[0-9a-f]{40}',workflow_commit),'EXPECTED_ACTUAL_IDENTITY')
    need(type(run['id']) is int and str(run['id'])==run_id and type(run['run_attempt']) is int and run['run_attempt']==1 and
         run['head_sha']==workflow_commit and run['head_branch']==b['branch'] and run['event']=='push' and
         run['repository']['full_name']==b['repository'],'ACTUAL_RUN_BINDING')
    need(run['status']==('in_progress' if kind=='live' else 'completed'),'ACTUAL_RUN_PHASE')
    need(commit['sha']==workflow_commit and commit['tree']['sha']==b['final_tree'] and
         [p['sha'] for p in commit['parents']]==[b['source_commit']],'ACTUAL_COMMIT_TREE_PARENT')
    name=('dg16-full-correspondence-review-' if kind=='live' else 'dg16-full-registry-')+run_id+'-1'
    need(type(artifact['id']) is int and artifact['id']>0 and artifact['name']==name and artifact['expired'] is False and
         artifact['size_in_bytes']==archive['bytes'] and artifact['digest']=='sha256:'+archive['sha256'] and
         artifact['workflow_run']['id']==run['id'] and artifact['workflow_run']['head_sha']==workflow_commit and
         artifact['workflow_run']['head_branch']==b['branch'],'ACTUAL_ARTIFACT_BINDING')
    return {'run_id':run_id,'run_attempt':1,'workflow_commit':workflow_commit,'artifact_id':artifact['id'],
            'metadata_sha256':{n:sha(encode(metadata[n])) for n in metadata},'archive':archive,
            'scope':'PROVIDED_METADATA_BINDINGS; acquisition authenticity is independently received'}

def public_bindings(public,kind,run_id,workflow_commit,b,modules,catalog,manifest):
    utility,parent,evidence=(modules[n] for n in ('host_utility.py','run.py','capture_evidence.py'))
    transport=utility.transport_lines(public)
    docs={n:strict(raw) for n,raw in public.items()}
    result,probe,source,failure,cleanup=(docs[n] for n in ('RESULT.json','PROBE.json','SOURCE.json','FAILURE.json','CLEANUP.json'))
    fixed={'schema':'dg16.full-registry-episode-result.v1','repository':b['repository'],'branch':b['branch'],
           'run_id':run_id,'run_attempt':1,'workflow_commit':workflow_commit}
    need(all(type(result.get(k)) is type(v) and result[k]==v for k,v in fixed.items()),'PUBLIC_RESULT_IDENTITY')
    for key,name in {'adapter_sha256':'run.py','utility_sha256':'host_utility.py','pair_driver_sha256':'pair_driver.py',
                     'source_manifest_sha256':'SOURCE_MANIFEST.json','policy_sha256':'POLICY.json','receiver_inputs_sha256':'RELATION_INPUTS.json'}.items():
        expected=parent.PAIR_DRIVER_SHA if name=='pair_driver.py' else b['modules'][name]['sha256']
        need(result.get(key)==expected,'PUBLIC_CODE_BINDING')
    need(all(result.get(k) is False for k in ('G1','C5','full_G2','G3','full_T14','original_acceptance','audit_closure','independent_assessment','automatic_retry')),'PUBLIC_NO_AWARDS')
    need(source['schema']=='dg16.full-registry-episode-source.v1' and source['commit']==b['source_commit'] and
         source['tree']==b['source_tree'] and source['tracked_source_mutations'] is False,'PUBLIC_SOURCE_BINDING')
    need(set(failure)=={'schema','present','failures','capture_observation','protected_streams'} and
         failure['schema']=='dg16.full-registry-episode-failure.v1' and type(failure['present']) is bool and
         type(failure['failures']) is list,'PUBLIC_FAILURE_SHAPE')
    need(failure['present'] is bool(failure['failures']),'PUBLIC_FAILURE_CONSISTENCY')
    observation=failure['capture_observation']
    need(observation is None or failure['present'] is True,'PUBLIC_SUPPLEMENT_REQUIRES_FAILURE')
    if observation is not None:
        keys={'schema','authority','mode','selection_file','reserved_modes','observation','scope','original_acceptance','Q02'}
        need(type(observation) is dict and set(observation)==keys and
             observation['schema']=='dg16.full-pair-failed-leg-observation.v1' and observation['authority']=='NONE' and
             observation['mode'] in ('legacy','dag') and observation['scope']=='SUPPLEMENTARY_FAILURE_DATA_NOT_FULL_PAIR_RECEIVING' and
             observation['original_acceptance'] is False and observation['Q02'] is False,'PUBLIC_SUPPLEMENT_SCOPE')
        evidence.descriptor(observation['selection_file'],4096)
        projection=evidence.validate_projection(observation['observation'],catalog);record=projection['record']
        need(record['mode']==observation['mode'] and record['attempts']==1 and record['owner_return']!=0 and
             observation['reserved_modes']==(['legacy'] if record['mode']=='legacy' else ['legacy','dag']) and
             projection['diagnostic_complete'] is False and len(encode(observation))<=32768,'PUBLIC_SUPPLEMENT_BINDING')
    ctx=dict(repository=b['repository'],branch=b['branch'],run_id=run_id,run_attempt=1,workflow_commit=workflow_commit,
      source_commit=b['source_commit'],source_tree=b['source_tree'],workflow_path='.github/workflows/dg16-r5-full-g2.yml',job_name='full-registry-raw-pair')
    need('protected_capability' in probe,'PROTECTED_CAPABILITY_FIELD_REQUIRED')
    protected=parent.load_protected(utility).validate_public(probe,failure,ctx,utility)
    native_projection=probe['native_prerequisite']
    native_host=None if native_projection is None or native_projection['requirement'] is None else {k:docs['HOST.json'][k] for k in modules['native_public.py'].HOST_KEYS}
    projection_failure=any(type(row) is dict and row.get('operation') in
        {step+'-native-projection' for step in (*parent.STEPS,'finalize')} for row in failure['failures'])
    native_observation=modules['native_public.py'].validate(native_projection,kind=kind,host=native_host,
        integration=modules['native_integration.py'],projection_failure=projection_failure)
    capture_observation=modules['native_public.py'].capture_records(docs['HOST.json']['commands'],
        positive=kind=='live' or result['status']=='FULL_CORRESPONDENCE_REVIEWED_AND_ROOT_CONSUMED_NO_AUTOMATIC_ACCEPTANCE')
    if probe['result'] is not None:parent.validate_pair_summary(probe['result'])
    if kind=='live':
        need(failure=={'schema':'dg16.full-registry-episode-failure.v1','present':False,'failures':[],'capture_observation':None,'protected_streams':None},'LIVE_FAILURE_PRESENT')
        need(cleanup['all_step_children_reaped'] is True and cleanup['private_outputs_uploaded'] is False,'LIVE_CHILD_CUSTODY')
        expected={'all_members_match':True,'file_count':manifest['file_count'],'manifest_sha256':b['modules']['SOURCE_MANIFEST.json']['sha256'],'total_bytes':manifest['total_bytes']}
        need(source['before']==expected and source['after'] is None,'LIVE_SOURCE_BOOKEND_STAGE')
        need(result['completed_steps']==list(parent.STEPS[:-2]) and probe['started'] is True and
             probe['currentness_before_pair'] is True and probe['currentness_after_pair'] is True and
             probe['result_disposition']=='RECEIVED_COMPLETE_RAW_PAIR','LIVE_STAGE_OR_PAIR_BINDING')
        summary=probe['result'];need(summary['receiving_status']=='RECEIVED_COMPLETE_RAW_PAIR','LIVE_COMPLETE_RAW_PAIR')
        need(summary['mapping']['mapped_nodes']==b['registry_population']['nodes'] and summary['mapping']['registered_tests']==b['registry_population']['registered_entries'] and
             summary['mapping']['command_stream']['sha256']==modules['full_relation.py'].COMMAND_SHA and
             all(r['registry_sha256']==modules['full_relation.py'].REGISTRY_SHA for r in summary['records']) and
             all(r['status']=='PASS' and r['terminal'] is True for r in summary['records'][1]['nodes']),'LIVE_FULL_POPULATION')
        need(probe['receiving'].get('status')==summary['receiving_status']==probe['result_disposition']=='RECEIVED_COMPLETE_RAW_PAIR' and
             probe['receiving']['result_sha256']==sha(encode(summary)) and
             probe['receiving']['while_same_checkout_current'] is True and probe['receiving']['receipt_transfer_authority'] is False,'LIVE_RAW_SUMMARY_RECEIVING_JOIN')
    return docs,{'transport_lines':len(transport),'public_bytes':sum(map(len,public.values())),
                 'terminal_status':result['status'],'failure_present':failure['present'],
                 'supplement_present':observation is not None,'native':native_observation,'captures':capture_observation,'protected':protected}

def inspect(files,kind,*,run_id,workflow_commit,metadata,archive,now=None):
    need(set(files)==expected_names(kind),'ARTIFACT_POPULATION')
    b,composition,gate,modules,catalog,manifest=verified()
    meta=metadata_bindings(metadata,kind,run_id,workflow_commit,archive,b)
    public={n:files[n if kind=='terminal' else 'public/'+n] for n in NAMES}
    docs,summary=public_bindings(public,kind,run_id,workflow_commit,b,modules,catalog,manifest)
    result={'schema':'dg16.current-full-g2.data-only-receiving-observation.v1','authority':'NONE',
            'status':'FORMAT_AND_BINDINGS_CHECKED_REQUIRES_ACTUAL_INDEPENDENT_ASSESSMENT','kind':kind,
            'binding_sha256':BINDING_SHA,'composition_seal_sha256':b['composition_seal_sha256'],
            'files':{n:desc(v) for n,v in sorted(files.items())},'metadata':meta,'public':summary,
            'review_issued':False,'root_consumption_issued':False,'launch_readiness':False,'original_acceptance':False}
    if kind=='terminal':
        result['terminal_log_join']='NOT_SUPPLIED_YET';return result
    request,proof,probe=strict(files['REQUEST.json']),strict(files['PROOF.json']),docs['PROBE.json']
    full,live=modules['full_relation.py'],modules['live_control.py']
    fixed={'schema':'dg16.full-correspondence-live-review-request.v1','authority':'NONE','repository':b['repository'],
        'branch':b['branch'],'run_id':run_id,'run_attempt':1,'workflow_commit':workflow_commit,'source_commit':b['source_commit'],
        'source_tree':b['source_tree'],'policy_sha256':b['modules']['POLICY.json']['sha256'],'policy_adoption_sha256':gate['adoption_sha256'],
        'receiver_inputs_sha256':b['modules']['RELATION_INPUTS.json']['sha256'],'full_receiver_sha256':b['modules']['full_relation.py']['sha256'],
        'proof':desc(files['PROOF.json']),'private_observations':proof['private_observations'],'hold_seconds':300,
        'control_branch':b['control_branch'],'control_path':'qualification/dg16-full-g2-control/'+run_id+'-1',
        'private_inputs_retained_while_live':True,'same_job_closing_readback_required':True,'all_declared_relations_equal':True,
        'original_acceptance':False,'automatic_full_G2_award':False}
    need(set(request)==set(fixed)|{'created_utc_epoch','expires_utc_epoch','same_job_currentness_sha256'} and
         all(type(request[k]) is type(v) and request[k]==v for k,v in fixed.items()),'LIVE_REQUEST_BINDINGS')
    need(type(request['created_utc_epoch']) is int and type(request['expires_utc_epoch']) is int and
         request['expires_utc_epoch']==request['created_utc_epoch']+300 and
         type(request['same_job_currentness_sha256']) is str and re.fullmatch('[0-9a-f]{64}',request['same_job_currentness_sha256']),'LIVE_REQUEST_TIME_SHAPE')
    current=time.time() if now is None else now
    need(request['created_utc_epoch']<=current<request['expires_utc_epoch'],'LIVE_REQUEST_EXPIRED_OR_FUTURE')
    full.validate_public_proof(proof,policy_sha=fixed['policy_sha256'],inputs_sha=fixed['receiver_inputs_sha256'],
        source_commit=b['source_commit'],source_tree=b['source_tree'])
    need(proof['all_declared_relations_equal'] is True and probe['result']['full_correspondence']==proof and
         probe['live_review']['status']=='ACTUAL_REVIEW_REQUIRED' and
         probe['live_review']['request_sha256']==sha(files['REQUEST.json']) and
         probe['live_review']['proof_sha256']==sha(files['PROOF.json']),'LIVE_PROOF_PUBLIC_JOIN')
    closing_now=time.time() if now is None else now
    need(request['created_utc_epoch']<=closing_now<request['expires_utc_epoch'],'LIVE_REQUEST_EXPIRED_DURING_VALIDATION')
    result.update(request_sha256=sha(files['REQUEST.json']),proof_sha256=sha(files['PROOF.json']),
        expires_utc_epoch=request['expires_utc_epoch'],seconds_remaining=request['expires_utc_epoch']-closing_now,
        private_observations=proof['private_observations'],raw_receive_record=probe['result']['receive_record'],
        live_log_join='NOT_APPLICABLE_WORKFLOW_DOES_NOT_EMIT_NINE_FILE_PREVIEW',
        outstanding_actual_assessment=['Actual host/native applicability and currentness records','Actual source/full raw and proof relations',
            'Actual job still live and enough fixed time remains','Genuine independent review then separate root consumption',
            'Later closing same-private-census/source/runtime/currentness and terminal artifact/log receipt'])
    return result

def match_terminal_log(files,raw):
    need(set(files)==set(NAMES) and type(raw) is bytes and len(raw)<=16*1024**2,'TERMINAL_LOG_INPUT_BOUND')
    _,_,_,modules,_,_=verified();utility=modules['host_utility.py'];expected=utility.transport_lines(files)
    found={};rows=[];encoded=[]
    for number,line in enumerate(raw.decode('utf-8-sig').splitlines(),1):
        match=re.fullmatch(r'(\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d\.\d+Z) (DG16_LINUX_HOST_JSON .*)',line)
        if not match:continue
        envelope=strict(match.group(2)[len(utility.PREFIX):]);name=envelope.get('name')
        need(set(envelope)=={'name','bytes','sha256','utf8_json'} and name in NAMES and name not in found,'TERMINAL_LOG_POPULATION')
        value=envelope['utf8_json'].encode();need(value==files[name] and desc(value)=={k:envelope[k] for k in ('bytes','sha256')},'TERMINAL_ARTIFACT_LOG_MISMATCH')
        canonical=utility.PREFIX+json.dumps(envelope,ensure_ascii=True,separators=(',',':'))
        need(match.group(2)==canonical and canonical in expected,'TERMINAL_ENVELOPE_ENCODING')
        found[name]=value;encoded.append(len(canonical.encode())+2);rows.append({'name':name,'log_line':number,'timestamp':match.group(1),**desc(value)})
    need(set(found)==set(NAMES) and max(encoded)<=262144 and sum(encoded)<=1048576,'TERMINAL_COMPLETE_LOG_REQUIRED')
    return {'schema':'dg16.terminal-artifact-log-byte-join.v1','authority':'NONE','log':desc(raw),'members':rows,
            'all_seven_exact':True,'encoded_bytes_including_CRLF':sum(encoded),'currentness_or_award':False}

def diagnostic_request(files,result):
    # Public validation runs in this fenced process. Only this data object
    # crosses into a separately admitted private decrypt process later.
    need(result['kind']=='terminal' and type(result['terminal_log_join']) is dict
      and result['terminal_log_join'].get('all_seven_exact') is True,'PRIVATE_REQUEST_REQUIRES_COMPLETE_PUBLIC_LOG_JOIN')
    b,_,_,modules,_,_=verified();docs={name:strict(files[name]) for name in NAMES}
    failure=docs['FAILURE.json'];need(failure['present'] is True,'PRIVATE_REQUEST_REQUIRES_FAILURE')
    ctx={k:docs['RESULT.json'][k] for k in ('repository','branch','run_id','run_attempt','workflow_commit')}
    ctx.update(source_commit=b['source_commit'],source_tree=b['source_tree'],
      workflow_path='.github/workflows/dg16-r5-full-g2.yml',job_name='full-registry-raw-pair')
    parent,u=modules['run.py'],modules['host_utility.py']
    protected=parent.load_protected(u).validate_public(docs['PROBE.json'],failure,ctx,u)
    need(protected['retention'] is not None and protected['retention']['status']=='ENCRYPTED_LOCAL_NOT_PROVIDER_RECEIVED',
      'PRIVATE_REQUEST_ENCRYPTED_COPY_NOT_READY')
    value=dict(schema='dg16.protected-full-private-diagnostic-request.v1',authority='NONE',context=ctx,
      public_receiver_binding_sha256=BINDING_SHA,public_archive=result['metadata']['archive'],
      public_receiving=desc(encode(result)),terminal_log_join=result['terminal_log_join'],
      failure_projection=failure['capture_observation'],protected_receipt=failure['protected_streams'],
      protected_capability=docs['PROBE.json']['protected_capability'],private_key_or_body_present=False,original_acceptance=False)
    need(len(encode(value))<=65536,'PRIVATE_REQUEST_BOUND');return value

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--archive',type=Path,required=True);parser.add_argument('--kind',choices=['live','terminal'],required=True)
    parser.add_argument('--run-id',required=True);parser.add_argument('--workflow-commit',required=True);parser.add_argument('--metadata',type=Path,required=True)
    parser.add_argument('--terminal-log',type=Path);parser.add_argument('--prepared',type=Path);parser.add_argument('--private-diagnostic-request',type=Path);args=parser.parse_args()
    raw=acquire(args.archive,400000);files=decode_zip(raw,args.kind)
    metadata=strict(acquire(args.metadata,262144));result=inspect(files,args.kind,run_id=args.run_id,workflow_commit=args.workflow_commit,metadata=metadata,archive=desc(raw))
    if args.terminal_log:
        need(args.kind=='terminal','NO_LIVE_LOG_SUBSTITUTION');result['terminal_log_join']=match_terminal_log(files,acquire(args.terminal_log,16*1024**2))
    if args.prepared:
        target=args.prepared.absolute();need(target.parent.resolve(strict=True)==target.parent and
            target.is_relative_to(RECEIVER_OUT) and not os.path.lexists(target),'PREPARED_OUTPUT_SCOPE')
        target.mkdir(mode=0o700)
        for name,body in files.items():
            path=target/name;path.parent.mkdir(mode=0o700,exist_ok=True);path.write_bytes(body)
    if args.private_diagnostic_request:
        target=args.private_diagnostic_request.absolute()
        need(target.name=='PRIVATE_DIAGNOSTIC_REQUEST.json' and target.parent.resolve(strict=True)==target.parent
          and target.is_relative_to(RECEIVER_OUT) and not os.path.lexists(target),'PRIVATE_REQUEST_OUTPUT_SCOPE')
        body=encode(diagnostic_request(files,result))
        with os.fdopen(os.open(target,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,0o600),'wb') as stream:
            stream.write(body);stream.flush();os.fsync(stream.fileno())
        need(acquire(target,65536)==body,'PRIVATE_REQUEST_READBACK')
    print(encode(result).decode(),end='')
if __name__=='__main__':main()
