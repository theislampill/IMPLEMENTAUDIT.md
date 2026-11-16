#!/usr/bin/env python3
"""Consume the retained DG18 packages through their four existing install routes.

Only fresh disposable task/currentness operations are performed. The existing
installers and claim owner make every installed-runtime decision. No package is
rebuilt, no host/model occurrence is asserted, and no accepting C02 or W-FULL
operation is called. STATE and ROADMAP reads are separate workflow steps.
"""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import signal
import stat
import subprocess
import sys
import time
import zipfile

SOURCE_HEAD = '6b353b48b2fc8a6de0c6223f48d341c484c98191'
SOURCE_TREE = '92da6bf5f9d2d8d7ea723b56f2e99c838a9d984b'
BRANCH = 'refs/heads/engineering/pro-dg18-installed-current-20261115'
TRANSPORT = 'handoff/pro-executor-results-20261115/dg18-installed-current/current-6b353b48/COMPLETED_EVIDENCE.zip'
TRANSPORT_BYTES = 1175365
TRANSPORT_SHA = '50eb80487eecd1db96d949e43e66e92b4795258853de60ba91521b39dec3be44'
ARCHIVES = {
    'canonical_plugin': ('IMPLEMENTAUDIT.plugin.zip', 586944, '25e7ec53d297d72bc8f8b2c903822b1865cbea9c1e7d6074c1213812d285593f'),
    'standalone_compatibility': ('IMPLEMENTAUDIT.skill', 582354, '5d906967287941a515d0053c611d2f0f689c5933efdbe0affeac163f77e2c5b3'),
}
ROUTES = ('plugin-codex', 'plugin-claude', 'standalone-codex', 'standalone-claude')
ENV = {'PATH': '/usr/bin:/bin', 'LANG': 'C.UTF-8', 'LC_ALL': 'C.UTF-8',
       'PYTHONDONTWRITEBYTECODE': '1', 'IMPLEMENTAUDIT_PYTHON': '/usr/bin/python3',
       'GIT_CONFIG_NOSYSTEM': '1', 'GIT_CONFIG_GLOBAL': '/dev/null'}


def require(value, reason):
    if not value:
        raise RuntimeError(reason)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def save(path, value):
    raw = value if isinstance(value, bytes) else (json.dumps(value, sort_keys=True, indent=2) + '\n').encode()
    with path.open('xb') as stream:
        stream.write(raw)


def fact(path):
    before = path.lstat()
    require(stat.S_ISREG(before.st_mode), 'nonregular evidence member')
    raw = path.read_bytes()
    after = path.lstat()
    require((before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns, before.st_ctime_ns) ==
            (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns, after.st_ctime_ns),
            'member changed during read')
    return {'bytes': len(raw), 'sha256': digest(raw), 'mode': stat.S_IMODE(before.st_mode)}


def population(root):
    rows = {}
    for path in sorted(root.rglob('*')):
        require(not path.is_symlink(), 'aliased population member')
        if path.is_file():
            rows[path.relative_to(root).as_posix()] = fact(path)
    return rows


def host_context():
    require(sys.platform == 'linux' and os.name == 'posix', 'Linux source qualification required')
    require(os.environ.get('GITHUB_REPOSITORY') == 'theislampill/IMPLEMENTAUDIT.md'
            and os.environ.get('GITHUB_REF') == BRANCH
            and os.environ.get('GITHUB_EVENT_NAME') == 'push'
            and os.environ.get('GITHUB_RUN_ATTEMPT') == '1', 'unbound hosted source qualification')
    run = os.environ.get('GITHUB_RUN_ID', '')
    require(run.isdigit(), 'missing actual run identity')
    tools = {}
    for name in ('python3', 'bash', 'git'):
        path = (Path('/usr/bin') / name).resolve(strict=True)
        for member in (path, *path.parents):
            item = member.stat()
            require(item.st_uid == 0 and not item.st_mode & 0o022, 'existing tool-custody predicate unavailable')
        tools[name] = {'path': str(path), **fact(path)}
    require(Path(sys.executable).resolve() == Path(tools['python3']['path']), 'use the actual system Python')
    return {'repository': os.environ['GITHUB_REPOSITORY'], 'branch': BRANCH,
            'run_id': run, 'attempt': '1', 'workflow_commit': os.environ['GITHUB_SHA'],
            'python_version': list(sys.version_info[:3]), 'tools': tools,
            'scope': 'ORDINARY_INSTALLED_SOURCE_CONSUMERS_ONLY'}


