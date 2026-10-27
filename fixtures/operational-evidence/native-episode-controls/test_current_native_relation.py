"""SOURCE_ONLY relation and causal controls over constructed local records.

No retained native record, private provider selection, session, or child is used.
The only substituted boundary is native provider authentication: its fixture
reader is restricted to the exact constructed context, paths, and selectors and
then delegates to the real bounded byte reader. All relation, header, artifact,
message, identity, digest, and causal checks under test are production functions.
These controls confer no native qualification, lifecycle, or acceptance credit.
"""

import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

import native_test_support as support


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def stamp(milliseconds):
    seconds, fraction = divmod(milliseconds, 1000)
    return f"2026-01-01T00:00:{seconds:02d}.{fraction:03d}Z"


class SourceOnlyEpisode:
    """Complete small wire fixtures; literal times are independent test inputs."""

    DEFAULT_TIMES = {
        "spawn_call": 100, "activation": 200, "load_call": 300,
        "load_output": 400, "spawn_output": 500, "route": 600,
        "authorization": 700,
    }

    def __init__(self, directory, observation, *, profile=None,
                 version="0.164.0-alpha.11.1", times=None, fork="none",
                 spawn_task="source_only_child", reply_task="/root/source_only_child"):
        self.directory = directory
        directory.mkdir()
        self.observation = observation
        self.profile = profile or observation.NONPROTECTED_PROFILE
        self.times = dict(self.DEFAULT_TIMES, **(times or {}))
        self.context = {
            "profile_id": self.profile,
            "parent_identity": {"host_id": "codex", "thread_id": "source-only-root", "agent_path": "/root"},
            "actual_child_identity": {"host_id": "codex", "thread_id": "source-only-child", "agent_path": "/root/source_only_child"},
        }
        self.rows = {}
        self.locators = {}
        self.pins = {}

        skill_bytes = b"# SOURCE_ONLY inert skill fixture\nNo native execution.\n"
        skill_path = directory / "fixture-skill.md"
        skill_path.write_bytes(skill_bytes)
        self.skill_pin = {"path": str(skill_path), "bytes": len(skill_bytes), "sha256": sha(skill_bytes)}
        loaded = dict(self.skill_pin, utf8=skill_bytes.decode())
        nested_output = {
            "chunk_id": "source-only", "wall_time_seconds": 0, "exit_code": 0,
            "original_token_count": 1, "output": canonical(loaded).decode(),
        }
        child_rows = [
            self.row(0, 0, "session_meta", {
                "id": "source-only-child", "session_id": "source-only-root",
                "parent_thread_id": "source-only-root", "agent_path": "/root/source_only_child",
                "thread_source": "subagent", "cli_version": version,
                "forked_from_id": None, "subagent_history_start_ordinal": None,
            }),
            self.row(1, self.times["activation"], "event_msg", {"type": "task_started", "turn_id": "source-only-child-turn"}),
            self.row(2, self.times["load_call"], "response_item", {
                "type": "custom_tool_call", "call_id": "source-only-load", "name": "exec", "status": "completed",
                # Existing command serialization only supplies a valid inert
                # envelope; no command is executed and no timing expectation
                # is derived from this production helper.
                "input": observation.load_tool_input(self.skill_pin),
            }),
            self.row(3, self.times["load_output"], "response_item", {
                "type": "custom_tool_call_output", "call_id": "source-only-load",
                "output": [{"type": "input_text", "text": "SOURCE_ONLY constructed response"},
                           {"type": "input_text", "text": canonical(nested_output).decode()}],
            }),
        ]
        self.write_source("child", child_rows, ("header", "activation", "load_call", "load_output"))
        self.context["child"]["history_start_ordinal"] = 1
        load_identity = {name: self.pins["child"][key]
                         for name, key in (("call", "load_call"), ("result", "load_output"))}
        obligation = {
            "parent_identity": self.context["parent_identity"],
            "actual_child_identity": self.context["actual_child_identity"],
            "observation_id": "SOURCE_ONLY-observation",
        }
        obligation_bytes = canonical(obligation)
        obligation_path = directory / "obligation.json"
        obligation_path.write_bytes(obligation_bytes)
        self.prepared = {"obligation": obligation, "obligation_pin": {
            "path": str(obligation_path), "bytes": len(obligation_bytes), "sha256": sha(obligation_bytes)}}
        authorization_value = {
            "schema": "implementaudit.compaction-use-authorization.v1",
            "action": "AUTHORIZE_BOUNDED_POST_COMPACTION_RECONCILIATION",
            "parent_identity": obligation["parent_identity"],
            "actual_child_identity": obligation["actual_child_identity"],
            "obligation_digest": sha(obligation_bytes),
            "observation_id": "SOURCE_ONLY-observation",
            "load_observation_identity": sha(canonical(load_identity)),
            "selected_child": "audit-state", "skill_source_pin": self.skill_pin,
            "authority_ceiling": "NONE",
        }
        parent_rows = [
            self.row(0, 0, "session_meta", {"id": "source-only-root", "session_id": "source-only-root", "cli_version": "0.163.0-alpha.10.2"}),
            self.row(1, self.times["spawn_call"], "response_item", {
                "type": "function_call", "namespace": "collaboration", "name": "spawn_agent", "call_id": "source-only-spawn",
                "arguments": canonical({"task_name": spawn_task, "fork_turns": fork}).decode(),
            }),
            self.row(2, self.times["spawn_output"], "response_item", {
                "type": "function_call_output", "call_id": "source-only-spawn",
                "output": canonical({"task_name": reply_task}).decode(),
            }),
            self.message(3, self.times["route"], "source-only-route", "```ini\nCHILD_TASK=source_only_child\nCHILD_SKILL_ROUTE=audit-state\nLOAD=VERIFIED\n```"),
            self.message(4, self.times["authorization"], "source-only-authorization", "```json\n" + canonical(authorization_value).decode() + "\n```"),
        ]
        self.write_source("parent", parent_rows, ("header", "spawn_call", "spawn_output", "route", "authorization"))
        self.context.update(spawn_call=self.pins["parent"]["spawn_call"],
                            spawn_output=self.pins["parent"]["spawn_output"],
                            child_activation=self.pins["child"]["activation"])
        self.evidence = {
            "load_call": self.locators["child"]["load_call"],
            "load_output": self.locators["child"]["load_output"],
            "route": self.locators["parent"]["route"],
            "authorization": self.locators["parent"]["authorization"],
        }

    @staticmethod
    def row(ordinal, milliseconds, kind, payload):
        return {"timestamp": stamp(milliseconds), "ordinal": ordinal, "type": kind, "payload": payload}

    def message(self, ordinal, milliseconds, identifier, text):
        content = {"type": "output_text", "text": text}
        if self.profile == self.observation.NONPROTECTED_PROFILE:
            content.update(annotations=[], logprobs=[])
        row = self.row(ordinal, milliseconds, "response_item", {
            "type": "message", "id": identifier, "role": "assistant", "phase": "commentary", "content": [content]})
        if self.profile in (self.observation.NONPROTECTED_PROFILE, self.observation.CURRENT_BOUNDARY_PROFILE):
            row["metadata"] = {"client_authored": False, "retained_source": {
                "complete": True, "revision": "retained_11111111-1111-4111-8111-111111111111",
                "id": {"message_id": identifier, "role": "assistant", "turn_id": "22222222-2222-4222-8222-222222222222"}}}
        return row

    def write_source(self, role, rows, names):
        path = self.directory / (role + ".jsonl")
        pieces = [canonical(row) + b"\n" for row in rows]
        path.write_bytes(b"".join(pieces))
        info = path.stat()
        physical = {"device": info.st_dev, "inode": info.st_ino}
        offset = 0
        locators = {}
        pins = {}
        for index, (name, row, raw) in enumerate(zip(names, rows, pieces)):
            locator = {"offset": offset, "bytes": len(raw), "sha256": sha(raw), "embedded_ordinal": row["ordinal"], "physical_line": index + 1}
            locators[name] = locator
            pins[name] = {"path": str(path), "physical": physical, "role": role, "locator": locator,
                          "timestamp": row["timestamp"], "message_or_call_id": row["payload"].get("id", row["payload"].get("call_id"))}
            offset += len(raw)
        self.context[role] = {"path": str(path), "physical": physical, "metadata": locators["header"],
                              "metadata_payload_digest": sha(canonical(rows[0]["payload"])),
                              "allowed_ranges": [{"offset": 0, "bytes": offset}]}
        self.rows[role] = rows
        self.locators[role] = locators
        self.pins[role] = pins

    def fixture_read(self, context, role, selectors):
        if context is not self.context or role not in ("parent", "child"):
            raise AssertionError("fixture reader cannot authorize another context or role")
        source = context[role]
        if source["path"] != str(self.directory / (role + ".jsonl")):
            raise AssertionError("fixture reader cannot open another path")
        if any(selector not in self.locators[role].values() for selector in selectors):
            raise AssertionError("fixture reader cannot widen the selected rows")
        return self.observation.read_records(source["path"], selectors, source["allowed_ranges"], source["physical"])

    def reader_scope(self):
        return mock.patch.object(self.observation, "_nonprotected_read_records", self.fixture_read)

    def fresh(self):
        with self.reader_scope():
            return self.observation.fresh_child_boundary(self.context)

    def authorize(self):
        with self.reader_scope():
            return self.observation.authorization(self.context, self.prepared, self.evidence, self.skill_pin)


