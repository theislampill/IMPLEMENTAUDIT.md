"""Exercise the real composer -> approved adapter -> semantic receiver boundary.

All generated records are TEST_ONLY schema fixtures, never issued acts. The
certificate-shaped ASCII is deliberately invalid: no key, recipient, actual
review, adoption, grant, provider artifact or native effect exists in this test.
Fixtures and every subprocess result stay in the declared test resource root.
"""
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import unittest

REPO = Path(__file__).resolve().parents[2]
HANDOFF = REPO / 'handoff/dg16-g221-root-execution-inputs'
TOOLS = HANDOFF / 'tools'
CUSTODY = HANDOFF / 'g220-custody'
SEMANTIC = REPO / 'qualification/dg16-github-evidence/semantic-integration'
RESOURCE = REPO / '.IMPLEMENTAUDIT/g221-binding-tests'
PREFIX = 'qualification/dg16-r5-full-g2/'
ISSUER = 'PRO-EXECUTOR-01'
OLD_ISSUER = '01a1cf82-cdd6-7053-b7b7-32f5c3d93d21'
OLD_HOST = 'pro/dg16-r5-full-g2-direct-host-20-20261114'
HOST = 'pro/dg16-r5-full-g2-direct-host-21-20261115'
REVIEWER = '/root/test_only_binding_schema_fixture'
ORIGINAL_BINDER = CUSTODY / 'author/bind_public_successor.py'
CERT = b'-----BEGIN CERTIFICATE-----\nINVALID-TEST_ONLY-NON_ADMISSIBLE-NOT-A-RECIPIENT\n-----END CERTIFICATE-----\n'
RECEIVER_NAMES = {'public_receiver.py', 'admission_gate.py', 'native_public.py',
    'BINDING.json', 'SUCCESSOR_RUNTIME_BINDING.json', 'FINAL_REVIEW_SELECTION.json',
    'PUBLIC_BINDING_REQUIREMENTS.json'}


def encode(value):
    return (json.dumps(value, sort_keys=True, indent=2) + '\n').encode('ascii')


def desc(raw):
    return dict(bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest())


# The semantic receiver must execute its real read/validation route while every
# process/network/file-write/native-operation entry point remains forbidden.
# Standard-library ctypes import is completed before installing the guard;
# source-native functions are never called and foreign function lookup is denied.
LOAD_RECEIVER = r'''
import ctypes, importlib.util, json, os, sys
from pathlib import Path
semantic_path, selection_path, context_path = map(Path, sys.argv[1:])
selection = json.loads(selection_path.read_bytes())
context = json.loads(context_path.read_bytes())
seen = set()
forbidden = []
def audit(event, args):
    denied = event in ('subprocess.Popen', 'os.system', 'os.fork', 'os.posix_spawn',
        'os.exec', 'os.spawn', 'socket.__new__', 'ctypes.dlopen', 'ctypes.dlsym',
        'ctypes.call_function', 'os.mkdir', 'os.remove', 'os.rename', 'os.chmod')
    if event == 'open':
        denied |= bool(args[2] & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND))
    if denied:
        forbidden.append(event)
        raise AssertionError('TEST_ONLY_EFFECT_FORBIDDEN:' + event)
def trace(frame, event, arg):
    if event != 'call':
        return
    name, function = Path(frame.f_code.co_filename).name, frame.f_code.co_name
    allowed = {'run.py': {'<module>', 'Refusal', 'Deadline', 'load_native', 'need', 'digest'},
        'native_integration.py': {'<module>', 'bindings', 'history'}}
    if name in allowed:
        seen.add(name + ':' + function)
        if function not in allowed[name]:
            forbidden.append(name + ':' + function)
            raise AssertionError('TEST_ONLY_NATIVE_ENTRY_FORBIDDEN:' + name + ':' + function)
sys.addaudithook(audit)
sys.setprofile(trace)
spec = importlib.util.spec_from_file_location('test_only_approved_semantic', semantic_path)
semantic = importlib.util.module_from_spec(spec)
spec.loader.exec_module(semantic)
receiver = semantic.load_receiver(selection, context)
assert receiver.BINDING_SHA == selection['binding_sha256']
assert 'run.py:load_native' in seen
assert 'native_integration.py:bindings' in seen and 'native_integration.py:history' in seen
assert not forbidden
print(json.dumps(dict(TEST_ONLY=True, admissible=False, authority='NONE',
    effect_grant=False, forbidden_effects=forbidden, original_verified_calls=sorted(seen))))
'''


