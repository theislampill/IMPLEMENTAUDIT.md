#!/usr/bin/env python3
"""One unchanged maintained legacy call with closed failed-capture evidence.

The reviewed pair-driver helpers and complete paired plan remain applicable.
Its two-operation main, DAG route, comparator and full receiver are not called.
"""
import argparse
import contextlib
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import types

PAIR_DRIVER_SHA = 'c7df24b98eeda5cb1dc69e835e04fff5d9ccb6b16b5cf52b8e5f13e1deeb4e67'
EVIDENCE_SHA = '4b5f1272697e7bcc5f396e0848273c5caaf582b6f4196a57f10ab1c35a7fa01d'
SOURCE_COMMIT = '3e0f4b6d05eb086017ce721d40459fdbd68714dd'
SOURCE_TREE = 'f8741d0293ce2fd1b4b2b2e9dfa1e28d153cd81a'

def sha(raw):return hashlib.sha256(raw).hexdigest()
def require(value,code):
    if not value:raise ValueError(code)
def module(name,expected):
    path=Path(__file__).with_name(name);raw=path.read_bytes()
    require(len(raw)<=65536 and sha(raw)==expected,'DIAGNOSTIC_ADAPTER_PIN')
    value=types.ModuleType('diagnostic_'+name.replace('.','_'));value.__file__=str(path)
    exec(compile(raw,str(path),'exec',dont_inherit=True,optimize=0),value.__dict__)
    return value

def closing_allowed(record):
    custody=record['custody']
    return (record['attempts']==1 and custody is not None
            and custody['quiescence']=='ECHILD_ALL_CHILDREN' and custody['flag_restored'] is True)

def first_progress_failure(diagnostics,evidence,progress,error):
    # The inherited helper has an exclusive first-failure file. Preserve that
    # primary observation when a later diagnostic or closing action also fails.
    if progress['failure'] is None:diagnostics.failed(evidence,progress,error)