class CurrentNativeRelationControls(unittest.TestCase):
    """SOURCE_ONLY: generic relation/causal semantics, not writer qualification."""

    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="source-only-current-relation-", dir=support.SCRATCH)
        self.addCleanup(temporary.cleanup)
        self.directory = Path(temporary.name)
        self.observation = support.load("compaction-result-observation.py")
        self.owner = support.load("bounded_source_owner.py")
        self.case_number = 0

    def episode(self, **arguments):
        self.case_number += 1
        return SourceOnlyEpisode(self.directory / f"case-{self.case_number}", self.observation, **arguments)

    def relation(self, *, root_version="0.164.0-alpha.11.1", child_version="0.164.0-alpha.11.1"):
        selection = {"root_thread_id": "source-only-root", "cli_version": root_version,
                     "native_version": "codex-cli " + child_version, "cwd": str(self.directory)}
        root = {"id": "source-only-root", "sessionId": "source-only-root", "parentThreadId": None,
                "cliVersion": root_version, "cwd": str(self.directory), "ephemeral": False, "historyMode": "paginated"}
        child = dict(root, id="source-only-child", sessionId="source-only-child", parentThreadId="source-only-root",
                     cliVersion=child_version, source_kind="subAgent", threadSource="subagent")
        root_header = {"id": "source-only-root", "session_id": "source-only-root", "cli_version": root_version, "cwd": str(self.directory)}
        child_header = dict(root_header, id="source-only-child", cli_version=child_version,
                            parent_thread_id="source-only-root", thread_source="subagent", agent_path="/root/source_only_child")
        return selection, root, child, root_header, child_header

    def assert_owner_accepts(self, invoke, label):
        try:
            return invoke()
        except ValueError as error:
            self.fail(f"{label}: production owner refused a valid SOURCE_ONLY fixture: {error}")

    def test_relation_matches_each_entity_to_its_own_version(self):
        # Catches comparing a fresh child to its older root's creation version.
        values = self.relation(root_version="0.163.0-alpha.10.2")
        result = self.assert_owner_accepts(lambda: self.owner.validate_relation(*values), "mixed-version relation")
        self.assertEqual(result, "source-only-child")

    def test_same_version_relation_stays_valid(self):
        # Catches a repair that requires an upgrade instead of allowing one.
        self.assertEqual(self.owner.validate_relation(*self.relation()), "source-only-child")

    def test_relation_rejects_foreign_identity_and_parent(self):
        # Each case starts from a valid same-version pair, so another version
        # failure cannot mask removal of the identity guard being exercised.
        cases = ((1, "id", "foreign"), (1, "sessionId", "foreign"), (1, "parentThreadId", "foreign"),
                 (2, "id", "source-only-root"), (2, "sessionId", "foreign"), (2, "parentThreadId", "foreign"),
                 (2, "source_kind", "ordinary"), (2, "threadSource", "ordinary"),
                 (3, "id", "foreign"), (4, "session_id", "foreign"),
                 (4, "parent_thread_id", "foreign"), (4, "thread_source", "ordinary"), (4, "agent_path", "/foreign/task"))
        for index, key, value in cases:
            with self.subTest(record=index, field=key):
                values = self.relation()
                values[index][key] = value
                with self.assertRaises(ValueError):
                    self.owner.validate_relation(*values)

    def test_relation_rejects_native_header_version_and_cwd_drift(self):
        # Catches trusting either native response or header alone, including cwd.
        cases = ((1, "cliVersion", "wrong"), (2, "cliVersion", "wrong"),
                 (3, "cli_version", "wrong"), (4, "cli_version", "wrong"),
                 (1, "cwd", "/foreign"), (2, "cwd", "/foreign"),
                 (3, "cwd", "/foreign"), (4, "cwd", "/foreign"),
                 (1, "ephemeral", True), (2, "ephemeral", True),
                 (1, "historyMode", "ephemeral"), (2, "historyMode", "ephemeral"))
        for index, key, value in cases:
            with self.subTest(record=index, field=key):
                values = self.relation()
                values[index][key] = value
                with self.assertRaisesRegex(ValueError, "VERSION_QUALIFIED_HEADER_RELATION_CHANGED"):
                    self.owner.validate_relation(*values)

    def test_relation_rejects_unbound_or_malformed_running_version(self):
        # Catches falling back to root version when the running provider is not bound.
        for version in (None, "", 164, True, "0.164.0-alpha.11.1", "codex-cli", "codex-cli ",
                        "codex-cli 0.164.0-alpha.11.1 extra", "codex-cli 0.163.0-alpha.10.2"):
            with self.subTest(native_version=version):
                values = self.relation()
                if version is None:
                    del values[0]["native_version"]
                else:
                    values[0]["native_version"] = version
                with self.assertRaises(ValueError):
                    self.owner.validate_relation(*values)

    def test_fresh_boundary_admits_activation_during_spawn_rpc(self):
        # Catches the unjustified response-before-activation edge in the real entrypoint.
        episode = self.episode()
        result = self.assert_owner_accepts(episode.fresh, "activation during spawn RPC")
        self.assertEqual(result["actual_activation"]["timestamp"], "2026-01-01T00:00:00.200Z")
        self.assertEqual(result["actual_spawn_output"]["timestamp"], "2026-01-01T00:00:00.500Z")
        self.assertEqual(result["observed_fork_turns"], "none")
        self.assertEqual(result["authority_ceiling"], "NONE")

    def test_fresh_boundary_keeps_legacy_completed_rpc_order(self):
        episode = self.episode(version="0.163.0-alpha.10.2", times={"spawn_output": 150})
        result = episode.fresh()
        self.assertEqual(result["actual_activation"]["timestamp"], "2026-01-01T00:00:00.200Z")

    def test_fresh_boundary_rejects_reversed_or_equal_causal_edges(self):
        # Catches weakening call<activation or call<response, including equal clocks.
        for times in ({"activation": 50}, {"activation": 100}, {"spawn_output": 50}, {"spawn_output": 100}):
            with self.subTest(times=times):
                with self.assertRaisesRegex(ValueError, "OBSERVATION_ORDER"):
                    self.episode(times=times).fresh()

    def test_fresh_boundary_uses_actual_header_and_qualified_profile(self):
        # An asserted caller version must not promote an older header/profile.
        cases = ({"version": "0.163.0-alpha.10.2"},
                 {"version": "0.164.0-alpha.11.2"},
                 {"profile": self.observation.CURRENT_BOUNDARY_PROFILE},
                 {"profile": self.observation.OWNED_STDIO_PROFILE})
        for arguments in cases:
            with self.subTest(arguments=arguments):
                episode = self.episode(**arguments)
                episode.context["native_version"] = "codex-cli 0.164.0-alpha.11.1"
                episode.context["cli_version"] = "0.164.0-alpha.11.1"
                with self.assertRaisesRegex(ValueError, "OBSERVATION_ORDER"):
                    episode.fresh()

    def test_fresh_boundary_refuses_mutated_header_bytes_or_digest(self):
        # Catches making the new ordering branch depend on an unverified header.
        episode = self.episode()
        path = Path(episode.context["child"]["path"])
        path.write_bytes(path.read_bytes().replace(b"0.164.0-alpha.11.1", b"0.164.0-alpha.11.2", 1))
        with self.assertRaisesRegex(ValueError, "RECORD_PIN_CHANGED"):
            episode.fresh()
        episode = self.episode()
        episode.context["child"]["metadata_payload_digest"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "SOURCE_METADATA_CHANGED"):
            episode.fresh()

    def test_fresh_boundary_preserves_spawn_identity_and_freshness(self):
        for arguments, reason in (({"fork": "all"}, "CURRENT_FRESH_SPAWN_REQUIRED"),
                                  ({"spawn_task": "foreign"}, "ACTUAL_SPAWN_CHILD_IDENTITY"),
                                  ({"reply_task": "/root/foreign"}, "ACTUAL_SPAWN_CHILD_IDENTITY")):
            with self.subTest(arguments=arguments):
                with self.assertRaisesRegex(ValueError, reason):
                    self.episode(**arguments).fresh()

    def test_authorization_admits_load_during_spawn_rpc(self):
        # Catches the old response-before-LOAD requirement through the real
        # authorization entrypoint, full skill readback, and public message grammar.
        episode = self.episode()
        result = self.assert_owner_accepts(episode.authorize, "LOAD during spawn RPC")
        self.assertEqual(result["load_identity"]["call"]["timestamp"], "2026-01-01T00:00:00.300Z")
        self.assertEqual(result["load_identity"]["result"]["timestamp"], "2026-01-01T00:00:00.400Z")
        self.assertEqual(result["route_record"]["timestamp"], "2026-01-01T00:00:00.600Z")
        self.assertEqual(result["value"]["selected_child"], "audit-state")
        self.assertEqual(result["value"]["authority_ceiling"], "NONE")

    def test_authorization_keeps_legacy_load_after_reply(self):
        episode = self.episode(version="0.163.0-alpha.10.2", times={"spawn_output": 150})
        result = episode.authorize()
        self.assertEqual(result["load_identity"]["call"]["timestamp"], "2026-01-01T00:00:00.300Z")

    def test_authorization_rejects_route_before_reply_or_load_result(self):
        # These are separate prerequisites, not one combined maximum-time oracle.
        cases = ({"route": 450}, {"load_output": 650}, {"route": 500},
                 {"spawn_output": 150, "route": 400})
        for times in cases:
            with self.subTest(times=times):
                with self.assertRaisesRegex(ValueError, "OBSERVATION_ORDER"):
                    self.episode(times=times).authorize()

    def test_authorization_rejects_load_before_or_at_activation(self):
        for load_call in (150, 200):
            with self.subTest(load_call=load_call):
                with self.assertRaisesRegex(ValueError, "OBSERVATION_ORDER"):
                    self.episode(times={"load_call": load_call}).authorize()

    def test_authorization_keeps_strict_order_for_other_header_or_profile(self):
        cases = ({"version": "0.163.0-alpha.10.2"},
                 {"version": "0.164.0-alpha.11.2"},
                 {"profile": self.observation.CURRENT_BOUNDARY_PROFILE},
                 {"profile": self.observation.OWNED_STDIO_PROFILE})
        for arguments in cases:
            with self.subTest(arguments=arguments):
                with self.assertRaisesRegex(ValueError, "OBSERVATION_ORDER"):
                    self.episode(**arguments).authorize()

    def test_authorization_keeps_strict_load_call_result_order(self):
        for load_output in (250, 300):
            with self.subTest(load_output=load_output):
                with self.assertRaisesRegex(ValueError, "OBSERVATION_ORDER"):
                    self.episode(times={"load_output": load_output}).authorize()

    def test_before_remains_strict_across_sources_and_physical_intervals(self):
        # Catches a global <= change, timestamp-only same-source comparison,
        # or replacement of cross-source time with unrelated byte offsets.
        first = {"path": "/SOURCE_ONLY/one", "timestamp": stamp(100), "locator": {"offset": 100, "bytes": 20}}
        later_other = {"path": "/SOURCE_ONLY/two", "timestamp": stamp(200), "locator": {"offset": 0, "bytes": 10}}
        self.observation.before(first, later_other)
        for other_time in (50, 100):
            other = dict(later_other, timestamp=stamp(other_time))
            with self.subTest(other_time=other_time):
                with self.assertRaisesRegex(ValueError, "OBSERVATION_ORDER"):
                    self.observation.before(first, other)
        overlap = dict(later_other, path=first["path"], locator={"offset": 119, "bytes": 10})
        with self.assertRaisesRegex(ValueError, "SOURCE_RECORD_ORDER"):
            self.observation.before(first, overlap)
        self.observation.before(first, dict(overlap, locator={"offset": 120, "bytes": 10}))


if __name__ == "__main__":
    unittest.main(verbosity=2)
