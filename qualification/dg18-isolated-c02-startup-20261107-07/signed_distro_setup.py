#!/usr/bin/env python3
"""Optional finite signed Ubuntu package setup for a reviewed disposable host.

This is never called by author qualification. Caller must authorize hosted
preparation separately. Does not repair modes/ownership, change LSM/sysctls or
relax apt authentication. Native startup remains a later one-shot operation.
"""
from pathlib import Path
import os
import copy
import stat
import re
import tempfile
import importlib.util
import sys
import bwrap_host as host


def _load_transaction_guard():
    # The retained adapter runs Python with -I, excluding the checkout from
    # sys.path. Load only the adjacent manifest-bound helper by absolute path.
    path = Path(__file__).resolve().with_name('apt_transaction_guard.py')
    spec = importlib.util.spec_from_file_location('apt_transaction_guard', path)
    module = importlib.util.module_from_spec(spec)
    sys.modules['apt_transaction_guard'] = module
    spec.loader.exec_module(module)
    return module


gate = _load_transaction_guard()

# Independent fixed public anchor, selected from Canonical's immutable Noble
# source. No installed keyring, keyserver, environment override or fallback.
PUBLIC_ARCHIVE_KEY = b'''-----BEGIN PGP PUBLIC KEY BLOCK-----

mQINBFufwdoBEADv/Gxytx/LcSXYuM0MwKojbBye81s0G1nEx+lz6VAUpIUZnbkq
dXBHC+dwrGS/CeeLuAjPRLU8AoxE/jjvZVp8xFGEWHYdklqXGZ/gJfP5d3fIUBtZ
HZEJl8B8m9pMHf/AQQdsC+YzizSG5t5Mhnotw044LXtdEEkx2t6Jz0OGrh+5Ioxq
X7pZiq6Cv19BohaUioKMdp7ES6RYfN7ol6HSLFlrMXtVfh/ijpN9j3ZhVGVeRC8k
KHQsJ5PkIbmvxBiUh7SJmfZUx0IQhNMaDHXfdZAGNtnhzzNReb1FqNLSVkrS/Pns
AQzMhG1BDm2VOSF64jebKXffFqM5LXRQTeqTLsjUbbrqR6s/GCO8UF7jfUj6I7ta
LygmsHO/JD4jpKRC0gbpUBfaiJyLvuepx3kWoqL3sN0LhlMI80+fA7GTvoOx4tpq
VlzlE6TajYu+jfW3QpOFS5ewEMdL26hzxsZg/geZvTbArcP+OsJKRmhv4kNo6Ayd
yHQ/3ZV/f3X9mT3/SPLbJaumkgp3Yzd6t5PeBu+ZQk/mN5WNNuaihNEV7llb1Zhv
Y0Fxu9BVd/BNl0rzuxp3rIinB2TX2SCg7wE5xXkwXuQ/2eTDE0v0HlGntkuZjGow
DZkxHZQSxZVOzdZCRVaX/WEFLpKa2AQpw5RJrQ4oZ/OfifXyJzP27o03wQARAQAB
tEJVYnVudHUgQXJjaGl2ZSBBdXRvbWF0aWMgU2lnbmluZyBLZXkgKDIwMTgpIDxm
dHBtYXN0ZXJAdWJ1bnR1LmNvbT6JAjgEEwEKACIFAlufwdoCGwMGCwkIBwMCBhUI
AgkKCwQWAgMBAh4BAheAAAoJEIcZINGZG8k8LHMQAKS2cnxz/5WaoCOWArf5g6UH
beOCgc5DBm0hCuFDZWWv427aGei3CPuLw0DGLCXZdyc5dqE8mvjMlOmmAKKlj1uG
g3TYCbQWjWPeMnBPZbkFgkZoXJ7/6CB7bWRht1sHzpt1LTZ+SYDwOwJ68QRp7DRa
Zl9Y6QiUbeuhq2DUcTofVbBxbhrckN4ZteLvm+/nG9m/ciopc66LwRdkxqfJ32Cy
q+1TS5VaIJDG7DWziG+Kbu6qCDM4QNlg3LH7p14CrRxAbc4lvohRgsV4eQqsIcdF
kuVY5HPPj2K8TqpY6STe8Gh0aprG1RV8ZKay3KSMpnyV1fAKn4fM9byiLzQAovC0
LZ9MMMsrAS/45AvC3IEKSShjLFn1X1dRCiO6/7jmZEoZtAp53hkf8SMBsi78hVNr
BumZwfIdBA1v22+LY4xQK8q4XCoRcA9G+pvzU9YVW7cRnDZZGl0uwOw7z9PkQBF5
KFKjWDz4fCk+K6+YtGpovGKekGBb8I7EA6UpvPgqA/QdI0t1IBP0N06RQcs1fUaA
QEtz6DGy5zkRhR4pGSZn+dFET7PdAjEK84y7BdY4t+U1jcSIvBj0F2B7LwRL7xGp
SpIKi/ekAXLs117bvFHaCvmUYN7JVp1GMmVFxhIdx6CFm3fxG8QjNb5tere/YqK+
uOgcXny1UlwtCUzlrSaP
=9AdM
-----END PGP PUBLIC KEY BLOCK-----
'''
_SIGNED_BY = b'Signed-By:\n' + b''.join(
    b'  ' + (line if line else b'.') + b'\n' for line in PUBLIC_ARCHIVE_KEY.splitlines())