def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',required=True,type=Path)
    parser.add_argument('--out',required=True,type=Path)
    parser.add_argument('--runtime-bin',required=True,type=Path)
    parser.add_argument('--capture-plan-profile',required=True,choices=['single-proc-v2'])
    parser.add_argument('--diagnose',required=True,action='store_true')
    args=parser.parse_args(argv)
    pair=module('pair_driver.py',PAIR_DRIVER_SHA)
    evidence_module=module('capture_evidence.py',EVIDENCE_SHA)
    catalog=evidence_module.load_catalog()
    source=args.source.resolve(strict=True);runtime=args.runtime_bin.absolute();out=args.out.absolute()
    require(not os.path.lexists(out) and out.parent.resolve(strict=True)==out.parent,'DIAGNOSTIC_FRESH_OUTPUT_REQUIRED')
    out.mkdir(mode=0o700);evidence=out/'evidence';evidence.mkdir(mode=0o700)
    captures=out/'captures';captures.mkdir(mode=0o700);(out/'ordinary-home').mkdir(mode=0o700)
    environment=pair.set_environment(runtime,out)
    proc=pair.proc_observation()
    diagnostics=pair.adapter_module('pair_diagnostics.py',pair.DIAGNOSTICS_SHA)
    progress=diagnostics.fresh('execute');diagnostics.save(evidence,progress)
    record=evidence_module.initial_record();evidence_module.save_record(evidence,record,catalog)
    commands=[];owner=None;ordinary_before=None;prior=None;current=None;full=None;fatal=False

    def command(label,argv,cwd):
        started=time.monotonic_ns()
        process=subprocess.run([str(x) for x in argv],cwd=cwd,env=environment,capture_output=True)
        (evidence/(label+'.stdout')).write_bytes(process.stdout);(evidence/(label+'.stderr')).write_bytes(process.stderr)
        commands.append({'label':label,'argv':[str(x) for x in argv],'returncode':process.returncode,
                         'elapsed_ns':time.monotonic_ns()-started,'stdout_sha256':sha(process.stdout),'stderr_sha256':sha(process.stderr)})
        pair.write_json(evidence/'COMMANDS.json',commands)
        require(process.returncode==0,'DIAGNOSTIC_PREFLIGHT_COMMAND_REFUSED')
        return process.stdout

    try:
        diagnostics.advance(evidence,progress,'ORDINARY_NODE')
        selected=shutil.which('node',path=environment['PATH']);require(selected is not None,'ORDINARY_NODE_REQUIRED')
        node=Path(selected).resolve(strict=True);require(node.is_file(),'ORDINARY_NODE_SHAPE')
        node_raw=node.read_bytes();node_version=command('ordinary-node-version',[node,'--version'],source)
        pair.write_json(evidence/'ORDINARY_NODE.json',{'path':str(node),'sha256':sha(node_raw),'bytes':len(node_raw),'version':node_version.decode().strip()})
        diagnostics.advance(evidence,progress,'SOURCE_CHECK')
        prior=command('input-status',['git','status','--porcelain=v1','--untracked-files=all'],source)
        require(not prior,'DIAGNOSTIC_CLEAN_INPUT_REQUIRED')
        command('fsck',['git','fsck','--full','--strict'],source)
        commit=command('commit',['git','rev-parse','HEAD'],source).decode().strip()
        tree=command('tree',['git','rev-parse','HEAD^{tree}'],source).decode().strip()
        require(commit==SOURCE_COMMIT and tree==SOURCE_TREE,'EXACT_PUBLIC_SOURCE_REQUIRED')
        diagnostics.advance(evidence,progress,'OWNER_LOAD')
        owner=pair.load_owner(source)
        compiled=evidence_module.compiled_owner(source,catalog)
        evidence_module.admit_owner(owner,compiled)
        diagnostics.advance(evidence,progress,'ORDINARY_INVENTORY')
        ordinary_before=pair.ordinary_inventory(owner,runtime)
        pair.write_json(evidence/'ORDINARY_BEFORE.json',ordinary_before);pair.write_json(evidence/'PROC_OBSERVATION.json',proc)
        # The unchanged normative policy is a separately bound prerequisite.
        # No relation/normalization evaluation or full-pair award follows here.
        full,relation,policy,adoption=pair.relation_context()
        pair.write_json(evidence/'POLICY_ADOPTION_READBACK.json',adoption)
        diagnostics.advance(evidence,progress,'FULL_POLICY_PREFLIGHT')
        full.source_profiles(source,owner,relation)
        diagnostics.advance(evidence,progress,'REPORT_RUNTIME_PREFLIGHT')
        full.runtime_observation(str(runtime/'python'),owner,evidence,initial=True)
        diagnostics.advance(evidence,progress,'MAPPING')
        registry=(source/'scripts/verify-package.sh').read_bytes()
        registered=owner.WG.verifier_registered_tests_v1(registry)
        physical=sorted(path.relative_to(source).as_posix() for path in (source/'tests').glob('*.test.sh'))
        progress['observed']['registered_physical_equality']=registered==physical;diagnostics.save(evidence,progress)
        require(registered==physical,'DIAGNOSTIC_FULL_REGISTRY_POPULATION')
        child_environment=owner.environment_identity(child_resolution=True)
        mapping=owner.WG.compile_verifier_graph_v1(registry,physical,child_environment)
        stream=owner.WG.verifier_command_stream_v1(mapping,registry)
        reassembled=b''.join(node['source'].encode() for node in mapping['nodes'])==registry
        progress['observed']['exact_registry_reassembly']=reassembled;diagnostics.save(evidence,progress)
        require(reassembled,'DIAGNOSTIC_EXACT_REGISTRY_REASSEMBLY')
        pair.write_json(evidence/'FULL_MAPPING.json',mapping);pair.write_json(evidence/'PHYSICAL_REGISTERED_TESTS.json',physical)
        (evidence/'commands.bin').write_bytes(stream)
        diagnostics.advance(evidence,progress,'PREFLIGHT_CURRENTNESS')
        current=owner.verifier_preflight_currentness_v1()
        capture={'retain_repro_assets':True,'stdin_file':None,'empty_stdin':True,'capture_dist':True,
                 'capture_portal_events':True,'retain_repro_events':True}
        plan={'schema':pair.PLAN_SCHEMA,'expected_currentness':current,
              'runs':[{'mode':mode,'output':str(captures/'work'),'retention':str(captures/mode),
                       'base_environment_sha256':current['base_environment_sha256'],'capture':capture} for mode in ('legacy','dag')]}
        plan_path=evidence/'PLAN.json';pair.write_json(plan_path,plan)
        diagnostics.advance(evidence,progress,'PLAN_PREFLIGHT')
        with (evidence/'preflight.stdout').open('w') as stdout,(evidence/'preflight.stderr').open('w') as stderr:
            with contextlib.redirect_stdout(stdout),contextlib.redirect_stderr(stderr):
                preflight=owner.preflight_verifier_pair_file_v1(plan_path)
        require(preflight==0,'DIAGNOSTIC_MAINTAINED_PLAN_PREFLIGHT')
        diagnostics.advance(evidence,progress,'PROCESS_PROFILE')
        child_preflight=owner._CaptureChildren();child_preflight.close()
        route={'schema':'dg16.g2-single-legacy-diagnostic-route.v1','authority':'NONE','source_commit':SOURCE_COMMIT,'source_tree':SOURCE_TREE,
               'registry':evidence_module.desc(registry),'mapped_nodes':len(mapping['nodes']),'registered_tests':len(registered),
               'registered_physical_equality':True,'exact_registry_reassembly':True,'preflight_exit':preflight,
               'capture_plan_schema':pair.PLAN_SCHEMA,'capture_process_profile':pair.PROC_PROFILE,'declared_plan_modes':['legacy','dag'],
               'requested_operation_mode':'legacy','fixed_command':['bash','scripts/verify-package.sh'],'capture':capture,
               'plan_file':evidence_module.desc(plan_path.read_bytes()),'normative_policy_sha256':pair.POLICY_SHA,
               'normative_relation_evaluated':False,'DAG_requested':False,'full_pair_requested':False,'original_acceptance':False}
        evidence_module.validate_route(route)
        evidence_module.write_exclusive(evidence/'DIAGNOSTIC_ROUTE.json',evidence_module.canonical(route),8192)
        diagnostics.advance(evidence,progress,'LEGACY_CAPTURE')
        returned=None;caught=None;actual_traceback=None
        with (evidence/'legacy.stdout').open('w') as stdout,(evidence/'legacy.stderr').open('w') as stderr:
            with contextlib.redirect_stdout(stdout),contextlib.redirect_stderr(stderr):
                record['attempts']=1;evidence_module.save_record(evidence,record,catalog)
                try:
                    returned=owner.run('legacy',captures/'work',**capture,retention_plan=plan_path)
                except BaseException as exc:
                    caught=exc;actual_traceback=sys.exc_info()[2]
                    evidence_module.observe_operation(record,evidence,captures,source,owner,compiled,catalog,
                                                      error=caught,traceback=actual_traceback)
                    first_progress_failure(diagnostics,evidence,progress,caught)
                else:
                    evidence_module.observe_operation(record,evidence,captures,source,owner,compiled,catalog,code=returned)
        # There is exactly one owner.run call site and no retry, changed guard,
        # namespace repair, trace hook, alternate command, DAG or comparator.
        if caught is None:diagnostics.advance(evidence,progress,'CLOSING')
    except BaseException as exc:
        fatal=True
        first_progress_failure(diagnostics,evidence,progress,exc)
        evidence_module.record_error(record,'SOURCE_FRAMES' if owner is None else 'BOOKENDS',exc)

    may_close=closing_allowed(record)
    if not may_close:
        evidence_module.record_error(record,'BOOKENDS',ValueError('DIAGNOSTIC_OWNER_BOOKENDS_CUSTODY_UNESTABLISHED'))
        fatal=True
    # Each closing fact is an actual independent observation. A first failure
    # cannot erase later facts; all owner calls require established custody.
    if may_close and owner is not None and prior is not None:
        try:
            record['source_status_unchanged']=command('input-status-after',['git','status','--porcelain=v1','--untracked-files=all'],source)==prior
            require(record['source_status_unchanged'],'DIAGNOSTIC_SOURCE_STATUS_CHANGED')
        except BaseException as exc:evidence_module.record_error(record,'BOOKENDS',exc);fatal=True
    if may_close and owner is not None and ordinary_before is not None:
        try:
            record['ordinary_runtime_unchanged']=pair.ordinary_inventory(owner,runtime)==ordinary_before
            require(record['ordinary_runtime_unchanged'],'DIAGNOSTIC_ORDINARY_RUNTIME_CHANGED')
            if full is not None:full.runtime_observation(str(runtime/'python'),owner,evidence,initial=False)
        except BaseException as exc:evidence_module.record_error(record,'BOOKENDS',exc);fatal=True
    if may_close and owner is not None and current is not None:
        try:
            record['currentness_unchanged']=owner.verifier_preflight_currentness_v1()==current
            require(record['currentness_unchanged'],'DIAGNOSTIC_CLOSING_CURRENTNESS_CHANGED')
        except BaseException as exc:evidence_module.record_error(record,'BOOKENDS',exc);fatal=True
    try:
        evidence_module.finish_record(record,evidence,catalog)
        projection=evidence_module.readback(evidence,catalog)
        if projection['diagnostic_complete'] and progress['failure'] is None:diagnostics.advance(evidence,progress,'COMPLETE')
        print(json.dumps({'schema':'dg16.g2-diagnostic-child-status.v1','authority':'NONE','phase':projection['record']['phase'],
                          'primary_retained':projection['retained_primary'] is not None,'diagnostic_complete':projection['diagnostic_complete'],
                          'original_acceptance':False},sort_keys=True),flush=True)
        return 0 if projection['diagnostic_complete'] and not fatal else 1
    except BaseException:
        # Earlier DIAGNOSTIC.json and the independent PRIMARY_EXIT.json remain
        # available to the parent even if final journaling cannot complete.
        print('{"schema":"dg16.g2-diagnostic-child-status.v1","authority":"NONE","phase":"FINAL_READBACK_REFUSED","original_acceptance":false}',flush=True)
        return 1

if __name__=='__main__':
    try:raise SystemExit(main())
    except (Exception,KeyboardInterrupt):
        print('{"schema":"dg16.g2-diagnostic-child-status.v1","authority":"NONE","phase":"PREENTRY_REFUSED","original_acceptance":false}',flush=True)
        raise SystemExit(1)
