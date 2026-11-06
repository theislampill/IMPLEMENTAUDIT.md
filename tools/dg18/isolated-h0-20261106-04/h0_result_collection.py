#!/usr/bin/env python3
"""Bounded diagnostic retention only; never a native owner or currentness reader.

Both native-driver finally and held-control public-summary use this collector.
Valid results and valid journal prefixes survive an absent/invalid final result.
Every exported value is schema checked; incomplete trailing bytes are omitted.
Root must reconcile exact native calls, source/episode binding and fresh grants.
"""
import hashlib
import importlib.util
import os
from pathlib import Path

MAX_INVOCATIONS = 5
MAX_PACKET = 256 * 1024
OBSERVER_SHA256 = 'c36ea5a71e27799cfc0cc3cf7aaeb6fe027d5878ea773815bd0ac0928bdd4f9a'  # Replaced by reproducible candidate composition.
REQUIRED_CODE = ('implementaudit/SKILL.md','audit-state/SKILL.md',
 'implementaudit/references/child-agents.md','implementaudit/references/continuity.md') + tuple(
 'implementaudit/scripts/'+n for n in ('compaction-audit-pending.py','compaction-result-observation.py',
 'compaction-source-owner-codex-app.py','codex-recovery-native-reader.py','bounded_file_custody.py',
 'bounded_native_reader.py','bounded_source_owner.py','host-session-binding.py','route-transaction.py',
 'compaction-prior-protocol.py','compaction-prior-mcp.py'))


def load_observer(path, host_io):
    # H.read supplies the existing bounded no-link physical read before exec.
    path=Path(path);raw=host_io.read(path,128*1024)
    if hashlib.sha256(raw).hexdigest()!=OBSERVER_SHA256:
        raise ValueError('H0_OWNER_OBSERVATION_REFUSED')
    spec=importlib.util.spec_from_file_location('h0_observer_collector',path)
    module=importlib.util.module_from_spec(spec)
    # Execute the checked bytes, never reopen the path after checking it.
    exec(compile(raw,str(path),'exec'),module.__dict__)
    return module


def prefix(run, binding, O):
    start=O.parse(O.read_safe(run/'supervisor-start.json',O.MAX_PUBLIC)[0],O.MAX_PUBLIC)
    O.need(type(start) is dict and set(start)=={'schema','binding_sha256','supervisor','child','pre','watchdog_seconds','watchdog_start_monotonic_ns'}
      and start['schema']==O.SCHEMA and start['binding_sha256']==O.sha(O.canonical(binding))
      and type(start['watchdog_seconds']) is int and start['watchdog_seconds']==O.WATCHDOG_SECONDS
      and type(start['watchdog_start_monotonic_ns']) is int and 0 < start['watchdog_start_monotonic_ns'] < 2**63
      and O.process_valid(start['child']) and O.process_valid(start['supervisor'])
      and start['child'] is not None and start['supervisor'] is not None and start['child']['ppid']==start['supervisor']['pid'])
    O.validate_snapshot(start['pre'])
    return start,O.journal_summary(run,binding,start['child'])


