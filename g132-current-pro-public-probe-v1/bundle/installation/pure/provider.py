# Exact bounded source projection; source module is never imported.
RAW_API_WORKFLOW='GITHUB_CONTENTS_RAW_API_V1'

SUPPORTED_TOOL_WORKFLOW='SUPPORTED_GITHUB_FETCH_DECODED_UTF8_V1'

def json_body(raw):
    def pairs(rows):
        value={}
        for key,item in rows:P.need(key not in value,'PROVIDER_DUPLICATE_KEY');value[key]=item
        return value
    try:return json.loads(raw,object_pairs_hook=pairs,
        parse_constant=lambda _: (_ for _ in ()).throw(ValueError('PROVIDER_NONFINITE_JSON')))
    except (UnicodeError,json.JSONDecodeError,RecursionError) as exc:raise ValueError('PROVIDER_JSON_REFUSED') from exc

def blob(value,maximum):
    P.need(type(value) is dict and value.get('encoding')=='base64'
      and type(value.get('content')) is str and len(value['content'])<=maximum*2+65536,'PROVIDER_BLOB_SHAPE')
    try:raw=base64.b64decode(value['content'].replace('\n',''),validate=True)
    except (ValueError,TypeError) as exc:raise ValueError('PROVIDER_BLOB_ENCODING') from exc
    P.need(type(value.get('size')) is int and len(raw)==value['size']<=maximum,'PROVIDER_BLOB_BOUND')
    git=hashlib.sha1(b'blob '+str(len(raw)).encode('ascii')+b'\0'+raw).hexdigest()
    P.need(value.get('sha')==git,'PROVIDER_GIT_BLOB_CHANGED');return raw

def workflow_endpoint(ctx):
    P.context(ctx)
    return 'https://api.github.com/repos/'+P.REPOSITORY+'/contents/'+ctx['workflow_path']+'?ref='+ctx['workflow_commit']

def workflow_body(value,ctx,expected_sha256,*,representation=RAW_API_WORKFLOW):
    """Exact body joins, never provider authentication or a transport fallback.

    The supported-tool form is explicitly derived evidence. Its tool-result
    descriptor joins the unchanged result retained by the root dispatcher;
    this pure function cannot attest that those bytes were actually acquired.
    """
    P.context(ctx);P.digest(expected_sha256)
    if representation==RAW_API_WORKFLOW:
        raw=blob(value,65536)
        P.need(value.get('type')=='file' and value.get('path')==ctx['workflow_path']
          and P.sha(raw)==expected_sha256,'PROVIDER_ACTUAL_WORKFLOW_BODY')
        return raw
    P.need(representation==SUPPORTED_TOOL_WORKFLOW,'PROVIDER_WORKFLOW_REPRESENTATION')
    P.exact(value,('schema','representation','authority','endpoint','repository','path','commit','body_text','body',
      'derived_git_blob_sha1','actual_tool_result','authentication_boundary'))
    P.need(value['schema']=='dg16.supported-tool-workflow-text.v1' and value['representation']==SUPPORTED_TOOL_WORKFLOW
      and value['authority']=='NONE' and value['authentication_boundary']=='ACTUAL_ROOT_TOOL_HISTORY_REQUIRED'
      and value['endpoint']==workflow_endpoint(ctx) and value['repository']==P.REPOSITORY
      and value['path']==ctx['workflow_path'] and value['commit']==ctx['workflow_commit'],
      'PROVIDER_SUPPORTED_WORKFLOW_CONTEXT')
    P.need(type(value['body_text']) is str,'PROVIDER_SUPPORTED_WORKFLOW_TEXT')
    try:raw=value['body_text'].encode('utf-8')
    except UnicodeError as exc:raise ValueError('PROVIDER_SUPPORTED_WORKFLOW_UTF8') from exc
    P.need(0<len(raw)<=65536,'PROVIDER_SUPPORTED_WORKFLOW_BOUND')
    for name,maximum in (('body',65536),('actual_tool_result',4*1024**2)):
        P.exact(value[name],('bytes','sha256'));P.integer(value[name]['bytes'],1,maximum);P.digest(value[name]['sha256'])
    git=hashlib.sha1(b'blob '+str(len(raw)).encode('ascii')+b'\0'+raw).hexdigest()
    P.need(value['body']==P.descriptor(raw) and P.sha(raw)==expected_sha256
      and value['derived_git_blob_sha1']==git,'PROVIDER_SUPPORTED_WORKFLOW_BODY')
    return raw

