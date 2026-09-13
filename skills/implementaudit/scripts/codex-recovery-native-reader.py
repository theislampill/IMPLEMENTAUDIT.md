"""Read-only native observation owner; no flags constitute producer authentication.

Durable observations require controlled writer/evidence custody. The actual OS,
source-pinned native API and current sources are reread on every consumption.
"""
import argparse, ctypes, datetime, hashlib, importlib.util, json, os, pathlib, queue, subprocess, sys, threading, time

EXPECTED_BINARY = '081e4de4be8e38fac6ed4d95e3b1a0b9f6d31c090ddc36e1696b349fe406f575'
EXPECTED_DESKTOP_PACKAGE = 'OpenAI.Codex_26.908.4834.0_x64__2p2nqsd0c76g0'
EXPECTED_ASAR = '2bd5b96a48232f3ccf3df6be50965920699ea3a1b4512dcdd770e209fd1f009e'
FEATURE = "retain_client_developer_messages"
LIMIT = 8 * 1024 * 1024
EXPECTED_RECOVERY_INPUT_ADAPTER_SHA256 = "ab5782898381268f6149359dc8be0fb05e3938d465275ce962448aa9da0d7754"

class Refusal(RuntimeError): pass

# After-startup retries are typed and bounded; accepted epoch comparators stay exact.
_ACQUISITION_RETRY_CODES = frozenset({'NATIVE_PAIR_CHANGED','PHYSICAL_PAIR_CHANGED','SNAPSHOT_BRACKET_CHANGED'})
_ACQUISITION_CODES = _ACQUISITION_RETRY_CODES | frozenset({'UNKNOWN_FAILURE','INTERRUPTED','DEADLINE_EXHAUSTED','ATTEMPTS_EXHAUSTED','NATIVE_PROTOCOL_FAILURE','NATIVE_CLEANUP_UNPROVED','NATIVE_RESPONSE_ERROR','MATERIAL_SHAPE_INVALID','ACQUISITION_CONTEXT_CHANGED','EPOCH_ALREADY_ATTEMPTED'})
_ACQUISITION_STAGES = frozenset({'FIRST_MATERIAL','SNAPSHOT','SECOND_MATERIAL','PAIR_VALIDATION','SNAPSHOT_EQUALITY','COMPLETE'})

class AcquisitionFailure(Refusal):
    def __init__(self, code):
        if code not in _ACQUISITION_CODES: code='UNKNOWN_FAILURE'
        self.code=code
        self.observation=None
        super().__init__('epoch acquisition '+code)

class ConfigurationInstability(AcquisitionFailure):
    def __init__(self, code):
        if code not in _ACQUISITION_RETRY_CODES: raise AcquisitionFailure('UNKNOWN_FAILURE')
        super().__init__(code)

def _observation_remaining(deadline, limit):
    if deadline is None: return limit
    remaining=deadline-time.monotonic()
    if remaining<=0: raise AcquisitionFailure('DEADLINE_EXHAUSTED')
    return min(limit,remaining)

_PROBE_OPERATIONS = {'PREPARE':'STREAM_PREPARATION_FAILED','LAUNCH':'PROBE_CREATE_FAILED',
    'THREAD_CREATE':'READER_CREATE_FAILED','THREAD_START':'READER_START_FAILED',
    'REQUEST':'NATIVE_REQUEST_FAILED','STDIN_CLOSE':'STDIN_CLOSE_FAILED',
    'WAIT':'PROBE_WAIT_FAILED','TERMINATE':'PROBE_TERMINATE_FAILED',
    'WAIT_AFTER_TERMINATE':'PROBE_WAIT_AFTER_TERMINATE_FAILED',
    'DRAIN_JOIN':'DRAIN_JOIN_FAILED','DRAIN_STATUS':'DRAIN_STATUS_FAILED',
    'FINALIZE':'PROBE_FINALIZE_FAILED'}
_PROBE_EXCEPTION_TYPES = ((AcquisitionFailure,'ACQUISITION_FAILURE'),
    (KeyboardInterrupt,'INTERRUPTED'),(FileNotFoundError,'FILE_NOT_FOUND'),
    (PermissionError,'PERMISSION_DENIED'),((TimeoutError,subprocess.TimeoutExpired),'TIMEOUT'),
    (OSError,'OS_ERROR'),(RuntimeError,'RUNTIME_ERROR'),(ValueError,'VALUE_ERROR'),
    (TypeError,'TYPE_ERROR'))

def _probe_error_number(value):
    return value if type(value) is int and -2147483648<=value<=4294967295 else None

def _probe_exception(operation, error):
    # Never derive a persisted label from exception names/messages or native data.
    category=next((name for kind,name in _PROBE_EXCEPTION_TYPES if isinstance(error,kind)),
                  'OTHER_EXCEPTION')
    def number(name):
        try: return _probe_error_number(getattr(error,name,None))
        except BaseException: return None
    return {'operation':operation,'predicate':_PROBE_OPERATIONS[operation],
        'category':category,'errno':number('errno'),'winerror':number('winerror')}

def _acquisition_protocol(protocol):
    # Do not retain failure text, raw call parameters, RPC rows or native stderr.
    def integer(value): return value if type(value) is int else None
    streams=protocol.get('stream_status',{})
    if not isinstance(streams,dict): streams={}
    result={'probe_pid':integer(protocol.get('probe_pid')),
        'process_terminated':protocol.get('process_terminated') is True,
        'exit_code':integer(protocol.get('exit_code')),
        'failure_present':protocol.get('failure') is not None,
        'streams_complete':protocol.get('streams_complete') is True,
        'streams':{}}
    counts=protocol.get('bytes',{})
    if not isinstance(counts,dict): counts={}
    result['bytes']={name:integer(counts.get(name)) for name in ('stdout','stderr')}
    for name in ('stdout','stderr'):
        row=streams.get(name,{})
        if not isinstance(row,dict): row={}
        result['streams'][name]={'done':row.get('done') is True,'eof':row.get('eof') is True,
            'failure_present':row.get('failure') is not None}
    diagnostics=protocol.get('diagnostics',[])
    result['diagnostics']=[]
    if isinstance(diagnostics,list):
        categories={name for _,name in _PROBE_EXCEPTION_TYPES}|{'OTHER_EXCEPTION'}
        for row in diagnostics:
            if not isinstance(row,dict): continue
            operation=row.get('operation')
            if operation not in _PROBE_OPERATIONS or row.get('predicate')!=_PROBE_OPERATIONS[operation]: continue
            result['diagnostics'].append({'operation':operation,'predicate':_PROBE_OPERATIONS[operation],
                'category':row.get('category') if row.get('category') in categories else 'OTHER_EXCEPTION',
                'errno':_probe_error_number(row.get('errno')),'winerror':_probe_error_number(row.get('winerror'))})
    return result

def _validate_acquisition_material(helper, native, physical):
    # Shape-check each actual read without pretending duplicated reads are evidence.
    helper._require(isinstance(native,list) and len(native)==2,'two config contexts required')
    mapped=helper._physical_map(physical)
    filtered=[helper._filter_native(row,mapped) for row in native]
    helper._require(len({row['cwd'] for row in filtered})==2,'duplicate native cwd')
    paths={entry['path'] for row in filtered for layer in row['layers'] for entry in layer['files']}
    helper._require(paths==set(mapped),'unrelated or missing physical evidence')

def _acquisition_identity(observation):
    return {'owner':owner_identity(observation['owner']),
        'stable':{key:value for key,value in stable(observation).items() if key!='configs'},
        'native_thread':observation['native_thread']}


def unique(pairs):
    result={}
    for key,value in pairs:
        if key in result: raise Refusal("duplicate JSON key")
        result[key]=value
    return result

def strict_json(raw):
    def constant(value): raise Refusal("nonfinite JSON")
    try: return json.loads(raw,object_pairs_hook=unique,parse_constant=constant)
    except (ValueError,UnicodeError,RecursionError) as error: raise Refusal("invalid bounded JSON") from error

def digest(b): return hashlib.sha256(b).hexdigest()

def canonical(v): return json.dumps(v, sort_keys=True, separators=(",", ":")).encode()

def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()

def file_observation(p):
    p = pathlib.Path(p)
    if not p.is_file(): return {"path": str(p), "exists": False}
    b = p.read_bytes()
    return {"path": str(p), "exists": True, "bytes": len(b), "sha256": digest(b), "mtime_ns": p.stat().st_mtime_ns}

def argv(command_line):
    n = ctypes.c_int()
    parse = ctypes.windll.shell32.CommandLineToArgvW
    parse.argtypes = [ctypes.c_wchar_p, ctypes.POINTER(ctypes.c_int)]
    parse.restype = ctypes.POINTER(ctypes.c_wchar_p)
    values = parse(command_line, ctypes.byref(n))
    if not values: return []
    try: return [values[i] for i in range(n.value)]
    finally: ctypes.windll.kernel32.LocalFree(values)

def command_classification(raw):
    words = argv(raw)
    overrides, feature_values, flags = [], [], []
    for i, word in enumerate(words[1:], 1):
        if word in ("-c", "--config") and i + 1 < len(words):
            value = words[i + 1]
            key, sep, val = value.partition("=")
            overrides.append({"key": key, "assignment_sha256": digest(value.encode())})
            if key.strip() == "features." + FEATURE:
                feature_values.append(val.strip() if val.strip() in ("true", "false") else "UNKNOWN")
        if word in ("--enable", "--disable") and i + 1 < len(words) and words[i + 1] == FEATURE:
            feature_values.append("true" if word == "--enable" else "false")
        if word.startswith("-") and "=" not in word: flags.append(word)
    return {"command_line_sha256": digest(raw.encode()), "subcommand_app_server": "app-server" in words, "flags": sorted(set(flags)), "unclassified_assignment_argument": any(w.startswith('-') and '=' in w for w in words), "override_keys_and_hashes": overrides, "feature_assignments": feature_values, "profile_argument_present": any(x in words for x in ("-p", "--profile")), "raw_command_line_persisted": False}

def processes(*, deadline=None):
    # Only native command lines are classified; other processes contribute
    # PID/start/path ancestry metadata, never environment or command content.
    script = "$p=Get-CimInstance Win32_Process; @($p | ForEach-Object { [pscustomobject]@{pid=$_.ProcessId;parent_pid=$_.ParentProcessId;name=$_.Name;path=$_.ExecutablePath;created_utc=$(if ($_.CreationDate) {$_.CreationDate.ToUniversalTime().ToString('o')} else {$null});command_line=$(if ($_.Name -eq 'codex.exe') {$_.CommandLine} else {''})} }) | ConvertTo-Json -Depth 3 -Compress"
    run = subprocess.run(["powershell.exe", "-NoProfile", "-Command", script], capture_output=True, text=True, timeout=_observation_remaining(deadline,10), creationflags=subprocess.CREATE_NO_WINDOW)
    if run.returncode: raise RuntimeError("process inspection failed; stderr withheld")
    rows = json.loads(run.stdout or "[]")
    if isinstance(rows, dict): rows = [rows]
    parents = {x["pid"]: x for x in rows}
    def chain(row):
        result=[];seen={row['pid']};ident=row['parent_pid']
        while ident in parents and ident not in seen:
            seen.add(ident);ancestor=parents[ident]
            result.append({k:ancestor[k] for k in ('pid','parent_pid','name','path','created_utc')})
            ident=ancestor['parent_pid']
        return result
    output = []
    for r in rows:
        if r["name"].lower() != "codex.exe": continue
        parent = parents.get(r["parent_pid"])
        classified = command_classification(r.get("command_line") or "")
        entry = {k: r[k] for k in ("pid", "parent_pid", "name", "path", "created_utc")}
        entry.update(classified)
        entry["desktop_owned"] = bool(parent and parent["name"] == "ChatGPT.exe" and "OpenAI.Codex_" in (parent["path"] or ""))
        entry["parent"] = {k: parent[k] for k in ("pid", "path", "created_utc")} if parent else None
        entry['ancestry']=chain(r)
        desktop=next((a for a in entry['ancestry'] if a['name']=='ChatGPT.exe' and 'OpenAI.Codex_' in (a['path'] or '')),None)
        entry['desktop_descendant']=desktop is not None
        entry['desktop_process_tree']=[]
        if desktop:
            for process in rows:
                if process['pid']==desktop['pid'] or any(a['pid']==desktop['pid'] for a in chain(process)):
                    entry['desktop_process_tree'].append({k:process[k] for k in ('pid','parent_pid','name','path','created_utc')})
            entry['desktop_process_tree'].sort(key=lambda p:p['pid'])
        entry["executable"] = file_observation(r["path"]) if r["path"] else None
        output.append(entry)
    return sorted(output,key=lambda p:p['pid'])

def native_read(binary, cwd, methods, env, *, deadline=None):
    start = time.monotonic()
    _observation_remaining(deadline,45)
    p = None; probe_pid = None; q = None; stderr_hash = None
    counts = {"stdout": 0, "stderr": 0}
    terminal = {name: {"failure": None, "eof": False, "done": False} for name in counts}
    readers, started_readers, sent, returned, diagnostics = [], [], [], [], []
    failure = None; material_error = None; operation = 'PREPARE'
    streams_complete = False; process_terminated = False; exit_code = None
    def note(operation, error, *, unexpected=True):
        nonlocal material_error, failure
        diagnostics.append(_probe_exception(operation,error))
        if unexpected:
            if material_error is None: material_error=error
            if failure is None: failure='native probe operation failed'
    def drain(stream, name):
        state = terminal[name]
        def failed(message):
            state["failure"] = message
            q.put({"probe_failure": message})
        try:
            for line in iter(lambda: stream.readline(LIMIT + 1), b""):
                counts[name] += len(line)
                if counts[name] > LIMIT:
                    failed("response byte limit"); return
                if name == "stderr": stderr_hash.update(line); continue
                try:
                    row = strict_json(line)
                    if not isinstance(row, dict): raise Refusal("protocol row is not an object")
                except (ValueError, Refusal):
                    failed("invalid protocol JSON"); return
                q.put(row)
            state["eof"] = True
        except Exception:
            failed("native stream read failed")
        finally:
            state["done"] = True
            if name == "stdout": q.put({"probe_failure": "native stdout closed"})
    def request(value):
        _observation_remaining(deadline,45)
        assert value["method"] in {"initialize", "initialized", "config/read", "hooks/list", "thread/read"}
        sent.append(value)
        p.stdin.write(canonical(value) + b"\n"); p.stdin.flush()
        if "id" not in value: return None
        while True:
            remaining = min(45 - (time.monotonic() - start), _observation_remaining(deadline,45))
            if remaining <= 0: raise TimeoutError("45 second native deadline")
            response = q.get(timeout=remaining)
            if "probe_failure" in response: raise RuntimeError(response["probe_failure"])
            if response.get("id") == value["id"]: return response
    try:
        q = queue.Queue(); stderr_hash = hashlib.sha256()
        operation = 'LAUNCH'
        args = [str(binary), "-c", 'model_reasoning_effort="high"', "app-server", "--stdio"]
        p = subprocess.Popen(args, cwd=cwd, env=env, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=subprocess.CREATE_NO_WINDOW)
        probe_pid = p.pid
        operation = 'THREAD_CREATE'
        for stream,name in ((p.stdout,'stdout'),(p.stderr,'stderr')):
            readers.append(threading.Thread(target=drain,args=(stream,name),daemon=True))
        operation = 'THREAD_START'
        for t in readers:
            # A start call can raise after partially starting its thread.
            started_readers.append(t); t.start()
        operation = 'REQUEST'
        init = request({"id": 1, "method": "initialize", "params": {"clientInfo": {"name": "implementaudit_producer_epoch_readback", "version": "1.0"}}})
        if "error" in init: raise RuntimeError("native initialize error")
        request({"method": "initialized"})
        for n, (method, params, schema_name) in enumerate(methods, 2):
            response = request({"id": n, "method": method, "params": params})
            if "error" in response: returned.append({"method": method, "error": response["error"]}); continue
            if not isinstance(response.get("result"), dict): raise Refusal("native result is not an object")
            returned.append({"method": method, "params": params, "result": response["result"], "response_sha256": digest(canonical(response))})
    except BaseException as error:
        note(operation,error,unexpected=(operation!='REQUEST' or not isinstance(error,Exception)
                                        or isinstance(error,AcquisitionFailure)))
        failure = 'native request failed' if operation=='REQUEST' else 'native probe setup failed'
    finally:
        if p is not None:
            # Every created probe reaches this cleanup, including setup failures.
            # Each failed step remains observable without skipping later steps.
            try: p.stdin.close()
            except (BrokenPipeError,OSError) as error:
                note('STDIN_CLOSE',error,unexpected=False)  # Existing tolerated close case.
            except BaseException as error: note('STDIN_CLOSE',error)
            terminate = False
            try: p.wait(timeout=3)
            except subprocess.TimeoutExpired as error:
                note('WAIT',error,unexpected=False); terminate=True
            except BaseException as error:
                note('WAIT',error); terminate=True
            if terminate:
                try:
                    if type(probe_pid) is not int or probe_pid<=0: raise Refusal('created probe PID unavailable')
                    subprocess.run(["taskkill.exe", "/PID", str(probe_pid), "/T", "/F"], capture_output=True, timeout=5, creationflags=subprocess.CREATE_NO_WINDOW)
                except (OSError,subprocess.TimeoutExpired) as error:
                    note('TERMINATE',error,unexpected=False); failure="native probe cleanup command failed"
                except BaseException as error:
                    note('TERMINATE',error); failure="native probe cleanup command failed"
                try: p.wait(timeout=2)
                except subprocess.TimeoutExpired as error:
                    note('WAIT_AFTER_TERMINATE',error,unexpected=False); failure="native probe cleanup unresolved"
                except BaseException as error: note('WAIT_AFTER_TERMINATE',error)
            drain_deadline = time.monotonic() + 2
            drain_unproved = False
            for t in started_readers:
                try: t.join(timeout=max(0,drain_deadline-time.monotonic()))
                except BaseException as error:
                    note('DRAIN_JOIN',error); drain_unproved=True
            for t in readers:
                try: drain_unproved = t.is_alive() or drain_unproved
                except BaseException as error:
                    note('DRAIN_STATUS',error); drain_unproved=True
            streams_complete = (not drain_unproved and len(readers)==2
                                and all(row['done'] for row in terminal.values()))
            if not streams_complete:
                failure = "native stream drain incomplete"
            else:
                stream_failure = next((row['failure'] for row in terminal.values() if row['failure']),None)
                if stream_failure is not None: failure=stream_failure
                elif not all(row['eof'] for row in terminal.values()): failure="native stream EOF unproved"
            try:
                exit_code = p.poll(); process_terminated = exit_code is not None
            except BaseException as error:
                note('FINALIZE',error); exit_code=None; process_terminated=False
            if not process_terminated: failure="native probe cleanup unresolved"
    elapsed = None; stderr_digest = None
    try:
        elapsed = time.monotonic()-start
        if stderr_hash is not None: stderr_digest=stderr_hash.hexdigest()
    except BaseException as error: note('FINALIZE',error)
    protocol = {"calls": sent, "probe_pid": probe_pid, "process_terminated": process_terminated,
        "exit_code": exit_code, "failure": failure, "elapsed_seconds": elapsed, "bytes": dict(counts),
        "streams_complete": streams_complete, "stream_status": {name:dict(row) for name,row in terminal.items()},
        "stderr_sha256": stderr_digest, "compatibility_override": 'model_reasoning_effort="high"',
        "raw_responses_persisted": False, "diagnostics": diagnostics}
    if material_error is not None:
        error = material_error if isinstance(material_error,AcquisitionFailure) else AcquisitionFailure(
            'INTERRUPTED' if isinstance(material_error,KeyboardInterrupt) else 'UNKNOWN_FAILURE')
        error.probe_protocol=protocol
        raise error from None
    return returned,protocol


