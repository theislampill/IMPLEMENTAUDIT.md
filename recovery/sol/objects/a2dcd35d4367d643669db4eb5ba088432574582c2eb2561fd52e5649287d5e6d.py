"""One bounded ordinary-Git fixture using the exact published capture boundary.

Only fresh private repositories below ROOT. No original project/owner/native
campaign, global configuration, credentials, lock removal or installation.
"""
import ctypes, hashlib, json, os, stat, subprocess, sys, time, types
from pathlib import Path

ROOT=Path('/home/agent/sol-git256-package-probe-20261109-01')
GIT=ROOT/'package/usr/bin/git'
EXEC_PATH=ROOT/'package/usr/lib/git-core'
TEMPLATES=ROOT/'package/usr/share/git-core/templates'
UTILITY=Path('/mnt/c/workspace/ai/improveimplementaudit/plans/sol-dg16-staged-execution-20261108/g1-current03-recovered/current04-finish-01/finish/tree/qualification/dg16-r5-g1-hosted-episode/host_utility.py')
UTILITY_SHA='429c6b50cef6ef6352a0c812ce9fcf386cc852156ba54c2d1419088c8f89f85c'
GIT_SHA='824d5b2fffef332ec7ba053e579659bb12f26a0b4747da6f9c6dc0e71d36f235'

def need(ok,code):
    if not ok:raise ValueError(code)

def sha(raw):return hashlib.sha256(raw).hexdigest()

def namespace(path):
    rows=[]
    if path.exists():
        for parent,dirs,files in os.walk(path,followlinks=False):
            for name in sorted(dirs+files):
                p=Path(parent)/name;st=p.lstat();relative=p.relative_to(path).as_posix()
                need(not stat.S_ISLNK(st.st_mode),'FIXTURE_NAMESPACE_ALIAS')
                rows.append(dict(path=relative,kind='DIRECTORY' if stat.S_ISDIR(st.st_mode) else 'FILE',
                                 bytes=st.st_size if stat.S_ISREG(st.st_mode) else None,
                                 is_lock=relative.endswith('.lock'),is_promisor=relative.endswith('.promisor')))
                need(len(rows)<=1024,'TINY_FIXTURE_NAMESPACE_BOUND')
    return dict(entries=len(rows),locks=[r for r in rows if r['is_lock']],
                promisors=[r for r in rows if r['is_promisor']],
                names_sha256=sha(json.dumps(rows,sort_keys=True,separators=(',',':')).encode()))

def await_natural_children(U):
    end=time.monotonic()+4;reaped=[]
    while time.monotonic()<end:
        try:pid,status=os.waitpid(-1,os.WNOHANG|0x40000000)
        except ChildProcessError:return dict(echild=True,pidfd_signals=0,reaped=reaped)
        if pid:reaped.append(dict(pid=pid,returncode=os.waitstatus_to_exitcode(status)))
        else:time.sleep(0.01)
    partial=U.stop_owned_children()
    raise RuntimeError('PLAIN_NATURAL_COMPLETION_UNESTABLISHED_'+json.dumps(partial,sort_keys=True))

