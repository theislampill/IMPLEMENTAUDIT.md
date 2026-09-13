#!/usr/bin/env python3
"""Focused real RETURN member-admission controls using synthetic owned records."""
import builtins
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import sys
import unittest
from unittest import mock

ROOT = Path(os.environ['IMPLEMENTAUDIT_F01_SOURCE_ROOT']).resolve()
spec = importlib.util.spec_from_file_location('retained_chain_support',
    ROOT / 'tests/compaction-result-consumer.test.py')
support = importlib.util.module_from_spec(spec); spec.loader.exec_module(support)


def pin(path):
    raw = path.read_bytes()
    return {'path': str(path), 'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}


class MemberPreflightTests(unittest.TestCase):
    def setUp(self):
        self.chain = support.ProspectiveChainTests(); self.chain.setUp()
        self.reserved, self.observed, bound = self.chain.bound_observation()
        self.evidence = self.chain.actual_result(self.reserved, self.observed, bound)
        self.returned = self.chain.typed_value('child', self.evidence['child_final'])
        self.result_path = Path(self.returned['result_bytes_identity']['path'])
        self.body = json.loads(self.result_path.read_bytes())
        path = ROOT / 'skills/implementaudit/scripts/compaction-audit-pending.py'
        spec = importlib.util.spec_from_file_location('member_preflight_owner', path)
        self.owner = importlib.util.module_from_spec(spec); spec.loader.exec_module(self.owner)
        self.opened = []

    def member(self, name, size):
        path = self.result_path.parent / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b'x' * size)
        return path

    def publish_members(self, members):
        self.body['members'] = members
        self.result_path.write_text(json.dumps(self.body, sort_keys=True), encoding='utf-8')
        self.returned['result_bytes_identity'] = pin(self.result_path)
        text = '```json\n' + json.dumps(self.returned, sort_keys=True) + '\n```'
        self.evidence['child_final'] = self.chain.message('child', text, 'final_answer')
        self.evidence['parent_delivery'] = self.chain.row('parent', 'response_item', {
            'type': 'agent_message', 'id': 'member-result-delivery',
            'author': '/root/' + self.chain.child, 'recipient': '/root',
            'content': [{'type': 'input_text', 'text':
                'Message Type: FINAL_ANSWER\nTask name: /root\nSender: /root/' +
                self.chain.child + '\nPayload:\n' + text}]})
        return {'child_id': self.chain.child, 'observation_id': self.observed['observation_id'],
                'result_evidence': self.evidence}

    def invoke(self, request, watched=(), wrap_stream=None):
        original_open = builtins.open
        watched = {Path(path) for path in watched}
        def observe_open(path, *args, **kwargs):
            selected = Path(path) in watched
            if selected:
                self.opened.append(str(path))
            stream = original_open(path, *args, **kwargs)
            return wrap_stream(stream, Path(path)) if selected and wrap_stream else stream
        stdin = io.TextIOWrapper(io.BytesIO(json.dumps(request).encode()), encoding='utf-8')
        stdout = io.StringIO()
        argv = ['compaction-audit-pending.py', '--store', str(self.chain.fx.store),
                '--session', self.chain.fx.session, '--owner-id', 'host-owner', 'return']
        before = self.chain.state_bytes()
        with mock.patch.dict(os.environ, self.chain.fx.env, clear=True), mock.patch.object(sys, 'argv', argv), \
             mock.patch.object(sys, 'stdin', stdin), mock.patch.object(sys, 'stdout', stdout), \
             mock.patch('builtins.open', side_effect=observe_open):
            code = self.owner.main()
        result = json.loads(stdout.getvalue())
        if code:
            self.assertEqual(self.chain.state_bytes(), before)
            self.assertEqual(result['status'], 'PENDING_OPERATION_REFUSED')
        self.assertEqual(result['authority'], 'NONE')
        return code, result

    def test_foreign_member_never_opened(self):
        foreign = self.chain.fx.root / 'outside-result.bin'
        foreign.write_bytes(b'owned synthetic canary')
        request = self.publish_members([pin(foreign)])
        code, result = self.invoke(request, [foreign])
        self.assertEqual(code, 2)
        self.assertIn('FOREIGN_OR_DUPLICATE_RESULT_MEMBER', result['reason'])
        self.assertEqual(self.opened, [], 'Foreign member content was opened before admission')

    def test_duplicate_member_never_reread(self):
        member = self.member('member.bin', 32)
        request = self.publish_members([pin(member), pin(member)])
        code, result = self.invoke(request, [member])
        self.assertEqual(code, 2)
        self.assertIn('FOREIGN_OR_DUPLICATE_RESULT_MEMBER', result['reason'])
        self.assertLessEqual(len(self.opened), 1, 'Duplicate member was opened twice')

    def test_over_budget_member_never_opened(self):
        first = self.member('first.bin', 1024 * 1024)
        second = self.member('second.bin', 1024 * 1024)
        request = self.publish_members([pin(first), pin(second)])
        code, result = self.invoke(request, [second])
        self.assertEqual(code, 2)
        self.assertIn('RESULT_CLOSURE_BYTE_BOUND', result['reason'])
        self.assertEqual(self.opened, [], 'Cumulative budget was checked after opening excess member')

    def test_exact_two_mib_legitimate_closure_is_accepted(self):
        first = self.member('first.bin', 1024 * 1024)
        second = self.member('nested/second.bin', 1000)
        for _ in range(6):
            self.body['members'] = [pin(first), pin(second)]
            raw = json.dumps(self.body, sort_keys=True).encode()
            required = 2 * 1024 * 1024 - len(raw) - first.stat().st_size
            if second.stat().st_size == required:
                break
            second.write_bytes(b'y' * required)
        request = self.publish_members([pin(first), pin(second)])
        self.assertEqual(self.result_path.stat().st_size + first.stat().st_size + second.stat().st_size,
                         2 * 1024 * 1024)
        code, result = self.invoke(request, [first, second])
        self.assertEqual(code, 0, result)
        self.assertEqual(result['status'], 'SUCCEEDED')
        self.assertEqual(len(result['identity']['members']), 2)
        self.assertEqual(len(self.opened), 2)
        self.assertTrue(self.chain.fx.pending('status')['pending'], 'RETURN alone consumed pending')
        self.assertEqual(result['actual_child_result_consumer'], 'UNQUALIFIED')

    def test_declared_size_mismatch_is_refused_before_open(self):
        member = self.member('member.bin', 32)
        value = pin(member); value['bytes'] += 1
        request = self.publish_members([value])
        code, result = self.invoke(request, [member])
        self.assertEqual(code, 2)
        self.assertIn('ARTIFACT_BYTE_COUNT', result['reason'])
        self.assertEqual(self.opened, [])

    def test_replaced_member_after_admission_is_refused_before_content_open(self):
        member = self.member('member.bin', 32)
        request = self.publish_members([pin(member)])
        adapter = self.owner.OBSERVATION
        original = adapter.artifact_preflight
        swapped = []
        def replace_after_admission(value, maximum=1024 * 1024):
            admitted = original(value, maximum)
            if Path(value['path']) == member and not swapped:
                replacement = self.member('replacement.bin', 32)
                os.replace(replacement, member)
                swapped.append(True)
            return admitted
        with mock.patch.object(adapter, 'artifact_preflight', side_effect=replace_after_admission):
            code, result = self.invoke(request, [member])
        self.assertEqual(code, 2)
        self.assertIn('ARTIFACT_ADMISSION_CHANGED', result['reason'])
        self.assertEqual(self.opened, [])

    def test_member_changed_during_read_still_refuses(self):
        member = self.member('member.bin', 32)
        request = self.publish_members([pin(member)])
        class ChangedStream:
            def __init__(self, stream, path): self.stream, self.path = stream, path
            def __enter__(self): return self
            def __exit__(self, *args): self.stream.close()
            def fileno(self): return self.stream.fileno()
            def read(self, count):
                raw = self.stream.read(count)
                self.path.write_bytes(raw + b'changed')
                return raw
        code, result = self.invoke(request, [member], ChangedStream)
        self.assertEqual(code, 2)
        self.assertIn('ARTIFACT_PIN_CHANGED', result['reason'])
        self.assertEqual(len(self.opened), 1)


if __name__ == '__main__':
    unittest.main(verbosity=2)