def filter_config(result):
    config = result["config"]
    layers = []
    for layer in result.get("layers") or []:
        name = layer["name"]
        files = []
        if name.get("file"): files.append(file_observation(name["file"]))
        if name.get("dotCodexFolder"): files.append(file_observation(pathlib.Path(name["dotCodexFolder"]) / "config.toml"))
        layers.append({"source": name, "version": layer["version"], "disabledReason": layer.get("disabledReason"), "feature": (layer.get("config") or {}).get("features", {}).get(FEATURE), "config_sha256": digest(canonical(layer.get("config"))), "files": files})
    return {"feature": config.get("features", {}).get(FEATURE), "layers": layers, "full_config_sha256": digest(canonical(config)), "feature_origin": result.get("origins", {}).get("features." + FEATURE), "raw_config_persisted": False}


def native_path(value, session_root):
    if not isinstance(value,str): raise Refusal('native task has no path')
    found={}
    root=pathlib.Path(session_root).resolve()
    for text in (value,value.replace('\\\\','\\')):
        p=pathlib.Path(text.removeprefix('\\\\?\\'))
        if p.is_file():
            physical=p.resolve()
            if not physical.is_relative_to(root): raise Refusal('native path outside session store')
            found[os.path.normcase(str(physical))]=physical
    if len(found)!=1: raise Refusal('native path does not resolve uniquely')
    return next(iter(found.values()))


def stream_frontier(value, session_root, task, previous=None, *, retain_suffix=True):
    """Hash the old byte prefix without decoding its conversation rows."""
    path=native_path(value,session_root)
    expected=0
    if previous is not None:
        expected=previous.get('complete_prefix_bytes')
        if (type(expected) is not int or expected<=0 or previous.get('path')!=str(path)
                or not isinstance(previous.get('complete_prefix_sha256'),str)):
            raise Refusal('invalid prior native frontier')
    with path.open('rb') as stream:
        stat=os.fstat(stream.fileno())
        if stat.st_size<expected or stat.st_size>512*1024*1024: raise Refusal('native prefix truncated or oversized')
        whole=hashlib.sha256();old=hashlib.sha256();count=0;offset=0;first=None;suffix=[];suffix_size=0;last=b''
        while offset<stat.st_size:
            chunk=stream.read(min(1024*1024,stat.st_size-offset))
            if not chunk: raise Refusal('native file shortened during read')
            whole.update(chunk)
            if offset<expected: old.update(chunk[:expected-offset])
            count+=chunk.count(b'\n')
            if first is None:
                last+=chunk
                split=last.find(b'\n')
                if split<0 and len(last)>131072: raise Refusal('native session metadata oversized')
                if split>=0:
                    first=last[:split+1]
                    if len(first)>131072: raise Refusal('native session metadata oversized')
                    last=b''
            if retain_suffix and previous is not None and offset+len(chunk)>expected:
                new=chunk[max(0,expected-offset):];suffix_size+=len(new)
                if suffix_size>1048576: raise Refusal('native current suffix exceeds 1 MiB')
                suffix.append(new)
            offset+=len(chunk)
            tail=chunk[-1:]
        if not first or tail!=b'\n': raise Refusal('native file has partial final record')
        after=os.fstat(stream.fileno())
        if (after.st_size,after.st_mtime_ns,after.st_ino)!=(stat.st_size,stat.st_mtime_ns,stat.st_ino):
            raise Refusal('native file changed during bounded read')
    if previous is not None and old.hexdigest()!=previous['complete_prefix_sha256']:
        raise Refusal('native saved prefix changed')
    meta=strict_json(first)
    payload=meta.get('payload') if isinstance(meta,dict) else None
    if (meta.get('type')!='session_meta' or type(meta.get('ordinal')) is not int or meta['ordinal']!=0
            or not isinstance(payload,dict) or payload.get('id')!=task
            or payload.get('cli_version')!='0.153.4' or not isinstance(payload.get('session_id'),str)):
        raise Refusal('native task/session/version metadata differs')
    return {'path':str(path),'complete_prefix_bytes':offset,'complete_prefix_sha256':whole.hexdigest(),
            'complete_rows':count,'session_id':payload['session_id'],'task_id':payload['id'],'native_session_cwd':payload.get('cwd'),
            'session_meta_sha256':digest(first),'session_meta_wire':first,'suffix':b''.join(suffix)}


def verify_historical_prefix(value, session_root, task, previous):
    """Verify only the exact frozen native prefix, never the growing live tail.

    Two bounded hash passes detect an already-read prefix rewritten during the
    first pass. Tail growth does not change this historical custody predicate.
    Current snapshot and latest-input readers retain their independent guards.
    """
    import stat
    path=native_path(value,session_root)
    if not isinstance(value,str) or pathlib.Path(value)!=path:
        raise Refusal('historical native input is not its saved physical path')
    size=previous.get('complete_prefix_bytes');rows=previous.get('complete_rows')
    expected=previous.get('complete_prefix_sha256')
    if (type(size) is not int or not 0<size<=512*1024*1024
            or type(rows) is not int or rows<1 or previous.get('path')!=str(path)
            or not isinstance(expected,str) or len(expected)!=64
            or any(c not in '0123456789abcdef' for c in expected)):
        raise Refusal('historical native prefix binding malformed')
    def check_path(opened):
        physical=native_path(value,session_root)
        link=path.lstat();current=path.stat()
        if (physical!=path or not stat.S_ISREG(link.st_mode)
                or bool(getattr(link,'st_file_attributes',0)&0x400)
                or (opened.st_dev,opened.st_ino)!=(current.st_dev,current.st_ino)
                or current.st_size<size):
            raise Refusal('historical native prefix path/handle custody changed')
    # Unbuffered bounded reads ensure no application read requests live-tail
    # bytes, including when the saved boundary lies inside a normal I/O block.
    with path.open('rb',buffering=0) as stream:
        opened=os.fstat(stream.fileno())
        if not stat.S_ISREG(opened.st_mode) or opened.st_size<size:
            raise Refusal('historical native prefix truncated or nonregular')
        check_path(opened)
        first=None
        for _ in range(2):
            stream.seek(0);offset=0;count=0;hashed=hashlib.sha256();last=b'';metadata=None
            while offset<size:
                chunk=stream.read(min(1024*1024,size-offset))
                if not chunk:raise Refusal('historical native prefix shortened during read')
                hashed.update(chunk);count+=chunk.count(b'\n');last=chunk[-1:]
                if metadata is None:
                    split=chunk.find(b'\n')
                    if split<0 or split+1>131072:
                        raise Refusal('historical native session metadata oversized or partial')
                    metadata=chunk[:split+1]
                offset+=len(chunk)
            if last!=b'\n' or count!=rows:
                raise Refusal('historical native prefix row boundary/count differs')
            if hashed.hexdigest()!=expected:
                raise Refusal('historical native prefix bytes changed')
            if first is not None and metadata!=first:
                raise Refusal('historical native metadata changed between passes')
            first=metadata
            after=os.fstat(stream.fileno())
            if (after.st_dev,after.st_ino)!=(opened.st_dev,opened.st_ino) or after.st_size<size:
                raise Refusal('historical native prefix handle changed or truncated')
            check_path(opened)
    meta=strict_json(first);payload=meta.get('payload') if isinstance(meta,dict) else None
    if (not isinstance(meta,dict) or meta.get('type')!='session_meta'
            or type(meta.get('ordinal')) is not int or meta['ordinal']!=0
            or not isinstance(payload,dict) or payload.get('id')!=task
            or payload.get('cli_version')!='0.153.4'
            or not isinstance(payload.get('session_id'),str)
            or payload['session_id']!=previous.get('session_id')
            or digest(first)!=previous.get('session_meta_sha256')
            or payload.get('cwd')!=previous.get('native_session_cwd')):
        raise Refusal('historical native task/session/version/metadata differs')
    return {'path':str(path),'complete_prefix_bytes':size,'complete_prefix_sha256':expected,
            'complete_rows':rows,'session_id':payload['session_id'],'task_id':task,
            'session_meta_sha256':digest(first),'native_session_cwd':payload.get('cwd')}


def read_native_turn_slice(value, session_root, task, previous):
    """Select latest native user-input occurrence; bytes alone confer no authority.

    Stream old bytes without decoding conversation content. Scan every later
    row, retaining only task markers and recovery developer candidates. Later
    internal goal continuation cannot displace a real user input. The existing
    route selector still validates candidate semantics and native attribution.
    """
    path=native_path(value,session_root)
    expected=previous.get('complete_prefix_bytes');prior_rows=previous.get('complete_rows')
    if (type(expected) is not int or expected<=0 or type(prior_rows) is not int or prior_rows<1
            or previous.get('path')!=str(path)):
        raise Refusal('invalid selected-turn prior frontier')
    offset=0;ordinal=0;old=hashlib.sha256();whole=hashlib.sha256();meta_wire=None
    first_new_ordinal=None;next_new_ordinal=None
    active=None;seen=set();active_rows=[];active_native=0;active_bytes=0
    selected=None;selected_rows=[];selected_native=0;selected_bytes=0;latest_input_ordinal=None
    with path.open('rb') as stream:
        stat=os.fstat(stream.fileno())
        if stat.st_size<expected or stat.st_size>512*1024*1024:
            raise Refusal('native selected-turn stream truncated or oversized')
        # Inspect only the last bounded saved row's mechanical envelope. Native
        # 0.153.4 can repeat this ordinal exactly once at measured restart.
        tail_start=max(0,expected-131073);stream.seek(tail_start)
        tail=stream.read(expected-tail_start)
        if not tail.endswith(b'\n'):raise Refusal('saved frontier lacks final record boundary')
        split=tail.rfind(b'\n',0,len(tail)-1)
        if split<0 and tail_start:raise Refusal('last saved native row exceeds bound')
        last_wire=tail[split+1:]
        if len(last_wire)>131072 or b'\r' in last_wire or b'\x00' in last_wire:
            raise Refusal('last saved native row malformed or oversized')
        last_row=strict_json(last_wire)
        if (not isinstance(last_row,dict) or set(last_row) not in ({'timestamp','ordinal','type','payload'},
                {'timestamp','ordinal','type','payload','metadata'})
                or type(last_row.get('ordinal')) is not int or last_row['ordinal']<0):
            raise Refusal('last saved native ordinal is malformed')
        last_old_ordinal=last_row['ordinal'];stream.seek(0)
        while offset<stat.st_size:
            # Old prefix is hashed in bounded chunks; do not parse old messages.
            if offset and offset<expected:
                raw=stream.read(min(1024*1024,expected-offset));old.update(raw);whole.update(raw)
                ordinal+=raw.count(b'\n');offset+=len(raw)
                if not raw:raise Refusal('native saved prefix shortened')
                continue
            line=stream.readline(min(8*1024*1024+1,stat.st_size-offset+1))
            if not line or len(line)>8*1024*1024 or not line.endswith(b'\n') or b'\r' in line or b'\x00' in line:
                raise Refusal('native selected-turn row malformed or oversized')
            if offset<expected:
                if offset+len(line)>expected:raise Refusal('native frontier is not at a record boundary')
                old.update(line)
            whole.update(line);offset+=len(line)
            row=strict_json(line)
            if (not isinstance(row,dict) or set(row) not in ({'timestamp','ordinal','type','payload'},
                    {'timestamp','ordinal','type','payload','metadata'})
                    or type(row.get('ordinal')) is not int or row['ordinal']<0):
                raise Refusal('native selected-turn ordinal or envelope differs')
            if meta_wire is None:
                if len(line)>131072:raise Refusal('selected native session metadata exceeds bound')
                if row['ordinal']!=0:raise Refusal('native session metadata ordinal differs')
            else:
                if first_new_ordinal is None:
                    if (ordinal!=prior_rows or old.hexdigest()!=previous.get('complete_prefix_sha256')
                            or row['ordinal'] not in (last_old_ordinal,last_old_ordinal+1)
                            or row['ordinal']<=0):
                        raise Refusal('native restart byte-boundary ordinal differs')
                    if row['ordinal']==last_old_ordinal and (row['type']!='event_msg'
                            or not isinstance(row['payload'],dict) or row['payload'].get('type')!='task_started'
                            or 'metadata' in row):
                        raise Refusal('repeated restart ordinal is not a native task start')
                    first_new_ordinal=row['ordinal'];next_new_ordinal=first_new_ordinal
                if row['ordinal']!=next_new_ordinal:
                    raise Refusal('native new suffix ordinal is not contiguous')
                next_new_ordinal+=1
            ordinal+=1
            if ordinal>1000000:raise Refusal('native selected-turn scan row ceiling')
            payload=row['payload']
            if meta_wire is None:
                if (row['type']!='session_meta' or not isinstance(payload,dict) or payload.get('id')!=task
                        or payload.get('session_id')!=previous.get('session_id')
                        or payload.get('cli_version')!='0.153.4'):
                    raise Refusal('native selected-turn session metadata differs')
                meta_wire=line;continue
            if ordinal==prior_rows+1 and old.hexdigest()!=previous.get('complete_prefix_sha256'):
                raise Refusal('native selected-turn saved prefix changed')
            if not isinstance(payload,dict):raise Refusal('native selected-turn payload malformed')
            if row['type']=='event_msg' and payload.get('type')=='task_started':
                if len(line)>131072:raise Refusal('selected native task marker exceeds bound')
                turn=payload.get('turn_id')
                if not isinstance(turn,str) or not turn or turn in seen:
                    raise Refusal('native selected-turn start absent or duplicate')
                if 'metadata' in row:raise Refusal('native task start provenance ambiguous')
                seen.add(turn);active=turn;active_rows=[line];active_native=0;active_bytes=len(line)
                continue
            if row['type']=='turn_context' and payload.get('turn_id')!=active:
                raise Refusal('native turn context disagrees with active occurrence')
            if row['type']!='response_item':continue
            role=payload.get('role');metadata=payload.get('internal_chat_message_metadata_passthrough')
            if role=='user':
                if payload.get('type')!='message':raise Refusal('native user input shape differs')
                if not isinstance(metadata,dict) or metadata.get('turn_id')!=active or not active:
                    raise Refusal('native user input has no matching task occurrence')
                kinds=metadata.get('content_item_kinds')
                if kinds==['user.text']:
                    if 'metadata' in row:raise Refusal('native user input provenance ambiguous')
                    selected=active;selected_rows=list(active_rows);selected_native=active_native
                    selected_bytes=active_bytes;latest_input_ordinal=row['ordinal']
                elif kinds not in (['goal.internal_context'],['environments.environment_context']):
                    raise Refusal('unsupported native user input kind')
                continue
            if role!='developer':continue
            recovery=False
            for item in payload.get('content',[]) if isinstance(payload.get('content'),list) else []:
                if not isinstance(item,dict) or not isinstance(item.get('text'),str):continue
                text=item['text']
                if 'implementaudit.recovery-host-input.v1' in text:recovery=True;break
                try:decoded=strict_json(text)
                except Refusal as error:
                    # Match the unchanged selector: ordinary non-JSON text
                    # is not a candidate; ambiguous/duplicate/nonfinite or
                    # excessive-depth developer JSON must not disappear.
                    if isinstance(error.__cause__,json.JSONDecodeError):continue
                    raise Refusal('native developer JSON is ambiguous or exceeds parser limits') from error
                if isinstance(decoded,dict) and decoded.get('schema')=='implementaudit.recovery-host-input.v1':
                    recovery=True;break
            hook_kind=isinstance(metadata,dict) and metadata.get('content_item_kinds')==['hooks.additional_context']
            if hook_kind and not recovery:raise Refusal('unrecognized native recovery hook content')
            if not recovery:continue
            if len(line)>131072:raise Refusal('selected native recovery row exceeds bound')
            if not active or not isinstance(metadata,dict) or metadata.get('turn_id')!=active:
                raise Refusal('native recovery row is outside matching task occurrence')
            active_rows.append(line);active_bytes+=len(line)
            client=row.get('metadata')=={'client_authored':True}
            if not client:active_native+=1
            if active_bytes>1048576 or len(active_rows)>4095:
                raise Refusal('selected native evidence slice exceeds bound')
            if active==selected:
                selected_rows=list(active_rows);selected_native=active_native;selected_bytes=active_bytes
        after=os.fstat(stream.fileno())
        if (stat.st_size,stat.st_mtime_ns,stat.st_ino)!=(after.st_size,after.st_mtime_ns,after.st_ino):
            raise Refusal('native selected-turn stream changed during read')
    if old.hexdigest()!=previous.get('complete_prefix_sha256') or prior_rows>ordinal:
        raise Refusal('native selected-turn saved prefix changed')
    if not selected or selected_native!=1 or latest_input_ordinal is None:
        raise Refusal('latest native user input has absent or ambiguous recovery hook')
    native_candidates=[strict_json(line) for line in selected_rows[1:]
                       if strict_json(line).get('metadata')!={'client_authored':True}]
    if len(native_candidates)!=1 or native_candidates[0]['ordinal']<=latest_input_ordinal:
        raise Refusal('native recovery hook predates latest user input')
    raw=meta_wire+b''.join(selected_rows)
    if len(raw)>1048576:raise Refusal('native selected evidence including metadata oversized')
    return {'raw':raw,'native_thread_id':task,'native_session_id':previous['session_id'],
        'native_turn_id':selected,'after_ordinal':first_new_ordinal-1,
        'readback_prefix':{'path':str(path),'complete_prefix_bytes':offset,'complete_prefix_sha256':whole.hexdigest(),
            'complete_rows':ordinal,'session_id':previous['session_id'],'task_id':task,
            'session_meta_sha256':digest(meta_wire),'native_session_cwd':strict_json(meta_wire)['payload'].get('cwd')}}


