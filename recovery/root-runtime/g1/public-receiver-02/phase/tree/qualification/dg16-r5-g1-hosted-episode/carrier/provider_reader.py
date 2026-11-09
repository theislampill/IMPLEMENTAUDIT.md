"""Fixed-repository authenticated HTTPS reads; no provider write capability.

Public JSON alone cannot construct ReceivedRequest. The entry point performs
fresh provider reads and binds the actual artifact ZIP to its provider digest.
The ZIP download itself is a separately owned acquisition, not a payload URL.
"""
import base64
import datetime
import hashlib
import io
import json
import math
import re
import signal
import ssl
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile
import carrier_policy as P

_RECEIVED = object()
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
    P.need(q['issued_unix_ms']<=unix_ms(artifact.get('created_at'))<=now_ms,'PROVIDER_ARTIFACT_CHRONOLOGY')
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

def check_control(ref,commit,tree,blobs,branch,parent):
    P.need(ref.get('ref')=='refs/heads/'+branch and ref.get('object',{}).get('type')=='commit'
      and ref['object']['sha']==commit.get('sha') and commit['sha']!=parent,'CONTROL_REF_BINDING')
    P.need(type(commit.get('parents')) is list and len(commit['parents'])==1
      and commit['parents'][0].get('sha')==parent,'CONTROL_ONE_FRESH_COMMIT')
    P.need(commit.get('tree',{}).get('sha')==tree.get('sha') and tree.get('truncated') is False
      and type(tree.get('tree')) is list and len(tree['tree'])==2,'CONTROL_TREE_BINDING')
    entries=tree['tree'];P.need({r.get('path') for r in entries}=={'CONTROL.json','INPUTS.cms'},'CONTROL_TREE_POPULATION')
    result={}
    for row in entries:
        name=row['path'];maximum=P.MAX_CONTROL if name=='CONTROL.json' else P.MAX_CIPHERTEXT
        P.need(row.get('mode')=='100644' and row.get('type')=='blob','CONTROL_TREE_MEMBER')
        raw=blob(blobs.get(row.get('sha')),maximum)
        P.need(blobs[row['sha']]['sha']==row['sha'] and row.get('size')==len(raw),'CONTROL_TREE_BLOB_BINDING')
        result[name]=raw
    return result

class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,*args,**kwargs):raise ValueError('PROVIDER_REDIRECT_REFUSED')

class GitHubReads:
    """No caller-selected origin, URL, HTTP method, proxy or publication."""
    def __init__(self,binding,token,deadline):
        P.need(token is None or (type(token) is str and 0<len(token)<=4096 and '\n' not in token and '\r' not in token),'PROVIDER_CREDENTIAL_SHAPE')
        self.binding=binding;self.token=token;self.deadline=deadline;self.audit=[]
        self.limit=math.ceil(binding['limits']['acquisition_seconds']/binding['limits']['poll_seconds'])*2+64
        self.opener=urllib.request.build_opener(urllib.request.ProxyHandler({}),
           urllib.request.HTTPSHandler(context=ssl.create_default_context()),_NoRedirect())
    def get(self,kind,identifier):
        P.need(time.monotonic()<self.deadline and len(self.audit)<self.limit,'PROVIDER_ACQUISITION_BOUND')
        prefix='/repos/'+P.REPOSITORY
        if kind in ('run','attempt','jobs','artifacts','artifact'):
            P.need(type(identifier) is str and re.fullmatch('[1-9][0-9]{0,19}',identifier),'PROVIDER_IDENTIFIER')
            suffix={'run':'/actions/runs/'+identifier,'attempt':'/actions/runs/'+identifier+'/attempts/1',
              'jobs':'/actions/runs/'+identifier+'/attempts/1/jobs?per_page=100&page=1',
              'artifacts':'/actions/runs/'+identifier+'/artifacts?per_page=100&page=1',
              'artifact':'/actions/artifacts/'+identifier}[kind]
        elif kind=='ref':
            P.need(identifier==self.binding['control_branch'],'PROVIDER_FIXED_REF')
            suffix='/git/ref/heads/'+urllib.parse.quote(identifier,safe='/')
        elif kind in ('commit','tree','blob','workflow'):
            P.need(type(identifier) is str and re.fullmatch('[0-9a-f]{40}',identifier),'PROVIDER_GIT_IDENTIFIER')
            suffix=('/contents/'+self.binding['workflow_path']+'?ref='+identifier if kind=='workflow' else
              '/git/'+{'commit':'commits','tree':'trees','blob':'blobs'}[kind]+'/'+identifier)
        else:raise ValueError('PROVIDER_READ_KIND')
        maximum=2*P.MAX_CIPHERTEXT+65536 if kind=='blob' else P.MAX_METADATA
        headers={'Accept':'application/vnd.github+json','X-GitHub-Api-Version':'2022-11-28','User-Agent':'DG16-fixed-private-carrier'}
        if self.token is not None:headers['Authorization']='Bearer '+self.token
        request=urllib.request.Request('https://api.github.com'+prefix+suffix,headers=headers,method='GET')
        started=time.monotonic();old_handler=signal.getsignal(signal.SIGALRM);old_timer=signal.getitimer(signal.ITIMER_REAL)
        def expired(*_):raise ValueError('PROVIDER_DEADLINE')
        remaining=self.deadline-started
        timeout=min(remaining,self.binding['limits']['command_seconds'])
        if old_timer[0]>0:timeout=min(timeout,old_timer[0])
        signal.signal(signal.SIGALRM,expired);signal.setitimer(signal.ITIMER_REAL,max(0.001,timeout))
        try:
            with self.opener.open(request,timeout=max(0.001,timeout)) as response:
                P.need(response.status==200,'PROVIDER_STATUS')
                chunks=[];count=0
                while True:
                    P.need(time.monotonic()<self.deadline,'PROVIDER_DEADLINE')
                    part=response.read1(min(65536,maximum-count+1))
                    if not part:break
                    count+=len(part);P.need(count<=maximum,'PROVIDER_BODY_BOUND');chunks.append(part)
                raw=b''.join(chunks)
        except (urllib.error.URLError,OSError) as exc:raise ValueError('PROVIDER_READ_REFUSED') from None
        finally:
            signal.setitimer(signal.ITIMER_REAL,0);signal.signal(signal.SIGALRM,old_handler)
            if old_timer[0]>0:signal.setitimer(signal.ITIMER_REAL,max(0.001,old_timer[0]-(time.monotonic()-started)),old_timer[1])
        self.audit.append(dict(kind=kind,bytes=len(raw),sha256=P.sha(raw),elapsed_ns=int((time.monotonic()-started)*10**9)))
        return json_body(raw)

