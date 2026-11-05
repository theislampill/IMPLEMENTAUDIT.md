#!/usr/bin/env python3
"""Emit only bounded public facts from one new C02 result. Never echo diagnostics."""
from pathlib import Path
import argparse, hashlib, json, re, stat

DIAGNOSTIC_SCHEMA = 'r5.c02-06.diagnostics.v1'
DIAGNOSTIC_BYTES = 2048
DIAGNOSTIC_PHASES = (
    'AUTHORIZED', 'SUBJECT_INIT', 'ROTATION', 'SOURCE_LOAD', 'BINARY_EXTRACT', 'BINARY_VERSION',
    'PROVIDER_SETUP', 'NATIVE_LAUNCH', 'NATIVE_INIT', 'THREAD_START', 'SEED_TURN', 'SOURCE_SELECT',
    'C02_INTERVAL', 'CONTROLLED_FAULT', 'APPEND_MATERIALIZE', 'MATERIALIZE_RETRY', 'APPEND',
    'APPEND_RETRY', 'C02_NEGATIVES', 'FRESH_GRANT', 'CORRECTION', 'CORRECTION_RETRY',
    'CORRECTED_READBACK', 'LEASE_WITHDRAW', 'LATER_COMPACT', 'LATER_RESUME', 'LATER_REGISTER',
    'LATER_PENDING', 'LATER_INVALIDATE', 'LATER_READBACK', 'CLEANUP', 'INPUT_VERIFY', 'COMPLETE')
DIAGNOSTIC_MILESTONES = (
    'INIT', 'ROTATE', 'BIN', 'PROVIDER', 'NATIVE', 'RPC_INIT', 'THREAD', 'SEED', 'SELECT',
    'INTERVAL', 'FAULT', 'REVISIONS', 'REV_RETRY', 'APPEND', 'APP_RETRY', 'NEGATIVE',
    'FRESH_GRANT', 'CORRECT', 'CORR_RETRY', 'READBACK', 'WITHDRAW', 'COMPACT', 'RESUME',
    'REGISTER', 'PENDING', 'INVALIDATE', 'RECEIVE', 'CLEANUP', 'INPUTS')
DIAGNOSTIC_CATEGORIES = (
    'TYPE_ERROR', 'KEY_ERROR', 'INDEX_ERROR', 'ATTRIBUTE_ERROR', 'VALUE_ERROR', 'RUNTIME_ERROR',
    'ASSERTION_ERROR', 'TIMEOUT', 'SUBPROCESS_TIMEOUT', 'FILE_NOT_FOUND', 'PERMISSION_ERROR',
    'OS_ERROR', 'MEMORY_ERROR', 'INTERRUPTED', 'SYSTEM_EXIT', 'OTHER')
DIAGNOSTIC_SITES = {
    'execute': 'EXECUTE', '__init__': 'INIT', 'command': 'COMMAND', 'check_bindings': 'BIND',
    'extract_owned_binary': 'BINARY', 'configure_native': 'CONFIG', 'native_call': 'CALL',
    'completed_turn': 'TURN', 'fixed_selection': 'SELECT', 'controlled_transaction': 'C02',
    'pending_tail': 'TAIL', 'owned': 'OWNED', 'expect_owner_refusal': 'NEGATIVE',
    'receive': 'RECEIVE', 'check_binary_custody': 'CUSTODY', 'shutdown': 'CLEANUP',
    'source_still_withdrawn': 'WITHDRAW', 'require': 'REQUIRE', 'read_regular': 'READ',
    'physical': 'PHYSICAL', 'verify_inputs': 'INPUTS', 'streamed_pin': 'STREAM',
    'write': 'WRITE', 'load': 'LOAD', 'gate': 'GATE', 'fresh_bodies': 'BODIES'}


