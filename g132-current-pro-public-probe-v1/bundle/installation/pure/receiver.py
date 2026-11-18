# Exact bounded source projection; source module is never imported.
CORE = 'tree/qualification/dg16-r5-g1-hosted-episode/'

MAX_RESULT = 4 * 1024**2

MAX_JOURNAL = 8 * 1024**2

PHASES = {
 'tools': ('dg16-core-host-tools-{run}-a1', ('HOST_TOOL_OBSERVATION.json',),131072,65536),
 'recipient': ('dg16-core-private-recipient-{run}-a1', ('REQUEST.json','RECIPIENT.pem'),65536,16384),
 'g3_initial': ('dg16-g1-root-request-{run}-1', ('ROOT_REQUEST.json','SCOPE_RECEIVING.json','G1_RECEIVING.json','ARTIFACT_MANIFEST.json'),65536,40960),
 'g3_final': ('dg16-g1-original-request-{run}-1', ('FINAL_REQUEST.json','INDEPENDENT_PROOF_RECEIPT.json','ARTIFACT_MANIFEST.json'),32768,24576),
 'terminal': ('dg16-g1-hosted-{run}-1', ('RESULT.json','HOST.json','SOURCE.json','OPERATION.json','G3.json','NSS.json','CLEANUP.json','FAILURE.json','ARTIFACT_MANIFEST.json'),262144,163840),
 'failure': ('dg16-g1-retention-failure-{run}-1', ('RETENTION_FAILURE.json','ARTIFACT_MANIFEST.json'),65536,32768),
}

AUTH = 'ACTUAL_ROOT_TOOL_HISTORY_AND_PROVIDER_AUTHENTICATION_REQUIRED'

class Refusal(ValueError): pass

def need(ok, code):
    if not ok: raise Refusal(code)

def sha(raw): return hashlib.sha256(raw).hexdigest()

def desc(raw): return dict(bytes=len(raw),sha256=sha(raw))

def encode(v): return (json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=True,allow_nan=False)+'\n').encode()

def parse(raw, maximum=MAX_RESULT):
    need(type(raw) is bytes and 0 < len(raw) <= maximum,'JSON_BOUND')
    def pairs(rows):
        out={}
        for k,v in rows:
            need(k not in out,'DUPLICATE_JSON_KEY');out[k]=v
        return out
    return json.loads(raw,object_pairs_hook=pairs,parse_constant=lambda _:(_ for _ in ()).throw(Refusal('NONFINITE_JSON')))

def integer(v,low=0,high=10**20):
    need(type(v) is int and low <= v <= high,'INTEGER_BOUND');return v

_ARTIFACT_CAUSAL_ROUTES = {
    'tools': ('tools', ('Observe host tools', 'Retain actual host tool observation'),
              'Receive separate actual root tool adoption'),
    'recipient': ('recipient', ('Create fresh recipient request', 'Retain fresh recipient request'),
                  'Receive authenticated private inputs after actual root sender/control'),
    'g3_initial': ('root-request', ('Core g3-receive', 'Export validated root-request',
                                   'Retain first actual G3 root request'), 'Core g3-consume'),
    'g3_final': ('final-request', ('Core g3-consume', 'Export validated final-request',
                                  'Retain second original receiving request'), 'Core g3-decide'),
}

