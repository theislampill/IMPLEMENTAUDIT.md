"""Full registered-operation correspondence and same-job raw evidence receiving.

The finite component reader stays byte-identical. This module explicitly owns
the separately proposed full applicability and the named additional field
relations. It supplies evidence to a live independent review/root consumption;
it cannot award G2, currentness, canonical conversion, retirement, or authority.
"""
import copy
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess


class Refusal(ValueError):
    pass


def demand(value, code):
    if not value:
        raise Refusal(code)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def desc(raw):
    return {'bytes': len(raw), 'sha256': sha(raw)}


def encode(value):
    return (json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + '\n').encode()


def stamp(info):
    return (info.st_dev, info.st_ino, info.st_mode, info.st_nlink, info.st_uid,
            info.st_gid, info.st_size, info.st_mtime_ns, info.st_ctime_ns)


MODULES = {'finite_relation.py': 'finite', 'full_output_relation.py': 'reports',
           'full_stdout.py': 'stdout', 'full_evidence.py': 'evidence', 'pending_relation.py': 'pending'}
DATA = {'REPORT_SLOTS.json': 'slots', 'OUTPUT_ROLES.json': 'roles', 'SOURCE_MANIFEST.json': 'source'}
SCOPES = ('whole', 'portal', 'repro', 'pending_durability', 'pending_loader')
RUNTIME_SHA = '51780085229bd3547a2751e8d75ab1d8f391dd2c9c3ca1d011b54529348faeb4'
REGISTRY_SHA = '65c7b6939c7bf9396f83cdad58c735cabbc7e28232ceff816e7a8909bf625878'
COMMAND_SHA = '50a794c866dd2b35cf5f10875c409a8e2347ea13f9ea3fb188582fca7dc6fc28'


def load(directory, inputs, module_loader, read_json):
    demand(set(inputs) == {'schema', 'source_commit', 'source_tree', 'files'} and
           inputs['schema'] == 'dg16.full-relation-inputs.v1' and set(inputs['files']) == set(MODULES) | set(DATA),
           'RELATION_INPUT_POPULATION')
    result = {}
    for name, key in {**MODULES, **DATA}.items():
        path = directory / name
        before = path.lstat()
        demand(stat.S_ISREG(before.st_mode) and before.st_nlink == 1 and 0 < before.st_size <= 1024**2, 'RELATION_INPUT_BOUND')
        raw = path.read_bytes()
        demand(stamp(before) == stamp(path.lstat()) and desc(raw) == inputs['files'][name], 'RELATION_INPUT_CHANGED')
        # Interpret exactly the acquired, hash-bound bytes. A second pathname
        # read could supply a different/restored profile after this fence.
        result[key] = (module_loader(name, inputs['files'][name]['sha256']) if name in MODULES
                       else result['evidence'].strict(raw))
    result['inputs'] = inputs
    demand(result['source']['commit'] == inputs['source_commit'] and result['source']['tree'] == inputs['source_tree'],
           'RELATION_SOURCE_MANIFEST')
    for key in ('slots', 'roles'):
        demand(result[key]['source_commit'] == inputs['source_commit'] and result[key]['source_tree'] == inputs['source_tree'],
               'RELATION_PROFILE_SOURCE')
    demand(result['slots']['slot_count'] == 110 and sum(row['test_count'] for row in result['slots']['slots']) == 2057 and
           result['slots']['registry_sha256'] == REGISTRY_SHA, 'RELATION_STATIC_REPORT_POPULATION')
    return result


