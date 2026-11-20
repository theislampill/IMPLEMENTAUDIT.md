#!/usr/bin/env python3
"""Independent inert-data receiver. No reviewed code import, extraction or mutation."""
from pathlib import Path, PurePosixPath
import hashlib
import io
import json
import re
import stat
import subprocess
import sys
import zipfile
from urllib.parse import parse_qsl, urlsplit, unquote

STAGE = Path('/workspace/scratch/9fad46324cc4/continuation-20261120/dg18-remaining/results21-stage')
PUB = STAGE / 'publish'
DESCRIPTOR_SHA = '6a077fda69661c37f48fdb6a36aaaab1bd566e46e1f31403788643ea3a8eb89c'
STAGE_SHA = '60a072fc66e852b6ea8d4d93611412c6160872ab85c025f3fcdb4f15c77d8101'
PARENT = '48588ed6e2cc34ad35b3bf7d78721dfbf24b2297'
BASE = '071bae063996a082a5b95498f2732eab150bd267'
EXPECTED = '053a5af81f8dd3fc26edbfd7550bb1bc605ef189'
PREFIX = 'handoff/pro-executor-results-20261115/continuing-execution-20261120-21'
FINAL_SEAL = '22fa9baaeafa23a54bc937f07911512fa41fb5b2b108ceafbe58cf3639ff9e03'
ARTIFACTS = {
    'a1': (824125, 'b66ab785c7bac0e43c4ca32816061c48a4085a5513ac1f91161d72ba93a32309', 7),
    'a3-r2': (1180836, 'cf11c1b09efa180dfad43e2a9b1d664747f555e4998522aa631b725f780be323', 10),
    'exact-tool-bodies': (6058490, 'f97e11f0e39830fa703a7106b9bba7cf445cba2a75bf37c6516e427e34448f59', 47),
    'review-evidence': (1313991, 'da59d73b4eda8addb67239c46f170ed71b91d9ab514773cecaa11c04a1509ab5', 11),
}
checks = 0


def require(ok, label):
    global checks
    checks += 1
    if not ok:
        raise AssertionError(label)


def identity(raw):
    return {'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest(),
            'git_blob': hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()}


def check_identity(raw, row, label):
    actual = identity(raw)
    for key in ('bytes', 'sha256', 'git_blob'):
        if key in row:
            require(actual[key] == row[key], label + ':' + key)
    return raw


def safe_relative(name):
    p = PurePosixPath(name)
    require(bool(name) and not p.is_absolute() and '..' not in p.parts
            and '\\' not in name and '\0' not in name and ':' not in name
            and str(p) == name.rstrip('/'), 'unsafe path:' + name)
    return p


def read_selected(path):
    p = Path(path)
    require(p.name != 'DOWNLOAD_ACTUALS.json', 'prohibited raw download source')
    require(not any('g132' in part.lower() for part in p.parts), 'private G132 source')
    require(not p.is_symlink(), 'selected source is symlink:' + str(p))
    return p.read_bytes()


def json_bytes(raw):
    return json.loads(raw)


def tree_oid(entries):
    require(len({r['path'] for r in entries}) == len(entries), 'duplicate tree names')
    chunks = []
    for row in sorted(entries, key=lambda r: r['path'].encode() + (b'/' if r['type'] == 'tree' else b'')):
        require('/' not in row['path'] and '\0' not in row['path'], 'tree child name')
        require((row['type'], row['mode']) in {
            ('tree', '040000'), ('blob', '100644'), ('blob', '100755'),
            ('blob', '120000'), ('commit', '160000')}, 'tree mode and type')
        chunks.append(row['mode'].lstrip('0').encode() + b' ' + row['path'].encode()
                      + b'\0' + bytes.fromhex(row['sha']))
    body = b''.join(chunks)
    return hashlib.sha1(b'tree ' + str(len(body)).encode() + b'\0' + body).hexdigest()