SOURCES = (b'Types: deb\nURIs: https://archive.ubuntu.com/ubuntu\nSuites: noble noble-updates\nComponents: main universe\nArchitectures: amd64\n' + _SIGNED_BY + b'\n' +
           b'Types: deb\nURIs: https://security.ubuntu.com/ubuntu\nSuites: noble-security\nComponents: main universe\nArchitectures: amd64\n' + _SIGNED_BY)
SYSTEM_TOOL_PATHS = (
    '/usr/bin/sudo', '/usr/bin/env', '/usr/bin/apt-get', '/usr/bin/apt-cache',
    '/usr/bin/dpkg-query', '/usr/bin/rm', '/usr/bin/dpkg', '/usr/bin/python3',
    '/bin/sh', '/usr/lib/x86_64-linux-gnu/libapt-pkg.so.6.0')
VERSION = r'[A-Za-z0-9.+:~\-]+'


def trust_anchor():
    """Fixed public provenance; exact runtime bytes, not key-signature verification."""
    host.need(type(PUBLIC_ARCHIVE_KEY) is bytes and len(PUBLIC_ARCHIVE_KEY) == 1660 and
              host.sha(PUBLIC_ARCHIVE_KEY) == '2a3cc57ab6b47626b496a101c29af6dfe54d54d03d613f2326b9f2a30a15c39b',
              'APT_EMBEDDED_ANCHOR_CHANGED')
    host.need(type(SOURCES) is bytes and len(SOURCES) == 3709 and
              host.sha(SOURCES) == 'e0a23d9fefd3b90e9f92c70ea21c5583a61f013190c4f4612fd8d51f919f61f0',
              'APT_FIXED_SOURCES_CHANGED')
    return {'schema': 'dg18.c02.embedded-archive-trust-anchor.v1',
        'kind': 'EXACT_EMBEDDED_SIGNED_BY_PUBLIC_ARCHIVE_KEY',
        'repository': 'canonical/chisel-releases',
        'commit': '23bf48f85a7f92a5ce58308cea0ca2aebc092eb1',
        'source_blob': '205608959a4ad6f122ec9830779c829fc6ac5221',
        'source_sha256': '954a98ea87100fd0e892f2933c7f6832b8b85608e2bc55db3ee60f01de7f1ebf',
        'key_selection': 'ubuntu-archive-key-2018', 'armor_bytes': 1660,
        'armor_sha256': '2a3cc57ab6b47626b496a101c29af6dfe54d54d03d613f2326b9f2a30a15c39b',
        'fingerprint': 'F6ECB3762474EDA9D21B7022871920D1991BC93C',
        'key_packet_version': 4, 'algorithm': 'RSA', 'rsa_bits': 4096}


def validate_trust_anchor(anchor):
    expected = trust_anchor()
    host.need(type(anchor) is dict and all(type(key) is str for key in anchor) and
              set(anchor) == set(expected), 'APT_TRUST_ANCHOR_DESCRIPTOR')
    host.need(all(type(anchor[key]) is type(value) and anchor[key] == value
                  for key, value in expected.items()), 'APT_TRUST_ANCHOR_DESCRIPTOR')


