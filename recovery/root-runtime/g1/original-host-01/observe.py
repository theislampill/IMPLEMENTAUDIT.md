"""Capture the selected current public job/artifact and its original-phase ceiling."""
import argparse
import datetime
import json
import time
from pathlib import Path
import types

host = types.ModuleType('bound_local_host')
host.__file__ = str(Path(__file__).resolve().with_name('host.py'))
exec(compile(Path(host.__file__).read_bytes(),host.__file__,'exec'),host.__dict__)

SPEC = {
    'tools': ('dg16-core-host-tools-{}-a1', 'Observe host tools', 600),
    'recipient': ('dg16-core-private-recipient-{}-a1', 'Create fresh recipient request', 600),
    'g3_initial': ('dg16-g1-root-request-{}-1', 'Core g3-receive', 300),
    'g3_final': ('dg16-g1-original-request-{}-1', 'Core g3-consume', 600),
    'terminal': ('dg16-g1-hosted-{}-1', None, 300),
    'failure': ('dg16-g1-retention-failure-{}-1', None, 300),
}

def observe(phase):
    job_info=json.loads((host.HERE/'JOB.json').read_bytes());rid=job_info['run_id']
    job=host.api('/actions/jobs/'+str(job_info['id']))
    listing=host.api('/actions/runs/'+str(rid)+'/artifacts?per_page=100')
    now=time.time_ns()//1000000
    assert job['id']==job_info['id'] and job['run_id']==rid and job['head_sha']==host.COMMIT and job['name']=='qualify'
    assert listing['total_count']==len(listing['artifacts'])
    fmt,stepname,seconds=SPEC[phase];rows=[a for a in listing['artifacts'] if a['name']==fmt.format(rid) and not a['expired']]
    if not rows:return {'available':False,'phase':phase,'job_status':job['status']}
    assert len(rows)==1
    if stepname:
        assert job['status']=='in_progress'
        step=next(s for s in job['steps'] if s['name']==stepname)
        opened=int(datetime.datetime.fromisoformat(step['started_at'].replace('Z','+00:00')).timestamp()*1000)
    else:
        assert job['status']=='completed'
        # This is a new bounded public terminal acquisition, not a renewal of a live hold.
        opened=now
    expiry=opened+seconds*1000
    assert now<expiry, 'existing phase budget exhausted'
    status={'job':job,'artifact':rows[0],'observed_unix_ms':now}
    host.save('CURRENT_'+phase+'.json',status)
    window={'opened':opened,'ends':expiry}
    host.save('WINDOW_'+phase+'.json',window)
    return {'available':True,'phase':phase,'artifact':rows[0]['id'],'artifact_bytes':rows[0]['size_in_bytes'],'job_status':job['status'],**window}

if __name__=='__main__':
    cli=argparse.ArgumentParser();cli.add_argument('phase',choices=SPEC);print(json.dumps(observe(cli.parse_args().phase)))
