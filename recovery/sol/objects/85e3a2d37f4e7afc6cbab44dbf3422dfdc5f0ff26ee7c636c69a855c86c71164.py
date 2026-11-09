"""One commissioned public HTTPS clone; no original owner/C5/host campaign.

Reuse its first clone. Preserve a complete clean pre-fetch filesystem baseline;
only an observed persistent lock or signal-terminated owned child permits the
command-scoped foreground control on an independent byte-identical copy.
"""
import ctypes, hashlib, json, os, shutil, stat, sys, time, types
from pathlib import Path

ROOT=Path('/home/agent/sol-git256-public-clone-20261109-01')
PACKAGE=Path('/home/agent/sol-git256-package-probe-20261109-01/package')
GIT=PACKAGE/'usr/bin/git';EXEC_PATH=PACKAGE/'usr/lib/git-core';TEMPLATES=PACKAGE/'usr/share/git-core/templates'
GIT_SHA='824d5b2fffef332ec7ba053e579659bb12f26a0b4747da6f9c6dc0e71d36f235'
UTILITY=Path('/mnt/c/workspace/ai/improveimplementaudit/plans/sol-dg16-staged-execution-20261108/g1-current03-recovered/current04-finish-01/finish/tree/qualification/dg16-r5-g1-hosted-episode/host_utility.py')
UTILITY_SHA='429c6b50cef6ef6352a0c812ce9fcf386cc852156ba54c2d1419088c8f89f85c'
URL='https://github.com/theislampill/IMPLEMENTAUDIT.md.git'
COMMIT='7e2b00b3a2a16fc6033a5eabe4fc795f6249366f'
TREE='6d3f972a424583f9d3d56d8bfd9ae11cf36ecf6e'

def need(ok,code):
    if not ok:raise ValueError(code)

def sha(raw):return hashlib.sha256(raw).hexdigest()

def census(path,content=False):
    rows=[];total=0;locks=[];promisors=[]
    if path.exists():
        for parent,dirs,files in os.walk(path,followlinks=False):
            for name in sorted(dirs+files):
                p=Path(parent)/name;s=p.lstat();rel=p.relative_to(path).as_posix()
                need(stat.S_ISREG(s.st_mode) or stat.S_ISDIR(s.st_mode),'ORDINARY_PUBLIC_NAMESPACE_ONLY')
                row=dict(path=rel,kind='DIRECTORY' if stat.S_ISDIR(s.st_mode) else 'FILE',mode=stat.S_IMODE(s.st_mode),
                         bytes=s.st_size if stat.S_ISREG(s.st_mode) else None)
                if stat.S_ISREG(s.st_mode):
                    total+=s.st_size;need(total<=512*1024**2,'PUBLIC_FIXTURE_BYTE_BOUND')
                    if content:row['sha256']=sha(p.read_bytes())
                rows.append(row);need(len(rows)<=4096,'PUBLIC_FIXTURE_NAMESPACE_BOUND')
                if rel.endswith('.lock'):
                    detail=dict(row,uid=s.st_uid,gid=s.st_gid,inode=s.st_ino,mtime_ns=s.st_mtime_ns)
                    if stat.S_ISREG(s.st_mode) and s.st_size<=4096:detail['body_sha256']=sha(p.read_bytes())
                    locks.append(detail)
                if rel.endswith('.promisor'):promisors.append(row)
    return dict(entries=len(rows),file_bytes=total,locks=locks,promisors=promisors,
                namespace_sha256=sha(json.dumps(rows,sort_keys=True,separators=(',',':')).encode()),
                content_bound=content)

def save(name,value):
    (ROOT/name).write_text(json.dumps(value,indent=2)+'\n')

