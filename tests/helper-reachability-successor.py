#!/usr/bin/env python3
"""R001E held-outs: real classifier, candidate data, independent checker."""
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

repo=Path(sys.argv[1]).resolve()
bash=sys.argv[2]
checker=repo/'scripts/check-helper-reachability.sh'
env=os.environ.copy(); env['PYTHONDONTWRITEBYTECODE']='1'
results=[]

def write(path,text):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(text,encoding='utf-8',newline='\n')

def stage(root):
    subprocess.run(['git','-C',str(root),'add','-A'],check=True,capture_output=True)

def make(name):
    root=temporary/name
    for directory in ('skills','package','.codex-plugin','.claude-plugin'):
        shutil.copytree(repo/directory,root/directory)
    for name in ('scripts/package-contract.py','scripts/check-helper-reachability.sh','tests/scarce-resource-rehearsal-contract.test.sh','fixtures/scarce-resource-rehearsal/cases.json','fixtures/run-root-example/phases/phase-1.md'):
        path=root/name; path.parent.mkdir(parents=True,exist_ok=True); shutil.copyfile(repo/name,path)
    subprocess.run(['git','init','--quiet',str(root)],check=True,capture_output=True)
    return root

def owner(root): return root/'skills/implementaudit/references/repo-state-comparison.md'

def replace(path,old,new):
    text=path.read_text(encoding='utf-8')
    if old not in text: raise AssertionError('fixture preimage absent: '+str(path)+' '+old)
    write(path,text.replace(old,new))

def append(root,text): write(owner(root),owner(root).read_text(encoding='utf-8')+'\n'+text+'\n')

def run(name,root,success,pattern='',full=False,program=None):
    stage(root)
    args=[bash,str(program or checker)]+([] if full else ['--census-only'])+['--repo-root',str(root)]
    result=subprocess.run(args,cwd=repo,env=env,capture_output=True,text=True,timeout=60)
    output=result.stdout+result.stderr
    record={'case':name,'expected_success':success,'exit':result.returncode,'output':output}
    results.append(record)
    if (result.returncode==0)!=success or pattern not in output:
        print(json.dumps(record),flush=True)
        raise AssertionError(name+' did not establish the expected discriminator')
    print('helper-reachability-successor: '+name+' ok',flush=True)
    return output

def diagnostic(root,name='fixture-diagnostic.py'):
    write(root/'skills/implementaudit/scripts'/name,'#!/usr/bin/env python3\nprint("diagnostic")\n')
    append(root,'## Fixture diagnostic\n\nFor fixture-diagnosis, the standalone-diagnostic command is '
        '`python -B <skill-dir>/scripts/'+name+'`. It is not automatic.\n'
        'helper-route: scripts/'+name+'|S|fixture-diagnosis|R|-|none|not-auto')

