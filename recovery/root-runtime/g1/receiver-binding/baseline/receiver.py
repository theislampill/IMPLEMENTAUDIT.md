"""Outcome-neutral, offline root receiving. No provider, command or grant API.

Supported tool calls occur ONLY in the root runtime. Call reserve first, retain
its complete actual result before the next call, then supply the actual ZIP.
Local JSON cannot authenticate a tool, root actor, publication or observation.
"""
import argparse
import ast
import base64
import builtins
import hashlib
import io
import json
import os
from pathlib import Path
import re
import stat
import time
import types
import zipfile

SOURCE_SHA = None  # Refuses until the pure final binder receives actual final review/root evidence.
LANE = Path(__file__).resolve().parent.parent
CORE = 'tree/qualification/dg16-r5-g1-hosted-episode/'
ENTRY = 'tree/qualification/dg16-r5-g1-hosted-entry/'
TOOL = 'mcp__codex_apps__github_fetch'
DOWNLOAD = 'mcp__codex_apps__github_download_workflow_artifact'
MAX_RESULT = 4 * 1024**2
MAX_JOURNAL = 8 * 1024**2
MAX_ENTRIES = 128
ORDER = ('artifacts','run','attempt','jobs','artifact','workflow','download')
PHASES = {
 'tools': ('dg16-core-host-tools-{run}-a1', ('HOST_TOOL_OBSERVATION.json',),131072,65536),
 'recipient': ('dg16-core-private-recipient-{run}-a1', ('REQUEST.json','RECIPIENT.pem'),65536,16384),
 'g3_initial': ('dg16-g1-root-request-{run}-1', ('ROOT_REQUEST.json','SCOPE_RECEIVING.json','G1_RECEIVING.json','ARTIFACT_MANIFEST.json'),65536,40960),
 'g3_final': ('dg16-g1-original-request-{run}-1', ('FINAL_REQUEST.json','INDEPENDENT_PROOF_RECEIPT.json','ARTIFACT_MANIFEST.json'),32768,24576),
 'terminal': ('dg16-g1-hosted-{run}-1', ('RESULT.json','HOST.json','SOURCE.json','OPERATION.json','G3.json','NSS.json','CLEANUP.json','FAILURE.json','ARTIFACT_MANIFEST.json'),262144,163840),
 'failure': ('dg16-g1-retention-failure-{run}-1', ('RETENTION_FAILURE.json','ARTIFACT_MANIFEST.json'),65536,32768),
}
PRECORE_SOURCE_SHA = '07613d2dad8a7fef9d8d27f552cc06b20d3a5131a50627c54047b19450759d89'
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

def read(path,maximum=MAX_RESULT):
    p=Path(path);need(p.is_absolute(),'ABSOLUTE_PATH_REQUIRED')
    for parent in [p.parent,*p.parents]: need(not parent.is_symlink(),'SYMLINK_ANCESTOR')
    fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW)
    try:
        a=os.fstat(fd);need(stat.S_ISREG(a.st_mode) and a.st_nlink==1 and a.st_size<=maximum,'ORDINARY_SINGLE_FILE_BOUND')
        chunks=[];n=0
        while True:
            b=os.read(fd,min(65536,maximum+1-n))
            if not b:break
            chunks.append(b);n+=len(b);need(n<=maximum,'FILE_BOUND')
        b=os.fstat(fd);need((a.st_dev,a.st_ino,a.st_size,a.st_mtime_ns,a.st_ctime_ns)==(b.st_dev,b.st_ino,b.st_size,b.st_mtime_ns,b.st_ctime_ns),'FILE_CHANGED')
        return b''.join(chunks)
    finally:os.close(fd)

