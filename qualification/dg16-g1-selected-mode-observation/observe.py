"""One exact selected acquisition observation on an independently admitted host."""
import contextlib
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import shutil
import signal
import stat
import sys
import time
import types

BRANCH = 'pro/dg16-g1-selected-mode-observation-01-20261110'
WORKFLOW = '.github/workflows/dg16-g1-selected-mode-observation.yml'
REPOSITORY = 'theislampill/IMPLEMENTAUDIT.md'
IMAGE = '20261101.360.1'
PRODUCT = '64219c67e9f1dc1e54c6be9ed8e56f26ab313606'
PROVIDER = Path('/usr/lib/implementaudit-c5-r5-hosted-python312-05-v1')
# Populated from actual received sources by the offline candidate generator.
PINS = {'PROVIDER_SETUP.json': {'bytes': 2963, 'sha256': 'f0b0b3a4c0dda6705e6ac335fd8d501f718a9fbee23cb3b4450ddede5a57746d'}, 'PUBLIC_PATH_ALLOWLIST.json': {'bytes': 2556, 'sha256': 'f3692f04e93cb8bc260579f037e10924037eef390629150860070a132bf76103'}, 'SOURCE_MANIFEST.json': {'bytes': 494941, 'sha256': 'd926bf518de51aeaf3f6522ce60852a548699583adb3b1805143dfe9554d8548'}, 'host_utility.py': {'bytes': 54556, 'sha256': '8ed45e8adc56907556a247b872ea745653e2bd4e28e54e5b19e4162788ebcce3'}, 'input_setup.py': {'bytes': 11747, 'sha256': 'fea0c04153b43d2bceb0b047ec00a16bdef935fc62043b2d695c8477876d9236'}, 'mode_public_projection.py': {'bytes': 7502, 'sha256': '8b5c42eb89f84a97d12b34e609e3fa00062ced05d18a97312ba6b06467d146df'}, 'nss_configuration.py': {'bytes': 14718, 'sha256': '7243b9a13f9597059d57f22e1cfd4b344a7fd0cee930e9f9d032eee6e9e42270'}, 'observe_selected_modes.py': {'bytes': 4792, 'sha256': '6905748ac568e310bbda01f7f683d6128e916d407f803e850073f40e7151ed8e'}, 'operation.py': {'bytes': 24220, 'sha256': '196e275d6ae23a4d6f6f46cafbc490b6ef4da01cc1058e078c44bb188267427d'}, 'provider_layout.py': {'bytes': 4752, 'sha256': '0ef5ddd7562906552b88cb7638d9a6d1fffd3fdd906ec407c3c56dc2c88dc112'}, 'run.py': {'bytes': 158909, 'sha256': '4c5d7ad4dbe970fda50144d981691cae536d9b7a5ead4d7d6c58842c0b6a704a'}, 'source_store.py': {'bytes': 6898, 'sha256': '100e01f0a5d0d86dad38e17bcae0cd43b3b092bcf4936531780e9e4ebca7a1e5'}}
TERMINAL_MARKER = b'DG16_SELECTED_DIRECTORY_MODE_TERMINAL '
STAGES = ('BOOTSTRAP', 'READ_ONLY_NSS', 'SOURCE_PREPARATION', 'NSS_CONDITIONAL', 'PROVIDER_PREPARATION',
          'FIRST_LAYOUT_OBSERVATION', 'SOURCE_CLOSING', 'CLEANUP')


