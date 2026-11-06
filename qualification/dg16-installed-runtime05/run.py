#!/usr/bin/env python3
"""One prospective installed-runtime episode; no original acceptance authority."""
import argparse
import ast
import ctypes
import errno
import hashlib
import json
import math
import os
from pathlib import Path
import re
import resource
import signal
import stat
import sys
import time
import traceback
import types

REPOSITORY = 'theislampill/IMPLEMENTAUDIT.md'
BRANCH = 'pro/dg16-r5-installed-runtime-05r1-20261106'
SOURCE_COMMIT = '0d57929be5bd15682b4e9da2c0209d5dff307843'
SOURCE_TREE = 'ee316c27250ec422d35a1ea965182ebddf7a5da0'
UTILITY_SHA = '429c6b50cef6ef6352a0c812ce9fcf386cc852156ba54c2d1419088c8f89f85c'
SUPPORT_SHA = 'bf4d53a55c1a1f7d5e38d8c3a9c4e91dc64d817ed6d512ce84f172ff10a15ca0'
INSTALLED_SHA = 'dce0a59af7341a7ce135a0e2f8042ed2bf0e18ac191a7c3f6728c6af6c7eda3d'
MANIFEST_SHA = 'a9d6b6ab0a4395e331ecba2499779103ff5bf8ac70d0c9a33a0a85b0d77d789e'
ROUTES = ('plugin-codex','plugin-claude','standalone-codex','standalone-claude')
STEPS = ('prepare','initialize','read-state','read-roadmap','resume','build','install',
         'qualify-plugin-codex','receive-plugin-codex','qualify-plugin-claude','receive-plugin-claude',
         'qualify-standalone-codex','receive-standalone-codex','qualify-standalone-claude','receive-standalone-claude')
PUBLIC_NAMES = ('RESULT.json','HOST.json','SOURCE.json','PACKAGES.json','ROUTES.json','PHASES.json','FAILURE.json','CLEANUP.json')
RUN_SECONDS, FINAL_SECONDS, SETUP_SECONDS, BUILD_SECONDS = 2400, 180, 600, 600
FILE_LIMIT, TOTAL_LIMIT, ENVELOPE_LIMIT, LOG_LIMIT = 65536, 262144, 262144, 1048576
PRIVATE_CAPTURE_LIMIT = 16 * 1024 * 1024
OWNER = 'skills/implementaudit/scripts/claim-run.sh'
AUTHOR = 'fixtures/controller-initialization/author_checkpoint.py'
PURPOSE = 'Build the exact current two-role package once and qualify the affected installed initialization and first normal continuity chain in four fresh isolated Linux layouts with separate-process receiving.'
NEXT_ACTION = 'Run the bounded package and installed-route operation, receive actual same-subject refs objects receipts and documents, and recheck parent and all received subjects before teardown while leaving every governed phase open'
DIAGNOSTICS = ((b'companion source executing claim code source changed before load binding','CLAIM_LOAD_BINDING_CHANGED'),
    (b'supported physical Python 3 interpreter is required','PHYSICAL_PYTHON_REFUSED'),
    (b'controller initialization','CONTROLLER_INITIALIZATION_DIAGNOSTIC'),
    (b'current continuity','CURRENT_CONTINUITY_DIAGNOSTIC'),
    (b'canonical source is dirty','PACKAGE_SOURCE_DIRTY'),
    (b'budget','PACKAGE_BUDGET_DIAGNOSTIC'), (b'zopfli','RELEASE_DEPENDENCY_DIAGNOSTIC'),
    (b'No module named','PYTHON_MODULE_UNAVAILABLE'), (b'permission denied','OS_PERMISSION_DENIED'),
    (b'No such file or directory','OS_REQUIRED_PATH_UNAVAILABLE'),
    (b'not a git repository','GIT_REPOSITORY_UNAVAILABLE'),
    (b'detected dubious ownership','GIT_OWNERSHIP_REFUSED'))
EXCEPTIONS = ('AssertionError','RuntimeError','ValueError','OSError','TimeoutError','FileNotFoundError',
              'PermissionError','ImportError','ModuleNotFoundError','CalledProcessError','ContractError','RotationError','WorkGraphError','CustodyError',
              'SystemExit','BadZipFile','JSONDecodeError','Refusal','Deadline','Interrupted')
DIAGNOSTIC_SOURCES = ('scripts/package-contract.py','fixtures/controller-initialization/author_checkpoint.py',
    'skills/implementaudit/scripts/claim-run-rotation.py','skills/implementaudit/scripts/compile-work-graph.py',
    'skills/implementaudit/scripts/canonical_custody.py')


class Refusal(Exception): pass
class Deadline(Exception): pass
class Interrupted(Exception): pass


def need(value, code):
    if not value:
        raise Refusal(code)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    return (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=True, allow_nan=False) + '\n').encode('ascii')


def load_module(name, expected, maximum=1024*1024):
    path = Path(__file__).with_name(name + '.py'); before = path.lstat()
    need(stat.S_ISREG(before.st_mode) and before.st_nlink == 1 and before.st_uid == os.geteuid()
         and not before.st_mode & 0o6022 and before.st_size <= maximum, 'ADAPTER_MODULE_SHAPE_REFUSED')
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC)
    try:
        def mark(s): return (s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
        need(mark(os.fstat(fd)) == mark(before), 'ADAPTER_MODULE_OPEN_CHANGED')
        with os.fdopen(os.dup(fd), 'rb') as stream:
            raw = stream.read(maximum + 1)
        need(len(raw) == before.st_size and digest(raw) == expected and mark(os.fstat(fd)) == mark(before)
             and mark(path.lstat()) == mark(before), 'ADAPTER_MODULE_DIGEST_REFUSED')
    finally:
        os.close(fd)
    module = types.ModuleType('sealed_' + name); module.__file__ = str(path)
    exec(compile(raw, str(path), 'exec'), module.__dict__)
    return module


def host_context(source, output):
    env = os.environ
    need(env.get('GITHUB_ACTIONS') == 'true' and env.get('GITHUB_REPOSITORY') == REPOSITORY
         and env.get('GITHUB_EVENT_NAME') == 'push' and env.get('GITHUB_REF') == 'refs/heads/' + BRANCH
         and env.get('GITHUB_RUN_ATTEMPT') == '1', 'EVENT_GUARD_REFUSED')
    run = env.get('GITHUB_RUN_ID', ''); commit = env.get('GITHUB_SHA', '')
    need(re.fullmatch('[0-9]{1,20}', run) and re.fullmatch('[0-9a-f]{40}', commit), 'HOST_CONTEXT_ID_REFUSED')
    workspace = Path(env.get('GITHUB_WORKSPACE', '')).resolve(strict=True)
    temp = Path(env.get('RUNNER_TEMP', '')).resolve(strict=True)
    need(source == workspace / 'qualified-source' and source.resolve(strict=True) == source
         and output == temp / ('dg16-installed05-' + run + '-1')
         and Path(__file__).absolute().parent == workspace / 'packet/qualification/dg16-installed-runtime05', 'HOST_PATH_BINDING_REFUSED')
    return {'repository': REPOSITORY, 'branch': BRANCH, 'run_id': run, 'attempt': 1, 'workflow_commit': commit}


def read_boot_identity():
    path = Path('/proc/sys/kernel/random/boot_id')
    def mark(s): return (s.st_dev,s.st_ino,s.st_mode,s.st_nlink,s.st_size,s.st_uid,s.st_gid)
    for parent in reversed(path.parents):
        info = parent.lstat()
        need(stat.S_ISDIR(info.st_mode) and info.st_uid == 0 and not info.st_mode & 0o022, 'BOOT_ANCESTRY_REFUSED')
    before = path.lstat()
    need(stat.S_ISREG(before.st_mode) and before.st_nlink == 1 and before.st_size == 0
         and before.st_uid == before.st_gid == 0 and stat.S_IMODE(before.st_mode) == 0o444, 'BOOT_FILE_REFUSED')
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK | os.O_CLOEXEC)
    try:
        need(mark(os.fstat(fd)) == mark(before), 'BOOT_OPEN_CHANGED')
        first = os.read(fd, 129)
        need(re.fullmatch(rb'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\n', first), 'BOOT_BYTES_REFUSED')
        need(os.lseek(fd, 0, os.SEEK_SET) == 0 and os.read(fd, 129) == first
             and mark(os.fstat(fd)) == mark(before) == mark(path.lstat()), 'BOOT_READBACK_CHANGED')
        return first
    finally:
        os.close(fd)


