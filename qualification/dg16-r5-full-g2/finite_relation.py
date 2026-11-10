#!/usr/bin/env python3
"""PROPOSED, non-authoritative relation for the observed complete C4/C5 verifier pair.

This does not alter Q.compare, accept a governor receipt, or grant live currentness.
Inputs are received by the maintained owners, then compared by a closed finite
relation. Only complete 49-portal/19-repro histories are supported. See the JSON
proposal and RERUN.md for the relation's deliberately limited acceptance status.
"""
import argparse
import base64
import collections
import copy
import datetime
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import sys
import time
sys.dont_write_bytecode = True

PINS = {
    'qualify-work-graph-verifier.py': '8cc8342f025866ffaf8c98cc1dd33d7576416c2de39e9d444b9acfd546685a0b',
    'portal-event-capture.py': '998c44341180efdf34518f37fbfe39581c91b403bcc8d78e459b138dfcbeb38c',
    'repro-event-capture.py': 'e1e40d28121f648ab1742ecc169d70e4a1f54054419225a12a696d3ac14f0d08',
}
PROFILE = 'PROPOSED_DG16_FINITE_49_PORTAL_19_REPRO_RELATION_20261104_V1'
PORTAL_FIELDS = set('after_stamps artifact capture_status consumed_generation exit expected_exit generation input_stamps invocation operation ordinal previous_event_sha256 runtime schema source_after status stderr stdout timed_out'.split())
INVOCATION_FIELDS = set('operation ordinal node run_id cwd source_root script argv process_argv artifact_path source_context lineage request_sha256 sources'.split())
PROC_FIELDS = set('pid ppid namespace_pid start_ticks uid'.split())
STAT_FIELDS = set('device inode mode links size mtime_ns ctime_ns'.split())
REPRO_FIELDS = set('argv capture_errors clone_after clone_before cwd end_monotonic_ns environment_projection environment_sha256 event_id executable_after executable_before exit_code generation_id index inputs_after inputs_before outputs_after outputs_before profile role run_id schema source_after source_before source_sha256 start_monotonic_ns stderr stdin stdout'.split())
REPRO_PROCESS_FIELDS = set('argv capture_errors cwd dispatch end_monotonic_ns environment_projection environment_sha256 event_id exit_code index profile role run_id schema source_sha256 start_monotonic_ns stderr_base64 stdin stdout_base64'.split())
WHOLE_FIELDS = set('actual_argv after authority before child_environment command command_stream dist_namespace elapsed_ms engine_binding environment environment_after execution_context exit graph_digest mapped_nodes mode node_trace nodes portal_events registered_tests registration_complete registry_sha256 repro_artifacts repro_events schema stderr_sha256 stdin stdout_sha256'.split())

class Refusal(ValueError):
    pass

def demand(condition, message):
    if not condition:
        raise Refusal(message)

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def canonical(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True, allow_nan=False) + '\n').encode()

