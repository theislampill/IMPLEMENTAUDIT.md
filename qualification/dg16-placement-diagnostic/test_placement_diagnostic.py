#!/usr/bin/env python3
"""Local, unprivileged qualification of the placement-only diagnostic proposal.

Run from a clone whose HEAD is the proposal commit:
  /usr/bin/python3.12 -I -B qualification/dg16-placement-diagnostic/test_placement_diagnostic.py
Optional local inputs (no download is performed by any test):
  DG16_PLACEMENT_DEB=<local copy of the pinned .deb>  DG16_PLACEMENT_PINNED_BWRAP=<bwrap extracted from it>
No test uses sudo or host root. Every receipt built here is SYNTHETIC or a LOCAL
user-namespace simulation (uid 0 mapped to the invoking user, namespace-only caps);
none is host evidence.
"""
import base64, copy, hashlib, io, json, os, re, shutil, stat, subprocess, sys, tempfile, types, unittest, zipfile
from pathlib import Path

HERE = Path(os.path.abspath(__file__)).parent
REPO = HERE.parent.parent
WORKFLOW = REPO / '.github/workflows/dg16-placement-diagnostic.yml'
TRIGGER = 'engineering/opus-dg16-placement-diag-trigger-20261125'


def module(name, path=None):
    path = path or HERE / (name + '.py')
    m = types.ModuleType('t_' + name)
    m.__file__ = str(path)
    exec(compile(Path(path).read_bytes(), m.__file__, 'exec'), m.__dict__)
    return m


D, RCV, A, R = module('diagnose'), module('receive'), module('access_matrix'), module('root_placement')
sha = lambda raw: hashlib.sha256(raw).hexdigest()
HEAD = subprocess.run(['git', '-C', str(REPO), 'rev-parse', 'HEAD'], stdout=subprocess.PIPE, check=True).stdout.decode().strip()
LOCAL_RUN = '900000000001'


def local_env(**over):
    env = dict(GITHUB_ACTIONS='true', RUNNER_ENVIRONMENT='github-hosted', GITHUB_REPOSITORY='theislampill/IMPLEMENTAUDIT.md',
               GITHUB_EVENT_NAME='push', GITHUB_REF='refs/heads/' + TRIGGER, GITHUB_RUN_ATTEMPT='1',
               GITHUB_RUN_ID=LOCAL_RUN, GITHUB_SHA=HEAD)
    env.update(over)
    return env


def exec_copy(tmp, run_id=LOCAL_RUN):
    """Mirror the workflow's staging: 0700 directories, 0400 copies of exactly the pinned files."""
    root = Path(tmp) / ('dg16-placement-exec-%s-a1' % run_id)
    root.mkdir(0o700)
    for rel in ('qualification', D.EXEC_DIR, 'scripts'):
        (root / rel).mkdir(0o700)
    for rel in D.EXEC_FILES:
        shutil.copyfile(REPO / rel, root / rel)
        os.chmod(root / rel, 0o400)
    for rel in ('.', 'qualification', D.EXEC_DIR, 'scripts'):
        os.chmod(root / rel, 0o700)
    return root


class Canonical(unittest.TestCase):
    def test_encode_and_parse(self):
        value = {'b': [1, {'z': None, 'a': chr(0xE9)}], 'a': True}
        raw = D.encode(value)
        self.assertEqual(raw, b'{"a":true,"b":[1,{"a":"\\u00e9","z":null}]}\n')
        self.assertEqual(raw, RCV.encode(value))
        self.assertEqual(raw, R.encode(value))
        self.assertEqual(RCV.canonical_parse(raw, 'X'), value)
        for bad, code in ((b'{"a":1,"a":2}\n', 'X_DUPLICATE_KEY'), (b'{"a":NaN}\n', 'X_NONFINITE'),
                          (b'{"a": 1}\n', 'X_NOT_CANONICAL'), (b'\xff', 'X_UNPARSEABLE')):
            with self.assertRaises(RCV.Refused) as ctx:
                RCV.canonical_parse(bad, 'X')
            self.assertEqual(ctx.exception.args[0], code)
        with self.assertRaises(ValueError):
            D.encode({'a': float('nan')})

    def test_population_agrees(self):
        self.assertEqual(len(D.STEPS), 23)
        self.assertEqual(D.STEPS, RCV.STEPS)
        self.assertEqual(tuple(D.PROPERTIES), RCV.PROPERTIES)
        self.assertEqual(D.SETUP, RCV.SETUP)
        self.assertEqual(D.LAUNCHER_PACKAGE, RCV.PACKAGE)
        self.assertEqual((D.PROBE, D.RETRY_LINE), (RCV.PROBE, RCV.RETRY_LINE))
        self.assertEqual(sorted(s for steps in D.PROPERTIES.values() for s in steps),
                         sorted(set(D.STEPS) - {'HOSTED_CONTEXT', 'EXEC_CUSTODY', 'HOST_FACTS'}))
        self.assertTrue(all(s in D.STEPS for s in RCV.PARTIAL_STEPS))
        self.assertTrue(D.STEPS.index('LIVE_CURRENT') < min(D.STEPS.index(s) for s in RCV.PARTIAL_STEPS))
        self.assertEqual((D.SOURCE_MODE, D.OUTPUT_MODE), (0o755, 0o755))