def inventory(u):
    need(sys.platform == 'linux' and os.name == 'posix' and os.geteuid() != 0
         and os.uname().machine == 'x86_64' and tuple(sys.version_info[:3]) == (3,14,4), 'HOST_RUNTIME_REFUSED')
    release = {}
    for line in u.checked_file(Path('/etc/os-release').resolve(strict=True), 16384).decode().splitlines():
        if '=' in line:
            key, value = line.split('=', 1)
            if key in ('ID','VERSION_ID'): release[key] = value.strip('"')
    need(release == {'ID':'ubuntu','VERSION_ID':'26.04'}, 'HOST_OS_REFUSED')
    paths = {}; facts = {}
    for name in ('bash','python3','git','env'):
        paths[name], facts[name] = u.trusted(name)
        need(paths[name] is not None, 'TRUSTED_HOST_TOOL_UNAVAILABLE')
    need(Path(sys.executable).resolve(strict=True) == Path(paths['python3']), 'INTERPRETER_CUSTODY_REFUSED')
    return paths, {'os': release, 'architecture':'x86_64', 'kernel':u.token(os.uname().release),
        'python_version':[3,14,4], 'uid':os.geteuid(), 'image_os':u.token(os.environ.get('ImageOS','')),
        'image_version':u.token(os.environ.get('ImageVersion','')), 'tools':facts,
        'boot_identity_sha256':digest(read_boot_identity())}


def venv_snapshot(root, python):
    rows = {}; total = 0; count = 0
    for parent, dirs, files in os.walk(root, followlinks=False):
        here = Path(parent); info = here.lstat()
        need(stat.S_ISDIR(info.st_mode) and info.st_uid == os.geteuid() and not info.st_mode & 0o6022, 'VENV_DIRECTORY_REFUSED')
        for name in list(dirs) + files:
            path = here / name; info = path.lstat(); rel = path.relative_to(root).as_posix()
            count += 1; need(count <= 10000 and info.st_uid == os.geteuid(), 'VENV_POPULATION_REFUSED')
            if stat.S_ISLNK(info.st_mode):
                target = os.readlink(path); resolved = path.resolve(strict=True)
                need(len(target) <= 4096 and ((rel in ('bin/python','bin/python3','bin/python3.14') and resolved == Path(python))
                     or (rel == 'lib64' and resolved == root / 'lib')), 'VENV_ALIAS_REFUSED')
                rows[rel] = {'kind':'alias','target':target,'mode':stat.S_IMODE(info.st_mode)}
                if name in dirs: dirs.remove(name)
            elif stat.S_ISDIR(info.st_mode):
                need(not info.st_mode & 0o6022, 'VENV_DIRECTORY_MODE_REFUSED')
            else:
                need(stat.S_ISREG(info.st_mode) and info.st_nlink == 1 and not info.st_mode & 0o6022
                     and info.st_size <= 64*1024*1024, 'VENV_FILE_REFUSED')
                raw = path.read_bytes(); total += len(raw)
                need(len(raw) == info.st_size and total <= 128*1024*1024, 'VENV_BYTES_BOUND')
                after = path.lstat()
                need((info.st_dev,info.st_ino,info.st_size,info.st_mtime_ns,info.st_ctime_ns) ==
                     (after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns,after.st_ctime_ns), 'VENV_READ_CHANGED')
                rows[rel] = {'kind':'file','bytes':len(raw),'sha256':digest(raw),'mode':stat.S_IMODE(info.st_mode)}
    need((root / 'pyvenv.cfg').is_file() and (root / 'bin/python').is_symlink(), 'VENV_STRUCTURE_REFUSED')
    return {'members':rows,'file_or_alias_count':len(rows),'total_file_bytes':total}


def adapter_codes():
    result = set()
    for name in ('run.py','installed_runtime.py','host_support.py','host_utility.py'):
        for node in ast.walk(ast.parse(Path(__file__).with_name(name).read_text())):
            if isinstance(node, ast.Constant) and type(node.value) is str and re.fullmatch('[A-Z][A-Z0-9_]{2,100}', node.value):
                result.add(node.value)
    return result


def diagnostic(stderr, source, manifest):
    codes = sorted({code for needle, code in DIAGNOSTICS if needle.lower() in stderr.lower()})
    exception = None
    for candidate in EXCEPTIONS:
        if re.search(rb'(?:^|\n)' + candidate.encode() + rb':', stderr): exception = candidate
    sites = []
    text = stderr.decode('utf-8', 'replace')
    for match in re.finditer(r'File "([^"\r\n]+)", line ([0-9]{1,7}), in ([A-Za-z_][A-Za-z_0-9]*|<module>)', text):
        path, number, function = match.groups()
        selected = next((name for name in DIAGNOSTIC_SOURCES if path.endswith('/' + name) or path.endswith('/' + Path(name).name)), None)
        if selected is None or selected not in manifest: continue
        raw = (source / selected).read_bytes()
        if len(raw) != manifest[selected]['bytes'] or digest(raw) != manifest[selected]['sha256']: continue
        try:
            functions = {node.name for node in ast.walk(ast.parse(raw)) if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef))}
        except (SyntaxError, UnicodeError): continue
        if (function == '<module>' or function in functions) and 1 <= int(number) <= len(raw.splitlines()):
            sites.append({'source':selected,'line':int(number),'function':function,'source_sha256':digest(raw)})
    refusals = []
    # A source-bound fixed diagnostic survives even when the maintained CLI
    # catches its exception and emits no traceback. This matches only literal
    # text already in the pinned public source, never a private interpolated value.
    if stderr:
        for selected in DIAGNOSTIC_SOURCES:
            if selected not in manifest: continue
            raw = (source / selected).read_bytes()
            if len(raw) != manifest[selected]['bytes'] or digest(raw) != manifest[selected]['sha256']: continue
            try: tree = ast.parse(raw)
            except (SyntaxError,UnicodeError): continue
            for node in ast.walk(tree):
                if not isinstance(node,ast.Raise) or not isinstance(node.exc,ast.Call) or not node.exc.args: continue
                name = node.exc.func.id if isinstance(node.exc.func,ast.Name) else None
                if name not in EXCEPTIONS: continue
                argument = node.exc.args[0]
                pieces = [argument.value] if isinstance(argument,ast.Constant) and type(argument.value) is str else []
                if isinstance(argument,ast.JoinedStr):
                    pieces = [item.value for item in argument.values if isinstance(item,ast.Constant) and type(item.value) is str]
                for text_piece in pieces:
                    fixed = text_piece.encode('utf-8')
                    if len(fixed) >= 24 and fixed in stderr:
                        refusals.append({'source':selected,'line':node.lineno,'source_sha256':digest(raw),
                            'declared_exception_class':name,'fixed_text_sha256':digest(fixed)})
                        break
    return {'known_codes':codes,'exception_type':exception,'source_sites':sites[-3:],
            'source_refusals':refusals[:8],'source_refusals_truncated':len(refusals)>8}