def validate_system_tools(system):
    host.need(type(system) is dict and all(type(path) is str for path in system) and
              set(system) == set(SYSTEM_TOOL_PATHS), 'APT_SYSTEM_TOOL_POPULATION')
    host.need(all(type(system[path]) is dict and type(system[path].get('invocation')) is str and
                  system[path]['invocation'] == path for path in SYSTEM_TOOL_PATHS),
              'APT_SYSTEM_TOOL_IDENTITY')


def parse_candidate(raw):
    candidates = re.findall(rb'^\s*Candidate:\s*(\S+)\s*$', raw, re.M)
    host.need(len(candidates) == 1 and re.fullmatch(VERSION, candidates[0].decode('ascii')), 'APT_CANDIDATE')
    return candidates[0].decode()


def validate_simulation(raw, version):
    host.need(re.fullmatch(VERSION, version), 'APT_VERSION')
    rows = [line.strip() for line in raw.decode('ascii', 'strict').splitlines()
            if re.match(r'^(Inst|Conf|Remv)\s', line)]
    pattern = r'(Inst|Conf) bubblewrap \(' + re.escape(version) + r' [^\n]+ \[amd64\]\)'
    host.need(len(rows) == 2 and [re.fullmatch(pattern, x).group(1) if re.fullmatch(pattern, x) else None for x in rows]
              == ['Inst', 'Conf'], 'APT_TRANSACTION_NOT_SINGLE_NEW_PACKAGE')
    return {'install': ['bubblewrap=' + version], 'remove': [], 'upgrade': []}


def apt_argv(config, operation, version=None):
    host.need(operation in ('update', 'simulate', 'install', 'policy'), 'APT_OPERATION')
    base = ['/usr/bin/apt-cache' if operation == 'policy' else '/usr/bin/apt-get', '-c', str(config)]
    if operation == 'policy':
        return base + ['policy', 'bubblewrap']
    if operation == 'update':
        return base + ['update', '--error-on=any']
    host.need(type(version) is str and re.fullmatch(VERSION, version), 'APT_VERSION')
    return base + (['--simulate'] if operation == 'simulate' else []) + [
        '--assume-yes', '--no-install-recommends', '--no-upgrade', '--no-remove', 'install', 'bubblewrap=' + version]


def write_new(path, raw, mode=0o644):
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, mode)
    with os.fdopen(fd, 'wb') as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())


def require_same_cleanup_tool(expected, observed):
    """Keep exact tool identity and ancestry after the authorized package write.

    Package installation may add a directory entry to /usr/bin. Only directory
    size/mtime/ctime are allowed to differ for cleanup. Device, inode, type,
    mode, owner/group, links, symlink targets and every tool byte remain bound.
    This exception never applies to native startup or bwrap admission.
    """
    left, right = copy.deepcopy(expected), copy.deepcopy(observed)
    host.need(set(left['path_chain']) == set(right['path_chain']), 'APT_CLEANUP_TOOL_CHAIN')
    for name in left['path_chain']:
        old, new = left['path_chain'][name]['identity'], right['path_chain'][name]['identity']
        if stat.S_ISDIR(old[2]) and stat.S_ISDIR(new[2]):
            old[6:] = new[6:] = [None, None, None]
    host.same_binding(left, right)


