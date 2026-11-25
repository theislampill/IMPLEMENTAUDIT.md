#!/usr/bin/env python3
"""Independent receiving of one DG16 placement-only diagnostic run.

A non-author receiver re-fetches only public bytes, within the 30-day artifact retention:
  R=repos/theislampill/IMPLEMENTAUDIT.md/actions
  gh api "$R/workflows/dg16-placement-diagnostic.yml/runs?branch=engineering/opus-dg16-placement-diag-trigger-20261125" > runs.json
  gh api "$R/runs/RUN/attempts/1" > run.json
  gh api "$R/runs/RUN/attempts/1/jobs" > jobs.json
  gh api "$R/jobs/JOB/logs" > job.log
  gh api "$R/runs/RUN/artifacts" > artifacts.json
  gh api "$R/artifacts/ARTIFACT/zip" > artifact.zip
and a git clone holding the authorized commit, then runs:
  python3 -I receive.py --commit SHA --repo CLONE --runs runs.json --run run.json --jobs jobs.json \
      --artifacts artifacts.json --log job.log --artifact-zip artifact.zip
The expected commit comes from the owner authorization, never from the receipt.
Every property is re-derived from raw observations; operator verdicts are only
compared. Output: one canonical JSON line.
  rc 0  RECEIVED_AT_DIAGNOSTIC_SCOPE   (P1-P7, run and job concluded success)
  rc 3  RECEIVED_PARTIAL_P1_P4         (operator refused at a launcher/route step; never
                                        substitutable for the full receiving)
  rc 1  REFUSED
Receiving awards nothing and replaces nothing without a new Root composition.
"""
import base64, hashlib, io, json, re, stat, subprocess, sys, types, zipfile

REPOSITORY = 'theislampill/IMPLEMENTAUDIT.md'
TRIGGER = 'engineering/opus-dg16-placement-diag-trigger-20261125'
WORKFLOW = '.github/workflows/dg16-placement-diagnostic.yml'
DIR = 'qualification/dg16-placement-diagnostic/'
SUBJECT = ('338c4c36d2ac95ca24345bc92fe8c53d66eaa15d', '53498df783ed441744ae5080982c2d5e59c34bbc')
PINS = {WORKFLOW: '98d2d886790eb230a803cd35a9245c276735705707d01c60019366740a255ef8',
        DIR + 'diagnose.py': '6a0f9130dfaddd62a94a59c82aef2e36c3a07e87295ab6df03ce3caec5b26eb7',
        DIR + 'root_placement.py': '18a93f8206a42435f73580ca65cf16d20dad96cb337b84a6d30104cce772ad4a',
        DIR + 'access_matrix.py': 'd0c192b858c5c806e3001d002bf013bb4add480e7ed818112c7ee16162763082'}
SETUP = dict(path='scripts/qualify-work-graph-c5-setup.py', bytes=86876,
             sha256='5e999f80140c517331943ecbac4215719d8f9416923672b7741788fe0ad673a9',
             origin='338c4c36d2ac95ca24345bc92fe8c53d66eaa15d:scripts/qualify-work-graph-c5-setup.py')
PACKAGE = dict(url='https://snapshot.ubuntu.com/ubuntu/20260901T000000Z/pool/main/b/bubblewrap/bubblewrap_0.9.0-1ubuntu0.1_amd64.deb',
               bytes=50178, sha256='1b506492bd9c7fd0cdb4f02ac822f1d3e336b0aead5113c1239baf8db5db562a')
POLICY_SHA = 'b3f303f76b8f2c097f92ca5e41b6e0126cd34a10df1d5d0e67b9e86e92e322af'
POLICY_NAMES = ('implementaudit-c5-bwrap-v1', 'implementaudit-c5-unpriv-bwrap-v1')
ADDED = set(PINS) | {DIR + 'receive.py', DIR + 'test_placement_diagnostic.py', DIR + 'PROPOSAL.json'}
EXEC_FILES = {DIR + 'diagnose.py': PINS[DIR + 'diagnose.py'], DIR + 'root_placement.py': PINS[DIR + 'root_placement.py'],
              DIR + 'access_matrix.py': PINS[DIR + 'access_matrix.py'], SETUP['path']: SETUP['sha256']}
MARKER = 'DG16_PLACEMENT_DIAG_EVIDENCE'
CHUNK_CHARS = 4096
NAMES = ('RECEIPT.json', 'ARTIFACT_MANIFEST.json')
BWRAP = (72160, '52231e1caf55bcbc667b269f49c63599a6f7db4767ae6a039580d0ff853db712')
SENTINEL = b'DG16_ACCESS08_FIXED_NONSECRET_SENTINEL\n'
PROBE = b'DG16_PLACEMENT_FIXED_NONSECRET_PROBE\n'
RETRY_LINE = b'urllib.error.HTTPError: HTTP Error 502: Bad Gateway'
ENODATA, EROFS = 61, 30
ACLS = [dict(attribute='system.posix_acl_access', result='ABSENT', errno=ENODATA),
        dict(attribute='system.posix_acl_default', result='ABSENT', errno=ENODATA)]