class Context:
    def __init__(self, state, source, output, u, h, installed, manifest, stage):
        self.state,self.source,self.output,self.u,self.h,self.installed,self.manifest,self.stage = state,source,output,u,h,installed,manifest,stage
        self.tools = state.get('tools', {}); self.names = h.NAMES
        self.parse = u.parse_json; self.canonical = canonical
        self.deadline = state['started_monotonic'] + (RUN_SECONDS if stage == 'finalize' else RUN_SECONDS - FINAL_SECONDS) - 5
        self.codes = adapter_codes()

    def persist(self):
        raw = canonical(self.state); need(len(raw) <= 1024*1024, 'PRIVATE_STATE_BOUND')
        self.h.save_state(self.output / 'private/STATE.json', self.state)

    def write(self, path, raw):
        need(len(raw) <= 1024*1024, 'PRIVATE_WRITE_BOUND')
        self.h.write_private(path, raw)

    def capture(self, label, argv, cwd=None, seconds=60, release_env=False):
        cwd = self.source if cwd is None else Path(cwd)
        need(cwd.resolve(strict=True) == cwd and not cwd.is_symlink(), 'COMMAND_CWD_REFUSED')
        need(re.fullmatch('[a-z0-9-]{1,100}', label) and self.state['pending_command'] is None
             and self.state['command_count'] < 512 and 0 < seconds <= 600, 'COMMAND_RESERVATION_REFUSED')
        if release_env:
            argv = [self.tools['env'], 'PATH=' + str(self.output / 'private/ordinary-venv/bin') + ':/usr/bin:/bin', *argv]
        argv = list(map(str, argv))
        number = self.state['command_count'] + 1
        stem = '%03d-%s' % (number, label)
        reserve = {'ordinal':number,'stage':self.stage,'label':label,'outcome':'STARTED_OUTCOME_UNKNOWN',
                   'argv':argv,'cwd':str(cwd),'seconds':seconds,'started_monotonic':time.monotonic()}
        self.write(self.output / 'private/commands' / (stem + '-START.json'), canonical(reserve))
        self.state['command_count'] = number; self.state['pending_command'] = reserve; self.persist()
        records = []; captured = None; error = None
        old = Path.cwd()
        try:
            os.chdir(cwd)
            captured = self.u.capture(label, argv, records, self.deadline, seconds=seconds)
        except BaseException as exc:
            error = exc
            value = getattr(exc, 'captured', None)
            if value is not None: captured = (value['returncode'],value['stdout'],value['stderr'])
        finally:
            os.chdir(old)
            if captured is not None:
                rc, out, err = captured
                amount = len(out) + len(err)
                need(self.state['captured_bytes'] + amount <= PRIVATE_CAPTURE_LIMIT, 'PRIVATE_CAPTURE_AGGREGATE_BOUND')
                self.write(self.output / 'private/commands' / (stem + '.stdout'), out)
                self.write(self.output / 'private/commands' / (stem + '.stderr'), err)
                self.state['captured_bytes'] += amount
            else:
                rc,out,err = None,b'',b''
            row = records[-1] if records else {'name':label,'process_started':None,'returncode':rc,'streams_complete':False}
            final = dict(reserve, outcome='COMPLETED_OBSERVATION' if records else 'STARTED_OUTCOME_UNKNOWN',
                         ended_monotonic=time.monotonic(),capture=row,diagnostic=diagnostic(err,self.source,self.manifest))
            self.write(self.output / 'private/commands' / (stem + '-END.json'), canonical(final))
            self.state['commands'].append(final)
            self.state['pending_command'] = None if records else reserve
            if not row.get('cleanup',{}).get('echild',False): self.state['all_children_reaped'] = False
            self.persist()
        if error is not None: raise error
        need(captured is not None and row.get('streams_complete') is True and row.get('cleanup',{}).get('echild') is True,
             'COMMAND_CAPTURE_INCOMPLETE')
        return captured

    def run(self, label, argv, cwd=None, seconds=60, release_env=False):
        rc, out, err = self.capture(label, argv, cwd, seconds, release_env)
        need(rc == 0, 'MAINTAINED_COMMAND_NONZERO')
        return out

    def parent_current(self, label):
        receipt = self.state['receipt']; need(receipt is not None, 'PARENT_CURRENTNESS_ABSENT')
        raw = self.run(label, [self.tools['bash'], str(self.source / OWNER), '--require-current-continuity', self.state['controller']], self.source)
        need(raw.decode('ascii').strip() == receipt, 'PARENT_CURRENT_RECEIPT_CHANGED')
        return digest(raw)


def provision(ctx):
    state = ctx.state; start = time.monotonic()
    sudo = ctx.h.setup_sudo(ctx.u)
    apt, apt_fact = ctx.u.trusted('apt-get'); need(apt is not None, 'ADMINISTRATIVE_APT_UNTRUSTED')
    ctx.write(ctx.output / 'private/ADMINISTRATIVE_TOOL.json', canonical(sudo))
    state['setup'] = {'status':'GUARDED_BEFORE_EXECUTION','canonical':sudo['canonical'],'bytes':sudo['bytes'],
        'sha256':sudo['sha256'],'mode':sudo['mode'],'uid':sudo['uid'],
        'alias_and_ancestor_count':len(sudo['aliases_and_ancestors']),
        'aliases_and_ancestors_sha256':digest(canonical(sudo['aliases_and_ancestors']))}
    ctx.persist()
    def command(label, args):
        remaining = int(SETUP_SECONDS - (time.monotonic() - start))
        need(remaining > 1, 'SETUP_WATCHDOG')
        return ctx.run(label, args, ctx.source, seconds=remaining)
    command('ordinary-apt-index', [sudo['canonical'],'-n','/usr/bin/apt-get','-qq','update'])
    command('ordinary-apt-prerequisites', [sudo['canonical'],'-n','/usr/bin/apt-get','-qq','install','-y',
            '--no-install-recommends','--no-upgrade','python3-venv'])
    venv = ctx.output / 'private/ordinary-venv'; need(not venv.exists(), 'VENV_REPLAY_REFUSED')
    command('ordinary-create-venv', [ctx.tools['python3'],'-I','-B','-m','venv',str(venv)])
    command('ordinary-install-release-dependency', [str(venv / 'bin/python'),'-I','-B','-m','pip','--isolated',
            '--disable-pip-version-check','--no-input','-q','install','--no-deps','--no-compile','--no-cache-dir',
            '--requirement',str(ctx.source / 'requirements-release.txt')])
    raw = command('ordinary-release-dependency-readback', [str(venv / 'bin/python'),'-I','-B','-c',
        "import hashlib,importlib.metadata,json,pathlib,sys,zopfli,zopfli.zlib;v=importlib.metadata.version('zopfli');assert v=='0.2.3.post1';assert sys.version_info[:3]==(3,14,4);p=pathlib.Path(zopfli.__file__);print(json.dumps({'version':v,'module_bytes':p.stat().st_size,'module_sha256':hashlib.sha256(p.read_bytes()).hexdigest()}))"])
    value = ctx.parse(raw)
    need(type(value) is dict and set(value) == {'version','module_bytes','module_sha256'}
         and value['version'] == '0.2.3.post1' and type(value['module_bytes']) is int and 0 < value['module_bytes'] < 65536
         and re.fullmatch('[0-9a-f]{64}',value['module_sha256']), 'RELEASE_DEPENDENCY_READBACK_REFUSED')
    need(ctx.h.setup_sudo(ctx.u) == sudo and ctx.u.trusted('apt-get')[1] == apt_fact, 'ADMINISTRATIVE_TOOL_CHANGED')
    state['venv'] = venv_snapshot(venv, ctx.tools['python3'])
    ctx.write(ctx.output / 'private/VENV_BEFORE.json', canonical(state['venv']))
    elapsed = time.monotonic() - start; need(elapsed <= SETUP_SECONDS, 'SETUP_WATCHDOG')
    state['setup'].update(status='COMPLETED',elapsed_seconds=elapsed,
                          zopfli_version=value['version'],module_bytes=value['module_bytes'],module_sha256=value['module_sha256'])


