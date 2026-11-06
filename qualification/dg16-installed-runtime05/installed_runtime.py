#!/usr/bin/env python3
"""Four actual isolated installed routes; bounded same-subject receiving.

Adapted from the retained qualify_installed.py method. This module has no
standalone entrypoint, imported owner, model invocation, or implicit home path.
All commands use the adapter's bounded actual-child capture interface.
"""
import hashlib
import io
import os
from pathlib import Path, PurePosixPath
import re
import stat
import zipfile

ROUTES = ('plugin-codex', 'plugin-claude', 'standalone-codex', 'standalone-claude')
CHILDREN = ('audit-state', 'audit-assess', 'audit-implement', 'audit-andon')
ASSETS = {'canonical_plugin': 'IMPLEMENTAUDIT.plugin.zip', 'standalone_compatibility': 'IMPLEMENTAUDIT.skill'}
SOURCE_COMMIT = '0d57929be5bd15682b4e9da2c0209d5dff307843'
SOURCE_TREE = 'ee316c27250ec422d35a1ea965182ebddf7a5da0'
SOURCE_BINDING = {'commit': SOURCE_COMMIT, 'tree': SOURCE_TREE, 'worktree_state': 'clean'}
RECEIPT_KEYS = ('schema','controller','controller_oid','claim_id','head','tree',
                'state_sha256','roadmap_sha256','invalidation_oid','boundary','epoch','next_action')
MAX_FILE, MAX_POPULATION, MAX_TREE = 1024 * 1024, 256, 16 * 1024 * 1024


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def require(value, code):
    if not value:
        raise RuntimeError(code)


def regular(path, maximum=MAX_FILE):
    """One held ordinary file; exact path/descriptor identity and actual bytes."""
    path = Path(path)
    def mark(s):
        return (s.st_dev,s.st_ino,s.st_mode,s.st_nlink,s.st_uid,s.st_gid,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
    before = path.lstat()
    require(stat.S_ISREG(before.st_mode) and before.st_nlink == 1
            and before.st_uid == os.geteuid() and 0 <= before.st_size <= maximum
            and not before.st_mode & 0o6022, 'PRIVATE_FILE_CUSTODY_REFUSED')
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC | os.O_NONBLOCK)
    try:
        require(mark(before) == mark(os.fstat(fd)), 'PRIVATE_OPEN_CHANGED')
        chunks = []; size = 0
        while size <= maximum:
            block = os.read(fd, min(65536, maximum + 1 - size))
            if not block:
                break
            chunks.append(block); size += len(block)
        raw = b''.join(chunks)
        require(len(raw) == before.st_size and len(raw) <= maximum
                and mark(os.fstat(fd)) == mark(before) == mark(path.lstat()), 'PRIVATE_READ_CHANGED')
        return raw
    finally:
        os.close(fd)


def file_fact(path, maximum=MAX_FILE):
    raw = regular(path, maximum)
    return {'bytes': len(raw), 'sha256': sha(raw), 'mode': stat.S_IMODE(Path(path).lstat().st_mode)}


def population(root, max_files=MAX_POPULATION, maximum=MAX_TREE):
    root = Path(root); result = {}; total = 0; directories = set()
    for parent, dirs, files in os.walk(root, followlinks=False):
        here = Path(parent); info = here.lstat()
        require(stat.S_ISDIR(info.st_mode) and info.st_uid == os.geteuid()
                and not info.st_mode & 0o6022, 'PRIVATE_DIRECTORY_CUSTODY_REFUSED')
        directories.add(here.relative_to(root).as_posix())
        require(len(directories) <= 1024, 'PRIVATE_DIRECTORY_POPULATION_BOUND')
        for name in dirs:
            info = (here / name).lstat()
            require(stat.S_ISDIR(info.st_mode) and not stat.S_ISLNK(info.st_mode), 'PRIVATE_ALIAS_REFUSED')
        for name in sorted(files):
            require(len(result) < max_files, 'PRIVATE_POPULATION_BOUND')
            path = here / name; row = file_fact(path)
            total += row['bytes']; require(total <= maximum, 'PRIVATE_AGGREGATE_BOUND')
            result[path.relative_to(root).as_posix()] = row
    require(root.is_dir() and not root.is_symlink(), 'PRIVATE_ROOT_REFUSED')
    expected_dirs = {'.'} | {str(parent) for name in result for parent in PurePosixPath(name).parents}
    require(directories == expected_dirs, 'PRIVATE_DIRECTORY_POPULATION_REFUSED')
    return result


