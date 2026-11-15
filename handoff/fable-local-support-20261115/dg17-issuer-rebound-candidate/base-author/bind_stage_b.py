"""Original B data fields only. No gate, authority, native action or model call issued."""
from pathlib import Path
import argparse,hashlib,json,time
HERE=Path(__file__).absolute().parent
A_SHA='6fb8b07c4274464cd46b84d639e0268348113c46777a4caa764e2b78033f68c9'
ROOT=Path('C:\\workspace\\ai\\improveimplementaudit\\plans\\astra-r3-execution-20261114-01\\dg17-native-20261114-01')
def pin(p):
 p=Path(p);raw=p.read_bytes();return dict(path=str(p),bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest())
def main():
 p=argparse.ArgumentParser();p.add_argument('--independent-post-a',type=Path,required=True);p.add_argument('--independent-sha256',required=True);p.add_argument('--new-store-owner',required=True);args=p.parse_args()
 raw=(HERE/'OPERATION_A.json').read_bytes();assert hashlib.sha256(raw).hexdigest()==A_SHA;a=json.loads(raw);case=Path(a['case']);post=case/'evidence/POST_A.json';actual=json.loads(post.read_bytes())
 assert actual['status']=='STAGE_A_BOUND_CONTEXT_READY_FOR_INDEPENDENT_REVIEW' and actual['thread_start_calls']==1 and actual['model_turns']==1
 assert actual['H0_effects']==actual['trust_effects']==actual['qualifying_events']==0 and actual['native_cleanup']['actor_idle'] is True
 assert time.perf_counter()<actual['window_start_ns']/1e9+570,'No clock reset or expired B preparation'
 independent=pin(args.independent_post_a);assert independent['sha256']==args.independent_sha256
 # Parent authenticates semantic PASS and exact native provenance outside this pure data formatter.
 assert args.new_store_owner and len(args.new_store_owner)<=128 and all(c.isalnum() or c in '-_' for c in args.new_store_owner)
 selected={k:a[k] for k in ['issuer','case','python','bash','fixed_path','expected_codex_home','appserver_argv','rpc_module','owner_approval','local_plugin_selection']}
 selected.update(schema='ordinary.dg17.actual-postA-B-source-binding.v1',status='SOURCE_BOUND_NOT_B_ADMISSION',post_A=pin(post),independent_post_A=independent,constructor=pin(case/'constructor/positive_hook_constructor_v2.py'),constructor_inputs=pin(case/'evidence/CONSTRUCTOR_ACTUAL_INPUTS.json'),constructor_manifest=pin(case/'evidence/CONSTRUCTOR_MANIFEST.json'),config_preimages=pin(case/'evidence/EXACT_THREE_LEAF_PREIMAGES.json'),new_store_owner=args.new_store_owner)
 manifest=json.loads(Path(selected['constructor_manifest']['path']).read_bytes())
 selected['readset']=[pin(HERE/x) for x in ['native_rpc.py','stage_b.py']]+[selected[x] for x in ['owner_approval','post_A','independent_post_A','constructor','constructor_inputs','constructor_manifest','config_preimages']]+[pin(manifest[x]) for x in ['policy_path','hook_proposal_path']]
 selected['readset'] += [pin(v['path']) for v in manifest['source_readset'].values()]
 out=ROOT/'OPERATION_B_BOUND.json';raw=(json.dumps(selected,sort_keys=True,indent=2)+'\n').encode();assert not out.exists();out.write_bytes(raw)
 print(json.dumps(dict(status='SOURCE_BOUND_ONLY_ROOT_B_GRANT_REQUIRED',operation=pin(out),grant_required=dict(issuer=selected['issuer'],stage='B',operation_sha256=hashlib.sha256(raw).hexdigest(),post_A_sha256=selected['post_A']['sha256'],owner_approval_sha256=selected['owner_approval']['sha256'],independent_post_A=independent))))
if __name__=='__main__':main()
