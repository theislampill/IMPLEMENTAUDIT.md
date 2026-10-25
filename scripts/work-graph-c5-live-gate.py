#!/usr/bin/env python3
"""Live original48 event gate; the enclosing fixed executor owns its child.

Only a captured-source owner may construct this component. Durable captures are
validated as data. Acceptance additionally requires the actual unreaped direct
child, its private inherited channel, live frontiers, and retained effect bytes.
This component neither launches a native issuer nor imports a prior completion.
"""
import hashlib
import json
import os
from pathlib import Path
import signal
import socket
import stat
import subprocess
import threading
import time

_CAPTURE = globals().pop('_R0035_C5_LIVE_GATE_CAPTURE', None)
if not isinstance(_CAPTURE, dict) or set(_CAPTURE) != {'capture', 'completion', 'compiler_sha256', 'check'}:
    raise RuntimeError('C5 live gate requires its separate captured-source owner')
E, C, COMPILER_SHA, _CHECK = (_CAPTURE[key] for key in ('capture', 'completion', 'compiler_sha256', 'check'))
PROFILE = 'LIVE_FIXED_ORIGINAL48_PRODUCER_EFFECT_GATE_V1'
ROOT_NODE, BUILD_A, BUILD_B = 'C5_ROOT', 'C5_00_BUILD_A', 'C5_01_BUILD_B'
OUTPUT, CONSUMERS, FINAL = 'C5_02_OUTPUT_JOIN', 'C5_03_CONSUMERS', 'C5_04_FINAL_JOIN'
BUILD_NODES = {'build:a': BUILD_A, 'build:b': BUILD_B}


class LiveGateError(ValueError):
    pass


def demand(value, message):
    if not value:
        raise LiveGateError(message)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def encode(value):
    return E.canonical(value)


def directory_identity(info):
    return [str(info.st_dev), str(info.st_ino), info.st_mode, info.st_uid, info.st_gid]


def file_identity(info):
    return [str(info.st_dev), str(info.st_ino), info.st_mode, info.st_nlink,
            info.st_size, info.st_mtime_ns, info.st_ctime_ns]


def node(name, **changes):
    value = dict(id=name, parent=ROOT_NODE, kind='TASK', state='OPEN', requires=[],
                 optional=[], reads=['path:source.json'], writes=[], acceptance=[], resources=[],
                 authority=[], effect='READ_ONLY', authorization='PERMITTED', independence='KNOWN',
                 resource_demand=1, rank=0, route_scopes=[], logical_delivery=None, future_consumer=None,
                 invalidators=[], independent_results=False, done_evidence=None,
                 context=dict(locality='GOVERNOR', governor_cost=1, child_cost=2, return_cost=1, useful_value=5))
    value.update(changes)
    return value


