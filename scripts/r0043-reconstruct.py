#!/usr/bin/env python3
"""Read the R0043 EAOSE/AMA documentary continuation (canonically unallocated).

Adapter over existing R0044 strict JSON/hash/archive helpers (canonically unallocated).
It reads immutable research records, never executes archive code, grants no
authority and does not implement a second runtime, evaluator or state machine.
Missing later preparation remains missing; aggregate counts cannot populate it.
"""
import argparse
from collections import Counter, defaultdict
import importlib.util
import io
import json
from pathlib import Path, PurePosixPath
import re
import sys
import zipfile


ROOT = Path(__file__).resolve().parents[1]
DOC = Path('docs/research/implementaudit')
spec = importlib.util.spec_from_file_location('r0044_reconstruction_core', ROOT / 'scripts/r0044-reconstruct.py')
core = importlib.util.module_from_spec(spec)
spec.loader.exec_module(core)
require, parse, canonical, digest, pointer = core.require, core.parse, core.canonical, core.digest, core.pointer
COMMIT = 'cacfe97da7656b472bf4f11e50c9d106a6c3f92a'
EAOSE_IDS = [f'EAOSE:EAOSE-C{i:03}' for i in range(1, 133)]
KEYS = [f'EAA:EAA-{i:03}' for i in range(1, 71)] + [f'EMAS:EMAS-{i:03}' for i in range(1, 77)] + EAOSE_IDS
EAOSE_STATES = {'STRONGLY_RETAINED': 18, 'RETAINED_IN_EVOLVED_FORM': 35,
    'USEFUL_BUT_EASILY_GAMED': 2, 'CONTEXT_DEPENDENT': 26, 'REJECTED_OR_DISFAVOURED': 20,
    'ASSUMPTION_SENSITIVE': 17, 'DOMAIN_SPECIFIC': 2, 'CONTESTED': 2,
    'SUPERSEDED_BY_STRONGER_FORM': 2, 'CEREMONY_NOT_GENERAL_PROPERTY': 4,
    'USEFUL_BUT_EASILY_BUREAUCRATISED': 1, 'UNRESOLVED': 2, 'NO_GENERAL_PROPERTY': 1}
PREPARED_COUNTS = {'PARTIALLY_ABSORBED': 34, 'CONDITIONAL': 66,
    'REJECTED_WITH_REASON': 25, 'DEFERRED': 3, 'RESEARCH_ONLY': 4}
TC10 = ['ESPLE:ESPLE-023', 'EBPM:EBPM-022', 'EPM:EPM-043', 'EPM:EPM-064', 'EMAS:EMAS-072', 'EAOSE:EAOSE-C124']
ACCEPTANCE = {'eaose_132': 'NOT_ACCEPTED', 'ama_278_32': 'NOT_ACCEPTED',
    'native_receiving': 'NOT_ESTABLISHED', 'predecessor_retirement': 'NOT_AUTHORISED'}
RELATION_COUNTS = {'directions': 20152, 'pairs': 24592, 'material_pairs': 9178,
    'no_material_pairs': 15414, 'hand_bridges': 105}
SIBLINGS = {
    'EAA': {'issue': 233, 'commit': '6f2183c782a283a9c0925a0195837a6310539070',
        'tree': 'd35b411fa7f1cfbb8df0a7ba127cb39ec18e8d22',
        'path': str(DOC / 'r0045-member-dispositions.json'), 'bytes': 636575,
        'sha256': '85b6e242ba567d5dc0cac3d90deb1d1479a9a27129a90dc949a5e968ed0a2122',
        'certificate': 'https://github.com/theislampill/IMPLEMENTAUDIT.md/issues/233#issuecomment-6204270650',
        'certificate_body_sha256': 'a7d73c2b0d06cf9f2d20a7df8a9a0c6954a38f24425707f35149f1d6019b4678',
        'scope': 'Accepted 70-member constituent documentary contribution; shared C001/EAA-001 evidence counted once; no host synthesis acceptance.'},
    'EMAS': {'issue': 231, 'commit': '44117ccd5af275f24bed923da7ba282a829f42e9',
        'tree': 'cf695dc0befdc0cbaa6a92e43db512ce2eb504ad',
        'path': str(DOC / 'r0044-member-dispositions.json'), 'bytes': 9359909,
        'git_blob': '86e4fa1f02a88d9759323dc018e63a25380e59bf',
        'certificate': 'https://github.com/theislampill/IMPLEMENTAUDIT.md/issues/231#issuecomment-6244484285',
        'certificate_body_sha256': 'b53fdd264942b4d3cedb49ded55d1b954995a04f53a3ab0cc2baf0c42d3dd4ae',
        'scope': 'Accepted 76-member documentary contribution; both six-unit alternatives complete, total cost INCONCLUSIVE; no new trial or whole-AMA acceptance.'}}


