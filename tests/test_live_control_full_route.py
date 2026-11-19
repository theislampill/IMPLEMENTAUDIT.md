"""Bounded NON_ACCEPTANCE integration of the real G2 control consumer.

This is an explicitly synthetic fixture, never a reviewer judgment or Root
decision for an original run. It uses real Git smart HTTPS, the unchanged
production capture/environment, and the unmodified consumer guards. Only the
remote endpoint and TLS trust source are fixture bindings. The Git wrapper adds
http.sslCAInfo only; it cannot authorize a protocol or fabricate Git output.
All files, fixture refs, and child activity remain inside the assigned directory.
"""
import ctypes
import hashlib
import http.server
import importlib.util
import json
import os
from pathlib import Path
import socket
import ssl
import subprocess
import sys
import threading
import time
import unittest
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
SOURCE = Path(os.environ.get('G2_SOURCE_DIR', str(ROOT / 'source-original/qualification/dg16-r5-full-g2')))
EVIDENCE = Path(os.environ.get('G2_ROUTE_EVIDENCE', str(ROOT / 'route-evidence')))
GIT = '/usr/bin/git'
NAMES = ('CONTROL.json', 'INDEPENDENT_REVIEW.json', 'ROOT_CONSUMPTION.json')


def canonical(value):
    return (json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + '\n').encode()


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def descriptor(raw):
    return {'bytes': len(raw), 'sha256': sha(raw)}


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def git(repo, *args, data=None):
    env = {'PATH': '/usr/bin:/bin', 'LC_ALL': 'C',
           'GIT_CONFIG_GLOBAL': '/dev/null', 'GIT_CONFIG_SYSTEM': '/dev/null',
           'GIT_CONFIG_NOSYSTEM': '1', 'GIT_TERMINAL_PROMPT': '0',
           'GIT_AUTHOR_NAME': 'NON_ACCEPTANCE_FIXTURE',
           'GIT_AUTHOR_EMAIL': 'fixture@invalid',
           'GIT_COMMITTER_NAME': 'NON_ACCEPTANCE_FIXTURE',
           'GIT_COMMITTER_EMAIL': 'fixture@invalid'}
    cmd = [GIT, '--git-dir', str(repo), *args]
    p = subprocess.run(cmd, input=data, stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE, env=env, timeout=10)
    if p.returncode:
        raise RuntimeError('Fixture Git failed: ' + str(args[:2]) + ': ' + p.stderr.decode())
    return p.stdout


def tree(repo, files):
    nested = {}
    for name, raw in files.items():
        parts = name.split('/')
        node = nested
        for component in parts[:-1]:
            node = node.setdefault(component, {})
        node[parts[-1]] = raw

    def make(node):
        rows = []
        for name, value in sorted(node.items()):
            if isinstance(value, dict):
                oid = make(value)
                rows.append('040000 tree ' + oid + '\t' + name + '\n')
            else:
                oid = git(repo, 'hash-object', '-w', '--stdin', data=value).decode().strip()
                rows.append('100644 blob ' + oid + '\t' + name + '\n')
        return git(repo, 'mktree', data=''.join(rows).encode()).decode().strip()

    return make(nested)


def commit(repo, files, parent=None, message=b'NON_ACCEPTANCE fixture\n'):
    args = ['commit-tree', tree(repo, files)]
    if parent:
        args += ['-p', parent]
    return git(repo, *args, data=message).decode().strip()


