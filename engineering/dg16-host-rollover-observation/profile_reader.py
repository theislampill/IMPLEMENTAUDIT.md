#!/usr/bin/env python3
"""Bounded new-run observations only. No original code, command or authority."""
import errno
import hashlib
import json
import os
from pathlib import Path
import re
import signal
import stat
import sys
import time

REPOSITORY = 'theislampill/IMPLEMENTAUDIT.md'
BRANCH = 'pro/dg16-g132-profile-diagnostic-20261121-01'
WORKFLOW = '.github/workflows/dg16-g132-host-profile-diagnostic.yml'
COLLECTOR = 'engineering/g132-profile-diagnostic/collect_profile.py'
BASELINE = 'engineering/g132-profile-diagnostic/REVIEWED_BASELINE.json'
BASELINE_SHA256 = '32bb2ff37dc01eae33960c0df95f187be9ff15c815eb6c3b51ac5dfaa90655f1'
TOOLS = ('python3.12', 'git', 'bash', 'bwrap', 'env', 'openssl')
MAXIMUM_READ = 128 * 1024 * 1024
MAXIMUM_TOOL = 64 * 1024 * 1024
MAXIMUM_OUTPUT = 65536
DEADLINE_SECONDS = 60

class Refusal(ValueError):
    pass

def need(condition, code):
    if not condition:
        raise Refusal(code)

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

class Budget:
    def __init__(self, maximum=MAXIMUM_READ, seconds=DEADLINE_SECONDS):
        self.maximum = maximum
        self.used = 0
        self.deadline = time.monotonic() + seconds

    def check(self):
        need(time.monotonic() < self.deadline, 'DEADLINE')

    def spend(self, count):
        self.check()
        need(type(count) is int and count >= 0 and self.used + count <= self.maximum, 'READ_BUDGET')
        self.used += count

def mark(value):
    return {name: getattr(value, 'st_' + name) for name in
            ('dev', 'ino', 'mode', 'nlink', 'uid', 'gid', 'size', 'mtime_ns', 'ctime_ns')}

def xattr_summary(path_or_fd):
    names = os.listxattr(path_or_fd)
    encoded = [name.encode('utf8', 'surrogateescape') for name in names]
    need(len(encoded) <= 32 and all(len(name) <= 255 for name in encoded)
         and sum(map(len, encoded)) <= 4096, 'XATTR_BOUND')
    return {'count': len(names), 'name_sha256': sorted(sha(name) for name in encoded),
            'posix_acl_present': any(name in ('system.posix_acl_access', 'system.posix_acl_default') for name in names),
            'security_capability_present': 'security.capability' in names}

def read_file(path, maximum, budget, allowed_roots, *, retain=False):
    """Read a fixed caller-selected public file; no traversal or discovery."""
    budget.check()
    path = Path(path).absolute()
    requested_mark = mark(path.lstat())
    target = path.resolve(strict=True)
    need(any(target.is_relative_to(Path(root).resolve(strict=True)) for root in allowed_roots), 'PATH_SCOPE')
    before = target.lstat()
    need(stat.S_ISREG(before.st_mode) and 0 <= before.st_size <= maximum, 'FILE_BOUND')
    need(budget.used + before.st_size + 1 <= budget.maximum, 'READ_BUDGET')
    ancestors = [{'path': str(parent), 'stat': mark(parent.lstat()), 'xattrs': xattr_summary(parent)} for parent in target.parents]
    need(all(stat.S_ISDIR(row['stat']['mode']) for row in ancestors), 'PATH_SCOPE')
    fd = os.open(target, os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW | os.O_NONBLOCK)
    chunks = []
    digest = hashlib.sha256()
    total = 0
    try:
        need(mark(os.fstat(fd)) == mark(before), 'FILE_CHANGED')
        while True:
            budget.check()
            raw = os.read(fd, min(1024 * 1024, maximum + 1 - total, budget.maximum - budget.used))
            if not raw:
                break
            budget.spend(len(raw)); total += len(raw)
            need(total <= maximum, 'FILE_BOUND')
            digest.update(raw)
            if retain:
                chunks.append(raw)
        try:
            cap = os.getxattr(fd, 'security.capability')
        except OSError as exc:
            need(exc.errno in (errno.ENODATA, errno.ENOTSUP), 'CAPABILITY_UNKNOWN')
            cap = b''
        xattrs = xattr_summary(fd)
        need(total == before.st_size and mark(os.fstat(fd)) == mark(before)
             and mark(target.lstat()) == mark(before) and path.resolve(strict=True) == target
             and mark(path.lstat()) == requested_mark, 'FILE_CHANGED')
    finally:
        os.close(fd)
    row = {'requested': str(path), 'canonical': str(target), 'requested_stat': requested_mark,
           'bytes': total, 'sha256': digest.hexdigest(), 'stat': mark(before), 'ancestors': ancestors,
           'xattrs': xattrs,
           'capability': {'observed': True, 'present': bool(cap), 'bytes': len(cap), 'sha256': sha(cap)}}
    close_file(row)
    return row, b''.join(chunks) if retain else None