def desktop_parent_binding(owner):
    """Resolve the ASAR from the actual CIM parent, never an unrelated constant path."""
    parent=owner.get('parent')
    if not isinstance(parent,dict) or not parent.get('path'): raise Refusal('native parent unavailable')
    path=pathlib.Path(__file__).with_name('codex-native-desktop-binding.py')
    raw=path.read_bytes()
    if digest(raw)!='3f66a37603609186fbd6b27e0926a0801ccf7b2b87f37a32c0f40e01431ebbf5':
        raise Refusal('desktop observation helper source differs')
    spec=importlib.util.spec_from_file_location('_native_desktop_binding',path)
    helper=importlib.util.module_from_spec(spec);exec(compile(raw,str(path),'exec'),helper.__dict__)
    binding=helper.observe_parent(parent['path'])
    if not helper.parent_matches({**parent,'source_binding':binding},file_observation(helper.ASAR)):
        raise Refusal('actual parent executable/version/package/derived ASAR is foreign')
    if path.read_bytes()!=raw: raise Refusal('desktop observation helper changed')
    return binding


def durable(value):
    return {key:item for key,item in value.items() if key not in {'session_meta_wire','suffix'}}


def owner_identity(owner):
    # Non-native UI/tool descendants may come and go. Native descendants are
    # separately refused by post-restart snapshot unless the exact owner.
    return {key:value for key,value in owner.items() if key!='desktop_process_tree'}


def stable(observation):
    return {key:observation[key] for key in ('binary','parent_binding','configs','hooks','recovery_hook_binding','package_files','source_identity','parameters')}


def recovery_hook_binding(plugin_root, plugin_id, hook):
    """Bind the exact native command/options to the pinned adjacent input adapter."""
    root=pathlib.Path(plugin_root).resolve()
    source=root/'hooks/hooks.json';raw=source.read_bytes()
    if len(raw)>131072: raise Refusal('recovery hook source is oversized')
    definition=strict_json(raw)
    unix='/usr/bin/python3 -I -S -B "${PLUGIN_ROOT}/skills/implementaudit/scripts/codex-recovery-prompt-input.py"'  # Native plugin uses the source repo-shaped package layout.
    windows='C:\\Windows\\py.exe -3 -I -S -B "${env:PLUGIN_ROOT}\\skills\\implementaudit\\scripts\\codex-recovery-prompt-input.py"'
    expected={'hooks':[{'type':'command','command':unix,'commandWindows':windows,
        'statusMessage':'Observing IMPLEMENTAUDIT recovery input','additionalContextLimit':5000,'timeout':60}]}
    if (not isinstance(definition,dict) or not isinstance(definition.get('hooks'),dict)
            or definition['hooks'].get('UserPromptSubmit')!=[expected]):
        raise Refusal('recovery hook source definition differs from qualified handler')
    fields={'key':plugin_id+':hooks/hooks.json:user_prompt_submit:0:0','eventName':'userPromptSubmit',
        'handlerType':'command','command':windows,'async':False,'matcher':None,'timeoutSec':60,
        'statusMessage':'Observing IMPLEMENTAUDIT recovery input','additionalContextLimit':5000,
        'source':'plugin','pluginId':plugin_id,'enabled':True,'isManaged':False,'trustStatus':'trusted'}
    if (any(type(hook.get(key)) is not type(value) or hook.get(key)!=value for key,value in fields.items())
            or pathlib.Path(hook.get('sourcePath','')).resolve()!=source
            or not isinstance(hook.get('currentHash'),str)
            or len(hook['currentHash'])!=71 or not hook['currentHash'].startswith('sha256:')
            or any(c not in '0123456789abcdef' for c in hook['currentHash'][7:])):
        raise Refusal('native recovery handler does not match qualified source/options')
    adapter=root/'skills/implementaudit/scripts/codex-recovery-prompt-input.py'  # Native plugin uses the source repo-shaped package layout.
    if digest(adapter.read_bytes())!=EXPECTED_RECOVERY_INPUT_ADAPTER_SHA256:
        raise Refusal('native recovery command adapter source differs')
    if source.read_bytes()!=raw: raise Refusal('native recovery definition changed during binding')
    return {'hook_source_sha256':digest(raw),'adapter_sha256':EXPECTED_RECOVERY_INPUT_ADAPTER_SHA256,
            'native_hook_key':hook['key'],'native_current_hash':hook['currentHash']}


# Exact optional successor comparison. This remains a consumer, never an event
# producer or a replacement for native observation and physical H0 readback.
CONFIG_TRANSITION_DIGEST = '8bdac47c22a66d0177d183ae51ece1bfb5ed3dd8fac2b43712d74bbfba553406'
SOURCE_TRANSITION_DIGEST = '15226d355a4d8a7ead2474125d9fb5039727f7724980a1121f0dedc8737e2ecc'


def load_transition_helper(name, expected):
    path = pathlib.Path(__file__).with_name(name)
    raw = path.read_bytes()
    if digest(raw) != expected: raise Refusal('reviewed transition helper source differs')
    import types
    module = types.ModuleType('_recovery_transition_' + expected)
    module.__file__ = str(path)
    exec(compile(raw, str(path), 'exec'), module.__dict__)
    return module


def load_successor_spec(path, expected):
    if (not isinstance(expected, str) or len(expected) != 64
            or any(c not in '0123456789abcdef' for c in expected)):
        raise Refusal('exact reviewed successor specification digest required')
    path = pathlib.Path(path)
    if path.stat().st_size > 8 * 1024 * 1024: raise Refusal('successor specification oversized')
    raw = path.read_bytes()
    if digest(raw) != expected: raise Refusal('review-bound successor specification differs')
    spec = strict_json(raw)
    if (not isinstance(spec, dict) or set(spec) != {
            'schema', 'source_transition', 'source_transition_sha256', 'config_witness', 'review_binding'}
            or spec['schema'] != 'implementaudit.observation-successor-spec.v1'):
        raise Refusal('successor specification schema differs')
    review = spec['review_binding']
    if (not isinstance(spec['source_transition'], dict)
            or not isinstance(review, dict) or set(review) != {'subject_sha256', 'report_sha256'}
            or any(not isinstance(v, str) or len(v) != 64 or any(c not in '0123456789abcdef' for c in v)
                   for v in review.values())
            or review['subject_sha256'] != spec['source_transition'].get('review_subject_sha256')):
        raise Refusal('exact independent review binding missing')
    if digest(canonical(spec['source_transition'])) != spec['source_transition_sha256']:
        raise Refusal('source transition is not the review-bound receipt')
    return spec


def epoch_file_pins(directory):
    result = []
    for stage in ('before', 'stopped', 'restarted'):
        path = pathlib.Path(directory) / (stage + '.json')
        if path.stat().st_size > 8 * 1024 * 1024: raise Refusal('epoch observation oversized')
        raw = path.read_bytes()
        result.append({'stage': stage, 'bytes': len(raw), 'sha256': digest(raw)})
    return result


def map_hook_source_paths(hooks, old_root, new_root):
    # Only the exact plugin hook definition path is relocatable. Other fields,
    # commands, hashes, paths and other plugins remain byte-for-byte semantic data.
    value = strict_json(canonical(hooks))
    old = str(pathlib.Path(old_root) / 'hooks/hooks.json')
    new = str(pathlib.Path(new_root) / 'hooks/hooks.json')
    if not isinstance(value, list): raise Refusal('hook population malformed')
    mapped = 0
    for entry in value:
        if not isinstance(entry, dict) or not isinstance(entry.get('hooks'), list):
            raise Refusal('hook context malformed')
        for hook in entry['hooks']:
            if not isinstance(hook, dict): raise Refusal('hook entry malformed')
            if hook.get('sourcePath') == old:
                hook['sourcePath'] = new
                mapped += 1
    if not mapped: raise Refusal('exact predecessor hook source path absent')
    return value


def validate_observation_successor(epoch, current, spec, pins, raw_reads, physical_reads):
    """Pure bounded comparison of original facts and a new consumer observation.

    Reviewed custody of the spec/digest is supplied by the install/composition
    owner. This function does not authenticate a self-asserted review JSON field.
    The concrete observer below obtains independent native reads and source facts.
    """
    source = load_transition_helper('codex-recovery-source-transition.py', SOURCE_TRANSITION_DIGEST)
    config = load_transition_helper('codex-recovery-config-transition.py', CONFIG_TRANSITION_DIGEST)
    receipt = spec['source_transition']
    try:
        comparison = source.validate_source_transition(epoch['package_files'], current['package_files'], receipt,
            expected_receipt_sha256=spec['source_transition_sha256'], epoch_files=pins)
        old_root, new_root = receipt['predecessor_root'], receipt['successor_root']
        if (epoch['parameters']['plugin_root'] != old_root or current['parameters']['plugin_root'] != new_root
                or current['parameters'] != {**epoch['parameters'], 'plugin_root': new_root}):
            raise Refusal('source roots do not bind exact observation parameters')
        reader = 'skills/implementaudit/scripts/codex-recovery-native-reader.py'  # Native plugin recovery uses the source repo-shaped package layout.
        for observation, root in ((epoch, old_root), (current, new_root)):
            expected_path = str(pathlib.Path(root) / reader)
            members = [r for r in observation['package_files'] if r['path'] == expected_path]
            if len(members) != 1 or observation['source_identity'] != members[0]:
                raise Refusal('executing reader is outside exact inventoried source')
        for key in ('binary', 'parent_binding', 'recovery_hook_binding'):
            if current[key] != epoch[key]: raise Refusal('native event producer or hook binding changed')
        if owner_identity(current['owner']) != owner_identity(epoch['owner']):
            raise Refusal('native owner changed after measured restart')
        if current['native_thread'] != epoch['native_thread']:
            raise Refusal('native task locator changed')
        if current['hooks'] != map_hook_source_paths(epoch['hooks'], old_root, new_root):
            raise Refusal('native hooks changed outside exact rooted source relocation')
        if current['parent_binding']['asar']['sha256'] != config.PRODUCER['asar_sha256']:
            raise Refusal('configuration writer source is not the pinned desktop')
        filtered, config_evidence = config.validate_config_transition(
            epoch['configs'], raw_reads, physical_reads, spec['config_witness'])
        if current['configs'] != filtered:
            raise Refusal('intervening native observation configuration differs')
        return {'schema': 'implementaudit.observation-successor-comparison.v1',
                'source': comparison, 'config': config_evidence,
                'original_epoch_files': pins, 'ordinary_effect_authority': 'NONE',
                'currentness_restored': False}
    except (source.Refusal, config.ConfigTransitionRefusal) as error:
        raise Refusal(str(error)) from None


"""Pure/read-only additions for the pinned native reader; no observer creation.

These functions rely on existing reader globals. JSON and path custody are not
authentication. Only the exact authenticated NativeRecoveryObserver caller may
bind this evidence to native producer/package authority.
"""

_ATTEMPT_SCHEMA = 'implementaudit.recovery-attempt-native-evidence.v1'
_ATTEMPT_V2_SCHEMA = 'implementaudit.recovery-attempt-native-evidence.v2'
_ATTEMPT_QUALIFICATION = 'UNQUALIFIED_WITHOUT_AUTHENTICATED_CALLER'
_ATTEMPT_PREFIX_KEYS = {'path','complete_prefix_bytes','complete_prefix_sha256',
    'complete_rows','session_id','task_id','session_meta_sha256','native_session_cwd'}
_ATTEMPT_ROW_KEYS = {'ordinal','type','row_digest','turn_id','bytes'}
_ATTEMPT_KEYS = {'schema','qualification','observability','native_thread_id',
    'native_session_id','native_turn_id','epoch_identity','native_epoch_frontier',
    'readback_prefix','selected_input_sha256','input_row_digest','attempt_start',
    'prior_terminal','rows','visible_assistant','compaction_markers','evidence_digest',
    'observation_successor_identity','observation_successor_spec_sha256'}
_ATTEMPT_V2_KEYS = _ATTEMPT_KEYS | {'incoming_inputs','capability_context'}


def _attempt_hash(value, prefixed=True):
    if not isinstance(value,str): return False
    if prefixed:
        if not value.startswith('sha256:'): return False
        value=value[7:]
    return len(value)==64 and all(c in '0123456789abcdef' for c in value)


def _attempt_text(value):
    return isinstance(value,str) and bool(value) and len(value.encode('utf-8'))<=4096


def _attempt_prefix_shape(value):
    if (not isinstance(value,dict) or set(value)!=_ATTEMPT_PREFIX_KEYS
            or type(value['complete_prefix_bytes']) is not int
            or not 0<value['complete_prefix_bytes']<=512*1024*1024
            or type(value['complete_rows']) is not int or not 1<=value['complete_rows']<=1000000
            or not all(_attempt_text(value[k]) for k in ('path','session_id','task_id'))
            or not _attempt_hash(value['complete_prefix_sha256'],False)
            or not _attempt_hash(value['session_meta_sha256'],False)
            or value['native_session_cwd'] is not None and not _attempt_text(value['native_session_cwd'])):
        raise Refusal('attempt prefix shape differs')


def _attempt_descriptor(row, wire, turn):
    return {'ordinal':row['ordinal'],'type':row['type'],'row_digest':'sha256:'+digest(wire),
            'turn_id':turn,'bytes':len(wire)}


def _attempt_envelope(wire):
    if not wire or len(wire)>8*1024*1024 or not wire.endswith(b'\n') or b'\r' in wire or b'\x00' in wire:
        raise Refusal('attempt native row partial or oversized')
    row=strict_json(wire)
    if (not isinstance(row,dict) or set(row) not in ({'timestamp','ordinal','type','payload'},
            {'timestamp','ordinal','type','payload','metadata'})
            or type(row.get('ordinal')) is not int or row['ordinal']<0
            or not _attempt_text(row.get('type')) or not _attempt_text(row.get('timestamp'))
            or not isinstance(row.get('payload'),dict)):
        raise Refusal('attempt native row envelope differs')
    return row


def _attempt_frozen_rows(value, session_root, task, previous, cutoff):
    """Stream only suffix records to a frozen cutoff; never decode old prose.

    Frozen prefix verification before/after the scan permits unrelated live-tail
    growth. This proves these byte boundaries, not indefinite immutability.
    """
    _attempt_prefix_shape(previous);_attempt_prefix_shape(cutoff)
    for key in ('path','session_id','task_id','session_meta_sha256','native_session_cwd'):
        if previous[key]!=cutoff[key]: raise Refusal('attempt source identity differs')
    if previous['task_id']!=task or cutoff['complete_prefix_bytes']<previous['complete_prefix_bytes']:
        raise Refusal('attempt cutoff predates epoch or task differs')
    path=native_path(value,session_root)
    verify_historical_prefix(value,session_root,task,previous)
    verify_historical_prefix(value,session_root,task,cutoff)
    start=previous['complete_prefix_bytes'];end=cutoff['complete_prefix_bytes']
    with path.open('rb',buffering=0) as stream:
        stream.seek(max(0,start-8*1024*1024-1));tail=stream.read(min(start,8*1024*1024+1))
        if not tail.endswith(b'\n'): raise Refusal('attempt prior prefix is incomplete')
        split=tail.rfind(b'\n',0,len(tail)-1)
        if split<0 and start>len(tail): raise Refusal('attempt previous last row exceeds bound')
        last=_attempt_envelope(tail[split+1:]);next_ordinal=last['ordinal']+1
        stream.seek(start);offset=start;count=previous['complete_rows'];first=True;pending=b''
        while offset<end:
            while b'\n' not in pending:
                remaining=end-offset-len(pending)
                if remaining<=0: raise Refusal('attempt cutoff is incomplete')
                chunk=stream.read(min(65536,remaining))
                if not chunk: raise Refusal('attempt suffix shortened during scan')
                pending+=chunk
                if len(pending)>8*1024*1024 and b'\n' not in pending:
                    raise Refusal('attempt native row oversized')
            split=pending.index(b'\n')+1;wire=pending[:split];pending=pending[split:]
            if offset+len(wire)>end: raise Refusal('attempt cutoff is incomplete')
            row=_attempt_envelope(wire)
            restart=(first and row['ordinal']==next_ordinal-1 and row['type']=='event_msg'
                and row['payload'].get('type')=='task_started' and 'metadata' not in row)
            if restart: next_ordinal-=1
            if row['ordinal']!=next_ordinal: raise Refusal('attempt suffix ordinal is not contiguous')
            next_ordinal+=1;first=False;offset+=len(wire);count+=1
            if count>1000000: raise Refusal('attempt suffix scan row ceiling')
            yield row,wire
        if count!=cutoff['complete_rows']: raise Refusal('attempt cutoff row count differs')
    verify_historical_prefix(value,session_root,task,previous)
    verify_historical_prefix(value,session_root,task,cutoff)