def route_paths(output, route):
    require(route in ROUTES, 'ROUTE_REFUSED')
    base = output / 'private' / 'installs' / route
    root = base / 'plugins/implementaudit' if route.startswith('plugin-') else base
    payload = root if route.startswith('plugin-') else root / 'skills/implementaudit'
    return base, root, payload


def source_payloads(source, manifest):
    """Independent finite projection from the already byte-verified source."""
    def normalized(relative):
        require(relative in manifest, 'PACKAGE_SOURCE_MEMBER_REFUSED')
        raw = regular(source / relative)
        require(len(raw) == manifest[relative]['bytes'] and sha(raw) == manifest[relative]['sha256'], 'PACKAGE_SOURCE_DRIFT')
        return raw.replace(b'\r\n', b'\n')
    common = {}
    for relative in sorted(manifest):
        if relative.startswith('skills/implementaudit/'):
            name = relative.removeprefix('skills/implementaudit/')
            common[name] = (normalized(relative), 0o755 if name.startswith('scripts/') else 0o644)
    require('SKILL.md' in common, 'GOVERNOR_PAYLOAD_ABSENT')
    plugin = {f'skills/implementaudit/{name}': value for name, value in common.items()}
    standalone = dict(common)
    for child in CHILDREN:
        name = f'skills/{child}/SKILL.md'; raw = normalized(name)
        plugin[name] = (raw, 0o644)
        body, count = re.subn(r'\A---\n.*?\n---\n+', '', raw.decode('utf-8'), count=1, flags=re.S)
        require(count == 1, 'CHILD_FRONTMATTER_REFUSED')
        body = re.sub(r'\.\.[\\/]+implementaudit[\\/]+((?:references|scripts|templates)[\\/]+[^`\r\n]+)',
                      lambda match: '../' + match.group(1).replace('\\', '/'), body)
        standalone[f'internal-procedures/{child}.md'] = (body.encode('utf-8'), 0o644)
    for name in ('.codex-plugin/plugin.json', '.claude-plugin/plugin.json', '.claude-plugin/marketplace.json'):
        plugin[name] = (normalized(name), 0o644)
    contract = normalized('package/implementaudit-package.json')
    plugin['IMPLEMENTAUDIT_PACKAGE.json'] = (contract, 0o644)
    standalone['IMPLEMENTAUDIT_PACKAGE.json'] = (contract, 0o644)
    return {'canonical_plugin': plugin, 'standalone_compatibility': standalone}