SAFE_REFUSALS = {'BOOTSTRAP': {'DIAGNOSTIC_ORIGINAL_SOURCE_OWNER': 'DIAGNOSTIC_ORIGINAL_SOURCE_OWNER', 'DIAGNOSTIC_FRESH_ROOTS_REQUIRED': 'DIAGNOSTIC_FRESH_ROOTS_REQUIRED', 'BOUND_DIAGNOSTIC_MEMBER': 'BOUND_DIAGNOSTIC_MEMBER', 'BOUND_DIAGNOSTIC_MEMBER_OPEN': 'BOUND_DIAGNOSTIC_MEMBER_OPEN', 'BOUND_DIAGNOSTIC_MEMBER_READBACK': 'BOUND_DIAGNOSTIC_MEMBER_READBACK', 'MODULE_PIN_REFUSED': 'MODULE_PIN_REFUSED'}, 'READ_ONLY_NSS': {'DIAGNOSTIC_EXACT_NSS_PREIMAGE_REQUIRED': 'DIAGNOSTIC_EXACT_NSS_PREIMAGE_REQUIRED', 'DIAGNOSTIC_EXACT_NSS_POSTIMAGE_REQUIRED': 'DIAGNOSTIC_EXACT_NSS_POSTIMAGE_REQUIRED', 'C5 provider actual passwd NSS is not files-only': 'NSS_FILES_ONLY_REFUSED', 'C5 provider actual NSS input is unsupported': 'NSS_INPUT_REFUSED', 'C5 provider actual UID0 passwd home is unqualified': 'NSS_UID0_REFUSED', 'C5 provider NSCD selector is not closed': 'NSS_NSCD_REFUSED'}, 'SOURCE_PREPARATION': {'ORDINARY_GIT_PREPARATION_REFUSED': 'ORDINARY_GIT_PREPARATION_REFUSED', 'SOURCE_GIT_IDENTITY_REFUSED': 'SOURCE_GIT_IDENTITY_REFUSED', 'SOURCE_TRACKED_STATE_CHANGED': 'SOURCE_TRACKED_STATE_CHANGED'}, 'NSS_CONDITIONAL': {'NSS_CONFIGURATION_PREIMAGE_REFUSED': 'NSS_CONFIGURATION_PREIMAGE_REFUSED', 'NSS_CONFIGURATION_REPLACEMENT_READBACK': 'NSS_CONFIGURATION_REPLACEMENT_READBACK', 'NSS_CONFIGURATION_FINAL_CHANGED': 'NSS_CONFIGURATION_FINAL_CHANGED'}, 'PROVIDER_PREPARATION': {'DIAGNOSTIC_PROVIDER_SPEC_PIN': 'DIAGNOSTIC_PROVIDER_SPEC_PIN', 'DIAGNOSTIC_PROVIDER_ROOT_PIN': 'DIAGNOSTIC_PROVIDER_ROOT_PIN', 'DIAGNOSTIC_PROVIDER_OWNER': 'DIAGNOSTIC_PROVIDER_OWNER', 'VENV_CREATION_REFUSED': 'VENV_CREATION_REFUSED', 'WHEEL_HTTP_REFUSED': 'WHEEL_HTTP_REFUSED', 'PROVIDER_WRITE_READBACK': 'PROVIDER_WRITE_READBACK', 'TRUSTED_ROOT_ANCESTRY_REQUIRED': 'TRUSTED_ROOT_ANCESTRY_REQUIRED'}, 'FIRST_LAYOUT_OBSERVATION': {'DIAGNOSTIC_OBSERVATION_DEADLINE': 'DIAGNOSTIC_OBSERVATION_DEADLINE', 'C5 exact mode diagnostic exceeds inherited manifest bound': 'MODE_PROJECTION_BOUND_REFUSED'}, 'SOURCE_CLOSING': {'DIAGNOSTIC_SOURCE_CLOSING': 'DIAGNOSTIC_SOURCE_CLOSING', 'SOURCE_GIT_IDENTITY_REFUSED': 'SOURCE_GIT_IDENTITY_REFUSED', 'SOURCE_TRACKED_STATE_CHANGED': 'SOURCE_TRACKED_STATE_CHANGED'}, 'CLEANUP': {'DIAGNOSTIC_CLEANUP_PATH': 'DIAGNOSTIC_CLEANUP_PATH', 'DIAGNOSTIC_CLEANUP_PARENT': 'DIAGNOSTIC_CLEANUP_PARENT', 'DIAGNOSTIC_CLEANUP_IDENTITY': 'DIAGNOSTIC_CLEANUP_IDENTITY', 'DIAGNOSTIC_CLEANUP_RETAINED': 'DIAGNOSTIC_CLEANUP_RETAINED', 'DIAGNOSTIC_CLEANUP_PARENT_CHANGED': 'DIAGNOSTIC_CLEANUP_PARENT_CHANGED', 'DIAGNOSTIC_NSS_EFFECT_UNRESOLVED': 'DIAGNOSTIC_NSS_EFFECT_UNRESOLVED'}}