def main():
    need(sys.platform=='linux' and os.getuid()==os.geteuid()>0,'FIXED_NONROOT_LINUX')
    need(ROOT.resolve()==ROOT and ROOT.stat().st_uid==os.geteuid() and stat.S_IMODE(ROOT.stat().st_mode)==0o700,'SCRATCH_CUSTODY')
    need(sha(GIT.read_bytes())==GIT_SHA,'EXACT_ORIGINAL_GIT_BINARY_REQUIRED')
    need(EXEC_PATH.is_dir() and TEMPLATES.is_dir(),'PACKAGE_HELPERS_AND_TEMPLATES_REQUIRED')
    raw=UTILITY.read_bytes();need(sha(raw)==UTILITY_SHA,'EXACT_PUBLISHED_CAPTURE_SOURCE_REQUIRED')
    U=types.ModuleType('exact_published_utility');U.__file__=str(UTILITY)
    exec(compile(raw,str(UTILITY),'exec'),U.__dict__)  # inert module, no --run/main
    libc=ctypes.CDLL(None,use_errno=True)
    need(libc.prctl(36,1,0,0,0)==0,'FIXTURE_SUBREAPER_UNAVAILABLE')
    observed=ctypes.c_int();need(libc.prctl(37,ctypes.byref(observed),0,0,0)==0 and observed.value==1,'FIXTURE_SUBREAPER_READBACK')
    # This new process owns no children before its first fixture command.
    need(U.children()==[],'FRESH_PROCESS_CHILD_CUSTODY')
    home=ROOT/'tiny';home.mkdir(mode=0o700)
    overall=time.monotonic()+120;commands=[];results=[]
    def command(label,args,mode='plain',foreground=False):
        need(time.monotonic()<overall,'FIXTURE_TOTAL_BOUND')
        argv=[str(GIT),'--exec-path='+str(EXEC_PATH),'-c','protocol.file.allow=always']
        if foreground:argv+=['-c','maintenance.autoDetach=false']
        argv+=args
        if mode=='capture':
            records=[]
            rc,out,err=U.capture(label,argv,records,overall,seconds=20)
            custody=records[-1]['cleanup']
        else:
            p=subprocess.run(argv,stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.PIPE,
                             env=U.safe_environment(),start_new_session=True,timeout=20,check=False)
            rc,out,err=p.returncode,p.stdout,p.stderr
            need(len(out)<=32768 and len(err)<=32768,'PLAIN_FIXTURE_STREAM_BOUND')
            custody=await_natural_children(U);records=[]
        row=dict(label=label,argv=argv,mode=mode,returncode=rc,stdout=out.decode('utf8','replace'),
                 stderr=err.decode('utf8','replace'),cleanup=custody,published_records=records)
        commands.append(row)
        (home/'COMMANDS.json').write_text(json.dumps(commands,indent=2)+'\n')
        need(rc==0 and custody['echild'] is True,'FIXTURE_COMMAND_OR_CUSTODY_REFUSED')
        return out
    try:
        origin=home/'origin'
        command('fixture-origin-init',['init','--quiet','--initial-branch=main','--template='+str(TEMPLATES),str(origin)])
        for i in range(3):
            command('fixture-origin-commit-'+str(i),['-c','user.name=DG16 synthetic fixture','-c','user.email=dg16-fixture@example.invalid',
                    '-C',str(origin),'commit','--quiet','--allow-empty','-m','synthetic '+str(i)])
        commit=command('fixture-origin-head',['-C',str(origin),'rev-parse','HEAD']).decode().strip()
        need(len(commit)==40 and all(c in '0123456789abcdef' for c in commit),'FIXTURE_HEAD_IDENTITY')
        def trial(mode,foreground=False):
            label=mode+('-foreground' if foreground else '-default')
            destination=home/label
            steps=[('clone',['clone','--quiet','--no-local','--no-hardlinks','--no-checkout','--template='+str(TEMPLATES),'--',origin.as_uri(),str(destination)]),
                   ('fetch',['-C',str(destination),'fetch','--quiet','--no-tags','--no-recurse-submodules','origin',commit]),
                   ('detach',['-C',str(destination),'checkout','--quiet','--detach',commit]),
                   ('optional-auto',['-C',str(destination),'maintenance','run','--auto'])]
            observations=[]
            for name,args in steps:
                before=namespace(destination)
                command(label+'-'+name,args,mode,foreground)
                immediate=namespace(destination)
                time.sleep(0.1)
                after=namespace(destination)
                observations.append(dict(step=name,before=before,immediate=immediate,after=after))
                if after['locks']:break  # Preserve the first lock; never retry/delete it.
            row=dict(trial=label,foreground_command_control=foreground,observations=observations,
                     final_namespace=namespace(destination))
            results.append(row)
            (home/'TRIALS.json').write_text(json.dumps(results,indent=2)+'\n')
            return row
        plain=trial('plain')
        captured=trial('capture')
        reproduced=bool(captured['final_namespace']['locks']) and not plain['final_namespace']['locks']
        control=trial('capture',foreground=True) if reproduced else None
        receipt=dict(schema='dg16.git256-tiny-ordinary-preparation-probe.v1',git_sha256=GIT_SHA,
            host_utility_sha256=UTILITY_SHA,subreaper=True,actual_version='git version2.56.0; exacthostbinary bytes',
            fixture_origin_commit=commit,reproduced_persistent_lock_after_owned_capture=reproduced,
            foreground_control_performed=control is not None,trials=results,commands=commands,
            original_host_lock_filename_or_owner='UNKNOWN; fixture is distinct',
            scope='Tiny local file-transport repositories; package exec-path/template overrides; existing WSL libraries/kernel; no original owner/C5/host campaign',
            actual_original_or_protected_effects=0,installed=False,global_config_changed=False,locks_deleted=False)
        (ROOT/'TINY_PROBE_RECEIVING.json').write_text(json.dumps(receipt,indent=2)+'\n')
        print(json.dumps(dict(reproduced=reproduced,control_performed=control is not None,
              final_locks={r['trial']:r['final_namespace']['locks'] for r in results},commands=len(commands))))
    finally:
        terminal=U.stop_owned_children()
        (ROOT/'FIXTURE_TERMINAL_CUSTODY.json').write_text(json.dumps(terminal,indent=2)+'\n')
        need(terminal['echild'] is True,'FIXTURE_TERMINAL_CUSTODY_UNKNOWN')

if __name__=='__main__':main()
