"""Read-only local receiving of two retained public Git fixtures. No C5 session."""
import ast
import configparser
import gc
import hashlib
import json
import os
from pathlib import Path
import re
import stat

here=Path('/mnt/c/workspace/ai/improveimplementaudit')
program=here/'plans/sol-dg16-staged-execution-20261108/g1-current03-recovered/original-host-failure-01/source/qualify-work-graph-prefix.py'
raw=program.read_bytes()
expected_sha='ff5dbdce5b4419268b0fc11c4659763ad68d40e32f18f721b6093a7dd269b7ab'
assert hashlib.sha256(raw).hexdigest()==expected_sha
tree=ast.parse(raw)
functions={'snapshot_tree','validate_git_namespace','digest','identity','open_directory','safe_name'}
items=[x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name in functions or isinstance(x,ast.Assign) and isinstance(x.targets[0],ast.Name) and x.targets[0].id=='SOURCE_BOUNDS']
assert len(items)==len(functions)+1
bindings=dict(configparser=configparser,hashlib=hashlib,os=os,Path=Path,stat=stat,re=re)
exec(compile(ast.Module(body=items,type_ignores=[]),str(program),'exec'),bindings)
base=Path('/home/agent/sol-git256-public-clone-20261109-01')
assert base.resolve(strict=True)==base and base.stat().st_uid==os.geteuid()>0
rows=[]
for arm in ('default','foreground'):
    target=base/arm
    assert target.resolve(strict=True)==target and target.stat().st_uid==os.getuid()
    objects={}
    state,stamps=bindings['snapshot_tree'](target,objects,bindings['SOURCE_BOUNDS'])
    error=None
    try: bindings['validate_git_namespace'](state,objects)
    except ValueError as exc:error=str(exc)
    locks=sorted(k for group in ('files','directories') for k in state[group] if k.endswith('.lock'))
    config=state['files']['.git/config']
    rows.append(dict(arm=arm,source_bytes=sum(v['bytes'] for v in state['files'].values()),files=len(state['files']),dirs_including_root=len(state['directories']),config_sha256=config['sha256'],locks=locks,namespace_guard='ACCEPTED' if error is None else 'REFUSED',refusal=error))
    del objects,state,stamps;gc.collect()
print(json.dumps({'scope':'All actual files, directories and config bytes from two public scratch roots; unchanged maintained acquisition and namespace guard, not a hosted C5/G1 execution. No files written to either root.','source':expected_sha,'bounds':bindings['SOURCE_BOUNDS'],'results':rows}))