def local_artifact_chronology(snapshot, context, phase, issued, now, unix_ms, workflow_body,
                              workflow_sha256, representation):
    artifact = snapshot['artifact']
    displayed = artifact.get('created_at')
    created = unix_ms(displayed)
    if issued <= created <= now:
        return True
    route = _ARTIFACT_CAUSAL_ROUTES.get(phase)
    if (route is None or type(displayed) is not str
            or re.fullmatch(r'[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z', displayed) is None
            or not created < issued <= now or issued - created >= 1000):
        return False
    directory, names, hold = route
    # The original consumers still bind the exact archive, request, context,
    # workflow and provider records. Verify the pinned workflow before using
    # its ordering as the alternative to the missing fractional precision.
    try:
        raw = workflow_body(snapshot['workflow'], context, workflow_sha256, representation=representation)
        workflow = parse(raw)
        workflow_steps = workflow['jobs'][context['job_name']]['steps']
        if not isinstance(workflow_steps, list) or len(workflow_steps) > 100:
            return False
        selected = []
        for name in (*names, hold):
            positions = [i for i, row in enumerate(workflow_steps) if row.get('name') == name]
            if len(positions) != 1:
                return False
            selected.append(positions[0])
        if selected != list(range(selected[0], selected[0] + len(selected))):
            return False
        upload = workflow_steps[selected[-2]]
        artifact_template, expected_files, _, _ = PHASES[phase]
        prefix = '${{ runner.temp }}/dg16-g1-public-${{ github.run_id }}-a1/' + directory + '/'
        with_args = upload['with']
        if (upload.get('uses') != 'actions/upload-artifact@ea165f8d65b6e75b540449e92b4886f43607fa02'
                or with_args.get('name') != artifact_template.replace('{run}', '${{ github.run_id }}')
                or with_args.get('if-no-files-found') != 'error'
                or with_args.get('path', '').splitlines() != [prefix + n for n in expected_files]):
            return False
        if any(not workflow_steps[i].get('run') or 'if' in workflow_steps[i] for i in selected[:-2]):
            return False
        jobs = snapshot['jobs']['jobs']
        if not isinstance(jobs, list) or len(jobs) != 1:
            return False
        job = jobs[0]
        if job.get('status') != 'in_progress' or job.get('name') != context['job_name']:
            return False
        rows = job['steps']
        if not isinstance(rows, list) or len(rows) > 100:
            return False
        matched = []
        for name in (*names, hold):
            matches = [row for row in rows if row.get('name') == name]
            if len(matches) != 1 or type(matches[0].get('number')) is not int:
                return False
            matched.append(matches[0])
        numbers = [row['number'] for row in matched]
        if numbers != list(range(numbers[0], numbers[0] + len(numbers))):
            return False
        spans = []
        for row in matched[:-1]:
            if row.get('status') != 'completed' or row.get('conclusion') != 'success':
                return False
            start, end = unix_ms(row['started_at']), unix_ms(row['completed_at'])
            if not start <= end <= now or spans and spans[-1][1] > start:
                return False
            spans.append((start, end))
        if not (spans[0][0] <= issued < spans[0][1] + 1000
                and spans[-1][0] <= created <= spans[-1][1]):
            return False
        waiting = matched[-1]
        if waiting.get('status') == 'pending':
            return waiting.get('started_at') is None and waiting.get('completed_at') is None
        return (waiting.get('status') == 'in_progress' and waiting.get('completed_at') is None
                and spans[-1][1] <= unix_ms(waiting['started_at']) <= now)
    except (AttributeError, KeyError, TypeError, ValueError, OverflowError):
        return False

def artifact_name(phase,ctx):
    need(phase in PHASES,'FIXED_PHASE');return PHASES[phase][0].format(run=ctx['run_id'])

def candidate(s,phase,ctx,raw):
    _,v=s.B.unwrap_tool_result(raw,s.endpoint(ctx,1,'artifacts'),kind='artifacts')
    need(type(v.get('artifacts')) is list and type(v.get('total_count')) is int
      and v['total_count']==len(v['artifacts'])<=100,'ARTIFACT_LIST_COMPLETE')
    rows=[r for r in v['artifacts'] if r.get('name')==artifact_name(phase,ctx)]
    need(len(rows)==1,'FIXED_ARTIFACT_NOT_UNIQUE_OR_NOT_PRESENT')
    integer(rows[0].get('id'),1);return rows[0]

