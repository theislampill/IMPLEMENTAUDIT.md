"""Bounded stdio transport over a process already held by the source owner."""
import copy
import hashlib
import json
import math
import queue
import subprocess
import threading
import time


MAX_FRAME = 256 * 1024
MAX_WIRE_PREFIX = 2 * 1024 * 1024


def _unique_fields(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate native field")
        result[key] = value
    return result


def _invalid_constant(_value):
    raise ValueError("nonfinite native value")


class OwnedStdioLoop:
    """The sole sender and reader. The existing ledger owns protocol admission."""

    def __init__(self, process, source_owner, *, emit, mode, selected_thread_id=None, native_module=None):
        if (type(process) is not subprocess.Popen or process.poll() is not None
                or process.stdin is None or process.stdout is None
                or process.stdin.closed or process.stdout.closed or process.text_mode
                or mode != "strict" or native_module is not None or not callable(emit)):
            raise ValueError("strict live owner pipes required")
        self.process, self.source_owner, self.emit = process, source_owner, emit
        self._input, self._output = process.stdin, process.stdout
        self.messages = queue.Queue(maxsize=1)
        self.ledger = source_owner.OwnedStdioQuiescenceV1(
            self.messages, selected_thread_id=selected_thread_id, native_process=process)
        self._state_lock = threading.RLock()
        self._condition = threading.Condition(self._state_lock)
        self._arm_lock = threading.RLock()
        self._send_lock = threading.Lock()
        self._outgoing = queue.Queue(maxsize=1)
        self._failure = None
        self._closing = False
        self._inbound = False
        self._raw_epoch = 0
        self._wire = hashlib.sha256()
        self._wire_bytes = 0
        self._ordinal = 0
        self._request_id = 0
        self._request = None
        self._reply = None
        self._written = False
        self._actual_initialize = None
        self._actual_initialized = None
        self._actual_start = None
        self._actual_resume = None
        self._actual_read = None
        self._live_producer = None
        self._retired_intervals = []
        self._transfer_stage = "CAPTURE"
        self.native_state = None
        self._usage_binding = None
        self._reader = threading.Thread(target=self._receive, daemon=True)
        self._writer = threading.Thread(target=self._send, daemon=True)
        self._reader.start()
        self._writer.start()

    @staticmethod
    def _budget(deadline):
        if type(deadline) not in (int, float) or not math.isfinite(deadline):
            raise ValueError("fixed monotonic deadline required")
        remaining = deadline - time.monotonic()
        if not 0 < remaining <= 30:
            raise TimeoutError("owned stdio deadline unavailable")
        return remaining

    def _check(self):
        if (self._failure is not None or self._closing or self.process.poll() is not None
                or self.process.stdin is not self._input or self.process.stdout is not self._output
                or self._input.closed or self._output.closed):
            raise ValueError("owned stdio process, pipes or interval unavailable")

    def _record_failure(self, error):
        with self._condition:
            if self._failure is None:
                self._failure = error
                try:
                    self.ledger.disconnect()
                except self.source_owner.QuiescenceRefusal:
                    pass
                finally:
                    try:
                        if self._live_producer is not None:
                            self._live_producer.cancel_now()
                    finally:
                        self._condition.notify_all()

    def _receive(self):
        try:
            while first := self._output.read(1):
                with self._condition:
                    self._check()
                    self._inbound = True
                    self._raw_epoch += 1
                    with self.ledger._lock:
                        self.ledger._fence = None
                        self.ledger._poison_all()
                raw = first + (self._output.readline(MAX_FRAME) if first != b"\n" else b"")
                if len(raw) > MAX_FRAME or not raw.endswith(b"\n"):
                    raise ValueError("native response frame exceeds its bound or is incomplete")
                message = json.loads(raw.decode("utf-8"), object_pairs_hook=_unique_fields,
                                     parse_constant=_invalid_constant)
                with self._condition:
                    self._check()
                    self._wire_bytes += len(raw)
                    if self._wire_bytes > MAX_WIRE_PREFIX:
                        raise ValueError("native response prefix exceeds its bound")
                    self._wire.update(raw)
                    self._ordinal += 1
                    self.ledger.after_record(message)
                    if "id" in message:
                        self._receive_reply(message, raw)
                    self._inbound = False
                    self._condition.notify_all()
            raise EOFError("owned native stdout closed")
        except Exception as error:
            self._record_failure(error)

    def _receive_reply(self, message, raw):
        if self._request is None or self._reply is not None or message["id"] != self._request["id"]:
            raise ValueError("native reply has no exact owned request")
        method, result = self._request["method"], message["result"]
        if method == "initialize":
            self._actual_initialize = {"sent": self._request, "reply": message}
        elif method == "thread/start":
            self._actual_start = (copy.deepcopy(self._request["params"]), result, hashlib.sha256(raw).hexdigest())
        elif method == "thread/resume":
            self._actual_resume = result
            if self._transfer_stage == "SELECTED_NEEDS_RESUME":
                self._transfer_stage = "SELECTED_RESUMED"
            elif self._transfer_stage == "FRESH_NEEDS_RESUME":
                self._transfer_stage = "FRESH_RESUMED"
        elif method == "thread/read":
            self._actual_read = (result, hashlib.sha256(raw).hexdigest(), self._ordinal, self._raw_epoch)
        self._reply = result

    def _send(self):
        try:
            while (raw := self._outgoing.get()) is not None:
                with self._condition:
                    self._check()
                if self._input.write(raw) != len(raw):
                    raise OSError("native frame write was incomplete")
                self._input.flush()
                with self._condition:
                    self._written = True
                    self._condition.notify_all()
        except Exception as error:
            self._record_failure(error)

    def _exchange(self, method, params, deadline, reply):
        if not self._send_lock.acquire(timeout=self._budget(deadline)):
            raise TimeoutError("owned stdio sender is already occupied")
        try:
            with self._condition:
                self._check()
                self._budget(deadline)
                request = {"method": method}
                if reply:
                    self._request_id += 1
                    request.update(id=self._request_id, params=copy.deepcopy(params))
                elif method != "initialized" or params:
                    raise ValueError("only the initialization notification is supported")
                raw = (json.dumps(request, separators=(",", ":"), allow_nan=False) + "\n").encode()
                if len(raw) > MAX_FRAME:
                    raise ValueError("native request exceeds its bound")
                self.ledger.before_send(request)
                self._request, self._reply, self._written = request, None, False
                self._outgoing.put_nowait(raw)
                while not self._written or reply and self._reply is None:
                    self._condition.wait(self._budget(deadline))
                    self._check()
                self._budget(deadline)
                if not reply:
                    self._actual_initialized = request
                result = copy.deepcopy(self._reply)
                self._request, self._reply = None, None
                return result
        except Exception as error:
            self._record_failure(error)
            raise
        finally:
            self._send_lock.release()

    def call(self, method, params, deadline):
        return self._exchange(method, params, deadline, reply=True)

    def notify(self, method, params, deadline):
        self._exchange(method, params, deadline, reply=False)

    def wait_terminal(self, turn_id, deadline):
        if not isinstance(turn_id, str) or not turn_id:
            raise ValueError("an actual turn identity is required")
        with self._condition:
            self._check()
            try:
                while self.ledger._last_completed != turn_id:
                    self._condition.wait(self._budget(deadline))
                    self._check()
                self._budget(deadline)
            except Exception as error:
                self._record_failure(error)
                raise

    def _assert_interval_transferable(self):
        self._check()
        if (self._inbound or self._request is not None or self.ledger._pending
                or self.ledger._turns or self.ledger._items or not self.messages.empty()):
            raise ValueError("owned interval has outstanding transport work")

    def live_acquisition_facts_v1(self):
        with self._state_lock:
            self._assert_interval_transferable()
            if self._actual_start is None or self._actual_read is None:
                raise ValueError("actual thread start and closing read required")
            params, started, start_hash = self._actual_start
            read, read_hash, ordinal, epoch = self._actual_read
            thread = started["thread"]
            source = thread.get("path")
            if (not isinstance(source, str) or not source or epoch != self._raw_epoch
                    or read["thread"].get("path") != source or read["thread"]["id"] != thread["id"]):
                raise ValueError("closing native source changed or is unavailable")
            return {"thread_id": thread["id"], "source_path": source, "thread_start": copy.deepcopy(params),
                    "effective_config": {key: copy.deepcopy(value) for key, value in started.items()
                                         if key != "thread"},
                    "thread_start_response_sha256": start_hash, "thread_read_response_sha256": read_hash,
                    "read_frame_ordinal": ordinal, "wire_prefix_sha256": self._wire.hexdigest(),
                    "wire_prefix_bytes": self._wire_bytes}

    def close(self, deadline):
        cancellation_error = None
        with self._condition:
            try:
                self._record_failure(ValueError("owned stdio interval closed"))
            except Exception as error:
                cancellation_error = error
            finally:
                self._closing = True
        if self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(min(2, self._budget(deadline) / 2))
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait(self._budget(deadline))
        try:
            self._outgoing.put_nowait(None)
        except queue.Full:
            pass
        for thread in (self._reader, self._writer):
            thread.join(self._budget(deadline))
            if thread.is_alive():
                raise TimeoutError("owned stdio worker did not stop")
        self._input.close()
        self._output.close()
        if cancellation_error is not None:
            raise cancellation_error
