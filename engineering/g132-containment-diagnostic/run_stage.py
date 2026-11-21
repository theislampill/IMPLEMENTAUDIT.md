#!/usr/bin/env python3
"""Four closed ordinary setup routes; no private or original operation."""
import hashlib
import os
from pathlib import Path
import re
import stat
import sys

REPOSITORY = 'theislampill/IMPLEMENTAUDIT.md'
BRANCH = 'pro/dg16-g132-containment-observe-20261121-01'
WORKFLOW = '.github/workflows/dg16-g132-containment-observe.yml'
SELF = 'engineering/g132-containment-diagnostic/run_stage.py'
OWNER = 'scripts/qualify-work-graph-c5-setup.py'
OWNER_BYTES = 81629
OWNER_SHA256 = '3b3078e9c86d73c1789f102fcfbf2a4eaa9a835ba58ac9885c770dfbdaa50368'
ROUTES = {'launcher': ('--provision-hosted-launcher',),
          'policy': ('--provision-hosted-bwrap-policy',),
          'witness': (), 'finalize': ('--finalize-hosted-bwrap-policy',)}

def need(value, code):
    if not value:
        raise ValueError(code)

def validate_call(argv, env):
    fixed = {'GITHUB_ACTIONS':'true', 'RUNNER_ENVIRONMENT':'github-hosted',
             'GITHUB_REPOSITORY':REPOSITORY, 'GITHUB_REF':'refs/heads/'+BRANCH,
             'GITHUB_EVENT_NAME':'push', 'GITHUB_RUN_ATTEMPT':'1', 'GITHUB_JOB':'observe',
             'GITHUB_WORKFLOW_REF':REPOSITORY+'/'+WORKFLOW+'@refs/heads/'+BRANCH}
    need(len(argv)==2 and argv[1] in ROUTES and all(env.get(k)==v for k,v in fixed.items()), 'FIXED_ORDINARY_DIAGNOSTIC_ONLY')
    head=env.get('GITHUB_SHA','');run=env.get('GITHUB_RUN_ID','')
    need(type(head) is str and re.fullmatch('[0-9a-f]{40}',head)
         and env.get('GITHUB_WORKFLOW_SHA')==head and head not in {
             'b393a9057c249335e6cdf4ccbb898d192b0830b8',
             '301aeecde08ba6f169bc3cd837eae6f6ad068219',
             '07bfbee66caa620c59e527536fbf25d1d19f1bcf',
             'aaf146d10ad69dd02733de0d93935f2748d6f751'}
         and type(run) is str and re.fullmatch('[1-9][0-9]{0,19}',run), 'FIXED_ORDINARY_DIAGNOSTIC_ONLY')
    return list(ROUTES[argv[1]])

def read_owner(path):
    path=Path(path).absolute()
    need(path.resolve(strict=True)==path,'LAUNCHER_OWNER_PATH')
    before=path.lstat()
    stamp=lambda s:(s.st_dev,s.st_ino,s.st_mode,s.st_nlink,s.st_uid,s.st_gid,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
    need(stat.S_ISREG(before.st_mode) and before.st_nlink==1 and before.st_size==OWNER_BYTES,'LAUNCHER_OWNER_SHAPE')
    fd=os.open(path,os.O_RDONLY|os.O_CLOEXEC|os.O_NOFOLLOW|os.O_NONBLOCK)
    try:
        need(stamp(os.fstat(fd))==stamp(before) and not os.listxattr(fd),'LAUNCHER_OWNER_CHANGED')
        raw=os.pread(fd,OWNER_BYTES+1,0)
        need(len(raw)==OWNER_BYTES and hashlib.sha256(raw).hexdigest()==OWNER_SHA256,'LAUNCHER_OWNER_PIN')
        need(stamp(os.fstat(fd))==stamp(before)==stamp(path.lstat())
             and path.resolve(strict=True)==path,'LAUNCHER_OWNER_CHANGED')
        return raw
    finally:
        os.close(fd)

def main():
    flags=validate_call(sys.argv,os.environ)
    need(sys.flags.isolated==1 and sys.dont_write_bytecode is True
         and sys.platform=='linux' and os.getuid()==os.geteuid()==os.getgid()==os.getegid()==0,
         'EXACT_ISOLATED_ROOT_INVOCATION_REQUIRED')
    workspace=Path(os.environ['GITHUB_WORKSPACE']).absolute()
    need(workspace.resolve(strict=True)==workspace and Path(__file__).absolute()==workspace/SELF,
         'FIXED_DIAGNOSTIC_SOURCE_LOCATION')
    owner=workspace/OWNER;raw=read_owner(owner)
    # Compile only the exact captured bytes. No unverified reopen or caller flag.
    # The unchanged owner retains its route-specific exclusive custody,
    # policy guards, sealed arguments/filter, process custody and finalization.
    sys.argv=[str(owner),*flags]
    exec(compile(raw,str(owner),'exec'),{'__name__':'__main__','__file__':str(owner)})

if __name__=='__main__':
    main()
