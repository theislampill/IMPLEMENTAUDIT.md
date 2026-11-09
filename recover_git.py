#!/usr/bin/env python3
"""Materialize the immutable public product/host sources and verify every path.
This is a source recovery command. It creates no remote branch and executes no
project hooks, checkout filters from global config, tests, or workflow.
"""
import argparse
import json
import os
from pathlib import Path
import subprocess

REPOSITORY='https://github.com/theislampill/IMPLEMENTAUDIT.md.git'
HERE=Path(__file__).resolve().parent
def require(v,msg):
    if not v:raise RuntimeError(msg)
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('destination',type=Path)
    args=p.parse_args();target=args.destination.absolute()
    require(not os.path.lexists(target) and target.parent.is_dir(),'Choose a new directory in an existing parent')
    indexes=[json.loads((HERE/'recovery/coordinator/git-trees'/(x+'.json')).read_bytes()) for x in ('product','host-g1','host-g2')]
    env={k:v for k,v in os.environ.items() if not k.startswith('GIT_')}
    env.update(GIT_CONFIG_NOSYSTEM='1',GIT_CONFIG_GLOBAL=os.devnull,GIT_TERMINAL_PROMPT='0',GIT_LFS_SKIP_SMUDGE='1')
    def git(*a):
        return subprocess.check_output(['git','-c','core.hooksPath='+os.devnull,'-c','credential.helper=',
            '-c','core.autocrlf=false','-c','core.longpaths=true','-C',str(target),*a],env=env)
    target.mkdir(mode=0o700)
    git('init','-q','--template=')
    git('remote','add','origin',REPOSITORY)
    # Full ancestry of only the pinned commits. No workflow is triggered by fetching.
    git('-c','maintenance.autoDetach=false','fetch','--no-tags','--no-recurse-submodules','origin',
        *[x['commit'] for x in indexes])
    for x in indexes:
        obj=x['commit']
        require(git('rev-parse',obj+'^{commit}').decode().strip()==obj,'commit mismatch')
        require(git('rev-parse',obj+'^{tree}').decode().strip()==x['tree'],'tree mismatch')
        got=[]
        for rec in git('ls-tree','-rlz',obj).split(b'\0'):
            if not rec:continue
            meta,n=rec.split(b'\t',1);mode,kind,oid,size=meta.split()
            require(kind==b'blob','unsupported tree leaf')
            got.append([n.decode('utf-8'),mode.decode(),oid.decode(),int(size)])
        require(got==x['leaves'],'leaf population, Git modes or blob identities differ')
    git('checkout','-q','--detach',indexes[0]['commit'])
    git('fsck','--full','--no-dangling')
    print(json.dumps({'verified':[{k:x[k] for k in ('commit','tree')}|{'leaves':len(x['leaves'])} for x in indexes],
          'worktree':str(target),'checked_out':indexes[0]['commit'],'native_admission':False},indent=2))
if __name__=='__main__':main()