def _attempt_native_turn(row):
    payload=row['payload'];turn=payload.get('turn_id')
    if 'metadata' in row or not _attempt_text(turn):
        raise Refusal('attempt native terminal/start identity absent or ambiguous')
    kind=payload.get('type')
    clocks={'started_at','completed_at','duration_ms','time_to_first_token_ms'}
    if any(key in payload and payload[key] is not None and type(payload[key]) is not int for key in clocks):
        raise Refusal('attempt native terminal timing shape differs')
    if kind=='task_complete':
        if (not {'type','turn_id','last_agent_message'}<=set(payload)
                or not set(payload)<={'type','turn_id','last_agent_message','error'}|clocks
                or payload['last_agent_message'] is not None and not isinstance(payload['last_agent_message'],str)
                or payload.get('error') is not None and not isinstance(payload['error'],dict)):
            raise Refusal('attempt native terminal shape differs')
    if kind=='turn_aborted':
        if (not set(payload)<={'type','turn_id','reason','started_at','completed_at','duration_ms'}
                or payload.get('reason') not in ('interrupted','replaced','review_ended','budget_limited')):
            raise Refusal('attempt native aborted terminal shape differs')
    return turn


def _attempt_compaction(row):
    return (row['type']=='compacted' or row['type']=='event_msg' and row['payload'].get('type')=='context_compacted'
        or row['type']=='response_item' and row['payload'].get('type') in ('compaction','compaction_summary','context_compaction'))


def _attempt_visible(row):
    p=row['payload']
    if row['type']=='event_msg': return p.get('type')=='agent_message'
    if row['type']!='response_item': return False
    kind=p.get('type')
    if kind=='message':
        # Native Message is public; hidden reasoning has a distinct item type.
        # None is the protocol's explicitly supported legacy unknown phase.
        return p.get('role')=='assistant' and p.get('phase') in (None,'commentary','final_answer') and p.get('channel') not in ('analysis','justify','confidence')
    if kind=='image_generation_call':
        raise Refusal('attempt combined call/result requires separately qualified projection')
    return kind in ('function_call','custom_tool_call','local_shell_call','tool_search_call','web_search_call')


def _attempt_incoming_message(row, pending, turn):
    """Validate the exact persisted incoming pair, never author-label identity."""
    p=row['payload']
    if (pending is None or row['ordinal']!=pending['ordinal']+1 or pending['turn_id']!=turn
            or 'metadata' in row or not _attempt_text(turn)):
        raise Refusal('ambiguous agent_message lacks same-turn native incoming pair')
    required={'type','id','author','recipient','content','internal_chat_message_metadata_passthrough'}
    if set(p)!=required or not all(_attempt_text(p[k]) for k in ('id','author','recipient')):
        raise Refusal('ambiguous agent_message incoming shape differs')
    if any('\n' in p[k] or '\r' in p[k] for k in ('author','recipient')):
        raise Refusal('ambiguous agent_message source labels malformed')
    meta=p['internal_chat_message_metadata_passthrough']
    if (not isinstance(meta,dict) or not {'turn_id','create_time'}<=set(meta)
            or not set(meta)<={'turn_id','create_time','content_item_kinds'} or meta['turn_id']!=turn
            or type(meta['create_time']) not in (int,float) or not 0<=meta['create_time']<float('inf')):
        raise Refusal('ambiguous agent_message stamped turn/time differs')
    content=p['content']
    if not isinstance(content,list) or len(content) not in (1,2):
        raise Refusal('ambiguous agent_message content variants differ')
    if 'content_item_kinds' in meta and (not isinstance(meta['content_item_kinds'],list)
            or len(meta['content_item_kinds'])!=len(content)
            or not all(_attempt_text(k) for k in meta['content_item_kinds'])):
        raise Refusal('ambiguous agent_message content metadata differs')
    first=content[0]
    if not isinstance(first,dict) or set(first)!={'type','text'} or first['type']!='input_text' or not isinstance(first['text'],str):
        raise Refusal('ambiguous agent_message plaintext framing differs')
    if len(content)==2:
        second=content[1]
        header=("Message Type: "+('NEW_TASK' if pending['trigger_turn'] else 'MESSAGE')
            +'\nTask name: '+p['recipient']+'\nSender: '+p['author']+'\nPayload:\n')
        if (not isinstance(second,dict) or set(second)!={'type','encrypted_content'}
                or second['type']!='encrypted_content' or not isinstance(second['encrypted_content'],str)
                or not second['encrypted_content'] or first['text']!=header):
            raise Refusal('ambiguous agent_message encrypted source framing differs')
        return 'ENCRYPTED_OR_MIXED_BODY_EXCLUDED'
    return 'PLAINTEXT_BODY_EXCLUDED'


def _attempt_coverage_decision(row, wire, turn, pending):
    """Closed conduct-only coverage; private/input bodies are never returned."""
    p=row['payload'];kind=p.get('type')
    agent=row['type']=='response_item' and kind=='agent_message'
    if pending is not None and not agent:
        raise Refusal('incoming metadata marker lacks immediately associated agent_message')
    if row['type']=='inter_agent_communication_metadata':
        if ('metadata' in row or set(p)!={'trigger_turn'} or type(p['trigger_turn']) is not bool
                or not _attempt_text(turn)):
            raise Refusal('incoming metadata marker shape/turn/provenance differs')
        return ({'ordinal':row['ordinal'],'row_digest':'sha256:'+digest(wire),
            'turn_id':turn,'trigger_turn':p['trigger_turn']},None,None)
    if row['type']!='response_item': return (None,None,None)
    if agent:
        readability=_attempt_incoming_message(row,pending,turn)
        descriptor={'metadata_ordinal':pending['ordinal'],'metadata_row_digest':pending['row_digest'],
            'message_ordinal':row['ordinal'],'message_row_digest':'sha256:'+digest(wire),
            'native_turn_id':turn,'trigger_turn':pending['trigger_turn'],'readability':readability,
            'source_role':'INCOMING_INPUT_CONDITIONED_ON_AUTHENTICATED_CALLER'}
        return (None,descriptor,None)
    if kind=='additional_tools':
        if (not {'type','role','tools'}<=set(p) or not set(p)<={'type','id','role','tools'}
                or not _attempt_text(p['role']) or 'id' in p and not _attempt_text(p['id'])
                or not isinstance(p['tools'],list) or len(p['tools'])>4096):
            raise Refusal('capability declaration shape incomplete or oversized')
        return (None,None,{'ordinal':row['ordinal'],'row_digest':'sha256:'+digest(wire),
            'classification':'CAPABILITY_DECLARATION_ONLY'})
    if kind=='compaction_trigger':
        raise Refusal('unsupported durable compaction_trigger request control; no compact-event claim')
    supported={'message','reasoning','local_shell_call','function_call','tool_search_call',
        'function_call_output','custom_tool_call','custom_tool_call_output','tool_search_output',
        'web_search_call','image_generation_call','compaction','compaction_summary','context_compaction'}
    if kind not in supported:
        raise Refusal('unknown response-item conduct coverage; no compact-event claim')
    return (None,None,None)


def _attempt_coverage_row(row, wire, turn, pending):
    try:
        return _attempt_coverage_decision(row,wire,turn,pending)
    except Refusal as error:
        # Diagnostic identity only, never a body, authorization or compaction.
        descriptor=_attempt_descriptor(row,wire,turn)
        refusal=Refusal(str(error)+'; ordinal='+str(row['ordinal'])+'; row_digest='+descriptor['row_digest'])
        refusal.coverage_refusal={'qualification':_ATTEMPT_QUALIFICATION,
            'reason_code':'UNQUALIFIED_NATIVE_CARRIER','row':descriptor,'detail':str(error)}
        raise refusal from error


def build_attempt_evidence(value, session_root, task, previous, selected):
    """Evidence only. Caller must already authenticate NativeRecoveryObserver.

    A prior terminal must occur AFTER the saved epoch, and the selected start
    must follow that terminal with a distinct turn ID. Restart and later UPS
    cannot erase earlier rows of that same selected turn. Only selected public
    commentary/final messages and calls are exposed, never hidden reasoning.
    """
    if not isinstance(selected,dict) or not isinstance(selected.get('raw'),bytes):
        raise Refusal('attempt selected native input absent')
    if len(selected['raw'])>1048576: raise Refusal('attempt selected input exceeds bound')
    cutoff=selected.get('readback_prefix');_attempt_prefix_shape(cutoff)
    if selected.get('native_epoch_frontier')!=previous:
        raise Refusal('attempt selected epoch frontier differs')
    target=selected.get('native_turn_id')
    if (not _attempt_text(target) or selected.get('native_thread_id')!=task
            or selected.get('native_session_id')!=previous.get('session_id')
            or not _attempt_hash(selected.get('epoch_identity'))):
        raise Refusal('attempt selected task/session/turn/epoch differs')
    source={k:selected.get(k) for k in ('observation_successor_identity','observation_successor_spec_sha256')}
    if (source['observation_successor_identity'] is None)!=(source['observation_successor_spec_sha256'] is None):
        raise Refusal('attempt successor source identity incomplete')
    if source['observation_successor_identity'] is not None and (not _attempt_hash(source['observation_successor_identity'])
            or not _attempt_hash(source['observation_successor_spec_sha256'],False)):
        raise Refusal('attempt successor source identity malformed')
    active=None;seen=set();terminal=None;start=None;prior=None
    rows=[];visible=[];markers=[];visible_bytes=0;selected_wire=[];hook_digests=[]
    pending=None;incoming=[];capabilities=[]
    for row,wire in _attempt_frozen_rows(value,session_root,task,previous,cutoff):
        payload=row['payload'];kind=payload.get('type')
        if row['type']=='event_msg' and kind in ('task_complete','turn_aborted'):
            turn=_attempt_native_turn(row)
            if active is not None and turn!=active: raise Refusal('attempt terminal disagrees with active turn')
            if turn==target: raise Refusal('selected attempt already terminal at admission cutoff')
            terminal={**_attempt_descriptor(row,wire,turn),'event_type':kind};active=None
        elif row['type']=='event_msg' and kind=='task_started':
            turn=_attempt_native_turn(row)
            if turn in seen: raise Refusal('attempt duplicate native turn start')
            seen.add(turn)
            if turn==target:
                if terminal is None: raise Refusal('selected attempt lacks post-epoch prior terminal')
                if terminal['turn_id']==turn or active is not None:
                    raise Refusal('selected attempt lacks distinct completed prior turn')
                start=_attempt_descriptor(row,wire,turn);prior=terminal;selected_wire=[wire]
            elif start is not None: raise Refusal('selected attempt cutoff crosses a later turn')
            active=turn;terminal=None
        elif row['type']=='turn_context' and payload.get('turn_id')!=active:
            raise Refusal('attempt context disagrees with active turn')
        if active!=target: continue
        descriptor=_attempt_descriptor(row,wire,target);rows.append(descriptor)
        if len(rows)>4096: raise Refusal('selected attempt row ceiling')
        pending,input_descriptor,capability=_attempt_coverage_row(row,wire,target,pending)
        if input_descriptor is not None: incoming.append(input_descriptor)
        if capability is not None: capabilities.append(capability)
        if row['type']=='response_item':
            meta=payload.get('internal_chat_message_metadata_passthrough')
            if isinstance(meta,dict) and meta.get('turn_id') not in (None,target):
                raise Refusal('selected attempt response attribution differs')
            if payload.get('role')=='developer':
                content=payload.get('content')
                recovery=isinstance(content,list) and any(isinstance(item,dict)
                    and isinstance(item.get('text'),str) and 'implementaudit.recovery-host-input.v1' in item['text'] for item in content)
                if recovery:
                    selected_wire.append(wire)
                    if row.get('metadata')!={'client_authored':True}: hook_digests.append(descriptor['row_digest'])
        if _attempt_visible(row):
            visible_bytes+=len(wire)
            if visible_bytes>1048576: raise Refusal('selected visible assistant byte ceiling')
            visible.append({'ordinal':row['ordinal'],'row_digest':descriptor['row_digest'],'wire':wire.decode('utf-8')})
        if _attempt_compaction(row):
            markers.append({'ordinal':row['ordinal'],'row_digest':descriptor['row_digest'],
                'turn_id':target,'invalidation_radius':'SELECTED_ATTEMPT'})
    if pending is not None: raise Refusal('incoming metadata marker incomplete at exact cutoff')
    if start is None or prior is None: raise Refusal('selected attempt terminal/start evidence absent')
    with native_path(value,session_root).open('rb',buffering=0) as stream:
        meta_wire=stream.readline(131073)
    if digest(meta_wire)!=previous['session_meta_sha256']: raise Refusal('attempt session metadata changed')
    if meta_wire+b''.join(selected_wire)!=selected['raw'] or len(hook_digests)!=1:
        raise Refusal('attempt selected input/hook does not match complete native attempt')
    result={'schema':_ATTEMPT_V2_SCHEMA,'qualification':_ATTEMPT_QUALIFICATION,
        'observability':'HOST_VISIBLE_MESSAGES_AND_CALLS','native_thread_id':task,
        'native_session_id':previous['session_id'],'native_turn_id':target,
        'epoch_identity':selected['epoch_identity'],'native_epoch_frontier':dict(previous),
        'readback_prefix':dict(cutoff),'selected_input_sha256':digest(selected['raw']),
        'input_row_digest':hook_digests[0],'attempt_start':start,'prior_terminal':prior,
        'rows':rows,'visible_assistant':visible,'compaction_markers':markers,
        'incoming_inputs':incoming,'capability_context':capabilities,**source}
    result['evidence_digest']='sha256:'+digest(canonical(result))
    validate_attempt_evidence_shape(result)
    return result


def _attempt_validate_v1_shape(value):
    """No I/O; validates serialization integrity, never native authentication."""
    if (not isinstance(value,dict) or set(value)!=_ATTEMPT_KEYS
            or value['schema']!=_ATTEMPT_SCHEMA or value['qualification']!=_ATTEMPT_QUALIFICATION
            or value['observability']!='HOST_VISIBLE_MESSAGES_AND_CALLS'):
        raise Refusal('attempt evidence closed shape differs')
    if len(canonical(value))>2*1024*1024: raise Refusal('attempt evidence byte ceiling')
    for key in ('native_thread_id','native_session_id','native_turn_id'):
        if not _attempt_text(value[key]): raise Refusal('attempt evidence identity malformed')
    for key in ('epoch_identity','input_row_digest','evidence_digest'):
        if not _attempt_hash(value[key]): raise Refusal('attempt evidence digest malformed')
    if not _attempt_hash(value['selected_input_sha256'],False): raise Refusal('attempt input digest malformed')
    for key in ('native_epoch_frontier','readback_prefix'): _attempt_prefix_shape(value[key])
    old=value['native_epoch_frontier'];new=value['readback_prefix']
    for key in ('path','session_id','task_id','session_meta_sha256','native_session_cwd'):
        if old[key]!=new[key]: raise Refusal('attempt prefix identities differ')
    if (old['task_id']!=value['native_thread_id'] or old['session_id']!=value['native_session_id']
            or new['complete_prefix_bytes']<=old['complete_prefix_bytes'] or new['complete_rows']<=old['complete_rows']):
        raise Refusal('attempt prefix identity/order differs')
    a=value['observation_successor_identity'];b=value['observation_successor_spec_sha256']
    if (a is None)!=(b is None) or a is not None and (not _attempt_hash(a) or not _attempt_hash(b,False)):
        raise Refusal('attempt successor identity differs')
    rows=value['rows'];visible=value['visible_assistant'];markers=value['compaction_markers']
    if not isinstance(rows,list) or not 1<=len(rows)<=4096 or not isinstance(visible,list) or not isinstance(markers,list):
        raise Refusal('attempt row arrays malformed')
    def descriptor(row, keys=_ATTEMPT_ROW_KEYS):
        if (not isinstance(row,dict) or set(row)!=keys or type(row['ordinal']) is not int or row['ordinal']<0
                or not _attempt_hash(row['row_digest']) or not _attempt_text(row['type'])
                or not _attempt_text(row['turn_id']) or type(row['bytes']) is not int or not 0<row['bytes']<=8*1024*1024):
            raise Refusal('attempt row descriptor malformed')
    for row in rows: descriptor(row)
    start=value['attempt_start'];prior=value['prior_terminal'];descriptor(start);descriptor(prior,_ATTEMPT_ROW_KEYS|{'event_type'})
    if (start!=rows[0] or start['type']!='event_msg' or prior['type']!='event_msg'
            or prior['event_type'] not in ('task_complete','turn_aborted')
            or prior['turn_id']==value['native_turn_id'] or prior['ordinal']>=start['ordinal']):
        raise Refusal('attempt terminal/start identity/order malformed')
    for i,row in enumerate(rows):
        if row['ordinal']!=start['ordinal']+i or row['turn_id']!=value['native_turn_id']:
            raise Refusal('attempt selected interval incomplete or mismatched')
    by_ordinal={r['ordinal']:r for r in rows}
    if value['input_row_digest'] not in {r['row_digest'] for r in rows}: raise Refusal('attempt hook row absent')
    used=set();visible_bytes=0
    for item in visible:
        if not isinstance(item,dict) or set(item)!={'ordinal','row_digest','wire'} or not isinstance(item['wire'],str):
            raise Refusal('attempt visible row malformed')
        wire=item['wire'].encode('utf-8');visible_bytes+=len(wire);row=_attempt_envelope(wire)
        descriptor_row=_attempt_descriptor(row,wire,value['native_turn_id'])
        if (type(item['ordinal']) is not int or item['ordinal'] in used or item['ordinal']!=row['ordinal']
                or by_ordinal.get(item['ordinal'])!=descriptor_row or item['row_digest']!=descriptor_row['row_digest']
                or not _attempt_visible(row) or visible_bytes>1048576):
            raise Refusal('attempt visible row digest/type/identity differs')
        used.add(item['ordinal'])
    used=set()
    for item in markers:
        if (not isinstance(item,dict) or set(item)!={'ordinal','row_digest','turn_id','invalidation_radius'}
                or type(item['ordinal']) is not int or item['ordinal'] in used
                or item['turn_id']!=value['native_turn_id'] or item['invalidation_radius']!='SELECTED_ATTEMPT'
                or item['ordinal'] not in by_ordinal or item['row_digest']!=by_ordinal[item['ordinal']]['row_digest']):
            raise Refusal('attempt compaction marker malformed')
        used.add(item['ordinal'])
    unsigned={k:v for k,v in value.items() if k!='evidence_digest'}
    if value['evidence_digest']!='sha256:'+digest(canonical(unsigned)):
        raise Refusal('attempt evidence digest differs')
    return True


