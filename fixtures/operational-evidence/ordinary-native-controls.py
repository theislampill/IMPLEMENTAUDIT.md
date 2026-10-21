"""Constructed ordinary-source controls; no native qualification or owner effects."""
import argparse
import base64
import copy
import hashlib
import json
from pathlib import Path
import types
import tempfile
import sys
import contextlib
import os
import shutil
import shlex
import subprocess
import unittest
import concurrent.futures
import threading
from unittest import mock

REPO = Path(__file__).resolve().parents[2]


def load_owner(name):
    lane = 'route-graph' if name == 'route-transaction.py' else 'native-runtime'
    path = REPO / ('source-peers/' + lane + '/skills/implementaudit/scripts') / name
    module = types.ModuleType("ordinary_test_" + name.replace(".", "_"))
    module.__file__ = str(path)
    exec(compile(path.read_bytes(), str(path), "exec"), module.__dict__)
    return module


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def sha(value):
    return hashlib.sha256(value if isinstance(value, bytes) else canonical(value)).hexdigest()


def wire(value):
    raw = canonical(value)
    return {"bytes": len(raw), "digest": "sha256:" + sha(raw), "bytes_b64": base64.b64encode(raw).decode()}


def reseal(value):
    value["export_digest"] = sha({k: v for k, v in value.items() if k != "export_digest"})
    return value


def replace_execution(value, mutate):
    receipt = value['receiving']['process']
    record = json.loads(base64.b64decode(receipt['wire']['bytes_b64']))
    mutate(record['execution'])
    record['execution_digest'] = 'sha256:' + sha(record['execution'])
    receipt['wire'] = wire(record)
    raw = base64.b64decode(receipt['wire']['bytes_b64'])
    receipt['oid'] = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()


