"""Constructed preparation controls; no native host, grant or canonical authority."""
import importlib.util
import contextlib
import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import time
import types
import unittest
from unittest import mock

sys.dont_write_bytecode = True
REPO = Path(__file__).resolve().parents[2]
SCRIPTS = REPO / 'skills/implementaudit/scripts'
SOURCE_TEMPLATE = REPO / 'source-peers/native-runtime/skills/implementaudit/scripts/compaction-source-owner-codex-app.py'
spec = importlib.util.spec_from_file_location('preparation_claim_under_test', SCRIPTS / 'claim-run-rotation.py')
owner = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = owner
spec.loader.exec_module(owner)


class PreparationControls(unittest.TestCase):
    def test_unselected_cannot_register_or_write(self):
        with tempfile.TemporaryDirectory(prefix='r0039-preparation-') as temporary:
            root = Path(temporary).resolve()
            owner.git(root, 'init', '--quiet')
            context = {'repo': root, 'controller': 'prepared-fixture', 'claim_id': '1' * 32,
                       'run_root_identity': '.IMPLEMENTAUDIT/runs/fixture-Ab12Cd'}
            constructor = getattr(owner, 'NativeInputPreparationV1', None)
            self.assertIsNotNone(constructor, 'existing-owner preparation rendezvous is absent')
            with self.assertRaisesRegex(owner.RotationError, 'SELECTION_ABSENT'):
                constructor(context, None)
            self.assertEqual(owner.git(root, 'for-each-ref'), b'')


class PortablePreparationShapeControls(unittest.TestCase):
    """Constructed process identities test schema edges; no native authority."""
    def setUp(self):
        self.stack = contextlib.ExitStack()
        self.addCleanup(self.stack.close)
        directory = self.stack.enter_context(tempfile.TemporaryDirectory(prefix='r0039-preparation-shape-'))
        self.root = Path(directory).resolve()
        self.context = {'repo':self.root,'controller':'prepared-fixture','claim_id':'1'*32,
                        'run_root_identity':'.IMPLEMENTAUDIT/runs/fixture-Ab12Cd'}
        self.selected = {'profile':'CONSTRUCTED_INERT_SHAPE_ONLY'}
        self.processes = {pid:{'pid':pid,'creation_filetime':1000+pid,'image':str(self.root/'fake-python')}
                          for pid in (41,42,43)}
        def identity(pid):
            if pid not in self.processes:
                raise owner.RotationError('CONSTRUCTED_DEAD_PROCESS')
            return dict(self.processes[pid])
        self.stack.enter_context(mock.patch.object(owner,'native_process_identity_v1',side_effect=identity))
        wall,mono = time.time_ns()//1000000,time.monotonic_ns()
        self.code = hashlib.sha256(owner._verify_claim_load_identity_v1()).hexdigest()
        self.record = {'schema':owner._NATIVE_PREPARATION_SCHEMA_V1,'phase':'REGISTERED','reservation_id':'d'*32,
            'selection':dict(self.selected),'consumer_sha256':self.code,
            'producer_process':dict(self.processes[41]),'host_process':dict(self.processes[42]),
            'cancellation':{'schema':'implementaudit.native-cancellation.v1','producer_process':dict(self.processes[41]),
                            'event_handle':99,'reservation_id':'d'*32},
            'created_wall_ms':wall,'created_monotonic_ns':mono,'deadline_wall_ms':wall+30000,
            'deadline_monotonic_ns':mono+30000000000,'prior_grant_oid':None,'previous_response_id':None}

    def test_inert_schema_clock_code_and_profile_edges(self):
        owner._native_preparation_validate_v1(self.context,self.record,self.selected)
        for kind in ('extra','code','profile','dead','extended-wait','expired','bad-grant-oid'):
            value = copy.deepcopy(self.record)
            if kind == 'extra':value['grant_authority']=True
            elif kind == 'code':value['consumer_sha256']='0'*64
            elif kind == 'profile':value['selection']['profile']='FOREIGN'
            elif kind == 'dead':value['producer_process']['pid']=44
            elif kind == 'extended-wait':value['deadline_monotonic_ns']+=1
            elif kind == 'bad-grant-oid':value['prior_grant_oid']=3
            else:
                for key in ('created_wall_ms','deadline_wall_ms'):value[key]-=30001
                for key in ('created_monotonic_ns','deadline_monotonic_ns'):value[key]-=30001000000
            with self.subTest(kind=kind), self.assertRaises(owner.RotationError):
                owner._native_preparation_validate_v1(self.context,value,self.selected)

    def test_prepared_source_requires_new_raw_window_and_bounded_grant(self):
        wall,mono = self.record['created_wall_ms'],self.record['created_monotonic_ns']
        metadata = {'registration_oid':'1'*40,'request_oid':'2'*40,'executor':dict(self.processes[43]),
            'consumer_sha256':self.code,'prepared_wall_ms':wall-2,'prepared_monotonic_ns':mono-2000000,
            'observation_after_wall_ms':wall-1,'observation_after_monotonic_ns':mono-1000000,
            'previous_response_id':None}
        source = {'preparation':metadata,'exact_usage':{'received_at_unix_ms':wall,'response_id':'resp_new'},
                  'observed_monotonic_ns':mono,'reported_window':{'received_at_unix_ms':wall,'received_monotonic_ns':mono}}
        grant = {'consumer_sha256':self.code,'not_before_unix_ms':wall,'expires_at_unix_ms':wall+30000}
        owner._native_preparation_source_v1(self.context,source,grant)
        for kind in ('raw-wall','raw-mono','window-wall','window-mono','replayed-response','grant-extension'):
            value,g = copy.deepcopy(source),dict(grant)
            if kind == 'raw-wall':value['exact_usage']['received_at_unix_ms']=wall-1
            elif kind == 'raw-mono':value['observed_monotonic_ns']=mono-1000000
            elif kind == 'window-wall':value['reported_window']['received_at_unix_ms']=wall-1
            elif kind == 'window-mono':value['reported_window']['received_monotonic_ns']=mono-1000000
            elif kind == 'replayed-response':value['preparation']['previous_response_id']='resp_new'
            else:g['expires_at_unix_ms']+=1
            with self.subTest(kind=kind), self.assertRaises(owner.RotationError):
                owner._native_preparation_source_v1(self.context,value,g)

    def test_plain_mapping_never_supplies_canonical_preparation_authority(self):
        with self.assertRaisesRegex(owner.RotationError,'actual local retained predecessor'):
            owner._NativePreparationConsumerV1(self.context,{},None,{},1,1)


