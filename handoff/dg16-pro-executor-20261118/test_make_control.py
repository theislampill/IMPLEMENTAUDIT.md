"""Non-acceptance controls for the operator formatter against the actual validator.

Every PASS below is a synthetic test vector, never an independent G2 verdict.
The external validator, not a duplicate of its logic, decides conformance.
"""
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import types
import unittest


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
WORKFLOW = 'd2f04874c549816141de002f9baec73dbc9d06fd'
VALIDATOR_SHA = '444b8d66f6c554fe1df3490b9db944a8bc5f8371b565f9377a07d168adc5e517'
ROOT_DECISION = 'CONSUME_AT_DECLARED_SCOPE_SUBJECT_TO_CLOSING_READBACK'
SUCCESSOR = 'PRO-EXECUTOR-01, designated by owner'


def encoded(value):
    return (json.dumps(value, sort_keys=True, indent=2) + '\n').encode()


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


class FormatterTests(unittest.TestCase):
    def setUp(self):
        subject = HERE / 'make_control.py'
        self.assertTrue(subject.is_file(), 'The operator formatter is not implemented')
        spec = importlib.util.spec_from_file_location('make_control', subject)
        self.subject = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.subject)
        raw = subprocess.check_output([
            'git', 'show', WORKFLOW + ':qualification/dg16-r5-full-g2/live_control.py'
        ], cwd=REPO)
        self.assertEqual(digest(raw), VALIDATOR_SHA)
        self.validator_raw = raw
        self.validator = types.ModuleType('original_live_control')
        exec(compile(raw, '<exact-original-live-control>', 'exec'), self.validator.__dict__)
        self.proof = encoded({'scope': 'SYNTHETIC_NON_ACCEPTANCE_FORMATTER_TEST',
                              'original_acceptance': False})
        request = {
            'schema': 'dg16.full-correspondence-live-review-request.v1',
            'run_id': 'NON_ACCEPTANCE_UNIT_TEST', 'run_attempt': 1,
            'repository': 'theislampill/IMPLEMENTAUDIT.md',
            'control_branch': 'pro/dg16-g2-accepting-control-20261117',
            'control_path': 'qualification/dg16-full-g2-control/NON_ACCEPTANCE_UNIT_TEST-1',
            'workflow_commit': WORKFLOW, 'source_commit': 'a' * 40,
            'source_tree': 'b' * 40, 'policy_sha256': 'c' * 64,
            'policy_adoption_sha256': 'd' * 64,
            'proof': {'bytes': len(self.proof), 'sha256': digest(self.proof)},
            'private_observations': {'bytes': 1, 'sha256': 'e' * 64},
            'created_utc_epoch': 1000, 'expires_utc_epoch': 4600,
            'hold_seconds': 3600,
            'rehearsal_only': True, 'original_acceptance': False,
        }
        self.request = encoded(request)
        common = {key: request[key] for key in
                  ('source_commit', 'source_tree', 'policy_sha256', 'policy_adoption_sha256')}
        review = {
            'schema': 'dg16.full-correspondence-independent-live-review.v1',
            'authority': 'NONE', 'decision': 'PASS', 'blocking_findings': [],
            'scope': 'ACTUAL_FULL_CORRESPONDENCE_PROOF_WHILE_PRIVATE_INPUTS_REMAIN_LIVE',
            'reviewer': '/root/synthetic_protocol_fixture_reviewer',
            'request_sha256': digest(self.request), 'proof_sha256': digest(self.proof),
            'private_observations_sha256': 'e' * 64, **common,
        }
        # Deliberately non-canonical whitespace: the author's bytes must survive.
        self.review = json.dumps(review, indent=1).encode() + b'\n\n'

    def build(self, **changes):
        args = dict(validator=self.validator, root_decision=ROOT_DECISION,
                    successor=SUCCESSOR, now=1001)
        args.update(changes)
        return self.subject.build_payload(self.request, self.proof, self.review, **args)

    def test_external_review_bytes_survive_and_actual_validator_consumes(self):
        # Catches silently rewriting the independent assessment or wrong descriptors.
        payload = self.build()
        self.assertEqual(payload['INDEPENDENT_REVIEW.json'], self.review)
        result = self.validator.validate(payload, self.request, now=1001)
        self.assertEqual(result['decision'], 'CONSUME')
        root = json.loads(payload['ROOT_CONSUMPTION.json'])
        self.assertEqual(root['review_sha256'], digest(self.review))
        self.assertIs(root['automatic_full_G2_award'], False)

    def test_cannot_create_pass_from_absent_or_rejected_review(self):
        # Catches a formatter that synthesizes PASS or erases reviewer findings.
        for raw in (b'', encoded({'decision': 'BLOCKED'})):
            with self.subTest(raw=raw), self.assertRaises((ValueError, KeyError)):
                self.subject.build_payload(self.request, self.proof, raw,
                    validator=self.validator, root_decision=ROOT_DECISION,
                    successor=SUCCESSOR, now=1001)

    def test_expired_window_and_implicit_root_decision_refuse(self):
        # Catches retroactive review serialization or a default Root authorization.
        with self.assertRaises(ValueError):
            self.build(now=4600)
        with self.assertRaises(ValueError):
            self.build(root_decision=None)

    def test_proof_substitution_refuses(self):
        # Catches controls bound to a proof the operator did not actually receive.
        with self.assertRaises(ValueError):
            self.subject.build_payload(self.request, self.proof + b' ', self.review,
                validator=self.validator, root_decision=ROOT_DECISION,
                successor=SUCCESSOR, now=1001)

    def test_wrong_validator_identity_refuses_before_loading(self):
        # Catches accidentally selecting the 300-second results-branch validator.
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'validator.py'
            path.write_bytes(self.validator_raw)
            with self.assertRaises(ValueError):
                self.subject.load_validator(path, '0' * 64)
            validator = self.subject.load_validator(path, VALIDATOR_SHA)
            self.assertEqual(validator.validate(self.build(), self.request, now=1001)['decision'], 'CONSUME')

    def test_bundle_creation_is_exclusive_and_exact(self):
        # Catches overwriting a prior control bundle or changing the review on disk.
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / 'control'
            payload = self.build()
            self.subject.write_bundle(out, payload)
            self.assertEqual({p.name for p in out.iterdir()}, set(self.validator.NAMES))
            self.assertEqual((out / 'INDEPENDENT_REVIEW.json').read_bytes(), self.review)
            with self.assertRaises(FileExistsError):
                self.subject.write_bundle(out, payload)


if __name__ == '__main__':
    unittest.main(verbosity=2)