def read_lock(root=ROOT):
    lock = parse((root / DOC / 'r0043-source-lock.json').read_bytes())
    require(lock['commit'] == COMMIT and lock['packet']['sha256'] == core.PINS[core.AMA_ZIP][1], 'wrong frozen source lock')
    return lock


def write_index(path, index):
    """Keep every text part below the observed GitHub content retrieval limit."""
    path.parent.mkdir(parents=True, exist_ok=True)
    manifest = {k: v for k, v in index.items() if k not in ('rows', 'groups')}
    manifest['storage_format'] = 'r0043-parts-v1'
    manifest['parts'] = []
    for axis in ('rows', 'groups'):
        pending, batches = [], []
        for record in index[axis]:
            if pending and len(canonical(pending + [record])) > 780000:
                batches.append(pending)
                pending = []
            pending.append(record)
        if pending:
            batches.append(pending)
        for i, records in enumerate(batches, 1):
            part = {'format': 'r0043-record-part-v1', 'allocation': 'Published R0043; canonically unallocated; documentary only',
                'axis': axis, 'records': records}
            data = canonical(part) + b'\n'
            require(len(data) <= 800000, 'one record exceeds retrievable part bound')
            name = f'{path.stem}-{axis}-{i:02}.json'
            (path.parent / name).write_bytes(data)
            manifest['parts'].append({'file': name, 'axis': axis, 'records': len(records), 'bytes': len(data), 'sha256': digest(data)})
    core.write_json(path, manifest)


def read_index(path):
    manifest = parse(path.read_bytes())
    if 'storage_format' not in manifest:
        return manifest
    require(manifest['storage_format'] == 'r0043-parts-v1', 'unsupported part manifest')
    index = {k: v for k, v in manifest.items() if k not in ('storage_format', 'parts')}
    index['rows'], index['groups'] = [], []
    seen = set()
    for item in manifest['parts']:
        name = item['file']
        safe_member(name)
        require('/' not in name and name not in seen and item['axis'] in ('rows', 'groups'), 'invalid or duplicate part route')
        seen.add(name)
        data = (path.parent / name).read_bytes()
        require(len(data) == item['bytes'] and len(data) <= 800000 and digest(data) == item['sha256'], 'projection part identity differs')
        part = parse(data)
        require(part['format'] == 'r0043-record-part-v1' and part['axis'] == item['axis'] and len(part['records']) == item['records'], 'projection part population differs')
        index[item['axis']].extend(part['records'])
    return index


def safe_member(name):
    require(isinstance(name, str) and name and not name.startswith('/') and
        '\\' not in name and ':' not in name and '\x00' not in name and
        all(p not in ('', '.', '..') for p in name.split('/')),
        'unsafe archive member: ' + repr(name))
    require(str(PurePosixPath(name)) == name, 'noncanonical archive member')


def checked_archive(data):
    archive = zipfile.ZipFile(io.BytesIO(data))
    names = archive.namelist()
    require(len(names) == len(set(names)), 'duplicate archive member')
    for info in archive.infolist():
        safe_member(info.filename)
        require(not info.is_dir() and (info.external_attr >> 16) & 0o170000 != 0o120000,
                'non-regular archive member')
    require(archive.testzip() is None, 'archive CRC failure')
    return archive


