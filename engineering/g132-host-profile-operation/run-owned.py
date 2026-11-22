#!/usr/bin/python3.12
"""Frozen prospective ordinary operator; not executed by candidate preparation."""
from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import resource
import signal
import stat
import sys
import types

SOURCE_COMMIT = '4ddd6403b70835339b6f55aeff9478b6d061247b'
SOURCE_TREE = '969df99854f9ca87fda54f21585864d7a0d61a38'
BASE_COMMIT = '760aaff5c478ff7354d36da186d62daba983aa49'
DRIVER = 'test-support/g132-host-profile-successor/ordinary_qualifier.py'
DRIVER_PIN = {'bytes': 14021, 'sha256': 'e316224f5492241b529161d37b4dbce5c63f6cfc038d0c750db82aae3de13a8e'}
PHASES = ('prepare', 'launcher', 'policy', 'namespace', 'inputs', 'finalize', 'collect')


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


def preparation(driver, context, target):
    target.mkdir(mode=0o700)  # Exclusive. No retry, no resumption or copied .git.
    result = dict(schema='g132.host-profile-preparation.v1', authority='NONE', context=context,
                  source_commit=SOURCE_COMMIT, source_tree=SOURCE_TREE, source_parent=BASE_COMMIT,
                  source_commands=[], complete=False, original_execution=False,
                  private_inputs_selected=False, credential_source='NONE')
    success = False
    try:
        with driver.owner('qualify-work-graph-c5-setup.py', driver.SETUP_PIN) as setup:
            baseline = setup.fds()
            received = setup.prepare_hosted_source_selected_v3(driver.ROOT, target, SOURCE_COMMIT,
                       BASE_COMMIT, records=result['source_commands'])
            driver.need(received['source_commit'] == SOURCE_COMMIT and received['source_tree'] == SOURCE_TREE
                        and received['ordered_parents'] == [BASE_COMMIT], 'prepared source identity differs')
            driver.need(setup.fds() == baseline, 'prepared source descriptor restoration differs')
            result['source'] = received
            with selected_driver(target / 'source') as fresh:
                fresh.need(fresh.SETUP_PIN == driver.SETUP_PIN and fresh.NSS_PIN == driver.NSS_PIN,
                           'prepared source pins differ')
            driver.need(driver.hosted_context() == context, 'source preparation context closing differs')
            result['complete'] = True
            success = True
    except BaseException as error:
        result['failure'] = dict(type=type(error).__name__, reason=str(error)[:512])
    finally:
        signal.alarm(0)
        driver.write_receipt(target / 'preparation.json', result, driver.LIMITS['report_bytes'])
    print(json.dumps(dict(phase='prepare', complete=success, source_commit=SOURCE_COMMIT,
                          source_tree=SOURCE_TREE, authority='NONE'), sort_keys=True))
    return 0 if success else 2


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


def copy_exact(driver, path, raw):
    fd = os.open(path, os.O_RDWR | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC, 0o600)
    try:
        offset = 0
        while offset < len(raw):
            count = os.write(fd, raw[offset:])
            driver.need(count > 0, 'ordinary exact delivery write stalled')
            offset += count
        os.fsync(fd)
        driver.need(os.pread(fd, len(raw) + 1, 0) == raw
                    and driver.identity(os.fstat(fd)) == driver.identity(os.lstat(path)), 'ordinary exact delivery readback differs')
        os.fchmod(fd, 0o644)
    finally:
        os.close(fd)


@contextmanager
def prepared_binding(driver, context, prepared):
    with driver.held_bytes(prepared / 'preparation.json', driver.LIMITS['report_bytes']) as raw:
        row = json.loads(raw)
        driver.need(row.get('schema') == 'g132.host-profile-preparation.v1'
                    and row.get('authority') == 'NONE' and row.get('complete') is True
                    and row.get('context') == context and row.get('source_commit') == SOURCE_COMMIT
                    and row.get('source_tree') == SOURCE_TREE and row.get('source_parent') == BASE_COMMIT,
                    'ordinary preparation source/provider/boot receipt differs')
        yield