def new_subtree(rows):
    root = {}
    for row in rows:
        parts = safe_relative(row['repository_path'][len(PREFIX) + 1:]).parts
        cursor = root
        for part in parts[:-1]:
            cursor = cursor.setdefault(part, {})
        require(parts[-1] not in cursor, 'new tree collision')
        cursor[parts[-1]] = row
    def visit(node):
        entries = []
        for name, child in node.items():
            if 'repository_path' in child:
                entries.append({'path': name, 'mode': child['mode'], 'type': 'blob', 'sha': child['git_blob']})
            else:
                entries.append({'path': name, 'mode': '040000', 'type': 'tree', 'sha': visit(child)})
        return tree_oid(entries)
    return visit(root)


def api_receipt(raw):
    receipt = json_bytes(raw)
    require(receipt.get('isError') is False, 'provider receipt error')
    return json.loads(receipt['structuredContent']['content'])


descriptor_raw = read_selected(STAGE / 'FINAL_PUBLICATION_DESCRIPTOR.json')
check_identity(descriptor_raw, {'bytes': 47161, 'sha256': DESCRIPTOR_SHA}, 'pinned descriptor')
desc = json_bytes(descriptor_raw)
stage_raw = read_selected(STAGE / 'FINAL_STAGE_MANIFEST.json')
check_identity(stage_raw, {'sha256': STAGE_SHA}, 'pinned stage seal')
stage = json_bytes(stage_raw)
require((desc['parent'], desc['base_tree'], desc['expected_tree'], desc['repository_prefix'])
        == (PARENT, BASE, EXPECTED, PREFIX), 'descriptor ancestry')
require(len(stage['payloads']) == stage['payload_count'] == 13, 'stage population')
require(sum(r['bytes'] for r in stage['payloads']) == stage['payload_bytes'], 'stage byte count')
for row in stage['payloads']:
    check_identity(read_selected(STAGE / str(safe_relative(row['path']))), row, 'stage:' + row['path'])

files = desc['files']
require(len(files) == desc['publication_files'] == 80, 'publication count')
require(sum(r['bytes'] for r in files) == desc['publication_bytes'] == 9435914, 'publication bytes')
actual_paths = {str(p.relative_to(PUB)) for p in PUB.rglob('*') if p.is_file()}
expected_paths = set()
publication_raw = {}
for row in files:
    require(row['repository_path'].startswith(PREFIX + '/'), 'outside new publication subtree')
    rel = row['repository_path'][len(PREFIX) + 1:]
    safe_relative(rel)
    require(row['local_path'] == str(PUB / rel), 'publication local path binding')
    require(row['type'] == 'blob' and row['mode'] == '100644' and row['encoding'] == 'base64', 'publication blob attributes')
    require(row['bytes'] <= 131072, 'publication file exceeds bound')
    publication_raw[rel] = check_identity(read_selected(PUB / rel), row, 'publication:' + rel)
    expected_paths.add(rel)
require(len(expected_paths) == 80 and actual_paths == expected_paths, 'publication exact allowlist')
packet = json_bytes(publication_raw['PACKET_MANIFEST.json'])
require(packet['seal_excluded_from_own_population'] is True, 'packet seal excludes itself')
require({r['path'] for r in packet['files']} == expected_paths - {'PACKET_MANIFEST.json'}, 'packet file set')
require(len(packet['files']) == packet['file_count'] == 79, 'packet file count')
require(sum(r['bytes'] for r in packet['files']) == packet['file_bytes'], 'packet bytes')
for row in packet['files']:
    check_identity(publication_raw[row['path']], row, 'packet member:' + row['path'])