def source_profiles(source, owner, relation):
    pins = {row['path']: row for row in relation['source']['members']}
    consumed = {}
    for profile in (relation['slots'], relation['roles']):
        for name, expected in profile.get('source_files', profile.get('source_closure')).items():
            demand(name in pins and all(expected[key] == pins[name][key] for key in ('bytes', 'sha256', 'mode')),
                   'PROFILE_FROZEN_SOURCE_PIN')
            if name in consumed: continue
            observed = owner.source_member(name, root=source, with_bytes=False, byte_limit=16*1024**2)
            demand(observed.get('kind') == 'FILE' and observed['bytes'] == expected['bytes'] and
                   observed['sha256'] == expected['sha256'] and observed['mode'] == int(expected['mode'], 8) & 0o777,
                   'PROFILE_ACTUAL_SOURCE_PIN')
            consumed[name] = {key: observed[key] for key in ('bytes', 'sha256', 'mode')}
    peers = []
    for group in ('native-runtime', 'route-graph'):
        name = 'source-peers/' + group + '/SOURCE_MANIFEST.json'
        observed = owner.source_member(name, root=source, with_bytes=True, byte_limit=1024**2)
        demand(observed.get('kind') == 'FILE' and desc(observed['_acquired_bytes']) ==
               {key: pins[name][key] for key in ('bytes', 'sha256')}, 'MATERIALIZATION_MANIFEST_SOURCE')
        peers.append(relation['evidence'].strict(observed['_acquired_bytes']))
    return {'members': consumed, 'source': relation['inputs']['source_commit']}, peers


RUNTIME_PROGRAM = r'''import hashlib,json,pathlib,stat,sys,unittest.runner
p=pathlib.Path(unittest.runner.__file__).resolve(strict=True)
s=p.lstat();stamp=lambda x:(x.st_dev,x.st_ino,x.st_mode,x.st_uid,x.st_gid,x.st_nlink,x.st_size,x.st_mtime_ns,x.st_ctime_ns)
assert stat.S_ISREG(s.st_mode) and s.st_nlink==1 and s.st_size<=131072
r=p.read_bytes();t=p.lstat();assert stamp(s)==stamp(t)
print(json.dumps(dict(path=str(p),version=sys.version.split()[0],bytes=len(r),sha256=hashlib.sha256(r).hexdigest(),physical=dict(device=s.st_dev,inode=s.st_ino,mode=s.st_mode,uid=s.st_uid,gid=s.st_gid,links=s.st_nlink,mtime_ns=s.st_mtime_ns,ctime_ns=s.st_ctime_ns)),sort_keys=True))
'''


def runtime_observation(runtime_python, owner, evidence, *, initial):
    process = subprocess.run([runtime_python, '-I', '-B', '-c', RUNTIME_PROGRAM],
                             capture_output=True, timeout=15)
    demand(len(process.stdout) <= 4096 and len(process.stderr) <= 4096, 'RUNTIME_METADATA_BOUND')
    if initial:
        owner.durable_bytes(evidence / 'RUNTIME_PROBE.stdout', process.stdout)
        owner.durable_bytes(evidence / 'RUNTIME_PROBE.stderr', process.stderr)
    demand(process.returncode == 0 and process.stderr == b'', 'RUNTIME_SOURCE_OBSERVATION_REFUSED')
    value = json.loads(process.stdout)
    demand(set(value) == {'path', 'version', 'bytes', 'sha256', 'physical'} and type(value['path']) is str and
           value['path'].startswith('/') and set(value['physical']) == {
               'device', 'inode', 'mode', 'uid', 'gid', 'links', 'mtime_ns', 'ctime_ns'}, 'RUNTIME_METADATA_SHAPE')
    if initial: owner.durable_bytes(evidence / 'RUNTIME_OBSERVED.json', encode(value))
    # Retain the actual observed hash before this cheap prospective-policy gate.
    demand(value['version'] == '3.14.4' and value['sha256'] == RUNTIME_SHA and value['bytes'] == 11383,
           'DECLARED_UNITTEST_RUNTIME_SOURCE_MISMATCH')
    member = owner.source_member(value['path'][1:], root=Path('/'), with_bytes=True, byte_limit=131072)
    raw = member.pop('_acquired_bytes')
    demand(member.get('kind') == 'FILE' and desc(raw) == {key: value[key] for key in ('bytes', 'sha256')},
           'RUNTIME_SOURCE_BYTES_CHANGED')
    info = Path(value['path']).lstat()
    actual = dict(device=info.st_dev,inode=info.st_ino,mode=info.st_mode,uid=info.st_uid,gid=info.st_gid,
                  links=info.st_nlink,mtime_ns=info.st_mtime_ns,ctime_ns=info.st_ctime_ns)
    demand(actual == value['physical'], 'RUNTIME_SOURCE_PHYSICAL_CHANGED')
    if initial: owner.durable_bytes(evidence / 'RUNTIME_RUNNER.py', raw)
    else:
        demand(owner.retained_bytes(evidence, 'RUNTIME_OBSERVED.json')[0] == encode(value) and
               owner.retained_bytes(evidence, 'RUNTIME_RUNNER.py')[0] == raw, 'RUNTIME_SOURCE_CLOSING_MISMATCH')
    return value


