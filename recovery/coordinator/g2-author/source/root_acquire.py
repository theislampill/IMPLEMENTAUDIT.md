"""Pure supported-tool plans and outcome-neutral artifact acquisition records.

Only the root runtime executes the returned tool plan. The separate resolver
receives an actual no-echo download result and performs at most one body GET.
"""
from pathlib import Path
import argparse,datetime,hashlib,json,os,re,stat,sys,time,urllib.parse
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import root_common as K

ROOT_BINDING_SHA=None
COMMON_SHA=None
TOOL='mcp__codex_apps__github_fetch'
DOWNLOAD='mcp__codex_apps__github_download_workflow_artifact'
ORDER=('run','attempt','jobs','commit','workflow','artifacts','download','closing-run','closing-artifacts')
JOURNAL_NAMES={'PLAN.json','BODY_GET_INTENT.json','BODY_GET_OUTCOME.json','ARTIFACT.zip','PROVIDER_RECEIVING.json','PUBLIC_METADATA.json'}|{
  kind+suffix for kind in ORDER for suffix in ('.INTENT.json','.RESULT.json','.READY.json','.REJECTED.json')}
need=K.need;parse=K.parse;encode=K.encode;desc=K.desc;read=K.read
diagnostic_disposition=K.diagnostic_disposition

def endpoint(ctx,kind):
    K.context(ctx);need(kind in ORDER and kind!='download','FIXED_PROVIDER_KIND')
    base='https://api.github.com/repos/'+ctx['repository'];run=ctx['run_id']
    paths={'run':'/actions/runs/'+run,'attempt':'/actions/runs/'+run+'/attempts/1',
      'jobs':'/actions/runs/'+run+'/attempts/1/jobs?per_page=100&page=1',
      'commit':'/git/commits/'+ctx['workflow_commit'],
      'workflow':'/contents/'+ctx['workflow_path']+'?ref='+ctx['workflow_commit'],
      'artifacts':'/actions/runs/'+run+'/artifacts?per_page=100',
      'closing-run':'/actions/runs/'+run,'closing-artifacts':'/actions/runs/'+run+'/artifacts?per_page=100'}
    return base+paths[kind]

def unwrap(raw,url,kind,binding):
    v=parse(raw);need(type(v) is dict and set(v)<={'content','structuredContent','isError','_meta'} and v.get('isError') is False,'TOOL_RESULT_SHAPE')
    meta=v.get('_meta',{});need(type(meta) is dict and set(meta)<={'truncated','isTruncated','partial','hasMore'}
      and all(type(x) is bool and not x for x in meta.values()),'TOOL_RESULT_INCOMPLETE')
    sc=v.get('structuredContent');need(type(sc) is dict and set(sc)<={'content','title','modified_date','url','display_url','display_title','structuredContent'}
      and sc.get('url')==url and sc.get('display_url')==url and type(sc.get('content')) is str,'ACTUAL_TOOL_ENDPOINT')
    if 'structuredContent' in sc:
        inner=sc['structuredContent'];need(type(inner) is dict and set(inner)<={'title','content','display_url'}
          and inner.get('content')==sc['content'] and inner.get('display_url')==url,'NESTED_RESULT_CHANGED')
    body=sc['content'].encode('utf-8');need(0<len(body)<=K.METADATA_MAX,'PROVIDER_BODY_BOUND')
    if kind=='workflow':
        need(len(body)<=65536 and K.sha(body)==binding['workflow_sha256'],'EXACT_SUPPORTED_WORKFLOW_TEXT')
        return {'representation':'SUPPORTED_TOOL_COMPLETE_TEXT','body':desc(body),'actual_tool_result':desc(raw),
          'derived_git_blob_sha1':hashlib.sha1(b'blob '+str(len(body)).encode()+b'\0'+body).hexdigest(),'endpoint':url}
    value=parse(body);need(type(value) is dict,'PROVIDER_BODY_OBJECT');return value