assembly = json_bytes(publication_raw['ASSEMBLY_INDEX.json'])
require((assembly['expected_parent'], assembly['expected_parent_tree']) == (PARENT, BASE), 'assembly ancestry')
require(assembly['part_bytes_maximum'] == 131072, 'part bound')
require({r['artifact'] for r in assembly['archives']} == set(ARTIFACTS), 'archive census')
archives, raw_members_by_artifact, used_parts, archive_observations = {}, {}, set(), []
for item in assembly['archives']:
    name = item['artifact']
    require((item['bytes'], item['sha256'], len(item['parts'])) == ARTIFACTS[name], 'pinned archive:' + name)
    offset, chunks = 0, []
    for ordinal, part in enumerate(item['parts']):
        require(part['ordinal'] == ordinal and part['offset'] == offset, 'part order:' + name)
        require(0 < part['bytes'] <= 131072 and part['path'] not in used_parts, 'part length/uniqueness')
        used_parts.add(part['path'])
        chunks.append(check_identity(publication_raw[part['path']], part, 'part:' + part['path']))
        offset += part['bytes']
    raw = check_identity(b''.join(chunks), item, 'archive:' + name)
    require(raw == read_selected(item['source_path']), 'exact retained source archive:' + name)
    z = zipfile.ZipFile(io.BytesIO(raw))
    infos = z.infolist()
    require(len(infos) == len({r.filename for r in infos}) == item['member_count'], 'ZIP member population:' + name)
    require(sum(r.file_size for r in infos) == item['uncompressed_bytes'], 'ZIP uncompressed size:' + name)
    members = {}
    for member in infos:
        safe_relative(member.filename)
        require(PurePosixPath(member.filename).name != 'DOWNLOAD_ACTUALS.json', 'prohibited raw receipt in ZIP')
        require(not any('g132' in x.lower() for x in PurePosixPath(member.filename).parts), 'private member path')
        require(not member.is_dir() and not stat.S_ISLNK(member.external_attr >> 16), 'ZIP regular-file members')
        require(not member.flag_bits & 1, 'encrypted ZIP member')
        members[member.filename] = z.read(member)  # ZIP CRC is checked by read().
    require(z.testzip() is None, 'ZIP CRC:' + name)
    archives[name], raw_members_by_artifact[name] = z, members
    archive_observations.append({'artifact': name, **identity(raw), 'parts': len(item['parts']),
                                 'members': len(members), 'safe_paths_and_crc': 'PASS'})
require(len(used_parts) == 75, '75 once-only parts')
require(expected_paths - used_parts == {'README.md', 'ASSEMBLY_INDEX.json', 'PACKET_MANIFEST.json',
                                       'PREPARATION_CHECKS.json', 'verify_packet.py'}, 'five ancillary publication files')

evidence = raw_members_by_artifact['review-evidence']
logical_rows = json_bytes(evidence['indexes/LOGICAL_MEMBER_INDEX.json'])['members']
review_rows = json_bytes(evidence['indexes/REVIEW_SEALS.json'])['reviews']
raw_index = json_bytes(evidence['indexes/RAW_ARTIFACT_MEMBERS.json'])['members']
require(len(logical_rows) == len({r['path'] for r in logical_rows}) == 311, 'logical population')
require(len(raw_index) == len({(r['artifact'], r['member']) for r in raw_index}) == 1511, 'raw member index population')
for row in raw_index:
    check_identity(raw_members_by_artifact[row['artifact']][row['member']], row, 'raw member:' + row['member'])
for name in ('a1', 'a3-r2', 'exact-tool-bodies'):
    require({r['member'] for r in raw_index if r['artifact'] == name} == set(raw_members_by_artifact[name]), 'complete raw index:' + name)
logical, logical_index, payloads, artifact_bindings = {}, {}, set(), 0
for row in logical_rows:
    safe_relative(row['path'])
    storage = row['storage']
    if storage['kind'] == 'deduplicated-evidence-payload':
        raw = evidence[storage['member']]
        payloads.add(storage['member'])
    else:
        require(storage['kind'] == 'exact-original-artifact-member', 'logical storage kind')
        require(storage['artifact_sha256'] == ARTIFACTS[storage['artifact']][1], 'logical raw artifact binding')
        raw = raw_members_by_artifact[storage['artifact']][storage['member']]
        artifact_bindings += 1
    check_identity(raw, row, 'logical:' + row['path'])
    require(raw == read_selected(row['source_path']), 'unchanged selected logical source:' + row['path'])
    logical[row['path']], logical_index[row['path']] = raw, row
require(len(payloads) == 293 and artifact_bindings == 9, 'compact storage census')
require(len({identity(evidence[n])['sha256'] for n in payloads}) == 293, 'evidence payload content deduplication')
indexes = {'indexes/' + n + '.json' for n in ['LOGICAL_MEMBER_INDEX', 'REVIEW_SEALS', 'RAW_ARTIFACT_MEMBERS',
           'PRIVACY_CHECK', 'BASE_TREE_CLOSURE', 'ROOT_DECISIONS']}
