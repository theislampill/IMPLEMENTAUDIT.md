"""Fixed one-attempt operator. Never imports a canonical product or executes the oracle."""
import base64
from datetime import datetime
import hashlib
import os
from pathlib import Path
import re
import resource
import selectors
import signal
import stat
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
sys.path.insert(0,str(Path(__file__).resolve().parent))
from contract import (AUTH, BASE, CARRIER, CONTROL, FILES, HELD, LIVE, MAX_CONTROL, MAX_ZIP, OWNER,
                      PREFIX, REPO, TRIGGER, WORKFLOW, admit_result, complete_after_omission, b64, binary, control_data,
                      decode, digest, need, regular, sha, template_digest, validate_composition, wire)

PYTHON='/usr/bin/python3.12'
GIT='/usr/bin/git'
BASH='/usr/bin/bash'
SETUP='fixtures/controller-initialization/author_checkpoint.py'
PACKAGE='scripts/package-contract.py'
SKILLS='skills/implementaudit/scripts/'
OWNER_COMMANDS={'decide','open','return','admit-current','complete'}
DIR=Path(__file__).resolve().parent
STAGE_BUDGET={'open':450,'hold':1500,'finish':265,'terminal':45}
PUBLIC_FIELDS=('GITHUB_REPOSITORY','GITHUB_RUN_ID','GITHUB_RUN_ATTEMPT','GITHUB_SHA','GITHUB_JOB','GITHUB_REF',
               'GITHUB_EVENT_NAME','GITHUB_ACTOR_ID','RUNNER_OS','RUNNER_ARCH','RUNNER_ENVIRONMENT','ImageOS','ImageVersion')

def iso_epoch(s):
    return int(datetime.fromisoformat(s.replace('Z','+00:00')).timestamp())
def compact_digest(obj):
    return 'sha256:'+sha(wire(obj))
def augmented(obj):
    return dict(obj,digest=compact_digest(obj))
def fixed_ancestors(target):
    result=[]
    path=Path(target)
    need(path==path.resolve(strict=True), 'selected system path aliases')
    for node in [path,*path.parents]:
        st=node.lstat()
        need(st.st_uid==0 and not (st.st_mode&0o022) and
             (stat.S_ISDIR(st.st_mode) or (node==path and stat.S_ISREG(st.st_mode))), 'system ownership/mode '+str(node))
        result.append(dict(path=str(node),uid=st.st_uid,mode=oct(st.st_mode),dev=st.st_dev,ino=st.st_ino))
    return result
def provider_path(s):
    return urllib.parse.quote(s,safe='/')
def identity_oid(x):
    need(type(x) is str and re.fullmatch('[a-f0-9]{40}',x),'invalid Git OID')
    return x
class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,*args):
        raise ValueError('provider redirect refused')