def refusal_code(stage, error):
    if type(error) is Watchdog:
        return 'WATCHDOG_EXPIRED'
    if len(error.args) == 1 and type(error.args[0]) is str:
        return SAFE_REFUSALS.get(stage, {}).get(error.args[0], 'UNCLASSIFIED')
    return 'UNCLASSIFIED'


def need(value, code):
    if not value:
        raise ValueError(code)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def encode(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'),
                      ensure_ascii=True, allow_nan=False).encode('ascii')


def stamp(info):
    return (info.st_dev, info.st_ino, info.st_mode, info.st_nlink, info.st_size,
            info.st_mtime_ns, info.st_ctime_ns, info.st_uid, info.st_gid)


def anchor(info):
    return (info.st_dev, info.st_ino, info.st_mode, info.st_uid, info.st_gid)


def pinned(base, name):
    expected = PINS[name]
    path = base / name
    before = path.lstat()
    need(stat.S_ISREG(before.st_mode) and before.st_nlink == 1
         and before.st_size == expected['bytes'] <= 1024 * 1024, 'BOUND_DIAGNOSTIC_MEMBER')
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK | os.O_CLOEXEC)
    try:
        need(stamp(os.fstat(fd)) == stamp(before), 'BOUND_DIAGNOSTIC_MEMBER_OPEN')
        with os.fdopen(fd, 'rb', closefd=False) as stream:
            raw = stream.read(expected['bytes'] + 1)
        need(len(raw) == expected['bytes'] and sha(raw) == expected['sha256']
             and stamp(os.fstat(fd)) == stamp(path.lstat()) == stamp(before),
             'BOUND_DIAGNOSTIC_MEMBER_READBACK')
        return raw
    finally:
        os.close(fd)


def module(base, name):
    raw = pinned(base, name)
    m = types.ModuleType('selected_mode_' + Path(name).stem)
    m.__file__ = str(base / name)
    exec(compile(raw, m.__file__, 'exec'), m.__dict__)
    return m


def actual_context(packet):
    e = os.environ
    need(os.getuid() == os.geteuid() == os.getgid() == os.getegid() == 0
         and platform.system() == 'Linux' and platform.machine() == 'x86_64'
         and sys.version_info[:3] == (3, 12, 3) and sys.flags.isolated
         and sys.flags.no_site and sys.dont_write_bytecode, 'DIAGNOSTIC_ACTUAL_UID_PLATFORM')
    head = e.get('GITHUB_SHA', '')
    run = e.get('GITHUB_RUN_ID', '')
    need(re.fullmatch('[0-9a-f]{40}', head) and re.fullmatch('[1-9][0-9]{0,19}', run)
         and e.get('GITHUB_ACTIONS') == 'true' and e.get('RUNNER_ENVIRONMENT') == 'github-hosted'
         and e.get('GITHUB_EVENT_NAME') == 'push' and e.get('GITHUB_RUN_ATTEMPT') == '1'
         and e.get('GITHUB_REPOSITORY') == REPOSITORY and e.get('GITHUB_REF') == 'refs/heads/' + BRANCH
         and e.get('GITHUB_JOB') == 'selected-directory-modes'
         and e.get('GITHUB_WORKFLOW_SHA') == head
         and e.get('GITHUB_WORKFLOW_REF') == REPOSITORY + '/' + WORKFLOW + '@refs/heads/' + BRANCH
         and e.get('ImageOS') == 'ubuntu24' and e.get('ImageVersion') == IMAGE,
         'DIAGNOSTIC_ACTUAL_CONTEXT')
    workspace = Path(e['GITHUB_WORKSPACE']).resolve(strict=True)
    temp = Path(e['RUNNER_TEMP']).resolve(strict=True)
    need(packet == workspace / 'packet' and temp.is_dir(), 'DIAGNOSTIC_OWNED_PATHS')
    context = dict(run_id=int(run), run_attempt=1, head_sha=head, image_os='ubuntu24', image_version=IMAGE)
    return context, temp / ('dg16-g1-mode-observation-' + run + '-a1')