def validate_attempt_evidence_shape(value):
    """Historical v1 stays closed; v2 adds body-free typed source coverage."""
    if isinstance(value,dict) and value.get('schema')==_ATTEMPT_SCHEMA:
        return _attempt_validate_v1_shape(value)
    if not isinstance(value,dict) or set(value)!=_ATTEMPT_V2_KEYS or value.get('schema')!=_ATTEMPT_V2_SCHEMA:
        raise Refusal('attempt v2 evidence closed shape differs')
    if len(canonical(value))>2*1024*1024: raise Refusal('attempt evidence byte ceiling')
    unsigned={k:v for k,v in value.items() if k!='evidence_digest'}
    if value['evidence_digest']!='sha256:'+digest(canonical(unsigned)):
        raise Refusal('attempt evidence digest differs')
    legacy={k:v for k,v in value.items() if k in _ATTEMPT_KEYS}
    legacy['schema']=_ATTEMPT_SCHEMA
    legacy['evidence_digest']='sha256:'+digest(canonical({k:v for k,v in legacy.items() if k!='evidence_digest'}))
    _attempt_validate_v1_shape(legacy)
    rows={row['ordinal']:row for row in value['rows']};used=set()
    incoming=value['incoming_inputs'];capabilities=value['capability_context']
    if not isinstance(incoming,list) or not isinstance(capabilities,list) or len(incoming)+len(capabilities)>4096:
        raise Refusal('attempt input/capability descriptors malformed')
    keys={'metadata_ordinal','metadata_row_digest','message_ordinal','message_row_digest',
        'native_turn_id','trigger_turn','readability','source_role'}
    for item in incoming:
        if (not isinstance(item,dict) or set(item)!=keys or type(item['metadata_ordinal']) is not int
                or type(item['message_ordinal']) is not int or item['message_ordinal']!=item['metadata_ordinal']+1
                or item['metadata_ordinal'] in used or item['message_ordinal'] in used
                or item['native_turn_id']!=value['native_turn_id'] or type(item['trigger_turn']) is not bool
                or item['readability'] not in ('PLAINTEXT_BODY_EXCLUDED','ENCRYPTED_OR_MIXED_BODY_EXCLUDED')
                or item['source_role']!='INCOMING_INPUT_CONDITIONED_ON_AUTHENTICATED_CALLER'):
            raise Refusal('attempt incoming descriptor shape/identity differs')
        for stem,kind in (('metadata','inter_agent_communication_metadata'),('message','response_item')):
            row=rows.get(item[stem+'_ordinal'])
            if row is None or row['type']!=kind or row['row_digest']!=item[stem+'_row_digest']:
                raise Refusal('attempt incoming descriptor row custody differs')
            used.add(row['ordinal'])
    if {r['ordinal'] for r in value['rows'] if r['type']=='inter_agent_communication_metadata'}!={i['metadata_ordinal'] for i in incoming}:
        raise Refusal('attempt incoming metadata descriptor coverage incomplete')
    for item in capabilities:
        if (not isinstance(item,dict) or set(item)!={'ordinal','row_digest','classification'}
                or type(item['ordinal']) is not int or item['ordinal'] in used
                or item['classification']!='CAPABILITY_DECLARATION_ONLY'
                or item['ordinal'] not in rows or rows[item['ordinal']]['type']!='response_item'
                or item['row_digest']!=rows[item['ordinal']]['row_digest']):
            raise Refusal('attempt capability descriptor shape/custody differs')
        used.add(item['ordinal'])
    if used & {v['ordinal'] for v in value['visible_assistant']}:
        raise Refusal('attempt input/capability body was exposed as conduct')
    return True


def _attempt_recompute_frozen(value, session_root, task, frozen):
    """Rebuild v2 classifications from exact retained source, not supplied JSON."""
    selected={k:frozen[k] for k in ('native_thread_id','native_session_id','native_turn_id',
        'epoch_identity','native_epoch_frontier','readback_prefix','observation_successor_identity',
        'observation_successor_spec_sha256')}
    with native_path(value,session_root).open('rb',buffering=0) as stream: meta=stream.readline(131073)
    wires=[meta];size=len(meta);active=None
    for row,wire in _attempt_frozen_rows(value,session_root,task,frozen['native_epoch_frontier'],frozen['readback_prefix']):
        p=row['payload']
        if row['type']=='event_msg' and p.get('type')=='task_started':
            active=p.get('turn_id')
            if active==frozen['native_turn_id']: wires.append(wire);size+=len(wire)
        if active==frozen['native_turn_id'] and row['type']=='response_item' and p.get('role')=='developer':
            content=p.get('content')
            if isinstance(content,list) and any(isinstance(i,dict) and isinstance(i.get('text'),str)
                    and 'implementaudit.recovery-host-input.v1' in i['text'] for i in content):
                wires.append(wire);size+=len(wire)
        if size>1048576: raise Refusal('frozen selected input reconstruction exceeds bound')
    selected['raw']=b''.join(wires)
    rebuilt=build_attempt_evidence(value,session_root,task,frozen['native_epoch_frontier'],selected)
    if rebuilt!=frozen: raise Refusal('frozen attempt classifications differ from exact source recomputation')


def revalidate_attempt_evidence(value, session_root, task, frozen, current_prefix):
    """Read-only proof of exact old prefix plus affected later boundary markers.

    The observer wrapper must freshly authenticate source/epoch first and raise
    on a REFUSE status. No global mutex and no independent holon invalidation.
    """
    validate_attempt_evidence_shape(frozen)
    if frozen['schema']!=_ATTEMPT_V2_SCHEMA:
        raise Refusal('historical v1 attempt cannot enter repaired live revalidation')
    if frozen['native_thread_id']!=task: raise Refusal('frozen attempt task differs')
    _attempt_recompute_frozen(value,session_root,task,frozen)
    verify_historical_prefix(value,session_root,task,frozen['native_epoch_frontier'])
    active=frozen['native_turn_id'];target=active;markers=list(frozen['compaction_markers']);ended=False
    later_rows=[];pending=None;incoming=[];capabilities=[]
    for row,wire in _attempt_frozen_rows(value,session_root,task,frozen['readback_prefix'],current_prefix):
        kind=row['payload'].get('type')
        if row['type']=='event_msg' and kind=='task_started':
            turn=_attempt_native_turn(row)
            if active==target or turn==target:
                raise Refusal('frozen attempt restart or same-turn alias is not a fresh boundary')
            active=turn
        elif row['type']=='event_msg' and kind in ('task_complete','turn_aborted'):
            turn=_attempt_native_turn(row)
            if active is not None and active!=turn: raise Refusal('lifecycle terminal active turn differs')
            if turn==target: ended=True
            active=None
        elif row['type']=='turn_context' and row['payload'].get('turn_id')!=active:
            raise Refusal('lifecycle context active turn differs')
        pending,input_descriptor,capability=_attempt_coverage_row(row,wire,active,pending)
        if input_descriptor is not None: incoming.append(input_descriptor)
        if capability is not None: capabilities.append(capability)
        if len(incoming)+len(capabilities)>4096: raise Refusal('lifecycle coverage descriptor ceiling')
        # This retained OPEN has not been disposed. A later same-parent turn
        # cannot make a boundary safe for its still-pending older cognition.
        if _attempt_compaction(row):
            markers.append({'ordinal':row['ordinal'],'row_digest':'sha256:'+digest(wire),
                'turn_id':target,'invalidation_radius':'SELECTED_ATTEMPT'})
        if active==target:
            item=_attempt_descriptor(row,wire,target);later_rows.append(item)
            if len(later_rows)>4096: raise Refusal('lifecycle selected interval row ceiling')
        if len(markers)>4096: raise Refusal('lifecycle compaction marker ceiling')
    if pending is not None: raise Refusal('lifecycle incoming pair incomplete at exact cutoff')
    return {'schema':'implementaudit.recovery-attempt-native-revalidation.v2',
        'qualification':_ATTEMPT_QUALIFICATION,'frozen_evidence_digest':frozen['evidence_digest'],
        'frozen_prefix_verified':True,'readback_prefix':dict(current_prefix),
        'affected_native_turn_id':target,'selected_turn_ended':ended,'later_rows':later_rows,
        'compaction_markers':markers,'incoming_inputs':incoming,'capability_context':capabilities,
        'semantic_status':'REFUSE_INTERVENING_COMPACTION' if markers else 'NO_NEW_SELECTED_ATTEMPT_COMPACTION'}


def _disposition_locator(locator, task, previous):
    keys={'schema','old_record_identity','capsule_digest','used_digest',
        'native_thread_id','native_session_id','native_turn_id','row_ordinal','row_digest','epoch_identity'}
    if (not isinstance(locator,dict) or set(locator)!=keys
            or locator['schema']!='implementaudit.retained-disposition-locator.v1'
            or locator['native_thread_id']!=task or locator['native_session_id']!=previous['session_id']
            or not _attempt_text(locator['native_turn_id'])
            or type(locator['row_ordinal']) is not int or locator['row_ordinal']<1
            or any(not _attempt_hash(locator[key]) for key in
                ('old_record_identity','capsule_digest','used_digest','row_digest','epoch_identity'))):
        raise Refusal('retained disposition locator differs')
    return locator


def read_disposition_turn_slice(value, session_root, task, previous, current_prefix, locator):
    """Verify retained occurrence for abandonment only; never select fresh input.

    previous is the actual committed restart-epoch prefix. current_prefix is a
    freshly authenticated scan bound, not a historical commitment through OPEN.
    No complete post-epoch conduct or clean-cognition assertion is made here.
    """
    _attempt_prefix_shape(previous);_attempt_prefix_shape(current_prefix)
    _disposition_locator(locator,task,previous)
    path=native_path(value,session_root)
    verify_historical_prefix(value,session_root,task,previous)
    verify_historical_prefix(value,session_root,task,current_prefix)
    with path.open('rb',buffering=0) as stream:meta=stream.readline(131073)
    if len(meta)>131072:raise Refusal('retained disposition metadata exceeds bound')
    active=None;seen=set();selected_rows=[];selected_bytes=len(meta);native_count=0
    user_ordinal=None;first=None;found=False;offset=previous['complete_prefix_bytes'];occurrence_end=None
    for row,wire in _attempt_frozen_rows(value,session_root,task,previous,current_prefix):
        offset+=len(wire)
        if first is None:first=row['ordinal']
        # Continue mechanical ordinal/prefix verification after the retained
        # occurrence. Later messages/hooks cannot substitute for or erase it.
        if found:continue
        if row['ordinal']>locator['row_ordinal']:
            raise Refusal('retained disposition occurrence missing')
        p=row['payload'];target=row['ordinal']==locator['row_ordinal']
        if target and 'sha256:'+digest(wire)!=locator['row_digest']:
            raise Refusal('retained disposition original raw row changed')
        if row['type']=='event_msg' and p.get('type')=='task_started':
            turn=p.get('turn_id')
            if not _attempt_text(turn) or turn in seen or 'metadata' in row or len(wire)>131072:
                raise Refusal('retained disposition task marker absent or ambiguous')
            seen.add(turn);active=turn;selected_rows=[wire];selected_bytes=len(meta)+len(wire);native_count=0;user_ordinal=None
        elif row['type']=='turn_context' and p.get('turn_id')!=active:
            raise Refusal('retained disposition turn context differs')
        if row['type']!='response_item':
            if target:raise Refusal('retained disposition locator is not a hook row')
            continue
        metadata=p.get('internal_chat_message_metadata_passthrough');role=p.get('role')
        if role=='user':
            if (p.get('type')!='message' or not active or not isinstance(metadata,dict)
                    or metadata.get('turn_id')!=active):
                raise Refusal('retained disposition user occurrence differs')
            kinds=metadata.get('content_item_kinds')
            if kinds==['user.text']:
                if 'metadata' in row:raise Refusal('retained disposition user provenance ambiguous')
                user_ordinal=row['ordinal']
            elif kinds not in (['goal.internal_context'],['environments.environment_context']):
                raise Refusal('retained disposition user kind unsupported')
            if target:raise Refusal('retained disposition locator selects user instead of hook')
            continue
        if role!='developer':
            if target:raise Refusal('retained disposition locator has wrong role')
            continue
        recovery=False
        for item in p.get('content',[]) if isinstance(p.get('content'),list) else []:
            if not isinstance(item,dict) or not isinstance(item.get('text'),str):continue
            text=item['text']
            if 'implementaudit.recovery-host-input.v1' in text:recovery=True;break
            try:decoded=strict_json(text)
            except Refusal as error:
                if isinstance(error.__cause__,json.JSONDecodeError):continue
                raise Refusal('retained disposition developer JSON is ambiguous') from error
            if isinstance(decoded,dict) and decoded.get('schema')=='implementaudit.recovery-host-input.v1':recovery=True;break
        hook_kind=isinstance(metadata,dict) and metadata.get('content_item_kinds')==['hooks.additional_context']
        if hook_kind and not recovery:raise Refusal('retained disposition hook content unknown')
        if not recovery:
            if target:raise Refusal('retained disposition row is not recovery input')
            continue
        if (not active or not isinstance(metadata,dict) or metadata.get('turn_id')!=active
                or len(wire)>131072):raise Refusal('retained disposition hook occurrence differs')
        selected_rows.append(wire);selected_bytes+=len(wire)
        if row.get('metadata')!={'client_authored':True}:native_count+=1
        if selected_bytes>1048576 or len(selected_rows)>4095:raise Refusal('retained disposition slice exceeds bound')
        if target:
            if (active!=locator['native_turn_id'] or user_ordinal is None or user_ordinal>=row['ordinal']
                    or native_count!=1 or 'metadata' in row or not hook_kind):
                raise Refusal('retained disposition original user-hook relation is ambiguous')
            found=True
            occurrence_end=offset
    if not found or first is None:raise Refusal('retained disposition occurrence missing')
    verify_historical_prefix(value,session_root,task,previous)
    verify_historical_prefix(value,session_root,task,current_prefix)
    return {'raw':meta+b''.join(selected_rows),'native_thread_id':task,
        'native_session_id':previous['session_id'],'native_turn_id':locator['native_turn_id'],
        'after_ordinal':first-1,'readback_prefix':dict(current_prefix),
        'occurrence_end_bytes':occurrence_end,
        'disposition_locator_identity':'sha256:'+digest(canonical(locator)),
        'historical_commitment_kind':'SAVED_RESTART_EPOCH_PREFIX_AND_RETAINED_OCCURRENCE',
        'post_epoch_conduct_qualified':False}


# Initial-epoch relation and explicit acquisition are isolated from native effects.
_EPOCH_V2 = 'implementaudit.native-owner-observation.v2'
_ACQUISITION_KEYS = {'schema', 'native_results_sha256', 'physical_metadata_sha256',
    'filtered_configs_sha256', 'pipe_value', 'user_config_path'}
_INITIAL_FAILURE_PREDICATES = {
    'HANDOFF_IDENTITY': {'HANDOFF_CONTEXT'},
    'FINISH_START': {'START_READBACK'},
    'ACTUAL_AFTER_CUSTODY': {'ACTUAL_AFTER_DIFFERS'},
    'CONFIG_IDENTITY': {'INITIAL_SOURCE_BINDING', 'ACQUISITION_BINDING', 'ACQUISITION_WITNESS',
                        'INITIAL_WITNESS', 'ACTUAL_AFTER_CONFIG', 'ORIGIN_BINDING'},
    'INVERSE_PHYSICAL': {'PHYSICAL_INVERSE'},
    'INVERSE_NATIVE': {'USER_CONFIG_INVERSE', 'RESOLVED_CONFIG_INVERSE'},
    'INITIAL_BEFORE_BINDING': {'BEFORE_NATIVE_DIGEST', 'BEFORE_PHYSICAL_DIGEST'},
    'STABLE_SOURCE': {'EPOCH_STABLE_FIELDS', 'PRODUCER_CONFIG_ARGUMENTS', 'NATIVE_TASK_SESSION'},
    'STOP_ORDER': {'STOP_BINDING', 'STARTUP_ORDER', 'PRODUCER_RESTART'},
    'HISTORICAL_PREFIX': {'HISTORICAL_PREFIX_REFUSED'},
    'EPOCH_RELATION': set(), 'FINAL_WRITE': set(), 'UNKNOWN': set()}