def supported_workflow(body,actual_tool_result,ctx,expected_sha256):
    """Called only after the broker checks the complete actual tool envelope.

    No GitHub API envelope, encoding, size, or provider-reported Git SHA is
    synthesized. The Git object ID here is explicitly computed from the body.
    """
    P.need(type(body) is bytes and type(actual_tool_result) is bytes,'PROVIDER_SUPPORTED_WORKFLOW_BYTES')
    value=dict(schema='dg16.supported-tool-workflow-text.v1',representation=SUPPORTED_TOOL_WORKFLOW,authority='NONE',
      endpoint=workflow_endpoint(ctx),repository=ctx['repository'],path=ctx['workflow_path'],commit=ctx['workflow_commit'],
      body_text=body.decode('utf-8'),body=P.descriptor(body),
      derived_git_blob_sha1=hashlib.sha1(b'blob '+str(len(body)).encode('ascii')+b'\0'+body).hexdigest(),
      actual_tool_result=P.descriptor(actual_tool_result),authentication_boundary='ACTUAL_ROOT_TOOL_HISTORY_REQUIRED')
    workflow_body(value,ctx,expected_sha256,representation=SUPPORTED_TOOL_WORKFLOW)
    return value

def artifact_files(raw):
    P.need(type(raw) is bytes and 0<len(raw)<=P.MAX_ARTIFACT,'REQUEST_ARTIFACT_BOUND')
    try:
        with zipfile.ZipFile(io.BytesIO(raw)) as z:
            infos=z.infolist()
            P.need(len(infos)==2 and {i.filename for i in infos}=={'REQUEST.json','RECIPIENT.pem'},'REQUEST_ARTIFACT_POPULATION')
            result={}
            for row in infos:
                maximum=P.MAX_REQUEST if row.filename=='REQUEST.json' else P.MAX_CERTIFICATE
                mode=(row.external_attr>>16)&0o170000
                P.need(not row.is_dir() and row.file_size<=maximum and row.file_size>0
                  and mode in (0,0o100000) and not row.flag_bits&1
                  and row.compress_type in (zipfile.ZIP_STORED,zipfile.ZIP_DEFLATED),'REQUEST_ARTIFACT_MEMBER')
                value=z.read(row) # Exact known member; CRC checked, no extraction.
                P.need(len(value)==row.file_size,'REQUEST_ARTIFACT_BODY');result[row.filename]=value
            return result
    except (zipfile.BadZipFile,RuntimeError,OSError) as exc:raise ValueError('REQUEST_ARTIFACT_CRC_OR_FORMAT') from exc

def unix_ms(value):
    P.need(type(value) is str and len(value)<=40,'PROVIDER_TIME')
    try:
        parsed=datetime.datetime.fromisoformat(value.replace('Z','+00:00'))
        P.need(parsed.tzinfo is not None,'PROVIDER_TIME')
        return int(parsed.timestamp()*1000)
    except (ValueError,OverflowError) as exc:raise ValueError('PROVIDER_TIME') from exc

