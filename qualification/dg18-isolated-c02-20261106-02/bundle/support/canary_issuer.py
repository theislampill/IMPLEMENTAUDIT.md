#!/usr/bin/env python3
"""Prospective, local canary issuer. No production/native authority.
Verifies an exact user-authorized disposable subject and actual event readback
before emitting an append grant and a separately scoped conditional fresh grant.
"""
import argparse,hashlib,json,pathlib,subprocess
p=argparse.ArgumentParser();p.add_argument('--policy',required=True);p.add_argument('--request',required=True);p.add_argument('--out',required=True);a=p.parse_args()
canon=lambda x:json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode();digest=lambda x:hashlib.sha256(canon(x)).hexdigest()
policy=json.loads(pathlib.Path(a.policy).read_text());r=json.loads(pathlib.Path(a.request).read_text());repo=pathlib.Path(r['repo']).resolve()
assert policy['scope']=='FRESH_CONTROLLED_CANARY_ONLY' and policy['repo']==str(repo) and policy['subject']==r['subject']
assert policy['event_id']==r['observed']['event_id'] and policy['append_authorized'] is True and policy['conditional_fresh_authorized'] is True
assert r['expected_old']==policy['expected_old'] and r['source_cutoff']==policy['source_cutoff']
def git(*args):return subprocess.check_output(['git',*args],cwd=repo)
event=git('cat-file','blob',r['observed']['invalidation_oid']).decode().strip().split('\t');assert event[-2:]==['new-session',policy['event_id']]
for role in ('controller','pointer','marker'):
 assert git('rev-parse',r['refs'][role]).decode().strip()==policy['expected_old'][role]
assert git('rev-parse',r['refs']['invalidation']).decode().strip()==r['observed']['invalidation_oid']
grant={'schema':'implementaudit.c02-issuer-grant.v1','issuer':policy['issuer'],'scope':{k:r['observed'][k] for k in ('controller','claim_id','run_root_identity','pointer_oid','receipt_oid','marker_oid','invalidation_oid','event_id')},'kind':'ERRONEOUS_INVALIDATION','effect':'APPEND_ONLY_NO_CURRENTNESS','code_sha256':r['code_sha256'],'revoked':False}
proposal={'schema':'implementaudit.c02-decision-proposal.v1','issuer':policy['issuer'],'grant_sha256':digest(grant),'evidence_sha256':r['evidence_sha256'],'kind':'ERRONEOUS_INVALIDATION','observation_sha256':digest(r['observed'])};proposal['decision_id']=digest(proposal)
scope=dict(r['subject'],controller_oid=r['expected_old']['controller'],pointer_oid=r['observed']['pointer_oid'],receipt_oid=r['observed']['receipt_oid'],marker_oid=r['observed']['marker_oid'],correction_record_oid='$OBSERVED_EXACT_APPEND',corrected_invalidation_oid=r['observed']['invalidation_oid'],projection_generation_id='G0003',continuity_epoch='G0003',source_cutoff=r['source_cutoff'])
doc={'schema':'implementaudit.c02-configured-owner-decision.v1','issuer':policy['issuer'],'role':'CONTINUITY_ADJUDICATION_OWNER','subject':r['subject'],'decision_id':proposal['decision_id'],'revoked':False,'qualification':'CONTROLLED_NONPROTECTED_FAULT_INJECTION','expected_old':r['expected_old'],'source_cutoff':r['source_cutoff'],'append_grant':grant,'conditional_fresh_grant':{'schema':'implementaudit.c02-fresh-transition-grant.v1','issuer':policy['issuer'],'scope':scope,'effect':'C02_FRESH_TRANSITION','code_sha256':r['code_sha256'],'projection_code_sha256':r['projection_code_sha256'],'revoked':False}}
out=pathlib.Path(a.out);out.mkdir(exist_ok=False);(out/'decision.json').write_bytes(canon(doc));(out/'proposal.json').write_bytes(canon(proposal));(out/'RECEIPT.json').write_bytes(canon({'schema':'dg18.r4.canary-issuer-receipt.v1','scope':policy['scope'],'native_authority':False,'policy_sha256':hashlib.sha256(pathlib.Path(a.policy).read_bytes()).hexdigest(),'request_sha256':hashlib.sha256(pathlib.Path(a.request).read_bytes()).hexdigest(),'decision_sha256':digest(doc),'grant_sha256':digest(grant),'actual_git_event_readback':True,'prospective_policy':True}));print(json.dumps({'status':'ISSUED_EXACT_CONTROLLED_CANARY_GRANTS','out':str(out)}))