def artifacts(value,ctx,binding):
    K.context(ctx);need(type(value) is dict and set(value)=={'total_count','artifacts'} and type(value['artifacts']) is list
      and K.integer(value['total_count'],0,100) and value['total_count']==len(value['artifacts']),'COMPLETE_RUN_ARTIFACT_LIST')
    result={};ids=set();names={K.artifact_name(role,ctx):role for role in K.ROLE_CAPS}
    for row in value['artifacts']:
        need(type(row) is dict and K.integer(row.get('id'),1) and row['id'] not in ids,'ARTIFACT_ID_POPULATION');ids.add(row['id'])
        name=row.get('name');need(type(name) is str and name in names and names[name] not in result,'ARTIFACT_ROLE_POPULATION');role=names[name]
        relation=row.get('workflow_run');need(type(relation) is dict and type(relation.get('id')) is int
          and str(relation['id'])==ctx['run_id'] and relation.get('head_sha')==ctx['workflow_commit']
          and relation.get('head_branch')==ctx['branch'],'ARTIFACT_RUN_BINDING')
        need(row.get('expired') is False and K.integer(row.get('size_in_bytes'),1,K.ROLE_CAPS[role])
          and type(row.get('digest')) is str and re.fullmatch('sha256:[0-9a-f]{64}',row['digest']),'ARTIFACT_DESCRIPTOR')
        result[role]=row
    return result

def download_reference(raw,artifact_id,file_name):
    """Validate all transient structure before constructing a fixed safe note.

    No arbitrary key, file ID, URL, or unstructured completion text is copied
    into retained notes. The original complete raw-result descriptor survives.
    """
    need(K.integer(artifact_id,1) and type(file_name) is str and re.fullmatch('[A-Za-z0-9._-]{1,256}',file_name),'FIXED_DOWNLOAD_IDENTITY')
    value=parse(raw);need(type(value) is dict and set(value)<={'content','structuredContent','isError','_meta'}
      and value.get('isError') is False,'DOWNLOAD_TOOL_RESULT')
    meta=value.get('_meta',{});need(type(meta) is dict and set(meta)<={'truncated','isTruncated','partial','hasMore'}
      and all(type(x) is bool and not x for x in meta.values()),'DOWNLOAD_INCOMPLETE')
    content=value.get('content');need(type(content) is list and len(content)<=32 and all(type(x) is dict and set(x)=={'type','text'}
      and x['type']=='text' and type(x['text']) is str for x in content),'DOWNLOAD_CONTENT_SHAPE')
    sc=value.get('structuredContent');need(type(sc) is dict,'DOWNLOAD_STRUCTURE')
    rows=[sc]+([sc['structuredContent']] if 'structuredContent' in sc else []);ids=[];urls=[]
    for level,row in enumerate(rows):
        need(type(row) is dict and set(row)<={'artifact_id','file_name','mime_type','file_uri','file_id','download_url','structuredContent'}
          and (level==0 or 'structuredContent' not in row) and type(row.get('artifact_id')) is int and row['artifact_id']==artifact_id
          and row.get('file_name')==file_name and row.get('mime_type')=='application/zip','DOWNLOAD_ARTIFACT_JOIN')
        uri=row.get('file_uri');need(type(uri) is dict and set(uri)=={'file_id','file_name','mime_type','download_url'}
          and uri['file_name']==file_name and uri['mime_type']=='application/zip' and type(uri['file_id']) is str
          and re.fullmatch('file_[0-9a-f]{32}',uri['file_id']),'DOWNLOAD_REFERENCE_SHAPE')
        ids.append(uri['file_id']);urls.append(uri['download_url'])
        if 'file_id' in row:need(row['file_id']==uri['file_id'],'DOWNLOAD_DUPLICATE_ID')
        if 'download_url' in row:urls.append(row['download_url'])
    need(len(set(ids))==1 and urls and all(type(u) is str and u==urls[0] for u in urls),'DOWNLOAD_DUPLICATE_REFERENCE')
    url=urls[0];need(0<len(url.encode())<=16384 and not any(ord(x)<33 or ord(x)==127 for x in url),'EPHEMERAL_REFERENCE_BOUND')
    parts=urllib.parse.urlsplit(url)
    need(parts.scheme=='https' and parts.username is None and parts.password is None and not parts.fragment
      and parts.port in (None,443) and type(parts.hostname) is str
      and re.fullmatch(r'sdmntpr[a-z0-9-]+\.oaiusercontent\.com',parts.hostname)
      and parts.path.startswith('/') and bool(parts.query),'FIXED_EPHEMERAL_STORAGE_FAMILY')
    note=dict(schema='dg16.g2-safe-download-result.v1',authority='NONE',artifact_id=artifact_id,archive_name=file_name,
      mime_type='application/zip',actual_tool_result=desc(raw),content_blocks=len(content),nested_structure_present=len(rows)==2,
      signed_url_retained=False,file_reference_identifier_retained=False,unstructured_text_retained=False,
      authentication_boundary=K.AUTH)
    return note,url

