#!/usr/bin/env python3
"""Public C02 routing and actual append mechanics with a fixture-only issuer."""
import io
import os
from types import SimpleNamespace
import unittest
from unittest import mock

import c02_publication_test as correction


class CorrectionCLI(unittest.TestCase):
    setUp = correction.CorrectionPublication.setUp
    rotate = correction.CorrectionPublication.rotate
    seed_correction = correction.CorrectionPublication.seed_correction
    digest = correction.CorrectionPublication.digest
    write_source = correction.CorrectionPublication.write_source
    write_grant = correction.CorrectionPublication.write_grant
    resolver = correction.CorrectionPublication.resolver
    fixture_owner = correction.CorrectionPublication.fixture_owner
    refs = correction.CorrectionPublication.refs

    def invoke(self, command, *arguments):
        output = io.BytesIO()
        previous = os.getcwd()
        try:
            os.chdir(self.fixture.repo)
            with mock.patch.object(self.owner.sys, 'stdout', SimpleNamespace(buffer=output)):
                self.assertEqual(self.owner.main([command, correction.CONTROLLER, *arguments]), 0)
        finally:
            os.chdir(previous)
        return self.owner.decode_json(output.getvalue().rstrip(b'\n'))

    def decision_path(self):
        path = self.fixture.run_root / 'c02-proposal.json'
        path.write_bytes(self.owner.canonical(self.decision))
        return str(path)

    def test_prepare_append_and_exact_retry_use_existing_owner(self):
        args = ('--expected-invalidation', self.event_token, '--decision', self.decision_path())
        before = self.refs()
        with self.fixture_owner():
            prepared = self.invoke('c02-prepare', *args)
            self.assertEqual(self.refs(), before)
            self.assertEqual(prepared['authority_ceiling'], 'INERT_PREPARATION_NO_EFFECT_AUTHORITY')
            first = self.invoke('c02-append', *args)
            self.assertEqual(first['status'], 'APPENDED_NO_CURRENTNESS')
            after = self.refs()
            retry = self.invoke('c02-append', *args)
            self.assertEqual(retry['record_oid'], first['record_oid'])
            self.assertEqual(retry['status'], 'EXACT_RETRY_NO_EFFECT')
            self.assertEqual(self.refs(), after)
            # The append issuer cannot authorize fresh currentness.
            with self.assertRaises(self.owner.RotationError):
                self.invoke('c02-apply', '--correction-record', first['record_oid'])
            self.assertEqual(self.refs(), after)
        with self.assertRaises(self.owner.RotationError):
            self.owner.require_current_generation_join_v1(self.context)

    def test_public_routes_refuse_unavailable_owner_without_claim_fallback(self):
        before = self.refs()
        population = sorted(str(p.relative_to(self.fixture.repo))
                            for p in self.fixture.repo.rglob('.claimed'))
        for flag in ('--prepare-c02-correction', '--append-c02-correction'):
            result = self.fixture.claim(flag, correction.CONTROLLER,
                '--expected-invalidation', self.event_token, '--decision', self.decision_path())
            self.assertNotEqual(result.returncode, 0)
            self.assertIn(b'C02 source-owner admission unavailable', result.stderr)
        result = self.fixture.claim('--apply-c02-correction', correction.CONTROLLER,
                                    '--correction-record', '0' * 40)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.refs(), before)
        self.assertEqual(sorted(str(p.relative_to(self.fixture.repo))
                                for p in self.fixture.repo.rglob('.claimed')), population)


if __name__ == '__main__':
    unittest.main()
