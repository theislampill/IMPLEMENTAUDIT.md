#!/usr/bin/env python3
"""R0035 repository completion consumer; no executor or acceptance issuer.

CompletionContract qualifies declared result/consumer semantics over freshly
acquired filesystem inputs. It has NO native dispatch or lifecycle authority.
The separate native reader accepts no serialized result and retains only the
existing fixed ordinary producer's singleton receiving observation.
"""
from contextlib import contextmanager
import copy
import fcntl
from functools import wraps
import hashlib
import json
import os
from pathlib import Path
import stat
import types
import threading
import uuid

MAX_JOURNAL_BYTES = 64 * 1024 * 1024
MAX_EVENTS = 1024
RESULT_FIELDS = {'schema', 'node', 'dispatch_id', 'graph_digest', 'input_digest',
                 'status', 'terminal', 'exit_code', 'evidence_digest',
                 'independence_key', 'scope'}
STATUSES = {'PASS', 'FAIL', 'PARTIAL', 'NONVERDICT', 'UNKNOWN', 'PENDING',
            'INTERRUPTED', 'TRANSPORT_FAILURE'}

class CompletionError(ValueError):
    pass

def _require(condition, message):
    if not condition:
        raise CompletionError(message)

def _raw(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'),
                      ensure_ascii=False, allow_nan=False).encode('utf-8')

def _hash(value):
    return hashlib.sha256(_raw(value)).hexdigest()

def _identity(st):
    return (st.st_dev, st.st_ino, st.st_mode, st.st_nlink, st.st_size,
            st.st_mtime_ns, st.st_ctime_ns)

def _physical(path):
    path = Path(path).absolute()
    for part in (path, *path.parents):
        st = part.lstat()
        _require(not stat.S_ISLNK(st.st_mode) and not getattr(st, 'st_file_attributes', 0) & 0x400,
                 'physical path contains a link or reparse point')
    return path

def _read(path, maximum):
    path = _physical(path)
    before = path.lstat()
    _require(stat.S_ISREG(before.st_mode) and before.st_nlink == 1 and before.st_size <= maximum,
             'unsafe or oversized physical file')
    # Reject a post-lstat FIFO replacement before attempting any read.
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    try:
        _require(_identity(os.fstat(fd)) == _identity(before), 'physical file changed before read')
        chunks, size = [], 0
        while True:
            chunk = os.read(fd, min(65536, maximum + 1 - size))
            if not chunk:
                break
            chunks.append(chunk)
            size += len(chunk)
            _require(size <= maximum, 'physical file exceeded bound')
        _require(_identity(os.fstat(fd)) == _identity(before) == _identity(path.lstat()),
                 'physical file changed during read')
        return b''.join(chunks), _identity(before)
    finally:
        os.close(fd)

class _Compiler:
    def __init__(self, expected_sha256=None):
        self.path = Path(__file__).absolute().parents[1] / 'skills/implementaudit/scripts/compile-work-graph.py'
        self.raw, self.identity = _read(self.path, 1024 * 1024)
        if expected_sha256 is not None:
            _require(type(expected_sha256) is str and len(expected_sha256) == 64
                     and all(c in '0123456789abcdef' for c in expected_sha256)
                     and hashlib.sha256(self.raw).hexdigest() == expected_sha256,
                     'captured compiler differs from required source digest')
        module = types.ModuleType('_r0035_completion_compiler')
        module.__file__ = str(self.path)
        # Execute captured physically checked bytes, never a module-cache entry.
        exec(compile(self.raw, str(self.path), 'exec'), module.__dict__)
        self.module = module
        self.check()

    def check(self):
        _require(_read(self.path, 1024 * 1024) == (self.raw, self.identity),
                 'executed compiler source changed')