def archive_snapshot(source, output, manifest, parse):
    packages = output / 'private/packages'
    require({p.name for p in packages.iterdir()} == {*ASSETS.values(), 'CHECKSUMS.txt'}, 'PACKAGE_OUTPUT_POPULATION_REFUSED')
    checksum = regular(packages / 'CHECKSUMS.txt', 4096)
    checksum_rows = {}
    for line in checksum.decode('ascii').splitlines():
        fields = line.split()
        require(len(fields) == 3 and fields[0] == 'sha256' and re.fullmatch('[0-9a-f]{64}', fields[1])
                and fields[2] in ASSETS.values() and fields[2] not in checksum_rows, 'CHECKSUM_SHAPE_REFUSED')
        checksum_rows[fields[2]] = fields[1]
    require(set(checksum_rows) == set(ASSETS.values()), 'CHECKSUM_POPULATION_REFUSED')
    expected = source_payloads(source, manifest)
    result = {'checksums': file_fact(packages / 'CHECKSUMS.txt', 4096), 'artifacts': {}}
    for role, name in ASSETS.items():
        raw = regular(packages / name, 589824)
        require(sha(raw) == checksum_rows[name] and len(raw) <= 589824 - 2000, 'PACKAGE_CHECKSUM_OR_RESERVE_REFUSED')
        rows = {}; bodies = {}; total = 0
        with zipfile.ZipFile(io.BytesIO(raw)) as archive:
            infos = archive.infolist()
            names = [info.filename for info in infos]
            require(len(infos) <= MAX_POPULATION and names == sorted(set(names)), 'ARCHIVE_POPULATION_REFUSED')
            for info in infos:
                path = PurePosixPath(info.filename)
                require(str(path) == info.filename and not path.is_absolute() and '..' not in path.parts
                        and '\\' not in info.filename and not info.is_dir(), 'ARCHIVE_PATH_REFUSED')
                mode = stat.S_IMODE(info.external_attr >> 16)
                wanted_mode = 0o755 if info.filename.startswith(('scripts/', 'skills/implementaudit/scripts/')) else 0o644
                require(info.create_system == 3 and info.compress_type == zipfile.ZIP_DEFLATED
                        and stat.S_IFMT(info.external_attr >> 16) == stat.S_IFREG
                        and mode == wanted_mode and not info.extra and not info.comment
                        and 0 <= info.file_size <= MAX_FILE, 'ARCHIVE_METADATA_REFUSED')
                total += info.file_size; require(total <= MAX_TREE, 'ARCHIVE_AGGREGATE_BOUND')
                body = archive.read(info); require(len(body) == info.file_size, 'ARCHIVE_LENGTH_REFUSED')
                bodies[info.filename] = body
                rows[info.filename] = {'bytes': len(body), 'sha256': sha(body), 'mode': mode}
        require(set(rows) == {*expected[role], 'IMPLEMENTAUDIT_INVENTORY.json'}, 'ARCHIVE_SOURCE_POPULATION_REFUSED')
        for member, (body, mode) in expected[role].items():
            require(bodies[member] == body and rows[member]['mode'] == mode, 'ARCHIVE_SOURCE_PARITY_REFUSED')
        contract = parse(bodies['IMPLEMENTAUDIT_PACKAGE.json'])
        require(contract['runtime_version'] == '0.4.0' and contract['release_family'] == 'v0.4.0.0'
                and contract['budget_revision']['revision'] == 4
                and contract['budget_revision']['owner_approval']['sha256'] == 'e4af32dc219e8c041d62170b960cdb465f0cdfebdb7e414d0f45b7726cc31488'
                and contract['budgets'][role]['cap_bytes'] == 589824
                and contract['budgets'][role]['reserve_bytes'] == 2000, 'PACKAGE_POLICY_BINDING_REFUSED')
        inventory = parse(bodies['IMPLEMENTAUDIT_INVENTORY.json'])
        require(inventory['schema'] == 'implementaudit.package-inventory.v1' and inventory['artifact_role'] == role
                and inventory['source'] == SOURCE_BINDING, 'INVENTORY_SOURCE_BINDING_REFUSED')
        for field in ('package_name','runtime_version','release_family','public_governor','required_skills','internal_skills'):
            require(inventory[field] == contract[field], 'INVENTORY_IDENTITY_REFUSED')
        declared = inventory['members']; require(type(declared) is list and len(declared) == len(expected[role]), 'INVENTORY_POPULATION_REFUSED')
        seen = set()
        for row in declared:
            require(set(row) == {'path','bytes','sha256'} and row['path'] in expected[role] and row['path'] not in seen,
                    'INVENTORY_MEMBER_REFUSED')
            actual = rows[row['path']]
            require(type(row['bytes']) is int and row['bytes'] == actual['bytes'] and row['sha256'] == actual['sha256'], 'INVENTORY_BYTES_REFUSED')
            seen.add(row['path'])
        require(seen == set(expected[role]), 'INVENTORY_POPULATION_REFUSED')
        result['artifacts'][role] = {'name': name, 'bytes': len(raw), 'sha256': sha(raw), 'members': rows,
            'inventory_members': len(declared), 'expanded_bytes': total, 'source': dict(SOURCE_BINDING)}
    return result


