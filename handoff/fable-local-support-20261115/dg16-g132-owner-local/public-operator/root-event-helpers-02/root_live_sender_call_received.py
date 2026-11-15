"""Mechanical Root recipe wiring. Import and `command` have no operation effects.

Guest readback/issuance commands require Root's explicit invocation. A supplied
decision reference records Root's claim; this program cannot authenticate Root,
native history, a recipient, or an authority grant. No retries or controller.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import sys
import time
import types

BASE = '/workspace/scratch/0269e6626329/fable-local-support/handoff/fable-local-support-20261115/dg16-g132-owner-local/public-operator'
ROOT = 'PRO-EXECUTOR-01'
FINAL = BASE + '/root-final-operators-01'
PIPELINE = FINAL + '/root_pipeline_inputs_v2.py'
PINS = {
    'issuer': (BASE+'/root-recipient-issuer-01/issue_recipient_inputs.py', '33579984c5e5d05f8e801fd75187886c38a604c6622cd1e4097412b565af9ad3'),
    'assembler': (BASE+'/late-assembler-01/assemble_actual.py', '58c148499349a40f9471a2a1371710daa2e5a1728856a09042702bd4c068cbf6'),
    'binder': (BASE+'/dispatcher-templates-02/bind_dispatcher.py', 'c59aa4cd4228cb4c081c191ad3d8b026e17765ef39b069d74de0778de48303ad'),
    'pipeline': (PIPELINE, '347205482ab76b60fb9b9fddda0c316240cb7c0ef5a711ed47c5ccd86eeed49b'),
    'binary': (FINAL+'/binary_publish_v3.py', '7143a193ac02131b4efed80b2ff80f53d9fb64540bff40284049265c1223eff4'),
    'journal': (FINAL+'/control_process_v3.py', 'e3b48846c8c260548fab8b8d4822bb856ff19c7d95f10ceaa39ea88a404c86c3'),
    'decoder': (FINAL+'/file_readback.py', 'ab938a99ce3971caaa5e740bf4c079e3245cf0893ea358580c3661807104dcb1'),
    'resolver': (BASE+'/public-receiver-02/author/resolve_artifact.py', 'e42fa2108e726597b3fa478ecdb8cbb0b0fc06695b12d176fa3add93581e3149'),
}
LOADER = "import hashlib,os,pathlib,stat,sys; p=pathlib.Path(sys.argv[1]); pin=sys.argv[2]; mark=lambda s:(s.st_dev,s.st_ino,s.st_mode,s.st_nlink,s.st_uid,s.st_gid,s.st_size,s.st_mtime_ns,s.st_ctime_ns); s=p.lstat(); assert stat.S_ISREG(s.st_mode) and s.st_nlink==1 and s.st_uid==os.geteuid() and stat.S_IMODE(s.st_mode) in (0o400,0o444) and 0<s.st_size<=1048576; fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK|os.O_CLOEXEC); opened=os.fstat(fd); assert mark(opened)==mark(s) and stat.S_ISREG(opened.st_mode) and not os.listxattr(fd); raw=os.pread(fd,s.st_size+1,0); assert len(raw)==s.st_size and hashlib.sha256(raw).hexdigest()==pin and mark(os.fstat(fd))==mark(s) and mark(p.lstat())==mark(s); os.close(fd); sys.argv=[str(p),*sys.argv[3:]]; exec(compile(raw,str(p),'exec'),{'__name__':'__main__','__file__':str(p)})"


def need(v, code):
    if not v:
        raise ValueError(code)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def parse(raw):
    def pairs(rows):
        out = {}
        for k, v in rows:
            need(k not in out, 'DUPLICATE_KEY')
            out[k] = v
        return out
    return json.loads(raw, object_pairs_hook=pairs,
                      parse_constant=lambda _: need(False, 'NONFINITE'))


def encode(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':'),
                       ensure_ascii=True, allow_nan=False)+'\n').encode('ascii')


def path(value):
    need(type(value) is str and '\x00' not in value and '\n' not in value and '\r' not in value,
         'LITERAL_PATH')
    p = PurePosixPath(value)
    need(p.is_absolute() and str(p) == value and '..' not in p.parts
         and p.is_relative_to(PurePosixPath(BASE)), 'ROOT_CANONICAL_PATH_REQUIRED')
    return value


def digest(value):
    need(type(value) is str and re.fullmatch('[0-9a-f]{64}', value)
         and value != '0'*64, 'SHA256_REQUIRED')
    return value


def stage_argv(stage, data):
    """Return the frozen executable selection and argv; never execute it."""
    need(type(data) is dict, 'PARAMETERS_OBJECT')
    specs = {
        'issue': ('issuer', ('session', 'recipient_receipt_sha256', 'publication_receipt', 'publication_receipt_sha256', 'episode')),
        'assemble': ('assembler', ('episode',)),
        'dispatcher-selection': ('pipeline', ('episode', 'late_receiving', 'late_receiving_sha256', 'install', 'output')),
        'requirements': ('binder', ('selection', 'output')),
        'bind': ('binder', ('selection', 'admission', 'install')),
        'publication-inputs': ('pipeline', ('episode', 'sender_terminal', 'sender_terminal_sha256', 'sender_receiving', 'sender_receiving_sha256', 'parent_ref_result', 'parent_ref_sha256', 'journal_directory', 'deadline_unix_ms', 'output')),
        'publication-config': ('pipeline', ('prepared', 'prepared_manifest_sha256', 'admission', 'admission_sha256', 'output')),
    }
    need(stage in specs, 'NO_IMPLICIT_SENDER_OR_PUBLISHER_LAUNCH')
    key, names = specs[stage]
    need(set(data) == set(names), 'EXACT_STAGE_PARAMETERS')
    for n in names:
        if n.endswith('sha256'):
            digest(data[n])
        elif n == 'deadline_unix_ms':
            need(type(data[n]) is int and data[n] > 0, 'ABSOLUTE_DEADLINE')
        else:
            path(data[n])
    if stage == 'publication-inputs':
        # Pure early form of the driver Journal root (control_process_v3.py:161-162); no filesystem access.
        sessions = PurePosixPath(BASE + '/public-receiver-02/control-sessions')
        journal = PurePosixPath(data['journal_directory'])
        need(journal != sessions and journal.is_relative_to(sessions), 'JOURNAL_BELOW_DRIVER_CONTROL_SESSIONS')
    if stage == 'issue':
        args = [data[n] for n in names]
    elif stage == 'assemble':
        e = data['episode']
        args = ['--stage', BASE+'/late-assembler-01/source-stage-01', '--host-phase', BASE+'/public-receiver-02/phase',
                '--root-reader', BASE+'/public-receiver-02/author/receiver.py', '--dispatcher-source', PINS['binder'][0],
                '--private-inputs', BASE+'/retained-final5f-private-inputs', '--late-inputs', e+'/late-inputs', '--output', e+'/assembled']
    elif stage in ('requirements', 'bind'):
        args = [stage] + [data[n] for n in names]
    else:
        args = [stage]
        for n in names:
            flag = 'parent-ref-sha256' if n == 'parent_ref_sha256' else n.replace('_', '-')
            args += ['--'+flag, str(data[n])]
    return PINS[key], args


def command_for(selected, args):
    selected_path, pin = selected
    path(selected_path); digest(pin)
    values = ['C:\\Windows\\System32\\wsl.exe', '--distribution', 'Ubuntu', '--user', 'agent', '--cd', '/',
              '--exec', '/usr/bin/python3', '-I', '-B', '-c', LOADER, selected_path, pin, *args]
    need(all(type(s) is str and not any(c in s for c in '\r\n\x00') for s in values), 'SCALAR_ARGUMENTS')
    quote = lambda s: "'"+s.replace("'", "''")+"'"
    cmd = "$PSNativeCommandArgumentPassing='Standard'; & "+' '.join(map(quote, values))+"; exit $LASTEXITCODE"
    need(len(cmd) <= 18000, 'LAUNCH_BOUND')
    return cmd


def pipeline():
    """Load captured, hash-checked definitions of the already received pure owner."""
    need(sys.platform == 'linux' and sys.flags.isolated and sys.dont_write_bytecode
         and os.getuid() == os.geteuid() > 0 and os.getgid() == os.getegid(), 'ROOT_FIXED_GUEST_RUNTIME')
    p = Path(PIPELINE)
    need(p.resolve(strict=True) == p, 'NO_PIPELINE_ALIAS')
    s = p.lstat()
    mark = lambda x: (x.st_dev,x.st_ino,x.st_mode,x.st_nlink,x.st_uid,x.st_gid,x.st_size,x.st_mtime_ns,x.st_ctime_ns)
    need(stat.S_ISREG(s.st_mode) and s.st_uid == os.geteuid() and s.st_nlink == 1
         and stat.S_IMODE(s.st_mode) in (0o400,0o444) and 0 < s.st_size <= 1048576, 'PINNED_PIPELINE_CUSTODY')
    fd = os.open(p, os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK|os.O_CLOEXEC)
    try:
        need(mark(os.fstat(fd)) == mark(s) and not os.listxattr(fd), 'PIPELINE_OPEN_CHANGED')
        raw = os.pread(fd, s.st_size+1, 0)
        need(len(raw) == s.st_size and sha(raw) == PINS['pipeline'][1]
             and mark(os.fstat(fd)) == mark(s) == mark(p.lstat()), 'PIPELINE_CLOSING_CHANGED')
    finally:
        os.close(fd)
    m = types.ModuleType('root_frozen_pipeline_definitions')
    m.__file__ = str(p)
    exec(compile(raw, str(p), 'exec'), m.__dict__)
    return m


def directory(P, d):
    d = P.exact_path(d); s = d.lstat()
    need(stat.S_ISDIR(s.st_mode) and s.st_uid == os.geteuid() and s.st_gid == os.getegid()
         and stat.S_IMODE(s.st_mode) == 0o700 and not os.listxattr(d), 'PRIVATE_DIRECTORY_CUSTODY')
    return d


def tree(P, d, manifest_name, manifest_sha, file_modes):
    """Read every declared byte and physical entry; disclose descriptors only."""
    d = directory(P, d)
    manifest_raw = P.read(d/manifest_name, 4*1024**2, digest(manifest_sha))
    manifest = P.parse(manifest_raw); members = manifest['members']
    need(type(members) is dict and 0 < len(members) <= 256, 'BOUNDED_MANIFEST')
    for name in members:
        rel = PurePosixPath(name)
        need(not rel.is_absolute() and '..' not in rel.parts and str(rel) == name
             and name != manifest_name, 'MANIFEST_MEMBER_PATH')
    observed = set(); observed_dirs = set()
    for current, dirs, files in os.walk(d, followlinks=False):
        directory(P, Path(current))
        for name in dirs:
            directory(P, Path(current)/name)
            observed_dirs.add((Path(current)/name).relative_to(d).as_posix())
        for name in files:
            target = Path(current)/name
            rel = target.relative_to(d).as_posix(); observed.add(rel)
            s = target.lstat()
            need(stat.S_IMODE(s.st_mode) == file_modes(rel) and s.st_gid == os.getegid(), 'EXACT_FILE_MODE_AND_GROUP')
    need(observed == set(members)|{manifest_name}, 'EXACT_INSTALLED_MEMBER_SET')
    expected_dirs = {str(p) for n in members for p in PurePosixPath(n).parents if str(p) != '.'}
    need(observed_dirs == expected_dirs, 'EXACT_INSTALLED_DIRECTORY_SET')
    for name, descriptor in members.items():
        need(P.desc(P.read(d/name, 32*1024**2, descriptor['sha256'])) == descriptor, 'MEMBER_DESCRIPTOR')
    need(P.read(d/manifest_name, 4*1024**2, manifest_sha) == manifest_raw, 'MANIFEST_CLOSING')
    return manifest, {'path':str(d/manifest_name), **P.desc(manifest_raw)}


def late(P, episode, manifest_sha):
    assembled, entry, eraw, op_path, op, mraw = P.episode_inputs(episode)
    manifest, row = tree(P, assembled, 'ROOT_SENDER_INSTALL_MANIFEST.json', manifest_sha,
                         lambda n: 0o600 if n.startswith('packet/private-inputs/') or n == 'ROOT_REQUEST_ARTIFACT.zip' else 0o400)
    need(P.desc(mraw) == {k:row[k] for k in ('bytes','sha256')}, 'INITIAL_MANIFEST_JOIN')
    index_raw = P.read(assembled/'packet/carrier/INPUT_INDEX.json', 1048576)
    index = P.parse(index_raw)
    actual_private = {n[len('packet/private-inputs/'):]:v for n,v in manifest['members'].items() if n.startswith('packet/private-inputs/')}
    need(len(actual_private) == 11 and actual_private == index, 'EXACT_ELEVEN_PRIVATE_INPUTS')
    need(op['input_index_sha256'] == P.sha(index_raw), 'OPERATION_INPUT_INDEX')
    late_dir = directory(P, Path(episode)/'late-inputs')
    names = {'ROOT_SENDER_ASSEMBLY_SELECTION.json','PRO_SENDER_OPERATION.json','PRO_SENDER_ADMISSION.json','ROOT_REQUEST_ARTIFACT.zip','HOST_PUBLICATION_ROOT_RECEIVING.json'}
    need({p.name for p in late_dir.iterdir()} == names, 'EXACT_FIVE_LATE_INPUTS')
    originals = {n:P.row(late_dir/n) for n in sorted(names)}
    need(P.read(late_dir/'PRO_SENDER_OPERATION.json') == P.read(op_path), 'ISSUED_OPERATION_JOIN')
    need(P.parse(P.read(late_dir/'ROOT_SENDER_ASSEMBLY_SELECTION.json'))['fixed_packet_directory'] == str(assembled/'packet'), 'ROOT_PACKET_SELECTION')
    need(P.read(late_dir/'ROOT_REQUEST_ARTIFACT.zip') == P.read(assembled/'ROOT_REQUEST_ARTIFACT.zip'), 'ACTUAL_REQUEST_ARCHIVE_JOIN')
    P.current(op, time.time_ns()//1000000)
    return dict(authority='NONE', kind='LATE_SOURCE_READBACK_ONLY', manifest=row, entry=P.row(entry),
                operation=P.row(op_path), context=op['context'], late_inputs=originals,
                private_source_bodies=11, expires_unix_ms=op['expires_unix_ms'], original_awards=[])


def prepared(P, d, manifest_sha):
    manifest, row = tree(P, d, 'PREPARED_MANIFEST.json', manifest_sha, lambda _:0o600)
    need(set(manifest['members']) == {'PLAN.json','PURPOSE.json','CONFIG_INPUTS.json','ADMISSION_REQUIREMENTS.json'}
         and manifest['binary_module_sha256'] == PINS['binary'][1], 'EXACT_BINARY_PREPARATION')
    d = Path(d); bodies = {n:P.parse(P.read(d/n, 65536)) for n in manifest['members']}
    plan, purpose, config, req = (bodies[n] for n in ('PLAN.json','PURPOSE.json','CONFIG_INPUTS.json','ADMISSION_REQUIREMENTS.json'))
    need(set(purpose) == {'request_nonce','recipient_sha256','input_index_sha256'}, 'INDEPENDENT_PURPOSE_FIELDS')
    import io, zipfile
    for value in purpose.values():
        digest(value)
    rid=plan['context']['run_id']
    need(type(rid) is str and re.fullmatch('[1-9][0-9]{0,19}',rid),'RUN_ID')
    session=Path(BASE)/'public-receiver-02'/'sessions'/('r'+rid+'-recipient')
    archived=P.read(session/'ARTIFACT.zip',65536)
    recv=P.parse(P.read(session/'RECEIVING.json',65536))
    need(recv['archive']==P.desc(archived) and recv['context']==plan['context'],'ACTUAL_RECEIVED_RECIPIENT')
    with zipfile.ZipFile(io.BytesIO(archived)) as z:
        need(len(z.infolist())==2 and set(z.namelist())=={'REQUEST.json','RECIPIENT.pem'},'RECEIVED_RECIPIENT_MEMBERS')
        request=z.read('REQUEST.json')
    need(P.desc(request)==plan['request'],'INDEPENDENT_REQUEST_PLAN_JOIN')
    request=P.parse(request)
    need(purpose==dict(request_nonce=request['nonce'],recipient_sha256=request['recipient_sha256'],input_index_sha256=request['input_index_sha256']),'INDEPENDENT_RECIPIENT_PURPOSE_JOIN')
    need(req['authority'] == 'NONE' and req['actual_admission'] is False
         and req['expected_body']['deadline_unix_ms'] == config['deadline_unix_ms'] == plan['expires_unix_ms']
         and time.time_ns()//1000000 < plan['expires_unix_ms'], 'LIVE_PREPARED_BINARY_DEADLINE')
    return row, bodies


def runtime_parents(P, episode, publication_receipt, journal_directory, planned_outputs=()):
    """Launch preflight. Evaluates the later owners' own parent predicates; creates nothing."""
    for value in (episode, publication_receipt, journal_directory, *planned_outputs):
        path(value)
    made = [Path(BASE)/'public-receiver-02'/n for n in ('event-configurations', 'sessions', 'control-sessions')]
    for d in made:
        # Each owner requires a canonical existing parent and then creates one fresh leaf with mkdir:
        # g1_event_config_corrected.py:173,178; role_process_v4.py:237 with receiver.py Session.create;
        # control_process_v5.py:169-171; control_process_v3.py:161-163. None of them checks owner or mode.
        need(d.resolve(strict=True) == d and stat.S_ISDIR(d.lstat().st_mode)
             and os.access(d, os.W_OK | os.X_OK), 'RUNTIME_CONTAINER_REQUIRED')
    issuer = P.module(Path(PINS['issuer'][0]), P.read(PINS['issuer'][0], 1048576, PINS['issuer'][1]),
                      'frozen_recipient_issuer_definitions')
    episode = Path(episode); receipt_parent = Path(publication_receipt).parent
    issuer.private_directory(episode)         # issue_recipient_inputs.py:121
    issuer.private_directory(receipt_parent)  # issue_recipient_inputs.py:122
    # issue_recipient_inputs.py:136,139 and assemble_actual.py:126,132 create these two leaves themselves.
    need(not os.path.lexists(episode/'late-inputs') and not os.path.lexists(episode/'assembled'),
         'FRESH_EPISODE_LEAVES_REQUIRED')
    P.journal_path(journal_directory)         # root_pipeline_inputs_v2.py journal owner; driver Journal root
    for value in planned_outputs:
        P.fresh_path(value)                   # every write_file/write_directory target of the pipeline and this recipe
    return dict(authority='NONE', kind='RUNTIME_PARENT_READBACK_ONLY',
                containers=[str(d) for d in made]+[str(episode), str(receipt_parent), str(Path(journal_directory).parent)],
                planned_outputs=list(planned_outputs), directories_created=0, launch_or_effect_performed=False,
                later_owner_checks='UNCHANGED_AND_STILL_REQUIRED', original_awards=[])