class InitialEpochFailure(Refusal):
    """Fixed identity only; exception messages never enter diagnostic records."""
    def __init__(self, stage, predicate, message):
        self.stage = stage if stage in _INITIAL_FAILURE_PREDICATES else 'UNKNOWN'
        self.predicate = predicate if predicate in _INITIAL_FAILURE_PREDICATES[self.stage] else 'UNKNOWN'
        super().__init__(message)


class _InitialFinishHandoff:
    """Live instance binding under controlled source custody, never a receipt."""
    __slots__ = ('owner','deadline')
    def __init__(self, owner, deadline): self.owner=owner;self.deadline=deadline
    def __copy__(self): raise TypeError('initial finish handoff is not copyable')
    def __deepcopy__(self, memo): raise TypeError('initial finish handoff is not copyable')
    def __reduce__(self): raise TypeError('initial finish handoff is not serializable')


def _initial_failure_file_pin(path):
    try:
        if path.stat().st_size > LIMIT: return {'status':'UNAVAILABLE'}
        raw = path.read_bytes()
        if len(raw) > LIMIT: return {'status':'UNAVAILABLE'}
        return {'status':'AVAILABLE', 'bytes':len(raw), 'sha256':digest(raw)}
    except (OSError, ValueError, TypeError):
        return {'status':'UNAVAILABLE'}


def _initial_failure_material(before, after, before_acquisition, after_acquisition, transition):
    """Allowlisted hashes only. Missing or invalid material never becomes evidence."""
    unavailable = lambda: {'status':'UNAVAILABLE'}
    result = {'acquisitions':{'before':unavailable(), 'after':unavailable()},
              'selected_material':unavailable(), 'witness':unavailable()}
    try: h = _config_helper()
    except (Refusal, OSError, ValueError, KeyError, TypeError): return result
    bindings = {}
    for label, observation, acquisition in (('before',before,before_acquisition), ('after',after,after_acquisition)):
        try:
            binding = acquisition['binding']
            _check_acquisition(binding, observation['configs'])
            bindings[label] = binding
            result['acquisitions'][label] = {'status':'AVAILABLE_VALID',
                'binding_sha256':digest(canonical(binding)),
                **{key:binding[key] for key in ('native_results_sha256','physical_metadata_sha256','filtered_configs_sha256')},
                **{key+'_sha256':digest(binding[key].encode()) if binding[key] is not None else None
                   for key in ('pipe_value','user_config_path')}}
        except (Refusal, OSError, ValueError, KeyError, TypeError): pass
    try:
        configs, selected = h.observed_config_material(after_acquisition['native_reads'], after_acquisition['physical_reads'])
        if configs == after['configs'] and selected == bindings.get('after'):
            result['selected_material'] = {'status':'AVAILABLE_VALID',
                **{key:selected[key] for key in ('native_results_sha256','physical_metadata_sha256','filtered_configs_sha256')}}
    except (Refusal, OSError, ValueError, KeyError, TypeError): pass
    try:
        bb, ab = bindings['before'], bindings['after']
        expected = {'schema':'implementaudit.config-pipe-transition.v1', 'field':h.FIELD,
            'previous_value':bb['pipe_value'], 'current_value':ab['pipe_value'],
            'user_config_path':bb['user_config_path'], 'producer':h.PRODUCER,
            'previous_filtered_configs_sha256':bb['filtered_configs_sha256'],
            'current_native_results_sha256':ab['native_results_sha256'],
            'current_physical_metadata_sha256':ab['physical_metadata_sha256']}
        if (isinstance(transition,dict) and transition.get('witness') == expected
                and transition.get('helper_sha256') == CONFIG_TRANSITION_DIGEST
                and transition.get('before_acquisition') == bb and transition.get('after_acquisition') == ab
                and isinstance(bb['user_config_path'],str) and bool(bb['user_config_path'])
                and bb['user_config_path'] == ab['user_config_path']
                and all(isinstance(v,str) and h.PIPE_PATTERN.fullmatch(v) for v in (bb['pipe_value'],ab['pipe_value']))
                and bb['pipe_value'] != ab['pipe_value']):
            result['witness'] = {'status':'AVAILABLE_VALID', 'witness_sha256':digest(canonical(expected)),
                'field':h.FIELD, 'producer':dict(h.PRODUCER),
                'previous_value_sha256':digest(bb['pipe_value'].encode()),
                'current_value_sha256':digest(ab['pipe_value'].encode()),
                'user_config_path_sha256':digest(bb['user_config_path'].encode()),
                **{key:expected[key] for key in ('previous_filtered_configs_sha256','current_native_results_sha256','current_physical_metadata_sha256')}}
    except (Refusal, OSError, ValueError, KeyError, TypeError): pass
    return result


def _config_helper():
    return load_transition_helper('codex-recovery-config-transition.py', CONFIG_TRANSITION_DIGEST)


def _check_acquisition(binding, configs):
    h = _config_helper()
    if (not isinstance(binding, dict) or set(binding) != _ACQUISITION_KEYS or
            binding['schema'] != 'implementaudit.config-acquisition-binding.v1' or
            any(not h._is_hash(binding[k]) for k in ('native_results_sha256',
                'physical_metadata_sha256', 'filtered_configs_sha256')) or
            binding['filtered_configs_sha256'] != digest(canonical(configs))):
        raise InitialEpochFailure('CONFIG_IDENTITY','ACQUISITION_BINDING','initial config acquisition binding differs')
    if (binding['pipe_value'] is not None and (not isinstance(binding['pipe_value'], str)
            or not h.PIPE_PATTERN.fullmatch(binding['pipe_value'])) or
            binding['user_config_path'] is not None and not isinstance(binding['user_config_path'], str)):
        raise InitialEpochFailure('CONFIG_IDENTITY','ACQUISITION_WITNESS','initial acquisition witness shape differs')


def validate_initial_config_chain(before, after, transition, raw_reads, physical_reads, *, later_witness=None):
    """No native calls: rederive initial relation from actual current supplied pairs.

    With a later successor, first prove after-to-current against those pairs,
    then use distinctly derived after material for before-to-after. No fake pair.
    """
    h = _config_helper()
    try:
        if (not isinstance(transition, dict) or set(transition) != {'schema', 'helper_sha256',
                'before_acquisition', 'after_acquisition', 'witness', 'task', 'source_identity'} or
                transition['schema'] != 'implementaudit.initial-config-transition.v1' or
                transition['helper_sha256'] != CONFIG_TRANSITION_DIGEST or
                transition['task'] != before['parameters']['task'] or
                transition['task'] != after['native_thread']['id'] or
                before['native_thread'] != after['native_thread'] or
                transition['source_identity'] != before['source_identity'] or
                before['source_identity'] != after['source_identity'] or
                before['parent_binding']['asar']['sha256'] != h.PRODUCER['asar_sha256'] or
                after['parent_binding']['asar']['sha256'] != h.PRODUCER['asar_sha256']):
            raise InitialEpochFailure('CONFIG_IDENTITY','INITIAL_SOURCE_BINDING','initial transition task/source/producer binding differs')
        bb, ab, witness = (transition[k] for k in ('before_acquisition', 'after_acquisition', 'witness'))
        _check_acquisition(bb, before['configs']);_check_acquisition(ab, after['configs'])
        expected = {'schema':'implementaudit.config-pipe-transition.v1', 'field':h.FIELD,
            'previous_value':bb['pipe_value'], 'current_value':ab['pipe_value'],
            'user_config_path':bb['user_config_path'], 'producer':h.PRODUCER,
            'previous_filtered_configs_sha256':bb['filtered_configs_sha256'],
            'current_native_results_sha256':ab['native_results_sha256'],
            'current_physical_metadata_sha256':ab['physical_metadata_sha256']}
        if witness != expected or bb['user_config_path'] != ab['user_config_path']:
            raise InitialEpochFailure('CONFIG_IDENTITY','INITIAL_WITNESS','initial transition witness differs from acquisitions')
        later = intermediate = None
        if later_witness is None:
            current, initial = h.validate_config_transition(before['configs'], raw_reads, physical_reads, witness)
            native, files = raw_reads[0], physical_reads[0]
        else:
            _, later = h.validate_config_transition(after['configs'], raw_reads, physical_reads, later_witness)
            native, files, intermediate = h.derive_previous_material(after['configs'], raw_reads[0], physical_reads[0], later_witness)
            current, initial = h.validate_derived_transition(before['configs'], native, files, witness, intermediate)
        if current != after['configs']:
            raise InitialEpochFailure('CONFIG_IDENTITY','ACTUAL_AFTER_CONFIG','initial transition does not reproduce actual after config')
        prior_native, prior_files, prior_binding = h.derive_previous_material(before['configs'], native, files, witness)
        if prior_binding['native_results_sha256'] != bb['native_results_sha256']:
            raise InitialEpochFailure('INITIAL_BEFORE_BINDING','BEFORE_NATIVE_DIGEST','initial inverse does not bind actual before acquisition')
        if prior_binding['physical_metadata_sha256'] != bb['physical_metadata_sha256']:
            raise InitialEpochFailure('INITIAL_BEFORE_BINDING','BEFORE_PHYSICAL_DIGEST','initial inverse does not bind actual before acquisition')
        return {'initial':initial, 'later':later, 'intermediate':intermediate,
            'before_inverse':prior_binding, 'ordinary_effect_authority':'NONE'}
    except h.ConfigTransitionRefusal as error:
        predicate = error.predicate
        stage = next((stage for stage, codes in _INITIAL_FAILURE_PREDICATES.items() if predicate in codes), 'CONFIG_IDENTITY')
        raise InitialEpochFailure(stage,predicate,'initial config relation refused') from None
    except (KeyError, TypeError, ValueError):
        raise InitialEpochFailure('CONFIG_IDENTITY','UNKNOWN','initial config relation refused') from None