def _preparation_fixture_load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _preparation_fixture_pin(path):
    raw = path.read_bytes()
    return {'path':str(path),'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}


def _preparation_fixture_support():
    source = _preparation_fixture_load('_preparation_actual_source_template',SOURCE_TEMPLATE)
    helper = _preparation_fixture_load('_preparation_actual_live_helper',SOURCE_TEMPLATE.with_name('bounded_source_owner.py'))
    return source,helper


class PortableFactoryLoaderControls(unittest.TestCase):
    """Actual loader and thin wrapper; constructed authority; no host/Event/Git."""
    claim_scripts = SCRIPTS

    def setUp(self):
        self.stack=contextlib.ExitStack();self.addCleanup(self.stack.close)
        temporary=self.stack.enter_context(tempfile.TemporaryDirectory(prefix='r0039-preparation-loader-'))
        self.root=Path(temporary).resolve()
        scripts=self.root/'skills/implementaudit/scripts';scripts.mkdir(parents=True)
        self.claim_path=scripts/'claim-run-rotation.py'
        for name in ('claim-run-rotation.py','canonical_custody.py'):
            origin = self.claim_scripts if name == 'claim-run-rotation.py' else SCRIPTS
            (scripts/name).write_bytes((origin/name).read_bytes())
        self.source_path=scripts/'compaction-source-owner-codex-app.py'
        self.source_path.write_bytes(SOURCE_TEMPLATE.read_bytes())
        self.source=_preparation_fixture_load('_preparation_actual_selected_source',self.source_path)
        _,self.helper=_preparation_fixture_support()
        self.claim_pin=_preparation_fixture_pin(self.claim_path)
        self.claim=self.helper.load_live_claim_v1(self.claim_pin,self.source._np_read_pin)
        self.assertIs(self.claim.native_preparation_for_owned_stdio_v1.__globals__,self.claim.__dict__)
        self.assertNotIn(self.claim.__name__,sys.modules)
        producer_path=self.root/'producer/compaction-source-owner-codex-app.py'
        producer_path.parent.mkdir();producer_path.write_bytes(SOURCE_TEMPLATE.read_bytes())
        runner=self.root/'constructed-runner.py';runner.write_bytes(b'# inert fixture pin\n')
        runner_pin=_preparation_fixture_pin(runner)
        dependencies={'claim-run-rotation.py':self.claim_pin,
            'bounded_source_owner.py':_preparation_fixture_pin(SOURCE_TEMPLATE.with_name('bounded_source_owner.py')),
            'compaction-source-owner-codex-app.py':_preparation_fixture_pin(producer_path),
            'owned_stdio_loop.py':runner_pin}
        provider={'producer_dependencies':dependencies,'capture_producer_pin':runner_pin}
        provider_path=self.root/'provider.json';provider_path.write_bytes(self.claim.canonical(provider))
        selected={'producer_sha256':_preparation_fixture_pin(self.source_path)['sha256']}
        self.context={'repo':self.root}
        self.runtime=(provider,None,None,None,None)
        identity={'pid':41,'creation_filetime':1041,'image':str(self.root/'constructed-producer')}
        self.stack.enter_context(mock.patch.object(self.claim,'native_process_identity_v1',return_value=identity))
        self.stack.enter_context(mock.patch.object(self.claim,'_native_selection_v1',return_value=selected))
        held=[self.stack.enter_context(self.claim.PinnedFile(path)) for path in (self.source_path,provider_path)]
        self.stack.enter_context(mock.patch.object(self.claim,'_NATIVE_PRIVATE_PROFILE_V1',(self.root,selected,held)))
        self.producer=types.SimpleNamespace(pins={'runner':runner_pin,'loop':runner_pin,
            'claim':self.claim_pin,'helper':dependencies['bounded_source_owner.py'],
            'source_owner':dependencies['compaction-source-owner-codex-app.py']},claim=self.claim,
            loop=types.SimpleNamespace(),producer_identity=identity,process=None,check=mock.Mock())
        self.producer.loop._live_producer=self.producer

    def invoke(self):
        return self.source.prepare_rotation_input_v1(self.runtime,self.producer,self.claim,self.context)

    def test_actual_unregistered_loader_reaches_real_absent_host_gate(self):
        with self.assertRaisesRegex(self.claim.RotationError,'requires the existing live owned host'):
            self.invoke()
        self.producer.check.assert_called_once_with()
        self.assertNotIn(self.claim.__name__,sys.modules)

    def test_foreign_or_equal_bytes_reloaded_module_refuses(self):
        reload=self.helper.load_live_claim_v1(self.claim_pin,self.source._np_read_pin)
        self.assertEqual(reload.__name__,self.claim.__name__)
        self.assertIsNot(reload.__dict__,self.claim.__dict__)
        foreign=types.ModuleType('_constructed_foreign_claim')
        foreign.__dict__.update(self.claim.__dict__)
        for candidate in (foreign,reload,types.SimpleNamespace(__dict__=self.claim.__dict__)):
            with self.subTest(kind=type(candidate).__name__):
                self.producer.claim=candidate
                with self.assertRaisesRegex(self.claim.RotationError,'selected dependency closure'):
                    self.invoke()
        self.producer.check.assert_not_called()

    def test_changed_physical_source_and_stale_pin_refuse(self):
        self.claim_path.write_bytes(self.claim_path.read_bytes()+b'\n_CONSTRUCTED_SOURCE_DRIFT = 1\n')
        with self.assertRaisesRegex(self.claim.RotationError,'bound load identity'):
            self.claim._verify_claim_load_identity_v1()
        with self.assertRaises(ValueError):
            self.helper.load_live_claim_v1(self.claim_pin,self.source._np_read_pin)
        self.producer.check.assert_not_called()

    def test_compiled_load_binding_refuses_stale_executing_bytes(self):
        old=self.claim_path.read_bytes()
        self.claim_path.write_bytes(old+b'\n_CONSTRUCTED_EXECUTING_CODE_DRIFT = 1\n')
        # Deliberately stale reader is a negative input to the ACTUAL loader;
        # existing v6 compile-to-physical binding must still veto it.
        with self.assertRaisesRegex(ImportError,'executing claim code differs from the physical load snapshot'):
            self.helper.load_live_claim_v1(self.claim_pin,lambda pin,bound:old)
        self.producer.check.assert_not_called()


class PortablePeerFactoryLoaderControls(PortableFactoryLoaderControls):
    """The same real loader controls on the separately bound native peer."""
    claim_scripts = SOURCE_TEMPLATE.parent


@unittest.skipUnless(os.name == 'nt', 'requires actual Windows process and Event custody')
class RendezvousMechanics(unittest.TestCase):
    """Real Git/Windows events/clocks; predecessor/issuer/image authority injected.

    No native host is launched. One owned idle Python process supplies real
    kernel PID/birth/liveness only. The canonical predecessor boundary is an
    explicitly constructed local test double, never cross-process JSON authority.
    """
    @classmethod
    def setUpClass(cls):
        cls.host = subprocess.Popen([sys.executable, '-I', '-S', '-c',
            'import sys; sys.stdin.buffer.read(1)'], stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        def stop():
            cls.host.stdin.close()
            cls.host.wait(timeout=5)
            cls.host.stdout.close()
        cls.addClassCleanup(stop)

    def setUp(self):
        self.stack = contextlib.ExitStack()
        self.addCleanup(self.stack.close)
        self.directory = tempfile.TemporaryDirectory(prefix='r0039-preparation-')
        self.stack.callback(self.directory.cleanup)
        self.root = Path(self.directory.name).resolve()
        owner.git(self.root, 'init', '--quiet')
        (self.root / '.IMPLEMENTAUDIT/.r36-locks').mkdir(parents=True)
        run = self.root / '.IMPLEMENTAUDIT/runs/fixture-Ab12Cd'
        run.mkdir(parents=True)
        self.file = run / 'STATE.md'
        self.file.write_bytes(b'constructed retained state\n')
        oid = owner.git(self.root, 'hash-object', '-w', '--stdin', input_bytes=b'constructed control\n').decode().strip()
        self.context = {'repo': self.root, 'run_root': run, 'controller': 'prepared-fixture',
            'claim_id': '1' * 32, 'run_root_identity': '.IMPLEMENTAUDIT/runs/fixture-Ab12Cd',
            'controller_ref': 'refs/implementaudit/controllers/prepared-fixture', 'controller_oid': oid,
            'pointer_ref': 'refs/implementaudit/current-generations/prepared-fixture',
            'marker_ref': 'refs/implementaudit/current-generation-migrations/prepared-fixture',
            'invalidation_ref': 'refs/implementaudit/continuity-invalidations/prepared-fixture'}
        receipt = 'refs/implementaudit/continuity-receipts/prepared-fixture/G0001'
        for ref in (self.context['controller_ref'], receipt):
            owner.git(self.root, 'update-ref', ref, oid)
        self.expected_canonical = {self.context['controller_ref']: oid, receipt: oid,
            self.context['pointer_ref']: None, self.context['marker_ref']: None, self.context['invalidation_ref']: None}
        self.predecessor = {key: self.context[key] for key in ('controller', 'claim_id', 'run_root_identity')}
        self.predecessor.update(controller_oid=oid, receipt_ref=receipt, receipt_oid=oid,
            state_sha256=hashlib.sha256(self.file.read_bytes()).hexdigest(), roadmap_sha256='4'*64,
            pointer_oid=None, migration_marker_oid=None, invalidation_oid='none')
        self.helper = owner.projection_helper()
        self.native = self.helper.native_inputs_module_v1()
        self.subject = self.helper._native_subject(self.predecessor)
        self.counts = (len(self.file.read_bytes()), 6)
        self.selected = {key: self.context[key] for key in ('controller', 'claim_id', 'run_root_identity')}
        self.selected.update(repo=str(self.root), issuer='CONSTRUCTED_ISSUER_NOT_AUTHORITY',
            source_owner='codex-owned-stdio-canonical-episode-public-source-v1', source_contract_sha256='a'*64,
            provider_selection_sha256='b'*64, producer_sha256='c'*64,
            owner_decision_locator='CONSTRUCTED_NO_OWNER_DECISION')
        self.current_selection = dict(self.selected)
        self.stack.enter_context(mock.patch.object(owner, '_native_selection_v1', side_effect=lambda _: dict(self.current_selection)))
        self.stack.enter_context(mock.patch.object(owner, '_NATIVE_PREPARATION_PRODUCER_V1', None))
        self.stack.enter_context(mock.patch.object(owner, '_NATIVE_PREPARATION_CONSUMER_V1', None))
        self.retained = owner.RetainedInputs([self.file])
        self.stack.callback(self.retained.close)
        self.read = object.__new__(owner._NativePredecessorReadV1)
        self.read._context, self.read._retained = self.context, self.retained
        self.read.verify = self.verify_canonical
        self.read.predecessor = lambda: dict(self.predecessor)
        self.stack.enter_context(mock.patch.object(owner, '_NATIVE_PREDECESSOR_BINDING_V1', self.read))
        self.image_checks = []
        def constructed_image(path, expected):
            self.image_checks.append((path, expected, self.head_record().get('phase')))
        self.stack.enter_context(mock.patch.object(owner, '_hold_native_input_image_v1', side_effect=constructed_image))
        self.preparation = owner.NativeInputPreparationV1(self.context, self.host)
        self.stack.callback(self.preparation.close)
        self.stack.enter_context(owner._CUSTODY.git_scope(self.root, owner.fixed_git(), owner.git_environment()))
        self.before = self.canonical_refs()

    def verify_canonical(self):
        self.retained.verify()
        if owner.read_refs(self.root, self.expected_canonical) != self.expected_canonical:
            raise owner.RotationError('CONSTRUCTED_CANONICAL_SUBJECT_DRIFT')

    def canonical_refs(self):
        result = dict(line.split(' ', 1) for line in owner.git(self.root, 'for-each-ref',
            '--format=%(refname) %(objectname)').decode().splitlines())
        return {ref: oid for ref, oid in result.items()
                if not ref.startswith(('refs/implementaudit/rotation-input-sources/',
                                       'refs/implementaudit/rotation-input-grants/'))}

    def head_record(self):
        ref = owner.native_input_revision_refs_v1(self.context)['source']
        oid = owner.read_ref(self.root, ref)
        return {} if oid is None else owner.decode_json(owner.read_blob(self.root, oid))

    def scope(self):
        return owner._native_preparation_scope_v1(self.context, self.read, self.retained, self.subject, *self.counts)

    def start_consumer(self, callback=None):
        result = {'entered': False}
        finished = threading.Event()
        def consume():
            try:
                with owner._CUSTODY.git_scope(self.root, owner.fixed_git(), owner.git_environment()):
                    with self.scope() as capability:
                        result.update(entered=True, capability=capability)
                        if callback:
                            callback(capability)
            except BaseException as error:
                result['error'] = error
            finally:
                finished.set()
        thread = threading.Thread(target=consume)
        thread.start()
        def stop():
            if thread.is_alive():
                self.preparation.cancel_now()
                thread.join(timeout=5)
            self.assertFalse(thread.is_alive(), 'owned constructed consumer must finish')
        self.stack.callback(stop)
        return result, finished

    def fresh_source(self, *, before_request=False, window_before_request=False, response='resp_constructed_after_request'):
        wall, mono = self.preparation.accepted_at
        while time.time_ns() // 1000000 <= wall or time.monotonic_ns() <= mono:
            time.sleep(.002)  # Real clocks; no patched cutoff or future stamp.
        now = time.time_ns() // 1000000
        host = {'name': 'codex', 'version': '0.153.4', 'binary_sha256': self.native.NATIVE_BINARY_SHA256,
                'effective_config_sha256': 'e'*64, 'model': 'gpt-6-astra'}
        policy = {'id': 'R0039-CONFIGURED-HEADROOM-v1', 'configured_usable_tokens': 258400, 'maximum_age_ms': 30000}
        tokenizer = {'name': 'cl100k_base', 'implementation': 'tiktoken', 'version': '0.13.0',
                     'encoding_sha256': '223921b76ee99bde995b7ff738513eef100fb51d18c93597a113bcffe865b2a7'}
        grant = {'schema': 'implementaudit.native-rotation-owner-grant.v1', 'status': 'ACTIVE',
            **{key: self.selected[key] for key in ('issuer','source_owner','source_contract_sha256',
                'provider_selection_sha256','producer_sha256','owner_decision_locator')},
            'episode_binding_sha256': 'f'*64, 'consumer_sha256': hashlib.sha256(owner._verify_claim_load_identity_v1()).hexdigest(),
            'subject': self.subject, 'host': host, 'budget_policy': policy, 'tokenizer': tokenizer,
            'not_before_unix_ms': now, 'expires_at_unix_ms': now + 30000}
        binding = {'issuer': grant['issuer'], 'grant_sha256': hashlib.sha256(owner.canonical(grant)).hexdigest(),
            'producer_sha256': grant['producer_sha256'], 'semantic_contract_sha256': grant['source_contract_sha256'],
            'host': host, 'budget_policy': policy, 'tokenizer': tokenizer, 'subject': self.subject,
            'source_bytes': self.counts[0], 'source_tokens': self.counts[1], 'thread_id':'constructed-thread', 'turn_id':'constructed-turn'}
        state = self.native.NativeInputState(binding)
        usage = {'inputTokens':193789, 'outputTokens':11, 'totalTokens':193800,
                 'cachedInputTokens':0, 'cacheWriteInputTokens':0, 'reasoningOutputTokens':0}
        kwargs = ({'received_at_unix_ms': wall, 'received_monotonic_ns': mono} if before_request else {})
        state.observe({'method':'rawResponse/completed','params':{'threadId':'constructed-thread',
            'turnId':'constructed-turn','responseId':response,'usage':usage}}, **kwargs)
        window_kwargs = ({'received_at_unix_ms': wall, 'received_monotonic_ns': mono}
                         if window_before_request else kwargs)
        state.observe({'method':'thread/tokenUsage/updated','params':{'threadId':'constructed-thread',
            'turnId':'constructed-turn','tokenUsage':{'last':dict(usage),'total':dict(usage),'modelContextWindow':258400}}}, **window_kwargs)
        state.observe({'method':'turn/completed','params':{'threadId':'constructed-thread',
            'turn':{'id':'constructed-turn','status':'completed'}}})
        return state, grant

    def snapshot(self, state, grant, identity, signal):
        return {'schema':'implementaudit.native-rotation-source.v3','phase':'READY',
            'binding':state._binding,'exact_usage':state._snapshot,'reported_window':state._reported_window,
            'cutoff_revision':state._revision,'observed_monotonic_ns':state._received_monotonic_ns,
            'reservation_id':identity,'producer_process':self.preparation.producer,'host_process':self.preparation.host,
            'cancellation':signal.descriptor,'episode_binding_sha256':grant['episode_binding_sha256'],
            **{key:self.selected[key] for key in ('source_owner','source_contract_sha256','provider_selection_sha256')}}

    def publish(self, state, grant):
        identity, signal = owner.native_rotation_parts_v1(self.context, state, grant)
        source = self.snapshot(state, grant, identity, signal)
        source = owner.bind_native_preparation_v1(self.context, source)
        owner._validate_native_revision_v1(self.context, source, grant, self.native)
        refs = owner.native_input_revision_refs_v1(self.context)
        previous = owner.read_refs(self.root, refs.values())
        self.assertTrue(owner.native_preparation_prior_v1(self.context, previous))
        plan = owner.prepare_native_source_update_v1(self.context, source, grant,
            expected_source_oid=previous[refs['source']], expected_grant_oid=previous[refs['grant']])
        soid, goid = owner.write_blob(self.context, plan['source_bytes']), owner.write_blob(self.context, plan['grant_bytes'])
        updates = owner.retention_updates(self.context, [soid, goid, *previous.values()])
        updates.update(plan['updates'])
        owner.update_refs(self.context, updates, owner.predecessor_guards(self.context, self.predecessor))
        return source, grant, {refs['source']:soid, refs['grant']:goid}

    def registered_request(self):
        self.preparation.register()
        result, finished = self.start_consumer()
        request = self.preparation.wait_request()
        self.assertIn('NEVER_START_MODEL_OR_API_TURN', request['action'])
        self.assertEqual(self.canonical_refs(), self.before)
        return result, finished

    def test_registration_and_wait_have_no_canonical_or_archive_effect(self):
        result, finished = self.registered_request()
        self.assertFalse(finished.is_set())
        self.assertFalse(result['entered'])
        self.assertEqual(self.head_record()['phase'], 'REQUESTED')
        self.assertEqual(self.image_checks[0][2], 'REGISTERED')
        state, grant = self.fresh_source()
        self.publish(state, grant)
        self.assertTrue(finished.wait(5))
        self.assertNotIn('error', result)
        self.assertTrue(result['entered'])

    def test_inert_record_is_never_native_input(self):
        self.preparation.register()
        with self.assertRaises(owner.RotationError):
            owner._validate_native_revision_v1(self.context, self.head_record(), {}, self.native)
        self.assertEqual(self.canonical_refs(), self.before)

    def test_registration_cannot_be_replayed_and_close_is_idempotent(self):
        self.preparation.register()
        with self.assertRaises(owner.RotationError):
            self.preparation.register()
        self.preparation.close()
        terminal = self.head_record()
        self.assertEqual(terminal['phase'], 'CANCELLED')
        self.preparation.close()
        self.assertEqual(self.head_record(), terminal)
        self.assertEqual(self.canonical_refs(), self.before)

    def test_closed_registration_cannot_be_reopened(self):
        self.preparation.register(); self.preparation.close()
        other = owner.NativeInputPreparationV1(self.context, self.host)
        try:
            with self.assertRaisesRegex(owner.RotationError, 'reconciliation'):
                other.register()
        finally:
            other.close()
        self.assertEqual(self.head_record()['phase'], 'CANCELLED')

    def test_request_can_be_consumed_only_once(self):
        result, finished = self.registered_request()
        with self.assertRaisesRegex(owner.RotationError, 'already consumed'):
            self.preparation.wait_request()
        self.preparation.cancel_now()
        self.assertTrue(finished.wait(5)); self.assertFalse(result['entered'])
        self.assertEqual(self.canonical_refs(), self.before)

    def test_cancel_before_request_refuses_without_archive(self):
        self.preparation.register(); self.preparation.cancel_now()
        with self.assertRaises(owner.RotationError):
            with self.scope(): self.fail('cancelled preparation yielded')
        self.assertEqual(self.head_record()['phase'], 'REGISTERED')
        self.assertEqual(self.canonical_refs(), self.before)

    def test_cancel_during_wait_retains_exact_inert_denial(self):
        result, finished = self.registered_request()
        self.preparation.cancel_now()
        self.assertTrue(finished.wait(5))
        self.assertIn('error', result); self.assertFalse(result['entered'])
        self.assertEqual(self.head_record()['phase'], 'CANCELLED')
        self.assertEqual(self.canonical_refs(), self.before)

    def test_existing_but_not_after_request_event_refuses(self):
        result, finished = self.registered_request()
        state, grant = self.fresh_source(before_request=True)
        with self.assertRaisesRegex(owner.RotationError, 'new raw/window'):
            self.publish(state, grant)
        self.assertTrue(finished.wait(5)); self.assertFalse(result['entered'])
        self.assertEqual(self.canonical_refs(), self.before)

    def test_grant_cannot_be_extended_for_new_observation(self):
        result, finished = self.registered_request()
        state, grant = self.fresh_source()
        grant['expires_at_unix_ms'] += 1
        with self.assertRaisesRegex(owner.RotationError, 'unchanged grant'):
            self.preparation.source_parts(state, grant)
        self.assertTrue(finished.wait(5)); self.assertFalse(result['entered'])
        self.assertEqual(self.canonical_refs(), self.before)

    def test_new_raw_cannot_reuse_old_reported_window(self):
        result, finished = self.registered_request()
        # Existing observe() rejects a regressing callback clock even before
        # READY construction. Preserve that earlier source gate explicitly.
        with self.assertRaisesRegex(self.native.NativeInputError, 'INVALID_OR_REORDERED_LIVE_RECEIPT_CLOCKS'):
            self.fresh_source(window_before_request=True)
        self.preparation.cancel_now()
        self.assertTrue(finished.wait(5)); self.assertFalse(result['entered'])
        self.assertEqual(self.canonical_refs(), self.before)

    def test_source_cannot_replace_prepared_counts(self):
        result, finished = self.registered_request()
        state, grant = self.fresh_source()
        state._binding = dict(state._binding, source_bytes=state._binding['source_bytes']+1)
        with self.assertRaisesRegex(owner.RotationError, 'new raw/window'):
            self.publish(state, grant)
        self.assertTrue(finished.wait(5)); self.assertFalse(result['entered'])
        self.assertEqual(self.canonical_refs(), self.before)

    def test_source_binding_cannot_be_reused(self):
        result, finished = self.registered_request()
        state, grant = self.fresh_source()
        self.preparation.source_parts(state, grant)
        with self.assertRaisesRegex(owner.RotationError, 'unused actual request'):
            self.preparation.source_parts(state, grant)
        self.assertTrue(finished.wait(5)); self.assertFalse(result['entered'])

    def test_foreign_process_code_profile_and_malformed_records_refuse(self):
        self.preparation.register()
        for kind in ('code','profile','dead-producer','malformed','extended-wait','nonstring-grant'):
            value = copy.deepcopy(self.preparation.registration)
            if kind == 'code': value['consumer_sha256'] = '0'*64
            elif kind == 'profile': value['selection']['provider_selection_sha256'] = '0'*64
            elif kind == 'dead-producer': value['producer_process']['pid'] = 2147483647
            elif kind == 'malformed': value['unexpected'] = True
            elif kind == 'nonstring-grant': value['prior_grant_oid'] = 4
            else: value['deadline_monotonic_ns'] += 1
            with self.subTest(kind=kind), self.assertRaises(owner.RotationError):
                owner._native_preparation_validate_v1(self.context, value, self.selected)
        self.assertEqual(self.canonical_refs(), self.before)

    def test_canonical_subject_drift_cannot_issue_request(self):
        self.preparation.register()
        new = owner.write_blob(self.context, b'changed canonical controller\n')
        owner.git(self.root,'update-ref',self.context['controller_ref'],new)
        with self.assertRaisesRegex(owner.RotationError,'SUBJECT_DRIFT'):
            with self.scope(): self.fail('changed predecessor yielded')
        self.assertEqual(self.head_record()['phase'],'REGISTERED')

    def test_profile_drift_after_request_cannot_return_ready(self):
        result, finished = self.registered_request()
        self.current_selection['provider_selection_sha256'] = '0'*64
        state, grant = self.fresh_source()
        with self.assertRaises(owner.RotationError):
            self.publish(state, grant)
        self.assertTrue(finished.wait(5)); self.assertFalse(result['entered'])
        self.assertEqual(self.canonical_refs(), self.before)

    def test_prepared_ready_cannot_be_taken_as_legacy_by_foreign_consumer(self):
        result, finished = self.registered_request()
        state, grant = self.fresh_source()
        source, grant, heads = self.publish(state, grant)
        self.assertTrue(finished.wait(5)); self.assertNotIn('error',result)
        with self.assertRaises(owner.RotationError):
            with self.scope(): self.fail('prepared READY became immediate legacy input')
        with self.assertRaisesRegex(owner.RotationError,'actual one-shot local consumer'):
            owner._native_preparation_require_consumer_v1(self.context,source,grant,heads)

    def test_registered_blob_can_be_pruned_after_request_without_authority_reread(self):
        result, finished = self.registered_request()
        registered = self.preparation.registration_oid
        owner.git(self.root,'prune','--expire','now')
        missing = owner.git_process(self.root,'cat-file','-e',registered)
        self.assertNotEqual(missing.returncode,0)
        state, grant = self.fresh_source()
        self.publish(state, grant)
        self.assertTrue(finished.wait(5)); self.assertNotIn('error',result)

    def test_plain_json_cannot_be_a_local_canonical_preparation(self):
        with self.assertRaisesRegex(owner.RotationError,'actual local retained predecessor'):
            owner._NativePreparationConsumerV1(self.context,dict(self.predecessor),self.retained,self.subject,*self.counts)
        self.assertEqual(self.canonical_refs(),self.before)

    def test_real_cancellation_duplicate_has_no_modify_right(self):
        self.preparation.register()
        wait = owner.NativeCancellationWaitV1(self.preparation.cancellation.descriptor,
            self.preparation.producer,self.preparation.reservation_id)
        try:
            self.assertFalse(wait.k.SetEvent(wait.handle))
            self.preparation.cancellation.check()
        finally:
            wait.close()

    def test_mailbox_read_waits_for_existing_namespace_gate(self):
        refs = owner.native_input_revision_refs_v1(self.context)
        started, finished = threading.Event(), threading.Event()
        result = {}
        def read():
            started.set()
            try:
                with owner._CUSTODY.git_scope(self.root, owner.fixed_git(), owner.git_environment()):
                    result['heads'] = owner._native_preparation_heads_v1(self.context, refs.values())
            except BaseException as error:
                result['error'] = error
            finally:
                finished.set()
        with owner.namespace_gate(self.context):
            thread = threading.Thread(target=read)
            thread.start()
            self.assertTrue(started.wait(2))
            self.assertFalse(finished.wait(.1), 'mailbox read crossed actual writer gate')
        thread.join(5)
        self.assertFalse(thread.is_alive())
        self.assertNotIn('error', result)
        self.assertEqual(result['heads'], {ref: None for ref in refs.values()})

    def test_custody_read_failure_is_never_retried(self):
        with mock.patch.object(owner, 'read_refs', side_effect=owner.RotationError('CONSTRUCTED_CUSTODY_REFUSAL')) as read:
            with self.assertRaisesRegex(owner.RotationError, 'CUSTODY_REFUSAL'):
                owner._native_preparation_heads_v1(self.context, [])
        self.assertEqual(read.call_count, 1)
        self.assertEqual(self.canonical_refs(), self.before)

    def test_expired_scheduling_record_cannot_issue_request(self):
        self.preparation.register()
        record = copy.deepcopy(self.preparation.registration)
        record['created_wall_ms'] -= 30001
        record['deadline_wall_ms'] -= 30001
        record['created_monotonic_ns'] -= 30001 * 1000000
        record['deadline_monotonic_ns'] -= 30001 * 1000000
        ref = owner.native_input_revision_refs_v1(self.context)['source']
        oid = owner.write_blob(self.context, owner.canonical(record))
        owner.update_refs(self.context, {ref: (oid, self.preparation.registration_oid)}, {})
        with self.assertRaisesRegex(owner.RotationError, 'scheduling interval expired'):
            with self.scope(): self.fail('expired inert registration yielded')
        self.assertEqual(self.head_record(), record)
        self.assertEqual(self.canonical_refs(), self.before)

    def test_scheduling_expiry_cannot_publish_late_source(self):
        result, finished = self.registered_request()
        state, grant = self.fresh_source()
        for key in ('created_wall_ms', 'deadline_wall_ms'):
            self.preparation.registration[key] -= 30001
        for key in ('created_monotonic_ns', 'deadline_monotonic_ns'):
            self.preparation.registration[key] -= 30001 * 1000000
        with self.assertRaisesRegex(owner.RotationError, 'scheduling interval expired'):
            self.publish(state, grant)
        self.assertTrue(finished.wait(5)); self.assertFalse(result['entered'])
        self.assertEqual(self.canonical_refs(), self.before)

    def test_grant_ref_drift_refuses_before_ready(self):
        result, finished = self.registered_request()
        refs = owner.native_input_revision_refs_v1(self.context)
        altered = owner.write_blob(self.context, b'constructed foreign grant\n')
        owner.update_refs(self.context, {refs['grant']: (altered, None)}, {})
        with self.assertRaisesRegex(owner.RotationError, 'request changed before READY'):
            owner.native_preparation_prior_v1(self.context, owner.read_refs(self.root, refs.values()))
        self.assertTrue(finished.wait(5)); self.assertFalse(result['entered'])
        self.assertEqual(owner.read_ref(self.root, refs['grant']), altered)
        self.assertEqual(self.canonical_refs(), self.before)

    def test_request_ref_replacement_is_not_overwritten_by_cleanup(self):
        result, finished = self.registered_request()
        refs = owner.native_input_revision_refs_v1(self.context)
        replacement = dict(self.preparation.request, source_tokens=self.counts[1]+1)
        oid = owner.write_blob(self.context, owner.canonical(replacement))
        owner.update_refs(self.context, {refs['source']: (oid, self.preparation.request_oid)}, {})
        self.assertTrue(finished.wait(5)); self.assertFalse(result['entered'])
        with self.assertRaisesRegex(owner.RotationError, 'request changed before READY'):
            owner.native_preparation_prior_v1(self.context, owner.read_refs(self.root, refs.values()))
        self.preparation.close()
        self.assertEqual(owner.read_ref(self.root, refs['source']), oid)
        self.assertEqual(self.canonical_refs(), self.before)

    def test_legacy_immediate_ready_keeps_original_freshness(self):
        self.preparation.accepted_at = (time.time_ns()//1000000-2, time.monotonic_ns()-2000000)
        state, grant = self.fresh_source()
        signal = owner.NativeCancellationSignalV1('d'*32)
        self.stack.callback(signal.close)
        source = self.snapshot(state, grant, 'd'*32, signal)
        owner._validate_native_revision_v1(self.context, source, grant, self.native)
        refs = owner.native_input_revision_refs_v1(self.context)
        updates = {refs['source']: (owner.write_blob(self.context, owner.canonical(source)), None),
                   refs['grant']: (owner.write_blob(self.context, owner.canonical(grant)), None)}
        owner.update_refs(self.context, updates, {})
        with self.scope() as value:
            self.assertIsNone(value)
        expired = copy.deepcopy(source)
        expired['exact_usage']['received_at_unix_ms'] -= 30001
        expired['observed_monotonic_ns'] -= 30001*1000000
        with self.assertRaises(owner.RotationError):
            owner._validate_native_revision_v1(self.context, expired, grant, self.native)
        self.assertEqual(self.canonical_refs(), self.before)

    def test_byte_and_token_cheap_routes_do_not_touch_preparation(self):
        roadmap = self.context['run_root']/'ROADMAP.md'
        roadmap.write_bytes(b'constructed roadmap\n')
        predecessor = dict(self.predecessor, projection_generation_id='G0001',
            state_path=self.file.relative_to(self.root).as_posix(), roadmap_path=roadmap.relative_to(self.root).as_posix())
        encoding = self.context['run_root']/'offline-encoding'
        encoding.write_bytes(b'constructed tokenizer DATA only\n')
        with mock.patch.object(owner, 'resolve_predecessor', return_value=predecessor), \
             mock.patch.object(owner, 'retained_owner_paths', return_value=[]), \
             mock.patch.object(self.helper, 'prepare_canonical_draft', return_value={'triggered':False,'live_bytes':1,'live_tokens':1}), \
             mock.patch.object(owner, '_native_preparation_scope_v1', side_effect=AssertionError('cheap route entered preparation')), \
             mock.patch.object(owner, '_native_selection_v1', side_effect=AssertionError('cheap route selected native source')):
            for tokenizer in (None, encoding):
                with self.subTest(tokens=tokenizer is not None):
                    result = owner.run_canonical_rotation_v1(self.context, 'absent-owner-map.json', {}, tokenizer_encoding=tokenizer)
                    self.assertEqual(result['status'], 'NOT_TRIGGERED')
        self.assertEqual(self.canonical_refs(), self.before)
        self.assertEqual(self.head_record(), {})

    def test_factory_binds_selected_owner_and_distinct_producer_copy(self):
        source,helper = _preparation_fixture_support()
        loaded = helper.load_live_claim_v1(_preparation_fixture_pin(SCRIPTS/'claim-run-rotation.py'),source._np_read_pin)
        self.assertNotIn(loaded.__name__,sys.modules)
        self.assertIs(loaded.native_preparation_for_owned_stdio_v1.__globals__,loaded.__dict__)
        selected_path = self.root/'skills/implementaudit/scripts/compaction-source-owner-codex-app.py'
        selected_path.parent.mkdir(parents=True)
        selected_path.write_bytes(SOURCE_TEMPLATE.read_bytes())
        selected_source = _preparation_fixture_load('_preparation_selected_windows_owner',selected_path)
        producer_path = self.root/'producer/compaction-source-owner-codex-app.py'
        producer_path.parent.mkdir();producer_path.write_bytes(SOURCE_TEMPLATE.read_bytes())
        source_pin = _preparation_fixture_pin(producer_path)
        fixture_pin = _preparation_fixture_pin(self.file)
        dependencies = {name:fixture_pin for name in ('owned_stdio_loop.py','claim-run-rotation.py','bounded_source_owner.py')}
        dependencies['compaction-source-owner-codex-app.py'] = source_pin
        provider = {'producer_dependencies':dependencies,'capture_producer_pin':fixture_pin}
        provider_path = self.root/'provider.json';provider_path.write_bytes(loaded.canonical(provider))
        held = [loaded.PinnedFile(path) for path in (selected_path,provider_path)]
        for value in held:self.stack.callback(value.close)
        selected = dict(self.current_selection,producer_sha256=_preparation_fixture_pin(selected_path)['sha256'])
        producer = types.SimpleNamespace(pins={'runner':fixture_pin,'loop':fixture_pin,'claim':fixture_pin,
            'helper':fixture_pin,'source_owner':source_pin}, claim=loaded, loop=types.SimpleNamespace(),
            producer_identity=loaded.native_process_identity_v1(os.getpid()), process=self.host,
            check=mock.Mock(), send=mock.Mock(side_effect=AssertionError('model/send forbidden')))
        producer.loop._live_producer = producer
        runtime = (provider,None,None,None,None)
        with mock.patch.object(loaded,'_native_selection_v1',return_value=selected), \
             mock.patch.object(loaded,'_NATIVE_PRIVATE_PROFILE_V1',(self.root,selected,held)):
            cap = selected_source.prepare_rotation_input_v1(runtime,producer,loaded,self.context)
            try:
                self.assertIs(cap._producer,producer)
                self.assertEqual(producer.check.call_count,1)
                self.assertNotIn(loaded.__name__,sys.modules)
                with self.assertRaises(loaded.RotationError):
                    loaded.native_preparation_for_owned_stdio_v1(runtime,producer,self.context,producer_path)
                producer.pins = dict(producer.pins,source_owner=dict(source_pin,sha256='0'*64))
                with self.assertRaisesRegex(loaded.RotationError,'dependency closure'):
                    selected_source.prepare_rotation_input_v1(runtime,producer,loaded,self.context)
            finally:
                cap.close()
        producer.send.assert_not_called()
        self.assertEqual(self.head_record(),{})



if __name__ == '__main__':
    unittest.main()
