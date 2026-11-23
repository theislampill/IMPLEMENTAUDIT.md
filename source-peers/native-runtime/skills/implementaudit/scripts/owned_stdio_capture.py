"""Owner-selected C02 capture over one bounded Windows app-server process."""

import contextlib
import hashlib
import os
from pathlib import Path
import re
import subprocess
import threading
import time


C02_CAPTURE_GRANT_PIN = None
NATIVE_IMAGE_SHA256 = "444a3f0008050605cae73cd9b7a2dcac61294062dfaab56dd20430fd6498518b"
MAX_CAPTURE_SECONDS = 600


def require(test, message):
    if not test:
        raise ValueError(message)


def _deadline(expires_at_ms, maximum_seconds):
    remaining = (expires_at_ms - time.time_ns() // 1_000_000) / 1000
    require(remaining > 0, "C02_CAPTURE_GRANT_EXPIRED")
    return time.monotonic() + min(remaining, maximum_seconds)


def _read_grant(owner, stack, context):
    pin = C02_CAPTURE_GRANT_PIN
    require(type(pin) is dict and set(pin) == {"path", "bytes", "sha256"}, "C02_CAPTURE_GRANT_UNSELECTED")
    path = Path(pin["path"])
    require(path.is_absolute() and path.resolve(strict=True) == path, "C02_CAPTURE_GRANT_ALIAS")
    held = owner.PinnedFile(path, max_bytes=64 * 1024)
    stack.callback(held.close)
    body = held.read()
    require(len(body) == pin["bytes"] and hashlib.sha256(body).hexdigest() == pin["sha256"],
            "C02_CAPTURE_GRANT_CHANGED")
    grant = owner.decode_json(body)
    fields = {"schema", "operation", "issuer", "effect", "subject", "candidate", "profile",
              "binary", "producer_pins", "expected_old", "receipt_token", "initialize", "thread_start",
              "turn", "maximum_elapsed_seconds", "expires_at_ms"}
    require(type(grant) is dict and set(grant) == fields
            and grant["schema"] == "implementaudit.c02-owned-stdio-capture-grant.v1"
            and grant["effect"] == "ONE_C02_TERMINAL_CAPTURE"
            and type(grant["operation"]) is str and re.fullmatch("[a-zA-Z0-9-]{1,80}", grant["operation"])
            and type(grant["issuer"]) is str and grant["issuer"]
            and type(grant["expires_at_ms"]) is int
            and type(grant["maximum_elapsed_seconds"]) is int
            and 0 < grant["maximum_elapsed_seconds"] <= MAX_CAPTURE_SECONDS,
            "C02_CAPTURE_GRANT_SCOPE")
    subject = {key: context[key] for key in ("controller", "claim_id", "run_root_identity")}
    require(grant["subject"] == dict(subject, repository=str(context["repo"])),
            "C02_CAPTURE_SUBJECT_CHANGED")
    require(owner.git(context["repo"], "rev-parse", "HEAD").decode().strip() == grant["candidate"],
            "C02_CAPTURE_CANDIDATE_CHANGED")
    require(owner.managed(context) == grant["expected_old"], "C02_CAPTURE_EXPECTED_OLD_CHANGED")
    joined = owner.require_current_generation_join_v1(context)
    require(joined["receipt_token"] == grant["receipt_token"]
            and joined["pointer_oid"] == grant["expected_old"]["pointer"]
            and joined["marker_oid"] == grant["expected_old"]["marker"],
            "C02_CAPTURE_CURRENT_PREIMAGE_CHANGED")
    require(type(grant["initialize"]) is dict and type(grant["thread_start"]) is dict
            and type(grant["turn"]) is dict and "threadId" not in grant["turn"],
            "C02_CAPTURE_RPC_SCOPE")
    thread_start = grant["thread_start"]
    require(thread_start.get("cwd") == str(context["repo"]) and thread_start.get("sandbox") == "read-only"
            and thread_start.get("approvalPolicy") == "never" and thread_start.get("experimentalRawEvents") is True,
            "C02_CAPTURE_FIXED_THREAD_POLICY")
    held.verify()
    return grant, held


class C02LiveCapture:
    def __init__(self, producer, owner, context, grant, held, end):
        self.producer, self.owner, self.context = producer, owner, context
        self._grant, self._held, self._end = grant, held, end
        self._turn_attempted = False

    def _check(self):
        self._held.verify()
        self.producer.check()
        require(self.owner.managed(self.context) == self._grant["expected_old"], "C02_CAPTURE_PREIMAGE_ADVANCED")
        require(time.monotonic() < self._end, "C02_CAPTURE_DEADLINE")
        return min(self._end, time.monotonic() + 30)

    def initialize(self):
        loop = self.producer.loop
        loop.call("initialize", self._grant["initialize"], self._check())
        loop.notify("initialized", {}, self._check())
        result = loop.call("thread/start", self._grant["thread_start"], self._check())
        thread = result["thread"]
        loop.call("thread/read", {"threadId": thread["id"], "includeTurns": False}, self._check())
        return loop.live_acquisition_facts_v1()

    @contextlib.contextmanager
    def terminal_interval(self, runtime, code_pins):
        """Run the fixed nominated turn on the original selected pipe, then hold it live."""
        source = self.producer.source_owner
        selected = runtime[0]
        require(not self._turn_attempted, "C02_CAPTURE_TURN_ALREADY_ATTEMPTED")
        self._check()
        require(source.OWNED_STDIO_SELECTION_PIN is not None and selected == source._np_selection()
                and selected["profile_id"] == source.OWNED_STDIO_PROFILE,
                "C02_CAPTURE_PROVIDER_UNSELECTED")
        scope = selected["c02_adjudication"]
        require(scope["issuer"] == self._grant["issuer"], "C02_CAPTURE_ISSUER_CHANGED")
        loop = self.producer.loop
        require(loop._transfer_stage == "OPEN_VERIFIED"
                and loop.ledger._thread == selected["root_thread_id"]
                and loop.process is self.producer.process, "C02_CAPTURE_ORIGINAL_SELECTED_OPEN_REQUIRED")
        self._turn_attempted = True
        thread_id = selected["root_thread_id"]
        result = loop.call("turn/start", dict(self._grant["turn"], threadId=thread_id), self._check())
        loop.wait_terminal(result["turn"]["id"], self._check())
        loop.call("thread/read", {"threadId": thread_id, "includeTurns": False}, self._check())
        with source.acquire_selected_c02_interval_v1(
                runtime, self.owner, self.context, loop.ledger, self.producer.process, code_pins) as interval:
            original_check = interval._source_check

            def verify_granted_interval():
                original_check()
                self._held.verify()
                require(time.monotonic() < self._end, "C02_CAPTURE_DEADLINE")

            interval._source_check = verify_granted_interval
            interval.verify()
            yield interval
            interval.verify()


@contextlib.contextmanager
def open_c02_capture_v1(owner, source_owner, context=None, *, emit):
    """Start only the exact approved child; no public CLI, argument or environment grant."""
    require(C02_CAPTURE_GRANT_PIN is not None, "C02_CAPTURE_GRANT_UNSELECTED")
    require(os.name == "nt", "C02_CAPTURE_REQUIRES_WINDOWS")
    with contextlib.ExitStack() as stack:
        grant, held = _read_grant(owner, stack, context)
        end = _deadline(grant["expires_at_ms"], grant["maximum_elapsed_seconds"])
        image = grant["binary"]
        require(type(image) is dict and set(image) == {"path", "bytes", "sha256"}
                and image["sha256"] == NATIVE_IMAGE_SHA256, "C02_CAPTURE_BINARY_PIN")
        executable = Path(image["path"])
        require(executable.is_absolute() and executable.resolve(strict=True) == executable,
                "C02_CAPTURE_BINARY_ALIAS")
        executable_handle = owner.PinnedFile(executable, max_bytes=512 * 1024 * 1024)
        stack.callback(executable_handle.close)
        require(executable.stat().st_size == image["bytes"]
                and owner.native_held_image_sha256_v1(executable_handle) == image["sha256"],
                "C02_CAPTURE_BINARY_CHANGED")
        profile = Path(grant["profile"])
        require(profile.is_absolute() and profile.resolve(strict=True) == profile and profile.is_dir()
                and profile.parent == context["repo"].parent and profile.name == "profile",
                "C02_CAPTURE_PROFILE_ALIAS")
        owner.safe_chain(profile)

        pins = grant["producer_pins"]
        require(type(pins) is dict and set(pins) == {"runner", "claim", "helper", "loop", "source_owner"},
                "C02_CAPTURE_DEPENDENCY_POPULATION")
        expected_paths = {"runner": Path(__file__), "claim": Path(owner.__file__),
                          "source_owner": Path(source_owner.__file__),
                          "helper": Path(source_owner.__file__).with_name("bounded_source_owner.py"),
                          "loop": Path(source_owner.__file__).with_name("owned_stdio_loop.py")}
        for name, path in expected_paths.items():
            require(Path(pins[name]["path"]) == path.absolute(), "C02_CAPTURE_DEPENDENCY_LOCATION")
            source_owner._np_read_pin(pins[name], 512 * 1024)
        helper = source_owner._np_module(pins["helper"], "bounded_source_owner.py")
        argv = [str(executable), "app-server", "--listen", "stdio://"]
        environment = {key: value for key, value in os.environ.items()
                       if key.casefold() in {"systemroot", "windir", "systemdrive", "comspec", "temp", "tmp"}}
        environment["CODEX_HOME"] = str(profile)
        held.verify()
        executable_handle.verify()
        require(time.monotonic() < end and owner.managed(context) == grant["expected_old"],
                "C02_CAPTURE_PRELAUNCH_SCOPE_CHANGED")
        attempt = profile / (".c02-start-" + grant["operation"])
        with attempt.open("xb") as receipt:
            receipt.write((grant["operation"] + "\n").encode("ascii"))
            receipt.flush()
            os.fsync(receipt.fileno())
        process = subprocess.Popen(argv, cwd=context["repo"], env=environment,
                                   stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                   stderr=subprocess.DEVNULL, creationflags=subprocess.CREATE_NO_WINDOW)
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
        watchdog.start()
        try:
            producer = helper.OwnedStdioLiveProducerV1(process, source_owner, owner, pins, emit=emit)
            require(producer.process_identity["image"] == str(executable), "C02_CAPTURE_LIVE_IMAGE_CHANGED")
            yield C02LiveCapture(producer, owner, context, grant, held, end)
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
