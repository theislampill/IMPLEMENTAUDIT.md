"""Pinned prospective hosted bootstrap. No import effects or target census.
Workflow validates these exact bytes before calling main with its actual context.
"""
import hashlib,json,os,re,signal,stat,sys,time,types
# Generated source-body pins bind loading; actual publication commit arrives from
# the trusted workflow context and is independently joined by root at launch.
SOURCE_PINS = {'envelope': [{'path': 'd0_job.py', 'bytes': 15669, 'sha256': 'e1d3755d39b20763a481818eb9e9375a198988a7fd877ed985a4d85d8fa576b3'}, {'path': 'INPUT_PINS.json', 'bytes': 1811, 'sha256': '39d97d2459d7fa45835c5de4e96c10672adb7aa61959038b80f9270d91b348f3'}, {'path': 'PUBLIC_ENVELOPE_SCHEMAS.json', 'bytes': 8615, 'sha256': '978c2e2824366e15c82b4bd26380090d051db807e536f9753786c22f71d5e537'}]}

def need(ok):
    if not ok:raise ValueError('ADMISSION_REFUSED')
def ident(s):return tuple(getattr(s,n) for n in ('st_dev','st_ino','st_mode','st_uid','st_gid','st_nlink','st_size','st_mtime_ns','st_ctime_ns'))
def stable(s):return ident(s)[:6]
def open_physical(path,anchor=None):
    """Explicit absolute path only, no realpath, aliases or discovery."""
    need(type(path) is str and path.startswith('/') and len(path)<4096)
    pieces=path.split('/')[1:];need(all(p and p not in ('.','..') for p in pieces))
    if anchor is None:
        fd=os.open('/',os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC)
        root=os.fstat(fd)
        if root.st_uid!=0 or root.st_mode&0o022:
            os.close(fd);raise ValueError('ADMISSION_REFUSED')
    else:
        # Control-only admitted ancestor seam; production main never passes it.
        anchor_fd,prefix=anchor;need(path.startswith(prefix+'/'))
        pieces=path[len(prefix)+1:].split('/');fd=os.dup(anchor_fd)
    held=[]
    try:
        for piece in pieces:
            before=os.stat(piece,dir_fd=fd,follow_symlinks=False)
            need(stat.S_ISDIR(before.st_mode) and before.st_uid in (0,os.geteuid()) and not (before.st_mode&0o022))
            child=os.open(piece,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=fd)
            held.append((fd,piece,child,stable(before)))
            need(ident(os.fstat(child))==ident(before));fd=child
        return fd,held
    except BaseException:
        for parent,_,child,_ in reversed(held):os.close(child)
        os.close(held[0][0] if held else fd);raise

def check_chain(held):
    for parent,name,child,before in held:
        need(stable(os.stat(name,dir_fd=parent,follow_symlinks=False))==stable(os.fstat(child))==before)
def close_chain(fd,held):
    for parent,_,child,_ in reversed(held):os.close(child)
    os.close(held[0][0] if held else fd)
def source(fd,pin):
    name=pin['path'];need('/' not in name and name not in ('.','..'))
    s=os.stat(name,dir_fd=fd,follow_symlinks=False)
    need(stat.S_ISREG(s.st_mode) and s.st_uid==os.geteuid() and s.st_gid==os.getegid() and s.st_nlink==1 and not(s.st_mode&0o022) and s.st_size==pin['bytes'] and 0<s.st_size<=1048576)
    f=os.open(name,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK|os.O_CLOEXEC,dir_fd=fd)
    try:
        need(ident(os.fstat(f))==ident(s));raw=b''
        for _ in range(18):
            c=os.read(f,65536)
            if not c:break
            raw+=c;need(len(raw)<=1048576)
        else:raise ValueError('ADMISSION_REFUSED')
        need(len(raw)==s.st_size and hashlib.sha256(raw).hexdigest()==pin['sha256'] and ident(os.fstat(f))==ident(s)==ident(os.stat(name,dir_fd=fd,follow_symlinks=False)))
        return raw,ident(s)
    finally:os.close(f)
def context(env,expected_branch,expected_predecessor):
    need(env['GITHUB_REPOSITORY']=='theislampill/IMPLEMENTAUDIT.md' and env['GITHUB_EVENT_NAME']=='push' and env['GITHUB_RUN_ATTEMPT']=='1' and env['GITHUB_JOB']=='d0_census')
    need(re.fullmatch(r'[0-9a-f]{40}',env['GITHUB_SHA']) is not None and re.fullmatch(r'[0-9]{1,20}',env['GITHUB_RUN_ID']) is not None)
    need(env['GITHUB_REF']=='refs/heads/'+expected_branch and env['D0_EVENT_BEFORE']==expected_predecessor)
    need(env['D0_EVENT_CREATED']==env['D0_EVENT_DELETED']==env['D0_EVENT_FORCED']=='false')
    need(re.fullmatch(r'[0-9a-f]{40}',expected_predecessor) is not None)

