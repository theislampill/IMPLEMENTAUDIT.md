"""Focused source controls; Win32 APIs are modeled, never host acceptance."""
import copy
import base64
import ctypes
from ctypes import wintypes as w
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import types
import unittest
from unittest.mock import patch

HERE = Path(__file__).absolute().parent
ROOT = HERE.parents[3]


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


builder = load(HERE / 'build_release_acl.py', 'bundle_builder')
generator = load(HERE / 'make_acl_stage_b.py', 'acl_generator')
rehearsal = load(HERE / 'rehearse_lifecycle.py', 'lifecycle_rehearsal')


class Call:
    def __init__(self, function):
        self.function = function

    def __call__(self, *args):
        return self.function(*args)


class WinApiModel:
    """Bounded fake security descriptors to exercise source refusal branches."""
    def __init__(self, sids=(1000, 22), *, owner=1000, control=0x1004,
                 kinds=None, flags=None, directory_flags=0x10, security_error=0,
                 null_dacl=False):
        self.held = []
        self.sids = sids
        self.owner = self.sid(owner)
        self.user = self.sid(1000)
        self.dacl = ctypes.create_string_buffer(16)
        self.descriptor = ctypes.create_string_buffer(16)
        self.control, self.directory_flags = control, directory_flags
        self.security_error, self.null_dacl = security_error, null_dacl
        self.aces = []
        for i, sid in enumerate(sids):
            ace = ctypes.create_string_buffer(16)
            ace[0] = bytes([(kinds or [0] * len(sids))[i]])
            ace[1] = bytes([(flags or [0] * len(sids))[i]])
            ctypes.memmove(ctypes.addressof(ace) + 4, (1).to_bytes(4, 'little'), 4)
            ctypes.memmove(ctypes.addressof(ace) + 8, sid.to_bytes(4, 'little'), 4)
            self.aces.append(ace)
        self.kernel = types.SimpleNamespace(
            GetCurrentProcess=Call(lambda: 7), CloseHandle=Call(lambda handle: 1),
            LocalFree=Call(lambda pointer: None), CreateFileW=Call(lambda *args: 9),
            GetFileInformationByHandle=Call(self.file_info))
        self.advapi = types.SimpleNamespace(
            OpenProcessToken=Call(self.open_token), GetTokenInformation=Call(self.token_info),
            EqualSid=Call(lambda a, b: self.value(a) == self.value(b)),
            IsValidSid=Call(lambda sid: bool(self.address(sid))),
            CreateWellKnownSid=Call(self.known), ConvertSidToStringSidW=Call(self.sid_text),
            GetSecurityInfo=Call(self.security), GetSecurityDescriptorControl=Call(self.descriptor_control),
            GetAclInformation=Call(self.acl_info), GetAce=Call(self.ace))
        self.kernel.CreateDirectoryW = Call(lambda *args: 0)
        self.advapi.ConvertStringSecurityDescriptorToSecurityDescriptorW = Call(lambda *args: 0)

    def sid(self, value):
        buf = ctypes.create_string_buffer(value.to_bytes(4, 'little') + b'\0' * 12)
        self.held.append(buf)
        return buf

    @staticmethod
    def address(value):
        return ctypes.cast(value, ctypes.c_void_p).value

    def value(self, value):
        return int.from_bytes(ctypes.string_at(self.address(value), 4), 'little')

    @staticmethod
    def set_ref(reference, type_, value):
        ctypes.cast(reference, ctypes.POINTER(type_))[0] = value

    def open_token(self, process, access, out):
        self.set_ref(out, w.HANDLE, 8)
        return 1

    def token_info(self, token, kind, buffer, size, out):
        self.set_ref(out, w.DWORD, ctypes.sizeof(ctypes.c_void_p))
        if buffer is not None:
            self.set_ref(buffer, ctypes.c_void_p, ctypes.addressof(self.user))
            return 1
        return 0

    def known(self, kind, domain, buffer, size):
        ctypes.memmove(buffer, int(kind).to_bytes(4, 'little'), 4)
        return 1

    def sid_text(self, sid, output):
        string = ctypes.create_unicode_buffer('SIMULATED-SID-' + str(self.value(sid)))
        self.held.append(string)
        self.set_ref(output, ctypes.c_void_p, ctypes.addressof(string))
        return 1

    def file_info(self, handle, buffer):
        ctypes.memmove(buffer, self.directory_flags.to_bytes(4, 'little'), 4)
        return 1

    def security(self, handle, kind, mask, owner, group, dacl, sacl, descriptor):
        self.set_ref(owner, ctypes.c_void_p, ctypes.addressof(self.owner))
        self.set_ref(dacl, ctypes.c_void_p, 0 if self.null_dacl else ctypes.addressof(self.dacl))
        self.set_ref(descriptor, ctypes.c_void_p, ctypes.addressof(self.descriptor))
        return self.security_error

    def descriptor_control(self, descriptor, control, revision):
        self.set_ref(control, w.WORD, self.control)
        self.set_ref(revision, w.DWORD, 1)
        return 1

    def acl_info(self, dacl, values, size, kind):
        values[0] = len(self.aces)
        return 1

    def ace(self, dacl, index, output):
        self.set_ref(output, ctypes.c_void_p, ctypes.addressof(self.aces[index]))
        return 1

    def check(self, function):
        os_before = function.__globals__['os']
        function.__globals__['os'] = types.SimpleNamespace(name='nt')
        try:
            with patch.object(ctypes, 'WinDLL', lambda name, **kw: (
                    self.kernel if name == 'kernel32' else self.advapi), create=True):
                return function('/SIMULATED/store', create=False)
        finally:
            function.__globals__['os'] = os_before


