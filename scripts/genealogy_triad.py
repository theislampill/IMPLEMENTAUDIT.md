"""Exact compressed synthesis custody; no target adoption or archive code execution."""
import io
import json
import hashlib
import zipfile
from collections import Counter
from pathlib import Path, PurePosixPath

OCCURRENCE_INDEX = Path('docs/research/genealogy/ARCHIVE_OCCURRENCE_INDEX.json')

def sha(data):
    return hashlib.sha256(data).hexdigest()

def safe(name):
    p = PurePosixPath(name)
    if not name or p.is_absolute() or '..' in p.parts or '\\' in name or ':' in name:
        raise ValueError('unsafe archive or repository path')
    return p

def occurrences(data, outer, chain=()):
    rows = []
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        names = set()
        for info in z.infolist():
            if info.is_dir():
                continue
            safe(info.filename)
            if info.filename in names:
                raise ValueError('duplicate ZIP member')
            names.add(info.filename)
            b = z.read(info)
            rows.append({'outer_packet': outer, 'archive_chain': list(chain),
                         'member': info.filename, 'bytes': len(b), 'sha256': sha(b),
                         'content_kind': 'nested_archive' if info.filename.endswith('.zip') else Path(info.filename).suffix.lstrip('.')})
            if info.filename.endswith('.zip'):
                rows.extend(occurrences(b, outer, chain + (info.filename,)))
    return rows

def compute_triad_models(root, lock):
    models, files, all_occurrences = {}, [], []
    for packet in lock.get('trifecta_packets', []):
        safe(packet['packet_path'])
        data = (root / packet['packet_path']).read_bytes()
        if len(data) != packet['packet_bytes'] or sha(data) != packet['packet_sha256']:
            raise ValueError('trifecta packet identity mismatch: ' + packet['trifecta'])
        rows = occurrences(data, packet['packet_path'])
        all_occurrences.extend(rows)
        members = [{k: r[k] for k in ('member', 'bytes', 'sha256')} for r in rows if not r['archive_chain']]
        if members != packet['members']:
            raise ValueError('trifecta member census differs from source lock')
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            register = json.loads(z.read(packet['property_register_member']))
            prop_rows = register.get('properties', register.get('property_by_key'))
            if len(prop_rows) != packet['property_count']:
                raise ValueError('trifecta property population mismatch')
            if isinstance(prop_rows, dict):
                property_keys = set(prop_rows)
            else:
                property_keys = {r.get('global_qualified_key', r.get('key')) for r in prop_rows}
            if None in property_keys or len(property_keys) != len(prop_rows):
                raise ValueError('missing or duplicate property key')
            relations = json.loads(z.read(packet['relations_member']))['relations']
            pairs = json.loads(z.read(packet['pair_matrix_member']))['pairs']
            ids = [r.get('relation_id', r.get('id')) for r in relations]
            if None in ids or len(ids) != len(set(ids)):
                raise ValueError('missing or duplicate relation identity')
            relation_ids = set(ids)
            pair_keys = [(p.get('left_property', p.get('left_key')), p.get('right_property', p.get('right_key'))) for p in pairs]
            if len(pair_keys) != len(set(pair_keys)) or any(None in p for p in pair_keys):
                raise ValueError('missing or duplicate matrix pair identity')
            selected = [r for r in lock['lineages'] if r['trifecta'] == packet['trifecta']]
            sizes = [r['property_count'] for r in selected]
            expected_pairs = sum(a*b for i,a in enumerate(sizes) for b in sizes[i+1:])
            if len(pairs) != expected_pairs:
                raise ValueError('complete Cartesian pair denominator mismatch')
            groups = [[k for k in property_keys if k.startswith(r['triad_alias']+':')] for r in selected]
            expected_pair_keys = {frozenset((a,b)) for i,g in enumerate(groups) for g2 in groups[i+1:] for a in g for b in g2}
            if {frozenset(p) for p in pair_keys} != expected_pair_keys:
                raise ValueError('Cartesian pair identity coverage mismatch')
            if any(r['source_property'] not in property_keys or r['target_property'] not in property_keys for r in relations):
                raise ValueError('relation endpoint absent')
            if any(rid not in relation_ids for p in pairs for rid in p['directional_relation_ids']):
                raise ValueError('dangling pair-to-relation locator')
            guard_key = {'sss':'scope_trigger_comparison', 'bwp':'trigger_scope_comparison', 'ama':'trigger_and_scope_comparison'}[packet['trifecta']]
            if any(not r.get(guard_key) for r in relations):
                raise ValueError('relation guard absent')
            for lineage in selected:
                origin = lineage['source_occurrence']
                if origin['outer_packet_path'] != packet['packet_path'] or sha(z.read(origin['member'])) != lineage['packet_sha256'] or origin['sha256'] != lineage['packet_sha256']:
                    raise ValueError('selected constituent occurrence identity mismatch')
            counts = {'selected_properties':len(prop_rows), 'directional_relations_including_unresolved':len(relations),
                      'complete_pairs':len(pairs), 'pair_statuses':dict(sorted(Counter(p.get('relation_status',p.get('status')) for p in pairs).items())),
                      'relation_rows_with_source_guards':len(relations), 'outer_members':len(members), 'recursive_member_occurrences':len(rows)}
        manifest = {'schema':'engineering-genealogy-trifecta-manifest-v1', 'trifecta':packet['trifecta'],
                    'authority_boundary':'Neutral custody; retained analytical guards and evidence limits do not establish target applicability, runtime behavior, currentness or release.',
                    'storage':packet['storage'], 'packet':{'path':packet['packet_path'], 'bytes':len(data), 'sha256':sha(data), 'identity_kind':'RAW_DELIVERED_ZIP_BYTES'},
                    'members':members, 'counts':counts,
                    'identity_note':'Embedded content/normalized digests keep their source scope. Exact raw ZIP digests above do not reinterpret them.'}
        models[root / f"docs/research/genealogy/{packet['trifecta']}/TRIFECTA_MANIFEST.json"] = manifest
        files.append({'role':'frozen_trifecta_packet', 'path':packet['packet_path'], 'bytes':len(data), 'sha256':sha(data)})
    if lock.get('trifecta_packets'):
        models[root / OCCURRENCE_INDEX] = {'schema':'engineering-genealogy-archive-occurrences-v1',
            'scope':'All recursively nested file occurrences in the three new exact outer packets; no identity deduplication or study-independence claim.',
            'occurrences':all_occurrences, 'counts':{'member_occurrences':len(all_occurrences), 'unique_member_byte_hashes':len({r['sha256'] for r in all_occurrences})}}
    return models, files