def decision_ref(value):
    need(type(value) is str and 8 <= len(value) <= 1024 and not any(c in value for c in '\r\n\x00'), 'ACTUAL_ROOT_DECISION_REFERENCE_REQUIRED')
    return value


def terminal_component(terminal, session_id, exit_code):
    need(terminal['schema']=='dg16.root-sender-terminal-export.v1'
         and terminal['result']['status']=='PAYLOAD_READY'
         and terminal['result']['cleanup_complete'] is True
         and terminal['publication_performed'] is False
         and terminal['original_awards']==[]
         and type(session_id) is int and session_id>0
         and type(exit_code) is int and exit_code==0, 'ACTUAL_TERMINAL_COMPONENT_REQUIRED')


def issue(P, expected, requirements_row, output, issuance_record, reference):
    """Explicit Root invocation, not a requirements-to-authority inference."""
    reference = decision_ref(reference)
    need(expected.get('successor') == 'PRO-EXECUTOR-01, designated by owner', 'ACTUAL_ROOT_SUCCESSOR_REQUIRED')
    need(Path(output) != Path(issuance_record), 'SEPARATE_ISSUANCE_RECORD')
    P.fresh_path(output); P.fresh_path(issuance_record)
    P.write_file(output, P.encode(expected))
    record = dict(schema='dg16.root-explicit-issuance-record.v1', issuer_thread=ROOT,successor='PRO-EXECUTOR-01, designated by owner',
                  root_decision_ref=reference, requirements=requirements_row, issued=P.row(output),
                  issued_unix_ms=time.time_ns()//1000000, authentication='ROOT_NATIVE_HISTORY_SEPARATE',
                  automatic_retry=False, original_awards=[])
    P.write_file(issuance_record, P.encode(record))
    return dict(authority='NONE', issued=P.row(output), issuance_record=P.row(issuance_record),
                provenance='EXPLICIT_ROOT_INVOCATION_REQUIRES_ACTUAL_ROOT_HISTORY', original_awards=[])


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest='action', required=True)
    c = sub.add_parser('command'); c.add_argument('stage'); c.add_argument('--parameters-json', required=True)
    h = sub.add_parser('helper-command'); h.add_argument('--installed-helper', required=True); h.add_argument('--helper-sha256', required=True); h.add_argument('arguments', nargs=argparse.REMAINDER)
    for name in ('check-late','receive-late','receive-sender-terminal','check-dispatcher','check-prepared','issue-admission','binary-selection','sender-command'):
        s = sub.add_parser(name)
        if name in ('check-late','receive-late','issue-admission','sender-command'):
            s.add_argument('--episode', required=True)
        if name in ('check-late','receive-late','sender-command'):
            s.add_argument('--manifest-sha256', required=True)
        if name in ('receive-late','receive-sender-terminal','issue-admission'):
            s.add_argument('--root-decision-ref', required=True); s.add_argument('--output', required=True)
        if name == 'issue-admission':
            s.add_argument('--requirements', required=True); s.add_argument('--requirements-sha256', required=True)
            s.add_argument('--issuance-record', required=True)
        if name in ('check-prepared','binary-selection','issue-admission'):
            s.add_argument('--prepared'); s.add_argument('--prepared-manifest-sha256')
        if name == 'check-dispatcher':
            s.add_argument('--install', required=True); s.add_argument('--install-manifest-sha256', required=True)
            s.add_argument('--selection', required=True); s.add_argument('--selection-sha256', required=True)
        if name == 'receive-sender-terminal':
            s.add_argument('--terminal', required=True); s.add_argument('--terminal-sha256', required=True)
            s.add_argument('--native-session-id', type=int, required=True); s.add_argument('--actual-exit-code', type=int, required=True)
        if name == 'binary-selection':
            s.add_argument('--configuration', required=True); s.add_argument('--configuration-sha256', required=True)
    r = sub.add_parser('check-runtime-parents')
    for name in ('--episode', '--publication-receipt', '--journal-directory'):
        r.add_argument(name, required=True)
    r.add_argument('--planned-output', action='append', default=[])
    a = ap.parse_args()
    if a.action == 'command':
        selected, args = stage_argv(a.stage, parse(a.parameters_json))
        result = dict(authority='NONE', command=command_for(selected,args), source_path=selected[0], source_sha256=selected[1], actual_execution=False)
    elif a.action == 'helper-command':
        result = dict(authority='NONE', command=command_for((path(a.installed_helper),digest(a.helper_sha256)),a.arguments), actual_execution=False)
    else:
        P = pipeline()
        if a.action == 'check-runtime-parents':
            result = runtime_parents(P, a.episode, a.publication_receipt, a.journal_directory, a.planned_output)
        elif a.action in ('check-late','receive-late','sender-command'):
            result = late(P, a.episode, digest(a.manifest_sha256))
            if a.action == 'receive-late':
                result.update(schema='dg16.root-actual-late-source-receiving.v1',issuer_thread=ROOT,successor='PRO-EXECUTOR-01, designated by owner',
                              root_decision_ref=decision_ref(a.root_decision_ref),decision='ACCEPT_EXACT_SOURCE_ONLY',
                              authentication='ROOT_NATIVE_HISTORY_SEPARATE',sender_started=False)
                P.write_file(a.output, P.encode(result)); result = dict(authority='NONE',receiving=P.row(a.output))
            elif a.action == 'sender-command':
                result = dict(authority='NONE',command=command_for((result['entry']['path'],result['entry']['sha256']),[]),
                              launch='ROOT_ONCE_NONBLOCKING_THEN_EXISTING_BOUND_DISPATCH_JS',automatic_retry=False)
        elif a.action == 'check-dispatcher':
            m,row = tree(P,a.install,'INSTALL_MANIFEST.json',a.install_manifest_sha256,lambda _:0o400)
            need(set(m['members']) == {'dispatcher_entry.py','dispatch.js','DISPATCHER_BINDING.json','DISPATCHER_ADMISSION.json','ROOT_LATE_RECEIVING.json'}, 'EXACT_SIX_DISPATCHER_FILES')
            d=Path(a.install); b=P.parse(P.read(d/'DISPATCHER_BINDING.json')); op=P.parse(P.read(b['operation_path'],65536,b['operation']['sha256']))
            P.current(op,time.time_ns()//1000000)
            need(m['helper_path'] == str(d/'dispatcher_entry.py') and m['owner_uid'] == os.geteuid() and m['owner_gid'] == os.getegid(), 'FINAL_DISPATCHER_LOCATION_OWNER')
            js=P.read(d/'dispatch.js').decode('utf-8')
            for token in ('const HELPER_PATH = '+json.dumps(m['helper_path'])+';', 'const HELPER_SHA256 = '+json.dumps(m['members']['dispatcher_entry.py']['sha256'])+';', 'const OP_EXPIRES_UNIX_MS = '+str(op['expires_unix_ms'])+';'):
                need(js.count(token)==1,'BOUND_DISPATCHER_JS_JOIN')
            need(P.desc(P.read(d/'DISPATCHER_ADMISSION.json')) == b['admission'], 'DISPATCH_ADMISSION_JOIN')
            selection=P.parse(P.read(a.selection,65536,digest(a.selection_sha256)))
            need(selection['helper_path']==str(d/'dispatcher_entry.py'),'RECEIVED_FINAL_SELECTION')
            binder=P.module(Path(PINS['binder'][0]),P.read(PINS['binder'][0],1048576,PINS['binder'][1]),'frozen_dispatcher_bind_definitions')
            expected=binder.bind(selection,P.read(d/'DISPATCHER_ADMISSION.json'))
            need(all(P.read(d/n,4*1024**2)==raw for n,raw in expected.items()),'EXACT_FROZEN_BINDER_OUTPUT_BYTES')
            result=dict(authority='NONE',manifest=row,dispatch=P.row(d/'dispatch.js'),expires_unix_ms=op['expires_unix_ms'],sender_terminal='SEPARATE')
        elif a.action == 'receive-sender-terminal':
            terminal=P.parse(P.read(a.terminal,65536,digest(a.terminal_sha256)))
            terminal_component(terminal,a.native_session_id,a.actual_exit_code)
            result=dict(schema='dg16.root-sender-terminal-component-receiving.v1',issuer_thread=ROOT,successor='PRO-EXECUTOR-01, designated by owner',
                        root_decision_ref=decision_ref(a.root_decision_ref),terminal=P.row(a.terminal,a.terminal_sha256),
                        actual_native_session_id=a.native_session_id,actual_exit_code=a.actual_exit_code,
                        decision='ACCEPT_ACTUAL_TERMINAL_COMPONENT_ONLY',authentication='ROOT_NATIVE_HISTORY_SEPARATE',
                        outcome_and_cipher_join='REQUIRED_IN_FROZEN_PUBLICATION_INPUTS_NOT_PROVED_BY_THIS_RECEIPT',original_awards=[])
            P.write_file(a.output,P.encode(result));result=dict(authority='NONE',receiving=P.row(a.output))
        elif a.action == 'issue-admission':
            assembled,entry,eraw,op_path,op,mraw=P.episode_inputs(a.episode)
            raw=P.read(a.requirements,65536,digest(a.requirements_sha256)); req=P.parse(raw)
            need(req['authority']=='NONE' and req['actual_admission'] is False,'REQUIREMENTS_NOT_ISSUANCE')
            expected=req['expected_body']; schema=expected['schema']
            if schema=='dg16.root-supported-tool-dispatch-admission.v1':
                need(expected['entry_path']==str(entry) and expected['entry']==P.desc(eraw) and expected['operation_body']==P.desc(P.read(op_path))
                     and expected['context']==op['context'] and expected['automatic_retry'] is False
                     and expected['crypto_or_native_effect_grant'] is False,'CURRENT_DISPATCH_ISSUANCE_SUBJECT')
            else:
                need(schema=='dg16.root-binary-cipher-publication-admission.v2' and a.prepared and a.prepared_manifest_sha256,'CURRENT_BINARY_REQUIREMENTS_ONLY')
                _,bodies=prepared(P,a.prepared,a.prepared_manifest_sha256)
                need(req==bodies['ADMISSION_REQUIREMENTS.json'] and expected['issuer_thread']==ROOT
                     and expected['sender_install_manifest']==P.desc(mraw) and expected['context']==op['context']
                     and expected['automatic_retry'] is False and expected['private_key_operation'] is False
                     and expected['deadline_unix_ms']<=op['expires_unix_ms'],'CURRENT_BINARY_ISSUANCE_SUBJECT')
            result=issue(P,expected,P.row(a.requirements,a.requirements_sha256),a.output,a.issuance_record,a.root_decision_ref)
        else:
            need(a.prepared and a.prepared_manifest_sha256,'RECEIVED_PREPARED_MANIFEST_REQUIRED')
            row,bodies=prepared(P,a.prepared,a.prepared_manifest_sha256)
            result=dict(authority='NONE',prepared_manifest=row,plan=P.row(Path(a.prepared)/'PLAN.json'),purpose=bodies['PURPOSE.json'],deadline_unix_ms=bodies['PLAN.json']['expires_unix_ms'])
            if a.action=='binary-selection':
                config=P.parse(P.read(a.configuration,65536,digest(a.configuration_sha256)))
                template=dict(config); admission=template.pop('admission')
                need(template==bodies['CONFIG_INPUTS.json'],'EXACT_PUBLICATION_CONFIG_TEMPLATE')
                need(P.parse(P.read(admission['path'],65536,admission['sha256']))==bodies['ADMISSION_REQUIREMENTS.json']['expected_body'],'EXACT_ISSUED_BINARY_ADMISSION')
                for key in ('binary','journal','decoder','resolver'):
                    P.read(PINS[key][0],1048576,PINS[key][1])
                result.update(selection=dict(rolePath=PINS['binary'][0],roleSha256=PINS['binary'][1],configurationPath=a.configuration,configurationSha256=a.configuration_sha256,controlDriverPath=PINS['journal'][0]),
                              trustedPlanRaw=P.read(Path(a.prepared)/'PLAN.json',65536).decode('ascii'),
                              driver_sha256='2deab0598af223126ecfc14ddf1246e23c0786fa661d31fda5bbb1b66319a595',
                              invocation='EXISTING_runBinaryWithSelection_ONCE_ONLY',actual_effects=0)
    print(encode(result).decode('ascii'),end='')


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, KeyError, TypeError, AttributeError):
        sys.stderr.write('ROOT_LIVE_RECIPE_STEP_REFUSED_NO_RETRY\n')
        raise SystemExit(1)