def installed_snapshot(output, packages):
    result = {}
    for route in ROUTES:
        base, root, payload = route_paths(output, route)
        role = 'canonical_plugin' if route.startswith('plugin-') else 'standalone_compatibility'
        rows = population(payload)
        require(rows == packages['artifacts'][role]['members'], 'INSTALLED_PACKAGE_PARITY_REFUSED')
        # The host-root sentinel belongs outside the plugin payload. No alias or
        # extra payload can hide in the wrapper directories.
        entire = population(base, 300)
        prefix = 'plugins/implementaudit/' if route.startswith('plugin-') else 'skills/implementaudit/'
        expected = {prefix + name: row for name, row in rows.items()}
        if route.startswith('plugin-'):
            sentinel = file_fact(base / '.implementaudit-isolated-host-root', 256)
            require(sentinel['bytes'] == len(b'dg16 installed runtime 05 isolated file-copy host\n'), 'ISOLATED_SENTINEL_REFUSED')
            expected['.implementaudit-isolated-host-root'] = sentinel
        require(entire == expected, 'INSTALLED_HOST_POPULATION_REFUSED')
        result[route] = {'files': rows, 'inventory_members': packages['artifacts'][role]['inventory_members'],
                         'role': role, 'source': dict(SOURCE_BINDING)}
    return result


def install_all(ctx, state):
    output, source = ctx.output, ctx.source
    installs = output / 'private/installs'; installs.mkdir(mode=0o700)
    packages = output / 'private/packages'
    for route in ROUTES:
        base, root, payload = route_paths(output, route)
        if route.startswith('plugin-'):
            base.mkdir(mode=0o700)
            ctx.write(base / '.implementaudit-isolated-host-root', b'dg16 installed runtime 05 isolated file-copy host\n')
            argv = [ctx.tools['bash'], str(source / 'scripts/install-plugin-from-release.sh'), '--asset',
                    str(packages / ASSETS['canonical_plugin']), '--checksum', str(packages / 'CHECKSUMS.txt'),
                    '--host', route.removeprefix('plugin-'), '--host-root', str(base), '--version', '0.4.0']
        elif route == 'standalone-codex':
            argv = [ctx.tools['bash'], str(source / 'scripts/install-codex-from-release.sh'), '--asset',
                    str(packages / ASSETS['standalone_compatibility']), '--checksum', str(packages / 'CHECKSUMS.txt'),
                    '--codex-home', str(base), '--version', '0.4.0']
        else:
            argv = [ctx.tools['bash'], str(source / 'scripts/install-claude-from-release.sh'), '--asset',
                    str(packages / ASSETS['standalone_compatibility']), '--checksum', str(packages / 'CHECKSUMS.txt'),
                    '--claude-skills-dir', str(payload)]
        ctx.run('install-' + route, argv, source, seconds=120, release_env=True)
    snapshot = installed_snapshot(output, state['packages'])
    state['installed'] = snapshot
    ctx.write(output / 'private/INSTALLED_BEFORE.json', ctx.canonical(snapshot))


def receipt_parts(raw):
    require(len(raw) <= 16384 and raw.endswith(b'\n') and raw.count(b'\n') == 1, 'RECEIPT_LINE_SHAPE_REFUSED')
    parts = raw.decode('utf-8').rstrip('\n').split('\t')
    require(len(parts) == 12 and parts[0] == 'implementaudit.continuity-receipt.v2', 'RECEIPT_SCHEMA_REFUSED')
    return dict(zip(RECEIPT_KEYS, parts))