require(set(evidence) == payloads | indexes, 'evidence ZIP complete population')
raw_nonempty_hashes = {identity(b)['sha256'] for n in ('a1', 'a3-r2', 'exact-tool-bodies')
                      for b in raw_members_by_artifact[n].values() if b}
require(not ({identity(evidence[n])['sha256'] for n in payloads} & raw_nonempty_hashes), 'no duplicate raw bodies inside evidence')
review_observations, review_payload_count = [], 0
require(len(review_rows) == 9, 'nine sealed reviews')
for row in review_rows:
    prefix = 'reviews/' + row['review'] + '/'
    seal_raw = check_identity(logical[prefix + row['seal_path']], row['seal_identity'], 'review seal:' + row['review'])
    seal = json_bytes(seal_raw)
    sealed_rows = next(seal[k] for k in ('files', 'payloads', 'members') if isinstance(seal.get(k), list))
    require(len(sealed_rows) == len({r['path'] for r in sealed_rows}) == row['payload_count'], 'review sealed count:' + row['review'])
    require(sum(r['bytes'] for r in sealed_rows) == row['payload_bytes'], 'review sealed bytes:' + row['review'])
    require({n for n in logical if n.startswith(prefix)} == {prefix + row['seal_path']} | {prefix + r['path'] for r in sealed_rows}, 'review exact population:' + row['review'])
    for member in sealed_rows:
        check_identity(logical[prefix + member['path']], member, 'sealed member:' + prefix + member['path'])
    review_payload_count += len(sealed_rows)
    review_observations.append({'review': row['review'], 'seal_sha256': row['seal_identity']['sha256'],
                                'payload_count': len(sealed_rows), 'payload_bytes': row['payload_bytes']})
require(review_payload_count == 223, '223 sealed payloads')

decisions_index = json_bytes(evidence['indexes/ROOT_DECISIONS.json'])
require(decisions_index['authority'] == 'ROOT_ONLY' and len(decisions_index['files']) == 5, 'Root decision population/authority')
for row in decisions_index['files']:
    check_identity(logical[row['path']], row, 'Root decision:' + row['path'])
decisions = {n: json_bytes(raw) for n, raw in logical.items() if n.startswith('root-decisions/')}
final_prefix = 'reviews/a1-a3-final-independent-receiving/'
require(identity(logical[final_prefix + 'SEAL.json'])['sha256'] == FINAL_SEAL, 'pinned final review seal')
for criterion, expected_sha, run, artifact in [
    ('A1', '17973bf158235270714b1b46f4a4cc99b7cc0f921301d183001572085de4c891', 44703838739, 'a1'),
    ('A3', 'd6ec2a51108e935b5215cd104da65af20ba088a77475b49d9de29a81c4ba6e28', 44702285737, 'a3-r2')]:
    name = 'root-decisions/DG18_' + criterion + '_ROOT_ACCEPTANCE.json'
    d = decisions[name]
    require(identity(logical[name])['sha256'] == expected_sha, 'pinned Root decision:' + criterion)
    require(d['criterion'] == criterion and d['adjudicator'] == '/root' and d['decision'] == 'ACCEPT_COMPLETE_ORIGINAL_CRITERION', 'Root attribution:' + criterion)
    require(d['product_commit'] == '51416b2f156b341c4a5f09029e2c6ceb5b30b1e7' and d['original_obligation']['criterion_denominator'] == 14, 'unchanged product/denominator')
    require(d['original_episode']['run_id'] == run and d['original_episode']['raw_artifact_sha256'] == ARTIFACTS[artifact][1], 'original episode archive binding')
    require(d['r02_late_retention_closure']['artifact_sha256'] == ARTIFACTS['exact-tool-bodies'][1]
            and d['r02_late_retention_closure']['capture_run'] == 44715708048, 'later acquisition binding')
    independent = d['independent_review']
    require(independent['seal_sha256'] == FINAL_SEAL and independent['sealed_payloads'] == 22
            and independent['sealed_payload_bytes'] == 3916931, 'final seal population binding')
    for key, name in [('report_sha256', 'REPORT.md'), ('requirements_matrix_sha256', 'REQUIREMENTS_MATRIX.json')]:
        require(identity(logical[final_prefix + name])['sha256'] == independent[key], 'final review member binding')
    require(d['unchanged_contract_sha256'] in {r['sha256'] for r in logical_rows}, 'unchanged contract retained')
    require(d['new_complete_original_criteria_awarded'] == 1, 'one Root award per decision')
