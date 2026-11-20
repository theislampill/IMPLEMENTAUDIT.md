#!/usr/bin/env python3
"""Read-only publication integrity/privacy/claims receiving; no source execution."""
from pathlib import Path, PurePosixPath
from collections import Counter
import hashlib
import io
import json
import posixpath
import re
import stat
import urllib.parse
import zipfile

BASE = Path('/workspace/scratch/9fad46324cc4/continuation-20261120')
STAGE = BASE / 'results22-stage'
REVIEW = BASE / 'results22-publication-review'
EXPECTED_DESCRIPTOR = 'd149eafb406a2b74884d79dd2d1453a9ae75e6e96c8407142f9a0555e70003ea'
PREFIX = 'handoff/pro-executor-results-20261115/continuing-execution-20261120-22/'
checks = []


def require(name, condition):
    checks.append({'name': name, 'passed': bool(condition)})
    if not condition:
        raise AssertionError(name)


def identity(raw):
    return {'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest(),
            'git_blob': hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()}


def safe_relative(name):
    p = PurePosixPath(name)
    return bool(name) and not p.is_absolute() and '..' not in p.parts and '\\' not in name and '\0' not in name


descriptor_raw = (STAGE / 'PUBLICATION_DESCRIPTOR.json').read_bytes()
descriptor = json.loads(descriptor_raw)
require('Exact requested descriptor SHA256', identity(descriptor_raw)['sha256'] == EXPECTED_DESCRIPTOR)
require('Exact base commit/tree', (descriptor['base_commit'], descriptor['base_tree']) ==
        ('25b55d06d1ed09ceffc9e271a7aa26b65d08c422', 'b0bf31f6a6da8b64ff010298c412117d54ab6afb'))
require('Ten files, 479790 bytes', len(descriptor['files']) == descriptor['files_count'] == 10
        and sum(row['bytes'] for row in descriptor['files']) == descriptor['bytes'] == 479790)
publication = {}
for row in descriptor['files']:
    path = Path(row['local_path'])
    require('Publication path and type: ' + row['path'], row['path'].startswith(PREFIX)
            and safe_relative(row['path']) and row['mode'] == '100644'
            and path == STAGE / 'files' / row['path'][len(PREFIX):]
            and path.is_file() and not path.is_symlink())
    raw = path.read_bytes()
    require('Publication byte/hash/blob: ' + row['path'], identity(raw) ==
            {key: row[key] for key in ('bytes', 'sha256', 'git_blob')})
    publication[row['path'][len(PREFIX):]] = raw
require('Closed staging file population', {p.relative_to(STAGE / 'files').as_posix()
        for p in (STAGE / 'files').rglob('*') if p.is_file()} == set(publication))
assembly = json.loads(publication['ARCHIVE.json'])
require('Assembly descriptor exact', assembly == descriptor['archive'])
require('Four bounded parts', len(assembly['parts']) == 4 and
        [row['bytes'] for row in assembly['parts']] == [131072, 131072, 131072, 40479])
for index, row in enumerate(assembly['parts']):
    require('Exact ordered part ' + str(index), row['path'] ==
            'evidence/G132_CURRENT_PUBLIC_EVIDENCE.zip.part' + str(index).zfill(3)
            and identity(publication[row['path']])['sha256'] == row['sha256'])
archive_raw = b''.join(publication[row['path']] for row in assembly['parts'])
require('Exact reconstructed archive', len(archive_raw) == assembly['bytes'] == 433695 and
        identity(archive_raw)['sha256'] == assembly['sha256'] ==
        '7b8efd091af7798d3f49f9a3c41183f58c470433b0c3290ab7290d97aad659aa')
require('Staged unsplit ZIP matches declared parts', (STAGE / assembly['file_name']).read_bytes() == archive_raw)