def typed_digest(value):
    """Domain-separated complete typed projection digest; never stringify raw blobs."""
    digest = hashlib.sha256()
    def visit(item):
        kind = type(item)
        if kind is bytes:
            digest.update(b'B' + str(len(item)).encode() + b':' + item)
        elif kind is dict:
            demand(all(type(key) is str for key in item), 'PROJECTION_KEY_TYPE')
            digest.update(b'D' + str(len(item)).encode() + b':')
            for key in sorted(item): visit(key); visit(item[key])
        elif kind is list or kind is tuple:
            digest.update(b'L' + str(len(item)).encode() + b':')
            for child in item: visit(child)
        elif kind in (str, int, float, bool) or item is None:
            raw = json.dumps(item, ensure_ascii=True, allow_nan=False, separators=(',', ':')).encode()
            digest.update(b'J' + str(len(raw)).encode() + b':' + raw)
        else: raise Refusal('PROJECTION_VALUE_TYPE')
    visit(value)
    return digest.hexdigest()


def compare(left, right):
    count, witnesses, traversed = 0, [], 0
    def visit(a, b, path):
        nonlocal count, traversed
        traversed += 1
        demand(traversed <= 1000000, 'PROJECTION_COMPARISON_BOUND')
        kind = type(a)
        if kind is type(b) and kind not in (dict,list,tuple) and a == b: return
        reason = 'TYPE' if kind is not type(b) else 'BYTES' if kind is bytes else 'VALUE'
        if kind is type(b) and kind is dict:
            if set(a) == set(b):
                for key in sorted(a): visit(a[key], b[key], path + [key])
                return
            reason = 'FIELD_POPULATION'
        elif kind is type(b) and kind in (list, tuple):
            if len(a) == len(b):
                for index, (x, y) in enumerate(zip(a, b)): visit(x, y, path + [index])
                return
            reason = 'POPULATION'
        count += 1
        if len(witnesses) < 2:
            row = {'kind': reason, 'location_sha256': sha(encode(path)),
                   'left_projection_sha256': typed_digest(a), 'right_projection_sha256': typed_digest(b)}
            if kind is type(b) and kind is bytes:
                offset = next((i for i, (x, y) in enumerate(zip(a, b)) if x != y), min(len(a), len(b)))
                row.update(first_different_offset=offset, left=desc(a), right=desc(b))
            witnesses.append(row)
    visit(left, right, [])
    return {'equal': count == 0, 'difference_count': count, 'witnesses': witnesses,
            'witnesses_complete': count <= 2, 'left_projection_sha256': typed_digest(left),
            'right_projection_sha256': typed_digest(right)}


