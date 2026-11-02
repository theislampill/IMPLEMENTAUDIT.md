#!/usr/bin/env python3
"""Read-only DG31 delivery verification. No network, native operation or issue effect.

The delivery contains payload/ plus checkpoint/. The published certificate pins
payload/MANIFEST.json. Outputs go to a caller-selected directory outside payload.
Passing proves this finite documentary reconstruction, never final adoption,
native effectiveness, issue certification authority or issue closure.
"""
import argparse
import hashlib
import importlib
import json
from pathlib import Path, PurePosixPath
import sys
sys.dont_write_bytecode = True
import tempfile


class DeliveryError(ValueError):
    pass


def digest(data):
    return hashlib.sha256(data).hexdigest()


def strict_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise DeliveryError('duplicate JSON key: ' + key)
        result[key] = value
    return result


def read_json(path):
    return json.loads(path.read_bytes(), object_pairs_hook=strict_object)


def safe_path(root, text):
    rel = PurePosixPath(text)
    if (not text or rel.is_absolute() or '..' in rel.parts or
            '\\' in text or ':' in text or rel.as_posix() != text):
        raise DeliveryError('unsafe or noncanonical manifest path')
    target = root.joinpath(*rel.parts)
    cursor = root
    for part in rel.parts:
        cursor = cursor / part
        if cursor.is_symlink():
            raise DeliveryError('symlink in required path: ' + text)
    return target


def verify_manifest(root, expected_manifest_sha256):
    if root.is_symlink() or not root.is_dir():
        raise DeliveryError('payload root must be a regular directory')
    manifest_path = root / 'MANIFEST.json'
    if manifest_path.is_symlink() or not manifest_path.is_file():
        raise DeliveryError('required manifest is absent or not regular')
    data = manifest_path.read_bytes()
    if digest(data) != expected_manifest_sha256:
        raise DeliveryError('payload manifest does not match the published certificate')
    manifest = read_json(manifest_path)
    if manifest.get('schema') != 'dg31.full-content-payload-manifest.v1':
        raise DeliveryError('unsupported payload manifest schema')
    expected = {}
    for entry in manifest['files']:
        name = entry['path']
        if name == 'MANIFEST.json' or name in expected:
            raise DeliveryError('duplicate or self manifest entry')
        target = safe_path(root, name)
        if not target.is_file():
            raise DeliveryError('required content is absent: ' + name)
        actual = target.read_bytes()
        if len(actual) != entry['bytes'] or digest(actual) != entry['sha256']:
            raise DeliveryError('required content identity mismatch: ' + name)
        expected[name] = entry
    observed = set()
    for item in root.rglob('*'):
        if item.is_symlink():
            raise DeliveryError('symlink in payload')
        if item.is_file():
            observed.add(item.relative_to(root).as_posix())
        elif not item.is_dir():
            raise DeliveryError('nonregular payload entry')
    if observed != set(expected) | {'MANIFEST.json'}:
        raise DeliveryError('payload membership differs from the manifest')
    return {'files': len(expected), 'bytes': sum(x['bytes'] for x in expected.values()),
            'manifest_sha256': digest(data)}


def verify_input_manifest(payload):
    root = payload / 'input'
    manifest = read_json(root / 'CONTENT_MANIFEST.json')
    expected_digest = '98c259951b35729e949ae8ca0e07f089058963d1346ebff4d6170be3ba38c70a'
    if digest((root / 'CONTENT_MANIFEST.json').read_bytes()) != expected_digest:
        raise DeliveryError('original handoff manifest identity changed')
    paths = []
    for entry in manifest['entries']:
        target = safe_path(root, entry['path'])
        if not target.is_file():
            raise DeliveryError('original handoff member unavailable')
        data = target.read_bytes()
        if len(data) != entry['bytes'] or digest(data) != entry['sha256']:
            raise DeliveryError('original handoff member identity changed')
        paths.append(entry['path'])
    actual = {p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file()}
    if len(paths) != len(set(paths)) or actual != set(paths) | {'CONTENT_MANIFEST.json'}:
        raise DeliveryError('original handoff population changed')
    return len(paths)