def unzip(archive,phase):
    _,names,bound,total=PHASES[phase];need(type(archive) is bytes and 0<len(archive)<=bound,'ZIP_BOUND')
    out={}
    with zipfile.ZipFile(io.BytesIO(archive)) as z:
        rows=z.infolist();need(len(rows)==len(names) and {r.filename for r in rows}==set(names),'ZIP_EXACT_POPULATION')
        for r in rows:
            mode=(r.external_attr>>16)&0xffff
            need(not r.is_dir() and not (r.flag_bits&1) and r.compress_type in (zipfile.ZIP_STORED,zipfile.ZIP_DEFLATED)
              and stat.S_IFMT(mode) in (0,stat.S_IFREG) and 0<r.file_size<=65536,'ZIP_MEMBER_BOUND_OR_TYPE')
            with z.open(r) as f:b=f.read(r.file_size+1)
            need(len(b)==r.file_size,'ZIP_MEMBER_SIZE');out[r.filename]=b
    need(sum(map(len,out.values()))<=total,'ZIP_PUBLIC_AGGREGATE');return out

def check_manifest(files,schema):
    expected=dict(schema=schema,members=[dict(name=n,**desc(b)) for n,b in sorted(files.items()) if n!='ARTIFACT_MANIFEST.json'])
    need(files['ARTIFACT_MANIFEST.json']==encode(expected),'EXACT_ARTIFACT_MANIFEST')

def download_note(raw,artifact_id,file_name):
    """Consume the actual complete download tool result IN MEMORY only.

    The complete original descriptor is retained. Every URL-bearing string is
    redacted in the otherwise complete structure; no signed URL is written.
    This credential exception is explicit, never described as raw retention.
    """
    integer(artifact_id,1);need(type(file_name) is str and re.fullmatch('[A-Za-z0-9._-]{1,256}',file_name),'DOWNLOAD_SAFE_FIXED_FILENAME')
    v=parse(raw);need(type(v) is dict and set(v)<= {'content','structuredContent','isError','_meta'} and v.get('isError') is False,'DOWNLOAD_TOOL_RESULT')
    meta=v.get('_meta',{});need(type(meta) is dict and set(meta)<={'truncated','isTruncated','partial','hasMore'} and all(type(x) is bool and not x for x in meta.values()),'DOWNLOAD_TOOL_TRUNCATED_OR_METADATA_KEYS')
    content=v.get('content');need(type(content) is list and len(content)<=32 and all(type(x) is dict and set(x)=={'type','text'} and x['type']=='text' and type(x['text']) is str for x in content),'DOWNLOAD_CONTENT_FIELDS')
    sc=v.get('structuredContent');need(type(sc) is dict,'DOWNLOAD_STRUCTURED_RESULT')
    rows=[sc]+([sc['structuredContent']] if 'structuredContent' in sc else [])
    ids=[]
    for level,r in enumerate(rows):
        need(level==0 or 'structuredContent' not in r,'DOWNLOAD_UNEXPECTED_NESTING')
        need(type(r) is dict and set(r)<={'artifact_id','file_name','mime_type','file_uri','file_id','download_url','structuredContent'} and r.get('artifact_id')==artifact_id and type(r.get('artifact_id')) is int
          and r.get('file_name')==file_name and r.get('mime_type')=='application/zip','DOWNLOAD_ARTIFACT_JOIN')
        uri=r.get('file_uri');need(type(uri) is dict and set(uri)<={'file_id','file_name','mime_type','download_url'},'DOWNLOAD_FILE_REFERENCE')
        for obj in (r,uri):
            if 'download_url' in obj:need(type(obj['download_url']) is str,'DOWNLOAD_URL_FIELD_TYPE')
        need(uri.get('file_name')==file_name and uri.get('mime_type')=='application/zip'
          and type(uri.get('file_id')) is str and re.fullmatch('file_[0-9a-f]{32}',uri['file_id']),'DOWNLOAD_FILE_REFERENCE_JOIN')
        ids.append(uri['file_id'])
        if 'file_id' in r:need(r['file_id']==uri['file_id'],'DOWNLOAD_DUPLICATE_FILE_ID')
    need(len(set(ids))==1,'DOWNLOAD_NESTED_CHANGED')
    def redact(x):
        if type(x) is dict:
            need(all(type(k) is str and not re.search(r'(?i)(https?://|sig=|token=|signature=)',k) for k in x),'DOWNLOAD_CREDENTIAL_BEARING_KEY')
            return {k:('[EPHEMERAL_URL_OR_CREDENTIAL_STRING_OMITTED]' if k=='download_url' else '[UNSTRUCTURED_TOOL_COMPLETION_TEXT_OMITTED]' if k=='text' else redact(y)) for k,y in x.items()}
        if type(x) is list:return [redact(y) for y in x]
        if type(x) is str and re.search(r'(?i)(https?://|sig=|token=|signature=)',x):return '[EPHEMERAL_URL_OR_CREDENTIAL_STRING_OMITTED]'
        return x
    clean=redact(v)
    return dict(schema='dg16.root-artifact-download-result.v1',authority='NONE',artifact_id=artifact_id,file_name=file_name,file_id=ids[0],
      actual_tool_result=desc(raw),redacted_complete_result=clean,signed_url_retained=False,authentication_boundary=AUTH)