class OperatorUnprivileged(unittest.TestCase):
    def test_refuses_without_root_and_creates_nothing(self):
        if os.geteuid() == 0:
            self.skipTest('must run unprivileged')
        r = D.observe(local_env(), HERE)
        self.assertEqual((r['status'], r['failure']), ('REFUSED', 'ROOT_CREDENTIALS_REQUIRED'))
        rows = {s['step']: s['result'] for s in r['steps']}
        self.assertEqual((rows['HOSTED_CONTEXT'], rows['CREDENTIALS']), ('PASS', 'REFUSED'))
        self.assertTrue(all(v == 'NOT_ATTEMPTED' for k, v in rows.items() if k not in ('HOSTED_CONTEXT', 'CREDENTIALS')))
        self.assertEqual(set(r['properties'].values()), {'NOT_OBSERVED'})
        self.assertFalse(os.path.lexists('/dg16-g1-' + LOCAL_RUN))

    def test_scope_refusals(self):
        for over, code in ((dict(RUNNER_ENVIRONMENT='self-hosted'), 'HOSTED_REQUIRED'),
                           (dict(GITHUB_ACTIONS=''), 'HOSTED_REQUIRED'),
                           (dict(GITHUB_REF='refs/heads/main'), 'TRIGGER_SCOPE_REQUIRED'),
                           (dict(GITHUB_EVENT_NAME='workflow_dispatch'), 'TRIGGER_SCOPE_REQUIRED'),
                           (dict(GITHUB_REPOSITORY='fork/IMPLEMENTAUDIT.md'), 'TRIGGER_SCOPE_REQUIRED'),
                           (dict(GITHUB_RUN_ATTEMPT='2'), 'FIRST_ATTEMPT_REQUIRED'),
                           (dict(GITHUB_SHA='abc'), 'RUN_IDENTITY_SHAPE')):
            r = D.observe(local_env(**over), HERE)
            self.assertEqual((r['status'], r['failure']), ('REFUSED', code), over)
            self.assertEqual(r['steps'][0], dict(step='HOSTED_CONTEXT', result='REFUSED', code=code))

    def test_module_pin_refusal(self):
        with tempfile.TemporaryDirectory() as tmp:
            for n in ('diagnose.py', 'root_placement.py', 'access_matrix.py'):
                shutil.copyfile(HERE / n, Path(tmp) / n)
            raw = bytearray((Path(tmp) / 'root_placement.py').read_bytes())
            raw[-2] ^= 1
            (Path(tmp) / 'root_placement.py').write_bytes(bytes(raw))
            self.assertEqual(D.observe(local_env(), Path(tmp))['failure'], 'MODULE_ROOT_PLACEMENT_PIN')
            (Path(tmp) / 'root_placement.py').write_bytes(bytes(raw) + b'#')
            self.assertEqual(D.observe(local_env(), Path(tmp))['failure'], 'MODULE_ROOT_PLACEMENT_SHAPE')

    def test_exec_custody_refusals(self):
        """Item 7: layout, owner/mode and population of the exec copy (owner refuses unprivileged)."""
        with tempfile.TemporaryDirectory() as tmp:
            root = exec_copy(tmp)
            here = root / D.EXEC_DIR
            with self.assertRaises(D.Refused) as ctx:
                D.exec_custody(here, '123')
            self.assertEqual(ctx.exception.args[0], 'EXEC_LAYOUT')
            with self.assertRaises(D.Refused) as ctx:
                D.exec_custody(here, LOCAL_RUN)
            self.assertEqual(ctx.exception.args[0], 'EXEC_LAYOUT')  # parent is not /run
        self.assertEqual(D.EXEC_PARENT, '/run')

    def test_transport_chunks(self):
        r = D.observe(local_env(), HERE)
        big = dict(r, padding='x' * 9000)
        with tempfile.TemporaryDirectory() as tmp:
            files, lines = D.publish(big, tmp + '/out')
            self.assertTrue(all(len(l.split(' ')[-1]) <= 4096 for l in lines if ' RECEIPT.json ' in l and '/' in l.split(' ')[2]))
            chunks = [l for l in lines if l.startswith(D.MARKER + ' RECEIPT.json ')]
            self.assertGreaterEqual(len(chunks), 3)
            members = RCV.log_members('\n'.join('2026-11-25T00:00:00.0000000Z ' + l for l in lines))
            self.assertEqual(members, files)
            for name, raw in files.items():
                self.assertEqual((Path(tmp) / 'out/public' / name).read_bytes(), raw)
                self.assertEqual(os.stat(Path(tmp) / 'out/public' / name).st_mode & 0o777, 0o644)
            with self.assertRaises(FileExistsError):
                D.publish(r, tmp + '/out')

    def test_launcher_single_502_retry_rule(self):
        """Item 5: exactly one retry, only on the HTTP 502 final line, only while the target is absent."""
        ok = D.encode(dict(scope=D.PROVISION_SCOPE, package=D.LAUNCHER_PACKAGE, target='/usr/bin/bwrap',
                           launcher=dict(bytes=72160, sha256=A.BWRAP_SHA, opening=[1], closing=[1], mode='0755',
                                         exclusive_creation=True)))
        e502 = b'Traceback (most recent call last):\n  x\n' + D.RETRY_LINE + b'\n'
        def case(results, exists_after_first=False):
            calls = []
            def fake_run(command, seconds, monotonic, limit=D.STREAM_BYTES, **kw):
                rc, err = results[len(calls)]
                calls.append(command)
                row = dict(argv=command, returncode=rc, timeout=False, stdout=D.stream(ok if rc == 0 else b''),
                           stderr=D.stream(err), elapsed_ns=1)
                return row, (ok if rc == 0 else b''), err
            class OS:
                def __getattr__(self, n):
                    return getattr(os, n)
            proxy = OS()
            proxy.lstat = lambda p: (_ for _ in ()).throw(FileNotFoundError(p))
            proxy.path = types.SimpleNamespace(lexists=lambda p: exists_after_first)
            saved = (D.os, D.bounded_run, D.pinned_bytes)
            D.os, D.bounded_run, D.pinned_bytes = proxy, fake_run, lambda *a: b''
            O = {}
            try:
                D.launcher_provision('/x', O, {}, lambda: 0.0)
                return 'PASS', O['launcher_provision'], len(calls)
            except D.Refused as exc:
                return exc.args[0], O['launcher_provision'], len(calls)
            finally:
                D.os, D.bounded_run, D.pinned_bytes = saved
        self.assertEqual(case([(0, b'')])[0::2], ('PASS', 1))
        code, rec, n = case([(1, e502), (0, b'')])
        self.assertEqual((code, n, [a['attempt'] for a in rec['attempts']], rec['attempts'][0]['retry_eligible']),
                         ('PASS', 2, [1, 2], True))
        self.assertEqual(case([(1, e502), (1, e502)])[0::2], ('LAUNCHER_PROVISION_REFUSED', 2))
        self.assertEqual(case([(1, b'urllib.error.URLError: x\n')])[0::2], ('LAUNCHER_PROVISION_REFUSED', 1))
        self.assertEqual(case([(1, e502 + b'extra\n')])[0::2], ('LAUNCHER_PROVISION_REFUSED', 1))
        self.assertEqual(case([(1, e502)], exists_after_first=True)[0::2], ('LAUNCHER_PROVISION_REFUSED', 1))