def refs(ctx, subject, label):
    raw = ctx.run(label, [ctx.tools['git'], '-C', str(subject), 'for-each-ref', '--format=%(refname)\t%(objectname)'], subject)
    result = {}
    for line in raw.decode('ascii').splitlines():
        parts = line.split('\t')
        require(len(parts) == 2 and re.fullmatch(r'refs/[A-Za-z0-9._/-]{1,240}', parts[0])
                and re.fullmatch('[0-9a-f]{40}', parts[1]) and parts[0] not in result and len(result) < 32,
                'REF_POPULATION_REFUSED')
        result[parts[0]] = parts[1]
    return result


def subject_paths(ctx, route):
    base, installed, payload = route_paths(ctx.output, route)
    return ctx.output / 'private/subjects' / route, installed, installed / 'skills/implementaudit/scripts/claim-run.sh'


def qualify(ctx, state, route):
    require(route in ROUTES and route not in state['subjects'], 'SUBJECT_REPLAY_REFUSED')
    subject, installed, helper = subject_paths(ctx, route)
    subject.mkdir(mode=0o700, parents=True, exist_ok=False)
    controller = 'dg16-installed05-' + state['context']['run_id'] + '-' + route
    next_action = 'Receive the actual installed ' + route + ' receipt and object/document population in a distinct process before host teardown'
    request = {'route': route, 'subject': str(subject), 'installed': str(installed), 'helper': str(helper),
               'controller': controller, 'next_action': next_action, 'owner_process_pid': os.getpid(),
               'source': dict(SOURCE_BINDING), 'status': 'STARTED_OUTCOME_UNKNOWN'}
    state['subjects'][route] = request; ctx.persist()
    ctx.write(subject / 'QUALIFICATION.md', ('# Actual installed runtime qualification\n\nRoute: ' + route + '\nProduct source: '
              + SOURCE_COMMIT + '\nProduct tree: ' + SOURCE_TREE + '\n\nFresh isolated Linux file-copy subject. '
              'The authorized task is installed initialization and first normal resume with separate-process receiving. '
              'Governed phase remains open. No native application discovery, acceptance or publication.\n').encode())
    ctx.write(subject / '.gitignore', b'.IMPLEMENTAUDIT/\n')
    ctx.run('subject-git-init', [ctx.tools['git'], '-c', 'init.templateDir=', 'init', '-q', '-b', 'qualification'], subject)
    ctx.run('subject-git-add', [ctx.tools['git'], 'add', '--', 'QUALIFICATION.md', '.gitignore'], subject)
    ctx.run('subject-git-commit', [ctx.tools['git'], '-c', 'user.name=DG16 installed qualification',
            '-c', 'user.email=dg16-installed@example.invalid', '-c', 'commit.gpgsign=false', '-c', 'core.hooksPath=/dev/null',
            'commit', '-qm', 'Define fresh bounded installed initialization task'], subject)
    raw = ctx.run('subject-baseline', [ctx.tools['git'], 'rev-parse', 'HEAD', 'HEAD^{tree}'], subject)
    baseline = raw.decode('ascii').splitlines()
    require(len(baseline) == 2 and all(re.fullmatch('[0-9a-f]{40}', item) for item in baseline), 'SUBJECT_BASELINE_REFUSED')
    request['subject_head'], request['subject_tree'] = baseline
    require(not any(name.startswith('refs/implementaudit/') for name in refs(ctx, subject, 'subject-no-imported-refs')), 'SUBJECT_IMPORTED_REFS_REFUSED')
    def owner(label, args):
        return ctx.run(label, [ctx.tools['bash'], str(helper), *args], subject)
    relative = owner('installed-claim', ['--controller', controller, 'installed runtime ' + route]).decode('ascii').strip()
    require(re.fullmatch(r'\.IMPLEMENTAUDIT/runs/[a-z0-9][a-z0-9-]*-[A-Za-z0-9]{6}', relative), 'INSTALLED_RUN_ROOT_REFUSED')
    request['run_relative'] = relative; root = subject / relative
    claimed = dict(line.split('=', 1) for line in regular(root / '.claimed', 65536).decode().splitlines())
    request['claim_id'] = claimed['claim_id']; ctx.persist()
    authored = ctx.run('installed-author', [ctx.tools['python3'], '-I', '-S', '-B',
            str(ctx.source / 'fixtures/controller-initialization/author_checkpoint.py'), '--repo', str(subject),
            '--run-root', relative, '--source', str(installed), '--purpose',
            'Qualify actual installed ' + route + ' initialization and first normal resume on this fresh authorized isolated Linux subject.',
            '--next-action', next_action], subject)
    authored_hashes = ctx.parse(authored)
    require(set(authored_hashes) == set((*ctx.names, 'phases/phase-1.md')), 'INSTALLED_AUTHORED_POPULATION_REFUSED')
    for name, digest in authored_hashes.items():
        require(sha(regular(root / name)) == digest, 'INSTALLED_AUTHOR_READBACK_REFUSED')
    inspection = ctx.parse(owner('installed-inspect', ['--inspect-controller-initialization', controller, '--run-root', relative]))
    require(inspection['missing_files'] == [] and inspection['current_controller_oid'] is None
            and inspection['binding_record_oid'] is None, 'INSTALLED_PENDING_STATE_REFUSED')
    initialization = inspection['initialization_token']
    require(re.fullmatch('refs/implementaudit/controller-initializations/' + controller + r'/[0-9a-f]{32}@[0-9a-f]{40}', initialization),
            'INSTALLED_INITIALIZATION_TOKEN_REFUSED')
    activation = ctx.parse(owner('installed-activate', ['--activate-controller', controller, '--run-root', relative,
                                                      '--expected-initialization', initialization]))
    require(activation['status'] == 'BOUND_ELIGIBLE_FOR_NORMAL_CURRENTNESS'
            and activation['authority_ceiling'] == 'ELIGIBLE_FOR_NORMAL_CURRENTNESS_ONLY', 'INSTALLED_ACTIVATION_SCOPE_REFUSED')
    request['activation'] = activation; ctx.persist()
    # Separate completed captured processes. No shell pipeline/composed read.
    reads = {}
    for role in ('STATE', 'ROADMAP'):
        raw = ctx.run('installed-read-' + role.lower(), [ctx.tools['python3'], '-I', '-S', '-B', '-c',
              'from pathlib import Path;import sys;sys.stdout.buffer.write(Path(sys.argv[1]).read_bytes())', str(root / (role + '.md'))], subject)
        require(raw == regular(root / (role + '.md')), 'INSTALLED_CANONICAL_READ_CHANGED')
        reads[role] = {'bytes': len(raw), 'sha256': sha(raw), 'command_ordinal': state['command_count']}
    require(reads['STATE']['command_ordinal'] < reads['ROADMAP']['command_ordinal'], 'INSTALLED_READ_ORDER_REFUSED')
    request['reads'] = reads
    receipt = owner('installed-first-resume', ['--resume-controller', controller, '--boundary', 'new-session', '--epoch', 'G0001']).decode('ascii').strip()
    require(re.fullmatch('refs/implementaudit/continuity-receipts/' + controller + r'/G0001@[0-9a-f]{40}', receipt), 'INSTALLED_RECEIPT_TOKEN_REFUSED')
    request['receipt_token'] = receipt; ctx.persist()
    for label, args in [('installed-verify', ['--verify-resume-receipt', receipt]),
                        ('installed-require', ['--require-current-continuity', controller])]:
        require(owner(label, args).decode('ascii').strip() == receipt, 'INSTALLED_CURRENT_RECEIPT_CHANGED')
    request['run_population'] = population(root)
    request['namespace_population'] = ctx.h.runtime_snapshot(subject, {'run_root':relative}, ctx.u)
    request['refs'] = refs(ctx, subject, 'installed-refs-after')
    request['status'] = 'FIRST_NORMAL_RESUME_VERIFIED'
    ctx.write(ctx.output / 'private' / (route + '-READBACK_REQUEST.json'), ctx.canonical(request))


