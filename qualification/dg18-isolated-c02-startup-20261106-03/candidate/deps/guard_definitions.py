# Inert exact pinned-source AST definitions; no production module imported.
class QuiescenceRefusal(ValueError):
    pass

class OwnedStdioQuiescenceV1:

    def __init__(self, existing_queue, *, selected_thread_id=None, native_process=None):
        if type(existing_queue) is not queue.Queue:
            raise QuiescenceRefusal('EXISTING_OWNER_QUEUE_REQUIRED')
        self.queue = existing_queue
        self.native_process = native_process
        self._selected_thread_id = selected_thread_id
        self._lock = threading.RLock()
        self._pending, self._seen_ids = ({}, set())
        self._turns, self._items, self._completed = (set(), {}, set())
        self._mcp, self._remote_seen = ({}, False)
        self._lifecycle = False
        self._lifecycle_validator = None
        self._compaction_expected = 0
        self._children = set()
        self._revision = 0
        self._initialized = False
        self._notified = False
        self._thread = None
        self._announced_thread = None
        self._last_completed = None
        self._fence = None
        self._failure = None
        self._reservations = []

    def _deny(self, reason):
        self._failure = reason
        raise QuiescenceRefusal(reason)

    def _poison_all(self):
        errors = []
        for reservation in tuple(self._reservations):
            try:
                reservation.cancel_now()
            except BaseException as exc:
                errors.append(exc)
        self._fence = None
        if errors:
            self._failure = 'OWNER_CANCELLATION_FAILED'
            raise errors[0]

    def before_send(self, message):
        with self._lock:
            self._poison_all()
            if self._failure and (not (self._lifecycle and self._failure == 'NONACCEPTING_LIFECYCLE_INTERVAL')):
                self._deny(self._failure)
            if type(message) is not dict or type(message.get('method')) is not str:
                self._deny('UNKNOWN_OWNER_REQUEST')
            method = message['method']
            if method == 'initialized' and 'id' not in message:
                if not self._initialized or self._notified:
                    self._deny('INITIALIZATION_ORDER')
                self._notified = True
                return
            identity = message.get('id')
            if type(identity) not in (str, int):
                self._deny('DUPLICATE_OR_UNKNOWN_REQUEST_ID')
            identity_key = (type(identity), identity)
            if identity_key in self._seen_ids:
                self._deny('DUPLICATE_OR_UNKNOWN_REQUEST_ID')
            if method not in {'initialize', 'thread/start', 'thread/resume', 'turn/start', 'thread/read'} | ({'thread/compact/start'} if self._lifecycle else set()):
                self._deny('REQUEST_OUTSIDE_CONSERVATIVE_PROFILE')
            if method == 'initialize':
                if self._initialized or self._pending or self._seen_ids:
                    self._deny('INITIALIZATION_ORDER')
            elif not self._notified:
                self._deny('REQUEST_BEFORE_INITIALIZATION')
            params = message.get('params', {})
            if type(params) is not dict:
                self._deny('REQUEST_PARAMS_SHAPE')
            if method in {'thread/start', 'thread/resume'} and (self._thread is not None or any((value in {'thread/start', 'thread/resume'} for value in self._pending.values()))):
                self._deny('SECOND_SESSION_OR_THREAD_NOT_ADMITTED')
            if method == 'thread/resume' and (not self._selected_thread_id or params.get('threadId') != self._selected_thread_id):
                self._deny('UNSELECTED_NATIVE_RESUME')
            if method == 'turn/start' and (self._turns or 'turn/start' in self._pending.values()):
                self._deny('OVERLAPPING_TURN_NOT_ADMITTED')
            if method == 'thread/compact/start':
                if self._compaction_expected or self._turns or self._items:
                    self._deny('COMPACTION_WITH_OUTSTANDING_WORK')
                self._compaction_expected = 1
            if method in {'turn/start', 'thread/read', 'thread/compact/start'} and (self._thread is None or params.get('threadId') != self._thread):
                self._deny('FOREIGN_REQUEST_SCOPE')
            self._seen_ids.add(identity_key)
            self._pending[identity_key] = method

    def send_failed(self):
        with self._lock:
            self._poison_all()
            self._deny('OUTGOING_EFFECT_UNKNOWN')

    def after_record(self, message):
        with self._lock:
            self._poison_all()
            self._revision += 1
            if self._failure and (not (self._lifecycle and self._failure == 'NONACCEPTING_LIFECYCLE_INTERVAL')):
                self._deny(self._failure)
            if type(message) is not dict:
                self._deny('UNKNOWN_NATIVE_RECORD')
            if 'id' in message:
                if set(message) != {'id', 'result'}:
                    self._deny('UNKNOWN_NATIVE_RESPONSE_ENVELOPE')
                if 'method' in message:
                    self._deny('NATIVE_SERVER_REQUEST_NOT_ADMITTED')
                identity = message['id']
                if type(identity) not in (str, int):
                    self._deny('NATIVE_RESPONSE_ID_TYPE')
                identity_key = (type(identity), identity)
                if identity_key not in self._pending or 'error' in message or 'result' not in message:
                    self._deny('UNKNOWN_DUPLICATE_OR_FAILED_RESPONSE')
                method = self._pending.pop(identity_key)
                result = message['result']
                if type(result) is not dict:
                    self._deny('RESPONSE_SHAPE')
                if method == 'initialize':
                    self._initialized = True
                elif method in {'thread/start', 'thread/resume'}:
                    thread = result.get('thread', {}).get('id')
                    if not isinstance(thread, str) or not thread or (self._announced_thread and thread != self._announced_thread):
                        self._deny('THREAD_CREATION_SCOPE')
                    self._thread = thread
                    if self._selected_thread_id and thread != self._selected_thread_id:
                        self._deny('SELECTED_THREAD_RESPONSE_CHANGED')
                elif method == 'turn/start':
                    turn = result.get('turn', {}).get('id')
                    if not isinstance(turn, str) or not turn:
                        self._deny('TURN_CREATION_SCOPE')
                    if turn not in self._completed:
                        self._turns.add(turn)
                elif method == 'thread/read':
                    if result.get('thread', {}).get('id') != self._thread:
                        self._deny('READ_FENCE_SCOPE')
                    if not self._pending and (not self._turns) and (not self._items) and self._last_completed and all((v == 'ready' for v in self._mcp.values())):
                        self._fence = self._revision
                return
            self._notification(message)

    def _notification(self, message):

        def need(ok, reason='UNKNOWN_NATIVE_NOTIFICATION_SHAPE'):
            if not ok:
                self._deny(reason)
        need(set(message) in ({'method', 'params'}, {'method', 'params', 'emittedAtMs'}))
        need('emittedAtMs' not in message or (type(message['emittedAtMs']) is int and 0 <= message['emittedAtMs'] < 2 ** 63))
        method, p = (message['method'], message['params'])
        need(type(method) is str and type(p) is dict)
        if method == 'remoteControl/status/changed':
            need(set(p) <= {'installationId', 'serverName', 'status', 'environmentId'} and {'installationId', 'serverName', 'status'} <= set(p) and (not self._remote_seen) and (p['status'] == 'disabled') and (p.get('environmentId') is None) and all((type(p[k]) is str and p[k] for k in ('installationId', 'serverName'))))
            self._remote_seen = True
            return
        if method == 'account/rateLimits/updated':
            need(set(p) == {'rateLimits'} and type(p['rateLimits']) is dict and (set(p['rateLimits']) <= {'credits', 'individualLimit', 'limitId', 'limitName', 'planType', 'primary', 'secondary', 'rateLimitReachedType', 'spendControlReached'}))
            return
        if method == 'thread/started':
            need(set(p) == {'thread'} and type(p['thread']) is dict)
            identity = p['thread'].get('id')
            need(type(identity) is str and identity and (not self._announced_thread) and (not self._thread or identity == self._thread) and (not self._selected_thread_id or identity == self._selected_thread_id), 'UNEXPECTED_NATIVE_THREAD')
            self._announced_thread = identity
            return
        need(self._thread is not None and p.get('threadId') == self._thread, 'FOREIGN_OR_UNKNOWN_NATIVE_SCOPE')
        if method == 'mcpServer/startupStatus/updated':
            need({'threadId', 'name', 'status'} <= set(p) <= {'threadId', 'name', 'status', 'error', 'failureReason'} and type(p['name']) is str and p['name'] and (p.get('error') is None) and (p.get('failureReason') is None))
            name, status = (p['name'], p['status'])
            need(status == 'starting' and name not in self._mcp or (status == 'ready' and self._mcp.get(name) == 'starting'), 'MCP_STARTUP_NOT_SETTLED')
            self._mcp[name] = status
        elif method == 'thread/goal/cleared':
            need(set(p) == {'threadId'} and (not self._turns) and (not self._last_completed))
        elif method == 'thread/status/changed':
            need(set(p) == {'threadId', 'status'} and p['status'] in ({'type': 'idle'}, {'type': 'active', 'activeFlags': []}))
            need(p['status']['type'] != 'active' or self._turns or 'turn/start' in self._pending.values() or self._compaction_expected)
        elif method in {'turn/started', 'turn/completed'}:
            need(set(p) == {'threadId', 'turn'} and type(p['turn']) is dict)
            turn = p['turn']
            identity = turn.get('id')
            need(type(identity) is str and identity and (set(turn) <= {'id', 'status', 'items', 'itemsView', 'startedAt', 'completedAt', 'durationMs', 'error'}))
            if method == 'turn/started':
                need(identity not in self._completed and (identity in self._turns or 'turn/start' in self._pending.values() or self._compaction_expected == 1), 'UNREQUESTED_NATIVE_TURN')
                self._turns.add(identity)
                self._compaction_expected = 0
            else:
                need(identity in self._turns and turn.get('status') == 'completed' and (not self._items), 'TURN_TERMINAL_WITH_PENDING_OR_UNKNOWN_WORK')
                self._turns.remove(identity)
                self._completed.add(identity)
                self._last_completed = identity
        else:
            need(p.get('turnId') in self._turns, 'FOREIGN_OR_INACTIVE_NATIVE_TURN')
            if method in {'item/started', 'item/completed'}:
                clock = 'startedAtMs' if method == 'item/started' else 'completedAtMs'
                need({'threadId', 'turnId', 'item'} <= set(p) <= {'threadId', 'turnId', 'item', clock} and (clock not in p or (type(p[clock]) is int and p[clock] >= 0)) and (type(p['item']) is dict))
                item = p['item']
                identity = item.get('id')
                kind = item.get('type')
                need(type(kind) is str and kind in {'userMessage', 'agentMessage', 'reasoning'} | ({'commandExecution', 'mcpToolCall', 'dynamicToolCall', 'collabAgentToolCall', 'contextCompaction'} if self._lifecycle else set()) and (type(identity) is str) and identity, 'TOOLS_OR_UNKNOWN_ITEM_NOT_ADMITTED')
                if kind not in {'userMessage', 'agentMessage', 'reasoning'}:
                    need(callable(self._lifecycle_validator), 'PINNED_LIFECYCLE_VALIDATOR_REQUIRED')
                    self._lifecycle_validator(self, item, method == 'item/completed')
                if method == 'item/started':
                    need(identity not in self._items, 'DUPLICATE_ITEM')
                    self._items[identity] = kind
                else:
                    need(self._items.get(identity) == kind, 'UNKNOWN_ITEM_COMPLETION')
                    if kind == 'collabAgentToolCall':
                        self._children.update(item['receiverThreadIds'])
                    del self._items[identity]
            elif method == 'item/agentMessage/delta':
                need(set(p) == {'threadId', 'turnId', 'itemId', 'delta'} and type(p['delta']) is str and (self._items.get(p['itemId']) == 'agentMessage'), 'UNKNOWN_DELTA_ITEM')
            elif method == 'rawResponseItem/completed':
                need(set(p) == {'threadId', 'turnId', 'item'} and type(p['item']) is dict)
                item = p['item']
                if self._lifecycle and item.get('type') in {'function_call', 'function_call_output', 'custom_tool_call', 'custom_tool_call_output', 'reasoning'}:
                    need(callable(self._lifecycle_validator), 'PINNED_LIFECYCLE_VALIDATOR_REQUIRED')
                    self._lifecycle_validator(self, item, True, raw=True)
                    return
                need({'type', 'id', 'role', 'content'} <= set(item) <= {'type', 'id', 'role', 'content', 'internal_chat_message_metadata_passthrough', 'phase'} and item['type'] == 'message' and (type(item['id']) is str) and (item['role'] in {'system', 'developer', 'user', 'assistant'}) and (type(item['content']) is list) and ('phase' not in item or item['phase'] in {None, 'commentary', 'final_answer'}), 'RAW_TOOLS_OR_UNKNOWN_ITEM')
            elif self._lifecycle and method in {'item/commandExecution/outputDelta', 'item/reasoning/textDelta', 'item/reasoning/summaryTextDelta', 'item/reasoning/summaryPartAdded'}:
                need(p.get('itemId') in self._items and set(p) <= {'threadId', 'turnId', 'itemId', 'delta', 'contentIndex', 'summaryIndex'})
            elif method == 'rawResponse/completed':
                need({'threadId', 'turnId', 'responseId', 'usage'} <= set(p) <= {'threadId', 'turnId', 'responseId', 'usage', 'usageMetadata'} and type(p['usage']) is dict and (type(p['responseId']) is str) and ('usageMetadata' not in p or type(p['usageMetadata']) is dict))
            elif method == 'thread/tokenUsage/updated':
                need(set(p) == {'threadId', 'turnId', 'tokenUsage'} and type(p['tokenUsage']) is dict)
            elif method == 'turn/moderationMetadata':
                need(set(p) == {'threadId', 'turnId', 'metadata'} and type(p['metadata']) is dict)
            else:
                self._deny('UNKNOWN_NATIVE_EVENT_REQUIRES_PROFILE_REVIEW')

    def ingest(self, message):
        with self._lock:
            self.after_record(message)
            try:
                self.queue.put_nowait(message)
            except queue.Full:
                self._deny('OWNED_QUEUE_REJECTED_INGRESS')

    def disconnect(self):
        with self._lock:
            self._poison_all()
            self._deny('NATIVE_INGRESS_CLOSED_OR_UNKNOWN')

    def acquire(self, *reservations):
        with self._lock:
            if self._failure or not self._initialized or (not self._notified) or (not self._thread) or self._pending or self._turns or self._items or (not self._last_completed) or (self._fence != self._revision) or (not self.queue.empty()):
                raise QuiescenceRefusal('NO_COMPLETE_CURRENT_OWNER_QUIESCENCE_FENCE')
            if any((not callable(getattr(value, 'cancel_now', None)) for value in reservations)):
                raise QuiescenceRefusal('MISSING_IMMEDIATE_CANCELLATION')
            self._reservations.extend(reservations)
            return _OwnedQuiescenceReceipt(self, self._revision, self._thread, self._last_completed)