def main():
    need(sys.platform=='linux' and os.getuid()==os.geteuid()>0,'FIXED_NONROOT_LINUX')
    need(shutil.disk_usage(ROOT.parent).free>=2*1024**3,'PUBLIC_FIXTURE_FREE_SPACE')
    ROOT.mkdir(mode=0o700)
    need(ROOT.resolve()==ROOT and ROOT.stat().st_uid==os.geteuid(),'FRESH_PRIVATE_ROOT')
    need(sha(GIT.read_bytes())==GIT_SHA,'EXACT_ORIGINAL_GIT_BYTES')
    raw=UTILITY.read_bytes();need(sha(raw)==UTILITY_SHA,'EXACT_PUBLISHED_CAPTURE_SOURCE')
    U=types.ModuleType('exact_public_fixture_capture');U.__file__=str(UTILITY)
    exec(compile(raw,str(UTILITY),'exec'),U.__dict__)
    libc=ctypes.CDLL(None,use_errno=True)
    need(libc.prctl(36,1,0,0,0)==0,'FIXTURE_SUBREAPER_UNAVAILABLE')
    state=ctypes.c_int();need(libc.prctl(37,ctypes.byref(state),0,0,0)==0 and state.value==1 and U.children()==[],
                           'FIXTURE_SUBREAPER_CUSTODY')
    end=time.monotonic()+600;commands=[];observations=[];control=[]
    result=dict(schema='dg16.git256-public-ordinary-repository-probe.v1',git_sha256=GIT_SHA,
        utility_sha256=UTILITY_SHA,source_url=URL,selected_commit=COMMIT,selected_tree=TREE,
        status='INCOMPLETE',commands=commands,observations=observations,control=control,
        original_host_lock_identity='UNKNOWN; observations belong to this distinct private fixture',
        no_installation=True,no_global_config_or_credentials=True,no_original_native_or_hosted_campaign=True,
        lock_deletions=0,network_clone_attempts=0,baseline_copy_performed=False,foreground_control_performed=False)
    def command(label,args,seconds,foreground=False):
        need(time.monotonic()<end,'PUBLIC_FIXTURE_TOTAL_BOUND')
        argv=[str(GIT),'--exec-path='+str(EXEC_PATH),'-c','protocol.https.allow=always']
        if foreground:argv+=['-c','maintenance.autoDetach=false']
        argv+=args;records=[]
        save('PENDING_COMMAND.json',dict(label=label,argv=argv,seconds=seconds,automatic_retry=False))
        try:
            rc,out,err=U.capture(label,argv,records,end,seconds=seconds)
        except BaseException as exc:
            captured=getattr(exc,'captured',{})
            commands.append(dict(label=label,argv=argv,returncode=captured.get('returncode'),
                stdout=captured.get('stdout',b'').decode('utf8','replace'),
                stderr=captured.get('stderr',b'').decode('utf8','replace'),
                published_records=records,refusal_type=type(exc).__name__,refusal=str(exc)[:512]))
            save('COMMANDS.json',commands)
            raise
        row=dict(label=label,argv=argv,returncode=rc,stdout=out.decode('utf8','replace'),
                 stderr=err.decode('utf8','replace'),published_records=records)
        commands.append(row);save('COMMANDS.json',commands)
        need(rc==0,'PUBLIC_GIT_COMMAND_REFUSED')
        return out,row
    def observe(label,path,rows):
        opened=census(path);time.sleep(0.1);closed=census(path)
        row=dict(label=label,opening=opened,closing=closed);rows.append(row)
        save('OBSERVATIONS.json',dict(default=observations,foreground=control))
        return closed
    def hazardous(command_row,closed):
        cleanup=command_row['published_records'][-1]['cleanup']
        killed=any(x['returncode']<0 for x in cleanup['reaped_statuses'])
        return bool(closed['locks']) or killed
    try:
        default=ROOT/'default'
        result['network_clone_attempts']=1;save('PUBLIC_PROBE_RECEIVING.json',result)
        _,clone_row=command('public-clone',['clone','--quiet','--no-local','--no-hardlinks','--no-checkout',
                            '--template='+str(TEMPLATES),'--',URL,str(default)],180)
        clone_state=observe('after-clone',default,observations)
        if hazardous(clone_row,clone_state):
            result.update(status='OWNED_CHILD_OR_LOCK_HAZARD_AFTER_CLONE_STOPPED',hazard=True,
                          default_final_namespace=clone_state,
                          control_refused='No clean pre-fetch baseline; original clone/lock preserved, no second download')
            return
        branch,_=command('default-branch',['-C',str(default),'symbolic-ref','--short','HEAD'],60)
        branch=branch.decode('ascii').strip()
        need(branch and all(c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789._/-' for c in branch),
             'OBSERVED_BRANCH_REFUSED')
        _,_=command('remove-observed-branch-tracking',['-C',str(default),'config','--local','--remove-section','branch.'+branch],60)
        prefetch=observe('before-fetch',default,observations)
        need(not prefetch['locks'],'PRE_FETCH_LOCK_REFUSED')
        baseline=ROOT/'pre-fetch-baseline';before=census(default,content=True)
        shutil.copytree(default,baseline,copy_function=shutil.copy2)
        copied=census(baseline,content=True)
        need(before==copied==census(default,content=True),'QUIESCENT_COMPLETE_BASELINE_COPY')
        result.update(baseline_copy_performed=True,baseline_census=copied)
        _,fetch_row=command('selected-fetch',['-C',str(default),'fetch','--quiet','--no-tags','--no-recurse-submodules','origin',COMMIT],120)
        after=observe('after-fetch',default,observations)
        hazard=hazardous(fetch_row,after)
        result['hazard']=hazard
        if not after['locks']:
            _,detach_row=command('selected-detach',['-C',str(default),'checkout','--quiet','--detach',COMMIT],60)
            after=observe('after-detach',default,observations)
            hazard=hazard or hazardous(detach_row,after)
            if not after['locks']:
                identity,_=command('selected-identity',['-C',str(default),'rev-parse','HEAD','HEAD^{tree}'],60)
                need(identity.decode().splitlines()==[COMMIT,TREE],'SELECTED_SOURCE_IDENTITY')
        if hazard:
            need(not census(baseline)['locks'] and census(baseline,content=True)==copied,'CLEAN_SAME_STATE_CONTROL_REQUIRED')
            alternate=ROOT/'foreground';shutil.copytree(baseline,alternate,copy_function=shutil.copy2)
            need(census(alternate,content=True)==copied,'INDEPENDENT_CONTROL_BASELINE_IDENTITY')
            result['foreground_control_performed']=True
            observe('control-before-fetch',alternate,control)
            command('foreground-selected-fetch',['-C',str(alternate),'fetch','--quiet','--no-tags','--no-recurse-submodules','origin',COMMIT],120,True)
            controlled=observe('control-after-fetch',alternate,control)
            if not controlled['locks']:
                command('foreground-selected-detach',['-C',str(alternate),'checkout','--quiet','--detach',COMMIT],60,True)
                controlled=observe('control-after-detach',alternate,control)
            result['foreground_final_namespace']=controlled
        result.update(status='COMPLETED_BOUNDED_PUBLIC_FIXTURE',hazard=hazard,default_final_namespace=census(default))
    except BaseException as exc:
        result.update(status='REFUSED_OR_UNKNOWN_NO_RETRY',failure_type=type(exc).__name__,failure=str(exc)[:512])
        raise
    finally:
        cleanup=U.stop_owned_children();result['terminal_custody']=cleanup
        result['distro_git_sha256']=sha(Path('/usr/bin/git').read_bytes())
        save('PUBLIC_PROBE_RECEIVING.json',result)
        need(cleanup['echild'] is True,'PUBLIC_FIXTURE_TERMINAL_CUSTODY_UNKNOWN')
        print(json.dumps(dict(status=result['status'],hazard=result.get('hazard'),
              foreground_control=result['foreground_control_performed'],network_clones=result['network_clone_attempts'],
              locks=result.get('default_final_namespace',{}).get('locks'),terminal=cleanup)))

if __name__=='__main__':main()
