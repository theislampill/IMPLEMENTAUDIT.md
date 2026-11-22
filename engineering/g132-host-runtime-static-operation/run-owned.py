#!/usr/bin/python3.12
"""Selected public runtime as static data; expected provider only, no original admission."""
from contextlib import contextmanager, ExitStack
import hashlib
import json
import os
from pathlib import Path
import re
import resource
import signal
import stat
import sys
import types

SOURCE_COMMIT = 'c53ed7de85de22ce313233472c8d8f02ad8e9d02'
SOURCE_TREE = 'd60733459425a059d961b6adc2aae9811bbb761c'
BASE_COMMIT = '760aaff5c478ff7354d36da186d62daba983aa49'
OPERATION = 'G132_HOST_RUNTIME_STATIC_20261122_01'
REF = 'refs/heads/pro/dg16-g132-host-runtime-static-20261122-01'
WORKFLOW_REF = 'theislampill/IMPLEMENTAUDIT.md/.github/workflows/dg16-g132-host-runtime-static.yml@' + REF
DRIVER = 'test-support/g132-boot-nss/ordinary_qualifier.py'
DRIVER_PIN = {'bytes': 14658, 'sha256': '5eea85cd1dc76c4edc2e24141da8c76ead9167231bee7a6b85743dcd4cd7e382'}
SETUP_PIN = {'bytes': 91535, 'sha256': '37c14d5c8ff0f6f3f8d252049be4fa0d90b4217861c3fb4dd0a740cc9248f592'}
LOADER_PIN = {'bytes': 59775, 'sha256': '8c31e2eb561937f686ccd553de748dee9ac01066ed3ae9f0266f6975c53a810d'}
PHASES = ('context', 'prepare', 'inputs', 'collect')
STATIC_FILES = {'runtime_static.py': {'bytes': 82827, 'sha256': '4eec99e3185f42d4128b74cab3b21b73359cb4ce07ad5cdbd8eeb41a13d53ec1'}, 'SOURCE_SELECTION.json': {'bytes': 34041, 'sha256': '7f9c4e18b5bf9b111b2854f5d21730d0acde3b41f373e7d47e5b442ee0985cf2'}, 'expected-provider.whl': {'bytes': 851127, 'sha256': '9ba214f4f45bec195ee8559651154d3ac2932470b9d91c5715fc29c013349f8c'}, 'retained-cache.bin': {'bytes': 38836, 'sha256': 'b0b5f4c96e3aedcc1c035c54839b5c39b92ff95a5359726052ba200474f0dc4b'}}


def need(value, message):
    if not value:
        raise ValueError(message)


def identity(value):
    return (value.st_dev, value.st_ino, value.st_mode, value.st_nlink,
            value.st_size, value.st_uid, value.st_gid, value.st_mtime_ns, value.st_ctime_ns)


def write_receipt(path, row, maximum):
    raw = (json.dumps(row, sort_keys=True, separators=(',', ':')) + '\n').encode()
    need(len(raw) <= maximum, 'ordinary report exceeds bound')
    fd = os.open(path, os.O_RDWR | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC, 0o600)
    try:
        offset = 0
        while offset < len(raw):
            count = os.write(fd, raw[offset:])
            need(count > 0, 'ordinary report write stalled')
            offset += count
        os.fsync(fd)
        need(os.pread(fd, len(raw) + 1, 0) == raw and identity(os.fstat(fd)) == identity(os.lstat(path)),
             'ordinary report closing readback differs')
    finally:
        os.close(fd)


@contextmanager
def selected_driver(root):
    path = root / DRIVER
    fd = os.open(path, os.O_RDONLY | os.O_NONBLOCK | os.O_NOFOLLOW | os.O_CLOEXEC)
    try:
        before = os.fstat(fd)
        if not stat.S_ISREG(before.st_mode) or before.st_nlink != 1 or before.st_size != DRIVER_PIN['bytes']:
            raise ValueError('operator driver kind/size differs')
        raw = os.pread(fd, DRIVER_PIN['bytes'] + 1, 0)
        if dict(bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest()) != DRIVER_PIN:
            raise ValueError('operator exact driver pin differs')
        module = types.ModuleType('g132_selected_ordinary_driver')
        module.__file__ = str(path)
        exec(compile(raw, str(path), 'exec'), module.__dict__)
        opening = module.identity(before)
        module.need(module.identity(os.lstat(path)) == opening == module.identity(os.fstat(fd)), 'operator driver opening differs')
        yield module
        module.need(module.identity(os.lstat(path)) == opening == module.identity(os.fstat(fd))
                    and os.pread(fd, len(raw) + 1, 0) == raw, 'operator driver closing differs')
    finally:
        os.close(fd)


