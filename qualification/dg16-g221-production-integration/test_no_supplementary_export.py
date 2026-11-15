"""Focused caller controls; stubbed effects are never accepting evidence."""
import ast
import hashlib
import json
from pathlib import Path
import types
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
ADAPTER = ROOT / 'qualification/dg16-r5-full-g2/run.py'


class DirectPairCallerTests(unittest.TestCase):
    def setUp(self):
        self.module = types.ModuleType('subject')
        self.module.__file__ = str(ADAPTER)
        exec(compile(ADAPTER.read_bytes(), str(ADAPTER), 'exec'), self.module.__dict__)
        m = self.module
        self.calls = []
        self.state = {'docs': {'PROBE.json': {}}, 'controller': 'test-only',
                      'receipt': 'test-only-current-receipt', 'policy_adoption': {},
                      'native': {'current_host_request': {'test_only': True}}}
        self.runtime = types.SimpleNamespace(Refusal=m.Refusal)
        m.actual_policy_adoption = lambda _: {}
        m.write_private = lambda path, raw: self.calls.append(('private', path.name))
        m.failed_leg_public_budget = lambda *_: {'original_public_budget': True}
        m.require_native_for_pair = lambda *_: self.calls.append(('native', 'received'))
        m.checked_driver = lambda _: Path('/test-only/pair_driver.py')
        self.actual_summary_reader = m.read_pair_summary
        m.read_pair_summary = lambda *_: {'status': 'COMPLETE_PAIR_RAW_RELATION_RECORDED'}
        def forbidden(*_):
            raise AssertionError('SUPPLEMENTARY_CRYPTO_SELECTED')
        for name in ('protected_capacity', 'protected_preflight', 'protected_failed_finalize', 'protected_emit'):
            setattr(m, name, forbidden)

    def command(self, label, argv, **kwargs):
        self.calls.append(('command', label))
        if label.endswith('currentness'):
            return 0, (self.state['receipt'] + '\n').encode(), b''
        return 0, b'{}\n', b''

    def invoke(self, command=None):
        self.module.operation('pair', self.state, Path('/test-only/source'),
                              Path('/test-only/output'), {'bash': '/test-only/bash',
                              'python3': '/test-only/python3'}, self.runtime, {},
                              command or self.command)

    def test_current_host_pair_keeps_native_and_currentness_without_crypto(self):
        self.invoke()
        self.assertEqual(self.state['failed_leg_public_capacity'], {'original_public_budget': True})
        selected = [x for x in self.calls if x[0] != 'private']
        self.assertEqual(selected, [('command', 'before-pair-currentness'),
                                   ('native', 'received'),
                                   ('command', 'complete-current-registry-pair'),
                                   ('command', 'after-pair-currentness')])

    def test_matching_historical_host_still_requires_native_receiving(self):
        self.state['native']['current_host_request'] = None
        self.invoke()
        self.assertEqual(self.calls.count(('native', 'received')), 1)

    def test_missing_native_receiving_blocks_pair(self):
        def refuse(*_):
            raise self.module.Refusal('TEST_ONLY_NATIVE_NOT_RECEIVED')
        self.module.require_native_for_pair = refuse
        with self.assertRaisesRegex(self.module.Refusal, 'TEST_ONLY_NATIVE_NOT_RECEIVED'):
            self.invoke()
        self.assertNotIn(('command', 'complete-current-registry-pair'), self.calls)

    def test_changed_policy_blocks_pair(self):
        self.module.actual_policy_adoption = lambda _: {'changed': True}
        with self.assertRaisesRegex(self.module.Refusal, 'POLICY_ADOPTION_CHANGED_BEFORE_PAIR'):
            self.invoke()
        self.assertEqual(self.calls, [])

    def test_currentness_refusal_blocks_pair(self):
        with self.assertRaisesRegex(self.module.Refusal, 'MAINTAINED_OWNER_REFUSED'):
            self.invoke(lambda *_args, **_kwargs: (1, b'', b''))
        self.assertNotIn(('command', 'complete-current-registry-pair'), self.calls)

    def test_failed_pair_remains_failed_and_retains_output(self):
        def command(label, argv, **kwargs):
            result = self.command(label, argv, **kwargs)
            return (1, b'actual-test-only-failure\n', b'') if label == 'complete-current-registry-pair' else result
        with self.assertRaisesRegex(self.module.Refusal, 'FULL_PAIR_INCOMPLETE_OR_FAILED'):
            self.invoke(command)
        self.assertIn(('private', 'pair.stdout'), self.calls)
        self.assertIn(('private', 'pair.stderr'), self.calls)

    def test_no_entrypoint_invokes_supplementary_crypto(self):
        tree = ast.parse(ADAPTER.read_bytes())
        retired = {'load_protected', 'protected_capacity', 'protected_preflight',
                   'protected_failed_finalize', 'protected_emit'}
        invoked = {n.func.id for n in ast.walk(tree)
                   if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}
        self.assertFalse(retired & invoked)
        workflow = (ROOT / '.github/workflows/dg16-r5-full-g2.yml').read_text()
        self.assertNotIn('--emit-protected', workflow)
        self.assertNotIn('FAILED_STREAMS.cms', workflow)
        self.assertIn('/review/PROOF.json', workflow)
        self.assertIn('/public/ARTIFACT_MANIFEST.json', workflow)
        self.assertEqual(workflow.count(hashlib.sha256(ADAPTER.read_bytes()).hexdigest()),
                         workflow.count('adapter="$GITHUB_WORKSPACE/packet/qualification/dg16-r5-full-g2/run.py"'))


    def receiving_fixture(self):
        """Constructed false proof through the existing writer/typed reader only.

        No historical result, real source admission, publisher or host runs.
        These synthetic shape inputs never become original acceptance evidence.
        """
        directory = tempfile.TemporaryDirectory(prefix='g2-receive-retention-')
        self.addCleanup(directory.cleanup)
        output = Path(directory.name)
        pair = output / 'private/full-pair'
        evidence = pair / 'evidence'
        evidence.mkdir(parents=True)
        m = self.module
        u = m.load_utility()
        driver = m.load_adapter('pair_driver.py', m.PAIR_DRIVER_SHA, u)
        full = m.load_adapter('full_relation.py', m.FULL_RELATION_SHA, u)
        h = hashlib.sha256(b'constructed retained result').hexdigest()
        other = hashlib.sha256(b'constructed differing result').hexdigest()
        descriptor = {'bytes': 0, 'sha256': hashlib.sha256(b'').hexdigest()}
        relations = {scope: {'equal': True, 'difference_count': 0, 'witnesses': [],
            'witnesses_complete': True, 'left_projection_sha256': h,
            'right_projection_sha256': h} for scope in full.SCOPES}
        relations['whole'] = {'equal': False, 'difference_count': 1, 'witnesses_complete': True,
            'left_projection_sha256': h, 'right_projection_sha256': other,
            'witnesses': [{'kind': 'VALUE', 'location_sha256': h,
                          'left_projection_sha256': h, 'right_projection_sha256': other}]}
        proof = {'schema':'dg16.full-correspondence-proof.v1','authority':'NONE',
            'scope':'FULL_CANONICAL_REGISTERED_OPERATION_AND_DECLARED_TRANSITIVE_OUTPUTS',
            'source_commit':m.SOURCE_COMMIT,'source_tree':m.SOURCE_TREE,'policy_sha256':m.POLICY_SHA,
            'receiver_inputs_sha256':m.RELATION_INPUTS_SHA,'registry_sha256':full.REGISTRY_SHA,
            'command_stream_sha256':full.COMMAND_SHA,'mapped_nodes':119,'registered_tests':91,
            'static_report_slots':111,'static_selected_tests':2068,'same_job_raw_receiving':True,
            'raw_census_bookends_equal':True,'source_and_runtime_bookends_equal':True,
            'portal_populations':[49,49],'repro_populations':[19,19],
            'declared_evidence_roles_per_route':2,'finite_rules_unchanged':13,
            'finite_narrowings_unchanged':6,'original_acceptance':False,'full_G2':False,
            'G1':False,'G3':False,'C5':False,'canonical_conversion':False,'legacy_retirement':False,
            'test_level_authenticity_claim':False,'unexported_fixture_internal_state_equivalence_claim':False,
            'private_observations':descriptor,'actual_report_slots':{'legacy':111,'dag':111},
            'actual_report_skips':{'legacy':0,'dag':0},'actual_report_expected_failures':{'legacy':0,'dag':0},
            'relations':relations,'all_declared_relations_equal':False}
        driver.write_json(evidence / 'FULL_RELATION_PROOF.json', proof)
        driver.write_json(evidence / 'FULL_MAPPING.json', {'nodes':[{} for _ in range(119)]})
        driver.write_json(evidence / 'PHYSICAL_REGISTERED_TESTS.json', ['constructed-%d' % i for i in range(91)])
        (evidence / 'commands.bin').write_bytes(b'constructed command shape only\n')
        driver.write_json(evidence / 'RECEIVING.json', {'constructed':'not an original receiving record'})
        records = [{'mode': mode, 'exit':0,'elapsed_ms':1,'mapped_nodes':119,'registration_complete':True,
            'stdout_sha256':h if mode=='legacy' else other,'stderr_sha256':h,'registry_sha256':h,'graph_digest':h,
            'legacy_node_trace':'UNAVAILABLE_WHOLE_PROCESS_ONLY' if mode=='legacy' else 'NOT_APPLICABLE',
            'test_level_skip_semantics':'RETAINED_IN_PRIVATE_RAW_STREAMS_NO_SYNTHETIC_PASS',
            'nodes':[{'ordinal':i,'status':'UNSETTLED' if mode=='legacy' else 'PASS',
                      'terminal':mode!='legacy'} for i in range(119)]} for mode in ('legacy','dag')]
        checks = ('same_source same_registry same_environment same_record_schema same_exit same_stdout '
            'same_stderr route_pair same_engine same_execution_cwd same_compiled_stream same_child_environment '
            'same_declared_repro_artifacts same_stdin same_dist_namespace same_portal_events same_repro_events').split()
        relation = {'checks':dict(dict.fromkeys(checks,True),same_stdout=False),'raw_observables_equal':False,
            'normalization':'NONE_RAW_BYTES','authority':'NONE',
            'full_population_normalization_adopted':False,'finite_normalization_unchanged':True}
        driver.write_public_summary(pair, {'status':'COMPLETE_CURRENT_PAIR_EXECUTED_RAW_RELATION_RECORDED',
            'subject_verifier_attempts':2,'exact_registry_reassembly':True},
            {'status':'RECEIVED_COMPLETE_RAW_PAIR','records':records,'raw_relation':relation,
             'same_live_source_current':True,'ordinary_toolchain_unchanged':True})
        summary_path = pair / 'RECEIVED_PUBLIC.json'
        value = json.loads(summary_path.read_bytes())
        # Only a constructed admission flag for this typed-public-shape control.
        # No actual policy/source decision is issued or consumed by this test.
        value['full_population_normalization_adopted'] = True
        summary_path.write_bytes(m.canonical(value))
        self.assertEqual(self.actual_summary_reader(output, True, u), value)
        m.read_pair_summary = self.actual_summary_reader
        self.runtime = u
        return output, summary_path, value

    def invoke_nonzero_receive(self, output):
        def command(label, argv, **kwargs):
            self.calls.append(('command', label))
            if label == 'before-receive-currentness':
                return 0, (self.state['receipt'] + '\n').encode(), b''
            self.assertEqual(label, 'separate-maintained-sealed-receiving')
            return 1, b'constructed nonzero receiving status\n', b''
        with self.assertRaisesRegex(self.module.Refusal, '^FULL_PAIR_NOT_COMPLETELY_RECEIVED$'):
            self.module.operation('receive', self.state, Path('/test-only/source'), output,
                {'bash':'/test-only/bash','python3':'/test-only/python3'}, self.runtime, {}, command)
        self.assertEqual([row for row in self.calls if row[0] == 'command'],
            [('command','before-receive-currentness'),('command','separate-maintained-sealed-receiving')])

    def test_nonzero_receive_retains_valid_false_proof_without_acceptance(self):
        output, _, value = self.receiving_fixture()
        self.invoke_nonzero_receive(output)
        probe = self.state['docs']['PROBE.json']
        self.assertEqual(probe['result'], value)
        self.assertFalse(probe['result']['full_correspondence']['all_declared_relations_equal'])
        self.assertFalse(probe['result']['original_acceptance'] or probe['result']['full_G2'])
        self.assertEqual(probe['result_disposition'], 'VALIDATED_UNACCEPTED_NONZERO_RECEIVE')
        self.assertNotIn('receiving', probe)
        self.assertIn(('private','receive.stdout'), self.calls)
        self.assertIn(('private','receive.stderr'), self.calls)

    def test_nonzero_receive_malformed_summary_preserves_original_refusal(self):
        output, path, _ = self.receiving_fixture()
        path.write_bytes(b'{}\n')
        previous = {'status':'CONSTRUCTED_PRIOR_UNRECEIVED'}
        self.state['docs']['PROBE.json']['result'] = previous
        self.invoke_nonzero_receive(output)
        self.assertIs(self.state['docs']['PROBE.json']['result'], previous)
        self.assertNotIn('receiving', self.state['docs']['PROBE.json'])
        self.assertNotIn('result_disposition', self.state['docs']['PROBE.json'])


if __name__ == '__main__':
    unittest.main()