STEPS = ('HOSTED_CONTEXT', 'CREDENTIALS', 'EXEC_CUSTODY', 'HOST_FACTS', 'ROOT_OBSERVE', 'ISLAND_ABSENT_BEFORE',
         'ISLAND_CREATE', 'PACKET_CREATE', 'SOURCE_OUTPUT_ABSENT_AT_PACKET', 'BOOTSTRAP_CLOSING_CUSTODY',
         'PACKET_FILE_CUSTODY', 'SENTINEL_CREATE', 'FIXED_SIBLINGS_CREATE', 'LIVE_CURRENT', 'ANCESTRY_BEFORE',
         'LAUNCHER_PROVISION', 'TOOL_PIN', 'POLICY_PROVISION', 'FD_ROUTE', 'ANCESTRY_AFTER', 'POLICY_FINAL',
         'TOOL_AFTER', 'CLOSING_CURRENT')
PARTIAL_STEPS = ('LAUNCHER_PROVISION', 'TOOL_PIN', 'POLICY_PROVISION', 'FD_ROUTE')
PROPERTIES = ('P1_ROOT_CREDENTIALS', 'P2_ROOT_ANCESTOR_CUSTODY', 'P3_EXCLUSIVE_FRESH_ISLAND', 'P4_FIXED_SIBLINGS',
              'P5_FD_ROUTE', 'P6_ANCESTRY_NO_DRIFT', 'P7_CLOSING_CURRENTNESS')
PARTIAL = PROPERTIES[:4]
RECEIPT_BYTES = 524288
REPLACES = 'NOTHING_WITHOUT_NEW_ROOT_COMPOSITION'


class Refused(Exception):
    pass