class FreshCanaryQuiescenceV1(OwnedStdioQuiescenceV1):
    """Closed current-native wire dialect; receives the actual owned pipe."""

    def __init__(self, existing_queue, *, selected_thread_id=None, native_process=None):
        super().__init__(existing_queue, selected_thread_id=selected_thread_id, native_process=native_process)
        self._hooks = {}
        self._early_mcp = []
        self._lifecycle = True
        self._lifecycle_validator = self._only_compaction
        self._usage = None
        self._rotation_records = []

    def after_record(self, message):
        with self._lock:
            super().after_record(message)
            if self._thread is not None and self._early_mcp:
                pending, self._early_mcp = (self._early_mcp, [])
                for notification in pending:
                    if notification['params']['threadId'] != self._thread:
                        self._deny('FRESH_CANARY_EARLY_MCP_SCOPE_MISMATCH')
                    self._notification(notification)

    def _only_compaction(self, ledger, item, completed, raw=False):
        if raw or set(item) != {'type', 'id', 'startedAtMs', 'completedAtMs'} or item.get('type') != 'contextCompaction' or (type(item['startedAtMs']) is not int) or (item['startedAtMs'] < 0) or (completed and (type(item['completedAtMs']) is not int or item['completedAtMs'] < item['startedAtMs'])) or (not completed and item['completedAtMs'] is not None):
            self._deny('FRESH_CANARY_TOOL_OR_RESULT_AUTHORITY_NOT_ADMITTED')

    def _notification(self, message):
        import copy

        def need(ok, reason='FRESH_CANARY_UNKNOWN_WIRE_SHAPE'):
            if not ok:
                self._deny(reason)
        need(type(message) is dict and set(message) in ({'method', 'params'}, {'method', 'params', 'emittedAtMs'}))
        need('emittedAtMs' not in message or (type(message['emittedAtMs']) is int and 0 <= message['emittedAtMs'] < 2 ** 63))
        method, p = (message.get('method'), message.get('params'))
        need(type(method) is str and type(p) is dict)
        if method == 'mcpServer/startupStatus/updated' and self._thread is None:
            need(sum((v in {'thread/start', 'thread/resume'} for v in self._pending.values())) == 1 and len(self._early_mcp) < 16 and (type(p.get('threadId')) is str) and (re.fullmatch('[0-9a-f-]{36}', p['threadId']) is not None), 'FRESH_CANARY_UNSOLICITED_EARLY_MCP')
            if self._early_mcp:
                need(p['threadId'] == self._early_mcp[0]['params']['threadId'], 'FRESH_CANARY_EARLY_MCP_SCOPE_MISMATCH')
            self._early_mcp.append(copy.deepcopy(message))
            return
        if method == 'deprecationNotice':
            need(p == {'summary': 'Full-history hydration is deprecated for paginated threads; omit `includeTurns` or set it to `false`, then page with `thread/turns/list` and `thread/items/list`.', 'details': None})
            return
        if method == 'warning':
            need(set(p) == {'threadId', 'message'} and p['threadId'] == self._thread and (p['message'] == 'Model metadata for `dg18-emulated-model` not found. Defaulting to fallback metadata; this can degrade performance and cause issues.'))
            return
        if method in {'hook/started', 'hook/completed'}:
            need(set(p) == {'threadId', 'turnId', 'run'} and p['threadId'] == self._thread and (p['turnId'] in self._turns))
            run = p['run']
            keys = {'id', 'eventName', 'handlerType', 'executionMode', 'scope', 'sourcePath', 'source', 'displayOrder', 'status', 'statusMessage', 'startedAt', 'completedAt', 'durationMs', 'entries'}
            need(type(run) is dict and set(run) == keys and (run['id'] == 'stop:1:/etc/codex/config.toml') and (run['eventName'] == 'stop') and (run['handlerType'] == 'mcpTool') and (run['executionMode'] == 'sync') and (run['scope'] == 'turn') and (run['sourcePath'] == '/etc/codex/config.toml') and (run['source'] == 'system') and (run['displayOrder'] == 1) and (run['statusMessage'] is None) and (type(run['startedAt']) is int))
            key = (p['turnId'], run['id'])
            if method == 'hook/started':
                need(key not in self._hooks and run['status'] == 'running' and (run['completedAt'] is None) and (run['durationMs'] is None) and (run['entries'] == []))
                self._hooks[key] = run['startedAt']
            else:
                need(self._hooks.get(key) == run['startedAt'] and run['status'] == 'completed' and (type(run['completedAt']) is int) and (run['completedAt'] >= run['startedAt']) and (type(run['durationMs']) is int) and (run['durationMs'] >= 0) and (run['entries'] == [{'kind': 'warning', 'text': 'DG17_LOCAL_MCP_CANARY_ACK'}]))
                del self._hooks[key]
            return
        if method == 'thread/readState/changed':
            need(set(p) == {'threadId', 'readState'} and p['threadId'] == self._thread)
            state = p['readState']
            need(type(state) is dict and set(state) == {'firstUnread', 'revision'} and (type(state['revision']) is str) and re.fullmatch('[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}', state['revision']))
            unread = state['firstUnread']
            need(type(unread) is dict and set(unread) == {'type', 'turnId'} and (unread['type'] == 'turn') and (unread['turnId'] in self._turns | self._completed))
            return
        normalized = copy.deepcopy(message)
        if method == 'rawResponseItem/completed':
            item = normalized['params'].get('item')
            need(type(item) is dict)
            if 'status' in item:
                need(item.get('type') == 'message' and item.get('role') == 'assistant' and (item['status'] == 'completed'), 'FRESH_CANARY_RAW_ITEM_STATUS')
                item.pop('status')
        if method == 'account/rateLimits/updated':
            limits = normalized['params'].get('rateLimits')
            need(type(limits) is dict and limits.get('normalModelSlug') is None)
            limits.pop('normalModelSlug', None)
        if method in {'turn/started', 'turn/completed'}:
            turn = normalized['params'].get('turn')
            need(type(turn) is dict and turn.get('rootTurnId') == turn.get('id'))
            turn.pop('rootTurnId')
            if method == 'turn/completed':
                need(not self._hooks, 'FRESH_CANARY_PENDING_HOOK')
        super()._notification(normalized)
        if method == 'thread/tokenUsage/updated':
            self._usage = copy.deepcopy(p)
        if method in {'rawResponse/completed', 'thread/tokenUsage/updated', 'turn/completed'}:
            import time
            self._rotation_records.append({'message': copy.deepcopy(message), 'received_at_unix_ms': time.time_ns() // 1000000, 'received_monotonic_ns': time.monotonic_ns(), 'stream_revision': self._revision})
            if len(self._rotation_records) > 64:
                self._rotation_records = self._rotation_records[-64:]

    def acquire(self, *reservations):
        with self._lock:
            if self._hooks:
                raise QuiescenceRefusal('FRESH_CANARY_PENDING_HOOK')
            return super().acquire(*reservations)
