"""Root-invoked event binding for the actual published G1 run. No provider calls."""
import argparse
import hashlib
import json
import os
import subprocess
import time
from pathlib import Path
import types

BASE=Path('/home/agent/dg16-g1-current04-operators')
RECEIVER=BASE/'public-receiver-02'
PUB=Path('/mnt/c/workspace/ai/improveimplementaudit/plans/astra-successor-reconciliation-20261108/g1-current04-issuer/original-host-01')
ISSUER=BASE/'root-event-helpers-02/g1_event_config_corrected.py'
ISSUER_SHA='af5925d5106209fcc26c26b28c48d960573038b2364f532acbda1c8d7bdf9229'
HEAD='f9ba187e8f5520956f0f16cf13c0a706e8360b96'
sha=lambda b:hashlib.sha256(b).hexdigest()
enc=lambda v:(json.dumps(v,sort_keys=True,separators=(',',':'))+'\n').encode()
now=lambda:time.time_ns()//1000000
def fresh(path,data):
    fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
    with os.fdopen(fd,'wb') as w:w.write(data);w.flush();os.fsync(w.fileno())
    assert path.read_bytes()==data
def directory(p):
    if not os.path.lexists(p):p.mkdir(mode=0o700)
    assert p.resolve(strict=True)==p and p.stat().st_uid==os.getuid() and p.stat().st_mode&0o777==0o700
def row(path):
    b=path.read_bytes();return dict(path=str(path),sha256=sha(b))
def issue(action,src,out):
    assert sha(ISSUER.read_bytes())==ISSUER_SHA
    x=subprocess.run(['/usr/bin/python3','-I','-B',str(ISSUER),action,str(src),str(out)],capture_output=True,timeout=12)
    if x.returncode:raise RuntimeError(x.stderr.decode(errors='replace')[-400:]+x.stdout.decode(errors='replace')[-300:])
    return json.loads(x.stdout)