def unix_ms(value):
    need(type(value) is str and len(value)<=40,'PROVIDER_TIME');d=datetime.datetime.fromisoformat(value.replace('Z','+00:00'))
    need(d.tzinfo is not None,'PROVIDER_TIME_ZONE');return int(d.timestamp()*1000)

def verify_snapshot(rows,ctx,role,binding,observed_ms):
    K.context(ctx);need(set(rows)=={'run','attempt','jobs','commit','workflow','artifacts'},'PROVIDER_SNAPSHOT_POPULATION')
    wanted='in_progress' if role=='live' else 'completed';repo=None
    for name in ('run','attempt'):
        row=rows[name];need(type(row.get('id')) is int and str(row['id'])==ctx['run_id'] and type(row.get('run_attempt')) is int
          and row['run_attempt']==1 and row.get('event')=='push' and row.get('head_sha')==ctx['workflow_commit']
          and row.get('head_branch')==ctx['branch'] and row.get('path')==ctx['workflow_path'] and row.get('status')==wanted
          and row.get('repository',{}).get('full_name')==ctx['repository'] and row.get('head_repository',{}).get('full_name')==ctx['repository'], 'ACTUAL_RUN_BINDING')
        identity=row['repository'].get('id');need(K.integer(identity,1) and row['head_repository'].get('id')==identity
          and (repo is None or repo==identity),'PROVIDER_REPOSITORY_ID');repo=identity
        need(unix_ms(row['run_started_at'])<=observed_ms,'RUN_TIME_BINDING')
    jobs=rows['jobs'];need(type(jobs.get('total_count')) is int and jobs['total_count']==1
      and type(jobs.get('jobs')) is list and len(jobs['jobs'])==1,'SINGLE_EXACT_JOB')
    job=jobs['jobs'][0];need(K.integer(job.get('id'),1) and type(job.get('run_id')) is int and str(job['run_id'])==ctx['run_id']
      and type(job.get('run_attempt')) is int and job['run_attempt']==1 and job.get('head_sha')==ctx['workflow_commit']
      and job.get('name')==ctx['job_name'] and job.get('status')==wanted,'ACTUAL_JOB_BINDING')
    started=unix_ms(job['started_at']);need(started<=observed_ms,'JOB_TIME_BINDING')
    commit=rows['commit'];need(commit.get('sha')==ctx['workflow_commit'] and commit.get('tree',{}).get('sha')==binding['final_tree']
      and [r.get('sha') for r in commit.get('parents',[])]==[K.SOURCE_COMMIT],'ACTUAL_COMMIT_TREE_PARENT')
    population=artifacts(rows['artifacts'],ctx,binding);need(role in population,'EXACT_ROLE_ABSENT');selected=population[role]
    need(selected['workflow_run'].get('repository_id')==repo and selected['workflow_run'].get('head_repository_id')==repo
      and started<=unix_ms(selected['created_at'])<=observed_ms,'ARTIFACT_PROVENANCE_TIME')
    return selected,dict(repository_id=repo,job_id=job['id'],run_status=rows['run']['status'],run_conclusion=rows['run'].get('conclusion'),
      job_status=job['status'],job_conclusion=job.get('conclusion'),roles=sorted(population))