class NativeRecoveryObserver:
    """Portable real observer. Epoch evidence is data under explicit owner custody."""
    def __init__(self, *, binary, home, repo, controller_cwd, plugin_root, plugin_id, task, epoch_directory=None, observation_successor_spec=None, observation_successor_sha256=None):
        self.binary=pathlib.Path(binary).resolve();self.home=pathlib.Path(home).resolve()
        self.repo=pathlib.Path(repo).resolve();self.controller_cwd=pathlib.Path(controller_cwd).resolve()
        self.plugin_root=pathlib.Path(plugin_root).resolve();self.plugin_id=plugin_id;self.task=task
        self.epoch_directory=epoch_directory
        if (observation_successor_spec is None) != (observation_successor_sha256 is None):
            raise Refusal('successor specification and exact review digest are both required')
        self.observation_successor_spec = observation_successor_spec
        self.observation_successor_sha256 = observation_successor_sha256
        if not isinstance(task,str) or not task or not isinstance(plugin_id,str) or '@' not in plugin_id:
            raise Refusal('native observation parameters malformed')
        self.env=dict(os.environ);self.env['CODEX_HOME']=str(self.home)
        # The owner normal-home assumption is checked on production epoch entry.
        self.parameters={'binary':str(self.binary),'home':str(self.home),'repo':str(self.repo),
                         'controller_cwd':str(self.controller_cwd),'plugin_root':str(self.plugin_root),
                         'plugin_id':plugin_id,'task':task}

    def successor_spec(self):
        if self.observation_successor_spec is None: return None
        spec = load_successor_spec(self.observation_successor_spec, self.observation_successor_sha256)
        if spec['source_transition']['successor_root'] != str(self.plugin_root):
            raise Refusal('successor specification names another executing package')
        if pathlib.Path(__file__).resolve() != self.plugin_root / 'skills/implementaudit/scripts/codex-recovery-native-reader.py':  # Native plugin recovery uses the source repo-shaped package layout.
            raise Refusal('successor reader is not executing from the exact package')
        return spec

    def _read_native(self, methods):
        context=getattr(self,'_acquisition_context',None)
        if context is None: return native_read(self.binary,self.repo,methods,self.env)
        _observation_remaining(context['deadline'],45)
        try:
            rows,protocol=native_read(self.binary,self.repo,methods,self.env,deadline=context['deadline'])
        except AcquisitionFailure as error:
            protocol=getattr(error,'probe_protocol',None)
            if isinstance(protocol,dict):
                context['protocols'].append({'stage':context['stage'],**_acquisition_protocol(protocol)})
            raise
        summary=_acquisition_protocol(protocol)
        context['protocols'].append({'stage':context['stage'],**summary})
        if (not summary['process_terminated'] or not summary['streams_complete'] or
                any(not row['done'] or not row['eof'] or row['failure_present'] for row in summary['streams'].values())):
            raise AcquisitionFailure('NATIVE_CLEANUP_UNPROVED')
        _observation_remaining(context['deadline'],45)
        if summary['failure_present'] or summary['exit_code']!=0:
            raise AcquisitionFailure('NATIVE_PROTOCOL_FAILURE')
        if any('error' in row for row in rows): raise AcquisitionFailure('NATIVE_RESPONSE_ERROR')
        _observation_remaining(context['deadline'],45)
        return rows,protocol

    def _write_acquisition_diagnostic(self, directory, context, category):
        if directory is None: return
        if context['stage'] not in _ACQUISITION_STAGES: raise AcquisitionFailure('UNKNOWN_FAILURE')
        value={'schema':'implementaudit.acquisition-diagnostic.v1','authority':'NONE',
            'stage':context['stage'],'category':category,'protocols':context['protocols'],
            'material_hashes':context['material_hashes'],'snapshot_returned':context['snapshot_returned'],
            'observation_window_max_seconds':120 if context['deadline'] is not None else None,
            'cleanup_reserve_seconds_per_probe':12,'raw_material_persisted':False,'currentness':False}
        with (pathlib.Path(directory)/'acquisition-diagnostic.json').open('xb') as stream:
            stream.write(canonical(value)+b'\n')

    def read_config_material(self):
        # Raw normalized config and physical bytes are transient memory only.
        methods = [('config/read', {'cwd': str(cwd), 'includeLayers': True}, 'ConfigRead')
                   for cwd in (self.repo, self.controller_cwd)]
        rows, protocol = self._read_native(methods)
        if (protocol['failure'] or not protocol['process_terminated'] or len(rows) != 2
                or any('error' in r for r in rows)):
            raise Refusal('fresh native configuration transition read failed')
        native = []
        paths = []
        for row, method in zip(rows, methods):
            if row['method'] != method[0] or row['params'] != method[1]:
                raise Refusal('native configuration response order differs')
            native.append({'cwd': row['params']['cwd'], 'result': row['result']})
            for layer in row['result']['layers']:
                name = layer['name']
                if name.get('file'): paths.append(name['file'])
                if name.get('dotCodexFolder'): paths.append(str(pathlib.Path(name['dotCodexFolder']) / 'config.toml'))
        physical = []
        for name in dict.fromkeys(paths):
            path = pathlib.Path(name)
            before = file_observation(path)
            raw = path.read_bytes() if before.get('exists') else None
            after = file_observation(path)
            if before != after or raw is not None and digest(raw) != before['sha256']:
                raise Refusal('physical configuration changed while being read')
            physical.append({'metadata': before, 'content': raw})
        return native, physical

    def native_snapshot(self, previous=None):
        """Actual config/hooks/API-resolved path. Also usable as a data-only fixture control."""
        binary=file_observation(self.binary)
        if binary.get('sha256')!=EXPECTED_BINARY: raise Refusal('native executable changed')
        methods=[('config/read',{'cwd':str(cwd),'includeLayers':True},'ConfigRead')
                 for cwd in (self.repo,self.controller_cwd)]
        methods += [('hooks/list',{'cwds':list(dict.fromkeys((str(self.repo),str(self.controller_cwd))))},'HooksList'),
                    ('thread/read',{'threadId':self.task,'includeTurns':False},'ThreadRead')]
        rows,protocol=self._read_native(methods)
        if protocol['failure'] or not protocol['process_terminated'] or any('error' in r for r in rows):
            raise Refusal('native observation failed')
        configs=[];hooks=None;thread=None
        for row in rows:
            value=row['result']
            if row['method']=='config/read': configs.append({'cwd':row['params']['cwd'],**filter_config(value)})
            elif row['method']=='hooks/list': hooks=value.get('data')
            elif row['method']=='thread/read': thread=value.get('thread')
        if len(configs)!=2 or any(c['feature'] is not True for c in configs): raise Refusal('feature is not explicitly true')
        if not isinstance(hooks,list) or len(hooks)!=len(set((str(self.repo),str(self.controller_cwd)))):
            raise Refusal('native hooks readback is incomplete')
        bindings=[]
        for entry in hooks:
            if entry.get('errors') or entry.get('warnings'): raise Refusal('native hook discovery is uncertain')
            active=[h for h in entry['hooks'] if h.get('eventName')=='userPromptSubmit' and h.get('enabled') is True]
            if len(active)!=1: raise Refusal('recovery hook is not unique')
            hook=active[0]
            if (hook.get('pluginId')!=self.plugin_id or hook.get('trustStatus')!='trusted'
                    or pathlib.Path(hook.get('sourcePath','')).resolve()!=self.plugin_root/'hooks/hooks.json'):
                raise Refusal('recovery hook source/trust differs')
            bindings.append(recovery_hook_binding(self.plugin_root,self.plugin_id,hook))
        if not isinstance(thread,dict) or thread.get('id')!=self.task or not thread.get('path'):
            raise Refusal('API returned another task or no native path')
        if (not isinstance(thread.get('cwd'),str)
                or pathlib.Path(thread['cwd']).resolve() not in {self.repo,self.controller_cwd}):
            raise Refusal('native task cwd is outside the observed configuration contexts')
        frontier=stream_frontier(thread['path'],self.home/'sessions',self.task,previous,retain_suffix=False)
        if (not isinstance(frontier['native_session_cwd'],str)
                or pathlib.Path(frontier['native_session_cwd']).resolve()!=pathlib.Path(thread['cwd']).resolve()):
            raise Refusal('native session cwd differs from the API task context')
        return {'binary':binary,'configs':configs,'hooks':hooks,'recovery_hook_binding':bindings,
                'package_files':[file_observation(p) for p in sorted(self.plugin_root.rglob('*')) if p.is_file()],
                'source_identity':file_observation(__file__),'parameters':self.parameters,
                'native_thread':{'id':thread['id'],'path':thread['path'],'cwd':thread.get('cwd')},
                'frontier':frontier,'protocol':protocol}

    def snapshot(self, previous=None, *, before_restart=False):
        if self.home!=pathlib.Path.home()/'.codex': raise Refusal('normal desktop home is not established')
        deadline=getattr(self,'_acquisition_context',{}).get('deadline')
        all_before=processes(deadline=deadline)
        before=[p for p in all_before if p['desktop_owned']]
        if len(before)!=1: raise Refusal('exact single desktop native owner required')
        owner=before[0]
        if before_restart and any(p['pid']==os.getpid() for p in owner['desktop_process_tree']):
            raise Refusal('restart watcher must be launched outside the desktop process tree')
        if before_restart and any(p.get('subcommand_app_server') and not p['desktop_descendant'] for p in all_before):
            raise Refusal('unrelated native writer is outside the observed old desktop tree')
        if not before_restart and any(p.get('subcommand_app_server') and p['pid']!=owner['pid'] for p in all_before):
            raise Refusal('additional current desktop native writer is unqualified')
        if (owner['executable']['sha256']!=EXPECTED_BINARY or pathlib.Path(owner['path']).resolve()!=self.binary
                or not owner['subcommand_app_server'] or owner['feature_assignments']
                or owner['profile_argument_present'] or owner['unclassified_assignment_argument']):
            raise Refusal('native producer source or arguments unqualified')
        allowed={'features.code_mode_host','mcp_servers.codex_app','chatgpt_base_url','openai_base_url'}
        if ({r['key'] for r in owner['override_keys_and_hashes']} - allowed
                or set(owner['flags'])-{'-c','--config','--analytics-default-enabled'}):
            raise Refusal('unknown native producer override')
        binding=desktop_parent_binding(owner)
        result=self.native_snapshot(previous)
        all_after=processes(deadline=deadline);after=[p for p in all_after if p['desktop_owned']]
        core=lambda rows:[{k:v for k,v in p.items() if k!='desktop_process_tree'} for p in rows]
        if (core(before)!=core(after) or desktop_parent_binding(after[0])!=binding
                or not before_restart and any(p.get('subcommand_app_server') and p['pid']!=owner['pid'] for p in all_after)
                or before_restart and any(p.get('subcommand_app_server') and not p['desktop_descendant'] for p in all_after)):
            raise Refusal('producer changed during observation')
        merged={p['pid']:p for p in owner['desktop_process_tree']+after[0]['desktop_process_tree']}
        owner['desktop_process_tree']=[merged[pid] for pid in sorted(merged)]
        return {**result,'owner':owner,'parent_binding':binding,'observed_utc':now()}

    def write_observation(self, directory, label, value):
        directory=pathlib.Path(directory).resolve()
        if label not in {'before','stopped','restarted'}: raise Refusal('unknown observation stage')
        path=directory/(label+'.json')
        body={**value}
        if 'frontier' in body: body['frontier']=durable(body['frontier'])
        raw=canonical({'schema':'implementaudit.native-owner-observation.v1','stage':label,'observation':body})+b'\n'
        with path.open('xb') as stream: stream.write(raw)

    def capture_epoch_boundary(self, previous=None, *, before_restart=False, directory=None,
                               diagnostic_directory=None, deadline=None):
        """Actual bracket only; typed errors preserve safe phase/cleanup evidence."""
        if getattr(self,'_acquisition_context',None) is not None: raise AcquisitionFailure('UNKNOWN_FAILURE')
        context={'stage':'FIRST_MATERIAL','deadline':deadline,'protocols':[],
                 'material_hashes':{},'snapshot_returned':False}
        self._acquisition_context=context
        observation=None;category='COMPLETE'
        evidence_directory=directory if directory is not None else diagnostic_directory
        try:
            _observation_remaining(deadline,45)
            first,first_files=self.read_config_material()
            context['material_hashes']['first_native']=digest(canonical(first))
            context['material_hashes']['first_physical']=digest(canonical([r['metadata'] for r in first_files]))
            context['stage']='SNAPSHOT'
            observation=self.snapshot(previous,before_restart=before_restart)
            context['snapshot_returned']=True
            if directory is not None: self.write_epoch_record(directory,'restarted-observed',observation,None)
            context['material_hashes']['snapshot_configs']=digest(canonical(observation['configs']))
            context['stage']='SECOND_MATERIAL'
            second,second_files=self.read_config_material()
            context['material_hashes']['second_native']=digest(canonical(second))
            context['material_hashes']['second_physical']=digest(canonical([r['metadata'] for r in second_files]))
            context['stage']='PAIR_VALIDATION';h=_config_helper()
            try:
                _validate_acquisition_material(h,first,first_files)
                _validate_acquisition_material(h,second,second_files)
            except (ValueError,KeyError,TypeError): raise AcquisitionFailure('MATERIAL_SHAPE_INVALID') from None
            if len(context['protocols'])!=3: raise AcquisitionFailure('NATIVE_CLEANUP_UNPROVED')
            _observation_remaining(deadline,45)
            if canonical(first)!=canonical(second): raise ConfigurationInstability('NATIVE_PAIR_CHANGED')
            if first_files!=second_files: raise ConfigurationInstability('PHYSICAL_PAIR_CHANGED')
            filtered,binding=h.observed_config_material([first,second],[first_files,second_files])
            context['stage']='SNAPSHOT_EQUALITY'
            if filtered!=observation['configs']: raise ConfigurationInstability('SNAPSHOT_BRACKET_CHANGED')
            _observation_remaining(deadline,45)
            context['stage']='COMPLETE'
            return observation,{'binding':binding,'native_reads':[first,second],
                                'physical_reads':[first_files,second_files]}
        except BaseException as error:
            failure=error if isinstance(error,AcquisitionFailure) else AcquisitionFailure('INTERRUPTED' if isinstance(error,KeyboardInterrupt) else 'UNKNOWN_FAILURE')
            category=failure.code;failure.observation=observation
            if directory is not None: self.write_epoch_outcome(directory,'REFUSED_NO_AUTHORITY')
            raise failure from None
        finally:
            del self._acquisition_context
            self._write_acquisition_diagnostic(evidence_directory,context,category)

    def acquire_restarted_boundary(self, directory, previous, *, watcher_deadline,
                                   before=None, stop=None, before_acquisition=None):
        """Fresh watcher only. No resume of an already attempted/completed epoch."""
        if self.__dict__.pop('_initial_finish_handoff',None) is not None:
            raise AcquisitionFailure('EPOCH_ALREADY_ATTEMPTED')
        directory=pathlib.Path(directory)
        if any((directory/name).exists() for name in ('restarted.json','restarted-observed.json','epoch-outcome.json','after-acquisition-attempts','initial-finish-start.json')):
            raise AcquisitionFailure('EPOCH_ALREADY_ATTEMPTED')
        if before is None or stop is None or before_acquisition is None or previous!=before.get('frontier'):
            raise AcquisitionFailure('UNKNOWN_FAILURE')
        attempts=directory/'after-acquisition-attempts';attempts.mkdir()
        deadline=min(watcher_deadline,time.monotonic()+120)
        baseline=None;index=0;started_attempts=0;category='COMPLETE'
        try:
            for index in range(1,4):
                _observation_remaining(deadline,45)
                attempt=attempts/('%02d'%index);attempt.mkdir()
                started_attempts+=1
                try:
                    observation,acquisition=self.capture_epoch_boundary(previous,directory=attempt,deadline=deadline)
                except ConfigurationInstability as failure:
                    if failure.observation is None: raise AcquisitionFailure('UNKNOWN_FAILURE')
                    identity=_acquisition_identity(failure.observation)
                    if baseline is not None and identity!=baseline: raise AcquisitionFailure('ACQUISITION_CONTEXT_CHANGED')
                    baseline=identity
                    if index==3: raise AcquisitionFailure('ATTEMPTS_EXHAUSTED')
                    time.sleep(_observation_remaining(deadline,1))
                    continue
                identity=_acquisition_identity(observation)
                if baseline is not None and identity!=baseline: raise AcquisitionFailure('ACQUISITION_CONTEXT_CHANGED')
                _observation_remaining(deadline,45)
                break
            else: raise AcquisitionFailure('ATTEMPTS_EXHAUSTED')
        except BaseException as error:
            category=error.code if isinstance(error,AcquisitionFailure) else 'UNKNOWN_FAILURE'
            try: self.write_epoch_outcome(directory,'REFUSED_NO_AUTHORITY')
            except Exception: pass
            raise
        finally:
            record={'schema':'implementaudit.after-acquisition-selection.v1','authority':'NONE',
                    'attempts':started_attempts,'category':category,'selected_attempt':index if category=='COMPLETE' else None,
                    'max_attempts':3,'observation_window_max_seconds':120,'cleanup_reserve_seconds_per_probe':12,
                    'currentness':False}
            selection_raw=canonical(record)+b'\n'
            with (directory/'after-acquisition-selection.json').open('xb') as stream:
                if stream.write(selection_raw)!=len(selection_raw):
                    raise AcquisitionFailure('UNKNOWN_FAILURE')
            if (directory/'after-acquisition-selection.json').read_bytes()!=selection_raw:
                raise AcquisitionFailure('UNKNOWN_FAILURE')

        # Issue only after selected capture, cleanup/identity/deadline checks and
        # successful selection persistence. This is a live object, never a receipt.
        _observation_remaining(deadline,45)
        binding=self._initial_finish_context(directory,before,stop,observation,before_acquisition,acquisition)
        token=_InitialFinishHandoff(self,deadline)
        self._initial_finish_handoff=(token,binding)
        return observation,acquisition,token

    def _initial_finish_context(self, directory, before, stop, after, before_acquisition, after_acquisition):
        directory=pathlib.Path(directory).resolve();identity=directory.stat()
        helper_path=pathlib.Path(__file__).with_name('codex-recovery-config-transition.py')
        if digest(helper_path.read_bytes())!=CONFIG_TRANSITION_DIGEST:
            raise Refusal('initial finish helper source differs')
        physical=[[{'metadata':entry['metadata'],
                    'content_sha256':digest(entry['content']) if entry['content'] is not None else None}
                   for entry in files] for files in after_acquisition['physical_reads']]
        # The live frontier has binary session metadata/suffix fields. Bind their
        # exact bytes by hash without serializing or persisting conversation data.
        frontier_digest=lambda value:digest(canonical({'durable':durable(value),
            'wire_sha256':{key:digest(value[key]) for key in ('session_meta_wire','suffix') if key in value}}))
        return {'schema':'implementaudit.initial-finish-context.v1','authority':'NONE','currentness':False,
            'epoch_sha256':digest(canonical([str(directory),identity.st_dev,identity.st_ino])),
            'task_sha256':digest(canonical(self.task)), 'parameters_sha256':digest(canonical(self.parameters)),
            'reader_sha256':digest(pathlib.Path(__file__).read_bytes()), 'helper_sha256':CONFIG_TRANSITION_DIGEST,
            'before_sha256':digest(canonical({**before,'frontier':durable(before['frontier'])})),
            'stop_sha256':digest(canonical(stop)), 'previous_frontier_sha256':frontier_digest(before['frontier']),
            'after_sha256':digest(canonical({**after,'frontier':durable(after['frontier'])})),
            'after_frontier_sha256':frontier_digest(after['frontier']),
            'before_acquisition_sha256':digest(canonical(before_acquisition['binding'])),
            'after_acquisition_sha256':digest(canonical(after_acquisition['binding'])),
            'native_pair_sha256':digest(canonical(after_acquisition['native_reads'])),
            'physical_pair_sha256':digest(canonical(physical)),
            'input_file_sha256':{name:digest((directory/name).read_bytes())
                for name in ('before.json','stopped.json','after-acquisition-selection.json')}}

    def _consume_initial_finish_handoff(self, handoff):
        # Pop before every check and before all fallible finish IO. Even a wrong
        # token invalidates the sole pending handoff; caller data cannot recreate it.
        pending=self.__dict__.pop('_initial_finish_handoff',None)
        if pending is None or handoff is not pending[0] or handoff.owner is not self:
            raise Refusal('live initial finish handoff missing or consumed')
        _observation_remaining(handoff.deadline,45)
        return pending[1]

    def _reserve_initial_finish(self, directory, binding):
        path=pathlib.Path(directory)/'initial-finish-start.json'
        raw=canonical({'schema':'implementaudit.initial-finish-start.v1',
                       'authority':'NONE','currentness':False,'context':binding})+b'\n'
        # A failed or partial reservation is retained. Absence is never permission:
        # the live handoff has already been consumed before this method is called.
        with path.open('xb') as stream:
            if stream.write(raw)!=len(raw):raise Refusal('initial finish start short write')
            stream.flush()
            os.fsync(stream.fileno())
        if path.read_bytes()!=raw:
            raise InitialEpochFailure('FINISH_START','START_READBACK','initial finish start readback differs')

    def write_epoch_record(self, directory, stage, observation, acquisition, transition=None):
        if stage not in {'before', 'stopped', 'restarted', 'restarted-observed'}:
            raise Refusal('unknown v2 observation stage')
        body = {**observation}
        if 'frontier' in body: body['frontier'] = durable(body['frontier'])
        binding = acquisition['binding'] if acquisition is not None else None
        if binding is not None: _check_acquisition(binding, body['configs'])
        record = {'schema':_EPOCH_V2, 'stage':stage, 'observation':body,
            'config_acquisition':binding, 'initial_config_transition':transition}
        with (pathlib.Path(directory)/(stage+'.json')).open('xb') as stream:
            stream.write(canonical(record)+b'\n')

    def write_epoch_outcome(self, directory, outcome):
        if outcome not in {'REFUSED_NO_AUTHORITY', 'RELATION_EVALUATED_NO_AUTHORITY'}:
            raise Refusal('unknown epoch outcome')
        with (pathlib.Path(directory)/'epoch-outcome.json').open('xb') as stream:
            stream.write(canonical({'schema':'implementaudit.epoch-outcome.v1',
                'outcome':outcome, 'currentness_restored':False})+b'\n')

    def initial_transition(self, before, after, before_acquisition, after_acquisition):
        bb, ab = before_acquisition['binding'], after_acquisition['binding']
        h = _config_helper()
        return {'schema':'implementaudit.initial-config-transition.v1',
            'helper_sha256':CONFIG_TRANSITION_DIGEST, 'before_acquisition':bb, 'after_acquisition':ab,
            'task':before['parameters']['task'], 'source_identity':before['source_identity'],
            'witness':{'schema':'implementaudit.config-pipe-transition.v1', 'field':h.FIELD,
                'previous_value':bb['pipe_value'], 'current_value':ab['pipe_value'],
                'user_config_path':bb['user_config_path'], 'producer':h.PRODUCER,
                'previous_filtered_configs_sha256':bb['filtered_configs_sha256'],
                'current_native_results_sha256':ab['native_results_sha256'],
                'current_physical_metadata_sha256':ab['physical_metadata_sha256']}}

    def _write_initial_failure_diagnostic(self, directory, stage, predicate, before, after,
                                          before_acquisition, after_acquisition, transition):
        # Fixed enums and selected hashes only, never an exception/native dict dump.
        failure = InitialEpochFailure(stage, predicate, 'initial relation diagnostic')
        directory = pathlib.Path(directory)
        record = {'schema':'implementaudit.initial-epoch-failure.v1', 'authority':'NONE',
            'currentness':False, 'stage':failure.stage, 'predicate':failure.predicate,
            'source_pin_kind':'FILES_AT_DIAGNOSTIC_WRITE_NOT_EXECUTION_ATTESTATION',
            'expected_helper_sha256':CONFIG_TRANSITION_DIGEST,
            'sources':{name:_initial_failure_file_pin(pathlib.Path(__file__).with_name(name))
                for name in ('codex-recovery-native-reader.py','codex-recovery-config-transition.py')},
            'input_files':{name:_initial_failure_file_pin(directory/name)
                for name in ('before.json','stopped.json','restarted-observed.json')},
            **_initial_failure_material(before, after, before_acquisition, after_acquisition, transition)}
        with (directory/'initial-epoch-failure.json').open('xb') as stream:
            stream.write(canonical(record)+b'\n')

    def finish_initial_epoch(self, directory, before, stop, after, before_acquisition, after_acquisition, *, handoff=None):
        """Retain truthful actual-after before validation; only complete v2 after it.

        No outcome record is a PASS or input to epoch acceptance.
        """
        binding=self._consume_initial_finish_handoff(handoff)
        stage = 'HANDOFF_IDENTITY'
        transition = None
        actual_after_retained = False
        try:
            directory = pathlib.Path(directory)
            if self._initial_finish_context(directory,before,stop,after,before_acquisition,after_acquisition)!=binding:
                raise InitialEpochFailure(stage,'HANDOFF_CONTEXT','initial finish handoff context differs')
            if any((directory/name).exists() for name in ('restarted.json','epoch-outcome.json','initial-epoch-failure.json')):
                raise Refusal('initial epoch already attempted')
            stage = 'FINISH_START'
            self._reserve_initial_finish(directory,binding)
            observed_path = directory/'restarted-observed.json'
            stage = 'ACTUAL_AFTER_CUSTODY'
            if not observed_path.exists():
                self.write_epoch_record(directory, 'restarted-observed', after, None)
            else:
                saved = strict_json(observed_path.read_bytes())
                expected = {**after, 'frontier':durable(after['frontier'])}
                expected_record = {'schema':_EPOCH_V2, 'stage':'restarted-observed', 'observation':expected,
                        'config_acquisition':None, 'initial_config_transition':None}
                # Match complete typed JSON content while permitting equivalent
                # formatting. Enforce finite numbers here without changing the
                # shared parser or canonical identity policy elsewhere.
                finite_canonical = lambda value: json.dumps(value, sort_keys=True,
                        separators=(",", ":"), allow_nan=False).encode()
                if finite_canonical(saved) != finite_canonical(expected_record):
                    raise InitialEpochFailure(stage,'ACTUAL_AFTER_DIFFERS','actual after custody differs')
            actual_after_retained = True
            stage = 'CONFIG_IDENTITY'
            if before['configs'] != after['configs']:
                transition = self.initial_transition(before, after, before_acquisition, after_acquisition)
            stage = 'EPOCH_RELATION'
            self.validate_epoch(before, stop, after, initial_transition=transition,
                raw_reads=after_acquisition['native_reads'], physical_reads=after_acquisition['physical_reads'])
            stage = 'FINAL_WRITE'
            self.write_epoch_record(directory, 'restarted', after, after_acquisition, transition)
            self.write_epoch_outcome(directory, 'RELATION_EVALUATED_NO_AUTHORITY')
        except (Refusal, OSError, ValueError, KeyError, TypeError) as error:
            predicate = 'UNKNOWN'
            if isinstance(error, InitialEpochFailure): stage, predicate = error.stage, error.predicate
            # Neither failed persistence operation may replace the original refusal.
            try: self.write_epoch_outcome(directory, 'REFUSED_NO_AUTHORITY')
            except Exception: pass
            try:
                self._write_initial_failure_diagnostic(directory, stage, predicate, before, after,
                    before_acquisition, after_acquisition, transition)
            except Exception: pass
            if not actual_after_retained:
                raise Refusal('initial epoch relation refused; actual after custody unavailable') from None
            raise Refusal('initial epoch relation refused; actual after retained') from None

    def _epoch_records(self, directory):
        records = []
        for stage in ('before', 'stopped', 'restarted'):
            path = pathlib.Path(directory)/(stage+'.json')
            if path.stat().st_size > LIMIT: raise Refusal('epoch observation oversized')
            record = strict_json(path.read_bytes())
            if not isinstance(record, dict): raise Refusal('foreign observation schema/stage')
            schema = record.get('schema')
            keys = {'schema', 'stage', 'observation'}
            if schema == _EPOCH_V2: keys |= {'config_acquisition', 'initial_config_transition'}
            elif schema != 'implementaudit.native-owner-observation.v1':
                raise Refusal('foreign observation schema/stage')
            if set(record) != keys or record['stage'] != stage:
                raise Refusal('foreign observation schema/stage')
            records.append(record)
        if len({record['schema'] for record in records}) != 1:
            raise Refusal('mixed epoch schemas')
        if records[0]['schema'] == _EPOCH_V2:
            for index in (0, 2):
                _check_acquisition(records[index]['config_acquisition'], records[index]['observation']['configs'])
            if (records[0]['initial_config_transition'] is not None or
                    records[1]['initial_config_transition'] is not None or
                    records[1]['config_acquisition'] is not None):
                raise Refusal('foreign initial transition stage')
            transition = records[2]['initial_config_transition']
            if transition is not None and not isinstance(transition, dict):
                raise Refusal('initial transition acquisition ancestry differs')
            if transition is not None and (transition.get('before_acquisition') != records[0]['config_acquisition'] or
                    transition.get('after_acquisition') != records[2]['config_acquisition']):
                raise Refusal('initial transition acquisition ancestry differs')
        return records

    def read_epoch(self, directory, *, raw_reads=None, physical_reads=None, later_witness=None):
        """File/prefix and pure relation checks only; never invokes native calls.

        v2 requires explicit caller-acquired current pairs. Native orchestration
        belongs to _current_input_context, not this comparator/readback method.
        """
        records = self._epoch_records(directory)
        before, stop, after = [record['observation'] for record in records]
        spec = self.successor_spec()
        expected_parameters = self.parameters
        if spec is not None:
            if epoch_file_pins(directory) != spec['source_transition']['epoch_files']:
                raise Refusal('original epoch bytes differ from reviewed source transition')
            expected_parameters = {**self.parameters, 'plugin_root':spec['source_transition']['predecessor_root']}
        transition = None
        if records[0]['schema'] == _EPOCH_V2:
            if raw_reads is None or physical_reads is None:
                raise Refusal('v2 epoch requires explicit independently acquired material')
            transition = records[2]['initial_config_transition']
            if transition is None:
                if before['configs'] != after['configs']:
                    raise Refusal('initial changed config witness missing')
                if later_witness is None:
                    h = _config_helper()
                    try: filtered, binding = h.observed_config_material(raw_reads, physical_reads)
                    except (ValueError, KeyError, TypeError): raise Refusal('epoch material refused') from None
                    if filtered != after['configs'] or binding != records[2]['config_acquisition']:
                        raise Refusal('independent epoch acquisition differs')
        self.validate_epoch(before, stop, after, expected_parameters=expected_parameters,
            initial_transition=transition, raw_reads=raw_reads, physical_reads=physical_reads,
            later_witness=later_witness)
        return before, stop, after

    def validate_epoch(self,before,stop,after, *, expected_parameters=None, initial_transition=None,
                       raw_reads=None, physical_reads=None, later_witness=None):
        expected_parameters = self.parameters if expected_parameters is None else expected_parameters
        stable_before, stable_after = stable(before), stable(after)
        if initial_transition is not None:
            validate_initial_config_chain(before, after, initial_transition, raw_reads, physical_reads,
                                          later_witness=later_witness)
            # Compare every other fact without rewriting either observation.
            stable_before = {k:v for k,v in stable_before.items() if k != 'configs'}
            stable_after = {k:v for k,v in stable_after.items() if k != 'configs'}
        if (before['parameters']!=expected_parameters or after['parameters']!=expected_parameters
                or stable_before!=stable_after or not before['package_files']):
            raise InitialEpochFailure('STABLE_SOURCE','EPOCH_STABLE_FIELDS','epoch sources/config/parameters changed')
        initial_tree={row['pid'] for row in before['owner']['desktop_process_tree']}
        old_ids=stop.get('old_ids')
        if (not isinstance(old_ids,list) or any(type(pid) is not int for pid in old_ids)
                or old_ids!=sorted(set(old_ids)) or not initial_tree.issubset(set(old_ids))
                or not {before['owner']['pid'],before['owner']['parent_pid']}.issubset(initial_tree)
                or stop.get('matching_pids_present')!=[] or stop.get('desktop_native_pids_now')!=[]
                or stop.get('before_identity')!=digest(canonical({**before,'frontier':durable(before['frontier'])}))):
            raise InitialEpochFailure('STOP_ORDER','STOP_BINDING','old-owner absence observation is unbound')
        stamp=lambda value:datetime.datetime.fromisoformat(value.replace('Z','+00:00'))
        if not (stamp(before['observed_utc'])<stamp(stop['observed_utc'])<stamp(after['observed_utc'])
                and stamp(after['owner']['created_utc'])>stamp(stop['observed_utc'])
                and stamp(after['owner']['parent']['created_utc'])>stamp(stop['observed_utc'])):
            raise InitialEpochFailure('STOP_ORDER','STARTUP_ORDER','producer startup ordering differs')
        if any(after['owner'][key]==before['owner'][key] for key in ('pid','parent_pid')):
            raise InitialEpochFailure('STOP_ORDER','PRODUCER_RESTART','producer did not restart')
        strip=lambda owner:[v for v in owner['override_keys_and_hashes'] if v['key']!='mcp_servers.codex_app']
        if strip(before['owner'])!=strip(after['owner']):
            raise InitialEpochFailure('STABLE_SOURCE','PRODUCER_CONFIG_ARGUMENTS','producer config arguments changed')
        if (before['frontier']['path']!=after['frontier']['path']
                or before['frontier']['session_id']!=after['frontier']['session_id']):
            raise InitialEpochFailure('STABLE_SOURCE','NATIVE_TASK_SESSION','native task/session/path changed')
        # Facts from retained observations remain under the explicitly controlled
        # evidence/writer custody assumption. Fresh independent readback is required.
        try: verify_historical_prefix(after['frontier']['path'],self.home/'sessions',self.task,before['frontier'])
        except Refusal:
            raise InitialEpochFailure('HISTORICAL_PREFIX','HISTORICAL_PREFIX_REFUSED','historical epoch prefix refused') from None
        except (OSError, ValueError, KeyError, TypeError):
            raise InitialEpochFailure('HISTORICAL_PREFIX','UNKNOWN','historical epoch prefix refused') from None

    def watch_restart(self,directory,timeout=900):
        if self.observation_successor_spec is not None: raise Refusal('successor cannot overwrite or create original epoch observations')
        directory=pathlib.Path(directory).resolve();directory.mkdir(exist_ok=False)
        before_diagnostics=directory/'before-acquisition';before_diagnostics.mkdir()
        before, before_acquisition = self.capture_epoch_boundary(before_restart=True,diagnostic_directory=before_diagnostics)
        self.write_epoch_record(directory, 'before', before, before_acquisition)
        before_acquisition = {'binding':before_acquisition['binding']}  # Release raw old config before waiting.
        print('READY_FOR_OWNER_AUTHORIZED_DESKTOP_QUIT',flush=True)
        deadline=time.monotonic()+timeout;tracked={row['pid'] for row in before['owner']['desktop_process_tree']}
        while time.monotonic()<deadline:
            current=processes()
            for process in current:
                if (process['pid'] in tracked or process['parent_pid'] in tracked
                        or any(a['pid'] in tracked for a in process['ancestry'])):
                    tracked.add(process['pid'])
                    tracked.update(row['pid'] for row in process['desktop_process_tree'])
            ids=sorted(tracked)
            # Every codex row exposes its actual parent PID; query old PIDs directly
            # so a remaining desktop without a native child is also excluded.
            script='$ids=@('+','.join(map(str,ids))+'); @(Get-CimInstance Win32_Process | Where-Object {$_.ProcessId -in $ids} | Select-Object -ExpandProperty ProcessId) | ConvertTo-Json -Compress'
            run=subprocess.run(['powershell.exe','-NoProfile','-Command',script],capture_output=True,text=True,timeout=10,creationflags=subprocess.CREATE_NO_WINDOW)
            if run.returncode: raise Refusal('old PID read failed')
            present=strict_json(run.stdout or '[]')
            if present==[] and not any(p['desktop_descendant'] for p in current): break
            time.sleep(1)
        else: raise Refusal('old desktop did not stop within observation deadline')
        stop={'observed_utc':now(),'old_ids':ids,'matching_pids_present':[], 'desktop_native_pids_now':[],
              'before_identity':digest(canonical({**before,'frontier':durable(before['frontier'])}))}
        self.write_epoch_record(directory,'stopped',stop,None);print('OLD_DESKTOP_ABSENT_RELAUNCH_SAME_APP',flush=True)
        while time.monotonic()<deadline:
            if any(p['desktop_owned'] for p in processes()): break
            time.sleep(1)
        else: raise Refusal('new desktop not observed within deadline')
        after, after_acquisition, handoff = self.acquire_restarted_boundary(directory,before['frontier'],
            watcher_deadline=deadline,before=before,stop=stop,before_acquisition=before_acquisition)
        self.finish_initial_epoch(directory, before, stop, after, before_acquisition, after_acquisition,handoff=handoff)
        print('NATIVE_EPOCH_OBSERVED_NO_ROUTE_ADMISSION',flush=True)

    def read_attempt_evidence(self, directory=None):
        selected = self.read_input(directory)
        evidence = build_attempt_evidence(selected['readback_prefix']['path'], self.home/'sessions',
            self.task, selected['native_epoch_frontier'], selected)
        if evidence['schema'] != _ATTEMPT_V2_SCHEMA:
            raise Refusal('repaired native observer must produce v2 attempt evidence')
        return evidence


    def revalidate_attempt_evidence(self, frozen, directory=None):
        validate_attempt_evidence_shape(frozen)
        if frozen['schema'] != _ATTEMPT_V2_SCHEMA:
            raise Refusal('historical v1 attempt is shape-readable only, not live revalidation')
        selected = self.read_input(directory)
        for key in ('native_thread_id','native_session_id','epoch_identity',
                    'native_epoch_frontier','observation_successor_identity',
                    'observation_successor_spec_sha256'):
            if selected.get(key) != frozen.get(key):
                raise Refusal('frozen attempt native source/epoch identity changed')
        # read_input establishes current source/producer custody; it does not reset
        # or replace this frozen attempt with a later UPS or selected native turn.
        proof = revalidate_attempt_evidence(selected['readback_prefix']['path'], self.home/'sessions',
            self.task, frozen, selected['readback_prefix'])
        if proof['compaction_markers']:
            raise Refusal('retained recovery attempt has intervening parent compaction')
        return proof

    def read_disposition_input(self, locator, directory=None, *, committed_prefix=None):
        """Internal abandonment consumer only; no CLI historical selector exists."""
        before,stop,epoch,observed,transition,epoch_identity=self._current_input_context(directory)
        previous=durable(epoch['frontier'])
        _disposition_locator(locator,self.task,previous)
        if locator['epoch_identity']!=epoch_identity:
            raise Refusal('retained disposition original epoch identity differs')
        selected=read_disposition_turn_slice(observed['frontier']['path'],self.home/'sessions',
            self.task,previous,durable(observed['frontier']),locator)
        if committed_prefix is not None:
            _attempt_prefix_shape(committed_prefix)
            if (any(committed_prefix[key]!=previous[key] for key in
                    ('path','session_id','task_id','session_meta_sha256','native_session_cwd'))
                    or committed_prefix['complete_prefix_bytes']<selected['occurrence_end_bytes']):
                raise Refusal('retained disposition existing attempt commitment differs')
            verify_historical_prefix(observed['frontier']['path'],self.home/'sessions',self.task,committed_prefix)
        result={**selected,'epoch_identity':epoch_identity,'native_epoch_frontier':previous}
        if transition is not None:
            result['observation_successor_identity']='sha256:'+digest(canonical(transition))
            result['observation_successor_spec_sha256']=self.observation_successor_sha256
        return result

    def _current_input_context(self,directory=None):
        directory=directory if directory is not None else self.epoch_directory
        if directory is None: raise Refusal('owned native epoch directory required')
        spec = self.successor_spec()
        pins = epoch_file_pins(directory)
        records = self._epoch_records(directory)
        epoch = records[2]['observation']
        transition = None
        v2 = records[0]['schema'] == _EPOCH_V2
        if v2 or spec is not None:
            first, first_files = self.read_config_material()
            observed = self.snapshot(epoch['frontier'])
            second, second_files = self.read_config_material()
            raw_reads, physical_reads = [first, second], [first_files, second_files]
            before, stop, epoch = self.read_epoch(directory, raw_reads=raw_reads,
                physical_reads=physical_reads, later_witness=spec['config_witness'] if spec else None)
        else:
            before, stop, epoch = self.read_epoch(directory)
            observed = self.snapshot(epoch['frontier'])
        if spec is None:
            if (stable(observed)!=stable(epoch) or owner_identity(observed['owner'])!=owner_identity(epoch['owner'])
                    or observed['native_thread'] != epoch['native_thread']):
                raise Refusal('native epoch is no longer current')
        else:
            transition = validate_observation_successor(epoch, observed, spec, pins, raw_reads, physical_reads)
            if self.successor_spec() != spec:
                raise Refusal('reviewed successor specification changed during observation')
        if epoch_file_pins(directory) != pins:
            raise Refusal('original epoch bytes changed during observation')
        identity_subject = [before, stop, epoch]
        if v2:
            identity_subject = {'schema':'implementaudit.native-epoch-identity.v2',
                'observations':identity_subject, 'epoch_files':pins}
        return before,stop,epoch,observed,transition,'sha256:'+digest(canonical(identity_subject))

    def read_input(self,directory=None):
        before,stop,epoch,observed,transition,epoch_identity=self._current_input_context(directory)
        selected=read_native_turn_slice(observed['frontier']['path'],self.home/'sessions',self.task,epoch['frontier'])
        result = {**selected,'epoch_identity':epoch_identity, 'native_epoch_frontier':durable(epoch['frontier'])}
        if transition is not None:
            result['observation_successor_identity'] = 'sha256:' + digest(canonical(transition))
            result['observation_successor_spec_sha256'] = self.observation_successor_sha256
        return result



