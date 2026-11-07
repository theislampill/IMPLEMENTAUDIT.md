"""Prospective single-process D0 envelope. Inert import; no target commands.
Root must admit descriptors, publication commit and effect before run().
No producer source is present in this derivation; INPUT_PINS deliberately refuses.
"""
import builtins, copy, hashlib, json, os, signal, stat, sys, time, types
PUBLIC_NAMES=('HOSTED_CENSUS_RESULT.json','D0_RECEIVING.json','D0_ENVELOPE.json')
PRIVATE_NAMES={'D0_PRIVATE_RECEIPT.json','D0_INDEPENDENT_RECEIVER_RECEIPT.json','D0_ELIGIBILITY.json'}
LIMIT=16384
class Refusal(Exception): pass
class Deadline(BaseException): pass
CODES={'SOURCE_PIN','SOURCE_UNRESOLVED','CARRIER','CARRIER_DRIFT','INVENTORY','BINDING','HOST','OUTPUT','SCHEMA','AGGREGATE','DEADLINE','RECEIVER_UNAVAILABLE','ENVELOPE_REFUSAL'}
def need(ok,code):
    if not ok: raise Refusal(code)
def closed_error(exc):
    return str(exc) if isinstance(exc,Refusal) and str(exc) in CODES else 'ENVELOPE_REFUSAL'
def codec(x): return (json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=True,allow_nan=False)+'\n').encode('ascii')
def digest(raw): return hashlib.sha256(raw).hexdigest()
def identity(s): return tuple(getattr(s,k) for k in ('st_dev','st_ino','st_mode','st_uid','st_gid','st_nlink','st_size','st_mtime_ns','st_ctime_ns'))
def custody(s): return identity(s)[:6]
def directory(fd):
    s=os.fstat(fd)
    need(stat.S_ISDIR(s.st_mode) and stat.S_IMODE(s.st_mode)==0o700 and s.st_uid==os.geteuid() and s.st_gid==os.getegid(),'CARRIER')
    return custody(s)
def inventory(fd,names):
    found=set()
    with os.scandir(fd) as entries:
        for e in entries:
            need(e.name in names and len(found)<64,'INVENTORY');found.add(e.name)
    need(found==set(names),'INVENTORY')
