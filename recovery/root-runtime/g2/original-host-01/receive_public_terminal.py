"""Join the genuine public archive to the same job's original public transport lines."""
from pathlib import Path
import hashlib
import json
import os
import sys
import types

ROOT = Path('/home/agent/dg16-g2-current04-public-20261109')
SLOT = ROOT/'public-receiving/terminal'
OUT = Path('/mnt/c/workspace/ai/improveimplementaudit/plans/astra-successor-reconciliation-20261108/g2-production-issuer-01/original-host-01')
rawlog = sys.stdin.buffer.read(16*1024**2+1)
assert 0 < len(rawlog) <= 16*1024**2
receiver = ROOT/'bound-public-receiver/public_receiver.py'
seal = (ROOT/'bound-public-receiver/SEAL.json').read_bytes()
sha = lambda b: hashlib.sha256(b).hexdigest()
assert sha(seal) == '2f86492f085eae40ab35530fe1d59773116841c120b5a9bd50421e5bdf02275d'
row = next(r for r in json.loads(seal)['members'] if r['path']=='public_receiver.py')
raw = receiver.read_bytes()
assert sha(raw)==row['sha256'] and len(raw)==row['bytes']
R = types.ModuleType('root_installed_public_terminal')
R.__file__ = str(receiver)
exec(compile(raw,str(receiver),'exec'),R.__dict__)
archive=R.acquire(SLOT/'ARTIFACT.zip',262144)
assert len(archive)==16572 and sha(archive)=='6b869e5e7543703e7f70def6119d4f7a7ce1aa0a9868ee7f0d11ba41542d1f31'
files=R.decode_zip(archive,'terminal'); metadata=R.acquire(SLOT/'PUBLIC_METADATA.json',262144)
got=R.inspect(files,'terminal',run_id='42579780645',workflow_commit='7f618adc702912f760d87f68fe9c94cc419e844c',metadata=R.strict(metadata),archive=R.desc(archive))
got['terminal_log_join']=R.match_terminal_log(files,rawlog)
assert got['terminal_log_join']['all_seven_exact']
out=OUT/'public-terminal';out.mkdir()
def save(name,b):
    with (out/name).open('xb') as f:f.write(b);f.flush();os.fsync(f.fileno())
    assert (out/name).read_bytes()==b
save('ARTIFACT.zip',archive);save('PUBLIC_METADATA.json',metadata)
save('PROVIDER_RECEIVING.json',R.acquire(SLOT/'PROVIDER_RECEIVING.json',262144))
save('ROOT_SEMANTIC_RECEIVING.json',(json.dumps(got,sort_keys=True,indent=2)+'\n').encode())
print(json.dumps({'terminal':got['status'],'matched_seven':True,'archive':R.desc(archive),'log':R.desc(rawlog),'file_names':list(files),'public_fields':list(got['public'])}))
