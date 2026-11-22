"""Source-only regressions for both proof consumers, original ingress, and diagnostics."""
import ast
from pathlib import Path
import json
import os
import shutil
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from source_fixture import EPISODE, desc, enc, fixture, historical_manifest, load_owner, source_manifests


def synthetic_first(p, files, size):
    """Build linked validation inputs in memory. All observation and request values are fixtures."""
    token = desc(b'SYNTHETIC FIRST HOLD')['sha256']
    original = (EPISODE/'ORIGINAL_SCOPE.json').read_bytes()
    basis = json.loads(original)
    pins = dict(schema='dg16.independent-consumer-pins.v1', source_commit=p.SOURCE, source_tree=p.TREE,
                scope_sha256=p.SCOPE_SHA, adverse_sha256=p.ADVERSE_SHA, compiler_sha256=p.COMPILER_SHA,
                owner_sha256=p.OWNER_SHA, scope_module_sha256=token, consumer_sha256=token,
                initial_control_branch='pro/synthetic-fixture')
    common = dict(source_commit=p.SOURCE, source_tree=p.TREE, authority='NONE')
    g1 = dict(common, schema='dg16.g1-live-receiving.v1', status='RECEIVED_AT_PROSPECTIVE_COMPONENT_SCOPE',
              original_G1_award=False, original_acceptance=False, actual_raw_comparison_sha256=token,
              operation_result_sha256=token, same_checkout_current=True, original_operation_complete=True,
              private_raw_publication=False)
    join = dict(common, run_id='123456', attempt=1, graph_sha256=token, dispatch_sha256=token,
                original_scope_sha256=p.SCOPE_SHA, complete_input_key=token)
    obligations = [
        dict(cell=cell, count=basis['original_population'][cell], original_ids_sha256=p.sha(p.encode(basis['original_ids'][cell])),
             consumer=consumer, condition=condition, state='RETAINED_SCOPE_NOT_EXECUTED_BY_THIS_HOST')
        for cell,consumer,condition in (
            ('DG16','DG16_ORIGINAL_RECEIVING','ACTIVE_TARGET_ORIGINAL_QUALIFICATION_REMAINS'),
            ('DG17','DG17_INTERFACE_SCOPE','INDEPENDENT_EXTERNAL_OWNER_CE057_INTERFACE_ONLY'),
            ('DG18','DG18_INTERFACE_SCOPE','INDEPENDENT_EXTERNAL_OWNER_CE051_CHANGED_INPUT_ONLY'))]
    scope = dict(join, schema='dg16.g3-host-scope-receiving.v2', selected_tracked_source_files=p.SOURCE_FILES,
                 selected_tracked_source_bytes=p.SOURCE_BYTES, node_count=14, original_total=157, selected=p.SELECTED,
                 ancestors=[p.PAIR,p.PHASE,p.ROOT], required_join=p.JOIN, root=p.ROOT, original_awards=0,
                 full_g2=p.FULL_G2, natural_transition=p.NATURAL, future_adoption='SEPARATE_GUARDED_RECEIVING_AND_OWNER_DECISION',
                 root_decision_before=p.BEFORE, result='HOST_SPECIFIC_OBLIGATION_CLOSURE_RECEIVED',
                 capacity_units='HOST_TASK_EXECUTION_SLOTS_NOT_AGENT_OR_JOB_SLOTS', host_capacity=2, operator_ceiling=2,
                 reserve=0, active_owned_task_slots=0, independence='DISJOINT_WRITERS_SHARED_SOURCE_BASELINE_NO_DOUBLE_CREDIT',
                 owner_arrangement=p.OWNER_ARRANGEMENT, observed_affinity_count=2, actual_complete_source_files=files,
                 actual_complete_source_bytes=size, received_input_bodies={k:v['sha256'] for k,v in basis['received_inputs'].items()},
                 scope_obligations=obligations)
    initial = dict(join, schema='dg16.g3-root-consumption-request.v2', source_parent=p.SOURCE_PARENT,
                   nonce='1'*32, control_branch=pins['initial_control_branch'],
                   control_path='qualification/dg16-r5-g3/ROOT_DECISION.json', root=p.ROOT, join=p.JOIN,
                   transition_sha256=token, join_sha256=token, scope_return_sha256=p.sha(p.encode(scope)),
                   g1_return_sha256=p.sha(p.encode(g1)), issued_unix_ms=1, expires_unix_ms=60001, hold_seconds=60,
                   shared_expires_unix_ms=180001, shared_window_seconds=180, returned_nodes=p.SELECTED,
                   decision_before=p.BEFORE, decision_after=p.AFTER, original_total=157, original_awards=0,
                   full_g2=p.FULL_G2, status='ROOT_REQUEST_READY')
    return p.validate_first(p.encode(initial),p.encode(scope),p.encode(g1),pins,basis,original_scope_raw=original)