def check_download(note,artifact_id,file_name):
    need(type(note) is dict and set(note)=={'schema','authority','artifact_id','file_name','file_id','actual_tool_result','redacted_complete_result','signed_url_retained','authentication_boundary'},'DOWNLOAD_NOTE_FIELDS')
    need(note['schema']=='dg16.root-artifact-download-result.v1' and note['authority']=='NONE'
      and note['artifact_id']==artifact_id and type(note['artifact_id']) is int and note['file_name']==file_name
      and note['signed_url_retained'] is False and note['authentication_boundary']==AUTH,'DOWNLOAD_NOTE_JOIN')
    d=note['actual_tool_result'];need(type(d) is dict and set(d)=={'bytes','sha256'} and type(d['bytes']) is int and 0<d['bytes']<=MAX_RESULT
      and type(d['sha256']) is str and re.fullmatch('[0-9a-f]{64}',d['sha256']),'DOWNLOAD_ORIGINAL_DESCRIPTOR')
    need(not re.search(rb'(?i)(https?://|sig=|token=|signature=)',encode(note)),'EPHEMERAL_URL_PERSISTENCE_REFUSED')
    need(download_note(encode(note['redacted_complete_result']),artifact_id,file_name)['file_id']==note['file_id'],'DOWNLOAD_NOTE_COMPLETE_JOIN')

def execution_join(s,snapshot,ctx,now,statuses,issued=None):
    for key in ('run','attempt'):
        r=snapshot[key]
        need(type(r.get('id')) is int and r['id']==int(ctx['run_id']) and type(r.get('run_attempt')) is int and r['run_attempt']==1
          and r.get('event')=='push' and r.get('status') in statuses and r.get('head_branch')==ctx['branch']
          and r.get('head_sha')==ctx['workflow_commit'] and r.get('path')==ctx['workflow_path']
          and r.get('repository',{}).get('full_name')==s.P.REPOSITORY and r.get('head_repository',{}).get('full_name')==s.P.REPOSITORY,'PROVIDER_RUN_JOIN')
        start=s.V.unix_ms(r.get('run_started_at'));need(start<=now and (issued is None or start<=issued),'PROVIDER_RUN_CHRONOLOGY')
    repo=integer(snapshot['run']['repository'].get('id'),1)
    for r in (snapshot['run'],snapshot['attempt']):
        need(type(r['repository'].get('id')) is int and type(r['head_repository'].get('id')) is int and r['repository']['id']==repo and r['head_repository']['id']==repo,'PROVIDER_REPOSITORY_JOIN')
    jobs=snapshot['jobs'];need(type(jobs.get('total_count')) is int and jobs['total_count']==1 and type(jobs.get('jobs')) is list and len(jobs['jobs'])==1,'PROVIDER_SINGLE_JOB')
    job=jobs['jobs'][0];integer(job.get('id'),1)
    need(type(job.get('run_id')) is int and job['run_id']==int(ctx['run_id']) and type(job.get('run_attempt')) is int and job['run_attempt']==1
      and job.get('head_sha')==ctx['workflow_commit'] and job.get('name')==ctx['job_name'] and job.get('status') in statuses,'PROVIDER_JOB_JOIN')
    start=s.V.unix_ms(job.get('started_at'));need(start<=now and (issued is None or start<=issued),'PROVIDER_JOB_CHRONOLOGY')
    s.V.workflow_body(snapshot['workflow'],ctx,s.binding['workflow_sha256'],representation=s.V.SUPPORTED_TOOL_WORKFLOW)
    return dict(repository_id=repo,job_id=job['id'],run_status=snapshot['run']['status'],run_conclusion=snapshot['run'].get('conclusion'),job_status=job['status'],job_conclusion=job.get('conclusion')),start