class Operation:
    def __init__(self, source, packet, output, host):
        self.source, self.packet, self.output, self.host = source, packet, output, host
        self.evidence = output / 'evidence'
        self.packages = output / 'packages'

    def run(self, label, argv, cwd=None):
        argv = [str(value) for value in argv]
        stdout, stderr = (self.evidence / (label + suffix) for suffix in ('.stdout.txt', '.stderr.txt'))
        start, timeout = time.monotonic(), False
        with stdout.open('xb') as out, stderr.open('xb') as err:
            child = subprocess.Popen(argv, cwd=cwd or self.source, env=ENV,
                stdin=subprocess.DEVNULL, stdout=out, stderr=err, start_new_session=True)
            try:
                code = child.wait(timeout=120)
            except subprocess.TimeoutExpired:
                timeout = True
                os.killpg(child.pid, signal.SIGKILL)
                code = child.wait()
        save(self.evidence / (label + '.json'), {'argv': argv, 'cwd': str(cwd or self.source),
             'exit_code': code, 'timeout': timeout, 'elapsed_seconds': time.monotonic() - start,
             'stdout': fact(stdout), 'stderr': fact(stderr),
             'timeout_descendant_termination': 'UNVERIFIED' if timeout else 'NOT_TRIGGERED'})
        require(not timeout and code == 0, 'operation refused: ' + label)
        require(stdout.stat().st_size <= 2 * 1024 * 1024, 'unexpected output volume')
        return stdout.read_bytes()

    def source_identity(self, label):
        values = self.run(label, ['/usr/bin/git', 'rev-parse', 'HEAD', 'HEAD^{tree}']).decode().splitlines()
        require(values == [SOURCE_HEAD, SOURCE_TREE], 'source identity differs')
        require(self.run(label + '-clean', ['/usr/bin/git', 'status', '--porcelain=v1',
                    '--untracked-files=all']) == b'', 'source checkout is dirty')
        return {'commit': SOURCE_HEAD, 'tree': SOURCE_TREE, 'worktree_state': 'clean'}

    def paths(self, route):
        base = self.output / route
        installed = base / ('host/plugins/implementaudit' if route.startswith('plugin-') else 'host/skills/implementaudit')
        skill = installed / 'skills/implementaudit' if route.startswith('plugin-') else installed
        return base, base / 'subject', installed, skill

    def owner(self, route, label, *arguments):
        _, subject, _, skill = self.paths(route)
        return self.run(route + '-' + label, ['/usr/bin/bash', skill / 'scripts/claim-run.sh', *arguments], subject).decode().strip()

    def parity(self, route):
        _, _, installed, _ = self.paths(route)
        role = 'canonical_plugin' if route.startswith('plugin-') else 'standalone_compatibility'
        expected = {}
        with zipfile.ZipFile(self.packages / ARCHIVES[role][0]) as archive:
            for item in archive.infolist():
                raw = archive.read(item)
                expected[item.filename] = {'bytes': len(raw), 'sha256': digest(raw), 'mode': (item.external_attr >> 16) & 0o777}
        require(population(installed) == expected, 'installed archive parity differs: ' + route)
        return expected

    def prepare(self):
        self.output.mkdir(mode=0o700)
        self.evidence.mkdir(mode=0o700)
        self.packages.mkdir(mode=0o700)
        save(self.evidence / 'HOST.json', self.host)
        source = self.source_identity('source-before')
        transport = self.packet / TRANSPORT
        require(transport.stat().st_size == TRANSPORT_BYTES and digest(transport.read_bytes()) == TRANSPORT_SHA,
                'retained transport differs')
        with zipfile.ZipFile(transport) as archive:
            require(len(archive.namelist()) == 6 and len(set(archive.namelist())) == 6, 'retained transport population differs')
            for role, (name, size, sha) in ARCHIVES.items():
                raw = archive.read('packages/published-6b353b48/' + name)
                require(len(raw) == size and digest(raw) == sha and 589824 - size >= 2000, 'original archive identity or reserve differs')
                save(self.packages / name, raw)
                self.run('verify-' + role, ['/usr/bin/python3', '-I', '-B', self.source / 'scripts/package-contract.py',
                    '--verify-artifact', role, self.packages / name, '--require-clean-source'])
        save(self.packages / 'CHECKSUMS.txt', ''.join('sha256 ' + row[2] + ' ' + row[0] + '\n' for row in ARCHIVES.values()).encode())
        save(self.evidence / 'PACKAGES.json', {'source': source, 'artifacts': population(self.packages),
             'transport_sha256': TRANSPORT_SHA, 'original_cap_bytes': 589824, 'original_reserve_bytes': 2000,
             'rebuilt': False, 'native_discovery': False})
        for route in ROUTES:
            base, subject, installed, skill = self.paths(route)
            base.mkdir(mode=0o700)
            host = base / 'host'
            host.mkdir(mode=0o700)
            checksum = ['--checksum', self.packages / 'CHECKSUMS.txt']
            if route.startswith('plugin-'):
                (host / '.implementaudit-isolated-host-root').write_text('Actual disposable DG18 package consumer\n')
                installer = ['install-plugin-from-release.sh', '--asset', self.packages / ARCHIVES['canonical_plugin'][0],
                             *checksum, '--host', route.split('-')[1], '--host-root', host]
            else:
                installer = ['install-' + route.split('-')[1] + '-from-release.sh', '--asset',
                    self.packages / ARCHIVES['standalone_compatibility'][0], *checksum]
                installer += ['--codex-home', host] if route.endswith('codex') else ['--claude-skills-dir', installed]
            self.run(route + '-install', ['/usr/bin/bash', self.source / 'scripts' / installer[0], *installer[1:]])
            save(self.evidence / (route + '-INSTALLED_BEFORE.json'), self.parity(route))
            subject.mkdir(mode=0o700)
            purpose = 'Receive the exact DG18 installed package through ' + route + ' and establish its actual fresh task currentness before independent receiving.'
            (subject / 'TASK.md').write_text('# Actual DG18 installed consumer task\n\n' + purpose + '\n\nProduct source: ' + SOURCE_HEAD + '.\nNo N1, host compaction, authentic OR, accepting C02 or W-FULL operation is asserted.\n')
            (subject / '.gitignore').write_text('.IMPLEMENTAUDIT/\n')
            self.run(route + '-init', ['/usr/bin/git', '-c', 'init.templateDir=', 'init', '-q', '-b', 'qualification'], subject)
            self.run(route + '-add', ['/usr/bin/git', 'add', '--', 'TASK.md', '.gitignore'], subject)
            self.run(route + '-baseline', ['/usr/bin/git', '-c', 'user.name=PRO-EXECUTOR-01',
                '-c', 'user.email=pro-executor@example.invalid', '-c', 'commit.gpgsign=false', '-c', 'core.hooksPath=/dev/null',
                'commit', '-qm', 'Define actual disposable DG18 installed-consumer task'], subject)
            controller = 'dg18-installed-' + self.host['run_id'] + '-1-' + route
            relative = self.owner(route, 'claim', '--controller', controller, 'DG18 installed current consumer')
            require(re.fullmatch(r'\.IMPLEMENTAUDIT/runs/[a-z0-9-]+-[A-Za-z0-9]{6}', relative), 'unexpected fresh claim root')
            # Existing author reads the exact source templates. It makes no owner call;
            # every claim/activation/currentness operation uses the installed copy.
            self.run(route + '-author', ['/usr/bin/python3', '-I', '-S', '-B',
                self.source / 'fixtures/controller-initialization/author_checkpoint.py', '--repo', subject,
                '--run-root', relative, '--source', self.source, '--purpose', purpose,
                '--next-action', 'Independently receive actual installed currentness and archive parity before any further operation'], subject)
            pending = json.loads(self.owner(route, 'inspect', '--inspect-controller-initialization', controller, '--run-root', relative))
            require(pending['missing_files'] == [] and pending['current_controller_oid'] is None and
                    pending['binding_record_oid'] is None, 'fresh pending initialization differs')
            active = json.loads(self.owner(route, 'activate', '--activate-controller', controller, '--run-root', relative,
                                           '--expected-initialization', pending['initialization_token']))
            require(active['status'] == 'BOUND_ELIGIBLE_FOR_NORMAL_CURRENTNESS', 'activation did not establish eligibility')
            save(self.evidence / (route + '-TASK.json'), {'controller': controller, 'relative': relative,
                 'source': source, 'initialization': pending, 'activation': active,
                 'documents': population(subject / relative), 'installed_skill': str(skill)})

    def task(self, route):
        task = json.loads((self.evidence / (route + '-TASK.json')).read_bytes())
        root = self.paths(route)[1] / task['relative']
        require(root.resolve().is_relative_to(self.paths(route)[1] / '.IMPLEMENTAUDIT/runs'), 'task escaped fresh subject')
        return task, root

    def read(self, role):
        for route in ROUTES:
            task, root = self.task(route)
            require(population(root) == task['documents'], 'fresh task changed before separate read')
            if role == 'ROADMAP':
                require((self.evidence / (route + '-read-state.json')).is_file(), 'STATE must be read first')
            observed = self.run(route + '-read-' + role.lower(), ['/usr/bin/cat', root / (role + '.md')], self.paths(route)[1])
            require(observed == (root / (role + '.md')).read_bytes(), 'separate document read differs')

    def consume(self):
        results = []
        for route in ROUTES:
            task, root = self.task(route)
            _, subject, _, _ = self.paths(route)
            require((self.evidence / (route + '-read-roadmap.json')).is_file(), 'separate ROADMAP read missing')
            require(population(root) == task['documents'], 'fresh task changed after separate reads')
            receipt = self.owner(route, 'resume', '--resume-controller', task['controller'], '--boundary', 'new-session', '--epoch', 'G0001')
            require(re.fullmatch('refs/implementaudit/continuity-receipts/' + task['controller'] + r'/G0001@[0-9a-f]{40}', receipt),
                    'unexpected actual receipt token')
            require(self.owner(route, 'verify', '--verify-resume-receipt', receipt) == receipt, 'actual receipt verification differs')
            require(self.owner(route, 'current', '--require-current-continuity', task['controller']) == receipt, 'actual currentness differs')
            controller = self.owner(route, 'controller', '--current-controller', task['controller'])
            before = population(root)
            refs = self.run(route + '-refs-before', ['/usr/bin/git', 'for-each-ref', '--format=%(refname)\t%(objectname)'], subject)
            self.run(route + '-receipt', ['/usr/bin/git', 'cat-file', 'blob', receipt.rsplit('@', 1)[1]], subject)
            require(self.owner(route, 'current-readback', '--require-current-continuity', task['controller']) == receipt, 'currentness readback drift')
            require(self.run(route + '-refs-after', ['/usr/bin/git', 'for-each-ref', '--format=%(refname)\t%(objectname)'], subject) == refs,
                    'read-only receiving changed refs')
            require(population(root) == before, 'read-only receiving changed task files')
            require(self.parity(route) == json.loads((self.evidence / (route + '-INSTALLED_BEFORE.json')).read_bytes()), 'installed payload changed')
            shutil.copytree(root, self.evidence / (route + '-runtime'))
            result = {'route': route, 'controller_readback': controller, 'receipt_token': receipt,
                      'installed_archive_parity': True, 'task_readback_unchanged': True, 'refs_readback_unchanged': True}
            save(self.evidence / (route + '-RESULT.json'), result)
            results.append(result)
        source = self.source_identity('source-after')
        save(self.evidence / 'RESULT.json', {'status': 'ACTUAL_INSTALLED_CURRENT_CONSUMERS_RECORDED',
             'source': source, 'host': self.host, 'routes': results, 'package_builds': 0,
             'model_turns': 0, 'native_host_discovery': False, 'protected_operations': 0,
             'original_DG18_acceptance': False, 'independent_receiving': 'PENDING_ROOT_REVIEW',
             'N1': 'LOST_UNKNOWN_UNCONSUMED', 'criterion5_exception_approved': False})

    def retain_partial_tasks(self, step):
        """Read only this job's already-created disposable task roots after failure."""
        retained = {}
        for route in ROUTES:
            _, subject, _, _ = self.paths(route)
            runs = subject / '.IMPLEMENTAUDIT/runs'
            target = self.evidence / (route + '-runtime')
            if target.exists():
                retained[route] = {'status': 'EXISTING_CAPTURE_RETAINED_COMPLETENESS_UNVERIFIED'}
                continue
            if not runs.exists():
                retained[route] = {'status': 'NO_TASK_ROOT_IN_THIS_FRESH_SUBJECT_AT_CAPTURE'}
                continue
            try:
                require(not runs.is_symlink() and runs.resolve().is_relative_to(subject.resolve()),
                        'partial task directory escaped its fresh subject')
                roots = list(runs.iterdir())
                require(len(roots) <= 1, 'unexpected extra root in single-claim fresh subject')
                if not roots:
                    retained[route] = {'status': 'NO_TASK_ROOT_IN_THIS_FRESH_SUBJECT_AT_CAPTURE'}
                    continue
                root = roots[0]
                require(root.is_dir() and not root.is_symlink(), 'aliased partial task root')
                before = population(root)
                require(len(before) <= 128 and sum(row['bytes'] for row in before.values()) <= 8 * 1024 * 1024
                        and all(row['bytes'] <= 2 * 1024 * 1024 for row in before.values()),
                        'partial task exceeds bounded retention')
                shutil.copytree(root, target)
                require(population(root) == before and population(target) == before,
                        'partial task changed during retention; currentness remains unverified')
                retained[route] = {'status': 'ACTUAL_PARTIAL_TASK_FILES_RETAINED_UNQUALIFIED',
                                   'relative': root.relative_to(subject).as_posix(), 'files': before}
            except Exception as error:
                retained[route] = {'status': 'PARTIAL_RETENTION_UNVERIFIED',
                                   'type': type(error).__name__, 'reason': str(error)}
        save(self.evidence / ('PARTIAL_TASKS-' + step + '.json'),
             {'scope': 'FRESH_DISPOSABLE_TASK_FILES_ONLY; no replay or state repair',
              'currentness_or_effect_outcome_inferred': False, 'routes': retained})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--step', choices=('prepare', 'read-state', 'read-roadmap', 'consume'), required=True)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    host = host_context()
    source, output = args.source.absolute(), args.output.absolute()
    packet = Path(__file__).resolve().parents[3]
    require(source == Path(os.environ['GITHUB_WORKSPACE']) / 'qualified-source', 'unexpected product checkout')
    require(packet == Path(os.environ['GITHUB_WORKSPACE']) / 'packet', 'unexpected packet checkout')
    require(output == Path(os.environ['RUNNER_TEMP']) / ('dg18-installed-' + host['run_id'] + '-1'), 'unexpected disposable output')
    operation = Operation(source, packet, output, host)
    try:
        if args.step == 'prepare':
            operation.prepare()
        else:
            require(json.loads((operation.evidence / 'HOST.json').read_bytes()) == host, 'host identity changed')
            if args.step.startswith('read-'):
                operation.read(args.step.removeprefix('read-').upper())
            else:
                operation.consume()
    except Exception as error:
        if operation.evidence.is_dir():
            save(operation.evidence / ('FAILURE-' + args.step + '.json'), {'step': args.step,
                 'type': type(error).__name__, 'reason': str(error), 'automatic_retry': False,
                 'original_DG18_acceptance': False, 'utc': datetime.datetime.now(datetime.timezone.utc).isoformat()})
            try:
                operation.retain_partial_tasks(args.step)
            except Exception as capture_error:
                save(operation.evidence / ('RETENTION_FAILURE-' + args.step + '.json'),
                     {'type': type(capture_error).__name__, 'reason': str(capture_error),
                      'primary_failure_record_preserved': True, 'partial_state': 'UNVERIFIED'})
        raise
    print('DG18 actual installed task step completed: ' + args.step)


if __name__ == '__main__':
    main()