def synthetic_facts(p, files, size):
    token = desc(b'SYNTHETIC ACTUAL G1 FACTS')['sha256']
    value = dict(schema='dg16.g3-g1-actual-facts.v2', source_commit=p.SOURCE, source_tree=p.TREE,
                 actual_dispatches=2, validated_actual_events=38, retained_artifacts=12,
                 original_children_exit_codes=[0,0], zero_subtracted_ns=0, producer_watchdog_seconds=120,
                 per_process_cpu_seconds=90, watchdog_events=0, cleanup_errors=0, wait4_reaped=True,
                 process_group_absent=True, runtime_physical_limit_bytes=128*1024**2,
                 source_acquisition_limit_bytes=256*1024**2, native_prerequisite_profile='DG16_8EE4_LINUX_CHANGED_NATIVE_BINDING_V1',
                 native_predicates=['fixed_receiver_identity','wrong_receiver_refusal','current_native_intake',
                                    'later_invalidation_refusal','host_and_diagnosed_intake'],
                 native_prerequisite_scope='ACTUALLY_CONSUMED_G0001_PREDICATES',
                 max_rss_scope='ACTUAL_OUTER_WAIT4_OBSERVATION_NOT_WINDOWS_WHOLE_JOB',
                 image_readback='COMPLETE_CAPTURED_SOURCE_RUNTIME_BYTES_MODES_ALIASES',
                 operation_scope='PROSPECTIVE_GENUINE_ORIGINAL19_SHARED_IMAGE_PAIR', producer_original48_qualification=False,
                 whole_DG16_awarded=False, native_prerequisite_receiving_sha256=token, raw_receiving_sha256=token,
                 producer_closing_sha256=token, maintained_elapsed_ns=1, enclosing_elapsed_ns=1,
                 measured_outer_wait4_max_rss_kib=1,runtime_mounted_bytes=1,runtime_unique_bytes=1,
                 runtime_logical_bytes=1,actual_source_files=files,actual_source_bytes=size)
    return p.bounded_g1_facts(value,dict(g1_return_sha256=token))


class ReviewControls(unittest.TestCase):
    def test_first_hold_and_bounded_facts_enforce_identical_census_ranges(self):
        proof = load_owner('proof_consumer')
        for consume in (synthetic_first, synthetic_facts):
            for files,size,valid in ((1778,167283667,True), (4096,256*1024**2,True),
                                     (1777,167283667,False), (1778,167283666,False),
                                     (4097,167283667,False), (1778,256*1024**2 + 1,False)):
                with self.subTest(consumer=consume.__name__,files=files,bytes=size):
                    if valid:
                        consume(proof, files, size)
                    else:
                        with self.assertRaisesRegex(proof.Refusal,'INTEGER_REFUSED'):
                            consume(proof, files, size)

    def test_loader_assignment_is_one_literal_and_joins_tuple_before_evaluation(self):
        operation = load_owner('operation')
        tree = ast.parse((EPISODE/'operation.py').read_bytes())
        values = [n.value for n in tree.body if isinstance(n,ast.Assign) and
                  any(isinstance(t,ast.Name) and t.id=='LOADER_SHA256' for t in n.targets)]
        self.assertEqual(len(values),1)
        name='scripts/load-work-graph-c5-executor.py'
        with self.subTest(contract='compose literal'):
            self.assertEqual(ast.literal_eval(values[0]), operation.EXECUTING_SOURCE_BINDINGS[name]['sha256'])
        with self.subTest(contract='runtime tuple'):
            with TemporaryDirectory() as tmp:
                directory=Path(tmp);(directory/'scripts').mkdir()
                body=b'SYNTHETIC invalid Python source'
                (directory/name).write_bytes(body)
                operation.LOADER_SHA256=desc(body)['sha256']
                with self.assertRaisesRegex(ValueError,'LOADER_PIN_DIFFERS'):
                    operation.load_selected(directory)

    def test_each_maintained_refusal_survives_original_diagnostic_and_public_projection(self):
        g3,driver=load_owner('g3_receiving'),load_owner('run')
        tree=ast.parse((EPISODE/'g3_receiving.py').read_bytes())
        codes={n.value for f in tree.body if isinstance(f,ast.FunctionDef) and f.name in
               ('receive_maintained_source_rows','maintained_evidence_bodies','receive_maintained_nonpackage_successor')
               for n in ast.walk(f) if isinstance(n,ast.Constant) and isinstance(n.value,str) and n.value.startswith('MAINTAINED_')}
        self.assertEqual(len(codes),24)
        with TemporaryDirectory() as temp:
            diagnostic=g3.Diagnostics(temp)
            for code in sorted(codes | {'SYNTHETIC_UNKNOWN_REFUSAL'}):
                with self.subTest(code=code):
                    expected=code if code in codes else 'UNCLASSIFIED_EXCEPTION'
                    error=g3.Refusal(code)
                    diagnostic.fail(error)
                    received=g3.validate_effect_state((Path(temp)/'G3_EFFECT_STATE.json').read_bytes())
                    state=dict(context=dict(run_id='123456',workflow_commit='a'*40),failures=[])
                    driver.record_failure(state,'cleanup',error)
                    public=driver.public_projection(state)['FAILURE.json']['failures'][0]
                    self.assertEqual((received['failure_code'],state['failures'][0]['code'],public['code']),
                                     (expected,expected,expected))


