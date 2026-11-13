"""Generic bounded read transport. Selection is supplied by its pinned source owner.
No CLI, profile selection, model call, or authority assertion exists here.
"""
import datetime

import hashlib

import json

import os

from pathlib import Path

import queue

import re

import subprocess

import threading

import time

MAX_LINE = 512 * 1024

MAX_STREAM = 2 * 1024 * 1024

def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")

def unique(pairs):
    out = {}
    for key, value in pairs:
        if key in out:
            raise ValueError("DUPLICATE_JSON_KEY")
        out[key] = value
    return out

OWNED_STDIO_PROFILE = 'codex-app-server-0.153.4-owned-stdio-candidate-v1'

def validate_read(method, params, *, profile_id=None):
    if profile_id == OWNED_STDIO_PROFILE and method == 'thread/items/list':
        if (isinstance(params, dict) and
                set(params) == {'threadId', 'turnId', 'limit', 'cursor', 'sortDirection'} and
                all(isinstance(params[key], str) and re.fullmatch(r'[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}', params[key])
                    for key in ('threadId', 'turnId')) and type(params['limit']) is int and
                0 < params['limit'] <= 64 and params['cursor'] is None and params['sortDirection'] == 'asc'):
            return
        raise ValueError('BOUNDED_EXACT_TURN_PAGE_REQUIRED')
    if profile_id == OWNED_STDIO_PROFILE and method == 'thread/list':
        if (isinstance(params, dict) and set(params) == {'cwd', 'sourceKinds', 'limit', 'cursor', 'archived', 'useStateDbOnly'} and
                isinstance(params['cwd'], str) and Path(params['cwd']).is_absolute() and params['sourceKinds'] == ['subAgent'] and
                type(params['limit']) is int and 0 < params['limit'] <= 64 and params['cursor'] is None and
                params['archived'] is False and params['useStateDbOnly'] is True):
            return
        raise ValueError('OWNED_STDIO_BOUNDED_CWD_CATALOG_REQUIRED')
    if method == 'thread/list':
        if (isinstance(params,dict) and set(params)=={'parentThreadId','sourceKinds','limit','cursor','archived','useStateDbOnly'} and
                isinstance(params['parentThreadId'],str) and params['parentThreadId'] and params['sourceKinds']==['subAgent'] and
                type(params['limit']) is int and 0<params['limit']<=100 and params['cursor'] is None and
                params['archived'] is False and params['useStateDbOnly'] is True):
            return
        raise ValueError('ONE_BOUNDED_PARENT_CATALOG_REQUIRED')
    if not isinstance(params, dict) or not isinstance(params.get("threadId"), str) or not params["threadId"]:
        raise ValueError("EXACT_THREAD_REQUIRED")
    if method == "thread/read":
        if set(params) == {"threadId", "includeTurns"} and params["includeTurns"] is False:
            return
    if method == "thread/items/read":
        items = params.get("itemIds")
        if (set(params) == {"threadId", "turnId", "itemIds"} and
                isinstance(params.get("turnId"), str) and params["turnId"] and
                isinstance(items, list) and 1 <= len(items) <= 100 and
                all(isinstance(item, str) and 0 < len(item) <= 256 for item in items) and
                len(set(items)) == len(items)):
            return
    raise ValueError("BOUNDED_READ_ONLY_REQUEST_REQUIRED")

def project_items(result, params):
    data = result.get("data") if isinstance(result, dict) else None
    if not isinstance(data, list) or len(data) != len(params["itemIds"]):
        raise ValueError("EXACT_ITEM_POPULATION_REQUIRED")
    seen = set()
    out = []
    for entry in data:
        item = entry.get("item") if isinstance(entry, dict) else None
        if (not isinstance(item, dict) or entry.get("turnId") != params["turnId"] or
                item.get("id") not in params["itemIds"] or item["id"] in seen or
                item.get("type") != "agentMessage" or item.get("phase") not in ("commentary", "final_answer") or
                not isinstance(item.get("text"), str)):
            raise ValueError("EXACT_PUBLIC_ITEM_REQUIRED")
        seen.add(item["id"])
        out.append({"id": item["id"], "turn_id": entry["turnId"], "phase": item["phase"],
                    "body_bytes": len(item["text"].encode("utf-8")),
                    "body_sha256": hashlib.sha256(item["text"].encode("utf-8")).hexdigest()})
    return out