def whole_projection(capsule, normalizer, relation, pending, owner):
    finite, result = relation['finite'], capsule['result']
    demand(set(result) == finite.WHOLE_FIELDS and result['before'] == result['after'] and
           result['environment'] == result['environment_after'] == capsule['mapping']['environment'],
           'FULL_WHOLE_FIELDS_OR_CURRENTNESS')
    demand(result['exit'] == 0 and result['authority'] == 'NONE' and result['mapped_nodes'] == 119 and
           result['registered_tests'] == 91 and result['registration_complete'] is True,
           'FULL_POPULATION_NOT_COMPLETE')
    demand(result['before']['head'] == relation['inputs']['source_commit'] and
           result['before']['tree'] == relation['inputs']['source_tree'] and result['registry_sha256'] == REGISTRY_SHA and
           sha(capsule['commands']) == COMMAND_SHA, 'FULL_WHOLE_SOURCE_OR_COMMAND')
    demand(result['stdout_sha256'] == sha(capsule['stdout']) and result['stderr_sha256'] == sha(capsule['stderr']),
           'FULL_STREAM_RAW_BINDING')
    names = [node['id'] for node in capsule['mapping']['nodes']]
    demand(len(names) == 119 and len(set(names)) == len(names), 'FULL_NODE_POPULATION')
    mode = result['mode']; demand(mode in ('legacy', 'dag'), 'FULL_ROUTE_MODE')
    expected = ['bash', 'scripts/verify-package.sh' if mode == 'legacy' else 'scripts/run-work-graph-verifier.sh']
    demand(result['command'] == expected, 'FULL_ROUTE_COMMAND')
    if mode == 'dag':
        expected += [result['execution_context']['output'] + '/commands.bin', result['execution_context']['output'] + '/nodes.tsv',
                     str(len(names)), result['command_stream']['sha256']]
    demand(result['actual_argv'] == expected and
           result['nodes'] == owner.trace_nodes(capsule['mapping'], mode, result['exit'], capsule['trace']), 'FULL_ROUTE_ACTUAL_TRACE')
    if mode == 'dag': demand(all(row['status'] == 'PASS' and row['terminal'] is True for row in result['nodes']), 'FULL_DAG_NODE_TERMINALS')
    stdout = normalizer.repro_stream(capsule['stdout'], whole=True)
    stdout, stdout_observations = relation['stdout'].normalize(stdout, relation['roles'], relation['evidence'], pending)
    stderr, report_observations = relation['reports'].report_elapsed_relation(capsule['stderr'], relation['slots'])
    projected = copy.deepcopy(result)
    for field in ('mode', 'command', 'actual_argv', 'nodes', 'node_trace'):
        projected[field] = normalizer.mark('whole_defined_legacy_dag_route_relation', '<VERIFIED_ROUTE_' + field.upper() + '>')
    demand(type(projected['elapsed_ms']) is int and projected['elapsed_ms'] >= 0, 'WHOLE_ELAPSED_DOMAIN')
    projected['elapsed_ms'] = normalizer.mark('whole_independent_elapsed_time', '<ELAPSED_MS>')
    projected['stdout_sha256'], projected['stderr_sha256'] = sha(stdout), sha(stderr)
    projected['portal_events'] = '<SEPARATELY_RECEIVED_COMPLETE_PORTAL_RELATION>'
    projected['repro_events'] = '<SEPARATELY_RECEIVED_COMPLETE_REPRO_RELATION>'
    return {'result': projected, 'mapping': capsule['mapping'], 'commands': capsule['commands'],
            'stdout': stdout, 'stderr': stderr, 'retained_outer_files': capsule['outer_files']}, {
                'report_slots': report_observations, 'stdout_roles': stdout_observations}


