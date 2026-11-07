#!/usr/bin/env python3
"""One prospective hosted C5 operation, called by the reviewed hosted adapter.

The adapter owns actual fresh initialization/currentness and bounded process
custody. It supplies a real require_current callback, not an imported receipt
decision. Provider05 and the exact ordinary Git subject must already be
provisioned. This module never provisions, dispatches, uploads, or grants G1.
All outputs are PRIVATE; public export requires the adapter's closed projection.
"""
import hashlib
import json
import math
import os
from pathlib import Path
import stat
import time
import types

MAX_PRIVATE_JSON=4*1024**2
SOURCE_TREE='6d3f972a424583f9d3d56d8bfd9ae11cf36ecf6e'
LOADER_SHA256='2989ba6cb8da6f52f9a2f94f27d141a931a0bffb8ebd03172091b170646d8017'
PROFILE='FIXED_GENUINE_C5_SHARED_IMAGE_R5_HOSTED_UBUNTU24_SINGLE_COPY_20261105_V1'
REVISION='R5_HOSTED_UBUNTU24_INNER_CAPTURE_SOURCE_20261107_V4'
NSS_ENUMS=frozenset(('files','systemd','compat','db','nis','nisplus','sss','ldap','winbind',
    'resolve','dns','mdns','mdns4','mdns6','mdns_minimal','mdns4_minimal','mdns6_minimal',
    'myhostname','mymachines'))


def need(value, code):
    if not value: raise ValueError(code)


def encode(value):
    return (json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode()


def sha(raw): return hashlib.sha256(raw).hexdigest()


def stamp(info):
    return (info.st_dev,info.st_ino,info.st_mode,info.st_nlink,info.st_size,
        info.st_mtime_ns,info.st_ctime_ns,info.st_uid,info.st_gid)


def read_regular(path, maximum):
    path=Path(path);before=path.lstat()
    need(stat.S_ISREG(before.st_mode) and before.st_nlink==1 and 0<=before.st_size<=maximum,
         'PRIVATE_INPUT_NOT_ORDINARY_BOUNDED_FILE')
    fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK|os.O_CLOEXEC)
    try:
        need(stamp(os.fstat(fd))==stamp(before) and not os.listxattr(fd),'PRIVATE_INPUT_CHANGED')
        with os.fdopen(fd,'rb',closefd=False) as stream: raw=stream.read(maximum+1)
        need(len(raw)==before.st_size and stamp(os.fstat(fd))==stamp(before)
             and stamp(path.lstat())==stamp(before),'PRIVATE_INPUT_CHANGED')
        return raw
    finally: os.close(fd)


def write_once(path, raw, maximum=MAX_PRIVATE_JSON):
    need(type(raw) is bytes and len(raw)<=maximum,'PRIVATE_OUTPUT_BOUND')
    fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,0o600)
    try:
        with os.fdopen(fd,'wb',closefd=False) as stream:
            stream.write(raw);stream.flush();os.fsync(fd)
        os.fchmod(fd,0o400)
    finally: os.close(fd)
    need(read_regular(path,maximum)==raw,'PRIVATE_OUTPUT_READBACK')
    return dict(bytes=len(raw),sha256=sha(raw))