def strict(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            demand(key not in result, 'duplicate JSON key: ' + key)
            result[key] = value
        return result
    return json.loads(raw, object_pairs_hook=pairs, parse_constant=lambda x: (_ for _ in ()).throw(Refusal('non-finite JSON')))

def desc(raw):
    return {'bytes': len(raw), 'sha256': sha(raw)}

def load_owners(source):
    source = Path(source).resolve(strict=True)
    for name, expected in PINS.items():
        actual = sha((source / 'scripts' / name).read_bytes())
        demand(actual == expected, f'owner pin mismatch: scripts/{name}: expected {expected}, actual {actual}')
    path = source / 'scripts/qualify-work-graph-verifier.py'
    spec = importlib.util.spec_from_file_location('dg16_advisory_owner_' + str(id(source)), path)
    q = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(q)
    return {'Q': q, 'P': q.portal_engine(), 'E': q.repro_event_engine(), 'source': str(source), 'pins': dict(PINS)}

def load_capsule(directory, owners):
    directory = Path(directory).resolve(strict=True)
    q, p, e = owners['Q'], owners['P'], owners['E']
    initial = q.retained_bytes(directory, 'result.json')[0]
    result = q.WG.decode_strict_json_bytes(initial, 'result.json')
    mapping = q.WG.decode_strict_json_bytes(q.retained_bytes(directory, 'mapping.json')[0], 'mapping.json')
    demand(result.get('schema') == 'implementaudit.verifier-run.v4' and result.get('exit') == 0,
           'proposal supports only successful complete verifier v4 records')
    # Run the actual maintained reader. A relocated retained capsule does not
    # authorize its declared original cwd. Keep that refusal visible. Before
    # this exact guard, Q has validated result/mapping/argv/trace/streams/stdin,
    # retained release artifacts, and both retained dist inventories.
    whole_status = 'MAINTAINED_WHOLE_RECEIVING_PASS'
    try:
        q.verified_record(directory)
    except Exception as exc:
        demand(str(exc) == 'retained dist integrity valid; current source context unavailable',
               'maintained whole receiving refusal: ' + str(exc))
        whole_status = 'RETAINED_CHECKS_PASS_THROUGH_DIST; LIVE_SOURCE_CONTEXT_UNAVAILABLE'
    # These calls are needed on the relocated branch and intentionally repeated
    # on the whole-pass branch: both finite owners receive all raw populations.
    q.verify_portal_record(directory, result, mapping)
    q.verify_repro_event_record(directory, result, mapping)
    demand(result['portal_events']['complete'] is True and
           result['repro_events']['record']['assessment'] == {'complete': True, 'issues': []},
           'finite owner completion missing')
    # Acquire each compared value once and bind those exact bytes transitively
    # to the result envelope just received above. A second unbound JSON read
    # after validation would let a writer replace accepted event/process bytes.
    def bound_bytes(path, expected, read):
        raw, observed = read(path)
        for key in ('bytes', 'sha256', 'mode'):
            if key in expected:
                actual = observed.get(key) if key == 'mode' else desc(raw)[key]
                demand(actual == expected[key], 'post-validation bound bytes differ: ' + str(path) + ':' + key)
        return raw
    def portal_json(path, expected=None, expected_value=None):
        raw = bound_bytes(path, dict({'mode': 0o600}, **(expected or {})), p.read)
        value = p.strict_json(raw)
        if expected_value is not None:
            demand(value == expected_value, 'post-validation portal declaration differs: ' + str(path))
        return value
    def repro_json(path, expected=None, expected_value=None):
        raw = bound_bytes(path, dict({'mode': 0o600}, **(expected or {})),
                          lambda target: e.read_regular(target, e.MAX_JSON))
        value = strict(raw)
        if expected_value is not None:
            demand(value == expected_value, 'post-validation repro declaration differs: ' + str(path))
        return value
    portal_path = directory / 'portal-events'
    portal = [portal_json(portal_path / f'event-{i:04d}/event.json',
                          {'sha256': result['portal_events']['events'][f'event-{i:04d}']}) for i in range(49)]
    portal_files, portal_stdout, portal_stderr = [], [], []
    for i, event in enumerate(portal):
        target = portal_path / f'event-{i:04d}'
        files = {}
        if event['artifact'] is not None:
            for name, member in event['artifact'].items():
                if member['kind'] == 'FILE':
                    files[name] = bound_bytes(target / 'artifact' / name, member, p.read)
        portal_files.append(files)
        portal_stdout.append(bound_bytes(target / 'stdout.log', event['stdout'], p.read))
        portal_stderr.append(bound_bytes(target / 'stderr.log', event['stderr'], p.read))
    aux = {'request': portal_json(portal_path / 'request.json', expected_value=result['portal_events']['request'])}
    for name in ('node', 'fixture', 'nested', 'node-return'):
        aux[name] = portal_json(portal_path / (name + '.json'), result['portal_events']['records'][name + '.json'])
    repro_path = directory / 'repro-events'
    record = repro_json(repro_path / 'record.json', expected_value=result['repro_events']['record'])
    session = repro_json(repro_path / 'session.json', {'sha256': record['session_sha256']})
    close = repro_json(repro_path / 'close.json', {'sha256': record['close_sha256']})
    reader = e.Readback(repro_path)
    events, processes = [], []
    for key, prefix, target in (('events', 'events', events), ('process_results', 'processes', processes)):
        demand(len(record[key]) == 19, 'post-validation repro population differs')
        for i, descriptor in enumerate(record[key]):
            name = f'{prefix}/{i:02d}.json'
            demand(descriptor['path'] == name, 'post-validation repro descriptor order differs')
            target.append(repro_json(repro_path / name, descriptor))
    blob_data = {}
    def blobs(value):
        if isinstance(value, dict):
            if set(value) == {'bytes', 'sha256'}:
                name = value['sha256']
                if (repro_path / 'blobs' / name).is_file():
                    blob_data[name] = reader.blob(value)
            for child in value.values(): blobs(child)
        elif isinstance(value, list):
            for child in value: blobs(child)
    for value in [session, close, *events]: blobs(value)
    rsout = [reader.blob(event['stdout']) for event in events]
    rserr = [reader.blob(event['stderr']) for event in events]
    outer_files = {}
    def outer_read(path):
        return q.retained_bytes(path.parent, path.name)
    outer_files['stdin.bin'] = bound_bytes(directory / 'stdin.bin',
        dict(desc(b'') if result['stdin']['bytes'] == 0 else
             {key: result['stdin'][key] for key in ('bytes','sha256')}, mode=result['stdin']['retained_mode']), outer_read)
    for name, key in (('child-environment.json','child_environment'), ('stdin.json','stdin'),
                      ('dist-namespace.json','dist_namespace'), ('repro-artifacts.json','repro_artifacts')):
        raw = outer_read(directory / name)[0]
        demand(raw == q.WG.canonical_json_v1(result[key]) + b'\n', 'post-validation outer declaration differs: ' + name)
        outer_files[name] = raw
    for phase in ('dist-before', 'dist-after'):
        for name, member in result['dist_namespace']['before' if phase == 'dist-before' else 'after']['entries'].items():
            if member['kind'] == 'FILE':
                outer_files[phase + '/' + name] = bound_bytes(directory / phase / name, member, outer_read)
    for member in result['repro_artifacts']['files'].values():
        if member['observation']['kind'] == 'FILE':
            name = member['relative_path']
            outer_files[name] = bound_bytes(directory / name, member['observation'], outer_read)
    commands = bound_bytes(directory / 'commands.bin', result['command_stream'], outer_read)
    registry = b''.join(n['source'].encode() for n in mapping['nodes'])
    demand(commands == q.WG.verifier_command_stream_v1(mapping, registry) and
           result['graph_digest'] == mapping['digest'] and result['registry_sha256'] == mapping['registry_sha256'],
           'post-validation mapping or command stream differs')
    trace = bound_bytes(directory / 'nodes.tsv', result['node_trace'], outer_read) if result['mode'] == 'dag' else None
    stdout = bound_bytes(directory / 'stdout.log', {'sha256': result['stdout_sha256']}, outer_read)
    stderr = bound_bytes(directory / 'stderr.log', {'sha256': result['stderr_sha256']}, outer_read)
    demand(q.retained_bytes(directory, 'result.json')[0] == initial, 'result changed during advisory receiving')
    return dict(directory=str(directory), result=result, mapping=mapping,
                commands=commands, trace=trace, stdout=stdout, stderr=stderr,
                portal=portal, portal_aux=aux, portal_files=portal_files, portal_stdout=portal_stdout, portal_stderr=portal_stderr,
                repro_events=events, repro_processes=processes, repro_session=session, repro_close=close, repro_record=record,
                repro_stdout=rsout, repro_stderr=rserr, repro_blobs=blob_data, outer_files=outer_files,
                receiving={'whole': whole_status, 'portal': 'MAINTAINED_COMPLETE_49_PASS',
                           'repro': 'MAINTAINED_COMPLETE_19_PASS', 'semantics': 'IMPORTED_DECLARED_CONSISTENCY_ONLY',
                           'compared_input_binding': 'EXACT_TRANSITIVE_RESULT_ENVELOPE_BYTES',
                           'result_sha256': sha(initial), 'source_owner_pins': owners['pins']})

TIME_TOKEN = re.compile(rb'("generated_at"\s*:\s*)("(?:[^"\\]|\\.)*")')

def replace_metadata_time_for_test(raw, text):
    return TIME_TOKEN.sub(lambda m: m.group(1) + json.dumps(text).encode(), raw, count=1)

def metadata_time(raw):
    matches = list(TIME_TOKEN.finditer(raw))
    if not matches:
        return raw
    demand(len(matches) == 1, 'metadata generated_at must occur once')
    value = strict(raw)
    demand(type(value) is dict and type(value.get('generated_at')) is str, 'metadata timestamp shape differs')
    match = matches[0]
    demand(json.loads(match.group(2)) == value['generated_at'], 'metadata timestamp is not the top-level value')
    text = value['generated_at']
    demand(re.fullmatch(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,9})?(?:Z|[+-]\d{2}:\d{2})', text) is not None,
           'metadata generated_at is not a complete timezone-aware timestamp')
    parsed = datetime.datetime.fromisoformat(text.replace('Z', '+00:00'))
    demand(parsed.tzinfo is not None, 'metadata timestamp is timezone-naive')
    return raw[:match.start(2)] + b'"<PROPOSED_GENERATION_TIMESTAMP>"' + raw[match.end(2):]

