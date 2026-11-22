#!/usr/bin/python3.12
"""Provider-bound ordinary boot NSS operator; R2 releases only a bounded verified public export."""
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

SOURCE_COMMIT = 'c53ed7de85de22ce313233472c8d8f02ad8e9d02'
SOURCE_TREE = 'd60733459425a059d961b6adc2aae9811bbb761c'
BASE_COMMIT = '760aaff5c478ff7354d36da186d62daba983aa49'
DRIVER = 'test-support/g132-boot-nss/ordinary_qualifier.py'
DRIVER_PIN = {'bytes': 14658, 'sha256': '5eea85cd1dc76c4edc2e24141da8c76ead9167231bee7a6b85743dcd4cd7e382'}
PHASES = ('prepare', 'launcher', 'policy', 'boot-nss', 'namespace', 'inputs', 'nss-finalize', 'finalize', 'collect')


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
    result = dict(schema='g132.boot-nss-source-preparation.v1', authority='NONE', context=context,
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



@contextmanager
def prepared_binding(driver, context, prepared):
    with driver.held_bytes(prepared / 'preparation.json', driver.LIMITS['report_bytes']) as raw:
        row = json.loads(raw)
        driver.need(row.get('schema') == 'g132.boot-nss-source-preparation.v1'
                    and row.get('authority') == 'NONE' and row.get('complete') is True
                    and row.get('context') == context and row.get('source_commit') == SOURCE_COMMIT
                    and row.get('source_tree') == SOURCE_TREE and row.get('source_parent') == BASE_COMMIT,
                    'ordinary preparation source/provider/boot receipt differs')
        yield


def collect(driver, context, prepared):
    """Release only a fresh verified finite public export; failures never upload."""
    parent = Path(os.environ['RUNNER_TEMP'])
    logs = parent / ('g132-boot-nss-logs-' + context['run_id'] + '-1')
    export = parent / ('g132-boot-nss-export-' + context['run_id'] + '-1')
    owner = Path(os.environ['GITHUB_WORKSPACE']).lstat()
    before = logs.lstat()
    driver.need(parent.is_absolute() and parent.resolve() == parent and logs.resolve() == logs
                and stat.S_ISDIR(before.st_mode) and stat.S_IMODE(before.st_mode) == 0o700
                and (before.st_uid, before.st_gid) == (owner.st_uid, owner.st_gid), 'ordinary source log owner differs')
    observed = parent / ('g132-boot-nss-observation-' + context['run_id'] + '-1')
    population = [('preparation.json', prepared / 'preparation.json')]
    population += [(name, observed / name) for name in ('boot-nss.json', 'namespace.json', 'inputs.json', 'nss-finalize.json')]
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
    manifest = dict(schema='g132.boot-nss-ordinary-delivery.v2', authority='NONE', context=context,
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



def main():
    if len(sys.argv) != 2 or sys.argv[1] not in PHASES:
        raise ValueError('operator requires one finite phase')
    phase = sys.argv[1]
    run = os.environ.get('GITHUB_RUN_ID', '')
    prepared = Path(os.environ['RUNNER_TEMP']) / ('g132-boot-nss-source-preparation-' + run + '-1')
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
        if phase == 'nss-finalize':
            # Read-only receipt/journal observation cannot recover failed prior custody.
            return driver.main(['--step', phase, '--source-commit', SOURCE_COMMIT, '--source-tree', SOURCE_TREE])
        with prepared_binding(driver, context, prepared):
            if phase in ('boot-nss', 'namespace', 'inputs'):
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