class GitHttpsHandler(http.server.BaseHTTPRequestHandler):
    protocol_version = 'HTTP/1.1'

    def log_message(self, *_):
        pass

    def do_GET(self):
        self.handle_git()

    def do_POST(self):
        self.handle_git()

    def handle_git(self):
        url = urlsplit(self.path)
        if not url.path.startswith('/fixture.git/'):
            self.send_error(404)
            return
        if url.path.endswith('/info/refs'):
            self.server.discovery_calls += 1
            if self.server.discovery_calls == 3:
                if self.server.change_head:
                    git(self.server.repo, 'update-ref', self.server.branch_ref, self.server.change_head)
                if self.server.delay_final:
                    time.sleep(self.server.delay_final)
        length = int(self.headers.get('Content-Length', '0'))
        raw = self.rfile.read(length) if length else b''
        env = {'PATH': '/usr/bin:/bin', 'LC_ALL': 'C',
               'GIT_PROJECT_ROOT': str(self.server.root), 'GIT_HTTP_EXPORT_ALL': '1',
               'REQUEST_METHOD': self.command, 'PATH_INFO': url.path,
               'QUERY_STRING': url.query, 'CONTENT_TYPE': self.headers.get('Content-Type', ''),
               'CONTENT_LENGTH': str(length), 'SERVER_PROTOCOL': 'HTTP/1.1',
               'REMOTE_ADDR': '127.0.0.1', 'GIT_CONFIG_NOSYSTEM': '1',
               'GIT_CONFIG_GLOBAL': '/dev/null', 'GIT_CONFIG_SYSTEM': '/dev/null'}
        proc = subprocess.run([GIT, 'http-backend'], input=raw, stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE, env=env, timeout=10)
        headers, body = proc.stdout.split(b'\r\n\r\n', 1)
        status = 200
        parsed = []
        for line in headers.split(b'\r\n'):
            key, value = line.decode().split(':', 1)
            if key.lower() == 'status':
                status = int(value.strip().split()[0])
            else:
                parsed.append((key, value.strip()))
        self.send_response(status)
        for key, value in parsed:
            self.send_header(key, value)
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        try:
            self.wfile.write(body)
        except (BrokenPipeError, ssl.SSLError):
            pass


