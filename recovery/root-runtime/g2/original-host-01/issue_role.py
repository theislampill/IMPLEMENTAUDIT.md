"""Root-invoked one-time public receiving grant for the selected, real G2 job."""
import hashlib
import json
import os
from pathlib import Path
import sys
import time

BASE = Path('/home/agent/dg16-g2-current04-public-20261109')
DRIVER = BASE / 'root-operation-driver-01'
ISSUER = '01a1953f-a15b-7811-aa72-3538ebb03562'
TURN = '01a1bf10-00d5-7a31-a177-dd3e45d7cde0'
PINS = {'live':'7de4d38ecb96eae37e1c776adf3a44d9f764841923bc0747c39d7a5ecba815f0',
        'terminal':'7dfaa0643161d10affb7ab196984a7ede9908b97bd85382a4a0b1a244fc0e1a8'}
sha = lambda b: hashlib.sha256(b).hexdigest()

def main(role, observed, host_deadline_ms):
    assert os.geteuid()==os.getuid()>0 and sys.flags.isolated and sys.dont_write_bytecode
    assert role in PINS and DRIVER.resolve(strict=True)==DRIVER
    cfg_raw=(DRIVER/(role+'.configuration.json')).read_bytes()
    assert sha(cfg_raw)==PINS[role]
    cfg=json.loads(cfg_raw);ctx=cfg['context']
    assert cfg['turn_id']==TURN and ctx['run_id']=='42579780645' and ctx['workflow_commit']=='7f618adc702912f760d87f68fe9c94cc419e844c'
    assert observed['bytes'] in range(1,262145) and len(observed['sha256'])==64 and observed['id']>0
    path=DRIVER/(role+'.admission.json')
    out=BASE/'public-receiving'/role
    assert not os.path.lexists(out) and not os.path.lexists(cfg['driver_journal_directory']) and not os.path.lexists(cfg['driver_channel_directory'])
    prep=(DRIVER/'PUBLIC_OPERATOR_PREPARATION.json').read_bytes()
    prepared=json.loads(prep);assert prepared['workflow_commit']==ctx['workflow_commit'] and prepared['actor']==ISSUER
    now=time.time_ns()//1000000
    until=min(now+300000,int(host_deadline_ms)) if role=='live' else now+300000
    assert now<until and (role=='terminal' or until-now>=60000)
    grant=dict(schema='dg16.public-only-operator-admission.v1',issuer_thread=ISSUER,turn=TURN,
               context=ctx,role=role,session_directory=str(out),preparation_sha256=sha(prep),
               receiver_seal_sha256=prepared['public_receiver_seal'],effect_grant=True,
               source_root_write_granted=True,automatic_retry=False,private_or_cipher=False,
               issued_ms=now,expires_ms=until,configuration_sha256=PINS[role],
               actual_public_artifact=observed,
               selected_effects=['one public role','owned public channel writes','owned driver journal writes',
                                 'nine reserved first-party calls','one bounded selected public ZIP fetch'])
    raw=(json.dumps(grant,sort_keys=True,separators=(',',':'))+'\n').encode()
    fd=os.open(path, os.O_CREAT|os.O_WRONLY|os.O_EXCL|os.O_NOFOLLOW,0o600)
    with os.fdopen(fd,'wb') as f:f.write(raw);f.flush();os.fsync(f.fileno())
    assert path.read_bytes()==raw
    print(json.dumps({'path':str(path),'deadline_ms':until,'grant_sha256':sha(raw),'context':ctx,'configuration_sha256':PINS[role],'role':role,'turn_id':TURN}))

if __name__=='__main__':
    main(sys.argv[1], json.loads(sys.argv[2]), int(sys.argv[3]))