with zipfile.ZipFile(io.BytesIO(archive_raw)) as archive:
    infos = archive.infolist()
    names = [info.filename for info in infos]
    require('Closed regular safe ZIP members', len(names) == len(set(names)) == 123 and all(
        safe_relative(info.filename) and not info.is_dir() and not (info.flag_bits & 1)
        and not stat.S_ISLNK(info.external_attr >> 16) for info in infos))
    require('Every ZIP CRC', archive.testzip() is None)
    index_raw = archive.read('INDEX.json')
    index = json.loads(index_raw)
    logical = {row['path']: row for row in index['files']}
    objects = {name.removeprefix('objects/'): archive.read(name)
               for name in names if name.startswith('objects/')}
    require('160 logical files and 122 unique bodies', len(logical) == len(index['files']) ==
            index['logical_file_count'] == assembly['logical_file_count'] == 160 and
            len(objects) == index['unique_objects'] == assembly['unique_object_count'] == 122)
    require('No unused or unindexed ZIP bodies', set(names) == {'INDEX.json'} | {'objects/' + sha for sha in objects}
            and set(objects) == {row['sha256'] for row in logical.values()})
    require('Logical and unique byte census', sum(row['bytes'] for row in logical.values()) ==
            index['logical_bytes'] == 2174714 and sum(map(len, objects.values())) == index['unique_bytes'] == 1953053)
    for sha, raw in objects.items():
        require('Unique object identity: ' + sha, hashlib.sha256(raw).hexdigest() == sha)
    for path, row in logical.items():
        require('Logical identity and safe path: ' + path, safe_relative(path) and identity(objects[row['sha256']]) ==
                {key: row[key] for key in ('bytes', 'sha256', 'git_blob')})
        original = BASE / path
        require('Exact original public file: ' + path, original.is_file() and not original.is_symlink()
                and original.read_bytes() == objects[row['sha256']]
                and oct(stat.S_IMODE(original.stat().st_mode)) == row['local_mode'])

def body(path):
    return objects[logical[path]['sha256']]


def document(path):
    return json.loads(body(path))


manifest_paths = [
    'g132-readiness/g132-sender-successor/MANIFEST.json',
    'g132-current-protected-request/MANIFEST.json',
    'g132-new-sender/PREQUALIFICATION_MANIFEST.json',
    'g132-current-preloads/ROOT_PRELOAD_SEAL.json',
    'g132-current-preloads/child-g132_sender_20261120/SEAL.json',
    'a1-a3-independent-receiving/g132-source-review/SEAL.json',
    'a1-a3-independent-receiving/g132-final-request-review/SEAL.json',
]
closed = []
covered = set()
for path in manifest_paths:
    doc = document(path)
    members = next(doc[key] for key in ('members', 'files', 'payloads') if isinstance(doc.get(key), list))
    for row in members:
        member = posixpath.join(posixpath.dirname(path), row['path'])
        require('Sealed inventory member: ' + member, member in logical and all(
                logical[member][key] == row[key] for key in ('bytes', 'sha256')))
        if 'mode' in row:
            require('Sealed original mode: ' + member, logical[member]['local_mode'] == row['mode'])
        covered.add(member)
    if 'member_count' in doc:
        require('Seal count: ' + path, doc['member_count'] == len(members))
    if 'member_bytes' in doc:
        require('Seal bytes: ' + path, doc['member_bytes'] == sum(row['bytes'] for row in members))
    closed.append({'manifest': path, 'sha256': logical[path]['sha256'], 'members': len(members),
                   'bytes': sum(row['bytes'] for row in members), 'all_exact': True})
    covered.add(path)
extras = sorted(set(logical) - covered)
expected_extras = {
    'G132_NEW_SENDER_ASSIGNMENT.json',
    'a1-a3-independent-receiving/g132-final-request-review/ACTUAL_FINAL_SEAL_TOOL_RETURN.json',
    'a1-a3-independent-receiving/g132-source-review/ACTUAL_SEAL_TOOL_RETURN.json',
    'g132-current-preloads/child-g132_sender_20261120/ACTUAL_SEAL_READBACK_TOOL_RETURN.json',
    'g132-current-preloads/child-g132_sender_20261120/ACTUAL_SEAL_TOOL_RETURN.json',
    'g132-current-ref-invocation-join.json', 'g132-new-sender/ASSIGNMENT_JOIN_POSTSEAL.json',
    'g132-new-sender/PARTIALREPORT.md', 'g132-new-sender/resources.json',
    'g132-owner-request-ready/ACTUAL_ROOT_READY_RETURN.json',
    'g132-owner-request-ready/ROOT_REQUEST_READY_ADJUDICATION.json',
}
require('Only eleven explicit public postseal/assignment/readiness supplements', set(extras) == expected_extras)