def check_snapshot(snapshot,archive,ctx,index,workflow_sha256,now_ms,*,workflow_representation=RAW_API_WORKFLOW):
    """Mechanical joins only. This pure function does not confer provenance."""
    P.context(ctx)
    P.exact(snapshot,('run','attempt','jobs','artifact','artifacts','workflow'))
    P.need(len(P.encode(snapshot))<=P.MAX_METADATA,'PROVIDER_SNAPSHOT_AGGREGATE_BOUND')
    files=artifact_files(archive)
    q=P.validate_request(files['REQUEST.json'],files['RECIPIENT.pem'],ctx,index,now_ms)
    for name in ('run','attempt'):
        row=snapshot[name]
        P.need(row.get('id')==int(ctx['run_id']) and row.get('run_attempt')==1
          and row.get('event')=='push' and row.get('status')=='in_progress'
          and row.get('head_branch')==ctx['branch'] and row.get('head_sha')==ctx['workflow_commit']
          and row.get('path')==ctx['workflow_path'] and row.get('repository',{}).get('full_name')==P.REPOSITORY
          and row.get('head_repository',{}).get('full_name')==P.REPOSITORY,'PROVIDER_RUN_BINDING')
        P.need(unix_ms(row.get('run_started_at'))<=q['issued_unix_ms'],'PROVIDER_RUN_CHRONOLOGY')
    repo_id=snapshot['run']['repository'].get('id')
    P.integer(repo_id,1,10**20)
    P.need(snapshot['run']['head_repository'].get('id')==repo_id
      and snapshot['attempt']['repository'].get('id')==repo_id
      and snapshot['attempt']['head_repository'].get('id')==repo_id,'PROVIDER_REPOSITORY_ID')
    jobs=snapshot['jobs']
    P.need(jobs.get('total_count')==1 and type(jobs.get('jobs')) is list and len(jobs['jobs'])==1,'PROVIDER_SINGLE_JOB')
    job=jobs['jobs'][0]
    P.need(job.get('run_id')==int(ctx['run_id']) and job.get('run_attempt')==1
      and job.get('head_sha')==ctx['workflow_commit'] and job.get('name')==ctx['job_name']
      and job.get('status')=='in_progress' and unix_ms(job.get('started_at'))<=q['issued_unix_ms'],'PROVIDER_JOB_BINDING')
    P.integer(job.get('id'),1,10**20)
    artifact=snapshot['artifact'];related=artifact.get('workflow_run',{})
    P.need(artifact.get('name')=='dg16-core-private-recipient-'+ctx['run_id']+'-a1'
      and artifact.get('expired') is False and artifact.get('size_in_bytes')==len(archive)
      and artifact.get('digest')=='sha256:'+P.sha(archive),'PROVIDER_ARTIFACT_DIGEST')
    P.need(related.get('id')==int(ctx['run_id']) and related.get('head_sha')==ctx['workflow_commit']
      and related.get('head_branch')==ctx['branch'] and related.get('repository_id')==repo_id
      and related.get('head_repository_id')==repo_id,'PROVIDER_ARTIFACT_RUN')
    P.need(local_artifact_chronology(snapshot,ctx,'recipient',q['issued_unix_ms'],now_ms,unix_ms,workflow_body,workflow_sha256,workflow_representation),'PROVIDER_ARTIFACT_CHRONOLOGY')
    listing=snapshot['artifacts']
    P.need(type(listing.get('artifacts')) is list and type(listing.get('total_count')) is int
      and listing['total_count']==len(listing['artifacts'])<=100,'PROVIDER_ARTIFACT_LIST_BOUND')
    candidates=[row for row in listing['artifacts'] if row.get('name')==artifact['name']]
    P.need(len(candidates)==1 and candidates[0]==artifact,'PROVIDER_ARTIFACT_EXACT_JOIN')
    P.integer(artifact.get('id'),1,10**20)
    workflow_raw=workflow_body(snapshot['workflow'],ctx,workflow_sha256,representation=workflow_representation)
    return dict(authority='NONE',request=q,request_raw=files['REQUEST.json'],certificate=files['RECIPIENT.pem'],
       archive_sha256=P.sha(archive),artifact_id=artifact['id'],job_id=job['id'],repository_id=repo_id,
       workflow_body_sha256=P.sha(workflow_raw))