def receive(ctx, state, route):
    require(route in state['subjects'] and route not in state['received'], 'RECEIVER_STATE_REFUSED')
    request_path = ctx.output / 'private' / (route + '-READBACK_REQUEST.json')
    request_raw = regular(request_path)
    request = ctx.parse(request_raw)
    require(request == state['subjects'][route] and request['status'] == 'FIRST_NORMAL_RESUME_VERIFIED'
            and request['owner_process_pid'] != os.getpid(), 'DISTINCT_RECEIVER_PROCESS_REFUSED')
    subject, installed, helper = subject_paths(ctx, route); root = subject / request['run_relative']
    def owner(label, args):
        return ctx.run(label, [ctx.tools['bash'], str(helper), *args], subject)
    receipt = request['receipt_token']
    require(owner('receive-current-before', ['--require-current-continuity', request['controller']]).decode().strip() == receipt,
            'RECEIVER_CURRENTNESS_REFUSED')
    before = refs(ctx, subject, 'receive-refs-before')
    require(before == request['refs'], 'RECEIVER_REF_DRIFT')
    require(ctx.h.runtime_snapshot(subject, {'run_root':request['run_relative']}, ctx.u) == request['namespace_population'],
            'RECEIVER_NAMESPACE_DRIFT')
    current = owner('receive-controller', ['--current-controller', request['controller']]).decode().strip().split('\t')
    require(current == [request['controller'], str(subject), str(root), request['claim_id']], 'RECEIVER_CONTROLLER_CONTEXT_REFUSED')
    baseline = ctx.run('receive-baseline', [ctx.tools['git'], 'rev-parse', 'HEAD', 'HEAD^{tree}'], subject).decode().splitlines()
    require(baseline == [request['subject_head'], request['subject_tree']], 'RECEIVER_BASELINE_DRIFT')
    receipt_ref, receipt_oid = receipt.split('@'); controller_ref = 'refs/implementaudit/controllers/' + request['controller']
    require(before.get(receipt_ref) == receipt_oid and before.get(controller_ref) == request['activation']['controller_oid'], 'RECEIVER_OID_BINDING_REFUSED')
    selected = {name: oid for name, oid in before.items() if name.startswith('refs/implementaudit/')}
    require(2 <= len(selected) <= 16, 'RECEIVER_AUTHORITY_POPULATION_REFUSED')
    objects = {}; received_receipt = None
    for index, (ref, oid) in enumerate(sorted(selected.items())):
        kind = ctx.run('receive-object-type-' + str(index), [ctx.tools['git'], 'cat-file', '-t', oid], subject).decode().strip()
        require(kind == 'blob', 'RECEIVER_OBJECT_TYPE_REFUSED')
        body = ctx.run('receive-object-' + str(index), [ctx.tools['git'], 'cat-file', 'blob', oid], subject)
        require(hashlib.sha1(b'blob ' + str(len(body)).encode() + b'\0' + body).hexdigest() == oid, 'RECEIVER_OBJECT_HASH_REFUSED')
        objects[ref] = {'oid': oid, 'bytes': len(body), 'sha256': sha(body)}
        if ref == receipt_ref:
            received_receipt = receipt_parts(body)
        if ref == controller_ref:
            require(body.decode().rstrip('\n').split('\t') == ['implementaudit.controller-current.v1', request['controller'], request['claim_id'], str(root)],
                    'RECEIVER_CONTROLLER_BODY_REFUSED')
    actual = population(root)
    expected = {'schema': 'implementaudit.continuity-receipt.v2', 'controller': request['controller'],
        'controller_oid': before[controller_ref], 'claim_id': request['claim_id'], 'head': baseline[0], 'tree': baseline[1],
        'state_sha256': actual['STATE.md']['sha256'], 'roadmap_sha256': actual['ROADMAP.md']['sha256'],
        'invalidation_oid': 'none', 'boundary': 'new-session', 'epoch': 'G0001', 'next_action': request['next_action']}
    require(received_receipt == expected, 'RECEIVER_RECEIPT_FIELDS_REFUSED')
    claim = dict(line.split('=', 1) for line in regular(root / '.claimed', 65536).decode().splitlines())
    require(claim['claim_id'] == request['claim_id'] and claim['repo_root'] == str(subject)
            and claim['run_root'] == request['run_relative'], 'RECEIVER_CLAIM_CUSTODY_REFUSED')
    activated = request['activation']['run_population']['files']
    require(len(activated) == len(actual) and {row['path'] for row in activated} == set(actual), 'RECEIVER_DOCUMENT_POPULATION_REFUSED')
    expected_dirs = sorted({'.'} | {str(parent) for name in actual for parent in PurePosixPath(name).parents})
    require(request['activation']['run_population']['directories'] == expected_dirs, 'RECEIVER_DIRECTORY_BINDING_REFUSED')
    for row in activated:
        require(all(row[key] == actual[row['path']][key] for key in ('bytes','sha256','mode')), 'RECEIVER_DOCUMENT_BINDING_REFUSED')
    require(actual == request['run_population'], 'RECEIVER_DOCUMENT_DRIFT')
    for label, args in [('receive-verify-final', ['--verify-resume-receipt', receipt]),
                        ('receive-require-final', ['--require-current-continuity', request['controller']])]:
        require(owner(label, args).decode().strip() == receipt, 'RECEIVER_FINAL_CURRENTNESS_REFUSED')
    after = refs(ctx, subject, 'receive-refs-after')
    require(before == after and population(root) == actual, 'RECEIVER_CLOSING_DRIFT')
    require(ctx.h.runtime_snapshot(subject, {'run_root':request['run_relative']}, ctx.u) == request['namespace_population'],
            'RECEIVER_CLOSING_NAMESPACE_DRIFT')
    result = {'status': 'PASS', 'route': route, 'receiver_pid': os.getpid(), 'owner_pid': request['owner_process_pid'],
        'request_sha256': sha(request_raw), 'refs': after, 'objects': objects, 'run_population': actual,
        'receipt': received_receipt, 'receipt_body_sha256': objects[receipt_ref]['sha256'],
        'final_currentness': True, 'phase_left_open': True, 'authority': 'NONE'}
    ctx.write(ctx.output / 'private' / (route + '-RECEIVED.json'), ctx.canonical(result))
    state['received'][route] = result