def diagnostic_projection(value):
    """Validate a closed observation; absent completion never proves no effect."""
    def check(ok):
        if not ok:
            raise ValueError('MALFORMED_DIAGNOSTICS_REFUSED')
    check(type(value) is dict and set(value) ==
          {'schema', 'phase', 'completed', 'failure', 'finalization_failure'})
    check(value['schema'] == DIAGNOSTIC_SCHEMA and type(value['schema']) is str)
    check(type(value['phase']) is str and value['phase'] in DIAGNOSTIC_PHASES)
    completed = value['completed']
    check(type(completed) is list and len(completed) <= len(DIAGNOSTIC_MILESTONES)
          and all(type(item) is str and item in DIAGNOSTIC_MILESTONES for item in completed))
    indices = [DIAGNOSTIC_MILESTONES.index(item) for item in completed]
    check(indices == sorted(set(indices)))
    output = {'schema': DIAGNOSTIC_SCHEMA, 'phase': value['phase'], 'completed': list(completed)}
    for name in ('failure', 'finalization_failure'):
        failure = value[name]
        if failure is None:
            output[name] = None
            continue
        check(type(failure) is dict and set(failure) == {'phase', 'category', 'sites'})
        check(type(failure['phase']) is str and failure['phase'] in DIAGNOSTIC_PHASES)
        check(type(failure['category']) is str and failure['category'] in DIAGNOSTIC_CATEGORIES)
        sites = failure['sites']
        check(type(sites) is list and len(sites) <= 3)
        for site in sites:
            check(type(site) is str and len(site) <= 24 and re.fullmatch('[A-Z_]+:[1-9][0-9]{0,4}', site) is not None)
            check(site.split(':', 1)[0] in DIAGNOSTIC_SITES.values())
        output[name] = {'phase': failure['phase'], 'category': failure['category'], 'sites': list(sites)}
    check(len(json.dumps(output, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()) + 1 <= DIAGNOSTIC_BYTES)
    return output


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
    result={'schema':'r5.c02-06.public-summary.v1','status':status,'result_sha256':hashlib.sha256(raw).hexdigest(),'raw_evidence_published':False,'original_acceptance':False,'authentic_provider_usage':False,'original_OR_award':False,'child_JOIN':False,'closure':False,'release':False,'automatic_retry':False}
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
    try:
        result['diagnostics'] = diagnostic_projection(data['diagnostics'])
    except KeyError:
        result['diagnostics'] = {'status': 'DIAGNOSTICS_UNAVAILABLE'}
    except (ValueError, TypeError):
        result['diagnostics'] = {'status': 'MALFORMED_DIAGNOSTICS_REFUSED'}
    return result

def summarize_checkpoint(raw):
    need(type(raw) is bytes and len(raw) <= DIAGNOSTIC_BYTES, 'DIAGNOSTIC_BYTE_BOUND')
    value = diagnostic_projection(parse(raw))
    return {'schema': 'r5.c02-06.public-summary.v1', 'status': 'RESULT_UNAVAILABLE_CHECKPOINT_ONLY',
        'checkpoint_sha256': hashlib.sha256(raw).hexdigest(), 'diagnostics': value,
        'raw_evidence_published': False, 'original_acceptance': False, 'authentic_provider_usage': False,
        'original_OR_award': False, 'child_JOIN': False, 'closure': False, 'release': False,
        'automatic_retry': False}

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--result',required=True);args=parser.parse_args()
    path=Path(args.result);need(path.is_absolute() and path.resolve(strict=True)==path,'CANONICAL_RESULT_REQUIRED')
    info=path.lstat();need(stat.S_ISREG(info.st_mode) and info.st_nlink==1 and info.st_size<=4*1024*1024,'BOUNDED_REGULAR_RESULT_REQUIRED')
    raw=path.read_bytes();after=path.lstat();need((info.st_dev,info.st_ino,info.st_size,info.st_mtime_ns)==(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns),'RESULT_CHANGED')
    print(json.dumps(summarize(raw),sort_keys=True,indent=2))

if __name__=='__main__':main()