request = json.loads(publication['PROTECTED_OPERATION_REQUEST_UNISSUED.json'])
decision = json.loads(publication['ROOT_REQUEST_READY_ADJUDICATION.json'])
final_seal = json.loads(publication['INDEPENDENT_REQUEST_SEAL.json'])
require('Visible request exact archived current request', publication['PROTECTED_OPERATION_REQUEST_UNISSUED.json'] ==
        body('g132-current-protected-request/PROTECTED_OPERATION_REQUEST_UNISSUED.json'))
require('Visible final review and seal exact complete archived review',
        publication['INDEPENDENT_REQUEST_RECEIVING.md'] == body('a1-a3-independent-receiving/g132-final-request-review/REPORT.md')
        and publication['INDEPENDENT_REQUEST_SEAL.json'] == body('a1-a3-independent-receiving/g132-final-request-review/SEAL.json'))
require('Visible Root decision exact archived decision', publication['ROOT_REQUEST_READY_ADJUDICATION.json'] ==
        body('g132-owner-request-ready/ROOT_REQUEST_READY_ADJUDICATION.json'))
require('Exact requested Root and independent pins', identity(publication['ROOT_REQUEST_READY_ADJUDICATION.json'])['sha256'] ==
        'c2847d42c3756ced9f5dcc6d0328557990f8a9bdac78e9258a3e3b1fda8577b6' and
        identity(publication['INDEPENDENT_REQUEST_SEAL.json'])['sha256'] ==
        '4f42349a7c474223458156967356cbd26546eb1f2f4d69536d49c62606aa46e4')
require('Decision joins exact frozen request and independent seal',
        decision['request']['sha256'] == identity(publication['PROTECTED_OPERATION_REQUEST_UNISSUED.json'])['sha256'] and
        decision['independent_receiving']['sha256'] == identity(publication['INDEPENDENT_REQUEST_SEAL.json'])['sha256'])
require('Readiness only; grants launch and sender admission unissued',
        decision['decision'] == 'READY_TO_PRESENT_EXACT_SEPARATE_PROTECTED_OPERATION_REQUEST' and
        all(decision[key] == 'UNISSUED' for key in ('fresh_owner_grant', 'protected_host_launch', 'original_sender_admission'))
        and request['owner_grant'] == descriptor['owner_grant'] == descriptor['protected_launch'] == 'UNISSUED')
require('No awards or changed whole-cell denominator', request['original_awards'] == decision['original_awards'] == []
        and (decision['dg18_current_accepted'], decision['dg18_denominator'], decision['whole_cells']) == (9, 14, '0/3'))
require('Single-use no-force/no-retry and retained historical unknown', request['single_attempt'] is True and
        request['automatic_retry'] is False and request['force_updates'] is False and
        decision['historical_301'] == 'UNKNOWN_NO_REPLAY' and decision['no_acceptance_amendment'] is True)
fixed = document('g132-readiness/g132-sender-successor/FIXED_FACTS.json')
baseline = document('g132-readiness/g132-sender-successor/baseline/FIXED_FACTS.json')
budget = {key: fixed[key] for key in ('maximum_native_calls', 'maximum_native_result_bytes',
          'minimum_remaining_ms', 'native_result_chunk_bytes', 'original_obligations', 'original_phase_max_ms')}
require('Source budgets unchanged from sealed prior selection', all(baseline[key] == value for key, value in budget.items()))
require('Request preserves original budgets and operation counts', request['phase_limit_ms'] == fixed['original_phase_max_ms'] == 600000
        and request['sender_remaining_time_floor_ms'] == fixed['minimum_remaining_ms'] == 300000
        and request['host_job_max_minutes'] == 75 and request['host_tools_adoption_seconds'] == 600
        and request['recipient_acquisition_seconds'] == 600 and request['original_root_metadata_reads'] == 18)

# Inspect only already-public packet content. Never read any referenced private input or active custody file.
reconciliation = document('g132-current-protected-request/CURRENT_LOCAL_RECONCILIATION.json')
private_rows = reconciliation['selected_input_checks']
private_hashes = {row['actual']['sha256'] for row in private_rows}
require('Eleven private roles represented only by exact metadata', len(private_rows) == 11 and all(
        set(row['actual']) == {'bytes', 'sha256'} for row in private_rows)
        and sum(row['actual']['bytes'] for row in private_rows) == 647342)