class Corpus:
    def __init__(self, path, lock):
        data = path.read_bytes()
        pin = core.PINS[core.AMA_ZIP]
        require(len(data) == pin[0] and digest(data) == pin[1], 'frozen packet identity differs')
        core.pinned_bytes(core.AMA_ZIP, data)
        self.archive = checked_archive(data)
        core.Corpus.verify_archive(self.archive, lock['ama_members'], 'EVOLVED_AMA_FROZEN_MANIFEST.json')
        self.cache, self.nested, self.nested_cache = {}, {}, {}
        for lineage in ('EAA', 'EAOSE', 'EMAS'):
            member = f'constituents/{lineage}.zip'
            nested = self.archive.read(member)
            self.nested[member] = checked_archive(nested)
            if lineage == 'EAOSE':
                require(len(nested) == lock['eaose_packet']['bytes'] and digest(nested) == lock['eaose_packet']['sha256'], 'EAOSE packet identity differs')
                # This frozen lineage uses payloads; the AMA/EMAS helper's
                # payload_inventory schema must not be imposed on its bytes.
                eaose = self.nested[member]
                embedded = 'EVOLVED_AGENT_ORIENTED_SOFTWARE_ENGINEERING_CANONICAL_FROZEN_MANIFEST.json'
                require(set(eaose.namelist()) == {r['member'] for r in lock['eaose_members']}, 'EAOSE member population differs')
                for item in lock['eaose_members']:
                    payload = eaose.read(item['member'])
                    require(len(payload) == item['bytes'] and digest(payload) == item['sha256'], 'EAOSE external member differs')
                inventory = parse(eaose.read(embedded))['payloads']
                require({r['filename'] for r in inventory} == set(eaose.namelist()) - {embedded}, 'EAOSE embedded member population differs')
                for item in inventory:
                    payload = eaose.read(item['filename'])
                    require(len(payload) == item['bytes'] and digest(payload) == item['sha256'], 'EAOSE embedded payload differs')
        self.register = self.load(core.REGISTER)['property_by_key']
        self.intake = self.load(core.INTAKE)['rows']
        self.intake_by_key = {r['global_qualified_key']: (i, r) for i, r in enumerate(self.intake)}
        self.relations = self.load(core.RELATIONS)['relations']
        self.relation_by_id = {r['relation_id']: r for r in self.relations}
        self.pairs = self.load(core.MATRIX)['pairs']
        self.groups = self.load(core.GROUPS)['clusters']
        self.profiles = self.load(core.PROFILES)
        self.bridges = self.profiles['hand_adjudicated_directional_bridges']
        self.sources = self.load(core.SOURCES)['source_by_key']
        self.context = self.load(core.CONTEXT)
        require(set(self.register) == set(KEYS) and set(self.intake_by_key) == set(KEYS) and len(self.intake) == 278, 'original population differs')
        require(dict(Counter(self.register[k]['disposition'] for k in EAOSE_IDS)) == EAOSE_STATES, 'EAOSE source statuses differ')
        require(len(self.relations) == len(self.relation_by_id) == 20152 and len(self.pairs) == 24592 and len(self.bridges) == 105, 'relation/pair population differs')
        require(Counter(p['relation_status'] for p in self.pairs) == Counter({'MATERIAL_RELATION': 9178, 'NO_MATERIAL_RELATION': 15414}), 'negative pair population differs')
        require([g['cluster_id'] for g in self.groups] == [f'AMA-K{i:03}' for i in range(1, 33)], 'group population differs')
        memberships = Counter(k for g in self.groups for k in g['member_properties'])
        require(sum(memberships.values()) == 1245 and sum(v > 1 for v in memberships.values()) == 266, 'membership population differs')
        require(len(self.sources) == 234 and sum(k.startswith('EAOSE:') for k in self.sources) == 124, 'packet-local bibliography differs')
        self.incident, self.pair_indices, self.bridge_indices = defaultdict(list), defaultdict(list), defaultdict(list)
        self.reverse_endpoints = defaultdict(list)
        for key, record in self.register.items():
            require(record['qualified_property_key'] == key and self.resolve_original(record) == record['frozen_record'], 'full original/register correspondence differs: ' + key)
            for group in record['cluster_ids']:
                require(key in next(g for g in self.groups if g['cluster_id'] == group)['member_properties'], 'group membership mismatch')
        for record in self.sources.values():
            require(self.resolve_original(record) == record['frozen_source_record'], 'source bibliography correspondence differs')
        for relation in self.relations:
            a, b = relation['source_property'], relation['target_property']
            require(a in self.register and b in self.register and relation['assumptions']['joint_guard'], 'unresolved relation endpoint/guard')
            self.incident[a].append(relation)
            if a != b:
                self.incident[b].append(relation)
            self.reverse_endpoints[(a, b)].append(relation)
            reverse = relation['reverse_relation_id']
            if reverse:
                other = self.relation_by_id[reverse]
                require(other['source_property'] == b and other['target_property'] == a, 'reverse endpoint mismatch')
        for i, pair in enumerate(self.pairs):
            for key in (pair['left_property'], pair['right_property']):
                require(key in self.register, 'unknown pair endpoint')
                self.pair_indices[key].append(i)
            require(all(r in self.relation_by_id for r in pair['directional_relation_ids']), 'unknown pair direction')
        for i, bridge in enumerate(self.bridges):
            for key in (bridge['source'], bridge['target']):
                require(key in self.register, 'unknown bridge endpoint')
                self.bridge_indices[key].append(i)

    def load(self, name):
        safe_member(name)
        if name not in self.cache:
            self.cache[name] = parse(self.archive.read(name))
        return self.cache[name]

    def resolve_original(self, record):
        loc = record['authority_locator']
        archive_name = loc['archive']
        raw = self.archive.read(archive_name)
        require(digest(raw) == loc['archive_sha256'], 'mixed constituent archive')
        key = (archive_name, loc['member'])
        if key not in self.nested_cache:
            self.nested_cache[key] = parse(self.nested[archive_name].read(loc['member']))
        return pointer(self.nested_cache[key], loc['json_pointer'])


