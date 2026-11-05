#!/usr/bin/env python3
"""Emit only bounded public facts from one new C02 result. Never echo diagnostics."""
from pathlib import Path
import argparse, hashlib, json, re, stat

def need(ok, reason):
    if not ok: raise ValueError(reason)

def parse(raw):
    def unique(pairs):
        value={}
        for key,item in pairs:
            need(key not in value,'DUPLICATE_RESULT_KEY');value[key]=item
        return value
    return json.loads(raw,object_pairs_hook=unique)

def summarize(raw):
    data=parse(raw);need(type(data) is dict,'RESULT_OBJECT_REQUIRED')
    status=data.get('status')
    status=status if status in ('PASS','FAIL_PRESERVED_NO_RETRY','IN_PROGRESS','PENDING_CLEANUP_AND_FINAL_INPUT_VERIFICATION') else 'UNRECOGNIZED_RESULT'
    result={'schema':'r5.c02-05.public-summary.v1','status':status,'result_sha256':hashlib.sha256(raw).hexdigest(),'raw_evidence_published':False,'original_acceptance':False,'authentic_provider_usage':False,'original_OR_award':False,'child_JOIN':False,'closure':False,'release':False,'automatic_retry':False}
    for name in ('root_go_sha256','preparation_sha256','independent_review_sha256','input_manifest_sha256'):
        value=data.get(name)
        if type(value) is str and re.fullmatch('[0-9a-f]{64}',value):result[name]=value
    if data.get('post_input_verification')=='PASS':result['post_input_verification']='PASS'
    if data.get('provider_text_and_usage')=='EXPLICIT_LOCAL_EMULATION':result['provider_text_and_usage']='EXPLICIT_LOCAL_EMULATION'
    if type(data.get('audit_state_required')) is bool:result['audit_state_required']=data['audit_state_required']
    if type(data.get('boundary_consumed_version')) is int and data['boundary_consumed_version']==0:result['boundary_consumed_version']=0
    if data.get('expected_final_currentness')=='STALE_AFTER_NEWER_BOUNDARY_EXPECTED':result['expected_final_currentness']='STALE_AFTER_NEWER_BOUNDARY_EXPECTED'
    clean=data.get('shutdown',{})
    if type(clean) is dict:
        result['cleanup']={k:clean[k] for k in ('direct_process_reaped','owned_process_group_absent','native_reader_stopped','native_handles_closed','provider_socket_closed','provider_thread_stopped') if type(clean.get(k)) is bool}
    # Exception values, messages, paths, native/provider text, IDs and refs never pass.
    for name in ('error_type','finalization_error_type'):
        if data.get(name) in ('ValueError','TimeoutError','FileNotFoundError','PermissionError','RuntimeError','KeyboardInterrupt','SystemExit'):result[name]=data[name]
    return result

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--result',required=True);args=parser.parse_args()
    path=Path(args.result);need(path.is_absolute() and path.resolve(strict=True)==path,'CANONICAL_RESULT_REQUIRED')
    info=path.lstat();need(stat.S_ISREG(info.st_mode) and info.st_nlink==1 and info.st_size<=4*1024*1024,'BOUNDED_REGULAR_RESULT_REQUIRED')
    raw=path.read_bytes();after=path.lstat();need((info.st_dev,info.st_ino,info.st_size,info.st_mtime_ns)==(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns),'RESULT_CHANGED')
    print(json.dumps(summarize(raw),sort_keys=True,indent=2))

if __name__=='__main__':main()
