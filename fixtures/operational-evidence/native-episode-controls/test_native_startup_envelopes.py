"""SOURCE_ONLY startup-envelope controls over real, owned physical history.

Only the native provider authentication boundary is substituted. All records,
locators, header checks, HOLD acquisition, pairing, and ordering use the current
public owner. No native process, archived implementation, or selection is run.
"""
import json
from pathlib import Path
import types
import unittest
from unittest import mock

import test_acquisition_resource_domains as acquisition_fixtures


class NativeStartupEnvelopeControls(unittest.TestCase):
    def setUp(self):
        self.fixture_helper = acquisition_fixtures.AcquisitionResourceDomainControls()
        self.fixture_helper.setUp()
        self.addCleanup(self.fixture_helper.doCleanups)
        self.obs = self.fixture_helper.obs
        self.directory = self.fixture_helper.directory

    def episode(self, *, settings=False, declaration=False, transport=None,
                equal_ticks=False, profile=None, version='0.164.0-alpha.11.1',
                mutate=None, forbidden=None, selected_settings=True):
        """Build a small complete pre-USE history; return its actual entry point."""
        helper, obs = self.fixture_helper, self.obs
        context_template = {'profile_id': profile or obs.NONPROTECTED_PROFILE,
                            'source_association': 'PUBLIC_BOUNDARY_CHILD_STRUCTURAL_UNQUALIFIED'}
        store, session, owner = str(self.directory), 'source-only-root', 'source-only-owner'
        bind_request = {'fixture': 'SOURCE_ONLY_STARTUP_ENVELOPES'}
        bind_input = obs.profile_tool_input(context_template,
            obs.delivery_tool_input(store, session, owner, bind_request))
        exchange_id = 'e' * 64
        initial_settings = {'source_only': True, 'permissions': {'network': False}}
        rows = [json.loads(helper.metadata())]
        rows[0]['payload']['cli_version'] = version
        labels = {'metadata': 0}

        def add(label, kind, payload, metadata=None):
            labels[label] = len(rows)
            row = json.loads(helper.wire(len(rows), kind, payload))
            if metadata is not None:
                row['metadata'] = metadata
            rows.append(row)

        add('activation', 'event_msg', {'type': 'task_started', 'turn_id': 'source-only-startup-turn'})
        add('clock_neighbor', 'event_msg', {'type': 'token_count'})
        if equal_ticks:
            rows[labels['clock_neighbor']]['timestamp'] = rows[labels['activation']]['timestamp']
        if settings:
            add('settings', 'event_msg', {'type': 'thread_settings_applied',
                'thread_id': 'source-only-child', 'thread_settings': initial_settings.copy()})
        if declaration:
            add('declaration', 'response_item', {'type': 'additional_tools',
                'id': 'source-only-declaration', 'role': 'developer',
                'tools': [{'namespace': 'collaboration', 'name': 'wait_agent'},
                          {'namespace': 'clock', 'name': 'sleep'}]},
                {'client_authored': False, 'mcp_attribution': {'status': 'none'}})
        if forbidden == 'clock':
            add('forbidden', 'response_item', {'type': 'function_call', 'namespace': 'clock',
                'name': 'sleep', 'arguments': '{"delay":1}', 'call_id': 'fixture-forbidden'})
        elif forbidden == 'early_use':
            add('forbidden', 'response_item', {'type': 'custom_tool_call', 'name': 'exec',
                'call_id': 'fixture-forbidden',
                'input': '// COMPACTION_OBSERVATION_EXCHANGE=' + exchange_id + '\nSOURCE_ONLY'})
        transport_metadata = {'client_authored': False, 'user_input_order': 0}
        for label, call_id, command in (('load', 'fixture-load', 'SOURCE_ONLY load'),
                                        ('exchange', 'fixture-exchange', 'SOURCE_ONLY exchange')):
            add(label + '_call', 'response_item', {'type': 'custom_tool_call', 'name': 'exec',
                'call_id': call_id, 'input': command})
            add(label + '_result', 'response_item', {'type': 'custom_tool_call_output',
                'call_id': call_id}, transport_metadata.copy()
                if transport in ('custom_tool_call_output', 'all') and label == 'load' else None)
        if transport in ('function_call', 'function_call_output', 'all'):
            add('collaboration_call', 'response_item', {'type': 'function_call',
                'namespace': 'collaboration', 'name': 'wait_agent', 'arguments': '{}',
                'call_id': 'fixture-collaboration'}, transport_metadata.copy()
                if transport in ('function_call', 'all') else None)
            add('collaboration_result', 'response_item', {'type': 'function_call_output',
                'call_id': 'fixture-collaboration'}, transport_metadata.copy()
                if transport in ('function_call_output', 'all') else None)
        add('bind', 'response_item', {'type': 'custom_tool_call', 'name': 'exec',
            'call_id': 'fixture-bind', 'input': bind_input})
        settings_digest = obs.digest(obs.canonical(initial_settings))
        context_changes = {}
        if mutate is not None:
            mutate(rows, labels, context_changes)
        fixture = helper.write(obs.canonical(row) + b'\n' for row in rows)
        context = helper.context(fixture, profile=profile)
        if settings and selected_settings:
            context['_current_child_settings_sha256'] = settings_digest
        context.update(context_changes)

        def pin(label):
            index = labels[label]
            return {'path': str(fixture['path']), 'physical': fixture['physical'], 'role': 'child',
                'locator': fixture['selectors'][index], 'timestamp': rows[index]['timestamp'],
                'message_or_call_id': rows[index]['payload']['call_id']}

        prepared = {'authorization': {'load_identity': {'call': pin('load_call'), 'result': pin('load_result')}},
                    'obligation': {'observation_id': 'a' * 64}}
        exchange = {'identity': exchange_id, 'records': {'call': pin('exchange_call'), 'result': pin('exchange_result')}}

        def fixture_read(ctx, role, selectors):
            self.assertIs(ctx, context)
            self.assertEqual(role, 'child')
            self.assertTrue(all(selector in fixture['selectors'] for selector in selectors))
            return obs.read_records(str(fixture['path']), selectors,
                context['child']['allowed_ranges'], fixture['physical'])

        def invoke():
            occurrences = []
            with mock.patch.object(obs, '_nonprotected_read_records', fixture_read):
                prefix = obs.history_with_priors(context, prepared, exchange, bind_request,
                    store, session, owner, {}, {}, occurrence_sink=occurrences)
            self.assertEqual([(entry['population'], entry['attempt_class'], entry['semantic'],
                               entry['completion']) for entry in occurrences],
                [('CURRENT', 'ORIGINAL', 'LOAD', 'COMPLETED'),
                 ('CURRENT', 'ORIGINAL', 'EXCHANGE', 'COMPLETED'),
                 ('CURRENT', 'ORIGINAL', 'BIND', 'PENDING')])
            return prefix

        return invoke, fixture, rows, labels, context

    def accepted(self, case):
        try:
            prefix = case[0]()
        except ValueError as error:
            self.fail('real history refused a valid SOURCE_ONLY envelope: ' + str(error))
        self.assertEqual(prefix['physical_records'], len(case[2]))
        self.assertEqual(prefix['prefix_sha256'], case[1]['sha256'])
        self.assertEqual(prefix['prefix_bytes'], case[1]['bytes'])
        self.assertIs(prefix['host_producer_authenticated'], False)
        return prefix

    def test_ordinary_history_without_selected_settings_remains_valid(self):
        self.accepted(self.episode())

    def test_selected_initial_settings_on_real_current_hold(self):
        self.accepted(self.episode(settings=True))

    def test_selected_settings_are_closed_and_bound_into_fixed_policy(self):
        owner = self.fixture_helper.owner
        baseline = self.obs.digest(self.obs.canonical({'source_only': True}))
        identity_pin = {'sha256': '1' * 64}
        selected = dict(schema='implementaudit.codex-nonprotected-provider-selection.v1',
            profile_id=self.obs.NONPROTECTED_PROFILE, root_thread_id='source-only-root',
            root_agent_path='/root', root_source=str(self.directory / 'source.jsonl'),
            session_root=str(self.directory), cwd=str(self.directory),
            cli_version='0.163.0-alpha.15', native_version='codex-cli 0.164.0-alpha.11.1',
            desktop_version='SOURCE_ONLY', host_process={}, desktop_process={},
            native_executable=identity_pin, desktop_executable=identity_pin,
            desktop_asar=identity_pin, config_file=identity_pin,
            runtime_helpers={name: {} for name in ('bounded_native_reader.py',
                'bounded_source_owner.py', 'bounded_file_custody.py')},
            episode_owner={'module_pin': {}},
            pending_owner={'store': str(self.directory), 'session_id': 'source-only-root',
                'owner_id': 'source-only-owner'}, child_initial_settings_sha256=baseline)
        path = self.directory / 'source-only-selection.json'

        def selection(value):
            raw = self.obs.canonical(value)
            path.write_bytes(raw)
            pin = {'path': str(path), 'bytes': len(raw), 'sha256': self.obs.digest(raw)}
            with mock.patch.object(owner, 'NONPROTECTED_SELECTION_PIN', pin):
                return owner._np_selection(), pin

        actual, pin = selection(selected)
        self.assertEqual(actual, selected)
        for field, value, reason in (
            ('child_initial_settings_sha256', False, 'NONPROTECTED_CHILD_SETTINGS_BASELINE'),
            ('child_initial_settings_sha256', 'A' * 64, 'NONPROTECTED_CHILD_SETTINGS_BASELINE'),
            ('native_version', 'codex-cli 0.163.0-alpha.15', 'NONPROTECTED_CHILD_SETTINGS_BASELINE'),
            ('caller_authenticated', True, 'NONPROTECTED_FIXED_SELECTION_SHAPE')):
            with self.subTest(field=field, value=value), self.assertRaisesRegex(ValueError, reason):
                selection({**selected, field: value})
        without = dict(selected)
        without.pop('child_initial_settings_sha256')
        self.assertEqual(selection(without)[0], without)
        names = ('compaction-source-owner-codex-app.py', 'codex-recovery-native-reader.py')
        code_pins = {str(Path('implementaudit/scripts') / name):
                     self.obs.digest((owner.HERE / name).read_bytes()) for name in names}
        relation = acquisition_fixtures.support.load('bounded_source_owner.py')
        helper = types.SimpleNamespace(child_cli_version=relation.child_cli_version)

        def policy(value):
            actual, pin = selection(value)
            # Only the unavailable live-provider acquisition is substituted.
            # Actual selection/code reads and fixed-policy construction execute.
            with mock.patch.object(owner, 'NONPROTECTED_SELECTION_PIN', pin), \
                 mock.patch.object(owner, '_np_runtime', return_value=(actual, None, None, helper, None)):
                result = owner.nonprotected_fixed_policy(self.obs, code_pins)
            self.assertEqual(result['descriptor']['provider_selection']['selection_pin'], pin)
            self.assertEqual(result['policy_digest'], self.obs.digest(self.obs.canonical(
                {key: result[key] for key in ('descriptor', 'code_and_skill_pins')})))
            return result

        first = policy(selected)
        second = policy({**selected, 'child_initial_settings_sha256': '2' * 64})
        self.assertEqual(first['descriptor']['exact_host_tuple']['child_initial_settings_sha256'], baseline)
        self.assertEqual(second['descriptor']['exact_host_tuple']['child_initial_settings_sha256'], '2' * 64)
        self.assertNotEqual(first['policy_digest'], second['policy_digest'])
        self.assertNotIn('child_initial_settings_sha256', policy(without)['descriptor']['exact_host_tuple'])

    def test_inert_developer_declaration_on_real_current_hold(self):
        self.accepted(self.episode(declaration=True))

    def test_transport_metadata_on_existing_paired_events(self):
        for kind in ('custom_tool_call_output', 'function_call', 'function_call_output'):
            with self.subTest(kind=kind):
                self.accepted(self.episode(transport=kind))

    def test_equal_ticks_on_contiguous_current_physical_rows(self):
        self.accepted(self.episode(equal_ticks=True))

    def reorder(self, rows, labels, ordered):
        """Move fixture events while recomputing all real ordinal/anchor positions."""
        labelled_rows = {name: rows[index] for name, index in labels.items()}
        rows[:] = ordered
        labels.clear()
        for index, row in enumerate(rows):
            row['ordinal'] = index
            row['timestamp'] = json.loads(self.fixture_helper.wire(index))['timestamp']
            for name, original in labelled_rows.items():
                if row is original:
                    labels[name] = index

    def rejected(self, case, reason=None):
        with self.assertRaises(ValueError) as caught:
            case[0]()
        if reason is not None:
            self.assertEqual(str(caught.exception), reason)
        return caught.exception

    def test_combined_current_startup_preserves_complete_original_occurrences(self):
        self.accepted(self.episode(settings=True, declaration=True, transport='all', equal_ticks=True))

    def test_selected_settings_require_exact_unique_preload_child_payload(self):
        def mutation(mode):
            def change(rows, labels, context):
                index = labels['settings']
                settings = rows[index]
                if mode == 'modified':
                    settings['payload']['thread_settings']['permissions']['network'] = True
                elif mode == 'foreign_child':
                    settings['payload']['thread_id'] = 'different-child'
                elif mode == 'late':
                    ordered = [row for row in rows if row is not settings]
                    ordered.insert(len(ordered) - 1, settings)
                    self.reorder(rows, labels, ordered)
                elif mode == 'duplicate':
                    self.reorder(rows, labels, rows[:index + 1] +
                        [json.loads(json.dumps(settings))] + rows[index + 1:])
                elif mode == 'missing':
                    self.reorder(rows, labels, [row for row in rows if row is not settings])
            return change
        for mode in ('no_selected_pin', 'modified', 'foreign_child', 'late', 'duplicate', 'missing'):
            with self.subTest(mode=mode):
                self.rejected(self.episode(settings=True,
                    selected_settings=mode != 'no_selected_pin', mutate=mutation(mode)))

    def test_declaration_scope_and_provenance_remain_closed(self):
        def mutation(mode):
            def change(rows, labels, context):
                declaration = rows[labels['declaration']]
                if mode == 'integer_false':
                    declaration['metadata']['client_authored'] = 0
                elif mode == 'wrong_role':
                    declaration['payload']['role'] = 'user'
                elif mode == 'extra_command':
                    declaration['payload']['input'] = 'SOURCE_ONLY injected command'
                elif mode == 'late':
                    ordered = [row for row in rows if row is not declaration]
                    ordered.insert(len(ordered) - 1, declaration)
                    self.reorder(rows, labels, ordered)
            return change
        for mode in ('integer_false', 'wrong_role', 'extra_command', 'late'):
            with self.subTest(mode=mode):
                self.rejected(self.episode(declaration=True, mutate=mutation(mode)))

    def test_declaration_does_not_authorize_calls_or_preuse_effects(self):
        for operation, reason in (('clock', 'HOLD_UNCLASSIFIED_TOOL_CALL'),
                                  ('early_use', 'HOLD_EARLY_SAME_EPISODE_USE')):
            with self.subTest(operation=operation):
                error = self.rejected(self.episode(declaration=True, forbidden=operation), reason)
                self.assertIsInstance(error, self.obs.HoldObservationRefusal)

    def test_transport_metadata_keeps_strict_shape_and_existing_call_identity(self):
        def mutation(mode):
            def change(rows, labels, context):
                metadata = rows[labels['collaboration_call']]['metadata']
                if mode == 'integer_false':
                    metadata['client_authored'] = 0
                elif mode == 'boolean_order':
                    metadata['user_input_order'] = True
                elif mode == 'negative_order':
                    metadata['user_input_order'] = -1
                elif mode == 'extra_key':
                    metadata['fallback_token_limit_override'] = 12000
                elif mode == 'foreign_output':
                    rows[labels['collaboration_result']]['payload']['call_id'] = 'another-call'
            return change
        for mode in ('integer_false', 'boolean_order', 'negative_order', 'extra_key', 'foreign_output'):
            with self.subTest(mode=mode):
                reason = 'HOLD_UNPAIRED_TOOL_OUTPUT' if mode == 'foreign_output' else None
                self.rejected(self.episode(transport='function_call', mutate=mutation(mode)), reason)

        def assistant_injection(rows, labels, context):
            row = rows[labels['clock_neighbor']]
            row['type'] = 'response_item'
            row['payload'] = {'type': 'message', 'role': 'assistant', 'content': []}
            row['metadata'] = {'client_authored': False, 'user_input_order': 0}
        self.rejected(self.episode(mutate=assistant_injection), 'CURRENT_PUBLIC_METADATA_SHAPE')

    def test_checked_header_and_profile_gate_current_equal_ticks(self):
        self.accepted(self.episode(equal_ticks=True, profile=self.obs.OWNED_STDIO_PROFILE,
                                  version='0.153.4'))
        for profile, version in ((self.obs.NONPROTECTED_PROFILE, '0.153.4'),
                                 (self.obs.OWNED_STDIO_PROFILE, '0.164.0-alpha.11.1'),
                                 ('SOURCE_ONLY_FOREIGN_PROFILE', '0.164.0-alpha.11.1')):
            with self.subTest(profile=profile, version=version):
                self.rejected(self.episode(equal_ticks=True, profile=profile, version=version))
        for key in ('id', 'session_id'):
            def foreign_header(rows, labels, context, field=key):
                rows[0]['payload'][field] = 'foreign-identity'
            with self.subTest(foreign_header=key):
                self.rejected(self.episode(equal_ticks=True, mutate=foreign_header))

    def test_equal_tick_scope_keeps_backwards_gaps_and_cross_source_order_strict(self):
        def backwards(rows, labels, context):
            rows[labels['clock_neighbor']]['timestamp'] = rows[0]['timestamp']
        self.rejected(self.episode(mutate=backwards), 'HOLD_EVENT_ORDER')
        def ordinal_gap(rows, labels, context):
            rows[labels['clock_neighbor']]['ordinal'] += 1
        self.rejected(self.episode(equal_ticks=True, mutate=ordinal_gap))
        case = self.episode(equal_ticks=True)
        source = case[1]['path']
        lines = source.read_bytes().splitlines(keepends=True)
        source.write_bytes(b''.join(lines[:2]) + b'\n' + b''.join(lines[2:]))
        case[4]['child']['allowed_ranges'][0]['bytes'] = source.stat().st_size
        self.rejected(case)
        timestamp = '2026-01-01T00:00:01Z'
        for same_source in (False, True):
            first = {'path': 'source-a', 'timestamp': timestamp,
                     'locator': {'offset': 0, 'bytes': 1}}
            second = {'path': 'source-a' if same_source else 'source-b', 'timestamp': timestamp,
                      'locator': {'offset': 1, 'bytes': 1}}
            with self.subTest(same_source=same_source), self.assertRaisesRegex(ValueError, '^OBSERVATION_ORDER$'):
                self.obs.before(first, second)