def index_row(index, key):
    rows = [r for r in index['rows'] if r['key'] == key]
    require(len(rows) == 1, 'unknown member: ' + key)
    return rows[0]


def continuation(record):
    source = record['disposition']
    reject = source in {'REJECTED_OR_DISFAVOURED', 'NO_GENERAL_PROPERTY', 'CEREMONY_NOT_GENERAL_PROPERTY'}
    return {'now': ('Retain the rejection or non-general result and its full rationale; do not turn it into an implementation promise.' if reject else
                    'Retain this exact conditional source meaning; obtain missing target correspondence before a stronger target claim.'),
        'if_selected': {'criterion': record['criterion'], 'actual_owner_and_rights': record['authority'],
            'assumptions': record['assumptions'], 'postcondition': record['output_or_postcondition'],
            'required_evidence': record['frozen_record'].get('EVIDENCE_NEEDED_AT_LATER_AUDIT',
                {'criterion': record['criterion'], 'source_evidence_ceiling': record['evidence_ceiling']})},
        'otherwise': record['non_trigger_or_cheap_path'],
        'reconsideration_trigger': record['trigger'],
        'horizon': 'Before relying on this stronger selected claim, changing its material premise, or retiring its existing custody; no future date or programme steward is appointed.',
        'receiving_route': 'Issue 232 owner for the separate EAOSE or AMA decision, with the applicable native mechanism owner; no owner acceptance asserted.'}