def initialize_parent(ctx):
    state = ctx.state; controller = state['controller']; helper = str(ctx.source / OWNER)
    def owner(label, args): return ctx.run(label, [ctx.tools['bash'],helper,*args], ctx.source)
    raw = ctx.run('no-imported-controller-refs', [ctx.tools['git'],'for-each-ref','--format=%(refname)','refs/implementaudit'], ctx.source)
    need(raw == b'', 'PREEXISTING_PARENT_REFS_REFUSED')
    run = owner('parent-claim', ['--controller',controller,'dg16 installed runtime 05']).decode('ascii').strip()
    need(re.fullmatch(r'\.IMPLEMENTAUDIT/runs/dg16-installed-runtime-05-[A-Za-z0-9]{6}',run), 'PARENT_RUN_ROOT_REFUSED')
    state['run_root'] = run; ctx.persist()
    raw = ctx.run('parent-author', [ctx.tools['python3'],'-I','-S','-B',str(ctx.source / AUTHOR),
        '--repo',str(ctx.source),'--run-root',run,'--source',str(ctx.source),'--purpose',PURPOSE,'--next-action',NEXT_ACTION], ctx.source)
    authored = ctx.parse(raw)
    need(set(authored) == set((*ctx.names,'phases/phase-1.md')), 'PARENT_AUTHOR_POPULATION_REFUSED')
    for name, sha in authored.items():
        need(digest(ctx.installed.regular(ctx.source / run / name)) == sha, 'PARENT_AUTHOR_READBACK_REFUSED')
    inspection = ctx.parse(owner('parent-inspect', ['--inspect-controller-initialization',controller,'--run-root',run]))
    need(inspection['missing_files'] == [] and inspection['current_controller_oid'] is None
         and inspection['binding_record_oid'] is None, 'PARENT_PENDING_STATE_REFUSED')
    token = inspection['initialization_token']
    need(re.fullmatch('refs/implementaudit/controller-initializations/' + controller + r'/[0-9a-f]{32}@[0-9a-f]{40}',token), 'PARENT_INITIALIZATION_TOKEN_REFUSED')
    activation = ctx.parse(owner('parent-activate', ['--activate-controller',controller,'--run-root',run,'--expected-initialization',token]))
    need(activation['status'] == 'BOUND_ELIGIBLE_FOR_NORMAL_CURRENTNESS'
         and activation['authority_ceiling'] == 'ELIGIBLE_FOR_NORMAL_CURRENTNESS_ONLY', 'PARENT_ACTIVATION_SCOPE_REFUSED')
    state['activation'] = activation; state['runtime'] = ctx.h.runtime_snapshot(ctx.source,state,ctx.u)
    current = owner('parent-discover', ['--current-controller',controller]).decode().strip().split('\t')
    claim = dict(line.split('=',1) for line in ctx.installed.regular(ctx.source / run / '.claimed',65536).decode().splitlines())
    need(current == [controller,str(ctx.source),str(ctx.source / run),claim['claim_id']], 'PARENT_CONTROLLER_CONTEXT_REFUSED')
    state['parent_initialized'] = True


def operation(ctx):
    state, step = ctx.state, ctx.stage
    if step == 'prepare':
        state['source_before'] = ctx.h.verify_source(ctx.source,ctx.manifest,ctx.u,False)
        ctx.h.check_source_git(ctx.capture,ctx.tools,ctx.source,True)
        provision(ctx)
        paths, facts = inventory(ctx.u)
        need(paths == ctx.tools and facts == state['host'], 'BOOTSTRAP_HOST_CHANGED')
    elif step == 'initialize':
        initialize_parent(ctx)
    elif step in ('read-state','read-roadmap'):
        name = 'STATE.md' if step == 'read-state' else 'ROADMAP.md'
        raw = ctx.installed.regular(ctx.source / state['run_root'] / name)
        ctx.write(ctx.output / 'private' / (step + '.read'), raw)
        state['reads'][name] = {'bytes':len(raw),'sha256':digest(raw),'ordinal':len(state['completed'])}
        if step == 'read-roadmap':
            need(state['reads']['STATE.md']['ordinal'] < state['reads'][name]['ordinal'], 'PARENT_READ_ORDER_REFUSED')
    elif step == 'resume':
        need(set(state['reads']) == {'STATE.md','ROADMAP.md'}, 'PARENT_READ_POPULATION_REFUSED')
        for name, row in state['reads'].items():
            need(digest(ctx.installed.regular(ctx.source / state['run_root'] / name)) == row['sha256'], 'PARENT_READ_BYTES_CHANGED')
        helper = str(ctx.source / OWNER)
        raw = ctx.run('parent-resume', [ctx.tools['bash'],helper,'--resume-controller',state['controller'],'--boundary','new-session','--epoch','G0001'], ctx.source)
        receipt = raw.decode('ascii').strip()
        need(re.fullmatch('refs/implementaudit/continuity-receipts/' + state['controller'] + r'/G0001@[0-9a-f]{40}',receipt), 'PARENT_RECEIPT_TOKEN_REFUSED')
        state['receipt'] = receipt; ctx.persist()
        verified = ctx.run('parent-verify', [ctx.tools['bash'],helper,'--verify-resume-receipt',receipt], ctx.source)
        need(verified.decode('ascii').strip() == receipt, 'PARENT_VERIFIED_RECEIPT_CHANGED')
        ctx.parent_current('parent-require'); state['parent_current'] = True
    elif step == 'build':
        packages = ctx.output / 'private/packages'; need(not packages.exists(), 'BUILD_REPLAY_REFUSED')
        ctx.run('build-two-release-roles', [ctx.tools['bash'],str(ctx.source / 'scripts/build-release-asset.sh'),str(packages)],
                ctx.source, seconds=BUILD_SECONDS, release_env=True)
        state['packages'] = ctx.installed.archive_snapshot(ctx.source,ctx.output,ctx.manifest,ctx.parse)
        ctx.write(ctx.output / 'private/PACKAGES_BEFORE.json',canonical(state['packages']))
    elif step == 'install':
        need(ctx.installed.archive_snapshot(ctx.source,ctx.output,ctx.manifest,ctx.parse) == state['packages'], 'PACKAGE_INPUT_CHANGED')
        ctx.installed.install_all(ctx,state)
    elif step.startswith('qualify-'):
        need(ctx.installed.installed_snapshot(ctx.output,state['packages']) == state['installed'], 'INSTALLED_INPUT_CHANGED')
        ctx.installed.qualify(ctx,state,step.removeprefix('qualify-'))
    elif step.startswith('receive-'):
        need(ctx.installed.installed_snapshot(ctx.output,state['packages']) == state['installed'], 'RECEIVER_INSTALLED_INPUT_CHANGED')
        ctx.installed.receive(ctx,state,step.removeprefix('receive-'))
    else:
        raise Refusal('STEP_NOT_IMPLEMENTED')


def finalize(ctx, predecessor_unknown):
    state = ctx.state
    state['source_after'] = ctx.h.verify_source(ctx.source,ctx.manifest,ctx.u,(ctx.source / '.IMPLEMENTAUDIT').exists())
    state['source_unchanged'] = state['source_after'] == state['source_before']
    if state.get('venv') is not None:
        state['venv_unchanged'] = venv_snapshot(ctx.output / 'private/ordinary-venv',ctx.tools['python3']) == state['venv']
        need(state['venv_unchanged'], 'CLOSING_VENV_CHANGED')
    if state.get('packages') is not None:
        state['packages_unchanged'] = ctx.installed.archive_snapshot(ctx.source,ctx.output,ctx.manifest,ctx.parse) == state['packages']
        need(state['packages_unchanged'], 'CLOSING_PACKAGES_CHANGED')
    if state.get('installed') is not None:
        state['installed_unchanged'] = ctx.installed.installed_snapshot(ctx.output,state['packages']) == state['installed']
        need(state['installed_unchanged'], 'CLOSING_INSTALLED_CHANGED')
    # A successor process cannot establish custody of prior unclean or unknown
    # children, even when the predecessor cleared its active command and step.
    if predecessor_unknown or state.get('all_children_reaped') is not True:
        state['final_currentness'] = None
        raise Refusal('PREDECESSOR_EFFECT_UNCERTAIN_NO_OWNER_READBACK')
    ctx.h.check_source_git(ctx.capture,ctx.tools,ctx.source,True)
    if state.get('runtime') is not None:
        state['runtime_unchanged'] = ctx.h.runtime_snapshot(ctx.source,state,ctx.u) == state['runtime']
        need(state['runtime_unchanged'], 'CLOSING_PARENT_DOCUMENT_DRIFT')
    if state['receipt'] is not None:
        ctx.parent_current('parent-final-before')
        for route in ROUTES:
            if route in state['received']:
                state['closing_subjects'][route] = ctx.installed.close_subject(ctx,state,route)
        ctx.parent_current('parent-final-after'); state['final_currentness'] = True


def fresh_state(context, source, output, h):
    start = time.monotonic()
    return {'schema':'dg16.installed-runtime-private-state.v1','context':context,'started_monotonic':start,
        'source_identity':h.identities(source),'git_identity':h.identities(source / '.git'),
        'output_identity':h.identities(output),'completed':[],'active_step':None,'pending_command':None,
        'command_count':0,'captured_bytes':0,'commands':[],'phases':[],'failures':[],
        'controller':'dg16-installed05-parent-' + context['run_id'] + '-a1','run_root':None,'receipt':None,
        'activation':None,'runtime':None,'reads':{},'parent_initialized':False,'parent_current':False,
        'source_before':None,'source_after':None,'source_unchanged':False,'venv':None,'venv_unchanged':False,
        'packages':None,'packages_unchanged':False,'installed':None,'installed_unchanged':False,
        'subjects':{},'received':{},'closing_subjects':{},'all_children_reaped':True,
        'runtime_unchanged':False,'final_currentness':None,'finalized':False,'finalization_attempted':False,
        'interrupted_predecessor_observed':False,'setup':None,'tools':{},'host':None}