class ApprovedBinding(unittest.TestCase):
    @classmethod
    def command(cls, label, arguments, *, expected=0, code=None):
        ordinal = len(list(cls.logs.glob('*.command.json'))) + 1
        stem = cls.logs / ('%02d-%s' % (ordinal, label))
        cmd = [sys.executable, '-I', '-B']
        cmd += ['-c', code] if code is not None else []
        cmd += [str(value) for value in arguments]
        stem.with_suffix('.command.json').write_bytes(encode(dict(
            TEST_ONLY=True, authority='NONE', argv=cmd)))
        result = subprocess.run(cmd, capture_output=True, timeout=30, cwd=REPO)
        stem.with_suffix('.stdout').write_bytes(result.stdout)
        stem.with_suffix('.stderr').write_bytes(result.stderr)
        stem.with_suffix('.result.json').write_bytes(encode(dict(returncode=result.returncode)))
        if expected is not None and result.returncode != expected:
            raise AssertionError(label + ': ' + result.stderr.decode('utf8', 'replace'))
        return result

    @classmethod
    def records(cls, command, *arguments):
        return cls.command(command, [TOOLS / 'draft_records.py', command, *arguments])

    @classmethod
    def setUpClass(cls):
        RESOURCE.mkdir(parents=True, exist_ok=True)
        (RESOURCE / 'RESOURCE.json').write_bytes(encode(dict(
            owner='g221_binding_engineer', resource=str(RESOURCE),
            scope='TEST_ONLY fixture directories and raw command evidence',
            cleanup='Retained for Root review; no external resources acquired',
            authority='NONE', admissible=False)))
        selected = os.environ.get('G221_BINDING_TEST_ROOT')
        if selected:
            cls.root = Path(selected).resolve()
            if cls.root.parent != RESOURCE:
                raise AssertionError('TEST_FIXTURE_MUST_USE_DECLARED_RESOURCE')
            cls.root.mkdir()
        else:
            cls.root = Path(tempfile.mkdtemp(prefix='TEST_ONLY_', dir=RESOURCE))
        cls.logs = cls.root / 'raw'
        cls.logs.mkdir()
        (cls.root / 'TEST_ONLY.json').write_bytes(encode(dict(TEST_ONLY=True,
            admissible=False, authority='NONE', effect_grant=False,
            warning='All Root/review-shaped bodies here are schema fixtures, not issued acts. '
                    'The certificate is invalid ASCII. No recipient, key, review, adoption, '
                    'grant, artifact receiving, native effect or acceptance is established.')))
        cls.base = cls.root / 'TEST_ONLY_base'
        cls.workspace = cls.root / 'TEST_ONLY_workspace'
        cls.issuer = cls.root / 'TEST_ONLY_issuer'
        cls.candidate = cls.workspace / 'candidate-e76-source-01'
        cls.composition = cls.workspace / 'composition'
        cls.decisions = cls.root / 'TEST_ONLY_decisions'
        cls.runtime_output = cls.workspace / 'TEST_ONLY_public_acquisition'
        cls.cert = cls.root / 'TEST_ONLY_INVALID_CERTIFICATE.pem'
        cls.cert.write_bytes(CERT)
        cls.command('build-current-source', [TOOLS / 'build_universe.py', 'g221',
            '--repo', REPO, '--out', cls.base])
        cls.command('propagate-data', [TOOLS / 'propagate_successor.py', cls.base,
            cls.workspace, cls.root / 'propagation.json', '--old-host-branch', OLD_HOST,
            '--new-host-branch', HOST, '--old-control-branch', OLD_HOST.replace('-host-', '-control-'),
            '--new-control-branch', HOST.replace('-host-', '-control-'), '--recipient-cert', cls.cert,
            '--old-issuer-thread', OLD_ISSUER, '--new-issuer-thread', ISSUER])
        cls.records('runtime', '--universe', cls.workspace, '--actor', '/root',
            '--issuer-thread', ISSUER, '--workspace-root', cls.workspace,
            '--receiver-output-root', cls.runtime_output,
            '--maintained-source-root', cls.root / 'TEST_ONLY_maintained_source',
            '--out', cls.issuer / 'PUBLIC_RUNTIME.json')
        cls.records('candidate-seal', '--candidate', cls.candidate, '--modes-from',
            cls.base / 'candidate-e76-source-01/SEAL.json', '--actor', '/root',
            '--issuer-thread', ISSUER, '--out', cls.issuer / 'CANDIDATE_SEAL.json')
        if (cls.issuer / 'CANDIDATE_SEAL.json').read_bytes() != (cls.candidate / 'SEAL.json').read_bytes():
            raise AssertionError('TEST_CANDIDATE_SEAL_MUST_MATCH_PROPAGATED_BYTES')
        cls.records('reviews', '--previous-universe', CUSTODY, '--universe', cls.workspace,
            '--previous-decisions', CUSTODY / 'root-issuer/decisions', '--candidate-seal',
            cls.issuer / 'CANDIDATE_SEAL.json', '--reviewer', REVIEWER, '--out-dir', cls.decisions)
        report = cls.root / 'TEST_ONLY_NOT_A_REVIEW.md'
        report.write_text('TEST_ONLY schema fixture. Not a review or an issued act.\n')
        cls.records('review-seal', '--reviews', cls.decisions, '--report', report,
            '--candidate-seal', cls.issuer / 'CANDIDATE_SEAL.json', '--reviewer', REVIEWER,
            '--out', cls.issuer / 'REVIEW_SEAL.json')
        cls.records('adoptions', '--previous-universe', CUSTODY, '--universe', cls.workspace,
            '--previous-decisions', CUSTODY / 'root-issuer/decisions', '--reviews', cls.decisions,
            '--review-seal', cls.issuer / 'REVIEW_SEAL.json', '--candidate-seal',
            cls.issuer / 'CANDIDATE_SEAL.json', '--author', '/root', '--out-dir', cls.decisions)
        composer = cls.root / 'TEST_ONLY_compose_final.py'
        cls.command('stage-pure-composer', [TOOLS / 'stage_composer.py', '--in',
            cls.workspace / 'author/compose-candidate-bound.py', '--out', composer,
            '--candidate-seal', cls.issuer / 'CANDIDATE_SEAL.json', '--runtime',
            cls.issuer / 'PUBLIC_RUNTIME.json', '--witness', CUSTODY / 'host-witness/root.json',
            '--review-seal', cls.issuer / 'REVIEW_SEAL.json'])
        cls.command('compose-source-only', [composer, '--candidate', cls.candidate,
            '--issuer', cls.issuer, '--host-witness', CUSTODY / 'host-witness/root.json',
            '--decisions', cls.decisions, '--code-review-seal', cls.issuer / 'REVIEW_SEAL.json',
            '--native-review-seal', cls.issuer / 'REVIEW_SEAL.json', '--output', cls.composition])
        cls.records('composition-seal', '--composition', cls.composition, '--actor', '/root',
            '--issuer-thread', ISSUER, '--out', cls.composition / 'SEAL.json')
        cls.records('selection', '--composition', cls.composition, '--composition-seal',
            cls.composition / 'SEAL.json', '--candidate-seal', cls.issuer / 'CANDIDATE_SEAL.json',
            '--actor', '/root', '--issuer-thread', ISSUER, '--author', '/root', '--reviewer',
            REVIEWER, '--out', cls.issuer / 'FINAL_REVIEW_SELECTION.json')

    def bind(self, label, *, binder=ORIGINAL_BINDER, issuer=None):
        out, report = self.workspace / label, self.root / (label + '.json')
        result = self.command(label, [TOOLS / 'bind_harness.py', 'pro-executor-actual',
            binder, self.candidate, self.composition, issuer or self.issuer, out, report], expected=None)
        return result, out, report

    def test_current_binding_reapplies_exact_original_and_verifies_without_effects(self):
        result, out, report = self.bind('TEST_ONLY_bound_receiver')
        self.assertEqual(result.returncode, 0, result.stderr.decode())
        self.assertEqual(json.loads(report.read_bytes())['bind_public'], 'PASS')
        self.assertEqual({p.name for p in out.iterdir()}, RECEIVER_NAMES)
        self.assertTrue(all(stat.S_IMODE(p.stat().st_mode) == 0o400 for p in out.iterdir()))
        self.assertEqual((out / 'SUCCESSOR_RUNTIME_BINDING.json').read_bytes(),
            (self.issuer / 'PUBLIC_RUNTIME.json').read_bytes())
        self.assertEqual((out / 'FINAL_REVIEW_SELECTION.json').read_bytes(),
            (self.issuer / 'FINAL_REVIEW_SELECTION.json').read_bytes())
        binding = json.loads((out / 'BINDING.json').read_bytes())
        composition = json.loads((self.composition / 'COMPOSITION.json').read_bytes())
        self.assertEqual(binding['branch'], HOST)
        self.assertEqual(binding['control_branch'], HOST.replace('-host-', '-control-'))
        self.assertEqual(binding['session'], ISSUER)
        self.assertEqual(binding['final_tree'], composition['final_tree'])
        self.assertEqual((out / 'native_public.py').read_bytes(),
            (CUSTODY / 'candidate-e76-source-01/receiver/native_public.py').read_bytes())
        self.records('receiver-seal', '--receiver', out, '--composition', self.composition,
            '--actor', '/root', '--issuer-thread', ISSUER, '--out', out / 'SEAL.json')
        (out / 'SEAL.json').chmod(0o400)
        selection = dict(directory=str(out))
        for name, field in [('public_receiver.py', 'receiver_sha256'), ('SEAL.json', 'seal_sha256'),
                ('BINDING.json', 'binding_sha256'), ('SUCCESSOR_RUNTIME_BINDING.json', 'runtime_sha256')]:
            selection[field] = desc((out / name).read_bytes())['sha256']
        selected_path, context_path = self.root / 'TEST_ONLY_selected.json', self.root / 'TEST_ONLY_context.json'
        selected_path.write_bytes(encode(selection))
        context = {key: binding[key] for key in ('repository', 'branch', 'source_commit', 'source_tree')}
        context['workflow_tree'] = composition['final_tree']
        context_path.write_bytes(encode(context))
        checked = self.command('unchanged-semantic-load', [SEMANTIC / 'semantic_receiver.py',
            selected_path, context_path], code=LOAD_RECEIVER)
        self.assertEqual(json.loads(checked.stdout)['forbidden_effects'], [])
        self.assertFalse(self.runtime_output.exists())

    def test_regenerated_binder_cannot_replace_approved_original(self):
        result, out, _ = self.bind('TEST_ONLY_reject_regenerated',
            binder=self.workspace / 'author/bind_public_successor.py')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('ORIGINAL_BINDER_PIN', result.stderr.decode())
        self.assertFalse(out.exists())

    def test_changed_semantic_source_is_refused_before_execution(self):
        clone = self.root / 'TEST_ONLY_corrupt_semantic_source'
        harness = clone / 'handoff/dg16-g221-root-execution-inputs/tools/bind_harness.py'
        semantic = clone / 'qualification/dg16-github-evidence/semantic-integration/semantic_receiver.py'
        harness.parent.mkdir(parents=True)
        semantic.parent.mkdir(parents=True)
        harness.write_bytes((TOOLS / 'bind_harness.py').read_bytes())
        marker = clone / 'TEST_ONLY_FORBIDDEN_EXECUTION'
        semantic.write_bytes(('from pathlib import Path\nPath(%r).write_text("TEST_ONLY executed\\n")\n'
            'raise RuntimeError("TEST_ONLY_ALTERED_SEMANTIC_EXECUTED")\n' % str(marker)).encode()
            + (SEMANTIC / 'semantic_receiver.py').read_bytes())
        out, report = self.workspace / 'TEST_ONLY_reject_semantic', self.root / 'TEST_ONLY_reject_semantic.json'
        result = self.command('reject-changed-semantic', [harness, 'pro-executor-actual',
            ORIGINAL_BINDER, self.candidate, self.composition, self.issuer, out, report], expected=None)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('APPROVED_SEMANTIC_PIN', result.stderr.decode())
        self.assertFalse(marker.exists(), 'Changed semantic bytes must never execute')
        self.assertFalse(out.exists())

    def test_optimized_pro_mode_refuses_before_binding(self):
        out, report = self.workspace / 'TEST_ONLY_reject_optimized', self.root / 'TEST_ONLY_reject_optimized.json'
        result = self.command('reject-optimized-pro-mode', ['-O', TOOLS / 'bind_harness.py',
            'pro-executor-actual', ORIGINAL_BINDER, self.candidate, self.composition,
            self.issuer, out, report], expected=None)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('PRO_EXECUTOR_REQUIRES_ASSERTIONS', result.stderr.decode())
        self.assertFalse(out.exists())

    def test_changed_external_selection_refuses_before_receiver_output(self):
        issuer = self.root / 'TEST_ONLY_wrong_selection'
        issuer.mkdir()
        (issuer / 'PUBLIC_RUNTIME.json').write_bytes((self.issuer / 'PUBLIC_RUNTIME.json').read_bytes())
        selection = json.loads((self.issuer / 'FINAL_REVIEW_SELECTION.json').read_bytes())
        selection['branch'] = OLD_HOST
        (issuer / 'FINAL_REVIEW_SELECTION.json').write_bytes(encode(selection))
        result, out, report = self.bind('TEST_ONLY_reject_selection', issuer=issuer)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(json.loads(report.read_bytes())['bind_public'],
            'REFUSED:ACTUAL_ROOT_DISTINCT_REVIEW_SELECTION_JOIN')
        self.assertFalse(out.exists())


if __name__ == '__main__':
    unittest.main(verbosity=2)