class _Journal:
    """Single cooperating writer; retained JSON is evidence, never a credential."""
    def __init__(self, root, run_identity, decoder):
        self._process_id = os.getpid()
        self.root = Path(root).absolute()
        self.root.mkdir(mode=0o700, parents=False, exist_ok=True)
        self.root = _physical(self.root)
        st = self.root.stat()
        _require(stat.S_ISDIR(st.st_mode) and st.st_uid == os.getuid() and not st.st_mode & 0o022,
                 'journal requires a private owned directory')
        self.directory = (st.st_dev, st.st_ino)
        self.fd = os.open(self.root / 'writer.lock', os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
        self.closed = False
        try:
            lock = os.fstat(self.fd)
            _require(stat.S_ISREG(lock.st_mode) and lock.st_nlink == 1 and lock.st_size == 0,
                     'unsafe journal writer gate')
            try:
                fcntl.flock(self.fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError as exc:
                raise CompletionError('journal already has a writer') from exc
            self.lock_identity = (lock.st_dev, lock.st_ino)
            self.path = self.root / 'history.json'
            if self.path.exists() or self.path.is_symlink():
                raw, _ = _read(self.path, MAX_JOURNAL_BYTES)
                self.value = decoder(raw, 'completion journal')
                _require(type(self.value) is dict and set(self.value) == {'schema', 'run_identity', 'events'}
                         and self.value['schema'] == 'implementaudit.completion-history.v1'
                         and self.value['run_identity'] == run_identity,
                         'foreign or malformed completion journal')
                events = self.value['events']
                _require(type(events) is list and len(events) <= MAX_EVENTS, 'journal event bound')
                previous = None
                for event in events:
                    _require(type(event) is dict and set(event) == {'previous', 'kind', 'body', 'digest'}
                             and event['previous'] == previous and event['kind'] in {'BATCH', 'JOIN'},
                             'journal chain or version mismatch')
                    _require(event['digest'] == _hash({k: v for k, v in event.items() if k != 'digest'}),
                             'journal digest mismatch')
                    previous = event['digest']
                self.disk = raw
            else:
                self.value = dict(schema='implementaudit.completion-history.v1',
                                  run_identity=run_identity, events=[])
                self.disk = None
            self.digest = _hash(self.value)
            self.check()
        except BaseException:
            self.close()
            raise

    def check(self, allowed_pending=None):
        _require(self._process_id == os.getpid(), 'journal belongs to another process')
        _require(not self.closed, 'journal writer is closed')
        st = _physical(self.root).stat()
        _require((st.st_dev, st.st_ino) == self.directory, 'journal directory replaced')
        with os.scandir(self.root) as entries:
            for index, entry in enumerate(entries):
                _require(index < MAX_EVENTS + 3, 'journal directory entry bound')
                _require(not entry.name.startswith('pending-') or Path(entry.path) == allowed_pending,
                         'pending journal transaction requires recovery')
        lock = _physical(self.root / 'writer.lock').stat()
        _require((lock.st_dev, lock.st_ino) == self.lock_identity and lock.st_nlink == 1,
                 'journal writer gate replaced')
        if self.disk is None:
            _require(not os.path.lexists(self.path), 'journal expected-old changed')
        else:
            _require(_read(self.path, MAX_JOURNAL_BYTES)[0] == self.disk, 'journal expected-old changed')

    def append(self, kind, body, expected_old):
        self.check()
        _require(expected_old == self.digest, 'journal expected-old mismatch')
        _require(len(self.value['events']) < MAX_EVENTS, 'journal event bound')
        event = dict(previous=self.value['events'][-1]['digest'] if self.value['events'] else None,
                     kind=kind, body=copy.deepcopy(body))
        event['digest'] = _hash(event)
        value = copy.deepcopy(self.value)
        value['events'].append(event)
        raw = _raw(value) + b'\n'
        _require(len(raw) <= MAX_JOURNAL_BYTES, 'journal byte bound')
        pending = self.root / ('pending-' + uuid.uuid4().hex + '.json')
        fd = os.open(pending, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
        with os.fdopen(fd, 'wb') as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
        self.check(allowed_pending=pending)
        os.replace(pending, self.path)
        directory = os.open(self.root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
        self.value, self.disk, self.digest = value, raw, _hash(value)
        return copy.deepcopy(event)

    def close(self):
        if not self.closed:
            self.closed = True
            # Closing a fork child's descriptor leaves the parent's writer gate
            # held. Never explicitly unlock their shared open-file description.
            os.close(self.fd)

def _serialized(method):
    @wraps(method)
    def call(self, *args, **kwargs):
        # A fork can inherit an RLock held by a thread that no longer exists.
        _require(self._process_id == os.getpid(), 'completion receiver belongs to another process')
        with self._operation_lock:
            return method(self, *args, **kwargs)
    return call

class CompletionContract:
    """Fresh portable consumer of declared result contracts, authority NONE.

    No run command, producer callback, graph import, native-mode flag or native
    acceptance API exists here. The original source graph is never rewritten.
    Reopening a journal holds previously observed nodes until producer custody
    is re-established; it cannot restore accepted results from JSON.
    """
    def __init__(self, run_root, journal_root, *, input_root=None, compiler_sha256=None):
        self._process_id = os.getpid()
        self._operation_lock = threading.RLock()
        self.owner = _Compiler(expected_sha256=compiler_sha256)
        self.wg = self.owner.module
        self.run = _physical(run_root)
        self.inputs = _physical(input_root if input_root is not None else run_root)
        self.journal = _Journal(journal_root, _hash([str(self.run), str(self.inputs)]),
                                self.wg.decode_strict_json_bytes)
        self._live, self._issued = {}, {}
        self._recovery = set()
        try:
            for event in self.journal.value['events']:
                body = event['body']
                _require(type(body) is dict and type(body.get('records')) is list, 'malformed history body')
                for record in body['records']:
                    _require(type(record) is dict and type(record.get('node')) is str, 'malformed history record')
                    self._recovery.add(record['node'])
        except BaseException:
            self.close()
            raise

    @_serialized
    def __enter__(self):
        return self

    def __exit__(self, *unused):
        self.close()

    def close(self):
        if self._process_id != os.getpid():
            # Inherited cleanup has no receiver use or live-custody authority.
            self.journal.close()
            return
        with self._operation_lock:
            self.journal.close()

    @property
    @_serialized
    def history_digest(self):
        return self.journal.digest

    @contextmanager
    def _graph(self):
        self.journal.check()
        self.owner.check()
        try:
            with self.wg.observe_native_run_v1(self.run, input_root=self.inputs) as raw:
                yield self.wg.decode_strict_json_bytes(raw, 'completion source graph')
            self.owner.check()
            self.journal.check()
        except self.wg.WorkGraphError as exc:
            raise CompletionError(str(exc)) from exc

    def _applicable(self, graph):
        nodes = {n['id']: n for n in graph['nodes']}
        valid, invalid = {}, set()
        pending = dict(self._live)
        while pending:
            progress = False
            for name, record in list(pending.items()):
                deps = record['predecessors']
                if any(dep in pending for dep in deps):
                    continue
                delta = self.wg.diff_native_graphs_v1(record['source_graph'], graph)
                applicable = (name in nodes and name not in delta['invalidated']
                              and all(valid.get(dep, {}).get('digest') == identity for dep, identity in deps.items()))
                if applicable:
                    valid[name] = record
                else:
                    invalid.add(name)
                del pending[name]
                progress = True
            _require(progress, 'completion history dependency cycle')
        return valid, invalid

    def _derive(self, graph):
        valid, invalid = self._applicable(graph)
        outcomes = {name: dict(status=record['status'], digest=record['digest']) for name, record in valid.items()}
        for name in self._recovery:
            if name in {n['id'] for n in graph['nodes']}:
                outcomes[name] = dict(status='RECOVERY_CUSTODY_UNVERIFIED', digest=self.history_digest)
        frontier = self.wg.derive_completion_frontier_v1(graph, outcomes)
        frontier.update(history_digest=self.history_digest, invalidated=sorted(invalid),
                        evidence_scope='PORTABLE_DECLARED_RESULT_CONTRACT',
                        recovery_status='PRODUCER_REOBSERVATION_REQUIRED' if self._recovery else 'LIVE_CONTRACT_ONLY')
        return frontier, valid

    def _transition(self, graph, frontier, valid):
        # Historical JSON alone never contributes. Every projected record must
        # still be retained by this live consumer and pass fresh applicability.
        _require(_hash(self.journal.value) == self.history_digest, 'live journal projection changed')
        context = self.wg._recursive_context_v1(graph, frontier, graph['event']['subject'])
        events, ancestry, directions = [], {}, {}
        for event in self.journal.value['events']:
            records = []
            for record in event['body']['records']:
                name = record['node']
                current = valid.get(name)
                if current is None or current['digest'] != record['digest']:
                    continue
                _require(current == record, 'live completion record differs from its journal')
                result = record['result']
                source = next(n for n in record['source_graph']['nodes'] if n['id'] == name)
                records.append(dict(node=name, digest=record['digest'], status=record['status'],
                    consumer=record['consumer'], scope=copy.deepcopy(result['scope']),
                    dispatch_id=result['dispatch_id'], input_digest=result['input_digest'],
                    evidence_digest=result['evidence_digest'],
                    source_graph_digest=record['source_graph']['digest'],
                    required=copy.deepcopy(source['requires']), optional=copy.deepcopy(source['optional']),
                    declared_future_consumer=copy.deepcopy(source['future_consumer']),
                    effect=source['effect'], authority=copy.deepcopy(source['authority']),
                    predecessors=copy.deepcopy(record['predecessors'])))
                reconsidered = self.wg._recursive_context_v1(graph, frontier, name)
                ancestry[name] = reconsidered['ancestors']
                directions[name] = reconsidered['directions']
            if records:
                events.append(dict(digest=event['digest'], previous=event['previous'],
                                   kind=event['kind'],
                                   original_scope=[r['node'] for r in event['body']['records']],
                                   retained_scope=[r['node'] for r in records], records=records))
        return self.wg._seal_graph(dict(context,
            schema='implementaudit.completion-transition.v1', completion_events=events,
            retained_ancestry=ancestry, retained_directions=directions, native_campaign_proven=False,
            evidence_scope='PORTABLE_DECLARED_COMPLETION_TRANSITION'))

    def _frontier(self, recursive):
        with self._graph() as graph:
            frontier, valid = self._derive(graph)
            if recursive:
                frontier = self._transition(graph, frontier, valid)
            predecessors = {node['id']: {dep: valid.get(dep, {}).get('digest')
                            for dep in node['requires'] + node['optional']}
                            for node in graph['nodes'] if node['id'] in frontier['selected']}
        # Issue only after every input/source observation guard has closed.
        _require(len(self._issued) < MAX_EVENTS, 'live dispatch retention bound')
        raw = _raw(frontier)
        _require(len(raw) <= MAX_JOURNAL_BYTES, 'completion projection byte bound')
        # Retain pending record identities on the exact issuing object. A second
        # otherwise equal frontier must not acquire another dispatch's custody.
        self._issued[id(frontier)] = (frontier, raw, copy.deepcopy(graph), set(), predecessors, {})
        return frontier

    @_serialized
    def frontier(self):
        return self._frontier(False)

    @_serialized
    def transition(self):
        """Reconsider complete ancestry from current source and live scoped history.

        The compiler supplies the same selection as frontier(); no supplied
        event, history, completion or ancestor-DONE override is accepted.
        Portable journal events are evidence, not native event authority.
        """
        return self._frontier(True)

    @_serialized
    def accept(self, frontier, results, consumer, *, expected_old):
        issued = self._issued.get(id(frontier))
        _require(issued is not None and issued[0] is frontier and issued[1] == _raw(frontier),
                 'frontier was not issued here or was modified')
        _require(expected_old == self.history_digest, 'journal expected-old mismatch')
        with self._graph() as graph:
            current, valid = self._derive(graph)
            delta = self.wg.diff_native_graphs_v1(issued[2], graph)
            _require(all(issued[2][key] == graph[key] for key in ('campaign', 'root', 'original_scope')),
                     'stale campaign scope')
            nodes = {n['id']: n for n in graph['nodes']}
            _require(consumer in nodes and nodes[consumer]['kind'] == 'JOIN', 'unknown consumer')
            contributes = set(nodes[consumer]['requires'] + nodes[consumer]['optional'])
            _require(type(results) is list and results, 'nonempty result batch required')
            records, seen = [], set()
            for result in results:
                _require(type(result) is dict and set(result) == RESULT_FIELDS,
                         'malformed result envelope')
                name = result['node']
                _require(type(name) is str and name in frontier['selected'] and name not in seen,
                         'foreign, duplicate or undispatched contributor')
                seen.add(name)
                _require(nodes[name]['kind'] == 'TASK', 'JOIN completion requires the shared JOIN reducer')
                pending_digest = issued[5].get(name)
                settling = pending_digest is not None
                pending = valid.get(name)
                _require(not settling or (pending is not None and pending['digest'] == pending_digest
                         and pending['status'] == 'PENDING' and not pending['result']['terminal']),
                         'stale pending result custody')
                available = (current['states'].get(name) == 'READY' if not settling else
                             current['states'].get(name) == 'BLOCKED'
                             and current['blocked'].get(name) == ['COMPLETION_PENDING'])
                _require(name not in issued[3] and name not in delta['invalidated']
                         and available, 'stale or already consumed result')
                # An already executed contributor need not win a new dispatch.
                # Its original prerequisite identities must still be applicable.
                _require(issued[4][name] == {dep: valid.get(dep, {}).get('digest')
                         for dep in nodes[name]['requires'] + nodes[name]['optional']},
                         'stale predecessor result identities')
                prior_nodes = {n['id']: n for n in issued[2]['nodes']}
                _require(prior_nodes[name]['input_digest'] == nodes[name]['input_digest'], 'stale result inputs')
                future = nodes[name]['future_consumer']
                _require(name in contributes and (future is None or future['node'] == consumer),
                         'foreign consumer scope')
                _require(result['schema'] == 'implementaudit.work-result.v1' and result['scope'] == [name]
                         and result['dispatch_id'] == frontier['dispatch_id']
                         and result['graph_digest'] == frontier['graph_digest']
                         and result['input_digest'] == frontier['inputs'][name], 'result identity or scope mismatch')
                _require(type(result['status']) is str and result['status'] in STATUSES
                         and type(result['terminal']) is bool, 'invalid result status')
                _require(result['exit_code'] is None or type(result['exit_code']) is int, 'invalid exit code')
                if result['evidence_digest'] is not None:
                    self.wg._require_digest(result['evidence_digest'], 'result evidence')
                self.wg._native_name(result['independence_key'], 'result independence')
                _require(result['status'] != 'PASS' or (result['terminal'] and result['exit_code'] == 0
                         and result['evidence_digest'] is not None), 'contradictory PASS')
                _require(result['status'] != 'PENDING' or not result['terminal'], 'terminal PENDING')
                _require(not settling or (result['terminal'] and consumer == pending['consumer']
                         and result['independence_key'] == pending['result']['independence_key']),
                         'pending settlement must be terminal with unchanged consumer and independence')
                record = dict(node=name, status=result['status'], consumer=consumer,
                              source_graph=copy.deepcopy(issued[2]), result=copy.deepcopy(result),
                              predecessors=copy.deepcopy(issued[4][name]))
                record['digest'] = _hash(record)
                records.append(record)
        event = self.journal.append('BATCH', dict(records=records), expected_old)
        for record in records:
            name = record['node']
            self._live[name] = record
            if record['status'] == 'PENDING':
                issued[5][name] = record['digest']
            else:
                issued[5].pop(name, None)
                issued[3].add(name)
        if issued[3] == set(frontier['selected']):
            del self._issued[id(frontier)]
        return event

    @_serialized
    def join(self, consumer, *, expected_old):
        _require(expected_old == self.history_digest, 'journal expected-old mismatch')
        with self._graph() as graph:
            frontier, valid = self._derive(graph)
            nodes = {n['id']: n for n in graph['nodes']}
            _require(consumer in nodes and nodes[consumer]['kind'] == 'JOIN', 'unknown JOIN consumer')
            node = nodes[consumer]
            mapped = {}
            for name in node['requires'] + node['optional']:
                record = valid.get(name)
                if record is not None and record['consumer'] == consumer:
                    mapped[name] = record['result']
            verdict = self.wg._join_native_results_v1(graph, mapped, consumer)
            verdict.update(evidence_scope='PORTABLE_DECLARED_RESULT_CONTRACT', native_dispatch_authorized=False)
            if verdict['status'] != 'SATISFIED_AT_DECLARED_RESULT_CONTRACT':
                return verdict
            if consumer in valid:
                return dict(verdict, completion_digest=valid[consumer]['digest'], replay=True)
            _require(frontier['states'][consumer] == 'READY', 'JOIN retains source or custody holds')
            _require(consumer in frontier['selected'], 'JOIN deferred by shared selection')
            result = dict(schema='implementaudit.work-result.v1', node=consumer,
                          dispatch_id=frontier['dispatch_id'], graph_digest=frontier['graph_digest'],
                          input_digest=frontier['inputs'][consumer], status='PASS', terminal=True,
                          exit_code=0, evidence_digest=_hash(verdict), independence_key='required-join-' + consumer,
                          scope=[consumer])
            future = node['future_consumer']
            record = dict(node=consumer, status='PASS', consumer=future['node'] if future else None,
                          source_graph=copy.deepcopy(graph), result=result,
                          predecessors={name: valid.get(name, {}).get('digest') for name in node['requires'] + node['optional']})
            record['digest'] = _hash(record)
        self.journal.append('JOIN', dict(records=[record]), expected_old)
        self._live[consumer] = record
        return dict(verdict, completion_digest=record['digest'], replay=False)


def observe_fixed_native_completion(run_root, repo_root, *, input_root=None):
    """Observe the existing singleton receiver; never generalize its authority."""
    owner = _Compiler()
    with owner.module.observe_native_run_episode_sources_v2(run_root, repo_root,
                                                            input_root=input_root) as raw:
        value = owner.module.decode_strict_json_bytes(raw, 'native completion observation')
    owner.check()
    episode = value['ordinary_episode']
    if episode is None or episode['status'] != 'AVAILABLE':
        return dict(status='PRODUCER_UNAVAILABLE', observation=value, authority='NONE',
                    native_dispatch_authorized=False, completions=[])
    policy = episode['custody']['policy']
    receiving = episode['receiving']
    result, joined = receiving['result'], receiving['join']
    _require(result['node'] == policy['receiver_node'] and result['scope'] == [policy['receiver_node']]
             and receiving['dispatch']['selected'] == [policy['receiver_node']]
             and joined['consumer'] == policy['consumer'] and joined['required'] == [policy['receiver_node']]
             and joined['optional'] == [] and joined['lifecycle_credit'] == 'NONE',
             'fixed native producer scope cannot be expanded')
    return dict(status='FIXED_RECEIVING_OBSERVATION_ONLY', observation=value,
                authority='NONE', native_dispatch_authorized=False, completions=[])