@unittest.skipUnless(os.environ.get('G132_TEST_V4_INPUT'), 'requires exact four historical scope inputs')
class OriginalIngressControl(unittest.TestCase):
    def test_actual_scope_ingress_requires_v5_and_matching_subject(self):
        original_path=Path(os.environ['G132_TEST_V4_INPUT']).resolve()
        historical=json.loads(original_path.read_bytes())
        original_scope=json.loads((EPISODE/'ORIGINAL_SCOPE.json').read_bytes())
        with TemporaryDirectory() as temp:
            directory=Path(temp)
            shutil.copyfile(EPISODE/'g3_receiving.py',directory/'g3_receiving.py')
            g3=load_owner('g3_receiving',directory)
            subject=dict(commit=g3.MAINTAINED_SOURCE_COMMIT,tree=g3.MAINTAINED_SOURCE_TREE)
            def bind(scope):
                body=enc(scope)
                (directory/'ORIGINAL_SCOPE.json').write_bytes(body)
                g3.SCOPE_SHA=desc(body)['sha256']
            (directory/'SOURCE_MANIFEST.json').write_bytes(historical_manifest())
            self.assertTrue(g3.receive_retained_package_relation(historical,original_scope,{}) ==
                            original_scope['retained_package_relation'])
            # Read the four authentic files in place. The historical records cannot enter a maintained scope.
            bind(dict(original_scope,current_subject=subject))
            with self.subTest(record='v4 in c53 scope'), self.assertRaisesRegex(g3.Refusal,'MAINTAINED_ACQUISITION_SUBJECT'):
                g3.scope_input_bodies(original_path.parent)
            source=source_manifests()
            (directory/'SOURCE_MANIFEST.json').write_bytes(enc(source[0]))
            acq,updates,bodies=fixture(*source,historical)
            scope=dict(original_scope,**updates)
            scope['received_inputs']=dict(original_scope['received_inputs'],**updates['received_inputs'])
            original_read=g3.read_file
            def check(acquisition):
                wire=enc(acquisition)
                # Only the test's synthetic current wire is supplied in memory.
                # The normal reader checks the temporary scope, actual manifest and other three real input files.
                def read(path,*args):
                    if Path(path)==original_path:
                        return wire
                    return original_read(path,*args)
                scope['received_inputs']['SOURCE_ACQUISITION.json']=desc(wire)
                bind(scope)
                with patch.object(g3,'read_file',read):
                    return g3.scope_input_bodies(original_path.parent)
            with self.subTest(record='v5 correct subject'):
                self.assertTrue(check(acq)['SOURCE_ACQUISITION.json']==bodies['SOURCE_ACQUISITION.json'])
            with self.subTest(record='v5 wrong subject'):
                with patch.object(g3,'receive_retained_package_relation',wraps=g3.receive_retained_package_relation) as dispatched:
                    with self.assertRaisesRegex(g3.Refusal,'MAINTAINED_ACQUISITION_SUBJECT'):
                        check(dict(acq,tree='0'*40))
                    dispatched.assert_not_called()


if __name__=='__main__':
    unittest.main()
