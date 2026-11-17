#!/usr/bin/env python3
"""C02 projection mechanics only; no adjudicator grant or native effect claim."""
import copy
import tempfile
from pathlib import Path
import unittest

import native_resume_v2_test as N

M, H, A, F = N.M, N.H, N.A, N.F
SCHEMA = 'implementaudit.c02-correction-transition.v1'
BOUNDARY = 'erroneous-invalidation-correction'


def pure_transition(preimage):
    value = N.native_transition(preimage)
    value.update(schema_version=SCHEMA, transition_kind='c02-correction', boundary=BOUNDARY)
    return value


class CorrectionAlgebra(unittest.TestCase):
    def test_correction_is_distinct_from_native_resume_and_preserves_payload(self):
        self.assertIn(BOUNDARY, M._V2_BOUNDARIES, 'C02 fresh transition is missing')
        self.assertNotIn(BOUNDARY, M._V2_NATIVE_BOUNDARIES)
        before = N.migrated_preimage()
        result = N.project_native(before, pure_transition(before))
        self.assertEqual(result['payload'], before['payload'])
        self.assertEqual(result['transition']['continuity_epoch'], 'G0003')
        self.assertTrue(M.verify_projection_equivalence_v2(before, result)['equivalent'])
        for changes in ({'transition_kind': 'native-resume'}, {'boundary': 'manual-resume'},
                        {'schema_version': M._V2_NATIVE_RESUME_SCHEMA}, {'continuity_epoch': 'G0002'},
                        {'continuity_epoch': 'G0004'}, {'failed_transition_epoch': 'G0002'}):
            with self.subTest(changes=changes), self.assertRaises(M.ProjectionV2Error):
                N.project_native(before, dict(pure_transition(before), **changes))


class CorrectionArchive(unittest.TestCase):
    def test_anchored_decision_prepares_distinct_archive_and_finalizes_fresh_generation(self):
        self.assertTrue(callable(getattr(H, 'prepare_c02_correction_draft', None)),
                        'C02 source preparation is missing')
        with tempfile.TemporaryDirectory(prefix='r0039-c02-projection-') as temp:
            s = A.make_subject(Path(temp) / 'repo')
            first = A.prepare(s)
            first_out = H.finalize_canonical_projection(s['repo'], s['run'], first, A.transition(s, first))
            N.fixture_commit_pointer(s, first_out['pointer'])
            p = s['predecessor']
            before = H.read_canonical_generation(s['repo'], s['run'], first_out['pointer'])
            invalidation = H._anchor_object(s['repo'], p['controller'],
                ('\t'.join(('implementaudit.continuity-invalidation.v1', p['controller'],
                 p['controller_oid'], p['claim_id'], 'inferred-context-gap', 'constructed-false-gap')) + '\n').encode())
            source_oid = H._anchor_object(s['repo'], p['controller'], b'constructed source-owner census\n')
            grant_oid = H._anchor_object(s['repo'], p['controller'], b'constructed issuer grant, not production admission\n')
            record = {'schema': 'implementaudit.c02-correction-record.v1',
                'observation': {'controller': p['controller'], 'claim_id': p['claim_id'],
                    'run_root_identity': p['run_root_identity'], 'pointer_oid': p['pointer_oid'],
                    'receipt_oid': p['receipt_oid'], 'marker_oid': p['migration_marker_oid'],
                    'invalidation_oid': invalidation},
                'expected_old': {'controller': p['controller'], 'claim_id': p['claim_id'],
                    'run_root_identity': p['run_root_identity'], 'controller_oid': p['controller_oid'],
                    'pointer_oid': p['pointer_oid'], 'receipt_oid': p['receipt_oid'],
                    'receipt_ref': p['receipt_ref'], 'marker_oid': p['migration_marker_oid'],
                    'invalidation_oid': invalidation},
                'decision': {'kind': 'ERRONEOUS_INVALIDATION'}, 'source': {'oid': source_oid, 'grant_oid': grant_oid},
                'currentness': 'DISABLED_PENDING_OWNER_PROTOCOL'}
            oid = H._anchor_object(s['repo'], p['controller'], F.canonical(record))
            prepared = H.prepare_c02_correction_draft(s['repo'], s['run'], p['controller'], 'G0003', p, record)
            self.assertEqual(prepared['schema'], 'implementaudit.c02-correction-prepared.v1')
            self.assertEqual(prepared['correction_record_oid'], oid)
            self.assertEqual(prepared, H.prepare_c02_correction_draft(s['repo'], s['run'], p['controller'], 'G0003', p, record))
            manifest = H.verify_canonical_archive(s['repo'], p['controller'], prepared['archive_ref'], prepared['archive_manifest_sha256'])
            self.assertEqual(manifest['preparation_kind'], 'c02-correction')
            self.assertEqual(manifest['correction_record_oid'], oid)
            guards = H.archive_retention_guards(s['repo'], p['controller'], prepared['archive_ref'], prepared['archive_manifest_sha256'])
            self.assertEqual(guards[f"refs/implementaudit/state-archives/{p['controller']}/objects/{oid}"], oid)
            transition = N.helper_native_transition(s)
            transition.update(schema=SCHEMA, transition_kind='c02-correction', boundary=BOUNDARY)
            output = H.finalize_canonical_projection(s['repo'], s['run'], prepared, transition)
            landed = H.read_canonical_generation(s['repo'], s['run'], output['pointer'])
            self.assertEqual(landed['protected_manifest']['PRESERVED_PAYLOAD']['payload'],
                             before['protected_manifest']['PRESERVED_PAYLOAD']['payload'])
            self.assertEqual(output['pointer']['continuity_epoch'], 'G0003')
            changed = copy.deepcopy(prepared)
            changed['correction_record_oid'] = 'b' * 40
            with self.assertRaises(H.RotationError):
                H._checked_prepared(s['repo'], s['run'], changed)
            A.git(s['repo'], 'update-ref', '-d', f"refs/implementaudit/state-archives/{p['controller']}/objects/{oid}")
            with self.assertRaises(H.RotationError):
                H.verify_canonical_archive(s['repo'], p['controller'], prepared['archive_ref'], prepared['archive_manifest_sha256'])


if __name__ == '__main__':
    unittest.main()