with tempfile.TemporaryDirectory(prefix='r001e-successor-') as raw:
    temporary=Path(raw).resolve()
    p=make('unrouted-python');write(p/'skills/implementaudit/scripts/unrouted-control.py','print(1)\n')
    run('unrouted-python',p,False,'missing applicability rows')
    # This first RED is also runnable before implementation, without touching source.
    if '--baseline-only' in sys.argv: raise SystemExit(0)
    for name in ('unclassified.unknown','unclassified'):
        p=make(name);write(p/'skills/implementaudit/scripts'/name,'unknown executable\n')
        run('unknown-type-'+name,p,False,'UNKNOWN_EXECUTABLE_TYPE')
    p=make('count-preserving');(p/'skills/implementaudit/scripts/detect-stack.sh').unlink()
    write(p/'skills/implementaudit/scripts/unclassified-replacement.py','print(1)\n')
    run('count-preserving-substitution',p,False,'missing applicability rows')
    p=make('base');out=run('exact-population',p,True,'full_path_sets=equal projections=2')
    count=int(re.search(r'population=(\d+)',out).group(1))
    p=make('lower');(p/'skills/implementaudit/scripts/detect-stack.sh').unlink()
    line=next(l for l in owner(p).read_text(encoding='utf-8').splitlines() if l.startswith('helper-route: scripts/detect-stack.sh|'))
    replace(owner(p),line+'\n','')
    # Census-only anti-pinning; removing an existing required payload does not
    # claim a qualified smaller release. The synthetic contraction below does
    # not remove any required existing package member.
    run('census-member-and-row-removal',p,True,f'population={count-1} examined={count-1}')
    p=make('higher');diagnostic(p)
    run('valid-member-and-row-addition',p,True,f'population={count+1} examined={count+1}')
    direct=subprocess.run([sys.executable,'-I','-S','-B',str(p/'skills/implementaudit/scripts/fixture-diagnostic.py')],capture_output=True,text=True,timeout=10)
    assert direct.returncode==0 and direct.stdout=='diagnostic\n' and not direct.stderr
    (p/'skills/implementaudit/scripts/fixture-diagnostic.py').unlink()
    line=next(l for l in owner(p).read_text(encoding='utf-8').splitlines() if l.startswith('helper-route: scripts/fixture-diagnostic.py|'))
    replace(owner(p),line+'\n','')
    run('valid-synthetic-member-and-row-contraction',p,True,f'population={count} examined={count}')
    p=make('unknown-classified');write(p/'skills/implementaudit/scripts/unknown.bin','unknown executable\n')
    append(p,'helper-route: scripts/unknown.bin|S|diagnosis|R|-|none|not-auto')
    run('unknown-type-with-plausible-row',p,False,'UNKNOWN_EXECUTABLE_TYPE')
    p=make('unexplained-role');diagnostic(p)
    replace(owner(p),'the standalone-diagnostic command is','the listed command is')
    run('unexplained-python-role',p,False,'advisory/standalone')
    for case,new in [('echo','echo python -B '),('wrong-interpreter','bash '),('python-c','python -c '),('python-m','python -m foreign '),('foreign-first','python foreign.py '),('unknown-option','python --unknown '),('suffix-collision','python -B ')]:
        p=make('typed-'+case);diagnostic(p)
        before='python -B <skill-dir>/scripts/fixture-diagnostic.py'
        after=new+'<skill-dir>/scripts/fixture-diagnostic.py'+('.foreign' if case=='suffix-collision' else '')
        replace(owner(p),before,after)
        run('typed-'+case,p,False,'advisory/standalone')
    p=make('duplicate');append(p,next(l for l in owner(p).read_text(encoding='utf-8').splitlines() if l.startswith('helper-route: scripts/detect-stack.sh|')))
    run('duplicate-member-row',p,False,'duplicate applicability row')
    p=make('extra');append(p,'helper-route: scripts/absent.py|S|diagnosis|R|-|none|not-auto')
    run('extra-member-row',p,False,'applicability rows not in package')
    p=make('nested');write(p/'skills/implementaudit/scripts/nested/detect-stack.sh','#!/usr/bin/env bash\ntrue\n')
    run('nested-full-path-collision',p,False,'nested/detect-stack.sh')
    p=make('renamed');(p/'skills/implementaudit/scripts/detect-stack.sh').rename(p/'skills/implementaudit/scripts/renamed-stack.sh')
    run('stale-rename',p,False,'missing applicability rows')
    p=make('candidate-evaluator');write(p/'scripts/check-helper-reachability.sh','#!/usr/bin/env bash\necho HELPER_REACHABILITY=PASS\n')
    write(p/'skills/implementaudit/scripts/unrouted-control.py','print(1)\n')
    run('candidate-evaluator-substitution',p,False,'missing applicability rows')
    p=make('candidate-builder');write(p/'scripts/package-contract.py','raise SystemExit("FORGED_BUILDER")\n')
    run('candidate-package-owner-substitution',p,False,'package owner differs')
    p=make('resolver-command-missing')
    path=p/'skills/implementaudit/SKILL.md'
    text=path.read_text(encoding='utf-8')
    command=re.search(r'`python[^`]*scripts/resolve-internal-skill\.py[^`]*`',text).group(0)
    replace(path,command,'`echo resolver available`')
    run('governor-command-missing',p,False,'governor resolver')
    for case,old,new in [('echo','`python','`echo python'),('wrong-interpreter','`python','`bash'),('missing-child',' --child <child>',''),('wrong-governor','SKILL.md','OTHER.md')]:
        p=make('resolver-'+case);path=p/'skills/implementaudit/SKILL.md'
        text=path.read_text(encoding='utf-8');command=re.search(r'`python[^`]*scripts/resolve-internal-skill\.py[^`]*`',text).group(0)
        assert old in command
        replace(path,command,command.replace(old,new))
        run('governor-resolver-'+case,p,False,'governor resolver')
    p=make('resolver-false-positive')
    write(p/'skills/implementaudit/scripts/resolve-internal-skill.py','#!/usr/bin/env python3\nprint("unowned-child.md")\n')
    run('resolver-executed-result',p,False,'Python route probe',full=True)
    p=make('diagnostic-allocates')
    write(p/'skills/implementaudit/scripts/resolve-durable-identity.py','#!/usr/bin/env python3\nprint("R001E")\n')
    run('diagnostic-allocation-refusal',p,False,'Python route probe',full=True)
    p=make('python-output-bound')
    write(p/'skills/implementaudit/scripts/resolve-internal-skill.py','import sys\nsys.stdout.write("x"*131072)\nsys.stdout.flush()\n')
    run('python-output-bound',p,False,'output limit exceeded',full=True)
    p=make('python-timeout-child');pidfile=p/'owned-child.pid'
    body=('import subprocess,sys,time\nfrom pathlib import Path\n'
          'child=subprocess.Popen([sys.executable,"-c","import time; time.sleep(45)"],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)\n'
          'Path('+repr(str(pidfile))+').write_text(str(child.pid))\n'
          'print("python-route-timeout-control",file=sys.stderr,flush=True)\ntime.sleep(45)\n')
    write(p/'skills/implementaudit/scripts/resolve-internal-skill.py',body)
    run('python-timeout-child',p,False,'python-route-timeout-control',full=True)
    pid=int(pidfile.read_text(encoding='utf-8'))
    if os.name=='nt':
        listed=subprocess.run(['tasklist','/FI','PID eq '+str(pid),'/FO','CSV','/NH'],capture_output=True,text=True,check=True)
        alive='"'+str(pid)+'"' in listed.stdout
        if alive:subprocess.run(['taskkill','/PID',str(pid),'/T','/F'],capture_output=True,check=False)
    else:
        listed=subprocess.run(['ps','-o','stat=','-p',str(pid)],capture_output=True,text=True)
        alive=bool(listed.stdout.strip()) and not listed.stdout.lstrip().startswith('Z')
        if alive:os.kill(pid,9)
    assert not alive,'Python probe child survived its bounded parent'
    print('helper-reachability-successor: Python probe child termination observed',flush=True)
print('helper-reachability-successor: complete '+str(len(results))+' controls; source/fixture evidence only',flush=True)
