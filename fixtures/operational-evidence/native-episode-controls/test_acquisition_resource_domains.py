"""SOURCE_ONLY acquisition policies over owned synthetic POSIX files.

Real existing owner entry points read the fixture bytes. The only substituted
boundary is native provider authentication for an exact fixture context. No
native selection, transcript, child, executable, or archived code is used.
"""
from datetime import datetime, timedelta, timezone
import hashlib
import math
from pathlib import Path
import tempfile
import unittest
from unittest import mock

import native_test_support as support


KIB = 1024
MIB = 1024 * KIB
TURN_BYTES = 16 * MIB
TURN_ROWS = 4096
TURN_FRAME = 2 * MIB
SOURCE_PREFIX_BYTES = 128 * MIB
TURN_ID = 'source-only-acquisition-turn'


class AcquisitionResourceDomainControls(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='acquisition-domains-', dir=support.SCRATCH)
        self.addCleanup(temporary.cleanup)
        self.directory = Path(temporary.name)
        self.obs = support.load('compaction-result-observation.py')
        self.owner = support.load('compaction-source-owner-codex-app.py')
        self.number = 0

    def wire(self, ordinal, kind='event_msg', payload=None, size=None):
        timestamp = (datetime(2026, 1, 1, tzinfo=timezone.utc) + timedelta(seconds=ordinal)).isoformat().replace('+00:00', 'Z')
        row = {'timestamp': timestamp,
               'ordinal': ordinal, 'type': kind,
               'payload': dict(payload or {'type': 'token_count'})}
        if size is not None:
            row['payload']['padding'] = ''
            missing = size - len(self.obs.canonical(row)) - 1
            self.assertGreaterEqual(missing, 0, 'fixture frame too small for its JSON envelope')
            row['payload']['padding'] = 'x' * missing
        raw = self.obs.canonical(row) + b'\n'
        if size is not None:
            self.assertEqual(len(raw), size)
        return raw

    def metadata(self):
        return self.wire(0, 'session_meta', {'id': 'source-only-child',
            'session_id': 'source-only-root', 'parent_thread_id': 'source-only-root',
            'agent_path': '/root/source_only_acquisition',
            'cli_version': '0.164.0-alpha.11.1'})

    def write(self, wires):
        self.number += 1
        path = self.directory / f'fixture-{self.number}.jsonl'
        selectors = []
        whole = hashlib.sha256()
        offset = 0
        with path.open('wb') as stream:
            for index, raw in enumerate(wires):
                # Large bodies are released as each frame is written. Fixtures
                # never materialize a complete 16 MiB turn in one allocation.
                row = self.obs.json.loads(raw)
                selectors.append({'offset': offset, 'bytes': len(raw),
                    'sha256': hashlib.sha256(raw).hexdigest(),
                    'embedded_ordinal': row['ordinal'], 'physical_line': index + 1})
                stream.write(raw)
                whole.update(raw)
                offset += len(raw)
        info = path.stat()
        return {'path': path, 'selectors': selectors, 'bytes': offset,
                'physical': self.obs.identity(info), 'sha256': whole.hexdigest()}

    def context(self, fixture, *, profile=None, history_start=1):
        first = fixture['selectors'][0]
        with fixture['path'].open('rb') as stream:
            metadata = self.obs.json.loads(stream.read(first['bytes']))
        return {'profile_id': profile or self.obs.NONPROTECTED_PROFILE,
            'source_association': 'PUBLIC_BOUNDARY_CHILD_STRUCTURAL_UNQUALIFIED',
            'parent_identity': {'thread_id': 'source-only-root'},
            'actual_child_identity': {'thread_id': 'source-only-child',
                'parent_thread_id': 'source-only-root', 'agent_path': '/root/source_only_acquisition'},
            'child': {'path': str(fixture['path']), 'physical': fixture['physical'],
                'metadata': first, 'metadata_payload_digest': self.obs.digest(self.obs.canonical(metadata['payload'])),
                'history_start_ordinal': history_start,
                'allowed_ranges': [{'offset': 0, 'bytes': min(fixture['bytes'], 2 * MIB)}]}}

    def accepted(self, invoke, label):
        try:
            return invoke()
        except ValueError as error:
            self.fail(f'{label}: real owner refused a valid SOURCE_ONLY fixture: {error}')

    def refused(self, invoke, reason=None):
        try:
            invoke()
        except ValueError as error:
            if reason is not None:
                self.assertEqual(str(error), reason)
            return error
        self.fail('real owner admitted an out-of-policy SOURCE_ONLY fixture')

    def turn(self, *, rows=3, frame_bytes=None, total_bytes=None):
        if total_bytes is not None:
            rows = math.ceil(total_bytes / TURN_FRAME) + 2
        activation = self.wire(1, payload={'type': 'task_started', 'turn_id': TURN_ID})
        terminal = self.wire(rows, 'response_item', {'type': 'message', 'id': 'source-only-selected',
            'role': 'assistant', 'phase': 'commentary', 'content': [{'type': 'output_text', 'text': 'fixture'}]})
        sizes = [None] * (rows - 2)
        if frame_bytes is not None:
            self.assertEqual(rows, 3)
            sizes[0] = frame_bytes
        if total_bytes is not None:
            remaining = total_bytes - len(activation) - len(terminal)
            minimums = [len(self.wire(n, size=256)) for n in range(2, rows)]
            sizes = []
            for index in range(rows - 2):
                size = min(TURN_FRAME, remaining - sum(minimums[index + 1:]))
                sizes.append(size)
                remaining -= size
            self.assertEqual(remaining, 0)

        def wires():
            yield self.metadata()
            yield activation
            for ordinal, size in enumerate(sizes, 2):
                yield self.wire(ordinal, size=size)
            yield terminal

        fixture = self.write(wires())
        context = self.context(fixture)
        context['child_activation'] = {'locator': fixture['selectors'][1]}
        pin = {'locator': fixture['selectors'][-1]}
        retained = {'id': {'turn_id': TURN_ID}}
        extent = fixture['bytes'] - fixture['selectors'][1]['offset']
        if total_bytes is not None:
            self.assertEqual(extent, total_bytes)
        self.assertEqual(len(fixture['selectors']) - 1, rows)
        return fixture, context, pin, retained

    def scan_turn(self, case):
        _, context, pin, retained = case
        return self.owner.active_public_turn(self.obs, context, 'child', pin, retained)

    def test_complete_turn_has_separate_positive_boundaries(self):
        cases = ({'rows': 65}, {'rows': TURN_ROWS}, {'frame_bytes': 1695304},
                 {'frame_bytes': TURN_FRAME}, {'total_bytes': 2 * MIB + 1},
                 {'total_bytes': TURN_BYTES})
        for arguments in cases:
            with self.subTest(arguments=arguments):
                case = self.turn(**arguments)
                self.accepted(lambda: self.scan_turn(case), 'complete physical turn')
                fixture, _, pin, _ = case
                chosen = pin['locator']
                # The large unselected frame never becomes selected evidence.
                selected = self.obs.read_records(str(fixture['path']), [chosen],
                    [{'offset': chosen['offset'], 'bytes': chosen['bytes']}], fixture['physical'])
                self.assertEqual(len(selected['records']), 1)
                self.assertFalse(selected['host_producer_authenticated'])

    def test_complete_turn_rejects_overbounds_truncation_and_wrong_turn(self):
        for arguments in ({'rows': TURN_ROWS + 1}, {'frame_bytes': TURN_FRAME + 1},
                          {'total_bytes': TURN_BYTES + 1}):
            with self.subTest(arguments=arguments):
                self.refused(lambda: self.scan_turn(self.turn(**arguments)))
        case = self.turn()
        with case[0]['path'].open('r+b') as stream:
            stream.truncate(case[0]['bytes'] - 1)
        self.refused(lambda: self.scan_turn(case))
        case = self.turn()
        case[3]['id']['turn_id'] = 'source-only-foreign-turn'
        self.refused(lambda: self.scan_turn(case), 'CURRENT_PUBLIC_WRONG_ACTIVE_TURN')

    def test_complete_readers_refuse_physical_replacement(self):
        original_open = Path.open
        for reader in ('turn', 'prefix'):
            for moment in ('before-open', 'during-read'):
                with self.subTest(reader=reader, moment=moment):
                    case = self.turn()
                    fixture, context, _, _ = case
                    path = fixture['path']
                    replaced = []

                    def replace():
                        if not replaced:
                            replaced.append(True)
                            held = path.with_suffix('.held')
                            path.rename(held)
                            with original_open(held, 'rb') as source:
                                raw = source.read()
                            with original_open(path, 'wb') as target:
                                target.write(raw)

                    class WatchedStream:
                        def __init__(self, stream): self.stream = stream
                        def __enter__(self): self.stream.__enter__(); return self
                        def __exit__(self, *args): return self.stream.__exit__(*args)
                        def __getattr__(self, name): return getattr(self.stream, name)
                        def read(self, *args):
                            raw = self.stream.read(*args); replace(); return raw
                        def readline(self, *args):
                            raw = self.stream.readline(*args); replace(); return raw

                    def opened(candidate, *args, **kwargs):
                        if candidate == path and args and args[0] == 'rb':
                            if moment == 'before-open': replace()
                            stream = original_open(candidate, *args, **kwargs)
                            return WatchedStream(stream) if moment == 'during-read' else stream
                        return original_open(candidate, *args, **kwargs)

                    with mock.patch.object(Path, 'open', opened):
                        if reader == 'turn':
                            self.refused(lambda: self.scan_turn(case))
                        else:
                            self.refused(lambda: self.owner.sealed_prefix(self.obs, context, 'child', fixture['bytes']))
                    self.assertTrue(replaced, 'physical replacement was not injected')

    def test_selected_evidence_limits_stay_unchanged(self):
        self.assertEqual((self.obs.MAX_RECORDS, self.obs.MAX_TOTAL, self.obs.MAX_RECORD), (64, 2 * MIB, 256 * KIB))
        cases = (([256] * 64, None), ([256 * KIB], None), ([256 * KIB] * 8, None),
                 ([256] * 65, 'RECORD_COUNT_BOUND'), ([256 * KIB + 1], 'RECORD_BYTE_BOUND'),
                 ([256 * KIB] * 7 + [256 * KIB - 255, 256], 'TOTAL_RECORD_BYTE_BOUND'))
        for sizes, reason in cases:
            with self.subTest(rows=len(sizes), total=sum(sizes), reason=reason):
                fixture = self.write(self.wire(n, size=size) for n, size in enumerate(sizes))
                windows = [{'offset': s['offset'], 'bytes': s['bytes']} for s in fixture['selectors']]
                read = lambda: self.obs.read_records(str(fixture['path']), fixture['selectors'], windows, fixture['physical'])
                if reason is None:
                    self.assertEqual(len(self.accepted(read, 'selected evidence')['records']), len(sizes))
                else:
                    self.refused(read, reason)

    def test_source_prefix_streams_above_selected_limit_and_keeps_128_mib_cap(self):
        case = self.turn(total_bytes=2 * MIB + 65537)
        fixture, context, _, _ = case
        with self.subTest(operation='above-selected-limit'):
            actual = self.accepted(lambda: self.owner.sealed_prefix(self.obs, context, 'child', fixture['bytes']),
                                   'registered source prefix')
            self.assertEqual(actual['prefix_bytes'], fixture['bytes'])
            self.assertEqual(actual['prefix_sha256'], fixture['sha256'])
            self.assertEqual(actual['physical'], fixture['physical'])
        # A sparse extent checks the finite ceiling before content I/O, without
        # allocating or hashing 128 MiB merely to test an over-bound refusal.
        with fixture['path'].open('r+b') as stream:
            stream.truncate(SOURCE_PREFIX_BYTES + 1)
        with mock.patch.object(Path, 'open', side_effect=AssertionError('over-bound prefix content was opened')):
            self.refused(lambda: self.owner.sealed_prefix(self.obs, context, 'child', SOURCE_PREFIX_BYTES + 1),
                         'CURRENT_PUBLIC_PREFIX_BOUND')

    def hold_fixture(self, *, count=70, frame_bytes=None, total_bytes=None, profile=None,
                     history_start=1, historical='absent', mutate_ordinal=None):
        if total_bytes is not None:
            count = 10
        header = self.metadata()
        activation = self.wire(1, payload={'type': 'task_started', 'turn_id': TURN_ID})
        sizes = [None] * (count - 2)
        if frame_bytes is not None:
            sizes[0] = frame_bytes
        if total_bytes is not None:
            remaining = total_bytes - len(header) - len(activation)
            sizes = []
            for index in range(count - 2):
                size = min(256 * KIB, remaining - 256 * (count - 3 - index))
                sizes.append(size)
                remaining -= size
            self.assertEqual(remaining, 0)

        def wires():
            yield header
            yield activation
            for n, size in enumerate(sizes, 2):
                ordinal = mutate_ordinal[1] if mutate_ordinal and n == mutate_ordinal[0] else n
                yield self.wire(ordinal, size=size)

        fixture = self.write(wires())
        context = self.context(fixture, profile=profile, history_start=history_start)
        if historical == 'null':
            context['child']['historical_prefix'] = None
        elif historical == 'metadata':
            context['child']['historical_prefix'] = {'bytes': len(header),
                'last_embedded_ordinal': 0, 'physical_records': 1, 'sha256': hashlib.sha256(header).hexdigest()}
        return fixture, context

    def test_fresh_nonprotected_hold_covers_all_rows_through_512(self):
        for count in (70, 512):
            with self.subTest(count=count):
                fixture, context = self.hold_fixture(count=count)
                records, prefix = self.accepted(lambda: self.obs.hold_records(context), 'fresh NONPROTECTED HOLD')
                self.assertEqual([r['row']['ordinal'] for r in records], list(range(count)))
                self.assertEqual(prefix['physical_records'], count)
                self.assertEqual(prefix['prefix_bytes'], fixture['bytes'])
                self.assertEqual(prefix['prefix_sha256'], fixture['sha256'])
                self.assertFalse(prefix['host_producer_authenticated'])
        _, context = self.hold_fixture(count=513)
        self.refused(lambda: self.obs.hold_records(context), 'HOLD_RECORD_COUNT_BOUND')

    def test_other_hold_contexts_keep_64_rows(self):
        cases = ({'profile': self.obs.CURRENT_BOUNDARY_PROFILE}, {'profile': self.obs.OWNED_STDIO_PROFILE},
                 {'profile': self.obs.PROFILE}, {'history_start': 2},
                 {'historical': 'null'}, {'historical': 'metadata'})
        for arguments in cases:
            with self.subTest(arguments=arguments):
                _, context = self.hold_fixture(count=64, **arguments)
                self.assertEqual(len(self.accepted(lambda: self.obs.hold_records(context), 'legacy HOLD ceiling')[0]), 64)
                _, context = self.hold_fixture(count=65, **arguments)
                self.refused(lambda: self.obs.hold_records(context), 'HOLD_RECORD_COUNT_BOUND')

    def test_hold_keeps_prefix_frame_and_complete_coverage_guards(self):
        for arguments in ({'count': 3, 'frame_bytes': 256 * KIB}, {'total_bytes': 2 * MIB}):
            with self.subTest(positive=arguments):
                fixture, context = self.hold_fixture(**arguments)
                _, prefix = self.accepted(lambda: self.obs.hold_records(context), 'HOLD byte ceiling')
                self.assertEqual(prefix['prefix_sha256'], fixture['sha256'])
        for arguments, reason in (({'count': 3, 'frame_bytes': 256 * KIB + 1}, 'HOLD_PARTIAL_OR_OVERFLOW_FRAME'),
                                  ({'total_bytes': 2 * MIB + 1}, 'HOLD_PREFIX_BYTE_BOUND'),
                                  ({'mutate_ordinal': (66, 67)}, 'HOLD_EVENT_GAP_OR_DUPLICATE')):
            with self.subTest(negative=arguments):
                _, context = self.hold_fixture(**arguments)
                self.refused(lambda: self.obs.hold_records(context), reason)
        fixture, context = self.hold_fixture(count=70)
        header_end = context['child']['metadata']['bytes']
        context['child']['allowed_ranges'] = [{'offset': 0, 'bytes': header_end},
            {'offset': header_end + 1, 'bytes': fixture['bytes'] - header_end - 1}]
        self.refused(lambda: self.obs.hold_records(context), 'HOLD_CONTIGUOUS_RANGE_REQUIRED')

    def test_hold_history_still_detects_prohibited_use_after_row_64(self):
        exchange_id = 'e' * 64
        bind_request = {'fixture': 'SOURCE_ONLY'}
        store, session, owner = str(self.directory), 'source-only-root', 'source-only-owner'
        template = {'profile_id': self.obs.NONPROTECTED_PROFILE,
                    'source_association': 'PUBLIC_BOUNDARY_CHILD_STRUCTURAL_UNQUALIFIED'}
        bind_input = self.obs.profile_tool_input(template, self.obs.delivery_tool_input(store, session, owner, bind_request))

        def history(early_use):
            def wires():
                yield self.metadata()
                yield self.wire(1, payload={'type': 'task_started', 'turn_id': TURN_ID})
                for n, payload in ((2, {'type': 'custom_tool_call', 'name': 'exec', 'call_id': 'fixture-load', 'input': 'SOURCE_ONLY load'}),
                    (3, {'type': 'custom_tool_call_output', 'call_id': 'fixture-load'}),
                    (4, {'type': 'custom_tool_call', 'name': 'exec', 'call_id': 'fixture-exchange', 'input': 'SOURCE_ONLY exchange'}),
                    (5, {'type': 'custom_tool_call_output', 'call_id': 'fixture-exchange'})):
                    yield self.wire(n, 'response_item', payload)
                for n in range(6, 69):
                    if early_use and n == 66:
                        yield self.wire(n, 'response_item', {'type': 'custom_tool_call', 'name': 'exec',
                            'call_id': 'fixture-prohibited-use', 'input': '// COMPACTION_OBSERVATION_EXCHANGE=' + exchange_id + '\nSOURCE_ONLY'})
                    else:
                        yield self.wire(n)
                yield self.wire(69, 'response_item', {'type': 'custom_tool_call', 'name': 'exec',
                    'call_id': 'fixture-bind', 'input': bind_input})

            fixture = self.write(wires())
            context = self.context(fixture)

            def pin(n):
                locator = fixture['selectors'][n]
                return {'path': str(fixture['path']), 'physical': fixture['physical'], 'role': 'child',
                    'locator': locator, 'timestamp': f'2026-01-01T00:{n // 60:02d}:{n % 60:02d}Z',
                    'message_or_call_id': {2: 'fixture-load', 3: 'fixture-load', 4: 'fixture-exchange', 5: 'fixture-exchange'}[n]}

            prepared = {'authorization': {'load_identity': {'call': pin(2), 'result': pin(3)}},
                        'obligation': {'observation_id': 'a' * 64}}
            exchange = {'identity': exchange_id, 'records': {'call': pin(4), 'result': pin(5)}}

            def fixture_read(ctx, role, selectors):
                self.assertIs(ctx, context)
                self.assertEqual(role, 'child')
                self.assertTrue(all(selector in fixture['selectors'] for selector in selectors))
                return self.obs.read_records(str(fixture['path']), selectors,
                    context['child']['allowed_ranges'], fixture['physical'])

            with mock.patch.object(self.obs, '_nonprotected_read_records', fixture_read):
                return self.obs.history_with_priors(context, prepared, exchange, bind_request,
                    store, session, owner, {}, {})

        with self.subTest(operation='complete-history'):
            prefix = self.accepted(lambda: history(False), 'complete 70-row pre-USE history')
            self.assertEqual(prefix['physical_records'], 70)
        with self.subTest(operation='prohibited-use-after-64'):
            error = self.refused(lambda: history(True), 'HOLD_EARLY_SAME_EPISODE_USE')
            self.assertIsInstance(error, self.obs.HoldObservationRefusal)
            self.assertEqual(error.evidence['prefix']['physical_records'], 70)
            self.assertEqual(error.evidence['record']['embedded_ordinal'], 66)

    def test_other_profiles_keep_legacy_turn_and_prefix_limits(self):
        for profile in (self.obs.OWNED_STDIO_PROFILE, 'SOURCE_ONLY_FOREIGN_PROFILE'):
            with self.subTest(profile=profile, boundary='legacy-turn-admitted'):
                case = self.turn(rows=64)
                case[1]['profile_id'] = profile
                self.accepted(lambda: self.scan_turn(case), 'legacy complete turn')
            for arguments in ({'rows': 65}, {'frame_bytes': 256 * KIB + 1}, {'total_bytes': 2 * MIB + 1}):
                with self.subTest(profile=profile, overbound=arguments):
                    case = self.turn(**arguments)
                    case[1]['profile_id'] = profile
                    self.refused(lambda: self.scan_turn(case))
            with self.subTest(profile=profile, boundary='legacy-prefix'):
                fixture, context, _, _ = self.turn(total_bytes=2 * MIB)
                context['profile_id'] = profile
                prefix = self.accepted(lambda: self.owner.sealed_prefix(self.obs, context, 'child', 2 * MIB),
                                       'legacy source prefix ceiling')
                self.assertEqual(prefix['prefix_bytes'], 2 * MIB)
                self.refused(lambda: self.owner.sealed_prefix(self.obs, context, 'child', 2 * MIB + 1),
                             'CURRENT_PUBLIC_PREFIX_BOUND')

    def test_complete_turn_refuses_duplicate_keys_and_malformed_frames(self):
        malformed = (
            (b'{"ordinal":2,"type":"event_msg","payload":{},"payload":{}}', 'DUPLICATE_JSON_KEY'),
            (b'{"ordinal":2,"type":"event_msg","payload":', None),
            (b'{"ordinal":2,"type":"event_msg","payload":[]}', 'CURRENT_PUBLIC_TURN_FRAME'),
            (b'[{"ordinal":2,"type":"event_msg","payload":{}}]', 'CURRENT_PUBLIC_TURN_FRAME'),
        )
        for body, reason in malformed:
            with self.subTest(body=body.decode(), reason=reason):
                case = self.turn()
                fixture = case[0]
                location = fixture['selectors'][2]
                self.assertLessEqual(len(body) + 1, location['bytes'])
                # Change only the unselected frame; preserve the header, final
                # selected record, file identity and complete physical extent.
                with fixture['path'].open('r+b') as stream:
                    stream.seek(location['offset'])
                    stream.write(body.ljust(location['bytes'] - 1, b' ') + b'\n')
                self.refused(lambda: self.scan_turn(case), reason)

    def test_source_prefix_hashes_exact_128_mib_with_bounded_reads(self):
        fixture, context, _, _ = self.turn()
        path = fixture['path']
        seed = path.read_bytes()
        with path.open('r+b') as stream:
            stream.truncate(SOURCE_PREFIX_BYTES)
        expected = hashlib.sha256(seed)
        zeros = b'\0' * 65536
        remaining = SOURCE_PREFIX_BYTES - len(seed)
        while remaining:
            count = min(len(zeros), remaining)
            expected.update(zeros[:count])
            remaining -= count
        original_open = Path.open
        reads = {'bytes': 0, 'maximum_request': 0, 'calls': 0}
        test = self

        class BoundedStream:
            def __init__(self, stream): self.stream = stream
            def __enter__(self): self.stream.__enter__(); return self
            def __exit__(self, *args): return self.stream.__exit__(*args)
            def __getattr__(self, name): return getattr(self.stream, name)
            def read(self, count=-1):
                test.assertGreater(count, 0, 'source prefix attempted an unbounded read')
                test.assertLessEqual(count, 65536, 'source prefix exceeded the streaming chunk bound')
                raw = self.stream.read(count)
                reads['bytes'] += len(raw)
                reads['maximum_request'] = max(reads['maximum_request'], count)
                reads['calls'] += 1
                return raw

        def opened(candidate, *args, **kwargs):
            stream = original_open(candidate, *args, **kwargs)
            return BoundedStream(stream) if candidate == path and args and args[0] == 'rb' else stream

        with mock.patch.object(Path, 'open', opened):
            actual = self.accepted(lambda: self.owner.sealed_prefix(self.obs, context, 'child', SOURCE_PREFIX_BYTES),
                                   'exact registered source prefix ceiling')
        self.assertEqual(actual['prefix_bytes'], SOURCE_PREFIX_BYTES)
        self.assertEqual(actual['prefix_sha256'], expected.hexdigest())
        self.assertEqual(reads['bytes'], SOURCE_PREFIX_BYTES)
        self.assertGreater(reads['calls'], 1)
        self.assertLessEqual(reads['maximum_request'], 65536)


if __name__ == '__main__':
    unittest.main(verbosity=2)