def limits(driver):
    for which, key in ((resource.RLIMIT_AS, 'address_bytes'), (resource.RLIMIT_CPU, 'cpu_seconds'),
                       (resource.RLIMIT_FSIZE, 'file_bytes'), (resource.RLIMIT_NOFILE, 'descriptors')):
        value = driver.LIMITS[key]
        resource.setrlimit(which, (value, value))
    signal.signal(signal.SIGALRM, driver.interrupted)
    signal.signal(signal.SIGTERM, driver.interrupted)
    signal.alarm(driver.LIMITS['wall_seconds'])


def exact_payload(driver, path):
    fd = os.open(path, os.O_RDONLY | os.O_NONBLOCK | os.O_NOFOLLOW | os.O_CLOEXEC)
    try:
        before = os.fstat(fd)
        driver.need(stat.S_ISREG(before.st_mode) and before.st_nlink == 1
                    and 0 <= before.st_size <= driver.LIMITS['report_bytes'], 'ordinary delivery file kind/size differs')
        raw = os.pread(fd, driver.LIMITS['report_bytes'] + 1, 0)
        opening = driver.identity(before)
        driver.need(len(raw) == before.st_size and driver.identity(os.fstat(fd)) == opening
                    and driver.identity(os.lstat(path)) == opening, 'ordinary delivery file readback differs')
        return raw
    finally:
        os.close(fd)


def copy_exact(driver, directory, name, raw):
    """Create one public export member through the held fresh directory."""
    fd = os.open(name, os.O_RDWR | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC,
                 0o600, dir_fd=directory)
    try:
        offset = 0
        while offset < len(raw):
            count = os.write(fd, raw[offset:])
            driver.need(count > 0, 'ordinary exact export write stalled')
            offset += count
        os.fchmod(fd, 0o444)
        os.fsync(fd)
        current = driver.identity(os.fstat(fd))
        driver.need(os.pread(fd, len(raw) + 1, 0) == raw
                    and current == driver.identity(os.stat(name, dir_fd=directory, follow_symlinks=False)),
                    'ordinary exact export readback differs')
        return current
    finally:
        os.close(fd)


def verify_export(driver, directory, payloads, created):
    """Verify the finite closed export, including manifest bytes, before release."""
    driver.need(set(os.listdir(directory)) == set(payloads), 'ordinary export population differs')
    total, held = 0, []
    try:
        for name, expected in payloads.items():
            fd = os.open(name, os.O_RDONLY | os.O_NONBLOCK | os.O_NOFOLLOW | os.O_CLOEXEC, dir_fd=directory)
            held.append((name, fd, expected))
            before = os.fstat(fd)
            driver.need(stat.S_ISREG(before.st_mode) and stat.S_IMODE(before.st_mode) == 0o444
                        and before.st_nlink == 1 and (before.st_uid, before.st_gid) == (os.geteuid(), os.getegid())
                        and 0 <= before.st_size <= driver.LIMITS['report_bytes'], 'ordinary export member metadata differs')
            raw = os.pread(fd, driver.LIMITS['report_bytes'] + 1, 0)
            opening = driver.identity(before)
            driver.need(raw == expected and len(raw) == before.st_size
                        and opening == created[name] == driver.identity(os.fstat(fd))
                        == driver.identity(os.stat(name, dir_fd=directory, follow_symlinks=False)),
                        'ordinary export member closing custody differs')
            total += len(raw)
        # Keep all members open through the complete receive; later reads cannot
        # hide drift of an earlier member. This remains a closing snapshot.
        for name, fd, expected in held:
            driver.need(os.pread(fd, driver.LIMITS['report_bytes'] + 1, 0) == expected
                        and created[name] == driver.identity(os.fstat(fd))
                        == driver.identity(os.stat(name, dir_fd=directory, follow_symlinks=False)),
                        'ordinary held export closing bookend differs')
        driver.need(total <= driver.LIMITS['report_bytes'], 'ordinary export including manifest exceeds report bound')
        driver.need(set(os.listdir(directory)) == set(payloads), 'ordinary export closing population differs')
        return total
    finally:
        close_error = None
        for _, fd, _ in reversed(held):
            try:
                os.close(fd)
            except OSError as error:
                close_error = error
        if close_error is not None:
            raise close_error