def close_file(row):
    try:
        requested = Path(row['requested']); target = Path(row['canonical'])
        need(requested.resolve(strict=True) == target and mark(requested.lstat()) == row['requested_stat']
             and mark(target.lstat()) == row['stat']
             and xattr_summary(target) == row['xattrs']
             and all(mark(Path(p['path']).lstat()) == p['stat'] and xattr_summary(Path(p['path'])) == p['xattrs']
                     for p in row['ancestors']), 'FILE_CHANGED')
    except OSError:
        raise Refusal('FILE_CHANGED') from None

def tool_verdict(file_mark, ancestors, capabilities_present, execute_access):
    chain_ok = file_mark['uid'] == 0 and not file_mark['mode'] & 0o022
    chain_ok = bool(chain_ok and all(r['stat']['uid'] == 0 and not r['stat']['mode'] & 0o022 for r in ancestors))
    privileged = bool(file_mark['mode'] & 0o6000 or capabilities_present)
    executable = bool(file_mark['mode'] & 0o111)
    return {'root_owned_nonwritable_chain': chain_ok, 'setid_or_file_capabilities': privileged,
            'executable_mode': executable, 'execute_access': execute_access,
            'trusted_file_custody': chain_ok and not privileged and executable and execute_access}

def observe_tool(path, budget, allowed_roots):
    try:
        row, _ = read_file(path, MAXIMUM_TOOL, budget, allowed_roots)
    except FileNotFoundError as exc:
        return {'requested': str(path), 'available': False, 'code': 'FILE_UNAVAILABLE', 'errno': exc.errno}
    row.update(available=True, **tool_verdict(row['stat'], row['ancestors'], row['capability']['present'],
                                            os.access(row['canonical'], os.X_OK)))
    return row

def close_tool(row):
    if row['available']:
        close_file(row)
        need(os.access(row['canonical'], os.X_OK) == row['execute_access'], 'FILE_CHANGED')
        return
    try:
        Path(row['requested']).resolve(strict=True)
    except FileNotFoundError:
        return
    raise Refusal('TOOL_AVAILABILITY_CHANGED')

def profile_facts(release_raw, platform_value, machine, version, environment, credentials):
    """Faithful ten-field projection of the reviewed read-only observer."""
    release = {}
    for line in release_raw.decode('utf8').splitlines():
        if '=' in line:
            key, value = line.split('=', 1)
            if key in ('ID', 'VERSION_ID'):
                release[key] = value.strip('"')
    need(set(release) == {'ID', 'VERSION_ID'} and
         all(type(v) is str and re.fullmatch('[A-Za-z0-9._-]{1,32}', v) for v in release.values()), 'FACT_SHAPE')
    need(type(platform_value) is str and re.fullmatch('[a-z0-9_-]{1,32}', platform_value)
         and type(machine) is str and re.fullmatch('[A-Za-z0-9_-]{1,64}', machine), 'FACT_SHAPE')
    need(len(version) == 3 and all(type(v) is int and 0 <= v < 10000 for v in version)
         and len(credentials) == 4 and all(type(v) is int and 0 <= v < 2**32 for v in credentials), 'FACT_SHAPE')
    image_os = environment.get('ImageOS', ''); image_version = environment.get('ImageVersion', '')
    need(type(image_os) is str and re.fullmatch('ubuntu[0-9]{2}', image_os)
         and type(image_version) is str and re.fullmatch('[0-9]{8}\\.[0-9]{1,8}\\.[0-9]{1,4}', image_version), 'FACT_SHAPE')
    return {'platform': platform_value, 'architecture': machine, 'os': release,
            'python_version': list(version), 'image_os': image_os, 'image_version': image_version,
            **dict(zip(('uid', 'euid', 'gid', 'egid'), credentials))}

def compare_profile(facts, baseline):
    comparisons = []
    for profile in baseline['profiles']:
        wanted = profile['facts']
        differences = sorted(k for k in set(facts) | set(wanted)
                             if k not in facts or k not in wanted or type(facts[k]) is not type(wanted[k]) or facts[k] != wanted[k])
        comparisons.append({'profile_id': profile['id'], 'different_fields': differences})
    matches = [r['profile_id'] for r in comparisons if not r['different_fields']]
    return {'classification': 'MATCHES_REVIEWED_PROFILE' if len(matches) == 1 else 'OUTSIDE_REVIEWED_PROFILES',
            'matching_profile_ids': matches, 'profiles': comparisons,
            'native_qualification': False, 'original_acceptance': False, 'original_awards': []}