class Fixture:
    def __init__(self, name, variant='valid'):
        self.path = EVIDENCE / name
        self.path.mkdir(parents=True, exist_ok=False)
        self.repo = self.path / 'fixture.git'
        subprocess.run([GIT, 'init', '--bare', '--quiet', str(self.repo)], check=True)
        module = load(SOURCE / 'live_control.py', 'fixture_controls')
        self.branch = module.CONTROL_BRANCH
        self.baseline = {'BASELINE.txt': b'NON_ACCEPTANCE fixture only; no original authority.\n'}
        self.parent = commit(self.repo, self.baseline)
        now = int(time.time())
        expires = now + (4 if variant == 'utc_expiry' else 90)
        request = {'schema': 'dg16.full-correspondence-live-review-request.v1', 'authority': 'NONE',
                   'repository': module.REPOSITORY, 'run_id': 'NON_ACCEPTANCE_' + name,
                   'run_attempt': 1, 'workflow_commit': self.parent,
                   'source_commit': '1' * 40, 'source_tree': '2' * 40,
                   'policy_sha256': '3' * 64, 'policy_adoption_sha256': '4' * 64,
                   'proof': descriptor(b'NON_ACCEPTANCE proof fixture'),
                   'private_observations': descriptor(b'NON_ACCEPTANCE private fixture'),
                   'hold_seconds': 3600, 'created_utc_epoch': expires - 3600,
                   'expires_utc_epoch': expires, 'control_branch': self.branch,
                   'control_path': 'qualification/dg16-full-g2-control/NON_ACCEPTANCE_' + name + '-1',
                   'private_inputs_retained_while_live': True,
                   'same_job_closing_readback_required': True,
                   'original_acceptance': False, 'automatic_full_G2_award': False}
        request_raw = canonical(request)
        common = {key: request[key] for key in ('source_commit', 'source_tree', 'policy_sha256', 'policy_adoption_sha256')}
        common.update(request_sha256=sha(request_raw), proof_sha256=request['proof']['sha256'],
                      private_observations_sha256=request['private_observations']['sha256'])
        reviewer = module.CURRENT_AUTHORS[0] if variant == 'author_as_reviewer' else '/root/non_acceptance_fixture_reviewer'
        review = {'schema': 'dg16.full-correspondence-independent-live-review.v1', 'authority': 'NONE',
                  'decision': 'PASS', 'blocking_findings': [],
                  'scope': 'ACTUAL_FULL_CORRESPONDENCE_PROOF_WHILE_PRIVATE_INPUTS_REMAIN_LIVE',
                  'reviewer': reviewer, **common}
        review_raw = canonical(review)
        root = {'schema': 'dg16.full-correspondence-root-consumption.v1', 'author': '/root',
                'successor': 'PRO-EXECUTOR-01, designated by owner',
                'decision': 'CONSUME_AT_DECLARED_SCOPE_SUBJECT_TO_CLOSING_READBACK', 'one_shot': True,
                'review_sha256': sha(review_raw), 'reviewer': reviewer,
                'automatic_full_G2_award': False, 'original_source_or_product_limits_changed': False, **common}
        root_raw = canonical(root)
        control = {'schema': 'dg16.full-correspondence-live-control.v1', 'publisher': '/root',
                   'successor': 'PRO-EXECUTOR-01, designated by owner', 'repository': module.REPOSITORY,
                   'run_id': request['run_id'], 'run_attempt': 1, 'workflow_commit': self.parent,
                   'request_sha256': sha(request_raw), 'proof_sha256': request['proof']['sha256'],
                   'private_observations_sha256': request['private_observations']['sha256'],
                   'decision': 'CONSUME', 'files': {'INDEPENDENT_REVIEW.json': descriptor(review_raw),
                                                  'ROOT_CONSUMPTION.json': descriptor(root_raw)}}
        self.payload = {'CONTROL.json': canonical(control), 'INDEPENDENT_REVIEW.json': review_raw,
                        'ROOT_CONSUMPTION.json': root_raw}
        if variant == 'tampered_review':
            self.payload['INDEPENDENT_REVIEW.json'] += b' '
        files = {**self.baseline, **{request['control_path'] + '/' + k: v for k, v in self.payload.items()}}
        if variant == 'extra_addition':
            files['UNAUTHORIZED_EXTRA.txt'] = b'guard must reject this\n'
        parent = self.parent
        if variant == 'wrong_parent':
            parent = commit(self.repo, self.baseline, message=b'Other NON_ACCEPTANCE parent\n')
        self.control_commit = commit(self.repo, files, parent)
        self.alternate_commit = commit(self.repo, files, parent, message=b'Changed NON_ACCEPTANCE head\n')
        if variant != 'absent_ref':
            git(self.repo, 'update-ref', 'refs/heads/' + self.branch, self.control_commit)
        self.request = request
        (self.path / 'REQUEST.json').write_bytes(request_raw)
        (self.path / 'TEST_SCOPE.json').write_bytes(canonical({'scope': 'SYNTHETIC_NON_ACCEPTANCE',
            'original_run_replayed': False, 'genuine_review_claim': False,
            'root_consumption_authority': False, 'original_acceptance': False,
            'fixture_parent': self.parent, 'fixture_control_commit': self.control_commit,
            'variant': variant, 'source_live_control_sha256': sha((SOURCE / 'live_control.py').read_bytes()),
            'source_host_utility_sha256': sha((SOURCE / 'host_utility.py').read_bytes())}))
        self.server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), GitHttpsHandler)
        self.server.root = self.path
        self.server.repo = self.repo
        self.server.branch_ref = 'refs/heads/' + self.branch
        self.server.discovery_calls = 0
        self.server.change_head = self.alternate_commit if variant == 'changed_head' else None
        self.server.delay_final = 4.1 if variant == 'utc_expiry' else 0
        tls = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        tls.load_cert_chain(str(EVIDENCE / 'tls/cert.pem'), str(EVIDENCE / 'tls/key.pem'))
        self.server.socket = tls.wrap_socket(self.server.socket, server_side=True)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.remote = 'https://127.0.0.1:%d/fixture.git' % self.server.server_port
        self.variant = variant

    def run(self, seconds=10, remote=None, repeat=False):
        config = {'source': str(SOURCE), 'request': str(self.path / 'REQUEST.json'),
                  'work': str(self.path / 'consumed'), 'result': str(self.path / 'worker-result.json'),
                  'git_path': str(EVIDENCE / 'git-with-fixture-ca'), 'remote': remote or self.remote,
                  'seconds': seconds, 'repeat': repeat}
        (self.path / 'worker-config.json').write_bytes(canonical(config))
        p = subprocess.run([sys.executable, '-I', '-S', '-B', str(Path(__file__)), '--worker', str(self.path / 'worker-config.json')],
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=20,
                           env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'})
        (self.path / 'worker.stdout').write_bytes(p.stdout)
        (self.path / 'worker.stderr').write_bytes(p.stderr)
        if p.returncode:
            raise RuntimeError('Worker failed independently of consumer: ' + p.stderr.decode())
        result = json.loads((self.path / 'worker-result.json').read_text())
        result['https_discovery_calls'] = self.server.discovery_calls
        (self.path / 'route-result.json').write_bytes(canonical(result))
        return result

    def close(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=3)


def worker(config_path):
    c = json.loads(Path(config_path).read_text())
    source = Path(c['source'])
    control = load(source / 'live_control.py', 'production_control')
    utility = load(source / 'host_utility.py', 'production_utility')
    control.REMOTE = c['remote']
    lib = ctypes.CDLL(None, use_errno=True)
    actual = ctypes.c_int()
    assert lib.prctl(36, 1, 0, 0, 0) == 0
    assert lib.prctl(37, ctypes.byref(actual), 0, 0, 0) == 0 and actual.value == 1
    work = Path(c['work'])
    work.mkdir(mode=0o700)
    request_raw = Path(c['request']).read_bytes()
    before = time.monotonic()
    result = {'scope': 'SYNTHETIC_NON_ACCEPTANCE', 'subreaper_enabled_and_read_back': True,
              'production_capture_unchanged': True, 'production_safe_environment_unchanged': True,
              'accepted': False, 'refusal': None}
    try:
        reserved = control.hold(work, request_raw, before + c['seconds'], utility, c['git_path'])
        result.update(accepted=True, reservation=reserved)
        # The exact production validation used by original closing must accept
        # the byte-exact reserved payload at its accepted time. This is the
        # control portion only, not raw-capture/currentness/native closing.
        payload = {name: (work / name).read_bytes() for name in NAMES}
        closing = control.validate(payload, request_raw, now=reserved['accepted_utc_epoch'])
        result['reserved_payload_revalidated'] = all(reserved[k] == v for k, v in closing.items())
        if c['repeat']:
            try:
                control.hold(work, request_raw, time.monotonic() + c['seconds'], utility, c['git_path'])
            except control.Refusal as exc:
                result['repeat_refusal'] = str(exc)
            else:
                result['repeat_refusal'] = 'MISSING'
    except (control.Refusal, utility.Refusal) as exc:
        result['refusal'] = str(exc)
    result['elapsed_seconds'] = time.monotonic() - before
    result['reservation_present'] = (work / 'CONSUMPTION_RESERVED.json').exists()
    if (work / 'CONTROL_READS.json').exists():
        reads = json.loads((work / 'CONTROL_READS.json').read_text())
        result['commands'] = reads['commands']
        result['seen_commits'] = reads['seen_commits']
        result['automatic_retry'] = reads['automatic_retry']
    Path(c['result']).write_bytes(canonical(result))


class FullRouteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        EVIDENCE.mkdir(parents=True, exist_ok=False)
        tls = EVIDENCE / 'tls'
        tls.mkdir()
        proc = subprocess.run(['openssl', 'req', '-x509', '-newkey', 'rsa:2048', '-nodes',
                               '-keyout', str(tls / 'key.pem'), '-out', str(tls / 'cert.pem'),
                               '-sha256', '-days', '1', '-subj', '/CN=localhost',
                               '-addext', 'subjectAltName=DNS:localhost,IP:127.0.0.1'],
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=10)
        if proc.returncode:
            raise RuntimeError('Fixture TLS certificate creation failed')
        wrapper = EVIDENCE / 'git-with-fixture-ca'
        wrapper.write_text('#!/usr/bin/python3\nimport os,sys\nos.execv(' + repr(GIT) + ', [' +
                           repr(GIT) + ', "-c", ' + repr('http.sslCAInfo=' + str(tls / 'cert.pem')) +
                           '] + sys.argv[1:])\n')
        wrapper.chmod(0o700)

    def fixture(self, name, variant='valid'):
        f = Fixture(name, variant)
        self.addCleanup(f.close)
        return f

    def assert_refused_without_reservation(self, f, expected, **kwargs):
        result = f.run(**kwargs)
        self.assertFalse(result['accepted'])
        self.assertEqual(result['refusal'], expected)
        self.assertFalse(result['reservation_present'])
        self.assertTrue(all(c.get('cleanup', {}).get('echild') is True for c in result['commands']))
        return result

    def test_complete_real_https_route_reserves_once_and_revalidates_payload(self):
        # Removing either HTTPS override must prevent this real reservation.
        f = self.fixture('valid')
        result = f.run(seconds=10, repeat=True)
        self.assertTrue(result['accepted'], result['refusal'])
        self.assertEqual(result['reservation']['control_commit'], f.control_commit)
        self.assertEqual(result['reservation']['request_sha256'], sha((f.path / 'REQUEST.json').read_bytes()))
        self.assertTrue(result['reserved_payload_revalidated'])
        self.assertEqual(result['repeat_refusal'], 'NO_REPEAT_LIVE_CONSUMPTION')
        self.assertLess(result['reservation']['accepted_utc_epoch'], f.request['expires_utc_epoch'])
        self.assertEqual(result['https_discovery_calls'], 3)
        self.assertEqual(len(result['commands']), 13)
        self.assertTrue(all(c['returncode'] == 0 and c['streams_complete'] and c['pidfd_acquired']
                            and c['cleanup']['echild'] and not c['timeout']
                            and not c['output_bound_exceeded'] for c in result['commands']))
        for name, raw in f.payload.items():
            self.assertEqual((f.path / 'consumed' / name).read_bytes(), raw)

    def test_fatal_discovery_refuses_immediately_without_polling(self):
        # Restoring status128-as-missing changes refusal to expiry, failing here.
        f = self.fixture('fatal')
        with socket.socket() as unavailable:
            unavailable.bind(('127.0.0.1', 0))
            remote = 'https://127.0.0.1:%d/fixture.git' % unavailable.getsockname()[1]
            result = self.assert_refused_without_reservation(f, 'LIVE_CONTROL_GIT_REFUSED', seconds=0.4, remote=remote)
        self.assertEqual(result['commands'][-1]['returncode'], 128)
        self.assertEqual(len(result['commands']), 2)

    def test_documented_absent_ref_polls_only_within_deadline(self):
        f = self.fixture('absent', 'absent_ref')
        result = self.assert_refused_without_reservation(f, 'ACTUAL_REVIEW_WINDOW_EXPIRED', seconds=0.3)
        self.assertEqual(result['commands'][-1]['returncode'], 2)
        self.assertEqual(result['seen_commits'], [])

    def test_wrong_parent_is_rejected(self):
        self.assert_refused_without_reservation(self.fixture('parent', 'wrong_parent'), 'LIVE_CONTROL_SOLE_WORKFLOW_PARENT')

    def test_extra_tree_addition_is_rejected(self):
        self.assert_refused_without_reservation(self.fixture('delta', 'extra_addition'), 'LIVE_CONTROL_EXACT_ONLY_ADDITIONS')

    def test_authored_source_cannot_supply_independent_review(self):
        self.assert_refused_without_reservation(self.fixture('author', 'author_as_reviewer'), 'ACTUAL_INDEPENDENT_LIVE_REVIEW_REQUIRED')

    def test_review_byte_change_is_rejected(self):
        self.assert_refused_without_reservation(self.fixture('digest', 'tampered_review'), 'LIVE_DECISION_DIGEST')

    def test_remote_head_change_before_reservation_is_rejected(self):
        self.assert_refused_without_reservation(self.fixture('moving', 'changed_head'), 'LIVE_CONTROL_CHANGED_OR_EXPIRED')

    def test_utc_expiry_during_final_read_prevents_reservation(self):
        self.assert_refused_without_reservation(self.fixture('expiry', 'utc_expiry'), 'LIVE_CONTROL_CHANGED_OR_EXPIRED')

    def test_other_transport_stays_denied(self):
        f = self.fixture('file_denial')
        result = self.assert_refused_without_reservation(f, 'LIVE_CONTROL_GIT_REFUSED', remote='file://' + str(f.repo))
        self.assertEqual(result['commands'][-1]['returncode'], 128)
        self.assertEqual(result['https_discovery_calls'], 0)


if __name__ == '__main__':
    if len(sys.argv) == 3 and sys.argv[1] == '--worker':
        worker(sys.argv[2])
    else:
        unittest.main(verbosity=2)