def record_failure(ctx, exc):
    message = str(exc).encode('utf-8','replace')
    code = str(exc) if str(exc) in ctx.codes else 'UNCLASSIFIED_PRIVATE_DIAGNOSTIC'
    entry = {'stage':ctx.stage,'code':code,'exception_type':type(exc).__name__ if type(exc).__name__ in EXCEPTIONS else 'OTHER',
             'diagnostic_bytes':len(message),'diagnostic_sha256':digest(message),'errno':getattr(exc,'errno',None)}
    need(len(ctx.state['failures']) < 32, 'FAILURE_POPULATION_BOUND')
    ctx.state['failures'].append(entry)
    raw = ''.join(traceback.format_exception(type(exc),exc,exc.__traceback__)).encode('utf-8','replace')
    ctx.write(ctx.output / 'private' / ('FAILURE-%02d.txt' % len(ctx.state['failures'])),raw[:65536])


def execute(step, source, output, u, h, installed):
    context = host_context(source,output); manifest = h.read_manifest(u)
    if step == 'prepare':
        need(not output.exists(), 'EPISODE_REPLAY_REFUSED')
        episode_started = time.monotonic()
        output.mkdir(mode=0o700); (output / 'private').mkdir(mode=0o700); (output / 'private/commands').mkdir(mode=0o700)
        state = fresh_state(context,source,output,h)
        state['started_monotonic'] = episode_started
    else:
        state = u.parse_json(installed.regular(output / 'private/STATE.json'))
        need(state['schema'] == 'dg16.installed-runtime-private-state.v1' and state['context'] == context
             and h.identities(source) == state['source_identity'] and h.identities(source / '.git') == state['git_identity']
             and h.identities(output) == state['output_identity'], 'EPISODE_CUSTODY_CHANGED')
    ctx = Context(state,source,output,u,h,installed,manifest,step)
    predecessor_unknown = state['active_step'] is not None or state['pending_command'] is not None or (output / 'private/STATE.next').exists()
    need(step == 'finalize' or not predecessor_unknown, 'PREDECESSOR_STEP_UNFINISHED')
    if step != 'finalize':
        need(not state['failures'] and state['completed'] == list(STEPS[:STEPS.index(step)]), 'STEP_SEQUENCE_REFUSED')
    else:
        need(not state['finalization_attempted'], 'FINALIZER_REPLAY_REFUSED')
        state['finalization_attempted'] = True
    if predecessor_unknown:
        state['all_children_reaped'] = False
        state['interrupted_predecessor_observed'] = True
    # A stale temporary state file is never overwritten or removed. Failure
    # fallback below remains available without claiming currentness.
    need(not (output / 'private/STATE.next').exists(), 'INTERRUPTED_STATE_WRITE_PRESERVED')
    started = time.monotonic(); first_command = state['command_count']
    state['active_step'] = step; ctx.persist()
    success = False; subreaper = False; cleanup = None
    oldcwd = Path.cwd()
    def deadline(_signum, _frame): raise Deadline('EPISODE_WATCHDOG_EXPIRED')
    def interrupted(_signum, _frame): raise Interrupted('HOST_INTERRUPTION_RECEIVED')
    signal.signal(signal.SIGALRM,deadline); signal.signal(signal.SIGTERM,interrupted)
    try:
        remaining = ctx.deadline - time.monotonic(); need(remaining > 0, 'EPISODE_WATCHDOG_EXPIRED')
        signal.setitimer(signal.ITIMER_REAL, remaining)
        h.enable_subreaper(); subreaper = True
        need(u.children() == [], 'PREEXISTING_ADAPTER_CHILDREN')
        tools, facts = inventory(u); ctx.tools = tools
        if state['host'] is None: state['host'],state['tools'] = facts,tools
        else: need(state['host'] == facts and state['tools'] == tools, 'HOST_CUSTODY_CHANGED')
        os.chdir(source)
        if step not in ('prepare','finalize'):
            h.verify_source(source,manifest,u,state['run_root'] is not None)
            h.check_source_git(ctx.capture,tools,source,True)
            if state['runtime'] is not None:
                need(h.runtime_snapshot(source,state,u) == state['runtime'], 'PARENT_RUNTIME_CHANGED')
            if state['venv'] is not None:
                need(venv_snapshot(output / 'private/ordinary-venv',tools['python3']) == state['venv'], 'VENV_RUNTIME_CHANGED')
        qualified_step = step in STEPS[STEPS.index('build'):]
        if qualified_step: ctx.parent_current('parent-before-' + step)
        if step == 'finalize': finalize(ctx,predecessor_unknown)
        else: operation(ctx)
        if qualified_step: ctx.parent_current('parent-after-' + step)
        if state['runtime'] is not None:
            need(h.runtime_snapshot(source,state,u) == state['runtime'], 'PARENT_RUNTIME_CLOSING_CHANGED')
        if step != 'finalize': state['completed'].append(step)
        else: state['finalized'] = True
        success = True
    except BaseException as exc:
        record_failure(ctx,exc)
    finally:
        signal.setitimer(signal.ITIMER_REAL,0)
        os.chdir(oldcwd)
        if subreaper:
            try:
                cleanup = u.stop_owned_children()
                if not cleanup['echild']: state['all_children_reaped'] = False
            except BaseException as exc:
                state['all_children_reaped'] = False
                cleanup = getattr(exc,'cleanup_partial',{'echild':False,'pidfd_signals':0,'reaped_statuses':[]})
                record_failure(ctx,exc)
        else:
            state['all_children_reaped'] = False
        ended = time.monotonic()
        usage = resource.getrusage(resource.RUSAGE_SELF); children_usage = resource.getrusage(resource.RUSAGE_CHILDREN)
        state['phases'].append({'stage':step,'status':'COMPLETED' if success else 'FAILED',
            'started_monotonic':started,'ended_monotonic':ended,'elapsed_seconds':ended-started,
            'command_count':state['command_count']-first_command,'own_children_reaped':bool(cleanup and cleanup['echild']),
            'own_max_rss_kib':usage.ru_maxrss,'reaped_child_max_rss_kib':children_usage.ru_maxrss,
            'rlimit_nofile':list(resource.getrlimit(resource.RLIMIT_NOFILE))})
        if not cleanup or not cleanup['echild']: success = False
        state['active_step'] = None
        state['last_observation_monotonic'] = ended
        if step == 'finalize': state['ended_monotonic'] = ended
        ctx.persist()
    return 0 if success and not state['failures'] else 1


def number(value, maximum=2**63-1):
    need(type(value) is int and 0 <= value <= maximum, 'PUBLIC_INTEGER_REFUSED')
    return value


def seconds(value):
    need(type(value) in (int,float) and math.isfinite(value) and 0 <= value <= 10**8, 'PUBLIC_TIME_REFUSED')
    return value


def hash_value(value):
    need(type(value) is str and re.fullmatch('[0-9a-f]{64}',value), 'PUBLIC_HASH_REFUSED')
    return value


def enum(value, choices):
    need(type(value) is str and value in choices, 'PUBLIC_ENUM_REFUSED')
    return value


def allowed_labels():
    result = {'ordinary-apt-index','ordinary-apt-prerequisites','ordinary-create-venv',
        'ordinary-install-release-dependency','ordinary-release-dependency-readback','source-identity','index-clean','tracked-clean',
        'no-imported-controller-refs','parent-claim','parent-author','parent-inspect','parent-activate','parent-discover',
        'parent-resume','parent-verify','parent-require','parent-final-before','parent-final-after','build-two-release-roles',
        'subject-git-init','subject-git-add','subject-git-commit','subject-baseline','subject-no-imported-refs',
        'installed-claim','installed-author','installed-inspect','installed-activate','installed-read-state','installed-read-roadmap',
        'installed-first-resume','installed-verify','installed-require','installed-refs-after','receive-current-before',
        'receive-refs-before','receive-controller','receive-baseline','receive-verify-final','receive-require-final','receive-refs-after'}
    for step in STEPS[STEPS.index('build'):]:
        result.update(('parent-before-' + step,'parent-after-' + step))
    for route in ROUTES:
        result.add('install-' + route)
        result.update('closing-' + route + '-' + ending for ending in ('refs-before','baseline','require','refs-after'))
    for index in range(16):
        result.update(('receive-object-' + str(index),'receive-object-type-' + str(index)))
    return result


