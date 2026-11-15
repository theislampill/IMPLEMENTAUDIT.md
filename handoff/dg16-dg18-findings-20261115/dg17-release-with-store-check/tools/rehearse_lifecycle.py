"""Linux deterministic producer/consumer rehearsal; ALL native traffic is SIMULATED.

This harness never starts Codex, reads authentication, grants native authority, or
accepts DG17. Real source commands, controller lifecycle, binding store, formatter,
receipt consumption and teardown run only inside the fresh owned work directory.
"""
import argparse
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path, PureWindowsPath
import queue
import shutil
import subprocess
import sys
import time
import types
from unittest.mock import patch

HERE = Path(__file__).absolute().parent
SESSION = '00000000-0000-4000-8000-000000000017'
OLD_OWNER = '05a0767e4a4a72eb7ff13f11bf9341a270b46954bab0e8e57e3e6c7bfa411aff'
OLD_PYTHON = '5f7b89a612c9b8af1d6456cdfcd1dbe5ca630849e79aebced9bee9a6694952ec'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def pin(path):
    path = Path(path).resolve()
    raw = path.read_bytes()
    return dict(path=str(path), bytes=len(raw), sha256=sha(raw))


def save(path, value):
    Path(path).write_text(json.dumps(value, indent=2, sort_keys=True) + '\n', encoding='utf-8')


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class NativeBoundary(RuntimeError):
    pass