class Session:
    """One local immutable journal per selected role; never executes a tool."""
    def __init__(self,path,binding,*,components=None):
        self.path=Path(path).absolute();need(self.path.resolve(strict=True)==self.path,'SESSION_PHYSICAL_PATH')
        self.binding=binding;self.modules=components;self.plan=parse(read(self.path/'PLAN.json',16384,True));K.context(self.plan['context'])
        need(self.plan['schema']=='dg16.g2-supported-acquisition-plan.v1' and self.plan['binding']==desc(K.encode(binding))
          and self.plan['role'] in K.ROLE_CAPS and self.plan['automatic_retry'] is False,'SESSION_BINDING')
        self.context=self.plan['context'];self.role=self.plan['role'];self._dir=K.identity(self.path.lstat());self.bound()
    @classmethod
    def create(cls,path,binding,ctx,role,components=None):
        K.context(ctx);need(role in K.ROLE_CAPS,'ROLE');path=Path(path).absolute()
        need(path.parent.resolve(strict=True)==path.parent and not os.path.lexists(path),'FRESH_SESSION_REQUIRED');path.mkdir(mode=0o700)
        value=dict(schema='dg16.g2-supported-acquisition-plan.v1',authority='NONE',binding=desc(K.encode(binding)),context=ctx,role=role,
          order=list(ORDER),automatic_retry=False,authentication_boundary=K.AUTH)
        fd=os.open(path/'PLAN.json',os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,0o600)
        try:
            data=encode(value);need(os.write(fd,data)==len(data),'PLAN_WRITE');os.fsync(fd)
        finally:os.close(fd)
        cls.sync(path);return cls(path,binding,components=components)
    @staticmethod
    def sync(path):
        fd=os.open(path,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC)
        try:os.fsync(fd)
        finally:os.close(fd)
    def bound(self,additional=0,entries=0):
        info=self.path.lstat();need(K.identity(info)==self._dir and info.st_uid==os.geteuid() and stat.S_IMODE(info.st_mode)==0o700,'SESSION_CUSTODY')
        metadata=0;body=0;count=0
        for path in self.path.iterdir():
            need(path.name in JOURNAL_NAMES,'JOURNAL_POPULATION');s=path.lstat();count+=1
            need(stat.S_ISREG(s.st_mode) and s.st_nlink==1 and s.st_uid==os.geteuid() and stat.S_IMODE(s.st_mode)==0o600,'JOURNAL_FILE_CUSTODY')
            if path.name=='ARTIFACT.zip':body+=s.st_size;need(body<=K.ROLE_CAPS[self.role],'ARCHIVE_ROLE_BOUND')
            else:metadata+=s.st_size
        need(count+entries<=48 and metadata+additional<=K.JOURNAL_MAX and metadata+body+additional<=K.BODY_TOTAL_MAX,'JOURNAL_ALLOCATION_BOUND')
    def write(self,name,raw):
        need(type(name) is str and name in JOURNAL_NAMES and name!='ARTIFACT.zip'
          and type(raw) is bytes and 0<len(raw)<=K.METADATA_MAX,'JOURNAL_WRITE_BOUND');self.bound(len(raw),1)
        fd=os.open(self.path/name,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,0o600)
        try:
            offset=0
            while offset<len(raw):count=os.write(fd,raw[offset:]);need(count>0,'JOURNAL_WRITE');offset+=count
            os.fsync(fd)
        finally:os.close(fd)
        self.sync(self.path);need(read(self.path/name,K.METADATA_MAX,True)==raw,'JOURNAL_READBACK');self.bound()
    def ready(self,kind):
        need(kind in ORDER,'FIXED_KIND');intent=read(self.path/(kind+'.INTENT.json'),16384,True)
        result=read(self.path/(kind+'.RESULT.json'),K.METADATA_MAX,True);receipt=parse(read(self.path/(kind+'.READY.json'),4096,True))
        need(receipt['intent']==desc(intent) and receipt['retained_result']==desc(result),'RESULT_RECEIPT_CHANGED');return result
    def selected(self):return artifacts(unwrap(self.ready('artifacts'),endpoint(self.context,'artifacts'),'artifacts',self.binding),self.context,self.binding)[self.role]
    def reserve(self,kind):
        need(kind in ORDER,'FIXED_KIND');position=ORDER.index(kind)
        for name in ORDER[:position]:self.ready(name)
        if kind.startswith('closing-'):need((self.path/'BODY_GET_OUTCOME.json').exists(),'BODY_GET_TERMINAL_REQUIRED')
        need(not any((self.path/(kind+suffix)).exists() for suffix in ('.INTENT.json','.RESULT.json','.READY.json','.REJECTED.json')),'NO_UNCERTAIN_REPLAY')
        args={'url':endpoint(self.context,kind)} if kind!='download' else {'repo_full_name':self.context['repository'],
          'artifact_id':self.selected()['id'],'file_name':K.artifact_name(self.role,self.context)+'.zip'}
        value=dict(schema='dg16.g2-supported-call-intent.v1',authority='NONE',kind=kind,tool=DOWNLOAD if kind=='download' else TOOL,
          arguments=args,issued_unix_ms=time.time_ns()//1000000,automatic_retry=False)
        self.bound(K.METADATA_MAX+16384,3);self.write(kind+'.INTENT.json',encode(value));return value
    def retain(self,kind,raw):
        need(kind in ORDER,'FIXED_KIND');intent=parse(read(self.path/(kind+'.INTENT.json'),16384,True))
        need(not any((self.path/(kind+x)).exists() for x in ('.RESULT.json','.READY.json','.REJECTED.json')),'RESULT_NO_REPLAY')
        original=desc(raw)
        try:
            if kind=='download':safe,_=download_reference(raw,intent['arguments']['artifact_id'],intent['arguments']['file_name']);retained=encode(safe)
            else:unwrap(raw,intent['arguments']['url'],kind,self.binding);retained=raw
        except (ValueError,TypeError,KeyError,UnicodeError,OverflowError):
            self.write(kind+'.REJECTED.json',encode(dict(schema='dg16.g2-tool-result-refused.v1',authority='NONE',actual_tool_result=original,
              raw_retained=False,reason='FIXED_SHAPE_OR_BINDING_REFUSED',automatic_retry=False)));raise K.Refusal('RESULT_REFUSED_BEFORE_RETENTION')
        self.write(kind+'.RESULT.json',retained)
        self.write(kind+'.READY.json',encode(dict(intent=desc(encode(intent)),retained_result=desc(retained),actual_tool_result=original,
          retained_unix_ms=time.time_ns()//1000000)));return desc(retained)
    def receive(self,save=True):
        now=time.time_ns()//1000000
        rows={name:unwrap(self.ready(name),endpoint(self.context,name),name,self.binding) for name in ORDER[:6]}
        selected,joins=verify_snapshot(rows,self.context,self.role,self.binding,now)
        closing=unwrap(self.ready('closing-run'),endpoint(self.context,'closing-run'),'closing-run',self.binding)
        for key in ('id','run_attempt','head_sha','head_branch','event','path','status','conclusion'):
            need(type(closing.get(key)) is type(rows['run'].get(key)) and closing.get(key)==rows['run'].get(key),'CLOSING_RUN_CHANGED')
        closing_roles=artifacts(unwrap(self.ready('closing-artifacts'),endpoint(self.context,'closing-artifacts'),'closing-artifacts',self.binding),self.context,self.binding)
        opening_roles=artifacts(rows['artifacts'],self.context,self.binding)
        need(closing_roles==opening_roles and closing_roles.get(self.role)==selected,'CLOSING_ARTIFACT_POPULATION_CHANGED')
        download=parse(self.ready('download'))
        need(download['artifact_id']==selected['id'] and download['archive_name']==K.artifact_name(self.role,self.context)+'.zip'
          and download['mime_type']=='application/zip','ACTUAL_DOWNLOAD_SELECTED_ROLE_JOIN')
        outcome=parse(read(self.path/'BODY_GET_OUTCOME.json',16384,True));archive={'bytes':selected['size_in_bytes'],'sha256':selected['digest'][7:]}
        need(outcome.get('status')=='RECEIVED' and outcome.get('archive')==archive and outcome.get('body_get_attempts')==1,'BODY_NOT_COMPLETELY_RECEIVED')
        need(self.modules is not None,'BOUND_COMPONENTS_REQUIRED');F=self.modules['fs_io']
        with F.Directory(self.path) as directory,F.Input(directory,'ARTIFACT.zip',K.ROLE_CAPS[self.role],archive,private=True) as held:held.descriptor(lambda:None)
        provider=dict(schema='dg16.failed-stream-provider-binding.v1',context=self.context,artifact_id=selected['id'],
          artifact_name=selected['name'],archive=archive,expired=False) if self.role=='cipher' else None
        receipt=dict(schema='dg16.g2-actual-provider-receiving.v1',authority='NONE',role=self.role,context=self.context,
          archive=archive,artifact_id=selected['id'],provider=provider,joins=joins,
          actual_tool_results={n:desc(self.ready(n)) for n in ORDER if n!='download'},
          download_actual_result=parse(self.ready('download'))['actual_tool_result'],download_file_identifier_retained=False,
          body_outcome=desc(read(self.path/'BODY_GET_OUTCOME.json',16384,True)),observed_unix_ms=now,
          direct_artifact_endpoint_used=False,authentication_boundary=K.AUTH,automatic_retry=False,original_awards=[])
        if save:
            self.write('PROVIDER_RECEIVING.json',encode(receipt))
            if self.role!='cipher':self.write('PUBLIC_METADATA.json',encode(dict(run=rows['run'],commit=rows['commit'],artifact=selected)))
        return receipt

def main():
    need(K.digest(COMMON_SHA) and K.sha(read(HERE/'root_common.py',65536))==COMMON_SHA,'ROOT_COMMON_PIN')
    b,_=K.binding(HERE,ROOT_BINDING_SHA);mods=K.components(HERE,b)
    p=argparse.ArgumentParser();sub=p.add_subparsers(dest='command',required=True)
    a=sub.add_parser('start');a.add_argument('role',choices=K.ROLE_CAPS);a.add_argument('context');a.add_argument('directory')
    for name in ('reserve','retain','receive'):
        a=sub.add_parser(name);a.add_argument('directory')
        if name!='receive':a.add_argument('kind',choices=ORDER)
        if name=='retain':a.add_argument('actual_result')
    args=p.parse_args()
    if args.command=='start':s=Session.create(Path(args.directory),b,parse(read(Path(args.context),16384)),args.role,mods);value=s.plan
    else:
        s=Session(Path(args.directory),b,components=mods)
        if args.command=='reserve':value=s.reserve(args.kind)
        elif args.command=='retain':
            need(args.kind!='download','DOWNLOAD_REQUIRES_SEPARATE_NO_ECHO_ENTRY');value=s.retain(args.kind,read(Path(args.actual_result)))
        else:value=s.receive()
    print(json.dumps(value,sort_keys=True));return 0
if __name__=='__main__':
    try:code=main()
    except BaseException:
        print('{"status":"REFUSED_OR_INCOMPLETE","automatic_retry":false,"authority":"NONE"}');code=1
    raise SystemExit(code)