def project_diagnostic(value, manifest):
    need(type(value) is dict and set(value) == {'known_codes','exception_type','source_sites','source_refusals','source_refusals_truncated'}, 'PUBLIC_DIAGNOSTIC_SHAPE_REFUSED')
    known = [enum(code,{code for _,code in DIAGNOSTICS}) for code in value['known_codes']]
    need(known == sorted(set(known)), 'PUBLIC_DIAGNOSTIC_POPULATION_REFUSED')
    exception = value['exception_type']
    if exception is not None: enum(exception,EXCEPTIONS)
    need(len(value['source_sites']) <= 3, 'PUBLIC_SOURCE_SITE_BOUND')
    sites = []
    for row in value['source_sites']:
        source = enum(row['source'],DIAGNOSTIC_SOURCES)
        need(source in manifest and row['source_sha256'] == manifest[source]['sha256']
             and re.fullmatch(r'[A-Za-z_][A-Za-z_0-9]*|<module>',row['function']), 'PUBLIC_SOURCE_SITE_BINDING_REFUSED')
        sites.append({'source':source,'source_sha256':hash_value(row['source_sha256']),
                      'line':number(row['line'],200000),'function':row['function']})
    need(len(value['source_refusals']) <= 8 and type(value['source_refusals_truncated']) is bool, 'PUBLIC_SOURCE_REFUSAL_BOUND')
    refusals = []
    for row in value['source_refusals']:
        source = enum(row['source'],DIAGNOSTIC_SOURCES)
        need(source in manifest and row['source_sha256'] == manifest[source]['sha256'], 'PUBLIC_SOURCE_REFUSAL_BINDING_REFUSED')
        refusals.append({'source':source,'line':number(row['line'],200000),'source_sha256':hash_value(row['source_sha256']),
            'declared_exception_class':enum(row['declared_exception_class'],EXCEPTIONS),'fixed_text_sha256':hash_value(row['fixed_text_sha256'])})
    return {'known_codes':known,'exception_type':exception,'source_sites':sites,'source_refusals':refusals,
            'source_refusals_truncated':value['source_refusals_truncated'],
            'refusal_match_scope':'FIXED_SOURCE_TEXT_OBSERVED; NOT_AN_INFERRED_CAUSE'}