require('No private input object body or logical path included', not (private_hashes & set(objects)) and all(
        row['path'] not in {str(BASE / name) for name in logical} for row in private_rows))
ledger_metadata = [row for row in reconciliation['custody'] if 'rows' in row]
require('Active ledger represented by metadata not body', len(ledger_metadata) == 1
        and isinstance(ledger_metadata[0]['rows'], int)
        and set(ledger_metadata[0]) == {'path','identity','identity_match','xattrs','bytes','sha256','rows'}
        and ledger_metadata[0]['sha256'] not in objects)
require('No custody-directory or private-input file payload paths', all(
        'g132-live-operation-' not in name and not any(part in {'.git','.IMPLEMENTAUDIT','private-inputs'}
        for part in PurePosixPath(name).parts) for name in logical))
findings = []
patterns = [re.compile(r'(?i)[?&](?:sig|signature|x-amz-signature|x-goog-signature)=[^&\s"\\]+'),
            re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----'),
            re.compile(r'\b(?:ghp_|github_pat_)[A-Za-z0-9_]{20,}')]
for label, raw in list(objects.items()) + [('visible/' + name, raw) for name, raw in publication.items()
                                        if not name.startswith('evidence/')]:
    try:
        value = raw.decode('utf-8')
    except UnicodeDecodeError:
        findings.append({'object_or_file': label, 'kind': 'unexpected_binary_public_body'})
        continue
    for decoding in range(3):
        for number, pattern in enumerate(patterns):
            if pattern.search(value): findings.append({'object_or_file': label, 'pattern': number, 'decode_round': decoding})
        decoded = urllib.parse.unquote(value)
        if decoded == value: break
        value = decoded
require('No signed-reference or credential-body scan findings', not findings)