def snapshot(api,ctx,artifact_id):
    return dict(run=api.get('run',ctx['run_id']),attempt=api.get('attempt',ctx['run_id']),
       jobs=api.get('jobs',ctx['run_id']),artifact=api.get('artifact',str(artifact_id)),
       artifacts=api.get('artifacts',ctx['run_id']),workflow=api.get('workflow',ctx['workflow_commit']))

class ReceivedRequest:
    def __init__(self,key,checked,archive,binding,api,observed=None,*,workflow_representation=RAW_API_WORKFLOW):
        P.need(key is _RECEIVED,'PUBLIC_JSON_IS_NOT_PROVIDER_AUTHORITY')
        P.need(workflow_representation in (RAW_API_WORKFLOW,SUPPORTED_TOOL_WORKFLOW),'PROVIDER_WORKFLOW_REPRESENTATION')
        self.workflow_representation=workflow_representation
        self.checked=checked;self.archive=archive;self.binding=binding;self.api=api
        self.observed=observed
        self.request_raw=checked['request_raw'];self.certificate=checked['certificate']
        self.context={k:checked['request'][k] for k in P.CONTEXT_KEYS}
        self.initial=dict(artifact_id=checked['artifact_id'],job_id=checked['job_id'],repository_id=checked['repository_id'],
            request_sha256=P.sha(self.request_raw),recipient_sha256=P.sha(self.certificate),archive_sha256=P.sha(archive))
    def recheck(self):
        observed=snapshot(self.api,self.context,self.checked['artifact_id'])
        checked=check_snapshot(observed,self.archive,self.context,
          self.binding['_index'],self.binding['workflow_sha256'],int(time.time()*1000),
          workflow_representation=self.workflow_representation)
        now=dict(artifact_id=checked['artifact_id'],job_id=checked['job_id'],repository_id=checked['repository_id'],
          request_sha256=P.sha(checked['request_raw']),recipient_sha256=P.sha(checked['certificate']),archive_sha256=checked['archive_sha256'])
        P.need(now==self.initial,'PROVIDER_REQUEST_CLOSING_CHANGED')
        self.observed=observed
        return dict(schema='dg16.actual-provider-request-receiving.v1',authority='NONE',**now,
          observed_reads=list(self.api.audit),fresh_provider_readback=True,original_awards=[])

def receive_request(binding,run_id,workflow_commit,artifact_id,archive,token,deadline):
    ctx=dict(repository=P.REPOSITORY,branch=binding['branch'],workflow_commit=workflow_commit,
      workflow_path=binding['workflow_path'],run_id=run_id,run_attempt=1,job_name=binding['job_name'])
    P.context(ctx);P.integer(artifact_id,1,10**20)
    api=GitHubReads(binding,token,deadline)
    observed=snapshot(api,ctx,artifact_id)
    checked=check_snapshot(observed,archive,ctx,binding['_index'],binding['workflow_sha256'],int(time.time()*1000))
    P.need(checked['artifact_id']==artifact_id,'PROVIDER_ARTIFACT_IDENTIFIER')
    return ReceivedRequest(_RECEIVED,checked,archive,binding,api,observed)

def control(api):
    binding=api.binding;ref=api.get('ref',binding['control_branch'])
    P.need(ref.get('ref')=='refs/heads/'+binding['control_branch'] and ref.get('object',{}).get('type')=='commit','CONTROL_REF_BINDING')
    selected=ref['object']['sha']
    if selected==binding['control_parent']:return None
    commit=api.get('commit',selected);tree=api.get('tree',commit.get('tree',{}).get('sha'))
    P.need(type(tree.get('tree')) is list and len(tree['tree'])==2,'CONTROL_TREE_POPULATION')
    blobs={row['sha']:api.get('blob',row['sha']) for row in tree['tree']}
    files=check_control(ref,commit,tree,blobs,binding['control_branch'],binding['control_parent'])
    closing=api.get('ref',binding['control_branch'])
    P.need(closing==ref,'CONTROL_REF_CHANGED_DURING_ACQUISITION')
    observed=dict(ref=ref,commit=commit,tree=tree,closing_ref=closing)
    P.need(len(P.encode(observed))<=P.MAX_METADATA,'CONTROL_PROVIDER_AGGREGATE_BOUND')
    return dict(commit=selected,files=files,reads=list(api.audit),provider=observed)