class Sources:
    """Verify the fixed phase; load reviewed source functions without main()."""
    def __init__(self):
        raw=read(LANE/'SOURCES.json');need(sha(raw)==SOURCE_SHA,'SOURCE_INDEX_CHANGED');self.sources=parse(raw)
        for name in ('phase','author_seal','dispatcher_seal','dispatcher_review_seal','root_offline_receiving','host_independent_review_seal','download_shape_observation','root_broker','predecessor_receiver_seal','consumer_author_seal','consumer_independent_review_seal'):
            row=self.sources[name];need(desc(read(Path(row['path']),4*1024**2))=={'bytes':row['bytes'],'sha256':row['sha256']},'BOUND_SOURCE_CHANGED')
        self.root=Path(self.sources['phase_root']);self.phase=parse(read(self.root/'PHASE.json'))
        members=self.phase['members'];actual={}
        for p in self.root.rglob('*'):
            need(not p.is_symlink(),'PHASE_SYMLINK')
            if p.is_file() and p.relative_to(self.root).as_posix()!='PHASE.json':actual[p.relative_to(self.root).as_posix()]=desc(read(p,32*1024**2))
        need(actual==members,'EXACT_PHASE_CHANGED')
        self.modules={}
        self.P=self.module('carrier_policy');self.V=self.module('provider_reader');self.B=self.module('tool_broker');self.H=self.module('host_tools')
        self.G=self.module('g3_receiving');self.R=self.module('run');self.I=self.module('proof_consumer')
        self.proof_pins=self.I.pins_contract(parse(self.body(CORE+'INDEPENDENT_PROOF_PINS.json')))
        self.scope_basis=parse(self.body(CORE+'ORIGINAL_SCOPE.json'))
        need(self.proof_pins['consumer_sha256']==sha(self.body(CORE+'proof_consumer.py')) and self.proof_pins['scope_module_sha256']==sha(self.body(CORE+'g3_receiving.py')) and self.proof_pins['scope_sha256']==sha(self.body(CORE+'ORIGINAL_SCOPE.json')) and self.proof_pins['adverse_sha256']==sha(self.body(CORE+'ADVERSE_APPLICABILITY.json')),'INDEPENDENT_CONSUMER_SOURCE_JOIN')
        self.R.load_module=lambda name:self.module(name) if name in ('g3_receiving','nss_configuration') else (_ for _ in ()).throw(Refusal('PURE_VALIDATOR_ONLY'))
        self.binding_raw=self.body(CORE+'carrier/CARRIER_COMPOSITION.json')
        self.binding=parse(self.binding_raw);self.index=parse(self.body(CORE+'carrier/INPUT_INDEX.json'))
        self.binding['_binding_raw']=self.binding_raw;self.binding['_index']=self.index
        self.anchor={
          'public_manifest_sha256':sha(self.body(ENTRY+'PUBLIC_PACKET_MANIFEST.json')),
          'bootstrap_admission_sha256':sha(self.body(ENTRY+'BOOTSTRAP_ADMISSION.json'))}
    def body(self,path):
        row=self.phase['members'][path];b=read(self.root/path,32*1024**2);need(desc(b)==row,'PHASE_MEMBER_CHANGED');return b
    def module(self,name):
        if name in self.modules:return self.modules[name]
        local={'bundle_codec','carrier_policy','carrier_io','provider_reader','tool_broker','host_tools'}
        need(name in local|{'g3_receiving','run','nss_configuration','proof_consumer'},'FIXED_DEPENDENCY_ONLY')
        rel=CORE+('carrier/' if name in local else '')+name+'.py'
        raw=read(Path(self.sources['root_broker']['path'])) if name=='tool_broker' else self.body(rel);m=types.ModuleType('dg16_root_receive_'+name);m.__file__=self.sources['root_broker']['path'] if name=='tool_broker' else str(self.root/rel)
        def importer(n,globals=None,locals=None,fromlist=(),level=0):
            if n in local:need(level==0,'RELATIVE_DEPENDENCY_REFUSED');return self.module(n)
            return builtins.__import__(n,globals,locals,fromlist,level)
        m.__dict__['__builtins__']=dict(vars(builtins),__import__=importer)
        self.modules[name]=m
        exec(compile(raw,m.__file__,'exec'),m.__dict__)
        return m
    def context(self,ctx):
        self.P.context(ctx)
        for k in ('repository','branch','workflow_path','job_name'):need(ctx[k]==self.binding[k],'FIXED_HOST_CONTEXT')
        return ctx
    def endpoint(self,ctx,artifact_id,kind):return self.B.endpoint(ctx,artifact_id,kind)

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
    created=s.V.unix_ms(a.get('created_at'));need(start<=created<=now and (issued is None or issued<=created),'PROVIDER_ARTIFACT_CHRONOLOGY')
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
        _,_,g1=s.I.validate_first(files['ROOT_REQUEST.json'],files['SCOPE_RECEIVING.json'],files['G1_RECEIVING.json'],s.proof_pins,s.scope_basis)
        issued=request['issued_unix_ms'];detail=dict(scope=scope,g1=g1,request=request,request_window_open=issued<=now_ms<request['expires_unix_ms'])
    elif phase=='g3_final':
        check_manifest(files,'dg16.g1-final-request-artifacts.v1');request=s.G.validate_public_final_request(files['FINAL_REQUEST.json']);issued=request['issued_unix_ms']
        need(type(previous) is dict and previous.get('phase')=='g3_initial' and previous.get('context')==ctx,'INITIAL_RECEIVING_REQUIRED')
        q=s.G.validate_public_request(previous['files']['ROOT_REQUEST.json']);s.G.validate_public_scope(previous['files']['SCOPE_RECEIVING.json'])
        need(request['initial_request_sha256']==sha(previous['files']['ROOT_REQUEST.json']) and request['initial_graph_sha256']==q['graph_sha256']
          and request['proofs']['scope_receiving']==sha(previous['files']['SCOPE_RECEIVING.json']) and request['g1_complete_input_key']==q['complete_input_key']
          and request['shared_window_started_unix_ms']==q['issued_unix_ms'] and request['expires_unix_ms']==q['shared_expires_unix_ms']
          and request['shared_window_seconds']==q['shared_window_seconds'] and sum(map(len,previous['files'].values()))+sum(map(len,files.values()))<=65536,'G3_BOTH_HOLDS_EXACT_JOIN')
        s.I.validate_first(previous['files']['ROOT_REQUEST.json'],previous['files']['SCOPE_RECEIVING.json'],previous['files']['G1_RECEIVING.json'],s.proof_pins,s.scope_basis)
        need(type(actual_root_raw) is bytes and 0<len(actual_root_raw)<=8192,'ACTUAL_ROOT_FIRST_DECISION_BYTES_REQUIRED')
        independent=s.I.validate_receipt(files['INDEPENDENT_PROOF_RECEIPT.json'],previous['files']['ROOT_REQUEST.json'],files['FINAL_REQUEST.json'],actual_root_raw,s.proof_pins)
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