def available_export(*, canonical_route=None, host_and_scope=None, scope=None, code_pins=None):
    """Constructed source fixture, never admitted native evidence."""
    obs = load_owner("compaction-result-observation.py")
    parent, child = "11111111-1111-1111-1111-111111111111", "22222222-2222-2222-2222-222222222222"
    task = "ordinary-fixture-review"
    controller = "constructed-ordinary"
    route = {"controller_id": controller, "controller_record_oid": "1" * 40,
        "ref": "refs/implementaudit/route-decisions/" + controller, "record_oid": "2" * 40,
        "record_identity": "sha256:" + sha("route"), "decision": "REQUIRED", "classification": "MECHANICALLY_REQUIRED",
        "route_transaction_id": "sha256:" + sha("transaction"), "obligation_id": "sha256:" + sha("obligation"), "route_state": "SATISFIED"}
    host = {"host_id": "codex", "host_session_id": parent, "host_binding_generation": "G0002", "host_correlation_id": "sha256:" + sha("correlation"),
        "continuity_generation": "G0003", "continuity_receipt": "refs/implementaudit/continuity-receipts/" + controller + "/G0003@" + "3" * 40,
        "obligation_id": route["obligation_id"], "route_transaction_id": route["route_transaction_id"], "controller_id": controller,
        "claim_id": "4" * 32, "explicit_run_root": "/constructed/repo/.IMPLEMENTAUDIT/runs/ordinary"}
    if canonical_route is not None: route = copy.deepcopy(canonical_route)
    if host_and_scope is not None: host = copy.deepcopy(host_and_scope)
    controller, parent = route['controller_id'], host['host_session_id']
    scope = copy.deepcopy(scope) if scope is not None else {"identity": "ordinary-review", "digest": "sha256:" + sha({"identity": "ordinary-review"})}
    names = ('route-transaction.py', 'compaction-audit-pending.py', 'compaction-result-observation.py', 'compaction-source-owner-codex-app.py',
        'bounded_source_owner.py', 'bounded_native_reader.py', 'bounded_file_custody.py', 'codex-recovery-native-reader.py',
        'host-session-binding.py', 'compile-work-graph.py', 'claim-run.sh', 'validate-run-root.sh', 'route_request_policy.py')
    code = {"implementaudit/scripts/" + name: sha(name) for name in names}
    code.update({name: sha(name) for name in ('implementaudit/SKILL.md', 'audit-assess/SKILL.md', 'implementaudit/references/child-agents.md', 'implementaudit/references/continuity.md')})
    if code_pins is not None: code = copy.deepcopy(code_pins)
    def pin(name, size=100): return {"path": "/constructed/results/" + name, "bytes": size, "sha256": sha(name)}
    policy = {"schema": "implementaudit.ordinary-native-policy.v1", "profile_id": obs.ORDINARY_PROFILE,
        "selection_pin": pin("selection.json"), "instance_selection": "EXACT_ROOT_EXECUTION_ANCESTRY",
        "provider": {key: pin(key) for key in ("native_executable", "desktop_executable", "desktop_asar", "config_file", "python_executable")},
        "code_pins": code, "receiver_argv": ['/constructed/results/python_executable', '-I', '-S', '-B',
            '/constructed/results/compaction-source-owner-codex-app.py', '--ordinary-receiver'], "receiver_node": "receiver",
        "consumer": "join", "artifact_root": "/constructed/results", "root_thread_id": parent, "root_agent_path": "/root"}
    mission = {"schema": "implementaudit.ordinary-review-mission.v1", "policy_digest": sha(policy), "scope": scope,
               "mission": "CONSTRUCTED source control only", "authority_ceiling": "NONE"}
    packet = {"schema": "implementaudit.route-packet.v1", "obligation_id": route["obligation_id"], "route_transaction_id": route["route_transaction_id"],
        "target_identity": "audit-assess", "source_event": {"schema": "implementaudit.source-event.v1", "source_identity": "fixture-event",
        "provenance": {"schema": "implementaudit.source-event-provenance.v1", "event_id": "fixture-event", "host_correlation_id": host["host_correlation_id"]},
        "body": canonical(mission).decode(), "kind": "one-shot-action", "reactivation": {"reopen": False, "target_changed": False, "invalidating_evidence": False}}}
    packet_wire = wire(packet)
    opening = {"schema": "implementaudit.r0033-current-episode-binding.v1", "route_current": route, "open_record_oid": "5" * 40,
        "open_record_identity": "sha256:" + sha("open"), "logical_task": task, "selected_child_role": "audit-assess",
        "selected_child_target": "independently assess the exact immutable review packet", "packet_pin": {k: packet_wire[k] for k in ("bytes", "digest")},
        "skill_pin": {"identity": "/constructed/skills/audit-assess/SKILL.md", "bytes": 100, "digest": "sha256:" + code["audit-assess/SKILL.md"]},
        "host_and_scope": host, "canonical_route_currentness": "VALIDATED_AT_READ", "authority_ceiling": "NONE"}
    binding_digest = "sha256:" + sha(opening)
    opening_digest = "sha256:" + sha({k: opening[k] for k in ('open_record_oid', 'open_record_identity', 'logical_task',
        'selected_child_role', 'selected_child_target', 'packet_pin', 'skill_pin', 'host_and_scope')})
    opening.update(opening_digest=opening_digest, binding_digest=binding_digest)
    owner = {"profile_id": obs.ORDINARY_PROFILE, "issuer_id": "codex-app-canonical-ordinary-public-v1", "policy_digest": sha(policy),
        "code_pins": code, "canonical_route": route, "host_and_scope": host, "opening": opening, "scope": scope}
    sources = {role: {"path": "/constructed/" + role + ".jsonl", "physical": {"device": 1, "inode": inode},
        "metadata": {"offset": 0, "bytes": 100, "sha256": sha(role), "embedded_ordinal": 0, "physical_line": 1},
        "thread_id": parent if role == "parent" else child, "cutoff": 750 if role == "parent" else 250} for role, inode in (("parent", 1), ("child", 2))}
    def record(role, ordinal, second, label):
        return {"path": sources[role]["path"], "physical": sources[role]["physical"], "role": role,
            "locator": {"offset": ordinal * 100, "bytes": 50, "sha256": sha(label), "embedded_ordinal": ordinal, "physical_line": ordinal + 1},
            "timestamp": "2026-10-20T12:00:%02dZ" % second, "message_or_call_id": label}
    opened, spawn_call, spawn_out = record("parent", 1, 1, "open"), record("parent", 2, 2, "spawn"), record("parent", 3, 3, "spawn-output")
    activation, final = record("child", 1, 4, "activation"), record("child", 2, 5, "final")
    accepted, call, output, joined = [record("parent", ordinal, second, name) for ordinal, second, name in
        ((4, 6, "accept"), (5, 7, "receiver-call"), (6, 8, "receiver-output"), (7, 9, "join"))]
    members = [{"pin": pin("review.txt", 17), "physical": {"device": 1, "inode": 3}}]
    returned = {"schema": "implementaudit.child-return.v1", "obligation_id": route["obligation_id"], "route_transaction_id": route["route_transaction_id"],
        "packet_digest": packet_wire["digest"], "status": "RETURNED", "payload": {"schema": "implementaudit.ordinary-review-payload.v1",
        "verdict": "PASS", "scope": scope, "summary": "CONSTRUCTED fixture review", "members": [m["pin"] for m in members], "authority_ceiling": "NONE"}}
    result = {"packet": packet_wire, "return": wire(returned), "actual_child_identity": {"thread_id": child, "parent_thread_id": parent,
        "agent_path": "/root/" + task}, "members": members, "final": final}
    decision = {"schema": "implementaudit.governor-route-decision.v1", "obligation_id": route["obligation_id"],
        "route_transaction_id": route["route_transaction_id"], "return_digest": result["return"]["digest"], "outcome": "SATISFIED", "reason": "CONSTRUCTED scoped acceptance"}
    acceptance = {"decision": wire(decision), "record": accepted}
    stdout = canonical(obs.ordinary_receiver_value_v1(owner, result, acceptance)).decode() + "\n"
    execution = {'schema': 'implementaudit.ordinary-receiver-execution.v1', 'policy_digest': sha(policy),
        'opening_digest': opening_digest, 'return_digest': result['return']['digest'], 'acceptance_digest': acceptance['decision']['digest'],
        'argv': policy['receiver_argv'], 'python_pin': policy['provider']['python_executable'],
        'source_pin': {**pin('compaction-source-owner-codex-app.py'), 'sha256': code['implementaudit/scripts/compaction-source-owner-codex-app.py']}, 'stdout': stdout,
        'stdout_sha256': sha(stdout.encode()), 'stderr_sha256': sha(b''), 'exit_code': 0}
    execution_record = {'schema': 'implementaudit.ordinary-receiver-record.v2', 'accepted_record_oid': route['record_oid'],
        'opening_digest': opening_digest, 'attempt_oid': '6' * 40, 'execution': execution, 'execution_digest': 'sha256:' + sha(execution)}
    raw_execution = canonical(execution_record)
    process = {'ref': 'refs/implementaudit/ordinary-receivers/' + controller + '/' + opening_digest.removeprefix('sha256:'),
        'oid': hashlib.sha1(b'blob ' + str(len(raw_execution)).encode() + b'\0' + raw_execution).hexdigest(), 'wire': wire(execution_record)}
    event = {"id": "fixture-review-accepted", "kind": "JOIN", "subject": "qualification"}
    graph_digest = sha("graph")
    dispatch_id = sha([graph_digest, event, ["receiver"]])
    dispatch = {"schema": "implementaudit.native-dispatch.v1", "graph_digest": graph_digest, "event": event,
        "dispatch_id": dispatch_id, "selected": ["receiver"], "inputs": {"receiver": sha("input")}, "capacity": 2,
        "active_occupancy": 1, "free_capacity": 1, "deferred": {}, "blocked": {}, "placements": {"receiver": "GOVERNOR"},
        "mode": "CHEAP_SERIAL", "graph_required": False, "authority": "NONE"}
    work = {"schema": "implementaudit.work-result.v1", "node": "receiver", "dispatch_id": dispatch_id, "graph_digest": graph_digest,
        "input_digest": sha("input"), "status": "PASS", "terminal": True, "exit_code": 0, "evidence_digest": execution["stdout_sha256"],
        "independence_key": "actual-receiver-only", "scope": ["receiver"]}
    join = {"schema": "implementaudit.native-join.v1", "status": "SATISFIED_AT_DECLARED_RESULT_CONTRACT", "all_required_settled": True,
        "required": ["receiver"], "optional": [], "missing": [], "omitted_optional": [], "retained_scopes": {"receiver": ["receiver"]},
        "graph_digest": graph_digest, "consumer": "join", "authority": "NONE", "lifecycle_credit": "NONE"}
    receiving = {"process": process, "dispatch": dispatch, "result": work, "join": join, "record": joined}
    def public(pin_value, body, phase="commentary"):
        return {"pin": pin_value, "message_id": pin_value["message_or_call_id"], "turn_id": "33333333-3333-3333-3333-333333333333",
                "revision": "retained_44444444-4444-4444-4444-444444444444", "phase": phase, "body": body, "body_sha256": sha(body.encode())}
    def fenced(value): return "```json\n" + canonical(value).decode() + "\n```"
    public_records = [public(opened, "```ini\nCHILD_TASK=" + task + "\nCHILD_SKILL_SELECTED=audit-assess\nSTATUS=OPEN\nLOAD=UNVERIFIED\n```"),
        public(final, fenced(returned), "final_answer"), public(accepted, fenced(decision)),
        public(joined, fenced(obs.ordinary_join_value_v1(owner, result, acceptance, receiving)))]
    value = {"schema": obs.ORDINARY_EXPORT_SCHEMA, "status": "AVAILABLE", "reason_code": None, "owner": owner, "result": result,
        "acceptance": acceptance, "receiving": receiving, "lifecycle": dict(obs.ORDINARY_LIFECYCLE),
        "occurrences": {"scope": "SELECTED_FRESH_CHILD_ONLY", "history": "UNEXAMINED_OUTSIDE_SELECTED_RECORDS", "open": opened,
            "spawn": {"call": spawn_call, "output": spawn_out, "task_name": task, "fork_turns": "none"}, "activation": activation},
        "custody": {"policy": policy, "sources": sources, "review_evidence": pin("review-evidence.json"),
            "receiving_evidence": pin("receiving-evidence.json"), "public_records": public_records}, "authority_ceiling": "NONE"}
    return reseal(value)