def collect(driver, context, prepared):
    """Release only a fresh verified finite public export; failures never upload."""
    parent = Path(os.environ['RUNNER_TEMP'])
    logs = parent / ('g132-host-runtime-static-logs-' + context['run_id'] + '-1')
    export = parent / ('g132-host-runtime-static-export-' + context['run_id'] + '-1')
    owner = Path(os.environ['GITHUB_WORKSPACE']).lstat()
    before = logs.lstat()
    driver.need(parent.is_absolute() and parent.resolve() == parent and logs.resolve() == logs
                and stat.S_ISDIR(before.st_mode) and stat.S_IMODE(before.st_mode) == 0o700
                and (before.st_uid, before.st_gid) == (owner.st_uid, owner.st_gid), 'ordinary source log owner differs')
    observed = parent / ('g132-host-runtime-static-observation-' + context['run_id'] + '-1')
    population = [('preparation.json', prepared / 'preparation.json')]
    population += [(name, observed / name) for name in ('context.json', 'inputs.json')]
    population += [(phase + '.' + suffix, logs / (phase + '.' + suffix))
                   for phase in PHASES[:-1] for suffix in ('stdout', 'stderr', 'status')]
    retained, payloads, aggregate = [], {}, 0
    for name, path in population:
        try:
            path.lstat()
        except FileNotFoundError:
            retained.append(dict(name=name, present=False))
            continue
        raw = exact_payload(driver, path)
        aggregate += len(raw)
        driver.need(aggregate <= driver.LIMITS['report_bytes'], 'ordinary selected payloads exceed report bound')
        payloads[name] = raw
        retained.append(dict(name=name, present=True, bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest(),
                             exact_source_bytes_retained=True))
    manifest = dict(schema='g132.host-runtime-static-ordinary-delivery.v1', authority='NONE', context=context,
                    source_commit=SOURCE_COMMIT, source_tree=SOURCE_TREE, files=retained,
                    aggregate_bytes=aggregate, aggregate_scope='PRESENT_PAYLOADS_EXCLUDING_MANIFEST',
                    report_bound_bytes=driver.LIMITS['report_bytes'], report_bound_includes_manifest=True,
                    admission='UNQUALIFIED', original_execution=False)
    payloads['manifest.json'] = (json.dumps(manifest, sort_keys=True, separators=(',', ':')) + '\n').encode()
    total = sum(len(raw) for raw in payloads.values())
    driver.need(total <= driver.LIMITS['report_bytes'], 'ordinary export including manifest exceeds report bound')
    # No export exists before the complete bound passes. A collision refuses;
    # partial failed exports are retained, never reused or deleted by this owner.
    parent_fd = os.open(parent, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC)
    try:
        parent_open = os.fstat(parent_fd)
        parent_anchor = (parent_open.st_dev, parent_open.st_ino, parent_open.st_mode,
                         parent_open.st_uid, parent_open.st_gid)
        os.mkdir(export.name, mode=0o700, dir_fd=parent_fd)
        directory = os.open(export.name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC,
                            dir_fd=parent_fd)
        try:
            opening = os.fstat(directory)
            driver.need(stat.S_ISDIR(opening.st_mode) and stat.S_IMODE(opening.st_mode) == 0o700
                        and (opening.st_uid, opening.st_gid) == (os.geteuid(), os.getegid())
                        and driver.identity(opening) == driver.identity(os.stat(export.name, dir_fd=parent_fd, follow_symlinks=False)),
                        'ordinary fresh export directory binding differs')
            created = {name: copy_exact(driver, directory, name, raw) for name, raw in payloads.items()}
            os.fsync(directory)
            os.fchmod(directory, 0o555)
            os.fsync(directory)
            driver.need(verify_export(driver, directory, payloads, created) == total,
                        'ordinary export verification total differs')
            closing = os.fstat(directory)
            driver.need((closing.st_dev, closing.st_ino, closing.st_uid, closing.st_gid)
                        == (opening.st_dev, opening.st_ino, opening.st_uid, opening.st_gid)
                        and stat.S_IMODE(closing.st_mode) == 0o555
                        and driver.identity(closing) == driver.identity(os.stat(export.name, dir_fd=parent_fd, follow_symlinks=False)),
                        'ordinary export closing directory binding differs')
        finally:
            os.close(directory)
        os.fsync(parent_fd)
        for value in (os.fstat(parent_fd), os.lstat(parent)):
            driver.need((value.st_dev, value.st_ino, value.st_mode, value.st_uid, value.st_gid) == parent_anchor,
                        'ordinary export parent closing binding differs')
    finally:
        os.close(parent_fd)
    # Successful return is required by the workflow's explicit upload gate.
    # Named readbacks remain snapshots; no privileged-writer exclusion is claimed.
    print(json.dumps(dict(phase='collect', authority='NONE', aggregate_bytes=aggregate,
                          export_bytes_including_manifest=total, export_verified=True,
                          original_execution=False, path=str(export)), sort_keys=True))
    return 0