def verify_sources(payload):
    entries = read_json(payload / 'SOURCE_MANIFEST.json')['files']
    keys = set()
    for entry in entries:
        key = (entry['commit'], entry['path'])
        if key in keys:
            raise DeliveryError('duplicate immutable source identity')
        keys.add(key)
        data = safe_path(payload / 'public-source', entry['commit'] + '/' + entry['path']).read_bytes()
        blob = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
        if (len(data) != entry['bytes'] or digest(data) != entry['sha256'] or
                blob != entry['git_blob'] or entry['mode'] not in ('100644', '100755')):
            raise DeliveryError('immutable public source identity mismatch')
    return len(keys)


def check_certificate(certificate, payload):
    if certificate['schema'] != 'dg31.r003f.documentary-certificate.v1':
        raise DeliveryError('unsupported certificate schema')
    if certificate['terminal_issue_certification'] != 'BLOCKED_PENDING_EXTERNAL_RECEIPTS_AND_FINAL_EFFECTS':
        raise DeliveryError('delivery cannot promote terminal issue certification')
    if certificate['issue_closed'] or certificate['terminal_comment_posted']:
        raise DeliveryError('unperformed issue effects cannot be credited')
    edges = {r['id']: r for r in certificate['edges']}
    if edges['CE085']['receipt'] is not None or edges['CE086']['receipt'] is not None:
        raise DeliveryError('this frozen delivery contains no DG21/DG22 final receipt')
    if [r['id'] for r in certificate['original_predicates']] != (
            ['E' + str(i) for i in range(1, 7)] + ['B' + str(i) for i in range(1, 9)]):
        raise DeliveryError('original predicate denominator changed')
    primary = read_json(payload / 'input/private-primary/PROPERTY_CONTINUATION_LEDGER.json')
    receipt_root = payload / 'input/evidence/original-certification-resumption-20261031/pro-package/evidence/root_receiving'
    ebpm_receipt = read_json(receipt_root / 'EBPM_ROOT_CURRENT_RECEIVING.json')
    bwp_receipt = read_json(receipt_root / 'BWP_ROOT_CURRENT_RECEIVING.json')
    ebpm_hashes = {r['key']: r['full_record_sha256'] for r in ebpm_receipt['accepted_members']}
    bwp_hashes = {r['key']: r['full_record_sha256'] for r in bwp_receipt['accepted_members']}
    group_hashes = {r['group_id']: r['full_record_sha256'] for r in bwp_receipt['accepted_groups']}
    members = certificate['member_dispositions']
    if len(members) != 234 or [r['key'] for r in members] != [r['key'] for r in primary['properties']]:
        raise DeliveryError('certificate member population changed')
    for declared, actual in zip(members, primary['properties']):
        if (declared['original_source_status'] != actual['full_original_record']['CURRENT_STATUS'] or
                declared['prepared_state'] != actual['absorption_state'] or
                declared['target_disposition'] != actual['full_corrected_target_disposition']['disposition'] or
                declared['group_ids'] != actual['group_ids'] or declared['operative_promotion']):
            raise DeliveryError('certificate source/target/member meaning changed')
        if (declared['bwp_accepted_record_sha256'] != bwp_hashes[declared['key']] or
                declared['ebpm_accepted_record_sha256'] != ebpm_hashes.get(declared['key'])):
            raise DeliveryError('certificate member receiving digest changed')
    groups = read_json(payload / 'input/private-primary/GROUP_CONTINUATION_LEDGER.json')['groups']
    if len(certificate['group_dispositions']) != 41:
        raise DeliveryError('certificate group population changed')
    for declared, actual in zip(certificate['group_dispositions'], groups):
        if (declared['group_id'] != actual['group_id'] or
                declared['member_keys'] != actual['member_original_property_identities'] or
                declared['member_preparation_counts'] != actual['member_absorption_counts'] or
                declared['operative_promotion']):
            raise DeliveryError('certificate group meaning changed')
        if declared['accepted_record_sha256'] != group_hashes[declared['group_id']]:
            raise DeliveryError('certificate group receiving digest changed')
    cache = {}

    def verify_refs(value):
        if isinstance(value, list):
            for child in value:
                verify_refs(child)
        elif isinstance(value, dict):
            required = {'path', 'bytes', 'sha256', 'json_pointer', 'selected_value_canonical_sha256'}
            if required <= set(value):
                name = value['path']
                if name not in cache:
                    target = safe_path(payload, name)
                    data = target.read_bytes()
                    cache[name] = (data, read_json(target))
                data, selected = cache[name]
                if len(data) != value['bytes'] or digest(data) != value['sha256']:
                    raise DeliveryError('certificate evidence file identity changed')
                pointer = value['json_pointer']
                if pointer and not pointer.startswith('/'):
                    raise DeliveryError('invalid certificate evidence pointer')
                for part in pointer[1:].split('/') if pointer else []:
                    key = part.replace('~1', '/').replace('~0', '~')
                    selected = selected[int(key)] if isinstance(selected, list) else selected[key]
                canonical = json.dumps(selected, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()
                if digest(canonical) != value['selected_value_canonical_sha256']:
                    raise DeliveryError('certificate evidence pointer content changed')
            for child in value.values():
                verify_refs(child)

    verify_refs(certificate)
    return len(certificate['original_predicates'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('delivery', type=Path, help='extracted handoff directory containing payload/')
    parser.add_argument('--output', type=Path, help='new or existing empty output directory outside the delivery')
    args = parser.parse_args()
    delivery = args.delivery.resolve()
    payload = delivery / 'payload'
    certificate = read_json(Path(__file__).resolve().parent / 'CERTIFICATE.json')
    summary = {'schema': 'dg31.delivery-readback.v1', 'proof_scope': 'finite documentary content and reference reconstruction only',
               'terminal_issue_certification': False, 'native_or_causal_credit': False}
    summary['manifest'] = verify_manifest(payload, certificate['delivery']['payload_manifest_sha256'])
    summary['original_handoff_files'] = verify_input_manifest(payload)
    summary['immutable_public_files'] = verify_sources(payload)
    summary['original_predicates'] = check_certificate(certificate, payload)
    output = args.output.resolve() if args.output else Path(tempfile.mkdtemp(prefix='dg31-readback-'))
    if output == delivery or delivery in output.parents:
        raise DeliveryError('outputs must be outside the immutable delivery')
    output.mkdir(parents=True, exist_ok=True)
    if any(output.iterdir()):
        raise DeliveryError('output directory must be empty')
    import record_checks as records
    records.ROOT, records.INPUT, records.OUT = payload, payload / 'input', output
    mapping = read_json(payload / 'input' / 'EVIDENCE_PATH_MAP.json')
    records.PRIVATE_ROOT = (mapping['source_root_mapping']['workspace'].replace('\\', '/').rstrip('/') +
                            '/plans/thread9-triad-owner-andon-20260908/')
    if records.main():
        raise DeliveryError('primary-record reconstruction failed')
    public = importlib.import_module('public_record_checks')
    if public.main():
        raise DeliveryError('immutable public reference reconstruction failed')
    first = read_json(output / 'record-verification.json')
    second = read_json(output / 'public-record-verification.json')
    summary.update({'result': 'PASS_DOCUMENTARY_DELIVERY', 'primary_record_checks': first['total_checks'],
                    'public_reference_checks': second['total_checks'], 'failed_checks': [],
                    'output_directory': str(output)})
    (output / 'DELIVERY_READBACK.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (DeliveryError, KeyError, OSError, TypeError, ValueError) as error:
        print(json.dumps({'result': 'FAIL', 'error': str(error), 'terminal_issue_certification': False}), file=sys.stderr)
        raise SystemExit(1)