def main(env,expected_branch,expected_predecessor):
    chains=[];episode=None;code=2;post_timer=False;old_alarm=None
    try:
        need(type(SOURCE_PINS) is dict);context(env,expected_branch,expected_predecessor)
        need(os.getuid()==os.geteuid()!=0 and os.getgid()==os.getegid()!=0 and sys.platform=='linux')
        paths={'envelope':env['GITHUB_WORKSPACE']+'/packet/qualification/dg17-claude-d0/envelope','receiver':env['GITHUB_WORKSPACE']+'/packet/qualification/dg17-claude-d0/receiver','producer':env['GITHUB_WORKSPACE']+'/packet/qualification/dg17-claude-d0/producer','temporary':env['RUNNER_TEMP']}
        fds={}
        for key,path in paths.items():
            fd,chain=open_physical(path);fds[key]=fd;chains.append((fd,chain))
        loaded={};ids={}
        for pin in SOURCE_PINS['envelope']:
            raw,i=source(fds['envelope'],pin);loaded[pin['path']]=raw;ids[pin['path']]=i
        m=types.ModuleType('admitted_envelope');exec(compile(loaded['d0_job.py'],'<admitted_envelope>','exec'),m.__dict__)
        pins=json.loads(loaded['INPUT_PINS.json']);schemas=json.loads(loaded['PUBLIC_ENVELOPE_SCHEMAS.json'])
        pins['reviewed_execution_commit']=env['GITHUB_SHA']
        inventories={'envelope':{p['path'] for p in SOURCE_PINS['envelope']}|{'bootstrap.py'},'receiver':{p['path'] for p in pins['receiver']},'producer':{p['path'] for p in pins['producer']}}
        for key,names in inventories.items():m.inventory(fds[key],names)
        name='dg17-d0-'+env['GITHUB_RUN_ID']+'-1'
        temp_before=stable(os.fstat(fds['temporary']))
        os.mkdir(name,0o700,dir_fd=fds['temporary'])
        temp_after=stable(os.fstat(fds['temporary']));need(temp_after[:5]==temp_before[:5] and temp_after[5]==temp_before[5]+1)
        # Exactly this exclusive child creation accounts for the parent link delta.
        for held_fd,chain in chains:
            if held_fd==fds['temporary']:
                parent,part,child,_=chain[-1];chain[-1]=(parent,part,child,temp_after)
        episode=os.open(name,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=fds['temporary'])
        episode_id=stable(os.fstat(episode));need(episode_id==stable(os.stat(name,dir_fd=fds['temporary'],follow_symlinks=False)))
        started=time.monotonic()
        code=m.run(episode,fds['receiver'],fds['producer'],pins,schemas,env)
        remaining=180-(time.monotonic()-started);need(remaining>0)
        old_alarm=signal.getsignal(signal.SIGALRM)
        def expired(*_):raise TimeoutError('DEADLINE')
        signal.signal(signal.SIGALRM,expired);signal.setitimer(signal.ITIMER_REAL,remaining);post_timer=True
        for fd,chain in chains:check_chain(chain)
        for key,names in inventories.items():m.inventory(fds[key],names)
        need(stable(os.stat(name,dir_fd=fds['temporary'],follow_symlinks=False))[:5]==episode_id[:5])
        for pin in SOURCE_PINS['envelope']:need(source(fds['envelope'],pin)==(loaded[pin['path']],ids[pin['path']]))
        for owner in ('receiver','producer'):
            for pin in pins[owner]:source(fds[owner],pin)
        # Independent diagnostic admission is deliberately separate from exit code.
        wire_pin=next(p for p in pins['receiver'] if p['path']=='d0_wire.py')
        w=m.module(source(fds['receiver'],wire_pin)[0],'bootstrap_wire')
        ready=w.decode(m.read_file(episode,'PUBLIC_DIAGNOSTIC_READY.json',16384),16384)
        out=os.open('public',os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=episode)
        try:
            m.inventory(out,set(m.PUBLIC_NAMES));actual={n:m.read_file(out,n,16384) for n in m.PUBLIC_NAMES}
            m.aggregate(actual.values());values={n:w.decode(v,16384) for n,v in actual.items()}
            for n,value in values.items():w.validate(value,schemas[n])
            w.validate_public(values[m.PUBLIC_NAMES[0]],schemas[m.PUBLIC_NAMES[0]])
            status=values['D0_ENVELOPE.json']['status']
            hashes={'aggregate_bytes':sum(map(len,actual.values())),'public_sha256':{n:m.digest(v) for n,v in actual.items()}}
            need(ready==dict(hashes,status=status))
            receiving=values['D0_RECEIVING.json'];decision=receiving['decision']
            need((receiving['state']=='UNAVAILABLE')==(decision is None))
            need(values['D0_ENVELOPE.json']['binding']['source_commit']==env['GITHUB_SHA'])
            if status=='VALIDATED_COMPLETE':
                need(code==0 and decision is not None and decision['observation']=='RECEIVED_FIXED_HOST_INPUTS')
                need(w.decode(m.read_file(episode,'PUBLICATION_READY.json',16384),16384)==hashes)
            else:
                need(code==2)
                try:os.stat('PUBLICATION_READY.json',dir_fd=episode,follow_symlinks=False)
                except FileNotFoundError:pass
                else:raise ValueError('FALSE_COMPLETION')
            need(time.monotonic()-started<180)
            return code,True
        finally:os.close(out)
    except BaseException:return 2,False
    finally:
        if post_timer:
            signal.setitimer(signal.ITIMER_REAL,0);signal.signal(signal.SIGALRM,old_alarm)
        if episode is not None:os.close(episode)
        for fd,chain in reversed(chains):close_chain(fd,chain)
