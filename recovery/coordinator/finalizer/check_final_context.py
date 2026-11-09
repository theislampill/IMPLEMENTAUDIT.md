"""Bounded path-routing control; never calls the continuity controller or C5."""
import ast
import copy
import hashlib
import json
import os
import subprocess
from pathlib import Path

CASE=Path(__file__).resolve().parent
SOURCE=Path('/mnt/c/workspace/ai/improveimplementaudit/plans/sol-dg16-staged-execution-20261108/g1-current03-recovered/original-host-failure-01/candidate-v2/run.py')
CONTROL_SOURCE=Path('/mnt/c/workspace/ai/improveimplementaudit/plans/astra-successor-reconciliation-20261108/g1-current04-issuer/sender-route/current04-public-receiver/candidate-02/phase/tree/qualification/dg16-r5-g1-hosted-episode/run.py')
digest=lambda b:hashlib.sha256(b).hexdigest()
sources=[('published',CONTROL_SOURCE),('diagnostic_v2',SOURCE),('corrected',CASE/'run.py')]
new=CASE.joinpath('run.py').read_bytes()
assert digest(new)=='b4c9013c0c665df6c2e66c609f93d5a08c2e12905a7663d3d144419b64b69865'
base=Path('/home/agent/dg16-finalize-git-context-control-01')
assert os.getuid()==os.geteuid()>0 and base.parent.resolve()==base.parent
base.mkdir(mode=0o700)
env={'PATH':'/usr/bin:/bin','LC_ALL':'C','GIT_CONFIG_NOSYSTEM':'1','GIT_CONFIG_GLOBAL':'/dev/null','GIT_TERMINAL_PROMPT':'0'}
for name in ('selected','other'):
 p=base/name;p.mkdir(mode=0o700)
 subprocess.run(['/usr/bin/git','-C',str(p),'init','--quiet','--template='],env=env,check=True)
selected=base/'selected';other=base/'other'
rotation_raw=(CASE/'DISCOVERY_EXCERPT.py').read_bytes()
discover=ast.parse(rotation_raw).body[0]
assert isinstance(discover,ast.Assign) and discover.targets[0].id=='repo'
discovery=compile(ast.Module(body=[discover],type_ignores=[]),'<exact-first-repository-lookup>','exec')
def git(cwd,*args):
    return subprocess.check_output(['/usr/bin/git','-C',str(cwd),*args],env=env,stderr=subprocess.DEVNULL)
def need(ok,why):
    if not ok:raise ValueError(why)
def control(label,argv,seconds):
    assert label=='final-currentness' and argv==['/usr/bin/bash',str(selected/'skills/implementaudit/scripts/claim-run.sh'),'--require-current-continuity','synthetic'] and seconds==30
    context={'Path':Path,'git':git,'os':os}
    exec(discovery,context)
    seen.append(context['repo'].as_posix())
    # Use a real directory identity as the inert comparison value only.
    # No real controller, continuity refs, or currentness claims are synthesized.
    return (1 if force_refusal else 0),str(context['repo']).encode()+b'\n',b''
rows=[]
for name,location in sources:
 body=location.read_bytes();tree=ast.parse(body)
 solve=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='execute')
 original_req=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='require_current')
 guard=next(n for n in ast.walk(solve) if isinstance(n,ast.If) and isinstance(n.test,ast.BoolOp) and any(isinstance(x,ast.Constant) and x.value=='all_step_children_reaped' for x in ast.walk(n.test)) and any(isinstance(stmt,ast.Assign) and 'final_currentness_sha256' in ast.unparse(stmt.targets) for stmt in n.body))
 initial_cwd=next(x for x in ast.walk(solve) if isinstance(x,ast.Expr) and ast.unparse(x)=="os.chdir('/')")
 ordinary=next(x for x in ast.walk(solve) if isinstance(x,ast.If) and ast.unparse(x.test)=="step != 'finalize'")
 assert any(isinstance(x,ast.Expr) and ast.unparse(x)=='os.chdir(source)' for x in ast.walk(ast.Module(body=ordinary.body,type_ignores=[])))
 for variant in (('correct_repo','stale_token','owner_refuses','no_child_custody') if name=='corrected' else ('correct_repo',)):
    seen=[];force_refusal=variant=='owner_refuses'
    state={'controller':'synthetic','all_step_children_reaped':variant!='no_child_custody','receipt':str(selected) if variant!='stale_token' else 'stale_fixture_value'}
    ns=dict(need=need,os=os,digest=digest,OWNER='skills/implementaudit/scripts/claim-run.sh',state=state,source=selected,output=base,command=control)
    block=ast.Module(body=[original_req,copy.deepcopy(guard)],type_ignores=[])
    # Model original neutral '/' with an *unrelated valid* Git repository, which
    # tests the stronger wrong-repository case without touching the user's /.git.
    prior=Path.cwd();os.chdir(other);error=None
    try:
        exec(compile(block,str(location),'exec'),ns)
    except ValueError as e:error=str(e)
    finally:os.chdir(prior)
    got='final_currentness_sha256' in state
    assert got==(name=='corrected' and variant=='correct_repo')
    assert seen==([] if variant=='no_child_custody' else [str(selected if name=='corrected' else other)])
    assert error==('CURRENTNESS_REFUSED' if variant in ('stale_token','owner_refuses') or name!='corrected' else None)
    rows.append({'source':name,'case':variant,'repo_seen':'NONE' if not seen else Path(seen[0]).name,'consumer_succeeded':got,'error':error})
print(json.dumps({'rows':rows,'real_git':'/usr/bin/git','scope':'Git discovery and original function/guard only; marked scratch path stands in for the receipt','real_native_or_controller_calls':0}))