def context_from(environment, process_identity, boot_id):
    """Separate the public context facts from the requested image predicate."""
    expected = dict(GITHUB_ACTIONS='true', RUNNER_ENVIRONMENT='github-hosted',
                    GITHUB_REPOSITORY='theislampill/IMPLEMENTAUDIT.md', GITHUB_RUN_ATTEMPT='1',
                    GITHUB_EVENT_NAME='push', GITHUB_JOB='qualify', GITHUB_REF=REF)
    keys = tuple(expected) + ('GITHUB_RUN_ID', 'GITHUB_SHA', 'GITHUB_WORKFLOW_SHA',
                              'GITHUB_WORKFLOW_REF', 'ImageOS', 'ImageVersion')
    values, issues = {}, []
    for key in keys:
        value = environment.get(key)
        if value is None or (type(value) is str and len(value.encode()) <= 512):
            values[key] = value
        else:
            # Retain only a bounded descriptor for an over-bound public field.
            raw = str(value).encode()
            values[key] = dict(bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest(),
                               disposition='OVER_BOUND_VALUE_NOT_EXPORTED')
            issues.append(key)
    for key, wanted in expected.items():
        if values[key] != wanted:
            issues.append(key)
    host = values['GITHUB_SHA']
    run = values['GITHUB_RUN_ID']
    if (type(host) is not str or re.fullmatch('[0-9a-f]{40}', host) is None
            or values['GITHUB_WORKFLOW_SHA'] != host or values['GITHUB_WORKFLOW_REF'] != WORKFLOW_REF):
        issues.append('host_workflow_identity')
    if type(run) is not str or re.fullmatch('[1-9][0-9]{0,19}', run) is None:
        issues.append('run_identity')
    if process_identity != dict(uid=0, euid=0, gid=0, egid=0):
        issues.append('root_identity')
    if type(boot_id) is not str or re.fullmatch('[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}', boot_id) is None:
        issues.append('boot_identity')
    requested = dict(ImageOS='ubuntu24', ImageVersion='20261116.133.1')
    return dict(values, operation=OPERATION, run_id=run, host_commit=host,
                workflow_ref=values['GITHUB_WORKFLOW_REF'], boot_id=boot_id,
                identity=process_identity, provider_matches=not issues,
                provider_issues=sorted(set(issues)), requested_image=requested,
                requested_image_matches=all(values[key] == value for key, value in requested.items()),
                image_adopted=False, overall_admission='UNQUALIFIED')


def capture_context():
    # No image comparison throws before the actual bounded public facts exist.
    try:
        with open('/proc/sys/kernel/random/boot_id', 'rb') as stream:
            boot = stream.read(65).decode('ascii').strip()
    except (OSError, UnicodeError):
        boot = None
    return context_from(os.environ,
                        dict(uid=os.getuid(), euid=os.geteuid(), gid=os.getgid(), egid=os.getegid()), boot)


def output_paths():
    run = os.environ.get('GITHUB_RUN_ID', '')
    need(re.fullmatch('[1-9][0-9]{0,19}', run), 'host image bounded run identity required for output paths')
    parent = Path(os.environ['RUNNER_TEMP'])
    workspace = Path(os.environ['GITHUB_WORKSPACE'])
    need(parent.is_absolute() and parent.resolve() == parent
         and workspace.is_absolute() and workspace.resolve() == workspace,
         'host image output/source alias refused')
    return (workspace,
            parent / ('g132-host-runtime-static-logs-' + run + '-1'),
            parent / ('g132-host-runtime-static-observation-' + run + '-1'),
            parent / ('g132-host-runtime-static-source-preparation-' + run + '-1'))


def private_directory(path, create=False):
    if create:
        path.mkdir(mode=0o700)
    current = path.lstat()
    need(path.resolve() == path and stat.S_ISDIR(current.st_mode) and stat.S_IMODE(current.st_mode) == 0o700
         and (current.st_uid, current.st_gid) == (os.geteuid(), os.getegid()),
         'host image private output directory custody differs')