def close_subject(ctx, state, route):
    require(route in state['received'], 'CLOSING_SUBJECT_NOT_RECEIVED')
    request = state['subjects'][route]; received = state['received'][route]
    subject, installed, helper = subject_paths(ctx, route)
    require(population(subject / request['run_relative']) == received['run_population'], 'CLOSING_SUBJECT_DOCUMENT_DRIFT')
    require(ctx.h.runtime_snapshot(subject, {'run_root':request['run_relative']}, ctx.u) == request['namespace_population'],
            'CLOSING_SUBJECT_NAMESPACE_DRIFT')
    before = refs(ctx, subject, 'closing-' + route + '-refs-before')
    require(before == received['refs'], 'CLOSING_SUBJECT_REF_DRIFT')
    baseline = ctx.run('closing-' + route + '-baseline', [ctx.tools['git'], 'rev-parse', 'HEAD', 'HEAD^{tree}'], subject).decode().splitlines()
    require(baseline == [request['subject_head'], request['subject_tree']], 'CLOSING_SUBJECT_BASELINE_DRIFT')
    raw = ctx.run('closing-' + route + '-require', [ctx.tools['bash'], str(helper), '--require-current-continuity', request['controller']], subject)
    require(raw.decode().strip() == request['receipt_token'], 'CLOSING_SUBJECT_CURRENTNESS_REFUSED')
    require(refs(ctx, subject, 'closing-' + route + '-refs-after') == before
            and population(subject / request['run_relative']) == received['run_population']
            and ctx.h.runtime_snapshot(subject, {'run_root':request['run_relative']}, ctx.u) == request['namespace_population'],
            'CLOSING_SUBJECT_READBACK_DRIFT')
    return {'currentness': True, 'refs_unchanged': True, 'documents_unchanged': True, 'phase_left_open': True}
