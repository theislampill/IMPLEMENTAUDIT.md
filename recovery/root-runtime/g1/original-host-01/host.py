"""Root’s one-shot original G1 publication and public run readback."""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
DB = ROOT.parent/'root-episode-store.git'
REPO = 'theislampill/IMPLEMENTAUDIT.md'
BRANCH = 'pro/dg16-g1-original-g3-04-20261109'
COMMIT = 'f9ba187e8f5520956f0f16cf13c0a706e8360b96'
TREE = '8390375505282e602759c7976b6bca82a44d5737'
PARENT = '7e2b00b3a2a16fc6033a5eabe4fc795f6249366f'
WF = '.github/workflows/dg16-r5-g1-hosted-episode.yml'
WORKING = ('pro/dg16-g1-tools-control-04-20261109','pro/dg16-g1-carrier-control-04-20261109','pro/dg16-g1-g3-control-04-20261109')
BASE = 'ea61b498d6cffd4747966e7dd716abd3b3cffc1f'

def utc():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def get(*argv): return subprocess.check_output(argv,timeout=25).decode().strip()
def git(*argv):return get('git','--git-dir='+str(DB),*argv)
def api(path):return json.loads(get('gh','api','repos/'+REPO+path))
def encode(obj):return (json.dumps(obj,separators=(',',':'),sort_keys=True)+'\n').encode()
def save(name,obj):
 p=HERE/name
 with p.open('xb') as h:h.write(encode(obj));h.flush();os.fsync(h.fileno())
 assert p.read_bytes()==encode(obj)
def branches(names):
 text=git('ls-remote','origin',*['refs/heads/'+n for n in names])
 return {ref.removeprefix('refs/heads/'):sha for sha,ref in (row.split() for row in text.splitlines())}
def ready():
 assert git('remote','get-url','origin')=='https://github.com/'+REPO+'.git'
 assert git('rev-parse',COMMIT+'^{tree}')==TREE and git('show','-s','--format=%P',COMMIT)==PARENT
 assert len(git('diff-tree','--name-only','--no-commit-id','-r',PARENT,COMMIT).splitlines())==49
 assert branches([BRANCH,*WORKING])==dict(zip(WORKING,(BASE,PARENT,BASE)))
 assert api('/actions/runs?branch='+BRANCH+'&per_page=10')['total_count']==0
 for status in ('queued','in_progress'):
  assert api('/actions/runs?status='+status+'&per_page=1')['total_count']==0
 actor=json.loads(get('gh','api','user'));assert actor['login']=='theislampill' and str(actor['id'])=='266501826' and api('')['permissions']['push'] is True
 wf=json.loads(git('show',COMMIT+':'+WF));assert wf['on']['push']['branches']==[BRANCH] and wf['jobs']['qualify']['timeout-minutes']==75
 assert not (HERE/'PUSH_INTENT.json').exists()
 return {'utc':utc(),'branch':BRANCH,'commit':COMMIT,'tree':TREE,'parent':PARENT,'job_timeout_minutes':75,'waiting_refs':dict(zip(WORKING,(BASE,PARENT,BASE)))}
def publish():
 latest=ready()
 grant=json.loads((HERE/'ROOT_HOST_ADMISSION.json').read_bytes())
 assert grant['admit_one_host'] is True and grant['commit']==COMMIT and grant['tree']==TREE and grant['retry'] is False
 assert grant['source_handoff']=='353593079f92e55178b8c0043bb7c4a94c6bc3cdc7a671ed33061f17b920d60a'
 guard=(HERE/'hooks/pre-push').read_bytes()
 assert hashlib.sha256(guard).hexdigest()==grant['pre_push_sha256']
 save('PUSH_INTENT.json',dict(latest,admission=hashlib.sha256((HERE/'ROOT_HOST_ADMISSION.json').read_bytes()).hexdigest(),expected_ref='absent'))
 cmd=['git','--git-dir='+str(DB),'-c','core.hooksPath='+str((HERE/'hooks').resolve()),'push','--porcelain','origin',COMMIT+':refs/heads/'+BRANCH]
 res=subprocess.run(cmd,capture_output=True,timeout=60);save('PUSH_RESULT.json',{'utc':utc(),'exit':res.returncode,'stdout':res.stdout.decode(errors='replace'),'stderr_sha256':hashlib.sha256(res.stderr).hexdigest()})
 assert res.returncode==0 and branches([BRANCH])=={BRANCH:COMMIT}
 return {'published':COMMIT,'branch':BRANCH}
def capture():
 runs=api('/actions/runs?branch='+BRANCH+'&per_page=10')
 assert runs['total_count']==len(runs['workflow_runs'])==1
 rid=runs['workflow_runs'][0]['id'];run=api('/actions/runs/'+str(rid));commit=api('/git/commits/'+COMMIT);ref=api('/git/ref/heads/'+BRANCH);jobs=api('/actions/runs/'+str(rid)+'/jobs')
 assert run['run_attempt']==1 and run['event']=='push' and run['head_sha']==commit['sha']==ref['object']['sha']==COMMIT and commit['tree']['sha']==TREE and [p['sha'] for p in commit['parents']]==[PARENT]
 assert run['path']==WF and run['head_branch']==BRANCH and run['repository']['full_name']==REPO and run['head_repository']['full_name']==REPO
 assert jobs['total_count']==len(jobs['jobs'])==1 and jobs['jobs'][0]['name']=='qualify';job=jobs['jobs'][0]
 save('ROOT_PUBLICATION_RECEIVING.json',dict(ref=ref,commit=commit,run=run))
 save('JOB.json',dict(id=job['id'],run_id=rid,html_url=job['html_url'],name=job['name']))
 return {'run':rid,'job':job['id'],'url':job['html_url'],'conclusion':job['conclusion']}
def status():
 job_info=json.loads((HERE/'JOB.json').read_bytes());job=api('/actions/jobs/'+str(job_info['id']));arts=api('/actions/runs/'+str(job_info['run_id'])+'/artifacts')
 return {'status':job['status'],'conclusion':job['conclusion'],'active_or_failed':[dict(number=s['number'],name=s['name'],status=s['status'],conclusion=s['conclusion']) for s in job['steps'] if s['status']=='in_progress' or s['conclusion'] in ('failure','cancelled','timed_out')],'artifacts':[{k:a[k] for k in ('name','id','size_in_bytes','digest','expired')} for a in arts['artifacts']]}
if __name__=='__main__':
 cli=argparse.ArgumentParser();cli.add_argument('action',choices=['ready','publish','capture','status']);a=cli.parse_args();print(json.dumps({'ready':ready,'publish':publish,'capture':capture,'status':status}[a.action]()))