def main():
    cli=argparse.ArgumentParser();cli.add_argument('stage',choices=['role','tools','g3-decision','control','receipt']);cli.add_argument('phase');cli.add_argument('shell_title');cli.add_argument('--external-body',type=Path);cli.add_argument('--review-input',type=Path);a=cli.parse_args()
    assert os.geteuid()==os.getuid()>0
    h=json.loads((PUB/'ROOT_PUBLICATION_RECEIVING.json').read_bytes());run=h['run'];rid=str(run['id'])
    assert run['head_sha']==HEAD and run['run_attempt']==1 and run['head_branch']=='pro/dg16-g1-original-g3-04-20261109'
    ctx=dict(repository='theislampill/IMPLEMENTAUDIT.md',branch=run['head_branch'],workflow_path=run['path'],job_name='qualify',workflow_commit=HEAD,run_id=rid,run_attempt=1)
    phase=a.phase;assert phase in ('tools','recipient','g3_initial','g3_final','terminal','failure')
    episode=BASE/('actual-current04-'+rid);directory(episode)
    for sub in ('sessions','control-sessions','event-configurations'):directory(RECEIVER/sub)
    key='r'+rid+'-'+phase;out=RECEIVER/'event-configurations'
    session=RECEIVER/'sessions'/key
    initial_key='r'+rid+'-g3_initial'; first_session=RECEIVER/'sessions'/initial_key
    first_body=out/(initial_key+'-publish')/'DECISION.json'
    first_publication=RECEIVER/'control-sessions'/(initial_key+'-publish')/'RECEIVING.json'
    pub=episode/'HOST_PUBLICATION_ROOT_RECEIVING.json'
    if not pub.exists():fresh(pub,(PUB/'ROOT_PUBLICATION_RECEIVING.json').read_bytes())
    assert pub.read_bytes()==(PUB/'ROOT_PUBLICATION_RECEIVING.json').read_bytes()
    srcmod=ISSUER.read_bytes();assert sha(srcmod)==ISSUER_SHA
    E=types.ModuleType('root_event_issuer');E.__file__=str(ISSUER);exec(compile(srcmod,E.__file__,'exec'),E.__dict__)
    R=E.receiver();s=R.Sources()
    if a.stage=='receipt':
        got=R.parse(R.read(session/'RECEIVING.json'));print(json.dumps({'session':str(session),'descriptor':R.desc(R.encode(got)),'phase':phase,'receipt':got}));return
    w=json.loads((PUB/('WINDOW_'+phase+'.json')).read_bytes())
    start,end=w['opened'],w['ends']
    if phase=='g3_final':
        first=E.received_session(R,s,str(first_session));end=min(end,R.parse(first['files']['ROOT_REQUEST.json'])['shared_expires_unix_ms'])
    assert start<=now()<end
    if a.stage=='role':
        p=episode/('status-'+phase+'.json');fresh(p,(PUB/('CURRENT_'+phase+'.json')).read_bytes())
        val=dict(schema='dg16.g1-root-role-status-issuance-input.v1',phase=phase,context=ctx,window_opened_unix_ms=start,deadline_unix_ms=end,shell_title=a.shell_title,initial_session=str(first_session) if phase=='g3_final' else None,actual_root_decision=row(first_body) if phase=='g3_final' else None,publication_receiving=row(pub),status_readback=row(p))
        source=episode/('role-input-'+phase+'.json');fresh(source,enc(val));dest=out/key
        issue('issue-role-from-status',source,dest)
        print(json.dumps({'selection':json.loads((dest/'WINDOWS_SELECTION.json').read_bytes()),'deadline':end,'session':str(session)}));return
    prev=None;initial=None
    if phase=='g3_final':prev=E.received_session(R,s,str(first_session));initial=first_body.read_bytes()
    got=E.received_session(R,s,str(session),prev,initial)
    if a.stage=='tools':
        assert phase=='tools';observed=R.parse(got['files']['HOST_TOOL_OBSERVATION.json']);tool=s.H.declaration(s.binding)
        maxend=observed['issued_unix_ms']+1000*(tool['observation_seconds']+tool['adoption_seconds']+s.binding['limits']['acquisition_seconds'])
        val=dict(schema='dg16.g1-root-tools-decision-input.v1',artifact_session=str(session),issued_unix_ms=now(),expires_unix_ms=maxend)
        source=episode/'tools-issue-input.json';fresh(source,enc(val));dest=out/(key+'-decision');issue('issue-tools-decision',source,dest)
        print(json.dumps({'body':row(dest/'DECISION.json')}));return
    if a.stage=='g3-decision':
        assert phase in ('g3_initial','g3_final')
        req=R.requirements(s,got)
        decision=dict(req['required_fixed_fields'])
        decision['issued_unix_ms']=now()
        if phase=='g3_final':
            assert a.review_input is not None
            # Root calls this only after personally receiving the actual reviewer,
            # both decision bodies, their applicability, and every row/gate.
            review=R.parse(R.read(a.review_input,65536))
            assert set(review)=={'independent_review','source_applicability','original_rows','gate_decisions','final_request_sha256'}
            assert review['final_request_sha256']==R.sha(got['files']['FINAL_REQUEST.json'])
            decision.update(independent_review_sha256=R.sha(E.bound(review['independent_review'],65536)),source_applicability_review_sha256=R.sha(E.bound(review['source_applicability'],65536)),original_rows=review['original_rows'],gate_decisions=review['gate_decisions'])
        body=R.encode(decision)
        assert set(decision)==set(req['required_fixed_fields'])|set(req['root_supplied_fields'])
        R.validate_control(s,got,body,now())
        dest=episode/(phase+'-actual-root-decision.json');fresh(dest,body)
        print(json.dumps({'body':row(dest)}));return
    assert phase in ('tools','g3_initial','g3_final')
    body=out/(key+'-decision')/'DECISION.json' if phase=='tools' else a.external_body or episode/(phase+'-actual-root-decision.json')
    assert body and body.resolve(strict=True)==body
    if phase!='tools':end=min(end,R.parse(got['files']['ROOT_REQUEST.json' if phase=='g3_initial' else 'FINAL_REQUEST.json'])['expires_unix_ms'])
    parent_input=episode/('parent-ref-'+phase+'.json');fresh(parent_input,(PUB/('PARENT_'+phase+'.json')).read_bytes())
    req=R.requirements(s,got);url='https://api.github.com/repos/'+ctx['repository']+'/git/ref/heads/'+req['branch']
    ref=R.unwrap_control(parent_input.read_bytes(),url);parent=ref['object']['sha'];assert ref['ref']=='refs/heads/'+req['branch'] and ref['object']['type']=='commit'
    val=dict(schema='dg16.g1-root-control-issuance-input.v1',artifact_session=str(session),decision=row(body),parent_sha=parent,parent_ref_result=row(parent_input),window_opened_unix_ms=start,deadline_unix_ms=end,shell_title=a.shell_title,initial_session=str(first_session) if phase=='g3_final' else None,initial_body=row(first_body) if phase=='g3_final' else None,initial_publication=row(first_publication) if phase=='g3_final' else None)
    source=episode/('control-input-'+phase+'.json');fresh(source,enc(val));dest=out/(key+'-publish');issue('issue-control',source,dest)
    plan=(dest/'TRUSTED_PUBLICATION_PLAN.json').read_bytes()
    print(json.dumps({'selection':json.loads((dest/'WINDOWS_SELECTION.json').read_bytes()),'deadline':end,'trusted_plan':plan.decode(),'trusted_sha':sha(plan)}))

if __name__=='__main__':main()