def provider_join(s,snapshot,archive,ctx,phase,now,issued=None):
    need(set(snapshot)==set(s.B.KINDS) and len(encode(snapshot))<=s.P.MAX_METADATA,'PROVIDER_SNAPSHOT_BOUND')
    joins,start=execution_join(s,snapshot,ctx,now,('in_progress','completed') if phase in ('terminal','failure') else ('in_progress',),issued)
    repo=joins['repository_id']
    a=snapshot['artifact'];integer(a.get('id'),1);rel=a.get('workflow_run',{})
    need(a.get('name')==artifact_name(phase,ctx) and a.get('expired') is False and type(a.get('size_in_bytes')) is int
      and a['size_in_bytes']==len(archive) and a.get('digest')=='sha256:'+sha(archive),'PROVIDER_ARCHIVE_DIGEST')
    need(type(rel.get('id')) is int and rel['id']==int(ctx['run_id']) and rel.get('head_sha')==ctx['workflow_commit'] and rel.get('head_branch')==ctx['branch']
      and type(rel.get('repository_id')) is int and rel['repository_id']==repo and type(rel.get('head_repository_id')) is int and rel['head_repository_id']==repo,'PROVIDER_ARTIFACT_RUN_JOIN')
    created=s.V.unix_ms(a.get('created_at'));need(start<=created<=now and (issued is None or issued<=created or local_artifact_chronology(snapshot,ctx,phase,issued,now,s.V.unix_ms,s.V.workflow_body,s.binding['workflow_sha256'],s.V.SUPPORTED_TOOL_WORKFLOW)),'PROVIDER_ARTIFACT_CHRONOLOGY')
    ls=snapshot['artifacts'];need(type(ls.get('total_count')) is int and type(ls.get('artifacts')) is list and ls['total_count']==len(ls['artifacts'])<=100,'PROVIDER_LIST_COMPLETE')
    need([r for r in ls['artifacts'] if r.get('name')==a['name']]==[a],'PROVIDER_EXACT_ARTIFACT_LIST_JOIN')
    s.V.workflow_body(snapshot['workflow'],ctx,s.binding['workflow_sha256'],representation=s.V.SUPPORTED_TOOL_WORKFLOW)
    return dict(joins,artifact_id=a['id'])

