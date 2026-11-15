#!/usr/bin/env python3
"""Focused CLI-profile source controls; constructed inputs are not admission.

Reuse the existing isolated C02 Git/claim fixture. Its initial JOIN, selection
and issuer assertions remain explicitly constructed. No native/model launch,
original task, actual owner grant or accepting C02 publication is performed.
"""
from pathlib import Path
import importlib.util
import hashlib
import json
import sys
import unittest
from unittest import mock

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('existing_c02_controls', HERE / 'c02_native_source_test.py')
existing = importlib.util.module_from_spec(spec)
spec.loader.exec_module(existing)


class ClosedCliControls(unittest.TestCase):
    blob = existing.NativeSourceControls.blob
    refs = existing.NativeSourceControls.refs
    instrument = existing.NativeSourceControls.instrument

    def setUp(self):
        existing.NativeSourceControls.setUp(self)
        self.selected = {'profile_id': 'claim-cli-controlled-nonprotected-c02-v1',
            'subject': {key: self.context[key] for key in ('controller', 'claim_id', 'run_root_identity')},
            'expected_old': self.initial,
            'receipt_token': 'CONSTRUCTED_INITIAL_JOIN_NOT_NATIVE',
            'c02_adjudication': {'census_owner': 'CONSTRUCTED_CLI_CENSUS_ONLY'},
            'event_domain': {'kind': 'CLOSED_NONPROTECTED_CLI_SUBJECT',
                'all_owner_calls_observed': True, 'covered_boundary_kinds': sorted(self.owner.BOUNDARIES),
                'covers_adjudications': True, 'unknown_ingress': 'POISON',
                'admission_locator': 'CONSTRUCTED_SOURCE_ADMISSION_NOT_PRODUCTION'}}
        self.source = self.source_owner.OwnedStdioC02CensusV1(self.selected, self.owner, self.context, None)
        joined = {'pointer_oid': self.initial['pointer'], 'marker_oid': self.initial['marker'],
                  'pointer': {'invalidation_oid': self.initial['invalidation']},
                  'receipt_token': 'CONSTRUCTED_INITIAL_JOIN_NOT_NATIVE'}
        with mock.patch.object(self.owner, 'require_current_generation_join_v1', return_value=joined):
            self.source.arm(None)
        self.source._production_binding = self.source_owner._C02_SOURCE_BINDING_SEAL_V1

    def test_actual_owned_inferred_gap_is_received_without_codex_fields(self):
        with self.instrument():
            token = self.source.inject_controlled_fault('constructed-cli-inferred-gap')
        oid = self.owner.exact_authority_token(self.context, 'invalidation', token)
        self.assertEqual(self.owner.invalidation_record(self.context, oid),
                         {'oid': oid, 'boundary': 'inferred-context-gap', 'event': 'constructed-cli-inferred-gap'})
        interval = self.source.census({})
        self.assertEqual(interval['events'], [{'sequence': 1, 'kind': 'native-boundary',
            'event_id': 'constructed-cli-inferred-gap', 'invalidation_oid': oid, 'boundary': 'inferred-context-gap'}])
        self.assertEqual(interval['covered_boundary_kinds'], sorted(self.owner.BOUNDARIES))
        self.assertTrue(interval['complete'] and interval['covers_adjudications'])
        self.assertNotIn('root_thread_id', self.selected)
        self.assertNotIn('turn_id', self.source._fence)
        self.assertEqual(self.invalidation_calls, 1)

    def unobserved_boundary(self, boundary):
        self.source.inject_controlled_fault('constructed-cli-original')
        before = self.owner.managed(self.context)
        token = self.owner.invalidate_current_generation_v1(self.context, boundary, 'constructed-unobserved-' + boundary)
        oid = self.owner.exact_authority_token(self.context, 'invalidation', token)
        # Deliberate fixture ABA: current ref equality must not hide retained ingress.
        self.owner.git(self.repo, 'update-ref', self.context['invalidation_ref'], before['invalidation'], oid)
        self.assertEqual(self.owner.managed(self.context), before)
        with self.assertRaisesRegex(ValueError, 'UNOBSERVED_CLI_BOUNDARY'):
            self.source.census_facts_v1()
        self.assertTrue(self.source._cancelled.is_set())

    def test_incomplete_return_after_real_effect_is_unknown_and_poisoned(self):
        actual = self.owner.invalidate_current_generation_v1
        def incomplete(*args, **kwargs):
            actual(*args, **kwargs)
            return ''
        with mock.patch.object(self.owner, 'invalidate_current_generation_v1', incomplete):
            with self.assertRaisesRegex(ValueError, 'OUTCOME_UNKNOWN_READBACK_REQUIRED'):
                self.source.inject_controlled_fault('constructed-cli-incomplete-output')
        self.assertTrue(self.source._cancelled.is_set())
        self.assertIsNone(self.source._original)
        self.assertNotEqual(self.owner.managed(self.context)['invalidation'], self.initial['invalidation'])

    def test_unobserved_adjudication_and_unknown_ingress_poison(self):
        self.source.inject_controlled_fault('constructed-cli-adjudication-census')
        with mock.patch.object(self.owner, '_c02_retained_decisions_v1', return_value=([({}, '6' * 40)], {})):
            with self.assertRaisesRegex(ValueError, 'UNOBSERVED_OWNER_ADJUDICATION'):
                self.source.census_facts_v1()
        self.assertTrue(self.source._cancelled.is_set())

    def test_no_fixed_selection_cannot_acquire_cli_authority(self):
        before = self.refs()
        with self.assertRaisesRegex(ValueError, 'CLI_C02_FIXED_SELECTION_REQUIRED'):
            with self.source_owner.acquire_selected_cli_c02_interval_v1(self.owner, self.context):
                self.fail('unselected source acquired an interval')
        self.assertEqual(self.refs(), before)

    def materialized_cli(self, *, unknown_template=False):
        provider = self.repo / 'constructed-cli-source-selection.json'
        decision = self.repo / 'constructed-cli-issuer.json'
        owner_path = self.scripts / 'claim-run-rotation.py'
        owner_raw = owner_path.read_bytes()
        selected = json.loads(json.dumps(self.selected))
        selected.update(schema='implementaudit.c02-closed-cli-selection.v1',
            episode_owner={'repository':str(self.repo), 'controller':self.context['controller'],
                'module_pin':{'path':str(owner_path), 'bytes':len(owner_raw),
                              'sha256':hashlib.sha256(owner_raw).hexdigest()}},
            c02_adjudication={'issuer':'CONSTRUCTED_ISSUER_ONLY', 'census_owner':'CONSTRUCTED_CLI_CENSUS_ONLY',
                'decision_path':str(decision), 'owner_decision_locator':'CONSTRUCTED_NOT_ENTITLEMENT',
                'source_contract_locator':self.selected['event_domain']['admission_locator']})
        raw = json.dumps(selected,sort_keys=True).encode()
        provider.write_bytes(raw)
        pin = {'path':str(provider),'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}
        body = existing.SOURCE.read_text().replace('OWNED_STDIO_SELECTION_PIN = None',
                                                  'OWNED_STDIO_SELECTION_PIN = '+repr(pin))
        if unknown_template:
            body += '\n# Constructed unknown template mutation.\n'
        path = self.scripts / 'compaction-source-owner-codex-app.py'
        path.write_text(body)
        module = existing.load(path, 'constructed_materialized_cli')
        joined = {'pointer_oid':self.initial['pointer'],'marker_oid':self.initial['marker'],
                  'pointer':{'invalidation_oid':self.initial['invalidation']},
                  'receipt_token':self.selected['receipt_token']}
        return module, provider, decision, joined

    def test_materialized_profile_requires_complete_explicit_domain(self):
        module, provider, _, _ = self.materialized_cli()
        selected = json.loads(provider.read_bytes())
        self.assertEqual(module.validate_cli_c02_selection_v1(selected),selected)
        for key, value in (('all_owner_calls_observed',False), ('all_owner_calls_observed',1),
                           ('covers_adjudications',False), ('covered_boundary_kinds',['manual-resume']),
                           ('admission_locator','UNSELECTED_SOURCE_CONTRACT')):
            with self.subTest(key=key,value=value):
                changed = json.loads(json.dumps(selected)); changed['event_domain'][key] = value
                with self.assertRaisesRegex(ValueError,'EVENT_DOMAIN_NOT_ADMITTED'):
                    module.validate_cli_c02_selection_v1(changed)

    def test_selected_cli_source_replacement_poison_is_physical(self):
        module, provider, _, joined = self.materialized_cli()
        # Only the initial fixture custody/JOIN is constructed; the selected
        # provider, source files and retained physical replacement are real.
        with mock.patch.object(self.owner,'verify_custody'), \
             mock.patch.object(self.owner,'require_current_generation_join_v1',return_value=joined):
            with self.assertRaises(self.owner.CustodyError):
                with module.acquire_selected_cli_c02_interval_v1(self.owner,self.context) as source:
                    replacement = provider.with_suffix('.replacement')
                    replacement.write_bytes(provider.read_bytes()); replacement.replace(provider)
                    source.verify()
            self.assertTrue(source._cancelled.is_set())

    def consumer_case(self, *, unknown_template=False, replace_issuer=False):
        module, _, decision_path, joined = self.materialized_cli(unknown_template=unknown_template)
        with mock.patch.object(self.owner,'verify_custody'), \
             mock.patch.object(self.owner,'require_current_generation_join_v1',return_value=joined):
            with module.acquire_selected_cli_c02_interval_v1(self.owner,self.context) as source:
                token = source.inject_controlled_fault('constructed-materialized-cli-fault')
                decision = {'decision_id':'constructed-append-only-scope'}
                document = {'schema':'implementaudit.c02-configured-owner-decision.v1',
                    'issuer':'CONSTRUCTED_ISSUER_ONLY','role':'CONTINUITY_ADJUDICATION_OWNER',
                    'subject':source.selected['subject'],'decision_id':decision['decision_id'],'revoked':False,
                    'qualification':'CONTROLLED_NONPROTECTED_FAULT_INJECTION',
                    'expected_old':source.expected_old,'source_cutoff':source.source_cutoff,
                    'append_grant':{},'conditional_fresh_grant':None}
                decision_path.write_text(json.dumps(document))
                runtime = (source.selected,)
                with module.selected_c02_materializer_session_v1(runtime,self.context,source) as (_,_,issuer):
                    if replace_issuer:
                        replacement = decision_path.with_suffix('.replacement')
                        replacement.write_bytes(decision_path.read_bytes()); replacement.replace(decision_path)
                        issuer.verify()
                    before = self.refs()
                    with module.OwnedStdioC02HooksV1(runtime,self.owner,self.context,token,decision,
                                                  source_owner_module=module) as operation:
                        self.assertIs(operation._active().source,source)
                        self.assertIs(operation._active().issuer,issuer)
                        with self.assertRaisesRegex(ValueError,'CLI_C02_APPEND_ONLY_PROFILE'):
                            operation.apply_conditional_successor('a'*40)
                    self.assertEqual(self.refs(),before)

    def test_actual_materialized_consumer_accepts_source_and_refuses_apply_without_effect(self):
        self.consumer_case()

    def test_unknown_materialized_template_still_refuses(self):
        with self.assertRaisesRegex(self.owner.RotationError,'shared reviewed source template'):
            self.consumer_case(unknown_template=True)

    def test_selected_configured_issuer_same_bytes_replacement_refuses(self):
        with self.assertRaises(self.owner.CustodyError):
            self.consumer_case(replace_issuer=True)


for boundary in ('host-reported-compaction', 'new-session', 'handoff-resume', 'manual-resume', 'inferred-context-gap'):
    def test(self, selected=boundary):
        self.unobserved_boundary(selected)
    setattr(ClosedCliControls, 'test_unobserved_' + boundary.replace('-', '_'), test)


class ClosedCliAppendControl(unittest.TestCase):
    """Complete real publisher path on the existing constructed semantic fixture."""
    materialized_cli = ClosedCliControls.materialized_cli

    def test_append_retry_and_subsequent_manual_boundary_use_existing_owners(self):
        sys.path.insert(0,str(HERE))
        try:
            import claim_transaction_test as transaction
        finally:
            sys.path.pop(0)
        transaction.RealHelperIntegration.setUp(self)
        self.assertEqual(transaction.RealHelperIntegration.rotate(self)['status'],'ROTATED')
        joined = self.owner.require_current_generation_join_v1(self.context)
        self.repo, self.scripts = self.fixture.repo, self.fixture.scripts
        self.initial = self.owner.managed(self.context)
        self.selected = {'profile_id':'claim-cli-controlled-nonprotected-c02-v1',
            'subject':{key:self.context[key] for key in ('controller','claim_id','run_root_identity')},
            'expected_old':self.initial,'receipt_token':joined['receipt_token'],
            'event_domain':{'kind':'CLOSED_NONPROTECTED_CLI_SUBJECT','all_owner_calls_observed':True,
                'covered_boundary_kinds':sorted(self.owner.BOUNDARIES),'covers_adjudications':True,
                'unknown_ingress':'POISON','admission_locator':'CONSTRUCTED_SOURCE_ADMISSION_NOT_PRODUCTION'}}
        module, _, decision_path, _ = self.materialized_cli()
        # Selection/issuer authority is expressly constructed. All claim, JOIN,
        # source custody, invalidation, materialization and publication calls are real.
        with module.acquire_selected_cli_c02_interval_v1(self.owner,self.context) as source:
            token = source.inject_controlled_fault('constructed-cli-full-append-fault')
            oid = token.rsplit('@',1)[1]
            observed = {'schema':'implementaudit.c02-observation.v1',**self.selected['subject'],
                'pointer_oid':joined['pointer_oid'],'marker_oid':joined['marker_oid'],
                'receipt_oid':joined['receipt_token'].rsplit('@',1)[1], 'invalidation_oid':oid,
                'event_id':'constructed-cli-full-append-fault','boundary':'inferred-context-gap','later_boundaries':[]}
            grant = {'schema':'implementaudit.c02-issuer-grant.v1','issuer':'CONSTRUCTED_ISSUER_ONLY',
                'scope':{key:observed[key] for key in ('controller','claim_id','run_root_identity',
                    'pointer_oid','receipt_oid','marker_oid','invalidation_oid','event_id')},
                'kind':'ERRONEOUS_INVALIDATION','effect':'APPEND_ONLY_NO_CURRENTNESS',
                'code_sha256':hashlib.sha256((self.scripts/'claim-run-rotation.py').read_bytes()).hexdigest(),
                'revoked':False}
            digest = lambda value: hashlib.sha256(self.owner.canonical(value)).hexdigest()
            decision = {'schema':'implementaudit.c02-decision-proposal.v1','issuer':grant['issuer'],
                'grant_sha256':digest(grant),'evidence_sha256':digest({'constructed_controlled_fault':observed}),
                'kind':'ERRONEOUS_INVALIDATION','observation_sha256':digest(observed)}
            decision['decision_id'] = digest(decision)
            decision_path.write_bytes(self.owner.canonical({
                'schema':'implementaudit.c02-configured-owner-decision.v1','issuer':grant['issuer'],
                'role':'CONTINUITY_ADJUDICATION_OWNER','subject':self.selected['subject'],
                'decision_id':decision['decision_id'],'revoked':False,
                'qualification':'CONTROLLED_NONPROTECTED_FAULT_INJECTION',
                'expected_old':source.expected_old,'source_cutoff':source.source_cutoff,
                'append_grant':grant,'conditional_fresh_grant':None}))
            runtime = (source.selected,)
            with module.selected_c02_materializer_session_v1(runtime,self.context,source):
                with module.OwnedStdioC02HooksV1(runtime,self.owner,self.context,token,decision,
                                               source_owner_module=module) as operation:
                    appended = operation.append()
                    self.assertEqual(appended['status'],'APPENDED_NO_CURRENTNESS')
                    repeated = operation.append()
                    self.assertEqual(repeated['status'],'EXACT_RETRY_NO_EFFECT')
                    self.assertEqual(repeated['record_oid'],appended['record_oid'])
                    self.assertEqual(len(self.owner._c02_retained_decisions_v1(self.context)[0]),1)
                    self.assertEqual([row['kind'] for row in source.census_facts_v1()['events']],
                                     ['native-boundary','adjudication'])
            self.assertEqual(self.owner.managed(self.context),dict(self.initial,invalidation=oid))
            with self.assertRaises(self.owner.RotationError):
                self.owner.require_current_generation_join_v1(self.context)
            self.owner.require_anchor(self.context,oid)
            self.owner.require_anchor(self.context,appended['record_oid'])
            self.assertEqual(len(self.owner.read_blob(self.repo,observed['receipt_oid']).strip().split(b'\t')),14)
        # End the closed interval before genuine newer ingress. No correction
        # fresh-currentness/apply method or new currentness writer is involved.
        newer = self.fixture.claim('--invalidate-continuity',self.context['controller'],
                                  '--boundary','manual-resume','--event','constructed-genuine-newer-cli-boundary')
        self.assertEqual(newer.returncode,0,newer.stderr.decode())
        new_oid = newer.stdout.decode().strip().rsplit('@',1)[1]
        self.assertNotEqual(new_oid,oid)
        self.assertEqual(self.owner.invalidation_record(self.context,new_oid)['boundary'],'manual-resume')


if __name__ == '__main__':
    unittest.main()