def build(corpus, lock, antecedent, tc):
    raw = antecedent.read_bytes()
    pin = lock['historical_target']
    require(len(raw) == pin['bytes'] and digest(raw) == pin['sha256'], 'historical target identity differs')
    old = {r['key']: (i, r) for i, r in enumerate(parse(raw)['properties'])}
    require(set(KEYS) <= set(old), 'missing historical original')
    tc_raw = tc.read_bytes()
    stored_tc = parse(tc_raw)
    if 'raw_source_json_unallocated' in stored_tc:
        tc_raw = stored_tc['raw_source_json_unallocated'].encode('utf-8')
    require(len(tc_raw) == lock['tc_source']['bytes'] and digest(tc_raw) == lock['tc_source']['sha256'], 'TC source identity differs')
    findings = parse(tc_raw)['findings']
    rows = []
    for key in KEYS:
        record = corpus.register[key]
        n, intake = corpus.intake_by_key[key]
        old_n, historical = old[key]
        require(historical['source_row_sha256'] == digest(canonical(intake)) and historical['source_semantic_disposition'] == record['disposition'], 'historical source/target correspondence differs: ' + key)
        rows.append({'key': key, 'original_id': record['constituent_id'], 'lineage': record['lineage'],
            'name': record['name'], 'source_status': record['disposition'],
            'original': {**record['authority_locator'], 'canonical_record_sha256': digest(canonical(record['frozen_record']))},
            'register': {'member': core.REGISTER, 'pointer': '/property_by_key/' + key, 'canonical_record_sha256': digest(canonical(record))},
            'intake': {'member': core.INTAKE, 'pointer': f'/rows/{n}', 'canonical_record_sha256': digest(canonical(intake))},
            'source_obligation': {'criterion': record['criterion'], 'trigger': record['trigger'],
                'cheap_path': record['non_trigger_or_cheap_path'], 'authority': record['authority'],
                'mechanism': record['mechanism'], 'assumptions': record['assumptions']},
            'groups': record['cluster_ids'], 'source_ids': record['source_ids'],
            'within_lineage_relation_ids': record['within_lineage_relation_ids'],
            'incident_direction_ids': [r['relation_id'] for r in corpus.incident[key]],
            'pair_indices': corpus.pair_indices[key], 'bridge_indices': corpus.bridge_indices[key],
            'historical_target': {'disposition': historical['disposition'], 'pointer': f'/properties/{old_n}',
                'canonical_record_sha256': digest(canonical(historical)),
                'record_json_unallocated': canonical(historical).decode(),
                'scope': 'OLDER_PUBLIC_ANTECEDENT_NOT_LATER_PREPARATION_OR_CURRENT_RUNTIME'},
            'later_prepared_target': None,
            'later_prepared_state': 'UNAVAILABLE_EAOSE_OR_AMA_TARGET' if record['lineage'] == 'EAOSE' else 'SEPARATE_ACCEPTED_CONSTITUENT_ROUTE',
            'accepted_constituent': SIBLINGS.get(record['lineage']),
            'current_scope': 'DOCUMENTARY_CONTINUATION_ONLY; no per-member operational pass or full absorption',
            'continuation': continuation(record)})
    groups = [{'id': g['cluster_id'], 'name': g['name'], 'members': g['member_properties'],
        'source_pointer': '/clusters/' + str(i), 'canonical_record_sha256': digest(canonical(g)),
        'original_record_json_unallocated': canonical(g).decode(),
        'later_prepared_group_record': None,
        'current_scope': 'Original mechanism and member guards recoverable; the later mechanism-specific RED and positive target controls are unavailable and unqualified.'}
        for i, g in enumerate(corpus.groups)]
    result = {'format': 'r0043-public-continuation-v1',
        'allocation': 'Published R0043; canonically unallocated. This projection allocates no new identity, cell or authority.',
        'source_commit': COMMIT, 'packet_sha256': lock['packet']['sha256'],
        'scope': 'ORIGINALS_AND_OLDER_PUBLIC_TARGET_WITH_SEPARATE_ACCEPTED_CONSTITUENTS; later EAOSE/AMA preparation unavailable',
        'population': {'originals': 278, 'eaose': 132, 'eaa': 70, 'emas': 76, 'groups': 32,
            'memberships': 1245, 'overlapping_originals': 266, 'additional_memberships': 967},
        'source_status_counts': EAOSE_STATES, 'reported_later_eaose_counts_only': PREPARED_COUNTS,
        'acceptance': ACCEPTANCE, 'relations': RELATION_COUNTS,
        'relation_scope': 'Original typed directions and independently recorded reverses, explicit negative pairs and guarded bridges; no execution edges or invented target relation dispositions.',
        'context_populations': {'bundles': 16, 'tensions': 24, 'configurations': 15, 'profiles': 54, 'rejected_novelty_candidates': 20, 'new_properties': 0},
        'full_context_members': lock['ama_members'],
        'tc_findings': [{'id': f['id'], 'parents': f['parents'], 'classification': f['classification'],
            'record_json_unallocated': canonical(f).decode(),
            'scope': 'Original analytical hypothesis, no new normative property; native owners and guards preserved.'} for f in findings],
        'accepted_siblings': SIBLINGS, 'rows': rows, 'groups': groups,
        'missing_input': {'eaose_crosswalk_unallocated': 'R0043_CROSSWALK.json', 'eaose_preparation': 'PREPARATION.json#/rows/0',
            'ama_preparation': 'PREPARATION.json#/rows/3',
            'binding': 'INPUT_EVIDENCE.json for the retained final preparation correspondence',
            'required_content': ['PROPERTY_LEDGER.jsonl', 'GROUP_LEDGER.jsonl', 'RELATION_LOCATORS.jsonl',
                'FULL_CONTEXT_LEDGER.jsonl', 'TARGET_RELATION_DISPOSITIONS.jsonl', 'TARGET_RECONCILIATION.json',
                'SOURCE_MEMBER_MANIFEST.json', 'INPUT_MANIFEST.json', 'OPERATIVE_SOURCE_BINDINGS.json', 'AMA_CONTINUATION_CANDIDATE.md'],
            'limit': 'Exact individual meaning cannot be recreated from historical counts. This is an input boundary, not evidence of a runtime defect.'}}
    return core.seal(result)