class Normalizer:
    def __init__(self, capsule, owners):
        self.c, self.p, self.e = capsule, owners['P'], owners['E']
        self.counts = collections.Counter()
        self.portal_aliases = {}
        self.repro_aliases = {}
        self.pids, self.proc_rows, self.external_parents = {}, {}, {}
        self.portal_run = capsule['portal_aux']['request']['run_id']
        self.repro_run = capsule['repro_session']['run_id']
        self.portal_generations = {self.portal_run + f':event-{i:04d}': f'<PORTAL_GENERATION_{i:04d}>' for i in range(49)}
        session = capsule['repro_session']
        root = Path(session['context']['work_root'])
        self.rroot = root
        self.repro_ids = {}
        for i, row in enumerate(self.e.profile(session)):
            self.repro_ids[self.repro_run + ':' + f'{i:02d}' + ':' + row['role']] = '<REPRO_EVENT_' + f'{i:02d}' + ':' + row['role'] + '>'
            if row['outputs']:
                self.repro_ids[self.repro_run + ':' + f'{i:02d}' + ':' + row['role'] + ':outputs'] = '<REPRO_EVENT_' + f'{i:02d}' + ':' + row['role'] + ':outputs>'
            for value in row['argv'] + row['inputs'] + row['outputs']:
                if type(value) is str and Path(value).is_absolute() and root in Path(value).parents:
                    self.repro_aliases[value] = '<REPRO_ROOT>/' + Path(value).relative_to(root).as_posix()
        self.repro_aliases[str(root)] = '<REPRO_ROOT>'
        for lane in 'ab':
            for name in ('checkout-' + lane, 'out-' + lane):
                self.repro_aliases[str(root / name)] = '<REPRO_ROOT>/' + name
            for script in (self.e.BUILD, self.e.CHECKSUM):
                value = root / ('checkout-' + lane) / script
                self.repro_aliases[str(value)] = '<REPRO_ROOT>/' + value.relative_to(root).as_posix()
        aux = capsule['portal_aux']
        tmp = Path(aux['node']['temporary_root'])
        fixture = tmp / 'portal-release-identity'
        self.portal_aliases[str(tmp)] = '<PORTAL_TEMP>'
        self.portal_aliases[str(fixture)] = '<PORTAL_FIXTURE>'
        for name in self.p.SOURCES[:2]:
            self.portal_aliases[str(fixture / name)] = '<PORTAL_FIXTURE>/' + name
        self.portal_aliases[str(fixture / 'dist/docs-portal')] = '<PORTAL_FIXTURE>/dist/docs-portal'
        for slot in self.p.profile():
            if slot['context'] == 'CANONICAL' and slot['target'] != '.':
                self.portal_aliases[str(tmp / slot['target'])] = '<PORTAL_TEMP>/' + slot['target']
        self.portal_aliases[aux['nested']['path']] = '<PORTAL_NESTED>/docs-portal'
        self.collect_processes(aux)
        self.collect_processes(capsule['portal'])

    def mark(self, rule, value):
        self.counts[rule] += 1
        return value

    def collect_processes(self, value):
        if type(value) is dict:
            if set(value) == PROC_FIELDS:
                self.p.validate_process(value)
                pid = value['pid']
                if pid in self.proc_rows:
                    demand(value == self.proc_rows[pid], 'one portal PID has conflicting declared identity')
                else:
                    self.proc_rows[pid] = value
                    self.pids[pid] = '<PORTAL_PROCESS_' + str(len(self.pids)) + '>'
            for child in value.values(): self.collect_processes(child)
        elif type(value) is list:
            for child in value: self.collect_processes(child)

    def process(self, value):
        pid, parent = value['pid'], value['ppid']
        if parent not in self.pids and parent not in self.external_parents:
            self.external_parents[parent] = '<PORTAL_EXTERNAL_PARENT_' + str(len(self.external_parents)) + '>'
        return self.mark('portal_process_identity_with_reference_graph', dict(
            pid=self.pids[pid], ppid=self.pids.get(parent, self.external_parents.get(parent)),
            namespace_pid=self.pids[pid], start_ticks='<PROCESS_START_TICKS>', uid=value['uid']))

    def portal_walk(self, value, path=()):
        if type(value) is dict:
            if set(value) == PROC_FIELDS:
                return self.process(value)
            return {key: self.portal_walk(child, path + (key,)) for key, child in value.items()}
        if type(value) is list:
            if len(path) == 2 and path[0] in ('input_stamps', 'after_stamps'):
                demand(len(value) == 6 and all(type(x) is int and x >= 0 for x in value), 'invalid physical portal stamp')
                return [self.mark('portal_physical_identity', '<DEV>'), self.mark('portal_physical_identity', '<INODE>'),
                        value[2], value[3], self.mark('portal_physical_time', '<MTIME>'), self.mark('portal_physical_time', '<CTIME>')]
            return [self.portal_walk(child, path + (i,)) for i, child in enumerate(value)]
        if type(value) is str:
            if value in self.portal_aliases:
                return self.mark('portal_exact_allocation_operand', self.portal_aliases[value])
            if path and path[-1] == 'run_id':
                demand(value == self.portal_run, 'foreign portal run identity')
                return self.mark('portal_run_identity', '<PORTAL_RUN>')
            if path and path[-1] in ('generation', 'consumed_generation'):
                demand(value in self.portal_generations, 'foreign portal generation')
                return self.mark('portal_generation_reference', self.portal_generations[value])
        return value

    def portal_stream(self, raw, event, stream):
        if stream != 'stdout' or event['operation'] != 'BUILD' or event['exit'] != 0:
            return raw
        operand = event['invocation']['artifact_path']
        if operand not in self.portal_aliases:
            return raw
        line = ('build-docs-portal: wrote ' + operand + '\n').encode()
        demand(raw.startswith(line) and raw.count(line) == 1, 'portal successful build progress line differs')
        self.counts['portal_exact_stdout_progress_operand'] += 1
        return ('build-docs-portal: wrote ' + self.portal_aliases[operand] + '\n').encode() + raw[len(line):]

    def portal_projection(self):
        c, aux = self.c, self.c['portal_aux']
        demand(len(c['portal']) == len(c['portal_files']) == len(c['portal_stdout']) == len(c['portal_stderr']) == 49, 'portal population must be exactly 49')
        demand(aux['request']['plan'] == self.p.profile(), 'portal finite plan differs')
        events, files, streams = [], [], []
        previous = None
        seen = []
        for i, original in enumerate(c['portal']):
            demand(set(original) == PORTAL_FIELDS and set(original['invocation']) == INVOCATION_FIELDS, 'unknown portal event/invocation field')
            inv, slot = original['invocation'], self.p.profile()[i]
            demand(original['ordinal'] == inv['ordinal'] == i and original['operation'] == inv['operation'] == slot['operation'], 'portal order/operation differs')
            demand(original['exit'] == original['expected_exit'] == slot['exit'] and original['capture_status'] == 'COMPLETE' and original['timed_out'] is False, 'portal exit/completion differs')
            demand(original['previous_event_sha256'] == previous and inv['request_sha256'] == sha(self.p.encode(aux['request'])), 'portal hash-chain or request binding differs')
            demand(original['input_stamps'] == original['after_stamps'], 'portal physical currentness window changed')
            demand(original['source_after'] == inv['source_context'], 'portal source currentness changed')
            self.p.validate_lineage(inv['lineage'], aux['node']['owner'])
            self.p.validate_runtime_observation(original['runtime'], inv['lineage'][0])
            generation = self.portal_run + f':event-{i:04d}' if original['operation'] == 'BUILD' and original['exit'] == 0 else None
            demand(original['generation'] == generation, 'portal generation identity changed')
            consumed = None
            if original['operation'] == 'CHECK':
                for old in reversed(seen):
                    if old['operation'] == 'BUILD' and old['exit'] == 0 and old['invocation']['artifact_path'] == inv['artifact_path']:
                        if old['artifact'] == original['artifact'] and old['invocation']['source_root'] == inv['source_root']:
                            consumed = old['generation']
                        break
            demand(original['consumed_generation'] == consumed, 'portal consumed-generation relation differs')
            row = copy.deepcopy(original)
            file_projection = {}
            expected_files = {name for name, member in (row['artifact'] or {}).items() if member['kind'] == 'FILE'}
            demand(set(c['portal_files'][i]) == expected_files, 'portal artifact file population differs')
            for name, raw in c['portal_files'][i].items():
                member = row['artifact'][name]
                demand(member['bytes'] == len(raw) and member['sha256'] == sha(raw), 'portal artifact descriptor differs: ' + name)
                normalized = metadata_time(raw) if name == 'docs-metadata.json' else raw
                if normalized != raw: self.counts['portal_docs_metadata_generated_at_only'] += 1
                file_projection[name] = desc(normalized)
                member.update(desc(normalized))
            stream_projection = {}
            for stream in ('stdout', 'stderr'):
                raw = c['portal_' + stream][i]
                demand(row[stream]['bytes'] == len(raw) and row[stream]['sha256'] == sha(raw), 'portal stream descriptor differs')
                normalized = self.portal_stream(raw, original, stream)
                row[stream].update(desc(normalized))
                stream_projection[stream] = normalized
            if previous is not None:
                row['previous_event_sha256'] = self.mark('portal_derived_previous_event_digest', f'<PREVIOUS_EVENT_{i-1:04d}>')
            row['invocation']['request_sha256'] = self.mark('portal_derived_request_digest', '<PORTAL_REQUEST_DIGEST>')
            events.append(self.portal_walk(row))
            files.append(file_projection)
            streams.append(stream_projection)
            previous = sha(self.p.encode(original))
            seen.append(original)
        return {'records': self.portal_walk(aux), 'events': events, 'files': files, 'streams': streams}

    def repro_walk(self, value, path=()):
        if type(value) is dict:
            if path and path[-1] == 'stat' and set(value) == STAT_FIELDS:
                result = dict(value)
                for key in ('device', 'inode', 'mtime_ns', 'ctime_ns'):
                    demand(type(value[key]) is int and value[key] >= 0, 'invalid repro physical field')
                    result[key] = self.mark('repro_physical_identity_or_time', '<' + key.upper() + '>')
                return result
            return {key: self.repro_walk(child, path + (key,)) for key, child in value.items()}
        if type(value) is list:
            return [self.repro_walk(child, path + (i,)) for i, child in enumerate(value)]
        if path and path[-1] in ('start_monotonic_ns', 'end_monotonic_ns'):
            demand(type(value) is int and value >= 0, 'invalid monotonic timestamp')
            return self.mark('repro_monotonic_time', '<' + path[-1].upper() + '>')
        if type(value) is str:
            if value in self.repro_aliases:
                return self.mark('repro_exact_allocation_operand', self.repro_aliases[value])
            if path and path[-1] == 'run_id':
                demand(value == self.repro_run, 'foreign repro run identity')
                return self.mark('repro_run_identity', '<REPRO_RUN>')
            if path and path[-1] in ('event_id', 'generation_id'):
                demand(value in self.repro_ids, 'foreign repro event or generation identity: ' + value)
                return self.mark('repro_event_or_generation_reference', self.repro_ids[value])
        return value

    def repro_stream(self, raw, lane=None, whole=False):
        replacements = []
        for selected in ('ab' if whole else lane or ''):
            for label, member in [('package-contract: wrote ', self.e.MEMBERS[0]), ('package-contract: wrote ', self.e.MEMBERS[1]), ('write-release-checksums: wrote ', self.e.MEMBERS[2])]:
                operand = str(self.rroot / ('out-' + selected) / member)
                old = (label + operand + '\n').encode()
                new = (label + self.repro_aliases[operand] + '\n').encode()
                replacements.append((old, new))
        lines = raw.splitlines(keepends=True)
        for old, new in replacements:
            demand(lines.count(old) == 1, 'expected exact repro progress line absent or duplicated')
            lines[lines.index(old)] = new
            self.counts['whole_exact_stdout_progress_operand' if whole else 'repro_exact_stdout_progress_operand'] += 1
        return b''.join(lines)

    def repro_projection(self):
        c = self.c
        demand(len(c['repro_events']) == len(c['repro_processes']) == len(c['repro_stdout']) == len(c['repro_stderr']) == 19, 'repro population must be exactly 19')
        events, processes, streams = [], [], []
        profile = self.e.profile(c['repro_session'])
        for i, (original, proc, slot) in enumerate(zip(c['repro_events'], c['repro_processes'], profile)):
            demand(set(original) == REPRO_FIELDS and set(proc) == REPRO_PROCESS_FIELDS, 'unknown repro event/process field')
            demand(original['index'] == proc['index'] == i and original['role'] == proc['role'] == slot['role'], 'repro order/role differs')
            demand(original['argv'] == proc['argv'] == slot['argv'] and original['exit_code'] == proc['exit_code'] == 0, 'repro argv/exit differs')
            demand(original['source_before'] == original['source_after'] == c['repro_session']['source_custody'], 'repro source currentness differs')
            demand(original['source_sha256'] == proc['source_sha256'] == sha(canonical(c['repro_session']['source'])), 'repro source digest differs')
            demand(original['start_monotonic_ns'] <= original['end_monotonic_ns'] and proc['start_monotonic_ns'] <= proc['end_monotonic_ns'], 'repro time order differs')
            row, process = copy.deepcopy(original), copy.deepcopy(proc)
            stream_projection = {}
            for stream in ('stdout', 'stderr'):
                raw = c['repro_' + stream][i]
                demand(row[stream] == desc(raw) and base64.b64decode(process[stream + '_base64'], validate=True) == raw, 'repro stream binding differs')
                normalized = self.repro_stream(raw, lane=slot['lane']) if stream == 'stdout' and slot['role'].startswith('build:') else raw
                row[stream] = desc(normalized)
                process[stream + '_base64'] = base64.b64encode(normalized).decode('ascii')
                stream_projection[stream] = normalized
            events.append(self.repro_walk(row))
            processes.append(self.repro_walk(process))
            streams.append(stream_projection)
        record = copy.deepcopy(c['repro_record'])
        demand(record['assessment'] == {'complete': True, 'issues': []} and record['handoff_failures'] == [] and record['unhanded_blobs'] == [], 'repro incomplete or unhanded population')
        demand(record['session_sha256'] == sha(canonical(c['repro_session'])) and record['close_sha256'] == sha(canonical(c['repro_close'])), 'repro session/close descriptor differs')
        record['session_sha256'] = self.mark('repro_derived_session_digest', '<REPRO_SESSION_DIGEST>')
        record['close_sha256'] = self.mark('repro_derived_close_digest', '<REPRO_CLOSE_DIGEST>')
        for field, raw_objects, normalized in [('events', c['repro_events'], events), ('process_results', c['repro_processes'], processes)]:
            demand(len(record[field]) == 19, 'repro envelope population differs')
            for i, descriptor in enumerate(record[field]):
                raw = canonical(raw_objects[i])
                demand(descriptor['bytes'] == len(raw) and descriptor['sha256'] == sha(raw), 'repro envelope event/process binding differs')
                descriptor.update(desc(canonical(normalized[i])))
                self.counts['repro_derived_' + field + '_descriptor'] += 1
        return {'session': self.repro_walk(c['repro_session']), 'close': self.repro_walk(c['repro_close']),
                'record': self.repro_walk(record), 'events': events, 'processes': processes, 'streams': streams}

    def whole_projection(self):
        c, r = self.c, self.c['result']
        demand(set(r) == WHOLE_FIELDS, 'unknown whole result field')
        demand(r['before'] == r['after'] and r['environment'] == r['environment_after'], 'whole source/environment currentness differs')
        demand(r['exit'] == 0 and r['authority'] == 'NONE', 'whole completion/authority differs')
        demand(r['mapped_nodes'] == 6 and r['registered_tests'] == 2 and r['registration_complete'] is False,
               'proposal is limited to the six-node/two-test finite registry, with canonical registration incomplete')
        demand(r['stdout_sha256'] == sha(c['stdout']) and r['stderr_sha256'] == sha(c['stderr']), 'whole stream binding differs')
        demand(r['environment'] == c['mapping']['environment'], 'whole environment/mapping differs')
        names = [node['id'] for node in c['mapping']['nodes']]
        mode = r['mode']
        demand(mode in ('legacy', 'dag'), 'whole mode differs')
        expected = ['bash', 'scripts/verify-package.sh' if mode == 'legacy' else 'scripts/run-work-graph-verifier.sh']
        demand(r['command'] == expected, 'whole route command differs')
        if mode == 'dag':
            expected += [r['execution_context']['output'] + '/commands.bin', r['execution_context']['output'] + '/nodes.tsv', str(len(names)), r['command_stream']['sha256']]
        demand(r['actual_argv'] == expected, 'whole actual argv differs')
        demand(r['nodes'] == self.c['_owners_q'].trace_nodes(c['mapping'], mode, r['exit'], c['trace']), 'whole ordered trace differs')
        stdout = self.repro_stream(c['stdout'], whole=True)
        value = copy.deepcopy(r)
        # These are interpreted by exact per-route predicates above, not ignored.
        for field in ('mode', 'command', 'actual_argv', 'nodes', 'node_trace'):
            value[field] = self.mark('whole_defined_legacy_dag_route_relation', '<VERIFIED_ROUTE_' + field.upper() + '>')
        demand(type(value['elapsed_ms']) is int and value['elapsed_ms'] >= 0, 'whole elapsed time differs')
        value['elapsed_ms'] = self.mark('whole_independent_elapsed_time', '<ELAPSED_MS>')
        value['stdout_sha256'] = sha(stdout)
        # All nested source objects are separately received and compared below;
        # envelope hashes are dependent bindings, not independently equal bytes.
        value['portal_events'] = '<SEPARATELY_RECEIVED_COMPLETE_PORTAL_RELATION>'
        value['repro_events'] = '<SEPARATELY_RECEIVED_COMPLETE_REPRO_RELATION>'
        return {'result': value, 'mapping': c['mapping'], 'commands': c['commands'],
                'stdout': stdout, 'stderr': c['stderr'], 'retained_outer_files': c['outer_files']}

    def all(self):
        return {'whole': self.whole_projection(), 'portal': self.portal_projection(), 'repro': self.repro_projection()}