@contextmanager
def context_binding(driver, context, observed, logs):
    with driver.held_bytes(observed / 'context.json', driver.LIMITS['report_bytes']) as raw:
        row = json.loads(raw)
        need(row.get('schema') == 'g132.host-runtime-static-context.v1' and row.get('authority') == 'NONE'
             and row.get('operation') == OPERATION and row.get('phase') == 'context'
             and row.get('source_commit') == SOURCE_COMMIT and row.get('source_tree') == SOURCE_TREE
             and row.get('context') == context and row.get('closing_context') == context
             and row.get('context_bookends_equal') is True and row.get('observation_complete') is True
             and row.get('overall_admission') == 'UNQUALIFIED' and row.get('image_adopted') is False
             and 'failure' not in row and exact_payload(driver, logs / 'context.status') == b'0\n',
             'host image prior context receipt or phase status differs')
        yield dict(bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest())


@contextmanager
def prepared_binding(driver, context, prepared, logs):
    with driver.held_bytes(prepared / 'preparation.json', driver.LIMITS['report_bytes']) as raw:
        row = json.loads(raw)
        need(row.get('schema') == 'g132.host-runtime-static-preparation.v1' and row.get('authority') == 'NONE'
             and row.get('operation') == OPERATION and row.get('phase') == 'prepare'
             and row.get('observation_complete') is True and 'failure' not in row
             and row.get('context') == context and row.get('closing_context') == context
             and row.get('context_bookends_equal') is True and row.get('source_commit') == SOURCE_COMMIT
             and row.get('source_tree') == SOURCE_TREE and row.get('source_parent') == BASE_COMMIT
             and row.get('descriptor_restoration') is True
             and exact_payload(driver, logs / 'prepare.status') == b'0\n',
             'host image preparation source/provider/boot receipt or phase status differs')
        yield dict(bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest())


def preparation(driver, context, target, row):
    with driver.owner('qualify-work-graph-c5-setup.py', driver.SETUP_PIN) as setup:
        baseline = setup.fds()
        received = setup.prepare_hosted_source_selected_v3(driver.ROOT, target, SOURCE_COMMIT,
                   BASE_COMMIT, records=row['source_commands'])
        need(received['source_commit'] == SOURCE_COMMIT and received['source_tree'] == SOURCE_TREE
             and received['ordered_parents'] == [BASE_COMMIT], 'host image prepared source identity differs')
        row['source'] = received
        with selected_driver(target / 'source') as fresh:
            need(fresh.SETUP_PIN == driver.SETUP_PIN and fresh.LIMITS == driver.LIMITS
                 and fresh.BASE_COMMIT == BASE_COMMIT, 'host image prepared source pins differ')
        row['descriptor_restoration'] = setup.fds() == baseline
        need(row['descriptor_restoration'], 'host image preparation descriptor restoration differs')




def inputs(driver, row):
    # The unchanged utility/setup own source custody only. No provider, NSS,
    # original harness, loader admission or subject executable is invoked.
    with driver.legacy() as previous, previous.owner('qualify-work-graph-c5-setup.py', driver.SETUP_PIN) as setup:
        previous.source_identity(setup, SOURCE_COMMIT, SOURCE_TREE, row['source_commands'])
        baseline = setup.fds()
        source_directory = Path(__file__).resolve().parent
        with ExitStack() as held:
            sources = {name: held.enter_context(driver.held_bytes(source_directory / name,
                         expected['bytes'], expected)) for name, expected in STATIC_FILES.items()}
            module = types.ModuleType('g132_selected_public_static_data')
            module.__file__ = str(source_directory / 'runtime_static.py')
            exec(compile(sources['runtime_static.py'], module.__file__, 'exec'), module.__dict__)
            contract = module.strict_json(sources['SOURCE_SELECTION.json'])
            need(contract['source_commit'] == SOURCE_COMMIT and contract['source_tree'] == SOURCE_TREE,
                 'static selection source identity differs')
            for name, expected in contract['source_owners'].items():
                held.enter_context(driver.held_bytes(driver.ROOT / name, expected['bytes'],
                                   {key: expected[key] for key in ('bytes', 'sha256')}))
            row['static_source_bindings'] = STATIC_FILES
            row['selected_source_owners'] = contract['source_owners']
            with module.Capture('/', contract, sources['expected-provider.whl'], sources['retained-cache.bin']) as capture:
                capture.opening()
                observed = capture.closing()
            maximum = driver.LIMITS['report_bytes'] - len(module.canonical(row)) - 262144
            need(maximum >= 1024, 'static public report envelope exhausted')
            raw = module.encode_report(observed, maximum=maximum)
            row['runtime_static'] = module.strict_json(raw)
            try:
                row['runtime_static_receiving'] = module.receive(raw, contract,
                    sources['expected-provider.whl'], sources['retained-cache.bin'])
            except module.Refusal as error:
                row['runtime_static_receiving'] = dict(accepted=False, authority='NONE',
                    complete_selected_public_static_surface=False, reason=error.code)
            row['complete_selected_public_static_surface'] = (
                row['runtime_static_receiving'].get('accepted') is True
                and row['runtime_static'].get('complete_selected_public_static_surface') is True)
            row['raw_host_elf_bodies_exported'] = False
            row['raw_account_bodies_exported'] = False
            row['raw_cache_body_exported'] = False
            row['provider_state'] = 'EXPECTED_ONLY_NO_INSTALL_OR_IMPORT'
        previous.source_identity(setup, SOURCE_COMMIT, SOURCE_TREE, row['source_commands'])
        row['descriptor_restoration'] = setup.fds() == baseline
        need(row['descriptor_restoration'], 'static observation descriptor restoration differs')


