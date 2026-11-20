#!/usr/bin/env python3
"""Verify this evidence packet as inert bytes. Does not run reviewed source."""
from pathlib import Path, PurePosixPath
import hashlib
import io
import json
import zipfile


def identity(raw):
    return {'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest(),
            'git_blob': hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()}


def safe_path(name):
    path = PurePosixPath(name)
    assert not path.is_absolute() and '..' not in path.parts and '\\' not in name
    return path


def checked(raw, expected):
    observed = identity(raw)
    assert all(observed[key] == expected[key] for key in observed), 'Byte identity mismatch'
    return raw


def verify(root):
    packet = json.loads((root / 'PACKET_MANIFEST.json').read_bytes())
    assert packet['seal_excluded_from_own_population'] is True
    expected_files = {row['path'] for row in packet['files']} | {'PACKET_MANIFEST.json'}
    actual_files = {str(p.relative_to(root)) for p in root.rglob('*') if p.is_file()}
    assert actual_files == expected_files, 'Unexpected or missing publication member'
    for row in packet['files']:
        checked((root / safe_path(row['path'])).read_bytes(), row)
    assembly = json.loads((root / 'ASSEMBLY_INDEX.json').read_bytes())
    archives = {}
    for item in assembly['archives']:
        offset = 0
        chunks = []
        for ordinal, part in enumerate(item['parts']):
            assert part['ordinal'] == ordinal and part['offset'] == offset
            assert 0 < part['bytes'] <= assembly['part_bytes_maximum']
            raw = checked((root / safe_path(part['path'])).read_bytes(), part)
            chunks.append(raw)
            offset += len(raw)
        raw = checked(b''.join(chunks), item)
        archive = zipfile.ZipFile(io.BytesIO(raw))
        assert archive.testzip() is None
        assert len(archive.namelist()) == len(set(archive.namelist()))
        for name in archive.namelist():
            safe_path(name)
        assert len(archive.namelist()) == item['member_count']
        archives[item['artifact']] = archive
    assert set(archives) == {'a1', 'a3-r2', 'exact-tool-bodies', 'review-evidence'}
    evidence = archives['review-evidence']
    logical = json.loads(evidence.read('indexes/LOGICAL_MEMBER_INDEX.json'))['members']
    reviews = json.loads(evidence.read('indexes/REVIEW_SEALS.json'))['reviews']
    raw_members = json.loads(evidence.read('indexes/RAW_ARTIFACT_MEMBERS.json'))['members']
    assert len({row['path'] for row in logical}) == len(logical)
    by_name = {}
    expected_payloads = set()
    for row in logical:
        storage = row['storage']
        if storage['kind'] == 'exact-original-artifact-member':
            artifact = next(x for x in assembly['archives'] if x['artifact'] == storage['artifact'])
            assert artifact['sha256'] == storage['artifact_sha256']
            raw = archives[storage['artifact']].read(storage['member'])
        else:
            assert storage['kind'] == 'deduplicated-evidence-payload'
            expected_payloads.add(storage['member'])
            raw = evidence.read(storage['member'])
        by_name[row['path']] = checked(raw, row)
        assert Path(row['source_path']).name != 'DOWNLOAD_ACTUALS.json'
    expected_indexes = {
        'indexes/LOGICAL_MEMBER_INDEX.json', 'indexes/REVIEW_SEALS.json',
        'indexes/RAW_ARTIFACT_MEMBERS.json', 'indexes/PRIVACY_CHECK.json',
        'indexes/BASE_TREE_CLOSURE.json', 'indexes/ROOT_DECISIONS.json',
    }
    assert set(evidence.namelist()) == expected_payloads | expected_indexes
    for row in raw_members:
        checked(archives[row['artifact']].read(row['member']), row)
    for name in ('a1', 'a3-r2', 'exact-tool-bodies'):
        assert {row['member'] for row in raw_members if row['artifact'] == name} == set(archives[name].namelist())
    payload_count = 0
    for review in reviews:
        prefix = 'reviews/' + review['review'] + '/'
        seal_bytes = checked(by_name[prefix + review['seal_path']], review['seal_identity'])
        seal = json.loads(seal_bytes)
        rows = next(seal[key] for key in ('files', 'payloads', 'members')
                    if isinstance(seal.get(key), list))
        assert len(rows) == review['payload_count']
        for row in rows:
            checked(by_name[prefix + row['path']], row)
        assert {name for name in by_name if name.startswith(prefix)} == {prefix + review['seal_path']} | {prefix + row['path'] for row in rows}
        payload_count += len(rows)
    privacy = json.loads(evidence.read('indexes/PRIVACY_CHECK.json'))
    assert privacy['findings'] == []
    decisions = json.loads(evidence.read('indexes/ROOT_DECISIONS.json'))
    assert decisions['authority'] == 'ROOT_ONLY'
    for row in decisions['files']:
        checked(by_name[row['path']], row)
    result = {'status': 'PASS_DATA_ONLY_PACKET_VERIFICATION',
              'publication_files': len(expected_files),
              'raw_artifacts': 3, 'raw_artifact_file_members': len(raw_members),
              'complete_sealed_reviews': len(reviews), 'review_payload_members': payload_count,
              'logical_evidence_members': len(logical),
              'unique_evidence_payloads': len(expected_payloads),
              'root_decision_files': len(decisions['files']),
              'provider_writes': 0, 'original_runtime_executions': 0,
              'awards_by_verifier': []}
    return result


if __name__ == '__main__':
    print(json.dumps(verify(Path(__file__).resolve().parent), sort_keys=True))