def check_index(index):
    require(index.get('format') == 'r0043-public-continuation-v1', 'wrong projection format')
    unsigned = dict(index)
    supplied = unsigned.pop('projection_sha256')
    require(supplied == digest(canonical(unsigned)), 'projection digest differs')
    require(index['source_commit'] == COMMIT and index['packet_sha256'] == core.PINS[core.AMA_ZIP][1], 'wrong original source')
    require(index['population'] == {'originals': 278, 'eaose': 132, 'eaa': 70, 'emas': 76,
        'groups': 32, 'memberships': 1245, 'overlapping_originals': 266, 'additional_memberships': 967}, 'original population differs')
    require([r['key'] for r in index['rows']] == KEYS, 'missing, duplicated or reordered original')
    require(index['acceptance'] == ACCEPTANCE, 'fabricated receiving acceptance or authority')
    require(index['relations'] == RELATION_COUNTS, 'relation or negative pair population differs')
    require(index['reported_later_eaose_counts_only'] == PREPARED_COUNTS, 'reported prepared counts differ')
    require(dict(Counter(r['source_status'] for r in index['rows'] if r['lineage'] == 'EAOSE')) == EAOSE_STATES, 'source status population differs')
    require(index['accepted_siblings'] == SIBLINGS, 'accepted constituent identity differs')
    for row in index['rows']:
        require(row['later_prepared_target'] is None, 'unavailable prepared target invented')
        require(row['key'] == row['lineage'] + ':' + row['original_id'], 'conflated original identity')
        historical = parse(row['historical_target']['record_json_unallocated'])
        require(historical['key'] == row['key'] and historical['disposition'] == row['historical_target']['disposition'] and
            historical['source_semantic_disposition'] == row['source_status'] and
            digest(canonical(historical)) == row['historical_target']['canonical_record_sha256'], 'historical member correspondence differs')
        require(historical['source_row_sha256'] == row['intake']['canonical_record_sha256'], 'historical intake binding differs')
        require(row['accepted_constituent'] == SIBLINGS.get(row['lineage']), 'mixed accepted sibling identity')
        require(row['source_obligation']['cheap_path'] == row['continuation']['otherwise'] and
            row['source_obligation']['trigger'] == row['continuation']['reconsideration_trigger'], 'guard/next action mismatch')
        require(row['source_obligation']['criterion'] == row['continuation']['if_selected']['criterion'], 'criterion/next action mismatch')
        for loc in ('original', 'intake', 'register'):
            require(re.fullmatch('[0-9a-f]{64}', row[loc]['canonical_record_sha256']), 'missing full-record identity')
    groups = index['groups']
    require([g['id'] for g in groups] == [f'AMA-K{i:03}' for i in range(1, 33)], 'group population differs')
    member_count = Counter(k for g in groups for k in g['members'])
    require(sum(member_count.values()) == 1245 and sum(v > 1 for v in member_count.values()) == 266, 'group membership population differs')
    for group in groups:
        require(group['later_prepared_group_record'] is None, 'unavailable prepared group invented')
        original = parse(group['original_record_json_unallocated'])
        require(original['cluster_id'] == group['id'] and original['member_properties'] == group['members'] and
            digest(canonical(original)) == group['canonical_record_sha256'], 'group source correspondence differs')
        require(all(group['id'] in index_row(index, k)['groups'] for k in group['members']), 'member/group relationship differs')
    require([f['id'] for f in index['tc_findings']] == [f'TC{i:02}' for i in range(1, 13)], 'TC population differs')
    for finding in index['tc_findings']:
        original = parse(finding['record_json_unallocated'])
        require(original['parents'] == finding['parents'] and original['id'] == finding['id'] and
            original['new_normative_property_admitted'] is False, 'TC parent or novelty substitution')
    require(index['tc_findings'][9]['parents'] == TC10, 'TC10 parent substituted')
    return {'scope': 'DOCUMENTARY_INDEX_INTEGRITY_ONLY', 'originals': 278, 'eaose': 132, 'groups': 32,
        'projection_sha256': supplied, 'limit': 'Integrity is not semantic receiving; --packet gives full records. Later EAOSE/AMA target and native acceptance remain unavailable.'}


def accepted_member(root, lineage, identity):
    if lineage not in SIBLINGS:
        return None
    pin = SIBLINGS[lineage]
    path = root / pin['path']
    if not path.is_file():
        return {'availability': 'EXACT_ACCEPTED_BYTES_UNAVAILABLE_LOCALLY', 'route': pin}
    raw = path.read_bytes()
    require(len(raw) == pin['bytes'], 'accepted constituent bytes differ')
    if 'sha256' in pin:
        require(digest(raw) == pin['sha256'], 'accepted constituent digest differs')
    else:
        import hashlib
        require(hashlib.sha1(f'blob {len(raw)}\0'.encode() + raw).hexdigest() == pin['git_blob'], 'accepted constituent Git blob differs')
    document = parse(raw)
    rows = document['rows'] if lineage == 'EAA' else document['target_continuation']['rows']
    selected = [r for r in rows if r.get('id') in (identity, lineage + ':' + identity) or r.get('key') == lineage + ':' + identity or r.get('property_id') == identity]
    require(len(selected) == 1, 'accepted constituent member unresolved')
    return {'availability': 'EXACT_ACCEPTED_MEMBER_BYTES', 'route': pin, 'record': selected[0],
        'full_document_route': pin['path'], 'limit': 'This row does not replace the complete accepted qualification, failure history or relation/group records.'}