def receive(source, out, owner, relation, policy, captures, censuses, *, runtime_python):
    """Caller holds maintained capture-parent lock throughout this entire read."""
    evidence = out / 'evidence'
    source_fact, peers = source_profiles(source, owner, relation)
    runtime = runtime_observation(runtime_python, owner, evidence, initial=False)
    owners = {'Q': owner, 'P': owner.portal_engine(), 'E': owner.repro_event_engine(),
              'source': str(source), 'pins': relation['finite'].PINS}
    projections, private_observations, external_censuses, readbacks = {}, {}, {}, {}
    roots = set()
    for mode in ('legacy', 'dag'):
        capsule = relation['finite'].load_capsule(captures[mode], owners)
        demand(capsule['receiving']['whole'] == 'MAINTAINED_WHOLE_RECEIVING_PASS', 'RELOCATED_SOURCE_FALLBACK_FORBIDDEN')
        capsule['_owners_q'] = owner
        pending, external = relation['evidence'].receive_declared(capsule['stdout'], out / 'declared-artifacts' / mode, owner)
        for role in relation['evidence'].ROLES:
            demand(pending[role]['root'] not in roots, 'INDEPENDENT_ROUTES_SHARE_PENDING_ALLOCATION')
            roots.add(pending[role]['root'])
        aggregate = censuses[str(captures[mode])]['total_bytes'] + external['bytes']
        demand(aggregate <= owner.CAPTURE_RETENTION_LIMITS['total_bytes'], 'COMBINED_ROUTE_CAPTURE_BOUND')
        norm = relation['finite'].Normalizer(capsule, owners)
        projected, observations = whole_projection(capsule, norm, relation, pending, owner)
        projections[mode] = {'whole': projected, 'portal': norm.portal_projection(), 'repro': norm.repro_projection()}
        observations['pending'] = {}
        for role in relation['evidence'].ROLES:
            projections[mode][role], observations['pending'][role] = relation['pending'].normalize(
                pending[role], role, relation['roles'], relation['source'], peers, relation['evidence'],
                source=str(source), runtime_python=runtime_python)
        observations['finite_rule_counts'] = dict(norm.counts)
        private_observations[mode] = observations
        external_censuses[mode] = {role: {key: pending[role][key] for key in ('root', 'original_census', 'retained_census')}
                                  for role in relation['evidence'].ROLES}
        readbacks[mode] = {'whole_result': capsule['receiving']['result_sha256'], 'external': external,
                          'raw_stdout': desc(capsule['stdout']), 'raw_stderr': desc(capsule['stderr']),
                          'retained_outer_files': len(capsule['outer_files']),
                          'portal_artifact_files': sum(len(files) for files in capsule['portal_files']),
                          'repro_referenced_blobs': len(capsule['repro_blobs'])}
    compared = {scope: compare(projections['legacy'][scope], projections['dag'][scope]) for scope in SCOPES}
    demand(source_profiles(source, owner, relation)[0] == source_fact and
           runtime_observation(runtime_python, owner, evidence, initial=False) == runtime, 'RELATION_SOURCE_OR_RUNTIME_CHANGED')
    for path, census in censuses.items():
        demand(owner._capture_census(Path(path)) == census, 'FULL_CAPTURE_CHANGED_DURING_RELATION')
    for mode in ('legacy', 'dag'):
        raw_stdout = owner.retained_bytes(captures[mode], 'stdout.log')[0]
        _, external = relation['evidence'].receive_declared(raw_stdout, out / 'declared-artifacts' / mode, owner)
        demand(external == readbacks[mode]['external'], 'DECLARED_ARTIFACTS_CHANGED_DURING_RELATION')
    private = {'schema': 'dg16.full-correspondence-private-observations.v1', 'source_profiles': source_fact,
               'runtime': runtime, 'routes': private_observations, 'raw_readbacks': readbacks,
               'captures': censuses, 'declared_artifacts': external_censuses}
    demand(len(encode(private)) <= 16*1024**2, 'PRIVATE_RELATION_METADATA_BOUND')
    owner.durable_bytes(evidence / 'FULL_RELATION_PRIVATE.json', encode(private))
    proof = {'schema': 'dg16.full-correspondence-proof.v1', 'authority': 'NONE',
             'scope': 'FULL_CANONICAL_REGISTERED_OPERATION_AND_DECLARED_TRANSITIVE_OUTPUTS',
             'source_commit': relation['inputs']['source_commit'], 'source_tree': relation['inputs']['source_tree'],
             'policy_sha256': sha(encode(policy)), 'receiver_inputs_sha256': sha(encode(relation['inputs'])),
             'private_observations': desc(encode(private)),
             'registry_sha256': REGISTRY_SHA, 'command_stream_sha256': COMMAND_SHA,
             'mapped_nodes': 119, 'registered_tests': 91,
             'static_report_slots': 110, 'static_selected_tests': 2057,
             'actual_report_slots': {mode: len(private_observations[mode]['report_slots']) for mode in ('legacy', 'dag')},
             'actual_report_skips': {mode: sum(row['skipped'] for row in private_observations[mode]['report_slots']) for mode in ('legacy', 'dag')},
             'actual_report_expected_failures': {mode: sum(row['expected_failures'] for row in private_observations[mode]['report_slots']) for mode in ('legacy', 'dag')},
             'same_job_raw_receiving': True, 'raw_census_bookends_equal': True,
             'source_and_runtime_bookends_equal': True, 'portal_populations': [49,49], 'repro_populations': [19,19],
             'declared_evidence_roles_per_route': 2, 'finite_rules_unchanged': 13, 'finite_narrowings_unchanged': 6,
             'relations': compared, 'all_declared_relations_equal': all(row['equal'] for row in compared.values()),
             'original_acceptance': False, 'full_G2': False, 'G1': False, 'G3': False, 'C5': False,
             'canonical_conversion': False, 'legacy_retirement': False,
             'test_level_authenticity_claim': False, 'unexported_fixture_internal_state_equivalence_claim': False}
    demand(len(encode(proof)) <= 16384, 'FULL_PUBLIC_PROOF_BOUND')
    validate_public_proof(proof, policy_sha=sha(encode(policy)), inputs_sha=sha(encode(relation['inputs'])),
                          source_commit=relation['inputs']['source_commit'], source_tree=relation['inputs']['source_tree'])
    owner.durable_bytes(evidence / 'FULL_RELATION_PROOF.json', encode(proof))
    return proof


