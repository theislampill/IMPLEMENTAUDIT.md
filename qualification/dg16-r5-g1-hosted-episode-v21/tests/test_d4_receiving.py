"""Offline controls for the conditional existing-artifact D4 receiving path.

All authority records are synthetic fixtures from the original D4 tests. The
real policy pins are checked separately; fixture policies remain synthetic. No hosted/native operation runs.
"""
import copy
import contextlib
import hashlib
import importlib.util
import io
import json
import sys
import types
from pathlib import Path
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
OP = ROOT
sys.path.insert(0, str(ROOT / 'tests'))
import test_host_profile_binding as first


def load(path, name, **values):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    module.__dict__.update(values)
    spec.loader.exec_module(module)
    return module


class Receiving(unittest.TestCase):
    def setUp(self):
        self.fixture = first.ProfileBinding('test_positive_returns_actual_bodies_and_passes_unchanged_c_validator')
        self.fixture.setUp(); self.addCleanup(self.fixture.doCleanups)
        self.produced = self.fixture.prepare()
        self.consumer = load(OP / 'packet/proof_consumer.py', 'conditional_d4_consumer',
                             _HOST_PROFILE_OWNER=self.fixture.owner)
        self.assertTrue(hasattr(self.consumer, 'validate_host_profile_evidence'),
                        'Independent D4 body consumption is not implemented')
        self.pins = json.loads((OP / 'packet/INDEPENDENT_PROOF_PINS.json').read_bytes())
        self.pins['host_profile_policy'] = first.pin(self.produced['evidence']['adoption'])
        self.packet = dict(schema='dg16.g1-prospective-host-profile-evidence.v1',
            binding=first.pin(first.wire(self.produced['binding'])),
            observation_body=self.produced['evidence']['observation'].decode('ascii'),
            policy_body=self.produced['evidence']['adoption'].decode('ascii'))

    def receive(self, **kwargs):
        return self.consumer.validate_host_profile_evidence(self.packet, self.pins,
            run_id=kwargs.get('run_id', self.fixture.context['run_id']), observed_before=1600)

    def refuse(self, code):
        with self.assertRaisesRegex(self.consumer.Refusal, '^' + code + '$'):
            self.receive()

    def test_positive_consumer_recovers_the_exact_two_raw_bodies_and_binding(self):
        result = self.receive()
        self.assertEqual(result['binding'], self.produced['binding'])
        self.assertEqual(result['observation_raw'], self.produced['evidence']['observation'])
        self.assertEqual(result['policy_raw'], self.produced['evidence']['adoption'])

    def test_unissued_independent_policy_pin_refuses_even_with_self_describing_bodies(self):
        self.pins['host_profile_policy'] = None
        self.refuse('HOST_PROFILE_POLICY_UNISSUED')

    def test_missing_body_refuses(self):
        del self.packet['observation_body']
        self.refuse('CLOSED_SCHEMA_REFUSED')

    def test_tampered_policy_body_refuses(self):
        self.packet['policy_body'] += ' '
        self.refuse('HOST_PROFILE_POLICY_PIN_REFUSED')

    def test_wrong_independently_trusted_policy_pin_refuses(self):
        self.pins['host_profile_policy']['sha256'] = '0' * 64
        self.refuse('HOST_PROFILE_POLICY_PIN_REFUSED')

    def test_wrong_run_refuses_even_if_all_body_descriptors_are_consistent(self):
        with self.assertRaisesRegex(self.consumer.Refusal, '^HOST_PROFILE_RUN_REFUSED$'):
            self.receive(run_id='987654321')

    def test_oversize_body_refuses_before_json_processing(self):
        self.packet['observation_body'] = 'x' * 4097
        self.refuse('HOST_PROFILE_BODY_BOUND_REFUSED')

    def test_tampered_observation_cannot_match_prepare_binding(self):
        value = json.loads(self.packet['observation_body'])
        value['host_identity']['boot_id'] = first.OTHER_BOOT.decode().strip()
        self.packet['observation_body'] = first.wire(value).decode('ascii')
        self.refuse('HOST_PROFILE_PREPARE_BINDING_REFUSED')

    def test_observation_of_a_different_source_refuses(self):
        value = json.loads(self.packet['observation_body']); value['source_commit'] = 'f' * 40
        self.packet['observation_body'] = first.wire(value).decode('ascii')
        self.refuse('SOURCE_IDENTITY_REFUSED')

    def test_noncanonical_observation_refuses(self):
        self.packet['observation_body'] = json.dumps(json.loads(self.packet['observation_body']))
        self.refuse('CANONICAL_BYTES_REFUSED')

    def test_later_receiving_does_not_pretend_to_renew_expired_prepare_policy(self):
        with mock.patch.object(self.consumer.time, 'time', return_value=10.0):
            self.assertEqual(self.receive()['policy_raw'], self.produced['evidence']['adoption'])

    def test_delivered_independent_pin_binds_actual_issued_policy(self):
        pins = json.loads((OP / 'packet/INDEPENDENT_PROOF_PINS.json').read_bytes())
        self.assertEqual(pins['host_profile_policy'], first.pin((OP / 'entry/G1_HOST_PROFILE_POLICY.json').read_bytes()))
        self.consumer.pins_contract(pins)

    def request_bodies(self):
        c = self.consumer
        scope_raw = (OP / 'packet/ORIGINAL_SCOPE.json').read_bytes()
        basis = json.loads(scope_raw)
        g1 = dict(schema='dg16.g1-live-receiving.v1', authority='NONE', source_commit=c.SOURCE, source_tree=c.TREE,
            status='RECEIVED_AT_PROSPECTIVE_COMPONENT_SCOPE', original_G1_award=False, original_acceptance=False,
            actual_raw_comparison_sha256='a' * 64, operation_result_sha256='b' * 64,
            same_checkout_current=True, original_operation_complete=True, private_raw_publication=False)
        request = dict(schema='dg16.g3-root-consumption-request.v3', authority='NONE', source_commit=c.SOURCE,
            source_tree=c.TREE, source_parent=c.SOURCE_PARENT, run_id=self.fixture.context['run_id'], attempt=1,
            nonce='a' * 32, control_branch=self.pins['initial_control_branch'],
            control_path='qualification/dg16-r5-g3/ROOT_DECISION.json', root=c.ROOT, join=c.JOIN,
            original_scope_sha256=c.SCOPE_SHA, graph_sha256='1' * 64, dispatch_sha256='2' * 64,
            transition_sha256='3' * 64, join_sha256='4' * 64, scope_return_sha256=None,
            g1_return_sha256=first.pin(first.wire(g1))['sha256'], complete_input_key='7' * 64,
            returned_nodes=c.SELECTED, issued_unix_ms=1600, expires_unix_ms=6001600, hold_seconds=6000,
            shared_expires_unix_ms=13201600, shared_window_seconds=13200,
            decision_before=c.BEFORE, decision_after=c.AFTER, original_total=157, original_awards=0,
            full_g2=c.FULL_G2, status='ROOT_REQUEST_READY', host_profile_evidence=copy.deepcopy(self.packet))
        obligations = [dict(cell=cell, count=basis['original_population'][cell],
            original_ids_sha256=first.pin(first.wire(basis['original_ids'][cell]))['sha256'],
            consumer=consumer, condition=condition, state='RETAINED_SCOPE_NOT_EXECUTED_BY_THIS_HOST')
            for cell, consumer, condition in [('DG16','DG16_ORIGINAL_RECEIVING','ACTIVE_TARGET_ORIGINAL_QUALIFICATION_REMAINS'),
                ('DG17','DG17_INTERFACE_SCOPE','INDEPENDENT_EXTERNAL_OWNER_CE057_INTERFACE_ONLY'),
                ('DG18','DG18_INTERFACE_SCOPE','INDEPENDENT_EXTERNAL_OWNER_CE051_CHANGED_INPUT_ONLY')]]
        scope = dict(schema='dg16.g3-host-scope-receiving.v2', authority='NONE', source_commit=c.SOURCE, source_tree=c.TREE,
            run_id=request['run_id'], attempt=1, graph_sha256=request['graph_sha256'], dispatch_sha256=request['dispatch_sha256'],
            complete_input_key=request['complete_input_key'], original_scope_sha256=c.SCOPE_SHA,
            selected_tracked_source_files=c.SOURCE_FILES, selected_tracked_source_bytes=c.SOURCE_BYTES,
            node_count=14, original_total=157, selected=c.SELECTED, ancestors=[c.PAIR,c.PHASE,c.ROOT],
            required_join=c.JOIN, root=c.ROOT, original_awards=0, full_g2=c.FULL_G2,
            natural_transition=c.NATURAL, future_adoption='SEPARATE_GUARDED_RECEIVING_AND_OWNER_DECISION',
            root_decision_before=c.BEFORE, result='HOST_SPECIFIC_OBLIGATION_CLOSURE_RECEIVED',
            capacity_units='HOST_TASK_EXECUTION_SLOTS_NOT_AGENT_OR_JOB_SLOTS', host_capacity=2, operator_ceiling=2,
            reserve=0, active_owned_task_slots=0, independence='DISJOINT_WRITERS_SHARED_SOURCE_BASELINE_NO_DOUBLE_CREDIT',
            owner_arrangement=c.OWNER_ARRANGEMENT, observed_affinity_count=2, actual_complete_source_files=1982,
            actual_complete_source_bytes=175292551, received_input_bodies={k:v['sha256'] for k,v in basis['received_inputs'].items()},
            scope_obligations=obligations)
        request['scope_return_sha256'] = first.pin(first.wire(scope))['sha256']
        return request, scope, g1, basis, scope_raw

    def test_actual_first_request_consumer_accepts_and_consumes_body_chain(self):
        request, scope, g1, basis, original = self.request_bodies()
        values = self.consumer.validate_first(first.wire(request), first.wire(scope), first.wire(g1),
            self.pins, basis, original_scope_raw=original)
        self.assertEqual(values[0]['host_profile_evidence'], self.packet)

    def test_actual_first_request_consumer_refuses_wrong_policy_chain(self):
        request, scope, g1, basis, original = self.request_bodies()
        request['host_profile_evidence']['policy_body'] += ' '
        with self.assertRaisesRegex(self.consumer.Refusal, '^HOST_PROFILE_POLICY_PIN_REFUSED$'):
            self.consumer.validate_first(first.wire(request), first.wire(scope), first.wire(g1),
                self.pins, basis, original_scope_raw=original)

    def test_independent_readback_checks_actual_callback_bytes(self):
        request = self.request_bodies()[0]
        self.assertTrue(hasattr(self.consumer, 'verify_host_profile_readback'), 'D4 readback is not integrated')
        called = []
        def actual():called.append(True);return copy.deepcopy(self.packet)
        result = self.consumer.verify_host_profile_readback({'host_profile_evidence': actual}, request, self.pins)
        self.assertEqual(called, [True]);self.assertEqual(result, first.pin(first.wire(self.packet)))
        changed = copy.deepcopy(self.packet);changed['binding']['sha256'] = '0' * 64
        with self.assertRaises(self.consumer.Refusal):
            self.consumer.verify_host_profile_readback({'host_profile_evidence': lambda: changed}, request, self.pins)

    def test_request_alone_cannot_substitute_for_live_callback(self):
        with self.assertRaisesRegex(self.consumer.Refusal, '^HOST_PROFILE_READBACK_REQUIRED$'):
            self.consumer.verify_host_profile_readback({}, self.request_bodies()[0], self.pins)

    def test_extra_private_fields_cannot_be_exported(self):
        self.packet['episode_body'] = 'PRIVATE_SENTINEL'
        self.refuse('CLOSED_SCHEMA_REFUSED')

    def test_old_request_schema_cannot_silently_acquire_new_semantics(self):
        request,scope,g1,basis,original = self.request_bodies()
        request['schema'] = 'dg16.g3-root-consumption-request.v2'
        with self.assertRaisesRegex(self.consumer.Refusal, '^INITIAL_SCHEMA_REFUSED$'):
            self.consumer.validate_first(first.wire(request),first.wire(scope),first.wire(g1),
                self.pins,basis,original_scope_raw=original)

    def new_core(self):
        return load(OP / 'packet/run.py', 'conditional_d4_core')

    def retained_episode(self):
        output = self.fixture.output
        (output / 'private').mkdir(parents=True)
        state = dict(host_profile_binding=self.produced['binding'],
            host_profile_evidence={k:v.decode('ascii') for k,v in self.produced['evidence'].items()})
        (output / 'private/episode.json').write_bytes(first.wire(state))
        return state

    def core_profile_boundary(self, core):
        return [mock.patch.object(core, 'independent_consumer_inputs', return_value=(self.consumer,self.pins,None,None)),
                mock.patch.object(core, 'load_module', side_effect=lambda name: self.fixture.owner if name=='host_utility' else self.fail(name)),
                mock.patch.object(core, 'host_context', return_value=copy.deepcopy(self.fixture.context)),
                mock.patch.object(core, 'read_boot_identity', return_value=first.BOOT)]

    def test_core_reads_retained_bodies_without_new_files_and_revalidates_live_binding(self):
        core = self.new_core();state = self.retained_episode()
        self.assertTrue(hasattr(core, 'host_profile_public_evidence'), 'Core D4 readback is not integrated')
        for patch in self.core_profile_boundary(core):patch.start();self.addCleanup(patch.stop)
        before = list(self.fixture.output.rglob('*'))
        actual = core.host_profile_public_evidence(state,self.fixture.source,self.fixture.output)
        self.assertEqual(actual,self.packet);self.assertEqual(list(self.fixture.output.rglob('*')),before)
        with mock.patch.object(core, 'read_boot_identity', return_value=first.OTHER_BOOT):
            with self.assertRaisesRegex(ValueError, '^HOST_PROFILE_CHANGED$'):
                core.host_profile_public_evidence(state,self.fixture.source,self.fixture.output)

    def test_core_refuses_changed_retained_episode_at_closing(self):
        core = self.new_core();state = self.retained_episode()
        for patch in self.core_profile_boundary(core):patch.start();self.addCleanup(patch.stop)
        raw=first.wire(state)
        with mock.patch.object(core,'read_regular',side_effect=[raw,raw+b' ']):
            with self.assertRaisesRegex(core.Refusal,'^D4_RETAINED_CLOSING_CHANGED$'):
                core.host_profile_public_evidence(state,self.fixture.source,self.fixture.output)

    def test_first_request_transport_keeps_original_bound(self):
        g3=load(OP / 'packet/g3_receiving.py','d4_bounded_g3')
        request=self.request_bodies()[0]
        self.assertEqual(g3.validate_public_request(first.wire(request)),request)
        request['host_profile_evidence']['observation_body']='x'*4097
        with self.assertRaisesRegex(g3.Refusal,'^PUBLIC_PROFILE_BODY_BOUND$'):
            g3.validate_public_request(first.wire(request))

    def test_real_root_request_export_preserves_four_existing_members_and_exact_bodies(self):
        core = self.new_core();request,scope,g1,basis,original = self.request_bodies()
        g3 = load(OP / 'packet/g3_receiving.py','conditional_d4_g3')
        # The proposal contains changed files only. The real scope validator
        # reads its unchanged, exact C sibling from the retained reference.
        g3.__file__ = str(OP / 'packet/g3_receiving.py')
        output = self.fixture.output;(output/'private').mkdir(parents=True)
        state = dict(failed=False,completed=['g3-receive'],operation_received=True)
        records = {'episode.json':state,'G3_ROOT_REQUEST.json':request,'G3_SCOPE_RECEIVING.json':scope,'RECEIVING.json':g1}
        for name,value in records.items():(output/'private'/name).write_bytes(first.wire(value))
        with mock.patch.object(core,'load_module',return_value=g3), mock.patch.object(core,'independent_consumer_inputs',
                return_value=(self.consumer,self.pins,basis,original)),contextlib.redirect_stdout(io.StringIO()):
            core.emit_root_request(output)
        names = {p.name for p in (output/'public-request').iterdir()}
        self.assertEqual(names,{'ROOT_REQUEST.json','SCOPE_RECEIVING.json','G1_RECEIVING.json','ARTIFACT_MANIFEST.json'})
        delivered = json.loads((output/'public-request/ROOT_REQUEST.json').read_bytes())['host_profile_evidence']
        self.assertEqual(delivered['observation_body'].encode('ascii'),self.produced['evidence']['observation'])
        self.assertEqual(delivered['policy_body'].encode('ascii'),self.produced['evidence']['adoption'])
        self.assertLessEqual((output/'public-request/ROOT_REQUEST.json').stat().st_size,8192)

    def test_bad_policy_refuses_before_any_public_request_file_is_created(self):
        core=self.new_core();request,scope,g1,basis,original=self.request_bodies()
        g3=load(OP / 'packet/g3_receiving.py','d4_bad_export_g3')
        g3.__file__=str(OP / 'packet/g3_receiving.py')
        self.pins['host_profile_policy']['sha256']='0'*64
        output=self.fixture.output;(output/'private').mkdir(parents=True)
        for name,value in {'episode.json':dict(failed=False,completed=['g3-receive'],operation_received=True),
            'G3_ROOT_REQUEST.json':request,'G3_SCOPE_RECEIVING.json':scope,'RECEIVING.json':g1}.items():
            (output/'private'/name).write_bytes(first.wire(value))
        with mock.patch.object(core,'load_module',return_value=g3),mock.patch.object(core,'independent_consumer_inputs',
                return_value=(self.consumer,self.pins,basis,original)),contextlib.redirect_stdout(io.StringIO()):
            with self.assertRaisesRegex(self.consumer.Refusal,'^HOST_PROFILE_POLICY_PIN_REFUSED$'):
                core.emit_root_request(output)
        self.assertFalse((output/'public-request').exists())
        self.assertFalse((output/'ROOT_REQUEST_ELIGIBLE').exists())

    def run_changed_execute_path(self, callback, on_receipt):
        """Exercise the actual new execute/readback ordering, not native proof.

        Existing compiler/G1/M4/custody inputs are controlled boundary fixtures.
        The real D4 body validator, callback checks, ordering and receipt draft
        execute. Stop at the unchanged receipt validator; no receipt is issued.
        """
        c=self.consumer;request,_,_,_,scope_raw=self.request_bodies()
        request_raw=first.wire(request);source=self.fixture.source;private=self.fixture.output/'private'
        run_name='.IMPLEMENTAUDIT/runs/r5-g1-hosted-ABC123'
        (source/run_name).mkdir(parents=True);private.mkdir(parents=True)
        compiler_raw=(b'import contextlib\n@contextlib.contextmanager\n'
                      b'def observe_native_run_sources_v2(*a,**k):\n    yield b"{}\\n"\n')
        owner_raw=b'offline unchanged-owner boundary fixture\n'
        pin_record=copy.deepcopy(self.pins)
        pin_record.update(compiler_sha256=c.sha(compiler_raw),owner_sha256=c.sha(owner_raw),
                          consumer_sha256=c.sha((OP / 'packet/proof_consumer.py').read_bytes()))
        class Population:
            def __init__(self,*args):self.total=0
            def read(self,key,path,**kwargs):
                raw={'initial':request_raw,'initial_request':request_raw,'compiler':compiler_raw,'owner':owner_raw,
                     'consumer':(OP / 'packet/proof_consumer.py').read_bytes(),
                     'original_scope':scope_raw}.get(key,b'{}\n')
                self.total+=len(raw);return raw
            def close(self):return {'fixture_boundary':True}
        api=dict(source=source,private=private,run_root=run_name,controller='r5-g1-hosted-'+request['run_id']+'-a1',
            receipt='offline-boundary-only',deadline_monotonic=c.time.monotonic()+17400,
            require_current=lambda _:None,verify_g1_retained=lambda:c.sha(b'{}\n'),host_profile_evidence=callback)
        checked=dict(initial=request,selected_run_root=run_name,selected={'digest':'1'*64},
                     current={'digest':'2'*64},final_wrapper={})
        patches=[mock.patch.object(c,'COMPILER_SHA',c.sha(compiler_raw)),mock.patch.object(c,'OWNER_SHA',c.sha(owner_raw)),
                 mock.patch.object(c,'Population',Population),mock.patch.object(c,'receive_retained_m4',return_value={}),
                 mock.patch.object(c,'check_bodies',return_value=checked),mock.patch.object(c,'native_identity'),
                 mock.patch.object(c,'validate_receipt',side_effect=on_receipt),
                 mock.patch.object(c,'write_once',side_effect=AssertionError('no fixture receipt may be issued')),
                 mock.patch.object(c,'bounded_timer',side_effect=lambda _:contextlib.nullcontext())]
        patches.extend(mock.patch.object(c.os,name,return_value=0) for name in ('getuid','geteuid','getgid','getegid'))
        with contextlib.ExitStack() as stack:
            for patch in patches:stack.enter_context(patch)
            c.execute(api,pin_record)

    def test_execute_opening_readback_refusal_prevents_receipt_draft(self):
        calls=[]
        def bad():calls.append(True);return None
        with self.assertRaisesRegex(self.consumer.Refusal,'^CLOSED_SCHEMA_REFUSED$'):
            self.run_changed_execute_path(bad,AssertionError('must not draft receipt'))
        self.assertEqual(calls,[True])

    def test_execute_closing_readback_change_prevents_receipt_draft(self):
        changed=copy.deepcopy(self.packet);observation=json.loads(changed['observation_body'])
        observation['observed_unix_ms']=1501;changed['observation_body']=first.wire(observation).decode('ascii')
        binding=copy.deepcopy(self.produced['binding']);binding['observation']=first.pin(first.wire(observation))
        changed['binding']=first.pin(first.wire(binding));calls=[]
        def readback():calls.append(True);return copy.deepcopy(self.packet) if len(calls)==1 else changed
        with self.assertRaisesRegex(self.consumer.Refusal,'^HOST_PROFILE_READBACK_CHANGED$'):
            self.run_changed_execute_path(readback,AssertionError('must not draft receipt'))
        self.assertEqual(calls,[True,True])

    def test_execute_records_predicate_only_after_both_actual_readbacks(self):
        class ReachedExistingReceiptValidator(Exception):pass
        calls=[];drafts=[]
        def readback():calls.append(True);return copy.deepcopy(self.packet)
        def inspect(raw,*args,**kwargs):
            self.assertEqual(calls,[True,True]);drafts.append(json.loads(raw))
            raise ReachedExistingReceiptValidator
        with self.assertRaises(ReachedExistingReceiptValidator):
            self.run_changed_execute_path(readback,inspect)
        self.assertEqual(drafts[0]['schema'],'dg16.independent-proof-consumption-receipt.v3')
        self.assertEqual(drafts[0]['predicate_results']['D4_PREPARE_BODY_CHAIN_AND_LIVE_HOST_READBACKS'],'OBSERVED_TRUE')
        self.assertEqual(drafts[0]['original_awards'],[])