class DriverBundle(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix='dg17-bundle-', dir=ROOT / '.IMPLEMENTAUDIT')
        cls.directory = Path(cls.temp.name)
        cls.author = cls.directory / 'first' / 'author'
        cls.manifest = builder.build(builder.BASE, cls.author, ROOT)
        cls.op = json.loads((cls.author / 'OPERATION_A.json').read_bytes())
        cls.stage_a = load(cls.author / 'stage_a.py', 'new_stage_a')
        cls.stage_b = load(cls.author / 'stage_b.py', 'new_stage_b')
        cls.old_stage_b = load(HERE.parent / 'author/stage_b.py', 'old_stage_b')

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_author_pin_closure(self):
        for item in self.op['readset']:
            if builder.relative(item['path'], str(self.author)) is not None:
                self.assertEqual(item, builder.pin(item['path']))
        self.assertIn(self.manifest['operation_A_sha256'],
                      (self.author / 'parent_launch_a.py').read_text())
        self.assertIn(builder.pin(self.author / 'stage_b.py')['sha256'],
                      (self.author / 'parent_launch_b.py').read_text())

    def test_b2_product_pin_closure(self):
        constructor = load(self.author / 'positive_hook_constructor.py', 'new_ctor')
        for role, name in [('binding_owner', 'host-session-binding.py'),
                           ('handler', 'host-stop-interlock.py'),
                           ('validator', 'validate-run-root.sh'), ('custody', 'canonical_custody.py')]:
            self.assertEqual(constructor.PINS[role], builder.pin(ROOT / 'skills/implementaudit/scripts' / name)['sha256'])
        self.assertEqual(self.op['binding_owner']['sha256'], constructor.PINS['binding_owner'])

    def test_limits_and_historical_issuer_preserved_without_admission(self):
        old = json.loads((builder.BASE / 'OPERATION_A.json').read_bytes())
        self.assertEqual(self.op['limits'], old['limits'])
        self.assertEqual(self.op['issuer'], old['issuer'])
        self.assertFalse(self.op['preparation']['native_admission'])
        self.assertTrue(self.op['preparation']['unverified_inputs'])
        self.assertEqual(self.manifest['original14_custody_unknown_differences'], 14)

    def test_windows_paths_relocate_under_posix(self):
        self.assertEqual(builder.relative(r'C:\base\author\stage_a.py', r'C:\base\author').name, 'stage_a.py')
        self.assertIsNone(builder.relative(r'C:\base\author-other\stage_a.py', r'C:\base\author'))
        for item in self.op['readset']:
            self.assertNotIn('FABLE_WORK_WIN', item['path'])

    def test_refuses_overwrite(self):
        with self.assertRaisesRegex(ValueError, 'Fresh'):
            builder.build(builder.BASE, self.author, ROOT)

    def test_refuses_aliased_output(self):
        link = self.directory / 'alias'
        link.symlink_to(self.directory / 'first', target_is_directory=True)
        with self.assertRaisesRegex(ValueError, 'Aliased'):
            builder.build(builder.BASE, link / 'elsewhere', ROOT)

    def test_refuses_hardlinked_input(self):
        first = self.directory / 'one'
        first.write_bytes(b'SIMULATED')
        second = self.directory / 'two'
        os.link(first, second)
        with self.assertRaisesRegex(ValueError, 'multiply linked'):
            builder.pin(first)

    def test_state_baseline_follows_selected_head(self):
        repo = self.directory / 'state-check'
        repo.mkdir()
        root = repo / 'run'
        root.mkdir()
        (root / '.controller').write_text('controller_id=simulated-dg17\n')
        self.stage_a.write_state(root, repo, 'G0001', 'SIMULATED', 'test',
                                 self.op['source_head'], self.op['source_tree'])
        self.assertIn('| Baseline ref | ' + self.op['source_head'] + ' |',
                      (root / 'STATE.md').read_text())

    def test_acl_modeled_positive_user_system_only(self):
        self.assertEqual(len(WinApiModel().check(self.stage_b.private_store_directory)['entries']), 2)

    def test_acl_historical_admin_acceptance_and_successor_refusal(self):
        self.assertEqual(len(WinApiModel((1000, 22, 26)).check(
            self.old_stage_b.private_store_directory)['entries']), 3)
        with self.assertRaisesRegex(RuntimeError, 'another principal'):
            WinApiModel((1000, 22, 26)).check(self.stage_b.private_store_directory)

    def test_acl_modeled_adversarial_population(self):
        models = [
            WinApiModel(owner=2000), WinApiModel((1000, 22, 2000)),
            WinApiModel(kinds=[1, 0]), WinApiModel(flags=[0x10, 0]),
            WinApiModel((22,)), WinApiModel(control=4), WinApiModel(null_dacl=True),
            WinApiModel(directory_flags=0x410), WinApiModel(directory_flags=0),
            WinApiModel(security_error=5),
        ]
        for index, model in enumerate(models):
            with self.subTest(index=index), self.assertRaises(RuntimeError):
                model.check(self.stage_b.private_store_directory)

    def test_receipt_deadlines_keep_original_bounds(self):
        b = self.stage_b
        self.assertEqual(b.qualification_receipt_deadline(180, 90), 90)
        self.assertTrue(b.terminal_receipt_on_time(90, 180, 90))
        self.assertFalse(b.terminal_receipt_on_time(90.001, 180, 90))
        self.assertEqual(b.qualification_recv_remaining(85, 180, 90, 30), 5)
        with self.assertRaises(RuntimeError):
            b.qualification_recv_remaining(90, 180, 90, 30)

    def test_selected_identity_refuses_mismatched_completion(self):
        b = self.stage_b
        trusted = dict(source='project', sourcePath='/SIMULATED/hooks.json', eventName='stop',
                       displayOrder=0, handlerType='command', statusMessage='SIMULATED')
        run = dict(trusted, id='SIMULATED-one', executionMode='sync', scope='turn', status='running')
        start = dict(method='hook/started', params=dict(threadId='t', turnId='q', run=run))
        fence = dict(selected_run_id=None, started=[start], completed=[])
        b.observe_selected_identity(fence, start, trusted, 't', 'q')
        done = copy.deepcopy(start)
        done['method'] = 'hook/completed'
        done['params']['run'].update(id='SIMULATED-another', status='completed')
        fence['completed'].append(done)
        with self.assertRaises(AssertionError):
            b.observe_selected_identity(fence, done, trusted, 't', 'q')

    def test_parent_a_command_fits_original_bound_before_window_write(self):
        parent = load(self.author / 'parent_launch_a.py', 'new_parent_a')
        path = self.author / 'stage_a.py'
        argv = [str(path), '--grant', 'SIMULATED-SIZE-ONLY', '--window-start-ns', '123456789']
        old_encoded = base64.b64encode(path.read_bytes()).decode()
        old_loader = 'import base64;exec(base64.b64decode(' + repr(old_encoded) + '))'
        self.assertGreaterEqual(len(subprocess.list2cmdline(['python.exe', '-c', old_loader])), 30000)
        loader = parent.driver_loader(path, argv)
        compile(loader, 'SIMULATED-parent-command', 'exec')
        self.assertLess(len(subprocess.list2cmdline(['python.exe', '-I', '-S', '-B', '-c', loader])), 30000)
        self.assertIn(parent.DRIVER_SHA, loader)
        text = (self.author / 'parent_launch_a.py').read_text()
        self.assertLess(text.index(' assert len(subprocess.list2cmdline(command))<30000'),
                        text.index(' save(window,'))

    def test_parent_capture_keeps_digest_and_physical_substitution_refusal(self):
        parent = load(self.author / 'parent_launch_a.py', 'parent_capture')
        path = self.directory / 'capture-fixture'
        path.write_bytes(b'SIMULATED exact buffer')
        expected = builder.pin(path)['sha256']
        # Windows open flags have no POSIX behavior; only the unchanged capture
        # identity/hash predicates are exercised here, never a Windows launch.
        with patch.object(os, 'O_BINARY', 0, create=True), patch.object(os, 'O_NOINHERIT', 0, create=True):
            self.assertEqual(parent.capture(path, expected, keep=True), path.read_bytes())
            with self.assertRaises(AssertionError):
                parent.capture(path, '0' * 64, keep=True)
            physical = path.stat()
            with self.assertRaises(AssertionError):
                parent.capture(path, expected, physical=(physical.st_dev, physical.st_ino + 1, physical.st_nlink))

    def test_process_guard_accepts_codex_only_as_binding_data(self):
        allowed = {'python': str(Path(sys.executable).resolve()),
                   'bash': str(Path(shutil.which('bash')).resolve()),
                   'git': str(Path(shutil.which('git')).resolve())}
        owner = str((self.directory / 'source-owner.sh').resolve())
        rehearsal.admit_deterministic_process(
            [allowed['python'], '-I', '-S', '-B', '/SIMULATED/host-session-binding.py',
             '--store', '/SIMULATED/store', 'bind', '--host-id', 'codex'], allowed, {owner})
        rehearsal.admit_deterministic_process([allowed['bash'], owner, '--host-id', 'codex'],
                                              allowed, {owner})
        for command, shell in [
                (['/SIMULATED/codex', 'app-server'], False),
                ([allowed['python'], 'app-server'], False),
                ([allowed['bash'], '-c', 'printf ok; codex app-server'], False),
                ([allowed['bash'], '-lc', 'codex exec'], False),
                ([allowed['bash'], '/SIMULATED/foreign-owner.sh'], False),
                ([allowed['bash'], owner], True),
                ('codex app-server', False)]:
            with self.subTest(command=command, shell=shell), self.assertRaises(AssertionError):
                rehearsal.admit_deterministic_process(command, allowed, {owner}, shell=shell)

    def test_identity_diagnostic_preserves_each_original_refusal(self):
        path = self.directory / 'identity-diagnostic'
        path.write_bytes(b'SIMULATED content must not be in the diagnostic')
        fields = ('st_dev', 'st_ino', 'st_mode', 'st_nlink', 'st_size', 'st_mtime_ns', 'st_ctime_ns')
        original = os.fstat
        for field in fields:
            def changed(fd):
                values = {key: getattr(original(fd), key) for key in fields}
                values[field] += 1
                return types.SimpleNamespace(**values)
            with self.subTest(field=field), patch.object(os, 'fstat', changed):
                with self.assertRaisesRegex(ValueError, 'Input identity changed before read') as caught:
                    builder.pin(path)
                message = str(caught.exception)
                facts = json.loads(message.split(': ', 1)[1])
                self.assertEqual(facts['mismatch_fields'], [field])
                self.assertEqual(set(facts['before']), set(fields))
                self.assertEqual(set(facts['opened']), set(fields))
                self.assertEqual(facts['python_version'], sys.version.split()[0])
                self.assertNotIn(str(path), message)
                self.assertNotIn('content must not', message)

    def test_failure_summary_keeps_first_source_predicate_and_no_authority(self):
        fixture = rehearsal.Fixture.__new__(rehearsal.Fixture)
        fixture.work = self.directory / 'failed-fixture'
        fixture.case = fixture.work / 'SIMULATED-case'
        fixture.mode = 'full'
        out = fixture.case / 'evidence/stage-B01'
        out.mkdir(parents=True)
        rehearsal.save(out / '03-owned-bind.json', {'exit': 2, 'stderr': 'SIMULATED first predicate'})
        rehearsal.save(out / 'POST_B.json', {'status': 'STOPPED_TEARDOWN_UNKNOWN_NO_RETRY',
                       'error': 'SIMULATED first predicate', 'cleanup': {'known': False}})
        fixture.preserve_failure(RuntimeError('SIMULATED cleanup exception'))
        result = json.loads((fixture.work / 'REHEARSAL_RESULT.json').read_bytes())
        self.assertEqual(result['result'], 'SOURCE_REHEARSAL_REFUSED')
        self.assertEqual(result['stages']['B']['error'], 'SIMULATED first predicate')
        self.assertEqual(result['failed_source_commands'][0]['exit'], 2)
        self.assertEqual(result['authority'], 'NONE')
        self.assertEqual(result['genuine_codex_turns'], 0)
        self.assertFalse(result['native_acceptance'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