def validate_context(env):
    fixed = {'GITHUB_ACTIONS': 'true', 'RUNNER_ENVIRONMENT': 'github-hosted',
             'GITHUB_REPOSITORY': REPOSITORY, 'GITHUB_REF': 'refs/heads/' + BRANCH,
             'GITHUB_RUN_ATTEMPT': '1', 'GITHUB_EVENT_NAME': 'push', 'GITHUB_JOB': 'observe',
             'GITHUB_WORKFLOW_REF': REPOSITORY + '/' + WORKFLOW + '@refs/heads/' + BRANCH}
    need(all(env.get(k) == v for k, v in fixed.items()), 'DIAGNOSTIC_CONTEXT')
    head = env.get('GITHUB_SHA', '')
    need(type(head) is str and re.fullmatch('[0-9a-f]{40}', head)
         and env.get('GITHUB_WORKFLOW_SHA') == head
         and head not in ('b393a9057c249335e6cdf4ccbb898d192b0830b8', '301aeecde08ba6f169bc3cd837eae6f6ad068219'), 'DIAGNOSTIC_CONTEXT')
    run = env.get('GITHUB_RUN_ID', ''); pin = env.get('EXPECTED_COLLECTOR_SHA256', '')
    need(type(run) is str and re.fullmatch('[1-9][0-9]{0,19}', run)
         and type(pin) is str and re.fullmatch('[0-9a-f]{64}', pin), 'DIAGNOSTIC_CONTEXT')
    return {'repository': REPOSITORY, 'ref': fixed['GITHUB_REF'], 'run_id': run, 'run_attempt': 1,
            'event': 'push', 'job': 'observe', 'head_sha': head, 'workflow_sha': head,
            'workflow_ref': fixed['GITHUB_WORKFLOW_REF'], 'expected_collector_sha256': pin}

def validate_checkout_head(raw, context):
    need(type(raw) is bytes and raw == (context['head_sha'] + '\n').encode('ascii'), 'CHECKOUT_HEAD_CHANGED')
    return context['head_sha']

def require_digest(row, expected):
    need(row.get('sha256') == expected, 'SOURCE_PIN')

def validate_boot_identity(raw):
    need(type(raw) is bytes and re.fullmatch(b'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\n', raw), 'BOOT_ID_VALUE')
    return raw

def read_boot_identity(budget):
    """Faithful bounded procfs reader; no size-zero ordinary-file shortcut."""
    path = Path('/proc/sys/kernel/random/boot_id')
    def identity(s):
        return (s.st_dev, s.st_ino, s.st_mode, s.st_nlink, s.st_size, s.st_uid, s.st_gid)
    for parent in reversed(path.parents):
        info = parent.lstat()
        need(stat.S_ISDIR(info.st_mode) and not stat.S_ISLNK(info.st_mode)
             and info.st_uid == 0 and not info.st_mode & 0o022, 'BOOT_ID_SHAPE')
    before = path.lstat()
    need(stat.S_ISREG(before.st_mode) and before.st_nlink == 1 and before.st_size == 0
         and before.st_uid == before.st_gid == 0 and stat.S_IMODE(before.st_mode) == 0o444, 'BOOT_ID_SHAPE')
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK | os.O_CLOEXEC)
    try:
        need(identity(os.fstat(fd)) == identity(before), 'BOOT_ID_CHANGED')
        first = validate_boot_identity(os.read(fd, 129)); budget.spend(len(first))
        need(os.lseek(fd, 0, os.SEEK_SET) == 0, 'BOOT_ID_CHANGED')
        second = os.read(fd, 129); budget.spend(len(second))
        need(first == second and identity(os.fstat(fd)) == identity(before)
             and identity(path.lstat()) == identity(before), 'BOOT_ID_CHANGED')
        return first
    finally:
        os.close(fd)

def capture_facts(budget):
    row, raw = read_file(Path('/etc/os-release'), 16384, budget, (Path('/etc'), Path('/usr/lib')), retain=True)
    facts = profile_facts(raw, sys.platform, os.uname().machine, sys.version_info[:3],
                          os.environ, (os.getuid(), os.geteuid(), os.getgid(), os.getegid()))
    return facts, row