def read_file(fd,name,limit,source=False):
    need('/' not in name and name not in ('.','..'),'CARRIER')
    before=os.stat(name,dir_fd=fd,follow_symlinks=False)
    need(stat.S_ISREG(before.st_mode) and before.st_nlink==1 and 0<before.st_size<=limit and before.st_uid==os.geteuid() and before.st_gid==os.getegid(),'CARRIER')
    need((stat.S_IMODE(before.st_mode)&0o022)==0 if source else stat.S_IMODE(before.st_mode)==0o600,'CARRIER')
    f=os.open(name,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC|os.O_NONBLOCK,dir_fd=fd)
    try:
        need(identity(os.fstat(f))==identity(before),'CARRIER_DRIFT')
        chunks=[];offset=0
        for _ in range(limit//65536+2):
            b=os.pread(f,min(65536,limit+1-offset),offset)
            if not b: break
            chunks.append(b);offset+=len(b);need(offset<=limit,'CARRIER')
        else: raise Refusal('CARRIER')
        need(offset==before.st_size and identity(before)==identity(os.fstat(f))==identity(os.stat(name,dir_fd=fd,follow_symlinks=False)),'CARRIER_DRIFT')
        return b''.join(chunks)
    finally:os.close(f)
def write_file(fd,name,raw):
    f=os.open(name,os.O_RDWR|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_NONBLOCK|os.O_CLOEXEC,0o600,dir_fd=fd)
    try:
        need(os.write(f,raw)==len(raw),'OUTPUT');os.fsync(f)
    finally:os.close(f)
    need(read_file(fd,name,max(len(raw),1))==raw,'OUTPUT')
def admit_file(fd,pin):
    raw=read_file(fd,pin['path'],1048576,True)
    need(len(raw)==pin['bytes'] and digest(raw)==pin['sha256'],'SOURCE_PIN');return raw

def require_pins(pins):
    need(pins.get('producer_admission_status')=='SOURCE_REVIEW_RECEIVED','SOURCE_UNRESOLVED')
    need(type(pins.get('producer')) is list and bool(pins['producer']),'SOURCE_UNRESOLVED')
    need(type(pins.get('reviewed_execution_commit')) is str,'SOURCE_UNRESOLVED')

def module(raw,name,dependencies=None):
    """No shared producer/receiver module global namespace or import search."""
    dependencies=dependencies or {};m=types.ModuleType(name)
    original=builtins.__import__
    def importer(n,*args,**kwargs):
        if n in dependencies:return dependencies[n]
        need(n.split('.')[0] in {'__future__','argparse','copy','errno','hashlib','json','os','stat','sys','re','time','types','builtins','signal'},'SOURCE_PIN')
        return original(n,*args,**kwargs)
    m.__dict__['__builtins__']={**vars(builtins),'__import__':importer}
    exec(compile(raw,'<admitted-'+name+'>','exec'),m.__dict__);return m

def aggregate(raws):need(sum(map(len,raws))<=LIMIT,'AGGREGATE')
def host_binding(w,pins,env):
    need(sys.platform=='linux' and os.getuid()==os.geteuid()!=0 and os.getgid()==os.getegid()!=0,'HOST')
    uname=os.uname();arches={'x86_64':(64,'LITTLE',62),'aarch64':(64,'LITTLE',183)}
    need(uname.machine in arches and env['RUNNER_OS']=='Linux','HOST')
    arch=arches[uname.machine]
    need(env['RUNNER_ARCH']=={'x86_64':'X64','aarch64':'ARM64'}[uname.machine],'HOST')
    need(env['GITHUB_SHA']==pins['reviewed_execution_commit'] and env['GITHUB_RUN_ATTEMPT']=='1' and env['GITHUB_JOB']=='d0_census','BINDING')
    need(env['ImageOS'] and env['ImageVersion'],'HOST')
    b={'schema':w.BINDING_SCHEMA_NAME,'operation_id':'DG17_CLAUDE_D0','run_id':env['GITHUB_RUN_ID'],'run_attempt':1,'job_id':env['GITHUB_JOB'],'host_instance_sha256':digest(codec({'nonce':os.urandom(32).hex(),'pid':os.getpid(),'start_ns':time.monotonic_ns(),'run_id':env['GITHUB_RUN_ID'],'job':env['GITHUB_JOB']})),'host_image':env['ImageOS']+'-'+env['ImageVersion'],'platform':'linux','source_commit':env['GITHUB_SHA'],'receiver_bundle_sha256':pins['receiver_bundle_sha256'],'evidence_uid':os.geteuid(),'evidence_gid':os.getegid(),'execution_uid':os.geteuid(),'execution_gid':os.getegid(),'host_arch':dict(zip(('elf_class','elf_endian','elf_machine'),arch)),**w.PINS}
    w.validate(b,w.BINDING);return b

def fallback(code):return {'schema':'dg17.claude.routing.fixed-host-census.v1','status':'INCOMPLETE_OR_REFUSED','rows':[],'private_receipt_sha256':None,'body_content_published':False,'startup_semantics_accepted':False,'native_processes_started':0,'target_commands_started':0,'source_effect_authority':'NONE','failure':code}

def private_export_check(fd,expected,private_raw,private_identity,public_raw,w,receiver):
    names=set()
    with os.scandir(fd) as entries:
        for entry in entries:
            need(entry.name in PRIVATE_NAMES and len(names)<3,'INVENTORY');names.add(entry.name)
    allowed=[{'D0_PRIVATE_RECEIPT.json'},{'D0_PRIVATE_RECEIPT.json','D0_INDEPENDENT_RECEIVER_RECEIPT.json'},PRIVATE_NAMES]
    need(names in allowed,'INVENTORY')
    need(read_file(fd,'D0_PRIVATE_RECEIPT.json',8388608)==private_raw and identity(os.stat('D0_PRIVATE_RECEIPT.json',dir_fd=fd,follow_symlinks=False))==private_identity,'CARRIER_DRIFT')
    if 'D0_INDEPENDENT_RECEIVER_RECEIPT.json' in names:
        rr=read_file(fd,'D0_INDEPENDENT_RECEIVER_RECEIPT.json',8388608);recut=w.decode(rr,8388608);w.validate(recut,receiver.RECUT_SCHEMA)
        need(recut['binding']==expected and recut['producer_private_sha256']==digest(private_raw) and recut['public_sha256']==digest(public_raw),'BINDING')
    if 'D0_ELIGIBILITY.json' in names:
        dr=read_file(fd,'D0_ELIGIBILITY.json',LIMIT);decision=w.decode(dr,LIMIT);w.validate(decision,receiver.DECISION_SCHEMA)
        need(decision['operation_binding_sha256']==digest(codec(expected)) and decision['private_receipt_sha256']==digest(private_raw) and decision['public_receipt_sha256']==digest(public_raw) and decision['independent_receipt_sha256']==digest(rr),'BINDING')

def export(fd,raws,w,schemas):
    need(set(raws)==set(PUBLIC_NAMES),'INVENTORY');aggregate(raws.values());inventory(fd,set())
    for name in PUBLIC_NAMES:
        obj=w.decode(raws[name],LIMIT);w.validate(obj,schemas[name])
        if name==PUBLIC_NAMES[0]: w.validate_public(obj,schemas[name])
    for name in PUBLIC_NAMES:write_file(fd,name,raws[name])
    inventory(fd,set(PUBLIC_NAMES))
    for name in PUBLIC_NAMES:need(read_file(fd,name,LIMIT)==raws[name],'OUTPUT')

def run(episode_fd,receiver_fd,producer_fd,pins,schemas,env):
    """All descriptors root-admitted. This call is only for an authorized hosted job.
    Returns closed code. Never logs exception objects or arbitrary private text.
    """
    try:
        require_pins(pins)
        need(digest(codec(schemas))==pins["public_envelope_schemas_sha256"],"SOURCE_PIN")
    except Exception:return 2
    need(signal.getitimer(signal.ITIMER_REAL)==(0.0,0.0),'HOST')
    start=time.monotonic();old=signal.getsignal(signal.SIGALRM)
    def alarm(*_):raise Deadline()
    signal.signal(signal.SIGALRM,alarm);signal.setitimer(signal.ITIMER_REAL,180)
    pfd=outfd=None
    try:
        original=directory(episode_fd);inventory(episode_fd,set())
        sources={p['path']:admit_file(receiver_fd,p) for p in pins['receiver']}
        source_ids={('r',p['path']):identity(os.stat(p['path'],dir_fd=receiver_fd,follow_symlinks=False)) for p in pins['receiver']}
        need(digest(codec(pins['receiver']))==pins['receiver_bundle_sha256'],'SOURCE_PIN')
        producers={p['path']:admit_file(producer_fd,p) for p in pins['producer']}
        source_ids.update({('p',p['path']):identity(os.stat(p['path'],dir_fd=producer_fd,follow_symlinks=False)) for p in pins['producer']})
        w=module(sources['d0_wire.py'],'d0_receiver_wire')
        receiver=module(sources['d0_receiver.py'],'d0_receiver',{'d0_wire':w})
        producer_dependencies={}
        if 'schema_data.py' in producers:
            producer_dependencies['schema_data']=module(producers['schema_data.py'],'d0_producer_schema')
        producer=module(producers['d0_producer.py'],'d0_producer',producer_dependencies)
        b=host_binding(w,pins,env);expected=copy.deepcopy(b)
        schema_raw=sources['HOSTED_CENSUS_RESULT.schema.json']
        need(digest(schema_raw)==w.PINS['public_schema_sha256'],'SOURCE_PIN')
        need(schemas[PUBLIC_NAMES[0]]==json.loads(schema_raw),'SCHEMA')
        os.mkdir('private',0o700,dir_fd=episode_fd);os.mkdir('public',0o700,dir_fd=episode_fd)
        need(directory(episode_fd)[:5]==original[:5],'CARRIER_DRIFT')
        original=directory(episode_fd)
        pfd=os.open('private',os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=episode_fd)
        outfd=os.open('public',os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=episode_fd)
        private_custody=directory(pfd);public_custody=directory(outfd)
        decision=None;failure=None;raw=None;producer_verified=False
        try:
            raw=producer.produce(episode_fd,copy.deepcopy(expected),schema_raw)
            public=w.decode(raw,LIMIT);w.validate_public(public,schemas[PUBLIC_NAMES[0]])
            inventory(pfd,{'D0_PRIVATE_RECEIPT.json'})
            private_identity=identity(os.stat('D0_PRIVATE_RECEIPT.json',dir_fd=pfd,follow_symlinks=False))
            private_raw=read_file(pfd,'D0_PRIVATE_RECEIPT.json',8388608)
            need(identity(os.stat('D0_PRIVATE_RECEIPT.json',dir_fd=pfd,follow_symlinks=False))==private_identity,'CARRIER_DRIFT')
            private=w.decode(private_raw,8388608);w.validate(private,w.PRIVATE_SCHEMA)
            need(private['binding']==expected,'BINDING')
            rebuilt,_=w.derive_public(private,digest(private_raw));need(w.public_projection_matches(public,rebuilt),'BINDING')
            producer_verified=True
            decision=receiver.receive(episode_fd,raw,copy.deepcopy(expected),schema_raw)
            inventory(pfd,PRIVATE_NAMES)
            need(read_file(pfd,'D0_PRIVATE_RECEIPT.json',8388608)==private_raw and identity(os.stat('D0_PRIVATE_RECEIPT.json',dir_fd=pfd,follow_symlinks=False))==private_identity,'CARRIER_DRIFT')
            dr=read_file(pfd,'D0_ELIGIBILITY.json',LIMIT);rr=read_file(pfd,'D0_INDEPENDENT_RECEIVER_RECEIPT.json',8388608)
            need(w.decode(dr,LIMIT)==decision,'OUTPUT');w.validate(decision,receiver.DECISION_SCHEMA)
            recut=w.decode(rr,8388608);w.validate(recut,receiver.RECUT_SCHEMA)
            need(recut['binding']==expected and decision['operation_binding_sha256']==digest(codec(expected)) and decision['private_receipt_sha256']==digest(private_raw) and decision['public_receipt_sha256']==digest(raw) and decision['independent_receipt_sha256']==digest(rr),'BINDING')
            if decision['observation']!='RECEIVED_FIXED_HOST_INPUTS':failure='RECEIVER_UNAVAILABLE'
        except Deadline:
            raise
        except Exception:
            decision=None;failure='RECEIVER_UNAVAILABLE'
            # Preserve only producer bytes already checked against actual private evidence.
            # Unsafe/untrusted producer evidence has no diagnostic transport.
            if not producer_verified:return 2
        need(time.monotonic()-start<180,'DEADLINE')
        private_export_check(pfd,expected,private_raw,private_identity,raw,w,receiver)
        need(directory(episode_fd)==original and directory(pfd)==private_custody and directory(outfd)==public_custody,'CARRIER_DRIFT')
        for name,fd in [('private',pfd),('public',outfd)]:need(custody(os.stat(name,dir_fd=episode_fd,follow_symlinks=False))==custody(os.fstat(fd)),'CARRIER_DRIFT')
        inventory(episode_fd,{'private','public'})
        # Re-admit every actual source byte after callbacks before any ready signal.
        for pin in pins['receiver']:need(admit_file(receiver_fd,pin)==sources[pin['path']] and identity(os.stat(pin['path'],dir_fd=receiver_fd,follow_symlinks=False))==source_ids[('r',pin['path'])],'SOURCE_PIN')
        for pin in pins['producer']:need(admit_file(producer_fd,pin)==producers[pin['path']] and identity(os.stat(pin['path'],dir_fd=producer_fd,follow_symlinks=False))==source_ids[('p',pin['path'])],'SOURCE_PIN')
        receiving={'schema':'dg17.claude.d0.receiving-export.v1','state':'AVAILABLE' if decision is not None else 'UNAVAILABLE','decision':decision}
        envelope={'schema':'dg17.claude.d0.envelope.v1','binding':expected,'status':'VALIDATED_COMPLETE' if failure is None else 'INCOMPLETE_OR_REFUSED','failure':failure,'deadline_seconds':180,'job_ceiling_minutes':5,'retries':0,'provider_numeric_job_join':'ROOT_RECEIVING_REQUIRED','original_acceptance':False,'source_effect_authority':'NONE'}
        raws={PUBLIC_NAMES[0]:raw,PUBLIC_NAMES[1]:codec(receiving),PUBLIC_NAMES[2]:codec(envelope)}
        export(outfd,raws,w,schemas)
        private_export_check(pfd,expected,private_raw,private_identity,raw,w,receiver)
        for pin in pins['receiver']:need(admit_file(receiver_fd,pin)==sources[pin['path']] and identity(os.stat(pin['path'],dir_fd=receiver_fd,follow_symlinks=False))==source_ids[('r',pin['path'])],'SOURCE_PIN')
        for pin in pins['producer']:need(admit_file(producer_fd,pin)==producers[pin['path']] and identity(os.stat(pin['path'],dir_fd=producer_fd,follow_symlinks=False))==source_ids[('p',pin['path'])],'SOURCE_PIN')
        need(directory(pfd)==private_custody and directory(outfd)==public_custody,'CARRIER_DRIFT')
        for name,fd in [('private',pfd),('public',outfd)]:need(custody(os.stat(name,dir_fd=episode_fd,follow_symlinks=False))==custody(os.fstat(fd)),'CARRIER_DRIFT')
        need(time.monotonic()-start<180,'DEADLINE')
        if failure is None:
            write_file(episode_fd,'PUBLICATION_READY.json',codec({'public_sha256':{n:digest(v) for n,v in raws.items()},'aggregate_bytes':sum(map(len,raws.values()))}))
        need(time.monotonic()-start<180,'DEADLINE')
        write_file(episode_fd,'PUBLIC_DIAGNOSTIC_READY.json',codec({'public_sha256':{n:digest(v) for n,v in raws.items()},'aggregate_bytes':sum(map(len,raws.values())),'status':envelope['status']}))
        need(time.monotonic()-start<180,'DEADLINE')
        return 0 if failure is None else 2
    except Deadline:return 2
    except Exception:return 2
    finally:
        signal.setitimer(signal.ITIMER_REAL,0);signal.signal(signal.SIGALRM,old)
        for fd in (pfd,outfd):
            if fd is not None:os.close(fd)