class ObservationPrimitives(unittest.TestCase):
    """Maintained functions against unprivileged temp directories (refusal or shape only)."""

    def test_observe_fd_refuses_non_root_owner(self):
        if os.geteuid() == 0:
            self.skipTest('must run unprivileged')
        with tempfile.TemporaryDirectory() as tmp:
            fd = R.open_dir(tmp)
            try:
                with self.assertRaises(ValueError) as ctx:
                    R.observe_fd(fd)
                self.assertEqual(ctx.exception.args[0], 'DIRECTORY_CUSTODY')
            finally:
                os.close(fd)
        with self.assertRaises(ValueError):
            R.credentials()

    def test_write_new_and_read_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            fd = R.open_dir(tmp)
            try:
                R.write_new('probe', D.PROBE, fd)
                info = os.stat('probe', dir_fd=fd)
                self.assertEqual((stat.S_IMODE(info.st_mode), info.st_nlink), (0o400, 1))
                self.assertEqual(R.read_file(Path(tmp) / 'probe', 4096), D.PROBE)
                with self.assertRaises(FileExistsError):
                    R.write_new('probe', D.PROBE, fd)
            finally:
                os.close(fd)

    def test_open_dir_refuses_symlink(self):
        with tempfile.TemporaryDirectory() as tmp:
            os.mkdir(tmp + '/real')
            os.symlink('real', tmp + '/alias')
            parent = R.open_dir(tmp)
            try:
                with self.assertRaises(OSError):
                    R.open_dir('alias', parent)
            finally:
                os.close(parent)

    def test_snapshot_shape_on_owned_target(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = os.path.realpath(tmp) + '/target'
            os.mkdir(target, 0o700)
            with open(target + '/sentinel', 'wb') as f:
                f.write(A.SENTINEL)
            fd = R.open_dir(target)
            try:
                s = A.snapshot(target, fd)
                A.check_snapshot(A.project_snapshot(s))
                self.assertEqual((s['fd_link'], s['paths'][-1], len(s['mounts'])), (target, target, len(s['paths'])))
            finally:
                os.close(fd)

    def test_children_and_limits(self):
        self.assertTrue(all(v == [] for v in D.children().values()))
        done = subprocess.run([sys.executable, '-I', '-c', 'import resource;print(resource.getrlimit(resource.RLIMIT_CPU),'
                               'resource.getrlimit(resource.RLIMIT_AS))'], stdout=subprocess.PIPE, preexec_fn=D.child_limits)
        self.assertEqual(done.stdout.strip(), b'(5, 5) (268435456, 268435456)')

    def test_receiver_argv_matches_pinned_module(self):
        pinned = RCV.pinned_access_matrix(str(REPO), HEAD)
        for root in A.HOST_ROOTS:
            self.assertTrue(os.path.exists(root), root)
        self.assertEqual(pinned.argv('/usr/bin/bwrap', '/dg16-g1-7/packet', 5, 'FD'),
                         A.argv('/usr/bin/bwrap', '/dg16-g1-7/packet', 5, 'FD'))


def bwrap_works():
    try:
        done = subprocess.run(['/usr/bin/bwrap', '--unshare-user', '--ro-bind', '/', '/', '/bin/true'],
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=10)
        return done.returncode == 0
    except (OSError, subprocess.SubprocessError):
        return False


FD_MECHANICS = r'''
import json, os, subprocess, sys, types
m = types.ModuleType('am'); m.__file__ = sys.argv[1]
exec(compile(open(sys.argv[1], 'rb').read(), sys.argv[1], 'exec'), m.__dict__)
os.mkdir('/dg16-g1-7', 0o700); os.mkdir('/dg16-g1-7/packet', 0o700)
with open('/dg16-g1-7/packet/sentinel', 'wb') as f: f.write(m.SENTINEL)
fd = os.open('/dg16-g1-7/packet', os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
before = m.snapshot('/dg16-g1-7/packet', fd)
cmd = m.argv('/usr/bin/bwrap', '/dg16-g1-7/packet', fd, 'FD')
done = subprocess.run(cmd, pass_fds=(fd,), stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                      env=m.environment(), timeout=10)
p = json.loads(done.stdout) if done.returncode == 0 else None
if p is not None: m.validate_payload(p, dict(route='FD', before=m.project_snapshot(before)))
print(json.dumps(dict(rc=done.returncode, err=done.stderr.decode('utf-8', 'replace'), payload=p)))
'''


@unittest.skipUnless(bwrap_works(), 'unprivileged bwrap/userns unavailable locally')
class LocalNamespaceMechanics(unittest.TestCase):
    """LOCAL mechanics only: '/' is a bwrap tmpfs, uid 0 is mapped to the invoking user, caps are namespace-only."""

    def sim_command(self, pinned_bwrap=None, absent_launcher=False):
        command = ['/usr/bin/bwrap', '--unshare-user', '--unshare-pid', '--uid', '0', '--gid', '0', '--cap-add', 'ALL',
                   '--die-with-parent']
        if absent_launcher:
            command += ['--unshare-net', '--tmpfs', '/usr']
            for sub in ('lib', 'lib64', 'share', 'sbin'):
                if os.path.isdir('/usr/' + sub):
                    command += ['--ro-bind', '/usr/' + sub, '/usr/' + sub]
            command += ['--tmpfs', '/usr/bin', '--ro-bind', '/usr/bin/python3.12', '/usr/bin/python3.12',
                        '--ro-bind', '/usr/bin/env', '/usr/bin/env']
        else:
            command += ['--ro-bind', '/usr', '/usr']
        command += ['--ro-bind', '/etc', '/etc', '--proc', '/proc', '--dev', '/dev', '--tmpfs', '/tmp']
        if pinned_bwrap is not None:
            command += ['--ro-bind', pinned_bwrap, '/usr/bin/bwrap']
        for link in ('bin', 'lib', 'lib64', 'sbin'):
            if os.path.islink('/' + link):
                command += ['--symlink', os.readlink('/' + link), '/' + link]
        return command

    def simulate(self, pinned_bwrap=None, absent_launcher=False):
        tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, tmp, True)
        self.addCleanup(lambda: [os.chmod(os.path.join(a, d), 0o700) for a, ds, _ in os.walk(tmp) for d in ds])
        root = exec_copy(tmp)
        out = Path(tmp) / 'out'
        out.mkdir()
        x = '/run/' + root.name
        command = self.sim_command(pinned_bwrap, absent_launcher)
        command += ['--ro-bind', str(root), x, '--bind', str(out), '/out', '--clearenv']
        for k, v in sorted(local_env().items()):
            command += ['--setenv', k, v]
        command += ['/usr/bin/python3.12', '-I', '-S', '-B', x + '/' + D.EXEC_DIR + '/diagnose.py', '--output', '/out/x']
        done = subprocess.run(command, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=120)
        self.assertEqual(done.stderr, b'')
        files = {n: (out / 'x/public' / n).read_bytes() for n in RCV.NAMES}
        self.assertEqual(RCV.log_members(done.stdout.decode()), files)
        r = RCV.canonical_parse(files['RECEIPT.json'], 'SIM')
        self.assertEqual(r['observations']['exec']['root'], x)
        return done, files, r, {s['step']: s['result'] for s in r['steps']}

    def receive_partial(self, done, files):
        """End-to-end partial receiving of a LOCAL simulation (synthetic run metadata, real log bytes)."""
        b = bundle(None, raw_files=files, run_id=int(LOCAL_RUN), conclusion='failure')
        b['log_text'] = done.stdout.decode()
        return RCV.receive(**b)

    def test_operator_unpinned_launcher_partial(self):
        done, files, r, rows = self.simulate()
        self.assertEqual((done.returncode, r['failure'], rows['TOOL_PIN']), (1, 'TOOL_PRECONDITION', 'REFUSED'), rows)
        self.assertEqual(r['observations']['launcher_provision']['mode'], 'PREEXISTING_NOT_PROVISIONED')
        self.assertTrue(all(rows[s] == 'PASS' for s in D.STEPS[:D.STEPS.index('TOOL_PIN')]), rows)
        A2 = RCV.pinned_access_matrix(str(REPO), HEAD)
        self.assertEqual(RCV.derive(r, A2), {**{k: True for k in RCV.PARTIAL}, 'P5_FD_ROUTE': False,
                                             'P6_ANCESTRY_NO_DRIFT': False, 'P7_CLOSING_CURRENTNESS': False})
        got = self.receive_partial(done, files)
        self.assertEqual((got['status'], got['substitutable_for_full'], got['failed_step'], got['launcher_mode'], got['replaces']),
                         ('RECEIVED_PARTIAL_P1_P4', False, 'TOOL_PIN', 'PREEXISTING_NOT_PROVISIONED',
                          'NOTHING_WITHOUT_NEW_ROOT_COMPOSITION'))
        O = r['observations']
        self.assertEqual((stat.S_IMODE(O['source']['identity']['mode']), stat.S_IMODE(O['output']['identity']['mode'])),
                         (0o755, 0o755))
        self.assertEqual(O['packet_files']['probe']['mode'], 0o100400)

    def test_operator_absent_launcher_runs_pinned_provisioner_offline(self):
        done, files, r, rows = self.simulate(absent_launcher=True)
        lp = r['observations']['launcher_provision']
        self.assertEqual((done.returncode, r['failure'], rows['LAUNCHER_PROVISION']), (1, 'LAUNCHER_PROVISION_REFUSED', 'REFUSED'))
        self.assertEqual((lp['before'], lp['mode'], lp['setup'], lp['package'], len(lp['attempts'])),
                         ('ABSENT', 'PROVISIONED_BY_MAINTAINED_V21_SETUP', RCV.SETUP, RCV.PACKAGE, 1))
        a = lp['attempts'][0]
        self.assertEqual(a['argv'], ['/usr/bin/python3.12', '-I', '-S', '-B', r['observations']['exec']['root'] + '/'
                                     + RCV.SETUP['path'], '--provision-hosted-launcher'])
        self.assertIn(b'urllib.error.URLError', base64.b64decode(a['stderr']['base64']))
        self.assertIs(a['retry_eligible'], False)
        got = self.receive_partial(done, files)
        self.assertEqual((got['status'], got['failed_step'], got['launcher_mode']),
                         ('RECEIVED_PARTIAL_P1_P4', 'LAUNCHER_PROVISION', 'PROVISIONED_BY_MAINTAINED_V21_SETUP'))

    @unittest.skipUnless(os.environ.get('DG16_PLACEMENT_PINNED_BWRAP'), 'set DG16_PLACEMENT_PINNED_BWRAP to a verified pinned bwrap')
    def test_operator_pinned_launcher_reaches_policy(self):
        """Pinned launcher: TOOL_PIN passes; the pinned policy step refuses (no AppArmor locally)."""
        pinned = os.environ['DG16_PLACEMENT_PINNED_BWRAP']
        raw = Path(pinned).read_bytes()
        self.assertEqual((len(raw), sha(raw)), RCV.BWRAP)
        done, files, r, rows = self.simulate(pinned)
        self.assertEqual((done.returncode, r['failure'], rows['TOOL_PIN'], rows['POLICY_PROVISION']),
                         (1, 'POLICY_PROVISION_REFUSED', 'PASS', 'REFUSED'), rows)
        pp = r['observations']['policy_provision']
        self.assertEqual(pp['argv'][:3], ['/usr/bin/env', 'GITHUB_ACTIONS=true', 'RUNNER_ENVIRONMENT=github-hosted'])
        self.assertNotEqual(pp['returncode'], 0)
        got = self.receive_partial(done, files)
        self.assertEqual((got['status'], got['failed_step']), ('RECEIVED_PARTIAL_P1_P4', 'POLICY_PROVISION'))

    @unittest.skipUnless(os.environ.get('DG16_PLACEMENT_PINNED_BWRAP'), 'set DG16_PLACEMENT_PINNED_BWRAP to a verified pinned bwrap')
    def test_fd_route_mechanics_with_pinned_launcher(self):
        """P5 mechanics with the pinned bwrap and the pinned argv/payload, under namespace uid 0 with caps."""
        command = self.sim_command(os.environ['DG16_PLACEMENT_PINNED_BWRAP'])
        command += ['--ro-bind', str(HERE / 'access_matrix.py'), '/am.py', '/usr/bin/python3.12', '-I', '-S', '-B', '-c',
                    FD_MECHANICS, '/am.py']
        done = subprocess.run(command, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=60)
        self.assertEqual((done.returncode, done.stderr), (0, b''))
        got = json.loads(done.stdout)
        self.assertEqual((got['rc'], got['err']), (0, ''))
        c = got['payload']['credentials']
        self.assertEqual((c['uid_map'], c['gid_map'], c['fields']['CapEff'], c['fields']['CapPrm'], got['payload']['readonly_errno']),
                         ([[0, 0, 1]], [[0, 0, 1]], 0, 0, 30))