def project_owned_stdio_items(result, params):
    """One complete exact-turn page; retain public-message hashes, no private bodies."""
    validate_read('thread/items/list', params, profile_id=OWNED_STDIO_PROFILE)
    if (not isinstance(result, dict) or result.get('nextCursor', 'ABSENT') is not None or
            not isinstance(result.get('data'), list) or len(result['data']) > params['limit']):
        raise ValueError('COMPLETE_BOUNDED_TURN_PAGE_REQUIRED')
    seen = set()
    public = []
    excluded = {}
    for entry in result['data']:
        if not isinstance(entry, dict) or entry.get('turnId') != params['turnId'] or not isinstance(entry.get('item'), dict):
            raise ValueError('EXACT_TURN_ITEM_REQUIRED')
        item = entry['item']
        identity, kind = item.get('id'), item.get('type')
        if not isinstance(identity, str) or not identity or len(identity) > 256 or identity in seen or not isinstance(kind, str):
            raise ValueError('UNIQUE_NATIVE_ITEM_REQUIRED')
        seen.add(identity)
        if kind != 'agentMessage':
            excluded[kind] = excluded.get(kind, 0) + 1
            continue
        body, phase = item.get('text'), item.get('phase')
        if not isinstance(body, str) or phase not in ('commentary', 'final_answer'):
            raise ValueError('PUBLIC_MESSAGE_PHASE_REQUIRED')
        raw = body.encode('utf-8')
        if len(raw) > MAX_LINE:
            raise ValueError('PUBLIC_MESSAGE_BYTE_BOUND')
        public.append({'id': identity, 'turn_id': params['turnId'], 'phase': phase,
                       'body_bytes': len(raw), 'body_sha256': hashlib.sha256(raw).hexdigest()})
    return {'items': public, 'excluded_type_counts': excluded, 'page_complete': True}

def project_thread(thread):
    if not isinstance(thread, dict) or thread.get("turns") != []:
        raise ValueError("UNEXPECTED_HYDRATED_OR_INVALID_THREAD")
    fields = ("id", "sessionId", "parentThreadId", "path", "cwd", "cliVersion",
              "originator", "threadSource", "ephemeral", "historyMode", "createdAt",
              "updatedAt", "model", "modelProvider", "reasoningEffort", "agentRole")
    projected = {key: thread[key] for key in fields if key in thread}
    source = thread.get("source")
    projected["source_kind"] = source if isinstance(source, str) else (
        "subAgent" if isinstance(source, dict) and "subAgent" in source else "other")
    projected["turn_count"] = 0
    return projected

class CatalogProjectionRefusal(ValueError):
    def __init__(self, detail):
        super().__init__('CATALOG_PARENT_SOURCE_OR_UNIQUENESS_CHANGED')
        self.detail=detail

def project_owned_stdio_catalog(result, params):
    validate_read('thread/list', params, profile_id=OWNED_STDIO_PROFILE)
    if (not isinstance(result, dict) or result.get('nextCursor', 'ABSENT') is not None or
            not isinstance(result.get('data'), list) or len(result['data']) > params['limit']):
        raise ValueError('OWNED_STDIO_COMPLETE_CATALOG_REQUIRED')
    seen, out = set(), []
    for thread in result['data']:
        row = project_thread(thread)
        if (not isinstance(row.get('id'), str) or not row['id'] or row['id'] in seen or
                row.get('cwd') != params['cwd'] or row.get('source_kind') != 'subAgent'):
            raise ValueError('OWNED_STDIO_CATALOG_SOURCE_OR_IDENTITY')
        seen.add(row['id']); out.append(row)
    return out