def differences(left, right, path=''):
    if type(left) is not type(right):
        return [{'path': path, 'reason': 'type', 'left': type(left).__name__, 'right': type(right).__name__}]
    if isinstance(left, dict):
        rows = []
        if set(left) != set(right):
            rows.append({'path': path, 'reason': 'member_population', 'left_only': sorted(set(left)-set(right)), 'right_only': sorted(set(right)-set(left))})
        for key in sorted(set(left) & set(right)):
            rows.extend(differences(left[key], right[key], path + '/' + str(key)))
        return rows
    if isinstance(left, list):
        rows = [] if len(left) == len(right) else [{'path': path, 'reason': 'length', 'left': len(left), 'right': len(right)}]
        for i, (a, b) in enumerate(zip(left, right)): rows.extend(differences(a, b, path + '/' + str(i)))
        return rows
    if left == right:
        return []
    if isinstance(left, bytes):
        return [{'path': path, 'reason': 'raw_bytes_outside_relation', 'left': desc(left), 'right': desc(right)}]
    return [{'path': path, 'reason': 'value_outside_relation', 'left': left, 'right': right}]


def raw_checks(a, b):
    x, y = a['result'], b['result']
    checks = dict(same_source=x['before'] == y['before'] == x['after'] == y['after'],
        same_registry=x['registry_sha256'] == y['registry_sha256'],
        same_environment=x['environment'] == x['environment_after'] == y['environment'] == y['environment_after'],
        same_record_schema=x['schema'] == y['schema'], same_exit=x['exit'] == y['exit'],
        same_stdout=a['stdout'] == b['stdout'], same_stderr=a['stderr'] == b['stderr'],
        route_pair={x['mode'], y['mode']} == {'legacy', 'dag'},
        same_engine=x['engine_binding'] == y['engine_binding'],
        same_execution_cwd=x['execution_context']['cwd'] == y['execution_context']['cwd'],
        same_compiled_stream=a['commands'] == b['commands'],
        same_child_environment=x['child_environment'] == y['child_environment'],
        same_declared_repro_artifacts=x['repro_artifacts'] == y['repro_artifacts'] and all(
            a['outer_files'][m['relative_path']] == b['outer_files'][m['relative_path']]
            for m in x['repro_artifacts']['files'].values() if m['observation']['kind'] == 'FILE'),
        same_stdin=x['stdin'] == y['stdin'] and a['outer_files']['stdin.bin'] == b['outer_files']['stdin.bin'],
        same_dist_namespace=x['dist_namespace'] == y['dist_namespace'] and x['dist_namespace']['before'] == x['dist_namespace']['after'] and all(
            a['outer_files'][name] == b['outer_files'][name] for name in a['outer_files'] if name.startswith(('dist-before/', 'dist-after/'))),
        same_portal_events=x['portal_events'] == y['portal_events'], same_repro_events=x['repro_events'] == y['repro_events'])
    return checks