@unittest.skipUnless(os.environ.get('DG16_PLACEMENT_DEB'), 'set DG16_PLACEMENT_DEB to a local copy of the pinned .deb')
class MaintainedLauncherDecode(unittest.TestCase):
    """The pinned V21 provisioner functions, offline, against a local copy of the pinned package."""

    def setUp(self):
        raw = (REPO / RCV.SETUP['path']).read_bytes()
        self.assertEqual((len(raw), sha(raw)), (RCV.SETUP['bytes'], RCV.SETUP['sha256']))
        self.S = module('setup', REPO / RCV.SETUP['path'])
        self.deb = Path(os.environ['DG16_PLACEMENT_DEB']).read_bytes()
        self.assertEqual((len(self.deb), sha(self.deb)), (RCV.PACKAGE['bytes'], RCV.PACKAGE['sha256']))
        self.assertEqual(self.S.HOSTED_PACKAGE_URL, RCV.PACKAGE['url'])
        self.assertEqual(self.S.HOSTED_BWRAP_POLICY_SHA256, RCV.POLICY_SHA)
        self.assertEqual(self.S.HOSTED_BWRAP_NAMES, RCV.POLICY_NAMES)

    def test_decode_and_exclusive_install_readback(self):
        launcher = self.S.decode_hosted_launcher(self.deb)
        self.assertEqual((len(launcher), sha(launcher)), RCV.BWRAP)
        with tempfile.TemporaryDirectory() as tmp:
            os.chmod(tmp, 0o755)
            fd = os.open(tmp, os.O_RDONLY | os.O_DIRECTORY)
            try:
                result = self.S.write_hosted_launcher(fd, launcher)
                self.assertEqual((result['bytes'], result['sha256'], result['mode'], result['exclusive_creation']),
                                 (72160, RCV.BWRAP[1], '0755', True))
                self.assertEqual(result['opening'], result['closing'])
                self.assertEqual((Path(tmp) / 'bwrap').read_bytes(), launcher)
                with self.assertRaises(FileExistsError):
                    self.S.write_hosted_launcher(fd, launcher)
            finally:
                os.close(fd)

    def test_decode_refusals(self):
        bad = bytearray(self.deb)
        bad[-1] ^= 1
        for raw in (bytes(bad), self.deb + b'x'):
            with self.assertRaises(ValueError):
                self.S.decode_hosted_launcher(raw)
        with self.assertRaises(ValueError):
            self.S.hosted_tar_launcher(bytes(1024))


# ---- synthetic receipts for receiver tests (never host evidence) ----
ACLS = RCV.ACLS
RUN_ID = 900000000002
EXEC_ROOT = '/run/dg16-placement-exec-%d-a1' % RUN_ID
POLICY_LOADED = {RCV.POLICY_NAMES[0]: dict(attach='/usr/bin/bwrap', mode='enforce', sha256='a' * 64),
                 RCV.POLICY_NAMES[1]: dict(attach=RCV.POLICY_NAMES[1], mode='enforce', sha256='b' * 64)}


def ident(inode, mode, kind=0o040000):
    return dict(device=2049, inode=inode, mode=kind | mode, uid=0, gid=0)


def text(value):
    raw = value.encode()
    return dict(readable=True, bounded=True, bytes=len(raw), sha256=sha(raw), text=value)


def policy_row(flag, record):
    raw = (json.dumps(record, sort_keys=True) + '\n').encode()
    return dict(argv=['/usr/bin/env', 'GITHUB_ACTIONS=true', 'RUNNER_ENVIRONMENT=github-hosted', '/usr/bin/python3.12',
                      '-I', '-S', '-B', EXEC_ROOT + '/' + D.SETUP['path'], flag],
                returncode=0, timeout=False, stdout=D.stream(raw, D.POLICY_STREAM_BYTES),
                stderr=D.stream(b'', D.POLICY_STREAM_BYTES), elapsed_ns=10**9, environment_keys=['GITHUB_ACTIONS'],
                record=copy.deepcopy(record))


def synthetic():
    base = '/dg16-g1-%d' % RUN_ID
    packet = base + '/packet'
    O = {}
    O['paths'] = dict(source=base + '/source', private_output=base + '/output', packet=packet)
    O['credentials'] = [0, 0, 0, 0]
    creds = dict(fields=dict(Uid=[0] * 4, Gid=[0] * 4, Groups=[0], CapInh=0, CapPrm=0x1ffffffffff, CapEff=0x1ffffffffff,
                             CapBnd=0x1ffffffffff, CapAmb=0, NoNewPrivs=0, Seccomp=0),
                 uid_map=[[0, 0, 4294967295]], gid_map=[[0, 0, 4294967295]], user_namespace=4026531837)
    O['parent_status'] = creds
    O['exec'] = dict(root=EXEC_ROOT, parent=dict(path='/run', mode=0o040755, uid=0, gid=0), directories={k: dict(mode=0o040700, uid=0, gid=0)
                                                  for k in ('.', 'qualification', D.EXEC_DIR, 'scripts')},
                     files={p: dict(bytes=len((REPO / p).read_bytes()), sha256=sha((REPO / p).read_bytes()), mode=0o100400)
                            for p in D.EXEC_FILES})
    for name, inode, mode in (('root', 2, 0o755), ('island', 100, 0o700), ('packet', 101, 0o700),
                              ('source', 102, 0o755), ('output', 103, 0o755)):
        O[name] = dict(identity=ident(inode, mode), acls=copy.deepcopy(ACLS))
    O['island_absent_before'] = True
    O['source_output_absent_at_packet'] = dict(source=True, output=True)
    O['packet_files'] = dict(probe=dict(device=2049, inode=105, mode=0o100400, nlink=1, uid=0, gid=0, bytes=len(D.PROBE),
                                        xattrs=[], readback_sha256=sha(D.PROBE)),
                             nested=dict(identity=ident(106, 0o700), acls=copy.deepcopy(ACLS)))
    O['sentinel'] = dict(ident(104, 0o644, 0o100000), bytes=len(A.SENTINEL), sha256=sha(A.SENTINEL))
    joins = dict(root=True, island=True, packet=True, source=True, output=True)
    O['live_joins'] = dict(joins)
    raw_acl = {'system.posix_acl_access': None, 'system.posix_acl_default': None}
    ancestors = [dict(O[k]['identity'], acl_absent=True, acl_sha256=sha(A.canonical(raw_acl)), raw_acl=dict(raw_acl))
                 for k in ('root', 'island', 'packet')]
    snap = dict(target=O['packet']['identity'], target_fd=5, fd_flags=1, sentinel=O['sentinel'], ancestors=ancestors,
                paths=['/', base, packet], mounts=['m1', 'm2', 'm3'], credentials=creds, fd_link=packet)
    O['ancestry_before'] = snap
    closing = [2049, 5000, 0o100755, 1, 72160, 1, 2, 0, 0]
    record = dict(scope=D.PROVISION_SCOPE, package=dict(D.LAUNCHER_PACKAGE), target='/usr/bin/bwrap',
                  launcher=dict(bytes=72160, sha256=A.BWRAP_SHA, opening=list(closing), closing=list(closing), mode='0755',
                                exclusive_creation=True))
    attempt = dict(argv=['/usr/bin/python3.12', '-I', '-S', '-B', EXEC_ROOT + '/' + D.SETUP['path'], '--provision-hosted-launcher'],
                   returncode=0, timeout=False, stdout=D.stream(D.encode(record)), stderr=D.stream(b''), elapsed_ns=2 * 10**9,
                   attempt=1)
    O['launcher_provision'] = dict(before='ABSENT', mode='PROVISIONED_BY_MAINTAINED_V21_SETUP', setup=dict(D.SETUP),
                                   package=dict(D.LAUNCHER_PACKAGE), attempts=[attempt], record=copy.deepcopy(record))
    O['launcher'] = dict(path='/usr/bin/bwrap', bytes=72160, sha256=A.BWRAP_SHA, mode=0o100755, uid=0, gid=0, device=2049,
                         inode=5000, nlink=1, xattrs=[], custody_stable=True, complete=True)
    O['policy_provision'] = policy_row('--provision-hosted-bwrap-policy', dict(
        scope='EPHEMERAL_CI_BWRAP_POLICY_ONLY_NO_NATIVE_ACCEPTANCE', profile_sha256=RCV.POLICY_SHA,
        loaded=copy.deepcopy(POLICY_LOADED), parser=dict(exit_code=0, stdout='', stderr=''),
        compiled_profiles={n: r['sha256'] for n, r in POLICY_LOADED.items()}, resolved_opaque_count=0,
        opaque_proofs_sha256='c' * 64, global_state_unchanged=True, receipt='/run/implementaudit-c5-bwrap-v1.json'))
    argv = A.argv('/usr/bin/bwrap', packet, 5, 'FD')
    payload = dict(schema='dg16.access08-payload.v1', route='FD', sentinel_hex=A.SENTINEL.hex(), target=O['packet']['identity'],
                   readonly_errno=30, credentials=dict(creds, user_namespace=4026532000, uid_map=[[0, 0, 1]], gid_map=[[0, 0, 1]],
                                                       fields=dict(creds['fields'], CapPrm=0, CapEff=0, CapBnd=0)))
    O['fd_route'] = dict(argv=argv, argv_sha256=sha(A.canonical(argv)), target_fd=5, diagnostic_fd_count=8, returncode=0,
                         timeout=False, stdout=D.stream(A.canonical(payload)), stderr=D.stream(b''), elapsed_ns=10**8,
                         payload_valid=True, child_limits=dict(cpu_seconds=5, address_space_bytes=268435456, core_bytes=0))
    O['ancestry_after'] = copy.deepcopy(snap)
    O['policy_final'] = policy_row('--finalize-hosted-bwrap-policy', dict(
        scope='EPHEMERAL_CI_BWRAP_POLICY_OBSERVATION_ONLY', status='ACTIVE_POLICY_AND_RECEIPT_RETAINED',
        profile_sha256=RCV.POLICY_SHA, loaded=copy.deepcopy(POLICY_LOADED), kernel_policy_unloaded=False,
        receipt_unlinked=False, retained_until='EPHEMERAL_VM_DISPOSAL', observation_limit='SNAPSHOT_ONLY_NOT_LAUNCH_EXCLUSION'))
    O['launcher_after'] = copy.deepcopy(O['launcher'])
    O['children_after'] = {'4242': []}
    O['closing'] = {k: copy.deepcopy(O[k]) for k in ('root', 'island', 'packet', 'source', 'output')}
    O['closing_joins'] = dict(joins)
    host = dict(os_release={'ID': 'ubuntu', 'VERSION_ID': '24.04'}, kernel='synthetic', machine='x86_64',
                apparmor_enabled=text('Y\n'), apparmor_restrict_unprivileged_userns=text('1\n'),
                unprivileged_userns_clone=text('1\n'), max_user_namespaces=text('63414\n'),
                bwrap_apparmor_profile=dict(readable=False, errno=2), bwrap_apparmor_extra_profile=dict(readable=False, errno=2),
                self_confinement=text('unconfined\n'), bwrap_before=dict(errno=2))
    return dict(schema=D.SCHEMA, authority='NONE', original_awards=[], cause='UNPROVED',
                scope='PLACEMENT_ONLY_FRESH_ROOT_ISLAND_FIXED_SIBLINGS_AND_FD_ROUTE', recorded_subject=copy.deepcopy(D.SUBJECT),
                modules={k: dict(v) for k, v in D.MODULES.items()}, setup=dict(D.SETUP),
                context=dict(run_id=str(RUN_ID), run_attempt=1, branch=TRIGGER, workflow_commit=HEAD),
                profile='FRESH_ROOT_ISLAND_FIXED_SIBLINGS_V1', host=host, observations=O,
                steps=[dict(step=s, result='PASS', code=None) for s in D.STEPS],
                properties={p: 'OBSERVED' for p in D.PROPERTIES}, cleanup='NONE_DISPOSABLE_RUNNER_NO_RECURSIVE_REMOVAL',
                bounds={}, status='COMPLETE', failure=None, elapsed_ns=5 * 10**9)