def collect(store, *, observer, selection_sha256, code_sha256, session_sha256):
    O=observer
    O.need(all(type(v) is str and O.HEX.fullmatch(v) for v in (selection_sha256,code_sha256,session_sha256)))
    root=Path(store)/O.DIRECTORY
    packet={'schema':'dg18.h0-observation-collection.v1','status':'NO_INVOCATIONS_RECORDED',
      'selection_sha256':selection_sha256,'assignment_code_sha256':code_sha256,'session_sha256':session_sha256,
      'records':[],'issues':[],'call_binding':'REQUIRES_INDEPENDENT_NATIVE_CALL_RECONCILIATION',
      'historical_effects':'UNCHANGED_UNCONFIRMED','canonical_currentness':'UNKNOWN',
      'descendant_provider_closure':'NOT_ESTABLISHED','authority':'NONE'}
    try: root.lstat()
    except FileNotFoundError: return packet
    try: O.safe_directory(root,private=True)
    except (OSError,ValueError):
        packet.update(status='COLLECTION_REFUSED',issues=['ROOT_REFUSED']);return packet
    names=[]
    with os.scandir(root) as entries:
        for position,entry in enumerate(entries):
            if position >= MAX_INVOCATIONS:
                packet['issues'].append('INVOCATION_COUNT_EXCEEDED');break
            if not O.HEX.fullmatch(entry.name) or not entry.is_dir(follow_symlinks=False):
                packet['issues'].append('ENTRY_REFUSED');continue
            names.append(entry.name)
    bindings=[]
    for name in sorted(names):
        try:
            run=O.safe_directory(root/name,private=True)
            binding=O.parse(O.read_safe(run/'binding.json',O.MAX_PUBLIC)[0],O.MAX_PUBLIC)
            O.validate_binding(binding)
            O.need(name==O.sha(O.canonical(binding)) and binding['selection_sha256']==selection_sha256
              and binding['assignment_code_sha256']==code_sha256 and binding['session_sha256']==session_sha256)
            bindings.append((binding,run))
        except (OSError,ValueError,TypeError,KeyError):
            packet['issues'].append('BINDING_REFUSED')
    bindings.sort(key=lambda pair:pair[0]['call_ordinal'])
    if ([binding['call_ordinal'] for binding,_ in bindings]!=[1,2,3,5,6][:len(bindings)]
      or len({binding['child_sha256'] for binding,_ in bindings})>1
      or any(binding['operation']!={1:'DELIVER',2:'BIND',3:'BIND',5:'DELIVER',6:'BIND'}.get(binding['call_ordinal']) for binding,_ in bindings)):
        packet['issues'].append('CALL_SET_REFUSED')
    for binding,run in bindings:
        try:
            result=O.read_result(run,binding)
            record={'status':'BOUNDED_RESULT_RETAINED','binding':binding,'result':result,'owner':result['owner']}
        except (OSError,ValueError,TypeError,KeyError):
            start=owner=None
            try: start,owner=prefix(run,binding,O)
            except (OSError,ValueError,TypeError,KeyError): pass
            record={'status':'INCOMPLETE_OR_INVALID_RESULT','binding':binding,'owner':owner,'start':start,
              'effect':'UNKNOWN','canonical_currentness':'UNKNOWN','authority':'NONE'}
            packet['issues'].append('RESULT_UNAVAILABLE_OR_INVALID')
        packet['records'].append(record)
    packet['issues']=sorted(set(packet['issues']))
    if packet['issues']: packet['status']='PARTIAL_OBSERVATIONS_WITH_REFUSALS'
    elif bindings: packet['status']='OBSERVATIONS_RETAINED_PENDING_EXACT_RECEIVING'
    O.need(len(O.canonical(packet))<=MAX_PACKET)
    return packet


def retain_for_work(work, output, H):
    """No owner calls, provider calls, currentness claims, raw stderr or requests."""
    work=Path(work);output=Path(output);private=work/'private';repo=private/'subject'
    selected_path=private/'SOURCE_SELECTION.json'
    if not selected_path.exists():
        return {'schema':'dg18.h0-observation-collection-ref.v1','status':'SELECTION_NOT_CREATED','effect':'UNKNOWN','authority':'NONE'}
    O=load_observer(Path(__file__).resolve().parent/'h0_owner_observation.py',H)
    raw=H.read(selected_path,256*1024);selected=H.parse(raw)
    exact={key:O.sha(H.read(repo/'skills'/key,512*1024)) for key in REQUIRED_CODE}
    packet=collect(private/'host-store',observer=O,selection_sha256=O.sha(raw),
      code_sha256=O.sha(O.canonical(exact)),session_sha256=O.sha(selected['pending_owner']['session_id'].encode()))
    for record in packet['records']:
        owner=record['owner']
        if owner is None:continue
        try:
            binding=record['binding'];name=O.sha(O.canonical(binding));run=private/'host-store'/O.DIRECTORY/name
            journal,_=O.read_safe(run/'owner.jsonl',O.MAX_JOURNAL)
            O.need(O.sha(journal)==owner['journal_sha256'])
            # The complete lines were already checked. A partial trailing write
            # may be arbitrary bytes and is deliberately never exported.
            checked=journal[:len(journal)-owner['journal_tail_bytes']]
            filename='H0_JOURNAL_'+name+'.jsonl'
            H.write(output/filename,checked,mode=0o600)
            record['journal_ref']={'file':filename,'bytes':len(checked),'sha256':O.sha(checked),
              'source_sha256':owner['journal_sha256'],'omitted_tail_bytes':owner['journal_tail_bytes']}
        except (OSError,ValueError,TypeError,KeyError):
            packet['issues'].append('PREFIX_EXPORT_REFUSED')
    packet['issues']=sorted(set(packet['issues']))
    if packet['issues']:packet['status']='PARTIAL_OBSERVATIONS_WITH_REFUSALS'
    O.need(len(O.canonical(packet))<=MAX_PACKET)
    H.write(output/'H0_OWNER_OBSERVATIONS.json',O.canonical(packet)+b'\n',mode=0o600)
    return {'schema':'dg18.h0-observation-collection-ref.v1','status':packet['status'],
      'sha256':O.sha(H.read(output/'H0_OWNER_OBSERVATIONS.json',MAX_PACKET)),
      'invocations':len(packet['records']),'effect':'UNKNOWN','authority':'NONE'}


def retain_for_subject(subject, host_io):
    return retain_for_work(subject.work,subject.evidence,host_io)