def project_catalog(result, params):
    if (not isinstance(result,dict) or 'nextCursor' not in result or result['nextCursor'] not in (None,'') or
            not isinstance(result.get('data'),list) or len(result['data'])>params['limit']):
        raise ValueError('COMPLETE_BOUNDED_CATALOG_REQUIRED')
    seen=set();out=[]
    for thread in result['data']:
        row=project_thread(thread)
        if (not isinstance(row.get('id'),str) or not row['id'] or row['id'] in seen or
                row.get('parentThreadId') not in (None,params['parentThreadId']) or row.get('source_kind') not in ('subAgent','unknown','other') or
                row.get('threadSource') not in (None,'subagent')):
            raise CatalogProjectionRefusal({'id':row.get('id'),'parentThreadId':row.get('parentThreadId'),
                'source_kind':row.get('source_kind'),'threadSource':row.get('threadSource'),
                'duplicate_id':row.get('id') in seen,'expected_parent':params['parentThreadId']})
        seen.add(row['id']);out.append(row)
    return out

def file_pin(path):
    before = path.stat()
    if not path.is_file() or before.st_size > 512 * 1024 * 1024:
        raise ValueError("EXECUTABLE_BOUND")
    h = hashlib.sha256()
    with custody.held_file(path) as stream:
        opened = os.fstat(stream.fileno())
        remaining = before.st_size
        while remaining:
            if os.fstat(stream.fileno()).st_size != before.st_size:
                raise ValueError("EXECUTABLE_CHANGED")
            block = stream.read(min(1024 * 1024, remaining))
            if not block:
                raise ValueError("EXECUTABLE_TRUNCATED")
            h.update(block)
            remaining -= len(block)
        after = os.fstat(stream.fileno())
    last = path.stat()
    def shape(s):
        return (s.st_dev, s.st_ino, s.st_size, s.st_mtime_ns)
    if len({shape(s) for s in (before, opened, after, last)}) != 1:
        raise ValueError("EXECUTABLE_CHANGED")
    return {"path": str(path), "device": before.st_dev, "inode": before.st_ino,
            "bytes": before.st_size, "mtime_ns": before.st_mtime_ns, "sha256": h.hexdigest()}

def cleanup_probe(process, readers, state):
    failures=[]
    def attempt(stage, action):
        try: return action()
        except BaseException as error:
            failures.append({'stage':stage,'exception_type':type(error).__name__})
            return None
    attempt('STDIN_CLOSE',process.stdin.close)
    attempt('WAIT',lambda:process.wait(timeout=3))
    first_poll=attempt('POLL_AFTER_WAIT',process.poll)
    forced=first_poll is None
    if forced:
        if os.name=='nt':
            result=attempt('TREE_TERMINATE',lambda:subprocess.run(
                [str(custody.trusted_system_tool('taskkill.exe')),'/PID',str(process.pid),'/T','/F'],stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,timeout=5,creationflags=subprocess.CREATE_NO_WINDOW))
            if result is not None and result.returncode!=0:
                failures.append({'stage':'TREE_TERMINATE','exception_type':'NONZERO_EXIT'})
        if attempt('POLL_AFTER_TREE_TERMINATE',process.poll) is None:
            attempt('KILL_CREATED_PROCESS',process.kill)
        attempt('WAIT_AFTER_TERMINATE',lambda:process.wait(timeout=2))
    for thread in readers:
        attempt('DRAIN_JOIN',lambda thread=thread:thread.join(timeout=2))
        if attempt('DRAIN_LIVE_CHECK',thread.is_alive) is not False:
            failures.append({'stage':'DRAIN_LIVE_CHECK','exception_type':'UNPROVED_STOP'})
    for name in ('stdout','stderr'):
        # An outstanding drain is already a qualification failure. Still try
        # closure so one broken setup/cleanup step cannot skip all later ones.
        if state[name]['done']:
            attempt('CLOSE_'+name.upper(),getattr(process,name).close)
        else:
            attempt('CLOSE_RAW_'+name.upper(),lambda name=name:os.close(getattr(process,name).fileno()))
            failures.append({'stage':'CLOSE_RAW_'+name.upper(),'exception_type':'DRAIN_NOT_PROVED'})
    code=attempt('FINAL_PROCESS_POLL',process.poll)
    complete=all(s['done'] and s['eof'] and s['failure'] is None for s in state.values())
    return {'forced_cleanup':forced,'exit_code':code,'process_terminated':code is not None,
            'streams_complete':complete,'cleanup_failures':failures}

