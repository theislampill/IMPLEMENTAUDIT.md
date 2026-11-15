"""Independent controls for only the six-file DG17 CI followup."""
import ast
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import types
import unittest
from unittest.mock import patch

ROOT = Path('/workspace/scratch/0269e6626329/dg17')
WORK = ROOT.parent / 'dg17-review/followup-bd58fc60'
TOOLS = ROOT / 'handoff/dg16-dg18-findings-20261115/dg17-release-with-store-check/tools'
BASE = '5a6825c73de82d7ba45d584527da882310f20a62'
HEAD = 'bd58fc6087f6bf35c244f2661c71d28467296204'


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


builder = load(TOOLS / 'build_release_acl.py', 'followup_builder')
rehearsal = load(TOOLS / 'rehearse_lifecycle.py', 'followup_rehearsal')


class Followup(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = WORK / 'fixtures'
        cls.temp.mkdir(exist_ok=False)
        cls.allowed = {name: str(Path(path).resolve()) for name, path in {
            'python': sys.executable, 'bash': shutil.which('bash'), 'git': shutil.which('git')}.items()}
        cls.owners = {str((cls.temp / 'source/skills/implementaudit/scripts' / name).resolve())
                      for name in ['claim-run.sh', 'validate-run-root.sh']}

    def test_exact_parent_guard_false_positive_and_successor_binding_data(self):
        relative = (TOOLS / 'rehearse_lifecycle.py').relative_to(ROOT).as_posix()
        old = ast.parse(subprocess.check_output(['git', '-C', str(ROOT), 'show', BASE + ':' + relative]))
        main = next(n for n in old.body if isinstance(n, ast.FunctionDef) and n.name == 'main')
        guard = next(n for n in main.body if isinstance(n, ast.FunctionDef) and n.name == 'deterministic_process')
        namespace = {'Path': Path, 'shutil': shutil, 'allowed': set(self.allowed.values()),
                     'original_popen': lambda *a, **kw: self.fail('No actual spawn belongs in the comparison')}
        exec(compile(ast.Module(body=[guard], type_ignores=[]), 'frozen-parent-guard', 'exec'), namespace)
        command = [self.allowed['python'], '-I', '-S', '-B', '/SIMULATED/host-session-binding.py',
                   '--store', '/SIMULATED/store', 'bind', '--host-id', 'codex']
        with self.assertRaisesRegex(AssertionError, 'No Codex or appserver'):
            namespace['deterministic_process'](command)
        rehearsal.admit_deterministic_process(command, self.allowed, self.owners)

    def test_exact_executables_and_only_two_bash_owners(self):
        for owner in self.owners:
            rehearsal.admit_deterministic_process([self.allowed['bash'], owner, '--host-id', 'codex'],
                                                  self.allowed, self.owners)
        rehearsal.admit_deterministic_process([self.allowed['git'], 'rev-parse', 'HEAD'], self.allowed, self.owners)
        foreign = self.temp / 'python'
        foreign.write_bytes(b'SIMULATED never executable')
        foreign.chmod(0o755)
        commands = [
            [str(foreign), '--host-id', 'codex'], ['/SIMULATED/codex', 'exec'],
            ['/SIMULATED/codex.exe', 'app-server'],
            [self.allowed['python'], '/SIMULATED/owner.py', 'app-server'],
            [self.allowed['git'], 'app-server'], [self.allowed['bash']],
            [self.allowed['bash'], '-c', 'true'], [self.allowed['bash'], '-lc', 'true'],
            [self.allowed['bash'], str(self.temp / 'foreign.sh')],
            [self.allowed['bash'], 'claim-run.sh'], [], 'codex exec']
        for command in commands:
            with self.subTest(command=command), self.assertRaises(AssertionError):
                rehearsal.admit_deterministic_process(command, self.allowed, self.owners)
        with patch.object(shutil, 'which', return_value=str(foreign)), self.assertRaises(AssertionError):
            rehearsal.admit_deterministic_process(['python', '--host-id', 'codex'], self.allowed, self.owners)
        with self.assertRaises(AssertionError):
            rehearsal.admit_deterministic_process([self.allowed['git'], 'status'], self.allowed, self.owners, shell=True)

    def test_identity_diagnostic_refuses_before_any_payload_read(self):
        path = self.temp / 'private-diagnostic-path'
        path.write_bytes(b'SIMULATED content sentinel')
        original_fstat = os.fstat
        original_open = Path.open
        fields = ('st_dev', 'st_ino', 'st_mode', 'st_nlink', 'st_size', 'st_mtime_ns', 'st_ctime_ns')
        class NoRead:
            def __init__(self, stream): self.stream = stream
            def __enter__(self): return self
            def __exit__(self, *args): self.stream.close()
            def fileno(self): return self.stream.fileno()
            def read(self, *args): raise AssertionError('Payload must not be read after identity drift')
        def checked_open(p, *args, **kwargs):
            return NoRead(original_open(p, *args, **kwargs))
        def mismatch(fd):
            values = {field: getattr(original_fstat(fd), field) for field in fields}
            values['st_ino'] += 1
            values['st_ctime_ns'] += 1
            return types.SimpleNamespace(**values)
        with patch.object(Path, 'open', checked_open), patch.object(os, 'fstat', mismatch):
            with self.assertRaisesRegex(ValueError, 'Input identity changed before read: ') as caught:
                builder.pin(path)
        text = str(caught.exception)
        value = json.loads(text.split(': ', 1)[1])
        self.assertEqual(value['mismatch_fields'], ['st_ino', 'st_ctime_ns'])
        self.assertEqual(set(value), {'python_version', 'mismatch_fields', 'before', 'opened'})
        self.assertEqual(set(value['before']), set(fields))
        self.assertNotIn(str(path), text)
        self.assertNotIn('content sentinel', text)
        self.assertLess(len(text), 2048)

    def test_original_after_read_identity_refusal_remains(self):
        path = self.temp / 'after-read'
        path.write_bytes(b'SIMULATED stable bytes')
        original = os.fstat
        fields = ('st_dev', 'st_ino', 'st_mode', 'st_nlink', 'st_size', 'st_mtime_ns', 'st_ctime_ns')
        for field in fields:
            calls = 0
            def drift(fd):
                nonlocal calls
                calls += 1
                observed = original(fd)
                values = {key: getattr(observed, key) for key in fields}
                if calls == 2: values[field] += 1
                return types.SimpleNamespace(**values)
            with self.subTest(field=field), patch.object(os, 'fstat', drift):
                with self.assertRaisesRegex(ValueError, '^Input identity changed during read$'):
                    builder.pin(path)

    def test_first_failure_and_cleanup_failure_both_retained_with_bounds(self):
        fixture = rehearsal.Fixture.__new__(rehearsal.Fixture)
        fixture.work = self.temp / 'failure-summary'
        fixture.case = fixture.work / 'SIMULATED-case'
        fixture.mode = 'full'
        evidence = fixture.case / 'evidence'
        stage_b = evidence / 'stage-B01'
        stage_b.mkdir(parents=True)
        rehearsal.save(evidence / 'POST_A.json', {'status':'A_SIMULATED', 'error':None})
        rehearsal.save(stage_b / 'POST_B.json', {'status':'STOPPED_TEARDOWN_UNKNOWN_NO_RETRY',
                       'error':'SIMULATED original guard refusal', 'cleanup':{'known':False}})
        rehearsal.save(stage_b / '03-owned-bind.json', {'exit':2, 'stderr':'x' * 6000 + 'FIRST'})
        rehearsal.save(stage_b / '09-cleanup.json', {'exit':3, 'stderr':'SIMULATED cleanup refusal'})
        rehearsal.save(stage_b / 'boolean.json', {'exit':True, 'stderr':'not a numeric command exit'})
        (stage_b / 'linked.json').symlink_to(stage_b / '03-owned-bind.json')
        (stage_b / 'oversized.json').write_bytes(b'x' * 262145)
        fixture.preserve_failure(RuntimeError('SIMULATED final cleanup exception'))
        value = json.loads((fixture.work / 'REHEARSAL_RESULT.json').read_bytes())
        self.assertEqual(value['stages']['B']['error'], 'SIMULATED original guard refusal')
        self.assertFalse(value['stages']['B']['cleanup_known'])
        self.assertEqual([x['exit'] for x in value['failed_source_commands']], [2,3])
        self.assertEqual(len(value['failed_source_commands'][0]['stderr']), 4096)
        self.assertTrue(value['failed_source_commands'][0]['stderr'].endswith('FIRST'))
        self.assertEqual(value['authority'], 'NONE')
        self.assertFalse(value['native_acceptance'])
        self.assertEqual(value['original14_unknown_differences'], 14)

    def test_diagnostic_failure_does_not_replace_original_exception(self):
        first = RuntimeError('SIMULATED original exception object')
        def run(): raise first
        def diagnostic(error):
            self.assertIs(error, first)
            raise ValueError('SIMULATED diagnostic unavailable')
        fixture = types.SimpleNamespace(python=self.allowed['python'], bash=self.allowed['bash'],
                  op={'git':self.allowed['git']}, case=self.temp, run=run, preserve_failure=diagnostic)
        output = io.StringIO()
        with patch.object(rehearsal, 'Fixture', return_value=fixture), patch.object(sys, 'argv',
             ['review', '--author', str(self.temp), '--work', str(self.temp)]), patch.object(sys, 'stderr', output):
            with self.assertRaises(RuntimeError) as caught: rehearsal.main()
        self.assertIs(caught.exception, first)
        observed = json.loads(output.getvalue())
        self.assertEqual(observed, {'result':'FAILURE_DIAGNOSTIC_UNAVAILABLE','authority':'NONE','error_type':'ValueError'})

    def test_exact_six_file_manifest_and_received_hosted_member_hashes(self):
        manifest_path = TOOLS.parent / 'SOURCE_QUALIFICATION_MANIFEST.json'
        manifest = json.loads(manifest_path.read_bytes())
        followup = manifest['source_ci_followup']
        changed = set(subprocess.check_output(['git', '-C', str(ROOT), 'diff', '--name-only', BASE, HEAD], text=True).splitlines())
        records = followup['changed_file_population_excludes_this_manifest']
        self.assertEqual(changed, {x['path'] for x in records} | {manifest_path.relative_to(ROOT).as_posix()})
        self.assertEqual(len(changed), 6)
        for record in records:
            raw = (ROOT / record['path']).read_bytes()
            self.assertEqual((len(raw), sha(raw)), (record['bytes'], record['sha256']))
        received = ROOT / '.IMPLEMENTAUDIT/dg17-ci-43675846002'
        for artifact in followup['artifacts']:
            directory = received / artifact['metadata']['name']
            self.assertEqual(json.loads((directory/'METADATA.json').read_bytes()), artifact['metadata'])
            self.assertEqual(json.loads((directory/'RECEIPT.json').read_bytes()), artifact['receipt'])
            for member, record in artifact['receipt']['members'].items():
                raw = (directory / member).read_bytes()
                self.assertEqual((len(raw), sha(raw)), (record['bytes'], record['sha256']))
        self.assertEqual(followup['received_pins']['source_head'], '52065bcee405715a2fc31d78b3aefd2958ba96a0')
        self.assertEqual(followup['received_pins']['source_tree'], '7da9f4e0d40e8dfb32d5dcf78df46b4e70c31f14')
        self.assertFalse(followup['native_admission'])
        self.assertEqual(followup['original14_custody_unknown_differences'], 14)


if __name__ == '__main__':
    with (WORK / 'independent-7-controls.log').open('w') as stream:
        result = unittest.TextTestRunner(stream=stream, verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Followup))
    print((WORK / 'independent-7-controls.log').read_text())
    raise SystemExit(not result.wasSuccessful())
