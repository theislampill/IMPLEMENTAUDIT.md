#!/usr/bin/env python3
"""Fixed receiver and inert revision-plan controls; no actual issuer is selected."""
import json
import re
import unittest
from unittest import mock

import windows_custody_test as custody_fixture


class OwnerSelection(unittest.TestCase):
    setUp = custody_fixture.GitObjectCustody.setUp
    git = custody_fixture.GitObjectCustody.git

    def subject(self):
        context = {'repo': self.repo, 'controller': 'c02-selection-test', 'claim_id': 'a' * 32,
                   'run_root_identity': '.IMPLEMENTAUDIT/runs/selection-test'}
        selected = {**{key: context[key] for key in ('controller', 'claim_id', 'run_root_identity')},
                    'repo': str(self.repo), 'census_owner': 'FIXTURE_ONLY_CENSUS',
                    'issuer': 'FIXTURE_ONLY_ISSUER', 'source_contract_locator': 'fixture-not-authority',
                    'owner_decision_locator': 'fixture-not-an-owner-decision'}
        request = {key: context[key] for key in ('controller', 'claim_id', 'run_root_identity')}
        request['effect'] = 'APPEND_ONLY_NO_CURRENTNESS'
        return context, selected, request

    def test_default_cannot_consume_caller_owner_labels(self):
        context, selected, request = self.subject()
        request.update(selected)
        before = self.git('for-each-ref')
        with self.assertRaisesRegex(self.claim.RotationError, 'admission unavailable'):
            self.claim._resolve_c02_source_owner_v1(context, request)
        self.assertEqual(self.git('for-each-ref'), before)

    def test_inert_plan_names_disjoint_roles_without_writing_any_ref(self):
        context, _, _ = self.subject()
        grant = {'schema': 'implementaudit.c02-issuer-grant.v1', 'issuer': 'FIXTURE_ONLY'}
        snapshot = {'schema': 'implementaudit.c02-owner-snapshot.v1', 'grant': grant}
        before = self.git('for-each-ref')
        plan = self.claim.prepare_c02_owner_revision_update_v1(context, snapshot, grant,
                                    expected_source_oid=None, expected_grant_oid=None)
        self.assertEqual(plan['authority_ceiling'], 'INERT_REVISION_PLAN_NO_EFFECT_AUTHORITY')
        self.assertEqual(self.git('for-each-ref'), before)
        registry = json.loads((custody_fixture.BASE / 'skills/implementaudit/references/canonical-state-ref-namespaces.json').read_bytes())
        for ref, (oid, expected) in plan['updates'].items():
            roles = [row for row in registry['role_patterns'] if re.fullmatch(row['fullmatch'], ref)]
            self.assertEqual(len(roles), 1)
            self.assertEqual(roles[0]['owner'], 'claim-run.sh')
            self.assertFalse(roles[0]['archive_anchor'])
            self.assertIsNone(expected)
            self.assertEqual(self.git('cat-file', '--batch-check', data=(oid + '\n').encode()).strip(),
                             (oid + ' missing').encode())

    def test_selection_scope_and_missing_revisions_refuse(self):
        context, selected, request = self.subject()
        for change in ({}, {'claim_id': 'b' * 32}, {'repo': str(self.repo.parent)},
                       {'repo': str(self.repo / '..' / self.repo.name)}, {'unexpected': 'field'}):
            with self.subTest(change=change), mock.patch.object(self.claim, '_C02_ADMITTED_OWNER_SELECTION_V1',
                                                               dict(selected, **change)):
                with self.assertRaises(self.claim.RotationError):
                    self.claim._resolve_c02_source_owner_v1(context, request)

    def test_separate_live_grant_cannot_be_substituted_by_snapshot(self):
        context, selected, request = self.subject()
        refs = self.claim._c02_owner_revision_refs_v1(context)
        grant = {'schema': 'implementaudit.c02-issuer-grant.v1', 'issuer': selected['issuer']}
        source = {'source_owner': selected['census_owner'], 'grant': grant}
        def publish(ref, value):
            oid = self.git('hash-object', '-w', '--stdin', data=self.claim.canonical(value)).decode().strip()
            self.git('update-ref', ref, oid)
            return oid
        source_oid = publish(refs['ref'], source)
        grant_oid = publish(refs['grant_ref'], grant)
        with mock.patch.object(self.claim, '_C02_ADMITTED_OWNER_SELECTION_V1', selected):
            resolved = self.claim._resolve_c02_source_owner_v1(context, request)
            self.assertEqual(resolved, dict(refs, oid=source_oid, grant_oid=grant_oid))
            publish(refs['grant_ref'], dict(grant, revoked=True))
            with self.assertRaises(self.claim.RotationError):
                self.claim._resolve_c02_source_owner_v1(context, request)
            publish(refs['grant_ref'], grant)
            publish(refs['ref'], dict(source, source_owner='FOREIGN'))
            with self.assertRaises(self.claim.RotationError):
                self.claim._resolve_c02_source_owner_v1(context, request)


if __name__ == '__main__':
    unittest.main()