def read_nss_inputs(engine):
    objects = {}
    observed = dict(
        files={name:engine.B.capture_selector(name, objects, limit=65536)
               for name in ('/etc/passwd', '/etc/nsswitch.conf')},
        nscd={name:engine.B.capture_selector(name, objects) for name in engine.B._NSCD})
    engine.CHECK()
    return observed, objects


def read_only_nss(engine):
    observed, objects = read_nss_inputs(engine)
    engine.D._validate_nss(observed, objects)


def needs_exact_nss_transition(engine, nss):
    observed, objects = read_nss_inputs(engine)
    try:
        engine.D._validate_nss(observed, objects)
        return False
    except ValueError as error:
        if str(error) != 'C5 provider actual passwd NSS is not files-only':
            raise
    name = '/etc/nsswitch.conf'
    before = objects[observed['files'][name]['sha256']]
    need((len(before), sha(before)) == (526, 'b953df1d0016f515fc052ca6bb0ccd092b8d13c8789c51c4eaef2b0461574e57'),
         'DIAGNOSTIC_EXACT_NSS_PREIMAGE_REQUIRED')
    after = nss.transform(before)
    need((len(after), sha(after)) == (518, '5cde76a7763cef05fea9a086f5db0025459d489ee658a8369602e415e47beff7'),
         'DIAGNOSTIC_EXACT_NSS_POSTIMAGE_REQUIRED')
    # This is an eligibility check only. Actual admission uses a new read of
    # the original predicate after the existing journaled replacement.
    projected = dict(observed, files=dict(observed['files']))
    projected['files'][name] = dict(observed['files'][name], sha256=sha(after))
    engine.D._validate_nss(projected, dict(objects, **{sha(after):after}))
    return True


class Watchdog(TimeoutError):
    pass


@contextlib.contextmanager
def watchdog(seconds):
    need(0 < seconds <= 1800 and signal.getitimer(signal.ITIMER_REAL) == (0.0, 0.0),
         'DIAGNOSTIC_WATCHDOG_SCOPE')
    before = signal.getsignal(signal.SIGALRM)
    def expired(_signum, _frame):
        raise Watchdog()
    signal.signal(signal.SIGALRM, expired)
    signal.setitimer(signal.ITIMER_REAL, seconds)
    try:
        yield
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, before)


def remove_owned_directory(path, expected):
    """Only the exact fresh directory returned by its owner may be removed."""
    need(shutil.rmtree.avoids_symlink_attacks and path.resolve(strict=True) == path
         and path.parent.resolve(strict=True) == path.parent, 'DIAGNOSTIC_CLEANUP_PATH')
    fd = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC)
    try:
        need(anchor(os.fstat(fd)) == anchor(path.parent.lstat()), 'DIAGNOSTIC_CLEANUP_PARENT')
        before = os.stat(path.name, dir_fd=fd, follow_symlinks=False)
        need(stat.S_ISDIR(before.st_mode) and before.st_uid == before.st_gid == 0
             and anchor(before) == expected, 'DIAGNOSTIC_CLEANUP_IDENTITY')
        shutil.rmtree(path.name, dir_fd=fd)
        try:
            os.stat(path.name, dir_fd=fd, follow_symlinks=False)
        except FileNotFoundError:
            pass
        else:
            raise ValueError('DIAGNOSTIC_CLEANUP_RETAINED')
        os.fsync(fd)
        need(anchor(os.fstat(fd)) == anchor(path.parent.lstat()), 'DIAGNOSTIC_CLEANUP_PARENT_CHANGED')
    finally:
        os.close(fd)


