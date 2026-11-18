"""Non-acceptance transport regressions using the real production capture env.

No verifier pair, review, Root decision, or consumption reservation is created.
Loopback endpoints are deliberately not listening; reaching a connection refusal
proves Git passed its protocol gate without requiring external DNS or credentials.
"""
import importlib.util
import json
from pathlib import Path
import socket
import tempfile
import time
import unittest
from unittest import mock


HERE = Path(__file__).resolve().parent


def load(name):
    spec = importlib.util.spec_from_file_location(name, HERE / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ObservedTransport(Exception):
    def __init__(self, result):
        self.result = result


class MissingRefPoll(Exception):
    pass


class TransportTests(unittest.TestCase):
    def setUp(self):
        self.control = load('live_control')
        self.utility = load('host_utility')
        self.temp = tempfile.TemporaryDirectory(prefix='g2-transport-nonacceptance-')
        self.addCleanup(self.temp.cleanup)
        self.work = Path(self.temp.name)
        self.request = (json.dumps({
            'repository': 'theislampill/IMPLEMENTAUDIT.md',
            'control_branch': self.control.CONTROL_BRANCH,
            'control_path': 'qualification/dg16-full-g2-control/TRANSPORT_TEST-1',
            'run_id': 'TRANSPORT_TEST',
        }, sort_keys=True) + '\n').encode()

    def observe_remote(self, operation, remote):
        control, utility = self.control, self.utility
        control.REMOTE = remote

        class CaptureUntilRemote:
            def capture(inner, label, argv, records, deadline, seconds):
                if operation == 'fetch' and 'ls-remote' in argv:
                    # Controlled remote discovery only, to reach the real fetch.
                    return 0, (('1' * 40) + '\trefs/heads/' +
                               control.CONTROL_BRANCH + '\n').encode(), b''
                result = utility.capture(label, argv, records, deadline,
                                         seconds=seconds)
                if operation in argv:
                    raise ObservedTransport(result)
                return result

        with self.assertRaises(ObservedTransport) as caught:
            control.hold(self.work, self.request, time.monotonic() + 10,
                         CaptureUntilRemote(), '/usr/bin/git')
        self.assertFalse((self.work / 'CONSUMPTION_RESERVED.json').exists())
        return caught.exception.result

    def assert_https_reaches_connection(self, operation):
        with socket.socket() as endpoint:
            endpoint.bind(('127.0.0.1', 0))
            remote = 'https://127.0.0.1:%d/fixture.git' % endpoint.getsockname()[1]
            code, out, err = self.observe_remote(operation, remote)
        self.assertEqual(code, 128)
        self.assertEqual(out, b'')
        self.assertNotIn(b"transport 'https' not allowed", err)
        self.assertIn(b'127.0.0.1', err)

    def test_discovery_https_survives_real_closed_capture_environment(self):
        self.assert_https_reaches_connection('ls-remote')

    def test_fetch_https_survives_real_closed_capture_environment(self):
        self.assert_https_reaches_connection('fetch')

    def test_other_protocols_still_denied(self):
        for protocol, remote in [('file', 'file:///NON_ACCEPTANCE_FIXTURE'),
                                 ('ext', 'ext::echo NON_ACCEPTANCE_FIXTURE')]:
            with self.subTest(protocol=protocol):
                code, out, err = self.observe_remote('ls-remote', remote)
                self.assertEqual(code, 128)
                self.assertEqual(out, b'')
                self.assertIn(("transport '%s' not allowed" % protocol).encode(), err)
                (self.work / 'CONTROL_READS.json').unlink()

    def classify_discovery(self, returncode):
        class DiscoveryOutcome:
            def capture(inner, label, argv, records, deadline, seconds):
                if 'ls-remote' in argv:
                    return returncode, b'', b'' if returncode == 2 else b'fatal: fixture transport refusal\n'
                if 'init' in argv:
                    return 0, b'', b''
                raise AssertionError('Unexpected operation beyond discovery')

        with mock.patch.object(self.control.time, 'sleep', side_effect=MissingRefPoll):
            self.control.hold(self.work, self.request, time.monotonic() + 10,
                              DiscoveryOutcome(), '/usr/bin/git')

    def test_fatal_discovery_error_is_not_polled_as_absent(self):
        with self.assertRaisesRegex(self.control.Refusal, '^LIVE_CONTROL_GIT_REFUSED$'):
            try:
                self.classify_discovery(128)
            except MissingRefPoll:
                self.fail('Fatal discovery error was retried as a missing ref')
        self.assertFalse((self.work / 'CONSUMPTION_RESERVED.json').exists())

    def test_documented_missing_ref_still_polls(self):
        with self.assertRaises(MissingRefPoll):
            self.classify_discovery(2)
        self.assertFalse((self.work / 'CONSUMPTION_RESERVED.json').exists())


if __name__ == '__main__':
    unittest.main(verbosity=2)