frontier = decisions['root-decisions/ACCEPTANCE_FRONTIER.json']
require(frontier['new_complete_original_criteria'] == ['DG18.A1', 'DG18.A3'] and frontier['other_new_complete_original_awards'] == [], 'only two new Root criteria')
require(frontier['dg18']['accepted_current'] == ['A1','A3','A6','A8','A9','A10','A11','A13','A14']
        and frontier['dg18']['accepted_count'] == 9 and frontier['dg18']['original_denominator'] == 14, '9/14 frontier')
require(frontier['dg18']['remaining_current'] == ['A2','A4','A5','A7','A12']
        and frontier['whole_original_cells_accepted'] == 0 and frontier['whole_original_cell_denominator'] == 3, 'remaining/whole-cell scope')
actual_adjudication = decisions['root-decisions/ROOT_ADJUDICATION_ACTUAL_TOOL_RETURN.json']
require(actual_adjudication['exit_code'] == 0, 'Root adjudication actual exit')
issued = json.loads(actual_adjudication['output'])
require(issued['new_complete_original_criteria'] == 2 and issued['whole_cells'] == '0/3', 'Root actual award scope')
for row in issued['decisions']:
    check_identity(logical['root-decisions/' + Path(row['path']).name], row, 'actual issued decision identity')
final_actual = decisions['root-decisions/ROOT_FINAL_RECEIVING_ACTUAL_TOOL_RETURN.json']
require(final_actual['exit_code'] == 0, 'Root final receiving actual exit')
received = json.loads(final_actual['output'])
require(received['review_seal_sha256'] == FINAL_SEAL and received['verified_payloads'] == 22
        and received['payload_bytes'] == 3916931, 'Root actual final review receiving')
for row in received['contracts']:
    matching = [r for r in logical_rows if r['source_path'] == row['path']]
    require(bool(matching), 'Root actual contract is retained')
    for member in matching:
        check_identity(logical[member['path']], row, 'Root actual contract identity')
readme = publication_raw['README.md'].decode()
for phrase in ['9/14', '0/3', '44697958629', 'remains failed', 'acquired later', 'does not claim a contemporaneous raw copy',
               'unobserved original Bash-version query', 'Original mode/owner observations', 'No original episode was replayed',
               'N1 LOST/UNKNOWN', 'W-FULL', 'only two new original criterion awards']:
    require(phrase in readme, 'README required qualified claim:' + phrase)
failed_report = logical['reviews/a3-actual-first/REPORT.md'].decode()
require('FAILED_INCOMPLETE_NO_A3_AWARD' in failed_report and '44697958629' in failed_report, 'first failed A3 history retained')
require('receipts/a3-r2-provider/metadata/DOWNLOAD_ACTUALS_PUBLIC.json' in logical
        and 'receipts/a3-r2-provider/metadata/REDACTION_CORRECTION.json' in logical, 'explicit A3 public replacements')

closure = json_bytes(evidence['indexes/BASE_TREE_CLOSURE.json'])
require(closure['expected_parent'] == PARENT and closure['expected_parent_tree'] == BASE, 'base closure binding')
require(len(closure['levels']) == 3, 'complete three-level closure')
base_commit = api_receipt(logical['stage-receipts/BASE_COMMIT_GET.json'])
require(base_commit['sha'] == PARENT and base_commit['tree']['sha'] == BASE, 'received base commit/tree relation')
levels = {x['directory']: x for x in closure['levels']}
for directory, level in levels.items():
    require(tree_oid(level['entries']) == level['sha'], 'independently reproduced base tree:' + directory)
    receipt = api_receipt(logical['stage-receipts/' + level['receipt']])
    require(receipt['sha'] == level['sha'] and receipt.get('truncated') is False, 'complete base tree receipt:' + directory)
    require([{k: r[k] for k in ('path','mode','type','sha')} for r in receipt['tree']] == level['entries'], 'receipt exact tree entries:' + directory)