def main():
    parser=argparse.ArgumentParser()
    for name in ('binary','home','repo','controller-cwd','plugin-root','plugin-id','task','epoch-directory'):
        parser.add_argument('--'+name,required=True)
    parser.add_argument('--observation-successor-spec')
    parser.add_argument('--observation-successor-sha256')
    parser.add_argument('command',choices=('watch-restart','read'))
    args=vars(parser.parse_args());command=args.pop('command');directory=args.pop('epoch_directory')
    observer=NativeRecoveryObserver(**args)
    if command=='watch-restart': observer.watch_restart(directory)
    else:
        path=pathlib.Path(__file__).with_name('route-transaction.py')
        spec=importlib.util.spec_from_file_location('_native_read_route_owner',path)
        route=importlib.util.module_from_spec(spec);sys.modules[spec.name]=route;spec.loader.exec_module(route)
        owned=route.create_recovery_native_observer_v1(**args,epoch_directory=directory)
        value=route.read_retained_recovery_input_v1(pathlib.Path(args['repo']).resolve(),observer=owned)
        print(json.dumps(value,sort_keys=True))


if __name__=='__main__':
    try: main()
    except (Refusal,OSError,ValueError,KeyError,TypeError) as error:
        raise SystemExit('NATIVE_RECOVERY_READ_REFUSED: '+str(error))