def validate_public_proof(value, *, policy_sha, inputs_sha, source_commit, source_tree):
    """Closed public-safe schema; arbitrary parsed receiver data is not exported."""
    import re
    def digest(value):
        return type(value) is str and re.fullmatch('[0-9a-f]{64}', value) is not None
    def descriptor(value, maximum):
        demand(type(value) is dict and set(value) == {'bytes','sha256'} and type(value['bytes']) is int and
               0 <= value['bytes'] <= maximum and digest(value['sha256']), 'PUBLIC_PROOF_DESCRIPTOR')
    fixed = {'schema': 'dg16.full-correspondence-proof.v1', 'authority': 'NONE',
             'scope': 'FULL_CANONICAL_REGISTERED_OPERATION_AND_DECLARED_TRANSITIVE_OUTPUTS',
             'source_commit': source_commit, 'source_tree': source_tree, 'policy_sha256': policy_sha,
             'receiver_inputs_sha256': inputs_sha, 'registry_sha256': REGISTRY_SHA, 'command_stream_sha256': COMMAND_SHA,
             'mapped_nodes': 119, 'registered_tests': 91, 'static_report_slots': 110, 'static_selected_tests': 2057,
             'same_job_raw_receiving': True, 'raw_census_bookends_equal': True, 'source_and_runtime_bookends_equal': True,
             'portal_populations': [49,49], 'repro_populations': [19,19], 'declared_evidence_roles_per_route': 2,
             'finite_rules_unchanged': 13, 'finite_narrowings_unchanged': 6, 'original_acceptance': False,
             'full_G2': False, 'G1': False, 'G3': False, 'C5': False, 'canonical_conversion': False,
             'legacy_retirement': False, 'test_level_authenticity_claim': False,
             'unexported_fixture_internal_state_equivalence_claim': False}
    varying = {'private_observations','actual_report_slots','actual_report_skips','actual_report_expected_failures',
               'relations','all_declared_relations_equal'}
    demand(type(value) is dict and set(value) == set(fixed) | varying and
           all(type(value[k]) is type(v) and value[k] == v for k,v in fixed.items()), 'PUBLIC_PROOF_FIXED_FIELDS')
    descriptor(value['private_observations'],16*1024**2)
    for key in ('actual_report_slots','actual_report_skips','actual_report_expected_failures'):
        row = value[key]
        demand(type(row) is dict and set(row) == {'legacy','dag'} and all(type(n) is int and 0 <= n <= 2057 for n in row.values()),
               'PUBLIC_PROOF_REPORT_COUNTS')
        if key == 'actual_report_slots': demand(row == {'legacy':110,'dag':110}, 'PUBLIC_PROOF_REPORT_POPULATION')
    demand(type(value['relations']) is dict and set(value['relations']) == set(SCOPES), 'PUBLIC_PROOF_SCOPE_POPULATION')
    for row in value['relations'].values():
        demand(type(row) is dict and set(row) == {'equal','difference_count','witnesses','witnesses_complete',
                                                 'left_projection_sha256','right_projection_sha256'} and
               type(row['equal']) is bool and type(row['difference_count']) is int and 0 <= row['difference_count'] <= 1000000 and
               row['equal'] == (row['difference_count'] == 0) and type(row['witnesses_complete']) is bool and
               row['witnesses_complete'] == (row['difference_count'] <= 2) and
               digest(row['left_projection_sha256']) and digest(row['right_projection_sha256']) and
               type(row['witnesses']) is list and len(row['witnesses']) == min(2,row['difference_count']), 'PUBLIC_PROOF_RELATION')
        demand(row['equal'] == (row['left_projection_sha256'] == row['right_projection_sha256']), 'PUBLIC_PROOF_EQUALITY_DIGEST')
        for witness in row['witnesses']:
            fixed_fields = {'kind','location_sha256','left_projection_sha256','right_projection_sha256'}
            demand(type(witness) is dict and witness.get('kind') in ('TYPE','BYTES','VALUE','FIELD_POPULATION','POPULATION') and
                   set(witness) == fixed_fields | ({'first_different_offset','left','right'} if witness['kind']=='BYTES' else set()) and
                   all(digest(witness[k]) for k in ('location_sha256','left_projection_sha256','right_projection_sha256')),
                   'PUBLIC_PROOF_WITNESS')
            if witness['kind']=='BYTES':
                descriptor(witness['left'],128*1024**2);descriptor(witness['right'],128*1024**2)
                demand(type(witness['first_different_offset']) is int and
                       0 <= witness['first_different_offset'] <= min(witness['left']['bytes'],witness['right']['bytes']),
                       'PUBLIC_PROOF_BYTE_OFFSET')
    demand(type(value['all_declared_relations_equal']) is bool and value['all_declared_relations_equal'] ==
           all(row['equal'] for row in value['relations'].values()), 'PUBLIC_PROOF_OVERALL_EQUALITY')
    demand(len(encode(value)) <= 16384, 'PUBLIC_PROOF_BYTE_BOUND')
    return value