def partial(r, step, code='TOOL_PRECONDITION'):
    at = D.STEPS.index(step)
    for i, s in enumerate(r['steps']):
        s.update(result='PASS' if i < at else 'REFUSED' if i == at else 'NOT_ATTEMPTED', code=code if i == at else None)
    r.update(status='REFUSED', failure=code)
    r['properties'] = {p: ('OBSERVED' if p in RCV.PARTIAL else 'NOT_OBSERVED') for p in D.PROPERTIES}
    return r


def bundle(receipt, mutate_files=None, raw_receipt=None, raw_files=None, run_id=RUN_ID, conclusion='success', lines=None):
    if raw_files is not None:
        files = dict(raw_files)
    else:
        raw = raw_receipt if raw_receipt is not None else D.encode(receipt)
        files = {'RECEIPT.json': raw, 'ARTIFACT_MANIFEST.json': D.encode(dict(schema=D.MANIFEST_SCHEMA,
                 members=[dict(name='RECEIPT.json', bytes=len(raw), sha256=sha(raw))]))}
    log_files = dict(files)
    if mutate_files:
        mutate_files(files, log_files)
    transport = lines(log_files) if lines else D.transport_lines(log_files)
    log = chr(0xFEFF) + '2026-11-25T00:00:00.0000000Z ##[group]Run set -euo pipefail\n' + ''.join(
        '2026-11-25T00:00:01.0000000Z %s\n' % l for l in transport)
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w') as z:
        for n, b in files.items():
            z.writestr(n, b)
    zraw = buf.getvalue()
    run = dict(id=run_id, repository=dict(full_name='theislampill/IMPLEMENTAUDIT.md'), event='push', head_branch=TRIGGER,
               head_sha=HEAD, run_attempt=1, path='.github/workflows/dg16-placement-diagnostic.yml', status='completed',
               conclusion=conclusion)
    runs = dict(total_count=1, workflow_runs=[dict(id=run_id, head_sha=HEAD)])
    jobs = dict(total_count=1, jobs=[dict(id=7, run_id=run_id, head_sha=HEAD, run_attempt=1, name='observe', conclusion=conclusion,
                                         labels=['ubuntu-24.04'], runner_group_name='GitHub Actions', status='completed')])
    arts = dict(total_count=1, artifacts=[dict(id=9, name='dg16-placement-diag-%d-a1' % run_id, expired=False,
                                               digest='sha256:' + sha(zraw), workflow_run=dict(id=run_id, head_sha=HEAD))])
    return dict(commit=HEAD, repo=str(REPO), runs=runs, run=run, jobs=jobs, artifacts=arts, log_text=log, artifact_zip=zraw)