def receive(s,phase,ctx,results,archive,note,now_ms,previous=None,actual_root_raw=None):
    s.context(ctx);integer(now_ms,1,10**16);need(phase in PHASES and set(results)==set(s.B.KINDS),'RECEIVE_FIXED_POPULATION')
    need(sum(map(len,results.values()))+len(archive)+len(encode(note))<=MAX_JOURNAL,'RECEIVE_AGGREGATE_BOUND')
    a=candidate(s,phase,ctx,results['artifacts']);file_name=artifact_name(phase,ctx)+'.zip';check_download(note,a['id'],file_name)
    snapshot={}
    for kind in s.B.KINDS:
        _,snapshot[kind]=s.B.unwrap_tool_result(results[kind],s.endpoint(ctx,a['id'],kind),kind=kind,context=ctx,workflow_sha256=s.binding['workflow_sha256'],artifact_id=a['id'])
    files=unzip(archive,phase);request=None;issued=None;detail={};linked=None
    if phase=='tools':
        detail=s.H.check_observation_artifact(archive,snapshot,ctx,s.binding,s.anchor,now_ms,workflow_representation=s.V.SUPPORTED_TOOL_WORKFLOW)
        request=parse(files['HOST_TOOL_OBSERVATION.json']);issued=request['issued_unix_ms']
    elif phase=='recipient':
        checked=s.V.check_snapshot(snapshot,archive,ctx,s.index,s.binding['workflow_sha256'],now_ms,workflow_representation=s.V.SUPPORTED_TOOL_WORKFLOW)
        detail={k:v for k,v in checked.items() if k not in ('request_raw','certificate')};request=checked['request'];issued=request['issued_unix_ms']
    elif phase=='g3_initial':
        check_manifest(files,'dg16.g1-root-request-artifacts.v1');request=s.G.validate_public_request(files['ROOT_REQUEST.json']);scope=s.G.validate_public_scope(files['SCOPE_RECEIVING.json'])
        need(request['scope_return_sha256']==sha(files['SCOPE_RECEIVING.json']) and scope['run_id']==ctx['run_id'] and scope['attempt']==ctx['run_attempt']
          and all(scope[k]==request[k] for k in ('graph_sha256','dispatch_sha256','complete_input_key','source_commit','source_tree','original_scope_sha256')),'G3_SCOPE_BODY_JOIN')
        _,_,g1=s.I.validate_first(files['ROOT_REQUEST.json'],files['SCOPE_RECEIVING.json'],files['G1_RECEIVING.json'],s.proof_pins,s.scope_basis,original_scope_raw=s.scope_basis_raw)
        issued=request['issued_unix_ms'];detail=dict(scope=scope,g1=g1,request=request,request_window_open=issued<=now_ms<request['expires_unix_ms'])
    elif phase=='g3_final':
        check_manifest(files,'dg16.g1-final-request-artifacts.v1');request=s.G.validate_public_final_request(files['FINAL_REQUEST.json'],retained_bodies=s.retained_m4_bodies());issued=request['issued_unix_ms']
        need(type(previous) is dict and previous.get('phase')=='g3_initial' and previous.get('context')==ctx,'INITIAL_RECEIVING_REQUIRED')
        q=s.G.validate_public_request(previous['files']['ROOT_REQUEST.json']);s.G.validate_public_scope(previous['files']['SCOPE_RECEIVING.json'])
        need(request['initial_request_sha256']==sha(previous['files']['ROOT_REQUEST.json']) and request['initial_graph_sha256']==q['graph_sha256']
          and request['proofs']['scope_receiving']==sha(previous['files']['SCOPE_RECEIVING.json']) and request['g1_complete_input_key']==q['complete_input_key']
          and request['shared_window_started_unix_ms']==q['issued_unix_ms'] and request['expires_unix_ms']==q['shared_expires_unix_ms']
          and request['shared_window_seconds']==q['shared_window_seconds'] and sum(map(len,previous['files'].values()))+sum(map(len,files.values()))<=65536,'G3_BOTH_HOLDS_EXACT_JOIN')
        s.I.validate_first(previous['files']['ROOT_REQUEST.json'],previous['files']['SCOPE_RECEIVING.json'],previous['files']['G1_RECEIVING.json'],s.proof_pins,s.scope_basis,original_scope_raw=s.scope_basis_raw)
        need(type(actual_root_raw) is bytes and 0<len(actual_root_raw)<=8192,'ACTUAL_ROOT_FIRST_DECISION_BYTES_REQUIRED')
        independent=s.I.validate_receipt(files['INDEPENDENT_PROOF_RECEIPT.json'],previous['files']['ROOT_REQUEST.json'],files['FINAL_REQUEST.json'],actual_root_raw,s.proof_pins,retained_bodies=s.retained_m4_bodies())
        linked=desc(encode(previous['receipt']));detail=dict(request=request,independent_receipt=independent,actual_first_root_decision=desc(actual_root_raw),independent_semantics='AUTHENTICATED_RECEIPT_REQUIRES_ACTUAL_ROOT_AND_DISTINCT_REVIEWER_APPLICABILITY',request_window_open=issued<=now_ms<request['expires_unix_ms'])
    elif phase=='terminal':
        s.R.validate_transport(files)
        values={n:parse(b,65536) for n,b in files.items()};detail=dict(public_outcomes=values,transport_validation='EXACT_EXISTING_TRANSPORT_VALIDATOR',semantic_original_acceptance='ROOT_REVIEW_OF_COMPLETE_RETAINED_BODIES_REQUIRED')
        for v in values.values():
            if type(v) is dict:
                if 'run_id' in v:need(v['run_id']==ctx['run_id'],'TERMINAL_RUN_JOIN')
                if 'workflow_commit' in v:need(v['workflow_commit']==ctx['workflow_commit'],'TERMINAL_COMMIT_JOIN')
                if 'source_commit' in v:need(v['source_commit']==s.P.SOURCE_COMMIT,'TERMINAL_SOURCE_JOIN')
                if 'source_tree' in v:need(v['source_tree']==s.P.SOURCE_TREE,'TERMINAL_TREE_JOIN')
    else:
        s.R.validate_failure_files(files);v=parse(files['RETENTION_FAILURE.json']);need(v['run_id']==ctx['run_id'] and v['workflow_commit']==ctx['workflow_commit'],'FAILURE_CONTEXT_JOIN');detail=dict(public_outcomes=v)
    if request is not None:
        if phase.startswith('g3_'):need(request['run_id']==ctx['run_id'] and request['attempt']==ctx['run_attempt'],'G3_REQUEST_RUN_JOIN')
        need(issued<=now_ms,'REQUEST_NOT_YET_ISSUED')
    joins=provider_join(s,snapshot,archive,ctx,phase,now_ms,issued)
    receipt=dict(schema='dg16.final-root-artifact-receiving.v1',authority='NONE',phase=phase,context=ctx,source_phase=s.sources['phase']['sha256'],
      observed_unix_ms=now_ms,archive=desc(archive),files={n:desc(b) for n,b in sorted(files.items())},actual_tool_results={k:desc(v) for k,v in sorted(results.items())},
      download_result_original=note['actual_tool_result'],download_file_id=note['file_id'],provider=joins,artifact_metadata=s.B.artifact_provenance(results['artifact'],s.endpoint(ctx,a['id'],'artifact'),ctx,a['id']),details=detail,initial_receiving=linked,
      authentication_boundary=AUTH,automatic_retry=False,original_awards=[],effect_grant=False)
    return dict(phase=phase,context=ctx,files=files,receipt=receipt)