class Job:
    def __init__(self,stage):
        self.stage=stage
        self.env={k:os.environ[k] for k in PUBLIC_FIELDS if k in os.environ}
        need(self.env.get('GITHUB_REPOSITORY')==REPO and self.env.get('GITHUB_RUN_ATTEMPT')=='1' and
             self.env.get('GITHUB_JOB')=='canonical' and self.env.get('GITHUB_REF')=='refs/heads/'+TRIGGER and
             self.env.get('GITHUB_EVENT_NAME')=='push' and self.env.get('RUNNER_ENVIRONMENT')=='github-hosted' and
             self.env.get('RUNNER_OS')=='Linux' and self.env.get('ImageOS')=='ubuntu24' and self.env.get('ImageVersion'),
             'provider environment')
        self.run=self.env['GITHUB_RUN_ID']
        need(re.fullmatch('[1-9][0-9]{0,18}',self.run),'invalid run id')
        self.operator=identity_oid(self.env['GITHUB_SHA'])
        self.workspace=Path(os.environ['GITHUB_WORKSPACE']).absolute()
        temp=Path(os.environ['RUNNER_TEMP']).absolute()
        need(temp==temp.resolve(strict=True) and self.workspace==self.workspace.resolve(strict=True)
             and DIR==self.workspace/PREFIX,'physical operator custody')
        self.root=temp/'dg17-m10'
        if stage=='open':
            self.root.mkdir(mode=0o700)
        st=self.root.lstat()
        need(self.root.resolve(strict=True)==self.root and st.st_uid==os.geteuid() and
             stat.S_ISDIR(st.st_mode) and (st.st_mode&0o077)==0,'private working directory')
        self.source=self.root/'source'
        self.product=self.root/'executing'
        self.store=self.root/'binding-store'
        self.controller='m10-'+self.run
        self.cutoff=time.monotonic()+STAGE_BUDGET[stage]
        self.pins=decode(regular(DIR/'pins.json',65536))
        self.evidence=self.saved('observations') if (self.root/'observations.json').exists() else []
        self.d=self.saved('context') if (self.root/'context.json').exists() else {}
        self.steps=self.saved('owner-commands') if (self.root/'owner-commands.json').exists() else []
        self.scope=None
    def save(self,name,value):
        target=self.root/(name+'.json')
        tmp=target.with_suffix('.stage')
        with tmp.open('xb') as fp:
            fp.write(wire(value)+b'\n')
        os.replace(tmp,target)
    def saved(self,name):
        return decode(regular(self.root/(name+'.json'),8*1024*1024))
    def observe(self,event,**fields):
        self.evidence.append(dict(stage=self.stage,event=event,unix=int(time.time()),**fields))
        self.save('observations',self.evidence)
        # Independent provider log joins carry identities only. No raw process stream is logged.
        print(wire(dict(schema='dg17.m10.command-bookend.v1',stage=self.stage,event=event,
                        index=len(self.evidence)-1,observation_sha256=sha(wire(self.evidence[-1])))).decode(),flush=True)
    def remaining(self):
        seconds=self.cutoff-time.monotonic()
        need(seconds>0,'stage time budget exhausted')
        return seconds
    def command(self,label,args,cwd=None,expected=0,public=False):
        """Bound the entire subprocess group. Capture only a finite combined stdout/stderr."""
        cwd=cwd or self.product
        seconds=min(self.remaining(),55)
        limit=1024*1024
        args=list(map(str,args))
        def limits():
            resource.setrlimit(resource.RLIMIT_CPU,(40,41))
            resource.setrlimit(resource.RLIMIT_AS,(1024**3,1024**3))
            resource.setrlimit(resource.RLIMIT_FSIZE,(384*1024**2,384*1024**2))
            resource.setrlimit(resource.RLIMIT_CORE,(0,0))
        env={'PATH':'/usr/bin:/bin','LC_ALL':'C','HOME':str(self.root/'private-home'),
             'TMPDIR':str(self.root/'private-tmp'),'PYTHONDONTWRITEBYTECODE':'1',
             'IMPLEMENTAUDIT_PYTHON':PYTHON,'GIT_CONFIG_NOSYSTEM':'1','GIT_CONFIG_GLOBAL':'/dev/null',
             'GIT_TERMINAL_PROMPT':'0','GIT_OPTIONAL_LOCKS':'0'}
        begin=time.monotonic()
        proc=subprocess.Popen(args,cwd=cwd,stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.PIPE,
                              env=env,start_new_session=True,preexec_fn=limits)
        streams=[bytearray(),bytearray()]
        try:
            with selectors.DefaultSelector() as poll:
                for idx,pipe in enumerate((proc.stdout,proc.stderr)):
                    poll.register(pipe,selectors.EVENT_READ,idx)
                while poll.get_map():
                    rem=seconds-(time.monotonic()-begin)
                    need(rem>0,'command wall limit '+label)
                    for obj,_ in poll.select(rem):
                        chunk=os.read(obj.fd,32768)
                        if not chunk:
                            poll.unregister(obj.fileobj)
                            continue
                        need(len(chunk)+sum(map(len,streams))<=limit,'command output cap '+label)
                        streams[obj.data].extend(chunk)
            rc=proc.wait(timeout=max(.01,seconds-(time.monotonic()-begin)))
        except BaseException:
            try:
                os.killpg(proc.pid,signal.SIGKILL)
            except ProcessLookupError:
                pass
            proc.wait()
            raise
        finally:
            for pipe in (proc.stdout,proc.stderr):
                pipe.close()
            # Raw output is private, including failed streams. Public diagnostics use identity + bounded known streams.
            seq=len(self.evidence)
            for i,raw in enumerate(streams):
                (self.root/f'private-{seq}-{i}').write_bytes(raw)
            obs=dict(argv=args,pid=proc.pid,exit_code=proc.returncode,elapsed_ms=int((time.monotonic()-begin)*1000),
                     stdout_sha256=sha(streams[0]),stderr_sha256=sha(streams[1]),
                     stdout_bytes=len(streams[0]),stderr_bytes=len(streams[1]))
            if public:
                # Public command set has no environment, store-file read or credential-printing command.
                obs['stderr']=bytes(streams[1][:1200]).decode('utf-8','replace')
            if label in {'claim-fresh','checkpoint-author','inspect-initialization','activate','current-controller',
                         'invalidate','resume','verify-receipt','require-current','final-require-current',
                         'unselected-materializer','store-init'}:
                need(sum(map(len,streams))<=65536,'public initializer stream bound')
                obs.update(stdout_b64=b64(streams[0]),stderr_b64=b64(streams[1]))
            if proc.returncode!=expected and public and sum(map(len,streams))<=65536:
                obs.update(failed_stdout_b64=b64(streams[0]),failed_stderr_b64=b64(streams[1]))
            self.observe(label,**obs)
        need(rc==expected,'subprocess exit '+label+' '+str(rc))
        return bytes(streams[0])
    def git(self,*args,cwd=None):
        return self.command('git-'+args[0],[GIT,*args],cwd=cwd).decode().strip()
    def py(self,label,script,*args,**opts):
        return self.command(label,[PYTHON,'-I','-S','-B',script,*args],public=True,**opts)
    def claim(self,label,*args):
        return self.command(label,[BASH,self.product/SKILLS/'claim-run.sh',*args],public=True).decode().strip()
    def binding(self,cmd,*args):
        return decode(self.py('store-'+cmd,self.product/SKILLS/'host-session-binding.py','--store',self.store,cmd,*args))
    def api(self,path,absent=False):
        need(path.startswith('/') and not path.startswith('//') and '..' not in path,'provider API path')
        url='https://api.github.com/repos/'+REPO+path
        req=urllib.request.Request(url,headers={'Authorization':'Bearer '+os.environ['DG17_READER'],
            'Accept':'application/vnd.github+json','X-GitHub-Api-Version':'2022-11-28','User-Agent':'dg17-m10-receiver'})
        start=time.monotonic()
        bounds=[8,self.remaining()]
        if self.stage=='hold' and 'deadline' in self.d:
            bounds.extend([self.d['deadline']-time.time(),self.d['opened_monotonic']+1500-time.monotonic()])
        deadline=min(bounds)
        need(deadline>0,'provider operation after deadline')
        signal.setitimer(signal.ITIMER_REAL,deadline)
        try:
            with urllib.request.build_opener(urllib.request.ProxyHandler({}),NoRedirect()).open(req,timeout=deadline) as res:
                body=res.read(1024*1024+1)
        except urllib.error.HTTPError as error:
            if absent and error.code==404:
                return None
            raise ValueError('provider HTTP '+str(error.code)) from None
        finally:
            signal.setitimer(signal.ITIMER_REAL,max(.001,self.cutoff-time.monotonic()))
        need(time.monotonic()-start<=9 and len(body)<=1024*1024,'provider read bound')
        return decode(body)
    def ref(self,branch,absent=False):
        row=self.api('/git/ref/heads/'+provider_path(branch),absent)
        if row is None:
            return None
        need(row['ref']=='refs/heads/'+branch and row['object']['type']=='commit','wrong provider ref')
        return identity_oid(row['object']['sha'])
    def live(self):
        run=self.api('/actions/runs/'+self.run)
        need(run['id']==int(self.run) and run['run_attempt']==1 and run['head_sha']==self.operator and
             run['head_branch']==TRIGGER and run['repository']['full_name']==REPO and run['path']==WORKFLOW and
             run['event']=='push' and run['status']=='in_progress' and run['actor']['id']==int(self.env['GITHUB_ACTOR_ID'])
             and run['triggering_actor']['id']==run['actor']['id'] and self.ref(TRIGGER)==self.operator,'run binding')
        jobs=self.api('/actions/runs/'+self.run+'/attempts/1/jobs?per_page=100')
        need(jobs['total_count']==len(jobs['jobs'])==1,'unexpected jobs')
        job=jobs['jobs'][0]
        need(job['run_id']==int(self.run) and job['name']=='canonical' and job['status']=='in_progress'
             and job['head_sha']==self.operator and 'ubuntu-24.04' in job['labels'],'live numeric job')
        scope=dict(repository=REPO,run_id=int(self.run),attempt=1,job_id=job['id'],job_key='canonical',
                   operator=self.operator,source=BASE,started_at=job['started_at'])
        if 'provider' in self.d:
            need(self.d['provider']==scope,'mixed job/attempt')
        self.observe('provider-current',scope=scope,workflow_id=run['workflow_id'])
        return scope
    def composition(self):
        wf=regular(self.workspace/WORKFLOW,65536)
        need(wf.count(LIVE.encode())==1 and HELD.encode() not in wf,'operator held')
        bundle=decode(regular(DIR/'composition.json',1024*1024))
        template=template_digest(DIR,wf.replace(LIVE.encode(),HELD.encode()))
        # Runtime rereads committed composition. Root separately authenticates the external appointment/grant.
        a,subjects=validate_composition(bundle,template,sha(wire(bundle['appointment'])))
        need(a['root_actor_id']==self.env['GITHUB_ACTOR_ID'],'foreign trigger actor')
        return bundle,a,subjects
    def source_check(self):
        pins=self.pins
        need(pins['commit']==BASE and pins['repository']==REPO and sha(regular(DIR/'fixed_oracle.py',8192))==pins['oracle'],
             'source/oracle pins')
        for checkout in (self.source,self.product):
            need(self.git('rev-parse','HEAD',cwd=checkout)==BASE and
                 self.git('rev-parse','HEAD^{tree}',cwd=checkout)==pins['tree'] and
                 checkout==checkout.resolve(strict=True) and (checkout/'.git').is_dir() and
                 not (checkout/'.git').is_symlink(),'fresh physical checkout pin')
        tracked=self.git('status','--porcelain','--untracked-files=all',cwd=self.source)
        need(not tracked,'reference source checkout dirty')
        for name,row in pins['selected'].items():
            for checkout in (self.source,self.product):
                raw=regular(checkout/name,1024*1024)
                need(len(raw)==row['bytes'] and sha(raw)==row['sha256'] and
                     oct((checkout/name).lstat().st_mode)[2:]==row['mode'],'selected source drift '+name)
    def assembled(self):
        self.source_check()
        extra=self.pins['materialized']
        for name,row in extra.items():
            path=self.product/name
            need(sha(regular(path,1024*1024))==row['sha256'] and oct(path.lstat().st_mode)[2:]==row['mode'],
                 'materialization drift '+name)
        need(not self.git('diff','--name-only','HEAD','--'),'tracked product drift')
        # Include gitignored additions. The maintained namespace lock and this actual run are the only
        # coordination exceptions after claim. Before claim the exact addition set is the 14 peer members.
        status=self.command('assembly-untracked',[GIT,'ls-files','--others','-z'])
        names={n.decode() for n in status.split(b'\0') if n}
        run=self.d.get('run_root','')
        inputs={'m10-subject/'+k for k in self.d.get('subjects',[])}
        if not run:
            need(names==set(extra),'initial materializer delta differs from the exact 14 files')
        else:
            need(set(extra)|inputs <= names and all(n in extra or n in inputs or n.startswith(run+'/')
                or n=='.IMPLEMENTAUDIT/.r36-locks/namespace.gate' for n in names),'unexpected worktree addition')
        if inputs:
            subject_dir=self.product/'m10-subject'
            if subject_dir.exists():
                need(not subject_dir.is_symlink() and {p.name for p in subject_dir.iterdir()}==set(self.d['subjects']),
                     'unexpected subject path')
        self.observe('assembly-bookend',extra={k:row['sha256'] for k,row in extra.items()},untracked=sorted(names))
    def file_record(self,label,ref):
        oid=self.git('rev-parse','--verify',ref)
        raw=self.command('canonical-blob-'+label,[GIT,'cat-file','blob',identity_oid(oid)])
        self.save(label,dict(ref=ref,oid=oid,raw=b64(raw)))
        return oid,raw
    def prepare_operator(self):
        need(self.git('rev-list','--parents','-n','1',self.operator,cwd=self.workspace).split()==[self.operator,BASE],
             'operator sole parent')
        need(not self.git('status','--porcelain','--untracked-files=all',cwd=self.workspace),'operator checkout dirty')
        delta=self.git('diff','--no-renames','--name-status',BASE,self.operator,'--',cwd=self.workspace)
        expected={WORKFLOW,PREFIX+'composition.json',*(PREFIX+n for n in FILES)}
        need(set(delta.splitlines())=={'A\t'+p for p in expected},'operator additive population')
        for p in expected:
            row=self.git('ls-tree',self.operator,'--',p,cwd=self.workspace)
            need(row.startswith('100644 blob ') and row.endswith('\t'+p),'operator blob mode')
            blob=regular(self.workspace/p,1024*1024)
            need(row.split()[2]==hashlib.sha1(b'blob '+str(len(blob)).encode()+b'\0'+blob).hexdigest(),
                 'operator blob readback')
        bundle,a,subjects=self.composition()
        return bundle,a,subjects
    def host_snapshot(self):
        os_data=Path('/etc/os-release').read_text()
        need('ID=ubuntu' in os_data.splitlines() and 'VERSION_ID="24.04"' in os_data.splitlines(),'Ubuntu image')
        tools={p:fixed_ancestors(p) for p in ('/','/usr/bin',PYTHON,BASH,GIT)}
        need(Path(sys.executable).resolve()==Path(PYTHON),'unrecognized Python')
        self.observe('host-observer',env=self.env,tools=tools,pid=os.getpid(),ppid=os.getppid(),
                     uname=list(os.uname()),effective_uid=os.geteuid(),job_directory=str(self.root),
                     job_directory_identity=[self.root.stat().st_dev,self.root.stat().st_ino])
        return tools
    def root_claim(self,purpose):
        output=self.claim('claim-fresh','--controller',self.controller,'dg17-m10')
        need(re.fullmatch(r'\.IMPLEMENTAUDIT/runs/dg17-m10-[A-Za-z0-9]{6}',output),'claimed run root')
        self.d['run_root']=output
        self.py('checkpoint-author',self.product/SETUP,'--repo',self.product,'--source',self.product,
                '--run-root',output,'--purpose',purpose,'--next-action',purpose)
        inspect=decode(self.claim('inspect-initialization','--inspect-controller-initialization',self.controller,
                                  '--run-root',output).encode())
        need(inspect['controller']==self.controller and not inspect['missing_files'] and
             inspect['prepared_source_head']==BASE and inspect['current_controller_oid'] is None,'pending initialization')
        act=decode(self.claim('activate','--activate-controller',self.controller,'--run-root',output,
                             '--expected-initialization',inspect['initialization_token']).encode())
        need(act['status']=='BOUND_ELIGIBLE_FOR_NORMAL_CURRENTNESS' and
             act['initialization_token']==inspect['initialization_token'],'fresh activation result')
        self.save('initialization',dict(inspection=inspect,activation=act))
        current=self.claim('current-controller','--current-controller',self.controller).split('\t')
        need(len(current)==4 and current[:3]==[self.controller,str(self.product),str(self.product/output)]
             and current[3]==inspect['claim_id'],'new controller identity')
        event=self.d['event']
        invalidated=self.claim('invalidate','--invalidate-continuity',self.controller,'--boundary','new-session','--event',event)
        iref,ioid=invalidated.split('@')
        got,raw=self.file_record('invalidation',iref)
        need(got==ioid and raw.decode().rstrip('\n').split('\t')[-2:]==['new-session',event],'boundary provenance')
        c_oid,_=self.file_record('controller','refs/implementaudit/controllers/'+self.controller)
        book={}
        for name in ('STATE.md','ROADMAP.md'):
            raw=regular(self.product/output/name,128*1024)
            book[name]=dict(bytes=len(raw),sha256=sha(raw),raw=b64(raw))
        self.save('checkpoint',book)
        receipt=self.claim('resume','--resume-controller',self.controller,'--boundary','new-session','--epoch','G0001')
        need(re.fullmatch('refs/implementaudit/continuity-receipts/'+self.controller+'/G0001@[0-9a-f]{40}',receipt)
             and self.claim('verify-receipt','--verify-resume-receipt',receipt)==receipt and
             self.claim('require-current','--require-current-continuity',self.controller)==receipt,
             'fresh continuity receipt')
        roid,rraw=self.file_record('continuity',receipt.split('@')[0])
        need(roid==receipt.split('@')[1],'receipt ref readback')
        need(act['controller_oid']==c_oid,'activation controller ref readback')
        self.d.update(receipt=receipt,claim=current[3],run_root=output,controller_oid=c_oid)
    def route(self,cmd,*args,expected=0):
        i=len(self.steps)
        sequence=('decide','open','return','admit-current','complete','admit-current')
        need(i<len(sequence) and sequence[i]==cmd and cmd in OWNER_COMMANDS,'duplicate or out-of-order owner call')
        # Record intent before calling. A partial failure cannot authorize retry.
        self.steps.append(cmd)
        self.save('owner-commands',self.steps)
        full=[*self.route_args(),*args]
        raw=self.py(cmd,self.product/SKILLS/'route-transaction.py',cmd,*full,expected=expected)
        result=decode(raw)
        self.save('owner-'+str(i),dict(command=cmd,exit_code=expected,raw=b64(raw)))
        need(result['schema']=='implementaudit.route-transaction-result.v1','route result schema')
        return result
    def route_args(self):
        return ['--controller',self.controller,'--store',self.store,*self.host_args(),
                '--binding-generation',self.d['generation']]
    def host_args(self):
        return ['--host-id',self.d['host'],'--host-session-id',self.d['session']]
    def custody(self):
        return ['--controller-id',self.controller,'--claim-id',self.d['claim'],'--explicit-run-root',
                self.product/self.d['run_root'],'--repository-identity',self.product,
                '--git-common-directory-identity',self.product/'.git','--worktree-identity',self.product,
                '--continuity-generation','G0001','--continuity-receipt',self.d['receipt']]
    def stage_open(self):
        for name in ('private-home','private-tmp'):
            (self.root/name).mkdir(mode=0o700)
        tools=self.host_snapshot()
        bundle,a,subjects=self.prepare_operator()
        scope=self.live()
        need(self.ref(CONTROL,absent=True) is None,'pre-existing control ref')
        recent=self.api('/actions/runs?head_sha='+self.operator+'&branch='+provider_path(TRIGGER)+'&event=push&per_page=100')
        need(recent['total_count']==len(recent['workflow_runs'])<=100 and
             [r['id'] for r in recent['workflow_runs'] if r['path']==WORKFLOW]==[int(self.run)],
             'fresh unique workflow allocation')
        self.d['provider']=scope
        self.d['tools']=tools
        self.d['event']='gh-job-'+self.run+'-1-'+str(scope['job_id'])+'-'+str(iso_epoch(scope['started_at']))
        self.d['host']='github-actions.'+self.env['RUNNER_ARCH']+'.'+os.uname().nodename
        self.d['session']=REPO+'/'+self.run+'/1/'+str(scope['job_id'])
        self.d['subjects']=sorted(subjects)
        self.save('context',self.d)
        for checkout in (self.source,self.product):
            checkout.mkdir(mode=0o700)
            self.git('init','--quiet',cwd=checkout)
            self.git('fetch','--quiet','--no-tags','--depth=1',self.workspace.as_uri(),BASE,cwd=checkout)
            self.git('checkout','--quiet','--detach',BASE,cwd=checkout)
        self.source_check()
        need(not self.git('status','--porcelain','--untracked-files=all'),'target initially dirty')
        self.py('unselected-materializer',self.source/PACKAGE,'--repo-root',self.source,
                '--materialize-c02-source',self.product,cwd=self.source)
        doc=self.pins['manual_document']
        row=self.pins['materialized'][doc]
        material=regular(self.source/row['path'],32768)
        need(row['path']=='source-peers/native-runtime/'+doc and row['mode']=='100644' and
             sha(material)==row['sha256'] and len(material)==row['bytes'],'supplemental reference pin')
        with (self.product/doc).open('xb') as fp:
            fp.write(material)
            os.fchmod(fp.fileno(),0o644)
        self.assembled()
        subject_dir=self.product/'m10-subject'
        subject_dir.mkdir(mode=0o700)
        for name,raw in subjects.items():
            with (subject_dir/name).open('xb') as fp:
                fp.write(raw)
        self.root_claim(a['purpose'])
        started=self.binding('init','--owner-id',a['store_owner'])
        need(started['status']=='READY' and started['owner_id']==a['store_owner'],'store owner')
        bound=self.binding('bind','--owner-id',a['store_owner'],*self.host_args(),*self.custody(),
                           '--activation-event-id',self.d['event'],'--activation-receipt',
                           compact_digest(dict(provider=scope,event=self.d['event'],process=self.evidence[0])))
        need(bound['status']=='BOUND' and bound['host_activation_proven'] is False and
             bound['binding']['controller_id']==self.controller and bound['binding']['claim_id']==self.d['claim']
             and bound['binding']['applicable_continuity_receipt']==self.d['receipt'],'binding producer')
        self.save('binding',bound)
        self.d['generation']=bound['binding']['binding_generation']
        self.save('context',self.d)
        # Include all selected operational/subject bytes and the exact peer manifests, as real relative paths.
        inputs={p:row['sha256'] for p,row in self.pins['selected'].items()}
        inputs.update({p:r['sha256'] for p,r in self.pins['materialized'].items()})
        inputs.update({'m10-subject/'+k:sha(raw) for k,raw in subjects.items()})
        request=dict(schema='implementaudit.route-decision-request.v1',predicate_version='R0033.route-predicate.v1',
            boundary=augmented(dict(kind='new-session',event_id=self.d['event'])),scope=augmented(dict(identity=a['purpose'])),
            action=augmented(dict(identity='review-'+a['subject_manifest'],argv=['route-trigger','IMMUTABLE_INDEPENDENT_REVIEW'],
                                  **{'class':'REQUIRED_INTERNAL_CHILD'})),
            inputs=[dict(identity=k,path=k,digest='sha256:'+v) for k,v in sorted(inputs.items())])
        self.save('request',request)
        req=['--request',self.root/'request.json']
        decided=self.route('decide',*req,'--expected-record','none')
        need(decided['status']=='DECIDED' and decided['decision']=='REQUIRED' and
             decided['route_state']=='UNSATISFIED' and decided['advance_allowed'] is False,'genuine REQUIRED')
        ids={k:decided[k] for k in ('obligation_id','route_transaction_id')}
        for val in ids.values():
            need(type(val) is str and val.startswith('sha256:'),'route identity')
            digest(val[7:])
        ref='refs/implementaudit/route-decisions/'+self.controller
        oid,_=self.file_record('required',ref)
        need(oid==decided['record_oid'],'REQUIRED readback')
        event='review-'+a['subject_manifest']
        attributed=self.binding('validate-event',*self.host_args(),'--binding-generation',self.d['generation'],*self.custody(),
                '--event-id',event,'--obligation-id',ids['obligation_id'],'--route-transaction-id',ids['route_transaction_id'])
        need(attributed['status']=='ATTRIBUTED' and all(attributed[k]==v for k,v in ids.items()),'source attribution')
        self.save('attribution',attributed)
        packet=dict(schema='implementaudit.route-packet.v1',target_identity='audit-assess',**ids,source_event=dict(
            schema='implementaudit.source-event.v1',source_identity=event,body=a['purpose'],kind='one-shot-action',
            reactivation=dict(reopen=False,target_changed=False,invalidating_evidence=False),provenance=dict(
            schema='implementaudit.source-event-provenance.v1',event_id=event,host_correlation_id=attributed['correlation_id'])))
        self.save('packet',packet)
        result=self.route('open',*req,'--expected-record',oid,'--packet',self.root/'packet.json','--logical-task',a['reviewer_task'])
        ooid,raw=self.file_record('opening',ref)
        need(result['status']=='CHILD_OPEN' and result['route_state']=='OPEN' and ooid==result['record_oid'] and
             all(result[k]==v for k,v in ids.items()),'OPEN readback')
        delivery=decode(raw)['lifecycle']['delivery']
        need(delivery==result['delivery'] and binary(delivery['child']['bytes_b64'])==
             regular(self.product/'skills/audit-assess/SKILL.md',128*1024) and
             binary(delivery['packet']['bytes_b64'])==regular(self.root/'packet.json',65536),'OPEN delivery identities')
        now=int(time.time())
        self.d.update(ids=ids,route_ref=ref,open_oid=ooid,packet_digest=delivery['packet']['digest'],
                      child_digest=delivery['child']['digest'],deadline=min(now+1500,iso_epoch(scope['started_at'])+45*60-500),
                      opened_at=now,opened_monotonic=time.monotonic())
        need(self.d['deadline']>now,'no remaining hold budget')
        self.save('context',self.d)
        self.assembled()
        self.live()
        self.publication('open',bundle)
    def record_set(self,phase):
        names=['controller','invalidation','continuity','initialization','checkpoint','binding','attribution','request',
               'packet','required','opening','owner-0','owner-1']
        if phase=='final':
            names+=['received-carrier','return-record','complete-record','owner-2','owner-3','owner-4','owner-5','oracle-input',
                    'terminal-status','failure']
        return {n:self.saved(n) for n in names if (self.root/(n+'.json')).exists()}
    def publication(self,phase,bundle=None):
        public=self.root/('public-'+phase)
        need(not public.exists(),'duplicate publication')
        records=self.record_set(phase)
        data={'evidence.json':wire(dict(schema='dg17.m10.'+phase+'.v1',provider=self.d.get('provider'),
             actual_context=self.d,observations=self.evidence,owner_commands=self.steps,records=records,
             oracle_sha256=self.pins['oracle'],external_authentication_required=True))}
        if phase=='open':
            need('opening' in records and self.steps==['decide','open'],'premature OPEN artifact')
            data.update({'subject-manifest.json':binary(bundle['subject_manifest']),'subject.zip':binary(bundle['subject_zip']),
                         'appointment.json':wire(bundle['appointment'])})
        # upload-artifact uses compression 0. Reserve >64 KiB for ZIP directory/metadata overhead.
        need(sum(map(len,data.values()))<=MAX_ZIP-65536,'public artifact size cap')
        public.mkdir(mode=0o700)
        for name,body in data.items():
            (public/name).write_bytes(body)
    def tree(self,oid):
        identity_oid(oid)
        result=self.api('/git/trees/'+oid)
        need(result['sha']==oid and result['truncated'] is False,'incomplete carrier tree')
        rows={}
        for row in result['tree']:
            name=row['path']
            need(name not in rows and '/' not in name and name not in ('.','..'),'bad tree member')
            rows[name]=(row['mode'],row['type'],identity_oid(row['sha']),row.get('size'))
        return rows
    def carrier(self,oid):
        control=self.api('/git/commits/'+identity_oid(oid))
        parent=self.api('/git/commits/'+self.operator)
        need(control['sha']==oid and parent['sha']==self.operator and [r['sha'] for r in control['parents']]==[self.operator],
             'control sole parent')
        before=self.tree(parent['tree']['sha'])
        after=self.tree(control['tree']['sha'])
        dirname='dg17-m10-control'
        need(dirname not in before and dirname in after,'control folder')
        mode,kind,tid,_=after.pop(dirname)
        need(after==before and (mode,kind)==('040000','tree'),'control-only tree delta')
        rows=self.tree(tid)
        need(set(rows)==set(CARRIER) and all(m=='100644' and k=='blob' and type(n) is int and n>0
             for m,k,_,n in rows.values()) and sum(r[3] for r in rows.values())<=MAX_CONTROL,'control tree population or budget')
        out={}
        for name,(_,_,bid,size) in rows.items():
            blob=self.api('/git/blobs/'+bid)
            need(blob['sha']==bid and blob['encoding']=='base64' and blob['size']==size,'provider blob metadata')
            raw=base64.b64decode(blob['content'].replace('\n',''),validate=True)
            need(len(raw)==size and hashlib.sha1(b'blob '+str(size).encode()+b'\0'+raw).hexdigest()==bid,'provider blob identity')
            out[name]=raw
        return out,[r['sha'] for r in control['parents']]
    def check_artifact(self,id_,hex_digest):
        digest(hex_digest)
        need(type(id_) is int and id_>0,'missing OPEN artifact ID')
        item=self.api('/actions/artifacts/'+str(id_))
        need(item['id']==id_ and item['name']=='dg17-m10-open-'+self.run+'-1' and
             item['workflow_run']['id']==int(self.run) and item['workflow_run']['head_sha']==self.operator
             and item['expired'] is False and 0<item['size_in_bytes']<=MAX_ZIP and
             item['digest']=='sha256:'+hex_digest,'OPEN artifact provider identity')
    def before_deadline(self):
        need(time.time()<self.d['deadline'] and time.monotonic()-self.d['opened_monotonic']<1500,
             'hold deadline expired')
    def stage_hold(self):
        need(self.steps==['decide','open'],'hold stage order')
        self.before_deadline()
        scope=self.live()
        bundle,a,_=self.composition()
        open_id=int(os.environ['DG17_OPEN_ID'])
        opened_hash=os.environ['DG17_OPEN_DIGEST'].removeprefix('sha256:')
        self.check_artifact(open_id,opened_hash)
        expected={**scope,**self.d['ids'],'authority':AUTH,'control_ref':'refs/heads/'+CONTROL,
              'open_oid':self.d['open_oid'],'open_artifact_id':open_id,'open_artifact_sha256':opened_hash,
              'packet_digest':self.d['packet_digest'],'child_digest':self.d['child_digest'],'owner_sha256':OWNER,
              'deadline':self.d['deadline'],'reviewer':a['reviewer'],'reviewer_task':a['reviewer_task'],
              'purpose':a['purpose'],'subject_manifest':a['subject_manifest'],'subject_zip':a['subject_zip'],
              'appointment_sha256':sha(wire(a))}
        while True:
            self.before_deadline()
            oid=self.ref(CONTROL,absent=True)
            if oid:
                break
            time.sleep(max(0,min(8,self.remaining(),self.d['deadline']-time.time())))
        population,parents=self.carrier(oid)
        reread=self.ref(CONTROL)
        self.before_deadline()
        control_data(population,expected,self.operator,parents,oid,reread,int(time.time()))
        self.live()
        self.before_deadline()
        self.save('received-carrier',dict(oid=oid,parents=parents,bindings=expected,
                      bytes={k:b64(v) for k,v in population.items()},received_at=int(time.time())))
        for name in CARRIER[:2]:
            with (self.root/name).open('xb') as fp:
                fp.write(population[name])
        self.observe('immutable-control-readback',oid=oid,expected=expected)
    def stage_finish(self):
        need(self.steps==['decide','open'],'finish stage order')
        received=self.saved('received-carrier')
        self.before_deadline()
        scope=self.live()
        data,parents=self.carrier(received['oid'])
        control_data(data,received['bindings'],self.operator,parents,received['oid'],self.ref(CONTROL),int(time.time()))
        self.before_deadline()
        for n in CARRIER[:2]:
            need(data[n]==regular(self.root/n,MAX_CONTROL),'carrier changed before return')
        _,a,subjects=self.composition()
        self.assembled()
        for name,raw in subjects.items():
            need(regular(self.product/'m10-subject'/name,len(raw))==raw,'reviewed subject drift')
        need(self.host_snapshot()==self.d['tools'],'host tool identity drift')
        need(self.binding('lookup',*self.host_args())==self.saved('binding'),'binding changed')
        ref=self.d['route_ref']
        req=['--request',self.root/'request.json']
        need(self.git('rev-parse','--verify',ref)==self.d['open_oid'],'stale OPEN ref')
        returned=self.route('return',*req,'--expected-record',self.d['open_oid'],'--return',self.root/'child-return.json')
        roid,rraw=self.file_record('return-record',ref)
        need(returned['route_state']=='RETURNED' and returned['record_oid']==roid,'RETURNED readback')
        def observe_arm(positive,oid):
            before=self.git('rev-parse','--verify',ref)
            expected=0 if positive else 3
            payload=self.route('admit-current',expected=expected)
            after=self.git('rev-parse','--verify',ref)
            if positive:
                admit_result(expected,payload,before,after,oid,True,self.d['ids'])
            return dict(exit_code=expected,payload=payload,before_record_oid=before,after_record_oid=after,
                        source_sha256=sha(regular(self.product/SKILLS/'route-transaction.py',500000)),provider_scope=scope)
        negative=observe_arm(False,roid)
        # Only one path reaches complete, after the observed request-free rejection and stable live identity.
        def complete():
            self.live()
            return self.route('complete',*req,'--expected-record',roid,'--packet',self.root/'packet.json',
                              '--return',self.root/'child-return.json','--decision',self.root/'decision.json')
        done=complete_after_omission(negative,roid,self.d['ids'],scope,complete)
        coid,craw=self.file_record('complete-record',ref)
        need(coid!=roid and done['record_oid']==coid and done['idempotent'] is False and
             done['route_state']=='SATISFIED','genuine completion')
        positive=observe_arm(True,coid)
        lifecycle=decode(rraw)['lifecycle']
        satisfied=decode(craw)['lifecycle']
        raw_packet=regular(self.root/'packet.json',65536)
        for item in (lifecycle,satisfied):
            need(binary(item['child_return']['bytes_b64'])==data['child-return.json']
                 and binary(item['delivery']['packet']['bytes_b64'])==raw_packet,'canonical packet/return join')
        need(lifecycle['governor_decision'] is None and binary(satisfied['governor_decision']['bytes_b64'])==
             data['decision.json'],'canonical Root decision join')
        joins=dict(returned_packet_digest=lifecycle['delivery']['packet']['digest'],
                   satisfied_packet_digest=satisfied['delivery']['packet']['digest'],
                   returned_child_return_digest=lifecycle['child_return']['digest'],
                   satisfied_child_return_digest=satisfied['child_return']['digest'],
                   satisfied_governor_return_digest=decode(data['decision.json'])['return_digest'])
        self.assembled()
        need(self.binding('lookup',*self.host_args())==self.saved('binding') and
             self.claim('final-require-current','--require-current-continuity',self.controller)==self.d['receipt']
             and self.ref(CONTROL)==received['oid'],'final custody readback')
        self.live()
        self.save('oracle-input',dict(negative=negative,positive=positive,return_result_record_oid=roid,
                 complete_result_record_oid=coid,canonical_record_joins=joins,recorded_owner_commands=self.steps,
                 open_provider_scope=self.d['provider']))
        self.save('terminal-status',dict(status='STRUCTURAL_OBSERVATIONS_COLLECTED',authority='NONE'))
    def stage_terminal(self):
        if not (self.root/'terminal-status.json').exists():
            self.save('terminal-status',dict(status='INCOMPLETE',authority='NONE'))
        try:
            self.publication('final')
        except ValueError as exc:
            if str(exc)!='public artifact size cap':
                raise
            # The upload is explicitly incomplete. Never issue an oracle input on this branch.
            where=self.root/'public-final'
            where.mkdir(mode=0o700)
            (where/'evidence.json').write_bytes(wire(dict(schema='dg17.m10.nonverdict.v1',
                reason='final artifact over cap',authority='NONE',provider=self.d.get('provider'),
                dispositions=[self.saved('terminal-status')],observations_sha256=sha(wire(self.evidence)))))
            raise
def main():
    need(len(sys.argv)==2 and sys.argv[1] in STAGE_BUDGET,'unknown operator phase')
    job=Job(sys.argv[1])
    def expired(_signal,_frame):
        raise TimeoutError('operator wall ceiling reached')
    signal.signal(signal.SIGALRM,expired)
    try:
        if job.stage=='hold':
            job.before_deadline()
            job.cutoff=min(job.cutoff,job.d['opened_monotonic']+1500,
                           time.monotonic()+job.d['deadline']-time.time())
        signal.setitimer(signal.ITIMER_REAL,max(.001,job.cutoff-time.monotonic()))
        getattr(job,'stage_'+job.stage)()
    except BaseException as exc:
        # Preserve only controlled exception messages, never raw HTTP headers or the inherited environment.
        name=type(exc).__name__
        detail=str(exc)[:500] if isinstance(exc,ValueError) else name
        job.save('failure',dict(stage=job.stage,exception=name,detail=detail,unix=int(time.time())))
        print('DG17 stage stopped:',job.stage,name,detail,file=sys.stderr)
        raise SystemExit(1)
    finally:
        signal.setitimer(signal.ITIMER_REAL,0)
if __name__=='__main__':
    main()