def main(argv=None):
    arguments = list(sys.argv[1:] if argv is None else argv)
    if len(arguments) != 1 or arguments[0] not in PHASES:
        raise ValueError('host image operator requires one finite read-only phase')
    phase = arguments[0]
    workspace, logs, observed, prepared = output_paths()
    root = prepared / 'source' if phase == 'inputs' else workspace
    if phase == 'collect':
        try:
            with selected_driver(root) as driver:
                limits(driver)
                context = capture_context()
                need(context['provider_matches'], 'host image collector provider identity differs')
                result = collect(driver, context, prepared)
                need(capture_context() == context, 'host image collector closing context differs')
            return result
        finally:
            signal.alarm(0)
    if phase == 'context':
        private_directory(observed, create=True)
    elif phase == 'prepare':
        private_directory(prepared, create=True)
        private_directory(observed)
    else:
        private_directory(observed)
    target = prepared / 'preparation.json' if phase == 'prepare' else observed / (phase + '.json')
    schemas = dict(context='g132.host-runtime-static-context.v1', prepare='g132.host-runtime-static-preparation.v1',
                   inputs='g132.host-runtime-static-inputs.v1')
    row = dict(schema=schemas[phase], operation=OPERATION, authority='NONE', phase=phase,
               source_commit=SOURCE_COMMIT, source_tree=SOURCE_TREE, source_parent=BASE_COMMIT,
               setup_pin=SETUP_PIN, loader_pin=LOADER_PIN, source_commands=[], observation_complete=False,
               overall_admission='UNQUALIFIED', image_adopted=False, native_admission=False,
               original_execution=False, private_inputs_selected=False, provider_acquired=False,
               session_constructed=False, administrative_operations=False,
               copied_runtime_provisioning='UNPERFORMED_SEPARATE_ORIGINAL_OWNER')
    success = False
    try:
        with selected_driver(root) as driver:
            limits(driver)
            row['limits'] = driver.LIMITS
            context = capture_context()
            row['context'] = context
            if phase != 'context':
                need(context['provider_matches'], 'host image observer provider identity differs')
                with context_binding(driver, context, observed, logs) as binding:
                    row['context_receipt'] = binding
                    if phase == 'prepare':
                        preparation(driver, context, prepared, row)
                    else:
                        with prepared_binding(driver, context, prepared, logs) as prepared_receipt:
                            row['preparation_receipt'] = prepared_receipt
                            inputs(driver, row)
            row['closing_context'] = capture_context()
            row['context_bookends_equal'] = row['closing_context'] == context
            need(context['provider_matches'], 'host image observer provider identity differs')
            need(row['context_bookends_equal'], 'host image closing context differs')
        # Held utility/setup/loader exits have completed before this flag and
        # receipt are written. A late source closing failure remains a failure.
        success = True
    except BaseException as error:
        row['failure'] = dict(type=type(error).__name__, reason=str(error)[:512])
    finally:
        signal.alarm(0)
    row['observation_complete'] = success
    write_receipt(target, row, 2097152)
    print(json.dumps(dict(operation=OPERATION, phase=phase, observation_complete=success,
                          requested_image_matches=row.get('context', {}).get('requested_image_matches'),
                          image_adopted=False, overall_admission='UNQUALIFIED', output=str(target)), sort_keys=True))
    return 0 if success else 2


if __name__ == '__main__':
    raise SystemExit(main())