subtree = new_subtree(files)
proof = json_bytes(read_selected(STAGE / 'FINAL_TREE_PROOF.json'))
require(subtree == proof['added_subtree'], 'new subtree identity')
new_oid, preservation = subtree, []
for directory, child in [('handoff/pro-executor-results-20261115', 'continuing-execution-20261120-21'),
                         ('handoff', 'pro-executor-results-20261115'), ('', 'handoff')]:
    old = levels[directory]
    kept = [dict(r) for r in old['entries'] if r['path'] != child]
    selected = [r for r in old['entries'] if r['path'] == child]
    if directory == 'handoff/pro-executor-results-20261115':
        require(not selected, 'new subtree did not exist')
    else:
        lower = directory + '/' + child if directory else child
        require(len(selected) == 1 and selected[0]['sha'] == levels[lower]['sha']
                and selected[0]['type'] == 'tree', 'existing ancestor relation')
    updated = kept + [{'path': child, 'mode': '040000', 'type': 'tree', 'sha': new_oid}]
    next_oid = tree_oid(updated)
    preservation.append({'directory': directory, 'old_tree': old['sha'], 'new_tree': next_oid,
                         'only_changed_or_added_child': child, 'preserved_other_entries': len(kept)})
    new_oid = next_oid
require(preservation == proof['levels'], 'independent tree proof matches staging proof')
require(new_oid == EXPECTED, 'expected resulting root tree')

# Screen explicit publication data; recursively decode JSON strings. Findings never print values.
rules = {
    'private-key-header': re.compile(r'-----BEGIN (?:RSA |EC |DSA |OPENSSH |ENCRYPTED )?PRIVATE KEY-----'),
    'github-token': re.compile(r'\b(?:gh[pousr]_[A-Za-z0-9]{24,}|github_pat_[A-Za-z0-9_]{30,})\b'),
    'aws-access-key': re.compile(r'\b(?:AKIA|ASIA)[A-Z0-9]{16}\b'),
    'slack-token': re.compile(r'\bxox[baprs]-[A-Za-z0-9-]{20,}\b'),
    'bearer-token': re.compile(r'(?i)\bBearer\s+[A-Za-z0-9._~+/-]{24,}=*'),
}
sensitive_keys = {'sig', 'signature', 'x-amz-signature', 'x-goog-signature', 'token', 'access_token',
                  'client_secret', 'refresh_token', 'auth', 'authorization'}
url_pattern = re.compile(r'https?://[^\s<>"\x00-\x20]+')
privacy_findings, scanned_strings = [], 0
seen_strings = set()


def scan_text(label, value, depth=0):
    global scanned_strings
    if depth > 30 or value in seen_strings:
        return
    seen_strings.add(value)
    scanned_strings += 1
    for rule, expression in rules.items():
        if expression.search(value):
            privacy_findings.append({'path': label, 'rule': rule})
    for match in url_pattern.finditer(value):
        url = match.group(0).replace('\\/', '/')
        try:
            parsed = urlsplit(url)
            if parsed.username or parsed.password:
                privacy_findings.append({'path': label, 'rule': 'URL-userinfo'})
            for key, val in parse_qsl(parsed.query, keep_blank_values=True):
                if key.lower() in sensitive_keys and val:
                    if not any(s in val.lower() for s in ('redacted','removed','placeholder','example','<','>','{','}')):
                        privacy_findings.append({'path': label, 'rule': 'value-bearing-URL-' + key.lower()})
        except ValueError:
            pass
    stripped = value.lstrip()
    if stripped.startswith(('{','[','"')):
        try:
            obj = json.loads(value)
        except (ValueError, RecursionError):
            return
        def walk(node):
            if isinstance(node, str):
                scan_text(label, node, depth + 1)
            elif isinstance(node, list):
                for item in node:
                    walk(item)
            elif isinstance(node, dict):
                for key, item in node.items():
                    scan_text(label, str(key), depth + 1)
                    walk(item)
        walk(obj)


privacy_population = [(name + ':' + member, raw) for name, members in raw_members_by_artifact.items()
                      for member, raw in members.items()]
