"""The issuer guard must allow the owner-designated identity without opening it.

These five-member data fixtures are intentionally not candidate universes: the
certificate text is invalid, the adoption has a TEST schema, and there are no
keys, real reviews, grants, producer effects or accepting claims. The real CLI
must propagate the authorized label and still reject unapproved label forms.
"""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

REPO = Path(__file__).resolve().parents[2]
TOOL = REPO / 'handoff/dg16-g221-root-execution-inputs/tools/propagate_successor.py'
OLD_ISSUER = '01a1cf82-cdd6-7053-b7b7-32f5c3d93d21'
OLD_HOST = 'pro/dg16-r5-full-g2-direct-host-20-20261114'
NEW_HOST = 'pro/dg16-r5-full-g2-direct-host-21-20261115'
Q = 'candidate-e76-source-01/candidate/public/qualification/dg16-r5-full-g2/'
CERT = b'-----BEGIN CERTIFICATE-----\nINVALID-SOURCE-TEST-NOT-A-RECIPIENT\n-----END CERTIFICATE-----\n'


def encode(value):
    return (json.dumps(value, sort_keys=True, indent=2) + '\n').encode()


class SuccessorIssuer(unittest.TestCase):
    def trial(self, identity, *, old=OLD_ISSUER):
        with tempfile.TemporaryDirectory(prefix='g221-issuer-test-') as root:
            root = Path(root)
            src, dst, report = root/'src', root/'dst', root/'report.json'
            public = src / Q
            public.mkdir(parents=True)
            previous_cert = b'NOT-A-RECIPIENT-OR-CERTIFICATE\n'
            adoption = dict(schema='SOURCE_TEST_ONLY_NOT_AN_ADOPTION',
                recipient=dict(bytes=len(previous_cert), sha256=hashlib.sha256(previous_cert).hexdigest()),
                branch=OLD_HOST, control_branch=OLD_HOST.replace('-host-', '-control-'),
                issuer_thread=OLD_ISSUER, authority='NONE', effect_grant=False)
            adoption_raw = encode(adoption)
            (public/'PROTECTED_RECIPIENT.pem').write_bytes(previous_cert)
            (public/'PROTECTED_RECIPIENT.json').write_bytes(adoption_raw)
            (public/'protected_bridge.py').write_text(
                'HOST_SELECTION_EXPECTED = '+repr(adoption)+'\n'+
                'SELECTION_SHA = '+repr(hashlib.sha256(adoption_raw).hexdigest())+'\n'+
                'BRANCH = '+repr(OLD_HOST)+'\n'+
                'CONTROL_BRANCH = '+repr(OLD_HOST.replace('-host-', '-control-'))+'\n')
            workflow = src/'candidate-e76-source-01/candidate/public/.github/workflows/dg16-r5-full-g2.yml'
            workflow.parent.mkdir(parents=True)
            workflow.write_text('SOURCE_TEST_ONLY_BRANCH: '+OLD_HOST+'\n')
            cert = root/'invalid-test-certificate.pem'
            cert.write_bytes(CERT)
            cmd = [sys.executable, '-I', '-B', str(TOOL), str(src), str(dst), str(report),
                '--old-host-branch', OLD_HOST, '--new-host-branch', NEW_HOST,
                '--old-control-branch', OLD_HOST.replace('-host-', '-control-'),
                '--new-control-branch', NEW_HOST.replace('-host-', '-control-'),
                '--recipient-cert', str(cert), '--old-issuer-thread', old,
                '--new-issuer-thread', identity]
            result = subprocess.run(cmd, text=True, capture_output=True, timeout=10)
            if result.returncode:
                self.assertFalse(dst.exists(), 'Refusal must precede creation of proposed outputs')
                self.assertFalse(report.exists())
                return result, None, None
            return result, json.loads(report.read_bytes()), json.loads((dst/Q/'PROTECTED_RECIPIENT.json').read_bytes())

    def test_designated_successor_reaches_real_propagation(self):
        result, report, adoption = self.trial('PRO-EXECUTOR-01')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(adoption['issuer_thread'], 'PRO-EXECUTOR-01')
        self.assertEqual(adoption['branch'], NEW_HOST)
        self.assertEqual(adoption['schema'], 'SOURCE_TEST_ONLY_NOT_AN_ADOPTION')
        self.assertEqual(len(report['joins']), 6)
        self.assertTrue(all(report['joins'].values()))
        self.assertEqual(report['authority'], 'NONE')

    def test_existing_uuid_shape_remains_supported_as_data_only(self):
        result, _, adoption = self.trial('11111111-2222-3333-4444-555555555555')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(adoption['issuer_thread'], '11111111-2222-3333-4444-555555555555')

    def test_similar_or_unfilled_successors_cannot_enter_propagation(self):
        for identity in ('PRO-EXECUTOR-02', 'pro-executor-01', 'PRO-EXECUTOR-01 ',
                         'PRO-EXECUTOR-01\n', '/root', '<SUCCESSOR>', 'Astra'):
            with self.subTest(identity=repr(identity)):
                result, _, _ = self.trial(identity)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn('ISSUER_THREAD_SHAPE', result.stderr)


if __name__ == '__main__':
    unittest.main(verbosity=2)