def compare_capsules(left, right, owners):
    demand({left['result']['mode'], right['result']['mode']} == {'legacy', 'dag'}, 'one legacy and one DAG capsule required')
    # The module pointer is a trusted explicitly supplied code dependency, not
    # anything loaded from a capsule. It is excluded from output/digests.
    left['_owners_q'] = owners['Q']
    right['_owners_q'] = owners['Q']
    try:
        na, nb = Normalizer(left, owners), Normalizer(right, owners)
        a, b = na.all(), nb.all()
    finally:
        left.pop('_owners_q', None); right.pop('_owners_q', None)
    rows = differences(a, b)
    raw = raw_checks(left, right)
    return dict(schema='dg16.r4.proposed-finite-correspondence.v1', profile=PROFILE,
        acceptance='PROPOSED_NOT_ACCEPTED', authority='NONE', original_acceptance_delta=0,
        proposed_equivalent=not rows, unexplained_differences=rows,
        approved_difference_counts={'meaning': 'structural substitutions per input; raw differences remain retained',
                                    'left': dict(na.counts), 'right': dict(nb.counts)},
        raw_checks=raw, raw_check_count=len(raw), raw_true_count=sum(raw.values()), raw_observables_equal=all(raw.values()),
        population={'portal_invocations_per_route': 49, 'repro_invocations_per_route': 19,
                    'mapped_registry_nodes': left['result']['mapped_nodes'], 'registered_tests': left['result']['registered_tests'],
                    'canonical_registration_complete': left['result']['registration_complete'],
                    'source_commit': left['result']['before']['head'], 'source_tree': left['result']['before']['tree'],
                    'registry_sha256': left['result']['registry_sha256'], 'scope': 'EXACT_RETAINED_FINITE_REGISTRY; NOT_FULL_CANONICAL_POPULATION'},
        receiving=[left['receiving'], right['receiving']],
        limitations=['No original acceptance or retirement authority.',
                     'No namespace, allocation, startup trust, or current live-source admission is created.',
                     'Existing FINITE_C5_ROLE_CORRESPONDENCE_V1 requires absent prospective allocation receipts for these capsules.',
                     'Original V03 depends on accepted normalization and complete mapped population; this relation is a proposal only.'])

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', required=True, type=Path)
    parser.add_argument('--left', required=True, type=Path)
    parser.add_argument('--right', required=True, type=Path)
    parser.add_argument('--out', required=True, type=Path)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    started = time.monotonic_ns()
    try:
        owners = load_owners(args.source)
        left, right = load_capsule(args.left, owners), load_capsule(args.right, owners)
        result = compare_capsules(left, right, owners)
        result['status'] = 'EVALUATED'
        code = 0 if result['proposed_equivalent'] else 1
    except Exception as exc:
        result = {'schema': 'dg16.r4.proposed-finite-correspondence.v1', 'profile': PROFILE,
                  'status': 'REFUSED', 'acceptance': 'PROPOSED_NOT_ACCEPTED', 'authority': 'NONE',
                  'original_acceptance_delta': 0, 'type': type(exc).__name__, 'message': str(exc)}
        code = 2
    result['elapsed_ns'] = time.monotonic_ns() - started
    (args.out / 'RESULT.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps({key: result[key] for key in ('status', 'proposed_equivalent', 'raw_true_count', 'raw_check_count', 'message') if key in result}, sort_keys=True))
    return code

if __name__ == '__main__':
    raise SystemExit(main())