privacy_population += [('publication:' + name, raw) for name, raw in publication_raw.items() if name not in used_parts]
for label, raw in privacy_population:
    scan_text(label, raw.decode('utf-8', errors='replace'))
require(not privacy_findings, 'bounded privacy findings:' + json.dumps(privacy_findings))
declared_privacy = json_bytes(evidence['indexes/PRIVACY_CHECK.json'])
require(declared_privacy['findings'] == [] and declared_privacy['private_G132_inputs_selected'] == 0, 'declared privacy scope')

# Execute only the reviewed inert verifier, preserving the actual return in the receiving result.
proc = subprocess.run([sys.executable, str(PUB / 'verify_packet.py')], cwd=PUB, capture_output=True, text=True, check=False)
require(proc.returncode == 0 and proc.stderr == '', 'provided data verifier execution')
provided = json.loads(proc.stdout)
require(provided['status'] == 'PASS_DATA_ONLY_PACKET_VERIFICATION' and provided['publication_files'] == 80
        and provided['complete_sealed_reviews'] == 9 and provided['awards_by_verifier'] == [], 'provided verifier result')
check_identity(read_selected(STAGE / 'FINAL_PUBLICATION_DESCRIPTOR.json'), {'sha256': DESCRIPTOR_SHA}, 'descriptor unchanged at completion')
check_identity(read_selected(STAGE / 'FINAL_STAGE_MANIFEST.json'), {'sha256': STAGE_SHA}, 'stage seal unchanged at completion')

print(json.dumps({
    'schema': 'dg18.results21.independent-publication-receiving.v1',
    'status': 'READY_LOCAL_PUBLICATION_DATA', 'reviewer': '/root/results21_publication_review',
    'authority': 'NONE', 'formal_audit_assess_activation': False, 'authoring_context_reuse': False,
    'descriptor': {'path': str(STAGE / 'FINAL_PUBLICATION_DESCRIPTOR.json'), **identity(descriptor_raw)},
    'stage_seal': {'path': str(STAGE / 'FINAL_STAGE_MANIFEST.json'), **identity(stage_raw)},
    'checks': checks, 'publication_files': 80, 'publication_bytes': 9435914,
    'archives': archive_observations, 'raw_artifact_members': 1511,
    'logical_evidence_paths': 311, 'unique_evidence_payloads': 293, 'artifact_member_bindings': 9,
    'complete_reviews': review_observations, 'review_payloads': review_payload_count,
    'source_comparisons': {'stage_payloads':13, 'publication_files':80, 'raw_and_evidence_archives':4, 'logical_members':311},
    'Root_decisions': {r['path']: r['sha256'] for r in decisions_index['files']},
    'Root_awards_referenced': ['DG18.A1', 'DG18.A3'], 'Root_frontier': '9/14', 'whole_original_cells': '0/3',
    'parent': PARENT, 'base_tree': BASE, 'expected_tree': new_oid, 'preservation': preservation,
    'privacy': {'status':'PASS_BOUNDED_SELECTED_DATA_SCREEN', 'scanned_raw_or_unique_payloads':len(privacy_population),
                'unique_text_strings':scanned_strings, 'rules':list(rules) + ['URL-userinfo','value-bearing-sensitive-URL-query'],
                'nested_JSON_strings':True, 'findings':privacy_findings, 'forbidden_old_download_receipt_read':False,
                'private_G132_inputs_selected':0, 'limit':'Deterministic bounded pattern screen over explicit selected bytes; not universal credential detection.'},
    'provided_verifier_actual': {'command':[sys.executable,str(PUB/'verify_packet.py')], 'exit_code':proc.returncode,
                                'stdout':proc.stdout, 'stderr':proc.stderr},
    'provider_writes':0, 'controller_calls':0, 'original_runtime_executions':0, 'original_awards':[],
    'limits':['Local publication receiving only; no provider publication receipt or currentness claim.',
              'Root alone awards criteria and governs publication; no closure, integration, protected grant or original-contract amendment.',
              'Original semantic source and episode review was not repeated. Earlier failed A3 and preliminary findings remain exact historical evidence.']
}, indent=2, sort_keys=True))