def check_source(corpus, index):
    """Bind the projected meaning and locators, not just a parallel source hash."""
    for row in index['rows']:
        key = row['key']
        record = corpus.register[key]
        n, intake = corpus.intake_by_key[key]
        expected_original = {**record['authority_locator'], 'canonical_record_sha256': digest(canonical(record['frozen_record']))}
        require(row['original'] == expected_original, 'original locator/source binding differs: ' + key)
        require(row['register'] == {'member': core.REGISTER, 'pointer': '/property_by_key/' + key,
            'canonical_record_sha256': digest(canonical(record))}, 'register source binding differs: ' + key)
        require(row['intake'] == {'member': core.INTAKE, 'pointer': f'/rows/{n}',
            'canonical_record_sha256': digest(canonical(intake))}, 'intake source binding differs: ' + key)
        expected_obligation = {'criterion': record['criterion'], 'trigger': record['trigger'],
            'cheap_path': record['non_trigger_or_cheap_path'], 'authority': record['authority'],
            'mechanism': record['mechanism'], 'assumptions': record['assumptions']}
        require(row['source_obligation'] == expected_obligation and row['continuation'] == continuation(record),
            'projected source authority, guard or action differs: ' + key)
        require(row['name'] == record['name'] and row['source_status'] == record['disposition'] and
            row['groups'] == record['cluster_ids'] and row['source_ids'] == record['source_ids'] and
            row['within_lineage_relation_ids'] == record['within_lineage_relation_ids'], 'source member meaning differs: ' + key)
        require(row['incident_direction_ids'] == [r['relation_id'] for r in corpus.incident[key]] and
            row['pair_indices'] == corpus.pair_indices[key] and row['bridge_indices'] == corpus.bridge_indices[key],
            'source member relation coverage differs: ' + key)
    for row, original in zip(index['groups'], corpus.groups):
        require(parse(row['original_record_json_unallocated']) == original, 'original group source differs')
    require(index['full_context_members'] == read_lock()['ama_members'], 'original full context routes differ')


def member_view(corpus, index, key, root=ROOT):
    row = index_row(index, key)
    record = corpus.register[key]
    require(digest(canonical(record)) == row['register']['canonical_record_sha256'], 'member source/index mismatch')
    relations = corpus.incident[key]
    reverses = {r['reverse_relation_id']: corpus.relation_by_id[r['reverse_relation_id']] for r in relations if r['reverse_relation_id']}
    opposite = {r['relation_id']: corpus.reverse_endpoints[(r['target_property'], r['source_property'])]
        for r in relations if not r['reverse_relation_id']}
    endpoint_keys = {r[field] for r in relations for field in ('source_property', 'target_property')}
    return {'scope': 'FULL_ORIGINAL_AND_GUARDED_CONTEXT; target layers separately identified', 'key': key,
        'original': corpus.resolve_original(record), 'source_register_record': record,
        'source_intake': corpus.intake_by_key[key][1],
        'bibliography': {k: corpus.sources[k] for k in record['source_ids']},
        'bibliography_limits': {k: v for k, v in corpus.load(core.SOURCES).items() if k != 'source_by_key'},
        'incident_relations': relations, 'independent_reverse_records': reverses,
        'null_reverse_opposite_endpoint_records': opposite,
        'opposite_limit': 'An independently typed opposite-endpoint record is not an asserted reciprocal. Null does not establish global absence.',
        'relation_definitions': {k: v for k, v in corpus.load(core.RELATIONS).items() if k != 'relations'},
        'explicit_pairs': [corpus.pairs[i] for i in corpus.pair_indices[key]],
        'pair_scope': {k: v for k, v in corpus.load(core.MATRIX).items() if k != 'pairs'},
        'guarded_bridges': [corpus.bridges[i] for i in corpus.bridge_indices[key]],
        'independent_endpoint_records': {k: corpus.register[k] for k in sorted(endpoint_keys)},
        'groups': [g for g in corpus.groups if key in g['member_properties']],
        'semantic_profiles': [p for p in corpus.profiles['profiles'] if key in p['member_keys']],
        'within_lineage_relations': {k: corpus.context['within_lineage_relation_by_key'][k] for k in record['within_lineage_relation_ids']},
        'lineage_full_context': corpus.context['lineage_top_level_context'][record['lineage']],
        'tensions': [t for t in corpus.load('EVOLVED_AMA_TENSION_LEDGER.json')['tensions'] if t['id'] in record['tension_ids']],
        'historical_target': parse(row['historical_target']['record_json_unallocated']),
        'historical_target_scope': row['historical_target']['scope'],
        'later_prepared_target': None, 'later_prepared_state': row['later_prepared_state'],
        'accepted_constituent': accepted_member(root, row['lineage'], row['original_id']),
        'continuation': row['continuation'], 'acceptance': index['acceptance'],
        'full_context_routes': index['full_context_members'], 'missing_input': index['missing_input']}