class OrdinaryControls(unittest.TestCase):
    @unittest.skipUnless(os.name == 'nt', 'Selected source loader uses Windows held-file custody')
    def test_changed_observation_module_refuses_before_execution(self):
        owner = load_owner('compaction-source-owner-codex-app.py')
        with tempfile.TemporaryDirectory(prefix='ordinary-code-pins-') as directory:
            scripts = Path(directory)/'skills/implementaudit/scripts'
            scripts.mkdir(parents=True)
            code = {}
            for relative in available_export()['owner']['code_pins']:
                source = REPO/'source-peers/native-runtime/skills'/relative
                if not source.is_file(): source = REPO/'source-peers/route-graph/skills'/relative
                if not source.is_file(): source = REPO/'skills'/relative
                destination = scripts.parent.parent/relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                raw = source.read_bytes(); destination.write_bytes(raw); code[relative] = sha(raw)
            selected = {'runtime_helpers': {name: {'path': str(scripts/name), 'bytes': (scripts/name).stat().st_size,
                'sha256': sha((scripts/name).read_bytes())} for name in
                ('bounded_file_custody.py','bounded_native_reader.py','bounded_source_owner.py')},
                'code_pins': {k:v for k,v in code.items() if not k.endswith('/compaction-source-owner-codex-app.py')}}
            (scripts/'compaction-result-observation.py').write_bytes(b'raise AssertionError("UNTRUSTED_OBSERVATION_MODULE_EXECUTED")\n')
            with mock.patch.object(owner, 'HERE', scripts):
                with self.assertRaisesRegex(ValueError, 'ORDINARY_FIXED_CODE_CHANGED'):
                    owner._ordinary_modules_v1(selected)

    def test_mission_policy_mismatch_refuses_before_native_effect(self):
        owner = load_owner('compaction-source-owner-codex-app.py')
        obs = load_owner('compaction-result-observation.py'); value = available_export()
        canonical_state = {'status':'SATISFIED', 'packet':value['result']['packet'], 'scope':value['owner']['scope']}
        policy = copy.deepcopy(value['custody']['policy']); policy['receiver_node'] = 'foreign-receiver'
        selected = {'episode_owner': {'repository': str(REPO), 'controller': 'constructed-ordinary'}}
        route = types.SimpleNamespace(read_current_ordinary_execution_v1=lambda *a:None)
        with mock.patch.object(owner, '_ordinary_selection_v1', return_value=selected), \
             mock.patch.object(owner, '_ordinary_modules_v1', return_value=((),obs,
                 {'implementaudit/scripts/compaction-source-owner-codex-app.py': '0'*64})), \
             mock.patch.object(owner, 'ordinary_policy_v1', return_value=policy), \
             mock.patch.object(owner, '_ordinary_canonical_v1', return_value=(route,canonical_state)), \
             mock.patch.object(owner, '_ordinary_provider_guard_v1', side_effect=AssertionError('NATIVE_EFFECT_REACHED')):
            with self.assertRaisesRegex(ValueError, 'ORDINARY_MISSION_POLICY_CHANGED'):
                owner.execute_ordinary_receiver_v1()

    @unittest.skipUnless(os.name == 'nt', 'Selected native document reader uses Windows held-file custody')
    def test_document_parent_substitution_cannot_read_outside_bytes(self):
        owner = load_owner('compaction-source-owner-codex-app.py')
        obs = load_owner('compaction-result-observation.py')
        custody_path = REPO/'source-peers/native-runtime/skills/implementaudit/scripts/bounded_file_custody.py'
        helper_raw = custody_path.read_bytes()
        with tempfile.TemporaryDirectory(prefix='ordinary-document-race-') as directory:
            root = Path(directory).resolve()
            folder, saved, outside = root/'selected', root/'saved', root/'outside'
            folder.mkdir(); outside.mkdir()
            target = folder/'record.json'; target.write_bytes(b'{}')
            sentinel = b'{"outside_owned_test_sentinel":true}'
            (outside/'record.json').write_bytes(sentinel)
            selected = {'receiving': {'artifact_root': str(root)}, 'runtime_helpers': {
                'bounded_file_custody.py': {'path': str(custody_path), 'bytes': len(helper_raw), 'sha256': sha(helper_raw)}}}
            actual_physical, actual_read = obs.physical, Path.read_bytes
            switched = False; outside_reads = []
            def race(path):
                nonlocal switched
                result = actual_physical(path)
                if Path(path) == target and not switched:
                    self.assertTrue(all(p.is_relative_to(root) for p in (folder, saved, outside)))
                    folder.rename(saved)
                    if os.name == 'nt':
                        subprocess.run(['cmd.exe', '/c', 'mklink', '/J', str(folder), str(outside)],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True, creationflags=subprocess.CREATE_NO_WINDOW)
                    else: folder.symlink_to(outside, target_is_directory=True)
                    switched = True
                return result
            def observe_read(path):
                raw = actual_read(path)
                if Path(path) == target and raw == sentinel: outside_reads.append(len(raw))
                return raw
            try:
                with mock.patch.object(obs, 'physical', side_effect=race), mock.patch.object(Path, 'read_bytes', observe_read):
                    with self.assertRaises((ValueError, OSError)):
                        owner._ordinary_document_v1(obs, selected, str(target))
                self.assertTrue(switched)
                self.assertEqual(outside_reads, [], 'document slot followed a substituted parent before custody validation')
            finally:
                if switched:
                    if os.name == 'nt': os.rmdir(folder)
                    else: folder.unlink()
                    saved.rename(folder)

    def test_ordinary_export_requires_its_own_validator(self):
        obs = load_owner("compaction-result-observation.py")
        self.assertTrue(callable(getattr(obs, "validate_ordinary_episode_export_v1", None)),
                        "ordinary receiving must not enter the compaction schema")

    def test_source_selection_stays_unbound_in_public_source(self):
        owner = load_owner("compaction-source-owner-codex-app.py")
        self.assertIsNone(owner.NONPROTECTED_SELECTION_PIN)
        self.assertTrue(hasattr(owner, "ORDINARY_SELECTION_PIN"))
        self.assertIsNone(owner.ORDINARY_SELECTION_PIN)
        observed = available_export()['owner']['code_pins']
        fixed = {k:v for k,v in observed.items() if not k.endswith('/compaction-source-owner-codex-app.py')}
        owner._ordinary_check_code_pins_v1({'code_pins':fixed}, observed)
        for changed in ({**fixed, 'extra':'0'*64}, {k:v for k,v in fixed.items() if k!='audit-assess/SKILL.md'},
                        {**fixed, 'implementaudit/scripts/host-session-binding.py':'0'*64}):
            with self.assertRaisesRegex(ValueError, 'ORDINARY_FIXED_CODE_CHANGED'):
                owner._ordinary_check_code_pins_v1({'code_pins':changed}, observed)

    def test_available_and_each_truthful_absence(self):
        obs = load_owner("compaction-result-observation.py")
        value = available_export()
        self.assertEqual(obs.validate_frozen_episode_export_v1(value), value)
        for reason in obs.ORDINARY_ABSENCES:
            self.assertEqual(obs.ordinary_export_unavailable_v1(reason)["reason_code"], reason)

    def test_resealed_semantic_faults_are_rejected(self):
        obs = load_owner("compaction-result-observation.py")
        mutations = [
            ("foreign child", lambda v: v["result"]["actual_child_identity"].update(agent_path="/root/other")),
            ("foreign role", lambda v: v["owner"]["opening"].update(selected_child_role="audit-state")),
            ("wrong packet", lambda v: v["owner"]["opening"]["packet_pin"].update(digest="sha256:" + "0" * 64)),
            ("scope", lambda v: v["owner"]["scope"].update(identity="later-boundary")),
            ("unaccepted", lambda v: v["owner"]["canonical_route"].update(route_state="RETURNED")),
            ("member identity", lambda v: v["result"]["members"][0]["pin"].update(sha256="0" * 64)),
            ("outside custody", lambda v: v["result"]["members"][0]["pin"].update(path="/other/result.txt")),
            ("missing member", lambda v: v["result"].update(members=[])),
            ("source alias", lambda v: v["custody"]["sources"]["child"].update(physical=v["custody"]["sources"]["parent"]["physical"])),
            ("cutoff", lambda v: v["custody"]["sources"]["child"].update(cutoff=120)),
            ("copied final", lambda v: v["result"]["final"]["locator"].update(offset=90)),
            ("fork", lambda v: v["occurrences"]["spawn"].update(fork_turns="all")),
            ("early acceptance", lambda v: v["acceptance"]["record"].update(timestamp="2026-10-20T11:00:00Z")),
            ("process nonzero", lambda v: replace_execution(v, lambda e: e.update(exit_code=1))),
            ("false exit", lambda v: replace_execution(v, lambda e: e.update(exit_code=False))),
            ("wrong interpreter", lambda v: replace_execution(v, lambda e: e['python_pin'].update(sha256='0' * 64))),
            ("wrong source", lambda v: replace_execution(v, lambda e: e['source_pin'].update(sha256='0' * 64))),
            ("wrong actual command", lambda v: replace_execution(v, lambda e: e.update(argv=['python', 'other.py']))),
            ("wrong execution ref", lambda v: v['receiving']['process'].update(ref='refs/implementaudit/ordinary-receivers/foreign/other')),
            ("wrong execution object", lambda v: v['receiving']['process'].update(oid='0' * 40)),
            ("raw process testimony", lambda v: v['receiving'].update(process={'exit_code': 0, 'stdout': 'PASS'})),
            ("model-as-process", lambda v: v["receiving"]["result"].update(node="reviewer")),
            ("whole parent", lambda v: v["receiving"]["result"].update(scope=["qualification"])),
            ("wrong dispatch", lambda v: v["receiving"]["result"].update(dispatch_id="0" * 64)),
            ("wrong graph", lambda v: v["receiving"]["join"].update(graph_digest="0" * 64)),
            ("missing contributor", lambda v: v["receiving"]["join"].update(required=["receiver", "other"])),
            ("join authority", lambda v: v["receiving"]["join"].update(authority="ROOT")),
            ("dispose credit", lambda v: v["lifecycle"].update(DISPOSE="VERIFIED")),
            ("parent complete", lambda v: v["lifecycle"].update(parent_complete=True)),
            ("private extra", lambda v: v["custody"].update(reasoning="untrusted extra")),
            ("public text drift", lambda v: v["custody"]["public_records"][1].update(body="changed")),
            ("missing source pin", lambda v: v["owner"]["code_pins"].pop("audit-assess/SKILL.md")),
        ]
        for name, mutate in mutations:
            with self.subTest(name=name):
                value = available_export(); mutate(value); reseal(value)
                with self.assertRaises((ValueError, KeyError, TypeError)):
                    obs.validate_frozen_episode_export_v1(value)

    def test_frozen_validation_performs_no_io(self):
        obs = load_owner("compaction-result-observation.py"); value = available_export()
        with mock.patch("builtins.open", side_effect=AssertionError("forbidden IO")), mock.patch.object(Path, "stat", side_effect=AssertionError("forbidden stat")):
            self.assertEqual(obs.validate_ordinary_episode_export_v1(value), value)

    def test_closed_exec_pair_requires_exact_call_and_success(self):
        obs = load_owner("compaction-result-observation.py")
        call = {"type": "response_item", "payload": {"type": "custom_tool_call", "name": "exec", "status": "completed", "input": "exact", "call_id": "one"}}
        nested = {"chunk_id": "chunk", "wall_time_seconds": 1.0, "exit_code": 0, "original_token_count": 1, "output": "ok"}
        output = {"type": "response_item", "payload": {"type": "custom_tool_call_output", "call_id": "one", "output":
            [{"type": "input_text", "text": "wrapper"}, {"type": "input_text", "text": json.dumps(nested)}]}}
        self.assertEqual(obs.ordinary_command_response_v1(call, output, "exact"), "ok")
        for mutate in (lambda c, o: c["payload"].update(input="other"), lambda c, o: o["payload"].update(call_id="other"),
                       lambda c, o: c["payload"].update(type="function_call"), lambda c, o: o["payload"].update(output=[{"type": "text", "text": "ok"}])):
            c, o = copy.deepcopy(call), copy.deepcopy(output); mutate(c, o)
            with self.assertRaises(ValueError): obs.ordinary_command_response_v1(c, o, "exact")

    def test_configuration_mismatch_stops_before_ancestry_or_native_read(self):
        owner = load_owner("compaction-source-owner-codex-app.py")
        with tempfile.TemporaryDirectory(prefix="ordinary-provider-control-") as temp:
            selected = {}
            for key in ("native_executable", "desktop_executable", "desktop_asar", "config_file", "python_executable"):
                path = Path(temp) / key; path.write_bytes(key.encode())
                selected[key] = {"path": str(path), "bytes": path.stat().st_size, "sha256": sha(path.read_bytes())}
            selected["config_file"]["sha256"] = "0" * 64
            helpers = types.SimpleNamespace(owning_ordinary_host=mock.Mock(side_effect=AssertionError("must not acquire host")))
            custody = types.SimpleNamespace(held_file=lambda path, **kwargs: open(path, "rb"))
            with self.assertRaisesRegex(ValueError, "ORDINARY_PROVIDER_DIGEST_CHANGED"):
                with owner._ordinary_provider_guard_v1((selected, custody, None, helpers, None)):
                    self.fail("mismatched policy reached acquisition")
            helpers.owning_ordinary_host.assert_not_called()

    def test_ordinary_ancestry_requires_explicit_policy_and_exact_unique_chain(self):
        owner = load_owner("bounded_source_owner.py")
        with tempfile.TemporaryDirectory(prefix="ordinary-ancestry-control-") as temp:
            native, desktop = Path(temp) / "codex.exe", Path(temp) / "ChatGPT.exe"
            native.write_bytes(b"fixture"); desktop.write_bytes(b"fixture")
            selected = {"schema": "implementaudit.codex-ordinary-selection.v1", "instance_selection": "EXACT_ROOT_EXECUTION_ANCESTRY",
                        "native_executable": {"path": str(native)}, "desktop_executable": {"path": str(desktop)}}
            rows = [{"pid": 10, "parent_pid": 20, "name": "python.exe", "path": "unused", "created_utc": "current"},
                    {"pid": 20, "parent_pid": 30, "name": "codex.exe", "path": str(native), "created_utc": "current"},
                    {"pid": 30, "parent_pid": 0, "name": "ChatGPT.exe", "path": str(desktop), "created_utc": "current"}]
            self.assertEqual(owner.ordinary_ancestry_pair_v1(selected, rows, 10)["native_process"]["pid"], 20)
            for change in (lambda s, r: s.update(schema="old-policy"), lambda s, r: r[0].update(parent_pid=99),
                           lambda s, r: r[1].update(pid=10), lambda s, r: r[1].update(path=str(desktop))):
                selection, records = copy.deepcopy(selected), copy.deepcopy(rows); change(selection, records)
                with self.assertRaises(ValueError): owner.ordinary_ancestry_pair_v1(selection, records, 10)

    def test_exact_public_acquisition_is_stable_after_unrelated_append(self):
        owner, obs = load_owner("compaction-source-owner-codex-app.py"), load_owner("compaction-result-observation.py")
        value = available_export(); expected = value["custody"]["public_records"][1]
        child = value["result"]["actual_child_identity"]
        header = {"timestamp": "2026-10-20T12:00:00Z", "ordinal": 0, "type": "session_meta", "payload": {"id": child["thread_id"]}}
        row = {"timestamp": "2026-10-20T12:00:05Z", "ordinal": 1, "type": "response_item", "payload": {"type": "message", "id": "final",
            "role": "assistant", "phase": "final_answer", "content": [{"type": "output_text", "text": expected["body"], "annotations": [], "logprobs": []}]},
            "metadata": {"client_authored": False, "retained_source": {"complete": True, "revision": expected["revision"],
                "id": {"message_id": "final", "role": "assistant", "turn_id": expected["turn_id"]}}}}
        raw_header, raw_row = canonical(header) + b"\n", canonical(row) + b"\n"
        with tempfile.TemporaryDirectory(prefix="ordinary-public-control-") as temp:
            path = Path(temp) / "child.jsonl"; path.write_bytes(raw_header + raw_row)
            _, info = obs.physical(str(path))
            metadata = {"offset": 0, "bytes": len(raw_header), "sha256": sha(raw_header), "embedded_ordinal": 0, "physical_line": 1}
            locator = {"offset": len(raw_header), "bytes": len(raw_row), "sha256": sha(raw_row), "embedded_ordinal": 1, "physical_line": 2}
            context = {"profile_id": obs.NONPROTECTED_PROFILE, "parent_identity": {"thread_id": child["parent_thread_id"]}, "actual_child_identity": child,
                "child": {"path": str(path), "physical": obs.identity(info), "metadata": metadata, "metadata_payload_digest": sha(header["payload"])}}
            response = {"responses": [{"items": [{"id": "final", "turn_id": expected["turn_id"], "phase": "final_answer",
                "body_bytes": len(expected["body"].encode()), "body_sha256": expected["body_sha256"]}]}]}
            with mock.patch.object(owner, "_np_call", return_value=response) as api:
                first = owner._ordinary_public_v1(None, obs, context, "child", locator, "final_answer")
                with path.open("ab") as stream: stream.write(b'{"unrelated":"not read"}\n')
                second = owner._ordinary_public_v1(None, obs, context, "child", locator, "final_answer")
                self.assertEqual(first, second)
                self.assertEqual(api.call_args.args[1][0][0], "thread/items/read")
                bad = copy.deepcopy(response); bad["responses"][0]["items"][0]["body_sha256"] = "0" * 64
                api.return_value = bad
                with self.assertRaisesRegex(ValueError, "ORDINARY_NATIVE_PUBLIC_BODY_DIFFERS"):
                    owner._ordinary_public_v1(None, obs, context, "child", locator, "final_answer")

    def test_review_only_validator_cannot_be_used_as_full_export(self):
        obs = load_owner("compaction-result-observation.py"); value = available_export()
        context = {role: value["custody"]["sources"][role] for role in ("parent", "child")}
        context.update(parent_identity={"thread_id": value["result"]["actual_child_identity"]["parent_thread_id"]},
                       actual_child_identity=value["result"]["actual_child_identity"])
        self.assertIsNone(obs.validate_ordinary_review_v1(value["owner"], value["result"], value["acceptance"], value["occurrences"],
            context, value["custody"]["public_records"][:3], value["custody"]["policy"]))
        value["receiving"] = None; reseal(value)
        with self.assertRaises(ValueError): obs.validate_ordinary_episode_export_v1(value)

    @unittest.skipUnless(os.name == 'nt', 'Selected ordinary native receiver uses Windows host custody')
    def test_real_held_interpreter_entry_refuses_unbound_public_selection(self):
        helper = load_owner('bounded_source_owner.py')
        helper.custody = load_owner('bounded_file_custody.py')
        source = REPO / 'source-peers/native-runtime/skills/implementaudit/scripts/compaction-source-owner-codex-app.py'
        def pin(path):
            raw = path.read_bytes()
            return {'path': str(path.resolve()), 'bytes': len(raw), 'sha256': sha(raw)}
        selected = {'python_executable': pin(Path(sys.executable)), 'episode_owner': {'repository': str(REPO)}}
        source_pin = pin(source)
        with mock.patch.object(helper.subprocess, 'Popen', wraps=subprocess.Popen) as launch:
            result = helper.run_held_ordinary_receiver_v1(selected, source_pin)
        environment = launch.call_args.kwargs['env']
        route = load_owner('route-transaction.py')
        # The actual receiver must still reach the existing R0011/R0033 owners
        # through their trusted Git/Bash discovery, never an ambient PATH.
        with mock.patch.dict(os.environ, environment, clear=True):
            self.assertTrue(route.trusted_host_executable(REPO, 'git').is_file())
            self.assertTrue(route.trusted_host_executable(REPO, 'bash').is_file())
        self.assertFalse(any(key.startswith(('GIT_', 'PYTHON')) for key in environment))
        self.assertEqual(result['exit_code'], 2)
        self.assertEqual(result['stdout'], '')
        self.assertEqual(result['argv'][-1], '--ordinary-receiver')
        self.assertEqual(result['source_pin'], source_pin)
        self.assertNotEqual(result['stderr_sha256'], sha(b''))
        for which in ('python', 'source'):
            selection, candidate = copy.deepcopy(selected), copy.deepcopy(source_pin)
            (selection['python_executable'] if which == 'python' else candidate)['sha256'] = '0' * 64
            with mock.patch.object(helper.subprocess, 'Popen', side_effect=AssertionError('must refuse before launch')):
                with self.assertRaisesRegex(ValueError, 'ORDINARY_RUNNER_PIN_CHANGED'):
                    helper.run_held_ordinary_receiver_v1(selection, candidate)

    def test_caller_execution_operand_refuses_before_any_store_access(self):
        route = load_owner('route-transaction.py')
        def refuse(message, **kwargs): raise ValueError(message)
        with mock.patch.object(route, 'git', side_effect=AssertionError('must refuse before Git')) as read, \
             mock.patch.object(route, 'write_route_record_blob', side_effect=AssertionError('must refuse before write')) as write, \
             mock.patch.object(route, 'fail', side_effect=refuse):
            with self.assertRaisesRegex(ValueError, 'caller-supplied ordinary execution results are not accepted'):
                route.record_current_ordinary_execution_v1(REPO, 'constructed-ordinary', {})
            read.assert_not_called(); write.assert_not_called()

    def test_execution_record_rejects_accepted_route_and_member_drift(self):
        obs = load_owner('compaction-result-observation.py')
        for which in ('route', 'member', 'return'):
            value = available_export()
            if which == 'route': value['owner']['canonical_route']['record_oid'] = '9' * 40
            elif which == 'member': value['result']['members'][0]['physical']['inode'] += 10
            else: value['result']['return']['digest'] = 'sha256:' + '9' * 64
            with self.assertRaises(ValueError):
                obs.validate_ordinary_execution_v1(value['receiving']['process'], value['owner'], value['result'],
                    value['acceptance'], value['custody']['policy'])

    @contextlib.contextmanager
    def producer_case(self, *, fail_after_run=False):
        """Constructed admission; real pinned code, held process, lease and Git."""
        route = load_owner('route-transaction.py')
        git_exe = shutil.which('git'); self.assertIsNotNone(git_exe)
        environment = route.sanitized_action_environment()
        with tempfile.TemporaryDirectory(prefix='ordinary-producer-') as temp:
            repo = Path(temp)
            def git(*args, raw=None):
                return subprocess.run([git_exe, '-C', str(repo), *args], input=raw, capture_output=True,
                                      env=environment, check=True).stdout.decode().strip()
            git('init', '--quiet')
            git('config', 'core.longpaths', 'true')
            folder = repo / 'skills/implementaudit/scripts'; folder.mkdir(parents=True)
            for name in ('bounded_file_custody.py', 'bounded_source_owner.py'):
                (folder/name).write_bytes((REPO/'source-peers/native-runtime/skills/implementaudit/scripts'/name).read_bytes())
            # This fixture policy deliberately admits a harmless test receiver.
            # It is not the production native profile or an authentication proof.
            owner = folder/'compaction-source-owner-codex-app.py'
            owner.write_text('''import hashlib,json,sys,types\nfrom pathlib import Path\nHERE=Path(__file__).parent\ndef data(): return json.loads((HERE/"fixture.json").read_bytes())\ndef ordinary_policy_v1(): return data()["policy"]\ndef load(name):\n p=HERE/name;m=types.ModuleType(name);m.__file__=str(p);exec(compile(p.read_bytes(),str(p),"exec"),m.__dict__);return m\ndef _ordinary_receiver_observation_v2():\n d=data();h=load("bounded_source_owner.py");h.custody=load("bounded_file_custody.py")\n p=Path(__file__);raw=p.read_bytes();pin={"path":str(p),"bytes":len(raw),"sha256":hashlib.sha256(raw).hexdigest()}\n selected={"python_executable":d["policy"]["provider"]["python_executable"],"episode_owner":{"repository":str(HERE.parents[2])}}\n result=h.run_held_ordinary_receiver_v1(selected,pin)\n if d["fail_after_run"]: raise ValueError("observed effect interrupted before receipt")\n result.update(d["binding"]);return result\nif __name__=="__main__":\n with (HERE/"runs.txt").open("a") as f:f.write("actual-process\\n")\n print("actual constructed receiver")\n''', encoding='utf-8', newline='\n')
            git('add', '--', 'skills')
            git('-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid', '-c', 'commit.gpgsign=false',
                '-c', 'core.hooksPath='+os.devnull, 'commit', '-qm', 'Constructed receiver source')
            controller_oid = git('hash-object', '-w', '--stdin', raw=b'constructed controller\n')
            accepted_oid = git('hash-object', '-w', '--stdin', raw=b'constructed accepted route\n')
            controller = 'constructed-ordinary'
            route_ref = 'refs/implementaudit/route-decisions/'+controller
            git('update-ref', 'refs/implementaudit/controllers/' + controller, controller_oid)
            git('update-ref', route_ref, accepted_oid)
            def pin(path):
                raw=path.read_bytes();return {'path':str(path),'bytes':len(raw),'sha256':sha(raw)}
            policy={'schema':'implementaudit.ordinary-native-policy.v1',
                'provider':{'python_executable':pin(Path(sys.executable))},
                'receiver_argv':[str(Path(sys.executable)),'-I','-S','-B',str(owner),'--ordinary-receiver'],
                'code_pins':{'implementaudit/scripts/'+name:sha((folder/name).read_bytes())
                    for name in ('bounded_file_custody.py','compaction-source-owner-codex-app.py')}}
            scope={'identity':'constructed','digest':'sha256:'+sha('constructed')}
            mission={'schema':'implementaudit.ordinary-review-mission.v1','policy_digest':sha(policy),'scope':scope,'authority_ceiling':'NONE'}
            canonical_state={'status':'SATISFIED','opening':{'opening_digest':'sha256:'+sha('opening')},
                'canonical_route':{'ref':route_ref,'record_oid':accepted_oid,'controller_record_oid':controller_oid},
                'child_return':{'digest':'sha256:'+sha('returned')},'governor_decision':{'digest':'sha256:'+sha('accepted')},
                'packet':wire({'source_event':{'body':canonical(mission).decode()}}),'scope':scope}
            binding={'schema':'implementaudit.ordinary-receiver-execution.v1','policy_digest':sha(policy),
                'opening_digest':canonical_state['opening']['opening_digest'],'return_digest':canonical_state['child_return']['digest'],
                'acceptance_digest':canonical_state['governor_decision']['digest']}
            (folder/'fixture.json').write_bytes(canonical({'policy':policy,'binding':binding,'fail_after_run':fail_after_run}))
            marker = repo / 'untrusted-reference-hook-ran'
            hook = repo / '.git/hooks/reference-transaction'
            hook.write_bytes(("#!/bin/sh\nprintf 'executed\\n' > " + shlex.quote(marker.as_posix()) + "\n").encode())
            hook.chmod(0o755)
            def refuse(message, **kwargs): raise ValueError(message)
            with mock.patch.object(route, 'trusted_host_executable', return_value=Path(git_exe)), \
                 mock.patch.object(route, 'sanitized_action_environment', return_value=environment), \
                 mock.patch.object(route, 'read_current_ordinary_result_v1', return_value=canonical_state), \
                 mock.patch.object(route, 'fail', side_effect=refuse):
                yield route, repo, controller, policy, folder, marker, git, controller_oid

    @unittest.skipUnless(os.name == 'nt', 'Production held custody uses Windows')
    def test_real_owner_held_process_receipt_and_duplicate_refusal(self):
        with self.producer_case() as (route,repo,controller,policy,folder,marker,git,controller_oid):
                result = route.execute_current_ordinary_receiver_v2(repo, controller, policy)
                self.assertTrue(result['executed']); published=result['receipt']
                self.assertEqual((folder/'runs.txt').read_text(), 'actual-process\n')
                self.assertFalse(marker.exists(), 'receipt publication executed an untrusted repository hook')
                self.assertEqual(route.read_current_ordinary_execution_v1(repo, controller), published)
                self.assertEqual(git('rev-parse', published['ref']), published['oid'])
                again=route.execute_current_ordinary_receiver_v2(repo,controller,policy)
                self.assertFalse(again['executed']);self.assertEqual(again['receipt'],published)
                self.assertEqual((folder/'runs.txt').read_text(), 'actual-process\n')
                self.assertEqual(git('rev-parse', published['ref']), published['oid'])
                wrong=copy.deepcopy(policy);wrong['receiver_argv'][-1]='other'
                with self.assertRaisesRegex(ValueError,'prospective policy'):
                    route.execute_current_ordinary_receiver_v2(repo,controller,wrong)
                git('update-ref', 'refs/fixture/hook-positive-control', controller_oid)
                self.assertEqual(marker.read_bytes(), b'executed\n')

    @unittest.skipUnless(os.name == 'nt', 'Production held custody uses Windows')
    def test_interrupted_effect_retains_attempt_and_cannot_replay(self):
        with self.producer_case(fail_after_run=True) as (route,repo,controller,policy,folder,marker,git,controller_oid):
            with self.assertRaisesRegex(ValueError,'observed effect interrupted'):
                route.execute_current_ordinary_receiver_v2(repo,controller,policy)
            self.assertEqual((folder/'runs.txt').read_text(),'actual-process\n')
            attempts=git('for-each-ref','--format=%(objectname)','refs/implementaudit/ordinary-receiver-attempts/')
            self.assertTrue(attempts)
            with self.assertRaisesRegex(ValueError,'prior attempt has no completed receipt'):
                route.execute_current_ordinary_receiver_v2(repo,controller,policy)
            self.assertEqual((folder/'runs.txt').read_text(),'actual-process\n')
            self.assertEqual(git('for-each-ref','--format=%(objectname)','refs/implementaudit/ordinary-receiver-attempts/'),attempts)
            self.assertFalse(git('for-each-ref','--format=%(objectname)','refs/implementaudit/ordinary-receivers/'))

    @unittest.skipUnless(os.name == 'nt', 'Production held custody uses Windows')
    def test_owner_source_drift_refuses_before_attempt_or_process(self):
        with self.producer_case() as (route,repo,controller,policy,folder,marker,git,controller_oid):
            with (folder/'compaction-source-owner-codex-app.py').open('ab') as f:f.write(b'\n# changed after policy\n')
            with self.assertRaisesRegex(ValueError,'active source differs'):
                route.execute_current_ordinary_receiver_v2(repo,controller,policy)
            self.assertFalse((folder/'runs.txt').exists())
            self.assertFalse(git('for-each-ref','--format=%(objectname)','refs/implementaudit/ordinary-receiver-attempts/'))

    @unittest.skipUnless(os.name == 'nt', 'Production held custody uses Windows')
    def test_route_drift_after_process_retains_unresolved_attempt(self):
        with self.producer_case() as (route,repo,controller,policy,folder,marker,git,controller_oid):
            original=route.read_current_ordinary_result_v1.return_value
            def current(*args):
                value=copy.deepcopy(original)
                if (folder/'runs.txt').exists(): value['canonical_route']['record_oid']='9'*40
                return value
            route.read_current_ordinary_result_v1.side_effect=current
            with self.assertRaisesRegex(ValueError,'effect observed but inputs changed'):
                route.execute_current_ordinary_receiver_v2(repo,controller,policy)
            self.assertEqual((folder/'runs.txt').read_text(),'actual-process\n')
            self.assertTrue(git('for-each-ref','--format=%(objectname)','refs/implementaudit/ordinary-receiver-attempts/'))
            self.assertFalse(git('for-each-ref','--format=%(objectname)','refs/implementaudit/ordinary-receivers/'))

    @unittest.skipUnless(os.name == 'nt', 'Production held custody uses Windows')
    def test_concurrent_owner_requests_launch_at_most_one_receiver(self):
        with self.producer_case() as (route,repo,controller,policy,folder,marker,git,controller_oid):
            barrier=threading.Barrier(2)
            def attempt():
                barrier.wait()
                try:return route.execute_current_ordinary_receiver_v2(repo,controller,policy)
                except ValueError as error:return str(error)
            with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
                results=list(pool.map(lambda _:attempt(),range(2)))
            self.assertEqual(sum(type(x)is dict and x['executed'] for x in results),1)
            self.assertEqual((folder/'runs.txt').read_text(),'actual-process\n')
            self.assertIsNotNone(route.read_current_ordinary_execution_v1(repo,controller))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=REPO)
    args, remaining = parser.parse_known_args()
    REPO = args.repo_root.resolve(strict=True)
    unittest.main(argv=[__file__, *remaining])