def transaction_request(directory, config, source, system, anchor, prestate, version, helper_binding):
    """Pure rendering of the exact request; no package or process effect."""
    validate_trust_anchor(anchor)
    validate_system_tools(system)
    request = {
        'schema': gate.SCHEMA, 'version': version, 'architecture': 'amd64',
        'apt_version': gate.require_supported_apt(prestate), 'prestate': prestate,
        'directory': str(directory), 'directory_identity': host.identity(directory.lstat())[:2],
        'owner_uid': os.getuid(), 'request_path': str(directory / 'TRANSACTION_REQUEST.json'),
        'base_config_path': str(directory / 'apt.conf'), 'base_config': config.decode(),
        'install_config_path': str(directory / 'install.conf'),
        'source_path': str(source), 'source': SOURCES.decode(),
        'trust_anchor': dict(anchor), 'sources_sha256': host.sha(SOURCES),
        'helper_path': helper_binding['path'], 'helper_sha256': helper_binding['sha256'],
        'apt_argv': apt_argv(directory / 'install.conf', 'install', version),
        'tools': dict(system),
        'dpkg_configuration': gate.dpkg_configuration(),
        'critical_config': {
            'Dir::Etc::main': '/dev/null', 'Dir::Etc::parts': '/dev/null',
            'Dir::Etc::sourcelist': str(source), 'Dir::Etc::sourceparts': '-',
            'Dir::Etc::trusted': '/dev/null', 'Dir::Etc::trustedparts': '-',
            'Dir::State::status': '/var/lib/dpkg/status', 'Dir::Bin::dpkg': '/usr/bin/dpkg',
            'Dir::State::lists': str(directory / 'lists'),
            'Dir::Cache::archives': str(directory / 'archives'),
            'APT::Get::AllowUnauthenticated': 'false', 'Acquire::AllowInsecureRepositories': 'false',
            'Acquire::AllowDowngradeToInsecureRepositories': 'false', 'Acquire::Check-Valid-Until': 'true',
            'Acquire::Retries': '0', 'Acquire::http::Timeout': '30', 'Acquire::https::Timeout': '30',
            'Dpkg::Use-Pty': '0', 'APT::Color': 'false',
            'DPkg::Tools::Options::/usr/bin/python3::Version': '3',
            'DPkg::Tools::Options::/usr/bin/python3::InfoFD': '0',
        },
    }
    return request


def receive_transaction(directory, request, request_sha):
    """Join root-owned PRE and POST receipts; derive count from actual state."""
    pre, pre_sha = gate.load_receipt(directory / 'PRE_DPKG.json')
    post, post_sha = gate.load_receipt(directory / 'POST_DPKG.json')
    host.need(pre['schema'] == 'dg18.c02.apt-before-dpkg.v1' and
              post['schema'] == 'dg18.c02.apt-after-dpkg.v1' and
              pre['status'] == 'EXACT_ACTUAL_TRANSACTION_ADMITTED' and
              post['status'] == 'EXACT_ACTUAL_EFFECTS_RECONCILED' and
              pre['request_sha256'] == post['request_sha256'] == request_sha and
              post['pre_receipt_sha256'] == pre_sha and
              pre['apt_process'] == post['apt_process'] and
              pre['prestate_sha256'] == request['prestate']['records_sha256'], 'APT_GATE_RECEIPT_JOIN')
    expected = {'install': ['bubblewrap=' + request['version']], 'upgrade': [], 'remove': [],
                'unchanged_package_count': len(request['prestate']['records']), 'install_count': 1}
    host.need(post['effects'] == expected and
              all(pre['transaction'][key] == expected[key] for key in ('install', 'upgrade', 'remove')),
              'APT_GATE_RECEIPT_EFFECTS')
    # A writer can start after apt releases the lock. Refuse preparation if its
    # current state no longer matches the lock-held completion receipt.
    observed = gate.read_snapshot()
    host.need(observed['records_sha256'] == post['poststate_sha256'] and
              gate.reconcile(request['prestate'], observed, request['version']) == post['effects'],
              'APT_GATE_RECEIVING_STATE_CHANGED')
    return {'status': 'ACTUAL_TRANSACTION_AND_EFFECTS_JOINED', 'effects': post['effects'],
            'request_sha256': request_sha, 'pre_receipt_sha256': pre_sha,
            'post_receipt_sha256': post_sha, 'poststate_sha256': post['poststate_sha256'],
            'protocol_sha256': pre['transaction']['protocol_sha256'],
            'archive_sha256': pre['transaction']['archive_sha256'], 'apt_version': request['apt_version']}