def nss_token_observation(config):
    """Bounded data projection, not NSS admission and not a config rewriter."""
    need(type(config) is bytes and 0<len(config)<=65536 and b'\0' not in config,'NSS_INPUT_SHAPE')
    text=config.decode('ascii','strict')
    lines=[line.split('#',1)[0].strip() for line in text.splitlines()]
    result=dict(schema='dg16.c5-nss-token-observation.v1',raw_bytes=len(config),raw_sha256=sha(config),
        scope='ACTUAL_PARSED_DIAGNOSTIC_ONLY_NO_SERVICE_ADMISSION',categories={})
    for category in ('passwd','group'):
        selected=[line for line in lines if line.partition(':')[0].strip()==category]
        canonical=encode(selected)
        row=dict(row_count=len(selected),parsed_rows_bytes=len(canonical),parsed_rows_sha256=sha(canonical),
            tokens=[],token_count=0,classification='AMBIGUOUS_OR_MISSING',matches_files_only_syntax=False)
        if len(selected)==1:
            tokens=selected[0].partition(':')[2].split()
            row.update(token_count=len(tokens),matches_files_only_syntax=tokens==['files'])
            if len(tokens)>16 or any(len(token)>128 for token in tokens):
                row['classification']='TOKEN_BOUND_REFUSED'
            else:
                for token in tokens:
                    if token in NSS_ENUMS: row['tokens'].append(dict(kind='KNOWN_SERVICE',value=token))
                    else: row['tokens'].append(dict(kind='WITHHELD_TOKEN',bytes=len(token),sha256=sha(token.encode('ascii'))))
                row['classification']=('FILES_ONLY' if tokens==['files'] else
                    'ACTION_SYNTAX_UNQUALIFIED' if any('[' in token or ']' in token for token in tokens) else
                    'FILES_FIRST_OTHER_UNQUALIFIED' if tokens and tokens[0]=='files' else 'OTHER_UNQUALIFIED')
        result['categories'][category]=row
    need(len(encode(result))<=8192,'NSS_DIAGNOSTIC_BOUND')
    return result


def load_selected(source):
    path=source/'scripts/load-work-graph-c5-executor.py'
    raw=read_regular(path,1024**2)
    need(sha(raw)==LOADER_SHA256,'LOADER_PIN_DIFFERS')
    module=types.ModuleType('r5_hosted_c5_selected_loader');module.__file__=str(path)
    exec(compile(raw,str(path),'exec'),module.__dict__)
    need(module.R5_HOSTED_PROFILE==PROFILE and module.R5_INNER_CAPTURE_SOURCE_REVISION==REVISION,'PROFILE_SELECTION_DIFFERS')
    engine=module._Engine(PROFILE,source_revision=REVISION).load()
    need(read_regular(path,1024**2)==raw,'LOADER_CHANGED_DURING_LOAD')
    engine.CHECK()
    return engine


def child_terminal_confirmed(output, owner_invoked):
    if not owner_invoked: return True
    try:
        value=json.loads(read_regular(output/'producer/closing-custody.json',MAX_PRIVATE_JSON))
        custody=value.get('custody')
        return (value.get('schema')=='implementaudit.genuine-c5-closing-custody.v1'
            and value.get('cleanup_errors')==[] and type(custody) is dict
            and custody.get('wait4_reaped') is True and custody.get('group_absent') is True)
    except (OSError,ValueError,TypeError): return False


