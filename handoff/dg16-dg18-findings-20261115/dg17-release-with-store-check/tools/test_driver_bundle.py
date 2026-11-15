"""Focused source controls; Win32 APIs are modeled, never host acceptance."""
import ast
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


def store_fixture_functions(**overrides):
    """Load helper source only; never import _winapi or run a Windows case here."""
    source = ast.parse((HERE / 'test_store_custody.py').read_text())
    selected = [node for node in source.body if isinstance(node, ast.FunctionDef) or (
        isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and
        target.id in {'POWERSHELL', 'OWNER_QUERY', 'DACL_SETUP'} for target in node.targets))]
    namespace = dict(base64=base64, json=json, os=os, stat=__import__('stat'),
                     subprocess=None, rows=[], bad=0, preconditions=[], me='SIMULATED\\User')
    exec(compile(ast.Module(body=selected, type_ignores=[]), 'store-fixture-controls', 'exec'), namespace)
    namespace.update(overrides)
    return namespace


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

    def test_store_fixture_sets_and_verifies_owner_before_acl_perturbation(self):
        calls = []
        state = {'owner': 'S-1-5-32-544', 'user': 'S-1-5-21-1000'}
        def acl(path, *args):
            calls.append(('icacls', args))
            if args[0] == '/setowner':
                state['owner'] = state['user']
        def facts(path):
            calls.append(('owner', state['owner']))
            return state.copy()
        def check(path):
            calls.append(('baseline', str(path)))
            self.assertEqual(state['owner'], state['user'])
            return {'owner': state['owner'], 'protected': True}
        def run(command, **kwargs):
            calls.append(('replace-dacl', kwargs['env']['DG17_FIXTURE_DACL_PATH']))
            return types.SimpleNamespace(returncode=0, stdout='', stderr='')
        ns = store_fixture_functions(work=self.directory, icacls=acl, owner_facts=facts, check=check,
                                     subprocess=types.SimpleNamespace(run=run))
        ns['private'](self.directory / 'new-private', ['*S-1-5-32-544:(OI)(CI)F'])
        self.assertEqual([entry[0] for entry in calls],
                         ['icacls', 'owner', 'replace-dacl', 'owner', 'baseline', 'icacls'])
        self.assertEqual(calls[0][1], ('/setowner', 'SIMULATED\\User'))
        self.assertEqual(calls[-1][1], ('/grant:r', '*S-1-5-32-544:(OI)(CI)F'))
        self.assertEqual(ns['preconditions'][-1]['check'], 'private user+SYSTEM baseline')

    def test_store_fixture_replaces_residual_acl_class_before_intended_perturbation(self):
        admin, creator, everyone = 'S-1-5-32-544', 'S-1-3-0', 'S-1-1-0'
        user, system = 'S-1-5-21-1000', 'S-1-5-18'
        # Cases include both observed principals and an unrelated residual entry.
        for index, residual in enumerate([{admin}, {creator}, {admin, creator},
                                         {everyone, 'S-1-5-21-2000'}]):
            grants = set(residual)
            observations = []
            def acl(path, *args):
                if args[0] == '/inheritance:r':
                    grants.update({user, system})
                elif args[0] == '/remove:g':
                    grants.discard(args[1].lstrip('*'))
                elif args[0] == '/grant:r':
                    grants.add(args[1].split(':', 1)[0].lstrip('*'))
            def run(command, **kwargs):
                # Model only the external ACL replacement; real factory and
                # baseline/negative classification run unchanged on Linux.
                grants.clear()
                grants.update({user, system})
                return types.SimpleNamespace(returncode=0, stdout='', stderr='')
            def check(path):
                observations.append(set(grants))
                foreign = grants - {user, system}
                if foreign:
                    raise RuntimeError('store custody refused: access granted to another principal ' + sorted(foreign)[0])
                return {'owner': user, 'protected': True}
            ns = store_fixture_functions(work=self.directory, icacls=acl, check=check,
                subprocess=types.SimpleNamespace(run=run),
                owner_facts=lambda p: {'owner': user, 'user': user})
            for suffix, extra in [('positive', []), ('admin', ['*' + admin + ':(OI)(CI)F']),
                                  ('everyone-write', ['*' + everyone + ':(W)']),
                                  ('everyone-read', ['*' + everyone + ':(R)'])]:
                grants.clear(); grants.update(residual); observations.clear()
                expected = 'REFUSED' if extra else 'PASS'
                reason = 'access granted to another principal ' + (admin if suffix == 'admin' else everyone)
                with self.subTest(residual=residual, perturbation=suffix):
                    ns['case'](suffix, expected,
                        lambda: check(ns['private'](self.directory / ('class-' + str(index) + '-' + suffix), extra)),
                        reason if extra else None)
                    row = ns['rows'][-1]
                    self.assertTrue(row['ok'], row)
                    self.assertEqual(observations[0], {user, system})
                    if extra:
                        self.assertEqual(observations[-1], {user, system, admin if suffix == 'admin' else everyone})

    def test_store_fixture_dacl_writer_is_fixed_module_free_and_bounded(self):
        captured = []
        def run(command, **kwargs):
            captured.append((command, kwargs))
            return types.SimpleNamespace(returncode=0, stdout='', stderr='')
        ns = store_fixture_functions(subprocess=types.SimpleNamespace(run=run),
            os=types.SimpleNamespace(environ={'SIMULATED': 'yes'}))
        self.assertIn('set_private_dacl', ns, 'fresh fixture needs complete independent DACL replacement')
        fixture = self.directory / "literal-'path; no command"
        ns['set_private_dacl'](fixture)
        command, kwargs = captured[0]
        self.assertEqual(command[:4], [r'C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe',
                                      '-NoProfile', '-NonInteractive', '-EncodedCommand'])
        query = base64.b64decode(command[4]).decode('utf-16le')
        # These are source-contract checks, not execution of PowerShell/.NET.
        for required in ["$ErrorActionPreference = 'Stop'", "$PSModuleAutoLoadingPreference = 'None'",
                '$path = $env:DG17_FIXTURE_DACL_PATH',
                '[System.Security.AccessControl.DirectorySecurity]::new()',
                '$acl.SetAccessRuleProtection($true, $false)',
                '[System.Security.AccessControl.FileSystemRights]::FullControl',
                '[System.Security.AccessControl.InheritanceFlags]::ContainerInherit',
                '[System.Security.AccessControl.InheritanceFlags]::ObjectInherit',
                '[System.Security.AccessControl.PropagationFlags]::None',
                '[System.Security.AccessControl.AccessControlType]::Allow',
                '[System.Security.Principal.WindowsIdentity]::GetCurrent()',
                "$system = [System.Security.Principal.SecurityIdentifier]::new('S-1-5-18')",
                'foreach ($sid in @($identity.User, $system))',
                '[System.Security.AccessControl.FileSystemAccessRule]::new(',
                '$sid, $rights, $inheritance, $propagation, $allow)',
                '$acl.AddAccessRule($rule)', '[System.IO.Directory]::SetAccessControl($path, $acl)',
                'finally { $identity.Dispose() }']:
            self.assertIn(required, query)
        for forbidden in ['GetAccessControl', 'Get-Acl', 'Set-Acl', 'Import-Module', 'New-Object',
                          'S-1-3-0', 'S-1-5-32-544', 'private_store_directory', str(fixture)]:
            self.assertNotIn(forbidden, query)
        self.assertEqual(kwargs['env'], {'SIMULATED': 'yes', 'DG17_FIXTURE_DACL_PATH': str(fixture)})
        self.assertEqual(kwargs['timeout'], 30)
        self.assertTrue(kwargs['capture_output'])
        self.assertTrue(kwargs['text'])
        self.assertNotIn('shell', kwargs)

    def test_store_fixture_dacl_setup_errors_stop_before_baseline_or_perturbation(self):
        for index, failure in enumerate(['nonzero', 'timeout', 'permission']):
            events = []
            def acl(path, *args):
                events.append(('icacls', args))
            def run(command, **kwargs):
                events.append(('replace-dacl',))
                if failure == 'timeout':
                    raise subprocess.TimeoutExpired(command, 30)
                if failure == 'permission':
                    raise PermissionError('SIMULATED denied fixture DACL write')
                return types.SimpleNamespace(returncode=1, stdout='',
                    stderr='SIMULATED access granted to another principal S-1-5-32-544')
            def check(path):
                events.append(('baseline',))
                return {}
            ns = store_fixture_functions(work=self.directory, icacls=acl, check=check,
                subprocess=types.SimpleNamespace(run=run),
                owner_facts=lambda p: {'owner': 'S-1-5-21-1000', 'user': 'S-1-5-21-1000'})
            with self.subTest(failure=failure):
                ns['case']('setup failure', 'REFUSED',
                    lambda: ns['private'](self.directory / ('setup-failure-' + str(index)),
                                          ['*S-1-5-32-544:(OI)(CI)F']),
                    'access granted to another principal S-1-5-32-544')
                self.assertEqual(ns['rows'][-1]['got'], 'ERROR')
                self.assertFalse(ns['rows'][-1]['ok'])
                self.assertEqual(events, [('icacls', ('/setowner', 'SIMULATED\\User')), ('replace-dacl',)])
                self.assertEqual(len(ns['preconditions']), 1)

    def test_store_fixture_ineffective_dacl_replacement_is_setup_error(self):
        for index, defect in enumerate(['creator-owner-remains', 'foreign-allow', 'deny-entry',
                                       'unprotected', 'null-dacl', 'wrong-owner']):
            perturbations = []
            facts = {'owner': 'S-1-5-21-1000', 'user': 'S-1-5-21-1000'}
            def acl(path, *args):
                if args[0] == '/grant:r': perturbations.append(args)
            def run(command, **kwargs):
                if defect == 'wrong-owner': facts['owner'] = 'S-1-5-32-544'
                return types.SimpleNamespace(returncode=0, stdout='', stderr='')
            def check(path):
                raise RuntimeError({
                    'creator-owner-remains': 'access granted to another principal S-1-3-0',
                    'foreign-allow': 'access granted to another principal S-1-5-32-544',
                    'deny-entry': 'unsupported access entry type 1',
                    'unprotected': 'DACL is not protected: inherited access can apply',
                    'null-dacl': 'no DACL: access is unrestricted',
                    'wrong-owner': 'owner is not the current user'}[defect])
            ns = store_fixture_functions(work=self.directory, icacls=acl, check=check,
                subprocess=types.SimpleNamespace(run=run), owner_facts=lambda p: facts.copy())
            with self.subTest(defect=defect):
                ns['case']('ineffective setup', 'REFUSED',
                    lambda: ns['private'](self.directory / ('ineffective-' + str(index)),
                                          ['*S-1-5-32-544:(OI)(CI)F']),
                    'access granted to another principal S-1-5-32-544')
                row = ns['rows'][-1]
                self.assertEqual(row['got'], 'ERROR')
                self.assertFalse(row['ok'])
                self.assertEqual(perturbations, [])
                self.assertNotIn('private user+SYSTEM baseline', [p['check'] for p in row['preconditions']])

    def test_store_fixture_existing_path_fails_before_owner_or_acl_write(self):
        existing = self.directory / 'existing-fixture'
        existing.mkdir()
        effects = []
        ns = store_fixture_functions(work=self.directory,
            icacls=lambda *a: effects.append('icacls'),
            subprocess=types.SimpleNamespace(run=lambda *a, **kw: effects.append('powershell')))
        ns['case']('existing path setup', 'REFUSED', lambda: ns['private'](existing), 'another principal')
        self.assertEqual(ns['rows'][-1]['got'], 'ERROR')
        self.assertFalse(ns['rows'][-1]['ok'])
        self.assertEqual(effects, [])

    def test_store_fixture_setup_failure_cannot_be_a_negative_pass(self):
        ns = store_fixture_functions(work=self.directory, icacls=lambda *a: None,
            owner_facts=lambda p: {'owner': 'S-1-5-32-544', 'user': 'S-1-5-21-1000'})
        ns['case']('wrong setup owner', 'REFUSED',
                   lambda: ns['private'](self.directory / 'wrong-setup'), 'access granted to another principal')
        self.assertEqual(ns['rows'][-1]['got'], 'ERROR')
        self.assertFalse(ns['rows'][-1]['ok'])
        def refused(*args):
            raise RuntimeError('store custody refused: owner is not the current user')
        ns['case']('wrong refusal reason', 'REFUSED', refused, 'junction, link or other reparse point')
        self.assertEqual(ns['rows'][-1]['got'], 'REFUSED')
        self.assertFalse(ns['rows'][-1]['ok'])
        ns['owner_facts'] = lambda p: {'owner': 'S-1-5-21-1000', 'user': 'S-1-5-21-1000'}
        ns['check'] = refused
        ns['case']('private precondition failure', 'REFUSED',
                   lambda: ns['private_baseline'](self.directory), 'owner is not the current user')
        self.assertEqual(ns['rows'][-1]['got'], 'ERROR')
        self.assertFalse(ns['rows'][-1]['ok'])
        self.assertEqual(ns['bad'], 3)

    def test_store_fixture_child_and_junction_preimages_precede_mutation(self):
        for name in ['inherited', 'inherited_only_users', 'unprotected_inherit_own', 'junction']:
            calls = []
            def private(path, extra=()):
                calls.append(('private', path))
                return path
            def acl(path, *args):
                calls.append(('icacls', path, args))
            def check(path):
                calls.append(('check', path))
                return {}
            def junction(target, link):
                calls.append(('junction', Path(target), Path(link)))
            ns = store_fixture_functions(work=self.directory, private=private, icacls=acl,
                check=check, _winapi=types.SimpleNamespace(CreateJunction=junction),
                os=types.SimpleNamespace(lstat=lambda p: types.SimpleNamespace(st_file_attributes=0x400)))
            with self.subTest(name=name):
                ns[name]()
                self.assertEqual(calls[0][0], 'private')
                self.assertEqual(calls[-1][0], 'check')
                if name == 'junction':
                    self.assertEqual(calls[1][0], 'junction')
                    self.assertEqual(calls[0][1], calls[1][1])
                    self.assertEqual(calls[-1][1], calls[1][2])
                else:
                    child = calls[-1][1]
                    baseline = calls.index(('private', child))
                    mutate = calls.index(('icacls', child, ('/inheritance:e',)))
                    self.assertLess(baseline, mutate)

    def test_store_fixture_owner_read_is_independent_literal_and_bounded(self):
        captured = []
        def run(command, **kwargs):
            captured.append((command, kwargs))
            return types.SimpleNamespace(returncode=0,
                stdout='S-1-5-21-1000\r\nS-1-5-21-1000\r\n', stderr='')
        ns = store_fixture_functions(subprocess=types.SimpleNamespace(run=run),
            os=types.SimpleNamespace(environ={'SIMULATED': 'yes'}))
        fixture = self.directory / "literal-'path; no command"
        self.assertEqual(ns['owner_facts'](fixture)['owner'], 'S-1-5-21-1000')
        command, kwargs = captured[0]
        self.assertEqual(command[1:4], ['-NoProfile', '-NonInteractive', '-EncodedCommand'])
        query = base64.b64decode(command[4]).decode('utf-16le')
        self.assertIn("$PSModuleAutoLoadingPreference = 'None'", query)
        self.assertIn('$path = $env:DG17_FIXTURE_OWNER_PATH', query)
        self.assertIn('[System.IO.File]::GetAttributes($path)', query)
        self.assertIn('[System.IO.FileAttributes]::Directory', query)
        self.assertIn('[System.IO.Directory]::GetAccessControl($path, $sections)', query)
        self.assertIn('[System.IO.File]::GetAccessControl($path, $sections)', query)
        self.assertIn('[System.Security.AccessControl.AccessControlSections]::Owner', query)
        self.assertIn('[System.Security.Principal.WindowsIdentity]::GetCurrent()', query)
        self.assertIn('finally { $identity.Dispose() }', query)
        self.assertEqual(query.count('[Console]::WriteLine('), 2)
        self.assertNotIn('Get-Acl', query)
        self.assertNotIn('ConvertTo-Json', query)
        self.assertNotIn('Import-Module', query)
        self.assertNotIn(str(fixture), query)
        self.assertEqual(kwargs['env']['DG17_FIXTURE_OWNER_PATH'], str(fixture))
        self.assertEqual(kwargs['timeout'], 30)

    def test_store_fixture_owner_query_rejects_error_missing_extra_and_malformed_sid(self):
        positive = 'S-1-5-32-544\r\nS-1-5-21-1000\r\n'
        for stdout, code in [(positive, 1), ('', 0), ('S-1-5-32-544\n', 0),
                (positive + 'unexpected\n', 0), ('not-a-sid\nS-1-5-21-1000\n', 0),
                ('S-1-5-32-544\nS-1-5-２１-1000\n', 0),
                ('S-1-5-32-544\nS-1-5-21-1000\n\n', 0)]:
            def run(command, **kwargs):
                return types.SimpleNamespace(returncode=code, stdout=stdout, stderr='SIMULATED query failure')
            ns = store_fixture_functions(subprocess=types.SimpleNamespace(run=run),
                os=types.SimpleNamespace(environ={'SIMULATED': 'yes'}))
            with self.subTest(stdout=stdout, returncode=code), self.assertRaises(AssertionError):
                ns['owner_facts'](self.directory)
        ns = store_fixture_functions(subprocess=types.SimpleNamespace(run=lambda *a, **kw:
            types.SimpleNamespace(returncode=0, stdout=positive, stderr='')),
            os=types.SimpleNamespace(environ={'SIMULATED': 'yes'}), work=self.directory)
        facts = ns['owner_facts'](self.directory)
        self.assertNotEqual(facts['owner'], facts['user'])
        with self.assertRaises(AssertionError):
            ns['require_owner'](self.directory)
        self.assertEqual(ns['require_owner'](self.directory, 'S-1-5-32-544'), facts)

    def test_store_fixture_all_negative_cases_have_specific_reason(self):
        source = ast.parse((HERE / 'test_store_custody.py').read_text())
        calls = [node.value for node in source.body if isinstance(node, ast.Expr) and
                 isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Name)
                 and node.value.func.id == 'case']
        self.assertEqual(len(calls), 14)
        negatives = [call for call in calls if ast.literal_eval(call.args[1]) == 'REFUSED']
        self.assertEqual(len(negatives), 11)
        for call in negatives:
            self.assertEqual(len(call.args), 4)
            self.assertTrue(ast.literal_eval(call.args[3]))


if __name__ == '__main__':
    unittest.main(verbosity=2)