def need(value, code):
    if not value:
        raise Refused(code)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def encode(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n').encode('ascii')


def parse(raw, code='JSON'):
    def pairs(items):
        out = {}
        for k, v in items:
            need(k not in out, code + '_DUPLICATE_KEY')
            out[k] = v
        return out
    def nonfinite(_):
        raise Refused(code + '_NONFINITE')
    try:
        return json.loads(raw.decode('utf-8'), object_pairs_hook=pairs, parse_constant=nonfinite)
    except (UnicodeError, ValueError):
        raise Refused(code + '_UNPARSEABLE') from None


def canonical_parse(raw, code):
    value = parse(raw, code)
    need(encode(value) == raw, code + '_NOT_CANONICAL')
    return value


def git(repo, *args):
    done = subprocess.run(['git', '-C', repo, *args], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          stdin=subprocess.DEVNULL, timeout=60)
    need(done.returncode == 0, 'GIT_' + args[0].upper().replace('-', '_'))
    return done.stdout


def check_source(repo, commit):
    """Commit = one child of the recorded subject that only adds the reviewed files."""
    need(re.fullmatch('[0-9a-f]{40}', commit), 'COMMIT_SHAPE')
    line = git(repo, 'rev-list', '--parents', '-n', '1', commit).decode().split()
    need(line == [commit, SUBJECT[0]], 'COMMIT_PARENT_NOT_SUBJECT')
    need(git(repo, 'rev-parse', SUBJECT[0] + '^{tree}').decode().strip() == SUBJECT[1], 'SUBJECT_TREE')
    rows = git(repo, 'diff-tree', '-r', '--no-renames', '--name-status', '-z', SUBJECT[0], commit).split(b'\0')
    rows = [r.decode() for r in rows if r]
    changes = dict(zip(rows[1::2], rows[0::2]))
    need(set(changes) == ADDED and set(changes.values()) == {'A'}, 'COMMIT_CHANGES_NOT_EXACT_ADDITIONS')
    for path, digest in PINS.items():
        need(sha(git(repo, 'cat-file', 'blob', commit + ':' + path)) == digest, 'FILE_PIN_' + path.rsplit('/', 1)[-1])
    setup = git(repo, 'cat-file', 'blob', commit + ':' + SETUP['path'])
    need(len(setup) == SETUP['bytes'] and sha(setup) == SETUP['sha256']
         and git(repo, 'rev-parse', commit + ':' + SETUP['path']) == git(repo, 'rev-parse', SUBJECT[0] + ':' + SETUP['path']),
         'SETUP_PIN')
    return {p: PINS[p] for p in sorted(PINS)}


def pinned_access_matrix(repo, commit):
    """The pinned module from the commit, with every hosted ubuntu-24.04 host root present."""
    raw = git(repo, 'cat-file', 'blob', commit + ':' + DIR + 'access_matrix.py')
    need(sha(raw) == PINS[DIR + 'access_matrix.py'], 'FILE_PIN_access_matrix.py')
    module = types.ModuleType('receiver_access_matrix')
    exec(compile(raw, 'access_matrix.py', 'exec'), module.__dict__)

    class HostedRoot(str):
        def exists(self):
            return self in module.HOST_ROOTS
    module.Path = HostedRoot
    return module


def check_run(runs, run, jobs, artifacts, commit, full):
    conclusion = 'success' if full else 'failure'
    listed = runs.get('workflow_runs')
    need(runs.get('total_count') == 1 and type(listed) is list and len(listed) == 1
         and listed[0].get('id') == run.get('id') and listed[0].get('head_sha') == commit, 'WORKFLOW_RUN_POPULATION')
    need(run.get('repository', {}).get('full_name') == REPOSITORY and run.get('event') == 'push'
         and run.get('head_branch') == TRIGGER and run.get('head_sha') == commit and run.get('run_attempt') == 1
         and run.get('path') == WORKFLOW and run.get('status') == 'completed', 'RUN_IDENTITY')
    need(run.get('conclusion') == conclusion, 'RUN_CONCLUSION')
    need(type(run.get('id')) is int and run['id'] > 0, 'RUN_ID')
    rows = jobs.get('jobs')
    need(type(rows) is list and len(rows) == 1 and jobs.get('total_count') == 1, 'EXACTLY_ONE_JOB')
    job = rows[0]
    need(job.get('run_id') == run['id'] and job.get('head_sha') == commit and job.get('run_attempt') == 1
         and job.get('name') == 'observe' and job.get('labels') == ['ubuntu-24.04']
         and job.get('runner_group_name') == 'GitHub Actions' and job.get('status') == 'completed', 'JOB_IDENTITY')
    need(job.get('conclusion') == conclusion, 'JOB_CONCLUSION')
    items = artifacts.get('artifacts')
    name = 'dg16-placement-diag-' + str(run['id']) + '-a1'
    need(type(items) is list and len(items) == 1 and artifacts.get('total_count') == 1
         and items[0].get('name') == name and items[0].get('expired') is False
         and items[0].get('workflow_run', {}).get('id') == run['id']
         and items[0].get('workflow_run', {}).get('head_sha') == commit, 'ARTIFACT_IDENTITY')
    return run, job, items[0]


def log_members(text):
    """Strict reassembly: one count line, then chunks 1..n consecutively, each <= 4 KiB."""
    marked = []
    for line in text.splitlines():
        at = line.find(MARKER)
        if at < 0:
            continue
        rest = line[at:]
        if rest.startswith(MARKER + '_SUMMARY '):
            continue
        need(at == 0 or re.fullmatch(r'[0-9T:.\-]+Z ', line[:at].lstrip(chr(0xFEFF))), 'LOG_LINE_PREFIX')
        marked.append(rest)
    found, i = {}, 0
    while i < len(marked):
        head = marked[i].split(' ')
        need(len(head) == 5 and head[0] == MARKER + '_COUNT' and head[1] in NAMES and head[1] not in found
             and re.fullmatch('[1-9][0-9]{0,3}', head[2]) and re.fullmatch('[0-9]{1,7}', head[3])
             and re.fullmatch('[0-9a-f]{64}', head[4]), 'LOG_COUNT_LINE')
        name, count = head[1], int(head[2])
        need(len(marked) >= i + 1 + count, 'LOG_CHUNKS_INCOMPLETE')
        text_parts = []
        for k in range(1, count + 1):
            bits = marked[i + k].split(' ')
            need(len(bits) == 4 and bits[0] == MARKER and bits[1] == name and bits[2] == '%d/%d' % (k, count)
                 and len(bits[3]) <= CHUNK_CHARS and (k == count or len(bits[3]) == CHUNK_CHARS), 'LOG_CHUNK_SEQUENCE')
            text_parts.append(bits[3])
        try:
            raw = base64.b64decode(''.join(text_parts), validate=True)
        except ValueError:
            raise Refused('LOG_BASE64') from None
        need(base64.b64encode(raw).decode('ascii') == ''.join(text_parts), 'LOG_BASE64_NONCANONICAL')
        need(len(raw) == int(head[3]) and sha(raw) == head[4], 'LOG_MEMBER_BINDING')
        found[name] = raw
        i += 1 + count
    need(set(found) == set(NAMES), 'LOG_MEMBERS_INCOMPLETE')
    return found


def zip_members(raw):
    try:
        archive = zipfile.ZipFile(io.BytesIO(raw))
        names = sorted(archive.namelist())
        need(names == sorted(NAMES), 'ARTIFACT_POPULATION')
        return {n: archive.read(n) for n in names}
    except zipfile.BadZipFile:
        raise Refused('ARTIFACT_ZIP') from None


def identity(o):
    need(type(o) is dict and set(o) == {'device', 'inode', 'mode', 'uid', 'gid'}
         and all(type(v) is int and v >= 0 for v in o.values()), 'IDENTITY_SHAPE')
    return o


def custody(o, mode=None):
    """Re-derivation of root_placement.observe_fd() from its raw output."""
    need(type(o) is dict and set(o) == {'identity', 'acls'}, 'OBSERVATION_SHAPE')
    i = identity(o['identity'])
    ok = stat.S_ISDIR(i['mode']) and i['uid'] == 0 and i['gid'] == 0 and not i['mode'] & 0o022 and o['acls'] == ACLS
    return ok and (mode is None or stat.S_IMODE(i['mode']) == mode)


def streamed(s):
    if not (type(s) is dict and set(s) == {'bytes', 'sha256', 'base64', 'complete'} and s['complete'] is True):
        return None
    try:
        raw = base64.b64decode(s['base64'], validate=True)
    except ValueError:
        return None
    return raw if len(raw) == s['bytes'] and sha(raw) == s['sha256'] else None


def text_is(fact, value):
    return type(fact) is dict and fact.get('readable') is True and fact.get('text', '').strip() == value


def absent_file(fact):
    return type(fact) is dict and fact.get('readable') is False and fact.get('errno') == 2


def exec_custody(r):
    """Item 7: operator ran from a root-owned 0700 copy whose files are exactly the pinned bytes."""
    e = r['observations'].get('exec')
    run_id = r['context']['run_id']
    if not (type(e) is dict and set(e) == {'root', 'parent', 'directories', 'files'}
            and e['root'] == '/run/dg16-placement-exec-' + run_id + '-a1'):
        return False
    p = e['parent']
    if not (type(p) is dict and set(p) == {'path', 'mode', 'uid', 'gid'} and p['path'] == '/run'
            and type(p['mode']) is int and stat.S_ISDIR(p['mode']) and not p['mode'] & 0o022
            and p['uid'] == 0 and p['gid'] == 0):
        return False
    dirs, files = e['directories'], e['files']
    return (type(dirs) is dict and set(dirs) == {'.', 'qualification', DIR[:-1], 'scripts'}
            and all(d == dict(mode=0o040700, uid=0, gid=0) for d in dirs.values())
            and type(files) is dict and set(files) == set(EXEC_FILES)
            and all(type(f) is dict and set(f) == {'bytes', 'sha256', 'mode'} and type(f['bytes']) is int
                    and f['sha256'] == EXEC_FILES[p] and f['mode'] == 0o100400 for p, f in files.items())
            and files[SETUP['path']]['bytes'] == SETUP['bytes'])


def derive(r, A):
    O = r['observations']
    got = {}
    paths = O.get('paths', {})
    base = '/dg16-g1-' + r['context']['run_id']
    packet = base + '/packet'
    need(paths == dict(source=base + '/source', private_output=base + '/output', packet=packet), 'FIXED_PATHS')
    st = O.get('parent_status', {}).get('fields', {})
    got['P1_ROOT_CREDENTIALS'] = O.get('credentials') == [0, 0, 0, 0] and st.get('Uid') == [0] * 4 and st.get('Gid') == [0] * 4
    got['P2_ROOT_ANCESTOR_CUSTODY'] = 'root' in O and custody(O['root'])
    got['P3_EXCLUSIVE_FRESH_ISLAND'] = (got['P2_ROOT_ANCESTOR_CUSTODY'] and O.get('island_absent_before') is True
        and 'island' in O and custody(O['island'], 0o700)
        and O['island']['identity']['device'] == O['root']['identity']['device']
        and O['island']['identity']['inode'] != O['root']['identity']['inode'])
    got['P4_FIXED_SIBLINGS'] = got['P3_EXCLUSIVE_FRESH_ISLAND'] and siblings(O)
    got['P5_FD_ROUTE'] = got['P4_FIXED_SIBLINGS'] and fd_route(r, packet, A)
    got['P6_ANCESTRY_NO_DRIFT'] = got['P4_FIXED_SIBLINGS'] and ancestry(O, base)
    got['P7_CLOSING_CURRENTNESS'] = (got['P5_FD_ROUTE'] and closing(O))
    return got


def siblings(O):
    if not ('packet' in O and custody(O['packet'], 0o700) and all(k in O and custody(O[k]) for k in ('source', 'output'))):
        return False
    files = O.get('packet_files')
    if type(files) is not dict or set(files) != {'probe', 'nested'}:
        return False
    p = files['probe']
    if not (type(p) is dict and p.get('mode') == 0o100400 and p.get('nlink') == 1 and p.get('uid') == 0 and p.get('gid') == 0
            and p.get('bytes') == len(PROBE) and p.get('xattrs') == [] and p.get('readback_sha256') == sha(PROBE)
            and p.get('device') == O['packet']['identity']['device'] and custody(files['nested'], 0o700)):
        return False
    inodes = {O[k]['identity']['inode'] for k in ('island', 'packet', 'source', 'output')} | {files['nested']['identity']['inode']}
    return (O.get('source_output_absent_at_packet') == dict(source=True, output=True) and len(inodes) == 5
            and all(O[k]['identity']['device'] == O['island']['identity']['device'] for k in ('packet', 'source', 'output'))
            and O.get('live_joins') == dict(root=True, island=True, packet=True, source=True, output=True))


def launcher_fact(f):
    return (type(f) is dict and f.get('path') == '/usr/bin/bwrap' and (f.get('bytes'), f.get('sha256')) == BWRAP
            and f.get('uid') == 0 and f.get('gid') == 0 and stat.S_ISREG(f.get('mode', 0)) and stat.S_IMODE(f['mode']) == 0o755
            and f.get('nlink') == 1 and f.get('xattrs') == [] and f.get('custody_stable') is True and f.get('complete') is True)


def launcher(rec, tool, exec_root):
    """Maintained V21 provisioning (one declared 502 retry), or a preexisting pinned file."""
    if type(rec) is not dict or rec.get('package') != PACKAGE or not launcher_fact(tool):
        return False
    if rec.get('mode') == 'PREEXISTING_NOT_PROVISIONED':
        b = rec.get('before')
        return (type(b) is dict and rec.get('record') is None and rec.get('attempts') == [] and b.get('uid') == 0
                and b.get('gid') == 0 and [b.get('device'), b.get('inode'), b.get('mode'), b.get('bytes')]
                == [tool.get('device'), tool.get('inode'), tool.get('mode'), tool.get('bytes')])
    if rec.get('mode') != 'PROVISIONED_BY_MAINTAINED_V21_SETUP' or rec.get('before') != 'ABSENT' or rec.get('setup') != SETUP:
        return False
    argv = ['/usr/bin/python3.12', '-I', '-S', '-B', exec_root + '/' + SETUP['path'], '--provision-hosted-launcher']
    attempts = rec.get('attempts')
    if not (type(attempts) is list and len(attempts) in (1, 2)):
        return False
    for n, a in enumerate(attempts, 1):
        if not (type(a) is dict and a.get('attempt') == n and a.get('argv') == argv and a.get('timeout') is False
                and type(a.get('elapsed_ns')) is int and a['elapsed_ns'] <= 60 * 10**9):
            return False
    if len(attempts) == 2:
        err = streamed(attempts[0].get('stderr'))
        body = err[:-1] if err and err.endswith(b'\n') else err
        if not (attempts[0].get('returncode') not in (0, None) and attempts[0].get('retry_eligible') is True
                and body is not None and body.rsplit(b'\n', 1)[-1] == RETRY_LINE):
            return False
    last = attempts[-1]
    out, err = streamed(last.get('stdout')), streamed(last.get('stderr'))
    if last.get('returncode') != 0 or out is None or err != b'':
        return False
    try:
        v = canonical_parse(out, 'PROVISION')
    except Refused:
        return False
    if v != rec.get('record') or type(v) is not dict or set(v) != {'scope', 'package', 'target', 'launcher'}:
        return False
    l = v['launcher']
    keys = {'bytes', 'sha256', 'opening', 'closing', 'mode', 'exclusive_creation'}
    if not (v['scope'] == 'LINUX_LAUNCHER_PROVISION_ONLY_NO_C5_OR_NATIVE_ACCEPTANCE' and v['target'] == '/usr/bin/bwrap'
            and v['package'] == PACKAGE and type(l) is dict and set(l) == keys and (l['bytes'], l['sha256']) == BWRAP
            and l['mode'] == '0755' and l['exclusive_creation'] is True and l['opening'] == l['closing']
            and type(l['closing']) is list and len(l['closing']) == 9):
        return False
    c = l['closing']
    return (c[:3] == [tool.get('device'), tool.get('inode'), tool.get('mode')] and stat.S_ISREG(c[2])
            and stat.S_IMODE(c[2]) == 0o755 and c[3] == 1 and c[4] == BWRAP[0] and c[7:] == [0, 0])


def policy_row(row, exec_root, flag):
    argv = ['/usr/bin/env', 'GITHUB_ACTIONS=true', 'RUNNER_ENVIRONMENT=github-hosted', '/usr/bin/python3.12',
            '-I', '-S', '-B', exec_root + '/' + SETUP['path'], flag]
    if not (type(row) is dict and row.get('argv') == argv and row.get('returncode') == 0 and row.get('timeout') is False):
        return None
    out, err = streamed(row.get('stdout')), streamed(row.get('stderr'))
    if out is None or err != b'':
        return None
    try:
        v = parse(out, 'POLICY')
    except Refused:
        return None
    return v if v == row.get('record') and type(v) is dict else None


def policy(O, host, exec_root):
    """The pinned V21 job-local policy, on the host shape the core's executed path requires.

    Expected values and where the executed b393a905 run.py path checks them (same moment:
    host facts are read before the policy load, as hosted_bwrap_policy_context() is at
    provision, and that context is re-read after the load by finalize):
      run.py:585-587 runs setup --provision-hosted-bwrap-policy; run.py:860-861 --finalize-...
      338c4c36 setup:1086 / setup:1167 call hosted_bwrap_policy_context() at those two moments
      setup:581 + 566-575  no bwrap policy file in /etc/apparmor.d or extra-profiles
      setup:582  /sys/module/apparmor/parameters/enabled == Y
      setup:583  /proc/sys/kernel/apparmor_restrict_unprivileged_userns == 1
      setup:584  /proc/sys/kernel/unprivileged_userns_clone == 1
    self_confinement and max_user_namespaces are recorded only: no executed core check reads them.
    host_utility.py:707-877 (the 26.04 probe; 734, 760-761) is not on the executed path.
    """
    if not (text_is(host.get('apparmor_enabled'), 'Y') and text_is(host.get('apparmor_restrict_unprivileged_userns'), '1')
            and text_is(host.get('unprivileged_userns_clone'), '1') and absent_file(host.get('bwrap_apparmor_profile'))
            and absent_file(host.get('bwrap_apparmor_extra_profile'))):
        return False
    v = policy_row(O.get('policy_provision'), exec_root, '--provision-hosted-bwrap-policy')
    if v is None:
        return False
    loaded, compiled = v.get('loaded'), v.get('compiled_profiles')
    if not (v.get('scope') == 'EPHEMERAL_CI_BWRAP_POLICY_ONLY_NO_NATIVE_ACCEPTANCE' and v.get('profile_sha256') == POLICY_SHA
            and v.get('global_state_unchanged') is True and v.get('receipt') == '/run/implementaudit-c5-bwrap-v1.json'
            and type(v.get('parser')) is dict and v['parser'].get('exit_code') == 0
            and type(loaded) is dict and set(loaded) == set(POLICY_NAMES) and type(compiled) is dict
            and set(compiled) == set(POLICY_NAMES)):
        return False
    for name, attach in zip(POLICY_NAMES, ('/usr/bin/bwrap', POLICY_NAMES[1])):
        row = loaded[name]
        if not (type(row) is dict and set(row) == {'attach', 'mode', 'sha256'} and row['mode'] == 'enforce'
                and (row['attach'] == attach or name == POLICY_NAMES[0] and row['attach'] == '<unknown>')
                and row['sha256'] == compiled[name] and re.fullmatch('[0-9a-f]{64}', str(row['sha256']))):
            return False
    return True


def fd_route(r, packet, A):
    O = r['observations']
    host = r.get('host') or {}
    exec_root = (O.get('exec') or {}).get('root')
    tool = O.get('launcher') or {}
    if not (exec_custody(r) and launcher(O.get('launcher_provision'), tool, exec_root) and policy(O, host, exec_root)):
        return False
    s = O.get('sentinel')
    if not (type(s) is dict and stat.S_ISREG(s.get('mode', 0)) and s.get('bytes') == len(SENTINEL) and s.get('sha256') == sha(SENTINEL)):
        return False
    route, before = O.get('fd_route'), O.get('ancestry_before')
    if type(route) is not dict or type(before) is not dict:
        return False
    fd = route.get('target_fd')
    if not (type(fd) is int and fd == before.get('target_fd')):
        return False
    expected = A.argv('/usr/bin/bwrap', packet, fd, 'FD')
    if not (route.get('argv') == expected and route.get('argv_sha256') == sha(A.canonical(expected))
            and route.get('child_limits') == dict(cpu_seconds=5, address_space_bytes=268435456, core_bytes=0)):
        return False
    if not (route.get('returncode') == 0 and route.get('timeout') is False and route.get('diagnostic_fd_count', 99) <= 32):
        return False
    out, err = streamed(route.get('stdout')), streamed(route.get('stderr'))
    if out is None or err != b'':
        return False
    try:
        p = canonical_parse(out, 'PAYLOAD')
    except Refused:
        return False
    target = before.get('target')
    creds = p.get('credentials') if type(p.get('credentials')) is dict else {}
    caps = creds.get('fields', {})
    parent_ns = before.get('credentials', {}).get('user_namespace')
    return (set(p) == {'schema', 'route', 'sentinel_hex', 'target', 'readonly_errno', 'credentials'}
            and p['schema'] == 'dg16.access08-payload.v1' and p['route'] == 'FD' and p['sentinel_hex'] == SENTINEL.hex()
            and p['readonly_errno'] == EROFS and caps.get('CapEff') == 0 and caps.get('CapPrm') == 0
            and creds.get('uid_map') == [[0, 0, 1]] and creds.get('gid_map') == [[0, 0, 1]]
            and type(parent_ns) is int and creds.get('user_namespace') != parent_ns
            and p['target'] == target == O['packet']['identity'] and route.get('payload_valid') is True)


def ancestry(O, base):
    b, a = O.get('ancestry_before'), O.get('ancestry_after')
    if type(b) is not dict or type(a) is not dict:
        return False
    if b.get('paths') != ['/', base, base + '/packet'] or b.get('fd_link') != base + '/packet':
        return False
    rows = b.get('ancestors')
    if not (type(rows) is list and len(rows) == 3):
        return False
    for row, key in zip(rows, ('root', 'island', 'packet')):
        if not (type(row) is dict and row.get('raw_acl') == {'system.posix_acl_access': None, 'system.posix_acl_default': None}
                and row.get('acl_absent') is True
                and {k: row.get(k) for k in ('device', 'inode', 'mode', 'uid', 'gid')} == O[key]['identity']):
            return False
    if b.get('target') != O['packet']['identity'] or b.get('sentinel', {}).get('sha256') != sha(SENTINEL):
        return False
    mounts = b.get('mounts')
    if not (type(mounts) is list and len(mounts) == 3 and all(type(m) is str for m in mounts)):
        return False
    same = ('target', 'target_fd', 'fd_flags', 'sentinel', 'ancestors', 'paths', 'mounts', 'credentials', 'fd_link')
    return set(a) == set(b) and all(a[k] == b[k] for k in same)


def closing(O):
    exec_root = (O.get('exec') or {}).get('root')
    final = policy_row(O.get('policy_final'), exec_root, '--finalize-hosted-bwrap-policy')
    provisioned = (O.get('policy_provision') or {}).get('record') or {}
    if not (type(final) is dict and final.get('status') == 'ACTIVE_POLICY_AND_RECEIPT_RETAINED'
            and final.get('profile_sha256') == POLICY_SHA and final.get('kernel_policy_unloaded') is False
            and final.get('loaded') == provisioned.get('loaded')):
        return False
    kids = O.get('children_after')
    if not (O.get('launcher_after') == O.get('launcher') and type(kids) is dict and kids
            and all(v == [] for v in kids.values())):
        return False
    sib = ('packet', 'source', 'output')
    return (O.get('closing') == {k: O[k] for k in ('root', 'island') + sib}
            and O.get('closing_joins') == dict(root=True, island=True, packet=True, source=True, output=True))


def receive(commit, repo, runs, run, jobs, artifacts, log_text, artifact_zip):
    pins = check_source(repo, commit)
    A = pinned_access_matrix(repo, commit)
    logged = log_members(log_text)
    zipped = zip_members(artifact_zip)
    need(logged == zipped, 'LOG_ARTIFACT_BYTES_DIFFER')
    raw = logged['RECEIPT.json']
    need(len(raw) <= RECEIPT_BYTES, 'RECEIPT_BOUND')
    manifest = canonical_parse(logged['ARTIFACT_MANIFEST.json'], 'MANIFEST')
    need(manifest == dict(schema='dg16.placement-only-diagnostic-artifacts.v1',
                          members=[dict(name='RECEIPT.json', bytes=len(raw), sha256=sha(raw))]), 'MANIFEST_BINDING')
    r = canonical_parse(raw, 'RECEIPT')
    need(type(r) is dict and r.get('schema') == 'dg16.placement-only-diagnostic-receipt.v2' and r.get('authority') == 'NONE'
         and r.get('original_awards') == [] and r.get('cause') == 'UNPROVED', 'RECEIPT_SCOPE')
    full = r.get('status') == 'COMPLETE'
    run, job, item = check_run(runs, run, jobs, artifacts, commit, full)
    if type(item.get('digest')) is str:
        need(item['digest'] == 'sha256:' + sha(artifact_zip), 'ARTIFACT_ZIP_DIGEST')
    need(r.get('recorded_subject') == dict(commit=SUBJECT[0], tree=SUBJECT[1],
         relation='RECORDED_PRODUCT_SUBJECT_ONLY_PLACEMENT_IS_A_HOST_PROPERTY'), 'RECEIPT_SUBJECT')
    need(r.get('context') == dict(run_id=str(run['id']), run_attempt=1, branch=TRIGGER, workflow_commit=commit), 'RECEIPT_CONTEXT')
    need(r.get('profile') == 'FRESH_ROOT_ISLAND_FIXED_SIBLINGS_V1', 'RECEIPT_PROFILE')
    need(r.get('setup') == SETUP, 'RECEIPT_SETUP_PIN')
    mods = r.get('modules', {})
    need(mods.get('root_placement', {}).get('sha256') == PINS[DIR + 'root_placement.py']
         and mods.get('access_matrix', {}).get('sha256') == PINS[DIR + 'access_matrix.py'], 'RECEIPT_MODULE_PINS')
    host = r.get('host') or {}
    need(host.get('os_release') == {'ID': 'ubuntu', 'VERSION_ID': '24.04'}, 'HOST_IMAGE')
    need(type(r.get('elapsed_ns')) is int and r['elapsed_ns'] <= 300 * 10**9, 'RECEIPT_ELAPSED_BOUND')
    steps = r.get('steps')
    need(type(steps) is list and [s.get('step') for s in steps] == list(STEPS), 'RECEIPT_STEP_POPULATION')
    results = [s.get('result') for s in steps]
    try:
        need(exec_custody(r), 'EXEC_CUSTODY_NOT_REDERIVED')
        derived = derive(r, A)
    except (KeyError, TypeError, AttributeError, IndexError):
        raise Refused('RECEIPT_STRUCTURE') from None
    need(set(derived) == set(PROPERTIES), 'PROPERTY_POPULATION')
    launcher_mode = ((r['observations'].get('launcher_provision') or {}).get('mode'))
    common = dict(schema='dg16.placement-only-diagnostic-receiving.v2', authority='NONE', original_awards=[], cause='UNPROVED',
                  commit=commit, run_id=run['id'], job_id=job.get('id'), artifact_id=item.get('id'),
                  artifact_zip_sha256=sha(artifact_zip), receipt=dict(bytes=len(raw), sha256=sha(raw)), file_pins=pins,
                  launcher_mode=launcher_mode, replaces=REPLACES,
                  scope='HOST_PLACEMENT_ONLY_THIS_RUN; CORE_MUST_STILL_CHECK_ITS_OWN_CURRENT_PLACEMENT')
    if full:
        need(r.get('failure') is None and results == ['PASS'] * len(STEPS), 'RECEIPT_NOT_COMPLETE')
        need(all(derived.values()), 'PROPERTY_NOT_REDERIVED_' + ','.join(k for k, v in derived.items() if not v))
        need(r.get('properties') == {k: 'OBSERVED' for k in PROPERTIES}, 'OPERATOR_VERDICT_DISAGREES')
        return dict(common, status='RECEIVED_AT_DIAGNOSTIC_SCOPE', substitutable_for_full=True,
                    properties={k: 'REDERIVED' for k in PROPERTIES})
    # Partial: refused exactly at one launcher/route step after every placement step passed.
    need(r.get('status') == 'REFUSED' and type(r.get('failure')) is str, 'RECEIPT_NOT_COMPLETE')
    need('REFUSED' in results, 'RECEIPT_NOT_COMPLETE')
    at = results.index('REFUSED')
    need(STEPS[at] in PARTIAL_STEPS and results[:at] == ['PASS'] * at
         and results[at + 1:] == ['NOT_ATTEMPTED'] * (len(STEPS) - at - 1)
         and steps[at].get('code') == r['failure'], 'PARTIAL_NOT_ELIGIBLE')
    need(all(derived[k] for k in PARTIAL), 'PROPERTY_NOT_REDERIVED_' + ','.join(k for k in PARTIAL if not derived[k]))
    need(r.get('properties') == {k: ('OBSERVED' if k in PARTIAL else 'NOT_OBSERVED') for k in PROPERTIES},
         'OPERATOR_VERDICT_DISAGREES')
    return dict(common, status='RECEIVED_PARTIAL_P1_P4', substitutable_for_full=False, failed_step=STEPS[at],
                failure=r['failure'], properties={k: ('REDERIVED' if k in PARTIAL else 'NOT_RECEIVED') for k in PROPERTIES})


def main(argv):
    args = dict(zip(argv[1::2], argv[2::2]))
    keys = {'--commit', '--repo', '--runs', '--run', '--jobs', '--artifacts', '--log', '--artifact-zip'}
    try:
        need(len(argv) == 17 and set(args) == keys, 'USAGE')
        read = lambda k: open(args[k], 'rb').read()
        result = receive(args['--commit'], args['--repo'], parse(read('--runs'), 'RUNS'), parse(read('--run'), 'RUN'),
                         parse(read('--jobs'), 'JOBS'), parse(read('--artifacts'), 'ARTIFACTS'),
                         read('--log').decode('utf-8'), read('--artifact-zip'))
    except (Refused, OSError, UnicodeError, subprocess.SubprocessError, KeyError, TypeError, AttributeError) as exc:
        code = exc.args[0] if isinstance(exc, Refused) else 'INPUT_' + type(exc).__name__.upper()
        sys.stdout.buffer.write(encode(dict(schema='dg16.placement-only-diagnostic-receiving.v2', status='REFUSED',
                                            authority='NONE', replaces=REPLACES, code=code)))
        return 1
    sys.stdout.buffer.write(encode(result))
    return 0 if result['status'] == 'RECEIVED_AT_DIAGNOSTIC_SCOPE' else 3


if __name__ == '__main__':
    raise SystemExit(main(sys.argv))