def public_project(state, context, manifest):
    need(state['schema'] == 'dg16.installed-runtime-private-state.v1' and state['context'] == context, 'PUBLIC_STATE_BINDING_REFUSED')
    need(len(state['phases']) <= len(STEPS)+1 and len(state['failures']) <= 32
         and len(state['commands']) <= 512 and set(state['subjects']) <= set(ROUTES)
         and set(state['received']) <= set(ROUTES), 'PUBLIC_STATE_POPULATION_REFUSED')
    current = state['final_currentness'] is True
    complete = (state['completed'] == list(STEPS) and state['finalized'] is True and not state['failures']
        and state['active_step'] is None and state['pending_command'] is None and state['all_children_reaped'] is True
        and state['source_unchanged'] is True and state['venv_unchanged'] is True and state['packages_unchanged'] is True
        and state['installed_unchanged'] is True and state['runtime_unchanged'] is True and current
        and set(state['received']) == set(ROUTES) and set(state['closing_subjects']) == set(ROUTES)
        and state['host'] is not None and state['setup'] is not None and state['setup'].get('status') == 'COMPLETED'
        and state['packages'] is not None and state['installed'] is not None and state['venv'] is not None)
    elapsed = None
    if 'ended_monotonic' in state:
        elapsed = seconds(state['ended_monotonic']-state['started_monotonic'])
        complete = complete and elapsed <= RUN_SECONDS
    else:
        complete = False
    result = dict(context,schema='dg16.installed-runtime-result.v1',status='PASS' if complete else 'UNQUALIFIED',
        source_commit=SOURCE_COMMIT,source_tree=SOURCE_TREE,source_manifest_sha256=MANIFEST_SHA,
        scope='FOUR_LINUX_ISOLATED_INSTALLED_INITIALIZATION_AND_FIRST_NORMAL_CONTINUITY_CHAINS',
        runtime_version='0.4.0',release_family='v0.4.0.0',budget_revision=4,
        original_predicates=['R35-Q04','R35-Q05'],canonical_registry_claim=False,
        installed_routes_received=len(state['received']),parent_final_currentness=current,
        mechanical_independence='DISTINCT_SAME_SUBJECT_PROCESS_ONLY',
        original_acceptance=False,native_application_discovery=False,windows=False,whole_cell_claim=False,
        public_release=False,audit_closure=False,governed_phase_completion_claimed=False,automatic_retry=False,
        interval='FIRST_ADAPTER_BOOTSTRAP_THROUGH_FINAL_BOOKENDS_AND_OWNED_CHILD_CLEANUP',
        checkout_and_artifact_transport_outside_interval=True,elapsed_seconds=elapsed,elapsed_subtraction=0,
        watchdog_seconds=RUN_SECONDS,finalization_reserve_seconds=FINAL_SECONDS,performance_threshold_claimed=False,
        command_count=number(state['command_count'],512),captured_bytes=number(state['captured_bytes'],PRIVATE_CAPTURE_LIMIT),
        private_command_ledger_sha256=digest(canonical(state['commands'])),authority='NONE')
    host = {'schema':'dg16.installed-runtime-host.v1','observation':None,'setup':None,'venv':None,
            'toolchain_bookends_equal':state['finalized'] is True and state['venv_unchanged'] is True}
    if state['venv'] is not None:
        need(state['venv']['file_or_alias_count'] == len(state['venv']['members']) and state['venv']['file_or_alias_count'] > 0,
             'PUBLIC_VENV_POPULATION_REFUSED')
        host['venv'] = {'file_or_alias_count':number(state['venv']['file_or_alias_count'],10000),
            'total_file_bytes':number(state['venv']['total_file_bytes'],128*1024*1024),
            'before_manifest_sha256':digest(canonical(state['venv'])),
            'closing_manifest_equal':state['venv_unchanged'] is True}
    if state['host'] is not None:
        actual = state['host']; tools = {}
        need(actual['os'] == {'ID':'ubuntu','VERSION_ID':'26.04'} and actual['python_version'] == [3,14,4]
             and actual['architecture'] == 'x86_64' and actual['image_os'] == 'ubuntu26'
             and re.fullmatch('[0-9][A-Za-z0-9.+-]{0,79}',actual['kernel'])
             and re.fullmatch(r'[0-9]{8}\.[0-9]{1,5}\.[0-9]{1,5}',actual['image_version']), 'PUBLIC_HOST_IDENTITY_REFUSED')
        need(set(actual['tools']) == {'bash','python3','git','env'}, 'PUBLIC_TOOL_POPULATION_REFUSED')
        for name, row in actual['tools'].items():
            permitted = {'bash':{'/usr/bin/bash'},'git':{'/usr/bin/git'},'env':{'/usr/bin/env'},
                         'python3':{'/usr/bin/python3.14','/usr/bin/python3'}}[name]
            need(row['available'] is True and row['requested'] == '/usr/bin/' + name
                 and row['canonical'] in permitted and row['root_owned_nonwritable_chain'] is True
                 and row['setid_or_file_capabilities'] is False, 'PUBLIC_TOOL_CUSTODY_REFUSED')
            tools[name] = {'canonical':row['canonical'],'bytes':number(row['bytes'],64*1024*1024),
                           'sha256':hash_value(row['sha256']),'root_owned_nonwritable_chain':True,'setid_or_file_capabilities':False}
        host['observation'] = {'os':{'ID':'ubuntu','VERSION_ID':'26.04'},'python_version':[3,14,4],
            'architecture':'x86_64','uid':number(actual['uid'],2**32-1),'kernel':actual['kernel'],
            'image_os':'ubuntu26','image_version':actual['image_version'],
            'boot_identity_sha256':hash_value(actual['boot_identity_sha256']),'tools':tools}
    if state['setup'] is not None:
        actual = state['setup']
        setup = {'status':enum(actual['status'],{'GUARDED_BEFORE_EXECUTION','COMPLETED'}),
            'canonical':enum(actual['canonical'],{'/usr/bin/sudo','/usr/bin/sudo-rs','/usr/bin/sudo.ws','/usr/lib/cargo/bin/sudo'}),
            'bytes':number(actual['bytes'],64*1024*1024),'sha256':hash_value(actual['sha256']),
            'mode':number(actual['mode'],4095),'uid':number(actual['uid'],0),
            'alias_and_ancestor_count':number(actual['alias_and_ancestor_count'],64),
            'aliases_and_ancestors_sha256':hash_value(actual['aliases_and_ancestors_sha256'])}
        if actual['status'] == 'COMPLETED':
            setup.update(elapsed_seconds=seconds(actual['elapsed_seconds']),watchdog_seconds=SETUP_SECONDS,
                zopfli_version=enum(actual['zopfli_version'],{'0.2.3.post1'}),module_bytes=number(actual['module_bytes'],65536),
                module_sha256=hash_value(actual['module_sha256']))
        host['setup'] = setup
    source = {'schema':'dg16.installed-runtime-source.v1','commit':SOURCE_COMMIT,'tree':SOURCE_TREE,
        'manifest_sha256':MANIFEST_SHA,'file_count':1755,'total_bytes':165855954,
        'before_complete':state['source_before'] == {'file_count':1755,'total_bytes':165855954,'manifest_sha256':MANIFEST_SHA,'all_members_match':True},
        'after_complete':state['source_after'] == {'file_count':1755,'total_bytes':165855954,'manifest_sha256':MANIFEST_SHA,'all_members_match':True},
        'source_unchanged':state['source_unchanged'] is True,'parent_runtime_unchanged':state['runtime_unchanged'] is True,
        'tracked_product_mutations_authorized':False}
    build_rows = [row for row in state['commands'] if row['label'] == 'build-two-release-roles']
    pending_build = state['pending_command'] if state['pending_command'] and state['pending_command']['label'] == 'build-two-release-roles' else None
    build_reservations = {row['ordinal'] for row in build_rows} | ({pending_build['ordinal']} if pending_build else set())
    need(len(build_reservations) <= 1, 'PUBLIC_BUILD_REPLAY_REFUSED')
    packages = {'schema':'dg16.installed-runtime-packages.v1','build_command_reservations':len(build_reservations),
        'build_started_observed':any(row['capture'].get('process_started') is True for row in build_rows),
        'build_completion_unknown':pending_build is not None,
        'source':{'commit':SOURCE_COMMIT,'tree':SOURCE_TREE},'artifacts':[],'packages_unchanged':state['packages_unchanged'] is True,
        'all_installed_populations_unchanged':state['installed_unchanged'] is True,'native_discovery_claimed':False}
    if state['packages'] is not None:
        need(set(state['packages']['artifacts']) == {'canonical_plugin','standalone_compatibility'}, 'PUBLIC_ARTIFACT_POPULATION_REFUSED')
        for role in ('canonical_plugin','standalone_compatibility'):
            row = state['packages']['artifacts'][role]
            need(row['source'] == {'commit':SOURCE_COMMIT,'tree':SOURCE_TREE,'worktree_state':'clean'}, 'PUBLIC_PACKAGE_SOURCE_REFUSED')
            need(len(row['members']) == (75 if role == 'canonical_plugin' else 72)
                 and row['inventory_members'] == len(row['members'])-1, 'PUBLIC_PACKAGE_MEMBER_COUNT_REFUSED')
            packages['artifacts'].append({'role':role,'name':'IMPLEMENTAUDIT.plugin.zip' if role == 'canonical_plugin' else 'IMPLEMENTAUDIT.skill',
                'bytes':number(row['bytes'],587824),'sha256':hash_value(row['sha256']),
                'members':number(len(row['members']),256),'inventory_members':number(row['inventory_members'],256),
                'expanded_bytes':number(row['expanded_bytes'],16*1024*1024),'member_bytes_modes_sha256':digest(canonical(row['members'])),
                'complete_inventory_and_source_parity':True,'cap_bytes':589824,'reserve_bytes':2000})
    routes = {'schema':'dg16.installed-runtime-routes.v1','routes':[],'authority':'NONE'}
    if state['installed'] is not None:
        need(state['packages'] is not None and set(state['installed']) == set(ROUTES), 'PUBLIC_INSTALLED_POPULATION_REFUSED')
        for route, value in state['installed'].items():
            role = 'canonical_plugin' if route.startswith('plugin-') else 'standalone_compatibility'
            need(value['role'] == role and value['source'] == {'commit':SOURCE_COMMIT,'tree':SOURCE_TREE,'worktree_state':'clean'}
                 and value['files'] == state['packages']['artifacts'][role]['members'], 'PUBLIC_INSTALLED_PARITY_REFUSED')
    for route in ROUTES:
        request = state['subjects'].get(route); received = state['received'].get(route); closing = state['closing_subjects'].get(route)
        installed = state['installed'].get(route) if state['installed'] else None
        row = {'route':route,'status':'RECEIVED' if received else ('STARTED_UNQUALIFIED' if request else 'UNSTARTED'),
            'installed_members':len(installed['files']) if installed else None,
            'installed_manifest_sha256':digest(canonical(installed['files'])) if installed else None,
            'first_normal_resume_verified':bool(request and request.get('status') == 'FIRST_NORMAL_RESUME_VERIFIED'),
            'distinct_receiver_process':bool(received and received['receiver_pid'] != received['owner_pid']),
            'refs_objects_receipt_documents_received':bool(received and received['status'] == 'PASS'),
            'receipt_body_sha256':hash_value(received['receipt_body_sha256']) if received else None,
            'readback_request_sha256':hash_value(received['request_sha256']) if received else None,
            'authority_ref_count':number(len(received['objects']),16) if received else None,
            'authority_objects_manifest_sha256':digest(canonical(received['objects'])) if received else None,
            'document_count':number(len(received['run_population']),256) if received else None,
            'document_population_sha256':digest(canonical(received['run_population'])) if received else None,
            'receiver_final_currentness':bool(received and received['final_currentness'] is True),
            'closing_currentness':bool(closing and closing['currentness'] is True),
            'closing_refs_and_documents_unchanged':bool(closing and closing['refs_unchanged'] is True and closing['documents_unchanged'] is True),
            'governed_phase_completion_claimed':False}
        routes['routes'].append(row)
    phases = {'schema':'dg16.installed-runtime-phases.v1','phases':[],
              'rss_scope':'PER_ADAPTER_PROCESS_AND_MAX_REAPED_CHILD_NOT_AGGREGATE_JOB_PEAK','memory_acceptance_threshold_claimed':False}
    for row in state['phases']:
        limits = row['rlimit_nofile']; need(type(limits) is list and len(limits) == 2, 'PUBLIC_RESOURCE_SHAPE_REFUSED')
        phases['phases'].append({'stage':enum(row['stage'],(*STEPS,'finalize')),'status':enum(row['status'],{'COMPLETED','FAILED'}),
            'elapsed_seconds':seconds(row['elapsed_seconds']),'command_count':number(row['command_count'],512),
            'own_children_reaped':row['own_children_reaped'] is True,'own_max_rss_kib':number(row['own_max_rss_kib']),
            'reaped_child_max_rss_kib':number(row['reaped_child_max_rss_kib']),
            'rlimit_nofile':[number(item) for item in limits]})
    route_success = all(row['first_normal_resume_verified'] and row['distinct_receiver_process']
        and row['refs_objects_receipt_documents_received'] and row['receiver_final_currentness']
        and row['closing_currentness'] and row['closing_refs_and_documents_unchanged'] for row in routes['routes'])
    phases_success = ([row['stage'] for row in phases['phases']] == [*STEPS,'finalize']
        and all(row['status'] == 'COMPLETED' and row['own_children_reaped'] for row in phases['phases']))
    result['status'] = 'PASS' if complete and route_success and phases_success and packages['build_command_reservations'] == 1 and packages['build_started_observed'] and not packages['build_completion_unknown'] else 'UNQUALIFIED'
    failures = {'schema':'dg16.installed-runtime-failure.v1','present':bool(state['failures']),'failures':[],
                'failed_commands':[],'raw_diagnostics_private':True}
    for row in state['failures']:
        error_number = row['errno']; need(error_number is None or (type(error_number) is int and 0 <= error_number <= 4096), 'PUBLIC_ERRNO_REFUSED')
        failures['failures'].append({'stage':enum(row['stage'],(*STEPS,'finalize')),
            'code':enum(row['code'],adapter_codes() | {'UNCLASSIFIED_PRIVATE_DIAGNOSTIC'}),
            'exception_type':enum(row['exception_type'],(*EXCEPTIONS,'OTHER')),'errno':error_number,
            'diagnostic_bytes':number(row['diagnostic_bytes'],1024*1024),'diagnostic_sha256':hash_value(row['diagnostic_sha256'])})
    failed = [row for row in state['commands'] if row['capture'].get('returncode') != 0
              or row['capture'].get('streams_complete') is not True or row['capture'].get('cleanup',{}).get('echild') is not True]
    need(len(failed) <= 8, 'PUBLIC_FAILED_COMMAND_BOUND')
    for row in failed:
        capture = row['capture']; rc = capture.get('returncode')
        need(rc is None or (type(rc) is int and -255 <= rc <= 255), 'PUBLIC_EXIT_CODE_REFUSED')
        item = {'ordinal':number(row['ordinal'],512),'stage':enum(row['stage'],(*STEPS,'finalize')),
                'label':enum(row['label'],allowed_labels()),'returncode':rc,
                'process_started':capture.get('process_started') is True,'streams_complete':capture.get('streams_complete') is True,
                'timeout':capture.get('timeout') is True,'output_bound_exceeded':capture.get('output_bound_exceeded') is True,
                'children_reaped':capture.get('cleanup',{}).get('echild') is True,
                'pidfd_acquired':capture.get('pidfd_acquired') is True,
                'elapsed_seconds':seconds(row['ended_monotonic']-row['started_monotonic']),
                'diagnostic':project_diagnostic(row['diagnostic'],manifest)}
        start_errno = capture.get('start_errno')
        need(start_errno is None or (type(start_errno) is int and 0 <= start_errno <= 4096), 'PUBLIC_START_ERRNO_REFUSED')
        item['start_errno'] = start_errno
        reason = capture.get('reason_code')
        item['capture_reason_code'] = enum(reason,adapter_codes()) if reason is not None else None
        cleanup_code = capture.get('cleanup',{}).get('code')
        item['cleanup_code'] = enum(cleanup_code,adapter_codes()) if cleanup_code is not None else None
        for stream in ('stdout','stderr'):
            item[stream+'_bytes'] = number(capture.get(stream+'_bytes',0),32768)
            item[stream+'_sha256'] = hash_value(capture.get(stream+'_sha256',digest(b'')))
        failures['failed_commands'].append(item)
    cleanup = {'schema':'dg16.installed-runtime-cleanup.v1','all_recorded_step_children_reaped':state['all_children_reaped'] is True,
        'unknown_pending_step':state['active_step'] is not None or state['interrupted_predecessor_observed'] is True,
        'unknown_pending_command':state['pending_command'] is not None,
        'final_bookends_complete':state['finalized'] is True,'private_outputs_uploaded':False,
        'private_retention':'LIVE_EPHEMERAL_HOST_ONLY; UNKNOWN_INTERRUPTION_IS_NOT_PROOF_OF_ABSENCE',
        'parent_final_currentness':current,'original_acceptance':False}
    return dict(zip(PUBLIC_NAMES,(result,host,source,packages,routes,phases,failures,cleanup)))