def require_prepared(view):
    require(view.get('later_prepared_target') is not None, 'later prepared EAOSE/AMA target unavailable; recover the exact input, not aggregate counts')


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('command', choices=['build', 'check', 'member', 'group', 'relation', 'context'])
    ap.add_argument('--index', type=Path, default=ROOT / DOC / 'r0043-member-dispositions.json')
    ap.add_argument('--packet', type=Path)
    ap.add_argument('--antecedent', type=Path)
    ap.add_argument('--key')
    ap.add_argument('--output', type=Path)
    ap.add_argument('--repo-root', type=Path, default=ROOT)
    ap.add_argument('--require-prepared', action='store_true')
    args = ap.parse_args()
    try:
        lock = read_lock()
        corpus = Corpus(args.packet, lock) if args.packet else None
        if args.command == 'build':
            require(corpus is not None and args.antecedent is not None, 'build requires --packet and --antecedent')
            result = build(corpus, lock, args.antecedent, ROOT / DOC / 'r0043-tc-source.json')
            check_index(result)
        else:
            index = read_index(args.index)
            result = check_index(index)
            if corpus is not None:
                check_source(corpus, index)
            if args.command == 'check' and corpus is not None:
                if args.antecedent:
                    require(index == build(corpus, lock, args.antecedent, ROOT / DOC / 'r0043-tc-source.json'), 'reconstruction differs')
                result['full_source_correspondence'] = 'VERIFIED_ALL_278_ORIGINALS_AND_INCIDENT_RELATIONS; not target or receiving'
            elif args.command != 'check':
                require(corpus is not None and args.key, 'this command requires --packet and --key')
                if args.command == 'member':
                    result = member_view(corpus, index, args.key, args.repo_root)
                    if args.require_prepared:
                        require_prepared(result)
                elif args.command == 'group':
                    group = next((g for g in corpus.groups if g['cluster_id'] == args.key), None)
                    require(group is not None, 'unknown group')
                    result = {'source_group': group, 'members': [index_row(index, k) for k in group['member_properties']],
                        'original_relations': [corpus.relation_by_id[k] for k in group['relation_ids']],
                        'later_prepared_group_record': None, 'acceptance': index['acceptance'],
                        'limit': 'Later mechanism-specific target controls remain unavailable. Original group membership is discovery only.'}
                elif args.command == 'relation':
                    require(args.key in corpus.relation_by_id, 'unknown relation')
                    relation = corpus.relation_by_id[args.key]
                    result = {'original': relation, 'explicit_reverse': corpus.relation_by_id.get(relation['reverse_relation_id']),
                        'opposite_endpoint_records': corpus.reverse_endpoints[(relation['target_property'], relation['source_property'])],
                        'source_member': index_row(index, relation['source_property']),
                        'target_member': index_row(index, relation['target_property']),
                        'later_target_relation': None, 'limit': 'Guarded analytical relation; not an execution prerequisite or accepted target disposition.'}
                else:
                    safe_member(args.key)
                    require(args.key in corpus.archive.namelist() and args.key.endswith(('.json', '.md')), 'context must name an existing text member')
                    raw = corpus.archive.read(args.key)
                    result = {'member': args.key, 'sha256': digest(raw), 'complete_content': parse(raw) if args.key.endswith('.json') else raw.decode(),
                        'scope': 'Complete original context bytes interpreted only within their frozen evidence ceiling.'}
        if args.output:
            if args.command == 'build':
                write_index(args.output, result)
            else:
                core.write_json(args.output, result)
        else:
            print(json.dumps(result, ensure_ascii=False, indent=2))
    except (ValueError, KeyError, IndexError, OSError, zipfile.BadZipFile) as exc:
        print('R0043 documentary reader refused: ' + str(exc), file=sys.stderr)  # canonically unallocated
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
