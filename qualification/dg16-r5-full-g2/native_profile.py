"""Compile-bound ordinary G2 profile. Observations confer no authority."""
import os
from pathlib import Path
import re
import sys

E = _HOST_EVIDENCE_IO
PROFILE = 'DG16_G2_SELECTED_ORDINARY_UBUNTU26_PY314_CURRENT_NATIVE_V2'
OS = {'ID': 'ubuntu', 'VERSION_ID': '26.04'}
VERSION = [3, 14, 4]
PYTHON = '/usr/bin/python3.14'
HOST_FIELDS = ('os', 'architecture', 'kernel', 'python_version', 'tools')
MATCH_FIELDS = ('os', 'architecture', 'kernel', 'python_version',
                'tools.bash', 'tools.bwrap', 'tools.git', 'tools.python3')
TOOLS = ('bash', 'bwrap', 'git', 'python3')
need = E.need


def credentials():
    uid, euid, suid = os.getresuid()
    gid, egid, sgid = os.getresgid()
    return dict(uid=uid, euid=euid, suid=suid, gid=gid, egid=egid, sgid=sgid)


def validate_credentials(value):
    need(type(value) is dict and set(value) == {'uid', 'euid', 'suid', 'gid', 'egid', 'sgid'}
         and all(type(v) is int and 0 <= v < 2**32 for v in value.values())
         and value['uid'] == value['euid'] == value['suid'] != 0
         and value['gid'] == value['egid'] == value['sgid'], 'G2_NATIVE_NONROOT_CREDENTIALS_REQUIRED')
    return value


def validate_host(host):
    keys = {'os', 'architecture', 'kernel', 'uid', 'python_version', 'image_os',
            'image_version', 'tools', 'boot_identity_sha256', 'credentials'}
    need(type(host) is dict and set(host) == keys and host['os'] == OS
         and host['architecture'] == 'x86_64' and host['python_version'] == VERSION,
         'G2_NATIVE_ORDINARY_HOST_PROFILE')
    creds = validate_credentials(host['credentials'])
    need(type(host['uid']) is int and host['uid'] == creds['euid'], 'G2_NATIVE_CALLER_IDENTITY')
    for name in ('kernel', 'image_os', 'image_version'):
        need(type(host[name]) is str and re.fullmatch(r'[A-Za-z0-9_.:+~/=-]{1,80}', host[name]),
             'G2_NATIVE_HOST_FACT_SHAPE')
    need(type(host['boot_identity_sha256']) is str and re.fullmatch('[0-9a-f]{64}', host['boot_identity_sha256']),
         'G2_NATIVE_BOOT_IDENTITY')
    need(type(host['tools']) is dict and set(host['tools']) == set(TOOLS), 'G2_NATIVE_TOOL_POPULATION')
    for name in TOOLS:
        row = host['tools'][name]
        need(type(row) is dict and set(row) == {'available', 'requested', 'canonical', 'bytes', 'sha256',
             'root_owned_nonwritable_chain', 'setid_or_file_capabilities'} and row['available'] is True
             and row['requested'] == '/usr/bin/' + name and type(row['canonical']) is str
             and row['canonical'].startswith('/usr/') and Path(row['canonical']).is_absolute()
             and '..' not in Path(row['canonical']).parts
             and type(row['bytes']) is int and 0 < row['bytes'] <= 64 * 1024**2
             and type(row['sha256']) is str and re.fullmatch('[0-9a-f]{64}', row['sha256'])
             and row['root_owned_nonwritable_chain'] is True and row['setid_or_file_capabilities'] is False,
             'G2_NATIVE_TRUSTED_TOOL_FACT_REQUIRED')
    need(host['tools']['python3']['canonical'] == PYTHON, 'G2_NATIVE_SYSTEM_INTERPRETER_REQUIRED')
    return {key: host[key] for key in HOST_FIELDS}


def compare_historical(host, historical):
    observed = validate_host(host)
    need(type(historical) is dict and set(historical) == set(HOST_FIELDS), 'G2_NATIVE_HISTORICAL_PROFILE_SHAPE')
    matches = {key: observed[key] == historical[key] for key in HOST_FIELDS if key != 'tools'}
    matches.update({'tools.' + name: observed['tools'][name] == historical['tools'][name] for name in TOOLS})
    need(set(matches) == set(MATCH_FIELDS), 'G2_NATIVE_HOST_MATCH_POPULATION')
    return matches


def observe_process():
    """Actual child observations; called only inside the admitted future probe."""
    need(sys.platform == 'linux' and os.name == 'posix', 'G2_NATIVE_PROCESS_PLATFORM')
    release = {}
    raw = E.read_packet(Path('/etc/os-release').resolve(strict=True), 16384)
    for line in raw.decode('utf-8', 'strict').splitlines():
        if '=' in line:
            key, value = line.split('=', 1)
            if key in ('ID', 'VERSION_ID'):
                need(key not in release, 'G2_NATIVE_OS_RELEASE_DUPLICATE')
                release[key] = value.strip('"')
    result = dict(schema='dg16.g2-native-actual-process-profile.v1', profile=PROFILE,
        credentials=credentials(), os=release, architecture=os.uname().machine,
        kernel=os.uname().release, python_version=list(sys.version_info[:3]),
        python_canonical=str(Path(sys.executable).resolve(strict=True)))
    validate_process(result)
    return result


def validate_process(value, host=None):
    need(type(value) is dict and set(value) == {'schema', 'profile', 'credentials', 'os',
         'architecture', 'kernel', 'python_version', 'python_canonical'}
         and value['schema'] == 'dg16.g2-native-actual-process-profile.v1' and value['profile'] == PROFILE
         and value['os'] == OS and value['architecture'] == 'x86_64'
         and value['python_version'] == VERSION and value['python_canonical'] == PYTHON,
         'G2_NATIVE_ACTUAL_PROCESS_PROFILE')
    validate_credentials(value['credentials'])
    need(type(value['kernel']) is str and re.fullmatch(r'[A-Za-z0-9_.:+~/=-]{1,80}', value['kernel']),
         'G2_NATIVE_PROCESS_KERNEL')
    if host is not None:
        validate_host(host)
        need(all(value[key] == host[key] for key in ('credentials', 'os', 'architecture', 'kernel', 'python_version'))
             and value['python_canonical'] == host['tools']['python3']['canonical'],
             'G2_NATIVE_CHILD_DIFFERS_FROM_ACTUAL_HOST')
    return value
