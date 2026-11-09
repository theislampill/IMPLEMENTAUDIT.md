"""Root-only local input wiring; never starts sender, tools, crypto or a host.

Root independently authenticates all supplied receipts and owns actual admission.
Generated requirements, plans and configs have no authority. No automatic retry.
Do not execute publication-inputs on a live packet from the Sol source task.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import stat
import sys
import time
import types

BASE = Path('/home/agent/dg16-g1-current04-operators')
FINAL = BASE / 'root-final-operators-01'
BINARY = FINAL / 'binary_publish_v3.py'
BINARY_SHA = '7f71f5928be04d194cdb1a19c04e6b5865173f9c488c13e0c91309a0aa6a5978'
CONTROL = FINAL / 'control_process_v3.py'
RESOLVER = BASE / 'public-receiver-02/author/resolve_artifact.py'
ISSUER = '01a1953f-a15b-7811-aa72-3538ebb03562'


def need(ok, code):
    if not ok:
        raise ValueError(code)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def desc(raw):
    return {'bytes': len(raw), 'sha256': sha(raw)}


def encode(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':'),
                       ensure_ascii=True, allow_nan=False) + '\n').encode('ascii')


def parse(raw):
    def pairs(rows):
        result = {}
        for name, value in rows:
            need(name not in result, 'DUPLICATE_KEY')
            result[name] = value
        return result
    return json.loads(raw, object_pairs_hook=pairs,
                      parse_constant=lambda _: need(False, 'NONFINITE'))


def exact_path(path):
    path = Path(path)
    need(path.is_absolute() and path.is_relative_to(BASE)
         and path.resolve(strict=True) == path, 'CANONICAL_ROOT_PATH')
    return path


def read(path, maximum=4*1024**2, pin=None):
    path = exact_path(path)
    before = path.lstat()
    need(stat.S_ISREG(before.st_mode) and before.st_nlink == 1
         and before.st_uid == os.geteuid()
         and stat.S_IMODE(before.st_mode) in (0o400, 0o444, 0o600)
         and 0 < before.st_size <= maximum, 'OWNED_BOUNDED_INPUT')
    mark = lambda s: (s.st_dev, s.st_ino, s.st_mode, s.st_nlink, s.st_uid,
                      s.st_gid, s.st_size, s.st_mtime_ns, s.st_ctime_ns)
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK | os.O_CLOEXEC)
    try:
        need(mark(os.fstat(fd)) == mark(before) and not os.listxattr(fd), 'INPUT_OPEN_CHANGED')
        raw = os.pread(fd, before.st_size+1, 0)
        need(len(raw) == before.st_size and mark(os.fstat(fd)) == mark(before)
             == mark(path.lstat()) and path.resolve(strict=True) == path,
             'INPUT_CLOSING_CHANGED')
    finally:
        os.close(fd)
    need(pin is None or sha(raw) == pin, 'ROOT_SELECTED_INPUT_HASH')
    return raw


def row(path, pin=None, maximum=4*1024**2):
    path = Path(path)
    raw = read(path, maximum, pin)
    return {'path': str(path), 'sha256': sha(raw)}


def module(path, raw, name):
    result = types.ModuleType(name)
    result.__file__ = str(path)
    exec(compile(raw, str(path), 'exec'), result.__dict__)
    return result


def current(operation, now):
    need(type(now) is int and type(operation['issued_unix_ms']) is int
         and type(operation['expires_unix_ms']) is int
         and operation['issued_unix_ms'] <= now < operation['expires_unix_ms']
         <= operation['issued_unix_ms'] + 600000, 'ORIGINAL_OPERATION_EXPIRED')


def fresh_path(path):
    path = Path(path)
    parent = exact_path(path.parent)
    st = parent.stat()
    need(stat.S_ISDIR(st.st_mode) and st.st_uid == os.geteuid()
         and stat.S_IMODE(st.st_mode) == 0o700 and not os.path.lexists(path),
         'FRESH_PRIVATE_OUTPUT')
    return path


def write_file(path, raw):
    path = fresh_path(path)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC, 0o600)
    try:
        offset = 0
        while offset < len(raw):
            count = os.write(fd, raw[offset:])
            need(count > 0, 'OUTPUT_WRITE_PROGRESS')
            offset += count
        os.fsync(fd)
    finally:
        os.close(fd)
    need(read(path, max(1, len(raw))) == raw, 'OUTPUT_READBACK')
    fd = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def write_directory(path, files):
    path = fresh_path(path)
    need(0 < len(files) <= 12 and all(Path(n).name == n for n in files), 'FIXED_OUTPUT_MEMBERS')
    path.mkdir(mode=0o700)
    for name, raw in files.items():
        write_file(path/name, raw)
    return {n: desc(raw) for n, raw in files.items()}


def episode_inputs(episode):
    episode = exact_path(episode)
    assembled = episode/'assembled'
    manifest_raw = read(assembled/'ROOT_SENDER_INSTALL_MANIFEST.json')
    manifest = parse(manifest_raw)
    entry_path = assembled/'root_sender_entry.py'
    entry_raw = read(entry_path, 1024**2)
    need(manifest['members']['root_sender_entry.py'] == desc(entry_raw), 'SENDER_ENTRY_INSTALL_JOIN')
    op_path = assembled/'packet/carrier/PRO_SENDER_OPERATION.json'
    op_raw = read(op_path, 65536)
    need(manifest['members']['packet/carrier/PRO_SENDER_OPERATION.json'] == desc(op_raw), 'SENDER_OPERATION_INSTALL_JOIN')
    op = parse(op_raw)
    current(op, time.time_ns()//1000000)
    return assembled, entry_path, entry_raw, op_path, op, manifest_raw


def dispatcher_selection(args):
    assembled, entry, _, operation_path, _, _ = episode_inputs(args.episode)
    receipt = row(args.late_receiving, args.late_receiving_sha256)
    helper_parent = fresh_path(args.install)
    # Binder creates this final directory directly: no post-bind relocation.
    selection = dict(entry_path=str(entry), operation_path=str(operation_path),
                     helper_path=str(helper_parent/'dispatcher_entry.py'),
                     python_path='/usr/bin/python3', late_sender_receiving_path=receipt['path'])
    raw = encode(selection)
    write_file(args.output, raw)
    return {'authority': 'NONE', 'selection': row(args.output),
            'Root_late_receiving': receipt, 'binder_output': str(helper_parent),
            'sender_started': False, 'actual_admission': False}


def expected_admission(B, plan, config, receiving_raw, manifest_raw, terminal_raw):
    return dict(schema='dg16.root-binary-cipher-publication-admission.v2', issuer_thread=ISSUER,
                context=plan['context'], branch=plan['branch'], parent_sha=plan['parent_sha'],
                sender_receiving=desc(receiving_raw), sender_install_manifest=desc(manifest_raw),
                sender_terminal=desc(terminal_raw), parent_ref_result=config['parent_ref_result'],
                files=plan['files'], request=plan['request'],
                readback_profile=B.READBACK_PROFILE, file_reader_source_sha256=B.FILE_READER_SHA,
                frame_seconds=B.FRAME_SECONDS, argument_chunk_bytes=B.ARGUMENT_CHUNK_BYTES,
                expected_tree=plan['expected_tree'],
                journal_directory=config['journal_directory'], deadline_unix_ms=plan['expires_unix_ms'],
                tools=list(B.TOOLS), automatic_retry=False, private_key_operation=False, original_awards=[])


def publication_inputs(args):
    assembled, entry_path, entry_raw, _, op, manifest_raw = episode_inputs(args.episode)
    B = module(BINARY, read(BINARY, 1024**2, BINARY_SHA), 'root_binary_plan_source')
    # Actual Root receiving supplies authentication and actual exit/custody evidence;
    # these hashes bind inputs but do not convert local JSON into native evidence.
    terminal_raw = read(args.sender_terminal, 65536, args.sender_terminal_sha256)
    terminal = B.parse(terminal_raw)
    need(terminal['result']['status'] == 'PAYLOAD_READY', 'NO_REENCRYPTION_OR_UNREADY_READ')
    receiving_raw = read(args.sender_receiving, 4*1024**2, args.sender_receiving_sha256)
    E = module(entry_path, entry_raw, 'actual_root_sender_inputs_only')
    loader, m, binding, selected, archive = E.inputs()  # Never E.sender().
    directory = m.carrier.session_path(binding, selected['operation']['context'], root=True)
    outcome_raw = m.files.read_file(directory/'OUTCOME.json', 65536, private=True)[0]
    outcome = m.policy.parse(outcome_raw, 65536)
    need(outcome['public'] == terminal['result'] and outcome['public']['cleanup_complete'] is True,
         'ACTUAL_SINGLE_SENDER_OUTCOME')
    files = {n: m.files.read_file(directory/n, m.policy.MAX_CONTROL if n == 'CONTROL.json'
                                else m.policy.MAX_CIPHERTEXT, private=True)[0]
             for n in ('CONTROL.json', 'INPUTS.cms')}
    request = m.provider.artifact_files(archive)['REQUEST.json']
    m.carrier.require_auth_enveloped(files['INPUTS.cms'])
    now = time.time_ns()//1000000
    plan = B.plan(m.policy, m.provider, binding, request, terminal,
                  files['CONTROL.json'], files['INPUTS.cms'], now)
    need(type(args.deadline_unix_ms) is int and now < args.deadline_unix_ms <= op['expires_unix_ms'],
         'ROOT_DEADLINE_WITHIN_ORIGINAL_WINDOW')
    plan['expires_unix_ms'] = min(plan['expires_unix_ms'], op['expires_unix_ms'], args.deadline_unix_ms)
    parent_row = row(args.parent_ref_result, args.parent_ref_sha256)
    parent = B.unwrap(read(args.parent_ref_result, B.MAX_RESULT, args.parent_ref_sha256),
                      'https://api.github.com/repos/'+plan['repository']+'/git/ref/heads/'
                      + B.urllib.parse.quote(plan['branch'], safe='/'))
    need(parent.get('ref') == 'refs/heads/'+plan['branch'] and parent.get('object', {}).get('type') == 'commit'
         and parent['object']['sha'] == plan['parent_sha'], 'ACTUAL_EXPECTED_PARENT_REF')
    journal = fresh_path(args.journal_directory)
    config = dict(issuer_thread=ISSUER, control_driver_path=str(CONTROL), resolver_path=str(RESOLVER),
                  sender_entry=row(entry_path), sender_install_manifest=row(assembled/'ROOT_SENDER_INSTALL_MANIFEST.json'),
                  sender_terminal=row(args.sender_terminal, args.sender_terminal_sha256),
                  sender_receiving=row(args.sender_receiving, args.sender_receiving_sha256),
                  parent_ref_result=parent_row, journal_directory=str(journal), deadline_unix_ms=plan['expires_unix_ms'])
    # Verify the exact frozen executable dependencies without invoking their CLIs.
    read(CONTROL, 1024**2, B.CONTROL_DRIVER_SHA)
    read(RESOLVER, 1024**2, 'b2ac1130149d9878a3a00c7d8ba214743920a1aede38cb6b75699e14a2d03530')
    q = m.policy.parse(request, m.policy.MAX_REQUEST)
    purpose = dict(request_nonce=q['nonce'], recipient_sha256=q['recipient_sha256'],
                   input_index_sha256=q['input_index_sha256'])
    expected = expected_admission(B, plan, config, receiving_raw, manifest_raw, terminal_raw)
    m.carrier.current_binding(binding)
    m.sender_policy.current(selected)
    loader.current()
    current(op, time.time_ns()//1000000)
    need(time.time_ns()//1000000 < plan['expires_unix_ms'], 'PUBLICATION_WINDOW_CLOSED')
    bodies = {'PLAN.json': B.encode(plan), 'PURPOSE.json': encode(purpose),
              'CONFIG_INPUTS.json': encode(config),
              'ADMISSION_REQUIREMENTS.json': encode(dict(authority='NONE', actual_admission=False,
                                                         expected_body=expected, original_awards=[]))}
    bodies['PREPARED_MANIFEST.json'] = encode(dict(authority='NONE', issuer_authentication=False,
        members={n: desc(raw) for n, raw in bodies.items()}, binary_module_sha256=BINARY_SHA,
        original_awards=[]))
    rows = write_directory(args.output, bodies)
    return {'authority': 'NONE', 'files': rows, 'directory': str(args.output),
            'actual_admission': False, 'sender_or_tool_or_crypto_executed': False,
            'Root_independent_plan_and_purpose_authentication_required': True}


def publication_config(args):
    prepared = exact_path(args.prepared)
    manifest = parse(read(prepared/'PREPARED_MANIFEST.json', 65536, args.prepared_manifest_sha256))
    names = {'PLAN.json', 'PURPOSE.json', 'CONFIG_INPUTS.json', 'ADMISSION_REQUIREMENTS.json'}
    need(set(manifest['members']) == names and manifest['binary_module_sha256'] == BINARY_SHA,
         'EXACT_PREPARED_MEMBER_SET')
    received = {n: read(prepared/n, 65536, manifest['members'][n]['sha256']) for n in names}
    need(all(desc(raw) == manifest['members'][n] for n, raw in received.items()), 'PREPARED_INPUT_DRIFT')
    requirements = parse(received['ADMISSION_REQUIREMENTS.json'])
    need(requirements['authority'] == 'NONE' and requirements['actual_admission'] is False,
         'REQUIREMENTS_ARE_NOT_ADMISSION')
    expected = requirements['expected_body']
    raw = read(args.admission, 65536, args.admission_sha256)
    need(parse(raw) == expected and raw == encode(expected), 'ACTUAL_ROOT_ADMISSION_BODY')
    config = parse(received['CONFIG_INPUTS.json'])
    need(time.time_ns()//1000000 < config['deadline_unix_ms'] == expected['deadline_unix_ms'],
         'PUBLICATION_WINDOW_CLOSED')
    for name in ('sender_entry', 'sender_install_manifest', 'sender_terminal', 'sender_receiving', 'parent_ref_result'):
        row(config[name]['path'], config[name]['sha256'])
    fresh_path(config['journal_directory'])
    config['admission'] = row(args.admission, args.admission_sha256, 65536)
    write_file(args.output, encode(config))
    return {'authority': 'NONE', 'configuration': row(args.output),
            'actual_tools_called': 0, 'Root_actual_issuer_authentication_required': True}


def parser():
    p = argparse.ArgumentParser(description=__doc__)
    s = p.add_subparsers(dest='command', required=True)
    d = s.add_parser('dispatcher-selection')
    d.add_argument('--episode', type=Path, required=True)
    d.add_argument('--late-receiving', type=Path, required=True)
    d.add_argument('--late-receiving-sha256', required=True)
    d.add_argument('--install', type=Path, required=True)
    d.add_argument('--output', type=Path, required=True)
    d.set_defaults(action=dispatcher_selection)
    v = s.add_parser('publication-inputs')
    v.add_argument('--episode', type=Path, required=True)
    for name in ('sender-terminal', 'sender-receiving', 'parent-ref-result', 'journal-directory', 'output'):
        v.add_argument('--'+name, type=Path, required=True)
    for name in ('sender-terminal-sha256', 'sender-receiving-sha256', 'parent-ref-sha256'):
        v.add_argument('--'+name, required=True)
    v.add_argument('--deadline-unix-ms', type=int, required=True)
    v.set_defaults(action=publication_inputs)
    c = s.add_parser('publication-config')
    for name in ('prepared', 'admission', 'output'):
        c.add_argument('--'+name, type=Path, required=True)
    c.add_argument('--admission-sha256', required=True)
    c.add_argument('--prepared-manifest-sha256', required=True)
    c.set_defaults(action=publication_config)
    return p


def main():
    args = parser().parse_args()
    need(sys.platform == 'linux' and sys.flags.isolated and sys.dont_write_bytecode
         and os.getuid() == os.geteuid() > 0 and os.getgid() == os.getegid(), 'ROOT_FIXED_NONROOT_RUNTIME')
    print(json.dumps(args.action(args), sort_keys=True, separators=(',', ':')))


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, KeyError, TypeError, AttributeError):
        sys.stderr.write('ROOT_PIPELINE_INPUTS_REFUSED_NO_AUTOMATIC_RETRY\n')
        raise SystemExit(1)