def build_transport(documents):
    need(set(documents) <= set(PUBLIC_NAMES) and {'RESULT.json','FAILURE.json'} <= set(documents), 'PUBLIC_POPULATION_REFUSED')
    files = {name:canonical(value) for name,value in documents.items()}
    need(all(len(raw) <= FILE_LIMIT for raw in files.values()), 'PUBLIC_FILE_BOUND')
    manifest = {'schema':'dg16.installed-runtime-artifact-manifest.v1','files':[
        {'name':name,'bytes':len(raw),'sha256':digest(raw)} for name,raw in sorted(files.items())],
        'private_outputs_included':False,'authority':'NONE'}
    files['ARTIFACT_MANIFEST.json'] = canonical(manifest)
    need(len(files['ARTIFACT_MANIFEST.json']) <= FILE_LIMIT and sum(map(len,files.values())) <= TOTAL_LIMIT, 'PUBLIC_TOTAL_BOUND')
    lines = []
    for name,raw in sorted(files.items()):
        envelope = {'schema':'dg16.installed-runtime-envelope.v1','name':name,
            'bytes':len(raw),'sha256':digest(raw),'utf8_json':raw.decode('ascii')}
        line = b'DG16_INSTALLED_RUNTIME ' + json.dumps(envelope,sort_keys=True,separators=(',',':'),ensure_ascii=True,allow_nan=False).encode('ascii') + b'\n'
        need(len(line) <= ENVELOPE_LIMIT, 'PUBLIC_ENVELOPE_BOUND')
        lines.append(line)
    need(sum(map(len,lines)) <= LOG_LIMIT, 'PUBLIC_LOG_AGGREGATE_BOUND')
    return files,lines


def emit(source, output, u, h, installed):
    context = host_context(source,output); manifest = h.read_manifest(u)
    need(output.is_dir() and not output.is_symlink(), 'PUBLIC_OUTPUT_ROOT_REFUSED')
    try:
        # A preserved state write makes the older committed state incomplete.
        need(not os.path.lexists(output / 'private/STATE.next'), 'INTERRUPTED_STATE_WRITE_PRESERVED')
        state = u.parse_json(installed.regular(output / 'private/STATE.json'))
        need(h.identities(output) == state['output_identity'], 'PUBLIC_OUTPUT_IDENTITY_CHANGED')
        files,lines = build_transport(public_project(state,context,manifest))
    except BaseException as exc:
        code = str(exc) if str(exc) in adapter_codes() else 'PUBLIC_PROJECTION_REFUSED'
        documents = {'RESULT.json':dict(context,schema='dg16.installed-runtime-result.v1',status='UNQUALIFIED',
            source_commit=SOURCE_COMMIT,source_tree=SOURCE_TREE,original_acceptance=False,audit_closure=False,
            fallback=True,private_outputs_uploaded=False,authority='NONE'),
            'FAILURE.json':{'schema':'dg16.installed-runtime-failure.v1','present':True,'fallback':True,'code':code,
                'exception_type':type(exc).__name__ if type(exc).__name__ in EXCEPTIONS else 'OTHER',
                'withheld_diagnostic_bytes':len(str(exc).encode('utf-8','replace')),
                'withheld_diagnostic_sha256':digest(str(exc).encode('utf-8','replace')),'raw_diagnostics_private':True}}
        files,lines = build_transport(documents)
    public = output / 'public'; need(not public.exists(), 'PUBLIC_EMIT_REPLAY_REFUSED')
    public.mkdir(mode=0o700)
    for name,raw in files.items(): h.write_private(public / name,raw)
    need({path.name for path in public.iterdir()} == set(files), 'PUBLIC_READBACK_POPULATION_REFUSED')
    for name,raw in files.items(): need(installed.regular(public / name,FILE_LIMIT) == raw, 'PUBLIC_READBACK_BYTES_REFUSED')
    # All raw bodies, encoded envelopes, aggregate caps and exact population have
    # passed before this first external line. Workflow eligibility follows exit 0.
    for line in lines: sys.stdout.buffer.write(line)
    sys.stdout.buffer.flush()
    return 0


def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--step',choices=(*STEPS,'finalize'))
    group.add_argument('--emit-public',action='store_true')
    parser.add_argument('--source',type=Path,required=True); parser.add_argument('--output',type=Path,required=True)
    args = parser.parse_args()
    try:
        u = load_module('host_utility',UTILITY_SHA)
        h = load_module('host_support',SUPPORT_SHA)
        installed = load_module('installed_runtime',INSTALLED_SHA)
        if args.emit_public: return emit(args.source.absolute(),args.output.absolute(),u,h,installed)
        return execute(args.step,args.source.absolute(),args.output.absolute(),u,h,installed)
    except BaseException:
        # No raw exception, path, controller/ref name or captured body reaches the
        # public log even if bootstrap or final state persistence itself failed.
        sys.stdout.write('DG16_INSTALLED_RUNTIME_STATUS {"status":"UNQUALIFIED","code":"ADAPTER_CLOSED_REFUSAL","authority":"NONE"}\n')
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