def _probe_held(selection, methods=None, *, child_id=None):
    BINARY = Path(selection['native_executable']['path'])
    EXPECTED_BINARY_SHA256 = selection['native_executable']['sha256']
    CWD = Path(selection['cwd'])
    ROOT_ID = selection['root_thread_id']
    owned_stdio = selection.get('profile_id') == OWNED_STDIO_PROFILE
    profile_id = OWNED_STDIO_PROFILE if owned_stdio else None
    if owned_stdio:
        code_home = Path(selection['codex_home'])
        if (selection.get('native_version') != 'codex-cli 0.153.4' or not code_home.is_absolute() or
                code_home.resolve(strict=True) != code_home or not code_home.is_dir()):
            raise ValueError('OWNED_STDIO_TASK_HOME_OR_VERSION_REQUIRED')
    if child_id is not None and (not isinstance(child_id, str) or not re.fullmatch(r"[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}", child_id) or child_id == ROOT_ID):
        raise ValueError("DISTINCT_CHILD_ID_REQUIRED")
    methods = methods if methods is not None else [
        ("thread/read", {"threadId": ident, "includeTurns": False}) for ident in (ROOT_ID, child_id) if ident is not None]
    if not isinstance(methods, list) or not 1 <= len(methods) <= 8:
        raise ValueError("REQUEST_COUNT_BOUND")
    for method, params in methods:
        validate_read(method, params, profile_id=profile_id)
        if method == 'thread/list' and (params['cwd'] != str(CWD) if owned_stdio else params['parentThreadId'] != ROOT_ID) or method != 'thread/list' and params['threadId'] not in (ROOT_ID, child_id):
            raise ValueError("UNSELECTED_THREAD")
    pin = file_pin(BINARY)
    if pin["sha256"] != EXPECTED_BINARY_SHA256:
        raise ValueError("SELECTED_EXECUTABLE_CHANGED")
    started = time.monotonic()
    deadline = started + 25
    q = queue.Queue(maxsize=64)
    bad = threading.Event()
    state = {name: {"bytes": 0, "eof": False, "done": False, "failure": None,
                    "sha256": None} for name in ("stdout", "stderr")}
    report = {"schema": "r0038.native-source-capability-probe.v1",
              "time_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
              "authority_ceiling": "NONE", "investigation_only": True,
              "root_thread_id": ROOT_ID, "candidate_child_thread_id": child_id,
              "observed_environment_thread_id": os.environ.get("CODEX_THREAD_ID"),
              "executable": pin, "command": [str(BINARY), "app-server", "--listen", "stdio://"] if owned_stdio else [str(BINARY), "app-server", "--stdio"],
              "responses": [], "failure": None, "protocol": {"streams": state}}
    process = None
    readers = []

    def drain(stream, name):
        h = hashlib.sha256()
        try:
            while True:
                raw = stream.readline(MAX_LINE + 1)
                if not raw:
                    state[name]["eof"] = True
                    break
                h.update(raw)
                state[name]["bytes"] += len(raw)
                if len(raw) > MAX_LINE or state[name]["bytes"] > MAX_STREAM:
                    raise ValueError("STREAM_BYTE_LIMIT")
                if name == "stdout":
                    row = json.loads(raw, object_pairs_hook=unique)
                    if not isinstance(row, dict):
                        raise ValueError("INVALID_RPC_OBJECT")
                    q.put_nowait(row)
        except Exception as error:
            state[name]["failure"] = type(error).__name__
            bad.set()
        finally:
            state[name]["sha256"] = h.hexdigest()
            state[name]["done"] = True

    def request(value):
        allowed = {'initialize', 'initialized', 'thread/read', 'thread/items/read', 'thread/list'}
        if owned_stdio:
            allowed.add('thread/items/list')
        if value['method'] not in allowed:
            raise ValueError("REQUEST_NOT_ALLOWED")
        if value["method"] not in {"initialize", "initialized"}:
            validate_read(value["method"], value["params"], profile_id=profile_id)
            if value['method'] == 'thread/list' and (value['params']['cwd'] != str(CWD) if owned_stdio else value['params']['parentThreadId'] != ROOT_ID) or value['method'] != 'thread/list' and value['params']['threadId'] not in (ROOT_ID, child_id):
                raise ValueError("UNSELECTED_THREAD")
        process.stdin.write(canonical(value) + b"\n")
        process.stdin.flush()
        if "id" not in value:
            return None
        while True:
            if bad.is_set():
                raise ValueError("NATIVE_STREAM_FAILURE")
            if time.monotonic() >= deadline:
                raise TimeoutError("NATIVE_READ_DEADLINE")
            try:
                row = q.get(timeout=min(.2, max(.001, deadline - time.monotonic())))
            except queue.Empty:
                if state["stdout"]["done"]:
                    raise ValueError("NATIVE_STDOUT_CLOSED")
                continue
            if row.get("id") == value["id"]:
                return row
            if "id" in row:
                raise ValueError("UNEXPECTED_RPC_ID_OR_SERVER_REQUEST")

    try:
        process = subprocess.Popen(report["command"], cwd=CWD, stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            env=dict(os.environ, CODEX_HOME=str(code_home)) if owned_stdio else None,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0)
        report["protocol"]["pid"] = process.pid
        for name in ("stdout", "stderr"):
            reader = threading.Thread(target=drain, args=(getattr(process, name), name), daemon=True)
            readers.append(reader)
            reader.start()
        init = request({"id": 1, "method": "initialize", "params": {
            "clientInfo": {"name": "r0038_source_capability_read", "version": "1.0"},
            "capabilities": {"experimentalApi": True, "explicitGatewayOauth": True}}})
        report["initialize_response_sha256"] = hashlib.sha256(canonical(init)).hexdigest()
        if "error" in init:
            report["initialize_error"] = init["error"]
            raise ValueError("INITIALIZE_ERROR")
        request({"method": "initialized"})
        for ident, (method, params) in enumerate(methods, 2):
            raw = request({"id": ident, "method": method, "params": params})
            row = {"method": method, "params": params,
                   "response_sha256": hashlib.sha256(canonical(raw)).hexdigest()}
            if "error" in raw:
                row["error"] = raw["error"]
            elif method == 'thread/items/list' and owned_stdio:
                row.update(project_owned_stdio_items(raw.get('result'), params))
            elif method == "thread/items/read":
                row["items"] = project_items(raw.get("result"), params)
            elif method == 'thread/list':
                row['threads'] = project_owned_stdio_catalog(raw.get('result'), params) if owned_stdio else project_catalog(raw.get('result'), params)
                row['catalog_complete']=True
            else:
                row["thread"] = project_thread(raw.get("result", {}).get("thread"))
            report["responses"].append(row)
    except BaseException as error:
        report["failure"] = type(error).__name__ + ":" + str(error)[:200]
        if isinstance(error,CatalogProjectionRefusal):report['refusal_detail']=error.detail
    finally:
        if process is not None:
            cleaned=cleanup_probe(process,readers,state)
            report['protocol'].update(cleaned)
            if cleaned['cleanup_failures'] or not cleaned['process_terminated'] or not cleaned['streams_complete']:
                report['failure']=report['failure'] or 'NATIVE_CLEANUP_UNQUALIFIED'
    try:
        report["executable_unchanged"] = file_pin(BINARY) == pin
    except BaseException as error:
        report['executable_unchanged']=False
        report['executable_postcheck_failure']=type(error).__name__
        report['failure']=report['failure'] or 'EXECUTABLE_POSTCHECK_FAILED'
    report["elapsed_seconds"] = round(time.monotonic() - started, 3)
    return report

def probe(selection, methods=None, *, child_id=None):
    # The byte pin, CreateProcess, reads, cleanup and final pin all occur while
    # the executable and every parent remain held against writes/deletion.
    with custody.held_file(Path(selection['native_executable']['path']),allow_append=False):
        return _probe_held(selection,methods,child_id=child_id)
