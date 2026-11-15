"""Copy the frozen base author set, changing only the issuer and the two literals that pin the base operation hash."""
import json,sys,hashlib
from pathlib import Path
src,dst=Path(sys.argv[1]),Path(sys.argv[2]); OLD='01a1cf82-cdd6-7053-b7b7-32f5c3d93d21'; NEW='PRO-EXECUTOR-01'
sha=lambda b:hashlib.sha256(b).hexdigest()
enc=lambda v:(json.dumps(v,indent=2,sort_keys=True,ensure_ascii=False)+'\n').encode()
out={p.name:p.read_bytes() for p in src.iterdir() if p.name!='__pycache__'}; assert len(out)==10
raw=out['OPERATION_A.json']; old_sha=sha(raw); op=json.loads(raw)
assert enc(op)==raw and op['issuer']==OLD and sum(v.count(OLD.encode()) for v in out.values())==1
op['issuer']=NEW
op['issuer_rebinding']={'previous_issuer':OLD,'successor':NEW,'role':'/root successor designated by owner; not Astra',
  'status':'CANDIDATE for PRO-EXECUTOR-01 review; prepared by Claude Fable 5.2 as local support, not adopted',
  'scope':'Issuer identity for DG17 Stage A/B grants only. Not a native grant.','historical_base_operation_sha256':old_sha}
out['OPERATION_A.json']=enc(op); new_sha=sha(out['OPERATION_A.json'])
for n in ['parent_launch_a.py','bind_stage_b.py']:
    assert out[n].count(old_sha.encode())==1; out[n]=out[n].replace(old_sha.encode(),new_sha.encode())
assert sum(v.count(old_sha.encode()) for k,v in out.items() if k!='OPERATION_A.json')==0
for n,b in sorted(out.items()): (dst/n).open('xb').write(b)
print(json.dumps({'historical_base_operation':old_sha,'rebound_base_operation':new_sha,'changed':['OPERATION_A.json','parent_launch_a.py','bind_stage_b.py']}))
