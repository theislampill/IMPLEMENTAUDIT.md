"""One separately authorized startup on the prospective OR owned connection."""

import ast
import contextlib
import hashlib
import os
from pathlib import Path
import re
import subprocess
import threading
import time


OR_STAGE_A_GRANT_PIN = None
CLI_BYTES = 295408944
CLI_SHA256 = '444a3f0008050605cae73cd9b7a2dcac61294062dfaab56dd20430fd6498518b'
MAX_STAGE_A_SECONDS = 600


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def _descriptor(raw):
    return {'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}


def _runner_template(raw):
    slots = [node.value for node in ast.parse(raw).body if isinstance(node, ast.Assign)
             and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name)
             and node.targets[0].id == 'OR_STAGE_A_GRANT_PIN']
    require(len(slots) == 1 and ast.literal_eval(slots[0]) == OR_STAGE_A_GRANT_PIN,
            'OR_STAGE_A_RUNNER_SELECTION_CHANGED')
    slot = slots[0]
    lines = raw.splitlines(keepends=True)
    start = sum(map(len, lines[:slot.lineno - 1])) + slot.col_offset
    end = sum(map(len, lines[:slot.end_lineno - 1])) + slot.end_col_offset
    return _descriptor(raw[:start] + b'None' + raw[end:])


def _held_pin(owner, stack, pin, maximum, *, image=False):
    require(type(pin) is dict and set(pin) == {'path', 'bytes', 'sha256'}, 'OR_STAGE_A_PIN_SHAPE')
    path = Path(pin['path'])
    require(path.is_absolute() and path.resolve(strict=True) == path, 'OR_STAGE_A_PIN_ALIAS')
    held = stack.enter_context(owner.PinnedFile(path, max_bytes=maximum))
    raw = None if image else held.read()
    actual = ({'bytes': path.stat().st_size, 'sha256': owner.native_held_image_sha256_v1(held)}
              if image else _descriptor(raw))
    require(pin == dict(actual, path=str(path)), 'OR_STAGE_A_PIN_CHANGED')
    return held, raw


def _validate_scope(owner, context, grant):
    fields = {'schema', 'operation', 'effect', 'owner_decision_locator', 'operator',
              'runner_process', 'runner_template', 'subject', 'candidate', 'tree',
              'expected_old', 'receipt_token', 'binary', 'profile', 'profile_config',
              'producer_pins', 'initialize', 'thread_start', 'expires_at_ms', 'maximum_seconds'}
    require(type(grant) is dict and set(grant) == fields
            and grant['schema'] == 'implementaudit.or-owned-stdio-stage-a.v1'
            and grant['effect'] == 'ONE_OR_STARTUP_WITHOUT_MODEL_OR_ROTATION'
            and type(grant['operation']) is str and re.fullmatch('[A-Za-z0-9-]{1,80}', grant['operation'])
            and all(type(grant[key]) is str and grant[key] for key in ('owner_decision_locator', 'operator'))
            and type(grant['expires_at_ms']) is int and type(grant['maximum_seconds']) is int
            and 0 < grant['maximum_seconds'] <= MAX_STAGE_A_SECONDS,
            'OR_STAGE_A_GRANT_SCOPE')
    subject = {key: context[key] for key in ('controller', 'claim_id', 'run_root_identity')}
    require(grant['subject'] == dict(subject, repository=str(context['repo']))
            and owner.native_process_identity_v1(os.getpid()) == grant['runner_process'],
            'OR_STAGE_A_SUBJECT_OR_OPERATOR_PROCESS_CHANGED')
    for key, revision in (('candidate', 'HEAD'), ('tree', 'HEAD^{tree}')):
        require(owner.git(context['repo'], 'rev-parse', revision).decode().strip() == grant[key],
                'OR_STAGE_A_CANDIDATE_CHANGED')
    joined = owner.require_current_generation_join_v1(context)
    require(joined['receipt_token'] == grant['receipt_token']
            and owner.managed(context) == grant['expected_old']
            and joined['pointer_oid'] == grant['expected_old']['pointer']
            and joined['marker_oid'] == grant['expected_old']['marker'], 'OR_STAGE_A_PREIMAGE_CHANGED')
    thread = grant['thread_start']
    require(type(grant['initialize']) is dict and type(thread) is dict
            and set(thread) == {'cwd', 'model', 'modelProvider', 'sandbox', 'approvalPolicy', 'experimentalRawEvents'}
            and thread['cwd'] == str(context['repo']) and thread['sandbox'] == 'read-only'
            and thread['approvalPolicy'] == 'never' and thread['experimentalRawEvents'] is True
            and all(type(thread[key]) is str and thread[key] for key in ('model', 'modelProvider')),
            'OR_STAGE_A_RPC_SCOPE')