class ExternalCheckoutReader(unittest.TestCase):
    def setUp(self):
        self.fixture=first.ProfileBinding('test_positive_returns_actual_bodies_and_passes_unchanged_c_validator')
        self.fixture.setUp();self.addCleanup(self.fixture.doCleanups)
        self.entry=load(OP / 'entry/core_prepare_entry.py','d4_external_entry')
        self.assertTrue(hasattr(self.entry,'read_external'),'External checkout reader is not implemented')
        self.selector=load(OP / 'packet/public_inputs.py','exact_c_checkout_reader')
        self.assertEqual(hashlib.sha256((OP / 'packet/public_inputs.py').read_bytes()).hexdigest(),
                         'deaaa65887202be00e0f1f70931cd3449222469faa5d8568699ad5e9d8943984')
        self.directory=self.fixture.workspace/'packet/qualification/dg16-r5-g1-hosted-episode-v21/entry'
        self.directory.mkdir(parents=True)
        self.entry.__file__=str(self.directory/'core_prepare_entry.py')
        self.core=types.SimpleNamespace(load_module=lambda name:self.selector if name=='public_inputs' else self.fail(name))
        self.raw=b'exact offline helper body\n';self.path=self.directory/'host_profile_binding.py';self.path.write_bytes(self.raw)
        self.digest=hashlib.sha256(self.raw).hexdigest()

    def test_accepts_exact_runner_owned_external_body_without_changing_custody(self):
        before=self.path.stat()
        self.assertEqual(self.entry.read_external(self.core,'host_profile_binding.py',65536,self.digest),self.raw)
        after=self.path.stat()
        self.assertEqual((before.st_uid,before.st_gid,before.st_mode,before.st_ino),
                         (after.st_uid,after.st_gid,after.st_mode,after.st_ino))

    def test_wrong_external_pin_refuses(self):
        with self.assertRaisesRegex(ValueError,'^PREPARE_EXTERNAL_BODY_PIN$'):
            self.entry.read_external(self.core,'host_profile_binding.py',65536,'0'*64)

    def test_nonfixed_checkout_refuses_before_reading(self):
        self.entry.__file__=str(self.fixture.root/'elsewhere/core_prepare_entry.py')
        with self.assertRaisesRegex(ValueError,'^PREPARE_FIXED_CHECKOUT$'):
            self.entry.read_external(self.core,'host_profile_binding.py',65536,self.digest)

    def test_external_alias_is_refused_by_unchanged_bounded_reader(self):
        original=self.directory/'original';self.path.rename(original);self.path.symlink_to(original)
        with self.assertRaisesRegex(self.selector.Refusal,'^PUBLIC_INPUT_ORDINARY_FILE$'):
            self.entry.read_external(self.core,'host_profile_binding.py',65536,self.digest)

    def test_root_island_reader_still_requires_root_custody(self):
        info=self.path.stat();nonroot=types.SimpleNamespace(st_mode=info.st_mode,st_nlink=info.st_nlink,
            st_size=info.st_size,st_uid=1000)
        with mock.patch.object(Path,'lstat',return_value=nonroot):
            with self.assertRaisesRegex(ValueError,'^PREPARE_FILE_CUSTODY$'):
                self.entry.read(self.path,65536,self.digest)


if __name__ == '__main__':
    unittest.main(verbosity=2)