class LiveC5Gate:
    """Private component of one fixed executor; no serialized result entrypoint.

    The enclosing captured-source executor must create the actual Popen child
    and socketpair from its fully acquired image. The gate takes exclusive wait
    custody: the caller must not poll/wait/reap that child independently.
    """
    def __init__(self, output, process, channel, *, expected_source, expected_context,
                 executable_inputs, acquisition_digest, require_current, wall_seconds=120):
        _CHECK()
        demand(type(process) is subprocess.Popen and process.returncode is None,
               'live gate requires the actual unreaped Popen child')
        demand(type(channel) is socket.socket and channel.family == socket.AF_UNIX,
               'live gate requires its private local channel')
        demand(signal.getsignal(signal.SIGCHLD) == signal.SIG_DFL,
               'external child reaping is unsupported')
        demand(type(wall_seconds) is int and 0 < wall_seconds <= 120,
               'live gate wall bound differs')
        demand(E.HEX.fullmatch(acquisition_digest) is not None, 'invalid acquisition identity')
        demand(callable(require_current), 'missing owner currentness closure')
        self.process, self.channel = process, channel
        self.pid, self.owner_pid = process.pid, os.getpid()
        demand(os.getpgid(self.pid) == self.pid and os.getsid(self.pid) == self.pid,
               'live gate child requires its own actual session and process group')
        self.fd_identity = file_identity(os.fstat(channel.fileno()))
        self.pidfd = os.pidfd_open(self.pid) if hasattr(os, 'pidfd_open') else None
        self.started, self.deadline = time.monotonic(), time.monotonic() + wall_seconds
        self.expected_source, self.expected_context = json.loads(encode(expected_source)), dict(expected_context)
        self.executable_inputs = dict(executable_inputs)
        self.acquisition_digest, self.require_current = acquisition_digest, require_current
        self.output = E.no_alias(Path(output), missing=True)
        demand(not self.output.exists(), 'live gate evidence must be fresh')
        self.output.mkdir(mode=0o700)
        self.output_identity = directory_identity(self.output.stat())
        self.capture = self.output / 'capture'
        for path in (self.capture, self.capture / 'blobs', self.capture / 'events', self.capture / 'processes'):
            path.mkdir(mode=0o700)
        self._owned, self._captured, self._projections, self._effects = {}, {}, {}, {}
        self._session = self._contract = self._pending = self._consumer_frontier = None
        self._sequence, self._event_count, self._received_bytes = 0, 0, 0
        self._finished = self._failed = self._closed = self._reaped = False
        self._wait_result = None
        self._lock = threading.RLock()
        self._live_child()

    def _live_child(self):
        demand(not self._closed and os.getpid() == self.owner_pid,
               'closed or transferred live gate cannot resume')
        demand(not self._reaped and self.process.returncode is None, 'child already reaped')
        try:
            state = os.waitid(os.P_PID, self.pid, os.WEXITED | os.WNOHANG | os.WNOWAIT)
        except ChildProcessError as exc:
            raise LiveGateError('actual direct-child custody is absent') from exc
        demand(state is None, 'actual direct child is already terminal')
        demand(file_identity(os.fstat(self.channel.fileno())) == self.fd_identity,
               'inherited channel identity changed')
        demand(directory_identity(E.no_alias(self.output).stat()) == self.output_identity,
               'owned evidence root changed')
        _CHECK()
        self.require_current()
        self._check_owned()

    def _write(self, relative, raw):
        path = self.output / relative
        storage_mode = 0o600 if relative.startswith('capture/') else 0o400
        path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        E.no_alias(path.parent)
        demand(not path.exists() and not path.is_symlink(), 'owned evidence already exists')
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
        try:
            view = memoryview(raw)
            while view:
                size = os.write(fd, view)
                demand(size > 0, 'owned evidence write made no progress')
                view = view[size:]
            os.fsync(fd)
            os.fchmod(fd, storage_mode)
            identity = file_identity(os.fstat(fd))
        finally:
            os.close(fd)
        self._owned[relative] = dict(bytes=len(raw), sha256=digest(raw), identity=identity, mode=storage_mode)

    def _check_owned(self):
        for relative, expected in self._owned.items():
            path = E.no_alias(self.output / relative)
            info = path.lstat()
            demand(file_identity(info) == expected['identity'] and stat.S_IMODE(info.st_mode) == expected['mode'],
                   'owned evidence identity or mode changed')
            raw, _ = E.read_regular(path, max(E.MAX_PROCESS_JSON, E.MAX_FILE))
            demand(len(raw) == expected['bytes'] and digest(raw) == expected['sha256'],
                   'owned evidence bytes changed')

    def _read_exact(self, count):
        demand(type(count) is int and 0 <= count <= E.MAX_PROCESS_JSON,
               'live transport object exceeds its inherited bound')
        data = bytearray()
        while len(data) < count:
            remaining = self.deadline - time.monotonic()
            demand(remaining > 0, 'live gate wall bound expired')
            self.channel.settimeout(remaining)
            chunk = self.channel.recv(min(65536, count - len(data)))
            demand(bool(chunk), 'live child channel closed before handoff')
            data.extend(chunk)
        return bytes(data)

    def _reply(self, phase, accepted, token):
        raw = encode(dict(schema=E.LIVE_REPLY_SCHEMA, phase=phase, accepted=accepted, token=token))
        self.channel.sendall(len(raw).to_bytes(8, 'big') + raw)

    @staticmethod
    def _member_limit(name):
        if name in ('session.json', 'close.json', 'record.json'):
            return E.MAX_JSON
        group, slash, leaf = name.partition('/')
        demand(slash and '/' not in leaf, 'foreign live capture path')
        if group == 'blobs' and E.HEX.fullmatch(leaf):
            return E.MAX_FILE
        if group == 'events' and E.re.fullmatch(r'[0-9]{2}\.json', leaf):
            return E.MAX_JSON
        if group == 'processes' and E.re.fullmatch(r'[0-9]{2}(?:\.handoff)?\.json', leaf):
            return E.MAX_PROCESS_JSON
        raise LiveGateError('foreign live capture member')

    def _receive(self):
        count = int.from_bytes(self._read_exact(8), 'big')
        demand(0 < count <= E.MAX_JSON, 'live frame header bound exceeded')
        raw = self._read_exact(count)
        frame = json.loads(raw.decode('utf-8', 'strict'))
        demand(encode(frame) == raw, 'live frame must use canonical unambiguous JSON')
        E.fields(frame, 'schema phase payload files', 'live frame')
        demand(frame['schema'] == E.LIVE_FRAME_SCHEMA and frame['phase'] in {'INIT', 'BEFORE', 'AFTER', 'FINISH'},
               'live frame schema or phase differs')
        rows = frame['files']
        demand(type(rows) is list and len(rows) <= E.MAX_LIVE_FILES, 'live frame population exceeds bound')
        names = []
        total = blob_total = 0
        for row in rows:
            E.fields(row, 'path bytes sha256 mode', 'live capture descriptor')
            name = row['path']
            demand(type(name) is str and type(row['bytes']) is int and type(row['mode']) is int
                   and E.HEX.fullmatch(row['sha256']) is not None, 'malformed live descriptor')
            limit = self._member_limit(name)
            demand(0 <= row['bytes'] <= limit and row['mode'] == 0o600,
                   'live capture object mode or size differs')
            names.append(name)
            total += row['bytes']
            if name.startswith('blobs/'):
                blob_total += row['bytes']
        demand(names == sorted(set(names)) and total <= E.MAX_LIVE_FRAME_BYTES and blob_total <= E.MAX_TOTAL,
               'live complete capture exceeds bounds or repeats a member')
        demand(set(self._captured) <= set(names), 'live capture omitted a retained predecessor')
        self._received_bytes += len(raw) + total
        demand(self._received_bytes <= 2 * 1024**3, 'live transport/evidence allocation exceeded')
        for row in rows:
            data = self._read_exact(row['bytes'])
            name = row['path']
            demand(digest(data) == row['sha256'], 'live object bytes differ from descriptor')
            if name.startswith('blobs/'):
                demand(name[6:] == row['sha256'], 'live blob address differs')
            if name in self._captured:
                demand(row == self._captured[name], 'live predecessor descriptor changed')
                owned = self._owned['capture/' + name]
                demand(owned['sha256'] == row['sha256'] and owned['bytes'] == row['bytes'],
                       'live predecessor bytes changed')
            else:
                self._write('capture/' + name, data)
                self._captured[name] = dict(row)
        self._sequence += 1
        self._write('transport/%03d.json' % self._sequence, raw)
        return frame, digest(raw)

    def _initialize(self):
        reader = E.Readback(self.capture)
        session = E.load_session(self.capture, reader)
        demand(session['source'] == self.expected_source, 'live original source differs from acquired image')
        context = session['context']
        for name in ('repository', 'cwd', 'python_command'):
            demand(context[name] == self.expected_context[name], 'live original context differs')
        work = Path(context['work_root'])
        demand(work.parent == Path(self.expected_context['work_parent']) and work.name not in ('.', '..'),
               'live clone/output root is outside its fixed private allocation')
        demand(not E.event_files(self.capture), 'imported event history cannot initialize a live gate')
        demand(not os.listdir(self.capture / 'processes'), 'imported process history cannot initialize a live gate')
        self._session = session
        future = lambda name: dict(node=name, condition='actual live owned original event and current effect bytes')
        artifacts = ['path:artifacts/' + lane + '/' + name for lane in 'ab' for name in E.MEMBERS]
        nodes = [node(ROOT_NODE, parent=None, kind='PLAN', requires=[FINAL], reads=[]),
                 node(BUILD_A, effect='PREPARATION', writes=['path:artifacts/a'], future_consumer=future(OUTPUT)),
                 node(BUILD_B, effect='PREPARATION', writes=['path:artifacts/b'], future_consumer=future(OUTPUT)),
                 node(OUTPUT, kind='JOIN', requires=[BUILD_A, BUILD_B], reads=artifacts, future_consumer=future(FINAL)),
                 node(CONSUMERS, requires=[OUTPUT], reads=['path:source.json', *artifacts], future_consumer=future(FINAL)),
                 node(FINAL, kind='JOIN', requires=[OUTPUT, CONSUMERS], reads=[])]
        state = dict(schema='implementaudit.native-state.v1', campaign=PROFILE, root=ROOT_NODE,
            original_scope='Two actual original48 builds, required output JOIN, then its 17 original consumers',
            nodes=[item['id'] for item in nodes], event=dict(id='c5-live-effect', kind='RETURN', subject=BUILD_A),
            context=dict(host_capacity=1, operator_ceiling=None, reserve=0, route_facts=[], outstanding_deliveries=[]))
        documents = {'STATE.md': state, 'ROADMAP.md': dict(schema='implementaudit.native-roadmap.v1', phases=[])}
        for item in nodes:
            name = ('plans/' if item['kind'] == 'PLAN' else 'tasks/') + item['id'] + '.md'
            documents[name] = dict(schema='implementaudit.native-spec.v1', nodes=[item])
        for name, value in documents.items():
            self._write('contract/' + name, b'```implementaudit-work-graph\n' + encode(value) + b'```\n')
        self._write('inputs/source.json', encode(dict(acquisition=self.acquisition_digest, source=self.expected_source)))
        self._contract = C.CompletionContract(self.output / 'contract', self.output / 'journal',
            input_root=self.output / 'inputs', compiler_sha256=COMPILER_SHA)

    def _prefix(self):
        reader = E.Readback(self.capture)
        events, _ = E.read_events(self.capture, reader, self._session)
        issues, generations = E.assess_events(reader, self._session, events)
        processes, failures, process_issues = E.read_process_results(self.capture, reader, self._session, events)
        incomplete = len(events) < len(E.profile(self._session))
        allowed = ['INCOMPLETE_FINITE_PROFILE'] if incomplete else []
        allowed_process = ['INCOMPLETE_PROCESS_PROFILE'] if incomplete else []
        demand(len(processes) == len(events) and issues == allowed and not failures
               and process_issues == allowed_process,
               'actual producer/consumer outcome, clone, source or raw correspondence refused')
        return reader, events, generations

    def _before(self, payload):
        demand(self._session is not None and self._pending is None and not self._failed and not self._finished,
               'missing, repeated or post-failure live invocation')
        E.fields(payload, 'common inputs outputs source clone executable', 'live before')
        common = payload['common']
        names = 'schema profile run_id index event_id role source_sha256 argv cwd environment_sha256 environment_projection stdin'
        E.fields(common, names, 'live invocation intent')
        index = self._event_count
        specs = E.profile(self._session)
        demand(index < len(specs), 'extra live invocation')
        spec = specs[index]
        event_id = self._session['run_id'] + ':' + ('%02d' % index) + ':' + spec['role']
        demand(common['schema'] == E.SCHEMA and common['profile'] == E.PROFILE
               and common['run_id'] == self._session['run_id'] and type(common['index']) is int
               and common['index'] == index and common['event_id'] == event_id
               and common['role'] == spec['role'] and common['argv'] == spec['argv']
               and common['cwd'] == self._session['context']['cwd']
               and common['source_sha256'] == digest(encode(self._session['source'])),
               'foreign or reordered live command')
        reader, events, generations = self._prefix()
        demand(len(events) == index, 'live invocation skipped or replayed an outcome')
        demand(payload['source'] == self._session['source_custody'], 'source drift before live dispatch')
        for field, expected in (('inputs', spec['inputs']), ('outputs', spec['outputs'])):
            observed = payload[field]
            demand(type(observed) is list and len(observed) == len(expected), 'live operand omission')
            for value, path in zip(observed, expected):
                E.observation(reader, value, path)
                if field == 'inputs':
                    demand(value == generations.get(path), 'consumer does not hold its exact live producer generation')
        clone_issues = []
        E.validate_clone(reader, self._session, payload['clone'], spec['lane'], clone_issues, spec['role'])
        demand(not clone_issues, 'clone source or currentness refused before dispatch')
        executable = payload['executable']
        demand(type(executable) is dict and executable.get('kind') == 'FILE', 'unavailable actual executable')
        E.observation(reader, executable, executable['path'])
        demand(self.executable_inputs.get(executable['path']) == executable['blob']['sha256'],
               'actual executable is outside the complete acquired runtime')
        if spec['inline']:
            demand(common['stdin']['mode'] == 'INLINE_BYTES'
                   and reader.blob(common['stdin']['blob']) == E.manifest_program(reader, self._session),
                   'original heredoc differs before dispatch')
        else:
            demand(common['stdin'] == dict(mode='INHERITED_UNQUALIFIED'), 'unexpected original stdin')
        if spec['role'] in BUILD_NODES:
            expected_environment = dict(SOURCE_DATE_EPOCH='315532800', TZ='UTC' if spec['lane'] == 'a' else 'America/New_York', LC_ALL='C')
            demand(common['environment_projection'] == expected_environment, 'original build environment differs')
            frontier = self._contract.frontier()
            demand(frontier['selected'] == [BUILD_NODES[spec['role']]], 'shared compiler did not select this actual builder')
        else:
            if self._consumer_frontier is None:
                demand(index == 2 and len(self._effects) == 6, 'consumer lacks both complete live build effects')
                view = self._contract.frontier()
                demand(view['selected'] == [OUTPUT], 'required output JOIN was not selected')
                verdict = self._contract.join(OUTPUT, expected_old=self._contract.history_digest)
                demand(verdict['status'] == 'SATISFIED_AT_DECLARED_RESULT_CONTRACT', 'required live output JOIN refused')
                self._write('output-join.json', encode(verdict))
                self._consumer_frontier = self._contract.frontier()
                demand(self._consumer_frontier['selected'] == [CONSUMERS], 'consumer was not released by the required JOIN')
            frontier = self._consumer_frontier
        token = os.urandom(32).hex()
        released_at = time.monotonic_ns()
        admission = dict(event_id=event_id, index=index, role=spec['role'],
            acquisition=self.acquisition_digest, actual_outer_child=self.pid,
            token_sha256=digest(token.encode()), release_monotonic_ns=released_at,
            required_output_join_sha256=None if index < 2 else self._owned['output-join.json']['sha256'],
            consumer_release_requires_live_output_join=index >= 2, authority='NONE')
        self._write('dispatch/%02d.json' % index, encode(admission))
        self._pending = dict(token=token, common=common, frontier=frontier, spec=spec, released_at=released_at)
        return token

    def _result(self, frontier, stage, evidence):
        return dict(schema='implementaudit.work-result.v1', node=stage, dispatch_id=frontier['dispatch_id'],
            graph_digest=frontier['graph_digest'], input_digest=frontier['inputs'][stage], status='PASS', terminal=True,
            exit_code=0, evidence_digest=evidence, independence_key=self.acquisition_digest + '-' + stage, scope=[stage])

    def _after(self, payload, frame_digest):
        demand(self._pending is not None and not self._finished, 'unowned or repeated live outcome')
        E.fields(payload, 'event_id token', 'live after')
        pending = self._pending
        demand(payload['event_id'] == pending['common']['event_id'] and payload['token'] == pending['token'],
               'outcome belongs to another invocation or channel generation')
        reader, events, _ = self._prefix()
        demand(len(events) == self._event_count + 1, 'actual outcome is missing or duplicated')
        actual = events[-1]
        demand(all(actual[name] == value for name, value in pending['common'].items()),
               'actual outcome differs from the live admitted command')
        demand(actual['start_monotonic_ns'] >= pending['released_at'],
               'actual event began before its live dispatch release')
        role = pending['spec']['role']
        if role in BUILD_NODES:
            outputs = actual['outputs_after']
            demand(len(outputs) == 1 and E.release_directory(outputs[0]), 'actual builder did not produce its exact release namespace')
            lane = pending['spec']['lane']
            for item in outputs[0]['members']:
                name = Path(item['path']).name
                raw = reader.blob(item['blob'])
                relative = 'artifacts/' + lane + '/' + name
                demand(relative not in self._effects, 'live artifact generation already exists')
                self._write('inputs/' + relative, raw)
                self._effects[relative] = dict(actual=item, event_id=actual['event_id'],
                    frame_sha256=frame_digest, acquisition=self.acquisition_digest)
            stage, consumer = BUILD_NODES[role], OUTPUT
        elif self._event_count == len(E.profile(self._session)) - 1:
            stage, consumer = CONSUMERS, FINAL
        else:
            stage = consumer = None
        if stage is not None:
            evidence = digest(encode(dict(frame=frame_digest, actual_events=events, effects=self._effects,
                acquisition=self.acquisition_digest, actual_outer_child=self.pid)))
            self._contract.accept(pending['frontier'], [self._result(pending['frontier'], stage, evidence)], consumer,
                                  expected_old=self._contract.history_digest)
        self._event_count += 1
        self._pending = None
        return os.urandom(32).hex()

    def handle_next(self):
        """Read only this owned live channel; there is no record-import variant."""
        with self._lock:
            phase, token = None, '0' * 64
            try:
                self._live_child()
                frame, frame_digest = self._receive()
                phase, payload = frame['phase'], frame['payload']
                closing_names = {'close.json', 'record.json'} & set(self._captured)
                demand(closing_names == (set() if phase != 'FINISH' else {'close.json', 'record.json'}),
                       'live closing records appeared in the wrong phase')
                if phase == 'INIT':
                    demand(self._session is None and self._sequence == 1, 'live INIT is missing or repeated')
                    E.fields(payload, 'run_id', 'live init')
                    self._initialize()
                    demand(payload['run_id'] == self._session['run_id'], 'live run identity differs')
                    token = os.urandom(32).hex()
                elif phase == 'BEFORE':
                    token = self._before(payload)
                elif phase == 'AFTER':
                    token = self._after(payload, frame_digest)
                else:
                    demand(self._session is not None and not self._finished, 'live FINISH is missing or repeated')
                    E.fields(payload, 'run_id complete script_exit', 'live finish')
                    demand(payload['run_id'] == self._session['run_id'], 'foreign live closing run')
                    record = E.verify_record(self.capture, expected_source=self.expected_source,
                                             expected_run_id=self._session['run_id'], require_complete=False)
                    demand(payload['complete'] == record['assessment']['complete'], 'closing completeness differs')
                    closing = E.json_read(self.capture / 'close.json')
                    demand(payload['script_exit'] == closing['script_exit'], 'actual original exit handoff differs')
                    self._finished = True
                    self._failed |= not payload['complete'] or payload['script_exit'] != 0 or self._pending is not None
                    token = os.urandom(32).hex()
                self._live_child()
                self._reply(phase, True, token)
                return dict(phase=phase, observed_events=self._event_count, finished=self._finished,
                            failed=self._failed, authority='NONE')
            except BaseException:
                self._failed = True
                if phase is not None:
                    try:self._reply(phase, False, token)
                    except (OSError, LiveGateError):pass
                raise

    def _reap(self, *, terminate):
        if self._reaped:
            return self._wait_result
        try:
            waited = os.wait4(self.pid, os.WNOHANG)
        except ChildProcessError as exc:
            raise LiveGateError('direct child was reaped outside its live gate') from exc
        killed = False
        if not waited[0] and terminate:
            # This still-unreaped direct child cannot have its PID reused.
            try:
                if self.pidfd is not None:
                    signal.pidfd_send_signal(self.pidfd, signal.SIGKILL, None, 0)
                else:
                    os.kill(self.pid, signal.SIGKILL)
                killed = True
            except ProcessLookupError:
                # Exit may win this race; actual wait4 custody still requires
                # collection below. No numeric group kill is ever inferred.
                pass
        deadline = time.monotonic() + 3
        while not waited[0] and time.monotonic() < deadline:
            time.sleep(0.01)
            waited = os.wait4(self.pid, os.WNOHANG)
        demand(waited[0] == self.pid, 'actual direct child has not been reaped within cleanup bound')
        self.process.returncode = os.waitstatus_to_exitcode(waited[1])
        self._reaped = True
        group_absent = False
        while True:
            try:
                os.killpg(self.pid, 0)  # Observation only; reaped PID gives no kill authority.
            except ProcessLookupError:
                group_absent = True
                break
            if time.monotonic() >= deadline:
                break
            time.sleep(0.01)
        self._wait_result = dict(actual_pid=self.pid, wait4_reaped=True, exit_code=self.process.returncode,
            wait_status=waited[1], max_rss_kib=waited[2].ru_maxrss, direct_child_killed=killed,
            group_absent=group_absent, numeric_group_signalled=False)
        return self._wait_result

    def finalize(self):
        """Accept the final JOIN only after the actual original has exited."""
        with self._lock:
            demand(os.getpid() == self.owner_pid and not self._closed, 'live finalizer owner changed')
            waited = self._reap(terminate=False)
            self._write('actual-outer-process.json', encode(waited))
            demand(self._finished and not self._failed and self._pending is None and waited['exit_code'] == 0
                   and waited['group_absent'] and self._event_count == 19, 'actual original did not close its full live gate')
            _CHECK();self.require_current();self._check_owned()
            E.verify_record(self.capture, expected_source=self.expected_source,
                            expected_run_id=self._session['run_id'], require_complete=True)
            verdict = self._contract.join(FINAL, expected_old=self._contract.history_digest)
            demand(verdict['status'] == 'SATISFIED_AT_DECLARED_RESULT_CONTRACT', 'final live C5 JOIN refused')
            self._write('final-join.json', encode(verdict))
            result = dict(schema='implementaudit.c5-live-gate-result.v1', scope=PROFILE,
                status='SATISFIED_AT_LIVE_PORTABLE_GATE_CONTRACT', acquisition=self.acquisition_digest,
                actual_outer_process=waited, validated_live_event_records=19, artifacts=len(self._effects),
                output_join_preceded_first_consumer=True, history_digest=self._contract.history_digest,
                enclosing_execution_image_qualification='REQUIRED_SEPARATELY_FROM_THIS_GATE_COMPONENT',
                original48_execution_qualified=False, canonical_acceptance='UNQUALIFIED',
                native_dispatch_authorized=False, authority='NONE')
            self._write('result.json', encode(result))
            return result

    def close(self):
        with self._lock:
            if self._closed:
                return
            try:
                if not self._reaped:
                    waited = self._reap(terminate=True)
                    self._write('contained-outer-process.json', encode(waited))
            finally:
                try:
                    if self._contract is not None:self._contract.close()
                finally:
                    self.channel.close()
                    if self.pidfd is not None:os.close(self.pidfd)
                    self._closed = True
