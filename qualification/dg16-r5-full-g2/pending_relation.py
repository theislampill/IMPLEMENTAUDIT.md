"""Closed relations for the two source-declared pending-fixture artifacts.

Input bytes must first pass full_evidence.receive_declared. Raw duration and
physical-history operands remain retained; this functional relation grants no
physical/native/occurrence authority and never weakens original test assertions.
"""
import copy
import hashlib
import json
import math
import re
import stat


class Refusal(ValueError):
    pass


def demand(value, code):
    if not value:
        raise Refusal(code)


def desc(raw):
    return {'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}


def encoded(value, *, indent=None, sort_keys=True, newline=True):
    return (json.dumps(value, indent=indent, sort_keys=sort_keys, ensure_ascii=False, allow_nan=False) + ('\n' if newline else '')).encode()


def finite_duration(value):
    demand(type(value) in (int, float) and math.isfinite(value) and value >= 0, 'PENDING_DURATION_DOMAIN')


SESSION = 'portable-pending-session'
SESSION_SHA = hashlib.sha256(SESSION.encode()).hexdigest()
BINDING_SHA = hashlib.sha256(('codex\0' + SESSION).encode()).hexdigest()
PENDING = 'constructed/store/compaction-audits-v1/' + SESSION_SHA + '/pending.json'
BINDING = 'constructed/store/bindings/' + BINDING_SHA[:2] + '/' + BINDING_SHA + '/binding.json'
PEER = 'source-peers/native-runtime/skills/implementaudit/scripts/'
PATH_FIELDS = {
    'explicit_run_root': 'constructed/worktree/.IMPLEMENTAUDIT/runs/fixture',
    'repository_identity': 'constructed/repository',
    'git_common_directory_identity': 'constructed/git-common',
    'worktree_identity': 'constructed/worktree',
}
BINDING_FIELDS = set(('schema host_id host_session_id controller_id claim_id explicit_run_root repository_identity '
                     'git_common_directory_identity worktree_identity binding_generation activation_event_id activation_receipt '
                     'applicable_continuity_generation applicable_continuity_receipt status predecessor_generation '
                     'supersession_or_tombstone_reason').split())
PROCESS_FIELDS = {'number', 'command', 'input', 'pending_before', 'exit', 'stdout', 'stderr',
                  'elapsed_seconds', 'pending_after'}

# Exact ordered control populations the two frozen producers emit for source 205aeab7 (durability 58; loader
# --top-level-counter-controls-only 54). Equality, not a shape: an extra, missing, reordered, renamed, empty,
# duplicate, non-string or differently-cased control refuses.
CONTROL_NAMES = {
    'pending_durability': (
        'constructed-attribution-remains-host-unproved empty-status-three-reads-zero-observations-zero-writes '
        'unresolved-currentness-or-absent-epoch-retains-durable-obligation '
        'repeated-resume-versions-one-unresolved-identity pending-status-four-reads-zero-observations-zero-writes '
        'crash-before-replace-retains-original-and-releases-writer-lock '
        'crash-after-replace-reloads-coherent-unconsumed-successor '
        'source-registration-requires-unmodified-selected-native-profile native-profile-absence-refuses-reservation '
        'unreserved-return-refuses-without-state-change unreserved-JOIN-refuses-without-state-change '
        'foreign-owner-cannot-modify-pending unknown-child-cannot-observe-pending status-rejects-observation-payload '
        'malformed-resume-retains-pending nonobject-request-retains-pending duplicate-request-key-retains-pending '
        'path-custody-regular-pending-reloads-read-only path-custody-genuine-absence-remains-read-only '
        'path-custody-dangling-file-refuses-status path-custody-dangling-file-refuses-resume '
        'path-custody-dangling-ancestor-refuses-status path-custody-dangling-ancestor-refuses-resume '
        'path-custody-fifo-refuses-status path-custody-original-pending-restored-exactly '
        'stored-json-unique-keys-remain-held-and-nonobserving stored-json-duplicate-observations-refuses-status '
        'stored-json-duplicate-observations-refuses-resume stored-json-duplicate-consumed-version-refuses-status '
        'stored-json-duplicate-consumed-version-refuses-resume stored-json-utf16-refuses-status '
        'stored-json-utf8-bom-refuses-status stored-json-preopen-nonregular-replacement-refuses '
        'stored-counter-genuine-integers-held-four-reads-zero-observations-zero-writes '
        'stored-counter-absence-three-reads-zero-observations-zero-writes stored-counter-value-only-two-1 '
        'stored-counter-value-only-two-2 stored-counter-genuine-resume-preserves-integer-successor '
        'stored-counter-version-nan-refuses-status stored-counter-version-nan-refuses-resume '
        'stored-counter-version-boolean-refuses-status stored-counter-version-boolean-refuses-resume '
        'stored-counter-version-float-refuses-status stored-counter-version-float-refuses-resume '
        'stored-counter-version-zero-refuses-status stored-counter-version-zero-refuses-resume '
        'stored-counter-version-negative-refuses-status stored-counter-version-negative-refuses-resume '
        'stored-counter-consumed-nan-refuses-status stored-counter-consumed-nan-refuses-resume '
        'stored-counter-consumed-boolean-refuses-status stored-counter-consumed-boolean-refuses-resume '
        'stored-counter-consumed-float-refuses-status stored-counter-consumed-float-refuses-resume '
        'stored-counter-consumed-negative-refuses-status stored-counter-consumed-negative-refuses-resume '
        'stored-counter-consumed-future-refuses-status stored-counter-consumed-future-refuses-resume').split(),
    'pending_loader': (
        'constructed-attribution-host-activation-false absent-status-original-three-file-read-guard '
        'finite-status-original-four-file-read-guard top-counter-empty-zero-status '
        'top-counter-empty-negative-refuses-status top-counter-revision-integer-0-held '
        'top-counter-revision-integer-1-held top-counter-revision-negative-refuses-status '
        'top-counter-revision-negative-refuses-resume top-counter-revision-boolean-refuses-status '
        'top-counter-revision-boolean-refuses-resume top-counter-revision-fraction-refuses-status '
        'top-counter-revision-fraction-refuses-resume top-counter-revision-string-refuses-status '
        'top-counter-revision-string-refuses-resume top-counter-revision-null-refuses-status '
        'top-counter-revision-null-refuses-resume top-counter-revision-nan-refuses-status '
        'top-counter-revision-nan-refuses-resume top-counter-revision-overflow-refuses-status '
        'top-counter-revision-overflow-refuses-resume top-counter-signals-integer-0-held '
        'top-counter-signals-integer-1-held top-counter-signals-negative-refuses-status '
        'top-counter-signals-negative-refuses-resume top-counter-signals-boolean-refuses-status '
        'top-counter-signals-boolean-refuses-resume top-counter-signals-fraction-refuses-status '
        'top-counter-signals-fraction-refuses-resume top-counter-signals-string-refuses-status '
        'top-counter-signals-string-refuses-resume top-counter-signals-null-refuses-status '
        'top-counter-signals-null-refuses-resume top-counter-signals-nan-refuses-status '
        'top-counter-signals-nan-refuses-resume top-counter-signals-overflow-refuses-status '
        'top-counter-signals-overflow-refuses-resume top-counter-unresolved_signal_version-integer-0-held '
        'top-counter-unresolved_signal_version-integer-1-held '
        'top-counter-unresolved_signal_version-negative-refuses-status '
        'top-counter-unresolved_signal_version-negative-refuses-resume '
        'top-counter-unresolved_signal_version-boolean-refuses-status '
        'top-counter-unresolved_signal_version-boolean-refuses-resume '
        'top-counter-unresolved_signal_version-fraction-refuses-status '
        'top-counter-unresolved_signal_version-fraction-refuses-resume '
        'top-counter-unresolved_signal_version-string-refuses-status '
        'top-counter-unresolved_signal_version-string-refuses-resume '
        'top-counter-unresolved_signal_version-null-refuses-status '
        'top-counter-unresolved_signal_version-null-refuses-resume '
        'top-counter-unresolved_signal_version-nan-refuses-status '
        'top-counter-unresolved_signal_version-nan-refuses-resume '
        'top-counter-unresolved_signal_version-overflow-refuses-status '
        'top-counter-unresolved_signal_version-overflow-refuses-resume top-counter-original-unresolved-state-retained').split(),
}


def binding(value, root, token):
    expected = {
        'schema': 'implementaudit.host-session-binding.v1', 'host_id': 'codex', 'host_session_id': SESSION,
        'controller_id': 'fixture-controller', 'claim_id': 'fixture-claim', 'binding_generation': 'G0001',
        'activation_event_id': 'fixture-activation', 'activation_receipt': 'opaque-fixture-activation',
        'applicable_continuity_generation': 'G0001', 'applicable_continuity_receipt': 'opaque-fixture-continuity',
        'status': 'ACTIVE', 'predecessor_generation': None, 'supersession_or_tombstone_reason': None,
        **{key: root + '/' + relative for key, relative in PATH_FIELDS.items()},
    }
    demand(set(value) == BINDING_FIELDS and value == expected, 'PENDING_CONSTRUCTED_BINDING')
    return {**value, **{key: token + '/' + relative for key, relative in PATH_FIELDS.items()}}


def report(value, role, profile, root, token):
    common = {'authority', 'host_activation_proven', 'native_JOIN_consumption', 'native_lifecycle',
              'source_sha256', 'evidence_dir', 'result', 'controls', 'process_count', 'source_unchanged'}
    fields = (common | {'scope', 'native_activation', 'authentic_physical_boundary',
                        'native_producer_runtime_equivalence', 'source_file_count', 'limitations',
                        'reservation_refusal_profile', 'control_names', 'materialization'} | set(profile['pending_ceiling'])
              if role == 'pending_durability' else
              common | {'schema', 'selection', 'include_existing_counter_controls', 'failures'})
    demand(set(value) == fields and value['source_sha256'] == profile['pending_source_pins'] and
           value['evidence_dir'] == root and value['result'] == 'PASS' and value['source_unchanged'] is True and
           value['authority'] == 'NONE' and value['host_activation_proven'] is False and
           value['native_JOIN_consumption'] == 'UNPROVED' and value['native_lifecycle'] == 'NOT_CLAIMED',
           'PENDING_REPORT_FIELDS_SOURCE_OR_AUTHORITY')
    if role == 'pending_durability':
        demand(value['scope'] == 'PORTABLE_ACTUAL_OWNER_CLI_PROCESS_CRASH_ONLY' and
               value['native_activation'] == value['authentic_physical_boundary'] == 'UNPROVED' and
               value['native_producer_runtime_equivalence'] == 'UNVERIFIED' and
               value['source_file_count'] == len(profile['pending_source_pins']) and
               value['limitations'] == profile['pending_limitations'] and
               value['reservation_refusal_profile'] == profile['pending_reservation_profile'] and
               {key: value[key] for key in profile['pending_ceiling']} == profile['pending_ceiling'],
               'PENDING_DURABILITY_REPORT')
        controls = value['control_names']
        demand(type(value['controls']) is int and value['controls'] == len(controls), 'PENDING_CONTROL_COUNT')
    else:
        demand(value['schema'] == 'constructed.pending-stored-loader-qualification.v1' and
               value['selection'] == 'top-level-counter-controls-only' and
               value['include_existing_counter_controls'] is False and value['failures'] == [], 'PENDING_LOADER_SELECTION')
        controls = value['controls']
    demand(type(controls) is list and all(type(name) is str for name in controls) and controls == CONTROL_NAMES[role],
           'PENDING_CONTROL_POPULATION')
    demand(type(value['process_count']) is int and 0 < value['process_count'] <= 1024, 'PENDING_PROCESS_COUNT')
    return {**value, 'evidence_dir': token}


def command(row, root, token, source, runtime_python):
    command = row['command']
    # Both frozen producers are launched as PATH `python3` (tests/internal-skill-routing.test.sh:284,286) and re-enter
    # sys.executable, so every recorded argv[0] is exactly the runtime directory's python3, never its `python` alias.
    interpreter = runtime_python.rsplit('/', 1)[0] + '/python3'
    demand(type(command) is list and 7 <= len(command) <= 48 and all(type(v) is str and len(v.encode()) <= 4096 for v in command)
           and command[:2] == [interpreter, '-B'], 'PENDING_COMMAND_SHAPE')
    normalized = list(command)
    owners = ('compaction-audit-pending.py', 'host-session-binding.py')
    scripts = {source + '/' + PEER + name for name in owners}
    materialized = {root + '/constructed-source-tree/skills/implementaudit/scripts/' + name for name in owners}
    if command[3] == '--worker':
        demand(len(command) == 10 and command[2] == source + '/tests/cognition-pending-durability.py' and
               command[4] in ('before-replace', 'after-replace', 'status-guard', 'pending-open-nonregular') and
               command[5] == source + '/' + PEER + 'compaction-audit-pending.py' and
               command[6:] == [root + '/constructed/store', SESSION, 'fixture-owner', 'resume' if command[4] in ('before-replace', 'after-replace') else 'status'],
               'PENDING_WORKER_ROLE')
        expected_exit = {'before-replace': 91, 'after-replace': 92, 'status-guard': 0, 'pending-open-nonregular': 2}[command[4]]
        demand(row['exit'] == expected_exit, 'PENDING_WORKER_EXIT')
        normalized[6] = token + '/constructed/store'
        return normalized, command[9], command[4], 'compaction-audit-pending.py'
    demand(command[2] in scripts | materialized and row['exit'] in (0, 2), 'PENDING_SCRIPT_OR_EXIT')
    script = command[2].rsplit('/', 1)[1]
    if command[2] in materialized: normalized[2] = token + command[2][len(root):]
    actions = {'init', 'bind'} if script == 'host-session-binding.py' else {
        'status', 'resume', 'register-source', 'reserve', 'return', 'join', 'observe-child'}
    selected = [item for item in command[3:] if item in actions]
    demand(len(selected) == 1, 'PENDING_ACTION_ROLE')
    path_flags = {'--store': 'constructed/store', **{'--' + key.replace('_', '-'): value for key, value in PATH_FIELDS.items()}}
    for index in range(3, len(command)):
        if command[index - 1] in path_flags:
            relative = path_flags[command[index - 1]]
            demand(command[index] == root + '/' + relative, 'PENDING_COMMAND_PATH_BINDING')
            normalized[index] = token + '/' + relative
        elif root in command[index]:
            demand(False, 'UNKNOWN_PENDING_COMMAND_PATH')
    demand(command.count('--store') == 1 and '--session' not in command if script == 'host-session-binding.py' else
           command.count('--store') == command.count('--session') == command.count('--owner-id') == 1 and
           command[command.index('--session') + 1] == SESSION, 'PENDING_COMMAND_CONTEXT')
    return normalized, selected[0], None, script


def physical_projection(value, row, files, normalized_files, evidence):
    demand(set(value) == {'before', 'after'}, 'PENDING_PHYSICAL_FIELDS')
    result = copy.deepcopy(value)
    stamps = {}
    for stage in ('before', 'after'):
        observed = value[stage]
        if observed == {'store_absent': True}:
            demand(row['number'] == 1 and stage == 'before', 'PENDING_STORE_ABSENCE_ROLE')
            stamps[stage] = {}; continue
        demand(type(observed) is dict and '.' in observed, 'PENDING_PHYSICAL_NAMESPACE')
        inodes = []
        for name, info in observed.items():
            demand(type(name) is str and (name == '.' or (not name.startswith('/') and '..' not in name.split('/'))) and
                   set(info) == {'mode', 'inode', 'mtime_ns', 'ctime_ns', 'bytes', 'sha256'}, 'PENDING_PHYSICAL_ROW')
            demand(all(type(info[key]) is int and info[key] >= (1 if key == 'inode' else 0)
                       for key in ('mode', 'inode', 'mtime_ns', 'ctime_ns')), 'PENDING_PHYSICAL_NUMBERS')
            inodes.append(info['inode'])
            relative = 'constructed/store' + ('' if name == '.' else '/' + name)
            if stat.S_ISREG(info['mode']):
                demand(type(info['bytes']) is int and 0 <= info['bytes'] <= 16*1024**2 and
                       type(info['sha256']) is str and re.fullmatch('[0-9a-f]{64}', info['sha256']),
                       'PENDING_PHYSICAL_DESCRIPTOR_TYPE')
                if relative == PENDING:
                    descriptor = row['pending_' + stage]
                    demand(descriptor is not None, 'PENDING_PHYSICAL_PREIMAGE_ABSENT')
                    raw = files[descriptor['path']]; normalized = raw
                else:
                    demand(relative in files, 'PENDING_PHYSICAL_UNBOUND_FILE')
                    raw, normalized = files[relative], normalized_files[relative]
                demand({'bytes': info['bytes'], 'sha256': info['sha256']} == desc(raw), 'PENDING_PHYSICAL_RAW_DIGEST')
                result[stage][name].update(desc(normalized))
            else:
                demand(stat.S_ISDIR(info['mode']) and info['bytes'] is None and info['sha256'] is None, 'PENDING_PHYSICAL_KIND')
        demand(len(inodes) == len(set(inodes)), 'PENDING_PHYSICAL_IDENTITY_ALIAS')
        stamps[stage] = observed
    # Original status/refusal assertions compare the complete within-call
    # snapshots. Keep that predicate, not merely a normalized resemblance.
    if row['number'] > 2 and (row['exit'] == 2 or row['command'][-1] == 'status'):
        demand(value['before'] == value['after'], 'PENDING_READONLY_PHYSICAL_ASSERTION')
    for name in set(stamps['before']) | set(stamps['after']):
        for field in ('inode', 'mtime_ns', 'ctime_ns'):
            before = stamps['before'].get(name, {}).get(field)
            after = stamps['after'].get(name, {}).get(field)
            if before is not None: result['before'][name][field] = '<BEFORE_' + field.upper() + '>'
            if after is not None:
                relation = 'NEW' if before is None else 'SAME' if before == after else (
                    'CHANGED' if field == 'inode' else 'LATER' if after > before else 'EARLIER')
                result['after'][name][field] = '<AFTER_' + field.upper() + '_' + relation + '>'
    return result


def materialization(received, profile, source_manifest, peer_manifests, evidence):
    files = received['files']; raw = files['materialization-record.json']; record = evidence.strict(raw)
    demand(raw == encoded(record, indent=2, sort_keys=False) and set(record) == {
        'frozen_commit', 'scope', 'native_admission', 'selected_file_count', 'selected_files', 'commands'}, 'MATERIALIZATION_RECORD')
    selected = []
    for manifest in peer_manifests:
        selected.extend({k: item[k] for k in ('path', 'materialized_path', 'bytes', 'sha256', 'mode')} for item in manifest['files'])
    demand(record['selected_files'] == selected and record['selected_file_count'] == len(selected) and
           record['frozen_commit'] == profile['source_commit'] and record['scope'] == 'SOURCE_ONLY_PRE_SELECTION_REFUSAL' and
           record['native_admission'] == 'NOT_ESTABLISHED' and received['report']['materialization'] == {
               key: record[key] for key in ('frozen_commit', 'scope', 'native_admission', 'selected_file_count')},
           'MATERIALIZATION_SOURCE_BINDING')
    expected = {row['path']: row for row in source_manifest['members'] if row['path'].startswith(('skills/', 'source-peers/'))}
    for item in selected: expected[item['materialized_path']] = item
    prefix = 'constructed-source-tree/'
    actual = {name[len(prefix):]: data for name, data in files.items() if name.startswith(prefix)}
    demand(set(actual) == set(expected), 'MATERIALIZED_COMPLETE_POPULATION')
    for name, data in actual.items():
        pin = expected[name]
        demand(desc(data) == {k: pin[k] for k in ('bytes', 'sha256')} and
               received['namespace'][prefix + name]['mode'] == int(pin['mode'], 8) & 0o777, 'MATERIALIZED_SOURCE_BYTES_OR_MODE')
    demand(len(record['commands']) == 2, 'MATERIALIZATION_COMMAND_POPULATION')
    for row, suffix in zip(record['commands'], (['rev-parse', 'HEAD'], ['archive', '--format=tar', profile['source_commit'], 'skills', 'source-peers'])):
        demand(set(row) == {'command', 'exit', 'stdout_bytes', 'stdout_sha256', 'stderr'} and row['exit'] == 0 and
               row['command'] == ['git', '-C', profile['_runtime_source'], *suffix] and row['stderr'] == '' and
               type(row['stdout_bytes']) is int and row['stdout_bytes'] > 0 and re.fullmatch('[0-9a-f]{64}', row['stdout_sha256']),
               'MATERIALIZATION_ACTUAL_COMMAND')
    demand({k: record['commands'][0]['stdout_' + k] for k in ('bytes', 'sha256')} ==
           desc((profile['source_commit'] + '\n').encode()), 'MATERIALIZATION_HEAD_READBACK')


def normalize(received, role, profile, source_manifest, peer_manifests, evidence, *, source, runtime_python):
    root, files = received['root'], received['files']
    token = '<' + role.upper() + '_ARTIFACT_ROOT>'
    changed = dict(files)
    normalized_report = report(received['report'], role, profile, root, token)
    demand(files['report.json'] == encoded(received['report'], indent=2), 'PENDING_REPORT_RAW_BINDING')
    changed['report.json'] = encoded(normalized_report, indent=2)
    binding_state = evidence.strict(files[BINDING])
    demand(files[BINDING] == encoded(binding_state, indent=2) and set(binding_state) == {'schema', 'host_id', 'host_session_id', 'records'} and
           binding_state['schema'] == 'implementaudit.host-session-binding-state.v1' and binding_state['host_id'] == 'codex' and
           binding_state['host_session_id'] == SESSION and len(binding_state['records']) == 1, 'PENDING_BINDING_STORE')
    normalized_state = {**binding_state, 'records': [binding(binding_state['records'][0], root, token)]}
    changed[BINDING] = encoded(normalized_state, indent=2)
    raw_lines = files['process-records.jsonl'].splitlines(keepends=True)
    demand(len(raw_lines) == received['report']['process_count'], 'PENDING_PROCESS_POPULATION')
    rows, normalized_rows, preimages, durations = [], [], set(), []
    for number, raw in enumerate(raw_lines, 1):
        row = evidence.strict(raw)
        demand(set(row) == PROCESS_FIELDS and row['number'] == number and raw == encoded(row) and
               all(type(row[field]) is str for field in ('input', 'stdout', 'stderr')) and type(row['exit']) is int,
               'PENDING_PROCESS_FIELDS_OR_ENCODING')
        for stage in ('before', 'after'):
            member = row['pending_' + stage]
            if member is None: continue
            name = f'preimages/{number:03d}-{stage}.pending.json'
            demand(set(member) == {'path', 'bytes', 'sha256'} and member['path'] == name and name in files and
                   {k: member[k] for k in ('bytes', 'sha256')} == desc(files[name]), 'PENDING_PREIMAGE_BINDING')
            preimages.add(name)
        normalized = copy.deepcopy(row)
        normalized['command'], action, worker, script = command(row, root, token, source, runtime_python)
        finite_duration(row['elapsed_seconds']); durations.append(row['elapsed_seconds'])
        normalized['elapsed_seconds'] = '<PENDING_PROCESS_DIAGNOSTIC_SECONDS>'
        if number == 1: demand(action == 'init' and row['exit'] == 0, 'PENDING_FIRST_INITIALIZATION')
        if number == 2: demand(action == 'bind' and row['exit'] == 0, 'PENDING_SECOND_BINDING')
        if action == 'bind':
            output = evidence.strict(row['stdout'].encode())
            demand(row['stdout'].encode() == encoded(output) and set(output) == {'schema', 'status', 'binding', 'host_activation_proven', 'proof_layers'} and
                   output['schema'] == 'implementaudit.host-session-binding-result.v1' and output['status'] == 'BOUND' and
                   output['host_activation_proven'] is False and output['proof_layers'] == {
                       'source_core': 'PRESENT', 'package': 'UNVERIFIED', 'install': 'UNVERIFIED', 'host_activation': 'UNVERIFIED'} and
                   output['binding'] == binding_state['records'][0], 'PENDING_BIND_OUTPUT')
            normalized['stdout'] = encoded({**output, 'binding': binding(output['binding'], root, token)}).decode()
        if action == 'register-source':
            request = evidence.strict(row['input'].encode())
            relative = 'constructed/unregistered-fixture.jsonl'
            demand(set(request) == {'task_id', 'transcript', 'expected_bytes', 'expected_sha256'} and request['task_id'] == SESSION and
                   request['transcript'] == root + '/' + relative and
                   {'bytes': request['expected_bytes'], 'sha256': request['expected_sha256']} == desc(files[relative]) and
                   row['input'].encode() == encoded(request, sort_keys=False, newline=False), 'PENDING_TRANSCRIPT_REFERENCE')
            normalized['input'] = encoded({**request, 'transcript': token + '/' + relative}, sort_keys=False, newline=False).decode()
        if worker in ('before-replace', 'after-replace'):
            demand(row['stdout'] == '' and row['stderr'] == 'FAULT_REACHED ' + worker + ' ' + root + '/' + PENDING + '\n',
                   'PENDING_CRASH_OPERAND')
            normalized['stderr'] = 'FAULT_REACHED ' + worker + ' ' + token + '/' + PENDING + '\n'
        if root in normalized['stdout']:
            # The only path-bearing ordinary refusal in this selected producer
            # is the deliberately dangling pending ancestor. Preserve errno,
            # message, endpoint role and all other output fields exactly.
            output = evidence.strict(row['stdout'].encode())
            prefix = 'HOST_CUSTODY_UNAVAILABLE: compaction audit pending ancestor is not a resolvable existing directory: [Errno 2] No such file or directory: '
            endpoint = root + '/constructed/store/compaction-audits-v1/absent-path-custody-directory'
            demand(row['exit'] == 2 and action in ('status', 'resume') and output.get('status') == 'PENDING_OPERATION_REFUSED' and
                   output.get('reason') == prefix + repr(endpoint) and row['stdout'].encode() == encoded(output),
                   'UNKNOWN_PENDING_STDOUT_PATH')
            normalized['stdout'] = encoded({**output, 'reason': prefix + repr(token + endpoint[len(root):])}).decode()
        demand(root not in normalized['input'] and root not in normalized['stdout'] and root not in normalized['stderr'],
               'UNKNOWN_PENDING_STREAM_REFERENCE')
        rows.append(row); normalized_rows.append(normalized)
    demand({name for name in files if name.startswith('preimages/')} == preimages, 'PENDING_PREIMAGE_NAMESPACE')
    changed['process-records.jsonl'] = b''.join(encoded(row) for row in normalized_rows)
    expected_aux = set()
    if role == 'pending_loader':
        for row, normalized in zip(rows, normalized_rows):
            number = row['number']; name = f'{number:03d}.physical.json'; expected_aux.add(name)
            observed = evidence.strict(files[name])
            demand(files[name] == encoded(observed, indent=2), 'PENDING_PHYSICAL_ENCODING')
            changed[name] = encoded(physical_projection(observed, row, files, changed, evidence), indent=2)
            for stream in ('stdin', 'stdout', 'stderr'):
                name = f'{number:03d}.{stream}'; expected_aux.add(name)
                key = 'input' if stream == 'stdin' else stream
                demand(files[name] == row[key].encode(), 'PENDING_STREAM_COPY_BINDING')
                changed[name] = normalized[key].encode()
        demand({name for name in files if re.fullmatch(r'[0-9]{3}\.(physical\.json|stdin|stdout|stderr)', name)} == expected_aux,
               'PENDING_AUXILIARY_POPULATION')
    else:
        materialization(received, {**profile, '_runtime_source': source}, source_manifest, peer_manifests, evidence)
    namespace = copy.deepcopy(received['namespace'])
    candidates = [name for name in files if re.fullmatch(re.escape(PENDING.rsplit('/', 1)[0]) + r'/\.pending\.json\.[a-z0-9_]{8}', name)]
    demand(len(candidates) == (1 if role == 'pending_durability' else 0), 'PENDING_ATOMIC_RESIDUE_POPULATION')
    if candidates:
        name = candidates[0]
        crashed = [row for row in rows if row['exit'] == 91]
        demand(len(crashed) == 1 and crashed[0]['pending_before'] == {**crashed[0]['pending_after'], 'path': crashed[0]['pending_before']['path']},
               'PENDING_BEFORE_REPLACE_PREIMAGE')
        before = evidence.strict(files[crashed[0]['pending_before']['path']]); after = evidence.strict(files[name])
        demand(after['revision'] == before['revision'] + 1, 'PENDING_ATOMIC_REVISION')
        key = 'unresolved-resume-' + SESSION_SHA
        demand(after['observations'][key]['version'] == before['observations'][key]['version'] + 1, 'PENDING_ATOMIC_DELIVERY_VERSION')
        reduced = copy.deepcopy(after); reduced['revision'] = before['revision']; reduced['observations'][key]['version'] = before['observations'][key]['version']
        demand(reduced == before, 'PENDING_ATOMIC_UNRELATED_FIELD')
        resumed = next(row for row in rows[crashed[0]['number']:] if row['command'][-1] == 'resume' and row['exit'] == 0)
        demand(files[resumed['pending_after']['path']] == files[name], 'PENDING_ATOMIC_SUCCESSOR_BYTES')
        alias = PENDING.rsplit('/', 1)[0] + '/<BEFORE_REPLACE_ATOMIC_CANDIDATE>'
        changed[alias] = changed.pop(name); namespace[alias] = namespace.pop(name)
    demand(set(changed) == {name for name, row in namespace.items() if row['kind'] == 'FILE'}, 'PENDING_NORMALIZED_NAMESPACE')
    return {'namespace': namespace, 'files': changed}, {'processes': len(rows), 'preimages': len(preimages),
            'raw_diagnostic_seconds': durations, 'retained_files': len(files), 'atomic_candidate_roles': len(candidates),
            'scope': 'FUNCTIONAL_DECLARED_ARTIFACT_RELATION_NO_PHYSICAL_OR_NATIVE_AUTHORITY'}