class Receiver(unittest.TestCase):
    def refused(self, inputs, code):
        with self.assertRaises(RCV.Refused) as ctx:
            RCV.receive(**inputs)
        self.assertEqual(ctx.exception.args[0], code)

    def derive(self, r):
        return RCV.derive(r, RCV.pinned_access_matrix(str(REPO), HEAD))

    def test_synthetic_complete_is_received(self):
        result = RCV.receive(**bundle(synthetic()))
        self.assertEqual((result['status'], result['authority'], result['substitutable_for_full'], result['launcher_mode'],
                          result['replaces']),
                         ('RECEIVED_AT_DIAGNOSTIC_SCOPE', 'NONE', True, 'PROVISIONED_BY_MAINTAINED_V21_SETUP',
                          'NOTHING_WITHOUT_NEW_ROOT_COMPOSITION'))
        self.assertGreater(sum(1 for l in bundle(synthetic())['log_text'].splitlines() if ' RECEIPT.json ' in l), 3)

    def test_declared_502_retry_is_received(self):
        r = synthetic()
        lp = r['observations']['launcher_provision']
        first = dict(lp['attempts'][0], attempt=1, returncode=1, stdout=D.stream(b''), retry_eligible=True,
                     stderr=D.stream(b'Traceback\n' + D.RETRY_LINE + b'\n'))
        lp['attempts'] = [first, dict(lp['attempts'][0], attempt=2)]
        self.assertTrue(self.derive(r)['P5_FD_ROUTE'])
        self.assertEqual(RCV.receive(**bundle(r))['status'], 'RECEIVED_AT_DIAGNOSTIC_SCOPE')
        for bad in (dict(first, stderr=D.stream(b'urllib.error.URLError: x\n')), dict(first, retry_eligible=False),
                    dict(first, returncode=0)):
            r2 = copy.deepcopy(r); r2['observations']['launcher_provision']['attempts'][0] = bad
            self.assertFalse(self.derive(r2)['P5_FD_ROUTE'])
        r3 = copy.deepcopy(r); r3['observations']['launcher_provision']['attempts'].append(dict(lp['attempts'][1], attempt=3))
        self.assertFalse(self.derive(r3)['P5_FD_ROUTE'])

    def test_source_refusals(self):
        b = bundle(synthetic()); b['commit'] = RCV.SUBJECT[0]
        self.refused(b, 'COMMIT_PARENT_NOT_SUBJECT')
        b = bundle(synthetic()); b['commit'] = 'f' * 40
        self.refused(b, 'GIT_REV_LIST')

    def test_run_job_artifact_refusals(self):
        for path, value, code in ((('run', 'run_attempt'), 2, 'RUN_IDENTITY'), (('run', 'head_branch'), 'main', 'RUN_IDENTITY'),
                                  (('run', 'event'), 'workflow_dispatch', 'RUN_IDENTITY'),
                                  (('run', 'head_sha'), '0' * 40, 'RUN_IDENTITY'),
                                  (('run', 'conclusion'), 'failure', 'RUN_CONCLUSION'),
                                  (('runs', 'total_count'), 2, 'WORKFLOW_RUN_POPULATION')):
            b = bundle(synthetic()); b[path[0]][path[1]] = value
            self.refused(b, code)
        b = bundle(synthetic()); b['runs']['workflow_runs'][0]['id'] = 1
        self.refused(b, 'WORKFLOW_RUN_POPULATION')
        b = bundle(synthetic()); b['runs']['workflow_runs'][0]['head_sha'] = '0' * 40
        self.refused(b, 'WORKFLOW_RUN_POPULATION')
        b = bundle(synthetic()); b['jobs']['jobs'][0]['labels'] = ['self-hosted']
        self.refused(b, 'JOB_IDENTITY')
        b = bundle(synthetic()); b['jobs']['jobs'][0]['conclusion'] = 'cancelled'
        self.refused(b, 'JOB_CONCLUSION')
        b = bundle(synthetic()); b['jobs']['jobs'].append(dict(b['jobs']['jobs'][0])); b['jobs']['total_count'] = 2
        self.refused(b, 'EXACTLY_ONE_JOB')
        b = bundle(synthetic()); b['artifacts'] = dict(total_count=0, artifacts=[])
        self.refused(b, 'ARTIFACT_IDENTITY')
        b = bundle(synthetic()); b['artifacts']['artifacts'][0]['digest'] = 'sha256:' + '0' * 64
        self.refused(b, 'ARTIFACT_ZIP_DIGEST')

    def test_transport_refusals(self):
        def drop(files, log):
            del files['ARTIFACT_MANIFEST.json']
        self.refused(bundle(synthetic(), drop), 'ARTIFACT_POPULATION')
        def log_only(files, log):
            log['RECEIPT.json'] = log['RECEIPT.json'].replace(b'"COMPLETE"', b'"COMPLETF"')
        self.refused(bundle(synthetic(), log_only), 'LOG_ARTIFACT_BYTES_DIFFER')
        def manifest(files, log):
            m = RCV.parse(files['ARTIFACT_MANIFEST.json']); m['members'][0]['sha256'] = '0' * 64
            files['ARTIFACT_MANIFEST.json'] = log['ARTIFACT_MANIFEST.json'] = D.encode(m)
        self.refused(bundle(synthetic(), manifest), 'MANIFEST_BINDING')
        good = D.transport_lines
        def edit(fn):
            return lambda f: fn(good(f))
        cases = (
            (lambda ls: [l for l in ls if not l.startswith(D.MARKER + '_COUNT RECEIPT.json')], 'LOG_COUNT_LINE'),
            (lambda ls: [ls[0], ls[2], ls[1]] + ls[3:], 'LOG_CHUNK_SEQUENCE'),
            (lambda ls: ls[:2] + ls[3:], 'LOG_CHUNK_SEQUENCE'),
            (lambda ls: ls + ls[-2:], 'LOG_COUNT_LINE'),
            (lambda ls: [ls[0].replace(ls[0].split(' ')[4], '0' * 64)] + ls[1:], 'LOG_MEMBER_BINDING'),
            (lambda ls: [ls[0].replace(' %s ' % ls[0].split(' ')[2], ' 99 ', 1)] + ls[1:], 'LOG_CHUNKS_INCOMPLETE'),
            (lambda ls: [ls[0]] + [ls[1] + 'AAAA'] + ls[2:], 'LOG_CHUNK_SEQUENCE'),
            (lambda ls: [l for l in ls if 'ARTIFACT_MANIFEST' not in l], 'LOG_MEMBERS_INCOMPLETE'))
        for fn, code in cases:
            self.refused(bundle(synthetic(), lines=edit(fn)), code)
        raw = json.dumps(synthetic(), indent=1).encode() + b'\n'
        self.refused(bundle(None, raw_receipt=raw), 'RECEIPT_NOT_CANONICAL')
        raw = D.encode(synthetic())[:-2] + b',"status":"COMPLETE"}\n'
        self.refused(bundle(None, raw_receipt=raw), 'RECEIPT_DUPLICATE_KEY')

    def test_field_refusals(self):
        def m(fn, code, **kw):
            r = synthetic(); fn(r); self.refused(bundle(r, **kw), code)
        m(lambda r: r.update(status='INCOMPLETE'), 'RECEIPT_NOT_COMPLETE', conclusion='failure')
        m(lambda r: r['steps'][5].update(result='REFUSED'), 'RECEIPT_NOT_COMPLETE')
        m(lambda r: r['steps'].pop(), 'RECEIPT_STEP_POPULATION')
        m(lambda r: r['context'].update(run_id='1'), 'RECEIPT_CONTEXT')
        m(lambda r: r['context'].update(workflow_commit=RCV.SUBJECT[0]), 'RECEIPT_CONTEXT')
        m(lambda r: r['recorded_subject'].update(tree='0' * 40), 'RECEIPT_SUBJECT')
        m(lambda r: r.update(original_awards=['G1']), 'RECEIPT_SCOPE')
        m(lambda r: r['modules']['access_matrix'].update(sha256='0' * 64), 'RECEIPT_MODULE_PINS')
        m(lambda r: r['setup'].update(sha256='0' * 64), 'RECEIPT_SETUP_PIN')
        m(lambda r: r['host'].update(os_release={'ID': 'ubuntu', 'VERSION_ID': '22.04'}), 'HOST_IMAGE')
        m(lambda r: r.update(elapsed_ns=301 * 10**9), 'RECEIPT_ELAPSED_BOUND')
        m(lambda r: r['properties'].update(P4_FIXED_SIBLINGS='NOT_OBSERVED'), 'OPERATOR_VERDICT_DISAGREES')
        m(lambda r: r['observations']['exec']['files'][D.EXEC_FILES[0]].update(mode=0o100444), 'EXEC_CUSTODY_NOT_REDERIVED')
        m(lambda r: r['observations']['exec']['files'][D.EXEC_FILES[3]].update(sha256='0' * 64), 'EXEC_CUSTODY_NOT_REDERIVED')
        m(lambda r: r['observations']['exec'].update(root='/tmp/elsewhere'), 'EXEC_CUSTODY_NOT_REDERIVED')
        m(lambda r: r['observations']['exec']['directories']['scripts'].update(mode=0o040755), 'EXEC_CUSTODY_NOT_REDERIVED')
        m(lambda r: r['observations']['exec']['parent'].update(mode=0o041777), 'EXEC_CUSTODY_NOT_REDERIVED')
        m(lambda r: r['observations']['exec']['parent'].update(uid=1001), 'EXEC_CUSTODY_NOT_REDERIVED')
        m(lambda r: r['observations']['exec'].update(root='/home/runner/work/_temp/dg16-placement-exec-%d-a1' % RUN_ID),
          'EXEC_CUSTODY_NOT_REDERIVED')

    def test_property_rederivation_refusals(self):
        O = lambda r: r['observations']
        H = lambda r: r['host']
        cases = (
            ('P1_ROOT_CREDENTIALS', lambda r: O(r).update(credentials=[1000, 0, 0, 0])),
            ('P2_ROOT_ANCESTOR_CUSTODY', lambda r: O(r)['root']['identity'].update(mode=0o040777)),
            ('P3_EXCLUSIVE_FRESH_ISLAND', lambda r: O(r).update(island_absent_before=False)),
            ('P3_EXCLUSIVE_FRESH_ISLAND', lambda r: O(r)['island']['acls'][0].update(result='PRESENT')),
            ('P3_EXCLUSIVE_FRESH_ISLAND', lambda r: O(r)['island']['identity'].update(device=7)),
            ('P4_FIXED_SIBLINGS', lambda r: O(r)['source']['identity'].update(uid=1000)),
            ('P4_FIXED_SIBLINGS', lambda r: O(r)['output']['identity'].update(mode=0o040777)),
            ('P4_FIXED_SIBLINGS', lambda r: O(r)['packet']['identity'].update(mode=0o040755)),
            ('P4_FIXED_SIBLINGS', lambda r: O(r)['source_output_absent_at_packet'].update(output=False)),
            ('P4_FIXED_SIBLINGS', lambda r: O(r)['live_joins'].update(packet=False)),
            ('P4_FIXED_SIBLINGS', lambda r: O(r)['packet_files']['probe'].update(mode=0o100600)),
            ('P4_FIXED_SIBLINGS', lambda r: O(r)['packet_files']['probe'].update(nlink=2)),
            ('P4_FIXED_SIBLINGS', lambda r: O(r)['packet_files']['probe'].update(xattrs=['user.x'])),
            ('P4_FIXED_SIBLINGS', lambda r: O(r)['packet_files']['probe'].update(readback_sha256='0' * 64)),
            ('P4_FIXED_SIBLINGS', lambda r: O(r)['packet_files']['nested']['identity'].update(mode=0o040755)),
            ('P5_FD_ROUTE', lambda r: O(r)['launcher'].update(sha256='e' * 64)),
            ('P5_FD_ROUTE', lambda r: O(r)['launcher'].update(nlink=2)),
            ('P5_FD_ROUTE', lambda r: O(r)['fd_route'].update(returncode=1)),
            ('P5_FD_ROUTE', lambda r: O(r)['fd_route'].update(stderr=D.stream(b'Permission denied'))),
            ('P5_FD_ROUTE', lambda r: O(r)['fd_route'].update(argv=O(r)['fd_route']['argv'] + ['--extra'])),
            ('P5_FD_ROUTE', lambda r: O(r)['fd_route'].update(argv_sha256='0' * 64)),
            ('P5_FD_ROUTE', lambda r: O(r)['fd_route'].update(child_limits={})),
            ('P5_FD_ROUTE', lambda r: O(r)['fd_route']['stdout'].update(sha256='0' * 64)),
            ('P5_FD_ROUTE', lambda r: O(r)['launcher_provision']['attempts'][0].update(returncode=1)),
            ('P5_FD_ROUTE', lambda r: O(r)['launcher_provision'].update(before={'uid': 0})),
            ('P5_FD_ROUTE', lambda r: O(r)['launcher_provision']['record']['package'].update(sha256='0' * 64)),
            ('P5_FD_ROUTE', lambda r: O(r)['launcher_provision']['record']['launcher']['closing'].__setitem__(1, 1)),
            ('P5_FD_ROUTE', lambda r: O(r)['launcher_provision']['attempts'][0].update(stderr=D.stream(b'urllib.error'))),
            ('P5_FD_ROUTE', lambda r: O(r)['launcher_provision']['attempts'][0]['argv'].__setitem__(4, '/tmp/x.py')),
            ('P5_FD_ROUTE', lambda r: O(r)['launcher_provision'].update(mode='PREEXISTING_NOT_PROVISIONED', record=None, attempts=[],
                before=dict(device=2049, inode=5000, mode=0o100755, uid=1000, gid=0, bytes=72160))),
            ('P5_FD_ROUTE', lambda r: H(r).update(apparmor_restrict_unprivileged_userns=text('0\n'))),
            ('P5_FD_ROUTE', lambda r: H(r).update(bwrap_apparmor_profile=text('profile\n'))),
            ('P5_FD_ROUTE', lambda r: H(r).update(apparmor_enabled=text('N\n'))),
            ('P5_FD_ROUTE', lambda r: H(r).update(unprivileged_userns_clone=text('0\n'))),
            ('P5_FD_ROUTE', lambda r: H(r).update(bwrap_apparmor_extra_profile=text('x\n'))),
            ('P5_FD_ROUTE', lambda r: O(r)['policy_provision'].update(returncode=1)),
            ('P5_FD_ROUTE', lambda r: O(r)['policy_provision']['argv'].__setitem__(1, 'X=1')),
            ('P5_FD_ROUTE', lambda r: O(r)['policy_provision']['record'].update(profile_sha256='0' * 64)),
            ('P5_FD_ROUTE', lambda r: O(r)['policy_provision']['record']['loaded'][RCV.POLICY_NAMES[0]].update(mode='complain')),
            ('P6_ANCESTRY_NO_DRIFT', lambda r: O(r)['ancestry_after']['ancestors'][0].update(inode=3)),
            ('P6_ANCESTRY_NO_DRIFT', lambda r: O(r)['ancestry_before'].update(fd_link='/elsewhere')),
            ('P7_CLOSING_CURRENTNESS', lambda r: O(r)['closing']['output']['identity'].update(inode=999)),
            ('P7_CLOSING_CURRENTNESS', lambda r: O(r)['closing_joins'].update(root=False)),
            ('P7_CLOSING_CURRENTNESS', lambda r: O(r)['launcher_after'].update(inode=1)),
            ('P7_CLOSING_CURRENTNESS', lambda r: O(r).update(children_after={'4242': ['4300']})),
            ('P7_CLOSING_CURRENTNESS', lambda r: O(r)['policy_final']['record'].update(status='NO_OWNED_POLICY_OBSERVED')),
        )
        for prop, fn in cases:
            r = synthetic(); fn(r)
            for row in ('policy_provision', 'policy_final'):  # keep stream and record consistent where only the record moved
                rec = r['observations'][row]
                if rec['record'] != json.loads(base64.b64decode(rec['stdout']['base64'])):
                    rec['stdout'] = D.stream((json.dumps(rec['record'], sort_keys=True) + '\n').encode(), D.POLICY_STREAM_BYTES)
            got = self.derive(r)
            self.assertFalse(got[prop], prop)
            self.refused(bundle(r), 'PROPERTY_NOT_REDERIVED_' + ','.join(k for k, v in got.items() if not v))
        r = synthetic(); r['host']['self_confinement'] = text('docker-default (enforce)\n')  # recorded only
        self.assertTrue(all(self.derive(r).values()))
        r = synthetic()  # live phase: no mode requirement for source/output
        for o in (r['observations']['source'], r['observations']['closing']['source']):
            o['identity']['mode'] = 0o040700
        self.assertTrue(all(self.derive(r).values()))

    def test_payload_property_refusals(self):
        def payload(fn):
            r = synthetic(); route = r['observations']['fd_route']
            p = json.loads(base64.b64decode(route['stdout']['base64'])); fn(p)
            route['stdout'] = D.stream(A.canonical(p))
            return r
        for fn in (lambda p: p['credentials']['fields'].update(CapEff=1),
                   lambda p: p['credentials'].update(user_namespace=4026531837),
                   lambda p: p['credentials'].update(uid_map=[[0, 1000, 1]]),
                   lambda p: p['credentials'].update(gid_map=[[0, 0, 4294967295]]),
                   lambda p: p.update(readonly_errno=13), lambda p: p['target'].update(inode=1),
                   lambda p: p.update(route='PATH')):
            self.assertFalse(self.derive(payload(fn))['P5_FD_ROUTE'])

    def test_partial_receiving(self):
        for step in RCV.PARTIAL_STEPS:
            r = partial(synthetic(), step)
            got = RCV.receive(**bundle(r, conclusion='failure'))
            self.assertEqual((got['status'], got['substitutable_for_full'], got['failed_step'], got['launcher_mode']),
                             ('RECEIVED_PARTIAL_P1_P4', False, step, 'PROVISIONED_BY_MAINTAINED_V21_SETUP'))
            self.assertEqual(got['properties'], {k: ('REDERIVED' if k in RCV.PARTIAL else 'NOT_RECEIVED') for k in RCV.PROPERTIES})
        r = partial(synthetic(), 'TOOL_PIN')
        r['observations']['launcher_provision'].update(mode='PREEXISTING_NOT_PROVISIONED', record=None, attempts=[],
                                                      before=dict(device=2049, inode=6000, mode=0o100755, uid=0, gid=0, bytes=72160))
        r['observations']['launcher'].update(sha256='e3189038' + '0' * 56)
        self.assertEqual(RCV.receive(**bundle(r, conclusion='failure'))['launcher_mode'], 'PREEXISTING_NOT_PROVISIONED')
        self.refused(bundle(partial(synthetic(), 'TOOL_PIN'), conclusion='success'), 'RUN_CONCLUSION')
        for step in ('ANCESTRY_AFTER', 'CLOSING_CURRENT', 'LIVE_CURRENT', 'CREDENTIALS'):
            self.refused(bundle(partial(synthetic(), step), conclusion='failure'), 'PARTIAL_NOT_ELIGIBLE')
        r = partial(synthetic(), 'FD_ROUTE'); r['steps'][-1]['result'] = 'PASS'
        self.refused(bundle(r, conclusion='failure'), 'PARTIAL_NOT_ELIGIBLE')
        r = partial(synthetic(), 'FD_ROUTE'); r['steps'][D.STEPS.index('FD_ROUTE')]['code'] = 'OTHER'
        self.refused(bundle(r, conclusion='failure'), 'PARTIAL_NOT_ELIGIBLE')
        r = partial(synthetic(), 'FD_ROUTE'); r['observations']['source']['identity']['uid'] = 1000
        self.refused(bundle(r, conclusion='failure'), 'PROPERTY_NOT_REDERIVED_P4_FIXED_SIBLINGS')
        r = partial(synthetic(), 'FD_ROUTE'); r['properties']['P5_FD_ROUTE'] = 'OBSERVED'
        self.refused(bundle(r, conclusion='failure'), 'OPERATOR_VERDICT_DISAGREES')
        r = partial(synthetic(), 'FD_ROUTE'); r['observations']['exec']['files'][D.EXEC_FILES[0]]['mode'] = 0o100644
        self.refused(bundle(r, conclusion='failure'), 'EXEC_CUSTODY_NOT_REDERIVED')

    def test_cli_rc_and_refusal_shape(self):
        done = subprocess.run([sys.executable, '-I', '-B', str(HERE / 'receive.py'), '--commit', HEAD],
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.assertEqual(done.returncode, 1)
        out = json.loads(done.stdout)
        self.assertEqual((out['code'], out['replaces']), ('USAGE', 'NOTHING_WITHOUT_NEW_ROOT_COMPOSITION'))
        with tempfile.TemporaryDirectory() as tmp:
            for label, conclusion, r, rc in (('full', 'success', synthetic(), 0),
                                             ('partial', 'failure', partial(synthetic(), 'TOOL_PIN'), 3)):
                b = bundle(r, conclusion=conclusion)
                paths = {}
                for key in ('runs', 'run', 'jobs', 'artifacts'):
                    paths[key] = Path(tmp) / (label + key + '.json'); paths[key].write_bytes(json.dumps(b[key]).encode())
                (Path(tmp) / (label + '.log')).write_text(b['log_text'], encoding='utf-8')
                (Path(tmp) / (label + '.zip')).write_bytes(b['artifact_zip'])
                done = subprocess.run([sys.executable, '-I', '-B', str(HERE / 'receive.py'), '--commit', HEAD, '--repo', str(REPO),
                                       '--runs', str(paths['runs']), '--run', str(paths['run']), '--jobs', str(paths['jobs']),
                                       '--artifacts', str(paths['artifacts']), '--log', str(Path(tmp) / (label + '.log')),
                                       '--artifact-zip', str(Path(tmp) / (label + '.zip'))], stdout=subprocess.PIPE)
                self.assertEqual(done.returncode, rc, done.stdout)


class Workflow(unittest.TestCase):
    def setUp(self):
        try:
            import yaml
        except ImportError:
            self.skipTest('PyYAML unavailable')
        self.raw = WORKFLOW.read_bytes()
        self.w = yaml.safe_load(self.raw)

    def test_trigger_is_one_exact_branch(self):
        w = self.w
        self.assertEqual(set(w), {'name', 'on', 'permissions', 'concurrency', 'jobs'})
        self.assertEqual(w['on'], {'push': {'branches': [TRIGGER]}})
        self.assertIsNone(re.search(r'[*?+\[\]!]', TRIGGER))
        self.assertEqual(list(w['jobs']), ['observe'])
        job = w['jobs']['observe']
        for clause in ("github.repository == 'theislampill/IMPLEMENTAUDIT.md'", "github.event_name == 'push'",
                       "github.ref == 'refs/heads/" + TRIGGER + "'", 'github.event.deleted == false',
                       "github.run_attempt == '1'"):
            self.assertIn(clause, job['if'])
        self.assertEqual(job['if'].count('&&'), 4)
        self.assertNotIn('||', job['if'])

    def test_bounds_and_permissions(self):
        w, text_ = self.w, self.raw.decode()
        job = w['jobs']['observe']
        self.assertEqual(w['permissions'], {'contents': 'read'})
        self.assertEqual(job['runs-on'], 'ubuntu-24.04')
        self.assertLessEqual(job['timeout-minutes'], 10)
        for word in ('secrets.', 'continue-on-error', 'workflow_dispatch:', 'schedule:', 'pull_request:', 'tags:'):
            self.assertNotIn(word, text_)
        self.assertNotIn('strategy', job)
        uses = [s['uses'] for s in job['steps'] if 'uses' in s]
        self.assertEqual(uses, ['actions/checkout@11d5960a326750d5838078e36cf38b85af677262',
                                'actions/upload-artifact@ea165f8d65b6e75b540449e92b4886f43607fa02'])
        checkout = job['steps'][0]['with']
        self.assertIs(checkout['persist-credentials'], False)
        self.assertEqual(checkout['ref'], '${{ github.sha }}')
        upload = job['steps'][-1]
        self.assertEqual((upload['if'], upload['with']['if-no-files-found'], upload['with']['retention-days']), ('always()', 'error', 30))

    def test_exec_copy_staging(self):
        run = self.w['jobs']['observe']['steps'][2]['run']
        self.assertIn('/usr/bin/mkdir -m 0700 "$x"', run)
        self.assertIn('exec_root="/run/dg16-placement-exec-$GITHUB_RUN_ID-a1"', run)
        self.assertIn('test "$(/usr/bin/stat -c %u:%g /run)" = 0:0', run)
        self.assertIn('test $(( 0$(/usr/bin/stat -c %a /run) & 022 )) -eq 0', run)
        self.assertNotIn('RUNNER_TEMP/dg16-placement-diag-exec', run)
        self.assertIn('/usr/bin/install -m 0400 -o root -g root "$src/$f" "$x/$f"', run)
        self.assertIn('umask 077', run)
        self.assertIn('/usr/bin/python3.12 -I -S -B "$exec_root/qualification/dg16-placement-diagnostic/diagnose.py"', run)
        self.assertNotIn('$GITHUB_WORKSPACE/packet/qualification/dg16-placement-diagnostic/diagnose.py', run)
        self.assertEqual(run.count('| /usr/bin/sha256sum --check --strict'), 1)

    def test_pins_match_actual_bytes(self):
        text_ = self.raw.decode()
        for name in ('diagnose.py', 'root_placement.py', 'access_matrix.py'):
            digest = sha((HERE / name).read_bytes())
            self.assertIn(digest + '  qualification/dg16-placement-diagnostic/' + name, text_)
            self.assertEqual(text_.count(digest), 2, name)
            self.assertEqual(RCV.PINS['qualification/dg16-placement-diagnostic/' + name], digest)
        self.assertEqual(text_.count(RCV.SETUP['sha256']), 2)
        setup = (REPO / RCV.SETUP['path']).read_bytes()
        self.assertEqual((len(setup), sha(setup)), (RCV.SETUP['bytes'], RCV.SETUP['sha256']))
        self.assertEqual(RCV.PINS['.github/workflows/dg16-placement-diagnostic.yml'], sha(self.raw))
        proposal = json.loads((HERE / 'PROPOSAL.json').read_bytes())
        for path, row in proposal['files'].items():
            raw = (REPO / path).read_bytes()
            self.assertEqual(row, dict(bytes=len(raw), sha256=sha(raw)), path)

    def test_proposal_declarations(self):
        p = json.loads((HERE / 'PROPOSAL.json').read_bytes())
        effects = ' '.join(p['effects'])
        for word in ('$RUNNER_TEMP', 'upload', 'AppArmor', 'root-owned 0700', 'HTTP 502', '/run/dg16-placement-exec-RUN-a1'):
            self.assertIn(word, effects)
        self.assertNotIn('RUNNER_TEMP/dg16-placement-diag-exec', effects)
        cites = ' '.join(p['host_expectations'].values())
        for cite in ('run.py:585', 'setup:581', 'setup:582', 'setup:583', 'setup:584', 'setup:1086', 'setup:1167'):
            self.assertIn(cite, cites)
        self.assertTrue(any('host_utility.py:707-877' in q for q in p['open_questions']))
        self.assertIn('30', p['receiving']['retention'])
        self.assertEqual(p['receiving']['replaces'], 'NOTHING_WITHOUT_NEW_ROOT_COMPOSITION')
        self.assertEqual(p['launcher']['retry'], 'ONE_RETRY_ONLY_ON_FINAL_LINE_HTTP_502_WHILE_TARGET_ABSENT_BEFORE_ANY_WRITE')

    def test_head_commit_shape(self):
        message = subprocess.run(['git', '-C', str(REPO), 'log', '-1', '--format=%B'], stdout=subprocess.PIPE,
                                 check=True).stdout.decode().lower()
        for marker in ('[skip ci]', '[ci skip]', '[no ci]', '[skip actions]', '[actions skip]', 'skip-checks'):
            self.assertNotIn(marker, message)
        self.assertEqual(RCV.check_source(str(REPO), HEAD), {p: RCV.PINS[p] for p in sorted(RCV.PINS)})


if __name__ == '__main__':
    unittest.main(verbosity=2)