def recheck(source, out, owner, relation, policy, *, runtime_python):
    evidence = out / 'evidence'
    raw = owner.retained_bytes(evidence, 'FULL_RELATION_PRIVATE.json')[0]
    private = relation['evidence'].strict(raw)
    proof_raw = owner.retained_bytes(evidence, 'FULL_RELATION_PROOF.json')[0]
    proof = relation['evidence'].strict(proof_raw)
    demand(proof['private_observations'] == desc(raw) and proof['policy_sha256'] == sha(encode(policy)) and
           proof['receiver_inputs_sha256'] == sha(encode(relation['inputs'])) and proof['all_declared_relations_equal'] is True,
           'CLOSING_PROOF_BINDING')
    demand(source_profiles(source, owner, relation)[0] == private['source_profiles'] and
           runtime_observation(runtime_python, owner, evidence, initial=False) == private['runtime'], 'CLOSING_SOURCE_RUNTIME_CHANGED')
    for path, census in private['captures'].items():
        demand(owner._capture_census(Path(path)) == census, 'CLOSING_SEALED_CAPTURE_CHANGED')
    for mode in ('legacy', 'dag'):
        capsule = out / 'captures' / mode / 'capture'
        stdout = owner.retained_bytes(capsule, 'stdout.log')[0]
        pending, readback = relation['evidence'].receive_declared(stdout, out / 'declared-artifacts' / mode, owner)
        demand(readback == private['raw_readbacks'][mode]['external'] and
               {role: {key: pending[role][key] for key in ('root', 'original_census', 'retained_census')}
                for role in relation['evidence'].ROLES} == private['declared_artifacts'][mode], 'CLOSING_EXTERNAL_CAPTURE_CHANGED')
    demand(owner.retained_bytes(evidence, 'FULL_RELATION_PRIVATE.json')[0] == raw and
           owner.retained_bytes(evidence, 'FULL_RELATION_PROOF.json')[0] == proof_raw, 'CLOSING_RECEIVER_RECORD_CHANGED')
    return {'schema': 'dg16.full-correspondence-closing-readback.v1', 'authority': 'NONE',
            'proof': desc(proof_raw), 'private_observations': desc(raw), 'same_private_censuses': True,
            'same_source_and_runtime': True, 'new_acceptance_or_currentness_authority': False}