class Fixture:
    def __init__(self, author, work, mode):
        self.work = Path(work).absolute()
        self.work.mkdir(parents=True, exist_ok=False)
        save(self.work / 'SIMULATED_ONLY.json', {
            'authority': 'NONE', 'native_acceptance': False, 'genuine_model_turns': 0,
            'notice': 'Every native-shaped receipt below is a test fixture, never authentic evidence.'})
        self.mode = mode
        self.original_author = Path(author).resolve()
        self.author = self.work / 'fixture-author'
        shutil.copytree(self.original_author, self.author)
        self.op = json.loads((self.author / 'OPERATION_A.json').read_bytes())
        self.case = self.work / 'SIMULATED-case'
        self.home = self.work / 'isolated-home-01'
        self.home.mkdir()
        shutil.copyfile(self.author / 'PROFILE.toml', self.home / 'config.toml')
        self.owner = self.work / 'SIMULATED-owner-input.json'
        save(self.owner, {'authority': 'NONE', 'purpose': 'SIMULATED test input, not owner permission'})
        self.python = str(Path(sys.executable).resolve())
        self.bash = str(Path(shutil.which('bash')).resolve())
        self.fixed_path = os.environ['PATH']
        self.calls = []
        self.clients = []
        self.config = {'web_search': 'disabled', 'plugins': {'implementaudit@implementaudit': {'enabled': True}}}
        self.version = 1
        self.turns = []
        self.journal = self.work / 'SIMULATED-native-journal.jsonl'
        self.journal.write_text(json.dumps({'type': 'session_meta', 'payload': {'id': SESSION},
                                           'SIMULATED': True}) + '\n')
        # Fixture substitutions retain the exact guard predicates while supplying
        # POSIX tool/owner carriers. No resulting constructor is a native candidate.
        ctor = (self.author / 'positive_hook_constructor.py').read_text()
        ctor = ctor.replace(OLD_OWNER, pin(self.owner)['sha256']).replace(OLD_PYTHON, pin(self.python)['sha256'])
        old = " if python!=Path(r'C:\\Users\\theis\\AppData\\Local\\Programs\\Python\\Python311\\python.exe'):"
        assert ctor.count(old) == 1
        ctor = ctor.replace(old, " if python!=Path(" + repr(self.python) + "):")
        lines = ctor.splitlines(keepends=True)
        matches = [i for i, line in enumerate(lines) if line.startswith(' fixed_path=str(python.parent)+')]
        assert len(matches) == 1
        lines[matches[0]] = ' fixed_path=' + repr(self.fixed_path) + '\n'
        (self.author / 'positive_hook_constructor.py').write_text(''.join(lines))
        self.op.update(case=str(self.case), expected_codex_home=str(self.home),
                       python=pin(self.python), bash=self.bash, bash_sha256=pin(self.bash)['sha256'],
                       git=str(Path(shutil.which('git')).resolve()), fixed_path=self.fixed_path,
                       issuer='SIMULATED-NO-AUTHORITY', owner_approval=pin(self.owner),
                       appserver_argv=['SIMULATED-NEVER-EXECUTED'],
                       status='SIMULATED_TEST_INPUT_NOT_NATIVE_OPERATION')
        for key, name in [('rpc_module', 'native_rpc.py'), ('constructor', 'positive_hook_constructor.py')]:
            self.op[key] = pin(self.author / name)
        self.op['readset'] = [pin(self.author / name) for name in [
            'native_rpc.py', 'stage_a.py', 'stage_b.py', 'PROFILE.toml', 'positive_hook_constructor.py']]
        self.op['readset'] += [pin(self.owner), pin(self.home / 'config.toml'),
                              pin(self.python), pin(self.bash), self.op['binding_owner']]
        save(self.author / 'OPERATION_A.json', self.op)
        self.rpc = load(self.author / 'native_rpc.py', 'simulated_rpc')
        fixture = self

        class Client(fixture.rpc.Client):
            def __init__(self, argv, cwd, env, out, deadline):
                assert argv == ['SIMULATED-NEVER-EXECUTED']
                fixture.calls.append('SIMULATED:Client')
                if fixture.mode == 'native-boundary':
                    raise NativeBoundary('SIMULATED stop before native appserver creation')
                self.cwd, self.deadline = Path(cwd), deadline
                self.seq, self.sent, self.events = 0, {}, []
                self.thread_id = self.turn_id = None
                self.active = False
                self.q = queue.Queue()
                self.proc = types.SimpleNamespace(stdin=types.SimpleNamespace(
                    write=lambda raw: fixture.calls.append('SIMULATED:interrupt-wire'),
                    flush=lambda: None))
                self.out = Path(out)
                self.out.mkdir()
                fixture.clients.append(self)

            def record(self, value):
                fixture.calls.append('SIMULATED:record:' + str(value.get('kind', value.get('direction'))))

            def init(self):
                return {'codexHome': str(fixture.home), 'SIMULATED': True}

            def recv(self, seconds=30):
                return self.q.get_nowait()

            def rpc(self, method, params, seconds=30):
                fixture.calls.append('SIMULATED:' + method)
                if method == 'account/read':
                    return {'account': {'type': 'SIMULATED-NOT-AUTHENTICATED'}}
                if method == 'plugin/install':
                    return {'appsNeedingAuth': []}
                if method == 'plugin/read':
                    return {'plugin': {'marketplaceName': 'implementaudit', 'apps': [], 'mcpServers': [],
                                       'hooks': [], 'summary': {'id': 'SIMULATED-PLUGIN'}}}
                if method == 'skills/list':
                    rows = []
                    for name, expected in fixture.op['native_skill_pins'].items():
                        source = Path(fixture.op['source_worktree']) / 'skills' / name / 'SKILL.md'
                        dest = fixture.home / 'SIMULATED-plugin' / name / 'SKILL.md'
                        dest.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copyfile(source, dest)
                        assert sha(dest.read_bytes()) == expected
                        rows.append(dict(name=name, path=str(dest), enabled=True, pluginId='SIMULATED-PLUGIN'))
                    return {'data': [{'skills': rows, 'errors': []}]}
                if method == 'config/read':
                    return {'config': copy.deepcopy(fixture.config), 'layers': [{
                        'name': {'type': 'user', 'file': str(fixture.home / 'config.toml')},
                        'version': str(fixture.version), 'config': copy.deepcopy(fixture.config)}]}
                if method == 'experimentalFeature/list':
                    return {'data': [{'name': key, 'enabled': value} for key, value in {
                        'apps': False, 'multi_agent': False, 'multi_agent_v2': False,
                        'memories': False, 'hooks': True, 'plugins': True}.items()]}
                if method == 'mcpServerStatus/list':
                    return {'data': []}
                if method == 'hooks/list':
                    return {'data': [{
                        'cwd': str(self.cwd), 'errors': [], 'warnings': [],
                        'hooks': [fixture.hook(self.cwd)] if (self.cwd / '.codex/hooks.json').exists() else []}]}
                if method in ['thread/start', 'thread/resume', 'thread/read']:
                    return fixture.thread(self.cwd)
                if method == 'config/value/write':
                    assert params['expectedVersion'] == str(fixture.version)
                    # All allowed paths have one quoted repo component or simple identifiers.
                    decoder = json.JSONDecoder()
                    remaining = params['keyPath']; keys = []
                    while remaining:
                        if remaining.startswith('"'):
                            key, end = decoder.raw_decode(remaining)
                            remaining = remaining[end:]
                        else:
                            key, _, remaining = remaining.partition('.')
                            keys.append(key)
                            continue
                        keys.append(key)
                        if remaining:
                            assert remaining[0] == '.'
                            remaining = remaining[1:]
                    target = fixture.config
                    for key in keys[:-1]:
                        target = target.setdefault(key, {})
                    target[keys[-1]] = params['value']
                    fixture.version += 1
                    return {'status': 'ok', 'version': str(fixture.version)}
                if method == 'turn/start':
                    turn_id = 'SIMULATED-B-TURN'
                    fixture.context(turn_id, self.cwd)
                    self.turn_id, self.active = turn_id, True
                    hook = fixture.hook(self.cwd)
                    run = dict(hook, id='SIMULATED-OPAQUE-RUN', executionMode='sync', scope='turn', status='running')
                    started = dict(method='hook/started', params=dict(threadId=SESSION, turnId=turn_id, run=run))
                    completed = copy.deepcopy(started)
                    completed['method'] = 'hook/completed'
                    completed['params']['run']['status'] = 'completed' if fixture.mode != 'blocked-hook' else 'blocked'
                    fixture.synthetic_receipt(turn_id)
                    for item in [
                        dict(method='turn/started', params={'threadId': SESSION, 'turn': {'id': turn_id}}),
                        started, completed,
                        dict(method='turn/completed', params={'threadId': SESSION,
                             'turn': {'id': turn_id, 'status': 'completed'}})]:
                        self.q.put(item)
                    return {'turn': {'id': turn_id}, 'SIMULATED': True}
                if method == 'turn/interrupt':
                    self.active = False
                    return {'SIMULATED': True}
                raise AssertionError('Unexpected simulated RPC: ' + method)

            def turn(self, thread_id, prompt, seconds=180):
                turn_id = 'SIMULATED-A-TURN'
                fixture.context(turn_id, self.cwd)
                self.thread_id, self.turn_id, self.active = SESSION, turn_id, False
                outputs = '\n'.join(sha((self.cwd / name).read_bytes()) for name in fixture.op['observation_members'])
                fixture.turns = [{'id': turn_id, 'items': [
                    {'type': 'commandExecution', 'status': 'completed', 'exitCode': 0, 'aggregatedOutput': outputs},
                    {'type': 'commandExecution', 'status': 'completed', 'exitCode': 0,
                     'aggregatedOutput': 'SIMULATED model observation, no native credit'}]}]
                return {'turn': {'id': turn_id}}, {'turn': {'id': turn_id, 'status': 'completed'}}

            def close(self, cleanup_deadline=None):
                self.active = False
                return {'actor_idle': True, 'readers_done': True, 'server_wait_returned': True,
                        'SIMULATED': True}
        self.rpc.Client = Client

    def thread(self, cwd):
        return {'thread': {'id': SESSION, 'path': str(self.journal), 'status': {'type': 'idle'},
                           'turns': copy.deepcopy(self.turns)},
                'cwd': str(cwd), 'model': 'gpt-6.1-sol', 'approvalPolicy': 'never',
                'sandbox': {'type': 'readOnly', 'networkAccess': False}, 'SIMULATED': True}

    def context(self, turn, cwd):
        with self.journal.open('a') as stream:
            stream.write(json.dumps({'type': 'turn_context', 'SIMULATED': True,
                'payload': {'turn_id': turn, 'cwd': str(cwd), 'model': 'gpt-6.1-sol', 'effort': 'high',
                            'approval_policy': 'never', 'sandbox_policy': {'type': 'read-only'}}}) + '\n')

    def hook(self, repo):
        path = repo / '.codex/hooks.json'
        proposal = json.loads(path.read_bytes())['hooks']['Stop'][0]['hooks'][0]
        state = self.config.get('hooks', {}).get('state', {}).get('SIMULATED-HOOK', {})
        digest = sha(path.read_bytes())
        trusted = (self.config.get('projects', {}).get(str(repo), {}).get('trust_level') == 'trusted'
                   and state.get('trusted_hash') == digest)
        return {'key': 'SIMULATED-HOOK', 'source': 'project', 'sourcePath': str(path),
                'eventName': 'stop', 'handlerType': 'command', 'timeoutSec': 60, 'isManaged': False,
                'currentHash': digest, 'enabled': state.get('enabled', False),
                'trustStatus': 'trusted' if trusted else 'untrusted', 'command': proposal['commandWindows'],
                'displayOrder': 0, 'statusMessage': proposal['statusMessage']}

    def synthetic_receipt(self, turn):
        manifest = json.loads((self.case / 'evidence/CONSTRUCTOR_MANIFEST.json').read_bytes())
        inputs = json.loads((self.case / 'evidence/CONSTRUCTOR_ACTUAL_INPUTS.json').read_bytes())
        # Execute real deterministic producer owners before formatting the
        # explicitly synthetic native transport envelope consumed by Stage B.
        env = os.environ | {'PYTHONDONTWRITEBYTECODE': '1'}
        result = subprocess.run([self.bash, inputs['validator'], '--nonterminal-yield',
                                 inputs['explicit_run_root']], cwd=inputs['repository_identity'],
                                env=env, capture_output=True, timeout=30)
        assert result.returncode == 0, result.stderr.decode()
        binding = json.loads(subprocess.check_output([
            self.python, '-I', '-S', '-B', inputs['binding_owner'], '--store', inputs['binding_store'],
            'lookup', '--host-id', 'codex', '--host-session-id', SESSION], env=env))
        assert binding['binding'] == manifest['expected_initial_B_full_binding']
        save(Path(inputs['evidence_directory']) / 'SIMULATED-native-receipt.json', {
            'SIMULATED': True, 'native_acceptance': False,
            'event': {'turn_id': turn, 'session_id': SESSION},
            'policy_sha256': manifest['policy_sha256'], 'validator_exit': result.returncode,
            'selected_disposition': 'NONTERMINAL_YIELD', 'binding': binding['binding'],
            'record_disposition': {'record_disposition': 'NONTERMINAL_YIELD'}})

    def run(self):
        stage_a = load(self.author / 'stage_a.py', 'stage_a_rehearsal')
        original_load = stage_a.pinned_module
        stage_a.pinned_module = lambda item, name: self.rpc if name == 'bounded_native_rpc' else original_load(item, name)
        grant_a = self.work / 'SIMULATED-input-A.json'
        save(grant_a, dict(issuer=self.op['issuer'], stage='A',
                          operation_sha256=sha((self.author / 'OPERATION_A.json').read_bytes()),
                          owner_approval_sha256=self.op['owner_approval']['sha256'],
                          resource_ack_received=True, authority='NONE', SIMULATED=True))
        start = time.perf_counter_ns()
        a_error = None
        try:
            stage_a.main(types.SimpleNamespace(grant=grant_a, window_start_ns=start))
        except NativeBoundary as error:
            a_error = str(error)
            assert self.mode == 'native-boundary'
        post_a = json.loads((self.case / 'evidence/POST_A.json').read_bytes())
        source_steps = [p.name for p in sorted((self.case / 'evidence').glob('[0-9]*.json'))]
        summary = {'schema': 'dg17.SIMULATED-deterministic-rehearsal.v1', 'authority': 'NONE',
                   'mode': self.mode, 'genuine_codex_turns': 0, 'native_appservers_started': 0,
                   'windows_custody_exercised': False, 'original14_unknown_differences': 14,
                   'stage_A_source_steps': source_steps, 'stage_A_status': post_a['status'],
                   'stage_A_error': a_error}
        if self.mode == 'native-boundary':
            assert source_steps[-1] == '10-source-positive.json'
            assert post_a['model_turns'] == post_a['thread_start_calls'] == 0
            summary['result'] = 'SOURCE_STEPS_01_TO_10_PASS_NATIVE_BOUNDARY_NOT_CROSSED'
        else:
            assert post_a['status'] == 'STAGE_A_BOUND_CONTEXT_READY_FOR_INDEPENDENT_REVIEW'
            reviewer = self.work / 'SIMULATED-independent-input.json'
            save(reviewer, {'SIMULATED': True, 'authority': 'NONE',
                            'scope': 'formatter input only; not independent native receiving'})
            binder = load(self.author / 'bind_stage_b.py', 'bind_stage_b_rehearsal')
            binder.A_SHA = sha((self.author / 'OPERATION_A.json').read_bytes())
            binder.ROOT = self.work
            with patch.object(sys, 'argv', ['bind_stage_b.py', '--independent-post-a', str(reviewer),
                                           '--independent-sha256', pin(reviewer)['sha256'],
                                           '--new-store-owner', 'SIMULATED-DG17-OWNER']):
                binder.main()
            operation_b = self.work / 'OPERATION_B_BOUND.json'
            b = json.loads(operation_b.read_bytes())
            grant_b = self.work / 'SIMULATED-input-B.json'
            save(grant_b, dict(issuer=b['issuer'], stage='B',
                              operation_sha256=sha(operation_b.read_bytes()),
                              post_A_sha256=b['post_A']['sha256'],
                              owner_approval_sha256=b['owner_approval']['sha256'],
                              independent_post_A=b['independent_post_A'],
                              authority='NONE', SIMULATED=True))
            stage_b = load(self.author / 'stage_b.py', 'stage_b_rehearsal')
            original_code = stage_b.load_code
            stage_b.load_code = lambda item, name: self.rpc if name == 'qualified_episode_rpc' else original_code(item, name)
            real_path = Path
            stage_b.Path = lambda value: (operation_b if PureWindowsPath(str(value)).name == 'OPERATION_B_BOUND.json'
                                         else real_path(value))
            def posix_test_store(path, create=False):
                assert create and not path.exists()
                path.mkdir(mode=0o700)
                assert path.stat().st_mode & 0o777 == 0o700
                return {'SIMULATED_WINDOWS_SEAM': True, 'posix_mode': '0700'}
            stage_b.private_store_directory = posix_test_store
            b_error = None
            try:
                stage_b.main(types.SimpleNamespace(grant=grant_b))
            except Exception as error:
                b_error = repr(error)
                if self.mode != 'blocked-hook':
                    raise
            post_b = json.loads((self.case / 'evidence/stage-B01/POST_B.json').read_bytes())
            assert post_b['cleanup']['known'] is True
            assert post_b['cleanup']['new_binding_tombstoned_object_open'] is True
            assert post_b['cleanup']['new_hook_disabled'] is True
            if self.mode == 'blocked-hook':
                assert post_b['status'] == 'FIRST_EVENT_OR_LATE_EXTRA_ACTIVITY_NOT_QUALIFYING'
                assert post_b['fence']['interrupt_request_id'] is not None
                assert b_error is not None
                summary['result'] = 'FIRST_NONPASS_CONTAINED_AND_CLEANED_UP'
            else:
                assert post_b['status'] == 'ONE_ACTUAL_SELECTED_NATIVE_ALLOW_AND_NATURAL_NONTERMINAL_COMPLETION_AWAIT_INDEPENDENT_RECEIVING'
                summary['result'] = 'DETERMINISTIC_LIFECYCLE_PASS_WITH_SIMULATED_NATIVE_SEAMS'
            summary.update(stage_B_status=post_b['status'], stage_B_error=b_error,
                           stage_B_steps=[p.name for p in sorted((self.case / 'evidence/stage-B01').glob('[0-9]*.json'))],
                           teardown_known_in_simulation=True,
                           actual_native_acceptance=False)
        summary['simulated_calls'] = self.calls
        summary['elapsed_seconds'] = (time.perf_counter_ns() - start) / 1e9
        summary['seams'] = ['native RPC and model traffic simulated', 'fresh simulated grant/reviewer inputs',
                            'constructor fixed host literals rebound only in test copies',
                            'Stage B operation path routed to test copy', 'Windows ACL replaced by POSIX private test directory']
        save(self.work / 'REHEARSAL_RESULT.json', summary)
        return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--author', type=Path, required=True)
    parser.add_argument('--work', type=Path, required=True)
    parser.add_argument('--mode', choices=['native-boundary', 'full', 'blocked-hook'], default='full')
    args = parser.parse_args()
    os.environ['IMPLEMENTAUDIT_PYTHON'] = str(Path(sys.executable).resolve())
    fixture = Fixture(args.author, args.work, args.mode)
    original_popen = subprocess.Popen
    allowed = {str(Path(p).resolve()) for p in [fixture.python, fixture.bash, fixture.op['git']]}
    def deterministic_process(argv, *pargs, **kwargs):
        if not isinstance(argv, (list, tuple)) or kwargs.get('shell'):
            raise AssertionError('Rehearsal refuses shell/string process launch')
        executable = shutil.which(str(argv[0])) if not Path(argv[0]).is_absolute() else str(argv[0])
        if not executable or str(Path(executable).resolve()) not in allowed:
            raise AssertionError('Rehearsal refuses any process except its exact Python, Bash and Git')
        if any(str(arg) == 'app-server' or Path(str(arg)).name.lower().startswith('codex')
               for arg in argv[1:]):
            raise AssertionError('No Codex or appserver invocation is permitted in this rehearsal')
        return original_popen(argv, *pargs, **kwargs)
    with patch.object(subprocess, 'Popen', deterministic_process):
        result = fixture.run()
    print(json.dumps({k: v for k, v in result.items() if k != 'simulated_calls'}, indent=2))


if __name__ == '__main__':
    main()