def qualify(source, private_output, expected_source, require_current, before_producer):
    """One actual pair with same-live-job raw receiving and measured enclosure.

    A fresh real currentness callback and a supervising bounded host process are
    integration prerequisites. They cannot be replaced by this function's JSON.
    The returned interval includes both callback calls, loading, acquisition,
    the actual producer, repeated raw receiving, final source checks and close.
    Its duration is observed, not silently compared with the different120-second
    maintained producer-watchdog interval. All time subtraction is zero.
    """
    began=time.monotonic_ns()
    source=Path(source).absolute();output=Path(private_output).absolute()
    need(callable(require_current),'ACTUAL_CURRENTNESS_CALLBACK_REQUIRED')
    need(callable(before_producer),'PROSPECTIVE_USEFUL_WORK_SELECTION_REQUIRED')
    need(type(expected_source) is dict and set(expected_source)=={'source_commit','source_tree'}
         and expected_source['source_tree']==SOURCE_TREE
         and all(type(v) is str and len(v)==40 and all(c in '0123456789abcdef' for c in v) for v in expected_source.values()),
         'EXACT_PUBLISHED_SUBJECT_REQUIRED')
    need(os.getuid()==os.geteuid()==os.getgid()==os.getegid()==0,'ACTUAL_UID_GID_ZERO_REQUIRED')
    need(not output.exists() and not output.is_symlink() and not output.is_relative_to(source),'FRESH_PRIVATE_OUTPUT_REQUIRED')
    output.mkdir(mode=0o700)
    phase='CURRENTNESS_BEFORE';session=engine=None;failure=None;closing_failure=None;received=False
    facts=dict(schema='dg16.g1-hosted-profile-operation.v1',authority='NONE',profile=PROFILE,
        source=dict(expected_source),status='INCOMPLETE',original_acceptance=False,original_G1_award=False,
        phase=phase,private_records={},producer_owner_invoked=False,raw_receiving_complete=False)
    try:
        require_current()
        phase='LOAD_EXACT_PROFILE';engine=load_selected(source)
        phase='NSS_ACTUAL_OBSERVATION'
        objects={}
        observed=dict(files={name:engine.B.capture_selector(name,objects,limit=65536)
            for name in ('/etc/passwd','/etc/nsswitch.conf')})
        for name,row in observed['files'].items():
            need(row['kind']=='FILE' and row['sha256'] in objects,'NSS_CAPTURE_INCOMPLETE')
            facts['private_records'][Path(name).name+'.raw']=write_once(output/(Path(name).name+'.raw'),objects[row['sha256']],65536)
        diagnostic=nss_token_observation(objects[observed['files']['/etc/nsswitch.conf']['sha256']])
        facts['private_records']['NSS_OBSERVATION.json']=write_once(output/'NSS_OBSERVATION.json',encode(diagnostic),8192)
        observed['nscd']={name:engine.B.capture_selector(name,objects) for name in engine.B._NSCD}
        phase='UNCHANGED_NSS_GATE'
        engine.D._validate_nss(observed,objects)
        # This is a preflight, not a cache. The maintained owner reacquires and
        # closes the same actual inputs during the timed producer operation.
        phase='CONSTRUCT_FRESH_OWNER'
        session=engine.GenuineC5Session(source,output/'producer',expected_source=expected_source)
        phase='MAINTAINED_INPUT_ACQUISITION_BEFORE_SELECTION'
        # This is the existing complete byte consumer under its unchanged source
        # and runtime bounds. Only its observation becomes a bounded G3 input;
        # an unconsumed manifest is never a credential for the referenced bytes.
        selected=session._acquire();selected_key=selected['key'];observation=selected['observation']
        del selected  # Do not retain a duplicate raw source/runtime allocation.
        facts['selected_acquisition_key']=selected_key
        totals=observation.get('runtime_totals',{})
        facts['selected_runtime_totals']={key:totals.get(key) for key in
            ('entries','mounted_bytes','unique_bytes','canonical_files','logical_bytes')}
        provider=observation.get('provider',{})
        facts['selected_complete_source_totals']={key:provider.get(key) for key in ('actual_source_files','actual_source_bytes')}
        def reacquire_inputs():
            actual=session._acquire()
            need(actual['key']==selected_key and actual['observation']==observation,'SELECTED_COMPLETE_INPUTS_CHANGED')
            return dict(key=actual['key'],observation=actual['observation'])
        phase='PROSPECTIVE_NATIVE_SELECTION'
        before_producer(observation,selected_key,reacquire_inputs)
        phase='CLOSING_SELECTED_INPUTS_BEFORE_PRODUCER'
        reacquire_inputs()
        phase='ACTUAL_PAIR';facts['producer_owner_invoked']=True
        actual=session.run()
        need(session.acquired['key']==selected_key and session.acquired['observation']==observation,
             'PRODUCER_INPUTS_DIFFER_FROM_PROSPECTIVE_SELECTION')
        facts['private_records']['PRODUCER_RETURN.json']=write_once(output/'PRODUCER_RETURN.json',encode(actual))
        facts['actual_producer_counts']={key:actual.get(key) for key in
            ('original48_dispatches','validated_actual_events','retained_artifacts')}
        phase='SAME_JOB_RAW_RECEIVING'
        session._check_owned();engine.CHECK()
        comparison=engine.Q.compare_c5_correspondence(output/'producer/live-first/capture',output/'producer/live-second/capture',None)
        original=read_regular(output/'producer/comparison.json',MAX_PRIVATE_JSON)
        need(encode(comparison)==original and comparison['equivalent'] is True
             and comparison['raw_observables_equal'] is False,'RAW_RECEIVING_RELATION_DIFFERS')
        facts['private_records']['RECEIVED_RAW_COMPARISON.json']=write_once(output/'RECEIVED_RAW_COMPARISON.json',encode(comparison))
        phase='FINAL_SOURCE_AND_EVIDENCE_CURRENTNESS'
        session._same_inputs();session._check_owned();engine.CHECK()
        facts['private_records']['OWNED_EVIDENCE_INDEX.json']=write_once(output/'OWNED_EVIDENCE_INDEX.json',encode(
            {name:{key:value[key] for key in ('bytes','sha256','mode')} for name,value in sorted(session.owned.items())}))
        session._check_owned()
        facts['private_records']['OWNED_PHYSICAL_CUSTODY.json']=write_once(output/'OWNED_PHYSICAL_CUSTODY.json',encode(
            dict(files={name:value['identity'] for name,value in sorted(session.owned.items())},
                 directories=session.retained_directories)),16*1024**2)
        session._check_owned()
        received=True
    except BaseException as exc:
        failure=dict(phase=phase,type=type(exc).__name__ if type(exc).__name__ in
            {'ValueError','RuntimeError','OSError','FileNotFoundError','PermissionError','KeyError','TypeError','WorkGraphError','KeyboardInterrupt','SystemExit'} else 'UNEXPECTED_EXCEPTION')
        raise
    finally:
        try:
            if session is not None: session.close()
            if engine is not None: engine.CHECK()
            facts['child_terminal_confirmed']=child_terminal_confirmed(output,facts['producer_owner_invoked'])
            need(facts['child_terminal_confirmed'],'CHILD_CUSTODY_UNPROVED_PARENT_CONTAINMENT_REQUIRED')
            require_current()
        except BaseException as exc:
            closing_failure=dict(phase='CLOSE_OR_FINAL_CURRENTNESS',type=type(exc).__name__ if type(exc).__name__ in
                {'ValueError','RuntimeError','OSError','KeyError','TypeError','WorkGraphError','KeyboardInterrupt','SystemExit'} else 'UNEXPECTED_EXCEPTION')
        ended=time.monotonic_ns()
        closing_path=output/'producer/closing-custody.json'
        if closing_path.is_file():
            try:
                raw=read_regular(closing_path,MAX_PRIVATE_JSON);closing=json.loads(raw)
                elapsed=closing.get('elapsed_seconds')
                facts['actual_closing_observation']=dict(bytes=len(raw),sha256=sha(raw),
                    elapsed_seconds=elapsed if type(elapsed) in (int,float) and math.isfinite(elapsed) and elapsed>=0 else None,
                    watchdog_event_count=len(closing.get('watchdog',[])),cleanup_error_count=len(closing.get('cleanup_errors',[])))
            except (OSError,ValueError,TypeError,KeyError):
                facts['actual_closing_observation']=None
        facts.update(phase=phase,failure=failure,closing_failure=closing_failure,
            status='RECEIVED_AT_PROSPECTIVE_COMPONENT_SCOPE' if received and failure is None and closing_failure is None else 'UNQUALIFIED',
            raw_receiving_complete=received,
            timing=dict(producer_watchdog_seconds=120,producer_watchdog_owner='MAINTAINED_EXECUTOR_UNCHANGED_INTERVAL',
                per_process_cpu_seconds=90,enclosing_start_ns=began,enclosing_end_ns=ended,enclosing_elapsed_ns=ended-began,
                enclosing_endpoints='BEFORE_FIRST_CURRENTNESS_THROUGH_OWNER_CLOSE_SOURCE_CHECK_AND_FINAL_CURRENTNESS',
                enclosing_120_second_gate='NOT_ASSERTED_DIFFERENT_STEP_CONTRACT',subtracted_ns=0),
            private_raw_retention='HELD_JOB_LOCAL_FOR_RAW_RECEIVING_NO_PUBLIC_UPLOAD')
        write_once(output/'RESULT.json',encode(facts))
        # Publication/projection time is not disguised as part of the measured
        # enclosure. The surrounding adapter records its own enclosing interval.
    need(closing_failure is None,'FINAL_CUSTODY_OR_CURRENTNESS_REFUSED')
    return facts


if __name__=='__main__':
    raise SystemExit('CALL_FROM_REVIEWED_HOSTED_ADAPTER_WITH_REAL_CURRENTNESS_CALLBACK')