def main():
    need(len(sys.argv) == 1 and sys.flags.isolated == 1 and sys.dont_write_bytecode is True, 'ISOLATED_ENTRY')
    context = validate_context(os.environ)
    need(sys.platform == 'linux' and os.getuid() == os.geteuid() == os.getgid() == os.getegid() == 0, 'ROOT_OBSERVER_REQUIRED')
    def expired(_sig, _frame):
        raise Refusal('DEADLINE')
    signal.signal(signal.SIGALRM, expired); signal.alarm(DEADLINE_SECONDS)
    budget = Budget(); started_ns = time.time_ns()
    workspace = Path(os.environ.get('GITHUB_WORKSPACE', '')).absolute()
    need(workspace.is_absolute() and workspace.resolve(strict=True) == workspace
         and Path(__file__).absolute() == workspace / COLLECTOR, 'SOURCE_LOCATION')
    source = {}; baseline = None
    for role, relative, maximum in (('collector', COLLECTOR, 65536), ('baseline', BASELINE, 16384),
                                    ('workflow', WORKFLOW, 65536), ('checkout_head', '.git/HEAD', 128)):
        row, raw = read_file(workspace / relative, maximum, budget, (workspace,), retain=True)
        need(Path(row['requested']) == Path(row['canonical']), 'SOURCE_LOCATION')
        source[role] = row
        if role == 'collector':
            require_digest(row, context['expected_collector_sha256'])
        elif role == 'baseline':
            require_digest(row, BASELINE_SHA256); baseline = json.loads(raw)
        elif role == 'checkout_head':
            validate_checkout_head(raw, context)
    facts, os_release = capture_facts(budget)
    boot_raw = read_boot_identity(budget)
    tools = {name: observe_tool(Path('/usr/bin') / name, budget, (Path('/usr'),)) for name in TOOLS}
    interpreter = tools['python3.12']
    need(interpreter.get('available') is True and Path(sys.executable).resolve(strict=True) == Path(interpreter['canonical']), 'INTERPRETER_IDENTITY')
    closing_facts, closing_release = capture_facts(budget)
    need(closing_facts == facts and closing_release == os_release and read_boot_identity(budget) == boot_raw, 'OBSERVATION_CHANGED')
    for row in (*source.values(), os_release):
        close_file(row)
    for row in tools.values():
        close_tool(row)
    need(validate_context(os.environ) == context, 'DIAGNOSTIC_CONTEXT')
    budget.check()
    comparisons = {}
    for name in ('python3.12', 'git', 'bwrap'):
        actual = tools[name]
        comparisons[name] = {'observed_sha256': actual.get('sha256'),
                             'matches_reviewed_profiles': [p['id'] for p in baseline['profiles']
                               if actual.get('available') and actual['sha256'] == p['core_tool_sha256'][name]]}
    value = {'schema': 'g132.nonprotected-host-profile-observation.v1', 'authority': 'NONE',
             'status': 'CAPTURED_UNQUALIFIED', 'diagnostic_only': True, 'new_run_observation_only': True,
             'context': context, 'source': source, 'facts': facts, 'os_release': os_release,
             'boot_identity_sha256': sha(boot_raw), 'interpreter_canonical': str(Path(sys.executable).resolve(strict=True)),
             'tools': tools, 'profile_comparison': compare_profile(facts, baseline), 'core_tool_comparison': comparisons,
             'opening_unix_ns': started_ns, 'closing_unix_ns': time.time_ns(),
             'limits': {'deadline_seconds': DEADLINE_SECONDS, 'maximum_tool_bytes': MAXIMUM_TOOL,
                        'maximum_total_read_bytes': MAXIMUM_READ, 'actual_read_bytes': budget.used,
                        'maximum_output_bytes': MAXIMUM_OUTPUT},
             'closing_unchanged': True, 'commands_executed': [], 'network_calls': 0,
             'original_subject_used': False, 'native_qualification': False, 'original_acceptance': False,
             'private_inputs_read': False, 'original_awards': []}
    raw = (json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n').encode()
    need(len(raw) <= MAXIMUM_OUTPUT, 'OUTPUT_BOUND')
    sys.stdout.buffer.write(raw); sys.stdout.buffer.flush()
    signal.alarm(0)
    return 0

if __name__ == '__main__':
    try:
        code = main()
    except BaseException as exc:
        reason = exc.args[0] if type(exc) is Refusal and len(exc.args) == 1 else 'UNCLASSIFIED_DIAGNOSTIC_REFUSAL'
        print(json.dumps({'schema': 'g132.nonprotected-host-profile-refusal.v1', 'authority': 'NONE',
                          'status': 'REFUSED', 'code': reason, 'native_qualification': False,
                          'original_acceptance': False, 'original_awards': []}, sort_keys=True))
        code = 1
    raise SystemExit(code)
