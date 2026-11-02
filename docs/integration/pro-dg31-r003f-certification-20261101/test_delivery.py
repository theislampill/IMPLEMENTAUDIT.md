#!/usr/bin/env python3
"""Discriminating controls for the new delivery consumer; no historical replay."""
import argparse
import copy
import json
from pathlib import Path
import tempfile
import unittest
import sys
sys.dont_write_bytecode = True
import verify_delivery as v

PAYLOAD = None
CERTIFICATE = None


class ManifestControls(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='dg31-integrity-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.body = b'complete supplied record\n'
        (self.root / 'record.json').write_bytes(self.body)
        self.manifest = {'schema': 'dg31.full-content-payload-manifest.v1', 'files': [
            {'path': 'record.json', 'bytes': len(self.body), 'sha256': v.digest(self.body)}]}

    def seal(self):
        data = (json.dumps(self.manifest) + '\n').encode()
        (self.root / 'MANIFEST.json').write_bytes(data)
        return v.digest(data)

    def test_complete_bytes_pass(self):
        self.assertEqual(v.verify_manifest(self.root, self.seal())['files'], 1)

    def test_wrong_manifest_anchor_refused(self):
        self.seal()
        with self.assertRaises(v.DeliveryError): v.verify_manifest(self.root, '0' * 64)

    def test_missing_primary_bytes_refused(self):
        anchor = self.seal(); (self.root / 'record.json').unlink()
        with self.assertRaises(v.DeliveryError): v.verify_manifest(self.root, anchor)

    def test_hash_only_placeholder_refused(self):
        anchor = self.seal(); (self.root / 'record.json').write_text(v.digest(self.body))
        with self.assertRaises(v.DeliveryError): v.verify_manifest(self.root, anchor)

    def test_unmanifested_extra_refused(self):
        anchor = self.seal(); (self.root / 'extra').write_text('undeclared')
        with self.assertRaises(v.DeliveryError): v.verify_manifest(self.root, anchor)

    def test_duplicate_manifest_member_refused(self):
        self.manifest['files'].append(copy.deepcopy(self.manifest['files'][0]))
        with self.assertRaises(v.DeliveryError): v.verify_manifest(self.root, self.seal())

    def test_parent_traversal_refused(self):
        self.manifest['files'][0]['path'] = '../outside'
        with self.assertRaises(v.DeliveryError): v.verify_manifest(self.root, self.seal())

    def test_duplicate_json_key_refused(self):
        data = b'{"schema":"dg31.full-content-payload-manifest.v1","files":[],"files":[]}'
        (self.root / 'MANIFEST.json').write_bytes(data)
        with self.assertRaises(v.DeliveryError): v.verify_manifest(self.root, v.digest(data))


class CertificateControls(unittest.TestCase):
    def changed(self): return copy.deepcopy(CERTIFICATE)

    def test_unmodified_certificate_passes(self):
        self.assertEqual(v.check_certificate(CERTIFICATE, PAYLOAD), 14)

    def test_forged_receiving_digest_refused(self):
        changed = self.changed(); changed['member_dispositions'][0]['bwp_accepted_record_sha256'] = '0' * 64
        with self.assertRaises(v.DeliveryError): v.check_certificate(changed, PAYLOAD)

    def test_changed_evidence_pointer_refused(self):
        changed = self.changed(); changed['original_predicates'][0]['original_full_control_ref']['json_pointer'] = '/scopes/R003F/original_controls/1'
        with self.assertRaises(v.DeliveryError): v.check_certificate(changed, PAYLOAD)

    def test_autonomy_promotion_refused(self):
        changed = self.changed(); changed['member_dispositions'][52]['prepared_state'] = 'FULLY_ABSORBED'
        with self.assertRaises(v.DeliveryError): v.check_certificate(changed, PAYLOAD)

    def test_count_preserving_member_exchange_refused(self):
        changed = self.changed(); rows = changed['member_dispositions']; rows[0], rows[1] = rows[1], rows[0]
        with self.assertRaises(v.DeliveryError): v.check_certificate(changed, PAYLOAD)

    def test_false_issue_closure_refused(self):
        changed = self.changed(); changed['issue_closed'] = True
        with self.assertRaises(v.DeliveryError): v.check_certificate(changed, PAYLOAD)

    def test_invented_external_receipt_refused(self):
        changed = self.changed(); changed['edges'][1]['receipt'] = {'result': 'PASS'}
        with self.assertRaises(v.DeliveryError): v.check_certificate(changed, PAYLOAD)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('delivery', type=Path)
    args, remaining = parser.parse_known_args()
    PAYLOAD = args.delivery.resolve() / 'payload'
    CERTIFICATE = v.read_json(Path(__file__).resolve().parent / 'CERTIFICATE.json')
    unittest.main(argv=[__file__, *remaining])