def requirements(s,received):
    phase=received['phase'];f=received['files'];ctx=received['context'];pending=[]
    if phase=='tools':
        q=parse(f['HOST_TOOL_OBSERVATION.json']);fixed=dict(schema='dg16.same-host-fixed-tool-root-adoption.v2',issuer='R5_ROOT_GOVERNOR',successor='PRO-EXECUTOR-01, designated by owner',operation='ADOPT_FIXED_SAME_HOST_TOOL_BODIES',observation=desc(f['HOST_TOOL_OBSERVATION.json']),command_scope=['recipient','decrypt'],automatic_retry=False,crypto_capability_claim=False,core_or_native_effect_grant=False,original_awards=[])
        for k in ('context','source_commit','source_tree','carrier_binding_sha256','input_index_sha256','public_manifest_sha256','bootstrap_admission_sha256','nonce','host_identity','tools','host_profile'):fixed[k]=q[k]
        pending=['issued_unix_ms','expires_unix_ms'];path='HOST_TOOL_ADOPTION.json';branch=s.binding['host_tools']['control_branch'];parent=s.binding['host_tools']['control_parent']
    elif phase=='g3_initial':
        q=s.G.validate_public_request(f['ROOT_REQUEST.json']);fixed=dict(schema='dg16.g3-root-consumption-decision.v2',issuer='R5_ROOT_GOVERNOR',successor='PRO-EXECUTOR-01, designated by owner',action='CONSUME_COMPONENT_RETURNS_ONLY',request_sha256=sha(f['ROOT_REQUEST.json']),outputs={s.G.PAIR:q['g1_return_sha256'],s.G.SCOPE:q['scope_return_sha256']},consumed_nodes=s.G.SELECTED,owner_arrangement=s.G.OWNER_ARRANGEMENT,original_awards=0)
        for k in ('run_id','attempt','nonce','source_commit','source_tree','graph_sha256','dispatch_sha256','join_sha256','decision_before','decision_after','full_g2','expires_unix_ms'):fixed[k]=q[k]
        pending=['issued_unix_ms'];path=q['control_path'];branch=q['control_branch'];parent=None
    elif phase=='g3_final':
        q=s.G.validate_public_final_request(f['FINAL_REQUEST.json'],retained_bodies=s.retained_m4_bodies());fixed=dict(schema='dg16.g3-root-original-decision.v3',issuer='R5_ROOT_GOVERNOR',successor='PRO-EXECUTOR-01, designated by owner',action='RECEIVE_EXACT_ORIGINAL_IDS_AND_GATES',request_sha256=sha(f['FINAL_REQUEST.json']),whole_DG16_awarded=False,full_g2='NOT_DISPATCHED_OR_CONSUMED_IN_THIS_HOST',v041_admission='PENDING_NOT_GRANTED_BY_THIS_EPISODE',global_liveness='NOT_ESTABLISHED',retirement_or_transfer='NOT_PERFORMED')
        for k in ('run_id','attempt','nonce','source_commit','source_tree','final_graph_sha256','current_receipt_sha256','proofs','retained_m4','expires_unix_ms'):fixed[k]=q[k]
        pending=['issued_unix_ms','independent_review_sha256','source_applicability_review_sha256','original_rows','gate_decisions'];path=q['control_path'];branch=q['control_branch'];parent=None
    else:raise Refusal('ROOT_CONTROL_REQUIREMENTS_PHASE')
    return dict(schema='dg16.root-control-requirements.v1',authority='NONE',receiving=desc(encode(received['receipt'])),required_fixed_fields=fixed,root_supplied_fields=pending,path=path,branch=branch,required_parent=parent,root_body_issued=False,effect_grant=False,original_awards=[])

def sender_requirements(s,received,root_selection,actual_host_receiving):
    return current_sender_requirements(s,received,root_selection,actual_host_receiving)

def validate_control(s,received,raw,now_ms):
    phase=received['phase'];f=received['files'];integer(now_ms,1,10**16)
    if phase=='tools':return s.H.validate_adoption(raw,f['HOST_TOOL_OBSERVATION.json'],s.binding,now_ms)
    if phase=='g3_initial':
        q=s.G.validate_public_request(f['ROOT_REQUEST.json']);return s.G.validate_decision(raw,q,sha(f['ROOT_REQUEST.json']),now_ms)
    if phase=='g3_final':
        q=s.G.validate_public_final_request(f['FINAL_REQUEST.json'],retained_bodies=s.retained_m4_bodies());return s.G.validate_final_decision(raw,q,sha(f['FINAL_REQUEST.json']),now_ms,retained_bodies=s.retained_m4_bodies())
    raise Refusal('CONTROL_PHASE')