class Session:
    """Write-once local call reservations. Never calls a tool or provider."""
    def __init__(self,path,s):
        self.path=Path(path);self.s=s;need(self.path.is_absolute() and self.path.resolve()==self.path,'SESSION_CANONICAL_PATH')
        need(self.path.is_dir() and not self.path.is_symlink() and stat.S_IMODE(self.path.stat().st_mode)==0o700,'SESSION_PRIVATE_DIRECTORY')
        self.plan=parse(read(self.path/'PLAN.json'));s.context(self.plan['context']);need(self.plan['phase'] in PHASES and self.plan['source_index_sha256']==SOURCE_SHA,'SESSION_SOURCE_JOIN');self.bound()
    @classmethod
    def create(cls,path,s,phase,ctx):
        s.context(ctx);need(phase in PHASES,'FIXED_PHASE');p=Path(path);need(p.is_absolute() and p.resolve()==p,'SESSION_CANONICAL_PATH')
        p.mkdir(mode=0o700)
        b=encode(dict(schema='dg16.root-artifact-call-plan.v1',authority='NONE',source_index_sha256=SOURCE_SHA,phase=phase,context=ctx,order=list(ORDER),automatic_retry=False,authentication_boundary=AUTH))
        fd=os.open(p/'PLAN.json',os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
        try:
            remaining=memoryview(b)
            while remaining:n=os.write(fd,remaining);need(n>0,'SHORT_WRITE');remaining=remaining[n:]
            os.fsync(fd)
        finally:os.close(fd)
        cls.sync(p);need(read(p/'PLAN.json')==b,'PLAN_READBACK');return cls(p,s)
    @staticmethod
    def sync(path):
        fd=os.open(path,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
        try:os.fsync(fd)
        finally:os.close(fd)
    def bound(self,additional=0,entries=0):
        rows=list(self.path.iterdir());need(len(rows)+entries<=MAX_ENTRIES,'JOURNAL_ENTRY_BOUND');n=0
        for p in rows:
            st=p.lstat();need(stat.S_ISREG(st.st_mode) and st.st_nlink==1 and stat.S_IMODE(st.st_mode)==0o600,'JOURNAL_FILE_CUSTODY');n+=st.st_size
        need(n+additional<=MAX_JOURNAL,'JOURNAL_BYTE_BOUND')
    def write(self,name,raw):
        need('/' not in name and type(raw) is bytes,'LOCAL_WRITE_SHAPE');self.bound(len(raw),1)
        fd=os.open(self.path/name,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
        try:
            remaining=memoryview(raw)
            while remaining:n=os.write(fd,remaining);need(n>0,'SHORT_WRITE');remaining=remaining[n:]
            os.fsync(fd)
        finally:os.close(fd)
        self.sync(self.path);need(read(self.path/name,max(len(raw),1))==raw,'LOCAL_WRITE_READBACK')
    def artifact(self):return candidate(self.s,self.plan['phase'],self.plan['context'],read(self.path/'artifacts.RESULT.json'))
    def reserve(self,kind):
        need(kind in ORDER,'FIXED_CALL_KIND');i=ORDER.index(kind)
        for before in ORDER[:i]:self.ready(before)
        need(not any((self.path/(kind+x)).exists() for x in ('.INTENT.json','.RESULT.json','.READY.json')),'NO_UNCERTAIN_REPLAY')
        ctx=self.plan['context'];a=None if kind=='artifacts' else self.artifact()
        args={'repo_full_name':ctx['repository'],'artifact_id':a['id'],'file_name':artifact_name(self.plan['phase'],ctx)+'.zip'} if kind=='download' else {'url':self.s.endpoint(ctx,a['id'] if a else 1,kind)}
        v=dict(schema='dg16.root-receiver-call-intent.v1',authority='NONE',kind=kind,tool=DOWNLOAD if kind=='download' else TOOL,arguments=args,issued_unix_ms=time.time_ns()//1000000,automatic_retry=False)
        self.bound(MAX_RESULT+8192,3)  # Reserve the complete maximum result and receipt before the root calls.
        self.write(kind+'.INTENT.json',encode(v));return v
    def ready(self,kind):
        intent=parse(read(self.path/(kind+'.INTENT.json')));raw=read(self.path/(kind+'.RESULT.json'));ready=parse(read(self.path/(kind+'.READY.json')))
        need(ready['intent']==desc(encode(intent)) and ready['retained_result']==desc(raw),'RETAINED_RESULT_CHANGED');return raw
    def retain(self,kind,raw):
        need(kind in ORDER,'FIXED_CALL_KIND');intent=parse(read(self.path/(kind+'.INTENT.json')))
        need(not any((self.path/(kind+x)).exists() for x in ('.RESULT.json','.READY.json','.REJECTED.json')),'RESULT_NO_REPLAY')
        need(0<len(raw)<=MAX_RESULT,'COMPLETE_RESULT_BOUND')
        original=desc(raw)
        if kind=='download':
            try:
                note=download_note(raw,intent['arguments']['artifact_id'],intent['arguments']['file_name'])
                check_download(note,intent['arguments']['artifact_id'],intent['arguments']['file_name'])
                raw=encode(note)
            except (ValueError,TypeError,KeyError):
                self.write(kind+'.REJECTED.json',encode(dict(schema='dg16.download-result-refused-before-retention.v1',authority='NONE',actual_tool_result=original,reason='DOWNLOAD_SHAPE_OR_CREDENTIAL_REFUSED',raw_result_retained=False,ready=False,automatic_retry=False,authentication_boundary=AUTH)))
                raise Refusal('DOWNLOAD_RESULT_REFUSED_BEFORE_RETENTION')
        self.write(kind+'.RESULT.json',raw)
        if kind!='download':
            self.s.B.unwrap_tool_result(raw,intent['arguments']['url'],kind=kind,context=self.plan['context'],workflow_sha256=self.s.binding['workflow_sha256'],artifact_id=self.artifact()['id'])
        self.write(kind+'.READY.json',encode(dict(intent=desc(encode(intent)),retained_result=desc(raw),actual_tool_result=original,retained_unix_ms=time.time_ns()//1000000)))
        return dict(retained_result=desc(raw),automatic_retry=False)
    def body(self,raw):
        self.ready('download');a=self.artifact();need(0<len(raw)<=PHASES[self.plan['phase']][2] and a.get('size_in_bytes')==len(raw) and a.get('digest')=='sha256:'+sha(raw),'ACTUAL_ARCHIVE_BODY_JOIN')
        self.write('ARTIFACT.zip',raw);return desc(raw)
    def receive(self,now_ms=None,previous=None,save=True,actual_root_raw=None):
        now=time.time_ns()//1000000 if now_ms is None else now_ms
        results={k:self.ready(k) for k in self.s.B.KINDS};note=parse(self.ready('download'))
        got=receive(self.s,self.plan['phase'],self.plan['context'],results,read(self.path/'ARTIFACT.zip',PHASES[self.plan['phase']][2]),note,now,previous,actual_root_raw)
        if save:self.write('RECEIVING.json',encode(got['receipt']))
        return got

def requirements(s,received):
    phase=received['phase'];f=received['files'];ctx=received['context'];pending=[]
    if phase=='tools':
        q=parse(f['HOST_TOOL_OBSERVATION.json']);fixed=dict(schema='dg16.same-host-fixed-tool-root-adoption.v1',issuer='R5_ROOT_GOVERNOR',operation='ADOPT_FIXED_SAME_HOST_TOOL_BODIES',observation=desc(f['HOST_TOOL_OBSERVATION.json']),command_scope=['recipient','decrypt'],automatic_retry=False,crypto_capability_claim=False,core_or_native_effect_grant=False,original_awards=[])
        for k in ('context','source_commit','source_tree','carrier_binding_sha256','input_index_sha256','public_manifest_sha256','bootstrap_admission_sha256','nonce','host_identity','tools'):fixed[k]=q[k]
        pending=['issued_unix_ms','expires_unix_ms'];path='HOST_TOOL_ADOPTION.json';branch=s.binding['host_tools']['control_branch'];parent=s.binding['host_tools']['control_parent']
    elif phase=='g3_initial':
        q=s.G.validate_public_request(f['ROOT_REQUEST.json']);fixed=dict(schema='dg16.g3-root-consumption-decision.v2',issuer='R5_ROOT_GOVERNOR',action='CONSUME_COMPONENT_RETURNS_ONLY',request_sha256=sha(f['ROOT_REQUEST.json']),outputs={s.G.PAIR:q['g1_return_sha256'],s.G.SCOPE:q['scope_return_sha256']},consumed_nodes=s.G.SELECTED,owner_arrangement=s.G.OWNER_ARRANGEMENT,original_awards=0)
        for k in ('run_id','attempt','nonce','source_commit','source_tree','graph_sha256','dispatch_sha256','join_sha256','decision_before','decision_after','full_g2','expires_unix_ms'):fixed[k]=q[k]
        pending=['issued_unix_ms'];path=q['control_path'];branch=q['control_branch'];parent=None
    elif phase=='g3_final':
        q=s.G.validate_public_final_request(f['FINAL_REQUEST.json']);fixed=dict(schema='dg16.g3-root-original-decision.v2',issuer='R5_ROOT_GOVERNOR',action='RECEIVE_EXACT_ORIGINAL_IDS_AND_GATES',request_sha256=sha(f['FINAL_REQUEST.json']),whole_DG16_awarded=False,full_g2='NOT_DISPATCHED_OR_CONSUMED_IN_THIS_HOST',v041_admission='PENDING_NOT_GRANTED_BY_THIS_EPISODE',global_liveness='NOT_ESTABLISHED',retirement_or_transfer='NOT_PERFORMED')
        for k in ('run_id','attempt','nonce','source_commit','source_tree','final_graph_sha256','current_receipt_sha256','proofs','expires_unix_ms'):fixed[k]=q[k]
        pending=['issued_unix_ms','independent_review_sha256','source_applicability_review_sha256','original_rows','gate_decisions'];path=q['control_path'];branch=q['control_branch'];parent=None
    else:raise Refusal('ROOT_CONTROL_REQUIREMENTS_PHASE')
    return dict(schema='dg16.root-control-requirements.v1',authority='NONE',receiving=desc(encode(received['receipt'])),required_fixed_fields=fixed,root_supplied_fields=pending,path=path,branch=branch,required_parent=parent,root_body_issued=False,effect_grant=False,original_awards=[])


def sender_requirements(s,received,root_selection,actual_host_receiving):
    need(received['phase']=='recipient','RECIPIENT_RECEIVING_REQUIRED');ctx=received['context'];q=parse(received['files']['REQUEST.json'])
    fields={'fixed_packet_directory','nonce','issued_unix_ms','expires_unix_ms','sender_uid','sender_gid'};need(type(root_selection) is dict and set(root_selection)==fields,'ROOT_SENDER_SELECTION_FIELDS')
    path=Path(root_selection['fixed_packet_directory']);need(path.is_absolute() and path.resolve()==path and path.name=='packet','FIXED_SENDER_PACKET_PATH')
    need(type(root_selection['nonce']) is str and re.fullmatch('[0-9a-f]{64}',root_selection['nonce']),'ROOT_OPERATION_NONCE')
    issued=integer(root_selection['issued_unix_ms'],q['issued_unix_ms']);integer(root_selection['expires_unix_ms'],issued+1,min(q['expires_unix_ms'],issued+s.binding['limits']['acquisition_seconds']*1000))
    integer(root_selection['sender_uid'],1);integer(root_selection['sender_gid'])
    need(type(actual_host_receiving) is bytes and 0<len(actual_host_receiving)<=MAX_RESULT,'ACTUAL_HOST_PUBLICATION_RECEIVING_BODY_REQUIRED')
    a=received['receipt']['provider']['artifact_id'];artifact=received['receipt']['archive']
    selection=dict(schema='dg16.late-root-sender-assembly-selection.v1',issuer='R5_ROOT_GOVERNOR',fixed_packet_directory=str(path),source_commit=s.P.SOURCE_COMMIT,source_tree=s.P.SOURCE_TREE,
      workflow_commit=ctx['workflow_commit'],workflow_branch=ctx['branch'],workflow_path=ctx['workflow_path'],workflow_sha256=s.binding['workflow_sha256'],**s.anchor,
      carrier_binding_sha256=sha(s.binding_raw),input_index_sha256=s.binding['input_index']['sha256'],artifact_id=a,artifact=artifact,request_sha256=sha(received['files']['REQUEST.json']),actual_host_receiving_sha256=sha(actual_host_receiving),original_awards=[])
    op=dict(schema='dg16.pro-private-sender-operation.v1',context=ctx,source_commit=s.P.SOURCE_COMMIT,source_tree=s.P.SOURCE_TREE,carrier_binding_sha256=sha(s.binding_raw),input_index_sha256=s.binding['input_index']['sha256'],artifact_id=a,artifact=artifact,original_awards=[])
    op.update({k:root_selection[k] for k in fields if k!='fixed_packet_directory'})
    comp=parse(s.body(CORE+'carrier/PRO_SENDER_COMPOSITION.json'))
    admission=dict(schema='dg16.pro-private-sender-root-admission.v1',issuer='R5_ROOT_GOVERNOR',operation_sha256=sha(encode(op)),capture_profile=comp['capture_profile'],provider_profile=s.B.PROFILE,source_commit=s.P.SOURCE_COMMIT,source_tree=s.P.SOURCE_TREE,carrier_binding_sha256=sha(s.binding_raw),limits=s.binding['limits'],one_encryption=True,metadata_reads=18,automatic_retry=False,host_or_native_effect_grant=False,original_awards=[])
    return dict(schema='dg16.late-root-sender-input-requirements.v1',authority='NONE',root_selection_fields=selection,operation_fields=op,required_admission_fields=admission,
      admission_issued=False,actual_host_receiving=desc(actual_host_receiving),authentication_boundary=AUTH,
      existing_assembler=str(LANE/'author/late_sender.py'),existing_dispatcher_binder=str(Path(s.sources['dispatcher_root'])/'author/bind_dispatcher.py'),dispatcher_reads=18,effect_grant=False,original_awards=[])

def validate_control(s,received,raw,now_ms):
    phase=received['phase'];f=received['files'];integer(now_ms,1,10**16)
    if phase=='tools':return s.H.validate_adoption(raw,f['HOST_TOOL_OBSERVATION.json'],s.binding,now_ms)
    if phase=='g3_initial':
        q=s.G.validate_public_request(f['ROOT_REQUEST.json']);return s.G.validate_decision(raw,q,sha(f['ROOT_REQUEST.json']),now_ms)
    if phase=='g3_final':
        q=s.G.validate_public_final_request(f['FINAL_REQUEST.json']);return s.G.validate_final_decision(raw,q,sha(f['FINAL_REQUEST.json']),now_ms)
    raise Refusal('CONTROL_PHASE')

def git_object(kind,raw):return hashlib.sha1(kind.encode()+b' '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
def fixed_tree(files):
    """Pure object hashing only, no Git process or repository operation."""
    tree={}
    for path,raw in files.items():
        node=tree;parts=path.split('/')
        for part in parts[:-1]:node=node.setdefault(part,{})
        node[parts[-1]]=raw
    def digest_tree(node):
        rows=[]
        for name,value in node.items():
            directory=type(value) is dict
            h=digest_tree(value) if directory else git_object('blob',value)
            key=(name+'/' if directory else name).encode()
            rows.append((key,(b'40000' if directory else b'100644')+b' '+name.encode()+b'\0'+bytes.fromhex(h)))
        return git_object('tree',b''.join(row for _,row in sorted(rows)))
    return digest_tree(tree)

def publication_plan(s,received,body,parent_sha,now_ms,initial_control=None):
    """Require an actual root-issued body; return inert supported-call inputs."""
    validate_control(s,received,body,now_ms);req=requirements(s,received)
    need(type(parent_sha) is str and re.fullmatch('[0-9a-f]{40}',parent_sha),'ACTUAL_CONTROL_PARENT_REQUIRED')
    if req['required_parent'] is not None:need(parent_sha==req['required_parent'],'FIXED_WAITING_PARENT')
    files={req['path']:body}
    if received['phase']=='g3_final':
        need(type(initial_control) is dict and set(initial_control)=={'body','receiving','published_commit'},'PRIOR_ACTUAL_G3_CONTROL_REQUIRED')
        prior=initial_control['receiving'];need(prior['phase']=='g3_initial' and prior['context']==received['context'],'PRIOR_G3_CONTROL_CONTEXT')
        q=s.G.validate_public_request(prior['files']['ROOT_REQUEST.json']);v=parse(initial_control['body'],8192)
        # Check the prior body at its recorded issuance; this grants no currentness.
        s.G.validate_decision(initial_control['body'],q,sha(prior['files']['ROOT_REQUEST.json']),v['issued_unix_ms'])
        need(parent_sha==initial_control['published_commit'] and received['receipt']['details']['request']['initial_request_sha256']==sha(prior['files']['ROOT_REQUEST.json']),'PRIOR_PUBLISHED_G3_COMMIT_JOIN')
        need(desc(initial_control['body'])==received['receipt']['details']['actual_first_root_decision'],'ACTUAL_FIRST_DECISION_CUSTODY_JOIN')
        files[s.G.CONTROL_PATH]=initial_control['body']
    return dict(schema='dg16.root-control-publication-plan.v1',authority='NONE',phase=received['phase'],context=received['context'],branch=req['branch'],parent_sha=parent_sha,
      files={n:dict(body_utf8=b.decode('utf-8'),**desc(b),git_blob_sha=git_object('blob',b)) for n,b in sorted(files.items())},expected_tree_sha=fixed_tree(files),
      receiving=desc(encode(received['receipt'])),root_body_validation_at_unix_ms=now_ms,root_issuer_authentication_required=True,authentication_boundary=AUTH,
      supported_tool_order=['mcp__codex_apps__github_create_tree','mcp__codex_apps__github_create_commit','mcp__codex_apps__github_update_ref'],
      reserve_and_retain_full_actual_result_before_next_call=True,automatic_retry=False,effect_grant=False,original_awards=[])

def result_sha(raw):
    v=parse(raw);need(type(v) is dict and set(v)<= {'content','structuredContent','isError','_meta'} and v.get('isError') is False,'WRITE_TOOL_RESULT_ERROR')
    m=v.get('_meta',{});need(type(m) is dict and not any(m.get(k) for k in ('truncated','isTruncated','partial','hasMore')),'WRITE_TOOL_TRUNCATION')
    sc=v.get('structuredContent');need(type(sc) is dict and type(sc.get('sha')) is str and re.fullmatch('[0-9a-f]{40}',sc['sha']),'ACTUAL_WRITE_RESULT_SHA_REQUIRED');return sc['sha']

def publication_call(plan,previous_results):
    need(plan.get('schema')=='dg16.root-control-publication-plan.v1' and plan.get('authority')=='NONE' and type(previous_results) is list and len(previous_results)<3,'PUBLICATION_PLAN_OR_STEP')
    files={n:r['body_utf8'].encode('utf-8') for n,r in plan['files'].items()}
    need(fixed_tree(files)==plan['expected_tree_sha'] and all(desc(files[n])=={'bytes':r['bytes'],'sha256':r['sha256']} and git_object('blob',files[n])==r['git_blob_sha'] for n,r in plan['files'].items()),'PUBLICATION_BODY_CHANGED')
    repo=plan['context']['repository'];i=len(previous_results)
    if i==0:args=dict(repository_full_name=repo,tree_elements=[dict(path=n,mode='100644',type='blob',content=b.decode('utf-8')) for n,b in sorted(files.items())])
    else:
        tree=result_sha(previous_results[0]);need(tree==plan['expected_tree_sha'],'ACTUAL_CREATED_TREE_DIFFERS')
        if i==1:args=dict(repository_full_name=repo,tree_sha=tree,parent_sha=plan['parent_sha'],message='DG16 root control '+plan['phase']+' run '+plan['context']['run_id'])
        else:args=dict(repository_full_name=repo,branch_name=plan['branch'],sha=result_sha(previous_results[1]),expected_sha=plan['parent_sha'],force=False)
    return dict(authority='NONE',tool=plan['supported_tool_order'][i],arguments=args,requires_separate_root_effect_authorization=True,
      previous_actual_tool_results=[desc(b) for b in previous_results],no_unknown_effect_replay=True)

def unwrap_control(raw,url):
    v=parse(raw);need(type(v) is dict and set(v)<= {'content','structuredContent','isError','_meta'} and v.get('isError') is False,'CONTROL_TOOL_RESULT')
    m=v.get('_meta',{});need(type(m) is dict and not any(m.get(k) for k in ('truncated','isTruncated','partial','hasMore')),'CONTROL_TOOL_TRUNCATED')
    sc=v.get('structuredContent');need(type(sc) is dict and set(sc)<= {'content','title','modified_date','url','display_url','display_title','structuredContent'}
      and sc.get('url')==url and sc.get('display_url')==url and type(sc.get('content')) is str,'CONTROL_ACTUAL_ENDPOINT')
    if 'structuredContent' in sc:
        inner=sc['structuredContent'];need(type(inner) is dict and set(inner)<= {'title','content','display_url'} and inner.get('content')==sc['content'] and inner.get('display_url')==url,'CONTROL_NESTED_CHANGED')
    body=sc['content'].encode();v=parse(body,1024**2);need(type(v) is dict,'CONTROL_PROVIDER_BODY');return v

def control_read_plan(plan,published_commit):
    need(type(published_commit) is str and re.fullmatch('[0-9a-f]{40}',published_commit),'ACTUAL_PUBLISHED_COMMIT_REQUIRED')
    prefix='https://api.github.com/repos/'+plan['context']['repository']
    urls={'ref':prefix+'/git/ref/heads/'+plan['branch'],'commit':prefix+'/git/commits/'+published_commit,
      'tree':prefix+'/git/trees/'+plan['expected_tree_sha']+'?recursive=1'}
    for i,(_,r) in enumerate(sorted(plan['files'].items())):urls['blob'+str(i)]=prefix+'/git/blobs/'+r['git_blob_sha']
    urls['closing_ref']=urls['ref']
    return [dict(kind=k,tool=TOOL,arguments={'url':url}) for k,url in urls.items()]

def receive_control(s,received,plan,published_commit,results,body,now_ms):
    validate_control(s,received,body,now_ms)
    need(plan['receiving']==desc(encode(received['receipt'])) and plan['context']==received['context'],'CONTROL_RECEIVING_JOIN')
    req=requirements(s,received);need(req['path'] in plan['files'] and plan['files'][req['path']]['sha256']==sha(body),'ACTUAL_CONTROL_BODY_JOIN')
    calls=control_read_plan(plan,published_commit);need(set(results)=={r['kind'] for r in calls} and sum(map(len,results.values()))<=MAX_JOURNAL,'CONTROL_FULL_RESULT_POPULATION')
    provider={r['kind']:unwrap_control(results[r['kind']],r['arguments']['url']) for r in calls}
    need(sum(len(encode(v)) for v in provider.values())<=1024**2,'CONTROL_METADATA_AGGREGATE')
    ref=provider['ref'];commit=provider['commit'];tree=provider['tree']
    need(ref==provider['closing_ref'] and ref.get('ref')=='refs/heads/'+plan['branch'] and ref.get('object',{}).get('type')=='commit' and ref['object'].get('sha')==published_commit
      and commit.get('sha')==published_commit and commit.get('tree',{}).get('sha')==plan['expected_tree_sha']
      and type(commit.get('parents')) is list and len(commit['parents'])==1 and commit['parents'][0].get('sha')==plan['parent_sha'],'CONTROL_COMMIT_PARENT_REF_JOIN')
    need(tree.get('sha')==plan['expected_tree_sha'] and tree.get('truncated') is False and type(tree.get('tree')) is list,'CONTROL_TREE_BOUND')
    expected={};prefixes=set()
    for n,r in plan['files'].items():
        expected[n]=('blob','100644',r['git_blob_sha'],r['bytes']);parts=n.split('/')
        prefixes.update('/'.join(parts[:i]) for i in range(1,len(parts)))
    rows={}
    for r in tree['tree']:
        n=r.get('path');need(type(n) is str and n not in rows,'CONTROL_TREE_DUPLICATE');rows[n]=r
    need(set(rows)==set(expected)|prefixes,'CONTROL_EXACT_TREE_POPULATION')
    for n,r in rows.items():
        if n in prefixes:need(r.get('type')=='tree' and r.get('mode')=='040000' and type(r.get('sha')) is str and re.fullmatch('[0-9a-f]{40}',r['sha']),'CONTROL_TREE_DIRECTORY')
        else:need((r.get('type'),r.get('mode'),r.get('sha'),r.get('size'))==expected[n],'CONTROL_EXACT_LEAF')
    for i,(n,r) in enumerate(sorted(plan['files'].items())):
        raw=r['body_utf8'].encode();need(s.V.blob(provider['blob'+str(i)],65536)==raw and desc(raw)=={'bytes':r['bytes'],'sha256':r['sha256']},'CONTROL_ACTUAL_BLOB_BODY')
    if received['phase']=='tools':
        s.H.check_control(dict(ref=ref,commit=commit,tree=tree,blob=provider['blob0'],closing_ref=provider['closing_ref']),body,s.binding)
    return dict(schema='dg16.root-control-body-receiving.v1',authority='NONE',phase=received['phase'],context=received['context'],root_body=desc(body),
      published_commit=published_commit,control_parent=plan['parent_sha'],control_tree=plan['expected_tree_sha'],artifact_receiving=plan['receiving'],
      full_actual_tool_results={k:desc(v) for k,v in sorted(results.items())},validated_unix_ms=now_ms,authentication_boundary=AUTH,
      host_consumption_observed=False,effect_grant=False,original_awards=[])

def waiting_refs_plan(s):
    prefix='https://api.github.com/repos/'+s.P.REPOSITORY+'/git/ref/heads/'
    return [dict(name=n,tool=TOOL,arguments={'url':prefix+b},required_ref='refs/heads/'+b,required_sha=p,absent_ref='IMMEDIATE_HOST_REFUSAL') for n,b,p in (
      ('tools',s.binding['host_tools']['control_branch'],s.binding['host_tools']['control_parent']),
      ('cipher',s.binding['control_branch'],s.binding['control_parent']))]

def receive_waiting_refs(s,results):
    calls=waiting_refs_plan(s);need(set(results)=={r['name'] for r in calls},'WAITING_REF_RESULTS')
    for r in calls:
        v=unwrap_control(results[r['name']],r['arguments']['url']);need(v.get('ref')==r['required_ref'] and v.get('object',{}).get('type')=='commit' and v['object'].get('sha')==r['required_sha'],'WAITING_REF_EXACT_PARENT')
    return dict(schema='dg16.root-prelaunch-waiting-refs-receiving.v1',authority='NONE',results={k:desc(v) for k,v in results.items()},
      tool_and_cipher_refs_observed=True,host_launch_granted=False,host_revision_requires_separate_independent_review=True,g3_control_branch=s.G.CONTROL_BRANCH,authentication_boundary=AUTH,original_awards=[])


def precore_validator():
    """Use the exact author's pure validators; never run emitter or wrapper code."""
    raw=read(LANE/'author/precore_projection_snapshot.py',65536);need(sha(raw)==PRECORE_SOURCE_SHA,'PRECORE_INTERFACE_CHANGED')
    tree=ast.parse(raw);allowed={'precore_need','carrier_refusal','precore_validate'};nodes=[]
    for n in tree.body:
        if isinstance(n,ast.Import) or (isinstance(n,ast.Assign) and all(isinstance(t,ast.Name) and t.id in ('PRECORE_CODES','CARRIER_REFUSAL_CODES') for t in n.targets)) or (isinstance(n,ast.FunctionDef) and n.name in allowed):nodes.append(n)
    scope={};exec(compile(ast.Module(body=nodes,type_ignores=[]),'bound-public-refusal-validator','exec'),scope)
    need(allowed<=set(scope),'PRECORE_VALIDATOR_POPULATION');return scope['precore_validate']

def job_log_plan(s,ctx,complete_jobs_result):
    """Plan one supported log read for the unique actual attempt job."""
    s.context(ctx);_,jobs=s.B.unwrap_tool_result(complete_jobs_result,s.endpoint(ctx,1,'jobs'),kind='jobs')
    need(jobs.get('total_count')==1 and type(jobs.get('jobs')) is list and len(jobs['jobs'])==1,'LOG_SINGLE_JOB')
    job=jobs['jobs'][0];integer(job.get('id'),1)
    need(job.get('run_id')==int(ctx['run_id']) and type(job.get('run_attempt')) is int and job['run_attempt']==1 and job.get('name')==ctx['job_name'] and job.get('head_sha')==ctx['workflow_commit'],'LOG_JOB_JOIN')
    return dict(tool='mcp__codex_apps__github_fetch_workflow_job_logs',arguments=dict(repo_full_name=ctx['repository'],job_id=job['id']))

def receive_logs(s,ctx,results,now_ms):
    """Receive complete actual job logs; an absent record never implies success.

    Full original result descriptors remain bound. Credential-bearing log lines
    are omitted before local retention, explicitly recorded as a redaction.
    """
    s.context(ctx);integer(now_ms,1,10**16)
    need(set(results)=={'run','attempt','jobs','workflow','logs'} and sum(map(len,results.values()))<=MAX_JOURNAL,'LOG_FULL_RESULT_POPULATION')
    snapshot={}
    for k in ('run','attempt','jobs','workflow'):
        _,snapshot[k]=s.B.unwrap_tool_result(results[k],s.endpoint(ctx,1,k),kind=k,context=ctx,workflow_sha256=s.binding['workflow_sha256'])
    need(len(encode(snapshot))<=s.P.MAX_METADATA,'LOG_METADATA_BOUND')
    joined,_=execution_join(s,snapshot,ctx,now_ms,('in_progress','completed'))
    call=job_log_plan(s,ctx,results['jobs']);raw=results['logs'];v=parse(raw)
    need(type(v) is dict and set(v)<={'content','structuredContent','isError','_meta'} and v.get('isError') is False,'LOG_COMPLETE_TOOL_RESULT')
    meta=v.get('_meta',{});need(type(meta) is dict and not any(meta.get(k) for k in ('truncated','isTruncated','partial','hasMore')),'LOG_TRUNCATED')
    sc=v.get('structuredContent');need(type(sc) is dict and set(sc)=={'content'} and type(sc['content']) is str,'SUPPORTED_LOG_RESULT_SHAPE')
    text=sc['content'];need(len(text.encode())<=2*1024**2,'LOG_TEXT_BOUND')
    validate=precore_validator();records=[];malformed=[]
    for number,line in enumerate(text.splitlines(),1):
        line=line.lstrip('\ufeff');payload=re.sub(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,9})?Z ', '',line)
        if 'dg16.precore-refusal.v1' not in payload:continue
        try:
            body=payload.encode();need(len(body)<=4096,'PRECORE_RECORD_BOUND');record=parse(body,4096);validate(record,record.get('phase'))
        except (ValueError,TypeError,KeyError):malformed.append(dict(line=number,descriptor=desc(payload.encode())));continue
        records.append(dict(line=number,body=desc(body),record=record));need(len(records)<=16,'PRECORE_RECORD_COUNT')
    omitted=[]
    def redact(value,path=''):
        if type(value) is dict:return {k:redact(x,path+'/'+k) for k,x in value.items()}
        if type(value) is list:return [redact(x,path+'/'+str(i)) for i,x in enumerate(value)]
        if type(value) is str:
            out=[]
            for i,line in enumerate(value.splitlines(keepends=True),1):
                if re.search(r'(?i)(https?://|sig=|token=|signature=)',line):
                    omitted.append(dict(field=path,line=i,descriptor=desc(line.encode())));out.append('[URL_OR_CREDENTIAL_LINE_OMITTED]\n')
                else:out.append(line)
            return ''.join(out)
        return value
    retained=redact(v)
    return dict(schema='dg16.root-precore-log-receiving.v1',authority='NONE',context=ctx,provider=joined,log_call=call,
      actual_tool_results={k:desc(b) for k,b in results.items()},retained_log_result=retained,omitted_lines=omitted,records=records,malformed_record_lines=malformed,
      observation='REFUSAL_RECORD_OBSERVED' if records else 'NO_VALID_PRECORE_REFUSAL_RECORD_OBSERVED',
      precore_validator_sha256=PRECORE_SOURCE_SHA,host_r2_final_binding=s.sources['phase']['sha256'],host_independent_review_seal=s.sources['host_independent_review_seal']['sha256'],
      authentication_boundary=AUTH,log_result_endpoint_asserted_by_actual_root_tool_history=True,
      success_inferred=False,absence_proves_no_effect=False,cleanup_inferred=False,automatic_retry=False,effect_grant=False,original_awards=[])

def bounded_stdin(maximum):
    """No file copy of an ephemeral download result. Root may pipe it here."""
    import sys
    need(not sys.stdin.isatty(),'PIPE_REQUIRED_FOR_EPHEMERAL_TOOL_RESULT')
    b=sys.stdin.buffer.read(maximum+1);need(len(b)<=maximum,'STDIN_BOUND');return b

def main():
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='cmd',required=True)
    x=sub.add_parser('start');x.add_argument('phase',choices=PHASES);x.add_argument('context');x.add_argument('directory')
    x=sub.add_parser('reserve');x.add_argument('directory');x.add_argument('kind',choices=ORDER)
    x=sub.add_parser('retain');x.add_argument('directory');x.add_argument('kind',choices=ORDER)
    x=sub.add_parser('body');x.add_argument('directory');x.add_argument('archive')
    x=sub.add_parser('receive');x.add_argument('directory');x.add_argument('--initial');x.add_argument('--actual-root-decision')
    x=sub.add_parser('requirements');x.add_argument('directory');x.add_argument('--initial');x.add_argument('--actual-root-decision')
    sub.add_parser('prelaunch-plan')
    a=p.parse_args();s=Sources()
    if a.cmd=='start':v=Session.create(Path(a.directory),s,a.phase,parse(read(Path(a.context)))).plan
    elif a.cmd=='prelaunch-plan':v=dict(authority='NONE',required_existing_waiting_refs=waiting_refs_plan(s),g3_control_branch=s.G.CONTROL_BRANCH,root_effects_authorized=False)
    else:
        session=Session(Path(a.directory),s)
        if a.cmd=='reserve':v=session.reserve(a.kind)
        elif a.cmd=='retain':v=session.retain(a.kind,bounded_stdin(MAX_RESULT))
        elif a.cmd=='body':v=session.body(read(Path(a.archive),PHASES[session.plan['phase']][2]))
        else:
            previous=None
            if a.initial:
                old=Session(Path(a.initial),s);old_receipt=parse(read(old.path/'RECEIVING.json'));previous=old.receive(old_receipt['observed_unix_ms'],save=False)
                need(encode(previous['receipt'])==encode(old_receipt),'INITIAL_RECEIPT_CHANGED')
            actual_root_raw=read(Path(a.actual_root_decision),8192) if a.actual_root_decision else None
            if a.cmd=='receive':v=session.receive(previous=previous,actual_root_raw=actual_root_raw)['receipt']
            else:
                saved=parse(read(session.path/'RECEIVING.json'));got=session.receive(saved['observed_unix_ms'],previous=previous,save=False,actual_root_raw=actual_root_raw)
                need(encode(got['receipt'])==encode(saved),'RECEIVING_CHANGED');v=requirements(s,got)
    import sys
    sys.stdout.buffer.write(encode(v))

if __name__=='__main__':
    try:main()
    except BaseException as e:
        import sys
        # Never echo exception text: an untrusted provider body could contain a URL.
        sys.stderr.write('DG16_ROOT_RECEIVER_REFUSED '+type(e).__name__+'\n');raise SystemExit(1)