# Reconstruct the exact base from already received complete ancestor trees and the 84 results21 additions.
def git_tree(entries):
    raw = b''
    for row in sorted(entries, key=lambda r: (r['path'] + ('/' if r['type'] == 'tree' else '')).encode()):
        mode = '40000' if row['type'] == 'tree' else row['mode']
        raw += mode.encode() + b' ' + row['path'].encode() + b'\0' + bytes.fromhex(row['sha'])
    return hashlib.sha1(b'tree ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()


def subtree(rows, prefix):
    node = {}
    for row in rows:
        path = row.get('repository_path', row.get('path'))
        require('Additive subtree prefix: ' + path, path.startswith(prefix))
        here = node
        parts = path[len(prefix):].split('/')
        for part in parts[:-1]: here = here.setdefault(part, {})
        require('Unique additive leaf: ' + path, parts[-1] not in here)
        here[parts[-1]] = (row['mode'], row['git_blob'])
    def finish(current):
        return git_tree([{'path': key, 'mode': '040000' if isinstance(value, dict) else value[0],
                          'type': 'tree' if isinstance(value, dict) else 'blob',
                          'sha': finish(value) if isinstance(value, dict) else value[1]} for key, value in current.items()])
    return finish(node)


closure_path = BASE / 'dg18-remaining/results21-stage/BASE_TREE_CLOSURE.json'
closure = json.loads(closure_path.read_bytes())
levels = {row['directory']: row for row in closure['levels']}
for directory, row in levels.items():
    require('Retained ancestor exact tree: ' + directory, git_tree(row['entries']) == row['sha'])
old_descriptor_path = BASE / 'dg18-remaining/results21-stage/FINAL_PUBLICATION_DESCRIPTOR.json'
envelope_path = BASE / 'results21-root-publication/REVIEW_ENVELOPE_DESCRIPTOR.json'
old = json.loads(old_descriptor_path.read_bytes())
envelope = json.loads(envelope_path.read_bytes())
old_subtree = subtree(old['files'] + envelope['files'], old['repository_prefix'] + '/')
results = list(levels['handoff/pro-executor-results-20261115']['entries'])
old_name = old['repository_prefix'].split('/')[-1]
require('Results21 prior added name absent in earlier base', old_name not in {row['path'] for row in results})
results.append({'path': old_name, 'mode': '040000', 'type': 'tree', 'sha': old_subtree})


def wrap_results(entries):
    result_oid = git_tree(entries)
    handoff = [dict(row, sha=result_oid) if row['path'] == 'pro-executor-results-20261115' else row
               for row in levels['handoff']['entries']]
    handoff_oid = git_tree(handoff)
    root = [dict(row, sha=handoff_oid) if row['path'] == 'handoff' else row for row in levels['']['entries']]
    return git_tree(root), result_oid, handoff_oid


base_oid, _, _ = wrap_results(results)
require('Exact reviewed immutable base tree reconstructed', base_oid == descriptor['base_tree'])
base_receipt_path = BASE / 'results21-root-publication/receipts/COMMIT_1_READBACK.json'
base_receipt = json.loads(base_receipt_path.read_bytes())
base_commit = json.loads(base_receipt['value']['structuredContent']['content'])
require('Actual retained provider base commit/tree join', base_commit['sha'] == descriptor['base_commit']
        and base_commit['tree']['sha'] == base_oid)
new_name = PREFIX.rstrip('/').split('/')[-1]
require('New results22 directory absent from exact base', new_name not in {row['path'] for row in results})
new_subtree = subtree(descriptor['files'], PREFIX)
final_tree, final_results, final_handoff = wrap_results(results +
    [{'path': new_name, 'mode': '040000', 'type': 'tree', 'sha': new_subtree}])
require('No descriptor drift after full receiving', (STAGE / 'PUBLICATION_DESCRIPTOR.json').read_bytes() == descriptor_raw)

result = {'schema': 'results22.independent-publication-receiving.v1', 'disposition': 'PASS',
          'scope': 'Exact local publication integrity, privacy boundaries and claim consistency only',
          'authority': 'NONE', 'reviewer': '/root/dg18_remaining', 'actual_model_self_report': 'GPT-6 Astra Pro',
          'requested_model': 'inherited/default; no override', 'provider_backend_configuration': 'not exposed',
          'not_author_of_G132_source_request_or_results22_stage': True,
          'ordinary_nonauthor_review_not_formal_audit_assess_route': True,
          'descriptor': identity(descriptor_raw), 'publication_files': 10, 'publication_bytes': 479790,
          'archive': identity(archive_raw), 'zip_members': 123, 'all_crc_checked': True,
          'logical_files': 160, 'logical_bytes': index['logical_bytes'], 'unique_objects': 122,
          'unique_object_bytes': index['unique_bytes'], 'index': identity(index_raw),
          'all_original_public_file_bytes_modes_checked': True, 'sealed_populations': closed,
          'explicit_public_supplements': extras,
          'claims': {'owner_grant': 'UNISSUED', 'protected_launch': 'UNISSUED', 'sender_admission': 'UNISSUED',
                     'awards': [], 'dg18': '9/14', 'whole_cells': '0/3', 'frozen_pending_metadata_retained_as_history': True,
                     'later_exact_independent_seal_and_Root_decision_joined': True, 'budgets': budget},
          'privacy': {'private_input_bodies_read_by_reviewer': 0, 'active_custody_bodies_read_by_reviewer': 0,
                      'signed_reference_or_credential_pattern_findings': findings,
                      'all_private_input_and_active_ledger_hashes_excluded': True,
                      'metadata_only_custody_shape_checked': True,
                      'scan_boundary': 'Complete 122 unique public bodies plus six visible public files; three percent-decoding rounds.'},
          'tree': {'base_commit': descriptor['base_commit'], 'base_tree': base_oid, 'new_subtree': new_subtree,
                   'expected_publication_tree': final_tree, 'results_tree': final_results, 'handoff_tree': final_handoff,
                   'every_existing_leaf_mode_type_oid_preserved': True, 'only_additions': 10,
                   'base_evidence': [{'path': str(p), **identity(p.read_bytes())} for p in
                                     (closure_path, old_descriptor_path, envelope_path, base_receipt_path)]},
          'source_or_preload_controls_rerun': 0, 'original_executions': 0, 'provider_calls': 0, 'controller_calls': 0,
          'archive_copies_created': 0, 'checks': checks, 'checks_passed': len(checks), 'blocking_findings': []}
target = REVIEW / 'RECEIVING.json'
with target.open('x') as handle:
    json.dump(result, handle, sort_keys=True, indent=2)
    handle.write('\n')
print(json.dumps({'disposition': result['disposition'], 'checks_passed': len(checks),
                  'sealed_populations': [(r['members'], r['bytes']) for r in closed],
                  'expected_publication_tree': final_tree, 'receiving': identity(target.read_bytes())}, indent=2))