def collect(driver, context, prepared):
    """Copy only named public receipts to the runner's private delivery folder."""
    out = Path(os.environ['RUNNER_TEMP']) / ('g132-host-profile-logs-' + context['run_id'] + '-1')
    owner = Path(os.environ['GITHUB_WORKSPACE']).lstat()
    before = out.lstat()
    driver.need(out.resolve() == out and stat.S_ISDIR(before.st_mode) and stat.S_IMODE(before.st_mode) == 0o700
                and (before.st_uid, before.st_gid) == (owner.st_uid, owner.st_gid), 'ordinary delivery owner differs')
    observed = Path(os.environ['RUNNER_TEMP']) / ('g132-host-profile-successor-' + context['run_id'] + '-1')
    population = [('preparation.json', prepared / 'preparation.json')]
    population += [(name, observed / name) for name in ('namespace.json', 'inputs.json', 'nss.json')]
    retained = []
    aggregate = 0
    for name, path in population:
        try:
            path.lstat()
        except FileNotFoundError:
            retained.append(dict(name=name, present=False))
            continue
        raw = exact_payload(driver, path)
        copy_exact(driver, out / name, raw)
        retained.append(dict(name=name, present=True, bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest(),
                             exact_source_bytes_retained=True))
        aggregate += len(raw)
    for phase in PHASES[:-1]:
        for suffix in ('stdout', 'stderr', 'status'):
            name = phase + '.' + suffix
            path = out / name
            try:
                info = path.lstat()
            except FileNotFoundError:
                retained.append(dict(name=name, present=False))
                continue
            raw = exact_payload(driver, path)
            retained.append(dict(name=name, present=True, bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest()))
            aggregate += len(raw)
    driver.need(aggregate <= driver.LIMITS['report_bytes'], 'aggregate ordinary delivery exceeds original report bound')
    driver.write_receipt(out / 'manifest.json', dict(schema='g132.host-profile-ordinary-delivery.v1', authority='NONE',
        context=context, source_commit=SOURCE_COMMIT, source_tree=SOURCE_TREE, files=retained,
        aggregate_bytes=aggregate, admission='UNQUALIFIED', original_execution=False), driver.LIMITS['report_bytes'])
    os.chmod(out / 'manifest.json', 0o644)
    print(json.dumps(dict(phase='collect', authority='NONE', aggregate_bytes=aggregate,
                          original_execution=False, path=str(out)), sort_keys=True))
    return 0


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in PHASES:
        raise ValueError('operator requires one finite phase')
    phase = sys.argv[1]
    run = os.environ.get('GITHUB_RUN_ID', '')
    prepared = Path(os.environ['RUNNER_TEMP']) / ('g132-host-profile-preparation-' + run + '-1')
    root = Path(os.environ['GITHUB_WORKSPACE']) if phase in ('prepare', 'collect') else prepared / 'source'
    with selected_driver(root) as driver:
        context = driver.hosted_context()
        limits(driver)
        if phase == 'prepare':
            return preparation(driver, context, prepared)
        if phase == 'collect':
            return collect(driver, context, prepared)
        if phase == 'finalize':
            # Always attempt the unchanged read-only finalizer, even if an earlier
            # receipt is partial. This never unloads policy or removes its receipt.
            with driver.owner('qualify-work-graph-c5-setup.py', driver.SETUP_PIN) as setup:
                return setup.finalize_hosted_bwrap_policy()
        with prepared_binding(driver, context, prepared):
            if phase in ('namespace', 'inputs'):
                return driver.main(['--step', phase, '--source-commit', SOURCE_COMMIT, '--source-tree', SOURCE_TREE])
            with driver.owner('qualify-work-graph-c5-setup.py', driver.SETUP_PIN) as setup:
                actions = {'launcher': setup.provision_hosted_launcher,
                           'policy': setup.provision_hosted_bwrap_policy}
                try:
                    return actions[phase]()
                finally:
                    setup.emergency_cleanup()


if __name__ == '__main__':
    raise SystemExit(main())