def install_if_missing(work):
    """Actual setup entry, only from fresh root-approved hosted preparation."""
    host.os_release()
    if os.path.lexists(host.BWRAP):
        return {'status': 'EXISTING_SYSTEM_PACKAGE_NO_INSTALL', 'install_count': 0,
                'provenance': 'HOST_PACKAGE_RECORD_PENDING_INDEPENDENT_RECEIVING'}
    helper = Path(__file__).resolve().with_name('apt_transaction_guard.py')
    helper_raw, _ = gate.read_regular(helper, 131072, owner=os.getuid())
    helper_binding = {'path': str(helper), 'sha256': host.sha(helper_raw)}
    system = {p: host.protected_file(p, executable=True) for p in
              ('/usr/bin/sudo', '/usr/bin/env', '/usr/bin/apt-get', '/usr/bin/apt-cache',
               '/usr/bin/dpkg-query', '/usr/bin/rm', '/usr/bin/dpkg', '/usr/bin/python3', '/bin/sh')}
    system['/usr/lib/x86_64-linux-gnu/libapt-pkg.so.6.0'] = host.protected_file(
        '/usr/lib/x86_64-linux-gnu/libapt-pkg.so.6.0')
    anchor = trust_anchor()
    status = host.run_bounded(['/usr/bin/dpkg-query', '-W', '-f=${db:Status-Abbrev}', 'bubblewrap'], timeout=10, limit=65536)
    host.need(status['returncode'] == 1 and status['stdout'] == b'' and status['cleanup'] == 'CLOSED'
              and not status['timed_out'] and not status['overflow'], 'APT_EXISTING_PACKAGE_INCONSISTENT')
    private = Path(work) / 'system-setup-private'
    private.mkdir(mode=0o700)
    directory = Path(tempfile.mkdtemp(prefix='dg18-c02-apt-', dir='/tmp'))
    # Only this newly owned, nonsecret apt workspace is traversable by _apt.
    directory.chmod(0o755)
    cfg = directory / 'apt.conf'
    source = directory / 'ubuntu.sources'
    config = (f'Dir::Etc::main "/dev/null";\nDir::Etc::parts "/dev/null";\n'
              f'Dir::Etc::sourcelist "{source}";\nDir::Etc::sourceparts "-";\n'
              f'Dir::Etc::trusted "/dev/null";\nDir::Etc::trustedparts "-";\n'
              f'Dir::State::lists "{directory}/lists";\nDir::Cache::archives "{directory}/archives";\n'
              'APT::Get::AllowUnauthenticated "false";\nAcquire::AllowInsecureRepositories "false";\n'
              'Acquire::AllowDowngradeToInsecureRepositories "false";\nAcquire::Check-Valid-Until "true";\n'
              'Acquire::Retries "0";\nAcquire::http::Timeout "30";\nAcquire::https::Timeout "30";\n'
              'Dpkg::Use-Pty "0";\nAPT::Color "false";\n').encode()
    write_new(source, SOURCES)
    write_new(cfg, config)
    (directory / 'lists').mkdir(mode=0o755)
    (directory / 'archives').mkdir(mode=0o755)
    directory_id = host.identity(directory.lstat())[:2]
    transcript = []
    install_cfg, actual_config = None, None
    def run(operation, version=None):
        host.need(cfg.read_bytes() == config and source.read_bytes() == SOURCES, 'APT_INPUT_CHANGED')
        gate.read_regular(helper_binding['path'], 131072, owner=os.getuid(), digest=helper_binding['sha256'])
        if operation == 'install':
            host.need(install_cfg is not None and install_cfg.read_bytes() == actual_config,
                      'APT_INSTALL_CONFIG_CHANGED')
        for path, binding in system.items():
            host.same_binding(binding, host.protected_file(path, executable=(path != '/usr/lib/x86_64-linux-gnu/libapt-pkg.so.6.0')))
        validate_trust_anchor(anchor)
        argv = apt_argv(install_cfg if operation == 'install' else cfg, operation, version)
        # APT_CONFIG is loaded before system configuration; its Dir::Etc disables
        # inherited snippets/hooks and chooses only the reviewed signed sources.
        # Hooks exist only in the later -c install.conf. Loading the hook config
        # through BOTH APT_CONFIG and -c would append each hook twice.
        command = ['/usr/bin/sudo', '-n', '/usr/bin/env', '-i', 'PATH=/usr/bin:/bin',
                   'LANG=C', 'LC_ALL=C', 'DEBIAN_FRONTEND=noninteractive', 'APT_CONFIG=' + str(cfg), *argv]
        result = host.run_bounded(command, timeout=180, limit=1048576)
        write_new(private / (operation + '.stdout'), result['stdout'], 0o600)
        write_new(private / (operation + '.stderr'), result['stderr'], 0o600)
        transcript.append({'operation': operation, 'returncode': result['returncode'],
                           'stdout_sha256': host.sha(result['stdout']), 'stderr_sha256': host.sha(result['stderr']),
                           'cleanup': result['cleanup'], 'timed_out': result['timed_out'], 'overflow': result['overflow']})
        host.need(result['returncode'] == 0 and result['cleanup'] == 'CLOSED' and
                  not result['timed_out'] and not result['overflow'], 'APT_COMMAND_REFUSED')
        return result['stdout']
    cleanup = 'NOT_RUN'
    try:
        run('update')
        version = parse_candidate(run('policy'))
        prestate = gate.read_snapshot()
        gate.require_supported_apt(prestate)
        transaction = validate_simulation(run('simulate', version), version)
        # This early absence check remains; the actual pre-dpkg hook additionally
        # checks the complete prestate while the apt frontend lock is held.
        check = host.run_bounded(['/usr/bin/dpkg-query', '-W', '-f=${db:Status-Abbrev}', 'bubblewrap'], timeout=10, limit=65536)
        host.need(check['returncode'] == 1 and check['stdout'] == b'' and check['cleanup'] == 'CLOSED' and
                  not check['timed_out'] and not check['overflow'] and not os.path.lexists(host.BWRAP), 'APT_PRESTATE_CHANGED')
        request = transaction_request(directory, config, source, system, anchor, prestate, version, helper_binding)
        request_raw = gate.encoded(request)
        host.need(len(request_raw) <= gate.REQUEST_LIMIT, 'APT_GATE_REQUEST_BOUND')
        request_sha = host.sha(request_raw)
        write_new(directory / 'TRANSACTION_REQUEST.json', request_raw)
        write_new(private / 'TRANSACTION_REQUEST.json', request_raw, 0o600)
        install_cfg = directory / 'install.conf'
        actual_config = gate.install_config(request, request_sha)
        write_new(install_cfg, actual_config)
        run('install', version)
        actual = receive_transaction(directory, request, request_sha)
        binding = host.inspect_binding()
        host.need(binding['package']['version'] == version, 'APT_INSTALLED_VERSION')
        return {'status': 'SIGNED_DISTRO_PACKAGE_INSTALLED', 'install_count': actual['effects']['install_count'], 'version': version,
                'transaction': actual['effects'], 'simulation': transaction, 'actual_transaction': actual,
                'sources_sha256': host.sha(SOURCES), 'config_sha256': host.sha(config),
                'install_config_sha256': host.sha(actual_config),
                'trust_anchor': dict(anchor), 'system_tools': system, 'steps': transcript,
                'cleanup_contract': 'OWNED_APT_WORKSPACE_REMOVED_IN_FINALLY', 'native_calls': 0}
    finally:
        # Preserve bounded gate evidence privately even when installation refuses.
        # Receipt errors must not skip the original owned-workspace cleanup.
        receipt_error = None
        try:
            for name in ('PRE_DPKG.json', 'POST_DPKG.json'):
                path = directory / name
                if path.exists():
                    raw, _ = gate.read_regular(path, gate.CAPTURE_LIMIT, owner=0)
                    write_new(private / name, raw, 0o600)
        except Exception as exc:
            receipt_error = exc
        # Exact newly allocated tree only; never repair the system executable.
        host.need(directory.parent == Path('/tmp') and directory.name.startswith('dg18-c02-apt-') and
                  not directory.is_symlink() and host.identity(directory.lstat())[:2] == directory_id and
                  directory.lstat().st_uid == os.getuid(), 'APT_CLEANUP_IDENTITY')
        require_same_cleanup_tool(system['/usr/bin/rm'], host.protected_file('/usr/bin/rm', executable=True))
        result = host.run_bounded(['/usr/bin/sudo', '-n', '/usr/bin/rm', '--recursive', '--one-file-system', '--', str(directory)], timeout=15, limit=65536)
        cleanup = 'CLOSED' if result['returncode'] == 0 and result['cleanup'] == 'CLOSED' and not directory.exists() else 'UNKNOWN'
        write_new(private / 'SETUP_CLEANUP.json', host.encoded({'cleanup': cleanup, 'steps': transcript}), 0o600)
        host.need(cleanup == 'CLOSED', 'APT_CLEANUP_UNKNOWN')
        if receipt_error is not None:
            raise receipt_error