@contextlib.contextmanager
def open_owned_or_stage_a_v1(owner, source, context, *, emit):
    """Yield an unadmitted producer and its actual startup facts while both pipes stay held."""
    require(OR_STAGE_A_GRANT_PIN is not None, 'OR_STAGE_A_GRANT_UNSELECTED')
    require(os.name == 'nt', 'OR_STAGE_A_REQUIRES_WINDOWS')
    with contextlib.ExitStack() as stack:
        grant_handle, raw = _held_pin(owner, stack, OR_STAGE_A_GRANT_PIN, 64 * 1024)
        grant = owner.decode_json(raw)
        _validate_scope(owner, context, grant)
        remaining = (grant['expires_at_ms'] - time.time_ns() // 1_000_000) / 1000
        require(remaining > 0, 'OR_STAGE_A_EXPIRED')
        end = time.monotonic() + min(remaining, grant['maximum_seconds'])
        binary = grant['binary']
        require(binary.get('bytes') == CLI_BYTES and binary.get('sha256') == CLI_SHA256,
                'OR_STAGE_A_CLI_IDENTITY')
        image_handle, _ = _held_pin(owner, stack, binary, 512 * 1024 * 1024, image=True)
        profile = Path(grant['profile'])
        require(profile.is_absolute() and profile.resolve(strict=True) == profile and profile.is_dir()
                and profile.parent == context['repo'].parent and profile.name == 'profile',
                'OR_STAGE_A_PROFILE_ALIAS')
        owner.safe_chain(profile)
        require(Path(grant['profile_config']['path']) == profile / 'config.toml', 'OR_STAGE_A_CONFIG_LOCATION')
        config_handle, _ = _held_pin(owner, stack, grant['profile_config'], 128 * 1024)
        runner = Path(__file__).absolute()
        runner_handle = stack.enter_context(owner.PinnedFile(runner, max_bytes=128 * 1024))
        runner_bytes = runner_handle.read()
        require(_runner_template(runner_bytes) == grant['runner_template'], 'OR_STAGE_A_RUNNER_CHANGED')
        peers = grant['producer_pins']
        source_path = Path(source.__file__).absolute()
        paths = {'source_owner': source_path, 'helper': source_path.with_name('bounded_source_owner.py'),
                 'loop': source_path.with_name('owned_stdio_loop.py'), 'claim': Path(owner.__file__).absolute()}
        require(type(peers) is dict and set(peers) == set(paths), 'OR_STAGE_A_DEPENDENCY_POPULATION')
        handles = [grant_handle, image_handle, config_handle, runner_handle]
        for name, path in paths.items():
            require(Path(peers[name]['path']) == path, 'OR_STAGE_A_DEPENDENCY_LOCATION')
            held, _ = _held_pin(owner, stack, peers[name], 512 * 1024)
            handles.append(held)
        pins = dict(peers, runner=dict(_descriptor(runner_bytes), path=str(runner)))
        environment = {key: value for key, value in os.environ.items()
                       if key.casefold() in {'systemroot', 'windir', 'systemdrive', 'comspec', 'temp', 'tmp'}}
        environment['CODEX_HOME'] = str(profile)

        def check():
            for held in handles:
                held.verify()
            require(owner.managed(context) == grant['expected_old'], 'OR_STAGE_A_PREIMAGE_ADVANCED')
            require(time.monotonic() < end, 'OR_STAGE_A_DEADLINE')
            return min(end, time.monotonic() + 30)

        check()
        attempt = profile / ('.or-stage-a-start-' + grant['operation'])
        with attempt.open('xb') as receipt:
            receipt.write((grant['operation'] + '\n').encode('ascii'))
            receipt.flush()
            os.fsync(receipt.fileno())
        check()
        process = subprocess.Popen([binary['path'], 'app-server', '--listen', 'stdio://'],
                                   cwd=context['repo'], env=environment, stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                                   creationflags=subprocess.CREATE_NO_WINDOW)
        producer = None

        def expire():
            try:
                if producer is not None:
                    producer.cancel_now()
            finally:
                if process.poll() is None:
                    process.kill()

        watchdog = threading.Timer(max(0, end - time.monotonic()), expire)
        watchdog.daemon = True
        try:
            watchdog.start()
            producer = source.own_live_stdio_process_v1(process, pins, emit=emit)
            require(producer.process_identity['image'] == binary['path'], 'OR_STAGE_A_LIVE_IMAGE_CHANGED')
            loop = producer.loop
            loop.call('initialize', grant['initialize'], check())
            loop.notify('initialized', {}, check())
            start = loop.call('thread/start', grant['thread_start'], check())
            loop.call('thread/read', {'threadId': start['thread']['id'], 'includeTurns': False}, check())
            facts = loop.live_acquisition_facts_v1()
            path = Path(facts['source_path'])
            require(path.is_absolute() and path.resolve(strict=True) == path
                    and path.is_relative_to(profile / 'sessions')
                    and path.name.endswith('-' + facts['thread_id'] + '.jsonl'), 'OR_STAGE_A_SOURCE_NAMESPACE')
            owner.safe_chain(path)
            check()
            producer.check()
            yield producer, facts
        finally:
            try:
                if producer is not None:
                    try:
                        producer.loop.close(time.monotonic() + 5)
                    finally:
                        producer.finish()
                else:
                    if process.poll() is None:
                        process.kill()
                    process.wait(timeout=5)
                    process.stdin.close()
                    process.stdout.close()
            finally:
                watchdog.cancel()
