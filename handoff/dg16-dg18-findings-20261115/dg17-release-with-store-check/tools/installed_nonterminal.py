#!/usr/bin/env python3
"""Run one actual disposable installed task; no native host or model operation.

The existing product owns build/install, claim/activation/currentness and yield.
This adapter captures those operations and authors only its own fresh task.
STATE and ROADMAP reads are separate workflow actions. Results require Root's
independent receiving and never discharge original DG17/native acceptance.
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

SOURCE_HEAD = 'a297957be11feb494c0ec467235794a1e0c54751'
SOURCE_TREE = 'b08dc4ecf4028beeedb579a312eccae23cb5d863'
BRANCH = 'refs/heads/engineering/pro-executor-dg17-installed-20261115'
NAMES = ('STATE.md', 'ROADMAP.md', 'PROTOCOL.md', 'THINKING.md',
         'sidecars.md', 'tools.md', 'context.md', 'phases/phase-1.md')
ENV = {'PATH': '/usr/bin:/bin', 'LANG': 'C.UTF-8', 'LC_ALL': 'C.UTF-8',
       'PYTHONDONTWRITEBYTECODE': '1', 'IMPLEMENTAUDIT_PYTHON': '/usr/bin/python3',
       'GIT_CONFIG_NOSYSTEM': '1', 'GIT_CONFIG_GLOBAL': '/dev/null'}


def require(value, reason):
    if not value:
        raise RuntimeError(reason)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def write(path, value):
    data = json.dumps(value, indent=2, sort_keys=True).encode() + b'\n'
    with path.open('xb') as stream:
        stream.write(data)


def fact(path, *, single_link=True):
    before = path.lstat()
    require(stat.S_ISREG(before.st_mode) and (not single_link or before.st_nlink == 1),
            'nonregular or aliased evidence member')
    raw = path.read_bytes()
    after = path.lstat()
    require((before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns, before.st_ctime_ns) ==
            (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns, after.st_ctime_ns),
            'evidence member changed during read')
    return {'bytes': len(raw), 'sha256': digest(raw), 'mode': stat.S_IMODE(before.st_mode)}


def population(root):
    rows = {}
    for path in sorted(root.rglob('*')):
        require(not path.is_symlink(), 'aliased evidence population')
        if path.is_file():
            rows[path.relative_to(root).as_posix()] = fact(path)
    return rows


def host_context():
    require(sys.platform == 'linux' and os.name == 'posix', 'Linux operation required')
    require(os.environ.get('GITHUB_REPOSITORY') == 'theislampill/IMPLEMENTAUDIT.md'
            and os.environ.get('GITHUB_REF') == BRANCH
            and os.environ.get('GITHUB_EVENT_NAME') == 'push', 'unbound hosted operation')
    run = os.environ.get('GITHUB_RUN_ID', '')
    attempt = os.environ.get('GITHUB_RUN_ATTEMPT', '')
    require(run.isdigit() and attempt.isdigit(), 'missing actual workflow identity')
    tools = {}
    for name in ('python3', 'bash', 'git'):
        path = Path('/usr/bin') / name
        actual = path.resolve(strict=True)
        for member in (actual, *actual.parents):
            info = member.stat()
            require(info.st_uid == 0 and not info.st_mode & 0o022,
                    'host tool lacks existing root-owned nonwritable ancestry')
        # Package-manager hardlinks do not weaken root-owned immutable tools.
        # Single-link custody remains required for task/package evidence.
        tools[name] = {'path': str(actual), **fact(actual, single_link=False)}
    require(Path(sys.executable).resolve() == Path(tools['python3']['path']),
            'adapter must use installed system Python')
    return {'repository': os.environ['GITHUB_REPOSITORY'], 'branch': BRANCH,
            'run_id': run, 'attempt': attempt, 'workflow_commit': os.environ['GITHUB_SHA'],
            'python_version': list(sys.version_info[:3]), 'tools': tools,
            'actor': 'PRO-EXECUTOR-01', 'native_or_model_operation': False}


class Operation:
    def __init__(self, source, output, context):
        self.source, self.output, self.context = source, output, context
        self.evidence = output / 'evidence'
        self.subject = output / 'subject'
        self.installed = output / 'isolated-host/plugins/implementaudit'
        self.helper = self.installed / 'skills/implementaudit/scripts/claim-run.sh'
        self.validator = self.installed / 'skills/implementaudit/scripts/validate-run-root.sh'
        self.controller = 'dg17-installed-' + context['run_id'] + '-' + context['attempt']

    def run(self, label, argv, cwd=None, seconds=90, environment=None):
        argv = [str(value) for value in argv]
        stdout = self.evidence / (label + '.stdout.txt')
        stderr = self.evidence / (label + '.stderr.txt')
        start = time.monotonic()
        timeout = False
        with stdout.open('xb') as out, stderr.open('xb') as err:
            child = subprocess.Popen(argv, cwd=cwd or self.source, env=environment or ENV,
                                     stdin=subprocess.DEVNULL, stdout=out, stderr=err,
                                     start_new_session=True)
            try:
                code = child.wait(timeout=seconds)
            except subprocess.TimeoutExpired:
                timeout = True
                os.killpg(child.pid, signal.SIGKILL)
                code = child.wait()
        record = {'argv': argv, 'cwd': str(cwd or self.source), 'exit_code': code,
                  'timeout': timeout, 'elapsed_seconds': time.monotonic() - start,
                  'stdout': fact(stdout), 'stderr': fact(stderr)}
        write(self.evidence / (label + '.json'), record)
        require(not timeout and code == 0, 'operation refused: ' + label)
        require(stdout.stat().st_size <= 2 * 1024 * 1024, 'bounded output exceeded: ' + label)
        return stdout.read_bytes()

    def owner(self, label, *arguments):
        return self.run(label, ['/usr/bin/bash', self.helper, *arguments], self.subject).decode().strip()

    def source_identity(self, label):
        identity = self.run(label, ['/usr/bin/git', 'rev-parse', 'HEAD', 'HEAD^{tree}']).decode().splitlines()
        require(identity == [SOURCE_HEAD, SOURCE_TREE], 'product source identity differs')
        require(self.run(label + '-clean', ['/usr/bin/git', 'status', '--porcelain=v1',
                                           '--untracked-files=all']) == b'', 'product source is dirty')
        return {'commit': identity[0], 'tree': identity[1], 'worktree_state': 'clean'}

    def installed_parity(self):
        asset = self.output / 'packages/IMPLEMENTAUDIT.plugin.zip'
        with zipfile.ZipFile(asset) as archive:
            require(archive.testzip() is None, 'package CRC refused')
            names = archive.namelist()
            require(len(names) == len(set(names)), 'duplicate package member')
            expected = {}
            for item in archive.infolist():
                raw = archive.read(item)
                expected[item.filename] = {'bytes': len(raw), 'sha256': digest(raw),
                                           'mode': (item.external_attr >> 16) & 0o777}
            inventory = json.loads(archive.read('IMPLEMENTAUDIT_INVENTORY.json'))
            require(inventory['source'] == {'commit': SOURCE_HEAD, 'tree': SOURCE_TREE,
                                            'worktree_state': 'clean'}, 'archive source identity differs')
        observed = population(self.installed)
        require(observed == expected, 'installed archive parity refused')
        return observed

    def prepare(self):
        self.output.mkdir(mode=0o700)
        self.evidence.mkdir(mode=0o700)
        write(self.evidence / 'HOST.json', self.context)
        source = self.source_identity('source-before')
        venv = self.output / 'build-venv'
        self.run('build-venv', ['/usr/bin/python3', '-I', '-B', '-m', 'venv', venv])
        self.run('release-dependency', [venv / 'bin/python', '-I', '-B', '-m', 'pip', '--isolated',
                 '--disable-pip-version-check', '--no-input', 'install', '--no-deps', '--no-compile',
                 '--no-cache-dir', '--requirement', self.source / 'requirements-release.txt'], seconds=180)
        build_env = {**ENV, 'PATH': str(venv / 'bin') + ':/usr/bin:/bin'}
        self.run('build-package', ['/usr/bin/bash', self.source / 'scripts/build-release-asset.sh',
                 self.output / 'packages'], seconds=600, environment=build_env)
        self.run('verify-package', ['/usr/bin/python3', '-I', '-B', self.source / 'scripts/package-contract.py',
                 '--verify-artifact', 'canonical_plugin', self.output / 'packages/IMPLEMENTAUDIT.plugin.zip',
                 '--require-clean-source'])
        host = self.output / 'isolated-host'
        host.mkdir(mode=0o700)
        (host / '.implementaudit-isolated-host-root').write_text('DG17 actual disposable installed consumer\n')
        self.run('install-package', ['/usr/bin/bash', self.source / 'scripts/install-plugin-from-release.sh',
                 '--asset', self.output / 'packages/IMPLEMENTAUDIT.plugin.zip', '--checksum',
                 self.output / 'packages/CHECKSUMS.txt', '--host', 'codex', '--host-root', host])
        installed = self.installed_parity()
        write(self.evidence / 'INSTALLED_BEFORE.json', installed)
        contract = json.loads((self.source / 'package/implementaudit-package.json').read_bytes())
        write(self.evidence / 'PACKAGES.json', {'source': source,
              'budget_revision': contract['budget_revision'], 'budgets': contract['budgets'],
              'artifacts': population(self.output / 'packages'), 'native_discovery': False})
        self.subject.mkdir(mode=0o700)
        purpose = ('Receive the exact DG17 installed package, establish one fresh governed task, '
                   'and evaluate its real nonterminal continuation before independent Root receiving.')
        (self.subject / 'TASK.md').write_text('# Actual DG17 installed consumer task\n\n' + purpose +
            '\n\nActor: PRO-EXECUTOR-01. Product: ' + SOURCE_HEAD + '.\n'
            'This disposable task stays open for independent receiving. Original DG17, native Stop, '
            'T12/T13 and fourteen historical custody UNKNOWN differences remain unresolved.\n')
        (self.subject / '.gitignore').write_text('.IMPLEMENTAUDIT/\n')
        self.run('subject-init', ['/usr/bin/git', '-c', 'init.templateDir=', 'init', '-q', '-b', 'qualification'], self.subject)
        self.run('subject-add', ['/usr/bin/git', 'add', '--', 'TASK.md', '.gitignore'], self.subject)
        self.run('subject-baseline', ['/usr/bin/git', '-c', 'user.name=PRO-EXECUTOR-01',
                 '-c', 'user.email=pro-executor@example.invalid', '-c', 'commit.gpgsign=false',
                 '-c', 'core.hooksPath=/dev/null', 'commit', '-qm', 'Define actual disposable DG17 consumer task'], self.subject)
        relative = self.owner('claim', '--controller', self.controller, 'dg17 installed nonterminal receiving')
        require(re.fullmatch(r'\.IMPLEMENTAUDIT/runs/[a-z0-9-]+-[A-Za-z0-9]{6}', relative), 'unexpected claimed root')
        root = self.subject / relative
        next_action = 'Receive the actual installed receipt, source parity and nonterminal result independently before authorizing further work'
        self.run('author', ['/usr/bin/python3', '-I', '-S', '-B',
                 self.source / 'fixtures/controller-initialization/author_checkpoint.py',
                 '--repo', self.subject, '--run-root', relative, '--source', self.installed,
                 '--purpose', purpose, '--next-action', next_action], self.subject)
        state = root / 'STATE.md'
        text = state.read_text()
        for key, value in {'Status': 'READY_TO_DISPATCH',
                'Owner/source': 'PRO-EXECUTOR-01 ordinary DG17 installed-consumer commission',
                'Last check': 'Exact source, package build, archive verification and installed population parity passed',
                'Authorization state': 'Fresh disposable deterministic installed task authorized; original acceptance remains with Root',
                'Re-entry condition': 'Read the actual STATE and ROADMAP separately and require this exact controller receipt before further work',
                'Pending decision': 'Independent Root receiving of the actual consumer outputs and remaining original obligations'}.items():
            pattern = r'^\| ' + re.escape(key) + r' \|[^\n]*\n'
            if re.search(pattern, text, re.M):
                text, count = re.subn(pattern, '| ' + key + ' | ' + value + ' |\n', text, flags=re.M)
                require(count == 1, 'ambiguous initial field')
            else:
                text = text.replace('| Field | Value |\n|---|---|\n',
                                    '| Field | Value |\n|---|---|\n| ' + key + ' | ' + value + ' |\n', 1)
        state.write_text(text)
        pending = json.loads(self.owner('inspect', '--inspect-controller-initialization', self.controller, '--run-root', relative))
        require(pending['missing_files'] == [] and pending['current_controller_oid'] is None
                and pending['binding_record_oid'] is None, 'pending initialization differs')
        active = json.loads(self.owner('activate', '--activate-controller', self.controller, '--run-root', relative,
                                     '--expected-initialization', pending['initialization_token']))
        require(active['status'] == 'BOUND_ELIGIBLE_FOR_NORMAL_CURRENTNESS', 'activation did not establish eligibility')
        write(self.evidence / 'TASK.json', {'relative': relative, 'controller': self.controller,
              'source': source, 'initialization': pending, 'activation': active,
              'document_population': population(root), 'next_action': next_action})

    def task(self):
        task = json.loads((self.evidence / 'TASK.json').read_bytes())
        require(task['controller'] == self.controller, 'task controller differs')
        return task, self.subject / task['relative']

    def read(self, role):
        task, root = self.task()
        require(population(root) == task['document_population'], 'initialized task changed before separate read')
        if role == 'ROADMAP':
            require((self.evidence / 'read-state.json').is_file(), 'STATE must be read first')
        observed = self.run('read-' + role.lower(), ['/usr/bin/cat', root / (role + '.md')], self.subject)
        require(observed == (root / (role + '.md')).read_bytes(), 'separate read differs')

    def consume(self):
        task, root = self.task()
        require((self.evidence / 'read-roadmap.json').is_file(), 'separate ROADMAP read missing')
        require(population(root) == task['document_population'], 'task changed after separate reads')
        receipt = self.owner('resume', '--resume-controller', self.controller, '--boundary', 'new-session', '--epoch', 'G0001')
        require(re.fullmatch('refs/implementaudit/continuity-receipts/' + self.controller + r'/G0001@[0-9a-f]{40}', receipt),
                'unexpected actual receipt token')
        require(self.owner('verify-receipt', '--verify-resume-receipt', receipt) == receipt, 'receipt verification differs')
        require(self.owner('current-before', '--require-current-continuity', self.controller) == receipt, 'current receipt differs')
        controller = self.owner('current-controller', '--current-controller', self.controller)
        refs_before = self.run('refs-before', ['/usr/bin/git', 'for-each-ref', '--format=%(refname)\t%(objectname)'], self.subject)
        before = population(root)
        installed_result = self.run('installed-yield', ['/usr/bin/bash', self.validator, '--nonterminal-yield', root], self.subject)
        source_result = self.run('source-yield', ['/usr/bin/bash', self.source / 'skills/implementaudit/scripts/validate-run-root.sh',
                                             '--nonterminal-yield', root], self.subject)
        require(installed_result == source_result and b'nonterminal yield record ok' in installed_result,
                'source and installed declared result differ')
        require(self.owner('current-after', '--require-current-continuity', self.controller) == receipt, 'currentness drift')
        require(self.run('refs-after', ['/usr/bin/git', 'for-each-ref', '--format=%(refname)\t%(objectname)'], self.subject) == refs_before,
                'read-only consumption changed refs')
        require(population(root) == before, 'read-only consumption changed governed records')
        require(self.installed_parity() == json.loads((self.evidence / 'INSTALLED_BEFORE.json').read_bytes()), 'installed payload changed')
        self.source_identity('source-after')
        self.run('receipt-object', ['/usr/bin/git', 'cat-file', 'blob', receipt.split('@')[1]], self.subject)
        shutil.copytree(root, self.evidence / 'runtime')
        write(self.evidence / 'RESULT.json', {'status': 'ACTUAL_INSTALLED_NONTERMINAL_CONSUMER_PASS',
              'source': task['source'], 'host': self.context, 'controller': controller,
              'receipt_token': receipt, 'runtime_before': before, 'runtime_after': population(root),
              'governed_records_unchanged': True, 'refs_unchanged': True, 'source_installed_result_equal': True,
              'native_stop_acceptance': False, 'native_host_discovery': False, 'model_turns': 0,
              'original_DG17_acceptance': False, 'independent_receiving': 'PENDING_ROOT_REVIEW',
              'original14_custody_unknown_differences': 14, 'task_audit_object_state': 'open'})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--step', required=True, choices=('prepare', 'read-state', 'read-roadmap', 'consume'))
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    context = host_context()
    source, output = args.source.absolute(), args.output.absolute()
    require(source == Path(os.environ['GITHUB_WORKSPACE']) / 'qualified-source', 'unexpected product checkout')
    require(output == Path(os.environ['RUNNER_TEMP']) / ('dg17-installed-' + context['run_id'] + '-' + context['attempt']),
            'unexpected disposable output')
    operation = Operation(source, output, context)
    try:
        if args.step == 'prepare':
            operation.prepare()
        else:
            require(json.loads((operation.evidence / 'HOST.json').read_bytes()) == context, 'host identity changed')
            if args.step.startswith('read-'):
                operation.read(args.step.removeprefix('read-').upper())
            else:
                operation.consume()
    except Exception as error:
        if operation.evidence.is_dir():
            write(operation.evidence / ('FAILURE-' + args.step + '.json'),
                  {'step': args.step, 'type': type(error).__name__, 'reason': str(error),
                   'native_stop_acceptance': False, 'original_DG17_acceptance': False,
                   'utc': datetime.datetime.now(datetime.timezone.utc).isoformat()})
        raise
    print('DG17 actual installed task step completed: ' + args.step)


if __name__ == '__main__':
    main()