def main():
    base = Path(__file__).resolve().parent
    packet = base.parents[1]
    context, work = actual_context(packet)
    os.umask(0o022)
    stage = 'BOOTSTRAP'
    status = 'REFUSED'
    failure_code = cleanup_code = None
    work_identity = provider_identity = None
    provider_attempted = False
    nss_attempted = False
    nss_journal = None
    nss_status = 'NOT_CHECKED'
    child_owner = False
    child_cleanup = 'NOT_STARTED'
    work_cleanup = provider_cleanup = 'NOT_CREATED'
    marker = None
    source_current = False
    setup_records = []
    try:
        R = module(base, 'run.py')
        need(R.SOURCE_COMMIT == PRODUCT and R.RUN_SECONDS == 1800 and R.FINAL_SECONDS == 60, 'DIAGNOSTIC_ORIGINAL_SOURCE_OWNER')
        U = R.load_module('host_utility')
        OP = R.load_module('operation')
        NSS = R.load_module('nss_configuration')
        observer = module(base, 'observe_selected_modes.py')
        public = module(base, 'mode_public_projection.py')
        allowlist = pinned(base, 'PUBLIC_PATH_ALLOWLIST.json')
        need(not os.path.lexists(work) and not os.path.lexists(PROVIDER), 'DIAGNOSTIC_FRESH_ROOTS_REQUIRED')
        overall = time.monotonic() + R.RUN_SECONDS
        stage = 'READ_ONLY_NSS'
        # The selected loader checks the unchanged tracked V7 files in the
        # pinned workflow checkout. No clone or provider write precedes NSS.
        with watchdog(min(120, overall - time.monotonic())):
            change_nss = needs_exact_nss_transition(OP.load_selected(packet), NSS)
        nss_status = 'EXACT_TRANSITION_REQUIRED' if change_nss else 'PASSED_READ_ONLY'
        stage = 'SOURCE_PREPARATION'
        work.mkdir(mode=0o700, exist_ok=False)
        work_identity = anchor(work.lstat())
        private = work / 'private'
        private.mkdir(mode=0o700)
        source = work / 'source'
        R.enable_subreaper()
        child_owner = True
        state = {}
        def command(label, argv, seconds=R.COMMAND_SECONDS):
            need(len(setup_records) < 180, 'DIAGNOSTIC_COMMAND_POPULATION')
            return U.capture(label, argv, setup_records, overall, seconds=seconds)
        with watchdog(overall - time.monotonic()):
            R.prepare_source(state, source, private, command)
        if change_nss:
            stage = 'NSS_CONDITIONAL'
            nss_attempted = True
            nss_status = 'UNRESOLVED'
            with watchdog(overall - time.monotonic()):
                NSS.prepare(private, str(context['run_id']), R.write_private)
                nss_journal = R.parse_json(R.read_regular(private/'NSS_CONFIGURATION.json', 8192))
                NSS.verify_configured(nss_journal)
                read_only_nss(OP.load_selected(source))
            nss_status = 'EXACT_TRANSITION_READ_BACK'
        stage = 'PROVIDER_PREPARATION'
        setup = R.load_module('input_setup')
        setup._COMMAND_DEADLINE = overall
        setup._UTILITY = U
        setup.root_ancestry(Path('/usr/bin/python3.12'))
        setup.root_ancestry(Path('/usr/bin/git'))
        spec_raw = pinned(base, 'PROVIDER_SETUP.json')
        need(sha(spec_raw) == R.PROVIDER_SETUP_SHA, 'DIAGNOSTIC_PROVIDER_SPEC_PIN')
        spec = R.parse_json(spec_raw)
        need(Path(spec['new_provider_root']) == PROVIDER, 'DIAGNOSTIC_PROVIDER_ROOT_PIN')
        with watchdog(overall - time.monotonic()):
            provider_records = []
            provider_attempted = True
            provider = setup.allocate_provider(spec, provider_records)
            need(provider == PROVIDER, 'DIAGNOSTIC_PROVIDER_OWNER')
            provider_identity = anchor(provider.lstat())
            R.load_module('provider_layout').convert_fresh_owned_provider05(provider)
        stage = 'FIRST_LAYOUT_OBSERVATION'
        observation_stop = min(overall, time.monotonic() + 120)
        with watchdog(observation_stop - time.monotonic()):
            engine = OP.load_selected(source)
            report = observer.observe_acquisition_to_layout(engine, source)
            marker = public.make_log_marker(report, allowlist, context)
            del report
            engine.CHECK()
            need(time.monotonic() < observation_stop, 'DIAGNOSTIC_OBSERVATION_DEADLINE')
        stage = 'SOURCE_CLOSING'
        with watchdog(overall - time.monotonic()):
            R.git_identity(source, command, True)
            need(R.identities(source) == state['source_directory_identity']
                 and R.identities(source / '.git') == state['git_directory_identity']
                 and R.verify_source(source, R.manifest(), False) == state['source_before']
                 and R.whole_source_census(source) == state['source_census_before'],
                 'DIAGNOSTIC_SOURCE_CLOSING')
        source_current = True
        status = 'OBSERVED'
    except Exception as error:
        failure_code = refusal_code(stage, error)
        status = 'REFUSED'
    finally:
        try:
            with watchdog(60):
                if child_owner:
                    try:
                        child_cleanup = 'ECHILD' if U.stop_owned_children()['echild'] else 'UNRESOLVED'
                    except Watchdog:
                        raise
                    except Exception as error:
                        cleanup_code = cleanup_code or refusal_code('CLEANUP', error)
                        child_cleanup = 'UNRESOLVED'
                if nss_attempted:
                    try:
                        need(nss_journal is not None, 'DIAGNOSTIC_NSS_EFFECT_UNRESOLVED')
                        NSS.verify_configured(nss_journal)
                        nss_status = 'EXACT_TRANSITION_CLOSING_VERIFIED_VM_SCOPE'
                    except Watchdog:
                        raise
                    except Exception as error:
                        cleanup_code = cleanup_code or refusal_code('CLEANUP', error)
                        nss_status = 'UNRESOLVED'
                if provider_attempted and provider_identity is None:
                    provider_cleanup = 'UNRESOLVED' if os.path.lexists(PROVIDER) else 'ABSENT'
                for path, identity, kind in ((PROVIDER, provider_identity, 'provider'), (work, work_identity, 'work')):
                    if identity is None:
                        continue
                    disposition = 'UNRESOLVED'
                    if child_cleanup == 'ECHILD' and not (kind == 'work' and nss_status == 'UNRESOLVED'):
                        try:
                            remove_owned_directory(path, identity)
                            disposition = 'OWNED_REMOVED_READ_BACK'
                        except Watchdog:
                            raise
                        except Exception as error:
                            cleanup_code = cleanup_code or refusal_code('CLEANUP', error)
                    if kind == 'provider':
                        provider_cleanup = disposition
                    else:
                        work_cleanup = disposition
        except Watchdog as error:
            cleanup_code = cleanup_code or refusal_code('CLEANUP', error)
            if nss_attempted and nss_status != 'EXACT_TRANSITION_CLOSING_VERIFIED_VM_SCOPE':
                nss_status = 'UNRESOLVED'
            if child_owner and child_cleanup != 'ECHILD':
                child_cleanup = 'UNRESOLVED'
            if provider_attempted and provider_cleanup == 'NOT_CREATED':
                provider_cleanup = 'UNRESOLVED'
            if work_identity is not None and work_cleanup == 'NOT_CREATED':
                work_cleanup = 'UNRESOLVED'
    if 'UNRESOLVED' in (child_cleanup, provider_cleanup, work_cleanup, nss_status):
        status = 'CLEANUP_UNRESOLVED'
        if failure_code is None:
            stage = 'CLEANUP'
            failure_code = cleanup_code or 'UNCLASSIFIED'
    if not source_current:
        marker = None
    terminal = dict(schema='dg16.g1-mode-observation-terminal.v2', authority='NONE',
        context=context, status=status, last_stage=stage, refusal_code=failure_code, source_bookends=source_current,
        child_cleanup=child_cleanup, provider_cleanup=provider_cleanup, work_cleanup=work_cleanup,
        nss_disposition=nss_status,
        mode_marker_sha256=sha(marker) if marker is not None else None)
    line = TERMINAL_MARKER + encode(terminal) + b'\n'
    need(len(line) <= 2048, 'DIAGNOSTIC_TERMINAL_BOUND')
    if marker is not None:
        sys.stdout.buffer.write(marker)
    sys.stdout.buffer.write(line)
    sys.stdout.buffer.flush()
    return 0 if status == 'OBSERVED' else 2


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except Exception:
        # A malformed bootstrap cannot establish job/selector provenance.
        print('DG16_MODE_OBSERVATION_BOOTSTRAP_REFUSED', flush=True)
        raise SystemExit(2)
